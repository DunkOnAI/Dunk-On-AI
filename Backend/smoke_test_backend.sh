#!/usr/bin/env bash

set -euo pipefail

# Super quick local backend check before pushing.
# Usage:
#   bash Backend/smoke_test_backend.sh
# Optional:
#   BASE_URL=http://127.0.0.1:5000 bash Backend/smoke_test_backend.sh

BASE_URL="${BASE_URL:-http://127.0.0.1:5000}"

echo "[smoke] checking ${BASE_URL}/api/health"
curl -fsS "${BASE_URL}/api/health" | sed -n '1,20p'
echo

echo "[smoke] checking ${BASE_URL}/api/supabase/health"
curl -fsS "${BASE_URL}/api/supabase/health" | sed -n '1,40p'
echo

EMAIL="smoke_$(date +%s)@example.com"
PASS="password123"

echo "[smoke] signup test user ${EMAIL}"
curl -fsS -X POST "${BASE_URL}/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASS}\",\"username\":\"smoke_user\"}" \
  | sed -n '1,80p'
echo

echo "[smoke] login test user ${EMAIL}"
curl -fsS -X POST "${BASE_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASS}\"}" \
  | sed -n '1,80p'
echo

echo "[smoke] done"
