#!/bin/bash
# Launch REF-C2C1 completion attempt 2 from main's bytes (the director's ruling: launch from main only). Fetches origin,
# takes the submit script and job script from origin/main's completion-attempt-2-guard/, requires the audited sha256 of
# each and the submit's embedded JOB_SHA line, then pipes main's submit bytes to the named login node, which re-hashes
# them before `setsid nohup`. Usage: launch_from_main.sh <login node> [--check-only]
NODE=${1:?login node}; MODE=$2; REF=${REF:-origin/main}   # REF overrides origin/main only for --check-only tests
W=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/7e3f49f7-e8e4-452d-b380-399d4f6c529e/scratchpad/scope-wt
G=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ref-c2c1/step2/units-replicas/completion-attempt-2-guard
SUB_SHA=c41ffb614a72864dff4d9fd0e44cb4ac54d07bf256fa3d6ab4f27321d229d503
JOB_SHA=c82055f6f8dea72a2e16fb4722d1613610576e929209b4a7c5eea0123b24589f
LEDGER=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ref-c2c1/step2/units-replicas/completion-attempt-1/rename-ledger/ledger.log
git -C "$W" fetch -q origin || { echo "REFUSED: fetch"; exit 3; }
echo "origin/main $(git -C "$W" rev-parse origin/main)"
F=$(mktemp /private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/7e3f49f7-e8e4-452d-b380-399d4f6c529e/scratchpad/refc2c1y/main-submit.XXXXXX)
git -C "$W" show "$REF:$G/refc2c1_completion_submit.sh" > "$F" 2>/dev/null || { echo "REFUSED: the submit script is not on main"; exit 4; }
s=$(shasum -a 256 "$F" | cut -d' ' -f1)
j=$(git -C "$W" show "$REF:$G/refc2c1_completion_job.sbatch" 2>/dev/null | shasum -a 256 | cut -d' ' -f1)
e=$(sed -n 's/^JOB_SHA=\([0-9a-f]*\)$/\1/p' "$F")
l=$(git -C "$W" show "origin/main:$LEDGER" 2>/dev/null | grep -c '^ref-c2c1 attempt-1 rename rc=0$')
echo "main: submit $s (audited $SUB_SHA); job $j (audited $JOB_SHA); submit's JOB_SHA $e; rename ledger rc=0 on main: $l"
[ "$s" = "$SUB_SHA" ] && [ "$j" = "$JOB_SHA" ] && [ "$e" = "$JOB_SHA" ] && [ "$l" = 1 ] || { echo "REFUSED: main does not hold the audited bytes and the rename ledger"; exit 4; }
[ "$MODE" = --check-only ] && { echo "check-only: would launch on $NODE"; exit 0; }
[ "$REF" = origin/main ] || { echo "REFUSED: a launch reads origin/main only"; exit 4; }
ssh -o ControlPath=none -o ConnectTimeout=20 -o LogLevel=ERROR saul.nersc.gov "ssh -o BatchMode=yes -o LogLevel=ERROR $NODE 'T=\$(mktemp /dev/shm/refc2c1-compl2.XXXXXX) && cat > \"\$T\" && s=\$(sha256sum \"\$T\" | cut -d\" \" -f1) && echo \"remote \$(hostname) file \$T sha256 \$s\" && if [ \"\$s\" = $SUB_SHA ]; then setsid nohup bash \"\$T\" \"\$T\" > /dev/null 2>&1 < /dev/null & echo \"launched pid \$!\"; else echo \"SHA MISMATCH: \$s is not $SUB_SHA; not launched; file left at \$T\"; exit 5; fi'" < "$F"
rc=$?; echo "ssh rc=$rc $(date -u +%T)"
[ "$rc" -eq 0 ] || { echo "REFUSED or failed on the login side (rc $rc): not launched"; exit "$rc"; }
