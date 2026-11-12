# T3 ADDENDUM V1: a test of the step-2 bound at exact equality (test-only, 2026-11-11, DRAFT for coverage-5b-audit's glance and the director's note in the binding)

**By:** session tier3-design, at the director's ruling (T3 binding 1, ruling 4).

**Under:** [`T3-PIPELINE-TESTS-DECLARATION.md`](T3-PIPELINE-TESTS-DECLARATION.md) rev 4 (sha256 `f96ed6f29a155e97`),
bound at M_T3 = `14fb9e5235307c96080d28da2c84ce0880931b9a` by `T3-BINDING-1.md` (PR #1063).

## What it closes

coverage-5b-audit's low v1 on rev 4: no test fixed the boundary of §5.2's rule at headroom = δ_A. A mutant that changes
`headroom < bars[arm]` to `<=` passed rev 4's suite. The code follows §5.2's strict "h < δ_A", and the two differ only
at exact equality.
<!-- absence-ok: restates the audit's own finding about one boundary case, which this addendum closes -->

## What changes

**Test-only.** `t3p_read.py`, `t3p_probe.py`, `t3p_arms.py` and `sbatch_t3p.sh` are byte-identical to M_T3. The
declaration, the rule, the readings and the price are unchanged.

- **`test_t3p.py`:** adds one test, `test_the_bound_is_strict_at_equality`. It calls `t3p_read.readings` on synthetic
  per-iteration values: every arm's ρ is 0.1 and OP's is 0.05, at every split. The test first asserts that
  0.1 − 0.05 = 0.05 exactly in binary, so the boundary is reached exactly. Then:
  - the bar is exactly 0.05 (zero spread over the splits, so the floor) and the headroom is exactly 0.05. MU, MW and
    MO read "no effect", not bounded;
  - with OP's ρ one ulp above 0.05, the headroom is below the bar, and all three read "no effect (bounded by step 2)".
- **`t3p_mutation.py`:** adds one mutant, "v1: the bound includes equality" (`<` → `<=`), named to that test.
  `EXPECTED_TESTS` goes from 68 to 69.
- **Counts:** 69 tests and 74 mutants.

| file | sha256 at M_T3 | sha256 after this addendum |
|---|---|---|
| `test_t3p.py` | `69621cb52deb2f965056ed219ad557fa34dc590586038f411975043f21fbc454` | `4879178f4f9783f011f8a5992273e0b34a3d022bb822edf688051f038e642aa8` |
| `t3p_mutation.py` | `3b532709e8d1b6d69e6ed69a54bc369e45a849e2ccfc52266b2f5131a060b7c0` | `ae9667bc71819f092a7f61ae6d58ed4e7659ea4b0fea08de299c10462d738001` |
| `t3p_arms.py`, `t3p_probe.py`, `t3p_read.py`, `sbatch_t3p.sh` | `4a685bde…`, `e27bf07a…`, `f4c221dd…`, `a21ad29f…` | unchanged |

**Receipts:** `addendum-v1/`, in a separate commit. They are made in a clean clone at the commit that adds this file,
by one serial process under `nice -n 19` with every BLAS and OpenMP thread cap at 1, as for rev 4.

## MEASURES / CANNOT AUTHORIZE

- **MEASURES:** that the suite fixes §5.2's strict boundary, and that the `<=` mutant is killed.
- **CANNOT AUTHORIZE:** any job, connect or submit (binding 1, ruling 1: nothing runs before the LL5D readout, and
  each connect needs the director's go); any change to the bound code, a reading or the price.

Nothing is run, submitted, deposited or tagged.
<!-- absence-ok: a statement about this addendum's own status -->
