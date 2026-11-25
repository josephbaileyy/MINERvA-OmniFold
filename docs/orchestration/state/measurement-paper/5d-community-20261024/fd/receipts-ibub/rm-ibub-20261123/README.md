# The removal of the old IBUB namespace /pscratch/sd/j/josephrb/ibub-20261123 (2026-11-24)

**By** `director-helper-3`, on the director's GO, under Joseph's authorization of 2026-11-24, given directly to the
director: "you can remove that old folder". It covers this one path and nothing else.

That namespace held BINDING 1's deploy, stage/ and logs. Connect R stopped there after sbatch (STOP 5, QOS=regular_1),
and job 61914825 was cancelled. Those records are on main in #1289 (`../connect/run-stop-61914825/`, fetch-run.tar
`7e84a86269f79a76ff5c124f40e495fdd864f678fec76721e389224aebb02346`). The IBUB run moves to `ibub-20261124` (M‴,
#1292), which this removal does not touch.

| item | record |
|---|---|
| the script | `rm-ibub-20261123.sh`, sha256 `e7f875eabff78091a706d435165be2d507cd680736a61f44908e90c5165714bc`. The path is a literal, there is no argument, and every check refuses (rc 9) before anything is removed |
| its launcher | `rm-launch.sh`, sha256 `5ffb30da32e66e1444999921dc1354266dca1b1a5b9c26b6b8d0eb14274daa4e`. It is its own login connect on login38: the /dev/shm copy is sha-checked, run detached, read back and deleted |
| the run | `launch-start-utc.txt` 2026-11-24T16:23:09Z; the script's first line, `host login38 utc 2026-11-24T16:23:21Z`; the launcher ended at 16:24:04Z (`launcher.out.txt`) |
| the checks | `path ok` (a directory, owner josephrb, realpath equal); `sacct ok: 1 ibub_ rows, all ended; 61914825: 61914825\|ibub_run\|CANCELLED by 112498`; the directory's stat (mtime 1795531043, inode 882727748622181832, owner josephrb) was equal before and after the inventory |
| the inventory | `inventory.txt`: the `find -printf '%y %s %T@ %p'` block as fetched, sha256 `f76f2d78960df24c9f1d6d919e663521d2bb068a5276baffe44fd543ea1ab938`. It has 32,660 entries (3,126 directories, 29,413 files, 121 symlinks) and 3,667,054,967 bytes in files. Counted again from the file, these equal the script's own line `inventory: 32660 entries, 29413 files, 3667054967 bytes` |
| what it held | deploy/ (the clone at `db8854e28`): 29,390 files, 1,505,626,478 bytes, of which the git pack is 520,401,567. stage/: 4 files, 2,161,334,428 bytes, of which the staged CV copy is 2,144,008,221. logs/, fetch-run/ and fetch-run.tar: 19 files, 94,061 bytes, all already on main in #1289 |
| the removal | `rm rc=0`; `stat rc=1: stat: cannot statx '/pscratch/sd/j/josephrb/ibub-20261123': No such file or directory`; `removed: … is gone (ENOENT)`; `rm-ibub rc=0`; launcher rc 0 |
| the ledger | `deletions.tsv`: one B9-form directory row in RE-2's columns (utc, path, sha256 of the inventory, size in bytes, mtime, inode, stat_match yes, condition) |
| the tests | `test/case.sh` (sha256 `c5e9e43a…`) ran 13 cases in Docker on this exact script, and `test/cases.log.txt` (`10403b94…`) has every case's output. The ok case removes only the path; the new `$N`, cov2d-run, cov2d-2a and an rpd root are kept, and a symlink inside the path is removed, not followed. Each of the 12 refusals fires with its own message, and the path is left in place |

`session.out.txt` is the whole session as the launcher fetched it, the inventory included. `session.err.txt` is the
NERSC login banner.
