# Two correct rulings compose into a defect when each is safe only under a precondition the other silently removes

**Lane B, 2026-08-19. `BEN-485`.** Two instances between lane C and lane B in one day, on unrelated
subject matter. Neither author could have seen either one alone.

---

## THE ONE PARAGRAPH

A ruling is written, reviewed, and correct **within its own scope**. Its safety, however, rests on a
precondition its author did not have to state because nothing in view threatened it. A *second* correct
ruling then removes that precondition — for its own good reasons — and the composition is a defect that
**exists in neither ruling and in neither reviewer's field of view.** The reason it survives review is
structural, not careless: **each author is reasoning inside their own ruling's scope, and the precondition
lives in the other's.**

**The tell is a diff that reviews as a no-op.** Both instances below break a gate via a change any
reviewer would wave through.

---

## 1. Instance A — a freed buffer and a live view

| ruling | author | correct because |
|---|---|---|
| explicit `obj.Delete()` after each key | C (§19b) | `GetListOfKeys()` holds every object until `f.Close()`; a live TH2D costs ~2 GB, so "one key at a time" must actually release |
| read content bins as `[1:ny+1, 1:nx+1]` of an `(ny+2, nx+2)` buffer | B | under/overflow bins must be excluded from a payload digest |

`np.frombuffer` returns a **view**. The returned array was independent **only because the padding-aware
slice is non-contiguous**, which is what made `np.ascontiguousarray` copy. That property is *incidental to
why the slice was written that way*.

**Remove the padding arithmetic — a plausible simplification — and the slice becomes contiguous,
`ascontiguousarray` returns its input unchanged, and the function returns a live view into a buffer that
`Delete()` has freed.** Use-after-free, composed from two correct rulings, reachable by a diff that reads
as tidying.

**Pinned:** `assert not np.shares_memory(out, flat)`, plus `np.array(..., copy=True)` so the copy is not
incidental. A test mutates the source after the read and requires the returned array unchanged.

## 2. Instance B — the pause deletes its own successor's input

| ruling | author | correct because |
|---|---|---|
| stop after step (3); do not produce the adopted roots | B, confirmed by the mediator | remedy (A) is unlanded, so those artifacts cannot carry an identity stamp and stage 1 could not admit them |
| §11g releases the 41.44 GB member intermediate once `MVFINAL_j` validates | C | it is an intermediate; the bar's operands live downstream |

`MVFINAL_j` is produced by steps **(4)/(5)** — the steps the pause does not run. So *"stop after (3)"*
plus *"§11g releases the intermediate"* would **delete the only input to the steps that have not run.**

C caught this one from inside its own ruling, which is the exception rather than the rule, and only
because the pause had been reported to it explicitly.

## 3. What distinguishes this from an ordinary interaction bug

- **Neither ruling is wrong, and no revision of either is the fix.** Both stand; what is missing is a
  statement of the precondition, which neither author had a reason to write.
- **It is invisible to single-scope review.** A reviewer checking C's ruling finds it correct. A reviewer
  checking B's finds it correct. The composition has no owner.
- **It is not "integration testing would catch it."** Instance A is latent — the code is correct *today*
  and becomes wrong on a future edit. There is no run that fails.

## 4. The check, and it is cheap

**When a ruling's safety depends on a property of code it does not itself control, PIN THE PROPERTY WHERE
THE CODE IS, not in the ruling.**

    assert not np.shares_memory(out, flat)          # instance A
    "DO NOT DELETE ${COMB}" + the reason, at the pause   # instance B

Both are one line. Both fail **exactly** when the other ruling's author would have made a change they had
every reason to think was safe. This is the same instrument as lane D's summation-route finding: the
bit-exactness of a recomputation depends on **numpy pairwise summation being on both sides**, a property
of the *route* and not of the mathematics, so the control asserts both that pairwise matches **and** that
a naive sequential sum does not.

**The general form: an invariant that spans two authors must be asserted in code, because prose lives in
one author's document and the violation happens in the other's.**

## 5. Why two instances in one day, and what that predicts

Both arose in a multi-lane review where rulings are issued by one lane and implemented by another —
which is exactly the configuration that maximises this class: **high review quality per scope, and no
reviewer whose scope is the composition.** The prediction, offered so it can be checked: the next
instance will also come from a ruling pair issued days apart, where the second author has read the first
ruling's *conclusion* and not the reasoning that made it safe.

## 6. What this does not claim

- **Two instances, not a census.** I have not swept the campaign's other ruling pairs for the same shape.
- Neither instance caused a wrong number. Instance A is latent; instance B was caught before either
  ruling was implemented.
- The fix for each is a pin, not a policy. **I am not proposing that every ruling enumerate its
  preconditions** — that is unbounded work with no natural stopping point, and it would be the
  over-broad remedy this ledger has repeatedly warned about.
