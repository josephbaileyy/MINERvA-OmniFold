"""Recompute the numbers quoted in section C of the Gemini Hydrogen-high read r1.

Full sample, merged-POT scaling (as README.md and HANDOFF.md). `fold` is the all-selected
prediction of ../score.py; `nom` is the nominal CV-weighted MC including backgrounds.
"""

import numpy as np
import pandas as pd

from events import load

x = load()
neg = x[x.sign == "-"].copy()
neg["w_fold"] = np.where(neg.is_data, neg.fold, neg.fold * neg.merged_scale)
neg["w_nom"] = np.where(neg.is_data, neg.tune_weight, neg.tune_weight * neg.merged_scale)


def table(frame, key, edges, label):
    frame = frame.assign(_b=pd.cut(frame[key], edges, right=False))
    d = frame[frame.is_data].groupby("_b", observed=False).w_fold.sum()
    m = frame[~frame.is_data].groupby("_b", observed=False)
    f, n = m.w_fold.sum(), m.w_nom.sum()
    tail = frame[~frame.is_data & (frame.true_pz >= 60)].groupby("_b", observed=False).w_fold.sum()
    out = pd.DataFrame({"data": d, "fold": f, "nom": n, "data/fold": d / f, "data/nom": d / n,
                        "data-fold": d - f, "frac_true_ge60_of_fold": tail.reindex(f.index).fillna(0) / f})
    print(f"\n## {label}")
    print(out.round(3).to_string())
    return out


good = neg.precision == "good"
b2040 = neg.pz.between(20, 40, inclusive="left")
table(neg[good & b2040], "evis", [20, 30, 40, 50, 60, 70, 80, np.inf],
      "C1: good negative tracks, reco pz 20-40, by E_vis = pz + E_avail (GeV)")
table(neg[b2040], "evis", [20, 30, 40, 50, 60, 70, 80, np.inf],
      "C1 (all precisions, for reference): negative tracks, reco pz 20-40, by E_vis")
table(neg, "pz", [40, 50, 55, 60], "C2a: negative tracks, reco pz 40-60 tilt")
table(neg[neg.pz.between(40, 60, inclusive="left")], "energy", [-np.inf, 5, np.inf],
      "C2b: negative tracks, reco pz 40-60, E_avail split at 5 GeV")
ge60 = neg.pz >= 60
print("\n## C3a: negative tracks, reco pz >= 60, by curvature precision")
g = neg[ge60].groupby(["precision", "is_data"]).w_fold.sum().unstack()
print(g.round(1).to_string())
table(neg[ge60 & good], "pcurv", [0, 55, 58, 60, 70, 80, 120, np.inf],
      "C3b: good negative tracks, reco pz >= 60, by curvature momentum 1/|q/p|")
table(neg[ge60], "pcurv", [0, 55, 58, 60, 70, 80, 120, np.inf],
      "C3c: all-precision negative tracks, reco pz >= 60, by curvature momentum 1/|q/p|")
print("\n## C1 check: true pz >= 60 fold fraction, good negative reco pz 20-40, all E_vis")
s = neg[good & b2040 & ~neg.is_data]
print(round(s.w_fold[s.true_pz >= 60].sum() / s.w_fold.sum(), 5))
