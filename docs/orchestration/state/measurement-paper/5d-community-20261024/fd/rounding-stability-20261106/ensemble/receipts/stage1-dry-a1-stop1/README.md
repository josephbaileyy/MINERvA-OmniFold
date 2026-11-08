# ENS1 A1 stage-1 dry rerun, SUBMIT connect: the stop receipt (2026-11-08)

**Recorded by** the rounding-instability lane (`director-helper-3`). The connect was run under `ENS1-BINDING-2.md`
("addendum A1") at M_A1 = `f4d2d7f3833834390b7b031df61ba1a5765e9900`, after the director's go on its sha256.
- **It STOPPED at the fence, rc 9.** Nothing was read, cloned, copied or submitted, so the charge is **0 node-h**.
- Stage 1's spend stays at 0.1586 of its 55.0 cap.
- The fence did what it was written to do: it refused names that are neither `rs1_*` nor `ens1_*`, as the director's
  rule requires.

**CITABLE FOR:**
- the stop: what the fence saw, and the 0 charge;
- the partial root's contents, by listing and sha256;
- the records-only overlap check that the director ordered before any relaunch (below).

**NOT CITABLE FOR:** any ENS1 product, reading or gate. No task ran.

## The connect (`connect/`)

**The scripts:**
- `ens1_a1_dry_submit.sh`, sha256 `48805783…`. This is the copy the connect wrote to the root, byte-identical to the
  one the director was sent.
- The launcher `ens1_a1_dry_submit_launch.sh`, `4a7c5875…`.
- The launcher's rc and ssh's rc were both 9, read unpiped (`launch-submit.out.txt`).

**`connect-a1-dry.log.txt`** (login23, 2026-11-08T07:13:50Z–07:13:52Z):
- The fence's squeue (`squeue-before.txt`) held seven RUNNING jobs, named `fd1b_pfd_p3_j0` to `fd1b_pfd_p3_j6`: ids
  60991405, 60991413, 60991415 and 60991418–60991421. Each had a 2:30:00 limit and was about 11 minutes in.
- There was no `cov2d-*` row and no `ens1_*` row.
- The fence printed `FENCE STOP: a job of another name is present` and finished with rc 9. That was before iris, the
  stat, the clone or any read.

**Whose jobs they were** (the director, afterwards): limitation-resolver's 1B pre-check Part 1 bulk (P3). The director
had given its go at about 07:00Z and had not yet told this lane. **The ruling:** the fence stays as written, with no
`fd1b_*` allowance, so the SUBMIT sha stays `48805783`.

## The partial root

The connect creates its root before the fence, so that the fence's squeue has somewhere to be written.
`/pscratch/sd/j/josephrb/ens1-a1-20261108` therefore holds only this (`connect/root-listing.txt`, a read-only `find`
after the stop):

| path | bytes | sha256 |
|---|---|---|
| `logs/connect-a1-dry.log` | 967 | `c424f08a5e784ee41f7430c3f08593fd49c0e485629af627e457330bd5a80969` |
| `logs/connect-a1-dry.done` | 2 | `2e6d31a5983a91251bfae5aefa1c0a19d8ba3cf601d0e8a706b4cfa9661a6b8a` |
| `logs/squeue-before.txt` | 322 | `9f91b0090d3b19e32049e6993525dc2f8dabf70abfa08fc65f33de8ede687fb3` |
| `logs/ens1_a1_dry_submit.sh` | 21,384 | `488057837438b79c745f53c3256107463fed04130f39c0f6d976bf2dd9faa20e` |
| `refs/runs/control/stability/` | (empty directories) | — |

All four files are copied here, and each matches its digest. The connect refuses a root that already exists, so the
relaunch needs this root deleted.

**The cleanup** (`cleanup/ens1_a1_delete_partial.sh`, sha256 `8f368b52…`):
- It runs only after this receipt merges, and on the director's go on its sha256.
- It refuses unless the root holds exactly the ten entries above, with the four files at these digests.
- It also refuses if any `ens1_*` job is queued.
- It prints the listing before and after, and deletes by literal path only.
- It checks each of the ten paths is gone, and that attempt 1's root `/pscratch/sd/j/josephrb/ens1-20261107` is still
  present.

Its output and its `fd/LEDGER.tsv` row will be added to this receipt.

**Tested locally** on a copy of the tree, with shims for `find -printf` and `squeue`:
- a clean tree gives DELETE: PASS;
- a queued `ens1_*` job, an extra file, and a changed byte in one log each give REFUSE, with nothing deleted.

## The overlap check (`overlap/overlap.json`; records only, local, 0 node-h)

**The director's question:** do ENS1's inputs overlap Part 1's 355 staging sources? If they do, a plain read by an ENS1
task could move a source's atime and stop Part 1's P4 re-stat.

**Part 1's sources:** the 355 lines of `fd/receipts-1b/precheck-fd/p1/stat-before.txt` on main (sha256 `a14aeddf…`, the
P1 receipt's own digest). These are the sources recorded when `staged.json` (`f2f06419`) was written. `staged.json`
itself is not committed.

**ENS1's inputs:**
- the npz (`07fccc1a`) and the bkg (`2addac8f`);
- FD-STAB's j1–j20;
- attempt 1's F₆₄.

The stat of the first 22 is from attempt 1's connect log (#908). F₆₄ has no recorded stat.

**The result:**
- **Literal paths:** 0 in common.
- **Directories:** 0 in common.
- **Size and mtime:** 0 pairs in common.
- **Size alone:** 0 pairs in common.
  - Every one of the 22 stat lines is a regular file (the stat sizes are file sizes, not link lengths).
  - A file reached through a symlink or a hard link would carry its target's size, so a shared real file would show up
    here.
- **The roots:**
  - Part 1 reads `fd-1b-20261030`, `s1-20261024`, and two single files under `MINERvA-OmniFold/` (`2d-unfolding/` and
    `MINERvA101/`).
  - ENS1 reads `MINERvA-OmniFold/nd-unfolding/`, `s5c-20260924`, `fd-stab-a1r-20261104` and `ens1-20261107`.
- **F₆₄** is disjoint from Part 1's sources by literal path and by directory.

**Verdict: DISJOINT** on the records. The director's rule for this case is to relaunch once no `fd1b_*` job is in
squeue.

**The check's limit:** real paths were not resolved on the cluster, since the director asked for a records-only check.
The size test stands in for that: a shared real file implies an equal size, and no sizes are equal.

## The relaunch

The relaunch uses the same SUBMIT sha `48805783…`, unchanged, once all three of these hold:
- this receipt has merged;
- the cleanup has passed;
- the queue holds no `fd1b_*` job.

The POST-RUN connect stays `90af5e54…`. On the director's ruling 3 (A1 §7), the post-run opens only attempt 1's F₆₄
product, and only through a digest-verified noatime copy. Attempt 1's other four products stay unopened.

**The ledger:** `fd/LEDGER.tsv` has one row for this stop.

**Renames:** git ignores `*.log` and `*.out`, so those files carry a `.txt` suffix here. Their contents are unchanged.
