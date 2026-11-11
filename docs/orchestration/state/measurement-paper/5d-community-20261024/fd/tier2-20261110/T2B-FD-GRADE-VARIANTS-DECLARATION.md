# T2B DECLARATION: the fake-data grading without C_model, and with statistical-only uncertainty, beside the existing grade (2026-11-10, DRAFT for the director's binding)

**By** the valid-region lane (director-helper-2), for the director.

**Under:**
- `DECISION-20261110-joseph-confirm-round-scope.md` (PR #1030, open at `04cb5b7d`), item 1.
- The director's Tier 2 rulings of 2026-11-10 on this lane's scoping.

**Nothing has been computed.** No variant matrix has been formed, and no χ² has been taken against one. <!-- absence-ok: a statement about this draft's own status before binding, not a claim that a result does not exist -->

**The records it reads:**
- `fd/readout/fd_f1_readout.json` (sha256 `cbe411a926a7392e4aa085c7beba6e1bda45aff55d937998c53e49f27e3516c7`). It grades
  all 16 records below in one run of `fd_f0_regrade.py` at `da5f157f` (`FD-F1-REPORT.md:140`; the file's sha256 is
  `0dfa722c…`, as the readout's `code_sha256` records it).
  - Its control 9 shows the twelve F0b truths grade exactly as `fd/readout/fd_f0b_readout.json` (`b9db935a…`) records
    them.
- The 16 records:
  - **F0b's twelve:** nominal, W1, W2, W3, q3, stage0c_gibuu, closure_nuwro, A7_mnvtune, A7_genie_cv, A7_genie_mec,
    A7_nuwro and A7_gibuu.
  - **F1's four:** F1_genie_v3_g18, F1_closure_genie_v3_g18, F1_genie_v3_ar23 and F1_closure_genie_v3_ar23.
  - Row 6 (P1r–P3g) is ungraded in both readouts and is not used.

## MEASURES / CANNOT AUTHORIZE

- **MEASURES:** each record's χ² (ndf 16) and max |z| against three smaller matrices, printed beside its existing grade
  against C^(T) + C_resp.
- **CANNOT AUTHORIZE:**
  - a change to any criterion, trigger or grade;
  - a re-grading of any record;
  - any statement about C_model's adoption;
  - any paper or note wording.

## CITABLE FOR (once the record lands)

- Per record, **as a description:** how large b is against (M1) the reported covariance without C_model, (M2) the
  statistical block alone and (M3) the statistical block plus C_resp, each with the record's own noise N, beside the
  existing grade.
- **The |z| > 2 counts under each variant,** as descriptive counts only, with no threshold applied.

## NOT CITABLE FOR

- **Coverage,** held-out-truth or detector-response statements. These are the same exclusions as F0, F0b and F1; F1's
  label reads "a bias test … not a coverage test".
- **That C_model is needed, sufficient, redundant or mis-sized,** or that the existing grade would change under another
  matrix. The existing grade stands as recorded.
- **A p-value reading.** b is a deterministic bias (the readouts' own label: "context only: b is a deterministic bias,
  not a Gaussian draw"). A χ² is printed with no p.
- **Any data-against-generator quantity** (as F0b).

## 1. The matrices

Every matrix is fractional, in S1's convention (`fd_f0_regrade.py@da5f157f:678`: C_rel = C / ffᵀ), with f as that tool
loads it from S1's npz (:658). The grade is `fd_f0_regrade.grade(b, N, C)` (:225-238): z = b / √diag(C + N) and
χ² = bᵀ(C + N)⁻¹b by Cholesky, ndf 16.

| name | C | note |
|---|---|---|
| M0 (the control; existing) | `leave_out(C_e/ffᵀ, S, own) + C_resp/ffᵀ`, own = the record's `own_vertex` (`None`: all three vertices) | `fd_f0_regrade.py@da5f157f:787` |
| **M1** | (C_e + C_resp) / ffᵀ | C_model removed entirely |
| **M2** | C_stat / ffᵀ | S1's `stat` block only |
| **M3** | (C_stat + C_resp) / ffᵀ | |

- **"Statistical" is S1's `stat` block** (npz key `C_stat`, :659), the data-statistical bootstrap block. It is the
  director's ruling.
- **S1's `seed` block is not included,** and it is zero:
  - `s1/readout/s1_assembly.json` `relative_sigma.seed` is 0.0 on all 16 cells, and `trace_share.seed` is 0.0;
  - `FD-STAB-DECLARATION.md:198`: "S1's seed block measured 0".
  - So including it or not changes no number.
- **N is kept in every variant,** as the record's own noise of its mean:
  - rows 1, 2, 4 and 7 use `fd_f0_regrade.unweighted` (:207-212), Cov_i(r)/B with ddof 1;
  - the closures (rows 3 and 8) have N = 0.
- **M2 is invertible:** fd_f0_regrade's control 4 checks "C_stat,rel is full rank" (:691).

## 2. Inputs (one scp fetch, then local)

| input | path | sha256 | bytes |
|---|---|---|---:|
| S1 assembly (f, C_e, C_stat, C_total, C_model_abs) | `/pscratch/sd/j/josephrb/s1-20261024/s1_assembly.npz` | `db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4` | 119,273 (`S1-REPORT.md:210`) |
| C_model's S (control M0 only) | `/pscratch/sd/j/josephrb/cmodel5d-20261024/out/cmodel_5d.npz` | `3008d8f6b1f295cdd648f14e1ab2c20d864ce054a19f97e90e1620d22484e882` | as fetched |
| C_resp | `/pscratch/sd/j/josephrb/cresp-20261026/out/cresp.npz`, key `C_resp` | `4d8b579732b79cbbb8e6c9a4f6335c4bda4eae6dd4194241a0d8cd6e7ea8a20a` | as fetched |
| the per-experiment table (r_<set>) | `/pscratch/sd/j/josephrb/fd-f1-20261027/grade/fd_f1_experiments.npz` | `997c7dae34ef9703291baece51eed05f3dd7d38a043630cac9667efaad2775bc` | as fetched |
| fallback for F0b's twelve, used only if B1 below fails on the F1 table | `/pscratch/sd/j/josephrb/fd-f0b-20261026/fd_f0b_experiments.npz` | `7384c6518aa0f59bd4964170fcc9b652f1c31958f422f1e1b597cd3e59219ad9` | 1,068,642 |
| the records | `fd/readout/fd_f1_readout.json`, `fd/readout/fd_f0b_readout.json` (committed) | `cbe411a9…`, `b9db935a…` | |
| cross-check | `fd/data-product/fd_data_product.json` (committed; its `inputs_sha256` names the same `s1_npz` and `cresp_npz`) | `b79556f0538c81942c0ddd3770ae55e5c6fe9ad53df47e470d306f727d7e7072` | |

- **The fetch:**
  - one ssh session's scp of the five files into a new empty directory under the scratchpad;
  - each file's sha256 is checked against the table, and the run stops on a mismatch;
  - the files are read only by a script kept in a different directory, under `python -I`, with `np.load(...,
    allow_pickle=False)`;
  - nothing is written on pscratch or CFS.
- **The code:** `fd_f0_regrade` is imported from a clean `git worktree` at `da5f157f`, file sha256 `0dfa722c…` checked
  before import.

## 3. Controls (all before any variant is formed; each fails closed: STOP to the director, no reading made)

| # | control | tolerance |
|---|---|---|
| B0 | S1's npz passes `fd_f0_regrade`'s control-4 loader checks (:667-691): C_e is the sum of S1's blocks, C_total = C_e + C_model_abs, S's committed equality, C_stat,rel full rank | that tool's TOL |
| B1 | the table has an r_<name> key for each of the 16 records; `unweighted`/noise-free b and √diag N reproduce each record's `bias` and `noise_sigma` | 10⁻¹² relative |
| B2 | **the existing grade on all 16 records:** `grade(b, N, M0)` reproduces each record's `grade.chi2` and `grade.z` | 10⁻¹² relative |
| B3 | f, C_e, C_resp (absolute) equal `fd_data_product.json`'s `f`, `matrices.C_e`, `matrices.C_resp` | 10⁻¹² relative |

Only when B0–B3 all pass are M1–M3 formed and graded.

## 4. Outputs and the reading

- **`fd/tier2-20261110/t2b/t2b.json`,** per record and per variant: χ², max |z| and its cell, and the |z| > 2 cell list.
  Beside them, the record's existing χ², max |z| and cell list from the readout.
- **Per variant,** the |z| > 2 counts by the readouts' groups (prior, vertex-family, non-vertex, held-out), labelled
  descriptive.
- **No f, no absolute cell value and no f − X** are written. This is ruling 6's discipline, kept although f is now
  committed in the data product.
- **The receipts:** the fetch log, the five sha256 checks and the local run's stdout.
- **The reading is made once,** by the director, from the committed record, under the licence above. Nothing is
  re-selected after it is seen.

## 5. Price

- **The fetch:** one ssh session, 0 node-h. It waits for Joseph's NERSC certificate renewal if the certificate has
  lapsed.
- **The computation:** seconds, locally.
- **No Slurm job.**
- **No CFS path** is named.

Nothing is submitted, deposited or tagged.
