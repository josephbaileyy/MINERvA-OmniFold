# FINDING 2026-08-14 — a check fed input built by the code it re-derives with is vacuous

**BEN-186.** Lane D (verifier), from `OI-22` leg (a). Adjudication: `VERDICTS-20260811-session-D.md`
§V52. Receipt: [`state/oi22-legA-real-input-verification-20260814.json`](state/oi22-legA-real-input-verification-20260814.json).

## The shape

`assert_no_truth_leakage(event_reco, reco_blocks, truth_blocks, …)` proves three things, and its
strongest is **PURITY**: rebuild `event_reco` from the reco blocks alone, with the same masked
normalisation, and require an **exact** match. Anything the truth arrays contributed shows up as a
mismatch. It is a good check, carefully written, with its reasoning in the docstring.

`event_reco` is not stored anywhere. It is the loader's **output**. So to run the check "on the real
publication input" someone has to produce an `event_reco` — and the obvious way is to call
`build_event_features` on the real blocks.

**That makes PURITY pass by construction.** The check re-derives with the same function that produced
its input, so the exact match is guaranteed before any data is looked at. The check runs, prints
nothing alarming, and has tested the identity `f(x) == f(x)`.

Measured, on a 2,000,000-event slice of the real NPZ:

| arm | expected | observed |
|---|---|---|
| L1 unmodified, self-built `event_reco` | PASS | **PASS — and worth nothing** |
| L2 truth pT substituted into the reco leg | FIRE | **FIRED**, *"event_reco is NOT a pure function of the reco blocks+pass_reco (leak?)"* |
| L3 all-NaN `event_reco` | FIRE | **FIRED**, on the finiteness guard ahead of the dissimilarity test |

**L2 is the point, and it cuts both ways.** It fires *through statement 2* — the same statement that is
vacuous in L1. So the check is not broken and is not weak; **the same assertion is vacuous or decisive
depending purely on where its input came from.** That is not a property you can read off the check.

## Why this is not just "circular reasoning"

The usual advice — *don't test a function with itself* — is about the check. Here the check is fine.
The defect is in the **provenance of the argument**, one call frame away, and it is invisible at the
call site: `assert_no_truth_leakage(er, r, t, …)` looks identical whether `er` came from the production
loader or from a line above it.

> **Check:** for any assertion of the form *"recompute X and require a match"*, ask **who built the X
> that was passed in.** If the answer is *"the same code path the assertion recomputes with"*, the
> assertion is an identity and proves nothing about the data. The finding is not that the check is
> wrong — it is that a green result from it carries no information unless the input has independent
> provenance.

Corollary worth keeping: **a self-built input still supports the negative arms.** L2 and L3 demonstrate
the detector engages the real object's own arrays, which is strictly more than fixture-only status and
is cheap. What it cannot do is license *"no-truth-leakage holds on the publication input"* — for that
the `event_reco` must come from `build_fullevent_loaders`, i.e. the production loader, over all
49,152,885 events.

## Family

- `BEN-173` — a positive control on one artifact and none on its sibling.
- `BEN-180` — a band tested only on the side the data is not on.
- `BEN-185` — a conditionally-skipped test reporting inside a passing suite.
- **`BEN-186`** — a check whose input was built by the code it re-derives with.

All four are *"the check ran and told you nothing"*, differing in **why**: no control, a one-sided
control, no execution, and execution against an input that cannot disagree. The first three are found
by reading the test; **this one is found only by reading the caller.**

## Named interest, and the estimate that was mine

I scoped leg (a) as *"numpy-only, one streaming pass, cheap"* and the orchestrator dispatched it back as
that spec. Half was right: schema parity is a property **of the NPZ** and is now
`PROVED-ON-REAL-INPUT`, digest-bound with 4/4 controls fired. **No-truth-leakage is a property of the
loader's output**, which the NPZ does not contain, so it costs a production loader pass — ~11–13 GB
resident, a compute-node job. **A verifier who under-scoped work has an incentive to present the
cheap half as the whole leg**, so: leakage remains `PROVED-ON-FIXTURE-ONLY`, and the four-row verdict
in §V52 says so.
