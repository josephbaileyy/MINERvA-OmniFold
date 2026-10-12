#!/usr/bin/env python3
"""P5 no-op and plumbing controls at the loader level (login node, one per-playlist file).

  python test_noop.py <repo_2d-unfolding_dir> <per-playlist omnifile> <override.npz> <report.json>

<repo_2d-unfolding_dir> holds the production driver unfold_2d_omnifold_unbinned.py (sha256 6be77c51...) and the
diagnostic copy driver_p5.py side by side, so both import the same helpers.

  C1 no-op: driver_p5.collect_signal_arrays_2d(miss_weight_override=None) == production loader, bitwise.
  C2 identity plumbing: an override equal to the stored proxy weight on every miss row == production, bitwise.
  C3 effect: the real override changes w_truth/w_reco only on miss rows, to exactly override x pot_scale;
     every kinematic and pass array stays bitwise equal.
All three run in universe mode (--universe MaRES:0 semantics, use_weights=True).
"""
import importlib.util
import json
import sys

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
d2, omni, ovpath, outp = sys.argv[1:5]
sys.path.insert(0, d2)
sys.path.insert(0, f"{d2}/uq")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


prod = load("prod_driver", f"{d2}/unfold_2d_omnifold_unbinned.py")
diag = load("p5_driver", f"{d2}/driver_p5.py")
from reported_cells import PT_EDGES, PZ_EDGES  # noqa: E402

lim = (float(PT_EDGES[0]), float(PT_EDGES[-1]), float(PZ_EDGES[0]), float(PZ_EDGES[-1]))
UNI = ("MaRES", 0)
POT = 1.0


def run(mod, **kw):
    f = ROOT.TFile.Open(omni)
    t = f.Get("mc_signal_reco")
    out = mod.collect_signal_arrays_2d(t, *lim, POT, use_weights=True, universe_branch=UNI, **kw)
    f.Close()
    return out


ov = np.load(ovpath, allow_pickle=False)
w = np.asarray(ov["w_override"], float)
rep = {"omnifile": omni, "override": ovpath, "universe": str(ov["universe"]), "n_override": int(np.isfinite(w).sum())}
ref = run(prod)
c1 = run(diag)
rep["C1_noop_bitwise"] = all(np.array_equal(ref[k], c1[k]) for k in ref) and set(ref) == set(c1)

# identity override: the proxy itself (the stored w_truth_<u>, which equals w_truth on miss rows)
f = ROOT.TFile.Open(omni)
proxy = ROOT.RDataFrame(f.Get("mc_signal_reco")).AsNumpy(["w_truth_MaRES_0"])["w_truth_MaRES_0"]
f.Close()
ident = np.where(np.isfinite(w), proxy, np.nan)
c2 = run(diag, miss_weight_override=ident)
rep["C2_identity_bitwise"] = all(np.array_equal(ref[k], c2[k]) for k in ref)

c3 = run(diag, miss_weight_override=w)
same = {k: bool(np.array_equal(ref[k], c3[k])) for k in ref}
rep["C3_unchanged_arrays"] = {k: v for k, v in same.items()}
# rows kept by the loader: the loader drops none of the miss rows that are in truth phase space; map by order
miss_kept = (~ref["pass_reco"]) & (ref["reco_pt"] == -9999.0)
changed = ref["w_truth"] != c3["w_truth"]
rep["C3_changed_rows"] = int(changed.sum())
rep["C3_changed_only_where_no_reco"] = bool(np.all(miss_kept[changed]))
rep["C3_w_reco_equals_w_truth_on_changed"] = bool(np.array_equal(c3["w_reco"][changed], c3["w_truth"][changed]))
rep["C3_sum_w_truth_ratio_changed"] = float(c3["w_truth"][changed].sum() / ref["w_truth"][changed].sum())
rep["PASS"] = bool(rep["C1_noop_bitwise"] and rep["C2_identity_bitwise"] and rep["C3_changed_only_where_no_reco"]
                   and rep["C3_w_reco_equals_w_truth_on_changed"]
                   and all(same[k] for k in ref if k not in ("w_truth", "w_reco")))
json.dump(rep, open(outp, "w"), indent=1)
print(json.dumps(rep, indent=1))
sys.exit(0 if rep["PASS"] else 2)
