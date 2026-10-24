# REPORT: 5D design Stage 0, Part P — inputs preserved on HPSS (2026-10-23)

**By** the measurement session, under [`STAGE0-BINDING-P.md`](STAGE0-BINDING-P.md), which binds Part P of
[`STAGE0-DECLARATION.md`](STAGE0-DECLARATION.md).
- Run on login12, 2026-10-23 21:32:34–21:33:57 UTC; 0 node-h; no Slurm job.
- Receipts are in [`stage0/receipts-P/`](stage0/receipts-P/): `preserve.log`, the tar's sha256 and `SHA256SUMS`.

**CITABLE FOR:** the HPSS copy of the 425 Stage 0 and 0c inputs, and its verification.
**NOT CITABLE FOR:** any Stage 0 result.

## Result: PASS

**What ran.** The committed `stage0/stage0_preserve.sh` (sha256 `27ccc04a…`) and `stage0/INVENTORY.sha256`
(`267c6c7c…`), as merged in PR #286. Both were copied to `/pscratch/sd/j/josephrb/5d-stage0-20261023/tools/`, and their
sha256 equal main's.

| step | outcome (`preserve.log`) |
|---|---|
| 1. re-verify the 425 input hashes | "inventory verified: 425 files" (21:32:53) |
| 2. one uncompressed tar | sha256 `5bd51c146f59356335b5213818ace82dc6d393b4e07a24ced10369a5e5d85f26`, 3,303,587,840 bytes, 425 members. tar printed "Removing leading `/` from member names" and "… from hard link targets" |
| 3. HPSS copy | `hsi put` to `/home/j/josephrb/mnv-5d-stage0-inputs-20261023/stage0-inputs.tar`. `hsi hashcreate` gave md5 `cb72a4b1fb32d75895bc26e0b07b7322`, and `hsi hashverify` gave "(md5) OK". The tar's sha256 file and the inventory were copied beside it |
| 4. retrieval check | `hsi get` back to pscratch: the retrieved sha256 equals the tar's. "PASS: HPSS copy verified by hashverify and by retrieval" (21:33:57) |

**HPSS listing after the run** (`hsi ls -l`, 21:35 UTC): `INVENTORY.sha256` 61,796 B; `stage0-inputs.tar`
3,303,587,840 B; `stage0-inputs.tar.sha256` 127 B.

**Cleanup, as bound.** The retrieved copy was deleted by the script. The temporary tar on pscratch was deleted after the
PASS (21:35 UTC). The inputs themselves are unchanged, and nothing was written to CFS.

**Quota.** `hpssquota` at 21:35 UTC still read 350.90 of 512.00 GiB (68.5%), the same as before the copy. HPSS
accounting may lag a new 3.3 GB file; no record says how long. pscratch is at 16.97 of 20.00 TiB (84.8%).

**What this changes.** Stage 0's inputs no longer depend on surviving the pscratch purge. If any is purged, it can be
restored from the tar and checked against `INVENTORY.sha256`. One input of Stage 0c is not in this tar: the vertical
bank's `cv.npz` (2.16 GB, `072643e1…`). It is named in the Part A declaration.

## Addendum: what the receipts do and do not show (after independent review, 2026-10-23)

**Unreceipted claims:**
- **"425 members"** is implied, not logged. The script's member-count check prints nothing on success and exits 4 on a
  mismatch. It reached PASS.
- **The retrieved copy's sha256** is not printed separately. The script compares it with the tar's and exits 8 on a
  difference. It reached PASS.
- **The 21:35 UTC readings** (`hsi ls -l`, `hpssquota` and the pscratch cleanup) come from the session's terminal
  output. They are transcribed in [`stage0/receipts-P/post-run.txt`](stage0/receipts-P/post-run.txt); they are not a
  captured log.

**Hard links.** tar's "Removing leading `/` from hard link targets" means at least one member is stored as a hard
link. The inventory has 3 groups of files with identical sha256. Restoring such a member alone also needs its link
target, so restore the whole tar or the named pair.
