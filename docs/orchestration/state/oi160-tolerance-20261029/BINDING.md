# Binding: OI-160, the pre-declared tolerance run on unseen replicas (2026-10-29)

**By** the paper-tighten lane, as director.

**Under** `DECISION-20261029-joseph-oi160-tolerance-run.md` (#498): "A new declaration settles OI-160", with the
tolerance fixed from the measured noise floor before any data, applied to unseen replicas.

**Binds** [`DECLARATION.md`](DECLARATION.md), merged in PR #499. Its file sha256 begins `cb87a939d47c877c`.

**MEASURES:** nothing. It authorizes the declaration's deploy and tests on a login node, its one 6-task CPU array,
and the grading on a login node.

**CANNOT AUTHORIZE:** any change to `C_stat`, `C_ML`, the trunk, a receipt or a published value; a resubmission, a
second array, a GPU, premium QOS, or a write to CFS or the canonical checkout; a reading beyond §3.3's tables; a regrade
of seed 1.

## 1. The bound code

**The deploy pin** is `a310bb352ad64aaa3875bdb2f129450fa07594d6`, main after PR #499.

**At the PR head `87968c97`, the director checked:**
- the seven §7 pins: `run_array.sh` `c21d188e`, `tol_compare.py` `47ff57c9`, `test_tol.py` `82cbe3a1`, `seeds.tsv`
  `d2029872`, `stored.sha256` `9197ee78`, `code.sha256` `5da5283b` (the first run's, unchanged), and the first run's
  `repro_run.py` `649b1291`;
- the declared test command itself, from `/` with `-I -B` and `discover`: **Ran 9 tests, OK**, with 0 porcelain lines
  (including ignored files);
- `run_array.sh`'s SBATCH lines: `--qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=36 --mem=64G
  --time=01:05:00 --array=0-5 --no-requeue --account=m3246`, with no GPU request;
- the reading tables (§3.3), per seed, per producer and overall, fixed in advance.

## 2. Rulings

1. **τ = 1e-8 on the union-nonzero max relative difference, with an identical zero pattern, is accepted,** with V1
   (the fresh same-code floor ≤ 1e-10) and V2 (the codes separate by ≥ 100τ per seed). The margins are 3,300× above
   K1's measured max and 740,000× below the separation.
2. **The graded seeds are accepted:** 2 (`55805463`), 3 and 6 (`55871150`), 40 and 85 (the interactive loop). The
   producer rule is metadata-only, and seeds 10 and 11 are excluded as raced.
3. **NEITHER is not evidence against either contract.**
   - The interactive loop's per-replica thread allocation is not known from metadata. A NEITHER at seeds 40 or 85 may
     reflect a thread-count or environment difference, not a third code.
   - The report states this beside any NEITHER, and says what metadata shows of that loop's allocation.
4. **A producer's verdict covers its ungraded seeds by inference only,** and `55805463`'s rests on one seed, as §4
   says. The report states both beside the verdicts, with the weights 2 / 7 / 91.

## 3. Conditions

1. **Deploy and tests,** exactly as §2.1, with `<pin>` = `a310bb352ad64aaa3875bdb2f129450fa07594d6`, into a new `$B`
   that must not exist beforehand. Anything other than HEAD = pin, 0/0 porcelain lines, the §7 digests, `tests rc=0` and
   "Ran 9 tests" is a STOP.
2. **The array,** submitted once with §2.2's command. Any control STOP, a non-zero exit or a timeout in a task is
   reported unrepaired for that task. Nothing is resubmitted.
3. **The grade,** on a login node as declared. The report is `REPORT.md` beside the declaration, opened as a PR to the
   director. It gives the readout's verdicts verbatim, V1 and V2, the distances labelled descriptive, the provenance,
   the `sacct` charge per task, and rulings 3 and 4. It draws no conclusion about `C_stat`. The director takes it to
   Joseph.
4. **The first run's `$B`** is kept until this report merges.

The steps may start once this record is on `main`.

## Not changed

- `C_stat`, `C_ML`, the trunk, every receipt and product.
- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.
