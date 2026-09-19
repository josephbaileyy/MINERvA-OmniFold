"""Turn campaign weights into a verdict, over the frozen endpoint.

Scoring is deliberately SEPARATE from training. `run_arm_evaluation` writes
weights and records ``"scored_here": False``: a run that scored itself could be
re-run until it scored well, and the re-run would be invisible. Here the
endpoint, the thresholds, the seeds and the pilot-exclusion rule all come from
`frozen_design`, and this module refuses inputs that disagree with them.

What it will NOT do, each because the frozen design says so:

* score a seed that is not on the frozen list -- an off-list seed is a run
  nobody predeclared;
* include the pilot observations in the final interval -- the pilot chose `n`;
* fall back to a single regional floor -- each region is judged against ITS OWN
  reference, and one scalar would hold regions of different acceptance to
  incomparable standards;
* silently score a partial campaign -- a missing arm-seed is a missing
  observation, not a smaller sample;
* clip overshoot -- a recovery above 1 is a real failure mode.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

import frozen_design as fd
import selection_rule as sr
from run_arm_evaluation import injected_truth_weights, recovery

ARMS = ("ours", "theirs")
CONFIDENCE = fd.INFERENCE["confidence"]
# The pilot's one-sided upper bound on sigma is taken at 80 %, per INFERENCE.
SIGMA_BOUND_LEVEL = 0.80


# --------------------------------------------------------------------------- #
# One run
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Run:
    """One (arm, stage, seed) and the push weights it produced."""
    arm: str
    stage: str
    seed: int
    weights: np.ndarray
    source: str = ""

    def __post_init__(self) -> None:
        if self.arm not in ARMS:
            raise ValueError(f"unknown arm {self.arm!r}; expected one of {ARMS}")
        if self.stage not in fd.SEEDS:
            raise ValueError(f"unknown stage {self.stage!r}")
        if self.seed not in fd.SEEDS[self.stage]:
            raise ValueError(
                f"seed {self.seed} is not on the frozen {self.stage} list "
                f"{fd.SEEDS[self.stage]}; an off-list seed is a run nobody "
                "predeclared, and admitting it here would let the sample be "
                "chosen after the fact"
            )
        w = np.asarray(self.weights, dtype=np.float64)
        if w.ndim != 1:
            raise ValueError(f"weights must be 1-D, got shape {w.shape}")
        if not np.isfinite(w).all():
            raise ValueError(
                f"{self.arm}/{self.stage}/seed{self.seed}: weights contain "
                "non-finite entries. A non-finite weight is a failed run, not a "
                "low score -- it is not scored and not silently dropped"
            )
        if (w < 0).any():
            raise ValueError(f"{self.arm}/{self.stage}/seed{self.seed}: negative weights")


def load_run(weights_path: str | Path) -> Run:
    """Read one weights file, taking arm/stage/seed from the RECEIPT, not the name.

    A filename is a label somebody typed; the receipt is what the run recorded
    about itself. Where both exist they must agree, and a disagreement is an
    error rather than a preference for either.
    """
    path = Path(weights_path)
    with np.load(path) as handle:
        weights = np.asarray(handle["weights"], dtype=np.float64)
    receipt_path = path.parent / "receipt.json"
    if not receipt_path.exists():
        raise FileNotFoundError(
            f"no receipt beside {path}: the arm, stage and seed of a run are "
            "taken from what the run recorded, and a filename cannot stand in"
        )
    receipt = json.loads(receipt_path.read_text())
    arm, stage, seed = receipt["arm"], receipt["stage"], int(receipt["seed"])
    stem = path.stem  # weights_<arm>_<stage>_<seed>
    expected = f"weights_{arm}_{stage}_{seed}"
    if stem != expected:
        raise ValueError(
            f"receipt says {arm}/{stage}/seed{seed} but the file is named {stem!r}; "
            f"expected {expected!r}. One of the two is from a different run"
        )
    return Run(arm=arm, stage=stage, seed=seed, weights=weights, source=str(path))


# --------------------------------------------------------------------------- #
# The endpoint
# --------------------------------------------------------------------------- #
def _histogram(eavail: np.ndarray, weights: np.ndarray,
               edges: Sequence[float]) -> np.ndarray:
    counts, _ = np.histogram(np.asarray(eavail, dtype=np.float64),
                             bins=np.asarray(edges, dtype=np.float64),
                             weights=np.asarray(weights, dtype=np.float64))
    return counts


@dataclass(frozen=True)
class Endpoint:
    """The frozen seven-bin `E_avail` closure, and the regions it is cut into.

    ``region_of_event`` labels each truth event with the region of its
    ``(pT, p_parallel)`` reporting cell. It is REQUIRED: deriving regions here by
    stratifying the marginal bins would be exactly the mistake the frozen design
    names -- a region is a set of cells, not a slice of the reported histogram.
    """
    truth_eavail: np.ndarray
    region_of_event: np.ndarray
    edges: tuple[float, ...] = tuple(fd.ENDPOINT["bin_edges_gev"])
    amplitude: float = fd.ENDPOINT["amplitude"]
    clip: float = fd.ENDPOINT["clip"]
    base_weights: np.ndarray | None = None

    def __post_init__(self) -> None:
        e = np.asarray(self.truth_eavail, dtype=np.float64)
        r = np.asarray(self.region_of_event)
        if e.shape != r.shape:
            raise ValueError(
                f"truth_eavail {e.shape} and region_of_event {r.shape} disagree; "
                "every truth event must carry a region or the regional safeguard "
                "would be computed over a different population than the aggregate"
            )
        if not np.isfinite(e).all():
            raise ValueError("truth E_avail contains non-finite entries")
        import characterize_regions as cr
        known = {name for name, _lo, _hi in _safeguard_regions()} | {cr.UNASSIGNED}
        unknown = sorted(set(np.unique(r).tolist()) - known)
        if unknown:
            raise ValueError(
                f"region labels {unknown} are not frozen regions {sorted(known)}"
            )

    @property
    def unassigned_fraction(self) -> float:
        """Share of truth events whose `(pT, p_parallel)` falls off the reporting grid.

        These events are in the AGGREGATE score -- they carry `E_avail` like any
        other -- but they belong to no cell and so to no region. The regional
        safeguard therefore covers less than the whole measurement, and by how
        much is reported rather than left implicit. Assigning them to the nearest
        edge cell would move mass into a region that never held it.
        """
        return float(np.mean(np.asarray(self.region_of_event) == _unassigned()))

    @property
    def n_events(self) -> int:
        return int(np.asarray(self.truth_eavail).size)

    def prior(self) -> np.ndarray:
        base = (np.ones(self.n_events) if self.base_weights is None
                else np.asarray(self.base_weights, dtype=np.float64))
        return base

    def target(self) -> np.ndarray:
        return self.prior() * injected_truth_weights(
            self.truth_eavail, self.amplitude, self.clip)


def _unassigned() -> str:
    import characterize_regions as cr
    return cr.UNASSIGNED


def _safeguard_regions() -> tuple[tuple[str, float, float], ...]:
    import characterize_regions as cr
    return tuple(cr.SAFEGUARD_REGIONS)


def overshoot_projection(prior: np.ndarray, unfolded: np.ndarray,
                         target: np.ndarray) -> float:
    """How far along the injected direction the estimator travelled, as a multiple.

    The L1 recovery cannot distinguish stopping short from going too far: both
    leave the estimate away from the target and both score below 1. This is the
    signed projection of the achieved displacement onto the injected one, so
    ``< 1`` is undershoot, ``> 1`` is overshoot and ``< 0`` is the wrong
    direction. It is reported beside the score rather than folded into it.
    """
    prior, unfolded, target = (np.asarray(a, float) / np.asarray(a, float).sum()
                               for a in (prior, unfolded, target))
    injected = target - prior
    denom = float(injected @ injected)
    if denom <= 0:
        raise ValueError("the injection displaces nothing; projection undefined")
    return float(((unfolded - prior) @ injected) / denom)


def score_run(run: Run, endpoint: Endpoint, *,
              scoreable_regions: Sequence[str]) -> dict[str, Any]:
    """Aggregate and per-region recovery for one run, over the frozen bins."""
    if run.weights.size != endpoint.n_events:
        raise ValueError(
            f"{run.arm}/{run.stage}/seed{run.seed}: {run.weights.size} weights "
            f"against {endpoint.n_events} truth events. A length mismatch means "
            "the weights and the endpoint are over different event sets, and "
            "scoring them together would compare unlike populations"
        )
    prior, target = endpoint.prior(), endpoint.target()
    edges = endpoint.edges
    h_prior = _histogram(endpoint.truth_eavail, prior, edges)
    h_unfolded = _histogram(endpoint.truth_eavail, prior * run.weights, edges)
    h_target = _histogram(endpoint.truth_eavail, target, edges)
    aggregate = recovery(h_prior, h_unfolded, h_target)
    projection = overshoot_projection(h_prior, h_unfolded, h_target)
    by_region: dict[str, float] = {}
    region_detail: dict[str, Any] = {}
    labels = np.asarray(endpoint.region_of_event)
    for name in scoreable_regions:
        inside = labels == name
        if not inside.any():
            raise ValueError(
                f"region {name!r} was declared scoreable but holds no event"
            )
        scored = recovery(
            _histogram(endpoint.truth_eavail[inside], prior[inside], edges),
            _histogram(endpoint.truth_eavail[inside],
                       (prior * run.weights)[inside], edges),
            _histogram(endpoint.truth_eavail[inside], target[inside], edges))
        by_region[name] = scored["recovery"]
        region_detail[name] = scored
    return {
        "arm": run.arm, "stage": run.stage, "seed": run.seed,
        "source": run.source,
        "recovery": aggregate["recovery"],
        "aggregate": aggregate,
        "recovery_by_region": by_region,
        "region_detail": region_detail,
        "unassigned_fraction": endpoint.unassigned_fraction,
        "overshoot_projection": projection,
        "overshoot": projection > 1.0,
        "wrong_direction": projection < 0.0,
        "worse_than_doing_nothing": aggregate["recovery"] < 0.0,
    }


# --------------------------------------------------------------------------- #
# Pairing and the interval
# --------------------------------------------------------------------------- #
def paired_differences(scores: Sequence[Mapping[str, Any]], stage: str,
                       ) -> dict[int, float]:
    """`d = recovery(ours) - recovery(theirs)`, per seed, for one stage.

    A seed with only one arm present is an error. It is the same event sample run
    two ways; half a pair is not an observation of the difference, and dropping
    it quietly would shrink `n` without saying so.
    """
    wanted = list(fd.SEEDS[stage])
    table: dict[int, dict[str, float]] = {}
    for row in scores:
        if row["stage"] != stage:
            continue
        table.setdefault(int(row["seed"]), {})[row["arm"]] = float(row["recovery"])
    incomplete = {seed: sorted(arms) for seed, arms in table.items()
                  if set(arms) != set(ARMS)}
    if incomplete:
        raise ValueError(
            f"{stage}: seeds with only one arm scored: {incomplete}. Half a pair "
            "is not an observation of the paired difference"
        )
    missing = [s for s in wanted if s not in table]
    if missing:
        raise ValueError(
            f"{stage}: no scored pair for seeds {missing} of the frozen list "
            f"{wanted}. A missing pair is a missing observation, not a smaller "
            "planned sample; score them or declare the campaign short"
        )
    extra = sorted(set(table) - set(wanted))
    if extra:
        raise ValueError(f"{stage}: scored seeds {extra} are not on the frozen list")
    return {seed: table[seed]["ours"] - table[seed]["theirs"] for seed in wanted}


def _t_quantile(p: float, df: int) -> float:
    """Two-sided t quantile without SciPy, by bisecting the Student-t CDF."""
    if df < 1:
        raise ValueError(f"t quantile needs df >= 1, got {df}")

    def cdf(t: float) -> float:
        x = df / (df + t * t)
        ib = _betainc_half(0.5 * df, x)
        return 1.0 - 0.5 * ib if t > 0 else 0.5 * ib

    lo, hi = 0.0, 1000.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _betainc_half(a: float, x: float) -> float:
    """Regularised incomplete beta `I_x(a, 1/2)`, by continued fraction."""
    b = 0.5
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = (math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b))
    front = math.exp(a * math.log(x) + b * math.log(1.0 - x) - lbeta)
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _bcf(a, b, x) / a
    return 1.0 - math.exp(b * math.log(1.0 - x) + a * math.log(x) - lbeta) \
        * _bcf(b, a, 1.0 - x) / b


def _bcf(a: float, b: float, x: float, iterations: int = 300) -> float:
    """Continued fraction for the incomplete beta, by the modified Lentz method.

    Written out as the two-term-per-iteration recurrence rather than a generic
    even/odd loop. The generic form got the FIRST term wrong -- it applied the
    `c` update to the initial step, where the recurrence starts at `h = d` -- and
    the resulting t quantiles came out too WIDE (25.44 against 12.706 at one
    degree of freedom). A too-wide interval looks conservative, so nothing about
    the shape of the answer would have flagged it; the published table did.
    """
    tiny = 1e-30
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    d = tiny if abs(d) < tiny else d
    d = 1.0 / d
    h = d
    for m in range(1, iterations + 1):
        m2 = 2 * m
        num = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + num * d
        d = tiny if abs(d) < tiny else d
        c = 1.0 + num / c
        c = tiny if abs(c) < tiny else c
        d = 1.0 / d
        h *= d * c
        num = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + num * d
        d = tiny if abs(d) < tiny else d
        c = 1.0 + num / c
        c = tiny if abs(c) < tiny else c
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-14:
            break
    return h


def t_interval(differences: Sequence[float], confidence: float = CONFIDENCE,
               ) -> dict[str, Any]:
    """Two-sided paired t interval, `n-1` df, as frozen in INFERENCE."""
    d = np.asarray(list(differences), dtype=np.float64)
    n = d.size
    if n < 2:
        raise ValueError(
            f"a t interval needs at least two pairs, got {n}; with one pair the "
            "spread is unmeasured and any interval would be invented"
        )
    mean = float(d.mean())
    sd = float(d.std(ddof=1))
    tq = _t_quantile(0.5 * (1.0 + confidence), n - 1)
    half = tq * sd / math.sqrt(n)
    return {
        "n_pairs": int(n), "mean": mean, "sd": sd, "df": int(n - 1),
        "t_quantile": tq, "half_width": float(half),
        "ci_low": float(mean - half), "ci_high": float(mean + half),
        "confidence": confidence,
        "statistic": fd.INFERENCE["statistic"],
    }


def _chi2_quantile(p: float, df: int) -> float:
    """Chi-square quantile by bisection on the regularised lower gamma."""
    lo, hi = 0.0, max(10.0 * df, 100.0)
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if _gammainc_lower(0.5 * df, 0.5 * mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _gammainc_lower(a: float, x: float) -> float:
    if x <= 0.0:
        return 0.0
    if x < a + 1.0:
        term = 1.0 / a
        total = term
        n = a
        for _ in range(1000):
            n += 1.0
            term *= x / n
            total += term
            if abs(term) < abs(total) * 1e-15:
                break
        return total * math.exp(-x + a * math.log(x) - math.lgamma(a))
    tiny = 1e-300
    b = x + 1.0 - a
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        d = tiny if abs(d) < tiny else d
        c = b + an / c
        c = tiny if abs(c) < tiny else c
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    return 1.0 - math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def size_from_pilot(pilot_differences: Sequence[float], *,
                    delta: float = fd.THRESHOLDS["non_inferiority_delta"],
                    confidence: float = CONFIDENCE,
                    bound_level: float = SIGMA_BOUND_LEVEL,
                    max_n: int = 512) -> dict[str, Any]:
    """Smallest `n` whose half-width fits `delta`, at the pilot's UPPER sigma bound.

    The pilot's own `sigma_hat` is an estimate from a handful of pairs and is as
    likely low as high; sizing on it would under-power the final half the time.
    The one-sided upper bound at ``bound_level`` is used instead, which is the
    frozen procedure, and it is the frozen procedure that is used -- not a
    procedure chosen after seeing the pilot.
    """
    d = np.asarray(list(pilot_differences), dtype=np.float64)
    if d.size < 2:
        raise ValueError(f"sizing needs at least two pilot pairs, got {d.size}")
    df = d.size - 1
    sigma_hat = float(d.std(ddof=1))
    chi2_low = _chi2_quantile(1.0 - bound_level, df)
    sigma_upper = sigma_hat * math.sqrt(df / chi2_low) if chi2_low > 0 else math.inf
    required = None
    for n in range(2, max_n + 1):
        half = _t_quantile(0.5 * (1.0 + confidence), n - 1) * sigma_upper / math.sqrt(n)
        if half <= delta:
            required = n
            break
    return {
        "pilot_pairs": int(d.size),
        "sigma_hat": sigma_hat,
        "sigma_upper_bound": float(sigma_upper),
        "bound_level": bound_level,
        "delta": delta,
        "required_n": required,
        "capped_at": max_n,
        "feasible": required is not None,
        "procedure": fd.INFERENCE["sizing"],
        "note": (
            "n is the number of PAIRS in the final stage. The pilot pairs are not "
            "among them: " + fd.INFERENCE["pilot_exclusion_reason"]
        ),
    }


# --------------------------------------------------------------------------- #
# The whole campaign
# --------------------------------------------------------------------------- #
def adequacy(scores: Sequence[Mapping[str, Any]], stage: str, *,
             reference: float,
             fraction: float = fd.THRESHOLDS["adequacy_fraction_of_reference"],
             ) -> dict[str, Any]:
    """Absolute adequacy, asked of EACH arm against the applicable reference.

    Per the frozen rule an arm failing this is ineligible, and one arm's failure
    says nothing about the other: if exactly one passes, the other's failure does
    not disqualify it.
    """
    floor = fraction * reference
    out: dict[str, Any] = {"reference": reference, "fraction": fraction,
                           "floor": floor, "arms": {}}
    for arm in ARMS:
        values = [float(r["recovery"]) for r in scores
                  if r["stage"] == stage and r["arm"] == arm]
        if not values:
            raise ValueError(f"no {stage} score for arm {arm!r}")
        mean = float(np.mean(values))
        out["arms"][arm] = {
            "mean_recovery": mean, "n": len(values),
            "adequate": bool(mean >= floor),
            "per_seed": values,
        }
    return out


def score_campaign(scores: Sequence[Mapping[str, Any]], *,
                   reference: float,
                   regional_reference: Mapping[str, float | None],
                   scoreable_regions: Sequence[str],
                   region_census: Mapping[str, Any] | None = None,
                   pilot_scores: Sequence[Mapping[str, Any]] | None = None,
                   ) -> dict[str, Any]:
    """Assemble the final stage into one verdict, with the pilot kept out of it."""
    final = [r for r in scores if r["stage"] == "final"]
    if not final:
        raise ValueError("no final-stage scores; there is nothing to decide")
    contaminating = [r for r in scores if r["stage"] == "pilot"]
    if contaminating:
        raise ValueError(
            f"{len(contaminating)} pilot rows were passed as campaign scores. "
            + fd.INFERENCE["pilot_exclusion_reason"]
            + ". Pass them as `pilot_scores`, which are reported and not pooled"
        )

    diffs = paired_differences(final, "final")
    interval = t_interval(list(diffs.values()))
    abs_adequacy = adequacy(final, "final", reference=reference)

    floors: dict[str, float] = {}
    unusable = []
    for name in scoreable_regions:
        ref = regional_reference.get(name)
        if ref is None:
            unusable.append(name)
            continue
        floors[name] = fd.THRESHOLDS["regional_fraction_of_regional_reference"] * ref
    if unusable:
        raise ValueError(
            f"regions {unusable} are scoreable but have no regional reference; a "
            "region without its own reference cannot be judged, and substituting "
            "the global one would hold it to a standard built from other cells"
        )

    mean_by_region = {
        arm: {name: float(np.mean([r["recovery_by_region"][name] for r in final
                                   if r["arm"] == arm]))
              for name in scoreable_regions}
        for arm in ARMS}
    regional = sr.regional_safeguard(mean_by_region, floors, scoreable_regions)

    outcome = sr.decide(
        ours_adequate=abs_adequacy["arms"]["ours"]["adequate"],
        theirs_adequate=abs_adequacy["arms"]["theirs"]["adequate"],
        ci_low=interval["ci_low"], ci_high=interval["ci_high"],
        delta=fd.THRESHOLDS["non_inferiority_delta"],
        delta_switch=fd.THRESHOLDS["switching_delta"],
        regional=regional)

    theirs_better = interval["mean"] < 0.0
    # "His arm scored better and we kept ours" is ADOPT_OURS reached while the
    # measured difference favours him -- the switching policy's own outcome. It
    # is flagged so it cannot be read as a win.
    retained_though_behind = bool(
        theirs_better and outcome.recommendation == sr.Recommendation.ADOPT_OURS)

    report = {
        "endpoint": dict(fd.ENDPOINT),
        "thresholds": dict(fd.THRESHOLDS),
        "paired_differences": diffs,
        "interval": interval,
        "absolute_adequacy": abs_adequacy,
        "regional_safeguard": regional,
        "mean_recovery_by_region": mean_by_region,
        "verdict": outcome.verdict.value,
        "recommendation": outcome.recommendation.value,
        "narrative": sr.describe(outcome),
        "theirs_scored_better": theirs_better,
        "retained_ours_though_theirs_scored_better": retained_though_behind,
        "non_inferiority_is_not_superiority": (
            fd.THRESHOLDS["report_when_theirs_better_but_retained"]
            if retained_though_behind else None),
        "pilot_excluded": True,
        "pilot_exclusion_reason": fd.INFERENCE["pilot_exclusion_reason"],
        "pilot_reported_separately": (
            None if pilot_scores is None
            else {"n_rows": len(list(pilot_scores)),
                  "sizing": size_from_pilot(
                      list(paired_differences(list(pilot_scores), "pilot").values()))}),
        "region_census": dict(region_census) if region_census is not None else None,
        "regional_coverage": _coverage(final),
        "low_acceptance": _low_acceptance_report(final, region_census),
        "scope": dict(fd.STEP_SCOPE),
    }
    return report


def _coverage(final: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """What fraction of the measurement the regional safeguard actually covered."""
    shares = [r["unassigned_fraction"] for r in final
              if r.get("unassigned_fraction") is not None]
    return {
        "off_grid_truth_fraction": (float(np.mean(shares)) if shares else None),
        "reading": (
            "events whose (pT, p_parallel) falls outside the reporting grid are in "
            "the aggregate score but in no region, so the safeguard covers the "
            "complement of this fraction. Reported because a safeguard's coverage "
            "is part of what it certifies"
        ),
    }


def _low_acceptance_report(final: Sequence[Mapping[str, Any]],
                           census: Mapping[str, Any] | None) -> dict[str, Any]:
    """The low-acceptance band, reported separately and never as a write-off."""
    name = "low_acceptance"
    present = [r for r in final if name in r.get("recovery_by_region", {})]
    row = None
    if census is not None:
        row = next((c for c in census.get("regions", []) if c["region"] == name), None)
    return {
        "region": name,
        "retained": True,
        "truth_mass_fraction": None if row is None else row["truth_mass_fraction"],
        "injected_displacement_share": None if row is None
        else row["injected_displacement_share"],
        "scoreable": None if row is None else row["scoreable"],
        "mean_recovery_by_arm": {
            arm: (float(np.mean([r["recovery_by_region"][name]
                                 for r in present if r["arm"] == arm]))
                  if any(r["arm"] == arm for r in present) else None)
            for arm in ARMS},
        "reading": (
            "These events are retained and reported. The acceptance reference is "
            "not an impossibility bound, and this band is not called fundamentally "
            "unresolvable. Any recommendation states its limits here"
        ),
    }
