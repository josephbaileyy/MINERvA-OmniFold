# REPORT — OI-160: the one-replica reproduction ran; its outcome is VOID (2026-10-29)

**By** the close-items session, for the director, who takes it to Joseph
(`DECISION-20261029-joseph-oi160-reproduction-and-q8.md`, item 1).

**Under:** [`DECLARATION.md`](DECLARATION.md) (sha256 `c82b9306447b8674…`) and [`BINDING.md`](BINDING.md) (#493),
at the deploy pin `a1630dd04e73b46c602cee29f1a4f54aa8bd1757`.

**CITABLE FOR:** what the bound job ran and wrote, its controls, its `outcome` under the declared table, and the
measured distances, as description.

**NOT CITABLE FOR:**
- which code wrote the top-level replica;
- any other replica than seed 1, or `C_ML`;
- whether either contract is correct;
- any change to `C_stat`, `C_ML` or the adopted trunk.

This report draws no conclusion about `C_stat`.

## 1. The outcome, verbatim from `run/out/readout.json`

> **`outcome`:** `VOID`
>
> **`reading`:** "the corrected code does not reproduce itself, so no difference can be read"

| flag | value |
|---|---|
| `K1_A1_equals_A2` | **false** |
| `K2_B1_equals_S_pre` | false |
| `A1_equals_S_top` | false |
| `B1_equals_S_top` | false |
| `A1_equals_S_pre` | false |

This is the declared table's VOID row (§3.3): no bitwise match anywhere, and K1 fails. Today's unfold does not
reproduce itself bit for bit, so, by the criterion fixed before the run, no "no" in the table can be read.

## 2. The job

- **One job:** `60484242` on `nid004104` (`shared_milan_ss11`, QOS `shared`). 36 CPUs, 64G, `--no-requeue`, no GPU.
  Submitted once from `login37` at 2026-10-29T07:38:10Z.
- **Result:** COMPLETED, exit `0:0`. Elapsed 00:45:34, against the declared limit of 1:30:00. TotalCPU 18:32:39,
  MaxRSS 12,931,692 K. `AllocTRES` was `billing=36,cpu=36,mem=64G,node=1`.
- **Charge:** 0.7594 h × 36/256 = **0.1068 node-h**, under the standing approval for jobs under 12 h
  (`run/logs/sacct-60484242.txt`).
- **The three unfolds** ran in sequence, each with exit 0: A1 14:23, A2 13:33, B1 17:21.

**§2.1, deploy** (`run/logs/deploy.log`, on `login37`):
- `$B` did not exist beforehand (`run/logs/deploy-session.txt`: `B-absent-before: yes`, from `[ -e "$B" ]` on `login37`);
- HEAD was the pin, with 0 porcelain lines before and after the tests;
- all seven digests matched, `DECLARATION.md`'s being `c82b9306…`;
- `tests rc=0` and "Ran 10 tests … OK".
Search: `[ -e /pscratch/sd/j/josephrb/oi160-repro-20261029 ]` on login37 before the clone, printed in `run/logs/deploy-session.txt` @ a1630dd04

**§3.1, controls** (`run/logs/job.log`), all passed:
- **P0:** the four code files matched `code.sha256`.
- **P1:** the input had 1,548,438,020 bytes and mtime epoch 1782610308. Its sha256 is
  `07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f`, now recorded.
- **P2:** both stored replicas matched `stored.sha256`.
- **P3:** `OMP_NUM_THREADS` was unset, and the affinity was 36.
- **P4:** see §3.

## 3. The provenance files (`run/out/{A1,A2,B1}.provenance.json`)

All three are identical in every field that matters:
- `preimported_under_lib: true`;
- `modules_under_forbidden_root: []`: nothing was loaded from the canonical checkout;
- LightGBM 4.6.0, numpy 1.26.4, Python 3.11.14;
- `affinity_cpus: 36`, `omp_num_threads_env: null`;
- `script_exit: 0`, `script_error: null`.

Each log carries only sklearn's `UserWarning: X does not have valid feature names, but LGBMClassifier was fitted with
feature names`. A1's and A2's logs are identical apart from their output paths.

## 4. The distances — DESCRIPTIVE ONLY

The declaration fixed bitwise equality as the only criterion and **no tolerance** (§3.2). The binding forbids a
reading beyond §3.3's table. **These numbers decide nothing.** They are reported as the declaration requires, to
describe each difference. Relative differences are taken over the bins nonzero in either file.

| pair | bins differing / union nonzero | median relative | max relative | max absolute |
|---|---:|---:|---:|---:|
| A1 vs A2 (K1) | 10,504 / 10,510 | 2.80e-13 | 3.01e-12 | 1.45e-50 |
| B1 vs S_pre (K2) | 10,527 / 10,527 | 9.21e-13 | 8.07e-12 | 4.30e-50 |
| A1 vs S_top | 10,506 / 10,510 | 3.39e-13 | 2.90e-12 | 2.27e-50 |
| B1 vs S_top | 10,653 / 10,653 | 7.42e-03 | 1.0 | 4.82e-40 |
| A1 vs S_pre | 10,653 / 10,653 | 7.42e-03 | 1.0 | 4.82e-40 |
| S_top vs S_pre | 10,653 / 10,653 | 7.42e-03 | 1.0 | 4.82e-40 |

A max relative difference of 1.0 marks a bin that is zero in one file. The output digests are A1 `b6752197…`,
A2 `68e1174c…` and B1 `fd430e02…`.

**Stated without a reading.** Two pairs sit at the scale of A1 vs A2 (about 10⁻¹³ median): A1 with S_top, and B1 with
S_pre. The other three sit at the scale of S_top vs S_pre (0.74% median). Turning that pattern into a reading would mean
choosing a tolerance after seeing the data, which the declaration ruled out (§3.2). Whether to do so, and how, is the
director's and Joseph's decision. Any such reading would need its own declaration, set before it is applied. This
report makes none.

## 5. §4's limits, restated beside the outcome

- **Seed 1 speaks only for its own producer,** array `55805463`. The other 99 top-level replicas had more than one
  producer: that array, the 07-13 interactive loop and array `55871150`.
- **`C_ML` is untouched.** Its 24 split replicas came from `seedscan_split.py` and a different array.
- **A reproduction shows which code ran, not that it was correct,** and VOID shows neither.
- **Nothing here changes `C_stat`, `C_ML` or the trunk.** That is Joseph's separate decision.

## 6. What the run found about the method

K1 failed. Two runs of the same code, on the same input and seed, on one node with 36 CPUs, wrote `xsec_flat` arrays
that differ in 10,504 of 10,510 nonzero bins. They differ only in the 13th significant figure. The declaration took
bit-reproducibility as a precondition and tested it, without assuming it (§3.2). It does not hold for this unfold
today, so the bitwise criterion cannot separate the two contracts on this host. That is the information VOID carries.

## 7. Files and storage

- **Committed under `run/`:** `out/readout.json`, the three `*.provenance.json`, `A1.npz`, `A2.npz` and `B1.npz`;
  `logs/deploy.log`, `logs/deploy-tests.log`, `logs/job.log`, `logs/{A1,A2,B1}.log`, `logs/sacct-60484242.txt`, and
  the deploy and submit session transcripts (`logs/deploy-session.txt`, `logs/submit-session.txt`).
  The empty `%j.out`/`%j.err` are not committed.
- **`$B`** (`/pscratch/sd/j/josephrb/oi160-repro-20261029`) is removed after this report merges, as §8 and the binding
  require. Nothing was written to CFS or to the canonical checkout.
- **Nothing was resubmitted.**
