#!/usr/bin/env bash
set -euo pipefail
if [[ -z "${GITHUB_TOKEN:-}" ]]; then echo "ERROR: GITHUB_TOKEN is not set." >&2; exit 1; fi
if ! command -v gh >/dev/null 2>&1; then echo "ERROR: gh not installed." >&2; exit 1; fi
echo "$GITHUB_TOKEN" | gh auth login --with-token >/dev/null 2>&1 || true

ISSUE_ID="${1:-}"; [[ -n "$ISSUE_ID" ]] || { echo "usage: ./bootstrap.sh <issue-id> [owner/repo]"; exit 1; }
REPO="${2:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"

rm -rf workdir
gh repo clone "$REPO" workdir >/dev/null
cd workdir
  # --- CI auth for pushes inside workdir ---
  if [ -n "$GITHUB_ACTIONS" ]; then
    echo "::add-mask::$GITHUB_TOKEN"
    REPO_EFFECTIVE="${2:-${REPO:-$GITHUB_REPOSITORY}}"
    if [ -z "$REPO_EFFECTIVE" ]; then echo "REPO_EFFECTIVE empty; cannot configure remote" >&2; exit 1; fi
    git remote set-url origin "https://x-access-token:${GITHUB_TOKEN}@github.com/${REPO_EFFECTIVE}.git"
    echo "[debug] remotes after set-url:"; git remote -v
  fi
  # --- end CI auth ---

DEFAULT_BRANCH="$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)"
AGENT_SPEC="${AGENT_SPEC:-./agent_spec.yaml}"
[[ -f "$AGENT_SPEC" ]] || { echo "ERROR: agent_spec.yaml not found."; exit 1; }

TITLE="$(gh issue view "$ISSUE_ID" --json title -q .title)" || true
if [[ -z "${TITLE:-}" ]]; then echo "ERROR: issue #$ISSUE_ID not found."; exit 1; fi

SLUG="$(printf '%s' "$TITLE" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g' | sed -E 's/^-+|-+$//g')"
BRANCH="fix/${ISSUE_ID}-${SLUG}"

git fetch --all --prune >/dev/null
git checkout -b "$BRANCH" "origin/$DEFAULT_BRANCH" 2>/dev/null || git checkout -b "$BRANCH"

set +e; git rebase "origin/${DEFAULT_BRANCH}"; set -e

if [[ -f package.json || -f pyproject.toml || -f go.mod ]]; then
# ensure git identity (CI/local)

if ! git config user.name >/dev/null 2>&1; then

  git config user.name "${GITHUB_ACTOR:-github-actions[bot]}";

fi

if ! git config user.email >/dev/null 2>&1; then

  git config user.email "${GIT_AUTHOR_EMAIL:-41898282+github-actions[bot]@users.noreply.github.com}";

fi

  git commit --allow-empty -m "chore(ci): bootstrap branch for #${ISSUE_ID}"
  : # ensure git identity in current repo (workdir)
  if ! git config user.name >/dev/null 2>&1; then
    git config user.name "${GITHUB_ACTOR:-github-actions[bot]}"
  fi
  if ! git config user.email >/dev/null 2>&1; then
    git config user.email "${GIT_AUTHOR_EMAIL:-41898282+github-actions[bot]@users.noreply.github.com}"
  fi
# --- CI auth for pushes ---

if [ -n "$GITHUB_ACTIONS" ]; then

  echo "::add-mask::$GITHUB_TOKEN"

  REPO_EFFECTIVE="${2:-${REPO:-$GITHUB_REPOSITORY}}"

  if [ -z "$REPO_EFFECTIVE" ]; then echo "REPO_EFFECTIVE empty; cannot configure remote" >&2; exit 1; fi

  git remote set-url origin "https://x-access-token:${GITHUB_TOKEN}@github.com/${REPO_EFFECTIVE}.git"

  echo "[debug] remotes after set-url:"; git remote -v

fi

# --- end CI auth for pushes ---
  push_with_token -u origin HEAD
echo "::add-mask::$GITHUB_TOKEN"
REPO="${2:-${REPO:-$GITHUB_REPOSITORY}}"
echo "::add-mask::$GITHUB_TOKEN"
fi

echo "NEXT: follow agent_spec.yaml workflow"
