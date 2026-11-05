REF-G1 reader, connect 2 of 2: the READ (REF-G1-BINDING-2.md rulings 3, 4 and 6; the director's ruling of 2026-11-05:
bars, then the merge of bars.json to main (#791, main 9d69945e), then this read). Run by limitation-resolver on login27,
2026-11-05T15:17:34Z-15:18:17Z, 0 node-h. Copied with dd iflag=noatime from /pscratch/sd/j/josephrb/ref-g1-20261105/read/
(and gibu1.done from .../batch/units/). Full sha256 of each file: SHA256SUMS.txt.

OUTCOME: STOP. The bound reader's G-IBU1 control failed; no Delta was formed and no readout.json was written. Reader
stderr: "STOP: failed controls ['G-IBU1']; no reading was formed"; reader rc 1, connect rc 1. Nothing was repaired or
rerun; the diagnosis is the director's.
- Preconditions, all met before the reader ran (read.log): batch DONE 233/233 (job 60857388), SHA256SUMS 6a4c1929...;
  local bars.json de12c674...; origin/main 9d69945e's committed bars.json de12c674..., equal to the local file; a fresh
  clone at M 609d8f24, porcelain --ignored 0 before, the 5 bound blobs verified; interpreter 3.11.14 (root_6_28).
- STOP.json (sha256 12762cf7...), written by ref_g1_read.py read (blob e49ab974) beside bars.json: it records the
  controls, not a reading. G-draw, G-pair, G-CV and G-cells pass; G-IBU1 fails with arrays {ks: equal, F_fold: not
  equal, F_sub: not equal} between the batch's gibu1.npz and the configured IBU-1 reference (whose own digest check
  passed: STOP.json carries no "why").
- The batch's gibu1 unit: gibu1.done (its done-marker, verdict PASS, sha256 70bb60d0...); gibu1.npz sha256
  70bb60d0c928822ee17494343226c35055f54a38d2dfb17bce60f0ad20a78741, recomputed now by an O_NOATIME read, equal to the
  marker's and to its line in the batch's SHA256SUMS (18,718 bytes; not committed).
- read.stdout is empty (0 bytes): the reader prints a reading only after the controls pass. read.time (GNU time: wall
  0:03.27, MaxRSS 88,064 kB), read.done (rc 1), clone-read.log (empty), and the connect as run, refg1_read_login.sh
  (25e44b6d..., approved by the director). Porcelain --ignored 0 after.
