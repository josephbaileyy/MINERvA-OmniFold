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

---

## 7. AMENDMENT, SAME DAY — A THIRD INSTANCE, AND I HIT IT WHILE THE ROW WAS BEING WRITTEN

**The third instance is this document's own remedy failing to be applied to this document's own
follow-up work.** Hours after filing §§1–6, the mediator found that
`launcher_argv_probe.py:452` used

    member = [o for o in outs if "member_k" in str(o)]

which is **true of both path shapes** — `uq_5d/.../member_k001200/x` and
`mii/member_k001200/uq_5d/.../x` — so the probe re-run C ordered *specifically to confirm
member-root-first* **could not distinguish it from what it replaced**, and returned byte-for-byte the
same summary as the pre-change run. I replaced it with a `startswith` shape test and then wrote:

    self.assertNotIn('if "member_k" in str(o)', src)

**which failed, because the new function's docstring quotes the old predicate verbatim** — deliberately,
so the next reader can see what was replaced. **The grep could not tell the retired predicate from the
explanation of its retirement.** Third time in one turn, in the work whose entire subject is this
mistake.

**A NEW GENERALISATION, and it is a different claim from §1's:** *a substring test cannot express a
POSITIONAL requirement.* §1 was about a matcher reading the wrong **corpus** (comments as code). This
is about a matcher whose **relation** is too weak for the claim: containment is the one relation blind
to order, and the requirement was *"the member root comes first."* Two distinct failure modes for one
tool, and the fix differs — §1's is *parse instead of grep*, this one's is *pick the right predicate*.
Both were satisfied here by parsing, which is why they were easy to conflate.

## 8. AND THE FIX'S FIRST FORM WAS TOO BROAD, WHICH IS ITS OWN LESSON

The AST assertion I wrote to replace the grep banned **any** `"member_k" in ...` containment in the
file. It failed — on a **legitimate** one at `:458`, inside `is_member_scoped` itself, where
containment is **not** the acceptance predicate (acceptance is `startswith`) but only **refines the
rejection reason**: *"contains a member component but in the wrong position"* — the shape C reversed —
versus *"not member-scoped at all."* Those are different defects with different fixes and collapsing
them makes the diagnostic worse.

**So the requirement is not "containment appears nowhere" but "containment is not the acceptance
predicate",** and the test now says exactly that: exactly one containment inside the classifier, zero
in every other function. **A blanket ban would have forced me to delete a better error message to
satisfy a test.** That is the shape of over-broad assertion that teaches people to weaken checks, and
it is worth naming beside the under-broad ones this row is otherwise about: **a check can fail by
demanding too much just as readily as by seeing too little, and the second failure mode is the one that
gets checks deleted rather than fixed.**

## 9. What the amendment does not change

The mediator's conclusion that the implementation **is** member-root-first stands, but it rests on its
own **behavioural bash read** of `mr_prefix` — not on the probe pass, which was invalid evidence for
placement in both directions. It said so itself and asked for the distinction on the record. **The
probe now prints every observed path**, because a passing run's log contained no path at all: 36 lines,
zero occurrences of `member_k` or `mii/` outside the summary counts, so nothing downstream could audit
what had passed. A verdict-only receipt is unfalsifiable (`CONVENTION-receipt-ingredients.md`); the
paths **are** the ingredients of `namespaced=N`.
