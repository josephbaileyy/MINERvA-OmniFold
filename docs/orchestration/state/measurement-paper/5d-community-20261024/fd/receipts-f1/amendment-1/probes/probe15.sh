G=/cvmfs/larsoft.opensciencegrid.org/products/genie/v3_04_00/Linux64bit+3.10-2.17-e20-prof/GENIE-Generator
echo "== EventGeneratorListAssembler.cxx 40-100"; sed -n 40,100p $G/src/Framework/EventGen/EventGeneratorListAssembler.cxx
echo "== where TuneGeneratorList is read"; grep -rn "TuneGeneratorList" $G/src --include=*.cxx | head -10
F=$(grep -rln "TuneGeneratorList" $G/src --include=*.cxx | head -1); echo "F=$F"; grep -n "TuneGeneratorList" -B3 -A12 $F | head -60
echo "== the pilots' gevgen logs: generator list lines"
OUT=/pscratch/sd/j/josephrb/fd-f1-20261027
for t in G18_10a_02_11b AR23_20i_00_000; do echo "--- $t"; grep -nE "EventGenerator/|generator list|Generator list|Loading.*Tune|tune" $OUT/f1a/pilot/$t/gevgen.log | head -30; echo "neg-xsec: $(grep -c 'Negative cross section' $OUT/f1a/pilot/$t/gevgen.log)"; done
source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh >/dev/null 2>&1
python3 - <<'PY'
import ROOT, numpy as np
for t in ("G18_10a_02_11b", "AR23_20i_00_000"):
    p = f"/pscratch/sd/j/josephrb/fd-f1-20261027/f1a/pilot/{t}/genie_v3.gst.root"
    cols = ["cc","nc","qel","mec","res","dis","coh","dfr","imd","imdanh","nuel","em","charm","singlek","amnugamma","Ev"]
    d = ROOT.RDataFrame("gst", p)
    have = [c for c in cols if d.HasColumn(c)]
    a = d.AsNumpy(have)
    n = len(a["cc"]); cc = a["cc"].astype(bool)
    print("==", t, "events", n, "CC", int(cc.sum()), "NC", int(a["nc"].astype(bool).sum()), "missing columns", sorted(set(cols)-set(have)))
    for c in have:
        if c in ("cc","nc","Ev"): continue
        v = a[c].astype(bool)
        print(f"  {c:9s} all {int(v.sum()):6d}  CC {int((v&cc).sum()):6d}  NC {int((v&~cc).sum()):6d}")
    flags = [c for c in have if c not in ("cc","nc","Ev")]
    m = np.zeros(n, int)
    for c in flags: m += a[c].astype(bool)
    print("  events with no process flag", int((m==0).sum()), "with two or more", int((m>1).sum()))
PY
