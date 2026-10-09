"""N2, as specified in DESIGN-20261008-2d-independent-statistical-validation.md §16.1 (PROPOSED).

N2 asks one narrow question: is the production DATA bootstrap faithful when the pseudo-data do not
sit on the training events? It is conditional on one training bank and one base pseudo-data set,
holds the MC stream fixed, uses no truth, and validates no interval, no MC stream, no coverage and
no total uncertainty. It is not admitted: running it needs Joseph to lift the KNOWN_ISSUES 85
deferral, the identity-carrying rebuild (R0) and an admission record (``harness.py``).

* Arm T: 50 pseudo-data sets drawn from the reservoir ``R`` (outer seeds ``20_261_008_000_000 + e``),
  each unfolded once, central only, with the fixed training bank ``S``. DATA: fresh pseudo-data.
  MC: held (no MC bootstrap).
* Arm B: 50 data-only bootstrap replicas of arm T's first pseudo-data set (inner seeds of
  ``e = 1``, by §3's formula ``20_261_008_200_000 + 1000 e + r``). DATA: bootstrap of one set.
  MC: held.
* Statistic: ``rho_b = sd_B,b / sd_T,b`` (``ddof = 1``) per reported bin; median ``M`` with a 95 %
  interval from 2,000 resamples of replicas within each arm. Rule: faithful if the interval lies in
  [0.80, 1.25], over-scatter if entirely above, under-scatter if entirely below, else INCONCLUSIVE.

Items §16.1 leaves open, fixed here only as proposals the registration must confirm or replace:
the resample seed (``RESAMPLE_SEED``); ``sd`` rather than the KI-85 relative spread
(``sd / mean``), which differ when the arms' means differ; which fold supplies the purity
background template (``INTENDED_FOLDS``).
"""

import hashlib
import json

import numpy as np

DESIGN = "N2"
N_T = 50
N_B = 50
OUTER_SEED_BASE = 20_261_008_000_000
INNER_SEED_BASE = 20_261_008_200_000
BASE_EXPERIMENT = 1
TOLERANCE = (0.80, 1.25)
N_RESAMPLE = 2000
LEVEL = 0.95
RESAMPLE_SEED = 20_261_009  # proposed; §16.1 does not fix it
N_REPORTED_BINS = 205

#: The production E_S settings (DESIGN §2), held fixed for every member; thread count included.
FROZEN_ESTIMATOR = {"driver": "2d-unfolding/unfold_2d_omnifold_unbinned.py", "estimator": "lgbm",
                    "iters": 5, "use_weights": True, "bkg_mode": "purity", "seed": 1,
                    "device": "cpu", "threads": 64}

#: Which fold each array a member hands to OmniFold must come from (contamination test C6).
INTENDED_FOLDS = {"bank": "training", "background_template": "training",
                  "pseudo_data": "reservoir"}

STREAMS = {"T": {"data_stream": "pseudo-data: Poisson(lambda_i) from the reservoir, expanded rows",
                 "mc_stream": "held"},
           "B": {"data_stream": "bootstrap: data-only Poisson(1) per row of the base pseudo-data",
                 "mc_stream": "held"}}


class DesignError(ValueError):
    """A plan or a result departs from the frozen N2 design."""


def design_record():
    return {"design": DESIGN, "n_T": N_T, "n_B": N_B, "outer_seed_base": OUTER_SEED_BASE,
            "inner_seed_base": INNER_SEED_BASE, "base_experiment": BASE_EXPERIMENT,
            "tolerance": list(TOLERANCE), "n_resample": N_RESAMPLE, "level": LEVEL,
            "resample_seed": RESAMPLE_SEED, "n_reported_bins": N_REPORTED_BINS,
            "estimator": FROZEN_ESTIMATOR, "intended_folds": INTENDED_FOLDS, "streams": STREAMS}


def design_digest():
    return hashlib.sha256(json.dumps(design_record(), sort_keys=True).encode()).hexdigest()


def members():
    """The declared plan: T001..T050, then B001..B050."""
    base_id = f"T{BASE_EXPERIMENT:03d}"
    out = [dict(id=f"T{e:03d}", arm="T", index=e, data_seed=OUTER_SEED_BASE + e, boot_seed=None,
                base=None, estimator=FROZEN_ESTIMATOR, **STREAMS["T"]) for e in range(1, N_T + 1)]
    out += [dict(id=f"B{r:03d}", arm="B", index=r, data_seed=OUTER_SEED_BASE + BASE_EXPERIMENT,
                 boot_seed=INNER_SEED_BASE + 1000 * BASE_EXPERIMENT + r, base=base_id,
                 estimator=FROZEN_ESTIMATOR, **STREAMS["B"]) for r in range(1, N_B + 1)]
    return out


def validate_plan(plan):
    """Refuse any plan that is not exactly the frozen one, naming the first departure."""
    want = members()
    if len(plan) != len(want):
        raise DesignError(f"plan has {len(plan)} members, the design {len(want)}")
    for got, ref in zip(plan, want):
        if got != ref:
            diff = sorted(k for k in set(got) | set(ref) if got.get(k) != ref.get(k))
            raise DesignError(f"member {got.get('id')} departs from the design in {diff}")
    for m in plan:
        if m["mc_stream"] != "held":
            raise DesignError(f"{m['id']}: N2 holds the MC stream; {m['mc_stream']!r} is a "
                              "different procedure")
    return plan


def check_record(member, record):
    """A member's result must carry the frozen estimator and a finite value per reported bin."""
    if record.get("estimator") != FROZEN_ESTIMATOR:
        raise DesignError(f"{member['id']}: ran with {record.get('estimator')}, "
                          f"not the frozen settings")
    v = np.asarray(record.get("values"), float)
    if v.shape != (N_REPORTED_BINS,) or not np.all(np.isfinite(v)):
        raise DesignError(f"{member['id']}: values shape {v.shape} or non-finite entries")


def ratios(XB, XT):
    return XB.std(axis=0, ddof=1) / XT.std(axis=0, ddof=1)


def median_interval(XB, XT, n=N_RESAMPLE, seed=RESAMPLE_SEED, level=LEVEL):
    """Interval of the median ratio, resampling replicas within each arm (the KI-85 construction)."""
    rng = np.random.default_rng(seed)
    meds = np.empty(n)
    for i in range(n):
        meds[i] = np.median(ratios(XB[rng.integers(0, len(XB), len(XB))],
                                   XT[rng.integers(0, len(XT), len(XT))]))
    a = (1 - level) / 2
    return [float(np.quantile(meds, a)), float(np.quantile(meds, 1 - a))]


def classify(ci):
    lo, hi = TOLERANCE
    if lo <= ci[0] and ci[1] <= hi:
        return "faithful"
    if ci[0] > hi:
        return "over-scatter"
    if ci[1] < lo:
        return "under-scatter"
    return "INCONCLUSIVE"


def evaluate(records):
    """Statistic and rule on a COMPLETE, plan-ordered list of records."""
    by_arm = {"T": [], "B": []}
    for r in records:
        by_arm[r["spec"]["arm"]].append(np.asarray(r["values"], float))
    XT, XB = np.array(by_arm["T"]), np.array(by_arm["B"])
    if XT.shape[0] != N_T or XB.shape[0] != N_B:
        raise DesignError(f"arm sizes {XT.shape[0]}/{XB.shape[0]}, design {N_T}/{N_B}")
    rho = ratios(XB, XT)
    ci = median_interval(XB, XT)
    return {"M": float(np.median(rho)), "M_ci95": ci, "verdict": classify(ci),
            "rho_p16_p84": [float(np.percentile(rho, 16)), float(np.percentile(rho, 84))],
            "n": {"T": int(XT.shape[0]), "B": int(XB.shape[0]), "bins": int(rho.size)}}
