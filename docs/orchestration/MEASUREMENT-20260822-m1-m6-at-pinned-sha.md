# M-1…M-6 RE-MEASURED at the declared sha — and four of the six have MOVED

**CITABLE FOR:** the state of the six measurements the review contract rests on, taken **2026-08-22
after the deploy refresh**, on the pinned tree and on the canonical checkout.

**NOT CITABLE FOR:** a Gate-1 pass, and **not** for a value older than a few hours — see §3.

**Closes `PR-05` / `F-17(a)`**, whose requirement is *"re-take the six measurements … on both trees,
at submission time, **and report every difference as a finding**."* Four differences are reported
below and **two of them are stale in the builder's favour**, which is the class `F-17(a)` exists to
surface.

- **Pinned tree** — `MNV_CODE_ROOT = /pscratch/sd/j/josephrb/k0r2/clean` @
  `6113a34d860ad9bcd643923d51170f228c80d894`, 775 tracked source files, listing sha256 `cc004894…`.
- **Canonical checkout** — `/pscratch/sd/j/josephrb/MINERvA-OmniFold` @ `b2d7d4ca…`.

---

## 1. THE SIX

### M-1 — imports after a rooted insert. **MOVED, and the contract's table is stale in the builder's favour.**

AST re-parse on the pinned tree:

| entrypoint | root literal (contract → now) | first insert (contract → now) | repository modules after it |
|---|---|---|---|
| `bootstrap_nd.py` | **yes → NO** | :11 → :28 | unchanged (3) |
| `seedscan_split.py` | **yes → NO** | :23 → :37 | unchanged (3) |
| `unified_throw_cov_5d.py` | **yes → NO** | :27 → :42 | unchanged (3) |
| `unfold_nd_omnifold_unbinned.py` | yes → yes | :52 → :77 | unchanged (4) |
| `sweep_bank_5d.py` | yes → yes | :35 → :51 | unchanged (5) |
| `combine_cov_nd.py` | no → no | none → none | — |
| `analyze_universes_5d.py` | no → no | none → none | — |
| `mii_adopt_unified_5d_stamped.py` | no → no | :149 → :149 | unchanged (1) |
| **`adopt_unified_5d.py`** | **yes → yes** | **:38 → :38** | **NONE — the empty set, unchanged** |

**Three literals are gone: the six source repairs landed.** The contract's "yes" for all six is now
false for three, so quoting that table today would overstate the hazard.

**And the three that remain are NOT the same kind of thing** — resolved rather than counted, because
a bare "3 still carry the literal" is the sentence that would mislead:

```
unfold_nd_omnifold_unbinned.py:73:  _DATA_ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
sweep_bank_5d.py:59:                _DATA_ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
adopt_unified_5d.py:35:             _REPO      = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
```

Two are **`_DATA_ROOT`** — the canonical checkout in its *data* role, which the two-root design
explicitly permits (*"the canonical checkout is acceptable in THIS ROLE ONLY. Nothing is executed or
imported from it."*). **Only `adopt_unified_5d.py:35` is a code-root `_REPO`**, and it is the known
inert case: it feeds the insert at `:38`, and the file imports **nothing repository-local**, which is
why the child-wrap design was vacuous by construction.

### M-2 — could the insert shadow a non-repository name? **UNCHANGED, and still zero.**

125 importable top-level names on the canonical checkout; intersected against
`sys.stdlib_module_names` (CPython 3.11.14) and a third-party set: **zero collisions in both
directions.** Identical to the contract's 125.

### M-3 — hash-bound files. **UNCHANGED.**

`python3 docs/orchestration/verify_hash_bindings.py` → **rc=0**, `ALL BINDINGS INTACT`. Status read
directly, not through a pipe.

### M-4 — the canonical checkout's actual state. **HOLDS on identity; the BEHIND-COUNT has moved twice.**

```
HEAD   = b2d7d4ca24707344cf12f99c0aa51381b81dd445      (unchanged)
dirty  = 721   ->  717 `??` + 4 ` M`                    (unchanged, exactly)
behind = 65    (contract recorded 36; PR-05's spot-check found 55)
ahead  = 0 ;  git merge-base --is-ancestor -> rc=0
```

**The behind-count is a DRIFTING quantity and should never be quoted without its date**: it moves
every time `main` moves, and `main` moved eight times today. `36 → 55 → 65` is `main` advancing, not
the checkout regressing. Identity (`HEAD`, `721`, `717/4`) is what actually holds.

### M-5 — the `.sh` half. **REPAIRED on the executing tree. The contract's finding is now FALSE there.**

```
$ /usr/bin/grep -nE '^[[:space:]]*(export[[:space:]]+)?REPO=' <the eight, on the pinned tree>
  -> 0 assignments
```

The contract records *"**all eight** assign `REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"`
unconditionally."* On `6113a34d` that is **zero of eight**; all eight take `MNV_CODE_ROOT`/
`MNV_DATA_ROOT` with `:?` fail-closed messages. **This is stale in the builder's favour and must be
restated, not merely re-run** — a reader taking M-5 at face value would think the executing tree is
unrepaired when it is repaired, and would also miss that **`main` is a different story**: the finding
survives wherever the launchers have not been updated.

### M-6 — the guard emits no evidence that it looked. **REPAIRED, with a caveat that is NOT closed.**

`mnv_guarded_run.py` now counts resolutions (`self.checked` at `:248`, incremented `:266`) and writes
it at `:369`. **But the write is `"checked": (guard.checked if guard is not None else 0)`** — so a
containment-path zero is a **default, not a measurement**, and a green arm with no repository imports
remains indistinguishable from a clean run. That is a live limit, recorded here rather than counted
as a clean repair.

---

## 2. THE FOUR DIFFERENCES, AS FINDINGS

| # | measurement | difference | direction |
|---|---|---|---|
| 1 | **M-1** | three entrypoints no longer carry the root literal; five insert line numbers moved | **stale in the builder's favour** — the contract overstates the hazard |
| 2 | **M-4** | behind-count `36 → 55 → 65` | neither; a drifting quantity quoted without a date |
| 3 | **M-5** | `8 of 8` → **`0 of 8`** `REPO=` assignments on the executing tree | **stale in the builder's favour** |
| 4 | **M-6** | repaired, but the `else 0` default keeps the vacuity hole open | against the builder |

**M-2 and M-3 are unchanged.**

---

## 3. EXPIRY — this is the fastest-expiring document in the package

- **M-2 rests on 717 untracked files** in a tree nobody controls. Contract §H.1 says so explicitly:
  they can change between measurement and submission. **125 was true at the moment it was read.**
- **M-4's behind-count** is falsified by any push to `main`.
- **M-1, M-5 and P-6** are falsified by any commit to `build-k0-execution-integrity`.
- **Re-run all six immediately before the first `sbatch`**, and again after the last leg. Do not
  inherit a number from this table.
