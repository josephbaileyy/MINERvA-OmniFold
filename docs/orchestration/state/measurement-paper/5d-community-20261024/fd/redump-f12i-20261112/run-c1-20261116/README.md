# RDX c1 at M_RDXC: STAGE 1 CHECKS PASS (receipt)

**By** session tier3-design, under the director's c1 go of 2026-11-16 (`../RDX-BINDING-1.md`, addendum J3, #1183 merged
at main `d09b2e06`). It is the rerun after the c1 STOP of 2026-11-15 (`../run-c1-20261115/`), with the fix of
`../code3/` (#1166, merged at M_RDXC `11e36cf1`).

## The run

c1 ran once on login27 at 19:35:36–19:36:28Z on 2026-11-16, pin M_RDXS `ad0535c4`. The job deploy stays at M_RDXS
(J3 ruling 1).

- **The launcher and connect** were taken by `git show` from M_RDXC `11e36cf1a5643ef6db2d480f3d345364d3247592`. Before
  the connect, `shasum -a 256` gave `602c728a7b4326f2…` and `eae946894be8ce02…`, J3's digests. On the node, the
  `/dev/shm` copy's sha256 was `eae946894be8ce02…` (`c1.session.txt:2, 4`).
- **Holds and fences:** no cov2d launch window was open. Their last cluster window, D2, ended at 09:45:04Z on
  2026-11-15, and the director stated that cov2d's current Fig. 1 work is laptop-only. `squeue --me` was empty (102-103).
- **Exit codes:** launcher rc 0, ssh rc 0, script rc 0 (`c1.session.txt:1, 233-234`).

`c1.session.txt` is the launcher's stdout byte for byte (sha256 `adf3fd45…`): ssh's rc line, then the session, then
the launcher's rc line. `c1.session.err.txt` is the ssh session's stderr, NERSC's login banner.

## What passed

| check | verdict | lines |
|---|---|---|
| the 15 purge-exposed MP-1 inputs, by stat only | PRESENT | 5-101 |
| `squeue --me` | empty | 102-103 |
| the policy check: c1's two reads, S0's `base_cv.root` and the pilot output, against the protected and never-read lists | CLEAR, no hits | 104-131 |
| `chkenv`: omnifold_py310's python 3.10.19, numpy 2.2.6, uproot 5.6.9 | imports pass | 132 |
| C-ALIGN-1A (`rdx_align.py`, mode rdx-equal): the staged `base_cv.root` against `runEventLoopOmniFold_RDX_1A.root` | PASS | 133-189 |
| C-TRUTHX (`rdx_truthx_rows.py`) on the pilot output | PASS | 190-204 |
| the walk probe (`rdx_probe_walk.py`, under `setup_salloc_env`) | PASS | 214-229 |
| the connect's summary | `C-ALIGN-1A rc=0 C-TRUTHX rc=0 walk probe rc=0`, `STAGE 1 CHECKS PASS` | 230-231 |

**What the checks recorded:**
- **C-ALIGN-1A:**
  - the four trees have equal entries in both files: data 360123, mc_background 52626, mc_signal_reco 2682267,
    mc_truth_denom 2682267;
  - the pilot output's only extra branches are the eight `truthx_*` branches, in mc_signal_reco and mc_truth_denom;
  - failures `[]`;
  - the reader is `omnifile_io.read_latest`, the highest TTree cycle. Its cycle lists are at 171-188.
- **C-TRUTHX:**
  - signal rows 2682267: miss 945434 and reco 1736833;
  - denom rows 2682267, matched 2682267, partnerless 0, matched miss 945434;
  - failures `[]`.
- **The walk probe:**
  - rows 2682267, kept 2682038;
  - `walks_bitwise_equal` true;
  - read 13.6 s, vectorized 0.6 s, loop 12.0 s;
  - peak RSS 3.94 GB;
  - the projection to the merged input: 175.0 s and 15.6 GB.
  - Lines 205-213 are ROOT's rootmap warnings (RooUnfold classes in two dictionaries), which come from loading the
    environment.

**The staging was not rerun.** `out/stage/base_cv.root` existed from the STOPped c1, so the connect's
`[ -e … ] || stage` line (`rdx_connect.sh:147`) skipped it. Its sha256 at that staging was `c76256a4…`, the connect's
`BASECV_SHA` (`../run-c1-20261115/README.md`). This run did not re-check it, which is the audit's low r1 (on the
follow-up list). C-ALIGN-1A then compared it with the pilot output and passed.

## Charge and state

- **Charge:** none. c1 runs on a login node and submits no job. RDX's total stays at 0.0704 of the 2.5 node-h cap.
- **Written on the cluster:** `out/checks/align_1A.json`, `out/checks/truthx_rows_1A.json` and
  `out/checks/walk_probe.json`. The session above prints their contents. s2 requires all three to record PASS
  (`rdx_connect.sh:160`).
- Nothing else changed. The pilot output and the staged copy were only read.

## Next

Per J1's order, the next step is gs2 and then s2, each on its own go.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** c1's STAGE 1 verdicts at M_RDXC (C-ALIGN-1A, C-TRUTHX, the walk probe), what they recorded, and the
  launcher and connect shas that ran.
- **Not citable for:** any RDX reading, any stage 2 or later verdict, or the staged copy's sha at this run (not
  re-checked: r1).
