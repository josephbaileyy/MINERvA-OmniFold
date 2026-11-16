# T2B receipt: the fake-data grading without C_model and with statistical-only uncertainty (2026-11-10)

**By** the valid-region lane (director-helper-2), under
[`T2B-FD-GRADE-VARIANTS-DECLARATION.md`](../T2B-FD-GRADE-VARIANTS-DECLARATION.md) (`52e2ba36…`) and
[`T2-BINDING-1.md`](../T2-BINDING-1.md) (M_T2 `3bb2a96c`).

**Gos:** the director's, for the fetch at `t2b_fetch.sh` `ce5e70c1…` and `t2b_fetch_remote.sh` `b407d055…`, for the
analysis at `t2b_grade.py` `53d4d7f2…` (run 1), and for its one-field revision at `208ca67d…` (run 2, §2.1).

**The result:** [`t2b.json`](t2b.json), sha256 `0e281a611177d90836db49736a57eff86d392eef955cb29221b79af2fa57ce43`
(run 2).
- Every control passed (B0–B3 and the nine input pins), and rc is 0.
- **This receipt makes no reading of the numbers.** The director makes that reading once, from this committed record
  (binding ruling 4).

## MEASURES / CANNOT AUTHORIZE

- **MEASURES:** each of the 16 graded records' χ² (ndf 16) and max |z| against M1 = (C_e + C_resp)/ffᵀ,
  M2 = C_stat/ffᵀ and M3 = (C_stat + C_resp)/ffᵀ, each with the record's own N, beside its existing grade.
  - The 16 records are F0b's twelve and F1's four.
- **CANNOT AUTHORIZE:**
  - a change to any criterion, trigger or grade;
  - a re-grading;
  - a statement about C_model's adoption;
  - any paper or note wording.

## CITABLE FOR

- Per record, **as a description:** how large b is against M1, M2 and M3, beside the existing grade.
- The |z| > 2 counts under each variant, **as descriptive counts only**.

## NOT CITABLE FOR

- **Coverage,** held-out-truth or detector-response statements.
- **That C_model is needed, sufficient, redundant or mis-sized,** or that the existing grade would change.
- **A p-value reading.** b is a deterministic bias, and no p is printed.
- **Any data-against-generator quantity.**

## 1. The fetch

- **The node.** login27 was chosen from a seven-node survey (`fetch/login-survey.txt`: one read-only ssh session
  reading `/proc/loadavg`).
  - login27 read 13.92 / 13.39 / 12.53 on 244 cores.
  - The others: login21 15.84, login33 23.63, login37 45.65, login05 58.39 and login11 319.88; login17 had no route.
- **The session.** One ssh session (saul, then login27), 2026-11-10T17:26:10Z to 17:26:17Z, `ssh rc=0`.
  - The /dev/shm copy was staged at `b407d055…`, and `script rc=0`.
  - Output: `fetch/fetch.out.txt` and `fetch/session.err.txt`; the latter includes NERSC's login banner.

| file (pscratch path) | bytes | sha256 (read on the node) | stat unchanged (size, mtime, atime) |
|---|---:|---|---|
| `/pscratch/sd/j/josephrb/s1-20261024/s1_assembly.npz` | 119,273 | `db000707…eb72a4` | True |
| `/pscratch/sd/j/josephrb/cmodel5d-20261024/out/cmodel_5d.npz` | 5,956 | `3008d8f6…84e882` | True |
| `/pscratch/sd/j/josephrb/cresp-20261026/out/cresp.npz` | 12,952 | `4d8b5797…a8a20a` | True |
| `/pscratch/sd/j/josephrb/fd-f1-20261027/grade/fd_f1_experiments.npz` | 1,075,668 | `997c7dae…2775bc` | True |
| `/pscratch/sd/j/josephrb/fd-f0b-20261026/fd_f0b_experiments.npz` | 1,068,642 | `7384c651…219ad9` | True |

- **Each file was read through O_NOATIME,** and the remote half wrote nothing on the cluster.
- **The local half:**
  - the tar (`4ff8f935…`) held exactly the five declared names as regular files;
  - each was written by its declared name, and all five are `OK` against T2B §2;
  - `fetch/SHA256SUMS` lists the tar and the five files.
- **The npz files are not committed;** they stay on pscratch at the paths above.

## 2. The run

- **The interpreter (run 1):** `t2b_grade.py` (`53d4d7f2…`) under `python3 -I -B`, Python 3.12.2 and numpy 1.26.4
  (`run/env.txt`), started 2026-11-10 (`run/start.txt`).
- **The inputs:**
  - `fd_f0_regrade` was imported from a registered detached worktree at `da5f157f`: porcelain 0, file
    `0dfa722c…`;
  - the three committed records (`fd_f1_readout.json` `cbe411a9…`, `fd_f0b_readout.json` `b9db935a…` and
    `fd_data_product.json` `b79556f0…`) were `git archive` copies at M_T2;
  - the npz files were read with `allow_pickle=False`.
- **Run 1's stdout** (`run-1/stdout.txt`): `T2B OK rc=0 … controls failed: []`. Its record, `t2b.json` `733a10b5…`,
  is not committed. See §2.1.

| control | outcome (`t2b.json` `controls`) |
|---|---|
| nine input pins | all pass |
| B0, fd_f0_regrade's control-4 loader checks | pass: f positive; C_e is the sum of S1's blocks; C_total = C_e + C_model_abs; C_model_abs = C_model·ffᵀ; C_model = SᵀS; C_stat,rel full rank; C_resp finite and symmetric |
| the 16 records are graded in the F1 readout | pass |
| B1, b and √diag N reproduce `bias` and `noise_sigma` to 1e-12 | pass for all 16, every one on `fd_f1_experiments.npz` (the F0b table was not needed) |
| B2, the existing grade reproduced to 1e-12 | pass for all 16: largest χ² relative difference 2.6e-14, z exact |
| B3, f, C_e and C_resp equal the data product's | pass |

## 2.1 Run 2: the same computation, with the inputs' full paths in the record

- **Why run 2.** Run 1's record names the five fetched files bare: as `inputs_sha256` keys and in B1's `table`.
  `docs/orchestration/verify_receipt_artifacts.py` treats the record itself as the receipt, and it refused the commit
  with MISSING ×5, because the README's full paths are not in the same file.
- **The fix,** approved by the director with nobody having read the numbers:
  - `t2b_grade.py` `208ca67d…` adds the dict `FETCHED_FROM` (T2B §2's five pscratch paths) and writes it as the
    top-level field `inputs_paths`;
  - nothing else changes (`code/t2b_grade.53d4d7f2-to-208ca67d.diff.txt`).
- **Run 2:**
  - same inputs and interpreter, rc 0, every control passed (`run/stdout.txt`);
  - **the gate** (`run/gate.txt`), a field-by-field comparison as data that prints no values: run 2's record equals run
    1's (`733a10b5…`) in all 10 shared top-level fields at full depth, and the only extra field is `inputs_paths`
    (`GATE EQUAL apart from inputs_paths`);
  - the test was rerun on `208ca67d…` (`run/test_t2b_grade.out.txt`, `ALL PASS`).
- **The committed record is run 2's.** The controls table above holds for both runs.

## 2.2 The record

- **The seed block is recorded and not gated:** `seed_block.max_abs_relative` is 0.0, as T2B §1 states.
- **The record's layout:**
  - `records.<name>.{existing, M1, M2, M3}`, each with `chi2`, `ndf`, `max_abs_z`, `max_abs_z_cell`,
    `cells_abs_z_gt_2` and `z`, plus `row`, `group`, `own_vertex` and `table`;
  - `abs_z_gt_2_by_group`, labelled descriptive.
- **What the record leaves out:** p-values, f, absolute cell values and f − X.

## 3. The code and its test

- **The code**, in `code/`: `t2b_fetch.sh`, `t2b_fetch_remote.sh`, `t2b_grade.py` (`208ca67d…`, run 2's), the diff
  from run 1's `53d4d7f2…`, and `test_t2b_grade.py` (`ed1144f6…`).
- **The test** (`run/test_t2b_grade.out.txt`, on `208ca67d…`: `ALL PASS`) builds synthetic inputs. It needs
  each case to end as declared:
  - a clean run is OK with 16 records;
  - the F0b-table fallback is used when the F1 table lacks a record;
  - a non-zero seed block is OK and recorded;
  - a rank-deficient C_stat stops at B0;
  - a perturbed bias stops at B1;
  - a 1e-9 χ² drift stops at B2;
  - a 1e-9 f drift stops at B3.
- **The pins are overridden only on the imported module;** the script has no test switch.
  <!-- absence-ok: a statement about this script's own interface, not a claim that a result does not exist -->

Nothing is submitted, deposited or tagged.
