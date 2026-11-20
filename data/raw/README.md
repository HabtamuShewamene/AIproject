# Stage A input: Sentiment140

Place the original Kaggle/Stanford training file in this directory with this exact name:

```text
training.1600000.processed.noemoticon.csv
```

Do not rename it, edit it, or commit it. The pipeline expects the six original no-header columns:

```text
target,id,date,query,user,text
```

Run the preparation step from the project root:

```bash
uv run python -m src.prepare_sentiment140
```

This produces ignored Stage A train/validation files plus a text-free manifest at `results/sentiment140_manifest.json`.
