# PREDECLARATION 2026-09-06 — the bounded read-only ROOT inspection for `PM-1`, `PM-3`, `PM-4`, `PM-5`

**CITABLE FOR:** what this inspection would run and read, declared before submission.
**NOT CITABLE FOR:** any discharge, grade, adoption, gate movement, spend, or publication claim.
**STATUS: DECLARED, NOT SUBMITTED.** Admission is blocked — see
`AUTHORIZATION-20260906-pm-root-inspection.md` §3. Nothing in this file has been executed.

Joseph's authorization (2026-09-06) requires the exact command, environment, memory request, input
paths and intended reads to be declared *before* submission. This is that declaration. It is
committed before execution, following the precedent of
`PREDECLARATION-20260816-hrowindex4d-readback.md`, whose receipt records the same discipline.

## 1. The allocation

    salloc --nodes 1 --constraint cpu --time 30 --account m3246 --qos interactive --no-requeue

- **one CPU node**, `--constraint cpu`. No GPU is requested and no `--gres` is passed.
- **`--time 30`** — the authorized 30-minute maximum, and the reservation bound a breach is measured
  against. **It is not the charge**: R5 meters actual `ElapsedRaw` (§5.2a, confirmed by measurement on
  `57128458`), so a task that exits when its work is done charges its runtime.
- **`--no-requeue`** — satisfies "no automatic retries or requeues" explicitly rather than by default.
- **Account `m3246`** (CPU), not `m3246_g`.
- **Memory:** the node default. A Perlmutter CPU node carries 512 GB; the declared reads need
  **under 8 GB** (largest single object read is `hXSecND_flat`, 65,856 float64 ≈ 527 KB; ten endpoint
  files ≈ 480 KB each). No `--mem` override is requested, so nothing is reserved beyond one node.
- **Released immediately** on completion by exiting the allocation shell; the run is a single
  non-interactive command, so the allocation ends when it returns.

**`alloc_run.sh` is deliberately NOT used.** It holds a `claude-hold` allocation alive with
`sleep 10800` (`alloc_run.sh:26,63-66`). That is exactly the hold-style dispatch measured at
`57128458`: elapsed `10,803 s` against a `10,800 s` request, metering `3.00` task-hours for `47:58` of
work. Using it here would breach the 30-minute limit and charge ~6x the runtime.

## 2. The environment

    source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh

The documented entry point (`2d-unfolding/2D_OMNIFOLD_REFERENCE.md:10-19`;
`nd-unfolding/sbatch_adopt_stamped_footing.sh:24-29`). It activates the `root_6_28` conda prefix by
full path via the creating base's hook, sources `unbinned_unfolding/build/setup.sh`, sets
`MINERVA_PREFIX` and sources `MINERvA101/opt/bin/setup.sh`.

**Sourcing it is a read of the deployed checkout, not a write to it.** No file under
`/pscratch/sd/j/josephrb/MINERvA-OmniFold` is created, modified or removed.

**PyROOT on a compute node under this environment is UNMEASURED.** On a login node with a bare
interpreter it segfaults during `import ROOT` (`cling::CIFactory::createCI`: cannot extract standard
library include paths → `modulemap.overlay` error → SIGSEGV). The environment script is the intended
fix; that it works has not been demonstrated. **If the import fails, the inspection stops and reports
that**, per "stop if the checks require work outside these limits". No package is installed, in a
shared environment or anywhere else.

## 3. Input paths — every file that would be opened

All under `MNV_DATA_ROOT=/pscratch/sd/j/josephrb/MINERvA-OmniFold`. Every file is opened `READ`.

| # | path | size | role |
|---|---|---:|---|
| 1 | `nd-unfolding/uq_5d/readopt_20260811_footing/stamped_bkgaware_meancentered_20260812.root` | 892,170,881 B | **G** |
| 2 | `nd-unfolding/uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root` | 41,436,632,945 B | **CS** — G's `combined_source` |
| 3 | `nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root` | unmeasured | **the central CV**, required only because G lacks the objects `PM-4` names — §5 |
| 4–13 | `nd-unfolding/uq_5d/universe_sweep_bkgaware/5d_xsec_MEFHC_5iter_lgbm_uni_full_<BAND>_<0\|1>.root` for the five `p4_lib.BANDS` | ~480 KB each | the ten `PM-3` endpoints |

**The directory is pinned, not the filename.** A second set of ten files with byte-identical names
exists at `nd-unfolding/uq_5d/universe_sweep/`, dated 2026-06-12 and of the wrong (non-`bkgaware`)
family. Filename identity is insufficient and the wrong set would silently answer a different question.

## 4. Intended reads — exactly these, in this order

| order | file | objects read | why |
|---|---|---|---|
| 1 | G | top-level TKey names/classes/cycles; scalars `combined_source`, `centering_convention`, `sqrt_tr_old`, `sqrt_tr_new`; `hInflation_g` bin count **only**; `hRowIndex5D` **only if the listing shows it** | bind CS by name, check stamps, establish the reported row count, and settle whether G carries a row index at all |
| 2 | CS | **top-level TKey listing only** — names matching `hCov_universe5d_<BAND>`, excluding `hCov_universe5d_total` | `PM-1` presence census and `PM-5` partition. **No `Get()` / `ReadObj()` on any band matrix** |
| 3 | central CV (file 3) | TKey listing; `hXSecND_flat` regular-bin contents (65,856 doubles) | reconstruct the mask and row-order digests — §5 |
| 4 | each of the ten endpoints, sequentially, closing each before the next | TKey listing; `hXSecND_flat`; the five `hXSec_{pt,pz,eavail,q3,W}` axis histograms (edges incl. final upper edge); scalars `ndim`, `dataPOT`, `globalCompleteness`, and `estimator_seed*` / `est_seed_offset*` when present | grid conformance, finiteness, support comparison, physical edges, available provenance |

**Digest algorithms, declared rather than invented** (`p4_evidence.py:78-84`; `p4_lib.py:1209-1218`;
`p4_build_components.py:198-203,224-230`): with `central` the regular bins of `hXSecND_flat`,
excluding under/overflow, `mask = central > 0`, `idx = np.nonzero(mask)[0].astype(np.int64)`,
`reported_mask_hash = sha256(idx.tobytes() + b"|C")`, `row_index_sha256 = sha256(idx.tobytes())`.
Zero-based ascending global indices on the C-order `(pt,pz,eavail,q3,W)` grid; native byte order; no
rounding. Comparison is **exact digest equality, no tolerance**, against S's committed
`reported_mask_hash = 74374b1af0795c3eb077c9ef0ee6ef3cfa4d7b7b3df63bd4f392d7db80eb136a` and
`row_index_sha256 = 61746918371fb9a99f69b8e657f98e0796ae9efd63e21a89346fbb620a596f08`
(`std_component_manifest.json:160-172`), expected count `10694`.

**Explicitly excluded as too expensive or unnecessary:**
- **No full sha256 of CS.** It would read all 41,436,632,945 bytes, and the historical digest already
  exists in G's own build receipt (`STAMPED_HASH_RECEIPT.slurm-56720356.json:18-22`).
- **No read of `hCov_combined5d_total`.** Its dense float64 contents are ≈0.9 GB; recomputing the
  block-sum trace is not part of this inspection. Reading only a diagonal afterward would not make the
  object read header-only.
- **No component-hash recomputation and no component builder run** — both load every band covariance.

**Read-onlyness, and where it can and cannot be proven.** G is 892 MB: its sha256 is taken before and
after and compared, so read-onlyness is *measured*, following `RECEIPT-20260816`'s G6 leg. CS is
41 GB: a before/after digest is not free, so for CS read-onlyness is **asserted by opening `READ` and
not proven by digest** — stated as a limitation exactly as `RECEIPT-20260816` stated it for the
39.4 GiB file, rather than claimed.

## 5. ⚠ What this inspection can and cannot discharge — declared before, not after

Discovered while writing this declaration, and it materially narrows the expected result.

- **`PM-4` cannot be discharged as written.** It requires G's mask digest and row-order digest **read
  from G**. G's committed key inventory is **13 keys** and contains neither `hRowIndex5D` nor
  `hXSecND_flat` (`receipt_candidate_stamps_5d.json:6-20`). The digests can only be *reconstructed*
  through G's producer-input route — the central CV at file 3, which G's launcher supplies by default
  (`sbatch_adopt_stamped_footing.sh:29,42-46`; `adopt_unified_5d.py:79,115-121`) — and G's own hash
  receipt does not bind that central file. **Any result must be labelled "digests reconstructed
  through G's producer-input route", never "read from G".** Whether that satisfies `PM-4` is a
  specification question for the spec author, not this inspection's to decide.
- **`PM-1` cannot be fully discharged from keys.** The key census closes the **presence** census only.
  CS's writer stores per-band covariances and totals and **no per-band migration census**
  (`analyze_universes_5d.py:189-211,270-293`), and a nonzero covariance is not evidence of migration.
  The weight-only/selection-support condition needs provenance CS does not carry.
- **`PM-5` is expected to be dischargeable** from the CS key listing alone: exact set partition of
  `F` into `V` (13, `adopt_unified_5d.py:42-43`), `A` (5, `p4_lib.py:18-19`) and `R` (the remainder),
  compared to S's recorded `45 = 13 + 5 + 27`.
- **`PM-3`'s grid arm is expected to be dischargeable**; its **footing arm is not**. The implemented
  background-mode evidence comes from `unfold_<BAND>_<EP>.log` (`p4_evidence.py:141-157`), and an
  equivalent provenance binding for the `universe_sweep_bkgaware/` endpoints is NOT RECORDED.

## 6. Prohibitions this inspection is bound by

No training. No covariance construction. No production execution. No modification of any source
artifact or frozen checkout. No package installation, into a shared environment or a private one. No
grading, discharge or adoption — this inspection **measures**; the SCOREBOARD/`OPEN_ITEMS` acts belong
to whoever owns those rows. No job beyond the single declared allocation. No requeue.

## 7. Outputs to be preserved

Inspection stdout/stderr, the key listings, every computed digest, the before/after G digests, and the
final `sacct` accounting for the allocation **including any failed execution time**, committed under
`docs/orchestration/state/`. Measurements are to be reported separately from any scientific reading of
them.
