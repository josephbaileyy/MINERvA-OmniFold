"""Print the first few entries of the flux-weight arrays whose leaf type changed (D in ours, I in the current release).
Usage: python -I peek_wgt.py <url> [tree]"""
import sys
import ROOT
f = ROOT.TFile.Open(sys.argv[1]); t = f.Get(sys.argv[2] if len(sys.argv) > 2 else "Truth")
for b in ("mc_wgt_ppfx1_Total", "mc_wgt_Flux_BeamFocus", "mc_wgt_ppfx1_Total_sz", "mc_wgt_Flux_BeamFocus_sz", "mc_cvweight_total", "mc_wgt_Flux_Tertiary"):
    br = t.GetBranch(b)
    print(b, br.GetTitle() if br else "ABSENT")
t.SetBranchStatus("*", 0)
for b in ("mc_wgt_ppfx1_Total", "mc_wgt_Flux_BeamFocus", "mc_wgt_ppfx1_Total_sz", "mc_wgt_Flux_BeamFocus_sz"):
    t.SetBranchStatus(b, 1)
for i in range(3):
    t.GetEntry(i)
    for b in ("mc_wgt_ppfx1_Total", "mc_wgt_Flux_BeamFocus"):
        lf = t.GetLeaf(b)
        print(i, b, "len", lf.GetLen(), [round(lf.GetValue(j), 6) for j in range(min(lf.GetLen(), 6))])
