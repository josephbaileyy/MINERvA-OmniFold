#!/usr/bin/env python3
"""MP1-A S1 gate G3 and the S2 design copies and decision table (PLAN §2.3; ADDENDUM-2 R3, R5).

    g3       per species s: ||f(+1) + f(-1) - 2 f(0)||_2 <= 0.2 ||f(+1) - f(-1)||_2 over the J cells of each null's
             test domain (all 109; GiBUU: p_par < 6 GeV/c), f = U x of the real-data unfolds of the +1/-1 sigma
             endpoints and of the delta = 0 control (mp1s1_<v>_b-_j-.npz). Exit 0 = every species PASS.
    designs  the primary design copy (lateral_endpoints + the four species bands proton, meson, em, other) and the
             R3 variant (+ cross-talk); every other leaf equals the frozen design (key-diff written beside them).
    table    the decision table: frozen joint-evaluate vs the band evaluation(s), with p, k, B, decision per test.
Run with the frozen evaluation deploy's nd-unfolding/ on PYTHONPATH (s5p_joint, s5p_stage1_inspect).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

SPECIES = {"proton": 1, "meson": 2, "em": 3, "other": 4, "xtalk": 5}   # R5 indices i_s
PRIMARY = ("proton", "meson", "em", "other")
Z_KEY = 0x4D31
TOL = 0.2


def band(s: str) -> str:
    return f"SpeciesResponse_{s}"


def unf(ns: str, v: str) -> str:
    return f"{ns}/unf/mp1s1_{v}_b-_j-.npz"


def sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def flatten(x, prefix="") -> dict:
    if isinstance(x, dict):
        out = {}
        for k, v in x.items():
            out.update(flatten(v, f"{prefix}/{k}"))
        return out
    if isinstance(x, list):
        out = {}
        for i, v in enumerate(x):
            out.update(flatten(v, f"{prefix}[{i}]"))
        return out
    return {prefix: x}


def u_matrix(design: dict):
    import s5p_joint as sj
    stage1 = json.loads(Path(design["stage1"]).read_text())
    supported = json.loads(Path(design["s5c_contract"]).read_text())["measurement"]["partition_J"]["supported_cells"]
    return sj.j_matrix(stage1, supported), sj.xs


def cmd_g3(a) -> int:
    design = json.loads(a.frozen.read_text())
    (U, names, pz_index), xs = u_matrix(design)
    f0 = U @ xs(unf(a.ns, "zero"))
    doms = {"all_109": np.ones(len(names), bool), "pz_lt_6 (GiBUU)": pz_index <= 1}
    res = {"tolerance": TOL, "zero_product": unf(a.ns, "zero"), "zero_sha256": sha256(unf(a.ns, "zero")), "species": {}}
    ok_all = True
    for s in SPECIES:
        pm, pp = unf(a.ns, f"{s}_m1"), unf(a.ns, f"{s}_p1")
        if not (Path(pm).is_file() and Path(pp).is_file()):
            res["species"][s] = {"not_evaluated": "endpoint unfold missing"}
            ok_all &= s not in PRIMARY
            continue
        fm, fp = U @ xs(pm), U @ xs(pp)
        out = {"minus": pm, "plus": pp, "minus_sha256": sha256(pm), "plus_sha256": sha256(pp),
               "primary": s in PRIMARY, "domains": {}}
        for dn, dom in doms.items():
            num = float(np.linalg.norm((fp + fm - 2.0 * f0)[dom]))
            den = float(np.linalg.norm((fp - fm)[dom]))
            ratio = num / den if den > 0 else float("inf")
            out["domains"][dn] = {"curvature_norm": num, "span_norm": den, "ratio": ratio, "pass": bool(ratio <= TOL),
                                  "median_abs_half_span_rel": float(np.median(np.abs((fp - fm)[dom] / 2 / f0[dom])))}
        out["G3"] = "PASS" if all(d["pass"] for d in out["domains"].values()) else "FAIL"
        if s in PRIMARY:
            ok_all &= out["G3"] == "PASS"
        res["species"][s] = out
    res["G3_primary"] = "PASS" if ok_all else "FAIL"
    text = json.dumps(res, indent=1)
    Path(a.out).write_text(text + "\n")
    print(text)
    return 0 if ok_all else 1


def cmd_designs(a) -> int:
    frozen_bytes = a.frozen.read_bytes()
    frozen = json.loads(frozen_bytes)
    a.outdir.mkdir(parents=True, exist_ok=True)
    report = {"frozen_design": str(a.frozen), "frozen_sha256": hashlib.sha256(frozen_bytes).hexdigest(), "copies": {}}
    ok = True
    for name, members in (("primary", PRIMARY), ("xtalk_variant", PRIMARY + ("xtalk",))):
        copy = json.loads(frozen_bytes)
        for s in members:
            if band(s) in copy["lateral_endpoints"]:
                raise SystemExit(f"{band(s)} already in the frozen design")
            for v in ("m1", "p1"):
                if not Path(unf(a.ns, f"{s}_{v}")).is_file():
                    raise SystemExit(f"missing unfold {unf(a.ns, f'{s}_{v}')}")
            copy["lateral_endpoints"][band(s)] = [unf(a.ns, f"{s}_m1"), unf(a.ns, f"{s}_p1")]
        copy["species_bands"] = {band(s): SPECIES[s] for s in members}
        copy["species_z_key"] = Z_KEY
        fa, fb = flatten(frozen), flatten(copy)
        diff = sorted(k for k in set(fa) | set(fb) if fa.get(k, "<absent>") != fb.get(k, "<absent>"))
        allowed = all(k.startswith("/lateral_endpoints/SpeciesResponse_") or k.startswith("/species_bands/")
                      or k == "/species_z_key" for k in diff)
        ok &= allowed
        out = a.outdir / f"design-mp1-{name}.json"
        out.write_text(json.dumps(copy, indent=1) + "\n")
        report["copies"][name] = {"file": str(out), "sha256": sha256(out), "differing_leaves": diff,
                                  "only_species_additions": allowed,
                                  "endpoint_sha256": {f"{s}_{v}": sha256(unf(a.ns, f"{s}_{v}")) for s in members for v in ("m1", "p1")}}
    report["verdict"] = "PASS" if ok else "FAIL"
    (a.outdir / "design-keydiff.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report, indent=1))
    return 0 if ok else 1


def cmd_table(a) -> int:
    frozen = json.loads(a.frozen_evaluate.read_text())
    rows, changed = {}, []
    evs = {lab: json.loads(Path(p).read_text()) for lab, p in (x.split("=", 1) for x in a.evaluate)}
    for k, fd in frozen["decisions"].items():
        r = {"frozen": {"p": fd.get("p"), "decision": fd["decision"]}}
        for lab, ev in evs.items():
            d = ev["decisions"][k]
            r[lab] = {"p": d.get("p"), "k": d.get("k"), "B": d.get("B"), "threshold": d.get("threshold"),
                      "decision": d["decision"]}
            if d["decision"] != fd["decision"]:
                changed.append(f"{lab}:{k}")
        rows[k] = r
    res = {"frozen_evaluate": str(a.frozen_evaluate), "frozen_sha256": sha256(a.frozen_evaluate),
           "evaluations": {lab: {"path": p, "sha256": sha256(p)} for lab, p in (x.split("=", 1) for x in a.evaluate)},
           "decisions": rows, "decision_changes": changed}
    Path(a.out).write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({"decision_changes": changed}, indent=1))
    for k, r in rows.items():
        print(k, " | ".join(f"{lab}: {v['decision']} p={v['p']}" for lab, v in r.items()))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("g3")
    g.add_argument("--ns", required=True)
    g.add_argument("--frozen", type=Path, required=True)
    g.add_argument("--out", required=True)
    d = sub.add_parser("designs")
    d.add_argument("--ns", required=True)
    d.add_argument("--frozen", type=Path, required=True)
    d.add_argument("--outdir", type=Path, required=True)
    t = sub.add_parser("table")
    t.add_argument("--frozen-evaluate", type=Path, required=True)
    t.add_argument("--evaluate", action="append", required=True, help="label=joint-evaluate.json")
    t.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    return {"g3": cmd_g3, "designs": cmd_designs, "table": cmd_table}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
