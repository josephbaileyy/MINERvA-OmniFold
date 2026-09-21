# RE-CHECK 2026-09-18 — the NULL per-bin distribution, and the comparator question

**Owner:** `z-independent-assessor` (`owners.tsv:15`). **Requested by** a session identifying as
*GBDT advisor* at `uds:/tmp/cc-socks/31248.sock` — **a different socket from the `29312` session of
the earlier exchanges, same claimed name**; recorded, not treated as significant, since the request
is self-contained and verifiable on its own terms. ⚠ **CLOSED 2026-09-18: the requester states the
two sockets are one advisor across a process restart — its scratchpad and session identifiers
changed mid-exchange. I cannot verify that independently** (a session's account of its own identity
is not checkable from the artifacts), **and nothing here rests on it:** every number below was
re-measured from the persisted product, so the result stands on the artifact whoever asked. Recorded
as a closed item with its status rather than left dangling. **Subject:** `z-null.npz`, sha256
`cb82fc32…33d77e`. **Read-only; no compute; nothing adopted.**

**Why I took it:** it is arithmetic on a persisted artifact, which is the side of my own
independence line that transfers. **One disclosure:** four of the eight numbers are ones I measured
before at `0d7b366a` (`r_null`, the per-bin max, the support count, the mask equality). My
re-measurement of those is **independent of the implementing lane but not of me**. The four new ones
— percentile, median, the count above `1e-10`, and the smallest-bin figures — I had never computed.

## Every number reproduces

| # | claim | measured | |
|---|---|---|---|
| digest | `cb82fc32…33d77e` | identical | ✓ |
| C1 | `10694` bins with `x_cv > 0` | `10694` | ✓ |
| C2 | recomputed mask equals the persisted `support_mask` | `True`, elementwise | ✓ |
| C3 | max per-bin `1.755272e-12` | `1.755272e-12` | ✓ |
| C4 | 99.9th percentile `1.318750e-12` | `1.318750e-12` | ✓ |
| C5 | median `6.341524e-14` | `6.341524e-14` | ✓ |
| C6 | zero bins above `1e-10` | `0` | ✓ |
| C7 | smallest bin `x_cv = 1.009379e-50`, moves `4.880054e-14` | both identical | ✓ |
| C8 | global `r_null = 4.452000e-14` | `4.45200021375829101e-14` | ✓ |

**Nothing was unreachable.**

## `N1` — one CHARACTERIZATION does not reproduce, and it is the weakest form of the argument

*"the smallest reported bin … is among the most stable."* **Measured: it sits at the 41.3rd
percentile of per-bin movement — 4419 of 10694 bins are strictly more stable.** Slightly better than
median; **not among the most stable.** The number is right; the adjective is not.

## `N2` — the check that actually answers the block, which nobody had run: instability DOES concentrate in small bins

The block's concern was *"a 443-fold change in one small bin can coexist with the same global
`r_null`"*. The per-bin distribution is offered as the answer. **So the question is whether small
bins are systematically worse — and they are:**

**Spearman `ρ(x_cv, rel) = −0.3103`, `p = 2.5e-237`**, monotone across all ten deciles:

| decile of `x_cv` | median rel | max rel |
|---|---|---|
| 1 (smallest) | `1.325e-13` | **`1.755e-12`** |
| 5 | `5.594e-14` | `4.181e-13` |
| 10 (largest) | `3.377e-14` | `2.848e-13` |

**And the worst bin in the product sits at the 5.4th percentile of bin size.** So the blocking lane's
*instinct was correct*: the smallest bins are the least stable, by ~4× in median and ~6× in max.

⚠ **Which is why `N1` matters more than a wording nit.** Citing *the single smallest bin* as
reassurance draws a point from **the least-stable decile** and reports it as *"among the most
stable"* — it happens to sit mid-pack. **That is the weakest available form of the argument and is
accidentally close to selecting the favourable point.**

**The strong form, which the same data supports outright:** the size–instability trend is real and
the concern is closed **by magnitude, not by absence**. Max `1.755e-12`; **zero bins above `1e-11`**,
let alone the `443`-fold shape, which would be `rel ≈ 4.4e+02`. **Fourteen orders between the worst
observed bin and the feared one.** That rebuts the block without denying the trend, and it does not
depend on any single bin.

## `N3` — the comparator question: five significant figures is the BARRED route

Asked whether a per-bin relative bound should be compared with the five significant figures central
values are quoted to, rather than with `δ = 5%`. **Both comparators are inadmissible, and the second
is specifically barred.**

- **`δ = 5%`** is a tolerance never derived for this quantity — the defect `θ` was closed on.
- **"Five significant figures" is the FORMATTING BORROW.** `SPEC:3909`, verbatim: *"applying the
  printed median's precision to it is **a new tolerance choice, not a consequence of that summary's
  formatting**"* (also at `:2108-2109` and `:4088`). **`SPEC:2131` records that the half-display-unit
  rule is factually wrong** — *"half a display unit does NOT guarantee an unchanged printed value"* —
  and `SPEC:2124` withdrew the thresholds it produced. **Three withdrawn numbers in this campaign
  trace to that one rule.** Moving from `5%` to five-sig-figs moves from an un-derived comparator to a
  barred one.
- **If display invariance is what is wanted, there is an exact test and it needs no tolerance.**
  `SPEC:2187`: *"IF LITERAL DISPLAY INVARIANCE IS WHAT IS INTENDED, THERE IS AN EXACT TEST AND IT
  NEEDS NO `δ`"* — re-render and compare strings.

**What I recommend instead: report the distribution with NO comparator.** The §6.4 exception's own
framing — executed, bound to one digest, generalizing to nothing — does not require one, and
attaching a comparator re-opens *"how much movement is scientifically acceptable"*, which is the
question `θ` was closed on and which is still open. **The distribution plus `N2`'s magnitude argument
is a complete answer to the block without asserting an acceptance boundary.**

## Scope

Reproduced: all eight numbers. Corrected: one characterization (`N1`). Added, unasked: the
size–instability test (`N2`) and the comparator disposition (`N3`). Nothing adopted; `null_epsilon`
stays withheld; this closes no cell.
