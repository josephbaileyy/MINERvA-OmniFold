# REPORT: S1 HPSS copy of the 5D universe weight bank and the detector dump (2026-10-25)

**By** the measurement session, under [`S1-BINDING.md`](S1-BINDING.md) §3, with its erratum (PR #342), and Joseph's
approval in `DECISION-20261024-joseph-approve-integration-wording-s1-compute-preserve.md`, item 3.
- Run on login12, 2026-10-25 00:36:21–01:07:34 UTC; 0 node-h; no Slurm job.
- Receipts are in [`s1/receipts-P/`](s1/receipts-P/): `preserve.log`, the tar's sha256, `quota-before.txt`,
  `launch.txt`, `post-run.txt`, `checks.txt`, and `SHA256SUMS`.
  - `checks.txt` is a later read-only capture from login12, taken at 01:18:36 UTC after independent review. It
    holds the link counts, times and sacct lines cited below.

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
  tree was untouched. This is the repair named in the S1-BINDING §3 erratum (PR #342).
- **Deviation: the copy started before the erratum was on `main`.**
  - S1-BINDING lets the copy start "once this record is on `main`".
  - The copy was launched at 00:36:21 UTC. The repaired inventory was written at 00:34:20 UTC.
  - The erratum was committed at 00:39:45 UTC (`f888722b`) and merged at 00:43:19 UTC (`a62a6040`).
  - So for about 7 minutes the run used an inventory path that no record on `main` authorized. `main`'s §3 command
    still read the inventory from `$D`.
  - The measurement session started the copy first and flagged the path to the director in its first status
    message, after the launch. The director accepted the repair afterwards and wrote the erratum. No prior
    acceptance was given. This sequence comes from the cross-session correspondence and is not receipted here.
  - The bytes the script read are the bound inventory: sha256 `cde96ca7…` is the binding's own prefix.
- **Arguments:** work dir `$B/preserve`; HPSS dir `/home/j/josephrb/mnv-5d-s1-inputs-20261024`.
- **How it was started:** detached on login12, pid 2207025.
  - `launch.txt` records only the pid, the time and the host.
  - The command, `setsid nohup bash …/stage0_preserve.sh … &`, comes from the session's terminal and is not
    receipted.
  - `nohup.out` is byte-identical to `preserve.log`; both have sha256 `b09b9cde…` (`checks.txt`).

**Preconditions (§3 condition 1),** read at 00:36:14 UTC (`quota-before.txt`):
- `hpssquota` read 353.98 of 512.00 GiB used, so 158.02 GiB was free. The floor is 80 GiB.
- pscratch read 16.99 of 20.00 TiB, so about 3 TiB was free. The tar and its retrieved copy need about 150 GB.
- `hsi ls -d` of the HPSS directory returned `HPSS_ENOENT`, so the directory was new.

**Overlap with S1 (§3 condition 3).**
- The copy ran beside the S1 pilot, job 60232432, which ran 00:47:54–00:59:56 UTC.
- S1's production and seed jobs were submitted at 01:01:57 UTC and were still PENDING at 01:18 UTC (`checks.txt`,
  sacct in PDT). The sacct rows carry no header; their columns are JobID, JobName, State, Submit, Start and End.
- **No inventoried file was written during the copy.** At 01:18:36 UTC the newest mtime and the newest ctime over all
  734 paths were both 2026-09-27T15:27:48Z (`checks.txt`). That is before the copy began. This also covers the
  interval between the hash re-verify (00:41:56) and the tar, which the script does not re-check.

| step | outcome (`preserve.log`) |
|---|---|
| 1. re-verify the 734 input hashes | "inventory verified: 734 files" (00:41:56) |
| 2. one uncompressed tar | sha256 `cc8353f7008e7ea77810942ee2e86c2116f22cc0c6c422abca353085ebd435a6`, 73,709,649,920 bytes (00:54:07). tar printed "Removing leading `/` from member names" and "… from hard link targets"; the second is not evidence of a hard link (below) |
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
- The inventory stored there is a copy of `PRESERVE-INVENTORY.sha256`, whose source has sha256 `cde96ca7…`. The
  HPSS copy's size, 116,791 B, equals the source's. Its hash was not checked on HPSS: it had no hashcreate and no
  retrieval.

**Cleanup (§3 condition 6).**
- The script deleted the retrieved copy itself.
- **Beyond condition 6's list:** the empty `retrieve/` directory was then removed.
- The temporary tar `$B/preserve/stage0-inputs.tar` was deleted after the PASS, at 01:09:18 UTC (`post-run.txt`).
- Kept: `stage0-inputs.tar.sha256`, `paths.list` and `preserve.log`. `paths.list` is 68,347 B, sha256
  `0dc13d9a…` (`checks.txt`).
- The inventoried files were not touched, and nothing was written to CFS.

**Quota after the copy** (`post-run.txt`, 01:09:09 UTC):
- `hpssquota` still read 353.98 of 512.00 GiB, the same as before. Stage 0 saw the same lag after its copy
  (`STAGE0-PRESERVE-REPORT.md`).
- Once accounting catches up, the 68.65 GiB tar should leave about 89.4 GiB free **(arithmetic)**.
- pscratch read 17.05 of 20.00 TiB.

**What this changes.** The bank and the detector dump no longer depend on surviving the pscratch purge, to which
they were exposed from about 2026-12-14 (`S1-PLAN.md:95-96`). That date is arithmetic, based on NERSC's 8-week purge
policy, which is not a repo record. If any file is purged, it can be restored from the tar and
checked against the stored inventory.

## What the receipts do and do not show

- **The member count** is now logged. `post-run.txt` records `tar -tf | wc -l` = 734, against 734 inventory lines.
  It was read from the pscratch tar before deletion. (The script's own count check prints nothing on success.)
- **The retrieved copy's sha256** is not printed separately. The script compares it with the tar's and exits 8 on a
  difference. It reached PASS.
- **The exit code** of the detached script was not captured; nohup's output is the log. The log ends in PASS. Each
  checked step (verify, tar, member count, put, hashcreate, hashverify, get, compare) prints "STOP" and exits 3–8 on
  failure, so reaching the PASS line means all of them passed.
- **Commands the script does not check:**
  - `mkdir -p`;
  - `hsi mkdir -p` (`|| true`);
  - `stat` and the `sha256sum > .sha256` write. A failed write would be caught only indirectly, by the retrieval
    compare;
  - `hsi ls -l`;
  - the `rm -f` of the retrieved copy. `post-run.txt` shows that it took effect.
- **Hard links: there are none.** All 734 inventoried paths are regular files with link count 1, and no inode
  appears twice (`checks.txt`). So no tar member is stored as a hard link, and any member can be restored alone.
  - GNU tar 1.34 prints "Removing leading `/` from hard link targets" even for an archive with no hard link. The
    independent reviewer reproduced this on two absolute paths with link count 1.
  - `STAGE0-PRESERVE-REPORT.md` drew the opposite inference from the same message. That inference is not supported
    there either.
  - 19 sha256 values appear more than once in the inventory: 15 pairs, two groups of 8, one of 14 and one of 22.
    That is equal content, not links.
- The post-run readings (`post-run.txt`) are a captured file written on login12, not a transcription.
