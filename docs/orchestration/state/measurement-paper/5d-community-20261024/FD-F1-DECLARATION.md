# DECLARATION F1: the GENIE v3 held-out bias test of the 16-cell result (2026-10-27)

**By** the measurement session, for the director to review and bind.

**Under:**
- [`DECISION-20261027-joseph-limitation-plan-f1-bias-test-and-flux-bootstrap.md`](../../../DECISION-20261027-joseph-limitation-plan-f1-bias-test-and-flux-bootstrap.md) item 1: 1A runs, and Joseph's earlier "skip F1 for now" is lifted for this test only.
- [`DECISION-20261027-joseph-f1-genie-v3-both-tunes.md`](../../../DECISION-20261027-joseph-f1-genie-v3-both-tunes.md): both tunes, with seeds fixed a priori.
- [`FD-PLAN.md`](FD-PLAN.md) §5.2, F1a–F1c, and its statistics in §3.
- [`FD-DIRECTOR-RULINGS.md`](FD-DIRECTOR-RULINGS.md) §§2 and 4.
- The director's rulings of 2026-10-27, by correspondence:
  - the cost stays near the priced 0.84–1.25 node-h;
  - a pilot projection above that is a STOP, not an overrun;
  - the flux, grading and spline-version items in §7.

**MEASURES:** nothing yet. The declaration commits the code, its tests and the exact procedure. Nothing runs before
the binding.

**CANNOT AUTHORIZE:** a run (the binding does that), a change to the reported covariance, a claim, or any wording.

**What it is:** a bias test at two held-out truths. It is **not a coverage test**: Poisson pseudo-data with no
nuisance draws cannot test the intervals' width. The detector response is not probed, because every truth is a
truth-level reweight of the same MC under the nominal response (`FD-PLAN.md:528-533`).

## 0. Summary

| stage | what | job | expected | cap |
|---|---|---|---:|---:|
| F1a | per tune: reduced CH splines and their header check, gspl2root graphs, a 10,000-event timed pilot and its conversion; the phi_t flux file and its check; the budget gate | 1 node, 0:20 | 0.05–0.17 | 0.33 |
| F1b | per tune: 64 × 17,500 events, the sampled-spectrum check, hadd, conversion, then the pv-ladder ratios and their bridge | 1 node, --time from the gate (≤ 0:45) | 0.11–0.33 | ≤ 0.75 |
| receipt commit | the F1a and F1b digests, f1-prep-SHA256SUMS and the F1c tables | login | 0 | 0 |
| F1c | 2 closures and 2 × 20 pseudo-experiments on one node of 8 lanes | 1 node, 0:54 | 0.68–0.75 | 0.9 |
| grade | `fd_f0_regrade.py` with F0b's argv plus the F1 options | login | 0 | 0 |
| **F1** | | | **0.84–1.25** | **≤ 1.98** |

- **The budget gate** (§6) stops F1 before F1b if the pilot projects the total above 1.25 node-h. It also sets F1b's
  time limit, so the scheduler bounds what F1 can be charged: `budget.json`'s `worst_case_node_h`.
- **Every job is submitted by `nd-unfolding/submit_fd_f1.sh`**, whose lines carry the account, QOS, constraint, time
  limit and arguments. A test checks them.
- **Job rules:** regular QOS of m3246, never premium; no GPU; `--no-requeue`; every job under 12 h; ledgered from
  `sacct`; stopped past 1.25× its projected wall.
- **Nothing goes to CFS.** HPSS copies are planned (§9).

## 1. The truths and the seeds

**Two truths,** both Joseph's choice: GENIE v3.04.00 **G18_10a_02_11b** and **AR23_20i_00_000**.
- Each is the generator's own 5D shape relative to GENIE 2.12 CV, with no amplitude.
- They are non-vertex truths: neither is one of C_model,5D's three vertices.
- See §7 for the overlap of G18_10a's Nieves 2p2h with the GENIE+MEC vertex.

**Seeds, fixed here.** No committed task table or script uses any of them.
- `test_fd_f1.py` scans every committed `--pseudo-seed(s)` in a `.tsv` or `.sh` against the pseudo-experiment seeds.
- A `git grep` for the gevgen seeds found no use either.
- Products on pscratch were not searched. The binding's deploy step lists the F1 output root, which must not exist.
<!-- absence-ok: scoped to the Search line below; products on pscratch are explicitly not covered -->
Search: `--pseudo-seeds?\s+N(:M)?` over every committed .tsv and .sh (test_fd_f1.py); `git grep -nE "\b80[67]0[01][0-9]\b|\b6[01]0[0-6][0-9]\b"` in 3d-unfolding/genie, nd-unfolding and docs/orchestration/state @ 289f4457

| use | G18_10a_02_11b | AR23_20i_00_000 | earlier ranges, for contrast |
|---|---|---|---|
| gevgen pilot (F1a) | 60000 | 61000 | gevgen 1–18, 1001–1008, 50001, 51001, 52001 |
| gevgen production (F1b), seed = run number | 60001–60064 | 61001–61064 | |
| pseudo-experiments (F1c) | 806000–806019 | 807000–807019 | s5e/Stage 0 800000–805019; f4 970000–970015; s5p 12xxxxx–14xxxxx |
| estimator | 42 | 42 | every (e) product |

## 2. The samples: provenance and generation

**Software.** genie `v3_04_00`, qualifier `e20:prof`, from `/cvmfs/larsoft.opensciencegrid.org/products`.
- UPS forces the SL7 flavour `Linux64bit+3.10-2.17` with `-H`, as `setup_genie.sh` does for v2.
- `3d-unfolding/genie/setup_genie_v3.sh` sets it up and writes nothing.
  - It uses the existing compat-lib shim and refuses if `libssl.so.10` or `libcrypto.so.10` is missing.
  - It refuses unless the genie_xsec product sets `GENIE_XSEC_TUNE` to the tune asked for.
- A read-only check on login25 resolved all 121 libraries of `gevgen`, `gntpc` and `gspl2root`
  (`fd/receipts-f1/declaration/probes/probe6.sh` and `.out`).
  <!-- absence-ok: F1a is declared below to run v3 first; this states the declaration's own order, not that a result is absent -->
  F1a is the first v3 run here.

**Splines.** genie_xsec `v3_04_00`, from `NULL/<qualifier>/data/gxspl-NUsmall.xml`:

| tune | qualifier | NUsmall sha256 | README sha256 | README's version line |
|---|---|---|---|---|
| G18_10a_02_11b | G1810a0211b-k250-e1000 | `1b4b0b37…ee35` | `abfca258…6726` | "version v3_02_00 qualifier G1810a0211b:k250:e1000" |
| AR23_20i_00_000 | AR2320i00000-k250-e1000 | `185d7d8a…0bbb` | `744cba18…bcb2` | "version v3_04_00 qualifier AR2320i00000:k250:e1000" |

- **The reduction:** `run_gevgen_v3.sh reduce` keeps only the C12 and H1 splines. It uses `reduce_splines.sh`'s awk
  filter verbatim, which a test compares line for line.
- **The header check** (`gen5d_v3.py spline-check`, the director's ruling):
  - the source's and the reduced file's own `<genie_tune name=...>` must both be the tune;
  - their spline-list format must agree (`3.00`);
  - the reduced file must hold exactly the source's C12 and H1 splines;
  - the source and README must be the files pinned above (`gen5d_v3.SPLINE_PINS`, measured in
    `probes/probe10.out`);
  - the README's single version line must be the pinned line.
  - The spline XML names its tune and format but no GENIE version, so the README line is the product's own
    statement of the version. For G18_10a_02_11b it says v3_02_00 (§7).
- **Graphs:** `gspl2root` of the reduced file for C12 and H1, to 100 GeV, per tune.

**Flux: phi_t, sampled directly.**
- **The file:** `gen5d_v3.py make-flux` writes `flux_numu` with content = phi_t density × bin width on all 128 phi_t
  bins, 0–100 GeV.
  - `TH1::GetRandom` picks a bin by content and E uniformly inside it. So `gevgen -e 0,100 -f <file>,flux_numu,NOWIDTH`
    samples phi_t exactly.
  - **`,NOWIDTH` is required.** GENIE v3.04.00's `gEvGen.cxx` (`src/Apps/gEvGen.cxx:528-548` on CVMFS,
    `probes/probe13.out`) multiplies every bin of a variable-width histogram by its width unless the flux string ends
    in `,NOWIDTH`.
    - v2.12.10c, which the 50–100 GeV supplement used, has no such step.
    - Without it, gevgen would sample phi_t × width², off by up to 100× between bins.
  - It is the supplement file's construction, `gen5d_flux_supplement.py make-flux`, over the full range.
  - No flux reweight follows.
- **Controls** (the director's ruling: phi_t must reproduce the data's constrained CV flux). Each refuses, writing
  nothing:
  - `phi_t.npz` is the pinned file (`bbcbade3…c5`), with `phi_t.json`'s own record of it;
  - `phi_t.json` defines phi_t as the FluxReweighter CV flux "nuE constraint true", over the 12 ME FHC playlists;
  - the file's integral, Σ contents, equals the data normalisation's `hFluxCV` (`2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root`,
    sha256 `5eecae84…80eb`, bin 1) to 1e-12 relative.
    - phi_t.json records 5.2e-16.
    - A read-only check today read `hFluxCV` bin 1 = 6.243343376851217e-4, which is Φ_t.
  - the file reads back bit for bit;
  - **what gevgen actually samples:** each work directory's `input-flux.root`, histogram `spectrum`, is what gevgen
    writes of the spectrum it samples (`gEvGen.cxx:570-571`). `gen5d_v3.py flux-check` requires it to equal the flux
    file's contents and edges bit for bit: in F1a for both pilots, and in F1b for all 128 tasks;
  - in each conversion, the strict sampling test (below).
  - `hFluxCV` itself was read on login25 (`probes/probe11.out`).

**Generation** (`run_gevgen_v3.sh genie`). The flags follow `run_gen5d_supplement.sh`'s gevgen and gntpc lines:
- `-p 14`;
- `-t '1000060120[0.9225],1000010010[0.0775]'`;
- `-e 0,100`;
- `-f <flux>,flux_numu,NOWIDTH`;
- `--tune <tune>`, with the tune's own generator list (Default: no `--event-generator-list`);
- `--cross-sections <reduced splines>`;
- `--seed S -r S`;
- the laconic messenger.

Then `gntpc -f gst`. The GHEP file is deleted; the gst is the product.

- **Pilot (F1a):** 10,000 events per tune, timed.
- **Production (F1b):** 64 tasks × 17,500 = 1,120,000 events per tune. The 128 tasks run at once on one node's 128
  cores, followed by `hadd`.
- **Against FD-PLAN's F1b** (1M + 0.1M at 50–100 GeV per configuration):
  - one range at the same total, 1.12M;
  - so no supplement normalisation and no range merge.
  - The cost is fewer events above 50 GeV, where σ_CC holds 0.44 % of the total (`state/s5p/gen5d/README-gen5d-fluxfix.md:154`).
  - The ratio's gate pools or sets r = 1 in cells with too few events (§3).

**Conversion** (`gen5d_v3.py convert`):
- **The binning:** the events go through `gen_to_xsec5d.py`'s GENIE extraction and `genie_cv` binning, imported
  unchanged. That is the same phase space, E_avail, q3 and W, and the same reader parity on the first 20,000 events.
- **The output:** a gen5d/v1 npz on the 65,856 cells.
- **The normalisation** is genie_cv's, σ_CC/13 × N_bin/N_CC. F1 uses the prediction only through a k-normalised shape
  ratio, so a global factor cancels.
- **Refusals** (exit 1, nothing written):
  - a non-finite axis value;
  - a reader-parity mismatch, or no events checked;
  - a failed **strict sampling test**: `gen5d_flux_reweight.sampling_test`, imported, on the CC events' E_ν against
    phi_t × σ_CC from the tune's own graphs. It needs p ≥ 1e-3 across and within bins, and no event outside the
    generation bins. The f_MEC fraction is recorded.

## 3. The truths as reweights

`nd-unfolding/fd_f1_prep.py`:
1. **A pvl-config/1 copy of the committed `nd-unfolding/pv-ladder/config.json`** (`078df3b6…8310`).
   - Its `vertices` are replaced by the two F1 predictions, each with its path and sha256.
   - Everything else is unchanged: rung L-5D-PV's npz (`07fccc1a…`) and bkg (`2addac8f…`), the recorded central
     value whose positive cells are the region (P5, `e36f3b25…`), the GENIE 2.12 CV reference (`cfa42210…`) and
     `stat_max` 0.05.
2. **`pvl_ratios.main`, imported unchanged:** each truth's gated, k-normalised shape ratio r to GENIE CV per fine cell.
   This is exactly how the C_model,5D vertices and the NuWro closure were built.
3. **The bridge** of each r to `s5e-shape-ratio/1` (axes 0–4, the fine edges, `shape_ratio` = r).
   - The pseudo-experiments' `ratio_nd` truth then applies the same per-cell r.
   - It rescales the in-grid w_truth total by one constant, as every ratio_nd truth does.
   - A test shows this equals `pvl_lib.row_weight` row by row up to that constant, with the -9999 sentinels of fakes
     left at 1.
   - A ratio with a truth cut is refused, since ratio_nd has no equivalent.
4. **`f1-prep-SHA256SUMS`** over everything written.

<!-- absence-ok: the region rule restates the pv-ladder's own convention (pvl_ratios.py:10, :123) and FD-PLAN ruling 6; it claims nothing about what was read -->
**The region:** the cells where P5's `xsec_flat` is positive, as for every vertex. This uses positivity only;
FD-PLAN's ruling 6 already covers using f.

## 4. The products (F1c)

`nd-unfolding/fd_f1_tasks.py` writes two tables from the committed `f1-prep-SHA256SUMS`: `f1c-steps.tsv` and
`tasks-f1c.tsv`.
- **Closures:** per truth, one noise-free, signal-only closure. It is the NuWro closure's `pvl_unfold.py` line from
  `sbatch_pvl.sh`: rung L-5D-PV, arm e, all features, `--closure`, the truth's pvl-ratio file with its committed
  sha256 as `--expect-ratio-sha256`, the npz and bkg with their pins, `--estimator-seed 42 --threads 32 --iters 5`.
- **Pseudo-experiments:** per truth, 20 Poisson experiments on half the MC.
  - It is F0's row 1 W2 line, `state/s5e/cand-assess-tasks.tsv` `aW2_s804000`, with only `--eavail-ratio` (the bridged
    ratio), `--pseudo-seeds` and `--out` changed.
  - That gives `s5e_candidate.py --candidate R`, negweight-refined background, truth `ratio_nd` at amplitude 1.
  - A test checks every other field against the committed line.
- **The estimator (e)** is S1's and F0's: LightGBM 100/8, 5 iterations, seed 42, deterministic, all-row binning; the
  Stay-Positive refinement 400/31 at 45 (candidate R; the closure records that the refinement did not run). The
  grader's `estimator_problems` checks every product's meta against this.
- **Packing,** as FD-PLAN §5.2 priced it:
  - one node with 8 lanes of 32 CPUs and 56 GB each (s5p's largest recorded step MaxRSS was 42 GiB, `measurement-scoping/pv-ladder/RUN.md:154-155`);
  - lanes 0–1 run one truth's closure and then 4 of its experiments;
  - lanes 2–4 and 5–7 run 6, 6 and 4 experiments of the G18 and AR23 truths;
  - `nd-unfolding/fd_f1_lane.py` runs a lane's steps in order and stops at the first failure;
  - the job is the committed `state/gpu-timing-20261023/tools/sbatch_timing_packed.sh` →
    `nd-unfolding/s5c_array.sh` (pinned-sha refusal and the guarded run) → `fd_f1_lane.py`.
  - **The submission** is `submit_fd_f1.sh f1c <deploy> <receipt pin> <OUT> <deploy>/…/tasks-f1c.tsv`. It runs
    `sbatch --account=m3246 --qos=regular --constraint=cpu --nodes=1 --exclusive --no-requeue --time=00:54:00
    sbatch_timing_packed.sh <deploy> <pin> <table> <OUT>/f1c 32 56G 0 7 none`, with no GPU request.
  - **Steps write their products** under `<OUT>/f1c/products/`: `closure/` and `pe/<truth>/`.
  - **Expected wall:** about 2,450 s plus load. The limit is 0:54, which is 1.25 × 2,550 s rounded up.

## 5. Grading, fixed before any F1 product is read

**The command:** `fd_f0_regrade.py` with F0b's recorded argv (`fd/receipts-f0b/step3.sh`), including `--extra-block`
for C_resp (`4d8b5797…`), plus:
- `--f1-prep-sums` and `--f1-prep-sums-sha256` (the committed prep manifest);
- `--f1-products-sums` and `--f1-products-sums-sha256`: the committed F1 product manifest, written by
  `fd_f1_tasks.py manifest --runs <OUT>/f1c/products`. That lists exactly the 42 declared products and refuses a
  missing one, a stray file or a `.partial`;
- `--f1-root`;
- `--f0b-readout` and `--f0b-readout-sha256` (`fd/readout/fd_f0b_readout.json`, `b9db935a…`).

It runs on a login node at 0 node-h, in F0b's environment: root_6_28, Python 3.11.14, numpy 1.26.4,
`env -u PYTHONPATH … -I -B`. Control 9's exact equality relies on that.

**The statistics are FD-PLAN §3's, unchanged:**
- **Ensembles (row 7):** r_i = X̂_i / X_true,i − 1 on R00–R15 by S1's integration rule. b = the unweighted mean, and
  N = Cov_i(r)/B (ddof 1).
- **Closures (row 8):** the noise-free r, with N = 0.
- **The grade matrix:** non-vertex, so C_total + C_resp with all three vertices.
  - Per-cell z = b/√diag(C + N).
  - χ² = bᵀ(C + N)⁻¹b, ndf 16, with the p value **descriptive** (b is a deterministic bias).
- **Triggers** (ruling 2: reporting triggers, not gates): |z| > 2 per cell, or p < 0.01 per truth.
  - They are counted in the truths' own group, **held-out**, with its denominators and the Gaussian reference.
  - That group is never pooled with the vertex-family, non-vertex or prior groups. It is also kept out of
    `all_graded`, so F0b's denominators stay F0b's.
- **The declared sensitivity matrix** leaves the GENIE+MEC vertex out. It is descriptive (§7).
- **The model-only variant** is descriptive, as in F0.

**Control 9:** in the same run, each of F0b's 18 truths must grade exactly as the committed F0b readout records it:
every field of every record. So the F1 readout is F0b's plus four records.

**The leak guard** (ruling 6) covers every output, as in F0b.

**The readout:** `fd-f1-readout/1`, labelled "a bias test at two held-out GENIE v3 truths, not a coverage test…".

## 6. Controls, planted defects and stop rules

| stage | control | refuses / stops on | planted defect (test) |
|---|---|---|---|
| every job | deploy HEAD = pin, no modified tracked file | another commit or a dirty tree | (the launchers' standing check, as sbatch_pvl.sh) |
| F1a | spline header check | another tune (in either file), list format, spline set, source or README file, version line or count | `Gen5dV3.test_spline_check`, nine defects; `test_the_committed_pins` |
| F1a | flux file | another phi_t or hFluxCV file, a phi_t not defined as constrained, an integral off hFluxCV by > 1e-12, a bad read-back | `Gen5dV3.test_phi_t_and_integral_checks`, `test_flux_contents`, `test_pins` (pure parts; the ROOT step first runs in F1a) |
| F1a, F1b | the sampled spectrum (NOWIDTH) | a work directory whose `input-flux.root:spectrum` is not the flux file bit for bit, or is missing | `Gen5dV3.test_same_spectrum`; `Scripts.test_generation_settings` asserts `,NOWIDTH` |
| F1a, F1b | conversion | non-finite axis, parity mismatch, a failed sampling test | `Gen5dV3.test_refusal_rules` |
| F1a | **budget gate** (`fd_f1_budget.py`) | projected F1 > 1.25 node-h, or 1.25 × projected F1b wall > 45 min: **STOP to the director**. On GO it writes F1b's time limit | `Budget.test_go_and_stop`, both rules on each side, the limit and the worst case |
| F1b | GO from F1a; every gevgen task rc 0; 64 gst per tune | anything else | (launcher) |
| F1b | prep | a prediction off its sha256, an existing output, the wrong truth set, a non-positive or wrong-length r, a truth cut | `Prep.*` |
| F1c | tables | a lane plan that misses or repeats a seed, a truth without exactly one closure | `Tasks.test_plan` |
| F1c | lanes | an entrypoint outside nd-unfolding; the first failing step stops the lane | `Lane.*` |
| receipt | the product manifest | a missing product, a stray file or `.partial`, another directory | `Tasks.test_manifest_lists_exactly_the_declared_products` |
| grade | controls 0–8 (F0b's) and 9 | as F0b; plus the F1 manifests' digests, an unlisted product, a wrong ratio or bridged-ratio identity, a count, any changed field of an F0b record | `GraderF1.*` |
| every job | the submission lines | another account, QOS, constraint or limit; a GPU request | `Scripts.test_batch_scripts_agree_with_the_budget` |

**How F1a's pilot feeds the budget gate.**
- It charges the pilot's whole wall, spline load included, to its 10,000 events.
- It multiplies by a declared contention factor of 1.25, because the pilot runs 2 processes on an idle node and F1b
  runs 128. The pilot does not measure memory-bandwidth and clock contention.
  - So the projection bounds F1b only if contention stays under 1.25× (the review's caveat).
  - The scheduler limit, 1.25 × the projection, is the hard bound.
- It adds one load per F1b task, and 900 s for `hadd`, conversion and prep. The pv-ladder prep took 318 s.
- It takes F1c at its priced 0.75 node-h.
- GO only if both rules hold.
- `worst_case_node_h` adds F1a's time so far, F1b's limit and F1c's 0:54. That is the most F1 can be charged, which
  is at most 0.33 + 0.75 + 0.9.

**The other stop rules:**
- **F1b runs only on GO.**
- **Every job** has a scheduler limit of about 1.25× its projected wall, set in `submit_fd_f1.sh`; F1b's comes from
  the gate.
- **Any failure is a STOP for the director.** Nothing is retried or repaired without a ruling.
- **The receipt commit between F1b and F1c** (as the pv-ladder's `prep-SHA256SUMS`):
  - It commits `f1a-SHA256SUMS`, `f1b-SHA256SUMS`, `f1-prep-SHA256SUMS`, the gen5d meta JSONs, `budget.json`, the
    spline-check JSONs and the two F1c tables that `fd_f1_tasks.py tables` writes from them.
  - After F1c, a second receipt commit adds the product manifest from `fd_f1_tasks.py manifest`. The grade reads it.
  - It changes only paths under `fd/receipts-f1/`.
  - The F1c deploy pin is that commit, and `git diff --stat <bound pin> <F1c pin>` must list only those paths.

**Tests:** `nd-unfolding/tests/test_fd_f1.py`, 31 tests, plus `test_fd_f0_regrade.py`'s 47 for F0/F0b, unchanged.
`fd/receipts-f1/declaration/tests-local.log` and `mutants.log` hold the outcomes (§10).

## 7. Choices for the director's ruling

1. **Flux:** phi_t is sampled directly, not the v2 route of an unweighted flux plus reweight. The control is §2's:
   the pinned phi_t, its constrained definition, its integral against hFluxCV, and the sampling test.
2. **Grading as a non-vertex truth,** against the full C_total + C_resp.
   - **The overlap:** G18_10a_02_11b carries the Nieves et al. (Valencia) 2p2h model. The GENIE+MEC vertex is GENIE
     2.12 + Valencia MEC, the same model family. So part of G18's departure from GENIE CV lies along a direction
     C_model,5D already holds.
   - **The companion variant:** the declared sensitivity matrix leaves the GENIE+MEC vertex out, and is descriptive.
   - **AR23_20i_00_000 overlaps too.** Its configuration on CVMFS (`config/AR23_20i/ModelConfiguration.xml`;
     `probes/probe12.out`) names `NievesQELCCPXSec` with a z-expansion form factor for CCQE and `SuSAv2MECPXSec` for
     2p2h. G18_10a names `NievesQELCCPXSec` and `NievesSimoVacasMECPXSec`.
     - So the two truths share their CCQE model and are not independent.
     - AR23's 2p2h is not the Valencia family.
     - The same descriptive leave-out-MEC variant is reported for both.
3. **Spline version:**
   - G18_10a_02_11b's splines ship in the v3_04_00 product, but their README says they were made with v3_02_00; they
     are dated 2022-03-18.
   - AR23_20i_00_000's say v3_04_00.
   - The events are generated by v3.04.00 with those splines. The provenance is recorded per tune, and the header
     check is §2's.
4. **One energy range** at 1.12M events per tune, in place of FD-PLAN's 1M + 0.1M at 50–100 GeV (§2).
5. **F1c packing:** one node with the lane launcher, as priced, in place of separate closure and pseudo-experiment
   jobs.
6. **The cost enforcement** (§6): the gate's contention factor of 1.25, and F1b's scheduler limit set from the
   projection.
7. **HPSS** (§9): the gst files and reduced splines are copied, since they depend on the CVMFS state. The gen5d
   predictions, ratios and unfold products are small and reproducible from the deploy and pinned inputs, and are
   copied with them.

## 8. Inputs and pins

| input | path | sha256 |
|---|---|---|
| phi_t | `/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix/phi_t.npz` | `bbcbade310d90e1ae487dde9d982e85cfe16fae35bba09dbde7db2dc99274ec5` |
| hFluxCV | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root` | `5eecae84509ba8ededbe8fdee63508d8e36cd057cc0547a940383f80248580eb` |
| G18 splines, README | CVMFS `…/G1810a0211b-k250-e1000/data/` | `1b4b0b37fc8c11acbf00884a94d0a3bda519d9c458f2c916573ef3d673a3ee35`, `abfca258817a3f7d8169cdd2dbf9349a025ab38312435c718347598b53f16726` |
| AR23 splines, README | CVMFS `…/AR2320i00000-k250-e1000/data/` | `185d7d8a4674b5df445fcadea3d17232804390c8421d563aa402c6ee743a0bbb`, `744cba18f82cc5fe4805cd8be120e5f7e5f7b36f657f4cc9f2118e69c803bcb2` |
| GENIE 2.12 CV reference | `/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix/genie_cv_xsec5d_full.npz` | `cfa42210dfe9cadc8e9460333316a639bd719c9ae52ab1144be900372a9adcc2` |
| pv-ladder config | `nd-unfolding/pv-ladder/config.json` (committed) | `078df3b6f361eca32c685374fc0b953024f69cf0bd49c1ebc25ea2b95f0f8310` |
| unfolding MC, background | as the config's L-5D-PV rung | `07fccc1a…649f`, `2addac8f…2d82955` |
| C_resp | `/pscratch/sd/j/josephrb/cresp-20261026/out/cresp.npz` | `4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a` |
| F0b readout | `fd/readout/fd_f0b_readout.json` (committed) | `b9db935a3187646ba2accaf3865cf4aa26ad72676063c58e7f5e6220224ef17b` |

The binding re-measures each digest before F1a.

## 9. Outputs and storage

- **pscratch:** `/pscratch/sd/j/josephrb/fd-f1-20261027/`, with `f1a/`, `f1b/` (about 1.1 GB of gst per FD-PLAN's
  sizing, two 1.6 MB predictions, the prep) and `f1c/` (42 products, about 8 MB).
- **HPSS:** one tar of `f1a/splines`, `f1b/gst`, `f1b/gen5d`, `f1b/prep` and `f1c/products`.
  - It follows `stage0_preserve.sh`'s pattern: `hsi put`, `hashcreate`, `hashverify`, get-back and sha256 compare.
  - Size about 1.2 GB; about 89 GiB was free at the last `hpssquota` (FD-PLAN §5).
- **Committed:** the receipts under `fd/receipts-f1/` and the readout `fd/readout/fd_f1_readout.json`, with its table
  on pscratch as F0b's.
- **CFS:** nothing.

## 10. Code and tests at this commit

**New:**
- `3d-unfolding/genie/setup_genie_v3.sh`
- `3d-unfolding/genie/run_gevgen_v3.sh`
- `3d-unfolding/genie/gen5d_v3.py`
- `nd-unfolding/fd_f1_prep.py`
- `nd-unfolding/fd_f1_tasks.py`
- `nd-unfolding/fd_f1_lane.py`
- `nd-unfolding/fd_f1_budget.py`
- `nd-unfolding/sbatch_fd_f1a.sh`
- `nd-unfolding/sbatch_fd_f1b.sh`
- `nd-unfolding/submit_fd_f1.sh`
- `nd-unfolding/tests/test_fd_f1.py`

**Changed:** `nd-unfolding/fd_f0_regrade.py`, adding the F1 options and control 9. Without the options it is F0b's,
and its 47 tests pass unchanged.

**Receipts** (`fd/receipts-f1/declaration/`):
- `tests-local.log`
- `mutants.py` and `mutants.log`: 45 planted defects across the new code and the F1 lines of the grader, the last
  13 for the review's findings.
  - In the first round, 30 of the first 32 were killed. The two survivors, the source-tune and extra-spline checks
    in `spline-check`, had no test that isolated them, so two cases were added. <!-- absence-ok: the mutation log's own survivors (mutants.log round 1), not a claim about the repository -->
  - `mutants.log` is the full rerun of all 45, with 44 killed. Mutant 26 targeted the control-9 line that round 2
    replaced, so it no longer applied. Re-pointed at the new line, it is killed in `mutants-26.log`.
- `probes/`: the read-only cluster checks cited here (the ldd resolution, spline headers and READMEs, pins, hFluxCV,
  the v3 source and the tune configurations).

**Not unit-tested, because they need ROOT or GENIE:**
- the ROOT steps of `make-flux` and `convert`;
- the GENIE scripts.

All of these run first in F1a, at its 0.33 node-h cap, where any failure is a STOP. Their pure parts are tested.

## 11. Review

An independent read-only review, with read-only checks of the CVMFS sources, ran before the PR. Its findings and what
was done are in §12.

## 12. Review dispositions

| finding | severity | done |
|---|---|---|
| GENIE v3.04.00 multiplies a variable-width flux by its widths unless `,NOWIDTH` is given, so the pilot would sample phi_t × width² | blocker | `,NOWIDTH` added; `flux-check` compares the sampled `input-flux.root:spectrum` with the file bit for bit, in F1a and F1b; tests and mutant 33. Confirmed in `gEvGen.cxx:528-548, :570-571` (`probes/probe13.out`) |
| the cost stop rules were not enforced by the scheduler; the pilot does not model 128-process contention | medium | F1b's `--time` is set from the gate's projection × 1.25; F1c's limit is 0:54; a contention factor of 1.25 enters the projection; `worst_case_node_h` is recorded; `submit_fd_f1.sh` carries every submission line |
| F1c's submission line was not declared | medium | `submit_fd_f1.sh f1c`, tested |
| nothing produced the F1 product manifest | medium | `fd_f1_tasks.py manifest`, which refuses missing, stray and `.partial` files; tested; a second receipt commit |
| the spline-version and pin controls recorded but did not compare | medium | the README version lines, NUsmall and README digests, and the hFluxCV digest are pinned and enforced |
| the both-tunes decision is not on this branch's base | medium | `origin/main` merged before the PR |
| the seed scan does not cover the gevgen seeds or pscratch products | medium | a Search line for the gevgen seeds; pscratch is explicitly not covered, and the binding's deploy step requires the output root to be absent |
| the held-out group was pooled in `all_graded`; `labels.not` said "not held-out truths" | low | held-out kept out of `all_graded`; the label is corrected in F1 mode; tested |
| control 9 was not field for field; it depends on the environment | low | it now compares whole records; the environment is stated; tested with a non-numeric field; mutant 45 |
| the planted-defect column overstated the tests | low | make-flux's pure checks, the format mismatch and the pins are now tested; the column is updated; the grader's and the tables' constants are cross-checked; the harness's count is fixed |
| the sentinel comment, the ldd receipt, the G18 generator label, the AR23 overlap | low | corrected; the probes are committed under `probes/`; the label says what made the splines; §7 states the AR23 overlap from its configuration |
