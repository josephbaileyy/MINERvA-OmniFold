# Local developer tools

Opt-in Python source navigation and a small reviewed test suite. Requires Git and
CPython 3.11. Verified on macOS arm64; Linux/POSIX is intended but unverified.
No default hooks, CI configuration, campaign environments, or launchers change.

## Setup

Work in a separate clone. Use a new development directory outside all checkouts
and campaign output locations. The following commands run from the clone root;
keep `DEV_WORK` set for the rest of this guide.

Create a private virtual environment and install the exact runtime versions:

```sh
DEV_WORK=$(mktemp -d "${TMPDIR:-/tmp}/minerva-dev.XXXXXX")
python3.11 -m venv "$DEV_WORK/venv"
"$DEV_WORK/venv/bin/python" -m pip install --no-cache-dir --no-deps -r tools/developer/requirements.lock
"$DEV_WORK/venv/bin/python" -m pip check
```

Bootstrap downloads packages. Test execution needs no network. All runtime and
transitive dependencies are version-pinned; Python and Git versions remain host
prerequisites and are disclosed in reports where applicable. A virtual environment
isolates dependencies; it is **not a security sandbox**. Run only reviewed code.
Keep environments/reports in private storage and remove them when finished.

## Python navigation

Find the scheduler definition and references within the orchestration source:

```sh
"$DEV_WORK/venv/bin/python" -B tools/developer/navigate.py \
  docs/orchestration/slurm_array_status.py build_snapshot \
  --scope docs/orchestration
```

Find transactional writes and their consumers across PET source and tests:

```sh
"$DEV_WORK/venv/bin/python" -B tools/developer/navigate.py \
  nd-unfolding/pet/atomic_write.py atomic_savez_compressed \
  --scope nd-unfolding/pet --scope nd-unfolding/tests
```

The backend is [Jedi](https://jedi.readthedocs.io/en/v0.19.2/docs/api.html), using
`Script`, `get_references`, and `Name.goto`. It parses source without importing
scientific modules. Explicit import aliases are resolved with Jedi before looking
up their uses. This small wrapper supplies checkout/scope control and JSON output;
it does not maintain a custom symbol graph or service.

`definition` is the selected function/class. `semantic_locations` contains static
Jedi references, import/assignment `binding` sites, and the definition, with
repository-relative filenames, **1-based lines and 0-based columns**.
`unresolved_text_occurrences` contains remaining exact-name text matches, including
comments, unrelated definitions and unresolved calls. They are **not confirmed
references or callers**. Reference locations can also be non-call uses.

Only nonignored Git-listed `.py` files in explicit scopes are copied to a private,
short-lived mirror. Hidden paths, symlinks, nested checkouts and named artifact
directories (see `EXCLUDED` in `navigate.py`) are excluded. No products or non-Python
files are indexed. Scopes also define the ordered Python import roots: use the
actual source directories, not a broad runtime `PYTHONPATH`. Name collisions across
import roots need manual review; split ambiguous scopes into separate queries.
There is no persistent index. Each query rereads current files, including untracked
source and edits, and honors deletions/renames. Reports disclose the checkout,
revision, dirty paths, scopes, file count, and content digest. A concurrent change
during the query causes refusal. Editor buffers must be saved first.

Limitations: Python only; shell and C++ have no semantic support here. Jedi may
stop searching complex references. Runtime dispatch, computed imports, sys.path
mutations, monkeypatches and references outside the selected scopes can be missed
or ambiguous. The supplied environment is not used as an import search path;
third-party semantic resolution is intentionally limited. Do not use this static
result as exhaustive impact analysis or as the sole reason to exclude tests.

## Lightweight tests

Run the manifest's two default suites into a new report directory:

```sh
"$DEV_WORK/venv/bin/python" -B tools/developer/run_tests.py \
  --output "$DEV_WORK/reports"
```

`suites.json` is the explicit admission list. Default suites are `scheduler`
(15 tests at the verified baseline) and `preservation` (3). Repeat `--suite NAME`
to select listed suites. `--timeout SECONDS` limits each suite (default 60).
Arbitrary pytest paths/options and whole-repository discovery are not accepted.
Output directories must be new and outside this checkout.

| Suite | Collection/import/execution review |
| --- | --- |
| `scheduler` | Imports only `slurm_array_status` and stdlib. Every test supplies a fake runner to `build_snapshot`; no Slurm command runs. |
| `preservation` | Imports only `preserve_f17b_record` and stdlib. Synthetic JSON is written, validated and hard-linked only inside each test's private `TemporaryDirectory`; no real evidence is read or written. |
| `open-items` (optional) | Imports the table checker and parser. Reads committed `docs/OPEN_ITEMS.md` as a fixture. Creates scratch Git repositories and hooks, invokes local Git and Python, and mutates only scratch copies. It currently fails on pre-existing malformed rows; no assertion is relaxed. |

All three suites have no required conftests. The worker explicitly disables
conftest discovery, ambient pytest plugins/options and pytest's cache. Each suite
has its own process and only its test directory is added to the Python import
path. Expected module origins are checked against this clone. Suite and imported
source hashes are checked **before collection**: changed code requires reviewing
imports, fixtures, collection and subprocess effects before deliberately updating
`suites.json`. Do not automatically refresh these hashes to make a run pass.
Read-only fixtures and reviewed inputs are hashed in the report and checked again
after execution. Package initializers resolved during collection/import also need
matching reviewed hashes, including newly added `__init__.py` files. Unreviewed
checkout initializers and package initializers from other source trees cause an
import/collection error before execution. Installed environment and standard-library
packages remain trusted. New admission requires the same review, including parent hooks.

The runner constructs a minimal environment with private HOME/temp/cache paths,
disables system/global Git configuration and inherited Git/Python/pytest settings,
and uses the private interpreter for Python subprocesses. Git hook tests keep
Git's child-generated `GIT_INDEX_FILE` intact. The worker and its ordinary child
processes share a new POSIX process group that is killed on timeout and on exit.
SIGTERM/SIGHUP received by the parent while a worker is active are recorded;
a 100 ms polling interval triggers group cleanup, with a five-second worker reap
bound. The parent stops selecting suites and reports exit 143/129 respectively.
SIGKILL cannot trigger cleanup. A fresh private bytecode lookup prefix prevents
existing source caches from overriding admitted source; writes remain disabled.
Ordinary Python children inherit the prefix, but children overriding Python
settings or using isolated mode must be reviewed separately.
A deliberately daemonized child could escape that group: this is not arbitrary-code
containment. No network restriction is installed by the runner itself.

Each run retains `report.json` and per-suite `stdout.txt`, `stderr.txt` and
`counts.json`. Reports include revision, dirty state, interpreter, installed
packages, selected suites, collection/pass/failure/error/skip counts, elapsed time,
exit status, actual import origins and source-status checks. Setup/teardown errors
are counted as errors, not passes. Collection failures are counted separately.
A missing worker report is incomplete, not zero tests passed. An interrupted parent
leaves the pre-execution report with `complete_pass: false` if final reporting
cannot finish; handled SIGTERM/SIGHUP also record `termination_signal`.

Success requires positive collection, every collected test fully passed, verified
origins, unchanged inputs/status and zero worker exits. **No expected skips** are
admitted: skip, xfail, xpass, deselection, zero collection, timeout, missing/wrong
versions and any failure all prevent a complete pass. The parent returns 1 for an
incomplete/failed run (argument errors return 2; handled termination returns
128 + signal number); raw pytest exits are retained.
This is tooling verification, not scientific validation or production admission.

`test_atomic_write.py` was inspected but not admitted: its final test imports
`fullevent_dump_contract`, which imports a loader that inserts a hardcoded cluster
checkout into `sys.path`. Its directory conftest can also skip temp-dependent tests.
Those existing files remain unchanged.

## Verify the tooling itself

Run the bounded acceptance fixtures (runtime lock is sufficient):

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$DEV_WORK/venv/bin/python" -B -m pytest \
  -q -c tools/developer/pytest.ini --noconftest -p no:cacheprovider \
  --basetemp="$DEV_WORK/acceptance-tmp" tools/developer/test_tooling.py \
  tools/developer/test_runner_regressions.py
```

The fixtures exercise duplicate names, import aliases, source changes/deletions/
renames, excluded files and static-only navigation; real failing/empty/skipped/
errored pytest executions; timeout child cleanup; environment contamination;
wrong import origins; missing dependencies; empty selection; admission drift;
existing valid bytecode; newly added and explicitly imported package initializers;
and parent SIGTERM/SIGHUP cleanup. These are reviewed-code checks, not containment
against custom import loaders, direct execution, or concurrent hostile source edits.

Install optional pinned review dependencies and check only the new tooling:

```sh
"$DEV_WORK/venv/bin/python" -m pip install --no-cache-dir --no-deps -r tools/developer/review.lock
"$DEV_WORK/venv/bin/python" -m ruff check --no-cache tools/developer
"$DEV_WORK/venv/bin/python" -m black --check tools/developer
"$DEV_WORK/venv/bin/python" -m mypy --strict --ignore-missing-imports \
  --cache-dir "$DEV_WORK/mypy-cache" tools/developer
```

Jedi has no installed typing stubs; its API boundary uses dynamic types. Existing
scientific sources and repository-wide discovery are outside these checks.
See [VALIDATION.md](VALIDATION.md) for the measured baseline and acceptance results.

See [REVIEW_RESOLUTION.md](REVIEW_RESOLUTION.md) for the independent findings,
before/after regressions, optional failure IDs and fresh-bootstrap limitation.
