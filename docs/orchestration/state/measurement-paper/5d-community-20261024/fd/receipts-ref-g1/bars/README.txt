REF-G1 reader, connect 1 of 2: the BARS (REF-G1-BINDING-2.md rulings 3, 4 and 6; the director's ruling of 2026-11-05:
bars, then this merge, then the read). Run by limitation-resolver on login27, 2026-11-05T15:01:14Z-15:05:38Z, 0 node-h.
Copied with dd iflag=noatime from /pscratch/sd/j/josephrb/ref-g1-20261105/read/. Full sha256 of each file:
SHA256SUMS.txt.

bars.json (sha256 de12c6745b4f5353a83ae8573c7cc75d986617f7a21d8b4ea4c5e275d8607780) is the file the read (connect 2)
must find on origin/main before it forms the central Delta; ref_g1_read.py read refuses unless --bars-sha256 equals this
file's sha256, and unless its reader_sha256, config_sha256 and products_digest match.
- Made by the bound reader's bars mode (ref_g1_read.py, blob e49ab974, at M 609d8f24) from a fresh clean clone,
  porcelain --ignored 0 before and 0 after, the 5 bound blobs verified; from the paired replica (50) and universe (175)
  differences of the batch (job 60857388, DONE 233/233, SHA256SUMS 6a4c1929...) alone. No read ran; no central Delta,
  T or reading exists.
- The self-check (the stat-only limit against (50-1)*16/(50-16) F(16, 34), 10^6 draws, seed 20261105): PASS at both
  levels (0.95: empirical CDF 0.949755 at the law quantile, tolerance 0.00087; 0.997: 0.996993, tolerance 0.00022).
- The bars at levels 0.95 and 0.997, from 10^6 draws (seed 20261104): see bars.json "bars"; the stat-only sensitivity
  null beside them, "sensitivity_stat_only_null".
- bars.log (the run's log), bars.time (GNU time: wall 3:45.53, MaxRSS 340,420 kB), bars.done (rc 0), and the connect as
  run, refg1_bars_login.sh (f2962b10...).
