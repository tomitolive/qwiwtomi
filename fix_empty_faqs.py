import os
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

data_dir = 'data/content'
count = 0
for filename in os.listdir(data_dir):
    if not filename.endswith('.json'):
        continue
    filepath = os.path.join(data_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    ai = data.get('ai_content', {})
    faq = ai.get('faq', [])
    
    if not faq or len(faq) == 0:
        title = data.get('title_ar') or data.get('title') or "هذا العمل"
        if data.get('first_air_date') or data.get('number_of_seasons'):
            # TV
            new_faq = [
                { "q": f"متى تتوفر حلقات {title} على موقع توميتو؟", "a": f"حلقات مسلسل {title} متاحة للمشاهدة والتحميل تزامناً مع موعد طرحها حصرياً وبجودة عالية مترجمة." },
                { "q": f"هل يمكنني المشاهدة بالجودة العالية 1080p؟", "a": f"نعم، نوفر سيرفرات مشاهدة متعددة تدعم جودة 1080p وتعمل بدون انقطاع لضمان أفضل تجربة لـ {title}." }
            ]
        else:
            # Movie
            new_faq = [
                { "q": f"متى يتوفر فيلم {title} على موقع توميتو؟", "a": f"فيلم {title} متاح الآن للمشاهدة والتحميل مباشرةً على موقع توميتو بجودة عالية مترجماً إلى العربية." },
                { "q": f"هل يمكنني تحميل {title} بجودة عالية؟", "a": f"نعم، يمكنك تحميل {title} عبر الضغط على زر التحميل، وتتوفر جودات متعددة تصل إلى Full HD و 4K." }
            ]
            
        data['ai_content']['faq'] = new_faq
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        count += 1

logging.info(f"Fixed {count} files with empty FAQs.")
