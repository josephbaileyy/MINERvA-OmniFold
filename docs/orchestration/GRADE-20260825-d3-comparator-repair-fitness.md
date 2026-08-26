# GRADE 2026-08-25 — is the D-3 repair of `compare_m1_m6.py` fit to support a future Gate-2 filing?

Author: independent grading lane. I authored no part of the instrument, its spec, its suite, its
whitelist, or the far-end evidence, and I repaired nothing. Under ruling 3 of
`DECISION-20260825-joseph-gate2-fail-and-four-rulings.md` I am the third party: spec author ≠
implementer ≠ grader.

## CITABLE FOR

- The fitness of **one instrument** — `docs/orchestration/compare_m1_m6.py` at content sha256
  `68b4af12` and `docs/orchestration/test_compare_m1_m6.py` at `b355ecdc`, both as repaired in
  `c8a29082` — against the defect it was assigned, **D-3**.
- The disposition of each of the implementer's seven claims, with the measurement beside it.
- **The ruling on partial wildcards in the `M-1` selector: (c), an ambiguity requiring a
  specification decision. It ESCALATES to Joseph and is not settled here.**
- The exact accepted and rejected pattern shapes, enumerated by running the guard (§7), which is
  the table the `m1m6_expected_differences.json` prose note may be written from.
- Three figures in the implementer's own mutation matrix that **do not reproduce** (§5).

## NOT CITABLE FOR

- **Any Gate-2 clause, F-number, or gate verdict. Gate 2 remains FAIL and open**, and nothing here
  changes that. This document grades an instrument; it discharges nothing.
- Authority to file, submit, adopt, consume, or quote any product of run
  `k0-aa67c426-20260824T145751Z`. That prohibition is untouched.
- Compute of any kind. None was authorized and none was used — **no Slurm job was submitted.**
- Leg 6, any member k≠0, family or undeclared-member adoption.
- The correctness of `measure_m1_m6.py`, the far-end script, the shipped whitelist's *content*, or
  any physics claim. Only the comparator's pattern guard was graded.
- **Selector-space breadth being closed. It is not** (§7). The verdict below is conditional on a
  precondition that is satisfied today and must be re-checked at filing time.

---

## 0. WHAT WAS GRADED, AND HOW I KNOW IT DID NOT MOVE

All work in a detached worktree at `47ad509d`, `git status --porcelain` empty, plus a full copy of
`docs/orchestration/` (229 files) under an explicit `TMPDIR`, `PYTHONDONTWRITEBYTECODE=1`, and
`__pycache__` purged between every mutation. Interpreter
`/global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3`.

| path | field | value |
|---|---|---|
| `docs/orchestration/compare_m1_m6.py` | content sha256 | `68b4af12…`, 63557 bytes |
| `docs/orchestration/test_compare_m1_m6.py` | content sha256 | `b355ecdc…`, 82143 bytes |
| `docs/orchestration/measure_m1_m6.py` (input instrument, not graded) | content sha256 | `0fcd90f7…` |
| `docs/orchestration/m1m6_expected_differences.json` (population, not graded) | content sha256 | `56c2e0ef…` |
| `docs/orchestration/state/f17b-k0-aa67c426-20260824T145751Z.json` (read-only) | content sha256 | `9109f371…`, 53226 bytes |

`bace69d2` is a **content sha256, not a rev.** The pre-repair blob is `compare_m1_m6.py` at commit
`dce8e8cc` = `c8a29082^`; I verified `git show dce8e8cc:…` hashes to `bace69d2`. Every "PRE"
measurement below was taken against that blob, executed, not read.

**The target did not move under me.** `HEAD` advanced from `47ad509d` to `34c16f16` during this
grade as peer lanes committed, but both instrument files are still `68b4af12` / `b355ecdc` and
`git log -1 --` on the pair still returns `c8a29082`.

**Prohibitions honoured.** The filed record was opened read-only and re-hashed afterwards:
`9109f371`, 53226 bytes, byte-identical, and `git status --porcelain docs/orchestration/state/`
is empty. I used only its *field names*, never its values. `/pscratch/sd/j/josephrb/k0r2/clean` was
not read or written. No `git add -A`, no `git stash`.

**Baseline before any null was believed:** 76 tests, `OK`, rc=0 — read directly, never through a
pipe.

---

## 1. VERDICT

**FIT to support a future Gate-2 filing — conditionally, and the condition is mechanical.**

The defect the repair was assigned, **D-3, is closed.** I re-measured all five fail-open spellings
at `bace69d2` and all five are refused at `68b4af12` (§7 table). The repair is not a seventh
spelling: it makes field-name breadth *unreachable*, its fixture is genuinely producer-derived and
non-circular, its negative control fires hard, and its backstop is live rather than decorative.

**The condition.** One breadth direction is **not** closed and the repair's own fixture is blind to
it by construction: a *partial wildcard in the `M-1` selector* is accepted with no warning and can
suppress the findings of more than one real file (§7, negative controls C and D). This is **not a
regression** — the pre-repair guard accepted it identically — and it was **not in the assigned
repair scope**. But the repair now documents it as intentional, on an argument my controls
falsify in the direction that matters, so it must not be inherited silently.

> **PRECONDITION ON ANY GATE-2 FILING THAT USES THIS INSTRUMENT:** the expected-differences list in
> force at filing time must contain **no partial selector** — that is, no pattern whose `M-1`
> selector both contains `*` and is not exactly `*`. **Satisfied today**: the shipped list has one
> entry, `M-4.behind`, with no selector at all, and 0 of the 30 `UNITS` patterns use one.

The one-line check, to be run against the list actually used:

```python
p, why = cm.parse_pattern(pattern)
assert why is not None or p["selector"] in (None, cm.WILDCARD) or cm.WILDCARD not in p["selector"]
```

I record plainly that a different grader could reasonably have called this **NOT FIT** pending
Joseph's ruling on §7. I did not, for a reason I can state and defend: the exposure is not new, is
not what the repair was for, cannot reach `M-2`, cannot reach a second field of one object, is
absent from every list in the tree today, and requires a reviewable diff to arrive. What it needs
is a decision, not a repair — and the decision is Joseph's, not mine and not the implementer's.

---

## 2. THE SEVEN CLAIMS

| # | Claim | Disposition |
|---|---|---|
| 1 | Defect wider — four further fail-open spellings | **REPRODUCED** |
| 2 | Positive grammar; breadth *inexpressible*; shared constants | **REPRODUCED, one clause OVERSTATED** |
| 3 | `matcher_disagreement` backstop; `field_matches` UNCHANGED | **REPRODUCED** |
| 4 | 64→76 arms; producer-derived fixture; 721 / 96 / 0 | **REPRODUCED EXACTLY** |
| 5 | Negative control 16 arms / 5 methods; mutation matrix 1 / 4 / 97 | **PARTLY REPRODUCED — three figures NOT reproduced** |
| 6 | Behaviour change; 265 of 721; nothing loses acceptance | **REPRODUCED, one denominator needs stating** |
| 7 | Partial wildcards in the `M-1` selector | **RULED (c) — ESCALATES** |

### Claim 1 — the defect was wider. REPRODUCED.

Executed against the `bace69d2` blob, with the filed record's 32 field names as the population:

| spelling | `bad_pattern` at `bace69d2` | filed findings it would suppress |
|---|---|---|
| `M-1[*` | **ACCEPTED** | **19 of 32** — all M-1, nothing else |
| `M-6[*` | **ACCEPTED** | 0 |
| `M-4.head*` | **ACCEPTED** | 1 |
| `M-3.*x` | **ACCEPTED** | 0 |
| `M-4.*e*` | **ACCEPTED** | 3 |

The headline reproduces exactly: **19 of 32, all M-1.** The six deny-list spellings
(`M-4`, `M-4.*`, `M-1[*].*`, `*`, `M-4behind`, `behind`) were all correctly refused at `bace69d2`,
confirming the guard was internally consistent and simply did not model the language it guarded.

On `M-4.*e*` reaching `M-4.head`, `.ahead` and `.behind` **at once** — reproduced, and the citation
holds: all three are `UNITS` entries and all three are emitted by `measure_m1_m6.py:184`. One
precision the implementer did not state: `.ahead` and `.behind` are **absent from the filed
record**, so on that artifact `M-4.*e*` reaches a different three (`head`, `modified`, `untracked`).
The claim is about the field universe, not the filed record, and is true of it.

**The "a seventh deny-list entry would not have closed it" argument is supported**, and by a
stronger route than the implementer gave: `M-3.*x` and `M-4.*e*` are not dotless at all, so the
class was never "dotless patterns". Any enumeration of spellings was going to lose this race.

Two things I add. `M-2[*` and `M-2.*x` were **refused** at `bace69d2` — the perishable claim was
never exposed by D-3, because the `M-2` arm precedes the breadth test. And `M-6[*` / `M-3.*x`
suppress **0** filed findings: they are real fail-opens, but their blast radius on this artifact
was nil, which the implementer's framing did not distinguish.

### Claim 2 — a positive grammar, breadth inexpressible, shared constants. REPRODUCED; one clause OVERSTATED.

Shared constants — **reproduced, and stronger than claimed.** Neither `flatten` nor `parse_pattern`
contains a single hardcoded `"M-k"` literal; both read `ROW_MEASUREMENT_ID`,
`BLOCK_MEASUREMENT_IDS` and `MEASUREMENT_IDS`. Drift test: I appended `M-7` to `MEASUREMENT_IDS` at
runtime and `parse_pattern("M-7.newfield")` immediately accepted it, following the constant rather
than a private model. All 30 `UNITS` patterns parse cleanly under the grammar, so the table and the
guard really are one language.

"A pattern cannot match two fields of one object" — **reproduced.** The terminal field is literal by
construction, and I confirmed by exhaustive sweep over the real population that no accepted pattern
reaches two distinct terminal field names.

**OVERSTATED:** *"breadth is now inexpressible rather than checked for."* That is true of
**field-name** breadth and false of **selector-space** breadth, which remains expressible, is
accepted silently, and is measured firing in §7. The correct statement is: *breadth across the
fields of one object is inexpressible; breadth across files is still expressible and is unchecked.*

### Claim 3 — the backstop, and `field_matches` unchanged. REPRODUCED.

`field_matches` is **byte-identical** across the repair: both sides hash to `07492454…`, 24 lines.
I also diffed the other load-bearing functions: `unit_of`, `canon`, `evaluate_rule`, `compare`,
`load_expected`, `resolve_citations` all identical; only `flatten` changed, and only to read the
shared constants. The stated rationale — that `field_matches` is also the `UNITS` lookup, where
breadth is legitimate — is borne out: `unit_of` matches `M-1[*].present` against every M-1 row, and
narrowing that would have broken the units table.

**The backstop is live, not decorative.** Deleting it (`matcher_disagreement` → `return None`)
reddens **exactly one arm — its own**, `test_the_matcher_BACKSTOP_fires_where_bad_pattern_cannot_reach_it`.
That is the claim, reproduced exactly.

I add a measurement the implementer did not make, and it is the one that shows the backstop earns
its place. Re-allowing a field-name wildcard **with the backstop intact reddens only 1 arm** —
because the backstop catches the rest. Re-allowing it **with the backstop also removed reddens 9
arms across 6 methods, including the producer sweep** `test_every_OVER_BROAD_candidate_the_PRODUCER_generates_is_refused`.
So the two layers are genuinely independent, and the producer sweep has real power against the
breadth class rather than passing vacuously.

### Claim 4 — 64→76 arms, producer-derived fixture, 721 / 96 / 0. REPRODUCED EXACTLY.

Arm count measured by executing **both** revisions, not by counting source: `dce8e8cc` runs **64
tests, OK**; `c8a29082` runs **76 tests, OK**.

Fixture counts, recomputed independently of the suite: **721 candidates, 96 over-broad, 0
accepted.** `"M-1[*" in candidates` is `True`.

**The fixture is genuinely producer-derived, and I checked this specifically because a fixture
derived from the rule cannot disagree with the rule.** Two independent properties hold:

1. `_candidate_patterns` is a mechanical enumeration — every prefix of every field `flatten` really
   emits, each with and without a trailing `*`, plus two structural substitutions. Nothing is typed.
   `M-1[*` falls out as a 4-character prefix plus a star, so the fixture **generates** the known
   failure rather than remembering it. This is a real improvement over the six-spelling deny-list.
2. The `over_broad` predicate is defined on what a pattern **reaches** through `field_matches` —
   distinct terminal field names, or any `M-2` contact — and **never** calls `bad_pattern`. It can
   therefore disagree with the guard, and under the two-layer mutation above it does.

**One caveat that must travel with the 0.** `over_broad` counts distinct **field names**. A pattern
reaching two *files* under one field name scores NARROW. So "96 over-broad, 0 accepted" is a true
and non-vacuous result **about field-name breadth**, and the sweep is structurally incapable of
detecting the selector-space breadth of §7. The 0 is real; its population is narrower than the word
"over-broad" suggests.

### Claim 5 — the negative control and the mutation matrix. PARTLY REPRODUCED; three figures NOT reproduced.

**First, a warning for anyone re-running this.** My own initial harness copied
`docs/orchestration/` to `<mut>/orchestration/`, dropping the `docs/` parent. That reported **6 red
arms at the unmutated baseline** — arms that resolve a citation against a repo root cannot find one.
Had I not run an M0 identity mutation I would have attributed those 6 to the repair. **The
`docs/orchestration` layout is load-bearing for this suite.** With it restored, M0 is rc=0, 0
failures, and every delta below is against a green baseline.

| mutation | arms RED (FAIL+ERROR) | distinct methods | classes | implementer said |
|---|---|---|---|---|
| M0 — identity | **0** | 0 | 0 | (baseline) |
| Restore pristine `bad_pattern` verbatim | **16** | **6** | 3 | "16 arms across 5 methods" |
| Delete the backstop | **1** | 1 | 1 | "exactly its own arm" ✓ |
| Re-allow a field-name wildcard | **1** | 1 | 1 | "reddens 4" |
| Reject-everything guard | **121** (111 fail + 10 error) | 54 | 11 | "reddens 97" |

- **"16 arms" — REPRODUCED EXACTLY** (`failures=16`). This is the number that matters, and it is
  right. The six methods it reddens include
  `test_the_D3_pattern_over_the_REAL_FILED_RECORD_is_refused` and
  `test_every_OVER_BROAD_candidate_the_PRODUCER_generates_is_refused`. **This is a genuine negative
  control, not a null:** the suite would have caught the pristine defect loudly.
- **"across 5 methods" — NOT REPRODUCED.** I measure **6** distinct test methods, 3 classes. No
  counting convention I tried yields 5.
- **"deleting the backstop reddens exactly its own arm" — REPRODUCED EXACTLY.**
- **"re-allowing a field-name wildcard reddens 4" — NOT REPRODUCED.** I measure **1** with the
  backstop intact, **9** (6 methods) with the backstop also removed. Neither is 4.
- **"a reject-everything guard reddens 97" — NOT REPRODUCED.** I measure **121**. I tried two other
  plausible placements of the same mutation: rejecting in `parse_pattern` gives **151**, rejecting
  in `matcher_disagreement` gives **117**. None is 97.

**Disposition.** The *direction* of the matrix is correct in every row: each mutation reddens
something, over-tightening reddens catastrophically, and the backstop is not dead. The repair's
power is real and I verified it independently. But **three of the reported figures are not
reproducible at the graded digests and should not be cited as measurements.** I could not
reconstruct a convention or a mutation placement that produces 5, 4, or 97. The most likely reading
is that they were taken against an intermediate working tree and not re-derived at the committed
state — the campaign's standing hazard of relaying a number that already fits the argument.
**None of this changes the verdict**, because the load-bearing figure (16) reproduces exactly and I
re-derived the rest myself.

### Claim 6 — the behaviour change. REPRODUCED; one denominator needs stating.

**"265 of 721" — REPRODUCED EXACTLY.** Of 721 candidates, 265 are refused despite reaching exactly
one field name today and touching no `M-2` field. (456 refused in total; 301 of those reach exactly
one name if `M-2` contacts are included.) The deliberate over-tightening is real and is the size
claimed.

Every named newly-refused spelling reproduces:

| pattern | at `bace69d2` | at `68b4af12` | reaches today |
|---|---|---|---|
| `M-4.behin*` | accepted | **refused** | exactly 1 field |
| `M-1[` | accepted | **refused** | 0 fields |
| `M-1[*]` | accepted | **refused** | 0 fields |
| `M-1.present` | accepted | **refused** | 0 fields |
| `M-3[x].y` | accepted | **refused** | 0 fields |

I endorse this trade. Four of the five reached **nothing** and were dead whitelist rows reading as
live cover, which is the F-17(a) failure mode arriving through the guard. Refusing `M-4.behin*` —
the one that does narrow today — is the right call for the reason given: it widens silently the day
a field with a shared prefix appears.

**"Nothing in the shipped list, the UNITS table, or the filed record loses acceptance" —
REPRODUCED**, by sweep: 0 losses in all three populations. **State the denominator with it**: the
shipped list contains **one** pattern (`M-4.behind`). "Nothing in the shipped list loses acceptance"
is a true statement over a population of 1, and quoting it without that number overstates the
coverage. `UNITS`: 30 patterns, 3 refused — all three `M-2`, all three refused pre-repair too, so
nothing was lost. Filed record: 32 fields, 1 refused (`M-2.importable`), likewise refused before.

---

## 7. CLAIM 7 — PARTIAL WILDCARDS IN THE `M-1` SELECTOR

**RULING: (c) — an ambiguity that requires a specification decision. This ESCALATES to Joseph.**

I did not reach this by reproducing the implementer's argument. Joseph's constraint was that the
verdict rest on measured positive and negative controls that could have come out the other way, and
that controls enumerated from the grammar's own definition of a legal selector would merely confirm
the grammar. So every control below is computed over the **real** `M-1` population —
`measure_m1_m6.py`'s `M1_FILES`, 10 files — crossed with the row keys `flatten` actually emits, and
the expected sets are computed by independent string operations on that file list, never by asking
`parse_pattern` what is legal.

### 7.1 Positive control — PASSES, and the implementer's argument is confirmed as far as it goes

For 12 probes (6 selector prefixes × 2 real keys), the set `field_matches` reaches is **exactly**
`{files starting with the prefix} × {the named key}`, and is **always a subset of what bare `*`
reaches**:

| pattern | reach | independently expected | subset of bare `*` |
|---|---|---|---|
| `M-1[nd-*].first_insert` | 10 | 10 | yes |
| `M-1[nd-unfolding/u*].first_insert` | 3 | 3 | yes |
| `M-1[nd-unfolding/bootstrap*].first_insert` | 1 | 1 | yes |
| `M-1[nd-unfolding/unified_throw_cov*].first_insert` | 2 | 2 | yes |
| `M-1[nd-unfolding/a*].first_insert` | 2 | 2 | yes |
| `M-1[nd-unfolding/s*].first_insert` | 2 | 2 | yes |

So the wildcard really does behave as a selector-space device, and **the implementer's argument is
sound on its own terms.** It is also the wrong comparison, which the next two controls show.

### 7.2 Negative controls A and B — do NOT fire

- **A: can a partial selector reach a second field NAME of one object?** Swept every prefix × every
  emitted key: **0 cases.** The terminal field is literal, so this direction is genuinely closed.
- **B: can a partial selector reach `M-2`, the unsuppressible claim?** **0 cases.** A pattern must
  begin `M-1[`, so the perishable claim is structurally out of reach.

These matter and I record them as real assurance.

### 7.3 Negative control C — **FIRES**, on the real population, with no hypothetical

`measure_m1_m6.py`'s `M1_FILES` already contains two files where one path is a prefix of the other:

```
nd-unfolding/unified_throw_cov.py
nd-unfolding/unified_throw_cov_5d.py
```

Therefore, at `68b4af12`:

```
pattern:  M-1[nd-unfolding/unified_throw_cov*].first_insert
verdict:  ACCEPTED — no refusal, no warning
suppresses: M-1[nd-unfolding/unified_throw_cov.py].first_insert
            M-1[nd-unfolding/unified_throw_cov_5d.py].first_insert
distinct field NAMES: 1   -> the repair's own over_broad predicate scores this NARROW
distinct FILES:       2
```

A reviewer reading that row sees something shaped like a file path and will read it as one file. It
is two. And the file it silently picks up alongside the named one is
`nd-unfolding/unified_throw_cov.py` — **the tenth M-1 row, whose omission from the 2026-08-22 filing
was the F-17(a) failure this whole instrument exists to prevent.** The blast radius is not
theoretical; it lands on the exact file with the worst history.

### 7.4 Negative control D — **FIRES**: reach is not stable under the population growing

The repair refuses `M-4.behin*` with the reason that such a pattern *"would whitelist more than one
field of that object"* — i.e. it may narrow today and widen silently tomorrow. I applied that same
test to selectors, adding one plausible file (`nd-unfolding/bootstrap_nd_v2.py`) to `M1_FILES`:

| pattern | reach before | after | accepted? |
|---|---|---|---|
| `M-1[nd-unfolding/bootstrap*].first_insert` | 1 | **2 — WIDENED SILENTLY** | yes |
| `M-1[nd-unfolding/bootstrap_nd.py].first_insert` (literal) | 1 | 1 — stable | yes |
| `M-1[*].first_insert` (bare star) | 10 | 11 — widened, but *visibly* maximal | yes |

**This is the finding.** The repair applies the silent-widening rule to field names and not to
selectors, and offers no measurement distinguishing the two. The partial selector is the **only**
form that is simultaneously (i) not visibly maximal and (ii) not stable under population change. A
literal is stable; a bare `*` is honest about covering everything; a partial selector looks specific
and moves. "Not broader than bare `*`" is not the property a whitelist entry needs — it is an
asymmetric comparison against the most permissive baseline available instead of against the
alternative actually on the table.

### 7.5 Why (c), and not (a) or (b)

**Not (b), an enlargement — this is measured, not argued.** The pre-repair guard accepted partial
selectors *identically*:

| pattern | `bace69d2` | `68b4af12` |
|---|---|---|
| `M-1[nd-*].n_after` | ACCEPTED | ACCEPTED |
| `M-1[nd-unfolding/bootstrap*].first_insert` | ACCEPTED | ACCEPTED |
| `M-1[nd-unfolding/unified_throw_cov*].first_insert` | ACCEPTED | ACCEPTED |

The repair did not widen what is expressible on this axis. Anyone reporting (b) is wrong on a fact.

**Not (a), within the existing contract.** The tempting argument is that the language "already
admitted it" because the old implementation accepted it. That argument fails, and it fails for a
reason specific to this defect: **the clause that accepted `M-1[nd-*].n_after` is the very clause
that accepted `M-1[*`.** `pattern.rsplit(".", 1)[-1] in ("*", "**")` waved the partial selector
through because it does not end in a wildcard *segment* — the same reasoning, in the same
expression, that is D-3. A behaviour inherited from a guard now known to be fail-open is an
artifact, not an admission. You cannot cite a defective guard as evidence of what the contract
permits.

And no governing document settles it. I checked each:

- `REVIEW-CONTRACT-20260822-k0-execution-integrity.md` `:621` / `:1471` — the F-17(b) clause says
  *differences are reported as findings*. It contains no whitelist concept at all, so a fortiori no
  selector grammar.
- `SPEC-20260825-f17b-tree-comparison-instrument.md` — says the expected list must be an input file
  and must have a failing arm. **Nothing about pattern shape.**
- `m1m6_expected_differences.json` prose — describes refusals as *"a bare measurement id or ends in
  a wildcard segment"*. A partial selector does not end in a wildcard segment, so the prose is
  consistent with accepting it — but it is describing the **deny-list that has just been deleted**,
  so it is a description of the defect, not a contract. (This note's staleness is separately routed
  and is not held against the repair.)
- The `UNITS` table — 30 patterns, **0** with a partial selector; bare `*` exclusively.

So: the pre-repair acceptance was accidental, the documents are silent, and the repair now converts
that accident into a **documented design rule** (*"Permitting `*` inside the selector costs
nothing in the breadth direction"*) on reasoning the implementer itself flagged as an argument
rather than a measurement — and which controls C and D falsify in the direction that loses
information. That is precisely an ambiguity the contract does not determine. **Someone must decide.
(c).**

### 7.6 My recommendation to Joseph — a recommendation, not a ruling

**Narrow the selector to `*`-or-literal.** Measured cost of doing so **today: zero.** The shipped
list contains no partial selector; 0 of 30 `UNITS` patterns use one; no pattern in the filed record
uses one. Nothing in the tree loses acceptance. The change is a two-line addition to
`parse_pattern` — reject a selector that contains `*` and is not exactly `*` — and it would move the
partial-selector class from "expressible and unchecked" into the same *inexpressible* status the
repair achieved for field names, which is the standard the repair set for itself.

If Joseph instead rules partial selectors admissible, that is a coherent position and the precondition
in §1 should be replaced by a requirement that any partial selector entry state its reach — the
list of files it covers — at the time it is added, so that widening is visible in the diff.

---

## 8. THE PATTERN GRAMMAR AS GRADED

Enumerated by **running** `bad_pattern` at `68b4af12`, not by reading it. This is the table the
prose note may be transcribed from; it describes graded behaviour, not intent.

**ACCEPTED**

| shape | example |
|---|---|
| `M-k.<field>`, k ∈ {3,4,5,6}, `<field>` a literal with no `*` | `M-4.behind`, `M-3.rc`, `M-6.present` |
| `M-1[<literal file path>].<field>` | `M-1[nd-unfolding/bootstrap_nd.py].first_insert` |
| `M-1[*].<field>` — the bare per-file wildcard | `M-1[*].present` |
| `M-1[<partial>*<partial>].<field>` — **accepted, and the open question of §7** | `M-1[nd-*].present` |

**REFUSED** — with the reason the guard actually prints

| shape | example | reason |
|---|---|---|
| not starting with a measurement id | `*`, `behind`, `M-7.x` | does not begin with a measurement id |
| bare measurement id | `M-4`, `M-1` | would whitelist all of it; name fields |
| id not followed by `.` or `[` | `M-4behind` | next character must be `.` |
| `M-1` without a selector | `M-1.present` | M-1 is measured per file |
| unclosed selector — **this is D-3** | `M-1[`, `M-1[*` | the `[` selector is never closed |
| empty selector | `M-1[]`, `M-1[].x` | selector between `[` and `]` is empty |
| no `.` after `]` | `M-1[*]` | after `]` the next character must be `.` |
| empty field name | `M-4.`, `M-1[*].` | the field name after `.` is empty |
| **any `*` in the terminal field name** | `M-4.*`, `M-4.head*`, `M-3.*x`, `M-4.*e*`, `M-4.behin*`, `M-1[*].*` | the wildcard is a selector-space device |
| `[...]` on any measurement but `M-1` | `M-6[*`, `M-3[x].y` | only M-1 is measured per file |
| **anything targeting `M-2`** | `M-2.importable`, `M-2.python` | the perishable claim is never suppressible |
| a pattern the matcher reads as matching nothing it names, or as also reaching a sibling / prefix / suffix / other-measurement field | (backstop) | guard and matcher disagree; failing closed |

The empty string and non-strings are refused as "a field pattern must be a non-empty string".

---

## 9. EXPIRY — MECHANICAL

**This grade expires automatically, with no notice and no judgement call, when any of these three
content digests moves.** All three were measured at the top of §0.

| path | content sha256 (full) |
|---|---|
| `docs/orchestration/compare_m1_m6.py` | `68b4af1293383f593b14a0922e61c0c3b1ec5a86ecfb396fceaf10a2a77fb35b` |
| `docs/orchestration/test_compare_m1_m6.py` | `b355ecdc809ef84fcd454eac2db3df3f44ff6e956f7f46971cfcfb072c347add` |
| `docs/orchestration/measure_m1_m6.py` | `0fcd90f7c92a7071208e62d09ebc38956f1a83b11af41a469b4886a6e6786d79` |

`measure_m1_m6.py` is pinned **even though it was not graded**, because every control in §7 is
computed over its `M1_FILES` and the keys `flatten` derives from its output. Change the file
population and §7's measurements describe a world that no longer exists — in particular, the
`unified_throw_cov` prefix collision could vanish or multiply.

```bash
sha256sum docs/orchestration/compare_m1_m6.py \
          docs/orchestration/test_compare_m1_m6.py \
          docs/orchestration/measure_m1_m6.py
```

Any mismatch ⇒ **this grade is void and the instrument is UNGRADED again.** The predecessor grade
`GRADE-20260825-f17b-comparison-instrument-fitness.md` (content sha256 `aa1b6eee`) expired by
exactly this mechanism and its expiry went unnoticed while it was still being cited — so a reader
who finds this document must run the command above before relying on a word of it.

**`m1m6_expected_differences.json` is deliberately NOT an expiry pin.** Its digest `56c2e0ef` is an
as-of identifier; it is expected to change when the prose note is corrected, and that change must
not void this grade. It is instead governed by the **standing precondition in §1**, which is checked
against the list in force at filing time rather than against a digest.

---

## 10. WHAT I DID NOT DO, AND WHERE I MAY BE WRONG

- I graded the **guard**. I did not re-grade citation resolution, the exit vocabulary, tolerance
  evaluation, or the record schema; the expired grade covered those at a different revision and I
  did not carry its conclusions forward.
- I ran the instrument only against fixtures and the filed record's **field names**. I ran no
  comparison producing a Gate-2 relevant verdict, and consumed no run product.
- My §7 controls use `M1_FILES` as the file population. If the far-end tree's real files differ from
  that tuple, control C's specific collision could differ — the *mechanism* would not.
- **On the framing of my assignment.** I was asked to say if the dispatching lane biased it. I do not
  think it did, and I want to be precise rather than polite about why: the brief named its own
  disqualification, listed the traps that would most damage its preferred outcome, told me to run the
  negative control myself, and pre-committed that "not fit" was an acceptable answer. Its one
  slanted element — a looser claim-7 framing that invited me to weigh the implementer's argument on
  its merits — it corrected mid-run by relaying Joseph's narrower three-way question, which is the
  correction that produced controls C and D. Had I ruled on the original wording I would probably
  have landed on (a) and been wrong. I record that the correction, not the original dispatch, is
  what made this ruling reachable.
- I am one lane. Claim 5's three unreproduced figures are the kind of thing a second grader should
  re-run before this document is leaned on.
