import os
import json
import glob
import time
import sys
from datetime import timedelta

def get_processed_count():
    files = glob.glob('data/content/*.json')
    total = len(files)
    processed = 0
    for f in files:
        try:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                desc = data.get('ai_content', {}).get('desc_ar', '')
                if "مشاهدة وتحميل" not in desc:
                    processed += 1
        except Exception:
            pass
    return processed, total

def main():
    print("جاري حساب الملفات وبدء المراقبة المباشرة (Live)... هادشي غياخد ثواني باش يحسب السرعة")
    
    last_processed, total = get_processed_count()
    last_time = time.time()
    speeds = [] 
    
    while True:
        try:
            time.sleep(3)
            current_processed, _ = get_processed_count()
            current_time = time.time()
            
            diff_processed = current_processed - last_processed
            diff_time = current_time - last_time
            
            if diff_processed > 0:
                speed = diff_processed / diff_time
                speeds.append(speed)
                if len(speeds) > 5:
                    speeds.pop(0)
            
            avg_speed = sum(speeds) / len(speeds) if speeds else 0
            
            remaining = total - current_processed
            eta_str = "جاري الحساب..."
            if avg_speed > 0:
                eta_seconds = remaining / avg_speed
                eta_str = str(timedelta(seconds=int(eta_seconds)))
                
            bar_length = 40
            bar = int(bar_length * current_processed / total) if total else 0
            
            sys.stdout.write('\033[H\033[J')
            sys.stdout.flush()
            
            print(f"\n🚀 Tomato SEO - Live Refactor Progress 🚀")
            print(f"=" * 50)
            print(f"[{'█' * bar}{'░' * (bar_length - bar)}] {current_processed}/{total}")
            print(f"التقدم     : {(current_processed/total)*100:.2f}%")
            print(f"السرعة     : {avg_speed:.2f} باج فالثانية")
            print(f"الوقت الباقي: {eta_str}")
            print(f"=" * 50)
            print("اضغط Ctrl+C باش تحبس المراقبة (السكريبت غيبقى خدام ف الخلفية)")
            
            last_processed = current_processed
            last_time = current_time
            
        except KeyboardInterrupt:
            print("\nتم إيقاف المراقبة. العملية باقا خدامة ف الخلفية!")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()
