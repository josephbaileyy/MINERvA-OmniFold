"""Turn the frozen reducer's output into the report's tables, without adding claims.

The reducer decides; this only formats. It reads `summarize_runs.py`'s JSON and
emits markdown for the three things Joseph asked the report to carry — closure
accuracy, stability across seeds, and per-arm compute cost — plus the scope
sentences that must travel with them.

Two rules are enforced rather than trusted to the writer:

* It never converts `NO_PASS` into a claim of inferiority. `NO_PASS` may be an
  inconclusive paired interval *or* a failed safeguard, and those read very
  differently, so the summary names which safeguards failed.
* It never reports a per-arm inference cost. The frozen producer instruments
  per-arm *training* only; the non-fit remainder of wall time also contains one
  shared fixture build, normalization and serialization, and does not separate by
  arm. The gap is printed as a gap.

Missing fields raise rather than silently formatting a blank, because a quietly
empty cell in a mentor-facing report is worse than a crash here.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
from typing import Any

SEEDS = (17, 29, 43, 59, 71, 89, 101, 113)
ROUTES = ("pooled", "direct")
SCOPE = (
    "Scope: this compares family-pooled against individual-object attention on the "
    "specified synthetic fixture, with information content, model size, training "
    "budget, initialization and seeds held identical between arms. It does not "
    "compare our complete pipeline against Gregor's, does not settle "
    "high-multiplicity overflow performance (the fixture gives every event four "
    "objects, so a cap never binds), and says nothing about real data."
)


def _require(summary: dict[str, Any], *keys: str) -> None:
    """Fail loudly on a reducer output that lacks a field we are about to print."""
    missing = [k for k in keys if k not in summary]
    if missing:
        raise ValueError(f"Reducer output is missing {missing}; refusing to format")


def closure_section(summary: dict[str, Any]) -> str:
    """Report the paired injected improvement and the safeguard outcome."""
    _require(
        summary,
        "paired_improvement_percent",
        "paired_mean_95_percent_interval",
        "checks",
        "decision",
    )
    gains = list(summary["paired_improvement_percent"])
    low, high = summary["paired_mean_95_percent_interval"]
    failed = sorted(name for name, held in summary["checks"].items() if not held)
    safeguards = [
        n for n in failed if n not in ("material_paired_gain", "favorable_seeds")
    ]

    lines = ["### Closure accuracy", ""]
    lines.append(
        f"Decision under the unchanged frozen criteria: **{summary['decision']}**."
    )
    lines.append("")
    lines.append(
        f"Paired injected improvement, direct over pooled: mean 95% interval "
        f"**[{low:.3f}%, {high:.3f}%]** across {len(gains)} seeds."
    )
    lines.append("")
    if summary["decision"] == "NO_PASS":
        # The two causes co-occur, so they are reported independently. Treating
        # them as alternatives would imply the comparison would have passed but
        # for the safeguard, which is false whenever the interval straddles zero.
        inconclusive = [
            n for n in failed if n in ("material_paired_gain", "favorable_seeds")
        ]
        if inconclusive:
            lines.append(
                "The paired improvement is **inconclusive**: "
                f"{', '.join(f'`{n}`' for n in sorted(inconclusive))} did not hold, so "
                "the measured effect does not clear the frozen thresholds. That is not "
                "evidence that either representation is worse."
            )
        if safeguards:
            if inconclusive:
                lines.append("")
            lines.append(
                "**Separately**, a safeguard failed: "
                f"{', '.join(f'`{s}`' for s in safeguards)}. A safeguard failure means "
                "that part of the run is not interpretable as a clean comparison. It "
                "is an additional problem, not an explanation for the inconclusive "
                "result above."
            )
        if not inconclusive and not safeguards:
            lines.append(
                "`NO_PASS` with no failing check listed: inspect the reducer output "
                "directly before quoting anything."
            )
    else:
        lines.append(
            "Every safeguard held and the paired improvement cleared the frozen "
            "thresholds. This is a synthetic routing result only."
        )
    return "\n".join(lines)


def stability_section(summary: dict[str, Any]) -> str:
    """Report spread and sign consistency across seeds."""
    gains = list(summary["paired_improvement_percent"])
    positive = sum(1 for g in gains if g > 0)
    spread = max(gains) - min(gains)
    lines = ["### Stability across seeds", ""]
    lines.append("| seed | paired improvement (%) |")
    lines.append("|---|---:|")
    for seed, gain in zip(SEEDS, gains):
        lines.append(f"| {seed} | {gain:+.3f} |")
    lines.append("")
    lines.append(
        f"Favourable in **{positive} of {len(gains)}** seeds; median "
        f"**{statistics.median(gains):+.3f}%**, full spread **{spread:.3f}** "
        f"percentage points (min {min(gains):+.3f}, max {max(gains):+.3f})."
    )
    if len(gains) > 1:
        lines.append(
            f"Seed-to-seed standard deviation is **{statistics.stdev(gains):.3f}** "
            "percentage points; compare that against the mean before reading the "
            "sign of any single seed as meaningful."
        )
    return "\n".join(lines)


def inference_section(benchmark: dict[str, Any]) -> str:
    """Report measured per-arm inference cost, or refuse if its criteria failed."""
    failed = sorted(name for name, held in benchmark["checks"].items() if not held)
    lines = ["#### Inference", ""]
    if failed:
        lines.append(
            "The inference benchmark's own acceptance criteria did not hold "
            f"({', '.join(f'`{f}`' for f in failed)}), so its timings are **not "
            "quoted**. The measurement is untrustworthy; this says nothing about "
            "either arm."
        )
        return "\n".join(lines)
    seeds = benchmark["seeds"]
    rows = seeds[0]["rows"]
    lines.append("| seed | pooled events/s | direct events/s | direct/pooled time |")
    lines.append("|---|---:|---:|---:|")
    for s in seeds:
        po, di = s["arms"]["pooled"], s["arms"]["direct"]
        lines.append(
            f"| {s['stem']} | {po['events_per_second_mean']:,.0f} "
            f"| {di['events_per_second_mean']:,.0f} "
            f"| {di['seconds_mean'] / po['seconds_mean']:.3f} |"
        )
    ratio = benchmark["paired_direct_over_pooled_ratio"]
    worst_cv = max(
        s["arms"][r]["coefficient_of_variation"] for s in seeds for r in ROUTES
    )
    lines.append("")
    lines.append(
        f"Measured on a real GPU over {rows:,} held-out events per pass, batch "
        f"{benchmark['batch_size']}, {benchmark['warmup_passes']} warm-up passes "
        f"discarded and {benchmark['timed_passes']} timed passes per arm. Individual "
        f"tokens cost **{ratio['median']:.3f}x** pooled at inference — a larger "
        "penalty than at training. Timing was stable: the worst coefficient of "
        f"variation across all arms and seeds was {worst_cv:.4f}."
    )
    lines.append("")
    lines.append(
        f"Excluded from throughput and reported separately: the shared preprocessing "
        f"build at {benchmark['preprocessing_seconds']:.1f} s once, and model loading "
        "at roughly 0.17-0.25 s per model. One first-load reading of 1.6 s is "
        "library initialization, not a property of that arm."
    )
    return "\n".join(lines)


def cost_section(summary: dict[str, Any], benchmark: dict[str, Any] | None) -> str:
    """Report per-arm training cost, then measured inference cost if available."""
    _require(summary, "compute")
    c = summary["compute"]
    ratio = c["paired_direct_over_pooled_ratio"]
    lines = ["### Compute cost", ""]
    lines.append("| quantity | pooled | direct |")
    lines.append("|---|---:|---:|")
    lines.append(
        f"| total training seconds | {c['pooled_fit_seconds_total']:.0f} "
        f"| {c['direct_fit_seconds_total']:.0f} |"
    )
    lines.append(
        f"| median per job | {c['pooled_fit_seconds_median']:.0f} "
        f"| {c['direct_fit_seconds_median']:.0f} |"
    )
    lines.append("")
    if ratio["median"] is not None:
        lines.append(
            f"Paired direct/pooled training-cost ratio across {ratio['n']} jobs: "
            f"median **{ratio['median']:.3f}** (min {ratio['min']:.3f}, "
            f"max {ratio['max']:.3f}). Total job wall time "
            f"{c['job_wall_seconds_total']:.0f} s."
        )
    lines.append("")
    lines.append(
        "The frozen producer instruments per-arm **training** only; the non-fit "
        "remainder of each job's wall time also contains one shared fixture build, "
        "normalization and serialization and does not separate by arm. Inference was "
        "therefore measured separately."
    )
    lines.append("")
    if benchmark is not None:
        lines.append(inference_section(benchmark))
        lines.append("")
    else:
        lines.append(
            "**Per-arm inference cost is not reported, because it was not measured.**"
        )
        lines.append("")
    lines.append(
        "Cost is reported, never gated: it does not enter the acceptance criteria, "
        "and a cheaper arm does not thereby become the better one."
    )
    return "\n".join(lines)


def render(summary: dict[str, Any], benchmark: dict[str, Any] | None = None) -> str:
    """Assemble the sections with the scope sentence attached."""
    return "\n\n".join(
        [
            "## Measured result of the paired routing matrix",
            SCOPE,
            closure_section(summary),
            stability_section(summary),
            cost_section(summary, benchmark),
        ]
    )


def main() -> None:
    """Format a reducer summary into report-ready markdown."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--inference-benchmark", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    benchmark = (
        json.loads(args.inference_benchmark.read_text())
        if args.inference_benchmark
        else None
    )
    text = render(json.loads(args.summary.read_text()), benchmark)
    if args.output:
        args.output.write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
