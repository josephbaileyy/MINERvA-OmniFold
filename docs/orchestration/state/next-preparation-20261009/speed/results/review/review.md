# Independent review: Session 4 (speed), fixed commit `1e4e6f46`

- **Reviewer:** a fresh, read-only Claude Opus 5.5 (`claude-opus-5-5`) agent, one initial review. It
  did not author the lane.
- **Fixed commit:** `1e4e6f465bcb2280514d13c21aff96a70d3f59a0` (branch `prep/next-speed-20261009`), base
  `5ac9706a21e8a5ac8863a65fd7623d8ab8d22269` (the PR #61 merge, confirmed with `git log -1`).
- **Worktree:** `/Users/josephbailey/local-research/MINERvA-OmniFold-next-speed-review-20261009`. `HEAD`
  was confirmed as `1e4e6f46`, and the driver blob is `e19aeb6d…` (`git hash-object`).
- **Lane diff:** `git diff --stat 5ac9706a..1e4e6f46` shows 22 files and 5,208 insertions, all under
  `Q/speed/`.
- Below, `Q` = `docs/orchestration/state/next-preparation-20261009/speed`, and `R:` = `Q/REPORT.md`.

## Worktree status

- **At start (2026-10-09T20:40:50Z):** `git status --short` printed nothing (rc 0).
- **At end (2026-10-09T23:31:40Z):** `git status --short` printed nothing (rc 0).
- **Writes:** nothing was written inside any worktree. Every file this review produced is in this
  directory:
  - `recompute_operands.py` / `.out`
  - `recompute_costs.py` / `.out`
  - `rss_distribution.out`
  - `boolview_mutant.py` / `boolview_full.out`
  - `boolview_probe.out`
  - `sacct_spot1.txt`, `sacct_spot2.txt`
  - `tests.out`, `mk*.out`
  - `trees/`, about 300 MB of disposable synthetic trees

## sacct spot-checks (2 queries, both read-only)

**Query 1:** `ssh -o BatchMode=yes -o ConnectTimeout=30 saul.nersc.gov 'sacct -j
55677843_17,59410433_5,53116554,55677844,59409026_1 --parsable2
--format=JobID,State,ElapsedRaw,TotalCPU,MaxRSS,MaxDiskRead,NCPUS,AllocTRES'`. An earlier attempt
used `timeout`, which macOS lacks. It failed locally with rc 127 before any ssh, so it is not counted.

```
53116554.batch|COMPLETED|69523|19:18:00|16786760K|2114.37M|256|cpu=256,mem=487802M,node=1
55677843_17.batch|COMPLETED|2579|12:47:09|69110532K|163350.86M|256|...
55677844.batch|COMPLETED|2561|13:30:06|74625444K|163350.84M|256|...
59409026_1.batch|COMPLETED|778|11:08:54|17233740K|2098.06M|256|...
59410433_5|COMPLETED|645|04:41:15|||64|billing=64,cpu=64,energy=293542,mem=121920M,node=1
59410433_5.batch|COMPLETED|645|04:41:15|15005496K|2097.44M|64|cpu=64,mem=121920M,node=1
```

**Query 2:** the same form, for `55677842_1,55677842_188,55677845,59410433_300`.

```
55677842_1.batch|COMPLETED|2541|12:35:19|170806248K|163350.85M|256|...
55677842_188.batch|COMPLETED|5|00:00.119|0|0|256|...
55677845.batch|COMPLETED|2597|12:44:00|69842960K|163350.84M|256|...
59410433_300.batch|COMPLETED|700|06:20:13|15064336K|2097.48M|64|...
```

All 9 jobs/tasks match their rows in `Q/operands/*.psv` byte for byte in ElapsedRaw, TotalCPU, MaxRSS
and MaxDiskRead. Full outputs are in `sacct_spot1.txt` and `sacct_spot2.txt`.

## Rubric

### 1. Operands and §2–§3 tables: OK, with MINOR labelling issues (F6, F7, F8, F9)

`recompute_operands.py` is my own parser. It treats sacct K/M as KiB/MiB and reports decimal GB. It
reads the raw psv files only. Every recomputed value matches the report:

| quantity | mine | report |
|---|---|---|
| replica 59410433 elapsed min / median / max (n = 300, all COMPLETED, billing 64) | 544 / 840 / 1,900 s | 544 / 840 / 1,900 (R:78) |
| replica mean node-h (E × 64 / 256 / 3600) | 0.059147 | 0.0591 |
| replica busy CPUs, median | 30.86 | 30.9 |
| replica serial-bound median (min–max) | 0.526 (0.414–0.610) | 53 % (41–61 %) |
| 55677843 tasks with elapsed > 300 s | 187 (of 400) | 187 |
| 55677843 median elapsed / node-h | 2,547 s / 0.7075 | 2,547 / 0.7075 |
| 55677843 MaxDiskRead | 171.2858–171.2860 GB (every task) | 171.29 |
| MaxRSS min / median / max: 55677843 | 65.23 / 71.16 / 186.56 GB | 64.5 / 71.2 / 186.6 (pooled) |
| MaxRSS min / median / max: 55677842 | 64.51 / 71.36 / 186.64 GB | (pooled) |
| tasks above 121,920 MiB (127.84 GB): 55677843 / 55677842 | 14 / 17 | 14 / 17 |
| excess = mean(2,561, 2,597) − 778 | 1,801 s; busy CPUs during the excess 3.94 | 1,801; ≈ 3.9 |
| f_io = (2,547 − 778) / 2,547 | 0.6945 | 0.695 |
| exact 53116554 | 69,523 s; 0.999 busy; 17.19 GB; 19.31 node-h | same |
| full-node replica 59409026_1 | 51.6 busy; serial 0.602; 17.65 GB | 51.6 / 60 % / 17.6 |
| KI-85 (n = 51) | 465 / 940 / 3,069 s; busy 35.6; serial 0.452; 0.0653 node-h median | same |
| RSS excess per byte, (71.16 − 17.65) / 171.117 | 0.313 | 0.31 |

The units are handled correctly in the code: node-h = E × billing / 256 / 3600, and KiB/MiB are
converted to decimal GB. The labels have defects, listed in F6–F9.

### 2. The natural experiment and its inference: MINOR (F5)

**The mechanism is confirmed in the code.** The driver at blob `e19aeb6d` contains no
`SetBranchStatus`, `ImplicitMT` or cache call. `git grep` gives rc 1 on both the driver and the
helper. All four loaders call `SetBranchAddress` and then `GetEntry(i)` per row:

- data: `unfold_2d_omnifold_unbinned.py:217-224`
- background: `:300-308`
- truth denominator: `:569-579`
- signal: `:663-700`

`GetEntry` on a tree with every branch active reads every branch. MaxDiskRead equals the file size in
374/374 tasks, so "reads all branches" is established. Causation of the excess is also supported by
an independent order-of-magnitude check:

- Locally, the per-row excess is about 9.8 µs per ≈ 1,455 extra bytes per row, about 6.7 ns per byte.
- Over 171 GB that predicts ≈ 1,150 s, against the measured 1,801 s.
- Lane C's documented full-node CV wall of 804 s corroborates the 778 s baseline.

**The "same CV unfold" wording is inaccurate** (R:41-43, 98-101). The two sides of the comparison
differ in more than date and node:

- `59409026_1` is a bootstrap replica: `--seed 1 --bootstrap-seed 1`, purity mode, the October driver
  with the KI-84 fix (`docs/orchestration/state/ki84-rebuild-20261006/sbatch_ki84_replicas.sh:58-66`).
- `55677844`/`45` are seed-42 runs without bootstrap. `55677844` is `--bkg-mode negweight`
  (`2d-unfolding/sbatch_uni_CV_negweight.sh:43-51`, `sbatch_uni_CV_puritynew.sh:43-50`). They ran on
  the July driver, which has gained 368 lines since (`git diff --stat 242e996c 5ac9706a`).

The n = 1 vs n = 2 caveat is stated (R:101-102, 335). It omits these argument and driver differences.
The magnitude survives them, so f_io ≈ 0.69–0.71 stands.

**The "representative sibling sweep, not E_U's own" caveat is adequate** (R:339-341).

### 3. Exact-backend pricing: MATERIAL (F1), with packing context

`recompute_costs.py` reproduces every row.

**Packing.** pack(17.19 GB) = 29, pack(186.6) = 2, pack(71.2) = 7, pack(8.52, analytical) = 60, on a
511.50 GB node.

| case | P05 (node-h) | P03 N=50 + P05 + P09b | ×1.15 / 0.8 |
|---|---:|---:|---:|
| (a) memory-safe, max RSS, 2/node | 1,853.11 | 1,893.06 | 2,721.3 |
| (b) median RSS, 7/node | 529.94 | 569.89 | 819.2 |
| (c) prototype 1, 29/node | 125.41 | 165.37 | 237.7 |
| prototypes 1 + 2 | 60.62 | 79.93 | 114.9 |
| A, 0.68 node-h | 127.84 | 168.64 | 242.4 |
| C ratio | 285.37 | 326.17 | 468.9 |

- **N = 300:** 2,059.55 (admitted 2,960.6) under today's driver, and 331.85 (477.0) with prototype 1.
- **Billing and waves:** the billing ratio is 14.85. At 30 nodes, P05 takes 4 waves today and 1 with
  prototype 1. These match R:171, 193-195 and 199-200.

**Is it legitimate to infer exact RSS from LightGBM tasks?** For the proportional loader excess, yes.

- On the CV file, exact (17.19 GB) and LightGBM (14.4–17.6 GB) have nearly equal RSS, so the loader
  dominates.
- The local single-threaded pinned loader shows RSS growth proportional to bytes read.
- That supports a median universe-file RSS of about 71 GB for an exact process too.

**It is not established for the 160–187 GB spikes.**

- R:342 says their mechanism is unknown.
- They occur in about 10 % of 128-thread LightGBM processes (pooled p90 120 GB, p95 183 GB;
  `rss_distribution.out`).
- They land in random bands, which suggests a run-to-run, possibly thread-related, phenomenon rather
  than the loader.
- Pricing every exact universe unfold at the worst spike (2/node) is a worst-case packing policy, not
  "the" price.

**Intermediate policies give intermediate P05 prices** (for P05 alone).

- 4/node gives ≈ 927; 31/374 tasks exceed 127.9 GB.
- 5/node gives ≈ 742.
- 7/node gives 530. At p ≈ 0.11 per task of a > 100 GB spike, about 57 % of 7-job nodes would hold a
  spike, so OOM is likely.

The today's-driver price is therefore a forecast range of ≈ 530–1,853 node-h for P05, depending on
packing policy and spike transfer. §1 (R:47-50), §9 (R:252-253) and D1 (R:300) quote 1,853 without
calling it a forecast or giving the range. §6 does show the 569.9 median case (R:199).

**Additive I/O for exact is defensible at 2/node.** The 1,801 s phase is serial Python I/O in a
LightGBM job as well. At 7/node it would mean concurrent 171 GB reads, which is unmeasured. That is a
NOTE (F16).

**Scope of "≈ 1,853 → ≈ 125".** It is a forecast resting on inferred RSS, local RSS evidence for
prototype 1, and unmeasured packing contention (R:336-338). The limitations section says so; the
headline does not.

### 4. Amdahl and fractions: OK, with MINOR issues (F8 and the upper-bound note)

My own reduction of `results/bench_loader_fill.jsonl` (minimum of repeats) gives:

- **Reads:** 32,849,103 × 2.0484 µs + (32,849,103 + 4,119,797 + 658,227) × 1.1160 µs = 109.3 s.
- **Fills:** 6 × 32,849,103 × 0.6383 µs = 125.8 s.
- **Total:** 235.1 s, so f_lo = 235.1 / 840 = 0.2799. f_hi (serial bound) = 0.5260.
- **After prototype 2:** 70,476,230 × 0.37237 + 6 × 32,849,103 × 0.021067 = 30.40 s, so s_loop = 7.734.
- **Prototype 1 residual:** (2.58667 − 1.91669) / (11.72648 − 1.91669) = 0.0683, so s_io = 14.64. The
  bytes ratio is 67.6.
- **S for I/O:** 2.834 at measured s; 1.532 / 2.250 / 2.667 / 3.201 at 2/5/10/100; ceiling 3.274.
- **S for loops:** 1.322–1.845 at measured s; 1.163–1.357 / 1.288–1.726 / 1.337–1.899 / 1.383–2.086;
  ceiling 1.389–2.110.
- **Exact backend:** loops 0.34–0.64 %, I/O 2.53 % (ceiling 1.026).

All match §4/§5 (R:160-162, 170-173).

**The lower-bound assumption is stated** (R:95-96, 172, 333-334) and reasonable: an M1 Pro P-core is
generally faster per thread than a 2.45 GHz Milan core. It still compares PyROOT 6.36 / Py 3.13
against 6.28 / 3.11, and the report says so.

**Is any speedup applied to a portion it does not accelerate?** Only at the upper end. f_hi is the
whole serial bound, which includes non-loop serial phases. Applying s_loop to it inflates S. This is
a bound, and it is presented as a bracket, so it is acceptable (NOTE). The "zero-cost loops" B floor
of 6,371 uses the same upper end and is therefore conservative for D4. Prototype 2 is not applied to
the prototype-1 residual.

**Six fill loops over 32.85 M rows** (`costs.py:40`) matches the code:

- two loops in `compute_efficiency_2d` (`:791-803`)
- two in `compute_omnifold_completeness_2d` (`:848-854`)
- `hTruth2D` and `hUnfold2D` (`:1788`, `:1883`)

`hTruth2D` and `hUnfold2D` loop over `truth_pt_in`, which may be shorter than 32.85 M rows. The data
and background loaders fill inside their loops but are priced at the truth-loop rate. Both effects
are small (NOTE).

### 5. Lane C reproduction and accelerated C totals: OK (NOTE F13)

My re-implementation of C's formula reproduces C's six published totals exactly:

- optimistic P1 288,792.599, P2 575.239, P3 20,352.517
- conservative P1 1,207,226.027, P2 3,517.952, P3 84,559.577

The accelerated rows also match the lane's `results/costs.json`:

- conservative "measured universe rate": P1 1,498,306.1, P2 3,579.3, P3 84,620.9
- p1_fullnode: 856,917.8 / 3,444.2 / 84,485.8
- p1_p2_fullnode: 486,661.5 / 2,092.2 / 46,020.7
- optimistic p1_shared64: 206,808.7 / 558.0 / 20,335.2
- optimistic p1_p2_shared64: 117,030.4 / 340.6 / 11,060.8
- every unfold 100× faster: optimistic 2,968 / 86 / 284; conservative 12,549 / 512 / 1,323

**Coupling.** C's executable keys its conservative setup on `uni == 0.5`
(`docs/orchestration/state/uncertainty-preparation-20261008/c/costs.py:249`). Run with any other
universe rate, it silently switches to the optimistic setup items. The lane passes conservatism
explicitly (`Q/costs.py:73-82, 307-308`), which is the intended semantics. Its conservative
accelerated rows therefore differ from what C's own code would print: P1 1,498,306 vs 1,498,117, P2
3,579 vs 3,391, P3 84,621 vs 84,432. That is ≤ 189 node-h and not consequential, but undisclosed.

The conservative accelerated columns use the optimistic f (`a_hi`). They are labelled "best measured
acceleration", which is fine for D4 (NOTE F14).

### 6. Prototype equivalence: OK, with one weak negative control (F12)

**The tests pass.** I generated trees with the lane's generator: 200 k rows with 192 extra branches,
and 200 k rows with none. `SPEED_TREES=… python3.13 -I bench/test_prototypes.py` then gave 11 tests
OK (28.2 s; `tests.out`). It reproduces "697 guard rows; unguarded arctan2 differs in keys: []".

**Byte identity is real.** `diff_keys` compares dtype, shape and `tobytes()` for all 8 keys
(`Q/bench/test_prototypes.py:53-57`). The equality tests cover every mode, with universes
`Flux:0` / `GEANT:0` on the 192-branch tree (`:33-37, 84-108`).

**Negative controls:**

- **Missing activation** (`:135-143`) demonstrates the silent wrong `w_reco` and the guard's refusal.
  That shows behaviorally that `SetBranchAddress` on a disabled branch leaves the value stale. The
  separate claim that "an after-the-fact address check is vacuous (measured)" (R:127-129) has no
  committed test, so it is not verifiable here (NOTE).
- **`sim_pass==1`, `wt<=1e4`, dropped angle cut and sentinel** reach the code they name. Each mutation
  site is asserted unique.
- **The "bool-view bypass" mutant** (`:152-153`) replaces the view with `astype(np.uint8) * 0`. That
  zeroes `sim_pass`; it does not bypass the view. I built a faithful mutant that removes the
  `raw.view(np.uint8)` line (`boolview_mutant.py`). On the 200 k tree with 666 byte-2 rows it changes
  all 8 output keys. So the bool/UChar_t trap is real and is caught by the same comparison, but the
  committed control does not show it.

**The atan2 claim is accurate as stated:** the guard is defensive and not shown necessary.

### 7. Categories and scope: MINOR inconsistency (part of F2 and F3)

These categories are applied correctly:

- LightGBM thread-count changes are category 2 (R:175).
- A faster exact-split trainer is category 2 because `E_C` has `random_state=None` (R:176). The driver
  pins `random_state` only under `--seed`, at `:1742-1744`.
- Histogram GBT, mixed precision and PET training changes are category 2.
- C's S1/S2 are category 3.

**The report then breaks its own rule.** It prices "prototype 1 on shared 64" as part of the
category-1 candidate:

- the billing "up to ≈ 10.6×" (R:192, 201, 300)
- the C optimistic `p1_shared64` rows

The launch scripts set `OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}`
(`2d-unfolding/sbatch_unfold_2d_MEFHC_5iter_universes_full_puritynew.sh:27`). So moving a universe
unfold from 128 to 64 threads is the category-2 change of R:175.

**"Rust/C++ not justified" is supported** (§8): the costly Python is per-row I/O and fills, which
existing compiled entry points remove.

**Nothing claims Perlmutter throughput from laptop numbers.** S values at "measured s" are labelled
local or Amdahl (R:166, 301, 332). Nothing claims scientific equivalence (R:7-8, 235-237). Nothing
claims that acceleration cures a methodological blocker (§7). Treated briefly for time.

### 8. Dispositions and SB1: MATERIAL (F2, F3), MINOR (F4, F10, F11a)

**D1 PASS is supported for one scope and overstated beyond it** (R:21, 295-302).

- **Supported:** LightGBM universe-file unfolds on a full node. f_io is measured, the whole-file read
  is observed in 374/374 tasks, the mechanism is in the code, and the fix is byte-verified. Even at a
  pessimistic Perlmutter s = 2, S = 1.53, so the gain is bounded below by more than the local-s
  uncertainty. Calling the Perlmutter numbers "Amdahl estimates until SB1" is honest, and PASS at that
  scope matches Goal 4's "bounded opportunity supported by representative measurements".
- **Overstated:** the bundling of two more items into PASS:
  - the exact-backend `P05` billing (`≈ 1,853 → ≈ 125`). No exact universe unfold has run, and the
    today price rests on the worst-case spike packing (F1).
  - the shared-64 ≈ 10.6× billing, which needs a category-2 thread change and an RSS reduction that
    is unmeasured on Perlmutter.

**D2 INCONCLUSIVE is supported:** f is bracketed, not phase-profiled, and that matches Goal 4's
INCONCLUSIVE definition.

**D3 INCONCLUSIVE for training is supported.** Its "FAIL for wrapper … routes (ceiling 1.017×)"
(R:306-307) is broader than the evidence (F10).

**D4 FAIL is supported** on the population and methodology constraints, which do not depend on speed.
One supporting sentence is wrong (F11b).

**SB1** is correctly unauthorised (R:257, 282-284), with inputs, tolerances, hardware, cap, abort rule
and success threshold all named. It has three specification defects:

1. **Step (b)'s tolerance test is confounded by thread count (F3).** It compares 64-thread shared runs
   against 128-thread references at 1e-8.
2. **Step (a) is mis-costed (F4).** One pinned-loader pass over the 171 GB file takes about 20–30 min
   (from the 1,801 s excess), and step (a) asks for several modes. That does not fit `debug`'s 30-min
   limit (`docs/orchestration/state/ki84-rebuild-20261006/sbatch_ki84_replicas.sh:20`) in one job. On
   a 256-billing node it costs about 1.5–2 node-h by itself, against "expected ≈ 0.4–1.0" and a cap
   of 2.0.
3. **Step (a) exceeds prototype 2's scope (F4).** It asks for prototype 2 "on all four trees", but
   prototype 2 covers only the signal loader (R:344-346).

### 9. Omissions and metadata: MINOR (F9, F11)

- **Header metadata.**
  - `Resources` (R:18) and §14 (R:365-367) carry caps and placeholders, not the measured elapsed,
    CPU, scratch and tracked bytes that `DISPATCH.md:82` requires. They are expected at delivery but
    absent at the reviewed commit.
  - `Pinned inputs` omits `2d-unfolding/uq/universes_full_list.txt`, which `Q/profile_from_sacct.py:115`
    reads, and gives no commit for `sacct_all.txt`.
  - The `Review` placeholder is expected at this stage.
- **Owner statements check out.** The hash-binding exception cited at `verify_hash_bindings.py:104-112`
  exists and says re-pinning is the gate owner's decision. `MANIFEST-overrides.tsv:529` registers
  `speed/REPORT.md` as `MACHINE open`.
- **Fill-loop count for the purity mode:** correct (see 4).
- **Cheaper options:** none material was dismissed. The array-caching row correctly restricts reuse
  to before the Poisson weights (R:174).

## Findings

**F1 — MATERIAL.** R:47-50, 171, 199, 221, 252-253, 300; `Q/costs.py:209-213`.

- **What is wrong:** "P05 ≈ 1,853 node-h today" (with "×14.9 billing" and "≈ 1,700 node-h payback")
  prices every exact universe unfold at the single worst LightGBM RSS spike, 186.6 GB, packed 2 per
  node. The spike mechanism is unestablished (R:342), and spikes are seen only in 128-thread LightGBM
  processes. 87 % of tasks peak at 64–72 GB, and 4–5/node gives ≈ 740–930. §1, §9 and D1 do not call
  the figure a forecast and give no range.
- **Smallest correction:** quote today's P05 as a forecast range, ≈ 530–1,853 node-h, naming the
  packing policy and the spike-transfer assumption. Keep ≈ 125 as the prototype-1 forecast. Write
  "forecast" in §1, §9 and D1.

**F2 — MATERIAL.** R:21, 295-302 (with 192, 201).

- **What is wrong:** D1 PASS bundles in two items that representative measurements do not support:
  the exact-backend P05 billing (no exact universe unfold has run; see F1), and the shared-64 ≈ 10.6×
  billing. The latter needs a 64-thread run, which is category 2 by R:175, and an RSS reduction that
  is unmeasured on Perlmutter.
- **Smallest correction:** scope D1 PASS to LightGBM universe-file unfolds on a full node (est. wall
  and billing 2.8×). Report exact P05 and shared-64 billing as forecasts contingent on SB1, or as a
  separate INCONCLUSIVE sub-item. Label the shared-64 move as category 2.

**F3 — MATERIAL.** R:269-270, 273-275, 277-278 vs R:175.

- **What is wrong:** SB1(b) runs prototype-1 unfolds on shared 64 (64 OpenMP threads) and compares
  `hXSec2D` with `purity_newomni` products made at 128 threads. The tolerance is 1e-8, taken from a
  same-argument rerun envelope. A failure could not be attributed to prototype 1, and the abort rule
  could fire on the thread change alone.
- **Smallest correction:** run (b) at 128 threads on a regular node to match the references. Test the
  shared-64 RSS fit separately, or add a pinned-loader control at 64 threads.

**F4 — MINOR.** R:266-268, 276-277.

- **What is wrong:** SB1(a) runs the pinned loader over the 171 GB universe file in several modes in
  one `debug` job. Each pass is about 20–30 min, against debug's 30-min limit (`sbatch_ki84_replicas.sh:20`).
  On a 256-billing node it costs about 1.5–2 node-h by itself, against "expected 0.4–1.0" and a cap
  of 2.0. It also asks for prototype 2 "on all four trees", although prototype 2 covers only the
  signal loader.
- **Smallest correction:** re-estimate the cost of (a). Split it into ≤ 30-min jobs, or run it on
  shared with enough memory. Restrict prototype 2 to `mc_signal_reco`.

**F5 — MINOR.** R:41-43, 98-102, 335.

- **What is wrong:** the report calls the comparison "the same CV unfold". It is a seed-1 bootstrap
  replica on the October driver against seed-42 non-bootstrap runs on the July driver, and one of the
  latter is negweight. The caveat names only n, dates and nodes.
- **Smallest correction:** say "comparable" and list the seed, bootstrap, bkg-mode and driver-version
  differences. The magnitude is corroborated by C's 804 s and the per-byte rate.

**F6 — MINOR.** R:100-101.

- **What is wrong:** "the 1,801 s excess … is 69.5 % of a universe task". In fact 1,801 / 2,547 =
  0.707. The 0.695 figure is (2,547 − 778) / 2,547 (`Q/profile_from_sacct.py:150`).
- **Smallest correction:** state f_io's definition, or quote 1,769 s.

**F7 — MINOR.** R:105, 192; `Q/costs.py:200-201`.

- **What is wrong:** "121.9 GB shared-64 allocation". The allocation is 121,920 MiB = 127.8 GB
  (119.1 GiB), while every RSS in the report is decimal GB. The counts 14/17 are right against
  121,920 MiB; against a literal 121.9 GB they would be 18/18.
- **Smallest correction:** write "121,920 MiB (127.8 GB)".

**F8 — MINOR.** R:72-74.

- **What is wrong:** the serial-bound caveat points the wrong way. If serial phases spin extra
  threads, TotalCPU rises and the formula under-counts serial time, so it stops being an upper bound.
  It over-counts when parallel phases run less than k-wide.
- **Smallest correction:** fix the sentence, and note that f_hi = 0.53 is then not strict.

**F9 — MINOR.** R:41-42, 82.

- **What is wrong:** the population selection is undisclosed. Each sweep array had 400 tasks. Tasks
  188–400 (213 per sweep) exited in ≤ 12 s with zero read, because the list has 187 universes. The
  reduction keeps ElapsedRaw > 300 s (`Q/profile_from_sacct.py:118-119`).
- **Smallest correction:** add one sentence.

**F10 — MINOR.** R:179, 306-307.

- **What is wrong:** D3 marks "FAIL for wrapper … routes (ceiling 1.017×)". The 1.017 ceiling bounds
  only the pre-training load phase. The per-step host and Python dispatch inside training is
  unbounded, and R:289-291 itself says a host-bound profile would open a category-1 candidate.
- **Smallest correction:** scope the FAIL to input loading and the process wrapper outside the
  training loop. Leave per-step wrapper costs under INCONCLUSIVE.

**F11 — MINOR.** Two defects.

- **(a) R:18, 365-367 — Resources are not measured.** `DISPATCH.md:82` requires measured values, but
  the field holds placeholders, and `Pinned inputs` omits `uq/universes_full_list.txt` and the
  `sacct_all.txt` commit. Correction: fill in the measured figures and add the two inputs.
- **(b) R:310 — a wrong supporting sentence.** "B primary and C P1 remain above every comparator even
  with zero-cost loops" is false for B. Its 6,371–9,679 node-h is below the 20,000 node-h annual
  comparator; even unaccelerated, B is 0.67× annual (B DESIGN:57-59). D4's verdict is unaffected
  because it rests on the population NO-GO. Correction: "above the remaining CPU balance".

**F12 — NOTE.** `Q/bench/test_prototypes.py:152-153`.

- **What is wrong:** the "bool-view bypass" control zeroes `sim_pass` instead of bypassing the view.
  The reviewer's faithful mutant (view removed) changes all 8 keys, so the trap and its detection are
  real.
- **Smallest correction:** replace the mutant with removal of the `raw.view(np.uint8)` line.

**F13 — NOTE.** `docs/orchestration/state/uncertainty-preparation-20261008/c/costs.py:249` vs `Q/costs.py:73-82`.

- **What is wrong:** C keys its conservative setup on `uni == 0.5`. The lane decouples that, which is
  the intended semantics, but does not say so. Its conservative accelerated rows differ from C's
  executable by ≤ 189 node-h.
- **Smallest correction:** add one sentence in §6.

**F14 — NOTE.** R:205-207.

- **What is wrong:** the conservative "prototypes 1 + 2" C column uses the optimistic f (`a_hi`).
- **Smallest correction:** label it "best case".

**F15 — NOTE.** R:127-129.

- **What is wrong:** "an after-the-fact address check is vacuous (measured)" has no committed test or
  record.
- **Smallest correction:** commit the probe, or drop "(measured)".

**F16 — NOTE.** R:171, 336-338.

- **What is wrong:** additive I/O for exact is plausible at 2/node. At the 7/node median packing,
  seven concurrent 171 GB reads per node are unmeasured.
- **Smallest correction:** add this to the limitations.

## Overall judgement

The arithmetic is sound. Every consequential number I recomputed independently from the raw operands
matches to the printed precision: the sacct reductions, Amdahl values, exact-backend pricing, lane C's
six totals and the accelerated rows, N2, B and PET. The operands faithfully reproduce the scheduler
(9/9 spot-checked tasks). The prototypes are byte-identical on the synthetic trees, and the tests
pass.

**Dispositions:**

- **D1 PASS — overstated in scope.** It is supported for LightGBM universe-file unfolds on a full
  node. It is overstated for the exact-backend P05 price and the shared-64 billing, which are
  forecasts: one rests on worst-case spike packing and the other on a category-2 thread change (F1,
  F2).
- **D2 INCONCLUSIVE — supported.**
- **D3 INCONCLUSIVE — supported.** Its FAIL leg is slightly over-broad (F10).
- **D4 FAIL — supported.** One supporting sentence is wrong (F11b).

The SB1 follow-up is correctly unauthorised. It needs the thread-count confound removed (F3) and its
step-(a) cost and scope corrected (F4) before it can be priced at ≤ 2 node-h.

**Coverage:** rubric items 6 and 7 were treated more briefly, as the coordinator allowed. Item 6 still
included running the suite and one faithful-mutant probe; item 7 was a category read-through.

## Resources

- **Wall time:**
  - first session: 20:40:50Z to about 20:50Z, before the API interruption
  - resumed: 23:22Z to about 23:40Z
  - total: about 30 min active
- **Local CPU:** about 1.5 CPU-minutes, ≈ 0.03 core-h, all at one thread:
  - tree generation 15 + 4 s user
  - test suite 27 s
  - probes and scripts < 15 s
- **Peak RSS:** 1.2 GB.
- **Scratch:** about 0.3 GB.
- **Cluster:** 2 read-only `sacct` queries. No jobs, GPU, training or toys.
