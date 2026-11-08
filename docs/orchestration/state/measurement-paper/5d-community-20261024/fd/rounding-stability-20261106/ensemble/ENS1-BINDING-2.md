# BINDING 2: ENS1, the ensemble-averaged estimator, its code (director, 2026-11-08)

**Binds the code** of ENS1, as merged in PR #899 at **M = `53382844e72057d6eacb47f3bf8556cd47766a70`**. The audited
head is `afca65da`, and the code files are identical at the two commits.

| file | sha256 (prefix) |
|---|---|
| `nd-unfolding/ensemble_estimator_probe.py` | `9721fc97e12794f3` |
| `nd-unfolding/ensemble_estimator_analyze.py` | `ef2f467cc010b370` |
| `nd-unfolding/sbatch_ens1.sh` | `0390e5c71f1b9585` |

The tests are in `nd-unfolding/tests/test_ensemble_estimator.py` (67), and the harness in
`tests/ensemble_estimator_mutation.py`.

**The design** is bound by [`ENS1-BINDING-1.md`](ENS1-BINDING-1.md) at `15305f2d`.

## What the director checked

**coverage-5b-audit's code GO at `afca65da`**
(https://github.com/josephbaileyy/MINERvA-OmniFold/pull/899#issuecomment-6715332209):
- **ENS1-C1 is closed.** The 32 sites the audit found without a killing test, at the gates, readings and refusals, now have tests, including the
  readings themselves (one fit in place of E₉₆'s mean at both stages, and G0 against E₉₆(x)).
- **ENS1-C2 is closed.** The three teardown-guard branches are ported from RS1 A1.
- **Mutants:** with a byte-only control, all 91 named mutants and the audit's 5 extras are killed.
- **Six LOWs** are held for the follow-up list.

## Rulings

1. **The code is bound at M.**
2. **Stage 1 runs as bound:**
   - a dry run of 9 tasks at `--time=0:45:00`;
   - then 6 one-node shards, under the projection gate;
   - the cap is 55.0 node-h.

   Stage 2 runs only on STAB_PASS and the director's go, with a cap of 46.0. `iris` is read before each launch.
3. **The root** is a fresh /pscratch/sd/j/josephrb/ens1-20261107. The FD-STAB j1–j20 copies are made with
   `dd iflag=noatime` and checked against SHA256SUMS. Every module call runs under the sourced environment.
4. **ENS1 may queue alongside RS1's resume** (job 60982139).
   - It reads none of RS1's products.
   - Its design was bound before RS1's outcome is read.
   - The total stays within the half-balance rule.
5. **Each connect's sha256** comes to the director before launch, and each receipt is a PR.

Nothing is submitted, deposited or tagged.
