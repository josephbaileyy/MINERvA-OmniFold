# DECLARATION 1B pre-check, band diagnosis: is the GEANT_Neutron and GEANT_Proton departure a defect or a non-linearity? (2026-11-08)

**By** the `limitation-resolver` lane, for `coverage-5b-audit` to audit and the director to bind.

**Under:** `DECISION-20261108-joseph-5d-coverage-and-parallel-studies.md` (#934), "What is decided" item 2: "The
GEANT_Neutron and GEANT_Proton departure is diagnosed, under a new declaration, in parallel. It does not gate the
coverage test and cannot change item 1's primary reading after the fact."

**After:** `OUTCOME-20261108-1b-precheck-part1.md` (#933), which records, under NOT CITABLE FOR: "For GEANT_Neutron
and GEANT_Proton: whether a defect or a non-linearity causes the departure, and any repair." That clause is the
question here. Part 1's design is [`FD-1B-PRECHECK-FD-DECLARATION.md`](FD-1B-PRECHECK-FD-DECLARATION.md), bound by
[`FD-1B-PRECHECK-FD-BINDING-1.md`](FD-1B-PRECHECK-FD-BINDING-1.md); its readout is
`fd/receipts-1b/precheck-fd/p4/records/p4/readout.json`, sha256 `8e05ca9bc2d0f2142b5c8d2bff28f05176c48f27454218390f09658344cea7b0` (#930).

**MEASURES:** nothing. No unfold has run, and no product has been opened, for this declaration.

**What the drafter has seen:**
- Part 1's readout.json and its receipts (#922–#930), and the outcome record;
- the code cited below, at main `1ad13b76`. Every `file:line` below is at that commit, under `nd-unfolding/`.

**What the drafter has computed,** from readout.json alone, before writing the rules below. It is disclosed because
it shaped §3's HK and §4.2's thresholds:
- in every κ-resolved cell of all four detector bands, κ / (F_src · F_side) = 1 to 2.2e-16 in |ln|;
- in every F_src-resolved cell, |ln F_side| is at most 6.0e-8 for GEANT_Neutron, 1.6e-7 for GEANT_Proton, 1.7e-8 for
  GEANT_Pion and 2.7e-9 for MinosEfficiency.

The drafter has computed nothing else. No F_src at another seed, scale or channel exists.

**CANNOT AUTHORIZE:**
- any job, before the director's binding;
- **any repair**, or any change to the toys, gate D, M_d, the window, the reported covariance or κ;
- any change to the like-for-like coverage test (DECISION-20261108 item 1). Its primary reading, without the two
  bands, is fixed there. **This diagnosis does not gate it and cannot change that reading**, whatever it finds;
- a study of the truth dependence, excluded item (c). Every unfold here is at the nominal truth (§1);
- any 1B rerun or redesign. Rule (iii) (`DECISION-20261102-joseph-1b-redesign.md:78`) stands;
- any paper or note text.

## 1. The question, and what is fixed

**The departure.** Part 1's rule S reads DEPARTS for:
- GEANT_Neutron in R00 R02 R08 R09 R10 R11;
- GEANT_Proton in R01 R05 R07 R08.

Rule K reads FAIL in the same cells. The cells and values are at `/bands/<b>/rule_S` and `/bands/<b>/rule_K`.
F_src = √(E/B) compares two objects:
- **E:** the derivation's nominal experiment with the toys' factors on the pseudo-data (signal reco weights × wr_u / w_reco, background × bkgw_u / bkg_w, `fd_1b_toys.py:255–261`), unfolded with the CV simulation;
- **B:** the nominal pseudo-data, unfolded with the CV simulation carrying the same factors (`fd_1b_precheck_fd.py:130–133`).

So the departure is between moving the pseudo-data and moving the simulation by the same factor. Part 1 §4.2
leaves open which of three things causes it:
1. a defect in how the two sides are built;
2. a non-linearity at the size of a ±1σ GEANT shift;
3. the estimator's own variation.

**The questions.**
1. Is rule K's FAIL the same comparison as rule S's DEPARTS for these bands, or separate evidence? (§4.2)
2. Do the two sides carry the same factor on the same reco rows? (§4.3)
3. Is the departure stable under the estimator's seed? (§4.4)
4. Does it shrink as the shift shrinks, as a non-linearity does, or stay constant, as a first-order mismatch does? (§4.5)

**Fixed:**
- **The 1B configuration, unchanged.** That means S1's estimator and settings: `fd_1b_toys.CONFIG`, `ITERS` and
  `ESTIMATOR_SEED` (`"R", 42, 5`, `fd_1b_toys.py:73`), the inputs npz and background dump at S1's digests, the
  detector dump at its pins, the derivation's nominal experiment (every Poisson draw at its mean, nominal truth r = 1,
  `fd_1b_inv.py:495–500`), and the CV simulation for unfolding. Two variations only, each a diagnostic and none a
  change to the toys:
  - the estimator seed, over S1's own seed list `(42, 45, 48, 51, 54)` (`s1_assemble.py:52`);
  - the size of the factor (§2).
- **The bands.** GEANT_Neutron and GEANT_Proton, two universes each (`s1_assemble.py:57,60`), are the subjects.
  GEANT_Pion and MinosEfficiency, which reproduced, are the references.
- **The window and the noise rule:** Part 1's, [0.9, 1.1] and I0's measured floors at k = 4 (Part 1 §4.1), applied
  unchanged to every variant.
- **The truth is never varied.** No product here moves w_truth, the denominator, the flux or r. Item (c) stays
  excluded.
- **No readout here feeds back** into gate D, the toys, M_d, κ, the coverage test or Part 1's record.

## 2. The objects

All are per-band diagonal blocks in the 16 reporting cells, by S1's estimator (`s1_assemble.mat_cov`,
`s1_assemble.py:125–130`: mean-centred, 1/N, unweighted for the detector bands). With two universes, a band's block
in a cell is ((s_0 − s_1)/2)², with s_i the cell's value in universe i. E and B are carried by g, as in Part 1.

**The scaled factor.** For each universe's signal and background factors f (Part 1's, as above):
- f_ε = f^ε, for ε ∈ {½, 1, 2};
- at ε = 1 the code uses f itself, with no arithmetic, so that ε = 1 reproduces Part 1 bit for bit (§5).

The power keeps every factor non-negative at ε = 2, and it scales ln f linearly in ε.

**The channels.** "signal" applies f_ε to the signal reco weights only (the background factor set to 1); "background"
applies it to the background only. "both" is Part 1's object.

| object | pseudo-data | unfolding simulation | seeds | ε | channel | status |
|---|---|---|---|---|---|---|
| **E** | nominal × f_ε | CV | 42 | 1 | both | committed: gate D's derivation products, staged by Part 1 (`$V/stage/derivation/`, `staged.json` `f2f06419…`) |
| **B** | nominal | CV × f_ε on reco and background weights | 42 | 1 | both | committed: Part 1's P3 products (`$V/unf/fd1b_pfd_B_<u>.npz`) |
| **A, Dnom** | as Part 1 §2 | as Part 1 §2 | 42 | — | — | committed: Part 1's P3 products |
| **E_s, B_s** | as E, B | as E, B | 45, 48, 51, 54 | 1 | both | new |
| **E^ε, B^ε** | as E, B with f_ε | as E, B with f_ε | 42 | ½, 2 | both | new |
| **E^c, B^c** | as E, B in channel c | as E, B in channel c | 42 | 1 | signal, background | new |

`$V` = `/pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107`, Part 1's root.

**The factors:** F_src = √(E/B), for every pairing of the same seed, ε and channel. The readout also reports s_E,i and s_B,i,
each universe's cell values, so a reader can see the ratio of differences behind each block.

## 3. Candidate mechanisms, each with its test

None has been tested. HK's arithmetic was read from Part 1's committed readout before these rules were written (disclosed
above); that read is a record, not a test.

| | mechanism | predicts | tested by |
|---|---|---|---|
| **HK** | for the weight-only detector bands at r = 1, rule K is rule S in another form. Dnom's pseudo-data (`fd_1b_precheck_fd.py:149–152`) are E's: the universe's reco and background weights at the nominal truth, unfolded with the CV simulation. A differs from B only in w_truth (`s5p_universe.py:111–112`, with the dump's denominator the CV's by Part 1's descriptive record). At r = 1, T_u = 1e4·denom_nd/(Φ·N·POT·vol) wherever ofin > 0 (`s5n_pseudo.py:170–186`, `xsec_nd.py:55–85`), so w_truth cancels from the truth Dnom subtracts. | g²·Dnom = E and B ≈ A in every cell, so κ = F_src · F_side with F_side ≈ 1 | §4.2, from Part 1's products |
| **HB0** | a defect in input construction: the two sides do not carry the same factor on the same reco rows | the row-level comparison differs | §4.3 |
| **HB1** | the estimator's variation: a cell resolved by the k = 4 rule whose departure is within the seed-to-seed spread of a 5-iteration, seeded estimator | F_src returns inside the window, or crosses to the other side, at another seed | §4.4 |
| **HB2** | a non-linearity in the size of the shift: moving the pseudo-data and moving the simulation agree to first order and differ at higher order | \|ln F_src\| grows with ε at least as ε^½ per doubling | §4.5 |
| **HB3** | a first-order difference between the two sides inside the estimator. This is either a code defect in the estimator path or the estimator's first-order behaviour (for example, the refinement step sees the background move in observed rows for E and in template rows for B, `fd_1b_toys.py:285–291`, `s5n_pseudo.py:194–201`). This study does not separate those two. | \|ln F_src\| constant in ε, with HB0 excluded | §4.5 with §4.3 |
| **HW** (descriptive) | E's pseudo-data keep only in-window rows (`fd_1b_toys.py:290`), while B's simulation carries f on every reco-passing row. Whether the estimator reads out-of-window simulation rows is not asserted here. | a large out-of-window share of the factor in the departing universes | §4.6 |
| **HC** (descriptive) | the departure sits in one channel | F_src^signal or F_src^background carries it | §4.6 |

## 4. The readings, fixed before any number is read

### 4.1 Which band-cells are read

Part 1 §4.1 applies unchanged. For each variant, F_src's cell is resolved unless both E's and B's blocks lie below
k = 4 times the carried nominal floor (`fd_1b_precheck_fd.py:415`).

The **departing cells** are Part 1's ten: GEANT_Neutron R00 R02 R08 R09 R10 R11 and GEANT_Proton R01 R05 R07 R08.
Verdicts are read on them. Every other resolved cell of the four detector bands is reported, without a verdict.

### 4.2 HK, rule K against rule S (Part 1's products, no new unfold)

Per detector band, over its κ-resolved cells:
- **SAME COMPARISON** if |ln(g²·Dnom / E)| ≤ 1e-12 and |ln(B / A)| ≤ 1e-5 in every such cell;
- **DIFFERENT** otherwise, with the cells and values listed.

The thresholds are set after seeing the factor-level values disclosed above. This reading records at the block level
what those values already show; it is not a test with power.

**Descriptive:** per universe, max over cells of |U·x̂_E − U·x̂_Dnom| / |s_E| and of |U·T_u − U·T_CV| / |U·T_CV|.

### 4.3 HB0, the inputs (one step in the pilot job, no unfold)

For each of the 8 detector universes, the experiments are built exactly as the unfolds build them, at ε = 1.
- **Signal.** Over every reco-passing row inside the window, E's observed count (`fd_1b_toys.py:284`, at its mean) is
  compared with B's simulation reco weight w_reco·f. A row absent from E's pseudo-data (`n_sig > 0`, :288) counts as 0.
- **Background.** Over every background row inside the window, E's observed count is compared with B's template weight.
- Rows of zero or negative weight are absent from E's pseudo-data (`fd_1b_toys.py:288–289`). They are left out of
  both sides of the comparison, and §4.6 reports their share.

Readings:
- **EQUAL** if both comparisons are bitwise equal, row by row, in all 8 universes;
- **DIFFER** otherwise, with the universe, the channel, the number of differing rows and the largest relative
  difference.

**DIFFER is a STOP** to the director before the bulk: a candidate defect, reported unrepaired.

### 4.4 HB1, the seed (E_s, B_s)

For each departing cell, F_src is taken at the five seeds 42 (Part 1's), 45, 48, 51 and 54, pairing E and B at the
same seed.
- **SEED-STABLE** if F_src is resolved and outside the window, on the same side of 1 as at seed 42, at all five seeds;
- **SEED-SENSITIVE** otherwise.

**Descriptive:** the five values; the standard deviation of ln F_src over the seeds; and, for the reference bands, the
number of resolved cells outside the window at each seed.

### 4.5 HB2 and HB3, the scale (E^ε, B^ε, seed 42)

Read only on SEED-STABLE cells; a SEED-SENSITIVE cell reads **NOT READ** here.

**The quantities.**
- Let σ = sign(ln F_src(1)) and ℓ(ε) = σ · ln F_src(ε), each where F_src(ε) is resolved.
- **The slopes:**
  - p_up = log₂(ℓ(2)/ℓ(1)), and −∞ if ℓ(2) ≤ 0;
  - p_down = log₂(ℓ(1)/ℓ(½)), and +∞ if ℓ(½) ≤ 0.
- p_up is required. p_down is used where ε = ½ is resolved.

**Per cell:**
- **SCALES** if p_up ≥ 0.5 and, where computed, p_down ≥ 0.5;
- **CONSTANT** if |p_up| ≤ 0.25 and, where computed, |p_down| ≤ 0.25;
- **MIXED** otherwise; **NOT READ** if ε = 2 is unresolved.

**Per band:** SCALES or CONSTANT if every read departing cell reads so. Otherwise MIXED, with the cells listed.

What the slopes mean:
- **A non-linearity that is smooth in the shift** gives a departure of order ε^p with p ≥ 1, which reads SCALES.
- **A first-order mismatch** gives p ≈ 0, which reads CONSTANT. This covers a factor carried differently by the two
  sides, or a first-order difference in how the estimator treats them.
- **The 0.5 and 0.25 margins** allow for the single seed at ε ≠ 1. At ε = ½ the blocks are about a quarter as large, so
  the seed variation weighs more there. That is why p_up, at the larger shift, is the required slope.

### 4.6 Descriptive, with no verdict role

- **HW:** per detector universe, the in-window sum Σ w_reco·(f − 1) over reco-passing rows, and two shares of it:
  - the same sum over rows outside the window;
  - the same sum over in-window rows whose weight w_reco·f is zero or negative.

  E's pseudo-data carry neither kind of row; B's simulation carries both.
- **HC:** for the four GEANT_Neutron and GEANT_Proton universes, F_src^signal and F_src^background in every resolved
  cell, set beside F_src.
- **The per-universe cell values** s_E,i and s_B,i for every variant, and F_src(ε) for the reference bands.

### 4.7 What each outcome licenses

| outcome | CITABLE FOR | NOT CITABLE FOR |
|---|---|---|
| §4.2 SAME COMPARISON for band b | a record of Part 1's committed products, not a test: "reading Part 1's committed readout and products, for band b κ/(F_src·F_side) = 1 to [value] in \|ln\| and g²·Dnom = E to [value], with F_side = √(B/A) differing from 1 by at most [value]; the thresholds were set after these values were seen. On that record, rule K's FAIL is not separate evidence" | a test of HK; anything about κ for the flux or interaction groups, or at another truth |
| §4.2 DIFFERENT | a finding for the director | a cause |
| §4.3 EQUAL | "the pseudo-data and the simulation side carry the same factor on the same reco rows inside the window, for every detector universe" | anything inside the estimator; HW's rows outside the window |
| §4.3 DIFFER | "for universe u, the two sides do not carry the same factor on the same rows in [channel]"; a candidate defect for the director | which code; any repair |
| §4.4 SEED-SENSITIVE in cell c | "band b's departure in cell c is within the variation of the estimator's seed at the 1B configuration" | that band b reproduces; coverage; any statement about other bands' cells |
| §4.5 SCALES for band b | with §4.3 EQUAL: "in the named cells, band b's departure shrinks with the size of the shift, as a non-linearity does, and the two sides carry the same factor" | which non-linearity; that it is harmless for coverage; any repair |
| §4.5 CONSTANT for band b | with §4.3 EQUAL: "in the named cells, band b's departure does not shrink with the shift: a first-order difference between moving the pseudo-data and moving the simulation by the same factor, inside the estimator"; a finding for the director | whether a code defect in the estimator path or the estimator's first-order behaviour causes it; any repair |
| §4.5 MIXED or NOT READ | the values only | a mechanism |

**In every outcome:** Part 1's record, gate D's FAIL, Part 0, rule (iii) and the coverage test's primary reading
stand. **No outcome here is a coverage statement.**

## 5. Controls

Any failed control makes the run **INVALID**, and it is reported unrepaired.
- **E rebuilt.** The new code's E at seed 42, ε = 1, channel both, for all 8 detector universes and for CV, equals the
  staged derivation product's `xsec_flat` bitwise.
- **B rebuilt.** The new code's B at seed 42, ε = 1, for the four GEANT_Neutron and GEANT_Proton universes and for CV,
  equals Part 1's P3 product's `xsec_flat` bitwise.
- **Part 1's readout reproduced.**
  - Gate D's builder (`fd_1b_score.derivation_blocks`, `fd_1b_score.py:432–466`) and `fd_1b_score.load_s1` read
    plainly, so they are not called. Their arithmetic (x_u = U·x̂, one truth across the products, g = f/(U·truth),
    the carried block) is repeated on O_NOATIME reads, with the builder's meta checks.
  - That repetition is checked twice. P1's F_src and κ for the four detector bands, from Part 1's products, equal
    readout.json's `/bands/<b>/factors/{F_src,kappa}` bit for bit. P4's F_src at seed 42, and its resolved cells,
    equal `/bands/<b>/factors/F_src` and `/bands/<b>/resolved/F_src`.
  - Part 1's A, B and Dnom products at CV equal the derivation CV product bitwise.
- **One code and one input set** across the new products: `fd_1b_inv.ONE_CODE_KEYS` less `estimator_seed`, which
  varies by design. The seed, ε and channel are recorded in each product and checked against its name. The
  estimator's parameters are checked at the product's own seed, by `s1_assemble.check_meta`'s clauses
  (`s1_assemble.py:203–208`): three estimators at random_state = seed, and the refinement at seed + 3.
- **Threads.** Every lane runs at 32 threads, as Part 1's P3 did, with Part 1's thread probe. Bitwise reproduction
  across jobs needs the same thread environment.
- **Every input has a sha256:**
  - Part 1's products and staged copies are hashed when first read (P1), and every later read must give the same
    digest;
  - the staged copies are also checked against `staged.json`;
  - no source's atime moves, compared by stat before P1 and after P3, byte for byte.

## 6. Inputs, reads and the fence

**Read, never written, with O_NOATIME (`fd_1b_inv.open_noatime`):**
- from Part 1's root `$V`:
  - `stage/staged.json`;
  - `stage/derivation/fd1b_derivation_{CV,<u>}.npz` for the 8 detector universes, each checked against `staged.json`;
  - `stage/s1/s1_assembly.npz`, checked against S1's digest (`fd_1b_score.S1_NPZ_SHA256`) and `staged.json`;
  - `unf/fd1b_pfd_{A,B,Dnom}_{CV,<u>}.npz` for the same universes;
- in place, as Part 1's jobs read them: the inputs npz (S1's digest), the background dump, and the 8 detector-dump
  weight sets (digest-checked against the pins file before every item);
- from the clone: readout.json (`8e05ca9b…`) and `i0.json`, each recorded by sha256.

Each file is hashed when first read, and a later read in the same step must give the same digest.

**No COV2D input is read.** The detector bands' blocks are unweighted, so no flux constraint is opened, and no Flux
universe is unfolded, so the flux-universe file is not either. Nothing therefore waits on the COV2D fence.

**Nothing is staged.** The new products go to a new root, `$W = /pscratch/sd/j/josephrb/fd-1b-band-diag-<date>`.

**The fence.** `cov2d_fence.sh` runs from the Mac before every connect. Each connect's in-script fence allows
`fd1b_bdg_*` and the families the director names at binding; anything else refuses.

**Before anything runs, a stat-only connect (P0)** records size, mtime and atime for every source above. A missing
source is a STOP to the director.

## 7. Steps, jobs and price

**The job-name family is `fd1b_bdg_`** (`fd1b_bdg_p2`, `fd1b_bdg_p3`). It is new, so the director's binding names it to
every fenced lane.

**Items.**

| set | universes | modes | seeds / ε / channels | items |
|---|---|---|---|---:|
| pilot controls | 8 detector + CV | E | 42, ε 1 | 9 |
| | 4 GEANT_Neutron/GEANT_Proton + CV | B | 42, ε 1 | 5 |
| seeds (§4.4) | 8 detector | E, B | 45, 48, 51, 54 | 64 |
| scale (§4.5) | 8 detector | E, B | ε ½, 2 | 32 |
| channels (§4.6) | 4 GEANT_Neutron/GEANT_Proton | E, B | signal, background | 16 |
| **total** | | | | **126** |

**Cost basis.**
- Part 1's pilot: max seconds_unfold 821.5 s, with at most 74 s of step overhead per item
  (`fd/receipts-1b/precheck-fd/p2/README.txt:54,79`).
- Part 1's bulk: 319 items for 9.0892 node-h (#928).
- The unit is S1's measured top, 1,370 s (`fd_1b_inv.UNIT_SECONDS`).

| step | what | jobs | limit (HH:MM:SS) | reserved node-h | expected |
|---|---|---|---|---:|---:|
| P0 | stat-only connect, login | — | — | 0 | 0 |
| P1 | §4.2 and the readout-reproduction control, from Part 1's products, login, `nice -n 19` | — | — | 0 | 0 |
| P2 | pilot, one node: the §4.3 inputs step, then the 14 control items on 8 lanes, at most 2 per lane | 1 | 01:30:00 | 1.5 | 0.7 |
| P3 | bulk: the 112 other items on 3 nodes × 8 lanes, at most 5 per lane | 3 | 02:30:00 | 7.5 | 3.8 |
| P4 | readout, login | — | — | 0 | 0 |
| **cap** | | | | **9.0** | **about 4.5** |

P3's worst lane at the unit is 5 × (1,370 + 75) + 60 = 7,285 s, inside 02:30:00 (9,000 s).

**Gates between the steps.** P3 is submitted only if all of the following hold:
- P2's E and B rebuild controls are bitwise;
- §4.3 reads EQUAL;
- P2's walls pass: the largest seconds_unfold ≤ 1,370 s and the largest peak RSS ≤ `fd_1b_inv.RSS_LIMIT_KIB`.
  Otherwise P2 is a REPRICE back to the director;
- coverage-5b-audit has seen P2's readout.

**Resources:**
- Each lane is 32 CPUs and 56G, with `-A m3246 -q regular -C cpu --exclusive --no-requeue`. That is 8 × 56G = 448G
  and 256 CPUs per node, as in Part 1 §7.
- Every `--time` is HH:MM:SS. Every connect prints `scontrol` TimeLimit and cancels on a mismatch.
- Nothing is written to CFS from a job.

**Balance.** `iris` is read before P2 and P3. A cap above half the remaining balance comes back to the director.

## 8. The code (in this PR before binding)

**The module:** `nd-unfolding/fd_1b_band_diag.py`. It imports `fd_1b_precheck_fd`, `fd_1b_inv`, `fd_1b_toys`,
`fd_1b_score`, `s5n_pseudo`, `s5p_universe` and `s1_assemble` unchanged and modifies none of them. Its subcommands:
- `same`: §4.2 and the readout-reproduction control;
- `inputs`: §4.3 and HW; rc 0 EQUAL, 1 DIFFER;
- `unfold --mode {E,B} --seed {42,45,48,51,54} --eps {0.5,1,2} --channel {both,signal,background} --universes …`,
  which refuses any universe outside CV and the 8 detector universes, and any combination outside §7's table;
- `pilot`: §5's E and B rebuild controls and §7's walls; rc 0 PASS, 1 REPRICE, 2 INVALID;
- `readout`: §4.4–§4.6.

**Its tests** (`nd-unfolding/tests/test_fd_1b_band_diag.py`, 49 tests, synthetic fixtures only):
- E at ε = 1, channel both, equals `fd_1b_toys.experiment("derivation", single_universe(u))`'s experiment bitwise;
- B at ε = 1 equals `fd_1b_precheck_fd.mode_inputs("B")` bitwise;
- f_ε = f at ε = 1 with no arithmetic, and f^ε otherwise;
- each channel sets the other factor to exactly 1;
- the seed reaches the estimator, and the product's estimator parameters are checked at its own seed;
- the §4.3 comparison fires on one planted row in each channel;
- rules §4.2, §4.4 and §4.5 at their edges:
  - the 1e-12 and 1e-5 thresholds;
  - a seed crossing the window, or crossing 1;
  - p at 0.5 and 0.25;
  - ℓ ≤ 0 at each ε;
  - unresolved ε = ½ and ε = 2;
- the readout end to end:
  - a planted constant mismatch reads CONSTANT;
  - a planted quadratic departure reads SCALES;
  - a planted seed jitter reads SEED-SENSITIVE;
- each control refuses with its own message;
- O_NOATIME over the call graph;
- an atime move exits 8.

**The mutation receipt** (`fd/receipts-1b/band-diag/code/mutation.{py,out}`) kills 60 of 60 single-site mutants. They
cover the factor, the channels and the two experiments; every job guard; §4.3's row comparison and its verdict; §4.2's
thresholds and resolution; each reproduction and digest control; the pilot's rebuild control and walls; §4.4's and
§4.5's edges (window, side of 1, resolution, the 0.5 and 0.25 margins, the infinite slopes, the band reading); and the
readout's item, one-code, seed-42 and I0 controls.
- The first run killed 57. The three survivors each got a test: ε applied to the signal factor only; g formed against
  the unmapped truth (g cancels from every ratio read here, so only a direct test of g sees it); and the window's edges
  made exclusive.
- The suite passes at PYTHONHASHSEED 0, 1 and 12345.

## 9. Routing

- The report goes to `coverage-5b-audit` and to the director, and through the director to Joseph. The director writes
  the outcome record; this lane does not.
- Any STOP or INVALID goes to the director unrepaired.
- Nothing is submitted, deposited or tagged.
