# A regex over source cannot tell a call from prose *about* a call — and the lint that demands the explanation is the one that punishes it

**Lane B, 2026-08-18. `BEN-482`.** Two instances in one turn, in two different codebases, both firing
on comments written to explain a real defect. Fixed at `aae49f2a`.

---

## THE ONE PARAGRAPH

A text matcher's corpus is *the file*. Its author's corpus is *the code*. Those differ by exactly the
comments, and **nothing in the output distinguishes them** — a scraped English word arrives looking
like an identifier. The asymmetry that makes this self-reinforcing: **the better the comment, the
likelier the misfire, because a good comment names the construct it is about.** So the pressure a
false positive creates is to *stop explaining*, which costs precisely what this ledger exists to
preserve.

---

## 1. The two instances

**(1) The repo's own lint, and it punished its own remedy.**
`nd-unfolding/tests/test_resume_guard.py:test_every_guarded_output_has_a_producer_stamp` reported:

    nd-unfolding/lib_member_resume.sh: guarded but never stamped: ['and']

`'and'` is the **English word**, scraped by `rg_skip_if_complete\s+"?([^"\s]+)"?` out of:

    # through to rg_skip_if_complete and was ACCEPTED on size and mtime. Member 0 could be handed the

— a comment explaining a resume defect, **in a resume library**. The lint's own docstring justifies
itself by saying an unstamped guard *"silently burns the allocation"*; the comment it choked on
documents an identity-resume hole that had **already handed member 0 the published archive**. That is
the comment the lint's rationale asks an author to write.

**(2) My own test, minutes earlier and independently.**
`assertNotIn("require_completeness=False", src)` — intended to assert that `load_flat` no longer skips
the completeness gate — failed **on the comment I had just written explaining why the flag was
removed**. Same shape, opposite polarity: instance (1) is a positive match on prose, instance (2) is a
*negative* assertion defeated by prose.

**Neither is a corner case.** Both were the first execution after the change.

## 2. The remedies are two, and they are not interchangeable

| language | remedy | why not the other one |
|---|---|---|
| Python | **parse it** — walk the AST, find the call, read its keywords | a comment is not in the tree, so the question cannot arise |
| shell | **strip full-line comments** (`_strip_full_line_comments`) | no cheap parser; `bash -n` validates syntax without exposing a token stream |

The Python remedy is `BEN-249`'s remedy for line-number citations **arrived at from the other
direction**: there the fix was to pin on *content* rather than a line number; here it is to read
*structure* rather than text. Both replace a positional/textual handle with a semantic one.

The fixed test walks `load_flat`, asserts it delegates **exactly once**, and reads the actual
keywords — so it now checks `require_completeness is True` and `min_complete == 0.0` as *values*,
which the substring form could not have done even when it worked.

## 3. THE HALF-MEASURE IS THE DANGEROUS ONE, AND IT IS THE OBVIOUS ONE

The instinct for the shell case is to strip from the first `#` to end-of-line. **That corrupts real
code.** `nd-unfolding/lib_member_resume.sh:126`:

    head="${p%%/nd-unfolding/*}/nd-unfolding"; tail="${p#*/nd-unfolding/}"

The `#` is **parameter expansion**. Cutting there silently shortens a line the lint exists to read —
**trading a false positive for a false negative, which is the wrong direction for a guard.** Worse,
it is undetectable from the lint's output: the line still parses, the truncated remainder simply
stops being scanned.

So the strip is **full-line only**: a line whose first non-whitespace character is `#`. That covers
both instances above (each was a full-line comment block) and cannot reach a code line. A trailing
comment on a real call — `rg_skip_if_complete "$out" "$@"     # no marker: not complete` — survives
intact, and its call is read correctly, which is the case the naive strip would have handled by luck.

## 4. And the narrowing gets a test that it STILL FIRES

A filter that removes false positives can strip everything and **pass vacuously forever**. A lint that
cannot fail is worse than an absent one, because it reports green.

`test_the_comment_strip_did_not_BLIND_the_stamp_lint` plants a genuinely unstamped guard beside a
prose mention and requires **the real one caught and the prose one gone**.
`test_the_strip_preserves_parameter_expansion_containing_a_hash` pins §3's false-negative direction.

This is `a-filter-needs-a-test-in-the-direction-it-acts` applied to a **narrowing** rather than a
guard: a guard gets a test that it *fires*; a narrowing gets a test that it does **not** — or widening
it later looks free.

## 5. Relation to `BEN-480` / `BEN-481` — inversion, not repetition

| row | the detector's blind spot | sign |
|---|---|---|
| `BEN-480` | power test assumed the guarded logic was textually **contiguous** | sees too little |
| `BEN-481` | power fixture was **monolingual** while the walk was not | sees too little |
| **`BEN-482`** | matcher reads **comments** as code | **sees too much** |

**Same root, opposite sign.** In all three the corpus a text matcher actually runs on is not the
corpus its author had in mind, and in all three **nothing in the output distinguishes the two** — the
green looks like the green, and the finding looks like a finding. `BEN-481` closed the
*conformance/discovery* split for a detector's own power; this closes it for the detector's *input*.

**Prediction, offered so it can be checked rather than assumed:** the next instance is a matcher over
**generated** or **vendored** code, where the corpus differs from the author's mental model not by
comments but by provenance. I have an unfiled observation that `test_resume_guard.py`'s own corpus
excludes `lib/` by an early `continue` — which is why `lib/resume_guard.sh`, the file that *defines*
every symbol the lint scrapes, is never scanned. Not yet an instance; recorded as the next place to
look.

## 6. What this does not claim

- **Two instances, not a census.** I have not swept the repo for other text matchers with the same
  exposure, and I should not be read as saying there are only two. `BEN-481`'s history is directly
  relevant here: I previously had `n=2` and reached for a structural law that measured false.
- The `aae49f2a` fix is to **one** lint. Other `test_*.py` files scrape shell with bare regexes.
- The suite reads 1756 pass / 4 skip / 3 fail, and **all three remaining failures reproduce at the
  pre-change baseline `8e48a811`** in a detached worktree — measured, not assumed.
