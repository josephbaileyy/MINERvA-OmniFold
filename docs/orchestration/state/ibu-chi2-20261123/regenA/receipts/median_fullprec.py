# Full-precision median_bin_ratio, the same definition as agreement_windows_receipt.py:141-148, from the same inputs.
# Control: round(median, 4) must equal the receipt's stored value for OLD (1.0054) and E (1.0075).
import sys, json, numpy as np
sys.path.insert(0, "/Users/josephbailey/local-research/wt-ibu-chi2/2d-unfolding")
import ROOT, compare_to_paper_fullcov as cpf
PUB = "/Users/josephbailey/cov2d-work/figfetch/er-anc/cov_ptpl_minerva_inclusive_6GeV.root"
ST = "/Users/josephbailey/local-research/wt-ibu-chi2/docs/orchestration/state/ibu-chi2-20261123"
fp = ROOT.TFile.Open(PUB); pv_all = cpf.flatten_th2d(fp.Get("pt_pl_cross_section")); stat = cpf.tmatrix_to_numpy(fp.Get("StatOnlyCovariance"))
mask = np.diag(stat) > 0
for name, path, rcpt in (("old", "/Users/josephbailey/cov2d-work/figfetch/er-anc/xsec.root", ST + "/regenA/out/old/RECEIPT-agreement-windows.json"),
                         ("e", ST + "/tier1/units/e/er.root", ST + "/regenA/out/e/RECEIPT-agreement-windows.json")):
    f = ROOT.TFile.Open(path); ov_all = cpf.flatten_ours(f.Get("hXSec2D")); f.Close()
    pv, ov = pv_all[mask], ov_all[mask]; use = pv > 0; r = ov[use] / pv[use]; med = float(np.median(r))
    stored = json.load(open(rcpt))["results"]["median_bin_ratio"]
    within5 = int((np.abs(r - 1) <= 0.05).sum())
    print(f"{name}: median={med!r}  round4={round(med, 4)}  stored={stored}  control={'PASS' if round(med, 4) == stored else 'FAIL'}  "
          f"3dp={med:.3f}  within5={within5}/{int(use.sum())}={100*within5/use.sum():.4f}%")
