# PART F — the minimum acceptance requirements for ENDPOINT A, derived before the packet exists

**Owner:** independent-assessment lane (`lane/z-criteria-independent-assessment-20260910`).
**Base of measurement:** `6f24fb0097a7603b7d6acb695de06dbb3f3ea157` (`origin/main`, 2026-09-10 01:01:27 -0700).
**Continues:** Parts A–E of `REVIEW-20260910-z-acceptance-criteria-independent-derivation.md` (`1508ead0`,
`09905260`, `69b9fde2`, `47ff4606`, `54c565a6`). Part A's `A1`–`A31` remain the standing yardstick; this
part adds `F1`–`F21` for the endpoint-A split, which did not exist when Part A was written.

**CITABLE FOR:** an independent yardstick against which the designer's endpoint-A packet can be judged
for completeness, and three measured findings (`F-0`, `F-I`, `F-II`).
**NOT CITABLE FOR:** adoption of any criterion, any grade, any contract amendment, or any statement about
what Joseph decided. Nothing here is a remedy; see §F.6.

---

## F.0 — PROVENANCE OF THIS DERIVATION, INCLUDING WHAT I REFUSED TO READ

The assignment requires the requirements to be derived from the governing decisions and the intended
publication claims *before* the designer's answers are read. The designer's endpoint-A packet did not
exist at any point during this part's authorship, so the ordering is guaranteed by chronology rather
than by discipline. What was *not* guaranteed is the prior packet, which does exist and whose title
(`…-z-consumer-set-and-endpoint-requirements`) says it already contains an endpoint-requirement list.

**So I did not read it.** Digested and recorded here, NOT read at authorship time, both at `173baf44`:

| artifact | sha256 | lines |
|---|---|---|
| `PACKET-20260910-z-consumer-set-and-endpoint-requirements.md` | `0dce72d2c34e3a448e03571b64b1e2d771070a35cf71e25318f90d1ac8246de3` | 308 |
| `RECOMMENDATION-20260910-z-scientific-acceptance-criteria.md` | `a528a8fdfd3953d074ce244d11087bd17991ab5369239d4947d7c7583f50eaf8` | 1406 |

The single exception is declared: to verify the finding relayed to me I needed the premise it attacks,
and I took that from **`CATALOG.md:227` at `173baf44`** — one line, *"`cause3_corr`'s hazard is
UNREALIZED — no released consumer reads off-diagonal structure"* — plus the relay itself. I read no
part of either body. The recommendation at `2ebdf095` was reviewed in Part D; `173baf44` is a later
revision of it and I have read only the `subspace` grep hits needed for §F.6.

### F-0 — MEASURED FINDING: both governing rulings are unrecorded

Every requirement below is conditional on two rulings that exist only as relay.

- No file matching `DECISION-2026091*` or `RULING-2026091*` exists in **any** of the 131 local and
  remote refs. The newest decision record in any ref is
  `docs/orchestration/DECISION-20260907-joseph-ratifies-r5-attempt-accounting-and-declines-untracking.md`.
- A per-ref search for four distinctive phrases from the relay — `finite-ensemble disclosure`,
  `deferred, not passed`, `verified ensemble size`, `not a bias correction` — returned zero hits, with
  an in-loop positive control (`Endpoint B`, which is in `docs/PUBLICATION_COMPLETION_RUNBOOK.md`)
  firing on 24+ refs. The instrument works.

**Scope this honestly.** The phrase search proves those four phrasings are absent, not that no
differently-worded record exists. The filename check is unconditional. `USER-DECISIONS.md`'s "Recorded
decisions" section says *"No workflow-era decisions have been recorded yet."*

**The consequence is not that the rulings are doubtful — it is that they are undiffable.** A
requirement set derived from an unrecorded ruling cannot later be checked against drift in that
ruling, because there is no text to compare against. Every lane's copy is a paraphrase, and this
campaign has four withdrawn relay claims in two days on these same artifacts. `CLAUDE.md`'s standing
rule — *"a result is live only after its evidence and required records land in a commit"* — applies to
a ruling as much as to a measurement.

**One thing partly rescues Ruling 2, and I record it because it cuts against my own finding's
weight.** Ruling 2's disclosure-only character is *not* new. `app_statmethods.tex:672-678` already
says no generic correction is mandated, for stated reasons (a block sum has no single debiasing
factor; the standard factor assumes independent Gaussian realizations and a data-independent
truncation), and already names the cheap unconditional half: *"record `N` beside each block in the
construction receipts."* `OI-137` records that Joseph ruled *"disclose, do not correct"* on
2026-08-22, at `DECISION-20260822-joseph-b1-lift-and-clause-c.md`, **which is recorded.** So Ruling 2
largely ratifies a live mandate. Ruling 1 has no such anchor that I found.

---

## F.1 — WHAT RULING 1 LEAVES LIVE, AND HOW WEAK THE CLAIM IS

Under Ruling 1 endpoint A releases **Z and declared projected uncertainties**, and releases no
Z-dependent non-2D significance, p-value or calibrated exclusion. The validated 2D scope is unchanged.

This is a *central-values-with-error-bars* claim. It is much weaker than a significance, and the
requirement set must be proportionate to it. The publication already says as much in its own voice:
`paper_body.tex:145-148` — *"Every non-two-dimensional result in this Letter is a central value. A
publication-level significance requires the adopted, selection-complete scalar five-dimensional
covariance, which is not yet in hand."*

Two consequences run in opposite directions and both are load-bearing.

1. **No inversion is performed.** So `app_statmethods.tex:645-651`'s declarations (i)–(iv) — the
   inverse used with its `rcond` or truncation rank, the retained rank as `ndf`, the rank-truncation
   scan, and which covariance is meant — are all conditioned on *"Any N-D $\chi^2$"* and are
   **inapplicable**. Declaration (v) is the only live one, and its `p` field ("the effective dimension
   actually inverted after truncation") is not applicable. This is exactly what Ruling 2 relays, so
   Ruling 2's substance is derivable from Ruling 1 plus the note. That corroborates the relay.
2. **An error bar still has to be the uncertainty of the thing it is attached to.** Weakening the
   claim from a significance to an error bar removes the inversion requirements; it does not remove
   completeness, operand-correctness, or the requirement that a released number not be silently zero.

---

## F.2 — F-I: MEASURED FINDING. A RELEASED PROJECTED UNCERTAINTY IS A FUNCTION OF OFF-DIAGONALS

This is the finding I was asked to verify rather than inherit. **The conclusion holds. The mechanism
as relayed to me is misrouted, and the correct form is different and stronger.**

### What was relayed, and what is actually there

The relay cited `eavailW_covariance.py:442` computing `project_covariance(C5stat, Mew)`, with M's row
shape attributed to `project_cov_nd.py:5-8`'s width-weighting. Measured at `6f24fb00`:

- `:441` computes `C_stat = project_covariance(C5stat, Mew)`. `:442-443` is the `sqrt(trace)` print.
- **`Mew` is built inline at `:404-406`.** `project_cov_nd.build_projection` (`:79`) never touches it.
  `project_cov_nd.py:5-8` is a different module's docstring and does not govern this `M`.
- **Width-weighting is not the operative cause.** It sets the weights. What admits the off-diagonals
  is that a destination row aggregates more than one source cell:
  `Mew[ewrow, np.arange(report5.size)] = …` puts exactly one nonzero in each **column** and collects
  every reported `(pt, pz, q3)` cell sharing an `(E_avail, W)` destination into one **row**. Hence
  `diag(M C Mᵀ)_i = Σ_{j,k → i} w_j w_k C_jk`, and a unit-weight `M` does the same.

### The general statement, which does not depend on this file

Endpoint A releases *declared projected uncertainties*. A projected uncertainty is
`σ_i = sqrt((M C Mᵀ)_ii)`. Whenever a destination row aggregates ≥ 2 source cells, off-diagonal
entries of `C` enter `σ_i`. **The geometry forces this**: `pt 14 × pz 16 × eavail 7 × q3 7 × W 6 =
65,856` cells (`2d-unfolding/unfold_2d_omnifold_unbinned.py:29-33`,
`nd-unfolding/unfold_nd_omnifold_unbinned.py:97-119`), of which `10,694` are reported
(`app_statmethods.tex:640`), projected onto `42` destination `(E_avail, W)` bins — mean row support
`254.6`, and by pigeonhole some row carries ≥ `255`.

**The dichotomy is complete and there is no third branch.** Either the projected uncertainty is
computed as `M C Mᵀ`, in which case off-diagonals enter; or it is computed by summing per-cell
variances, which is the error `eavailW_covariance.py:393-395` exists to forbid — *"Never sum standard
deviations across marginalized cells."* And if instead the full matrix `Z` is released and projected
downstream, the off-diagonals are released *a fortiori*.

### Magnitude, measured

`docs/orchestration/state/probe-z-endpointA-projected-diagonal-20260910.py`, `rc = 0` from the repo
root. It imports the production `uq_math.project_covariance` (`:171-180`) and reproduces the
`:404-406` construction shape-for-shape; the two source covariances and the arm sizes are declared as
mine. **With the source diagonal held exactly fixed** (`max |Δdiag| = 0.000e+00`):

| arm | result |
|---|---|
| production path, 42 rows, support 27 | released σ ratio `2.514` – `3.552` per destination bin |
| CONTROL A — selection-only `M`, row support 1 | `max |Δσ| = 0.000e+00` — effect vanishes, so it is attributable to row support and nothing else |
| CONTROL B — unit weights, multi-support | ratio `2.468` – `3.620` — survives; width-weighting is not the cause |
| CONTROL C — opposite direction | identical inputs → `0.000e+00`; diagonal scaled `1.05` → ratio exactly `1.050000` |
| one row at the real support `255` | equicorrelation alone spans `0.986×` to `2.803×` |
| same row, exact envelope over PSD correlation structures | `max/min = 2.62e+06`; the minimum drives σ to `1.58e-05` |

**I corrected an overstatement inside this probe before committing it.** The first draft printed
`sqrt(m) = 15.97` as a reference and its conclusion then claimed "more than an order of magnitude",
while the table in the same section said `2.803`. `sqrt(m)` is the full-correlation factor only when
the `w_j σ_j` terms are equal; with real bin widths and sigmas over two decades the attained factor is
the inverse participation ratio, `2.803`. The probe now says so in the section that prints it. This is
`[[my-unchecked-numbers-err-toward-my-active-argument]]` caught one step before it shipped.

### Where I do not follow the relay's framing

`z_contract.py:231-235` gives `cause3_corr`'s withholding reason verbatim: *"SPEC §3.7d: no
correlation-sensitive leg is adopted, and none has a boundary. Both adopted statistics are functions
of the diagonal alone, so a MET result on them licenses nothing about `C_Z`'s off-diagonal
structure."*

That is a claim about the **grading legs**. The premise at `CATALOG.md:227` is a claim about the
**released consumers**. Two different propositions, and only the second is what `F-I` falsifies. The
contract's own sentence runs *toward* the finding rather than against it: if a released error bar is a
linear functional of off-diagonals, then diagonal-only legs are blind to a quantity the release
depends on — which is precisely what that sentence says cannot be licensed. **The withholding text was
right about the legs and is being read as though it were about the release.**

---

## F.3 — F-II: MEASURED FINDING. THE ENSEMBLE-SIZE EVIDENCE IS BETTER THAN CITED, AND STILL HAS A HOLE

The relay cautions that the cited sources are `#SBATCH --array=` declarations, which record what was
submitted. That is correct about those two lines and it points at the weaker of two available sources.

Measured at `6f24fb00`:

| block | N | normalization | is N on the artifact? |
|---|---|---|---|
| unified throws | `160` | biased `1/N`, `uq_math.py:104` | **yes** — recounted `T = X.shape[0]` (`unified_throw_cov.py:412`), stamped `n_throws` (`:564`) |
| systematics universes | `169` | biased `1/N` | **yes** — `analyze_universes_5d.py:278` stamps `n_universes = len(paths)`, from the files actually read |
| `C_stat` | `100` | **unbiased `1/(N−1)`**, `combine_cov_nd.py:20` | **no** — recounted and printed at `:22`, but `:23-26` writes only the TH2D |
| `C_ML` | `24` | **unbiased `1/(N−1)`**, `combine_cov_nd.py:20` | **no** — same |
| ~45 MAT bands | `2` each | biased `1/N` via `mat_covariance` | n/a — see `F7` |

`--array=1-100%32` (`sbatch_bootstrap_5d_gpu.sh:5`) and `--array=1-24%24`
(`sbatch_seedscan_split_5d.sh:5`) are submission declarations. But `combine_cov_nd.py:14-18` makes
`--expected-ids LO-HI` a **required** argument and passes `set(range(lo, hi+1))` to
`replica_manifest.py`, whose `:44-48` raises on `got != expected_ids` and reports **both**
`missing=` and `extra=`. That is a fail-closed, bidirectional set-equality check at consumption: the
product cannot exist unless exactly those ids were present. **That is not a declaration; it is an
enforced check**, and it is materially stronger than the `--array=` line.

**The residual hole is a different one, and it is precedented in this repository.** `--expected-ids`
is a launcher constant, so the enforcement proves *consistency between the constant and what landed* —
never *adequacy of the constant*. A constant edited down to match a shortfall passes silently.
`OI-17` records that exact event: *"The J28 reroll used 122 of 160 throws because slabs 31 through 39
were lost"*, with the offered resolution being *"rethrowing slabs 31 through 39"* or *"labeling the
replacement as a 122-throw product."* Both remain live options in that row.

---

## F.4 — THE DERIVED MINIMUM REQUIREMENTS

Stated as requirements on the packet, not as designs. Where a requirement is not yet justifiable from
this tree I say what evidence would justify it and stop.

### Group 1 — the released object and its declared population

- **F1.** The released set must be **enumerated**, not described by role. For each member: the
  destination space, the source covariance, and whether what is released is a matrix or a set of error
  bars. *Ground:* a population named by a definite description can re-point to nothing — measured in
  Part B, where the `C-1` statistic's declared population (`(generator, projection)` pairs the
  publication quotes) had **zero** members, the four `\gbdtFive*` macros at `values.tex:112-115` being
  defined and used nowhere.
- **F2.** Each released projection must name its **builder and commit**. Four non-equivalent builders
  exist at `6f24fb00`: `p4_lib.py:1353`, `project_cov_nd.py:79`,
  `pet/assemble_ctotal_bkgsub.py:36`, and the inline construction at
  `eavailW_covariance.py:404-406`. *Ground:*
  `FINDING-20260910-projection-builders-agree-numerically-and-diverge-on-refusal.md`, in `main` — they
  agree on weights and **diverge on refusal**, so numeric agreement is not interchangeability.
- **F3.** Endpoint A must state affirmatively that **no significance, p-value, χ², `ndf`, `rcond` or
  retained rank is released.** This is load-bearing, not a courtesy: it is what makes declarations
  (i)–(iv) inapplicable and makes (v)'s `p` field "not applicable". Without the statement, `F12` has
  no premise.

### Group 2 — off-diagonal completeness (from `F-I`)

- **F4.** If any projected uncertainty is released, **off-diagonal completeness of the projected source
  block is a requirement of endpoint A**, not deferrable to endpoint B. The diagonal-only premise
  cannot carry the deferral.
- **F5.** If `cause3_corr` is deferred, the amendment must state **which released quantity is thereby
  ungoverned**, and must not rest on the diagonal-only premise. Naming the exposure is compatible with
  deferring the boundary; resting the deferral on a false premise is not.
- **F6.** A released projected row with zero or near-zero variance must be **refused or marked at the
  point of release**. `eavailW_covariance.py:425-432` is deliberately fail-open with a printed
  warning, for a stated and correct physics reason — the `(E_avail, W)` plane is kinematically
  constrained, so an empty row can be legitimate. But `:410-413` names the consequence exactly: a zero
  variance *"does not look like missing data — it looks like a very good measurement."* **A print
  statement does not survive into a released table.** Section 6 of the probe shows the same
  near-zero σ is reachable at a fully populated row purely through correlation structure, so the
  existing warning does not cover the case `F-I` opens.

### Group 3 — Ruling 2 and declaration (v)

- **F7.** The block partition must be by **sampling character, not by which function computed the
  block.** The ~45 MAT bands go through `mat_covariance(np.stack([x_minus, x_plus]))`
  (`unified_throw_cov.py:460`, `p4_build_components.py:74`, `eavailW_covariance.py:363`) with `N = 2`,
  yet each is algebraically `((x₊−x₋)/2)((x₊−x₋)/2)ᵀ` — exactly rank one and deterministic, with no
  sampling and therefore no finite-ensemble bias. `app_statmethods.tex:672-674` already draws the
  line, calling them *"about 45 deterministic rank-one MAT band outer products plus statistical and
  ML blocks."* Declaring *"N = 2, biased 1/N, no finite-ensemble treatment applied"* for them would
  satisfy the letter of Ruling 2 while inviting the reader to apply a correction where none applies —
  and `(N−p−2)/N` at `N = 2` is not a number anyone should be handed. **The note supplies the
  partition Ruling 2 needs; the packet must use it rather than the function name.**
- **F8.** The declaration must be **per block**, because **two normalization conventions coexist in one
  sum**: biased `1/N` (`uq_math.py:104`) for throws and MAT bands, unbiased `1/(N−1)`
  (`combine_cov_nd.py:20`) for `C_stat` and `C_ML`. A single convention quoted for Z would be false of
  most of it. (v)'s per-block form already accommodates this, so this is satisfiable as written.
- **F9. RESERVED, NOT ANSWERED: "verified" is undefined between two readings that differ by a code
  change.** (A) *re-measurable from the released artifact* — **not satisfied** for `C_stat`/`C_ML`,
  and closing it needs one scalar stamped beside the TH2D at `combine_cov_nd.py:23-26`. (B)
  *established by a fail-closed check at construction* — **already satisfied**, by
  `--expected-ids` + `replica_manifest.py:44-48`. The evidence that would settle which is meant is the
  ruling's own text, which does not exist (`F-0`). **I do not pick between them.** Under reading (A)
  a requirement for a new stamp is justified; under (B) demanding a re-measurement rejects an
  acceptable case, which is axis (c).
- **F10.** Whichever reading holds, **the citation must move** from
  `sbatch_bootstrap_5d_gpu.sh:5` / `sbatch_seedscan_split_5d.sh:5` to the enforcement site
  (`combine_cov_nd.py:14-18` + `replica_manifest.py:44-48`). Citing the `--array=` line understates
  the evidence that exists and misdescribes its kind.
- **F11.** The declaration must distinguish **intended N from achieved N**, because `--expected-ids` is
  a launcher constant editable to match the outcome, and `OI-17` records that situation (`122 of 160`)
  as still open. A single number cannot carry both, and reporting only one lets a silently reduced
  ensemble pass a disclosure requirement — axis (b).
- **F12.** `p` must be recorded as **not applicable with its reason** (no inversion is performed under
  Ruling 1), not left blank and not filled with a truncation rank that no consumer computed. Blank and
  not-applicable are different disclosures.

### Group 4 — the discharge machinery, unchanged by the endpoint split

- **F13.** Requirements must attach to **(cause × artifact) pairs**. A list naming causes without
  naming Z as the artifact is not gradeable (`CRITERIA-20260811` §0; `DECISION-20260902` on the
  referent being the candidate).
- **F14.** **"Deferred" is not a grade.** The vocabulary is closed to MET / OPEN / UNRESOLVED
  (`DECISION-20260902-joseph-rules-no-fourth-grade-token.md`). If `cause3_corr` is deferred from
  endpoint A, `(cause 3, Z)` remains non-passing, and no column may read "deferred". The relay's own
  distinction — *deferred versus passed* — is the same point and I am recording that it is already
  ruled, not newly proposed.
- **F15.** Any test leg must be **power-tested in both directions**: fires on the bad case, silent on
  the good case, and covers the opposite-direction bad case.
- **F16.** §6.6's form constraint holds: **statistic, denominator, precision target and boundary are
  approved together.** A packet that supplies three of the four supplies none of them.

### Group 5 — completeness, and what must NOT be required

- **F17.** Every requirement **dropped** from endpoint A must carry **the check that dropped it**, not
  the category it fell into. "Endpoint B material" is a category; "no released quantity reads this,
  measured at ⟨cite⟩" is a check. `F-I` is what a category-level drop looks like when it is wrong.
- **F18. Axis (c), and it is the one most likely to be got wrong.** Endpoint A must **not** be
  required to satisfy inversion-grade criteria. Specifically out of scope, because no significance is
  released: the ρ bound and its `rho_max`, retained rank, retained-subspace identity, `rcond`,
  `ndf`, the rank-truncation scan, and `s_sig` over declared pairs. Importing any of them rejects
  acceptable cases. This is the requirement I expect to have to defend, because those criteria are the
  ones with the most developed mathematics behind them and are therefore the easiest to reach for.
- **F19.** Endpoint A must **not** be required to apply a finite-ensemble correction. Ruling 2 is
  disclosure only, `app_statmethods.tex:672-677` declines a generic correction for stated reasons, and
  `OI-137` records Joseph's *"disclose, do not correct"* at
  `DECISION-20260822-joseph-b1-lift-and-clause-c.md`.
- **F20.** Requirements must be satisfiable **without new cluster compute**. The R5 ceilings and the
  2026-09-30 stop are unchanged, and every measurement named in `F1`–`F19` is a read of an existing
  artifact, a code citation, or one scalar written beside an existing product.
- **F21.** The packet must not assert what Joseph decided beyond what is recorded. Per `F-0` this
  currently means: Ruling 1 and Ruling 2 are **relayed**, and the packet should carry them as such
  until a decision record lands.

---

## F.5 — PRE-REGISTERED: WHAT WOULD MAKE ME RETURN *BLOCK*

Committed before the packet exists, so the verdict cannot be fitted to it afterwards.

1. **The diagonal-only premise survives** as the ground for deferring `cause3_corr`, in any wording,
   while a projected uncertainty is released. (`F4`, `F5`; falsified by `F-I`.)
2. **A grade column reads "deferred"**, or `(cause 3, Z)` is presented as anything but non-passing.
   (`F14`.)
3. **Ruling 2's block set is defined by the computing function**, so that ~45 deterministic rank-one
   bands acquire `N = 2` disclosures. (`F7`.)
4. **"Verified" is silently resolved** in either direction without saying which reading is used.
   (`F9`.)
5. **One ensemble number is reported** where intended and achieved may differ, with no statement of
   which it is. (`F11`.)
6. **A requirement is dropped by category** with no check cited. (`F17`.)
7. **Inversion-grade criteria are imposed on endpoint A.** (`F18`.) This one blocks in the
   *permissive* direction and I am naming it explicitly so that an over-strict packet is not waved
   through merely because strictness is safe-looking. It is not safe: it makes an acceptable release
   unattainable before the stop.

A packet can be **READY** with `F9` open, provided it says which reading it is using and why. `F9` is
Joseph's to close, not the designer's and not mine.

---

## F.6 — INDEPENDENCE STATUS, RE-MEASURED

Part E recorded that supplying `D1`'s remedy cost this lane its independence for `D1`'s own fix.
Re-measured at `173baf44`: **the remedy is in the document as an adopted clause** — the retained-
subspace gate `‖P_0 − P_k‖_2 <= 1e-8` appears as terminal-outcome clause (d) at `:392` and again at
`:795`, with the derivation at `:889-892` and the attribution at `:204-210` labelled RELAYED. So
Part E's boundary is live and was honoured: I remain **non-independent for that clause** and do not
review it.

Two things have changed and both narrow the problem rather than widening it.

1. `:1234` records that the `1e-8` tolerance *"is not mine and was attacked"* by a third lane, and
   `:1190` reports a bidirectional redundancy measurement against it (`0 / 4000` unequal-rank pairs
   silent under the gate even with nested bases; `2000 / 2000` firing at equal rank with a different
   subspace). **My remedy was reviewed by someone else and tested in both directions.** That is the
   routing Part E asked for, done without my involvement.
2. The relay states the universal 5D bound is discontinued as the acceptance instrument. If that
   holds, clause (d) is not in the recommended gated set, and **my non-independence is moot for the
   recommended path while remaining live if the bound is adopted anyway.** I flag the conditional
   rather than declaring myself clear.

**Nothing in Part F is a remedy.** `F1`–`F21` are requirements and reserved questions; `F9` is
explicitly left unanswered where answering it would be a design choice. `F-I`, `F-II` and `F-0` are
findings, and the probe is a falsification instrument, not a proposed gate. This lane therefore
remains independent for the whole of the endpoint-A packet except clause (d) of the superseded
instrument.

## F.7 — WHAT I HAVE NOT MEASURED

Named so that no reader takes silence for coverage.

- **Whether `C5stat` as projected at `eavailW_covariance.py:441` is a block of Z**, and whether that
  2D consumer would be rebuilt from Z under endpoint A. `F-I`'s general form does not need this — it
  follows from "endpoint A releases projected uncertainties" alone — but the *attribution* of the
  hazard to `(cause 3, Z)` specifically does. Not settled here.
- **The real reported mask.** The `x5flat > 0` selection lives in a cluster product unreadable from
  this checkout, so the probe uses full support on a small grid plus the measured mean support as a
  scalar. The pigeonhole argument in §F.2 needs no mask.
- **The bodies of both `173baf44` artifacts**, deliberately (§F.0).
- **Whether any differently-worded record of Rulings 1 and 2 exists.** `F-0`'s phrase search is
  scoped to four phrasings; its filename check is not.
