# AUTHORIZATION 2026-10-11 — XR on the Linux runtime: amendment of the exhausted XR recovery grant (repair, two preflights, the five runs)

**CITABLE FOR:** the exact text, date and scope of Joseph's amendment of the XR recovery grant. It covers:
- a new XR launch package for the Linux runtime under `state/next-preparation-20261009/xr-linux/xr/`;
- one fresh read-only reviewer, with at most two focused repair/re-review cycles;
- at most two in-allocation preflight/fixture jobs;
- the five original XR runs, after admission and a passing preflight.

It is bound to one package commit and one manifest digest.

**NOT CITABLE FOR:**
- any XR result, seed invariance, or a resolution of the 2D pairing;
- an uncertainty-transfer measurement, covariance production, N2, a KI-85 lift, a re-quote, a publication adoption or the reopening of a terminal campaign;
- other compute.

This record launches nothing itself. The execution record is
`state/next-preparation-20261009/xr-linux/REPORT.md`.

## 1. Binding (named in full)

| item | value |
|---|---|
| package commit | `60bd68c05ad89116ac5a4bca5f925f8da1240e4e` |
| manifest SHA256 (`state/next-preparation-20261009/xr-linux/xr/manifest/expected-code.json`) | `5d2f5955464c3be0117f36f35240b7626a719b6a985350e1bda6c7d99ff850b0` |
| amends | [`AUTHORIZATION-20261011-xr-recovery.md`](AUTHORIZATION-20261011-xr-recovery.md) (package `07428e5dec9fecd2e1148d8a2bdabc139a35138f`): its package, preflight allowance, review budget and execution window. The first grant [`AUTHORIZATION-20261010-xr.md`](AUTHORIZATION-20261010-xr.md) and both earlier packages, outroots and failure records are unchanged |
| package | `state/next-preparation-20261009/xr-linux/xr/` (new). `manifest/runs.json` defines the preflight PF and the five runs, the inputs, the kinds, the 1e-8 criterion, the comparisons and the control; the runs, references, criterion, comparisons and control are those of `07428e5d`. X0p executes the frozen two-d-followup record copy of the `d1bc8813` driver (sha256 `447288e2…`); X0, X1, L0 and L1 execute the 2D driver at sha256 `3cc5adc7306b3043c2fd147602d866b90162644523b64060462aa4d934766933` (last changed in `355174fe64309811ca6a0d79ced46f2a71f653a9`), the pre-selective-I/O driver of integration §8 |
| output namespace | `/pscratch/sd/j/josephrb/xr-linux-20261011` (new; the outroots `xr-two-d-followup-20261010` and `xr-recovery-20261011` are kept unchanged and refused by `draft`) |
| job names | `xrl_<RUN>_a<N>` |
| cap | **6.4 charged CPU node-hours on m3246 in total, cumulative with every earlier XR job: the five `xr_*` and `xrr_PF_a1`, 2132/921600 = 0.002313368055555556 node-h, recomputed from sacct by every ledger; zero GPU; no full-node substitution** |
| planned ceiling | 6.385125868055556 node-h: prior 0.002313368055555556; 2 preflights × 5 min × 12/256 (0.0078125); 4 exact × 30 h × 12/256 (5.625); 3 LightGBM × 1 h × 64/256 (0.75) |
| window | 72 h from the first preflight submission |
| admission review | **ADMIT** at `60bd68c0` (`state/next-preparation-20261009/xr-linux/review/admission-review-60bd68c0.md`, verbatim): 0 MATERIAL; E-1 MINOR (the accounting of a repaired package's second preflight, to be checked in any focused re-review); notes E-2 to E-4, A-1 to A-4, B-1, C-1, D-1. No repair cycle has been used |

## 2. Scope (as granted; the verbatim text is §3)

- One fresh read-only reviewer: an admission review before the cluster preflight, a focused review of
  any repaired package before its retry, and the final independent numerical verification; at most two
  focused repair/re-review cycles in total.
- At most two preflight/fixture jobs (shared QOS, ≤ 5 min, ≤ 12/256 billing each); the second only
  after a diagnosed infrastructure repair and its review. Tiny synthetic fits are permitted in the
  preflight and are never scientific outputs.
- After a passing preflight: L0 first; X0, X0p, X1 and L1 only after L0 has a complete, comparable
  guarded receipt. At most 4 exact jobs (≤ 30 h, ≤ 12/256 each) and 3 LightGBM jobs (≤ 1 h,
  ≤ 64/256 each), retries included; spare attempts only for diagnosed infrastructure failures. A
  comparison failure is not a reason to retry or tune.
- At the window's end, only this assignment's verified unfinished job ids are cancelled; missing
  comparisons are INCONCLUSIVE.

## 3. The instruction, verbatim

Received in the xr-linux session on 2026-10-11 (UTC). SHA-256 of the text between the fences (UTF-8,
with a final newline): `3e52f52f5b84f39f656cc05aa6394f6fe8b2ab3d431d2d54819d91466181c744`.

```text
Please complete a bounded Linux-runtime repair and execution of the existing XR reproduction experiment. I authorize the work and resource envelope below. Do not redesign the scientific comparisons.

BASELINE AND REQUIRED READING

The evidence integration completed through PR #77 at canonical main:
3892e769043cddebfd58ec19e1ab1a567eb01784

Refresh remote main and reconcile subsequent changes before starting. Use an isolated worktree and a separately pinned cluster deployment. Preserve unrelated local files.

Read:
- AGENTS.md
- docs/orchestration/CAMPAIGN-REVIEW-20260929.md
- docs/CURRENT_WORK.md and the relevant governing records

Let Q = docs/orchestration/state/next-preparation-20261009.
Read the reports and routed reviews under:
- Q/two-d-followup/
- Q/xr-recovery/
- Q/sb1-run/
- Q/xr-sb1-integration/REPORT.md, especially §8

DECISION

Can the original five XR runs, with unchanged inputs, estimator settings, references and comparison rules, answer the central-reproduction and one-seed questions?

An infrastructure blocker or an inconclusive scientific comparison is a valid terminal outcome. Successful reproduction is not required to complete this assignment.

AUTHORITY AND OWNERSHIP

Own Q/xr-linux/, including REPORT.md, a new launch package, tests and receipts.

You may create a uniquely named committed AUTHORIZATION- amendment under docs/orchestration/, quoting this instruction and binding the reviewed package commit and manifest. You may add the dedicated authorization's required override and routing rows, as allowed by integration §8.

This dispatch amends the exhausted recovery grant's package, preflight allowance, review budget and execution window. Its TWO-preflight allowance supersedes the older report's one-preflight proposal.

Preserve all earlier packages, authorizations, outputs and failure records. Do not edit:
- Q/two-d-followup/xr/ or the earlier lane records;
- shared scientific status or publication sources;
- production drivers or the pinned OmniFold helper;
- guard permissions;
- SB1's packages or outputs.

Other shared-register and binding-inventory changes belong to integration. Deliver exact proposed changes for that owner.

CONCURRENT WORK

A separate session may implement selective reading in the supported 2D driver.

XR must remain bound to the pre-selective-I/O driver identified by integration §8, digest prefix 3cc5adc7. Verify its full digest and source commit. Pin it from the integrated baseline or use a verified execution-only record copy, consistent with the existing XR mechanism.

Do not silently adopt the concurrent driver change, move the canonical cluster checkout, or modify another session's deployment.

REPAIR AND VERIFICATION

1. Replace the environment inspection that launches ldconfig. Keep the guard strict. Loaded-library paths and thread environment may supplement evidence but do not by themselves establish effective estimator thread counts.

2. Establish and record effective threading consistent with the frozen XR configuration. Address the known loky/lscpu fallback without silently changing estimator settings.

3. Exercise the entire real Linux guarded path:
   allocation parsing, admission, environment checks, driver/helper loading,
   core-count setup, fit recorder, thread checks, input rechecks and fit/predict.

4. Exercise the package's end-to-end tiny fixtures for all five configurations. Stub-only tests and macOS success are insufficient. Tiny synthetic fits are explicitly permitted in the bounded preflight; they must never be treated as scientific outputs.

5. Cover actual scheduler formats and repair the outstanding ledger-header handling defect. Demonstrate successful guarded execution and meaningful refusal controls.

6. Freeze a new package, manifest and output namespace. Preserve the original five scientific runs, comparisons, 1e-8 criterion, negative control, references, cell identities and missing-result rules.

REVIEW AND RELEASE

One fresh read-only reviewer is authorized. Record the owner/reviewer setup and actual model identities; do not claim unavailable cross-provider independence.

Require:
- admission review before cluster preflight;
- focused review of any repaired package before its retry;
- final independent numerical verification.

Allow at most two focused repair/re-review cycles across this assignment. Do not reopen the completed methodological review.

Exercise Linux fixtures locally in the frozen environment if available. Otherwise use the first admitted cluster preflight. Do not run training on a login node.

Permit at most TWO preflight/fixture jobs, each at most five minutes and at most 12/256 node billing. After the first fails, one diagnosed infrastructure repair and a reviewed second attempt are allowed.

No scientific run may start until the complete preflight passes. If adequate fixture coverage cannot fit this envelope, finish with the precise blocker and a costed next decision.

After preflight passes:
- Run L0 first.
- Require a complete, comparable guarded receipt before releasing X0, X0p, X1 and L1.
- Follow the frozen outcome rules. A scientific comparison failure is not permission to tune or retry for a better result.

RESOURCE LIMITS

The cumulative ceiling is 6.4 charged CPU node-hours on m3246, INCLUDING all prior XR attempts, fixtures, preflights, failures, retries and remote verification.

Recompute previous spending from scheduler records. The integrated total is:
0.002313368055555556 node-hours.

Maximum new execution:
- Two preflight/fixture jobs: <=5 minutes, <=12/256 billing each.
- Four exact jobs total: <=30 hours, <=12/256 billing each.
- Three LightGBM jobs total: <=1 hour, <=64/256 billing each.

Scientific job totals include retries: at most one extra exact attempt across the three exact arms and one extra LightGBM attempt across the two LightGBM arms. Spare attempts are for diagnosed infrastructure failures only.

The stated ceilings total approximately 6.3852 node-hours including prior spending. Re-measure actual allocation and billing, and enforce the cumulative cap. No GPU, full-node substitution or automatic resource expansion.

Use a new 72-hour execution window beginning with the first preflight submission. At expiry, cancel only this assignment's verified unfinished job IDs. Record missing comparisons as INCONCLUSIVE.

Local limits, including review and delivery:
- Ten active hours, excluding scheduler waiting.
- Six CPU core-hours.
- Two compute threads.
- 8 GiB RAM.
- 3 GiB scratch beyond worktrees.
- 20 MiB tracked evidence.

Protect the final quarter of active time for verification and delivery.

DELIVERY AND TERMINATION

Independently reproduce consequential comparisons from output histograms and verified references. Recompute charges from scheduler operands. Report admission, preflight, execution and each comparison separately.

Push a reviewable branch/PR; do not merge. Preserve required receipts durably through the repository's registration process. Do not hide bindings to bypass a gate. Complete unaffected work when a dependency is unavailable.

PASS, FAIL and INCONCLUSIVE are valid terminal outcomes. No further routine permission is needed within this grant. If a hard limit or material unresolved finding prevents completion, deliver the evidence, consequence and exact next decision, then stop the dependent work.

Nothing authorizes uncertainty-transfer measurements, covariance production, N2, lifting KI-85, a re-quote, publication adoption or reopening terminal campaigns.
```
