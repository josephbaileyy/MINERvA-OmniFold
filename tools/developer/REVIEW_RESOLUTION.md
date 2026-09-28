# Developer runner review and resolution

Reviewed revision: `05e4200add600694a7f74fda3c0bc5e27bc5f3be`.
Implementation/main baseline: `58ffc4c30699a3355bd132b7a837edd663248c5f`.
Measurements: 2026-09-27, CPython 3.11.15, macOS arm64. The fixes start directly
from the reviewed revision. The last successful fetch observed main at the same baseline; a final fetch was
blocked by GitHub DNS resolution, so later remote changes are unverified. Admitted
source, manifest, runtime pins and scientific inputs are unchanged.

## Independent findings and fixes

All three original findings were P2 correctness defects, independently reproduced
in a separate read-only review. Passing the original 18 acceptance fixtures did
not exclude these defects.

1. **Cached bytecode bypassed admitted source.** The worker used `-I -B`, which
   prevents bytecode writes but still reads valid existing caches. Compiling
   `VALUE = 1`, replacing it with equal-size `VALUE = 2`, preserving its timestamp,
   and admitting the new source allowed an assertion of `VALUE == 1` to pass.
   The report falsely showed complete pass, correct origins and unchanged inputs.
   The worker now uses a fresh private `-X pycache_prefix`; ordinary Python children
   inherit `PYTHONPYCACHEPREFIX`. Existing caches are neither read nor deleted.
2. **New package initializers expanded collection without admission.** Adding only
   `docs/orchestration/__init__.py` to an otherwise exact default-suite fixture
   executed its marker write while all 18 tests passed. `--noconftest` does not
   suppress package initialization. A finder now checks package initializer
   source hashes before normal imports execute them, including implicit pytest
   collection imports, newly added files, and explicit package imports. Packages
   outside the checkout must belong to the interpreter/environment; another source
   tree is refused. Deliberately admitted initializers remain usable.
3. **Parent SIGTERM left ordinary processes running.** Default signal handling
   bypassed cleanup; the worker and its ordinary child survived the parent and the
   child wrote a marker afterward. The persisted incomplete report was correct.
   SIGTERM/SIGHUP now record a termination request without interrupting assignment
   of the process handle. A wait loop checks it every 100 ms, kills the worker
   process group and bounds worker reaping to five seconds. Further suites stop;
   exit status is 128 + signal and the report remains incomplete.

## Durable regression evidence

The executable reproductions are in `test_runner_regressions.py`. They invoke the
public CLI in private synthetic Git repositories and clean up their own probes,
including when run against the defective implementation. No campaign is launched.

| Regression (test name without `test_` prefix) | Reviewed implementation | Fixed implementation |
| --- | --- | --- |
| `cached_bytecode_cannot_override_admitted_source[worker]` | Incorrect assertion passes; regression fails | Source assertion fails as required; corrected assertion passes |
| `cached_bytecode_cannot_override_admitted_source[python-child]` | Child executes stale cache; regression fails | Child executes current source; positive control passes |
| `new_initializer_cannot_expand_default_admission` | Unreviewed marker executes; regression fails | Exact default manifest refuses added initializer; marker absent |
| `imported_package_initializer_requires_admission` | Unreviewed marker executes; regression fails | Refused until hash admitted; admitted control passes; changed hash refused |
| `parent_signal_stops_worker_and_child[SIGTERM]` | Processes survive; regression fails | Worker/child gone, no delayed marker, exit 143, incomplete report |
| `parent_signal_stops_worker_and_child[SIGHUP]` | Processes survive; regression fails | Worker/child gone, no delayed marker, exit 129, incomplete report |
| `initializer_outside_checkout_is_not_an_environment_dependency` | External initializer executes; regression fails | Import refused and marker absent |

The final seven cases against the exact reviewed checkout produced **7 failed in
6.82 s**, all at the expected defect assertions. The fixed combined acceptance run
produced **25 passed in 17.56 s** (18 original plus seven new cases). Signal probes
wait for a worker/child startup handshake, require parent exit within five seconds,
then check both PIDs disappear and the child cannot perform a released write.

To reproduce the before result, keep the fixed tests in the current clone, extract
the reviewed revision to a separate private directory, and point only the runner
source selector at it. Use the private pinned environment from README setup:

```sh
mkdir "$DEV_WORK/reviewed"
git archive 05e4200add600694a7f74fda3c0bc5e27bc5f3be | tar -x -C "$DEV_WORK/reviewed"
DEVELOPER_TOOLING_TEST_SOURCE="$DEV_WORK/reviewed/tools/developer" \
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$DEV_WORK/venv/bin/python" -B -m pytest \
  -q --noconftest -p no:cacheprovider -c tools/developer/pytest.ini \
  --basetemp="$DEV_WORK/before-tests" tools/developer/test_runner_regressions.py
```

Expect seven failures. Unset `DEVELOPER_TOOLING_TEST_SOURCE` and use the README
acceptance command for the after result; expect 25 passes. No old checkout edits
are required. The fixtures import current common helpers for scratch Git setup;
the runner and worker under test are copied exclusively from the selected source.

## Current suite results and optional disposition

| Check | Result |
| --- | --- |
| Default scheduler | 15 collected/passed, zero failures/errors/skips |
| Default preservation | 3 collected/passed, zero failures/errors/skips |
| Default whole run | Complete pass, exit 0, 1.153 s; input hashes/source status unchanged |
| Combined tooling acceptance | 25 passed in 17.56 s |
| Static checks | Ruff, Black and strict mypy passed for all six Python files |
| Optional open-items | 33 collected, 15 passed, 18 failed, zero errors/skips; exit 1, incomplete; input hashes/source status unchanged |

The 18 optional failing IDs match both the previous runner result and the
independent direct-pytest control extracted from pristine baseline main. The
malformed table rows remain `OI-176` (14 fields) and `OI-175` (8), against seven
required. These are pre-existing failures with separate disposition pending;
no assertion, fixture, admission hash, skip policy or scientific input was changed.
They do not automatically block this opt-in tooling and remain visibly failing.

Exact failing IDs (all in `docs/open-items/test_check_open_items_columns.py`):

```text
test_check_open_items_columns.py::test_a_pathspec_commit_is_not_blocked_by_another_lanes_staged_row
test_check_open_items_columns.py::test_an_escaped_pipe_is_one_field
test_check_open_items_columns.py::test_an_unstaged_malformation_does_not_block_the_index
test_check_open_items_columns.py::test_end_to_end_clean_index_exits_zero
test_check_open_items_columns.py::test_every_off_by_n_width_fires_in_both_directions[11]
test_check_open_items_columns.py::test_every_off_by_n_width_fires_in_both_directions[14]
test_check_open_items_columns.py::test_every_off_by_n_width_fires_in_both_directions[3]
test_check_open_items_columns.py::test_every_off_by_n_width_fires_in_both_directions[5]
test_check_open_items_columns.py::test_every_off_by_n_width_fires_in_both_directions[6]
test_check_open_items_columns.py::test_every_off_by_n_width_fires_in_both_directions[8]
test_check_open_items_columns.py::test_fires_on_a_long_row
test_check_open_items_columns.py::test_fires_on_a_renamed_header_at_the_same_width
test_check_open_items_columns.py::test_fires_on_a_reordered_header
test_check_open_items_columns.py::test_fires_on_a_short_row
test_check_open_items_columns.py::test_git_gives_a_partial_commit_its_own_index
test_check_open_items_columns.py::test_scrubbing_git_index_file_reintroduces_the_false_block
test_check_open_items_columns.py::test_self_test_passes_on_a_clean_tree
test_check_open_items_columns.py::test_silent_on_a_good_tree
```

## Fresh bootstrap and remaining limitations

An independent empty venv was created successfully. Installing the unchanged lock
with `--no-cache-dir --no-deps --retries 0 --timeout 10` failed at Jedi. Repeating
with pip `--isolated --index-url https://pypi.org/simple` also exited 1:

```text
ERROR: Could not find a version that satisfies the requirement jedi==0.19.2 (from versions: none)
ERROR: No matching distribution found for jedi==0.19.2
```

A direct `socket.getaddrinfo("pypi.org", 443)` probe returned `gaierror` (Errno 8,
name resolution unavailable). Thus independent fresh package retrieval remains
unverified; these messages do not establish an invalid pin or dependency defect.
Validation used the existing private environment with all six runtime pins present:
Jedi 0.19.2, parso 0.8.4, pytest 8.3.5, iniconfig 2.1.0, packaging 25.0 and pluggy
1.5.0. The earlier successful bootstrap in VALIDATION.md is historical evidence,
not a successful fresh installation for this fix.

Only macOS arm64 was measured; Linux/POSIX remains unverified. SIGKILL cannot run
cleanup, and deliberately daemonized children may escape the process group. Python
children that override cache settings or use isolated mode need separate review.
The import guard covers normal source imports, not hostile custom loaders, direct
execution or concurrent malicious edits. Installed interpreter/environment code is
trusted. A venv is not a security sandbox and the runner adds no network restriction.
Navigation is unchanged: Python-only, static, scoped, and not exhaustive for dynamic
calls or suitable as the sole basis for excluding tests. All changes are confined
to developer tooling; shared checkouts and PET/GBDT campaigns are outside this work.
