#!/bin/bash
# Launch REF-C2C1 stage 3b (the read) from main's bytes, the same way as completion attempt 2's launch_from_main.sh
# (40126474). It fetches origin, takes the read connect from origin/main's step2/read-connect/, requires the audited sha256,
# requires completion/REPLICAS-DONE-j4 to be on main, then pipes main's bytes to the named login node, which re-hashes them
# before `setsid nohup`. Each comparison refuses on mismatch and records both values. ssh's rc is read from the ssh command
# itself. Usage: launch_read_from_main.sh <login node> [--check-only]
NODE=${1:?login node}; MODE=$2
W=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/7e3f49f7-e8e4-452d-b380-399d4f6c529e/scratchpad/scope-wt
P=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ref-c2c1/step2
READ_SHA=b162ba9ac8b12887e02ab3130dae4a9185f6fbdcfa2a0db684021e5e06c63f79
DONE4_SHA=5680f1f9d0e37602e5627fbb6eefd014ce18a9b5e96806d8e3ecf352e4b918e5
git -C "$W" fetch -q origin || { echo "REFUSED: fetch"; exit 3; }
echo "origin/main $(git -C "$W" rev-parse origin/main)"
F=$(mktemp /private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/7e3f49f7-e8e4-452d-b380-399d4f6c529e/scratchpad/refc2c1y/main-read.XXXXXX)
git -C "$W" show "origin/main:$P/read-connect/refc2c1_read_login.sh" > "$F" 2>/dev/null || { echo "REFUSED: the read connect is not on main"; exit 4; }
s=$(shasum -a 256 "$F" | cut -d' ' -f1)
d=$(git -C "$W" show "origin/main:$P/units-replicas/completion/REPLICAS-DONE-j4" 2>/dev/null | shasum -a 256 | cut -d' ' -f1)
echo "main: read connect $s (audited $READ_SHA); completion/REPLICAS-DONE-j4 $d (recorded $DONE4_SHA)"
[ "$s" = "$READ_SHA" ] && [ "$d" = "$DONE4_SHA" ] || { echo "REFUSED: main does not hold the audited read connect and the completion record"; exit 4; }
[ "$MODE" = --check-only ] && { echo "check-only: would launch on $NODE"; exit 0; }
ssh -o ControlPath=none -o ConnectTimeout=20 -o LogLevel=ERROR saul.nersc.gov "ssh -o BatchMode=yes -o LogLevel=ERROR $NODE 'T=\$(mktemp /dev/shm/refc2c1-read.XXXXXX) && cat > \"\$T\" && s=\$(sha256sum \"\$T\" | cut -d\" \" -f1) && echo \"remote \$(hostname) file \$T sha256 \$s\" && if [ \"\$s\" = $READ_SHA ]; then setsid nohup bash \"\$T\" \"\$T\" > /dev/null 2>&1 < /dev/null & echo \"launched pid \$!\"; else echo \"SHA MISMATCH: \$s is not $READ_SHA; not launched; file left at \$T\"; exit 5; fi'" < "$F"
rc=$?; echo "ssh rc=$rc $(date -u +%T)"
[ "$rc" -eq 0 ] || { echo "REFUSED or failed on the login side (rc $rc): not launched"; exit "$rc"; }
