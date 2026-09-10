#!/usr/bin/env python3
"""Does any endpoint-A criterion bound the RELEASED error bars? Measured, at `6f24fb00`.

Joseph's adequacy question, verbatim through the orchestrator: *"retained rank and subspace
stability do not by themselves establish stability of projected uncertainties."* This probe
establishes that mechanically and then measures the candidate that does.

⚠ THIS FILE IS NOT THE FROZEN rho PROBE. `probe-z-criteria-acceptance-mathematics-20260910.py` is
history and is not touched here; the universal-bound approach it explored is NOT reopened. Nothing
below computes a bound over an unmeasured ensemble -- every section evaluates a DECLARED functional
on a DECLARED operand, which is the shape round 2's outcome (2) left standing.

SECTIONS
  1  the released error bar IS `sqrt(u' C u)` with `u` a row of `M` -- an exact identity, not an
     analogy, and it is what makes `s_proj` the released quantity rather than a proxy for it
  2  A-4 IS INADEQUATE, DEMONSTRATED: a member with `||P_0 - P_k||_2` EXACTLY 0 and identical
     retained rank, whose released error bars move by a chosen amount
  3  the diagonal legs are blind THROUGH the projection, and the projection is where A lives
  4  the validator mechanics for task (2): what actually happens to cause 3 if `cause3_corr` is
     scoped out -- measured by running `assess`, including with the registry entry DELETED
  5  `s_proj` on the cases Z's contract permits: rank-deficient, zero-baseline, support-changing
  6  power in BOTH directions, plus a false-positive control

No production compute, no adoption, no grading. Local numpy arithmetic only.
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
# state/ -> orchestration/ -> docs/ -> REPO ROOT. Three levels, not two: an earlier instrument in
# this campaign used two, landed on `docs/`, found 0 files and EXITED 0. So the root is ASSERTED.
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
assert os.path.isdir(f"{_REPO}/nd-unfolding"), (
    f"repo root resolved to {_REPO!r}, which has no nd-unfolding/. Refusing to run against a "
    f"tree that cannot contain the operands -- a wrong root here would import nothing and a "
    f"silent skip would read as a pass.")
for _p in (f"{_REPO}/nd-unfolding", f"{_REPO}/2d-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import z_contract as zc          # noqa: E402
import z_statistics as zs        # noqa: E402
import z_validator as zv         # noqa: E402
from uq_math import project_covariance   # noqa: E402

FAIL = []


def check(label, cond, detail=""):
    print(f"    [{'ok ' if cond else 'FAIL'}] {label}" + (f"  -- {detail}" if detail else ""))
    if not cond:
        FAIL.append(label)


def projector(C, rcond=1e-15):
    """Retained-subspace projector, the A-4 operand. Cutoff as applied, not as defaulted."""
    w, V = np.linalg.eigh(0.5 * (C + C.T))
    keep = w > rcond * max(w.max(), 0.0)
    Q = V[:, keep]
    return Q @ Q.T, int(keep.sum())


# ---------------------------------------------------------------------------- 1. the identity --
def section1():
    print("\n1. THE RELEASED ERROR BAR IS `sqrt(u' C u)` FOR `u` A ROW OF `M` -- exact identity")
    print("   `eavailW_covariance.py:442` projects, `:463` takes `np.diag`. `project_cov_nd.py:5-8`")
    print("   says M's rows are width-weighted SUMS over dropped-axis cells, so rows are dense.")
    rng = np.random.default_rng(20260910)
    n_src, n_dst = 40, 6
    A = rng.normal(size=(n_src, n_src))
    C = A @ A.T                                  # PSD, full rank
    # a width-weighted marginalization map: each destination bin sums a disjoint group of cells
    M = np.zeros((n_dst, n_src))
    groups = np.array_split(np.arange(n_src), n_dst)
    for r, g in enumerate(groups):
        M[r, g] = rng.uniform(0.5, 2.0, size=g.size)     # bin-width products, all nonzero
    nz = (M != 0).sum(axis=1)
    check("every row of M has more than one nonzero", bool(np.all(nz > 1)),
          f"nonzeros per row = {nz.tolist()}")

    C_low = project_covariance(C, M)
    lhs = np.diag(C_low)
    rhs = np.einsum("ij,jk,ik->i", M, C, M)      # exactly `s_proj`'s internal expression
    check("diag(M C M') == einsum used by s_proj", bool(np.allclose(lhs, rhs, rtol=1e-12)),
          f"max |diff| = {np.max(np.abs(lhs - rhs)):.3e}")

    # and it is NOT a function of diag(C) alone
    C_diagonly = np.diag(np.diag(C))
    lhs_d = np.diag(project_covariance(C_diagonly, M))
    rel = np.abs(lhs_d - lhs) / lhs
    check("the released bar CHANGES when off-diagonals are zeroed (so it reads them)",
          bool(rel.max() > 0.01),
          f"max relative change from dropping off-diagonals = {100*rel.max():.1f}%")
    print("    -> so `u' C u` with u = M[i] IS the released variance of destination bin i.")
    print("       `s_proj` does not approximate the release; it evaluates it.")


# --------------------------------------------------------------- 2. A-4 is inadequate, measured --
def section2():
    print("\n2. A-4 (`||P_0 - P_k||_2 <= 1e-8`) DOES NOT BOUND THE RELEASED ERROR BARS")
    print("   Construction: C_k = (1+a) C_0. Same eigenvectors, so the retained SUBSPACE and the")
    print("   retained RANK are identical -- A-4's gap is exactly 0 -- while every eigenvalue moves.")
    rng = np.random.default_rng(7)
    n_src, n_dst = 30, 4
    A = rng.normal(size=(n_src, n_src))
    C0 = A @ A.T
    M = np.zeros((n_dst, n_src))
    for r, g in enumerate(np.array_split(np.arange(n_src), n_dst)):
        M[r, g] = rng.uniform(0.5, 2.0, size=g.size)

    for a in (0.05, 0.2, 1.0):
        Ck = (1.0 + a) * C0
        P0, r0 = projector(C0)
        Pk, rk = projector(Ck)
        gap = float(np.linalg.norm(P0 - Pk, 2))
        out = zs.s_proj({0: C0, 1: Ck}, M, baseline_key=0)
        expected = np.sqrt(1.0 + a) - 1.0
        print(f"    a={a:<5} ||P_0-P_k||_2={gap:.3e}  rank {r0}->{rk}  "
              f"s_proj={out['s_proj']:.6f}  sqrt(1+a)-1={expected:.6f}")
        check(f"a={a}: A-4 gap passes 1e-8", gap <= 1e-8, f"gap={gap:.3e}")
        check(f"a={a}: retained rank unchanged", r0 == rk, f"{r0} vs {rk}")
        check(f"a={a}: released bars move by sqrt(1+a)-1",
              bool(abs(out["s_proj"] - expected) < 1e-9),
              f"s_proj={out['s_proj']:.9f}")
    print("    -> A-4 is SATISFIED EXACTLY (gap 0, rank identical) while the released error bars")
    print("       move by 41.4% at a=1. A-4 constrains WHICH directions are retained, not HOW BIG")
    print("       the uncertainty in them is. It is not a weak bound on the bars; it is silent.")


# ------------------------------------------------- 3. the diagonal legs are blind THROUGH M -----
def section3():
    print("\n3. `s_agg` AND `s_med` ARE BLIND TO WHAT THE PROJECTION READS -- SPEC 3.7d's pair,")
    print("   re-measured with the projection actually applied.")
    C0 = np.eye(2)
    Ck = np.array([[1.0, 0.9], [0.9, 1.0]])
    x_cv = np.array([1.0, 1.0])
    mask = np.array([True, True])
    agg = zs.s_agg({0: C0, 1: Ck}, baseline_key=0)
    med = zs.s_med({0: C0, 1: Ck}, x_cv, mask, baseline_key=0)
    check("s_agg is exactly 0 on an off-diagonal-only change", agg["s_agg"] == 0.0,
          f"s_agg={agg['s_agg']!r}")
    check("s_med is exactly 0 on an off-diagonal-only change", med["s_med"] == 0.0,
          f"s_med={med['s_med']!r}")

    # M = the width-weighted SUM over the dropped cell -- the actual marginalization shape
    M_sum = np.array([[1.0, 1.0]])
    proj = zs.s_proj({0: C0, 1: Ck}, M_sum, baseline_key=0)
    sig0 = np.sqrt(float(M_sum @ C0 @ M_sum.T))
    sigk = np.sqrt(float(M_sum @ Ck @ M_sum.T))
    print(f"    projected sigma: baseline {sig0:.6f} -> member {sigk:.6f}   "
          f"s_proj = {proj['s_proj']:.6f}  ({100*proj['s_proj']:.1f}%)")
    check("s_proj fires where both diagonal legs return exactly 0", proj["s_proj"] > 0.3,
          f"s_proj={proj['s_proj']:.6f}")
    print("    -> the +37.8% in SPEC 3.7d's table is the RELEASED bar of the marginal bin.")
    print("       Endpoint A publishes that bar. The two adopted legs score it 0.0.")


# ------------------------------------------- 4. task (2): the validator mechanics, run not read --
def section4():
    print("\n4. WHAT ACTUALLY HAPPENS TO CAUSE 3 IF `cause3_corr` IS SCOPED OUT -- by running it")
    AGG = zv.Leg("agg", "aggregate", "cause3_agg", "s_agg")
    MED = zv.Leg("med", "per-bin", "cause3_med", "s_med")
    L2 = zv.LegSet([AGG, MED], predeclared_at="PROBE")
    ok = zv.Validity(footing_ok=True, digests_agree=True, partition_agrees=True,
                     identities_pass=True, cv_held_fixed=True, offsets_match_K=True,
                     offset_declared_nonzero=True, product_digests_distinct=True,
                     all_members_finite=True)
    stats = {"s_agg": 1e-4, "s_med": 1e-4}

    print("\n  (a) NO production leg set exists in this tree -- measured separately; every")
    print("      `LegSet(...)` is in `tests/`. So `L` is whatever an adopter declares.")
    print("  (b) with the two diagonal boundaries DECLARED (probe-local), L = {agg, med}:")
    saved = dict(zc.Z_BOUNDARIES)
    try:
        zc.Z_BOUNDARIES["cause3_agg"] = zc.Boundary.declared("cause3_agg", 1e-3, "PROBE")
        zc.Z_BOUNDARIES["cause3_med"] = zc.Boundary.declared("cause3_med", 1e-3, "PROBE")
        out_with = zv.assess(L2, stats, ok)
        print(f"      branch={out_with.branch} ({out_with.branch_label})  "
              f"assessable={out_with.assessable}  is_met={out_with.is_met}")
        check("cause 3 reaches MET with cause3_corr STILL WITHHELD", out_with.is_met,
              "so cause3_corr is not what blocks MET")
        check("the diagonal-only scope statement is attached",
              out_with.scope_statement == zv._DIAGONAL_ONLY_SCOPE)
        check("cause3_corr never appears in the leg results",
              "cause3_corr" not in str(out_with.leg_results))

        print("\n  (c) now DELETE `cause3_corr` from the registry entirely and re-run:")
        del zc.Z_BOUNDARIES["cause3_corr"]
        out_without = zv.assess(L2, stats, ok)
        same = out_without.describe() == out_with.describe()
        check("the outcome is BYTE-IDENTICAL with the registry entry removed", same,
              "the registry site is INERT to `assess` while no leg names it")
        zc.Z_BOUNDARIES["cause3_corr"] = saved["cause3_corr"]

        print("\n  (d) and what the MET result in (b) actually disclaims:")
        txt = zv._DIAGONAL_ONLY_SCOPE
        for word in ("marginalization", "projection", "coverage validation"):
            check(f"the scope statement excludes {word!r}", word in txt)
        print("      -> so a MET under a diagonal-only leg set disclaims, in its own emitted text,")
        print("         EXACTLY the release endpoint A is for. Deferral does not need the boundary;")
        print("         it needs this sentence narrowed -- which is a contract change, not a scope")
        print("         change, and it is the site the registry line does not reach.")

        print("\n  (e) with a correlation-sensitive leg declared and `cause3_corr` withheld:")
        CORR = zv.Leg("corr", "aggregate", "cause3_corr", "s_proj", sees_correlations=True)
        L3 = zv.LegSet([AGG, MED, CORR], predeclared_at="PROBE")
        out3 = zv.assess(L3, dict(stats, s_proj=1e-4), ok)
        print(f"      assessable={out3.assessable}  branch={out3.branch}  "
              f"reject={out3.reject_conditions}  failing={out3.failing_legs}")
        check("adopting the leg makes the withheld boundary BIND", out3.assessable is False)
        check("reject condition 4c is raised", out3.reject_conditions == ("4c",))
        check("the scope statement is withdrawn once a corr leg exists",
              out3.scope_statement is None)
    finally:
        zc.Z_BOUNDARIES.clear()
        zc.Z_BOUNDARIES.update(saved)
    check("registry restored to 4 boundaries", len(zc.Z_BOUNDARIES) == 4,
          f"{sorted(zc.Z_BOUNDARIES)}")


# ------------------------------------- 5. s_proj on the cases Z's contract permits --------------
def section5():
    print("\n5. `s_proj` ON THE CASES THE CONTRACT PERMITS -- singular, zero-baseline, support change")
    rng = np.random.default_rng(11)

    print("\n  (a) RANK-DEFICIENT C (Z's own case: rank <= 265 of 10,694). No inversion, so no rcond.")
    B = rng.normal(size=(12, 3))
    C0 = B @ B.T                                  # rank 3 of 12
    Ck = 1.1 * C0
    M = np.zeros((2, 12))
    M[0, :6] = rng.uniform(0.5, 2, 6)
    M[1, 6:] = rng.uniform(0.5, 2, 6)
    r = int(np.linalg.matrix_rank(C0))
    out = zs.s_proj({0: C0, 1: Ck}, M, baseline_key=0)
    check(f"s_proj evaluates on a rank-{r}-of-12 operand", out["s_proj"] > 0,
          f"s_proj={out['s_proj']:.6f}, expected {np.sqrt(1.1)-1:.6f}")
    check("and it equals sqrt(1.1)-1 exactly", abs(out["s_proj"] - (np.sqrt(1.1) - 1)) < 1e-12)
    print("      -> singularity is IRRELEVANT to s_proj: `u' C u` needs no inverse and no")
    print("         positive-definite baseline. That is why it survives where a rho-style bound")
    print("         does not, and it is the same reason round 2's outcome (2) preferred direct checks.")

    print("\n  (b) ZERO BASELINE SIGMA on a declared functional -- `eavailW_covariance.py:429-431`")
    print("      warns these bins are 'NOT measured-and-precise; they are unsupported'.")
    M_bad = np.zeros((2, 12))
    M_bad[0, :6] = 1.0
    # row 1 all zeros: an (Eavail,W) cell that NO reported 5D bin reaches
    empty_rows = np.nonzero(~M_bad.any(axis=1))[0]
    check("the empty row is exactly what `ew_coverage_report` already returns",
          empty_rows.tolist() == [1], f"empty rows = {empty_rows.tolist()}")
    try:
        zs.s_proj({0: C0, 1: Ck}, M_bad, baseline_key=0)
        check("s_proj ABORTS on a zero-baseline functional", False, "it returned instead")
    except Exception as exc:                                  # noqa: BLE001
        check("s_proj ABORTS on a zero-baseline functional", "zero baseline" in str(exc),
              f"{type(exc).__name__}: {exc}")
    print("      -> ABORT, not a silent 0/0 and not a pass. So the functional set MUST be declared")
    print("         over the SUPPORTED destination bins, and the predicate for that already exists")
    print("         (`eavailW_covariance.ew_coverage_report`). An abort on a bin declared SUPPORTED")
    print("         is a construction defect, not a tolerance question.")

    print("\n  (c) SUPPORT CHANGE across members -- ⚠ and this is a RESIDUE, not a covered case.")
    print("      `U` is predeclared and FIXED, so if member k's destination support differs from")
    print("      the baseline's, `s_proj` measures the movement of the BASELINE's functionals and")
    print("      is SILENT about the appearance or loss of a destination bin.")
    M_k = M.copy()
    M_k[1, :] = 0.0                     # member k loses destination bin 1 entirely
    e0 = np.nonzero(~M.any(axis=1))[0].size
    ek = np.nonzero(~M_k.any(axis=1))[0].size
    check("the support DID change between baseline and member", e0 != ek, f"{e0} -> {ek}")
    out_fixed = zs.s_proj({0: C0, 1: Ck}, M, baseline_key=0)
    print(f"      s_proj with the fixed declared U = {out_fixed['s_proj']:.6f}  "
          f"(unchanged; it never sees M_k)")
    print("      -> so support IDENTITY across members is a PRECONDITION, in `Validity`'s style,")
    print("         NOT something a tolerance absorbs. It belongs with the branch-1/2 falsifiers.")


# ---------------------------------------------------- 6. power in both directions + control -----
def section6():
    print("\n6. POWER IN BOTH DIRECTIONS, AND A FALSE-POSITIVE CONTROL")
    rng = np.random.default_rng(3)
    A = rng.normal(size=(20, 20))
    C0 = A @ A.T
    M = np.zeros((3, 20))
    for r, g in enumerate(np.array_split(np.arange(20), 3)):
        M[r, g] = rng.uniform(0.5, 2, g.size)

    out_same = zs.s_proj({0: C0, 1: C0.copy()}, M, baseline_key=0)
    check("CONTROL: identical members give exactly 0.0", out_same["s_proj"] == 0.0,
          f"s_proj={out_same['s_proj']!r}")

    # direction 1: bars get BIGGER
    out_up = zs.s_proj({0: C0, 1: 1.3 * C0}, M, baseline_key=0)
    # direction 2: bars get SMALLER -- a filter must act here too
    out_dn = zs.s_proj({0: C0, 1: 0.7 * C0}, M, baseline_key=0)
    check("fires when released bars INFLATE", out_up["s_proj"] > 0.1,
          f"{out_up['s_proj']:.6f} = sqrt(1.3)-1 = {np.sqrt(1.3)-1:.6f}")
    check("fires when released bars SHRINK", out_dn["s_proj"] > 0.1,
          f"{out_dn['s_proj']:.6f} = 1-sqrt(0.7) = {1-np.sqrt(0.7):.6f}")

    # off-diagonal only, at scale, with the all-ones functional SPEC 3.7d names
    d = np.sqrt(np.diag(C0))
    R = C0 / np.outer(d, d)
    Ck = (0.5 * (R + np.eye(20))) * np.outer(d, d)   # halve every correlation, keep the diagonal
    check("the off-diagonal-only member has an IDENTICAL diagonal",
          bool(np.allclose(np.diag(Ck), np.diag(C0), rtol=1e-12)),
          f"max rel diag diff = {np.max(np.abs(np.diag(Ck)-np.diag(C0))/np.diag(C0)):.2e}")
    agg = zs.s_agg({0: C0, 1: Ck}, baseline_key=0)
    U = np.vstack([M, np.ones((1, 20))])
    out_off = zs.s_proj({0: C0, 1: Ck}, U, baseline_key=0)
    print(f"    s_agg on the off-diagonal-only member = {agg['s_agg']:.3e}")
    print(f"    s_proj on the same pair (M rows + all-ones) = {out_off['s_proj']:.6f} "
          f"(worst functional index {out_off['argmax_functional']})")
    check("s_agg is ~0 on a correlation-only change", agg["s_agg"] < 1e-12)
    check("s_proj is NOT", out_off["s_proj"] > 1e-3)


if __name__ == "__main__":
    print(__doc__)
    print("=" * 78)
    section1(); section2(); section3(); section4(); section5(); section6()
    print("\n" + "=" * 78)
    if FAIL:
        print(f"PROBE FAILED: {len(FAIL)} check(s): {FAIL}")
        raise SystemExit(1)
    print("PROBE GREEN -- every check above passed. No compute, no adoption, no grading.")
