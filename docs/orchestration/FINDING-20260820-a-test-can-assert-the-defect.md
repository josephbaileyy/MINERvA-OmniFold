# A TEST CAN ASSERT THE OBSERVABLE THAT *IS* THE DEFECT, WHICH MAKES THE DEFECT A REQUIREMENT OF THE GREEN SUITE

**`BEN-510`.** *(Id ruled by lane C in `VERDICT-20260820-lanec-remedy-a-ROUND2-PASS-WITH-SCOPE.md:103`,
opening the closed ten-block `510-519`. **Freeness re-derived here by the filer immediately before
writing, by BOTH routes against a freshly fetched `origin/main`** — `git grep -ohE 'BEN-51[0-9]'
origin/main` and `grep -rhoE 'BEN-51[0-9]' --exclude-dir=.git .` over tracked AND untracked each
returned **`BEN-510` only, and every one of those occurrences is C's verdict RULING the id or the
control-plane narration of it — zero rows in `FINDINGS.md`**, so the block is unfiled and this filing
claims it. The two routes agreed at **392 distinct ids** with an empty `comm -3`. C measured 391; the
difference is C's own verdict commit introducing the token `BEN-510`, which is a confirmation of the
method rather than a disagreement about it. **`511-519` free — derive it, do not trust this clause.**)*

Related: `BEN-469` (a misfiring guard's message accuses a named file, and the accusation is the
damage), `BEN-040` (a fixture shaped like the consumer rather than the producer makes a fail-closed
gate unfalsifiable), `BEN-485` (two correct rulings compose into a defect), `BEN-482` (a text search
cannot distinguish a claim from prose about the claim).

---

## THE MECHANISM

A test that pins a failure message by asserting **the sentence it contains** has, without anyone
choosing it, made that sentence a requirement of the suite. If the sentence is later found to be
*wrong* — misleading, accusatory, or simply false — then **the fix cannot be applied without deleting
or editing an assertion, and until that edit is made the suite is red in defence of the defect.**

The green suite is supposed to be the thing that tells you a change is safe. Here it says the
opposite of what it means: it goes red on the repair and stays green on the damage.

## THE INSTANCE, VERIFIED FROM THE DIFF BY LANE C

Remedy (A)'s wrapper, `nd-unfolding/mii_adopt_unified_5d_stamped.py`. Its TOCTOU closure
(`assert_diag_matches_sqrt_tr_old`) refused, and its refusal ended:

> *The combined intermediate is not the matrix this product was built from.*

That is `BEN-469`: a false corruption report aimed at the **41.44 GB combined intermediate**, the one
artifact in this campaign that costs **~2.087 TiB** to regenerate — and the D1 coercion defect made
that message the wrapper's **default output on every real product**.

The two sides, both read off the diff rather than relayed:

| sha | the assertion |
|---|---|
| `59987fea` | `assertIn("not the matrix this product was built from", ...)` |
| `be7aec21` | `test_a_DISAGREEMENT_is_refused_WITHOUT_BLAMING_AN_INPUT_FILE`, `assertNotIn` on that identical string |

**So the accusatory wording was literally a requirement of the green suite.** Fixing D1's second half
was impossible without deleting an assertion, and a reviewer looking only at test results would have
seen the repair break the build.

## IT FIRED AGAIN DURING ITS OWN FILING, WHICH IS THE PART WORTH READING

Round 3 closed lane C's Q3(a) residual: `NOTHING HAS BEEN WRITTEN` is **true of the stamp and false of
the product** — the child has already run and `--out`, an ~892 MB adopted root, exists unstamped. A
reader who believed the sentence would go looking for a file that is already on disk.

`test_the_REFUSAL_DOES_NOT_ACCUSE_THE_41GB_INTERMEDIATE` asserted `assertIn("NOTHING HAS BEEN
WRITTEN", msg)`. **Correcting the false sentence turned that test red, in the same session that was
filing this finding about that exact shape** — three test failures, all of them the fix, none of them
a regression. The replacement asserts that the message does **not** claim nothing was written and
**does** say what exists, which is a property; the comment at the site records why the line changed so
the next reader does not read the edit as a weakening.

Two independent fires inside three rounds on one file is what makes this a mechanism and not an
anecdote.

## WHY IT IS NOT `BEN-469`, AND THE DISTINCTION IS THE USEFUL PART

Lane C drew it and it is worth keeping verbatim in shape:

- **`BEN-469` asks, at WRITE time: "what does my message ACCUSE, and what would a reader DO about
  it?"** It is about the content of a diagnostic when a guard misfires.
- **`BEN-510` asks, at FIX time: "does any test assert the observable I am about to change?"** It is
  about the suite's grip on that content, and it applies to any observable — a message, an exit code,
  a printed table, a filename — not only to accusations.

They compose: `469` tells you the message is wrong, `510` tells you why fixing it will look like a
regression. A lane that knows only `469` files a correct finding and then hesitates over a red suite.

## THE CHECK TO CARRY

> **Assert the PROPERTY a failure message must have. Never the SENTENCE it must contain.**

Properties that have done real work in this file, all of them derived from live operands rather than
typed twice:

- the message must **not** contain the old accusation (`assertNotIn`) — a *safety* property;
- this wrapper must be the **first** cause listed (an ordering, checked with `index()` comparisons);
- the do-not-delete banner must be **present**, with its two operands;
- a caveat naming a test double must name it by **`_FakeROOTModule.__name__`**, so renaming the class
  fails the test instead of quietly rotting the paragraph;
- a discriminator must be **offered** for the expensive cause, and must not itself name a write.

And the operational half, which is cheap and was skipped twice:

> **Before changing an observable, grep the suite for it.** If a test asserts it, decide whether that
> assertion pins a *safety* property (keep it, point it at the new form) or pins the *defect* (delete
> it, and say in the diff that you did). Do not discover the answer from a red run.

## THE RESIDUAL, RECORDED HONESTLY

**Round 3's new tests still assert substrings.** They pin a *safety* property rather than a defect —
the accusation must be **absent**, the banner **present** — which is the legitimate direction and is
the form C accepted. But it is **the same brittleness pointed somewhere better**, and a future
reworder of these messages will again have to edit tests. The distinction that matters is not
"substring vs no substring"; it is **whether the string being asserted is one you would defend**. An
assertion that the accusation is gone is one I would defend. An assertion that a particular wording is
present is not, and three of them are still in this suite.

A second residual in the same family, found while fixing the first and worth naming because C did not
cite it: the wrapper's `:43` caveat was false, **and the test file's own module docstring carried the
identical false sentence.** C cited the line it had measured. The mechanism does not care which file
it is in, so both were corrected and the pinning test checks both. **A caveat is a claim**, and a
stale claim about what is *not* established is the most load-bearing kind to get wrong: it overstates
the suite in the direction that flatters it.

## MEASURED

- `tests/test_remedy_a_adopt_wrapper.py` + `tests/test_uq_remediation.py`: **303 passed / 2 skipped**
  (both skips pre-existing), up from 283/2.
- `tests/mutation_probe_remedy_a.py`: **23/23 CAUGHT**, every row naming a failing test. The seven new
  mutations include `D8` (revert to `NOTHING HAS BEEN WRITTEN`) and `D11` (put the *no double* denial
  back) — i.e. **both halves of this finding now have a mutation that would catch a regression**, which
  is the only form in which a finding like this stays true.
- The probe's own criterion was corrected from `CAUGHT if rc != 0` to **"a NAMED test failed"** (lane
  C's caveat), with `--self-test` proving the new `UNATTRIBUTED` branch fires: an import-breaking
  mutation returns `rc=2` and names nothing, and **under the old criterion that would have counted as
  caught.**
