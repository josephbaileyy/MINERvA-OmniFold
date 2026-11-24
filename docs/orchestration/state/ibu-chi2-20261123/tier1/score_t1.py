# Tier 1 local scorer (DECLARATION sha 8d845062...). Reads fetched/units_{old,e}. Published side: the release TH2D
# pt_pl_cross_section values and TotalCovariance (cov_ptpl_minerva_inclusive_6GeV.root, sha 6c6dce72), compared cell by
# cell; no bin widths enter. Our hXSec2D is the driver's own extraction on its own PT_EDGES (for E, the release TH2D's
# axis: 0.075/0.325/0.475). bin_mapping.txt is not read.
import sys, json, hashlib, numpy as np
sys.path.insert(0, "/Users/josephbailey/local-research/MINERvA-OmniFold/2d-unfolding")
import ROOT, compare_to_paper_fullcov as cpf
T = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/8f21a498-e586-4293-aaeb-c5560401abaa/scratchpad/tier1/fetched"
PUBF = "/Users/josephbailey/cov2d-work/figfetch/er-anc/cov_ptpl_minerva_inclusive_6GeV.root"
ERF = "/Users/josephbailey/cov2d-work/figfetch/er-anc/xsec.root"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
fp = ROOT.TFile.Open(PUBF); pub = cpf.flatten_th2d(fp.Get("pt_pl_cross_section")); C = cpf.tmatrix_to_numpy(fp.Get("TotalCovariance"))
ax = fp.Get("pt_pl_cross_section").GetYaxis(); pub_pt_edges = [round(ax.GetBinLowEdge(i), 6) for i in range(1, ax.GetNbins() + 2)]
mask = np.diag(C) > 0; Ci = np.linalg.pinv(C[np.ix_(mask, mask)])
D = lambda x: float((x - pub)[mask] @ Ci @ (x - pub)[mask]) / 205
def vec(h): return np.array([h.GetBinContent(ix, iy) for ix in range(1, 15) for iy in range(1, 17)])
def edges(h): a = h.GetXaxis(); return [round(a.GetBinLowEdge(i), 6) for i in range(1, a.GetNbins() + 2)]
out = {"inputs": {"publication_sha256": sha(PUBF), "er_central_sha256": sha(ERF), "pub_pt_edges": pub_pt_edges}}
res, ctl = {}, {}
for d in ("old", "e"):
    f = ROOT.TFile.Open(f"{T}/units_{d}/er.root"); xs, un, dr = (vec(f.Get(k)) for k in ("hXSec2D", "hUnfold2D", "hDataReco2D"))
    pt_edges = edges(f.Get("hXSec2D")); f.Close()
    z = np.load(f"{T}/units_{d}/c2_central.npz", allow_pickle=True); ks = list(z["ks"]); X = z["xsec"]
    done = {u: json.load(open(f"{T}/units_{d}/{u}.done"))["verdict"] for u in ("er", "c2_central")}
    res[d] = {"pt_edges": pt_edges, "D_ER": D(xs), "D_IBU_K5": D(X[ks.index(5)]), "D_IBU_K10": D(X[ks.index(10)]), "verdicts": done,
              "col_data": [float(dr[np.arange(224) % 16 == j].sum()) for j in range(16)], "col_unf": [float(un[np.arange(224) % 16 == j].sum()) for j in range(16)]}
    if d == "old":
        g = ROOT.TFile.Open(ERF); ref = vec(g.Get("hXSec2D")); g.Close(); nz = ref != 0
        ctl["C-REF-OLD"] = float(np.max(np.abs(xs[nz] / ref[nz] - 1)))
ctl["C-UNITS"] = all(v == "PASS" for d in res for v in res[d]["verdicts"].values())
ctl["C-D-OLD"] = {"D_ER": res["old"]["D_ER"], "D_IBU_K10": res["old"]["D_IBU_K10"],
                  "pass": abs(res["old"]["D_ER"] - 2.270) <= 5e-4 and abs(res["old"]["D_IBU_K10"] - 1.0266) <= 5e-4}
cd = max(abs(a - b) for a, b in zip(res["old"]["col_data"], res["e"]["col_data"]))
cu = max(abs(a / b - 1) for a, b in zip(res["old"]["col_unf"], res["e"]["col_unf"]) if b)
ctl["C-COL"] = {"data_max_abs": cd, "unfold_max_rel": cu, "pass": cd == 0 and cu <= 1e-6}
ctl["E_edges_equal_release_axis"] = res["e"]["pt_edges"] == pub_pt_edges
ok = ctl["C-UNITS"] and ctl["C-REF-OLD"] <= 1e-8 and ctl["C-D-OLD"]["pass"] and ctl["C-COL"]["pass"] and ctl["E_edges_equal_release_axis"]
out.update(controls=ctl, controls_pass=ok, results={d: {k: v for k, v in r.items() if not k.startswith("col_")} for d, r in res.items()},
           reading=("STOP" if not ok else "READ"))
print(json.dumps(out, indent=1))
