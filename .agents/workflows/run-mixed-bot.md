---
description: Run the mixed content bot (trending & random content) and auto-index to Google
---

# Mixed Content Bot Workflow

This workflow will run the `run_bot_with_mixed_content.py` script. The script fetches 1 trending and 1 random high-rated movie/tv show, creates pages for them, submits them directly to the Google Indexing API, updates `content_index.json`, and regenerates the Sitemaps. After running, the new changes are committed and pushed.

## Steps

// turbo
1. Run the mixed content bot:
```bash
python3 run_bot_with_mixed_content.py
```

// turbo
2. Add, commit, and push the newly generated files (content, index, and sitemaps):
```bash
git add . && git commit -m "🤖 bot: added new mixed content, updated index and sitemaps" && git push origin main
```
