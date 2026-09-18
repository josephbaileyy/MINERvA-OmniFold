# DECISION PACKET — every remaining scalar-5D publication blocker

**CITABLE FOR:** the current blocker set and its recommended dispositions.
**NOT CITABLE FOR:** adoption, criterion approval, or any publication significance. Nothing here is
approved.

**Objective (Joseph's):** an **adopted scalar-5D covariance**; the **required verified projections
with correctly paired central values**; **synchronized note/primer/paper**. Submission is his act.

Supersedes the scattered decision lists in `PLAN-20260918-…` §2/§6/§17/§19 as the *current* view;
those retain the derivations.

---

## 1. ⚠ SCOPE AMENDMENT, PROPOSED EXPLICITLY — the generator significance is OPTIONAL and is not a prerequisite

`main_paper.tex:49-51` already states the deferred item as *"a central-value result; its significance
awaits adoption of a common five-dimensional covariance."* **So the paper's required content is the
localization at central-value level plus quoted uncertainties — not a significance.**

**Everything below that serves only a significance is therefore OPTIONAL and must not gate the
required deliverables:** `y_gen`, `N` (D3's threshold), the 12-cell χ², the retained-subspace rule,
`rcond`, any pseudoinverse, and the conclusion-flip `τ`.

⚠ **I had been treating these as prerequisites. That was a scope error and it lengthened the critical
path.** Proposed amendment, for Joseph's explicit ruling: **the required deliverable set excludes the
generator significance; the significance is a separate, later, optional claim.**

**What does NOT move into "optional":** the correlation-sensitive acceptance leg — see §2 row C3.

---

## 2. THE BLOCKER TABLE — required deliverables only

| # | Blocker | Governing requirement | Existing evidence | Recommended disposition | Smallest remaining action |
|---|---|---|---|---|---|
| **C3** | Cause 3 correlation-sensitive leg | **`SPEC` §3.7d, titled "IT IS A REQUIREMENT, NOT A CAVEAT".** Its Answer (a) states a MET result *"does **not** license the assembled covariance for marginalization, projection, coverage validation"* | §3.7d measured: `I₂` vs `[[1,.9],[.9,1]]` give identical `√Tr` and identical per-bin σ while the sd of their sum/difference move `+37.8%`/`−68.4%`. Both adopted legs return **exactly 0.0** | **ANSWER (b) — ADD `s_proj`.** Answer (a) is unavailable: it explicitly withholds the licence for projection, and projections are a **required** deliverable. `s_proj` is `SPEC`'s own first choice | **Joseph's ruling (a)/(b)**, then declare the functional set and `δ` (§3) |
| **C1** | Cause 1 endpoint-interpolation counterfactual | `z-receipt-cv.json` `causes.1 status UNRESOLVED` | requirement stated; `SPEC` §5.8b prices it at **`≈0.03` CPU task-h** | **Approve as priced** — tolerance-free, it is a disclosure | one bounded run, ~0.03 task-h |
| **C2** | Cause 2 F7 operands, `k` and its source | `causes.2 status UNRESOLVED`; `joint_mean_shift_sha256` present | `F7_FLOOR_MULTIPLE = 2.0` at `uq_math.py:138` is **chosen, with an owner**; both centering variants exist | **Approve**, wording *"inherits a tolerance with a stated derivation and an owner"* — **not** *"not chosen"* | D2: create `cause2_f7_margin`, withheld; declare the margin |
| **C4** | Cause 4 jitter print | `causes.4 status UNRESOLVED` | §2.4's four conditions; the guard enforces **condition 3** (§2.4 item 4's own prose) | **Approve**, and amend `SPEC:1237`'s *"condition 4"* to *"condition 3"* | text amendment; then the print, `≤ 0.5764` task-h |
| **C5** | Cause 5 §6.1 disposition | `SPEC:1238` | falsifier **NEGATIVE** across the 15 modules Z invokes, incl. `adopt_unified_5d.py` | **CLOSE as not-falsified, scoped to the 15 traced modules** | Joseph's ruling. No compute |
| **C6** | Cause 6 stat/ML reuse | audit: *"decide from compatibility evidence rather than assume reruns"* | `combine_cov_nd.py` now records all nine fingerprint fields + realized `n_members` | **REUSE** on one zero-compute footing check | read the nine fields; no compute |
| **C7** | Cause 7 sufficiency | `ESTIMATOR_REGISTRY:29` `#16` five-band **publication gate** | **measured twice, two files:** 45 bands, V 13 / R 27 / A 5, and all four weight-only bands **present in R**; receipt `G5_band_partition exhaustive: true` | **CLOSE as sufficient** | Joseph's ruling. No compute |
| **R5** | Two unified-throw ensembles; registry names a file the chain did not consume | `ESTIMATOR_REGISTRY:29` | **step 2 performed:** receipt records `parent.lineage_status: "UNVERIFIED"` and names the 08-11/12 object as `parent_candidate`, **not a component** | **Documentation + verification, no recomputation** | amend `:29` to the consumed file, record both `√tr` |
| **NULL** | `ε` / `null_epsilon` | `SPEC` §6.4 | every route closed (packet §2.1); receipt: `WITHHELD`, *"Neither B nor S is established"*; `r_null = 4.452e-14`; the guard's `max(‖base‖,1)` clamp makes it inert | **Joseph's §6.4 route ruling.** The §6.4 G precedent — *"the defect is in the guard, not in the product"* — is the live question | his ruling; `58524334` informs the remedy, not the requirement |
| **ADOPT** | Trunk adoption | Joseph's goal; `AGENTS.md` | candidate **exists and verifies** (3/3 digests); construction complete, `adoptable: false`, `NON-PASSING` **because criteria are absent, not because construction failed** — every closure identity exact | **his act**, after C1–C7 | — |
| **PROJ** | Verified projections, paired centrals | `AGENTS.md:27` / `:30` | **diagnostic M1 produced and verified**: `n_empty 0`, `src_cells_dropped 0`, exact symmetry, row order cross-checked, source binding carried | **re-run on the adopted trunk** with `--run-class publication` | one `0.25` task-h run after ADOPT |
| **DOCS** | Synchronized note/primer/paper | Joseph's goal | `RESULT :: PASS`, 26 `.tex`/`.bib` byte-identical, containment green across all three | **re-verify after PROJ's content edits** | one build |

**Nothing in this table requires `y_gen`, `N`, a χ², a pseudoinverse, or a rank choice.**

---

## 3. TOLERANCE RECOMMENDATIONS, DERIVED — not read off observed values

**One ground for all three cause-3 boundaries.** The estimator-seed choice must be a **negligible
contributor to any quoted uncertainty**. Treat a relative drift `δ` in a standard deviation as an
additional component in quadrature; it inflates a quoted `σ` by `√(1+δ²) − 1`:

    delta =  5%  ->  0.125%        delta = 14.2% ->  1.003%
    delta = 10%  ->  0.499%        delta = 20%   ->  1.980%

**RECOMMEND `δ = 10%` for `s_proj`, `s_agg` and the per-bin leg of `s_med`.** Ground: a 10% drift
inflates any quoted uncertainty by **0.50%**, which is negligible against every component in the
budget. ⚠ This is **not** display-derived — `SPEC` rev. 16 withdrew the format-derived `0.0861%` and
the half-display-unit rule, and this uses neither. It reads **no observed drift**, so it is
declarable before the members exist.
⚠ **Residual:** the `0.50%` target is a judgement. It is the *right kind* — a negligibility
threshold on the uncertainty budget — rather than a tolerance fitted to a result.

**`s_med`'s second number, the coverage fraction.** **RECOMMEND: 100% on bins entering any quoted
projection; ≥ 99% on the full reported support, with every failing bin enumerated in the receipt.**
Ground: a bin that enters a quoted number must satisfy the tolerance, while with 10,694 bins a
100% requirement over all of them makes the criterion hostage to one pathological bin — so failures
are **named and counted, never absorbed**.

**`s_proj`'s functional set.** **RECOMMEND `SPEC`'s own: the rows of `project_cov_nd.py`'s `M`, plus
the all-ones vector.** This **reconciles the region question and dissolves it**: the rows of `M` cover
all 42 `(E_avail,W)` cells, so the criterion does not depend on which region the *claim* uses. D5's
region choice affects only the optional significance. My earlier corner-integral criterion is
`s_proj` with a **single** functional — a special case, and strictly weaker.

---

## 4. WITHDRAWALS

1. **`rcond = 1e-5` / retained rank 6, and the first-order statistic, are PROPOSALS, not settled
   engineering choices.** They change the statistical prescription and are therefore scientific.
   **And they are not needed for any required deliverable:** `s_proj` is a **forward** quadratic form
   `√(uᵀ C u)` — **no inversion, no rank choice, no cutoff.** The whole rank/`rcond`/pseudoinverse
   apparatus belongs to the optional significance only.
2. **WITHDRAWN: that eigenvalue ratios of `1.8` and `1.7` establish indistinguishability.** They do
   not. Close eigenvalues make the *eigenvectors within that subspace* poorly determined; they do
   **not** make the eigenvalues unusable, nor the subspace ill-defined. I conflated eigenvalue
   proximity with numerical meaninglessness. The gap structure remains a fact; the inference from it
   does not.
3. **Any approximation must be validated against the exact restricted calculation first.** If the
   first-order statistic is ever wanted, compute the **exact** member-wise restricted `χ²` and
   compare; adopt the approximation only where they agree, and report the disagreement where they do
   not. **No approximation machinery before that comparison.**
4. Previously withdrawn and still withdrawn: the conclusion-flip `τ` as an acceptance criterion; the
   three causal branches for `58524334`; "rank 36" bare; "`M C Mᵀ` averages the negatives out"; and
   the three determinism inferences.

---

## 5. WHAT REMAINS

**Joseph's rulings:** §3.7d (a)/(b) — recommended **(b)**; `δ = 10%` and the coverage fractions;
`s_proj`'s functional set; C1/C2/C4/C5/C6/C7 dispositions; D2's key and margin; R5's registry
amendment; the §6.4 null route; the §1 **scope amendment**; then ADOPT.

**Running:** `58524334`, the CV-divergence probe. It informs the **reproduction-path remedy** — which
blocker NULL's ruling may rest on — and **no acceptance requirement in §2 depends on it.**

**No further diagnostics are proposed.** A successor experiment would need a specific unresolved
failure it must detect and a named unmet requirement it would resolve; an unexplained mechanism is
not by itself such a requirement.
