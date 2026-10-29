# Binding: OI-160, one bootstrap replica reproduced under each seed contract (2026-10-29)

**By** the paper-tighten lane, as director.

**Under** `DECISION-20261029-joseph-oi160-reproduction-and-q8.md` (#487), item 1: the reproduction "runs under the
standing approval for jobs under 12 h, declared and bound as usual".

**Binds** [`DECLARATION.md`](DECLARATION.md), merged in PR #490. Its file sha256 begins `c82b9306447b8674`.

**MEASURES:** nothing. It authorizes the declaration's deploy and tests on a login node, and its one CPU job.

**CANNOT AUTHORIZE:**
- any change to `C_stat`, `C_ML`, the adopted trunk, a receipt or a published value, which is Joseph's separate
  decision;
- any second job, a resubmission, GPU use, premium QOS or a write to CFS or to the canonical checkout;
- a reading beyond §3.3's table, or any claim about the other 99 replicas or `C_ML`.

## 1. The bound code

**The deploy pin** is `a1630dd04e73b46c602cee29f1a4f54aa8bd1757`, main after PR #490.
- `B=/pscratch/sd/j/josephrb/oi160-repro-20261029` and `D=$B/deploy/a1630dd0`.

**At the PR head `100823ea`, the director checked:**
- the six §7 pins: `run_job.sh` `46d0afac`, `repro_run.py` `649b1291`, `repro_compare.py` `456d6bce`,
  `test_repro.py` `30589eec`, `code.sha256` `5da5283b`, `stored.sha256` `8e3cf248`;
- `code.sha256` against git: A's `bootstrap_nd.py` `da0f7724` is `07c18aee`'s, and B's `57c4f2bb` is `07c18aee^`'s
  and `c70397e04`'s;
- the declared §2.1 test command itself, from `/` with `-I -B`: **Ran 10 tests, OK**, with 0 porcelain lines (including
  ignored files). At the previous head, `88b2f9f8`, that command failed with `ModuleNotFoundError`. The director returned
  it, and the session fixed the command without changing any pinned file;
- `run_job.sh`'s SBATCH lines: `--qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=36 --mem=64G
  --time=01:30:00 --no-requeue --account=m3246`, with no GPU request.

## 2. Rulings

1. **QOS `shared` with 36 CPUs is accepted** in place of the director's "regular". It matches the allocation of both
   stored runs, which is what makes K2 meaningful. It is not a premium QOS.
2. **The criterion is bitwise equality, with K1 and K2,** and the §3.3 table, as declared. No tolerance is set, and no
   distance decides anything.
3. **§4's limits stand.** The report restates them beside the outcome: seed 1 speaks only for its own producer
   (`55805463`), and `C_ML` is untouched.

## 3. Conditions

1. **Deploy and tests,** exactly as §2.1, with `<pin>` = `a1630dd04e73b46c602cee29f1a4f54aa8bd1757`.
   - `$B` must not exist beforehand.
   - It must show HEAD equal to the pin, 0 porcelain lines before and after, the §7 digests, `tests rc=0` and "Ran 10
     tests". Anything else is a STOP.
2. **The job,** with §2.2's command exactly, submitted once. Any control STOP (P0–P4), exit other than 0 or timeout is
   a STOP, reported unrepaired. Nothing is resubmitted without a new binding.
3. **The report is `REPORT.md` beside the declaration, opened as a PR to the director.** It gives the readout's
   `outcome` and `reading` verbatim, every equality flag, the distances labelled descriptive, the three provenance files,
   the `sacct` charge, and §4's limits. It draws no conclusion about `C_stat`. The director takes it to Joseph.
4. **Storage** as §8: nothing in CFS or the canonical checkout, and `$B` removed after the report merges.

The steps may start once this record is on `main`.

## Not changed

- `C_stat`, `C_ML`, the trunk, every receipt and product.
- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.
