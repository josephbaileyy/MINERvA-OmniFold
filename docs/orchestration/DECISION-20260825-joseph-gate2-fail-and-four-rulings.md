# DECISION 2026-08-25 — Gate 2 recorded FAIL; Joseph's four rulings

Author: publication close-out lane (the producing lane; see the independence ledger in §6 for what
that disqualifies me from). Decision-maker: Joseph. This document records a ruling. It does not
grade anything, and nothing in it may be read as a grade.

## CITABLE FOR

- The Gate-2 outcome for run `k0-aa67c426-20260824T145751Z`: **FAIL, no partial credit.**
- The per-clause record **as ruled**, which differs from the grader's filed grades on three clauses.
- Joseph's four rulings and what each one forecloses.
- The defect ledger for the far-end evidence path, including which defects are corrected, which is
  irreparable, and which is bounded.
- The next admissible sequence, and the fact that no compute is authorized by this ruling.

## NOT CITABLE FOR

- Any clause being discharged. Six of nine are NOT DISCHARGED; three PASS. Nothing here discharges
  Gate 2, and Gate 2 remains open.
- Adoption, consumption, or quoting of any product of this run. That prohibition is unchanged and
  survives this document.
- The `:1471` half of F-17(b) being pending, deferred, or scheduled. Ruling 2 forecloses all three
  readings.
- Gate-2 credit, uncertainty adoption, or any publication claim. None follow from this document or
  from the mechanism work it sequences.
- Any PET-scoped conclusion. This work is **GBDT uncertainty**; see §0.
- The state of `MANIFEST.tsv`. That is routed to F-14 / §7.0.7 and is deliberately out of scope here
  (§7).
- Any statement about the *canonical* checkout's working tree at submission time. Only its HEAD is
  established (§5, D-C note).

## 0. Scope, and a withdrawn framing

**This is the GBDT uncertainty work.** It is not PET work, and no PET-scoped conclusion may be drawn
from anything in this document.

Recorded because it is otherwise undiscoverable: the first committed version of this document, and
the message of commit `109bb130` that carries it, framed the non-authorization clause in PET terms
-- PET covariance adoption, `C_ML`, and a declined PET central/statistical pairing. Joseph withdrew
that framing on 2026-08-25 as mistaken and directed that it not enter the canonical record. The body
of this document is corrected. **A commit message is immutable, so `109bb130`'s still carries the
withdrawn framing** and a reader who finds it there should treat this section as governing.

**The four rulings themselves are unchanged by the correction.** Only the scope label moved.

## 1. Verdict

**Gate 2 of the k=0 rehearsal: FAIL.** No partial credit over the nine clauses of §7.0.18.

Three clauses PASS. Six are NOT DISCHARGED. The gate fails on any of the six independently, so the
outcome is not sensitive to ruling 1 — ruling 1 changes the clause record, not the result.

## 2. Clause record as ruled

The middle column is what the independent grader filed. The right column is the record after
Joseph's ruling 1. Where they differ, **the right column governs.**

| Clause | Grader's filed grade (`a3000487`) | AS RULED | Basis |
|---|---|---|---|
| F-1(b) | PASS | **PASS** | Producer-filed and independently reproduced |
| F-2(b) | PASS (measured by the grader) | **NOT DISCHARGED** | Ruling 1 — no producer filing exists |
| F-3(b) | PASS on substance, by a stronger instrument | **NOT DISCHARGED** | Ruling 1 — no producer filing exists |
| F-4(b) | PASS | **PASS** | Producer-filed; count correct, justification corrected (§5 D-B) |
| F-5(b) | PASS (measured by the grader) | **NOT DISCHARGED** | Ruling 1 — no producer filing exists |
| F-7(b) | NOT DISCHARGED | **NOT DISCHARGED** | No rehearsal pin recorded on any ref |
| F-8(b) | NOT DISCHARGED | **NOT DISCHARGED** | No run receipt authored |
| F-17(b) | NOT DISCHARGED | **NOT DISCHARGED** | `:1471` half impossible; ruling 2 |
| F-18(b) | PASS on delivery | **PASS** | Delivered |

F-6(b) is not one of the nine. It moved to a separate leg-6 gate and remains mandatory. Nothing here
touches it.

## 3. Ruling 1 — strict producer/grader separation under §7.0.10

F-2(b), F-3(b) and F-5(b) had no producer-filed evidence. The grader measured them itself and graded
its own measurements. That is a narrower §7.0.10 conflict than the one that disqualified me, but it
is the same conflict.

**Recorded as NOT DISCHARGED.** The grader's measurements are **retained as verification evidence**
and are not discarded — but verification evidence cannot substitute for a missing producer filing.
When a producer files these three, the retained measurements become an independent check of that
filing, which is worth more than they are worth now.

## 4. Ruling 2 — F-17(b) is not backfilled

The two-tree half of F-17(b) (`:621`) was measured, filed, and independently reproduced bit for bit.
**That measurement is preserved as a measurement.** It does not discharge the clause.

The `:1471` half obliges that any difference from `MEASUREMENT-20260822-m1-m6-at-pinned-sha.md` be
reported as a finding. That document is markdown prose; the comparator consumes `--json`; and no
`--json` column was ever filed pre-submission. **This rehearsal cannot discharge it.**

Three readings are foreclosed by this ruling:

- It is **not pending.** Nothing is scheduled that would complete it.
- It is **not deferred.** §7.0.8 forbids reading an impossibility as a deferral, and this ruling
  affirms that.
- It is **not backfillable.** Manufacturing the pre-submission column after the fact is barred
  outright by OI-123, and would be barred by this ruling even if OI-123 did not exist.

**Forward requirement:** future rehearsals must emit machine-readable `--json` evidence at **both**
ends. Prose at one end and JSON at the other is not a comparison; it is a comparison that cannot be
performed, discovered too late to fix.

## 5. Ruling 4 and the referent — `b2d7d4ca` is immutable

F-17(b)'s historical referent is `/pscratch/sd/j/josephrb/MINERvA-OmniFold` at
`b2d7d4ca24707344cf12f99c0aa51381b81dd445`. It is **immutable and must not be rewritten to make the
rehearsal pass.**

`/global/u2/j/josephrb/mnv-work/MINERvA-OmniFold` is redesignated the canonical checkout
**forward-only.** It was created 2026-08-25, after the 2026-08-24T07:58:01 submission, so it cannot
be the referent for anything taken at submission time. The redesignation changes nothing already
filed.

Because "the canonical checkout" now has two candidate trees, that phrase alone no longer identifies
anything. Cite path **and** digest, or cite nothing.

**What is and is not established about the referent.** Its HEAD is established as of submission: the
reflog shows HEAD last moved 2026-08-21 21:39:10 -0700 and it has not moved since, so `b2d7d4ca` was
its HEAD at submission time. **Its working tree is not established.** `dirty=742` (718 untracked +
24 modified) is a 2026-08-25 measurement, and untracked files could have appeared in the four
intervening days. So F-17(b)'s findings split into two evidentiary classes that must not be quoted
as one:

- **As-of-submission:** `M-4.head`, and everything downstream of tree identity — M-1, M-5, M-6.
- **2026-08-25 only:** `M-4.dirty` / `.untracked` / `.modified`, and `M-2.importable` (its population
  is `*.py` stems tracked *or* untracked, which is why the instrument already singles M-2 out as the
  perishable claim).

## 6. Ruling 3 and the independence ledger

The `bad_pattern` fail-open in `compare_m1_m6.py` is to be repaired, together with its test, now
that the §7.0.19 deployment freeze has expired with F-1(b) passing.

**The spec author must not repair or grade their own instrument.** Implementation and grading go to
independent parties. Because the prior GRADE's three pinned digests have all moved, that grade is
**expired**: the instrument that produced the filed record has never been graded, and the *repaired*
instrument needs a **new independent grade before it can support another Gate-2 filing.**

| Party | Disqualified from | Because |
|---|---|---|
| Publication close-out lane (me) | Grading any Gate-2 clause whose evidence I produced; repairing **or** grading `compare_m1_m6.py` | I produced the evidence and authored the instrument spec (§7.0.10) |
| Gate-2 grader (`a3000487`) | Grading a producer filing of F-2(b), F-3(b), F-5(b) | It measured those three itself |
| Comparator repairer (unassigned) | Grading its own repair | Ruling 3 |

The repairer and the grader of the repair must be different parties, and neither may be me.

Two determinations arising from this ruling are **delegated to the grader and are not decided here**;
see §12. Joseph declined to pre-rule on one of them deliberately.

## 7. Explicitly out of scope

**CORRECTED 2026-08-25, and the original wording was wrong in a way worth naming.** This section
said `MANIFEST.tsv` "was already stale on `main`" and was "routed to F-14 / §7.0.7 and handled
separately" — a dated observation written in a tense that reads as a live condition. It was
surfaced by the independent comparator-repair lane, which needed to know whether drift in its own
commit was its own.

Measured, each in a clean detached worktree at the named commit:

| Commit | `generate_manifest.py --check` | rows |
|---|---|---|
| `e428a645` | rc=**1**, OUT OF DATE | 525 |
| `a0d0e5a1` | rc=0, OK | 526 |
| `dce8e8cc` | rc=0, OK | 527 |
| `65f95600` | rc=0, OK | 527 |
| `7d0776b8` | rc=0, OK | 528 |

So the drift **was real at `e428a645` and was CLOSED by `a0d0e5a1`**, the Gate-2 grader's
second-pass regeneration, and has stayed closed since. It is not an open condition and nothing is
pending on it. Any manifest drift appearing in a commit after `a0d0e5a1` belongs to that commit's
author.

The "23 rows" figure originated with the Gate-2 grader and I had relayed it twice without deriving
it. Now derived: regenerating at `e428a645` and diffing against the committed manifest gives
**23 differing rows, of which 5 are rows absent from the committed file entirely** — so 23 is
correct, and it mixes two kinds of drift that are worth separating.

None of this changes or repairs the Gate-2 verdict, and no part of that verdict rests on it. The
F-14 discipline question is filed separately in
`DISCIPLINE-20260825-f14-manifest-coupling-omissions.md`.

## 8. Defect ledger for the far-end evidence path

### 8.1 Corrected in `38a7b16b`

**D-A — the digest bracket was loose while being described as tight.** `COMPARATOR_PRE` and
`EXPECTED_PRE` were read before both ruler passes: 44 min 48 s of wall clock on the filed run, with a
second copy of the script executing out of a mutation worktree inside that window. The failure is not
reduced sensitivity. An early PRE and the POST both read the reverted bytes and **agree with each
other**, so a file swapped, used, and reverted is caught by an adjacent PRE and missed by an early
one. Now adjacent to the call.

**D-B — the F-4(b) exclusion justification was false.** The block counted the run with
`find $RUN/inv -type f` and each sibling with a recursive `*.jsonl` search of the whole sibling
directory: two populations printed adjacent as though they were one. That is the origin of the
"298 jsonl" figure — those records are in `k0-a54038b2-20260823T205254Z/guard-inventories/`, a
directory name no glob in the script reads. Measured: `runs/*/inv/*.jsonl` = 374, equal to the run's
own count; two siblings have no `inv/` directory at all and the third's is empty. The
exclusion-by-name prevented nothing and is **defensive, not load-bearing**. The count of 374 was
always correct.

**Both prior explanations are RETRACTED and are not preserved as valid claims.** Specifically: the
comparator-tightness statement in `30ede740`'s message, and the F-4(b) exclusion rationale in
`a3ed8631`'s message and in the script's own pre-`38a7b16b` output. A reader encountering either
should treat it as superseded by this section, not as a weaker version of a true claim.

### 8.2 Irreparable, therefore recorded

**D-C — `a3ed8631`'s message states the canonical tree is "233 behind main" with no right-hand side
named.** Measured 2026-08-25: 233 against `30ede740`; **234 against `a3ed8631` itself**; 240 against
`HEAD` and `github/main`; 238 against the canonical tree's own `github/main`. Four answers to one
sentence, and the figure written into the commit is wrong at that very commit. The direction (0
ahead) holds. The commit message is immutable, so this is recorded rather than fixed. Any future
statement of this quantity must name its right-hand side and its date; a bare "behind main" is not a
measurement.

### 8.3 Bounded, and the bound is load-bearing

**D-3 — `bad_pattern` is fail-open on the dotless pattern `M-1[*`.** The breadth test is
`rsplit(".", 1)[-1] in ("*", "**")`, and a dotless pattern has no last segment, so the whole pattern
is compared against `"*"` and passes. Demonstrated on the real far-end inputs with a genuine
one-line citation: **all 19 M-1 findings suppressed as EXPECTED-BY-RULING**, expected 0 → 19, with no
warning and no refusal. The deny-list arm tests `("M-4", "M-4.*", "M-1[*].*", "*", "M-4behind",
"behind")` and omits `M-1[*` — the spellings someone thought to type.

**The filed record is UNAFFECTED**, and the bound is specific rather than reassuring: the far-end
script hardcodes the shipped expected-list path, and the suite pins that shipped list (adding the
bad pattern to it moves the suite from 64 pass to 4 fail). The exposure requires substituting a
different expected-list, which the filed path cannot do.

This is a **repairable defect**, not a disclosure. Ruling 3 assigns it.

**REPAIRED 2026-08-25 at `c8a29082`, and UNGRADED.** The repair replaced the deny-list breadth test
with a positive grammar. Two consequences for this section: the defect was **wider than described
above** — the implementer reproduced four further fail-open spellings, including one
(`M-4.*e*`) that reaches `M-4.head`, `.ahead` and `.behind` at once, which shows the class is not
merely "dotless" and that adding a seventh deny-list entry would not have closed it. And the
six-spelling deny-list arm described above still exists but is now a **regression pin**; the
covering control has moved to a fixture generated from the producer. Under ruling 3 this repair
cannot support another Gate-2 filing until an independent lane grades it, and it has not been
graded.

## 9. Compute and authorization

**No compute is authorized by this ruling.**

Nothing here confers **Gate-2 credit**, authorizes **uncertainty adoption**, or supports any
**publication claim**. The mechanism construction sequenced in §10 step 3 is authorized as mechanism
construction only and carries none of those either.

Leg 6 and the undeclared-member adoption route remain prohibited. No product of this run may be
adopted, consumed, or quoted while Gate 2 is open, which it is.

(An earlier PET-framed version of this paragraph was withdrawn; see §0.)

## 10. Next admissible sequence

1. **Land the canonical record.** This document.
2. **Independently repair and grade the comparator.** Repairer ≠ grader ≠ spec author (§6).
3. **Establish the required import/rehearsal pin and run-receipt path** — the F-7(b) and F-8(b) gaps,
   which are absences of evidence rather than disagreements about evidence.
4. **Perform a new forward-only rehearsal**, emitting `--json` at both ends per ruling 2.

Steps 2 and 3 are independent of each other and may proceed in parallel. Step 4 depends on both.

## 11. Cited artifacts, with the field named

Digests are content `sha256` truncated to 8 unless labelled otherwise. Note that a git **blob id** is
a sha1 over a header plus content and is a *different field* from a content sha256 — both appear
below and are labelled, because conflating them is how a receipt stops being falsifiable.

**Every digest below is AS-OF the commit named in its row or in the commit list that follows, not a
current state.** A later legitimate edit moves the digest and does not falsify this table. Stating
this because a cited digest otherwise silently converts into a prohibition on editing the file —
the comparator-repair lane correctly declined to update
`m1m6_expected_differences.json`'s now-understated prose note on exactly that reasoning, which means
the citation had already acquired a force it was never meant to have.

| Artifact | Field | Value |
|---|---|---|
| `VERDICT-20260825-gate2-k0-rehearsal-nine-clauses.md` | content sha256 | `72da7d60`, 30751 bytes |
| same file | git blob id (sha1) | `679f1b73` |
| `state/f17b-k0-aa67c426-20260824T145751Z.json` | content sha256 | `9109f371`, 53226 bytes |
| `compare_m1_m6.py` (unrepaired, as it produced the record) | content sha256 | `bace69d2`, 53667 bytes |
| `compare_m1_m6.py` (repaired at `c8a29082`, UNGRADED) | content sha256 | `68b4af12` |
| `test_compare_m1_m6.py` (repaired at `c8a29082`, UNGRADED) | content sha256 | `b355ecdc` |
| `m1m6_expected_differences.json` (**historical referent**, as it produced the record) | content sha256 | `56c2e0ef`, 4464 bytes |
| `m1m6_expected_differences.json` (prose note transcribed from the grade, per §12.1) | content sha256 | `92091ae8` |
| `measure_k0_farend_f1b_f17b.sh` (post-repair) | content sha256 | `c40e6b54`, 15722 bytes |
| `GRADE-20260825-f17b-comparison-instrument-fitness.md` (EXPIRED) | content sha256 | `aa1b6eee`, 41819 bytes |

Commits: `a3ed8631` producer filing · `30ede740` first bracket attempt · `38a7b16b` D-A and D-B
repairs · `a3000487` grader verdict · `a0d0e5a1` second-pass manifest regeneration.

Run: `/pscratch/sd/j/josephrb/k0r2/runs/k0-aa67c426-20260824T145751Z`, submitted
2026-08-24T07:58:01, seven jobs `57527866 57527869 57527870 57527872 57527873 57527874 57527875`,
all terminal, 1122 accounting rows `COMPLETED 0:0`, 374 guard inventories.

Frozen deploy tree: `/pscratch/sd/j/josephrb/k0r2/clean` at
`aa67c426afaa9b6ca91c9996637a6bade950da9a`, detached, porcelain 0, 782 tracked files,
`listing_sha256 fa3489e2...` — note that `listing_sha256` is a **field of the manifest**, not the
manifest file's own digest, which is `622ddc0a`.

## 12. Open determinations delegated to the grader (Joseph, 2026-08-25)

Both of these post-date §§1–11 and neither is settled by this document. They are recorded here
because a lane that reads only the message traffic will not find them.

### 12.1 The `m1m6_expected_differences.json` prose note — a CONDITIONAL protocol

That file's prose note still describes the superseded deny-list and now **understates** the guard the
repair installed. The comparator-repair lane declined to correct it because its digest `56c2e0ef` is
cited in §11.

**Ruling: the cited digest is an AS-OF identifier, not a permanent prohibition on editing the file.**
That restraint was correct given how §11 was originally written, and the defect was in my drafting,
not in the lane's judgement. What follows is conditional on the independent grade:

- **If the repair PASSES:** update the prose note to describe the **exact graded behaviour** — not the
  intended behaviour and not the implementer's summary of it. Record the new digest, **preserve
  `56c2e0ef` as the historical referent**, and regenerate `MANIFEST.tsv` **in the same commit**
  (F-14 / §7.0.7). Do not rewrite history.
- **If the repair FAILS:** the note is **NOT** updated. Nobody writes prose describing a rejected
  implementation.

**DISCHARGED 2026-08-25.** The independent grade came back **FIT, conditionally** (`69dafb2c`), so
the first branch applied. The note was updated by transcription from §8 of
`GRADE-20260825-d3-comparator-repair-fitness.md` — the table that grade produced by *running*
`bad_pattern`, not by reading it — and it now carries the open §12.2 question rather than
asserting a resolution. `56c2e0ef` is preserved above as the historical referent. Verified after the
edit: the file still parses, the comparator still returns the filed `32/0/32` at exit 20 over the
same inputs, and the suite is 76/76 rc=0 — a prose note must be inert to behaviour, and this one is.
The grade deliberately does **not** pin this file, so the transcription does not void it.

A consequence worth stating: the grade must be specific enough that the note can be written *from*
it. A verdict of "fit" alone leaves whoever updates the note with nothing to transcribe, so the
accepted and rejected pattern shapes have to be named precisely.

### 12.2 Partial wildcards in the `M-1` selector — NOT pre-ruled

The repair admits partial wildcards inside the `M-1` bracket, e.g. `M-1[nd-*].n_after`. The
implementer's justification is that a partial selector cannot exceed the breadth of the already-legal
bare `*`, and it stated plainly that this is **an argument, not a measurement**.

**Joseph has explicitly declined to rule on this ahead of the grader.** The grader must determine
which ONE of three things it is:

| | Determination | Escalates? |
|---|---|---|
| (a) | Within the **existing** selector contract — already admitted, merely made explicit | No |
| (b) | An **enlargement** of the admitted language, harmful or not | No |
| (c) | An **ambiguity** requiring a specification decision — the contract does not determine it | **Yes, to Joseph** |

These are materially different findings and must not be collapsed into "acceptable / not
acceptable".

**Binding constraint on method:** the verdict must rest on **measured positive and negative
controls**, not on the argument that bare `*` is broader. Reproducing that argument, however soundly,
does not discharge it. A negative control that cannot be made to fire is itself the finding, and it
points at (c). Controls enumerated from the grammar's own definition of a legal selector will confirm
the grammar — the standing hazard that a fixture derived from the rule cannot disagree with the rule.

### 12.2.1 RULED (Joseph, 2026-08-25): narrow to bare `*` or an exact literal

The grader returned **(c)** — an ambiguity requiring a specification decision — and it reached that
by controls rather than by the implementer's argument, which is what the constraint above was for.

**Ruling: selector syntax narrows to a bare `*` or an exact literal. Partial selector wildcards are
REFUSED.** The decisive control is that a partial can silently broaden one intended file to several,
and the present corpus pays **zero compatibility cost**.

The measurement, reproduced independently by this lane before relaying it:

    M-1[nd-unfolding/unified_throw_cov*].first_insert
      bad_pattern() -> None          ACCEPTED, no warning
      reaches 2 files: unified_throw_cov.py, unified_throw_cov_5d.py
      the literal form reaches 1

and the inconsistency is *internal to the guard*: it REFUSES `M-4.behin*`, which reaches exactly one
field today, printing that a wildcard "would whitelist more than one." It applies that reasoning in
field space and not in selector space. `unified_throw_cov.py` is the row whose omission **was** the
F-17(a) failure.

**This is a PROSPECTIVE specification decision.** It does not reinterpret the failed rehearsal as
having satisfied any clause, and it discharges nothing.

**Implementation route, mandatory:** the normal independent implementation-and-grade sequence — the
implementer and the grader are different parties, and neither is the spec author. **The
specification and its digest are updated ONLY AFTER the implementation passes**, not before. All
historical digests are preserved as as-of referents; none is rewritten.

Consequence for the note transcribed under §12.1: `m1m6_expected_differences.json` at `92091ae8`
currently describes partial selectors as accepted, because that is the **graded** behaviour and the
note is required to describe graded behaviour rather than intent. It is deliberately **left
unchanged** until the narrowing is implemented and passes, per this ruling. Its sentence deferring to
Joseph is therefore stale in wording while remaining correct in effect — do not add a partial
selector — and it is knowingly left so rather than edited early. §12.2.1 governs.

### 12.3 Scope, and what these do not move

The four newly identified fail-open spellings (`M-6[*`, `M-4.head*`, `M-3.*x`, `M-4.*e*`) and the
`M-4` overlap that `M-4.*e*` demonstrates fall **within the current repair's grading scope** rather
than constituting a separate finding.

**None of this changes the Gate-2 FAIL recorded in §1.** No new compute and no Gate-2 filing is
authorized by anything in this section, and a passing grade confers neither.


## 13. Withdrawn and non-citable: three mutation figures

**Ruled by Joseph, 2026-08-25.** The comparator-repair lane's claim 5 reported a mutation matrix.
Under independent grading, two figures reproduce exactly and three do not:

| Figure as claimed | Independently measured | Status |
|---|---|---|
| 16 arms RED on restoring the pristine guard | 16 — exact | reproduces |
| deleting the backstop reddens exactly its own arm | exact | reproduces |
| "across **5 methods**" | **6** | **WITHDRAWN, non-citable** |
| re-allowing a field-name wildcard reddens **4** | **1** (9 if the backstop is also removed) | **WITHDRAWN, non-citable** |
| reject-everything guard reddens **97** | **121** (111 fail + 10 error); two other placements give 151 and 117 — nothing yields 97 | **WITHDRAWN, non-citable** |

The direction of every row holds and **the repair's power is real and independently established**;
the grader's assessment is that the three were most likely taken against an intermediate tree and
never re-derived at the committed state.

**Ruled: do NOT dispatch another lane to recover these counts.** The reproducible controls already
establish the repair's relevant power and D-3's closure. Re-measure only if a later gate actually
depends on the mutation matrix. An inaccurate diagnostic count is not itself an audit campaign.

Also recorded from the same grade: claim 2's "breadth is inexpressible" is **overstated** — true of
field-name breadth, false of selector-space breadth (which is what §12.2.1 now closes). Claim 6 is
true but over a shipped-list population of **one** pattern, and must be quoted with that denominator.

## 14. F-14 self-reports: confession is not validation

**Ruled by Joseph, 2026-08-25**, in answer to a structural objection raised by the comparator-repair
lane: both lanes had produced a false compliance claim *inside a record whose purpose was to
establish compliance*, and in both cases the unmeasured belief was the one that excused its author.

**Ruling: independent authorship of an F-14 self-report is NOT required.** A party remains
responsible for filing its own omission — attribution belongs with the party that made it, and
outsourcing the confession would break that.

**But independent VERIFICATION is required before such a filing can discharge F-14 or support a gate
claim.** This separates confession from validation while preserving attribution.

Consequence, stated plainly: the two F-14 discipline records now on `main` are **filings, not
discharges**. Neither discharges F-14 and neither supports a gate claim until independently
verified. Nothing currently depends on them doing so.
