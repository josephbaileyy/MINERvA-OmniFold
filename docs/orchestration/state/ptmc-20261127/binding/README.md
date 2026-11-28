# PTMC-BINDING-1: the bound launch scripts and the scorer's PINS.json (2026-11-28)

The merge commit of #1433 is **M = `ace6e5552c3b822dabedc22b16be5de1b04a0d68`**. Its second parent is `87aca5b0c`,
and its `2d-unfolding/ptmc` is identical to that parent's. Everything here was computed from M's objects, with no
value typed. Under `2d-unfolding/ptmc/`, nothing changes except the new `launch/bound/`.

| file | how it was made | record |
|---|---|---|
| `2d-unfolding/ptmc/launch/bound/ptmc_remote.sh`, `ptmc_launch.sh`, `PINS.txt` | `bash 2d-unfolding/ptmc/launch/fill_pins.sh M` | `fill_pins-output.txt` |
| the deploy tree at M (local, not committed) | `make_tree.sh DEST archive REPO /pscratch/sd/j/josephrb/ptmc-20261128/stage` | `make_tree-output.txt` |
| `2d-unfolding/ptmc/launch/bound/PINS.json` (sha256 `bf7a95afa62f21236c62ae219e02a911425bba84ccab3469267148d85407fc68`) | `write_pins_json.py` (this directory) on M and that tree | `write_pins_json-output.txt` (a rerun is byte-identical) |
| the self-checks | `selfcheck_pins.py` (this directory) | `selfcheck-output.txt`: 5 of 5 ok |

## The PINS.json values

- **own**: the sha256 of `git show M:2d-unfolding/ptmc/<f>` for M's `OWN_FILES`: `ptmc_lib.py`, `ptmc_score.py`,
  `ptmc_run.py` and `make_tree.sh`.
- **tree**: the bytes the deploy tree holds, read from a tree that `make_tree.sh` built at M. Each value must equal
  make_tree's own listing.
  - `re2_driver.py` gets make_tree's **built PTMC driver** (`b5c1c9f0…` = `PTMC_SHA`). It does not get a git blob:
    the tree holds M's driver with `oofvc_driver.diff` and `ptmc_driver.diff` applied. The scorer hashes the tree's
    own bytes (`ptmc_score.py:400`, `need(sha256(a.tree / f) == pins["tree"][f], f"C-PINS: the deploy tree's {f}")`). C-PINS compares the runner's recorded driver with the same pin
    (`ptmc_score.py:289`, `need(bfr.get("driver") == pins["tree"][TREE_FILES[0]] and bfr.get("config") == pins["tree"][TREE_FILES[1]]`). The runner records the deploy tree's driver (`ptmc_run.py:549`, `def pins():`).
  - `config.json` is the copy make_tree re-pins to that driver and to the staging root. Its digest therefore depends
    on the string `/pscratch/sd/j/josephrb/ptmc-20261128/stage`. `ptmc_remote.sh`'s `$R` is a literal
    (`ptmc_remote.sh:19`, `R=/pscratch/sd/j/josephrb/ptmc-20261128`), not derived from a date. Its setup builds with
    `ptmc_remote.sh:136` (`PTMC_PY=$PY nice -n 19 bash "$O/make_tree.sh" "$R/deploy" clone "$URL" "$R/stage" > "$R/logs/deploy.log" 2>&1 \`), so the remote config is this one.
- **rows**: M's `CONST["ROWS_SHA"]`, which must equal `ptmc_run.py`'s `PINS["rows"]` and `ptmc_remote.sh`'s
  `ROWS_SHA`.
- **join**: `ptmc_run.py`'s `PINS["join"]`, which must equal `ptmc_remote.sh`'s `JOIN_SHA`.
- **roounfold_lib_sha256**: the built `config.json`'s `inputs.roounfold_lib_sha256`, which the runner checks the
  library against. It must equal `ptmc_remote.sh`'s `LIB_SHA`.

## Scoring later

The local `--tree` given to `ptmc_score.py` must be built the same way, with archive mode at M and the exact staging
string:
`bash 2d-unfolding/ptmc/make_tree.sh <new dir> archive <repo> /pscratch/sd/j/josephrb/ptmc-20261128/stage`.
Any other string gives another `config.json`, and C-PINS STOPs. It would also change the canonical argv's rows path.

## The self-checks (`selfcheck-output.txt`)

`selfcheck_pins.py` imports the scorer's own `check_bytes` from a git archive of M's `2d-unfolding/ptmc`. On the
tree built at M with this PINS.json, the results were:

- It passes.
- A flipped driver digest STOPs with "C-PINS: the deploy tree's 2d-unfolding/re2/re2_driver.py".
- A flipped `make_tree.sh` digest STOPs with "C-PINS: the scorer's own make_tree.sh".
- `PINS.txt`'s `make_tree.sh` value equals PINS.json's `own["make_tree.sh"]`.
- **One limitation.** `check_bytes` also hashes the rows file, and r3's `oofvc_rows.npz` is on pscratch; no local
  copy was used. That clause therefore ran on a labelled stand-in, whose digest temporarily replaced
  `CONST["ROWS_SHA"]`. The PINS.json rows value was checked statically against M's `CONST["ROWS_SHA"]`, which also
  equals the runner's and the remote's rows pins.
