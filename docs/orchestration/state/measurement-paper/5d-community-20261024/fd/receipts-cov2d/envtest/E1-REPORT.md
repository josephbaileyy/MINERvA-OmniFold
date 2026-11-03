# COV2D connect E1: the cluster-env test receipt. **E1 FAIL**: no test ran (2026-11-03)

**By** the `cov2d` session, under `COV2D-BINDING-1.md` (merged at `95e371700ec57546c459ba029a8e8a616d8ccdee`).
**MEASURES:** that pytest is absent from both cluster envs. **CANNOT AUTHORIZE:** anything; no suite ran.

## The run

- **Script:** `connect-e1.sh`, sha256 `24c9d3cc129b48d284ca5f59bc277f81c9b6419fa7e773143f6bb4fee99f5b7d`, sent to the
  director before it ran and approved. The copy on the node had the same digest.
- **Where and when:** login02, 2026-11-03T18:07:58Z to 18:11:53Z, 0 node-h, no job.
- **What it read and wrote:** a fresh clone at M′ = `c96c97f392f7402791e921ccdac952e74d454cee` (#726's merge) in
  `/dev/shm/josephrb-cov2d-e1`. No pscratch or CFS path was read or written.
- **What it tests:** the code as bound at `dec97852` (#723), with the tests at M′.

## What it found

- **The checkout:** porcelain 0 lines before and after, HEAD = M′.
- **The bound blobs:** 5 of 5 at M′ (`bound.blobs.txt`): `re2_driver.py` 97f26a1d, `cov2d.py` 7dafdd3f,
  `cov2d_receipt.py` d5718bf4, `cov2d_writer.py` 2402ed4b, `fd_1b_null.py` 1810161d.
- **root_6_28:** lightgbm 4.6.0, sklearn 1.8.0, no uproot. `python -m pytest` gave "No module named pytest": rc 1, 0
  passed against 16 expected. FAIL.
- **omnifold_py310:** no ROOT. `python -m pytest` gave "No module named pytest": rc 1, 0 passed against 19 expected.
  The skip check also FAILED, because all 18 expected skips were absent. FAIL.
- **The env listing** (descriptive, a directory listing): `cernroot` has ROOT and no uproot; `omnifold_py310` has
  uproot and no ROOT; `root_6_28` has ROOT and no uproot.
- **Verdict line:** `E1 FAIL`.

**The fail-closed checks worked.** The expected pass counts and the expected-skip set, a condition the director added,
turned an empty run into a FAIL.

**The cause is my preparation.** I checked the ROOT, uproot, LightGBM and scikit-learn imports on the cluster, but
never the test runner. The earlier connects (R1, C1, C2) ran scripts directly and never needed pytest.

**The director accepted E1 FAIL as recorded,** and approved E2: the stdlib runner `python -m unittest -v`, nothing
installed, with an import preflight and per-file guards.

## Removals (the director's instruction)

Logged in `removal.log.txt`, login02, 2026-11-03T18:12:31Z:
- `/dev/shm/josephrb-cov2d-e1` (1.2G): `rm -rf` rc 0;
- `/dev/shm/josephrb-cov2d-e1.sh` (sha256 `24c9d3cc…`): `rm -f` rc 0;
- `ls` then shows neither.

## Files

These are the node's files. `.out` logs are renamed `.txt`, because the repository ignores `*.out`. Contents are
unchanged, and the node's digests of the two test logs are in `connect-e1.log.txt`.

| file | from the node's |
|---|---|
| `connect-e1.sh` | the script as run |
| `connect-e1.log.txt` | `connect-e1.log` |
| `tests_root628.txt`, `tests_py310.txt` | `tests_root628.out`, `tests_py310.out` |
| `tests_py310.skipdiff.txt` | `tests_py310.out.skipdiff` |
| `expected_py310.skips.txt` | `expected_py310.skips` |
| `bound.blobs.txt` | `bound.blobs` |
| `removal.log.txt` | the removal's own output |
