#!/bin/bash
# SessionStart hook (§2.7). Warns, does not block — not every session
# touches gated work.
if ! docker ps --filter name=harness_postgres --filter status=running -q 2>/dev/null | grep -q .; then
  echo "[harness-os] Warning: harness_postgres is not running. Gated writes will fail closed until it's started (docker compose -f <harness-os repo>/db/docker-compose.yml up -d)." >&2
fi
exit 0
