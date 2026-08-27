# F-8(b) redesign — NOTHING IN THE TOOLCHAIN RETURNS 0

> **SUPERSEDED TITLE, kept because prior verdicts cite this document:** *"a linter that cannot pass,
> and an attestation that can"*. The second clause stopped being true at `65ee6476`. The filename
> still says `attestation-gate`; the attestation checker is **not** the gate and the name is retained
> only because five preserved verdicts and the MANIFEST bind to this path.

**CITABLE FOR:** the design and exit-code contract of `verify_run_receipt_blind_spots.py` and
`verify_f8b_attestation.py` **as stated in §2, which is the current contract surface**; the measured
correction to the recorded BREAK-1 result; two defects measured in the §10.1 readiness verdict.
Sections 3.1–3.5 are a HISTORY of superseded states and are citable only as history — where they
describe an exit-0 result they describe a version that no longer exists.

**NOT CITABLE FOR:** discharge of F-8(b) — nothing here discharges it. **Gate 2 remains FAIL.** No
rehearsal is authorized, none was run, no receipt for `k0-aa67c426-20260824T145751Z` is created or
backfilled, and no estimator, covariance, adoption, compute result or publication claim is touched.

**AUTHOR.** `claude-school-main` (publication close-out lane), conversation
`0a6252ff-192d-41ee-ab49-c749f55c97f9`. This lane **wrote both instruments** and therefore cannot
grade them. Independent grades are recorded separately.

## 1. What was blocked, and by whom

The §10.1 readiness review returned **`READINESS-10-1: NOT READY`**, preserved verbatim at
`docs/orchestration/runs/agy-g2-gate-verifier/20260826-readiness-10-1-VERDICT.md`, sha256
`67bee6f2dd710659d1442780c99792ef5c6d4dc0e33dca00b76104c16c87099e`, 8136 B. All three mechanisms
were answered *present and independently graded: YES*; the block was the fourth question:

> *do the prefilter's rc=0 semantics create a fail-open gate?* **YES**

> *"A mechanical check that outputs a green rc=0 creates a strong anchoring effect, degrading the
> likelihood that a subsequent human or grader will perform the 'mandatory' prose judgment with
> sufficient skepticism… While the script prints 'THIS IS NOT A DISCHARGE OF F-8(b)', a label is
> insufficient protection against the systemic risk of a future lane simply citing the rc=0 result
> as proof of compliance, especially when the 'mandatory independent prose judgment' is a process
> intention rather than an encoded, cryptographic gate."*

The redesign below was authorized by the Codex proxy to whom Joseph delegated PASS/BLOCK authority.

## 2. The design

**The linter has no passing exit status.** Not a relabelled one — an absent one. There is no green to
cite, so the anchoring argument has nothing to anchor on and the "future lane cites rc=0" failure
mode is unreachable rather than discouraged.

`docs/orchestration/verify_run_receipt_blind_spots.py`

| exit | meaning |
|---|---|
| **10** | `REVIEW_REQUIRED` — mechanically acceptable. **Not a pass.** Emits a JSON report bound to the receipt's sha256, whose `this_is_not_a_pass` field says so in the artifact itself, not only on stdout. |
| 2 | CANNOT CHECK — an input could not be read. |
| 3 | NO SECTION — absent or empty blind-spots section. |
| 4 | INCOMPLETE — a blind spot is not addressed; the spot is named. |
| 5 | TRANSCLUDED — a ≥200-char verbatim run shared with F-8(a) §1.6. |

Missing, incomplete and copied stay **three distinct codes**; collapsing them would hide which
fired. `0` is unreachable by construction and `test_no_exit_constant_in_the_module_is_zero` plus
`test_no_input_whatsoever_can_produce_exit_zero` are the encoded form of the ruling.

**THE GATE IS A RECORDED AUTHORITY DECISION, NOT A PROGRAM.** No exit code discharges F-8(b).
`docs/orchestration/verify_f8b_attestation.py` is a CONFORMANCE CHECKER over a recorded independent
prose attestation. It has **no zero exit**:

| exit | meaning |
|---|---|
| **11** | `ATTESTATION_WELL_FORMED` — complete and correctly bound. **Not a pass, not a discharge**, not a finding that the judgement is correct, and **not** a finding that the named reviewer wrote it. |
| 2 | CANNOT CHECK — an input could not be read or parsed. |
| 3 | REJECTED — any requirement below unmet. |

`0` is unreachable by construction; `test_no_exit_constant_in_the_module_is_zero` and
`test_no_attestation_whatsoever_can_produce_exit_zero` are the encoded form of that. It reaches **11**
only when the attestation:

1. binds the **exact** receipt sha256 **and** the **exact** linter-report sha256, both recomputed
   from disk at validation time — so editing either artifact afterwards invalidates the attestation
   without anyone having to remember to mark it superseded;
2. names **both** parties as `{role, conversation_uuid}` and rejects self-attestation on **either**
   field — a lane can rename itself, and one conversation can claim two roles;
3. carries a written independence basis above an emptiness floor;
4. gives a **distinct, non-empty** semantic finding of at least 80 characters for **each of the four
   blind spots — a FLOOR, not a ceiling**: additional blind spots are welcome and held to the same
   floor. Duplicates across spots are rejected on a **letters-only** normal form, and a finding with
   no letters at all is rejected outright;
5. explicitly addresses the copying / word-salad risk (≥80 characters);
6. carries a `verdict` field of **`PASS`** — the REVIEWER's word, not this tool's. `FAIL`,
   `CANNOT CHECK`, absent, and `PASS WITH RESERVATIONS` are all rejected. **A `PASS` in that field
   still yields exit 11, never 0**;
7. carries only declared top-level and party fields — the schema is **strict**, so an undeclared
   field such as `verdict_hedging` is a rejection rather than something ignored;
8. keeps identity fields printable **ASCII**, with `conversation_uuid` in canonical uuid form, and
   roles compared on a punctuation-and-case normal form that **keeps digits**;
9. omits `status`, or sets it to exactly `filed` — an **allowlist**; and omits `superseded_by`, or
   names a real successor, a present-but-falsy value being a rejection;
10. does not sit under `docs/orchestration/runs/<dir>/` with a `<dir>` disagreeing with the claimed
   reviewer. That is a **refusal only** — the convention is not authentication, since any writer can
   create any role directory, and agreement with it establishes nothing and is never reported.

**Independence is checked structurally, never by grading prose.** Word-count, keyword-density and
threshold-tuning fixes were explicitly ruled out and none was added. The comparison that does the
work is two distinct conversation uuids, which is a fact a program can actually check.

**WHAT EXIT 11 DOES NOT CLAIM,** and the tool prints all of this whenever it reaches 11: it checks the
recorded **decision and its bindings**, not the semantic truth of the judgement, and not that the
named reviewer wrote the file. A reviewer who writes four
thoughtful-looking findings about a bad receipt produces a valid attestation of a wrong judgement.
What is established is that a named party who is not the author judged **these exact bytes**, and
cannot silently reuse that judgement for different ones.

## 3. Tests, and their power

**88 arms, all OK: 18 in `test_verify_run_receipt_blind_spots.py` and 70 in
`test_verify_f8b_attestation.py`.** Not 103 — **that figure, which this lane relayed and which
reached an authorization, was wrong.** It came from running the glob `test_verify_*.py`, which also
picks up the pre-existing, unrelated `test_verify_receipt_artifacts.py` (15 arms). 18 + 70 + 15 =
103; the two F-8(b) suites are **88**. Cite the two suites by exact filename, never the glob. Every requirement has an arm that **removes** it and asserts
rejection, and `EveryRequirementHasARemovalArm` reads the suite's own source so a future field added
without a removal arm fails the suite.

Mutation-measured, because a suite of only good-input arms proves nothing about refusal:

| mutant | result |
|---|---|
| validator returns `PASS` unconditionally | **38 of 50 fail** |
| linter's `REVIEW_REQUIRED_EXIT` set back to `0` | **5 of 18 fail**, including the two named no-green arms and the recorded-break arm |

The two recorded adversarial texts are **read from the grader's verdict file at test time and its
digest asserted**, not copied into the suite. A copy could drift from the evidence; this coupling
makes deletion or edit of the preserved examples a loud test failure.

## 3.1 The first implementation grade returned UNFIT, and it was right

`agy-f8b-impl-grade` (conversation `d71dbff7-9710-4bd9-94e3-a0dc3ac436f0`) graded `da6e28aa`
**`F8B-REDESIGN-GRADE: UNFIT`** — *is the attestation validator fail-closed?* **NO**. The linter's
unreachable zero, the non-overstatement and the scope were all confirmed YES; the validator was not.
It found three ways to pass an attestation that should not pass. **All three were real.** Its exact
inputs are now arms in `TheAdversarialInputsFoundByTheIMPLEMENTATIONGRADE`.

| its finding | status | how |
|---|---|---|
| unknown top-level fields were **ignored**, so `verdict_hedging: "PASS but with some reservations"` sat beside a clean `verdict: PASS` | **CLOSED** | the schema is strict at top level and inside both party objects; an undeclared field is a rejection, not a shrug |
| `conversation_uuid` was any non-empty string, so author `uuid-1234` and reviewer `uuid-123` read as two parties | **CLOSED** | canonical uuid form required, which makes "distinct string" and "distinct conversation" the same fact the check was already assuming |
| four findings that differ trivially — the same 80-char run plus `1` and plus `2` — counted as four judgements | **CLOSED** | duplicate detection now compares a letters-only normal form. **Not a similarity threshold**: there is no distance and no tunable number, because a similarity metric on prose is exactly what was ruled out |

Re-measured against the fixed validator with a **passing control in the same run** (unmodified
attestation → `rc=0`), so that a rejection cannot be credited to the wrong cause: all five of its
bypasses now return `rc=3`, each naming its own reason. Disabling any one of the three new guards
fails 2 arms.

**A FOURTH HOLE IS OPEN AND IS NOT CLOSEABLE HERE, so it is disclosed rather than papered over:**
**nothing binds an attestation to the party it names.** There is no signature in this campaign.
Whoever can write the file can type any role and uuid into it, or retype a real reviewer's digests
for a different receipt. And findings that differ by more than a trivial edit are accepted as four
judgements whether or not they are. Both are **process** guarantees, not mechanical ones. The
validator says so on the pass path and in its docstring, and
`test_the_UNCLOSEABLE_hole_is_disclosed_on_the_pass_path_and_in_the_docstring` fails if that
disclosure is removed.

## 3.2 Second grade, also UNFIT: four more closed, and ONE UNRESOLVED STRUCTURAL OBJECTION

`agy-f8b-impl-grade` re-graded `8f1ef2e2` **`F8B-REDESIGN-GRADE-2: UNFIT`**. It confirmed *all three
of your earlier findings actually closed: **YES***, confirmed the suites, the power measurements and
the scope, and judged this design record's §3.1 to represent its grade **fairly**. Two items failed.

### The six new inputs: four were closeable, two were the residuals already disclosed

| input | disposition |
|---|---|
| author `close-out lane` / reviewer `close out lane` | **CLOSED** — roles now compare on the same letters-only normal form the findings use, so punctuation aliases are one party |
| `аuthor` (Cyrillic а) vs `author` | **CLOSED** — identity fields must be printable ASCII; one invisible byte defeated the whole independence check |
| `status: "pending"` | **CLOSED** — the status check was a DENYLIST banning draft/withdrawn/retracted, so it waved through every unfiled-sounding value nobody had thought of. It is now an ALLOWLIST: `filed`, or omit the key |
| `superseded_by: false` / `""` / `null` | **CLOSED** — present-but-falsy is now rejected as ambiguous rather than read as absent |
| two fabricated but well-formed uuids pass | **NOT A NEW FINDING** — this is the disclosed fourth hole. No signature exists; form is all a program can check |
| findings ending `potato` vs `tomato` pass | **NOT A NEW FINDING** — the disclosed residual. Closing it needs a similarity threshold on prose, explicitly ruled out |

Re-measured with a passing control in the same run (unmodified → `rc=0`): the four closed cases
return `rc=3` naming their own reason; the two residuals return `rc=0` and now have arms that
**assert they pass**. That is deliberate — an undisclosed hole and a disclosed one are different
objects, and pinning the disclosed behaviour is what stops it being quietly re-described as closed.

**The grade slightly overstated here, and it should be said:** it listed all six as evidence the
validator "retains fail-open surfaces", counting two documented, un-closeable residuals as new
findings. Four were new; two were the thing the previous commit had already written down.

### THE UNRESOLVED ITEM — and it is a governance question, not an engineering one

> *is the fourth hole's disclosure adequate?* **NO.** *"The current validator repeats the exact same
> mistake: it emits an `rc=0` for an unauthenticated file lacking a cryptographic signature, while
> merely printing that the independence is a 'PROCESS guarantee, not a mechanical one'. Emitting
> `rc=0` while explicitly relying on a printed label to disclaim mechanical verification is the same
> structural failure that was ruled insufficient."*

**Where it is right, and I think it substantially is:** the SHAPE is identical to what §10.1 struck
down. A machine-readable success plus a human-readable caveat — and the caveat is invisible to every
pipeline that will ever consume the exit code. "A future lane cites the exit 0 as proof of
compliance" is exactly as available here as it was for the linter.

**Where it differs, and this is not nothing:** the linter's `rc=0` stood for a judgement that HAD
NOT OCCURRED. The validator's stands for one that HAS — recorded, bound to exact bytes, by a named
party who is not the author. The gap is the AUTHENTICITY of the naming, not the EXISTENCE of the
judgement. Those are different sizes of hole. But the load-bearing part of F-8(b) is precisely
whether a real independent party really read the prose, so an unauthenticated name is a gap in the
one place it matters most, and that is why I do not think the distinction rescues the design.

**THE AVAILABLE FIX, AND WHY THIS LANE DID NOT APPLY IT.** Give the validator no zero exit either: a
distinct non-zero `ATTESTATION_WELL_FORMED`, meaning *"complete and correctly bound; whether F-8(b)
is discharged is a decision for the gate authority."* Then **nothing in the F-8(b) toolchain returns
0**, consistently, and the clause is discharged by a recorded authority decision citing a well-formed
attestation — which is what §10.1 asked for in the first place.

That change **contradicts the standing authorization**, which specifies a validator that *"can return
success"* and *"ends in an unambiguous PASS"*. Whether F-8(b) may be closed by machinery at all, or
only by a recorded human decision, is the decision-maker's call and not this lane's. **It is referred,
not decided here, and the branch is NOT landed to `main` while it is open.**

## 3.3 RESOLVED against the authorization's letter: the checker has no zero exit either

**The §10.1 re-run agreed with the implementation grade, independently and on the same reasoning.**
`agy-readiness-rerun` (conversation `2fbd0b4f-da89-4a90-bf95-7f847dfc226d`), a role that neither
built the mechanisms nor authored the remedy prescription, returned
**`READINESS-10-1-RERUN: NOT READY`** with all three mechanisms confirmed *present at this tip and
independently graded: YES*, and:

> *is the fail-open gate closed rather than moved?* **NO** — *"A fail-open surface that can be
> bypassed by spoofing identity is structurally identical to a fail-open surface that can be
> bypassed by spoofing prose."*
>
> *should the validator also have no zero exit?* **YES**
>
> *can F-8(b) be closed by machinery at all?* **NO** — *"F-8(b) can only be closed by a recorded
> human decision."*

It also verified **both record corrections by its own measurement** — BREAK 1 at `rc=3`, the repaired
stuffer at `rc=0`, and the first run's tip missing the instrument — and judged the handling proper.

**Three independent reads now agree, including this lane's own.** The defence that failed was that
the linter's green stood for a judgement that had NOT occurred while the checker's stands for one
that HAS. That difference is real and it is not sufficient: it holds only if the attestation is
authentic, and nothing mechanical here can establish authenticity.

**So `verify_f8b_attestation.py` no longer has a zero exit.** Its best outcome is
**`11 ATTESTATION_WELL_FORMED`** — complete and correctly bound, explicitly *not* a discharge, *not*
a finding that the judgement is honest, and *not* a finding that the named reviewer wrote it. It is
no longer described as the gate. **The gate is a recorded authority decision citing a well-formed
attestation.** Nothing in the F-8(b) toolchain returns 0.

### THIS EXCEEDS THE LETTER OF THE STANDING AUTHORIZATION, DELIBERATELY, AND IS ISOLATED SO IT CAN BE DROPPED

The authorization specified a validator that *"can return success"* and *"ends in an unambiguous
PASS"*. **This change contradicts that sentence** while serving the same instruction's stated intent
— *fail-closed* — which two independent reviews say the literal reading defeats.

It is committed **alone**, touching only the checker, its tests and this section, so that reverting
exactly one commit restores the authorized behaviour without disturbing anything else. It moves only
in the conservative direction: it removes a passing status and can never manufacture one. **The
branch is not landed to `main`.** If the decision-maker prefers the literal reading, drop that one
commit; the referral in §3.2 stands either way.

## 3.4 Two defects this lane found in its OWN fixes, neither caught by any grader

Both were introduced by a guard added to close a grader's finding, and both were found by asking
what the new guard does in the direction it was *not* written for. **Neither of the two grades
caught either one** — both were probing for things that should be refused and were passed, never for
things that should pass and are refused, nor for a guard that opens a hole one line after closing one.

**(i) A false positive, `4798f927`.** Comparing roles on the findings' letters-only form closed the
`close-out lane` / `close out lane` alias and collided **`codex-school` with `codex-school2`** — two
real profiles in this repo — plus `agy-g2-gate-verifier` with `agy-g3-`. All three would have been
refused as self-attestation. It fails **closed**, so it blocks honest attestations rather than
passing dishonest ones, which is the safe way to be wrong and still wrong. Role identity now keeps
digits; findings still strip them, because there the digit was the whole trick.

**(ii) A false negative created by a guard against (i)'s shape.** The duplicate check skipped
comparison when a finding's normal form was empty (`if key and key in seen…`). 80+ characters of
punctuation clears the length floor and normalises to the empty string, so **two IDENTICAL letterless
findings counted as two judgements** — measured `rc=11` before the fix. A finding with no letters is
now rejected outright.

**The transferable part:** a guard added to fix a reviewer's finding is unreviewed code, and it is
written in a hurry under the impression that the thinking has already been done. Both of these were
in the *fix*, not the original.

## 3.5 A fourth, UNINVOLVED review dissents: `F8B-SOUNDNESS: UNSOUND`

`agy-f8b-soundness` (conversation `c12551c8-3da6-43f4-be8b-129c6ad9f48c`) was commissioned because
the previous reviewer said so itself — *"a fourth, uninvolved role is necessary"* — and because the
first three parties all agreed with each other, which is the condition under which a shared wrong
assumption survives. It was told it could conclude the whole redesign was theatre. **It did.** Its
five findings are recorded here graded individually, because they are not of equal quality.

### ONE FINDING IS REAL AND IS FIXED

**The four blind spots were a CEILING, not a floor.** The validator rejected any `per_spot_findings`
key outside F-8(a)'s four, so a rehearsal receipt that disclosed a **fifth** blind spot could not
have that disclosure attested. *"The attestation validator restricts the reviewer to evaluating only
those four hardcoded spots, actively rejecting any additional blind spots the producer might have
found."* That is the opposite of what the clause wants and it is now reversed: the four are required,
extras are welcome and are held to the same floor and distinctness. Nobody else caught it, including
this lane, and it is the clearest argument for having commissioned a fourth read.

### ONE FINDING IS REFUTED BY MEASUREMENT

**The claimed underscore hole does not exist.** It reported that `_role_key` and `_skeleton`
*"rely on the `\W` regex character class"*, which does not match underscore, so
*"`close-out lane` can self-attest by naming the author `close_out_lane`"*.

**Measured at the tip it reviewed: the file contains ZERO occurrences of `\W`.** The normalizers are
`[^a-z]` and `[^a-z0-9]`, under which underscore IS stripped. `close-out lane` and `close_out_lane`
both normalise to `closeoutlane` and **do collide**, so that self-attestation is caught; `finding 1`
and `finding_1` both skeleton to `finding`. **The reviewer described an implementation it did not
read** — the same failure this campaign already recorded once this week, in the review whose blocker
started this whole sequence.

### ONE IS OVERSTATED, AND IS TAKEN ONE-DIRECTIONALLY

It proposed `docs/orchestration/runs/<role>/` as an identity mechanism *"the lane missed"*. It is not
one: the attestation path is a command-line argument and any writer can create any role directory, so
satisfying the convention proves nothing. Treated as a credential it would be precisely the false
guarantee this redesign exists to remove. **Implemented as a REFUSAL ONLY** — a path under `runs/`
naming a role other than the claimed reviewer is rejected; agreement earns nothing and is never
reported. A test asserts that the passing output mentions neither the path nor authenticity.

### TWO ARE DISSENT ON THE OPEN GOVERNANCE QUESTION, AND ARE RECORDED AS DISSENT

> *is the no-green design sound rather than theatre?* **NO** — *"future lanes will inevitably wrap
> them in constructs like `verify_f8b.py || [ $? -eq 11 ]`… This wrapper restores the very `rc=0`
> 'green' the redesign tried to eliminate."*
>
> *was the original automation-bias diagnosis correct?* **NO** — *"a mechanical pre-filter returning
> 0 simply means 'mechanical pre-conditions are met, proceed to human review.' It does not defeat
> the human review; it enables it… The original pre-filter was adequate."*

**This directly contradicts the two reviews that required the change**, and this lane does not resolve
it. The wrapper argument is a good one and nobody in the chain had made it. **The count is now two
reviews for the no-green design and one against, which is not a vote and should not be read as one.**
The alternative it proposed — a signed artifact consumed downstream — is unavailable here: there is no
signing infrastructure in this campaign, which is the same fact that makes the fourth hole open.

**The governance question in §3.2 is therefore WIDER, not narrower, than when it was referred:** not
only *may F-8(b) be closed by machinery*, but *was the original diagnosis right at all*. If it was
not, `65ee6476` and possibly the whole redesign should be dropped. That is the decision-maker's call.

## 3.6 Final-tip grade: FIT, substantiated only on demand, with one inaccuracy inside it

`agy-f8b-final-tip` (conversation `7a312e96-cc1b-46c7-866e-952939d68f28`), the first role that neither
authored nor resolved this branch, graded the doc-only repair **`F8B-FINAL-TIP: FIT`** on all seven
questions. Preserved verbatim at
`docs/orchestration/runs/agy-f8b-final-tip/20260827-f8b-final-tip-VERDICT.md`.

**Its first delivery cited no operands at all** — no digest, no exit code, no arm count, no AST
result, and no mention of the 88-vs-103 discriminator the brief had planted precisely because only
running the suites can answer it. It was sent back to substantiate, not re-graded. **The substantiated
measurements then matched this lane's own, exactly:**

| measurement | grader | this lane |
|---|---|---|
| AST minus docstrings, both instruments | IDENTICAL | IDENTICAL |
| linter on acceptable prose / checker well-formed / checker absent file | 10 / 11 / 2 | 10 / 11 / 2 |
| extra spot long / below floor / pasted | 11 / 3 / 3 | 11 / 3 / 3 |
| role-path mismatch / match, and `authentic` in passing output | 3 / 11, absent | 3 / 11, absent |
| arm counts by exact filename | 18, 70, and 15 in the unrelated file — **total 88** | 18, 70, 15 — **88** |
| `--check --committed-only` | rc=0, `rows=572` | rc=0, `rows=572` |
| all seven prior verdict digests + byte counts | pasted | **all seven verified equal by recomputation** |
| any prior verdict EDITED in `4beb63ee..5b1f989c` | none, all `A` | none, `464 insertions(+)`, zero deletions |

**ONE INACCURACY, recorded because a verdict's own reliability is evidence.** Citing condition 1 it
quoted three lines of `verify_f8b_attestation.py`; the first two are verbatim and the third,
`if att.get(key) != actual:`, **does not appear in the file** — the real code is `claimed =
att.get(key)` / `if not claimed:` / `elif claimed != actual:`. Its **line numbers were exact** (232-237
and 341-347) and its condition-6 quote **is** verbatim, and the substance is right: both digests are
bound and a mismatch is rejected. So this is a paraphrase presented as a quote, not an invented
mechanism — a much smaller thing than §3.5's `\W` claim, but the same family, and it is the third
time in this branch that a reviewer has produced text attributed to source that source does not
contain. **Grade findings individually; the numbers here are corroborated, one inline quote is not.**

**A COSMETIC DEFECT FOUND BY THIS LANE AND DELIBERATELY LEFT:** one short extra blind spot emits
**two** messages — the generic 80-character floor from the main loop, which now iterates extras, plus
the dedicated "ADDITIONAL blind spot" note. Exit code and defect identification are correct; the text
is redundant. Not changed, because the authorized arm was doc-only and forbade behaviour changes. It
is a candidate for a later cleanup, not a defect in the contract.

## 4. CORRECTION — the recorded BREAK 1 result does not reproduce

`20260826-f8b-VERDICT.md` records `rc=0` for both breaks. **Measured, with the exact recorded texts,
against the pre-redesign instrument at `f31d07df`:**

| example | recorded | **measured (old instrument)** |
|---|---|---|
| BREAK 1, keyword-stuffing | `rc=0` | **`rc=3`** — refused. `namespace-packages` and `already-imported-modules` both NOT ADDRESSED |
| BREAK 2, moral paste | `rc=0` | `rc=0` — **confirmed**, longest shared span 150 chars against a 200 threshold |

BREAK 1's string — `origin is none sys.modules child process .sh` — contains neither `namespace` nor
any `already-imported` alternate, so the old instrument always refused it. **The keyword-stuffing
CLASS is real even though the recorded instance is not:** adding exactly the two missing words and
nothing else gives `namespace origin is none sys.modules install( child process .sh`, one line of
pure stuffing, which the old instrument passed at **`rc=0`** (measured). That string is
`STUFFER_THAT_WORKS` in the suite and has its own arm.

The grader's verdict file is **preserved unedited** — it is not this lane's to correct. The false
annotation is corrected here and in the author disposition, which is this lane's own file.

**This does not overturn the readiness block.** BREAK 2 alone demonstrates the fail-open mode, and
the readiness review's central argument does not depend on either example.

## 5. Two defects measured in the §10.1 readiness verdict itself

Recorded so the re-run does not inherit them, **not** as grounds to discount the verdict:

1. **It recorded `TIP SHA: 3ae656951734bc90371bd64c56ccc4ce970b1470`** — local `main` — while the
   brief named branch tip `f31d07df`. Measured: `verify_run_receipt_blind_spots.py` is **ABSENT** at
   `3ae65695`, ABSENT at `4beb63ee`, and PRESENT only at `f31d07df`; it is also absent from the
   primary checkout's working tree. **The reviewer never had the instrument source in front of it**,
   and its verdict quotes no instrument internals.
2. **It inherited both break results** — *"as demonstrated by the F-8(b) grader"* — rather than
   measuring them, which is how the false BREAK-1 result propagated into the readiness reasoning.

Its three *present and independently graded: YES* answers are nonetheless **true of `f31d07df`**,
verified here: the exclusion-digest pin (`57508b31`, an ancestor), `compare_m1_m6.py` and
`measure_m1_m6.py` are all present in that one tree. The answers are correct; they were not
established by what the reviewer measured. The §10.1 re-run must name and verify its tip, and must
measure the adversarial examples rather than inherit them.

## 6. What still stands between here and Gate 2

Unchanged by this work: producer filings for **F-2(b)**, **F-3(b)** and **F-5(b)**; the rehearsal
itself; and F-17(b)'s `:1471` half, which **cannot be backfilled for this rehearsal** — only a new
forward-only rehearsal can satisfy it. **Gate 2 remains FAIL, with no partial credit.**
