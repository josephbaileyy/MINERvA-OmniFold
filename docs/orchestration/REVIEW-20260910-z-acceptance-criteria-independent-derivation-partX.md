# PART X — cause-3 amendment Part A (`1b7db825`): BLOCK on where the licensing clause is placed

**Owner:** independent-assessment lane. **Subject:** `AMENDMENT-20260911-cause3-conditional-scope-and-kappa.md`
at `1b7db825`, sha256 `a37a970e1d3fc68c…`, 231 lines. **Yardstick:** Part W's `W1`–`W5`, committed at
`69114890` before this landed. **No grade assigned.** Consequential only; no sweep.

## VERDICT

> **BLOCK — two consequential issues, one of them decisive.**
>
> **(1) `W4` fails: A.5 item 2 places the licensing clause in `cause3_corr`'s contract entry, which I
> proved by execution does not reach the outcome.** The clause's *content* is good; its *location* is
> the one place the narrowing cannot travel from.
>
> **(2) The "ambiguity" frame is wrong on the dates: reading (b) was not expressible when `SPEC:3550`
> was written, so the amendment is asking to NARROW the declared quantity, not to disambiguate it.**
> That changes what Joseph is deciding.
>
> `W1`, `W2`, `W3`-in-content and `W5` are satisfied. `κ` is not mine.

---

## X.1 — DECISIVE: THE CLAUSE IS PLACED WHERE IT CANNOT TRAVEL

A.4 writes a five-part licensing clause and A.5 item 2 says where it goes: *"**Add A.4's licensing
clause to the contract, in `cause3_corr`'s existing template**."*

**Part I §I.1 established by execution that `cause3_corr`'s entry is inert to the outcome**, with both
positive controls passing: deleting it from `Z_BOUNDARIES` leaves `describe()` **byte-identical**,
because `assess` reaches a boundary only at `z_validator.py:247` via `leg.boundary_key`, and
`LegSet.describe()` surfaces `boundary_status` only at `:107-111`, **both keyed on declared legs.**

`Boundary.describe()` **does** carry `reason` (`z_contract.py:206`), so a clause on a boundary that a
leg names *would* travel. **`cause3_corr` is named by no leg** — and that is not incidental, it is the
entry's own stated premise: *"no correlation-sensitive leg is adopted, and none has a boundary."*

**So the amendment proposes to record the licensing consequence of the deferral inside the very entry
whose unreachability is what the deferral is about.** The clause would be true, committed, and
invisible to every grade.

**And the mechanism that would make it travel is not mentioned anywhere in the amendment.** Grepping
`1b7db825` for `_DIAGONAL_ONLY_SCOPE`, `z_validator` and `scope_statement`: **zero hits.**
`z_validator.py:166-167` states the rule the amendment needed:

> *"The narrowing that must travel WITH the grade, not sit in a specification the grader may not
> open"*

— and `_DIAGONAL_ONLY_SCOPE` is the non-suppressible emitter, already firing on every outcome with no
correlation-sensitive leg. **The amendment's clause belongs there, or in whatever emits with the
grade. It does not belong in a registry entry no leg reaches.**

**I am not choosing the destination.** `_DIAGONAL_ONLY_SCOPE`'s text, a new emitted scope statement, or
a boundary an adopted leg names are all available and the choice is the designer's. What I am stating
is that **the proposed location is measurably not one of them.**

## X.2 — THE FRAME: THIS IS A NARROWING, NOT A DISAMBIGUATION, AND THE DATES DECIDE IT

The amendment's position is that cause 3 does not distinguish **(a) TOTAL** from **(b) ATTRIBUTABLE**,
that the ambiguity is the finding, and that *"the ambiguity was invisible until the decoupling, because
with one switch (a) and (b) were not distinguishable configurations, so no wording had to choose."*

**Measured, and the claim needs correcting in a way that matters:**

| | |
|---|---|
| `MNV_EST_SEED_OFFSET` first commit | **2026-08-18** |
| `SPEC-20260906` first appears | **2026-09-06** — nineteen days later |
| the launcher at `6f24fb00` | `:417` `if mr_declared` → own blocks; `:424` `else` → archive reuse. **Binary.** |

**So (a) and (b) were not two indistinguishable configurations — (b) did not exist.** Only (a) was
producible, and `SPEC:3550`'s wording was written **after** the binary machinery existed. Its author
was writing against a world in which the *only* expressible variation was the one that regenerates the
blocks.

**Therefore `SPEC:3550`'s natural referent is (a) TOTAL, and the decoupling CREATES (b) rather than
revealing a pre-existing ambiguity.** In Part W's frame this is response **(b) narrow the subject** —
which I pre-registered as *"available, but it is a contract change and therefore Joseph's, and it must
be argued scientifically rather than by convenience."*

**Why the difference is consequential rather than semantic:** *"which did you mean?"* invites a cheap
answer and puts the burden on Joseph's memory. *"May I narrow the declared quantity from the assembled
`C_Z` to the estimator-attributable part, and here is the scientific argument"* puts the burden on the
proposer, where a contract change belongs. **The amendment already contains the argument** — A.6
prices both branches and recommends (b) on the ground that it is the only branch where A-7 can both
bind and be satisfiable. **It is asking the right question in the wrong grammar.**

## X.3 — SATISFIED, AND ONE OF THEM WELL

- **`W1`** — element 5 engages the objection directly, quotes it rather than paraphrasing, and states
  its own position. Satisfied.
- **`W2`** — it does **not** claim the excluded summands are invariant or their variation negligible,
  which is what Part W §W.2 closed by measurement. A.4(i) says the opposite in terms: *"the components
  held fixed are exactly the ones not tested."* **Satisfied, and honestly.**
- **`W3` in content** — A.3 states what passing licenses and A.4 states what it does not, and A.4(ii)
  adds something I had not required and which is correct: the finite-ensemble contribution *"is
  common-mode under fixed digests and cancels in `C_k − C_0` by construction."* **The content reaches
  the objection. Only §X.1's placement defeats it.**
- **`W5`** — A.5 records that cause 3 is not made passable, that all three boundaries remain withheld,
  and that (a) is to be recorded **explicitly undischarged** rather than omitted. No fourth token.
  Satisfied. *(Verified independently: `cause3_agg` and `cause3_med` are `withheld` at `6f24fb00` and
  **are** named by the adopted legs, so they are what force non-passing — `cause3_corr`, named by no
  leg, is not. The conclusion holds; the stated reason is looser than the mechanism.)*

## X.4 — NOT ASSESSED

- **Part B, `κ`** — the reviewer's, whole, per Part W §W.5.
- **`ec5f0b99`** and **`6d959ab3`** — frozen, and the rate-closure block is the reviewer's.
- **`S2`** — still held; the maps are not here.
- **Still open:** `A-6(a)`, `A-6(b)`, the excluded producing execution, the three-or-four block
  population. **Part V's non-member return `BLOCK` is discharged** at `f0537dc3`, per the coordinator's
  verification; I have not re-verified it and record it as relayed.
