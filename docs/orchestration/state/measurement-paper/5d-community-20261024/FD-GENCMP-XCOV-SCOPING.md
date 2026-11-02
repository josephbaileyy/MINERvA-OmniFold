# SCOPING: the covariance between the 2D result and the sixteen-cell result, per (p_T, p_∥) quadrant (2026-11-01)

**By** the limitation-resolver lane (Claude), for the director.

**Under** [`DECISION-20261101-joseph-gencmp-paper-adoption.md`](../../../DECISION-20261101-joseph-gencmp-paper-adoption.md)
(#651) item 5: "whether the 2D result and the 16-cell result share bootstrap and systematic replicas from which their
covariance can be computed, and at what price". Any compute it proposes falls under
`DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md` and needs the director's binding first.

**MEASURES:** what pairing exists between the two results' covariance blocks, by code, digests and committed records,
and from names and `stat` on pscratch. It also gives the price of each route from measured per-unfold costs, and the
rule and paper text fixed before any number is read.

**How it was measured:** committed files at `origin/main` `da277773`, read in a detached worktree. The cluster was
touched only by `ls` and `stat` on saul login nodes (§8). No covariance value, quadrant sum or cross quantity was
computed, and the one deviation is in §8.

**CANNOT AUTHORIZE:** any run, any paper edit, or any change to step C's bound rule.

**CITABLE FOR:**
- which blocks pair, which pair only after a check, and which cannot;
- the routes and their prices;
- the rule proposed for binding.

**NOT CITABLE FOR:** a correlation value; the outcome of the test; a validation of either covariance.

Base for every `file:line` below: `da277773`. "[I]" marks an inference.

## 0. The answer in brief

1. **The 2D result is `E_R` with `Q_R`, not `E_U` with Q.** `DECISION-20261024-joseph-adopt-re2-2d-refined.md:30`
   reads: "The adopted 2D result is `E_R`, with `Q_R` as its headline uncertainty. This replaces `E_U` and Q."
   - GENCMP step C (declaration §4, INPUTS family F) and the brief for this scoping both named `E_U`
     (`4f5a1b6d…`) and Q (`8ccb4d72…`). This lane wrote the declaration, so the miss is first of all its own. The
     director has confirmed it and ruled that step C be rerun on `E_R` and `Q_R` as step C-R (declared with
     amendment E). Everything below is about `E_R` and `Q_R`.
   - The pins:
     - `Q_R` is `combination/s5_plus_playlist.npz`, `b57d6c96…` (`RE2-PARTC-REPORT.md:132`).
     - `S5_R` is `631cf255…` (`:131`).
     - `C_PL_R` is `playlist/playlist_term.npz`, `dbb067aa…` (`:129`).
     - `E_R` is part B's `out/ER/xsec.root`.
2. **(a) Statistical replicas: they share seeds and laws, but not draws.** Both sides use
   `default_rng(b)`, `default_rng(b + 10,000,000)` and `default_rng(b + 20,000,000)` for the data, signal-MC and
   background streams. Every draw is positional over each side's own row arrays, and neither side carries an event
   key.
   - The data and background arrays differ in length and order, so a shared seed does not give a shared draw.
   - The MC arrays have the same length (32,849,103). Whether their order is the same is unrecorded.
   - Pairing the existing replicas by seed would therefore give the same Poisson number to *different* data events,
     a spurious coupling. The existing replicas cannot measure the statistical cross term.
3. **(b) Systematic universes: they pair one to one by name and index, and the weight files differ.**
   - **The same:** the 38 bands and 175 universes, the 5 lateral bands from the same active files, the flux
     universe file, the constraint weights in the same order, the X01 factors and the 1.4% normalization rule. Each is
     identical by digest or by code.
   - **Different:** the per-universe event weights come from two different 171 GB omnifiles, and no committed
     control compares them. Settling it needs one read-only check, V1 (§5).
4. **(c) The other blocks:**
   - **C_PL vs C_PL,5D:** the same three periods and the same construction rule, so a period-paired cross term can
     be built from existing files.
   - **C_model:** the 5D vertices pair with C_model,2D beside `Q_R`, but `Q_R` itself holds no model block.
   - **No 2D partner:** C_resp, the QA/QB unreported-box term and 2D's C08_R. The 5D seed block is exactly 0.
5. **(d) The cheapest route that makes step C a test** (route A) costs ≤ 2.0 CPU node-h of caps. It consists of:
   - a 0.25 node-h probe, then the V1 weight check;
   - the row-order check V0;
   - the cross blocks on a login node from products already on pscratch and HPSS, at 0 node-h.
   It measures every systematic pairing and bounds the statistical one over [0, 1]. Route B adds the statistical
   pairing: 100 new 5D replicas whose draws are mapped from the existing 2D replicas, 2.28 node-h measured basis,
   ≤ 4.5 node-h in all.
6. **(e) The rule:** per quadrant, z = d/σ_d with σ_d² = σ₁₆² + σ₂D² − 2K and K the measured cross covariance;
   "agree" if |z| ≤ 2. Under route A the statistical cross term spans [0, 1], so a middle outcome with its r* remains.
   §6 fixes the paper text for each outcome.

**What the test can now do:** with ρ measured, step C stops being a bound. GENCMP's ρ* were 0.989–0.9999
(`FD-GENCMP-REPORT.md` §2.3, on `E_U` and Q). If the measured ρ exceeds a quadrant's ρ*, that quadrant reads "differ".
That outcome is possible, and §6 provides for it.

## 1. The two results and their blocks

| side | central | reported covariance | blocks | record |
|---|---|---|---|---|
| 16 cells | f = U x, P5 (`k1_p5_rerun.npz` `e36f3b25…`) | C_total + C_resp + C_PL,5D, C_total = C_e + C_model_abs | C_e = C_stat + Σ_b C_b (38 bands) + 5 laterals + C_norm + C_seed (`s1_assemble.py:11-23`); 46 blocks in the committed readout `s1/readout/s1_assembly.json` (`81e5ef3f…`) | `fd/with-cpl/data-product/fd_data_product_cpl.json` |
| 2D | `E_R` (refined estimator, RE-2) | `Q_R` = S5_R + C_PL_R | S5_R = universe (38 bands + 10 S3 laterals + normalization) + stat + C08 (`re2c_rollup.py:12-13`, `:467-480`; S5 rule `stageC/production/DESIGN.md:273-276`) | `RE2-PARTC-REPORT.md:129-134` |

Beside `Q_R`, but not in it: C_model,2D. The users' total is `Q_R` + C_model
(`DECISION-20261024-joseph-adopt-re2-2d-refined.md:31-32`).

## 2. (a) The statistical replicas

| | 2D `Q_R` stat (RE-2 S1) | 16-cell C_stat (S1) |
|---|---|---|
| replicas | 300, `--bootstrap-seed 1…300 --bootstrap-streams three --seed 42` (`re2/run/partb_runs.tsv:190` onward) | 50, b = 1…50, jitter seed 100 + b (`s1_assemble.py:54`, `:316-321`) |
| producer | `re2_driver.py` `38ff3705…` | `s5p_numerics.py` → `s5n_pseudo.bootstrap_replica` (`s5n_pseudo.py:207-219`) |
| data stream | `default_rng(b).poisson(1, n)` over the window's data rows (`re2_driver.py:2087`, `:2094`): **4,091,707** rows, closed window 0 ≤ p_T ≤ 4.5, 1.5 ≤ p_∥ ≤ 60 (`stageC/pilot/p1/evidence/test_noop_report.json:163`; `ASSESSMENT-20261008-2d-estimator-pairing.md:72-73`) | `default_rng(b).poisson(obs_counts)` over the observed rows (`s5n_pseudo.py:210`, `:214`): **4,091,579** rows in the half-open 5-axis window (`state/s5e/cand/review2/r2_integrity.json:15116`; `s5n_pseudo.py:105-110`, `:194-200`) |
| signal-MC stream | `default_rng(b + 10,000,000)` over `sig["w_truth"]`, 32,849,103 rows, applied to w_truth and w_reco (`re2_driver.py:2088`, `:2095`) | `default_rng(b + 10,000,000)` over `w_truth`, 32,849,103 rows (MCgen), applied to both (`s5n_pseudo.py:211`, `:215-217`) |
| background stream | `default_rng(b + 20,000,000)` over **all 658,227** `mc_background` entries, applied by entry index to the in-window rows (`re2_driver.py:377-384`, `:2103`, `:2178`; entries `test_noop_report.json:43`) | `default_rng(b + 20,000,000)` over the **621,445** in-window template rows (`s5n_pseudo.py:212`, `:218`; `r2_integrity.json:15117`) |
| event key | none: the driver reads `measured`, `measured_pz` and `measured_pass` only, and the CV omnifile has no identity branch (`DESIGN-20261008-2d-independent-statistical-validation.md:177-184`) | none: `nn_dump_inputs.py:92-103` saves no key array |

**Do they share per-event Poisson weights? No.**
- **Same seeds and offsets.** The seed offsets are the same, and seeds 1–50 occur on both sides.
- **Data stream.** The two arrays differ by 128 rows, and no row correspondence is recorded. A draw at position i
  therefore lands on different events once the first unmatched row is passed [I: the 128 rows' positions are
  unknown].
- **Background stream.** The 2D side draws over 658,227 entries and the 5D side over 621,445 rows, so the draws do
  not line up.
- **MC stream.** The lengths are equal. The 5D MCgen order is G2's `mc_signal_reco` in playlist order 1A…1P,
  bitwise (`mp2/S0-S1-REPORT.md:23-25`). No control compares the 2D omnifile's `mc_signal_reco` order with it.
- **The consequence.** Pairing existing replicas by seed would assign one Poisson number to two different data
  events. Their sample cross covariance would then contain a spurious term of order N·ḡ₁₆·ḡ₂D, in place of the
  per-event Σ_e g₁₆(e) g₂D(e) [I, from the draw law]. **The existing replicas cannot give the statistical cross term
  by any reuse.**

**Correction, made before this report.** An interim note of this lane's cited 2,586,886 observed rows from
`S1-REPORT.md:414-416`. Those are replica b1's counts after the draw: `signed_sample` keeps rows still weighted above
zero (`s5n_pseudo.py:221-227`). They are not the window count. The conclusion above does not depend on them.

**The populations are nearly the same.** The window counts differ by 128 data rows and 102 template rows. That makes
a key join by ordered subsequence on exact coordinates plausible [I]: the two sides read the same data, in the same
playlist order, through slightly different windows. Route B rests on it (§5).

## 3. (b) The systematic universes

**Names and indices: identical.**
- On pscratch, `2d-closeout-re2-20261023/partb/out/U_*` holds 175 directories and `s1-20261024/runs/uni/S1_*.npz` 175
  files plus `S1_CV.npz`.
- Their band:index name sets are identical, compared by name only (`ls`, §8).
- The records agree: RE-2 J2's 175 rows (`RE2-DECLARATION-B.md:177`) and S1's `EXPECT` and `MODEL_BANDS_2`
  (`s1_assemble.py:55-65`, required exactly at `:169-191`).
- Rvp1pi is dropped on both sides (`s1_assemble.py:182-183`; `RE2-DECLARATION-B.md:177`).
- The 5 lateral bands come from active-file unfolds on both sides: RE-2 J3's 10 and S1's `lat_<band>_{0,1}`.

**Inputs identical by digest or code:**

| input | 2D (`Q_R`) | 16 cells | same? |
|---|---|---|---|
| flux universe file | `flux_integral_universes_MEFHC.root` `5eecae84…` (`stageC/production/DESIGN.md:49`; RE-2 `re2_env.sh:15-16`) | the same `5eecae84…` (`S1-PLAN.md:71`) | yes |
| Flux constraint weights | `sorted_NuEConstraint_FHC_RHC_IMD.txt` `e38ad7d2…`, entries 0–99 in index order (`s5_rollup.py:161-167`; `re2c_rollup.py:93`) | the same file, entries < 100 sorted by index (`s1_assemble.py:133-144`) | yes |
| lateral sources | `active_universe_5d/standard/merged/*_active_*.root`, CFS copies with source and destination lists both `73775251…` (`stageB/diagnostics/copy/SHA256SUMS.active.{src,dst}`) | the same pscratch paths (`state/s5p/s3-latdump-tasks.tsv:2-10`) | yes, by path and the 2026-10-12 digest list; the dumps recorded only paths [I: files unchanged between] |
| X01 (`Muon_Energy_MINOS`) | `minos_rescaled.npz` `8912376e…` (`re2c_rollup.py:88-89`) | the same (`s1_assemble.py:45`) | yes |
| normalization | rank 1, 0.014 (`re2c_rollup.py:100`) | rank 1, 0.014 (`s1_assemble.py:50`, `:343`) | yes |

**The per-event weights per universe: not shown to be the same.**
- **2D.** `w_truth_<B>_<i>`, `w_reco_<B>_<i>` and `w_bkg_<B>_<i>` are read from
  `2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root` (`220c479e…`, 171,117,087,867 B, mtime 2026-07-08;
  `unfold_2d_omnifold_unbinned.py:270-302`, `:470-498`; the omnifile's branch list,
  `DESIGN-20261008-2d-independent-statistical-validation.md:177-184`, is for the CV file).
- **16 cells.**
  - Every universe reads the bank `nd-unfolding/bank_sweep_5d_bkgaware/{B}_{i}_{wt,wr,tdw,bkgw}.npy` for `wt`, `wr`
    and `bkgw`. The 167 outside the four detector bands also take `tdw` from it. Its 701 files
    are digested in `stageF/methods/sf1/manifest/inputs-sha256.txt` (`3a50f502…`). The bank was built by
    `sweep_bank_5d.py --dump` from `nd-unfolding/runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root`
    (171,117,093,365 B, mtime 2026-07-13; `AUDIT-FINDINGS-20260820.md:55`).
  - The 8 universes of the four detector bands (GEANT_Neutron, GEANT_Pion, GEANT_Proton and MinosEfficiency) take
    `denom_nd` from the detector dump instead (`s5p-20260926/bank_detector/`; `s1_assemble.py:57`, `:221-225`).
- **What is unchecked.** Same branch names, different files (5,498 B apart). The only weight checks on record are
  inside the 5D side:
  - the bank's CV against the npz rows, except 2,801 sentinel rows (`s5p_universe.py:64-80`);
  - a known difference between the bank's GEANT `wr` and the dump's (`S1-PLAN.md:72`).
- [I] The two files are sibling outputs of the same MAT event loop. That is a hypothesis, which V1 tests.

**The estimators.**
- **2D universes:** refined, `--seed 42` on all 175 rows (`re2/run/partb_runs.tsv`). The estimators use seed, seed + 1
  and seed + 2, and the refinement 400/31 uses seed + 3 (`RE2-DECLARATION-B.md:190-195`).
- **5D universes:** configuration R. All three estimators use seed 42 and the refinement 400/31 uses 45
  (`s1_assemble.py:194-216`). The 5D seed block is exactly 0 (`S1-REPORT.md:34`).
- The two estimators' training noise is independent, so it drops out of the cross term in expectation and stays in
  each side's own variance [I].

**What a pairing gives.**
- For each band, K_b = (1/N) Σ_u (X₁₆,u − X̄₁₆)(X₂D,u − X̄₂D)ᵀ, by each side's own rule:
  - MAT `CalcCovMx` mean-centred;
  - Flux weighted and centred on the weighted mean;
  - laterals as half-span outer products;
  - MINOS X01-rescaled on both sides.
- The universe products are exactly those inside each stated block (2D `re2c_rollup.py:467-480`; 5D
  `s1_assembly.json`'s `inputs_sha256`). So the joint universe matrix is a sum of outer products and is PSD by
  construction.

## 4. (c) The remaining blocks

| block | side | partner | cross term | what it needs |
|---|---|---|---|---|
| C_PL,5D, relative P = k Σ_X e_X g_X g_Xᵀ (`fd_ct_periods.py:421-426`), absolute diag(f) P diag(f) (`fd_cpl_addition.py:186-196`) | 16 | C_PL_R, v_X = √(k e_X) x g_X, C = Σ_X v_X v_Xᵀ (`2d-closeout/playlist-term/scripts/playlist_term.py:136-143`; RE-2 `re2c_playlist_term.py`) | **period-paired**: Σ_X √(k₁₆ e_X) √(k₂D e_X) (f∘g_X^16)(x∘g_X^2D)ᵀ. The periods are the same: PA = 1A–1F, PB = 1G/1L/1M, PC = 1N–1P (`FD-CT-5B-DECLARATION.md:58`; 2D `period-unfold-20261014/scripts/periods.py:10-12`). The flux files are equal (`:132`) | 5D g, e and k from the committed `fd/readout/fd_ct_5b_periods.json` (`a5b17895…`); 2D from `playlist_term.npz` `dbb067aa…`. 0 node-h. It is a **construction by the blocks' shared rule**, not a measurement |
| C_model_abs, SᵀS over GENIE+MEC, NuWro and GiBUU against Tune v1 (`pv-ladder/build_cmodel5d.py:5-10`, `:47`) | 16 | C_model,2D, the same three vertices, SᵀS (`DECISION-20261024-joseph-2d-model-dependence-component.md:39-45`), **beside `Q_R`, not in it** | **vertex-paired** (Σ_k s_k^16 s_k^2Dᵀ, scaled) **only if** the 2D side is `Q_R` + C_model; zero against `Q_R` alone, which has no model block | committed S matrices (`cmodel_5d.json`; RE-2 `cmodel_R.json`). 0 node-h. 5D's GiBUU shape applies below p_∥ = 10 GeV/c only (`build_cmodel5d.py:67`) |
| C_resp, per species d dᵀ of ±1σ recoil-response re-unfolds (`build_cresp.py:105-114`; `C-RESP-SPEC.md:82-91`) | 16 | none: 2D has no species-response row, and C10 is unpriced (`stageB/REPORT.md:314`) | 0 | — |
| QA/QB unreported boxes, P5 central ±100% (`FD-GENCMP-DECLARATION.md:243-246`) | 16 | none | 0 | — |
| C_seed | 16 | 2D C08_R | 0 exactly: the 5D block is identically 0 (`S1-REPORT.md:34`) | — |
| C08_R (seed main effect) | 2D | none (above) | 0 | — |
| C_stat / stat | both | each other | **not pairable from existing replicas** (§2) | route B |

**What the zeros mean.** Within the stated covariances, a block absent on one side can have no cross term. It enters
σ_d² in full. Those blocks set a floor on σ_d that no pairing removes. The readout prints each block's share of σ_d²,
so the floor is visible.

## 5. (d) The routes and their prices

**Measured per-unfold costs** (node-h = ElapsedRaw × billing / 256 / 3600):

| unfold | node-h each | basis |
|---|---|---|
| 5D configuration (e) data replica | 0.02281 | S1 seed job 60233154, 1.82500 for 80 (`S1-REPORT.md:136`) |
| 5D universe | 0.02283 | S1 P1 60233152, 2.00889 for 88 (`S1-REPORT.md:134`) |
| RE-2 2D replica | 0.04887 | J4a–c, 14.6609 for 300 (`RE2-PARTB-REPORT.md:58-60`) |
| RE-2 2D universe | 0.1220 | J2a–d, 21.3538 for 175 (`RE2-PARTB-REPORT.md:53-56`) |

**On disk** (names and `stat` only; §8):
- **2D:** `partb/out/` holds 175 `U_*`, 300 `S1_*` and 10 `S3_*`, each a 63 KB `xsec.root`. The part B archive is on
  HPSS: `mnv-re2-2d-rebuild-20261024/re2-2d-rebuild-20261024.tar` `0a64d4ff…`, 175 `U_` members
  (`RE2-HPSS-RECEIPT.md:19-38`).
- **16 cells:** `runs/uni/` holds 176 files and `runs/seed/` 80. The products archive is on HPSS:
  `mnv-5d-s1-products-20261024/s1-products.tar` `96181007…` (`S1-REPORT.md:506`). The bank is on pscratch, 701 files,
  and also on HPSS in `mnv-5d-s1-inputs-20261024/stage0-inputs.tar` `cc8353f7…` (`S1-PRESERVE-REPORT.md:61`).

**Route A: measure every systematic pairing and bound the statistical one. ≤ 2.0 node-h of caps.**
- **V0, row order (login node, 0 node-h).** Does the 2D universe omnifile's `mc_signal_reco` equal the 5D npz's
  `MCgen`/`MCreco` rows, position by position (2,801 sentinel rows excepted, as `s5p_universe.py:72-75`)? It reads
  coordinates only.
  - It fixes how V1 aligns weights.
  - It also gives route B's MC stream for free if positional.
- **V1, weight equivalence (one regular CPU job: a 0.25 node-h probe, then ≤ 1.75 node-h).** For each of the 175
  universes, compare the 2D omnifile's `w_truth_<B>_<i>`, `w_reco_<B>_<i>` and `w_bkg_<B>_<i>` with the bank's
  `wt`, `wr` and `bkgw`, and with the detector dump's `denom_nd` for the four detector bands. Rows are aligned by V0. The CV weights
  are compared as a control.
  - **Outcome per band:** identical (max relative difference ≤ 1e-6, float32 storage) or differs.
  - **A band that differs** leaves the measured set and joins the bounded set, with r ∈ [0, 1].
  - **Pricing.** No like-for-like timing exists for reading these branches. The probe reads one 2-universe band and
    Flux 0–9, and prices the rest before it runs. It aborts above 0.25 node-h.
  - **Reads.** The 2D universe omnifile (atime 2026-10-24) and the bank, both with O_NOATIME. The 5D bkgaware
    omnifile is not read: its atime is 2026-09-27, so by the 8-week rule it is exposed from 2026-11-22
    (`FD-CT-RETENTION.md:65`), and O_NOATIME will not reset that.
- **K, the cross blocks (login node, 0 node-h).** From the 175 + 175 universe products, 10 + 10 lateral products,
  period vectors and model S matrices, all named above.
  - **Controls first:**
    - K1: recomputing each side's own blocks from these products reproduces the stated blocks to 1e-12 (5D
      `s1_assembly.npz` per band; 2D `outA/cov2d_Q_205.npz` `7153b194…`).
    - K2: every joint block, and each quadrant's 2×2, is PSD.
    - K3: the V1 outcome table.
- **The statistical cross term in route A:** r × σ_stat,16 σ_stat,2D per quadrant, with r ∈ [0, 1]. Both results
  resample the same data, so the true r is positive [I]. It is not measured.
  <!-- absence-ok: a scoping statement about route A's design (the statistical cross term is bounded by construction, not measured), not a claim that a result does not exist -->

**Route B: route A plus the statistical pairing. Adds ≤ 2.5 node-h (2.28 measured basis), ≤ 4.5 node-h in all.**
- **The idea.** Keep the 300 existing RE-2 2D replicas unchanged. Run new 5D replicas whose draws are the 2D draws,
  mapped to the same events:
  - **data:** obs_count_i = b_data^2D[j(i)];
  - **MC:** positional if V0 passes;
  - **background:** tmpl_w_i × b_bkg^2D[entry(i)].
  The 2D draws are deterministic, regenerated from `default_rng` with the counts above.
- **J, the join (login node, 0 node-h).** j(i) maps each 5D observed row to its 2D window row, by ordered
  subsequence on exact float32 (p_T, p_∥). entry(i) maps each 5D template row to its `mc_background` entry.
  - **Control.** All 4,091,579 rows and all 621,445 rows are matched, order-preserving and injective, and the 128 and
    102 unmatched 2D rows are listed with the window edge that excludes each.
  - **If the join fails,** the data stream stays bounded and route B stops at a price of 0.
- **The draw check (login node).** The regenerated 2D draw sums for b = 1…100 equal those printed in the RE-2 S1
  logs ("data factor sum=… (n=…)").
- **The run.** 100 replicas × 0.02281 = 2.28 node-h, one regular CPU job of ≤ 3 h, from a fresh clone at the bound
  commit, with jitter seed 100 + b as S1's.
- **New code:** a replica builder that takes external draws, bound by blob digest. A test shows that, fed the native
  draws, it reproduces S1's `data_b1_j101.npz` bitwise.
- **Scaling.** The cross term is ρ̂_q σ_stat,16,q σ_stat,2D,q, with ρ̂ the paired sample correlation of the quadrant
  sums. Scaling by the stated σ keeps every 2×2 PSD, because the stated 5D stat block is from 50 different replicas.
  The jackknife SE of ρ̂ is printed.

**The price against the bar.** Route A is ≤ 2.0 node-h and route B ≤ 4.5 node-h. Half the group balance is
1,037 node-h, so neither goes to Joseph on cost. Writes go under a new `$B`, nothing to CFS. The HPSS copy is made at
the end, as before.

## 6. (e) The rule and the paper text, fixed before any number is read

**The quantities, per quadrant q.**
- S₁₆ and S₂D:
  - S₁₆ is the sum of the reported cells, with QA/QB's unreported boxes as in step C.
  - S₂D is `E_R` integrated over the quadrant's 2D bins with their areas (step C-R's inputs).
- d = S₁₆ − S₂D, and σ_d² = aᵀ C₁₆ a + bᵀ C₂D b − 2 aᵀ K b.
- C₁₆ is the reported matrix C_total + C_resp + C_PL,5D, plus the unreported-box term.
- K is the sum of the measured and constructed cross blocks of §3–§4, plus the statistical term (route B measured;
  route A r × σσ).

**The choice of C₂D is for the binding.** Recommended: **`Q_R` + C_model,2D, with C_model vertex-paired.**
- **Why:** both totals then carry the same three generator vertices, which is like for like.
- **The alternative:** `Q_R` alone, the headline (`DECISION-20261024-joseph-adopt-re2-2d-refined.md:30`). Then
  C_model₁₆ has no partner and enters σ_d² in full. That weakens the test by an amount the readout prints.
- **Either way,** the other choice is printed beside it, labelled.

**The outcome per quadrant.**
- **Route B (or route A when the statistical term is 0):** "agree" if |z| ≤ 2, otherwise "differ", with
  z = d/σ_d printed.
- **Route A:** evaluate z at r = 0 and r = 1.
  - **"agree":** |z| ≤ 2 at both.
  - **"differ":** |z| > 2 at both.
  - **Otherwise "agree only if r < r*",** with r* printed to four decimals.
- **Always printed:**
  - the 2×2 correlation ρ_q;
  - each block's share of σ_d²;
  - the joint χ² of the four d with their full 4×4 covariance, with its p-value (descriptive).

**Multiplicity, for the binding.** Four quadrants at 2σ each: if all agree and the quadrants were independent, the
chance of at least one "differ" is about 17% [arithmetic, 1 − 0.9545⁴]. The rule above keeps step C's per-quadrant
2σ, for continuity. The alternative is a joint χ²₄ at p = 0.05 with |z| ≤ 2.50 per quadrant (Bonferroni). The binding
picks one before anything runs.

**The paper text in each outcome.** Each replaces `paper_body.tex:119`'s first sentence, which stays until Joseph
rules (#651 item 5). The wording and the numbers go to Joseph with the readout.

<!-- absence-ok: proposed paper text for each outcome, fixed before any number is read; 'not measured' describes route A's design, not an absent result -->
| outcome | minimum text |
|---|---|
| all four agree | "Summed over each of the four (p_T, p_∥) quadrants, the sixteen-cell result agrees with the two-dimensional result within two standard deviations of their difference (largest \|z\| = …). Their covariance is computed from the systematic universes, lateral shifts and run-period offsets the two results share[, and from paired bootstrap replicas]." Route A adds: "the statistical correlation, which is not measured, is allowed anywhere from 0 to 1." |
| agree only below r* (route A) | "… agrees in every quadrant if the two results' statistical fluctuations are correlated by less than r*. Above that, quadrant … differs (z = …). That correlation is not measured." |
| any quadrant differs | **No paper text until the director and Joseph rule** (as GENCMP ruling 4). If it stands, the minimum is: "In the … quadrant, the sixteen-cell sum differs from the two-dimensional result by …% (z = …, with their measured covariance); the other quadrants agree. The cause is not established." It may not be dropped or softened into a bound |

**Unaffected in every outcome:** the 3D clause (note only, descriptive at σ₁₆; #651 item 4) and the three-observable
marginal sentence.

## 7. What stays uncovered, and its effect on the test

- **Blocks with no partner** (C_resp, unreported boxes, C08_R, and C_model₁₆ if C₂D = `Q_R`) enter σ_d² in full. That
  is correct within the stated covariances. It makes "agree" easier than a model that also correlated them would. The
  readout prints their share, so a reader can see how much of σ_d they are.
- **Route A's statistical term** is the only shared-data block left unmeasured. Its effect on z is printed at both
  ends of [0, 1].
  <!-- absence-ok: a scoping statement about route A's design (the statistical cross term is bounded by construction, not measured), not a claim that a result does not exist -->
- **The C_PL pair** is constructed by the two blocks' shared rule, not sampled. The readout labels it so and prints
  z with it set to 0 as a sensitivity.
- **A band failing V1** moves from measured to bounded, and the readout names it.
- **Estimator differences** (refined 2D LightGBM against 5D configuration R) are what the test examines. A "differ"
  says the two estimators' quadrant sums disagree beyond their stated uncertainties. It does not say which is right.

## 8. Deviations and how the cluster was touched, reported unprompted

1. **Matrix entries printed during a key walk (accepted by the director).**
   - What was printed: inspecting `fd_data_product_cpl.json`'s keys, the walk printed the first three entries of each
     matrix list's first row, three relative σ per block and the first correlation row.
   - What was not: no quadrant sum or cross quantity was printed or computed.
   - Every walk after it printed keys only.
2. **Writes on the cluster.** One `ssh` wrote two name lists (universe names from `ls`) to `/dev/shm` on a login node,
   diffed them and deleted them in the same command. Nothing was written on pscratch or CFS.
3. **Reads on the cluster.** Only `ls` and `stat` of directories and files, on 2026-11-01:
   - `2d-closeout-re2-20261023/{,partb,partb/out}`;
   - `s1-20261024/{,runs,runs/uni,runs/seed,products-hpss}`;
   - the three universe omnifiles and `bank_sweep_5d_bkgaware` (count only);
   - `s5p-20260926/bank_detector`.
   No file contents were read (`ls` and `stat` do not move atime; `FD-CT-RETENTION.md:52`).
4. **Delegation.** Three read-only subagents on this account searched the committed records under the same rule, with
   no values printed. This lane re-read every `file:line` this report relies on for a pairing verdict or a price.

## 9. For the binding

The decisions needed:
1. Route A or B.
2. C₂D: `Q_R` + C_model paired, or `Q_R` alone.
3. Per-quadrant 2σ, or joint χ²₄ with Bonferroni.
4. The C_PL pair: constructed, or set to 0.

Then the lane writes the declaration, with code bound by blob digest and tests, the controls above (K1–K3, V0, J and
the draw check) and the outcome table of §6. Step C-R is declared with amendment E, under the director's ruling.

Nothing is submitted, deposited or tagged.
