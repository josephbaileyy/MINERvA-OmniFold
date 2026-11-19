# PILOT-FB code 2: the code audits' findings fixed (receipt)

**By** session tier3-design, under PILOT-FB-BINDING-1 (declaration rev 3 at M_PFB `522ac0b6`). Code 1 (`0be8aaac`,
receipt `../code1/`) was audited by two readers. Codex and Grok both read FAIL, on fidelity gaps rather than the design.
Their reports are `~/codex-reports/pilot-fb-audit/code1/{codex,grok}/report.md`. Code 2 makes the director's fixes, each
with a test and a mutant, and adds the declared login-node prep-only smoke. **Nothing has run on the cluster.**
<!-- absence-ok: an operational status of this tranche, not a claim that a result does not exist -->

## The code, at `18c24d35`

| file | sha256 |
|---|---|
| `nd-unfolding/fb_pilot_edges.py` | `4e3b811a830c52ca0045f41f9357c14f39ab554e7faa4f863dd7300d1a02e727` |
| `nd-unfolding/fb_pilot_gates.py` | `b55ea40d3691521248813b1702d7c3442aa7564e9956d1a8d211a1522371cd09` (unchanged) |
| `nd-unfolding/fb_pilot_probe.py` | `64a4c763e587efc7910ac4f18fb50e98f9fcd53cf1b997fcb6de8f899cd0e646` |
| `nd-unfolding/fb_pilot_analyze.py` | `0f0693d87102327e4e64878fb15c5af8274b120563a6afb76cffe1a2b2958919` |
| `nd-unfolding/sbatch_pfb.sh` | `c96363a07edfc33483d756b32a51f1c78f87b81fdd67cdd5c7b179e3bf6b5cee` |
| `nd-unfolding/pfb_smoke_prep.sh` | `6d8d906db044072c456fc07138066d7341b2cddcc94c056322a352cef7641478` (new) |
| `nd-unfolding/tests/test_fb_pilot.py` | `8213d6c21adb8862f1e5a491cc7e2796e6b70ebb5e653b7a10e4e91f38d861fb` (45 tests) |
| `nd-unfolding/tests/fb_pilot_mutation.py` | `71fb27ccbfd68f0ce74873676d2e08939145821f3c5fba210f00c16459f95760` (58 mutants) |

## The findings and their fixes

| # | finding (severity) | fix | test |
|---|---|---|---|
| 1 | placement took the right end of a plateau of B, the regressor's scored-only values (high, both) | the global `argmin` of \|B_k − t_i\|, which returns the lowest k among ties (§3 rule 6) | `test_placement_takes_the_lowest_gap_on_a_plateau` |
| 2 | no `#SBATCH --time`; the 0.9 node-h cap and the job family were not enforced (high, both) | `#SBATCH --time=0:50:00` and `--job-name=pfb_run` are in the script. The job refuses unless Slurm's TimeLimit is at most 0:50:00 (`fb_pilot_analyze.py slurm-limit`) and its name starts `pfb_` | `test_the_slurm_limit_and_the_scripts_cap`, `test_the_job_refuses_…` |
| 3 | G4's analysis check omitted the inputs and the deploy, and an input exit lost its name (high) | the analysis re-hashes `of_inputs_5d.npz` and `bkg_dump.npz` (O_NOATIME where the platform has it), the deploy at its pin (clean), RS1's A0 copies and the σ copy. A task's exit 4 is INPUTS CHANGED | `test_g4_rechecks_…`, `test_exits_4_and_5_…` |
| 4 | identity came from the first fit only, and sidecars were not bound to products (high) | identity is recorded at every fit, with the forced file's sha256 read at that fit. Each sidecar names its product's sha256, set, seed, edges INDEX and code. The analysis checks all of them against the product's meta, `INDEX.json` and the deploy; an unbound sidecar is PREMISE FAILED (identity), after G1 and J | `test_identity_is_every_fit_…`, `test_a_sidecar_is_bound_…` |
| 5 | exit 5, a bad digest and mixed failures broke the precedence (medium) | after each round, exit 4 is INPUTS CHANGED and exit 5 is RUN REFUSED (§5.2 item 2). Any other failure is an operational interruption that outranks the gates. Only a clean round reaches the round-1 gate | `test_exits_4_and_5_and_operational_failures_keep_their_place` |
| 6 | S1's INVALID crashed the reader, and a non-finite endpoint could not be written (medium) | INVALID reads INVALID, and the flag wins over any band. Non-finite numbers are written as null, with their places listed | `test_s1_invalid_reads_invalid_…` |
| 7 | a gate stop discarded computable statistics (medium) | each statistic is computed from its own inputs. S3 and the shifts need only the bases, so they survive a round-1 stop | `test_base_only_statistics_survive_a_round1_stop` |
| 8 | freshness and status handling changed the bound rule (medium) | a separate stage holds the connect's O_NOATIME copies and the smoke's edges. The run root is the declared `/pscratch/sd/j/josephrb/pfb-20261117`: it must not exist, and the job creates it (§4, literally). A refusal is recorded as `<stage>/job-<id>.refused.json`, and the analysis is bound to one job id | `test_the_job_refuses_…`, `test_the_analysis_is_bound_to_one_job` |
| 9 | the σ receipt was a plain read (medium, Grok) | it is the stage's O_NOATIME copy, checked against its pin | `test_g4_rechecks_…` |
| low | G0 named the first failure only; readouts were missing | G0 records every role and feature's z, n, admissible-gap count and first failing rule, and writes no edges when it refuses. The readouts add S3 on the 16 cells, the E1–E2 edge differences, the time per unfold and the gate overhead | `test_g0_records_every_role_and_feature` |

**The six README choices (code 1).**
- Grok finds choices 1–4 decided by the declaration.
- Choice 5 (identity) follows Grok's reading and the director's ruling: identity now carries the file's digest at every
  fit (fix 4).
- Choice 6 (a refused root) follows Grok's fix: the refusal record is per job id in the stage, and the analysis takes one
  job's status (fix 8).

**The login-node prep-only smoke** (`pfb_smoke_prep.sh`, both readers' request) is a declared step before the job. It
runs the prep step alone on a login node: no sbatch, no fit, 0 node-h. It writes `<stage>/smoke-edges/` or, on
INFEASIBLE, G0's full record. It refuses inside a Slurm job. The job's prep must then reproduce the smoke's
`INDEX.json` byte for byte; if it does not, the job reads INPUTS CHANGED. The smoke does not exercise the fits, J, G2 or
G3: round 1 remains their first contact with the real pipeline.

## The receipts, in a clean clone at `18c24d35` (`receipts.sh`, sha256 `c18a63bd…`)

| file | result |
|---|---|
| `tests_lightgbm.txt` | Python 3.10.20, numpy 2.2.6, LightGBM 4.6.0, scikit-learn 1.7.2: 45 tests OK, none skipped, exit 0 |
| `mutation.txt` | the same venv. The unmutated suite: 45 OK, none skipped. Mutation check PASS: 58 of 58 killed, each by its named test |
| `tests_laptop.txt` | Python 3.12.2, numpy 1.26.4, no LightGBM: 36 OK and 9 skipped (the LightGBM tests), exit 0 |
| `syntax.txt` | `bash -n` on `sbatch_pfb.sh` and `pfb_smoke_prep.sh`: exit 0. The clone is clean after the run |

The job script's refusal paths now run locally (`PFB_LOCAL_TEST`, a scratch deploy): a stage that lacks its copies, a
root that exists, a root that is not the declared one, and a job name outside `pfb_`. The smoke's refusal inside a Slurm
job also runs.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the code's shas, the fixes listed and these receipts.
- **Not citable for:** any PILOT-FB reading. No note or paper wording follows from this code.
