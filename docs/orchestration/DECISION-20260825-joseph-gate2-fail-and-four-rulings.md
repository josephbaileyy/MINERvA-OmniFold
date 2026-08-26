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

### 10.1 A SEPARATE READINESS CHECK gates step 4 (Joseph, 2026-08-25)

Completing and grading any prospective mechanism — including the `verify_receipt_artifacts.py`
repair — **authorizes only that mechanism**. It is not a step toward permission and it accumulates
no credit.

**Do not start a rehearsal, file Gate-2 evidence, or launch compute without a separate readiness
check confirming that ALL prospective F-7(b), F-8(b) and F-17(b) mechanisms are present AND
independently graded.**

Stated as a gate rather than a habit because the failure it prevents is the one this campaign
already made: a sequence of individually-authorized steps read, at the end, as authorization for the
thing none of them authorized. The readiness check is a distinct act with its own evidence. A lane
that has just finished the last mechanism is not thereby cleared to proceed, and "all three are
done" asserted by the lane that built them is not the check.

### 10.2 The register is CLOSED for this pass (Joseph, 2026-08-25)

Once §§11.1.1, 12.4, 13.1--13.2, the corrected note and the `codex-school` dispatch land,
**the register is closed for this pass** and this lane returns to the **5D uncertainties**, which is
its actual assignment.

**Gate 2 remains FAIL and Joseph is holding it.** The third independent origin is the `codex-school`
implementation dispatched in
`DEFECT-20260825-generate-manifest-dirty-warning-nondiscriminating.md` §6, working **from
artifacts only**. That dispatch is **UNCLAIMED** — a handoff, not a delivery — so it is not yet an
origin of anything. Re-evaluation happens when it lands, **on its own evidence**, not on this lane's
agreement with an advisory lane, which is one origin counted twice. **No compute until then.**

**SUPERSEDING STATUS NOTE, 2026-08-26.** That dispatch was **CLAIMED in writing** on 2026-08-26 by the
`codex-school` Codex session (`DEFECT-20260825-generate-manifest-dirty-warning-nondiscriminating.md`
§6, which carries the attribution and the preserved history). **The UNCLAIMED sentence above is
retained as the state at the time of this ruling and is deliberately not rewritten**, so the ruling
and the fact it was made against remain readable together. **Nothing else in this paragraph moves:** a
claim is not a delivery, it is **not yet an origin of anything**, a third party must still grade any
delivery, Joseph alone re-evaluates Gate 2, and there is still **no compute until it lands.**

**SECOND SUPERSEDING NOTE, 2026-08-26 — THE THIRD ORIGIN NOW EXISTS AND IS GRADED.** The dispatch was
delivered and then graded by **two independent parties, neither of them the implementer nor this
lane**: `agy-publication-redteam` returned **FIT** on eight required items (turn 33, rc 0), and
`agy-g2-gate-verifier` returned **SUPPLEMENT PASS / grade COMPLETE** (turn 9, rc 0) after measuring
the broad suite at both shas under the mandated Python 3.11.14 — **431 tests, 3 failures + 3 errors,
identical in both directions, no regression.** Full closure, with the attempt history and every
digest, is `DEFECT-...-nondiscriminating.md` §8.

**The two sentences above are NOT rewritten.** "Not yet an origin of anything" was true when written
and is now superseded by measurement; both readings stay visible.

**What does NOT follow, and this is the operative half:** **Gate 2 remains FAIL and Joseph alone
re-evaluates it.** A complete instrument grade is an input to that re-evaluation, not a substitute for
it. No compute, rehearsal, adoption, F-14 discharge, or use of the `k0-aa67c426-20260824T145751Z`
products follows. The closure record lands on branch `closeout/dirty-warning-grade-20260826`;
**`main` is deliberately not moved and not merged**, and the routed control-plane views are
deliberately not republished, because doing so would take the merge and state-publication decision
ahead of the re-evaluation Joseph has reserved.

**DELEGATED GATE-2 RE-EVALUATION, 2026-08-26 — VERDICT: FAIL. BLOCK. The wording above is retained,
not rewritten.**

The phrase *"Joseph alone re-evaluates"* in the paragraphs above is **preserved as the state of the
authority at the time it was written**, and it is not edited. What changed is not that phrase's
accuracy then, but the authority now: **Joseph subsequently delegated, directly and to the
`codex-school` Codex session, any PASS or BLOCK decision** (and per-arm compute decisions only where
each arm is strictly under 500 GPU-hours and strictly under 500 CPU-hours). **That direct delegation
is the whole reason that session could re-evaluate Gate 2 without impersonating him.** The
re-evaluation below is that session's exercise of its own delegated authority; it is **not Joseph
speaking**, and no relayed peer message was treated as human authorization.

**VERDICT: Gate 2 remains FAIL, and the decision is BLOCK.**

**Basis, and note what the complete grade does and does not reach.** The complete independent
comparator grade closes the **third-origin / instrument question only.** The governing nine-clause
table still carries **six independently sufficient NOT DISCHARGED clauses**, each on its own enough to
defeat a PASS:

| clause | why it is not discharged |
|---|---|
| **F-2(b)** | no producer filing |
| **F-3(b)** | no producer filing |
| **F-5(b)** | no producer filing |
| **F-7(b)** | no rehearsal pin on a ref |
| **F-8(b)** | no run receipt |
| **F-17(b)** | its `:1471` half is **impossible for this rehearsal** and cannot be backfilled |

**Therefore no merge, no complete grade, and no inference can turn THIS rehearsal's Gate 2 into
PASS.** Six clauses would each have to be discharged on their own evidence, and three of them require
producer filings that do not exist while a fourth is impossible for this run by construction.

**This verdict is SUBSTANTIVE, not a cost-boundary referral.** It is not a decision deferred for want
of compute budget, and it is not a referral upward for want of authority — the authority was held and
was exercised. It is a finding on the merits of the clause table.

**It authorizes nothing.** No readiness check, no new rehearsal, no compute, no adoption, no F-14
discharge for any lane, no use or quoting of any product of run `k0-aa67c426-20260824T145751Z`, and no
scientific claim. `main` and the routed control-plane views remain unmoved and unrepublished.

**DELIVERY STATUS NOTE, 2026-08-26 — NOT A NEW RULING.** The assigned `codex-school` implementer
subsequently delivered the repair and its implementer controls in the commit carrying
`DEFECT-20260825-generate-manifest-dirty-warning-nondiscriminating.md` §7. The delivery is
**UNGRADED**. It therefore supplies neither the independent grade nor Gate-2 credit; the separate
third-party grade remains the next admissible action, and Joseph alone still re-evaluates Gate 2.
There is still **no compute, rehearsal, adoption, consumption, or quotation** authorized here.

**Where this lane goes next, corrected by Joseph 2026-08-26.** The assignment **remains publication
close-out**; "go back to the 5D uncertainties" was imprecise, not a change of lane. After the Gate-2
freeze receipt lands, the route is: **re-read a fresh `LIVE-STATE.md` and the governing `OI-*`, then
resume the node that is actually routed there** — not an assumed workstream. If the adopted scalar-5D
covariance is still the critical path, continue **that exact adoption gate**; do **not** reopen
completed or broadly scoped 5D uncertainty work.

**The `MANIFEST` classification finding is an OPEN REFERRAL and is explicitly NON-BLOCKING.** Not
overriding another lane's classifications was correct, and this lane does not adopt the referral as
its own work. It blocks nothing here **unless the routed publication gate explicitly depends on it**,
which must be established by reading that gate rather than assumed either way.

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
| `m1m6_expected_differences.json` (**intermediate**: transcribed from the D-3 grade) | content sha256 | `92091ae8` |
| `m1m6_expected_differences.json` (**intermediate**: transcribed from the narrowing grade) | content sha256 | `c2f0d920` |
| `m1m6_expected_differences.json` (**current**: §12.4's strike applied to the `notes` array only) | content sha256 | `2e5f3d52` |
| `compare_m1_m6.py` (narrowed at `63262a3a`, graded FIT at `fba7da70`) | content sha256 | `5dc92487` |
| `test_compare_m1_m6.py` (same) | content sha256 | `762fac14` |
| `measure_k0_farend_f1b_f17b.sh` (post-repair) | content sha256 | `c40e6b54`, 15722 bytes |
| `GRADE-20260825-f17b-comparison-instrument-fitness.md` (EXPIRED) | content sha256 | `aa1b6eee`, 41819 bytes |

Commits: `a3ed8631` producer filing · `30ede740` first bracket attempt · `38a7b16b` D-A and D-B
repairs · `a3000487` grader verdict · `a0d0e5a1` second-pass manifest regeneration.

Run: `/pscratch/sd/j/josephrb/k0r2/runs/k0-aa67c426-20260824T145751Z`, submitted
2026-08-24T07:58:01, seven jobs `57527866 57527869 57527870 57527872 57527873 57527874 57527875`,
all terminal, 1122 accounting rows `COMPLETED 0:0`, 374 guard inventories.

Frozen deploy tree: `/pscratch/sd/j/josephrb/k0r2/clean` at
`aa67c426afaa9b6ca91c9996637a6bade950da9a`, detached, `listing_sha256 fa3489e2...` — note that
`listing_sha256` is a **field of the manifest**, not the manifest file's own digest, which is
`622ddc0a`.

**The file count is 782 SOURCE files, and the population matters.** An earlier version of this
paragraph said "782 tracked files" with no population named, which is the same defect this paragraph
corrects for digests and D-C records for "233 behind main" — a bare count with no right-hand side.
Raised by the comparator-repair lane, which measured `git ls-files` on that tree, got **1583**, and
correctly declined to call the ruling wrong without knowing the population. Measured:

| population | count |
|---|---|
| `git ls-files`, all | 1583 |
| **`git ls-files` filtered to `*.py` or `*.sh`** | **782** |
| `git ls-files -- docs` | 543 |

782 is the middle row. It is `mnv_source_manifest.py`'s definition of a *source* file
(`SOURCE_SUFFIXES = (".py", ".sh")`, applied to `git ls-files`), confirmed independently by the
baseline manifest's own fields: `file_count: 782`, `suffixes: ['.py', '.sh']`. A grader reaching for
the obvious instrument gets 1583 and would conclude this document is in error.

**On the frozen tree's cleanliness — the evidence is the far-end run, not a later re-check.**
`porcelain=0` is F-1(b) clause (b) as measured by
`measure_k0_farend_f1b_f17b.sh` during the run that produced the filed record. A *separate* re-check
attempted at 19:25 on 2026-08-25 **never completed** — `git status` on that Lustre tree exceeds nine
minutes — and left a 0-byte output file, which this lane briefly read as a clean result. It is not
one: an empty file from a killed job is an absent answer. The same trap caught the comparator-repair
lane independently, in the same shared scratchpad. Cheap bounded evidence that does hold, measured
2026-08-25: `.git/HEAD` = `aa67c426`, `.git/index` unwritten since 2026-08-24 04:36:13, zero `.git`
lock files, working-copy mode `dr-xr-x---`.

A second attempt, this one carrying a COMPLETION SENTINEL, also had not finished at the time of
writing. **The sentinel is the point:** without it a 0-byte output file is indistinguishable from a
clean result, and that is the form the earlier error took.

### 11.1 THE FREEZE DOES NOT COVER `.git`, and that is measured

Raised by the selector-narrowing lane, which observed a `.git` mtime it had not caused and declined
to call it benign. Reconciled here because the frozen-deploy route belongs to this lane.

**Permissions, measured 2026-08-25:**

| path | mode | consequence |
|---|---|---|
| working-copy root | `dr-xr-x---` | file edits BLOCKED |
| `.git` | **`drwxrwx---`** | **HEAD, refs and objects are WRITABLE** |
| `.git/objects`, `.git/refs` | `drwxrwx---` | same |

So §7.0.19's freeze is enforced by permissions **on the working copy only**. A `git update-ref`,
`git fetch`, `git gc` or `git checkout --detach` would not be stopped by the mode bits. Immutability
of the pinned state rests on convention plus *partial* permissions, not on permissions alone — a
weaker basis than "it is read-only" suggests, which is what this document had been saying.

**Nothing actually changed, and that is also measured.** The `.git` *directory* mtime is
2026-08-25 18:32:35, but no entry inside it is newer than 2026-08-24: `HEAD` content `aa67c426`
(mtime 08-24 04:34:10), `packed-refs` / `objects/` / `config` at 08-24 05:07:34, `index` at
08-24 04:36:13, `refs/` and `logs/` at 08-22, and the reflog's last entry is the original 08-24
checkout to `aa67c426`. A directory mtime moves when an entry is created or removed, so this fits a
transient `index.lock` written and removed by a `git` read that then died — and there were at least
two such reads against this deploy copy today, from two different lanes.

**The consequence worth carrying: inspecting the frozen deploy with `git` is not a read-only act.**
Any git invocation there may write a lock into `.git`. Our own diagnostics are the most likely author
of the mtime we then had to investigate.

**F-1(b) is NOT disturbed.** HEAD is the pinned sha, and the source manifest was measured IDENTICAL
during the run that produced the filed record. What weakened is the confidence available *from the
mode bits*, not the state of the artifact. Whether to `chmod` `.git` read-only is a decision for
Joseph, not a silent repair to a frozen artifact.

#### 11.1.1 RULED (Joseph, 2026-08-25): do NOT `chmod` `.git`. Produce a bundle receipt instead.

**Ruling: do not `chmod` `.git` read-only, and revert it if it was applied. Verified NOT applied** --
`/pscratch/sd/j/josephrb/k0r2/clean/.git` measured `drwxrwx---` on 2026-08-25 *after* the ruling,
i.e. unchanged from the table above, so there is nothing to revert.

Two reasons, in the order Joseph gave them:

1. **It is an accident guard the tree owner undoes in one command**, so it is not a control. It
   raises the cost of an accident and does nothing against a decision.
2. **It breaks `git worktree add`, which is this repo's MANDATED mechanism for audit and review
   work** (`CLAUDE.md`: audit and review work is read-only and uses an isolated worktree). A guard
   that disables the audit path costs more than the accident it prevents.

The second reason was **not** in this lane's framing, which had scored the chmod "technically safe"
on the strength of this measurement: on an equivalent read-only replica, all twelve read paths F-1(b)
uses returned rc=0 with no index write, all write paths failed rc=128, and `clone` / `archive` /
`bundle` survived -- **`worktree add` was the ONLY thing that broke.** This lane reported that as a
narrow exception. It is the load-bearing case, and reporting it as an exception is how a measurement
that contained the answer got relayed as a clearance.

**What is ordered instead: a `git bundle` plus a recorded `sha256`.** The property the freeze actually
lacks is **detectability**, not resistance -- nothing currently distinguishes "the pinned state is
intact" from "nobody has looked". A bundle with a recorded digest is inspectable by someone who was
not there, and it fails loudly rather than silently. Filed as a `state/` receipt.

#### 11.1.2 LANDED 2026-08-26 — the receipt, and the postcondition that nearly did not fire

`docs/orchestration/state/RECEIPT-20260826-k0-freeze-bundle-detectability.json`. Bundle
`k0-clean-aa67c426-20260826T075536Z.bundle`, **79 140 251 bytes**, sha256
**`8ce58391…22c0`**. Measured at emission: frozen HEAD **= the pin**, ref set **= exactly the ten
`refs/tags/evidence/*` rows and nothing else**, and `.git` still **`drwxrwx---`** — the chmod was not
applied, re-measured rather than assumed.

**Recovery is TESTED, not asserted.** `git clone --no-local` from the bundle (which forbids object
sharing, so the bundle is the only source) → `fsck` rc=0 → checkout of the pin: HEAD
`aa67c426…`, tree `60120bfb…`, **porcelain 0**, 1583 tracked files. The receipt also states this
arm's honest limit: the recovered tree matching the primary checkout's `aa67c426^{tree}` is the *same
git object*, so it is not independent — what the arm establishes is that the bundle **alone**
rebuilds a clean checkout at the pin.

**The postcondition Joseph required is the reason this receipt is worth anything.** A `git bundle
create --all` would have **passed `verify`, produced a digest, and contained nothing to recover**:
that clone has **no branch and no remote-tracking refs**, so `--all` expands to the ten evidence tags
alone, and `merge-base --is-ancestor aa67c426 <tag>` is **FALSE for all ten**. The first attempt was
built that way and was discarded. The pin is now named **explicitly** through a local-only tag
`refs/tags/freeze/k0-aa67c426`, and `bundle list-heads` is asserted to contain it before any receipt
is emitted. `bundle verify` does **not** cover this: it checks well-formedness and prerequisites, not
that the bundle holds what you meant.

**Stated limitation, because it changes what the receipt can be cited for.** The bundle was generated
from the **primary checkout**, not from the frozen clone's own object store, because `bundle create`
there did not complete in **45 minutes** and had to be killed while the primary produced it in
seconds. So this is a recovery source for the pinned **commit and ref set**, not a byte-image of that
clone. Detectability of the pinned state rests on HEAD + ref set + commit content, and all three are
recorded.

**CORRECTION 2026-08-26 — I named the wrong mechanism for that slowness, in a receipt I had already
committed.** This section and the receipt said the frozen store is **loose-object on Lustre**.
Measured once Lustre quietened: `.git` is **2.7 GiB**, of which **2.598 GiB is 19 `.pack` files**,
against **1850** loose objects. The store is **almost entirely PACKED.** The real reason
`bundle create` crawled is that it had to read and re-pack 2.598 GiB across 19 packs over Lustre —
roughly **33×** the primary's single 80.81 MiB pack. My error was reading *`ls .git/objects` returns
the 00/01/02… fanout directories* as *the store is loose*: **directory presence is not a count**, and
the byte accounting settles it the other way. It matters because the wrong mechanism prescribes the
wrong lever — someone would run `gc` to pack objects that are already packed. Left visible rather
than overwritten, per the register's own rule.

**Two facts measured in the same pass, both recorded in the receipt.** The frozen working copy's
`git status --porcelain` finally returned: **rc=0, 0 lines** — the same measurement whose earlier
claim was retracted at `8f80050c` because that invocation had been *killed* and its 0-byte output was
an absent answer. The retraction stands; the claim was unfounded when made and this does not make it
founded in retrospect. And the two discarded `bundle create` runs left **no `tmp_pack_*`, no `.lock`,
no debris** in the frozen `.git` — checked because inspecting that clone with `git` is not a
read-only act.

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

**DISCHARGED.** Implemented at `63262a3a` by an independent lane, graded **FIT with NO condition**
at `fba7da70` by a third. The prior grade's mechanical expiry tripped by design (two of its three
pinned digests moved) and was verified tripped rather than assumed. The prior grade's standing
precondition — "no partial M-1 selector in the list at filing time" — is now **unnecessary**: the
guard makes one unrepresentable.

The note was then updated per §12.1's first branch, `92091ae8` → **`c2f0d920`**, transcribed from §8
of the narrowing grade and verified inert to behaviour (parses; comparator still returns the filed
`32/0/32` at exit 20; suite 81/81). Both earlier digests are preserved in §11 as as-of referents.

**Moved once more by §12.4's strike, `c2f0d920` → `2e5f3d52`.** Inertness re-established more sharply
than by re-running: `schema` and `entries` are **structurally equal** across the change and only
`notes` moved (103 → 109 strings), and `compare_m1_m6.py` contains **zero** occurrences of `notes`
against **6** of `"entries"` — so the edited region is not on any code path, rather than merely
having produced the same answer once. Suite re-run in a clean detached worktree: **81/81**.

**Newly accepted = 0**, independently measured over 115160 corpus-derived patterns scored in separate
processes against one serialized population: accepted 42997 → 773, with
`accepted_new \ accepted_old` empty. That was the column that had to be empty.

### 12.3 Scope, and what these do not move

The four newly identified fail-open spellings (`M-6[*`, `M-4.head*`, `M-3.*x`, `M-4.*e*`) and the
`M-4` overlap that `M-4.*e*` demonstrates fall **within the current repair's grading scope** rather
than constituting a separate finding.

**None of this changes the Gate-2 FAIL recorded in §1.** No new compute and no Gate-2 filing is
authorized by anything in this section, and a passing grade confers neither.

### 12.4 RULED (Joseph, 2026-08-25): the dead literal stays. NO CHANGE.

The question put to Joseph: a literal naming a file or field that does not exist is **accepted** by
`bad_pattern` and reaches nothing, so a reviewer now told to "name the exact file" can typo one and
get a whitelist row that reads as live cover. Should that be a refusal rather than a report?

**Ruling: no change.** The failure is **fail-closed under-coverage, in the direction OPPOSITE to
D-3**, and it does not justify a repair that has no correct form.

Measured -- and this is the measurement the framing that reached Joseph had omitted: a typo'd row
**suppresses nothing.** With `M-4.behin` whitelisted while `M-4.behind` genuinely differs, the
comparator still exits **20, UNEXPECTED**; the finding is reported, not swallowed. A dead row
under-covers and can never over-cover. D-3's fail-open let a real difference through unreported; this
lets a real difference be reported while its excuse sits unused. Opposite directions, and only the
first is a hazard to a gate. Supporting: `expected_entries_unused` reaches neither the exit code nor
the verdict, so promoting it is a new failure mode, not a stricter reading of an existing one.

**STRUCK, as unsatisfiable:** the middle option this lane proposed -- *"an unused expected entry must
force a non-zero exit"*. A **correct** entry is unused whenever the two documents agree, which is the
outcome the instrument exists to certify, so the rule fails the all-agree case. Recorded here struck
rather than omitted, because it is the obvious repair and the next lane will propose it.

**STRUCK, as a population/qualifier conflation:** the figure **"517 of the 773"** accepted patterns
being dead literals -- at `GRADE-20260825-selector-narrowing-fitness.md:456` and transcribed from
there into `m1m6_expected_differences.json`. That ratio is a property of a **generator emitting every
prefix of every path**, not of anything a reviewer types; the shipped list contains **one** live
pattern. Leaving it in the record invites exactly the conflation that produced the retracted
§13.2. The note is corrected in the same commit as this section. The grade is another lane's
artifact and is **NOT CITABLE for that figure**; this lane records the strike rather than editing a
filed grade it did not author.

**OWED AND UNDELIVERED — recorded as an open obligation, not as a discharged one.** The narrowing
grade also needs its §9 corrected (the retracted 265 claim, §13.2 here). Its author is **not a live
session** — `ListAgents` on 2026-08-25 and again on 2026-08-26 reported no reachable peer — so **no
notification was sent and none is queued.** The correction exists here and in §13.2 and nowhere in
the grade itself. **Anyone reading that grade directly will not see it.** The grade's overall verdict
(FIT, no condition) is unaffected by either strike; this obligation closes when its author, or a
party that adopts the artifact, records the correction in the grade.


## 13. Withdrawn and non-citable: three mutation figures

> **Scope of authority in this section.** §13 proper is **Joseph's ruling 2** and covers exactly the
> three mutation figures below. §§13.1–13.3 are **findings by the publication close-out lane**, not
> rulings, and were nested under a "Ruled by Joseph" heading — which is itself a defect this section
> now corrects, because it lent his authority to my findings. One of them, §13.2, was wrong.

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

### 13.1 The narrowing grade's four overstatements, recorded compactly

Per ruling 2's principle — an inaccurate diagnostic count is not an audit campaign — these are
recorded and not chased. **None is behavioural**; the narrowing's own verdict is FIT with no
condition.

| Claim | Status |
|---|---|
| "4060 of **4840**" | the 4840 denominator is **not recoverable** from committed artifacts. Cite `4060`, or the grader's 115160. Never "4060 of 4840". |
| `field_matches` untouched because narrowing it would cost unit assignment | **wrong ground.** 0 of 30 UNITS patterns is a partial selector, so mirroring the narrowing there would cost nothing. The correct reason is **backstop independence**: `field_matches` is the independent second implementation that `matcher_disagreement` interrogates, and teaching it the grammar makes the backstop circular. |
| "prose corrected in three places" | **four** |
| the `over_broad` assertion demonstrating the old sweep could not catch this | **degenerate as written** — it passes on the bench universe because the pattern reaches 0 fields there, not because the predicate counts field names. The substance holds over the real universe; the cited line does not carry it. |

| the new invariant arm's docstring | **states the opposite of the claim it supports.** It frames the narrowing's point as a *reach* property — "an accepted M-1 entry covers either one nameable file or, visibly, the whole population" — but `M-1[nd-*]` **satisfies** that (reaches 10 of 10), so the arm advertised as catching under-refusal residue would not have caught the very spelling §12.2.1 banned. Verified at `test_compare_m1_m6.py:957-982`: the assertion is `len(reached) <= 1 or reached == everything`. Coverage survives via the separate 4060-candidate sweep. **Prose defect, not behaviour.** |

Also: "all 76 pre-existing arms stay green" — there are **75** name-identical pre-existing arms; the
76th is the one the implementation inverted.

**Both prose corrections are now recorded here rather than edited into the file.** Editing either
moves a pinned digest and voids the live grade; recording them moves nothing. They are **mandatory on
next touch** — the next commit that moves `test_compare_m1_m6.py` for a behavioural reason must carry
them. The `field_matches` correction (row 2 above) was already recorded when this table was written;
the invariant-arm row closes the asymmetry, which was the actual gap.

### 13.2 RETRACTED — the "265 of 721" figure is CORRECT, and this section was wrong

**This finding is withdrawn. It was mine, it was wrong, and it was wrong in the direction that
discredited a correct prior grade.**

What this section previously said: that `test_compare_m1_m6.py`'s docstring figure "265 of 721
generated candidates are refused although they reach exactly one field name" does not reproduce, that
the measured values are 301 or 360, that **265 is the ACCEPTED count**, and that the figure "survived
the D-3 grade unchallenged". It instructed: *do not cite "265 of 721"*.

**Re-derived independently, twice** — by a fresh advisory lane and then by this lane with its own
probe, both over the suite's own `_candidate_patterns` on the bench universe:

| population | count |
|---|---|
| generator candidates | 721 |
| accepted | **265** |
| refused | 456 |
| refused ∧ exactly one field **name** | 301 |
| **refused ∧ one field name ∧ touches no `M-2`** | **265** |
| refused ∧ not `over_broad` | 360 |

**265 reproduces exactly** under the third reading, and the 36-pattern gap from 301 is entirely
`M-2`-targeted (`M-2.i*`, `M-2.im*`, …). Excluding them is substantively right for the claim the arm
makes: those 36 would be refused by the `M-2` rule regardless, so counting them as cost-of-the-
field-wildcard-rule double-counts.

**The D-3 grade graded this figure and AFFIRMED it** (`GRADE-20260825-d3-comparator-repair-fitness.md`
line 253, which states the qualifier and the 456 and the 301). So "survived unchallenged" was false:
it was tested and upheld. The narrowing grade's §9 tried two readings, missed the third, did not
consult the prior grade's claim-6 section where it is written out, and concluded from the
**coincidence** that `accepted` is also 265 (456 + 265 = 721) that 265 "is instead the accepted
count." Both halves of that sentence are individually true and the inference is wrong.

**The docstring's real defect is a MISSING QUALIFIER, not a wrong number.** Adding "and touch no
`M-2` field" makes it exactly true at both `68b4af12` and `5dc92487`. That correction is recorded in
§13.1's mandatory-on-next-touch set, not applied here.

**Still to be corrected elsewhere:** `CATALOG.md` echoes the retracted instruction, and the narrowing
grade's §9 stands uncorrected in a filed grade whose overall verdict (FIT) is unaffected. The grade
is its author's artifact; this lane has notified it rather than editing it.

**How I got it wrong, since that is the reusable part.** I received "cannot reproduce under either
natural reading" from a grader and relayed it into a ruling section without asking *which two
readings*, or checking whether an earlier grade had already scored the same figure. A negative result
about a figure is a claim about a **population and its qualifiers**, and I recorded it as a claim
about a number. That is the campaign's most-repeated failure mode and I committed it while
maintaining the register that documents it.

**The narrow rule worth keeping**, which is cheaper than "grades should check every figure": a figure
quoted in a docstring **must name its population and qualifiers inline**, and a grade that touches a
figure **must state the reading it scored**. Both graders here did correct arithmetic over
differently-defined sets; no amount of "check more" would have caught that, and stating the reading
would have caught it immediately.

**ADOPTED (Joseph, 2026-08-25), and it fixes the relay rather than the figure.** A negative result --
"cannot reproduce" -- is **not admissible as input to a ruling section** unless it carries (a) the
readings tried, **verbatim**, and (b) the result of a **search for prior grades touching the same
figure**. The rule above fixes the figure and the grade; this one fixes the step where it actually
broke, which was the relay. Both are in force.

### 13.3 My own briefing was self-contradictory, and the grader caught it

Two defects in how I briefed the narrowing grader, both reported by the grader itself:

- I relayed the implementer's claim 8 as "**nothing previously refused changes even its printed
  reason**". That is **false as stated** — and my own relay of claim 1, three paragraphs earlier in
  the same brief, said 305 verdicts were *reworded*. The two cannot both hold and I passed both
  without noticing. The defensible claim is about the **identity of the check that fires**, not its
  text; graded that way it holds exactly (one transition, `ACCEPT → partial-selector`, 42224).
- I asked the grader to "**assess whether the implementation is honest** about that". That is an
  attitude question and it invites a yes. Testing the same thing as a *proposition* is what produced
  the finding that the new invariant arm's docstring states the opposite of the claim it supports.

Recorded because the fix is to the briefing, not to anyone's code, and an unrecorded briefing defect
propagates to the next lane silently. **Rule for future dispatches: relay a claim as a proposition
with its operand, never as a question about the author's candour, and check a relayed claim set for
internal contradiction before sending it.**

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
