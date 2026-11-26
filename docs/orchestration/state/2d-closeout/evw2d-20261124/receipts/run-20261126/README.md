# EVW2D run, 2026-11-26 (EVW2D BINDING 1)

The run of `2d-unfolding/evw2d/evw2d.py` under EVW2D BINDING 1 (#1370, merge 3a305b56). It used the binding commit C
462a0756 and the lane `/pscratch/sd/j/josephrb/evw2d-20261126`. The bound launch scripts ran from
`launch/bound/` in a clean checkout at 3a305b56. The director accepted the result as PASS.

| step | when (UTC) | result |
|---|---|---|
| connect (login02) | 07:23–07:27:10 | rc 0; job 62022231 submitted held, checked by scontrol (`NumNodes=1-1`, TimeLimit 00:30:00), then released |
| job 62022231 | 08:34:00–08:45:53 | COMPLETED 0:0, 713 s on 1 node, 0.1981 node-h |
| post (login02) | 08:48:20–08:48:46 | rc 0, `PASS=true`; `post.pass` published |
| fetch | 08:48:46– | `post.tar.gz` |
| cleanup (login02), its own GO (BINDING 1, ruling 2) | 09:01:07–09:01:35 | rc 0; `evw2d.py cleanup` removed exactly the two stage copies (`cleanup/deletions.tsv`, 2 rows) |
| fetch | 09:01:35– | `cleanup.tar.gz`; `post.tar.gz` byte-identical to the first fetch |

- `post.tar.gz` (sha256 `b4b26dc30bad15342441713c91f355f1098e207cb01e930ed048e2471208533e`) is the archive as fetched; `post/` is its extraction. It holds the post's log,
  accepted.json, sacct.txt, stat-post.txt, the small products and the job's and connect's logs.
- The products' SHA256SUMS digest is `e60867ef66eb47172a0e90140abc7a366d780dfc3aa3f9beb426a40a48d1416e`. weights.npz stays on scratch and is not copied here.
- The exactness gates in `post/out/run.json` are C-EXACT-ER (max_rel 9.16e-12) and C-EXACT-PAPER (max_rel 5.06e-12),
  against 1e-8. All 12 controls pass, and there is no fallback.
- `post/logs/probe-62022231.log` puts on record that inside an srun step on Perlmutter `SLURM_JOB_NUM_NODES` is the
  bare `1`, with `SLURM_STEP_ID=0` and affinity 64.
- `session/` holds the Mac-side launcher output for each step: the session's stdout and stderr (stderr is NERSC's
  login banner) and the scp logs.
- `cleanup.tar.gz` (sha256 `b2030e065524ff0173c9c2cfb46f82c0b4c0a0a37e2446f6fec0fdf04f251ebd`) and its extraction
  `cleanup/` hold the ledger: `<lane>/stage/runEventLoopOmniFold_MEFHC.root` (43f8cc16…, 2144008221 bytes) and
  `<lane>/stage/runEventLoopMC_MEFHC.root` (d40aea69…, 5143 bytes). The stage listing is there before and after: the
  directory stays, empty. The products and `out/` are untouched; removing them is Joseph's call.
