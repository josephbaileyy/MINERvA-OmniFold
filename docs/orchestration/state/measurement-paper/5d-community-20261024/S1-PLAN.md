# PLAN S1: what a configuration (e) 5D covariance on the H2 cells would cost, inputs included (2026-10-24)

**By** the measurement session, for the director. Assignment S1 of
`DECISION-20261024-joseph-5d-community-standard-route.md` (item 7).
- **Scoping only:** 0 node-h. No job was submitted.
- **Cluster reads:** login12, 2026-10-24 18:15–18:26 UTC. Only `ls`, `stat`, `find`, `du`, `sha256sum` on files under
  2 GB, npz header reads, `myquota` and `prjquota`.
- **Repo reads:** main at `2c8c1e4f`.

**CITABLE FOR:**
- the inventory of (e) covariance inputs;
- the unit costs and their bases;
- a proposed staged plan with caps;
- what carries over from (a);
- what the H2 cells need.

**NOT CITABLE FOR:** any authorization. Any compute here needs Joseph's approval, and a declaration and binding. No GPU is
proposed. No claim changes.

## 0. Answer

**Almost every input of an (e) covariance already exists.** What is missing is mainly one kind of product: the
per-universe (e) real-data unfolds, 177 of them plus a CV control.
- One more piece is missing unless the lateral bands are mean-centered: a CV to centre them against. The lateral
  products lack the 2,801 sentinel rows, and no sentinel-free (e) CV exists (§1, row 7).
- Two small code changes are needed before assembly (§3.3).
- **Already made for R:**
  - the 10 re-selected lateral endpoint unfolds;
  - 50 refit-per-replica data bootstrap replicas, plus 100 bootstrap-only replicas;
  - the (e) central value;
  - the seven prior-variation unfolds.
- **Estimator-independent, so they serve (e) as they are:**
  - the universe weight bank (175 universes);
  - the weight-only detector dump (8 universes);
  - the flux-universe integrals;
  - the background stream;
  - the base inputs.
- **Tooling:** `s5p_universe.py` already runs config R at 400/31 with refinement `random_state` = seed + 3.

**Cost of the missing piece:** 0.0436–0.0476 CPU node-h per universe unfold, by step wall at today's speed
**(arithmetic, §2)**.
- Pilot: cap **0.5** CPU node-h.
- Production: cap **10.5** CPU node-h; expected 7.7–8.4.
- Readout: login node, 0 node-h.
- **Total cap: 11.0 CPU node-h.** No GPU is needed: a GPU node costs more per (e) data unfold than a CPU node (§2).
- **Storage:** about 20 MB of new products on pscratch. No input staging, and nothing on CFS.

**Eight assembly choices must be declared before any of these products is read (§3.3).** They are:
- centering;
- the lateral bands' reference;
- Rvp1pi;
- whether (a)'s inflation D is kept;
- the C_stat replica set;
- the GEANT source;
- how C_model is combined;
- the final reporting cells.

A governance question also goes to the director (§5, item 1): what counts as having "read" a refined-estimator data
result under DECISION-20261024 item 2. The pilot itself creates such products.

## 1. Inputs: what exists, for what, and whether (e) can use it

`$P` = `/pscratch/sd/j/josephrb`. Shas marked "measured" were re-hashed on 2026-10-24; the others are taken from the
record named.

| # | input | path | sha256 / size | built for | usable under (e) (400/31, seed + 3)? |
|---|---|---|---|---|---|
| 1 | **base inputs** | `$P/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz` | `07fccc1a…` measured; 1,548,438,020 B | both | yes; every R product's `input_npz_sha256` names it |
| 2 | **background stream** | `$P/s5c-20260924/runs/p2/bkg_dump.npz` | `2addac8f…` measured; 16,017,201 B | R (negweight-refined) | yes |
| 3 | **flux universes (100), event weights** | `$P/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware/Flux_{0..99}_{wt,wr,tdw,bkgw}.npy` | each file in `state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt`; 2 spot checks match | per-event weights, estimator-independent | yes; the s5p R null ensemble already reads this bank (`state/s5p/s3-pilot-tasks.tsv`, `--bank`) |
| 4 | **flux-universe integrals** | `$P/MINERvA-OmniFold/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root` | `5eecae84…` measured; 6,396 B | both | yes. `s5p_universe.py` requires it for Flux (`nd-unfolding/s5p_universe.py:116-118`) |
| 5 | **interaction-model bands** (34 bands, 69 universes, including 2p2h ×3) | the same bank, `{tag}_{wt,wr,tdw,bkgw}.npy`; alignment reference `cv.npz` | sf1 manifest; `cv.npz` `072643e1…` (2,163,648,810 B, from the record) | estimator-independent | yes |
| 6 | **weight-only detector bands** (MinosEfficiency, GEANT_Neutron/Pion/Proton, ±1 each: 8 universes) | `$P/s5p-20260926/bank_detector/` (33 files, 2.0 GB), with `detector-dump.json` | every file's sha in that receipt; 2 spot checks match | the R path (job 58953705) | yes. The bank also has 6 GEANT universes, but they are **not identical** to the dump's. For GEANT_Neutron_0, `wt` and `bkgw` are byte-equal but `wr` differs (bank `2611781d…`, dump `745de05b…`, measured). `s5p_nullexp.py:25-28` prefers the dump, so the source is a declared choice |
| 7 | **re-selected laterals** (5 bands × 2 endpoints) | `$P/s5p-20260926/runs/s3/latunf/lat_<band>_{0,1}_b-_j-.npz` | in the sf1 manifest and `m2-archive/inputs_sha256.txt` | **R** (meta: config R, 400/31/45, 5 iterations; `state/s5p/s3-latunfold-tasks.tsv`) | yes as products, **but they need a matched reference.** They lack the 2,801 sentinel rows, so "a lateral band's shift must be taken against a CV product without them" (`state/s5p/campaign-state.json:247`). `s5p_assemble.py:129-135` centres them on the full central value. The only sentinel-free data CV, `s5e-20260925/runs/diag/rep/rep_data_nosentinel.npz`, is B0 (refinement 100/8), not (e). The remedies are in §3.3. The lateral input dumps were deleted after use (`campaign-state.json:263`); they are needed only to re-unfold |
| 8 | **stat replicas, set A** | `$P/s5p-20260926/runs/s2/num/data/data_b{1..50}_j{101..150}.npz` | each in `5d-design-20261023/stage0/INVENTORY.sha256`, 50/50 measured equal | **R**, refit per replica: data Poisson, MC Poisson(1), template Poisson(1), with jitter | yes. This set absorbs the numerical component (`state/s5p/contract-amendment-4-stage2-decisions.json:12`). Stage 0 used it |
| 9 | **stat replicas, set B** | `$P/s5e-20260925/runs/cand/assess/data/boot/boot_b{1..100}.npz` | per-file shas in `nd-unfolding/gbdt_model_dependence/inputs/inventory.json` | **R**, bootstrap only, no jitter | usable, with `--numerical explicit` and ≥ 20 jitters (`s5p_assemble.py:118`); `data_b-_j{1..20}.npz` exist. This set does not carry the rounding component that set A absorbs **(inference)** |
| 10 | **(e) central value** | `$P/s5p-20260926/runs/s2/num/data/data_b-_j-.npz` | `fb5cc679…` measured; equal bitwise to s5e's `data_R.npz` (`361030f3…`) | **R** | yes |
| 11 | **prior-variation vertices** (for C_model, S2's question) | `$P/s5p-20260926/runs/s2/prior/prior_R5fix_{CV,prior_d0..d5}.npz` | in the stage0 inventory; measured equal | **R** | yes (S2 decides how) |
| 12 | **per-universe (e) data unfolds** (100 flux + 69 model + 8 detector = 177) | none | — | — | **missing.** (a) has its own, as LightGBM ROOT products in `$P/MINERvA-OmniFold/nd-unfolding/uq_5d/universe_sweep_bkgaware/`. They are not usable under (e) |

<!-- absence-ok: row 12 is a cluster search: find over s5c-20260924 s5e-20260925 s5n-20260925 s5p-20260926 5d-stage0-20261023 for Flux_*.npz, MaCCQE_*.npz, MinosEfficiency_*.npz and *_uni_*.npz returned 0 files (login12, 2026-10-24T18:25Z); the repo record agrees: RECORD-20260927-s5p-stage2-exit.md:171 "built … not run" -->

**Counts.** The bank holds 175 universes: 100 flux, 69 interaction-model universes in 34 bands, and 6 GEANT. The dump
holds 8. All were counted on login12 by listing `*_wt.npy`.
- Under (e): 169 bank universes (setting aside the 6 bank GEANT copies; their source is declared in §3.3) + 8 detector universes = **177 unfolds**.
- Add the 10 existing laterals and the set equals (a)'s 187 universe unfolds (169 + 18).
  - The 18 are the 10 single-pass laterals plus the 8 weight-only detector universes
    (`nd-unfolding/uq_5d/detector_universes.txt:1-18`).
  - Under z-cv, the re-selected laterals replace the single-pass ones **(inference from the counts)**.
- The 45-band inventory of z-cv (13 vertical + 27 residual + 5 lateral; `nd-unfolding/z_contract.py:116-141`) is
  covered by: 35 bank bands (34 model + Flux) + 4 detector bands + 5 laterals + flat normalization.

**Purge exposure.** The two largest inputs, the bank (67 GB) and the detector dump (2 GB), are **not** in Part P's HPSS
tar.
- Their oldest access times are 2026-10-19 and 2026-10-20 (login12, `find -printf %A@`). Under NERSC's 8-week purge of
  unaccessed scratch files (NERSC policy, not a repo record), they are exposed from about 2026-12-14 **(arithmetic)**.
- Either run production before then, or copy both to HPSS at 0 node-h. That is about 69 GB, against about 158 GiB free
  after Part P **(inference: 512 − 350.9 GiB before Part P, less its 3.3 GB; `hpssquota` lags)**.
- pscratch is at 16.98 of 20.00 TiB (84.9 %); m3246 is at 85,615 of 102,400 GB.

## 2. Unit cost

**What a universe unfold is.** `s5p_universe.py` runs one real-data unfold with the universe's signal weights,
denominator and background weights swapped in. The background template and the refinement are refit per universe
(`nd-unfolding/s5p_universe.py:10-17, :109-128`). Its precision is hard-coded to float32 (`:200, :227`).
- It therefore costs about one float32 (e) data unfold.
- A direct receipt supports this. The seven `s5p_universe.py` prior and CV products took a median 644.091 s (max 660.0;
  `stage2_receipt.json` `costs`, category `('?', 5, None, 'float32')`), against 629.908 s for the plain data unfold.
  The universe path's extra weight loads fall inside `seconds_unfold` **(inference)**.

**The measured 5D unit, scaled to today** **(arithmetic)**:

| quantity | value | source |
|---|---:|---|
| 5D (e) data unfold, float32, September | 629.908 s median (n = 3, max 692.864) | `state/s5p/stage2/stage2_receipt.json`, `costs` |
| 5D (e) pseudo unfold, float32, September | 293.973 s (n = 423) | same |
| data / pseudo ratio | 2.1427 (median), 2.3569 (max) | (arithmetic) |
| today's pseudo unfold, CPU node, 8 × 32 (C0) | 533.06 s | `state/gpu-timing-20261023/REPORT.md` table, C0 |
| today's (e) universe unfold, 8 × 32, unfold only | 1,142 – 1,256 s | 533.06 × 2.1427 to × 2.3569 |
| per-task overhead outside the unfold | about 114 s | C0's step wall 647–648 s against 533 s unfolding (`gpu-timing REPORT.md:67`). It was measured on an `s5p_numerics` step; carrying it to `s5p_universe`, which also loads `cv.npz` and checks alignment, is an **(inference)** the pilot tests |
| **today's step wall per universe** | **1,256 – 1,370 s** | the sum |
| **CPU node-h per universe unfold** | **0.0436 – 0.0476** | step wall ÷ 3600 ÷ 8 |
| float64 data unfold (bootstrap replicas), for the options | 1,018 – 1,175 s unfold; 1,132 – 1,289 s step wall; 0.0393 – 0.0448 node-h | DESIGN.md's basis: 533.06 × 648.0435 / 339.244 to / 293.973, plus the 114 s overhead |

- **Assumption, untested:** the 1.4–1.8× slowdown measured on pseudo unfolds carries to data unfolds
  (`gpu-timing REPORT.md` §1). The pilot measures this directly. <!-- absence-ok: an assumption this plan makes and states as such; the pilot is its test -->
- **GPU nodes are the costlier option.** A float32 (e) universe unfold costs 0.0612–0.0673 GPU node-h at G2 × 4
  (0.028559 × 2.1427 to × 2.3569, unfold only; `DESIGN.md:366` gives 0.0546–0.0630 with the float64 ratios). That is
  more node-h than on CPU nodes, so nothing here asks for m3246_g.

**The RE-2 cross-check, as asked.**
- RE-2 charged 53.1838 node-h in all. That is part B's 47.7083 for its 644 runs plus J0's 5.4755
  (`RE2-PARTB-REPORT.md:9, :64`; `RE2-J0-REPORT.md:32-34`).
- Part B's mean is 0.0741 node-h per run. Its universe class (175 runs in J2a–d) is 21.3538 node-h, or 0.1220 per run
  **(arithmetic)**.
- **Scaled per run:** 178 × 0.1220 gives 21.7 node-h. That is the right figure only if a 5D unfold costs what a 2D
  universe run cost at 2 × 128 CPUs per lane. No record measures both on the same footing (`RE2-PARTB-REPORT.md:50-64`
  for 2D; the 5D unit above).
- **Per CPU-second, 5D is cheaper** (arithmetic). A 5D universe step here is 32 CPUs × 1,256–1,370 s, which is
  40,190–43,840 CPU-s. A 2D universe step in J2a–d took a median 859 s (n = 175, `run/partb_readout/steps.psv`) at
  128 CPUs, which is 109,950 CPU-s. So the 5D step is about 0.37–0.40 of the 2D one.
- **Conclusion:** the RE-2 scaling is a loose upper bound. The plan prices from the 5D unit, and the pilot re-measures
  it before production is bound.

## 3. Staged plan (proposed; nothing is authorized)

All stages run on regular QOS CPU nodes of m3246, never premium, exclusive, `--no-requeue`. Every job is ledgered from
`sacct`, and stopped and reported past 1.25× its projected wall. Caps are the enforced reservation: nodes × time
limit.

### 3.1 Pilot: one job, cap 0.5 CPU node-h

**What runs:** 8 lanes × 32 CPUs × 56 GB, one wave, at a pinned deploy:
- `--universe CV`, the control;
- Flux_0 and Flux_99;
- 2p2h_0, MaCCQE_1 and FrAbs_pi_0;
- MinosEfficiency_0 and GEANT_Neutron_1, from the detector dump.
- The pilot assumes the dump as the GEANT source. If the declaration chooses the bank copies, one lane runs a bank
  GEANT universe instead.

**Wall:** 1,256–1,370 s expected by step wall, so 0.35–0.38 node-h. Limit 0:30 (1,800 s ≥ 1.25 × 1,370), giving
0.5 node-h.

**Checks.** Each fails closed, and **none computes a cell value** (see §5, item 1):
- the CV control's `xsec_flat` equals `data_b-_j-.npz`'s bitwise. The prior tool's CV did (`stage0-binding.json`
  C2 `CV_equals_N1_base`);
- every product records OmniFold `capacity` None and refinement 400/31/45, `estimator_seed` 42, float32, and the input
  and background shas of rows 1–2. "400/31" also names the rejected OmniFold capacity (amendment-4:10), hence the
  explicit fields;
- the alignment checks pass: exactly 2,801 sentinel rows (`s5p_universe.py:53, :64-80`);
- Flux universes read their own integral, and detector universes read `denom_nd`;
- `xsec_flat` is finite and non-negative. This reads fine-cell values without forming any cell, a point for §5,
  item 1;
- **the bank path's denominator, at 0 node-h on a login node.** The CV control never calls the universe weight,
  denominator or flux functions that 169 of the 177 universes use (`s5p_universe.py:217-218`).
  - The bank's GEANT `tdw` files are CV-equal: GEANT_Neutron_0, GEANT_Neutron_1 and GEANT_Pion_0 share sha256
    `c0ae3c18…` (review measurement).
  - So `denominator(bank cv.npz, GEANT_*_tdw)` must equal the dump's `GEANT_*_denom_nd`, which reproduces the CV
    (`detector-dump.json`, `cv_reproduced`).
  - Flux fails closed by itself if the file's CV flux differs from the npz's (`flux_universe.py:202`);
- the per-task step wall and MaxRSS are recorded. A comparable `s5p_universe` job used 18.95 GB at `--mem=56G` (job
  58916065).

**Re-pricing rule:** if any pilot step wall exceeds 1,500 s, production is re-priced before binding. Then 11 waves
take 16,500 s, 13 % under the 5:15 limit.

### 3.2 Production: 170 universe unfolds, cap 10.5 CPU node-h

- **Packing:** 2 jobs × 8 lanes × 11 waves, giving 176 slots for the remaining 170 universes.
- **Wall per job:** at most 11 × 1,370 s = 4.19 h. Limit 5:15 (≥ 1.25 × 15,070 s), so the cap is 2 × 5.25 =
  **10.5 node-h**.
- **Expected:** 2 × 11 × 1,256–1,370 s gives 7.68–8.37 node-h, wave-quantized **(arithmetic)**.
- **Checks:** the same health checks as the pilot, on every product. The counts must be exact: 100 flux, 69 model and
  8 detector, with the pilot's 7 included.
- **Storage:** about 95 KB per product (the s5p R data products are 94–96 KB), so 177 products come to about 17 MB.
  Logs are under 10 MB. A durable HPSS copy follows, with hashverify.

### 3.3 Readout and assembly: login node, 0 node-h

`s5p_assemble.py` assembles on the reporting definitions directly. RD2 is the reported H2 cells plus the total: 27 + 1 =
28 functionals (`nd-unfolding/s5p_assemble.py:5-7, :42, :55-70, :116-137`).
- It gives C_stat (ddof 1), the per-band C_b including the lateral bands, and C_norm = (0.014 f)(0.014 f)ᵀ.
- It fails closed on `--expect-universes`.
- C_model, the unscaled M2 of the decision, is S2's question and sits beside these blocks.
- **The tool does not compute the decided total.** `--envelope-scale` is required (`s5p_assemble.py:104`; `--priors` defaults
  to none, `:103`), and it builds the
  bounded envelope h (`s5p_assemble.py:18-23, :138-142`), not M2's Σ s sᵀ.
  - So the readout needs either a run with no priors at scale 0 plus a separate combination with C_model, or a code
    change. Either is login-node work, but it is code to write and review.
- Its docstring says "RD2 = the 32 H2 cells" (`:5-7`). The code keeps only the reported 27 (`:65-69`). Its output does carry
  `prior_shifts` (`:138-141`), from which Σ s sᵀ can be formed.

**Choices to declare before any product is read:**

| choice | options | what the record says |
|---|---|---|
| **centering of each universe band** | about the matched CV, or MAT mean-centered (z-cv's per-band convention) | z-cv's per-band blocks are mean-centered (`docs/analysis-note/sec_5d.tex:621-622`). `s5p_assemble.py:14-15` centers on the CV and labels that the adopted "cv" convention, but in z-cv "cv" names only the throw's centering (`sec_5d.tex:621-639`). So the label looks wrong **(inference)** |
| **the lateral bands' reference** | (i) mean-centered, Δ_b = (f₁ − f₀)/2 per two-endpoint band, as s5p's own null work did (`nd-unfolding/s5p_joint.py:9, :108`), 0 node-h but an `s5p_assemble` change; (ii) an R float32 sentinel-free CV unfold, 1 unfold (about 0.05 node-h) plus a `--drop-sentinel-rows` path, which only `s5e_trace.py:477` has | the laterals lack the sentinel rows (`campaign-state.json:247`). (i) ties to the centering choice above **(inference)** |
| **Rvp1pi** | keep, as z-cv does, or drop, as 2D does | 2D drops it because it "encodes the same shift as Rvn1pi" (`docs/analysis-note/sec_systematics.tex:28, :226-229`). Unfolding both costs 0.09 node-h, so the choice is free to make at assembly |
| **(a)'s inflation D** | omit (s5p_assemble has none), or build an (e) unified-throw ensemble | D came from (a)'s throw ensemble (`sec_5d.tex:597-611`). Option O3 prices an (e) version; it is not recommended. The joint-throw inflation is limited to the five-axis covariance (`sec_systematics.tex:285-288`), and no joint throw has tested the 2D block sum (`:290-292`, comment) |
| **C_stat replicas** | set A (50, refit with jitter) or set B (100, bootstrap only) | set A carries the absorbed numerical component (amendment-4:12). For RD2's 28 functionals, 50 replicas allow a full-rank estimate (rank ≤ 49) **(arithmetic)**. Option O1 extends set A to 100 |
| **GEANT source** | the detector dump (preferred by `s5p_nullexp.py:25-28`) or the bank copies | the two differ in `wr` (§1, row 6) |
| **combining C_model** | as above: a scale-0 run plus a separate sum, or a code change | DECISION-20261024 item 3 |
| **final reporting cells** | H2's 27, or a declared merge or restriction | DECISION-20261024 item 2; see §5 |

<!-- absence-ok: "s5p_assemble has none" is a read of nd-unfolding/s5p_assemble.py:9-25 (its component list names no inflation); the 2D statement cites sec_systematics.tex:285-292 directly -->
Search: inflat in docs/analysis-note/sec_systematics.tex (hits :287-288, :292, :575, all five-axis); inflation in nd-unfolding/s5p_assemble.py @ 2c8c1e4f

**Readout checks:**
- PSD;
- the band count equals the declared set;
- C_stat's rank;
- per H2 cell, the share of each component.
- Also a **descriptive** comparison of the (e) total with z-cv projected to H2, both relative to their own central
  values. Stage 0 mixed them, adding (a)'s relative z-cv to (e)'s blocks (`stage0_analysis.py:301-314`).

### 3.4 Options, each separately priced (not in the caps above)

| option | what | unfolds | expected, CPU node-h | cap | recommendation |
|---|---|---:|---:|---:|---|
| O1 | 50 more set-A replicas, b51–100 (float64) | 50 | 1.97–2.24 | 3.2 (1 node, 7 waves, 3:10) | not needed. The H2 bootstrap σ median is 0.29 %, against a total σ ≥ 6 % (`RECORD-20260927-s5p-stage2-exit.md:39-40, :52-53`) **(inference)** |
| O2 | an estimator-seed block, as RE-2's P6(i): 20 replicas × 3 more seeds | 60 | 2.36–2.69 | 3.6 (1 node, 8 waves, 3:35) | first read s5e's B0 (not (e)) data runs at estimator seeds 42/43/44 (`state/s5e/contract-amendment-1-diagnosis-execution.json:16`) and amendment 3's seed-43 item (`:58, :127`), at 0 node-h. I have not read their results |
| O3 | an (e) unified-throw ensemble, to reproduce (a)'s D | 162 (160 throws + 2 null) | 7.06–7.71, plus throw tooling for R | unpriced (tooling) | not recommended. z-cv's D is an (a) construction, and the community-standard route does not require it **(inference)** |
| O4 | HPSS copy of the bank and detector dump | 0 | 0 | — | recommended if production cannot start before about 2026-12-14 |

## 4. What carries over from (a)'s 5D covariance (`sec_5d.tex:561-680`)

z-cv stores only its total (`hCov_combined5d_total_uthrow`), the inflation g, the masks, the row index and (a)'s
central (`nd-unfolding/z_build.py:732-739`). Its per-band blocks are in its input files. No unfolded block is reusable
under (e).

| (a) component | carries over to (e)? |
|---|---|
| Σ_V C_b, 13 vertical bands (12 model knobs + Flux); Σ_R C_b, 27 residual bands | **the inputs do; the blocks do not.** The weights and per-universe background weights are estimator-independent. The blocks are (a) LightGBM purity unfolds, and are rebuilt as §3.2 |
| Σ_A L_b, 5 re-selected lateral bands | **the inputs do, and the (e) unfolds already exist** (§1, row 7), but they need the reference chosen in §3.3. (a)'s came from `std_final5_candidate.root` (`950f8cb1…`) |
| C_stat, 100 (a) replicas, data and signal MC only | **does not.** The (e) sets A/B exist and also resample the background template (`s5p_assemble.py:9-10`) |
| C_ML, 24 split-seed replicas | **does not.** It is specific to (a)'s training (`sec_systematics.tex:530-536`). (e)'s numerical component is absorbed in set A (amendment-4:12) |
| D = diag(g), from 160 unified throws plus 124 donors | **does not**, and is optional (§3.3, O3) |
| normalization 1.4 % flat | **the rule does** (`s5p_assemble.py:16, :136`), applied to (e)'s own central value |
| central value and the 10,694-cell support mask | **does not.** (e) has its own central value. H2 assembly from each product's full 65,856-cell `xsec_flat` needs no fine support mask **(inference)** |
| the known limitations: seed sensitivity, 5 pinned lateral bands, conditioning (`sec_5d.tex:640-715`) | **do not transfer as numbers.** For (e) they are unmeasured, and the conditioning of a 27-cell matrix is a separate measurement | <!-- absence-ok: follows from row 12: no (e) covariance exists, so none of its seed, pinned-band or conditioning measurements can exist -->

## 5. What the H2 cells need that J or EW did not

1. **Declare the cells before reading.** DECISION-20261024 item 2 allows merging or restriction "provided it is declared
   before any refined-estimator data result is read". The universe products are refined-estimator data unfolds.
   - So the final cells should be declared before §3.3 reads any product. The pilot's checks (§3.1) compute no cell
     values for the same reason.
   - **For the director, three questions:**
     - does making the pilot's products, and its finite and non-negative check on fine-cell values, count as
       reading?
     - does the existing (e) central value, which Stage 0 already read on H2, count as already read?
     - does this plan's quoting of the H2 data-bootstrap σ (item 8) count?
   - The safe order is to declare the final cells before the pilot is bound **(inference)**.
2. **Mapping.** H2 is a 2⁵ partition: 32 cells, keeping all 32 with a reported mask, like EW's 42
   (`nd-unfolding/s5p_stage1_inspect.py:47-48, :77-96`). J instead drops unsupported cells to −1.
   - So the 27 × 27 matrix is a selection by `reported` (`stage0_analysis.py:308`).
   - Every edge is a fine-grid edge, so the projection is exact (`s5p_stage1_inspect.py:85-87`).
3. **Five unreported cells: 2, 6, 10, 14 and 17** (`state/s5p/contract-amendment-1-use-case-and-targets.json:48`).
   - The first four are the (p_T < 0.7, q₃ ≥ 2, W < 1.8) cells. With W² = (M̄ + q₀)² − q₃²
     (`sec_eavailw.tex:109-114`), they are kinematically forbidden **(inference from the arithmetic)**.
   - Cell 17 is allowed but sparse: 553 expected reco signal events against the 1,000 rule.
   - They hold 0.0156 % of the expected reco signal, and stay in the total.
4. **Partial fine support.** Every H2 cell contains fine cells with zero (a) central value. For example, H2_21 has 10 of
   1,944 fine cells in z-cv's support.
   - Building from each universe product's full `xsec_flat` avoids that mask **(inference)**.
   - (e)'s own mass outside z-cv's support is unmeasured. That matters only for a fine-cell matrix. <!-- absence-ok: names a quantity this plan did not compute; it needs the (e) central and z-cv's mask, both cluster-only, and no record of it was found by the H2 read of stage0 receipts and s5p records -->
5. **Low-purity cells.** H2_25 (0.007), H2_11 (0.012), H2_9 (0.028) and H2_1 (0.035) have joint purity far below the
   0.31 median (`state/s5p/stage1/stage1_inspect.json`, `mc.H2`).
   - Their results lean on the background model, which (e) refits per universe **(inference)**.
   - They are candidates for a declared merge.
6. **Acceptance holes and within-cell shape.** 10 of the 27 cells have acceptance holes at the split truth grid, against
   7 of 109 for J. The width is 2.9 % with the within-cell shape fixed by MC, and 54.0 % with it free
   (`state/measurement-paper/PLAN.md:369-373`).
   - This is model dependence: it belongs with S2's C_model and with the paper's limitations, not with this
     covariance.
7. **The GiBUU domain does not fit H2's edges.** The paper restricts GiBUU to p_∥ < 6 GeV
   (`docs/analysis-note/paper_body.tex:245-246`), but H2's p_∥ edge is 4.5. So GiBUU comparisons on the high-p_∥ cells
   need a stated treatment **(inference)**.
8. **Precision.** The reported cells have 1,999–791,779 expected reco signal events. Their data-bootstrap σ is 0.12–0.52 %
   (median 0.30 %) (`stage1_inspect.json`; the stage-0 H2 replicas). So the covariance will be systematics-dominated
   **(inference)**.

## 6. Summary of costs

| stage | CPU node-h, expected | cap | GPU | storage |
|---|---:|---:|---|---|
| pilot (8 unfolds) | 0.35–0.38 | 0.5 | 0 | < 1 MB |
| production (170 unfolds) | 7.68–8.37 | 10.5 | 0 | about 17 MB, plus HPSS copy |
| readout | 0 (plus code: the lateral reference and the C_model combination) | 0 | 0 | < 50 MB (assembled matrices, JSON) |
| **total** | **8.0–8.8** | **11.0** | **0** | **< 0.1 GB on pscratch; nothing on CFS** |

- **The comparable earlier figure.** DESIGN.md priced 288 unfolds at 15.9–18.4 CPU node-h, admitted (× 1.25 / 0.8),
  once the inputs existed (`DESIGN.md:368`). That is 10.2–11.8 before admission, the figure comparable with this plan's
  expected 8.0–8.8 **(arithmetic)**.
- **Why this is smaller:** 111 of those 288 already exist under R: the central value, a bootstrap set and the 10
  laterals. No new event loop is needed **(arithmetic, from §1)**.
  - The 111 count holds with set B, the 100 bootstrap-only replicas. With set A's 50 it is 61.
- **The options add** up to 6.8 node-h of caps (O1 + O2). O3 is not recommended.

## 7. Unchanged

- MP-2 stays held, and Stage 0 is held.
- No claim, target or endpoint changes. No GPU request.
- Any compute here needs Joseph's approval, then a declaration and a binding.
