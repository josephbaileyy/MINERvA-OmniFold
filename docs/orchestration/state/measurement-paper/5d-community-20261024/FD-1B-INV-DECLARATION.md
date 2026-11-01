# DECLARATION 1B reopened: an investigation of gate D's mismatch (2026-11-01)

**By** the measurement session `coverage-5b`, for the director to bind.

**Under:**
- [`DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md`](../../../DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md)
  (#640, main `2f62fe4e`), item 1 (the investigation) and item 2 (compute).

**After:**
- [`FD-1B-STAGE2-REPORT.md`](FD-1B-STAGE2-REPORT.md) §4.1, which records gate D FAIL;
- [`FD-1B-DIAG-REPORT.md`](FD-1B-DIAG-REPORT.md) (#634), which records NOT LOCALIZED;
- the director's brief of 2026-11-01, which named H1 and H2.

**This declares**, before any new number is read:
- three steps, cheapest first: I0 (0 node-h), I1 (conditional, ≤ 4.0 node-h) and I2 (≤ 12.0 node-h);
- each step's readouts, and a decision rule naming the allowed outcome its readout supports;
- the reads, the price, and the code still to be written and reviewed.

**MEASURES:** nothing. No step has run, and no product has been read for this declaration.
- The numbers quoted here come from committed records, each cited where it is used.
- The algebra in §2 is first-order and labelled as such.

**CANNOT AUTHORIZE:**
- any job, before the director's binding;
- any change to the pseudo-experiments, M_d, the reported covariance, κ or gate D's window;
- a coverage result. Gate D's FAIL and the diagnosis's NOT LOCALIZED stand as recorded.

## 1. The question, and what is fixed

**The question (the decision, item 1):** do S1's systematic-universe blocks and the pseudo-experiments propagate the
same uncertainty through the same estimator? Where they differ, which of them is wrong?

**Where it starts:** the interaction group. Its per-cell σ ratio has median 1.659 and range 0.418–6.521. It is above 1
in 13 cells and below 1 in 3 (R03, R05 and R07), and outside [0.9, 1.1] in 15 of 16 (all but R06). Flux's median is
0.996, and detector's is 0.973 (`FD-1B-STAGE2-REPORT.md` §4.1).

**Fixed by the decision:**
- The allowed outcomes are four: (O1) the pseudo-experiment design must change; (O2) the covariance must change;
  (O3) the estimator must be stabilised; (O4) unresolved. Each is a finding, and none is a coverage result.
- Changing the toys, the covariance or the window in order to make gate D pass is forbidden. No readout here feeds
  back into gate D, the toys or M_d. A later change must follow from a finding, under its own declaration and binding.

## 2. The two objects, side by side

For one interaction universe u, the two shifts in one cell are:

| | S1's block M_b (`s5p_universe.universe_inputs`) | gate D's E_b (`fd_1b_toys`, derivation mode) |
|---|---|---|
| what is unfolded | the real data | noise-free pseudo-data at the nominal truth: all of the MC, every Poisson draw at its mean |
| the unfolding MC's truth weights | → universe u's | CV |
| its reco weights | → universe u's | CV |
| its completeness denominator | → universe u's `tdw` histogram | CV |
| the background template | → universe u's `bkgw` | CV |
| the pseudo-data source | — (data) | reco weights × k_wr × g_f; background × k_b. The truth is kept in every fine cell (g_f, `s5p_nullexp.truth_preserving`) |
| the shift | x̂_S1(u) − x̂_S1(CV), in f space | x̂_D(u) − x̂_D(CV), carried by diag(g), g = f / x_T |
| the block | MAT mean-centred, 1/N (`s1_assemble.mat_cov`) | the same estimator |

So the two differ on three axes at once:
- **where the universe acts:** in the unfolding MC, or in the pseudo-data;
- **what it moves:** S1 moves the prior and the response, while gate D moves the response only;
- **at which truth:** the data's, or the nominal.

**First-order algebra (inference, not measured).** For an estimator that is locally linear, write r for the shift from
a response change seen in the pseudo-data, and p for the shift from the prior change in the MC. Then, per universe:
- S1's shift is about −r + p (the response moved on the MC side enters with the opposite sign);
- gate D's shift is about r.

So E_b > M_b when p partly cancels r in S1's shift. This is the condition the director named for H1 to fit 13 cells
above 1.

## 3. Candidate mechanisms

None of these has been measured. Each step tests the ones named against it.

| | mechanism | predicts | tested by |
|---|---|---|---|
| **H1** | prior versus response: S1's universe moves the prior too, and the fixed-truth toys do not | E ≠ M even at one truth, with A ≈ B + C (§6) and B/A outside the window | I2 |
| **H2** | estimator noise: with two universes per band, a band whose true shift is near the rounding spread gives a noise-dominated block on either side | the excess sits in band-cells whose blocks are within a few times their noise floor; it scatters in sign and does not localize | I0, then I1 |
| **H3** (added) | truth dependence: S1's blocks are made at the data and gate D's at the nominal truth. The carry diag(f / x_T) rescales a block, but does not change its shape within a cell | A (S1's mechanism at the nominal truth) ≠ M | I2 |
| **H4** (added) | side asymmetry: the same response change moves the result differently when it is put in the pseudo-data than when it is put in the MC (non-linearity at ±1σ) | E ≠ B | I2 |

**One recorded fact bears on H2, quoted and not re-measured.** On the 32 H2 boxes, configuration R's edge-safe
rounding spread has these medians (`state/s5p/stage2/stage2_receipt.json`, `0daa7cd8…`, `study_N`):
- 0.176 % (max 0.490 %) on the real data;
- 0.0125 % (max 0.021 %) on nominal pseudo-data;
- 0.067 % at the GiBUU departure.

The data spread is about 14× the nominal one (KNOWN_ISSUES 80: "it grows as the data move away from the MC prior").
- **What that implies:** if H2 acts, it should act mostly on S1's side, which is made on the data. It would add to M_b
  rather than to E_b, which pushes the ratio below 1.
- **Why that does not settle H2:** the toys' derivation mode is not the pseudo-experiment the receipt jittered, so I0
  measures the floor rather than assuming it.

## 4. Step I0: shifts against the measured rounding floor (0 node-h, login node)

**Reads.** Each input is read once, with `O_NOATIME`, into a staged copy under `$V/i0/in/`, with its sha256
recorded. All the I0 code then reads only the copies (§8).
- **Gate D's inputs:** the 176 derivation products, `$P/fd-1b-20261030/runs/derivation/fd1b_derivation_<u>.npz`
  (this lane's);
- **S1's 176 universe unfolds,** CV control included: `$P/s1-20261024/runs/uni/S1_<u>.npz` (S1's lane; on HPSS
  `mnv-5d-s1-products-20261024`);
- **S1's assembly,** `$P/s1-20261024/s1_assembly.npz` (`db000707…`);
- **s5p study N's jitters** (s5p's lane):
  - `$P/s5p-20260926/runs/s2/num/data/data_b-_j-.npz` and `data_b-_j{1..20}.npz`. That base is S1's central, by S1's
    gates G2 and G4 (`S1-DECLARATION.md:181-183`);
  - `…/num/nom/nom_b-_j-.npz` and `nom_b-_j{1..20}.npz`;
- **the flux constraint file,** to re-run gate D on the copies.

`$V` is a new directory, `$P/fd-1b-inv-20261101`.

**Controls.** Any failure is INVALID, and I0 is reported unrepaired.
- Gate D's reader, run unchanged on the staged copies, reproduces `gate-d.json`'s ρ bit for bit.
- `S1_CV` equals the N1 base bitwise (S1's G4, re-checked on the copies).
- `mat_cov` over the staged S1 universe unfolds reproduces each of the assembly's 38 band blocks exactly.

**Readouts,** per cell c, with x the 16 cell integrals (U x̂):
- **The rounding floor.**
  - σ_J,c^data is the sample SD (ddof 1) of the 20 data jitters. σ_J,c^nom is the same for the 20 nominal jitters,
    carried by g_c.
  - A band with n universes and pure noise has an expected block of ((n − 1)/n) σ_J² per cell. That is ½ σ_J² for a
    pair and ⅔ σ_J² for 2p2h. For Flux the factor is 1 − Σw²/(Σw)².
  - This gives the floor N_b,c^data for S1's side and N_b,c^nom for gate D's side.
  - **The upper floor** uses σ_J² × 19 / χ²₁₉(0.05) = 1.878 σ_J², the one-sided 95 % bound from 20 jitters.
- **Resolution.** Band b is *resolved* in cell c if M_b,cc ≥ 4 N_b,c^data and E_b,cc ≥ 4 N_b,c^nom. That is the
  block at least four times its pure-noise expectation, on both sides.
- **ρ_c^res = √(1 + Σ_{b resolved in c} t_b,c).** Here t_b,c = (E_b,cc − M_b,cc) / M_d,cc is the diagnosis's
  per-band term (`FD-1B-DIAG-REPORT.md` §2; the terms sum to ρ_c² − 1 exactly). Bands that are not resolved have
  their E_b replaced by M_b, the diagnosis's substitution applied to the noise-defined set.
- **Computed twice:** at the point floor, and at the upper floor.
- **Descriptive, with no verdict role,** per interaction universe:
  - the shifts s_S1 and s_D;
  - their sign concordance across cells;
  - the correlation of s_D with −s_S1;
  - the pair antisymmetry |s₊ + s₋| / (|s₊| + |s₋|), on each side;
  - q = √(block / floor), per band and cell.

**Rule H2,** for each of gate D's 11 cells outside the window (R00, R02, R05, R07, R08, R09, R10, R11, R12, R13 and
R15):
- **SUPPORTED in c** if ρ_c^res lies in [0.9, 1.1] at both floors. The cell's failure is then carried by bands that
  are not resolved above the noise.
- **REJECTED in c** if it lies outside the window at both floors.
- **OPEN in c** otherwise.

| I0 readout | outcome it supports | next |
|---|---|---|
| SUPPORTED in all 11 | **O3**, the estimator must be stabilised | I0's report. I1 and I2 do not run |
| any cell OPEN | none yet | I1 |
| otherwise (REJECTED in at least one cell, OPEN in none) | O3 for the SUPPORTED cells, if any; H2 is rejected as the account of the others | I2 |

**Fallback, if the s5p jitter products are gone.**
- The floor comes from the committed receipt's per-box relative σ (`sigma_num_base_rel`, data and nominal). It is
  bounded for each cell by the triangle inequality: σ_c ≤ Σ_{i ∈ c} σ_i x_i, a full-correlation upper bound that
  makes the most bands unresolved.
- Under the fallback the point floor is that bound, so SUPPORTED cannot be read: a cell that would read SUPPORTED reads
  OPEN.
- REJECTED stands, because it holds under the floor most generous to H2.

**Assumption, stated:** a universe unfold's noise component has the size of the CV's rounding spread on the same
input. I1 tests it if it runs.

## 5. Step I1: H2 directly (conditional, ≤ 4.0 node-h)

**It runs only if I0 leaves a cell OPEN.** It is cheaper than I2 and runs before it.
- **The design:**
  - 10 edge-safe rounding jitters of the derivation CV experiment, in derivation mode at the nominal truth;
  - 5 jitters each of S1's universe unfolds on the data, for up to 6 universes. They are the bands I0 names as changing
    resolution between the floors in the OPEN cells, the largest |t_b,c| first.

  That makes at most 40 unfolds.
- **The rule:** I0's rule is re-read with the measured floors. A universe's floor is its own jitter spread, at its own
  truth. Each OPEN cell becomes SUPPORTED or REJECTED. If it is still neither, it reads **O4 (unresolved)** for H2,
  and I1 does not repeat.
- **The jitter code and argv** come to the director as an amendment, to be reviewed and bound before I1 runs. The
  price is fixed now (§9).

## 6. Step I2: S1's mechanism, decomposed at the nominal truth (≤ 12.0 node-h)

**It runs unless I0 or I1 reads H2 SUPPORTED in all 11 cells.** The 67 interaction universes (32 pairs and 2p2h's 3)
are each unfolded three more times. Every unfold uses the derivation CV experiment as its pseudo-data: the nominal
truth, all of the MC, means not draws. Only the unfolding side changes:

| mode | the unfolding MC | object |
|---|---|---|
| **A** (S1 at the nominal truth) | `universe_inputs` exactly: truth and reco weights, completeness denominator and background template → universe u's | S1's mechanism, at gate D's truth |
| **B** (response in the MC) | reco weights × k_wr × g_f and background template × k_b, the factors gate D's source uses. Truth weights and denominator are CV | the response alone, moved on the MC side |
| **C** (prior in the MC) | `prior_inputs` with r = the fine-cell mean of k_wt: truth and reco weights × r, and the denominator by the same per-cell factor. The response within each fine cell is CV | the prior alone |

Each mode also runs once at u = CV, as a control: 3 unfolds. That makes 204 unfolds.

**Controls.** Any failure is INVALID, and I2 is reported unrepaired.
- Every mode at u = CV equals the derivation CV product's `xsec_flat` bitwise. The code computes each per-cell factor
  before applying it, so a factor of 1 is exact; a test holds this.
- Every universe's inputs carry the digests the stage-2 pins file recorded.

**Readouts,** each group sum built with the pair estimator and carried by g as gate D's E is:
- for the interaction group, per cell, A_c, B_c and C_c, beside E_c (gate D) and M_c (S1);
- three factors whose product is the gate's interaction ratio, exactly:

      √(E/M) = F_src · F_prior · F_truth,   F_src = √(E/B),   F_prior = √(B/A),   F_truth = √(A/M).

  - F_src is H4.
  - F_prior is H1: the response alone, against the response with the prior.
  - F_truth is H3.
- **Descriptive:**
  - per band, A_b, B_b and C_b against M_b and E_b;
  - the prior share C/A;
  - the additivity residual block(A − B − C)/A, which holds the completeness change and the second order;
  - the per-universe correlation of s_D with −s_B.

**Rule I2,** for each of the interaction group's 15 cells outside the window:
- The cell is **attributed** to the factor with the largest |ln F| among those on the same side of 1 as √(E/M), if that
  factor lies outside [0.9, 1.1] itself and carries at least half of |ln √(E/M)|.
- Otherwise the cell is **unresolved**.

| attribution | outcome | what it means |
|---|---|---|
| F_prior (H1) | **O1**, the pseudo-experiment design must change | gate D compared unlike objects. The fixed-truth toys cannot produce the prior part, which S1's blocks hold by construction, so a control of S1's blocks needs toys whose truth moves with the universe, or blocks split into response and prior parts |
| F_truth (H3) | **O1** | S1's blocks at the data are not the same mechanism's at the nominal truth, beyond the carry. A control at the nominal truth must use blocks made at its own truth |
| F_src (H4) | **O2**, the covariance must change | propagating a model change by moving the MC does not reproduce the estimator's response to the same change in the data. S1's construction then misstates that part of the error |
| none | **O4**, unresolved, for that cell | |

**The headline** is the outcome attributed in at least 8 of the 15 cells. Otherwise it is **O4 (mixed)**. Every
cell's attribution and the counts are printed either way, together with any O3 cells from I0 or I1.

**What O1 under H1 does not decide.**
- **The fact:** S1's interaction block is var(−r + p) by construction. If F_prior attributes the excess, that block is
  smaller than the response-only spread at the nominal truth.
- **The open question:** whether the reported intervals should carry var(r) and leave the prior part to C_model. That
  is a question about what the covariance is for, and C_model already holds a model-dependence term.
- **What the report does:** it prints B beside M in the data's frame, for the director and Joseph. It does not answer
  the question.

## 7. The outcomes, in one place

| step | readout | O1 design | O2 covariance | O3 estimator | O4 unresolved |
|---|---|---|---|---|---|
| I0 | rule H2 per failing cell | | | SUPPORTED | |
| I1 | rule H2 with measured floors | | | SUPPORTED | still OPEN |
| I2 | rule I2 per interaction cell | F_prior or F_truth | F_src | | no factor, or no 8-of-15 majority |

None of these is a coverage result. A later coverage ensemble needs its own declaration and binding (the decision).

## 8. Reads, access times and retention

- **`O_NOATIME`, everywhere this lane's code reads pscratch** (the decision; `FD-1B-DIAG-REPORT.md` §5):
  - **I0:** a staging command opens each input with `O_NOATIME`, verifies and copies it into `$V/i0/in/`, and records
    its sha256. Everything after reads the copies.
  - **I2's job:** the inputs npz, the background dump and the bank's weight files are too large to copy. Streaming 34 bands'
    weight arrays reads about 13 GB, by `s5p_nullexp.ModelCache`'s own estimate. They are opened with `O_NOATIME` and passed to numpy as file
    objects. `load_inputs` and the weight reads are replaced by loaders that a test holds equal, array by array, to the
    path-based loaders they stand in for. Hashing uses the same descriptors.
- **A check of the property itself:** each connect runs `stat` on the inputs before and after. An access time that
  moves is a deviation, reported unprompted and not restored.
- **The per-playlist event-loop files: no step needs them.**
  - I0 reads products only.
  - I1 and I2 read the inputs npz, the background dump, the bank and the detector dump, the same inputs stage 2's
    jobs read.
  - Joseph's choice to let those files age out does not touch this investigation.
- **Retention:** I0's first connect runs `stat` on every input above, before the run. A missing or exposed input is
  reported, together with the fallback, before anything runs.
  - `$V` is named here for the pscratch retention list.
  - Its products get an HPSS copy at each step's end. Nothing goes to CFS.

## 9. Price

| step | unfolds | nodes × lanes | most per lane | unit | projected wall | projected node-h | limit | **cap** |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| I0 | 0 | login37, `nice -n 19` | — | — | minutes | 0 | — | **0** |
| I1 (if run) | ≤ 40 | 2 × 8 | 3 | 1,370 s | 1.2 h | 2.4 | 2.0 h | **4.0** |
| I2 (if run) | 204 | 4 × 8 | 7 | 900 s | 1.8 h | 7.1 | 3.0 h | **12.0** |
| **all** | ≤ 244 | | | | | **≤ 9.5** | | **16.0** |

- **The units:**
  - I1: S1's universe steps took 1,256–1,370 s on the data (`S1-DECLARATION.md:100`), and its derivation-mode jitters
    are shorter.
  - I2: gate D's largest derivation `seconds_unfold` was 801.4 s (`FD-1B-STAGE2-REPORT.md` §2), and the declared
    full-MC unit is 832 s. I add about 70 s per unfold for reading mode A's four weight arrays, an ESTIMATE.

  Node-h is nodes × elapsed. The cap is nodes × limit.
- **Jobs:** `-A m3246 -q regular -C cpu --exclusive --no-requeue`, through the committed packer.
  - Every limit is under 12 h, and the longest is 3.0 h.
  - CPU only, and nothing to CFS.
  - Any rerun beyond a failed step's same-seed rerun needs an amendment.
- **Against the balance:** the caps total 16.0 node-h, against half of the last recorded balance, 1,037.3 (2,074.5
  remaining; the decision, item 2). The first connect re-reads `iris` before any submission.

## 10. Code, tests, review and order

1. **This declaration.** Its PR carries no code.
2. **The code,** in a second commit on this PR:
   - `nd-unfolding/fd_1b_inv.py` has these subcommands:
     - `stage`, the `O_NOATIME` copy;
     - `i0`, the reader and rule H2;
     - `unfold`, modes A, B and C, composed from `s5p_universe`, `s5p_nullexp`, `fd_1b_toys` and `s5n_pseudo`, which
       are imported and left unchanged;
     - `i2`, the reader and rule I2.
   - The tests cover:
     - each rule in each direction on synthetic fixtures (SUPPORTED, REJECTED, OPEN; each attribution; unresolved;
       the 8-of-15 headline);
     - the telescoping identity;
     - the bitwise CV controls;
     - every `O_NOATIME` loader equal to its path loader;
     - the fallback floor's bound.
   - A mutation receipt covers the rules and the controls.
3. **The review:** `coverage-5b-audit` reviews the declaration and the code (the decision), and the dispositions are
   recorded in this PR.
4. **The binding** is the director's. Before it, nothing reads a product and nothing is submitted. After it, the order
   is I0, then I1 (through its amendment, if triggered), then I2. Each step's report goes to `coverage-5b-audit` and
   the director before the next step is submitted.
5. **The time-box:** I0's report is due within 24 h of the binding. I2 is submitted within 72 h of the last report
   before it, or the lane reports why not.

Every connect and every submission is announced to the director first.

## 11. Not changed

- gate D's readout and verdict, and the diagnosis and its verdict;
- the toys, M_d, the window, the reported covariance, κ, every claim and number, and the data product;
- the paper's statement that coverage has not been validated;
  <!-- absence-ok: restates the paper's own statement (DECISION-20261024-joseph-5d-community-standard-route.md:46-47), which this investigation leaves as it is; no search claim -->
- the per-playlist event-loop files' retention.

Nothing is submitted, deposited or tagged.

## 12. For the director to rule

1. The three steps, their order and their caps, 16.0 node-h in all (§9).
2. Rule H2: the resolution threshold of 4× the floor, the two floors, and the three-way per-cell reading (§4).
3. The I0 fallback, if the s5p jitter products are gone (§4).
4. Rule I2: the attribution test, the 8-of-15 headline, and the outcome each factor maps to (§6). In particular, F_src
   maps to O2 and F_truth to O1.
5. I1's jitter code and argv as a later amendment, bound before I1 runs (§5).
6. The `O_NOATIME` scheme: staged copies for I0, file-object loaders for I2 (§8).
