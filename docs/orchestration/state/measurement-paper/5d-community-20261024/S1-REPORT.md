# REPORT: S1, configuration (e)'s 5D covariance on the 16 H2 cells (2026-10-25)

**By** the measurement session, under [`S1-BINDING.md`](S1-BINDING.md) (with its §3 erratum, PR #342) and
[`S1-BINDING-AMENDMENT-1.md`](S1-BINDING-AMENDMENT-1.md), which bind [`S1-DECLARATION.md`](S1-DECLARATION.md).
Joseph's approval is `DECISION-20261024-joseph-approve-integration-wording-s1-compute-preserve.md`, item 2.

- Run on Perlmutter, 2026-10-25 00:34–05:51 UTC.
- **6.04 CPU node-h** of the 15.5 cap; no GPU, regular QOS only, nothing on CFS.
- Receipts are in [`s1/receipts-S1/`](s1/receipts-S1/), listed in `SHA256SUMS`. The ledger is
  [`s1/LEDGER.tsv`](s1/LEDGER.tsv). The readout is [`s1/readout/s1_assembly.json`](s1/readout/s1_assembly.json).
- The bank and detector-dump HPSS copy is reported separately, in [`S1-PRESERVE-REPORT.md`](S1-PRESERVE-REPORT.md).

**CITABLE FOR:** the S1 jobs, gates and assembly as run; the readout as computed; the measured seed-block zero and
its diagnosis D1–D4.
**NOT CITABLE FOR:** any publishability conclusion; any claim; the interpretation of the seed block, which is
**open until the director rules** (§7).

## 0. Summary

| step | outcome |
|---|---|
| deploy `d5617470` | HEAD and a clean tree; the §6 code, task-table, definition and declaration digests match; 20 tests OK |
| G1, bank-path denominator | ALL PASS; all 12 comparisons match the declared review |
| G2, central = data_R = P5 | ALL PASS |
| pilot, job 60232432 | COMPLETED 0:0, 722 s, 0.20 node-h. Load plus unfold at most 701.0 s, so no re-pricing |
| G3 on the pilot's 7 universes; G4 | ALL PASS; ALL PASS (bitwise) |
| P1, P2, seed (60233152/3/4) | all COMPLETED 0:0; 2.01, 2.01 and 1.83 node-h |
| G3 on all 175; G5 on 4 seeds | 175 PASS; 4 × 20 PASS |
| products and logs to HPSS | PASS (`s1-products.tar` `96181007…`) |
| assembly at `d5617470` | **STOP:** rc 1, `ModuleNotFoundError` (§4). Repaired by PR #346 and amendment 1 |
| deploy `3f545564`; module resolution | clean; 24 tests OK; PASS |
| assembly at `3f545564` | rc 0. npz `db000707…`, readout `81e5ef3f…` |
| assembly output and logs to HPSS | PASS (`s1-assembly.tar` `a4912d2f…`) |
| **seed block** | **exactly 0 in every cell**: the 80 seed products are bitwise equal to seed 42's. Diagnosed in D1–D4 (§7); interpretation open |

Definitions as in the declaration §3: `P=/pscratch/sd/j/josephrb`, `B=$P/s1-20261024`. Times are UTC; `sacct`'s
are PDT (UTC − 7). Log names are under `receipts-S1/logs/` unless a path is given.

## 1. Deploy (S1-BINDING §2)

**The first deploy,** `$B/deploy/d5617470`, cloned from GitHub at 00:34:02 (`deploy.log`):
- HEAD is `d5617470a7d08215e1da5622722d348da6a148d1`, and `git status --porcelain --ignored` printed 0 lines.
- These all match the declaration §6 and the binding §1:

  | file | sha256 |
  |---|---|
  | `s1_assemble.py` | `5ebe1a8a…` |
  | `s1_controls.py` | `bfc8986e…` |
  | `test_s1_assemble.py` | `a4bb6982…` |
  | the three task tables | `6db31a34…`, `bb32d918…`, `4425a91e…` |
  | `h2_definition.json` | `b6790761…` |
  | `sbatch_timing_packed.sh` | `b72aaa62…` |
  | `stage0_preserve.sh` | `27ccc04a…` |
  | the declaration | `f1c7288c…` |

- `s5c_array.sh` is present.
- **The §6 input digests are not in `deploy.log`.** The tasks check `of_inputs_5d.npz` and `bkg_dump.npz` at run
  time (`--expect-npz-sha256`, `--expect-bkg-sha256`), and the assembly checks its own inputs (§5).
- **The tests.** From `nd-unfolding/tests`, I ran
  `TMPDIR=$B/tmp env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -B -m unittest test_s1_assemble test_s5p_assemble`.
  It reported "Ran 20 tests … OK" (`deploy-tests.log`).
  - The command works from `nd-unfolding/tests`, or from the deploy root with module paths. It fails to import from
    `nd-unfolding/`, because `tests/` has no `__init__.py`.

**The `.pyc` note.** The director accepted it, by correspondence on 2026-10-25; it is not in a committed record.
- The G1 and G2 runs used `$PY` with `-I` but without `-B`. They wrote 13 `.pyc` files into
  `$D/nd-unfolding/__pycache__/` at 00:34:27–32 (`pycache-removed.txt` lists them).
- The pilot ran with them present. The files are ignored and untracked, so `s5c_array.sh`'s
  `--untracked-files=no` check could not see them. They are bytecode of the pinned sources, and Python checks each
  against its source's mtime and size.
- My stricter `--porcelain --ignored` recheck before submitting production caught them. I removed them at 01:01:56,
  the recheck printed 0 lines, and then I submitted (`deploy.log`).
- Every later gate and check ran with `-B`.

**The reviewer's `/tmp` write.**
- During the declaration's review (2026-10-24), the review agent wrote `/tmp/s1rev_meta_read.py`, a 1,052 B
  metadata helper, on login12, against its read-only rules.
- I inspected it and removed it. It touched no S1 input or product. It is recorded here at the director's request, made by correspondence.

**The second deploy,** `$B/deploy/3f545564`, made at 05:44:56 for the assembly only, under amendment 1 §4.1
(`deploy-3f545564.log`):
- HEAD is `3f5455648ff9b2c8ce85315f8f95458d87ea5673`, and `--porcelain --ignored` printed 0 lines before and after the
  tests.
- `s1_assemble.py` has sha256 `b157250a…`.
- `test_s1_scripts_isolated`, `test_s1_assemble` and `test_s5p_assemble` ran 24 tests, OK, with `-B` and
  `TMPDIR=$B/tmp` (`deploy-3f545564-tests.log`).
- The old deploy was left as it is.
- `deploy-3f545564.log` holds one stderr line, `sha256sum: …S1-BINDING-AMENDMENT-1.md: No such file or directory`.
  It is harmless: the amendment landed after that pin.
- **The environment.** Every S1 step sourced the deploy's `setup_salloc_env.sh`, as `s5c_array.sh` does, and so did
  the D1/D2 diagnostic. Each env log (`$B/runs/logs/*.env.log`, `logs/diag-env.log`) prints two
  "No such file or directory" lines, for `unbinned_unfolding/build/setup.sh` and `MINERvA101/opt/bin/setup.sh`, which
  are not built in a fresh clone. The Python 3.11 check in `s5c_array.sh` passed in every step.

## 2. Gates (S1-DECLARATION §4)

Every gate printed PASS or FAIL per check and no cross-section value. Only G1, which is simulation-only, printed
deviations.

| gate | when (UTC) | command target | output (verbatim summary line) | rc | log |
|---|---|---|---|---|---|
| G2 | 00:34:27, from the session terminal; the log has no timestamp | `central` | 5 × PASS, "ALL PASS central" | 0 | `G2.log` |
| G1 | 00:34:32 per the log (53 s; peak RSS 3,168,456 KiB = 3.24 GB) | `denominator` | 12 × PASS, "ALL PASS denominator" | 0 | `G1.log`, `G1.time` |
| G3, pilot | about 01:00, after the pilot's 00:59:56 end; the log has no timestamp | `products`, 7 universes | 7 × PASS, "ALL PASS products" | 0 | `G3-pilot.log` |
| G4 | about 01:00; the log has no timestamp | `cv` | "PASS cv_control_equals_central_bitwise", "ALL PASS cv" | 0 | `G4.log` |
| G3, all | about 05:16, after the seed job's 05:16:02 end; the log has no timestamp | `products`, 175 universes | 175 × PASS, "ALL PASS products" | 0 | `G3-all.log`, `G3-all.universes` |
| G5 | about 05:16; the logs have no timestamp | `seeds`, s = 45, 48, 51, 54 | 20 × PASS each, "ALL PASS seeds" | 0 each | `G5-<s>.log` |

**G1's deviations.**
- Each of the 6 GEANT universes was compared against both the dump's and the npz's CV `denom_nd`. All 12 comparisons
  gave the same numbers:
  - same support;
  - total relative deviation 3.546 × 10⁻¹²;
  - maximum cell deviation 4.0978 × 10⁻⁴;
  - 5,066 cells above 10⁻⁹.
- That is the declared review's measurement. The per-cell bound is 10⁻³.

**G3's universe list** is the `--universes` fields of `tasks-pilot.tsv` lines 1–7 and `tasks-prod.tsv` lines 0–15.
That gives 175 entries with none duplicated. They are recorded verbatim in `G3-all.universes`.

## 3. Jobs and ledger (S1-DECLARATION §3)

Every job ran with `-A m3246 -q regular -C cpu`, exclusive and `--no-requeue`, through the bound
`sbatch_timing_packed.sh` at pin `d5617470`, with 8 lanes × 32 CPUs × 56 GB. `squeue` and `sacct` show the QOS as
`regular_1`. The submissions are in `submit.log`.

An over-time watcher, `tools/watch.sh`, ran for each job, detached on login12. It would cancel a job whose run time
exceeded 1.25 × its projected wall: 1,712 s, 18,837 s, 18,837 s and 16,112 s. None fired; every exit was logged
(`watch.log`).

| job | id | lines | elapsed | node-h (billing 256) | cap | declared expected | peak RSS per step (sacct MaxRSS; K = KiB) |
|---|---|---|---|---|---|---|---|
| pilot | 60232432 | `tasks-pilot.tsv` 0–7 | 722 s | **0.20056** | 0.5 | 0.35–0.38 | 16.40–17.63 GB |
| P1 | 60233152 | `tasks-prod.tsv` 0–7 (88 bank universes) | 7,232 s | **2.00889** | 5.25 | 3.84–4.19 | 19.40–19.78 GB |
| P2 | 60233153 | `tasks-prod.tsv` 8–15 (74 bank + 6 detector) | 7,226 s | **2.00722** | 5.25 | 3.84–4.19 | 18.99–19.72 GB |
| seed | 60233154 | `tasks-seed.tsv` 0–7 | 6,570 s | **1.82500** | 4.5 | 3.14–3.58 | 23.69–24.08 GB |
| **total** | | 256 unfolds | | **6.04167** | **15.5** | 11.2–12.3 | |

**Results.**
- All 4 jobs and all 32 steps were COMPLETED 0:0. Every line log ends with rc 0, and every batch script printed
  "done rc=0" (`s1*_<jobid>.out`).
- Products: 176 in `$B/runs/uni` (175 universes and the CV control) and 80 in `$B/runs/seed`, with no `.partial-`
  files.
- **The pilot's timings** (`pilot-timing.log`, product metadata): `seconds_load + seconds_unfold` ran 694.3–701.0 s,
  under the 1,500 s re-pricing line (declaration §3, rule 2).
- **Actual walls were below the projections.** The declared projections were 1,370 s for a universe step and
  1,132–1,289 s for a seed step. The walls came in at about half that: the pilot's products took 694.3–701.0 s each. In production a step took
  7,129–7,227 s for 11 universes, 6,549–6,567 s for 10, and 3,939 s for the 6 detector universes. A seed step took
  6,526–6,565 s for 10 unfolds. So every job used less than its
  declared expected range.
- **Ledger.** `s1/LEDGER.tsv` is built from `receipts-S1/sacct.txt`, the full `sacct -P` of all four jobs and their
  steps. Node-h is `ElapsedRaw × billing / 256 / 3600`.

## 4. The first assembly: STOP (05:17:00, login12)

- **The run.** I ran the §3.1 argv at `D=$B/deploy/d5617470`, with `--cmodel-sha256 3008d8f6…e882`. The one
  difference from the declaration is the interpreter flags, `-I -B` where the declared `$PY` has `-I`; `-B` was adopted
  after the `.pyc` note (§1). The argv is in `assembly.err`.
- **The result:** it exited with rc 1 after 0.34 s and wrote no output. The traceback is in `assembly.err` and
  `assembly.log`, which are kept as they were:
  ```
  File ".../deploy/d5617470/nd-unfolding/s1_assemble.py", line 37, in <module>
      import s5p_stage1_inspect as s1
  ModuleNotFoundError: No module named 's5p_stage1_inspect'
  ```
- **The cause** is in the code this session wrote.
  - Under `-I`, Python does not put the script's directory on `sys.path`; on this 3.11 interpreter
    `sys.flags.safe_path` is True.
  - `s1_controls.py:31-33` inserts its own directory. `s1_assemble.py` did not.
  - No test ran the script as declared.
- **Handling:** it was reported unrepaired, as S1-BINDING §2 rule 5 requires. The director ruled for a code fix and a
  re-pin. That is PR #346, merged at `3f545564` and recorded in amendment 1:
  - the `_ND` insert copied from `s1_controls.py`;
  - a subprocess test that fails on the old bytes and passes on the new;
  - a sweep that found no other affected script.
- **The products HPSS copy** went ahead before the re-pin.
  - The director ruled by correspondence, after my STOP report, that it could.
  - I wrote `products_hpss.sh` at 05:18:27, and the copy ran 05:18:29–05:18:33, 89 s after the STOP.
  - Amendment 1 §2.2 recorded the ruling afterwards.
- **A scratch clone during the STOP.** For PR #346, `$B/tmp/fixcheck-fe5d79c6` (05:23:59) was a scratch clone of the
  fix branch. It ran the new test both ways on the cluster interpreter. It is not a deploy, and no S1 step used it.

## 5. The assembly under amendment 1 (05:45:39–05:45:43, login12)

**Module resolution (amendment 1 §4.2),** logged in `modres-3f545564.log`.
- **How it was run:** under `$PY` with `-B`, from cwd `$B/tmp`. I loaded `s1_assemble` by path with
  `importlib.util.spec_from_file_location`, which runs its top-level imports.
- **The interpreter:** Python 3.11.14, `isolated=1`, `safe_path=True`.
- **The repo modules it loaded:**
  - `s1_assemble` → `$B/deploy/3f545564/nd-unfolding/s1_assemble.py`;
  - `s5p_stage1_inspect` → `$B/deploy/3f545564/nd-unfolding/s5p_stage1_inspect.py`.
- **The one third-party module:** `numpy`, from the conda env's `site-packages`.
- **Result: PASS under this session's reading.** I read the rule as covering repo code, so numpy from the env's
  site-packages falls outside it.
  - Amendment 1 §4.2 as written says every non-standard-library module must lie under the new deploy, and numpy does
    not.
  - I applied my reading before the run: the probe wrote at 05:45:24, and the assembly started at 05:45:39.
  - The director accepted the reading by correspondence, after the run.
- **The probe** ran from a heredoc on stdin. Its text is committed as `tools/modres_probe.transcribed.py`, a
  transcription of what was sent; its bytes were not hashed at run time.

**The run.**
- I ran the §3.1 argv once, with `D=$B/deploy/3f545564` and `--cmodel-sha256 3008d8f6…e882`. As in §4, it ran under
  `-I -B` where the declared `$PY` has `-I`.
- The output path was empty beforehand. The full argv is recorded in `assembly-3f545564.err`'s `time -v` header.
- **Result:** rc 0 in 3.73 s, peak RSS 77,824 KB, and stderr carried nothing but the timing. The deploy stayed clean.

| output | bytes | sha256 |
|---|---|---|
| `$B/s1_assembly.npz` | 119,273 | `db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4` |
| `$B/s1_assembly.json`, committed as `s1/readout/s1_assembly.json` | 33,421 | `81e5ef3fe8e7b055360dc43b8a8240c9b5c39c8aa6e7c507b3211d305b326b21` |

- The readout's `assembly_sha256` is the npz's sha256.
- The npz holds `f`, `U`, the 46 blocks, `C_e`, `C_model_frac`, `C_model_abs`, `C_total` and `meta`.
- The readout records `code_sha256`: `s1_assemble.py` `b157250a…` and `s5p_stage1_inspect.py` `26569afc…`.

**The input digests,** from the readout's `meta.inputs_sha256`, 291 entries:
- 175 universe products, 80 seed products, the central value, 20 set-A replicas and 10 laterals;
- the definition, X01, the constraint file, C_model and `of_inputs_5d.npz`.
- `receipts-S1/hpss/PRODUCTS-INVENTORY.sha256` gives the sha256 of every product file on pscratch.
- **A recording gap,** not a missing check:
  - `stat_replicas` is 50, and all 50 set-A replicas `data_b{1..50}_j{101..150}` were hashed against the Stage 0
    `INVENTORY.sha256` (`s1_assemble.py:316-319` at `3f545564`, `require_listed` → `require_sha`).
  - But `inputs_sha256` lists only the 20 that the seed-42 block reuses (`:346-350` at `3f545564`).
  - The other 30 digests are pinned in `5d-design-20261023/stage0/INVENTORY.sha256`, not in the readout.

**The 285 cited npz, tracked beside the readout.** The pre-commit receipt-artifact check refused the first commit.
The director then ruled for option (B), by correspondence on 2026-10-25; the ruling is not in a committed record.
- **Beyond the declared commit set.** These npz carry the `xsec_flat` arrays. That goes beyond declaration §3.1's
  commit set, which was the JSON plus the npz's sha256.
- **Why it refused.** `verify_receipt_artifacts.py:185-214` resolves each bare filename against the receipt's own
  directory and its companion directory. The readout's `inputs_sha256` keys name 285 npz files by bare name.
- **Where they now are:** in the companion directory
  [`s1/readout/s1_assembly/`](s1/readout/s1_assembly/), 27,179,746 B in all.
- **How the list was made.** `FILES.tsv` lists each file's basename, its readout sha256 and its pscratch source. It
  was generated from `meta.inputs_sha256` and holds 285 unique basenames:
  - 175 from `$B/runs/uni` and 80 from `$B/runs/seed`;
  - 20 from `$P/s5p-20260926/runs/s2/num/data` and 10 from `$P/s5p-20260926/runs/s3/latunf`.
- **How they were copied.** One `tar` stream of exactly those paths, staged with `git add -f` one explicit path at a
  time, with no glob and no directory add.
- **How they were checked:**
  - every local sha256 equals the readout's value, and equals the live pscratch file's (285 of 285);
  - the 255 S1 products equal `receipts-S1/hpss/PRODUCTS-INVENTORY.sha256`;
  - the 20 set-A replicas equal the Stage 0 `INVENTORY.sha256`, and the 10 laterals equal the sf1 manifest.
- `SHA256SUMS` in that directory covers `FILES.tsv` and the 285 files; `sha256sum -c` reports all OK.
- With the files tracked, the receipt check reads "0 missing". UNRESOLVED is unchanged at the pinned 66.

## 6. The readout, as computed

Per-cell relative σ, in %, by component group. These are from `s1_assembly.json` `relative_sigma` and
`median_relative_sigma`, rounded to 0.01.

| cell | stat | flux | interaction | detector | lateral | normalization | seed | C_e | C_model | C_total |
|---|---|---|---|---|---|---|---|---|---|---|
| R00 | 0.20 | 3.93 | 0.98 | 1.56 | 5.01 | 1.40 | 0.00 | 6.77 | 0.43 | 6.79 |
| R01 | 0.23 | 3.58 | 1.18 | 2.14 | 4.85 | 1.40 | 0.00 | 6.66 | 0.67 | 6.69 |
| R02 | 0.33 | 3.75 | 3.56 | 1.96 | 5.08 | 1.40 | 0.00 | 7.65 | 11.36 | 13.69 |
| R03 | 0.33 | 3.52 | 5.39 | 1.66 | 4.70 | 1.40 | 0.00 | 8.27 | 9.38 | 12.50 |
| R04 | 0.14 | 3.47 | 0.58 | 1.31 | 0.57 | 1.40 | 0.00 | 4.05 | 0.88 | 4.14 |
| R05 | 0.37 | 4.14 | 2.13 | 1.68 | 1.85 | 1.40 | 0.00 | 5.48 | 3.46 | 6.49 |
| R06 | 0.33 | 3.48 | 2.25 | 1.21 | 0.73 | 1.40 | 0.00 | 4.61 | 3.19 | 5.60 |
| R07 | 0.30 | 3.90 | 5.08 | 1.76 | 1.75 | 1.40 | 0.00 | 7.02 | 3.45 | 7.82 |
| R08 | 0.22 | 3.74 | 1.52 | 2.17 | 0.77 | 1.40 | 0.00 | 4.86 | 1.63 | 5.13 |
| R09 | 0.18 | 3.52 | 1.85 | 2.18 | 1.08 | 1.40 | 0.00 | 4.87 | 3.24 | 5.84 |
| R10 | 0.25 | 3.42 | 5.53 | 2.42 | 0.43 | 1.40 | 0.00 | 7.10 | 4.03 | 8.16 |
| R11 | 0.31 | 3.35 | 5.16 | 2.56 | 2.91 | 1.40 | 0.00 | 7.42 | 11.15 | 13.39 |
| R12 | 0.18 | 3.48 | 1.95 | 1.68 | 4.25 | 1.40 | 0.00 | 6.23 | 0.51 | 6.25 |
| R13 | 0.28 | 3.85 | 5.93 | 2.08 | 3.93 | 1.40 | 0.00 | 8.47 | 6.81 | 10.87 |
| R14 | 0.16 | 3.73 | 1.22 | 2.14 | 1.34 | 1.40 | 0.00 | 4.87 | 0.82 | 4.94 |
| R15 | 0.22 | 3.48 | 3.19 | 1.82 | 3.16 | 1.40 | 0.00 | 6.13 | 4.78 | 7.77 |
| **median** | **0.24** | **3.55** | **2.19** | **1.89** | **2.38** | **1.40** | **0.00** | **6.45** | **3.34** | **6.74** |

**Trace shares** of C_total (`trace_share`):

| component | stat | interaction | flux | detector | lateral | normalization | seed | C_model | sum |
|---|---|---|---|---|---|---|---|---|---|
| trace share | 0.0010 | 0.1705 | 0.1881 | 0.0525 | 0.1406 | 0.0276 | 0.0000 | 0.4196 | 1.0000 |

**Eigenvalue extremes and rank** (`eigen`; absolute, (cm²/nucleon)²):

| matrix | min eigenvalue | max eigenvalue | rank at 1e-12 relative |
|---|---|---|---|
| C_e | 9.3509e-84 | 1.8690e-79 | 16 |
| C_total | 1.1947e-83 | 1.8939e-79 | 16 |

**What the components are** (declaration §3.1):
- **stat** is set A's 50 bootstrap replicas.
- **flux** is the 100 Flux universes, weighted by the ν-e + IMD constraint. `flux_weights`: sum 211.012, n_eff 19.06.
- **interaction** and **detector** are the MAT mean-centred bands. GEANT comes from the detector dump.
- **lateral** is the 5 lateral bands, with X01 applied to Muon_Energy_MINOS.
- **normalization** is 1.4 %.
- **seed** is C08 over seeds 42, 45, 48, 51 and 54 (§7).
- C_e is the sum of the above, and C_total = C_e + C_model_abs.
- `not_included`: "inflation D", "C_ML", "bounded envelope h", "Rvp1pi".
- `integral`: "sum_f xsec_flat_f * vol_f (cm^2/nucleon)".

**Labels, verbatim.**
- The S1 readout carries no label strings of its own.
- The C_model input's labels are in `cmodel_5d.json`, sha256 `3cfdc6a5…`, on pscratch and committed at
  `nd-unfolding/pv-ladder/readouts/cmodel_5d.json`:
  - **component:** "generator-shape model dependence; not a calibrated bound (M2, kappa = 1, unscaled)"
  - **coverage:** "coverage at held-out truths was not validated (DECISION-20261024-joseph-5d-community-standard-route.md item 3); the paper states this as a limitation"
    <!-- absence-ok: a verbatim label quoting cmodel_5d.json, which quotes DECISION-20261024-joseph-5d-community-standard-route.md item 3 -->
  - **gibuu:** "GiBUU's shape is applied on p_parallel < 10 GeV/c; above it the prior is unchanged. At 6 <= p_parallel < 10 GeV/c GiBUU's sample lacks the E_nu > 20 GeV part, 4.9-5.3 % of the cross section there. The paper's joint tests use the narrower p_parallel < 6 GeV/c (H2-DEFINITION-ADDENDUM-GIBUU-DOMAIN.md)"
  - **step_adjacent:** "in every reporting cell 77-100 % of the prior weight lies beside a step in r > 0.1 drawn by the noise gate or a cut, where PV-2D found the large-shift tail; the shifts go in as measured (H2-DEFINITION-DECLARATION.md §1.3, §3.4)"
  - **positive_control:** "positive control passed on the 27 base H2 cells"
  - **positive_control.reporting16:** "not powered: the 16 reporting cells cannot carry the declared rule (ungraded)".
    S1's readout is on these 16 reporting cells.

## 7. The seed block: measured as exactly zero (interpretation open)

**What the readout shows.** The seed component's relative σ is 0.00 in all 16 cells, and its trace share is 0.0000.

**What was measured** (`seed-equality.log`, 05:47:09, login12; no values printed). The producer ran from a heredoc;
its text is committed as `tools/seed_equality.transcribed.py`, a transcription whose bytes were not hashed at run
time.
- The `xsec_flat` of all 80 seed products, `S1seed<s>_b<b>_j<100+b>` for s = 45, 48, 51, 54 and b = 1–20, is
  **bitwise equal** to set A's seed-42 `data_b<b>_j<100+b>`.
- Their metadata does differ as declared, and G5 checked it:
  - `estimator_seed` is s;
  - the three B0 estimators carry `random_state` s;
  - the refinement carries `random_state` s + 3 (48, 51, 54, 57).
- For each seed, the printed record of b1 shows `subsample` 1.0, `subsample_freq` 0, `colsample_bytree` 1.0,
  `deterministic` True and `bin_construct_sample_cnt` 2147483647 for all three B0 estimators and for the refinement.
  The refinement runs at 400 trees and 31 leaves.
  - `estimator_seed` is checked in all 80 products, by G5 and by the independent reviewer. The other parameters were
    printed for b1 only.
- LightGBM is 4.6.0.

The director asked, by correspondence, for D1–D4 before the report draws anything from this.

### D1: the seed reaches LightGBM

`tools/diag_seed.py` (sha256 `32845870…`) ran on login12 at 05:50:57–05:51:22, 0 node-h, from the deploy that ran S1.
Its output is `diag-D1D2.log`.
- **What it builds:** the B0 estimators by the production path, `s5c_unfold.estimator_config` over
  `omnifold_nn_core.make_estimators` with `config_params("deterministic", …)`, as `s5p_numerics.unfold_one` →
  `s5c_unfold.unfold` does.
- **The refinement classifier:** `s5n_pseudo.refine_params`, after `s5e_candidate.install("R")` as
  `s5p_numerics.main` installs it, then `unfold_2d_omnifold_unbinned._make_bkg_classifier`, as `s5n_pseudo.refine`
  does.
- **How the parameters were read:** each classifier was fit on a small synthetic set, and the effective parameters
  were read from the trained model string.
- The module files resolve to `$B/deploy/d5617470/nd-unfolding/`.
- **A first run** omitted `s5e_candidate.install("R")`, so its refinement ran at 100/8. It is kept as
  `diag-D1D2-without-candidate-R.log`. Its conclusions are the same.
  - Its script is committed as `tools/diag_seed_v1.py`. I reconstructed it by undoing the one edit, and its sha256
    `24284078…` equals the one that log records.
- **Not at production settings in two respects.**
  - D1 and D2 ran with `num_threads` 8, where S1 used 32.
  - D1's table shows `clf1`, the first of the three B0 estimators.

| effective parameter | B0, seed 42 | B0, seed 45 | refinement, seed 42 | refinement, seed 45 |
|---|---|---|---|---|
| `seed` | 42 | 45 | 45 | 48 |
| `data_random_seed` | 175 | 185 | 185 | 195 |
| `bagging_seed` | 400 | 32645 | 32645 | 32123 |
| `feature_fraction_seed` | 30056 | 3942 | 3942 | 10596 |
| `extra_seed`, `drop_seed`, `objective_seed` | 12879, 17869, 16083 | 24660, 5926, 14259 | 24660, 5926, 14259 | 3672, 26750, 12434 |
| `deterministic`, `force_row_wise` | 1, 1 | 1, 1 | 1, 1 | 1, 1 |
| `bin_construct_sample_cnt` | 2147483647 | 2147483647 | 2147483647 | 2147483647 |
| `bagging_fraction`, `bagging_freq` | 1, 0 | 1, 0 | 1, 0 | 1, 0 |
| `feature_fraction`, `feature_fraction_bynode`, `extra_trees` | 1, 1, 0 | 1, 1, 0 | 1, 1, 0 | 1, 1, 0 |
| `num_iterations`, `num_leaves` | 100, 8 | 100, 8 | 400, 31 | 400, 31 |

**Result:** the seed reaches the boosters. `seed` and every seed derived from it differ between 42 and 45, and
nothing else differs. This rules out a plumbing defect in which only the metadata changes.

### D2: positive control

The same factories were fit on a synthetic two-class set of 400,000 rows and 5 features. The predicted
probabilities on 20,000 held-out synthetic rows were compared between seeds 42 and 45 (`diag-D1D2.log`):

| setting | B0 | refinement |
|---|---|---|
| production, as S1 (`deterministic`; bins from all rows; no bagging) | **bitwise equal** | **bitwise equal** |
| plus `subsample` 0.8, `subsample_freq` 1 | differ (max \|Δp\| 0.110) | differ (0.222) |
| `bin_construct_sample_cnt` 200000, LightGBM's default, on 400,000 rows | differ (0.110) | differ (0.479) |

**Result:** with one stochastic setting on, the factories respond to the seed, so the null is not a dropped
parameter. With the production settings they are seed-invariant, and so are the S1 products.

### D3: 5D against 2D

This was compiled by an independent read-only agent and spot-checked by this session. Labels: **[R]** recorded in
run outputs, **[C]** read from code, **[I]** inference.

- **The 2D code** is cited at `dcac48e3`. The RE-2 runs used deploy `dbdad2f9`. Their logs record the driver and helper
  sha256 (`38ff3705…`, `e9623412…`), and both files are byte-identical at `dcac48e3`.
- **The 5D code** is cited at `d5617470`.

**The 2D figure, corrected.**
- RE2-PARTC-REPORT.md's values-table appendix has columns "printed", "purity control value" and "regenerated".
- For `tabuq-c08-median` (`:452`) it lists 0.057 printed (purity, unrounded 0.0571922) and **0.048 regenerated**
  for the refined estimator.
- So the refined 2D C08 per-cell median is 0.048. 0.057 is the value now printed, from the purity (E_U) estimator.
  Both are nonzero. The values table does not state units; the printed site is `N/sec_results.tex:195`.

**How the seed is used in each path:**

| | 2D `a-refined-400-31` (RE-2 C08) | 5D configuration (e) (S1) |
|---|---|---|
| runs | `re2_driver.py` via `mnv_guarded_run.py`; `--estimator lgbm --seed S --bootstrap-seed b --bkg-mode negweight-refined --refine-n-estimators 400 --refine-num-leaves 31`, 64 CPUs (`run/partb_runs.tsv:190`, `:490-569`) [R] | `s5p_numerics.py --config R --construction data --pairs b:100+b --estimator-seed S --threads 32` (`s1/tasks-seed.tsv`) [R] |
| B0 `random_state` | s, s+1, s+2 for step-1 classifier, step-2 classifier and regressor (`re2_driver.py:2247-2250`); log "Pinned GBDT seeds: step1=45, step2=46, regressor=47" [C, R] | s for all three (`omnifold_nn_core.py:146-147`) [C, R] |
| refinement `random_state` | s+3, at 400/31 (`re2_driver.py:2182-2185`); recorded `{n_estimators 400, num_leaves 31, random_state 48}` for s = 45 [C, R] | s+3, at 400/31 (`s5n_pseudo.py:234-236`, `s5e_candidate.py:36-49`) [C, R] |
| `bin_construct_sample_cnt` | **not passed in any fit** (`re2_driver.py:466-471`, `:2182-2185`, `:2247-2250`; `omnifold.py:209-220`), so LightGBM 4.6.0's default 200,000 applies [C] | **2,147,483,647 (all rows)** in every fit (`s5c_unfold.py:57`, applied at `:63-84` and through `refine_params`) [C, R] |
| `deterministic`, `force_row_wise` | not passed, so False and automatic [C] | True, True [R] |
| `num_threads` | `n_jobs=None`; the value is not recorded [C], so undetermined | 32 [R] |
| bagging, feature fraction, `extra_trees` | not passed, so 1.0, 0, 1.0 and False [C] | 1.0, 0, 1.0; `extra_trees` absent, so False [R, C] |
| other seed uses | none: `args.seed` is used only at `:2182-2183` and `:2247-2250`; the bootstrap uses `--bootstrap-seed`; the helper has no split, shuffle or early stopping (`omnifold.py:247-269`) [C] | none: the bootstrap is seeded by b (`s5n_pseudo.py:207-218`); `train_frac` 1.0 means no split [C] |

**Training rows,** each far above 200,000:

| fit | 2D: `/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/logs/S4B_s45_01.log` [R] | 5D, b1: product metadata `n_observed_rows`/`n_template_rows`; `of_inputs_5d.npz` MCgen 32,849,103 rows, `pass_reco` 20,404,292 [R; the sums are arithmetic] |
|---|---|---|
| refinement | 4,713,254 | 2,979,708 (2,586,886 observed + 392,822 template) |
| step-1 classifier | 25,117,546 | 23,384,000 |
| regressor | 20,404,292 | 20,404,292 |
| step-2 classifier | 65,698,206 | 65,698,206 |

**What distinguishes 2D's nonzero C08 from 5D's zero.** On the 5D side this is recorded. For 2D the causal step is
[I], because no 2D full-binning run exists.
- **2D:** the 200,000-row sample that sets each fit's histogram bin edges is drawn with a seed-dependent
  `random_state` in all four fits. That is 0.3–4.2 % of the rows. With bagging, feature subsampling and `extra_trees`
  off, this sample is the seed's only consumer **[I, consistent with D2 and the s5c P1 record below]**. RE-2 measured
  the effect:
  - **the same seed repeated:** max relative difference 9.2 × 10⁻¹², not bitwise;
  - **seed 45 against 42 at the same replica:** median 1.96 × 10⁻³, max 1.98 × 10⁻² (`run/partb_readout/k1_core.json`,
    PB-ER-rep and PB-pow-S4B_s45_01) [R].
- **5D:** `s5c_unfold.py:57` sets `bin_construct_sample_cnt = ALL_ROWS` for the B0 estimators and, through
  `refine_params`, for the refinement. That leaves the seed nothing to act on [C].
- **The isolating record already exists:** `state/s5c/p1/p1_summary.json` at `6fab459b`, 5D B0 on the same inputs.

  | comparison | knob changed | difference |
  |---|---|---|
  | `production_s42_vs_s43` (`:52`) | none | median 5.7 × 10⁻³, max 0.12 |
  | `full_binning_s42_vs_s43` (`:61`) | bins from all rows, only | median 1.3 × 10⁻¹³ |
  | `production_repeat_s42` (`:79`) | same seed, repeated | 2.1 × 10⁻¹³ |
  | `deterministic_s42_vs_s43` (`:70`) | deterministic | bitwise equal |

  [R]
- **Reading:** full binning removes the seed's effect down to run-to-run noise. `deterministic=True`,
  `force_row_wise=True` and fixed `num_threads` remove that noise, which turns "below 10⁻¹²" into "exactly zero"
  [R, I].
- **A difference that does not decide it:** 2D gives its three estimators s, s+1 and s+2, and 5D gives all three s.
  With bagging and feature fractions off on both sides, this does not change the conclusion [I].
- **Not determined:** the exact `num_threads` of the 2D fits.
- **LightGBM version:** the 5D environment's version is 4.6.0, measured in the D1 run (`diag-D1D2.log`). That the 2D
  runs used the same `root_6_28` LightGBM is [I].

### D4: the code-byte note

Set A (job 58904837: estimator seed 42, float64, per its product metadata) and S1's seed products are bitwise equal, although their recorded code differs
in two files.

- **`nd-unfolding/s5p_numerics.py`:** `9d7c1232…` is the file at `abdc88c5` and `7ad8ca0f…` the file at `3669be38`.
  - `git diff abdc88c5 3669be38` adds two lines: `import s5p_truths` (`:52`) and `s5p_truths.install(s5n_pseudo)`
    (`:159`).
  - `s5p_truths.install` (`s5p_truths.py:137` at `3669be38`) only adds two pseudo-truth weightings, `cond_ratio`
    and `coarse_ratio`, to `s5n_pseudo.truth_weight`. The later file adds a third, `fine_ratio` (`:271` at
    `d5617470`).
  - The data construction (`s5p_numerics.py:193-195`, `s5n_pseudo.build_data`) does not call `truth_weight`.
  - **So the difference cannot touch the fit (read from code).**
- **`2d-unfolding/unfold_2d_omnifold_unbinned.py`:** `8ebe0277…` is the file at `cf8a4a67` and `74a4ed69…` the file at
  `c53e9c36`. There are five commits between them: `bb4b0b6f`, `971fc00c`, `355174fe`, `a35b1a3f` and `c53e9c36`.
  - In an AST comparison, the only pre-existing function that changed is `main`.
  - The added functions are branch-selection and provenance helpers, plus five module-level statements: three
    imports and two constants.
  - `refine_stay_positive` and `_make_bkg_classifier`, the only functions the 5D path calls
    (`s5n_pseudo.py:240-273` at `d5617470`), are **identical**.
  - **So the difference cannot touch the fit (read from code).**

### What is open

- **As measured:** the seed block is in the readout as computed, zero.
- **The zero is conditional on full binning.** Configuration (e) builds every fit's histogram bins from all rows
  (`s5c_unfold.py:57`), with bagging and feature subsampling off.
  - So this estimator's seed main effect is zero **by construction, not by chance**. The evidence is recorded: the
    settings are in every product, s5c P1 isolated full binning on 5D, and D2 reproduces it.
  - 2D's `a-refined-400-31` samples its bin rows by seed. That this is **why** its C08 is nonzero is [I]: it is
    consistent with D2 and the s5c P1 record, but no 2D full-binning run exists.
  - D1 shows the seed reaches LightGBM, and D2 shows the fit is invariant to it at these settings.
  - The director accepted this explanation by correspondence, pending its read of this report.
- **What this means is not decided here.** That covers choice 9 of the declaration, the readout's C_e and C_total, and
  the 2D precedent. It is **open until the director rules**.
- Nothing has been rerun, and nothing in the declaration or the readout has changed.
- The seed job cost 1.82500 node-h.

## 8. HPSS copies of the S1 products (S1-BINDING §2 item 7; amendment 1 §2.2)

Both copies went to `/home/j/josephrb/mnv-5d-s1-products-20261024`, a new directory beside the Stage 0 ones. Each
was made by a script modelled on `stage0_preserve.sh`:
- one sha256 inventory;
- one uncompressed tar, with its member count checked and the inventory re-verified after taring;
- `hsi put`, `hashcreate` and `hashverify`;
- a retrieval compared by sha256, then removal of the retrieved copy.

They ran on login12 with no Slurm job.

| copy | script (sha256) | files, bytes | tar sha256, bytes | hashcreate md5 | hashverify | retrieval | log |
|---|---|---|---|---|---|---|---|
| products and logs, 05:18:29–05:18:33 | `tools/products_hpss.sh` (`a60ea5d6…`) | 376, 25,812,762 | `9618100757472daee5ecc0f5ffd6374d17c1922a22493127d3b4ccccecb6cc61`, 26,470,400 | `d444883e1e35f9cf39ebc7748d7b4ed4` | "(md5) OK" | equal | `hpss/products.log` |
| assembly output and complete logs, 05:47:44–05:47:48 | `tools/assembly_hpss.sh` (`80308494…`) | 36, 262,006 | `a4912d2fcc263df6d2e3ea224b659b6d5d102cf2e02433cf8818190bcfd7309b`, 337,920 | `8d9f8fda4f5fd158a937dd8c4250ac24` | "(md5) OK" | equal | `hpss/assembly-hpss.log` |

**The products tar** holds:
- 176 `runs/uni` products and 80 `runs/seed` products;
- 32 line logs, 32 per-task inventories and 32 environment logs;
- `$B/logs` as of 05:18, which includes the first STOP's `assembly.log` and `assembly.err`;
- `watch.sh`.

**The assembly tar** holds:
- `s1_assembly.npz` and `s1_assembly.json`;
- `$B/logs` as of 05:47;
- `products_hpss.sh` and the products copy's receipts. The products tar itself is excluded, since it is already on
  HPSS.

**Not on HPSS,** all committed here:
- `assembly_hpss.sh` and its own log;
- `$B/diag/` (`diag_seed.py` and `env.log`) and the D1/D2 logs (05:50–05:51), which postdate the second tar;
- `sacct.txt`, a local capture.

**What was kept on pscratch:** both tars, `products-hpss/s1-products.tar` (26,470,400 B) and
`assembly-hpss/s1-assembly.tar` (337,920 B). The retrieved copies were removed by the scripts. The scripts'
inventories and tar sha256 files are in `receipts-S1/hpss/`.

**A note on `assembly_hpss.sh`.** It is `products_hpss.sh` with a different file set, tar name and work directory. It
was derived by `sed`. The first derivation also renamed the exclusion, to `s1-assembly.tar`; that was corrected to
`s1-products.tar` before it ran. The committed file is the one that ran.

## 9. Deviations and what the receipts do not show

- **The `.pyc` files and the reviewer's `/tmp` write** (§1).
- **The first assembly STOP** (§4), repaired under amendment 1.
- **The HPSS directory name** is this session's choice. The declaration says only "beside the Stage 0 tars".
- **A second HPSS copy** (§8) was added so that the declared npz is on HPSS (§3.1); the first copy predated it.
- **The watchers' and launch commands** come from the session's terminal; `submit.log` and `watch.log` record their
  effects.
- **The `/usr/bin/time -v` wrappers** on G1 and the assemblies add timing to stderr. They change nothing else.
- **The readout's set-A record** lists 20 of the 50 replicas it checked (§5).
- **Interpreter flags.** Both assemblies ran under `-I -B`, where the declared `$PY` has `-I` (§4, §5).
- **The products HPSS copy** ran 89 s after the STOP, on a ruling given by correspondence and recorded afterwards in
  amendment 1 §2.2 (§4).
- **Module resolution** passed under this session's reading, applied before the run (§5). The director accepted
  that reading after the run.
- **The scratch clone** `$B/tmp/fixcheck-fe5d79c6` (§4).
- **The tracked npz** go beyond the declared commit set (§5).
- **Three producers committed as transcriptions or reconstructions:** the module-resolution probe, the
  seed-equality probe and the first diagnostic. Only the reconstruction has a run-time sha to check against (§5, §7).
- **Director statements cited from correspondence** are marked as such.

## 10. Not concluded

This report makes no claim and draws no conclusion about publishability. The seed block's interpretation is open
until the director rules (§7).
