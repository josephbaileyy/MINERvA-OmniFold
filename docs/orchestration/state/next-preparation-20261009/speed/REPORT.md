# Session 4 — performance feasibility before a language rewrite

**CITABLE FOR:** where the measured cost of the named 2D and PET uncertainty procedures goes; the
measured fractions, local speedups and Amdahl estimates of two behavior-preserving loader changes;
full-procedure prices at 2×/5×/10×/100×; and the one follow-up benchmark this lane can specify.
**NOT CITABLE FOR:** Perlmutter throughput of any prototype (all prototype timings are laptop
measurements), scientific equivalence of any estimator, coverage, adoption, compute authority, or a
change to any quoted number or gate. Nothing here makes the overall publication-ready measurement
achieved.

| field | content |
|---|---|
| `Lane` | Session 4, speed |
| `Decision` | *Could an implementation change substantially reduce the cost of a specifically named future uncertainty procedure while preserving its estimator, and what is the smallest credible acceleration experiment?* |
| `Branch` / `Base` / `Head` | `prep/next-speed-20261009` / `5ac9706a21e8a5ac8863a65fd7623d8ab8d22269` (PR #61 merge; supersedes `901f0088`/`8eafd357` per the session prompt) / the commit that last changed this file; the reviewed freeze is named in `Review` |
| `Owned files` | everything under `docs/orchestration/state/next-preparation-20261009/speed/`, exactly: `REPORT.md`; `profile_from_sacct.py`, `costs.py`, `check_headlines.py`; `bench/make_synthetic_trees.py`, `bench/pinned.py`, `bench/test_prototypes.py`, `bench/bench_loader.py`, `bench/run_benchmarks.sh`; `proto/branch_status.py`, `proto/vector_loader.py`; `operands/sacct_59410433_steps.psv`, `operands/sacct_universe_sweeps_batch.psv`, `operands/sacct_exact_pilots_ki85_steps.psv`, `operands/perlmutter_env_and_inputs.txt`; `results/profile.json`, `results/costs.json`, `results/bench_loader_fill.jsonl`, `results/synthetic_trees.jsonl`, `results/test_prototypes.txt`, `results/startup_imports_local.txt`, `results/check_headlines.txt`, `results/review/` (reviewer output, if any). No other path in the repository was written |
| `Pinned inputs` | driver `2d-unfolding/unfold_2d_omnifold_unbinned.py` blob `e19aeb6d3c242a21a67fa1b4e4573ddf72729206` at the base (checked by `bench/pinned.py` before every import); `unbinned_unfolding/python/omnifold.py` at the base; A `ASSESSMENT-20261008-2d-estimator-pairing.md`, B `DESIGN-20261008-2d-independent-statistical-validation.md`, C `ASSESSMENT-20261008-2d-total-uncertainty-feasibility.md` and `state/uncertainty-preparation-20261008/c/costs.json`, all at the base; `state/ki84-rebuild-20261006/sacct_all.txt`; PET `nd-unfolding/pet/final_design/resources/cost_fb_look1-20260930.json` and `DECISION_RECORD-pet-final-design.md` at the base; read-only `sacct` of completed jobs `59410433`, `59409026`, `59409027`, `53116554`, `59466329`, `59466330`, `59469539`, `55677842`–`55677845` (2026-10-09, `operands/`); production file sizes, tree entries/branches and library versions read on a login node (`operands/perlmutter_env_and_inputs.txt`, §2) |
| `Resources` | §14: elapsed from 2026-10-09T19:59Z (cap 6 h); local CPU (cap 4 core-h); scratch peak 0.9 GB (cap 2 GiB); tracked ≈ 0.4 MB (cap 10 MiB); cluster 0 node-h, GPU 0, training 0, toys 0 (read-only `ssh` sessions ran `sacct`, `ls`, a log `grep` and one ROOT file open on a login node) |
| `Review` | see §11 |
| `Model / effort` | Claude Opus 5.5 (`claude-opus-5-5`), Claude Code; reasoning effort not observable to the session |
| `Disposition` | four decisions, §10: **D1 PASS** (bounded behavior-preserving opportunity on the universe-file procedures, including the exact-backend transfer measurement); **D2 INCONCLUSIVE** (CV-file LightGBM procedures; fraction bracketed, not phase-profiled); **D3 INCONCLUSIVE** for PET GPU training, **FAIL** for any wrapper/I/O/transpilation route; **D4 FAIL** — no implementation gain makes an infeasible procedure feasible once populations and estimator matching are reapplied |
| `Next action` | Joseph decides whether to authorize benchmark **SB1** (§9): ≤ 2 CPU node-h on shared/debug QOS, ≈ 1 h wall, no training beyond the three production-argument unfolds it repeats. It only matters if option (b) "measure the transfer" or option (c)'s matched seed-1 sweep is to be priced; it changes nothing for keep-and-disclose or N2 |

## 0. Session setup (campaign review §1)

The decision is the Goal 4 sentence above; a measured no-go is a valid terminal. One owner (this
session) and one fresh read-only reviewer, one initial review and one focused re-review after a single
repair batch (session prompt). Budget: Goal 4's 6 h / 4 core-h / 2 GiB, final quarter protected;
prototypes ≤ 2 active hours. Laptop: Apple M1 Pro, 10 cores, 16 GiB, macOS 26.6.2; other lanes ran
concurrently (load average 6–32), so every benchmark ran single-threaded, sequentially, with one
warm-up and 3–5 repeats, and the minimum is the operand.

## 1. Answer in brief

- **Where the money goes is not where a language rewrite would act.** Every classifier already runs
  in compiled code: sklearn's exact splitter (Cython, single-threaded), LightGBM (C++/OpenMP) and
  TensorFlow 2.15 kernels on A100s. The Python that remains is per-row PyROOT I/O and histogram
  filling in the 2D driver, plus PET's ≈ 1 % input loading.
- **The one large, measured, behavior-preserving opportunity is I/O on the universe omnifile.** The
  driver never calls `SetBranchStatus`, so every `GetEntry` decompresses all 470 branches of
  `mc_signal_reco` (and 236 of `mc_truth_denom`). Every one of 374 measured universe unfolds read
  **171.3 GB, the whole file**, to use 17 branches. The same CV unfold took **2,561 s on the universe
  file against 778 s on the CV file**; that excess is 69 % of a universe task. Peak RSS on the
  universe file is **65–187 GB** against 14–17 GB on the CV file, and a local test reproduces the
  same proportionality (RSS excess ≈ 0.26–0.31 × bytes read) and its removal.
- **That changes a price Joseph would weigh, not a feasibility verdict.** For the exact-backend
  transfer measurement (A's option (b): `P03` N = 50, `P05`, `P09b`), the memory-safe packing on the
  universe file under today's driver is 2 exact unfolds per node, so `P05` costs **≈ 1,853 node-h**,
  not A's 128 or C's 285. With prototype 1 it returns to **≈ 125 node-h**. Wall time per exact unfold
  stays ≈ 19.3–19.8 h either way.
- **Nothing becomes feasible because of speed.** B's primary still costs ≥ 6,371 node-h even if every
  Python loop took zero time, and it still has zero disjoint production-size populations. C's P1 stays
  ≥ 117,000 node-h. N2 is already 10–12 node-h and blocked by non-computational gates. PET's repair
  costs 1.4 % of the remaining GPU balance and failed on interval construction, not cost.

## 2. The actual stack and inputs (measured, not inferred from `.py`)

| item | value | source |
|---|---|---|
| 2D CPU environment | `root_6_28` conda env: Python 3.11.14, ROOT 6.28/12, numpy 1.26.4, LightGBM 4.6.0, scikit-learn 1.8.0, xgboost 3.2.0, libgomp 15.2.0, OpenBLAS 0.3.30 | `operands/perlmutter_env_and_inputs.txt` |
| PET environment | NERSC module `tensorflow/2.15.0`, A100 40 GB, 2 runs per GPU (declared packing) | `nd-unfolding/pet/final_design/jobs/sbatch_guarded_task.sh:20`; PROTOCOL §6.7 |
| CV omnifile | 2,144,008,221 B; `mc_signal_reco` 32,849,103 rows × 7 branches (1.32 GB zipped); `mc_truth_denom` 32,849,103 × 3; `data` 4,119,797 × 3; `mc_background` 658,227 × 4; compression setting 1 | login-node ROOT read |
| universe omnifile | 171,117,087,867 B; `mc_signal_reco` 470 branches (112.1 GB zipped); `mc_truth_denom` 236 (57.7 GB); `mc_background` 240 (1.17 GB); `data` 6 | same |
| local | M1 Pro; ROOT 6.36.000 + numpy 2.4.4 + Python 3.13.7 (Homebrew) for ROOT work; Python 3.12.2, scikit-learn 1.6.1, TF 2.16.2 (miniconda) for import timing only | `results/*.jsonl` |

Estimator identities are A's (§2.1): `E_C` sklearn exact GBT, `random_state=None`; `E_S`, `E_U`,
`E_ML` LightGBM (100 trees, 8 leaves, seeds as A lists). PET's final designs are H2S1T24 (K = 5) and
L128S1T24 (K = 4).

## 3. Where the time goes, per estimator family (Perlmutter receipts)

Reduced by `profile_from_sacct.py` into `results/profile.json`. "Serial bound" is the largest
single-threaded wall time compatible with elapsed and TotalCPU if all other time ran k-wide; it
over-counts if serial phases spin extra OpenMP threads.

| workload (n) | elapsed s, min / median / max | busy CPUs (TotalCPU/elapsed), median | serial bound, median | MaxRSS GB | read GB | node-h |
|---|---|---|---|---|---|---|
| LightGBM CV-file replica, shared 64 (`59410433`, 300) | 544 / 840 / 1,900 | 30.9 of 64 | 53 % (41–61 %) | 14.4–17.2 | 2.20 | 0.0591 mean |
| same, full node, 128 threads (`59409026_1`, 1) | 778 | 51.6 | 60 % | 17.6 | 2.20 | 0.216 |
| KI-85 runs, shared 64 (51 queried) | 465 / 940 / 3,069 | 35.6 | 45 % | 12.9–14.9 | 1.38 | 0.065 median |
| exact GBT central `E_C` (`53116554`, 1) | 69,523 | 0.999 | 100 % | 17.2 | 2.22 | 19.31 |
| LightGBM universe unfold, full node (`55677843` purity, 187; `55677842` negweight, 187) | 2,350–2,369 / 2,547 / 2,735–2,751 | 17.6–17.9 of 256 | 87 % | 64.5 / 71.2 / 186.6 | **171.29 each** | 0.7075 median |
| CV unfold on the universe file (`55677844`/`45`, 2) | 2,561 / 2,597 | 19.0 / 17.7 | — | 76.4 / 71.5 | 171.29 | 0.71 |

What this decomposes into:

- **Exact GBT (`E_C`).** One busy core for 19.3 h. The per-row Python loops are 0.3–0.6 % of it
  (§4), I/O on the universe file would add ≈ 2.5 % (additive, below), and the rest is sklearn's
  compiled splitter. A wrapper or loader change cannot shorten its wall by more than ≈ 1.03×.
  Its **billing** is set by memory: a 17.2 GB process packs 29 per 511.5 GB node (A's 0.68 node-h
  assumed ≈ 28).
- **LightGBM on the CV file (`E_S`, N2, B's runs, C's P2/P3).** About half the wall is outside
  64-wide work. Local timing of the driver's own row loops at production row counts gives 235 s of
  pure-Python per-row work (≈ 109 s `GetEntry` reads, ≈ 126 s in six `TH2D.Fill` loops over 32.85 M
  rows). That is 28 % of the median replica if a Milan core is no faster per row than an M1 Pro core
  (assumed). The sacct serial bound caps it at 53 %. So `f_loop ∈ [0.28, 0.53]`. Contention also
  matters: identical work spans 3.5× (replicas) to 6.6× (KI-85) in elapsed on shared nodes.
- **LightGBM on the universe file (`E_U`, S-a, P1's universes).** The natural experiment above: the
  same CV unfold (no `--universe`) costs 2,561–2,597 s on the universe file and 778 s on the CV file,
  both on a full node at 128 threads. The 1,801 s excess ran at ≈ 3.9 busy CPUs. It is 69.5 % of a
  universe task (`f_io = 0.695`). n = 1 against n = 2 on different dates and nodes; the 374 sweep tasks
  (spread 1.16×) bound the variation of the latter.
- **Memory on the universe file.** RSS 65–187 GB. The 187 GB spikes land in different bands in the two
  sweeps (`max_rss_gb_by_band`), so they are not universe-specific. 14 (purity) and 17 (negweight)
  of 187 tasks exceeded the 121.9 GB shared-64 allocation, so C's optimistic "universe unfold on shared
  64 CPUs" rate is not executable as-is. Median RSS excess per byte of file = 0.31.
- **PET (H2S1T24, n = 352 FB runs).** Load 1.15 % median (max 1.63 %) of an unfolding's A100 time;
  iterations ≈ 2,520 s each at 2 runs per GPU. A committed step-2 receipt shows ≈ 29–35 ms per optimizer
  update at batch 512 for a ≈ 49 k-parameter model
  (`nd-unfolding/pet/final_design/results/step2int/B-Cpull1-pdg_onehot-eff-T0-D4d.receipt.json`: epoch 0
  66.6 s for 1,876 updates; 433.7 s for 8 epochs). Whether that is GPU-compute-, launch- or host-bound is **not recorded**
  anywhere: no GPU utilization or TF profile exists.
- **Process start-up and storage.** Local imports: ROOT 0.6 s, sklearn 1.7 s, TF 6.0 s
  (`results/startup_imports_local.txt`); under 0.3 % of any unit above. Output 0.06 MB per 2D unfold
  (C). Neither is a target.

## 4. Local measurements and the two prototypes

Synthetic `mc_signal_reco`-shaped trees (`bench/make_synthetic_trees.py`; production branch names and
types; ≈ 1 % adversarial rows: non-finite values, weights at and beyond `[0, 1e4)`, rectangle edges,
±4 ulps around the 20° cut, `sim_pass` ∈ {0, 1, 2}); with 192 extra `double` branches standing in for
universe columns (zlib-1, like production). Nothing is trained or fitted.

**Prototype 1 — `proto/branch_status.py`.** `SetBranchStatus("*", 0)`, then exactly the loader's
branches; the pinned `collect_signal_arrays_2d` runs unchanged. It found one real hazard and guards
it: `TBranch::SetAddress` is a no-op on a disabled branch, so a forgotten activation leaves the value
at its initial buffer for every row **and leaves no address behind to detect**. An after-the-fact
address check is vacuous (measured), so `ActiveOnlyTree` refuses `SetBranchAddress` on an inactive
branch at call time.

**Prototype 2 — `proto/vector_loader.py`.** `RDataFrame.AsNumpy` (single-threaded, tree order) plus
array masks, replacing the per-row loop. Two traps found and handled: ROOT 6.36 returns the `UChar_t`
`sim_pass` as a NumPy **bool** array whose bytes still hold 2, so the prototype tests the bytes; and
`math.atan2` versus `np.arctan2` at the 20° cut is re-evaluated with `math.atan2` within 64 ulps
(697 rows here; unguarded NumPy happened to agree on this platform, so the guard is defensive, not
shown necessary).

**Equality (`bench/test_prototypes.py`, `results/test_prototypes.txt`): 11 tests, OK.** Both
prototypes return byte-identical arrays (dtype, shape, every byte, `-0.0` included) to the pinned
loader on three trees × CV with and without weights, a vertical universe (`Flux:0`) and a lateral one
(`GEANT:0`). Negative controls, each caught by the same comparison: a missing activation (silent
wrong `w_reco`, then refused by the guard); `sim_pass == 1`; the bool-view bypass; `wt <= 1e4`; a
dropped angle cut; a wrong sentinel. Each mutation is asserted to change the source exactly once.

**Timings (`results/bench_loader_fill.jsonl`; µs per row, minimum of 5; M1 Pro, one thread).**

| pattern | CV-like tree (7 branches) | universe-like tree (+192 branches) |
|---|---:|---:|
| pinned `collect_signal_arrays_2d`, all branches active (production) | 2.05 | 11.73 (11.82 at 400 k rows) |
| prototype 1 (only needed branches active) | 2.06 | 2.59 (2.75 at 400 k) |
| prototype 2 (columnar) | 0.37 | 0.39 |
| pinned `collect_truth_denom_arrays` (3 branches) | 1.12 | — |
| per-row `TH2D.Fill` loop (driver pattern) | 0.638 | — |
| one `TH2D.FillN` call; contents, Sumw2, stats and entries byte-identical | 0.021 | — |

Peak RSS with 192 extra active branches rose by 74 MB at 200 k rows and 168 MB at 400 k (≈ 0.26–0.29 ×
bytes read). Under prototype 1 it returned to the 7-branch baseline (475 against 473 MB at 200 k rows).
That is the same linear signature as production's 0.31.

Derived (`costs.py`): prototype 1 removes 93 % of the local per-row excess (`s_io = 14.6` locally;
the bytes ratio 171.3 GB / ≈ 2.5 GB gives an analytical 68). Prototype 2 with `FillN` makes the 235 s
of production-scale loops 30 s (`s_loop = 7.7`, local).

## 5. Candidates, by category

Amdahl `S = 1/((1-f) + f/s)`. `f` is a Perlmutter measurement unless marked; `s` is local.

| # | candidate | category | applies to | `f` (regime) | `s` (regime) | `S` at measured `s` | `S` at 2 / 5 / 10 / 100 | ceiling |
|---|---|---|---|---|---|---|---|---|
| 1 | read only the needed branches (prototype 1) | 1, behavior-preserving (byte-identical inputs) | universe-file unfolds, any backend | 0.695 (LightGBM, full node) | 14.6 local; 68 analytical | 2.83 | 1.53 / 2.25 / 2.67 / 3.20 | 3.27 |
| 1x | same, exact backend | 1 | exact universe unfold | 0.025 (additive I/O, inferred) | as above | 1.02 | — | 1.026 wall; **billing ×14.9 via packing** (§6) |
| 2 | columnar loaders + `FillN` (prototype 2) | 1, byte-identical inputs and histograms | every 2D unfold | 0.28–0.53 (LightGBM CV file, shared 64; lower bound assumes Milan ≥ M1 per row) | 7.7 local | 1.32–1.84 | 1.16–1.36 / 1.29–1.73 / 1.34–1.90 / 1.38–2.09 | 1.39–2.11 |
| 2x | same, exact backend | 1 | exact CV unfold | 0.003–0.006 | 7.7 | ≤ 1.006 | — | 1.006 wall; RSS 17.2 → ≈ 8.5 GB **analytical** (lists → arrays), packing 29 → 60 |
| — | cache the loaded arrays across replicas (keyed by file digest, branch set, cuts, `pot_scale`, driver blob) | 1 | replica/toy loops | ≤ the read share of `f_loop` | ∞ on reads after the first | — | — | below candidate 2; adds staleness risk. Valid only because Poisson weights are drawn after loading (driver `:1643`); never across universes or pseudo-data draws |
| — | fewer threads / smaller allocation per LightGBM unfold | **2** (LightGBM output can change with `num_threads`; needs a declared tolerance against the ≤ 5.8e-9 rerun envelope) | CV-file LightGBM | the full-node run was only 7 % faster than the shared-64 median at 4× the billing | unmeasured | — | — | not ranked |
| — | faster exact-split trainer (presort, C++/Rust port) | **2** (`E_C` used `random_state=None`; tree-level identity is undefined, so equivalence needs `E_C`'s own seed noise, `P09b`, first) | exact | 0.994 | hypothetical | — | P05+P03+P09b at P1: 83 / 34 / 17 / 2.6 node-h | — |
| — | histogram GBT, mixed precision, XLA, larger batch, more PET runs per GPU | **2** (estimator/precision/backend changes) | exact → LightGBM is the existing `E_S`/`E_C` split itself; PET | — | — | — | PET at 2/5/10/100 on training: 1,609 / 666 / 351 / 68 A100-h | — |
| — | per-experiment intervals in a new form, fewer inner replicas (C's S1/S2), etc. | **3** (different uncertainty algorithm) | C's P3 | — | — | — | — | priced by C; not an implementation gain |
| — | PET loader/wrapper rewrite | 1 | PET | 0.0115 (max 0.0163) | — | — | — | **1.017** |

## 6. Full-procedure cost (node-h; `results/costs.json`)

`costs.py` re-implements lane C's admitted-total formula and first reproduces all six of C's published
totals to the third decimal (`lane_C_reproduction.all_within_0.01_node_h = true`), then changes only
the unit rates a candidate touches. Retry, verification, development, setup and the 20 % protected
reserve are C's. Comparators: `m3246` CPU 3,040.6 node-h remaining, 20,000 annual; `m3246_g`
55,107 GPU node-h remaining (B §14, 2026-10-09). They are comparators, not ceilings.

**Unit rates.** LightGBM universe unfold: C optimistic 0.132 (assumed shared 64), C conservative 0.5
(documented "~30 min" on the May sweep's file), **measured 0.7075** (full node, current 171 GB file);
with prototype 1: 0.250 full node, 0.067 shared 64 (contingent on RSS ≤ 121.9 GB, local evidence
only); with prototypes 1 + 2 on shared 64: 0.040–0.053. LightGBM CV-file unfold: 0.0591 → 0.032–0.044
with prototype 2. Exact unfold: 19.31 as run, 0.666 packed 29/node; exact universe unfold under
today's driver 9.91 at the memory-safe 2/node (2.83 at the median-RSS 7/node, with OOM risk), 0.667
with prototype 1, 0.322 with 1 + 2 (analytical).

| named procedure (estimator) | as priced by A–C | at measured current rates | prototype 1 | prototypes 1 + 2 | wall-time effect |
|---|---|---|---|---|---|
| **exact-backend transfer**, `P03` N = 50 + `P05` + `P09b` (`E_C`) | 168.6 (A) / 326.2 (C ratio); admitted 242 / 469 | **1,893.1** (P05 1,853.1); admitted **2,721** = 0.89 × remaining CPU. Median-RSS packing: 569.9 | **165.4** (P05 125.4); admitted 238 | 79.9 (analytical); admitted 115 | 19.3–19.8 h per exact unfold in every column. P05 at 30 nodes: 4 waves today, 1 with P1 |
| same at `P03` N = 300 | 205–215 for P03 (A) | 2,059.5; admitted 2,961 | 331.9; admitted 477 | — | as above |
| **LightGBM matched sweep S-a** (`E_S` seed, 187 + CV) | 24.8 / 93.7 (C) | **132.5** | 47.0 full node / 12.6 shared | 7.6–9.9 | 42.5 min → ≈ 15–16 min per task |
| **N2** (`E_S`; 100 runs + R0, 20 % reserve) | 9.8–12.2 (B) | same | — | 5.5–9.9; saving ≤ 4.3 | — |
| **B primary** N = 719 (`E_S`) | 13,440.6 | same | — | 7,285–10,165; loops at zero cost 6,371–9,679 = 2.1–3.2 × remaining | — |
| B at design N = 1,116 | 20,861.8 | same | — | 11,308–15,778 | — |
| **C P2** fixed band, 4 × 1,250 (opt / cons) | 575 / 3,518 | cons 3,579 | 558 / 3,444 | 341 / 2,092 | — |
| **C P3** shortcut | 20,353 / 84,560 | cons 84,621 | 20,335 / 84,486 | 11,061 / 46,021 | — |
| **C P1** reconstructed full | 288,793 / 1,207,226 | cons **1,498,306** | 206,809 / 856,918 | 117,030 / 486,662 | — |
| C, every unfold of every kind 100× faster (an upper bound that includes category 2) | — | — | — | P1 2,968 / 12,549; P2 86 / 512; P3 284 / 1,323 | — |
| **PET repair** of H2S1T24 (720 DEV + 1,080 RB unfoldings; record §11, not run) | ≈ 3.2 k A100-h, ≈ 12 days | 3,182 A100-h = 1.4 % of remaining GPU | wrapper/I/O ≤ 1.017× | — | training 2/5/10/100×: 1,609 / 666 / 351 / 68 A100-h (category 2) |

**Shorter wall versus lower billing.** For the exact backend, implementation changes leave wall time
per unfold where it is and change only how many unfolds share a node; that is the whole of the `P05`
effect. For LightGBM on shared nodes, billing scales with elapsed. Moving a universe unfold from a full
node to shared 64 is a further ×3.7 in billing on top of the wall-time gain. It needs RSS below the
allocation, which only SB1 can confirm.

**Development, verification and payback** (`payback`). Prototype 1 in production: ≈ 0.5–1
person-day including review (assumed); 0.87 node-h of A/B verification. It saves 0.46 node-h per
LightGBM universe unfold on a full node (0.64 on shared) and 9.24 per exact universe unfold, so it
pays back its verification compute after ≈ 2 universe unfolds and ≈ 1,700 node-h over one exact
`P05`. Prototype 2: ≈ 1–2 person-days (four loaders, six fill loops, the equality suite); 0.35 node-h
of verification. It saves 0.014–0.027 node-h per CV-file unfold, so it pays back after 13–25 unfolds
in compute. For N2 alone (100 runs, ≤ 4.3 node-h) it is not worth the engineering and review.

## 7. Constraints reapplied after the cost calculation

| procedure | after the best measured acceleration | binding constraint unchanged by speed |
|---|---|---|
| B primary, C P1/P2 | B ≥ 6,371; C P1 ≥ 117,030 (opt); P2 341–2,092 | **Independent populations**: the one ME-FHC production supports ⌊4.708/5.708⌋ = 0 disjoint production-size pairs; no event identity (R0); no validated generative law (B §3–§6, DELIVERY §1). More, faster unfolds of the same bank are not new populations. C09/C10 (guaranteed model-dependence, response departure) have no method at any cost |
| exact transfer (`P03`/`P05`/`P09b`) | 165 node-h (238 admitted) | **Estimator matching is what it measures**, but no observable or tolerance is predeclared, `E_C`'s executed bytes are unavailable, and `random_state=None` means `P09b` must precede any "same estimator" statement. It needs its own design and Joseph's authorization (DELIVERY §6 option (b)) |
| S-a / option (c) re-quote | 7.6–47 node-h | An estimator and publication-scope decision reserved to Joseph; comparisons and figures re-derived |
| N2 | 5.5–9.9 node-h | KI-85 deferral (Joseph), guarded harness and `OI-136` / KI-89, registration and review; it validates no interval and no MC stream |
| PET repair | ≈ 1.6 k A100-h at a hypothetical 2× | Terminal `NO_ELIGIBLE_DESIGN`; the failing component is the interval construction; PET is diagnostic-only (Joseph 2026-08-20); a repair is a new design iteration |

**Bias and response.** None of the candidates touches what the estimators compute, so no bias,
response or coverage property moves. That is the point of category 1, and it is also why category 1
cannot cure a methodological blocker.

## 8. Rust/C++ transpilation

Not justified by any measurement here. The compiled work is already compiled. The Python that costs
time is per-row I/O and histogram filling, which existing compiled ROOT/NumPy entry points
(`SetBranchStatus`, `AsNumpy`, `FillN`) remove 5–30× locally with byte-identical results and no new
toolchain. A Rust/C++ loader could at most match them, and it would be a second implementation needing
the same equality suite. Rewriting a trainer is a category-2 estimator change unless bitwise, and for
`E_C` bitwise is undefined. For PET a wrapper rewrite has a 1.017× ceiling. Code-generation capability
is not evidence of performance or equivalence (Goal 4).

## 9. Ranked opportunities and the follow-up benchmark

1. **Selective branch activation for the universe omnifile** (prototype 1). Largest measured `f`,
   byte-identical inputs, smallest change, and it is the difference between ≈ 1,850 and ≈ 125 node-h
   for an exact `P05`.
2. **Columnar loaders + `FillN`** (prototype 2). It is worth doing only if a procedure with thousands
   of CV-file unfolds is ever admitted; it is not worth doing for N2.

**SB1 — specified, not run, not authorized.** Perlmutter CPU, `root_6_28`, guarded launch
(`mnv_guarded_run.py`) from a clean checkout at a pinned commit carrying only this lane's prototypes
and a benchmark wrapper (no production edit). It records driver and helper digests.

- **Inputs:** the production CV and universe omnifiles (sizes above, `sha256` taken in the job); the
  pinned driver blob `e19aeb6d`; universes `Flux:0` (vertical) and one lateral band from
  `runEventLoopOmniFold.cpp:238-244`; and the CV. Arguments are those of the `purity_newomni` sweep
  (`55677843`), so existing products are the references.
- **Steps.**
  - (a) A loader-only identity job on `debug`, one thread: pinned versus prototype 1 versus
    prototype 2 on all four trees, each mode. Assert byte equality of every returned array and
    histogram. Record `MaxRSS`/`MaxDiskRead` per variant.
  - (b) Three full unfolds on shared 64 with prototype 1 (CV on the universe file, `Flux:0`, the
    lateral band). Compare `hXSec2D` against the existing `purity_newomni` products.
  - (c) One CV-file replica (seed 1, bootstrap seed 1, as `59410433_1`) with a timing wrapper around
    the loader, fill and `ohf.omnifold` calls, giving the phase profile D2 lacks.
- **Correctness tolerances:** (a) byte-identical, no tolerance. (b)/(c) per-bin relative difference
  ≤ 1e-8 against the reference product, set just above the measured same-argument rerun envelope
  (5.8e-9, `VL170`).
- **Hardware / cost cap / abort.** Shared 64-CPU (and `debug` for (a)). Cap 2.0 node-h in total;
  expected ≈ 0.4–1.0. Abort on the first byte mismatch in (a), any (b)/(c) difference above tolerance,
  any prototype-1 run with `MaxRSS` > 100 GB or elapsed > 2,000 s, or any OOM.
- **Success threshold:** a universe-file unfold with prototype 1 completes on shared 64 with
  `MaxDiskRead` ≤ 10 GB, `MaxRSS` ≤ 30 GB and elapsed ≤ 0.5 × 2,547 s, at identical outputs.
  Separately, (c) attributes ≥ 90 % of its wall to named phases.
- **What it cannot authorize:** a production change (the driver is owned by no current lane, and its
  hash-binding exception at `verify_hash_bindings.py:104-112` needs that owner), any transfer
  measurement, a re-quote or a gate change.

**PET profile request (bounded, not run).** One H2S1T24 iteration on 1 A100 (≈ 0.35–0.7 A100-h, cap
1 A100-h) under `tensorflow/2.15.0` with the TF profiler over 200 step-1 and 200 step-2 updates and
`nvidia-smi` sampling at 1 s. Record TF32 state and the precision policy actually applied, not only
the declared one. Output: GPU busy fraction, host time per step, input-pipeline stall. Only a
host-bound result would open a category-1 candidate (e.g. `steps_per_execution`); anything else is
category 2.

## 10. Dispositions

- **D1 — universe-file procedures (exact-backend transfer `P05`; LightGBM S-a, `E_U` rebuilds, C P1's
  universes): PASS, bounded.**
  - The opportunity rests on representative Perlmutter receipts (`f_io = 0.695`, whole-file reads in
    374/374 tasks, RSS 65–187 GB) and a local, byte-verified prototype that removes the mechanism.
  - Estimated gains: universe-unfold wall 2.8–3.2×; billing 2.8× on a full node, up to ≈ 10.6× on
    shared 64; exact `P05` ≈ 1,853 → ≈ 125 node-h.
  - These Perlmutter gains are Amdahl estimates until SB1. Wall-time acceleration of the exact
    backend by implementation: **FAIL** (ceiling 1.03×).
- **D2 — CV-file LightGBM procedures (N2, B primary, C P2/P3, `P07`): INCONCLUSIVE.** `f_loop` is
  bracketed at [0.28, 0.53], not phase-profiled, so the gain is 1.3–1.8× at the measured local `s`
  (ceiling 1.4–2.1×). For N2 the absolute saving (≤ 4.3 node-h) does not justify a production change.
- **D3 — PET successor: INCONCLUSIVE** for GPU training (no utilization or TF profile exists);
  **FAIL** for wrapper, I/O or transpilation routes (ceiling 1.017×).
- **D4 — does even the optimistic gain change feasibility after the constraints are reapplied?
  FAIL.**
  - B primary and C P1 remain above every comparator even with zero-cost loops.
  - The population NO-GO, the unmeasured transfer, the KI-85 deferral and PET's terminal ruling are
    untouched.
  - The one decision input that does move is the price of option (b), which is not a feasibility
    verdict.

The overall objective — a publication-ready measurement with a reproducible central estimator,
matched uncertainty and supporting validation — is **not** met by this stage.

## 11. Verification and review

- `python3.13 -I bench/test_prototypes.py`: 11 tests OK (`results/test_prototypes.txt`). It launches
  nothing (synthetic trees only).
- `costs.py` reproduces C's six published totals exactly. `check_headlines.py` re-derives 11 headline
  numbers from the raw operands with separate parsing and unit conversion, all within 0.5 %
  (`results/check_headlines.txt`). It is the same author as `costs.py`, so it is a consistency check,
  not an independent origin.
- Delivery hooks: see the commit's `Checks:` trailer. Manifest freshness: §13.
- **Independent review.** *(filled in after the review; see below)*

## 12. Limitations

- Every prototype speedup is a laptop measurement (M1 Pro, ROOT 6.36, Python 3.13), not Perlmutter
  throughput (ROOT 6.28, Python 3.11). The lower bound of `f_loop` assumes a Milan core is not faster
  per row than an M1 Pro core.
- The 2,561 s versus 778 s comparison is n = 1 against n = 2, on different nodes and dates.
- Exact-backend RSS on the universe file is inferred from LightGBM tasks with the identical loader; no
  exact universe unfold has run. Packing contention (memory bandwidth) for 29–60 single-threaded exact
  jobs per node is unmeasured, as it was for A.
- The universe sweeps measured are the July `purity_newomni` and `negweight` sweeps on the current
  171 GB file, not `E_U`'s own earlier sweep. C's documented 0.5 node-h may have been right for that
  file.
- The mechanism of the 187 GB RSS spikes is not established; prototype 1 removes the proportional
  excess locally but SB1 must show it on Perlmutter.
- Prototype 2 covers `collect_signal_arrays_2d` (not the alt-model path) and one fill pattern. The
  other three loaders and the efficiency/completeness loops are priced by their per-row costs, not
  ported.
- PET: no GPU profile; the 29–35 ms per update is from one step-2 receipt.

## 13. Requests for the integration owner (not done here)

- **Manifest.** This lane adds files under `Q/speed/` only. `REPORT.md` is pre-registered
  (`MANIFEST-overrides.tsv`, `MACHINE open`). Whether the generated `MANIFEST.tsv` needs regenerating
  for the new non-Markdown files is recorded in the commit's hook output and in §11's delivery line.
  Regeneration, if needed, is the integration owner's (`generate_manifest.py`), not this lane's.
- **For A's and C's records (their lanes are closed; this lane does not edit them).** Their `P05` and
  universe-rate forecasts omit memory. Under today's driver an exact or LightGBM universe unfold peaks
  at 65–187 GB, so A's 0.68 node-h packing and C's optimistic shared-64 universe rate are not
  executable on the current file. C's conservative 0.5 node-h is below the measured 0.708. Corrected
  figures are in §6; whether to annotate their documents is the integration owner's call.
- **Proposed register text (for `KNOWN_ISSUES.md`'s owner).** *"The 2D driver reads every branch of
  the universe omnifile (no `SetBranchStatus`): 171.3 GB read and 65–187 GB peak RSS per universe
  unfold, 69 % of its wall; a byte-identical selective-read prototype and a ≤ 2 node-h confirmation
  benchmark are in `state/next-preparation-20261009/speed/REPORT.md` §9."*

## 14. Resources

*(final figures filled in at delivery)*
