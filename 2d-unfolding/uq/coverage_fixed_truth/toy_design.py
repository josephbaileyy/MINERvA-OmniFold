"""Pure (ROOT-free) pieces of the fixed-truth 2D coverage toy design.

The design is pre-registered in
``docs/orchestration/PREREG-20261005-2d-fixed-truth-coverage.md``. One toy is

* pseudo-data: every closure MC event ``i`` (``pass_reco & pass_truth``) enters the
  measured sample ``k_i ~ Poisson(w_reco_i)`` times, where ``w_reco`` is already
  POT-scaled to the data exposure. The pseudo-data therefore has data-sized Poisson
  statistics and expectation equal to the MC reco distribution;
* MC: the production bootstrap's MC stream, one ``b_i ~ Poisson(1)`` per signal
  event multiplying both ``w_truth`` and ``w_reco``;
* truth: the unfluctuated MC truth marginal, the same in every toy.

``k`` and ``b`` come from two independent generators seeded from a namespace that
cannot meet the production replicas (data 1..300, MC 10_000_001..10_000_300) or the
superseded closure+bootstrap toys (1001..1200, 10_001_001..10_001_200).
"""

import numpy as np

DATA_SEED_BASE = 20_261_005_000_000
MC_SEED_BASE = 20_261_005_500_000
MAX_TOY_INDEX = 99_999

PRODUCTION_DATA_SEEDS = range(1, 301)
PRODUCTION_MC_SEEDS = range(10_000_001, 10_000_301)
OLD_TOY_DATA_SEEDS = range(1001, 1201)
OLD_TOY_MC_SEEDS = range(10_001_001, 10_001_201)


# KNOWN_ISSUES 85 diagnostic (2026-10-06): data-only bootstrap replicas of one toy's pseudo-data.
BOOT_SEED_BASE = 20_261_006_000_000
MAX_BOOT_INDEX = 9_999


def toy_seeds(toy_index):
    """Return ``(data_seed, mc_seed)`` for a toy index in ``1..MAX_TOY_INDEX``."""
    t = int(toy_index)
    if not 1 <= t <= MAX_TOY_INDEX:
        raise ValueError(f"toy index must be in 1..{MAX_TOY_INDEX}, got {toy_index!r}")
    return DATA_SEED_BASE + t, MC_SEED_BASE + t


def draw_pseudo_data_counts(w_reco_closure, data_seed):
    """Per-event Poisson counts ``k_i ~ Poisson(w_reco_i)`` for the closure events."""
    w = np.asarray(w_reco_closure, dtype=float)
    if w.ndim != 1:
        raise ValueError("w_reco_closure must be one-dimensional")
    if not np.all(np.isfinite(w)) or np.any(w < 0):
        raise ValueError("pseudo-data Poisson means must be finite and non-negative")
    return np.random.default_rng(data_seed).poisson(w).astype(float)


def draw_mc_bootstrap(n_events, mc_seed):
    """Production MC-stream multipliers ``b_i ~ Poisson(1)``."""
    return np.random.default_rng(mc_seed).poisson(1.0, size=int(n_events)).astype(float)


def compress_pseudo_data(reco_pt, reco_pz, counts):
    """Drop zero-count events; keep one row per selected event with weight ``k_i``.

    A row of weight ``k`` is the same training input as ``k`` unit rows for a
    weighted classifier, and it mirrors production, where the measured sample has
    one row per data event carrying its bootstrap multiplicity.
    """
    keep = np.asarray(counts) > 0
    return (np.asarray(reco_pt)[keep], np.asarray(reco_pz)[keep],
            np.asarray(counts, dtype=float)[keep])


def bootstrap_seed(boot_index):
    """Seed of data-only bootstrap replica ``boot_index`` in ``1..MAX_BOOT_INDEX``."""
    b = int(boot_index)
    if not 1 <= b <= MAX_BOOT_INDEX:
        raise ValueError(f"bootstrap index must be in 1..{MAX_BOOT_INDEX}, got {boot_index!r}")
    return BOOT_SEED_BASE + b


def draw_data_bootstrap(counts, boot_seed):
    """Per-event Poisson(1) bootstrap of pseudo-data held as per-event counts.

    An event selected ``k`` times stands for ``k`` measured events, and the production
    data bootstrap gives each measured event its own ``Poisson(1)`` multiplicity, so
    the event's resampled count is their sum, ``Poisson(k)``, not ``k * Poisson(1)``.
    """
    k = np.asarray(counts, dtype=float)
    if not np.all(np.isfinite(k)) or np.any(k < 0) or np.any(k != np.round(k)):
        raise ValueError("pseudo-data counts must be finite non-negative integers")
    return np.random.default_rng(boot_seed).poisson(k).astype(float)
