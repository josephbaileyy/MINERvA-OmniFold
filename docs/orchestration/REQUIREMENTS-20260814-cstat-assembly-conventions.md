# REQUIREMENTS — what `C_stat` must look like to compose into the P5B assembly

**Author:** Lane B (Gate 6), **the sole builder** under `OI-121`. **Date:** 2026-08-14.
**Status:** INPUT TO LANE C'S SPEC. Written *before* any implementation, deliberately.

> **AMENDED 2026-08-14 — THE DUAL BUILD IS DROPPED. Joseph, verbatim: *"Okay yeah drop the second
> builder"*.** This document was written as builder 1's input to a two-builder design. **There is now
> one builder and there was never a second.** Four reasons, all measured: (1) lane D established that
> `Xc.T @ Xc` and `np.einsum` are **bitwise identical** because NumPy routes both to the same BLAS
> `dgemm` — reproduced independently by the mediator at `0.000e+00` (`BEN-188`); (2) C's spec pins
> `dof`, `centering`, `ravel_order` and member selection, which were the only decisions two builders
> could genuinely have diverged on; (3) both `codex` accounts are out of quota; and (4) **I had already
> read and quoted the in-tree recipe** (`combine_cstat_bkgsub.py:57-58`) in §0.3 while auditing for
> exactly this leak, so I cannot serve as an implementation independent of it.
>
> **WHAT THE RECEIPT MAY AND MAY NOT CLAIM — the part that outlives this decision.**
> **MAY:** spec conformance; a regression comparison against the established in-tree recipe; and that
> D's element-wise harness found no ordering or permutation defect — a real result, because D measured
> that a permutation is invisible to trace, to the eigenvalue spectrum, and to every structural
> property, and is caught **only** by per-cell comparison.
> **MAY NOT:** independent construction, independent verification, or that two implementations agreed.
> **They did not; there was one.** The two-builder machinery will remain in git history looking like it
> proved something, so **an ambiguous receipt will be read as the stronger claim.** State it in plain
> words.
>
> §0.3 below is retained unedited as the audit that produced reason (4). Its conclusion was right and
> its consequence was larger than I drew — it did not merely weaken the dual build, it disqualified me
> as its second arm.

**What this document is not.** It contains no covariance code and no implementation. Every convention
below is either (a) already fixed by a committed artifact or executable check, cited by file and line,
or (b) explicitly flagged as *not* fixed and therefore Joseph's or C's to decide. Precedent beats
preference, so where precedent exists I cite it and state no preference.

**Everything numeric here was measured this turn** from the tree at `037ecb4`. Nothing is from memory.

---

## §0 — Three answers up front, because each one saves a round trip

### 0.1 The bin count: the question has two candidate answers a factor of 40 apart, and the spec must pick one

The peer asked whether I know the bin count. I know two, and **which one applies is the first thing
the spec has to settle**, because it changes every downstream number:

| Candidate grid | Shape | Total cells | Reported | Where it is fixed |
|---|---|---|---|---|
| **2D extended FPS** | `(15, 19)` | **285** | **262** measured on the only committed PET extraction; **266** on the canonical lgbm mask | `fps_provenance.py:24-31`; `fullevent_fps_dataloader.py:64-69` |
| **5D corrected PET** | `(14,16,7,7,6)` | **65,856** | **10,550** | `assemble_ctotal_bkgsub.py:5,33` |

**The Gate-5 replicas being extracted right now are on the 2D grid, not the 5D one.**
`extract_fullevent_replica.py:305-318` writes `xsec`, `edges_pt`, `edges_pparallel` and calls
`total_xsec_2d`; there is no 5D product in that path. Measured from the only committed PET extraction
receipt (`fullevent_diagnostic_nonquotable/NONQUOTABLE-DIAGNOSTIC.xsec.slurm-56527676.summary.json`):

```
extraction/shape             = [15, 19]
extraction/n_cells           = 285
extraction/n_cells_populated = 262
extraction/n_cells_no_denominator = 23
extraction/bin_order = "pt-major row-major: cell = i_pt * n_pparallel_bins + i_pparallel"
```

**But the existing PET assembler expects the 5D mask.** `assemble_ctotal_bkgsub.py:25-26` requires each
component npz to carry `reported_mask` as a **65,856-length bool**. A 285-length mask will not load
through it. So one of these is true, and the spec must say which:

- **(a)** `C_stat` is a 2D component and **there is no 2D PET assembler in the tree** — I looked; the
  only two are `assemble_ctotal_bkgsub.py` (5D) and `assemble_cretrain.py`. Then P5B assembly item 5
  needs a new assembler and `C_stat` is its first client.
- **(b)** the replicas are to be re-extracted or projected onto the 5D grid, in which case the 285-bin
  extraction now running is not the `C_stat` input and the reported count is 10,550.

**I cannot establish which from the repo.** `PUBLICATION_COMPLETION_RUNBOOK.md:213-214` says *"Every
component uses the P5A central/mask/order"* — so the answer is *whatever P5A's mask is*, and **P5A's
committed reported-bin count is not in my tree.** That is a one-line lookup for whoever holds P5A.
**Needs: the P5A nominal extraction receipt's `n_cells_populated` and its grid shape.**

**262 ≠ 266, and that is not a rounding difference.** The canonical FPS mask is 266/285
(`fps_reported_mask.json`: `n_reported=266`, `ravel_order=C`, fingerprint `23b2a2f4…`) and is derived
from an **lgbm purity-control central** whose own manifest records
`publication_gate_rejects_this = true` (`fps_control_manifest.json`). The PET diagnostic excludes 23
cells, not 19. `285−266 = 19`, `285−262 = 23`, difference `4`, and the PET receipt independently
reports `n_cells_masked_zero_acceptance = 4` — **consistent with** the PET mask being the FPS mask
minus 4 more, but I had not verified nesting because the PET mask's indices were not recorded in any
committed artifact.

**NESTING NOW VERIFIED — by lane D, not by me.**
`COMPARATOR-PREDECLARATION-20260814-cstat.md:50-51` publishes the exact PET reported index set:
`[0..227] + [229..246] + [254..265] + [281..284]`. Complementing it against `0..284`:

```
PET excluded (23) = {228} u {247..253} u {266..280}
FPS excluded (19) =         {247..250} u {266..280}
FPS_excluded is a strict SUBSET of PET_excluded; the 4 extra are {228, 251, 252, 253}
```

So the PET reported domain **is** the FPS reported domain minus exactly 4 cells, matching
`n_cells_masked_zero_acceptance = 4` independently. My "do not assume it" is discharged. **The
requirement it produced is unchanged and D reached it independently:** *"Any reduction to 'the reported
cells' must be defined by a shipped boolean mask, never an index range"* (`:50-51`) — because the set is
contiguous only *within* each row, so two builders slicing by range will silently differ.

**Consequence, and this is a hard requirement:** `C_stat` must **NOT** call
`fps_provenance.require_reported_mask` (`fps_provenance.py:177-194`). That function hard-codes
`N_REPORTED = 266` (`:62`) and the canonical lgbm fingerprint (`:61`) and **fails closed on anything
else** — including a correct PET mask. It is the FPS-lgbm lateral chain's gate, not P5B's. Adjacent
trap: `mask_hash` and `mask_fingerprint` (`:161`, `:168`) are two different functions returning
different strings for the same mask (`mask_hash` appends `:n266/285`). A builder that picks the wrong
one gets a plausible hex string that binds nothing.

### 0.2 The rank question — CLOSED. Read this section as the derivation of a settled answer, not an open item

> **CLOSED 2026-08-14.** It was predeclared before launch
> (`PREDECLARATION-20260813-gate5-coherent-replicas-n50.md`: *"Rank is not the criterion"*), the
> ~~treatment is field-normal for multisim covariances~~ **[RETRACTED — see below]**, and the number that settled it is the trace
> fraction in point 3 below: **`C_stat` + `C_ML` + norm are 0.323% of the total variance trace.** Do not
> re-open it. What follows is the derivation, kept because a settled answer with no recoverable
> derivation is the thing this repo keeps having to rebuild.
>
> **RETRACTION, 2026-08-14 — the external-precedent clause above was FALSE and I repeated it from a
> relay without checking a single paper.** The mediator relayed that rank-deficient covariances are
> field-normal, that MINERvA releases them as-calculated, and that ~100/~50 universes are typical. It
> then checked the actual sources and **none of it is supported**: one citation was the wrong paper
> entirely; the MINERvA toolkit paper contains **zero** occurrences of `rank`, `singular`, `invert` or
> `regulari`; and **Hartlap 2007 argues the opposite** — it is the canonical proof that a sample
> covariance is singular when `P > N`, so beside our matrix it is evidence *against* comfort, not for it.
>
> **The closure is unaffected and that is the point worth keeping.** §0.2 rests on our own
> predeclaration and on the 0.323% trace fraction, **neither of which ever depended on outside
> precedent** — which is why the false clause could be deleted without touching the conclusion. What is
> gone is only the reassurance that everyone else does this too. A measurement of a real released
> MINERvA covariance is running to settle it properly.
>
> **Why this is struck in place rather than removed:** I accepted a comforting external claim into a
> document whose every other number I had measured myself, and the clause's only function was
> reassurance. **A claim that does no work in an argument is the one least likely to be checked** — and
> it is the third time today this lane has recorded something on the strength of a relay rather than a
> read (`BEN-241` a document, `BEN-243` an objection, this a citation). Same operation, third object.

The peer flagged: 50 replicas ⇒ rank ≤ 49; if bins > 49 the matrix is singular. **It is singular, by a
wide margin, and the repo already knows.**

Arithmetic, on the 2D reading (`n_rep = 50`, mean-centred so `dof = 49`):

```
rank(C_stat) <= n_rep - 1        = 49
reported bins                    = 262      (measured, §0.1)
null space                       = 262 - 49 = 213    -> 81.30% of the space
```

On the 5D reading it is far worse: `10550 − 49 = 10501`, **99.54%** null.

**The repo states this as a construction property, not a defect.** `combine_cstat_bkgsub_100rep.py:90-93`:

> *"`C = Z^T Z / (n-1)` is a Gram matrix, so its nonzero spectrum equals that of the small
> `n_rep x n_rep` Gram `G = Z Z^T / (n-1)`; PSD is verified from `G` (**full-space min eig = 0 by
> construction**)."*

**Three reasons this does not block construction:**

1. **Singularity is a property of the consumer, not the constructor.** A rank-49 `C_stat` is the
   *correct* object — it is exactly what 50 replicas support. The declared treatment is needed before
   the first **inversion**, which is P6 (`RUNBOOK:246-250`), not P5B.
2. **The declared treatment already exists and is named.** `COLLABORATOR_QUESTIONS.md:36-42` — a
   **truncated-spectral pseudo-inverse retaining `λ > 1e-10 λ_max`** — used at **rank 201 of 205** in
   2D and **rank 247 of 1431** in 3D. `:131-136` records it **CONFIRMED: the collaboration does the
   same truncated-spectral pseudo-inverse.** What is still owed under `OI-29` is endorsement of
   *publishing the full 1431-bin covariance*, not the GoF method.
3. **`C_stat` is not the object whose rank governs the total, and its magnitude is sub-percent.**
   `VALIDATION_LEDGER.md:1289-1295`, the canonical entry for the **adopted FPS 2D covariance on this
   very 266-bin grid**:

   ```
   C_syst block-sum          rank 144/266   median 7.27%/bin   sqrt-tr 8.027e-39
     + norm  1.4%
     + C_stat 0.669%  (100 bootstraps)
     + C_ML   0.357%  (24 splits)
   = combined                rank 222/266   median 7.33%/bin   sqrt-tr 8.040e-39
   adopted final: median 8.19%/bin, PSD exact, 0 negative eigenvalues
   ```

   Two things follow. **`C_syst` is not full rank either** — 144 of 266, 54.1% — so a rank-49
   `C_stat` is not being added to a full-rank object; component ranks add, and the accounting closes
   (`144 + 99 + 23 + 1 = 267 >= 266`, realized 222). And from the two published sqrt-traces:

   ```
   (8.040e-39)^2 - (8.027e-39)^2
   -----------------------------  =  0.00323  ->  0.323%
         (8.040e-39)^2
   ```

   **`C_stat` + `C_ML` + norm are together 0.323% of the total variance trace; `C_syst` is the other
   99.68%.** Per-bin, `C_stat` 0.669% against `C_syst` 7.27% is a factor of **10.9**.

   *Ingredient that does not close, per `CONVENTION-receipt-ingredients` (BEN-077):*
   `sqrt(7.27² + 1.4² + 0.669² + 0.357²) = 7.4423`, **not** the published `7.33`. Expected — these
   are medians of per-bin fractions and medians are not additive in quadrature — but it means the
   0.323% must be derived from the traces. **Do not quote a median-quadrature decomposition.**

   Regime comparison, so "unprecedented" is not claimed where it is false:

   ```
   2D paper GoF          201/205   = 98.0%
   FPS 2D adopted        222/266   = 83.5%
   3D adopted (OI-29)    247/1431  = 17.3%   <- same regime as ours
   Gate-5 C_stat alone    49/262   = 18.7%
   PET 5D status quo      19/10550 =  0.2%   (20-replica product, 100rep:24-26)
   ```

   **Precedented but unendorsed**, not unprecedented — and `OI-29` is the row that already holds it.

**So my recommendation — C's and Joseph's to accept or reject — is that the singularity is not a
pre-construction blocker and both builders should proceed.** What *is* a genuine pre-construction
decision is in §0.3 and §9.1.

**One thing the spec must nevertheless state, because two existing gates will pass a rank-49 matrix
silently:**

- `assemble_ctotal_bkgsub.py:66` — `psd_within_tol = ev.min() >= -1e-12 * max_eig`. An exact-zero
  eigenvalue satisfies this. It is a **negativity** gate, not a **rank** gate.
- `p4_validate_active_lateral_fps.py:68` — same relative form; and `:71` sets
  `n_reported = sum(diag > 0)`, which for a rank-49 matrix still reads **262**, because a
  rank-deficient covariance can have a strictly positive diagonal.

Both will report PASS. The rank must therefore be **declared and recorded by the builder**, not left
to be caught downstream. Note `p4_validate_active_lateral_fps.py:67` *does* record
`min_over_max_eig` — the evidence gets written, only the threshold is missing. **Both arms of that
validator's defect are now filed as `ISSUE-46`** (`docs/known-issues/`), so they no longer live only in
this document; the fix is a threshold decision for that file's owner, not a mechanical edit, and not
mine.

**And one live inconsistency worth C's attention:** the declared threshold is `1e-10 λ_max`
(`COLLABORATOR_QUESTIONS.md:38-39`), but `_ours_only_chi2.py:123` reports rank at `1e-12 λ_max` and
`compare_to_paper_fullcov.py:103` uses bare `np.linalg.pinv` at numpy's default rcond. I am **not**
calling those defects: `_ours_only_chi2.py:5-7` says in its own docstring it is a *quick* diagnostic
using a direct inverse, and `compare_to_paper_fullcov.py` compares against the *paper's* covariance,
for which `ndf = n_keep` (`:106`) may well be right. The point is narrower and it is load-bearing:
**`receipt_model_chi2_2d.py:32-35` justifies `ndf = n_reported` by a measured rank-truncation scan and
states the condition — *"effective rank is not far below `n_reported`"* (rank 204/205). That condition
is FALSE at 49/262.** The existing justification names the premise that fails here, so `ndf = n_reported`
cannot be inherited into P5B by precedent. That is the cleanest statement of the blocking question, and
it is the repo's own sentence, not mine.

### 0.3 A prior PET `C_stat` implementation exists in the tree — this is a second independence leak

`OI-121` identifies one leak (both lanes push to `main`, so builder 2 could read builder 1). **There is
a second, and it is already present at whatever commit builder 2 is pinned to:**

- `nd-unfolding/pet/combine_cstat_bkgsub.py` — Phase-4 PET `C_stat`, replica-mean-centred, CV>0 mask.
- `nd-unfolding/pet/combine_cstat_bkgsub_100rep.py` — the 100-replica extension with a gate battery.
- `nd-unfolding/replica_manifest.py:12` — `load_replica_manifest`, the strict inventory loader that
  already implements `RUNBOOK:220`'s *"reject incomplete inventories"*.

The core recipe is two lines, and **it appears identically in two independent files**:

```
combine_cstat_bkgsub.py:57-58     Z = Xr - Xr.mean(0)  ;  C = (Z.T @ Z) / (Xr.shape[0] - 1)
combine_seedscan_split.py:65,68   mean = Xr.mean(axis=0)  ;  cov = (Z.T @ Z) / (Xr.shape[0] - 1)
```

**Both builders will find this.** "Two implementations written blind to each other" then means "two
lanes that both read `combine_cstat_bkgsub.py`", and the agreement `OI-121` wants to buy is
substantially pre-purchased. I am raising it rather than working around it, because the workaround
("don't read it") is unenforceable and unverifiable.

**My recommendation, C's to accept or reject:** treat the two-line sample-covariance recipe as **fixed
precedent that both builders adopt**, and point the independence at what is actually new and where the
errors actually live — the Gate-5 coherent-replica contract (`RUNBOOK:216-220`: complete draws before
subsetting, background factors before per-replica Stay-Positive, exact applicable MC/background factors
in training *and* extraction, persisted replay evidence), the mask/central binding, and the embedding
back to the full grid. Agreement on `(Z.T @ Z)/(n-1)` is worth almost nothing; agreement on *which
rows go into `X` and on which mask* is worth a great deal.

**And lane D has since measured the stronger version of this, which is worth more than my argument.**
`BEN-188`: calibrating the comparator across four legitimate routes to one sample covariance, worst
disagreement was `6.26e-16` — but **`Xc.T @ Xc` versus `np.einsum` was exactly `0.000e+00`, bit for
bit, because both dispatch to the same BLAS kernel.** So perfect agreement between two implementations
is achievable with **no independence at all**, while reading as the strongest evidence in the campaign.
D's formulation is the one to adopt: **establish that two COMPUTATIONS occurred, not two authors.**
This makes the reconciliation above not merely preferable but necessary — if the two builders agree on
the covariance kernel to `0.000e+00`, that number is evidence about BLAS, not about the spec.

### 0.4 What actually consumes `C_stat` — enumerated, because the severity of §0.2 is conditional on it

**Nothing in the repo inverts `C_stat` alone. Zero sites.** Every consumer of `C_stat` /
`hCov_stat*_reported` / `pet_cstat_bkgsub_5d.npz` falls into one of three kinds:

| Kind | Site | What it does |
|---|---|---|
| **Diagonal only** | `coverage_valid_nd.py:44-53` | `_load_cov_diag` reads literally `GetBinContent(i+1, i+1)`; `:9` — *"sigma_i = sqrt(diag(C)) from an INDEPENDENTLY estimated covariance (C_stat …)"* |
| **Diagonal only** | `pet_lateral_correction.py:142-146` | per component: `sqrt(trace)` and median `sqrt(diag)/base`. No inverse in the file |
| **Sum / identity** | `pet/assemble_ctotal_bkgsub.py:4-5` | `C_total = C_syst + C_stat + C_ml + C_retrain (+ C_lateral)` |
| **Sum / identity** | `pet_lateral_correction.py:125-127` | `C_total = C_syst + C_stat + C_ML + C_pet_lat` |
| **Sum / identity** | `p4_build_components.py:121,136,145`; `p4_validate_active_lateral.py:196-199` | addition identities to `1e-9`; no inversion |
| **Projection** | `eavailW_covariance.py:365` | `M C Mᵀ`. Projection, not inversion |
| **Inversion — of the TOTAL only** | `compare_to_paper_fullcov.py:103,124`; `receipt_model_chi2_2d.py`; `uq/_ours_only_chi2.py:127` | the GoF consumers |

So `C_stat`'s rank matters **only** through the total, and the total's rank is governed by `C_syst`
(§0.2). The **published per-bin error bars are unaffected by rank at any level** — each of the ~262
diagonal variances has all 50 samples behind it, at a 10.10% relative SE (§7).

**The one real concern, stated so it is not mistaken for a pathology:** in a direction where `C_stat`
has no information, the total's variance there is `C_syst`'s. That is not a silent fill-in — it is
what a sum of covariances means, and a GoF in such a direction is testing the systematic rather than
the statistical uncertainty. Since `C_syst` is 10.9× larger per-bin anyway, the inverse is not
materially different from what it would be with a full-rank `C_stat`.

### 0.5 The inventory size: two live predeclarations disagree, and neither retires the other

**Correction to an earlier draft of this document, kept visible because it is the more instructive
half.** I wrote that *"I can find no committed predeclaration of 50 anywhere in the tree"* and called
that the blocking question. **That was wrong.** `PREDECLARATION-20260813-gate5-coherent-replicas-n50.md`
exists, committed in `6bd3707`, and is cited from `docs/OPEN_ITEMS.md:111` (OI-55) — a row in a file I
was already reading. Its first line: *"Written before any replica is submitted, and before the replica
code path exists. Nothing here was chosen after seeing a spread."* Joseph's verbatim authorization is
**"sounds good, get N=50 up and running"**, and it **already disposes of the rank question**:

> *"Rank is not the criterion — 1431 bins is unreachable at any affordable N, and the rank-deficient GoF
> treatment is already disclosed under `OI-29`. The criterion is precision on a subdominant component:
> the fractional uncertainty on an estimated standard deviation is `1/√(2(N−1))`, giving 10.1% at N=50
> against a model-dominated systematic budget. N=100 buys 7.1% for double the compute, on a term that is
> not driving the total."*

with its arithmetic verified in-document (`1/√(2·49) = 0.10102`, `1/√(2·99) = 0.07107`) — the same
`0.10102` I derived independently in §7, arrived at from the other direction. **So N=50 was predeclared,
reasoned on a stated precision criterion, and authorized, all before any spread was observable. The
prohibited order of operations did NOT happen, and §0.2's rank framing was already settled here.**

**The generalisable error:** an absence claim needs a stated search that would have found the thing. I
had `grep`-shaped evidence for a filename containing `n50`, linked from the file I was in.

**What is real, and it is the opposite direction.**
`PREDECLARATION-20260812-fullevent-cstat-100-replicas.md` is **also committed and also live**, and it
is stronger than merely unretired:

- `:52-53` — *"`n_replicas = 100`, declared **before** any is drawn. The number is not to be revised
  downward on observing the spread; if 100 proves unaffordable the run is **not** shipped at 60 with a
  [caveat]."*
- `:73` — its predeclared verdict clause: **`INSUFFICIENT` — "fewer than 100 complete manifests at
  assembly. Not repaired by rescaling."**
- `:79` — `PASS` requires *"100 complete."*
- `:3-8` — its own authority is a **Joseph** quotation from 2026-08-12: *"Predeclare and run 100
  replicas for the eventual full-event publication `C_stat`."*

**I searched the N=50 document for a supersession reference to the N=100 one and found none** (`grep -i
"supersed|retire|replaces"` returns nothing). So: **two committed predeclarations, two Joseph
authorizations a day apart, two different N, and no supersession chain between them — and the older
one's live verdict rule labels a 50-replica product `INSUFFICIENT`.**

One measured ingredient bearing on the older document's own escape clause, offered because it is
derivable and neither document uses it: N=100's cost basis was *"~1.2 h each"*
(`FULL_EVENT_FEATURE_CONTRACT.md:233`, cited at `:93`), against a measured **3.02 h** (Gate 5 mean,
n=35) and **3.24 h** (Leg F draws) — a **2.5×** overrun, so *"if 100 proves unaffordable"* is live on
measurement. Whether that satisfies the clause or trips its *"not shipped at 60 with a caveat"*
prohibition is **exactly the ratification I am not making.**

**This is a documentation repair, and the ratification is Joseph's. I have not written the supersession
and will not.** See §9.1.

---

## §1 — Bin ordering and the exact binning

**FIXED BY PRECEDENT. Do not re-derive; adopt and bind.**

1. **Ravel order is C**, and this is independently asserted in two places that were written by
   different paths:
   - `fps_provenance.py:31` — `RAVEL_ORDER = "C"`; `fps_reported_mask.json` — `ravel_order: "C"`.
   - the PET extractor writes its own order string, `extract_fullevent_fps.py:556` —
     *"pt-major row-major: cell = i_pt * n_pparallel_bins + i_pparallel"*, which is C-order for
     `(pt, pparallel)`.

   These agree. **`C_stat` must record the order string it used**, so a future reader can falsify the
   agreement rather than trust it.

2. **The 2D grid is the canonical extended FPS grid, not the paper grid.** 16 pt edges → 15 bins,
   20 p∥ edges → 19 bins, 285 cells (`fps_provenance.py:24-30`;
   `fullevent_fps_dataloader.py:64-69`). The PET loader **fails closed on the paper grid**:
   `assert_extended_fps_edges` (`fullevent_fps_dataloader.py:102-125`) rejects a 4.5 GeV pT top edge
   and a 1.5 GeV p∥ bottom edge explicitly, so supplying the paper's 14×16 raises rather than silently
   measuring a restricted domain. **`C_stat` must pass this check on the edges it carries.**

3. **`C_stat` must carry `layout_fingerprint`** (`fps_provenance.py:153-162`) — a sha256 over the exact
   edges, `npt`, `npz`, `nbins`, and `ravel_order`. This is the mechanism that makes a silent reshape
   impossible. The canonical 2D value in the tree is
   `53119a407987c3b65911581ead7701b6a12d10742c6156682603a30da80a97fe`.

4. **`C_stat` must NOT hard-code a reported count and must NOT call `require_reported_mask`** — §0.1.

5. **The reported mask is adopted, not defined.** The PET reporting rule is
   `extract_fullevent_fps.py:517-519`: `reported = comp > 0`, with `xsec` zeroed outside it.
   `RUNBOOK:213-214` makes P5A the authority. `C_stat` must **bind** the mask (carry it plus the sha256
   of the central it came from) and must **refuse** if the replicas' own CV>0 pattern differs from the
   bound mask, rather than intersecting them — an intersection would let a bad replica shrink the
   reported domain.

---

## §2 — Units, and absolute vs fractional

**FIXED. `C_stat` is ABSOLUTE, in the square of the differential cross-section unit.**

1. **The per-bin quantity is a DENSITY, not a bin-integrated number.** `total_xsec_2d`
   (`extract_fullevent_fps.py:561-565`) integrates with `dpt[:,None] * dpp[None,:]`, so `xsec` is
   `d²σ/dp_T dp_∥`. Units: **cm² / nucleon / (GeV/c)²**. The 5D assembler says the same for its grid —
   *"the PET xsec is a density `d^5sigma/prod dx_a`"* (`assemble_ctotal_bkgsub.py:6-7`).

2. **`C_stat` is therefore in (cm²/nucleon/(GeV/c)²)²**, i.e. `~1e-76` for a `~1e-38` cross section.
   Absolute, never fractional.

3. **Bin volume must NOT be applied by the component.** It is applied *only* by the consumer that
   integrates or projects — `total_xsec_2d` for a total, and the `dW` column of the projection matrix
   for a marginal (`assemble_ctotal_bkgsub.py:36-56`). A component that pre-multiplied by bin volume
   would be double-counted at projection time, and nothing in the chain would catch it because the
   result would still be finite, symmetric and PSD.

4. **Fractional forms are diagnostics only, computed by the reader.** Precedent:
   `combine_seedscan_split.py:70-71` computes `rel = diag/cv_rep` purely to print, and the stored
   object stays absolute. **This is why the component must ship its `cv`** — a fractional covariance
   cannot be re-absolutised by a downstream reader who does not have the exact central.

5. **A tolerance warning that has already fired once in this repo, quoted because it applies directly
   here.** `combine_cstat_bkgsub_100rep.py:20-22` records *"the `atol=1e-8` default measured against
   cross sections of ~1e-38 … an absolute tolerance inherited into a problem whose natural scale is
   ~1e-80."* **Every tolerance in `C_stat` must be relative, or its absolute scale must be stated
   against `1e-76`.**

---

## §3 — Shape, dtype, and the artifact contract

**LARGELY FIXED by `assemble_ctotal_bkgsub.py:24-26`. The component npz carries `C_*`,
`reported_mask` (full-grid bool), and `cv` (full-grid flat central).**

Required, with the reason each one is required:

| Field | Form | Why |
|---|---|---|
| `C_stat` | dense `float64`, `(n_reported, n_reported)`, on the **reported sub-space** | matches every existing component; `float64` throughout (`extract_fullevent_replica.py:186-187,291`; TH2D is double) |
| `reported_mask` | `bool`, **full grid length** (285 or 65856), C-order | the assembler compares masks by `np.array_equal` (`assemble_ctotal_bkgsub.py:106`), so it must be the full-grid mask, not the compressed index list |
| `cv` | `float64`, full grid, flat | absolutisation (§2.4) and the common-central check (`:108-113`) |
| `edges_pt`, `edges_pparallel` | `float64` | so `assert_extended_fps_edges` can be re-run by any reader |
| `layout_fingerprint` | 64-hex | §1.3 |
| `central_sha256` | 64-hex | binds the mask to the central that defined it |
| `n_replicas`, `replica_ids` | int, int array | inventory completeness is auditable; precedent `combine_cstat_bkgsub.py:68,72` |
| `n_reported` | int, **declared from the mask** | **NEVER inferred from `diag > 0`.** `p4_validate_active_lateral_fps.py:72` does infer it that way, and a reported cell with zero replica variance (all 50 draws identical — possible in a low-occupancy cell) then silently undercounts. See §3.1 |
| `dof` | int, `= n_replicas - 1` | the rank bound is stated, not inferred |
| `rank_at_1em10_lambda_max` | int | §0.2 — the declared threshold, recorded so the consumer need not rediscover it |
| `ravel_order` | `"C"` | §1.1 |
| `centering` | string, `"replica_mean"` | §5 |
| `units` | string | §2 |
| **`asymmetry_before_symmetrisation`** | float | **REQUIRED, promoted by C on D's catch.** "Symmetrise, then check symmetry" is **vacuous** — post-symmetrisation every artifact passes by construction. The *pre*-symmetrisation value is the only informative one: `~1e-16` is healthy, `1e-9` means a plumbing defect nothing downstream can see |
| **`member_sha256`** | list of 50 hex digests | **REQUIRED, not optional.** The digest of each `GATE5_REPLICA_XSEC.npz` actually read. **`replica_ids` proves what you believe you used; digests prove what you read.** Live reason: the failed r1 array `56935552` and the live r2 array `56936015` **write to the same output root**. Nothing is contaminated (r1 died before writing any product; the directory holds 17 products, all in r2's window) — but a glob would have taken r1's output had it existed |

**Symmetry.** `(Z.T @ Z)` is symmetric up to floating-point summation order only. The existing gates
demand `rel_asymmetry <= 1e-9` (`p4_validate_active_lateral_fps.py:66,123`) and
`|C − Cᵀ|max < 1e-9` (`test_pet_assembly.py:46`). **Symmetrise explicitly and record the asymmetry
you symmetrised away** — a value far above `1e-9` before symmetrisation is evidence of a real bug that
symmetrising hides.

**What is NOT fixed and I will not invent:** whether the deliverable is npz (PET convention) or ROOT
TH2D (the FPS/GBDT convention, `combine_seedscan_split.py:99`, hist name suffix `_reported`). The PET
chain is npz and pure-numpy login-node-runnable, which I'd prefer for a dual-build comparison because
element-wise comparison by D is trivial on npz and needs ROOT on TH2D. **C's call.**

### 3.1 A REAL DISAGREEMENT with lane D's comparator predeclaration — **OPEN, awaiting C's ruling**

> **STATUS: OPEN.** An earlier revision of this section recorded it as *"resolved-not-adopted"* in
> favour of `(n_reported, n_reported)`, on the basis that D was realigning its harness. **That was D's
> position for about twenty minutes and I should not have written its epitaph.** Retracting a premature
> closure is cheaper than defending one, and this is the second time today I have asserted something
> settled that was not (`BEN-241` was the first, and both share a shape: **I treated the absence of a
> visible counter-position as a resolution**).
>
> **THERE ARE NOW THREE PROPOSALS, and the third is the mediator's recommendation to C:**
>
> | # | Proposal | Origin |
> |---|---|---|
> | 1 | `(n_reported, n_reported)` only | this document's §3, and every existing component |
> | 2 | `(285,285)` + boolean mask only | D's comparator predeclaration `:168` |
> | 3 | **BOTH** — `(285,285)` + mask **and** the reduced `(n_reported, n_reported)` derived from it | D, on reconsideration; endorsed by the mediator |
>
> **D's argument for (3) is correct and it is the one that should decide this.** If only the full form
> is compared while the *published* object is the reduced one, **the reduction is verified by nobody** —
> and the reduction is precisely the operation D and I independently identified as error-prone, because
> the reported set is contiguous only within rows. *"The comparison passed"* would then be a true
> statement about an object that is not the deliverable. That is `BEN-185`'s shape exactly: a property
> proved on the wrong object, reported inside a passing suite.
>
> **Recorded because it bears on how D's input should be weighted:** D disclosed unprompted that its
> harness was already written for `(285,285)`, so it is **not neutral** on this question — and then
> argued for the option that costs it rework, on the ground that *"the published object should be the
> verified object, and my convenience is not a reason to verify the intermediate instead."* An interest
> declared and then argued against is stronger evidence than a position with no interest at all.
>
> **MY ONE ADDITION, because emitting both is necessary and not yet sufficient.** Shipping two arrays
> does not by itself verify their *relationship*; it verifies each against whatever reference the
> comparator has. The check that makes (3) pay for itself is an **exact, bit-identical internal
> consistency assertion inside the artifact's own gates**:
>
> ```
> C_reduced  ==  C_full[np.ix_(mask, mask)]        exactly, not to a tolerance
> ```
>
> Three reasons it must be bit-identical rather than `allclose`: it is a pure gather with no arithmetic,
> so any difference at all is a defect and not float noise; it needs no reference artifact, so it has
> power even if the regression comparison is unavailable; and it is the *only* check that fires on the
> specific failure D named — a correct full matrix reduced through a wrong index set. **A tolerance here
> would convert the one exact check in the chain into an approximate one**, which is the family the repo
> already recorded when an `atol=1e-8` default met cross sections of `~1e-38`
> (`combine_cstat_bkgsub_100rep.py:20-22`).
>
> **And one trap that (3) creates, which I would not have seen under (1) or (2).** With a reduced form in
> play, `n_reported` becomes inferrable from the diagonal — and an existing validator already does
> exactly that: `p4_validate_active_lateral_fps.py:72` sets `n_reported = int(np.sum(d > 0))`. **That is
> not the reported-bin count.** A cell can be *reported* (`comp > 0`) and still have **zero replica
> variance** if all 50 draws land on the same value, which is not impossible in a low-occupancy cell; its
> diagonal entry is then `0.0` and the inferred `n_reported` silently undercounts. **`n_reported` must be
> read from the shipped mask and declared, never inferred from `diag > 0`** — and a zero on the reduced
> diagonal is a fact to report, not a cell to drop.
>
> **The requirement that survives under all three proposals is D's, not mine:** the reduction must be
> expressed by a **shipped boolean mask, never an index range** (`:50-51`). And **`BEN-189` bites on any
> full-grid form** — relative eigenvalue metrics divide `~1e-18` by `~1e-18` there and return `~1.0` for
> any input, so absolute-scaled-by `|λ_max|` is the only correct form on the `(285,285)` array.
>
> **Whether §3.1 came out my way is not the point and I have no preference to defend here.** (3) is
> better than my (1) on the merits: it keeps the single well-defined comparison dimension I argued for,
> keeps the assembler's no-translation-step property C needs, and puts the error-prone step inside the
> verified scope — for one numpy line and ~650 KB. **C rules; I will diff the spec against this section
> and report before writing code.**



The table above says the component lives on the **reported sub-space**,
`(n_reported, n_reported)`, because that is what every existing component is and what
`assemble_ctotal_bkgsub.py` consumes. **Lane D's `COMPARATOR-PREDECLARATION-20260814-cstat.md:168`
requires the compared artifact to be shape `(285,285)`** — the full grid — with the reduction expressed
by a shipped boolean mask, on the sound reasoning at `:184-185` that the extractor already writes hard
`0.0` outside the mask (`extract_fullevent_fps.py:517-518`) so the full matrix carries an explicit zero
block. **Both conventions are defensible and they are not the same artifact.** Left unresolved, the
comparator and the assembler want different objects and one of them gets a reshape — which is exactly
the translation step `OI-121` put me on this task to eliminate.

**Proposed reconciliation, C's to accept or reject:** builders emit **`(285,285)` plus the full-grid
boolean `reported_mask`** — D's convention wins at the comparison boundary because the comparator is
the immediate consumer and a fixed dimension makes element-wise comparison well-defined — and the
**reduction to `(n_reported, n_reported)` happens once, in the assembly step, not in either builder.**
That keeps a single reduction site instead of two, and it is the one place the mask-equality gate
(`assemble_ctotal_bkgsub.py:105-107`) can enforce agreement. **What must NOT happen is each builder
reducing independently**, per D's own `:50-51` warning about slicing a set that is contiguous only
within rows.

**One consequence to declare explicitly if `(285,285)` is adopted:** the 23 all-zero rows/columns are
structural, so a naive rank count returns ≤ 49 out of 285 and `min_over_max_eig` is exactly 0 — and
`BEN-189` (lane D, same work) shows a *relative* eigenvalue metric then divides ~1e-18 by ~1e-18 and
returns ~1.0 for **any** input, including a permutation that provably preserves the spectrum. **On this
object, relative tolerances are noise; absolute-scaled-by `|λ_max|` is the correct form.** D measured
236 numerically-zero eigenvalues of 285, which is `285 − 49` exactly and corroborates §0.2's arithmetic
from the opposite direction.

---

## §4 — How components are summed, and what that requires of each one

**Summation is PURE ADDITION on one common mask and order.** `assemble_ctotal_bkgsub.py:4-5`:
`C_total = C_syst + C_stat + C_ml + C_retrain (+ C_lateral)`. Same for the GBDT chain
(`assemble_gbdt5d_adopted.py:4-20`, *"All inputs are TH2D on the SAME … CV>0 reported ordering"*).

What pure addition **requires of `C_stat`**:

1. **Bit-identical mask.** `assemble_ctotal_bkgsub.py:105-107` fails closed on
   `not np.array_equal(m, ref_mask)` with *"common-mask violation"*. The reference is **`C_syst`'s**
   mask (`:104`) — so `C_stat` is a mask *consumer*. It does not get to define the reported domain.
2. **Same central.** `:108-113` checks `cv` against `C_syst`'s. **Note this is a `[warn]`, not a
   failure** — the one place in the chain where a real mismatch would print and proceed. `C_stat`
   should carry `central_sha256` so a reader can turn that warning into a check.
3. **Same units and same embedding** — §2. Nothing enforces this; it is why `units` is a required field.
4. **A declared rank and dof**, so the total's rank is *derivable from the components* rather than
   discovered at inversion. Ranks add: `rank(C_total) <= Σ rank(C_i)`, and this is how the GBDT chain's
   222/266 arises (§0.2). **`C_syst` is itself a sample covariance, so its rank is bounded by the
   throw/universe count and not by the nuisance count** — `unified_throw.py:391`,
   `C_uni = (Z.T @ Z)/(Xr.shape[0]-1)` over `T` throws (`T = 160` for the adopted 5D product).

   **A bound is not a realization, and I will not present one as the other.** The GBDT sweep's **187
   universes realized rank 144** — 77% of the bound. My `C_syst` scoping (`3e59c91`) puts the PET
   vertical inventory at **124 endpoints**, so `rank(C_syst^PET) <= 124 < 144`, and the PET total will
   therefore be **more** rank-deficient than the adopted GBDT one regardless of what `C_stat` does. I
   have **not** computed a PET-specific realized rank, because a 77% realization measured on one
   universe set does not transfer to another. **Needs: the PET vertical sweep, which does not exist.**
5. **Explicit non-overlap with the sibling it is most easily double-counted against.** The precedent
   for how to discharge this is `assemble_ctotal_bkgsub.py:10-22`, which proves
   `C_syst + C_retrain` is disjoint by showing `Δ_u = x_retrain(r_u) − x_frozen(r_u)` subtracts the
   very quantity `C_syst` varies. `C_stat` needs the analogous one-paragraph argument against `C_ML`:
   **`C_stat` varies the Poisson draw at fixed seed policy, `C_ML` varies the seed at fixed data
   (`RUNBOOK:224` — "no Poisson variation")**. That is a clean factorisation *if* the replica jobs hold
   the seed policy fixed, and the spec should require the receipt to show it rather than assert it.
6. **`RUNBOOK:243` — "There is no standalone additive `C_retrain` block."** `C_stat` must not
   reintroduce one by a side door.

Assembly-level checks `C_stat` must survive (`RUNBOOK:233-235`): exact component reconstruction, mean
shifts, symmetry, PSD/eigen diagnostics, finite diagonal, exact marginal checks. Plus the adopter's
**measured** identities: `p4_adopt_standard.py:62-67` requires
`C_combined_eq_syst_stat_ml_relerr` and `full_total_residual_eq_stat_plus_ml_relerr` to be recorded as
**measurements** and `<= identity_rtol` (default `1e-9`). Read `:52-58` for why: that gate previously
read a self-asserted literal `True` and *"the strictest gate in the chain was reading a constant and
calling it evidence."* **`C_stat` must therefore be reconstructible from the total by subtraction to
`1e-9` relative — which in practice means it must be stored, not regenerated.**

---

## §5 — Centring and the denominator

**FIXED, and by the runbook itself rather than by inference.**

1. **Centre on the replica mean.** `RUNBOOK:220` — *"Center on the replica mean."* Precedent agrees:
   `combine_cstat_bkgsub.py:57` (`# replica-mean-centered`), `combine_seedscan_split.py:65`.
   Do **not** centre on the frozen CV.
2. **Denominator `n − 1`** (unbiased). `combine_cstat_bkgsub.py:58`, `combine_seedscan_split.py:68`.
3. **The mean-vs-CV shift is REPORTED, not absorbed.** `combine_seedscan_split.py:75-79` computes
   `(mean − cv_rep)/cv_rep` and prints median and max. `RUNBOOK:234` lists *"mean shifts"* among the
   assembly requirements. **So the replica-mean-minus-central shift is a required output field of
   `C_stat`, not an internal diagnostic** — if the replica mean has moved off the central, that is a
   finding about the central, and folding it into the covariance would hide it.

---

## §6 — Precedent index

Every convention above, with its authority. Precedent beats preference; where a row says
NOT FIXED, I am not supplying a preference.

| Convention | Fixed by | Line |
|---|---|---|
| Ravel order `C` | `nd-unfolding/fps_provenance.py` | 31 |
| Ravel order `C` (independent) | `nd-unfolding/pet/extract_fullevent_fps.py` | 556 |
| 2D grid 15×19 = 285 | `nd-unfolding/fps_provenance.py` | 24-30 |
| 2D grid, PET copy | `nd-unfolding/pet/fullevent_fps_dataloader.py` | 64-69 |
| Paper-grid rejection (fail-closed) | `nd-unfolding/pet/fullevent_fps_dataloader.py` | 102-125 |
| `layout_fingerprint` | `nd-unfolding/fps_provenance.py` | 153-162 |
| lgbm mask is 266/285 and NOT ours | `nd-unfolding/fps_provenance.py` | 61-62, 177-194 |
| PET reporting rule `comp > 0` | `nd-unfolding/pet/extract_fullevent_fps.py` | 517-519 |
| xsec is a density; volume applied at integration | `nd-unfolding/pet/extract_fullevent_fps.py` | 561-565 |
| Component npz contract | `nd-unfolding/pet/assemble_ctotal_bkgsub.py` | 24-26 |
| Common-mask fail-closed | `nd-unfolding/pet/assemble_ctotal_bkgsub.py` | 105-107 |
| Common-central (warn only) | `nd-unfolding/pet/assemble_ctotal_bkgsub.py` | 108-113 |
| Pure addition | `nd-unfolding/pet/assemble_ctotal_bkgsub.py` | 4-5 |
| Pure addition (GBDT chain) | `nd-unfolding/assemble_gbdt5d_adopted.py` | 4-20 |
| Disjointness proof, the shape to imitate | `nd-unfolding/pet/assemble_ctotal_bkgsub.py` | 10-22 |
| Measured addition identities, rtol `1e-9` | `nd-unfolding/p4_adopt_standard.py` | 62-67 |
| Sample-cov recipe, `n−1`, replica mean | `nd-unfolding/pet/combine_cstat_bkgsub.py` | 57-58 |
| Same recipe, independent file | `nd-unfolding/combine_seedscan_split.py` | 60-68 |
| Mean-vs-CV shift reported separately | `nd-unfolding/combine_seedscan_split.py` | 75-77 |
| Gram-rank / min-eig-zero-by-construction | `nd-unfolding/pet/combine_cstat_bkgsub_100rep.py` | 90-93 |
| Strict replica inventory loader | `nd-unfolding/replica_manifest.py` | 12 |
| Symmetry `<= 1e-9`, PSD relative tol | `nd-unfolding/p4_validate_active_lateral_fps.py` | 66-68, 123 |
| PSD tol (PET) | `nd-unfolding/pet/assemble_ctotal_bkgsub.py` | 66 |
| Adopted FPS 2D ranks + component magnitudes (266 grid) | `VALIDATION_LEDGER.md` | 1289-1295 |
| **`C_stat` precedent is 100 bootstraps; `C_ML` 24 splits** | `VALIDATION_LEDGER.md` | 1293 |
| `C_syst` is a sample cov over throws, so rank ≤ T | `nd-unfolding/unified_throw.py` | 391 |
| `C_stat` consumed diagonal-only | `nd-unfolding/coverage_valid_nd.py` | 9, 44-53 |
| `C_stat` consumed diagonal-only | `nd-unfolding/pet_lateral_correction.py` | 142-146 |
| Inversion happens on the TOTAL only | `2d-unfolding/compare_to_paper_fullcov.py` | 103, 124 |
| Truncated-spectral pinv, `λ > 1e-10 λmax`, CONFIRMED | `docs/COLLABORATOR_QUESTIONS.md` | 36-42, 131-136 |
| `ndf = n_reported` justified only when rank ≈ n | `2d-unfolding/receipt_model_chi2_2d.py` | 32-35 |
| Rank-deficient GoF endorsement still owed | `docs/OPEN_ITEMS.md` OI-29 | 84 |
| P5B: components share P5A central/mask/order | `docs/PUBLICATION_COMPLETION_RUNBOOK.md` | 213-214 |
| F7 `C_stat` contract | `docs/PUBLICATION_COMPLETION_RUNBOOK.md` | 216-222 |
| Assembly requirements | `docs/PUBLICATION_COMPLETION_RUNBOOK.md` | 233-235 |
| No standalone `C_retrain` | `docs/PUBLICATION_COMPLETION_RUNBOOK.md` | 243 |

---

## §7 — What 50 replicas can and cannot support

Not a convention, but the spec should not require of `C_stat` something 50 draws cannot deliver.
All from `n = 50`, `dof = 49`:

```
relative SE on a diagonal sigma_i   = 1/sqrt(2*dof) = 1/sqrt(98)  = 0.10102  ->  10.10%
SE on an off-diagonal rho (at rho=0) = 1/sqrt(dof)  = 1/7          = 0.14286  ->  14.29%
off-diagonal entries at 262 bins     = 262*261/2                   = 34,191
```

So: **per-bin statistical errors are good to ~10%**, and that is a publishable diagonal. **The
off-diagonal correlation structure is essentially unmeasured** — 34,191 entries each carrying ~0.143 of
noise. This is not an argument against building `C_stat`; it is an argument that the spec should require
the *diagonal* to be gated numerically and should treat the correlation matrix as reported-but-noisy,
with the rank truncation of §0.2 as the mechanism that keeps the noise out of any inversion. If C's
spec wants a shrinkage or a banding, that is a **new** convention with no precedent in the tree that I
could find, and it needs Joseph.

---

## §8 — What I cannot establish from the repo

Stated plainly, per the standing instruction that *"needs X" is a complete answer*.

1. **Which grid `C_stat` lives on** (§0.1). **Needs:** the P5A nominal extraction receipt — its grid
   shape and `n_cells_populated`.
2. **The publication reported-bin count.** 262 is from a file whose own name is
   `NONQUOTABLE-DIAGNOSTIC`. It fixes the *shape and order* reliably; it does not fix the count.
   **Needs:** the same P5A receipt.
3. ~~**Whether the PET mask nests inside the FPS 266 mask.**~~ **RESOLVED by lane D** — it nests, the
   4 extra exclusions are `{228, 251, 252, 253}`, derived in §0.1 from D's published index set
   (`COMPARATOR-PREDECLARATION-20260814-cstat.md:50-51`). Struck rather than deleted so the sequence is
   legible: I stated the limit of my evidence and another lane closed it within the hour.
4. **Whether a 2D PET assembler is to be written.** Only 5D assemblers exist. **Needs:** C's or
   Joseph's decision.
5. ~~**Whether 50 is the predeclared publication inventory or a pilot.**~~ **RESOLVED — it is
   predeclared** (`PREDECLARATION-20260813-gate5-coherent-replicas-n50.md`, `6bd3707`, cited from
   `OPEN_ITEMS.md:111`). Struck rather than deleted: I asserted its absence from a failed search, which
   is the error `BEN-241` records. **What remains open is not the predeclaration but the supersession of
   the N=100 one** (§0.5, §9.1). **Needs:** Joseph's ratification.
6. **Whether the existing 20-replica `pet_cstat_bkgsub_5d.npz` is superseded or a cross-check.**
   **Needs:** C's spec to say.
7. **The realized rank of a PET `C_syst`.** Bounded by 124 endpoints; the GBDT analogue realized 144 of
   a 187 bound (77%), which does not transfer. **Needs:** the PET vertical sweep, which does not exist
   (`3e59c91`: ~402 GPU-h at `k=1`, blocked behind a Gate-4 code-gate re-issue).
8. **Where the production truncated-spectral pseudo-inverse is implemented.** I found the convention
   declared in a letter to collaborators and three *different* rank thresholds across three scripts
   (`1e-10` declared, `1e-12` in `_ours_only_chi2.py:123`, numpy default in
   `compare_to_paper_fullcov.py:103`). I did not find one production implementation of the declared
   form. It may exist under a name I did not search. **Needs:** either the file, or the acknowledgement
   that the convention is currently declared in prose only.

---

## §9 — Disagreements to surface BEFORE two builders start

Per the peer's request that mismatches be found now rather than by D at comparison time.

1. **The undocumented supersession between two live predeclarations — a documentation repair Joseph
   must ratify, not a builder decision (§0.5).** Both
   `PREDECLARATION-20260812-fullevent-cstat-100-replicas.md` (N=100, *"not to be revised downward"*,
   `INSUFFICIENT` at fewer than 100) and
   `PREDECLARATION-20260813-gate5-coherent-replicas-n50.md` (N=50, precision criterion, *"sounds good,
   get N=50 up and running"*) are committed and live, each rests on its own Joseph authorization a day
   apart, and **neither references the other**. The decision for 50 is defensible on every axis —
   different estimator, stated criterion, authorized, all before any spread — but **the supersession
   chain is the thread a referee pulls**, and the older document's verdict clause currently reads on a
   50-replica product as `INSUFFICIENT`. **Ratify and record the supersession before either builder
   writes a line.** I have deliberately not written it: retiring another lane's predeclaration is not a
   builder's act, and `combine_cstat_bkgsub_100rep.py` sitting in the tree makes "just run 100 instead"
   a one-command temptation that would resolve the conflict in the wrong direction — by compute rather
   than by decision.

   *Note on the rank framing:* the N=50 document already settled it — *"Rank is not the criterion …
   already disclosed under `OI-29`"* — so §0.2's analysis corroborates an existing decision rather than
   raising a new question. That is the right outcome and it is worth saying, because two independent
   derivations of `1/√(2·49) = 0.10102` from opposite directions is the cheapest confirmation available.
2. **`C_stat` must not define the reported mask; `C_syst` does** (`assemble_ctotal_bkgsub.py:104`). But
   `C_syst` **does not exist** (my scoping, `3e59c91`, ~402 GPU-h at k=1, blocked behind a Gate-4 code
   gate). So the mask authority for `C_stat` is a component that has not been built. Either P5A's mask
   is promoted to the authority directly — which is what `RUNBOOK:213-214` actually says — or `C_stat`
   is built against a mask that a later `C_syst` could contradict. **`RUNBOOK:213-214` should win, and
   the spec should say so explicitly**, because the assembler's code currently says `C_syst`.
3. **npz vs ROOT TH2D** (§3). Affects how expensive D's element-wise comparison is.
3a. **The artifact shape — THREE live proposals, §3.1, OPEN and awaiting C's ruling.** `(n_reported,
   n_reported)` only (this document), `(285,285)` + mask only (D's committed predeclaration `:168`), or
   **both** (D on reconsideration, the mediator's recommendation to C). The third is better than my own
   on the merits because it puts the reduction — the error-prone step — inside the verified scope. **It
   needs the exact bit-identity assertion in §3.1 to pay for itself**, and it creates the `n_reported`
   inference trap recorded there. This is the one item on this list that is not a question awaiting an
   answer but committed documents wanting different artifacts.
4. **Whether the shared prior implementation counts as an independence leak** (§0.3), and if so what
   the two builders are actually being asked to independently derive.
5. **My §4.4 rank arithmetic implies the P5B total is rank-deficient regardless of `C_stat`.** If that
   is news, it belongs on `OI-29` rather than inside this spec — but it should not be discovered during
   P6.

---

**Lane B's Gate-6 position is unchanged by any of the above. GATE 6 IS NOT UNBLOCKED.** All five
prohibitions at `19585b7` remain live: `do_not_select_passing_subset`, `do_not_construct_C_ML`,
`do_not_move_central`, `do_not_start_leg_2`, `do_not_retry_unchanged`. Floor draw
`56863958_5` was measured PENDING at 2026-08-14T12:00:45Z; the floor verdict takes precedence over
this work the moment it lands.
