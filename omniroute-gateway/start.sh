#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# OmniRoute Gateway — Local Starter
# ─────────────────────────────────────────────────────────────────────────────
# يشغّل OmniRoute على 127.0.0.1:20128 (loopback) من نفس repo.
# البوت كيتصل عليه على: http://127.0.0.1:20128/v1/chat/completions
#
# الاستعمال:
#   ./omniroute-gateway/start.sh
# أو مع مفاتيح إضافية:
#   OPENROUTER_API_KEY=sk-or-... STORAGE_ENCRYPTION_KEY=... ./omniroute-gateway/start.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail
cd "$(dirname "$0")"

export OMNIROUTE_SERVER_HOST="${OMNIROUTE_SERVER_HOST:-127.0.0.1}"
export PORT="${PORT:-20128}"

# تجهيز الحزمة إن لم تكن مثبتة محلياً
if [ ! -d node_modules ]; then
  echo "📦 Installing OmniRoute (first run only)..."
  npm install --no-audit --no-fund
fi

# تحميل مفاتيح المستخدم من ~/.omniroute/.env (إن وجد — لا أسرار داخل repo)
if [ -f "${HOME}/.omniroute/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "${HOME}/.omniroute/.env"
  set +a
fi

echo "🚀 Starting OmniRoute on http://${OMNIROUTE_SERVER_HOST}:${PORT} ..."
exec ./node_modules/.bin/omniroute