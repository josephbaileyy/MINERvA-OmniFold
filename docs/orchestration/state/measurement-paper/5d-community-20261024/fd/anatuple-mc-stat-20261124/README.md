# MC AnaTuple retention stat, 2026-11-24T11:58:32Z (login05): exposure now 2027-01-18

**By** limitation-resolver, at the director's request (2026-11-24), to re-measure the purge exposure of the MC
AnaTuples that an event-loop E_ν pass would read. The 11-11 retention record (`retention-20261110/AT-RISK.md`) gave
2026-12-19.

**How it ran.**
- One ssh session to login05 ran [`anatuple_stat.sh`](anatuple_stat.sh) on stdin. It gives each of 489 listed paths
  once to `stat -c "%s %X %Y %n"`, which reports the size, atime, mtime and name.
- No directory was listed and no file was opened. stat does not move the atime. Nothing was written on the cluster.
- The list is the 11-11 record's two MC groups, exactly as its committed `receipts/session.txt` names them:
  - `anatuple_mc_1A`, 41 files;
  - `anatuple_mc_1B-1P`, 448 files.
- ssh rc 0 ([`ssh-rc.txt`](ssh-rc.txt)). [`stat.out`](stat.out) is the session's stdout, verbatim: `checked 489 missing 0`.

**The result.**

| group | files | bytes | oldest atime now | exposure (oldest atime + 56 d) | 11-11 exposure |
|---|---|---|---|---|---|
| `anatuple_mc_1A` | 41 | 706,929,079,280 | 2026-11-23T22:35:46Z | **2027-01-18** | 2026-12-19 |
| `anatuple_mc_1B-1P` | 448 | 9,827,031,062,141 | 2026-11-23T22:03:30Z | **2027-01-18** | 2026-12-19 |

- All 489 are present.
- All 489 have the same size and mtime as on 11-11.
- All 489 atimes moved since 11-11. They were read between 2026-11-23T22:03:30Z and 2026-11-24T07:52:06Z, by someone
  other than this lane.
- The earliest exposure of the set is therefore **2027-01-18T22:03:30Z**, about a month later than the 11-11 figure.
- Exposure is the date from which pscratch's 8-week purge may take an unread file. A later read moves it further.

**CITABLE FOR:** that these 489 files existed at 2026-11-24T11:58Z with the sizes and atimes recorded, and the
exposure arithmetic. **NOT CITABLE FOR:** who read them, or any physics result.
