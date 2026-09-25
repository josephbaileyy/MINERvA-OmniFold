# AUTHORIZATION 2026-09-25 — `OI-192` diagnosis and bounded estimator development (campaign `s5e`)

**CITABLE FOR:** the exact text, date and scope of Joseph's authorization of the `OI-192` diagnosis and
bounded estimator development; the identity of the attached goal file; the scoped supersession mapping;
the carried-forward CPU budget arithmetic. **NOT CITABLE FOR:** any scientific result, cause, grade,
adoption, measured cost of new work, or publication readiness. It launches nothing. Executor choices
live in the campaign contract [`state/s5e/contract.json`](state/s5e/contract.json) and the campaign state,
not here.

## 1. The actual authorization

Sent by Joseph as a Claude Code `/goal` on **2026-09-25** to session
`8ad4e62d-1079-4f28-aa0b-dccf6476a48b`. The attached file
`docs/orchestration/GOAL-20260925-oi192-estimator-diagnosis.txt` (untracked in the shared main checkout)
carries mtime 2026-09-25 15:25:20 PDT (22:25:20Z). The session's first clock reading after receipt was
`2026-09-25T22:27:05Z` (`date -u` on login23), so the message was sent between those two instants. There
is no separate handoff attachment. The text below is verbatim, line breaks as sent. It is byte-identical
to the attached file: `diff` of the received text against the file exits 0, and both hash to blob
`23ed4e12…`.

> Complete OI-192 diagnosis and bounded estimator development. The objective is a
> verified diagnosis and candidate assessment, not a guaranteed working estimator.
> Failure or inconclusive diagnosis is a valid terminal disposition.
>
> Read AGENTS.md and routed instructions, then docs/orchestration/:
> - OUTCOME-20260925-s5n-stage1-development-fail.md
> - CAMPAIGN-s5n-20260925-index.md and its contract
> - AUTHORIZATION-20260925-negweight-refined-successor.md
> - PLAN-scalar5d-reportable-uncertainties-and-inference.md (historical; unchanged).
> Read OI-192, VL151-VL152, KNOWN_ISSUES 75, 77-79 and routed independent reviews.
> Refresh heads, worktrees, scheduler and resources. Preserve concurrent work.
>
> I authorize the diagnostics below, necessary code repairs, a bounded scan and
> candidate changes to iterations/stopping, classifier capacity or
> regularization, and missed-event regression. This supersedes the previous
> prohibition on those changes FOR THIS CAMPAIGN ONLY. Keep negweight-refined as
> the candidate background treatment; permit targeted refinement/resampling repairs.
> No PET, architecture search, historical regrading or general cleanup.
>
> Commit this actual authorization, date/blob, contract, state and budget before
> implementation. Use an isolated worktree
> from current origin/main and fresh outputs. Preserve historical evidence and
> reuse valid recovery checks and diagnostics.
>
> Budget: at most 60 additional billed CPU node-hours including verification; no GPU
> allocation or bulk storage expansion. Also limit spending to the prior cumulative
> CPU envelope's unspent balance and 10% of current uncommitted CPU allocation after
> reservations. Carry prior charges forward. Reserve 20% for verification. Continue the
> campaign-specific replacement of R5 task-hour/calendar ceilings for this scope;
> verify admission without globally bypassing guards. At most two CPU nodes.
>
> 1. Diagnose first, initially capped at 10 CPU node-hours. Reproduce the decisive
> E_avail and repaired q3 departures on matched driver and NPZ paths. Reconcile
> coordinates, precision, weights, masks, normalization, seeds and refinement.
> Separate pipeline differences from scientific effects. Measure forward-fold
> agreement, step-1 and step-2 response, missed-event regression and a small fixed
> iteration scan. Check departure observability after detector response. Isolate
> the nominal background-related joint-cell bias. Do not name a cause without evidence.
>
> 2. Choose at most TWO supported candidates and ONE development revision each.
> Freeze and cost them first; stop if none is justified. Check background-
> inclusive nominal closure, generator-anchored E_avail departures, repaired q3
> departures, seed stability and statistical-width calibration. Use additional
> withheld physical deformations and genuinely fresh seeds for final assessment;
> development examples alone cannot qualify a candidate. Freeze useful-width and
> acceptance criteria before assessment. Validate the same estimator and intervals
> intended for data, including declared background fluctuations and correlations.
> Do not repair failure by inflating errors, choosing favorable seeds, or silently
> weakening a gate. Keep model dependence distinct from statistical uncertainty.
>
> 3. Obtain independent read-only operand-level review and reverify repairs. Commit
> and push code, tests and evidence. Update affected deliverables, build/synchronize
> note, primer and paper in both repositories and verify heads. No full covariance
> production, large coverage campaign, adoption,
> joint inference, release tagging, deposits or submission in this goal.
>
> Checkpoint, monitor owned jobs and avoid duplicates. Deliver diagnosis, candidate
> results/limits, verification, spend, heads and a costed next validation design
> with sample-size/assurance calculations. Report the four status fields separately.
> Mark this goal complete
> when its bounded assessment and delivery are finished, even if all candidates
> fail; do not claim the larger publication objective is met.

## 2. Identities (measured 2026-09-25T22:30Z)

| document | Git blob | SHA-256 | state |
|---|---|---|---|
| [`GOAL-20260925-oi192-estimator-diagnosis.txt`](GOAL-20260925-oi192-estimator-diagnosis.txt) | `23ed4e1205024029cc6646e8c0396bd585ca6feb` | `ed3c77ffdf12a3673705695f8cc5eaffa3ea67471021a999ebe96b5e59a510f7` | committed in this commit, byte-identical to the untracked copy in the shared checkout and to the received `/goal` text |
| [`PLAN-scalar5d-reportable-uncertainties-and-inference.md`](PLAN-scalar5d-reportable-uncertainties-and-inference.md) | `8b0617b6e044a55a9b5870b46e5d90a15a6ced7a` | — | historical approved plan; `git hash-object` at `35f8757b` equals the approved blob; **not edited** |
| [`state/s5n/contract.json`](state/s5n/contract.json) | — | — | the predecessor's frozen contract; **not edited** |

`git log --all` over the goal file's path is empty: it had no commit before this one. Durable starting
heads, re-measured: canonical `origin/main` = `35f8757b231f524e52c060e4db93af87420af4d9` (`git fetch`,
2026-09-25T22:2xZ); standalone note `main` = `a1027e6449f60db55f83d8f6806995f633131479` (the s5n closeout's
recorded head; re-verified by `git ls-remote` at the deliverables step). This work runs in the isolated
worktree `MINERvA-OmniFold-oi192`, branch `campaign/oi192-diagnosis-20260925`, created from that
`origin/main`. The shared main checkout (`c496135f`, behind `origin/main`, with untracked files from
other lanes) is not touched.

Concurrent work observed at start (preserved, not touched): Slurm jobs `58880337`, `58880338`
(`pfd-chain`, GPU debug) and `58880339` (`pfd-inter`, GPU interactive), then further `josephrb` jobs on
`m3246_g` and one pending `shared` job on `m3246` (`58880449`): all other lanes' work. Twenty-odd sibling
worktrees exist (PET, pfd, KI and audit lanes); none is used.

## 3. Scoped supersession mapping (this campaign only)

Every displaced record stays in place, unedited, and keeps governing everything outside this campaign.
This mapping cannot expand the delegation in §1.

| # | displaced record / clause | its operative text (abridged; open the record) | newly authorized action, this campaign only | explicitly unchanged |
|---|---|---|---|---|
| E1 | `docs/OPEN_ITEMS.md` `OI-192`, *"decision reserved to Joseph"* / *"a decision by Joseph"* | the next increments wait on Joseph | increments (2) diagnosis, (3) bounded estimator development, the C3 mechanism and driver/npz parity are executed as campaign `s5e-20260925` under this record; increment (1), an unfolding-model uncertainty component, is **not** produced here (no covariance production) and is costed as a next step | `OI-192`'s filer, scope and evidence route |
| E2 | the s5n contract `family.revision_rule` / `not_allowed` (*"it may not change the classifier architecture or hyperparameters by search"*; iterations fixed at 5), s5n outcome §5 (*"Changing iterations or classifier capacity is outside this delegation and is Joseph's decision"*), `KNOWN_ISSUES.md` 77 blocker (*"an estimator change (iterations, capacity) is outside every standing delegation"*) | the estimator's iterations, capacity and missed-event treatment are frozen | diagnostics; necessary code repairs; a bounded, predeclared iteration scan; and candidate changes to **iterations/stopping, classifier capacity or regularization, and missed-event regression**, plus targeted refinement/resampling repairs; background treatment stays `negweight-refined` | no PET; **no architecture search** (no change of classifier family, no search over hyperparameter grids beyond the ≤ 2 frozen candidates and their one revision each); no historical regrading; no general cleanup |
| E3 | plan `8b0617b6` §6 family/revision limits as exhausted by s5c and the s5n limits (ONE family, TWO revisions, s5n authorization N2) | no further family or revision | **at most TWO candidates**, each frozen and costed before its first run, with **ONE development revision each**; final assessment on genuinely fresh seeds and withheld physical deformations | s5c F1–F3 and s5n family `N` verdicts; none is reopened or re-graded |
| E4 | the s5n budget (caps 325.184 CPU / 115.2138 GPU node-h) | the successor envelope | a separate campaign cap of **60 billed CPU node-h** including verification, also held to the unspent prior cumulative envelope and to 10% of the uncommitted allocation after reservations (§4); **no GPU pool**; prior charges carried forward | the s5c and s5n ledgers and receipts |
| E5 | `AUTHORIZATION-20260924-scalar5d-campaign-activation.md` §3 rows S1–S2, as carried forward by s5n N4 | R5's calendar stop and task-hour ceilings displaced for the scalar-5D campaigns | **carried forward to this campaign**: admission and accounting through `nd-unfolding/s5c_meter.py` bound to this campaign's own budget, ledger and `s5e-` job prefix, verified in native billed units before any compute | `r5_meter.py` and every guard that calls it; S2's retained clauses (reservation = enforced cap × tasks; no automatic requeue; ≤ 2 infrastructure retries per task; ≤ 1 corrective resubmission per stage after a diagnosed code defect) |

**Retained as binding:** plan `8b0617b6` §§3, 5–7 and 9–11 as scientific gates and protections (20%
verification/repair floor; 2-CPU-node concurrency; *"do not use independent validation failures to tune
and re-test on the same sample"*); the adopted trunk `3d7465f6…` with its byte-scoped §6.4 exception and
four travelling measurements; Joseph's `(B)`; the s5c dependencies D4 (protected namespace), D6 (shared
cluster checkout not moved), D7 (outward acts), D8 (no `git pull` in the shared main checkout). PET stays
diagnostic. `AGENTS.md` *Next-action discipline* item 3 is satisfied for this campaign's compute by this
record; every compute receipt still names the quantity it measures and what it cannot authorize.

## 4. Budget (native billed units)

Measured 2026-09-25T22:30:34Z (`iris`, `squeue -h -r -A m3246,m3246_g` all users, `showquota`,
`hpssquota`, `sacctmgr` QOS factors; raw capture
[`state/s5e/allocation-measurement-20260925T2230Z.txt`](state/s5e/allocation-measurement-20260925T2230Z.txt))
and 2026-09-25T22:30:51Z / 22:30:52Z by `s5c_meter.py measure` on the s5c and s5n ledgers (receipts
[`state/s5e/prior-ledger-s5c-20260925T2230Z.json`](state/s5e/prior-ledger-s5c-20260925T2230Z.json), ledger
`4f89112e…`, and
[`state/s5e/prior-ledger-s5n-20260925T2230Z.json`](state/s5e/prior-ledger-s5n-20260925T2230Z.json), ledger
`5e3fa429…`; no admission open in either).

| limit | arithmetic | CPU node-h |
|---|---|---:|
| (a) explicit cap | §1 | **60.000** |
| (b) unspent prior cumulative envelope | 345.27 − (20.0859 s5c + 4.6011 s5n = 24.6870) | 320.583 |
| (c) 10% of uncommitted CPU after reservations | 0.1 × (20000 − 16571.7 − 0.1406) = 0.1 × 3428.16; the one CPU reservation is `58880449`, `shared`, 18 CPUs × 1 h = 18/128 node-h | 342.816 |
| **campaign cap** | min(a, b, c) | **60.000** (binding: the explicit cap) |

Stages: **diagnosis ≤ 10.0** (§1 item 1, "initially capped"); **verification/repair ≥ 12.0** (20% of
60); the remaining 38.0 is **unallocated** until a candidate is frozen and costed by a contract amendment
and a budget revision with a ledger `rebind`. GPU: **0** (no GPU allocation). Storage: no bulk
expansion; this campaign's namespace `/pscratch/sd/j/josephrb/s5e-20260925/` is capped at 20 GiB of new
files (pscratch 16.38 of 20.00 TiB used). Concurrency: at most 2 CPU nodes over every open admission.
These balances are not new grants beyond §1.

## 5. What this activates and what it does not

| activated | not activated |
|---|---|
| diagnosis items of §1.1 on development seeds and deterministic (Asimov) constructions; necessary code repairs with regression tests | any claim of cause without the contract's evidence rule |
| ≤ 2 frozen, costed candidates in the authorized dimensions, one development revision each; final assessment on fresh seeds and withheld physical deformations at development scale | architecture search; PET; a large coverage campaign; full covariance production; adoption; joint inference |
| the same estimator and σ construction run on the real data as a pipeline validation (method sensitivity only) | a corrected central value; any change to the adopted trunk or to s5c/s5n/Z grades |
| independent read-only operand-level review; commits and pushes to `origin` and `analysis-note`; deliverable updates stating the findings | force-push or history rewrite; release tags; deposits; submission; external messages |
