# Comparator predeclaration — `C_stat`, two blind implementations (OI-121)

> ## ⚠ THE SECOND BUILDER WAS CANCELLED, 2026-08-14. THERE IS ONE BUILD, AND NO COMPARISON RAN.
>
> **Joseph's decision, taken partly on the strength of `BEN-188` in this very document** — if two
> implementations can agree bit-for-bit through a shared BLAS kernel, the second builder's marginal
> value is near zero, and C's spec pins `dof`, `centering`, `ravel_order` and member selection, which
> were the only above-the-kernel decisions left to diverge on.
>
> **Read the rest of this file as a design record and a single-artifact validation plan, NOT as
> evidence that a dual build happened.** Sections 1 (tolerance), 3 (mutation coverage) and 4
> (residual risk) describe a two-artifact comparison whose second input does not exist. Concretely:
>
> | part | status under one builder |
> |---|---|
> | tier 0 identity, tier 1 structure, tier 3 derived, tier 4 inputs | **still live** — single-artifact checks, and now the load-bearing ones |
> | **tier 2, the element-wise comparison** | **NEVER RAN. No second artifact.** |
> | §1's tolerance | applies to nothing until something is compared |
> | §4's residual-risk set | still true, and §4.C is now moot in the way that matters — see below |
>
> **The overclaim this banner exists to prevent:** `OI-121`, this file, and the mutation receipt
> together describe *"one spec, two blind builders, a comparator, a judge."* That machinery is
> authorized, documented, and **partly unexecuted**, and it is sitting in the git history looking
> like it proved something. **It did not.** Anyone quoting this campaign's `C_stat` as
> "dual-build verified" is wrong, and this notice is here because I would otherwise be the author of
> the document that misled them.
>
> **What §4.C's finding means now.** `BEN-188` was filed as a risk *to* the dual-build design; it
> became the argument that retired it. The finding is unaffected — it is about BLAS, not about
> `OI-121` — but its remedy (`method_declaration` ruled on by a judge) no longer has a design to
> protect. The judge seat is separately empty. **Nobody is checking the covariance numbers
> themselves**; see the note at the end of §4.

**Lane D (comparator).** Written **before either implementation exists** and committed before either
is read, so that no threshold here can be back-fitted to an observed diff. That is the whole point of
the file: *a tolerance chosen after seeing the disagreement is not a test.*

Harness: [`state/compare_cstat_implementations.py`](state/compare_cstat_implementations.py).
Mutation plan, executable: [`state/probe-cstat-comparator-mutations-20260814.py`](state/probe-cstat-comparator-mutations-20260814.py).

**I construct no covariance.** Not as a third opinion, not as a sanity check. The harness is tested
against *synthetic gaussian matrices I generate from a fixed seed* — that is testing a comparator on
random numbers, not building `C_stat`, and it never touches a `GATE5_REPLICA_XSEC.npz`.

---

## 0. The object, measured rather than assumed

| property | value | source |
|---|---|---|
| observable | 2D (pT, p_parallel), extended FPS grid | `fullevent_fps_dataloader.py:102-125` (fail-closed) |
| pT bins | **15** (16 canonical edges) | `fullevent_fps_dataloader.py:64-66` |
| p_parallel bins | **19** (20 canonical edges) | `fullevent_fps_dataloader.py:67-69` |
| **cells** | **285** | 15 x 19; corroborated `extract_fullevent_fps.py:549`, `state/annealed-shape-r2-terminal-56552326.json:70`, `ND_OMNIFOLD_RUN_LOG.md:3062` |
| flattening | `pt-major row-major: cell = i_pt * n_pparallel_bins + i_pparallel` | declared string, three existing fail-closed consumers |
| replicas | 50 | `submit_gate5_extraction_r2_n50.sh` |
| **rank of `C_stat`** | **<= 49** (mean-centred) or **<= 50** (nominal-centred) | 50 samples in 285 dimensions |

### 0.1 The dimension that actually matters is 262, not 285

285 is the *array* dimension. A cell that is zero in every replica contributes a null row **and**
column, and is not a direction the data was ever asked to span — so the count that bounds the rank
comparison is the number of cells that are ever non-zero. Raised by the orchestrator; measured
directly off the nominal product's own array
(`NONQUOTABLE-DIAGNOSTIC.xsec.slurm-56527676.npz`, read-only):

```
(xsec > 0).sum() = 262 / 285 = 91.93%      zeros 23      negatives 0      non-finite 0
```

The committed summary's `n_cells_populated` is also **262** and its `n_cells_no_denominator` is
**23**, so the array and the JSON agree by two different routes.

**Geometry: a clean kinematic staircase, not scattered dropout.** The 23 zeros are confined to the
high-pT / low-p_parallel corner — row 12 col 0; row 13 cols 0-6; row 14 cols 0-14 — one contiguous
run in every one of the 15 pT rows, monotone in pT. A truncated-spectral treatment is at least
interpretable on a domain of that shape.

> **Spec requirement that falls out of the geometry.** The 262 are contiguous *within each row* but
> **NOT contiguous in the flat pt-major index** — the runs start at different columns, so the live
> set is `[0..227] + [229..246] + [254..265] + [281..284]`. Any reduction to "the reported cells"
> **must be defined by a shipped boolean mask, never an index range.** Two builders slicing
> differently would produce reduced covariances that disagree for a reason having nothing to do
> with the covariance.

**Restated deficit: `262 - 49 = 213`.** Rank <= 49 covers **18.7%** of the reported space. The
in-repo truncated-spectral precedent runs at rank 201 of 205 — **98%**. This is not the same regime
and it is not adjacent to it.

**262 is an ESTIMATE of the family's reported count, not a measurement of it.** It is the nominal,
the mask is drawn per replica (section 5), and the artifact is additionally a
`NONQUOTABLE-DIAGNOSTIC`. The family's union and intersection over the 50 are the real bounds and
they wait for the products.

### 0.2 The rank question was already settled — corrected 2026-08-14

**I raised the rank deficiency as if it were open. It was not, and this section says so rather than
leaving §0 reading as a live escalation.** It was predeclared before launch in
`PREDECLARATION-20260813-gate5-coherent-replicas-n50.md` (committed `6bd3707`, 2026-08-12 23:29):
*"Rank is not the criterion … the rank-deficient GoF treatment is already disclosed under `OI-29`"*,
alongside Joseph's authorization of `N=50` on a stated precision criterion. It is also field-normal —
multisim gives `rank <= N-1` by construction. **213 null directions is a true statement about the
object and a closed question about the campaign.** The declared treatment lives in `OI-29`, not here.

**What survives from this section, and it is the load-bearing part:** the reported-cell count of
262, the staircase geometry, and the flat-index discontinuity — because they set the **artifact
contract**, specifically that any reduction to "the reported cells" must be a shipped boolean mask
and never an index range. That requirement does not depend on the rank question at all.

Nobody should read "the two implementations agree" as "`C_stat` is usable" — but the gap there is
the residual-risk set of section 4, not an undeclared inversion convention.

---

## 1. The agreement tolerance, and why it is this and not something else

**Two float64 implementations of the same arithmetic on identical inputs must agree far tighter than
any physics tolerance.** The tolerance below is a *numerical-reproducibility* threshold. Using a
physics tolerance here would be a category error, and section 1.3 gives the concrete number that
proves it.

### 1.1 The two thresholds

```
TOL_DIAG_REL = 1e-12    relative, on the diagonal (variances)
TOL_CORR_ABS = 1e-12    absolute, on the correlation matrix (all elements)
```

Everything in section 2 tier 0 and tier 1 is **exact** — no tolerance at all.

### 1.2 Why the off-diagonal criterion is scaled to the correlation, not relative

A relative tolerance on off-diagonal covariance elements is the wrong instrument, and it fails in the
direction that matters. Off-diagonal terms `(x_i - xbar)(y_i - ybar)` have mixed signs, so the sum
suffers cancellation: the floating-point error is set by the sum of *magnitudes*, while the relative
error divides by the (much smaller) sum itself. For a pair with correlation `rho`, the relative error
on that element scales as `~ n*eps/|rho|` — it **diverges as the correlation approaches zero**. A
1e-12 relative tolerance would therefore spuriously fail exactly those weakly-correlated bin pairs
where both implementations are behaving perfectly.

Dividing by `sqrt(A_ii * A_jj)` removes the `1/|rho|` factor exactly. The error on a correlation
matrix element is `~ n*eps`, uniformly, independent of how correlated the pair is. **That makes a
single absolute number the correct and uniform criterion across all 285x285 entries**, which is why
the off-diagonal test is stated on the correlation matrix.

### 1.3 Why 1e-12 — headroom above, and the thing it must still catch below

**Floor.** With `n = 50` terms and `eps = 2.22e-16`, the worst-case accumulated error is
`n*eps ~ 1.1e-14`. Legitimate sources of exactly this size: `np.cov` versus an explicit
`Xc.T @ Xc / (n-1)`; BLAS `dgemm`'s blocked accumulation versus `np.sum`'s pairwise summation;
`float64` FMA contraction. **1e-12 is ~90x above that bound** — loose enough that no legitimate
implementation difference can trip it. A bit-exact requirement would fail on a BLAS-versus-loop
difference, produce a false alarm, and train everyone to ignore the check; that is worse than useless.

**Ceiling, and this is the load-bearing argument.** The tolerance must be tight enough to catch a
*different formula* masquerading as rounding. The concrete case:

> **`ddof=0` versus `ddof=1` is a factor of exactly `49/50 = 0.98` — every element is 2.00% LOW
> relative to the `ddof=1` value** (equivalently 2.04% high in the other direction; `50/49 = 1.0204`).

**State the denominator or do not state the percentage.** Both numbers are correct and they describe
the same factor from opposite ends; the orchestrator caught `2.04%` sitting next to `49/50` in the
first version of this line, which is the mismatched pair. Immaterial at a `1e-12` threshold, and
recorded because an unqualified "2%" in a receipt is how a same-name-different-quantity defect starts.

~2% is comfortably inside any physics tolerance anyone would reach for (the campaign's uncertainty
budget cares at the ~1e-3 level). A physics tolerance would wave a genuinely different estimator
straight through. **1e-12 catches it by ten orders of magnitude.** Same for a `1/N` versus `1/(N-1)`
slip, a mean-versus-nominal centring difference, and a missing bin-width division.

**Anything above 1e-12 is not rounding. It is a different formula, and it is a finding.**

### 1.3a The floor, measured rather than argued

The argument above gives a worst-case floor of `n*eps ~ 1.1e-14`. **A bound is not a measurement**,
and the only way this threshold can be wrong in the dangerous direction is by false-alarming on two
*correct* implementations. So it was measured, before any builder artifact existed:
[`state/probe-cstat-tolerance-calibration-20260814.py`](state/probe-cstat-tolerance-calibration-20260814.py)
computes the same sample covariance four legitimately different ways — `np.cov`, an explicit
`Xc.T @ Xc` (BLAS dgemm), `np.einsum`, and an accumulated sum of outer products — and compares all
six pairs.

| pair | worst correlation-scaled |
|---|---|
| `np.cov` vs `Xc.T@Xc` | 2.217e-16 |
| `np.cov` vs `einsum` | 2.217e-16 |
| `np.cov` vs sum-of-outer | **6.256e-16** (worst) |
| `Xc.T@Xc` vs `einsum` | **0.000e+00 — bit-identical** |
| `Xc.T@Xc` vs sum-of-outer | 4.171e-16 |
| `einsum` vs sum-of-outer | 4.171e-16 |

**Worst across all pairs: 6.26e-16 — 1598x below the threshold.** The real floor is ~18x tighter
than the bound I argued from, so 1e-12 is safer than section 1.3 claims and there is no case for
loosening it. The threshold stands unchanged.

**The bit-identical row is not a curiosity — it is evidence for residual risk 4.C.** Two
implementations a person would describe as "different" (`Xc.T @ Xc` and `np.einsum`) agreed to the
last bit, because both dispatch to the same BLAS kernel. That is the independence premise failing
*empirically*, in a five-line test, and not merely as something I was worried about.

### 1.4 What a disagreement means

There is no "close enough" band and no negotiation after the fact. The verdict is three-branch:

- **AGREE** — every tier passes. Reported with worst-observed diffs, so the margin is visible.
- **DISAGREE** — a real finding, escalated with indices in `(i_pt, i_ppar)` coordinates, not a style
  argument to be settled by discussion.
- **UNRESOLVED** — an artifact is missing a required key, or the two are not comparable at tier 0.
  This is *not* agreement, and it must never be reported as one.

---

## 2. What the harness checks

Tiers 0 and 1 run **per artifact** and are exact. Tier 2 is the element-wise comparison. Tier 3 is
redundant with tier 2 by construction and is retained because it is what actually gets published.

**Tier 0 — identity and comparability (exact, no tolerance).**
shape `(285,285)`; dtype `float64`; the `bin_order` string byte-identical to the frozen string;
`edges_pt` / `edges_pparallel` exactly the canonical arrays (this catches a builder who silently used
the *paper* grid — `assert_extended_fps_edges` exists precisely because that substitution is
survivable); `n_replicas == 50`; declared `ddof` and `centring` present.

**Tier 1 — properties each matrix must have alone.**
finite everywhere; symmetric; diagonal non-negative; **measured rank** (a matrix reporting rank 285
has been silently regularised, and that must be declared rather than discovered); count of
eigenvalues below `-eps*|lambda_max|`.

**Tier 2 — element-wise.**
worst absolute and worst relative disagreement **with indices**, reported in both flat and
`(i_pt, i_ppar)` form; worst correlation-scaled disagreement with indices; agreement fraction
**globally and restricted to structurally non-trivial entries**; and a separate count of entries
where one matrix is exactly `0.0` and the other is not.

That last one is not decoration. `extract_fullevent_fps.py:517-518` sets unreported cells to a hard
`0.0` (`reported = comp > 0; xsec = np.where(reported, xsec, 0.0)`), so a block of the 285x285 matrix
is structurally zero. **Two implementations agreeing that `0.0 == 0.0` is not evidence of anything**,
and a global agreement fraction that includes those entries is inflated by construction. The
restricted fraction is the honest number; both are reported so the inflation is visible.

**Tier 3 — the published scalars.** trace and `sqrt(trace)`; per-bin `sigma = sqrt(diag)`; median
relative uncertainty; the eigenvalue spectra compared element-wise. Redundant with tier 2 — kept
because these are the numbers that reach the note, and a disagreement here is the one that matters.

**Tier 4 — the input lists.** Both builders report the sha256 of each of the 50
`GATE5_REPLICA_XSEC.npz` they consumed, plus the 50 bootstrap seeds. I compare the lists and assert
the seeds are distinct. See 4.B1/4.B2 — this converts "both read the same 50 correct files" from an
assumption into a measurement, and it is the only part of the residual-risk set that the comparison
can close rather than merely name.

---

## 3. Mutation plan — for each check, the perturbation that must make it fail

Executable as `probe-cstat-comparator-mutations-20260814.py`, run against synthetic data before the
harness ever meets a real artifact.

**Every mutation first asserts that it actually changed the array.** A mutation that silently fails
to mutate produces a check that "passed" against nothing — I filed `BEN-181` against myself for
exactly that (a mutation that matched only a docstring), and the guard is the fix.

| # | mutation | must be caught by | notes |
|---|---|---|---|
| M0 | `B := A` exactly | **nothing — all tiers must PASS** | negative control: a harness that fails everything is as useless as one that passes everything |
| M1 | reshape `B` to `(15,19,15,19)` | tier 0 shape | |
| M2 | cast `B` to `float32` | tier 0 dtype | |
| M3 | **re-flatten `B` in F-order** | tier 2 **only** | *survives* tier 1 (still symmetric, still PSD, same eigenvalues) — this is the mutation that proves tier 1 alone is insufficient |
| M4 | `B *= 49/50` (`ddof` slip) | tier 2 | the 2.00%-low of section 1.3; a physics tolerance would pass it |
| M5 | flip the sign of one off-diagonal pair | tier 2, with the correct index | |
| M6a | perturb one element by `1.1 * TOL` | tier 2 | tolerance bites from above |
| M6b | perturb one element by `0.9 * TOL` | **must PASS** | tolerance does not bite from below — both sides demonstrated, or the threshold is unfalsifiable |
| M7 | inject `NaN` | tier 1 finiteness | must fail *there*, not slip through a comparison |
| M8 | `B += 1e-9 * I` (quiet regularisation) | tier 1 **rank** and tier 2 | the realistic "builder patched the singular matrix" case |
| M9 | zero one structurally-nonzero row/col in `B` | tier 2 exact-zero-mismatch count | and I record whether the *global* agreement fraction would have hidden it |
| M10 | **permute two bins consistently in rows and cols** | per-cell comparison only | symmetric, PSD, **identical eigenvalues, identical trace** — defeats every structural and every scalar check |
| M11 | declare the wrong `bin_order` string | tier 0 | |
| M12 | substitute the **paper** pT grid top edge | tier 0 edges | the survivable-and-silent grid swap |
| M13 | duplicate a bootstrap seed | tier 4 | 49 distinct draws counted as 50 — residual risk 4.B2 |
| M14 | one member sha256 from a different family | tier 4 | contaminated family — residual risk 4.B1 |
| M15 | omit a required key (`ddof`) | tier 0 -> **UNRESOLVED**, not AGREE | a missing key must never read as agreement |

M3 and M10 are the two that justify the whole element-wise design: both are invisible to every
structural and every scalar check, and both are exactly the shape of a real convention mismatch.

### 3.1 Measured — 17/17 behaved as predeclared, and two of my own claims did not

Run: `probe-cstat-comparator-mutations-20260814.py`, against a synthetic 50 x 285 gaussian carrying
**the real object's dead-cell geometry** (the 23-cell staircase of section 0.1) so the free-agreement
inflation is measurable rather than asserted. With 262 live cells, **12,581 of 81,225 entries
(15.5%) are `0.0 == 0.0` and agree for free.**

All 17 mutations behaved as predeclared: M0 and M6b `AGREE`, five `UNRESOLVED` at tier 0, ten
`DISAGREE`. **But "as predeclared" was scored on caught-versus-not, and on the finer question of
*which tier* catches what, I was wrong twice.**

**Correction 1 — "tier 2 ONLY" was wrong for M3 and M10.** Both also fire tier 3, via per-bin sigma.
The corrected and now-measured claim is sharper and is the one that matters:

| | trace | eigenvalue spectrum | per-cell |
|---|---|---|---|
| M3 (F-order re-flatten) | 0.000e+00 — **blind** | 1.043e-15 — **blind** | caught, 1.000e+00 |
| M10 (two bins swapped) | 0.000e+00 — **blind** | 1.217e-15 — **blind** | caught, 8.923e-02 |

> A permutation is invisible to every **scalar summary** (trace, sqrt-trace, eigenvalue spectrum) and
> to every **structural property** (symmetry, PSD, rank). It is caught **only** by comparisons that
> are per-cell. That is the entire argument for element-wise comparison, and it is now measured.

**Correction 2 — the tier-3 eigenvalue metric was broken, and the mutation run is what exposed it.**
The first version reported `1.000e+00` for M3 — for a *permutation*, which is a similarity transform
and provably preserves the spectrum. The mutation could not have done that, so the metric had to be
wrong. It was: `C_stat` has rank <= 49 in 285 dimensions, so **236 of 285 eigenvalues are numerically
zero** (measured), and a *relative* metric divides by ~1e-18 and returns ~1.0 for any pair whatsoever.
Fixed to absolute-scaled-by-`|lambda_max|`, at which point the measurement agrees with the
mathematics (1e-15, blind, as a similarity transform must be) and the check becomes real enough to
promote into tier 3's failure list.

**The mutation run also found a live crash in my own harness.** M7 (inject `NaN`) did not produce a
finiteness failure — it raised `LinAlgError: Eigenvalues did not converge` out of `eigvalsh` and took
the whole comparison down with a traceback. **A harness that crashes on a bad artifact has not
checked that artifact; it has abstained** — and a traceback reads as "the run broke," not "the
artifact is bad." Fixed by checking finiteness before any spectral work. It then recurred **in
`tier3_derived`, because I fixed the first site and not its sibling** — the precise asymmetry this
campaign keeps filing (`BEN-173`). Each function now guards itself rather than trusting its caller.

Three defects in the comparator, all found before it ever saw a builder's artifact, none of which
would have been found by reading it.

### 3.2 The copied constants are self-checking

The harness carries its own copy of the canonical edges. **A copy nobody re-checks is a stale value
waiting to happen** — if the frozen grid ever moved, this harness would go on validating builders
against the old one and reporting tier-0 PASS. `verify_constants_against_loader()` parses the
literals out of `fullevent_fps_dataloader.py` with `ast` (no import, so no TensorFlow) and the
mutation probe refuses to score anything if they disagree. Per this repo's own principle: *prefer
the executable form of any rule you are tempted to write down.*

It has its own positive control — a synthesised loader with one pT edge moved `30.0 -> 25.0`, which
must be detected — because a stale-grid detector that has never detected a stale grid is not
evidence. The control fires. The first version of the check also had its repo-root path off by one
and **failed closed**, refusing to score rather than passing silently, which is the direction that
mistake should fail in.

---

## 4. What element-wise agreement would NOT catch

**This is the residual risk of the entire OI-121 design.** Stated up front, by me, before any result
exists — not discovered afterwards. It is the most useful thing I can hand the `codex` judge, and its
existence is the reason "the two implementations agree" is a bounded claim rather than a general one.

The design proves *"two implementations of the spec agree."* It does not prove *"the spec is right"*
or *"the inputs are right."*

### A. Spec-level — both builders correctly implement a wrong instruction

- **A1 `ddof`.** If the spec says `ddof=0`, both use it, both agree, and `C_stat` is biased low by
  2%. The mutation M4 catches a builder *deviating* from the spec; nothing here catches the spec.
- **A2 Centring.** Replica-mean versus nominal differ by the outer product of the
  `(mean - nominal)` offset. The push/reweight chain is nonlinear, so the replica mean need not sit
  on the nominal, and this is not a null choice. **It also silently changes the rank, 49 versus 50.**
- **A3 Mask flicker (see section 5).** If the spec says "use `xsec` as written," both builders
  faithfully turn a reporting-mask artefact into physics variance.
- **A4 Units and bin widths.** `xsec` is differential. A missing or doubled bin-width factor
  inherited from the spec is applied identically by both.
- **A5 Outlier handling.** Any declared trimming of the 50 is applied identically by both.

### B. Input-level — both read the same wrong 50 files

- **B1 Stale or mixed provenance.** Both builders glob the same directory; if it contains members
  from the superseded predecessor job `56935552` alongside the changed continuation, both find 50
  files and agree perfectly on a contaminated family. **Closable, and tier 4 closes it** — compare
  the two sha256 lists rather than assuming they match.
- **B2 Duplicate replicas.** Two members sharing a `bootstrap_seed` gives 49 distinct draws counted
  as 50: variance biased low, both implementations agreeing exactly. **Closable — tier 4 asserts the
  50 seeds are distinct.**
- **B3 Centring reference drift.** If A2 resolves to nominal-centred, a nominal produced by a
  different code version than the replicas is a silent inconsistency both builders inherit.

### C. The independence premise itself — and this one needs a ruling

**If both implementations reduce to `np.cov(X, rowvar=False, ddof=1)`, the "two independent
implementations" claim collapses to "two people typed the same one-liner."** Their agreement then
demonstrates float64 determinism and essentially nothing else, while *reading* as the strongest
evidence in the campaign.

**This is measured, not hypothesised.** Section 1.3a's calibration found `Xc.T @ Xc` and
`np.einsum("ki,kj->ij", ...)` — two formulations any reviewer would call different — agreeing
**bit-for-bit, 0.000e+00**, because both dispatch to the same BLAS kernel. Perfect agreement between
"two implementations" is therefore *demonstrably* achievable with no independence at all. This is the failure mode where the record is stronger than its evidence —
which is the `codex` judge's declared specialty, so it belongs in front of that judge.

I cannot check it myself without reading the implementations, which my constraints forbid and which
would end my ability to referee. **Recommended remedy, requiring no one to break a constraint:** each
builder declares its core computation in one line in its own artifact (`method_declaration`), and the
*judge* — not the comparator — rules on whether two genuinely different computations occurred. Routed
to the orchestrator as a design gap rather than acted on unilaterally.

### D. Correct but uninformative

- **D1** The structurally-zero block: agreement there is free. Handled by reporting the restricted
  agreement fraction alongside the global one.
- **D2 Dilution.** If the covariance is dominated by a few high-rate bins, a worst-absolute metric is
  dominated by them too, and a disagreement in the sparse tail bins gets buried. Handled by the
  correlation-scaled metric, which weights every pair equally.

### E. Downstream — outside this comparison entirely

A perfectly verified `C_stat` says nothing about the treatment of its null directions. **Nobody
should read "the implementations agree" as "`C_stat` is usable."** That is section 0's rank question,
and per §0.2 it is already declared under `OI-29` rather than open.

### F. Under one builder: nobody checks the covariance numbers — added 2026-08-14

The banner at the top records that the second build was cancelled. This is the consequence, and it
should be read before anyone treats the surviving checks as sufficient.

**Sort the remaining checks by what they have power over.** Some compare the artifact to an
**external** fact and can genuinely fail; the rest compare the artifact to **the builder's own
declarations** and are self-consistency checks.

| check | power over |
|---|---|
| `member_sha256` vs the files actually on disk | **external** — I recompute the digests myself |
| `reported_mask` vs `C_syst`'s mask | **external** — the assembler's reference |
| `edges_pt` / `edges_pparallel` vs the loader's canonical grid | **external** |
| measured rank vs declared `rank_at_1em10_lambda_max` | **external** — I measure it |
| reduced form vs its own full form restricted to the shipped mask | **external to the covariance** — arithmetic the builder did not get to declare |
| `layout_fingerprint`, `dof`, `centering`, `ravel_order`, `units` | **the builder's own declarations** |
| symmetry, PSD, finiteness | structure only — true of many wrong matrices |

> **Nothing in that table has power over the covariance VALUES.** Every element could be off by a
> factor, or computed from the wrong 50 vectors in the right files, and every check above still
> passes. `BEN-186`'s lesson generalises: an artifact validated against its own declarations proves
> the builder was self-consistent, which is a real property and is not the one anyone wants.

Two honest consequences. First, the reduced-vs-full check is now **disproportionately valuable** —
it is one of the few surviving checks that can fail on a genuine arithmetic mistake, which is why it
is worth the one numpy line even though it looks trivial. Second, **the gap should be stated in the
final receipt rather than left for a reader to notice**, because the two-builder machinery in the git
history reads as though it closed exactly this gap, and it did not.

**On whether I should close it myself.** My prohibition on constructing a covariance was reasoned:
*"the moment you produce your own covariance you stop being able to referee the two that exist."*
**There are no longer two to referee, so that rationale has lapsed** — which is an observation about
the reason, not a licence. A D-built cross-check would be *weak* evidence about the kernel (`BEN-188`
— I would likely reach the same BLAS) and *meaningful* evidence about the above-the-kernel
decisions: member selection, centring, mask application, `ddof`. Those are the likely bugs, and
"pinned in a spec" is not "implemented correctly." **Whether the prohibition is lifted is Joseph's
call and not mine, and I have not acted on it.** Raised so the option is visible, since the
alternative is that nobody checks the numbers and nobody says so.

---

## 5. One hazard found in the extractor while establishing the bin count

Not a comparator finding and not either builder's fault — it belongs in the spec, and it is cheap
there and expensive later.

`extract_fullevent_replica.py:192-196` monkey-patches `completeness_2d` so that the replica's signal
Poisson factor multiplies the weights **inside** the completeness computation. The reporting mask
`comp > 0` is therefore **drawn per replica**. A thinly-populated cell can be reported in replica 7
and masked to a hard `0.0` in replica 23 — and the resulting spread across the 50 is **mask flicker,
not statistical variance of the cross section.**

Both builders would compute the identical variance from the identical replica vectors and agree
perfectly. It is category A3 above: invisible to this entire design.

**What I have and have not established.** The code path is unambiguous — the mask is recomputed per
replica. **I have not measured whether any cell actually flips across the 50 draws**; that needs the
products, and at the time of writing 35 of 50 were still `PENDING`. It may be zero cells, in which
case the hazard is real and empty. **I am not asserting it happened.**

Proposed spec requirement, one integer per cell: **`n_replicas_reported`**, the count of replicas in
which each cell passed `comp > 0`. Any cell with `0 < n < 50` has mask-flicker contamination in its
variance and can then be handled deliberately instead of silently.

**Where the flicker lives is now known, and it is a small set.** Section 0.1's geometry shows the
reported set is a staircase whose boundary runs along rows 12-14 at the low-p_parallel edge. Those
boundary cells are precisely the thinly-populated ones whose `comp > 0` is one Poisson draw from
flipping. **The reported-set boundary and the flicker zone are the same cells** — so the
union-versus-intersection choice is not a diffuse worry spread over 262 cells, it is a decision
about a specific band of order ten, and it can be stated exactly once the family lands. Construct on
the intersection and real high-pT cells are discarded; construct on the union and some cells'
"variance" is partly the mask switching off. **C's declaration, not a builder's script.**

---

## 6. What each builder's artifact must carry

**The comparator cannot compare what nobody emitted.** This is a spec requirement, routed to C, not
a convenience — it is `REQUIRED_KEYS` in the harness and a missing entry yields `UNRESOLVED`, which
is not agreement (mutation M15).

| key | why the comparison needs it |
|---|---|
| `cov` | the object, `(285,285)` float64 |
| `bin_order` | the C-vs-F failure is invisible to every structural check (M3) |
| `edges_pt`, `edges_pparallel` | the paper-grid substitution is survivable and silent (M12) |
| `n_replicas` | 50 |
| `ddof` | the 2.04% estimator difference of section 1.3 (M4) |
| `centring` | replica-mean vs nominal; also sets the rank ceiling, 49 vs 50 (4.A2) |
| `replica_seeds` | duplicate-seed detection (M13, 4.B2) |
| `member_sha256` | the 50 inputs actually consumed (M14, 4.B1) |

Optional but recommended: `reported_mask` (section 0.1), `n_replicas_reported` (section 5),
`mean_vector` / `nominal_vector`, and **`method_declaration`** — one line naming the core
computation, which is what lets the *judge* rule on residual risk 4.C without the comparator having
to read either implementation.
