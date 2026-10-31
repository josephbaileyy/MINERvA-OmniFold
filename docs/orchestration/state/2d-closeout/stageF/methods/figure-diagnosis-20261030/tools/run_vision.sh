#!/usr/bin/env bash
# usage: XMODEL_DIR=<scratch> run_vision.sh sol2|gemini <prompt-file> <out-file> <text-file|-> <image>...
# One read-only vision rating (PLAN.md section 3). The images are copied into a fresh scratch directory under neutral
# names (img1.png, img2.png, ...), so a file name never tells the rater whose item it is; <text-file> (the caption
# texts) is appended to the prompt. sol2: gpt-6.1-sol (read-only, ephemeral), images by -i, as
# register-method/tools/run_x.sh runs sol2, on codex-school2 by default; SOL_CODEX_HOME selects the other allowed
# account (2026-10-30: codex-school2 reported its usage limit until 2026-11-04, so the runs use ~/.codex-school, the
# same model, as r22 did the other way round on 2026-10-21). The account used is written to <out>.account. gemini: agy (gemini-3.8-flash-high, sandboxed), which has no image flag;
# the prompt names the files in its working directory, and the vision probe (PROBE.prompt.txt) decides whether it can
# see them at all.
set -u
who=$1; pf=$2; out=$(cd "$(dirname "$3")" && pwd)/$(basename "$3"); tf=$4; shift 4
X=${XMODEL_DIR:?set XMODEL_DIR to a scratch directory}
wd=$(mktemp -d "$X/.vwd.XXXXXX"); full=$(mktemp "$X/.vprompt.XXXXXX")
cat "$pf" > "$full"
n=0; names=()
for img in "$@"; do n=$((n + 1)); cp "$img" "$wd/img$n.png"; names+=("img$n.png"); done
if [ "$tf" != - ]; then printf '\n\n===== CAPTION TEXT =====\n' >> "$full"; cat "$tf" >> "$full"; fi
case $who in
  sol2)
    args=(); for nm in "${names[@]}"; do args+=(-i "$wd/$nm"); done
    ch=${SOL_CODEX_HOME:-/Users/josephbailey/.codex-school2}
    case $ch in /Users/josephbailey/.codex-school|/Users/josephbailey/.codex-school2) ;; *) echo "account not allowed: $ch"; exit 2 ;; esac
    echo "$ch" > "$out.account"
    (cd "$wd" && CODEX_HOME=$ch /Users/josephbailey/.local/bin/codex exec -m gpt-6.1-sol \
      -s read-only --skip-git-repo-check --ephemeral -C "$wd" -o "$out" "${args[@]}" - < "$full" > "$out.log" 2>&1); rc=$? ;;
  gemini)
    printf '\n\nThe image files are in your current working directory: %s. Open and view each of them with your file-viewing tool before you answer. Do not run any shell command, and do not modify any file.\n' "${names[*]}" >> "$full"
    (cd "$wd" && agy --print "$(cat "$full")" --model gemini-3.8-flash-high --sandbox --print-timeout 0 > "$out" 2> "$out.err"); rc=$? ;;
  *) echo "unknown $who"; exit 2 ;;
esac
cp "$full" "$out.prompt"; rm -f "$full"; rm -rf "$wd"
echo "$who rc=$rc out=$out"
exit $rc
