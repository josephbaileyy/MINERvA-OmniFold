# RDX c1 fix: the checkers under omnifold_py310, behind a fail-closed env check (receipts, for the audit delta)

**By** session tier3-design, within the director's approved outline of 2026-11-15, after the c1 STOP
(`../run-c1-20261115/`). Code HEAD `44d2170c`. Only these three files change from M_RDXS:

| file | sha256 at M_RDXS | sha256 now |
|---|---|---|
| `nd-unfolding/rdx/rdx_connect.sh` | `11e7ef921bcc227255200347277d7b976d927c5fee2824dd613d31896c968827` | `eae946894be8ce02354e8bd6aaf038d78bd8f574772a359b90eaeb0d1dfd985d` |
| `nd-unfolding/rdx/rdx_connect_launch.sh` | `165fb98ebed89cf8fabd76d13c9bdc671c9ae5ca27c2377055c89d2760e0fb55` | `602c728a7b4326f2146bc219ec88ffb5da145869e81df9f4c1e214022e94212b` |
| `nd-unfolding/rdx/smoke_rdx_stages.sh` | `676bff5125548481b88a71986dc7625ea268ffb836b6ff845508d8502c3f1280` | `f02ca57acdfab743dc4774393d6d2742e07c1dd9badfdb0f639a152737511a54` |

No checker, job script, test or other file changes. The deploy stays at M_RDXS: the cluster's deploy is HEAD `ad0535c4`
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

## The receipts (clean clone at `44d2170c`, serial, nice 19, threads 1)

| file | result |
|---|---|
| `tests.txt` | 54 tests (`test_rdx.py` 38, `test_rdx_stages.py` 16), OK: Python 3.12.2, numpy 1.26.4 |
| `tests_py310.txt` | `test_rdx.py`'s 38 tests, OK, under a uv venv at omnifold_py310's measured versions: Python 3.10, numpy 2.2.6, uproot 5.6.9 |
| `mutation.txt` | 51 of 51 declared mutants killed by their named tests |
| `mutation_stages.txt` | 28 of 28 declared mutants killed by their named tests |
| `smoke.txt` | 38 cases, exit 0. Against `../launch/smoke.txt`, the only behavioural changes are the env check's line in each passing c1 case and the four new cases |

**What `tests_py310.txt` covers:** the checkers' logic under the cluster env's interpreter and numpy. Those tests inject
their readers, so the uproot read of a real event-loop file is covered only by the cluster probe
(`../run-c1-20261115/envprobe.session.txt`). There, `omnifile_io.cycles` read the staged `base_cv.root`.

No test or mutant pins `chkenv()` itself. The smoke's three no-uproot cases exercise it. A test with a mutant would mean
a change to `test_rdx_stages.py` and `rdx_mutation_stages.py`, which is outside the approved outline.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** what the tests, mutants and smoke check at `44d2170c`, and the three files' shas.
- **Not citable for:** any c1 verdict, or any RDX reading. Nothing ran on the cluster for this change.
