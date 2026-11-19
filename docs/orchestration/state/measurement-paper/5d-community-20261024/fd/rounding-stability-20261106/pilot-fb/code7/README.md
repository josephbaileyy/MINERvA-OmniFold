# PILOT-FB code 7: the director's code-6 items G1–G3 (receipt)

**By** session tier3-design, under PILOT-FB-BINDING-1 (declaration rev 3 at M_PFB `522ac0b6`). The scoped read of code 6
(`e3e2c887`, receipt `../code6/`; `~/codex-reports/pilot-fb-audit/code6/codex/report.md`) found F2, F3, F5 and F6 FIXED
and the C1 README a PASS. It found F1 and F4 PARTLY FIXED, plus one regression. Code 7 is exactly those three items,
each with a test and a mutant. The confirmation read checks only them, plus regressions in the diff from code 6.
**Nothing has run on the cluster.**
<!-- absence-ok: an operational status of this tranche, not a claim that a result does not exist -->

## The code, at `87ab91ba`

| file | sha256 |
|---|---|
| `nd-unfolding/fb_pilot_edges.py` | `439e92262c85a86b4aca6b7e368972d2cc0a12bca3c55eb02e5ec019b927965a` (unchanged) |
| `nd-unfolding/fb_pilot_gates.py` | `b55ea40d3691521248813b1702d7c3442aa7564e9956d1a8d211a1522371cd09` (unchanged) |
| `nd-unfolding/fb_pilot_probe.py` | `478316c13b2d902cebbb56e68c3e2762ecc49f57063a545ff87c0fdf9678e464` (unchanged) |
| `nd-unfolding/fb_pilot_analyze.py` | `4e1f92b8c3ea056a6f28b66548a1c1dfe75b4893c63d1f40efbaf98230db4b2d` |
| `nd-unfolding/sbatch_pfb.sh` | `63b96b64e310463e3eeb658e85e10c236859d5cda2e1ded0edad6100009cb6eb` |
| `nd-unfolding/pfb_smoke_prep.sh` | `4cc6771736b0268d6b61f15d822849459d819723d5f507fc421599de47d4cac4` |
| `nd-unfolding/tests/test_fb_pilot.py` | `0944bfa9f1c7fb235788a1a9024dc7b56dd59e9f9bc46de6a79035b9e5d04833` (81 distinct tests) |
| `nd-unfolding/tests/fb_pilot_mutation.py` | `625decfd692ed0330fba643203c241b841c671f53c943a6f7075565d596fc9a1` (150 mutants) |

The reviewed launch commands are unchanged from code 6 (`../code6/README.md`).

## The fixes

| item | fix | test |
|---|---|---|
| **G1** (F1): positive evidence only | the smoke accepts NIL only if (a) `sbatch --version` exits 0 and its first line parses (`^slurm[[:space:]-]*X.Y.Z`) to at least 23.02.3, or (b) `sbatch --help` exits 0 and NIL is on a line that names `--export`. Anything else exits 8, a STOP for the director: a nonzero exit, an unparsable version, or NIL anywhere else (in a failing probe's message, or on another help line). It uses bash builtins only, and records both exit statuses and outputs in `smoke-sbatch.txt`. The test stub answers only `--version` and `--help`; any other invocation fails loudly and leaves a marker, so a submission would be caught | `test_nil_needs_positive_evidence`, `test_the_smoke_confirms_nil_without_submitting` |
| **G2 (a)** (F4): an unambiguous snapshot | `setup_env_text` writes one record per name: the name, its status (`exported`, `set` but not exported, or `unset`) and the value under `printf %q`. GIT_CONFIG_* names come from `compgen -v`, so set-but-unexported ones are included. A multiline value can no longer move a fragment to the next variable | `test_the_snapshot_is_unambiguous` (the report's CONDA_PREFIX/CONDARC newline-shift probe gives different snapshots with equal record counts; the export statuses), `test_the_newline_shift_refuses_at_the_job` (end to end) |
| **G2 (b)**: a required digest | the receipt writer exits 9 unless `smoke-setup-env.txt` exists and hashes to a 64-hex sha256. The checker refuses unless both the receipt's digest and the file's are 64-hex sha256 and they are equal. A null digest never matches a missing file | `test_a_null_setup_digest_refuses` |
| **G2 (c)**: refusal without the setup's interpreter | `newfile`, which creates every refusal record and log, runs `/usr/bin/python3 -I -S` by absolute path. The F4 mismatch refusal after the setup never runs a setup-selected `python3` | `test_a_mismatch_refusal_never_runs_the_setups_python` (the setup puts a loud stub `python3` first on PATH; the refusal is written and the stub never ran) |
| **G3** (code 6 regression) | `traced_setup` restores PYTHONDONTWRITEBYTECODE, PYTHONNOUSERSITE, GIT_CONFIG_NOSYSTEM and GIT_CONFIG_GLOBAL before the denied-variable check, so the refusal path runs with the declared values | `test_the_declared_values_are_restored_before_the_denied_check` (the function as the script defines it: a setup that clears both Python settings and exports PYTHONSTARTUP returns 97 with both restored) |

## Receipts

The receipt files are code 7.1's (`receipts.sh 8da6738a`, clean clone). Code 7's own receipts (at `87ab91ba`: 81/81
tests, 150/150 mutants) are in this directory's git history at commit `be69ed86`.

## Code 7.1: the director's final mechanical patch P1–P4

The director read code 7 (`c41c5a8c`; `~/codex-reports/pilot-fb-audit/code7/codex/report.md`). G2b was FIXED; G1,
G2a, G2c and G3 were PARTLY FIXED. The director ruled a mechanical patch of four items, with no further model read. The
director checks the diff.

| item | change | test |
|---|---|---|
| **P1** (G1) | the help-text path is dropped. The smoke calls only `sbatch --version`, and accepts NIL only when it exits 0 and its first line matches the anchored `^slurm[ -]([0-9]+)\.([0-9]+)\.([0-9]+)$` with a version of at least 23.02.3. Anything else exits 8. The test stub compares its whole argv, which must be exactly `--version`, and otherwise exits 99 with a marker | `test_nil_needs_positive_evidence` (`slurm 24.05.4garbage` gives exit 8; the stub run as `--version extra` hits the marker), `test_the_smoke_confirms_nil_without_submitting` (the old help-pass case is now a 23.02.3 version pass) |
| **P2** (G2a) | export status comes from the `x` flag anywhere in `declare -p`'s attribute field, so `-x`, `-rx` and `-xr` all count as exported | `test_readonly_plus_export_is_an_export` (`readonly GIT_CONFIG_COUNT=0` in the smoke against a readonly exported one in the job refuses) |
| **P3** (G3, the -I regression) | `newfile` runs `/usr/bin/python3 -I -S -B`, because `-I` ignores PYTHONDONTWRITEBYTECODE | `test_newfile_writes_no_bytecode` (`sys.dont_write_bytecode` is True under that exact command line) |

### Accepted residuals added to the C1 list (P4; each fails closed)

These join the ten accepted items in `../code6/README.md`.

- **(r11)** A setup could define a shell function named like the absolute interpreter path, or set loader-trace
  variables. Either can suppress the refusal record on a mismatch. The job still exits nonzero and never fits. This
  falls under the accepted residual for setup side effects.
- **(r12)** A readonly declared variable that the setup clears cannot be restored. The denied-variable path still
  returns 97, and the job refuses.
- **(r13)** A director gate replaces the help-text evidence for NIL. Before the job go, the director reads the
  actual `sbatch --version` line in the smoke's `smoke-sbatch.txt` and confirms it is at least 23.02.3. The runtime
  check alone does not prove NIL support: an older sbatch could read `--export=NIL` as a variable list and still set
  `SLURM_EXPORT_ENV=NIL`.

### Code 7.1's code, at `8da6738a`

| file | sha256 |
|---|---|
| `nd-unfolding/sbatch_pfb.sh` | `5407e3f90ca3755a464346e7e6fd0f200025164dc10b1f97822720e2e25ad168` |
| `nd-unfolding/pfb_smoke_prep.sh` | `307109fee38eab867bc4dd0dd33f0e02198f2b838069d9ff38ff6791bdfd833f` |
| `nd-unfolding/fb_pilot_analyze.py` | `4e1f92b8c3ea056a6f28b66548a1c1dfe75b4893c63d1f40efbaf98230db4b2d` (unchanged from code 7) |
| `nd-unfolding/tests/test_fb_pilot.py` | `a2acdd75b886bfcfe86b6868a82ac1fb0220548527d5c1d1493e05001fa8add6` (83 tests) |
| `nd-unfolding/tests/fb_pilot_mutation.py` | `3f09d061b5a7476e8793fb2b936f40b5693e7237ea88e99d544f9e6a53942add` (151 mutants) |

Edges, gates and probe are unchanged: `439e9226`, `b55ea40d`, `478316c1`.

### Code 7.1's receipts (`receipts.sh 8da6738a`, clean clone)

- `tests_lightgbm.txt`: 83/83 under Python 3.10.20, numpy 2.2.6, LightGBM 4.6.0, scikit-learn 1.7.2.
- `tests_laptop.txt`: 83 run under Python 3.12.2 and numpy 1.26.4, 9 LightGBM tests skipped, OK.
- `mutation.txt`: 151/151 mutants killed by their named tests, with the unmutated suite at 83 and none skipped.
- `syntax.txt`: `bash -n` of both scripts; clone status clean.
