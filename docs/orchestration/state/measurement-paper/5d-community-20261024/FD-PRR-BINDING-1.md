# BINDING 1: FD-PRR, the prior-retention study (director, 2026-11-08)

**Binds** [`FD-PRR-DECLARATION.md`](FD-PRR-DECLARATION.md) (rev 2) and its code, as merged in PR #937 at
**M = `a5235714a379457f09c539a2c94054354640648c`**. The audited head is `493ea6b4`; the declaration and every file under
`nd-unfolding/prior_retention/` are identical at the two commits.

| file | sha256 (prefix) |
|---|---|
| `FD-PRR-DECLARATION.md` | `5be1e19cb8db6706` |
| `nd-unfolding/prior_retention/prr_probe.py` | `f87ee90c58d2b890` |
| `nd-unfolding/prior_retention/prr_ibu.py` | `17acad82bad7c43f` |
| `nd-unfolding/prior_retention/prr_read.py` | `f35bc3282b50215d` |
| `nd-unfolding/prior_retention/sbatch_prr.sh` | `323f491afa2038a5` |
| `nd-unfolding/prior_retention/test_prr.py` | `33bfdf099077dbc4` |
| `nd-unfolding/prior_retention/prr_mutation.py` | `28f3f9e5edf1e63c` |

**Under:** `DECISION-20261106-joseph-plateau-next-work.md` item 2 (the prior-retention study, authorized and paused) and
`DECISION-20261108-joseph-5d-coverage-and-parallel-studies.md` item 3 (released).

## What the director checked

coverage-5b-audit's GO at `493ea6b4` (https://github.com/josephbaileyy/MINERvA-OmniFold/pull/937#issuecomment-6728818077):
- 103 tests pass and 62 of 62 mutants are killed by their named tests at the head, matching the committed receipt
  (made at code commit `0478e727` in a clean clone; the failed first run, 59 of 62, is kept as
  `mutation-run1-fail.txt`);
- the §8.1 digests match; the §10.3 packing, rebuilt independently, gives the 27.0 cap exactly;
- the director's rulings 1–2 are carried in the licences, `prr_read.LABELS` and `clears()`;
- C-CT reproduces F0b's committed σ to 0 and its closure_nuwro χ² to 1.9e-14;
- the §10.4 ENS1 queue check works, and both its mutants are killed.

## Rulings

1. **The design is bound as declared at M:** both routes (one factor at a time on FD-STAB's noise-free closures at the
   12 graded truths, and REF-G1's IBU on the same expectation experiments), the floor, the readings PR-1 to PR-3 and the
   descriptive R-ID and R-SUP.
2. **No level is adopted, whatever PR-3 shows** (FD-STAB §6's terminal rule). A level that clears the flagged truths is
   a finding about the mechanism; any change to the reported procedure needs a new decision by Joseph and its own
   held-out test.
3. **Grading at F0b's truths is description only.** NOT CITABLE FOR a held-out performance claim, or that any level
   "would pass". PR-3 reads "clears / does not clear at these truths".
4. **The price.** The cap is **27.0 CPU node-h**, the sum of the five jobs' limits (prr_dry 4:45:00, prr_iter 7:30:00,
   prr_cap 9:00:00, prr_misc 4:45:00, prr_ibu 0:30:00), with about 12.8 expected. A gate refuses a full job whose
   projection is above 0.9 × its `--time`, and no limit is raised without an addendum. `iris` is read before each
   connect.
5. **Sequencing.** prr_dry is submitted only after ENS1's stage 2 has ended and its post-run and analysis are done (the
   script's ens1_* queue check enforces the first part). Shared inputs with ENS1, the band diagnosis and LL5D (the
   inputs npz, the background dump and the bank's cv.npz, `receipts-ll5d` overlap check #949) are read only through
   noatime copies with per-file stat records before and after; no two lanes' connects copy at the same time. Directory
   atimes are not a control.
6. **The job-name family `prr_*`** is new. The director names it to every lane with a live fence before the first prr_
   go.
7. **Each connect** sends its sha256 and path to the director before launch, from a fresh clone at M with empty
   porcelain. ssh's rc is read unpiped, every `--time` is HH:MM:SS with scontrol's TimeLimit checked, and each receipt
   goes in as a PR.
8. **The report** gives PR-1 to PR-3 and the descriptive readouts with their licences, and the cost measured. It goes to
   the director, then to Joseph. No paper or note text.

The audit's two lows (the dry gate's 657 s unit against the 1,062 s `--time`; C-IBU(a) exercised only on the cluster)
are held for the follow-up list. Both fail safe.

Nothing is submitted, deposited or tagged.

## Binding 1, addendum A1: the job script sources its environment first (director, 2026-11-09)

**Binds** [`FD-PRR-ADDENDUM-A1.md`](FD-PRR-ADDENDUM-A1.md) and its code, as merged in PR #966 at
**M_A1 = `6727020a7c58b00dd00806151c627c8a24f72402`**. The audited head is `3c612c12`; every file under
`nd-unfolding/prior_retention/` is identical at the two commits. This **supersedes M above** for every FD-PRR job.

| file | sha256 (prefix) |
|---|---|
| `FD-PRR-ADDENDUM-A1.md` | `ca6b8457e74c9323` |
| `nd-unfolding/prior_retention/sbatch_prr.sh` | `10290087cdd57d97` |
| `nd-unfolding/prior_retention/test_prr.py` | `44223143a6982fb8` |
| `nd-unfolding/prior_retention/prr_mutation.py` | `4666aa0654dccbe9` |

`prr_probe.py`, `prr_ibu.py` and `prr_read.py` are M's bytes.

**What led to it.** Before any connect, director-helper-2 found that `sbatch_prr.sh:34` ran `python3 prr_probe.py limit`
before sourcing `setup_salloc_env.sh`. Under the login environment's `/usr/bin/python3` 3.6.15, `from __future__ import
annotations` is a SyntaxError, so the job would refuse at once. RS1's A1 hit the same order on 2026-11-07 (#905).

**What the director checked:** coverage-5b-audit's GO at `3c612c12`
(https://github.com/josephbaileyy/MINERvA-OmniFold/pull/966#issuecomment-6730268631): the diff is the one source line, its
REQUIRED test and the mutant "limit above the source"; no python3 call precedes the source on any path; each half of the
test kills the mutant alone; 104 tests and 63 of 63 mutants reproduce at the head.

**Rulings:**
1. **Every FD-PRR job runs from M_A1.** BINDING 1's rulings 1–8 stand otherwise.
2. **The connects carry the audit's two lows:** the login-side `prr_probe.py limit` call that sets `--time` runs under
   root_6_28's python3 after sourcing, in a subshell, as the job does; and the source's rc is checked with its own STOP
   message before any limit call.

## Binding 1, erratum E1: ruling 4's per-job limits (director, 2026-11-09)

**The defect.** Ruling 4 lists the job limits as prr_dry 4:45:00, prr_iter 7:30:00, prr_cap 9:00:00, prr_misc 4:45:00
and prr_ibu 0:30:00. Those are rev 1's limits, and they sum to 26.5, not the 27.0 the same ruling states. director-helper-2
found it while drafting the prr_iter connect.

**What is bound, and always was:** the declaration rev 2, §10.3 (`FD-PRR-DECLARATION.md`:506–513 at M_A1), and
`prr_probe.py`'s `JOB_LIMIT_H` (line 201 at M_A1 `6727020a`), which set `--time` in every connect and job:

| job | --time | node-h |
|---|---|---:|
| `prr_dry` | 5:15:00 | 5.25 |
| `prr_iter` | 7:30:00 | 7.50 |
| `prr_cap` | 6:30:00 | 6.50 |
| `prr_misc` | 7:15:00 | 7.25 |
| `prr_ibu` | 0:30:00 | 0.50 |
| **total, the cap** | | **27.00** |

Ruling 4's per-job list should read as this table. The cap, 27.0 CPU node-h, the 0.9 × `--time` gate and every
other ruling are unchanged. No job ran under the wrong limits: prr_dry (61022062) ran at 5:15:00, and prr_iter
(61024185) was submitted at 07:30:00 against this file's earlier bytes (`e3d8724b`), with the same limits.

**For the connects:** prr_cap, prr_misc and prr_ibu pin this file's sha256 as it is on main after this erratum merges.

Nothing is submitted, deposited or tagged.

## Binding 1, addendum A2: the readout emits d (director, 2026-11-09)

**Binds** [`FD-PRR-ADDENDUM-A2.md`](FD-PRR-ADDENDUM-A2.md) and its code, as merged in PR #980 at
**M_A2 = `cf76aec7cdff4e86f375ffe945f4d22f4799c4e0`**. The audited head is `ded09733`. The branch's later commit
`227b982d` merged main and changed only the index files; the addendum and every file under
`nd-unfolding/prior_retention/` are identical at `ded09733` and M_A2.

| file | sha256 (prefix) |
|---|---|
| `FD-PRR-ADDENDUM-A2.md` | `41e53237ceacb99e` |
| `nd-unfolding/prior_retention/prr_read.py` | `d7c7c2c0d6cbe4a1` |
| `nd-unfolding/prior_retention/test_prr.py` | `59e6fcf8d6a56c05` |
| `nd-unfolding/prior_retention/prr_mutation.py` | `a6f673cdc4ab8bcb` |

`prr_probe.py` (`f87ee90c58d2b890`), `prr_ibu.py` (`17acad82bad7c43f`) and `sbatch_prr.sh` (`10290087cdd57d97`) are
M_A1's bytes. No job script changes, so every FD-PRR job still runs from M_A1 (addendum A1, ruling 1) until addendum
A3 is bound.

**What led to it.** V-HALF (`DECISION-20261109-joseph-bias-half-rule.md`) needs each graded truth's departure from the
prior, d = (X − P)/P, on R00–R15. The director ruled option B for V-HALF's input: the bias from F0b's committed readout,
and d from FD-PRR's own computation, which the readout computed inside `rho()` but did not emit.

**What the director checked:**
- coverage-5b-audit's GO at `ded09733`, with no lows
  (https://github.com/josephbaileyy/MINERvA-OmniFold/pull/980#issuecomment-6744156227):
  - the diff is the d line, its key, the REQUIRED test and its mutant, with EXPECTED_TESTS 105;
  - d is (X − P)/P with P the prior at the entry's own split, and the denominator-swap mutant is killed by the named
    test;
  - the fixture comparison reproduces in the auditor's own clean worktrees at M_A1 and at the head: readout.txt is
    identical, and readout.json less its 181 d keys is byte-identical;
  - the leak guard refuses d emitted as x − p, p or x, and the readout stays a set of ratios;
  - 105 tests pass and 64 of 64 mutants are killed at the head.
- The director ran `test_prr.py` from a `git archive` of M_A2 (one thread, `PYTHONHASHSEED=0`, own TMPDIR): 105 passed.

**Rulings:**
1. **The PRR read runs from M_A2's `prr_read.py`.** Binding 1's rulings 1–8 and addendum A1's rulings stand otherwise.
   No reading, class, control, label or licence reads d.
2. **d is an input to V-HALF only,** declared and licensed separately under its own declaration and binding. Its
   CITABLE FOR here is the emitted value with FD-PRR §4.1's definition.
3. **Addendum A3 (#989)** merges main by union, and the union head is what is audited and bound. The PRR read then runs
   from the later of the two merge commits.

Nothing is submitted, deposited or tagged.
