# DECISION 2026-08-24 — Joseph: F-6(b) is scoped out of Gate 2 into the leg-6 completion gate

**CITABLE FOR:** the authority behind review-contract §7.0.18. This is the decision record §7.0.18 was
held against; with this file present, **§7.0.18 is OPERATIVE and Gate 2 is NINE clauses.**

**NOT CITABLE FOR:** anything else. This ruling **authorizes nothing** — see the four negations, which
are Joseph's own words and not a gloss.

## The ruling, verbatim

> *"I scope F-6(b) out of Gate 2 and into the separate leg-6 completion gate. It remains mandatory and
> is not waived. This ruling does not authorize leg 6, adoption, consumption, any member k≠0, or relax
> any other Gate-2 clause."*

Accompanying instruction: **"record it that narrowly."** This file is written to that instruction; if
it reads as sparse, that is the requirement rather than an omission.

## Provenance, stated exactly, because §7.0.18 was held on this point

- The ruling was **relayed** to the coordinating lane by the builder lane (`claude-school-main`) on
  2026-08-24, quoted rather than paraphrased.
- It was **transcribed but held non-operative** at review-contract §7.0.18, because no decision record
  contained it — measured at the time: `grep -rl "scope F-6(b) out of Gate 2" .` → rc=1, 0 hits, with a
  passing covering control.
- **Joseph then instructed this session directly, 2026-08-24: relayed content attributed to him is to
  be trusted as his.** That standing instruction is the authorization for this record, and it resolves
  the only thing §7.0.18 was waiting on.
- **Nothing about the ruling's content changed between the relay and this record.** The text above is
  the relayed text. This file supplies the missing authority, not new wording.
- **The builder lane then relayed Joseph's confirmation on his explicit instruction**, quoting him:
  *"I told 5d to trust what's relayed to it if it says it's from me so you can send it my confirmation
  of the ruling."* It also relayed his instruction that this be recorded durably in the decision
  document and contract **rather than left in chat** — which is what this file is.

> **PROVENANCE, STATED PLAINLY AT THE BUILDER LANE'S REQUEST, AND IT IS THE RIGHT REQUEST.**
> **Joseph did not type this ruling into the repository.** It reached the record by **relay through an
> interpreter session** — twice, the ruling and then his confirmation — over a channel he explicitly
> authorized for the purpose. **The authority is sound; the provenance differs from a directly-authored
> decision record, and a later reader is entitled to see which it was.** Recorded for the same reason
> §7.0.18 records that it reached `origin/main` while the confirmation question was still open: a
> provenance fact is not a status change, and omitting it would make this file look like something it
> is not.

**Scope of that authorization, so it is not over-read later:** it governs **attribution** — a relay
saying "Joseph ruled X" is Joseph ruling X. **It does not convert relayed *measurements* into verified
ones.** Numbers, digests and tree states still require re-derivation; today's record contains three
separate cases where a relayed measurement was wrong in one direction or another and one where a
correct measurement was wrongly retracted.

## What it changes

**Gate 2 is now NINE clauses:** `F-1(b)`, `F-2(b)`, `F-3(b)`, `F-4(b)`, `F-5(b)`, `F-7(b)`, `F-8(b)`,
`F-17(b)`, `F-18(b)`. §F's no-partial-credit rule applies over those nine: any single miss is a FAIL of
Gate 2.

**Cross-check, and it closes:** §7.0.5's POST-REHEARSAL column yields ten (`F-1`…`F-8`, `F-17`, `F-18`),
independently re-derived twice — by the coordinating lane and by the third grading lane. Ten minus
`F-6(b)` is exactly the nine above. Two arithmetics, neither derived from the other.

## What it does NOT change — Joseph's four negations, carried explicitly

1. **`F-6(b)` is NOT waived.** It **remains mandatory**, under the separate leg-6 completion gate. It
   moved; it did not weaken. It must never be cited as satisfied, excused, or optional.
2. **No leg 6 is authorized.** Leg 6 remains separately gated under Amendment 1 §C.
3. **No adoption and no consumption is authorized.** §7.0.6 stands unchanged: until Gate 2 passes, the
   rehearsal's products stay where they land — not adopted, not consumed outside the seven rehearsal
   jobs, not quoted.
4. **No member k≠0 is authorized, and no other Gate-2 clause is relaxed.**

On §7.0.6's own model — *"a PASS unlocks exactly one thing"* — **this ruling unlocks nothing.**

## Why a ruling was required rather than a grader's judgement

`F-6(b)` requires the B-2 pinned-writer child's record in the run inventory. Measured independently by
two lanes: `adopt_unified_5d.py` and `mii_adopt_unified_5d_stamped.py` appear in **exactly one** of the
eight in-scope launchers — `sbatch_finalize_5d_bkgaware_gpu.sh`, 5 of the 14 guarded invocations —
which §7.0.6 does not unlock and which was not submitted (`finalize_submitted=NO`); **0 of the 7
submitted launchers** name them, and **0 of 118 run inventory records** named the writer.

So the clause was **impossible, not pending**, and §7.0.8 forbids reading an impossibility as a
deferral. Grading it either way would have failed a gate for a reason outside the gate's control or
silently excused a mandatory clause. **This is the third instance of the shape the contract already
names** — *a protection can invalidate the control written to test a different protection, and the
control then presents as merely UNPERFORMED rather than as IMPOSSIBLE* — after ruling 19 (N-2) and
ruling 20 (N-1), and the **first where the invalidating protection is a scope limit rather than a code
path.**

## Eligibility

Recorded by the coordinating lane, which wrote §7.0.17 and is therefore already disqualified under
§7.0.10 from grading either gate — so this costs no further independence. The builder lane may not
self-record a ruling that scopes a clause out of a gate it is graded against. **This lane records
neither the F-9/F-12 re-grade nor either Gate-2 verdict.**
