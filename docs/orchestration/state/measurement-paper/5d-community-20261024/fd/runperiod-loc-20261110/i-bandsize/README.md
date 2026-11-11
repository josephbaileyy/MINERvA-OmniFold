# RPL (i) the band's size, MC only: σ_band measured (2026-11-11)

**By** the valid-region lane (director-helper-2), for the director, under
[`RPL-BINDING-1.md`](../RPL-BINDING-1.md) ruling 1 (the MC-only band-size read before P-RPD) and the director's GO of
2026-11-11 at exactly `rpl_band_launch.sh` `beedd94f`, `rpl_bandsize.sh` `b13c9437` and `cov2d_fence.sh` `16a2a5cd`.

**limitation-resolver's condition is kept** (`RPL-DECLARATION.md`: "the band sizes are not printed beside, or compared
with, any per-playlist data step until P-RPD holds"). This record holds MC numbers only. It prints no data step, and
check (i)'s fit and outcome (SCALE-WITHIN-BAND and the others) are not formed here.

## What ran

- **The survey** at 2026-11-11T02:22:04Z (`connect/login-survey.txt`) chose login27 (loadavg 12.83 on 244 cores).
- **The fence**, `connect/cov2d_fence.sh` (`16a2a5cd…`), on login27 at 02:22:30Z: no cov2d or t2a job queued; 28
  cov2d/t2a sacct rows in 14 days, none unended; `FENCE CLEAR` (`connect/fence.session.txt`).
- **The read**, `connect/rpl_bandsize.sh` (sha256
  `b13c9437280f0e06a6f51a95fd646b8f986261a678d94fdce26f10e58caa463a`), launched by `connect/rpl_band_launch.sh`
  (`beedd94f…`) on login27, staged at that sha (`connect/bandsize.session.txt`). It ran foreground on the login node
  at nice 19 with threads 1, 0 node-h.
  - 02:22:44Z to 02:23:06Z (`cluster/bandsize.log.txt:1,19`), `BANDSIZE OK []` (`:16`), rc 0.
  - Python: `omnifold_py310`, Python 3.10.19, uproot 5.6.9, numpy 2.2.6 (`:3`). It did not exit 4 (NO-UPROOT).
  - The cluster's copy, `cluster/rpl_bandsize.cluster-copy.sh`, is byte-identical to the approved script (`cmp`), and
    the log records the same sha256 (`:2`).
- **The fetch** (`connect/fetch.session.txt`): scp rc 0; `post.tar.gz`
  `84e9bfb13482b6f1777dbb86bdf10f56ddc90140ebc18406daaf67b2a2a24057`, `bandsize.log` `9a4c46dd…`. It was unpacked into
  an empty directory and read with `python3 -I`. `cluster/band.json` (sha256
  `9ae255fec5c3b8e394982b832160beed946e814e106d70ddf9e59875908ed771`, equal to the cluster's own line,
  `cluster/bandsize.log.txt:17`) is the file from the archive.

## The inputs

- **The files:** the 12 per-playlist universe files
  `/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_<PL>_universes_full.root`.
- **How they were read:** O_NOATIME, through uproot over the O_NOATIME file object. Size, mtime and atime are
  unchanged for all 12 (`stat_unchanged` true in `cluster/band.json`).
- **The rows:** the first 500,000 `mc_signal_reco` entries of each, in file order (not a random draw, as declared).
  1L has only 383,848, so all of them were read; 5,883,848 rows in all.
- **The selection:** rows passing `sim_pass` with finite, positive p and finite weight. `sim_pass` is the universe
  files' name for the declaration's `pass_reco`.

## The result (`cluster/band.json` `sigma_band`)

σ_band is the `w_reco`-weighted median of |p_μ,shifted / p_μ − 1|, pooled over both ±1σ endpoints and all 12
playlists, with p = √(p_T² + p_∥²) from `sim` / `sim_pz`. It is computed over 9,895,766 row-endpoints per band.

| band | role (`RPL-DECLARATION.md`, recheck R1, audit m2) | overall | p_∥ < 8 GeV/c | p_∥ ≥ 8 GeV/c |
|---|---|---:|---:|---:|
| `Muon_Energy_MINOS` | **deciding (overall)** | **0.008482** | 0.007880 | 0.010264 |
| `Muon_Energy_MINERvA` | descriptive only | 0.006195 | 0.006788 | 0.002641 |

- **Full precision** is in `cluster/band.json`: MINOS overall `0.008482265633139363`, and MINERvA overall
  `0.006195481709967088`.
- **Per playlist (MC, descriptive):** the MINOS median runs from 0.008443 (1B) to 0.008539 (1M), and MINERvA's from
  0.006131 (1M) to 0.006243 (1B, 1C).
  - Within each band and playlist, the −1σ and +1σ endpoints give the same median to six figures.
  - The per-playlist values are in `cluster/band.json` `files.<PL>`.
- **The p_∥ strata are descriptions.** Only the overall MINOS value enters (i)'s outcomes, after P-RPD.

## MAT-MINERvA's source of the shifts (`matsrc/`)

**The quote the declaration asks for** (`RPL-DECLARATION.md` inputs row "(i) the band's size") was made under the
director's GO of 2026-11-11, at exactly `rpl_matsrc.sh` `a35c07f0` and `rpl_mat_launch.sh` `2f595e6b`.
- **The run:** login27, 2026-11-11T02:37:03Z, `MATSRC OK []`, rc 0 (`matsrc/matsrc.log.txt`).
  - The cluster's copy of the script is byte-identical to the approved one.
  - The fetch's `post.tar.gz` is `721e0446…` (`matsrc/fetch.session.txt`).
- **The one file read:**
  `/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/MAT-MINERvA/universes/MuonSystematics.cxx`.
  - 9,150 bytes, sha256 `85780aeed6ce8af2b033f2c78d475fc39ed3c8c530d39b804140da96264143af`.
  - It was read by O_NOATIME with stat unchanged (`matsrc/matsrc.json`).
- **The checkout's commit:** `50d7631416d1c93edd4db6886a2ca29da64fee60`, from `.git/HEAD` (`ref: refs/heads/main`)
  and `.git/refs/heads/main`, both read the same way. No git command ran.
- **The full file, line-numbered:** `matsrc/MuonSystematics.cxx.numbered.txt`. Below, `MuonSystematics.cxx` means
  that file at sha256 `85780aee…`.

**What that file shows:**
- **The bands' members.** `Muon_Energy_MINOS` holds `MuonUniverseMinos` at nsigma −1 and +1 (`MuonSystematics.cxx:50-51`).
  `Muon_Energy_MINERvA` holds `MuonUniverseMinerva` at −1 and +1 (`:26-27`).
- **The MINOS shift** (`GetMuonMomentumShiftMinos`, `:121-152`):
  - It is applied to the MINOS component of the muon momentum, `GetPmuMinos` (`:134`, `:155-160`), not to the total.
  - The range term is `minosCVMomentum*NSFDefaults::MinosMuonPRange_Err` (`:136`).
  - A curvature term is added in quadrature only when `<AnaTool>_minos_used_curvature` is true (`:130-131`,
    `:140-147`). It is `NSFDefaults::MinosMuonHighPCurvature_Err` when `minosCVMomentum` exceeds 1000 (in `GetPmuMinos`'s units, which this file does
    not state) and
    `NSFDefaults::MinosMuonLowPCurvature_Err` below (`:141`).
  - The shift is `m_nsigma` × that quadrature sum (`:149`).
- **The MINERvA shift** (`GetMuonMomentumShiftMinerva`, `:68-95`):
  - It is the quadrature sum of `NSFDefaults::dEdxUncertainty` and `NSFDefaults::MaterialAssayUncertainty`, or their
    `NoNuke` values outside the nuclear targets (`:80-90`).
  - It is applied to the MINERvA component, `GetPmuMinerva` (`:98-103`).
- **The MINOS band's flux weight.** The band also carries a flux-weight change in ME playlists
  (`GetFluxAndCVWeight` `:163-186`, `GetWeightRatioToCV` `:189-204`, via `GetSysUniFluxWeightCorrection` `:184`,
  `:202`). σ_band measures only the lateral shift.

**The magnitudes are not in this file.** The five `NSFDefaults::` constants are defined elsewhere in MAT-MINERvA.
Under the GO's terms ("If the magnitude is defined in another file, say so and stop; a second file needs its own go"),
they are not quoted here.
- So the quote stands as **the construction** only: which component, which flag and which terms.
- It does not give the error values.

## Not done here

- **The `NSFDefaults::` values** behind the shifts, which live in a second MAT file. Reading it needs its own go.
- **Check (i)'s scale fit α̂ ± σ_α,** and the published 1 % muon-energy scale placed beside σ_band. These wait for
  P-RPD.

## Licence

**CITABLE FOR:** the size of the Muon_Energy_MINOS and Muon_Energy_MINERvA ±1σ fractional muon-momentum shifts in our
MC (the weighted median over the read rows, overall and in the two p_∥ strata), as the comparator check (i) declares;
and how MAT-MINERvA builds those shifts, at `MuonSystematics.cxx` sha256 `85780aee…`, checkout commit `50d76314`.

**NOT CITABLE FOR:**
- any statement about the data, or about the per-playlist data step;
- check (i)'s outcome, or whether a per-period scale lies within the band;
- that the band covers or explains the step (the band shifts every playlist alike: `RPL-DECLARATION.md`, audit M3);
- a random-sample estimate over the whole MC (the rows are the first in file order);
- the universe files' integrity (no digest was taken);
- the values of the `NSFDefaults::` error constants (not read).

Nothing is submitted, deposited or tagged.
