# RSN connect 1: the run of 2026-11-12 (receipt)

**By** session tier3-design, under the director's go of 2026-11-12. The go covered exactly `rsn_connect1.sh`
`4fbb8f29…` and `rsn_connect1_launch.sh` `f7cc3c80…`, as merged in #1088 at `02f9d648`, on one login node at 0 node-h.

**The result:** `CONNECT 1 PASS` (`connect1.session.txt:369`), rc 0 (`:370`). The login node was login27, and the run
went from 03:13:16Z to 03:14:01Z (`:4`, `:370`). The script was staged at its approved sha256 (`:2`).
- **Deploy:** `/pscratch/sd/j/josephrb/rsn-20261112/deploy`, at HEAD `af711298` (M_RSN), clean with untracked files
  included (`:10`). All nine §7 files were at their bound sha256s (`:11-19`), and the deploy was still clean afterwards
  (`:367`).
- **Staging:** the four NC-R inputs were staged into `$OUT/stage` by O_NOATIME copy (`:21-24`). Each copy's sha256
  equals its pin, and each source's size, mtime and atime were unchanged. **The director accepted this addition:**
  the bound code is unchanged, and only its argument paths point at byte-identical copies. The reason is AR23
  attempt 1's atime STOP on the flux file, an input of the LL5D gates. Both gate jobs, 61078463 and 61078506, were
  RUNNING (`:6-7`).
- **rsn_prep:** rc 0. G6's k is 1.201246, and **SM was built at radius 2** (`:26-27`). `prep.json`'s controls all
  hold: the frozen reweights are reproduced, the gate-or-cut share is reproduced, and G6 reproduces option ii. The
  sums list four reweights: G6/gibuu, and SM/genie_mec, SM/gibuu and SM/nuwro.
  - **`rsn-prep-SHA256SUMS`** has sha256 `13cf043e…` (`:29`). Every listed file matched, and every file but `prep.json`
    is listed.
  - **`prep.json`** has sha256 `db61ae8c…` (`:36`).
  - SM is built, so §6's job is **J2** (eight steps), not J2n.
- **NC-R:** rc 0, `NC-R PASS: 22 records reproduce the committed F1 readout` (`:336-337`). `nc_r.json` has sha256
  `e76aaa1e…` (`:338`). It reproduces control 7 as F1 had it: `pass` false, χ² 245.742, p 0.0.
- **Ruling 4 (r1):** the recorded, deployed and bound sha256s of `rsn_regrade.py` are all `661608d8…`
  (`:363-365`), so `R1 EQUAL`.
- **`fence.txt`** is absent (`:368`), and nothing was submitted.
- The environment was root_6_28's Python 3.11.14 with numpy 1.26.4 (`:8`).

**Files.**
- `connect1.session.txt` is the launcher's output, with every product printed in full. `connect1.session.err.txt`
  holds only NERSC's login banner.
- `rsn-prep-SHA256SUMS`, `prep.json` and `nc_r.json` were extracted from the session. Each is byte-equal to the
  sha256 printed beside it.
- **`nd-unfolding/rsn/rsn-prep-SHA256SUMS`** is the same bytes, at the path where `sbatch_rsn.sh` reads it, at the
  director's ruling. This PR's merge commit becomes **M_P1**, the pin for J2 and J3. J1 runs from the M_RSN deploy.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the deploy at M_RSN, the RSN reweights and their sums, prep.json's controls, and the NC-R PASS, as
  of 2026-11-12T03:14Z.
- **Not citable for:** any RSN reading. No unfold has run.
