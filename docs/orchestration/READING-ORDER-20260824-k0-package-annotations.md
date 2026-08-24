# READING ORDER — every live annotation in the k=0 execution-integrity package

**CITABLE FOR:** finding, in one pass, every in-place annotation in the k=0 package that changes what
a clause requires or what a number means — and knowing which ones do **not**.

**NOT CITABLE FOR:** any requirement, verdict, measurement or authorization. **This file is a router,
not evidence.** Every row points at the annotation that governs; the annotation's own words bind, not
this summary of them. A grader who cites this file instead of the artifact has failed F-18, which
requires the artifact cited per F-number.

## Why this exists

The k=0 package was corrected **by annotating in place rather than by rewriting.** That was the right
call each time — a retraction a reader cannot check against the words it retracts is not falsifiable,
and several of these corrections are themselves the evidence for a finding about how the campaign
errs. **But the package's correctness now depends on a reader finding every one of them**, and Gate 2
is graded against these documents. Nine annotations across five files, filed over three days by at
least four lanes, is past the point where "read carefully" is a mechanism.

**This file does not add a tenth thing to find.** It is linked from `CATALOG.md` (the router) and from
§7 of the review contract, which are the two places a grader necessarily enters the package.

> **THE HAZARD THAT MAKES A GREP USELESS HERE, and it is not new.** By this package's convention, an
> annotation **quotes the sentence it withdraws**, and in four cases below the withdrawn sentence is
> printed *after* its own retraction, verbatim and unmarked at the point of use. **So a substring
> search cannot distinguish "still asserted" from "quoted while being withdrawn", and it fails toward
> the accusation.** A hit is not evidence the claim is live; a miss is not evidence it is dead. Read
> the **role** of the occurrence. This is the same rule already stated at
> `INDEX-retracted-and-superseded-values.md`, and it was measured there: a lane verified a correction
> with `'already failing' not in cell`, got FALSE, and would have reported a landed correction as
> never landed. **Do not audit this package by grep in either direction.**

## The two classes, because only one of them can change a verdict

| class | what it means | how many |
|---|---|---|
| **BINDING** | changes what a clause requires, or what a number counts. **Read before grading the clause named.** | 4 |
| **HISTORICAL** | records that a sentence was once wrong, or that a state has moved. The current disposition is already correct without it. **Safe to skip while grading; do not delete — several are the evidence for a finding.** | 5 |

## The reading order

Read top to bottom. Ordered by what a Gate-grader hits first, not by date.

| # | class | document / anchor | believe THIS | affects |
|---|---|---|---|---|
| 1 | **BINDING** | `REVIEW-CONTRACT-…k0-execution-integrity.md` §7.0.17 (new, 2026-08-24) | The O-1 paired arm's `exit 0` / `outcome=ok` requirement in §7.0.11's three-arm table is **struck**. Grade the paired arm on **P.1–P.5**. The real arm measures exit **1**, `outcome=child-systemexit`, `checked=9`, marker **present**. P.5 carries an explicitly **STRIKEABLE** clause. | F-9, F-12 (both Gate 1) |
| 2 | **BINDING** | same file, §7.0.11 — the **three-arm** table, `O-1 paired` row, and the prose under *"why the paired arm is permitted"* | Both are annotated in place and route to §7.0.17. The row's `0` and `outcome=ok` are struck **in the normative table**. | F-9, F-12 |
| 3 | **BINDING** | same file, §7.0.11 — the **fixture** table (`e39ab74f`, three arms) | **Its numbers are left exactly as measured and must not be rewritten.** Its paired row reads `0`/`ok`/`checked=7` because **the fixture had no ROOT child to fail**. It is evidence about the fixture only and **does not transfer to the real arm**. | F-9, F-12 |
| 4 | **BINDING** | `PACKET-…round10-oi136-runtime-violation-repair.md` — the census headline, corrected 2026-08-24 | The census on the deployed candidate is **52**, not 53. **53 is the count at `aa67c426^`, pre-repair.** One digit was doing duty for two populations; the wrong part was the sentence naming the population. `KNOWN_UNREPAIRED` = 52, census set equal to it exactly. | any clause quoting the census; F-8 |
| 5 | HISTORICAL | `RECEIPT-20260824-k0-…-filings.md` §1.7, scope corrected by the round-12 lane | *"one child, covered; zero uncovered"* is true **of the entrypoint set**, which is P-5's stated population — not of the whole import closure. A closure-wide search finds `seed_offset_policy.py:420`, whose child is **`git`, not an interpreter**, so it cannot resolve a Python import. **Disposition unchanged.** | F-8(a) |
| 6 | HISTORICAL | same receipt, **FINDING 5** | **CLOSED.** The finding says the branch rubric *"is 575 lines (`cf53f587`)"*; it was already 1160 lines / sha256 `e0fb342b…` at the very commit that filed it, synced by an independent lane at `b2075558`. **The original text is retained verbatim BELOW its own retraction** — read the banner, not the body. | nothing; it is a finding about filing discipline |
| 7 | HISTORICAL | `DECLARATION-20260823-k0-candidate-aa67c426.md` §1 | *"The deployment is at the declared sha"* was false for ~21 h — the declaration's own docs-only commit `9db42a6d` was deployed on top of the candidate, and round 10 failed `F-1(a)` on exactly that. **Restored 2026-08-24T11:36:43Z**; the sentence is **true again**. **The false sentence is printed after its retraction.** Do not read §1 without §6. | F-1(a) — verify by running the falsifier, not by reading either sentence |
| 8 | HISTORICAL | same declaration, **§6.3** | *"`refs/heads/build-k0-execution-integrity` is left unmoved at `9db42a6d`, still equal to `origin`"* is **now false**: the builder deleted that branch and the remote in the §6.9 hardening. **The false sentence is printed after its retraction, verbatim and unmarked.** This is the instance that motivated this file. | nothing directly; **but see the branch-divergence note below** |
| 9 | HISTORICAL | `CATALOG.md` — the ⚠ ROUND 11 heading | Round 11 stood at **16 PASS / 2 FAIL**, with F-8(a)/F-17(a) then unfiled. Round 12 has since run. **The router's own heading is a dated snapshot, not current state.** | orientation only |

## Two live conditions a grader must not learn by accident

**(a) The contract now exists in TWO NON-IDENTICAL copies.** `b2075558` had synced
`build-k0-execution-integrity`'s copy to `main`'s **byte for byte** (both sha256 `e0fb342b…`, 1160
lines). §7.0.17 was added to **`main`'s copy only**, so the two have **diverged again** and the build
branch copy is now the stale one. **Grade against a named path plus digest plus sha, never against
"main" as a bare word.** Re-syncing the branch copy is a non-builder task and is **not** done here;
it is flagged, deliberately, because FINDING 5 above is precisely what happens when that sync is
assumed rather than measured. Also note B-4 itself lives only on the build branch: `main` at
`115c73bb` has neither the containment check nor `write_inventory`.

**(b) A line number that is right in one tree and wrong in another.** The `[remedyA] running the
PINNED writer as a subprocess:` marker is `mii_adopt_unified_5d_stamped.py:711` in the canonical
checkout **and** on `main`, and `:787` on `build-k0-execution-integrity` (child spawn `:788`).
**Neither is wrong; they are different trees.** A grader who greps the build branch for `:711` lands
on an unrelated `finally:` block.

**(c) A THIRD condition, found while building this file, and it is not an annotation at all.**
`CATALOG.md`'s Gate-1-round-9 section enumerates Gate 2's debt as
*"`F-1(b)`, `F-2(b)`, `F-4(b)`–`F-8(b)`, `F-17(b)`, `F-18(b)`"* — **nine clauses. `F-3(b)` is
missing**, and the enumeration jumps `F-2(b)` straight to `F-4(b)`. §7.0.5 makes **F-3 SPLIT**, with
the post-rehearsal half *"grep the job stdout → zero `--allow`; publish the command."* Re-derived from
the §7.0.5 table by parsing its class column: **10 SPLIT** (F-1…F-8, F-17, F-18) and **8 pure
PRE-SUBMISSION** (F-9…F-16), which matches §7.0.5's own stated arithmetic exactly. **A Gate-2 lane
that inherits the router's list grades nine clauses and misses one — and because §F gives no partial
credit, the miss is silent rather than loud.** The router is annotated; **derive the clause list from
§7.0.5's POST-REHEARSAL column, never from a summary of it.** Filed here rather than repaired in
silence because a partial enumeration repaired in full erases that it was ever partial.

**(e) §7.0.18 IS PUBLISHED, INERT, AND THE ONE ANNOTATION WHOSE HAZARD IS THAT A READER TREATS ITS
EXISTENCE AS ITS ADOPTION.** It transcribes Joseph's `F-6(b)` ruling and is held against confirmation:
no `DECISION-*` record contains the ruling, so **Gate 2 remains ten clauses and F-6(b) remains one of
them.** Its own header says so in bold. **Publication is not adoption** — it reached `origin/main` at
`0a61972f` while the confirmation question was still open with Joseph, which is a provenance fact
about the commit and not a change in the clause's status. Classify it **HISTORICAL until the decision
record lands, then BINDING.** The distinction that matters for a grader: the bytes narrow nothing, and
a reader who cites §7.0.18 as authority for nine clauses is citing a document that says ten.

**(d) §7.0.17 HAS ITSELF BEEN CORRECTED TWICE, on 2026-08-24, by the third grading lane — so read it
to its end.** Both corrections are inside the subsection and both are BINDING. **(i)** Its mechanism
sentence originally read *"`write_inventory` is called once, at `:552`"*; the callee, the count and the
line were each wrong (`write_inventory` is called at `:415` inside `_safe_inventory`, which has **six**
call sites; the executing one on this arm is the `finally:` at `:550-552`). The verdict is unchanged.
**(ii) P.5's two original clauses are STRUCK** — `≠ 3` was redundant given P.4 and a false-fail risk,
and the attributability clause cited **O-4** (a no-pipe rule) for an ordering requirement whose real
authority is **O-3**, which forbids exactly the stdout-vs-stderr comparison the clause needed.
**P.4 is the test; the exit status is recorded, not graded.** A grader working from the amendment's
first three paragraphs alone will grade a struck clause.

## Maintenance rule, so this file does not become the next hazard

**Any new in-place annotation in the k=0 package gets a row here in the same commit as the
annotation.** A row is one line: class, anchor, what to believe, what it affects. **If the annotation
changes what a clause requires, it is BINDING and the row says which F-number.** This file is a view
over the annotations and is never the authority for one; when it disagrees with the artifact it
points at, **the artifact wins and this file is the bug.**
