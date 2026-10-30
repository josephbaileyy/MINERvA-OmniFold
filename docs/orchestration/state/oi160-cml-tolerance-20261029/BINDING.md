# Binding: OI-160, the C_ML tolerance run on unseen seedscan_split replicas (2026-10-30)

**By** the paper-tighten lane, as director.

**Under** `DECISION-20261029-joseph-oi160-close-cml-and-5b-session.md` (#515), item 2: "C_ML is checked the same way",
as one pre-declared tolerance run with a fresh same-code floor control.

**Binds** [`DECLARATION.md`](DECLARATION.md), merged in PR #517. Its file sha256 begins `c665e7c126fa4b92`.

**MEASURES:** nothing. It authorizes the declaration's deploy and tests on a login node, its one 6-task CPU array, and
the grading on a login node.

**CANNOT AUTHORIZE:** any change to `C_ML`, `C_stat`, the trunk, a receipt or a published value; a resubmission, a
second array, a GPU, premium QOS, or a write to CFS or the canonical checkout; a reading beyond §3.3's tables.

## 1. The bound code

**The deploy pin** is `eb2282e1eedf89c51dda67102fd7f682bbc04976`, main after PR #517.

**At the PR head `8d21e8dd`, the director checked:**
- the seven §7 pins, each against its file;
- `code.sha256` against git: A's `seedscan_split.py` `8bb7e74c` is `07c18aee`'s, and B's `4fade69b` is
  `07c18aee^`'s. The diff between them is the fixed `--estimator-seed` (default 42) in place of the split seed;
- the declared test command, from `/` with `-I -B` and `discover`: **Ran 13 tests, OK**;
- `run_array.sh`'s SBATCH lines: `--qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=36 --mem=64G
  --time=01:30:00 --array=0-5 --no-requeue --account=m3246`, with no GPU request;
- the reading table (§3.3), with INERT and the GREY band, fixed in advance.

## 2. Rulings

1. **τ = 1e-8 carries over on the structural argument,** valid only if V1 measures seedscan_split's own fresh floor at
   ≤ τ/100. If V1 fails, everything is VOID.
2. **INERT is a full answer:** if A and B coincide and both match the stored replica, `C_ML` is the same under either
   contract for the graded seeds.
3. **The one producer, `55849763`, rests on five graded seeds,** 4, 9, 14, 19 and 24. The other 19 are covered by
   inference only, and the report says so.
4. **The 36-CPU run against the committed launcher's `--cpus-per-task=16`,** and the difference from KI-79's F2
   configuration, are stated in the report beside the verdict.

## 3. Conditions

1. **Deploy and tests,** exactly as §2.1, with `<pin>` = `eb2282e1eedf89c51dda67102fd7f682bbc04976`, into a new directory that must not exist
   beforehand. Anything other than HEAD = pin, 0/0 porcelain lines, the §7 digests, `tests rc=0` and "Ran 13 tests" is
   a STOP.
2. **The array,** submitted once with §2.2's command. A STOP in any task is reported unrepaired. Nothing is
   resubmitted.
3. **The report is `REPORT.md` beside the declaration, opened as a PR to the director.** It gives the readout's
   verdicts verbatim, V1, the distances labelled descriptive, the provenance, the `sacct` charge per task, and rulings
   2–4. It draws no conclusion about `C_ML` beyond §3.3. The director takes it to Joseph.

The steps may start once this record is on `main`.

## Not changed

- `C_ML`, `C_stat`, the trunk, every receipt and product.
- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.
