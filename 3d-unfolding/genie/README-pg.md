# COVFIX PG: the two validation truths through F1's GENIE v3 pipeline

`pg_generate.sh` is the one executable that cov2d's bound PG binary runs as a subprocess
(`state/2d-closeout/covfix-20261122/COVFIX-DECLARATION.md` §4.1–§4.2). It runs F1's bound pipeline with only the
tune names and the seeds changed, in F1b′'s single-wave layout (`FD-F1-DECLARATION-AMENDMENT-2.md` §4).

**Status: not ready to bind.** `gen5d_v3.PG_SPLINE_PINS` is empty until PG's probe has run
(`state/2d-closeout/covfix-20261122/pg/probe/`). Until it is filled, `spline-check` refuses every PG tune, so the run
STOPs at its second step. `test_covfix_pg.py::Consistency::test_pg_pins_match_the_probe` checks the filled pins
against the committed probe output.

## Contract

```
cd W && TMPDIR=W/tmp pg_generate.sh --workdir W --seeds W/seeds.json < /dev/null
```

- **The parent** gives it cwd W, `TMPDIR=W/tmp` (existing), stdin `/dev/null`, captured stdout and stderr, and a
  scrubbed environment. It runs on one exclusive CPU node. The parent verifies this file's sha256.
- **seeds.json:** `{"tunes": [{"u": 0, "name": "G21_11b_00_000", "task_seeds": [7 ints]}, {"u": 1, "name":
  "G18_02b_02_11b" | "G18_02a_02_11b", "task_seeds": [7 ints]}]}`. `pg_lib.load_seeds` checks §4.2's rule as far as the
  file allows, since the base is not in it. u0's first seed must be in [1e9, 2e9). Seeds must be consecutive within a
  tune, and u1's first must be u0's + 10,000. Every seed must be below 2³¹ − 1. A refusal names the rule, never the value.
- **Exit:** 0 on success, 1 on a failed step (a STOP), 2 on a refusal before any step (bad arguments, cwd, TMPDIR, an
  existing `W/out`, `W/run` or `W/PRODUCTS.json`, or a deploy that is not `PG_DEPLOY_PIN` or has a modified tracked
  file).
- **Its own stdout and stderr** carry only step names with pass/STOP, task and file counts, timestamps and the host
  name. They carry no seed, no path under W and no physics number. Every sub-step's output goes to `W/out/logs/` or
  `W/out/work/u<u>/t<k>/task.log`.

## Environment it needs

| variable | why |
|---|---|
| `PATH` | at least `/usr/bin:/bin`: bash, git, awk, xargs, `/usr/bin/time`, timeout, sha256sum, find, sort, cmp, hostname |
| `HOME` | `setup_salloc_env.sh` activates `$HOME/.conda/envs/root_6_28`. `setup_genie_v3.sh` reads the compat-lib shim at `$HOME/.genie_compatlibs` |
| `TMPDIR` | must be `W/tmp`. It is re-exported after every environment activation, because `setup_salloc_env.sh` sets `TMPDIR=$SCRATCH/tmp` |
| `PG_DEPLOY_PIN` | the full commit sha the deploy must be at. The executable refuses without it |
| `SCRATCH` (optional) | read by `setup_salloc_env.sh` only for the TMPDIR and CODEX_HOME it sets. TMPDIR is then overridden |
| `GENIE_COMPAT` (optional) | overrides the shim directory, as in F1 |
| `ROOT628_PREFIX`, `ROOT628_CONDA` (optional) | override the analysis environment's location, as `setup_salloc_env.sh` allows |

It needs no network, no `SLURM_*` variable, no passphrase and no GNUPGHOME: encryption is the parent's.

## What it writes (all under W)

- `W/run/`: `queue.txt` (tune, seed and work directory per task; seed-bearing) and the deploy status snapshots.
- `W/out/splines/`: the reduced splines. `W/out/`: the flux file and its JSON, the spline-check JSONs, the gspl2root
  graphs and their logs.
- `W/out/work/u<u>/t<k>/`: each task's gst, `input-flux.root`, `gevgen.log`, `gntpc.log`, `task.log`, `task.time` and
  `gevgen.status`. gevgen names that file `genie-mcjob-<seed>.status`, and it is renamed so that no file name carries a
  seed.
- `W/out/gst/`, `W/out/gen5d/`: the merged gst and the gen5d npz with its meta JSON (f_MEC, the sampling test, the
  counts).
- `W/out/prep/`: `config-pg.json`, `ratios/L-5D-PV/<truth>.json`, `bridged/<truth>.json` and `f1-prep-SHA256SUMS`.
- `W/PRODUCTS.json`: per u, the tune, the truth name and the relative paths of the bridged ratio (what PV applies,
  §3.4), the pvl ratio and the prediction.
- `W/out/PG-SHA256SUMS`: the plaintext sha256 of every product. **It is seed-bearing and must stay inside the seal.**

Nothing is written into the deploy. Python runs with `-B` and `PYTHONDONTWRITEBYTECODE=1`, and the deploy's full
`git status --ignored` is compared before the run, after the environment-using setup steps, and at the end. Any
difference is a STOP.

## Differences from F1, all mechanical

- **No pilot and no budget gate.** PG's price comes from F1b′'s measured timings (director, 2026-11-23). The per-task
  timeout is F1b′'s 5,115 s (`budget3.json`), and the node's wall limit is the parent's.
- **Work directories** are `u<u>/t<k>`, not `s<seed>`, and the status file is renamed (above).
- **The truths** go through `fd_f1_prep.py --truth-set pg`, with the names `genie_v3_g21` and `genie_v3_g18_02b` (or
  `genie_v3_g18_02a`). `--truth-set f1`, the default, is F1's, unchanged.
- **The PG spline pins** are in `gen5d_v3.PG_SPLINE_PINS`, apart from F1's bound `SPLINE_PINS`.
- `setup_genie_v3.sh` and `run_gevgen_v3.sh` gain the three PG qualifier cases. `setup_genie_v3.sh`'s
  `GENIE_XSEC_TUNE` check is unchanged: it requires the product to set the tune asked for, and the probe prints the
  product's UPS lines for it.

## Tests

`python3 -B -m pytest -q nd-unfolding/tests/test_covfix_pg.py` runs `pg_lib.py` and the PG additions on synthetic
inputs. It also runs `pg_generate.sh` end to end against a throwaway git deploy whose GENIE, ROOT and prep steps are
stubs that record their arguments. F1's own `test_fd_f1.py` passes unchanged.
