#!/usr/bin/env python3
"""S2R read: the declared rule (``s2r_rule.verdict``) on the six products, with T3's per-iteration quantities.

Declaration ``S2R-DECLARATION.md`` section 3. Runs once, in the job, after C-PAIR, C-X and C-ONE passed. Reuses
``tier3/t3p_read`` (C-TRACE, C-RECO, the per-k quantities) and ``prior_retention/prr_read`` (rho, the F0b grade
matrices with C-CT). The prior P is M16 times FD-PRR's nominal B0 product's truth (C-P, its staged copy at its pin).

MEASURES: rho, rms b, chi2, p, max|z| and the flag of each arm at each truth per iteration, and the verdict at k = 5.
CANNOT AUTHORIZE: adopting S2R (the director's, then Joseph's), any cause, or any statement about data.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ND = HERE.parent
REPO = ND.parent
for _p in (HERE, ND, ND / "tier3", ND / "pv-ladder", ND / "prior_retention"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import prr_read as RD  # noqa: E402
import t3p_probe as T  # noqa: E402
import t3p_arms as A  # noqa: E402
import t3p_read as RT  # noqa: E402
import s2r_arm as S  # noqa: E402
import s2r_probe as SP  # noqa: E402
import s2r_rule as RULE  # noqa: E402

SCHEMA = "s2r-readout/1"


class Stop(RuntimeError):
    def __init__(self, control: str, why: str):
        super().__init__(f"{control}: {why}")
        self.control, self.why = control, why


def load(path: Path) -> tuple[dict, dict]:
    with np.load(path, allow_pickle=False) as z:
        arrays = {k: np.asarray(z[k]) for k in z.files if k != "meta"}
        meta = json.loads(str(z["meta"]))
    return arrays, meta


def products(runs: Path) -> dict:
    out = {}
    for arm, t, s in SP.all_tasks():
        p = SP.product_path(runs, arm, t, s)
        files = sorted(p.parent.glob(f"{SP.task_id(arm, t, s)}*.npz"))
        if files != [p]:
            raise Stop("completeness", f"{p.parent}: expected exactly {p.name}, found {[f.name for f in files]}")
        arrays, meta = load(p)
        blk = meta.get("s2r") or {}
        if blk.get("arm") != arm or blk.get("truth") != t or blk.get("iters") != S.ITERS[arm]:
            raise Stop("product", f"{p.name}: its s2r block names {blk.get('arm')}/{blk.get('truth')}/{blk.get('iters')}")
        need = [f"xs_k{k}" for k in A.PAIR_KS if k <= S.ITERS[arm]]
        missing = [k for k in need if k not in arrays]
        if missing or S.GRADE_K not in [int(k[4:]) for k in need]:
            raise Stop("C-TRACE", f"{p.name}: the snapshots {missing} are missing (k = {S.GRADE_K} is graded)")
        if arrays["X16_push"].shape != (S.ITERS[arm], 16):
            raise Stop("product", f"{p.name}: X16_push has shape {arrays['X16_push'].shape}")
        if not all(np.all(np.isfinite(arrays[k])) for k in ("xsec_flat", "xtrue_flat", "X16_push")):
            raise Stop("C-FIN", f"{p.name}: a non-finite value")
        out[(arm, t)] = (arrays, meta)
    return out


def prior(stage_rec: dict, M16: np.ndarray) -> np.ndarray:
    copies = {e["role"]: (Path(e["copy"]), e["sha256"]) for e in stage_rec["files"]}
    path, pin = copies.get(f"prr_B0_nominal_s{SP.SEED}", (None, None))
    if path is None or T.sha256_path(path) != pin:
        raise Stop("C-P", "FD-PRR's nominal B0 product is not staged with its pin")
    return M16 @ T._load(path, "xtrue_flat").astype(float)


def read(runs: Path, stage_rec: dict, pair_rec: dict, repo: Path = REPO) -> dict:
    import estimator_stability_analyze as an
    import fd_f0_regrade as F
    if not pair_rec.get("pass"):
        raise Stop("C-PAIR", "the job's pair record does not pass")
    M16 = an.cell_matrix(str(repo / "nd-unfolding/pv-ladder/readouts/h2_definition.json"))
    prods = products(runs)
    Pr = prior(stage_rec, M16)
    mats, f, ct = RD.grade_matrices(repo)
    q, integrals = {}, []
    for (arm, t), (arrays, meta) in prods.items():
        it = S.ITERS[arm]
        bad = RT.trace_controls(arrays, M16, it)
        if bad:
            raise Stop("trace", f"{SP.task_id(arm, t)}: {'; '.join(bad)}")
        X = M16 @ arrays["xtrue_flat"].astype(float)
        if not np.all(X > 0) or not np.all(Pr > 0):
            raise Stop("C-FIN", f"{SP.task_id(arm, t)}: a non-positive truth or prior on R00-R15")
        q[(arm, t)] = RT.quantities(arrays, X, Pr, mats[t], it)
        q[(arm, t)]["evidence"] = meta["s2r"]["evidence"]
        integrals += [X, Pr, *arrays["X16_push"], *arrays["X16_pull"]]
    k = S.GRADE_K
    at = {key: v["per_k"][k - 1] for key, v in q.items()}
    v = RULE.verdict({t: at[("S2R", t)]["rho"] for t in RULE.TRUTHS},
                     {t: at[("B0", t)]["rho"] for t in RULE.TRUTHS},
                     bool(at[("S2R", "nominal")]["flagged"]))
    out = {"schema": SCHEMA, "verdict": v["verdict"], "rule": v, "grade_k": k,
           "controls": {"C-PAIR/C-X/C-ONE": {"pass": True}, "C-CT": {kk: vv for kk, vv in ct.items()
                                                                     if kk != "table_ii_flags"},
                        "C-P": {"pass": True}, "C-TRACE": {"pass": True}, "C-RECO": {"pass": True}},
           "at_k5": {f"{arm}/{t}": at[(arm, t)] for (arm, t) in at},
           "table": {f"{arm}/{t}": q[(arm, t)] for (arm, t) in q}}
    F.LeakGuard(f, integrals).check("readout", out)
    return out


def text(out: dict) -> str:
    r = out["rule"]
    lines = [f"S2R readout: {out['verdict']} (k = {out['grade_k']}, bar {r['bar']}, nominal flagged "
             f"{r['nominal_flagged']})"]
    for t, p in r["per_truth"].items():
        lines.append(f"{t}: rho_B0 {p['rho_B0']}, rho_S2R {p['rho_S2R']}, delta {p['delta']}, clears {p['clears']}")
    for key, a in out["at_k5"].items():
        lines.append(f"{key} k=5: rho {a['rho']}, rms b {a['rms_b']:.4g}, chi2 {a['chi2']:.4g}, p {a['p']:.3g}, "
                     f"max|z| {a['max_abs_z']:.3g}, flagged {a['flagged']}")
    for t in SP.TRUTHS:
        traj = [x["rho"] for x in out["table"][f"S2R/{t}"]["per_k"]]
        lines.append(f"S2R/{t} rho by k: " + ", ".join("None" if x is None else f"{x:.4f}" for x in traj))
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="s2r_read.py", allow_abbrev=False)
    ap.add_argument("--runs", type=Path, required=True)
    ap.add_argument("--stage", type=Path, required=True)
    ap.add_argument("--pair", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"refusing: {a.out} exists", file=sys.stderr)
        return 2
    try:
        out = read(a.runs, json.loads(a.stage.read_text()), json.loads(a.pair.read_text()))
    except Stop as e:
        print(f"STOP {e}", file=sys.stderr)
        return 5
    a.out.mkdir(parents=True)
    (a.out / "readout.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    (a.out / "readout.txt").write_text(text(out))
    print(json.dumps({"verdict": "COMPLETE"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
