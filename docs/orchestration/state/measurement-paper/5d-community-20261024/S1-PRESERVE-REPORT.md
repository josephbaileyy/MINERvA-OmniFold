# REPORT: S1 HPSS copy of the 5D universe weight bank and the detector dump (2026-10-25)

**By** the measurement session, under [`S1-BINDING.md`](S1-BINDING.md) §3, with its erratum (PR #342), and Joseph's
approval in `DECISION-20261024-joseph-approve-integration-wording-s1-compute-preserve.md`, item 3.
- Run on login12, 2026-10-25 00:36:21–01:07:34 UTC; 0 node-h; no Slurm job.
- Receipts are in [`s1/receipts-P/`](s1/receipts-P/): `preserve.log`, the tar's sha256, `quota-before.txt`,
  `launch.txt`, `post-run.txt`, and `SHA256SUMS`.

**CITABLE FOR:** the HPSS copy of the 734 inventoried bank and detector-dump files, and its verification.
**NOT CITABLE FOR:** any S1 result.

## Result: PASS

**What ran.**
- **The script:** the committed Stage 0 preserve script, unchanged, run from the deploy clone
  `$B/deploy/d5617470` (`B=/pscratch/sd/j/josephrb/s1-20261024`). That is
  `state/measurement-paper/5d-design-20261023/stage0/stage0_preserve.sh`, sha256
  `27ccc04a8c14d640efe1657b3d04b657f61a682db381c105daee82f901ea5d68`, measured in the deploy.
- **The inventory:** `$B/preserve-inv/PRESERVE-INVENTORY.sha256`, sha256
  `cde96ca78f732c0aa42bcde5b437fbd8ff331568668623a02bedd23695e4861f`, 734 lines:
  - 701 lines under `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware`;
  - 33 lines under `/pscratch/sd/j/josephrb/s5p-20260926/bank_detector`.
- **Why the inventory is not read from the deploy:** the file is not in the deploy pin `d5617470`. It came in with
  PR #341 (`c0889e53`). It was written from the clone's own objects with `git show c0889e53:<path>`, so the deploy
  tree was untouched. This is the repair named in the S1-BINDING §3 erratum (PR #342), which the director accepted.
- **Arguments:** work dir `$B/preserve`; HPSS dir `/home/j/josephrb/mnv-5d-s1-inputs-20261024`.
- **How it was started:** `setsid nohup … &` on login12, pid 2207025 (`launch.txt`).

**Preconditions (§3 condition 1),** read at 00:36:14 UTC (`quota-before.txt`):
- `hpssquota` read 353.98 of 512.00 GiB used, so 158.02 GiB was free. The floor is 80 GiB.
- pscratch read 16.99 of 20.00 TiB, so about 3 TiB was free. The tar and its retrieved copy need about 150 GB.
- `hsi ls -d` of the HPSS directory returned `HPSS_ENOENT`, so the directory was new.

**Overlap with S1 (§3 condition 3).** The copy ran beside the S1 pilot (job 60232432, 00:47:54–00:59:56 UTC). S1's
production jobs were submitted at 01:01:57 UTC and pended through the end of the copy. All S1 jobs only read the
inventoried files.

| step | outcome (`preserve.log`) |
|---|---|
| 1. re-verify the 734 input hashes | "inventory verified: 734 files" (00:41:56) |
| 2. one uncompressed tar | sha256 `cc8353f7008e7ea77810942ee2e86c2116f22cc0c6c422abca353085ebd435a6`, 73,709,649,920 bytes (00:54:07). tar printed "Removing leading `/` from member names" and "… from hard link targets" |
| 3. HPSS copy | `hsi put` to `…/mnv-5d-s1-inputs-20261024/stage0-inputs.tar` at 1,875,661.8 KBS. `hsi hashcreate` gave md5 `5540cc327482bdfa7d10ffefd02170ce`; `hsi hashverify` gave "(md5) OK". The tar's sha256 file and the inventory were copied beside it |
| 4. retrieval check | `hsi get` back to `$B/preserve/retrieve/`; the retrieved sha256 equals the tar's. "PASS: HPSS copy verified by hashverify and by retrieval" (01:07:34) |

**HPSS listing** (`hsi ls -l`, in `preserve.log` and again in `post-run.txt` at 01:09:09 UTC):

| file | bytes |
|---|---|
| `INVENTORY.sha256` | 116,791 |
| `stage0-inputs.tar` | 73,709,649,920 |
| `stage0-inputs.tar.sha256` | 129 |

`hsi hashlist` lists md5 `5540cc32…` for the tar.

**Name mismatch (§3 condition 4).**
- The script names its tar `stage0-inputs.tar`, and it stores the inventory on HPSS as `INVENTORY.sha256`. Neither
  name was changed.
- This copy is the S1 bank and detector-dump copy, not Stage 0's. The HPSS directory name,
  `mnv-5d-s1-inputs-20261024`, is what identifies it.
- The inventory stored there is `PRESERVE-INVENTORY.sha256`, 116,791 B; its sha256 is `cde96ca7…`.

**Cleanup, as bound (§3 condition 6).**
- The script deleted the retrieved copy itself, and the empty `retrieve/` directory was then removed.
- The temporary tar `$B/preserve/stage0-inputs.tar` was deleted after the PASS, at 01:09:18 UTC (`post-run.txt`).
- Kept: `stage0-inputs.tar.sha256`, `paths.list` (68,347 B, sha256 `0dc13d9a…`) and `preserve.log`.
- The inventoried files were not touched, and nothing was written to CFS.

**Quota after the copy** (`post-run.txt`, 01:09:09 UTC):
- `hpssquota` still read 353.98 of 512.00 GiB, the same as before. Stage 0 saw the same lag after its copy
  (`STAGE0-PRESERVE-REPORT.md`).
- Once accounting catches up, the 68.65 GiB tar should leave about 89.4 GiB free **(arithmetic)**.
- pscratch read 17.05 of 20.00 TiB.

**What this changes.** The bank and the detector dump no longer depend on surviving the pscratch purge, to which
they were exposed from about 2026-12-14 (`S1-PLAN.md:95-96`). If any file is purged, it can be restored from the tar and
checked against the stored inventory.

## What the receipts do and do not show

- **The member count** is now logged. `post-run.txt` records `tar -tf | wc -l` = 734, against 734 inventory lines.
  It was read from the pscratch tar before deletion. (The script's own count check prints nothing on success.)
- **The retrieved copy's sha256** is not printed separately. The script compares it with the tar's and exits 8 on a
  difference. It reached PASS.
- **The exit code** of the detached script was not captured; nohup's output is the log. The log ends in PASS. Each
  checked step (verify, tar, member count, put, hashcreate, hashverify, get, compare) prints "STOP" and exits 3–8 on
  failure, so reaching the PASS line means all of them passed. The script does not check two commands, `hsi mkdir -p`
  (`|| true`) and `hsi ls -l`.
- **Hard links.** tar's "from hard link targets" means at least one member is stored as a hard link, as at
  Stage 0. Restoring such a member alone also needs its link target, so restore the whole tar or the named pair.
- The post-run readings (`post-run.txt`) are a captured file written on login12, not a transcription.
