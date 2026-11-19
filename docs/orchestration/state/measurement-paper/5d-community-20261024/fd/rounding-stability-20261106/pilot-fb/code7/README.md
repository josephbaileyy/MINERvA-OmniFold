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

## Receipts (`receipts.sh 87ab91ba`, clean clone)

- `tests_lightgbm.txt`: 81/81 under Python 3.10.20, numpy 2.2.6, LightGBM 4.6.0, scikit-learn 1.7.2.
- `tests_laptop.txt`: 81 run under Python 3.12.2 and numpy 1.26.4, 9 LightGBM tests skipped, OK.
- `mutation.txt`: 150/150 mutants killed by their named tests, with the unmutated suite at 81 and none skipped.
- `syntax.txt`: `bash -n` of both scripts; clone status clean.
