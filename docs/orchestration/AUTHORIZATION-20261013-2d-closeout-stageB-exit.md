# AUTHORIZATION 2026-10-13 — 2D closeout: Stage B terminal outcome, the G2 route, and the director's diagnostics rulings

**Issued by** the paper-tighten lane, as director, under
[`AUTHORIZATION-20261012-2d-closeout-delegation.md`](AUTHORIZATION-20261012-2d-closeout-delegation.md).
It follows the merge of the Stage B diagnostics (PR #107, `main` `ac45462c`). Inputs:
- [`state/2d-closeout/stageB/REPORT.md`](state/2d-closeout/stageB/REPORT.md), sha256 `3e100f60…`;
- [`state/2d-closeout/stageB/diagnostics/REPORT.md`](state/2d-closeout/stageB/diagnostics/REPORT.md), sha256 `3b59251a…`.

**CITABLE FOR:**
- Stage B's terminal outcome and its two remaining conditions;
- the G1 disposition;
- the route by which G2 is decided;
- the director's three rulings made by cross-session message during the diagnostics (§3), which the
  diagnostics verifier could not check.

**NOT CITABLE FOR:**
- compute. The Stage C pilot is granted separately in
  [`AUTHORIZATION-20261013-2d-closeout-stageC-pilot.md`](AUTHORIZATION-20261013-2d-closeout-stageC-pilot.md);
- a July rebuild or a G2 repair;
- how G2 is carried in the construction or disclosed in the deliverables (Joseph's);
- adoption, claims, the KI-85 lift or publication changes (Joseph's).

## 1. Stage B terminal outcome: EXIT CONDITIONAL, with two named conditions carried into the pilot

The plan's exit is "no unassigned or omitted material source; feasible inputs and a reviewed final recipe".
The recipe is final in content. It is Stage B §4 with Joseph's 2026-10-12 decisions
([`../publication/DECISION-20261012-joseph-2d-closeout-recipe.md`](../publication/DECISION-20261012-joseph-2d-closeout-recipe.md)):

| item | disposition |
|---|---|
| R2 | the C04+X01 repair, since adopted as VL175 |
| R5 | the three-stream seed-42 bootstrap |
| C07′ | omitted, with the disclosure of diagnostics §6.2 |
| G3 | `NormDISCC` kept null and disclosed as zero and unconfirmed. The collaboration question is recorded for Joseph or Ben to ask |

The diagnostics add:
- **G1: no repair needed.** P4 measured G1 = 0, and `E_U` is not implicated.
- **G2:** P5 routed NOT RESOLVED ABOVE TRAINER NOISE in `MaRES_0`, so the pre-declared rule triggers no repair
  there.

Two conditions remain open. Each needs a run, and its consequence is declared here, before that run:

| condition | why it is open | measured by | passes when | otherwise |
|---|---|---|---|---|
| **K1. July-sweep qualification** (KI 93) | July ran on an uncommitted producer revision, so its qualification is provisional (Stage B §2.5) | pilot P2's bridge, against an envelope frozen in the pilot DESIGN before P2 runs | the bridge PASSES: July products are reused under R1 | a FAIL is diagnosed and reported to the director before any replacement. A July rebuild (Stage B §7 bracket, 47–142 node-h) needs its own committed grant record |
| **K2. G2 outside `MaRES_0`** | P5 measured one vertical universe. Its completeness deviation \|c_off − 1\| has max 6.76% over the 205 cells, and Flux universes reach 18%. Without a Flux measurement, "no omitted material source" cannot be asserted for Flux | pilot item P2-G2: an off/on pair on one Flux universe, with its quantities re-declared for Flux and frozen before data (pilot record §2) | P2-G2 routes **NOT MATERIAL** or **NOT RESOLVED ABOVE TRAINER NOISE** | **MATERIAL** or **INCONCLUSIVE** goes to the director and from the director to Joseph, before any production grant |

**Stage B exit becomes MET** when K1 passes and K2 passes. Both terminal outcomes go in the pilot REPORT, and
the director reports the stage exit to Joseph (delegation §3.6). The pilot writes no quoted product.

**How G2 is carried is Joseph's decision** (Stage B R10; diagnostics §1). After K2, the director puts a
recommendation to him:
- **if K2 passes:** carry G2 as a disclosed approximation, naming both universes measured, and say that an
  effect below trainer noise is not excluded;
- **if K2 is MATERIAL:** a priced repair.

Repair prices on record:
- **Committed:** Stage B §7 bracket, 43–129 node-h, as revised by diagnostics §3.3 to re-unfolds only with no
  event loops.
- **The 2d closer's re-pricing, labelled as a derivation:** ≈ 35–46 node-h. It multiplies 170 universes by the
  measured P5 "on" charges, 0.204–0.268 node-h, from one vertical universe only. The pilot REPORT reprices it
  from Flux.

## 2. Why K2 is a pilot item rather than a disclosure

The routing rule in P5 DESIGN §7 settles `MaRES_0`. It was never applied to Flux, so it cannot settle Flux.
The plan's Stop rule says "disclosure alone does not close a missing-source defect". The measured P5 pairs cost
0.348 and 0.376 node-h, and a repair on either price above costs at least 35 node-h. The pair is cheap
compared with the decision it informs.

## 3. Rulings made by message during the diagnostics, now recorded

These were sent by SendMessage to the 2d closer and are quoted in the diagnostics REPORT. They are restated
here so they can be cited from `main`.

1. **Seed-43 go-ahead, 2026-10-13.**
   - Before deciding, the director recomputed the actual charge independently from `sacct`: 0.9046 node-h,
     as ElapsedRaw × billing / 256 over every `2dc_B4`/`2dc_B5` row since 2026-10-11.
   - The pre-declared check of P5 DESIGN §7 then read 0.9046 + 1.75 = 2.6546 ≤ 3.0, which PASSES.
   - The pair was approved on two conditions:
     - routing, thresholds and the r1 rule on d̄ stay frozen;
     - a failed or timed-out pair leaves P5 final at seed-42-only NOT RESOLVED, with no retry.
   - This condition differs from P5 DESIGN §7's frozen row "any | INCONCLUSIVE → INCONCLUSIVE". The
     difference was moot, because both seed-43 jobs completed. For P2-G2 the frozen DESIGN row applies, not
     this condition (pilot record §2).
2. **Stale docstring.** `analyze_p5.py` (`8f37fd7f…`, pinned) still says "enforced 1.25 node-h" after the
   DESIGN §5 amendment set the figure to 1.75.
   - The script was left unchanged and the discrepancy recorded in the REPORT.
   - The budget check used 1.75.
3. **1P walltime cap accepted.**
   - 1P was not retried, so the 1.5 × projection rule for retries did not bind it.
   - It kept its first-round 2 h cap against a projected 82 min, a margin of 1.46×.
   - The cap was accepted because 1P kept its one walltime retry under the P4 retry decision.
   - 1P completed in 1:05:07.
   - 1N's retry cap rested on a size proxy, which the REPORT marks as such. 1N completed in 2:44:03 against 6 h.
