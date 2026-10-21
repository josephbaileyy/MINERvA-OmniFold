#!/usr/bin/env python3
"""MP1-A input-jitter study (DESCRIPTIVE; DECLARATION-jitter.json). The noise-floor study's mp1_nf.py with the
estimator seed replaced by the s5p_numerics jitter seed.

    table    the s5c task table: the S1 unfold line of each declared variant with --pairs=-:<J>, one table row per
             (J, variant), J major; product <out>/mp1nj_<v>_b-_j<J>.npz
    analyze  the declared readout; run from the frozen evaluation deploy with its nd-unfolding/ on PYTHONPATH
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np


def sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def load_decl(path: Path, expect: str) -> dict:
    got = sha256(path)
    if got != expect:
        raise SystemExit(f"declaration sha256 {got} != expected {expect}")
    return json.loads(path.read_text())


def cmd_table(a) -> int:
    decl = load_decl(a.declaration, a.declaration_sha256)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    lines = [f"# MP1-A input jitter (descriptive); declaration {a.declaration_sha256}; deploy 4e4b4f56bb0c4715dcf567829ac0449bfac745de"]
    for seed in decl["unfold"]["jitter_seeds"]:
        for v in decl["inputs"]["variants"]:
            npz, bkg = Path(f"{a.s1}/lateral/lat_{v}.npz"), Path(f"{a.s1}/lateral/lat_{v}_bkg.npz")
            lines.append("\t".join([f"mp1nj_unfold_{v}_j{seed}", "s5p_numerics.py", "--npz", str(npz), "--bkg", str(bkg),
                                    "--expect-npz-sha256", sha256(npz), "--expect-bkg-sha256", sha256(bkg),
                                    "--config", "R", "--iters", "5", "--construction", "data", f"--pairs=-:{seed}",
                                    "--tag", f"mp1nj_{v}", "--threads", "32",
                                    "--out", str(a.unf)]))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text("\n".join(lines) + "\n")
    print(f"{a.out}: {len(lines) - 1} tasks")
    return 0


def cmd_analyze(a) -> int:
    import mp1_s2 as m
    decl = load_decl(a.declaration, a.declaration_sha256)
    design = json.loads(a.frozen.read_text())
    (U, names, pz_index), xs = m.u_matrix(design)
    seeds = decl["unfold"]["jitter_seeds"]
    K = len(seeds)
    f, shas = {}, {}
    for v in decl["inputs"]["variants"]:
        rows = []
        for s in seeds:
            p = Path(f"{a.unf}/mp1nj_{v}_b-_j{s}.npz")
            if not p.is_file():
                raise SystemExit(f"missing {p}")
            shas[p.name] = sha256(p)
            rows.append(U @ xs(str(p)))
        f[v] = np.array(rows)
        p42 = Path(f"{a.s1}/unf/mp1s1_{v}_b-_j-.npz")
        shas[p42.name] = sha256(p42)
        f[v + "@42"] = U @ xs(str(p42))
    doms = {"all_109": np.ones(len(names), bool), "pz_lt_6 (GiBUU)": pz_index <= 1}
    res = {"status": decl["status"], "reading_rule": decl["readout"]["reading_rule"],
           "declaration_sha256": a.declaration_sha256, "K": K, "seeds": seeds,
           "products_sha256": shas, "zero_seed_scatter": {}, "species": {}}
    for dn, dom in doms.items():
        z = f["zero"][:, dom]
        res["zero_seed_scatter"][dn] = {
            "T_0": float(z.var(axis=0, ddof=1).sum()),
            "median_rel_sd": float(np.median(z.std(axis=0, ddof=1) / np.abs(z.mean(axis=0)))),
            "S1_minus_jittermean_norm": float(np.linalg.norm(f["zero@42"][dom] - z.mean(axis=0))),
            "S1_minus_jittermean_rel_median": float(np.median(np.abs(f["zero@42"][dom] - z.mean(axis=0)) / np.abs(z.mean(axis=0))))}
    for sp in decl["readout"]["per_species"]:
        out = {}
        for dn, dom in doms.items():
            fm, fp, f0 = f[f"{sp}_m1"][:, dom], f[f"{sp}_p1"][:, dom], f["zero"][:, dom]
            T = {k: float(x.var(axis=0, ddof=1).sum()) for k, x in (("minus", fm), ("plus", fp), ("zero", f0))}
            N = float(np.sqrt(T["plus"] + T["minus"] + 4 * T["zero"]))
            c42 = float(np.linalg.norm((f[f"{sp}_p1@42"] + f[f"{sp}_m1@42"] - 2 * f["zero@42"])[dom]))
            s42 = float(np.linalg.norm((f[f"{sp}_p1@42"] - f[f"{sp}_m1@42"])[dom]))
            cp = [float(np.linalg.norm(fp[k] + fm[k] - 2 * f0[k])) for k in range(K)]
            sk = [float(np.linalg.norm(fp[k] - fm[k])) for k in range(K)]
            cmean = float(np.linalg.norm(fp.mean(0) + fm.mean(0) - 2 * f0.mean(0)))
            smean = float(np.linalg.norm(fp.mean(0) - fm.mean(0)))
            out[dn] = {"T": T, "N_unpaired": N, "curv_S1": c42, "span_S1": s42, "curv_paired_k": cp, "span_k": sk,
                       "curv_jittermean": cmean, "span_jittermean": smean,
                       "ratios": {"curv_S1/N_unpaired": c42 / N,
                                  "median_k curv_paired_k/N_unpaired": float(np.median(cp)) / N,
                                  "curv_jittermean/(N_unpaired/sqrt(K))": cmean / (N / np.sqrt(K)),
                                  "curv_jittermean/span_jittermean (descriptive, NOT a gate)": cmean / smean}}
        res["species"][sp] = out
    Path(a.out).write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({sp: {dn: v["ratios"] | {"N_unpaired": v["N_unpaired"], "curv_S1": v["curv_S1"]}
                           for dn, v in o.items()} for sp, o in res["species"].items()}, indent=1))
    print(json.dumps(res["zero_seed_scatter"], indent=1))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("table", "analyze"):
        p = sub.add_parser(name)
        p.add_argument("--declaration", type=Path, required=True)
        p.add_argument("--declaration-sha256", required=True)
        p.add_argument("--s1", required=True, help="the S1 namespace (lateral/ and unf/)")
        p.add_argument("--unf", required=True, help="jitter product directory")
        if name == "table":
            p.add_argument("--out", type=Path, required=True)
        else:
            p.add_argument("--frozen", type=Path, required=True)
            p.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    return {"table": cmd_table, "analyze": cmd_analyze}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
