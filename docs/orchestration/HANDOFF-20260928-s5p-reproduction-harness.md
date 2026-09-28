# s5p reproduction harness: fresh-checkout handoff (2026-09-28)

**CITABLE FOR:** what the harness at `reproduction/s5p/` reproduces from a fresh checkout, what it cannot, the
exact commands, and the route for adding the final joint result. This is task 3 of
[`HANDOFF-20260928-s5p-parallel-tasks.md`](HANDOFF-20260928-s5p-parallel-tasks.md).
**NOT CITABLE FOR:** any physics result, grade, adoption, release, or anything about the joint test. Agreement
shows that the committed calculation was re-executed faithfully. It does not show that the calculation is
scientifically adequate. Expected values live in the receipts the harness reads, never in this file.

## Two statuses, never to be merged

| | status |
|---|---|
| **This bounded preparation** (harness, fresh-checkout test, durable route for the joint result) | **COMPLETE** at the commit that carries this file, on branch `s5p-parallel-reproduction-20260928` (not merged) |
| **The s5p campaign (`OI-193`)** | **NOT complete.** Production is still writing: at 15:10 PDT 2026-09-28, `find` showed files newer than 14:45 PDT under `s5p:runs/prod/cal/*` and `s5p:runs/prod/pow/P1_a1.0`. No terminal joint product exists. The final joint-result reproduction is **PENDING** until independently verified terminal products exist. |

## Tested source

- **Harness commit `888dae697e5dfaf4e0d3f50a5a87a5daf562b656`** (branch `s5p-parallel-reproduction-20260928`,
  parent `129917715b2c`, the `origin/main` of 2026-09-28). The scope is written against the receipts at
  `12991771` (`scope.SOURCE_COMMIT`). The frozen admission is `4f5a613f`, and the frozen design sha256 is
  `404446eb…` at both commits.
- **Fresh clone:** `git clone https://github.com/josephbaileyy/MINERvA-OmniFold.git`, checked out at `888dae69`
  into `/pscratch/sd/j/josephrb/s5p-parallel-reproduction/fresh-888dae69`. `git status --porcelain` was empty
  before and after the run.
- **Environment:** Perlmutter `login07`; root_6_28 activated by prefix; Python 3.11.14, numpy 1.26.4, ROOT
  6.28/12, matplotlib 3.10.8. These are the interpreter and versions the production receipts record.
- **Result:** unit tests 17/17 OK. `run` exited **0** after 128 s wall time (login node, no Slurm). The report is
  committed at [`reproduction/s5p/reports/fresh-888dae69/`](../../reproduction/s5p/reports/fresh-888dae69/):
  `report.json` sha256 `e827a945…`, `report.md` `de523e12…`, `unittest-output.txt` (the run's `fresh-unittest.log`) `26a728bd…`. The unit tests also
  pass from a second fresh clone on macOS (Python 3.12.2, numpy 1.26.4); the products are not reachable there.
- **Negative control on real inputs:** one pin corrupted (the 3D unfold's digest). Tier A then exited **1**,
  with exactly one `MISMATCH` on that file.

| tier | REPRODUCED | WITHIN_TOL | DECLARED_DIFFERENCE | other |
|---|---:|---:|---:|---|
| A replay | 880 | 3 | 5 | 0 mismatch, 0 missing |
| B regenerate | 54 | 0 | 2 | 0 mismatch, 0 missing; no producer imported code outside the checkout (35 launches) |
| C full regeneration | | | | 6 `NOT_RUN` |
| D joint | | | | 1 `PENDING` |

## What reproduced

**Replay (tier A), from preserved bytes:**

- The 52 committed receipts, logs, designs and note figures equal their pins.
- All 382 distinct `(path, sha256)` pairs recorded by the 37 in-scope JSON receipts reproduce, apart from the 3
  declared differences below. This includes the flux-repaired 5D predictions and their input identities
  (pre-fix products, `phi_t`, GENIE graphs, cvmfs flux files, supplement events and flux) and the stored ROOT
  prediction and mode files.
- The producers match the code that ran.
- The integrated σ of every repaired prediction agrees with the generator-context sidecars exactly, and with the
  flux-fix receipts to at most 4e-16 relative.
- The F2/F4/M1 summary statistics and V's receipt fields match exactly.
- All 401 lane-pinned unrecorded inputs match their pins.

**Regeneration (tier B), from the fresh checkout on the preserved inputs:**

- `gen5d_to_rootpreds.py`: all 8 prediction ROOT files, every histogram bitwise.
- The six figure runs, with logs equal line for line and PDFs bitwise except creation date and ID:
  `eavailW_band` (VL156–VL158), `generators_vs_unfolded_band` (VL159), `compare_3d_fullcov`,
  `compare_mec_eavail` (VL160), `compare_mec_eavail_before`, `mode_decomp_eavail_before`. The four PDFs among
  them are the note's `eavailW_band`, `generators_vs_unfolded_band`, `compare_3d_fullcov` and
  `compare_mec_eavail`.
- `s5p_pairdiff.py`: all 17 F2/F4/M1 products, arrays bitwise.
- `s5p_prefreeze.py units` and `devpower`: `result` exactly.
- `s5p_joint.py build-v`: V bitwise.
- `s5p_envelope.py`: every block exactly, apart from 2 declared recorded digests.

## Findings a later session needs

1. **The figures' scratch export is gone.** `s5p:deploy/4e4b4f56` no longer exists; `deploy/` holds only
   `4f5a613f` and `55a41765`. The figure producers' recorded digests equal the git blobs at `4e4b4f56`, so the
   harness checks them there, and the report row says so. A fresh clone therefore needs full history (not
   `--depth 1`).
2. **The envelope receipt's d1/d2 bias sources were running-trace checkpoints**
   (`runs/s2/conv/k_b0_{gibuu,w1}.npz.partial.npz`). They were modified after the receipt (mtimes 02:12 and
   02:32 PDT 2026-09-27; receipt committed `66cf3129` at 01:24). Their recorded digests no longer hold. The
   envelope reads only iteration 5, and its **linearity blocks regenerate exactly** from the later files. An
   earlier draft of `scope.py` said these blocks "cannot be replayed". The measurement refuted that before
   commit, and the committed text is the measured one.
3. **`gen5d-fluxfix-2.json` records two digests for `run_gen5d_supplement.sh`.** The earlier one
   (`supplement_flux.code`, `6b925371…`) is in no commit. The README says the supplement flux file "was written
   once, by an earlier version of the script". The flux file itself matches.
4. **The four 4-pair F4 `D-*.json` were written by the committed `66cf3129` version of `s5p_pairdiff.py`.** The
   later producer regenerates them bitwise. Code identity is reported separately from numerical agreement.
5. **Six groups of input (17 globs, 401 files) have no producer-recorded digest.** They are listed in
   `scope.UNRECORDED_INPUT_GLOBS` (untracked figure data in the canonical analysis checkout, lateral endpoints,
   data jitters, V ensemble, power pilot, M1 mid asimovs, s5e W2, MnvTune 5D). The committed lane pins
   (`pins/unrecorded-inputs-20260928.json`) prove only constancy since 21:56Z 2026-09-28. What ties them to
   production is tier B's bitwise regeneration of the committed outputs.
6. **An unattributed observation, recorded without inference.** `s5p:deploy/4f5a613f/.git` has directory mtime
   15:09:28 PDT, about 8 s after the fresh run's last write, and no file inside it is newer. No code in the
   harness references that directory.

## Not reproduced here (tier C, and why)

- the <50 GeV flux reweight and the 50–100 GeV supplements from events (event generation; the producers hardcode
  `S5P`/`REPO`);
- the per-mode files and the σ-weighted `mode_decomp_eavail` run behind the note's `mode_decomp_eavail.pdf`
  (`gen5d_mode_components.py` writes only to the campaign's stage-7 directory). Its outputs and log are
  digest-checked;
- the generator event samples;
- every production unfold behind F2/F4/M1, V, devpower and the envelope;
- `paper_eavailW_generators.pdf` (`pdfcrop` is absent on Perlmutter; the committed file is digest-pinned).

Also untested: relocated roots end to end (only unit-tested), other interpreters or numpy builds, and the joint
result. Making the mode files regenerable needs an output-directory option on `gen5d_mode_components.py`. That
is a producer change and was not made here.

## Exact commands

```bash
W=/pscratch/sd/j/josephrb/s5p-parallel-reproduction
git clone https://github.com/josephbaileyy/MINERvA-OmniFold.git $W/fresh-<sha> && cd $W/fresh-<sha> && git checkout <sha>
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"; export TMPDIR=$SCRATCH/tmp      # not setup_salloc_env.sh
python3 -m unittest discover -s reproduction/s5p/tests
# a config: config.example.json with out_dir set to a NEW directory, e.g. $W/runs/fresh-<sha>
python3 reproduction/s5p/repro_s5p.py run --config $W/config-fresh.json \
    --pins reproduction/s5p/pins/unrecorded-inputs-20260928.json
```

Do not use `set -u` in the calling shell. The root_6_28 activation script references unset variables
(`ADDR2LINE`) and aborts. The scope, tolerances and the full not-run list are in
[`reproduction/s5p/README.md`](../../reproduction/s5p/README.md) and `repro_s5p.py list`.

## Steps to incorporate the final joint result

Tier D is already wired (`repro_s5p.py tier_d`). It reports `PENDING` until
`state/s5p/stage7/joint/joint-evaluate.json` is committed and all five `s5p:runs/prod/status/<null>-final.json`
exist. Once the campaign is terminal (see the parallel-tasks handoff §1):

1. Wait for the campaign's committed `joint-evaluate.json` and for the independent recomputation's report. Task 1
   is branch `s5p-parallel-recompute-20260928`; its lane states the output route
   `/pscratch/sd/j/josephrb/s5p-parallel-recompute/final/{recompute.json,compare.json}`, which is the config
   default for `joint.independent_compare`.
2. On a new branch from that `origin/main`, add the joint receipt(s) and the note/primer/paper joint figures to
   `scope.RECEIPTS`. Add the calibration and power products either to `DIGEST_SOURCES` (if the campaign's
   receipt records their digests) or to `UNRECORDED_INPUT_GLOBS` plus a new `pin`. Add each joint figure's
   producer to `FIGURE_RUNS`. Move `SOURCE_COMMIT`.
3. From a fresh clone, run `run`. Tier D then checks the design/V pins (`404446eb…`/`35979ef7…`), replays
   `s5p_joint.py evaluate` into the output directory, compares it with the committed file at 1e-12, and records
   the independent report by digest. The harness does not grade that report.
4. Commit the report beside this one, and write a successor to this handoff.

Until then, nothing here is evidence about the joint result.

## Coordination and footprint

- The lanes were declared to the note-sync session (branch `note-sync-s5p-20260928`) and the recomputation session
  (branch `s5p-parallel-recompute-20260928`). Neither touches `reproduction/s5p/**` or this file.
- All three branches add neighbouring rows to `CATALOG.md` / `MANIFEST-overrides.tsv` and regenerate
  `MANIFEST.tsv`. Whichever merges later should rebase and regenerate rather than hand-merge.
- No Slurm job was submitted. Nothing was written to `../MINERvA-OmniFold-s5p`, `state/s5p/`, or
  `/pscratch/sd/j/josephrb/s5p-20260926/`.
- Cluster outputs are only under `/pscratch/sd/j/josephrb/s5p-parallel-reproduction/`: `dev/`, a scratch
  clone with the harness copied in, used for development runs `runs/dev1`, `runs/dev2`; `fresh-888dae69/`;
  `runs/fresh-888dae69/`; `runs/control-corrupt-pin/`; and the pins, configs and logs. Scratch is purgeable,
  so the committed report copy is the durable record.
