# Session and campaign review — read before campaign work

**Assessment date: 2026-09-29. Status: advisory retrospective, not independently reviewed.**
Joseph requested this review and then asked for it to be made prominent so future campaign sessions
can make informed decisions. Required reading is routed from `AGENTS.md` and `CLAUDE.md`.
Preservation of the review is not ratification of every recommendation.

**Main finding:** bounded scientific tasks, explicit terminal outcomes, and independent review of
the actual artifacts have the strongest project evidence. Open-ended orchestration and repeated
review-until-perfect loops have conspicuous failures. Model choice matters, but the same Opus
generation appears in both strong campaigns and the clearest failed review loop.

This document does not authorize compute, delegation, external communication, publication adoption,
or changes to scientific gates. Existing task instructions and campaign contracts take precedence.
Read `docs/CURRENT_WORK.md` and the governing record before acting. The cases below are historical
observations, not a live scientific-status dashboard or a source for quoting physics results.

## 1. How to use this review

Before designing, starting, resuming, coordinating, or reviewing a campaign, record a short choice
in its existing plan or handoff:

- Which decision will the work answer, and what counts as a useful terminal failure or inconclusive result?
- Who owns the artifact, who independently reviews it, and why do the selected models/efforts fit?
- What is the compute and review/repair budget, and when will the strategy be reassessed?

Use a few sentences, not a new approval form or another campaign-wide accounting system. For an
existing campaign, preserve its frozen criteria and required reviewer set. Reading this review
does not authorize adding agents or changing the stopping rule.

## 2. Basis and limits of the assessment

The review inspected committed outcomes and selected session transcripts/metadata. The remote
`main` was checked at **`6b08861fad14609d526a0c655ebd96be582af978`**; the completed PET improvement
branch was checked at **`9368ec9e55eb486109498772753825fc24616851`**. The original local main was
160 commits behind that remote snapshot, so relying on its front door alone would have missed the
newer campaigns. Future sessions must likewise check their actual baseline.

Success here means durable scientific progress, an independently supported decision, a consequential
defect caught, or justified compute avoided. A failed scientific candidate can be a successful
investigation. Commit count, token count, number of findings, and completed jobs are not success scores.

At the pinned main snapshot, **404 of 3,706 reachable commits** contained at least one explicit
`Claude-Session:`, `Codex-Session:`, `Agent-Session:`, or `Session-ID:` line, matched case-insensitively
at the beginning of a commit-message line. This is a limited trailer census, not a complete session
inventory. Many authors are generic or human identities; coauthor labels are attribution claims,
not independently authenticated runtime records. Sessions can change model mid-task.

The inspection included an inventory of 212 project-path Codex thread records and 100 Claude
project transcript files. These are not a deduplicated cross-provider population: copied transcripts,
child threads, different task sizes, and incomplete historical retention prevent a fair denominator.
Selected runtime model fields were checked for the sessions listed below. Raw private transcripts
are not copied into this public repository; model/session mappings reported from them are
observations of this retrospective. The linked committed artifacts support the campaign outcomes.

**No controlled model win rate, cost-normalized ranking, or causal effect of reasoning effort was
established.** Compute costs below are campaign resource figures, not model inference costs. Newer
or still-running campaigns are not counted as completed successes. No new scientific computation
was performed for this retrospective.

## 3. Strongest successful examples

### 2D Phase-18.2 and uncertainty repairs — strongest durable publication contribution

The May–June campaign produced the validated central result and matched-CV uncertainty construction.
Key production and MAT-comparison commits credit **Claude Opus 4.7**; the flux repair credits
**Opus 4.8**. The flux repair reused existing universe products analytically, then checked agreement
with the driver. The covariance implementation was compared directly with MAT.

What to reuse: an external reference, explicit invariants, independent implementation comparisons,
and cheap exact repairs before expensive retraining. This does not establish that the older models
are better than their successors: the target and task distribution differ substantially.

Sources: [2D status](../../2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md),
[production commit](https://github.com/josephbaileyy/MINERvA-OmniFold/commit/ce49a567),
[MAT comparison](https://github.com/josephbaileyy/MINERvA-OmniFold/commit/b480c261),
[flux repair](https://github.com/josephbaileyy/MINERvA-OmniFold/commit/983e3568).
For scientific quotations, follow the current validation ledger and its exact receipts.

### PET improvement, September 22–25 — strongest recent experimental campaign design

The campaign separated development, pilot, final, and stress samples; froze candidates; completed
36 final and 36 stress runs; and stopped before coverage because no frozen candidate qualified at
the declared iteration. It delivered a defensible diagnostic answer, not a publication uncertainty
product. The closeout reports **268.3 GPU-hours and 9,221 CPU-core-hours**: successful does not mean cheap.

Implementation and coordination involved **Opus 5/5.5**, including session
`b160e1e8-d9e0-44fe-ab81-24d89902eec7` and a subsequent takeover. **Astra High** supplied independent
review. The review corrected several substantive problems; the campaign was not flawless on first pass.

What to reuse: distinct sample roles, frozen comparisons, matched interventions, explicit stress
tests, candid limitations, and a terminal rule that prevents retrospective promotion of a better-looking
iteration. PET remains diagnostic/method-development only.

Sources at the preserved campaign commit:
[closeout and resources](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/9368ec9e55eb486109498772753825fc24616851/nd-unfolding/pet/improvement_campaign/HANDOFF-pet-improvement-campaign.md),
[confirmatory results and coverage decision](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/9368ec9e55eb486109498772753825fc24616851/nd-unfolding/pet/improvement_campaign/confirm/CONFIRM_RESULTS.md).

### OI-192 / s5e, September 25–26 — strongest bounded diagnostic session

**Opus 5.5**, session **`8ad4e62d-1079-4f28-aa0b-dccf6476a48b`**, diagnosed refinement-classifier
capacity as a cause of nominal background bias, assessed one targeted candidate, accepted its
subsequent assessment failure, and closed with independently reproduced results. The campaign used
**10.399 CPU node-hours and no GPU**. Its bounded diagnosis/assessment objective was met; the larger
publication objective was not.

The outcome also records limits worth retaining: the candidate's reproducibility failure was
foreseeable from its baseline, the development screen was explicitly weakened before candidate
data, pooled calibration did not establish per-functional calibration, and no estimator was adopted.
Praise for this session is not a claim that every experiment was necessary or every initial claim correct.

What to reuse: a goal that permits a verified failure, a specific causal intervention, fresh assessment
seeds, independent numerical reproduction, and a costed next decision instead of an automatic rerun.

Sources: [committed closeout](https://github.com/josephbaileyy/MINERvA-OmniFold/commit/5683e329),
[outcome](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/6b08861fad14609d526a0c655ebd96be582af978/docs/orchestration/OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md).

### Astra High PET reviewers — clearest model-attributed review success

Runtime metadata was checked for these **`gpt-6-astra`, high-effort** sessions:

| Session | Contribution |
|---|---|
| `01a0d21d-4756-79e2-be0d-0a2915505faf` | Reproduced a competing-writer lock race; exposed final decisions from incomplete samples and a reduced multiple-testing family; challenged unsupported scientific interpretations. |
| `01a0d5e3-74f9-7252-9720-a899ca19edab` | Found that missing/incomplete audit evidence could still yield a complete final gate, and that missing execution records could be classified clean. |
| `01a0d89c-c56c-7160-b794-7984f7f3d734` | Recomputed stress results, upheld the declared no-coverage decision, and narrowed overbroad conclusions about iterations, identifiability, and mechanism. |

What to reuse: a fresh read-only context, a fixed commit, reproductions of consequential defects,
and explicit separation between a defective gate and a demonstrated error in the numerical result.
These reviews also stated what they could not verify in their environment.

Committed dispositions (the owner's checked restatement, not verbatim reviewer transcripts):
[round 1](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/9368ec9e55eb486109498772753825fc24616851/nd-unfolding/pet/improvement_campaign/REVIEW_DISPOSITION-20260924.md),
[round 2](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/9368ec9e55eb486109498772753825fc24616851/nd-unfolding/pet/improvement_campaign/REVIEW_DISPOSITION-ROUND2-20260925.md).

### s5c, September 24–25 — useful falsification and resource control

The **Opus 5.5** campaign (session `eb3ae0a2-92c9-47d8-92e9-208221cd08f3`) applied a predeclared
futility rule and stopped validation. Independent code reproduced the terminal failure. The verdict
did not depend on a defective deformation point discovered during review. No result was adopted.

This was a useful investigation and resource-control outcome, but **the campaign's stated scientific
objective was not met**. Do not replace that distinction with a general PASS label.

Sources: [terminal outcome](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/6b08861fad14609d526a0c655ebd96be582af978/docs/orchestration/OUTCOME-20260925-s5c-tier-s-futility-fail.md),
[closeout commit](https://github.com/josephbaileyy/MINERvA-OmniFold/commit/3905893f).

## 4. Strategies to avoid

### Unbounded review-until-perfect loops

The September 22–24 session **`0d684b57-4cd1-4847-b6ec-cded39aa7e2c`** used both **Opus 5 and
Opus 5.5**. It reached independent review **#49 without convergence**. The closing commit records
that, from review #39 onward, about half the counted findings concerned defects introduced by the
previous repair. Joseph ended the loop. Earlier reviews found useful defects; later bookkeeping and
its new instruments became a continuing source of work.

This was partly a stopping-condition and scope problem. Do not infer that independent review is
unhelpful, or that switching models alone would fix it. Freeze the object and rubric, prioritize
material findings, and budget repair cycles before starting.

Sources: [closing commit](https://github.com/josephbaileyy/MINERvA-OmniFold/commit/c496135f992fc22eb2d89816a9de1b5b844c5872),
[review-residue report](REPORT-20260922-review-residue.md).

### A reasoning-heavy coordinator acting as the scientific authority

The August 11 retrospective names the oversight session as the largest source of wrong claims that
day; worker lanes caught its errors. Internally coherent reasoning was built on unchecked premises.
Narrower coordination and direct source checks address the observed failure. The retrospective's
suggestion that cheaper reasoning could help is a hypothesis, not a measured effort-level comparison.

Source: [four-session retrospective](PROMPTS-20260811-four-session-closeout.md). Its historical run
authorizations and model suggestions do not supply current authority.

### Trusting generated quotations or results

The PET coordinating transcript records an `agy` delegate supplying nonexistent paper quotations
and a placeholder results file with `data_sha256` set to `fake` and uniform recovery values. They
were caught and excluded, not committed as evidence. The committed campaign handoff preserves the
warning. The exact runtime Gemini model was not established in this retrospective; do not generalize
the incident into a ranking of every Gemini model.

Use secondary-model proposals and code only after checking sources, executing the code where
appropriate, and verifying result provenance. Never treat a plausible output file as a measurement.

Source: [campaign handoff, Known traps](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/9368ec9e55eb486109498772753825fc24616851/nd-unfolding/pet/improvement_campaign/HANDOFF-pet-improvement-campaign.md).

### Substituting activity or agreement for validation

Avoid counting commits, findings, completed jobs, hashes, or agreeing workers as proof of scientific
validity. A hash establishes identity with a target; a test establishes what its exercised path can
detect. Neither proves the target or criterion is scientifically appropriate. Different accounts or
models are not automatically independent origins. Trace claims to their first measurement.

Source: [PLAYBOOK.md](PLAYBOOK.md), especially PB-04, PB-05, PB-12, PB-13, PB-16, PB-23 and PB-25.

## 5. Model and effort choices

These are **dated, role-specific recommendations**, not a mandated provider mix or an automatic
model upgrade. Check current availability and explicit task constraints before selecting a model.

| Role | Recommended starting point | Evidence strength and limit |
|---|---|---|
| Scientific implementation and bounded campaign ownership | Opus 5.5 with a written contract and terminal outcomes | Strong project examples; no proof it universally beats Astra. |
| Consequential code, statistical, or publication-claim review | Astra High in a fresh read-only session | Strongest directly attributable review examples inspected. |
| Routine implementation with clear acceptance tests | Sol-class model; escalate when needed | Prospective efficiency choice, not a measured project win-rate advantage. |
| Scheduling, status extraction, deterministic reporting | Scripts first; Luna or Sonnet for language/routing | Workflow recommendation; comparative model superiority not measured here. |
| Exploratory alternatives | A secondary model, including Gemini, with verified sources | A challenger can help; generated numbers and quotations remain unverified. |

The suggested setup for a new substantial campaign is an Opus 5.5 owner, an Astra High reviewer,
scripted coordination, and a predeclared stop, **when that arrangement is available and authorized**.
Do not downgrade to Opus 4.7/4.8 solely because the 2D campaign succeeded. Do not rank Astra above
Opus overall from these examples. Do not equate longer context or maximum effort with correctness.

[Official OpenAI model guidance](https://developers.openai.com/codex/models), consulted 2026-09-29,
recommends Astra for the hardest work, Sol for repeated complex work, and Luna for focused tasks;
it does not recommend maximum effort for every task. This is vendor guidance, not independent
project evidence, and may change. Verify it again before using it for a new purchase or configuration.

## 6. Recommended campaign practices

1. **Answer a decision.** Define success as an evidence-backed disposition. Allow a verified failure,
   inconclusive diagnosis, or demonstrated infeasibility to terminate the bounded task honestly.
2. **Keep ownership simple.** One owner and one independent reviewer are a useful starting point for
   new tasks; preserve extra reviewers required by the governing contract. Add specialists only for
   separable work and within delegation authority. More participants do not create independence.
3. **Freeze the review target and rubric.** Require operands, reproductions, scope, material impact,
   and a concrete disposition. Reviewers remain read-only; a writer fixes the artifact.
4. **Budget repair cycles.** For a new campaign, consider two repair/review cycles before explicitly
   choosing continue, redesign, or stop. This is a reassessment checkpoint, not permission to ignore
   a material defect or skip required review. Continuing should answer a named unresolved question;
   minor bookkeeping should not silently restart the entire campaign.
5. **Run cheap discriminating checks first.** Check actual imports, input semantics, exclusive output
   ownership, complete-manifest gates, and whether the candidate can satisfy its criteria before
   launching expensive ensembles. Reuse validated intermediates when a later stage alone fails.
6. **Rotate at task boundaries.** Start from durable handoffs and exact input commits. Persistent
   continuity is useful for provenance; it should not become an all-purpose authority. Repeated
   material corrections or confusion between superseded and current state warrant a fresh context.
7. **Measure outcomes, not activity.** In the existing closeout, record model/version, effort, full
   session identity, input/output commits, measured compute and available inference cost, accepted
   consequential findings, residual defects, and the decision resolved. Mark missing cost data as
   unavailable; cumulative token counters are not directly comparable bills.

Keep this review compact enough to read at campaign start. Update recommendations when new durable
evidence changes them, preserving the date and attribution limits. Do not create a recursive review
campaign merely to maintain this document.
