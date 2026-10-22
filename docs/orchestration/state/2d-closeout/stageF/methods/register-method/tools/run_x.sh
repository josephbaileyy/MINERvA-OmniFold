#!/usr/bin/env bash
# usage: run_x.sh gemini|sol|sol2 <prompt-file> <out-file> [input files appended to the prompt...]
# Read-only critique runs. gemini: agy (gemini-3.8-flash-high). sol: codex-school (gpt-6.1-sol), read-only sandbox.
set -u
who=$1; pf=$2; out=$(cd "$(dirname "$3")" && pwd)/$(basename "$3"); shift 3
X=${XMODEL_DIR:-$(cd "$(dirname "$0")" && pwd)}   # scratch dir for temporary prompt files; set XMODEL_DIR to override
full=$(mktemp "$X/.prompt.XXXXXX")
cat "$pf" > "$full"
for f in "$@"; do printf '\n\n===== BEGIN FILE %s =====\n' "$(basename "$f")" >> "$full"; cat "$f" >> "$full"; printf '\n===== END FILE %s =====\n' "$(basename "$f")" >> "$full"; done
wd=$(mktemp -d "$X/.wd.XXXXXX")
case $who in
  gemini) (cd "$wd" && agy --print "$(cat "$full")" --model gemini-3.8-flash-high --sandbox --print-timeout 0 > "$out" 2> "$out.err"); rc=$? ;;
  sol) (cd "$wd" && CODEX_HOME=/Users/josephbailey/.codex-school /Users/josephbailey/.local/bin/codex exec -m gpt-6.1-sol -s read-only --skip-git-repo-check --ephemeral -C "$wd" -o "$out" - < "$full" > "$out.log" 2>&1); rc=$? ;;
  sol2) (cd "$wd" && CODEX_HOME=/Users/josephbailey/.codex-school2 /Users/josephbailey/.local/bin/codex exec -m gpt-6.1-sol -s read-only --skip-git-repo-check --ephemeral -C "$wd" -o "$out" - < "$full" > "$out.log" 2>&1); rc=$? ;;  # added 2026-10-21: codex-school out of credits; same model via codex-school2
  *) echo "unknown $who"; exit 2 ;;
esac
cp "$full" "$out.prompt"; rm -f "$full"; rm -rf "$wd"
echo "$who rc=$rc out=$out words=$(wc -w < "$out" 2>/dev/null)"
exit $rc
