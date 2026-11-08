1B pre-check Part 1: P2's three CV products against the staged derivation CV, bit for bit. PASS. 2026-11-08T06:50Z,
login03, 0 node-h.

coverage-5b-audit suggested this check on #923 as optional, and the director gave the go before P3. The connect is
pfd_p2_cvcheck.sh, sha256 70ebae4d75506437c70be301d52ff33686456dc568a7010c0bc7fa3f764e06ed. It reads, with O_NOATIME,
the staged derivation CV copy and P2's three CV products; reading those three arrays was allowed for this check alone.
It writes nothing.

Before the connect, from the Mac: fence-mac.out (no cov2d-* job) and survey.txt (login03 lowest). One ssh
(saul -> login03) compared the script's sha256 (matched) and ran it. ssh's rc was 0, read unpiped; the connect's rc
was 0. The in-script fence passed: squeue listed no jobs.

cvcheck.out:
  reference $V/stage/derivation/fd1b_derivation_CV.npz  sha256 44f22acf...  keys meta, xsec_flat, xtrue_flat
  fd1b_pfd_A_CV.npz     sha256 0876f73e...
  fd1b_pfd_B_CV.npz     sha256 dfc186f9...
  fd1b_pfd_Dnom_CV.npz  sha256 ecea5e25...
  For every mode, xsec_flat and xtrue_flat each match the reference: dtype float64, shape (65856,), array_equal True,
  no differing index.
  CV BITWISE: PASS.

cvcheck.err holds the login banner and host line only.
