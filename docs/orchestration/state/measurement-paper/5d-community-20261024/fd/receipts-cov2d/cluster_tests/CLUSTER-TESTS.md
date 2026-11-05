# COV2D: the suites in the cluster environments (binding 2 ruling 5): 13 of 13 suite runs pass

**By** the `cov2d` session, 2026-11-05, with the director's GO for `connect-tests.sh` (sha256
`9895515aea1332d0bc124a9c6b41455ad6a151424ba8988365a6eca2c800f9a8`). The director ruled on two flags before the run:
RM's pinned MAT setup reads are allowed, and `test_cov2d`'s Receipt-class skips are accepted. **MEASURES:** the
COV2D suites at M, in the cluster's environments. **CANNOT AUTHORIZE:** any job. The G18 pseudo-data job's connect
goes to the director separately.

## The run

- **Commit:** a fresh clone of GitHub at **M = `cb31611ca8b96ed2d1eeb809fda7236e56645863`** (binding 2), with
  HEAD asserted. Its `2d-unfolding/cov2d` blob list is `logs/blobs.txt`. That list is identical to main at
  `30a1b6c0`, the merge of binding 2.
- **Node and time:** login02, `/dev/shm/josephrb-cov2d-tests`, 2026-11-05 10:12:52Z to 10:19:42Z.
- **Launch:** the sha was verified (DIGEST_MATCH) and the script launched in one invocation, under nice 19,
  `taskset -c 8-11`, with one thread per library.
- **0 node-h.**
- **Porcelain:** before, plain 0 and `--ignored` 0. After, plain 0 and `--ignored` 0.
- **Process:** each suite ran in its own process through a small runner (`unittest -v`), which prints a `SUITE` line
  with its counts and lists every skip.
- **Audit hook:** the runner records any `open`, `os.listdir`, `os.scandir`, `glob.glob` or `shutil.copyfile` of a
  `/pscratch` or `/global/cfs` path made by the suites. Before the run, a local positive control showed it catching a
  `/pscratch` open, a `/global/cfs` open and a `/pscratch` listdir. **It caught 0 in every run.**

## The environments

Each is named in `connect-tests.log.txt`, with its interpreter and versions.

| env | what | interpreter | Python | numpy | uproot | ROOT |
|---|---|---|---|---|---|---|
| P | omnifold_py310 | `/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python` | 3.10.19 | 2.2.6 | 5.6.9 | absent |
| R | root_6_28, activated by full prefix through the conda 24.10.0 hook; no MAT | `/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python` | 3.11.14 | 1.26.4 | absent | 6.28/12 |
| RM | root_6_28 + the pinned MAT environment | the same (what MAT's setup leaves on PATH, as in the jobs) | 3.11.14 | 1.26.4 | absent | 6.28/12 |

**RM's setup.**
1. `fd_rpd_inputs.run_check_mat_setup` checked the six MAT setup scripts at their pinned digests, through O_NOATIME,
   before any was sourced. It logged `{"mat_setup_scripts": 6, "mismatches": 0}`.
2. Then `$A/setup_salloc_env.sh` was sourced, with A = `/pscratch/sd/j/josephrb/MINERvA-OmniFold`.
3. `mat_environment` then logged libMAT.so mapped and the `PlotUtils::MnvH1D` dictionary present.

The pins are `fd_rpd_inputs.py` (blob `7c2e018f`, `MAT_SETUP`) at M. These are the only pscratch reads, and they are
environment setup, not data. The director allowed them.

| setup script (under `$A`) | pinned sha256 |
|---|---|
| `setup_salloc_env.sh` | `ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48` |
| `unbinned_unfolding/build/setup.sh` | `40ff3a3d0c0308a82d90fd6cb4858696931fa00563277e5865141f8ebdc84598` |
| `MINERvA101/opt/bin/setup.sh` | `e22a5b93d327111bf6ffc80f15ef36b908fab642072a6ef296e8bb9cd3719ba6` |
| `MINERvA101/opt/bin/setup_MAT.sh` | `733e9cd839a0f75186d109eaab3dfe746a921d6d7b0347fbd6662b6f1ced3c0e` |
| `MINERvA101/opt/bin/setup_MAT-MINERvA.sh` | `c259101619ac365dcc57043d8ac4926908e51a8a87dad08f601394c9b418c3ac` |
| `MINERvA101/opt/bin/setup_UnfoldUtils.sh` | `bd305c17ddcd507f88ab49cbfcf5fe5a14075e0c1a173e631addcb3423212cd9` |

RM's log also carries ROOT's rootmap warnings, which say the RooUnfold classes in libUnfoldUtilsDict.so are already in
libRooUnfold.so. They are warnings, and no suite failed.

## The results

| env | suite | ran | failures | errors | skipped | guarded reads |
|---|---|---:|---:|---:|---:|---:|
| P | `test_cov2d_pseudo` (step A) | 16 | 0 | 0 | 0 | 0 |
| P | `test_cov2d_readouts` | 12 | 0 | 0 | 0 | 0 |
| P | `test_cov2d_null` | 5 | 0 | 0 | 0 | 0 |
| P | `test_cov2d_score` | 12 | 0 | 0 | 0 | 0 |
| P | `test_cov2d_jobs` (the submit side) | 31 | 0 | 0 | 1 | 0 |
| P | `test_cov2d` | 28 | 0 | 0 | 11 | 0 |
| R | `test_cov2d_blocks` | 25 | 0 | 0 | 0 | 0 |
| R | `test_cov2d_null` | 5 | 0 | 0 | 0 | 0 |
| R | `test_cov2d_score` | 12 | 0 | 0 | 0 | 0 |
| RM | `test_cov2d_pseudo_write` (step B) | 13 | 0 | 0 | 0 | 0 |
| RM | `test_cov2d_pilot` | 13 | 0 | 0 | 0 | 0 |
| RM | `test_cov2d_jobs` (the in-job check; the real parser) | 31 | 0 | 0 | 0 | 0 |
| RM | `test_cov2d` (`deploy_head`) | 28 | 0 | 0 | 11 | 0 |

**13 of 13 suite runs pass** (`TESTS-SUMMARY 13 ok of 13 suite runs`). Every one of the amendment's nine test modules
passed in at least one cluster environment, with only the skips below.

<!-- absence-ok: each skip is listed by name with its reason and the receipt where the test did run; the paragraph scopes this run, not whether a test exists -->
**The skips are the expected ones only, listed by name with the runner's reason** (the director's ruling on flag 2).
- **P, 1:** `test_cov2d_jobs.RealParser.test_every_line_parses` ("re2_driver imports PyROOT"). It ran and passed in
  RM.
- **P and RM, 11 each:** the `test_cov2d.Receipt` class ("needs PyROOT and uproot"). No cluster environment has both.
  - The tests: `test_mild_bank_passes_and_every_row_is_evaluated`, `test_compounding_row_stops`,
    `test_the_bound_is_exact_at_the_edge`, `test_an_unequal_band_is_not_certified_by_its_largest_universe`,
    `test_negative_composites_are_counted`, `test_nonfinite_weights_are_zeroed_and_counted`,
    `test_a_nonpositive_truth_cell_stops`, `test_truth_cells_are_recomputed_independently`,
    `test_driver_names_without_root_equal_the_import`, `test_truth_cell_matches_a_th2d` and `test_atime_move_stops`.
  - They test `cov2d_receipt.py`, the binding-1-era receipt, which no COV2D job runs.
  - All 11 ran and passed in the one local environment holding both, in the 155-test receipt at `5c0e02a2`
    (`../amendment/suites_5c0e02a2.txt`, 0 skipped).
  - Step A's library use of `cov2d_receipt` (`truth_cell`, `universe_columns`, `driver_phase_space`, `open_noatime`,
    `read_noatime`) is exercised by `test_cov2d_pseudo` in P. The cross-terms CLI's use of it is exercised by
    `test_cov2d_readouts` in P.

## Files

- `connect-tests.sh`: the script as run, sha256 `9895515a…`.
- `connect-tests.log.txt`: the connect's log, sha256 `593ae0a7…`, the digest taken on the node in `node_listing.txt`.
- `logs/`: one log per suite run. `blobs.txt` is the clone's `2d-unfolding/cov2d` tree. `SHA256SUMS` was written on the
  node. The logs carry a `.txt` suffix here, because `*.log` is gitignored. Their bytes are unchanged, and every digest
  in `SHA256SUMS` matches its file.
- `node_listing.txt`: `/dev/shm/josephrb-cov2d-tests` on login02, listed right after the fetch and before the removal, with the script's sha256.
- `removal.log.txt`: the clone, tmp and runner were removed by the script itself (in its log). After the fetch,
  `/dev/shm/josephrb-cov2d-tests` and `/dev/shm/josephrb-cov2d-tests.sh` were removed (rc 0 each), and `/dev/shm`
  was left empty.
