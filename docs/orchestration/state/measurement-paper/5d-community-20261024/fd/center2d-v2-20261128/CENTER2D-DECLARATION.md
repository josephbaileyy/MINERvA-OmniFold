# DECLARATION CENTER2D: how far the nominal-centred 2D covariance sits from the mean-centred one, at the data and at the two held-out tunes (rev 1; tier3-design, 2026-11-28)

**Under:** Joseph's "sure lets put it on the v2 list" (2026-11-27) and "lets do 2" (2026-11-28), relayed by the
director. The director accepted the plan on 2026-11-28 with seven rulings, applied here:
1. the scope, three size measures, the T2A rank bands, the controls and the decision rules as planned, fixed here
   before any number is computed;
2. the training-noise term (D11) is reported beside the raw term, or, if the universes share X₀'s training seed,
   recorded as "noise term not separable, disclosed", with no correlated-noise model built on the fly;
3. no grade rerun with C_T′ + M;
4. COVFIX independence (§9);
5. the fence families and the atime rule for the connect (§8);
6. if the inputs are purged, part D STOPs and comes back as a separate costed ask, and the tunes still report;
7. v2 and records only: nothing in `docs/analysis-note` or on Overleaf.

**After:** tier3-design's pricing note of 2026-11-27, item 1, which priced this from the App. A review's Comment 2
("have we quantified the difference?"). §10 corrects one input it named.

**This text is fixed before any number below is computed.** Its sha256 goes to the director, who reviews and merges
it. Nothing is tuned on the output.

**MEASURES:** for each universe band b of the reported 2D covariance, the offset of the band's centre from the
nominal unfold, and the size of the summed outer product M = Σ_b b bᵀ against the covariance it would be added to.
That covers the reported data covariance C_new and the adopted tune covariances C_T′ at AR23 and G18. All of it is
descriptive.

**CANNOT AUTHORIZE:**
- any change to a covariance or its centring convention (that is Joseph's, and would interact with COVFIX);
- any note, paper or Overleaf text (v1's App. A keeps its convention sentence, #1436);
- a coverage statement or a cause;
- any statement that separates physical response asymmetry from training noise (§4).

The `fd/` paths are under `docs/orchestration/state/measurement-paper/5d-community-20261024/`. Every committed file
below was read at origin/main `02ae86003006bcaf50c1f509b45d84256bc17d81`. Each sha256 is of the file's bytes, computed
with `shasum -a 256`.

## 1. The quantity

The reported universe bands are MAT-centred (DRAFT-disclosures D12: "each universe band's covariance is taken about
the mean of its universes, with the constraint-weighted mean for Flux and 1/N normalization").
- The code is `band_cov` (`2d-unfolding/re2/partc/re2c_rollup.py:199`).
- It calls `wcov` (`docs/orchestration/state/2d-closeout/c04-repair/scripts/build_repair.py:127`), which takes
  μ = Σ_i w_i X_i / Σ_i w_i and returns Σ_i w_i (X_i − μ)(X_i − μ)ᵀ / Σ_i w_i.
- w is the 100 constraint weights for Flux and 1 for every other band.

For a band with universes X_i (n_u × 205) and the nominal unfold X₀ of the same data:
- **mean-centred** (reported): V_mean = wcov(X, w);
- **nominal-centred:** V_nom = Σ_i w_i (X_i − X₀)(X_i − X₀)ᵀ / Σ_i w_i;
- **their difference is exact:** V_nom − V_mean = b bᵀ, with b = μ − X₀. This holds for any weights, so for the
  two-universe bands, 2p2h's three universes and Flux's 100 weighted universes alike.

**The bands:**
- the 38 weight bands (175 universes);
- the 5 lateral bands: BeamAngleX, BeamAngleY, MuonResolution, Muon_Energy_MINERvA and Muon_Energy_MINOS, with two
  universes each. Muon_Energy_MINOS enters through its X01 rescale `minos_x`, as `universe_block`
  (`re2c_rollup.py:256`) uses it;
- the normalization entry is not a universe band and is excluded.

M = Σ_b b_b b_bᵀ over these 43 bands. M is what V_nom would add to the reported covariance.

## 2. Where it is measured, and against which covariance

| part | universes X_i | X₀ | covariance under test C | status |
|---|---|---|---|---|
| **D, the data (the answer)** | weight bands: `data_g2r.npz` `band__<b>` (G2R's 175 corrected universe unfolds); laterals: part B's 10 `S3_<L>` unfolds, MINOS × X01 scale | E_R, `cov2d_Q_205.npz` `x` | C_new, `data_g2r.npz` `C_new` | needs the read (§8) |
| **T, the tunes AR23 and G18** | `blocks_g2r_<T>.npz` `band__<b>` (43 bands) and `minos_x` | `x_T` | C_T′, `blocks_g2r_<T>.npz` `C_T` | needs the read (§8) |
| **R, the rehearsal** | committed `blocks_<T>.npz` `band__<b>` and `minos_x` (pre-G2R) | `x_T` | the superseded C_T, `blocks_<T>.npz` `C_T` | local, committed |

- **C_new is the reported 2D covariance.** It was adopted on 2026-11-14 (`DECISION-20261114-joseph-d1-g2r-adopted.md`,
  `c834794b…`). The G2R re2shapes receipt says "the reported 2D covariance is `data_g2r.npz`'s C_new"
  (`fd/receipts-cov2d/g2r/re2shapes/run2/README.md:6`, `41b53dfe…`).
- **C_T′ is the adopted tune covariance.** COV2D-G2R §4 (`225a89ae…`) builds it from the corrected universes at each
  tune and keeps every other block of `blocks_<T>.npz`.
- **Part R describes a superseded matrix.** It carries no label (§5) and exists to run the whole driver on committed
  inputs before any connect. Its readings go to the director like the others.
- **A tune result does not carry over to the data's matrix** (COV2D-DECLARATION.md:226-227, `0328c916…`). The labels
  in §5 are decided at part D. Part T's labels are printed as descriptions only.

## 3. Inputs

**Committed, each read only after its sha256 matches:**

| input | sha256 | used for |
|---|---|---|
| `fd/receipts-cov2d/readout/AR23/blocks_AR23.npz` | `abaebaeae6c9cb075dcb974a420dbf148809d01b2cabc8deda31f318bf6715ee` | part R; C-X0 and C-FLUX at AR23 |
| `fd/receipts-cov2d/readout/G18/blocks_G18.npz` | `7eb657b82ae953bdf0584eda27264c52a64bcb48baea52dfc194f5efe440ea3d` | the same at G18 |
| `fd/receipts-cov2d/g2r/readout/data/data_g2r.json` | `cd975b64402325da489ae608277faf5f6d7a7cbebe4974465f90b07c336e083f` | `npz_sha256`, verdict PASS, flux-weight sum and n_eff |
| `fd/receipts-cov2d/g2r/readout/AR23/score_g2r_AR23.json` | `fb6d1f7fddfa18124bf097087a2f895582ef0991f9888c5ab1ce16cefbbe3079` | `blocks_npz_sha256`, `controls_failed` [] |
| `fd/receipts-cov2d/g2r/readout/G18/score_g2r_G18.json` | `27374aab74793444ee20561ced1066247b225a40067092d7d181e186128b9ec2` | the same |
| `docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/SHA256SUMS` | `bf259be46ef1c4ddf8e6a18bfd49e1626b04f9a284e42a4024403e66ed60e25b` | digests of `outA/cov2d_Q_205.npz` and `s5/production_cov.npz` |
| `docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/s5/s5.json.gz` | `5c489837f999ea4bf8ea416be7d67fa5ba9e3107acf32cfc18f74545a1ee705e` (decompressed `ec4a407b…`) | S5_R's lateral product digests, its pins and X01 checks |
| `docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partb_readout/sums/SHA256SUMS.J*` (35 files) | concatenated in name order: `d3e89361695bd95735bd918008a741377782bf7f3635f146e76b567e1cac77d9` | digests of `ER/xsec.root` and the 10 `S3_<L>/xsec.root` |

**Local, already verified:** E_R's `xsec.root` at `/Users/josephbailey/c2eff-data/c2eff-run1/files/inputs/001_xsec.root`,
sha256 `a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef`. That is part B's `ER/xsec.root` digest, and
C2-EFF's verified fetch. It is used for C-X0 at the data.

**On pscratch, read once (§8):** 16 files, each checked against the committed digest named.

| file | sha256 | digest from |
|---|---|---|
| `/pscratch/sd/j/josephrb/cov2d-g2r-20261112/readout/data/data_g2r.npz` | `3b8cc7ceaef97c3dc6bbcd2c5cfdf853442c347e37e23f64eca54898d0e9eb4b` | `data_g2r.json` `npz_sha256`; `data/README.md` |
| `/pscratch/sd/j/josephrb/cov2d-g2r-20261112/readout/AR23/blocks_g2r_AR23.npz` | `c060cb40232e0112ec440951f94841e87fc98b542a165eed2c8242898508a70a` | `score_g2r_AR23.json` `blocks_npz_sha256`; `AR23/out.sha256.txt` |
| `/pscratch/sd/j/josephrb/cov2d-g2r-20261112/readout/G18/blocks_g2r_G18.npz` | `55ad7cc4faa4680b49391a9d68f52fcaa707150bd1300915063d66a16be9bfbe` | `score_g2r_G18.json`; `G18/out.sha256.txt` |
| `/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partc-r2/outA/cov2d_Q_205.npz` | `7153b194b95c27f80db5997bdde35fe2475f2b1c40c9ff456edd409850cf47d2` | partc-r2 `SHA256SUMS` |
| `/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partc-r2/s5/production_cov.npz` (S5_R) | `631cf255fff43b5cb35acd9cefdcee99e5ee95b85dc2f30d8e0aca513095eea1` | partc-r2 `SHA256SUMS` |
| `/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out/S3_<L>/xsec.root`, 10 files: `<L>` in BeamAngleX0/1, BeamAngleY0/1, MuonResolution0/1, MuonEnergyMINERvA0/1, MuonEnergyMINOS0/1 | each its part-B digest (for example `S3_BeamAngleX0` `b8bf4ac3…`, `S3_MuonEnergyMINOS1` `d380303a…`) | part B `SHA256SUMS.J*`, equal to S5_R's `inputs.production_outputs` |
| `/pscratch/sd/j/josephrb/2d-closeout-c04repair-20261012/build/minos_rescaled.npz` | `8912376ef2a6cfce8bed515cc945d9d5778cf5c838154a685435c3c7ce25416d` | S5_R `inputs.vl175_minos_npz`; `re2c_export_cov.py:63` |

**What each fetched file supplies:**
- `data_g2r.npz`: `C_new`, `C_univ_new`, `C_univ_old` and the 38 `band__<b>` written at `g2r_readout.py:315`.
- `blocks_g2r_<T>.npz`: the layout of `g2r.blocks_npz_arrays` (`g2r.py:254`), namely `C_T`, `C_univ`, `C_lat`,
  `x_T`, `rep`, `minos_x`, `w_flux` and 43 `band__<b>`.
- `cov2d_Q_205.npz`: `Q` (Q_R) and `x`.
- S5_R: `band_<b>` for all 43 bands and the normalization.
- `minos_rescaled.npz`: `scale`, the X01 factor. S5_R's checks `s3_x01_scale_equals_vl175` and
  `pin_vl175_minos_npz` are both True in the committed `s5.json`.

**The data's X01:** minos_x[u] = (H_u ⊙ scale[u][:, None]) flattened in C order on E_R's 205 cells, with H_u the
`hXSec2D` contents of `S3_MuonEnergyMINOS<u>`. That is `re2c_rollup.x01`'s last line, using the scale S5_R checked
against this file. C-RECON (§6) tests the result against S5_R's own MINOS block.

## 4. The training-noise term (D11): not separable, disclosed

**Do the universes share X₀'s training seed? Yes, at the data and at the tunes.**
- **Data:** part B's argv gives `--seed 42` to E_R (J1), to all 175 universes and to all 10 laterals
  (`docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partb_runs.tsv`, `526b70e0…`). RE2-PARTB-REPORT.md:202
  (`6b896a71…`) records `random_state` 45 (seed + 3) for 522 core rows.
- **G2R's corrected universes:** they ran "at estimator seed 42 and part B's thread configuration"
  (COV2D-G2R-DECLARATION.md:99).
- **Tunes:** COV2D's unfolds use seed 42 for every unfold (COV2D-DECLARATION.md:138; `2d-unfolding/cov2d/jobs/cov2d_jobs.py:35`,
  `09bcc7b9…`). G2R's tune universes take E_R's argv (COV2D-G2R §4).

**So, under ruling 2, the record writes `noise_term: "not separable, disclosed"`.** There is no noise-expectation
column, no difference column and no D11-scaled column. The independent-noise expectation (1 + 1/N_b)·S would be the
wrong model here, and no correlated model is built.

**What can still be said, and what this declaration uses.** Write each band's b as b̄ + n:
- b̄ is b averaged over training seeds;
- n is the training-noise deviation, so E_seed[n] = 0 by definition.

Then E_seed[b bᵀ] = b̄ b̄ᵀ + Cov_seed(b), and Cov_seed(b) is positive semi-definite. This is an identity. It assumes
nothing about how the noise in X_i and X₀ is correlated. So **the raw M is, in expectation over training seeds, at
least the seed-averaged term Σ b̄ b̄ᵀ.** Any one realization (this one, at seed 42) can fall on either side.

**The disclosure the record carries:**
- D11 (DRAFT-disclosures:298, `8512fccd…`) measured the seed SD of six universes' shifts U(s) − CV(s), with the
  universe and CV at the same seed s, at a median 1.24–1.33 σ_ML (stageC REPORT.md:128, `47a44fba…`).
- That is the only measurement of this noise. It was made on Stage C's July universes, not on part B's or G2R's.
- It is cited, not used.

If the director wants a noise reference column (for example a diagonal-only one built on the S4(ii) panel), that
is a separate costed addendum.

## 5. The readings and the decision rules (fixed here)

For each part and covariance pair (M, C), in C's absolute units.

**The non-null subspace:** C = U Λ Uᵀ by `numpy.linalg.eigh`, ranked by descending eigenvalue. The retained ranks are
the eigenvalues above 1e-12 of the largest. ndf is their count. This is COV2D's and G2R's rule.

**Readings:**
- **R1, trace share:** s_tr = tr(M) / tr(C). Printed beside it, as a description: tr(M) / tr(C_sys), with C_sys the
  sum of the 43 band blocks. At the data C_sys is C_univ_new plus S5_R's five lateral blocks; at a tune it is
  `C_univ` + `C_lat`.
- **R2, per cell:** d_c = M_cc / C_cc. Printed: the median, the 84th percentile, the maximum and its cell (GlobalID).
- **R3, whitened by rank:**
  - r_k = u_kᵀ M u_k / λ_k for each retained rank k;
  - the rank-band means over ranks 1–73, 74–139 and 140–ndf (T2A's bands);
  - the overall mean, which equals tr(C⁺M)/ndf;
  - the largest r_k and its rank.
- **R4, the largest added fraction:**
  - ε = the largest eigenvalue of Λ^{-1/2} Uᵀ M U Λ^{-1/2} on the retained ranks;
  - the coupling ‖P_⊥ M U Λ^{-1/2}‖₂ to the discarded ranks, printed beside it, as G2R prints its ε.
- **R5, per-band attribution:**
  - R1 and the three R3 rank-band means for each band's b bᵀ alone. All are linear in M, so they sum to the totals
    (C-ADD);
  - the five largest bands by each;
  - the decision quantities with each band left out in turn, printed as the range.
- **R6, per-band offsets** (descriptive):
  - the median over cells of |b_c| / X₀_c;
  - the median over cells of |b_c| / √(V_mean,cc) for the band.

**The labels, decided at part D:**

| label | rule |
|---|---|
| **NEGLIGIBLE** | s_tr < 0.01 **and** every R3 rank-band mean < 0.10 |
| **APPRECIABLE** | any R3 rank-band mean ≥ 0.10 |
| **INTERMEDIATE** | anything else (s_tr ≥ 0.01 with every rank-band mean < 0.10) |

**How each label reads, fixed now:**
- **NEGLIGIBLE:** nominal centring would add less than 1 % of the trace, and less than 10 % on average in every rank
  band. By §4 the seed-averaged term is, in expectation, no larger.
- **APPRECIABLE:** as built (one training seed), M adds at least 10 % on average in some rank band. How much of it is
  asymmetric response and how much is training noise is not separable from these records (§4).
- **INTERMEDIATE:** visible in the trace, but under 10 % on average in every rank band.

**A change from the plan, for the director to rule on.** The plan said "beyond its bootstrap SE (bootstrap over
universes within each band)". For the 42 bands with two or three universes, a resample within the band is
degenerate: two universes give three possible centres. So it would not estimate an SE. This declaration therefore
decides on the point values. It prints the R5 attribution and the leave-one-band-out range, so a label driven by one
band is visible. If the director prefers another uncertainty, it goes in before the code.

## 6. Controls (each a STOP, recorded unrepaired)

A STOP writes the record with `status: STOP` and the failing control, and no readings for that part.
- **C-PIN:** every committed input matches its §3 sha256 before it is parsed.
- **C-FETCH:**
  - each of the 16 fetched files matches its committed digest;
  - for each file, the before and after `stat` atime are equal, both taken on the same login node in the same
    session;
  - the remote side writes nothing.

  If a part-D file is missing or differs, part D STOPs and the tunes continue when their two files verify. If the
  inputs are purged, that is the separate costed ask of ruling 6.
- **C-RECON, the convention is understood:**
  - **Tunes:** Σ over the 38 weight bands of band_cov(`band__<b>`, w for Flux) equals `blocks_g2r_<T>.npz` `C_univ`
    (the 38-band sum, without the normalization, as `cov2d_blocks.assemble` and `g2r.c_t_prime` form it), and the
    five laterals with `minos_x` equal `C_lat`. Each match is to 1e-12 of the matrix's largest |entry|.
  - **Data:**
    - Σ over the 38 bands of band_cov(`band__<b>`) equals `data_g2r.npz` `C_univ_new`;
    - each lateral's band_cov equals S5_R's `band_<L>` (MINOS through the X01 rescale), to 1e-12 of its own largest
      |entry| (null bands at the total's scale, as S5's control does);
    - Σ over S5_R's 43 bands plus the normalization equals `cov2d_Q_205.npz`'s `universe` array;
    - C_new equals Q − Σ_38 S5_R `band_<b>` + C_univ_new, to 1e-12 of max |C_new|.
  - **Rehearsal:** the same as the tunes, against the committed `blocks_<T>.npz`.
- **C-ID:** for every band, V_nom − V_mean − b bᵀ is zero to 1e-12 of max |V_nom|, with V_nom computed directly.
- **C-X0:**
  - **Data:** `cov2d_Q_205.npz` `x` equals E_R's `hXSec2D` on its positive cells, bit for bit, and those cells are
    the 205.
  - **Tunes:** `blocks_g2r_<T>.npz` `x_T` and `rep` equal the committed `blocks_<T>.npz`'s, bit for bit. G2R changed
    only the universe unfolds.
- **C-FLUX:** each `w_flux` equals the committed `blocks_<T>.npz`'s bit for bit. Its sum and n_eff equal
  `data_g2r.json`'s logged 211.01200325082078 and 19.060534772246488.
- **C-PSD:**
  - C is symmetric, and its smallest eigenvalue is ≥ −1e-12 of its largest;
  - M is symmetric with smallest eigenvalue ≥ −1e-12 of its largest.
- **C-ADD:** the per-band R1 and R3 values sum to the totals, to 1e-12 relative.
- **C-FINITE:** every array is finite, with the shapes stated in §3.

## 7. Code, record and order

**The code:** a driver, `center2d.py`, plus its tests. It uses numpy, with uproot for `hXSec2D` (the same reader as
C2-EFF's `th2_values`, with edge and shape checks). There is no ROOT, and nothing it reads is edited. The fetch
package follows C2-EFF's bound design:
- a wrapper with the cert and fence gates;
- one ssh to a login node, running `env -i … nice -n 19 ionice -c 3 /usr/bin/python3 -I -B -` with the reader on
  stdin;
- O_RDONLY|O_NOATIME|O_NOFOLLOW reads with lstat/fstat identity checks;
- a tar streamed back, with the manifest as its last member;
- a laptop verifier that writes `SHA256SUMS`.

**The order:**
1. This declaration: the director reviews and merges it.
2. The code PR: the driver, the fetch package and the tests.
3. Mutation testing, with a receipt.
4. The director's binding.
5. Part R runs locally on committed inputs. Its readings go to the director.
6. The read (§8), after the director's GO.
7. Parts T and D run locally on the verified fetch. Their readings go to the director first.
8. A receipt PR.

Any changed byte of a bound script goes back to the director before it runs.

**The record:** `run/center2d.json` (parts T and D) and `run-rehearsal/center2d_rehearsal.json` (part R), each with
every control, every reading, the labels, the noise statement of §4, and the sha256 of every input.

## 8. The read

**What needs to be in place first:**
- the director's GO on the bound wrapper;
- a cert valid for over 1800 s;
- cov2d's ack, including its condition B on foreign job families;
- limitation-resolver told START just before the connect and END after.

**The fence at START:** sacct and squeue for every family:
- cov2d*, t2a*, rpd*, precharge_c, geanttw_, oofvc_, covfix_, ibuchi_ and ptmc_;
- this lane's own family, center2d*.

**The read itself:**
- one login node, 16 files (npz and ROOT files; each size is recorded in the fetch manifest);
- O_NOATIME, with the before and after atime stat taken on that node within the one session (never compared across
  nodes or jobs, and no read is ordered by atime);
- nothing written to pscratch or CFS, and nothing removed;
- 0 node-h.

**The namespaces read:**
- cov2d's `cov2d-g2r-20261112/readout/`;
- RE-2's `2d-closeout-re2-20261023/partb/out/` and `partc-r2/`;
- the c04-repair `build/`.

A STOP after contact is terminal and goes to the director.

## 9. COVFIX independence (ruling 4)

- This lane reads COV2D, G2R and T2A records. The 11-26 read ban was tune-generator's, and it still binds what flows
  to tune-generator.
- **No CENTER2D input, reading or interim number is sent to tune-generator or to the COVFIX lane.** Anything
  COVFIX-relevant goes to the director, who routes it.
- **AR23 and G18 are used for description only.** They enter no candidate, no bar and no choice. COVFIX §5.2 treats
  them as spent, and this study does not change that.

## 10. Corrections and disclosures

- **A correction to the pricing note.** It named
  `docs/orchestration/state/2d-closeout/stageC/production/evidence/production/results/production_cov.npz`
  (`6689d2fc…`) as holding "the per-band covariances" of the reported matrix. That file is Stage C's July-universe
  rollup, not the reported one.
  - The reported matrix's chain is S5_R (`partc-r2/s5/production_cov.npz`, `631cf255…`, on pscratch), then Q_R, then
    G2R's C_new.
  - The `s5.json` centring medians quoted in the pricing note (0.12–0.50 %, 0.08–2.26 σ_band) are Stage C's (R9),
    not the reported matrix's.
- **Seen during the inventory:** the committed S5_R `s5.json` `numbers.centring` (per-band median offsets, part B's
  pre-G2R universes). It is a committed summary of the R6 kind, and it decides nothing here. No quantity of §5 has
  been computed.
- **Read for this declaration** (at origin/main `02ae8600`), with no file opened beyond these:
  - G2R: the readout README, the data README and CORRECTION, `products.tsv.txt` row heads and counts, `out.sha256.txt`,
    `score_g2r_<T>.json` top-level keys, the declaration's lines 1–135, and `g2r_readout.py`'s and `g2r.py`'s
    output-writing functions;
  - the G2R adoption decision;
  - the re2shapes run-2 README, lines 1–60;
  - `cov2d_blocks.py` lines 1–150;
  - `re2c_rollup.py` lines 100–350 and 445–520;
  - `build_repair.py`'s `wcov` and `th2`;
  - `blocks_AR23.npz`'s keys and shapes;
  - S5_R's `s5.json` key lists, `inputs`, product digests and X01 checks;
  - part B's argv seeds and REPORT §4.2–4.3;
  - DRAFT-disclosures lines 125–140 and 293–330;
  - stageC DESIGN lines 270–300 and REPORT lines 100–145;
  - the release upload manifest's 2D rows.
