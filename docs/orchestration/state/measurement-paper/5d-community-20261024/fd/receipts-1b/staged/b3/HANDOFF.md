# 1B staged, binding 3: final handoff (stage 1 ended, 2026-11-06)

**What this is.** 1B is the declared 5D coverage test of the measurement's full-dimensional unfolding (`fd_1b_mc.py`
and its helpers in `nd-unfolding/`). Binding 3 ran it under staged amendment 2 and addendum A2.1, on the no-plug-in path
(G18 and AR23). Its stage 3 receipt STOPped on §2b, and stage 1 ended under amendment 2 §8 and decision item 2 (iii):
see `docs/orchestration/OUTCOME-20261106-1b-stage1-receipt-stop.md` on main (#832). That record is the authority for
the verdict and what it licenses. This file covers only where things are left. Nothing is running or queued (squeue,
2026-11-06T15:15Z).

## The branch

`decl/1b-staged-a2-1-20261103`. The campaign's last content commit is `206bfd508ea6a7b9d8737413a3da144c6edd50fa`; this
handoff is the one commit on top of it. Measured against main `96231c60` on 2026-11-06: merge-base `7bdd39f6` (#727),
92 commits and 217 files on the branch only, nothing of it merged. No PR is open from this branch. The amendment 2
branch it grew from (`decl/1b-staged-amend2-20261102`) is PR #717, still OPEN. There is no tag.

**On the branch, not on main:**
- **Declarations:** `FD-1B-STAGED-REDESIGN-PROPOSAL.md`, `FD-1B-STAGED-AMENDMENT-2.md` and `FD-1B-STAGED-ADDENDUM-A2-1.md`
  (§11 is binding 3), all under `state/measurement-paper/5d-community-20261024/`, plus their CATALOG and MANIFEST rows.
- **Code:** `fd_1b_binning.py`, `fd_1b_c2.py`, `fd_1b_cal300_pins.json`, `fd_1b_cvdenom.py` and
  `fd_1b_noatime_guard.py` are new; `fd_1b_mc.py` is modified. There are 8 test files, `test_fd_1b*.py` (6 new,
  2 modified), plus 2 data fixtures. `stage1/tables/make_stage1_tables.py` is modified.
- **Records,** under `fd/receipts-1b/staged/`:
  - `a2-1/` holds the calibrations, the timing probes, the CV denominator reads, the binning runs, the mutation
    receipts and their connect scripts;
  - `b3/` holds the per-stage runs below, the connects, `guard_scan.py` and the guard's mutation receipts;
  - `mutation_a21.py` and `mutation_mc_a2.{py,out}` are the mutation harnesses.

**Main's OUTCOME cites `b3f27fab` and `206bfd50` on this branch,** so the branch is the only home of the evidence it
rests on. Do not delete or rewrite the branch without first pushing an evidence tag (follow-up 1).

## Binding 3's runs

| stage | job | result | node-h | record (under `b3/`) |
|---|---|---|---:|---|
| 1 | c2check G18, 60880987 | PASS | 4.879 | `c2check-g18-run/` |
| 1 | c2check AR23, 60880988 | PASS | 4.974 | `c2check-ar23-run/` |
| 2 | c2check-merge (login) | PASS, option (1) at both | 0 | `merge-run/` |
| 3 | receipt, 60889950 | INVALID: its 480G step exceeded the 487802M allocation and never started | 1.681 | `receipt-run-60889950/` |
| 3 | receipt v2, 60893641 (M4 `5771ce20`) | STOP, §2b: 892 of 900 draws have a non-positive denominator cell; N1 clean | 1.312 | `receipt-run-60893641/`, with `breakdown.{py,out}` |
| 4–7 | S1-0, S1-0b, clipcheck, the smoke run, the bulk, the readout | not run | 0 | none |

**The final spend** (sacct ElapsedRaw × 1 node, re-measured 2026-11-06) is **16.329 node-h**:
- 3.484 before binding 3: jobs 60771025, 60783756, 60805733, 60857361, 60859504 and 60870880 (A2.1 §11's price table);
- 12.845 in binding 3: the four jobs above.

55.671 node-h remains of the 72.0 ceiling.

## pscratch

Under `P=/pscratch/sd/j/josephrb`, measured read-only from login32 at 2026-11-06T15:15Z. Only campaign outputs were
read, with stat, du, find and git, and sha256 for the files outside `deploy/`. No declared root was listed or opened.

Every directory below has the same shape:
- a `deploy/` clone of about 1.15 GiB. Each is clean (`git status --porcelain --ignored` is empty apart from
  `__pycache__`), and its HEAD is a commit on the branch;
- a few small outputs beside it.

Every output file outside `deploy/` matches a committed file byte for byte, except the 9 env logs marked "not
committed".

| path | job | deploy HEAD | outside `deploy/` |
|---|---|---|---|
| `fd-1b-a21-cvdenom-20261103` | login | `435d8957` | 5 files, all committed |
| `fd-1b-a21-cvdenom2-20261103` | login | not listed | **a declared root** (`ROOTS` in `fd_1b_noatime_guard.py`); keep |
| `fd-1b-a21-binning-20261103` | login | `e7641a9b` | 5 files; `env.log` not committed |
| `fd-1b-a21-binning2-20261103` | login | `663a7609` | 5 files; `env.log` not committed |
| `fd-1b-a21-binning3-20261103` | login | `917907aa` | 6 files; `env.log` not committed |
| `fd-1b-a21-calib-20261104` | 60771025 | `02e71a0b` | 8 files, 4.7 MiB with `calibration.npz`; `logs/env-job.log` not committed |
| `fd-1b-a21-calibN-20261104` | 60783756 | `51d67b54` | 8 files; `logs/env-job.log` not committed |
| `fd-1b-a21-calibN-rerun-20261104` | 60805733 | `8a9b8db9` | 8 files; `logs/env-job.log` not committed |
| `fd-1b-a21-calibN-rerun2-20261105` | 60857361 | `bf36901f` | 8 files; `logs/env-job.log` not committed |
| `fd-1b-a21-c2probe-20261105`, plus `.atime-{pre,post}.tsv` beside it | 60859504 | `bf36901f` | 7 files; `logs/env-job.log` not committed |
| `fd-1b-a21-c2probe-1t-20261105`, plus `.atime-{pre,post}.tsv` | 60870880 | `a47cfb4b` | 7 files; `logs/env-job.log` not committed |
| `fd-1b-b3-c2check-g18` | 60880987 | `a47cfb4b` | 9 files, all committed |
| `fd-1b-b3-c2check-ar23` | 60880988 | `a47cfb4b` | 9 files, all committed |
| `fd-1b-b3-merge`, plus `.atime-{pre,post}.tsv` | login | `a47cfb4b` | 6 files, all committed |
| `fd-1b-b3-receipt-60889950-evidence` | 60889950 | none | `pre-cancel.txt`, committed |
| `fd-1b-staged-20261102/stage1/a2` | 60893641 | `5771ce20` | 24 files, 9.3 MiB with `receipt.json`; all committed |
| `fd-1b-staged-20261102/stage1/a2-invalid-60889950` | 60889950 | `8dd16e04` | 21 files, all committed |

Only `stage1/a2` and `stage1/a2-invalid-60889950` belong to this campaign inside `fd-1b-staged-20261102/`. Its
`stage1/in` is a declared root.

**Not this campaign's, so not listed:** earlier 1B lanes' `fd-1b-20261030`, `fd-1b-inv-20261101` and the rest of
`fd-1b-staged-20261102`, plus the shared inputs (`MINERvA-OmniFold/`, `s5p-20260926/`, `s5c-20260924/`). Each holds
declared roots.

**Deletion: nothing needs deleting now, and no ledger row authorizes any deletion.** I found no pscratch deletion ledger
on main, and nothing was deleted. pscratch is purgeable, so what these directories hold is preserved by the commits,
not by the directories. If space is wanted, a ledger row could release:
- the 15 `deploy/` clones, about 17.1 GiB in all. Each is clean, and a clone of its HEAD reproduces it;
- the output files, once the 9 env logs are committed or explicitly released.

The row should not release these while (iii) could still be overridden:
- `fd-1b-a21-cvdenom2-20261103`, a declared root;
- `stage1/a2` and `stage1/a2-invalid-60889950`: the generator fixes the receipt's path at `stage1/a2`, and v2's move
  rule depends on both.

## Open follow-up items

1. **Preserve the evidence before any branch cleanup.** The branch holds every record main's OUTCOME cites. A pushed
   evidence tag at the branch head (or a merge, if Joseph wants the declarations on main) needs the director's call.
2. **The 9 uncommitted env logs** (table above), about 0.4 KB each. Commit them or release them before any pscratch
   deletion.
3. **The auditor's held lows**, none blocking. Each fails closed:
   - in `connect-receipt.sh` v2, the guarded move runs before the queue, balance and clone checks, so a later STOP
     leaves a re-run refusing "both exist" until someone steps in by hand;
   - the stat-after window spans the whole job, so another lane's read under `ROOTS` in that window would show up as a
     1B deviation;
   - each 1B entry point's `main` could refuse to run unless the guard is installed. Today `guard_scan.py` covers only
     the scripts in `b3/`, not a hand-typed launch.
4. **The record's limit, which the breakdown states.** `denominator_check` (`fd_1b_mc.py:388` at `206bfd50`) keeps
   `sorted(bad)`, `max(bad.values())` and `n1` only. So the flagged cells' identities, the per-draw distribution below
   the maximum, and whether the cells are the sparse low-d_CV ones of amendment 2 §5 are not in the record. Under
   (iii) this stays unrepaired. The disclosed read of the flux constraint before the breakdown request was narrowed
   is recorded in the OUTCOME. Nothing derived from it was kept.
5. **Moot unless (iii) is overridden:** whether the plug-in truth belongs in 1B (`FD-1B-STAGED-BINDING-3.md:52` at
   `3d976a76`).

## If Joseph overrides rule (iii)

A fresh session needs all of the following, in order. None of it exists now.
1. **Joseph's written ruling, and a new post-hoc declaration he authorizes.** The OUTCOME explains why the director
   does not recommend it: any change of form, universes, cells or exclusions would be chosen after seeing the STOP.
   The declaration must say what changes in the composition or the §2b rule, and must be committed before any code.
2. **Code at a new M on a branch from `206bfd50`** (never a merge with main; A2.1 §11). If the receipt is to say
   which cells fail, `denominator_check` must record the cell identities. Any change to the five gate files changes
   the gate pin, and c2check's records then no longer satisfy their identity rules. Check §11's PASS-identity rules
   before reusing them.
3. **A connect v3.** `connect-receipt.sh` v2 refuses now, because `stage1/a2` holds `receipt.json`. A new rule for
   moving the STOP receipt aside (or a new receipt path) needs the director's ruling. Carry over v2's pre-submission
   fit check, which sums every concurrent step's CPUs and memory against `sinfo`'s CPUs and the partition's
   MaxMemPerNode (487802M). Carry over the post-submission TimeLimit, Partition and ReqTRES checks with scancel too.
4. **A price.** At caps the rest of the sequence is 53.5 node-h (`CAP_NODE_H` in `connect-receipt.sh`): a receipt
   2.0, S1-0 and S1-0b 2.0, the smoke run 1.5, the bulk 48.0. With 16.329 spent, that totals 69.829, within the 72.0
   ceiling. A redesign is repriced from
   its own timings.
5. **The auditor's read and the director's binding** before each first run. Stages 4–7's scripts are undeclared blobs,
   not yet written (A2.1 §11, "Scripts not yet written").
6. **The standing rules:**
   - every 1B read of a declared input goes through `fd_1b_noatime_guard.py`, and every job line passes
     `b3/guard_scan.py`;
   - jobs are under 12 h, CPU only, QOS regular, with nothing written to CFS;
   - each stage gets a fresh W;
   - connect scripts are sha-compared and launched in one ssh.
