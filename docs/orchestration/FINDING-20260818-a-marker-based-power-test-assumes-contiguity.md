# A marker-based power test assumes the logic it guards is TEXTUALLY CONTIGUOUS — and refactoring for testability is what breaks that

**Lane B, 2026-08-18. Read-only analysis of a diff I applied (`20518416`); every operand re-derived
against the fetched remote. Nothing run.**
**AWAITING A BEN ID: lane B's blocks `100-129` and `240-249` are fully allocated (derived tracked and
untracked immediately before writing this). A block has been requested from the mediator. Indexed in
`FINDINGS.md`'s long-form table so it is readable before it is numbered — an unindexed finding is one
nobody reads, and that is how nine of them sat orphaned until 2026-08-06.**

---

## THE ONE PARAGRAPH

A **power test** proves a static assertion can fail, by reconstructing the pre-fix source and requiring
the assertion to fail on it. The common implementation excises a text region between two markers.
**That implementation assumes the guarded logic lives in ONE contiguous block — and the standard way to
make a guard testable is to move its value somewhere a test can reach, which puts the logic in two or
three places.** So the technique degrades exactly when someone improves the thing it guards.

**The design rule, which is the filable part: assert on MORE THAN ONE token.** Lane D's test failed
**loudly** only because it asserted on two. A single-token version would have gone on passing while
controlling nothing.

---

## 1. The instance

`nd-unfolding/tests/test_uq_remediation.py::Cause6ProjectionCoverageTests::test_the_prefix_source_would_fail`
reconstructs a pre-`BEN-450` `eavailW_covariance.py` by partitioning on a comment marker
(`# BOTH DIRECTIONS (added 2026-08-11, quarantine cause 6).`) and cutting to a known following line
(`    fs = ROOT.TFile.Open(args.stat5d)`), then asserts two tokens are absent from the remainder:
`_ew_empty` and `Mew.any(axis=1)`.

**Applying `BEN-450`'s repair broke it twice, both times for correct reasons:**

| break | why | where the token went |
|---|---|---|
| `_ew_empty` still present | **propagation** puts the value in a second place *by design* | the `write_ew_outputs(...)` call in `main()` |
| `Mew.any(axis=1)` still present | the **single-source helper** puts the computation in a third | `ew_coverage_report()`, above `main()` |

**Neither location is inside a marker-based excision of the guard block, and neither could be** —
propagation exists to carry the value *away* from the guard, and the helper exists so the value has one
source a test can bind to. **The two refactors most likely to be required by "make this testable" are
exactly the two that defeat contiguity.**

## 2. Why it is a property of the technique, not a defect in the test

D's test is a good one and it did its job: it went red, immediately, on the same commit as the
refactor. The failure mode being described is the *other* case. **Excision keys on text; the invariant
being guarded is behavioural.** As long as the behaviour lives in one block those coincide, and the
first time the behaviour is factored they diverge — **with no signal, because a text search over a
region that no longer contains the token returns exactly what a correct pre-fix source would.**

**THE DISCRIMINATING DETAIL: TWO TOKENS, NOT ONE.** With `n` asserted tokens, the test survives a
refactor only if *all* `n` migrate out of the excised region. D's asserted two, they migrated one at a
time, and each migration produced a red test. **Had it asserted only `_ew_empty`, the first refactor
would have moved it, the assertion would have passed on a source that still contained the guard's
computation, and the power test would have silently stopped being one.** So the rule is not *avoid
markers* — it is **assert on several tokens, or key on something structural (an AST node, a call site)
rather than on text.**

## 3. My own mistake inside the repair belongs in the same row, one layer down

Extending the excision, my first attempt **deleted** the line carrying the propagated argument
(`        (_ew_empty, _n_ew_empty))`). That line sits inside a multi-line call, so deleting it left an
**unclosed parenthesis** — and:

**THE ASSERTIONS WOULD HAVE PASSED.** `assertNotIn("_ew_empty", prefix_src)` is true of mangled source.
The reconstruction was no longer a Python program, and every token-absence assertion in the test was
satisfied *because* it had been mangled.

**It was caught by `ast.parse(prefix_src)` — a guard D had already written into the test for exactly
this, whose docstring says so:** *"it must still be valid Python, i.e. the reconstruction is a real
pre-fix source and not a mangling that would fail the assertions for the wrong reason."* **A test suite
that passes on unparseable source is this same failure at the next layer down, and the only thing
between the two was somebody else's earlier caution.** The repair is **substitution, not deletion**:
the argument is replaced with `(np.array([], dtype=int), 0)`, which removes the token and keeps the
call closed.

## 4. The family, which is why this is a row rather than a paragraph

**Four instruments in one evening that EXECUTED SUCCESSFULLY AND WERE BLIND** — the through-line is
lane D's formulation and the fourth member is this one:

| instrument | executed | blind because |
|---|---|---|
| a substring-absence check over a corpus | returned a clean number | the corpus excluded the members that mattered (`BEN-235`'s family) |
| the static cause-6 test | asserted the value was computed and named | **deleting both `print`s left it green** — it never asserted *reporting* (`BEN-450`) |
| the concordance's rendered table | enumeration complete and correct | the **render** printed 3 of 6 citers as basenames plus a count |
| a marker-based power test | went red on refactor | would have gone **green** on a single-token variant, controlling nothing |

**And a fifth, mine, measured the same evening:** a citation check comparing **counts** rather than
`(file, line)` pairs. Baseline `26e4e343` → the gate-1 commit `3dd5e66e`: **`103 → 103`, a delta of
exactly ZERO, while 38 of 50 cited lines rotted and 10 went extinct.** It reports faithfully and cannot
move.

**D's pairing is the lesson and it is better than the list: `BEN-450` is detection without propagation;
a count-based check is propagation without detection. Both green, both worthless. "The check ran and
reported" is silent about both halves — ask separately whether it can SEE and whether anyone can HEAR.**

## 5. What to do differently, concretely

1. **Assert on several tokens in a power test**, so a partial migration is loud. One token is a coin
   flip on whether the test survives its own subject being improved.
2. **Prefer a structural key** — an AST node, a specific call site — over a comment marker. A marker is
   a citation into source, and `BEN-249` already says what those do.
3. **Always keep the `ast.parse` arm** on any test that reconstructs source. It is the only thing that
   distinguishes *the assertion failed* from *the input stopped being a program*.
4. **When you excise inside an expression, SUBSTITUTE, do not DELETE.**
5. **When a power test goes red under a refactor, do not repair it silently.** Its excision model has
   just told you something about the code's shape, and the next person will hit the same wall.

**Attribution: the test, its `ast.parse` guard, the `BEN-450` specification and the
detection-vs-propagation pairing are lane D's. The contiguity result, the two-token discriminator and
§3 are this lane's. The mediator asked for it to be filed and named the fourth-instrument through-line.**
