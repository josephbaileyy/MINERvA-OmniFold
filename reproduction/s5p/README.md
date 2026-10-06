# s5p reproduction harness

**CITABLE FOR:** how to reproduce, from a fresh checkout, the already-final s5p components: the flux-repaired
generator predictions and their input identities, the deliverable generator figures and numbers built from them
(`VALIDATION_LEDGER.md` VL156–VL160), the pre-freeze quantities of the joint-test design, and (tier D) the committed
outputs of the final joint result's evaluator and label step. It also records which of these reproduce, and to
what tolerance.
**NOT CITABLE FOR:** any physics result, grade, adoption or release, and no statement about the joint result itself.
Agreement shows that the committed calculation was re-executed faithfully. It does not show that the calculation is
scientifically adequate, and tier D does not grade the independent recomputation. There are no joint-result figures
yet, so none is reproduced.

The scope is declared as data in [`scope.py`](scope.py): pinned receipts, recorded roots, tolerances, figure
runs, declared differences, and the not-run tier. The engine is [`repro_s5p.py`](repro_s5p.py). Every expected
value is read from the committed receipts, never from this README.

## Tiers (separate claims; the report never merges them)

| tier | what it does | runs here |
|---|---|---|
| **A replay** | Pins the 56 committed receipts, logs, designs, figures and joint outputs. Re-measures every file digest the 39 JSON digest-source receipts record, on the preserved bytes, and checks that every other recorded digest was compared. Compares the checkout's producers with the code that ran. Recomputes the committed numbers from stored products: integrated σ of every 5D prediction; F2/F4/M1 summary statistics; V's fields. Checks the lane-pinned inputs no receipt digests (401 from 2026-09-28; 8328 joint calibration/power/status files from 2026-10-06). | numpy only |
| **B regenerate** | Re-runs the committed producers from **this checkout** into a fresh directory, on the preserved inputs, and compares: `gen5d_to_rootpreds.py` (8 prediction ROOT files, all histograms bitwise); the six figure runs (logs exactly, PDFs bitwise except creation date and document ID); `s5p_pairdiff.py` (17 F2/F4/M1 pair differences, arrays bitwise); `s5p_prefreeze.py units`/`devpower`; `s5p_joint.py build-v` (V bitwise); `s5p_envelope.py`. Each producer runs through [`_launch.py`](_launch.py), which refuses a run that imported project code from outside the checkout (OI-136). | needs PyROOT (root_6_28) |
| **C not regenerated** | Full scientific regeneration: event generation, the flux reweight from events, the per-mode files, the production unfolds, the joint seed-state classification and the missing-seed sensitivity. Each item is listed with its dependency and reported `NOT_RUN`. | never |
| **D joint** | The final joint result: replays `s5p_joint.py evaluate` (with the evaluation's thread settings) and `s5p_robust_labels.py` from **this checkout** on the lane-pinned calibration and power products and compares them with the committed `joint-evaluate.json` / `robust-labels.json` at the same-code tolerance; checks the design/V/evaluate identities the joint receipts and status files record, and the final B and power n against the pinned products; the seed-states copy against its original's digest; the frozen modules against `4f5a613f` and every imported module against the evaluation deploy `e9372b75`. Records the independent recomputation's report by digest (identity with the report the recording cites; never graded). The joint figures are a `PENDING` row: none exists yet. | numpy only |

## Commands (Perlmutter login node, about 4–10 min depending on login-node load; 244 s on 2026-10-06)

```bash
git clone https://github.com/josephbaileyy/MINERvA-OmniFold.git CHECKOUT   # full history: tier A reads git blobs
cd CHECKOUT && git checkout <commit>
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"      # Python 3.11.14, numpy 1.26.4, ROOT 6.28/12, matplotlib 3.10.8
export TMPDIR=$SCRATCH/tmp
cp reproduction/s5p/config.example.json /path/config.json   # set out_dir to a NEW directory
python3 reproduction/s5p/repro_s5p.py list                  # the declared scope
python3 -m unittest discover -s reproduction/s5p/tests      # controls; no products or ROOT needed
python3 reproduction/s5p/repro_s5p.py run --config /path/config.json \
    --pins reproduction/s5p/pins/unrecorded-inputs-20261006.json
```

`run` writes `report.json`, `report.md`, the regenerated products, the logs and the per-producer import
provenance under `out_dir`. Exit codes:

- **0** only if tiers A, B and D all ran; every A/B row is `REPRODUCED`, `REPRODUCED_WITHIN_TOLERANCE` or one of
  the seven `DECLARED_DIFFERENCE`s; the joint replay reproduced; and every other D row passed or is one of D's two
  declared non-grades (`joint:independent-verification` `INFO`, `joint:figures` `PENDING`);
- **1** on any `MISMATCH`, or on any `ERROR` (a harness exception, recorded as a row), in any tier;
- **2** otherwise: a missing input, environment or pins file, a `NOT_RUN` or `INFO` row in A/B, any other
  non-passing D row, or a tier not run.

A `PENDING`, `INFO` or `NOT_RUN` row never counts as reproduced.

The pins file to use is `pins/unrecorded-inputs-20261006.json` (`scope.PINS_FILE`). It was made by
`pin --extend pins/unrecorded-inputs-20260928.json`: the six 2026-09-28 groups are copied from that file verbatim and
keep its measurement time (21:56Z 2026-09-28; a unit test checks the copy), and only the three tier-D groups were
measured. The 2026-09-28 file alone now fails the pin-population rows of the tier-D groups.

## Reading a report

Every row carries a **basis**: what its agreement rests on.

| basis | meaning |
|---|---|
| receipt-recorded digest (historical provenance) | the producing campaign recorded this digest; the preserved bytes still hash to it |
| receipt-recorded digest, bytes read from git history | as above, for a code copy whose scratch export was removed; the bytes are the export commit's git blob |
| lane-pinned digest (newly recorded by this harness; NOT historical provenance) | no producer recorded it; `pin` measured it on 2026-09-28. A match proves only constancy since then |
| committed file vs scope.py pin | a committed receipt, log, design or figure equals the bytes this scope was written against |
| code identity vs recorded code | the checkout's producer against the code that ran |
| recomputed from preserved products | a committed number recomputed from the stored product |
| regenerated by this checkout's producer | a committed output regenerated into the output directory |
| coverage of the receipts' recorded digests | every 64-hex value in the receipts was compared by some row |

`report.md` puts each group in its own section: failures; the declared differences, each listed individually
with its recorded and observed digest and its reason; within-tolerance rows; the lane pins, counted apart from
the receipt-backed digests; not-run and pending rows; and last, the exact matches, grouped by basis.
`report.json` records the pins file's path, sha256 and measurement time. It also carries
`declared_differences` as a separate list.

Do not activate the environment through `setup_salloc_env.sh`. It sources `unbinned_unfolding/build/setup.sh`,
a build artifact that a fresh checkout lacks. The environment activated by prefix, as above, is the one the
generator-context receipts record. The committed logs also carry RooUnfold rootmap warnings, which exist only
under the full analysis environment. The harness drops ROOT `Info`/`Warning` lines from both sides before it
compares a log.

## Configuration

One JSON file ([`config.example.json`](config.example.json)):

- **`roots`**: the four input roots. The receipts record absolute paths under
  `/pscratch/sd/j/josephrb/{s5p-20260926,MINERvA-OmniFold,s5e-20260925}` and `/cvmfs`. These are identities
  that are re-rooted onto the configured roots, never read directly.
- **`out_dir`**: must be new and outside the checkout and every root.
- **`joint.independent_compare`**: the independent recomputation lane's report route. It is the extended
  comparer's report, `/pscratch/sd/j/josephrb/s5p-parallel-recompute/final-ext/compare.json` (sha256 `97e1666a…`,
  the report `RECORD-20261005-s5p-joint-5d-inference-result.md` §4 cites; also on branch
  `s5p-parallel-recompute-20260928` at `docs/orchestration/state/s5p/recompute/final-ext/compare.json`). The
  older `final/compare.json` was the earlier, incomplete run; tier D reports any other digest as a `MISMATCH`.

**Relocation.** `stage` copies exactly the declared inventory into a new tree, `<to>/<root>/<relative path>`,
and checks each copy's digest. The declared inventory is every receipt-recorded file plus every lane-pinned
file. Point `roots` at `<to>/{s5p,analysis,s5e,cvmfs}` and trace the run:

```bash
python3 reproduction/s5p/repro_s5p.py stage --config CONFIG --pins PINS --to STAGE      # reads only; writes STAGE
strace -f --seccomp-bpf -e trace=%file -o TRACE \
    python3 reproduction/s5p/repro_s5p.py run --config RELOCATED_CONFIG --pins PINS
python3 reproduction/s5p/repro_s5p.py scan-trace --trace TRACE --expect-prefix STAGE
```

`scan-trace` exits 1 if the run touched any path under a recorded root. It exits 2 if the trace shows no access
under `STAGE`, meaning it could not have looked. If the run reports `INPUT_MISSING`, the declared inventory is
incomplete.

## Required artifacts and their identities

- **Committed** (pinned in `scope.RECEIPTS`): the gen5d build and flux-fix receipts (rounds 1–3); the
  generator-context receipt, its 8 prediction sidecars, the E_avail ratios and the 7 logs; the F2/F4/M1 JSONs; the
  V, units, devpower and envelope receipts; the draft and frozen designs; the J-partition definitions; the six
  note figures.
- **Preserved on scratch, digest recorded by the campaign**: every `(path, sha256)` pair in those receipts (383
  distinct paths, 384 (path, sha256) pairs; tier D added the cluster copy of `joint-evaluate.json` that `robust-labels.json` records), including the flux-repaired 5D predictions, their inputs (pre-fix products, `phi_t`, GENIE graphs,
  cvmfs flux files, supplement events), the stored ROOT prediction and mode files, the F2/F4/M1 and V products,
  and the envelope's prior unfolds. The figure producers ran from a scratch export of `4e4b4f56` that has since
  been removed. Their recorded digests are therefore checked against that commit's git blobs, and each report
  row says so.
- **Preserved, digest recorded by nobody**: the untracked figure data in the canonical analysis checkout (3D unfold,
  covariance, stat band, Tune-v1, the committed pre-repair GENIE files, the gst events, `excess_eavail_W.root`);
  the lateral endpoints and data jitters; the V ensemble and power pilot; the M1 mid asimovs; the s5e W2 ensemble;
  the MnvTune 5D prediction. [`pins/unrecorded-inputs-20260928.json`](pins/unrecorded-inputs-20260928.json)
  pins them (lane-measured 2026-09-28, 401 files). A pin proves only that the bytes are constant since that
  measurement. What ties them to production is that tier B regenerates the committed outputs from them bitwise.
- **Tier D, preserved, digest recorded by nobody**: the five nulls' calibration ensembles (`runs/prod/cal/<null>/`,
  partials excluded, one product per counted draw of the final B), the six power ensembles (`runs/prod/pow/<set>/`)
  and the five sequential-status files (`runs/prod/status/<null>-final.json`). No receipt records their digests, so
  [`pins/unrecorded-inputs-20261006.json`](pins/unrecorded-inputs-20261006.json) pins them (lane-measured
  2026-10-06). What ties them to the joint result is tier D's replay of the committed evaluator output from them.
  The report-only recovered products under `s5p-20260926/recovery/` are **not** inputs of the frozen joint result
  and are outside every glob.
- **Tier D, committed**: `state/s5p/stage7/joint/{joint-evaluate,robust-labels,missing-sensitivity}.json` and
  `seed-states.abs-log-paths.json` (pinned in `scope.RECEIPTS`). `joint-evaluate.json` and `robust-labels.json` are
  digest sources; the other two are not (they record scheduler logs and the live meter ledger, see tier C), and their
  design/V/evaluate digests are compared by `joint:receipt-identities`.

## Tolerances

| comparison | rule |
|---|---|
| same producer, same interpreter | bitwise expected; `REPRODUCED_WITHIN_TOLERANCE` admits relative 1e-12 (BLAS or summation order); anything larger is `MISMATCH` |
| one total computed by two committed producers (flux-fix receipts vs `gen5d_to_rootpreds` arithmetic) | relative 1e-12 (measured at most 4e-16) |
| ROOT histograms | contents, errors (including under/overflow) and edges bitwise. The file bytes differ, because ROOT embeds a creation time and UUID |
| `np.savez` products (V, D) | arrays bitwise. The archive bytes carry write times |
| logs | exact line equality after dropping ROOT `Info`/`Warning` lines and the capture's `[stderr]` separator, with this run's directory written as the recorded one |
| PDFs | bitwise, else bitwise after blanking `/CreationDate`, `/ModDate`, `/ID` and XMP dates |
| joint evaluator and label outputs (tier D) | same producer: every leaf equal, `REPRODUCED_WITHIN_TOLERANCE` at relative 1e-12; the report also says whether the replayed file is bitwise the committed one. Paths are re-rooted; in a relocated run the design digest is the re-rooted design copy's. The label step reads the replayed evaluator output, so its recorded input path and digest are this run's |
| joint identities and counts (tier D) | exact |

## Declared differences (measured, still reported)

- **Envelope checkpoints.** The receipt's `bias_sources.d1`/`d2` digests are those of two running-trace
  checkpoints (`runs/s2/conv/k_b0_{gibuu,w1}.npz.partial.npz`), which were modified after the receipt. The
  envelope reads only iteration 5, and its linearity blocks regenerate exactly from the later files. Only the
  recorded digests differ.
- **`run_gen5d_supplement.sh`.** `gen5d-fluxfix-2.json` records an earlier version of this script for the
  supplement flux file (`supplement_flux.code`). That version is in no commit. The flux file itself matches.
- **`s5p_pairdiff.py`.** The four 4-pair F4 JSONs (`D-*.json`) were written by the committed `66cf3129` version. The
  checkout's later version regenerates their arrays and statistics bitwise.

These are exactly seven rows: three tier-A digests, two tier-A producer identities, and two tier-B envelope
blocks. `scope.py` declares each one by its recorded **and** its observed digest. Any other value, including
new bytes or a digest that starts to match, is a `MISMATCH`. An older committed blob with the recorded digest is
reported as context, and is never a declaration.

## What remains untested

Tier C, as listed by `list`:

- the <50 GeV flux reweight and the 50–100 GeV supplements, both from events (producers hardcode the campaign's
  output root);
- the per-mode files and the σ-weighted `mode_decomp_eavail` run that makes the note's `mode_decomp_eavail.pdf`
  (the producer writes only to the campaign's stage-7 directory). Its stored outputs and log are digest-checked,
  and `compare_mec_eavail` is regenerated from those outputs;
- the generator event samples;
- the production unfolds behind F2/F4/M1, V, devpower and the envelope;
- `paper_eavailW_generators.pdf` (`pdfcrop` is absent on Perlmutter; the committed file is digest-pinned);
- the joint seed-state classification (a classification of the Slurm task logs; tier D checks the committed copy
  against its original's digest);
- the missing-seed sensitivity (its recorded meter-ledger input has since been appended to; the committed output is
  pinned and its producer's identity checked).

Also untested: other interpreters or numpy builds. The relocation checks' results are recorded in the handoffs.

## The final joint result (tier D)

Tier D was made final on 2026-10-06
([`HANDOFF-20261006-s5p-reproduction-tier-d.md`](../../docs/orchestration/HANDOFF-20261006-s5p-reproduction-tier-d.md)).
It reads the four committed joint outputs, the five `s5p:runs/prod/status/<null>-final.json`, the pinned
calibration/power products through the frozen design's globs, and `joint.independent_compare`. Its rows:

1. `joint:receipt-identities`: every joint receipt and status file names the frozen design (`404446eb…`), V
   (`35979ef7…`) and the committed evaluator output (`b9604502…`) where it records one; each null's final B equals
   the evaluated B and the number of pinned calibration products; each power set's n equals its pinned products;
2. `joint:seed-states-copy`: the committed copy, with its log prefix removed, hashes to the original's recorded
   `6823e701…`;
3. `joint:frozen-module:*`: `s5p_joint.py`, `s5p_inference.py`, `s5p_seqstop.py` are the `4f5a613f` blobs;
4. `joint:replay` and `joint:replay-labels`: `s5p_joint.py evaluate` and `s5p_robust_labels.py` from the checkout
   into `out_dir/joint/`, compared with the committed files; `joint:module:*`: every project module they imported
   is the blob of the evaluation deploy `e9372b75`;
5. `joint:independent-verification`: the configured report recorded by digest, `INFO` when it is the cited report
   and `MISMATCH` otherwise. Its verdict is not read;
6. `joint:figures`: `PENDING`. There are no joint-result figures yet, because the note's Stage-7 text is not
   written. When they exist, add each figure to `scope.RECEIPTS` and its producer to `FIGURE_RUNS` (they will be
   regenerated in tier B), set `JOINT["figures"]`, drop `joint:figures` from `D_NON_GRADES`, move `SOURCE_COMMIT`,
   and re-run from a fresh clone.

Neither this harness nor its exit code grades the joint result: a reproduced replay shows the committed outputs
were computed by the committed code from the pinned products, not that the inference is adequate.
