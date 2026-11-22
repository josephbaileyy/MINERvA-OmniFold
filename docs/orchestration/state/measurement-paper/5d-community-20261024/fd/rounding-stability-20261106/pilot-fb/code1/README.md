# PILOT-FB code 1: the code for the bound design (receipt)

**By** session tier3-design, under PILOT-FB-BINDING-1 (#1217, main `94f31779`). It binds
`PILOT-FB-DECLARATION.md` rev 3 at M_PFB `522ac0b6`, and ruling 1 asks for code with its tests and declared mutants,
then an independent code audit by two readers and a code addendum before any connect. **Nothing has run on the
cluster.**
<!-- absence-ok: an operational status of this tranche, not a claim that a result does not exist -->

## The code, at `1d8873ba`

| file | sha256 | what it does (declaration rev 3) |
|---|---|---|
| `nd-unfolding/fb_pilot_edges.py` | `5add7476ed7f48eddd898e509221ddb44ffe0ab72f782decffdbf187bd4b0015` | §3 rules 1–7: finiteness, the zero band, z from the fit column with K = float64(float32(1e-35)), admissible gaps against the jitter's \|x\| envelope, placement and the walk, INFEASIBLE. Also the intended upper-bound lists, and the twelve forced-bins files with `INDEX.json` (G0) |
| `nd-unfolding/fb_pilot_gates.py` | `b55ea40d3691521248813b1702d7c3442aa7564e9956d1a8d211a1522371cd09` | **G2:** intended indices, under LightGBM's `value <= bound`. **G3:** (a) the rebuilt Dataset's dumped training indices, (b) every fitted threshold, at `{:.17g}`, in the intended list, (c) no missing-value or categorical split. **J:** bitwise comparisons for a jitter and value comparisons for a base, plus moves off and on the grid edges |
| `nd-unfolding/fb_pilot_probe.py` | `d989a9e5ff62daf1a3af53b8667cdf5476c4d2430a4618261be7b1b90787472d` | the prep step: the edges, written before any fit. One remedy unfold through RS1's bound stability path, with the role rebindings and the in-process rebuild of the base and jittered role matrices (§2 item 9; J2 calls `build_pseudo` as `s5p_numerics.py:198` does, with `signed_sample`). A gate sidecar for every product |
| `nd-unfolding/fb_pilot_analyze.py` | `6c06e3a4a139cfc4048c2a2772614c860ebf37898021d5109992bdf2ccc6d159` | G4, G1 and the per-product gates; the eight gate outcomes in their precedence; S1 (RS1's `spread_ratio`, with a non-finite endpoint read as INCONCLUSIVE), S2, and S3 with S3-place and S3-res; INVALID; the seven rows and the readouts. Also the job's round-1 gate |
| `nd-unfolding/sbatch_pfb.sh` | `45e86e5075062da7e34eabd9e499aa500d4f221812983a24f21b9066e91b76c9` | the deploy pin and a fresh root; prep, round 1, the round-1 gate and the wall projection, then rounds 2–3. The job status distinguishes an interruption from a deliberate gate stop |
| `nd-unfolding/tests/test_fb_pilot.py` | `f601c32c928a10ad4c35a8b30aac92e08b2a8cece2e3b065d3abc019c83e6f3b` | 33 tests |
| `nd-unfolding/tests/fb_pilot_mutation.py` | `8e2e87ddf21c0aa1163ee737fc768a3009f99dcd14916a7e8b3998ad3caad625` | 34 mutants |

A0R is RS1's own A0 task, run unchanged as `rounding_mechanism_probe.py run --arm A0` with the pair `-:-` and tag
`rs1_A0`. G1 compares its `xsec_flat` with RS1's pinned base.

## Choices the declaration leaves to the code (for the code audit)

1. **G3 (a)'s rebuilt Dataset** takes the fit's matrix and the binning keys of the estimator's own `get_params()` at
   that fit: `max_bin`, `forcedbins_filename`, `bin_construct_sample_cnt`, `min_data_in_bin`, `feature_pre_filter`,
   `min_data_in_leaf`/`min_child_samples`, `use_missing`, `zero_as_missing`, threads, `deterministic` and
   `force_row_wise`. Labels and weights do not enter binning (§2 item 2), so the label is zeros.
2. **When each G3 read runs.** G3 (a) runs on each role's first fit, as §2 item 2 allows: one role's matrix is the same
   at every iteration. G3 (b)–(c) run on every fit.
3. **Scored rows** are the rows a role first predicts on:
   - for clf1 and clf2, `predict_proba`'s argument;
   - for reg, `predict`'s argument (the reco-failing truth rows);
   - for the refinement, its fit rows, since it scores the same rows.
4. **J's rebuild runs inside the bound `unfold_one`,** after the runner's own installs (`s5e_candidate.install`,
   `s5p_truths.install`). That way `build_pseudo` sees the same rebinding the run saw.
5. **The identity gate** compares `max_bin` and `forcedbins_filename` from each role's `get_params()` at its fit. The
   product's `estimator_params` and `refinement.classifier_params` also carry them, because the bound code records
   `get_params()`.
6. **A root that is not fresh** writes `job-status.refused.json` instead of `job-status.json`, which is itself one of the
   paths that must not exist. The analysis takes whichever the job wrote.

## The receipts, in a clean clone at `1d8873ba` (`receipts.sh`, sha256 `b90fe25b…`)

| file | result |
|---|---|
| `tests_lightgbm.txt` | Python 3.10.20, numpy 2.2.6, LightGBM 4.6.0, scikit-learn 1.7.2 (a uv venv): 33 tests OK, none skipped, exit 0 |
| `mutation.txt` | the same venv. The unmutated suite: 33 tests OK, none skipped. Mutation check PASS: 34 of 34 killed, each by its named test |
| `tests_laptop.txt` | Python 3.12.2, numpy 1.26.4, no LightGBM: 24 OK and 9 skipped (the LightGBM tests), exit 0 |
| `syntax.txt` | `bash -n sbatch_pfb.sh`: exit 0. The clone is clean after the run |

**What the tests cover, each guard in both directions** (§8):
- **admissibility:** u = ±½ on both signs, powers of two and their neighbours, signed zeros, the zero band, and both
  auditors' signed-spacing counterexamples;
- **placement and z per role:** one pool gives one edge set; ties and the walk; INFEASIBLE; edges at 17 digits;
- **G3, harmful changes that must fail,** each with a fixture that activates it:
  - a middle edge removed, so the refill changes the partition, caught by (a);
  - an edge moved inside a used training gap, caught by (b), with a scored row shown to change bin;
  - a misparsed edge used as a split, caught by (b);
  - a NaN on a split feature, caught by (c);
  - an unopenable file, caught by (a);
  - an unforced fit;
- **G3, harmless changes that may pass,** with predictions shown unchanged: a surplus edge after the budget, and an
  unused bound moved;
- **LightGBM's own zero split** stores exactly K, which (b) accepts, while it would refuse the decimal 1e-35;
- **the remedy on a toy:** with forced edges, predictions are bitwise identical under the jitter, on fit and on scored
  rows. Without them, the jitter moves the predictions;
- **J:**
  - the bound selection, and that `jitter_coords` of a role matrix is not what a role receives (Grok's case);
  - a source slice is not the signed sample;
  - an unapplied jitter, a wrong seed and a moved grid-edge entry are each caught;
  - a base is compared as values;
  - J2's rebuild takes the run's truth, amplitude, split key, pseudo-seed and ratio;
- **the outcome:** all 16 combinations reach one row; the bars include equality; rows 5 and 7 name what crossed; a
  non-finite endpoint reads INCONCLUSIVE; the gate precedence, including a round-1 gate failure with the later
  products absent; the INVALID branches; and S2 and S3 against their definitions.

## What a local test cannot show (for the audit and the code addendum)

The pipeline end to end on the real inputs. `of_inputs_5d.npz` and the background dump live only on the cluster:
- The probe's rebindings, the role captures and J's rebuild are exercised here on synthetic arrays and stubs, not
  through `s5p_numerics.main`.
- The job script's lanes and gates are syntax-checked, not run.

The declaration has no dry run (§7). Its round-1 gate is the first place these meet the real pipeline: a wiring fault
there stops the run with a named gate outcome, at about one round's cost. The code audit may ask for a login-node smoke
on the real inputs (prep only, no fit, 0 node-h) before the go.
<!-- absence-ok: the scope of these local tests, not a claim that a result does not exist -->

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the code's shas, what each module does, the choices listed, and these receipts.
- **Not citable for:** any PILOT-FB reading. No note or paper wording follows from this code.
