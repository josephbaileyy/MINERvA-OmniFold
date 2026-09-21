# PART Z — cause-3 Part A at `6f587e59`: READY, and a shape my own Part V requirement created

**Owner:** independent-assessment lane. **Subject:** `6f587e59`. **Supersedes:** Part Y's assessment of
`f00e4bee`. **No grade assigned.** Consequential only.

## VERDICT ON MY SLICE

> **READY FOR JOSEPH'S DECISION.** Part Y's `BLOCK` is closed, verified by execution on all five cases
> including a positive control. Two non-blocking notes below, one of which is a correction to a
> relayed claim and one of which is about a mistake in a requirement of mine.

---

## Z.1 — THE BLOCK IS CLOSED, AND PINNED WHERE I NAMED THE DEFECT

Part Y's diagnosis was *"copied at the function level and broken at the signature level."* Measured at
`6f587e59` by `inspect.signature`:

| case | result |
|---|---|
| `build_path` default | **`inspect._empty` — REQUIRED**, same as `kappa` |
| omit `build_path` | `TypeError: missing 1 required keyword-only argument` |
| `build_path=None` | `ZContractError: build_path is REQUIRED and must be a BuildPath, got NoneType` |
| **non-member** path | `ZContractError: build_path declares no member offset, but A-7 grades ACROSS …` |
| **member + `scale_kind='lambda_max'`** *(positive control)* | **`GRADED`, `scope_statement` present** |

**Both reachabilities I found are closed, including the second**, and the designer's ground for it is
right: A-7 grades *across* offsets, so no configuration legitimately yields a graded outcome with no
scope statement. **The property is pinned by signature inspection rather than behaviour**, which is
the level at which I named the defect.

**And the uniformity holds across branches**, re-measured rather than assumed:

    GRADED                 keys = ['detail','routed_to','s_proj','scope_statement','state']
    DEGENERATE_FUNCTIONAL  keys = ['detail','routed_to','s_proj','scope_statement','state']
    identical: True        scope present on the refusal: True

Suites, control first: **136** control / **90** passed, no skips / **56 passed + 1 skipped**.

## Z.2 — A SHAPE WORTH KEEPING, AND MY PART V REQUIREMENT IS WHAT CREATED IT

The designer found that one of its own tests had **encoded** the defect:
`test_without_a_build_path_the_key_is_still_present` asserted that omitting `build_path` yields a
**present key with a `None` value** — which is the suppressibility bug stated as a passing assertion.
Grep for the old name at `6f587e59`: **0**.

**The generalisation is theirs and it is good:** *a test written for property A can lock in a defect in
property B, and the more rigorously it enforces A the more firmly it holds B.* It is adjacent to
fixture-derived-from-the-rule but distinct — here the fixture was derived from a **different, correct**
rule.

**And the correct rule was mine.** Part V's `BLOCK` required *"one identical key set across all
branches."* That test is a faithful implementation of my requirement. **The failure mode is specific
and I had not seen it: a uniformity requirement can be satisfied by NORMALISING THE DEFECTIVE CASE
INTO THE UNIFORM SHAPE rather than by eliminating it.** Returning `scope_statement=None` for a call
with no build path makes the key set uniform — and preserves the suppressibility that made the call
possible.

**So the requirement was under-specified, not the implementation wrong.** *"Uniform keys"* needed to be
*"uniform keys over the configurations that should exist"*, and the second clause is the one that does
the work. I record it against my own requirement because the next reviewer to demand uniformity should
demand the second clause with it.

## Z.3 — ONE CORRECTION TO A RELAYED CLAIM, NOT BLOCKING AND NOT MY RESIDUAL

Relayed: *"`scale` and `scale_kind` are carried in **every** return, so a receipt records what was
used."*

**Measured — the substance holds and the position does not.** They are **not** top-level keys of the
return; the full graded key set is the five above. They are nested at
`detail['degeneracy']['c_scale']` and `detail['degeneracy']['scale_kind']`.

**A receipt can therefore record what was used, but only by reaching into `detail`.** That matters
because *"carried in every return"* invites a top-level read, and a top-level `.get('scale_kind')`
returns `None` — indistinguishable from *"no scale was declared."*

**And one thing I could not determine:** whether the **support-refusal** branch (`:75-76`, which
returns `detail=sup` **before** the degeneracy classifier runs) carries `scale_kind` at all. My
attempts either graded or raised through arm 2's `require`, so I did not reach that return. **I do not
know, and I am not asserting either way.** Residual 1 is the reviewer's; I flag this rather than block
on it.

**A note on my own method here:** my first read used `r.get('scale')`, got `None`, and that was a
**missing key**, not a present-`None`. I checked the full key set before asserting. On a different day
that is a published false finding.

## Z.4 — NOT ASSESSED

- **Part B / `κ`** — the reviewer's, whole; its value is withdrawn with `B.1`, `B.3`'s floor and `B.4`
  standing.
- **The power of the 90 tests**, including the scope tests' power arm — the reviewer's, and explicitly
  left by me.
- **Residual 1's substance** — the `lambda_max` gate is a **bound check**, not a verification, as its
  own label says; whether the bound is the right one is the reviewer's.
- **`ec5f0b99`**, **`6d959ab3`**, **`S2`** — frozen, held, or not mine.
- **Still open:** `A-6(a)`, `A-6(b)`, the excluded producing execution, the three-or-four block
  population — none touched by this pin.
