# RDX c1 fix: the checkers under omnifold_py310, behind a fail-closed env check (receipts, for the audit delta)

**By** session tier3-design, within the director's approved outline of 2026-11-15, after the c1 STOP
(`../run-c1-20261115/`), with the director's addition: chkenv pinned by a test and mutants. Code HEAD `d2bd5479`
(the fix at `44d2170c`, the pin at `d2bd5479`). Only these five files change from M_RDXS:

| file | sha256 at M_RDXS | sha256 now |
|---|---|---|
| `nd-unfolding/rdx/rdx_connect.sh` | `11e7ef921bcc227255200347277d7b976d927c5fee2824dd613d31896c968827` | `eae946894be8ce02354e8bd6aaf038d78bd8f574772a359b90eaeb0d1dfd985d` |
| `nd-unfolding/rdx/rdx_connect_launch.sh` | `165fb98ebed89cf8fabd76d13c9bdc671c9ae5ca27c2377055c89d2760e0fb55` | `602c728a7b4326f2146bc219ec88ffb5da145869e81df9f4c1e214022e94212b` |
| `nd-unfolding/rdx/smoke_rdx_stages.sh` | `676bff5125548481b88a71986dc7625ea268ffb836b6ff845508d8502c3f1280` | `f02ca57acdfab743dc4774393d6d2742e07c1dd9badfdb0f639a152737511a54` |
| `nd-unfolding/rdx/test_rdx_stages.py` | `d19068d15ae7d09c1343a4433e5d85e641809c70a5e0b1814358ebdc5878de5f` | `b40f5beeb0cea98cfceb3451f9f9342986a1f779bd35ba946701f02ec69f4681` |
| `nd-unfolding/rdx/rdx_mutation_stages.py` | `4bfea59830bd707cfe68f2c7583ccbc2c386f07218ee5d88ca7e69e2109bf9e9` | `bc06bf00dc8326f28ce36c921873b6d77ddcd687c7cd1dd8a0523c3f17de51b6` |

No checker, job script or other file changes. The deploy stays at M_RDXS: the cluster's deploy is HEAD `ad0535c4`
with porcelain 0 (`../run-c1-20261115/envprobe.session.txt:2`), and the checkers' code there is what runs.

## The change

**`rdx_connect.sh`:**
- `CHKPY` = omnifold_py310's python. It runs `rdx_align.py` and `rdx_truthx_rows.py` (in c1 and c2) and
  `rdx_truthx_npz.py` (in cm). Each needs uproot and numpy and no ROOT: `omnifile_io` imports uproot, and
  `compare_omnifiles` imports ROOT only inside `read()`, which the checkers never call.
- The walk probe stays under `setup_salloc_env` (it imports ROOT), and provenance (s0) stays under root_6_28.
- `chkenv()` runs at the head of c1's checks, of c2 and of cm. It STOPs unless `CHKPY` imports uproot, numpy and the
  deploy's `omnifile_io` and `compare_omnifiles`, with `read_latest` and `same`. It replaces c1's old
  `$PY -c "import uproot"` line.

**`rdx_connect_launch.sh`:** the new connect sha256 only.

**`smoke_rdx_stages.sh`:**
- the checker stub fakes only the checkers' output. The connect's env check runs for real under python3, against the
  committed `omnifile_io.py` and `compare_omnifiles.py`, copied from git into the smoke deploy at the paths the check
  imports them from;
- `SMOKE_CHK=nouproot` hides uproot from that check;
- the root_6_28 stub no longer answers anything but provenance, so a checker routed back to `$PY` would fail in the
  smoke;
- new cases: c1, c2 and cm each STOP with a checker python that cannot import uproot, and cm passes.

**`test_rdx_stages.py`** (16 → 18 tests), class `CheckerEnv`:
- `test_every_checker_runs_under_chkpy_behind_chkenv`, a static test:
  - `CHKPY` is omnifold_py310's python;
  - chkenv's invocation is `$CHKPY -I -B - "$DEP" <<'EOF' || stop`, and it imports numpy, uproot, `omnifile_io` and
    `compare_omnifiles`;
  - every checker line runs under `$CHKPY`;
  - c1, c2 and cm each call chkenv before their first checker.
- `test_chkenv_fails_closed_without_uproot_or_the_modules`, a behavioural test. The connect's `chkenv()` runs verbatim
  in bash, three ways:
  - a checker python with uproot (a stub module) and the committed mp1/w2 modules: it passes;
  - a checker python without uproot: STOP, rc 8;
  - a deploy without the modules: STOP, rc 8.

**`rdx_mutation_stages.py`:** `EXPECTED_TESTS` 18, and eight new mutants, each killed by its named test:
- `CHKPY` back on root_6_28;
- c1's align back on `$PY`;
- c1, c2 or cm without chkenv;
- chkenv without the uproot import;
- chkenv's stop neutered to `true`;
- chkenv running nothing.

## The receipts (clean clone at `d2bd5479`, serial, nice 19, threads 1)

| file | result |
|---|---|
| `tests.txt` | 56 tests (`test_rdx.py` 38, `test_rdx_stages.py` 18), OK: Python 3.12.2, numpy 1.26.4 |
| `tests_py310.txt` | the same 56 tests, OK, under a uv venv at omnifold_py310's measured versions: Python 3.10, numpy 2.2.6, uproot 5.6.9 |
| `mutation.txt` | 51 of 51 declared mutants killed by their named tests |
| `mutation_stages.txt` | 36 of 36 declared mutants killed by their named tests (28 as before, and chkenv's eight) |
| `smoke.txt` | 38 cases, exit 0. Against `../launch/smoke.txt`, the only behavioural changes are the env check's line in each passing c1 case and the four new cases |

**What `tests_py310.txt` covers:** the checkers' logic under the cluster env's interpreter and numpy. The checkers' tests
inject their readers, so the uproot read of a real event-loop file is covered only by the cluster probe
(`../run-c1-20261115/envprobe.session.txt`). There, `omnifile_io.cycles` read the staged `base_cv.root`.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** what the tests, mutants and smoke check at `d2bd5479`, and the five files' shas.
- **Not citable for:** any c1 verdict, or any RDX reading. Nothing ran on the cluster for this change.
