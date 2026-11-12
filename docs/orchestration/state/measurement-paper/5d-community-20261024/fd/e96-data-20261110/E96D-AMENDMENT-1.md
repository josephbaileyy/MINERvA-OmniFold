# E96D AMENDMENT 1, DRAFT: the full run's time limit, after the dry run's projection failure (2026-11-11)

**By** the valid-region lane (director-helper-2), at the director's request after the dry run's STOP.

**For** the director's binding, after coverage-5b-audit's audit. **It does not edit** `E96D-DECLARATION.md` or
E96D-BINDING-1. **Nothing runs** until this amendment is audited and bound, and not before NERSC's maintenance of
2026-11-11 ends.

## The director's rulings (2026-11-11), written in

1. **Option (a) is chosen:** one full job at `--time=4:15:00`, with the gate's bound t ≤ 962.1 s. The cap is
   **5.1 node-h**, which is 0.3 % of the 1525.6 node-h balance read on 2026-11-11, so it is within the director's
   authority.
2. **The 2026-11-11 dry products stay as the STOP record.** They are not read, carried in or deleted.
3. **A new dry run at M_A1 is required** before any full run (§Common to both options).
4. **A t above 962.1 s STOPs again** at the gate, unrepaired. There is no further amendment for time in this study
   unless the director rules one.
   - **The trigger:** a second time-STOP (the projection control failing at M_A1) comes to the director as a
     decision, not as a re-price. The lane reports it and drafts nothing.
5. **The slower-unfold cause is left unmeasured,** as the dry receipt leaves it.
   <!-- absence-ok: the director's ruling on this study's scope; no cause measurement is declared or run -->

6. **Scheduling:** E96D's new dry run and full run wait until LL5D's two gate jobs, 61078463 and 61078506, have ended
   and their receipts hold their atime readings.
   - **Why:** LL5D is the paper's critical path, and its gate compares the atimes of the same two inputs E96D reads
     plainly.
   - **The fence** runs before each connect.
   - **If the LL5D gates are still PENDING a day after the maintenance ends,** the lane tells the director rather than
     going ahead.

## The code (option (a)), on this branch

| file | change | sha256 |
|---|---|---|
| `nd-unfolding/ensemble_estimator_data.py` | `FULL_TIME_S = 4.25 * 3600`, was `3.5 * 3600`, with its comment | `414f7d352560b1cd310666af8e363fe294fda6ebb13239309887cb96c5f0b33a` |
| `nd-unfolding/sbatch_e96data.sh` | the header's full line reads `--time=4:15:00` (a comment; no executed line changes) | `72680b62d48e07554e1c8ac07dc6bd7289798892bdfaa08f0733068c8d17ec7e` |
| `nd-unfolding/tests/test_ensemble_estimator_data.py` | see below | `186d881a29fc51c1941bd9a3d575061f4b841692c198b437ea02ff40abb35469` |
| `nd-unfolding/tests/ensemble_estimator_data_mutation.py` | see below | `2a7187422715599f3186e29ee2902c46ab50ce3ce08cea8356f8dc19a0f3cdbd` |

**The test changes:**
- **The "slow" fixture** now has t = 965 s (seconds_unfold 950 + seconds_load 15). The old 900 s would pass the
  amended bound.
- **A new REQUIRED test,** `test_the_amended_limit_admits_the_measured_t_and_stops_above_962`:
  - FULL_TIME_S is 4.25 h;
  - the gate records lane_max 14 and limit_s 15,300;
  - t = 907.572 s (the 2026-11-11 measured value) and 962 s pass;
  - 963 s fails with rc 8.

**The mutation changes:**
- **A new REQUIRED mutant,** "the 3:30:00 limit restored", which puts `3.5 * 3600` back.
- **A second mutant,** "the amended limit raised further", which sets `4.5 * 3600`.
- Both are killed by the new test.
- EXPECTED_TESTS is now 31.

**The local run** (2026-11-11, this branch, python3 -B):
- `unittest` ran 31 tests, OK.
- The mutation check gave `UNMUTATED SUITE: 31 tests, rc 0` and `MUTATION CHECK :: PASS (43 mutations)`, 16 of them
  REQUIRED, every one killed by its named test.
- The receipt is `receipts/a1-code/mutation-receipt.txt`.

The bound ENS1 probe, FD-STAB's refusals and every other line of the four files are unchanged (`git diff` against
M_E96D `1d25f8e7`).

## Why

- **The dry run's gate failed on its projection** (the receipt is PR #1065,
  `receipts/dry-20261111/README.md`). The run was job 61137569 on 2026-11-11, at M_E96D `1d25f8e7`.
  - A-D0, A-D1 (the control reproduces (e)'s xsec_flat bitwise), k = 1's declared call and the one-code check all
    passed.
  - The projection failed: lane_max 14 × t 907.572 s + 300 s = 13,006 s, against 0.9 × 12,600 s = 11,340 s.
- **The measured walls** were 14:46 for the control and 15:10 for k = 1, with per-unfold t of 883.257 s and 907.572 s.
  The declaration's unit was 657 s. No cause is offered (none was measured).
- **The bound rule did its job:** at this t, a 3:30 full run would have been expected to time out.

## What does not change

- **The declaration's call, modes, controls (A-D0 to A-D3), readout, quotable fields and licence.**
- **The projection gate itself.** The rule stays "lane_max × the dry run's slowest per-unfold t + 300 s ≤ 0.9 × the
  limit", with lane_max the list-scheduling bound ⌈Σ/8 + max_task × 7/8⌉. The gate runs inside the dry job, and full
  refuses without a passing GATE.json at its pin and queue sha.
- **8 lanes per node, 32 threads per unfold,** and the job family `e96data`.

## Common to both options: a new dry run

The job script's full mode requires the dry DONE and GATE.json at the same pin as the full run (`sbatch_e96data.sh`,
the `full` refusals). Either option changes bound code, so its pin is a new commit M_A1. The 2026-11-11 dry products
are at `1d25f8e7` and cannot carry in.

- **The new run:** a new dry run at M_A1 in a new directory (`/pscratch/sd/j/josephrb/e96data-<date>/`), with the
  same two tasks. It costs about 0.26 node-h, the 2026-11-11 job's 15:38.
- **What it gives:** it re-measures t on the day, and the projection is evaluated on that t.
- **The 2026-11-11 run** stays as its STOP record. Its products are not read.

## The two options

The prices use t = 907.572 s (k = 1, 2026-11-11), and "t up to about 950 s" as the director asked. Node-h are
exclusive single-node hours, as in the declaration's price table. Every figure is **arithmetic** from the measured t
and the full queue (50 tasks, 97 unfolds: F₆₄ 1, the repeat 1, k = 2–95 in 47 pairs, k = 96 alone).

### (a) One full job, with the limit raised to 4:15:00

- **The code change:**
  - `ensemble_estimator_data.py`: `FULL_TIME_S = 4.25 * 3600`, with its comment;
  - `sbatch_e96data.sh`: the header's full line reads `--time=4:15:00`;
  - the gate tests' thresholds move with the constant.
  - The queue, the task lines and A-D3 are unchanged.
- **The gate's bound:** t ≤ (0.9 × 15,300 − 300) / 14 = 962.1 s. That allows 6 % above the measured 907.6 s, and
  covers 950 s.
- **The expected wall:** 13,006 s = 3.61 node-h at the bound's 14 unfolds. Under queue-order list scheduling, the
  largest lane holds 13 unfolds, giving 12,098 s = 3.36 node-h. At t = 950 s, the bound gives 3.78 node-h.
- **The ceiling:** 4.25 node-h, from `--time` on one exclusive node.

| run | expected node-h | `--time` | ceiling |
|---|---:|---|---:|
| the new dry run | 0.26 | `0:30:00` | 0.50 |
| full | 3.36–3.61 | `4:15:00` | 4.25 |
| **A1's runs** | **3.6–3.9** | | **4.75** |
| with 2026-11-11's dry run (0.26, spent) | 3.9–4.1 | | **cap 5.1** |

### (b) The full queue split into two jobs, each under the current 3:30:00

- **The code change:**
  - `tasks` writes `full-a.tsv` (tasks 1–25: F₆₄, the repeat and k = 2–47, 48 unfolds) and `full-b.tsv` (tasks
    26–50: k = 48–96, 49 unfolds).
  - The gate projects each part by the same rule and pins both queue shas. Each part's full job refuses without a
    passing gate for its own queue.
  - `sbatch_e96data.sh full` takes the part. Its log becomes `log-full-a` or `log-full-b`, each with its own DONE.
  - `analyze` reads both parts and requires both DONEs.
  - A-D3's repeat stays in part a, at 8-lane packing.
- **The gate's bound:** each part's lane_max is 8, so t ≤ (0.9 × 12,600 − 300) / 8 = 1,380 s.
- **The expected wall:** per part, 7,561 s = 2.10 node-h at the bound, or 6,653 s = 1.85 node-h under list
  scheduling (7 unfolds). Both parts together come to 3.70–4.20 node-h.
- **The ceiling:** 2 × 3.5 = 7.0 node-h at 3:30:00 each. A 2:30:00 limit would still meet the rule up to
  t = 975 s, and would bring the ceiling to 5.0.

| run | expected node-h | `--time` | ceiling |
|---|---:|---|---:|
| the new dry run | 0.26 | `0:30:00` | 0.50 |
| full-a and full-b | 3.70–4.20 | `3:30:00` each | 7.00 |
| **A1's runs** | **4.0–4.5** | | **7.50** |
| with 2026-11-11's dry run (0.26, spent) | 4.2–4.7 | | **cap 7.8** |

## Recommendation: (a) (chosen by the director, ruling 1)

- **The smallest code change:** one constant, a header line and its tests. The queue, the task lines, the job
  script's refusals and `analyze` are unchanged, so the audit is short.
- **The cheaper run:** expected 3.36–3.61 node-h against 3.70–4.20, because (b) pays two setups and two tails.
  The ceiling is 4.25 against 7.0, or 5.0 at 2:30.
- **A-D3 stays as declared,** one full run at one 8-lane packing.

**What (b) buys:** two shorter jobs, each 2.1 h at the bound, which can run on two nodes at once or fit a shorter
window. That matters only if a 4:15 job queues much worse than two 3:30 jobs, which has not been measured.
<!-- absence-ok: a statement about this draft's own evidence; no queue-wait measurement was taken for either limit -->

**Under either option, a t above the new bound STOPs again at the gate,** unrepaired: above 962.1 s for (a), or
1,380 s for (b).

## Scheduling (for the director)

- **After the maintenance,** LL5D's two gate jobs (`ll5d_gate_G18` 61078463 and `ll5d_gate_AR23` 61078506) are
  queued, and they read the same two inputs. Their receipts compare those files' atimes before and after.
- **If E96D runs while they do,** its plain reads move the same atimes. The stat-only readings before and after
  (2026-11-11's dry receipt) would then be repeated around each E96D job.
- **Whether to wait for LL5D's gates to end first** was the director's call. It is ruling 6: E96D waits.

## Licence

This amendment changes the run's time limit and price only. **NOT CITABLE FOR** any E₉₆ or F₆₄ statement, a cause
of the slower unfolds, or any change to (e), C_e or any record. The declaration's licence holds unchanged.

Nothing is submitted, deposited or tagged.
