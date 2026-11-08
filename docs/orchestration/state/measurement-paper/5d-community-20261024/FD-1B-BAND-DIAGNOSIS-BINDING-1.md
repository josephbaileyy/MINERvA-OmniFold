# BINDING 1: the GEANT_Neutron and GEANT_Proton band diagnosis (director, 2026-11-08)

**Binds** [`FD-1B-BAND-DIAGNOSIS-DECLARATION.md`](FD-1B-BAND-DIAGNOSIS-DECLARATION.md) and its code, as merged in PR
#935 at **M = `83ac32fb5024026ac6c51c0621d5ae9ff9073370`**. The audited head is `931ba8bd`. The declaration, the module
and its tests are identical at the two commits.

| file | sha256 (prefix) |
|---|---|
| `FD-1B-BAND-DIAGNOSIS-DECLARATION.md` | `541bf3fe4373c7db` |
| `nd-unfolding/fd_1b_band_diag.py` | `658ca91849a8151a` |
| `nd-unfolding/tests/test_fd_1b_band_diag.py` | `c567aaf6c8ac4060` |
| `fd/receipts-1b/band-diag/code/mutation.py` | `35b4efb7024b1004` |
| `fd/receipts-1b/band-diag/code/mutation.out` | `8b29415afb9cec1a` |

**Under:** `DECISION-20261108-joseph-5d-coverage-and-parallel-studies.md` (#934), item 2: the departure is diagnosed
under a new declaration, in parallel. It does not gate the like-for-like coverage test (LL5D) and cannot change its
primary reading.

## What the director checked

- **The audit.** coverage-5b-audit's NO-GO at `f28f2215` on one text item (C1, the HK record presented as a finding),
  then its GO at `931ba8bd` (https://github.com/josephbaileyy/MINERvA-OmniFold/pull/935#issuecomment-6724475055):
  - 60 of 60 single-site mutants killed, reproduced line for line;
  - 49 tests passing at three hash seeds;
  - the disclosed HK arithmetic reproduced from readout.json `8e05ca9b`;
  - §3 and §4.7 now call the HK reading a record of committed products, not a test.
- **The tests.** At M, the director ran `tests/test_fd_1b_band_diag.py` from a `git archive` of M (`-B`, own
  TMPDIR): 49 passed.

## Rulings

1. **The design is bound as declared at M:** HB0 to HB3, the descriptive channel and out-of-window readouts, and §4.7's
   licences. HK stays a record, not a test. Gate D's FAIL, Part 0, Part 1, 1B's rule (iii) and every earlier record
   stand in every outcome. No repair, and no study of the truth dependence (item c), follows from this campaign.
2. **The steps and the price** are bound as in §7:
   - **P0:** stat-only connect; **P1:** login, `nice -n 19`;
   - **P2, the pilot:** one node, `--time=01:30:00`, 1.5 node-h reserved. Its rebuild controls, §4.3 and its walls
     gate P3, and coverage-5b-audit sees its readout before P3;
   - **P3, the bulk:** 3 jobs at `--time=02:30:00`;
   - **the cap is 9.0 CPU node-h,** with about 4.5 expected. `iris` is read before P2 and before P3 (the last reading,
     2026-11-08 17:10Z, was a balance of 1,698.3 node-h, half 849.1). A REPRICE from the pilot comes back to the
     director.
3. **The job-name family `fd1b_bdg_`** (`fd1b_bdg_p2`, `fd1b_bdg_p3`) is new. The director names it to every lane with
   a live fence before P2's go: ENS1 (`director-helper-3`), RPD-RECO's prologue (Codex2), LL5D (cov2d) and FD-PRR
   (`director-helper-2`).
4. **Shared inputs, checked by real path at P0.** The in-place reads (§6: the inputs npz, the background dump, the 8
   detector-dump weight sets) may share files with ENS1 stage 2, whose tasks read their inputs plainly. The stage-2
   inputs are listed in ENS1's committed `stage2-inputs-stat.txt` (#940). P0 records the realpath of every source and
   compares it with that list.
   - **If any realpath is shared,** this campaign's P1-to-P3 window does not overlap any `ens1_*` job. The connects'
     fence then allows `fd1b_bdg_*` only, and the director sequences the two lanes' gos. §5's atime comparison is not
     narrowed.
   - **If none is shared,** the connects' fence allows `fd1b_bdg_*`, `ens1_*` and `rs1_*`, and the two campaigns may
     run together.
   - P0's receipt states which branch applies.
5. **Each connect** sends its sha256 and path to the director before launch, from a fresh clone at M with empty
   porcelain. `cov2d_fence.sh` runs from the Mac before every connect. ssh's rc is read unpiped. Every `--time` is
   HH:MM:SS, with scontrol's TimeLimit checked. Each receipt goes in as a PR.
6. **The report** gives the readings per §4.4–§4.6 with §4.7's licences, and the cost measured. It goes to the
   director, then to Joseph. No paper or note text.

Nothing is submitted, deposited or tagged.
