# A green verdict bounds the numerator and never the denominator — three instances in one file's blast radius

**Lane E, 2026-08-18. `BEN-415`, `BEN-416`, `BEN-417`.** Filed as one long form because the three rows
are one shape found three times in one afternoon, on three different layers of the same work:

| layer | the check that reported success | the population it actually covered |
|---|---|---|
| the pinned validator | `n_failed = 1` | **22 of 77** check sites — the other 55 never ran |
| the extraction branch | reviewed as written, no failures reported | **0 executions** — the branch was unreachable |
| the control suite | `Ran 30 tests … OK` | **30 of 61** — every F1/F2/F3 control hidden |

In none of the three did anything lie. In all three the *count of failures* was correct and the *count
of things examined* was never stated, so the reader supplied a denominator that was not there.

---

## 1. `BEN-415` — the early return makes a large defect present as a small one

`validate_gate5_training_artifacts.py:206-214` builds a 27-element `required_keys` set and `:219-220`
returns early when any is absent:

```python
checks.eq("required_npz_keys_missing", sorted(required_keys - set(store.files)), [])
if required_keys - set(store.files):
    return {"replica_index": idx, "verdict": "FAIL", "checks": checks.summary()}
```

Measured on this tree: **22 of the 77 static `checks.eq/truth/close` sites in `validate_member` run
before that return, and 55 run after it.** So one missing key costs 55 checks, and
`checks.summary()` reports `n_failed = 1` — which is true, and which a reader will pair with an assumed
denominator of 77.

The gap was found by AST-diffing the two writers' `augmented` dicts against the required set rather
than by reading either:

```
REQUIRED, supplied by the COHERENT writer, ABSENT from the DATA-ONLY writer:
    bkg_indices  bootstrap_factor_sha256  bootstrap_seed  bkg_bootstrap_factor  sig_bootstrap_factor
```

Four are mode-independent omissions and are now written. The fifth, `bootstrap_seed`, cannot be written
honestly — see `BEN-426`, which resolves it as a routing constraint rather than a value.

**Why this matters beyond one validator.** The wrapper design being built on top of this validator had
a clause *"non-manifest checks PASSED"* and a floor on **manifest size**. Both are satisfiable by 55
checks that never executed. The amendment is a floor on `n_passed + n_failed`, and — lane C's
improvement on it — that floor must **equal what the coherent partition observes** rather than being a
number the manifest's author picks. *A floor you author is part of the claim, not a check on it.*

## 2. `BEN-416` — three defects stacked so that no one of them is observable

`extract_fullevent_replica.py`'s data-only branch had three independent defects:

1. **Unreachable.** It sat behind a required-key gate demanding `bootstrap_seed`, a `campaign_role`
   check against the coherent role, and an `int(scalar(store, "bootstrap_seed"))` identity read. All
   three reject a data-only artifact, so the branch could not be entered by the artifacts it exists
   for.
2. **Wrongly shaped.** It ended `return dict(contract=…, n_data=…, …)` — nine keys — while both call
   sites are `contract, sig_factor, evidence = read_replica_contract(...)`. Nine into three is a
   `ValueError`. **It had never executed once.**
3. **Wrong key name.** It returned `factor_hashes=` where eight downstream sites index
   `evidence["factor_sha256"]["signal_factor_sha256"]`.

Each defect prevented the next from being observed, and the dispatch that sent me here described the
work as *"the required-key set plus the identity read"* — an accurate description of defect 1 alone.

**The transferable sentence:** *"it is written" and "it has run" are different claims about a branch,
and reading the code establishes only the first.* A branch that nothing exercises is not covered by
review; the covering artifact is a test that reaches it.

## 3. `BEN-417` — a misplaced `unittest.main()`, and why the fix had to be covering

`test_cstat_data_only_predicates.py` carried

```python
if __name__ == "__main__":
    unittest.main()
```

in the **middle** of the file, with three classes defined after it. `unittest.main()` runs at
module-execution time, so nothing below it is collected under direct invocation.

```
python3 test_cstat_data_only_predicates.py   ->  Ran 30 tests ... OK
pytest test_cstat_data_only_predicates.py    ->  61 passed
```

The 31 hidden tests included **every F1/F2/F3 control** — the provenance legs rebuilt three times that
day by four parties. Anyone confirming *"the controls pass"* the direct way saw green over half the
suite.

**The remedy is a check, not a habit,** and it is applied to every `test_*.py` in the directory,
because a rule enforced only where it was already broken catches nothing new. The sweep immediately
found two more modules, neither mine:

| module | direct | collected | hidden | disposition |
|---|---|---|---|---|
| `test_uq_remediation.py` | 20 | 35 | **15** | repaired; both routes now 35 |
| `test_pet_nominal_gate4_validator.py` | 63 | 97 | **34** | **hash-pinned at 5 digest sites** — declared, not skipped |

**80 controls across three files were invisible to direct invocation, and all three printed `OK`.**

The pinned one cannot be repaired without breaking `cluster-local-fork-freeze-20260812.json` and three
`p3f-pet-gate4-launch-code-gate-*.json`, and no repin is available. So it is **declared with its
sha256**, and the control asserts that digest still matches. When the file is next legitimately
re-issued the control goes red and the exemption must be re-justified. *An exemption without an expiry
is how a narrowing becomes permanent* — and this is the same reasoning as recording a pinned module's
digest in a divergence manifest so a re-issue is distinguishable from the check breaking.

---

## The check to steal

For any verdict that reports failures, ask **what it examined**, and require that number to come from
somewhere other than the verdict's own author:

- a report of `n` failures needs `n_examined`, and `n_examined` needs an independent source;
- a "no failures" over an early-returning routine is a claim about the prefix, not the routine;
- a suite's exit status is evidence about the tests it **collected**;
- and a branch's correctness-by-inspection is evidence about the text, not the execution.

**Relation to staleness, which this is not.** Nothing here was out of date. Every number was correct
when read. The population was simply smaller than the shape of the report implied — which is why
re-measuring does not help and only naming the denominator does.

**Cross-references.** `BEN-405`/`BEN-407` (a replacement that never fires is the forbidden relaxation
with extra steps), `BEN-386` (the file an edit lives in is not the file that validates it),
`BEN-410` (a command you have not executed is still a description), `BEN-426` (`bootstrap_seed`'s
under-dimensioned encoding, and the guard that must never be reached), `BEN-258` (`cannot-fail` is a
two-place predicate — check × input domain — which is why two of this session's vacuous shell guards
were repaired rather than deleted).
