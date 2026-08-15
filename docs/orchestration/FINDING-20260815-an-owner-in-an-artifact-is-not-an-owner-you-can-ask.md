# An owner recorded in an artifact is not an owner who can be asked

**Filed 2026-08-15 by the propagation-correction lane** (`BEN-324`, block `320-329`), on the mediator's
instruction. Subject items `OI-81`, `OI-58`, `OI-127`. **This is not a finding that a session failed to
reply.** It is that **a contract with a named owner has no reachable owner, and the campaign discovered
that only at the moment it needed a ruling.**

## 1. What happened

`nd-unfolding/pet/gate5_cstat_contract.json` records its owning lane in its own `lane` field. When a
proposal needed a ruling on whether a reduced-`n` diagnostic is coherent under that contract, the ruling
had no addressee: `minerva-omnifold-f7` was asked twice, directly, and did not answer. The mediator had
told it explicitly that *"the owner is not reachable"* is itself an actionable answer where silence is not.

**The decision was reached anyway, correctly** — a decision **not** to run needs no spec interpretation, so
the 4-0 consensus on `(0)` stands without it. The exposure is that the *next* proposal of this shape needs
that ruling, and so does `OI-81`, whose script is the same lane's.

## 2. Why the field does not help

**`lane` is provenance, not a routing table.** It records who authored a contract at a moment in the past.
Nothing maps it to a live session, and there is no mechanism that could:

* `ListAgents` reports which sessions are **alive**, never what they own or what they are doing.
* Sessions are **renamed and respawned keeping their names** — this session was `minerva-omnifold-8e`
  and is now `A`, mid-task, and the mediator had two sessions claim `minerva-omnifold-8e` inside a minute
  from different sockets.
* A lane label like `C` is **not an address.** The mediator compounded this by naming a *different* peer
  `C` and treating it as the spec owner; **that peer refused, correctly.** Two distinct referents for one
  label is `BEN-080`'s shape in the lane namespace rather than the id namespace.

So an artifact's `lane` field, a `RUN_LOG` attribution and a row's owner column are all the same kind of
object: **a durable record of past authorship, being read as a current routing destination.**

## 3. This is `BEN-300` one level out, and the difference matters

`BEN-300` established that **the holder of a task is a hand-maintained fact with no machine-derivable
source**, and that a rule nobody can comply with is not a rule. This is the same defect applied to
**ownership of a decision right** rather than to a work assignment, and it is worse in one specific way:

**a task can be re-dispatched to whoever is available; a spec ruling cannot.** If the lane that authored
`gate5_cstat_contract.json` is gone, the authority to interpret it does not transfer by availability. It
escalates to Joseph or it stalls. **So the unreachable-owner failure is not recoverable by the mechanism
that recovers an unreachable worker.**

## 4. It is not one item — that is why it is filed

Two items on the publication critical path are blocked on owners nobody can reach:

| item | what is blocked | owner as recorded | reachable? |
|---|---|---|---|
| `OI-81` | the canonical-nominal designation's safety argument (guard RED since designation) | lane C — `check_canonical_designation.py` is C's script | **no**, two asks unanswered |
| `OI-58` / `OI-57` | the `inputs_sha256` stamping defect | needs whoever owns the Gate-6 Leg 0 launcher and its receipt | **not identified** |

A single unanswered session is an anomaly. **Two, on the critical path, at the same time, discovered only
when a ruling was needed, is a structural property of how this campaign records ownership.**

## 5. The rule

> **An owner recorded in an artifact is not an owner who can be asked. Before a decision is made to depend
> on a named owner's ruling, establish that the owner is REACHABLE — and if they are not, say so and
> escalate, because "unreachable" is a finding and silence is not.**

Corollaries, each cheap:

* **Ask for the ruling before you need it**, when it is still an ordinary question rather than a blocker.
* **Record unreachability as a state.** *"Asked twice on 2026-08-15, no answer"* in the row is worth more
  than the owner's name, because it is the fact the next lane needs.
* **A decision that does not require the ruling should be identified as such and taken.** The `(0)` vote is
  the model: it needed no spec interpretation, and noticing that is what let it proceed.
* **Never invent an addressee.** Naming an available peer as the owner of another lane's spec produces a
  refusal at best and an unauthorised ruling at worst.

## 6. What would actually fix it, and why nothing is proposed here

The obvious remedy — a `docs/orchestration/OWNERS.tsv` mapping subjects to live sessions — **is the exact
object `BEN-228` and `BEN-300` warn about: a hand-maintained index of a fact with no machine-derivable
source**, maintained by the party with least reason to reread it. It would be stale the first time a
session was respawned, and its staleness would be invisible.

**So no mechanism is proposed, deliberately.** What is proposed is the cheap discipline in §5, and the
honest admission that this exposure is **known and accepted rather than fixed** — the same disposition
`CLAUDE.md` already records for the `BEN-*` per-lane ranges. `ROW-OWNERS.tsv` exists for `CLM-*` rows and
`OI-53` records that **all 12 are UNASSIGNED** with the gate exiting 2 on unassigned, which is the same
problem already measured in a namespace that *does* have the file.

**Stated plainly because it is the load-bearing limit: the enforcement of §5 is attention, not mechanism.**

## 7. What this finding does not establish

* **Why `minerva-omnifold-f7` did not answer.** It may be busy, dead, or have never received the messages;
  no diagnosis was attempted and none is claimed. **The finding is about the addressing, not the session.**
* **That the `OI-81` guard's RED needs C's ruling to interpret.** It does not — see `BEN-325`, which
  answers the substantive question read-only. C's ruling is needed to *change the script*, not to read it.
* **Whether any other artifact's `lane` field has a reachable owner.** Only `gate5_cstat_contract.json`
  was at issue; no survey was run.
