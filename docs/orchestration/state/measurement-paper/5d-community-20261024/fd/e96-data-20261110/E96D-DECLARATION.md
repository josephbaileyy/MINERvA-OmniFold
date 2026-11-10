# E96D DECLARATION: the ensemble-averaged estimator E₉₆ on the real data, beside configuration (e)'s result (2026-11-10, DRAFT; runs only after the LL5D readout)

**By** the valid-region lane (director-helper-2), for the director, under `DECISION-20261110-joseph-confirm-round-scope.md`.
- Tier 2 excluded the data half of the ensemble diagnostic as not "from existing products only".
- The director moved it to the post-LL5D list with Tier 3, and asked for a code draft and this declaration.

**Nothing runs before the LL5D readout,** and then only after the director's binding, a priced dry run and each
connect's go.

**Nothing has been computed.** No E₉₆ data fit exists.
<!-- absence-ok: a statement about this draft's own status; ENS1-DECLARATION.md:105-107 keeps the data out of every ENS1 product -->

## Why, and what it is not

**The request.** The confirming round's Claude referee (`referee-methods-confirm-20261110/claude.txt@879b9501` M5,
:108-109 and :172) asked for "the ensemble average on data with the magnitude of its one deficit". The deficit's
magnitude was licensed by Joseph (`DECISION-20261110-joseph-ens1-deficit-licence.md`). This declaration is the data
half.

**What E₉₆ is.** ENS1's E₉₆ (`ENS1-DECLARATION.md` §2) is the mean of 96 fits of configuration (e), each on the input
with ENS1's internal rounding-scale jitter δ_k (±½ float32 spacing, in float64, edge-safe, seeds 10001–10096).

**ENS1's outcome stands** (`OUTCOME-20261109-ens1-stab-pass-bias-worse.md`):
- STAB_PASS, then BIAS_WORSE at Stage 0c GiBUU;
- E₉₆ is not a stabilised variant and is not adopted;
- the reported estimator is (e).

**This declaration changes none of that.** It measures what E₉₆ gives on the data, beside (e)'s data result.

## What runs

**The code:** `nd-unfolding/ensemble_estimator_data.py` and `nd-unfolding/sbatch_e96data.sh`, at the head of the PR
that carries this declaration (branch `tool/e96-data-20261110`). Their sha256s go to the director before any go.
- It is a separate data role.
- ENS1's bound probe and FD-STAB's refusals of the data (`ensemble_estimator_probe.py:136,179,247`;
  `estimator_stability_probe.py:215,481`) are unchanged.
- It reuses ENS1's internal jitter through ENS1's own functions, and calls the bound runner `s5p_numerics.main` with
  `--construction data`.

**The call** in every mode is (e)'s own (`docs/orchestration/state/s5p/s2-num-tasks.tsv:2`, `n1_data_ctrl`):
`of_inputs_5d.npz` `07fccc1a…`, `bkg_dump.npz` `2addac8f…`, config R, 5 iterations, 32 threads and estimator seed 42.
- These are read from `rounding_mechanism_probe.STABILITY`, and a test pins them to that line.
- Refused: a pseudo construction, `--capacity`, `--eavail-ratio`, pseudo or split seeds, a non-default truth or
  amplitude, and any pair but the mode's.

| mode | pair | what | unfolds |
|---|---|---|---:|
| control | `-:-` | (e)'s own float32 path, rerun: it must reproduce (e)'s product `fb5cc679…` bitwise | 1 |
| base | `-:0` | F₆₄: the float64 copy, with no jitter. It separates the float64 change from the averaging | 1 |
| ensemble | `-:0` + δ_k | the 96 fits, k = 1–96 | 96 |

## Price

**The unit:** 0.022828 CPU node-h per unfold at 8 lanes per node, ENS1's (`ENS1-DECLARATION.md:283`, measured on S1),
657 s of one lane. (e)'s own data unfold measured 692.864 s (`inventory.json` selected[360], job 58911473), at 32
threads.

| run | tasks / unfolds | expected node-h | `--time` | charge ceiling |
|---|---|---:|---|---:|
| dry: the control and k = 1, one exclusive node | 2 / 2 | 0.05 | `0:30:00` | 0.50 |
| full: F₆₄ and k = 2–96 (the dry run's products carry in and are skipped), one exclusive node, 8 lanes | 49 / 96 | 2.19 | `3:00:00` | 3.00 |
| **total** | **98 unfolds** | **2.24** | | **cap 3.5** |

- **The projection gate.** The full run starts only if the dry run's per-unfold time t gives a largest lane load
  (13 unfolds) × t + 300 s ≤ 0.9 × 3 h, that is t ≤ 724 s. Otherwise it returns to the director for a reprice.
- **The job family is `e96data`.** It has no repo hits at origin/main `1f37b251` (`git grep -i e96data`; `e96d` has
  14 and was avoided). Every fenced lane is told before the go.
- **The job script** is `nd-unfolding/sbatch_e96data.sh`.
  - It is adapted from `nd-unfolding/sbatch_ens1.sh`. The queue loop, teardown guard, expect check and receipts are
    byte-identical to ENS1's apart from the log label.
  - It has two modes: `dry` (`dry.tsv`: the control and k = 1, `--time=0:30:00`) and `full` (`full.tsv`: F₆₄ and
    k = 2–96, `--time=3:00:00`).
  - `full` refuses without the dry run's DONE receipt at the same pin. Both refuse a deploy off the pin and an
    existing log.
- **The balance check:** the cap is at most half the group balance, by iris, at the connect.

## Controls (each a STOP; the result is reported as not made, nothing repaired)

The analysis is `ensemble_estimator_data.py analyze`.

- **A-D0:** (e)'s product is `fb5cc6798b97b5902ad8f0fecbc49990271f7772f98d3063c1dc8596340e680c`, and U @ its
  `xsec_flat` equals the committed data product's f (`fd/data-product/fd_data_product.json`) to 10⁻¹² relative.
  - U is S1's functional matrix (`s1_assemble.functional_matrix(fine_map(h2_definition.json))`).
- **A-D1:** the control rerun's `xsec_flat` equals (e)'s bitwise, and its meta is the declared call. That shows the
  deploy, threads and runner reproduce (e).
- **A-D2:** F₆₄ and all 96 fits exist, each is the declared call of its mode, all come from one code, the 96
  coordinate digests are distinct, and every product records zero moved rows.
- **In the code** (`tests/test_ensemble_estimator_data.py`, 22 tests, two of them on the job script): the control equals the bound runner's own
  `-:-` product bitwise; the base is the float64 copy with no δ; δ_k is ENS1's byte for byte; and every refusal holds.
- **The mutation check** (`tests/ensemble_estimator_data_mutation.py`) kills 26 mutations by their named tests, three
  of them on the job script. Six are REQUIRED:
  - a pseudo construction admitted;
  - the base taking a protocol jitter;
  - a write without the check;
  - the control passing at one ulp;
  - the control taking the float64 path;
  - the full run starting without the dry run's DONE.

## The readout (fixed; descriptive, no criterion)

Per cell R00–R15, relative to (e)'s f (the committed data product):
- E₉₆/(e) − 1, F₆₄/(e) − 1 and E₉₆/F₆₄ − 1;
- the SD of E₉₆'s mean over its 96 fits / √96, relative to f;
- (E₉₆/(e) − 1) and (F₆₄/(e) − 1) in units of C_e's relative σ (the data product's `relative_sigma.C_e`).

**No threshold is applied, and no outcome name is given.** The director reads the committed record once.

## Licence

**CITABLE FOR (once the record lands):** E₉₆'s sixteen-cell result on the data, and F₆₄'s, as differences from
(e)'s reported result, with the SD of E₉₆'s mean. These are descriptions of how the ensemble average and the float64
change move the data result.

**This is the first statement about real data from E₉₆.** ENS1 kept the data out of every product
(`ENS1-DECLARATION.md:105-107`), and its outcome's NOT CITABLE FOR excludes "any statement about the real data". So
this result is licensed here, by its own record, not by ENS1's.

**NOT CITABLE FOR:**
- **an adoption of E₉₆,** a replacement of (e), or "a stabilised variant" (ENS1's BIAS_WORSE stands);
- **coverage,** or any uncertainty or bias statement, or a reading of the differences as any of them;
- a change to (e), C_e, C_PL, any covariance or any record;
- which estimator is right.

**A finding enters the paper only by Joseph's decision,** through the paper lane and a PRD-referee read.

Nothing is submitted, deposited or tagged.
