# AMENDMENT 1 to the staged 1B declaration: stage 1's code, for binding 2 (2026-11-02)

**By** the measurement session `coverage-5b`, for `coverage-5b-audit` to review and the director to bind as binding 2.

**Under:**
- [`FD-1B-STAGED-DECLARATION.md`](FD-1B-STAGED-DECLARATION.md), revision 2, §11 ("Still to come, in binding 2");
- [`FD-1B-STAGED-BINDING-1.md`](FD-1B-STAGED-BINDING-1.md), ruling 5 (N1, N2 and the §4.5 nit go here) and ruling 6
  (the code may be written while stage 0 runs).

**What this does:**
- delivers stage 1's code, its tests and a mutation receipt (§1);
- records six places where the declaration's text could not be built as written, with what the code does instead
  (§2). None of them changes a rule, a threshold, a truth, a draw law, a count or the price;
- answers N1, N2 and the nit (§3);
- fixes S1-0's tables and the order (§4).

**Revision 1** follows `coverage-5b-audit`'s D1 on #679 (stage 0's report). It changes four things:
- §2 (vi), new: stage 1's reads of the staged S1 assembly and of the flux constraint go through O_NOATIME;
- §1's digests and counts;
- §1.2's tests and mutants;
- §4's stat lists.

Nothing else changes.

**MEASURES:** nothing. No job for stage 1 has run. This amendment cannot authorize S1-0. Under binding 1's ruling 2,
stage 1 waits for four things:
- stage 0's PASS;
- the audit's acknowledgement of stage 0's report;
- this binding;
- Joseph being told.

## 1. The code

| file | sha256 | status |
|---|---|---|
| `nd-unfolding/fd_1b_mc.py` | `66679b27…` | new (revision 0 was `90ae99f2…`) |
| `nd-unfolding/tests/test_fd_1b_mc.py` | `7be937f1…` | new: 41 tests |
| `nd-unfolding/fd_1b_null.py` | `ec1402db…` | unchanged from `main` (binding 1 left it unbound) |
| `fd/receipts-1b/staged/mutation_mc.{py,out}` | — | 35 of 35 killed (§1.2) |
| `fd/receipts-1b/staged/stage1/tables/make_stage1_tables.py` | — | the committed generator (§4) |

**The test suites** (`TMPDIR` set): `test_fd_1b_mc.py`, `test_fd_1b_null.py` and `test_fd_1b_moded.py` together pass
98 (41, 23 and 34). Stage 0's files are untouched. `fd_1b_score.py`, `s1_assemble.py`, `fd_1b_toys.py`, `fd_1b_inv.py`
and `fd_1b_moded.py` are byte-identical to `main`.

### 1.1 What the module does (by subcommand)

**`unfold`:** one product per item, with the roles of declaration §4.2–§4.3, §6 and §9:
- `central` and `seed` at T;
- `block`: the 175 universes at d_T;
- `stat`: set A's replicas b = 1–50 of one Poisson realization of T;
- `toy`: the nature drawn, composed, at T;
- `control`: the four data reproductions;
- `capture`: the plug-in's weights.

**The other subcommands:**
- `stage-flux` and `receipt`, both on a login node;
- `walls`: S1-0's trigger;
- `null`: the draw-matched nulls for C_T and for the leave-out-MEC C_T⁻, computed from the remade products only and
  written before any toy is opened;
- `readout`: §5's grading and §7's readouts.

**What the readout refuses:**
- a null whose digest differs from the declared one;
- a null that was not made from the very products it reads, by a digest over the block products;
- toys that are not exactly the declared seeds.

**What it imports rather than copies:**
- the draws (`fd_1b_toys.draw_for_seed`);
- the experiments (`fd_1b_toys.build_full`, `mc_template_streams`);
- S1's arrays (`s5p_universe.universe_inputs` over `fd_1b_inv.universe_weights(..., "zero")`);
- the block estimators (`s1_assemble.mat_cov`, `flux_weights`, `model_abs`);
- the surrogates (`fd_1b_score.surrogate`);
- set A's jitter and unfold (`s5p_numerics.jittered`, `unfold_one`);
- the rule (`fd_1b_null`).

### 1.2 Tests and mutation

**The tests** cover every item §11 listed:
- **the composition rule:**
  - one universe is `universe_inputs`' arrays exactly, for a bank universe, a 2p2h universe, a detector-dump universe
    with `denom_nd`, MinosEfficiency and a Flux universe;
  - two universes multiply where the CV is non-zero and add where it is zero;
  - a negative CV row and a negative universe weight are kept;
  - non-finite weights are zeroed at load;
  - two flux universes refuse;
- **the experiments:**
  - the unfolding MC's flux is the nominal one, and a block's is the universe's;
  - the toy's truth is the nature's;
  - set A's streams are applied;
  - d_T is the toy path at its means;
  - set A's data path holds bitwise;
- **the plug-in:**
  - r is the push weights on the truth-passing rows;
  - control (b) holds by construction;
  - the capture is bitwise the unfold, keeps a copy and unwraps;
- **every refusal,** in both directions;
- **the remade blocks:**
  - each law's covariance is its block;
  - the flux block is constraint-weighted;
  - the lateral is S1's block, transferred;
  - the seed check fires on a difference of 1 ulp;
- **the grading:**
  - matched errors cover;
  - wide errors flag, attributed to width;
  - a bias flags, attributed to bias;
  - narrow errors do not flag (one-sided);
  - wrong correlations flag the joint region only;
  - the cell flag at its boundary count;
- **walls:** PASS and REPRICE;
- **the reads (§2 (vi)):** at each of the four call sites, the staged assembly and the flux constraint are opened
  only with `O_NOATIME`, and the copy gives the bound reader's answer.

**The mutation receipt** (`mutation_mc.py`, with digests; a kill counts only on a test failure): 35 of 35 killed.
Revision 1 added §2 (vi)'s five mutants, and all five were killed at their first run.
- **Disclosed:** at the first run, 4 of 29 survived: the toy without streams, the capture's wrap not removed, the joint
  flag dropped, and a strict cell-flag boundary.
- Each is now killed by a sharpened or added test, and 1 mutant was added when `compose` was made to stream.

## 2. Where the declaration could not be built as written

**(i) The denominator composes per cell, not per row** (§4.2).
- **The problem:** §4.2 composes the denominator's per-event weight tdw by its ratio to the CV's. The bank's `cv.npz`
  holds the denominator's coordinates (`td_pt` … `td_w`) but no CV per-event weight (`nd-unfolding/sweep_bank_5d.py:211–222`
  lists its arrays). So the ratio tdw_u / tdw_CV cannot be formed.
- **The rule instead:** the denominator composes by the same product-or-sum rule per cell, over each universe's own
  histogram (`universe_inputs`' `denom_nd`, made from its tdw or read from the detector dump). For one universe it is
  `universe_inputs`' array exactly, so the k = 1 identity and κ's nature are unchanged.
- **What changes:** the composition is per cell rather than per event, a second-order difference within a cell.
- **Detector-dump universes,** which carry `denom_nd`, enter by their cell ratio to the CV. §4's receipt reports
  whether each equals the CV's.

**(ii) The unfolding MC's flux is set with its weights.**
- **The problem:** an experiment carries the flux its unfold divides by (`s5n_pseudo.build_data`; `s5e_trace.unf_inputs`
  passes `flux` to the unfold). `fd_1b_inv.with_mc` swaps only `w_truth`, `w_reco`, `denom_nd` and `tmpl_w`, because
  I2's universes were interaction-only. Used as it is, a toy whose nature draws a flux universe would unfold dividing
  by that universe's Φ_u.
- **The fix:** stage 1's `with_mc` also sets `flux`. A toy unfolds with the nominal flux, and a Flux block with its own
  Φ_u, as S1 did. Tested, and a mutant of it is killed.

**(iii) The flux table is staged once, through O_NOATIME.**
- **The problem:** S1 read the Flux universes' Φ_u from `2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root`
  (`s1/tasks-prod.tsv`) through ROOT, which cannot open a file with O_NOATIME.
- **The fix:** `stage-flux` reads the file's bytes once through `fd_1b_inv.open_noatime`. It parses them in memory with
  `ROOT.TMemFile` and writes `hFluxCV` and `hFluxUniv` to `$W/stage1/in/flux_universes.npz`, recording the source's
  sha256.
- **How the jobs use it:** they read the staged table by digest, and map it to the pT grid by
  `flux_universe.flux_universe_bins` with its own guards, the CV match included.
- **The end-to-end check** is S1-0's Flux_0 procedure control, bitwise against S1's product.
- `stage-flux` needs ROOT and is exercised only there.

**(iv) The plug-in enters as a truth weight, like the tunes** (§6 (b)).
- **The construction:** r = w_push on the truth-passing rows, passed to `fd_1b_toys.build_full` like F1's ratio. Its
  truth goes through `s5n_pseudo.true_xsec`, which keeps the CV completeness per cell. That is the effect §6 (b) names
  through `s5p_universe.prior_inputs`, without a second path.
- **Control (b)** is unchanged: U x_T = U f to 10⁻¹². It is still labelled a plumbing check.

**(v) The two unfold paths, named.**
- S1's universe products ran through `s5p_numerics.unfold_one` in float32 (`s5p_universe.main`). The toys and I2's
  mode A run through `s5n_pseudo.unfold_negweight`.
- Both share the measured side (`s5e_trace.measured_side`, documented as `unfold_negweight`'s), and S1's G4 found the
  CV control bitwise equal to the central product.
- **The split:** `central`, `seed` and `block` use S1's path, so the four procedure controls test the very path the
  remade blocks run. The toys keep the toy path.
- Set A's replicas are `s5p_numerics`' own construction: jitter at 100 + b, float64 (the declaration's "set A's
  procedure", now explicit).

**(vi) Two bound readers open their files plainly; stage 1 now reads both through O_NOATIME** (revision 1,
`coverage-5b-audit`'s D1 on #679).
- **The problem.** Two bound readers open their files without `O_NOATIME`:
  - `fd_1b_score.load_s1` (`fd_1b_score.py:127–129`) reads the staged S1 assembly with a plain sha256 and a plain
    `np.load`;
  - `s1_assemble.flux_weights` (`s1_assemble.py:133–141`) reads the flux constraint file the same way.

  Both break the declaration's §9 read rule. In revision 0, stage 1 called them on inputs this lane did not make:
  - `load_s1` in `null` and `readout`;
  - `flux_weights` in `remade`, and through `fd_1b_toys.flux_probabilities` in every toy item.

  Stage 0's readout moved the staged assembly's atime by the same path (stage 0 report, deviation 5).
- **The fix (`fd_1b_mc.via_noatime`).** It reads the file's bytes once through `fd_1b_inv.open_noatime`, writes them
  to a private temporary copy, and runs the bound reader on that copy, unchanged.
  - The digest and the arrays both come from bytes read through `O_NOATIME`.
  - `fd_1b_score.py`, `s1_assemble.py` and `fd_1b_toys.py` are not edited and stay byte-identical to `main`, so
    every recorded `code_sha256` of theirs still holds.
  - It is used at all four call sites.
- **The tests (`NoAtime`, five).**
  - `os.open` is wrapped to record which opens carry the flag; `builtins.open` and `io.open` are wrapped to record
    plain opens.
  - At each of the four call sites, the source must be opened with the flag and never plainly, and the bound reader
    must be handed the copy, not the source.
  - A fifth test shows that the copy gives the bound reader's own answer.
  - Five mutants, one reverting each site to a plain call and one handing the reader the source, are all killed (§1.2).
- **Outside stage 1.** I2's `fd_1b_inv` (`:310`, `:652`) and stage 0's `fd_1b_moded` (`:192`, `:447`) keep the plain
  `load_s1`. They are bound and have run, and this amendment does not change them. `fd_1b_inv` also passes the staged
  `flux_constraint.txt` to `fs.derivation_blocks`, which reads it through `flux_weights`. That is the same hole, in
  I2's code.

## 3. N1, N2 and the §4.5 nit (binding 1, ruling 5)

**N1 (the audit):** a near-zero, non-zero CV weight can multiply two large ratios.
- **The bound** is declared now: **10** (`fd_1b_mc.N1_BOUND`).
- **`receipt`** prints, over the real bank, per universe and array:
  - the rows with a CV of 0 and a non-zero universe weight;
  - the rows with a negative CV weight;
  - the rows with a negative universe weight;
  - the rows that are non-finite before zeroing;
  - max |a_u / a_CV|, and the count of rows above the bound;
  - whether each detector universe's `denom_nd` equals the CV's.
- **Each toy's product** records, per array, max over rows of |a_D| / max_j |a_uj| and the count above the bound. The
  readout prints the maximum over the toys.
- **The rule:** if `receipt` shows a single-universe ratio above 10 on any row, the S1-0 readout says so. The bulk then
  waits, and an amendment under §11 follows. The same holds if the toys' composite ratio exceeds 10, which the bulk's
  readout reports before any grading is read.

**N2, the scope sentence.** It is added to §13 and to clause S, printed when such cells exist:
- **§13, CANNOT SUPPORT, added:** *in a cell where C_model_abs(T) is more than half of C_T's diagonal, a COVERS says
  little about whether the drawn groups' widths are right. Only §5.4's spread-alone readout tests that. For example (the audit's, R02),
  drawn errors 1.5× too wide hold about 0.77 there and are not flagged.*
- **Clause S, added when any such cell exists at a tune:**
  > In cells [list], where the model term dominates, coverage does not test the widths of the drawn uncertainties.

**The §4.5 nit.** "Then B depends on (m_n, m_s) only through the difference of their responses, and vanishes when they
agree" reads: **"Then B vanishes whenever the two responses agree."**

## 4. S1-0, its tables and the order

**The generator** (`stage1/tables/make_stage1_tables.py`) builds both tables:
- **S1-0:** `fd_1b_mc.PILOT[plugin]`:
  - the four controls, G18's central value, G18's toy 3,620,000 and AR23's stat replica b = 1;
  - the capture with the plug-in, or AR23's toy 3,630,000 without it;
- **the bulk:** every other item, round-robin by role, at most 22 per lane:
  - 1,050 items on 6 one-node jobs without the plug-in;
  - 1,578 items on 9 with it.

The bulk table needs the push weights' digest, so it is made after S1-0.

**This is the declared price, unchanged** (declaration §8):
- S1-0 1.0, plus 48.0 for the base or 72.0 with the plug-in;
- every job 8:00:00 at 81 % fill at the unit.

**The order after binding 2:**
1. **One connect:**
   - `stage-flux` and `receipt` on a login node, at 0 node-h, every read through O_NOATIME, with their outputs read
     before anything is submitted;
   - the tables;
   - S1-0's submission, its line sent to the director first.
2. **S1-0's readout** goes to the audit and the director:
   - walls (`fd_1b_mc.py walls --plugin`);
   - the four controls, bitwise;
   - the capture's bitwise identity with S1's central product;
   - the receipt's N1 counts;
   - the atime record.
3. **The bulk** is submitted only after walls PASS, every control passes and the audit's written acknowledgement.

   **The stat lists** (revision 1, D1). Every connect that submits takes a `stat` (atime, mtime, size) before and
   after. So do the S1-0 readout, each bulk readout, `null` and `readout`. The lists cover every file that a stage-1
   job, `stage-flux`, `receipt`, `null`, `readout` or a control comparison reads and this lane did not make:
   - the 272 stage-0 sources: the inputs npz, background, bank, detector dumps and pins;
   - the flux constraint file;
   - the flux-universe ROOT table;
   - F1's prep ratio files for G18 and AR23;
   - every file under `fd-1b-inv-20261101/i0/in` and `fd-1b-inv-20261101/i2/unf`;
   - the S1 and Stage 0 products the four controls are compared with.

   Each list is written by the connect's committed script before the first read. A difference is a deviation,
   reported and not restored.
4. **Per truth,** after the bulk:
   - `null`, whose output and digest are committed before `readout` is run;
   - `readout`, with the null's digest;
   - the HPSS copy, then the report.

## 5. For the director

1. **Bind** `fd_1b_mc.py` `66679b27…` and its generator as stage 1's code. The rules, truths, draws, thresholds and
   price are revision 2's as merged.
2. **§2 (i)–(v)** are construction findings, not rule changes:
   - (i) changes the composition from per event to per cell for the denominator only;
   - (ii) fixes a defect that the declaration's text would have carried into the toys.
3. **N1's bound of 10** is my choice, and is yours to change before any receipt is read.
