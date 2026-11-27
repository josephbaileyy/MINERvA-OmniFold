#!/bin/bash
# Harness for ptmc_launch.sh's local gates and routing. ssh, scp and (for one case) shasum are stubs on PATH: no
# network is reached. One case per gate: the sha pin, the session dir, the node name per mode, the mode, a changed
# remote script, the stage's direct route to dtn01 versus the login modes' hop through saul, and fetch's failures.
set -u
L=$(cd "$(dirname "$0")" && pwd)
pass=0; fail=0
ok() { if [ "$1" = 0 ]; then pass=$((pass+1)); echo "ok   $2"; else fail=$((fail+1)); echo "FAIL $2"; fi; }
T=$(mktemp -d); cp "$L/ptmc_launch.sh" "$L/ptmc_remote.sh" "$T/"; mkdir "$T/bin"
cat > "$T/bin/ssh" <<'S'
#!/bin/bash
printf '%s\n' "$@" > "$SSH_LOG"; cat > /dev/null; echo "remote ok"; exit 0
S
cat > "$T/bin/scp" <<'S'
#!/bin/bash
[ -n "${SCP_FAIL:-}" ] && exit 1
for a in "$@"; do :; done; f=${@: -2:1}; printf 'tar' > "$a/${f##*/}"; exit 0
S
cat > "$T/bin/shasum" <<'S'
#!/bin/bash
[ -n "${SHASUM_FAIL:-}" ] && exit 1
exec /usr/bin/shasum "$@"
S
chmod +x "$T/bin/"*
export PATH="$T/bin:$PATH" SSH_LOG="$T/ssh.args"
d() { mktemp -d; }
run() { rm -f "$SSH_LOG"; out=$(bash "$T/ptmc_launch.sh" "$@" 2>&1); rc=$?; }
has() { printf '%s' "$out" | grep -q -- "$1"; }
run setup "$(d)" login04; [ "$rc" = 9 ] && has 'not filled in' && [ ! -e "$SSH_LOG" ]; ok $? "an unfilled sha: STOP 9"
sed -i.bak "s/__REMOTE_SHA256__/$(/usr/bin/shasum -a 256 "$T/ptmc_remote.sh" | cut -d' ' -f1)/" "$T/ptmc_launch.sh"
x=$(d); : > "$x/f"; run setup "$x" login04; [ "$rc" = 9 ] && has 'not a new empty directory'; ok $? "a non-empty session dir: STOP 9"
run setup "$T/nonexistent" login04; [ "$rc" = 9 ] && has 'is not a directory'; ok $? "a missing session dir: STOP 9"
run setup "$(d)" bogus; [ "$rc" = 9 ] && has 'not a login node'; ok $? "a bad node name: STOP 9"
run setup "$(d)" dtn01; [ "$rc" = 9 ] && has 'not a login node'; ok $? "a login mode on dtn01: STOP 9"
run stage "$(d)" login04; [ "$rc" = 9 ] && has 'stage runs on dtn01' && [ ! -e "$SSH_LOG" ]; ok $? "stage on a login node: STOP 9"
run stage "$(d)"; [ "$rc" = 9 ] && has 'stage runs on dtn01'; ok $? "stage with no node: STOP 9"
run nonsense "$(d)" login04; [ "$rc" = 9 ] && has "STOP: mode"; ok $? "an unknown mode: STOP 9"
run stage "$(d)" dtn01; [ "$rc" = 0 ] && grep -qx dtn01.nersc.gov "$SSH_LOG" && ! grep -q saul "$SSH_LOG" && grep -q 'ptmc-stage' "$SSH_LOG"
ok $? "stage: direct ssh to dtn01.nersc.gov, no saul hop"
run prestage "$(d)" login04; [ "$rc" = 0 ] && grep -qx saul.nersc.gov "$SSH_LOG" && grep -q 'login04' "$SSH_LOG" && grep -q 'prestage' "$SSH_LOG"
ok $? "prestage: through saul to the login node"
y=$(d); run fetch "$y"; [ "$rc" = 0 ] && [ -s "$y/post.tar.gz" ] && [ -s "$y/d4.tar.gz" ]; ok $? "fetch: both tars, hashed"
y=$(d); SCP_FAIL=1 run fetch "$y"; [ "$rc" != 0 ]; ok $? "fetch: a failed scp fails"
y=$(d); SHASUM_FAIL=1 run fetch "$y"; [ "$rc" = 9 ] && has 'hashing post.tar.gz failed'; ok $? "fetch: a failed hash fails"
echo "# changed" >> "$T/ptmc_remote.sh"; run pilot "$(d)" login04; [ "$rc" = 8 ] && has 'not the approved one' && [ ! -e "$SSH_LOG" ]
ok $? "a changed remote script: STOP 8"
SHASUM_FAIL=1 run pilot "$(d)" login04; [ "$rc" = 9 ] && has 'hashing the remote script failed'; ok $? "a failed hash of the remote script: STOP 9"
echo "pass $pass fail $fail"; [ "$fail" = 0 ]
