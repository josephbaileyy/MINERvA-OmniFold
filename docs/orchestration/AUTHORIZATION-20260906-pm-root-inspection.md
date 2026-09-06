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

**The alternative:** wait for the integration lane's `r5_meter` repair, re-measure, commit a receipt
that is actually complete, and go through campaignctl properly — which still needs a campaign contract
and Joseph's TTY approval, so 3.2, 3.3 and 3.4 remain even then. **The honest summary is that this
inspection does not fit the campaign queue at all**, and the real decision is whether an attended,
declared, bounded allocation should ever have to.

### 4a. ⚠ The two paths have DIFFERENT BLAST RADII, and the procedurally correct one is the larger act

**An earlier revision of this section called the alternative the choice "if there is no hurry",
implying it was the same outcome reached more safely. That was wrong and is withdrawn.** The
correction is the integration lane's, made while reviewing its own repair.

Committing the first complete receipt to `docs/orchestration/state/r5-meter-receipt.json` does not
admit one item. **It arms compute admission for the entire queue.** That path is the gate's only
input, `R5_MAX_AGE` is 24 hours, and once a valid fresh receipt is committed every ready compute item
is measured against headroom rather than refused for want of a receipt. So:

| | path 1 — one-off exception | path 2 — wait for the repair |
|---|---|---|
| what it authorizes | **one** declared, attended, 30-minute allocation | **every** compute item the queue holds or later admits |
| the gate afterwards | **stays shut** | **open for ≤24 h, then stale-shut — repeatable** (§4c) |
| procedural correctness | an exception, recorded as one | the front door |
| reversibility | expires with the allocation | the receipt can be removed, but anything admitted meanwhile already ran |

**The more procedurally correct path is the larger commitment.** That is not an argument against it —
a gate that is never opened is a gate nobody has tested, and the queue exists to be used. It is an
argument against treating it as the cautious default, which is how §4 previously read.

### 4c. The opening is TIME-BOUNDED, which narrows path 2's radius without making it small

**Measured after §4a was written, and it corrects §4a's own table.** §4a said path 2 leaves the gate
"open" full stop. It does not: the opening **expires**.

`r5_refusal_reason` refuses a receipt whose `measured_at_utc` is older than
`R5_MAX_AGE = 24 hours` (`campaignctl.py:292`, checked at `:3358`), with a 60-second future-skew bound
the other way (`:296`). So a committed receipt admits compute for **at most 24 hours from the instant
it was measured** — not from when it was committed — and then the queue stale-refuses again until
someone re-measures and re-commits.

**What that does change:** path 2's radius is "every compute item, for up to a day", not "every
compute item, forever". The gate is **repeatable-and-expiring rather than permanent**, and its default
resting state is shut. That is a materially smaller commitment than §4a implied and Joseph should
weigh the corrected version.

**What it does not change, and why the act is still not small:**
- Within that window **every ready compute item is admissible**, not merely this inspection.
  `committed_r5_receipt(queue)` takes the queue and no item (`:3080`), and `r5_refusal_reason` consults
  it for every compute item — one commit clears that refusal for all of them.
- **Anything admitted in the window has already run.** Expiry closes the gate; it does not undo what
  went through. The commit is reversible, the compute is not.
- It is **repeatable**, so "it expires" is a property of one receipt, not a bound on the practice.

*(Expiry measured and its significance framed by the Z-specification lane, in its §5.6a. This lane's
§4a understated the bound and is corrected here rather than edited silently.)*

**Neither path is obviously right and this lane does not recommend one.** The choice is between a
narrow exception that leaves the gate shut, and opening the gate for everything in order to put one
small inspection through it correctly. That is Joseph's to weigh.

**Timing, from the lane that owns the repair (2026-09-06):** branch expected the same day; landed in
one to three days **if an independent review passes first time**, longer if it returns BLOCK — the
last comparable round did. Stated as "days, not weeks, but contingent on a review that lane does not
own". **If the decision is needed sooner than that, it should not wait on the repair.**

**Two things that do NOT follow from the repair landing**, recorded so neither is assumed:
1. **It does not unblock this inspection.** It clears 3.1 only. Blockers 3.2 (TTY approval), 3.3 (item
   shape) and 3.4 (no committed contract) are untouched by it. Necessary, not sufficient.
2. **It does not arm the gate by itself.** The repair writes no receipt, and an operational receipt
   cannot be manufactured from a preserved historical capture. Arming is a separate, deliberate act —
   and must not happen as a side effect of someone running the repaired tool once to see if it works.

### 4b. ⚠ The command that arms the gate is the one the documentation tells you to run

**Measured, because §4a's caution is abstract and this is what makes it live.**
`docs/orchestration/R5-METER.md:13-16` gives the tool's canonical usage, verbatim:

    python3 docs/orchestration/r5_meter.py measure \
      --write docs/orchestration/state/r5-meter-receipt.json

**That command is the arming act.** It writes a receipt to the exact path `campaignctl` reads as its
compute-admission gate, and once a valid one under 24 hours old is committed there, every ready
compute item is measured against headroom instead of refused.

**So the hazard is not a careless flag — it is a careful reader.** The tool is safe by default:
`measure`'s `--write` has **no default** (`r5_meter.py:751`), so a bare `measure` writes nothing, and
the only default aimed at the gate path is `check --receipt` (`:753`), which reads. The danger is
that someone verifying the repaired meter does the conscientious thing, opens the tool's own
documentation, runs the documented command, and arms the queue. **Following the instructions is the
dangerous path**, which is worse than a footgun, because the people most exposed are the ones being
most diligent — an independent reviewer of the repair above all.

**The operational rule:** verify with `measure` and **no** `--write`, or `--write` to a scratch path.
**Never run `R5-METER.md`'s example as a smoke test.** The example is not wrong for the act it
describes; what it omits is that the act is a queue-wide decision.

The `check` default cuts the safe way: with no receipt at that path, `check` fails closed. **The gate
is currently shut by absence**, which is the right kind of shut.

*(Mechanism found by the integration lane. This lane first asserted that `measure --write` defaulted
to the gate path — it does not, and that claim was withdrawn. The instinct was right and the
mechanism was wrong; the real one is worse.)*

## 5. Status

**DECLARED, COMMITTED, NOT SUBMITTED.** No job was submitted. No credential was created or changed.
No unattended execution was configured. No frozen checkout was modified. No admission control was
bypassed, and none was tested against a fabricated receipt. Awaiting Joseph's separate decision on §4.
