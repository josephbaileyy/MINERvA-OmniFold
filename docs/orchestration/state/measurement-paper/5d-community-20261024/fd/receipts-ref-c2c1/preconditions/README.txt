REF-C2C1 step one, REF-C2C1-DECLARATION.md §4 preconditions 3, 4 and 6 (REF-C2C1-BINDING-1.md ruling 4, #777, main
d00a3b66), with the REF-G1 follow-up listing folded in. Run by the cluster lane (limitation-resolver) on login04,
2026-11-05T09:46:56Z-09:47:48Z, 0 node-h. Copied with dd iflag=noatime from
/pscratch/sd/j/josephrb/ref-c2c1-20261105/preconditions/. Full sha256 of each file: SHA256SUMS.txt.

THE RECORD'S VERDICT IS FAIL (listing.json sha256 8790cce5...), AND IT DOES NOT BLOCK.
- The one failing line: MISSING E_R_inputs /pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/inputs/
  runEventLoopOmniFold_MEFHC.root, the staged copy of $CV that RE-2 part B's runs read.
- The cause: RE-2 part B's B9 cleanup deleted it on purpose at 2026-10-24T12:43:04Z, condition "last reader read out
  (J1,J4,J6 core PASS; J7 PASS)", as row 2 of docs/orchestration/state/2d-closeout/stageF/methods/re2/run/
  partb_readout/deletions.tsv records (sha256 43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df,
  2,144,008,221 bytes), and RE2-PARTB-REPORT.md §5 describes.
- The one MISSING file is a LISTING-DESIGN ERROR, NOT DATA LOSS: the listing required a staged copy without reading
  the campaign's deletion ledger first. The CFS original $CV (/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/
  xr-input/runEventLoopOmniFold_MEFHC.root), listed in the same run, is present and equal to 43f8cc16, the digest the
  deleted copy held. The other 306 files pass, and the library loads.

THE DIRECTOR'S RULING (2026-11-05), quoted:
  "1. Commit the FAIL record as is under fd/receipts-ref-c2c1/preconditions/, with SHA256SUMS. Add a README.txt that
   names the cause, citing deletions.tsv's row and RE2-PARTB-REPORT §5; states that the one MISSING file is a
   listing-design error, not data loss; quotes this ruling.
   2. (a) No rerun. The record is sufficient as the evidence of E_R's inputs: the CFS $CV equals 43f8cc16, which is the
   digest the deleted staged copy held, and the other 306 files pass. The verdict field stays FAIL in the record; the
   README says why it doesn't block. Next time, read each campaign's deletion ledger before listing its staged inputs."

WHAT PASSED
- Precondition 3: libRooUnfold.so (0b34e1e3...), with libRooUnfold_rdict.pcm (c0c995d7...) and libRooUnfold.rootmap
  (fa15007e...), copied by O_NOATIME read and loaded from the copy in PyROOT: gSystem.Load rc 0, RooUnfoldBayes class
  with dictionary, ROOT 6.28/12. The build directory listing is librooUnfold-ls.txt. (The copies stay on pscratch in
  libcopy/; binaries are not committed.)
- Precondition 4: E_R's central product (a5c13fc3), the CFS $CV and the baseline flux $MC (d40aea69), E_R's run log,
  and Q_R's 300 replica products S1_001..S1_300, each equal to its RE-2 part B SHA256SUMS row, seeds exactly 1..300.
- The REF-G1 follow-up: tune_v1.json (13bb1eae, = fd_f0_regrade.RATIO floor), s1_assembly.npz (db000707), the
  flux-universe file (5eecae84) and the flux constraint (e38ad7d2), each equal to its pin.
- Exposure (oldest atime + 8 weeks): the earliest is the pscratch baseline flux $MC, from 2026-12-18 (the director's
  calendar item 4; $CV is on CFS and not purged); E_R's central 12-27; the replicas, E_R's log and the follow-up
  files 12-19.
