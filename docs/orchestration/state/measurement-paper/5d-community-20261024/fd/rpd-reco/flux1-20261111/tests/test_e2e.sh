#!/bin/bash
# Local end-to-end run (revision 2) on macOS: the connect, the job (run by the sbatch shim as a local background
# process), then the fetch. Test copies substitute the literal root, the job's /dev/shm directory, MAT_PYTHON, the
# clone URL (a local repository holding the commit), /usr/bin/strace and /bin/true. #848's real wrapper runs in the
# job and refuses at check-mat-setup (no MAT here). Then three refusals: an rpd job queued (rc 3), a TimeLimit that
# differs from 03:00:00 (scancel, rc 6), and a second connect on an existing root (rc 9).
SP=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/7e3f49f7-e8e4-452d-b380-399d4f6c529e/scratchpad
D=$SP/wtrc/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/flux1-20261111
SHIM=$D/tests/shim
PY=$SP/venvlint/bin/python
S=${E2E_S:-2d05eb7fdf7fddaae8d482130e67ad039d517c6c}
T=$SP/flux1/te; mkdir -p "$T/gen" || exit 9
cp "$D/production-config.ready.json" "$T/gen/"; cp -R "$D/tools" "$T/gen/tools"; cp "$D"/tools/*.template.sh "$D/tools/gen_flux1.py" "$T/gen/"
python3 -I "$T/gen/gen_flux1.py" "$T/gen" "$S" "$SP/wtrc" > "$T/gen/gen.out" || { echo "gen failed"; exit 9; }
mk() {  # a test copy of the connect for root $1
  sed -e "s#/pscratch/sd/j/josephrb/rpd-reco-flux-20261111#$1/root#g" -e "s#/dev/shm/limres-rpd-flux1#$1/shm/flux1#g" \
      -e "s#/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3#$PY#g" \
      -e "s#https://github.com/josephbaileyy/MINERvA-OmniFold.git#file://$SP/wtrc#" -e "s#/usr/bin/strace#$SHIM/fakestrace#g" \
      -e "s# /bin/true# /usr/bin/true#" "$T/gen/rpd_flux1_connect.sh" > "$1/connect.sh"
}
W=$T/main; mkdir -p "$W/shm"; mk "$W"; cp "$W/connect.sh" "$W/self.sh"
PATH=$SHIM:$PATH bash "$W/connect.sh" "$W/self.sh" > "$W/connect-out.txt" 2>&1; echo "e2e connect rc=$?"
for i in $(seq 1 120); do [ -f "$W/root/job.rc" ] && break; sleep 1; done
echo "job.rc: $(cat "$W/root/job.rc" 2>&1)"; echo "job /dev/shm entries left: [$(ls -A "$W/shm")]"
sed -e "s#/pscratch/sd/j/josephrb/rpd-reco-flux-20261111#$W/root#g" -e "s#/dev/shm/limres-rpd-flux1-fetch#$W/shm/fetch#g" \
    -e "s#/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3#$PY#g" "$T/gen/rpd_flux1_fetch.sh" > "$W/fetch.sh"
cp "$W/fetch.sh" "$W/fself.sh"; FAKE_STATE=COMPLETED PATH=$SHIM:$PATH bash "$W/fetch.sh" "$W/fself.sh" > "$W/fetch-out.txt" 2>&1; echo "e2e fetch rc=$?"
echo "== refusal: an rpd job queued"
W2=$T/rpd; mkdir -p "$W2/shm"; mk "$W2"; cp "$W2/connect.sh" "$W2/self.sh"
FAKE_RPD=1 PATH=$SHIM:$PATH bash "$W2/connect.sh" "$W2/self.sh" > "$W2/out.txt" 2>&1; echo "rpd-queued connect rc=$?"; tail -2 "$W2/out.txt"
echo "== refusal: TimeLimit differs"
W3=$T/tl; mkdir -p "$W3/shm"; mk "$W3"; cp "$W3/connect.sh" "$W3/self.sh"
( cd "$W3" && FAKE_TIMELIMIT=01:00:00 PATH=$SHIM:$PATH bash "$W3/connect.sh" "$W3/self.sh" > "$W3/out.txt" 2>&1; echo "timelimit connect rc=$?" )
grep -E 'MISMATCH|scancel|STOP' "$W3/out.txt"; echo "scancel shim log: $(cat "$W3/.scancel" 2>&1)"
for i in $(seq 1 120); do [ -f "$W3/root/job.rc" ] && break; sleep 1; done
echo "== refusal: second connect on the same root"
cp "$W/connect.sh" "$W/self2.sh"; PATH=$SHIM:$PATH bash "$W/connect.sh" "$W/self2.sh" > "$W/connect2-out.txt" 2>&1; echo "second connect rc=$?"; tail -2 "$W/connect2-out.txt"
