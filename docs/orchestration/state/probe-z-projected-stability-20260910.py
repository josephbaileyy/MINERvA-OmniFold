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

REV. 2 -- ROUND-1 REVIEW. Every one of these FALSIFIES something this probe or its packet asserted:
  7  F1  `B` is the noise floor of the WRONG POPULATION, and the direction REVERSES with sharing
  8  F3  the abort claim holds at EXACT zero and FAILS at round-off; the declared predicate is not
         the predicate the code tests
  9  F4  section 5(c) tested an M-change; a COVARIANCE support loss is NOT silent, it saturates
 10  F6  A-4's `1e-8` is not tuned -- the statistic is ~binary, so 9 orders behave identically
 11      the two POSITIVE CONTROLS section 4 lacked, without which byte-identity is not evidence
 12  F7  the sample-covariance population is THREE, not two, and one of them is BIASED 1/N
 13      the sample blocks CANCEL when reused -- the arm is closed to the top-level (shared)
         one, so this is the branch Z is in. ⚠ REV. 4 CORRECTS ITS CONCLUSION: see 14
 14  F21 `B' = 0` is not exact -- but the CITED mechanism (pairwise vs sequential) does NOT
         fire at 45 legs. ORDER is the real one. The precondition is FIXED SUMMATION ORDER
 15  F24 is `s_proj` unfalsifiable under reuse? NO -- the bands are member-scoped (`mr_run`), so
         the variation has support OUTSIDE the reused blocks. F22's half stands; the composition
         does not

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




# ============================ REV. 2 -- ROUND-1 REVIEW FINDINGS ============================
# Added after independent review at 05bf8647. Sections 7-12 verify findings F1, F3, F4, F6, F7 and
# adopt the two positive controls the assessor supplied for section 4. ⚠ EVERY ONE OF THESE
# FALSIFIES SOMETHING THIS PROBE OR ITS PACKET PREVIOUSLY ASSERTED.


def section7():
    """F1: B is the noise floor of the WRONG POPULATION, and the direction depends on sharing."""
    print("\n7. F1 -- `B` IS COMPUTED ON THE WRONG POPULATION  (CONFIRMED; packet claim withdrawn)")
    print("   `B = 1/sqrt(2(N-1))` is the noise floor of a SINGLE bar, single-sample.")
    print("   `s_proj` is a MAXIMUM over K x functionals of a TWO-SAMPLE difference.")

    def null_sproj(N, K, nbins, share=0.0, seed=0):
        """Members statistically IDENTICAL (true C = I). Only finite-ensemble noise differs."""
        rng = np.random.default_rng(seed)
        n_shared = int(round(share * N))

        def cov_from(X):
            Z = X - X.mean(0)
            return (Z.T @ Z) / (X.shape[0] - 1)

        X0 = rng.normal(size=(N, nbins))
        shared = X0[:n_shared]
        covs = {0: cov_from(X0)}
        for k in range(1, K + 1):
            fresh = rng.normal(size=(N - n_shared, nbins))
            covs[k] = cov_from(np.vstack([shared, fresh]) if n_shared else fresh)
        return zs.s_proj(covs, np.eye(nbins), baseline_key=0)["s_proj"]

    N = 100
    B = 1.0 / np.sqrt(2 * (N - 1))
    print(f"    B at N={N} = {100*B:.3f}%")
    med = float(np.median([null_sproj(N, 10, 100, 0.0, seed=s) for s in range(9)]))
    print(f"    (a) K=10, 100 functionals, independent draws: null s_proj median = "
          f"{100*med:.2f}%  -> ratio {med/B:.2f}")
    check("a NULL object exceeds B by several-fold", med / B > 3.0,
          f"ratio {med/B:.2f} -- so `B <= S` can PASS while A-7 reports NOT MET on a null")
    med1 = float(np.median([null_sproj(N, 1, 1, 0.0, seed=100 + s) for s in range(400)]))
    print(f"    (b) CONTROL K=1, ONE functional -- s_proj's population collapses to B's: "
          f"{100*med1:.2f}%  -> ratio {med1/B:.2f}")
    check("at K=1 with one functional the ratio is ~1, so B's FORMULA is right",
          0.8 < med1 / B < 1.2, f"ratio {med1/B:.2f} -- a POPULATION mismatch, not a formula error")

    print("    (c) ⚠ AND THE DIRECTION REVERSES WITH REPLICA-DRAW SHARING:")
    ratios = {}
    for share in (0.0, 0.5, 0.9, 0.99):
        m = float(np.median([null_sproj(N, 10, 100, share, seed=200 + s) for s in range(7)]))
        ratios[share] = m / B
        print(f"        share={share:<5} null s_proj median = {100*m:6.2f}%  ratio {m/B:.2f}")
    check("B is ANTI-conservative at independent draws", ratios[0.0] > 3.0)
    check("B becomes CONSERVATIVE as sharing -> 1", ratios[0.99] < 1.0,
          f"{ratios[0.99]:.2f} -- adequacy cannot be settled without the SHARING DECLARATION")
    check("and the ratio is monotone in sharing",
          all(ratios[a] > ratios[b] for a, b in ((0.0, 0.5), (0.5, 0.9), (0.9, 0.99))))


def section8():
    """F3: the abort claim holds at EXACT zero and FAILS at round-off."""
    print("\n8. F3 -- ABORT BEHAVIOUR ON A NEAR-NULL FUNCTIONAL  (packet claim FALSE at round-off)")
    print("   Section 5(b) used an EMPTY M row (exact zero) on a benign rank-3-of-12 operand.")
    print("   Z's case is 265 of 10,694, where a declared functional can be ~orthogonal to range(C).")
    rng = np.random.default_rng(4)
    msgs, noabort, bases = {}, 0, []
    for _ in range(500):
        n, r = 40, 4
        Bm = rng.normal(size=(n, r))
        C0 = Bm @ Bm.T
        _w, V = np.linalg.eigh(C0)
        u = V[:, 0]                                  # numerically-null eigenvector
        U = np.vstack([u, u])
        try:
            zs.s_proj({0: C0, 1: 1.1 * C0}, U, baseline_key=0)
            noabort += 1
            bases.append(float(u @ C0 @ u))
        except Exception as exc:                     # noqa: BLE001
            k = str(exc).split(":")[-1].strip()[:52]
            msgs[k] = msgs.get(k, 0) + 1
    print(f"    of 500 trials: {noabort} did NOT abort. Aborts by message:")
    for k, v in sorted(msgs.items(), key=lambda kv: -kv[1]):
        print(f"        {v:4d}  {k!r}")
    check("a near-null functional does NOT reliably abort", noabort > 0,
          f"{noabort}/500 pass `base > 0` on a ROUND-OFF positive and divide by it")
    check("the dominant abort BLAMES THE OPERAND, not the declaration",
          any("not PSD" in k for k in msgs),
          "'C is not PSD on these u' -- but C IS PSD; the FUNCTIONAL is the problem")
    check("the message section 4.3 advertised is the RARE one",
          sum(v for k, v in msgs.items() if "zero baseline" in k) < noabort)
    if bases:
        a = np.array(bases)
        print(f"    non-aborting baseline u'Cu in [{a.min():.3e}, {a.max():.3e}] -- round-off")
    print("    -> 'ABORT, not a silent 0/0 and not a pass' is true ONLY at EXACT zero.")
    print("       And the DECLARED predicate (`ew_coverage_report`, empty M rows) is NOT the")
    print("       predicate the code tests (`m_i' C m_i > 0`). At 265 of 10,694 these differ.")


def section9():
    """F4: the support residue conflated two mechanisms; only one was verified."""
    print("\n9. F4 -- SUPPORT CHANGE HAS TWO MECHANISMS AND SECTION 5(c) TESTED ONE")
    print("   5(c) changed the member's PROJECTION MATRIX with C untouched -> correctly silent.")
    print("   The prose generalised to 'a destination bin appearing or vanishing'. Measured:")
    rng = np.random.default_rng(9)
    n = 12
    Bm = rng.normal(size=(n, 6))
    C0 = Bm @ Bm.T
    M = np.zeros((2, n)); M[0, :6] = 1.0; M[1, 6:] = 1.0
    Ck = C0.copy()
    Ck[6:, :] = 0.0; Ck[:, 6:] = 0.0          # member's COVARIANCE loses that bin's support
    out = zs.s_proj({0: C0, 1: Ck}, M, baseline_key=0)
    print(f"    member's C zeroed on destination bin 1's source cells: "
          f"s_proj = {out['s_proj']:.6f}, argmax_functional = {out['argmax_functional']}")
    check("a COVARIANCE support loss is NOT silent -- it saturates", out["s_proj"] > 0.99,
          "so only the M-CHANGE direction is a genuine blind spot")
    check("and it names the responsible functional", out["argmax_functional"] == 1)


def section10():
    """F6: A-4's tolerance is not load-bearing -- the statistic is essentially binary."""
    print("\n10. F6 -- IS A-4's `1e-8` A TUNED NUMBER?  (no: any separator behaves identically)")
    rng = np.random.default_rng(11)
    n = 30
    A = rng.normal(size=(n, n))
    C = A @ A.T
    w, V = np.linalg.eigh(C)
    P0, r0 = projector(C)
    Pm, rm = projector(2.5 * C)                                    # structural match
    Cdrop = V[:, 1:] @ np.diag(w[1:]) @ V[:, 1:].T                 # one retained mode removed
    Pd, rd = projector(Cdrop)
    g_match = float(np.linalg.norm(P0 - Pm, 2))
    g_drop = float(np.linalg.norm(P0 - Pd, 2))
    print(f"    structural MATCH (rescale): rank {r0}->{rm}  gap = {g_match:.3e}")
    print(f"    RANK CHANGE (drop a mode):  rank {r0}->{rd}  gap = {g_drop:.6f}")
    check("a structural match sits at round-off", g_match < 1e-12)
    check("a rank change gives EXACTLY 1 for orthogonal projectors", abs(g_drop - 1.0) < 1e-12)
    same = all((g_match <= tol) and (g_drop > tol) for tol in (1e-12, 1e-10, 1e-8, 1e-5, 1e-3))
    check("every tolerance in [1e-12, 1e-3] separates them IDENTICALLY", same,
          "so `1e-8` is a ROBUSTNESS property, not a fitted number -- 9 orders behave alike")


def section11():
    """The two positive controls the assessor supplied for section 4. Adopted, not paraphrased."""
    print("\n11. POSITIVE CONTROLS FOR SECTION 4 -- without these, byte-identity is not evidence")
    print("    A byte-identical `describe()` with no positive control is exactly the shape of a")
    print("    check that CANNOT FAIL. Both controls are the assessor's, adopted here.")
    AGG = zv.Leg("agg", "aggregate", "cause3_agg", "s_agg")
    MED = zv.Leg("med", "per-bin", "cause3_med", "s_med")
    L2 = zv.LegSet([AGG, MED], predeclared_at="PROBE")
    ok = zv.Validity(footing_ok=True, digests_agree=True, partition_agrees=True,
                     identities_pass=True, cv_held_fixed=True, offsets_match_K=True,
                     offset_declared_nonzero=True, product_digests_distinct=True,
                     all_members_finite=True)
    stats = {"s_agg": 1e-4, "s_med": 1e-4}
    saved = dict(zc.Z_BOUNDARIES)
    try:
        zc.Z_BOUNDARIES["cause3_agg"] = zc.Boundary.declared("cause3_agg", 1e-3, "PROBE")
        zc.Z_BOUNDARIES["cause3_med"] = zc.Boundary.declared("cause3_med", 1e-3, "PROBE")
        print("    CONTROL A: delete a DECLARED leg's own boundary -- is the registry consulted?")
        del zc.Z_BOUNDARIES["cause3_agg"]
        raised = None
        try:
            zv.assess(L2, stats, ok)
        except Exception as exc:                     # noqa: BLE001
            raised = type(exc).__name__
        check("deleting a declared leg's boundary RAISES", raised == "ZContractError",
              f"got {raised} -- so section 4(c)'s byte-identity is a REAL negative, not a blind one")
        zc.Z_BOUNDARIES["cause3_agg"] = zc.Boundary.declared("cause3_agg", 1e-3, "PROBE")

        print("    CONTROL B: does the scope statement FLIP when a corr leg is declared?")
        out2 = zv.assess(L2, stats, ok)
        CORR = zv.Leg("corr", "aggregate", "cause3_corr", "s_corr", sees_correlations=True)
        out3 = zv.assess(zv.LegSet([AGG, MED, CORR], predeclared_at="PROBE"),
                         dict(stats, s_corr=1e-3), ok)
        check("present without a corr leg", out2.scope_statement == zv._DIAGONAL_ONLY_SCOPE)
        check("None with one", out3.scope_statement is None,
              "so the narrowing is LEG-DERIVED, not incidental")
    finally:
        zc.Z_BOUNDARIES.clear()
        zc.Z_BOUNDARIES.update(saved)
    check("registry restored", len(zc.Z_BOUNDARIES) == 4)


def section12():
    """F7: the sample-covariance population is THREE, and one of them is biased 1/N."""
    print("\n12. F7 -- THE SAMPLE-COVARIANCE POPULATION IS THREE, NOT TWO  (packet claim FALSE)")
    print("   `z_assembly.py:4`'s `sum_V C_b` is ITSELF A SUM, and a third sample covariance")
    print("   sits one level inside it. Reading the formula's SURFACE answered a narrower question")
    print("   than the one asked. A derivation is not safer than an enumeration unless it RECURSES.")
    import adopt_unified_5d as au                    # noqa: PLC0415
    from uq_math import mat_covariance               # noqa: PLC0415
    vb = list(au.VERT_BANDS)
    print(f"    adopt_unified_5d.VERT_BANDS ({len(vb)} entries); last = {vb[-1]!r}")
    check("Flux is a VERTICAL band, hence a summand of sum_V", "Flux" in vb)
    check("and there are 13 of them", len(vb) == 13, f"{len(vb)}")
    check("z_contract re-exports the same tuple", tuple(zc.VERT_BANDS) == tuple(vb))

    rng = np.random.default_rng(5)
    N, nb = 40, 6
    X = rng.normal(size=(N, nb))
    got = mat_covariance(X)
    Zc = X - X.mean(0)
    biased = (Zc.T @ Zc) / N
    unbiased = (Zc.T @ Zc) / (N - 1)
    check("mat_covariance is BIASED 1/N -- measured, not read off its docstring",
          bool(np.allclose(got, biased)), "matches Z'Z/N exactly")
    check("and it is NOT unbiased 1/(N-1)", not bool(np.allclose(got, unbiased)),
          f"ratio {float(got[0,0]/unbiased[0,0]):.6f} = (N-1)/N")
    print("    -> `unified_throw_cov.py:467` builds `C_flux = mat_covariance(...)` over the flux")
    print("       universes; `:468` does `C_block += C_flux`; `:470` PRINTS 'MAT mean-centered")
    print("       1/N'. So the packet's 'one script, one convention -- unbiased 1/(N-1)' was FALSE")
    print("       of part of Z's own sum, INSIDE A DISCLOSURE REQUIREMENT.")
    print("    -> `:460` applies the SAME function to each of the 12 knob bands over 2 declared")
    print("       +/- endpoints. Same biased normalizer -- but a 2-point endpoint pair is NOT a")
    print("       random ensemble, so it is a construction to DISCLOSE, not an ensemble size.")


def section13():
    """REV. 3 / F-provenance: B' = 0 EXACTLY when the sample blocks are reused byte-identically."""
    print("\n13. `B'` COLLAPSES TO EXACTLY ZERO IN THE REUSE BRANCH  (the arm is closed: top-level)")
    print("   `s_proj` is a function of `C_k - C_0`. Byte-identical blocks CANCEL in that")
    print("   difference, so their finite-ensemble noise is COMMON-MODE, not merely small.")
    rng = np.random.default_rng(20260911)
    n_src, n_dst, N, K = 60, 8, 40, 10

    def sample_block(seed):
        r = np.random.default_rng(seed)
        X = r.normal(size=(N, n_src))
        Z = X - X.mean(0)
        return (Z.T @ Z) / (N - 1)

    A = rng.normal(size=(n_src, n_src))
    C_det = A @ A.T                       # the deterministic bands: identical across members
    M = np.zeros((n_dst, n_src))
    for r_, g in enumerate(np.array_split(np.arange(n_src), n_dst)):
        M[r_, g] = rng.uniform(0.5, 2.0, size=g.size)

    # --- REUSE: one shared sample block, byte-identical in every member
    shared = sample_block(7)
    reuse = {k: C_det + shared for k in range(K + 1)}
    out_reuse = zs.s_proj(reuse, M, baseline_key=0)
    check("REUSE: null s_proj is EXACTLY 0.0", out_reuse["s_proj"] == 0.0,
          f"s_proj={out_reuse['s_proj']!r} -- so B' = 0 and the feasibility check passes for any "
          f"positive delta_proj")
    check("and it is exact, not merely small", abs(out_reuse["s_proj"]) < 1e-300)

    # --- REGENERATE: each member draws its own sample block
    regen = {k: C_det + sample_block(100 + k) for k in range(K + 1)}
    out_regen = zs.s_proj(regen, M, baseline_key=0)
    print(f"    REGENERATE: null s_proj = {100*out_regen['s_proj']:.3f}%  "
          f"(argmax offset {out_regen['argmax_offset']}, functional {out_regen['argmax_functional']})")
    check("REGENERATE: the null spread is NOT zero", out_regen["s_proj"] > 0.0,
          "the same object, graded against a different reuse decision, gives a different floor")
    check("so the two branches differ by construction, not by degree",
          out_regen["s_proj"] > out_reuse["s_proj"])

    # --- the common-mode property stated as an identity, not an outcome
    d_reuse = reuse[1] - reuse[0]
    check("REUSE: C_k - C_0 is identically zero", bool(np.all(d_reuse == 0.0)),
          "byte-identical blocks cancel; this is the mechanism, measured")
    print("    -> ⚠ AND THE SIGN IS COUNTERINTUITIVE: reuse makes A-7 ENFORCEABLE by removing the")
    print("       noise that would mask a violation. It does NOT make the object more stable, and")
    print("       it removes the only route by which ensemble-driven instability could be DETECTED.")
    print("       A criterion becoming enforceable is a fact about the CRITERION, not the object.")


def section14():
    """F21: the route mechanism does NOT fire at band-assembly scale. ORDER is what matters."""
    print("\n14. F21 -- `B' = 0` IS NOT EXACT, BUT THE CITED MECHANISM DOES NOT FIRE HERE")
    print("   Section 13 summed ONE shared array onto ONE deterministic array, so both members used")
    print("   the SAME route. It verified the ALGEBRA, not the world. Measured properly:")
    rng = np.random.default_rng(1)
    legs = [rng.normal(size=(40, 40)) for _ in range(45)]

    a = np.sum(np.stack(legs), axis=0)          # numpy reduction
    b = np.zeros_like(legs[0])
    for L in legs:                              # sequential accumulation, SAME order
        b = b + L
    check("SAME order, pairwise vs sequential, 45 legs: BIT-IDENTICAL",
          bool(np.array_equal(a, b)),
          "numpy's pairwise blocksize is 128, so at 45 terms BOTH routes are sequential -- "
          "so `mii_anchor_comparator:241-246`'s cited mechanism does NOT fire at this scale")

    c = np.zeros_like(legs[0])
    for i in reversed(range(45)):               # DIFFERENT order
        c = c + legs[i]
    diff = float(np.max(np.abs(b - c)))
    rel = diff / float(np.max(np.abs(b)))
    check("DIFFERENT order: NOT bit-identical", not bool(np.array_equal(b, c)),
          f"max |diff| = {diff:.3e}, relative {rel:.1e} -- ORDER is the real mechanism")

    x = rng.normal(size=10694) ** 2             # the docstring's own case: a long reduction
    check("and a >128-element REDUCTION does differ by route",
          np.sum(x) != sum(x),
          f"relative {abs(np.sum(x)-sum(x))/np.sum(x):.1e} over 10,694 entries -- this is the "
          f"docstring's case (a TRACE), a different operation from band assembly")

    M = np.zeros((8, 40))
    for r_, g in enumerate(np.array_split(np.arange(40), 8)):
        M[r_, g] = rng.uniform(0.5, 2.0, size=g.size)
    Ca, Cc = a @ a.T, c @ c.T
    out = zs.s_proj({0: Ca, 1: Cc}, M, baseline_key=0)
    print(f"    s_proj between order-variant assemblies = {out['s_proj']:.3e}")
    check("so the reuse-branch floor is NONZERO but tiny", 0.0 < out["s_proj"] < 1e-10,
          f"{out['s_proj']:.3e}")
    print("    -> CORRECTED CONCLUSION: `B'` is nonzero, so `q` is moot under reuse because B' is")
    print("       NEGLIGIBLE and not because it is ZERO. ⚠ AND THE PRECONDITION IS NARROWER THAN")
    print("       F21 STATED: not 'bit-reproducibility' in general, but FIXED SUMMATION ORDER over")
    print("       the band legs. At fixed order and 45 legs, assembly IS bit-reproducible.")
    print("    ⚠ NOT ESTABLISHED: any of this on Z's real band assembly. Toy scale only.")


def section15():
    """F24: does the member variation have support OUTSIDE the reused blocks? Measured."""
    print("\n15. F24 -- IS `s_proj` UNFALSIFIABLE ON THE REUSE BRANCH?  (no -- and this decides it)")
    print("   `sbatch_finalize_5d_bkgaware_gpu.sh:456` runs COMB -- the systematic-universe combine,")
    print("   i.e. THE BANDS -- through `mr_run`, the MEMBER-SCOPED runner. So the bands are")
    print("   REGENERATED PER MEMBER while :8-10 reuses C_stat/C_ML as '#13-invariant'.")
    rng = np.random.default_rng(99)
    n_src, n_dst, N, K = 60, 8, 40, 6

    def sample_block(seed):
        r = np.random.default_rng(seed)
        X = r.normal(size=(N, n_src))
        Z = X - X.mean(0)
        return (Z.T @ Z) / (N - 1)

    shared = sample_block(7)                     # REUSED: identical bytes in every member
    A = rng.normal(size=(n_src, n_src))
    bands0 = A @ A.T
    M = np.zeros((n_dst, n_src))
    for r_, g in enumerate(np.array_split(np.arange(n_src), n_dst)):
        M[r_, g] = rng.uniform(0.5, 2.0, size=g.size)

    # THE NULL: bands identical too -> floor
    null = {k: bands0 + shared for k in range(K + 1)}
    out_null = zs.s_proj(null, M, baseline_key=0)
    check("NULL (bands identical, blocks reused): s_proj ~ 0 -- this is B'",
          out_null["s_proj"] == 0.0, f"{out_null['s_proj']!r}")

    # REAL MEMBERS: blocks reused byte-identically, BANDS regenerated per member
    real = {0: bands0 + shared}
    for k in range(1, K + 1):
        pert = 1.0 + 0.03 * k
        real[k] = (bands0 * pert) + shared       # member-scoped COMB moves; block does not
    out_real = zs.s_proj(real, M, baseline_key=0)
    print(f"    REAL (blocks reused, bands per-member): s_proj = {100*out_real['s_proj']:.3f}%")
    check("⚠ s_proj is NOT identically zero when the bands move", out_real["s_proj"] > 0.01,
          "so the statistic RETAINS SUPPORT through the member-scoped band sum")
    check("and it names the responsible offset", out_real["argmax_offset"] == K)
    print("    -> SO F24's FIRST HALF IS REFUTED: the variation `s_proj` exists to detect has")
    print("       support OUTSIDE the reused blocks, in member-scoped COMB. An exact 0.0 arises")
    print("       ONLY under the null, which is what a null FLOOR is supposed to be.")
    print("    -> ⚠ BUT F24's SECOND HALF (F22) STANDS INDEPENDENTLY: a ~0 floor still makes the")
    print("       `B' < delta_proj` PRECONDITION contentless, so it must report NOT APPLICABLE.")
    print("       One of the two halves survives; the COMPOSITION does not.")


if __name__ == "__main__":
    print(__doc__)
    print("=" * 78)
    section1(); section2(); section3(); section4(); section5(); section6()
    section7(); section8(); section9(); section10(); section11(); section12()
    section13(); section14(); section15()
    print("\n" + "=" * 78)
    if FAIL:
        print(f"PROBE FAILED: {len(FAIL)} check(s): {FAIL}")
        raise SystemExit(1)
    print("PROBE GREEN -- every check above passed. No compute, no adoption, no grading.")
