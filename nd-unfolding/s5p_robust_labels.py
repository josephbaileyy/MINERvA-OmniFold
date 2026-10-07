#!/usr/bin/env python3
"""s5p: the reported sub-fine-residual robustness labels under the owner's A7 and A7-VS rulings (report only).

Rulings (docs/orchestration/RULING-20260929-s5p-A7-robustness-flag.md; A7-VS is an explicit report-only clarification
made on 2026-09-29 after production outputs became visible, not a recovered pre-production definition):
* the kappa = 3 robustness family of a test keeps its process-shift variants (c S, c in the design's coefficients) and
  REPLACES the M1 claim variants F +- kappa delta_M1 by F +- kappa_robust delta_M1 ("replace"); its robust claim p is
  the largest p over that family; the full Holm procedure with determinacy (``s5p_inference.holm_determined``) is run
  on the ten robust claim p-values;
* a hypothesis REJECTED by the primary (kappa = 2) procedure (``decisions``) is labelled "robust to the sub-fine
  residual" iff it is also rejected in that kappa = 3 re-run, else "not robust"; every other hypothesis "not
  applicable".

The kappa = 3 p-values are taken from the frozen evaluator's stored per-variant leaves (``tests.<null>.variants`` and
``robustness_variants``, each with p, k, B); no statistic is recomputed and ``s5p_joint.py`` is unchanged. Before
using the leaves the primary claims and the frozen keep-both robust claims are rebuilt from them and must reproduce
the evaluator's ``decisions`` and ``decisions_robust_kappa`` exactly (otherwise refused).

Diagnostics kept under separate names, never reported as the label: the frozen boolean
``robust_to_the_sub_fine_residual`` (equal decision labels in the frozen runs, all ten tests) verbatim, and the
keep-both calculation (claim variants union F +- kappa_robust delta_M1: the frozen ``decisions_robust_kappa``) with the
labels it would give.

Reads the evaluator output; writes a SEPARATE file. MEASURES: nothing. CANNOT AUTHORIZE: a claim, a decision or a
change of the frozen rules.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import s5p_inference as si

ROBUST, NOT_ROBUST, NA = "robust to the sub-fine residual", "not robust", "not applicable"
RULING = "docs/orchestration/RULING-20260929-s5p-A7-robustness-flag.md"
FAMILY = "replace: the process-shift variants c S and F +- kappa_robust delta_M1 (the F +- kappa delta_M1 members removed)"
SIDES = ("total", "shape")


def labels(decisions: dict, decisions_k3: dict) -> dict:
    if set(decisions) != set(decisions_k3):
        raise SystemExit("the primary and the kappa = 3 Holm runs cover different tests")
    return {t: (NA if d["decision"] != "rejected" else (ROBUST if decisions_k3[t]["decision"] == "rejected" else NOT_ROBUST))
            for t, d in decisions.items()}


def _largest(leaves: list, side: str) -> dict:
    """The largest p over ``leaves`` for one side, first maximum in order (as ``s5p_joint.test_null`` takes it)."""
    best = max((v[side] for v in leaves), key=lambda x: x["p"])
    return {"p": best["p"], "k": int(best["k"]), "B": int(best["B"])}


def families(res: dict) -> dict:
    """Per test: the primary claim, the frozen keep-both robust claim and the replace robust claim, from the leaves."""
    out = {}
    for null, e in res["tests"].items():
        if "not_calibrated" in e:  # a null stopped at B = 0: p = 1 with k = B = 0 in every family (s5p_joint.main)
            for s in SIDES:
                one = {"p": 1.0, "k": 0, "B": 0}
                out[f"{null}:{s}"] = {"primary": one, "keep_both": one, "replace": one, "members": []}
            continue
        m1 = e.get("m1_shift")
        claim_m1 = {f"m1+{m1['kappa']}", f"m1-{m1['kappa']}"} if m1 else set()
        robust_m1 = {f"m1+{m1['kappa_robust']}", f"m1-{m1['kappa_robust']}"} if m1 else set()
        if not claim_m1 <= set(e["variants"]) or set(e.get("robustness_variants", {})) != robust_m1:
            raise SystemExit(f"{null}: the stored variants do not match its declared m1_shift")
        shift = [v for n, v in e["variants"].items() if n not in claim_m1]
        k3 = [e["robustness_variants"][n] for n in e.get("robustness_variants", {})]
        members = [n for n in e["variants"] if n not in claim_m1] + list(e.get("robustness_variants", {}))
        for s in SIDES:
            primary = _largest(list(e["variants"].values()), s)
            out[f"{null}:{s}"] = {"primary": primary, "keep_both": _largest([{s: primary}] + k3, s),
                                  "replace": _largest(shift + k3, s), "members": members}
    return out


def _same(a: dict, b: dict) -> bool:
    return (a["decision"], int(a["k"]), int(a["B"])) == (b["decision"], int(b["k"]), int(b["B"]))


def derive(res: dict, alpha: float) -> dict:
    fam = families(res)
    if set(fam) != set(res["decisions"]):
        raise SystemExit("the leaves and the evaluator's decisions cover different tests")
    prim = si.holm_determined({t: f["primary"] for t, f in fam.items()}, alpha)
    keep = si.holm_determined({t: f["keep_both"] for t, f in fam.items()}, alpha)
    for t in fam:  # the leaves must reproduce the frozen evaluator's own runs before they are used
        if not _same(prim[t], res["decisions"][t]):
            raise SystemExit(f"{t}: the primary claim rebuilt from the leaves differs from the evaluator's decisions")
        if not _same(keep[t], res["decisions_robust_kappa"][t]):
            raise SystemExit(f"{t}: the keep-both claim rebuilt from the leaves differs from decisions_robust_kappa")
    rep = si.holm_determined({t: f["replace"] for t, f in fam.items()}, alpha)
    return {"kappa3_family": FAMILY, "labels": labels(res["decisions"], rep),
            "decisions_kappa3_replace": rep,
            "family_members": {t: f["members"] for t, f in fam.items()},
            "diagnostics": {
                "frozen_boolean_robust_to_the_sub_fine_residual": res.get("robust_to_the_sub_fine_residual"),
                "keep_both": {"family": "claim variants union F +- kappa_robust delta_M1 (the frozen decisions_robust_kappa)",
                              "labels": labels(res["decisions"], res["decisions_robust_kappa"])}}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--evaluate", type=Path, required=True, help="the s5p_joint.py evaluate output (read only)")
    ap.add_argument("--design", type=Path, required=True, help="the frozen design it was evaluated with")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    raw, draw = a.evaluate.read_bytes(), a.design.read_bytes()
    res, design = json.loads(raw), json.loads(draw)
    if res.get("design_sha256") != hashlib.sha256(draw).hexdigest():
        raise SystemExit("the evaluator output was not produced with this design")
    out = {"schema": "s5p-robust-labels/2", "ruling": RULING,
           "evaluate": str(a.evaluate), "evaluate_sha256": hashlib.sha256(raw).hexdigest(),
           "design_sha256": res["design_sha256"], "alpha_family": design["alpha_family"],
           "code_sha256": hashlib.sha256(Path(__file__).resolve().read_bytes()).hexdigest(),
           **derive(res, float(design["alpha_family"]))}
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out["labels"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
