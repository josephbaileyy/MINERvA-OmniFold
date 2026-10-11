# AUTHORIZATION 2026-10-10 — the fixed SB1 benchmark package, at most 2.0 charged CPU node-hours

**CITABLE FOR:** the exact text, date and scope of Joseph's authorization to execute the fixed SB1
six-job package. Also its binding to one package commit and one manifest digest.
**NOT CITABLE FOR:** any benchmark result, speedup, production change, estimator equivalence,
adoption or other compute. This record launches nothing itself. The execution record is
`state/next-preparation-20261009/sb1-run/REPORT.md`.

## 1. Binding (named in full, as the grant requires)

| item | value |
|---|---|
| package commit | `d4335d3b9bc2502002f93390f9555d07e134855f` |
| manifest SHA256 (`state/next-preparation-20261009/sb1-prep/manifest/expected-code.json`) | `f060df81338b17069a31a0a2cc7a3430ed81c91ce64de6d6f3d54b80e08eb15a` |
| integrated main the run is based on | `016265cceadbd0f38de31e7f4956377f3d3c5e82` (PR #72) |
| package | `state/next-preparation-20261009/sb1-prep/` (immutable input; byte-identical to the package commit) |
| launch plan | that package's `launch/launch-spec.json`: six jobs H0, UL, SL, J1, C, H1, ceilings 1.69921875 node-h |
| cap | **2.0 charged CPU node-hours on m3246, in total; zero GPU** |

## 2. Scope and exclusions

- **Authorized:** the six jobs of the launch spec, once, at its limits and dependency chain, from an
  isolated detached checkout at the commit that carries this record:
  - H0, the input hashes;
  - UL and SL, the matched pair on `Muon_Energy_MINOS:0`;
  - J1, the vertical `Flux:0` input equality and activation controls;
  - C, the CV replica, profile and CV input equality;
  - H1, the final hashes, accounting and verification.
- **Excluded:**
  - all other compute;
  - retries, requeues and any extra submission;
  - an alternate universe, an extra vertical timing pair, additional fits;
  - any transfer study, sweep or production implementation;
  - a production-driver edit, a Rust rewrite or an estimator change;
  - N2, a KI-85 lift, covariance production, adoption or publication.
- **Stop rule:** stop after 24 elapsed hours from submission if unfinished. Partial evidence is
  preserved, and only this attempt's remaining jobs are cancelled, by verified id.

## 3. The actual authorization

Sent by Joseph as the session prompt on 2026-10-10. The session's first clock reading after receipt
was `2026-10-10T19:58:35Z` (`date -u`, local). The text below is verbatim (sha256 of the text,
newline-terminated: `dec02013f3c1baf69936a32de2d97cbb7829fa422a5decd8b838deaa47294b3f`).

> Please execute the bounded SB1 benchmark after final admission. I authorize only the fixed six-job package below, with a hard total cap of 2.0 charged CPU node-hours on m3246 and zero GPU. No extra transfer study, sweep or production implementation follows automatically.
>
> START: Read AGENTS.md, the campaign review, CURRENT_WORK and governing records, applicable skills, and Q/integration-followup/REPORT.md, where Q = docs/orchestration/state/next-preparation-20261009. Refresh remote main and use an isolated worktree at the integrated pin. The delivered package is prep/sb1-ready-20261009 at b7c951b301ee2142119d3db8fa4201e768f6bf42; any integration repairs supersede that pin and must be inspected. Read its REPORT, both reviews, manifest and launch spec. Confirm the final post-review shell/admission changes were checked at integration; if not, include them in admission review.
>
> The integrated main is 016265cceadbd0f38de31e7f4956377f3d3c5e82 (PR #72). The authorization must name package commit d4335d3b9bc2502002f93390f9555d07e134855f and manifest SHA256 f060df81338b17069a31a0a2cc7a3430ed81c91ce64de6d6f3d54b80e08eb15a in full. The older lane head is historical input, not the admitted package pin. Keep Q/sb1-prep byte-identical to the integrated package, including its tests and report. This assigned prompt supplies the permission that the integration report correctly recorded as absent at its closeout; commit the required authorization before submission.
>
> DECISION: On the real file, does selective branch reading preserve the required inputs and materially reduce I/O, memory and elapsed time for the declared matched lateral comparison?
>
> OWN: Q/sb1-run/ only: REPORT.md, admission, scheduler/input/provenance receipts, compact outputs and verification. The integrated sb1-prep package is immutable input. You may add one dedicated AUTHORIZATION record under docs/orchestration using the repository mechanism; it must quote this grant, name the final package commit and manifest SHA256 in full, and exclude all other compute. Register that exact record through a scoped metadata commit with no competing writer. Do not change shared scientific status, production code, the helper or publication sources. Substantive package redesign terminates this admission and becomes a separately reviewable proposal.
>
> BEFORE SUBMISSION:
> 1. Pin the final package commit and manifest digest. Verify the integrated guard, exact module identities, environment-setup digest, file identities, new output root and no-overwrite rules. Freshly measure allocation/billing, input availability, filesystem headroom and scheduler state. Confirm all six job ceilings, including final verification, sum to <=2.0 charged node-hours.
> 2. Use one fresh read-only reviewer, explicitly authorized, for admission. Its review covers any unreviewed final delta, exact authorization binding, negative controls and complete charge accounting. Maximum one admission review, one final result verification and one focused repair/re-review across this task. No other agents or peer messages.
> 3. Freeze the deployment before launching. Check the XR/deployment records. Use an isolated pinned checkout with the package's verified helper preload where supported. If either run depends on the canonical checkout, never move it while XR or another dependent job is pending/running. Serialize if safe concurrency is not established. Do not wait indefinitely for another session.
> 4. Implement the integration report's orphan-job operator procedure in your own run record or external operator wrapper, without changing the pinned package. Record the submission time window and unique output root. After any failed or ambiguous submission, inspect squeue and sacct and identify all jobs from this attempt using their user, submission time, WorkDir and output/error paths (the launcher binds these to the unique outroot), including jobs whose IDs were not returned. Cancel only this attempt's remaining jobs by verified ID; never cancel every sb1_* job by name alone. Confirm cancellation and count all charges, even when submission.json is absent. Do not assume only a hash job can survive: dependency cleanup also depends on whether its predecessor had already completed. No retry or extra submission is authorized. If job identity or accounting cannot be established, stop and report INCONCLUSIVE with the unresolved jobs explicitly named.
>
> EXECUTION AUTHORIZED AFTER ADMISSION PASS:
> - H0: hash the inputs.
> - UL and SL: the matched all-branches/selective pair on Muon_Energy_MINOS:0 at the frozen settings.
> - J1: vertical Flux:0 input equality and activation controls.
> - C: the CV replica/profile and CV input equality.
> - H1: final hashes, accounting and verification.
> Use the integrated launch-spec limits and dependency chain. Planned ceilings were 1.69921875 node-hours; expected use about 1.19 is a forecast, not a grant beyond the cap. No retries, requeue, alternate universe, extra vertical timing pair or additional fits. Cancel only your own jobs on a cap/provenance failure. Stop after 24 elapsed hours from submission if unfinished, preserving partial evidence and cancelling only remaining SB1 jobs.
>
> Keep S1 input equality mandatory. Apply the frozen P/S1/NC/S2/S3/S4 verdict and report S5 output equivalence and S6 phase coverage separately. Do not relax criteria after seeing results. Trainer nondeterminism, missing telemetry, OOM or failed jobs receive their declared outcomes. A benchmark PASS alone does not establish production equivalence; an unresolved S5 must be resolved before any deployment proposal. Do not turn one lateral timing into a whole-sweep or exact-backend speedup.
>
> FINAL VERIFICATION: The reviewer independently checks raw receipts, hashes and fresh sacct accounting, recomputes charges and performance ratios from operands, and checks the verdict logic rather than merely rerunning the owner verifier. Report queue time separately from charged time and all failures. Preserve compact evidence sufficient to reconstruct the decision; large artifacts get durable identities/recovery paths under storage policy.
>
> BUDGET: 6 active hours including review/delivery; 3 local CPU core-hours, two local compute threads, 8 GiB local RAM, 2 GiB local scratch, <=20 MiB tracked evidence. Cluster settings remain the frozen six-job manifest, <=2.0 CPU node-hours, no GPU. Protect the final quarter of active time for verification. No bulk local copy of the 171-GB file.
>
> TERMINAL: PASS, FAIL or INCONCLUSIVE under the frozen rules, with a separate verification verdict. If admission, access, deployment or resources are unavailable, finish unaffected local checks and deliver the exact blocker without submitting. Push a result branch/PR; do not merge. Recommend at most one next implementation action justified by the profile, with measured versus forecast gains separated. No production-driver edit, Rust rewrite, estimator change, N2, KI-85 lift, covariance production, adoption or publication is authorized.
