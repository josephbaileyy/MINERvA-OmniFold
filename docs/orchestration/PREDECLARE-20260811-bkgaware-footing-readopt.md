# PREDECLARATION — the background-aware footing re-adoption (BEN-102)

**Written 2026-08-11 BEFORE the run.** Purpose: produce the footing-matched J28 candidate, so that the
value which would eventually replace `\gbdtFiveAdoptTrace` / `\gbdtFiveCVTrace` differs from them by the
**flux fix alone** and not also by a background footing inherited from a missing CLI flag.

**THIS ADOPTS NOTHING.** The 2026-07-12 quarantine stands, causes 1–6 are open, `values.tex` is untouched,
and no number produced here becomes quotable. This exists so that the correct candidate is ready when the
gate opens. Authorized by the orchestrator, under the standing <12 h approval; the a/b footing question
only bites at adoption time, which is why it does not need Joseph now.

## What is being corrected

`sbatch_j28_adopt_5d.sh` passes the J28-corrected `--uthrow` correctly and **never passes `--combined`**,
so it fell through to `adopt_unified_5d.py:76-77`'s default — the **non**-background-aware combined
product. Confirmed in that run's own stdout, not merely inferred from the launcher:
`j28_adopt_56429334.out` prints `[adopt5d] sqrt-trace old combined = 4.3455e-38`, which is the
non-bkgaware block sum (`uq_5d/universe_stage2_5d/uq_universe_5d_summary.txt` → `combined
sqrt-trace=4.3455e-38 median rel=13.432%`). The bkgaware value is `4.3578e-38`, median `13.359%`.

So the published pair `5.81e-38` / `6.24e-38` is bkgaware and the proposed pair `5.2600e-38` /
`5.6609e-38` is not. Two inputs differ, one of them silently.

## The run

Four adoptions from **one unchanged input**, the existing corrected throw ROOT
`uq_5d/unified_throw_cov_5d_fluxfix_20260806_full160.root` — no re-combine, no re-throw, nothing
recomputed upstream:

| arm | `--combined` | `--cv-centered` | role |
|---|---|---|---|
| **A1** | bkgaware | no | **the target**: footing-matched replacement for `\gbdtFiveAdoptTrace` |
| **A2** | bkgaware | yes | footing-matched replacement for `\gbdtFiveCVTrace` (F7 requires it to exist) |
| **C1** | non-bkgaware | no | **reproduction control** — must return `5.2600e-38` |
| **C2** | non-bkgaware | yes | reproduction control — must return `5.6609e-38` |

The controls are the point of running four instead of two: they make the footing difference a **measured**
quantity on one throw ensemble rather than a difference between two historical runs that also differ in
other ways. That is the Magnitude leg's standard applied to this comparison.

**Whole stream redirected, never through `tail`/`head` (BEN-026).** `sbatch_j28_adopt_5d.sh` is left
byte-unchanged so it stays faithful to the run it documents; this is a new launcher.
**`--out` is passed explicitly on all four arms** — `adopt_unified_5d.py:79-80` defaults to the July
product and opens it `RECREATE`, so taking the default would destroy a historical artifact and let the
CV-centered arm clobber the mean-centered one.

## The footing is provable from the PRODUCTS, not just the launchers — and it leaves one empty cell

Added 2026-08-11 after the construction-contract receipt
(`nd-unfolding/uq_5d/receipt_construction_contract_5d.json`). `adopt_unified_5d.py:166` stamps
`sqrt_tr_old` into every adopted product — **the √Tr of the `--combined` input it was actually given** — so
each product records its own footing and no launcher reading is required:

| adopted product | `sqrt_tr_old` | footing it proves | `sqrt_tr_new` |
|---|---|---|---|
| `…_bkgaware_uthrow.root` → `\gbdtFiveAdoptTrace` | **4.357790406860002e-38** | **background-aware** | 5.807716496958672e-38 |
| `…_bkgaware_uthrow_cvcentered.root` → `\gbdtFiveCVTrace` | **4.357790406860002e-38** | **background-aware** | 6.236702327843976e-38 |
| `adopted_meancentered_20260806_full160.root` → proposed `5.2600e-38` | **4.345454363683128e-38** | **NON**-background-aware | 5.25997091000714e-38 |
| `adopted_cvcentered_20260806_full160.root` → proposed `5.6609e-38` | **4.345454363683128e-38** | **NON**-background-aware | 5.660863966183672e-38 |
| `universe_stage2_5d/…_uthrow.root` (July, superseded) | **4.345454363683128e-38** | **NON**-background-aware | 5.802415620046235e-38 |

So the design is a **2 × 2 in (footing × J28) with exactly one cell empty**, and that cell is arm A1:

| | non-background-aware | background-aware |
|---|---|---|
| **pre-J28 throws** | `5.802416e-38` (July) | `5.807716e-38` (**what `values.tex` quotes**) |
| **J28 throws** | `5.259971e-38` (**what is proposed**) | **EMPTY → arm A1** |

Three filled cells give the two main effects separately, each footing-matched, from committed stamps:

    block-sum footing effect          4.345454e-38 -> 4.357790e-38    +0.2839%
    adopted mean-centered footing effect, pre-J28                     +0.0914%
    J28 effect, FOOTING-MATCHED (both non-bkgaware)                   -9.3486%
    J28 effect as PROCEDURE §4 computes it (mixed footings)           -9.4313%
    difference between the two readings                              +0.0827 pp

Note the footing effect on the **adopted** value (+0.0914%) is **not** the `+0.30%` that
`sec_systematics.tex:170-173` quotes — that `0.30%` is the **block sum** (+0.2839% exactly). The adoption's
`max()` inflation transfer damps it threefold. Two different quantities, and the note's sentence is about
the block sum.

## PRE-REGISTERED PREDICTION, stated before the run

Under **no interaction** between the flux correction and the background footing, arm A1 must come out at

    A1_pred = 5.259971e-38 x (5.807716e-38 / 5.802416e-38) = 5.264776e-38  ->  5.2648e-38

**This is the test, and it is a real one rather than a formality:** the two corrections both act on the
vertical block, one through `C_vert` and one through `g`, so multiplicative independence is an assumption
and not a theorem. A1 landing on `5.2648e-38` is B1. A1 landing materially off it is B2 — a measured
interaction, which is physics rather than bookkeeping. **I am recording the predicted value so that
agreement cannot be claimed retrospectively at whatever precision the answer happens to have.**

## PREDECLARED BRANCH SET — and UNRESOLVED is a real third outcome

**B1 — CONTROLS REPRODUCE, FOOTING EFFECT SMALL.** C1 returns `5.2600e-38` and C2 `5.6609e-38` to the
printed precision, and A1/A2 differ from them by an amount consistent with the `+0.30%` bkgaware
refinement recorded at `KNOWN_ISSUES.md` #13 (i.e. roughly `5.26e-38 × 1.003 ≈ 5.28e-38`). → The
footing-matched candidate is established, the mismatch is a provenance defect with a small numerical
consequence, and A1/A2 are the values a future adoption should use.

**B2 — CONTROLS REPRODUCE, FOOTING EFFECT NOT SMALL.** C1/C2 reproduce but A1/A2 move by materially more
than `+0.30%`. → The `+0.30%` bkgaware refinement measured on the *pre-J28* products does **not** transfer
to the J28-corrected ensemble, which would be a real physics result rather than bookkeeping: the two
corrections would not be independent. `sec_systematics.tex:170-173` quotes that `0.30%` and would need
re-deriving. Escalate; do not quietly adopt A1/A2.

**B3 — CONTROLS DO NOT REPRODUCE.** C1/C2 disagree with `5.2600e-38`/`5.6609e-38`. → Something other than
`--combined` also differs between this run and `56429334`, and **the whole BEN-102 diagnosis is then
unsafe** — the footing story would be at best incomplete. Stop, do not report A1/A2 as a candidate, and
find the second difference first. This is the branch that would refute my own finding, and it is the one to
check before believing any of the others.

**B4 — UNRESOLVED.** The job cannot run to completion: the 41 GB bkgaware `--combined` unreadable, an
out-of-memory on the `10694²` eigendecomposition, or a missing per-band `hCov_universe5d_<band>` in the
bkgaware file that is present in the non-bkgaware one. → **UNRESOLVED, not "the footing does not matter"
and not B3.** A per-band inventory difference between the two combined files would itself be a finding:
`adopt_unified_5d.py` needs all 13 `VERT_BANDS`, and if the bkgaware file lacks one, arm A1 cannot be
built at all and the footing-matched candidate does not exist by construction.

## Reported on every branch

A committed receipt carrying, per arm: `--uthrow` and `--combined` paths with sha256, the printed `bins`,
the `g` census (`bins>1`, median, max), `sqrt_tr_old`, `sqrt_tr_new`, the ratio, `median frac/bin` old and
new, and the PSD `min eigenvalue` with `most-neg/max`. Ingredients beside every derived number, so the
ratio can be checked against its operands and the numbers can contradict each other
(`CONVENTION-receipt-ingredients.md`, BEN-077). Plus the four-arm table, so the footing effect and the
J28 effect are separately readable rather than summed.
