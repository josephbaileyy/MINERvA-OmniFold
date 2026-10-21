#!/usr/bin/env python3
"""MP1-A partial S2, DESCRIPTIVE: "not the MP-1 result; species restricted after the G3 outcome; post hoc"
(director ruling on the G3 outcome, 2026-10-20, item 3).

    design   one design copy with ONLY the two bands that passed G3 (proton i_s=1, meson i_s=2), built exactly as
             mp1_s2.py designs builds the primary copy (same endpoints, same R5 indices, same z key); the key diff
             against the frozen design must hold only those additions
    compare  every test beside A7: T_obs, p, k, B, threshold, decision, and the kappa = 3 robust decision
Run with mp1_s2.py (frozen, ff2f79ec) importable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import mp1_s2 as m

MEMBERS = ("proton", "meson")
LABEL = "not the MP-1 result; species restricted after the G3 outcome; post hoc"


def cmd_design(a) -> int:
    frozen_bytes = a.frozen.read_bytes()
    frozen = json.loads(frozen_bytes)
    copy = json.loads(frozen_bytes)
    for s in MEMBERS:
        if m.band(s) in copy["lateral_endpoints"]:
            raise SystemExit(f"{m.band(s)} already in the frozen design")
        copy["lateral_endpoints"][m.band(s)] = [m.unf(a.ns, f"{s}_m1"), m.unf(a.ns, f"{s}_p1")]
    copy["species_bands"] = {m.band(s): m.SPECIES[s] for s in MEMBERS}
    copy["species_z_key"] = m.Z_KEY
    fa, fb = m.flatten(frozen), m.flatten(copy)
    diff = sorted(k for k in set(fa) | set(fb) if fa.get(k, "<absent>") != fb.get(k, "<absent>"))
    allowed = all(k.startswith("/lateral_endpoints/SpeciesResponse_") or k.startswith("/species_bands/")
                  or k == "/species_z_key" for k in diff)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(copy, indent=1) + "\n")
    rep = {"label": LABEL, "frozen_design": str(a.frozen), "frozen_sha256": hashlib.sha256(frozen_bytes).hexdigest(),
           "file": str(a.out), "sha256": m.sha256(a.out), "differing_leaves": diff, "only_species_additions": allowed,
           "endpoint_sha256": {f"{s}_{v}": m.sha256(m.unf(a.ns, f"{s}_{v}")) for s in MEMBERS for v in ("m1", "p1")}}
    Path(str(a.out) + ".keydiff.json").write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps(rep, indent=1))
    return 0 if allowed else 1


def leaf_agreement(x, y) -> dict:
    """Non-float leaves must be equal; float leaves are compared by relative difference."""
    fx, fy = m.flatten(x), m.flatten(y)
    out = {"leaves": len(fx), "key_sets_equal": set(fx) == set(fy), "nonfloat_unequal": [], "float_unequal": 0,
           "max_rel_diff": 0.0, "worst": None}
    for k in sorted(set(fx) & set(fy)):
        u, v = fx[k], fy[k]
        if isinstance(u, float) and isinstance(v, float):
            if u != v:
                out["float_unequal"] += 1
                r = abs(u - v) / max(abs(u), abs(v))
                if r > out["max_rel_diff"]:
                    out["max_rel_diff"], out["worst"] = r, k
        elif u != v:
            out["nonfloat_unequal"].append(k)
    return out


def cmd_compare(a) -> int:
    fz = json.loads(a.frozen_evaluate.read_text())
    ctl = json.loads(a.control.read_text())
    ev = json.loads(a.partial.read_text())
    res = {"label": LABEL, "frozen_evaluate_sha256": m.sha256(a.frozen_evaluate), "control_sha256": m.sha256(a.control),
           "partial_sha256": m.sha256(a.partial), "control_equals_frozen": {}, "tests": {}, "decision_changes": [],
           "robust_decision_changes": []}
    for key in ("decisions", "decisions_robust_kappa", "holm_point", "tests"):
        res["control_equals_frozen"][key] = ctl[key] == fz[key]
    res["control_tests_float_agreement"] = leaf_agreement(fz["tests"], ctl["tests"])
    for k, fd in fz["decisions"].items():
        name, kind = k.split(":")
        row = {}
        for lab, e in (("A7", fz), ("partial", ev)):
            d, r = e["decisions"][k], e["decisions_robust_kappa"][k]
            row[lab] = {"T_obs": e["tests"][name][f"T_{kind}_obs"], "p": d.get("p"), "k": d.get("k"), "B": d.get("B"),
                        "threshold": d.get("threshold"), "decision": d["decision"], "robust_decision": r["decision"]}
        if row["partial"]["decision"] != row["A7"]["decision"]:
            res["decision_changes"].append(k)
        if row["partial"]["robust_decision"] != row["A7"]["robust_decision"]:
            res["robust_decision_changes"].append(k)
        res["tests"][k] = row
    Path(a.out).write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({x: res[x] for x in ("control_equals_frozen", "control_tests_float_agreement", "decision_changes",
                                          "robust_decision_changes")}, indent=1))
    for k, r in res["tests"].items():
        print(f"{k:28s} A7 {r['A7']['decision']:>13s}/{r['A7']['robust_decision']:<13s} p={r['A7']['p']:.3g} T={r['A7']['T_obs']}"
              f" | partial {r['partial']['decision']:>13s}/{r['partial']['robust_decision']:<13s} p={r['partial']['p']:.3g}"
              f" k={r['partial']['k']} B={r['partial']['B']} T={r['partial']['T_obs']}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("design")
    d.add_argument("--ns", required=True)
    d.add_argument("--frozen", type=Path, required=True)
    d.add_argument("--out", type=Path, required=True)
    c = sub.add_parser("compare")
    c.add_argument("--frozen-evaluate", type=Path, required=True)
    c.add_argument("--control", type=Path, required=True, help="evaluate of the UNMODIFIED frozen design, this run")
    c.add_argument("--partial", type=Path, required=True)
    c.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    return {"design": cmd_design, "compare": cmd_compare}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
