# RDX gmerge and m: the merge gate, and the merge-and-dump job (receipt)

**By** session tier3-design, under the director's goes of 2026-11-17 (`../RDX-BINDING-1.md`, addendum J5, #1198 merged
at main `394438d0`). J5 ruled the merge limit at 0:45:00, from 5B's ALL-lane timings. One run each. Both steps used the
launcher and connect from M_RDXD `9a333f9f6ca9fb339bbb0734767109de217da5d2`, which were taken by `git show` and checked
by `shasum -a 256` before the connects: `256003a1b997a57d…` and `52ad6a0edf92b4ed…`, J4's digests. The pin was M_RDXS
`ad0535c4`.

`*.session.txt` is the launcher's stdout byte for byte. `*.session.err.txt` is the ssh session's stderr, NERSC's login
banner.

## gmerge: login27, 2026-11-17T02:37:55Z, rc 0

- **The checks:**
  - the `/dev/shm` copy was `52ad6a0edf92b4ed…` (`gmerge.session.txt:2, 4`);
  - the 15 purge-exposed MP-1 inputs were PRESENT, by stat only (5-101);
  - `squeue --me` was empty (102-103).
- **What it wrote:** `out/gates/merge.ok`, with the lines `pin=ad0535c4a62ac0a20711a4a00f2266ddaf926d7c`,
  `limit=0:45:00` and `utc=2026-11-17T02:37:55Z` (104-106). gmerge STOPs if the gate file is already there
  (`rdx_connect.sh:98` at M_RDXC, the same line at M_RDXD), and it exited rc 0, so this run created it.
- **Exit codes:** launcher, ssh and script all rc 0 (1, 107-109).
- **Charge:** none (no job).

## The holds, before m

- **cov2d acked before the m connect:** no cov2d cluster window was open or planned in the next ~3 h. Their fences
  refuse every `rdx_` job other than `rdx_s1_1A`. cov2d said they will ask for this lane's end message before any new
  cluster work.
- **FYIs** on `rdx_s2_merge` went to director-helper-2 and limitation-resolver.

## m: login27, 02:38:24–02:38:36Z, rc 0

- **The prologue:**
  - the `/dev/shm` copy was `52ad6a0edf92b4ed…` (`m.session.txt:2, 4`);
  - the 15 inputs were PRESENT (5-101);
  - `squeue --me` was empty (102-103).
- **The connect's requirements** passed, since it STOPs on each: `out/loops.sha256` is non-empty (c2's, 2026-11-17), and
  `gates/merge.ok` names the pin and `limit=0:45:00`.
- **The policy check:** CLEAR, with 0 hits, over MP-1's `lat_zero.npz`, `lat_zero_bkg.npz` and `out/evloop` (104-131).
- **chkenv:** omnifold_py310's python 3.10.19, numpy 2.2.6, uproot 5.6.9 (133). MP1_ZERO's two pins were then read
  under CHKPY.
- **The staging, by O_NOATIME:** each copy's sha256 must equal its pin. The copy refuses if the source's size, mtime or
  atime moved, and never overwrites.

  | file | bytes | sha256 = MP1_ZERO pin | lines |
  |---|---|---|---|
  | `lat_zero.npz` | 1,548,311,762 | `6ca02c3d…` yes | 134-143 |
  | `lat_zero_bkg.npz` | 28,494,557 | `f09727d0…` yes | 144-154 |
- **The merge launcher's smoke:** checks passed, 4 steps: merge, nndump, dump and k1 (156-160).
- **The fence** was clear, and the cap gate passed: spent 0.8309, held 0, the merge's ceiling 0.75 (exclusive, one node,
  0:45:00), total 1.5809 of 2.5 (161).
- **The submit:** `SUBMIT id=61443055 name=rdx_s2_merge limit=0:45:00 utc=2026-11-17T02:38:36Z`, PENDING in QOS
  regular_1 (162-164).
- **Exit codes:** launcher, ssh and script all rc 0 (1, 165-167).

## The job's outcome

To be added from sacct over 61443055 when it ends. The watch reads sacct only, never squeue.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:**
  - the merge gate's contents;
  - m's pre-submit checks and staging;
  - the job id, its limit and the cap gate's total;
  - the launcher and connect shas that ran.
- **Not citable for:** the job's outcome (recorded in a later commit), any K1 or C-TRUTHX-NPZ verdict (cm's, under its
  own go), or any RDX reading.
