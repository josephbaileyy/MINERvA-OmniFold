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
| `c0_sums.py` | C0. It runs after re2's comparator `re2c_determinism.py` (M's, `84951a8f…`) and classifies every SHA256SUMS line as bitwise, path-pairs, values_table (bitwise only), scratch (the period selftest's mkdtemp directory: the one named exception, with a rule per file), skipped (logs/, mpl/, ROOT, PDF) or OTHER. Any OTHER line is a STOP. |
| `c1_compare.py` | C1, (a)-(d) as restated by the director: entries within 1e-14 sqrt(C_ii C_jj); Q's median and integral at the spec's printed formats; per-band medians at their printed formats; x and F equal partc-r2's. It also prints (i)-(iv). |
| `test_driver.sh` (+ `run_mutants.sh`) | The driver stand-in test, run via `re2c_run.sh`'s own `step()` invocation. 4 of 4 mutants are killed. |
| `test_c0.sh`, `test_c1.py` | The C0 and C1 tests on synthetic trees and npz files (test_c0: two mkdtemp names; a one-value values_table change STOPs; extra, missing and changed scratch files STOP). |
| `fence-families.txt` | The grep-derived job-name families whose code reads or watches the NuE constraint (the director's M3b). The fence refuses every job regardless. |

**Why B and not M:** partc-r2's `periods/analysis.json` pins `re2_driver.py`'s sha256, and that file changed after B, so
a run at M would differ from partc-r2 by construction. `re2c_rollup.py`, `re2c_run.sh`, `re2c_build_q.py`,
`build_repair.py`, `re2c_values_spec.tsv` and part B's sums are the same at B and M.

**Expected C0:** the comparator's only difference is `SHA256SUMS` itself. It lists the digests of logs/, the PDFs, the
ROOT files and the selftest's scratch, which the comparator skips or pairs. Every other line is bitwise, path-pairs,
scratch or skipped; values_table.* are bitwise.

**Revision after coverage-5b-audit (1 blocker, 2 majors) and the director's specs, 2026-11-15:**
- B1: the selftest's mkdtemp directory (`periods_ns/tmp/tmp[a-z0-9_]{8}/`, its five files only) is joined across the two
  runs under one placeholder. id.txt and inj.txt must be bitwise. id.json and inj.json must be equal after the path
  pairs and the mkdtemp name (and, for inj.json, inj.root's digest). inj.root is accepted, but only when its listed
  digest is the one its own inj.json records. Checked on the real partc vs partc-r2 directories (O_NOATIME): all
  five files pass.
- M2: values_table.* bitwise (partc-r2's hold no path, host or time).
- M3: the fence fails closed and refuses every job (see the connect and fence-families.txt).
- Low: the fence runs again before the g2r arm.

**Rev 3, after the first run's C0 STOP (2026-11-15T22:53Z; the director's ruling (a2)):** that run, in
`/pscratch/sd/j/josephrb/cov2d-re2shapes-20261114`, stopped on two metadata causes, and the g2r arm never ran.
(1) `receipts/receipt_model_chi2.json`'s repo_commit is the shared `$A` checkout's HEAD (receipt_model_chi2_2d.py:56,
:307-308; re2c_run.sh MNV_REPO=$A), which moved from 32e403b8 to ed3590ea. (2) partc-r2's directory holds 8 files that
the later Fig. 1 steps added, absent from its SHA256SUMS, and the comparator saw them as only_stopped. c0_sums gains
exactly two named rules: R1 compares that receipt with only repo_commit set aside, beside the comparator's FIELD_SKIP
pair; R2 accepts only_stopped only when it equals those 8 files by name, none listed in partc-r2's SHA256SUMS.
test_c0 has both rules, with STOP mutants: a second differing receipt field, a ninth only_stopped file, and one of
the 8 missing. The next connect reruns everything in a new namespace, `cov2d-re2shapes-20261115`.
