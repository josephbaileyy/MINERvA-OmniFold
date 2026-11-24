# The Docker stand-in at M = 1031c8200 (2026-11-24)

The same driver, image and variants as `../README.md`. The local-only stand-in commit
`892c7320206bf7d1e15fb37e60f462271e974c79` is `1031c8200` with only `config.json`'s five input pins changed. It is never pushed, and
it is deleted after the run.

All 10 variants behaved as declared, with the same rc, stop, records and sbatch outcome as before. Their logs are in
this directory.

**The real connect R** (`../../ibub_run_connect.sh`, generated at M = `1031c8200`) differs from the stand-in's
connect in exactly two lines: `M=` and `config.json`'s embedded sum (checked by `diff`). The sums of the other
five ibub files, and every other byte, are identical.
