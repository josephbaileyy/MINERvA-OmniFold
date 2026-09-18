# Readiness report — preparation package for the complete comparison

**Objective, unchanged:** compare our complete configuration against Gregor's intended
**pretrained** method and recommend whichever the evidence supports. **A scratch-only
Tier-A result cannot complete that objective**, and nothing in this package claims
otherwise.

**Updated 2026-09-18 after the calibration milestone.** 81 tests pass; bindings intact.
Two jobs ran and completed: cost calibration (**58527080**) and `E_avail` endpoint
characterization (**58527254**). Results in `CALIBRATION_RESULTS-20260918.md`; receipts
in `receipts/20260918-calibration/`. **Nothing exported, sent or adopted; no threshold
ratified; the optional full Tier-A campaign was not launched.**

**The headline:** `r` is measured at **2.82** (12 tokens) and **4.30** (33 tokens), so the
complete pretrained comparison costs **≈207 GPU-hours against a 600-hour ceiling with
≈16 consumed** — affordable, where before it was unknown within two orders of magnitude.
And the candidate endpoint's reference model is **0.713**, not the pT endpoint's 0.618:
the inherited value would have been wrong by about five times the margin under
discussion.

---

## 1. Executable now — no external dependency

| item | artifact | evidence it works |
|---|---|---|
| reference-model calibration (**a model, not a proven bound**) | `reference_calibration.py` | reproduces the committed `ideal_recovery_percell_truthmass_weighted_by_k` at k=1…4 to **1.1e-16** |
| the demonstration that the pT reference does not transfer | `receipts/reference-calibration.json` | the reference spans **0.017 → 0.973** at k=3 purely by re-weighting |
| the selection rule, total and unambiguous | `selection_rule.py` | 420-point partition sweep; every verdict in the enum reachable; policy-driven recommendations flagged unratified |
| join identity checks I1–I10 | `identity_contract.py` | 14 tests, each against the direction the check must fail in |
| authorization-scope enforcement | `authorization_scope.py` | 6 tests; the existing guard measured at **75 branches against A1's 19** |
| the typed-branch gap, enumerated | `authorization_scope.typed_object_gap` | **exactly 21 branches** need new authorization |
| GPU cost calibration | `calibrate_cost.py`, `sbatch_cost_calibration.sh` | one arm per interpreter; reducer refuses a partial pair; both repos pinned; ≤20 min |
| requests to Agent A and to Gregor | `requests/DRAFT-*.md` | drafted, **not sent** |

**Implementable next with no external dependency, not done here:** the Keras port of
PET2-small and its P-1…P-6 checks (forward, gradient, weight-update — all float64 on
CPU), and the `OI-125` fold-forward recorder (~8 lines, new file, **not** an edit to the
pinned driver). Both are ordinary implementation work; neither waits on anyone.

---

## 2. Externally blocked

| blocker | owner | blocks |
|---|---|---|
| **R-1** three event-key branches `ev_run/ev_subrun/ev_gate` on the dump trees | **Agent A** | the entire typed representation. Draft ready |
| **R2** pretrained checkpoints `best_model_pretrain_{s,m}.pt` + sha256 + licence | **Gregor** | **the objective itself** — without them only his scratch arm runs, which does not test the transfer claim his paper makes. Draft ready |
| **R1** which commit and model the paper reports | **Gregor** | whether any result speaks about his *published* method. Draft ready |
| **R3** his `E_avail` definition | **Gregor** | any numeric comparison against his reported values. Draft ready |
| **R4** authorization to read the 21 typed-object branches at scale | **Joseph** | building the typed representation |
| ~~**E-1/E-2**~~ | ~~Joseph~~ | **DONE** — job 58527254; the acceptance map, displacement field and reference model are measured |
| **U1–U8** ratification of the endpoint variable, binning, reference value, `f`, δ, δ_switch | **Joseph** | the freeze |
| **OI-71** disposition | **Joseph / PET lane** | whether `VL100` may be quoted at all |

---

## 3. The smallest next authorization

**Both of the previous two are done.** The `E_avail` characterization ran (58527254) and
the GPU calibration ran (58527080), so the endpoint has a calibrated reference model and
the objective has a price.

**The smallest next authorization is now a scientific ratification, not compute:
U1–U8**, and in particular U3 — whether the scoring domain stays 1-D `E_avail` or becomes
2-D. The measurement surfaced a specific reason to consider 2-D: a 1-D projection
**averages over** (pT, p‖) cells whose acceptance spans 0.004 to 0.89, so poorly accepted
regions stay in the truth mass but stop being resolved. That is a scientific choice and
it is outside this milestone's scope.

**Not blocked on ratification, and the obvious next implementation:** the Keras port of
PET2-small with checks P-1…P-6, and the `OI-125` fold-forward recorder. Neither needs an
authorization, GPU time, or a resolved threshold.

**Still blocking the objective itself:** the pretrained checkpoints (R2). Without them
only his scratch arm runs, which does not test the transfer claim his paper makes.

---

## 4. Three corrections this package makes to my own earlier work

1. **"Every typed field is already inside the A1-authorized branch set" — false.** It is
   inside the fixed-source smoke's `REQUIRED_BRANCHES`, a broader clearance. A1 covers
   blob and prong **counts**, not values. 21 branches need new authorization.
2. **The existing branch guard cannot catch an authorization overrun** — it checks a
   75-branch superset. The read that ran was inside A1; the guard is what is defective.
3. **The pT reference value, scatter and tolerance cannot be inherited**, and the reason
   is now quantitative rather than cautionary: the reference moves over 0.017–0.973 with
   the weighting alone. It is a reference **model, not a proven bound**.
4. **Binning must not be chosen to hide poorly accepted regions.** An earlier draft of
   mine said the binning should avoid prior-dominated bins; that would raise the reference,
   flatter both arms, and remove the region where a better hadronic representation is most
   likely to matter. Low-acceptance bins stay in, and results are stratified by
   acceptance against each stratum's own reference.

---

## 5. Budget position, stated plainly

At planning values `c = 1.5`, `r = 6` (both **unmeasured**), an arm-pair evaluation is
10.5 GPU-h. **Tier A with retries is ~211 GPU-h against 274 remaining — about
three-quarters of the ceiling — and it cannot complete the objective.** Completion at the
typed representation is **not costed**, because `c′` and `r′` at the raised token count
are unmeasured and it is blocked on R-1, R2 and a dump re-run.

The sequence that respects the budget is therefore: **stage 2 first**, then decide whether
Tier A is worth 211 GPU-h *given what stage 2 says about completion's price*. Committing
to Tier A before measuring `r` would be spending most of the remaining allocation on the
optional half.

---

## 6. Scope

PET remains method development. Nothing here is a publication adoption, an uncertainty
product, a central-value change, a Gate-6 action, or a discharge of `OI-71`. No cluster
job was submitted, no production export made, no message sent, and no scientific
threshold ratified.
