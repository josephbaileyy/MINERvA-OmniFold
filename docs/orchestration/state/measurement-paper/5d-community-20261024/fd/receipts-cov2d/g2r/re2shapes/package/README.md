# RE-2-shapes package (DRAFT for the director and coverage-5b-audit; not yet given a go)

**By** the `cov2d` session, under the director's rulings of 2026-11-14:
1. the driver counts as "through re2's own code" (noatime_inputs precedent);
2. the reported matrix stays data_g2r.npz's C_new, and C1's criterion is as restated;
3. NuE constraint option (a): the run happens after rdx_s1_1A ends.

The connect (`connect-g2r-re2shapes.sh`, outside this commit because it pins this commit) re-runs RE-2 part C's
refined arm twice, on a fresh deploy at partc-r2's commit B = 903fb78b. The first run (C0, mode identity) must
reproduce partc-r2. The second (mode g2r) is route A: the 175 J2 universes are G2R's products at their committed
digests. C1 compares route A's Q with C_new.

**CANNOT AUTHORIZE:** any adoption or wording. The reported matrix is C_new (D1). Route A supplies only the derived
quantities in re2's shapes.

| file | what |
|---|---|
| `re2c_rollup_g2r.py` | The driver. It imports `re2c_rollup.py` unchanged and patches `ro.partb_sums` (the 175 U_* digests become G2R's, from products.tsv `a0f86fe1…`) and `ro.Path` (the 175 U_* paths become G2R's out/A_*). In mode identity, nothing is redirected. In mode g2r, it exits 3 unless exactly 175 calls are redirected. Its sidecar goes outside `$O`. |
| `re2c_run_g2r.sh`, `make_run_g2r.py`, `run_g2r-vs-ff66c7a9.diff.txt` | `re2c_run.sh` (`ff66c7a9…`, identical at B and M) with one line changed: the refined arm's rollup step. |
| `c0_sums.py` | C0. It runs after re2's comparator `re2c_determinism.py` (M's, `84951a8f…`) and classifies every SHA256SUMS line as bitwise, path-pairs, skipped (the comparator's own list) or OTHER. Any OTHER line is a STOP. |
| `c1_compare.py` | C1, (a)-(d) as restated by the director: entries within 1e-14 sqrt(C_ii C_jj); Q's median and integral at the spec's printed formats; per-band medians at their printed formats; x and F equal partc-r2's. It also prints (i)-(iv). |
| `test_driver.sh` (+ `run_mutants.sh`) | The driver stand-in test, run via `re2c_run.sh`'s own `step()` invocation. 4 of 4 mutants are killed. |
| `test_c0.sh`, `test_c1.py` | The C0 and C1 tests on synthetic trees and npz files. |

**Why B and not M:** partc-r2's `periods/analysis.json` pins `re2_driver.py`'s sha256, and that file changed after B, so
a run at M would differ from partc-r2 by construction. `re2c_rollup.py`, `re2c_run.sh`, `re2c_build_q.py`,
`build_repair.py`, `re2c_values_spec.tsv` and part B's sums are the same at B and M.

**Expected C0:** the comparator's only difference is `SHA256SUMS` itself. It lists the digests of logs/, the PDFs and
the ROOT files, which the comparator skips or pairs. Every other line is bitwise, path-pairs or skipped.
