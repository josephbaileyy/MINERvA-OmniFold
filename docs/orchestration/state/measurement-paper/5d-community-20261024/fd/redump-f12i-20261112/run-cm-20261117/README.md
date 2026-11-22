# RDX cm at M_RDXD: MERGE CHECKS PASS (receipt)

**By** session tier3-design, under the director's cm go of 2026-11-17 (`../RDX-BINDING-1.md`, addendum J5, ruling 3).
One run.

## The run

cm ran on login27 at 05:06:59–05:08:48Z on 2026-11-17, pin M_RDXS `ad0535c4`.
- **The launcher and connect** were taken by `git show` from M_RDXD `9a333f9f6ca9fb339bbb0734767109de217da5d2`, and
  `shasum -a 256` gave `256003a1b997a57d…` and `52ad6a0edf92b4ed…` before the connect, J4's kit.
- **Holds and fences:** cov2d was idle with no hold sent since this lane's m end message. cm submits no job.
- **Exit codes:** launcher, ssh and script all rc 0 (`cm.session.txt:1, 291-292`).

`cm.session.txt` is the launcher's stdout byte for byte (sha256 `c510a6a0…`). `cm.session.err.txt` is the ssh session's
stderr, NERSC's login banner.

## What passed

- **The prologue:** the 15 MP-1 inputs PRESENT, by stat only (6-101). `squeue --me` empty (102-103).
- **k1.json** records `"verdict": "PASS"`. The connect STOPs otherwise, and it went on.
- **chkenv:** omnifold_py310's python 3.10.19, numpy 2.2.6, uproot 5.6.9 (104).
- **C-TRUTHX-NPZ** (`rdx_truthx_npz.py`): PASS, failures `[]` (105-285).
  - It covered 32,846,302 MCgen rows. In every one of the 12 playlists, the rows equal the joined rows, and 0 rows
    differ in MC, MC_pz, w_truth or any of the five truthx doubles.
  - pot_scale is 0.21240500334472884.
  - The npz's sha256 is `6ca02c3d…` and the sidecar's is `641ba34c…`.
  - The npz loads written by the job's python, under numpy 2.2.6, ran without a COULD_NOT_CHECK.
- **The three dumps' sha256,** as cm printed them (286-288). These are the lines for `rdx-inputs-SHA256SUMS`:

```
6ca02c3d8b09dfd168b5184c03d433a7bd65749f5f6fc4cefecdbed7b6ce052f  ./lat_RDX_ALL.npz
0e005fb11ccb9addf00a3b88096ada1084fc6ecab3db57c47cf6abec2b195ce3  ./lat_RDX_ALL_bkg.npz
641ba34c5ebde6d1881c705b862fab144a6fbb8a58ef3d84e59f1c8ba030a79e  ./truthx_RDX_ALL.npz
```

- **MERGE CHECKS PASS** (289).

**Against MP-1's pins:**
- `lat_RDX_ALL.npz`'s sha256 equals MP-1's `lat_zero.npz` pin (`6ca02c3d…`, staged at m), so the two files are
  byte-identical.
- `lat_RDX_ALL_bkg.npz` (`0e005fb1…`) differs in bytes from MP-1's `lat_zero_bkg.npz` pin (`f09727d0…`). K1 gates key
  equality and only records byte equality (`rdx_merge.py:14-15` at `ad0535c4`), and K1 passed. This receipt does not
  read `k1.json`'s per-key record.

## Charge and state

- **Charge:** none. cm runs on the login node with no job. RDX's total stays at 1.1492 of the 2.5 node-h cap.
- **Written:** `out/checks/truthx_npz.json`.

## Next

Per J1: the commit of `nd-unfolding/rdx/rdx-inputs-SHA256SUMS` from the three lines above, then gs3a and gs3b, then
s3a and s3b. Each takes its own go.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:**
  - cm's C-TRUTHX-NPZ verdict and counts;
  - the three dumps' sha256;
  - the launcher and connect shas that ran.
- **Not citable for:** any RDX reading or stage 3 verdict, or K1's per-key detail (not read here).
