#!/usr/bin/env bash
# Build the orchestration handoff bundle: everything needed to reproduce the
# campaign's continuity that is NOT in the git repository.
#
# The bundle CONTAINS PROVIDER CREDENTIALS (codex auth, claude credentials,
# agy/gemini state). It is written to the login home — never into the repo,
# never committed, never pushed. Copy it off-site with scp if extra safety is
# wanted before a maintenance window.
set -euo pipefail
umask 077

login_home=$(getent passwd "$(id -u)" | cut -d: -f6)
repo=${HANDOFF_REPO:-/pscratch/sd/j/josephrb/MINERvA-OmniFold}
stamp=$(date -u +%Y%m%dT%H%M%SZ)
out=${HANDOFF_OUT:-${login_home}/orchestration-handoff-${stamp}.tar.gz}
work=$(mktemp -d "${login_home}/.handoff-${stamp}.XXXXXX")
trap 'rm -rf -- "$work"' EXIT

stage=${work}/orchestration-handoff-${stamp}
mkdir -p "$stage"

# 1. Provider session stores and credentials (continuity of every UUID).
mkdir -p "$stage/homes"
cp -a "$login_home/codex-homes/personal" "$stage/homes/codex-personal"
cp -a "$login_home/codex-homes/school" "$stage/homes/codex-school"
for name in personal school; do
  src="$login_home/claude-homes/$name"
  dst="$stage/homes/claude-$name"
  mkdir -p "$dst/.claude"
  [[ -f "$src/.claude.json" ]] && cp -a "$src/.claude.json" "$dst/"
  for item in projects .credentials.json settings.json CLAUDE.md; do
    [[ -e "$src/.claude/$item" ]] && cp -a "$src/.claude/$item" "$dst/.claude/"
  done
done
# Legacy nested school home holding the migrated A/B/C sessions.
legacy="$login_home/claude-homes/school/claude-homes/personal"
if [[ -d "$legacy" ]]; then
  dst="$stage/homes/claude-school-legacy"
  mkdir -p "$dst/.claude"
  [[ -f "$legacy/.claude.json" ]] && cp -a "$legacy/.claude.json" "$dst/"
  for item in projects .credentials.json settings.json; do
    [[ -e "$legacy/.claude/$item" ]] && cp -a "$legacy/.claude/$item" "$dst/.claude/"
  done
fi
[[ -d "$login_home/.gemini" ]] && cp -a "$login_home/.gemini" "$stage/homes/gemini-agy-state"
[[ -x "$login_home/.local/bin/agy" ]] && install -D "$login_home/.local/bin/agy" "$stage/homes/bin/agy"

# 2. Untracked orchestration state from the repo (spool, ledgers, run
#    transcripts, receipts). Tracked files live on GitHub already.
mkdir -p "$stage/repo-untracked"
(
  cd "$repo"
  { git ls-files --others docs/orchestration | grep -v __pycache__ || true
    [[ -f .mcp.json ]] && git ls-files --others .mcp.json || true
  } | tar -cf - -T - 2>/dev/null | tar -xf - -C "$stage/repo-untracked"
)

# 3. Environment snapshot needed for restore.
{
  echo "created_utc: ${stamp}"
  echo "node: $(hostname)"
  echo "repo: ${repo}"
  echo "repo_head: $(git -C "$repo" rev-parse HEAD)"
  echo "repo_remote: $(git -C "$repo" remote get-url github 2>/dev/null || echo unknown)"
  echo "codex_bin: $(command -v codex || echo missing)"
  echo "claude_bin: $(command -v claude || echo missing)"
} > "$stage/ENVIRONMENT.txt"
scrontab -l > "$stage/scrontab.txt" 2>&1 || true
cp "$repo/docs/orchestration/PORTING.md" "$stage/PORTING.md" 2>/dev/null || true

# 4. File inventory then the sealed tarball plus its hash.
( cd "$stage" && find . -type f | sort > FILELIST.txt )
tar -C "$work" -czf "$out" "$(basename "$stage")"
sha256sum "$out" > "${out}.sha256"

echo "bundle: $out ($(du -h "$out" | cut -f1))"
echo "sha256: $(cut -d' ' -f1 "${out}.sha256")"
echo "REMINDER: contains credentials; keep out of git, scp off-site if desired."
