#!/bin/bash
# run_leads.sh <manifest> <outdir> — detached delegate jobs for lead vetting.
# manifest lines: jobid|engine|promptfile   (engine: agy | cs)
M="$1"; OUT="$2"; mkdir -p "$OUT" "$OUT/agy-ws"
while IFS='|' read -r jobid engine pfile; do
  [ -z "$jobid" ] && continue
  (
    start=$SECONDS
    echo "start=$(date -u +%FT%TZ) engine=$engine" > "$OUT/$jobid.meta"
    case "$engine" in
      agy)
        "$HOME/.local/bin/agy" --model "Gemini 3.1 Pro (High)" --print-timeout 25m0s \
          --dangerously-skip-permissions --add-dir "$OUT/agy-ws" \
          -p "$(cat "$pfile")" > "$OUT/$jobid.md" 2> "$OUT/$jobid.log"
        rc=$?
        ;;
      cs)
        env CLAUDE_CONFIG_DIR="$HOME/.claude-school" claude -p "$(cat "$pfile")" \
          --model opus --allowedTools "WebSearch,WebFetch" \
          > "$OUT/$jobid.md" 2> "$OUT/$jobid.log"
        rc=$?
        ;;
      cx)
        scratch=$(mktemp -d "$OUT/cx-XXXXXX")
        env CODEX_HOME="$HOME/.codex-personal" codex exec -c model="gpt-5.6-sol" \
          -c model_reasoning_effort="xhigh" -c tools.web_search=true \
          --sandbox read-only --skip-git-repo-check -C "$scratch" \
          --output-last-message "$OUT/$jobid.md" "$(cat "$pfile")" < /dev/null \
          > "$OUT/$jobid.log" 2>&1
        rc=$?
        ;;
      cxs)
        scratch=$(mktemp -d "$OUT/cxs-XXXXXX")
        env CODEX_HOME="$HOME/.codex-school" codex exec -c model="gpt-5.6-sol" \
          -c model_reasoning_effort="xhigh" -c tools.web_search=true \
          --sandbox read-only --skip-git-repo-check -C "$scratch" \
          --output-last-message "$OUT/$jobid.md" "$(cat "$pfile")" < /dev/null \
          > "$OUT/$jobid.log" 2>&1
        rc=$?
        ;;
      cxsw)
        scratch=$(mktemp -d "$OUT/cxsw-XXXXXX")
        env CODEX_HOME="$HOME/.codex-school" codex exec -c model="gpt-5.6-sol" \
          -c model_reasoning_effort="xhigh" -c tools.web_search=true \
          --full-auto --skip-git-repo-check -C "$scratch" \
          --output-last-message "$OUT/$jobid.md" "$(cat "$pfile")" < /dev/null \
          > "$OUT/$jobid.log" 2>&1
        rc=$?
        ;;
      *) rc=99 ;;
    esac
    echo "exit=$rc secs=$((SECONDS-start)) end=$(date -u +%FT%TZ)" > "$OUT/$jobid.done"
  ) &
done < "$M"
wait
touch "$M.ALLDONE"
