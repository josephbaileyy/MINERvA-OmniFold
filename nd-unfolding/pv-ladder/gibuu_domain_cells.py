#!/usr/bin/env python3
"""GiBUU's 6 <= p_parallel < 10 GeV/c slice on the 16 H2 reporting cells (H2-DEFINITION-DECLARATION addendum A2-A3;
numpy only, simulation and generator predictions only).

Per reporting cell (readouts/h2_definition.json):
  the share of the cell's prior truth weight in fine cells with 6 < upper p_parallel edge <= 10 (the slice), and how
      L-5D-PV's GiBUU gate tiers it (own ratio, J-coarse pooled, r = 1);
  GiBUU's truth-level departure d = sum(p r) / sum(p) - 1 under the frozen reweight (option i, p_parallel < 10), and
      under option ii (r = 1 at p_parallel >= 6).
Option ii's reweight is computed exactly from the frozen ratios.json: the gate pools within J-coarse cells, and J's
p_parallel edges include 6, so every rho and label below 6 is what pvl_ratios.py would give with pz_max = 6; above 6
every cell is off; pvl_lib.normalize then sets k over the remaining assigned cells.

Never opens an unfold product. MEASURES: arithmetic on the frozen reweights. CANNOT AUTHORIZE: the GiBUU domain.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import pvl_lib as L  # noqa: E402
import s2_h2_scope as S2  # noqa: E402

SLICE = (6.0, 10.0)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--definition", type=Path, default=_HERE / "readouts" / "h2_definition.json")
    ap.add_argument("--ratios", type=Path, required=True, help="the frozen prep/ratios/L-5D-PV directory")
    ap.add_argument("--prep-sums", type=Path, default=_HERE / "prep-SHA256SUMS")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"[FAIL] refusing to overwrite {a.out}")
    prep = dict(ln.split()[::-1] for ln in a.prep_sums.read_text().splitlines() if ln.strip())
    inputs = {"h2_definition.json": L.sha256_path(a.definition)}
    for f in ("ratios.json", "gibuu.json"):
        inputs[f"ratios/{S2.RUNG}/{f}"] = S2.check(a.ratios / f, prep[f"./ratios/{S2.RUNG}/{f}"], f)
    D = L.load_json(a.definition)
    cell, _ = S2.h2_of_fine()
    rmap = np.asarray(D["h2_to_reporting_cell"])[cell]
    n = int(D["n_reporting_cells"])
    ok = rmap >= 0

    def agg(v):
        return np.bincount(rmap[ok], weights=np.asarray(v, float)[ok], minlength=n)

    R = L.load_json(a.ratios / "ratios.json")
    rv = R["vertices"]["gibuu"]
    shape = tuple(len(L.FINE[x]) - 1 for x in L.AXES5)
    p = np.asarray(R["prior_truth_weight"], float)
    rho = np.asarray(rv["rho"], float)
    lab = np.asarray(rv["label"], dtype=object)
    r_i = np.asarray(L.load_json(a.ratios / rv["ratio_file"])["r"], float)
    pz_hi = np.asarray(L.FINE["pz"][1:])[np.unravel_index(np.arange(p.size), shape)[1]]
    assigned = np.isin(lab, ("fine", "coarse"))
    r_chk, k_chk = L.normalize(rho, assigned, p)
    if not np.allclose(r_chk, r_i, rtol=1e-12, atol=0) or abs(k_chk - rv["k"]) > 1e-12 * rv["k"]:
        raise SystemExit("[FAIL] normalize(rho, labels) does not reproduce the frozen GiBUU reweight")
    if np.any(assigned & (pz_hi > 10.0)):
        raise SystemExit("[FAIL] the frozen GiBUU reweight assigns a cell above 10 GeV/c")
    r_ii, k_ii = L.normalize(rho, assigned & (pz_hi <= SLICE[0]), p)
    sl = (pz_hi > SLICE[0]) & (pz_hi <= SLICE[1])
    P = agg(p)
    with np.errstate(invalid="ignore", divide="ignore"):
        out = {"schema": "gibuu-domain-cells/1", "simulation_only": True, "slice_pz": list(SLICE), "inputs": inputs,
               "code": {"gibuu_domain_cells.py": L.sha256_path(__file__), "pvl_lib.py": L.sha256_path(L.__file__)},
               "k": {"i": float(rv["k"]), "ii": k_ii},
               "prior_share_in_slice_of_all": float(p[sl].sum() / p.sum()),
               "slice_share": (agg(p * sl) / P).tolist(),
               "slice_tiers": {"own ratio": (agg(p * (sl & (lab == "fine"))) / P).tolist(),
                               "coarse cell": (agg(p * (sl & (lab == "coarse"))) / P).tolist(),
                               "r = 1": (agg(p * (sl & np.isin(lab, ("noisy", "off")))) / P).tolist()},
               "rho_weighted_mean": {"pz<6": float(np.sum((p * rho)[assigned & (pz_hi <= 6)]) / p[assigned & (pz_hi <= 6)].sum()),
                                     "6-10": float(np.sum((p * rho)[assigned & sl]) / p[assigned & sl].sum())},
               "departure": {"i": (agg(p * r_i) / P - 1.0).tolist(), "ii": (agg(p * r_ii) / P - 1.0).tolist()}}
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print(f"k: (i) {out['k']['i']:.4f}, (ii) {k_ii:.4f}; the slice holds {100 * out['prior_share_in_slice_of_all']:.1f} % "
          f"of the prior; prior-weighted rho on assigned cells: p<6 {out['rho_weighted_mean']['pz<6']:.3f}, "
          f"6-10 {out['rho_weighted_mean']['6-10']:.3f}\n")
    print("| cell | slice share | of it: own ratio / pooled / r = 1 | GiBUU d, (i) p∥ < 10 | GiBUU d, (ii) p∥ < 6 | change |")
    print("|---|---:|---|---:|---:|---:|")
    for c in D["reporting_cells"]:
        i = c["id"]
        s = out["slice_share"][i]
        t = " / ".join(f"{100 * out['slice_tiers'][k][i]:.0f}" for k in ("own ratio", "coarse cell", "r = 1"))
        di, dii = out["departure"]["i"][i], out["departure"]["ii"][i]
        print(f"| R{i:02d} | {100 * s:.0f} % | {t} % | {100 * di:+.1f} % | {100 * dii:+.1f} % | {100 * (dii - di):+.1f} pp |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
