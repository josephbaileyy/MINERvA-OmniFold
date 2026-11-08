# SCOPING: can the advisor's point (3) be tested blind? (2026-11-07)

**By:** the valid-region lane (session director-helper-2), at the director's request on Joseph's behalf.

**The question, as the director put it:** can point (3), "in the identified region of 2D mismodeling, the
mismodeling is localized in the extra dimensions, in valid regions", be tested with operands nobody has seen?
Reading (3) of [`OUTCOME-20261107-valid-region.md`](../../../OUTCOME-20261107-valid-region.md) could not be, because
its operands had been seen (L4).

**How it was done:**
- records only, at 0 node-h, with no cluster contact;
- nothing was computed that compares the data with the prior or with any generator;
  <!-- absence-ok: a statement of this lane's own process in this scoping, not a claim that a result is absent from the repository -->
- every search printed its hits with the numbers masked (§6);
- the one computation, [`scoping/power_sim.py`](scoping/power_sim.py), reads only covariance matrices, Tune v1's
  predictions g, simulation quantities and data-bootstrap widths. It reads no data central value. Its output is
  [`scoping/power_sim.out`](scoping/power_sim.out).

All line numbers are at main `59997e37d`.

**MEASURES:** an inventory of the committed products finer than the 16 cells, and an indicative resolved size for
within-quadrant contrasts, from covariance and simulation only.

**CITABLE FOR:**
- the inventory (§1), within the search scope stated in §6;
- the 16-cell contrast resolved sizes (§2a), which are covariance-only and reproduce the bound readout;
- the multiplicity arithmetic (§3);
- the verdict as a scoping judgement for Joseph's decision.

**NOT CITABLE FOR:**
- any reading of the data, the prior or a generator;
- the finer-cell resolved sizes in §2b as measured: they are an inference from a scale factor;
- the absence of a data-against-prior comparison outside the §6 scope, or in anyone's memory or console;
- a declaration. None is drafted here.

**What the lane saw while searching.** Masking hid the numbers, but two kinds of material came into view:
- the captions' qualitative descriptions of the (E_avail, W) and (E_avail, q₃) data/Tune v1 maps. These are
  integrated over p_T and p_∥;
- two macro values, integrated over the same, at `docs/analysis-note/values.tex:238` and `:240`. Their names say
  "data over Tune v1" in (E_avail, W) regions.

Nothing at the H2 box level, and nothing within a (p_T, p_∥) quadrant, came into view.

## 1. The unseen-operand inventory

The 16 cells resolve the extra axes within each (p_T, p_∥) quadrant only as far as their merges allow. A finer
product helps only if it nests inside the quadrant edges p_T = 0.7 and p_∥ = 4.5 GeV/c.

| # | product | nests in the quadrants? | (a) data against the prior or a simulation printed at this granularity? | (b) covariance at this granularity | (c) fake-data closure at this granularity |
|---|---|---|---|---|---|
| K1 | **the 32 H2 boxes** (28 used, 4 unreported), the 16 cells before their 12 purity merges (`nd-unfolding/pv-ladder/readouts/h2_definition.json`, sha256 `b6790761…`, `steps` and `h2_to_reporting_cell`) | **yes:** 2 bins per axis on the H2 edges (`nd-unfolding/s5p_stage1_inspect.py:47`) | **no hit in the §6 scope.** The only data-side H2 quantities committed are widths: `sigma_boot_data_R/H2` (`docs/orchestration/state/s5p/stage1/stage1_inspect.json`, sha256 `def4c67c…`) and `study_N/N1_data/H2/*_rel` (`state/s5p/stage2/stage2_receipt.json`, sha256 `0daa7cd8…`). The C_model,5D positive control uses data *shifts* under prior reweighting on the 27 base cells (`DECISION-20261024-joseph-h2-16-cell-definition.md:39`), not data against the prior. The earlier reads disclosed at `H2-DEFINITION-DECLARATION.md:23-35` are widths, h and P5 as a file. **But the operand is committed:** the reported (e) central value on the 65,856-cell fine grid is tracked at `…/fd/receipts-f1/run/cluster/f1b3/prep/k1_p5_rerun.npz` (`e36f3b25…`, `FD-PSCRATCH-RETENTION-PROPOSAL.md:48`, `:82`). This lane did not open it | **no.** Only S1's 16 × 16 blocks (`fd_data_product_cpl.json`, `d6752d2c…`, `matrices`) and stat-only diagonal widths at H2 (the two width keys above). The inputs keep fine arrays: S1's products carry `xsec_flat` (`S1-REPORT.md:229`, `:317`), archived on HPSS (`FD-PSCRATCH-RETENTION-PROPOSAL.md:76`). C_resp's and C_PL,5D's fine-level inputs were not checked | **partly.** Development residuals at the 32 boxes for nominal Tune v1 and 5 stress truths, with s5e candidate R at its development operands (`stage1_inspect.json` `development_residuals/<truth>/H2`). **Not** the 12 graded F0b truths: their readouts are 16-cell, and the fine products (`xsec_flat`, `xtrue_flat`, shape 65,856; `FD-F0-DECLARATION.md:223`) are on pscratch (`:76-80`). An older estimator's historical noise-free recovery at H2 is in `nd-unfolding/gbdt_model_dependence/results/recovery.csv` |
| K2 | **finer partitions nested in the quadrants**, built from the fine grid (E_avail edges 0, 0.1, 0.2, 0.4, 0.8, 1.5, 3, 100; q₃ and W similar; `s5p_stage1_inspect.py:38-44`) | yes: the fine grid contains every H2 edge | **its quadrant sum is printed.** The 7 × 6 (E_avail, W) data/Tune v1 map, integrated over p_T and p_∥ (`docs/analysis-note/sec_eavailw.tex:124`; `primer_body.tex:217`; release code `publication/release/figs/export_fig_arrays.py:10`). The quadrant-resolved version: no hit | none | none committed; same fine products as K1 |
| K3 | **partition J**, 109 joint cells of the 153 functionals | **no.** J's edges p_T 0.55, 0.85 and p_∥ 3.5, 6.0 (`s5p_stage1_inspect.py:45`) cross the quadrant boundaries | not searched to the end: J fails the nesting requirement | z-cv (configuration (a)) on the 153 functionals; not (e) | s5c/s5e campaign closures (configuration (a)/F2) |
| K4 | **EW**, the 42 (39 in the ladder) (E_avail, W) cells | **no:** integrated over p_T and p_∥ | **yes, printed:** `sec_eavailw.tex:124`, `primer_body.tex:217`, `values.tex:238`, `:240` | z-cv, configuration (a) | yes, configuration (a) (`paper_body.tex:105`, development variant) |
| K5 | **the 3D and 4D results** (configuration (a): p_T, p_∥, E_avail and q₃) | yes, on their own grids | **yes, for the very question.** `nd-unfolding/q3_vs_ascencio_metrics.py:92` (first committed `b64cf582`, 2026-06-09; last touched `8ff5d843`) prints "low-Eavail data/GENIE in pT slices (flat => excess factorizes from muon kin.)". Its output is not in the §6 scope, but the script was written to be run. Projections against Tune v1 are printed at `sec_3d.tex:145` and `:223` | **none quoted:** "no 3D or 4D covariance is quoted" (`sec_3d.tex:10`) | not for (e) |
| K6 | the 16 cells (reading (3)) | yes | **seen** (OUTCOME L4) | yes | yes (F0b) |

**The only candidate is K1**: it nests, and nothing at its granularity was found printed. Its sub-box contrasts
are not independent of what has been seen:
- each merged cell's sum is a seen 16-cell value;
- the quadrant-integrated extra-axis pattern is printed (K2, K4);
- the June script (K5) asked the same factorization question of a different estimator.

So K1 is operand-blind, not uninformed.

## 2. The power, from covariance and simulation only

**The yardstick.** If the departure were wholly localized in one sibling, a single-axis contrast between it and an
unaffected sibling would be at least about r_Q. The values are Q1 +0.099, Q2 +0.046, Q3 +0.170 and Q4 +0.212
(`OUTCOME-20261107-valid-region.md:107-110`). "Resolvable" here means 3σ(Δr) < r_Q.

**(a) The 16 cells (measured, covariance-only).** σ(r_i − r_j) comes from the reported
C_total+C_resp+C_PL,5D, in units of Tune v1's g (`power_sim.out`, first block). It reproduces the bound readout's
`resolved_3sigma`: R12−R14 0.1976 and R10−R11 0.5579 agree exactly; R06−R07 gives 0.2253 against 0.2254, the gap being
the omitted V_P term.
- The 24 within-quadrant pairs have 3σ from 0.150 (R04−R06) to 0.558 (R10−R11).
- **Only 1 of 24 resolves r_Q:** R12−R14 in Q4, 0.198 < 0.212.
- The contrast σ is 14–47 times its stat-only value. The median per quadrant is ×31.7, ×19.7, ×44.7 and ×34.0
  (Q1–Q4). **The contrasts are systematics-limited at the 16 cells already.**

**(b) The H2 boxes (inference).** The 38 single-axis edges within quadrants among the 28 used boxes include 13
that fall inside a merged cell. These 13 are the information the 16 cells lack.
- **The stat floor:** 3σ is 0.008–0.021, from `sigma_boot_data_R/H2` with 100 replicas, assuming independence. Stat
  alone would resolve every edge.
- **No committed covariance says how the systematic terms behave at the boxes.** Scaling the floor by its quadrant's
  16-cell factor gives 3σ of 0.20–0.85. **That resolves r_Q at none of the 38 edges.**
- The scale factor is an assumption. The boxes' lower purity suggests that response and regularization terms do not
  shrink. 26 of the 38 edges, and every one of the 13 new edges, touch a box with MC purity below 0.1. That purity is
  why the boxes were merged (`h2_definition.json` `steps`; purities from `stage1_inspect.json` `mc/H2/purity`).

**So whether K1 has power is open,** and the indication is that it does not. Only a box-level covariance can
settle it.

## 3. The multiplicity

| family | contrasts | P(any \|z\| ≥ 3) under the null, if independent | Bonferroni two-sided 0.05 bar |
|---|---|---|---|
| the new edges, inside a merged cell | 13 | 0.035 | \|z\| ≥ 2.89 |
| all single-axis edges within quadrants | 38 | 0.098 | \|z\| ≥ 3.21 |

From `power_sim.out`, last block. The edges share boxes, so they are correlated, and the independent figures are
approximate.

## 4. The blockers

1. **There is no box-level covariance.** Assembling C_total+C_resp+C_PL,5D on the 28 boxes needs the fine-array
   products:
   - S1's are on HPSS and pscratch;
   - C_resp's and C_PL,5D's fine-level inputs are unchecked.
   This needs cluster contact. The pscratch copies are exposed to purge from about 2026-12-22
   (`RECORD-20261030-director-pscratch-retention-additions.md:22`).
2. **There is no box-level validity grading.**
   - V-ATLAS's A3 needs the 12 F0b truths' closure on the boxes under the box covariance. Their fine products are on
     pscratch. The committed box-level closure covers 6 development truths, not the 12.
   - V-PRIOR's S_b needs the same.
   - The low purities (§2b) predict that many boxes fail either rule. A test confined to valid boxes may have few
     edges left.
3. **The power is unproven and indicated against** (§2).
4. **The blindness is partial and rests on custody, not on unavailability.**
   - The fine data central value is in git (K1 (a)).
   - The quadrant-integrated pattern is printed (K2, K4).
   - The June script asked the same factorization question (K5).
   - A declaration would have to fix the boxes, the edges, the rule and the bar before anyone forms a box-level data
     quantity, and disclose all of this.
5. The paper's own figures show nothing finer than the 16 cells against a prediction (`paper_body.tex:96-106`,
   `:267-269`). This is not a blocker.

## 5. Verdict

**FEASIBLE ONLY WITH NEW COMPUTE, and expected, by inference, not to be powered.**

**The test it would be:** on K1, the 13 within-merged-cell single-axis contrasts, restricted to boxes valid under a
box-level V-ATLAS/V-PRIOR, against a declared bar such as Bonferroni |z| ≥ 2.89. It would be declared before any box
data quantity is formed.

**What is missing, and the cheapest order:**
1. **A power gate, covariance-only, before any data/prior quantity.** Assemble the reported covariance blocks on the
   28 boxes from the retained fine products, and compute the 13 edges' 3σ against r_Q. This is login-node work, like
   S1's assembly (`S1-DECLARATION.md:122`, 0 node-h), but it needs cluster contact. Check C_resp's and C_PL,5D's
   inputs first. **If no edge resolves r_Q, stop:** point (3) is then not testable at this granularity, blind or not.
2. **If the gate passes,** re-grade the 12 F0b truths' closure on the boxes from their pscratch products, at login
   node, 0 node-h by analogy with F0b (`FD-F0-DECLARATION.md:42`). That fixes which boxes are valid.
3. **Only then** would a declaration on the data follow.

Both steps act before the pscratch purge exposure noted in §4.

**The lane's recommendation, if Joseph wants (3) pursued:** run step 1 alone as a priced and bound
covariance-only step. Step 1 alone likely settles the question with no data read.

## 6. Search scope (for the "no hit" entries)

Every search used `git grep -n -I` on main `59997e37d`, with output masked by
`(?<![A-Za-z_0-9])[+\-−]?\d+(?:\.\d+)?` → `#` ([`scoping/mask.py`](scoping/mask.py)). Re-runnable as [`scoping/search.sh`](scoping/search.sh) (output [`search.out`](scoping/search.out)) and [`scoping/h2_json_scan.py`](scoping/h2_json_scan.py) (output [`h2_json_scan.out`](scoping/h2_json_scan.out)):
- **data against a prior or simulation, at the boxes:** a structural scan of every committed `*.json` naming `"H2"`,
  `h2_cells` or `"h2"` (44 files) for 32-element numeric arrays. It found mc, closure, departure and width keys
  only, listed in K1;
- **text:** `*.md`, `*.tex` and `*.txt`, for the word H2 within 80 characters of tune, prior, data/, f/g, pull or
  departure (`search.sh` S1). It gave 13 hits, and each was read masked. None is a data-against-prior quantity:
  - widths, and data shifts under prior reweighting: `S2-H2-CMODEL-SCOPE.md:227`,
    `nd-unfolding/gbdt_model_dependence/README.md:69`. The latter's `results/prior.csv` header has
    `data_boot_sigma_pct` and `d1..d5_shift_pct` only;
  - simulation recovery: `gbdt_model_dependence/README.md:62`, `state/next-preparation-20261009/gbdt/REPORT.md:116`,
    `:177`, `PROPOSAL-20261005-scalar-measurement-successor.md:141-144`;
  - definitions and C_model construction: `H2-DEFINITION-DECLARATION.md:135`,
    `H2-DEFINITION-ADDENDUM-GIBUU-DOMAIN.md:123`, `S2-H2-CMODEL-SCOPE.md:80`, `:170`,
    `DECISION-20261024-joseph-5d-community-standard-route.md:60`;
  - an unrelated "H2" (a PET hypothesis or study label): `nd-unfolding/pet/...` (three lines);
- **comparisons broken down by p_T or quadrant:** extra-axis names within 60 characters of slice, per p_T,
  quadrant or p_T bin, over `*.md`, `*.tex` and `*.py`;
- **the "factoriz" family,** for recorded output of K5 (no hit beyond an inventory listing);
- **code that reads P5** (`k1_p5`): two files. `build_cmodel5d.py` forms data shifts on the reporting cells, not data
  against the prior;
- **figures:** the 415 committed figures were listed by name, and the captions of those about E_avail, q₃, W or 5D
  were read with numbers masked.

**Out of scope:** pscratch, HPSS, consoles, session transcripts, figure pixels.

## 7. Not changed

Nothing else changed: no reported value, covariance, readout, paper or note. No declaration is drafted. Joseph
decides whether one follows.
