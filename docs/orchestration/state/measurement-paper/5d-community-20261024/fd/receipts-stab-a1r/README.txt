Receipts of the FD-STAB (B4) dry run under ADDENDUM A1 and the Director's correction (FD-STAB-BINDING-1-A1.md,
merged ff6ba188, corrected c6f104ee/#766). Code pin M_A1 = cc54d86f7ac66c1346fa69e5894b2d2f000fb09c.
Copied by limitation-resolver on 2026-11-04/05, every cluster file read with dd iflag=noatime, from
$OUT = /pscratch/sd/j/josephrb/fd-stab-a1r-20261104 unless stated. Full sha256 of every file: SHA256SUMS.txt.

pins/      the fresh DTN pins check on dtn01: pins-check.json (verdict PASS, written 2026-11-04T23:51:48Z), check.log,
           check.done, and the script as run (stab_pins_a1r_dtn.sh, sha256 33d3d782...).
connect/   the dry-run submit on login03: connect-dry.log (it prints "invalid job 60826464: TIMEOUT|73|1",
           "cap_left_node_h=7.9797" and "scontrol TimeLimit=00:45:00 (declared 00:45:00)"), connect-dry.done,
           submit-dry.out, the script as run (stab_dry_a1r_submit.sh, sha256 ed2c74fc...), the job's Slurm output
           fd_stab_dry_60827080.out, and the queue the job ran (queue.tsv, 128 tasks; dry.tsv, 9 tasks).
dry/       $OUT/log-dry: truth-control.json and .log (C1 and C2 pass), DONE, SHA256SUMS (the 9 products), env.log,
           and tasks/: the 9 GNU time records (.time) and the 9 gate start/end epochs (.start/.end).
binding-delta.txt    the receipt-binding inventory delta (one ADDED: s1/PRESERVE-INVENTORY.sha256) and its power test.
gate-projection/  project_offline.py and its output project_offline.out.txt: the bound probe's project() at M_A1 on
           connect/queue.tsv and dry/tasks/, at now = t0 (the full run's first gate, before any full-run time).
sacct-60827080.txt   the valid dry run (COMPLETED, 992 s, 1 node).
sacct-60826464.txt   the INVALID run (TIMEOUT at its 1-minute limit, 73 s, 1 node), counted against the cap.
invalid-60826464/    that run's connect log, Slurm output and script as run, from /pscratch/sd/j/josephrb/fd-stab-a1-20261104.
