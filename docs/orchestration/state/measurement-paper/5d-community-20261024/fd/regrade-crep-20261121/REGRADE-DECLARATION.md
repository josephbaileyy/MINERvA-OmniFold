# REGRADE declaration: the held-out-tune coverage toys graded against the full reported covariances (2026-11-21, rev 2.1 after Grok's read and two rechecks; bound by REGRADE-BINDING-NOTE.md)
<!-- absence-ok: the declaration's own status line (unrun) -->

**By** tier3-design, under Joseph's go of 2026-11-21 on items a + c of the methods scoping, as the director relayed it
(`~/codex-reports/note-measurement/methods-scoping-20261121/SCOPING.md`).
**Joseph's reading rule, as relayed:** "if the regrade fails, the note's wording rests on the mean χ² (exact), not on a
claim about the coverage fraction."

**MEASURES:**
- the existing COV2D toys (2D, 205 cells) and LL5D toys (sixteen cells), graded against their tune's covariance plus
  the blocks the original tests left out:
  - 2D: C_T + C_run(T);
  - sixteen cells: C_T + C_resp(T) + C_PL,5D(T);
- the mean χ²/ndf and its split under that covariance (primary);
- the bound grade with the null rebuilt to include the added blocks (descriptive).

**CANNOT AUTHORIZE:**
- a change to Q_R, C_rep or any reported covariance;
- a cause of the under-coverage;
- a p-value;
- any note or paper wording. That goes to the director and Joseph.

**No new toys and no unfolds.** The 2D half is a local computation by cov2d from committed files. The sixteen-cell half
needs one O_NOATIME login read (§5). Price: 0 node-h.

## 1. Inputs, pinned

| input | path (repo-relative unless absolute) | sha256 |
|---|---|---|
| 2D errors, AR23 (300 × 205, after the surrogates; seeds 5,730,000–5,730,299; M ac25b665) | `fd/tier2-20261110/t2a/AR23/E_AR23.npz` | `ccda9c50c6bb1cbbdd2206c8954652f4f77c6cf2b4451e8488601e9896b0a85e` |
| 2D errors, G18 (seeds 5,720,000–5,720,299; M b1d56e4f) | `fd/tier2-20261110/t2a/G18/E_G18.npz` | `846b9d852218b531d605bd955ca9a9037d187e74723077bdfff4557efafc3ba6` |
| 2D blocks at AR23 (C_T and its parts, bands, x_T, x_R, rep) | `fd/receipts-cov2d/readout/AR23/blocks_AR23.npz` | `abaebaeae6c9cb075dcb974a420dbf148809d01b2cabc8deda31f318bf6715ee` |
| 2D blocks at G18 | `fd/receipts-cov2d/readout/G18/blocks_G18.npz` | `7eb657b82ae953bdf0584eda27264c52a64bcb48baea52dfc194f5efe440ea3d` |
| C_run = key `C_PL` (205 × 205, absolute at x_R), with keys `cells`, `x` | `/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partc-r2/outA/cov2d_Q_205.npz` (local copies: cov2d's, verified by sha) | `7153b194b95c27f80db5997bdde35fe2475f2b1c40c9ff456edd409850cf47d2` |
| 16-cell C_resp, C_PL,5D, P_rel, f (data central values) | `fd/with-cpl/block/cpl_block.npz` | `d9aa32fdb64357760348c9ccbc32fbea81d517f0f0786eedf17ab4946eaca59f` |
| committed grades the A0 control reproduces | `fd/receipts-cov2d/readout/<T>/score_<T>.json` (AR23 `fe5263e9…`, G18 `84976694…`); `fd/receipts-ll5d/readout/node/readout-<t>.json` (g18 `7bd6d390…`, ar23 `5b3fbbf5…`) | as listed |
| the sixteen-cell toys and remade blocks | §5 | §5 |

- **C_PL file.** The pinned file is the one `cov2d_blocks.py:52` and `g2r_readout.py:67` already pin.
- **cov2d's measurement, 2026-11-21:** its `C_PL`, `cells` and `x` are bitwise equal to those in the route-A file
  `ff66b91d…` (the adopted C_new). The two files differ only in `s5_total` and `Q` (the G2R change). So the choice of
  file does not move C_run.

## 2. The carry to tune T (choice 1)

- **Primary, fractional:**
  - 2D: C_run(T) = diag(x_T / x_R) · C_PL · diag(x_T / x_R);
  - 16 cells: C_PL,5D(T) = diag(X_T) · P_rel · diag(X_T) and C_resp(T) = diag(X_T / f) · C_resp · diag(X_T / f).
  - X_T is the remade central integral at T (`ll5d_b.remade`'s `X_T`). x_T and x_R are the blocks' keys.
- **Why fractional:**
  - It is the rule COV2D already applies to C08 (`cov2d_blocks.py:12`, `:142`).
  - Both run-period blocks are built from double ratios, so they are fractional in construction: C_PL from
    (x∘g_X) in `state/2d-closeout/playlist-term/DESIGN.md`, and C_PL,5D = diag(f) P_rel diag(f) exactly (max
    deviation 0.0, measured on the committed npz).
- **C_resp** (rev 1, Grok m3) carries as COV2D's C08 and LL5D's laterals do: by the ratio of central values (`cov2d_blocks.py:141-142`; `g = X_T / s1["f"]`, `ll5d_b.py:443-450`).
- **Sensitivity, printed and read by nothing:** the absolute carry, C_add(T) = C_add at the data.

## 3. The cell map (choice 2)

- **2D.** C_PL's 205 cells must equal COV2D's 205 cells in the same order.
  - Control C-MAP: `Q["cells"] == np.flatnonzero(blocks_<T>["rep"])` and `Q["x"] == blocks_<T>["x_R"]` bitwise, at both
    tunes.
  - cov2d measured both true on 2026-11-21. The control re-checks them in the run.
  - AR23's ndf of 204 comes from C_T's eigenvalue cut (1e-12 of the largest), not from a masked cell. ndf is
    recomputed on the new covariance's non-null subspace by `fd_1b_null.chi2_nonnull`.
- **16 cells.** R00–R15 in `cpl_block.npz` order. C-MAP16: that order equals `fd_data_product_cpl_cells.csv` and the
  `U` rows of `ll5d_b.setup` (`h2_definition.json`).

## 4. The statistics and their readings

**Per evaluation.** The evaluations are:
- 2D AR23 and G18;
- LL5D g18/minus2 (the primary reading), g18/all, ar23/minus2 and ar23/all.

**Definitions.** E is the 300 error vectors, n = 300 and C′ = C_T + C_add(T).
- **One factorisation for every quantity (rev 1, Grok M1).** The quadratic-form matrix is A = V_k Λ_k⁻¹ V_kᵀ, with
  k = {i : λ_i(C′) > 1e-12 · λ_max(C′)}. It is the factorisation `fd_1b_null.chi2_nonnull` uses (`fd_1b_null.py:92-97`),
  and ndf′ = |k|.
- **The driver calls that one function** for χ², the trace and the split. No `pinv` and no other cutoff.

**R-χ² (primary; the only reading that wording may rest on).**
- **Printed:**
  - M′ = mean_t χ²_t / ndf′, with SE(M′) = sd_t(χ²_t) / √n / ndf′ (ddof 1, as `fd_1b_mc.grade` computes it);
  - the split ēᵀAē / ndf′ (mean error) and tr(A S) / ndf′ (spread). Here S = (1/n) Σ_t (e_t − ē)(e_t − ē)ᵀ, divisor n,
    so the two parts sum to M′ exactly, as T2A's do (rev 1, Grok m1);
  - τ = tr(A C_add(T)) / ndf′;
  - **M_full = M′ + τ.**
- **The exact statement** (Grok's OK-check 1).
  - Suppose the natures also varied along the added blocks, with r independent of e, E r = 0 and Cov r = C_add(T).
  - Then, given the stored errors, the full test's expected mean χ²/ndf against C′ is M′ + τ = M_full ≥ M′.
  - The identity holds on the cut subspace, because A is fixed once C′ is.
- **The reading is one-sided (rev 1, Grok BLOCKING).**
  - **"under-describes on average"** if M_full − 1 > 3 · SE(M′). The trace is fixed given C′ and C_add, so
    SE(M_full) = SE(M′). The licensed sentence (rev 2, Grok recheck MAJOR) is about the full test, not the stored
    toys: "under the stated model, a full test whose natures also varied along the added blocks would have a
    conditional expected mean χ²/ndf′ against C′ of M_full, which exceeds 1 by more than 3 SE". It is always printed
    with M′ (the stored toys' own mean χ²/ndf′, to which the split adds) and τ. It never says the stored toys' mean
    exceeds 1 unless M′ − 1 > 3 SE(M′), which is printed as its own descriptive line.
  - **"not shown"** otherwise.
  - No branch reads "over-describes". Under the model, E[M′] = 1 − τ when C′ is right, so a low M′ is the model's own
    prediction and licenses nothing.
- **What the matrix is (rev 1, Grok M3).**
  - C′ is the tune-remade covariance (C_T(T), including C_model_abs) plus the carried blocks. It is the analogue at the
    tune of the full reported covariance (Q_R for 2D; C_rep for the sixteen cells).
  - It is not the published matrix at the data. COV2D's own rule applies: a result at T does not carry over to the
    reported matrix by itself (`COV2D-DECLARATION.md:226-227`).
  - Any use names C′ and the tune.
- **Assumptions printed with any use:**
  - the model for the added blocks is untested;
  <!-- absence-ok: a stated modelling assumption printed with the reading, not a claim that a result does not exist -->
  - for the run-period blocks there is no generative law at all (SCOPING.md item a3);
  - the carry of §2;
  - M_full is a conditional expectation, not a draw, and not a coverage fraction.

**R-grade (descriptive; nothing that reaches wording reads it).**
- **The bound grade, with the null rebuilt to include C_add(T):**
  - 2D: `cov2d_null.null_at_T` on a copy of the blocks dict with `C_T_minus` removed (rev 1, Grok M4: otherwise the
    leave-out-MEC null silently drops C_run). In the copy, `C08` is replaced by `C08 + C_run(T)` and `C_T` by
    `C_T + C_run(T)`. The seed is `cov2d.NULL_SEED`.
  - 16 cells: `fd_1b_null.null_contents(laws, gauss + C_add(T), C_T + C_add(T), seed=ll5d.NULL_SEED[e])`.
  - Then `fd_1b_mc.grade` at A5's tolerance, max(1e-9, 10 κ₂(C′) ε) (`ll5d_b.cholesky_tol`'s rule).
- **The record** prints the joint count against k′_J and the per-cell flags under the key `descriptive_regrade`. Any
  verdict string appears there only with the prefix `descriptive-` and the line "a reading, not a proof" beside it
  (rev 1, Grok m7).
- The joint fraction is not monotone in the added covariance under the full model (cov2d, 2026-11-21).

**Stability of the cut, printed (rev 1, Grok m4).** The record prints, against C_T alone:
- the kept-set difference;
- the smallest kept and largest dropped eigenvalues of C′, relative to λ_max.

## 5. The sixteen-cell read (one O_NOATIME login connect)

The per-toy sixteen-cell vectors are committed nowhere, so one capture runs on a login node.
- **The capture:** new code, `ll5d_regrade_capture.py`. It calls `ll5d_b.setup`, `ll5d_b.remade` and
  `ll5d_b.toy_errors` at LL5D's readout commit **M_L = `4231b14de5ea693e92cb31b1358a816b5c2f6625`**, all imported
  unchanged (the T2A capture pattern).
- **It writes**, per evaluation:
  - E (300 × 16), X_T and s1["f"];
  - every block (16 × 16), the gauss sum, and each band law's X matrix and probabilities;
  - the lateral deltas.

  The outputs are small npz files, fetched with sha256.
- **It reads exactly the inputs those three functions open:** 454 null-role products, 1,200 toys, the S1 assembly, the
  definition, the cmodel json and the flux constraint (Grok's OK-check 6). Not the null, clipcheck or gate records.

| what | path | pin |
|---|---|---|
| $U products: the 454 null-role products (each truth's central T, seed T, 175 blocks, stat replicas) and the 1,200 toys | `/pscratch/sd/j/josephrb/ll5d-unfolds-r2/` | rows `null_roles` and `toys` of `fd/receipts-ll5d/hpss-u/hpss_ll5d_u_list.tsv` (sha256 `980bb95e20eac386a220bb7d0dbb16a5a3477248688f9a72bc07671a7ad5842d`; each truth's products digest equals its null record's `products_sha256`: g18 c16e9ce0…, ar23 b716657b…) |
| S1 assembly | `/pscratch/sd/j/josephrb/fd-1b-inv-20261101/i0/in/s1/s1_assembly.npz` | `db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4` |
| flux constraint | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt` | `e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2` |
| definition and cmodel | the deploy at M_L: `nd-unfolding/pv-ladder/readouts/h2_definition.json`, `…/cmodel_5d.json` | the readout's bound list `7540b2de…` |

- **Read discipline:**
  - every product is opened through `inv.open_noatime`, as the bound functions already do;
  - before and after, the capture stats every listed path and requires every sha256 to equal its pin;
  - atime moved must be [].
  - `toy_errors` refuses unless the toy glob is exactly the 300 declared names, with no partials (`ll5d_b.py:597-603`).
    An extra file is a STOP (Grok m6).
- **Login read or HPSS.** The login read is preferred: the files are on pscratch, the toys' 8-week exposure starts about
  2027-01-07 (arithmetic, from the manifest's atimes), and the read is one pass of about 0.5 GB. HPSS is the fallback if
  any pin differs or a file is missing: `/home/j/josephrb/mnv-ll5d-unfolds-r2-20261116/`, four groups, ARCHIVE PASS
  (`fd/receipts-ll5d/hpss-u/README.md`).
- **The fence:** the fenced lanes' acks, each with a UTC time under 15 minutes old, and a window epoch from `date`.
  Job state comes from sacct.

## 6. Controls (any failure is a STOP, recorded unrepaired)

| control | condition |
|---|---|
| C-PIN | every input in §1 and §5 equals its sha256 |
| C-MAP, C-MAP16 | §3 |
| C-F16 (rev 1, Grok m3) | `cpl_block["f"]` equals the capture's s1["f"] to 1e-12 relative, and `cpl_block["C_PL5D"] == diag(f) P_rel diag(f)` to 1e-12 of max |
| C-PSD | for each nonzero C_add(T): symmetric to 1e-12 relative and min eigenvalue ≥ −1e-12 · λ_max (`cpl_block.npz` keys `C_resp`, `C_PL5D`, `P_rel`, `f`). Every rebuilt null runs with RuntimeWarning raised as an error (`warnings.simplefilter("error", RuntimeWarning)`), so NumPy's `multivariate_normal(method="eigh")` PSD warning (`check_valid='warn'`, absolute tolerance 1e-8) is a STOP. λ_max of the Gaussian is printed. The covariances here are of order 1e-78 in cross-section units, so C-PSD's relative floor (−1e-12 · λ_max) is the tighter check and binds first; NumPy's absolute floor is the looser one (rev 2.1, Grok recheck 2's note). Skipped when C_add ≡ 0 (rev 1, Grok m2; rev 2, Grok recheck m2) |
| **A0** (rev 1, Grok M2) | with C_add = 0, in the same driver: (a) ndf, joint_count and the per-cell in-interval counts equal the committed grade's; (b) chi2_mean_over_ndf within 1e-9 relative. These depend only on E and C_T. (c) k_joint and the flags (2D `flagged_cells`; 16 cells `cell_flag` in R00–R15 order) depend on the re-simulated null. A mismatch in (c) alone is recorded as "null redraw differs", not a STOP. Committed grades: 2D `score_<T>.json`; 16 cells `readout-<t>.json` |
| C-NULL | `check_matched` passes at 1e-12 for every rebuilt null |

## 7. Code, tests, who runs it

- **The driver:** `regrade_crep.py` under `fd/regrade-crep-20261121/`. It is glue over `cov2d_null`, `fd_1b_null` and
  `fd_1b_mc`, all imported unchanged. It computes §4 for 2D (inputs §1) and for the sixteen cells (§1 plus the
  capture's npz).
- **The capture:** `ll5d_regrade_capture.py` (§5).
- **Authorship:**
  - tier3-design writes both. cov2d reviews them, and runs the 2D half locally (the director's assignment).
  - The sixteen-cell capture connect is run by tier3-design.
- **Tests:** unit tests for the carry, the maps, M_full and the one-sided rule (each direction and each operand), the
  split's divisor, the C_T_minus removal and A0's three parts. A mutation receipt accompanies them.
- **Each result is read once** from its committed record.

## 8. Order

1. Grok's recheck of rev 1, then the binding note.
2. Code, tests and mutation, and cov2d's review.
3. The 2D half, locally.
4. The sixteen-cell capture connect, before the toys' exposure date (about 2027-01-07) and well before 12-23. The
   capture opens no C_resp / C_PL,5D source: the driver reads those blocks from the committed `cpl_block.npz` (rev 1,
   Grok m5).
5. The sixteen-cell regrade, locally.
6. The records are committed and read once.

<!-- absence-ok: a declaration of an unrun study; statements about what is not committed are routed to the receipts named -->
