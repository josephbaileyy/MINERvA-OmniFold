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
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Verdict(str, Enum):
    """The closed set of verdicts. Nothing outside this set can be returned."""

    NEITHER_ADEQUATE = "NEITHER_ADEQUATE"
    ONLY_OURS_ADEQUATE = "ONLY_OURS_ADEQUATE"
    ONLY_THEIRS_ADEQUATE = "ONLY_THEIRS_ADEQUATE"
    OURS_SUPERIOR = "OURS_SUPERIOR"
    OURS_NON_INFERIOR = "OURS_NON_INFERIOR"
    THEIRS_SUPERIOR = "THEIRS_SUPERIOR"
    THEIRS_BETTER_BELOW_SWITCHING_THRESHOLD = "THEIRS_BETTER_BELOW_SWITCHING_THRESHOLD"
    INCONCLUSIVE = "INCONCLUSIVE"


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


def decide(
    *,
    ours_adequate: bool,
    theirs_adequate: bool,
    ci_low: float,
    ci_high: float,
    delta: float,
    delta_switch: float,
) -> Outcome:
    """Apply the rule. Exactly one verdict, for every input.

    ``delta`` is the non-inferiority margin and ``delta_switch`` the switching threshold.
    ``delta_switch > delta > 0`` is required: a switching threshold at or below the
    non-inferiority margin would make "ours is acceptable" and "his is worth adopting"
    overlap, and the rule would be ambiguous exactly where it matters.
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
    if ci_high < 0.0:
        return Outcome(
            Verdict.THEIRS_BETTER_BELOW_SWITCHING_THRESHOLD,
            Recommendation.ADOPT_OURS,
            measured,
            preference="RETAIN_INCUMBENT_BELOW_SWITCHING_THRESHOLD",
            preference_is_ratified=False,
            notes=(
                "HIS ARM MEASURABLY WON. The interval lies entirely below zero, so the "
                "advantage is demonstrated, but it is smaller than the switching "
                "threshold. The recommendation to keep ours is therefore a POLICY about "
                "adoption cost and not a performance finding. Report it as 'his scored "
                "better by X; we retain ours for the stated costs'. Never as 'no "
                "difference was found'.",
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
