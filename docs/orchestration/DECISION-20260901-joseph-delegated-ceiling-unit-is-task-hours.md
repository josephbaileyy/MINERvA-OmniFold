# DECISION 2026-09-01 — the delegated compute ceiling is denominated in TASK-HOURS

**CITABLE FOR:** the unit of the `500 GPU-h / 500 CPU-h` per-arm delegated ceiling, and nothing else.
**NOT CITABLE FOR** ratifying any per-arm ceiling, moving any gate, or authorizing any compute.
`OI-177` remains **OPEN** and unsigned. Gate 2 remains **FAIL**. No scalar-5D covariance is adopted.
Quarantine counts are unchanged at CAND `1 of 7`, QUOTED `0 of 7`.

## Authority

Joseph, 2026-09-01, answering a direct question from the personal-account orchestrator about which
unit the standing per-arm ceiling is written in:

> *"It is task hours"*

His words, in his own turn, in response to the measurement below. Not relayed, not inferred.

## Why the question was asked

`OI-177` asks him to ratify per-arm CPU ceilings. Before signing, the orchestrator measured arm 5 and
found the amendment's figure reconciles **only under one of two readings**:

| arm 5 `uthrow5d_runF`, job `57753245`, 40 tasks | |
|---|---|
| elapsed summed | **49.11 task-hours** ← the amendment's number |
| `AllocCPUS` per task | **50** |
| elapsed × AllocCPUS | **2455.51 core-hours** |

The delegation is written unqualified — *"strictly below 500 GPU-hours and strictly below 500
CPU-hours"* (`DEFECT-20260825-generate-manifest-dirty-warning-nondiscriminating.md:174`,
`:421`, `:444`). **Under task-hours arm 5 is far inside; under core-hours it is ~4.9× over.** A ceiling
whose unit is undefined is not a ceiling, so ratifying `OI-177` without settling this would have
signed a number that does not constrain anything.

**The distinction was already known in this campaign and simply never reached the delegation
sentence.** `SCOREBOARD-20260817-quarantine-seven-causes.md:223` writes both explicitly — *"`39.078`
A100-hours PLUS `55.182` CPU task-hours (`2759.1` CPU-core-hours)"* — and
`INDEX-retracted-and-superseded-values.md:78` carries a standing warning about quoting one column of a
two-unit quantity bare. This is the same hazard family, one level up: not a wrong number, an
unlabelled one.

## THE RULING

> **The per-arm delegated ceiling — strictly under 500 GPU-hours and strictly under 500 CPU-hours — is
> denominated in TASK-HOURS: the sum of `ElapsedRaw` over the arm's tasks. It is NOT core-hours and
> not `AllocCPUS`-weighted.**

## What it settles, measured

Round 2 of the k=0 rehearsal, jobs `57753239`–`57753248`, all seven arms at full population:

| arm | job | n | **task-h (governing)** | AllocCPUS | core-h (not governing) |
|---|---|---:|---:|---:|---:|
| boot5dG | `57753239` | 100 | **14.86** | 32 | 475.64 |
| ssplit5d | `57753243` | 24 | **5.83** | 36 | 210.02 |
| det5dBKG | `57753244` | 19 | **13.76** | 32 | 440.37 |
| uthrow5d_runF | `57753245` | 40 | **49.11** | 50 | 2455.51 |
| uthrow5d_block | `57753246` | 21 | **31.01** | 44 | 1364.33 |
| sweep5dBKGrun | `57753247` | 169 | **26.28** | 32 | 840.81 |
| uthrow5d_combF | `57753248` | 1 | **0.58** | 50 | 28.82 |

**Under the ruling every arm is far inside 500 — the largest is 49.11, about 10% of the ceiling.** No
authority boundary was crossed by this rehearsal, and none of its seven `sbatch` calls needed
authority it did not have.

**What the other reading would have meant, stated so the stakes are on the record and not implied:**
under core-hours, `uthrow5d_runF` at `2455.51` and `uthrow5d_block` at `1364.33` would each have
exceeded the CPU delegation — one by ~4.9× and one by ~2.7× — and the run would have been executed
outside the delegated competence. **It was not.** The ruling resolves an ambiguity in the wording, and
it resolves it in the direction the campaign's own arithmetic had always assumed.

## What this does NOT do

It does not ratify `OI-177`, which stays OPEN and unsigned — §3's proposed 40 CPU-h for arm 5 is dead
on the round-2 actual of 49.11, and §3b's revised 60 is the figure awaiting his signature. It does not
move Gate 1 or Gate 2, adopt any covariance, discharge any quarantine cause, or authorize any further
compute. It does not settle the GPU column's unit by symmetry: the ruling names task-hours for the
ceiling as written, and no GPU-hour reconciliation was measured here.

## One provenance caveat, carried forward rather than resolved

`DEFECT-20260825:172-176` records that the `500 GPU-h / 500 CPU-h` delegation is *"the Codex session's
own written claim about its own authority"* and is **NOT Joseph speaking**. This decision fixes the
UNIT of that threshold as he stated it. **It does not convert the threshold itself into his words**,
and a later lane must not cite this record as evidence that he set 500.
