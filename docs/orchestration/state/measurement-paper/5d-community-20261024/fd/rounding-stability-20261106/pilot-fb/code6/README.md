# PILOT-FB code 6: the director's code-5 rulings F1–F6 (receipt)

**By** session tier3-design, under PILOT-FB-BINDING-1 (declaration rev 3 at M_PFB `522ac0b6`). Code 5 (`98a3e0cc`,
receipt `../code5/`) got a confirmation read (codex-school, SMOKE FAIL, JOB FAIL;
`~/codex-reports/pilot-fb-audit/code5/codex/report.md`). The director ruled this the last code round with open scope:
F1–F6, each with a test and a mutant. The next confirmation read checks only F1–F6 and regressions. **Nothing has run
on the cluster.**
<!-- absence-ok: an operational status of this tranche, not a claim that a result does not exist -->

## The code, at `47e67884`

| file | sha256 |
|---|---|
| `nd-unfolding/fb_pilot_edges.py` | `439e92262c85a86b4aca6b7e368972d2cc0a12bca3c55eb02e5ec019b927965a` (unchanged) |
| `nd-unfolding/fb_pilot_gates.py` | `b55ea40d3691521248813b1702d7c3442aa7564e9956d1a8d211a1522371cd09` (unchanged) |
| `nd-unfolding/fb_pilot_probe.py` | `478316c13b2d902cebbb56e68c3e2762ecc49f57063a545ff87c0fdf9678e464` (unchanged) |
| `nd-unfolding/fb_pilot_analyze.py` | `3a3750b1c950565f8399d364cbaec43251c1cd61bc3b4070adf20d0c3a995db8` |
| `nd-unfolding/sbatch_pfb.sh` | `8055dcb59baa5275ba086fb544d9758537c39b414205c8d5d84583dd94d5818c` |
| `nd-unfolding/pfb_smoke_prep.sh` | `bfbeb49b524770d7676acff168e08475ef3f990a6cfd8738beaa8d775fa99e27` |
| `nd-unfolding/tests/test_fb_pilot.py` | `5b1e7bf4133c28fc7672027f169f5bb2689b450458848cf52ca5526b0a646699` (75 distinct tests) |
| `nd-unfolding/tests/fb_pilot_mutation.py` | `20a1af3f744b446b75dad7ca67f6516ad7123bef8be1e0714e0cb254bee4d73b` (141 mutants) |

## The reviewed launch commands (the only approved entry; for the connect and C1)

**The smoke**, on a login node. The guard refuses inside an allocation before `env -i` clears `SLURM_JOB_ID`:

```
[ -z "${SLURM_JOB_ID-}" ] && /usr/bin/env -i HOME=/global/homes/j/josephrb PATH=/usr/bin:/bin /bin/bash --noprofile --norc <deploy>/nd-unfolding/pfb_smoke_prep.sh <deploy> <pin> /pscratch/sd/j/josephrb/pfb-20261117-stage
```

**The job.** `env -i` means no SBATCH_EXPORT reaches sbatch, and `#SBATCH --export=NIL` creates no login
environment on the node:

```
/usr/bin/env -i HOME=/global/homes/j/josephrb PATH=/usr/bin:/bin sbatch <deploy>/nd-unfolding/sbatch_pfb.sh <deploy> <pin> /pscratch/sd/j/josephrb/pfb-20261117-stage /pscratch/sd/j/josephrb/pfb-20261117
```

The smoke confirms at 0 node-h that `scontrol` and `sbatch` are on `/usr/bin:/bin` and that this sbatch supports NIL.
If `sbatch` sits elsewhere, the connect names its absolute path inside the same `env -i` command.

## The fixes

| ruling | fix | test |
|---|---|---|
| **F1** (High, job): `--export=NONE` triggers `--get-user-env` | `#SBATCH --export=NIL`. Slurm's manual says "Unlike NONE, NIL will not automatically create a user's environment using the --get-user-env mechanism", and lists `SLURM_EXPORT_ENV` under OUTPUT ENVIRONMENT VARIABLES ("Same as --export"). The job refuses unless `SLURM_EXPORT_ENV` is exactly `NIL`, so `NONE`, `ALL` or an unset value all refuse. The smoke records `sbatch --version` and `sbatch --help` in `smoke-sbatch.txt`. It accepts NIL if the help names it, or if the version is at least 23.02.3, the release that added it (SchedMD `CHANGELOG/slurm-23.02.md`: "sbatch - Added new --export=NIL option", under 23.02.3). Otherwise it exits 8, a STOP for the director. Nothing is submitted | `test_the_job_requires_export_nil`, `test_the_smoke_confirms_nil_without_submitting`, `test_the_test_switch_cannot_reach_a_real_job` |
| **F2** (smoke regression): `env -i` strips `SLURM_JOB_ID` | the documented line is prefixed `[ -z "${SLURM_JOB_ID-}" ] &&`. The test runs that line itself: inside an allocation the smoke never starts, and outside it does | `test_the_documented_smoke_launch_refuses_inside_an_allocation` |
| **F3**: interpreter and git startup | `PYTHONNOUSERSITE=1`, `GIT_CONFIG_NOSYSTEM=1` and `GIT_CONFIG_GLOBAL=/dev/null` are declared, value-checked, and restored after setup, so every python3 call runs without the user site. Every git call runs `-c core.fsmonitor=false`, in the scripts through `pgit` and in G4 through `GIT` and `git_env()`. The job's LightGBM check (`fb_pilot_analyze.py lgbm-check`, run from `nd-unfolding/` as the tasks run) records the version, path, numpy and interpreter. It asserts 4.6.0, resolved under `/global/homes/j/josephrb/.conda/envs/root_6_28` (setup_salloc_env.sh's `ROOT628_PREFIX`). The launches call `/usr/bin/env` | `test_user_site_and_git_config_are_off` |
| **F4**: values, not names | after setup, `setup_env_text` (bash builtins only) records PATH, PYTHONPATH, LD_LIBRARY_PATH, LD_PRELOAD, CONDA_PREFIX, CONDARC, PYTHONNOUSERSITE and every GIT_CONFIG_*. The smoke writes them to `smoke-setup-env.txt`, whose sha256 is in the receipt. The job reproduces them exactly, before the live limit, stage and receipt checks run any setup-selected tool | `test_the_setup_values_are_reproduced_before_any_setup_tool` (a changed PATH refuses, and refuses before a simultaneous stage-check failure) |
| **F5** (low) | the module-level `_cls` alias is deleted, so Rev5 is no longer collected twice: the suite has 75 distinct tests, and the harness expects 75. INDEX's `max_bin` and `offset` must have the declared type as well as value, so a JSON `false` is not `0.0`. `K` must be a float equal to `fb_pilot_edges.K`; no boolean can equal it, so its type mutant would be equivalent and is not listed | `test_boolean_policy_fields_fail` |
| **F6**: J2's jitter rebuild | the run-mode jitter rebuild is pinned: `build_pseudo(ji, jb, truth, amplitude, split_key, pseudo_seed, ratio)` on the jittered inputs and background, after the base rebuild on the unjittered ones | `test_j2_rebuilds_the_jitter_from_the_jittered_sources` |

## Accepted, for C1 to state (the director's rulings; detection only, not to be re-raised)

- The conda/setup closure's side effects and incomplete pre-execution inventory.
- Slurm opening `slurm-%j.out/.err` in the stage before stage-check.
- The live TimeLimit, first seen on the job; the check fails closed.
- `bash script` invoked without the shebang. The reviewed launches are the only approved entry.
- The dynamic loader's own environment ahead of `env -i`. The launch calls `/usr/bin/env` by absolute path, and the
  job's values come from F4.
- INDEX feature content: the job reproduces the smoke's INDEX bytes, which the prep produced.
- An empty fit column is classified INFEASIBLE.
- The external O_NOATIME copier, which is connect-side and audited at the connect.
- Cell S3 and the gate-overhead labels: C1 states the "relative shift" reading and the timing limits, against the
  declaration's §6 (lines 372 and 375).
- `--stage` unbound in the analyzer beyond the root check.

## Receipts (`receipts.sh 47e67884`, clean clone)

- `tests_lightgbm.txt`: 75/75 under Python 3.10.20, numpy 2.2.6, LightGBM 4.6.0, scikit-learn 1.7.2.
- `tests_laptop.txt`: 75 run under Python 3.12.2 and numpy 1.26.4, 9 LightGBM tests skipped, OK.
- `mutation.txt`: 141/141 mutants killed by their named tests, with the unmutated suite at 75 and none skipped.
- `syntax.txt`: `bash -n` of both scripts; clone status clean.
