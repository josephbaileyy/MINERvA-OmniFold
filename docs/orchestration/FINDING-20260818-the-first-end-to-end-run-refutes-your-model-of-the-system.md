# The first end-to-end run refuted my model of the system three times in ten minutes

**Lane E, 2026-08-18. `BEN-470`.** A module with 165 passing unit controls, every predicate individually
power-tested in both directions, could not grade a single member of the family it was written for. The first
time it was executed as a program rather than exercised as a collection of functions, it produced three
distinct refutations — and none of the three was reachable by any test I had written or could have written
without running it.

This is not "integration tests are good." It is narrower and more useful: **the first end-to-end run tells
you where your MODEL of the system was wrong, and unit controls cannot, because a unit control is written
from that same model.**

## Refutation 1 — the module could not import what it needed, and nothing said so

```
ModuleNotFoundError: No module named 'pet_bootstrap'
```

`pet_bootstrap` lives one directory above the validator. It is imported **lazily, inside**
`fullevent_fps_dataloader.coherent_bootstrap_factors`, which P4's canonical-draw check reaches. The
validator's `sys.path` carried only its own directory.

**Why nothing caught it:**
- the module **imports cleanly** — the failing import is not in any header;
- **every predicate passes its own controls** — they run under pytest, whose `sys.path` includes both
  directories because the test file adds them;
- so the defect lives **only in the composition**, and only in a subprocess with the module's own path.

This is `BEN-414` from the other side. That finding says *the absence of a module-level import is evidence
about the HEADER, not the DEPENDENCIES* — there it cost two minutes of I/O before an environment error. Here
the same property meant a validator that would have died at member 0 **hours after being reported as
finished.** The lazy import is invisible in both directions: you cannot see the dependency by reading the
header, and you cannot see the missing path by exercising the function under a runner that supplies it.

**The check:** run the thing as a subprocess, from its own directory, the way the launcher will. `pytest`'s
path is not the program's path.

## Refutation 2 and 3 — my fixture was wrong twice, and the validator was right both times

Building the synthetic family for the end-to-end control, I used `np.ones` for `data_bootstrap_factor` and
literal placeholders for the two target digests. Both were refused:

```
[gate5-dataonly] P4 data factor != canonical draw at this seed (post-hoc redraw or wrong seed)
[gate5-dataonly] replica_00: the artifact records target-receipt digest placeholder... but the file on
                 disk digests to 0d6af2a6...; the receipt has changed since training
```

**The fixture was wrong and the predicate was right, in both cases.** The repair was to compute the real
canonical draw via `fe.coherent_bootstrap_factors` and to digest the files *after* writing them.

### Why this is the entry worth having

**When a NEGATIVE control fails you suspect the code. When a POSITIVE control fails, the pull is toward
relaxing the predicate.** The reasoning is seductive and available in one step: *the fixture is obviously
fine, I built it to be correct, so the predicate must be too strict.* Every ingredient of that sentence is
something I wrote, which is exactly the situation in which I should trust it least.

Two things make the correct diagnosis cheap, and both are worth doing before touching the predicate:

1. **Read the failure message as a claim and check it.** *"data factor != canonical draw at this seed"* is a
   statement about my fixture, not about the predicate's strictness. It was true.
2. **Ask what the fixture asserts that the real producer does not.** `np.ones` asserts a draw of all-ones;
   the real writer never produces that. A fixture that is *simpler* than the producer is not a
   simplification — it is a different object.

**And the fixture being wrong is evidence FOR the predicate.** Both refusals demonstrated a check firing on
a state the producer cannot reach, which is the direction a guard is supposed to work in — so the two
"failures" were the only end-to-end evidence that P4 and `assert_target_binding` fire at all.

## The pattern across all three

Each refutation was a place where I had a model of the system and the model was wrong:

| my model | reality |
|---|---|
| "this module's imports are the ones in its header" | one is lazy, inside a callee, two directories away |
| "a unit-tested predicate set composes into a working program" | the composition has its own preconditions |
| "my fixture is correct because I built it to be" | it asserted a state the producer cannot produce |

**Unit controls are written from the model.** A control cannot test the part of the model it is built on, so
the errors it cannot catch are precisely the ones in the assumptions shared by every control in the suite.
165 of them agreed with each other and with me.

## The check to steal

Before reporting a multi-module program as finished:

- **Run it as a subprocess, from a clean cwd, with the arguments the launcher will pass.** Not `import` it,
  not call its functions from a test — *run it*. The path, the cwd, and the argument parsing are three
  separate untested surfaces.
- **Build one end-to-end fixture even when every unit is covered**, and expect the fixture to be wrong
  first. Budget for that; it is not wasted work, it is the only place your model of the producer gets
  checked.
- **When a positive control fails, write down which of the two you are about to change and why** — the
  fixture or the predicate. If the answer is "the predicate, because the fixture is obviously right", read
  the failure message again as a factual claim.
- **Count how many of your controls share an assumption.** If it is all of them, that assumption is
  untested no matter how many there are.

**Cross-references.** `BEN-414` (a lazy import makes the header lie about dependencies — the same property
from the other side), `BEN-416` (*it is written* and *it has run* are different claims about a branch; this
is the same distinction about a program), `BEN-417` / `BEN-415` (a green verdict over a silently smaller
population), `BEN-418` (the instrument family — seven checks that fired on correct code).
