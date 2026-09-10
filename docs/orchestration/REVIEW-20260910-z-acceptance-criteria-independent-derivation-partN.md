# PART N — my own strengthening is WITHDRAWN: "exactly two places" is four

**Owner:** independent-assessment lane. **Base of measurement:** `6f24fb00`.
**Withdraws:** Part I §I.1's *"structurally unreachable"* paragraph and its Part M §M.6 row. Banners
are placed at both sites.

**CITABLE FOR:** §N.1's withdrawal and measurement. **NOT CITABLE FOR:** what the packet's wording
should become — §N.4.

---

## N.1 — WITHDRAWN, AND VERIFIED AGAINST MYSELF

**The claim.** Part I §I.1 said the `cause3_corr` registry entry is not merely *"inert"* but
**structurally unreachable**, because *"`assess` looks up a boundary only at `:247` … and
`LegSet.describe()` surfaces boundary status only at `:110`, also keyed on declared legs."* Rev. 3
adopted it verbatim at `:346-347`.

**It is false.** Covering grep of `z_validator.py` at `6f24fb00` — **four** sites:

| site | context | keyed on |
|---|---|---|
| `:83` | `boundary(self.boundary_key)   # fail fast on an unknown boundary name` | declared leg; result discarded |
| `:110` | `describe()` | declared leg |
| `:247` | `assess` | declared leg |
| **`:296`** | `assess_null`, signature `assess_null(r_null: float, boundary_key: str = "null_epsilon")` at `:286` | **a caller-supplied parameter with a default — not a declared leg** |

`assess_null(r_null, boundary_key="cause3_corr")` therefore reaches that boundary **with no leg
declared anywhere**. The exhaustiveness claim my argument rests on is wrong, so the conclusion is not
established by it. `:83` falsifies *"exactly two"* a second time and independently, though it does not
touch the conclusion, being leg-keyed.

**What my measurement does support.** Caller census for `assess_null`: five call sites —
`z_build.py:521` and `tests/test_z_validator.py:223,426,434,444` — and **zero** pass a non-default
`boundary_key`. So the path is **latent, not live**: unreachable through every path any current caller
takes, with one API path that could reach it and does not.

## N.2 — THE IRONY IS THE FINDING, AND IT IS THE REVIEWER'S

I replaced *"inert"* — a contingent word — with an absolute one, and **the truth is contingent.** The
`:296` path is closed by a caller census, which is a fact about today's callers, not about structure.
**"Inert" was contingent in precisely the way the truth is contingent.** My instinct that *"inert
reads as contingent, as though the entry happened not to matter"* was right about the connotation and
**wrong about the logic** — the connotation I objected to was the accurate one.

That diagnosis is the mathematical reviewer's and I am recording it as theirs, including the part that
is most against me: an absolute word was falsified by a covering search of the very file my argument
cited.

## N.3 — THIRD INSTANCE, AND I HELD THE DISPROOF IN MY OWN GREP OUTPUT

When I first measured this in Part I, I ran the covering grep and it printed **all four** sites — `:83`,
`:110`, `:247`, `:296`. I noted in passing that other lookups existed, and then wrote the claim as
*"exactly two places."* **The rows that falsified my claim were in my own output and I dropped them.**

Third instance of one failure in this campaign:

1. **`B8`** — `grep -rl` returned **eight** launchers; I wrote seven, because `SPEC` §3.7b said
   *"exactly seven."*
2. **`A14` versus `A30`** — the disqualifier was in my own document, seventeen items earlier.
3. **This one** — four sites in my own grep, written as two.

All three share the mechanism: a **correct measurement**, then a **claim over a filtered subset of
it**, with the filter unnoticed and pointed in the direction of the argument I was making. Per-cell
checking cannot see it, because every cell is right. The only instrument that catches it is diffing
the raw command's output against the claim's population — and in this case the raw output was already
on screen.

**And this one propagated.** I wrote it into another lane's artifact, where it was adopted verbatim,
so neither the designer nor I could catch it — which is exactly the argument I made in Part M §M.6
when I enumerated all five contribution sites instead of declaring one. The routing worked. That is
the strongest evidence I have that the boundary is worth its cost.

## N.4 — WHAT I AM NOT DOING

**I am not prescribing the packet's replacement wording.** Correcting my own defective claim is
required of me; choosing what §3.1 should say instead is the designer's, and the coordinator has
already recorded that neither reviewer proposes it. §N.1 records what my measurement supports and
stops there.

I also do not re-assert the conclusion by another route. Whether the entry is unreachable in a sense
that survives the `:296` path is exactly the question my argument failed to settle, and I am not the
lane to settle it now.

## N.5 — THE REST OF THE SPOT-CHECK, AND ONE CORRECTION OF THEIRS I ACCEPT

- **`:294` is upheld and upgraded.** *"A count cannot identify a population"* is confirmed, and
  `PROVENANCE-20260822` is now a **live worked instance** of it — right `N`, wrong arm. An abstract
  point with an example in the tree is worth more than the argument alone.
- **My hedge at `:294` is discharged in my favour**, with the coordinator's own over-reach removed
  before relay: content (`estimator_seed` present or absent) identifies which arms exist, but the
  product is a bare `TH2D`, so content discriminates the **inputs** and cannot bind the digested bytes
  to an arm. Content **narrows** A-6(b) without closing it. That was my point to them and it stands.
- **Their "inverts" is withdrawn and my "not exhaustive" stands.** The resolution is **(a)
  duplicates, (b) repairs** — leg (i) untouched because A-6(a)'s values still duplicate delivered
  work, and leg (ii) worse, because an uncited live record with a defective citation stays defective
  when nothing points at it. I accept the correction; it is against their own earlier relay to me.
- **RELAYED, NOT VERIFIED:** the reviewer's tightening that the cited invocation *"could not have
  completed"* because that arm refuses at the stated indices. I have not measured it, it is in the
  reviewer's slice, and my §M.3 does not depend on it.
- **My failed attack on the thirteen count is confirmed unfounded** by their independent re-run, as
  §M.1 already recorded.
