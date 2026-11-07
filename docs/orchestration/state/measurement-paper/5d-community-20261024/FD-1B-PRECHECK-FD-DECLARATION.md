# DECLARATION 1B gate-D pre-check, Part 1: the flux and detector bands split as I2 and κ split the interaction group (2026-11-06)

**By** the `limitation-resolver` lane, for `coverage-5b-audit` to audit and the director to bind.

**Under:**
- `DECISION-20261106-joseph-diagnoses-jinst-corrections.md`, item 1.2: the coverage pre-check's cause, as a diagnosis
  only;
- the director's scope ruling of 2026-11-06, Part 1. It approves the I2- and κ-shaped split for the Flux band and the
  four detector bands, each drawn alone at the 1B configuration, with F_src as the harness check.

**After:** [`FD-1B-PRECHECK-ATTRIBUTION.md`](FD-1B-PRECHECK-ATTRIBUTION.md) (Part 0, #858). Its §6 (a) is the question
here.

**MEASURES:** nothing. No unfold has run and no product has been read for this declaration. Every number quoted comes
from a committed record and is cited where it is used.

**What the drafter has seen:**
- Part 0's five readouts (`gate-d.json`, `diag.json`, `i0.json`, `i2.json`, stage 0's `readout.json`) and their reports;
- the code cited below, read at main `869dc269`.

The drafter has computed no F_src, F_side, F_truth or κ for any flux or detector band.

**CANNOT AUTHORIZE:**
- any job, before the director's binding;
- any coverage pseudo-experiment, or any change to the toys, gate D, M_d, the window, the reported covariance or κ;
- any 1B rerun or redesign. Rule (iii) (`DECISION-20261102-joseph-1b-redesign.md:78`) stands, and this result cannot
  be used to reopen 1B without Joseph;
- a study of the truth dependence (excluded by the director's ruling, item 4) or of the additivity residual (not now,
  item 3);
- any paper or note text.

## 1. The question, and what is fixed

**The question.** Gate D's flux ratio lies outside [0.9, 1.1] in 9 of 16 cells and its detector ratio in 3
(`FD-1B-STAGE2-REPORT.md:146–150` @ `869dc269`). The Flux band carries 0.41 of ρ_c² − 1 at R00 and 0.58 at R05
(Part 0 §3).
1. For these bands, do the pseudo-experiments realize what they draw? That is the harness check, F_src.
2. If they do, is the departure a comparison of unlike objects, as I2 found for the interaction group?

**Fixed:**
- The 1B configuration: gate D's derivation (noise-free, nominal truth, every Poisson draw at its mean), S1's
  estimator and settings, `fd_1b_toys.CONFIG`, `ITERS` and `ESTIMATOR_SEED`, the inputs npz and background dump at
  S1's digests, and S1's flux weights (the first 100 Flux entries of the constraint file, `S1-DECLARATION.md:70`).
- **The bands:** Flux (100 universes, weighted); MinosEfficiency, GEANT_Neutron, GEANT_Pion and GEANT_Proton (2
  universes each, `s1_assemble.py:57,60`). Each is drawn alone, one universe per unfold.
- **The window** is gate D's, [0.9, 1.1], and the noise rule is I0's (§4.1).
- **No readout here feeds back** into gate D, the toys, M_d or the reported covariance.

## 2. The objects

All are per-band diagonal blocks in the 16 reporting cells, by S1's estimator (`s1_assemble.mat_cov`: mean-centred,
1/N, and for Flux the constraint weights with weighted-mean centring). E, B, A and Dnom are carried or uncarried
exactly as in I2 and stage 0.

| object | pseudo-data | unfolding MC | status |
|---|---|---|---|
| **M_b** | the data | S1's universe u: truth, reco, denominator, background, and for Flux its own flux Φ_u | committed: S1's assembly (`db000707…`) |
| **E_b** | the derivation's nominal experiment × the toys' source factors for u (`fd_1b_toys.py:243–260`): Flux by wr_u / w_reco on signal reco and bkgw_u / bkg_w on background, no truth preservation; a detector band the same, from the detector dump | CV, with Φ_CV | committed: gate D's 176 derivation products |
| **B_b** (the toys' factors on the MC side) | the derivation's nominal experiment | reco weights × the same signal factor, background × the same background factor; truth, denominator and flux are CV | new |
| **A_b** (S1's mechanism at the nominal truth) | the derivation's nominal experiment | `s5p_universe.universe_inputs` for u exactly, with Φ_u for Flux (`s5p_universe.py:116–122`) | new |
| **Dnom_b** (mode D, like-for-like) | the universe's MC and background at r = 1, as `fd_1b_moded.d_experiment` | the nominal simulation, with Φ_CV | new |

**The factors**, for each band b and each cell:
- ρ_b = √(E_b / M_b), from `diag.json`'s carried `sigma_ratio`;
- F_src = √(E_b / B_b): the harness check. It asks whether the toys and the MC side, moving the same factors, give
  the same block;
- F_side = √(B_b / A_b): the toys' factors on the MC side against S1's whole universe at the same truth. This is I2's
  "F_prior", renamed because no prior is involved (the director's I2 review, :43–44);
- F_truth = √(A_b / M_b): S1's mechanism at the nominal truth against S1 at the data;
- ρ_b = F_src · F_side · F_truth, exactly. The readout checks it to 1e-12;
- κ_b = √(Dnom_b / A_unc,b), with A_unc = A / g², as stage 0 defines it (`FD-1B-MODED-DECLARATION.md:70`).

**Each group's factors** use the group's summed blocks, as gate D's `per_group_sigma_ratio` does. The flux group is the
Flux band; the detector group is the sum of its four bands.

**Flux only, descriptive, at no extra unfold.** The flux enters the extraction as a pure per-pT divisor
(`xsec_nd.py:54–80`; `S1-DECLARATION.md:71`). So the shift that S1's Φ_u alone makes, with the MC unchanged, is
arithmetic on the CV product: U · [x̂_CV · (Φ_CV/Φ_u − 1)]. A_Φ is that shift's weighted block. The readout reports
√(A_Φ / A_Flux) per cell. Φ_u comes from the flux file S1's Flux products record (`S1-DECLARATION.md:182`), which
that declaration lists as `flux_integral_universes_MEFHC.root`, `5eecae84…` (:261). P1 refuses if the products name
another file or digest.

### 2.1 A defect the code must not inherit

The I2 helper `fd_1b_inv.with_mc` (`fd_1b_inv.py:503–506`) replaces only `MC_KEYS = ("w_truth", "w_reco",
"denom_nd", "tmpl_w")` (:75). Its comment at :74 reads "the pseudo-data, truth, flux and template coordinates stay the
CV's". That was right for the interaction universes I2 ran, which leave the flux unchanged. Reused for a Flux universe,
it would get both modes wrong:
- **mode A** would unfold with Φ_CV and drop S1's main flux mechanism;
- **mode Dnom** (`fd_1b_moded.d_experiment`, :170–176) would keep the pseudo-data's Φ_u as the unfolding flux.

The Part 1 code sets the unfolding flux explicitly in every mode: Φ_u for A, and Φ_CV for B and Dnom. One test per mode
kills the inherited behaviour (§8).

## 3. Candidate mechanisms, each with its test

None has been measured.

| | mechanism | predicts | tested by |
|---|---|---|---|
| **HF0** (the referees' guess) | a harness defect, or a non-linearity: the toys do not reproduce what the same factors give on the MC side | F_src outside the window in a resolved cell | rule S (§4.2) |
| **HF1** | unlike objects: the toys move the event rate in the pseudo-data, while S1 moves the MC, the denominator and, for Flux, the flux normalization | F_side outside the window, with F_src inside | rule F (§4.3) |
| **HF2** (Flux) | normalization against rate: S1's Flux universe acts mainly through 1/Φ_u per pT bin, the toys' through the rate of each cell's events, whose E_ν distribution differs from the pT bin's flux-weighted mean | √(A_Φ / A_Flux) inside the window where F_side is outside | descriptive (§4.5) |
| **HD1** (detector) | the detector bands are weight-only on reco and background (`fd_1b_toys.py:255–260`); if the dump's truth weights and denominator equal the CV's, A ≡ B up to the ratio guards | F_side inside the window in every resolved cell | rule F, and a control on the dump's arrays (§5) |
| **H2** (noise) | a band whose blocks sit near the rounding floor | the band-cell is noise-consistent | the noise rule (§4.1) |

F_truth is computed as an attribution operand only; not studied (the director's ruling D1 on #861; CANNOT AUTHORIZE, above).

## 4. The readings, fixed before any number is read

### 4.1 Which band-cells are read

A band-cell is **noise** if both of the blocks a factor compares lie below k = 4 times their own side's pure-noise
expectation. This is `fd_1b_inv.noise_consistent` with I0's measured floors (`i0.json`):
- the data floor σ_J for M;
- the nominal floor, carried, for E, B and A; for κ, whose blocks are uncarried, the same floor divided by g;
- `fd_1b_inv.noise_factor` for the estimator's expectation, which is weighted for Flux.

The upper floor is used, as in Part 0's classes. A noise band-cell is excluded from every count below. A zero-block
band-cell on both sides is **undefined** and excluded too.

### 4.2 Rule S, the harness check (HF0)

Per band and per group, over its resolved cells:
- **REPRODUCED** if F_src is inside [0.9, 1.1] in every resolved cell;
- **DEPARTS** if F_src is outside in at least one resolved cell. The cells and values are listed.

What DEPARTS establishes is that the toys and the MC side, moving the same factors, give blocks more than 10 % apart
in σ. It does not separate a code defect from a non-linearity at ±1σ (I2's H4). A DEPARTS goes to the director
unrepaired, and any follow-up needs its own declaration.

### 4.3 Rule F, the attribution (HF1)

For each band and group, take the cells where ρ is outside the window and that are resolved for all three factors.
- **Attribution:** in each such cell, the factor with the largest |ln F| on the same side of 1 as ρ. It is attributed
  if it lies outside the window and carries at least half of |ln ρ|; otherwise the cell is unresolved. This is I2's
  rule (`fd_1b_inv.attribute`), without its S1-resolved F_truth clause, which the noise class replaces here.
- **The level**, with n such cells:
  - a factor is **the account** if it is attributed in more than n/2 cells;
  - it is **refuted as the account** if it is attributed in at most n/4;
  - otherwise it is **partial**;
  - n = 0 reads **nothing to attribute**.
- **Each factor is counted separately**, and the counts are never pooled.

### 4.4 Rule K, like-for-like (κ)

Per band and per group:
- **PASS** if κ is inside [0.9, 1.1] in every resolved cell;
- **FAIL** if it is outside in any resolved cell, with the cells listed.

### 4.5 Descriptive, with no verdict role

- √(A_Φ / A_Flux) per cell (HF2);
- per universe, the correlation of the toys' shift with −(B's shift) and with −(A's shift), as I2 §4.2 reports them;
- the readings with the point floor in place of the upper floor.

### 4.6 What each outcome licenses

| outcome | CITABLE FOR | NOT CITABLE FOR |
|---|---|---|
| rule S REPRODUCED for the flux and detector groups | with Part 0's interaction checks, "in all three drawn groups the pseudo-experiments reproduce, within 10 % in σ in every resolved cell, the block that the same weight factors give on the simulation side" | coverage; that S1's flux or detector block is right; the laterals and normalization surrogates (29.0 % of the trace, `gate-d.json:6`), C_model and C_resp |
| rule S DEPARTS for a band | "for band b the pseudo-experiments and the simulation side give blocks more than 10 % apart in σ in cells …"; a finding for the director | which of a defect and a non-linearity causes it; any repair |
| rule F, F_side the account | "gate D's departure for band b is mostly a comparison of unlike objects, the toys' factors against S1's whole universe at the same truth" | why they differ (HF2 is descriptive); which object is right |
| rule F, F_truth the account | "in the named cells, the dominant same-side factor is F_truth = √(A/M), the full universe at the nominal truth against S1's blocks" | any study of the truth dependence, any mechanism for it, and any statement about which truth the intervals should use: all outside this study, as excluded item (c) |
| rule K PASS | "full-universe pseudo-data reproduce S1's universe block for band b at the nominal truth" | that the toys realize S1's M; coverage |
| rule K FAIL | a finding for the director | a repair |

In every outcome, Gate D's FAIL, Part 0 and every earlier record stand, and so does rule (iii).

## 5. Controls

Any failed control makes the run **INVALID**, and it is reported unrepaired.
- **E reproduced.** From the staged derivation copies, gate D's flux and detector `per_group_sigma_ratio`
  (`gate-d.json`) and each band's `diag.json` `sigma_ratio` are reproduced bit for bit.
- **M reproduced.** S1's Flux and detector blocks, rebuilt from the staged S1 universe unfolds, equal the staged
  assembly's bitwise.
- **The CV control in each mode** (A, B and Dnom at u = CV) equals the derivation CV product's `xsec_flat` bitwise.
- **The flux in each product.** Each records the flux array it unfolded with. It must be Φ_u for A on a Flux universe,
  and Φ_CV for B and Dnom, compared by sha256 of the array (§2.1).
- **HD1's premise, recorded and not gated.** Per detector universe, whether the dump's `wt` and `denom_nd` equal the
  CV's bitwise.
- **The identity.** ρ_b = F_src · F_side · F_truth to 1e-12 in every cell.
- **One code and one input set** across every product (`fd_1b_inv.ONE_CODE_KEYS`).
- **Every input** has its staged sha256, and no source's atime moves: stat before staging and after the jobs, compared
  byte for byte.

## 6. Inputs, reads and the fence

**Staged: read once each, with O_NOATIME, into a stage under a new
`$V = /pscratch/sd/j/josephrb/fd-1b-precheck-fd-<date>`, with sha256 recorded (`fd_1b_inv.stage`):**
- all 176 of gate D's derivation products, `$P/fd-1b-20261030/runs/derivation/`. Gate D's builder
  (`fd_1b_score.derivation_blocks`) needs the full set for control E;
- all 176 of S1's universe unfolds, `$P/s1-20261024/runs/uni/`, and S1's assembly (`db000707…`);
- S1's flux-integral file, as its Flux products record it (`5eecae84…` by `S1-DECLARATION.md:261`);
- the flux constraint `sorted_NuEConstraint_FHC_RHC_IMD.txt` (`e38ad7d2…`), a COV2D input.

The readout reads only these copies and three committed files (`gate-d.json`, `diag.json`, `i0.json`, the last for
its measured floors).

**Read in place by the jobs, as I2's were:** the inputs npz (S1's digest), the background dump, the bank's `cv.npz`,
the 100 Flux weight sets and the 8 detector-dump weight sets. Each is opened only through `fd_1b_inv.open_noatime`.
The weights are digest-checked against the pins file before every item, and each job records the atime of every file
it opened, exiting 8 on a move. A test drives all three modes through an instrumented `os.open` and finds no plain
read of any of them.

**The jobs' flux file is the staged copy.** `flux_universe` (ROOT in production) reads it plainly. Its digest is
therefore read plainly too, and it is not an atime-tracked source. The test suite caught the alternative: an
O_NOATIME digest followed by ROOT's plain read made every job report a false atime move. The readout refuses unless
every product's `flux_file_sha256` is the staged copy's.

**The fence.**
- `cov2d_fence.sh` runs before every connect.
- **Staging waits** until no cov2d-* job is queued or running and the fence exits 0, because the stage includes a COV2D
  input. This is the same rule the director set for RPD-RECO's flux-constraint copy.
- **Stat-only checks** may run at any time.

**Before anything is staged, a stat-only connect** confirms that every source exists and records its size, mtime and
atime. A missing source is a STOP to the director, with HPSS fallback paths named there and nothing staged.

**Order.** RPD-RECO's connect runs first. This run comes after it, under the binding.

## 7. Steps, jobs and price

**Unfolds.**
- **A, B and Dnom** each cover the 108 universes (100 Flux and 8 detector) plus one CV control.
- **Total:** 327.
- **Cost basis:** I2's products had median 725.1 s and maximum 849.6 s per unfold (`FD-1B-INV-I2-REPORT.md:81`). S1's
  measured top, 1,370 s, is the unit (`fd_1b_inv.UNIT_SECONDS`).
- **Cost per item:** I2's bulk was 196 items for 5.370 node-h, and stage 0's was 96 for 2.819 node-h. That is
  0.027–0.029 node-h per item.

| step | what | jobs | limit (HH:MM:SS) | reserved node-h | expected |
|---|---|---|---|---:|---:|
| P0 | stat-only connect, login | — | — | 0 | 0 |
| P1 | staging and controls E and M, login, `nice -n 19` | — | — | 0 | 0 |
| P2 | pilot: A, B and Dnom at CV; A, B and Dnom at Flux_0; A and B at MinosEfficiency_0 (8 items, one lane each) | 1 | 01:00:00 | 1.0 | 0.3 |
| P3 | bulk: the other 319 items, 8 lanes per node, at most 6 items per lane | 7 | 02:30:00 | 17.5 | 9.3 |
| P4 | readout, login | — | — | 0 | 0 |
| **cap** | | | | **18.5** | **about 9.6** |

**Gates between the steps:**
- **The bulk** is submitted only if P2's `walls` reads PASS. The largest `seconds_unfold` must be ≤ 1,370 s and the
  largest peak RSS ≤ `fd_1b_inv.RSS_LIMIT_KIB`. Otherwise P2 is a REPRICE back to the director.
- **The audit sees P2's readout** before the bulk is submitted (the director's I2 review, §2).

**Resources and fit:**
- Each lane is 32 CPUs and 56G, with `-A m3246 -q regular -C cpu --exclusive --no-requeue`.
- 8 × 56G = 448G ≤ MaxMemPerNode 487,802M, and 8 × 32 = 256 CPUs; both fit the node's allocatable resources.
- Every connect prints `scontrol` TimeLimit and cancels on a mismatch.

**Balance.** `iris` is read before P2 and P3. A cap above half the remaining balance comes back to the director.

## 8. The code (in this PR before binding)

**The module:** `nd-unfolding/fd_1b_precheck_fd.py`. It imports `fd_1b_inv`, `fd_1b_moded`, `fd_1b_toys` and
`s5p_universe` unchanged and does not modify them. It has four subcommands:
- `stage`, reusing `fd_1b_inv.stage`;
- `unfold --mode {A,B,Dnom} --universes …`, which refuses any universe outside CV, Flux_0–99 and the 8 detector
  universes;
- `walls`;
- `readout`.

**Its tests** (`nd-unfolding/tests/test_fd_1b_precheck_fd.py`, 30 tests, synthetic fixtures only):
- **B's factors** equal `fd_1b_toys.source_factors`' bitwise;
- **each mode at CV** equals the derivation CV experiment bitwise;
- **§2.1's flux key** in each mode, with the inherited `with_mc` shown to give the wrong flux. The job refuses a
  product unfolded with another mode's flux;
- **Dnom's truth** carries Φ_u;
- **HD1's flags** are recorded;
- **rules S, F and K** at their edges, with unresolved cells ignored, and the levels at n/2 and n/4;
- **the readout end to end:**
  - B = E reads REPRODUCED and 1.2 E DEPARTS;
  - the attribution lands on the factor the fixture sets;
  - κ = 1.2 fails;
  - κ's floor is uncarried;
  - A_Φ = A for pure-normalization universes;
- **each of nine controls** refuses with its own message;
- **an atime move** exits 8;
- **O_NOATIME over the call graph.**

**The mutation receipt** (`fd/receipts-1b/precheck-fd/code/mutation.{py,out}`) kills 37 of 37 mutants:
- the flux key in each mode, and the job's flux refusal;
- B's factors, and Dnom's nature and unfolding MC;
- every threshold and every rule edge;
- the weights, the carry and Dnom's object;
- κ's floor and A_Φ;
- each control.

The suite passes at PYTHONHASHSEED 0, 1 and 12345.

## 9. Routing

- The report goes to `coverage-5b-audit` and to the director, and through the director to Joseph if a rule reads
  DEPARTS or FAIL.
- Part 0's §6 (a) is updated by a new record. Part 0 itself is not edited.
- Nothing is submitted, deposited or tagged.
