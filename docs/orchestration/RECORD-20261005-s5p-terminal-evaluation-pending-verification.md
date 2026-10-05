# s5p (`OI-193`): terminal evaluation outputs, PENDING the independent recompute (2026-10-05)

**CITABLE FOR:**
- production reaching terminal, and the evidence for it;
- the evaluation deploy;
- the paths and sha256 of the four frozen-procedure outputs, with committed copies;
- what those outputs contain, transcribed from the files.

**NOT CITABLE FOR:**
- **The recorded joint result.** Amendment 7 `validation_and_assurance` (v) bars recording it before the independent
  recompute report (`gbdt independent`, its handoff §5). This record transcribes outputs; it decides nothing.
- **Any interpretation of the missing-seed sensitivity label.** CHECKLIST-20261001 §3 makes that Joseph's decision.
- **Any of the four final status fields** (CHECKLIST §4).

## 1. Terminal (CHECKLIST §1)

`stage7/s5p_terminal_run.sh check`, run on saul at 2026-10-05T20:32Z, printed `TERMINAL: YES` (rc 0). Every clause
passed:

| null | final B | stop reason |
|---|---:|---|
| `MnvTune_v1` | 1365 | rule met for both tests |
| `GENIE_2_12_10_CV` | 1366 | rule met for both tests |
| `GENIE_2_12_10_MEC` | 1343 | rule met for both tests |
| `NuWro_21_09` | 1751 | rule met for both tests |
| `GiBUU_2019` | 1351 | rule met for both tests |

The other clauses:
- power: `queue done` in `/pscratch/sd/j/josephrb/s5p-20260926/runs/queue-prod-r3-pow.log` (2026-10-04T15:42:06Z);
- `squeue`: rc 0, with no s5p cal/pow job;
- meter: rc 0, open concurrency cpu/gpu 0.0/0.0;
- no runner process and no queue-runner session leader on login33.

The campaign-state incident at the terminal entry has the details.

## 2. Evaluation

- **Deploy:** a new clean clone of origin/main `e9372b757250e9607f52e471d9b0c447b08e65d5` at
  `$NS/deploy/e9372b75`. `deploy` verified it VALID:
  - HEAD and a clean tree;
  - `s5p_joint.py`, `s5p_inference.py` and `s5p_seqstop.py` byte-identical to `4f5a613f`;
  - design `404446eb…` and V `35979ef7…`.
- **Code since the production deploy:** between `756e1d6c` and the evaluation commit, PR #15 changed only
  `nd-unfolding/pet/**`, `nd-unfolding/tests/**` and two `.md` logs. No top-level `nd-unfolding/*.py` changed.
- **Run:** `evaluate` ran detached on login31 from 20:35:24Z to about 20:37Z. Its log is
  `/pscratch/sd/j/josephrb/s5p-20260926/stage7/evaluate-run-20261005T203524Z.log`. It re-ran the terminal and deploy
  checks, then ran evaluate, labels, seed states and the missing-seed sensitivity. Exit 0; sensitivity `COMPLETE`.

| output (`$NS/stage7/joint/`; repository copies in `state/s5p/stage7/joint/`, see below) | sha256 |
|---|---|
| `joint-evaluate.json` | `b9604502b1aa263508ba46f0be91846d7a2106f6f2fd0ba5c172b87ee256dd11` |
| `robust-labels.json` | `206655f906bdffac636676f39ed86267f31eb9600ed9d45a335905fdaf7fde2a` |
| `seed-states.json` | `6823e701064b5dfc1286015be88b6d660e8f64099dc5bf3bff99b783724e58a8` |
| `missing-sensitivity.json` | `f48e16ef351ea78c59b7e75f5bf653dc5742857457786e3d8fd1a067be8e2293` |

**The repository copies:**
- `joint-evaluate.json`, `robust-labels.json` and `missing-sensitivity.json` are byte-identical to the cluster files;
  each sha256 was re-computed on the copy.
- `seed-states.json` is not copied byte for byte. It cites its 1462 task logs by bare filename (`"log": "s5p-…out"`),
  so the pre-commit receipt-artifact check refuses it: those logs are cluster files, not repository artifacts. The
  repository therefore carries `seed-states.abs-log-paths.json` (sha256
  `bd25f1ec03ac07a205aed533193fa291bef785525529b1e5bf54a45984eaf031`). It is derived from the original by one
  transformation: each of the 1462 `"log": "` values is prefixed with
  `/pscratch/sd/j/josephrb/s5p-20260926/runs/prod/logs/`. Removing that prefix reproduces the original exactly
  (sha256 `6823e701…`, checked when the copy was made). The cluster file remains the canonical object.

## 3. What the outputs contain (transcribed; pending verification)

**Primary decisions** (`joint-evaluate.json` `decisions`; Holm with determinacy, α = 0.05, m = 10, 95% CP
intervals). All 10 read `rejected`.

| test | k | B | p | Holm threshold | 95% interval |
|---|---:|---:|---:|---:|---|
| NuWro total | 0 | 1751 | 1/1752 | 0.005 | [0, 0.00210] |
| GENIE CV total | 0 | 1366 | 1/1367 | 0.00556 | [0, 0.00270] |
| GENIE CV shape | 0 | 1366 | 1/1367 | 0.00625 | [0, 0.00270] |
| MnvTune total | 0 | 1365 | 1/1366 | 0.00714 | [0, 0.00270] |
| MnvTune shape | 0 | 1365 | 1/1366 | 0.00833 | [0, 0.00270] |
| GiBUU total | 0 | 1351 | 1/1352 | 0.01 | [0, 0.00273] |
| GiBUU shape | 0 | 1351 | 1/1352 | 0.0125 | [0, 0.00273] |
| MEC total | 0 | 1343 | 1/1344 | 0.0167 | [0, 0.00274] |
| MEC shape | 0 | 1343 | 1/1344 | 0.025 | [0, 0.00274] |
| NuWro shape | 1 | 1751 | 2/1752 | 0.05 | [0.0000145, 0.00318] |

The p-values are Monte Carlo (k + 1)/(B + 1); none is zero.

**Robustness labels** (`robust-labels.json`, schema 2, per `RULING-20260929-s5p-A7-robustness-flag.md`; κ = 3 replace
family). All 10 read `robust to the sub-fine residual`, and every κ = 3 replace decision is `rejected`. In that family,
NuWro shape is k = 2 and p = 3/1752.

**Seed states** (`seed-states.json`): 1462 tasks finished and 137 were killed, every kill a TIME LIMIT.

| lane | completed | interrupted | never started |
|---|---:|---:|---:|
| MnvTune | 1365 | 22 | 13 |
| GENIE CV | 1366 | 17 | 17 |
| GENIE MEC | 1343 | 25 | 32 |
| NuWro | 1751 | 27 | 22 |
| GiBUU | 1351 | 20 | 29 |

The power sets have their own counts. Among completed draws, runtime shows no clear association with the statistic:
per lane, |ρ| ≤ 0.06, and all but one permutation p exceed 0.05 (MEC shape raw p = 0.044, node-adjusted 0.066). The
file's own reading limit applies: "a null association does not establish that the missing experiments are unbiased".

**Missing-seed sensitivity** (`missing-sensitivity.json`; labelled report-only; status COMPLETE; no unestablished
seed):
- **Per test:** every test reads `can change (counterexample: worst_interrupted, worst_all_missing)`.
- **worst_interrupted** (every interrupted draw exceeds the observed statistic): p ranges from 0.0130 (CV) to 0.0190
  (MEC), and all 10 are `not rejected`.
- **worst_all_missing:** p ranges from 0.0250 to 0.0414, and all 10 are `not rejected`.
- **best_all_missing:** all 10 are `rejected`.
- **Certificates:** the sufficient all-assignment certificate certifies no rejection, in either missing class, for
  either the primary or the κ = 3 family. The 95% CP upper end at (k + M, B + M) exceeds α/m = 0.005.
- **Stopping:** at each null's final look, the frozen stopping rule holds under best_all_missing but not under either
  worst corner.
- **Power:** bounds per power set, conditioning on the retained null calibration.

This is a labelled sensitivity. The primary decisions are reported as the evaluator gives them, and they are not
revised by this step (CHECKLIST §3). Whether the label enters the deliverables as a stated condition, or otherwise,
is Joseph's decision.

## 4. Next

1. Send the packet in §2 to `gbdt independent`. It re-measures terminal state itself and runs its own deploy and
   seed disposition.
2. Record the joint result only after its report.
3. Ask Joseph how the missing-seed label enters the claims. That interpretation is his decision under §3.
4. Then the Stage-7 deliverables and the four fields, under CHECKLIST §4.
