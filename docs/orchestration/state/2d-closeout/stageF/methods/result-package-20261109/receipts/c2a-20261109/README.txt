Result package, 2D arrays: the read-only copy of cov2d_Q_205.npz and its lossless CSV transcription. Run by
limitation-resolver on login27 at 2026-11-09T08:13:10Z, at nice 19 and 0 node-h, with no Slurm job. These receipts are
internal records; they are not part of the shipped package.

RELEASE: the director's GO of 2026-11-09 on connect/cov2d_arrays_login.sh, sha256
f883554c71eb83d20e9831eee948cfcbf9c1308d096ac41ea14905ce74c2191b, verified by the director from git at 88878aa3. The
node compared the digest of its /dev/shm copy before running it. The sshproxy certificate is valid to
2026-11-10T00:11:04Z (ssh-keygen -L, read locally).

BEFORE THE CONNECT
- cov2d_fence.sh from the Mac, rc 0 at 08:10:48Z: "FENCE: no cov2d-* job queued or running" (fence-mac.out).
- Login survey: login27 had the lowest load, 10.36 (survey.txt).

THE CONNECT (c2a.out; c2a.err is the NERSC banner only). ssh rc 0, read unpiped.
- stat before and after, byte-identical, atime included:
  regular file|882727051059074779|1|2022426|1792858709|1792862994|1792858709|/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partc-r2/outA/cov2d_Q_205.npz
- One O_NOATIME read: 2022426 bytes, sha256 7153b194b95c27f80db5997bdde35fe2475f2b1c40c9ff456edd409850cf47d2, equal to
  the bound digest (re2/run/partc_r2/partc-r2/SHA256SUMS:76). Read rc 0.
- Nothing was written on the cluster beyond deleting the connect's own /dev/shm copy.
- In the committed c2a.out, the base64 block is replaced by a one-line note giving the decoded bytes' sha256 and the full
  stdout's.

THE MAC SIDE
- decode_c2a.py (connect/, sha256 609725e3...), rc 0 (decode.out):
  - the decoded bytes' sha256 equals the cluster's and the bound digest;
  - Q, s5_total, universe, stat, c08 and C_PL are each float64 [205, 205], with sqrt(trace) equal to the committed
    outA/cov2d_Q_205.json.gz to 1e-12 relative;
  - cells is int64 [205] and x float64 [205].
- The npz itself stays outside the repository (director's ruling).
- transcribe_c2a.py, rc 0 (transcribe.out), wrote transcription/:
  - cov2d_x.csv: global_id and x;
  - cov2d_{Q, s5_total, universe, stat, c08, C_PL}.csv: 205 x 205 matrices with global_id headers.
  Each float64 is written as Python's repr. The round trip parses every file back, and every array is bitwise equal to
  the npz's (ndarray.tobytes()). It found no NaN, infinity or negative zero. The seven files' sha256 are in
  transcribe.out and SHA256SUMS.txt.

WHAT USES IT: build_package.py reads transcription/ as committed input, pinned by sha256. It checks the arrays against
outA/cov2d_Q_205.json.gz (sqrt-traces), outA/budget_Q.json.gz (per-cell median, p84, min and max per block; the
integral sigma; the pT and p_par projection sigmas), fig67/fig67_projections.json (projection totals), values.tex
(\sigTwoD, \uqMedian, \uqIntegral) and 2d-unfolding/pv2d/ratios/projections.json (bin edges, reported cells).

FILES: c2a.out, c2a.err, fence-mac.out, survey.txt, decode.out, transcribe_c2a.py, transcribe.out, transcription/.
Digests: SHA256SUMS.txt.
