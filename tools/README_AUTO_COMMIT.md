Auto-commit watcher
===================

This watcher will create non-empty commits automatically when files change in the repository.

Quick start:

1. Install dependencies (inside your project's venv):

```bash
pip install watchdog
```

2. Run the watcher:

```bash
python tools/auto_commit.py
```

3. To run continuously on Windows, consider creating a Scheduled Task or run it inside a long-running terminal session.

Configuration is in `tools/auto_commit_config.json`.
