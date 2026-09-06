# AUTHORIZATION 2026-09-06 — Joseph authorizes one bounded read-only ROOT inspection allocation

**CITABLE FOR:** the authorization in §1, its limits in §2, and the admission blocker measured in §3.
**NOT CITABLE FOR:** any discharge, grade, adoption, gate movement, launch, spend, or publication
claim. **Nothing was submitted under this authorization.** Gate 2 remains FAIL. CAND `1 of 7`,
QUOTED `0 of 7`. PET `C_stat` remains `EXISTS — UNVERIFIED, PAIRING DECLINED`. The five Gate-6
prohibitions stand.

## 1. Authority

Joseph, 2026-09-06, in his own turn, to this lane:

> *"I authorize one CPU-only interactive allocation for read-only ROOT inspection of the exact files
> and objects needed for PM-1, PM-4, PM-5, and PM-3's grid/footing checks."*

Recorded because in this repository an authorization is itself an evidence artifact.

## 2. Limits, as given

Quoted, because a paraphrased limit is a different limit:

> *"Limits: one CPU node, one inspection task, maximum 30 minutes, no GPUs, no automatic retries or
> requeues. Release the allocation immediately when finished. Declare the exact command, environment,
> memory request, input paths, and intended reads before submission."*
>
> *"No training, covariance construction, production execution, changes to source artifacts or frozen
> checkouts, package installation into shared environments, grading, or adoption. Stop if the checks
> require work outside these limits."*
>
> *"Before submission, commit the preflight evidence and this named authorization. Label the existing
> R5 receipt explicitly as incomplete because it omits requeue expenditure; do not present it as valid
> admission evidence."*
>
> *"Submission must use corrected, verified accounting and the existing admission controls. If those
> cannot admit this allocation, return the precise blocker and any proposed one-off accounting
> exception for my separate approval—do not bypass them."*
>
> *"Preserve the inspection outputs and final scheduler accounting, including failed execution time.
> Report measurements separately from scientific conclusions."*

The declaration those limits require is `PREDECLARATION-20260906-pm-root-inspection.md`, committed
before any submission. The preflight evidence is at
`docs/orchestration/state/preflight-20260906-r5/`, whose `README.md` carries the INCOMPLETE label and
explains why the receipts are **not** at the admission path.

## 3. ⚠ THE EXISTING ADMISSION CONTROLS CANNOT ADMIT THIS ALLOCATION — four independent blockers

Measured against `docs/orchestration/campaignctl.py` at this base. **Nothing was bypassed and nothing
was submitted.**

### 3.1 The R5 receipt gate — and Joseph's own instruction closes it

Compute admission requires an R5 receipt that is **committed at `HEAD`** at
`docs/orchestration/state/r5-meter-receipt.json` (`campaignctl.py:271` `DEFAULT_R5_RECEIPT`;
`:3080-3111` `committed_r5_receipt`, where an untracked file or a working-tree edit after the commit
is a refusal), **structurally valid** (`:2921-2975` `validate_r5_receipt`), and **under 24 hours old**
(`:292` `R5_MAX_AGE`; checked at `:3355-3360`).

The only receipt the landed meter can produce reports `0.0016667` CPU task-hours where the
requeue-inclusive reading is `12.5903` (evidence directory `README.md`). Joseph ruled it *"incomplete
… do not present it as valid admission evidence."* **Committing it to that path is exactly that
presentation** — that path is the gate's input and nothing else reads it. So the instruction that
labels the receipt also forecloses the only route to admission.

There is no honest way around this from inside this lane. Repairing `r5_meter.py` is a change to a
source artifact, which §2 forbids, and the repair is already owned by the integration lane. Editing
the receipt's bytes to carry a corrected number would fabricate a measurement the meter never made.

### 3.2 Approval requires an interactive TTY, and no agent can supply one

`campaignctl.py:3476-3477`: `if not sys.stdin.isatty(): raise QueueError("approval requires an
interactive TTY")`. By design, a staged item becomes runnable only after **a human** reviews its
complete digest and approves it from a terminal. That is a human act. This lane does not attempt it,
and the module is explicit that *"an operator's typed phrase is additional confirmation, never the
authorization."*

### 3.3 The item cannot be expressed — an interactive allocation is not a queue item

A compute item requires a **committed campaign contract** (`:2737-2738`, refusing outright without
one) declaring a **guarded producer** and an **independently bound terminal validator**, both routed
through `nd-unfolding/mnv_guarded_run.py`, both committed at `HEAD` and working-tree identical
(`:2762-2790`), with the validator alone selecting *"an exhaustive terminal branch with a decision
consequence"*, and one shared `maximum_cost.wall_hours` deadline. The ticker executes items
**without a shell**.

Joseph authorized an **interactive** allocation for exploratory inspection. It has no producer/
validator pair, and an inspection whose declared purpose includes discovering whether `hRowIndex5D`
is present has no exhaustive terminal branch to select. No such contract exists, and writing one
would mean inventing a validator for a question whose answer is not yet known.

### 3.4 No committed campaign contract exists for this work

Stated separately from 3.3 because it is separately fatal: even were the shape right, the contract
must exist and be committed before staging.

### 3.5 The evasion that exists, named so it is on the record as rejected

A `--kind read-only` item skips the R5 gate entirely — `r5_refusal_reason` is called only under
`if item["kind"] == "compute"` (`:4287-4288`) — and needs no contract, no guard and no receipt. Staging
a compute allocation as `read-only` would therefore "pass". **That is precisely the bypass Joseph
forbade**, it would defeat the ceiling the gate exists to protect, and this lane rejects it. It is
recorded here so that its availability is a known, refused option rather than an undiscovered one.

### 3.6 What is NOT blocking

For completeness, since a blocker list is only useful if it is exact: the origin remote is correct and
reachable. `git remote get-url origin` and `--push` both return
`https://github.com/josephbaileyy/MINERvA-OmniFold`, byte-matching `origin_url` in the committed
`control-plane/campaign-origin.json` (campaign key `r5-20260902-0836139b`), and `git ls-remote`
succeeds. The admission namespace is intact. The blockers are the receipt, the TTY, the item shape and
the missing contract — not the control plane.

## 4. The proposed one-off accounting exception, for Joseph's separate approval

Offered as a proposal only. **This lane will not act on it without his explicit approval**, and it is
deliberately the narrowest thing that unblocks the inspection.

**The problem in one line:** the inspection needs a few minutes of CPU, but the gate that would admit
it requires committing a receipt whose number Joseph has ruled must not be presented as valid.

**Proposal — approve the allocation OUTSIDE campaignctl, under this record, with the accounting
reconciled afterwards.** The reasoning: campaignctl governs the *unattended campaign queue*, and its
gates exist to stop an unattended ticker spending against a ceiling nobody is watching. This is a
single attended allocation, declared in advance, bounded at 30 minutes, releasing on exit, run by a
human-authorized lane and not by a ticker. Routing it through a queue built for a different object
requires inventing a contract and a validator, which is more fabrication than the exception.

**The conditions that would make the exception safe, all four together:**
1. **A bounded, declared cost.** ≤ 30 minutes, one CPU task, no GPU. Prior art puts the real cost near
   a minute: `RECEIPT-20260816` records a 5D key listing at **9 s** and an `hRowIndex5D` readback at
   **14 s**. Against the 500 CPU ceiling this is ≈ 0.008–0.5 task-hours.
2. **Reconciliation against the corrected reading, not the meter's.** The charge is added to the
   requeue-inclusive figure — `12.5903` CPU task-hours as of `2026-09-06T08:54Z` — not to the
   `0.0016667` the meter reports. Corrected CPU headroom is `487.41`, and this inspection cannot
   plausibly move the third decimal place.
3. **No arming of admission.** The receipt stays out of
   `docs/orchestration/state/r5-meter-receipt.json`. The exception admits **one allocation**, never
   the queue.
4. **A post-run receipt**, preserving the final `sacct` accounting for the allocation including any
   failed execution time, committed beside the preflight evidence.

**The alternative, which needs no exception and which this lane prefers if there is no hurry:** wait
for the integration lane's `r5_meter` repair, re-measure, commit a receipt that is actually complete,
and go through campaignctl properly — which still needs a campaign contract and Joseph's TTY approval,
so 3.2, 3.3 and 3.4 remain even then. **The honest summary is that this inspection does not fit the
campaign queue at all**, and the real decision is whether an attended, declared, bounded allocation
should ever have to.

## 5. Status

**DECLARED, COMMITTED, NOT SUBMITTED.** No job was submitted. No credential was created or changed.
No unattended execution was configured. No frozen checkout was modified. No admission control was
bypassed, and none was tested against a fabricated receipt. Awaiting Joseph's separate decision on §4.
