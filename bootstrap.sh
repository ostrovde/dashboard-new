#!/usr/bin/env bash
# --- FORCE origin to correct repo URL (early) ---
REPO_EFFECTIVE="${2:-${REPO:-$GITHUB_REPOSITORY}}"
if [ -z "$REPO_EFFECTIVE" ] || [ "$REPO_EFFECTIVE" = "origin" ]; then
  echo "[bootstrap] Bad REPO_EFFECTIVE='$REPO_EFFECTIVE'" >&2
  exit 1
fi

fix_origin() {
  # если бежим в CI с токеном — используем x-access-token
  if [ -n "${GITHUB_ACTIONS:-}" ] && [ -n "${GITHUB_TOKEN:-}" ]; then
    echo "::add-mask::$GITHUB_TOKEN"
fix_origin 
  else
fix_origin 
  fi
  echo "[bootstrap] origin now -> $(git remote get-url origin)" >&2
}

# на случай, если дальше где-то используют NWO — синхронизируем его
NWO="${REPO_EFFECTIVE}"
# --- END FORCE ---
# --- begin: FORCE origin to correct repo URL ---
NWO="${REPO_EFFECTIVE}"
# Определяем owner/repo (NWO) надёжно и один раз
REPO_EFFECTIVE="${2:-${REPO:-$GITHUB_REPOSITORY}}"
case "$REPO_EFFECTIVE" in
  ""|origin) echo "[bootstrap] Bad REPO_EFFECTIVE='$REPO_EFFECTIVE'" >&2; exit 1;;
  */*) ;; # ok
  *) echo "[bootstrap] REPO_EFFECTIVE must look like owner/repo, got '$REPO_EFFECTIVE'"; exit 1;;
esac

# Без условий: ставим корректный origin прямо сейчас.
if [ -n "$GITHUB_ACTIONS" ] && [ -n "$GITHUB_TOKEN" ]; then
  echo "::add-mask::$GITHUB_TOKEN"
fix_origin
else
fix_origin
fi

# Упрощённый помощник: перед любым push всегда переставляем origin ещё раз.
fix_origin(){ 
  if [ -n "$GITHUB_ACTIONS" ] && [ -n "$GITHUB_TOKEN" ]; then
fix_origin
  else
fix_origin
  fi
  # Для наглядности в логах:
  echo "[bootstrap] origin now -> $(git remote get-url origin)" >&2
}
# Немедленно починим origin в самом начале выполнения скрипта:
fix_origin
# --- end: FORCE origin to correct repo URL ---
# --- begin: robust origin fixer ---
fix_origin(){
  # Определяем NWO (owner/repo). Берём уже вычисленный REPO_EFFECTIVE, иначе REPO, иначе GITHUB_REPOSITORY
  local NWO="${REPO_EFFECTIVE:-${REPO:-$GITHUB_REPOSITORY}}"
  if [ -z "$NWO" ] || [ "$NWO" = "origin" ]; then
    echo "[bootstrap] Bad repo value (NWO='$NWO')" >&2
    return 1
  fi

  local want="https://github.com/${REPO_EFFECTIVE}.git"
  local cur
  cur="$(git remote get-url origin 2>/dev/null || true)"

  # Если origin пустой, указывает на /origin.git, имеет хвостовой слэш или просто не наш repo — чиним.
  if [ -z "$cur" ] || ! printf "%s" "$cur" | grep -Eq "github\.com/${REPO_EFFECTIVE}(\.git)?/?$"; then
    if [ -n "$GITHUB_ACTIONS" ] && [ -n "$GITHUB_TOKEN" ]; then
      echo "::add-mask::$GITHUB_TOKEN"
fix_origin
    else
fix_origin
    fi
  fi
}
# --- end: robust origin fixer ---

# === hard guard for origin url & safe push ===
REPO_EFFECTIVE="${2:-${REPO:-$GITHUB_REPOSITORY}}"
case "$REPO_EFFECTIVE" in */*) ;; ""|origin) echo "[bootstrap] Bad REPO_EFFECTIVE=\"$REPO_EFFECTIVE\"" >&2; exit 1;; esac
SAFE_URL="https://x-access-token:${GITHUB_TOKEN}@github.com/${REPO_EFFECTIVE}.git"

fix_origin(){
  local cur; cur=$(git remote get-url origin 2>/dev/null || echo "")
  if [ -z "$cur" ] || echo "$cur" | grep -qE "/origin\.git$"; then
    fix_origin
  fi
}

push_with_token(){
  fix_origin
  local BR="${1:-${NEW_BRANCH:-$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)}}"
  if [ -n "${GITHUB_ACTIONS:-}" ] && [ -n "${GITHUB_TOKEN:-}" ]; then
    echo "::add-mask::$GITHUB_TOKEN"
  fi
  fix_origin
  printf "[bootstrap] Пушим ветку: %s → origin\n" "$BR" >&2
  git remote -v >&2
  fix_origin; git push -u origin "$BR"
}
# === end guard ===
set -euo pipefail

# --- stable repo detection ---
REPO_EFFECTIVE="${2:-${REPO:-$GITHUB_REPOSITORY}}"
case "$REPO_EFFECTIVE" in
  */*) ;;
  ""|origin) echo "[bootstrap] Bad REPO_EFFECTIVE=\"$REPO_EFFECTIVE\"" >&2; exit 1;;
esac

# --- safe push helper (uses REPO_EFFECTIVE) ---
push_with_token(){
  fix_origin
  local BR="${1:-${NEW_BRANCH:-$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)}}"
  if [ -n "${GITHUB_ACTIONS:-}" ] && [ -n "${GITHUB_TOKEN:-}" ]; then
    echo "::add-mask::$GITHUB_TOKEN"
    fix_origin
  fi
  # если origin внезапно стал https://github.com/${REPO_EFFECTIVE:-${REPO:-$GITHUB_REPOSITORY}}.git — починим
  if git remote get-url origin 2>/dev/null | grep -q "/origin\.git$"; then
    fix_origin
  fi
  printf "[bootstrap] Пушим ветку: %s → origin\n" "$BR" >&2
  git remote -v >&2
  fix_origin; git push -u origin "$BR"
}

# --- helpers (auto) ---

log(){ printf "[bootstrap] %s\n" "$*" >&2; }

warn(){ printf "[bootstrap][WARN] %s\n" "$*" >&2; }

repo_effective(){

  # 1) позиционный аргумент $2 > 2) REPO > 3) GITHUB_REPOSITORY

  local r="${2:-${REPO:-$GITHUB_REPOSITORY}}"

  printf "%s" "$r"

}

push_with_token(){
  fix_origin

  local BR="${NEW_BRANCH:-$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo)}"

  local NWO="$(repo_effective "$@")"

  [ -n "$BR" ] || { warn "Пустое имя ветки"; return 1; }

  if [ -n "$GITHUB_ACTIONS" ] && [ -n "$GITHUB_TOKEN" ] && [ -n "$NWO" ]; then

    echo "::add-mask::$GITHUB_TOKEN"

    fix_origin

  fi

  log "Пушим ветку: ${BR} → origin"

  fix_origin; git push -u origin "$BR"

}

# --- helpers (auto) ---

set -euo pipefail

if [[ -z "${GITHUB_TOKEN:-}" ]]; then echo "ERROR: GITHUB_TOKEN is not set." >&2; exit 1; fi

if ! command -v gh >/dev/null 2>&1; then echo "ERROR: gh not installed." >&2; exit 1; fi

echo "$GITHUB_TOKEN" | gh auth login --with-token >/dev/null 2>&1 || trueISSUE_ID="${1:-}"; [[ -n "$ISSUE_ID" ]] || { echo "usage: ./bootstrap.sh <issue-id> [owner/repo]"; exit 1; }

REPO="${2:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"rm -rf workdir

gh repo clone "$REPO" workdir >/dev/null

cd workdirDEFAULT_BRANCH="$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)"

AGENT_SPEC="${AGENT_SPEC:-./agent_spec.yaml}"

[[ -f "$AGENT_SPEC" ]] || { echo "ERROR: agent_spec.yaml not found."; exit 1; }TITLE="$(gh issue view "$ISSUE_ID" --json title -q .title)" || true

if [[ -z "${TITLE:-}" ]]; then echo "ERROR: issue #$ISSUE_ID not found."; exit 1; fiSLUG="$(printf '%s' "$TITLE" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g' | sed -E 's/^-+|-+$//g')"

BRANCH="fix/${ISSUE_ID}-${SLUG}"git fetch --all --prune >/dev/null

git checkout -b "$BRANCH" "origin/$DEFAULT_BRANCH" 2>/dev/null || git checkout -b "$BRANCH"set +e; git rebase "origin/${DEFAULT_BRANCH}"; set -eif [[ -f package.json || -f pyproject.toml || -f go.mod ]]; then

# ensure git identity (CI/local)if ! git config user.name >/dev/null 2>&1; then  git config user.name "${GITHUB_ACTOR:-github-actions[bot]}";fiif ! git config user.email >/dev/null 2>&1; then  git config user.email "${GIT_AUTHOR_EMAIL:-41898282+github-actions[bot]@users.noreply.github.com}";fi  git commit --allow-empty -m "chore(ci): bootstrap branch for #${ISSUE_ID}"

  : # ensure git identity in current repo (workdir)

  if ! git config user.name >/dev/null 2>&1; then

    git config user.name "${GITHUB_ACTOR:-github-actions[bot]}"

  fi

  if ! git config user.email >/dev/null 2>&1; then

    git config user.email "${GIT_AUTHOR_EMAIL:-41898282+github-actions[bot]@users.noreply.github.com}"

  fi

# --- CI auth for pushes ---if [ -n "$GITHUB_ACTIONS" ]; then  echo "::add-mask::$GITHUB_TOKEN"  REPO_EFFECTIVE="${2:-${REPO:-$GITHUB_REPOSITORY}}"  if [ -z "$REPO_EFFECTIVE" ]; then echo "REPO_EFFECTIVE empty; cannot configure remote" >&2; exit 1; fi  fix_origin
# --- end CI auth for pushes ---

  fix_origin; git push -u origin HEAD

echo "::add-mask::$GITHUB_TOKEN"

REPO="${2:-${REPO:-$GITHUB_REPOSITORY}}"

echo "::add-mask::$GITHUB_TOKEN"

fiecho "NEXT: follow agent_spec.yaml workflow"

