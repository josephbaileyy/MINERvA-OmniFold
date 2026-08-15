# FINDING 2026-08-14 — a sha256 written into prose is not a binding, and two guards passed over a wrong one

**`BEN-227`.** Lane A, found while correcting a receipt on the mediator's dispatch. **Scope ruled by the
mediator after lane A declined to rule it**, on the ground that whether the checker should learn to resolve
prose digests is a scope question and not the finding's to settle. **The remedy below is prescriptive; the
tooling question is deliberately left open.**

## What happened

`state/p3f-pet-gate4-nominal-promotion-56563761.json` recorded, in a prose field:

> *"…on `/pscratch` is the PRE-supersede file, sha256 `81849396611856a1…`, versus the git record
> `fc4fcbe863963b22…`"*

**The git-side value was already wrong.** Measured 2026-08-14: the file at `c29e3522` hashes to
`67c487cd01907597742ff4c6fc8c572af6ab62837aa4e281e395d6ed1a44b4bf`. The receipt it describes had been edited
after the note was written and the note did not follow.

**It was found only because something else made it move.** Lane A was editing that same receipt for an
unrelated reason (`next_dependency` staleness), asked who records its digest, and checked. **Nothing was
looking for it, and nothing would have.**

## THE PART THAT MAKES IT A FINDING: two independent guards both passed

| guard | result while the digest was wrong |
|---|---|
| `verify_hash_bindings.py` | **`ALL BINDINGS INTACT`**, 175 bindings resolved |
| the receipt-binding floor (`RECEIPT_BINDING_FLOOR = 140`) | **160 receipt bindings, floor cleared** |

Neither is broken and neither was misconfigured. **A binding is a `files`/`sha256` pair the verifier can
resolve. A digest written into a prose sentence has no pair** — so it is not a binding, it is a *character
string that looks like one*, and it is invisible to the one check built for exactly this failure. The floor
cannot see it either, because the floor counts resolvable bindings and this was never counted.

**This is the green-count trap one level down.** `CONVENTION-verifying-a-check-is-deployed.md`'s
generalisation is *"a green count is a statement about what ran, not about what was checked."* Here both
greens were **accurate**: 175 bindings really were intact. The defect was in a quantity that was never a
binding, so the check was not even wrong — **it was silent about a thing shaped like its subject.**

## THE REMEDY, and it is not "teach the checker to parse prose"

**The mediator ruled against building prose-digest resolution**, and the reason is worth keeping: scanning
free text for 64-hex strings **false-positives on every digest legitimately quoted as history**, and this
repo quotes retired digests deliberately — `INDEX-retracted-and-superseded-values.md` exists to do it. A
checker that flags those is a checker that gets switched off.

> **THE RULE: do not write a bare digest into prose. Write the derivation, and quote every value WITH its
> ref.**

Applied to the offending field, which is how it now reads:

- **The point value was removed, not refreshed.** Refreshing restarts the same clock — the digest of a
  mutable, concurrently-edited document is stale at its next edit, and this note had already been wrong once
  for precisely that reason.
- **Replaced with the derivation:**
  `git show <ref>:docs/orchestration/state/annealed-nominal-complete-56563761.json | shasum -a 256`.
- **Both observed values recorded WITH their refs** — `67c487cd0190…` at `c29e3522`, `435be86816b1…` after
  the same-day supersession — because a digest plus a ref is a *fact*, and a digest alone is a *claim with a
  hidden timestamp*.
- **The cluster-side value was left exactly as recorded and explicitly marked not re-measured**, since
  nothing in that dispatch went near the cluster.

**Why this is the better buy than detection:** it makes the defect *impossible* rather than *findable*. A
derivation cannot go stale, and a value carrying its ref cannot be silently falsified by a later edit — it
becomes a historical measurement, which is what it always was. This is the same move as
`CONVENTION-receipt-ingredients.md`: publish the ingredients so the numbers can contradict each other.

**The generalisation, which is broader than digests:** *a fact about a concurrently-written repository is a
measurement with a timestamp, and publishing it without one is the failure* — already written in
`CONVENTION-verifying-a-check-is-deployed.md`. **A bare sha256 in prose is that failure in its purest form**,
because it looks maximally precise while carrying no timestamp at all.

## LEFT OPEN, deliberately

**Whether `verify_hash_bindings.py` should ever resolve prose digests is NOT decided here.** The mediator
declined to build it tonight and did not rule it out. If someone wants it later, the tractable version is
almost certainly **not** "scan all prose": it is to require that any digest in a receipt live in a structured
field with its ref beside it, and then verify *those* — which is the remedy above, enforced rather than
merely prescribed. **This row is where that work should start.**

## Related

`CONVENTION-verifying-a-check-is-deployed.md` (the green-count generalisation and the timestamped-measurement
premise), `CONVENTION-receipt-ingredients.md` (`BEN-077` — ship the ingredients), `BEN-219` (a citation correct
at write time), `BEN-225` / `BEN-228` (the two ways a correct citation becomes false without anyone touching
it), `INDEX-retracted-and-superseded-values.md` (why blanket prose scanning would false-positive).
