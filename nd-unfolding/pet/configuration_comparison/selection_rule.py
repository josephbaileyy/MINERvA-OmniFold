"""The configuration selection rule, as code, so it cannot be applied ambiguously.

A decision rule written in prose gets read differently by different people once a number
exists. This module is the rule: it takes adequacy for each arm and a confidence interval
on the paired difference, and returns exactly one verdict from a closed set. Every
combination of inputs maps to a verdict, and the tests enumerate the partition rather
than sampling it.

Two separations are structural rather than editorial.

**Measured performance is computed independently of the verdict.** ``Outcome.measured``
says which arm scored higher, by how much, and whether the difference is resolved --
derived only from the interval, never from the recommendation. So a case where Gregor's
arm measurably wins and we nonetheless keep ours reports both facts, and the second
cannot quietly absorb the first.

**A preference is not a measurement.** When the recommendation is not licensed by
measured performance -- because his advantage is real but smaller than the switching
threshold, or because the interval is unresolved -- ``Outcome.preference`` names the
policy that decided it and ``preference_is_ratified`` is ``False``. The switching
threshold encodes adoption costs, which is a judgement about what we are willing to pay,
not a property of the estimators.

The sign convention is fixed once, here: ``d = recovery(ours) - recovery(theirs)``, so
**negative d favours Gregor**.

**A defect this module had, and the reason ``THEIRS_BETTER_MAGNITUDE_UNRESOLVED``
exists.** An earlier version concluded "his advantage is below the switching threshold"
from ``ci_high < 0`` alone. That is unsound: ``CI = [-0.10, -0.01]`` with
``delta_switch = 0.02`` establishes only that his advantage is *positive*, and is equally
compatible with an advantage of 0.10 -- five times the threshold. Concluding "below the
threshold" there would license retaining the incumbent on a comparison that does not
support it. Establishing a magnitude is **below** a threshold requires the whole interval
to be inside it, which is a statement about ``ci_low``, not ``ci_high``.

The asymmetry with our own arm is deliberate and not the same error. Retaining the
incumbent needs only non-inferiority -- that the deficit is *bounded* -- so
``OURS_NON_INFERIOR`` is a sound conclusion from ``ci_low > -delta`` even when the
interval extends far above zero. Adopting his arm needs a demonstrated magnitude, which
is a strictly stronger requirement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence


class Verdict(str, Enum):
    """The closed set of verdicts. Nothing outside this set can be returned."""

    NEITHER_ADEQUATE = "NEITHER_ADEQUATE"
    ONLY_OURS_ADEQUATE = "ONLY_OURS_ADEQUATE"
    ONLY_THEIRS_ADEQUATE = "ONLY_THEIRS_ADEQUATE"
    OURS_SUPERIOR = "OURS_SUPERIOR"
    OURS_NON_INFERIOR = "OURS_NON_INFERIOR"
    THEIRS_SUPERIOR = "THEIRS_SUPERIOR"
    THEIRS_BETTER_BELOW_SWITCHING_THRESHOLD = "THEIRS_BETTER_BELOW_SWITCHING_THRESHOLD"
    THEIRS_BETTER_MAGNITUDE_UNRESOLVED = "THEIRS_BETTER_MAGNITUDE_UNRESOLVED"
    INCONCLUSIVE = "INCONCLUSIVE"
    REGIONAL_SAFEGUARD_FAILED = "REGIONAL_SAFEGUARD_FAILED"


class Recommendation(str, Enum):
    """What the verdict licenses. ``NO_SELECTION`` is a real outcome, not a failure."""

    ADOPT_OURS = "ADOPT_OURS"
    ADOPT_THEIRS = "ADOPT_THEIRS"
    NO_SELECTION = "NO_SELECTION"


@dataclass(frozen=True)
class Outcome:
    """One verdict, with measured performance and any applied preference kept apart."""

    verdict: Verdict
    recommendation: Recommendation
    measured: dict[str, Any]
    preference: str | None = None
    preference_is_ratified: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def decided_by_measurement(self) -> bool:
        """True when measured performance, not a policy, licensed the recommendation."""
        return self.preference is None


def _measured(ci_low: float, ci_high: float) -> dict[str, Any]:
    """Describe what was measured, independently of what it licenses."""
    point = 0.5 * (ci_low + ci_high)
    resolved = ci_low > 0.0 or ci_high < 0.0
    if not resolved:
        favours = "unresolved"
    elif point > 0.0:
        favours = "ours"
    else:
        favours = "theirs"
    return {
        "difference_convention": "d = recovery(ours) - recovery(theirs)",
        "interval": [ci_low, ci_high],
        "midpoint": point,
        "difference_resolved": resolved,
        "favours": favours,
        "magnitude": abs(point),
    }


def regional_safeguard(
    regional_recovery: Mapping[str, Mapping[str, float]],
    floor: float,
    scoreable_regions: Sequence[str],
) -> dict[str, Any]:
    """Can either arm be recommended at all, given per-REGION recovery?

    The aggregate score is a marginal, and a marginal can pass while a region fails:
    the seven-bin `E_avail` census showed no bin under 0.05 acceptance while the
    underlying `(pT, p-parallel)` cells it averages over span 0.004 to 0.89. So
    regions are defined on those cells, and every SCOREABLE region -- one carrying
    enough injected displacement to measure a recovery at all -- must clear
    ``floor`` for an arm to remain recommendable.

    `regional_recovery` maps arm -> region -> recovery. Missing a scoreable region
    is a failure, not an exemption: an arm that did not report a region cannot be
    shown to have passed it.
    """
    scoreable = list(scoreable_regions)
    if not scoreable:
        raise ValueError(
            "no scoreable region: the injection puts no measurable displacement "
            "anywhere, so the endpoint cannot support a recommendation"
        )
    eligibility: dict[str, Any] = {}
    for arm in ("ours", "theirs"):
        reported = dict(regional_recovery.get(arm, {}))
        missing = [r for r in scoreable if r not in reported]
        failed = [r for r in scoreable if r in reported and reported[r] < floor]
        eligibility[arm] = {
            "eligible": not missing and not failed,
            "regions_below_floor": failed,
            "regions_not_reported": missing,
            "recovery_by_region": reported,
        }
    return {
        "floor": floor,
        "scoreable_regions": scoreable,
        "arms": eligibility,
        "both_ineligible": not (eligibility["ours"]["eligible"]
                                or eligibility["theirs"]["eligible"]),
        "criterion": (
            "every scoreable region must clear the floor. A region defined on the "
            "reporting cells, not on the marginal, and a region not reported counts "
            "as failed."
        ),
    }


def decide(
    *,
    ours_adequate: bool,
    theirs_adequate: bool,
    ci_low: float,
    ci_high: float,
    delta: float,
    delta_switch: float,
    regional: Mapping[str, Any] | None = None,
) -> Outcome:
    """Apply the rule. Exactly one verdict, for every input.

    ``delta`` is the non-inferiority margin and ``delta_switch`` the switching threshold.
    ``delta_switch > delta > 0`` is required: a switching threshold at or below the
    non-inferiority margin would make "ours is acceptable" and "his is worth adopting"
    overlap, and the rule would be ambiguous exactly where it matters.

    ``regional`` is `regional_safeguard`'s output. It is applied BEFORE anything
    else, because it answers a prior question: whether an arm is recommendable at
    all. An arm that fails a region is not made recommendable by winning the
    aggregate comparison -- that is precisely the failure the marginal hides.
    """
    if not (delta > 0.0):
        raise ValueError(f"delta must be positive, got {delta}")
    if not (delta_switch > delta):
        raise ValueError(
            f"delta_switch ({delta_switch}) must exceed delta ({delta}); otherwise "
            "non-inferiority and adoption overlap and the rule is ambiguous"
        )
    if ci_low > ci_high:
        raise ValueError(f"interval is inverted: [{ci_low}, {ci_high}]")

    measured = _measured(ci_low, ci_high)

    # The regional safeguard runs FIRST and can only ever remove eligibility. Its
    # consequence on failure is NO_SELECTION, never "recommend the other arm": one
    # arm failing a region does not establish that the other passed it, and both
    # are checked against the same floor.
    if regional is not None:
        ours_eligible = regional["arms"]["ours"]["eligible"]
        theirs_eligible = regional["arms"]["theirs"]["eligible"]
        if not (ours_eligible and theirs_eligible):
            return Outcome(
                Verdict.REGIONAL_SAFEGUARD_FAILED,
                Recommendation.NO_SELECTION,
                measured,
                preference=None,
                notes=(
                    "the regional safeguard blocks a recommendation: "
                    f"ours {'passed' if ours_eligible else 'FAILED'} "
                    f"{regional['arms']['ours']['regions_below_floor'] or ''}, "
                    f"theirs {'passed' if theirs_eligible else 'FAILED'} "
                    f"{regional['arms']['theirs']['regions_below_floor'] or ''}. "
                    "Regions are defined on the (pT, p-parallel) reporting cells, so "
                    "a failure here is one the aggregate E_avail score cannot see. "
                    "Failing one arm does not license the other: the consequence is "
                    "NO_SELECTION and a report of which regions failed for whom."
                ),
            )

    # Adequacy is asked of each arm alone and dominates the comparison. An inadequate
    # configuration is not made recommendable by scoring well against another one.
    if not ours_adequate and not theirs_adequate:
        return Outcome(
            Verdict.NEITHER_ADEQUATE,
            Recommendation.NO_SELECTION,
            measured,
            notes=(
                "Both arms failed absolute adequacy. The comparison is not reported as a "
                "selection: a difference between two unusable configurations is not a "
                "reason to adopt either.",
            ),
        )
    if ours_adequate and not theirs_adequate:
        return Outcome(
            Verdict.ONLY_OURS_ADEQUATE,
            Recommendation.ADOPT_OURS,
            measured,
            notes=(
                "Licensed by adequacy, NOT by the comparison. Report the measured "
                "difference alongside, and state that his arm was excluded on adequacy "
                "rather than outscored.",
            ),
        )
    if theirs_adequate and not ours_adequate:
        return Outcome(
            Verdict.ONLY_THEIRS_ADEQUATE,
            Recommendation.ADOPT_THEIRS,
            measured,
            notes=(
                "Our arm failed absolute adequacy, so his is the only recommendable "
                "configuration EVEN IF ours scored higher. Switching costs do not apply: "
                "they are a reason to keep an adequate incumbent, not an inadequate one.",
            ),
        )

    # Both adequate. Partition the interval against -delta_switch < -delta < 0 < delta_switch.
    if ci_low > delta_switch:
        return Outcome(
            Verdict.OURS_SUPERIOR,
            Recommendation.ADOPT_OURS,
            measured,
            notes=("Ours is better by more than the switching threshold.",),
        )
    if ci_low > -delta:
        return Outcome(
            Verdict.OURS_NON_INFERIOR,
            Recommendation.ADOPT_OURS,
            measured,
            notes=(
                "Ours is not materially worse: the interval excludes a deficit of delta "
                "or more. If the measured difference favours his arm by less than delta, "
                "say so -- non-inferiority is not superiority.",
            ),
        )
    if ci_high < -delta_switch:
        return Outcome(
            Verdict.THEIRS_SUPERIOR,
            Recommendation.ADOPT_THEIRS,
            measured,
            notes=("His is better by more than the switching threshold. Adopt his.",),
        )
    if ci_high < 0.0 and ci_low <= -delta_switch:
        # His advantage is demonstrated but its SIZE is not resolved against the
        # threshold: the interval spans -delta_switch, so the data is compatible both
        # with an advantage worth switching for and with one that is not.
        return Outcome(
            Verdict.THEIRS_BETTER_MAGNITUDE_UNRESOLVED,
            Recommendation.NO_SELECTION,
            measured,
            preference=None,
            notes=(
                "HIS ARM MEASURABLY WON -- the interval lies entirely below zero. But it "
                "also spans the switching threshold, so whether the advantage is worth "
                "the adoption cost is UNRESOLVED. This licenses neither adopting his arm "
                "(superiority beyond the threshold is not established) nor retaining ours "
                "on the threshold argument (the advantage being below it is not "
                "established either). More seeds would resolve it; asserting either "
                "conclusion here would be claiming a magnitude the interval does not "
                "support.",
            ),
        )
    if ci_high < 0.0:
        return Outcome(
            Verdict.THEIRS_BETTER_BELOW_SWITCHING_THRESHOLD,
            Recommendation.ADOPT_OURS,
            measured,
            preference="RETAIN_INCUMBENT_BELOW_SWITCHING_THRESHOLD",
            preference_is_ratified=False,
            notes=(
                "HIS ARM MEASURABLY WON. The interval lies entirely below zero AND "
                "entirely inside the switching threshold, so the advantage is both "
                "demonstrated and demonstrably smaller than the threshold. The "
                "recommendation to keep ours is therefore a POLICY about adoption cost "
                "and not a performance finding. Report it as 'his scored better by X; we "
                "retain ours for the stated costs'. Never as 'no difference was found'.",
            ),
        )
    return Outcome(
        Verdict.INCONCLUSIVE,
        Recommendation.NO_SELECTION,
        measured,
        preference="RETAIN_INCUMBENT_PENDING_RESOLUTION",
        preference_is_ratified=False,
        notes=(
            "The interval admits both a material deficit for ours and no difference, so "
            "non-inferiority is NOT established. Keeping the incumbent is continuity, "
            "not evidence: label it a provisional engineering choice.",
        ),
    )


def describe(outcome: Outcome) -> str:
    """One paragraph a report can quote, with the separation preserved."""
    m = outcome.measured
    if m["difference_resolved"]:
        performance = (
            f"Measured: the difference is resolved and favours {m['favours']} by "
            f"{m['magnitude']:.4f} recovery points "
            f"(95% interval [{m['interval'][0]:.4f}, {m['interval'][1]:.4f}])."
        )
    else:
        performance = (
            f"Measured: the difference is NOT resolved "
            f"(95% interval [{m['interval'][0]:.4f}, {m['interval'][1]:.4f}] contains zero)."
        )
    lines = [performance, f"Verdict: {outcome.verdict.value}.",
             f"Recommendation: {outcome.recommendation.value}."]
    if outcome.preference is not None:
        lines.append(
            f"This recommendation was decided by an UNRATIFIED policy "
            f"({outcome.preference}), not by measured performance."
        )
    else:
        lines.append("This recommendation is licensed by the measurement.")
    lines.extend(outcome.notes)
    return " ".join(lines)
