# For "does X call Y", the text is not the program

**Date:** 2026-08-16 · **Lane:** `standard-p4-verifier` (repair-10, repair-11), block `330-339`
**Row:** `BEN-335` · **Nearly inverted repair-11's verdict**

---

## The instance

repair-11 turned on whether `projection_M_from_recipe` is a genuinely independent reconstruction of
the projection matrix, or a re-execution of the function it is supposed to check. If it delegated to
`build_projection_M`, the recipe gate would compare a function against itself — **the exact defect
this lane retired an `OI-120(c)` probe arm for the same week** — the wrong-`M` property would be
unestablished, `B1` would be unmet, and the verdict would have been `BLOCK`.

Measured at `13f9e0a`, both instruments over the same function body:

```
grep -c build_projection_M   (over the function's source range)   ->  2
ast walk, Call nodes only                                         ->  0
```

**Both hits are docstring mentions** — the docstring says *"the matrix `build_projection_M` builds"*
and *"Kept deliberately free of `build_projection_M`'s helpers"*. The second one is describing the
absence of the very thing the grep counted as its presence.

**The grep answer was 2 and the true answer is 0.** Reported as delivered, it establishes delegation,
which is a `BLOCK`. `authorizes_covariance_stages_4_6` would have been `false`, and the repair would
have been sent back to fix a defect it did not have.

## The general form

> **For "does X call Y", the text is not the program.** A textual hit is not a call: it may be a
> docstring, a comment, a string literal, a different function in the same file, an import that is
> never used, or — as here — **prose asserting the very absence being tested for**.

The remedy is not a better regex. It is a different instrument:

```python
fn = next(n for n in ast.walk(ast.parse(src))
          if isinstance(n, ast.FunctionDef) and n.name == TARGET)
calls = {ast.unparse(n.func) for n in ast.walk(fn) if isinstance(n, ast.Call)}
```

`ast` answers the question actually asked — *what does this function invoke* — and is immune to every
one of those confusions. It costs four lines.

## Why this is not `BEN-344`, and the distinction is the useful part

`BEN-344` is **a null that could not have been otherwise**: a measurement returning nothing because
nothing could make it return something. Its remedy is *show the instrument capable of firing.*

**This is the mirror image: a POSITIVE hit that is not the thing it appears to be.** `BEN-344`'s
remedy does not catch it — the grep *can* fire, *does* fire, and fires on the wrong thing. Requiring
it to demonstrate non-nullity would have confirmed it, not exposed it.

> `BEN-344`: the check cannot fail, so its silence means nothing.
> `BEN-335`: the check fires, and its noise means something else.

Both are text instruments answering questions about program structure. Together they cover the two
directions in which that substitution fails.

## The same failure is already sitting in this campaign, from the other side

`R11-1` — filed by this lane in repair-11 — is the wiring guard
`self.assertIn("check_projection_matrix_matches_recipe", src)`. **It accepts a commented-out call as
evidence of wiring.** That is this row's failure with the polarity reversed: there, text-present is
read as call-present and the reading is too generous; here, text-present was read as call-present and
the reading was too damning. **One instrument, one substitution, two opposite wrong answers in the
same verdict.**

That is the argument for treating it as a class rather than two incidents, and it is why lane B's
proposed fix for `R11-1` — an **execution witness** carrying `nnz > 0` and `entries_differing == 0`,
numbers a commented-out call cannot produce — is the right shape. **Where `ast` is unavailable or the
question is "did it run" rather than "does it call", the answer is a number the absent behaviour
cannot manufacture.**

## What gave it teeth, and what did not

**What caught it:** reading the two hits rather than counting them. Nothing systematic — the count was
suspicious only because `2` is a strange number of times to call a helper you claim not to use.

**What did NOT catch it:** the whole apparatus this campaign has built. `BEN-344`'s remedy would have
confirmed it. `falsified_by` would have been written as *"an AST/grep hit showing delegation"* and
satisfied by the grep. The predeclared bar `B1` did not name an instrument. **A verdict discipline
that specifies what must be established but not what may establish it leaves the instrument choice
unexamined**, and the instrument is where this one lived.

## Scope

* One instance, one function, one verdict. No claim about how often grep-for-a-call misleads here.
* The remedy is specific to *"does X call Y"* within a **Python** file. It does not extend to the
  shell drivers, where there is no AST and the honest instrument is execution.
* This row does not revisit repair-11's `PASS`; the AST result is what that verdict recorded and acted
  on, and the grep was caught before the verdict was written, not after.
