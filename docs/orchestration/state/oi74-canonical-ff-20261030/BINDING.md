# Binding: OI-74, the canonical cluster checkout's fast-forward to main (2026-10-30)

**By** the paper-tighten lane, as director.

**Under** `DECISION-20261030-joseph-canonical-checkout-and-table-check.md` (#544), item 1.

**Binds** [`DECLARATION.md`](DECLARATION.md), merged in PR #547. Its file sha256 begins `f94a146316f8c333`. The script
it declares is [`ff.sh`](ff.sh), with sha256 `afe92465b1a7178f06a122365b1a282d9b7daf5ebcf94950a2ea67751360ce52`, the same
on `main` after the merge (`e9daec3b`).

**AUTHORIZES:** exactly one run of `ff.sh` against `/pscratch/sd/j/josephrb/MINERvA-OmniFold`, by one ssh to
`saul.nersc.gov`, as the declaration's §6 gives it, with its transcript captured to `run/session.txt`.

**CANNOT AUTHORIZE:**
- a second run;
- any repair after a STOP;
- any write to the tree beyond the script's W1–W4 steps;
- touching untracked files;
- launching a job;
- any write to CFS.

## 1. What the director checked at the PR head `446b1c2f`

- `ff.sh`'s digest equals the declaration's.
- `test_ff.sh` against a scratch github remote and checkout: **11 passed, 0 failed**. The cases are:
  - the good path;
  - an identical ignored file proceeding;
  - five STOPs before any write: a job present, a HEAD mismatch, an extra tracked change, an existing aside directory,
    and a failed squeue;
  - four STOPs that roll back: a differing ignored file at an added path, an untracked file at an added path, a failed
    fetch, and a job appearing before the merge.
- The script's order:
  1. read-only preconditions: squeue --me must be empty; HEAD must be `32e403b84` on branch main; no merge or index lock;
     the tracked porcelain exactly the two live-state files; the aside directory absent;
  2. **W1**, the files copied aside with sha256 and verified;
  3. **W2**, both restored to HEAD;
  4. **W3**, `fetch github`;
  5. an ancestry check, then **P5**, which guards ignored and untracked paths that the merge adds;
  6. a second squeue check;
  7. **W4**, `merge --ff-only --no-stat`;
  8. the post-check.
  Every git call runs without hooks, auto-gc or maintenance, and with `GIT_OPTIONAL_LOCKS=0`.

## 2. Rulings on the declaration's additions

1. **Any job under `squeue --me` is a STOP,** including scrontab entries. The 214 launchers hard-code the path, so no
   job's directory can be trusted. If the STOP fires because of a standing scron job, the session reports it unrepaired,
   and the director decides.
2. **P5's overwrite guard is accepted.** A silent replacement of an ignored file is the hazard it measured on a scratch
   repo.
3. **The rollback on any STOP after W2 is accepted.** A failed post-check (exit 30) is not undone, and is reported as it
   stands.
4. **The KI 89 correction** is accepted: the import that hard-codes the tree is the 2D driver's, and the blob it loads
   is unchanged.

## 3. The report

`REPORT.md` beside the declaration gives:
- the transcript;
- HEAD before and after, and the fetched main;
- the tracked count, which must be 0, and the untracked count before and after;
- the aside directory and its SHA256SUMS;
- the A/M/D counts and what now loads new code.

It goes to the director as a PR, with OI-74's row updated.

The run may start once this record is on `main`. Tell the director before connecting.
