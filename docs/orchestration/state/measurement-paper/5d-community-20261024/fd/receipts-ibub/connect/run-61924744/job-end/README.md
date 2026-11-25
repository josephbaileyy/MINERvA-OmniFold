# IBUB job 61924744's end: COMPLETED 0:0, IBUB-DONE published (2026-11-25)

**By** `director-helper-3`. The job was submitted by connect R under IBUB BINDING 2 (`../README.md`). Its state was
followed by sacct only. These are the watch's records and one read-only end check. The job's own records (the units,
the stage, the slurm out and the scontrol-batch log) are not here. They come in through connect O's fetch, checked
against RECORDS.SHA256SUMS, by the director's ruling of 2026-11-25.

| record | what it holds |
|---|---|
| `watch.sh.txt` | the watch script. It ran sacct `-X` on login38 every 600 s, logged every reading, and exited on a State change. At the certificate's expiry (1795570595, 2026-11-25T01:36:35Z) it would log `unknown` and stop with no retry |
| `sacct-watch.txt` | every reading, 2026-11-24T16:40:55Z to 2026-11-25T00:29:29Z: 4 PENDING, then 45 RUNNING, then the COMPLETED row. No reading was `unknown` |
| `watch.out.txt` | the watch's stdout: `CHANGED: 61924744\|ibub_run\|regular_1\|COMPLETED\|0:0\|None\|2026-11-24T09:02:14\|2026-11-24T16:29:24\|07:27:10` |
| `after-end-check.txt` | one read on login38 at 2026-11-25T00:29:51Z (stdout and stderr, NERSC's login banner included): `stat` and the bytes of `IBUB-DONE` read with `dd iflag=noatime`, its sha256 computed there, and `sacct -j` with every step |

**The end.** The job ran COMPLETED with ExitCode 0:0. It started at 09:02:14 and ended at 16:29:24, both -0800 (the
end is 00:29:24Z), for an elapsed time of 07:27:10, about 7.45 node-h against the 11.48 cap. `sacct -j` lists 63 rows,
all COMPLETED 0:0: batch, extern, 2 `ibub_refs_l*` steps and 60 `ibub_toys_l*_c*` steps. Each toy step ran 29:04 to
30:15. The highest MaxRSS was 15456696K, in step `.10`.

**IBUB-DONE** is a regular file of 507 bytes with mtime 16:29:24 -0800, and its sha256 is
`de4ff5467448e765e2fd8be6c971e9121a74736c4d78e4159a7871ca7b874064`. Its fields:
- job 61924744, M `d12c4f2a38a53001eb92bbefc8b2dc6001f034dc`, stage `toys`, rc 0;
- ref_rcs `0 0` and toy_rcs `0 0 0 0`;
- a completion block of schema `ibub-complete/2`: verdict PASS, toy_pass 600 of 600 expected, not_pass_count 0, no
  undeclared markers, barrier_pass true (`784163284dec6f750a8215146fb881a3564bc0bfe6672d94aef5494a3d58e579`) and
  deploy_head `d12c4f2a`.

These are the job's own claims. The readout grades them under the director's item-4 ruling: the job-wide
prerequisites, then C-COMPLETE per tune, with the terminal state disclosed and not used as a gate.

**CITABLE FOR:** the job's sacct end state and that IBUB-DONE was published with these bytes. **NOT CITABLE FOR:**
any IBU bias, any tune's grade, or any readout result.
