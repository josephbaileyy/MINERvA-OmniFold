#!/usr/bin/env python3
"""P2 #16 interface-validation readback. Reads a smoke ROOT and checks the
active-universe metadata, branch schema, native-miss/completeness, migration
census, and point-cloud completeness. Exit 0 = all gates pass.

Usage: p2_validate.py <root> <mode> [band] [idx] [is_lateral 0/1]
  mode = cv | endpoint | fps_cv
"""
import sys
import ROOT

path = sys.argv[1]
mode = sys.argv[2]
band = sys.argv[3] if len(sys.argv) > 3 else "cv"
idx = int(sys.argv[4]) if len(sys.argv) > 4 else 0
want_lateral = int(sys.argv[5]) if len(sys.argv) > 5 else 0

f = ROOT.TFile.Open(path)
if not f or f.IsZombie():
    print(f"FAIL open {path}")
    sys.exit(1)

fails = []
def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)

def get_param(name, kind="double"):
    o = f.Get(name)
    if o is None:
        return None
    return o.GetVal() if hasattr(o, "GetVal") else o.GetTitle()

# --- trees present ---
trees = {}
for t in ("mc_truth_denom", "mc_signal_reco", "mc_background", "data"):
    tr = f.Get(t)
    trees[t] = tr
    check(tr is not None, f"tree present: {t}")

# --- metadata: active universe identity ---
has_active = get_param("hasActiveUniverse")
a_band = get_param("activeUniverseBand", "named")
a_idx = get_param("activeUniverseIndex")
a_lat = get_param("activeUniverseIsLateral")
print(f"[meta] hasActiveUniverse={has_active} band={a_band} idx={a_idx} isLateral={a_lat}")

if mode == "endpoint":
    check(has_active == 1, "hasActiveUniverse==1 for endpoint")
    check(a_band == band, f"activeUniverseBand=='{band}' (got '{a_band}')")
    check(int(a_idx) == idx, f"activeUniverseIndex=={idx}")
    check(int(a_lat) == want_lateral, f"activeUniverseIsLateral=={want_lateral}")
else:  # cv / fps_cv
    check(has_active == 0, "hasActiveUniverse==0 for CV")
    check(a_band == "cv", "activeUniverseBand=='cv' for CV")

# --- native-miss / completeness metadata ---
has_misses = get_param("hasTruthOnlyMisses")
n_misses = get_param("nTruthOnlyMisses")
check(has_misses is not None, "hasTruthOnlyMisses param present")
check(n_misses is not None, "nTruthOnlyMisses param present")
print(f"[misses] hasTruthOnlyMisses={has_misses} nTruthOnlyMisses={n_misses}")

# --- migration census counters present + finite ---
te = get_param("activeUniverseTruthEntrants")
tx = get_param("activeUniverseTruthExits")
re_ = get_param("activeUniverseRecoEntrants")
rx = get_param("activeUniverseRecoExits")
for nm, v in (("TruthEntrants", te), ("TruthExits", tx),
              ("RecoEntrants", re_), ("RecoExits", rx)):
    check(v is not None, f"migration counter present: activeUniverse{nm}")
print(f"[census] truth entrants={te} exits={tx}; reco entrants={re_} exits={rx}")
if mode == "endpoint":
    # CV comparison run; for a lateral band at least one migration direction is nonzero
    total_mig = sum(abs(x) for x in (te, tx, re_, rx) if x is not None)
    check(total_mig > 0, "lateral endpoint shows nonzero selection migration vs CV")
else:
    # CV mode: no comparison universe -> census counters must be exactly zero
    allzero = all((x == 0) for x in (te, tx, re_, rx) if x is not None)
    check(allzero, "CV mode census counters all zero (no comparison run)")

# --- truth-authoritative completeness: signal-reco truth-pass rows vs truth denom ---
n_td = trees["mc_truth_denom"].GetEntries() if trees["mc_truth_denom"] else -1
n_sig = trees["mc_signal_reco"].GetEntries() if trees["mc_signal_reco"] else -1
n_bkg = trees["mc_background"].GetEntries() if trees["mc_background"] else -1
n_dat = trees["data"].GetEntries() if trees["data"] else -1
print(f"[counts] truth_denom={n_td} signal_reco={n_sig} background={n_bkg} data={n_dat}")
check(n_td > 0 and n_sig > 0, "truth_denom and signal_reco non-empty")
# by-construction completeness: signal_reco entries == truth_denom entries (Phase 18.2)
if n_td > 0:
    c = n_sig / n_td
    print(f"[completeness] signal_reco/truth_denom = {c:.6f}")
    check(abs(c - 1.0) < 0.02, "completeness signal_reco/truth_denom within 2% of 1.0")

# --- point-cloud completeness (DUMP_POINTCLOUD=1) ---
def has_branch(tr, b):
    return tr is not None and tr.GetBranch(b) is not None

# signal reco: truth + reco clouds
for b in ("part_gen_E", "part_gen_pdg", "part_reco_E", "part_reco_pos", "part_reco_z"):
    check(has_branch(trees["mc_signal_reco"], b), f"signal_reco has point-cloud branch {b}")
# background: reco cloud (the branch this diff adds)
for b in ("part_reco_E", "part_reco_pos", "part_reco_z"):
    check(has_branch(trees["mc_background"], b), f"background has point-cloud branch {b}")
# data: reco cloud
for b in ("part_reco_E", "part_reco_pos", "part_reco_z"):
    check(has_branch(trees["data"], b), f"data has point-cloud branch {b}")

# point-cloud content: at least some rows carry non-empty reco clouds
tr = trees["mc_signal_reco"]
tr.GetEntry(0)
nonempty = 0
nscan = min(2000, n_sig)
for i in range(nscan):
    tr.GetEntry(i)
    v = getattr(tr, "part_reco_E")
    if v.size() > 0:
        nonempty += 1
frac = nonempty / max(1, nscan)
print(f"[cloud] signal_reco non-empty reco-cloud frac over {nscan} rows = {frac:.3f}")
check(frac > 0.0, "signal_reco reco point clouds are populated")

print("")
if fails:
    print(f"RESULT FAIL ({len(fails)} gate(s) failed): " + "; ".join(fails))
    sys.exit(1)
print("RESULT PASS — all interface gates satisfied")
sys.exit(0)
