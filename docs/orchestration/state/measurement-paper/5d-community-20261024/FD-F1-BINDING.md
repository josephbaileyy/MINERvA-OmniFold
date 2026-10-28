# Binding: F1, the GENIE v3 held-out bias test of the 16-cell result (2026-10-27)

**By** the paper-tighten lane, as director.

**Under:**
- `DECISION-20261027-joseph-limitation-plan-f1-bias-test-and-flux-bootstrap.md` (PR #423), item 1: 1A runs, as a
  bias test and not a coverage test, under the standing approval for jobs under 12 h;
- `DECISION-20261027-joseph-f1-genie-v3-both-tunes.md` (PR #424): both tunes, seeds fixed a priori, and "the binding
  sets the exact budget".

**Binds** [`FD-F1-DECLARATION.md`](FD-F1-DECLARATION.md), merged in PR #427. Its file sha256 begins
`80d7679cb9a87517`.

**MEASURES:** nothing. It authorizes the declaration's deploy, its tests, the jobs F1a, F1b and F1c as declared, the
grade on a login node, and the HPSS copy.

**CANNOT AUTHORIZE:**
- any charge above §3's ceiling, or any job not in the declaration;
- a GPU, premium QOS, `--requeue`, or any write to CFS;
- any change to the reported covariance, a cell, a readout or κ;
- a rerun or a repair after a STOP;
- a claim, a reading, or printed wording, including the paper's coverage-limitation sentence. That goes through the
  paper lane's PRD read and truth column, then to Joseph (limitation-plan decision item 5).

## 1. The bound code

**The deploy pin** is `5015535e5567c42827e2b618b9b679d534ec47cf`, main after PR #427.
- `OUT=/pscratch/sd/j/josephrb/fd-f1-20261027` and `D=$OUT/deploy/5015535e`, a clean clone of the pin.

**At the PR head `2106256f`, the director checked:**
- the declared test modules, locally with `-I -B` and a TMPDIR: `test_fd_f1.py` **Ran 31 tests, OK**;
  `test_fd_f0_regrade.py` **Ran 47 tests, OK**; 0 porcelain lines after;
- `submit_fd_f1.sh`: every stage carries `--account=m3246 --qos=regular --constraint=cpu --nodes=1 --exclusive
  --no-requeue`, with no GPU request. F1a's limit is 0:20, F1b's comes from a GO `budget.json`, and F1c's is 0:54;
- `fd_f1_budget.py`: GO requires 1.25 × the projected F1b wall ≤ 45 min **and** F1a + F1b + 0.75 ≤ 1.25 node-h;
  `worst_case_node_h` is F1a + F1b's limit + 0.9;
- `fd_f0_regrade.py`: the F1 records are in group `held-out`, which is excluded from the pooled totals; control 9
  compares every F0b record against the committed readout;
- `run_gevgen_v3.sh`: the flux argument ends `,NOWIDTH`.

## 2. Rulings on §7

1. **Flux: phi_t sampled directly is accepted,** with §2's controls: the pinned phi_t and its constrained definition,
   its integral against hFluxCV to 10⁻¹², the bit-for-bit `input-flux.root:spectrum` check in F1a and all 128 F1b
   tasks, and the strict sampling test. The `,NOWIDTH` finding is the review's, and its check is what makes the
   sampling claim measured rather than assumed.
2. **Grading as non-vertex truths, against C_total + C_resp, in their own `held-out` group, is accepted.**
   - The full-matrix grade is the graded result. The leave-out-GENIE+MEC variant is descriptive, for both truths.
     Neither grade is chosen after reading.
   - **The report states the overlaps:** G18_10a_02_11b's 2p2h is the Valencia family of the GENIE+MEC vertex; both
     truths use `NievesQELCCPXSec` for CCQE; both are GENIE-family truths, so they are partial evidence
     (`LIMITATION-PLAN.md` §1.4, 1A).
   - **The two truths are not counted as two independent tests.** Each is reported on its own. No sentence in the
     report sums or combines them as independent.
3. **The spline version is accepted.** G18_10a_02_11b's splines are the ones GENIE ships in the genie_xsec v3_04_00
   product, though its README says v3_02_00. The report gives each tune's README version line and the header check's
   result.
4. **One energy range at 1.12M events per tune is accepted.** The report gives, per tune, the number of generated CC
   events above 50 GeV and the number of fine cells the ratio gate pooled or set to r = 1.
5. **One-node F1c packing through the lane launcher is accepted,** as priced.
6. **The cost enforcement is accepted,** with §3's budget.
7. **The HPSS plan is accepted,** with §4's order.

## 3. Budget

- **The priced budget is 1.25 node-h.** The gate enforces it on the pilot's projection: a projection above it is a
  STOP to the director, not an overrun.
- **The ceiling is `budget.json`'s `worst_case_node_h`,** which is at most 1.98 node-h (0.33 + 0.75 + 0.9). This
  binding authorizes no charge above it.
- **Any job that reaches its scheduler limit is a STOP,** like any other failure.
- **The ledger** records each job's charge from `sacct`, and the report gives the total beside the priced 1.25.

## 4. Conditions

1. **Deploy and tests** (login node):
   - `$OUT` must not exist beforehand, as the declaration's seed search requires (§1);
   - clone the pin to `$D`, detached. HEAD must equal the pin, with 0 porcelain lines (including ignored files);
   - re-measure every §8 digest. Each must match;
   - run `test_fd_f1.py` and `test_fd_f0_regrade.py` at `$D` with root_6_28's Python, `-I -B` and
     `TMPDIR=$OUT/tmp`. Both must pass, with 31 and 47 tests, and 0 porcelain lines after;
   - anything else is a STOP.
2. **F1a,** with `submit_fd_f1.sh f1a $D <pin> $OUT`. A gate STOP, a failed control or a non-zero exit comes to the
   director with `budget.json`, unrepaired.
3. **F1b,** only on GO, with `submit_fd_f1.sh f1b`.
4. **The first receipt commit,** pushed on the report branch, changes only paths under `fd/receipts-f1/`.
   `git diff --stat <pin> <F1c pin>` is in the receipts and lists only those paths. F1c deploys at that commit.
5. **F1c,** with `submit_fd_f1.sh f1c`, then the second receipt commit with the product manifest, under the same
   path rule.
6. **The grade,** on a login node, with the declared argv in F0b's environment. Control 9 must pass. Any refusal is a
   STOP.
7. **HPSS, before the report PR:** the declared tar, `hsi put`, `hashcreate`, `hashverify`, get-back and sha256
   compare, as `stage0_preserve.sh`. The report gives the HPSS path and the tar's digest.
8. **The report is `FD-F1-REPORT.md`, opened as a PR to the director.**
   - It is labelled a bias test at two held-out GENIE v3 truths, not a coverage test, as the readout is.
   - It gives numbers only: per truth, the full-matrix record (b, z, χ²/16, and the trigger counts in the held-out
     group), the descriptive leave-out-MEC record, the closures, f_MEC, and control 9's result.
   - It applies rulings 2–4, gives the cost and HPSS records, and draws no reading.
   - The results index is regenerated in-branch under the standing ruling (a), if needed.
9. **Ledger** rows go in `fd/LEDGER.tsv`. **Retention:** `fd-f1-20261027` joins the pscratch list.

The steps may start once this record is on `main`.

## Not changed

- The reported covariance, every cell, readout and κ. The fake-data limitation stays as stated (decision item 2).
- `docs/analysis-note/**`.
- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.
