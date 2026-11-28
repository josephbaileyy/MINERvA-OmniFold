# (b) part 3: the 5D bias block and fluctuation block (declaration, rev 1; tier3-design, 2026-11-24)

**Authority:**
- Joseph's decision, relayed by the director on 2026-11-24: "yes build the 5D bias block". That is part 3 as priced:
  no new unfolds.
- The director's rulings of the same day:
  - (a) f̂ comes from LL5D's toys, with F0's cal sets as a printed flux-only cross-check;
  - (b) the expectation is LL5D's own rebuilt per-truth block, and no S1 per-universe product is read;
  - C_b's family is nominal plus the three C_model vertex truths.
- The spec is `~/codex-reports/note-measurement/b-design-20261124/B-SPEC-DRAFT.md` (2c735ebc…), "Open before binding":
  the 5D bias and fluctuation matrices.

**This text is fixed before any input below is read for this purpose.** Its sha256 goes to the director before the
read connect, and nothing is tuned on the output.

**Simulation only.** Nothing here reads data, a seal, or a sealed output, and nothing reads S1's data-derived
per-universe products.

## 1. What the build produces, and what it does not decide

**It produces, in a committed record:**
- C_b^5D, the fitted bias allowance, in Tune v1 units and in absolute units;
- f̂_R, its SE and its trigger outcome per band;
- V_F^5D, the fluctuation block after the band factors;
- the diagnostics printed below.

**Whether an inflated V_F, or C_b, becomes part of the REPORTED 16-cell covariance is Joseph's adoption decision.** It
goes to him, through the director, with these numbers. The reported covariance is unchanged by this build. It is
`fd/with-cpl/deposit-candidate/covariance-reported.csv`, sha256
`76730c5b7143f8933019a502ca23eed635e45340f7d1ed5534813b2242956170`.

**Its intended use** is to give the reported 16-cell covariance a 5D bias block and fluctuation block before any (b)
support claim attaches to it (spec, "Open before binding").

## 2. Inputs

The `fd/` paths are under `docs/orchestration/state/measurement-paper/5d-community-20261024/`.

**Committed, read at the binding's commit with these sha256:**

| input | sha256 | used for |
|---|---|---|
| `fd/with-cpl/readout/fd_f0b_readout.json` | `5f542830561731b567f2b97d78e5e9677a9802a35ef9c21855828bf184e6f3d6` | b̂ for the C_b family and the diagnostics |
| `fd/readout/fd_f1_readout.json` | `cbe411a926a7392e4aa085c7beba6e1bda45aff55d937998c53e49f27e3516c7` | b̂ at G18 and AR23 (printed against C_b) |
| `fd/receipts-prr/read/cluster/readout.json` | `9238f22bfe29685e33c1d5bb46da3938a3ebfdc93a54575a4fe99de3a7af9ead` | R = 1 + d (as B-SEL §2) |
| `fd/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_readout.json` | `a19009e0bd83b9bb8f9ad65fb65804e6f62c8953310103fbfe6fce5f84995875` | g_TuneV1, for the absolute C_b |
| `fd/with-cpl/data-product/fd_data_product_cpl_C_e.csv` | `222c4dd4efef0780c408b82caa8d360723bc8b73b784885789f374a624e6c715` | F_A^5D = the reported C_e, the matrix the band factors act on |
| `s1/readout/s1_assembly.json` | `81e5ef3fe8e7b055360dc43b8a8240c9b5c39c8aa6e7c507b3211d305b326b21` | the committed per-cell relative σ of `flux` and `stat`, for the cal-set cross-check only |
| `ben-b-20261124/selection-20261124/record/selection/fd_f0b_experiments.npz` | `7384c6518aa0f59bd4964170fcc9b652f1c31958f422f1e1b597cd3e59219ad9` | S_t for the C_b family; the cal sets |
| `ben-b-20261124/selection-20261124/record/selection/fd_f1_experiments.npz` | `997c7dae34ef9703291baece51eed05f3dd7d38a043630cac9667efaad2775bc` | the F1 diagnostics |
| `ben-b-20261124/selection-20261124/record/selection/L-5D-PV_e_closure_{tune_v1,nuwro}.npz`, `f1_closure_genie_v3_{g18,ar23}.npz` | as in B-SEL §1 | R for closure_nuwro and the F1 tunes (as B-SEL §2) |
| `fd/receipts-ll5d/hpss-u/hpss_ll5d_u_list.tsv` | `980bb95e20eac386a220bb7d0dbb16a5a3477248688f9a72bc07671a7ad5842d` | the pins of LL5D's products |
| `fd/receipts-ll5d/null/node/null-g18.json`, `null-ar23.json` | `73dbaf9517374646c719ff589015cb12c1a6a2eafd5579e1074ef700bde703c2`, `a0544ab9f6f0ec55c9866bee689d2563b13c9d07f4b3fdc37ce4762718a23933` | C-LL5D: the products LL5D graded against |
| `nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89` | U, the cell functional |

**Fetched by one bound login read connect** (O_NOATIME, each copy refused unless it is its pin in
`hpss_ll5d_u_list.tsv`). There are 1,654 files from `/pscratch/sd/j/josephrb/ll5d-unfolds-r2`, 498.1 MB, in the
manifest's two groups:
- **`toys`**: 1,200 files (421.9 MB), 300 per reading (`all`, `minus2`) at each of G18 and AR23;
- **`null_roles`**: 454 files (76.2 MB), the products LL5D's blocks were remade from at each truth:
  - `central_T` and `seed_T`;
  - the 175 `block` universes;
  - the 50 `stat` replicas.
- **Not fetched:** `extras`, which are 4 data-control products (data) and 4 clipmeans, and `sidecars`.
- **Plus one more file:** the flux constraint LL5D's Flux band was weighted with,
  `/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt`.
  - It is the `--flux-constraint` of every LL5D unfold and null line, and MINERvA's own parameter file.
  - It is pinned by `s1_assemble.CONSTRAINT_SHA256` =
    `e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2`, which F0b's readout also records as its
    `constraint` input. The copy is refused unless it is that pin, and C-FLUX (§5) checks it further.
- A purged file is retrieved by htar from LL5D's HPSS archive on a loginNN, never a DTN, only as its own amendment.

**Code reused unchanged:** `ll5d.layout` and `ll5d.TOY_SEEDS`, and through `ll5d_b`:
- the reading's bands (`ll5d_b.bands_of`);
- `s1_assemble`'s `EXPECT`, `mat_cov`, `functional_matrix` and `fine_map` (code only; no S1 product is read);
- `ll5d_b.products_digest`.

`fd_1b_score.surrogate` and S1's lateral and normalization blocks are **not** used: they need the data result and
S1's assembly.

## 3. The bias block C_b^5D

- **The family F,** non-spent and COVFIX's analogue: **nominal, A7_genie_mec, A7_nuwro and A7_gibuu**, the prior and
  the three C_model vertices.
- **Per member t:**
  - β_t = b̂_t ⊙ R_t, in Tune v1 units, with R_t as in B-SEL §2 (R = 1 at nominal, 1 + d at the A7 truths);
  - Σ_t = diag(R_t) N_t diag(R_t), with N_t = Cov(r_t)/B_t (ddof 1, the full 16 × 16) from the F0b table: nominal's 40
    row-1 experiments, and the A7 truths' 16 row-4 splits.
  - This is COVFIX's S_t/(N_t − 1) with S_t the ddof-0 covariance: the same matrix.
- **C_b = [Σ_{t∈F} (β_t β_tᵀ − Σ_t)]₊.** [·]₊ is the eigen-decomposition with negative eigenvalues set to 0 (numpy
  `eigh`). The rank is at most 4. It is the sum, not the mean, as in COVFIX.
- **Absolute:** C_b,abs = diag(g_TuneV1) C_b diag(g_TuneV1), with g_TuneV1 from `fd_g_readout.json`.
- **Printed against C_b (never summed):**
  - the diagnostics W1, W2, W3, stage0c_gibuu and closure_nuwro;
  - the spent tunes F1_genie_v3_g18 and F1_genie_v3_ar23, as β = b̂ ⊙ R;
  - LL5D's toy mean error at G18 and AR23 (the raw error of §4, per reading), divided by the Tune v1 cell integral
    through R.
  - For each: βᵀ C_b⁺ β, the fraction of ‖β‖² outside C_b's span, and the undebiased member bound βᵀ(C_b⁰)⁺β for F's
    members.
- **What C_b is, and is not** (COVFIX's words carry over). It is a fitted bias allowance. The positive part changes its
  expectation. It is not claimed to bound any model class.

## 4. The fluctuation block V_F^5D

**The ensembles.**
- **Primary:** LL5D's `minus2` toys at G18 and at AR23, N = 300 each.
- **Printed beside them:** the `all` readings, which pair with `minus2` (shared streams) and are not independent.
- **Why the spent tunes may enter here.** COVFIX left G18 and AR23 out of its fitted factors because in 2D they were the
  sealed validation truths. In 5D, (b)'s held-out truths are PV's sealed truths (u = 0, 1, 2 under rev 12), and G18 and
  AR23 are not among them. So COVFIX's reason does not carry over, and using them here takes nothing from (b)'s
  held-out test.

**The expectation (the drawn part only).** At each truth T and reading, D = Σ_{band ∈ reading} C_band + C_stat:
- C_band = `mat_cov` of the band's universe products at T, flux-weighted for Flux, uniform otherwise, exactly as
  `ll5d_b.remade` forms them;
- C_stat = Cov(50 stat replicas), ddof 1.
- The laterals, the normalization and C_model are **not** in D, because the toys do not draw them.

**The errors:** e_s = U·xsec_flat_s − U·xtrue_flat_s per toy s. These are raw, with no surrogate. The centred errors are
e_s − ē.

**The basis.** D's eigenbasis by numpy `eigh`, each eigenvector signed so its largest-magnitude component is positive,
exactly tied eigenspaces by COVFIX's Gram–Schmidt rule. The kept modes are λ_i > 1e-12 λ_1.

**Per mode:** z_{s,i} = u_iᵀ(e_s − ē)/√λ_i and v_i = (1/N) Σ_s z²_{s,i}.

**Bands by eigen-rank:** R1 = ranks 1–4, R2 = 5–8, R3 = 9–16. A band with fewer than 4 kept modes is dropped and named.
- This is a disclosed departure from COVFIX's 2D bands (73 / 66 / rest, with at least 10 modes). The 16-cell space
  has only 16 modes.

**The measured factor:**
- F̃_R(E) = mean_{i∈R} v_i / ((N − 1)/N);
- **f̂_R = (1/2)(F̃_R(G18, minus2) + F̃_R(AR23, minus2))**;
- SE(f̂_R) = the standard deviation over **2,000** joint bootstrap replicates, toys resampled within each ensemble at
  seed 9_991_000, eigenbases fixed at the full-sample D.

**The trigger:** band R is active if and only if f̂_R − 1 > 3·SE(f̂_R). Then φ_R = f̂_R; otherwise φ_R = 1. Factors are
never below 1.

**The block.**
- F_A^5D = the reported C_e (§2), the stat and universe part plus the laterals and normalization at the data.
- L = I + Σ_{R active} (√φ_R − 1) P_R, with P_R the projector onto band R's ranks of **C_e's** own eigenbasis (same
  sign and tie rules).
- V_F^5D = L F_A^5D Lᵀ.
- f̂_R is a rank-band summary transferred from D's basis at T to C_e's basis at the data. It is not a mode-matched
  estimate, and that is disclosed.

**If the bootstrap cannot resolve f̂** (SE(f̂_R) > 0.5 in every band), the build stops short of V_F. The case goes to
the director with the price of new toys (the fallback is not authorized).

**The cal-set cross-check (printed, never entering f̂).** For each of the five `cal_<A7 truth>` sets in the F0b table,
compare:
- the per-cell unweighted standard deviation of r;
- √(σ_flux² + σ_stat²) per cell, from `s1_assembly.json`'s `relative_sigma`.

These sets draw Poisson plus one flux universe each, so they speak to the flux block only.

**The disclosed gap, not graded:**
- the laterals and the normalization, about 17% of C_e's trace (`s1_assembly.json` trace_share 0.141 + 0.028);
- GEANT_Neutron and GEANT_Proton, absent from the primary `minus2`;
- C_model, 42% of C_total's trace, which is the bias block's job;
- C_resp and C_PL5D (the run period), which no ensemble at any truth varies;
- finite-MC split variation, which is not a component of the reported covariance.

## 5. Controls (each a STOP)

- **C-PIN:** every committed input at its sha256 above, and every fetched copy at its manifest pin.
- **C-LL5D:** `ll5d_b.products_digest` over the fetched `central`, `seed`, `block` and `stat` products equals each null
  record's `products_sha256`; and each reading's toys are exactly `ll5d.TOY_SEEDS[truth]` (300).
- **C-SEED:** U·central_T equals U·seed_T exactly at each truth (LL5D's own seed check).
- **C-FLUX:** `s1_assemble.flux_weights` on the fetched constraint reproduces two values in `s1_assembly.json`'s
  `meta.flux_weights`, to 1e-12 relative:
  - the sum, 211.01200325082078;
  - the effective count, n_eff = 19.060534772246488, from (Σw)²/Σw².
  This ties the file to the weights S1, and through `ll5d_b.remade` LL5D, used.
- **C-TAB:** the F0b table's nominal and A7 sets reproduce the readout's bias and noise_sigma to 1e-12 (as B-SEL).
- **C-PSD:** each D is positive definite on the kept modes, and C_b is positive semidefinite after [·]₊.
- **C-FIN:** every F̃, f̂ and SE is finite, and every band denominator is positive.
- **C-LEAK:** no absolute cross section in the record, except C_b,abs and V_F^5D, which are covariance matrices in
  (cm²/nucleon)² like the reported one.

## 6. The 5D reproduction test (declared here; its own small binding)

- **The test.** One pair of unfolds of the frozen 16-cell estimator (E_R) on identical inputs: one on a CPU node and one
  on a GPU node's CPUs, at matched threads (32), seed (42) and deploy commit.
- **Pass** if and only if max relative difference ≤ 1e-8 on R00–R15 and on the 5D cross section. Bitwise is expected:
  gpu-timing-20261023's K-T1 found 16 of 16 products byte-identical across node types.
- **Cost:** about 0.1 node-h of each kind.
- It has its own script, connect and binding. It is not run by this build.
  <!-- absence-ok: a scoping statement: the reproduction test runs under its own binding, not this build -->

## 7. Outputs, code and what this cannot authorize

- **Code:** `nd-unfolding/b5d/b5d_build.py`, with tests, a line trace and mutants. Reads come first: agy on
  `gemini-4-hydrogen-xhigh`, since this gates a support claim, and codex-school, with every finding fixed.
- **The record** (`blocks5d.json`, `blocks5d.txt`, and the matrices as CSV, with their sha256) is committed under this
  directory and goes to the director first.
- **CAN:** C_b^5D, f̂_R with SE and trigger, V_F^5D, and the diagnostics, as candidates for Joseph's adoption decision.
- **CANNOT:**
  - change the reported covariance;
  - any coverage or support claim;
  - any held-out statement;
  - any data statement;
  - any note wording.
