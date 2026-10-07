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

nvm install
nvm use

# Persist the nvm-selected Node for the session's later commands.
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  {
    echo "export NVM_DIR=\"$NVM_DIR\""
    echo ". \"$NVM_DIR/nvm.sh\""
    echo "nvm use >/dev/null"
  } >> "$CLAUDE_ENV_FILE"
fi

npm install
