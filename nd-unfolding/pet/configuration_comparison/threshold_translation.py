"""Turn recovery thresholds into the residual shape error they permit.

A threshold expressed as "recovery >= 0.8 of the reference" is not a scientific
statement until someone says what it lets through. This converts every candidate
threshold into the quantity a physicist can weigh: **how much of the truth mass
ends up in the wrong bin.**

THE ARITHMETIC, and why each step is what it is.

The closure injects a tilt, moving the normalised truth density from `prior` to
`target`. The L1 displacement is ``D = sum_b |target_b - prior_b|``, measured
**0.2733** on the candidate `E_avail` endpoint. L1 between two normalised
densities is twice the total variation, so the injection displaces
``D / 2 = 13.66 %`` of the truth mass -- that is the fraction of probability
that has to move from one bin to another to turn the prior into the target.

Recovery ``R`` is the fraction of ``D`` the estimator recovers. What it fails to
recover stays as residual shape error, ``(1 - R) * D`` in L1, hence
``(1 - R) * D / 2`` as a fraction of truth mass in the wrong bin. A margin
``delta`` in recovery therefore permits ``delta * D / 2`` **additional** misplaced
mass, and that is the number a threshold is really choosing.

Two consequences worth stating because they are easy to get backwards.

* The translation is **linear in D**, so it is a property of the injection, not of
  the estimator. Change the injected variable or the amplitude and every threshold
  means something different in physics even though the number is unchanged. This
  is the same reason the pT reference could not be inherited.
* The reference value is **calculated, not chosen**. ``ceiling(k=3)`` on this
  endpoint is 0.7131 under the displacement weighting the L1 statistic implies.
  It is a reference model and not a proven bound -- BEN-038 measured a response
  above it -- so "80 % of the reference" is 80 % of a modelled quantity, and the
  residual figure below is the honest way to read it.

NOT CITABLE FOR any ratified threshold. Every value here is a proposal.
"""

from __future__ import annotations

from typing import Any

# Measured on the candidate endpoint, receipts/eavail-endpoint.json.
INJECTED_L1_DISPLACEMENT = 0.2733
REFERENCE_RECOVERY_K3 = 0.7131          # displacement-weighted, the L1 statistic's weight
REFERENCE_TRUTH_MASS_WEIGHTED = 0.7552  # reported for contrast; NOT the one to use


def injected_truth_mass_fraction(displacement: float = INJECTED_L1_DISPLACEMENT) -> float:
    """Fraction of truth mass the injection moves: ``D / 2`` (L1 is twice TV)."""
    if not 0.0 <= displacement <= 2.0:
        raise ValueError(f"an L1 displacement between normalised densities is in "
                         f"[0, 2]; got {displacement}")
    return displacement / 2.0


def residual_truth_mass_fraction(recovery: float,
                                 displacement: float = INJECTED_L1_DISPLACEMENT) -> float:
    """Truth mass left in the wrong bin at a given recovery."""
    if recovery > 1.0:
        # Recovery above 1 is possible -- the reference is not a bound -- but it
        # does not make the residual negative in any meaningful sense.
        recovery = 1.0
    return (1.0 - recovery) * injected_truth_mass_fraction(displacement)


def margin_cost(margin: float, displacement: float = INJECTED_L1_DISPLACEMENT) -> float:
    """Additional misplaced truth mass a recovery margin permits."""
    if margin < 0.0:
        raise ValueError(f"a margin must be non-negative; got {margin}")
    return margin * injected_truth_mass_fraction(displacement)


def adequacy_floor(fraction_of_reference: float,
                   reference: float = REFERENCE_RECOVERY_K3) -> float:
    """The recovery an arm must reach to be adequate on its own."""
    if not 0.0 < fraction_of_reference <= 1.0:
        raise ValueError(f"fraction must be in (0, 1]; got {fraction_of_reference}")
    return fraction_of_reference * reference


def describe_policy(fraction_of_reference: float, delta: float, delta_switch: float,
                    regional_fraction: float,
                    displacement: float = INJECTED_L1_DISPLACEMENT,
                    reference: float = REFERENCE_RECOVERY_K3) -> dict[str, Any]:
    """One policy, with every threshold translated into misplaced truth mass."""
    if not delta_switch > delta > 0.0:
        raise ValueError(
            f"need delta_switch ({delta_switch}) > delta ({delta}) > 0, or "
            "non-inferiority and adoption overlap"
        )
    if not 0.0 < regional_fraction <= fraction_of_reference:
        raise ValueError(
            "the regional fraction must be positive and no stricter than the global "
            "one: a region is a smaller sample and holding it to a tighter standard "
            "would block on noise"
        )
    floor = adequacy_floor(fraction_of_reference, reference)
    return {
        "injection": {
            "l1_displacement": displacement,
            "truth_mass_moved": injected_truth_mass_fraction(displacement),
        },
        "reference": {
            "recovery_k3": reference,
            "residual_truth_mass_at_the_reference": residual_truth_mass_fraction(
                reference, displacement),
            "status": "CALCULATED, not for approval; a reference model, not a bound",
        },
        "adequacy": {
            "fraction_of_reference": fraction_of_reference,
            "recovery_floor": floor,
            "residual_truth_mass_permitted": residual_truth_mass_fraction(floor, displacement),
            "extra_over_the_reference": (
                residual_truth_mass_fraction(floor, displacement)
                - residual_truth_mass_fraction(reference, displacement)
            ),
        },
        "non_inferiority": {
            "delta": delta,
            "additional_misplaced_truth_mass": margin_cost(delta, displacement),
        },
        "switching": {
            "delta_switch": delta_switch,
            "additional_misplaced_truth_mass": margin_cost(delta_switch, displacement),
        },
        "regional": {
            "fraction_of_regional_reference": regional_fraction,
            "note": ("applied to each scoreable region against THAT region's own "
                     "reference, because regions differ in acceptance and a single "
                     "absolute floor would be a different standard in each"),
        },
    }
