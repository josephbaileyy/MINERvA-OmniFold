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

## Binding 2, addendum A1: the internal jitter's edge zone (director, 2026-11-08)

**Binds** `ENS1-ADDENDUM-A1.md` and its code, as merged in #912, at
**M_A1 = `f4d2d7f3833834390b7b031df61ba1a5765e9900`**. The audited head is `56e306ca`. This **supersedes M above** for
every ENS1 run from the stage-1 dry rerun on.

| file | sha256 (prefix) |
|---|---|
| `ENS1-ADDENDUM-A1.md` | `1b8a4592d9e4cad1` |
| `ENS1-DECLARATION.md` (§2.3 withdrawn, §2.1 points to A1) | `fb523c7a7a8215b4` |
| `nd-unfolding/ensemble_estimator_probe.py` | `807c40d3cb64e2e0` |
| `nd-unfolding/ensemble_estimator_analyze.py` | `1d6a0448ac75c90a` |
| `nd-unfolding/sbatch_ens1.sh` (unchanged) | `0390e5c71f1b9585` |

**What led to it.** The stage-1 dry run (job 60983221, #908) was refused by the bound grid guard. Protocol jitter 1
plus δ_k moved 2, 1, 2 and 1 MCgen rows. The diagnosis (#909) confirmed the cause: the movers sit at the farther float32
neighbour of a non-representable edge. That falsified declaration §2.3.

**The freeze.** A1's design was frozen at `1ae4fcea`, before RS1's outcome was read (#915).
- After the freeze, only tests, the harness and text changed: commit `21c58e07`, labelled "audit fix, after RS1's read",
  and receipts.
- The probe, the analysis, `sbatch_ens1.sh`, `s5p_numerics` and `s5e_trace` are byte-identical to `1ae4fcea`. The
  director checked this with `git diff`.
- A1's text sha moved from `6561e3b6` to `1b8a4592` through those text pointers only.

**What the director checked:** coverage-5b-audit's GO at `56e306ca`, after a NO-GO on A1-C1 and A1-C2 at `1ae4fcea`.
- **The design and the margin** were re-derived as an inequality, with one edge definition shared with `cell_membership`.
- **The tests.** 106 of 106 lane mutants are killed by their named tests, including the REQUIRED B16–B19, B14, B12 and
  B03, against a byte-only control.
- **The auditor's extras.** 19 of its 20 are killed. B07 (1 + 2⁻¹⁰ spacing, quasi-equivalent) is held as a low.

**Rulings:**
1. **δ_k = 0 within one float32 spacing of any edge,** as A1 states. The draws and the bound grid guard are unchanged,
   and the 179 affected coordinates are part of the estimator's definition.
2. **The dry rerun's connect** checks all three of A1's preconditions on the npz's own edges, and refuses on any failure:
   - d_min > 1 + 2⁻²⁰ spacings;
   - every farther neighbour more than ½ + 2⁻²⁰ of its own spacing away;
   - no power-of-two float32 neighbour of a non-representable edge.
3. **The dry rerun** is 9 tasks at `--time=0:45:00` (parsed TimeLimit checked), in the fresh root
   /pscratch/sd/j/josephrb/ens1-a1-20261108. Attempt 1's root stays intact as evidence.
   - **moved_rows must be 0 in every class at all nine tasks** (gate E5).
   - **F₆₄ is recomputed** and compared bitwise with attempt 1's (`94ef5153…`). A difference is a STOP.
4. **Stage 1's cap stays 55.0 node-h,** with 0.1586 spent in attempt 1. Stage 2 is unchanged: it runs only on STAB_PASS
   and the director's go.
5. **Unchanged:** rulings 1–5 above, and binding 1. Each connect's sha256 comes to the director before launch.

Nothing is submitted, deposited or tagged.
