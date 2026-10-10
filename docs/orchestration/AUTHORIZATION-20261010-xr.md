# AUTHORIZATION 2026-10-10 — XR, central reproduction and one seed comparison, at most 6.4 charged CPU node-hours

**CITABLE FOR:** the exact text, date and scope of Joseph's authorization to execute XR's five runs. It is
bound to one package commit and one manifest digest.
**NOT CITABLE FOR:** any XR result, seed invariance, a resolution of the 2D pairing, a transfer measurement,
stage T, adoption or other compute. This record launches nothing itself. The execution record is
`state/next-preparation-20261009/two-d-followup/REPORT.md`.

## 1. Binding (named in full)

| item | value |
|---|---|
| package commit | `06eae0fede3508419f235f8cbe61954b33de8497` |
| manifest SHA256 (`state/next-preparation-20261009/two-d-followup/xr/manifest/expected-code.json`) | `fbca1be80d56b09751bcd9f8fbe698ac65786ebe08e21ae04e561e5c73dd06b8` |
| integrated main the work is based on | `016265cceadbd0f38de31e7f4956377f3d3c5e82` (PR #72) |
| package | `state/next-preparation-20261009/two-d-followup/xr/` (`manifest/runs.json` defines the five runs, the inputs, the kinds and the 1e-8 criterion) |
| cap | **6.4 charged CPU node-hours on m3246 in total; zero GPU.** Ceiling 6.375 = 4 exact attempts × 30 h × 12/256 + 3 LightGBM attempts × 1 h × 64/256 |
| admission review | independent read-only reviewer: admission review at `8378ec23` ADMIT WITH CHANGES (`state/next-preparation-20261009/two-d-followup/review/admission-review-8378ec23.md`); the one repair batch, then focused re-review at `06eae0fe` **ADMIT** (`…/review/rereview-06eae0fe.md`) |

## 2. Scope and exclusions

- **Authorized:** X0, X0′ (`X0p`), X1, L0 and L1 as frozen in `runs.json`.
  - They run once each, plus at most ONE extra exact attempt across the exact arms and ONE extra LightGBM
    attempt across both LightGBM arms. Failures and cancellations count.
  - Shared QOS only, at the frozen kinds, from an isolated detached checkout at the commit carrying this
    record.
  - The X1 one-seed comparison is explicitly authorized.
- **Excluded:**
  - stage T and any uncertainty-transfer measurement;
  - statistical-band production, N2, a KI-85 lift;
  - a re-quote, adoption, gate changes, publication edits;
  - full-node substitution, and any other compute.
- **Stop rule:** 72 elapsed hours after the first submission. Only this attempt's unfinished XR jobs are
  cancelled, by verified id. Missing comparisons are INCONCLUSIVE.

## 3. The actual authorization

Sent by Joseph as the session prompt on 2026-10-10. The session's first recorded cluster clock reading
after receipt was `2026-10-10T20:02:47Z`. The text below is verbatim (sha256 of the text,
newline-terminated: `4c469151f28d6f9395514d490530fb47a0296e05169c7f6eaaf961287453d499`).

> Please complete two bounded follow-ups: resolve the methodological scope of your 2D proposal, and implement/review/run XR. I am not accepting the proposed narrower publication claims or commissioning the 303–1,131 node-hour program. XR has separate, conditional execution authority below and need not wait for a positive methodological verdict.
>
> START: Read AGENTS.md, the campaign review, CURRENT_WORK and governing records, applicable skills, and Q/integration-followup/REPORT.md, where Q = docs/orchestration/state/next-preparation-20261009. Refresh remote main and use its integrated pin in an isolated worktree. Your delivered design is prep/two-d-publication-path-20261009 at 2a28a13d49eee9b2b27a92ef805bfa1f9ef00907; read its REPORT, operands and both reviews. If integration is unavailable, complete local preparation from that head but do not deploy or submit.
>
> Integration is now complete at main 016265cceadbd0f38de31e7f4956377f3d3c5e82 (PR #72). Use its corrected records and inspect any newer main delta. The integration report itself granted no compute; this assigned prompt supplies the conditional XR authority below. Do not seek a second routine ruling on X1 or on the already specified cap.
>
> OWN: Q/two-d-followup/: REPORT.md, methodological checks, XR wrapper/launch files, admission/configuration manifests, review and compact results. You may additionally create one dedicated XR AUTHORIZATION record under docs/orchestration, quoting this grant and binding the reviewed implementation/input manifest, with only the scoped metadata registration that this exact record requires. Preserve other owners' registrations. Keep the original two-d-path evidence and reviews immutable. Do not edit the production driver, pinned OmniFold helper, publication, shared scientific registers or generated manifest. Return proposed shared-status updates for their owner. Work under repository commit/push/PR rules.
>
> TASK A — DECIDE WHAT THE PROPOSED CALIBRATION ACTUALLY SUPPORTS:
> 1. Retain the original publication objective. Clearly separate conditional width agreement, repeated-sampling coverage, nuisance-law assumptions and model/regularization bias. A scientifically justified alternative claim is a proposal for me to decide, not a replacement endpoint already approved.
> 2. Derive the target of SD/SM under complementary splits, shared bin mappers, zero-weight rows and fixed full-data purity. Distinguish randomness over splits of one fixed bank from new data/MC productions. Account for covariance of the two estimates and for finite-bank uncertainty that more splits cannot remove. Determine which assurance statements are proven, empirically controlled or assumed. Arithmetic self-tests alone are insufficient.
> 3. Use bounded analytic and synthetic non-training controls, with known answers, to test the proposed uncertainty and sizing formulas. Assess half-to-full scaling and the meaning of an added seed-variation block for a fixed-seed estimator. Do not declare block independence from the synthetic binning mechanism alone. No actual SD/SM unfolds are authorized.
> 4. With read-only saved products and existing construction code, resolve as far as possible the Flux-background anomaly, confounded cross-sweep pair changes and duplicate-looking bands. Specify the missing evidence for selection-complete lateral treatment, flux identity and background-template statistics. Do not silently substitute the old background-frozen sweep as a complete construction. No new universe event loop or unfold is authorized here.
> 5. Deliver an explicit admission matrix: supported claim, remaining assumption, required evidence and minimum next decision. Keep all 205 cells unless a scope change is presented separately for my decision. If the original objective has no feasible route under current inputs, say so; disclosure alone does not discharge a validation requirement.
>
> TASK B — XR, CENTRAL REPRODUCTION AND ONE SEED COMPARISON:
> I authorize XR's X0, X0-prime, X1, L0 and L1 as specified in two-d-path REPORT §10, after the executable package passes independent admission review. This explicitly authorizes X1's one-seed comparison despite the earlier blanket hold; it does not authorize stage T or any uncertainty-transfer measurement. A passing X1 is evidence for that comparison only, not proof of seed invariance or resolution of the whole pairing issue.
>
> Implement a guarded, hash-pinned launcher/wrapper. Keep the historical driver as a pinned record copy, use the existing pinned helper, and preserve the ruling on the production driver's rooted import. Enforce actual module origins and expected digests. Freeze exact argv, working directory, input identities, environment, output cell identities and the 1e-8 reproduction criterion before submission. Every output must be unique, new and outside frozen product paths; test overwrite/path-alias refusals. Check that all run modes execute their intended backend and normalization.
>
> Protect and hash the existing CV input in durable storage before execution if that preservation is still missing. This prompt authorizes one verified copy of the named approximately 2.1-GB CV input, not a bulk archive. Use existing authenticated access and designated storage policy. Missing access or space blocks only the dependent run.
>
> DEPLOYMENT: Prefer a fixed isolated checkout with imports explicitly pinned while preserving the production source. If the rooted-import ruling requires the canonical checkout, I authorize moving it to the reviewed XR implementation commit only after recording a clean checkout and no pending/running jobs that depend on it. Coordinate through the committed SB1/deployment records: never move a checkout while SB1 or another job uses it. If a safe concurrent deployment cannot be established, serialize XR and SB1. No overwriting another session's work or changing a receipt-bound helper.
>
> RESOURCE AUTHORITY: At most 6.4 charged CPU node-hours total on m3246, zero GPU. Verify current allocation, shared-QOS eligibility and actual memory-driven billing before admission. The proposed ceiling is 6.375: at most four exact jobs total, each <=30 h at <=12/256 node billing, and at most three LightGBM jobs total, each <=1 h at <=64/256 node billing. This allows only ONE extra exact attempt across all exact arms and ONE extra LightGBM attempt across both LightGBM arms, not a retry of every run. Count failures and cancellations. No full-node substitution if shared admission fails. Revise the manifest downward or terminate the affected comparisons INCONCLUSIVE if these ceilings cannot be enforced. Recompute the ceiling from actual scheduler settings rather than assuming it.
>
> Stop at 72 elapsed hours after first submission, cancelling only your own unfinished XR jobs if necessary. Record missing comparisons as INCONCLUSIVE. Report maxima and affected cells even when a reproduction tolerance fails; a failure of these available paths is not a proof that every possible reconstruction is impossible. No stage T, statistical-band production, N2, KI-85 lift, re-quote, adoption, gate changes or publication edits.
>
> REVIEW: One fresh read-only reviewer is explicitly authorized. It reviews the methodological derivation and frozen XR package before launch, then independently reproduces consequential XR comparisons from outputs. Maximum one initial admission review, one final numerical verification and one focused repair/re-review across this assignment. Keep the two task verdicts separate: an unresolved method does not block a correctly admitted reproduction experiment. A remaining XR material defect after the review budget prevents launch or leaves its result INCONCLUSIVE. No extra workers or peer messages.
>
> LOCAL BUDGET: 10 active hours including all reviews and delivery; 4 local CPU core-hours, two local compute threads, 8 GiB RAM, 3 GiB new local scratch beyond worktrees, <=20 MiB tracked evidence. Remote setup/reductions must follow cluster policy and be counted; heavy work belongs in admitted jobs, not on login nodes. The named durable input copy and small XR products are additional remote storage. Protect the final quarter of active time for checks/delivery.
>
> DELIVERY: Fixed implementation/input/result refs, exact resource use, independent numerical verification, and separate PASS/FAIL/INCONCLUSIVE outcomes for method, admission and each XR comparison. Push a reviewable branch; do not merge or change scientific status yourself. Complete unaffected tasks on a blocker and deliver the exact reopening requirements, without a routine permission loop. No next experiment starts automatically.
