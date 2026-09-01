# FINDING 2026-09-01 — cause 4's jitter floor is RECOVERED, and the ledger's `1.539` describes a product that no longer exists

**CITABLE FOR:** the recovered values in §2, their internal consistency in §3, and the ledger
inconsistency in §5.
**NOT CITABLE FOR** discharging cause 4, grading its `M` cell, moving any gate, or adopting anything.
Gate 2 remains **FAIL**. Counts hold at CAND `1 of 7`, QUOTED `0 of 7`.

**Authorized by Joseph in his own turn** — asked whether this lane should take the measurement he had
left unowned: *"You can take it"*. Run read-only in an isolated worktree at `4a3b53a5`, which exited
with a clean `git status`; the only cluster actions were three read-only `ssh` reads.

## 1. The question, and why it had a deadline

`OI-173` (Joseph, 2026-09-01) rules:

> **AND IF THE PRINTED `jit_trace` VALUE IS NOT RECOVERABLE FROM COMMITTED BYTES, `M` IS `NOT MET`
> — UNMEASURED — RATHER THAN `N/A`.**

`8a6cf176` (Lane D, 2026-08-17) had already found exactly one surviving printed value, on **purgeable
scratch**, and warned: *"Recoverable today, not necessarily next month."* That was 15 days ago. The
first thing this lane did was check whether it was still there. **It was.** It is now durable:
`state/RECEIPT-20260901-cause4-jitter-floor-recovered.json`, whose embedded transcript **re-hashes to
the sha256 measured on the cluster** (`a34b554d…`), so the committed copy is byte-identical to the
original rather than merely similar.

## 2. What the log actually says

`/pscratch/…/uq_5d/uthrow5d_comb_55286276.out`, 969 B, mtime `2026-07-01 23:54:25 -0700`, read from
`login28` at `2026-09-01T18:20:05Z`:

```
[null] jitter floor ||x_cv(s+7)-x_cv||^2 = 3.731e-78  (= 2*sum sigma_jit^2); sqrt = 1.932e-39

===== Unified-throw vs block-sum =====
  sqrt-trace  unified=4.1209e-38  block=2.6749e-38  raw ratio=1.541
  jitter-corrected unified sqrt-trace=4.1164e-38  corrected ratio=1.539
```

**`jit_trace = 3.731e-78`.** And the printed block carries the raw ratio too, which no committed
source does.

## 3. Internal consistency — four for four

Every printed number re-derives from the printed operands, using the retired code at `a0cdc019:232-252`:

| quantity | re-derived | printed |
|---|---|---|
| raw ratio `st_uni/st_block` | `4.1209/2.6749 = 1.5406` | `1.541` |
| `st_uni_corr = sqrt(tr_uni − jit)` | `4.1164e-38` | `4.1164e-38` |
| corrected ratio | `4.1164/2.6749 = 1.5389` | `1.539` |
| `sqrt(jit_trace)` | `1.932e-39` | `1.932e-39` |

**THE MAGNITUDE OF CAUSE 4's DEFECT ON THE REPORTED RATIO IS `1.541 → 1.539`, or −0.11%.**

## 4. An alternative reading this lane held, and the measurement REFUTED

Before reading the log, the committed operands made `1.539` arithmetically **impossible** as a
jitter-corrected sqrt-trace ratio (§5), and exactly one reading survived: that `1.539` was a *trace*
ratio rather than a *sqrt-trace* ratio, under which `jit_trace` inverted cleanly to `2.0736e-76`.

**That reading is wrong, and it is recorded here because it was the convenient one.** The log prints
`corrected ratio` from `st_uni_corr/st_block` — a sqrt-trace ratio, exactly as the sibling 4D and FPS
lines read. Adopting the trace reading *because it was the one that made the value recoverable* would
have been measurability choosing the specification, which is the failure `SCOREBOARD` §2c and this
row's own ruling both name. It was held as a hypothesis and killed by an observation.

## 5. THE LARGER FINDING: the ledger attributes `1.539` to an artifact whose own operands contradict it

`VALIDATION_LEDGER.md:1192` reads: *"the 5D unified-throw check subsequently landed and was ADOPTED
2026-07-01/02 (jitter-corrected trace ratio **1.539**…); adopted covariance
`uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root`"*.

But the adopted throw ROOT's **own committed operands** — VL44 at `:488`, restated at `:1021` as *"read
from the adopted ROOT directly"* — are `sqrt_tr_unified = 4.4607819710748654e-38` and
`sqrt_tr_block = 3.4032639007214586e-38`, whose **raw** sqrt-trace ratio is **1.3107**.

**A jitter-corrected ratio can never exceed its raw ratio**, because the correction subtracts a
non-negative `jit_trace`. `1.539 > 1.3107`, so **`1.539` cannot describe the adopted artifact.**

The recovered log resolves why. Its last line is `[combine] wrote uq_5d/unified_throw_cov_5d.root`,
and that path's current occupant is **2 677 168 123 B, mtime `2026-07-13 02:15:41 -0700`** — measured
this session, matching Lane D. **The path was reused and overwritten twelve days later.** So `1.539`
is the 2026-07-01 occupant's number, and the ledger prints it under the name of the artifact that
replaced it.

**A SECOND-ORDER CONSEQUENCE, recorded not resolved:** `:1214-1215` compares PET's `5.711` — an
explicit sqrt-trace ratio with both operands stated — against *"the GBDT-side 5D ratio (1.539)"* as
like-for-like. Both are sqrt-trace ratios, so the units agree; but they describe artifacts of
different vintage, and the 5D side is a superseded occupant. That is an asymmetric comparison in the
published ledger.

**AND THE 5D LINE IS THE ONLY ONE OF ITS FOUR SIBLINGS WITH NEITHER OPERANDS NOR A RAW COUNTERPART.**
PET `:1214` states both operands; 4D `:1252` states both operands; FPS `:1350` states raw **and**
corrected. 5D `:1192` states neither — which is exactly why it could drift without contradiction.

## 6. A SCOPE FLAG on the 4D arm, not graded here

`VALIDATION_LEDGER.md:1252` gives 4D as *"sqrt-tr unified `3.3924e-38` vs block `1.6858e-38`, ratio
**2.012**"*. That quotient is `2.0123` — **the RAW ratio**. Yet
`docs/HIGHER_DIM_OMNIFOLD_DESIGN.md:155` calls `2.01` the *"jitter-corrected unified/block sqrt-trace"*,
and `:153-157` records it as **adopted** as the published 4D systematic. So the 4D arm may carry the
same raw-labelled-as-corrected slippage. **This lane did not audit `adopt_unified_4d.py`**; per the
(cause × artifact) rule that is separate grading, and this is a flag, not a finding.

## 7. What this does and does not settle for `M`

**The value IS now in committed bytes — as of this commit, and not before it.** Under `OI-173`'s
conditional, `M` was `NOT MET` at `4a3b53a5` because nothing durable carried the value. This receipt
changes the input to that test; **it does not by itself grade the cell**, and this lane does not move
it.

**Two things a grader must weigh, and neither is this lane's call:**

1. **The recovered value belongs to a superseded product.** Joseph ruled 2026-08-31 that the seven
   causes are graded **against the candidate**, `stamped_bkgaware_meancentered_20260812.root` — not
   against the July artifact, and certainly not against the July artifact's *predecessor*. On the face
   of it a July-01 jitter floor grades neither.
2. **No jitter floor is known for the currently adopted artifact.** Lane D's open question — whether
   the 07-13 headline run passed `--null` at all — is still open here. A repository-wide scratch sweep
   for any other printed jitter floor was launched this session and had not returned when this record
   was written; **its result is not incorporated, and its absence is not evidence.**

## 8. Recommended next step, costing nothing

Correct `VALIDATION_LEDGER.md:1192` so the `1.539` is attributed to the 2026-07-01 occupant it
actually describes, and record the adopted artifact's raw ratio `1.3107` beside it — or state plainly
that no jitter-corrected ratio is known for the adopted artifact. **That is a documentation
correction, not a discharge**, and it removes a number that currently reads as a property of a live
adopted product while being a property of a deleted one.
