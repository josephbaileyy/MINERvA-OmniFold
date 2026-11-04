# BINDING 1 (step one): the B4 stabilisation probe (director, 2026-11-04)

**Binds** [`FD-STAB-DECLARATION.md`](FD-STAB-DECLARATION.md), sha256
`06d8334ae437bf24dcf33229da48991add4596b71f4c28d5ada075669d7856e4`, as merged in PR #720 at
**M = `dd47f98eb4437bd354de78b90db0f05fe1f564b8`** (PR head `e42cca4c`).

**Under** `DECISION-20261102-joseph-bias-and-stabilisation-routes.md` items 1–3 (#714).

**The code, by blob at M:**

| file | blob |
|---|---|
| `nd-unfolding/estimator_stability_probe.py` | `cb382ce1` |
| `nd-unfolding/sbatch_fd_stab.sh` | `10140331` |
| `nd-unfolding/estimator_stability_analyze.py` | `5450ac34` |
| `nd-unfolding/tests/test_estimator_stability_probe.py` | `a581f1be` |
| `nd-unfolding/tests/estimator_stability_mutation.py` | `7340538f` |
| `docs/orchestration/state/measurement-paper/5d-community-20261024/fd/stab/no-ratio.json` | `27947e1a` |

No production module is edited (§8).

## What the director checked

- **The digest.** The declaration's sha256 at M is the one above.
- **The audit.** `coverage-5b-audit` gave four reviews, recorded in #720's comments and in the declaration's §12:
  - the first found six fixes and thirteen gaps;
  - the second found F1–F3: the runner's argparse refused every stability task, the gate could spend into an
    incomplete campaign, and a failed dry run was accepted;
  - the third found G1–G3: §7's claim, the reprice-stop path, and a test gap;
  - the fourth found that the receipt was not tied to its run.
  Each finding is fixed and verified on the delivered code. The last check, at `e42cca4c`, passed 94 tests and the
  committed harness's 68 mutations, and the auditor's own three mutants were killed.
- **The criteria** (§§4–6) match the decision:
  - the stability bar is at most 0.3 (median) and 1.0 (maximum) statistical σ;
  - the bias at every F0b truth must be no worse, against a measured floor;
  - the GiBUU-truth bias is a readout only, outside every criterion and the tie-break, as the auditor verified;
  - inputs are simulated pseudo-data only, so no data are read;
  - there is a terminal branch for "none pass", and an INCOMPLETE outcome.

## Rulings

1. **Step one is bound:** the design and the code at M. Nothing runs at scale before step two.
2. **The cluster lane is `limitation-resolver`** (§7 and §11.2). It accepted after the run-period diagnosis's jobs.
   - It submits, watches and charges both jobs, then pins and reports.
   - Each submission connect's sha256 comes to the director, and the lane waits for the go.
   - Each job runs from a fresh clone at M, with thread caps, nothing written to CFS, and O_NOATIME reads.
   - REPRICE, INCOMPLETE and STOP outcomes come to the director unrepaired.
3. **The dry run** (§11.2): `sbatch_fd_stab.sh dry`, one regular CPU node, `--time=0:45`, eight one-unfold tasks on
   the full run's 8 lanes.
   - It establishes the environment: `setup_salloc_env.sh`, and `lightgbm` and `scipy` must import.
   - It confirms the pv-ladder closure ratio's presence, digest and schema (§11.1).
   - Its record comes to the director before step two.
4. **Step two** binds the full run after the dry run's record, with the gate's 8-lane timings.
5. **The price.**
   - The cap is **8.0 CPU node-h** for the dry run and the full run together, with about 6.4 expected.
   - The coded cumulative gate stops before any launch whose projected total, tail included, exceeds the cap's
     remainder. Slurm's `--time` is the hard limit. A REPRICE stop resumes only through an addendum and the
     director's binding.
   - Joseph was shown about 3.2–6.4 in the scope (#713). The cap is above that range, because the declaration runs
     the required control and a second B3 point (§7). That is reported to Joseph with this binding. It is well
     below half the balance.
6. **The auditor's last nit is a follow-up, not a block:** the `./` spelling in the receipt subtest, which pathlib
   collapses. Its failure mode is fail-closed, a correct receipt refused. limitations-catalog fixes it in a
   test-only follow-up PR, whose test blob step two binds.
7. **Unchanged:** adopting a winner as the single final estimator is Joseph's separate decision (#714 item 2), and
   1B's stage 1 waits for it.

Nothing is submitted, deposited or tagged.
