# COV2D A2, stage 1: the cluster test run PASSES at M a6054769 (attempt 2)

**By** the `cov2d` session, 2026-11-06. This is the first stage of A2's fixed conditional sequence (COV2D-BINDING-2.md,
"Binding 2, addendum A2", revision 2: **M = `a60547692df5f963e428cdfe4661fc51ab785b7b`**, the merge of #817).
- Attempt 1, at `cf533377`, failed on two defects and was not a STOP (`../cluster_tests-attempt1/`).
- The director unfroze exactly their fixes (#817).

**MEASURES:**
- the suites at M in the cluster environments;
- A2's guard tests on Linux;
- the submission's quota check on a login node;
- the fresh deploy.

**CANNOT AUTHORIZE** anything beyond stage 2, which proceeds on this record.

**Verdict: PASS.** 13 of 13 suite runs pass. All four guard tests ran OK on Linux. The deploy is clean at M, and the
quota headroom is at least 2× what AR23's job stages.

## The run

- **The connect:** `connect-a2tests-2.sh`, sha256 `d0bfd1aea9a9fe06c0ddfb211d24d02ff70f5a275dbd2a787db526f50824492f`.
  DIGEST_MATCH, then launched on login02, 05:48:03Z to 05:56:58Z. Its log is `connect-a2tests.log.txt` (`72ea74d6…`,
  the node's digest in `node_and_removal.txt`).
- **Pre-checks:** binding 2's M line for `a6054769` is at column 0 (line 135); `a6054769`'s `2d-unfolding/cov2d` is
  identical to the reviewed code `94544e0b`; A2's sha256 there is `79de07ed…`.
- **The clone:** a fresh clone of GitHub at M, with HEAD asserted. Porcelain before was plain 0, `--ignored` 0; after,
  the same. The audit hook caught 0 guarded reads.

| env | suite | ran | failed | skipped |
|---|---|---:|---:|---:|
| P (omnifold_py310) | `test_cov2d_pseudo` | 20 | 0 | 0 |
| P | `test_cov2d_readouts` | 12 | 0 | 0 |
| P | `test_cov2d_null` | 5 | 0 | 0 |
| P | `test_cov2d_score` | 12 | 0 | 0 |
| P | `test_cov2d_jobs` | 44 | 0 | 1 |
| P | `test_cov2d` | 35 | 0 | 11 |
| R (root_6_28) | `test_cov2d_blocks` | 26 | 0 | 0 |
| R | `test_cov2d_null` | 5 | 0 | 0 |
| R | `test_cov2d_score` | 12 | 0 | 0 |
| RM (root_6_28 + the pinned MAT environment, 6/0) | `test_cov2d_pseudo_write` | 17 | 0 | 0 |
| RM | `test_cov2d_pilot` | 13 | 0 | 0 |
| RM | `test_cov2d_jobs` | 44 | 0 | 0 |
| RM | `test_cov2d` | 35 | 0 | 11 |

The skips are only the expected ones: P's real-parser test (it runs in RM), and the 11 tests of `test_cov2d.Receipt`,
in P and in RM (as in the ruling-5 receipt).

**A2's guard tests, on Linux** (real O_NOATIME, no emulation):

| test | env | |
|---|---|---|
| step A, silent on a clean run | P | RAN-OK |
| step A, fires on a plain read of a private copy | P | RAN-OK (failed in attempt 1; fixed in #817) |
| step B, silent on a clean run | RM | RAN-OK |
| step B, fires on a plain read of a private copy | RM | RAN-OK |

**The deploy:** `/pscratch/sd/j/josephrb/cov2d-deploy-a6054769` was made as a fresh clone at M, with porcelain 0/0
before and after. The `cf533377` deploy is untouched and still clean at its commit (`node_and_removal.txt`).

**The submission's quota check, on the login node** (A2 §3, option (c); `logs/quota_login.log.txt`):
- showquota's row: `|    pscratch |   17.70TiB |    20.00TiB |  88.5% | …`.
- The seven shared inputs AR23's job stages come to 173,261,737,169 bytes, read by stat only.
- `headroom_problem` returns **None**: the headroom of 2.30 TiB is at least 2× the 161.4 GiB to be staged.

**Cleanup:** `/dev/shm/josephrb-cov2d-a2tests2` and its script were removed, rc 0 each, and `/dev/shm` was left empty.
The logs' `SHA256SUMS` were written on the node, and every digest matches its file here. The logs carry a `.txt`
suffix because `*.log` is gitignored.

## The auditor's verdict on #817 (coverage-5b-audit), verbatim

#817 at f2d21c3b (code 94544e0b): no blocker. Posted on the PR.

- **Scope:** only the 8 cov2d files and A2's docs.
- **staged_inputs:** it equals the files steps A and B stage at their defaults, and the sbatch passes no overrides.
- **The gate:** it stats only, and pass requires quota_problem to be None. No read_quota call is left on a compute path.
- **Unreadable or missing showquota:** this fails closed at submission.
- **TMPDIR on pscratch:** step B's ROOT copies are a subset of the staged seven, so the 2× headroom covers them.
- **Run here:**
  - jobs, core and pseudo tests: 87 passed, 12 skipped;
  - your two new quota mutants plus "headroom at 1x": 3 of 3 killed.
