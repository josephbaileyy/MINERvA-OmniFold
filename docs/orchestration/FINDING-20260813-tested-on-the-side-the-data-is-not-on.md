# FINDING 2026-08-13 — tested on the side the data is not on

**BEN-180, BEN-181.** Lane D (verifier), independent pass on lane B's Gate 6 Leg F floor replication
at `2fecce7`. Per-item adjudication is in `VERDICTS-20260811-session-D.md` §V44–V49; this file is the
transferable part.

**Context, stated first because it changes how the finding should be read.** Lane B's Leg F artifacts
are the most defensible thing I have audited on this campaign. The predeclaration has one commit and is
byte-identical to it; all three frozen thresholds are inside that blob, so they were fixed before any
draw existed and no timestamp argument is needed; the branch-1 unreachability claim is a sound theorem;
and **eight of nine mutations I threw at the 52-test battery were caught, including the two that test
whether the refusal-to-verdict binds.** The finding below is a hole in an otherwise unusually good
instrument, not a case against it.

## 1. The surviving mutant (BEN-180)

`gate6_floor_statistics.py` computes `d_by_draw[j] = abs(v[j,k] - 1.0)`, and branch 1 fires only if
every `d ≤ 0.10`. **Drop the `abs` and all 52 tests still pass.**

Without it, `d = v - 1.0`, so a draw at `v = 0.5` yields `d = -0.5 ≤ 0.10` — in band. **Every draw below
1 becomes unconditionally in-band, however far below.** The band check survives only on the above-1 side.

All four band tests exercise that side alone:

| test | input |
|---|---|
| `test_small_range_but_a_draw_outside_the_band_is_intermediate_not_seed_determined` | values `1.20, 1.21` |
| `test_band_boundary_is_inclusive` | via `stats_at` |
| `test_band_one_float_step_outside_is_not_inclusive` | via `stats_at` |
| `test_a_single_draw_outside_the_band_is_enough_to_fail_branch1` | via `stats_at` |

`stats_at` hand-builds the minimal stats dict `apply_verdict` reads, so it **never calls
`floor_statistics`** and the `abs` is not on its path at all. Its docstring is candid about the bypass —
*"`<=` vs `<` at the boundary … is only testable at the predicate"*, which is correct and well-reasoned —
and closes *"the value-driven tests below cover the wiring."* **They cover it on one side.**

**Why this side.** Gate-6 members 4 and 5 sit at `0.819792` and `0.753477` at iteration 2; draw 3's
iteration-0 value is `0.8400`. The whole Leg F question is about trajectories approaching 1 **from
below**. That is the half the battery cannot defend, and `d = −0.16` reads as in-band without the `abs`.

The code is right today. The battery is what protects a frozen rule from what B's own docstring calls
*"a future edit under schedule pressure"*, and against that edit, on this side, it is silent.

> **Check:** for a predicate built on a symmetric quantity — an absolute value, a magnitude, a
> two-sided band — find the test on each side. `BEN-173` is the same shape at the level of two fields in
> one function; this is it at the level of two signs in one comparison. Ask which mutation each test
> could survive, not whether the suite is green.

## 2. The harness that manufactured a hole (BEN-181)

Before the above was real, it was fake — in a different arm.

My first `ddof` mutation replaced the literal string `ddof=1`. That string occurs in
`gate6_floor_statistics.py` **only at `:198`, inside a docstring, and at `:219`, as the dict key
`F_sd_ddof1`.** The standard deviation is computed by hand:
`math.sqrt(sum((x - mean) ** 2 for x in col) / (n - 1))`. So the regex rewrote prose, changed no
behaviour, the suite passed, and my harness printed **SURVIVED**.

Rewritten against the actual expression (`/ (n - 1)` → `/ n`), the same battery **caught it in two
tests** — `test_sd_is_ddof1_not_population` is a perfectly binding test, built on the one input where
the two estimators differ visibly (`sqrt(2)` vs `1`).

**I was one step from filing a coverage hole against a test that works.** What stopped it was reading
the mutated source before reading the result — the same ordering that saved the E_avail pass, where an
arm claimed four of six sites were dead code and hand-checking showed the regex had simply never covered
two idioms.

> **Check:** a surviving mutant is a claim about the test suite **only if** the mutation reached
> executable code. `re.subn` returning 1 proves a string was replaced, not that behaviour changed.
> Diff the mutant's *behaviour*, or at minimum read the line that was rewritten. A mutation harness
> that can silently mutate a comment reports the auditor's bug as the auditee's.

Kept in the committed harness as `M7void` alongside the corrected `M7`, because a harness that hides
its own false positive is the thing this finding is about.

## What this pass did not establish

- **No Slurm reach.** "3 of 5 draws, tasks 2 and 3 COMPLETED" is B's measurement, not mine. I verified
  the rule and the battery, not the job states, and not that the receipt's `v` values were read off the
  artifacts they name.
- **Nine mutations is a sample.** M9 was found by going to look at the `abs`. There may be other
  survivors I did not construct, and `52 passed` was never the evidence.
- **The eight validity clauses were checked for independent tests that fail on one degradation, not
  against real draw artifacts.**
