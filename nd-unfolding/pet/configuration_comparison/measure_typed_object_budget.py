"""Compare token budgets: our calorimeter-cluster cloud against a typed-object cloud.

Both projects cap the number of tokens per event, but they cap *different objects*.
Ours caps non-muon calorimeter clusters at 12; Gregor's caps reconstructed objects
(muon, photons, blobs, prongs) at 33. The interesting quantity is not the cap but
how often each cap binds, and that is decided by the multiplicity of the thing being
capped -- which the A1 source characterization already measured on the same tuple
entries for both vocabularies.

This script re-reads that frozen receipt and derives the comparison. It introduces
no new source read.

The one subtlety it refuses to paper over: the receipt records *marginal* histograms
per family, not the joint distribution of (photons, blobs, prongs). A typed cap binds
on the total, so the exact binding fraction is not recoverable from marginals. What is
recoverable is a bracket, and a bracket is what gets reported:

    lower bound  P(blobs >= cap)                         -- blobs alone overflow
    upper bound  P(blobs >= cap - 1 - max_photons - max_prongs)

using each file's own observed family maxima. Reporting the midpoint, or quietly
reporting the lower bound as "the" answer, would turn an interval into a number the
data cannot support.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

OUR_CAP = 12
TYPED_CAP = 33  # src/scripts/train.py --max_particles default, pinned commit fc9a099


def _tail_fraction(histogram: dict[str, int], threshold: int) -> float:
    """Fraction of events with a count at or above ``threshold``."""
    counts = {int(k): v for k, v in histogram.items()}
    total = sum(counts.values())
    if total == 0:
        raise ValueError("Empty histogram")
    return sum(v for k, v in counts.items() if k >= threshold) / total


def typed_bracket(source: dict[str, Any], cap: int) -> dict[str, Any]:
    """Bracket how often a typed-object cap binds, from marginal histograms."""
    blobs = source["blobs"]
    max_photons = int(source["photons"]["max"])
    max_prongs = int(source["prongs"]["max"])
    # One muon token at most: the production selection keeps a MINOS-matched muon.
    headroom = 1 + max_photons + max_prongs
    lower = _tail_fraction(blobs["histogram"], cap)
    upper = _tail_fraction(blobs["histogram"], max(1, cap - headroom))
    return {
        "cap": cap,
        "binds_at_least": lower,
        "binds_at_most": upper,
        "derivation": (
            f"lower = P(blobs >= {cap}); upper = P(blobs >= {cap - headroom}) using this "
            f"file's observed maxima (photons {max_photons}, prongs {max_prongs}) plus one "
            "muon. The joint multiplicity is not in the receipt, so only a bracket is "
            "derivable."
        ),
    }


def main() -> None:
    """Derive the token-budget comparison from the frozen A1 receipt."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    receipt = json.loads(args.source_receipt.read_text())
    if int(receipt["cap"]) != OUR_CAP:
        raise ValueError(f"Source receipt caps at {receipt['cap']}, expected {OUR_CAP}")

    rows = []
    for source in receipt["sources"]:
        clusters = source["generic_clusters_nonmuon"]
        rows.append({
            "role": source["role"],
            "playlist": source["playlist"],
            "entries_read": source["entries_read"],
            "cluster_cloud": {
                "cap": OUR_CAP,
                "median_objects": clusters["median"],
                "mean_objects": clusters["mean"],
                "max_objects": clusters["max"],
                "binds": clusters["fraction_above_cap"],
                "discarded_energy_share_median": source["tail_energy_share_beyond_cap"]["median"],
            },
            "typed_objects": {
                # Per-family medians, NOT summed: a sum of medians is not the median
                # of the sum, and the joint distribution is not in the receipt.
                "median_by_family": {
                    "blobs": source["blobs"]["median"],
                    "prongs": source["prongs"]["median"],
                    "photons": source["photons"]["median"],
                },
                "mean_objects": (
                    source["blobs"]["mean"] + source["prongs"]["mean"]
                    + source["photons"]["mean"] + 1.0
                ),
                "max_blobs": source["blobs"]["max"],
                **typed_bracket(source, TYPED_CAP),
            },
        })

    output = {
        "scope": (
            "how often each project's token cap binds, on the same tuple entries. "
            "Derived from the frozen A1 source receipt; no new source read."
        ),
        "source_receipt_sha256": __import__("hashlib").sha256(
            args.source_receipt.read_bytes()
        ).hexdigest(),
        "our_cap": OUR_CAP,
        "typed_cap": TYPED_CAP,
        "rows": rows,
        "qualifications": [
            "These are UNSELECTED tuple entries, one file per role, unweighted. The "
            "production selection and POT weighting are not applied, so these fractions "
            "do not determine the selected-population behaviour.",
            "A lower token count is not equivalent information. Whether reconstructed "
            "objects preserve what the raw cluster cloud carries is NOT measured here "
            "and is the prerequisite for any adoption.",
            "The typed binding fraction is a bracket, not a point, because the receipt "
            "holds marginal and not joint family multiplicities.",
        ],
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    for row in rows:
        c, t = row["cluster_cloud"], row["typed_objects"]
        print(
            f"{row['role']:4s} clusters cap{OUR_CAP} binds {c['binds']:.3f} "
            f"(median {c['median_objects']:.0f} objects, discards "
            f"{c['discarded_energy_share_median']:.1%} of energy) | "
            f"typed cap{TYPED_CAP} binds {t['binds_at_least']:.3f}-{t['binds_at_most']:.3f}"
        )


if __name__ == "__main__":
    main()
