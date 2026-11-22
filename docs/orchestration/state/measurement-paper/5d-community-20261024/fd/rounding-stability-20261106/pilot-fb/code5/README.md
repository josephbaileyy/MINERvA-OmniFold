# PILOT-FB code 5: the director's code-4 rulings (receipt)

**By** session tier3-design, under PILOT-FB-BINDING-1 (declaration rev 3 at M_PFB `522ac0b6`). Code 4 (`cc38f157`,
receipt `../code4/`) was read by Grok (SMOKE PASS, JOB PASS WITH FIXES) and Codex (FAIL on both); the reports are in
`~/codex-reports/pilot-fb-audit/code4/{codex,grok}/report.md`. The director ruled that two narrow fixes were needed:
check values as well as names with a clean first shell, and classify a status of the wrong type, with the INDEX
policy fields checked too. The rest is accepted as residual risk. Every fix has a test and a mutant. **Nothing has run
on the cluster.**
<!-- absence-ok: an operational status of this tranche, not a claim that a result does not exist -->

## The code, at `85ae54be`

| file | sha256 |
|---|---|
| `nd-unfolding/fb_pilot_edges.py` | `439e92262c85a86b4aca6b7e368972d2cc0a12bca3c55eb02e5ec019b927965a` (unchanged) |
| `nd-unfolding/fb_pilot_gates.py` | `b55ea40d3691521248813b1702d7c3442aa7564e9956d1a8d211a1522371cd09` (unchanged) |
| `nd-unfolding/fb_pilot_probe.py` | `478316c13b2d902cebbb56e68c3e2762ecc49f57063a545ff87c0fdf9678e464` (unchanged) |
| `nd-unfolding/fb_pilot_analyze.py` | `577288a0965cb5ec0780925b9ece7566eaeaac539c30675abdee5f7729ebb055` |
| `nd-unfolding/sbatch_pfb.sh` | `4296242afd331ca79099c04ea32625044801dfbb7151c873e4287c6a8b6ff0a6` |
| `nd-unfolding/pfb_smoke_prep.sh` | `65b5ffc9757ec213cb7fa826c56e79bc0e64b76f0e962a37ae49674e1d711d62` |
| `nd-unfolding/tests/test_fb_pilot.py` | `a9b19a37677ab62ff533f4b04b5efddadd9a71572ac38e632df3efd1059f6b93` (73 tests) |
| `nd-unfolding/tests/fb_pilot_mutation.py` | `fd374c82255c559567c16c8d43541e324cf4e2d1294ffc48c9f930a900b62264` (128 mutants) |

## The reviewed launch commands (for the connect and the C1 addendum)

**The smoke**, on a login node, from a clean shell. `env -i` clears the environment, so no BASH_ENV runs in the
first shell:

```
env -i HOME=/global/homes/j/josephrb PATH=/usr/bin:/bin /bin/bash --noprofile --norc <deploy>/nd-unfolding/pfb_smoke_prep.sh <deploy> <pin> /pscratch/sd/j/josephrb/pfb-20261117-stage
```

**The job.** `env -i` clears the environment, so no SBATCH_EXPORT can override `#SBATCH --export=NONE`:

```
env -i HOME=/global/homes/j/josephrb PATH=/usr/bin:/bin sbatch <deploy>/nd-unfolding/sbatch_pfb.sh <deploy> <pin> /pscratch/sd/j/josephrb/pfb-20261117-stage /pscratch/sd/j/josephrb/pfb-20261117
```

The job's first shell is the script's shebang, `#!/usr/bin/env -S -u BASH_ENV -u ENV /bin/bash --noprofile
--norc`, so a BASH_ENV in the batch environment never runs. The script refuses if Slurm reports a
`SLURM_EXPORT_ENV` other than `NONE`.

Both commands assume Slurm's tools are on `/usr/bin:/bin`. The smoke checks this for `scontrol`, at 0 node-h, before
the job is submitted. If `sbatch` sits elsewhere on Perlmutter, the connect names its absolute path in the same
`env -i` command.

## The fixes

| ruling | fix | test |
|---|---|---|
| 1. values, not only names; no inherited marker bypass; re-check after setup | the environment block checks each value whatever `PFBCLEAN` says: HOME, PATH, USER, LOGNAME, SCRATCH, `LC_ALL=C` and `PYTHONDONTWRITEBYTECODE=1`. A missing value refuses too. After the setup, a denied variable refuses (exit 97): BASH_ENV, ENV, PYTHONHOME, PYTHONSTARTUP, PYTHONPYCACHEPREFIX, PYTHONUSERBASE, PYTHONINSPECT, GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE. The smoke receipt records the names the setup leaves exported, and the job must reproduce them | `test_the_environment_values_are_checked_whatever_the_marker`, `test_the_setup_may_not_export_a_denied_variable`, `test_the_job_preflight_spends_no_root` (a name the smoke's setup did not leave refuses) |
| 2. a clean first shell; SBATCH_EXPORT (Grok) | the shebang above, the two reviewed launch commands, and the `SLURM_EXPORT_ENV` check | `test_the_first_shell_starts_clean` (a BASH_ENV hook never runs when either script is executed through its shebang; the reviewed smoke launch runs), `test_the_test_switch_cannot_reach_a_real_job` (`SLURM_EXPORT_ENV=ALL` refuses) |
| 3. a status of type `[]`; INDEX policy (Codex 4) | a status that is not a JSON object refuses with its reason and never raises `AttributeError`. INDEX's `K` must equal `fb_pilot_edges.K`, and each set's `max_bin` and `offset` must equal `fb_pilot_edges.SETS` | `test_a_status_of_the_wrong_type_is_classified`, `test_the_index_policy_fields` |

## Accepted as residual risk (the director's ruling; to be stated in C1)

- **The conda and setup hooks' side effects under the declared HOME.** Every prior campaign used this same setup. The
  closure from the xtrace is an inventory, not confinement: a sourced file that runs `set +x` leaves no path.
- **Slurm opens `slurm-%j.out/.err` in the stage before stage-check runs.** A pre-placed link there is detected and
  refused, not prevented.
- **The live TimeLimit string** is first seen on the job. The check fails closed.

Carried from code 4: the J2 test stops at the base rebuild, and the empty-fit-column INFEASIBLE (G11) is unchanged.

## Receipts (`receipts.sh 85ae54be`, clean clone)

- `tests_lightgbm.txt`: 73/73 under Python 3.10.20, numpy 2.2.6, LightGBM 4.6.0, scikit-learn 1.7.2.
- `tests_laptop.txt`: 73 run under Python 3.12.2 and numpy 1.26.4, 9 LightGBM tests skipped, OK.
- `mutation.txt`: 128/128 mutants killed by their named tests, with the unmutated suite at 73 and none skipped.
- `syntax.txt`: `bash -n` of both scripts; clone status clean.
