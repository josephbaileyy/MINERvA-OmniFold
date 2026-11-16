BV96 O1: the read-only copy of FD-STAB's 70 control products, and the power simulation it feeds. Run by
limitation-resolver on login40 at 2026-11-10T05:14:35Z, at nice 19 and 0 node-h, with no Slurm job.

RELEASE: the director's GO of 2026-11-10 on connect/bv96_power_read_login.sh, sha256
2f35f99f873a0ff462e3666e81ff7745ad214ae0b4cd63c73d3b7527d44dac44, checked by the director at 7d2a8dedc. The node compared
the digest of its /dev/shm copy before running it. The sshproxy certificate is valid to 2026-11-11T04:15:08Z
(ssh-keygen -L, read locally).

BEFORE THE CONNECT
- cov2d_fence.sh from the Mac, rc 0 at 05:12:21Z: "FENCE: no cov2d-* job queued or running" (fence-mac.out).
- Login survey (survey.txt): login27 had the lowest load, 4.97. The launcher goes through saul.nersc.gov, which placed
  the connect on login40, the seventh most loaded of the 37 surveyed (246.69 on 244 CPUs). The read took 5 s at nice 19; a
  later connect should target the surveyed node.

THE CONNECT (o1.out; o1.err is empty). ssh rc 0, read unpiped.
- 70 products listed. Each sha256 equals its committed line in fd/receipts-stab-a1r/full/SHA256SUMS: 70 OK.
- stat before and after: all 70 byte-identical, atime included.
- The bundle: 210 arrays (xsec_flat, xtrue_flat for the 18 closures, meta), 12,909,680 bytes, sha256 8199bd26...
  Read rc 0.
- Nothing was written on the cluster beyond deleting the connect's own /dev/shm copy.
- In the committed o1.out, the base64 block is replaced by a one-line note giving the bundle's sha256 and the full
  stdout's. The bundle stays outside the repository (the director's ruling).

THE MAC SIDE
- bv96_power_derive.py, rc 0 (derive.out), run on the full stdout rebuilt from the bundle (its sha256 equals the
  received stdout's, 697270c1...): the decoded bundle's sha256 equals the node's.
  - Its controls reproduce the committed fd_stab.json: sd51 median 0.5813263504 and maximum 2.5152797815, both within
    1e-9 relative; cell_sd within 4.7e-9 of cell_sd.control, which is rounded to 1e-8.
  - The determinism pair (nominal, A7_mnvtune) is bitwise equal.
  - It wrote ../bv96_power_inputs.json.
- bv96_power_sim.py, seed 20261110, 2,000 replications, rc 0: ../bv96_power_sim.out.txt.

FILES: README.txt, fence-mac.out (and .err), survey.txt (and .err), o1.out, o1.err, derive.out. Digests: SHA256SUMS.txt.
