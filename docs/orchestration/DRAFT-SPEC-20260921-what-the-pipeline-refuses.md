# DRAFT SPEC 2026-09-21 — what the pipeline refuses, compressed from 1,061 tests into five rules

**CITABLE FOR:** the five rules below as a *derived description* of the existing suite, the
measurements behind them, and the **five-test** gap the derivation exposed and repaired.
**NOT CITABLE FOR:** any guarantee about behaviour, any authorization, and any claim that a rule is
*enforced*. **Nothing is deleted, nothing is modified, and no test was touched to produce this.**

Brought for review, per Joseph's framing: *"test consolidation is a form of compression and
compression usually reveals strong insights and ease of understanding, which is important with the
note and paper."* The product of the compression is **this document**, not a smaller suite. The
suite is unchanged.

---

## 0. ⚠ A NUMBER I PUBLISHED YESTERDAY WAS WRONG, AND IT WAS WRONG IN MY FAVOUR

`PROPOSAL-20260921` §2 says the refusal family is **538** tests. **It is 1,061.** The 538 came from
`def test_[a-z0-9_]*(REFUS|refus|…)` — the character class before the keyword is **lowercase only**,
so every name with an uppercase word before the keyword was invisible:
`test_a_WRONG_declared_digest_refuses_before_any_object_is_read` did not match. Corrected at source
in that proposal; recorded here because an undercount made the target look smaller and more
tractable than it is.

## 1. Method, so the compression can be checked rather than believed

One pass over `nd-unfolding/tests/test_*.py` (122 files, 3,749 `def test_` definitions). A test is
in the family if its **name** matches `REFUS|refus|reject|denied|blocked|FAIL|fails_closed` case
-insensitively: **1,061**.

⚠ **The body-level figures below use a narrower extractor** — a 4-space-indented
`def test_…(self…)` — which matched **958** of the 1,061. The 103 it missed are decorated or
differently indented. **Where a denominator is a body count it is 958, not 1,061**, and the two are
not interchangeable.

| measurement | count |
|---|---|
| exit-code assertions (`returncode`/`exit_code`/`rc` vs an integer) | **399** |
| …distribution | `0`×269, `3`×45, `1`×40, `2`×13, then 7/9/4/5 |
| `assertIn` (a message pinned) | 2,113 |
| bare `assertRaises` / `assertRaisesRegex` | 776 / 68 |
| *positive control* / *negative control* mentions | 70 / 34 |
| names asserting an **order** (`…before…`) | 59 |
| names of the form `…rather_than_X` | 81 |
| *fail(s) closed* | 170 |

## 2. The five rules

These are not proposals. Each is a description of what the suite already asserts, with the count of
instances and the incident it encodes.

### R1 — ABSENCE REFUSES. A missing operand is never a default.

A missing, absent, empty or undeclared operand must produce a **refusal** — never a skip, a
warning, a default, a derived substitute, or a guess.

Derived from the 81 `rather_than_X` names, where the measured `X` values are exactly the wrong
behaviours: *skipping / skipped* (6), *guessing* (3), *passing / passed* (4), *defaulting* (3),
*deriving*, *coercing* (2), *copying* (2), *reporting*, *warning*, *silently* (2).

> The suite states this in its own voice: `test_a_missing_declared_rate_is_refused_rather_than_derived`,
> `test_a_missing_policy_key_FAILS_rather_than_being_skipped`,
> `test_the_guard_RAISES_rather_than_warning`.

### R2 — THE GUARD RUNS BEFORE THE THING IT GUARDS.

A check must execute before the side effect it exists to prevent, and the ordering is itself
asserted. **59 tests assert an order in their name.**

**The incident:** `import ROOT` placed above `argparse` killed every guard in a file before one
could fire. `OPERATIVE-SHEET-scalar5d.md` §4d records **seven** instances of this one shape and
states the general form: *a step whose verification is not on the path the failure takes cannot
catch that failure.*

### R3 — A REFUSAL IS PINNED TO ITS EXACT EXIT CODE **AND** ITS OWN MESSAGE.

Exit codes carry fixed meanings — `0` accept, `1` refused, `2` cannot-check, `3` refused-at-load —
and a refusal identified by number alone does not distinguish *refused for the right reason* from
*crashed with the same number*.

**The incident:** a guard-set control tested `expect REFUSE and rc == 0`, so **three segfaults at
`rc=139` were reported as three refusals**. Three guards that never executed read as three that
fired.

⚠ **I FIRST WROTE THAT THIS IS THE RULE THE SUITE FOLLOWS LEAST. THE MEASUREMENT REFUTES IT.**
Of the 209 refusal tests that read an exit code, **181 discriminate the reason** — by message,
by a structured receipt field, or by a code unique to their condition. The genuine residue was
**5**, and it is repaired. §3 keeps the whole chain because the two wrong numbers on the way
are the instructive part.

### R4 — EVERY GUARD HAS AN ACCEPT ARM THAT COULD HAVE FAILED.

A refusal arm alone is not evidence: a check that can only refuse is indistinguishable from one
that always refuses. **70 positive-control mentions, and 269 of the 399 exit-code assertions are
`0`** — the accept arms.

The repository's own formulation, from the same operative sheet: *every protection's refuse arm
exercised on the real path with a positive control; and every accept arm either exercised, or
explicitly deferred to the act with its failure mode named.*

### R5 — AN INABILITY IS NOT A VERDICT.

*Cannot check* is its own outcome with its own exit code, never folded into pass or fail.
**170 mentions of fail-closed**, and `2` reserved for the inability.

**The incident:** a tally of zero from a probe that could not look. Recorded repeatedly — a
`sacct` query that printed a header and no rows, a `find` whose error its own `2>/dev/null`
swallowed, a `grep` whose pattern could not match the line that would refute it.

## 3. ⚠ WHAT THE COMPRESSION REVEALED — and my measurement of it was WRONG TWICE, both times in my favour

**The gap is 5 tests, not 53.** The chain below is kept in full because the two corrections are more
instructive than the finding, and both errors made the defect look bigger and my work look more
necessary.

| pass | instrument | "deficient" | why it was wrong |
|---|---|---|---|
| 1 | *no `assertIn` in the body* | **53** | treats a **message substring** as the only way to identify a refusal |
| 2 | *no assertion whose operand is anything but the exit code* | **28** | many tests pin **structured receipt fields** — `record["violation"]["module"]`, `by_depth[1]["verdict"]`, `refusal_site` — which is **stronger** than a substring, not weaker |
| 3 | *the asserted exit code is SHARED by another condition of the same entry point* | **5** | where each condition has its **own** code, the code **is** the discriminator |

**Pass 3 is the right question**, and the reason is R3's own incident: a segfault at `rc=139` was
read as a refusal because the check asked `rc == 0` instead of `rc == <the specific code>`. A test
asserting `rc == 4` is immune to that. A test asserting `rc == 9` is **not**, when three different
conditions all exit 9.

One test in the family says this in its own name:
`test_the_refusal_SITE_is_a_field_because_exit_3_cannot_carry_it` — the suite had already reached
this conclusion and solved it with a field. My first two instruments could not see that solution.

### The genuine five, and they are REPAIRED

All in `run_m1_diagnostic.sh`'s refusal ladder, where two codes are overloaded:

| test | shared code | now also pins |
|---|---|---|
| `test_output_into_a_product_tree_refuses_rc6` | `6`, with the missing-marker case | *"points into a publication or candidate product tree"* |
| `test_output_into_the_candidate_projection_tree_refuses_rc6` | `6` | the same message |
| `test_missing_r5_receipt_refuses_rc9` | `9`, with two meter refusals | *"no R5 receipt at"* |
| `test_exhausted_headroom_refuses_rc9` | `9` | *"R5 admission REFUSED"* + **`meter rc 5`** |
| `test_stale_receipt_refuses_rc9` | `9` | *"R5 admission REFUSED"* + **`meter rc 4`** |

**The meter's own rc is embedded in the message** (`lib_r5_admission.sh:101`), and it is the only
thing separating a ceiling refusal from a staleness refusal — both exit 9. That the codes are 5 and
4 was **verified by running**, not read off the comment beside them.

**AND THE ASSERTIONS WERE POWER-TESTED.** Swapping `meter rc 5` for `meter rc 4` in the ceiling test
makes it **fail**, so the two assertions genuinely discriminate rather than both matching whatever
the meter prints. `27 passed` before the mutation and after restoring it; `1 failed` during.

⚠ **What is NOT claimed:** that the other 23 of pass 2's 28 are correct. They pin an exit code that
is unique among *the conditions this suite tests*; an untested condition sharing that code would be
invisible. That is a limit of the corpus, not a defect in those tests, and it is the same limit §4
states about the whole document.

## 3b. ⚠ THE SUPERSEDED FINDING, KEPT VERBATIM

**Everything in this section is the pass-1 reasoning and its conclusion is WRONG.** It is retained
because deleting a superseded count leaves the next reader no way to tell a corrected number from a
number nobody checked — and because the error is the recurring one: an instrument that could only
see the remedy *I* had in mind, reporting every other remedy as an absence.

*Original text follows.*

This is the payoff Joseph predicted, and it is a gap rather than an insight, which is the more
useful kind.

Of the 958 extractable refusal bodies, **211 read an exit code**. Of those:

| | |
|---|---|
| pin the exit code **and** a message | **158** (75%) |
| pin **only** the exit code | **53** (25%) |

Those 53 assert that something was refused **by number alone** — which is precisely the condition
under which three segfaults read as three refusals. Examples:
`test_end_to_end_refuses_a_synthetic_fixture_closure`,
`test_a_root_carrying_the_data_only_component_is_REFUSED`,
`test_a_grandchild_is_refused_and_records_depth_two`.

⚠ **AND THE SCOPING MATTERS, BECAUSE THE RAW RATIO OVERSTATES IT.** 389 refusal bodies pin a
message and **no** exit code, and for most of them that is correct — they assert a Python exception
in-process, where there is no exit code to pin. **R3 is a rule about subprocess refusals**, so the
denominator is 211 and not 958. Read as "53 of 958" it would look like a systemic failure; read as
"53 of 211" it is a specific, listable repair.

**Not repaired here.** Adding a message assertion to 53 tests requires knowing what each guard's
message actually is, which is 53 small verifications and not a sweep — and a sweep that guessed
would be the defect R3 exists to prevent.

## 4. What this is for, and what it is not

**For the note.** The analysis note describes constructions, closures and budgets, and contains
**no compact statement of what the pipeline refuses to do**. §2 is that statement in five rules. It
is short enough for a methods paragraph and each rule is traceable to instances.

**For the suite.** It gives the suite, for the first time, a candidate test of the *rule* rather
than of 1,061 instances of it — and §3 is a worked example of what such a test finds.

⚠ **THE LIMIT, AND IT BOUNDS EVERYTHING ABOVE.** A spec derived from the existing tests can only be
as complete as they are. **It cannot discover a rule nobody encoded.** So:

- *"the spec is green"* must never be read as *"the behaviour is specified"*;
- the absence of a sixth rule here is evidence about the suite, not about the pipeline;
- and **nothing in §2 is enforced by anything.** These are descriptions. Making one executable is a
  separate proposal with its own power tests, and would be the first thing to get wrong.

**NOT AUTHORIZED BY THIS DOCUMENT:** deleting, merging or rewriting any test. The consolidation rule
stands — additive first, and every deletion names the finding it retires. On the evidence of §3 the
deletion question may never be worth asking: once the rules are written down, the 1,061 instances
cost only disk, and they caught three separate things this week.

**Co-Authored-By: Claude Opus 5 (1M context)**
