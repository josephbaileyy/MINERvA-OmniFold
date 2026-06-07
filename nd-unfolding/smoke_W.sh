#!/bin/bash
# One-file smoke test for the W axis + truth diagnostics (Workstream F).
# Runs the rebuilt event loop on a single 1A MC+data file (CV branches) and,
# if SMOKE_UNIV is set, also a single lateral band to exercise the shifted-W
# branches (W_truth_/MC_W_/sim_W_). Then inspects the new branches for sanity.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
BIN="${REPO}/MINERvA101/opt/bin/runEventLoopOmniFold"

WORK="${REPO}/nd-unfolding/smoke_W_work"
rm -rf "${WORK}"; mkdir -p "${WORK}"; cd "${WORK}"
head -1 "${REPO}/2d-unfolding/playlist_manifests/1A_MC.txt"   > mc1.txt
head -1 "${REPO}/2d-unfolding/playlist_manifests/1A_Data.txt" > data1.txt
echo "[smoke] MC  = $(cat mc1.txt)"
echo "[smoke] DAT = $(cat data1.txt)"
echo "[smoke] bin = ${BIN} ($(stat -c '%y' ${BIN}))"

if [[ -n "${SMOKE_UNIV:-}" ]]; then
  echo "[smoke] universe dump enabled: MNV101_DUMP_UNIVERSES=${SMOKE_UNIV}"
  export MNV101_DUMP_UNIVERSES="${SMOKE_UNIV}"
fi
echo "[smoke] running event loop ..."
"${BIN}" data1.txt mc1.txt
ls -la runEventLoopOmniFold.root

echo "[smoke] inspecting new branches ..."
python3 - <<'PY'
import ROOT, numpy as np
ROOT.gROOT.SetBatch(True)
f = ROOT.TFile.Open("runEventLoopOmniFold.root")
def stats(tname, branches, nmax=300000):
    t = f.Get(tname)
    if not t:
        print(f"  [MISS] tree {tname}"); return
    n = min(int(t.GetEntries()), nmax)
    print(f"  {tname}: entries={t.GetEntries()} (scan {n})")
    for b in branches:
        if not t.GetBranch(b):
            print(f"    [MISS] branch {b}"); continue
        vals = np.empty(n)
        for i in range(n):
            t.GetEntry(i); vals[i] = getattr(t, b)
        good = vals[vals > -9990]
        if good.size:
            print(f"    {b:16s} good={good.size:7d} median={np.median(good):8.3f} "
                  f"min={good.min():8.3f} max={good.max():8.3f}")
        else:
            print(f"    {b:16s} good=0 (all sentinel)")
stats("mc_signal_reco", ["MC_W","sim_W","MC_q3","MC_nproton","MC_npip","MC_hadangle"])
stats("data",          ["measured_W","measured_q3"])
stats("mc_background", ["sim_background_W"])
# shifted-W lateral branches if the universe dump ran
import re
if __import__("os").environ.get("MNV101_DUMP_UNIVERSES"):
    t = f.Get("mc_signal_reco")
    shifted = [br.GetName() for br in t.GetListOfBranches()
               if re.match(r"(MC_W_|sim_W_)", br.GetName())]
    print(f"  shifted-W branches on mc_signal_reco: {len(shifted)}  e.g. {shifted[:4]}")
    if shifted:
        b = shifted[0]; cvb = "sim_W" if b.startswith("sim_W_") else "MC_W"
        n = min(int(t.GetEntries()), 50000); ds=0; tot=0
        for i in range(n):
            t.GetEntry(i)
            cv=getattr(t,cvb); sh=getattr(t,b)
            if cv>-9990 and sh>-9990:
                tot+=1; ds += (abs(sh-cv)>1e-9)
        print(f"  {b} vs {cvb}: shifted in {ds}/{tot} events (W is muon+recoil dependent -> expect >0)")
print("[smoke] OK")
PY
