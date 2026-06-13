#!/usr/bin/env bash
# Build HackerOne Basic Auth header and test GET /v1/hackers/me
#
# Usage:
#   export HACKERONE_API_USERNAME=mpeshekhonov
#   export HACKERONE_API_TOKEN='your+token/with=chars'
#   ./scripts/hackerone-auth-test.sh
#
# Or interactive (token hidden):
#   ./scripts/hackerone-auth-test.sh

set -euo pipefail

USERNAME="${HACKERONE_API_USERNAME:-mpeshekhonov}"
TOKEN="${HACKERONE_API_TOKEN:-}"

if [[ -z "$TOKEN" ]]; then
  read -r -p "HackerOne API username [$USERNAME]: " input_user
  [[ -n "$input_user" ]] && USERNAME="$input_user"
  read -r -s -p "HackerOne API token: " TOKEN
  echo
fi

if [[ -z "$TOKEN" ]]; then
  echo "Error: token is empty" >&2
  exit 1
fi

# macOS + Linux compatible base64 (no line wrap)
if base64 --help 2>&1 | grep -q '\-w'; then
  B64=$(printf '%s' "${USERNAME}:${TOKEN}" | base64 -w 0)
else
  B64=$(printf '%s' "${USERNAME}:${TOKEN}" | base64 | tr -d '\n')
fi

echo
echo "=== Basic Auth (copy for Authorization header) ==="
echo "Authorization: Basic ${B64}"
echo
echo "=== curl -u (same thing, often easier) ==="
echo "curl -u '${USERNAME}:<TOKEN>' 'https://api.hackerone.com/v1/hackers/me' -H 'Accept: application/json'"
echo
echo "=== Live test ==="

HTTP_CODE=$(curl -sS -o /tmp/h1-me.json -w '%{http_code}' \
  -H "Accept: application/json" \
  -H "Authorization: Basic ${B64}" \
  "https://api.hackerone.com/v1/hackers/me/reports")

echo "HTTP ${HTTP_CODE}"
head -c 500 /tmp/h1-me.json
echo

if [[ "$HTTP_CODE" == "200" ]]; then
  echo
  echo "OK — creds work. Put in secrets/.env.bounty:"
  echo "HACKERONE_API_IDENTIFIER=${USERNAME}"
  echo "HACKERONE_API_USERNAME=${USERNAME}"
  echo "HACKERONE_API_TOKEN=<same token>"
  exit 0
fi

echo
  echo "401 on /hackers/me is normal for some accounts — this script uses /hackers/me/reports."
echo "Regenerate token at https://hackerone.com/settings/api_token/edit and paste immediately."
exit 1
