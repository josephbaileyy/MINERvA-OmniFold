# AUTHORIZATION 2026-09-08 — attended **batch** allocation replaces interactive, for the already-scoped ROOT inspection

**CITABLE FOR:** the execution route of the PM-1/PM-3/PM-4/PM-5 ROOT inspection, and nothing else.
**NOT CITABLE FOR:** any scientific scope, any additional allocation, any relaxation of admission,
approval, review or accounting.

This is **additive**. It changes one thing in
`AUTHORIZATION-20260906-pm-root-inspection.md` and `PREDECLARATION-20260906-pm-root-inspection.md`:
the allocation is **attended batch** rather than interactive. Everything else in both records
stands unaltered.

## 1. The exchange, verbatim

> **Assistant:** *"Do you authorize an **attended batch allocation instead**, retaining one CPU
> node/task, ≤30 minutes, no GPUs or retries, and all existing admission and human-approval
> controls?"*
>
> **Joseph:** *"Yes"*

**Attribution.** The question was put by the assistant in a **Codex coordination session**; the
approval is Joseph's. **Provenance: relayed.** That exchange did not occur in the preflight
session that authored this file — it was reported here by the Codex coordinator, and then, on
request, sent verbatim by that coordinator, which is the text quoted above. There is no session URL
for it and none is invented. A reader who needs the primary record must go to that Codex
conversation, not to this file.

**Why the relay is recorded rather than smoothed.** A relayed approval is not the approval itself;
this campaign has ruled that twice today in the other direction. It is recorded here because a route
change needs a citable basis, and the honest basis is "Joseph said Yes to this question, in another
session, reported and then quoted verbatim by its coordinator". If that provenance is not good
enough for whoever reads this before submission, the remedy is to obtain it from Joseph directly —
not to treat this file as though it were firsthand.

## 2. What changes

Interactive allocation → **attended batch** allocation. That is the whole change.

**"Attended" is unchanged and is not satisfied by approving.** The executing session remains present
through completion and cleanup, per the ruling of 2026-09-08.

## 3. What does NOT change

Retained verbatim from the question Joseph answered: **one CPU node, one task, ≤30 minutes, no GPUs,
no retries**, and **all existing admission and human-approval controls**.

Retained from the 2026-09-06 records: the **13 declared inputs** and no others; read-only opening;
no training, no covariance construction, no production execution; no modification of any source
artifact or frozen checkout; no package installation anywhere; **no grading, discharge or adoption**;
prompt release; preservation of outputs **including failed execution time**; measurements reported
separately from conclusions.

**Explicitly NOT bypassed by this authorization**, because a route change is not a control change:

- **TTY approval.** `campaignctl.py:3540-3541` still requires a human at an interactive terminal
  pasting back the staged proposal digest. No agent can supply it and this file does not.
- Independent review of the package and the launcher before staging or execution.
- The merge guard.
- Campaign admission and the R5 reservation and accounting rules.

## 4. Why the route changed — the technical reason, stated so it can be checked

An interactive allocation yields no scheduler identity until it is granted, so an allocation can
exist and begin spending before anything has recorded what to meter or what to cancel. The guard's
shim wraps `sbatch`, `srun`, `scancel`, `squeue`, `sacct` and **not `salloc`**, so the interactive
route also has no guarded spelling. Batch submission returns the job id **at submission**, before
the job can spend, which is what makes immediate identity recording and scoped cancellation
possible.

**This does not make the batch route risk-free, and two limits are recorded here rather than
discovered later.** A non-zero submission does **not** prove no job was created — an acknowledgement
can be lost — so an uncertain submission is classified as uncertain and its **reservation is
retained**, never released on an assumption of zero spend. And identity recovery by a scoped job
token is **best effort**, bounded by query visibility and lag, not a guarantee that every lost-id
window is closed.

## 5. Status

**AUTHORIZED, NOT EXERCISED.** Nothing has been staged, submitted or executed under this record.
