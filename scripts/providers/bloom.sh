#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
export LPF_ROOT="${LPF_ROOT:-$REPO_ROOT}"

exec bash "$REPO_ROOT/skills/page-visuals/scripts/providers/bloom.sh" "$@"
