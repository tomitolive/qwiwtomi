#!/usr/bin/env python3
"""test_gateway.py — اختبار اتصال البوت بـ OmniRoute (مع أو بدون السيرفر).

يغطي:
  1. فحص إعدادات AI_MODELS (يجب أن تشير إلى OmniRoute).
  2. الدوال القالبية (لا تحتاج سيرفراً — تعمل دائماً).
  3. إن كان السيرفر شغالاً: طلب حي صغير عبر _call_openai_llm.
  4. مع --deep: استدعاء generate_bilingual_description كاملاً (يستهلك وقتاً و tokens).

الاستعمال:
  python test_gateway.py            # فحص سريع
  python test_gateway.py --deep     # الفحص الكامل + توليد وصف حقيقي

المتغيرات:
  OMNIROUTE_URL  (افتراضياً: مضبوطة من ai_engine -> http://127.0.0.1:20128/v1/chat/completions)
"""
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SERVER_OK = False


def check_server(url):
    """Check whether OmniRoute responds (HTTP 401/403 تعني أن السيرفر حي أيضاً)."""
    global SERVER_OK
    base = url.rsplit("/v1/chat/completions", 1)[0] if "/v1/chat/completions" in url else url
    probe = f"{base.strip('/')}/v1/models"
    try:
        req = urllib.request.Request(probe, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            code = resp.status
    except urllib.error.HTTPError as exc:
        # HTTP 401/403 = السيرفر موجود ويستجيب لكن يتطلب auth — مقبول للفحص
        code = exc.code
    except Exception as exc:
        print(f"ℹ️  OmniRoute not reachable at {base}: {exc}")
        print("   (سيتم فحص الواجهة القالبية فقط — وعند تشغيل السيرفر يُعاد الاختبار)")
        return False
    SERVER_OK = True
    print(f"✅ OmniRoute reachable at {probe} (HTTP {code})")
    return True


def test_config(ai_engine):
    print("== 1) AI_MODELS config ==")
    for m in ai_engine.AI_MODELS:
        key = (m.get("api_key") or "").strip()
        masked = (key[:6] + "...") if key else "(بدون مفتاح)"
        print(f"   • name    = {m['name']}")
        print(f"     url     = {m['url']}")
        print(f"     model   = {m['model_id']}")
        print(f"     api_key = {masked}")
    if len(ai_engine.AI_MODELS) != 1 or ai_engine.AI_MODELS[0]["name"].lower() != "omniroute":
        raise SystemExit("❌ AI_MODELS لم يُعدَّ إلى OmniRoute! راجع ai_engine.py")
    print("   ✅ كل طلبات AI تتجه إلى OmniRoute عبر عنصر واحد")


def test_templates(ai_engine):
    print("== 2) Template functions (لا تحتاج سيرفراً) ==")
    mt = ai_engine.generate_meta_tags("فيلم الاختبار", "Test Movie", 2026, ["دراما"], "movie")
    assert mt["meta_desc"] and mt["keywords"], "generate_meta_tags رجعت قيماً فارغة!"
    print(f"   ✅ generate_meta_tags → {mt['meta_desc'][:60]}...")

    op = ai_engine.generate_tomito_opinion("فيلم الاختبار", "Test Movie", 2026, "movie")
    assert op, "generate_tomito_opinion رجعت فارغاً!"
    print(f"   ✅ generate_tomito_opinion → {op[:60]}...")

    intro, outro = ai_engine.generate_page_intro_outro("فيلم الاختبار", "Test Movie", 2026, "movie", ["دراما"])
    assert intro and outro, "intro/outro فارغ(a)!"
    print(f"   ✅ generate_page_intro_outro → {intro[:60]}...")

    faq = ai_engine.generate_faq("فيلم الاختبار", "Test Movie", 2026, "movie", overview="قصة اختبارية.")
    assert isinstance(faq, list) and faq, "generate_faq رجعت قائمة فارغة!"
    print(f"   ✅ generate_faq → {len(faq)} أسئلة")


def test_live_call(ai_engine):
    if not SERVER_OK:
        print("⚠️  تم تخطي الطلب الحي (السيرفر غير شغال).")
        return
    print("== 3) طلب حي عبر OmniRoute (_call_openai_llm) ==")
    res, model_used = ai_engine._call_openai_llm(
        "You are a test assistant.",
        "Reply with the single word: OK",
        max_retries=2,
    )
    if res:
        print(f"   ✅ نجح عبر {model_used} → {res[:120]}")
    else:
        raise SystemExit("❌ الطلب الحي فشل — تحقق من السيرفر ومن AI_MODELS.")


def test_deep(ai_engine):
    """توليد فعلي لوصف كامل (مكلف قليلاً في الوقت وtokens)."""
    if not SERVER_OK:
        print("⚠️  --deep يتطلب السيرفر شغالاً.")
        return
    print("== 4) generate_bilingual_description (فحص كامل) ==")
    data = ai_engine.generate_bilingual_description(
        title_ar="المهمة المستحيلة",
        title_en="Mission Impossible",
        year=2025,
        genres_ar=["أكشن", "إثارة"],
        media_type="movie",
        overview_ar="قصة اختبارية عن مهمة خطيرة.",
        overview_en="A test story about a dangerous mission.",
    )
    assert isinstance(data, dict) and data.get("desc_ar") and data.get("desc_en"), "الوصف ناقص!"
    print(f"   ✅ desc_ar   = {data['desc_ar'][:80]}...")
    print(f"   ✅ desc_en   = {data['desc_en'][:80]}...")
    print(f"   ✅ meta_desc = {len(data.get('meta_desc', ''))} حرف")
    print(f"   ✅ opinion_ar = {data.get('opinion_ar', '')[:60]}...")


def main():
    import ai_engine

    print("🧪 اختبار بوابة OmniRoute للبوت")
    print("=" * 60)
    url = os.getenv("OMNIROUTE_URL", ai_engine.OMNIROUTE_URL)
    print(f"🌐 OMNIROUTE_URL = {url}")
    check_server(url)
    print()
    test_config(ai_engine)
    print()
    test_templates(ai_engine)
    print()
    if "--deep" in sys.argv:
        test_deep(ai_engine)
    else:
        test_live_call(ai_engine)
    print("=" * 60)
    print("✅ اكتمل الاختبار بنجاح.")


if __name__ == "__main__":
    main()