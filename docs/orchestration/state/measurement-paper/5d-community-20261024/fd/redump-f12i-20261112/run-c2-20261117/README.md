# RDX c2 at M_RDXD: STAGE 2 CHECKS PASS (receipt)

**By** session tier3-design, under the director's c2 go of 2026-11-17 (`../RDX-BINDING-1.md`, addendum J4, #1196 merged
at main `6b0bcc97`). It is the first c2 run, with the fix of `../code4/` (#1195, merged at M_RDXD `9a333f9f`).

## The run

c2 ran once on login27 at 02:02:59–02:06:41Z on 2026-11-17 (3 min 42 s), pin M_RDXS `ad0535c4`.

- **The launcher and connect** were taken by `git show` from M_RDXD `9a333f9f6ca9fb339bbb0734767109de217da5d2`. Before
  the connect, `shasum -a 256` gave `256003a1b997a57d…` and `52ad6a0edf92b4ed…`, J4's digests. On the node, the
  `/dev/shm` copy's sha256 was `52ad6a0edf92b4ed…` (`c2.session.txt:2, 4`).
- **Holds and fences:** cov2d had been idle since this lane's s2 end message, with no hold sent since. c2 submits no job,
  so no lane's fence is touched. `squeue --me` was empty (102-103).
- **Exit codes:** launcher rc 0, ssh rc 0, script rc 0 (1, 1164-1165).

`c2.session.txt` is the launcher's stdout byte for byte (sha256 `45a9a4dd…`). `c2.session.err.txt` is the ssh session's
stderr, NERSC's login banner.

## What passed

- **The prologue:** the 15 purge-exposed MP-1 inputs PRESENT, by stat only (5-101). `squeue --me` empty (102-103).
- **chkenv:** omnifold_py310's python 3.10.19, numpy 2.2.6, uproot 5.6.9 (104).
- **The policy check (l2):** CLEAR, with 0 hits over its 24 reads, the 12 MP-1 zero loops and the 12 RDX outputs
  (105-154).
- **Per playlist,** each in its own block of the session:
  - the pin read under CHKPY;
  - the O_NOATIME staging of MP-1's zero loop, STAGED;
  - C-ALIGN-PL, the staged zero loop against the RDX output: PASS, failures `[]`;
  - C-TRUTHX: PASS, failures `[]`.
- **The end:** `out/loops.sha256` was written with the 12 outputs' sha256 (1150-1161), then `STAGE 2 CHECKS PASS` (1162).

| PL | staged (bytes) | zero-loop sha256 = ZERO_LOOPS pin | C-ALIGN-PL: data / bkg / signal reco = truth denom | C-TRUTHX: miss + reco | reco = N_SIG | lines |
|---|---|---|---|---|---|---|
| 1A | 398375296 | `2745e38c…` yes | 360123 / 52626 / 2682267 | 945434 + 1736833 | yes | 155-237 |
| 1B | 106517598 | `a2b7e413…` yes | 75192 / 14182 / 721082 | 251998 + 469084 | yes | 238-320 |
| 1C | 204230889 | `7985c0f1…` yes | 173122 / 26898 / 1376832 | 482805 + 894027 | yes | 321-403 |
| 1D | 596287802 | `52da8f22…` yes | 580834 / 78987 / 4003632 | 1408544 + 2595088 | yes | 404-486 |
| 1E | 495761736 | `7f9293a6…` yes | 408075 / 66077 / 3350021 | 1184467 + 2165554 | yes | 487-569 |
| 1F | 689044069 | `7481c947…` yes | 642737 / 92219 / 4660210 | 1740511 + 2919699 | yes | 570-652 |
| 1G | 581501093 | `259aa195…` yes | 538406 / 76742 / 3922748 | 1438551 + 2484197 | yes | 653-735 |
| 1L | 56587445 | `d2b4dafc…` yes | 49872 / 7820 / 383848 | 151725 + 232123 | yes | 736-817 |
| 1M | 862899975 | `f80bb016…` yes | 591031 / 120642 / 5917406 | 2333600 + 3583806 | yes | 818-900 |
| 1N | 499729347 | `9e9875ec…` yes | 415928 / 70774 / 3416266 | 1374033 + 2042233 | yes | 901-983 |
| 1O | 150945068 | `22064448…` yes | 110836 / 22038 / 1042088 | 448729 + 593359 | yes | 984-1066 |
| 1P | 199848958 | `5efe83f9…` yes | 173641 / 29222 / 1372703 | 590693 + 782010 | yes | 1067-1149 |

**How to read the table:**
- **The zero-loop column:** `rdx_paths.py stage` refuses unless the copy's sha256 is the pin, and each block says
  STAGED. Each printed sha256 also equals the ZERO_LOOPS entry of the deploy's `fd_ct_period_inputs.py` (checked
  against the committed module).
- **C-ALIGN-PL:** in every playlist the four trees have equal entries in the zero loop and the output. The only extra
  branches are the eight `truthx_*` branches, in mc_signal_reco and mc_truth_denom.
- **C-TRUTHX:** in every playlist, matched rows equal the denominator rows and partnerless rows are 0.
- **The N_SIG column:** each playlist's reco row count equals the per-playlist signal count `N_SIG` that
  `test_rdx_stages.py:35-36` pins from `proxy_hists_meta.json`.
- **1A's output sha256** in `loops.sha256` is `e042d191…`, the sha256 s1's job logged (`../run-c1-20261115/README.md`).

**p4, the aligns' memory:** the checkers print no RSS, so none is recorded here. The 12 aligns and row checks ran in
sequence on login27 inside the run's 3 min 42 s, and none failed.

## Charge and state

- **Charge:** none. c2 runs on the login node and submits no job. RDX's total stays at 0.8309 of the 2.5 node-h cap.
- **Written on the cluster:**
  - `out/stage/zero/`: the 12 zero-loop copies, 0444, 4,841,729,276 bytes in all;
  - `out/checks/align_<PL>_pl.json` and `truthx_rows_<PL>_pl.json`: 24 files;
  - `out/loops.sha256`, renamed from `checks/loops.sha256.partial`.
- c1's `checks/align_1A.json` and `truthx_rows_1A.json` are not c2's output names (l1), so c2 did not write them.
- MP-1's zero loops were read only by the O_NOATIME copy, which refuses if a source's size, mtime or atime moved.

## Next

Per J1's order, the next steps are gmerge, then m, then cm, each on its own go. m's go waits for this receipt to merge.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:**
  - c2's STAGE 2 verdicts at M_RDXD: C-ALIGN-PL and C-TRUTHX for all 12 playlists, and what they recorded;
  - `out/loops.sha256`'s 12 sha256s;
  - the launcher and connect shas that ran.
- **Not citable for:** any RDX reading, any merge or later verdict, or the aligns' memory (not recorded).
