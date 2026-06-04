"""Auto-commit watcher for the repository.

Usage:
  python tools/auto_commit.py

This script watches the repository for file changes and makes non-empty commits
automatically. Configure behavior in `tools/auto_commit_config.json`.
"""
import os
import sys
import time
import json
import logging
import threading
import subprocess
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except Exception as e:
    print("Missing dependency: watchdog. Install with `pip install watchdog`.")
    raise

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = Path(__file__).resolve().parent / "auto_commit_config.json"

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
logger = logging.getLogger("auto_commit")


def load_config():
    default = {
        "push": True,
        "branch": "",
        "debounce_seconds": 2.0,
        "ignored_paths": [".git", ".venv", "venv", "models", "data/raw", "data/processed"]
    }
    if CONFIG_PATH.exists():
        try:
            cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            default.update(cfg)
        except Exception as e:
            logger.warning("Failed to parse config, using defaults: %s", e)
    return default


def run_git(*args):
    cmd = ["git", "-C", str(ROOT), *args]
    logger.debug("Running: %s", " ".join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res


class DebouncedCommitter:
    def __init__(self, debounce_seconds, cfg):
        self.debounce_seconds = debounce_seconds
        self._timer = None
        self._lock = threading.Lock()
        self._changed = set()
        self.cfg = cfg

    def notify(self, path):
        with self._lock:
            self._changed.add(path)
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self.debounce_seconds, self._commit)
            self._timer.start()

    def _commit(self):
        with self._lock:
            files = sorted(self._changed)
            self._changed.clear()
        if not files:
            return
        # Stage changes
        res = run_git("add", "-A")
        if res.returncode != 0:
            logger.error("git add failed: %s", res.stderr)
            return
        status = run_git("status", "--porcelain")
        if not status.stdout.strip():
            logger.info("No changes to commit")
            return
        message = f"chore(auto): auto-commit - changed files: {', '.join(Path(p).name for p in files)}"
        # Commit
        res = run_git("commit", "-m", message)
        if res.returncode == 0:
            logger.info("Committed: %s", message)
        else:
            logger.error("Commit failed: %s", res.stderr)
            return
        # Optional push
        if self.cfg.get("push"):
            branch = self.cfg.get("branch") or get_current_branch()
            if not branch:
                logger.warning("Could not determine branch for push; skipping push")
                return
            res = run_git("push", "origin", branch)
            if res.returncode == 0:
                logger.info("Pushed to origin/%s", branch)
            else:
                logger.error("Push failed: %s", res.stderr)


def get_current_branch():
    res = run_git("rev-parse", "--abbrev-ref", "HEAD")
    if res.returncode == 0:
        return res.stdout.strip()
    return ""


class RepoEventHandler(FileSystemEventHandler):
    def __init__(self, committer, cfg):
        super().__init__()
        self.committer = committer
        self.cfg = cfg

    def _is_ignored(self, path):
        for ig in self.cfg.get("ignored_paths", []):
            if ig and ig in path.parts:
                return True
        return False

    def on_any_event(self, event):
        try:
            p = Path(event.src_path).resolve()
            if self._is_ignored(p):
                return
            # Only consider files inside repo
            try:
                p.relative_to(ROOT)
            except Exception:
                return
            logger.debug("Detected change: %s", p)
            self.committer.notify(str(p))
        except Exception as e:
            logger.exception("Error handling event: %s", e)


def main():
    cfg = load_config()
    branch = cfg.get("branch") or get_current_branch()
    logger.info("Starting auto-commit watcher on repo: %s (branch: %s)", ROOT, branch)
    committer = DebouncedCommitter(cfg.get("debounce_seconds", 2.0), cfg)
    event_handler = RepoEventHandler(committer, cfg)
    observer = Observer()
    observer.schedule(event_handler, str(ROOT), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
