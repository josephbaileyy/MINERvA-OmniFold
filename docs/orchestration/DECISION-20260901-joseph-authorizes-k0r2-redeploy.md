# DECISION 2026-09-01 — Joseph authorizes advancing the k=0 deploy from `7ac0edec` to current `main`

**CITABLE FOR:** the authorization quoted in §1, its scope as drafted in §2, and the ordering
constraint in §3 — which is part of the ruling and does not travel separately from it.

**NOT CITABLE FOR:** cutting a live freeze short; a Gate-1 PASS; a Gate-2 clause; a readiness or
fitness finding; authorization to submit any job, arm, leg or member; leg 6; any M(ii) leg; `C_ML`; a
covariance construction or adoption; discharge of any quarantine cause; or any publication claim.
**Gate 2 remains FAIL.** CAND `1 of 7`, QUOTED `0 of 7`. A deployment is a position change; it
authorizes no science.

## 1. Authority — his own turn, to this lane, not relayed

Joseph, 2026-09-01, answering this lane's report that submission of the cause-3 `M(ii)` estimator-seed
scan was blocked because `nd-unfolding/mnv_env_provenance.py` is absent from the deployed tree, and
that a redeploy would also change preconditions for the other eight k=0 arms:

> *"Yes redeploy it and reconcile the other issues"*

**Those are his words.** Everything below the quote is **this lane's drafting**, written to scope an
authorization that arrived as one sentence. He did not type it into the repository. Read §2 and §3 as
ratified drafting in the shape of `DECISION-20260830-joseph-accept-forward-only-rehearsal.md`, not as
his text.

**What he was told when he ruled**, so the authorization can be read against its own premises:
`mnv_env_provenance.py` is absent from the deploy; the launcher dies in its tool-existence loop within
seconds without a redeploy; a redeploy brings `OI-179` defect-3 enforcement into the other eight
launchers and so changes their submit-time preconditions; and neither this lane nor the `claude-school`
lane had at that point established whether a live hold binds `7ac0edec`. **The last of those premises
was WRONG, and the error was this lane's.** §3 records what was found and why the authorization
survives it intact.

## 2. THE RULING

> **The deployed execution tree `/pscratch/sd/j/josephrb/k0r2/clean` may be advanced from
> `7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b` to ONE named commit on canonical `main`, detached, under
> the preservation and declaration discipline the previous pin move used — and the consequential
> precondition changes to the other eight k=0 launchers are to be reconciled rather than deferred.**

**THE TARGET IS A SHA, NOT A BRANCH NAME, AND THIS CLAUSE IS PART OF THE RULING.** An earlier draft
said *"to the current canonical `main`"*. That is a **definite description**, and this repository has
already been bitten by one re-pointing when a second object came to satisfy it. `main` moved twice
during the peer lane's session alone (`83666a09` → `050dbb72`). **The target sha is fixed and recorded
in the superseding pin row at the instant of the move, and this decision authorizes no other.** A
later reader who finds `main` elsewhere may not cite this record to move the tree there.

The second clause is his — *"and reconcile the other issues"* — and it is an instruction, not a
permission. The precondition delta is to be **measured and recorded**, not discovered by a later lane
at its own submit time.

## 3. THE ORDERING CONSTRAINT, which is part of the ruling

**This decision does NOT cut a live freeze short, and must not be cited as doing so.**

`FREEZE-20260830-k0-deployment-7ac0edec.md` §1 is **live**. Its expiry condition is verbatim:

> *"It expires when that rehearsal's F-1(b) producer filing is committed — not when its jobs merely
> look terminal."*

That filing **does not exist**. The only F-1(b) receipt in the repository,
`RECEIPT-20260830-k0-f1b-producer-filing.md`, is scoped by its own CITABLE FOR box to a measurement
taken `2026-08-29T22:08:01Z` against the deploy at `aa67c426`, and its §1 names the prior rehearsal's
combine job `57527875` ending `2026-08-25T16:24:42`. It is the **old** rehearsal's far end.

The rehearsal the live freeze names is round 2 of run `k0-7ac0edec-20260830T000215Z`, which completed
**374 of 374** with zero failures (`RECORD-20260901-k0r2-round2-outcome.md` §1, counted as distinct
`jobid_task` identities with `.batch`/`.extern` and array-bracket rows excluded — **not** from an empty
queue, which both that record and the freeze warn is not the condition).

> **THEREFORE: the round-2 F-1(b) producer filing is taken and committed FIRST, the freeze expires on
> its own stated terms at that commit, and only then does the authorization in §2 take effect.**

**This is not a hedge against his instruction; it is what makes his instruction cheap instead of
expensive.** Moving the tree first would destroy the far-end measurement of a completed 36-hour,
374-task, zero-failure run — a measurement recoverable only by re-running everything, and the one
thing that makes that run gradeable at all. The delay is hours; the alternative cost is the run.

**No precedent exists for superseding a LIVE hold.** `FREEZE-20260830-k0-deployment-7ac0edec.md` §2
supersedes the `aa67c426` freeze and says so explicitly — *"this deployment did not break a live hold;
it replaced a spent one."* Letting this one expire on its own terms keeps that precedent intact rather
than establishing a new and worse one.

**Independently checked before this record was written.** The peer `claude` session
`minerva-omnifold-c7` was asked to attack the reasoning above. What it confirmed, stated at the
strength it actually measured and no higher:

- **No round-2 filing exists.** It grepped every `docs/orchestration` file mentioning `F-1(b)` and
  `7ac0edec` for a producer filing; the five hits are all **pre-run** documents referring to the filing
  as future. Nothing claims to be it.
- **Round 1 and round 2 are rounds of the SAME run under the SAME pin**, so round 2's far end **is**
  *"that rehearsal's"* far end. It checked this as the strongest available attack on the claim, and the
  attack fails: `RECORD-20260901-…` §1 records *"Round 1 of this same run died… The only change between
  the two was one exported variable… No code, launcher or `MANIFEST` pin was altered."*
- **No COMMITTED route to a legitimate move existed at the time of the check**, and expiry is stated in
  exactly one place.

**That third limb is deliberately narrower than "nothing else can expire it."** Freeze §2 does
establish a supersession route in principle — the `OI-123` row — and the sentence above must not be
cited to refuse a future Joseph-level supersession. What is categorical is the sentence below, which
is this lane's own and is accurate as written.

## 4. What the move must carry, and what it must not disturb

**Items 1–6 are THIS LANE'S DERIVATION, not his enumeration.** He said four words —
*"and reconcile the other issues"* — and the list below is what this lane derived as their subject, from
what the `aa67c426`→`7ac0edec` move actually did rather than from memory. Read it as ratified drafting.
If he meant something narrower or wider, his reading governs and this list yields to it:

1. **The old pin is preserved before anything becomes writable, not alongside the move.** The existing
   bundle for `7ac0edec` is re-verified in full — including recovery from the bundle **alone** and the
   `git bundle list-heads` **exact-row** assertion, count 1, never a substring match.
2. **The freeze ref is confirmed present in BOTH repositories first.** §4 of the freeze records this as
   the thing that failed silently last time: `refs/tags/freeze/k0-aa67c426` had vanished from every live
   cluster repository and survived only inside the bundle. Cheap, read-only, and done before the move.
3. **The old freeze ref is not repointed and the old pin is not destroyed.**
4. **A superseding pin row** stating old value, new value, reason and authority, per `OI-123` — never a
   silent repoint.
5. **A new declaration and freeze**, instantiated under this decision rather than by the deploying lane
   on its own authority.
6. **The precondition delta for the other eight launchers is recorded**, per §2's second clause.

**Out of scope and explicitly not disturbed:** the canonical cluster checkout
`/pscratch/sd/j/josephrb/MINERvA-OmniFold`, the ten `refs/tags/evidence/*` anchors in the deploy tree
(other lanes' provenance, not this lane's to remove), the quarantine tree, and every sibling member.

## 5. The instrument, and a freeze risk that was raised and then did NOT obtain

This lane's first execution plan was to write a parameterised round-2 copy of
`measure_k0_farend_f1b_f17b.sh`. The peer lane flagged a freeze risk on it, citing
`FREEZE-20260830-k0-deployment-7ac0edec.md` §5, which records that this script *"was deliberately not
edited"* during the frozen interval because it is a tracked `.sh` and an edit would move the A-2(f)
listing digest.

**That risk was raised on the assumption that the TRACKED script would be edited, and it does not
obtain.** A-2(f) digests the **deploy** tree, which is detached at `7ac0edec` and does not follow
`main`; a new file added on `main` cannot move it, and `main`'s copy is bound only prospectively. This
lane established that and the peer withdrew the objection. **It is recorded here at that strength
deliberately: "would have violated the freeze" is NOT established, and must not stand in a committed
record merely because a peer said it.**

**What survives the exchange is the instrument point, and it is the one that governs.** The precedent
filing did not use that wrapper at all: `RECEIPT-20260830-…` §2 measured with **the instrument inside
the subject tree**, `nd-unfolding/mnv_source_manifest.py`, run once with all five fail-closed
`--require-*` flags, `--compare`, and a temporary `--write` destination **outside** the deploy tree. At
`7ac0edec` that in-tree copy is the **repaired** measurer — dissolving finding N1 was the entire reason
for the pin move. A wrapper that re-implements the measurement is unfaithful to that precedent and more
expensive; a wrapper that merely *calls* the in-tree instrument is neither.

> **The producer filing MUST name the instrument and the interpreter that produced its seven A-2
> values, as the precedent filing did.** Whether the values came from the in-tree measurer directly or
> through a wrapper that calls it, the filing states which — this decision does not settle it, and a
> filing that leaves it implicit is incomplete.

**Nothing inside the deploy tree is edited to take this measurement.**

## 5a. Preservation prerequisites, MEASURED before the move rather than assumed

Freeze §4 records that for the previous pin these were the things that failed silently:
`refs/tags/freeze/k0-aa67c426` had vanished from **every** live cluster repository and recoverability
survived only because the ref was read out of the bundle. Re-measured 2026-09-01, read-only, before
anything moved:

| check | result |
|---|---|
| `refs/tags/freeze/k0-7ac0edec` in the deploy tree | present, loose, at the pin |
| the same ref in the canonical cluster checkout | present, loose, at the pin |
| bundle at the declared path | present, **82,761,577 bytes** — the declared count exactly |
| bundle `sha256` | `514bd46e…0280d` — the declared digest exactly |
| `git bundle list-heads` **exact-row** match, count | **1** — an exact row, not a substring |
| the superseded `aa67c426` bundle | still present, 79,140,251 bytes |

**Terminality, measured to the freeze's own standard rather than from an empty queue.** `sacct -X` over
the seven round-2 ids returns **374 distinct identities, 374 COMPLETED, zero otherwise**.

**THE COVERING CONTROL, stated because a parent-id query does not carry it on its face.** This campaign
has a live `sacct -X` hazard on the record: an array throttle can promote tasks to their **own** JobIds,
so a query over the seven parent ids can silently miss a promoted task — and a promoted task that
FAILED would appear under none of the seven, leaving the count short rather than wrong. **It is not
short.** 374 measured reconciles exactly with 374 declared, and independently with `RECORD-20260901-…`
§1's 374 counted as distinct `jobid_task` identities (447 raw `sacct` rows). Two lanes counting by
different methods over the same population agree. That reconciliation — not the query — is what
establishes coverage.

**Dependency reason codes: the literal artifact is unobtainable, and a stronger one replaces it.**
`scontrol` no longer holds them, the jobs having aged out of the live scheduler records. The
conjunctive-`afterok` combine job `57753248` has a real `Start=2026-09-01T01:21:23`, `End=01:55:58`,
`Elapsed=00:34:35`, `ExitCode=0:0`. **Both failure modes the clause names are excluded by execution
rather than by inference** — it did not read as queued while terminal, and it was not absent through
never being submitted. A reason code could only have said why something did *not* run.

**`ExitCode=0:0` is cited with the product verification, not alone**, because an allocation-level zero
does not by itself prove the science step succeeded — a script can exit 0 over a failed inner step.
`RECORD-20260901-…` §3 carries the rest: **143 `.done` markers**; **100 bootstrap / 24 seedscan / 61
`uq_5d` `.npz` opened and every member read, 0 unreadable**; and combine's 9,178-byte stderr containing
**0 tracebacks**.

**Not yet done:** recovery from the bundle **alone**. It belongs before the move, not beside it, and
**rc=0 is not the pass condition** — freeze §4 declares what a passing recovery looks like and all six
values must match: `rc=0/0/0`, HEAD the pin, tree `5c23cad6…`, porcelain **0**, **1804** tracked files,
and the recovered clone independently measuring **820 files / `8d036d94…`**. A recovery reported as
`rc=0` proves the command ran, not that it recovered the declared bytes. The six-item recipe is taken
from `7ac0edec`'s **own** receipt, `state/RECEIPT-20260830-k0-deployment-and-freeze-bundle-7ac0edec.json`,
and the result is filed in the shape of `state/RECEIPT-20260830-aa67c426-preservation-remeasurement.json`
— which records `bytes_expected` beside `bytes_measured` per item, so each is falsifiable on its face,
and which kept a `why_this_is_not_a_mismatch` field for an anomaly its own author caused rather than
dropping it. Anything odd here gets the same treatment.

**One leg already reconciles against that receipt:** the superseded `aa67c426` bundle measures
79,140,251 bytes against its recorded `bytes_expected: 79140251`.

## 6. What this decision does NOT establish

It does not grade the round-2 rehearsal, discharge `F-1(b)` or `F-17(b)`, or move Gate 1 or Gate 2. It
does not ratify `OI-185`, and nothing in this record depends on it. Uncommitted working-tree edits to
`nd-unfolding/mnv_preflight_census.py` and `nd-unfolding/mnv_preflight_exclusions.json` were present
while this record was drafted, authored by neither this lane nor either lane it dispatched. **They are
another lane's authorized work in progress** — `minerva-omnifold-38`, holding Joseph's direct word, and
filing its own decision record and `OPEN_ITEMS` move before committing. **An earlier draft of this
paragraph read them as asserting a ruling not yet made; that reading was WRONG and is retracted here
rather than deleted.** The `14/38` boundary was already committed at `865b42d7` under his `OI-179`
authorization, flagged rather than absorbed; the pending part changes only how the ruling is enforced,
and `guarded` stays pinned at **14**. This lane commits with explicit pathspecs and diffs its own hunks,
which is the ordinary discipline for a shared checkout and not a comment on that work. It does not
authorize the
cause-3 `M(ii)` submission, which has its own predeclared authority and its own preconditions. And per
`FREEZE-…-7ac0edec.md` §5, the next rehearsal's own gate — a fresh independent full-chain FIT, §10.1
readiness, and a Gate-1 PASS — is **separate from the freeze and does not travel with this redeploy**.

## 7. THIS RECORD GOES BACK IN FRONT OF HIM, and that is the honest close

He said *"yes redeploy it."* §3 says *"not yet."*

**That is a material change to what he authorized, made by the lane that received the authorization,
under a premise he was given that turned out to be false** — this lane told him no live hold was known
to bind `7ac0edec`, and one does. The delay is defensible on its merits and this lane would make the
same call again; the run it protects is not recoverable, and the delay is hours. **But a lane that both
receives an authorization and rewrites its timing has ratified its own drafting**, and the distinction
between ratified drafting and self-ratifying drafting is the whole reason these records carry provenance
boxes.

So: §3's ordering stands as this lane's operating decision and is defended above — **and it is put back
in front of him for confirmation, not filed as settled.** If he rules that the move goes first, the cost
is stated plainly in §3 and the call is his.
