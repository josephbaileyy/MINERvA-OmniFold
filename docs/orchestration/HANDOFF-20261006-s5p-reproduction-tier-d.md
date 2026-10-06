# s5p reproduction harness, tier D (the final joint result): fresh-checkout handoff (2026-10-06)

Successor to [`HANDOFF-20260928-s5p-reproduction-harness.md`](HANDOFF-20260928-s5p-reproduction-harness.md), following
its "Steps to incorporate the final joint result" and `reproduction/s5p/README.md` "The final joint result (tier D)".

**CITABLE FOR:**
- what tier D of the harness at `reproduction/s5p/` checks;
- that, from a fresh clone of `3a80aa74`, the frozen evaluator (`s5p_joint.py evaluate`) replayed on the lane-pinned
  calibration and power products **bitwise** reproduces the committed `joint-evaluate.json` (`b9604502…`) at the
  recorded roots, and reproduces every leaf (relative tolerance 1e-12; observed: no difference) on a relocated,
  traced copy of the inputs;
- that the label step (`s5p_robust_labels.py`) run on that replay reproduces the committed `robust-labels.json`;
- the exact commands, the outcomes per tier, and the digests below.

**NOT CITABLE FOR:**
- **Any physics result, grade, adoption or release**, and no statement about the joint result's correctness or
  adequacy. A reproduced replay shows that the committed outputs were computed by the committed, frozen code from the
  pinned products. It does not show the inference is right, and it is not independent: it re-runs the same code.
- **The independent verification.** Tier D records the extended comparer's report by digest and checks only that it
  is the report `RECORD-20261005-s5p-joint-5d-inference-result.md` §4 cites. Its verdict is not read or graded here.
- **The missing-seed sensitivity or the seed states.** Neither is replayed (tier C, below). The report-only lost-seed
  recovery is not an input of the frozen joint result and is outside every glob.
- **Joint-result figures.** None exists yet; nothing about them is reproduced.

## Status

| | status |
|---|---|
| **This bounded task** (tier D wired, pins measured, fresh-clone recorded-root and relocated runs, reports committed) | **COMPLETE** on branch `s5p-stage7-reproduction-20261006`. **Not merged into `main`**: that is the owner's integration step. |
| **Joint-result figures** | **PENDING.** The note's Stage-7 text is not written, so there is no figure and no producer. `FIGURE_RUNS` has no joint entry; tier D reports `joint:figures` as `PENDING`. |
| **The s5p campaign (`OI-193`)** | Not changed by this task. Read its own records. |

## What changed (branch `s5p-stage7-reproduction-20261006`, from `origin/main` `2fb6f035`)

- `reproduction/s5p/scope.py`
  - `SOURCE_COMMIT` moves `12991771` → `2fb6f0353fbc2908cb01bac5f8bf67bacac1f16a`. That commit carries the 2026-09-28
    receipts unchanged and the four joint outputs committed in `0afd9ef5`.
  - `RECEIPTS` adds the four committed joint outputs:
    - `joint-evaluate.json` `b9604502…`
    - `robust-labels.json` `206655f9…`
    - `missing-sensitivity.json` `f48e16ef…`
    - `seed-states.abs-log-paths.json` `bd25f1ec…`
  - Digest sources. The first two are digest sources. Through `robust-labels.json` that adds the cluster file
    `s5p:stage7/joint/joint-evaluate.json`, which is re-measured and staged. The last two are pinned only
    (`NOT_DIGEST_SOURCES`, with the reason in the file).
  - `PRODUCER_FILES` / `PRODUCER_SHA_FIELDS` add `s5p_robust_labels.py` and `s5p_missing_sensitivity.py`, checked
    against the `code_sha256` their outputs record. The 2026-09-28 handoff asked for the first.
  - `UNRECORDED_INPUT_GLOBS` adds three groups, taken from the frozen design's own globs (a unit test checks that):
    - the five calibration ensembles;
    - the six power ensembles;
    - the five `runs/prod/status/<null>-final.json`.

    No group reaches `s5p:recovery/`.
  - `NOT_REGENERATED` adds `joint-seed-states` and `joint-missing-sensitivity`.
  - `JOINT` gains the evaluation deploy `e9372b75`, the frozen modules, the evaluation's thread settings (4/4/4), the
    cited report digest `97e1666a…`, and `figures: {}`.
- `reproduction/s5p/repro_s5p.py`
  - Tier D is rewritten (rows below).
  - `pin --extend OLD` copies `OLD`'s groups verbatim, each keeping its measurement time, and measures only the rest.
  - The exit code now requires tier D (see "Exit-code change").
  - The coverage row also counts tier-D comparisons.
- `reproduction/s5p/pins/unrecorded-inputs-20261006.json`. Made by `pin --extend pins/unrecorded-inputs-20260928.json`
  on login04 at 2026-10-06T05:47:49Z, from a fresh clone of `da1ffb50`:
  - the six 2026-09-28 groups (401 files) are copied verbatim and keep their 21:56Z 2026-09-28 time;
  - measured: 7176 calibration products, 1147 power products and 5 status files.
- `reproduction/s5p/config.example.json`: `joint.independent_compare` now points at
  `/pscratch/sd/j/josephrb/s5p-parallel-recompute/final-ext/compare.json`. The old default, `final/compare.json`
  (`4cd73439…`), reads `verdict: INCOMPLETE` (measured 2026-10-06).
- `reproduction/s5p/tests/test_repro_s5p.py`: 28 → 36 tests. Each new guard is exercised in both directions:
  - pending only without the committed result; `INPUT_MISSING` and never exit 0 without the products;
  - receipt identities fire on a wrong count and on a status B that differs from the evaluated B;
  - the seed-states copy reverts to the recorded original, and fires on a wrong prefix;
  - the independent report gives `INFO` on the cited digest, `MISMATCH` on any other and `INPUT_MISSING` when absent,
    and its verdict field is never read;
  - `pin --extend` copies verbatim, measures only new groups, and refuses an extension or a stale group;
  - the joint groups equal the design's globs and exclude the recovery;
  - the committed pins extend the 2026-09-28 file verbatim, and their counts equal the evaluated B and n;
  - the exit codes.
- `reproduction/s5p/README.md`: rewritten for tier D.
- `reproduction/s5p/reports/{fresh,reloc}-3a80aa74/`: the reports.

Commits: `da1ffb50` (code), `bc80806b` (pins, README, config), `3a80aa74` (the two replayed scripts also get a
deploy-identity row; a dev run at `bc80806b` showed they were absent from the import record because they run as
`__main__`). The reports' commit and this file follow.

## Tier D rows (identical in both runs)

| row | what it compares | outcome |
|---|---|---|
| `joint:receipt-identities` | 44 exact comparisons:<br>• the design `404446eb…`, V `35979ef7…` and evaluate `b9604502…` digests in the four joint receipts and five status files;<br>• `stop` in each status file;<br>• each null's status B = evaluated B (total and shape) = number of pinned calibration products;<br>• each power set's evaluated n = number of pinned power products | REPRODUCED |
| `joint:seed-states-copy` | the committed copy, with its 1462 log prefixes removed, against `seed_states_sha256` `6823e701…` | REPRODUCED |
| `joint:frozen-module:*` (3) | `s5p_joint.py`, `s5p_inference.py` and `s5p_seqstop.py` against their `4f5a613f` blobs | REPRODUCED |
| `joint:replay` | `s5p_joint.py evaluate` from the checkout (OMP/OPENBLAS/MKL threads 4) against the committed `joint-evaluate.json`, at 1e-12 | REPRODUCED. Recorded roots: **bitwise**, sha256 `b9604502…`. Relocated: every leaf equal; not bitwise, as expected, because paths are re-rooted and the design digest is the re-rooted copy's |
| `joint:replay-labels` | `s5p_robust_labels.py` on the replayed output against the committed `robust-labels.json`. The input path and digest are this run's | REPRODUCED |
| `joint:module:*` (4) | `s5p_joint.py`, `s5p_robust_labels.py`, `s5p_inference.py` and `s5p_stage1_inspect.py` against their blobs in the evaluation deploy `e9372b75` | REPRODUCED |
| `joint:independent-verification` | the configured report's sha256 against the cited `97e1666a7e5722b08fb7754653bbf2d273e14e74b966f1c1049fdc84fc3f09ec` | INFO: recorded, not graded |
| `joint:figures` | none exists | PENDING |

Tier A also checks the producer identities of `s5p_robust_labels.py` (`e08b7608…`) and `s5p_missing_sensitivity.py`
(`34768e47…`), and the receipt-recorded digest of the cluster `stage7/joint/joint-evaluate.json` (`b9604502…`). All
three are REPRODUCED.

## Results

**Environment:** Perlmutter login33; root_6_28 activated by prefix; Python 3.11.14, numpy 1.26.4, ROOT 6.28/12.
Fresh clone `/pscratch/sd/j/josephrb/s5p-parallel-reproduction/fresh-3a80aa74` at
`3a80aa74ff2aedf905f1ce620973fd40e7684406`. `git status --porcelain` was empty before and after every run.

**Unit tests:** `Ran 36 tests in 7.771s` / `OK`, on the cluster from the fresh clone. Locally (macOS, Python 3.12.2):
`Ran 36 tests` / `OK`.

| run | exit | rows | wall time | report digests |
|---|---:|---:|---:|---|
| recorded roots (`fresh-3a80aa74`) | **0** | 9311 | 244 s | `report.json` `4e40bc6c4118df7f…`; `report.md` `e9d301b86d796880…` |
| relocated, traced (`reloc-3a80aa74`) | **0** | 9311, the same checks; 0 statuses differ | 308 s | `report.json` `bbb8a6074f796c62…`; `report.md` `fd1a7a9343765a77…` |

Counts by tier and basis are identical in both runs:

| tier and basis | REPRODUCED | WITHIN_TOL | DECLARED | other |
|---|---:|---:|---:|---|
| A: committed file vs scope pin | 56 | | | |
| A: receipt-recorded digest | 378 | | 3 | |
| A: receipt-recorded digest, bytes from git history | 3 | | | |
| A: code identity vs recorded code | 18 | | 2 | |
| A: recomputed from preserved products | 32 | 3 | | |
| A: coverage of the receipts' recorded digests | 1 | | | |
| A: lane-pinned digest (NOT historical provenance) | 8738 (8729 files + 9 population rows) | | | |
| B: regenerated by the checkout's producer | 47 | | 2 | |
| B: code identity | 7 | | | |
| C: not run | | | | 8 `NOT_RUN` |
| D: final joint result slot | 3 | | | 1 `INFO`, 1 `PENDING` |
| D: code identity | 7 | | | |
| D: recomputed (seed-states copy) | 1 | | | |

There are no failures, errors or missing inputs. The seven declared differences are the 2026-09-28 seven,
unchanged. The three within-tolerance rows are the same `_full` integrated-σ rows as before.

**Relocation.**
- `stage` copied the declared inventory into `/pscratch/sd/j/josephrb/s5p-parallel-reproduction/staging-3a80aa74`:
  9095 files, 6,788,043,772 B, in 107 s. The 3 files absent at source are the removed deploy copies, read from git as
  before. `staging-manifest.json` is `e64b418982360aa2…`.
- The `strace -f --seccomp-bpf -e trace=%file` trace has 1,010,058 lines and 37,619 accesses under the staging tree.
  **0 paths under any recorded root were touched** (`trace-scan.json` `bd9e5aa1b172cea0…`).
- The trace stays on scratch: `/pscratch/sd/j/josephrb/s5p-parallel-reproduction/reloc-3a80aa74.strace`, sha256
  `1637ce356a97bd5a…`, 129,112,039 B.
- No input was missing, so the inventory is complete for tier D too.

**Negative control (tier D).** `run --tiers D` with `joint.independent_compare` pointed at the earlier
`final/compare.json` (`4cd73439…`, INCOMPLETE) exits **1**: `joint:independent-verification` is a `MISMATCH`, "not the
report … §4 cites". The report is `runs/control-wrong-report-3a80aa74/` on scratch.

**Digests of the committed reports** (`reproduction/s5p/reports/`):

| file | sha256 |
|---|---|
| `fresh-3a80aa74/report.json` | `4e40bc6c4118df7fae5f7ec7202f91a517b08a974acfae00d948da586ccab3c4` |
| `fresh-3a80aa74/report.md` | `e9d301b86d796880287f3d41ec42f2e8d0ec419aaec604fc9f87f7dafe6ece2d` |
| `fresh-3a80aa74/unittest-output.txt` | `0115ed8e515b5b37da8614cda9d4ff73280f134ccceb4b50a6540a559fd5662e` |
| `reloc-3a80aa74/report.json` | `bbb8a6074f796c6258a150c31ef12d18f92c9c44ae5000c55c90686c53eb9c29` |
| `reloc-3a80aa74/report.md` | `fd1a7a9343765a770572d50b6b191007e4b5b9482f6e5e9c46bf2c0380928877` |
| `reloc-3a80aa74/staging-manifest.json` | `e64b418982360aa2a0dae8a73170224573f4316b2441bf2dbf55a43b0bb98ed8` |
| `reloc-3a80aa74/trace-scan.json` | `bd9e5aa1b172cea02cddab231c7852a763af8062b7e8af052147bab55d9fd363` |
| `pins/unrecorded-inputs-20261006.json` | `7ed86877ffeadb1a44427f333fbb7304731c0a73dd16174d0336c4b575d522d4` |

Each report digest was re-computed on the copy and equals the cluster file's.

## Exit-code change

Exit 0 now requires all of the following:
- tiers A, B **and D** ran;
- every A/B row passed;
- `joint:replay` reproduced;
- every other D row passed, or is one of the two declared non-grades: `joint:independent-verification` `INFO` and
  `joint:figures` `PENDING`.

A D row with missing inputs gives exit 2, and any `MISMATCH`/`ERROR` gives exit 1. The 2026-09-28 pins file alone
now fails the tier-D pin-population rows: use `pins/unrecorded-inputs-20261006.json` (`scope.PINS_FILE`).

## Not reproduced (tier C additions, with the measured reason)

- **`joint-seed-states`** (`s5p:stage7/joint/seed-states.json`). It is a classification of the Slurm task logs, not
  a computation from products. Tier D checks only the committed copy's transformation back to `6823e701…`.
- **`joint-missing-sensitivity`.** Its recorded input, the meter ledger `s5p:ledger/admissions.jsonl` at `7056145f…`,
  no longer exists: measured 2026-10-06, the file hashes `52b4da9f…` with mtime 2026-10-06T02:48:57Z, after the
  2026-10-05T20:37Z sensitivity output. The committed output is pinned and its producer's identity is checked.

## Exact commands

The lane's scripts are on scratch, outside the repository, so they are reproduced here.

```bash
W=/pscratch/sd/j/josephrb/s5p-parallel-reproduction
git clone https://github.com/josephbaileyy/MINERvA-OmniFold.git $W/fresh-3a80aa74 && cd $W/fresh-3a80aa74 \
  && git checkout 3a80aa74ff2aedf905f1ce620973fd40e7684406
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"; export TMPDIR=$SCRATCH/tmp   # not setup_salloc_env.sh; no `set -u`
P=reproduction/s5p/pins/unrecorded-inputs-20261006.json
python3 -m unittest discover -s reproduction/s5p/tests
sed "s#runs/CHANGE-ME#runs/fresh-3a80aa74#" reproduction/s5p/config.example.json > $W/config-fresh-3a80aa74.json
python3 reproduction/s5p/repro_s5p.py run --config $W/config-fresh-3a80aa74.json --pins $P        # recorded roots
python3 reproduction/s5p/repro_s5p.py stage --config $W/config-stagesrc-reloc-3a80aa74.json --pins $P \
    --to $W/staging-3a80aa74                                                                       # recorded roots in
# config-reloc-3a80aa74.json: roots = $W/staging-3a80aa74/{s5p,analysis,s5e,cvmfs}, out_dir = $W/runs/reloc-3a80aa74
strace -f --seccomp-bpf -e trace=%file -o $W/reloc-3a80aa74.strace \
    python3 reproduction/s5p/repro_s5p.py run --config $W/config-reloc-3a80aa74.json --pins $P
python3 reproduction/s5p/repro_s5p.py scan-trace --trace $W/reloc-3a80aa74.strace --expect-prefix $W/staging-3a80aa74
```

- **The pins:** `python3 reproduction/s5p/repro_s5p.py pin --config <recorded roots> --out $W/pins/unrecorded-inputs-20261006.json --extend reproduction/s5p/pins/unrecorded-inputs-20260928.json`,
  from a fresh clone of `da1ffb50` (`$W/pin-da1ffb50`). It took 112 s.
- **Where it all ran:** login nodes only (login04, login33). **No Slurm job was submitted and no allocation was used.**

## Footprint

- **Scratch, `/pscratch/sd/j/josephrb/s5p-parallel-reproduction/` only:**
  - clones `pin-da1ffb50`, `dev-bc80806b` (a pre-check run, exit 0) and `fresh-3a80aa74`;
  - `staging-3a80aa74` (6.4 GB, a copy of the preserved inputs);
  - `runs/{dev-bc80806b,fresh-3a80aa74,reloc-3a80aa74,control-wrong-report-3a80aa74}`;
  - `pins/unrecorded-inputs-20261006.json`, the trace, the configs, and the lane scripts `lane-{pin,run,run-reloc,post}.sh`.

  Scratch is purgeable, so the committed reports are the durable record.
- **Nothing was written** to `s5p-20260926/` (deploy, runs, status, recovery), `state/s5p/`, or any other branch or
  worktree. The traced relocated run verifies this for the harness itself.

## What remains

1. **The joint-result figures**, once the note's Stage-7 text exists. Then:
   - add each figure to `scope.RECEIPTS` and its producer to `FIGURE_RUNS` (tier B regenerates it);
   - set `JOINT["figures"]`, and remove `joint:figures` from `D_NON_GRADES` in `repro_s5p.py`;
   - move `SOURCE_COMMIT` to the commit that carries them;
   - re-run both runs from a fresh clone, and commit the reports beside these.
2. **Integration of this branch into `main`.** That is the owner's step, and it is not done here.
3. Optional, not owed: a replay of the missing-seed sensitivity would need the ledger at `7056145f…`, which no longer
   exists on scratch.
