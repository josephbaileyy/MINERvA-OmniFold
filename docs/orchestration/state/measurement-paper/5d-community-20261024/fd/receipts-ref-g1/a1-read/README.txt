REF-G1 addendum A1, connect 2: the READ (REF-G1-BINDING-2-A1.md ruling 4.3; A1 section 5 step 4; code at M' =
0bb9a1bf). Run by limitation-resolver on login27, 2026-11-06T05:41:30Z-05:42:19Z, 0 node-h, under the binding's
fixed conditional sequence (sha256 and result reported, no go awaited). The connect as run: refg1a1_c2_read_login.sh,
sha256 ce6e616690e04949c074c627851dcf645134c37a3dbd01d48922bf752840bf50. Copied with dd iflag=noatime from
/pscratch/sd/j/josephrb/ref-g1-20261106/read/ and its logs-read/. Full sha256 of each file: SHA256SUMS.txt.

OUTCOME: the read completed, rc 0; readout.json written (sha256 4db170d36cffa0be2aeb53926e94158ef4e5e2e1d88fa50dd29baeace8ed6fd7,
43,561 bytes); no STOP.json (the reader writes STOP.json and returns 1 when a control fails). The readings are in
readout.json and read.stdout; this lane has not opened either and quotes none (the director reads them from main).
- The gate (read.log): connect 1's PASS record on main: origin/main a6054769's fd/receipts-ref-g1/a1-connect1/bars.json
  hashes to ba4b6985..., equal to the read directory's bars.json; its gibu1-product.tsv carries exactly this connect's
  pin (/pscratch/sd/j/josephrb/ref-g1-20261106/gibu1/gibu1.npz, 683b4936...), equal to the product on pscratch. The
  batch is the accepted one (DONE 233/233, job 60857388; SHA256SUMS 6a4c1929...).
- The read: a fresh clone at M', porcelain --ignored 0 before and 0 after, the binding's 5 blobs, 0 mismatches;
  `ref_g1_read.py read --run <batch>/units --bars <read>/bars.json --bars-sha256 ba4b6985... --out
  <read>/readout.json --gibu1-product <...>/gibu1.npz --gibu1-sha256 683b4936...`, root_6_28 (3.11.14), 4 threads,
  nice 19, ionice idle; GNU time (read.time) wall 0:04.27, MaxRSS 96,256 kB. The reader staged 235 files into
  read/inputs-read/ (its 234 declared inputs and the gibu1 product), each through O_NOATIME.
- The stat (no read) of 237 paths, `ref_g1_read.py reads`' 236 and the gibu1 product (watch.txt), before and after
  (watch-before.txt, watch-after.txt): byte-identical, so no atime moved; all 237 owned by josephrb.
- COV2D fence: no cov2d-* job in squeue at 05:41:30Z (also checked from saul at 05:39:44Z).
- The reader's stdout went to read.stdout (40 bytes), not to read.log, so read.log carries no reading.
- Files: readout.json, read.stdout, read.log, read.time, read.done (rc 0), clone.log, reads.tsv, reads.err (empty),
  watch.txt and the two stat files, and the connect as run.
