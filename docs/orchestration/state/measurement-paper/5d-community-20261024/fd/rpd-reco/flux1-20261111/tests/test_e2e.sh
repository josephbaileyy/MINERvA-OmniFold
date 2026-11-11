#!/bin/bash
# Local end-to-end run of rpd_flux1_connect.sh and then rpd_flux1_fetch.sh, on macOS, with test copies whose literal roots,
# MAT_PYTHON, clone URL (a local clone of #848), strace and /bin/true are substituted, and the 30 s wait cut to 8 s.
# #848's real fd_rpd_reco_flux_connect.sh runs and refuses at check-mat-setup (no MAT here), so this tests the
# connect's checks, the detach and connect.rc, and the fetch on what the runner left. It does not test MAT.
SP=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/7e3f49f7-e8e4-452d-b380-399d4f6c529e/scratchpad
D=$SP/wtrc/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/flux1-20261111
SHIM=$D/tests/shim
PY=$SP/venvlint/bin/python
W=$SP/flux1/tc; mkdir -p "$W/shm" || exit 9
sed -e "s#/dev/shm/limres-rpd-flux1#$W/shm/flux1#g" -e "s#/pscratch/sd/j/josephrb/rpd-reco-flux-20261111#$W/root#g" \
    -e "s#/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3#$PY#g" \
    -e "s#https://github.com/josephbaileyy/MINERvA-OmniFold.git#file://$SP/wt848#" -e "s#/usr/bin/strace#$SHIM/fakestrace#g" \
    -e "s# /bin/true# /usr/bin/true#" -e "s#sleep 30#sleep 8#" "$D/rpd_flux1_connect.sh" > "$W/connect.sh"
cp "$W/connect.sh" "$W/self.sh"; PATH=$SHIM:$PATH bash "$W/connect.sh" "$W/self.sh" > "$W/connect-out.txt" 2>&1; echo "e2e connect rc=$?"
sed -e "s#/pscratch/sd/j/josephrb/rpd-reco-flux-20261111#$W/root#g" -e "s#/dev/shm/limres-rpd-flux1-fetch#$W/shm/fetch#g" \
    -e "s#/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3#$PY#g" "$D/rpd_flux1_fetch.sh" > "$W/fetch.sh"
cp "$W/fetch.sh" "$W/fself.sh"; PATH=$SHIM:$PATH bash "$W/fetch.sh" "$W/fself.sh" > "$W/fetch-out.txt" 2>&1; echo "e2e fetch rc=$?"
echo "== a second connect on the same roots (must refuse, rc 9)"
cp "$W/connect.sh" "$W/self2.sh"; PATH=$SHIM:$PATH bash "$W/connect.sh" "$W/self2.sh" > "$W/connect2-out.txt" 2>&1; echo "second connect rc=$?"
tail -2 "$W/connect2-out.txt"
echo "== a failing strace probe on fresh roots (must refuse, rc 6)"
W3=$SP/flux1/tc3; mkdir -p "$W3/shm" || exit 9
sed -e "s#$SHIM/fakestrace#$SHIM/failstrace#g" -e "s#$W/#$W3/#g" "$W/connect.sh" > "$W3/connect.sh"
cp "$W3/connect.sh" "$W3/self.sh"; PATH=$SHIM:$PATH bash "$W3/connect.sh" "$W3/self.sh" > "$W3/connect-out.txt" 2>&1; echo "strace-fail connect rc=$?"
tail -3 "$W3/connect-out.txt"; echo "runner written: $([ -e "$W3/root/runner.sh" ] && echo yes || echo no)"
