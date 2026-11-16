# FD-PRR addendum A4: the staging of the four fine-ratio rho arrays

The valid-region lane ran this on 2026-11-09, on the director's go for `prr_stage_a4.sh` at sha256
f8b87d89cf4b893a3edb532d900d69eb52d0894dd0a44b222a625505dc1f4c6a, after A4's binding (#1003, 5591ec00; M_A4 = cb13a644).
It is FD-PRR-ADDENDUM-A4.md section 10.2: the four rho-*-F.npz that route 2's fine-ratio hypotheses name were copied
once, through `prr_probe.py stage` (O_NOATIME), into `$OUT/stage/s5p-nullsF/`. The record went to `$OUT/stage-a4.json`;
`$OUT/stage.json` was not touched. It cost 0 node-h, on a login node.

CITABLE FOR: the four copies' sha256, each equal to its committed json's rho_npz sha256; stage-a4.json's content and
sha256 (00457e58…); each source's stat (size, mtime, atime, inode) unchanged across the copy; the deploy's checks at
M_A4; cov2d's answer on s5p-20260926 as recorded, and the director's ruling on it.
NOT CITABLE FOR: attempt 3 or any route-2 result; what read the sources before this step (their atimes, 13:28-13:35Z
on 2026-11-09, predate it).

## The session

- **One foreground ssh session** on login28 at 2026-11-09T22:40:00Z, with ssh's rc read unpiped: 0. The whole session
  is in `lane/stage-session.txt`.
  - The script was copied to /dev/shm and checked at its sha256 (`:2`). The connect removed that copy at exit (`:9`).
  - iris's m3246 row and `squeue --me` were printed first (`:3-7`). The two jobs listed are cov2d's ll5d_gate_AR23
    61040235 and ll5d_gate_G18 61040163, then RUNNING; no prr_* job.
    <!-- absence-ok: the session's own squeue --me listing, lane/stage-session.txt:5-7 -->
  - The session printed the connect's done file, `0` (`:10-11`), and its log, `$OUT/logs/connect-stage-a4.log`
    (`:13-133`).
- **The script** is `lane/prr_stage_a4.sh`. `lane/stage-a4-fill.diff` is its diff against the template
  `fd/receipts-prr/a4/prr_stage_a4.sh.template` (c4b7148f), and it holds:
  - the fills for M, A4_SHA and BIND_SHA;
  - the six FD-PRR sums at M_A4;
  - a four-line echo block that records cov2d's answer.

## What the connect checked and did (`lane/stage-session.txt`)

- **No other process, and no other lane copying.**
  - No process on the node named s5p-20260926 (`:19-20`).
  - cov2d's answer, asked at the director's instruction before the connect was made (`:21-24`): its LL5D gates read and
    list only under `s5p-20260926/bank_detector`, never `ratios/` or nullsF, and none of its steps copies from
    s5p-20260926.
  - The director ruled them clear (2026-11-09). The condition was about copying. The gates read other files, and
    directory atimes are not a control (BINDING 1 ruling 5).
- **The deploy** at `$OUT/deploy-stage-a4`:
  - HEAD cb13a6443a457bd3887d1c421723dfcdb1909ec8, with 0 porcelain --ignored lines before (`:25`) and after (`:131`);
  - the six FD-PRR files OK (`:26-31`);
  - the declaration and addendums A1, A3 and A4 at their bound sha256 (`:32-35`);
  - BINDING 1 at origin/main 5591ec00 at 634cded3… (`:36`).
- **The pins.** The committed `null-*-F.json` rho_npz entries in the deploy are the connect's four pins (`:37-40`). The
  deploy's own `prr_ibu.py stage-a4-manifest` equals them ("MANIFEST OK", `:41`).
- **The copy.** `prr_probe.py stage` printed `{"staged": 4}` (`:42-43`). Each copy then passed `sha256sum -c` against
  its pin (`:44-47`).
- **The record.** `stage-a4.json` sha256 00457e58f135c6bff0207901f9bb977ce6338d9b01971df376d2fe333750d7df (`:48`).
  - The file's content as the session printed it is `cluster/stage-a4.json`. Its sha256 is the same 00457e58…, so the
    copy is byte for byte.
  - The connect ended with rc 0 at 2026-11-09T22:40:46Z (`:132-133`).

## The four copies and the stat records (`cluster/stage-a4.json`)

| copy | sha256 (= its json's rho_npz) | size | mtime (UTC) | atime before = after (UTC) |
|---|---|---|---|---|
| rho-genie_cv-F.npz | `124e726163b38d24735bacfc67e2d88bec1e47634dc5d294f6460fe4223efb8b` | 37568 | 2026-09-27T09:10:43Z | 2026-11-09T13:28:29Z |
| rho-genie_mec-F.npz | `2945a15a54dcf71f7ff495555f3cd0efb6c486232c2ddc18d6bbad46579e09b3` | 37982 | 2026-09-27T09:10:44Z | 2026-11-09T13:28:29Z |
| rho-gibuu_cv-F.npz | `d8f52112b010e5adb6a56fa4aa3629b4c98ab62a1cea3b4190af77c3ac33491b` | 39772 | 2026-09-27T09:10:45Z | 2026-11-09T13:31:31Z |
| rho-nuwro_cv-F.npz | `c5e10bd0edf70b8aced95ab8214630998fd1c903683570be30b85e25c12637fd` | 42605 | 2026-09-27T09:10:45Z | 2026-11-09T13:35:30Z |

- For each source, `stat_before` equals `stat_after` in every field: size, mtime_ns, atime_ns and ino. The times above
  are the json's nanosecond values, converted.
- `prr_probe.stage` refuses when the two stats differ, and when a copy's sha256 differs from the source's.

## Files

- `lane/stage-session.txt`: the session's output, with the connect's log inside it.
- `lane/prr_stage_a4.sh` (f8b87d89…) and `lane/stage-a4-fill.diff`.
- `cluster/stage-a4.json` (00457e58…).
