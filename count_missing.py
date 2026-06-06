import os
import json
import glob

missing = 0
total = 0
for f in glob.glob("data/content/*.json"):
    total += 1
    with open(f, "r", encoding="utf-8") as fp:
        try:
            d = json.load(fp)
        except:
            continue
        ai = d.get("ai_content", {})
        desc_ar = ai.get("desc_ar", "")
        # A rich story is usually multi-sentence and doesn't start exactly with "مشاهدة وتحميل"
        if not desc_ar or desc_ar.startswith("مشاهدة وتحميل") or "مترجم بجودة عالية" in desc_ar:
            missing += 1

print(f"Missing Story: {missing} / {total}")
