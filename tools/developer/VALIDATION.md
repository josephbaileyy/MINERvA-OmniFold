# Developer tooling validation

Measured on 2026-09-27. Implementation baseline:
`58ffc4c30699a3355bd132b7a837edd663248c5f`, observed as remote `main` before
implementation. The handoff inspection baseline
`c496135f992fc22eb2d89816a9de1b5b844c5872` was present and matched the shared local
checkout. A separate clone fetched and checked out the observed remote commit.
The selected source/tests were unchanged between those revisions; no equivalent
navigation or isolated developer runner was found in the remote tree.

No delivery commits were created. All additions are under `tools/developer/`.
Tracked files, Git index, hooks and configuration in the shared checkout were
unchanged; its original untracked plans remained present. Both implementation and
fresh validation clones had no tracked/staged diff. Validation did not contact a
cluster, launch scientific compute, or change campaign/evidence/publication files.

## Environment and execution

Fresh clone at the implementation baseline, with the tooling files copied in;
fresh CPython 3.11.15 venv installed using exactly `requirements.lock` with
`pip install --no-cache-dir --no-deps`. `pip check`: no broken requirements.
Platform: macOS 26.6.2 arm64; Git 2.39.3 (Apple Git-146). No other platform was tested.

The exact bootstrap/query/test command forms are in [README.md](README.md).
The following additional offline command was executed from the fresh clone with
`DEV_WORK` referring to its private environment/report storage:

Run the default suite with all network access denied:

```sh
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  "$DEV_WORK/venv/bin/python" -B tools/developer/run_tests.py \
  --output "$DEV_WORK/offline-reports"
```

A negative control under the same profile used `socket.connect_ex` to loopback
port 9; it returned `EPERM` (1), confirming network denial rather than merely an
unused connection. This proves offline execution for the admitted suites on the
tested platform, not filesystem/process containment or safety of arbitrary tests.

| Check | Observed result |
| --- | --- |
| Default `scheduler` | 15 collected, 15 passed; 0 failed/errored/skipped; 0.184 s |
| Default `preservation` | 3 collected, 3 passed; 0 failed/errored/skipped; 0.131 s |
| Whole default run | Complete pass, exit 0; 0.650 s including metadata/preflight; source status and input hashes unchanged; actual imports from the fresh clone |
| Tooling acceptance fixtures | 18 passed in 6.84 s in the fresh environment |
| Optional `open-items` investigation | 33 collected: 15 passed, 18 failed, 0 errored/skipped; parent exit 1; 4.668 s for this suite |
| Static checks on five new Python files | Ruff clean; Black check clean; mypy strict clean with untyped Jedi imports allowed |

The optional table suite reports existing malformed rows in `docs/OPEN_ITEMS.md`:
`OI-176` at line 97 has 14 fields and `OI-175` at line 100 has 8 fields, against
7 required. A representative failure was:

```text
AssertionError: assert ['docs/OPEN_I... it as `\\|`'] == []
docs/OPEN_ITEMS.md:97: 14 fields, expected 7 [OI-176]
```

Reproduce the existing defect with `run_tests.py --suite open-items --output` and
a new external output directory. It remains optional and reports failure;
no test assertion, source fixture, threshold or ledger was altered.

## Navigation

Both documented real queries succeeded in the fresh environment. Every returned
semantic location was checked against the corresponding source line and column.
Definitions and representative consumer statements/imports were also inspected.

| Query | Scope/result |
| --- | --- |
| `build_snapshot` | 95 Python files; definition `docs/orchestration/slurm_array_status.py:125`, column 4; 23 semantic locations and 9 text-only occurrences. Representative consumer: `docs/orchestration/dashboard_collector.py:623`, column 23. |
| `atomic_savez_compressed` | 270 Python files; definition `nd-unfolding/pet/atomic_write.py:141`, column 4; 32 semantic locations and 6 text-only occurrences. Representative import: `nd-unfolding/pet/extract_fullevent_fps.py:89`; calls: lines 616 and 659. |

These counts describe the selected static scopes, not a complete call graph.
Semantic locations include definitions and bindings. Remaining exact-name text
occurrences include comments and monkeypatch-related code. Runtime replacement of
`atomic_savez_compressed` in `train_fullevent_replica.py` needs manual reasoning;
the tool does not establish which callable executes at runtime.

Fixtures independently exercised duplicate definitions in separate modules, an
import alias and its call, uncommitted line changes, rename to an untracked path,
deletion and refusal after target deletion. The content digest changed after an
edit. A source module containing an import-time write did not execute that write.
Symlinks, nested checkout source and artifact/hidden directories were excluded.

## Failure-path coverage

The acceptance fixtures invoke real pytest subprocesses on temporary source:

- A passing test gives a complete pass; a failed assertion gives failure.
- Empty collection, collection import failure, test skip, module-level skip,
  xfail and xpass all give incomplete/failing results.
- Setup and teardown errors count as errors; a successful call followed by a
  teardown error does not count as passed.
- A timeout returns 124 at suite level and cannot pass. The fixture proves its
  child was started, then verifies that child cannot perform a delayed write.
- Ambient `PYTEST_ADDOPTS`, `PYTHONPATH` and `GIT_DIR` do not alter the worker;
  a wrong expected import origin prevents success even with a passing test.
- Public-CLI fixtures return 1 and retain an error report for an empty manifest
  selection, missing dependency and missing admitted source.
- A passing test that edits its already-untracked input leaves Git's dirty-path
  list unchanged; the input-content check still detects it and returns failure.

Raw execution reports and stdout/stderr are generated outside the checkout and
are intentionally not committed. The commands and acceptance fixtures reproduce
these checks without production artifacts. Only runtime versions are locked;
interpreter, Git and platform identity remain explicit prerequisites.
