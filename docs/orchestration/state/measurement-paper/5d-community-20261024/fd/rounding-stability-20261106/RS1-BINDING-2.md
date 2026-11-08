# BINDING 2: RS1, the rounding-instability mechanism study, its code (director, 2026-11-07)

**Binds the code** of RS1, as merged in PR #882 at **M = `e306087e68fd497541d32b440848a40f7f29611e`**. The code head
is `a884aeb8`, and the code files are identical at the two commits.

| file | sha256 (prefix) |
|---|---|
| `nd-unfolding/rounding_mechanism_probe.py` | `b2e6785837470d8e` |
| `nd-unfolding/rounding_mechanism_analyze.py` | `5542278154f701d2` |
| `nd-unfolding/sbatch_rs1.sh` | `b4fc2f69131d292e` |

The tests are in `nd-unfolding/tests/test_rounding_mechanism.py` and the harness in
`tests/rounding_mechanism_mutation.py`.

**The design** is bound by [`RS1-BINDING-1.md`](RS1-BINDING-1.md), at declaration head `0d51e054`.

## What the director checked

**coverage-5b-audit's code GO at `a884aeb8`** (https://github.com/josephbaileyy/MINERvA-OmniFold/pull/882):
- RS1-C1 is closed: the input digests are checked per product and at the namespace, there is one code across all
  products, and the dry and full pins must agree in sbatch and in the analysis;
- the install order composes over RS1's rebindings, with no bound module edited;
- 53 tests OK and 69 of 69 mutants killed, reproduced.

**One property only the dry run can test:** tie invariance through real LightGBM, which is the dry run's V jitter 1
against A0's seed-0 float64 base. The audit reads it in the dry-run receipt.

## Rulings

1. **The code is bound at M.**
2. **The dry run comes first,** with `sbatch --time=0:45:00` and the parsed TimeLimit checked. Its receipt goes to
   coverage-5b-audit, which reads the tie-invariance property, before the full run.
3. **The full run** uses `--time=7:15:00` on one node. The cap is 8.0 CPU node-h for the dry and full runs together, as
   RS1-BINDING-1 ruling 2 binds. `iris` is read before each launch.
4. **Each connect** sends its sha256 to the director before launch:
   - a fresh clone at M;
   - the cov2d squeue check recorded;
   - the inputs and G1 references stat'd, then copied with `dd iflag=noatime`;
   - ssh's rc read unpiped;
   - each receipt committed as a PR.
5. **Step 2,** the ensemble-averaged estimator, is declared before RS1's outcome is read (RS1-BINDING-1 ruling 5).

## Binding 2, addendum A1: the resume after the teardown crash (director, 2026-11-07)

**Binds** `RS1-ADDENDUM-A1.md` (sha256 prefix `0899d55cb35c1d54`) and its code, as merged in PR #902 at
**M_A1 = `4fd5b9c2db1cda2177cd4540c9a44c404cb1cc81`**. The audited head is `7ddbad47`. `7a6de074` changes only the
manifest, and the code and addendum are byte-identical to the audited head.
- New wrapper: `nd-unfolding/sbatch_rs1_a1.sh` (`d526f0cca205fa7b`).
- New planner: `nd-unfolding/rs1_a1_plan.py` (`01e0f82ba6baad5b`).
- The tasks still run from the bound deploy at M = `e306087e`. The bound modules and `sbatch_rs1.sh` are unchanged.

**What led to it.** The full run, job 60972000, ended INVALID (infrastructure), recorded in #901.
- One task, rs1_V_02, segfaulted in PyROOT during interpreter teardown (CPyCppyy::op_str from Py_FinalizeEx), after
  writing all four products with rc 0.
- xargs then stopped launching, so 45 tasks never started.
- ROOT is loaded in every task, through `s5n_pseudo.refine` → `load_u2d` → the 2D driver's module-level `import ROOT`.
  The path never uses it.

**What the director checked.** coverage-5b-audit gave GO at `7ddbad47`. The first head, `9e840cf7`, was NO-GO: 11
surviving mutants at the staging rules, refusals and guard branches, including an mv failure that could have left the
crashed run's files in use. Each is now tested and killed against a byte-only control: 28 tests, 33 of 33 killed.

**Rulings:**
1. **A fresh root,** /pscratch/sd/j/josephrb/rs1-a1-20261107, with attempt 1 left intact as evidence.
   - log-dry is copied verbatim.
   - The 9 dry tasks' and the 11 ended full tasks' products and sidecars are copied by dd and verified by digest.
   - V_02's four products go to runs-attempt1/ for a comparison only.
2. **The teardown guard.**
   - A task counts as done only if its products and sidecars verify by digest.
   - xargs continues past a failure.
   - A non-zero exit after every product and sidecar exists is recorded as `TEARDOWN-CRASH`. The products are moved
     aside and the task is recomputed once. The re-run's products are used, and the bitwise comparison is recorded.
   - A second teardown crash is a failure, and so is a failure before writing.
3. **V_02 is recomputed,** and its bitwise comparison with attempt 1 is recorded.
4. **The price:** 46 tasks and 178 unfolds, projected at 3.43 h against a 4.05 h limit, at `--time=4:30:00`. That
   fits within the 6.76 node-h left of the 8.0 cap, which stands for RS1 as a whole.
5. **Open item 1, the follow-up refactor.** Move `refine` and `_make_bkg_classifier` out of the ROOT-importing driver.
   It touches FD-STAB's, RS1's and ENS1's bound code, so it is not done here.
6. **The connect's sha256** comes to the director before launch, and its receipt is a PR.

### Addendum A1, revision 2: the planner's interpreter (director, 2026-11-07)

**Binds** the repaired A1, as merged in PR #904, at **M_A1 = `1f747346519d75a680b5c67d644bae798eeb5f86`**. The audited
head is `fe39a495`, and the A1 files are identical at the two commits. This **supersedes A1's M_A1 above** (`4fd5b9c2`).

| file | sha256 (prefix) |
|---|---|
| `RS1-ADDENDUM-A1.md` | `cef9555afdf99ecf` |
| `nd-unfolding/sbatch_rs1_a1.sh` | `c34512725d24408d` |
| `nd-unfolding/rs1_a1_plan.py` | `41c1c25ceea03ab1` |

**What led to it.** The first A1 connect stopped at staging (#905, 0 node-h). It ran `rs1_a1_plan.py` under the login
node's /usr/bin/python3 3.6.15, where `from __future__ import annotations` is a SyntaxError. The bound wrapper would
also have run the planner's `verify` before sourcing the environment. The partial root, which held no product, was
deleted under ledger rows in #905.

**Rulings:**
1. **Every planner call runs after the deploy's environment is sourced,** under root_6_28's Python 3.11, in both the
   wrapper and the connect. This is tested, including with the REQUIRED mutant "verify above the source".
2. **The Python 3.6-compatibility claim is withdrawn** (the director's choice (b)). The planner is not claimed to run
   under 3.6, and no call relies on it.
3. **The connect's preflight** runs the planner's `--help` under the sourced environment, and refuses on failure.
4. **Unchanged:** A1's rulings 1–6, including the fresh root at the same path, the teardown guard, V_02 recomputed,
   and the 8.0 cap. RS1 stands at 1.2400 node-h spent.
5. **coverage-5b-audit's GO** at `fe39a495`: 34 named mutants and its 12 extras are killed, with a byte-only control.
   The audit reads the connect script with its receipt.

Nothing is submitted, deposited or tagged.
