# Binding: the 5B run-period block audit (2026-10-30)

**By** the paper-tighten lane, as director.

**Under** `DECISION-20261030-joseph-4b-not-now-5b-audit-then-add.md` (#542), item 2: "audited, then added".

**Binds** [`FD-CT-5B-AUDIT-DECLARATION.md`](FD-CT-5B-AUDIT-DECLARATION.md), merged in PR #546, with its reader, tests,
mutation receipt and review. Its file sha256 begins `65213f15a68010e5`.

**MEASURES:** nothing. It authorizes the deploy and tests, and one run of the reader `fd_ct_5b_audit.py` on a login
node at 0 node-h.

**CANNOT AUTHORIZE:**
- adding the block. That is its own declared step (§8), taken only if `stop` is false;
- any change to the reported matrix, a claim or printed wording;
- a rerun after a refused control;
- any Slurm job, GPU use or write to CFS.

## 1. The bound code

**The deploy pin** is `6dd415391da44d3d996bed7ab39a0654a2a5345e`, main after PR #546.
- `BA=/pscratch/sd/j/josephrb/fd-ct-5b-audit-20261030` and `D=$BA/deploy/6dd41539`.

**At the PR head `37ede1cf`, the director checked:**
- all 19 §14 pins, each against its file;
- the declared three test modules, locally with `-B` and a TMPDIR: **Ran 210 tests, OK (skipped=4)**. The skips are
  the ROOT-only tests, which run on the cluster. The deploy must show none skipped;
- the mutation receipt: 54 of 54 killed in pass 2;
- §7's STOP condition, `stop` = O ∨ N ∨ R, with its thresholds as frozen in the design and unchanged since. The
  controls leave the condition undecided, and the block is then not added.

## 2. Rulings on §13

1. **The descriptive residual's χ²₁₄** is accepted. A 2-parameter fit on 16 cells leaves 14 degrees of freedom, and it
   has no stop role.
2. **Clause N's low power** is accepted as stated. Its threshold stays at 0.5. The report says in words that N fires
   only when the replica blocks' size is itself unstable.
3. **The added refusing controls** are accepted. Each one only refuses more.
4. **The leak guard's table** holds the 5B integrals. 2D's are on 205 cells and are never written.
5. **5A's noise on the 2D double ratios,** controlled against 2D's committed noise share, is accepted.
6. **The retyped 2D loader** is accepted, because importing it would put cluster paths at `sys.path[0]` (OI-136). A
   control checks its outputs against the committed digests.

## 3. Conditions

1. **Deploy and tests,** as §10.1. `$BA` must not exist beforehand. The deploy log must show HEAD = pin, 0/0
   porcelain lines, the §14 digests and "Ran … tests … OK" with no skip. Anything else is a STOP.
2. **The run,** as §10.2, once. A refused control (exit 1) or a leak-guard refusal (exit 3) is reported unrepaired,
   with the condition undecided.
3. **The report is `FD-CT-5B-AUDIT-REPORT.md`, opened as a PR to the director.** It gives `stop_condition` verbatim,
   each clause's statistic, threshold and decider, and the descriptive numbers labelled as such.
   - If `stop` is false, it names §8's addition step as the next declaration.
   - If `stop` is true, it names the clause and draws no repair.

The steps may start once this record is on `main`.

## Not changed

- The reported covariance and every claim.
- Nothing is submitted, deposited or tagged.
