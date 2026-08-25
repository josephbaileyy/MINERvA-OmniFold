# GRADE 2026-08-25 — is `compare_m1_m6.py` fit to discharge F-17(b)'s "differences reported as findings"?

**CITABLE FOR:** the fitness of one instrument — `compare_m1_m6.py`, its whitelist
`m1m6_expected_differences.json`, and its suite `test_compare_m1_m6.py` — against the F-17(b) clause,
at the exact shas and digests named in §0. Seven findings, a 34-mutation power survey with each catch
attributed to a named arm, and an independent re-derivation of every rejection the builder made.

**NOT CITABLE FOR:** any F-number PASS or FAIL, any Gate-2 verdict, the far-end evidence, or authority
to grade. **This document records no F-number verdict and no gate verdict.** F-18(b) is a separate
fresh non-builder, later; §7.0.10 of the contract also makes a summary attesting "all controls passed"
a FAIL of F-18, and nothing here should be read as that summary. It grades an instrument. It authorizes
nothing, and it does not license submission, adoption, consumption, leg 6, or any member k≠0.

**Eligibility and disclosure.** Written by a lane that authored no part of the instrument, the
whitelist, the suite, the spec, or the k=0 plan, working read-only in an isolated worktree and writing
only this document and the three index artifacts a new `LIVE` document must move with. The lane that
*dispatched* this grade is the lane that wrote the spec and produces the F-17(b) evidence, and it
disclosed that; §9 records what I found in its spec and its briefing that was false or slanted.

---

## 0. WHAT WAS GRADED — pinned, because the target moved under me

The tip moved once during this work, and the grade moved with it.

| | sha |
|---|---|
| tip when I started | `a72e967ffc0773452222a24315d75b7666c4c3aa` |
| **tip graded** | **`2790ba904ae31bebd3f96d9a77cf95d0d8698e2e`** (`main`, and `origin/main` at the same sha) |

All three target files changed between those two commits (`2790ba90`, *"Drop M-4.ahead: its citation
recorded the opposite of the field"*, 272 insertions / 75 deletions over 4 files). Work done against
`a72e967f` — my first read of the whitelist and my independent reading of the cited M-4 block — was
re-run against `2790ba90` before anything below was written; no measurement below is carried forward
from the older sha. Where I state what the *older* file did, I name `a72e967f` or `74c25c3c` explicitly.

**Digests at the graded sha** (sha256, from the worktree at `2790ba90`, `git status --porcelain` empty):

| path | sha256 | lines |
|---|---|---|
| `docs/orchestration/compare_m1_m6.py` | `422ed9e7eaf16af6b6f110e480e0c7843c9612f3eb20ba08be60919a020bf430` | 782 |
| `docs/orchestration/m1m6_expected_differences.json` | `299c579968b67cbf165f962bf3671ab28784a7a128f7c79a923187ca0e158b20` | 48 |
| `docs/orchestration/test_compare_m1_m6.py` | `9b3ef0d4290743af848b1a98c7e4df23959baead8a6dda7c4bd8ccfbe609b48b` | 919 |
| `docs/orchestration/measure_m1_m6.py` (input instrument, not graded) | `0fcd90f7c92a7071208e62d09ebc38956f1a83b11af41a469b4886a6e6786d79` | 272 |
| `docs/orchestration/MEASUREMENT-20260822-m1-m6-at-pinned-sha.md` (the cited doc) | `458d540b5e3780732b4e766ecc66a9b47ff879826b87fd2a3c4c3f02ab331666` | 146 |
| `docs/orchestration/REVIEW-CONTRACT-20260822-k0-execution-integrity.md` (the clause) | `8b42260e3bbf69950331baeba0108e0246e6ede966d75d1c35bd78839000b378` | 1516 |
| `docs/orchestration/SPEC-20260825-f17b-tree-comparison-instrument.md` (not the standard) | `22b73175f90fdc423a49072c380ae0854f6f717a7e0d62f8d2025bd27025a06c` | 208 |

**Fixture discipline.** Everything was run against a full copy of `docs/orchestration/` at those exact
digests under `/tmp/f17b-grade/mut/docs/orchestration` (whole directory, so the arms that invoke
`measure_m1_m6.py` and the arm that resolves the shipped citation against a repo root both work), with
`TMPDIR` set explicitly, `PYTHONDONTWRITEBYTECODE=1`, and `__pycache__` purged between every
consecutive mutation. **Baseline confirmed green before any null result was believed: 53 tests, `OK`,
in both the real worktree and the fixture copy.** Nothing under `/pscratch` was read or written; no
rehearsal product was opened, quoted or consumed; the frozen deploy at `aa67c426` was not touched.

---

## 1. THE CLAUSE, QUOTED BY DIGEST WITH THE TREE NAMED

From `docs/orchestration/REVIEW-CONTRACT-20260822-k0-execution-integrity.md` **in this repository's
`main` at `2790ba90`, sha256 `8b42260e…`** — never "the contract", because the deployed tree at
`aa67c426` carries a superseded rubric with no §7.0 in it at all, and the far-end script itself prints
that occurrence count before quoting anything.

- **`:621`, the §7.0.5 F-17 split row.** Pre-submission half: *"M-1…M-6 re-measured on `MNV_CODE_ROOT`
  at the pinned sha **and** on the canonical checkout, at submission time; differences reported as
  findings"*. Post-rehearsal half: *"re-measured **again after the path runs**; M-2's inventory claim
  over the untracked set is the perishable one and is re-tested here"*.
- **`:1471`, the "Freshness" bullet.** *"F-17 M-1 through M-6 are **re-measured on `MNV_CODE_ROOT` at
  the pinned sha and on the canonical checkout as it stands at submission time**, and any difference
  from this document is reported as a finding. M-2 in particular is an inventory claim about 717
  untracked files and is the most perishable statement here; the authorized work is exactly what can
  falsify it, so it is re-measured **after** the path runs as well as before."*

**Two things the clause does and does not say, and they set the grading standard.**

1. The obligation is **reporting**, not judging: *any* difference *is reported as a finding*. The
   clause contains no concept of an expected difference and no whitelist. A whitelist is therefore not
   something the clause authorizes; it is a *deviation* from the clause that needs its own authority,
   entry by entry. The instrument's own docstring reaches the same conclusion in its own words
   (*"reporting is the obligation and suppression needs authority"*), which is the right reading, and
   it is why §3 grades the whitelist harder than the code.
2. The comparator is **"this document"** — the contract's own M-1…M-6 in §1 — *and* the two trees
   against each other. `compare_m1_m6.py` implements the second and cannot implement the first: the
   contract's §1 numbers are prose, not a `--json` document. That is not a defect of the instrument,
   but it bounds what a green run from it can discharge, and §3 G-5 makes that concrete.

---

## 2. VERDICT ON FITNESS

**As an instrument, it is a large and real improvement over what it replaces, and it is not yet
sufficient on its own to make F-17(b)'s "differences reported as findings" a machine statement.**

What it genuinely achieves, measured rather than read: it computes no measurement of its own (R1 holds
by inspection and by an arm that parses its own imports); it fails closed on every absence I could
manufacture; its exit vocabulary is disjoint and now *refuses to be importable* if collapsed; the
joint-not-pairwise semantics is real and is pinned by a fixture that a baseline-relative implementation
fails; M-2 is genuinely non-suppressible by two independent mechanisms; the record pins its operands by
digest; and every finding carries a unit and a population. Of 34 mutations I applied, 27 were caught by
at least one named arm, **all 27 behaviourally** — not one catch in my survey was attributable only to
the help-text arm, which is the specific hole previously reported here.

Three defects, each demonstrated end to end, still let a difference the clause obliges be reported as
`DIFFERENCES-ALL-EXPECTED` with the full suite green (G-1, G-2, G-3). One of them (G-3) is live in the
*shipped* configuration and needs no bad actor at all. And one wiring gap (G-5) means that at this sha
nothing in the repository's F-17(b) procedure invokes the instrument, so its existence has not yet
changed how F-17(b) would be discharged.

**Is the E1 class exhausted? No.** §5 answers that question and the guard-design question put to me.

---

## 3. FINDINGS

Each is stated as a signature you can re-run, not as a diagnosis. Severity is my judgement of the
consequence for the clause, not a gate score.

### G-1 (HIGH) — the arm that guards the shipped whitelist is blind in the M-1 direction, because it uses `fnmatch`

`test_the_shipped_list_does_NOT_whitelist_M1_M5_or_M6__the_rejected_bullet`
(`test_compare_m1_m6.py:524`) says in its own docstring *"FIRES if the rejected 'any commit to the
build branch' entry is ever added."* It does not, for the M-1 form of that entry. It matches patterns
with `fnmatch.fnmatchcase`, and M-1 field paths contain brackets:

```
field  = M-1[nd-unfolding/bootstrap_nd.py].literals
pattern= M-1[*].literals
fnmatch.fnmatchcase(field, pattern) -> False        # `[*]` is a CHARACTER CLASS matching one "*"
cm.field_matches(pattern, field)    -> True         # the instrument's own matcher
```

This is the exact bug `compare_m1_m6.py`'s `field_matches` docstring was written to record — *"THE
FIELD PATHS THEMSELVES CONTAIN BRACKETS … to `fnmatch` the pattern `M-1[*].first_insert` reads `[*]`
as a CHARACTER CLASS"* — re-introduced in the test that guards the whitelist. A rule retyped is a
second implementation of it; here the second implementation is the naive reading of the first.

**Demonstrated end to end.** Two documents differing only in `M-1[bootstrap_nd.py]`'s `literals`,
`first_insert`, `n_after` and `repo_modules_after`:

| expected list | exit | classification | findings |
|---|---|---|---|
| the shipped file (`299c5799…`) | **20** DIFFERENCES-SOME-UNEXPECTED | UNEXPECTED | 4 |
| the rejected bullet re-added as `M-1[*].…` patterns, each with its own resolving citation | **10** DIFFERENCES-ALL-EXPECTED | EXPECTED-BY-RULING | 4 suppressed |

and the full suite stays **green, 53 arms, `OK`**. The flat-field arms do work — re-adding
`M-4.ahead` as a flat pattern was caught by 4 arms, 2 of them behavioural — so the arm is not broken,
it is *one-directional in the wrong dimension*: it covers exactly the field spellings `fnmatch` can
express, and M-1 is one of the three populations the rejected bullet names.

**Fix that closes it and G-2 together, recommended not implemented:** replace the 12-name enumeration
with a covering control — take the field universe from a real `measure_m1_m6.py --json` document,
match it with `cm.field_matches`, and assert that the *only* suppressible field in the shipped list is
`M-4.behind`. That is an allow-list over a measured population instead of a deny-list over remembered
spellings, and it fails on any widening rather than on the widenings someone thought to type.

### G-2 (HIGH) — a citation of no informational content licenses a suppression, and no arm fires

The guard requires `quote.strip()` to be non-empty and the quote to be present in the cited document.
It requires nothing else of the quote. A **one-character** quote satisfies both.

Shipped file plus one entry whose four fields are each licensed by `{"quote": "a"}` against the real
cited measurement document:

```
SHIPPED  -> exit 20 | n_unexpected 4
1-CHAR   -> exit 10 | DIFFERENCES-ALL-EXPECTED | n_unexpected 0
             EXPECTED-BY-RULING M-3.all_intact      <- verify_hash_bindings went RED, suppressed
             EXPECTED-BY-RULING M-3.rc
             EXPECTED-BY-RULING M-4.modified
             EXPECTED-BY-RULING M-6.counts_resolutions   <- the guard's vacuity repair regressed, suppressed
suite with that list SHIPPED: rc = 0, OK
```

Note *which* fields: none of the four is in G-1's 12-name enumeration, so the shipped-list arm is
silent by construction. Adding a one-character-quote entry over `M-5.repo_assign` *is* caught — but
caught because the **field name** is on the deny-list, never because the quote is worthless. **No arm
in the suite examines a quote's substance at all.** The instrument's docstring is honest about this
(*"resolving is not SUPPORTING, and no mechanical check reads a quote's aboutness"*), and that honesty
is why this is a finding about coverage rather than about candour. See §6 for whether audit-after
suffices.

### G-3 (HIGH, and live in the shipped configuration) — a MISSING measurement is suppressible, and `field_set_differs` does not do what the docstring says it does

`compare_m1_m6.py`'s docstring states: *"two documents from different revisions of `measure_m1_m6.py`
cannot be told apart by this instrument. What it CAN see is that their field sets differ, and it
reports that (`field_set_differs`) as an unexpected finding — the F-17(a) failure was exactly an
instrument difference."* **That is false at this sha.** `field_set_differs` is a boolean in the record;
it is not a finding, it is not counted, and it does not reach the exit code. A field present in one
document and absent from the other becomes an ordinary finding whose value on one side is the sentinel
`<FIELD ABSENT FROM THIS DOCUMENT>` — and `evaluate_rule`'s `may-differ` arm returns `True`
unconditionally without looking at the values, so the whitelist suppresses it.

Measured, against the **shipped** whitelist, with two documents whose only difference is that one lacks
the `M-4.behind` key (precisely "two documents from different revisions"):

```
exit 10 | field_set_differs True | verdict DIFFERENCES-ALL-EXPECTED | n_unexpected 0
   EXPECTED-BY-RULING  M-4.behind  [5, '<FIELD ABSENT FROM THIS DOCUMENT>']
```

So the one shipped entry already suppresses *"this measurement is missing from one side"*, which is not
drift and is not what its citation licenses. This also undercuts the builder's stated ground for
deferring the input-schema fix — *"adding fields to it mid-rehearsal … this instrument would correctly
report that as a finding"* — in the direction of a **removed** field covered by the list. Two candidate
repairs, either sufficient: treat the `ABSENT` sentinel as never suppressible (the mechanism already
exists for M-2), or make `field_set_differs` force `EXIT_DIFFERENCES_SOME_UNEXPECTED`.

### G-4 (MEDIUM) — the `UNITS` class is not exhausted; three more claims are wrong or incomplete

The builder audited its own 30-row `UNITS` table and repaired 2 rows at `2790ba90`. I confirm both
repairs are correct at the lines they name (`measure_m1_m6.py:225` does require a colon as well as the
`"checked"` token; `:177` does drop blank lines before counting `dirty`/`untracked`/`modified`). An
independent pass over the other 28 finds three more:

1. **`M-6.state` has a FOURTH value, and on that branch it is not derived from what the entry says.**
   Declared: *"one of three named states, never a boolean"*, population *"derived from the two line
   sets above"*. `measure_m1_m6.py:221` returns `{"present": false, "state": "FILE ABSENT"}` when
   `mnv_guarded_run.py` is missing — no line sets exist on that path. Measured on a real tree:
   `M-6 = {"present": false, "state": "FILE ABSENT"}`. **The suite's own R7 fixture tree produces
   exactly this document**, so this is not a hypothetical, and a tree missing the guard is precisely a
   difference F-17 must surface.
2. **`M-1[*].literals`' declared unit describes the human print, not the compared value.** Declared
   *"rendered `name@line(form)`"* — that is `measure_m1_m6.py:260`, the non-`--json` path. The compared
   value is a sorted list of compact-JSON objects with **four** keys, `value` included:
   `["{\"form\":\"subpath\",\"line\":1,\"name\":\"_ND\",\"value\":\"/pscratch/…/nd-unfolding\"}"]`. Two
   trees agreeing on name, line and form but differing in `value` produce a delta the declared unit
   does not describe.
3. **`M-3.rc` and `M-3.all_intact` are not properties of the measured tree alone.** `m3()` runs
   `sys.executable` — the *measuring* interpreter — with `cwd` set to the tree. `M-2.python` carries an
   explicit *"NOT a property of the measured tree"* caveat; these two need the same one and lack it.
   This matters concretely: the F-17(a) filing was taken on CPython 3.11.14 on the cluster, and any
   local re-measurement is a different interpreter.

Also conditional presence is undeclared throughout: `M-3.rc`, `M-3.all_intact`, `M-4.head` and the
rest of `M-4`, and every `M-6` field but `present`/`state`, are **absent** rather than false when their
precondition fails, and `M-4.behind`/`ahead`/`upstream` are absent when the upstream ref does not
resolve. The "a field with no entry is reported UNDECLARED" mechanism does not help, because absence is
not a new field. Combined with G-3, an absent measurement is the weakest-guarded case in the design.

### G-5 (HIGH for fitness, not a code defect) — at this sha the instrument is not on the F-17(b) path, and the pre-submission column it would compare against is prose

Three measurements, all in-repo:

- `docs/orchestration/measure_k0_farend_f1b_f17b.sh` — the far-end measurement script, tracked — names
  `measure_m1_m6.py` twice and **never** `compare_m1_m6.py`, `--json`, or the whitelist. Its own
  deferred-defect block still carries item 1, *"the comparison of those two column sets is
  UNINSTRUMENTED — done by eye into a receipt, as F-17(a) did at 30ec0707"*, as open.
- **No `measure_m1_m6.py --json` document exists anywhere under `docs/`.** `grep -rl '"M-1"' docs/`
  returns exactly three files: the instrument, the measuring tool, and the suite.
- The filed F-17(a) both-trees half,
  `MEASUREMENT-20260823-m1-m6-at-the-candidate-and-canonical.md`, is **markdown tables** produced by
  the non-`--json` path, on CPython 3.11.14.

Consequence: `compare_m1_m6.py` requires two `--json` documents, and the pre-submission column of
record is not one. F-17(b) cannot be discharged by this instrument against the filed pre-submission
half without re-emitting that column — and re-running `measure_m1_m6.py` on the pinned sha *now* would
measure the tree as it is now, not as it stood at submission time, which is this campaign's named
defect. The clean route is to emit `--json` alongside the human table at **both** ends from here on and
to have the far-end script invoke the comparator and file its `--record`; the route to avoid is
back-filling the pre-submission column after the fact. **I could not determine whether `--json`
documents were filed cluster-side** — see §8.

### G-6 (LOW, but on the reviewable surface) — the whitelist's own notes commit the asymmetric comparison they exist to prevent

The shipped notes read: *"only 10 of the 46 commits in `8c156a37..build-k0-execution-integrity` touch
any file in those three populations **(2 of 10 M-1 files, 8 of 8 launchers, 3 for
`mnv_guarded_run.py`)**"*. The three figures in that parenthetical do not share a unit. By per-commit
enumeration (§4): **2 is a COMMIT count**, while **7 of the 10 M-1 files** were touched across those 2
commits. `8 of 8 launchers` happens to be true as both a commit count and a file count, which is what
makes the mixed parenthetical read as consistent. `compare_m1_m6.py`'s own docstring states the same
facts unambiguously (*"2 touch the ten M-1 files"*) and is correct; only the whitelist's notes — the
artifact a reviewer reads when deciding whether the rejection was sound — carry the ambiguity.

### G-7 (LOW) — five smaller uncovered behaviours, from the mutation survey

Each survived the full suite with zero failures.

| mutation | what is unpinned | consequence |
|---|---|---|
| `canon` returns lists unsorted | the documented *"a difference of order alone is not a difference of measurement"* | spurious findings (the safe direction), but the docstring's guarantee is untested |
| `entry["used"] = True` only when the rule is satisfied | the *used* direction of `expected_entries_unused` | a matched-but-unsatisfied entry reports as "matched nothing"; a one-directional check |
| a `citation` present but not an object | the type check | `AttributeError` → uncaught traceback → exit **1**, which the file itself reserves as *"never a verdict"*. Loud, not silent, but it is a refusal path with no arm |
| a whitespace-only quote | `quote.strip()` | with the check removed, `"   "` resolves in any document; see G-2 for why this class matters |
| `if pattern in MEASUREMENT_IDS` removed | nothing — **equivalent mutant** | a bare `M-4` is still refused by the next clause (`rest[0] not in ".["`). Recorded so the survivor count is not over-read |

---

## 4. THE REJECTIONS, RE-DERIVED

A rejection that reduces the rejecter's own work is the one to re-derive hardest. I re-derived all of
them from the artifacts, not from the spec or the briefing.

### R4's second bullet — REJECTION CORRECT, and the arithmetic is exact

The claim rejected: *"M-1, M-5 and P-6 are falsified by any commit to `build-k0-execution-integrity`."*
Re-measured by **per-commit** enumeration (`git show --name-only --format= <sha>` per commit,
intersected in Python against `measure_m1_m6.py`'s own `M1_FILES` and `LAUNCHERS` tuples), never by a
`rev-list <range> -- <paths>` pathspec:

```
range 8c156a37..build-k0-execution-integrity  ->  46 commits
tip 3bdda8cca5534eeaf7d90530598c18a30cfb2c9a ; merge-base(main, branch) = 8c156a374a00e024b9f28d575d38c75f345dcb3b
commits touching the ten M-1 files ........ 2
commits touching the eight M-5 launchers .. 8
commits touching nd-unfolding/mnv_guarded_run.py .. 3
commits touching ANY of the three ......... 10          =>  36 of 46 cannot move them
CONTROL (must be non-zero): commits touching docs/orchestration/ .. 33
```

Every figure the builder published matches. "Any commit" is false, and the second half of the
rejection is the stronger half and also correct: as a whitelist entry it would have suppressed M-1's
dropped tenth entrypoint and M-5's `0 of 8` against `8 of 8` — the two F-17(a) findings *against the
builder*. Refusing it therefore cost the builder rather than saved it. The `P-6`/`M-6` correction is
also right: `P-6` is not a measurement this tool emits. (See G-6 for the one unit slip in how the
numbers are written down.) The spec's own *"46 ahead of and 164 behind `origin/main`"* now measures
**46 ahead, 171 behind** — the spec predicted its own staleness there and told me to re-measure.

### R4's first bullet, and the `M-4.ahead` drop — CORRECT, and I read the citation before I was told

I read the cited block at `a72e967f`, before the builder's repair landed and before I was briefed on
it, and reached the same conclusion independently: `MEASUREMENT-20260822-m1-m6-at-pinned-sha.md:89-95`
is headed *"HOLDS on identity; the BEHIND-COUNT has moved twice"*, its drift paragraph is about the
behind-count, its expiry bullet names *"M-4's behind-count"* alone, and its only mention of ahead is
`ahead = 0 ; git merge-base --is-ancestor -> rc=0` — a **stable zero**, grouped with the ancestry check
as part of the identity that *holds*. The citation did not fail to support `M-4.ahead`; it recorded the
opposite of it.

I also grade the reasoning, not just the outcome, and I agree with it on its merits: `ahead` moves for
two distinct causes — the upstream absorbing that tree's commits (harmless) or that tree gaining a
commit no other tree has (a fork, which is exactly the drift F-17 exists to surface) — and a whitelist
may not swallow the second to spare a reviewer the first. The entry's own `why` already reasons that
way about `head` and `dirty` (*"those are the tree's identity"*), and `ahead` sits with them, not with
`behind`. The retained `M-4.behind` suppression is the one the citation earns: `36 → 55 → 65` with
`HEAD`, `dirty` and the `717/4` split unchanged **in the same block** is drift exhibited with the tree
held fixed.

Independently confirmed: the superseded entry from `74c25c3c` fed to the current instrument exits **5**
with *"a single 'citation' may license exactly ONE field pattern, and this entry names 2"*; and on real
inputs differing only in `M-4.ahead` the shipped list yields exit **20** with the finding UNEXPECTED.

### R5 — REJECTION-BY-REINTERPRETATION, CORRECT

R5 asked for a fixture of three trees "pairwise-consistent and jointly inconsistent". Under exact
equality that fixture cannot exist, because equality is an equivalence relation — so the spec's stated
control was unbuildable as written, and building it would have been fiction. The builder implemented
the *requirement* (joint distinct-value sets over all n; `global_agreement_inferred_from_pairs: false`)
and relocated the fixture to the only place the failure is expressible: a `max-abs-delta` tolerance
with values 3/0/6 and tolerance 4, where a baseline-relative pass sees nothing and the joint spread is
6. Verified powered: replacing the joint spread with a baseline-relative maximum is caught by
`test_pairwise_CONSISTENT_but_jointly_INCONSISTENT_does_not_get_a_global_agreement`.

### R3's "detached-or-branch" and R6's "wall-clock" — PARTIAL, CORRECTLY, and honestly disclosed

Confirmed against the producer: `measure_m1_m6.py`'s `main()` emits `label`, `tree`, `M-1`…`M-6` and
nothing else, and `m4()` returns `is_git, head, dirty, untracked, modified, behind, ahead, upstream`.
Neither a symbolic-ref state nor a timestamp is derivable from the input, and deriving them by running
git would both break R1 and answer about the tree *now* rather than as measured. Emitting
`UNAVAILABLE-BY-INPUT-SCHEMA` with the reason attached, plus `input_file_mtime_utc` explicitly labelled
a property of the *file*, is the right disposition and is pinned by an arm. One caveat: the stated
ground for deferring the schema fix leans on already-filed pre-submission documents that I cannot find
in the repository (G-5, §8), and G-3 shows the "we would correctly report it" half is false for a
*removed* field that the list covers.

### The refusal to build an F-7(b) instrument at all — CORRECT, on the clause, not on the spec

§7.0.9 of the contract (`8b42260e…`, `:685-695`) settles it without needing the spec: *"P-4 pins the
per-entrypoint import set as an identity taken from the first clean run. The k=0 rehearsal is that
first clean run, so it can only establish the pin … F-7's ratchet is never exercised inside this
contract's scope."* Disposition there is explicit — F-7(b) is discharged by *recording and committing*
the sets, and *"the reviewer must say in those words that the pin is recorded and untested."* An
instrument built for that would have nothing it could fail on. The spec's supporting claim also checks
out, with the tree named, which the spec did not name: `nd-unfolding/mnv_preflight_census.py`,
`nd-unfolding/mnv_preflight_exclusions.json` and `nd-unfolding/tests/test_k0_preflight_exclusion_census.py`
(**13** arms) exist on `build-k0-execution-integrity` at `3bdda8cc` and **none of the three exists on
`main`**.

---

## 5. IS THE E1 CLASS EXHAUSTED, AND SHOULD THE GUARD CHECK EACH FIELD SEPARATELY?

**The guard change is the right shape and it works in both directions.** One `citation` now licenses
exactly one pattern; a multi-field entry needs a `citations` mapping; a field with no citation, a
citation for an unclaimed field, both keys at once, an empty mapping, and a per-field citation that
does not resolve are all refused, and the refusal names the offending field and not the innocent one.
Mutating any of those five checks is caught. That is the correct answer to the question put to me:
yes, a multi-field entry's citation must be checkable against each field separately, and it now is.

**But the class is NOT exhausted, and the residual is the part the shape cannot reach.** The three
predicates are distinct: (a) the citation *resolves*; (b) the quote is *present*; (c) the cited section
*supports that entry's fields*. The guard decides (a) and (b) — and (b) only as a substring test over
the whole document, with no minimum substance, no section anchor, and a multi-line quote able to
resolve with `matched_lines == []`. Predicate (c) is unmechanised, is stated as unmechanised in both
the code and the whitelist notes, and **G-1 and G-2 show it is exploitable without a single arm
firing**: a resolving one-character quote suppresses `M-3.rc`, `M-3.all_intact`, `M-4.modified` and
`M-6.counts_resolutions`, and the rejected M-1 bullet re-added in wildcard form suppresses four M-1
fields, both at exit 10 with 53 arms green. G-3 adds a member the citation shape cannot see at all: a
`may-differ` rule suppresses a *missing* measurement, and the shipped entry already does.

So: the fix for the reported defect is correct and complete **for the defect as reported**. The class it
belongs to — *a whitelist entry suppressing a difference F-17(b) obliges to be reported, with no arm
firing* — has at least three further live members at this sha.

---

## 6. IS AUDIT-AFTER SUFFICIENT FOR THE ABOUTNESS GAP? — MY ANSWER: NOT AS THINGS STAND

The case for sufficiency is real: `--expected` has no default, the record pins
`expected_list.path`, `expected_list.sha256` and every citation's `doc_sha256_measured`, and the
shipped file's contents are pinned by arms. A substituted whitelist is therefore *recoverable* from the
record.

It is nonetheless insufficient today, for three reasons I measured rather than inferred.

1. **The after-the-fact audit is not obliged anywhere.** Detectability only becomes detection if some
   party is required to re-derive the whitelist's committed digest and compare it to
   `expected_list.sha256`. Neither the contract's F-17 row, the Freshness bullet, nor the far-end
   script imposes that; and the far-end script does not invoke the comparator at all (G-5), so there is
   no receipt for anyone to audit yet. **Cheapest sufficient repair: make it a stated obligation of the
   F-17(b) receipt** — quote the whitelist's path *and* committed sha256 beside the record's, and
   require the F-18(b) reviewer to re-derive it. That costs one line and needs no code.
2. **The behavioural pin is over a 12-name deny-list, not over the population.** G-1 and G-2 both walk
   straight through it, and neither needs a substituted file — a *committed* widening passes too. That
   is not an aboutness problem; it is a coverage problem, and it is fixable in code (see G-1's
   recommendation). Until it is fixed, "the protection is a behavioural pin on the shipped file" is
   weaker than it sounds, because the pin does not cover the shipped file's field universe.
3. **Prevention is available for part of it without breaking R1.** Refusing an `--expected` path that
   does not resolve inside `--repo` costs nothing and removes the whole "whitelist from `/tmp`" branch.
   I do *not* recommend requiring `doc_sha256` on every entry: the builder's stated reason for omitting
   it — the cited document is classed LIVE/open, so a pin would turn a peer's correction into a refusal
   at measurement time, the worst moment to be editing a whitelist — is sound, and the digest is
   recorded in the output either way.

One thing to keep in view: the aboutness gap is the *least* dangerous of the three, because it requires
someone to write a bad citation and a reviewer to not read it. G-1 requires no bad faith at all (the
guard arm simply does not see the pattern), and G-3 requires nobody at all.

---

## 7. THE MUTATION SURVEY — 34 mutations, and which arm caught each

Baseline 53/53 `OK` confirmed before and after the survey; caches purged between consecutive
mutations; every anchor asserted to occur exactly once before substitution, so no mutation silently
failed to apply. **27 caught by ≥1 named arm, all 27 behaviourally. 1 caught with zero arms. 6
survived (1 of the 6 an equivalent mutant).**

| # | mutation | outcome |
|---|---|---|
| M01 | `EXIT_DIFFERENCES_SOME_UNEXPECTED` 20 → 10 | **caught, ZERO arms** — `check_vocabulary` raises at import, so the suite cannot be collected (`rc=1`, `RuntimeError: exit vocabulary COLLAPSED`). Behavioural and fail-closed, but attributable to no arm; a reader must not mistake the collection crash for a broken harness |
| M02 | M-2 pattern ban removed | `test_M2_CANNOT_BE_WHITELISTED_at_all` |
| M03 | M-2 no longer forced UNEXPECTED | `test_M2_STAYS_UNEXPECTED_even_if_a_list_somehow_covers_it__the_second_mechanism` |
| M04 | quote presence not required | `…QUOTE_is_absent_is_a_hard_error`; `…citations_MAPPING_is_checked_in_BOTH_directions` |
| M05 | cited document existence not required | `…DOCUMENT_is_absent_is_a_hard_error`; `…refusal_NAMES_the_field_whose_citation_failed` |
| M06 | declared `doc_sha256` mismatch not refused | `test_a_DECLARED_DIGEST_that_no_longer_matches_is_a_hard_error` |
| M07 | one-citation-per-pattern removed | `test_ONE_QUOTE_MAY_NOT_LICENSE_A_FIELD_LIST__the_defect_in_the_shipped_entry` |
| M08/M09/M10 | `citations` missing field / extra field / both keys | `test_a_citations_MAPPING_is_checked_in_BOTH_directions` (all three) |
| M11 | trailing-wildcard pattern allowed | 3 arms incl. `…OVER_BROAD_pattern_is_refused…` |
| M12 | bare measurement id allowed | **survived — equivalent mutant** (still refused downstream) |
| M13 | `field_matches` narrowing broken | `test_a_PER_FILE_wildcard_is_still_allowed__the_narrowing_direction` |
| M14 | tolerance baseline-relative, not joint | `test_pairwise_CONSISTENT_but_jointly_INCONSISTENT…` |
| M15 | tolerance over non-numeric fails open | `test_a_tolerance_over_a_NON_NUMERIC_or_ABSENT_value_fails_closed` |
| M16/M17/M18/M19 | empty input / missing key / one input / absent list accepted | one arm each, all behavioural |
| M20 | findings never reach the some-unexpected code | **14 arms** |
| M21 | unit lookup always "declared" | `test_a_field_with_NO_DECLARED_UNIT_is_reported_as_undeclared_and_counted` |
| M22 | input sha256 not recorded | `…reconstruct_WHICH_files_were_compared`; `…pins_the_OPERAND_and_not_merely_its_PATH` |
| M23 | M-1 rows no longer keyed by file | `test_a_PER_FILE_wildcard_is_still_allowed…` |
| M24 | `canon` no longer order-insensitive | **survived** (G-7) |
| M25 | `used` set only when satisfied | **survived** (G-7) |
| M26 | vocabulary collision check disabled | `test_a_COLLISION_is_REPRESENTABLE_in_the_sequence_and_is_refused` |
| M27 | refusals return 0 | **17 arms** |
| M28 | non-dict `citation` accepted | **survived** — becomes an uncaught traceback, exit 1 (G-7) |
| M29 | expected-list schema unchecked | `test_a_malformed_list_is_refused_in_every_shape` |
| M30 | whitespace-only quote accepted | **survived** (G-7) |
| W01 | `M-4.ahead` re-added on `behind`'s citation (the old defect) | 4 arms, 2 behavioural |
| W02 | `M-4.ahead` re-added with its own resolving-but-about-behind citation | 2 arms, 1 behavioural |
| W03 | the rejected bullet re-added as `M-1[*]` patterns | **SURVIVED — G-1** |
| W04 | `M-5.repo_assign` whitelisted on a one-character quote | 1 arm — and it fired on the **field name**, not the quote (G-2) |

`test_every_code_is_documented_in_help` and `test_the_vocabulary_is_PINNED_to_literal_integers_and_names`
appear in **no** catch list, i.e. no result in this survey rests on a docstring or help-text arm.

---

## 8. WHAT I COULD NOT DETERMINE — read this before treating §2 as complete

1. **Whether `measure_m1_m6.py --json` documents were filed cluster-side.** None exists under `docs/`,
   and the filed pre-submission half is markdown (G-5). Whether the pre-submission `--json` column
   exists outside the repository I cannot say: reading `/pscratch` is prohibited for this lane and I
   did not attempt it. What would settle it: the far-end lane naming the path and digest of any filed
   `--json` document, or stating that none exists. G-5's consequence and the R3/R6 deferral premise
   both hang on this.
2. **Whether the instrument behaves the same on the cluster interpreter.** Everything above is CPython
   3.12.2 on macOS. `M-2.python`, `M-2.stdlib_collisions` and `M-3.rc`/`M-3.all_intact` are properties
   of the *measuring* interpreter (G-4), and the F-17(a) column was taken on 3.11.14. I did not run
   `compare_m1_m6.py` or its suite under 3.11, and I did not run either against real cluster documents.
   Predictable and worth flagging to the far-end lane: if the two ends use different interpreters,
   `M-2.python` differs, M-2 is non-suppressible by design, and the run **will** exit 20. That is
   correct behaviour, not a defect, but it must not be read as a substantive M-2 change.
3. **Whether `measure_m1_m6.py`'s M-1/M-2 population matches the contract's.** The contract's §1 method
   for M-1 and M-2 is *".py stems **plus directories carrying `__init__.py`**"*; `repo_modules()`
   globs `*.py` stems only and never consults a directory. If the two trees contain package
   directories, the re-measurement's population is narrower than the contract's, so a comparison
   against "this document" is between two different measurements. I did not measure whether any such
   directory exists in either tree, because one of them is the frozen deploy. This is a finding about
   the **input** instrument, which is outside what I was asked to grade, and I have not graded it.
4. **Whether any of G-1…G-7 is already known to the builder.** I did not ask, deliberately. G-1, G-2
   and G-3 are new to this document as far as the graded files, the spec and my briefing show.
5. **Anything about the far end, the rehearsal, F-1(b), or Gate 2.** Out of scope by construction and
   by the boundaries this lane was given. **This document records no F-number verdict.**

---

## 9. WHAT I FOUND FALSE OR SLANTED IN THE SPEC AND IN MY BRIEFING

Reported because the spec and the briefing both came from the lane that produces the F-17(b) evidence,
and both invited this.

- **`SPEC:§4 R4` second bullet — false as written**, in the direction that would have suppressed the
  builder's own adverse findings. Re-derived in §4: 10 of 46 commits, not "any". The spec flagged this
  bullet as the number it was most recently wrong about, and it was.
- **`SPEC:§4 R4`'s "46 ahead of and 164 behind"** — now 46 ahead, **171** behind. Self-flagged as
  perishable; recorded so nobody quotes 164.
- **`SPEC:§4 R5`'s control is unbuildable as written** — see §4. The spec asked for a fixture that
  cannot exist under exact equality, and named it "the control that would catch it being wrong".
- **`SPEC:§2`'s "the widening detector already exists" names no tree.** All three artifacts are on
  `build-k0-execution-integrity`, none on `main` — in a spec whose own §1 insists that "the contract"
  must never be an ambiguous referent. The substance of the claim holds.
- **Slant by omission in the spec, one instance and it is minor.** §1 quotes F-17(b) and §4 then frames
  the whitelist as a normal component with a failing arm. It never says that the clause contains **no**
  concept of an expected difference, so every entry is a deviation needing its own authority — the
  reading the builder arrived at independently and wrote into its own docstring. A spec from the
  evidence-producing lane that presents a suppression mechanism as the default shape is exactly the
  omission its own §0 warned me to look for. It is minor because §4's control statement
  (*"a whitelist with no failing arm is how a gate stops being able to fail"*) points the right way.
- **My briefing was accurate on every point I checked, and I checked the load-bearing ones.** The old
  entry exits 5 with the stated message; the shipped list yields exit 20 on an `M-4.ahead`-only
  difference; baseline was 53/53 before those nulls; and both new `UNITS` claims are correct at the
  lines named. The briefing also scoped two items to me as "still open" and both were real. Where I
  differ: it presents the aboutness gap as the residual, and G-1 and G-3 are larger residuals than
  aboutness — G-1 defeats the behavioural pin the briefing offers as the protection, and G-3 needs no
  actor at all.
- **The briefing's own framing of the `ahead` drop was correct and I concur on the merits**, having
  read the citation independently at `a72e967f` before being told. I record that ordering because
  "I agree with the lane that briefed me" is worth less than "I measured it first".

---

## 10. STATE AT COMPLETION

Re-fetched after all measurements: `origin/main` at `2790ba904ae31bebd3f96d9a77cf95d0d8698e2e`,
unchanged from the graded sha, and the three graded files' digests are the ones in §0. **This verdict
expires the moment any of those digests moves.** If you are reading it against a different digest, the
mutation survey in §7 and findings G-1…G-7 have not been re-taken.

No `OPEN_ITEMS.md` row was filed, deliberately: this lane holds no clear ten-block (the spec records
120–139 as exhausted, and a mis-allocated id is refused by a pre-commit hook), and `OPEN_ITEMS.md`
rows are digest-bound to `source-record-inventory.tsv`, which a live peer lane is editing. G-1 through
G-7 are routed here instead, and the builder and the F-18(b) reviewer are the parties who should read
them. G-1, G-2 and G-3 are repairable in the instrument and its suite; they are **not** disclosures,
and they should not be filed as such.
