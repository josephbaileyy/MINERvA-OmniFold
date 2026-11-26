# PG rehearsal checklist: what the first real run's log must answer

<!-- absence-ok: "untested", "cannot" and "no line" here describe this host's test coverage and how to read a log, not a claim that a result does not exist -->

The director (2026-11-25) accepted two guards that this host cannot exercise, on condition that the first real run
shows whether each fired or was needed. Both log a count-only line to pg_generate.sh's stdout, which holds no seed and
no path under W. Read that stdout after the rehearsal and record each answer here, with the run's head sha.

| guard | code | log line if it fired | if no line |
|---|---|---|---|
| A job reaped only once it is dead (one in uninterruptible sleep cannot hang the cleanup) | `kill_tree` | `[pg] cleanup: a job is left unreaped, still alive after KILL`, and before it `[pg] cleanup: <n> processes of a tree outlived KILL by 15 s` | every tree ended within 15 s of KILL; the guard was not needed |
| The 30 s poll after KILL in the drain (`pg_verify.py drain`, the generation's session) | `drain` | `[pg] cleanup: <n> processes outlived their trees`, then `the survivors ended after <i> polls (0.5 s each, 30 s at most)` or `<n> survivors still alive 30 s after KILL` (a STOP) | no survivor outlived its tree; the poll was not needed |
| A process outside the run with its cwd in W (round 5) | `drain` | `[pg] cleanup: <n> processes outside this run have a cwd in W (not killed)` (a STOP) | none was there |

For each line, record the step it follows (`[pg] ...: pass` or STOP), and for the poll, the `<i>` at which the
survivors ended.
On this host, `test_an_orphan_that_left_w_is_killed_by_its_group` exercises the drain's first two lines, and
`test_a_process_outside_the_run_with_its_cwd_in_w_stops_and_lives` the third row. `Round5Drain` exercises the 30 s
deadline with a simulated clock. The first row, and the 30 s STOP on a real kernel, are not exercised here.

Also record, from `W/out/node_check.json` (C3 and Q2, a record and never a gate): `hidepid`, `slurm_job`,
`all_cpus_allocated`, `other_user_processes`, `core_pattern` and `core_limit` (the job's, 0 after `ulimit -c 0`).
From `W/out/pin_hash_start.json` and `pin_hash_end.json` (Q1): `files`, `links` and `pass`.

| run | head | kill_tree | drain poll | node_check |
|---|---|---|---|---|
| (rehearsal) | | | | |
