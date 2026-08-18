# Match the moment, and never let a null on dependence name a mechanism

`BEN-430`. Mediator lane, from Assistant's formulation, filed against the mediator's own published
error rather than someone else's. Companion to `BEN-422` (lane C's refutation) and to
`FINDING-20260817-the-identity-claim-is-three-orders-too-strong.md`, whose amendments 1 and 2 are the
instance this generalizes.

## Rule 1 — MATCH THE MOMENT

**Before writing *"therefore"*, state which feature of the distribution the EVIDENCE constrains —
location, dispersion, shape, or dependence-on-X — and which feature the CONCLUSION is about. If they
differ, the bridge is an argument that must be made, not an assumption.**

*Instance.* `{(a), (b)}` — *the estimator is honestly unstable* and *the proxy is invalid* — are both
**dispersion** claims. The `OI-126` observation, the nominal sitting outside its own family, is a
**location** fact. A location fact excludes neither dispersion claim and selects neither. That is
exactly why the binary was never exhaustive, and the non-exhaustiveness was diagnosed twice before
anyone traced it to the type mismatch.

## Rule 2 — A NULL ON DEPENDENCE EXCLUDES A FAMILY; IT DOES NOT NAME A MEMBER

**"X does not depend on Y" rules out Y-driven mechanisms and nothing else. Before concluding
"therefore Z", enumerate the other Y-independent mechanisms and say why Z rather than them.**

**AND THE CLAUSE THAT MAKES THE RULE SAFE, without which it reproduces the defect it fixes
(lane C, `34ccd090`).** This finding first read *"if the list has one entry, say so; if it has two, you
have not finished"* — which invites the reading **enumerate until one survives, then conclude.** That
is the same over-confidence in a new dress, and it would have licensed the exact inference `BEN-422`
refuted: draw-independence plus a one-item list would have "authorized" it.

> **Two survivors does not mean the enumeration is unfinished — it means you cannot yet conclude.
> One survivor does not license concluding it, because the list is never provably complete.**
> **The survivor list BOUNDS WHAT YOU MAY CLAIM; it never certifies completeness.**

A one-entry list supports *"the only mechanism I can name"*. It never supports *"the mechanism."*

*Instance.* The measured residual is draw-independent: median `8.047e-04` at `data_factor == 1`
against `8.022e-04` at `>= 2`. That excludes **draw-driven** mechanisms. **Nonlinear coupling and a
constant archived-vs-rebuilt construction offset both survive it.** The first was named as though the
null had selected it; the second is the one `OI-126` actually needs, and `BEN-422` is the refutation.

**Rule 2 is the mechanical one and it is cheap: after any null, write the survivor list BEFORE the
conclusion.** Here that list has two entries and writing it would have stopped the inference at no
cost. Rule 1 requires judgment; Rule 2 requires a sentence.

## The structure the three instances share, which is the part worth keeping

Three rules caught their own authors on the next attempt in a single day: the find-the-authority rule,
the allocation-by-suspicion rule, and — twice over — this one. The dispersion-vs-location mismatch
recurred **inside the argument retiring a third route, in a document written by the lane that had just
filed the finding about it.** Assistant committed Rule 2's violation **on the very test it designed to
be careful**, having specified both the restriction and the reading to attach to it.

**In every case the rule was applied to OTHERS' claims and not to the author's own next inference.**

**Naming a failure mode raises your detection rate on INPUTS and leaves your GENERATION rate
unchanged.** So the durable form is not *"remember the rule"* — vigilance is not checkable, and a rule
that only fires when someone else is speaking is a reviewing habit rather than a reasoning one. It is:

> **Apply the rule to your own conclusion in the same turn you apply it to someone else's.**

which is checkable, because it names a turn.
