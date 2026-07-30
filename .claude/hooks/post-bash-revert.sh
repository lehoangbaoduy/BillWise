#!/bin/bash
# PostToolUse hook: Bash. Reactive backstop for whatever enforce-gate.sh's
# Bash-write heuristic misses (§2.1 component 4). Phase 1 scope is narrow but
# highest-value: the three CONST-CORE-004-tracked config files, since those
# protect the enforcement mechanism itself. Broader gatedGlobs reverting (any
# source file with no open gate) extends this same script once Phase 2's
# spec/test gate can answer "is there an open gate covering this file" — not
# a rewrite.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PAYLOAD="$(cat)"
eval "$(printf '%s' "$PAYLOAD" | node "$SCRIPT_DIR/parse-tool-call.mjs")"

if [[ "$HARNESS_TOOL_NAME" != "Bash" ]]; then
  exit 0
fi

cd "$HARNESS_PROJECT_PATH"

# Open Item #9: this backstop needs a git repo to diff against. harness init
# should require this precondition; a non-git project just gets a warning,
# not a crash — component 1's PreToolUse gate is still the primary defense.
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "[post-bash-revert] Warning: $HARNESS_PROJECT_PATH is not a git repository — the revert backstop cannot run (Open Item #9)." >&2
  exit 0
fi

TRACKED_FILES=(".claude/harness.config.json" ".claude/hooks/enforce-gate.sh" ".claude/settings.json")

for FILE in "${TRACKED_FILES[@]}"; do
  STATUS_LINE="$(git status --porcelain -- "$FILE" 2>/dev/null || true)"
  if [[ -z "$STATUS_LINE" ]]; then
    continue
  fi

  echo "[post-bash-revert] Uncommitted change to $FILE detected after a Bash call — reverting (CONST-CORE-004)." >&2
  if [[ "$STATUS_LINE" == '??'* ]]; then
    rm -f "$FILE"
  else
    git checkout -- "$FILE"
  fi

  docker exec harness_gate_daemon node cli/dist/log-revert.js \
    --project-path "$HARNESS_PROJECT_PATH" \
    --file "$FILE" >&2 || true
done

exit 0
