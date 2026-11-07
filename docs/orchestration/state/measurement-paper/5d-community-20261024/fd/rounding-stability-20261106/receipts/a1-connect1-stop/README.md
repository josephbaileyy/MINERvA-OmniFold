# RS1 A1 connect 1: the stop receipt, and the deletion of the partial root (2026-11-07)

**Recorded by** the rounding-instability lane (`director-helper-3`). The connect ran under RS1-BINDING-2 addendum A1 at
M_A1 = `4fd5b9c2`, after the director's go on its sha256. **It stopped at staging with rc 6. Nothing was submitted or
staged, and the charge is 0 node-h.** RS1's total stays at 1.2400 of the 8.0 cap.

**CITABLE FOR:**
- the stop: its checks, its cause and its 0 charge;
- the deletion of the partial root: what was there, the literal paths, and the check that each path is gone.

**NOT CITABLE FOR:** any RS1 product or result.

## The connect (`logs/`, `launch-a1.out.txt`)

**The scripts:** `logs/rs1_a1_submit.sh`, sha256 `deab082b…` (the copy the connect wrote, byte-identical to the one
sent), and the launcher `rs1_a1_launch.sh`, `1a1db47a…`. The launcher's rc and ssh's rc were both 6, read unpiped.

**`logs/connect-a1.log.txt`** (login03, 2026-11-07T22:46:22Z–22:47:39Z). Every check before staging passed:
- **the fence:** no cov2d-* job;
- **iris:** 1,769.4 node-h remaining;
- **attempt 1:**
  - `log-dry/SHA256SUMS` was `e3cc597c…` and `log-full/SHA256SUMS` was `846e322a…`;
  - FAILED read `rc=124`;
  - sacct read `COMPLETED|944|1` and `FAILED|3520|1`;
- **the inputs** were stat'd;
- **the clones:** both were clean at e306087e and 4fd5b9c2, with 6/6 blobs, and the declaration, binding 1 and addendum
  at their digests;
- **the queue:** `252c9628…`, and dry `92195b6d…`.

**The stop** (`logs/stage.out.txt`). `python3 -I -B …/rs1_a1_plan.py stage` failed with
`SyntaxError: future feature annotations is not defined` at `rs1_a1_plan.py:20`. The login node's `/usr/bin/python3` is
3.6.15. The repair is #904, for the delta audit and a rebinding of A1.

## The partial root, deleted (`delete-partial.out.txt`, `rs1_a1_delete_partial.sh`)

**The ruling:** the director's item 4, with a go on the script's sha256 `df4a64ce…`. The run was on login09,
2026-11-07T22:49:33Z–22:50:15Z, with ssh rc 0.

**What was there.** `/pscratch/sd/j/josephrb/rs1-a1-20261107` held exactly `a1`, `deploy`, `dry.tsv`, `logs` and
`queue.tsv`: 41,678 files and 2,492,240,149 bytes, almost all of them the two clones.
- deploy: HEAD e306087e, 20,699 files, clean;
- a1: HEAD 4fd5b9c2, 20,968 files, clean;
- none of `runs/`, `log-dry/`, `plan.tsv`, `log-full/`, `copies.sha256`, `stage.json` or `runs-attempt1/`.

The script lists the sha256 of every file in `queue.tsv`, `dry.tsv` and `logs/`. Every file in `logs/` here matches its
listed digest (checked after copying), so the receipt preserves them.

**The deletion and the check:** literal paths only. All six paths (the five entries and the root) were reported gone.
Attempt 1's root `/pscratch/sd/j/josephrb/rs1-20261106` is still present. **DELETE: PASS.**

**The ledger:** `fd/LEDGER.tsv` has rows for the stopped connect and for the deletion.

**Renames:** git ignores `*.log` and `*.out`, so those files carry a `.txt` suffix here. Their contents are unchanged.
