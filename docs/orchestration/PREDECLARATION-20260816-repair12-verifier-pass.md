# PREDECLARATION — repair-12: the token gates a wrapper, not a capability

**Written 2026-08-16 BEFORE the repair exists.** Author: the `standard-p4-verifier` lane (repair-10,
repair-11). **No verdict, no token, no repair.** Scoping and the bar only.

Repair-11's bar worked *including where it convicted itself* (`B1` was unsatisfiable as written), so
the same instrument is used again.

---

## 1. The defect, reproduced rather than relayed

Measured here at `5fb7e38`, independently of lane B:

```
p4_validate_active_lateral.py    0 occurrences of P4_VERIFIER_PASS
p4_project_4d.py                 0
p4_build_components.py           1  -- line 161, a COMMENT describing the OLD gate's shape
run_p4_standard.sh               5  -- the only real gate
```

**The three stage modules are individually executable and individually ungated.** Running them
directly — the only way to run stages 4–6 without re-running 1–3 — bypasses the token completely.

**This is `KNOWN_ISSUES #21` one layer out.** `#21` was *any non-empty string opens the stages*.
This is *not going through the wrapper opens the stages*. **The repair strengthened the predicate and
left it in the same single location**, which is why the same class recurred against a stronger check.

**Found the honest way, and it is recorded because it bears on the fix:** the orchestrator's dispatch
said "run stages 4–6", and the literal execution of that instruction is the route that defeats the
control. The bypass is not exotic — **it is what the instruction asks for.** A gate that only holds
when nobody does the obvious thing is not holding.

## 2. What must be preserved — the token's actual strength

Verified in `p4_check_verifier_token.resolve()`, because the fix is worthless if it degrades this:

1. the token must be a **64-hex sha256**, not a passphrase;
2. it must equal `sha256_file()` of an **actual receipt** in the verifier directory, matched by
   scanning them — not asserted;
3. **the receipt must be `git ls-files`-tracked AND byte-identical to its committed blob.**

**(3) is the load-bearing one and it is what defeats `#21`'s lesson** that *an agent who can set an env
var can also write a file*. An invented receipt is untracked and is refused. **Any repair that checks
`P4_VERIFIER_PASS` for non-emptiness, or for any property short of resolving it through this function,
re-opens `#21` in a new location and is a BLOCK regardless of how many modules it touches.**

## 3. Scoping — argued, and none of the three offered options is right alone

**(a) A gate in each of the three modules.** The *logic* would live once in `resolve()`, so this is
three call sites, not three copies — `BEN-228`'s stale-copy argument does not quite apply. But the
real exposure is **omission**: a fourth stage module gets written and nobody adds the call. That is
the same "wired?" failure as `R11-1`.

**(b) A shared entry check in `p4_lib`.** Strictly weaker than (a): it still has to be *called*, so it
adds a function without adding a guarantee. **A library gate nobody invokes is the defect repair-11
just finished ruling on.**

**(c) Refusal to be importable-as-`__main__` without the token.** Correctly targets the bypass route
and leaves library import free for tests — but leaves any *library* caller ungated, and the campaign
has library callers.

**RECOMMENDED: (a) for the mechanism, plus the thing none of the three supplies — a DERIVED test that
makes omission fail closed.**

> The set of modules that must gate is **not** to be hand-listed. Derive it — from the stage scripts
> `run_p4_standard.sh` actually invokes — and assert each one resolves the token. Then a fourth stage
> module without a gate **fails a test** rather than relying on someone remembering.

That is the `OI-124` pattern (*derive, do not narrate*) and it converts personal's "three places to
drift" from a discipline problem into a checkable one. **Without the derived test, (a) is a BLOCK.**

**The durable end-state, recommended as a FOLLOW-ON and explicitly not as repair-12: gate the WRITE,
not the entry.** Every path that publishes a candidate, component or projection must resolve the
token, so no entry point — existing, new, or direct — can bypass it. **Costed and rejected for now:
there is no shared publish path.** Measured — all three modules write directly via
`ROOT.TFile.Open(..., "RECREATE")` or `json.dump(open(...,"w"))`. Creating one touches all three
surface files plus `p4_lib.py`, and **any surface edit invalidates repair-11's PASS under rule 4b**,
which is currently load-bearing with the cluster at `5fb7e38`. That is a real cost to pay
deliberately, not as a side effect of a scoping note.

## 4. THE BAR — what returns PASS for repair-12

**C1. Every module the wrapper invokes for stages 4–6 resolves the token through
`p4_check_verifier_token`, not through an env-var predicate.** A non-emptiness check, a truthiness
check, or any check that a bare `export` satisfies is a BLOCK — that is `#21` relocated.

**C2. The gated set is DERIVED, not listed.** A test that enumerates the stage modules from the
wrapper's own invocations and asserts each gates. **A hand-written tuple of three module names does
not satisfy C2**, because the failure being repaired is omission and a hand-list cannot detect its own
incompleteness.

**C3. The bypass is demonstrated closed, by execution.** Invoke a stage module directly with no token
and observe refusal; with a token that resolves, observe it proceed. **Both directions**, or the guard
has not been shown able to fire. A source-level `assertIn` does not satisfy C3 — that is `R11-1`.

**C4. No surface file changes that repair-11's PASS did not cover, or the PASS is re-earned.** Rule 4b
is not a formality here: the cluster verifies against it. If repair-12 touches the surface — and C1
means it almost certainly must — **repair-11's PASS dies and repair-12 must re-establish 4a/4b/4c and
the suite baseline itself.** Stated now so it is not discovered afterwards.

**C5. Every defect row carries `falsified_by`** — the observation that would have shown the defect
absent, addressing the claim's **predicate**, not merely some fact about its subject.

**Not gating C1–C5:** `R11-1`, `self_guards_adequate`, and anything about the real-product
`C4 = M C5 Mᵀ` identity, which needs cluster compute and is not authorized by any verdict of mine.

**If I return PASS on a basis other than C1–C5, this document is the falsifier.**

## 5. Boundary with lane B on `R11-1`

B proposes converting the text-level `assertIn` into an **execution witness** — the receipt's
`projection_M_recipe_check` carrying `nnz > 0`, `entries_differing == 0`, and `nnz` matching an
independent recount. **That is the right instrument and it satisfies what `R11-1` asked for**: numbers
a commented-out call cannot produce. Approved as a post-run check.

**Boundary, so we are not both inside it:** `R11-1` is **B's to close**. This lane wrote the row and
will verify the closure in repair-12; it will not implement it. **I am not touching
`test_p4_repair.py` or `p4_lib.py`** — lane A may still be narrowing `BEN-328`, and a surface edit
would invalidate repair-11's PASS.

## 6. Scope

* No verdict, no token, no repair, nothing launched. `P4_VERIFIER_PASS` is never set by hand.
* The recommendation binds how repair-12 will be **judged**, not who writes it or how.
* The follow-on write-gate is recorded as a recommendation only, with its cost stated; it is not
  authorized here and not required by C1–C5.
