#!/usr/bin/env bash
# Usage: ./bootstrap.sh <issue-id> [owner/repo]
set -euo pipefail

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "ERROR: GITHUB_TOKEN is not set." >&2; exit 1; fi
export GITHUB_TOKEN

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: gh CLI not installed." >&2; exit 1; fi

echo "$GITHUB_TOKEN" | gh auth login --with-token >/dev/null 2>&1 || true

ISSUE_ID="${1:-}"; [[ -n "$ISSUE_ID" ]] || { echo "usage: ./bootstrap.sh <issue-id> [owner/repo]"; exit 1; }
REPO="${2:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"

WORKDIR="workdir"
rm -rf "$WORKDIR"
gh repo clone "$REPO" "$WORKDIR" >/dev/null
cd "$WORKDIR"

DEFAULT_BRANCH="$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)"
AGENT_SPEC="${AGENT_SPEC:-./agent_spec.yaml}"
[[ -f "$AGENT_SPEC" ]] || { echo "ERROR: agent_spec.yaml not found."; exit 1; }

TITLE="$(gh issue view "$ISSUE_ID" --json title -q .title)"
[[ -n "$TITLE" ]] || { echo "ERROR: Issue #$ISSUE_ID not found."; exit 1; }

SLUG="$(printf '%s' "$TITLE" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g' | sed -E 's/^-+|-+$//g')"
BRANCH="fix/${ISSUE_ID}-${SLUG}"

git fetch --all --prune >/dev/null
git checkout -b "$BRANCH"

set +e
git rebase "origin/${DEFAULT_BRANCH}"
set -e

echo "Branch: $BRANCH"
if [[ -f package.json || -f pyproject.toml || -f go.mod ]]; then
  git commit --allow-empty -m "chore(ci): bootstrap branch for #${ISSUE_ID}"
  git push -u origin HEAD
fi

cat <<'EOF'
NEXT: follow agent_spec.yaml workflow:
1) discover_and_scope → 2) reproduce_and_baseline → 3) implement_iteratively
4) verify_and_harden → 5) open_pr → 6) merge_and_followup
EOF
