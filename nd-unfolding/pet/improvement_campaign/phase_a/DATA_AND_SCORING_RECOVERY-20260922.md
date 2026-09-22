# Phase A2, Parts 1–2 — recovering the comparison's numbers and verifying its data path

Scope §3 (recover and recompute the headline) and §5 Phase A item 5 (event identity, dual-leg
weights, normalization, selection, masks, feature units, split isolation).

Everything below is a measurement made by code in this branch running under
`nd-unfolding/mnv_guarded_run.py` from clean pinned checkouts, over the **original** campaign
outputs under `/pscratch/sd/j/josephrb/campaign-20260920/`. Nothing in the historical comparison was
modified. Machine-readable forms: `receipts/recompute_scores.json`,
`receipts/recompute_directional.json`, `receipts/recompute_data_path.json`,
`receipts/mask_conjuncts.json`.

Each finding is tagged **MEASURED**, **INFERRED** (from source, no runtime capture) or
**NOT-ESTABLISHED**.

For the input arrays as the model actually receives them — feature semantics, the PDG column, mask
handling inside PET — see delegate A1's `phase_a/INTENDED_VS_EXECUTED-20260922.md` on branch
`pet-improvement-20260922-phaseA1`. This document covers identity, joins, weights, the tilt,
selection, normalization and split isolation.

## 0. What this corrects in the superseded draft

The first A2 draft (commit `7d687a62`, rejected) stated four things this measurement contradicts.
They are listed here so the corrections are not silently buried.

| Superseded claim | Measured |
|---|---|
| tilt "clipped at 3.0 GeV" | the clip is on a **standardized** coordinate `z=(E_avail−p50)/IQR`, `z∈[−3,+3]`; the clip is first reached at **E_avail = 9.366 GeV** (§3.3) |
| halves of 600,143 rows "vs the report's 600,130/600,111 (+32 dropped)" | both are right and not in conflict: each half **is** 600,143 rows; 600,130/600,111 are their **truth-passing** subsets. The 13 and 32 differences are exactly the **fake** (reco-only) rows (§3.4) |
| masks/padding PASS | **FAIL** (§3.6) |
| join integrity proved by a `row_index` mapping of length 49,152,885 | that is row *alignment*, not a join. The join is by `(mc_run, mc_subrun, mc_nthEvtInFile)` and matches 59.5 % of inventory rows overall — explained, and 100 % on the rows that matter (§3.5) |

## 1. Provenance of every input used

All four pinned digests re-verified by reading the bytes; all match what the report and
`frozen_design.py` declare. **MEASURED.**

| Input | sha256 | Matches pin |
|---|---|---|
| `…/g2_input/G2_FPS_MEFHC_P12.npz` | `fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625` | yes (report) |
| `…/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz` | `01e07412b253ff496c30025cc71a9185b166a00892b1e1b4c8bce714ddd5f95c` | yes (`frozen_design`) |
| `…/g2_input/G2_FPS_MEFHC_P12_RECEIPT.json` | `d466a0c18deaafa2ae645002c8dbc9b9879476adb45a40a85c0bae9e0129d25e` | yes (`frozen_design`) |
| committed `campaign_report.json` | `96955a10222b6c95c13a5db0e48c9af96717371045398a837b996ba3d17625c2` | — |
| `campaign-20260920/join/join_sig.npz` | `33709fa057d1443478f798112b1ca61905b3a2f9e55659e6f9726d15d55b48b6` | — |
| `campaign-20260920/cache/theirs-final.npz` | `cc88626bc44293a12e221c6e540476f7d29c718126daf1a090bcdf489d635045` | — |

Scoring modules were imported from a clean checkout of `68cf9d29`, each recorded with its own
sha256 in `receipts/recompute_scores.json` (`score_campaign.py`
`4dc1214bbebceac07eaff1184c8bc89fb6db7d0d8afdd17cf3e58ce3971d4a4e`, `characterize_regions.py`
`f31495bd…`, `reference_calibration.py` `e4b2612d…`, `frozen_design.py` `aa9fa4ac…`). All 56 original
per-run output directories (32 tuning, 8 pilot, 16 final) were present; **nothing had to be
recovered from HPSS or CFS.**

## 2. Part 1 — the headline reproduces

Two independent routes were run.

**Route A — re-run the committed reporter.** `report_campaign.py` from the `68cf9d29` checkout, over
the original outputs. The regenerated `recomputed_campaign_report.json` is **byte-identical** to the
committed report (same sha256 `96955a10…`). Leaf-by-leaf: **837 of 837 leaves bit-identical, 0
within-1e-10, 0 mismatched, 0 missing.** **MEASURED.**

**Route B — an independent scorer.** `independent_recovery()` (`a2_recover.py:170-181`) implements
the seven-bin score from the specification rather than importing `score_campaign`, reading each
run's own saved arrays (`dump_rows_a`, `dump_rows_b`, `tilt_a`, `weights`) plus `eavail`/`w_truth`
from the inventory. This is the step the rejected draft omitted. It reproduces every per-run
recovery and the aggregate to **≤ 2·10⁻¹⁵** — the residue of float summation order, not a
disagreement. **MEASURED.**

### 2.1 Headline

| Quantity | Committed | Recomputed | Class |
|---|---:|---:|---|
| Overall mean recovery, ours | 0.30367486660122656 | 0.30367486660122656 | bit-identical |
| Overall mean recovery, theirs | 0.41652658344946014 | 0.41652658344946014 | bit-identical |
| Aggregate reference | 0.6949731568655361 | 0.6949731568655361 | bit-identical |
| Adequacy floor (0.8 × reference) | 0.5559785254924289 | 0.5559785254924287 | within 1e-10 |
| ours, low acceptance | 0.05579216507588465 | = | bit-identical |
| ours, moderate | 0.22639608558715230 | = | bit-identical |
| ours, good | 0.53810127861986180 | = | bit-identical |
| theirs, low acceptance | 0.15260764163974938 | = | bit-identical |
| theirs, moderate | 0.41421311151239326 | = | bit-identical |
| theirs, good | 0.68861737311595550 | = | bit-identical |
| Regional floor, low acceptance | 0.008376759448816837 | 0.008376759448816844 | within 1e-10 |
| Regional floor, moderate | 0.465916639061693\<95\> | 0.465916639061693\<84\> | within 1e-10 |
| Regional floor, good | 0.5852874937783695 | 0.5852874937783695 | bit-identical |
| Low-acceptance truth-mass fraction | 0.3103084462065607 | = | bit-identical |
| Verdict / recommendation | `NEITHER_ELIGIBLE` / `NO_SELECTION` | = | bit-identical |

The `within 1e-10` rows are the floors and the regional references, which the reporter writes from
a re-derivation rather than a stored constant; the differences are at the 1e-16–1e-15 level.

### 2.2 The eight paired differences and the interval

All eight bit-identical under Route A; Route B agrees to ≤ 1e-15. **MEASURED.**

| Seed | ours − theirs |
|---|---:|
| 127 | −0.16785575267122055 |
| 139 | −0.16536426303594665 |
| 151 | −0.09597126778749154 |
| 163 | −0.11126936123547460 |
| 179 | −0.05338420441045710 |
| 191 | −0.13626938815203826 |
| 211 | −0.07596759774320605 |
| 223 | −0.09673189975003416 |

mean −0.11285171684823361, sd 0.04101484745791815, t(7, .975) 2.364624251592784,
95 % CI **[−0.14714098742050435, −0.07856244627596287]**. Gregor's arm scores higher in all eight
pairs.

### 2.3 The reference and floor are computed on a different domain from the score they gate

**MEASURED, and it is a documented design choice rather than a hidden defect — but its size was
not previously quantified.**

`frozen_design.REFERENCE` = 0.6949731568655361 is `reference_calibration.ceiling(acceptance,
injected-displacement, k=3)` evaluated over the **285 (pT, p_parallel) reporting cells**
(`frozen_design.REGIONS`: `"defined_on": "(pT, p_parallel) reporting cells, 15 x 19 = 285"`). The
score it gates is the **seven-bin E_avail marginal** (`frozen_design.ENDPOINT`:
`"primary_score": "seven-bin E_avail recovery"`).

Recomputing the same ceiling, same tilt, same rows, on each domain:

| Domain | k=1 | k=2 | **k=3** | k=4 |
|---|---:|---:|---:|---:|
| 285 (pT, p_∥) cells — **the frozen number** | 0.5104038956 | 0.6482928244 | **0.6949731569** | 0.7146286370 |
| 7 E_avail bins — **the endpoint's own domain** | 0.3958247356 | 0.5966744142 | **0.7131426234** | 0.7882637668 |

The k=3 values differ by **+0.0181694665**. Had the reference been built on the endpoint's own
binning the floor would be 0.8 × 0.7131426234 = **0.5705140987** instead of 0.5559785255 — i.e.
slightly *stricter*.

The frozen comment justifying the choice says the weighting makes "the reference and the score
describe the same population". That is true of the **rows** and false of the **binning**. **The
verdict is unaffected** — both arms (0.304, 0.417) fall far below either floor — so this does not
disturb the historical result. It is recorded because scope question 4 asks whether the adequacy
reference is appropriate, and a like-for-like reference is a prerequisite for answering that.

### 2.4 Directional diagnostic — the report's missing piece

Per bin: `injected = target − prior`, `achieved = unfolded − prior`,
`signed_residual = unfolded − target`, `achieved_fraction = achieved / injected`. Means over the
eight final seeds, on normalized spectra. **MEASURED** (`receipts/recompute_directional.json`).

The injection moves mass **out** of bins 0–5 and **into** the top bin:

| E_avail bin (GeV) | injected | achieved fraction, ours | achieved fraction, theirs |
|---|---:|---:|---:|
| 0.0–0.1 | −0.01613 | 0.538 | 0.606 |
| 0.1–0.2 | −0.01383 | 0.596 | 0.664 |
| 0.2–0.4 | −0.02539 | 0.517 | 0.621 |
| 0.4–0.8 | −0.03565 | 0.353 | 0.490 |
| 0.8–1.5 | −0.03177 | 0.133 | 0.269 |
| **1.5–3.0** | **−0.01543** | **−0.318** | **−0.206** |
| 3.0–100 | +0.13820 | 0.304 | 0.417 |

Three findings, all **MEASURED**:

1. **No bin overshoots, in any run.** `runs_with_any_overshoot_bin = 0` for both arms, final and
   pilot. The deficit is pure undershoot, not oscillation around the target.
2. **One bin moves the wrong way, in every run.** `runs_with_any_wrong_direction_bin = 8` of 8 for
   both arms. It is the same bin each time — **[1.5, 3.0] GeV**, where mass should leave and
   instead accumulates. Both arms pile mass up immediately below the bin the injection fills.
3. **Recovery degrades monotonically with E_avail** across bins 0→5 for both arms, from ~0.54–0.61
   in the lowest bin to negative at 1.5–3.0 GeV. The two arms differ by a roughly constant offset
   rather than in shape; Gregor's arm is better in every bin.

Note the top bin's achieved fraction equals the overall recovery exactly (0.304 / 0.417). That is
structural, not a coincidence: on normalized spectra both the injected and residual vectors sum to
zero, and the top bin carries the whole of one sign, so `R = 1 − Σ|res|/Σ|inj|` collapses to that
bin's achieved fraction.

### 2.5 Per-iteration recovery — NOT-ESTABLISHED

Each run directory holds **one** event-weight array (the final push), plus a Keras checkpoint and a
pickle per (iteration, step). The pickles were opened: they contain only per-epoch training
history, no event weights. **Per-iteration recovery cannot be recovered from the saved artifacts.**

The route that does exist: re-infer each iteration's step-2 checkpoint on half B's truth cloud — 48
inferences over ~600 k rows, a GPU job outside this CPU-scoped task. Phase B item "recovery
trajectories across unfolding iterations" needs that job; it is not a re-read of existing outputs.

## 3. Part 2 — the data path

Thirteen checks. **MEASURED** unless noted.

| # | Check | Result |
|---|---|---|
| 1 | identity binding (sidecar ↔ inventory) | **PASS** |
| 2 | identity uniqueness (rows are events) | **PASS** |
| 3 | MC subsample reproducibility | **PASS** |
| 4 | split isolation (stages and halves) | **PASS** |
| 5 | selection flags | **PASS** |
| 6 | dual-leg weights | **PASS** |
| 7 | pseudodata tilt | **PASS** |
| 8 | pseudodata normalization | **OBSERVATION** |
| 9 | masks and padding | **FAIL** |
| 10 | theirs join and cache | **FAIL** |
| 11 | theirs model inputs | **PASS** |
| 12 | feature units at model input | **PASS** |
| 13 | engine files on the hardcoded root | **OBSERVATION** |

### 3.1 Identity and uniqueness — PASS

`(mc_run, mc_subrun, mc_nthEvtInFile)` identifies exactly one inventory row across all 49,152,885
rows. **Rows are events.** Every downstream "row-disjoint" statement is therefore also
identity-disjoint; this is the fact that licenses the Phase D draw counts.

### 3.2 Split isolation — PASS, and tested rather than cited

- Stage assignment is `stage_splits.assign` = blake2b of the identity triple salted with
  `split_seed=20260920`; halves come from `deterministic_halves(stage_rows, half=n//2, seed=20260920)`.
- All six stage/half row sets (tuning A/B, pilot A/B, final A/B) were compared **by event identity,
  pairwise**: all 15 intersections are **0**.
- Each stage's halves were **re-derived bit-for-bit** from the committed split code and matched the
  arrays the runs actually saved.
- Every run within a stage used the **same** halves (one distinct `(sha(rows_a), sha(rows_b))` pair
  per stage).

### 3.3 The tilt, as executed — PASS

Re-derived from the inventory and compared against each run's saved `tilt_a`: **bit-identical.**
Applied to half A's truth-passing rows only.

```
z    = clip( (E_avail − p50) / IQR , −3.0, +3.0 )
tilt = exp(0.35 · z) / mean(exp(0.35 · z))
```

Standardization constants actually used (half A, GeV): **p25 0.5318406671, p50 1.4653696418,
p75 3.1655117869, IQR 2.6336711198**; pre-normalization mean 1.1561864050.

| | |
|---|---|
| clip is on | the **standardized coordinate**, not the weight and not raw GeV |
| E_avail at the upper clip | **9.3663830012 GeV** (z=+3) |
| E_avail at the lower clip | −6.4356437176 GeV (z=−3) — unreachable |
| rows clipped high / low | **2.882 %** / **0 %** |
| tilt range | [0.7118654595, 2.4716179898] |
| unweighted mean tilt on injected rows | 1.0000000000 (rate-preserving by construction) |
| **w_truth-weighted mean tilt** | **1.0293403572** |

The last row is worth carrying forward: the tilt is rate-preserving **unweighted**, but the score's
spectra are `w_truth`-weighted, under which the injection changes the total rate by **+2.93 %**. The
seven-bin score normalizes both spectra, so this does not corrupt it; it does mean the injection is
not purely a shape change in the weighted population.

A separate tilt instance, computed over the **whole** truth-passing inventory (p50 1.4587417841,
IQR 2.6292083412), is used by `report_campaign.build_endpoint` for the region census and the
references only. The score's target uses the half-A tilt above. Two tilt instances with slightly
different constants therefore coexist by design; both were re-derived and both match.

### 3.4 Selection flags — PASS, and this resolves the "dropped rows" question

`pass_reco` and `pass_truth` partition the inventory into both / miss / fake with **no "neither"
row**, and every `!pass_reco` row carries the −9999 sentinel in `reco_scalars`.

| Population | rows | pass_truth | pass_reco | both | miss (truth only) | **fake (reco only)** |
|---|---:|---:|---:|---:|---:|---:|
| inventory | 49,152,885 | 49,150,928 | 20,573,521 | 20,571,564 | 28,579,364 | **1,957** |
| final half A | 600,143 | 600,130 | 250,514 | 250,501 | 349,629 | **13** |
| final half B | 600,143 | 600,111 | 251,109 | 251,077 | 349,034 | **32** |

**The report's 600,130 and 600,111 are the truth-passing subsets of two 600,143-row halves, and the
13 and 32 "dropped" rows are exactly the fake rows.** They are dropped from the *score* because the
score lives in truth space; they are not lost data.

How each class enters (read from `run_arm_evaluation.evaluate`, `68cf9d29`):

| Stage | Population |
|---|---|
| step-1 pseudodata | half A, `pass_reco & pass_gen` |
| step-1 prior | half B, `pass_reco & pass_gen` |
| step-2 prior | half B, `pass_gen` (**misses included**) |
| score target | half A `pass_truth`, `w_truth · tilt` (misses included) |
| score prior / unfolded | half B `pass_truth`, `w_truth` and `w_truth · push` |
| **fakes** | **enter nothing** — not step 1, not step 2, not the score |

### 3.5 The theirs join — FAIL on one conjunct, and the 59.5 % is explained

The check ANDs seven conditions. **Six pass:**

- a 4,000-row random sample of half-B `pass_reco` rows resolves to shard rows carrying the **same**
  `(mc_run, mc_subrun, mc_nthEvtInFile)` — 4,000 / 4,000;
- a fresh gather equals the cache the tasks actually read, for both `packed` and `globals`;
- the cache's rows equal the runs' halves, and its step-1 A set equals `pass_reco & pass_gen`;
- `positional_fallback` is **`never`** — the join never silently fell back to row order;
- **every one of the 20,573,521 `pass_reco` rows has a built input (fraction 1.000000).**

**The single failing conjunct is `duplicate_built_keys == 0`; the measured value is 111** out of
91,390,364 built rows (1.2 × 10⁻⁶). That is the whole of the FAIL.

The overall match fraction of **0.5951** is *not* a defect and is *not* part of the criterion: the
inventory's truth denominator includes 28.6 M rows with no reconstructed object, which cannot have a
reco-derived built input and are zeroed for **both** arms. The rejected draft's `row_index`
alignment argument did not test this at all.

**Open:** the 111 duplicate keys are not diagnosed here — their effect, if any, is confined to which
of two built rows a duplicated key resolves to. Worth closing before Phase C reuses `join_sig`.

### 3.6 Masks and padding — FAIL

The aggregate check failed and the original receipt recorded only the AND, so the conjuncts were
re-run one at a time (`a2_mask_diagnose.py`).

<!-- MASK_CONJUNCTS -->
*Job `58752537` was still queued when this document was written; §3.6's per-conjunct result is
filled in from `receipts/mask_conjuncts.json` when it lands.*

What is already measured, and matters more than the verdict:

| | reco cloud | truth cloud |
|---|---:|---:|
| token cap | 12 | 12 |
| **events at the cap** | **85.08 %** of `pass_reco` | 2.51 % of `pass_truth` |
| events with **zero** tokens | 1,000 | 4 |
| tokens on `!pass_reco` rows | 0 | — |
| energy ordering within event | descending | — |
| tokens with negative energy | 0 | — |

`dump_pointcloud_inputs._pad_tokens` keeps the top-12 tokens by energy and **drops the rest; no
overflow summary is written.** The 1,000 `pass_reco` rows with zero reco tokens are
indistinguishable, at the model input, from a row that failed reco selection.

The quantitative consequence of the cap — ~40 % of cluster energy discarded — is Part 3's leading
result; see `FEATURE_INVENTORY-20260922.md` §0.

### 3.7 Dual-leg weights — PASS, with one observation

`w_truth` and `w_reco` are finite, positive and row-aligned (`w_truth` mean 0.8213, max 18.3389;
`w_reco` mean 0.8075, max 18.1283). On rows passing both, `w_reco/w_truth` ∈ [0.9311, 0.9977], mean
0.9812, and is **never exactly 1**. `w_reco` enters step 1 (both legs); `w_truth` enters step 2 and
every truth-space spectrum in the score.

**Observation:** the stated rule is that miss rows carry `w_reco := w_truth`, but the two are
exactly equal on only **69.63 %** of miss rows. Not pursued, because miss rows' `w_reco` enters
nothing (§3.4) — but the rule as written does not describe the array.

### 3.8 Pseudodata normalization — OBSERVATION, not a pass/fail

Measured in the executed logs (all 16 final runs printed the same three lines): the engine
normalizes **both** step-1 classes to 10⁶ —
`INFO: Normalizing sum of weights to 1000000.0 …`.

The pseudodata class is `Σ w_reco·tilt` over half A's step-1 rows and the prior class is
`Σ weight_reco` over half B's; normalizing both to the same constant **discards the physical class
ratio the tilt implies**. `class_ratio_used = 1.0`.

**INFERRED consequence (not measured):** step 1 then learns `r(x)/R_phys` on accepted rows while the
pull weight on misses stays 1 — a shape-only closure. Whether that costs recovery is a Phase B
question; this records the executed behaviour and its evidence, not an effect size.

### 3.9 Feature units and the engine's import root

Feature units at the model input **PASS**: the executed loader (`68cf9d29`, `bkg_mode='mc-only'`,
`max_events=2e6`, seed 0) returns the same subsample and flags as the inventory; inputs are
GeV/m/ns-scaled clouds and z-normalized event blocks; `!pass_reco` event rows are zero. Gregor's
step-1 inputs likewise zero on `!pass_reco`. See A1's audit for the in-model view.

**OBSERVATION (not established):** `fullevent_fps_dataloader.py:57-60` and
`train_fullevent_nominal.py:36-39` insert hardcoded `/pscratch/.../MINERvA-OmniFold` paths at
`sys.path[0]`. By that ordering the historical tasks would resolve `omnifold` (MultiFold, DataLoader,
PET) and `annealed_estimator` **from the production checkout, not from the pinned campaign
checkout**. Which file actually loaded is **NOT-ESTABLISHED** — there is no runtime capture in the
historical outputs. It is recorded because it determines whether `68cf9d29` is the code that ran.
A1's runtime audit is the place this gets settled.

## 4. What Parts 1–2 leave open

1. Per-iteration recovery needs the 48-inference GPU job (§2.5).
2. The 111 duplicate built keys in `join_sig` are undiagnosed (§3.5).
3. Which conjunct of the mask check fails — job `58752537` (§3.6).
4. Whether the engine loaded the pinned checkout or the production one (§3.9) — A1's scope.
5. The step-1 class-ratio discard (§3.8) has an inferred mechanism and no measured effect size.
