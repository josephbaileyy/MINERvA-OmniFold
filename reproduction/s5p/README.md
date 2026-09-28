# s5p reproduction harness

**CITABLE FOR:** how to reproduce, from a fresh checkout, the already-final s5p components: the flux-repaired
generator predictions and their input identities, the deliverable generator figures and numbers built from them
(`VALIDATION_LEDGER.md` VL156–VL160), and the pre-freeze quantities of the joint-test design. It also records which
of these reproduce, and to what tolerance.
**NOT CITABLE FOR:** any physics result, grade, adoption or release. Agreement shows that the committed
calculation was re-executed faithfully. It does not show that the calculation is scientifically adequate.
The final joint result is **not** reproduced here. It is a declared slot (tier D) that stays `PENDING`.

The scope is declared as data in [`scope.py`](scope.py): pinned receipts, recorded roots, tolerances, figure
runs, declared differences, and the not-run tier. The engine is [`repro_s5p.py`](repro_s5p.py). Every expected
value is read from the committed receipts, never from this README.

## Tiers (separate claims; the report never merges them)

| tier | what it does | runs here |
|---|---|---|
| **A replay** | Pins the 52 committed receipts, logs, designs and figures. Re-measures every digest the 37 JSON receipts record, on the preserved bytes. Compares the checkout's producers with the code that ran. Recomputes the committed numbers from stored products: integrated σ of every 5D prediction; F2/F4/M1 summary statistics; V's fields. Checks the 401 lane-pinned inputs no receipt digests. | numpy only |
| **B regenerate** | Re-runs the committed producers from **this checkout** into a fresh directory, on the preserved inputs, and compares: `gen5d_to_rootpreds.py` (8 prediction ROOT files, all histograms bitwise); the six figure runs (logs exactly, PDFs bitwise except creation date and document ID); `s5p_pairdiff.py` (17 F2/F4/M1 pair differences, arrays bitwise); `s5p_prefreeze.py units`/`devpower`; `s5p_joint.py build-v` (V bitwise); `s5p_envelope.py`. Each producer runs through [`_launch.py`](_launch.py), which refuses a run that imported project code from outside the checkout (OI-136). | needs PyROOT (root_6_28) |
| **C not regenerated** | Full scientific regeneration: event generation, the flux reweight from events, the per-mode files, and the production unfolds. Each item is listed with its dependency and reported `NOT_RUN`. | never |
| **D joint** | The final joint result. `PENDING` until its terminal products exist; see "Adding the final joint result". | when terminal |

## Commands (Perlmutter login node, about 2–3 min)

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
    --pins reproduction/s5p/pins/unrecorded-inputs-20260928.json
```

`run` writes `report.json`, `report.md`, the regenerated products, the logs and the per-producer import
provenance under `out_dir`. Its exit code is 0 when every tier-A/B check reproduced (a `DECLARED_DIFFERENCE`
counts as reproduced), 1 on any `MISMATCH`, and 2 when an input or the environment is missing. A `PENDING` or
`NOT_RUN` never counts as reproduced.

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
- **`joint.independent_compare`**: the independent recomputation lane's report route.

Re-rooting onto other locations is implemented and unit-tested. It is **not** tested end to end: every recorded
run used the recorded locations.

## Required artifacts and their identities

- **Committed** (pinned in `scope.RECEIPTS`): the gen5d build and flux-fix receipts (rounds 1–3); the
  generator-context receipt, its 8 prediction sidecars, the E_avail ratios and the 7 logs; the F2/F4/M1 JSONs; the
  V, units, devpower and envelope receipts; the draft and frozen designs; the J-partition definitions; the six
  note figures.
- **Preserved on scratch, digest recorded by the campaign**: every `(path, sha256)` pair in those receipts (382
  distinct), including the flux-repaired 5D predictions, their inputs (pre-fix products, `phi_t`, GENIE graphs,
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

## Tolerances

| comparison | rule |
|---|---|
| same producer, same interpreter | bitwise expected; `REPRODUCED_WITHIN_TOLERANCE` admits relative 1e-12 (BLAS or summation order); anything larger is `MISMATCH` |
| one total computed by two committed producers (flux-fix receipts vs `gen5d_to_rootpreds` arithmetic) | relative 1e-12 (measured at most 4e-16) |
| ROOT histograms | contents, errors (including under/overflow) and edges bitwise. The file bytes differ, because ROOT embeds a creation time and UUID |
| `np.savez` products (V, D) | arrays bitwise. The archive bytes carry write times |
| logs | exact line equality after dropping ROOT `Info`/`Warning` lines and the capture's `[stderr]` separator, with this run's directory written as the recorded one |
| PDFs | bitwise, else bitwise after blanking `/CreationDate`, `/ModDate`, `/ID` and XMP dates |

## Declared differences (measured, still reported)

- **Envelope checkpoints.** The receipt's `bias_sources.d1`/`d2` digests are those of two running-trace
  checkpoints (`runs/s2/conv/k_b0_{gibuu,w1}.npz.partial.npz`), which were modified after the receipt. The
  envelope reads only iteration 5, and its linearity blocks regenerate exactly from the later files. Only the
  recorded digests differ.
- **`run_gen5d_supplement.sh`.** `gen5d-fluxfix-2.json` records an earlier version of this script for the
  supplement flux file (`supplement_flux.code`). That version is in no commit. The flux file itself matches.
- **`s5p_pairdiff.py`.** The four 4-pair F4 JSONs (`D-*.json`) were written by the committed `66cf3129` version. The
  checkout's later version regenerates their arrays and statistics bitwise.

## What remains untested

Tier C, as listed by `list`:

- the <50 GeV flux reweight and the 50–100 GeV supplements, both from events (producers hardcode the campaign's
  output root);
- the per-mode files and the σ-weighted `mode_decomp_eavail` run that makes the note's `mode_decomp_eavail.pdf`
  (the producer writes only to the campaign's stage-7 directory). Its stored outputs and log are digest-checked,
  and `compare_mec_eavail` is regenerated from those outputs;
- the generator event samples;
- the production unfolds behind F2/F4/M1, V, devpower and the envelope;
- `paper_eavailW_generators.pdf` (`pdfcrop` is absent on Perlmutter; the committed file is digest-pinned).

Also untested: re-rooted (relocated) inputs, other interpreters or numpy builds, and anything of the joint
result.

## Adding the final joint result (tier D)

Tier D already reads `docs/orchestration/state/s5p/stage7/joint/joint-evaluate.json`,
`s5p:runs/prod/status/<null>-final.json` for the five nulls, and `joint.independent_compare`. When all of them
exist, it:

1. checks that the committed result's `design_sha256`/`v_sha256` equal the frozen design (`404446eb…`) and V
   (`35979ef7…`);
2. replays `s5p_joint.py evaluate` from the checkout into `out_dir/joint/` and compares it with the committed file
   at the same-code tolerance;
3. records the independent lane's report by digest. The report is not graded here.

To make the slot final:

- add the joint receipt and its calibration/power product digests to `scope.RECEIPTS` / `DIGEST_SOURCES`;
- pin the calibration and power products (the campaign's own receipt should record them; otherwise
  `UNRECORDED_INPUT_GLOBS` plus a new `pin`);
- add the note/primer/paper joint figures to `FIGURE_RUNS` with their producers;
- move `SOURCE_COMMIT` to the commit that carries them, and re-run from a fresh clone.

Until then the joint result stays `PENDING`. Neither this harness nor its exit code is evidence about it.
