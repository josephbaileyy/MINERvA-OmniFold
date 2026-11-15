#!/bin/bash
# launch-g2r.sh run end to end in its test mode (G2R_LAUNCH_TEST=1) against stubs: ssh runs the remote command locally,
# setsid/squeue/sacct are stand-ins, and a stand-in connect writes its log in a temporary "shm" directory. Cases:
#   done     the stand-in ends with DONE inside the window: rc 0, the whole log fetched, then the script and log removed
#   timeout  the stand-in outlasts the window: rc 5, TIMEOUT printed with the log's last lines, both files left in place
#   lrcfail  the launch ssh fails: rc 4 (STOP), nothing tailed, the staged script left in place
# A real digest is never used: the stand-in's own sha256 is the "go". Exit 0 only if every case behaves.
#     bash test_launch_g2r.sh [path/to/launch-g2r.sh]
set -u
H=$(cd "$(dirname "$0")" && pwd)
L=${1:-$H/launch-g2r.sh}
T=$(mktemp -d "${TMPDIR:-/tmp}/lg2r.XXXXXX")
# the launcher runs from a copy in $T: it writes run-envtest beside itself and the cases remove it; run from its own
# directory, the old form deleted the real r1 record (2026-11-13)
mkdir -p "$T/lh"; cp "$L" "$T/lh/launch-g2r.sh"; LH=$T/lh
mkdir -p "$T/bin" "$T/shm" "$T/home"
cat > "$T/bin/ssh" <<'EOF'
#!/usr/bin/env bash
cmd=${@: -1}; inner=${cmd#*login02 }
if [ "${STUB_LAUNCH_FAIL:-}" = 1 ] && [ "$inner" = "bash -s" ]; then
    body=$(cat); case "$body" in *setsid*) exit 255 ;; esac; printf '%s\n' "$body" | bash -s; exit $?
fi
case "$inner" in
    "bash -s") exec bash -s ;;
    \'*\') inner=${inner#\'}; inner=${inner%\'}; exec bash -c "$inner" ;;
    *) exec bash -c "$inner" ;;
esac
EOF
printf '#!/usr/bin/env bash\nexec "$@"\n' > "$T/bin/setsid"
printf '#!/usr/bin/env bash\nexit 0\n' > "$T/bin/squeue"
printf '#!/usr/bin/env bash\nexit 0\n' > "$T/bin/sacct"
chmod +x "$T/bin/"*
standin() {  # standin <file> <seconds before DONE>
    cat > "$1" <<EOF
#!/bin/bash
LOG=$T/shm/josephrb-g2r-envtest.log
exec >> "\$LOG" 2>&1
echo "host=stand-in start=\$(date -u +%FT%TZ)"
sleep $2
echo "submit envtest rc=0"
echo "end=\$(date -u +%FT%TZ)"; echo DONE
EOF
}
ok=0
run() {  # run <case> <seconds before DONE> <wait polls> <expect rc> [env...]
    local name=$1 secs=$2 polls=$3 want=$4; shift 4
    rm -rf "$LH/run-envtest" "$T/shm/"*
    standin "$T/connect-$name.sh" "$secs"
    local sha; sha=$(shasum -a 256 "$T/connect-$name.sh" | cut -c1-64)
    env PATH="$T/bin:$PATH" G2R_LAUNCH_TEST=1 G2R_SHM="$T/shm" G2R_TEST_SRC="$T/connect-$name.sh" G2R_WAIT_N="$polls" \
        G2R_POLL_S=1 "$@" bash "$LH/launch-g2r.sh" envtest "$sha" > "$T/$name.out" 2>&1
    local rc=$?
    local sh_left=0 log_left=0
    [ -e "$T/shm/josephrb-g2r-envtest.sh" ] && sh_left=1
    [ -e "$T/shm/josephrb-g2r-envtest.log" ] && log_left=1
    local verdict=PASS
    [ "$rc" = "$want" ] || verdict=FAIL
    case "$name" in
        done)    grep -q '^DONE$' "$LH/run-envtest/connect.log" && grep -q '^submit envtest rc=0$' "$LH/run-envtest/connect.log" \
                     && [ "$sh_left$log_left" = 00 ] || verdict=FAIL ;;
        timeout) grep -q '^TIMEOUT:' "$T/$name.out" && [ "$sh_left$log_left" = 11 ] && ! grep -q '^removal rc=' "$T/$name.out" \
                     || verdict=FAIL ;;
        lrcfail) grep -q '^STOP: the launch ssh returned rc=255' "$T/$name.out" && [ "$sh_left" = 1 ] \
                     && ! grep -q '^last line:' "$T/$name.out" || verdict=FAIL ;;
    esac
    echo "$verdict $name rc=$rc (want $want) staged_left=$sh_left log_left=$log_left"
    [ "$verdict" = PASS ] || { ok=1; sed 's/^/    /' "$T/$name.out" | tail -12; }
    sleep $((secs > polls ? secs - polls + 2 : 1))   # let a slow stand-in finish before the next case
    rm -rf "$LH/run-envtest"
}
echo "launcher $(shasum -a 256 "$L" | cut -c1-64)"
run done 2 30 0
run timeout 8 3 5
run lrcfail 1 5 4 STUB_LAUNCH_FAIL=1
rm -rf "$T"
[ "$ok" = 0 ] && echo "LAUNCH-G2R TEST PASS" || echo "LAUNCH-G2R TEST FAILED"
exit $ok
