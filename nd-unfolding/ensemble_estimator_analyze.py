#!/usr/bin/env python3
"""ENS1's analysis (ENS1-DECLARATION.md §4-§7): gates E1-E4 and G0, stage 1's stability verdict, ĉ and the readouts;
stage 2's bias verdict. Relative quantities only; no data read.

    ensemble_estimator_analyze.py --stage {1,2} --root OUT --pin M --refs DIR --fdstab-sums SHA256SUMS
        --s5c-contract P --sigma-receipt P --h2-definition P --out JSON [--fdstab-readout fd_stab.json --repo .]

``--refs`` mirrors FD-STAB's run directory: a reference named ``runs/control/...`` in FD-STAB's SHA256SUMS is read at
``<refs>/runs/control/...`` and must carry that line's digest. Stage 2 needs stage 1's products (its floor s_E).

Each product is reduced on load to its 169 functionals: s5e's 153 (U) and the 16 cells (M16), both linear in xsec_flat,
so the ensemble mean of the functionals is the functional of the ensemble mean (§2.1).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import ensemble_estimator_probe as eep  # noqa: E402
import estimator_stability_analyze as esa  # noqa: E402
import estimator_stability_probe as esp  # noqa: E402

N, P = eep.N_ENS, 10
BOUND_MEDIAN, BOUND_MAX = esa.BOUND_MEDIAN, esa.BOUND_MAX
C_STAR = 1.0 / 6.827531337314785 ** 2 - 1.0 / N      # §4.3 (fd_stab.json:7)
EPS = math.sqrt(2.0 / 20.0) / N                       # §7.1
SD_UPPER_E = 1.357637703528655                        # sqrt(20 / chi2_0.05,20), §5.2
FDSTAB_PREFIX = "runs/control/"
STAB_REF = FDSTAB_PREFIX + "stability/stab_control_b-_j{}.npz"
CLOSURE_REF = FDSTAB_PREFIX + "closure/{t}/stab_control_{t}_s991000.npz"
STAGE_SHARDS = eep.SHARDS
INCOMPLETE_RC, STOP_RC = 3, 4


class Stop(RuntimeError):
    """A gate failed: nothing is graded (§4.4)."""


def sha256_path(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 22), b""):
            h.update(block)
    return h.hexdigest()


# ------------------------------------------------------------------------------------------------- receipts
def incomplete(root: Path, stage: int, pin: str) -> str | None:
    """Why the stage is not complete: the dry DONE and all six shards' DONE, rc 0, every task ended, one pin."""
    sd = root / f"stage{stage}"
    for name in ["log-dry"] + [f"log-shard{i}" for i in range(STAGE_SHARDS)]:
        done = sd / name / "DONE"
        if not done.is_file():
            return f"no DONE receipt at {done}"
        for bad in ("STOP", "FAILED"):
            if (sd / name / bad).exists():
                return f"{name} left {bad}"
        d = json.loads(done.read_text())
        if d.get("rc") != 0 or d.get("tasks") != d.get("ended") or d.get("pin") != pin or d.get("stage") != stage:
            return f"{name}: the receipt is not a completed run at pin {pin}: {d}"
    return None


# ------------------------------------------------------------------------------------------------- the pieces
def functional_matrices(contract: Path, h2_definition: Path):
    U, names = esa.functionals(json.loads(Path(contract).read_text()))
    return np.asarray(U), list(names), np.asarray(esa.cell_matrix(str(h2_definition)))


def sigma_rel(receipt: Path, names: list) -> np.ndarray:
    """E4: the pinned σ receipt over s5c's 153 functionals."""
    if sha256_path(receipt) != esa.SIGMA_RECEIPT_SHA256:
        raise Stop("E4: the sigma receipt is not the pinned file")
    r = json.loads(Path(receipt).read_text())
    if list(r["functional_names"]) != list(names):
        raise Stop("E4: the receipt's functionals are not s5c's reported functionals")
    return np.asarray(r["sigma_rel_pct"], float) / 100.0


def pinned_refs(refs: Path, sums: Path, names: list[str]) -> dict[str, Path]:
    """E3: each named FD-STAB reference at its SHA256SUMS line."""
    pinned = dict(reversed(line.split(None, 1)) for line in Path(sums).read_text().splitlines() if line.strip())
    out = {}
    for n in names:
        p = Path(refs) / n
        if n not in pinned or not p.is_file() or sha256_path(p) != pinned[n]:
            raise Stop(f"E3: {n} is not FD-STAB's pinned product")
        out[n] = p
    return out


def estimator_code(meta: dict) -> dict:
    """The estimator files' digests a product carries: the runner's code_sha256 and the bound probe's."""
    return {"runner": meta.get("code_sha256"), "stability_probe": (meta.get("stability_probe") or {}).get("code_sha256")}


def check_stability_meta(m: dict, name: str) -> None:
    st = eep.STABILITY
    if (m.get("construction"), m.get("truth"), m.get("eavail_ratio_sha256"), m.get("pseudo_seed")) != (
            "pseudo", st["truth"], st["ratio_sha256"], st["pseudo_seed"]):
        raise Stop(f"E1: {name} is not the declared stability input")
    if (m.get("input_npz_sha256"), m.get("bkg_dump_sha256")) != (st["npz_sha256"], st["bkg_sha256"]):
        raise Stop(f"E1: {name} was not made from the declared inputs")
    if m.get("bootstrap_seed") is not None:
        raise Stop(f"E1: {name} is a bootstrap replica")
    if (m.get("stability_probe") or {}).get("candidate") != "control":
        raise Stop(f"E1: {name} did not go through FD-STAB's control path")


def stage1_products(root: Path, U_all: np.ndarray):
    """E1/E2 and the reduction: F[s, k] (21 x 96 x 169), xtrue of the base, the F64 base's functionals and meta."""
    F = np.full((1 + len(eep.PROTOCOL_SEEDS), N, U_all.shape[0]), np.nan)
    codes, digests, xtrue = set(), {}, None
    seeds = (eep.BASE_SEED, *eep.PROTOCOL_SEEDS)
    for i, s in enumerate(seeds):
        for k in range(1, N + 1):
            p = root / "runs" / "stability" / f"ens1_k{k:03d}_b-_j{s}.npz"
            if not p.is_file():
                raise Stop(f"E1: {p.name} is missing")
            x, xt, m = esa.load(p)
            e = m.get("ens1") or {}
            if (e.get("schema"), e.get("mode"), e.get("k"), e.get("internal_seed"), e.get("protocol_seed")) != (
                    eep.SCHEMA, "stability", k, eep.INTERNAL_BASE + k, s) or m.get("jitter_seed") != s:
                raise Stop(f"E1: {p.name} does not carry its own (s, k)")
            check_stability_meta(m, p.name)
            if e.get("moved_rows") != {"MCgen": 0, "MCreco": 0, "measured": 0, "bkg_reco": 0}:
                raise Stop(f"E5: {p.name} records moved rows {e.get('moved_rows')} (A1: the zone keeps every cell)")
            if m.get("coords") != "float64":
                raise Stop(f"E1: {p.name} did not run in float64 coordinates")
            codes.add(json.dumps({**estimator_code(m), "ens1": e.get("code_sha256")}, sort_keys=True))
            digests[(s, k)] = json.dumps(e.get("coord_sha256"), sort_keys=True)
            F[i, k - 1] = U_all @ x
            if s == eep.BASE_SEED and k == 1:
                xtrue = xt
    if len(codes) != 1:
        raise Stop(f"E1: the products carry {len(codes)} code digest sets, not one")
    for k in range(1, N + 1):          # E2: the perturbations survived
        if len({digests[(s, k)] for s in seeds}) != len(seeds):
            raise Stop(f"E2: at internal seed {k} two inputs' coordinates are identical after the internal jitter")
    for s in seeds:
        if len({digests[(s, k)] for k in range(1, N + 1)}) != N:
            raise Stop(f"E2: at input {s} two internal seeds gave identical coordinates")
    return F, xtrue, json.loads(codes.pop())


def f64_base(root: Path, U_all: np.ndarray, code: dict):
    """E3 for G0's base: ENS1's F64(x), float64, seed 0, no internal jitter, the same ENS1 code."""
    p = root / "runs" / "F64" / "ens1_F64_b-_j0.npz"
    if not p.is_file():
        raise Stop("E3: the F64 base is missing")
    x, xt, m = esa.load(p)
    e = m.get("ens1") or {}
    check_stability_meta(m, p.name)
    if e.get("mode") != "base" or e.get("k") is not None or e.get("code_sha256") != code["ens1"]:
        raise Stop("E3: the F64 base is not ENS1's base product")
    if e.get("moved_rows") != {"MCgen": 0, "MCreco": 0, "measured": 0, "bkg_reco": 0}:
        raise Stop(f"E5: the F64 base records moved rows {e.get('moved_rows')}")
    check_float64_base(m, p.name)
    return U_all @ x, xt, m


def check_float64_base(m: dict, name: str) -> None:
    """G0 refuses a float32 base (§4.2, audit ENS-1)."""
    if m.get("coords") != "float64" or m.get("jitter_seed") != eep.BASE_SEED:
        raise Stop(f"G0: {name} is not a float64 seed-0 base (coords {m.get('coords')}, jitter {m.get('jitter_seed')})")


def control_jitters(refs: Path, sums: Path, U_all: np.ndarray, base_meta: dict):
    """FD-STAB's control jitters 1-20 (E3), each with the F64 base's estimator code (audit LOW-2)."""
    names = [STAB_REF.format(s) for s in eep.PROTOCOL_SEEDS]
    paths = pinned_refs(refs, sums, names)
    out = []
    want = estimator_code(base_meta)
    for n in names:
        x, _, m = esa.load(paths[n])
        check_stability_meta(m, n)
        if estimator_code(m) != want:
            raise Stop(f"E3: {n} was made by other estimator code than the F64 base")
        out.append(U_all @ x)
    return np.array(out)


# ------------------------------------------------------------------------------------------------ statistics
def stats_at_p(rel: np.ndarray, sigma: np.ndarray, p: int = P) -> dict:
    """The bound FD-STAB §4.3 statistic (esa.stability_stats) with N_PAIRS rebound to p for the call (§4.1)."""
    saved = esa.N_PAIRS
    esa.N_PAIRS = p
    try:
        return esa.stability_stats(rel, sigma)
    finally:
        esa.N_PAIRS = saved


def usable(base: np.ndarray, sigma: np.ndarray) -> np.ndarray:
    ok = (base != 0) & np.isfinite(sigma) & (sigma > 0)
    if int(ok.sum()) != esa.N_FUNCTIONALS:
        raise Stop(f"{int(ok.sum())} usable functionals, not s5e's {esa.N_FUNCTIONALS}")
    return ok


def c_hat(F_base_k: np.ndarray, E: np.ndarray) -> np.ndarray:
    """§7.1 per functional: q = v_b / v_w - 1/N, ĉ = q / (1 + q). F_base_k: (N, f) single fits at x; E: (21, f)."""
    v_w = np.var(F_base_k / E[0] - 1.0, axis=0, ddof=1)
    v_b = np.var(E / E[0] - 1.0, axis=0, ddof=1)
    q = v_b / v_w - 1.0 / N
    return q / (1.0 + q)


def c_hat_reading(verdict: str, top: float) -> str | None:
    """§7.1's interpretation rule; it never moves the verdict."""
    if verdict != "STAB_FAIL":
        return None
    if top >= C_STAR:
        return "the failure is carried by a component that averaging over rounding perturbations does not remove"
    if top <= EPS:
        return ("no input-dependent component is resolved; the failure is consistent with the declared power "
                "(§4.6, §6) or with a heavier tail than the model's")
    return None


def stage1(a) -> dict:
    root = Path(a.root)
    U, names, M16 = functional_matrices(a.s5c_contract, a.h2_definition)
    sigma = sigma_rel(Path(a.sigma_receipt), names)
    U_all = np.vstack([U, M16])
    nf = U.shape[0]
    F, xtrue, code = stage1_products(root, U_all)
    E = F.mean(axis=1)                                        # (21, 169): E_96 at x and at x_1..x_20
    ok = usable(E[0, :nf], sigma)
    rel_E = E[1:, :nf][:, ok] / E[0, :nf][ok] - 1.0
    stab_E = stats_at_p(rel_E, sigma[ok])
    f64, _, f64_meta = f64_base(root, U_all, code)
    Fj = control_jitters(Path(a.refs), Path(a.fdstab_sums), U_all, f64_meta)
    ok0 = usable(f64[:nf], sigma)
    rel_F = Fj[:, :nf][:, ok0] / f64[:nf][ok0] - 1.0
    stab_F = stats_at_p(rel_F, sigma[ok0])
    g0 = not stab_F["passes"]
    if not g0:
        verdict = "UNINFORMATIVE"
    else:
        verdict = "STAB_PASS" if stab_E["passes"] else "STAB_FAIL"
    ch = c_hat(F[0][:, :nf][:, ok], E[:, :nf][:, ok])
    z = np.abs(rel_E) / sigma[ok]
    per_fun = np.maximum(z[0::2], z[1::2]).mean(axis=0)
    top10 = np.argsort(per_fun)[::-1][:10]
    top_med = float(np.median(ch[top10]))
    sd_k = np.std(F[0] / E[0] - 1.0, axis=0, ddof=1) / math.sqrt(N)
    cells_E = E[:, nf:]
    s_E = esa.cell_sd(cells_E[0], list(cells_E[1:]))
    out = {"schema": "ens1-analysis/1", "stage": 1, "label": "ENS1 stage 1 on the probe's products; relative only",
           "verdict": verdict, "g0_informative": g0, "stability_E96": stab_E, "stability_F_P10": stab_F,
           "bars": {"median": BOUND_MEDIAN, "max": BOUND_MAX}, "pairs": P, "N": N,
           "c_hat": {"median_all": float(np.median(ch)), "top10_functionals": [names_ok(names, ok)[i] for i in top10],
                     "top10": [float(ch[i]) for i in top10], "top10_median": top_med, "c_star": C_STAR, "eps": EPS,
                     "reading": c_hat_reading(verdict, top_med), "note": "descriptive; never moves the verdict (§7.1)"},
           "numerical_uncertainty": {"functionals_sigma_units": (sd_k[:nf][ok] / sigma[ok]).tolist(),
                                     "cells_relative": sd_k[nf:].tolist()},
           "cell_sd_E96": s_E.tolist(), "code": code}
    if xtrue is not None:
        xt16 = M16 @ xtrue
        out["stability_truth_bias_descriptive"] = {"E96": (cells_E[0] / xt16 - 1.0).tolist(),
                                                   "F64": (f64[nf:] / xt16 - 1.0).tolist()}
    return out


def names_ok(names, ok):
    return [n for n, keep in zip(names, ok) if keep]


# ------------------------------------------------------------------------------------------------- stage 2
def stage2(a, s1: dict) -> dict:
    if s1.get("verdict") != "STAB_PASS":
        raise Stop(f"stage 2 runs only on STAB_PASS; stage 1 read {s1.get('verdict')}")
    root = Path(a.root)
    U, names, M16 = functional_matrices(a.s5c_contract, a.h2_definition)
    refs, sums = Path(a.refs), Path(a.fdstab_sums)
    # F's floor: FD-STAB's control base and 51 jitters, reproducing the committed cell_sd.control
    stab_names = [STAB_REF.format("-")] + [STAB_REF.format(j) for j in range(1, 52)]
    sp = pinned_refs(refs, sums, stab_names)
    cells = [M16 @ esa.load(sp[n])[0] for n in stab_names]
    s_F = esa.cell_sd(cells[0], cells[1:])
    committed = np.asarray(json.loads(Path(a.fdstab_readout).read_text())["cell_sd"]["control"], float)
    if not np.allclose(s_F, committed, rtol=0, atol=1e-8):
        raise Stop("s_F does not reproduce FD-STAB's committed cell_sd.control")
    s_E = np.asarray(s1["cell_sd_E96"], float) * (SD_UPPER_E / esa.SD_UPPER)
    judged = [t for t in eep.CLOSURE_TRUTHS if t != eep.DETERMINISM[1]]
    cp = pinned_refs(refs, sums, [CLOSURE_REF.format(t=t) for t in judged])
    bias, ok_all = {}, []
    for t in judged:
        xs, xt0, metas = [], None, []
        for k in range(1, N + 1):
            p = root / "runs" / "closure" / t / f"ens1_{t}_k{k:03d}_s991000.npz"
            if not p.is_file():
                raise Stop(f"{p.name} is missing")
            x, xt, m = esa.load(p)
            e = m.get("ens1") or {}
            if (e.get("mode"), e.get("truth"), e.get("k")) != ("closure", t, k):
                raise Stop(f"{p.name} does not carry its own (truth, k)")
            if e.get("moved_rows") != {"MCgen": 0, "MCreco": 0, "measured": 0, "bkg_reco": 0}:
                raise Stop(f"E5: {p.name} records moved rows {e.get('moved_rows')}")
            if xt0 is None:
                xt0 = xt
            elif not np.array_equal(xt, xt0):
                raise Stop(f"{t}: the truth vector differs across internal seeds")
            xs.append(M16 @ x)
            metas.append(m)
        xF, xtF, mF = esa.load(cp[CLOSURE_REF.format(t=t)])
        for key in ("hypothesis", "alternative"):
            got = {json.dumps((m.get(key) or {}).get("sha256")) for m in metas}
            if got != {json.dumps((mF.get(key) or {}).get("sha256"))}:
                raise Stop(f"{t}: the {key} digest differs from FD-STAB's control closure")
        if {m.get("split_key") for m in metas} != {mF.get("split_key")}:
            raise Stop(f"{t}: the MC split differs from FD-STAB's control closure")
        b_E = np.mean(xs, axis=0) / (M16 @ xt0) - 1.0
        b_F = (M16 @ xF) / (M16 @ xtF) - 1.0
        bias[t] = esa.no_worse(b_E, s_E, b_F, s_F)
        ok_all.append(bias[t]["no_worse"])
    d0 = esa.load(root / "runs" / "closure" / "nominal" / "ens1_nominal_k001_s991000.npz")
    d1 = esa.load(root / "runs" / "closure" / "A7_mnvtune" / "ens1_A7_mnvtune_k001_s991000.npz")
    if not (np.array_equal(d0[0], d1[0]) and np.array_equal(d0[1], d1[1])):
        raise Stop("the determinism pair (nominal, A7_mnvtune) at k = 1 differs")
    status = esa.bias_status(ok_all)
    verdict = "INVALID" if status is None else ("PASS" if status else "BIAS_WORSE")
    readout = {t: {"E96": [bias[t]["rms"], bias[t]["max"]], "F": [bias[t]["rms_control"], bias[t]["max_control"]]}
               for t in esa.GIBUU_READOUT if t in bias}
    return {"schema": "ens1-analysis/1", "stage": 2, "verdict": verdict, "bias": bias, "truths_judged": judged,
            "worse": sorted(t for t in judged if bias[t]["no_worse"] is False),
            "sd_upper": {"E96": SD_UPPER_E, "F": esa.SD_UPPER}, "s_F": s_F.tolist(), "s_E_scaled": s_E.tolist(),
            "gibuu_readout_descriptive": {"note": "used by no criterion (§5.3)", **readout}}


# ------------------------------------------------------------------------------------------------------ main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--stage", type=int, choices=(1, 2), required=True)
    for opt in ("--root", "--pin", "--refs", "--fdstab-sums", "--s5c-contract", "--sigma-receipt", "--h2-definition",
                "--out"):
        ap.add_argument(opt, required=True)
    ap.add_argument("--stage1", help="stage 2: stage 1's analysis JSON")
    ap.add_argument("--fdstab-readout", help="stage 2: fd_stab.json (readout-2), for the s_F reproduction")
    a = ap.parse_args(argv)
    why = incomplete(Path(a.root), a.stage, a.pin)
    if why:
        Path(a.out).write_text(json.dumps({"schema": "ens1-analysis/1", "stage": a.stage, "verdict": "INCOMPLETE",
                                           "why": why}, indent=1) + "\n")
        print(json.dumps({"verdict": "INCOMPLETE", "why": why}))
        return INCOMPLETE_RC
    try:
        if a.stage == 1:
            out = stage1(a)
        else:
            if not a.stage1 or not a.fdstab_readout:
                raise Stop("stage 2 needs --stage1 and --fdstab-readout")
            out = stage2(a, json.loads(Path(a.stage1).read_text()))
    except Stop as exc:
        Path(a.out).write_text(json.dumps({"schema": "ens1-analysis/1", "stage": a.stage, "verdict": "STOP",
                                           "why": str(exc)}, indent=1) + "\n")
        print(json.dumps({"verdict": "STOP", "why": str(exc)}))
        return STOP_RC
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"verdict": out["verdict"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
