# MSR DECLARATION: which combinations of the reported cells do the detector-level inputs constrain, and where do the known biases sit? (rev 3, 2026-11-22)

**By** tier3-design, for the director. **Authority:** Joseph via the director, 2026-11-22 ("yes can we do the measurability study"),
from an outside review of the note (Fix 2). **Base:** origin/main `7d5a98361`. **Compute:** the projections are local, at 0 node-h.
The two responses (2D and 5D) are built on the cluster (§8) under a separate go, with the fence and fresh acks. Nothing is
computed before this declaration, its reads and the director's GO.
<!-- absence-ok: a statement of this study's own order of work, not a claim that a result does not exist -->

**Revisions, all before any computation:**
- **rev 0** `889d9302`.
- **rev 1** `817ee125` (commit): the director's four items:
  - a floor on ‖β‖;
  - a noise-max bar on the noisy vectors;
  - k = 50 printed for T3's arms, with a pairing rule;
  - C-DID-CONS as a scripted test.
- **rev 2** (this file): every finding of the agy (Gemini 3.8 Flash High) and Grok reads of rev 1, taken as fixes (reports in
  `reads/`), plus one operand change:
  - **Grok 1, the span maximum.** Z_well is read on the largest bias over the whole well-constrained span, √χ²_well, not
    per axis (§3.6). The per-axis maximum is printed only.
  - **Grok 2, U∞ per direction.** U∞ is defined per direction, by D-ID's null-fraction rule, with the pseudo-inverse at
    D-ID's eigenvalue cut (§3.3).
  - **Grok 3 / agy 4, own bands.** The bands are this study's own. From b1 only the two-driver pattern is reused (§2).
  - **Grok 4, D-ID's b.** D-ID's "signal-only" keeps the out-of-grid known term. C-DID uses it, and b = 0 is only a
    printed variant (§3.2, §6).
  - **Grok 5, the 16-cell map.** L maps H2 truth counts to the 16 cross-section functionals, and a new STOP control C-L
    requires L t0 = FD-PRR's P (§3.1, §6). Cells with f0 = 0 are dropped.
  - **Grok 6 / agy 1, 2, 7, the reading rules.** One set of inequalities. Sentinels for an empty well-constrained set and
    for the r floors. The noise-max rule is on the interval. The floor no longer overrides a resolved "resolvable".
    Percentile intervals for the noisy vectors, one perturbation scheme for F0b and A2, and a split guard on ‖β‖ for the
    5-split means (§3.6, §5.1).
  - **Grok 7, the MO sentence.** It is tightened (§5.2).
  - **Grok 8, the §1 wording.** The R-ID capture is C-RID's input only (§1).
  - **Grok 9 / agy 3, 5, controls.**
    - The 3D/4D Fisher is rebuilt from the summed R and b, with the dropped axes pinned.
    - One background template for the full build and both halves.
    - C-T3 at k = 5.
    - 2D R = M/T with a named b.
    - An absolute floor in N-PREC.
    - One-to-one half matching, and dim U∞ equal across the halves (§3.4, §5.3, §6).
  - **Grok 10, notes.** Full code sha256 in §2; "size" means the sum of squares; the login gate is hard (§8).
  - **agy 6, M3's sentence.** It completes the partition (§5.2).
  - **agy 8, the §4 wording.** It is harmonized (§4).
  - **Operand change, 2D.** The 2D response is built from the IBUKT bank `bank.npz` (sha256 `60416384…`, A2's
    `bank_sha256`), numpy only, in place of a ROOT read of the CFS omnifile. The bank holds the very event arrays, background
    and `ibu_response` that A2's IBU used. No PyROOT read is made, so the MAT-dictionary test is not needed. That is
    stated, not skipped (§2, §8).
- **rev 3** (this file): every finding of Grok's confirming read of rev 2 `a3f35ed5` (`reads/rev2-grok.txt`), taken as a fix:
  - **1, the null fraction.** U∞ and F⁺ are now taken in count space on `did.fisher(R, t0, b)` with the count-space
    gradient, exactly as `widths_from_eig` does. A synthetic case at a t0 ratio of 10⁷ is added, and ρ must match
    `widths_from_eig`'s null fraction on the 16 coordinate directions (§3.3, §6).
  - **2, OP's iterations.** T3's OP arm runs 2 iterations (`t3p_arms.ITERS["OP"] = 2`), so OP is read at k = 2 only.
    B0 and MO are read at k = 5 (and k = 50 printed) (§4, §5.2).
  - **3, the 2D map.** It indexes the readout's `cells` (the bank's `selected` mask), not `signed_identity.truth_indices`
    (§3.1, §6 C-L).
  - **4, the 2D construction.** `binned_problem` returns (T, M, y, t). R's columns with T = 0 are set to 0. C-2D checks
    b_bkg and b_known cell by cell between two constructions (§3.1, §6).
  - **5, the Z_well sentences.** They speak of the span W of the well-constrained eigen-combinations, which is what Z_well
    bounds (§5.1).
  - **6, the noise-max endpoint.** "Contains Z_noise" means f_lo < Z_noise < f_hi (§5.1).
  - **7, sd and the empty well-constrained set.** sd is the sample SD with divisor 4. With n_well = 0, Z_noise and Z's
    numeric N-PREC test are skipped (§3.6, §6).
  - **8, C-ROUTE's bars.** They are written per statistic (§6).
  - **9, the dropped cells.** The dropped-cell sets must be equal across full, A and B before any projector comparison
    (§5.3).
  - **10, the H2 grid.** The capture's grid identity is checked against H2 (§3.1, §6 C-GRID).
  - **Also found while writing the builder:** FD-PRR's P is the nominal truth's cross section from half B at the same
    split (`prr_read.py:19`, `t3p_read.priors`), so rev 2's C-L (L t0 = P) cannot hold by construction. C-L now checks
    that L is the extraction, linear, and equal to T3's M16. The ratio P/f0 converts FD-PRR's b to φ-units, and it is
    printed (§3.1, §3.5, §6). At 2D the corresponding ratio is computed from the bank, not assumed.
  - **From the Grok and agy reads of the connect-P code** (`reads/connectP-grok.txt`, `reads/connectP-agy.txt`), the
    parts this declaration describes:
    - the 5D inputs are loaded without the two data keys (`measured`, `measured_weights`), under `ibu1.load_inputs`' own
      digest checks. test_msr_build checks every array equal to the pinned loader's (§0, §2);
    - the probe times a row subsample written by a separate process, so its peak RSS is its own (§8);
    - C-DID-CONS always runs in connect P, whatever the gate reads, with both sides' exit codes checked. An incomplete side
      records INCOMPLETE, never EQUAL or DIFFERS (§1, §8);
    - every stop after `$OUT` exists writes the records first;
    - connect B reads T3's originals only through O_NOATIME copies (§8).
  - **From Grok's confirming read of the fixed connect code** (`reads/connectP-confirm-grok.txt`): the bank's `selected`
    is 205 integer ids, not a mask (§3.1, C-L); the 2D probe also times the halves; the launcher's `/dev/shm/msrp.*`
    staging copies are in the overlap; a failed probe part sets login_ok false and the run still reaches C-DID-CONS; the
    four C-DID-CONS hashes are taken before anything is printed; a reco DIFFERS is checked for the upper-edge convention.
  - **The director's ruling on the IBUKT root (2026-11-22):** the bank is read at its one recorded path, with no search
    and stat before and after (§2, §8).
- **rev 4** (2026-11-23, after connect P attempt 2, `run-p2/`): **C-DID-CONS is EQUAL on both lists.** The J-cell
  memberships match (134, sha256 bd1434b0…), and so do the occupied reco cells (10,499, sha256 8b82482b…). So C-DID is a
  **STOP control** in connect B (§1, §6). Nothing else changes.
- **Amendment B (2026-11-23, the director's rulings for connect B; it changes how the build runs, not what it
  computes):**
  - connect B runs `msr_build.py build --part` once per part, in its own process, in order r5d, r2d, t3;
  - each part's peak RSS is recorded in `<part>.json`, and a peak above 8e9 B refuses that part (rc 9, no product
    written, a STOP);
  - the probe's three staged copies (`msr-p-20261122/stage`) are reused only after an O_NOATIME sha256 re-check against
    their pins at connect start, and a mismatch is a STOP;
  - all of B's outputs go under a fresh `$OUT` (`msr-b-20261123`), never into the probe's. The probe's `$OUT` stays as
    is until B's records merge, and its removal is Joseph's call (it is listed for him);
  - every C-* control, including C-DID and C-RID, is applied locally to the fetched products, before any reading.
- **Amendment C (2026-11-23, after the local run STOPped at C-DID, `run-local/`; the director's ruling):** an executability
  fix that changes no number, bar or set of any reading. It makes three controls implement §6's text as written.
  - **C-DID** compares "on the functionals both name", as §6 says.
    - Rule: the intersection must be non-empty, and its size must equal **151** for these inputs. That value is a
      recorded expectation, pinned, not a tolerance.
    - The one-sided names are recorded and printed: IBU-1 only `EW_all_ones` and `total_integrated`, plus D-ID's 32
      names that IBU-1 lacks.
    - Values are checked on the intersection at the declared bars. The code had also required every IBU-1 name to be
      among D-ID's, which is stricter than §6 and caused the STOP.
  - **C-2D** takes §6's bar, relative ≤ 1e-12 cell by cell. The code had required M and b_known to match exactly.
  - **C-D** checks each F0b truth whose bias is converted with d: the 11 primary truths and the secondary
    `closure_nuwro`.
    - The six P-sets (ungraded, §4 printed secondary) have no FD-PRR entry, so they are printed only in truth-relative
      units (P/f0), and C-D records them as "printed without d".
    - The code had checked the primaries only. A literal "each F0b truth used" would have stopped on the P-sets, which
      §4 prints without d.
  - **C-RID, C-T3 and C-F0B** were audited against §6 and need no change:
    - C-T3 matches §6.
    - C-F0B's equal-name-set condition is implied by "bias equal in the two readouts".
    - C-RID's NaN-pattern condition on null_fraction is no stricter than the declared absolute bar for these inputs,
      which hold no NaN.
- **Amendment E (2026-11-23, after the rerun STOPped at C-ROUTE, `run-local-2/`; the director's ruling on
  `route-diag2/`):** an executability fix that changes **how** §3.3's quantities are computed. It changes no number, bar,
  cut (1e-12 and 0.10 stay), set or reading.
  - **Why.** Diagnostic 1 (`route-diag/`) found the routes disagreeing on 21 2D Z_well rows, with κ₂(Wᵀ C W) only 539.
    Diagnostic 2 (`route-diag2/`) compared both routes with a 50-digit mpmath reference, from the same float64 inputs
    through §3.3, and its pre-committed rule printed `c-formation`, which the director confirmed. So C's float64
    formation is the defect, not either route alone. C = J F_c⁺ Jᵀ takes its scale from the largest widths, so rounding
    at ε‖C‖ swamps well-constrained s² ≤ 0.01 in both routes.
  - **E1, F_c's eigenpairs.** They come from the thin SVD of its root A: the rows R_i/√μ_i over reco cells with μ > 0,
    which are `did.fisher`'s rows, so AᵀA = F_c. Then λ = σ², and v are the right singular vectors, completed with A's
    null space if fewer reco cells are kept than parameters. F_c is not formed for §3.3's decomposition, and the
    1e-12·λ_max cut applies to these λ unchanged. C-DID's reproduction of D-ID keeps `eigh(did.fisher)`, as D-ID
    computed it.
  - **E2, the eigen route.** C is never formed. G = J V_r Λ_r^{-1/2}, so C = G Gᵀ. C_Q's eigenpairs (s², c) are the
    singular pairs of B_Qᵀ G, and w = B_Q c. The well-constrained block (s ≤ 0.10) is then re-diagonalized from Gᵀ W,
    whose singular values are ≤ 0.10, so no small width is a difference of large numbers. In exact arithmetic this is
    §3.3's C_Q eigen-decomposition. C_Q cannot be singular on Q, because a zero-width direction would lie in U∞. So
    dim Q > the number of range directions (G's columns) is refused as a numerical defect (a crash, so the run stops),
    not padded with zero widths. A zero width within these dimensions needs J to be row-rank deficient, which C-RANK
    stops. After refinement the widths are re-sorted ascending, because rounding may reorder near-equal widths.
  - **E3, the independent route (C-ROUTE).** χ²_well = aᵀ(Wᵀ C W)⁻¹a by a triangular solve with the R factor of a QR of
    Gᵀ W, since Wᵀ C W = (Gᵀ W)ᵀ(Gᵀ W). W still comes from a pivoted QR of the well-constrained block. It remains a solve,
    not eigenvalues (QR against SVD).
  - **E4, N-PREC's driver pair.** The pair applies to these SVDs as two LAPACK families: "numpy" is
    `numpy.linalg.svd` (gesdd), and "evr" is `scipy.linalg.svd(lapack_driver="gesvd")`. The generalized eigenproblem
    for U∞ is unchanged (`scipy.linalg.eigh`).
  - **Tests.**
    - A synthetic ill-conditioned fixture (`test_msr.AmendmentE`, two seeds). On the pre-amendment code at 88994c9a,
      both routes miss the 50-digit reference by more than 1e-8 (`old_formation_check.py`). On this code both routes
      are within 1e-8 with both drivers.
    - The existing suite, a line tracer over every executable line, and mutants. One mutant restores C's float64
      formation in each route, and both must be killed.
    - An agy read, and the director's review of the diff.
  - **What follows.**
    - A blind confirmation on the real inputs with diagnostic 2's fields and rows: both routes within 1e-8 of the
      reference on all 21 2D rows, with `ref_partition_equal` true. The 5D control rows get a 50-digit reference too,
      since 5D has 29 parameters. Only pass or fail and the count are reported.
    - Then one rerun of the full run at the merged commit into `run-local-3/`. Any STOP is terminal and goes to the
      director.

**Rulings folded in (the director, 2026-11-22):** Q1, a cluster build (login node if light, otherwise one shared-QOS job of
at most 0.1 node-h); Q2, T3's B0, MO and OP as operands; Q3, H2 truth cells, with the 16-cell biases taken through the
functional map and R00–R15 printed alone; V_r with background, at the data exposure; a split-half MC control; the cut fixed
with its basis; a section on D-ID and R-ID; C-RID as a STOP control; R-ID's use fixed before its values are seen (§5.2); the
four rev-1 items.

## 0. What this can say, and what it cannot

**It can say:**
- for each tested bias vector, how its sum of squares (in relative units on the reported cells) divides between the
  combinations of reported cells that the binned detector-level inputs constrain to 10 % or better at the data exposure,
  and the rest;
- whether, anywhere in the well-constrained span, the bias exceeds what the data could resolve (in binned Cramér–Rao
  widths);
- for T3's oracle arms (MO, OP), which part the true missed-event weights remove;
- how many combinations of the 16 reported cells each reco feature set (3D, 4D, 5D) constrains to 10 % or better.

**It cannot say:**
- a cause beyond "consistent with". "Consistent with an information limit" names where the bias lies. It is not a
  proof that no estimator could remove it, because binned Fisher information does not bound unbinned estimators or
  estimators that use prior information (D-ID §5);
- that any estimator change would fix a bias, or which one. Nothing is adopted;
- coverage or the validity of any interval;
- anything about the data. No data count, data unfold or data residual is read; the data arrays of `of_inputs_5d.npz` are
  never loaded (§2). The data enter only through the exposure scale of V_r (§3.2);
- note wording. Results go to the director first.

**NOT CITABLE FOR:** a cause beyond "consistent with", an estimator change, coverage, any data quantity, or note wording.

**What I saw before writing this.**
- Committed readouts: field names and structure only, with no values, for
  - FD-PRR (`readings`, `table` with fields `rho`, `n_S`, `b`, `rms_b`, `r`, `grade`, `d`; `R-ID` field names `label`,
    `sigma_rel`, `null_fraction`, `n_cells_grid`, `n_null_modes`; `R-SUP`);
  - F0b (`truths[].bias`, `noise_sigma`; the truth names, groups, estimators and `n_experiments`);
  - T3 (top-level keys `schema`, `labels`, `verdict`, `controls`, `readings`, `table`; the table's arm, truth and split
    keys; the per-k field names). **T3's readout has no R-ID block and no per-cell bias vector**;
  - IBUKT A2 (truth names; per-method `residuals`, `mean`, `noise_guard`, `departure`; `bank_sha256`).
- The values I know from the note or the records: D-ID's published outcome (branch C; 121 of 144; the medians in
  `sec_5d.tex:84`), and FD-PRR's B0 ρ(50) at A7 GiBUU and q3 as T3's declaration quotes them.
- No response, spectrum, width or projection has been computed.
<!-- absence-ok: a statement of this study's own order of work and of which fields were seen, not a claim that a result does not exist -->

## 1. Prior art, and how this differs

| study | what it did | how this study differs |
|---|---|---|
| **D-ID** (2026-10-10; `state/next-preparation-20261009/d-id/`, note `sec_5d.tex:84`) | Exact binned response from `of_inputs_5d.npz` at the 10,499 occupied reco cells; truth grids T1 (109 J cells), T2 (J split), T3 (fine). Fisher F = Rᵀ diag(1/(Rt+b)) R with b the out-of-grid signal known term and no physics background ("signal-only"), which is the Gram matrix of the whitened R. Per-functional CR widths, null fractions (cut 1e-12 relative), invisible share. Branch C: 121 of 144 eligible J residuals in functionals with CR width > 10 % at both truth resolutions | (a) **estimator:** the current reported route, FD-PRR / T3 configuration (e) and F0b's ensembles, in place of the retired GBDT; (b) **background:** V_r includes the expected physics background besides the known term; (c) **exposure:** the data exposure, D-ID's "analysis exposure", with background; (d) **truths:** FD-PRR / T3 at A7 GiBUU and q3, F0b's graded truths, A2's at 2D, in place of D1/W1/W3/q3/W2; (e) **2D:** new; (f) **cells:** the 16 reported cells R00–R15 on H2 truth cells, in place of the J cells; (g) **combinations:** it reads the bias along constrained and unconstrained *combinations* of reported cells, not per functional; (h) **feature sets:** the 3D/4D/5D reco comparison is new |
| **FD-PRR R-ID** (2026-11-08; `FD-PRR-DECLARATION.md:201-208`, `prr_ibu.py:252`) | D-ID's `did.fisher` and `did.widths_from_eig` on the H2 response, prior and known term captured from the nominal truth's fold unfold (half A at ×2, with the template). Per reported cell: sigma_rel and null_fraction; also n_cells_grid and n_null_modes. "Descriptive, read by nothing"; the note does not cite it | The reading response is built by **the same code** (REF-G1's H2 World, `ibu1`'s response construction, `did.response`), but from the **full MC at ×1** with the full background template (§3.1). R-ID's own construction, half A at ×2, is rebuilt **only as the input to the STOP control C-RID**. Combinations rather than cells |
| Coverage scoping R1, "identifiability ladder" (2026-10-22, `measurement-scoping/SCOPING.md:43,108,363`) | Proposed D-ID's Fisher at 2D–5D. Never run | This study is the first run of that question at 2D, and at 5D for the current estimator |
| pv2d/cmodel, pv-ladder H2, DECISION-20261024 | Singular values of S, the generator-spread factor of C_model (rank 3) | Not the response. Not used |
| s5e diagnosis (DIAGNOSIS-20260926 :145) | A capacity probe gave a better reco fit with no better truth, read as "part of the residual is weakly constrained" | Qualitative precursor only |
Search: identifiability ladder; singular value; response SVD; identifiab; weakly constrained; poorly constrained; Fisher; R-ID; Cramér–Rao (CATALOG, OUTCOME-*, DECISION-*, state/**/*.md, docs/analysis-note on main and on rewrite/journal-voice-20261121) @ 7d5a98361

**Does the new builder reproduce D-ID?** It is tested as C-DID (§6), at T1 with D-ID's own settings: full MC, same sample,
the out-of-grid known term and no physics background, nominal weights (`did.Diagnostic.problem(grid="T1", role="same",
weighting="nom")`). Whether C-DID gates is decided by a scripted test, not a judgment.
- **The test, C-DID-CONS, in connect P** (`msr_build.py did-cons`):
  - it builds IBU-1's J world and D-ID's T1 grid, each through its own unchanged code, from the same events;
  - it writes four sorted lists: the J-cell truth definitions (fine-cell membership per J cell) and the occupied reco
    cells (flat indices), from each path;
  - it prints each list's sha256 and their equality.
- **If both pairs are equal,** C-DID is a STOP control. **If either differs,** C-DID is a printed comparison, and the
  differing list is named.
- Rev 3 records which branch holds, from connect P's log, before connect B runs.

## 2. Operands

| operand | identity | role |
|---|---|---|
| 5D events | `of_inputs_5d.npz` sha256 `07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f`, read from `/pscratch/sd/j/josephrb/t3p-20261121/stage/of_inputs_5d.npz` (T3's stage, this lane's) | R, t0, halves (§3.1) |
| 5D background | the background dump T3's stage holds beside it, at the digest `t3p-20261121/stage.json` records | the full background template (§3.2) |
| 2D bank | IBUKT's `bank.npz`, sha256 `60416384474d1a3b0644f1e09869cf09371382ecbf3c116b1ed110cd47341e2f` (A2's `bank_sha256`), at IBUKT's own path `/pscratch/sd/j/josephrb/ibukt-20261119-d/prepare/out/bank.npz` (`2d-unfolding/ibukt/connect.py:563`). Per the director's ruling of 2026-11-22: no search; that one file is read only through an O_NOATIME sha check and a dd iflag=noatime copy; nothing is written, renamed or opened plainly under the root; the root's and the file's stat (incl. atime) are recorded before and after; a sha other than A2's is a STOP | 2D R, t0, b, halves (§3.1) |
| T3 products | `t3p-20261121/runs/*.npz` for arms B0, MO, OP at A7 GiBUU (splits 991000, 994001–994004) and q3 (991000), at the sha256 in `run-20261121/cluster/log-floor/SHA256SUMS` | MO and OP bias vectors; P and X for C-L (§4, §6) |
| FD-PRR readout | `fd/receipts-prr/read/cluster/readout.json` sha256 `9238f22bfe29685e33c1d5bb46da3938a3ebfdc93a54575a4fe99de3a7af9ead` | B0 bias and departure vectors (`table`); R-ID (control only, §5.2) |
| F0b readout | `fd/readout/fd_f0b_readout.json` `b9db935a3187646ba2accaf3865cf4aa26ad72676063c58e7f5e6220224ef17b`; the with-C_PL copy `fd/with-cpl/readout/fd_f0b_readout.json` `5f542830561731b567f2b97d78e5e9677a9802a35ef9c21855828bf184e6f3d6` (C-F0B only) | F0b bias vectors (§4) |
| T3 readout | `fd/tier3-20261110/run-20261121/cluster/read/readout.json` `b0362c387ec3d8fd48616abe5dcf589407fd007b62214d6297b47418d1a9ecce` | C-T3's verdict check only |
| IBUKT A2 readout | `state/2d-closeout/ibukt-a2/readout.json` `dfae50f595ac37b5179722a6a9d264f758cce91c163ca6cc1ab3b03462da8da6` | 2D bias vectors (§4) |
| D-ID tables | `d-id/outputs/tables.npz` `2aab22703747bfbc33247fe015213c5d9d0a65dcfc0074f0e3c53a1de29327a4` | C-DID only |
| 3D/4D inputs | `methods-paper/re1-20261022/out/{3d,4d}/of_inputs_{3d,4d}.npz` on pscratch | sha256 and size recorded in connect P for the inventory. Not used: the feature-set comparison sums the 5D reco cells (§3.4) |

**Code reused unchanged**, each checked at this sha256 by C-OPS:

| file | sha256 |
|---|---|
| `docs/orchestration/state/next-preparation-20261009/d-id/did.py` | `d918c816080a292eecaa0cc182a73906b868bb75189056862cf88d7152c4bbbd` |
| `nd-unfolding/prior_retention/prr_ibu.py` | `fa91394507c0e6a32486af25fa52f7e162135cf6483519ccf15510e1c9473cb0` |
| `nd-unfolding/prior_retention/prr_read.py` | `d7c7c2c0d6cbe4a13d445a779335699de3d5275c4bcd3efc9f4e84a166868fbe` |
| `nd-unfolding/ibu1/ibu1.py` | `f862a953425c006f6c73f2190bd65172eb9295f0f6c181d3d2247d4de881cf12` |
| `nd-unfolding/ref_g1/ref_g1.py` | `8e34c48552857f5eec55e1067f70f4d26b2a6de0eaae46c57983fd91fbc6e7b1` |
| `nd-unfolding/s1_assemble.py` | `b157250af21a2ef74e4164db6009a40ac596e225f33ac655475798ef49f613f7` |
| `nd-unfolding/tier3/t3p_read.py` | `f4c221dda95fbbdf2318f7fcdde57b9e1b7fb265e85b13e1dea15341cf069295` |
| `2d-unfolding/ref_c2c1/ref_c2c1.py` | `285dd138363d090a4ce5dea3361be81fada8680bd782b918e9d95198d1b5d6ea` |
| `2d-unfolding/ibukt/ibukt.py` | `ef8590cf6d6d025b6db1fb8fdd100f76114390ac78eded62274b2c077c290789` |
| `2d-unfolding/ibukt/run_ibukt.py` | `f2b4c017e1a2e84c2cb30b43a8824b95c3f7e022f5fca23b0ceac2a750c33683` |
| `2d-unfolding/ibukt/config.json` | `60d6c4d747596137423a869ac315c484ef65ad69f3ec209d6fd73d6e573c716c` |

**From b1** (`b1_projection.py` `b0cf7d0d443dd59a72d0fca0d948b44066be9d3da3f3f925351ca9bae7512fb4`), only the
two-driver eigen pattern (`basis`) is imported. b1's `band_of` and `label` encode b1's own five bands, so `msr_project.py`
writes one band function per statistic of §5.1, with b1's form of "read only if the interval lies in one band".

## 3. Definitions

### 3.1 The response

- **5D.**
  - **The truth grid:** the H2 truth cells of REF-G1's g world (`ref_g1.worlds`), n_H = its `n_cells`.
  - **The reco cells:** the occupied 5D reco cells of the World.
  - **R** is built by `ibu1.unfold_ibu`'s own construction, captured where it calls `did.ibu` (as `prr_ibu.capture_ibu`
    does), with no IBU iteration run and no data or pseudo-data in the call.
    - It is called on REF-G1's **g world**, whose coarse map is H2 (`ref_g1.worlds`: `gw.coarse_of` =
      `s1.coarse_map(H2_EDGES)`). `ref_g1.unfold_experiment` calls the same `ibu1.unfold_ibu` on that world.
      `unfold_ibu` names its grid "J" as a literal, but the cells are H2's. The J world is used only for C-DID.
    - C-GRID checks the H2 identity (§6).
    - **For the reading:** a `Half` holding every row at weight ×1 (`ref_g1.full_half`).
    - **For C-RID:** half A at ×2 of FD-PRR's primary split, with that experiment's template.
  - R_ij is the expected reco count in cell i per unit truth count in H2 cell j, at the half's within-cell truth shape.
    t0 is that half's truth count per H2 cell (the captured prior).
- **The 5D reported map L (16 × n_H)** maps H2 truth counts to the 16 cross-section functionals R00–R15 that FD-PRR's b is
  defined on:
  - L_{·j} = the reported functionals (`gw.functionals`) of the cross section that `ibu1.extract` returns for H2 cell j's
    unit count spread over its fine cells by the prior shape (`did.share_matrix`);
  - the extraction is linear in the counts at fixed completeness, so L is exact;
  - FD-PRR's P (the nominal truth's cross section at the same split, from half B; `prr_read` §4.1, `t3p_read.priors`)
    is not L t0 (the full MC's prior) by construction. The ratio P/f0 converts FD-PRR's b to φ-units (§3.5) and is
    printed per cell (control C-L).
- **2D.**
  - From the bank's event arrays (`gen`, `reco`, `pr`, `pt`, `wt`, `wr`), `ref_c2c1.binned_problem` gives (T, M, y, t).
    y and t are discarded.
  - **R = M / T** columnwise. A column with T = 0 is set to 0. t0 = T.
  - The truth grid is `driver.PT_EDGES × PZ_EDGES`, with 224 reco bins.
  - L selects A2's 205 reported cells: the readout's `cells`, which are the bank's `selected` (205 integer cell ids,
    `run_ibukt.py:237-239`, `:402`), in that order. These
    are the cells A2's `mean`, `residuals` and `departure` refer to, and they are not `signed_identity.truth_indices`.
    The other truth bins are parameters and are marginalized.
  - At 2D each reported cell is one truth bin, so a per-cell scale (extraction, completeness) cancels in relative units.
- **Relative coordinates.** θ_j = t_j / t0_j, and φ_c = f_c / f0_c with f = L t and f0 = L t0. The Jacobian is
  G = diag(1/f0) · L · diag(t0). A cell with f0 = 0 is dropped from φ, and its count is printed.

### 3.2 V_r: known term and background, data exposure

- **μ = R t0 + b**, with **b = b_known + b_bkg**:
  - **b_known:** the reco-passing signal rows outside the truth grid or failing truth (`ibu1`'s `known_rows`; D-ID's
    out-of-grid term).
  - **b_bkg:** the expected physics background, the full background template at ×1 histogrammed on the reco cells
    (5D: `world.reco_hist` of the background dump; 2D: the bank's `bkg`/`bw`).
  - At 2D, b_known is the in-window reco-passing signal rows whose truth falls outside the truth grid, from the bank. A
    signal fake (pr and not pt) is refused, as IBUKT refuses it (`run_ibukt.py:360`).
- V_r = diag(μ), Poisson. Only reco cells with μ > 0 enter (D-ID AM-15).
- **Exposure.** The MC weights at ×1 are the data-exposure expectation: the data unfold uses the full MC at weight ×1, and
  the pseudo-data use half B at ×2 for the same reason (`M2-AUDIT.md` §Q1; `s5n_pseudo.build_data`). At 2D the bank's
  weights are the ones IBU used, and the bank's `factor` is printed.
- **No data count enters.**
- **Printed variants:**
  - **"D-ID settings":** b = b_known only. C-DID uses it (at T1).
  - **"b = 0":** printed, and no control depends on it.
  - **"R-ID settings":** half A at ×2 with that experiment's b. C-RID uses it.

### 3.3 Information, widths and combinations

- **The Fisher matrix, in count space** (D-ID's): F_c = `did.fisher(R, t0, b)` = Rᵀ V_r⁻¹ R over reco cells with μ > 0.
  (A = V_r^{-1/2} R diag(t0) and F = AᵀA = diag(t0) F_c diag(t0) are the same information in θ-space. Only F_c and the
  count-space gradient are used below, so the null space and the cut are D-ID's exactly.)
- **The count-space gradient of φ:** J = diag(1/f0) · L, of size n_cells × n_params.
- **The numerical range.** F_c's eigenpairs (λ, v), with D-ID's cut: λ > 1e-12·λ_max is the range, and the rest spans
  the null space N (basis V_N). F_c⁺ is the pseudo-inverse **on that same cut** (eigenvalues at or below it are not
  inverted).
- **U∞, per direction** (D-ID's rule, `widths_from_eig`: a functional is unconstrained if its null fraction exceeds
  1e-6).
  - The null fraction of a combination w (unit vector in φ-space) is ρ(w) = ‖V_Nᵀ Jᵀ w‖ / ‖Jᵀ w‖, `widths_from_eig`'s
    null fraction for the functional wᵀJ.
  - With M = J V_N V_Nᵀ Jᵀ and K = J Jᵀ, the generalized eigenproblem M u = ρ² K u gives directions u_i.
  - **U∞** = span{u_i : ρ_i > 1e-6}. **Q** = span{u_i : ρ_i ≤ 1e-6}, orthonormalized in φ-space with basis B_Q.
  - K must be positive definite, so J has full row rank after the f0 = 0 drop. Otherwise STOP (C-RANK).
  - On each coordinate direction e_c, ρ(e_c) must equal `widths_from_eig`'s null fraction for the functional e_cᵀJ (C-RHO,
    §6).
- **The constrained widths.** C_Q = B_Qᵀ J F_c⁺ Jᵀ B_Q has eigenpairs (s_k², c_k), and w_k = B_Q c_k. Each w_k is a unit
  combination of reported cells with binned Cramér–Rao width s_k in relative units.
- **The cut.** w_k is **well-constrained** if s_k ≤ 0.10. W = span of the well-constrained w_k, and n_well = dim W.
  - **P_well** = the orthogonal projector onto W, and **P_poor** = I − P_well. "Poorly constrained" is everything outside W:
    the w_k with s_k > 0.10, and U∞.
  - Every unit vector in W has width ≤ 0.10, because C_Q restricted to W is diagonal with entries ≤ 0.01. The converse
    does not hold: a unit combination outside W can also have width ≤ 0.10 (a mixture weighted to a well-constrained
    axis). The readings speak of W only (§5.1).
- **Basis of the cut.** It is D-ID's 10 % CR-width criterion, the same number, applied to a unit-norm combination of
  reported cells instead of to a single functional.
  - Relation to D-ID: a single cell c has width² = Σ_k (w_k·e_c)² s_k², and is infinite if e_c has a component in U∞. So a
    cell is weak in D-ID's sense if, and in proportion as, it loads on poorly constrained combinations.
  - The threshold is fixed here and not tuned.
  - The partition at 0.05 and at 0.20 is printed and read by nothing.

### 3.4 The feature sets (5D only)

- The 3D and 4D reco feature sets are the 5D reco cells **summed** over dropped reco axes, pinned to the World's edge
  vectors by name: W for 4D; q3 and W for 3D. The 3D set is (p_T, p∥, E_avail), the 4D set adds q3 and the 5D set adds W
  (`nn_dump_inputs.py --axes eavail` and `eavail,q3`, RE1-AMENDMENT §2.2).
- **R and b are summed in the same way.** F is rebuilt from the summed R and b, and the whole §3.3 chain is repeated per
  set.
- The truth (H2), the reported cells (L) and t0 are the same for all three sets, so the comparison isolates what each reco
  variable adds.
- C-MARG checks that the reco cells lie on the World's product grid, that the dropped axes are the named ones, and that
  the sums conserve Σ R and Σ b.

### 3.5 The bias vectors (relative to the prior, on reported cells)

- **FD-PRR's b_c = (X̂_c − X_c) / P_c** (§4.1 there), with P the nominal truth's functionals at the same split and X
  the known truth's. In φ-units the bias is **δφ_c = b_c · P_c / f0_c**, with f0 = L t0 (C-L prints the ratio).
- A bias given relative to the truth, e_c = X̂_c / X_c − 1 (F0b's `rel`; A2's e), is converted as
  δφ_c = e_c (1 + d_c) · P_c / f0_c, with d_c = X_c / P_c − 1:
  - for F0b, d is from FD-PRR's table entry of the same truth name at split 991000 (the same truth files; control C-D);
  - for A2, d is from A2's own `departure` (`ibukt.py:197`, truth/prior − 1). A2's prior is the bank's `truth_nominal`,
    in cross-section units, and t0 = T is in counts. At 2D each reported cell is one truth bin, so P/f0 is the per-cell
    ratio `truth_nominal` / (`factor` · T). It is computed from the bank, printed, and used as is. It is expected constant
    in relative units, and its spread is printed beside it.

### 3.6 The statistics

For a bias vector β = δφ:
- **S_poor = ‖P_poor β‖² / ‖β‖²**, the share of the bias's **sum of squares** (relative units) outside the
  well-constrained span. The isotropic reference (n_cells − n_well) / n_cells is printed beside it.
- **Z_well = √(Σ_{k well} (w_k·β)² / s_k²)**, the largest bias in **any** unit combination in W, in units of that
  combination's binned CR width at the data exposure. It is max over a ∈ W of |a·β| / width(a). The per-axis maximum
  max_k |w_k·β| / s_k is printed and not read.
  - **If n_well = 0,** Z_well is the sentinel **"no well-constrained combination"**, which is never "below".
- **For an arm A against B0** (T3, same truth and split, k = 5):
  - **r_poor** = 1 − ‖P_poor β_A‖ / ‖P_poor β_B0‖. It is computed only if ‖P_poor β_B0‖ > 0.005; otherwise it reads "no
    poorly constrained component to remove".
  - **r_well** = 1 − ‖P_well β_A‖ / ‖P_well β_B0‖. It is computed only if ‖P_well β_B0‖ > 0.005; otherwise it reads "no
    well-constrained component to remove".
- **Intervals.** Every statistic f gets an interval [f_lo, f_hi]:
  - **5-split means** (FD-PRR and T3 at A7 GiBUU): f is computed on the mean vector of the five splits, and on each split's
    vector f_s. The interval is f ± h, with h = 2.7764451051977987 · sd(f_s) / √5, where sd is the sample standard
    deviation with divisor 4 (ddof = 1, as b1). This is b1's guard form, descriptive, since the statistics are not linear.
    - For r_poor and r_well: if any split fails its 0.005 floor, the r reads "unresolved across bands".
  - **Noisy vectors** (F0b, A2): 2,000 Gaussian perturbations of β with independent per-cell SD, RNG seed 20261122:
    - F0b's SD is `noise_sigma`, a declared approximation, since F0b's covariance is not committed;
    - A2's SD is the sample SD of the five trials over √5.

    f is computed on β. The interval is the 2.5 % and 97.5 % points of f over the perturbed vectors, used as is
    (asymmetric).
  - **Single-split vectors** (q3) have no interval and are secondary.
- **The floor on ‖β‖.** ‖β‖₂ has an interval by the same rule. For a single-split vector, the interval is the point.
  - **"no bias to locate":** the interval lies below 0.01;
  - **"unresolved at the floor":** the interval contains 0.01;
  - **S_poor is read** only if the interval lies above 0.01.
  - **Basis:** 0.01 is a 1 % relative norm over the reported cells, twice the 0.005 floor on the r. Fixed here.
- **The noise maximum for Z_well (noisy vectors only).** The same 2,000 perturbations, applied to a **zero** vector, give
  Z_noise = the 97.5 % point of Z_well under noise alone, printed beside Z_well. With n_well = 0, Z_noise is not computed
  and Z_well keeps its sentinel.
  <!-- absence-ok: a declared computation rule of this study (what is skipped when n_well = 0), not a claim that a result does not exist --> FD-PRR and T3 vectors are noise-free
  constructions at fixed splits; their split spread enters through h, and they have no Z_noise.

## 4. The tested bias vectors

| set | vectors | role |
|---|---|---|
| **5D-B0** | FD-PRR's B0 b at A7 GiBUU: the mean over the five splits (991000, 994001–994004), with the individual splits giving the interval (§3.6). FD-PRR's B0 equals T3's (T3's C-PAIR, rechecked by C-T3) | **primary** |
| **5D-ARMS** | T3 MO at A7 GiBUU at k = 5 (configuration (e)'s iteration count), and OP at k = 2, its only and final iterate (`t3p_arms.ITERS["OP"] = 2`, the step-2 bound T3 reads as ρ_OP(2)): the five-split mean, with the splits giving the interval | **primary** (M2) |
| 5D-ARMS at k = 50 | T3 B0 and MO at A7 GiBUU (five splits) and q3, at k = 50, the k at which the note prints T3's values. OP has no k = 50 | **printed secondary**, under §5.2's pairing rule |
| **5D-F0b** | F0b's graded truths with n_experiments ≥ 16: nominal, W1, W2, W3, q3, stage0c_gibuu, A7_mnvtune, A7_genie_cv, A7_genie_mec, A7_nuwro, A7_gibuu | **primary** |
| 5D secondary | FD-PRR B0 and T3 B0/MO at q3 (one split, k = 5), and T3 OP at q3 (k = 2); F0b closure_nuwro (N = 0); F0b P-sets (ungraded) | printed, marked secondary |
| **2D-A2** | A2 OmniFold mean at nominal, genie_mec, nuwro (5 trials) | **primary** |
| 2D secondary | A2 OmniFold at bump, tilt, within_plus, within_minus; IBU K=5 and K=10 at every truth | printed, marked secondary |

No vector, truth, split, k or set not listed here is computed for reading.
<!-- absence-ok: a pre-declared scoping rule about this study's own vectors, not a claim that a result does not exist -->

## 5. Readings, fixed before any computation

### 5.1 Bands, labels and sentences

**One set of inequalities** for each statistic:

| statistic | band | range | sentence it licenses (t = the truth, D = 2D or 5D) |
|---|---|---|---|
| S_poor | **poor-dominated** | S ≥ 0.8 | "At truth t (D), at least four fifths of the bias's sum of squares lies outside the combinations of reported cells that the binned detector-level inputs constrain to 10 % or better at the data exposure." |
| | **mixed** | 0.2 < S < 0.8 | "…between a fifth and four fifths of the bias's sum of squares lies outside the well-constrained combinations." |
| | **well-dominated** | S ≤ 0.2 | "…at least four fifths of the bias's sum of squares lies in combinations the binned inputs constrain to 10 % or better." |
| Z_well | **below** | Z < 1 | "In every combination in the span of the eigen-combinations of reported cells that the binned inputs constrain to 10 % or better, the bias is below one binned Cramér–Rao width at the data exposure." |
| | **intermediate** | 1 ≤ Z < 2 | "In some combination in that span the bias reaches between one and two binned CR widths, and in none does it reach two." |
| | **resolvable** | Z ≥ 2 (noisy vectors: see below) | "In some combination in the span of the eigen-combinations the binned inputs constrain to 10 % or better, the bias is at least two binned CR widths: a component the binned data could resolve carries it." |
| | **within the noise maximum** (noisy vectors only) | Z ≥ 2 but not above Z_noise (below) | "In some combination in that span the bias reaches two binned CR widths, but no more than noise alone would give across it; no component is resolved." |
| | **no well-constrained combination** | n_well = 0 | "No combination of reported cells is constrained to 10 % or better." |
| r_poor, r_well | **removes most** | r ≥ 0.5 | "Arm A removes at least half of B0's bias in the poorly (well-) constrained combinations." |
| | **removes part** | 0.2 ≤ r < 0.5 | "…between a fifth and a half…" |
| | **no change** | −0.2 < r < 0.2 | "…changes it by less than a fifth, either way." |
| | **increases** | r ≤ −0.2 | "…increases it by at least a fifth." |
| | sentinels | §3.6 | "No poorly (well-) constrained component of B0's bias to remove." |

**The interval rule.**
- A label is read only if [f_lo, f_hi] lies inside one band. Otherwise the reading is "unresolved across ⟨bands⟩", in b1's
  sentence form.
- **For a noisy Z_well:**
  - **resolvable** requires f_lo ≥ 2 **and** f_lo > Z_noise;
  - **within the noise maximum** requires f_lo ≥ 2 and f_hi ≤ Z_noise;
  - an interval with f_lo ≥ 2 and f_lo < Z_noise < f_hi reads "unresolved across within-the-noise-maximum and
    resolvable". An interval with f_hi = Z_noise (and f_lo ≥ 2) is "within the noise maximum";
  - an interval reaching below 2 follows the plain rule.
- A statistic that N-PREC (§6) or the MC control (§5.3) marks reads "numerically unresolved" or "MC-unresolved", with no
  reading.

**Combined statement per truth.** The first case that applies is used:
1. **points at a resolvable component:** Z_well resolvable. This holds **whatever S_poor or the floor reads.** "At truth t,
   a combination the binned inputs constrain to 10 % or better carries at least two binned CR widths of bias. This points
   at an estimator effect that the binned data could in principle resolve; it does not show that it is fixable, or how."
2. **no bias to locate** (or **unresolved at the floor**): the ‖β‖ floor (§3.6).
3. **consistent with an information limit:** S_poor poor-dominated **and** Z_well below. "At truth t, the bias lies
   outside the span of the eigen-combinations the binned inputs constrain to 10 % or better, and is below one binned CR
   width everywhere in that span. This is consistent with an information limit of the binned inputs; it does not show that no estimator could
   remove it."
4. **all combinations poorly constrained:** n_well = 0. "No combination of reported cells is constrained to 10 % or
   better; the bias's location among combinations is not tested."
   <!-- absence-ok: a pre-written licensed sentence for a declared outcome of this study, not a claim that a result does not exist -->
5. **intermediate:** every other case where both statistics are resolved. Both labels are reported, with no summary
   sentence.
6. **unresolved:** either statistic is unresolved. Its kind is reported.

**Across truths, per set:** b1's §3 rule:
- "unresolved at ⟨truths⟩" if any primary truth is unresolved;
- otherwise "⟨statement⟩ at every tested truth" if all agree;
- otherwise "truth-dependent", with each truth's statement reported.

### 5.2 Readings

- **M1 (primary):** S_poor, Z_well and the combined statement for every 5D-B0, 5D-F0b and 2D-A2 vector.
- **M2 (primary, the oracle arms):** r_poor and r_well for MO at k = 5 and OP at k = 2, each against B0 at k = 5, at A7
  GiBUU, by §5.1's bands.
  - **The licensed MO sentence:** "At k = 5, the true missed-event weights remove mainly the poorly constrained part of
    B0's bias." It requires r_poor "removes most" **and** r_well "no change" or the well sentinel. The mirror sentence (r_well
    "removes most" and r_poor "no change" or the poor sentinel) reads "…mainly the well-constrained part…". Every other
    resolved case is reported label by label.
  - OP is the bound on what step 2 can reach (T3 §3.3), at its only iterate k = 2. It is read by the same bands and stated
    as that bound, and every OP sentence names "k = 2".
  - **The pairing rule.** M2 reads k = 5, the reported estimator's iteration count, while the note prints T3's values at
    k = 50. An M2 sentence at k = 5 is never paired or juxtaposed with the note's k = 50 values, or with this study's
    k = 50 printout, as if they described the same unfold.
    - Every k = 50 line in the readout carries "k = 50, secondary; not M2".
    - Every M2 sentence names its k: "k = 5" for B0 and MO, "k = 2" for OP.
    - The one allowed mix is OP at k = 2 against B0 at k = 5, which is T3's own comparison of the step-2 bound with the
      reported estimator. Every other mix of iterations is forbidden.
- **M3 (5D, feature sets):**
  - It reads n_well, n_mid (the constrained combinations with s_k > 0.10) and dim U∞ for the 3D, 4D and 5D reco feature
    sets. Each count is read only if MC-resolved (§5.3).
  - **The licensed sentence:** "With the ⟨D⟩ reco feature set, n combinations of the 16 reported cells are constrained to
    10 % or better at the data exposure, p are constrained to worse than 10 %, and m are unconstrained."
  - The difference between sets is stated as a count, with no cause. The principal angles between the well-constrained
    subspaces of consecutive sets are printed.
- **M4 (2D):** the same three counts at 2D, by the same rule.
- **R-ID.** FD-PRR's committed R-ID values are used **only** in the STOP control C-RID (§6): reproduce them under R-ID's
  own settings.
  - They are not an operand, they enter no reading, and no new sentence about them is licensed.
  - I have seen the R-ID field names (`label`, `sigma_rel`, `null_fraction`, `n_cells_grid`, `n_null_modes`) and not
    their values.
  - The run prints them only inside C-RID's comparison.
- **Printed and read by nothing:**
  - the spectra s_k and F's H2-level spectrum;
  - the partitions at 0.05 and 0.20;
  - the "b = 0" and "D-ID settings" variants at H2;
  - the per-axis maximum of Z_well;
  - per-cell D-ID-style widths and null fractions at the data exposure with background;
  - R00–R15 alone (L = identity on the 16 cells, truth = the 16 cells), as Q3's comparison;
  - every secondary vector.

No band, cut, set, truth, k or exposure is changed after any statistic is computed.
<!-- absence-ok: a pre-declared rule about this study's own readings, not a claim that a result does not exist -->

### 5.3 The finite-simulation control (split-half R): only MC-resolved quantities are read

- R and t0 are also built from MC half A and half B of the **signal** MC, each at ×2:
  - 5D uses the split key of seed 991000, FD-PRR's;
  - 2D uses `s5c_pseudo.half_mask` at key 20261122.
- b_bkg is the same full-exposure template in the full build and both halves; only the signal MC is halved. b_known comes
  from each half's own rows at ×2.
- **The same φ-space first:** the set of cells dropped for f0 = 0 must be equal at full, A and B. Otherwise every reading
  of that dimension reads "MC-unresolved".
- **A reading is MC-resolved** only if its label is the same at full, half A and half B, and the partition is stable:
  - n_well and dim U∞ are each equal at full, A and B;
  - ‖P_well^A − P_well^B‖₂ ≤ 0.2 and ‖P_well^full − P_well^X‖₂ ≤ 0.2 for X = A, B.

  Otherwise it reads "MC-unresolved".
- **A combination counts in M3/M4** only if all of these hold:
  - it is matched one-to-one across the halves (the assignment maximizing Σ|w_k^A·w_j^B|, Hungarian), with
    |w_k^A·w_j^B| ≥ 0.9;
  - the same holds against the full build;
  - its widths at full, A and B lie on the same side of 0.10.

  dim U∞ is read only if it is equal at full, A and B.
- Each half has half the MC, so this test is conservative for the full build.

## 6. Controls (a STOP control's failure stops every reading and goes to the director with its values; no repair round)

| id | check | bar | STOP? |
|---|---|---|---|
| C-OPS | every operand and code file at its full sha256 (§2) | exact | STOP |
| C-RID | under R-ID's settings (half A at ×2 of FD-PRR's primary split, the nominal fold unfold's prior and b, `did.fisher`, `widths_from_eig`, prr_ibu's `maps`), the 5D construction reproduces FD-PRR's committed R-ID: `sigma_rel[16]` and `null_fraction[16]` (∞ matches ∞), `n_null_modes` and `n_cells_grid` | finite sigma_rel relative ≤ 1e-6; null_fraction absolute ≤ 1e-6; counts exact | STOP |
| C-DID-CONS | connect P: IBU-1's J-world and D-ID's T1 J-cell definitions and occupied reco cells, as four sorted lists compared by sha256 (§1). The lists are fetched, so a reco DIFFERS is checked for the upper-edge convention (IBU-1's window excludes the last edge, D-ID's `flat_index` keeps it) before it is read as a different grid | exact | decides whether C-DID gates; recorded in rev 4 |
| C-DID | the J world at T1 under D-ID's settings (full MC, same sample, b = b_known, nominal weights) reproduces `tables.npz` `T1/nominal/widths_nom/{sigma_rel,null_fraction}` on the functionals both name | as C-RID | STOP if C-DID-CONS is equal; otherwise printed |
| C-L | 5D: L is linear and equals the extraction: L t = `ibu1.extract(share · t)` for t0 and for two positive random t, and the reported map equals T3's M16 (`h2_definition`). The P that converts FD-PRR's b to φ-units is `t3p_read.priors`' P (FD-PRR's nominal product at the same split), with the ratio P/f0 printed per cell (P is half B's nominal truth, f0 the full MC's, so they are not equal by construction). 2D: the readout's `cells` has 205 entries, is equal for every primary truth, and equals the bank's `selected` ids (205 distinct integers in 0..223) | relative ≤ 1e-12; exact | STOP |
| C-GRID | the 5D reading capture and the R-ID capture report the same grid `n_cells`, equal to the number of non-empty H2 coarse cells under the g world's `coarse_of`, and to the committed R-ID's `n_cells_grid` | exact | STOP |
| C-RHO | ρ(e_c) (§3.3) equals `widths_from_eig`'s null fraction for e_cᵀJ, at every reported cell, for each build | absolute ≤ 1e-9 | STOP |
| C-RANK | G has full row rank after the f0 = 0 drop (K positive definite) | smallest eigenvalue of K > 1e-12·largest | STOP |
| C-T3 | B0 at A7 GiBUU (five splits) and q3, at k = 5, recomputed from T3's products by `t3p_read`'s b_c, equals FD-PRR's committed `table` b; the T3 readout's verdict is COMPLETE | 1e-12 absolute; exact | STOP |
| C-F0B | `truths[].bias` equal in the two F0b readouts | exact | STOP |
| C-D | each F0b truth used has an FD-PRR table entry of the same name at split 991000 with a 16-vector d | exact | STOP |
| C-A2 | A2's means recomputed from the five residuals equal `mean` (b1's C-A2); the bank's sha256 equals A2's `bank_sha256` | 1e-15; exact | STOP |
| C-2D | `binned_problem` on the bank's arrays reproduces the bank's `ibu_response` (= M) and `ibu_prior` (= T); b_bkg and b_known each built twice, by `ibukt.histogram` and by `ref_c2c1.global_index` on `config.json`'s edges (no `re2_driver` import), are equal cell by cell | relative ≤ 1e-12 | STOP |
| C-MARG | the 5D reco cells lie on the World's product grid; the dropped axes are W (4D) and q3, W (3D) by name; the sums conserve Σ R and Σ b | exact map; relative ≤ 1e-12 | STOP |
| C-ROUTE | S_poor and Z_well (and each r) by the eigen route (§3.3) equal those by an independent route (W from a pivoted QR of the well-constrained block; χ²_well by solving rather than by eigenvalues) | \|ΔS\| ≤ 1e-10 + 1e-8·\|S\|; \|ΔZ\| ≤ 1e-10 + 1e-8·\|Z\|; \|Δr\| ≤ 1e-10 + 1e-8·\|r\| | STOP |
| **N-PREC** | every eigen-decomposition with two LAPACK drivers (numpy `eigh`, scipy `eigh(driver="evr")`). For a vector, "numerically unresolved" if the partition differs, if S_poor or an r differs by > 0.01, or if \|Z_numpy − Z_evr\| > max(0.01, 0.01·Z). With n_well = 0 the numeric Z test is skipped (the sentinel is compared as a label) | as stated | per reading |

**Synthetic tests before any real input** (`test_msr.py`):
- a toy R with a planted spectrum:
  - β in the poor span gives S_poor = 1, and β in W gives S_poor = 0;
  - Z_well equals the planted span maximum, including a two-axis case where the per-axis maximum is below 1 and Z_well is
    above 1;
  - a duplicated column puts its difference combination in U∞;
  - a direction with a tiny null component under a global cut but a null fraction > 1e-6 goes to U∞ (Grok 2's case);
  - R = [1, 1] with t0 = [1, 1e7]: the difference combination, which `widths_from_eig` marks infinite, lands in U∞ and
    outside W, and ρ on the coordinate directions matches `widths_from_eig` (rev-2 read, item 1);
- the C-RID path on a fixture reproduces `prr_ibu.r_id`'s output exactly;
- the 3D/4D summation on a toy product grid equals direct binning, with F rebuilt;
- every band edge of §5.1, each sentinel, the floor's three branches, the noise-maximum rule's three cases, and the order
  of the combined statement;
- the Hungarian matching on a permuted, sign-flipped basis;
- a line tracer runs every new line before the read.

## 7. Products and limits carried to the result

- **Products.** Code (`msr_build.py` for the cluster step, `msr_project.py` for the local step, `test_msr.py`), the
  fetched response files, `readout.json`, `readout.txt` and a REPORT go under this directory. They are committed before the
  results go to the director. The two reads of rev 1 are in `reads/`.
- **Limits:**
  - **Binned, local information.** Fisher widths assume the Poisson Gaussian limit and are local at the nominal
    expectation. They do not bound unbinned estimators or estimators that use prior information. Coarse truth cells hide
    within-cell freedom (optimistic), and binned reco hides reco information (conservative). Neither error is bounded
    here (D-ID §5).
  - **V_r** is at the nominal expectation for every truth, a linearization. Detector-systematic covariance is not in V_r.
    Only statistical constrainability at the data exposure is measured.
  - **The cut** is D-ID's number applied to unit combinations. It is a convention with a stated basis, not a physical
    threshold. S_poor can be poor-dominated while below its isotropic reference, when the poorly constrained span is most of
    the dimension. The reference is printed for that reason.
  - **The bias vectors** are those already measured, at development truths, on one simulated bank. Their noise is handled
    as stated, not sampled anew.
  - **"Consistent with an information limit"** says where the bias lies, not that it cannot be removed.

## 8. The cluster step (scripts follow, each sha to the director before it runs)

- **Connect P, the probe** (0 node-h, login node).
  - The fence: cov2d rev 2, `cov2d_fence.sh` sha256 `3fbc9cbd6c08d4c86c71aeeccf28b0b3d8a77393121ef23787c1d421b682171e`,
    plus an overlap check of this study's input set (§2) against the cov2d and rpd protected paths and
    limitation-resolver's flux2 input set, on fresh acks.
  - stat and sha256, with O_NOATIME, of every §2 input and of the 3D/4D inputs for the inventory. The 2D bank is the one
    file at IBUKT's recorded path, with the stat of the root and of the file before and after the copy (§2).
  - C-DID-CONS, always, whatever the gate reads. Both sides' exit codes are checked, and an incomplete side records
    INCOMPLETE (rc 6), not EQUAL or DIFFERS.
  - A timed build at row fractions 0.02 and 0.10 of each response. Each subsample is written by a separate process, so
    the timed process never holds the full arrays. The connect prints wall time and in-process peak RSS, and the full
    build's two-point linear extrapolation.
  - No PyROOT read is made anywhere in this study (§2's operand change).
  - It writes only under a fresh `$OUT` on pscratch, and nothing to CFS.
- **Connect B, the build.**
  - **The gate is hard:** on a login node if the probe's extrapolation for every response is ≤ 30 min wall and ≤ 8 GB peak
    RSS. Otherwise one shared-QOS job of at most 0.1 node-h, with job-name prefix **`msr_`**, which the director announces to
    every fenced lane first.
  - It builds the full, half-A and half-B responses at 5D and 2D, the R-ID-settings and D-ID-settings captures, L, P and
    T3's B0/MO/OP b vectors. All are small npz files under `$OUT` with a SHA256SUMS.
  - It reads with O_NOATIME, from pinned shas, in a fresh clone at a pinned commit, and writes nothing to CFS. T3's
    products, SHA256SUMS, stage.json and the FD-PRR nominal copies are read through O_NOATIME copies into the build's own
    stage. The files are fetched by dd streaming with a sha check.
- Everything after the fetch is local.

<!-- absence-ok: a declaration of an unrun study; "nothing is computed" describes its own order of work -->
