# DECLARATION: V-HALF, the per-cell half-departure bias rule on the sixteen cells (2026-11-09)

**By:** the valid-region lane (session director-helper-2).

**Under:**
- `DECISION-20261109-joseph-bias-half-rule.md` (#974). Joseph decided to declare and compute the advisor's suggested
  rule, as Joseph relayed it.
- The director's rulings of 2026-11-09 on V-HALF's input, quoted in §1: option (B), the hybrid, with its six points.

**Status:**
- This is a declaration for coverage-5b-audit's read and then the director's binding.
- **Nothing in §§3–6 has been computed.** No V-HALF d, b, margin or class has been formed.
- **The departure d does not exist yet in any committed record.** It comes from FD-PRR's readout (§2).
  - FD-PRR addendum A2 is bound: FD-PRR BINDING 1 addendum A2 (#990, `cc9ee532`), with M_A2 =
    `cf76aec7cdff4e86f375ffe945f4d22f4799c4e0`.
  - The PRR read waits for prr_ibu, which runs again after addendum A3 (#989) is bound. It is committed at the later of
    M_A2 and A3's merge commit.
  - Search: git ls-tree -r --name-only 5a028842 | grep -E 'receipts-prr/.*readout|prior_retention/.*readout\.json|prr-read' gives 0 files @ 5a028842
- The work is records-only: arithmetic on two committed files, on a local machine, at 0 node-h, with no cluster
  contact.

**MEASURES (once bound and run):** for each of the 16 reporting cells R00–R15, its V-HALF class (§5).

**CANNOT AUTHORIZE:**
- any paper or note wording;
- any change to the reported result, its cells, its observables, its binning or its covariance;
- any reading of a non-valid cell as excluded, wrong or unreported;
- anything outward.

**The advisor's consequence is not decided here** (decision item 5). That is modifying the observable or the binning if
a cell fails. It goes back to Joseph with the result.

## 0. Disclosure: what was seen before this rule was declared

- **What V-PRIOR's declaration (§0) records this lane had seen** of F0b's readout I1, the paper's tab:fd16 and its
  comments, and FD-F0b-REPORT. It carries over unchanged. The A7 GiBUU hybrid is flagged in R02, R06 and R07, and
  Stage 0c GiBUU in R06.
- **The valid-region read** (`OUTCOME-20261107-valid-region.md`, receipt #897) printed I1's per-cell pulls at every
  graded truth.
  - The largest are A7 GiBUU in R02 (z = +4.19) and in R06 (z = +4.53). Every other truth–cell pair has |z| ≤ 2.
  - V-HALF's r is I1's `bias`, which is z × σ. So **where d is small, a V-HALF fail at A7 GiBUU in R02 and R06 is
    foreseeable.** V-HALF is not blind at those two pairs.
- **No d has been seen.** FD-PRR's products exist only on pscratch, and no FD-PRR read has run. The dry-run receipt
  (#972) carries timings and checks, not d. <!-- absence-ok: a statement about this lane's own process; FD-PRR's readout does not exist yet -->
- **What was mapped while drafting:** only I1's keys and its truths' names, rows, groups and own vertices, and FD-PRR's
  readout schema (`prr_read.py` @ `cf76aec7`, M_A2). No bias, noise or z value was printed.

## 1. The rule, and the director's rulings

**The decision's rule** (item 1), per cell c and graded truth t:
- d_{c,t} = (X_{c,t} − P_c)/P_c and b_{c,t} = (X̂_{c,t} − X_{c,t})/P_c, with FD-PRR §4.1's definitions;
- the rule applies at (c, t) only where |d_{c,t}| ≥ 0.01;
- (c, t) passes when |b_{c,t}| ≤ 0.5 |d_{c,t}|;
- a cell is V-HALF-valid when it passes at every truth where the rule applies. A cell where the rule applies at no
  truth is reported as such, not as valid.

**The director's rulings (2026-11-09), option (B), the hybrid:**
1. **The rule in I1's terms.** r = I1's relative bias X̂/X − 1, so b = r(1 + d), and the rule reads
   **|r| ≤ 0.5 |d| / (1 + d)** where |d| ≥ 0.01. Both forms are stated here, and a test and control C-FORM check that
   they agree.
2. **d comes from FD-PRR's readout,** which emits d from addendum A2 on. A2 is bound (#990), with M_A2 = `cf76aec7`.
3. **The truth mapping** is by name (§3). A truth without a B0 d is "no d", and that is not valid.
4. **The noise:**
   - I1's `noise_sigma` carries the bias's noise, scaled by (1 + d);
   - d's own noise comes from FD-PRR's five splits at A7_gibuu, the only measured points;
   - a pair whose pass or fail flips within the combined band is "unresolved (noise)" (§4);
   - the limitation is stated: d is PRR's half-MC truth departure, not F0b's pseudo-data source (§10).
5. **Print-only, beside the verdict:** option (A), each cell's threshold boundaries, and GiBUU excluded on p_∥ ≥ 4.5.
   None of these changes a class.
6. **The order:**
   1. the A2 PR, its audit and its binding (done: #980 merged as `cf76aec7`, bound in #990);
   2. this PR, its audit and its binding;
   3. the PRR read, committed, at the later of M_A2 and A3's merge commit, once prr_ibu has completed;
   4. the V-HALF read, local at 0 node-h;
   5. its receipt and an outcome to the director.

**Why the hybrid (the director's reasoning, recorded).** The decision names two sources. The bias comes from the
products V-ATLAS graded, and d from §4.1's computation. The committed F0b readout carries only r. Its leak guard
refuses absolute cell integrals (`nd-unfolding/fd_f0_regrade.py:18-23` @ `82ee901c`), so it has no X and no P. FD-PRR's
B0 products at the same 12 truths are the only source of §4.1's d.
- Search: git grep -l -E '"(x_true|truth_integral|x_truth|departure|truth_over_prior|X_true|xtrue)"' -- '*.json' @ 82ee901c
  gives 6 files. None of them is per truth on R00–R15: they are the pv-ladder spaces, the response, the d-id results
  and the domain cells.

## 2. Inputs

| # | file | pin | used for |
|---|---|---|---|
| H1 | `$FD/fd/with-cpl/readout/fd_f0b_readout.json` | `5f542830561731b5…` in [`INPUTS.sha256`](INPUTS.sha256) (V-ATLAS's I1) | per graded truth: `bias` (r), `noise_sigma` (ν), `own_vertex`, `p_parallel_lt_4p5.cells` |
| H2 | FD-PRR's committed readout, `readout.json`, made by `prr_read.py` at the later of M_A2 (`cf76aec7`) and A3's merge commit | `PRR-READOUT.sha256`: its path and sha256, added by the director's binding once the PRR read is committed | per truth, `table["B0/<t>/s991000"]`: `d` (A2), `b`, `r`; `table["B0/A7_gibuu/s<seed>"]` at the five splits; `verdict` |

`$FD` is `docs/orchestration/state/measurement-paper/5d-community-20261024`.

**Without `PRR-READOUT.sha256` the code refuses** (exit 4). So no V-HALF value can be formed before the binding names
H2's bytes.

**H2 is read only for d, and for option (A), which is print-only.** FD-PRR's own readings, labels and classes are not
read.

## 3. The truth mapping (F0b's 12 graded truths to FD-PRR's B0 truths)

| H1 graded truth (in H1's order) | row | group | own vertex | FD-PRR truth (`prr_probe.TRUTHS`) | H2 key |
|---|---|---|---|---|---|
| nominal | 1 | prior | – | nominal | `B0/nominal/s991000` |
| W1 | 1 | vertex-family | nuwro | W1 | `B0/W1/s991000` |
| W2 | 1 | vertex-family | genie_mec | W2 | `B0/W2/s991000` |
| W3 | 1 | vertex-family | nuwro | W3 | `B0/W3/s991000` |
| q3 | 1 | non-vertex | – | q3 | `B0/q3/s991000` |
| stage0c_gibuu | 2 | vertex-family | gibuu | stage0c_gibuu | `B0/stage0c_gibuu/s991000` |
| closure_nuwro | 3 | vertex-family | nuwro | closure_nuwro | `B0/closure_nuwro/s991000` |
| A7_mnvtune | 4 | prior | – | A7_mnvtune | `B0/A7_mnvtune/s991000` |
| A7_genie_cv | 4 | non-vertex | – | A7_genie_cv | `B0/A7_genie_cv/s991000` |
| A7_genie_mec | 4 | vertex-family | genie_mec | A7_genie_mec | `B0/A7_genie_mec/s991000` |
| A7_nuwro | 4 | vertex-family | nuwro | A7_nuwro | `B0/A7_nuwro/s991000` |
| A7_gibuu | 4 | vertex-family | gibuu | A7_gibuu | `B0/A7_gibuu/s991000` |

- **The names are identical.** FD-PRR's truths are "the ones F0's pins name" (`FD-PRR-DECLARATION.md` §3.2), in F0's
  order (`prr_probe.py:145-146` @ `6727020a`).
- **The six ungraded row-6 truths (P1r–P3g) are not in V-HALF,** as in V-ATLAS's A3.
- **The two prior-group truths are included,** as in A3. Their d is 0 or near it, so the rule will usually not apply
  there. Where |d| ≥ 0.01, it does.
- **GiBUU-family truths are graded on all 16 cells** (decision item 2).
- **A missing key or a missing `d`** makes that truth "no d" in every cell. It is not a STOP.

## 4. The quantities and the noise, per pair (c, t)

**The point values:**
- r = H1 `bias[c]` and ν = H1 `noise_sigma[c]`, the standard error of r. ν is 0 for the noise-free closure rows.
- d = H2's B0 `d[c]` at split 991000.
- b = r (1 + d), which is §4.1's (X̂ − X)/P, because X/P = 1 + d.
- **Applies** ⇔ |d| ≥ 0.01, by the point value.
- **The margin** is m = 0.5 |d| − |b|. The pair passes by the point value iff m ≥ 0.

**The noise band:**
- σ_d(c) is the sample s.d. (ddof 1) of H2's B0 `d[c]` at A7_gibuu over the five splits 991000 and 994001–994004.
  They are the only measured points of d's noise. σ_d(c) is applied to every truth in cell c, and the readout prints it.
  - The nominal truth's five splits enter only as each split's P. Its own d is 0 by construction, and control C-PRR
    checks that.
- σ_m² = ((1 + d) ν)² + (0.5 sgn(d) − |r|)² σ_d². These are the two terms linearized:
  - ∂m/∂r = −(1 + d) sgn(r);
  - ∂m/∂d = 0.5 sgn(d) − |r|.
- **K = 2.** lo = m − K σ_m and hi = m + K σ_m.

**The pair's class:**
- **pass** if lo ≥ 0;
- **fail** if hi < 0;
- **"unresolved (noise)"** otherwise, because the point class flips within the band;
- **"not applicable"** if |d| < 0.01;
- **"no d"** if the truth has no d.

**Why these choices:**
- **K = 2 matches the paper's own per-cell trigger of 2** (`FD-DIRECTOR-RULINGS.md:35-39`). K = 1 and K = 3 are
  printed beside it, print-only.
- **The ≥ at the pass edge keeps the decision's "≤".** With σ_m = 0, the band reduces to the point rule exactly.
- **Applicability is by the point value of |d|.** The readout lists, print-only, the pairs whose |d| lies within
  K σ_d of 0.01.

## 5. The cell's class

The classes, in order of precedence:
1. **not valid:** some pair fails;
2. **no d:** no pair fails, and some truth has no d;
3. **unresolved (noise):** none of the above, and some pair is unresolved;
4. **rule applies at no truth:** every pair is "not applicable";
5. **valid:** otherwise. Every applicable pair passes, and at least one applies.

A resolved fail is a fail whatever else the cell holds. "No d" is never valid. "Rule applies at no truth" is never
valid.

## 6. Print-only, beside the verdict (read by nothing; no class changes)

- **Option (A).** The same rule, with FD-PRR's own B0 bias b = (X̂ − X)/P at split 991000 in place of r(1 + d).
  - The bias noise is the per-cell s.d. of B0's b at A7_gibuu over the five splits.
  - d's noise is σ_d, as in §4.
- **The threshold boundaries,** per cell, by point values:
  - h* is the largest |b|/|d| over the pairs where the rule applies. At the 1 % floor, the cell is valid by point
    value iff 0.5 ≥ h*.
  - The readout also lists the floors at which h* changes as the floor rises past each truth's |d|.
- **GiBUU excluded on p_∥ ≥ 4.5.** The class with stage0c_gibuu and A7_gibuu dropped outside their
  `p_parallel_lt_4p5.cells`, which are the eight p_∥ < 4.5 cells.
- **The band at K = 1 and K = 3.**
- **Applicability near the floor:** the pairs with ||d| − 0.01| < K σ_d.

## 7. Controls (any failure: exit 3, nothing classified)

| control | check |
|---|---|
| C-PIN | H1 and H2 equal their pins |
| C-CELLS | H1's cells are R00–R15 in order. Every graded truth's `bias` and `noise_sigma` has 16 entries |
| C-TRUTHS | H1's graded truths are exactly §3's 12, in order. H2 has B0/A7_gibuu at all five splits. Each truth's H2 entry is listed; a missing one is "no d", not a STOP |
| C-PRR | H2's `verdict` is COMPLETE. At every B0 entry used, H2's own b = r(1 + d), to a relative 10⁻⁹ (its d, b and r agree). B0/nominal's d is exactly 0 at all five splits. Every d, b and r present at those entries has 16 values (§8.2); H2 carries no cell labels, so their order rests on `prr_read.py`'s M16 |
| C-DOMAIN | the two GiBUU-family truths name the same eight `p_parallel_lt_4p5.cells` |
| C-FINITE | every r, ν, d and σ_d is finite; ν ≥ 0; 1 + d > 0 |
| C-FORM | the two forms of the rule agree at every applicable pair, by point value |
| C-HAND | d and b re-derived at one cell, R06 at A7_gibuu, by a separate path. d is read raw from H2, and again as b/r − 1 from FD-PRR's own b and r. r is read raw from H1. b = r + r·d is computed by hand. Each must equal the code's value |

**The hand check in the receipt.** The read receipt also carries the same R06/A7_gibuu derivation, done by hand from
the printed raw values and written out in its README. R06 is the cell where A3 fails most strongly.

## 8. Code, tests and mutation (before the binding)

- **The files:** `v_half.py`, `test_v_half.py` and `mutate_v_half.py`, in this directory.
- **The tests** use synthetic fixtures in the inputs' schema. Every rule clause and noise term is tested at, just
  inside and just outside its boundary, and so are the class precedence, every control in both directions, the
  refusals and the print-only separation.
  - Among them is the director's REQUIRED `test_the_two_forms_agree`, over 20,000 random (r, d) pairs.
- **The mutation harness** follows `mutate_valid_region.py`'s pattern: in place, with the sha checked before and
  after, and the child run with PYTHONDONTWRITEBYTECODE. There is one mutant per rule clause:
  - the floor's value, its inclusivity and its two-sidedness;
  - the 0.5;
  - b's factor (1 + d);
  - each absolute value.
- **There is also one mutant for each of:**
  - each noise term, K and the pass edge;
  - σ_d's ddof and its split set;
  - each class rule and its precedence;
  - the truth set;
  - the print-only separation (GiBUU domain, option A, h*);
  - each control.
- **Every mutant must be killed.** The digests and counts are recorded in §8.1 at commit.

### 8.1 As committed

| file | sha256 |
|---|---|
| `v_half.py` | `ce07a6f0429e155902d4da0532dea48f4031b4d17239fdff7e775453f4499cf5` |
| `test_v_half.py` | `1a5160491e650c4a2b84d69f24ae385d5c1b20f55c2748ab030e6926154cf41c` |
| `mutate_v_half.py` | `72a5d7adfa337ab06bbcab4362ead17928bde998cc399da44308326d627d2270` |
| `INPUTS.sha256` | `7ee797131963da0e11838a4b3fdb09d863d9631a1a3564626af630cd300f76cc` (H1's one line, as in §2) |

- **The tests:** 33, all passing, the REQUIRED `test_the_two_forms_agree` among them.
- **The mutants:** 36, all killed ([`mutants.txt`](mutants.txt), sha256 `8c1247c9d54e13e0…`). Its last line is "mutants
  36; killed 36; survivors []", and the target's sha256 is the same after the run as before it.
- **The run:** made in place in this directory, one serial process under `nice -n 19`, with every thread cap at 1. Its
  rerun in a clean clone of this declaration's commit is in `receipts/code/`, added by the following commit.
- **The pin file `PRR-READOUT.sha256` is absent by design.** The binding adds it after the PRR read is committed.
  Until then `v_half.py read` refuses (exit 4).

### 8.2 The follow-up to coverage-5b-audit's lows (#992, before the binding)

coverage-5b-audit's GO on #992 (at `fd0ed5f1`) held four non-blocking lows. The director ruled that all four close
before the V-HALF read, (a) and (c) by tests only and (b) and (d) by code. **`v_half.py`'s diff from `ce07a6f0` is
exactly these two changes:**
- **(d) the length check, in C-PRR.** C-PRR fails unless every d, b and r present at the B0 entries it reads (the 12
  truths at 991000, A7_gibuu and nominal at the five splits) has 16 values. Without it, seventeen values passed every
  control and were cut to 16 cells, and one value passed b = r(1 + d) by broadcasting. Order cannot be checked, because
  H2 carries no cell labels. The binding states its reliance on `prr_read.py`'s M16.
- **(b) the licence.** LICENCE carries §10's list in full. Its new item is "held-out truths (the truths are not held
  out)". Its ATLAS item now also names "the hybrid source of d" among this record's additions, as §10 does.

**The tests (tests only, for (a) and (c); with the code, for (b) and (d)):**

| low | test | mutant it kills |
|---|---|---|
| (a) | `test_the_departure_noise_derivative_holds_in_every_sign_quadrant`: σ_m's d-term against a central finite difference at d < 0 and d > 0, r < 0 and r > 0 | `sigma-d-sgn-d-dropped`, `sigma-d-abs-r-dropped` |
| (b) | `test_the_licence_is_section_10_in_full`: the whole LICENCE, pinned | `licence-without-held-out` |
| (c) | `test_c_form_fails_where_the_two_forms_disagree`: `ctl_form` called directly on a pair with 1 + d < 0, the only place the forms differ, which C-FINITE also refuses | `c-form-compares-a-form-with-itself` |
| (d) | `test_c_prr_refuses_an_h2_entry_not_sixteen_long`: 17 and 1 values at q3, 15 at nominal s994004 | `c-prr-no-length-check` |

- **Against `ce07a6f0`**, the four new tests give exactly two failures, the (b) and (d) tests. The (a) and (c) tests
  pass there, because their code was already right.

**As committed:**

| file | sha256 |
|---|---|
| `v_half.py` | `8a1cdbe7da7d8af4cbf50f941a40ac0754255e19ced04e913ad5d3ddb107932d` |
| `test_v_half.py` | `d2d28b9f38f422c9e350c407d76c1307795a0ac1348e0f232b87520ebfbd1df7` |
| `mutate_v_half.py` | `09a10bc79152f1988ca4eb8cb81488080e6fa3d5613e92794bb9a4a4a34f99e7` |
| `INPUTS.sha256` | unchanged, `7ee79713…` |

- **The tests:** 37, all passing.
- **The mutants:** 41, all killed ([`mutants.txt`](mutants.txt), sha256 `36696b39…`, last line "mutants 41; killed
  41; survivors []").
- **The run:** in place, the same way as §8.1. The clean-clone rerun is in `receipts/code-lows/`, and the receipts of
  §8.1 stay in `receipts/code/`.

## 9. The run, the outputs and the receipts

**The run.** It is made locally, from a fresh clone at the binding commit with empty porcelain, after
`PRR-READOUT.sha256` has landed:
`python3 -B v_half.py read --repo <clone> --out <dir>`
- Exit codes: 0 readings; 3 STOP; 4 refused.
- No network, no cluster contact, and no file outside `<dir>` is written.

**The outputs** are `readout.json` and `readout.txt`:
- the controls;
- per cell, its class and every pair's r, ν, d, b, applicability, m, σ_m, lo, hi and class;
- σ_d per cell;
- the class counts;
- the print-only sections;
- the licence.

**The receipts** go in `receipts/read/`:
- the stdout and stderr;
- the environment;
- the hand derivation at R06/A7_gibuu;
- a `SHA256SUMS`.

## 10. Licences and limits

**CITABLE FOR:** each cell's V-HALF class, with its inputs, as declared.

**NOT CITABLE FOR:**
- **coverage;**
- **a measurement;**
- **the cause of any failure;**
- **V-HALF as ATLAS's rule, or as the advisor's exact formulation.** The 1 % floor, the noise treatment and the hybrid
  source of d are this record's additions;
- **a failing cell as excluded, wrong or unreported;**
- **held-out truths.** The truths are not held out (`paper_body.tex:168`);
- **the print-only sections,** which change no class;
- **any paper or note sentence** without the PRD-referee read and Joseph.

**Limits:**
- **L1: d is FD-PRR's half-MC truth departure at split 991000, not F0b's pseudo-data source.** The two differ by MC
  sampling. Their spread is bounded only by d's five-split s.d. at A7_gibuu.
- **L2: d's noise is measured at one truth.** σ_d comes from A7_gibuu alone and is applied to every truth.
- **L3: some pairs carry no bias noise.** ν is 0 for the noise-free closure rows (closure_nuwro), so their band is σ_d
  alone.
- **L4: applicability is by the point value of |d|.** Pairs near the floor are listed, print-only.
- **L5: not blind at A7 GiBUU in R02 and R06** (§0).
- **L6: the GiBUU-family truths are graded on all 16 cells,** including the eight where no GiBUU prediction is formed.
  The exclusion is print-only.

## 11. Not changed

Nothing outside this directory is changed by this declaration. In particular, these are unchanged: V-ATLAS, V-PRIOR,
their declaration, binding and outcome; the reported result, R00–R15, every covariance block, every fake-data readout,
FD-PRR (A2 is bound in #990; A3 is #989), the paper and the note.
