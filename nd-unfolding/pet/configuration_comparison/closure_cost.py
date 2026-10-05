"""What the campaign costs as it is now built: a closure, split three ways.

`calibrate_cost` models the REAL-DATA nominal -- `ROWS_PER_FIT_STEP1` is
`train_events + n_data`, with `n_data` the measured 4.1 M-row data leg. The
comparison does not have a data leg. It is a powered closure: `mc-only`, the
pseudo-data is half A of the MC subsample, the prior is half B, and each stage
sees only its own share of the draw. Every row count in the old model is
therefore the wrong row count, and the 366 GPU-hour figure built on it is not
this campaign's number.

This module derives the counts from the structure the driver actually builds
and prices them with the measured throughputs, each imported or cited rather
than retyped.

NOT CITABLE FOR a throughput. It multiplies measurements; it makes none.
"""
from __future__ import annotations

import math
from typing import Any, Mapping

import frozen_design as fd
import training_recipe as recipe

# Measured, one A100, production precision. Ours from COST_UPDATE2-20260919
# (12 tokens, batch 512). His from the optimised XLA path at 33 tokens and
# batch 2048, which is the configuration the arm now actually builds --
# `flat_projection` through the attention and `jit_compile` forced in
# `compile`. Before those two repairs the arm ran a different model from the
# one these numbers describe, and OOMed.
MICROSECONDS_PER_EXAMPLE = {
    "ours": {"train": 38.97, "inference": 18.15},
    "theirs": {"train": float(fd.EXECUTION["measured_microseconds_per_example"]),
               # Measured 134.86 at the matched cell; the optimised path's
               # inference was not separately measured at 33/2048, so this is
               # the matched-cell figure and is flagged as such.
               "inference": 134.86},
}
INFERENCE_IS_MEASURED_AT_THE_RUN_CONFIGURATION = {"ours": True, "theirs": False}

# MEASURED, job 58601269's prematerialize report: 4,141 of 10,000 half-A rows
# are `pass_reco & pass_gen`. The pseudo-data leg is that subset, so it is a
# row count the cost depends on and not a detail.
STEP1_PASS_FRACTION = 4141 / 10000

# Tuning sweeps the frozen grid: 4 rates x 4 seeds x 2 arms. It was 8, which
# evaluated one point and selected nothing.
TASKS_PER_STAGE = {"tuning": 32, "pilot": 8, "final": 16}
RETRY_ALLOWANCE = 1.25


def rows(max_events: int, stage: str) -> dict[str, int]:
    """The row counts one arm-evaluation of `stage` actually presents."""
    fraction = float(fd.SPLITS["fractions"][stage])
    owned = int(max_events * fraction)
    half = owned // 2
    pdata = int(round(half * STEP1_PASS_FRACTION))
    return {
        "stage_owns": owned, "half": half,
        "pdata_rows": pdata, "prior_rows": half,
        # `MultiFold` concatenates both classes before training: step 1 sees
        # pseudo-data plus prior, step 2 sees the prior twice.
        "step1_ntrain": pdata + half, "step2_ntrain": 2 * half,
    }


def evaluation_hours(arm: str, max_events: int, stage: str) -> dict[str, Any]:
    """GPU-hours for one arm-evaluation, training plus the forward-only work."""
    if arm not in MICROSECONDS_PER_EXAMPLE:
        raise ValueError(f"unknown arm {arm!r}")
    r = rows(max_events, stage)
    niter, epochs, frac = int(recipe.NITER) if hasattr(recipe, "NITER") else 3, \
        int(recipe.EPOCHS), 0.8
    train_examples = niter * epochs * frac * (r["step1_ntrain"] + r["step2_ntrain"])
    validation = (1.0 - frac) / frac * train_examples
    reweight = 2 * niter * r["prior_rows"]
    us = MICROSECONDS_PER_EXAMPLE[arm]
    train_hours = train_examples * us["train"] * 1e-6 / 3600.0
    infer_hours = (validation + reweight) * us["inference"] * 1e-6 / 3600.0
    return {
        "arm": arm, "stage": stage, **r,
        "train_examples": int(train_examples),
        "inference_examples": int(validation + reweight),
        "train_hours": train_hours, "inference_hours": infer_hours,
        "hours": train_hours + infer_hours,
        "inference_rate_measured_at_this_configuration":
            INFERENCE_IS_MEASURED_AT_THE_RUN_CONFIGURATION[arm],
    }


def campaign(max_events: int = 2_000_000,
             tasks: Mapping[str, int] | None = None) -> dict[str, Any]:
    """The whole campaign, by stage and arm, with the retry allowance."""
    tasks = dict(TASKS_PER_STAGE if tasks is None else tasks)
    rows_out = []
    total = 0.0
    for stage, count in tasks.items():
        per_arm = count // 2
        for arm in ("ours", "theirs"):
            cell = evaluation_hours(arm, max_events, stage)
            cell["tasks"] = per_arm
            cell["stage_hours"] = cell["hours"] * per_arm
            total += cell["stage_hours"]
            rows_out.append(cell)
    return {
        "max_events": max_events,
        "cells": rows_out,
        "hours_without_retries": total,
        "retry_allowance": RETRY_ALLOWANCE,
        "hours_with_retries": total * RETRY_ALLOWANCE,
        "superseded": ("the 366 GPU-hour figure, which was built on the "
                       "real-data nominal's row counts -- a 4.1 M-row measured "
                       "leg this campaign does not have"),
        "caveat": ("his inference rate is the matched-cell measurement, not one "
                   "taken at 33 tokens and batch 2048; the inference term is "
                   "the smaller one but the number is not his run's"),
    }


def half_size_for(max_events: int, stage: str) -> int:
    return rows(max_events, stage)["half"]


def max_events_for_half(half: int, stage: str) -> int:
    """The draw needed to give `stage` two halves of `half` rows."""
    return int(math.ceil(2 * half / float(fd.SPLITS["fractions"][stage])))
