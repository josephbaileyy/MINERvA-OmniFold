"""Producer for \\uqPaper: the published 2D total uncertainty, as a per-bin median relative sigma over the 205
reported bins. Read-only; run on Perlmutter in the root_6_28 environment:

    python paper_median.py      (writes paper_median.json in the current directory)

Definition: median over bins with StatOnlyCovariance diagonal > 0 (205, the same set as cross section > 0) of
sqrt(diag TotalCovariance) / cross section. The full-precision inputs are the ROOT data release
(cov_ptpl_minerva_inclusive_6GeV.root: TotalCovariance and pt_pl_cross_section), flattened by the same
helpers as compare_to_paper_fullcov.py and _ours_only_chi2.py. For comparison it also evaluates the same
median with each operand taken from the CSV release, whose cross sections and total uncertainties are
rounded to three significant figures. The median bin lies close enough to its neighbours that this rounding
moves the result from 6.8525 % to 6.859 %.
"""
import csv, hashlib, json, sys
import numpy as np

D = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
A = f"{D}/minerva_paper_anc/"
sys.path.insert(0, f"{D}/uq")
import _ours_only_chi2 as oo  # noqa: E402
import ROOT  # noqa: E402
ROOT.gROOT.SetBatch(True)

files = {"root": A + "cov_ptpl_minerva_inclusive_6GeV.root",
         "csv_result": A + "data_result_ptpl_2D_minerva_inclusive_6GeV.txt",
         "csv_bin_mapping": A + "bin_mapping.txt"}
fp = ROOT.TFile.Open(files["root"])
x = oo.flatten_paper(fp.Get("pt_pl_cross_section"))
var = np.diag(oo.tmatrix_to_numpy(fp.Get("TotalCovariance")))
stat = np.diag(oo.tmatrix_to_numpy(fp.Get("StatOnlyCovariance")))
fp.Close()
rep = stat > 0
gid = {(int(r["P||bin"]), int(r["Ptbin"])): int(r["GlobalID"]) for r in csv.DictReader(open(files["csv_bin_mapping"]))}
xc, ec = np.zeros(x.size), np.zeros(x.size)
for r in csv.DictReader(open(files["csv_result"])):
    g = gid[(int(r["P||bin"]), int(r["Ptbin"]))]
    xc[g], ec[g] = float(r["cross_section"]), float(r["total_uncertainty"])
assert np.array_equal(rep, x > 0) and np.array_equal(rep, xc > 0) and rep.sum() == 205


def med(num, den):
    return float(100 * np.median(num[rep] / den[rep]))


out = {"n_reported": int(rep.sum()),
       "uqPaper_pct": med(np.sqrt(var), x),
       "variants_pct": {"csv_total_over_csv_xs": med(ec, xc), "root_sigma_over_csv_xs": med(np.sqrt(var), xc),
                        "csv_total_over_root_xs": med(ec, x)},
       "csv_vs_root_max_rel_diff": {"xs": float(np.max(np.abs(xc[rep] / x[rep] - 1))),
                                    "sigma": float(np.max(np.abs(ec[rep] / np.sqrt(var[rep]) - 1)))},
       "mean_pct": float(100 * np.mean(np.sqrt(var[rep]) / x[rep])),
       "inputs": {k: {"path": p, "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest()} for k, p in files.items()}}
json.dump(out, open("paper_median.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "inputs"}, indent=1))
