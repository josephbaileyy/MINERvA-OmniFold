# GRADE 2026-08-25 — is the NARROWED `M-1` selector fit to support a future Gate-2 filing?

Author: independent grading lane. I authored no part of this instrument, its suite, its
specification, its whitelist, or the far-end evidence, and **I repaired nothing** — every defect and
imprecision below is reported, not fixed. Under ruling 3 of
`DECISION-20260825-joseph-gate2-fail-and-four-rulings.md` I am the third party: spec author
(publication close-out lane) ≠ implementer (selector-narrowing lane, `63262a3a`) ≠ grader (this
document). The prior grading lane is also disqualified here: it *recommended* this narrowing, so it
cannot grade its own recommendation's implementation.

## CITABLE FOR

- The fitness of **one instrument** — `docs/orchestration/compare_m1_m6.py` at content sha256
  `5dc92487` and `docs/orchestration/test_compare_m1_m6.py` at `762fac14`, both as changed in
  `63262a3a` — against **one specification**: §12.2.1 of
  `DECISION-20260825-joseph-gate2-fail-and-four-rulings.md`, "selector syntax narrows to a bare `*`
  or an exact literal; partial selector wildcards are REFUSED."
- **`NEWLY ACCEPTED = 0`**, measured over 115160 patterns of my own construction (§3). The column
  that had to be empty is empty.
- The disposition of each of the implementer's thirteen claims, with my measurement beside it (§5).
- **The ruling on claim 8's placement argument: CORRECT** (§6), and on claim 9's
  syntactic-not-reach honesty: **mechanism honest, framing claim NOT reproduced** (§7).
- The exact accepted and rejected pattern shapes, enumerated by **running** `bad_pattern` (§8). This
  is the table `m1m6_expected_differences.json`'s prose note may be transcribed from, per §12.1.
- Four implementer figures that do **not** reproduce or are **overstated** (§5, claims 1, 6, 9, 11),
  and one **pre-existing** unreproduced docstring figure inherited from `68b4af12` (§9).

## NOT CITABLE FOR

- **Any Gate-2 clause, F-number, or gate verdict. Gate 2 remains FAIL and open** and nothing here
  changes that. This document grades an instrument; it discharges nothing.
- **A rehearsal, a Gate-2 filing, or compute.** Per §10.1 a passing grade **authorizes only that
  mechanism** and accumulates no credit toward permission. Those need a *separate readiness check*
  confirming that all prospective F-7(b), F-8(b) **and** F-17(b) mechanisms are present **and
  independently graded**. That check is a distinct act and this is not it.
- Authority to file, submit, adopt, consume or quote any product of run
  `k0-aa67c426-20260824T145751Z`. Untouched. **No product of that run was read, parsed or
  consumed by this grade** — not even as a comparator input.
- Leg 6, any member k≠0, family or undeclared-member adoption. No `values.tex` negweight swap.
- **Compute of any kind. No Slurm job was submitted.**
- The correctness of `measure_m1_m6.py`, the far-end script, the whitelist's *content*, citation
  resolution, the exit vocabulary, tolerance evaluation, the record schema, or any physics claim.
  I graded the selector narrowing and its blast radius on the pattern guard, nothing else.
- **The implementer's denominator "4840".** It is not reproducible from the committed artifacts
  (§5.1). Cite the numerator `4060`, which reproduces exactly, or cite my `115160`.

---

## 0. WHAT WAS GRADED, HOW I KNOW IT DID NOT MOVE, AND THAT THE PRIOR GRADE'S EXPIRY TRIPPED

All work in **detached worktrees** (`git worktree add --detach`), five of them, each verified by
`git -C "$T" rev-parse --git-dir` (a worktree's `.git` is a file). Explicit `TMPDIR`,
`PYTHONDONTWRITEBYTECODE=1`, `__pycache__` purged between mutations. Interpreter
`/global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3` = **Python 3.11.14** (system `python3` is
3.6.15 and was not used). The `docs/orchestration/` layout was preserved in every worktree — it is
load-bearing, and flattening it is how the prior grader's first harness produced 6 false reds.

| path | field | value |
|---|---|---|
| `docs/orchestration/compare_m1_m6.py` | content sha256 | `5dc92487bd5c2f6a…`, 66599 bytes |
| `docs/orchestration/test_compare_m1_m6.py` | content sha256 | `762fac146baee350…`, 93747 bytes |
| `docs/orchestration/measure_m1_m6.py` (input instrument, NOT graded) | content sha256 | `0fcd90f7c92a7071…` |
| `docs/orchestration/m1m6_expected_differences.json` (population, NOT graded, frozen) | content sha256 | `92091ae8…` |
| `docs/orchestration/state/f17b-k0-aa67c426-20260824T145751Z.json` (never opened) | content sha256 | `9109f371…`, 53226 bytes |

Instrument commit **`63262a3a`**. Tree HEAD at the time of writing: **`fb44fb56`**.

### 0.1 THE PRIOR GRADE'S EXPIRY TRIPPED — VERIFIED, NOT ASSUMED

I ran `GRADE-20260825-d3-comparator-repair-fitness.md` §9's own command verbatim and compared to the
three digests it pins:

| path | §9 pinned | measured at `fb44fb56` | moved? |
|---|---|---|---|
| `compare_m1_m6.py` | `68b4af1293383f59…` | `5dc92487bd5c2f6a…` | **YES** |
| `test_compare_m1_m6.py` | `b355ecdc809ef84f…` | `762fac146baee350…` | **YES** |
| `measure_m1_m6.py` | `0fcd90f7c92a7071…` | `0fcd90f7c92a7071…` | no |

Two of three moved, so **the prior grade is VOID by its own mechanism, by design**, and the
instrument had **no live grade** until this document. This grade replaces it. §7 of the prior grade
(the (c) ruling) is *superseded by Joseph's §12.2.1 ruling*, not by me; its §8 table is superseded by
my §8.

### 0.2 THE TARGET MOVED UNDER ME — RE-DERIVED, NOT INHERITED

The implementer reported that `main` moved under it and **explicitly asked me to re-derive that
rather than take it from it.** I did, by **blob id** (`git rev-parse <rev>:<path>`) and by content
sha256, which are different fields:

| rev | `compare_m1_m6.py` blob | `test_compare_m1_m6.py` blob |
|---|---|---|
| `4a62f1b4` (its cut point) | `c23116b8` | `02220f5f` |
| `1efa69b2` (peer) | `c23116b8` | `02220f5f` |
| `8f80050c` (peer) | `c23116b8` | `02220f5f` |
| `63262a3a` (its commit) | `7ca17299` | `f268cff6` |

Byte-identical across all three pre-commit revs, content sha256 `68b4af12` / `b355ecdc` at both
`4a62f1b4` and `8f80050c`, and `git show --name-only` on both peer commits lists neither file.
**Claim 13 reproduced.** It moved again under *me*: `bf23fa8f` and `fb44fb56` landed during this
grade (a `.git`-mtime reconciliation and a live-state refresh). Neither touches the pair; all three
graded digests are unchanged at `fb44fb56`. §12.2.1 itself is byte-unchanged since `63262a3a`.

### 0.3 PROHIBITIONS HONOURED

`docs/orchestration/state/f17b-k0-aa67c426-20260824T145751Z.json` was **never opened at all** — not
read, not parsed, only re-hashed to prove it: `9109f371`, 53226 bytes, unchanged.
`m1m6_expected_differences.json` was read only, digest `92091ae8` unchanged. `generate_manifest.py`
untouched (`git diff` empty). `/pscratch/sd/j/josephrb/k0r2/clean` was **not written, not read, and
no `git` was run against it** — §11.1 of the decision now records that a `git` read there is not a
read-only act. No `git add -A`, no `git stash`, no Slurm job, no sweep.

---

## 1. VERDICT

**FIT to support a future Gate-2 filing, as an instrument, with no condition attached.**

The narrowing implements §12.2.1 exactly and its blast radius is the smallest it could be: over
115160 patterns of my own construction, the **only** verdict transition anywhere is
`ACCEPT → REFUSED-as-partial-selector`, 42224 times, and **the newly-accepted set is empty**. Every
one of the thirteen other refusal checks refuses a population of *identical size* before and after.
The suite gained a real firing arm, a real power control, a real covering sweep and a real
silent-on-good arm, and **both negative controls fire**, reproducing the implementer's 5/134/0 and
6-red matrices exactly.

The prior grade's standing precondition — "the expected list at filing time must contain no partial
`M-1` selector" — is now **unnecessary**: the guard makes it unrepresentable rather than checked
for. That is a strict improvement in kind, not only in degree.

**Four claims are overstated or unreproduced, none of them behavioural** (§5). One is a prose
correction Joseph should see (§7). Two figures should not be cited as measurements: the implementer's
denominator `4840`, and a **pre-existing** `265` inherited from `68b4af12` (§9).

**This authorizes only this mechanism.** Gate 2 stays **FAIL and open**. No rehearsal, no filing, no
compute.

---

## 2. THE SUITE, AND WHAT ACTUALLY CHANGED IN IT

| tree | guard sha256 | suite sha256 | result |
|---|---|---|---|
| `8f80050c` (pre-ruling) | `68b4af12` | `b355ecdc` | **76 tests, OK** |
| `63262a3a` (graded) | `5dc92487` | `762fac14` | **81 tests, OK** |

Arm-name diff, computed from `unittest -v` output, not from the diff:

- **75** arms name-identical.
- **1** removed: `test_a_PARTIAL_selector_wildcard_still_narrows_end_to_end__silent_on_good` — the
  **inverted** arm. It had asserted the old behaviour on the asymmetric "cannot widen past bare `*`"
  argument, and its docstring now preserves that argument *and* why it was the wrong comparison.
  Keeping the retired reasoning visible is the right call.
- **6** added by name: the firing arm (`…_is_REFUSED_end_to_end__fires_on_bad`), the two-real-file
  power control, the reach-instability control, the 4060-candidate covering sweep, the
  two-legal-forms silent-on-good sweep, and the reaches-one-file-or-all invariant.

Net **+5**, which is the implementer's "76 → 81" and its "one inverted, five added" — the inversion
is a rename, so 6 new names for 5 net arms. **Claim 3 reproduced.**

### 2.1 Negative control 1 — revert the guard, keep the new suite. REPRODUCED EXACTLY.

`compare_m1_m6.py` restored to the `8f80050c` blob (`68b4af12`) in a worktree at `63262a3a`, suite
left at `762fac14`, `__pycache__` purged:

```
Ran 81 tests ... FAILED (failures=134)
5 distinct test methods red, 0 errors
```

The five: `…_is_REFUSED_end_to_end__fires_on_bad`, `…_really_DOES_cover_TWO_REAL_FILES…`,
`…_REACH_MOVES_when_the_population_grows…`,
`…_every_PARTIAL_selector_the_PRODUCER_generates_is_refused…`,
`…_every_ACCEPTED_M1_pattern_reaches_ONE_FILE_or_ALL_of_them…`. **`comm` against the pre-existing
arm names returns empty: not one pre-existing arm goes red.** `5 / 134 / 0` is the implementer's
figure exactly. One correction: it says "all **76** pre-existing tests stay GREEN"; there are **75**
name-identical pre-existing arms (the 76th is the one it inverted). Immaterial, but the number is 75.

### 2.2 Negative control 2 — the opposite mutation. REPRODUCED EXACTLY, AND IT IS REAL.

Over-tightening so that literals are refused too — one edit, `selector != WILDCARD and WILDCARD in
selector` → `selector != WILDCARD`:

```
Ran 81 tests ... FAILED (failures=78)
6 distinct test methods red, 0 errors
```

Including the intended silent-on-good arm
`test_the_TWO_LEGAL_selector_forms_survive_over_the_REAL_population__silent_on_good`, and **exactly
two pre-existing** arms: `test_every_field_the_PRODUCER_emits_is_accepted_verbatim__silent_on_good`
and `test_every_field_in_the_FILED_RECORD_is_nameable_one_at_a_time__silent_on_good`. **Claim 5
reproduced exactly**, and the opposite-direction arm is not decorative — the guard has an arm that
fires on bad, one silent on good, and one for the opposite-direction bad.

### 2.3 M0 identity mutation — clean baseline.

Rewriting `compare_m1_m6.py` through the same mutation harness with an identity substitution left
sha256 `5dc92487` unchanged, `git status --porcelain` **0 lines**, and the suite **81 OK**. The
harness produces no false reds and the repo layout survived it.

---

## 3. THE BEHAVIOUR DELTA, ON A POPULATION I BUILT MYSELF

The implementer's fixture is a defensible corpus-derived generator (§4), but a grader who scores only
the implementer's population has measured the implementer's argument. I built my own: **115160
distinct patterns**, generated from `measure_m1_m6.M1_FILES` and the row keys the producer emits —
not typed, and **never consulting `parse_pattern` or `bad_pattern`**, which are the things under
test. It contains: every legal literal and bare-`*` M-1 form; every prefix-star, star-suffix and
star-in-the-middle selector of every real path; every block-measurement literal and every
wildcarded spelling of every block field; every wildcarded terminal field under both selector
forms; **every proper prefix (truncation) of all of the above, each with and without a trailing
star** (this is what generates D-3's `M-1[*` and the `M-6[*` class mechanically rather than from
memory); and mechanically-formed structural oddities including `M-2`, `M-7`, the empty string and
non-strings. Both revs were scored in **separate processes** over the **same serialized population
file**, so the operand is provably identical.

| | old guard `68b4af12` | new guard `5dc92487` |
|---|---|---|
| accepted | 42997 | **773** |
| refused | 72163 | 114387 |
| exceptions raised | 0 | 0 |

| transition | count |
|---|---|
| **newly ACCEPTED** | **0** |
| newly REFUSED | 42224 |
| same verdict, message reworded | 50270 |
| byte-identical message | 22666 |

**`NEWLY ACCEPTED = 0`, and set-theoretically: `accepted_new \ accepted_old = ∅`.** `42997 − 42224 =
773` closes. This is also structurally guaranteed by the diff — the only executable change is one
*added* `return None, (…)` refusal branch; every other change is f-string message text, which cannot
turn a refusal into an acceptance — and the 115160-pattern sweep is the measurement that would have
caught it had I misread the diff.

**Every one of the 42224 newly-refused patterns is a closed partial `M-1` selector**, verified by an
independent selector extractor (`p[4:p.index("]")]`, star-containing, not equal to `*`): the
count of newly-refused patterns *not* of that shape is **0**, and the count whose message lacks the
string `PARTIAL` is **0**. **No unexplained residue.**

**The 50270 rewordings fall in exactly two classes and no third:** 50266 are the field-wildcard
refusal text, 4 are the `M-1`-shape hint (`<file or *>` → `<exact file path or *>`). Both are
cosmetic — see §6 for the proof that neither changed *which* check fired.

---

## 4. IS THE NEW FIXTURE GENUINELY CORPUS-DERIVED? YES.

The standing hazard is that a fixture derived from the rule cannot disagree with the rule.
`_partial_selector_patterns` is built from `measure_m1_m6.M1_FILES` crossed with the row keys, by
pure string slicing. **It does not import, call or reference `parse_pattern` or `bad_pattern`** —
verified by reading it and by the fact that every pattern it emits was *accepted* by the pre-ruling
guard, which is the operational definition of a fixture that can disagree. I re-ran it:

| measurement | implementer's claim | mine | verdict |
|---|---|---|---|
| candidates generated | 4060 | **4060** | exact |
| of those, reach **>1** real file today | 210 | **210** | exact |
| of those, reach exactly **1** | 3850 | **3850** | exact |
| of those, reach **0** | — | 0 | — |
| escaped the new guard | 0 | **0** | exact |

The "second generator, not a widening" decision is **correct on its stated ground, and I measured
the ground**: `_candidate_patterns` only ever appends a star to a *prefix* of an emitted field, so
its M-1 output is either unclosed (D-3, already refused) or carries the star in the terminal field.
Over the real universe it emits **1499** candidates and **0** closed partial selectors — it
structurally cannot reach this class. And the graded numbers did not move: over the bench universe,
`_candidate_patterns` = **721 candidates, 96 over-broad, 0 escaped** at *both* `68b4af12` and
`5dc92487`, using the suite's own `over_broad` predicate. **Claim 7 reproduced.**

`base_document` really cannot carry the failure: its two M-1 selectors are
`nd-unfolding/adopt_unified_5d.py` and `nd-unfolding/bootstrap_nd.py`, and the decisive pair is
`unified_throw_cov.py` / `unified_throw_cov_5d.py`. Building the new arms on `M1_FILES` was
necessary, not stylistic.

**One sub-claim of claim 7 is degenerate as implemented.** The implementer says the pre-existing
`over_broad` predicate scores the decisive pattern NARROW "because it counts distinct field *names*
while a partial selector spans *files* at one field name." That is **true over the real
population** — I measured `M-1[nd-unfolding/unified_throw_cov*].first_insert` reaching **2 files but
1 distinct terminal name**, so a name-counting predicate scores it narrow. But the arm asserts
`assertFalse(self.over_broad(partial))` over the **bench** universe, where that pattern reaches
**0 fields** — so the assertion passes because the reach is *empty*, not for the stated reason. The
conclusion is right; the line cited for it is not evidence for it. **Reported, not repaired.**

---

## 5. THE THIRTEEN CLAIMS

| # | claim | disposition |
|---|---|---|
| 1 | delta over 4840: 4060 newly refused all partial, 0 other shape, **0 newly accepted**, 305 reworded (303+2), no residue | **REPRODUCED IN SHAPE on a 24× larger population; denominator NOT REPRODUCIBLE** (§5.1) |
| 2 | of the 4060: 210 reach >1 today, 3850 reach exactly 1 | **REPRODUCED EXACTLY** |
| 3 | 76 → 81 arms, one inverted, five added | **REPRODUCED** (6 new names, 1 removed, 75 identical) |
| 4 | NC1: 5 distinct red, 134 with subTests, 0 errors, pre-existing green | **REPRODUCED EXACTLY** (pre-existing count is 75, not 76) |
| 5 | NC2 over-tighten: 6 red incl. the silent-on-good arm and two pre-existing | **REPRODUCED EXACTLY** |
| 6 | `field_matches` untouched because it is also the UNITS lookup | **fact REPRODUCED; stated GROUND OVERSTATED** (§5.2) |
| 7 | second generator, 0 of 721, `over_broad` scores it narrow, bench can't carry it | **REPRODUCED**, one fixture assertion degenerate (§4) |
| 8 | the check is placed LAST; nothing previously refused changes | **REPRODUCED and the placement is CORRECT** (§6) |
| 9 | `M-1[nd-*]` reaches all 10, so this is syntactic and it says so in the code | **measurement REPRODUCED; the honesty claim NOT REPRODUCED** (§7) |
| 10 | 0 of 30 UNITS patterns; shipped list's only pattern is `M-4.behind` | **REPRODUCED EXACTLY** |
| 11 | prose corrected in three places; `"SELECTOR-space"` deliberately kept | **partly reproduced: FOUR prose sites, not three** (§5.3) |
| 12 | digests; F-14 `--check` rc=0, rows=532; suite 81 OK | **REPRODUCED EXACTLY** |
| 13 | `main` moved; neither peer commit touches the pair; byte-identical | **REPRODUCED, and extended** (§0.2) |

### 5.1 Claim 1 — the denominator is not recoverable

`4060`, `210`, `3850`, `0 newly accepted` and the two-class rewording structure all reproduce; the
**`4840`** does not. The implementer did not commit its probe script, and "the real `M1_FILES`
population crossed with the row keys `flatten` emits" is 50 field paths, not 4840 patterns. I could
not reconstruct a population of that size from the committed artifacts, so `305`, `303` and `2` are
not checkable either — my own population gives `50270` reworded in the *same two classes* with the
*same* ordering (field-wildcard text ≫ M-1 shape hint) and **no third class**, which is the
substantive content. **Cite the numerator `4060` or my `115160`; do not cite "4060 of 4840" as a
measurement.** This is the same class the prior grade withdrew three figures for, and it is why every
figure in this document names the population beside the count.

### 5.2 Claim 6 — right to leave `field_matches` alone, wrong reason

`field_matches` is untouched: verified, the diff does not reach it. Leaving it alone is **correct**,
but not for the reason given. The stated ground is that `M-1[*].<key>` must match every file's field
to assign a unit, so narrowing it would break unit assignment and the `matcher_disagreement`
backstop. Measured: **0 of 30 `UNITS` patterns is a partial selector** — the five M-1 rows are all
bare `M-1[*].<key>` — so mirroring *the ruled narrowing* (bare `*` or exact literal) inside
`field_matches` would cost unit assignment **nothing**. The claim only holds under a different
narrowing (stripping `*` semantics entirely), which nobody proposed.

The **correct and sufficient** reason is the one the file already states elsewhere and the claim
does not: `field_matches` is deliberately an *independent second implementation* that
`matcher_disagreement` interrogates instead of modelling the language twice. Teaching it the grammar
would make the backstop circular — a fixture derived from the rule cannot disagree with the rule.
**Right decision, wrong justification. Reported, not repaired.**

### 5.3 Claim 11 — four prose sites, not three

Prose changed at: the **module docstring** (grammar summary, lines ~54-65); the **`parse_pattern`
docstring** (the retired argument and the two retiring measurements); the **`M-1`-shape hint
message** (`<file or *>` → `<exact file path or *>`); and the **field-wildcard refusal message**.
That is four, claimed three. The literal `"SELECTOR-space"` **is** preserved — 3 occurrences in
`compare_m1_m6.py` — and the pre-existing `M-4.behin*` arm's `assertIn("SELECTOR-space", why)` binds
and is green. An undercount, immaterial to behaviour.

### 5.4 Claim 10 — zero compatibility cost, confirmed operationally

`0 of 30 UNITS` patterns is a partial selector. The shipped
`m1m6_expected_differences.json`'s only field pattern is **`M-4.behind`** — not an M-1 pattern at
all. And the decisive operational check: `load_expected()` on the shipped file succeeds **identically
under both guards**, 3 entries, no refusal. Repo-wide, the only tracked files containing
partial-selector text are five markdown records plus the two graded files and the `notes` prose block
of `m1m6_expected_differences.json` (lines 23-49) — **prose, never an operative pattern**. That
prose is the stale text §12.1/§12.2.1 says is to be transcribed from this grade.

---

## 6. RULING ON CLAIM 8 — THE PLACEMENT IS CORRECT

Asked to press this design point, so here is the measurement rather than a reading. I fingerprinted
each refusal message into the **identity of the check that fired** (15 discriminating substrings,
one per refusal site plus `ACCEPT`) and diffed old against new across all 115160 patterns.

**There is exactly one check-identity transition in the entire population:**

```
ACCEPT  ->  partial-selector      42224
(no other transition, in either direction)
```

and the population of every other check is **the same size before and after** — `unclosed` 18342,
`field-wildcard` 50266, `no-dot-after-bracket` 1646, `bracket-on-block` 966, `empty-field` 828,
`no-mid` 58, `m2` 33, `no-dot-after-id` 10, `bare-id` 6, `m1-shape` 4, `empty-sel` 3, `nonstring` 1,
identical on both sides. So the newly-refused set is **exactly** {parsed clean **and** carried a
partial selector}, which is what placing the check last was for, and nothing previously refused
changed *which* check refuses it. **Claim 8's placement argument: REPRODUCED and CORRECT.**

**But the stronger phrasing put to me — "nothing previously refused changes even its printed
*reason*" — is FALSE as stated**, and the implementer's own claim 1 discloses why: 305 patterns in
its population (50270 in mine) print *different text* for the *same* check. The defensible claim is
the one about check identity, not about text. I record the distinction because a reader who tests
the stronger sentence will find it fails and may wrongly conclude the placement claim failed.

**One consequence of the placement, which is the right tradeoff but should be stated.** 38976
patterns in my population carry **both** a partial selector and a terminal field wildcard; **all
38976 print the field-wildcard reason**, and the partial-selector reason is masked. That is
unavoidable given last-placement — and last-placement is precisely what buys the no-regression
property above. Reporting the more fundamental structural error first is also the better message.
Not a defect; a documented consequence.

---

## 7. RULING ON CLAIM 9 — THE MECHANISM IS HONEST, THE CLAIM ABOUT THE CODE IS NOT

The claim has two halves and they part company.

**The measurement reproduces.** `M-1[nd-*].first_insert` reaches **10 of 10** files in `M1_FILES`
today. So the ruling genuinely **cannot** be expressed as a reach predicate: a breadth test would
accept `M-1[nd-*]` (it reaches everything, so it is not a *proper* subset) while the ruling refuses
it. The ruling is syntactic.

**The mechanism is honest.** `parse_pattern`'s new branch is
`selector is not None and selector != WILDCARD and WILDCARD in selector` — pure syntax. I confirmed
by introspection that the body of `parse_pattern` references **neither** `field_matches` **nor**
`M1_FILES`: there is no reach computation anywhere in the guard, and no pretence of one. The
docstring's justification is correspondingly forward-looking rather than breadth-measuring ("its
reach moves silently when the measured file population changes"), which is the same reasoning the
guard already applied to `M-4.behin*`.

**The claim that it "says so in the code" does NOT reproduce.** No file records the `nd-*`
measurement or the sentence "this cannot be a reach test". Worse, the new invariant arm's docstring
says the *opposite* of claim 9:

> "The point of the narrowing is not that a particular syntax is banned; it is that an accepted M-1
> entry covers either one nameable file or, visibly, the whole population — never a silent proper
> subset. … so it fails if some future spelling slips past `parse_pattern` while landing in the
> middle. … this one catches the residue of under-refusal."

Measured: `M-1[nd-*].first_insert` **satisfies** that invariant (`reached == everything`). So had
that spelling slipped past `parse_pattern`, this arm would **not** have caught it — the arm's
advertised job, "the residue of under-refusal", is not fully discharged by it, and the framing it
offers is the reach framing claim 9 says the implementation avoided.

**Coverage is nevertheless intact, by a different arm than the docstring credits.** I verified
`M-1[nd-*].first_insert` **is** a member of the 4060-candidate covering sweep (it falls out of
`rel[:3] + "*"`) and is asserted refused there. And over the *whole* accepted set from my own sweep —
572 accepted M-1 patterns — **zero** reach a silent proper subset: 50 reach exactly 1, 5 reach all
10, 517 reach 0. The invariant holds; the docstring simply overstates what the invariant *tests*.

**Ruling: claim 9's measurement REPRODUCED, its honesty claim OVERSTATED.** Behaviour is correct and
coverage exists, so this does not affect fitness. It is a **prose defect** in
`test_compare_m1_m6.py`: the invariant arm should say it is a *necessary condition over the accepted
set*, not "the point of the narrowing", and should name the covering sweep as the arm that catches
under-refusal. **I did not repair it** (ruling 3). It belongs to whoever next touches that file, and
it will void this grade when it does — which is correct.

---

## 8. THE SELECTOR GRAMMAR AS GRADED — THE TRANSCRIPTION TABLE

Enumerated by **running** `bad_pattern` at `5dc92487`, not by reading it. This is graded behaviour,
not intent, and it is what `m1m6_expected_differences.json`'s prose note may be written from under
§12.1. Reach figures are over `measure_m1_m6.M1_FILES` (**10** files) as of `fb44fb56`.

### ACCEPTED — 773 of my 115160, in exactly three shapes

| shape | example | reaches today |
|---|---|---|
| `M-k.<literal field>`, k ∈ {3,4,5,6} | `M-4.behind`, `M-3.rc`, `M-6.present` | that one field |
| `M-1[*].<literal field>` — the bare per-file wildcard, **the only wildcard form left** | `M-1[*].first_insert` | **all 10 files, visibly maximal** |
| `M-1[<exact literal file path>].<literal field>` | `M-1[nd-unfolding/unified_throw_cov.py].first_insert` | **exactly 1 file** |

No accepted pattern contains a `*` anywhere except as a whole selector. No accepted pattern targets
`M-2`. **No accepted pattern reaches a silent proper subset of files** (measured over all 572
accepted M-1 patterns: 1, all, or none — never in between).

**Disclosed residual, pre-existing and deliberate:** a literal that names a file or field which does
not exist is **accepted** and reaches nothing (`M-1[nd-unfolding/no_such_file.py].first_insert`,
`M-1[nd-unfolding/bootstrap_nd.py].pres`, `M-1[?].first_insert`, `M-4.behin`) — 517 of the 773.
The suite states this scope explicitly and correctly: such a row is "legitimate and is surfaced by
`expected_entries_unused`, not refused." **It is a report, not a refusal**, and the narrowing does
not change it — but a reviewer now instructed to "name the exact file" can typo one and get a dead
whitelist row that reads as live cover. Behaviour identical at `68b4af12` and `5dc92487`; recorded
for Joseph, not a defect in this change.

### REFUSED — NEW IN `63262a3a`

| shape | examples | reason the guard prints |
|---|---|---|
| **any `M-1` selector containing `*` that is not exactly `*`** — prefix-star, star-suffix, star-in-the-middle, `**`, or padded | `M-1[nd-*].present`, `M-1[nd-unfolding/unified_throw_cov*].first_insert`, `M-1[*_5d.py].n_after`, `M-1[nd-unfolding/b*_nd.py].literals`, `M-1[**].first_insert`, `M-1[ * ].first_insert` | *"the selector '…' is a PARTIAL wildcard. Inside M-1[…] exactly two forms are legal: the bare '\*', which is visibly EVERY file, or ONE exact literal file path. A partial is neither — it reads as one file, can already cover several, and its reach moves silently when the measured file population changes. Name the file, or use '\*'."* |

42224 patterns in my population; **4060** in the producer-derived sweep, of which **210** already
reach more than one real file today and **3850** reach exactly one and are refused for the same
forward-looking reason `M-4.behin*` already was. A partial carrying *also* a field wildcard prints
the **field-wildcard** reason instead (38976 patterns; §6).

### REFUSED — UNCHANGED FROM `68b4af12`, populations byte-identical in size

Unclosed selectors (**D-3**, 18342, e.g. `M-1[*`); no measurement id (58); bare measurement id (6);
`M-1` without a selector (4); empty selector (3); no `.` after `]` (1646); `[...]` on any
measurement but `M-1` (966, including `M-6[*`); no `.` after a block id (10); empty field name (828);
**any `*` in the terminal field name** (50266, including `M-4.*`, `M-4.head*`, `M-3.*x`, `M-4.*e*`,
`M-4.behin*`, `M-1[*].*`); **anything targeting `M-2`** (33); the empty string and non-strings (1);
plus the `matcher_disagreement` backstop, which remains unreachable through `bad_pattern` by design
and is exercised directly by its own arm.

---

## 9. ONE PRE-EXISTING FIGURE THAT DOES NOT REPRODUCE (INHERITED, NOT INTRODUCED)

`test_compare_m1_m6.py`'s `test_a_wildcard_in_the_FIELD_NAME_is_refused_even_when_it_narrows_today`
docstring states: *"Measured 2026-08-25: 265 of 721 generated candidates are refused although they
reach exactly one field name."* I cannot reproduce 265 under either natural reading: candidates that
are refused **and** reach exactly one field name = **301**; candidates that are refused **and** are
not `over_broad` = **360**. `265` is instead the number of the 721 candidates that are **accepted**.
Identical at `68b4af12` and `5dc92487`, so this is **inherited from the previously-graded file and
not introduced by `63262a3a`** — it does not bear on this verdict. Flagged because it survived the
prior grade, and because a mislabelled number in a docstring is exactly the class that grade
withdrew three figures for. **Do not cite "265 of 721". Reported, not repaired.**

---

## 10. F-14 / §7.0.7

`generate_manifest.py --check` in a **clean detached worktree** at `63262a3a`, `git status
--porcelain` **0 lines**:

```
rc=0
OK: docs/orchestration/MANIFEST.tsv; rows=532 ARCHIVAL=106 DEAD=1 LIVE=73 MACHINE=352
    overrides=94 defaults=438 tracking=tracked:532
```

**Claim 12 reproduced exactly** — digests, `rc=0`, `rows=532`, and 81 tests OK at the committed sha.
This document's own F-14 obligation is discharged in the commit that lands it, with `--check` re-run
in a clean detached worktree at that sha.

---

## 11. EXPIRY — MECHANICAL

**This grade expires automatically, with no notice and no judgement call, when any of these three
content digests moves.**

| path | content sha256 (full) |
|---|---|
| `docs/orchestration/compare_m1_m6.py` | `5dc92487bd5c2f6a82d2d4ba51ccd57fa73abeac6eb836ab0343e95206595301` |
| `docs/orchestration/test_compare_m1_m6.py` | `762fac146baee3507a8baaabf3febad157eb9ab236517b32ec5f98db5fba9432` |
| `docs/orchestration/measure_m1_m6.py` | `0fcd90f7c92a7071208e62d09ebc38956f1a83b11af41a469b4886a6e6786d79` |

```bash
sha256sum docs/orchestration/compare_m1_m6.py \
          docs/orchestration/test_compare_m1_m6.py \
          docs/orchestration/measure_m1_m6.py
```

Any mismatch ⇒ **this grade is void and the instrument is UNGRADED again.** `measure_m1_m6.py` is
pinned although it was **not** graded, because every reach figure in §4, §7 and §8 is computed over
its `M1_FILES` and the row keys `flatten` derives from its output: change the file population and
the `unified_throw_cov` prefix collision, the `nd-*`-reaches-10 measurement and the 4060/210/3850
split all describe a world that no longer exists. **Two of the three digests pinned by the
predecessor grade had already moved when I began** (§0.1), which is what an expiry is for and why a
reader must run the command above before relying on a word of this document.

**`m1m6_expected_differences.json` is deliberately NOT an expiry pin.** Its digest `92091ae8` is an
as-of referent; §12.1 requires it to change when the prose note is transcribed from §8, and that
change must not void this grade. `56c2e0ef` remains the historical referent. **Do not add a partial
selector to it** — that is now enforced by the guard rather than by the note.

---

## 12. WHAT I DID NOT DO, AND WHERE I MAY BE WRONG

- I graded the **selector narrowing** and its blast radius on the pattern guard. I did **not**
  re-grade citation resolution, the exit vocabulary, tolerance evaluation, the record schema, the
  far-end script, or `measure_m1_m6.py`. I did not carry the prior grade's conclusions forward on
  those; it is void.
- I ran the comparator only against the suite's own bench fixtures and against the **shipped**
  expected list. **I ran no comparison producing a Gate-2-relevant verdict and consumed no product
  of run `k0-aa67c426-20260824T145751Z`** — I did not even open the filed record.
- My reach figures use `M1_FILES` as the file population, as the expiry pin says. If the far-end
  tree's real files differ from that tuple, the specific counts (10, 2, 210/3850) differ; the
  mechanism does not.
- **My 115160-pattern population is mine and is not exhaustive over strings.** It is a covering
  sweep by construction (truncations of everything, plus all three star placements over every real
  path), and it found the same shape the implementer reported on a 24× larger denominator — but a
  spelling I did not generate could in principle behave differently. The structural argument in §3
  (the only executable change is one *added* refusal branch) is what makes `newly accepted = 0`
  robust to that, and it is why I state both.
- **Four claims are overstated and I did not fix any of them** (claims 1, 6, 9, 11, plus the §4
  degenerate assertion and the §9 pre-existing figure). Under ruling 3 that is the correct
  behaviour, but it means the instrument ships with prose that misdescribes its own reasoning in two
  places. §7 is the one Joseph should actually read.
- **On the framing of my assignment.** I was asked to say if the dispatching lane biased me. I do
  not think it did, and the precise reason matters more than the courtesy: the brief named its own
  disqualification, listed the traps most damaging to its preferred outcome, told me to run both
  negative controls myself, pre-committed that "not fit" was acceptable, told me the prior grade was
  void **and to verify that rather than assume it**, and relayed claim 8 as a point to *press*
  rather than to confirm. Two elements were slanted and both were self-correcting: it repeated the
  implementer's "nothing previously refused changes even its printed *reason*", which is **false as
  stated** and which its own claim-1 relay contradicts three paragraphs earlier — I would have
  reported a failure had I tested only the strong sentence — and it relayed claim 9 as an honesty
  question ("assess whether the implementation is honest about that") in a form that invited a yes.
  Testing it as a proposition instead of an attitude is what produced §7. I flag both because the
  next grader will be handed the same sentences.
- I am one lane. §5.1's unrecoverable denominator and §9's inherited `265` are the kind of thing a
  second grader should re-run before this document is leaned on.
