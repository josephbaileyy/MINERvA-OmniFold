# An unlock trigger written to remove judgement is a stored measurement — and the commit that satisfies it can be the commit that breaks it

**BEN-394.** Filed 2026-08-17 by the seconding lane (block `390-399`). **The trigger was reported to me as
fired; I measured it as not fired, and the commit that flipped it is the one announced in the same message.**
Nothing was wired. The wiring decision is not this lane's and is routed to Joseph below.

## The trigger

`.githooks/pre-commit:47-49`, verbatim:

> **UNLOCK TRIGGER, single and checkable:** when `python3 nd-unfolding/pet/check_canonical_designation.py`
> exits 0 on a clean tree, move this to the run list as check 7. **No other condition, no judgement call —
> run the command.**

## Measured, both sides named

| tree | verdict | exit |
|---|---|---|
| `8a34f12^` | `[designation] PASS — every namespace occurrence IN CODE (33 of 230) has an explicit disposition` | **0** |
| `a05feee` (HEAD, current `origin/main`) | `[designation] FAIL — the designation's safety depends on this being empty` | **1** |

The FAIL names two `UNACCOUNTED FILE`s:

- `docs/orchestration/state/regen_canonical_namespace_field_pins.py` — 1 occurrence, 1 in CODE, first operand at `:114`
- `nd-unfolding/tests/test_hash_bindings.py` — 5 occurrences, 4 in CODE, first operand at `:292`

**Both come from `8a34f12`** (`A` and `M` respectively, `+302` lines) — lane E's own commit, the one whose
push was announced in the same message that reported the trigger as firing. The control at `8a34f12^` is what
makes this causal rather than correlational: **the parent passes.**

**So the report was true when measured and false when sent, falsified by one commit — its author's own.**
This is `BEN-228`'s shape and *measure after the change, not before*, in the one place designed to need no
judgement.

## Why the "no judgement call" design is what makes it dangerous

1. **A trigger is a stored measurement wearing the grammar of a rule.** *"Run the command"* reads as an
   instruction whose answer is stable. The answer is a property of a tree, and the tree moves under it — five
   lanes push to this repo.
2. **The predicate is tree-global, so any lane can flip it, and none is told.** The check counts namespace
   occurrences across 80 files. A lane adding a test that mentions the namespace flips a latch in a hook
   header it has never read. There is no observer on either transition.
3. **A trigger written to remove judgement is the one place nobody re-derives the property**, which is lane
   E's own formulation and is the load-bearing sentence. The instruction's whole promise is that you do not
   have to think; its failure mode is that nobody does.
4. **The instrument is coupled to the corpus it measures, including its own documentation.** E measured the
   digest-site count going `24 → 25` because *the determination it wrote quotes the digest in its own table*.
   **Writing about a pin increments its count.** Same property, third direction: an instrument whose reading
   changes when you document it cannot have a stable stored value.

## The second, independent reason not to wire it — lane E's, and it survives a green

The trigger tests *"exits 0 today."* The dispatcher's own **admitting rule**, eleven lines above it at
`.githooks/pre-commit:11`, is lane D's (`OI-64`):

> *a check belongs here iff **a committer who did nothing wrong can always make it pass**.*

`check_canonical_designation.py` **reddens when a committer deletes a prose sentence** (`BEN-387`: the
occurrence count is not crude but *inverted* — silent on a sibling repoint, red on prose deletion). So it
fails the admitting rule **whether or not it is green today**, and the trigger cannot see that because
greenness is not the property the rule is about.

**Two independent reasons, one measured and one reasoned, and they fail differently:** mine says the
trigger's precondition is not met; E's says the precondition is the wrong one. Fixing the tree would answer
mine and leave E's standing.

## Not wired, and not this lane's call

**This lane did not wire it and is not the hook's owner.** Dispatcher changes in this repo go through an
authorization document — `AUTHORIZATION-20260813-hash-binding-gate-in-precommit.md` and
`AUTHORIZATION-20260813-oi-id-check-and-launch-code-floor.md` are the precedents, and the second records that
*being overruled on the design is not the same as being authorized on it*. **And `966d202` already declined
this exact wiring**, which is where the trigger came from. A peer routing the decision to another lane does
not create authority for it.

**Routed to Joseph, with the recommendation stated so it can be overruled:** do not wire it, and **replace
the trigger rather than waiting for it to go green.** A trigger that latches on a tree-global measurement,
with no observer on either transition, will be stale whenever it is next read. If a trigger is kept, it needs
the tree sha it was measured against — the same remedy `BEN-382` proposes for the `Checks:` trailer, and the
third notation of *evidence must be bound to what it is evidence about*.

## Resolved same day — and the resolution is the sharper half of the finding

Lane E reproduced the flip independently before acting on it (`8a34f12^` → 0, `8a34f12` → 1, `be06d45` → 1)
and fixed it at `890fa0f`. Three facts this row was filed without, all re-measured here at `890fa0f`:

**1. The commit that broke the trigger is the `OI-96` fix itself.** The pin generator and the tests that
power-test it both mention the protected namespace in code. **So the remedy for the item falsified the trigger
being reported on, in the same hour, and both were announced in one message** — measured before the fix was
written, never re-measured after. Causally linked and still not connected, which is worse than staleness and
better as evidence: no amount of care about *timing* helps when the two facts are the same act.

**2. A committed assertion shipped on a tree where it was false.** `be06d45` added to the hook header:

> `*** THE TRIGGER FIRED ON 2026-08-17 AND IS DELIBERATELY NOT HONOURED. DO NOT WIRE IT. ***`

Verified here at exit 1. **This is `BEN-382`'s durable-PRESENCE defect in a third artifact — a hook comment —
and what kept it harmless is that the `DO NOT WIRE IT` conclusion was right while its premise was false.**
Safety by correct conclusion, not by true premise, is the thing that does not generalise.

**3. Restored to exit 0**, verified: `PASS`, 33 of 294 in-code occurrences dispositioned, via **five
line-level `# NS-EXEMPT` markers** (1 in `regen_canonical_namespace_field_pins.py`, 4 in
`test_hash_bindings.py`, counted at HEAD rather than quoted). The lighter of the two sanctioned remedies — it
leaves lane C's inventory untouched, and the guard **prints every exemption on every run**, so the narrowing
lives in the output rather than in a document.

### Two upgrades to this row's remedy, both lane E's

**Bind a trigger to the sha AND state what would invalidate it.** This trigger was invalidated by a file
*merely mentioning a string* — which no reader of *"exits 0 on a clean tree"* would predict. A sha tells you a
reading is old; it does not tell you **what kind of edit ages it**, and that is the part a reader needs in
order to know whether to re-measure.

**The trigger is not a pending decision — it is a re-litigation latch on a decision already made.** `966d202`
had already *declined* this exact wiring. So the trigger takes a settled no and converts it into a standing
invitation to redo it, **with the re-opening condition delegated to a tree-global measurement nobody
watches.** That reframing changes what the object is, not just how stale it is, and it is the strongest single
sentence produced about it. **Three parties have now declined** — `966d202`, the mediator as hook owner, and
this lane — **and none of the three is authorization to wire, which is the only direction that would need
one.**

## Cross-references

- `BEN-387` (lane E) — the guard's inversion, and the reason a green would not license the wiring anyway.
- `BEN-382` — a trailer that survives the rebase that invalidates it. Same defect in a durable artifact;
  same remedy (bind to a tree sha).
- `BEN-393` — a correction site inherits the trust of the index and none of its scrutiny. A trigger inherits
  the trust of the header it sits in.
- `BEN-228` — re-derive every coordinate; a narrated free-list is stale one filing later.
- `BEN-370` — the hook's own history of failing open with no diagnostic.
