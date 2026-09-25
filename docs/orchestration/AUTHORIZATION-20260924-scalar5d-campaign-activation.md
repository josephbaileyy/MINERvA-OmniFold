# AUTHORIZATION 2026-09-24 — activation of the scalar-5D reportable-uncertainty and inference campaign

**CITABLE FOR:** the exact text, date and scope of Joseph's activation of
[`PLAN-scalar5d-reportable-uncertainties-and-inference.md`](PLAN-scalar5d-reportable-uncertainties-and-inference.md)
and of the *Complete estimator goal prompt*; the identities of the approved versions; the scoped
supersession mapping plan §2 requires; the two additional authorizations D2 and D3.
**NOT CITABLE FOR:** any scientific result, grade, adoption, measured cost, or publication readiness.
It launches nothing. Later delegated choices live in the campaign contract and state, not here.

## 1. The actual authorization

Sent by Joseph as a Claude Code `/goal` on **2026-09-24 (PDT)** to session
`eb3ae0a2-92c9-47d8-92e9-208221cd08f3`. The session's first clock reading after receipt was
`2026-09-25T05:59:18Z` (`date -u`), so the message was sent no later than that instant (22:59 PDT on
2026-09-24). Verbatim, line breaks as sent:

> Execute the scalar-5D uncertainty and inference campaign through final disposition. Read:
> - docs/orchestration/DRAFT-preservation-and-stabilization-session-prompts.md — only “Complete estimator
> goal prompt”.
> - docs/orchestration/PLAN-scalar5d-reportable-uncertainties-and-inference.md.
> - docs/orchestration/HANDOFF-20260924-preparation-for-scalar5d-campaign.md.
> - docs/orchestration/RECOVERY-MANIFEST-20260924-preparation-epoch.md.
>
> I approve that complete estimator prompt and plan, including all five clarifications, scoped
> supersession, delegated scientific choices, conditional adoption, resource limits, independent review,
> and commits, merges and pushes to both existing project repositories. Proceed without further routine
> approval.
>
> Verify the preserved document identities and current state. The approved plan is blob
> 8b0617b6e044a55a9b5870b46e5d90a15a6ced7a, first committed in bf34a12cff9a2f06f0a3f1c516628085565eef60.
> Keep it unchanged. Before implementation, commit a separate record of this actual authorization, its
> date, those identities and the scoped supersession mapping. Resolve identity conflicts before dependent
> work. Follow AGENTS.md and routed instructions with these supersessions.
>
> D2: For this new campaign only, I supersede R5’s 2026-09-30 stop and cumulative task-hour ceilings,
> including their application through AUTHORIZATION-20260918-d-resource-required-deliverable-path.md §1.
> Use the plan’s section 3 envelope: at most 500 billed CPU node-hours and 500 A100-equivalent GPU-hours,
> each also capped at 10% of measured uncommitted remaining allocation after existing reservations. No
> inherited calendar deadline applies. Retain the plan’s concurrency, candidate, reservation and stopping
> rules. Preserve historical R5 accounting and its application to other campaigns. Establish verified
> campaign-specific admission and accounting before compute; do not disable or bypass guards globally.
>
> D3: I authorize one durable HPSS backup of the exact nine sole-copy objects in the recovery manifest,
> up to 64 GiB of additional archival storage. Recheck source identities, sizes and free quota. Use
> existing approved accounts; no purchases or allocation transfers. Necessary transfer and restore jobs
> are authorized within applicable campaign resource limits; staging and restores must fit the plan’s
> storage envelope. Restore all nine, verify recorded SHA-256 digests and commit the recovery receipt.
> Preserve originals. If blocked, report the exact dependency and continue independent work. Preserve
> required inputs before dependent production.
>
> Reuse Session 1’s completed preparation. Do not repeat preservation or general cleanup. Track remaining
> handoff dependencies by the exact actions they block. Use isolated worktrees and fresh output
> namespaces, preserve concurrent work, and avoid duplicate jobs or changes to historical adopted bytes.
>
> My objective is publication readiness with defensible uncertainties and calibrated joint-5D generator
> inference at a declared resolution. Significant disagreement is not required; projection-only results
> do not fulfill the joint-5D objective.
>
> Complete costed feasibility before expensive production. Cost measurement and inference separately,
> protect measurement validation resources, and deliver an independently verified uncertainty checkpoint
> when qualified. Continue feasible joint inference within the approved limits. Finish independent
> validation, scientific disposition, release preparation and synchronized deliverables. Maintain durable
> checkpoints.
>
> Report campaign_disposition, reportable_uncertainty_scope, joint_5d_inference_status and
> publication_readiness separately, with failed or missing requirements, costed next increments and both
> verified remote heads. Do not label an unmet objective publication-ready. External publication, public
> data deposition and final publication release tagging remain separate decisions.

The approval wording inside the plan and the draft was draft text until this message. Nothing in this
record treats it as an earlier executed decision.

## 2. The approved versions, by identity (measured 2026-09-25T06:0xZ)

| document | Git blob | first and only commit that changed it | tag |
|---|---|---|---|
| `docs/orchestration/PLAN-scalar5d-reportable-uncertainties-and-inference.md` | `8b0617b6e044a55a9b5870b46e5d90a15a6ced7a` | `bf34a12cff9a2f06f0a3f1c516628085565eef60` | `evidence/preparation-2026-09-24-bf34a12c` |
| `docs/orchestration/DRAFT-preservation-and-stabilization-session-prompts.md` (only its *Complete estimator goal prompt* section is activated) | `cf3c2e858d4526ad356e604af9bc6100e6cc7e9f` | `bf34a12cff9a2f06f0a3f1c516628085565eef60` | same |

How measured: `git hash-object` on the files at `origin/main = 6abfb5f4`; `git rev-parse
evidence/preparation-2026-09-24-bf34a12c:<path>` for both; `git log -- <path>` lists only
`bf34a12c` for each; the untracked copies in the shared main checkout hash to the same two blobs.
**No identity conflict exists.** The plan stays byte-identical at `8b0617b6…` for the life of the
campaign.

**The five clarifications are present in the approved plan** (checked before recording approval):

| clarification (prompt §1–5) | plan location at blob `8b0617b6…` |
|---|---|
| 1. inference adoption gates apply to the named comparison; joint-5D needs joint seed-stability and anchored joint power; projection qualification does not fulfil joint-5D | §9 condition 4 (lines 565–571) |
| 2. power alternatives outside the tested null family incl. nuisances and detector response; truth-parameter change alone insufficient | §5 (lines 251–256) |
| 3. inference gates apply to every calibrated comparison incl. non-rejecting; measurement may qualify separately | §9 (lines 565–566, 574–576); §1 (lines 26–35) |
| 4. declare what each seed changes; reproducibility ≠ sensitivity ≠ coverage; determinism not a failure | §6 (lines 338–342) |
| 5. seed averaging: freeze object and stage, apply consistently, validate independent ensembles; averaging covariances is not validation | §6 (lines 346–353) |

## 3. Scoped supersession mapping (plan §2; D2; D3)

Applies **to this campaign only**. Every displaced record stays in place, unedited, and keeps
governing everything outside this campaign. This mapping cannot expand the plan's delegation.

| # | displaced record / clause | its operative text (abridged; open the record) | newly authorized action, this campaign only | authority | explicitly unchanged |
|---|---|---|---|---|---|
| S1 | `DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md` `R5` and §3's meter | stop `2026-09-30` UTC or `500` GPU / `500` CPU **task-hours** | campaign envelope of plan §3: **≤ 500 billed CPU node-hours** and **≤ 500 A100-equivalent GPU-hours**, each also **≤ 10% of the measured uncommitted remaining allocation** after existing reservations, fixed at activation by the campaign budget receipt; **no calendar deadline** | D2 | `R5`'s historical accounting and its application to the seven-cause discharge campaign and every other campaign; campaign jobs are not charged against `R5`'s ceilings nor removed from any `R5` record |
| S2 | `AUTHORIZATION-20260918-d-resource-required-deliverable-path.md` §1, sentence *"Unchanged and binding: `R5`'s ceilings … stop `2026-09-30`); per-submission accounting and admission via `r5_meter.py`"* | `R5` applied to the scalar path; admission via `r5_meter.py` | admission and accounting through a **campaign-specific** meter in native billed units, verified (defect and innocent controls) **before** any campaign compute | D2 | `r5_meter.py` and every guard that calls it stay as they are for other work; no guard is disabled or bypassed globally. §1's other clauses are **retained** for this campaign: reservations priced as enforced cap × tasks; automatic requeue disabled; and — alongside plan §3's *"at most two retries per task for a diagnosed infrastructure failure"* — at most one corrective resubmission per stage after a diagnosed code defect, verified repair and fresh admission (executor choice: where both rules speak, the stricter applies) |
| S3 | `AUTHORIZATION-20260918…` §2 ruling 1; `DECISION-20260919-joseph-rules-pm1-cause7-and-completion.md` §6 *"The generator-significance claim remains optional and outside this completion path"* | significance excluded from the required path | joint-5D and calibrated projection/contrast generator inference are in scope under plan §§5, 7, 8 | plan §2 | the completed required path and its adoption stand; no historical χ², `N`σ, 12-cell statistic, `rcond` or pseudoinverse is revived — plan §5 forbids raw-covariance inversion and pseudoinverse DOF |
| S4 | `DECISION-20260919…` §6 *"Do not reopen the declined member campaign"*; its §7 stopping rule; `AGENTS.md`'s corresponding caution | holds on additional scalar seed/member studies | fresh estimator-seed ensembles (≥ 10 seeds in development where a spread is estimated), fresh members and **fresh paired rebuilds at one pinned revision**, in new namespaces (plan §§2, 6) | plan §2 | PET, `OI-126` and Gate 6 are not reopened; completed central-value campaigns are not repeated |
| S5 | `AUTHORIZATION-20260918…` §2 ruling 8, *"PINNING — RESERVED"* (`deterministic` / `force_row_wise` / `num_threads` on `make_estimators`) | named estimator changes reserved | deterministic settings, thread policy, fresh seed ensembles, seed averaging and complete lateral seed propagation **in new isolated candidates** | plan §2 | the adopted trunk's code path and bytes; historical defaults are not edited in place for historical products |
| S6 | `DECISION-20260919…` §6 *"Final covariance adoption remains my reserved act"*; `AGENTS.md` *Decisions reserved for Joseph* (publication adoption) | adoption is Joseph's personal act | **delegated conditional adoption** of newly produced, independently verified candidates that meet **every** plan §9 condition, recorded as delegated with exact digests | plan §2, §9 | `3d7465f6…`'s adoption and its byte-scoped §6.4 exception; any **new** exception stays outside the delegation (report without adopting) |
| S7 | `OUTCOME-20260922-L2-sproj-measured-and-the-pair-is-not-code-comparable.md` (same-commit rebuild declined; handoff D5) | the L2 pair is not code-comparable | fresh paired rebuilds when code comparability requires both members | plan §2 | the recorded L2 measurement and its `footing_ok` failure |
| S8 | `RECOVERY-MANIFEST-20260924…` §2 *The gaps* — a storage decision of the kind `OI-131` reserves (handoff D3) | the nine objects need a storage decision | **one** durable HPSS backup of exactly those nine objects, ≤ 64 GiB additional archival storage, with the transfer and restore jobs it needs, inside campaign limits; restore all nine and verify SHA-256 | D3 | originals preserved; no purchases or allocation transfers; `OI-131`'s other items |

**Not displaced — retained as binding on this campaign:**

- Joseph's `(B)` in `OUTCOME-20260920-cause3-two-member-assessable-FAIL.md` (*"recorded once. No
  retries, re-seeding or reconfiguration to change it"*). New candidates are graded against a new
  contract; nothing re-grades the Z candidates or edits the 2026-09-20 verdict or `M1`.
- `SPEC-20260906-complete-scalar5d-successor-Z.md` stays **frozen**. A result passing the successor
  contract is not a retroactive PASS under Z.
- `OUTCOME-20260922-ten-adopted-receipts-superseded-by-code-drift.md` (handoff D4): baseline
  re-production of the ten endpoints in the protected `active_universe_5d/standard/unfolds/`
  namespace stays reserved and its guard stays closed. Plan §2's *complete lateral seed
  propagation in new isolated candidates* is performed only as **fresh endpoint unfolds in a new
  campaign namespace** with their own receipts.
- `DECISION-20260902…` `R6`, `OI-126`'s ruling and the Gate-6 prohibitions: PET stays diagnostic.
- The four adoption measurements of `DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md`
  §4 travel with every product derived from `3d7465f6…`.
- `AGENTS.md` *Next-action discipline* item 3 is satisfied for campaign compute by this activation;
  every campaign compute receipt still names the quantity it measures and what its terminal result
  cannot authorize (plan §11).

## 4. What this activates and what it does not

| activated | not activated |
|---|---|
| plan `8b0617b6…` §§1–11 and the draft's *Complete estimator goal prompt* | journal/arXiv submission, public data deposition, final publication release tagging |
| D2's campaign envelope and D3's single HPSS backup | purchases, allocation transfers, credential changes, external messages |
| commits, merges and pushes to `origin` and `analysis-note` | force-push or history rewrite |
| delegated adoption under plan §9 | adoption of anything requiring a new exception |
