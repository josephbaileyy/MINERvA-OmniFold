#981 re-pin, the rebuilt 2D covariance: the lossless CSV transcription of COV2D-G2R's data_g2r.npz. Made by the
limitation-resolver lane on the Mac on 2026-11-14, at the director's request of that day, for rows RP34-RP40 of
../repin_list.tsv (D1: DECISION-20261114-joseph-d1-g2r-adopted.md). No cluster connect: the source is cov2d's local
copy. These receipts are internal records. They are not part of the shipped package, and #981 is not edited before
the freeze.

THE SOURCE (SOURCE.txt)
- cov2d fetched the readout outputs with O_NOATIME reads. The copy used is
  /Users/josephbailey/cov2d-work/g2r/readout-fetch/node/readout/data/data_g2r.npz, 1,306,260 bytes.
- Its sha256 3b8cc7ceaef97c3dc6bbcd2c5cfdf853442c347e37e23f64eca54898d0e9eb4b equals the node's, as committed in
  fd/receipts-cov2d/g2r/readout/data/out.sha256.txt (PR #1144). The npz stays outside the repository, like c2a's.

THE TRANSCRIPTION (transcribe_g2r.py, transcribe.out; rc 0)
- The npz holds C_new, C_univ_old and C_univ_new (each float64 205 x 205), and 38 band__<band> arrays with 175
  universe rows in all (Flux 100, 2p2h 3, every other band 2), each row 205 cells.
- The cell order: the npz names no cell ids. C_new equals c2a's Q - C_univ_old + C_univ_new byte for byte, with Q
  read from #981's committed c2a transcription (cov2d_Q.csv, sha256 4f07aa88...). So the npz is in c2a's order, and
  the transcription uses c2a's global ids.
- The medians: the script recomputes the median per-cell relative sigma of c2a's Q (6.413665927768751) and of C_new
  (6.463024978099694). Each equals data_g2r.json's readings.sigma.median_pct exactly.
- transcription/ holds g2r_C_new.csv, g2r_C_univ_old.csv and g2r_C_univ_new.csv (205 x 205, global_id headers)
  and g2r_bands.csv (band, universe, then the 205 cells). Each float64 is written as Python's repr.
- The round trip parses every file back. Every array is bitwise equal to the npz's (ndarray.tobytes()), after NaN,
  infinities and negative zeros are refused. The four files' sha256 are in transcribe.out and SHA256SUMS.txt.
- TESTS.out: four refusals, each rc 1: a file with another sha256, an output directory that is not empty, a lossy
  (15-digit) writer, and a wrong cell order.

WHAT IT MEANS FOR #981 (SUMS.out, sums_check.py)
- The package's universe block is not C_univ_old. G2R rebuilt the 175-universe part. The package's block also holds
  the other bands and the normalization: their difference has 6 eigenvalues above 1e-12 of the largest. So the
  package's new universe and s5_total blocks are derived as universe - C_univ_old + C_univ_new, and s5_total likewise.
  Q is C_new itself.
- #981 requires Q == s5_total + C_PL and s5_total == universe + stat + c08 bitwise (build_package.py:575-579). Under
  C_new they hold only to rounding. Under either derivation order about 5,000 to 11,000 of the 42,025 entries
  differ in the last bits; the largest residual is at most 1.3e-16 of the largest entry. The old blocks satisfy both
  identities exactly. Any derivation leaves at least one of them inexact, so RP35's "the exact-sum needs stay" needs
  the director's ruling. The lane proposes shipping Q = C_new byte for byte and checking both identities at 1e-15
  relative.
- \fluxBand (RP38) is budget_Q's bands.Flux.median_pct (re2c_build_q.py:618). It needs the 100 Flux universe weights
  with g2r_bands.csv's Flux rows. data_g2r.json records only their sum and n_eff, and the npz does not carry them. Its
  producer is being agreed with cov2d, as the director asked.

FILES: README.txt, SOURCE.txt, transcribe_g2r.py, transcribe.out, TESTS.out, sums_check.py, SUMS.out, transcription/.
Digests: SHA256SUMS.txt.
