# Evidence/Writeup Audit: Round 2 Final

I am operating as the durable `evidence_ablation_auditor` for session `4be5058b-7e1a-49f2-a102-04fe530e5f3a`. I have completed a read-only audit of branch `codex/gregor-pet2-omnifold` at commit `d2bead0f`, comparing the executed campaign and writeup against the preregistration rules.

## 1. Adversarial Challenge & Findings

**Finding 1: Pilot Power and Event Count Limitation**
*Classification:* **MAJOR**
*Evidence:* `final_campaign_summary.json` lines 32-34 show `training_events: 100000` for the synthetic matched matrix. The preregistration and feature contract anticipated a 2M event subsample.
*Challenge:* Training on 100k events significantly reduces the statistical power to resolve small ($\mathcal{O}(1\%)$) architectural benefits. The fact that "every matched synthetic arm failed the preregistered absolute density-ratio closure gate" and that variations were "seed-inconsistent" may be an artifact of this low-statistics regime rather than intrinsic representation failure. The assessment prose states the effects were below threshold, but does not explicitly caveat that the pilot was vastly underpowered compared to the production target.

**Finding 2: TensorFlow Superiority Disclaimer**
*Classification:* **CLEAR**
*Evidence:* `GREGOR_PET2_OMNIFOLD_ASSESSMENT.md` lines 19-20 and 388-390.
*Challenge:* Does the writeup imply TF is better? No. The writeup explicitly guards against this: "This is a conservative evidence decision, not a finding that the current architecture is intrinsically superior" and correctly assigns the TF default decision to "continuity".

**Finding 3: Evidence Compartmentalization**
*Classification:* **CLEAR**
*Evidence:* `final_campaign_summary.json` correctly segregates `synthetic-fixture`, `recoil-input-pilot`, and `public-gregor-dataset`. Lines 314-318 of the assessment prohibit cross-framework B-vs-C conclusions.
*Challenge:* Did numerical comparisons bleed across boundaries? No. The prose successfully respects the `b_to_c_architecture_claim_permitted: false` flag.

**Finding 4: Representation Isolation & Truth-Freezing**
*Classification:* **CLEAR**
*Evidence:* `GREGOR_PET2_OMNIFOLD_ASSESSMENT.md` lines 305-318 and `final_campaign_summary.json` lines 28.
*Challenge:* The mid-campaign discovery that Step-1 representation changes were bleeding into Step-2 was properly caught. The pre-fix runs were quarantined, and the final results used the `truth_frozen_pet2_matrix` commit to strictly isolate the Step-1 detector observable effects.

**Finding 5: Handling of Unavailable G2 Data and Gregor Checkpoints**
*Classification:* **CLEAR**
*Evidence:* `GREGOR_PET2_OMNIFOLD_ASSESSMENT.md` lines 30-37, 131-134, and 405-420.
*Challenge:* The lack of G2 full-schema inputs, unverified Gregor checkpoint licenses/hashes, and the MC-only nature of the public dataset are clearly stated as missing requirements that defer deployment, rather than silently waived checks.

## 2. Preregistration Scorecard

| Preregistration Rule | Score | Notes |
| :--- | :--- | :--- |
| 1. Population, seeds, budgets, optimizer matched | PASS | Common seeds (101, 202, 303), fixed hyperparameters across C-E matrix. |
| 2. Quantitative closure, ESS, tails evaluated | PASS | `log_ratio_rmse`, global/tail ESS, and weight percentiles collected. |
| 3. Gates applied without outcome selection | PASS | All arms failed the absolute gate; rules enforced blindly. |
| 4. D/E isolate representation, truth-frozen | PASS | Truth-frozen commit utilized, previous runs quarantined. |
| 5. Strict evidence compartmentalization | PASS | TF vs PyTorch and XPS2 vs Synthetic cleanly partitioned. |
| 6. Prose categorizes inclusion/neutral/harmful | PASS | Explicit decision table used in Section 13. |
| 7. Missing G2 / checkpoints explicitly stated | PASS | Documented as primary reason for deferrals. |
| 8. Quoted numbers trace to ledger / JSON | PASS | Summary JSON exactly matches assessment prose. |

## 3. Evidence/Writeup Verdict

**VERDICT: CONDITIONAL PASS**
The campaign execution and the decision logic are incredibly rigorous, strictly adhering to the preregistration rules. The isolation of the truth-freezing bug and the refusal to declare a false winner between TF and PyTorch based on uncalibrated frameworks represents excellent auditing. However, the writeup omits a critical limitation regarding the statistical power of the synthetic pilot.

## 4. Exact Required Revisions Before Handoff

1. **Update `docs/GREGOR_PET2_OMNIFOLD_ASSESSMENT.md`:**
   In Section 1 and Section 9, explicitly state that the matched synthetic matrix was run on a 100,000-event pilot sample (rather than the anticipated 2M production statistics). Note that this limited statistical power likely contributed to the failure to pass the absolute closure gate and the seed-inconsistency of small representation differences.

## 5. Unresolved Dissent

*   **Pilot Scale Validity:** I dissent from treating the absolute closure gate failure as a property of the *architectures* themselves. At 100k events, the noise floor is too high to definitively conclude that rich features (E, D) are neutral or harmful; we can only conclude they are unresolvable at this pilot scale.

## 6. Same-Session Final Reassessment Checklist

- [ ] Does the assessment text acknowledge the 100k-event limit?
- [ ] Does it clarify that the pilot power was insufficient to resolve $\mathcal{O}(1\%)$ differences?
- [ ] Do all other evidence boundaries, decisions, and quarantines remain intact?
