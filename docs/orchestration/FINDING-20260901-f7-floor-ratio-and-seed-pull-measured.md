# FINDING 2026-09-01 — the F7 predeclared test, measured on the candidate, and the seed-ensemble pull

**CITABLE FOR:** the two measurements below and the scope limits stated with them.
**NOT CITABLE FOR** discharging any quarantine cause, moving any gate, or adopting anything.
Gate 2 remains **FAIL**. Counts hold at CAND `1 of 7`, QUOTED `0 of 7`.

Run 2026-09-01 by the personal-account orchestrator to settle whether
`BRIEF-20260901-greif-fps-thesis-implications-for-gbdt5d.md` §4's reframing opens a route to
redefining the 5D central value as an ensemble mean. **It does not.** Both measurements are
read-only against existing artifacts; no compute was authorized or used.

## 1. The predeclared test governs, and the candidate fails it

`nd-unfolding/uq_math.py:119-138` records the **F7 rule as PREDECLARED in
`CORRECTED_UQ_PRODUCTION_STATUS.md` before the data**: measure `||mean_shift||` against the sampling
floor `sqrt(Tr C)/sqrt(N)`; at the floor, mean-centering alone is acceptable; well above it, the
CV-centered variant is **also** required and the shift must be reported either way, *"never silently
dropped."* `F7_FLOOR_MULTIPLE = 2.0`, and the file states it was set so that a shift AT the floor is
unambiguously below and the observed value unambiguously above — *"a threshold placed to make today's
answer come out right is not a criterion."*

Measured from `stamped_bkgaware_meancentered_20260812.root`'s own stamps, through `uq_math`'s own
functions rather than a re-implementation:

| | |
|---|---|
| `sqrt_tr_new` | `5.269625166386846e-38` |
| `upstream_joint_mean_shift_norm` | `1.878697e-38` |
| `upstream_n_throws` | `160` |
| sampling floor `sqrt(Tr)/sqrt(N)` | `4.166004e-39` |
| **`||mean_shift|| / floor`** | **`4.510x`** (threshold `2.0`) |
| **`f7_cv_centered_required`** | **`True`** |

**So mean-centering alone is disqualified for the CANDIDATE, not only for the July artifact.** This is
consistent with, and independently supports, cause 2's 2026-08-12 discharge for the candidate, which
required the CV-centered variant rather than waiving it.

## 2. The Greif analogy does not transfer, and this is the substantive finding

The brief's §4 observes that Greif mean-centers without raising a question because his nominal **is**
the ensemble mean, and reframes our disqualification as following from our nominal being a separate
draw. That reframing is fair as far as it goes, **but the two ensembles are not the same kind of
object, and the analogy fails at exactly that point.**

Greif's centering is over a **bootstrap / seed** ensemble — a nuisance one legitimately averages over.
Our mean shift is measured against the **joint SYSTEMATIC throw** ensemble.
`nd-unfolding/unified_throw_cov.py:288` says so in its own words: *"Systematic throws all use the SAME
estimator seed. ML variation belongs"* elsewhere. **Defining a central value as the mean over
systematic throws would fold systematic variation into the central value.** Greif does not do that,
and no precedent here licenses it.

## 3. The seed-ensemble pull, which rules out the benign explanation

Measured over the 24-member `seedscan_split_5d` ensemble in `mii/member_k000000/` against the frozen
production CV `products/5d/xsec_5d_MEFHC_5iter_lgbm.root` (`hXSecND_flat`), on the `cv>0` support,
which came out at exactly **10694** bins as `mii_root_payload_classes.py`'s `REPORTED_NBINS` requires:

| | 3D reference (2026-06-03 audit) | **5D measured** |
|---|---|---|
| pull median | `0.63` | **`0.588`** |
| pull p90 | `1.48` | **`1.616`** |
| shift median | `+0.013%` | **`+0.0129%`** |
| band median | `0.450%` | `0.651%` |
| de-noised `÷√n` | `0.14%` | `0.133%` |

Total shift `-0.0338%`; `27.0%` of bins above pull 1 and `5.0%` above pull 2, against `4.6%` expected
for a normal — no tail pathology.

**The frozen CV is a consistent draw from the seed family.** That does not support redefining the
central value; it **removes the one explanation that would have made the throw-mean offset benign.**
ML stochasticity does not account for a `4.510x` offset, and the offset survives without it.

## 4. Scope limits, stated rather than left to inference

- **`ssplit5d` varies the TRAIN/TEST SPLIT ONLY.** The npz metadata carries `estimator_seed = 42` for
  all 24 members while `split_seed` sweeps `1..24`. It is **not** the T2K-style *total* ML band: 3D
  measured model-init only, this measures split only, and **no scan anywhere varies both.** The
  2026-06-03 audit's recommendation (3) remains open. The near-identical pulls across two different
  noise sources are interesting and are not a like-for-like comparison.
- **These are REHEARSAL products.** Measuring from them is legitimate; quoting or adopting from them
  is not.
- **§3 measures a different ensemble from §1.** The seed family is not the throw family, and no claim
  here transfers between them.

## 5. A statistic this lane deliberately did NOT compute

An ad-hoc per-bin pull of the nominal against the throw ensemble was proposed by this lane and then
**not run**, because a predeclared statistic already governs this question. Choosing a new statistic
after seeing the data is the failure mode this campaign repeatedly files against others, and it does
not become acceptable when the lane doing it agrees with the expected answer.

## 6. A correction to this lane's own reasoning, recorded rather than quietly dropped

Before finding the predeclared rule, this lane argued from `||mean_shift|| / sqrt(Tr C) = 28%` that the
nominal sat *"comfortably inside"* the throw ensemble. **That was wrong, and it pointed the opposite
way to the truth.** The governing denominator is the sampling floor `sqrt(Tr C)/sqrt(N)`, smaller by
`sqrt(160) ≈ 12.65`. The same shift is therefore several times the floor, not a fraction of it. A
norm-level heuristic against the wrong denominator is not a weak version of the right test; it is a
different test with the opposite answer.

## 7. What this finding does not do

It discharges nothing, adopts nothing, and moves no gate. It does not settle whether `4.510x` and the
`4.83x` recorded in `uq_math.py`'s comment describe the same inputs — see `OI-186`. It makes no claim
about `OI-126`, consistent with the brief's own explicit non-claim.
