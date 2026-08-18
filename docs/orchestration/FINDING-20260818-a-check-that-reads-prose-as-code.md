# Seven instrument defects in one session, one family, and the remedy was wrong three times

**Lane E, 2026-08-18. `BEN-418`.** Every negative control I wrote this session that asserted a token was
ABSENT from some code failed, at least once, on prose that *mentioned* the token while explaining why the
code does not do the thing. Seven instances. What makes this worth a finding is not the count — it is that
**the remedy I adopted after each instance was itself wrong twice more**, in a way that was invisible until
the next instance.

## The sequence, with what each one refuted

| # | the check | what it matched instead | remedy adopted |
|---|---|---|---|
| 1 | `OI-96`'s field-pin coverage grep | prose-only receipts describing pins | strip comments |
| 2 | the `P5′`-locality control | the block's own explanatory comment | strip comments |
| 3 | the anti-tautology control | the predicate's comment saying why a leg was **removed** | **use `ast.unparse`, which drops comments by construction** |
| 4 | the `${VAR@Q}` bash control | the comment warning against `${VAR@Q}` | strip whole-line `#` (shell has no AST here) |
| 5 | the `default_rng` control | the function's **docstring** explaining why it must not call it | **`ast.unparse` is not a prose-stripper — `_code_only` strips docstrings too** |
| 6 | the `bootstrap_seed` exclusion control | the function's **return value**: `{283: "the overloaded bootstrap_seed, replaced by F1/F3"}` | **`_reads_key`: ask about ACCESSES, not text** |
| 7 | the pinned `fatal_tokens` extraction | `r"\[[^\]]*\]"` stopped at the `]` inside `"[gate5-train][FAIL]"` | parse, don't bracket-count |

## The three claims, in the order they were learned

**1. Comments are not code, and a grep cannot tell.** The first three instances. Every one matched an
explanation of why the code does *not* do the forbidden thing — which is the text most likely to exist
next to a correct implementation, so the check is *most likely to fail exactly where the code is right*.

**2. `ast.unparse` drops comments but PRESERVES DOCSTRINGS.** A docstring is a string expression, not a
comment. So the remedy from instance 3 — *"use `ast.unparse`, which drops comments by construction"* —
was true and incomplete, and I repeated it as settled after instance 4. The gap is invisible until a
docstring happens to quote the forbidden token, and a docstring explaining a prohibition is exactly the
docstring that will.

**3. A SUBSTRING ABSENCE CHECK CANNOT DISTINGUISH A MENTION FROM A USE.** Instance 6, and it defeats every
prose-stripper by construction: the token was in a **return value** — a dict documenting that a pinned site
is deliberately excluded — which *is* code. No amount of stripping removes it, and stripping it would be
wrong.

> The property anyone actually cares about is **"this function does not read that field"**, which is a
> question about **accesses**, not about text.

`_reads_key(fn, key)` walks the AST for `x.get("key")`, `x["key"]` and `_scalar(x, "key")`. It is
narrower than a grep and it is the thing being claimed.

## The two second-order lessons, which are the transferable part

**A negative-only helper that has never returned True is unverified.** `_reads_key` gets a **positive
control** — `assert_data_only_target_is_this_replicas` *does* read `bootstrap_seed`, so the helper is
shown to fire — because a predicate that has only ever returned the answer you wanted is lane D's third
`BEN-258` category (*live, and never exercised*) wearing a different hat.

**Fix it covering, not locally.** After instance 5 I audited all 13 `ast.unparse` sites in the suite and
found **two more latently vulnerable absence checks**. Neither was failing. Both happened not to quote
their own forbidden token — and *"happens not to"* is not a property anyone maintains. This is the third
time in one session that a covering sweep after a local failure found more than the local failure (the
others: the misplaced `unittest.main()`, 2 more files; the vacuous shell guard, 1 more guard).

## Instance 7 is a different mechanism worth naming separately

`r"\[[^\]]*\]"` over

```python
fatal_tokens = ["Traceback (most recent call last)", "[gate5-train][FAIL]", "SystemExit:"]
```

stops at the first `]`, which falls **inside a string element**. It produced a `SyntaxError` from
`literal_eval` rather than a wrong answer — a loud failure, so cheap. But the general form is the same
mistake as the rest: **a bracket-counting regex over source that contains brackets is the wrong
instrument.** The parser already knows where the list ends. Use it.

## The check to steal

Before writing any assertion that a token is ABSENT from code, ask:

1. **Would the correct implementation's own documentation contain this token?** If it explains a
   prohibition, yes — and your check will fail on correctness.
2. **Am I asserting absence of TEXT or absence of a BEHAVIOUR?** If a behaviour, walk the AST for the
   accesses. Text absence is almost never the property.
3. **Has this negative check ever returned the other answer?** If not, give it a positive control.
4. **Where else in this repo did I write the same shape?** Fix those too, before one of them fails.

**Cross-references.** `BEN-417` (a green verdict over a silently smaller population — same session, the
subject rather than the instrument), `BEN-258` amendment 1 (a live guard that has never fired is
unverified), `BEN-416` (*it is written* and *it has run* are different claims), `BEN-423` (a comparison is
evidence only if its two operands came from independent routes — instance 6's control exists to keep a
tautology from returning).
