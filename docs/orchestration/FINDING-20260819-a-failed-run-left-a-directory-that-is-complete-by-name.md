# A failed run left a checkpoint directory that is COMPLETE BY NAME, and both guards look elsewhere

*Lane E, 2026-08-19. `BEN-477`. Campaign `EP-2026-08-17-data-only-cstat`.*

## The measurement

`57256638_0` FAILED at the receipt write after 02:58:44 (see [`BEN-476`](FINDING-20260819-a-guard-forbade-what-a-pinned-producer-must-produce.md)).
Taken from the cluster in the same turn as this finding:

```
=== the FOUR paths the train-stage collision guard requires ABSENT:
  absent   training/GATE5_REPLICA_WEIGHTS.npz
  absent   training/GATE5_REPLICA_WEIGHTS.npz.done
  absent   training/GATE5_REPLICA_TRAINING_RECEIPT.json
  absent   training/GATE5_REPLICA_TRAINING_RECEIPT.json.done
=== EVERYTHING ELSE under training/:
  14 files, 7,903,936 bytes under w_nominal/
```

And `expected_checkpoints()` expects **exactly those 14 names** — verified by running it:

```
14 expected
  OmniFold_fe_nominal_nominal_iter0_step1.pkl        ... iter0_step2, iter1_step1, iter1_step2 ...
  OmniFold_fe_nominal_nominal_iter2_step1_final.weights.h5
  OmniFold_fe_nominal_nominal_iter2_step2_final.weights.h5
```

> **A RUN THAT FAILED LEFT BEHIND A CHECKPOINT DIRECTORY THAT THE COMPLETENESS TEST CALLS COMPLETE**, while
> every one of the four DECLARED products is absent. Artifact-present, declaration-absent — the shape lane C's
> invariant is about — except the artifact in question is the one nobody enumerated.

## Both guards look elsewhere, and neither is broken

**The collision guard enumerates four paths.** `submit_gate5_data_only_n50.sh` asserts the four training
products absent; `w_nominal/` is not among them. It did its job exactly as written.

**The read-back checks the finals by path and existence.** `cstat_data_only_readback.py:369-377`:

```python
got = os.path.realpath(str(contract.get(key, "")))
if got != os.path.realpath(str(path)): raise SystemExit(...)
if not (path.is_file() and not path.is_symlink()): raise SystemExit(...)
```

Path identity, `is_file`, not-a-symlink. **No digest, no size, no run id, no mtime.** Then a set equality on
the directory listing, which is a check on **filenames**.

> **NOTHING IN THE ARTIFACT BINDS A CHECKPOINT TO THE RUN THAT WROTE IT.** So the question *"are these this
> run's weights?"* has no answer in the data — only in the mtimes, which nothing reads.

## Why the finals are the worst case rather than an edge case

The finals are written **last**. That makes them, simultaneously:

- the files **most likely to be stale**, because any failure between the first checkpoint and the end leaves a
  previous attempt's finals in place while the earlier iterations get overwritten; and
- the files **validated most weakly**, since they are the two the read-back checks by path-and-existence.

A later run that died before writing `iter2_step*_final.weights.h5` would present a directory with 14 correct
names, fresh non-finals from itself, and **finals from a different run** — and every check would pass.

## A LIVE HAZARD HELD OFF BY ONE DEFAULT ARGUMENT (not "checked, not live" — that reads as closed)

Cross-run contamination through `omnifold.py`'s `LoadStart` is **not reachable today, and nothing about the code prevents it** — it is held off by a default argument that nobody has had a reason to change yet. Stating it as *"checked, not live"* would be true and would get it read as closed. `LoadStart` does
`temp1.load_weights(model1_name)  #better starting point for model 1` — is **not reachable here**:

| link | evidence |
|---|---|
| `LoadStart` is gated | `omnifold.py:165` — `if self.start>0:` |
| the default is 0 | `omnifold.py:59` — `start = 0,` |
| our driver never sets it | `grep 'start' train_fullevent_replica.py` finds only `started`/`started_utc` |
| the names differ | it reads `iter{N}_step1.weights.h5`, **no `_final`** |

**But all six of those non-final names exist on disk right now.** So the hazard is dormant by *one default
argument*, not by construction — and a resume feature is exactly the kind of thing a future session adds
without knowing that a stale directory is waiting for it.

## Repair, and what it does not cover

The train stage now refuses if **any file or symlink** exists under a member's `w_nominal/`. An empty
directory is allowed, because the trainer creates it (`omnifold.py:142`) and an empty one carries no
attribution. Power-tested four ways — clean tree, one leftover file, empty directory, and a `ln -s` bypass
attempt — against a **committed** tree, because the controller refuses to run on a dirty worktree.

**That closes re-runs through the controller and nothing else.** The durable fix is to record the 14
checkpoint digests in the receipt and re-verify them at read-back, so completeness becomes a claim about
**content**; it changes the artifact schema, so it is proposed rather than done (`OI-133`).

## Where the evidence lives

The 14 files were **QUARANTINED, NOT DELETED** — moved on 2026-08-19 to

    /pscratch/sd/j/josephrb/gate5-do-g2-evidence/BEN-477-57256638_0/

with a `README.txt` beside it. **14 files and 7,903,936 bytes verified on both sides of the move**, and the
member's `training/` verified empty afterwards. They are this finding's only physical evidence: a checkpoint set
that is complete by name and was produced by a failed run.

**NOT inside `training/`, and the proposed path there was withdrawn for a measured reason:** the read-back
asserts an EXACT SET over `train_dir.iterdir()` (`cstat_data_only_readback.py:388-390`), and `iterdir()` returns
**directories**, so a quarantine sibling named `w_nominal.FAILED-…` would become `unexpected` and fail the next
run's read-back. That check is correct and was not weakened to make room for evidence — the evidence moved
instead, to outside the DATA ROOT, where no data-root walk reaches it.

**AND NOW COPIED OFF SCRATCH, 2026-08-19** — `/pscratch` is purgeable, and this is the finding's only
physical evidence:

    /global/homes/j/josephrb/evidence/BEN-477-57256638_0/

A COPY, not a second move: the scratch original was re-counted afterwards and still holds 14 files. Verified
three ways — 14 files and 7,903,936 bytes on both sides, and **all 14 sha256 digests identical**, because equal
totals are not equal contents. `cp -a`, preserving mtimes, since mtime is the only run-identity signal these
files carry (see `OI-133`). Home was at 22.50 of 40.00 GiB (56.2%) before the write.

**A vacuous guard in my own copy script, recorded because it is the day's pattern and not because it changed the
outcome:** I gated the copy on `df -Pk /global/homes/...`, which reported **22.8 TiB available** — the raw GPFS
filesystem, *not* the 40 GiB quota that actually binds. **The refusal could not have fired**, and would have
passed a home directory at 100% of quota. The decision was still correct, taken from the `myquota` output
printed beside it — but the CHECK measured the wrong quantity, which is `BEN-473`'s shape (the convenient number
rather than the governing one) inside a script guarding against exactly that.

**A byte figure I published at the wrong scope, corrected here:** I first reported `7,908,032 bytes` for
`w_nominal/`. That was `du -sb` on **`training/`**, its parent, which at the time contained only `w_nominal`.
The directory's own total is **7,903,936**. The claim was true of a different object than the one it named —
which is the same defect shape as everything else in this pair, one level down and with no consequence beyond
the number.

## Check to steal

**For every completeness test, ask whether a PREVIOUS ATTEMPT could satisfy it.** A set-equality on filenames
answers *"are the right names here?"*, never *"did this run put them here?"* — and the second question is the
one a re-run needs answered.
