# BEN-345 — a guard that could not be observed in the environment it was written for, and the six things that fell out of finally observing it

**Date:** 2026-08-16 · **Lane:** B · **Subject:** `nd-unfolding/tests/conftest.py`, repair-10 defect `N6`
**Index row:** `docs/orchestration/FINDINGS.md`
**Receipt:** `docs/orchestration/state/RECEIPT-20260816-n6-tmpdir-guard-observed.json`

---

## The shape

`N6` was carried through **three consecutive verifier rounds** with the same sentence each time, and
the sentence was honest:

> *the guard is inert wherever a writable tmpdir exists, which is the condition this round also had
> to create in order to execute the suite at all, so this round could not exercise it either.*

That is a correct observation and a **false conclusion**, and the gap between them is the finding. It
is true of the *process running the suite*. It is not true of a *subprocess* — which can be given a
manufactured `sitecustomize.py` on `PYTHONPATH` that breaks temp-directory creation before pytest,
before conftest, before anything. The deadlock was in the framing, not in the environment.

**Generalisation:** *when a guard's precondition contradicts the precondition for running the test
suite, the answer is a second process, not a caveat.* Three rounds of "could not exercise it" cost
more than the ~90 minutes this took, and each round wrote the impossibility down as though it were a
property of the world.

Filed alongside `BEN-344`: a check nobody has ever seen fire is in the same category as a null that
could not have been otherwise.

---

## What running it actually found

The point of doing this was to close a hygiene item. Six substantive things came out instead, and
**four of them corrected something I had just written**.

### 1. The largest miss was the one stratum that produces ERRORS, and it was completely unguarded

Detection read the **test function's own source** for the string `TemporaryDirectory`. Measured over
the real suite (1465 collected items) with the guard forced on:

| stratum | items | how it breaks | was it detected? |
|---|---|---|---|
| pytest `tmp_path` / `tmpdir` / `tmp_path_factory` fixture | **171** | **ERROR** (setup phase) | **no — fixtures were never looked at** |
| tmpdir built in `setUp` / `setup_method` | **119** | failure (call phase) | no |
| `mkdtemp` / `NamedTemporaryFile` in the test body | **26** | failure (call phase) | no — only `TemporaryDirectory` was searched |
| tmpdir one indirection past `setUp` (`setUp` builds `_Repo()`, `_Repo.__init__` calls `mkdtemp`) | **12** | failure (call phase) | no |

`157` skipped before, `485` after — both sides measured on **this** tree over the same 1465-item
collection, the before side by pointing the measurement at `git show HEAD:nd-unfolding/tests/
conftest.py` rather than by reconstructing the old rule. **6 of the 119 and 1 of the 157 are this
change's own probe tests**, so the pre-existing exposure was `113` and `156`; the derived figures are
quoted rather than the pre-existing ones because a before/after taken from two different collections
is the kind of pair that cannot contradict itself.

The file's entire justification is that **errors read as defects** — and the only stratum that errors
is the fixture one, which had zero coverage.

### 2. A simulation the code under test can route around is not a simulation

The first attempt patched `tempfile.TemporaryDirectory`, `mkdtemp` and `NamedTemporaryFile`. The
fixture stratum **still passed**, because pytest's `tmp_path` does not call `mkdtemp` — it calls
`gettempdir()` and then `os.mkdir` (`make_numbered_dir`). 171 items looked covered by a harness that
could not touch them. The patch had to move to the `os` layer.

**Generalisation:** *a negative control has to be verified against the actual call path, not against
the API you would have used.* Patching the obvious entry point and seeing green is the same error as
grepping for the name you would have chosen (`BEN-344`).

### 3. Being *more* faithful broke the harness — and that bounded the guard's reach

The textbook simulation of "no writable temp directory" is `gettempdir()` raising
`FileNotFoundError`. With that in place **pytest never started**: `_pytest.capture` builds its
`FDCapture` from `tempfile.TemporaryFile`, which calls `gettempdir()` during
`pytest_load_initial_conftests` — the process died before any conftest was loaded.

Two consequences, both load-bearing:

* **The guard's value is bounded to sandboxes where pytest itself survives.** If nothing under the
  temp root can be created, no conftest hook of any kind can help, because collection never happens.
* **conftest.py's own description of the historical sandbox cannot be literally true.** It says the
  sandbox *"provides no writable temporary directory"*. But pytest ran there and reported **23
  ERRORS**, so it created its capture temp file successfully. The condition consistent with the
  observed history is narrower: **`mkdir` under the temp root is refused, a temp FILE is fine.** That
  is what is simulated, and `NamedTemporaryFile`/`mkstemp`/`TemporaryFile` are deliberately left
  working.

**Generalisation:** *when a faithful reproduction of the failure kills the harness, the recorded
description of the original failure is wrong — and the discrepancy tells you what the failure
actually was.*

### 4. `ERROR` is not an outcome, it is a rendering — so the obvious assertion can never pass

I wrote `assertEqual(outcome, "error")`. `TestReport.outcome` is **`"failed"`** for a setup-phase
break as well as a call-phase one; the terminal derives the `ERROR` label from `when != "call"`. A
test asserting `outcome == "error"` is red no matter how the code behaves. The assertion is on the
**phase**.

### 5. pytest runs `unittest` `setUp` in the CALL phase, which inverted my ranking of the misses

I had written that the `setUp` stratum "actually ERRORS" and was therefore the important miss.
Measured: pytest's unittest integration runs `setUp` inside `runtest`, so that stratum produces
**failures**. The fixture stratum is the erroring one. Both are worth skipping — a phantom failure
costs the same triage as a phantom error — but the ranking I gave was backwards, and I only found
out because the assertion was written against the phase and went red.

### 6. `BEN-342` recurred in my own work, and mutation testing is what caught it

Five mutants were run against the fix. **`M4` — delete the direct `setUp`-source check entirely —
survived.** The probe suite's `setUp` test used the *indirection* shape (`setUp` builds a helper), so
the depth-1 helper walk covered it and the direct check was never the thing under test. **That is
exactly `BEN-342`: a fixture degenerate on the axis it was meant to vary**, filed by this lane
yesterday, reproduced by this lane today. Fixed by splitting the probe into `4a` (direct) and `4b`
(indirection) as separate classes.

Chasing `M4` then exposed a real over-reach in the fix itself: the depth-1 walk read the source of
anything `setUp` mentioned, and the first name `setUp` mentions is `tempfile` — whose module source
contains every string in `TMPDIR_APIS`. **The walk was matching the standard library, not the
helper**, which is why deleting the direct check changed nothing. Restricted to definitions owned by
the test module.

---

## The last mutant, and a rule for filters

`M7` — delete the `__module__` equality that keeps the walk inside the test module — **survived**,
because nothing in the probe suite distinguished an imported helper from a local one. The filter was
**unfalsifiable**: it could be removed with no test noticing.

The fix is not to delete the filter (following imports reintroduces the over-fire this design exists
to avoid). It is to **pin the filter in the direction it acts**: `Route4c` builds an *imported*
helper and is asserted **not** skipped, with `Route4d` showing the marker as the remedy on the
identical shape. `M7` is now caught.

**Generalisation, and the one worth carrying:** *every deliberate narrowing needs a test asserting
the thing it excludes stays excluded.* A guard gets a test that it fires; **a filter gets a test that
it does not** — otherwise widening it later looks free. This is the same rule as `BEN-344`'s but
applied to the negative side of a boundary, and it is what the over-fire test (`M5`) and the residual
test (`M7`) each buy.

## And the over-fire boundary was real, not hypothetical

The obvious fix — scan the whole class body — was measured before being rejected: **154 further
items** sit in classes where a *sibling* method uses a tmpdir while the test itself needs none.
Skipping those hides real coverage behind phantom skips, which is the failure mode symmetric to the
one this file was written for. `M5` confirms the boundary test catches that widening.

---

## Result

| | |
|---|---|
| new tests | 7, in `nd-unfolding/tests/test_conftest_tmpdir_guard_live.py` |
| mutants run / caught | **6 / 6** (after `M4` and `M7` were made catchable) |
| guard skips, guard forced on | `157` → `485` over 1465 items, both sides one collection |
| strata closed | fixture `171`, `setUp` `119`, body `26`, indirection `12` |
| deliberately excluded | `154` sibling-method items (over-fire), `1` defaulted-`tmp_path` parameter |
| known residual | imported `setUp` helper — asserted, not silent; marker is the remedy |
| suite | `1461 passed, 3 failed, 1 skipped` — the 3 are pre-existing off-cluster environment failures (macOS `/private/var` symlink; absent `/pscratch` paths) and cannot be caused by this change, which early-returns wherever a writable tmpdir exists |

`N6` closed. The pre-existing four unit tests of the guard (`TmpdirGuardItself`) still pass unchanged
and are complementary: they test the hook body, this file tests the hook under a live pytest, and
neither reaches what the other does — the fake items in the unit tests have no class, no fixture
closure, and a `get_closest_marker` that returns `None` unconditionally, so the marker, fixture and
`setUp` routes were all unreachable from them.

---

## ADDENDUM 2026-08-16 — the same file then failed on ANSI colour codes, one line below the robust assertion

Finding (4) above is that **`ERROR` is not a stored outcome** — the terminal derives it from
`when != "call"`. Having written that down, `test_WHICH_shape_errors_and_which_merely_fails` then
asserted the *rendering* of it:

```python
self.assertEqual(self.control_phase.get("test_route2_pytest_fixture"), "setup")   # robust
self.assertRegex(self.control_text, r"(?m)^ERROR ")                              # fragile, next line
```

**When pytest colourises, that summary line begins `\x1b[1m`, not `E`, so `^ERROR ` cannot match at line
start.** Reproduced on one machine by flipping one variable — `PY_COLORS=1` → 1 failed;
`NO_COLOR=1 PY_COLORS=0` → 7 passed. **Three lanes reporting three different suite totals were reading
colour settings, not code**; `git log` over both files since the commit first blamed is empty, and
repair-12 touched neither.

**The defect is `BEN-335`'s shape — text as a proxy for a program fact — and its placement is the
lesson.** In a test whose entire subject is *which phase broke*, the phase was answered correctly from
the report objects and then **re-asked, fragilely, of the terminal output.** The robust assertion and the
fragile one were adjacent. Knowing the general rule did not prevent the specific instance, because the
two assertions look like they check the same thing.

**Fixed by deriving the label the way the terminal derives it** — a `_label()` helper computing
`"FAILED" if phase == "call" else "ERROR"` from the two fields the test already collects — and deleting
the text assertion. **Not** by forcing `NO_COLOR` in the subprocess: that suppresses the variable while
leaving the dependency, and leaves no trace the assertion was ever rendering-dependent.

**Controls, because a derived label can be wrong in two directions:** the fixture route must derive
`ERROR` **and** the three call-phase routes must derive `FAILED`, so a helper returning either label
unconditionally is caught. Mutation-tested under `PY_COLORS=1`: **4/4 caught** — always-`ERROR`,
always-`FAILED`, inverted rule, and dropping the missing-phase raise. That last one **survived until a
test manufactured the state no probe produces** (a name present in the outcome map and absent from the
phase map); rather than accept the survivor or let a silent default stand, the impossible case now
raises and is exercised — the same move as manufacturing an unwritable tmpdir in a subprocess.
**8/8 green under default, forced-colour, forced-plain and forced-TTY.**

**Acceptance check: the suite now resolves to ONE number under both colour settings —
`4 failed, 1477 passed, 1 skipped`** — where three lanes previously disagreed at 2, 3 and 4. The fourth
failure is *not* colour and *not* this file: `test_no_LIVE_pipeline_instances` reports 2 live instances,
both in `docs/orchestration/shared_push.sh` (lines 98 and 105, no `set -o pipefail`), another lane's
active file. **Removing the noise revealed a signal the noise was hiding**, which is the argument for
fixing rendering-dependence rather than pinning around it. Note for its owner: both instances end
`|| true`, so the return code is deliberately discarded and this may be a sweep false-positive rather
than a defect — but the test asserts `0`, so the disposition is theirs. Not touched here.
