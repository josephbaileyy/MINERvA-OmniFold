# PILOT-FB code 3: the code-2 confirmation audits' findings fixed (receipt)

**By** session tier3-design, under PILOT-FB-BINDING-1 (declaration rev 3 at M_PFB `522ac0b6`). Code 2 (`89be3731`,
receipt `../code2/`) was read by Codex, who returned FAIL, and by Grok, who returned PASS WITH FIXES. Their reports are
`~/codex-reports/pilot-fb-audit/code2/{codex,grok}/report.md`. Code 3 makes every fix the director listed, each with
a test and a mutant. **Nothing has run on the cluster.** The smoke and the job wait for the director's code addendum
(C1) and go.
<!-- absence-ok: an operational status of this tranche, not a claim that a result does not exist -->

## The code, at `ca2da8ea`

| file | sha256 |
|---|---|
| `nd-unfolding/fb_pilot_edges.py` | `439e92262c85a86b4aca6b7e368972d2cc0a12bca3c55eb02e5ec019b927965a` |
| `nd-unfolding/fb_pilot_gates.py` | `b55ea40d3691521248813b1702d7c3442aa7564e9956d1a8d211a1522371cd09` (unchanged) |
| `nd-unfolding/fb_pilot_probe.py` | `c697af661c8263b283fcd8cd47fb67e5e5b0d4a7b2a0bd71416c9b5a4e3f89b4` |
| `nd-unfolding/fb_pilot_analyze.py` | `25d1bd87413585ae12346b73774fdd64398ecba0126e1851eb468b2acb3ea116` |
| `nd-unfolding/sbatch_pfb.sh` | `96edd14a2b85b34dc6d7835212490bfa5dde67f20cd3fc53f1e5521d2b3fd20e` |
| `nd-unfolding/pfb_smoke_prep.sh` | `bcc4758eb3386fa713fd35bceb0278a50419d1779866cbd0ad2c7279813f7b95` |
| `nd-unfolding/tests/test_fb_pilot.py` | `5aaa4794f873b3623371a5b22fd51e294247ddf4692c9085aa2b6435376ed79f` (55 tests) |
| `nd-unfolding/tests/fb_pilot_mutation.py` | `f441398c82bfed5f0921a5f10d255115e07be48c1d384e5f2a3a7b490dfa519c` (96 mutants) |

`setup_salloc_env.sh`, which both scripts source, is pinned in them at
`ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48` (tracked at the repo root).

## The findings and their fixes

| # | finding (severity) | fix | test |
|---|---|---|---|
| 1 | a missing INDEX disabled the identity check (high, Codex; Grok 2) | the run's `edges/INDEX.json` must exist, list the three sets' four roles, and every file it lists must hash as it records. A missing INDEX, sidecar, meta or deploy code fails the binding (PREMISE FAILED (identity)) and never skips it | `test_a_missing_index_or_an_altered_edge_file_fails_identity`, `test_a_sidecar_is_bound_to_its_product` |
| 2 | the job id bound two caller arguments, not the products (high, Codex) | every product's meta must record this job (`slurm_job`, written at `s5p_numerics.py:212`). A product of another job, or with none, means the root was not this job's alone: RUN REFUSED. The status must name the job, the pin and the declared root, and be read from `<root>/job-status.json` or `<stage>/job-<id>.refused.json` | `test_products_of_another_job_are_run_refused`, `test_the_analysis_is_bound_to_one_job` |
| 3 | the smoke's writes were not confined (high, Codex; Grok 5) | see "Write confinement" below | `test_the_smoke_writes_only_under_its_stage`, `test_the_test_switch_cannot_reach_a_real_job` |
| 4 | `PFB_LOCAL_TEST` with `--export=ALL` bypassed the cap, family and root checks (high, Codex; Grok 3) | inside Slurm, any `PFB_` variable refuses, even when empty or `0`. The allocation must be one node. The family, root and stage checks run unconditionally in a job. The local-test mode exists only outside Slurm and refuses cluster paths | `test_the_test_switch_cannot_reach_a_real_job`, `test_the_job_preflight_spends_no_root` |
| 5 | malformed inputs or products erased the named outcome (medium, Codex) | G4 is decided first. If it fails, no product, sidecar, edges file or σ copy is read and INPUTS CHANGED is written. An unreadable product counts as missing (INCOMPLETE, listed), an unreadable sidecar fails its binding, and a statistic that cannot be formed reads INVALID only when no gate outcome applies | `test_a_malformed_artifact_keeps_the_named_outcome` |
| 6 | prep turned the loader's exit 4 into 5 (medium, both) | prep returns the runner's nonzero code unchanged. 5 remains only for "never reached the unfold" | `test_the_prep_step_keeps_the_runners_exit_4` |
| 7 | a gate passed on a product whose meta recorded it failed (medium, Grok 2) | the sidecar's gate bits must equal the product meta's `gates_pass`, or the binding fails and no gate is read from it | `test_a_sidecar_is_bound_to_its_product` |
| low | O_NOATIME staging of σ and the A0 copies | the claim is reworded. This tree does not make the copies; the connect does. The analysis requires each copy to be a plain file at its pin, refusing a symlink or a hard link, so no read here reaches a protected original. Only the two raw inputs are read with `noatime`, and their plain read is allowed by §7 | `test_a_stage_copy_must_be_a_plain_file` |
| low | the cells "S3" divided by ones (Grok 6) | §6 asks for S3 on R00–R15, but the pseudo-data σ is defined on the 153 functionals only (the receipt has 153 entries). The readout is renamed `readouts_cells16_relative_policy_shift` and states its units | `test_a_complete_valid_run_reads_one_row` |
| low | overstated diagnostics (Codex 7) | S1's own INVALID no longer suppresses S2. Each base has its own shift from (e). G0 reports z, n and the gap count when a policy rule fails on finite values. The gate time is renamed `readouts_gate_seconds_in_unfold`, with its scope stated | `test_s2_survives_s1s_own_invalid_and_each_base_has_its_shift`, `test_g0_counts_survive_a_policy_failure` |
| low | open test holes | the row test checks each row's label. The S2 and S3 bars are tested at equality with mutants. The harmless-change test asserts G3 passes and predicts on unseen scored rows | `test_every_combination_reaches_exactly_one_row`, `test_the_bars_include_equality_and_rows_5_7_name_what_crossed`, `test_harmless_changes_…` |

### Write confinement (finding 3)

- **The stage** is a fixed path, `/pscratch/sd/j/josephrb/pfb-20261117-stage`, a sibling of the declared root. Both
  scripts require it exactly. The path must be absolute, contain no `.`, `..` or `//`, not be a symlink, and resolve
  physically (`pwd -P`) to itself. The smoke creates the stage only if its parent exists at that physical path.
- **No bytecode.** `PYTHONDONTWRITEBYTECODE=1` is exported, and exported again after sourcing the setup file.
- **No git index refresh.** The deploy is checked with `git --no-optional-locks status`, so its index is read but never
  refreshed. The test makes the index stat-dirty and checks that its mtime does not move.
- **Slurm's logs** go to the stage: `#SBATCH --output=…-stage/slurm-%j.out` and `--error=…-stage/slurm-%j.err`.
- **The setup file** is checked against its pinned sha256 before it is sourced, with `PYTHONPATH`, `PYTHONHOME`,
  `PYTHONSTARTUP` and `PYTHONUSERBASE` unset. Its return status is checked, and so are the script's own variables
  afterwards. The file's last line is an `export`, so its status rarely fails. The working check on the environment
  is the LightGBM 4.6.0 import that follows, now part of the job's preflight.
- **The smoke's final hash fails its exit status.** Prep exiting 0 without an `INDEX.json` exits 9 and writes no
  receipt. The smoke writes `smoke-receipt.json` (stage, pin, mode, the INDEX's sha256), and the job's preflight
  requires it to match.
- **What the smoke writes** is only under the stage: `smoke-edges/` (or `smoke-edges.g0.json`), `smoke-receipt.json`,
  `smoke-env.log`, `smoke.log` and the runner's empty `smoke-unused/`. The test lists the stage exactly and checks
  that the deploy and the caller's directory gain nothing.
- **The job's preflight** runs entirely before the root is created, including the TimeLimit and the LightGBM check
  (Grok's lows). A preflight refusal is `<stage>/job-<id>.refused.json` with `preflight_refused`, which the analysis
  treats as having no outcome. An existing root alone is `refused` (RUN REFUSED, §5.2). A refusal before the stage
  is validated writes only to stderr.

## Choices for the director

1. **The stage path.** I fixed it at `/pscratch/sd/j/josephrb/pfb-20261117-stage`. It cannot sit inside the root,
   because the root must not exist when the job starts and the stage must exist before it. The `#SBATCH --output`
   lines need a literal path.
2. **`--export=ALL,HOME=…` is kept.** 133 of this repo's sbatch scripts use it, and none uses `--export=NONE`. An
   untested environment change could only be tested by a job. Instead the script no longer trusts the submit
   environment: it refuses any `PFB_` variable, unsets the four Python path variables before sourcing the pinned
   setup file, and checks LightGBM 4.6.0 in preflight. The smoke runs the same unset-and-source sequence on the login
   node, so a broken import shows up at 0 node-h. `--export=NONE` remains an option if you prefer it.
   <!-- absence-ok: an operational choice about a job's environment export, not a claim that a result does not exist -->
3. **Products of another job read RUN REFUSED,** not a refusal to analyze. Such products mean the root was not
   fresh, which is the RUN REFUSED condition in §5.2. A preflight refusal reads no outcome.

## Not covered by these tests

- The TimeLimit check (`scontrol`) and the physical-path check on Perlmutter run only in a real job or smoke. The smoke
  exercises the path check at 0 node-h.
- The real `setup_salloc_env.sh` sources two untracked files in the deploy (`unbinned_unfolding/build/setup.sh`,
  `MINERvA101/opt/bin/setup.sh`) and runs conda's activation hook. Their side effects are not pinned here.
- The empty-fit-column INFEASIBLE (G11) is unchanged. It can only refuse.

## Receipts (`receipts.sh ca2da8ea`, clean clone)

- `tests_lightgbm.txt`: 55/55 under Python 3.10, numpy 2.2.6, LightGBM 4.6.0, scikit-learn 1.7.2.
- `tests_laptop.txt`: 55 run, 9 LightGBM tests skipped, OK.
- `mutation.txt`: 96/96 mutants killed by their named tests, with the unmutated suite at 55 and none skipped.
- `syntax.txt`: `bash -n` of both scripts; clone status clean.
