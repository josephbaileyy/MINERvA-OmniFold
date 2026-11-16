# RDX s1: the 1A pilot submitted, job 61315648 (submit receipt)

**By** session tier3-design. This ran under the director's go of 2026-11-15 for `rdx_connect.sh` `11e7ef92…`,
`rdx_connect_launch.sh` `165fb98e…` and `sbatch_rdx_evloop.sh` `7ce210dc…` at M_RDXS `ad0535c4` (#1099; binding 1,
addendum J2). It was step s1 on login27, run once:

    bash rdx_connect_launch.sh <new empty dir> login27 s1 ad0535c4a62ac0a20711a4a00f2266ddaf926d7c 2026-11-15T02:21:21Z

The two scripts came from M_RDXS by `git show` into a scratch directory, and each re-hashed to its approved sha256
before the run. The connect staged on the node is `11e7ef92…` (`s1.session.txt:2`). The launcher, ssh and the script
each ended rc 0, with the step at 02:35:17–02:35:24Z (`s1.session.txt:1, 4, 140-141`).

## The go's terms

- **The fourth argument** is cov2d's LL5D atime-post UTC, from the LL5D readout on login25 (2026-11-15T02:21:21Z), the
  latest of cov2d's four, all SAME-SET-NONE-MOVED over the 1146 paths. The director confirmed it (cov2d's
  condition a). The step records it in `out/gates/ll5d_atime_post.txt`.
- **The price:** a ceiling of 0.088 node-h (2.25 h at the shared rate 0.0391 node-h per hour), accepted against the
  half-balance without a fresh probe. The last iris reading on main was 1238.8 node-h (2026-11-14T11:34Z, LL5D null's
  `connect.log.txt`), half 619.4. The lane's whole cap, 2.5 node-h, is 0.4% of that.
- **The overlap check** of s1's declared reads against cov2d's RE-2-shapes and xk re-run input sets, as cov2d gave them
  before either package was drafted:
  - the one shared input is the NuE constraint file, which both read and neither writes or atime-watches;
  - s1 reads no 2D partc-r2 or part B product, no rollup pin and no G2R product;
  - those two runs read no AnaTuple and nothing in `opt/lib`.
- **The director's ruling (ii):** cov2d's RE-2-shapes and xk connects may proceed while `rdx_s1_1A` runs, since there
  is no custody overlap. Their fences refuse every other `rdx_` job.
- **The announcements:** cov2d had the job family from the overlap check. One-line FYIs went to director-helper-2
  (E96D) and limitation-resolver (RPD flux1) before the submit.

## What passed (`s1.session.txt`)

- the 15 purge-exposed MP-1 inputs: PRESENT, by stat only (5-100). Their atimes are 2026-10-20 (`base_cv.root`) and
  2026-10-30 (the rest);
- the fence: `squeue --me` was empty (102-103);
- the policy check: CLEAR, with no hits. s1's four read paths (the two 1A manifests, `minerva_large_files` and the
  patched binary) hit none of prologue5's eight protected or RDX's eight never-read entries (104-132);
- the launcher's own smoke for 1A: 294 AnaTuples checked by size and mtime, none differing (134-135);
- the cap gate: spent 0, held 0, wanted 0.087975, total 0.087975 against the cap 2.5, a pass (136);
- the submit: **`rdx_s1_1A` = 61315648**, at 2026-11-15T02:35:22Z, PENDING, limit 2:15:00, QOS shared (137-139).

`s1.session.err.txt` is the ssh session's stderr, NERSC's login banner.

## Next

The job checks the fence again at start and immediately before the binary, and logs the NuE file's atime and mtime
before and after. When it ends, step c1 (the O_NOATIME copy of S0's `base_cv.root`, C-ALIGN-1A, C-TRUTHX and the
walk probe) runs on the director's go.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** s1's submit at M_RDXS: the job id, the checks that passed before it, the cap gate's numbers and the
  recorded LL5D atime-post time.
- **Not citable for:** the job's outcome, any check past s1 (C-ALIGN-1A, C-TRUTHX), or any reading.
