---
description: Run the fix descriptions bot in a loop every 20 minutes until all pages are complete
---

// turbo-all
# Fix Descriptions Bot Loop (Every 20 Minutes)

This workflow runs `fix_short_descriptions_bot.py` every 20 minutes in a continuous loop until all non-compliant pages are fixed.

> **To stop the loop**: Press `Ctrl+C` in the terminal.

## Execution Command

1. Start the fix bot loop:
```bash
cd /home/tomito/Desktop/v.lkhere && while true; do
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🚀 [$(date '+%Y-%m-%d %H:%M:%S')] Starting Fix Bot batch..."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  python3 fix_short_descriptions_bot.py
  echo ""
  echo "✅ Batch completed. Sleeping for 20 minutes..."
  echo "⏳ Next batch at: $(date -d '+20 minutes' '+%H:%M:%S')"
  sleep 1200
done
```
