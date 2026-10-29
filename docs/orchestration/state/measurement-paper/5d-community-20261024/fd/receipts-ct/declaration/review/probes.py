#!/usr/bin/env python3
"""Reviewer probes on fd_ct_readers.py at 0cdb2cb4 (read-only: imports the worktree's modules, writes only under this
scratch dir). Each section prints what it measures.

    TMPDIR=<scratch> python3 -B probes.py
"""
import contextlib
import io
import json
import shutil
import sys
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
WT = Path(str(HERE).replace("review-ct-notes", "review-ct"))
sys.path.insert(0, str(WT / "nd-unfolding"))
sys.path.insert(0, str(WT / "nd-unfolding/tests"))
import fd_ct_readers as ct  # noqa: E402
import fd_f0_regrade as F  # noqa: E402
import s1_assemble as sa  # noqa: E402
import test_fd_ct_readers as T  # noqa: E402

ROOT = HERE / "probe-tree"


def section(t):
    print("\n==== " + t, flush=True)


def run_tool(t, argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.ExitStack() as st:
        st.enter_context(mock.patch.dict(ct.PINS, t.pins))
        st.enter_context(mock.patch.dict(ct.W2B, getattr(t, "w2b", ct.W2B)))
        st.enter_context(contextlib.redirect_stdout(out))
        st.enter_context(contextlib.redirect_stderr(err))
        try:
            rc = ct.main(argv)
        except SystemExit as e:
            rc = e.code
    return rc, out.getvalue(), err.getvalue()


def out_of_span(v, G):
    """Euclidean share of v outside span(columns of G)."""
    Q, _ = np.linalg.qr(G)
    res = v - Q @ (Q.T @ v)
    return float(np.linalg.norm(res) / np.linalg.norm(v))


shutil.rmtree(ROOT, ignore_errors=True)

# --------------------------------------------------------------------------------------------- 5A: S_ref projection
section("P-A  5A S_ref16: ratio of footprint-averaged r (tool) vs footprint average of the 2D relative b_X/x (linear)")
t = T.Tree(ROOT / "a", seed=1).write_common().write_period()
z = {f"{q}_{X}": v for X in ct.PERIODS for q, v in (("g", t.g[X]), ("r", t.r[X]))}
om, outside = ct.footprint(t.U, t.fm, t.xc, t.support)
g = {X: om @ t.g[X] for X in ct.PERIODS}
G = np.array([g["PA"], g["PB"]]).T            # span of C_PL16 (rank 2)
for label, mvar in (("fixture m ~ U(0.8, 1.2)", None), ("m with a p_parallel step of 7 % (2D-like)", "step")):
    if mvar == "step":
        ipz = t.support % 16
        m = np.where(ipz >= 10, 1.07, 1.0) * np.random.default_rng(5).uniform(0.9, 1.1, t.support.size)
        r = {X: (1 + t.g[X]) * m for X in ct.PERIODS}
    else:
        r = t.r
    rt = {X: om @ r[X] for X in ct.PERIODS}
    tool = {X: t.e[X] * (rt[X] / rt["PA"] - 1) for X in ("PB", "PC")}
    lin = {X: t.e[X] * (om @ (r[X] / r["PA"] - 1)) for X in ("PB", "PC")}
    for X in ("PB", "PC"):
        d = np.abs(tool[X] - lin[X]) / np.abs(lin[X])
        print(f"{label}: b_{X}: |tool - linear| / |linear| per cell median {np.median(d):.3e} max {d.max():.3e}; "
              f"out-of-span share of C_PL16: tool {out_of_span(tool[X], G):.3e}, linear {out_of_span(lin[X], G):.3e}")
    sd_t = np.sqrt(sum(tool[X] ** 2 for X in tool))
    sd_l = np.sqrt(sum(lin[X] ** 2 for X in lin))
    print(f"{label}: sigma(S_ref16) tool/linear per cell: median {np.median(sd_t / sd_l):.4f} "
          f"min {np.min(sd_t / sd_l):.4f} max {np.max(sd_t / sd_l):.4f}")

# ---------------------------------------------------------------------------------- 5A: leak through 'outside'
section("P-C  5A weight_outside_2d_support (central) = |X_sup / f - 1| for X_sup = the central value's supported-"
        "footprint integral, which is not in the guard's table")
t = T.Tree(ROOT / "c", seed=2).write_common().write_period()
rc, so, se = run_tool(t, t.argv_period)
print("tool rc", rc)
out = json.loads((t.out / "period.json").read_text())
shape = sa.s1.fine_shape()
idx = np.unravel_index(np.arange(t.fm.size), shape)
c2 = idx[0] * 16 + idx[1]
ins = np.isin(c2, t.support)
Usup = t.U * ins[None, :]
Xsup = Usup @ t.xc
outside = np.array(out["variants"]["central"]["weight_outside_2d_support"])
print("max | outside - (1 - X_sup/f) | :", float(np.max(np.abs(outside - (1 - Xsup / t.f)))))
f0g = F.LeakGuard(t.f, [t.U @ t.xp])
print("tool's guard (f, U@prior): offending numbers in the written readout:", f0g.count(out))
g2 = F.LeakGuard(t.f, [t.U @ t.xp, Xsup])
print("guard with X_sup added:    offending numbers in the written readout:", g2.count(out))

# ---------------------------------------------------------------------------------- 4C: percentile definitions
section("P-B  4C weighted percentiles (inverted ECDF) vs unweighted (np.percentile, linear interpolation): "
        "difference at EQUAL weights, chi2_16 samples of A7's sizes")
rng = np.random.default_rng(7)
for n in (1343, 1365, 1751):
    diffs = []
    for _ in range(200):
        v = rng.chisquare(16, n)
        a = np.array(ct.weighted_percentiles(v, np.ones(n), ct.PERCENTILES))
        b = np.percentile(v, ct.PERCENTILES)
        diffs.append(a - b)
    diffs = np.array(diffs)
    print(f"n={n}: mean (weighted@w=1 - unweighted) per percentile {dict(zip(ct.PERCENTILES, np.round(diffs.mean(0), 4)))}; "
          f"max |diff| {dict(zip(ct.PERCENTILES, np.round(np.abs(diffs).max(0), 4)))}")

# ---------------------------------------------------------------------------------- 4C: C4 is an identity
section("P-D  4C control C4 (weighted mean chi2 about truth = about b~ + chi2(b~)) on arbitrary inputs")
worst = 0.0
for k in range(2000):
    n = int(rng.integers(5, 300))
    r = rng.normal(rng.normal(0, 0.5), rng.uniform(0.001, 1), (n, 16)) * rng.uniform(0.1, 10, 16)
    w = rng.uniform(0, 5, n) ** rng.uniform(0.5, 4)
    A = rng.normal(size=(16, 16))
    M = A @ A.T * 10 ** rng.uniform(-6, 0) + 1e-9 * np.eye(16)
    L = np.linalg.cholesky(M)
    b = (w[:, None] * r).sum(0) / w.sum()
    yt, yc = np.linalg.solve(L, r.T), np.linalg.solve(L, (r - b).T)
    c2t, c2c = (yt * yt).sum(0), (yc * yc).sum(0)
    gap = abs(float(w @ c2t / w.sum()) - float(w @ c2c / w.sum()) - ct.quad(b, M))
    worst = max(worst, gap / max(1.0, float(w @ c2t / w.sum())))
print(f"2000 random (r, w, M) sets: worst normalized gap {worst:.3e} against the 1e-9 refusal: C4 cannot fire on any input")

# ---------------------------------------------------------------------------------- 5A: P4 implied by P0
section("P-E  5A control P4 on any footprint of offsets that pass P0 (sum_X e_X g_X = 0 on the 2D cells)")
worst_ident, worst_rank, worst_neg = 0.0, 0, 0.0
for k in range(500):
    e = rng.dirichlet([3, 2, 1])
    n2 = 205
    gA, gB = rng.normal(0, 0.05, n2), rng.normal(0, 0.05, n2)
    gC = -(e[0] * gA + e[1] * gB) / e[2]
    W = rng.uniform(0, 1, (16, n2)) * (rng.uniform(size=(16, n2)) < 0.3)
    W[:, 0] += 1e-3
    W /= W.sum(1, keepdims=True)
    gR = [W @ gA, W @ gB, W @ gC]
    ident = float(np.max(np.abs(sum(ei * gi for ei, gi in zip(e, gR)))))
    V2 = float((e ** 2).sum())
    C = V2 / (1 - V2) * sum(ei * np.outer(gi, gi) for ei, gi in zip(e, gR))
    lam = np.linalg.eigvalsh(C)
    worst_ident = max(worst_ident, ident)
    worst_rank = max(worst_rank, int(np.sum(lam > 1e-12 * lam.max())))
    worst_neg = min(worst_neg, lam.min() / lam.max())
print(f"500 random footprints: worst |sum e g_R| {worst_ident:.3e} (refusal > 1e-12), worst rank {worst_rank} "
      f"(refusal > 2), worst min/max eigenvalue {worst_neg:.3e} (refusal < -1e-12): P4 cannot fire once P0 passes")

# ---------------------------------------------------------------------------------- 3a: in-span chance level
section("P-F  3a fraction_of_half_span_in_C_resp_span for a direction-free d (isotropic random) and a rank-4 C_resp")
t = T.Tree(ROOT / "f", seed=3).write_common()
ff = np.outer(t.f, t.f)
lam, V = np.linalg.eigh(t.Cr / ff)
keep = lam > 1e-12 * lam.max()
fr = []
for k in range(20000):
    d = rng.normal(size=16)
    Pd = V[:, keep] @ (V[:, keep].T @ d)
    fr.append(Pd @ Pd / (d @ d))
fr = np.array(fr)
print(f"rank {keep.sum()}: random-direction in-span fraction mean {fr.mean():.4f} (rank/16 = {keep.sum() / 16:.4f}), "
      f"16-84 % {np.percentile(fr, 16):.3f}-{np.percentile(fr, 84):.3f}")
# the 3a label states only that 1 means wholly inside; a value like 0.4 has no stated reference
# dependence on the coordinate choice: same d, same C_resp, in absolute units instead of relative
d = rng.normal(size=16) * 0.03
lamA, VA = np.linalg.eigh(t.Cr)
keepA = lamA > 1e-12 * lamA.max()
dA = d * t.f
PA_ = VA[:, keepA] @ (VA[:, keepA].T @ dA)
Pr = V[:, keep] @ (V[:, keep].T @ d)
print(f"one d: in-span fraction in relative units {Pr @ Pr / (d @ d):.4f}, in absolute units {PA_ @ PA_ / (dA @ dA):.4f}, "
      f"in C_total_resp's metric (M-orthogonal) "
      f"{float(np.linalg.solve(np.linalg.cholesky((t.Ct + t.Cr) / ff), Pr) @ np.linalg.solve(np.linalg.cholesky((t.Ct + t.Cr) / ff), Pr)) / float(np.linalg.solve(np.linalg.cholesky((t.Ct + t.Cr) / ff), d) @ np.linalg.solve(np.linalg.cholesky((t.Ct + t.Cr) / ff), d)):.4f} (Euclidean projector, metric norm)")

# ---------------------------------------------------------------------------------- 3a: curvature form vs build_cresp
section("P-G  3a curvature_ratio (relative-unit norms) vs build_cresp.curvature_ratio (MP-1 G3 form, absolute norms)")
sys.path.insert(0, str(WT / "nd-unfolding"))
import build_cresp as bc  # noqa: E402
rng2 = np.random.default_rng(11)
for k in range(3):
    Z = t.f * (1 + rng2.normal(0, 0.01, 16))
    sm, sp = rng2.normal(-0.03, 0.01, 16), rng2.normal(0.03, 0.01, 16)
    X0, X1 = Z * (1 + sm), Z * (1 + sp)
    tool = float(np.linalg.norm(sp + sm) / np.linalg.norm(sp - sm))
    g3 = bc.curvature_ratio(X0, Z, X1)
    print(f"draw {k}: tool form {tool:.4f}; build_cresp G3 form on the same three products {g3:.4f}; "
          f"f max/min {t.f.max() / t.f.min():.1f}")
