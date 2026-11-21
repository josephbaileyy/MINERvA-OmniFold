# REGRADE amendment 1, rev 1: A0(b)'s tolerance at COV2D A5's rule (tier3-design, 2026-11-21, at the director's call)

**Adopted after a STOP.** The rule was chosen after cov2d's 2D run stopped at G18's A0(b). This amendment says so
plainly. It loosens a numerical-identity tolerance only, and it changes no reading rule, no statistic and no
criterion.

## What happened

- **The STOP.** cov2d's 2D run (`run2d` at driver 058bca19, 2026-11-21T11:00:38–11:04:45Z) is committed at
  `752c3f6073621af93dba3f0ae95c6a8e6696226c` on `lane/regrade-2d-20261121`, as `run2d/regrade_2d.json` (sha256
  `98fa09b4…`), exit 1.
  - **G18** stopped at A0(b): chi2_mean_over_ndf differs from the committed COV2D grade by **1.73e-8 relative**,
    against the declared flat 1e-9.
  - Every other A0 part was equal: ndf, joint_count, counts, k_joint and the flags.
- **cov2d's diagnosis.**
  - G18's C_T is full rank with κ₂ ≈ 9.5e11. A laptop-against-cluster LAPACK difference near 1e-8 is expected at
    that conditioning.
  - T2A met the same gap on the same E and C_T: its A1 χ² relative difference was 6.8e-9 at G18 and 2.0e-9 at AR23
    (`t2a_G18.json`).
- **The director's call (2026-11-21, under Joseph's standing go):** "amend A0(b) in both the 2D and the 16-cell paths to
  COV2D A5's rule, max(1e-9, 10 κ₂ ε). It's the same remedy T2-BINDING-1 addendum 1 adopted for T2A … It's a
  numerical-identity tolerance, not a test criterion, so no reading rule changes."

## The change

- **A0(b) (section 6):** chi2_mean_over_ndf must equal the committed grade's within
  **tol = max(1e-9, 10 · κ₂(C) · ε)**, relative. Here:
  - ε is float64's machine epsilon;
  - C is the matrix A0 grades (C_T, with C_add = 0);
  - κ₂ = λ_max / λ_min over C's non-null subspace, that is, eigenvalues above `fd_1b_null.RANK_REL` (1e-12) of the
    largest, the χ²'s own subspace.
- **On the non-null subspace (rev 1, after Grok's read; Grok M1 corrected a false claim of rev 0):**
  - For a C whose every eigenvalue is above the cut, this κ₂ equals A5's full-spectrum κ₂ exactly. That is G18:
    λ_min/λ_max = 1.05e-12 (`T2-BINDING-1.md:58`), so tol ≈ 2.11e-3.
  - At 2D AR23, λ_min/λ_max = 9.99e-13 is positive. A5's raw rule is therefore finite there (tol ≈ 2.22e-3) and not
    vacuous, which corrects rev 0. That eigenvalue falls under the 1e-12 cut, so the χ² (ndf 204) and this κ₂ both
    exclude it. The subspace tolerance is then the stricter of the two.
  - In general the subspace rule is never looser than T2A's full-spectrum rule. It is equal when nothing falls under
    the cut, stricter when a positive eigenvalue does, and finite where A5's raw rule is infinite (λ_min ≤ 0).
  - So this is a stricter variant of the rule the director named (T2A computes κ₂ on the full spectrum,
    `t2a_split.py:72-78`), chosen because it is the conditioning of the matrix the χ² actually inverts.
  - A C with no positive eigenvalue is a STOP.
- **Unchanged:** A0(a) (ndf, joint_count and counts, all exact) and A0(c) ("null redraw differs" is not a STOP).
- **The record** prints `b_tol` and `b_rule` (κ₂ and the rule) beside `b_rel`.
- **Also:** `run2d --tunes` (default both). cov2d asked for it, so the G18 rerun writes a G18-only record and AR23 is
  neither recomputed nor recorded twice.

## What stands, and what reruns

- **2D AR23:** its record in 752c3f60 stands. It was committed before this amendment, and its A0 passed at the flat
  1e-9 (b 3.4e-10).
- **The sixteen cells:** the record at `a923a02e` (`run16/capture/regrade16.json`, df590558…) stands. It was run at
  driver 5073bb7a before this amendment, and A0(b) passed at the flat 1e-9 at all four evaluations, so the looser rule
  could not change it.
- **2D G18 reruns** locally (cov2d), at the amended driver, with `--tunes G18`.

## Code and tests

- **Code:** `regrade_crep.py`: `a0_chi2_tol` and `a0_compare(..., tol)`; `run2d(q205, tunes)` and the `--tunes` flag.
- **Tests (54 OK):**
  - the G18 case (κ₂ 9.5e11) passes a 1.73e-8 difference;
  - a difference of 1.1 × tol stops;
  - κ₂ = 1 gives the 1e-9 floor;
  - a rank-deficient C gives a finite κ₂;
  - a numerical null below zero beside a kept eigenvalue at 1e-11 gives κ₂ 1e11, not the full-spectrum ratio (rev 1,
    Grok M2);
  - an AR23-like spectrum gives a tolerance stricter than A5's;
  - a C with no positive eigenvalue is a STOP;
  - run16 passes a0_chi2_tol(C_T) and records b_rule (rev 1, Grok m2);
  - `--tunes G18` evaluates only G18, and a bad tunes value is refused before any read.
- **Mutants (35 of 35 killed), including:** max → min; the 10 κ₂ ε term dropped; κ₂ on the full spectrum (it survived
  rev 0's suite, Grok M2; now killed by two tests); A0(b) forced true; run16's tolerance reverted to the floor; the
  non-positive guard removed; the tunes loop ignoring `--tunes`.

<!-- absence-ok: an amendment describing a tolerance and the records it leaves standing, not a claim that a result does not exist -->
