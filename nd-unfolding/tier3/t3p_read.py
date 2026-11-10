#!/usr/bin/env python3
"""T3 reader: the one read of the study's products (T3-PIPELINE-TESTS-DECLARATION.md rev 2, §4, §5, §6, §7).

COMPLETENESS: each job's DONE (dry, q3, floor) with every queued task ended rc 0 and its C-PAIR / C-X record passed;
otherwise the verdict is INCOMPLETE and nothing is read.

CONTROLS: every product's metadata (arm, truth, split, iterations, construction, code digests) and its C-ARM evidence;
C-TRACE (the recorder's R00-R15 at k equals M16 times the production extraction at k); C-RECO; C-FIN; C-P (P from
FD-PRR's nominal product at each split, its staged copy carrying its pin); C-CT (FD-PRR's ``grade_matrices``).

QUANTITIES (§4) at every k: rho(k) and rho_pull(k) by ``prr_read.rho``; b_par, b_perp, RMS b; the noise-free chi2 by
``prr_read.table_ii``; the reco-level rho_R1(k), rho_R2(k) and rho_RD.

READINGS (§5): TR-1 (8 primary) and TR-2 (2 primary) at max(0.05, T_Q s), s over five splits at A7 GiBUU; the
trajectory, location and "consistent with" classes (descriptive). The readout passes F0b's LeakGuard.

MEASURES: the declared readings. CANNOT AUTHORIZE: an estimator change, a cause beyond "consistent with", a held-out
claim, or any wording.
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
for _p in (HERE, ND, ND / "pv-ladder", ND / "prior_retention"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import prr_read as RD  # noqa: E402
import t3p_arms as A  # noqa: E402
import t3p_probe as T  # noqa: E402

SCHEMA = "t3-readout/1"
Stop = RD.Stop
INCOMPLETE_RC, STOP_RC = RD.INCOMPLETE_RC, RD.STOP_RC
BAR_FLOOR = 0.05
T_Q = 8.610301581379899  # Student t, 4 dof, two-sided 0.01/10: t.ppf(1 - 0.01/20, 4); test_t3p recomputes it
DELTA = 0.05  # §5.3 and §5.4
DELTA_R = 0.05
DELTA_T_FLOOR = 0.02
PRR_READOUT = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-prr/read/cluster/readout.json"
INPUT_PINS = {PRR_READOUT: "9238f22bfe29685e33c1d5bb46da3938a3ebfdc93a54575a4fe99de3a7af9ead"}
TR1_ARMS = ("MU", "MW", "MO", "SO")
TRAJ_ARMS = ("B0", "MU", "MW", "MO", "SO")
LABELS = {"what": "T3: (e)'s retained prior per iteration under one replaced pipeline component, at the two flagged "
                  "truths; noise-free, one MC split, simulation only",
          "not": ["a cause beyond 'consistent with'", "an estimator change (MO and OP use the truth)",
                  "a held-out claim", "Table II or its grades", "any data quantity", "paper or note wording"]}


def check_inputs(repo: Path) -> dict:
    for rel, want in INPUT_PINS.items():
        if T.sha256_path(repo / rel) != want:
            raise Stop("inputs", f"{rel} is not its pin")
    ro = json.loads((repo / PRR_READOUT).read_text())
    fl = ro["readings"]["floor"]
    return {"s_F1": float(fl["s_F"]["F1"]), "T_FD": float(fl["T_Q"])}


def delta_t(prr: dict) -> float:
    return max(DELTA_T_FLOOR, prr["T_FD"] * prr["s_F1"])


# ------------------------------------------------------------------------------------------- completeness
def queue_ids(run: Path, job: str) -> list[str]:
    return [ln.split("\t")[0] for ln in (run / "queues" / f"{job}.tsv").read_text().splitlines()
            if ln and not ln.startswith("#")]


def incomplete(run: Path) -> str | None:
    for j in T.JOBS:
        log = run / f"log-{j}"
        for name in ("STOP", "FAILED"):
            if (log / name).exists():
                return f"job {j} left {name}"
        if not (log / "DONE").is_file():
            return f"job {j} has no DONE"
        d = json.loads((log / "DONE").read_text())
        n = len(queue_ids(run, j))
        want = sum(1 for t in T.all_tasks() if T.job_of(*t) == j)
        if d.get("mode") != j or d.get("rc") != 0 or d.get("tasks") != n or d.get("ended") != n or n != want:
            return f"job {j}'s DONE is not a completed run of its {want} tasks: {d}"
        pr = log / "pair.json"
        if not pr.is_file() or json.loads(pr.read_text()).get("pass") is not True:
            return f"job {j}'s C-PAIR / C-X record is missing or did not pass"
    return None


# ------------------------------------------------------------------------------------------- products
TRACE_KEYS = ("X16_push", "X16_pull", "R16_pull", "R16_push", "R16_D", "R16_true", "R16_prior", "miss_share16",
              "norm_pull", "norm_push", "clip_step1", "clip_step2", "reco_in_cells")


def load(path: Path) -> tuple[dict, dict]:
    with np.load(path, allow_pickle=False) as z:
        arrays = {k: np.asarray(z[k]) for k in z.files if k != "meta"}
        meta = json.loads(str(z["meta"]))
    return arrays, meta


def meta_problems(meta: dict, arrays: dict, arm: str, truth: str, seed: int, repo: Path) -> list[str]:
    import s5c_pseudo
    bad = []
    t3 = meta.get("tier3") or {}
    it = A.ITERS[arm]
    if (t3.get("schema"), t3.get("arm"), t3.get("truth"), t3.get("iters")) != (T.SCHEMA, arm, truth, it):
        bad.append(f"tier3 block {t3.get('arm')}/{t3.get('truth')}/{t3.get('iters')}")
    if meta.get("iters") != it or meta.get("capacity") is not None or meta.get("nuisance_draw") is not None:
        bad.append("iters, capacity or nuisance draw")
    if meta.get("development") != {"expectation": True, "mc_fraction": "half"}:
        bad.append(f"development {meta.get('development')}")
    if meta.get("pseudo_seed") != seed or meta.get("split_key") != s5c_pseudo.split_key_for(seed):
        bad.append("seed or split key (C-SPLIT)")
    want = RD.expected_truth(truth, repo)  # FD-PRR's rule, as prr_read.meta_problems applies it
    if (meta.get("hypothesis") or {}).get("sha256") != want["hyp"]:
        bad.append("C-PINS: the hypothesis is not the truth's file")
    alt = meta.get("alternative")
    if want["alt"] is None:
        if alt is not None:
            bad.append("an alternative the truth does not name")
    elif alt is None or alt.get("sha256") != want["alt"]["sha256"] or float(alt.get("amplitude")) != \
            want["alt"]["amplitude"] or alt.get("truth") != want["alt"]["truth"]:
        bad.append("C-PINS: the alternative is not the truth's")
    code = meta.get("code_sha256") or {}
    pins = {Path(rel).name: d for rel, d in T.CODE_PINS.items()}
    for name in ("s5p_nullexp.py", "s5n_pseudo.py", "unfold_2d_omnifold_unbinned.py"):
        if code.get(name) != pins[name]:
            bad.append(f"C-PINS: the product's {name} is not the bound file")
    moved = sorted(n for n, d in code.items() if n in pins and d != pins[n])
    if moved:
        bad.append(f"C-PINS: the product's code digests {moved} are not the bound files'")
    here = {"t3p_probe.py": T.sha256_path(Path(T.__file__).resolve()),
            "t3p_arms.py": T.sha256_path(Path(A.__file__).resolve())}
    if t3.get("code_sha256") != here:
        bad.append("the product's T3 code digests are not this reader's")
    ev, ref, so = t3.get("evidence") or {}, meta.get("refinement") or {}, t3.get("so") or {}
    if arm == "SO":
        if not (ref.get("ran") is False and so.get("template_rows") == 0 and so.get("pseudo_background_events") == 0
                and so.get("no_background") is True):
            bad.append("C-ARM SO")
    elif ref.get("ran") is not True:
        bad.append("the refinement did not run")
    if arm == "MU" and not (len(ev.get("fill_all_one", [])) == it and all(ev["fill_all_one"])):
        bad.append("C-ARM MU")
    if arm == "MW" and ev.get("mw_fits") != it:
        bad.append("C-ARM MW")
    if arm in ("MO", "OP"):
        dev = ev.get("max_rel_oracle", [])
        if len(dev) != it or not all(d <= A.ORACLE_RTOL for d in dev):
            bad.append(f"C-ARM {arm}")
    if arm == "OP" and not isinstance(ev.get("op_push_rel_change"), float):
        bad.append("C-ARM OP: no record of the second iteration")
    for k in TRACE_KEYS:
        if k not in arrays:
            bad.append(f"no {k}")
    if not bad:
        shapes = {"X16_push": (it, 16), "X16_pull": (it, 16), "R16_pull": (it, 16), "R16_push": (it, 16),
                  "R16_D": (16,), "R16_true": (16,), "R16_prior": (16,), "norm_push": (it,), "clip_step1": (it, 2)}
        for k, s in shapes.items():
            if arrays[k].shape != s:
                bad.append(f"{k} shape {arrays[k].shape}")
        if not all(np.all(np.isfinite(arrays[k])) for k in TRACE_KEYS + ("xsec_flat", "xtrue_flat")):
            bad.append("C-FIN: a non-finite array")
    return bad


def products(run: Path, repo: Path) -> dict:
    out = {}
    for arm, t, s in T.all_tasks():
        p = T.product_path(run / "runs", arm, t, s)
        files = sorted(p.parent.glob(f"{T.task_id(arm, t, s)}*.npz"))
        if files != [p]:
            raise Stop("completeness", f"{p.parent}: expected exactly {p.name}, found {[f.name for f in files]}")
        arrays, meta = load(p)
        bad = meta_problems(meta, arrays, arm, t, s, repo)
        if bad:
            raise Stop("product", f"{p.name}: {'; '.join(bad)}")
        out[(arm, t, s)] = (arrays, meta)
    return out


def priors(stage_rec: dict, M16: np.ndarray) -> dict[int, np.ndarray]:
    """C-P: P at each split, M16 times FD-PRR's nominal product's truth (its staged copy, carrying its pin)."""
    copies = {e["role"]: (Path(e["copy"]), e["sha256"]) for e in stage_rec["files"]}
    out = {}
    for s in (T.PRIMARY_SEED, *T.FLOOR_SEEDS):
        path, pin = copies.get(f"prr_B0_{T.PRIOR}_s{s}", (None, None))
        if path is None or T.sha256_path(path) != pin:
            raise Stop("C-P", f"FD-PRR's nominal product at split {s} is not staged with its pin")
        out[s] = M16 @ T._load(path, "xtrue_flat").astype(float)
    return out


# ------------------------------------------------------------------------------------------- quantities (§4)
def split_bias(b: np.ndarray, d: np.ndarray, rho: float | None) -> dict:
    """b_par = -rho d on S (0 outside), b_perp = b - b_par; ||b||^2 = ||b_par||^2 + ||b_perp||^2 exactly."""
    if rho is None:
        return {"rms_par": None, "rms_perp": None, "perp_share": None}
    S = np.abs(d) >= RD.D_MIN
    par = np.where(S, -rho * d, 0.0)
    perp = b - par
    nb = float(np.sum(b ** 2))
    return {"rms_par": float(np.sqrt(np.mean(par ** 2))), "rms_perp": float(np.sqrt(np.mean(perp ** 2))),
            "perp_share": float(np.sum(perp ** 2) / nb) if nb > 0 else None}


def trace_controls(arrays: dict, M16: np.ndarray, it: int) -> list[str]:
    """C-TRACE: the recorder's R00-R15 at k equals M16 times the production extraction at k (the final unfold, and
    each stored k), to 1e-12 relative; C-RECO: the reco cells lose no row."""
    bad = []
    pairs = [(it, arrays["xsec_flat"])] + [(k, arrays[f"xs_k{k}"]) for k in A.PAIR_KS if f"xs_k{k}" in arrays]
    for k, xs in pairs:
        ref = M16 @ np.asarray(xs, float)
        if not np.allclose(arrays["X16_push"][k - 1], ref, rtol=1e-12, atol=0):
            bad.append(f"C-TRACE at k = {k}")
    ric = arrays["reco_in_cells"]
    for i, key in ((0, "R16_prior"), (1, "R16_D")):
        if not np.isclose(ric[i], float(np.sum(arrays[key])), rtol=1e-12, atol=0):
            bad.append(f"C-RECO {key}")
    if np.any(arrays["R16_prior"] <= 0):
        bad.append("C-FIN: a reco cell with no prior")
    return bad


def quantities(arrays: dict, X: np.ndarray, P: np.ndarray, C: np.ndarray, it: int) -> dict:
    d = (X - P) / P
    per_k = []
    for k in range(1, it + 1):
        xh, xp = arrays["X16_push"][k - 1], arrays["X16_pull"][k - 1]
        rho, n_s = RD.rho(xh, X, P)
        b = (xh - X) / P
        g = RD.table_ii(xh / X - 1, C)
        per_k.append({"k": k, "rho": rho, "n_S": n_s, "rho_pull": RD.rho(xp, X, P)[0],
                      "rms_b": float(np.sqrt(np.mean(b ** 2))), **split_bias(b, d, rho),
                      "chi2": g["chi2"], "p": g["p"], "max_abs_z": g["max_abs_z"], "flagged": g["flagged"],
                      "rho_R1": RD.rho(arrays["R16_pull"][k - 1], arrays["R16_D"], arrays["R16_prior"])[0],
                      "rho_R2": RD.rho(arrays["R16_push"][k - 1], arrays["R16_D"], arrays["R16_prior"])[0]})
    dR = (arrays["R16_D"] - arrays["R16_prior"]) / arrays["R16_prior"]
    return {"per_k": per_k, "rms_d": float(np.sqrt(np.mean(d ** 2))), "rms_d_reco": float(np.sqrt(np.mean(dR ** 2))),
            "rho_RD": RD.rho(arrays["R16_D"], arrays["R16_true"], arrays["R16_prior"])[0],
            "clip_max": {"step1": arrays["clip_step1"].max(axis=0).tolist(), "step2": arrays["clip_step2"].max(axis=0).tolist()},
            "norm_push": arrays["norm_push"].tolist(), "miss_share_max": float(np.max(arrays["miss_share16"]))}


def rho_at(q: dict, k: int) -> float | None:
    return q["per_k"][k - 1]["rho"]


# ------------------------------------------------------------------------------------------- readings (§5)
def tr1_class(delta: float | None, bar: float) -> str:
    if delta is None:
        return "undefined"
    if delta <= -bar:
        return "lowers the limit"
    if delta >= bar:
        return "raises the limit"
    return "no effect"


def tr2_class(rho_op: float | None, bar: float) -> str:
    if rho_op is None:
        return "undefined"
    return "step 2 carries the truth" if abs(rho_op) < bar else "step 2 does not carry the truth"


def trajectory_class(rhos: list[float | None], dt: float, delta: float = DELTA) -> str:
    """§5.3, on rho(1..50): crosses, reaches 0, slow approach, plateau or rises (one class)."""
    if len(rhos) < 50 or any(r is None for r in rhos):
        return "undefined"
    r25, r50 = rhos[24], rhos[49]
    if min(rhos) <= -delta:
        return "crosses"
    if r50 < delta:
        return "reaches 0"
    if r25 - r50 >= dt:
        return "slow approach"
    if r50 - r25 >= dt:
        return "rises"
    return "plateau"


def location_class(r1: float | None, r2: float | None, rho: float | None, rho_d: float | None = None) -> str:
    """§5.4 at the last k: where the departure is lost (|.| >= the bar; a reco or truth overshoot counts too)."""
    if r1 is None or r2 is None or rho is None:
        return "undefined"
    if abs(r1) >= DELTA_R:
        return "step 1 does not match the pseudo-data"
    if abs(r2) >= DELTA_R:
        return "the pull-back or step 2 loses it"
    if abs(rho) >= DELTA:
        return "reco matched, truth not"
    return "closed"


def labels_for(tr1: dict, tr2: str, b0_traj: str, b0_loc: str) -> list[str]:
    out = []
    if tr1.get("MO") == "lowers the limit":
        out.append("consistent with a limit set at the misses")
    if tr1.get("MW") == "lowers the limit" or tr1.get("MU") == "lowers the limit":
        out.append("consistent with a limit a feasible miss treatment lowers")
    if tr1.get("SO") == "lowers the limit":
        out.append("consistent with a share from the background and refinement")
    if tr2 == "step 2 does not carry the truth":
        out.append("consistent with a limit set by step 2's representation")
    if b0_loc == "reco matched, truth not":
        out.append("consistent with weakly constrained directions")
    if b0_traj in ("slow approach", "reaches 0", "crosses"):
        out.append("consistent with slow convergence, not a fixed point")
    return out or ["unattributed"]


def readings(q: dict, prr: dict) -> dict:
    S0, FT = T.PRIMARY_SEED, T.FLOOR_TRUTH
    seeds = (S0, *T.FLOOR_SEEDS)
    s, bars = {}, {}
    for arm in TR1_ARMS:
        deltas = []
        for sd in seeds:
            a, b = rho_at(q[(arm, FT, sd)], 50), rho_at(q[("B0", FT, sd)], 50)
            deltas.append(None if a is None or b is None else a - b)
        s[arm] = RD.floor_sd(deltas)
        bars[arm] = max(BAR_FLOOR, T_Q * s[arm])
    s["OP"] = RD.floor_sd([rho_at(q[("OP", FT, sd)], 2) for sd in seeds])
    bars["OP"] = max(BAR_FLOOR, T_Q * s["OP"])
    dt = delta_t(prr)
    out = {"floor": {"s": s, "bars": bars, "T_Q": T_Q, "dof": len(seeds) - 1, "delta_t": dt,
                     "transfer": f"s is measured at {FT} and applied at q3 (a transfer); delta_t from FD-PRR's s_F1"},
           "TR-1": {}, "TR-1_k5": {}, "TR-2": {}, "rho_OP": {}, "trajectory": {}, "location": {}, "labels": {},
           "beside": {}}
    for t in T.TRUTHS:
        b50 = rho_at(q[("B0", t, S0)], 50)
        b5 = rho_at(q[("B0", t, S0)], 5)
        tr1, k5 = {}, {}
        for arm in TR1_ARMS:
            a50, a5 = rho_at(q[(arm, t, S0)], 50), rho_at(q[(arm, t, S0)], 5)
            tr1[arm] = tr1_class(None if a50 is None or b50 is None else a50 - b50, bars[arm])
            k5[arm] = None if a5 is None or b5 is None else a5 - b5
        op = rho_at(q[("OP", t, S0)], 2)
        tr2 = tr2_class(op, bars["OP"])
        if tr1["MO"] == "no effect" and tr2 == "step 2 does not carry the truth":
            tr1["MO"] = "no effect (bounded by step 2)"
        traj = {arm: trajectory_class([r["rho"] for r in q[(arm, t, S0)]["per_k"]], dt) for arm in TRAJ_ARMS}
        loc = {}
        for arm in A.ARMS:
            last = q[(arm, t, S0)]["per_k"][-1]
            loc[arm] = location_class(last["rho_R1"], last["rho_R2"], last["rho"])
        out["TR-1"][t], out["TR-1_k5"][t], out["TR-2"][t], out["rho_OP"][t] = tr1, k5, tr2, op
        out["trajectory"][t], out["location"][t] = traj, loc
        out["labels"][t] = labels_for(tr1, tr2, traj["B0"], loc["B0"])
        out["beside"][t] = {arm: {f"k{k}": {key: q[(arm, t, S0)]["per_k"][min(k, A.ITERS[arm]) - 1][key]
                                            for key in ("rho", "rms_b", "rms_perp", "chi2")} for k in (5, 50)}
                            for arm in A.ARMS}
    return out


# ------------------------------------------------------------------------------------------- the read
def read(run: Path, repo: Path, stage_rec: dict | None = None) -> tuple[dict, int]:
    why = incomplete(run)
    if why:
        return {"schema": SCHEMA, "labels": LABELS, "verdict": "INCOMPLETE", "why": why}, INCOMPLETE_RC
    import estimator_stability_analyze as an
    prr = check_inputs(repo)
    stage_rec = stage_rec if stage_rec is not None else json.loads((run / "stage.json").read_text())
    M16 = an.cell_matrix(str(repo / "nd-unfolding/pv-ladder/readouts/h2_definition.json"))
    prods = products(run, repo)
    Pr = priors(stage_rec, M16)
    mats, f, ct = RD.grade_matrices(repo)
    q, integrals = {}, []
    for (arm, t, s), (arrays, meta) in prods.items():
        it = A.ITERS[arm]
        bad = trace_controls(arrays, M16, it)
        if bad:
            raise Stop("trace", f"{T.task_id(arm, t, s)}: {'; '.join(bad)}")
        X = M16 @ arrays["xtrue_flat"].astype(float)
        if not np.all(X > 0) or not np.all(Pr[s] > 0):
            raise Stop("C-FIN", f"{T.task_id(arm, t, s)}: a non-positive truth or prior on R00-R15")
        q[(arm, t, s)] = quantities(arrays, X, Pr[s], mats[t], it)
        integrals += [X, Pr[s], *arrays["X16_push"], *arrays["X16_pull"]]
    rd = readings(q, prr)
    out = {"schema": SCHEMA, "labels": LABELS, "verdict": "COMPLETE",
           "controls": {"C-CT": {k: v for k, v in ct.items() if k != "table_ii_flags"}, "C-P": {"pass": True},
                        "C-TRACE": {"pass": True}, "C-RECO": {"pass": True}, "products": {"pass": True}},
           "readings": rd,
           "table": {f"{arm}/{t}/s{s}": v for (arm, t, s), v in q.items()}}
    import fd_f0_regrade as F
    F.LeakGuard(f, integrals).check("readout", out)
    return out, 0


def text(out: dict) -> str:
    if out["verdict"] != "COMPLETE":
        return f"verdict {out['verdict']}: {out.get('why')}\n"
    rd = out["readings"]
    lines = [f"verdict COMPLETE; floor s {rd['floor']['s']}, bars {rd['floor']['bars']}, delta_t {rd['floor']['delta_t']:.4f}"]
    for t in T.TRUTHS:
        lines.append(f"{t}: TR-1 {rd['TR-1'][t]}; TR-2 {rd['TR-2'][t]} (rho_OP {rd['rho_OP'][t]})")
        lines.append(f"{t}: trajectory {rd['trajectory'][t]}")
        lines.append(f"{t}: location {rd['location'][t]}")
        lines.append(f"{t}: labels {rd['labels'][t]}")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--run", type=Path, required=True, help="the study's OUT directory")
    ap.add_argument("--repo", type=Path, default=REPO)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    try:
        out, rc = read(a.run, a.repo)
    except Stop as e:
        out, rc = {"schema": SCHEMA, "labels": LABELS, "verdict": "STOP", "why": str(e)}, STOP_RC
    a.out.mkdir(parents=True, exist_ok=False)
    (a.out / "readout.json").write_text(json.dumps(out, indent=1) + "\n")
    (a.out / "readout.txt").write_text(text(out))
    print(text(out), end="")
    return rc


if __name__ == "__main__":
    sys.exit(main())
