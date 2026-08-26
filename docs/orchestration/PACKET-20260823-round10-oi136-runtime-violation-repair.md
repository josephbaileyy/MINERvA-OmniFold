# ROUND-10 REPAIR PACKET — the OI-136 runtime violation that stopped legs 5a/5b

**CITABLE FOR:** what was built, where it is, and what was measured, 2026-08-23.

**NOT CITABLE FOR:** a Gate-1 verdict. **Gate 1 is NOT claimed passed at this sha.** The builder
does not grade this. **No compute was submitted in producing it.**

## ROUND 9 IS HISTORICALLY VALID AND SUPERSEDED FOR FURTHER SUBMISSION

Round 9 returned **18 PASS / 0 FAIL** at `a54038b2` and **that verdict stands as a true statement
about that sha.** Nothing in it is withdrawn.

**It does not carry forward.** The rehearsal it authorized then failed at runtime: the OI-136 guard
refused legs 5a and 5b before any work ran. A pre-submission gate that passes and is then falsified
by the first submission has not been shown wrong about what it checked — it has been shown
**incomplete for the purpose of authorising submission at a new sha.** The candidate has moved, the
defect it now repairs was live inside the graded tree, and PB-25 requires a grade to score a
stationary object. **A full independent regrade at the new sha is owed. This is not a delta review.**

## SHAs AND TREES

| | value |
|---|---|
| **REPAIRED / DEPLOYED** | `aa67c426afaa9b6ca91c9996637a6bade950da9a` |
| deployment | `/pscratch/sd/j/josephrb/k0r2/clean` — `porcelain 0`, **0 writable** |
| superseded candidate | `a54038b2…` (round 9's PASS; declaration retained, marked superseded) |
| declaration | [`DECLARATION-20260823-k0-candidate-aa67c426.md`](DECLARATION-20260823-k0-candidate-aa67c426.md) |
| rubric — **grade by digest** | 1160 lines, `e0fb342b6466ab9bb7fbcdef4b7a65a40351a2a0b22ab8f4fb534486dd5f1173` |

**A-2(a)–(g) all MET, each measured separately, every rc taken with `--write` or `--compare`:**
782 tracked source files, listing sha256 `fa3489e22168954bebcc9a602338d924582fd231643bfa285b3a9225e7535420`;
`--compare` rc=0 `SOURCE MANIFEST IDENTICAL`; 0 writable by an independent filesystem walk.

**780 → 782** is two *added* test files. `compare_unified_throw.py` was **modified, not added** —
count-neutral, stated because the previous declaration's gloss counted renames as adds.

**Why the candidate is the branch, not `main`.** `main` has none of the Gate-1 apparatus — no
`lib_mnv_env_preflight.sh`, no `lib_mnv_env_pathcheck.sh`, no parity gate. The repair was authored on
`main` and cherry-picked to the branch. Deploying `main` would have deployed a tree without the thing
round 9 graded.

## THE FAILURE

```
[oi136] IMPORT TREE VIOLATION -- REFUSING BEFORE THE WORK RUNS.
[oi136]   module        uq_math
[oi136]   resolved to   /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_math.py
[oi136]   expected      /pscratch/sd/j/josephrb/k0r2/clean
[oi136] inventory: checked=135 repo_origin_count=5 outside_expect_root=1 verdict=REFUSED
```

Six elements, exit 3, 25–61 s each. **The guard did its job**: it refused before any science ran and
before any product was written. Evidence: 12 logs at `<RUN_ROOT>/failure-evidence-2/`, `sacct`
before and after cancel.

**Cause.** Both 5a/5b routes are `unified_throw_cov_5d.py` → `unified_throw_cov.py` →
`compare_unified_throw.py:38`, which hardcoded the canonical root into `sys.path.insert(0, …)`. The
first two already derived their roots from `__file__`. **A repaired importer does not protect you
from an unrepaired import**, and their correctness bought nothing.

**Legs 1–4 completed** (292 tasks, 415 products) before this surfaced, because their import closures
do not reach that file.

## THE REPAIR — BOTH LAYERS

**Source.** `_REPO = str(Path(__file__).resolve().parents[1])`. No absolute fallback. Proved a no-op
on the canonical checkout. Not hash-bound — its sha256 appears zero times in the tree, checked.

**Scanner.** The static ratchet had called that file clean three times. The insert argument is `_p`,
a loop variable bound from an f-string mentioning `_REPO` — never the rooted name. Rewritten with
**dataflow to a fixpoint and order-awareness**; order matters in the other direction, since ignoring
it marks names rooted from assignments *after* the insert and turns an undercount into an overcount.

```
scanner WITHOUT dataflow : 13 files, compare_unified_throw.py ABSENT
scanner WITH    dataflow : 53 files, compare_unified_throw.py PRESENT
```

## TESTS — EXACT OUTPUT

```
$ pytest test_k0_5ab_separated_roots.py test_oi136_rooted_insert_ratchet.py \
         test_oi136_failopen_inventory_ratchet.py -q
21 passed in 27.94s
```

`test_k0_5ab_separated_roots.py`, 4 arms. **The decoy tree is POPULATED** with a same-named module
carrying a marker, so "resolved under the code root" and "resolved under the decoy" are different
observable outcomes — a fixture whose wrong tree is empty passes whatever the code does. Imports run
in a **child process**, because `sys.path` and `sys.modules` are process state.

**Power, measured:** restoring the hardcode in the *source* file fails **2 of 4**.

**The dormant-2D claim is executed, not asserted.** An arm imports the k=0 chain and asserts
`unfold_2d_omnifold_unbinned` is never pulled in — with a negative control proving the arm can see it
when it is.

## THE CENSUS — 52 / 2 / 1

> **CORRECTED 2026-08-24, after the round-10 grade.** The headline and the first row read
> **53**. That is the count at `aa67c426^`, *before* the repair — the figure that correctly
> appears in the scanner block above. On the deployed candidate the repaired file no longer
> matches, so the census there is **52**. The right number was already printed four lines
> below (*"52 remain"*), which is what makes this a stated-class error rather than an
> arithmetic one: one digit was doing duty for two different populations, and the sentence
> naming the population was the part that was wrong. Measured three independent ways at
> `aa67c426`, at `9db42a6d` and in a working tree: **52**, with `KNOWN_UNREPAIRED` at
> **52** entries and the census set equal to it exactly (0 in one and not the other).

```
52  repository-wide on the deployed candidate aa67c426, POST-repair
    (53 at aa67c426^, PRE-repair -- that is the scanner-block figure, not this one)
 2  in the static k=0 import closure (15 files)
 1  ACTUALLY EXECUTED violation -- compare_unified_throw.py, repaired here
```

**52 remain and NONE is presented as repaired or authorized.** All named in the ratchet in five
reasoned categories: 6 repaired on `main` awaiting merge, 8 PET-lane, 3 probe records, 1 the
published 2D arm, and **34 off the k=0 closure that are NEITHER REPAIRED NOR AUTHORIZED** — listed
so the count is honest, not because anyone has decided about them.

**The published 2D arm is reachable in the static closure and DORMANT** — its insert is inside
`main()`, which the k=0 route never calls. Joseph's ruling to leave it stands; the dormancy is a test,
not a claim, and a digest assertion fires if `omnifold.py` ever moves.

**Both ratchet constants are ref-dependent** and the files now say so: this branch carries six B-1
repairs `main` lacks, `main` carries six sweep repairs this branch lacks. The count matches at 51 on
both; the *set* does not. Do not reconcile by copying across refs.

## QUARANTINE — RECEIPT `dfef7871`

The failed run's **415** partial products are moved to
`/pscratch/sd/j/josephrb/quarantine/20260823-k0-a54038b2-failed-rehearsal/`. Union is **415, not
538** — the 123 `.done` markers are a subset, not an additional set.

**Not bookkeeping:** `mr_skip_if_complete` keys on those markers. Left in place, **123 tasks of the
rerun would have silently skipped** and the fresh single-sha run would have reused products built
under the defective sha. Verified after: member `.done` = 0, member files = 0, destination 415/123,
0 digest mismatches, 0 source paths remaining, July archive and the 08-22 quarantine untouched.

**These products are diagnostic output from a failed candidate, not reusable components.**

## WHAT IS NOT CLAIMED

- **Gate 1 does not pass at `aa67c426` and has not been graded here.**
- **No compute was submitted.** No `sbatch`, no science, no covariance work, no deployment beyond the
  candidate tree, no `set -u`.
- The 34 off-closure hazards are unrepaired and unauthorized.
- Nothing establishes that the rerun will succeed.
