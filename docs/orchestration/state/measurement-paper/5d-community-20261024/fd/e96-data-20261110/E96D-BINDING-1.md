# BINDING 1: E96D, the ensemble average E₉₆ on the data (director, 2026-11-10)

**Binds** [`E96D-DECLARATION.md`](E96D-DECLARATION.md) and its code, as merged in PR #1046 at
**M_E96D = `1d25f8e791c503f8ef2ef6f6642546ee2008cc41`**. The audited head is `c5ae7949`; every file below is
byte-identical at both commits.

| file | sha256 (prefix) |
|---|---|
| `E96D-DECLARATION.md` | `486068bd2d171512` |
| `nd-unfolding/ensemble_estimator_data.py` (new) | `3f77191485d2a06e` |
| `nd-unfolding/sbatch_e96data.sh` (new) | `7ac31407598f1e42` |
| `nd-unfolding/tests/test_ensemble_estimator_data.py` (new) | `7aafcfe4bec40950` |
| `nd-unfolding/tests/ensemble_estimator_data_mutation.py` (new) | `b0cb6adc9a67a516` |

The bound ENS1 probe and FD-STAB's data refusals are byte-unchanged.

**Under** `DECISION-20261110-joseph-confirm-round-scope.md`: the ensemble average on data is on the post-LL5D list,
and its design may start earlier if usage allows. Also under the referee's follow-up
(`referee-methods-confirm-20261110/claude-followup-ens1.txt`), which made a data run no condition of the methods
paper's acceptance.

## What the director checked

- **coverage-5b-audit's two rounds.** Revision 1 had no blockers and three majors. Revision 2 resolved them:
  - E1: a coded gate on the dry products, checking A-D0, A-D1, the declared call and the projection; `full` refuses
    without a passing GATE.json at its pin.
  - E2: a bitwise repeat of k = 1 inside the full run, at 8-lane packing (A-D3).
  - E3: the five post-hoc checks, now tested.
  Its three minors were folded in at `c5ae7949`.
- **Reproduced by the audit:** 30 tests, 41 of 41 mutants killed (15 REQUIRED), FD-STAB's 114 tests, and the OI-136
  ratchet.
- **The licence:** this is the first statement about real data from E₉₆ (ENS1 kept the data out of every product,
  `ENS1-DECLARATION.md:105-107`). It is not citable for adoption, coverage, uncertainty or bias, or for any change to
  configuration (e).

## Rulings

1. **Nothing runs before the LL5D readout.** After it, each connect (the dry run, then the full run) comes to the
   director with its sha256s and a go. The job family `e96data` is announced to every fenced lane before the first
   submit, and cov2d_fence.sh runs before each connect.
2. **The price:** 99 unfolds, about 2.9 CPU node-h expected, with ceilings of 0.5 (dry) and 3.5 (full). The cap is
   raised to **4.0 node-h**. `iris` is read before each connect.
3. **The gate is binding:** a failed A-D0, A-D1, A-D2 or A-D3 is a STOP. It is reported as not made, with no E₉₆ data
   reading.
4. **The re-stage route** for (e)'s pscratch product, if it is purged first, is the declared CFS-archive copy by
   O_NOATIME, checked against `fb5cc679`. It goes to the director as its own script first.
5. **The result is read once** from its committed record. It enters the paper or the note only by Joseph's decision.

Nothing is submitted, deposited or tagged.
