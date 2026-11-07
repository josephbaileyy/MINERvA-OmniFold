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

Nothing is submitted, deposited or tagged.
