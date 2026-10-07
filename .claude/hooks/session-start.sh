#!/bin/bash
# Prepares Claude Code cloud sessions: installs the Node and npm versions from
# .nvmrc, then the project dependencies. Local sessions are left alone.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}"

export NVM_DIR="${NVM_DIR:-/opt/nvm}"
# shellcheck disable=SC1091
. "$NVM_DIR/nvm.sh"

# nvm's version resolution/download and npm's registry fetch can fail on a
# transient network blip during container boot. Retry a few times so one bad
# request doesn't silently skip the rest of the hook.
retry() {
  local attempts=3
  local delay=5
  local n=1
  until "$@"; do
    if [ "$n" -ge "$attempts" ]; then
      echo "session-start: '$*' failed after $attempts attempts" >&2
      return 1
    fi
    echo "session-start: '$*' failed (attempt $n/$attempts), retrying in ${delay}s" >&2
    sleep "$delay"
    n=$((n + 1))
  done
}

retry nvm install
nvm use

# Persist the nvm-selected Node for the session's later commands.
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  {
    echo "export NVM_DIR=\"$NVM_DIR\""
    echo ". \"$NVM_DIR/nvm.sh\""
    echo "nvm use >/dev/null"
  } >> "$CLAUDE_ENV_FILE"
fi

retry npm install
