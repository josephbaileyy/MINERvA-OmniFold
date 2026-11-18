# PILOT-FB code 4: the code-3 confirmation audits' findings and the director's rulings (receipt)

**By** session tier3-design, under PILOT-FB-BINDING-1 (declaration rev 3 at M_PFB `522ac0b6`). Code 3 (`04cd5f56`,
receipt `../code3/`) was read by Codex (FAIL) and Grok (PASS WITH FIXES); their reports are
`~/codex-reports/pilot-fb-audit/code3/{codex,grok}/report.md`. The director's rulings for code 4:
- reverse choice (ii): use `--export=NONE` and pass only named variables;
- confine writes;
- check protected copies physically and by inode;
- bind the root read;
- fail null edge hashes;
- classify wrong-typed artifacts.

Choices (i) (the stage path) and (iii) (foreign products read RUN REFUSED) stand. Every fix has a test and a mutant.
**Nothing has run on the cluster.**
<!-- absence-ok: an operational status of this tranche, not a claim that a result does not exist -->

## The code, at `f2582535`

| file | sha256 |
|---|---|
| `nd-unfolding/fb_pilot_edges.py` | `439e92262c85a86b4aca6b7e368972d2cc0a12bca3c55eb02e5ec019b927965a` (unchanged) |
| `nd-unfolding/fb_pilot_gates.py` | `b55ea40d3691521248813b1702d7c3442aa7564e9956d1a8d211a1522371cd09` (unchanged) |
| `nd-unfolding/fb_pilot_probe.py` | `478316c13b2d902cebbb56e68c3e2762ecc49f57063a545ff87c0fdf9678e464` |
| `nd-unfolding/fb_pilot_analyze.py` | `630fde0489f2559bc6293d4971315011aa19574bb9d292e0ab5a987337879c06` |
| `nd-unfolding/sbatch_pfb.sh` | `3a2697397cfa5d6e1af52950009f99cfa9ef3bedd6a54c765ab6513da8bd57f9` |
| `nd-unfolding/pfb_smoke_prep.sh` | `84fde405b8c7e2ccd3507536e1b08db59cc6d3236d696ea6e5918b3428baf4d5` |
| `nd-unfolding/tests/test_fb_pilot.py` | `594bd0ccdf1be12d6c6fca27ecb65a24837e3112796a3826460e8e7abb24b7fa` (63 tests) |
| `nd-unfolding/tests/fb_pilot_mutation.py` | `efe45dceb1eaf75d33ba669c63fa0ccec1cad7ae1fb84cd10076223d23277130` (117 mutants) |

## The fixes

| finding | fix | test |
|---|---|---|
| `--export=ALL` cannot be confined; an inherited `BASH_ENV` (Codex 1; the director's ruling on choice ii) | `#SBATCH --export=NONE`. Both scripts share one environment block: they re-execute under `env -i` with a named list (HOME, USER, LOGNAME, PATH=/usr/bin:/bin, SCRATCH, LC_ALL=C, PYTHONDONTWRITEBYTECODE=1 and the three Slurm job variables), and afterwards any other variable refuses. The smoke runs in exactly this environment at 0 node-h and checks for git, sha256sum, python3 and scontrol. Local tests keep their own HOME, PATH and PFB_ variables outside Slurm only | `test_the_environment_is_the_declared_one` |
| a pre-placed link in the stage is written through (Codex 1) | the smoke creates the stage, which must not exist, so it starts fresh and empty. Every file either script creates there is opened `O_CREAT\|O_EXCL\|O_NOFOLLOW`: the env logs, refusal records, smoke logs, receipt, G0 record, sidecar temporaries and status temporaries. The job's `stage-check` refuses any entry except the smoke's files, the copies and the jobs' own logs, and refuses any link anywhere | `test_the_job_writes_through_no_pre_placed_link`, `test_the_stage_inventory`, `test_the_smoke_writes_only_under_its_stage` |
| the analyzer's `--out` is unrestricted (Codex 1) | `--out` must be new and physically under the stage or the run root, and it is created `O_EXCL\|O_NOFOLLOW` | `test_the_analysis_writes_only_a_new_file_under_the_stage_or_root` |
| the setup's dependency closure is unpinned (Codex 1, Grok 4) | the setup is sourced with an xtrace whose PS4 names each sourced file. The receipt records the closure: every sourced file and the conda executable, each with its sha256. The job recomputes it from its own trace and must match | `test_the_job_preflight_spends_no_root` (a changed nested setup file refuses) |
| a symlinked `a0-refs` directory passes (Codex 2, Grok 1) | the copy's realpath must equal its lexical path under the stage's realpath, so a symlink in any component, the leaf included, fails. A copy with a protected original's inode fails too: RS1's `runs/A0/<file>`, and the σ receipt in the deploy and the repo | `test_a_symlinked_a0_directory_or_the_original_inode_fails_g4`, `test_a_stage_copy_must_be_a_plain_file` |
| the root actually read is unbound (Codex 3) | the physical path read must equal the status's and the declared root | `test_the_root_read_is_the_statuss_root` |
| null recorded hashes with missing files pass (Codex 4, new) | every INDEX row must name `<set>_<role>.json`, record a 64-hex sha256 that matches the file as read, and list five features' edges. The INDEX must carry schema `pfb-edges/1` | `test_null_hashes_missing_files_and_a_bad_index_fail` |
| wrong-typed meta erases the outcome (Codex 5) | a meta that is not a JSON object is unreadable, so its product counts as missing (INCOMPLETE). A non-object `pilot_fb` block or sidecar fails its binding. A display-only readout (`rs1_read.json`) that fails is recorded and never removes the statistics | `test_wrong_typed_meta_keeps_the_named_outcome` |
| a `lightgbm.py` could shadow the import (Grok, choice ii) | an untracked `.py` in the deploy's `nd-unfolding/` refuses. The LightGBM check runs with `nd-unfolding/` first on the path, as the tasks do, and logs `lightgbm.__file__` | `test_the_job_preflight_spends_no_root` |
| the smoke's header claimed exit 2 writes nothing (Grok 3) | reworded: a refusal before the stage is created writes nothing; after, it writes only under the new stage | — |

## Order of steps at the connect (for the addendum)

1. The smoke creates the stage at 0 node-h.
2. The connect copies `a0-refs/` (21 files) and `assess_receipt.json` into the stage as plain files.
3. The job runs.

`stage-check` and G4 then refuse anything else in the stage.

## Not covered by these tests

- `scontrol`'s TimeLimit and the Perlmutter physical-path checks run only on the cluster. The smoke exercises the path
  check and the presence of `scontrol`.
- The conda activation hook's own side effects are not pinned beyond its executable's sha256 and the sourced-file
  closure.
- Slurm opens `slurm-%j.out/.err` before the script runs. A pre-placed link there is refused by `stage-check`, but
  only after Slurm has opened it. The stage is fresh, and only this lane writes to it.
- The J2 test still stops at the base rebuild (Grok 2, low; carried).
- The empty-fit-column INFEASIBLE (G11) is unchanged. It can only refuse.

## Receipts (`receipts.sh f2582535`, clean clone)

- `tests_lightgbm.txt`: 63/63 under Python 3.10.20, numpy 2.2.6, LightGBM 4.6.0, scikit-learn 1.7.2.
- `tests_laptop.txt`: 63 run, 9 LightGBM tests skipped, OK.
- `mutation.txt`: 117/117 mutants killed by their named tests, with the unmutated suite at 63 and none skipped.
- `syntax.txt`: `bash -n` of both scripts; clone status clean.
