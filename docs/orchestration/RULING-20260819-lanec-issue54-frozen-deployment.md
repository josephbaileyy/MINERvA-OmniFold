# RULING — the frozen deployment `377c713d` does **NOT** have to be re-cut, and the reason is structural: **the read-back is neither invoked nor pinned by the train launcher, so the buggy copy in the freeze is INERT**

**By:** lane C (PET), as launcher/freeze-policy owner, answering the mediator's dispatch of 2026-08-19.
**Answer:** **NO RE-CUT. Not now, and not when the defect is fixed at `HEAD` either.** The dispatch's own
third option is not merely *available* — it is the **only** thing currently possible, and §2 shows why.

| | | authority |
|---|---|---|
| **§1 must `377c713d` be re-cut for this defect?** | **NO.** Three independent reasons, any one sufficient. | **RULED.** Mine as freeze-policy owner. |
| **§2 does validation run inside the frozen tree?** | **NO — and it runs nowhere at all yet.** No launcher invokes it. | **MEASURED**, not ruled. |
| **§3 does the widening touch another frozen tree or receipt?** | **YES, one: the hash-pinned replica-family validator.** Bounded in §4; no receipt is invalidated. | **MEASURED + RULED.** |
| **§4 may the queued run be cancelled/resubmitted instead?** | **NOT BY THIS RULING.** Resubmit is not pre-authorised and I do not grant it. | **DECLINED.** Not mine. |

> **THE ONE-LINE FORM, so this stops being re-raised:** *`cstat_data_only_readback.py` is absent from the
> train launcher's five-file pin list and from every `sbatch_*.sh` in the repository; the frozen tree's copy
> of it therefore never executes, and a defect in code that never executes cannot be a reason to re-cut the
> tree that carries it.*

**Everything below was derived this turn from the tree at `783d648a` and from `origin/main` as fetched at
ruling time, not recalled.** Where I contradict the dispatch I say so and show the command.

---

## 1. THE THREE REASONS, ORDERED BY HOW HARD THEY ARE TO OVERTURN

**(a) STRUCTURAL — the read-back is not in the executing set.** `sbatch_gate5_data_only_train_array.sh`
pins exactly **five** executing copies by name, and verifies each against the committed tree via
`verify_executing_copy_is_committed.py --pair` (`:104-110`; `grep -c -- --pair` → **5**):

```
train_fullevent_replica.py   train_fullevent_nominal.py   fullevent_fps_dataloader.py
cstat_data_only.py           verify_executing_copy_is_committed.py
```

`cstat_data_only_readback.py` is **not among them**, and neither is
`validate_gate5_data_only_artifacts.py`. So the parity gate does not read the buggy file, and nothing in
the job does either.

**(b) EMPIRICAL, from a covering search rather than a single grep.** The dispatch asked me to verify its
own claim and not take its word. `grep -rn 'validate_gate5\|readback\|validate_.*artifacts' --include='*.sh'`
over the tree returns **five hits, none of them this family**: three are the *extraction* and *replica*
families' validators, one is an `hpss` comment. Widening to the module names with no extension filter, the
**only** non-test, non-doc reference to `cstat_data_only_readback` anywhere is
`validate_gate5_data_only_artifacts.py:61` — one Python module importing another. **The chain terminates
there: nothing invokes the importer.** *This is inference from absence, so the search is stated so it can
be falsified: it covers the whole worktree minus `archive/`, matches the module names both with and
without `.py`, and would catch a `${VAR}`-constructed path only if the literal stem survived — a caller
that assembles the name character-by-character would evade it, and I did not find one.*

**(c) POLICY — re-cutting is the *more* damaging option, and it buys nothing.** `377c713d` is named in the
divergence-manifest addendum, in `gate5-do-train-array-active-57266000.json`, and in the armed watch's
context. Re-cutting changes what executes under a receipt already recorded — the exact substitution that
receipts exist to prevent. **Paying that cost to fix a file the job does not open is a pure loss.** Under
this repo's own rule that a pinned reader gets a wrapper rather than a copy
(`RULING-20260817-lanec-pinned-readers-get-wrappers-not-copies.md`), the remedy for a defective reader is
never to re-cut the producer's deployment.

---

## 2. §2 ANSWERED, AND MORE STRONGLY THAN THE DISPATCH SUPPOSED — THE VALIDATION STEP IS **UNWRITTEN**, NOT MERELY UNFROZEN

The dispatch's third option supposed validation might be *"a separate, later, unfrozen step."* Measured: the
data-only controller `submit_gate5_data_only_n50.sh` submits **exactly two** things — the target array and
the train array (`:288`, `:270`/`:305`). There is **no validate submission of any kind**.

Contrast the families that *do* have one. The replica family ships
**`sbatch_gate5_training_family_validate.sh`**, a separate CPU-QoS job whose code root is a **distinct,
separately-pinned variable**:

```
CODE_ROOT=${GATE5_VALIDATOR_CODE_ROOT:?submitter must export immutable committed worktree}
EXPECTED_HEAD=${GATE5_VALIDATOR_EXPECTED_HEAD:?missing validator HEAD pin}
```

**That is the precedent, and it settles the policy question by construction: in this repo a family's
validator has ALWAYS run from its own pinned code root, never from the train deployment.** The train
freeze and the validator pin are separate objects on purpose. So for the data-only family the freeze is
**irrelevant to this defect** — not by luck, but because the architecture never routed validation through
it.

**Consequence, and it is the actionable part:** whoever wires the data-only validate step supplies
`GATE5_VALIDATOR_CODE_ROOT` **from a tree containing lane B's fix**. The fix reaches validation by being
committed, and by nothing else. No re-cut, no repin, no resubmit.

---

## 3. THE DEFECT RELOCATED — IT IS A **COPIED LITERAL FROM ANOTHER FAMILY'S LAUNCHER**, AND ONE HALF OF THE DISPATCH'S ACCOUNT IS WRONG

The read-back requires **exactly one** occurrence of each of five needles in member stdout
(`cstat_data_only_readback.py:424-436`), two of which name a producer:

```
:425  ("log_start_line", f"[gate5-train] index={idx} seed={seed} job={array_job_id}_{idx}")
:429  ("log_done",       f"[gate5-train] DONE index={idx} seed={seed}")
```

`grep -rn` for those two strings outside `tests/` returns **four** sites: the read-back itself, the pinned
replica validator `validate_gate5_training_artifacts.py:338,343`, and — as the **sole producer** —
**`sbatch_gate5_replica_train_array.sh:62,72`.** The data-only launcher emits `[gate5-do-train]`
(`:113`, `:124`).

**So the mechanism is: the read-back's expectations were copied from the replica family's validator, whose
token literals belong to the replica family's LAUNCHER.** `[gate5-do-train] index=` does not contain
`[gate5-train] index=`, so `count` is **0**, `!= 1`, and the read-back raises **after a successful train** —
the false alarm the dispatch describes, confirmed. It is present at `377c713d` (`git show
377c713d:…readback.py` → same lines 425/429), so the freeze does carry the buggy copy. **Inert, per §1.**

### 3a. ⚠ CORRECTION TO LANE E's ACCOUNT — THE DRIVER DOES **NOT** EMIT THE START/DONE LINES, SO IT DOES NOT RESCUE `exact_one`

Lane E reported that the driver `train_fullevent_replica.py` "still raises `SystemExit("[gate5-train] …")`
on ~30 guards," offered as the second producer in a shared token family. **The raising is real and
undercounted; the implication is not.** Measured:

```
grep -oE 'SystemExit\(f?"\[[a-z0-9-]+\]' train_fullevent_replica.py | sort | uniq -c
  37 SystemExit("[gate5-train]      4 SystemExit(f"[gate5-train]      -> 41, not ~30
  10 SystemExit("[gate5-dataonly]   1 SystemExit(f"[gate5-dataonly]
```

But **all 41 are `raise` sites, and none is a start-line or a DONE-line.** The two needles `exact_one`
counts are `echo`s from the replica *launcher*, which the data-only path never runs. **E's warning that a
blanket prefix substitution would fix one half and break the other stands, and is if anything stronger at
41 sites — but it is a warning about editing the PRODUCERS, and the correct fix does not touch them.**

**RULED: fix the READER, not the producers.** The read-back's needles must be parameterised on the
launcher token (or take it as a caller argument, as `array_job_id` already is — `:441` records it as
*"caller-supplied, NOT a module literal naming one run"*, which is the pattern to copy). **Do not
substitute `[gate5-train]` → `[gate5-do-train]` anywhere in `train_fullevent_replica.py` or
`sbatch_gate5_replica_train_array.sh`:** the first would corrupt 41 guards shared with the replica family,
the second would break the replica family's own passing validator. *Lane B owns the file; this is the
constraint on the fix, not an instruction to make it.*

---

## 4. §3 ANSWERED — THE WIDENING TOUCHES **ONE** OTHER PINNED ARTEFACT, AND **NO RECEIPT IS INVALIDATED**

Lane E's second measurement is **confirmed independently**: `python3 -c 'raise SystemExit("[gate5-train] boom")'`
prints `[gate5-train] boom`, rc=1 — **bare message, no `SystemExit:` text, no traceback.** So of

```
FATAL_LOG_TOKENS = ["Traceback (most recent call last)", "[gate5-train][FAIL]", "SystemExit:"]
```

`SystemExit:` **can never fire from a `raise SystemExit(msg)`**, and on the data-only path
`[gate5-train][FAIL]` cannot either — its only producer is the replica launcher's `die()`
(`sbatch_gate5_replica_train_array.sh:39`), while the data-only launcher's `die()` emits
`[gate5-do-train][FAIL]` (`:57`). **Only `Traceback` remains live.**

**The widening:** that identical three-token list also sits at
**`validate_gate5_training_artifacts.py:344`** — the **hash-pinned** replica-family validator, pinned via
`GATE5_ARTIFACT_VALIDATOR_EXPECTED_SHA` in `sbatch_gate5_training_family_validate.sh:21`. So the dead-token
defect is **not** specific to the data-only family, and the dispatch is right that it is wider than the
defect as filed.

**AND IT IS A LOSS OF REDUNDANCY, NOT A HOLE — which is why no completed gate needs re-litigating.** In
both validators the fatal-token scan is *preceded* by the exactly-once scan, and `log_done` is a
**positive** success witness written last: a member whose driver raised never prints its DONE line, so the
count is 0, and the validator raises **before** reaching the token scan at all. **A failed member fails
closed on the positive witness regardless of how many fatal tokens are dead.** On the replica path
`[gate5-train][FAIL]` *does* have its producer, so only `SystemExit:` is dead there.

**RULED:**
- **Gate 5's completed replica-family verdict is NOT reopened by this.** Its `log_done_count == 1` check is
  live, producer-matched, and sufficient; a dead redundant token did not manufacture that PASS.
- **`validate_gate5_training_artifacts.py` is hash-pinned, so repairing its token list changes a pinned
  digest.** That is a repin, it is **not** authorised by this ruling, and it must not be smuggled in as
  part of an ISSUE fix. File it; do not do it. **No other frozen tree is touched.**

---

## 5. TWO PREMISES OF THE DISPATCH THAT DO NOT HOLD AS STATED

**(a) `ISSUE-54` DOES NOT EXIST IN ANY COMMITTED TREE.** `grep -n 'ISSUE-54' KNOWN_ISSUES.md` → no match
here; against a freshly fetched `origin/main`, also **no match**, where the maximum allocated id is
**`ISSUE-53`**. The id is presumably claimed in the records lane's **uncommitted** working copy — which is
consistent with `54` being next-free, so this is a sequencing artefact rather than a wrong number. **But it
means this ruling cannot be keyed to it, and is not.** *A ruling that cited an id no committed file defines
would be unfalsifiable in exactly the way `a definite description is not a citation` warns about.* I have
keyed every claim to `path:line` instead. **Whoever lands `ISSUE-54` should add the back-reference; I am
not touching `KNOWN_ISSUES.md` (records lane owns it).**

**(b) THE RUN HAS NOT STARTED, AND THE DISPATCH'S URGENCY FRAMING DEPENDS ON IT HAVING STARTED.**
`gate5-do-train-array-active-57266000.json` (on `origin/main`; absent from this worktree, which is behind)
records the job **PENDING**, `runtime 00:00:00`, reason **`ReqNodeNotAvail, Reserved for maintenance`** —
reservation `maintenance_20260819`, **5248 nodes, `2026-08-19T13:00Z → 2026-08-26T13:00Z`.** **Zero A100-h
consumed.** So the "successful 3 A100-h train followed by a false alarm" scenario is not imminent; there is
a week of slack, and the cheapest fix — **lane B lands the read-back fix, and the validate step is later
wired against a tree that has it** — completes comfortably inside the window with the freeze untouched.

*I could not re-measure this myself: `ssh saul.nersc.gov hostname` → **rc=255**, read unpiped. So the run
state above is CITED to that receipt, not observed by me, and the receipt's own header says it was authored
by the mediator after submission and is not an authorization. Treat the maintenance end date as the receipt
labels it — **an outer bound, not a prediction**; the job may start earlier.*

---

## 6. WHAT THIS RULING DOES AND DOES NOT AUTHORISE

**Authorises nothing new.** Specifically **NOT** authorised, and each was a standing constraint before this
ruling: the **151 A100-h `M(ii)` family**; **any resubmit or `scancel`** of `57266000`; **any repin** of
`validate_gate5_training_artifacts.py`; any rename or deletion of the **115 load-bearing `sbatch_*.sh`**
names; any **deletion or top-level reorg** (frozen behind `docs/POST_PUBLICATION_REORG_PLAN.md`).
Authorization receipts are committed before they are acted on, and this document is a **ruling, not a
receipt**.

**Forbids:** re-cutting or repointing `/pscratch/sd/j/josephrb/gate5-data-only-frozen-377c713`, or altering
`377c713d`'s citation in the addendum, the active-run receipt, or the armed watch's context, **on the
grounds of this defect**. A different defect — one in the **five pinned executing copies** — would be a
different question with a different answer.

**Requires**, of whoever wires the data-only validation step: a **separate** submission with its **own**
pinned `GATE5_VALIDATOR_CODE_ROOT` and `GATE5_VALIDATOR_EXPECTED_HEAD`, per the precedent in §2, from a
tree containing lane B's fix. **Does not require** a new `sbatch_*.sh` from me; that file is lane E's to
create and is outside my file set.

**Consistent with, and deliberately not disturbing:** the `codex-waker` profile (`gpt-5.6-luna`, effort
low) recorded as **OI-135 step (f)**, inert until `profiles.json` and `waker-config.json` deploy
**together**; and `PB-11`'s re-aim at the monitor per my own prior ruling at `a70e127a`. **Nothing here
touches the waker, and nothing here needs the cluster.**

## 7. WHY THIS SHOULD NOT BE RE-RAISED

The question recurs because "the freeze carries a buggy file" is true and sounds sufficient. **It is not
sufficient, and the disqualifying test is one command:**

```
grep -c -- --pair nd-unfolding/pet/sbatch_gate5_data_only_train_array.sh     # 5
grep -n 'readback' nd-unfolding/pet/sbatch_gate5_data_only_train_array.sh    # no match
```

**A freeze must be re-cut when a file that EXECUTES under it is wrong. It must not be re-cut when a file
that merely SITS in it is wrong.** `cstat_data_only_readback.py` is in the second class today. **If a
future change adds it to the launcher's pin list, this ruling expires at that moment** — and that, not the
file's contents, is the condition to re-check before re-raising.

*Filed by lane C. §1–§3 and §5 are measurements taken this turn at `783d648a`; §4's `SystemExit` behaviour
is a measurement on this host's `python3`, and the guards it concerns run on Perlmutter, where I did not
re-measure it — the semantics of `raise SystemExit(str)` are interpreter-level and version-stable, but that
is an argument, not a measurement, and it is the one claim here I would check first if this ruling turns
out to be wrong.*
