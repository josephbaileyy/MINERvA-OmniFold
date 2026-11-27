# DECLARATION: the bias and fluctuation split of the sixteen-cell held-out-tune closures under C_rep with C_e^infl (rev 1; tier3-design, 2026-11-27)

**Under:** Joseph's approval of item (A) for v1, relayed by the director on 2026-11-27, with these rulings:
- the carry of C_e^infl to each tune is rule (i), `carry_frac(DeltaC_e, X_T, f)`, the COV2D C08 rule REGRADE already
  uses for C_resp, as primary, with rule (ii) printed beside it;
- the debiased bias term ēᵀC⁻¹ē − tr(C⁻¹S)/N is added;
- the readings are declared before anything is computed, and the circularity is stated here as in the scoping note;
- 0 node-h, local only.

**After:** REGRADE (`fd/regrade-crep-20261121/`, REGRADE-DECLARATION.md `20697e6b…`, record `run16/capture/regrade16.json`
`df590558…`), which already splits M′ into a mean-error part and a spread part for the pre-V_F matrix; the V_F
adoption (`FD-VF-ADDITION-DECLARATION.md`, the block `fd/with-vf/block/vf_block.npz`), whose §8 left LL5D and REGRADE
unchanged because a tune-carried DeltaC_e "would need its own prescription". This record is that prescription.

**This text is fixed before any number below is computed.** Its sha256 goes to the director first. Nothing is tuned on
the output.

**MEASURES:** per held-out-tune evaluation, the split of the mean χ²/ndf of LL5D's 300 coverage pseudo-experiments
against the reported covariance with C_e^infl, carried to the tune, into a debiased bias term, a fluctuation term and
the added-block term τ.

**CANNOT AUTHORIZE:** any change to a reported covariance; any note or paper wording (rewrite-helper drafts, Joseph
approves); a coverage or calibration statement; a validated size of C_e^infl or of C_rep; a cause; a p-value.

The `fd/` paths are under `docs/orchestration/state/measurement-paper/5d-community-20261024/`.

## 1. Inputs (all committed; each read only after its sha256 matches)

| input | sha256 | used for |
|---|---|---|
| `fd/regrade-crep-20261121/run16/capture/capture_g18_minus2.npz` | `2fae21c50ea983395216f1781f64ead974ebc4dee5b0957bca5f6079a9cd1f8b` | E, X_T, f, C_T, C_e(T) |
| `fd/regrade-crep-20261121/run16/capture/capture_g18_all.npz` | `29a9f1d5842924008574bc55d425d12c6f71a0cd901d516f505cb1154c11bfb8` | same |
| `fd/regrade-crep-20261121/run16/capture/capture_ar23_minus2.npz` | `7212996c87cd3526764f7d38779e8d36b4daa0fa5099f50a34d9800ede18a9c2` | same |
| `fd/regrade-crep-20261121/run16/capture/capture_ar23_all.npz` | `97b3d915f40a27026c9cc71bec5fc01fdaf0b9e067016257266dfcfbc5cea313` | same |
| `fd/regrade-crep-20261121/run16/capture/regrade16.json` | `df5905586ef4d05894363ea85557578d65be5164eab327c90303e69a874d8054` | control C-A0 |
| `fd/with-cpl/block/cpl_block.npz` | `d9aa32fdb64357760348c9ccbc32fbea81d517f0f0786eedf17ab4946eaca59f` | f, C_resp, P_rel |
| `fd/with-vf/block/vf_block.npz` | `cef8460a1dcc0db64f536af0099db1e1523ed2601d5c8ecc682afc0f9440c99b` | f, C_e, C_e_infl, DeltaC_e |
| `ben-b-20261124/blocks5d-20261124/record/blocks5d.json` (under `docs/orchestration/state/`) | `c465768b490acc96515c5340585b8ff1f14735254f269af605ffaf182ae521f9` | φ_R and L for rule (ii) and control C-L |

**Code imported unchanged:** `fd/regrade-crep-20261121/regrade_crep.py` (`479e03cc…`): `r_chi2`, `carry_frac`,
`carry_rel`, `Stop`, and through it `fd_1b_null.chi2_nonnull`. Nothing it imports is edited.

**The draws** are LL5D's held-out-tune coverage pseudo-experiments, N = 300 per evaluation, at the GENIE v3 tunes G18
and AR23, each in two readings: `minus2` (without the GEANT4 neutron and proton bands) and `all`. The `all` reading
shares its streams with `minus2` at the same tune, so the two are not independent. E holds the raw errors
e_s = U·xsec_s − U·xtrue_s (`ll5d_b.toy_errors`, as captured by REGRADE).

## 2. The matrices, per evaluation (T, reading), 16 × 16, absolute units at T

- From the capture: E (300 × 16), X_T, f, C_T = C_e(T) + C_model_abs(T), and C_e(T).
- C_add(T) = `carry_frac(C_resp, X_T, f)` + `carry_rel(P_rel, X_T)`, exactly REGRADE's (C_resp and C_PL,5D at T).
- **Rule (i), primary:** dF_i(T) = `carry_frac(DeltaC_e, X_T, f)` = diag(X_T/f) DeltaC_e diag(X_T/f), with DeltaC_e
  = C_e_infl − C_e from `vf_block.npz`.
- **Rule (ii), printed beside:** dF_ii(T) = L_T C_e(T) L_Tᵀ − C_e(T), where
  L_T = I + Σ_R (√φ_R − 1) P_R(T), P_R(T) = Σ_{i∈R} u_i u_iᵀ over C_e(T)'s eigenvectors (numpy `eigh`, ranked by
  descending eigenvalue), R1 = ranks 1–4, R2 = 5–8, R3 = 9–16, and φ_R = `blocks5d.json`
  `fluctuation.trigger[R].phi` (every band ACTIVE: R1 1.0912…, R2 1.2924…, R3 2.9774…). This is B5D's own
  construction (B5D-DECLARATION.md §4) applied to the tune's C_e instead of the data's.
- **The covariance under test:** C_rep(T; v) = C_T + dF_v(T) + C_add(T), for v ∈ {i, ii}. At the data this is the
  reported C_total + C_resp + C_PL,5D + DeltaC_e; at T it is REGRADE's C′ with C_e replaced by its inflated carry.
- **Before (printed for comparison):** C′(T) = C_T + C_add(T), REGRADE's matrix, without DeltaC_e.

**τ covers C_add(T) only, not dF_v(T).** τ stands for blocks the draws do not vary (the response and run-period
terms). dF stands for spread the draws already show (it was fitted to it, §5), so adding it to τ would count that
spread twice. In code: `r_chi2(E, C_T + dF_v(T), C_add(T))`.

## 3. The quantities, per evaluation and matrix

Let A be the inverse of C on its non-null subspace and ndf its rank, as `fd_1b_null.chi2_nonnull` forms them
(eigenvalues above 1e-12 of the largest). N = 300.
- M′ = mean_s e_sᵀ A e_s / ndf, and SE = sd(e_sᵀ A e_s, ddof 1)/√N/ndf (`r_chi2` `M_prime`, `SE`).
- B_raw = ēᵀ A ē / ndf (`r_chi2` `mean_error_part`).
- S₁ = Σ_s (e_s − ē)(e_s − ē)ᵀ / (N − 1).
- **The fluctuation term:** F = tr(A S₁) / ndf.
- **The debiased bias term:** B = B_raw − F/N. With independent draws of common mean b and covariance Σ,
  E[B] = bᵀAb/ndf and E[F] = tr(AΣ)/ndf.
- The identity M′ = B + F holds exactly (B_raw + F(N − 1)/N = B_raw + `spread_part`); it is control C-ID.
- τ = tr(A C_add(T)) / ndf (`r_chi2` `tau`), and M_full = M′ + τ = B + F + τ.
- The shares B/M_full, F/M_full and τ/M_full.
- **Bootstrap SEs** of B, F and B − F: 2,000 resamples of the N draws with replacement, `numpy.random.default_rng`
  seeded per evaluation (g18/minus2 9_991_271, g18/all 9_991_272, ar23/minus2 9_991_273, ar23/all 9_991_274), with A
  held fixed at the full sample's C. The same resample indices serve every matrix of an evaluation.

## 4. The readings (fixed here)

**Primary:** rule (i) at g18/minus2 and ar23/minus2. The `all` evaluations are printed beside them and are not
independent of them.

Per evaluation, under rule (i):
1. **The numbers:** B, F, τ, M_full, SE, the three shares, and the bootstrap SEs.
2. **REGRADE's R-χ² reading, unchanged:** "under-describes on average" iff M_full − 1 > 3·SE, else "not shown".
3. **Bias resolved:** "yes" iff B > 3·SE_boot(B), else "not resolved".
4. **Bias against fluctuation:** "bias larger" iff B − F > 3·SE_boot(B − F); "fluctuation larger" iff F − B >
   3·SE_boot(B − F); else "not separated".

**Rule (ii)** gets the same numbers and classes, printed beside rule (i). If any class or R-χ² reading differs between
(i) and (ii) at any evaluation, the record names that evaluation as "carry-sensitive". Rule (ii) decides nothing
else.

**Before:** the same B, F, τ and classes for REGRADE's C′ (no DeltaC_e), so that the change made by C_e^infl is shown
on the same draws with the same definitions.

Every reading is descriptive. None is a coverage result.

## 5. The circularity (stated as the scoping note put it)

The draws here are the same draws C_e^infl was fitted to. B5D (RECEIPT.md `6277f5cb…`, B5D-DECLARATION.md §4) built its
factor f̂_R from these LL5D toys: primary `minus2` at G18 and AR23, f̂_R = ½(F̃_R(G18) + F̃_R(AR23)); the `all` readings
were printed only and share streams with `minus2`. f̂_R uses the CENTRED errors e_s − ē, so it measures spread only,
relative to D = Σ drawn bands + C_stat in D's eigen-rank bands R1 (ranks 1–4), R2 (5–8) and R3 (9–16) at T; φ_R is
then transferred by rank band onto the data's C_e eigenbasis.

**What the split can show:**
- The bias term is a fair reading of the mean error against the inflated matrix: its numerator ē never entered f̂.
  It is not strictly independent, because the matrix was scaled from the same draws' spread.
- The fluctuation term shows what is left after the factor's approximations: averaging over the two tunes, averaging
  over the modes within a band, and the transfer from D(T)'s basis to C_e(data)'s (or, under rule (ii), to C_e(T)'s).
  It also shows how much C_model, C_resp and C_PL,5D, which the draws do not vary, dilute it.

**What it cannot show:**
- That C_e^infl or C_rep is the right size. The fluctuation term is partly fixed by construction in D's bands, so a
  value near or below its share is expected and is not a test of the matrix.
- Coverage or calibration of C_rep.
- Whether any remaining excess is estimator bias or variance the draws do not contain (the laterals and the
  normalization, about 17% of C_e's trace; C_model; C_resp; the run period).
- Anything independent from the `all` readings.

A fluctuation check that is not circular would need fresh pseudo-experiments at a truth the factor never saw.

## 6. Controls (each a STOP, recorded unrepaired)

- **C-PIN:** every §1 input and the imported `regrade_crep.py` equal their sha256.
- **C-A0:** `r_chi2(E, C_T, C_add(T))` reproduces `regrade16.json`'s `R_chi2` fields `M_prime`, `SE`,
  `mean_error_part`, `spread_part`, `tau` and `M_full` at every evaluation, each within 1e-12 relative.
- **C-F:** the f of `vf_block.npz`, of `cpl_block.npz` and of each capture agree within 1e-12 relative.
- **C-DF:** `DeltaC_e` equals `C_e_infl − C_e` within 1e-12 of max|C_e_infl|, and `carry_frac(DeltaC_e, f, f)`
  equals `DeltaC_e` within the same bound.
- **C-L:** the rule (ii) builder applied to `vf_block.npz`'s C_e with `blocks5d.json`'s φ_R reproduces `C_e_infl`
  and `blocks5d.json`'s L, each within 1e-10 of its largest element. This checks the builder at the data before it is
  used at T.
- **C-GAP:** in `vf_block.npz`'s C_e and in each C_e(T), λ₄/λ₅ − 1 and λ₈/λ₉ − 1 both exceed 1e-9, so that each band's
  projector is unambiguous.
- **C-PSD:** dF_i(T), dF_ii(T) and each C_rep(T; v) are symmetric within 1e-12 relative, with smallest eigenvalue at
  least −1e-12 of the largest.
- **C-RANK:** ndf = 16 for every C_rep(T; v) and C′(T), and `r_chi2`'s `C_T_kept_modes_outside_C_prime_kept_span` is 0.
- **C-ID:** |M′ − (B + F)| ≤ 1e-12·M′ for every matrix and evaluation.

A STOP at an evaluation leaves its readings unwritten. The record keeps the STOP text.

## 7. Code, record and order

- **Code:** one new driver, `fd/regrade-vf-20261127/regrade_vf.py`, with `test_regrade_vf.py` and a mutation runner,
  all in this directory. The driver writes one JSON record, refused if the file exists, and prints only each
  evaluation's status.
- **Order:**
  1. this declaration, committed, with its sha256 to the director;
  2. the driver, the tests and the mutants;
  3. one codex-school read of the code (agy if codex-school is low), and fixes;
  4. the code's sha256 to the director before the real run;
  5. one local run;
  6. the record committed before any number in it is read;
  7. the receipt, with the readings, to the director.
- **Cost:** 0 node-h; nothing on NERSC.
