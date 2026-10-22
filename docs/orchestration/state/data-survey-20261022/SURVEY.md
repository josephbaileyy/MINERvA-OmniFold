# MINERvA public release: a read-only survey for a second measurement and the newer FHC inputs (2026-10-22)

**By** the measurement session, at the director's request, for Joseph through the director. It proposes and does not
decide.
**Compute:** 0 node-h. No data or simulation file was downloaded. Every read is one of:
- the release's web pages;
- its 50 playlist file lists;
- `xrdfs ls -l` metadata (names, sizes, mtimes) from a Perlmutter login node;
- the 432-byte flux-area README;
- public MINERvA GitHub sources.

**CITABLE FOR:**
- the release's file counts, sizes and mtimes, as listed at 2026-10-22T21:44Z;
- our FHC anatuples against that listing, file by file, by size;
- what MAT's public code does for RHC;
- where our chain is FHC-specific.

**NOT CITABLE FOR:**
- byte identity beyond size: adler32 identity for the 448 1B–1P MC files is from 2026-10-14 (§2);
- the RHC tuples' branches: no RHC file was opened;
- anything inside the 2.6 GB flux-and-reweight tarball;
- the public files staying as they are;
- any physics effect or cost not marked as measured.

## 0. Answer

1. **Inventory.** The release as listed on 2026-10-22:
   - **ME FHC:** 12 playlists, 1,818 data and 489 MC files, 0.994 TB data and 10.706 TB MC.
   - **ME RHC:** 11 playlists, 1,085 data and 473 MC files, 0.490 TB data and 4.377 TB MC, 11.26 × 10²⁰ POT in
     data.
   - **Low energy:** "soon", and empty.
   - **Special MC:** FHC only, 5.12 TB.
   - **6F:** its MC has not been replaced since the vertex bug was found.
2. **The newer FHC release differs from our inputs in playlist 1A only.**
   - The other 11 playlists are identical by size, file for file: 448/448 MC and 1,565/1,565 data.
   - 1A has the same 41 MC and 253 data file names, at 1.244× and 1.056× the size. It is a reprocessing, not new
     events.
   - Switching therefore means re-downloading 0.964 TB and re-making every product, 2D benchmark included, for a
     change confined to 1A.
3. **RHC is supported by MAT,** but our chain needs:
   - inputs we do not have: per-playlist RHC flux files, antineutrino RPA tables and RHC kinematic renormalization;
   - about 80 lines of code changes;
   - new antineutrino generator samples for GENIE, NuWro and GiBUU;
   - and above all a new validation of the method, in a sample with a different hadronic system (neutron-led) and
     larger wrong-sign and hydrogen components.
4. **Storage does not fit as it stands.**
   - Scratch holds 16.95 of 20.00 TiB, leaving 3.05 TiB free. RHC in full is 4.43 TiB.
   - Staging one playlist at a time fits: the largest is 6A at 0.58 TiB.
   - The 8-week purge rule sets the pace.
5. **Recommendation** (§5):
   - Keep the FHC inputs. If a switch is wanted, do it once, after the release's announced late-2026 fixes.
   - Treat RHC as a second measurement once a method is validated, and after 6F is fixed.
   - Three cheap read-only steps would remove the main unknowns.

## 1. Inventory of the current release

The source is `getdata` and its linked pages, fetched 2026-10-22 at 14:42 PDT. The file counts come from the 50
playlist lists, and the sizes and mtimes from `xrdfs ls -l -R` on
`root://fndcadoor.fnal.gov:1095//pnfs/fnal.gov/usr/minerva/persistent/OpenData`. All 50 lists match their directories
name for name. GB = 10⁹ B.

**ME FHC (neutrino mode)**

| playlist | data POT (×10²⁰) | data files | data GB | MC files | MC GB | MC mtime | ours: same size as release |
|---|---:|---:|---:|---:|---:|---|---|
| 1A | 0.9 | 253 | 85.1 | 41 | 879.3 | 2026-01-06 | data 0/253, MC 0/41 |
| 1B | 0.19 | 47 | 17.9 | 11 | 237.6 | 2026-01-06 | data 47/47, MC 11/11 |
| 1C | 0.43 | 102 | 41.0 | 21 | 454.3 | 2026-01-08 | data 102/102, MC 21/21 |
| 1D | 1.4 | 283 | 136.8 | 61 | 1,319.0 | 2026-01-08 | data 283/283, MC 61/61 |
| 1E | 1.0 | 219 | 96.5 | 51 | 1,103.0 | 2026-01-09 | data 219/219, MC 51/51 |
| 1F | 1.7 | 260 | 154.1 | 71 | 1,515.3 | 2026-01-08…2026-01-09 | data 260/260, MC 71/71 |
| 1G | 1.4 | 233 | 129.0 | 61 | 1,273.0 | 2026-01-09 | data 233/233, MC 61/61 |
| 1L | 0.13 | 15 | 12.4 | 6 | 124.9 | 2026-01-09 | data 15/15, MC 6/6 |
| 1M | 2.1 | 202 | 147.0 | 98 | 1,927.9 | 2026-01-09 | data 202/202, MC 98/98 |
| 1N | 1.1 | 138 | 102.3 | 31 | 1,102.7 | 2025-12-18 (see note) | data 138/138, MC 31/31 |
| 1O | 0.3 | 26 | 28.0 | 16 | 331.1 | 2026-01-09 | data 26/26, MC 16/16 |
| 1P | 0.47 | 40 | 43.9 | 21 | 438.3 | 2026-01-11 | data 40/40, MC 21/21 |
| **ME FHC** | **11.12** | **1818** | **994.0** | **489** | **10,706.3** | | data 1565/1818, MC 448/489 |

**ME RHC (antineutrino mode)**

| playlist | data POT (×10²⁰) | data files | data GB | MC files | MC GB | MC GB per file | MC mtime |
|---|---:|---:|---:|---:|---:|---:|---|
| 5A | 0.55 | 79 | 23.6 | 22 | 190.7 | 8.7 | 2025-12-31 |
| 6A | 1.6 | 160 | 71.1 | 64 | 567.4 | 8.9 | 2025-12-18 |
| 6B | 1.0 | 102 | 44.9 | 42 | 369.8 | 8.8 | 2026-01-08 |
| 6C | 1.1 | 126 | 48.7 | 50 | 440.0 | 8.8 | 2026-01-08 |
| 6D | 1.2 | 95 | 50.9 | 46 | 399.5 | 8.7 | 2026-01-09 |
| 6E | 0.87 | 72 | 38.1 | 42 | 355.1 | 8.5 | 2026-01-09 |
| 6F | 1.4 | 117 | 61.0 | 32 | 546.8 | 17.1 | 2026-01-08…2026-01-09 |
| 6G | 0.74 | 63 | 32.3 | 42 | 368.5 | 8.8 | 2026-01-09 |
| 6H | 1.1 | 123 | 47.3 | 51 | 450.2 | 8.8 | 2026-01-09 |
| 6I | 0.79 | 72 | 33.8 | 41 | 348.8 | 8.5 | 2026-03-05 |
| 6J | 0.91 | 76 | 38.5 | 41 | 340.3 | 8.3 | 2026-03-04 |
| **ME RHC** | **11.26** | **1085** | **490.2** | **473** | **4,377.1** | | |

**Notes:**
- **6F:** "A bug in the Playlist 6F Standard Monte Carlo sample machine learning vertex predictions was found Apr. 2,
  2026. Please check back in the next few weeks following its discovery for it to be addressed."
  - No 6F MC file has an mtime after 2026-01-09, so nothing has been replaced in the 6.5 months since.
  - The 6F MC files average 17.1 GB (13.1–17.7 GB), against 8.3–8.9 GB per file in every other RHC playlist. That
    is unexplained here.
  - 6F data is not named in the bug.
- **6I** is also offered split into water-full (data 47, MC 24; 0.46 × 10²⁰) and water-empty (data 25, MC 17;
  0.33 × 10²⁰) lists. Together the split lists equal the 6I lists, as sets of file names.
- **1N MC** files are 33.5–36.1 GB, against about 21 GB elsewhere in FHC, and carry the 2025-12-18 mtime. The
  directory also holds a stray 3,230-byte `.nfs…` file, dated 2025-10-09, that is not in the list. Our 1N files are
  these same files.
- **Low energy:**
  - `LowEnergy_FHC/{Data,MC}` and `LowEnergy_RHC/{Data,MC}` exist, dated 2025-10-07, and are empty.
  - The page says LE "will also be provided soon".
  - The playlists page warns that LE "can't be mixed with Medium Energy (ME) data because the flux and other
    conditions are too different".
- **Special MC samples** are all FHC. The RHC directories exist but are empty.

  | sample | files | TB | statistics, as stated |
  |---|---:|---:|---|
  | Downstream calorimeters (no 1M) | 236 | 3.154 | about 4× data |
  | Extended 2p2h (Valencia to q3 = 2 GeV) | 44 | 1.031 | about 16× data |
  | Electron neutrino (no 1F) | 400 | 0.870 | about 4× data |
  | CC diffractive pion | 13 | 0.040 | about 30× data |
  | ν–e elastic | 13 | 0.020 | about 300× data |
  | NC diffractive pion | 13 | 0.006 | about 30× data |
  | CC coherent pion | 0 | — | "will be available in the future" |

- **Planned updates "later in 2026":**
  - more flux information in the tuples, with the note "Tutorial analysis flux usage does not rely on this";
  - a fix for "minor position-dependent bias in EM shower momentum reconstruction";
  - more consistent ML predictions, for the vertex in CC muon events and for EM-like cluster selection in π⁰
    reconstruction.

  The release expects these changes to be small, and they would change every tuple again.
- **Flux and parameter files** are a single dated tarball,
  `FluxAndReweightFiles_Tarred_Feb_20_2026_1145_FNALTime.tgz` (2,596,125,261 B). The README says updates are placed
  as "dated tarballs … often replacing the previous".
  - A GENIE-to-MINERvA tarball is also present: `genie2minerva-AL9-20261001.tar.gz` (506,528,985 B).
  - The ME flux page offers the FHC+RHC ν–e plus IMD-constrained fluxes, for all four flavours, with covariances. It
    calls this the flux "used for most Medium Energy antineutrino analyses".

## 2. Our FHC inputs against the current FHC release

Our inputs are recorded in `publication/release/preservation/anatuple-checksums/ANATUPLE-SHA256.tsv`: 2,307
anatuples, with sha256 and bytes. That manifest was compared to the 2026-10-22 listing, keyed by (MC or data,
playlist, file name) (`outputs/fhc_compare.json`, `scripts/compare_fhc.py`).

| | files | ours (B) | release (B) | same name | same size |
|---|---:|---:|---:|---:|---:|
| MC 1B–1P | 448 | 9,827,031,062,141 | 9,827,031,062,141 | 448 | **448** |
| MC 1A | 41 | 706,929,079,280 | 879,283,927,358 | 41 | 0 (ratio 1.244) |
| Data 1B–1P | 1,565 | 908,922,520,965 | 908,922,520,965 | 1,565 | **1,565** |
| Data 1A | 253 | 80,610,192,765 | 85,107,535,992 | 253 | 0 (ratio 1.056) |

- **Correction to the brief.** OI-55's "24% smaller files" is true of 1A only.
  - `state/2d-closeout/stageD-inputs/q2-opendata-20261014/REPORT.md` found this on 2026-10-14. 1A was downloaded
    on 2025-12-18, before the public 1A was reprocessed (2026-01-06/11). 1B–1P were downloaded on 2026-04-19/20,
    after it, and match the current release.
  - `state/2d-closeout/preservation-20261014/REPORT.md` found the 448 1B–1P MC files byte-identical by adler32.
  - This survey adds the size comparison for all 12 data playlists. The Q2 report compared three.
- **What differs in 1A,** from the Q2 report, which read both 1A versions on 2026-10-14:
  - the same events, reconstructed differently: `muon_P` = −9999 in 54,685 events against 0;
    `minos_trk_is_ok` 90,738 against 131,723;
  - 4,102 branches against 4,190;
  - most of the size growth (about 81%) is `mc_wgt_ppfx1_Total` and `mc_wgt_Flux_BeamFocus`, going from 100 to
    1,000 universes. Our chain does not read either (`q2-opendata-20261014/triage/REPORT.md:27-46`).
  - The triage verdict was "NO MATERIAL BIAS EXPECTED".
  - 1A is 0.897 × 10²⁰ of our 10.57 × 10²⁰ data POT, 8.5%.
- **Branches.** No new branch comparison was possible without opening files. The public branch documentation
  (`MinervaExpt/Tuple-Documentation`, last commit 2025-10-08, `da1087cc`) is a single table, `MAD_tuple_MainDoc`,
  of 256 rows (251 named branches). It does not distinguish productions.
- **What switching would cost:**
  - **Download:** 1A only, 0.964 TB (879.3 GB MC and 85.1 GB data). At the April download's rate, that is about
    2.5 h. The April MC finished 9.83 TB between 00:43Z on 04-19 and 01:29Z on 04-20, at most about 110 MB/s
    sustained.
  - **Storage:** +0.964 TB while the old 1A is kept, and the frozen products need it. The old 1A MC is the only copy
    of that processing: one copy on scratch, purge-eligible from 2026-12-09, and one sha256-verified copy on CFS
    (`preservation-20261014/cfs-copy-1A-mc/REPORT.md`).
  - **Compute:**
    - Every product that reads 1A is re-made. Every product pools all 12 playlists, so that is every product.
    - The event-loop layer costs about 5 CPU node-h for a set of 11 endpoints over 12 playlists, measured in the
      analogous MP1-A S1 (4.808 node-h, `../measurement-paper/phase1/LEDGER.tsv`).
    - The 2D benchmark's Stage C production alone charged 29.03 node-h
      (`../2d-closeout/stageC/production/REPORT.md:24`).
    - Stages A, B, D and E of the 2D closeout, the validation records and the note's numbers would all follow.
    - The compute is small. The record work, weeks of it, is the real cost.
  - **And it would happen twice** if the late-2026 fixes land, because they change every tuple.

## 3. RHC compatibility with our chain

Our sites are cited from `origin/main` `40a08681`, and spot-checked at `7ea30e3d`. MAT is cited from `MinervaExpt/MAT` `5d066e7a` (`PlotUtils/`) and
`MinervaExpt/MAT-MINERvA` `5bf46c53`. The MAT and MINERvA-101 headers are not vendored in this repo
(`.gitignore:59-82`), so their internals are read from GitHub.

| area | what changes | where | size |
|---|---|---|---|
| **Selection: muon charge** | the reco cut `minos_trk_qp < 0` (μ⁻) becomes the μ⁺ sign | `runEventLoopOmniFold.cpp:1715` (`reco::IsNeutrino`); diagnostics `intensity.py:105`, `triage/scripts/pair.py:54`, `probe.py:77` | 1 + 3 lines |
| **Signal definition** | truth ν̄_μ CC (`mc_incoming` = −14, μ⁺); the analysis PDG drives the flux and RPA weights | `runEventLoopOmniFold.cpp:1700,1717`, `runEventLoop.cpp:350`; `nd-unfolding/bkg_channel_split.py:14,22-26,115-122` | about 10 lines |
| **Flux** | MAT supports RHC: per-playlist `minervame5A`…`6J` names (`FluxReweighter.cxx:1979-2000`), a ν̄ flux branch, and the FHC+RHC+IMD constraint already on disk (`sorted_NuEConstraint_FHC_RHC_IMD.txt`). **We hold no RHC flux file**: our flux set is `flux-{g4numiv6,gen2thin}-pdg{±12,±14}-minervame{1D,1M,1N}` only | `util/GetFluxIntegral.cpp` (upstream); generator-flux code `gen5d_flux_reweight.py:64,66,234,289-290,302`, `make_flux_for_genie.py:22`, `gen5d_flux_supplement.py:733-734`, `combine_flux_MEFHC.py:28` | per-playlist RHC flux files, `flux-<version>-pdg<pdg>-minervame{5A…6J}[_rearrangedUniverses].root` (`FluxReweighter.cxx:933`), presumably in the tarball; about 10 lines |
| **Systematics universes** | MAT sets the horn current from the playlist (`MinervaUniverse.cxx:132-184`). The MINOS efficiency and its band take `isFHC()` (`MinosEfficiencySystematics.cxx:48-102`). RPA takes the analysis PDG (`MnvTuneSystematics.cxx:239-244`). Our 44 bands and 187 universes come from `GetStandardSystematics`, with no FHC flag of our own | `runEventLoopOmniFold.cpp:1785,1789` | 0 lines here; **inputs missing**: antineutrino RPA tables (we hold `outNievesRPAratio-nu*` only), RHC `Renorm_Kine_Truth_MinervaME5A…6J` (we hold ME1A–1P), and RHC MINOS-efficiency tables if they are file-based |
| **Backgrounds** | larger wrong-sign (ν_μ) and NC shares in RHC. ν̄ on hydrogen (ν̄p → μ⁺n) is part of the CH signal. The final state is neutron-led, so E_avail sees less of the hadronic energy | `bkg_channel_split.py` (wrong-sign = −14 today) | logic, about 8 lines, plus physics review |
| **Event loop and dumpers** | 52 py/sh files hard-code the 12 FHC playlists; the download path names `MediumEnergy_FHC`; `MEFHC` appears in 984 lines of 374 files (cosmetic) | e.g. `sbatch_evloop_array.sh:27`, `download_playlist.sh:5,25` | about 55 lines |
| **Generators** | antineutrino samples: GENIE `-p -14`, NuWro `beam_particle = -14`, GiBUU `process_ID = -2`. `gibuu_to_xsec3d.py:9` assumes μ⁻ | `run_gevgen.sh:42`, `run_nuwro.sh:28`, `run_gen5d_supplement.sh:59`, `mp3b_job.sh:54`, `mp3b_jobA.sh:57`, `gibuu_mefhc_numu.job:46` | about 7 lines, plus an RHC flux for each generator and new production runs |
| **Unchanged** | the fiducial volume and nucleon count, phase space, E_avail/q3/W code (handles ±PDG, `CVUniverse.h:262,273-274`), and POT accounting | | 0 |

**In total:** roughly 80 lines of code, three sets of parameter files, and new generator productions. The code is the
small part. The large part is re-validating the method on an antineutrino sample. MP-2's hold
(`DECISION-20261022-joseph-mp2-hold.md`) and the validation lane's scoping come first.

## 4. Storage plan ($PSCRATCH only; CFS stays closed)

Measured 2026-10-22 (`myquota`, `du`):

| | TiB |
|---|---:|
| scratch quota | 20.00 |
| used | 16.95 (84.8%) |
| `minerva/` (our FHC inputs) | 10.5 |
| `MINERvA-OmniFold/` (products) | 5.5 |
| everything else | about 0.9 |
| **free** | **3.05** |

| item | TiB | fits now? |
|---|---:|---|
| RHC data, all 11 | 0.446 | yes |
| RHC MC, all 11 | 3.981 | no |
| RHC MC without 6F (held for the fix) | 3.484 | no |
| largest single RHC playlist (6A, MC + data) | 0.581 | yes |
| new FHC 1A (MC + data), beside the old | 0.877 | yes |
| flux-and-reweight tarball | 0.0024 | yes |

**Staging order, if Joseph approves RHC.** No step is taken without approval.
1. **Parameter tarball first** (2.6 GB). Confirm the RHC flux, RPA and renormalization files exist.
2. **All RHC data** (0.45 TiB). It is small, and the 6F bug does not name data.
3. **MC one playlist at a time,** smallest first, beginning with 5A (0.19 TiB) as the debugging playlist. Run each
   playlist's event loops and keep the outputs. Delete its inputs only after the products are verified, recording each
   input's adler32 against the public value so it can be re-fetched exactly.
4. **6F last,** after the release replaces it.

Peak use stays under about 1.1 TiB: the data, plus one MC playlist, plus products. The products are small next to
the inputs: the whole of `measurement-paper/` is 176 GiB today.

**Purge risk.** NERSC: "assume that any file not accessed within 8 weeks may be purged at any time". Our records show
real purges on 2026-06-08 and 2026-08-03 (`preservation-20261014/REPORT.md:85-90`).
- Staged inputs should therefore be processed within about 2–3 weeks of download.
- Anything kept longer must be read within each 8-week window, or it is re-fetchable from the release.
- Products cannot be re-fetched. They need an HPSS copy once they are frozen. HPSS has 350.9 of 512 GiB used
  (`preservation-20261014/REPORT.md:70-71`).
- Streaming over xrootd (`root://`) would avoid staging, at the cost of wall time and network dependence. It is not
  measured here.

## 5. Recommendation and costs (for Joseph, through the director)

| option | download | storage now | compute | record work | recommendation |
|---|---:|---:|---|---|---|
| **A. Keep the FHC inputs** | 0 | 0 | 0 | 0 | **recommended** |
| B. Switch FHC to the current release now | 0.964 TB | +0.88 TiB | ≳ 35 node-h (event loops plus Stage C), plus Stages A, B, D, E | weeks: every 2D and measurement product and the note's numbers | not now: it affects 1A only, and would be repeated after the late-2026 fixes |
| C. Switch once, after the late-2026 release | all FHC, about 11.7 TB (unless sizes match again) | must free space first, or stream | as B | as B | the right time for a switch, if one is wanted |
| D. RHC as a second measurement | 4.87 TB, staged | about 1.1 TiB peak | event loops about 5 node-h per 11-endpoint set; generator productions not priced | a new validation of the method | after a validated method and after the 6F fix, as the director read it |

**Three read-only steps would remove the main unknowns.** Each is small and outside this brief, so each needs
approval:
1. **Fetch the 2.6 GB parameter tarball** (not data or MC) and list it, to confirm the RHC flux, RPA and
   renormalization files.
2. **Open one RHC MC file and one RHC data file over xrootd** and list their trees and branches, against the FHC
   branch set. This reads metadata only, megabytes.
3. **Re-list the release once a month,** with `scripts/release_inventory.py` over a fresh `xrdfs ls -l -R`, to catch
   the 6F fix and the late-2026 release.

## 6. Limits

- **Size is not identity.** Equal size is strong evidence only together with the 2026-10-14 adler32 result. That
  result covers the 448 MC files, not data.
- **mtimes are the release's.** That 6F MC has not been replaced is read from mtimes.
- **The RHC code-change estimates are line counts at cited sites.** The MAT and MINERvA-101 headers that are not
  vendored here were read upstream, not in the copy we build.
- **The FHC-switch compute is an order of magnitude from analogous ledgered work,** not a pricing.

## Evidence (`outputs/`, `scripts/`)

- `outputs/playlist-lists/`: the 50 playlist lists as served, with `_urls.txt`.
- `outputs/xrdfs/`: `ls_<area>.txt` (the six top-level areas), `listed_at_utc.txt` (2026-10-22T21:44:03Z), and
  `flux_README.txt`.
- `outputs/pages/`: the text of `getdata`, `opendata`, the five special-sample pages, `minerva-fluxes` and
  `minerva-playlists`.
- `outputs/release_inventory.json`, from `scripts/release_inventory.py`: per directory, counts, bytes, mtimes, and the
  list-against-directory check.
- `outputs/fhc_compare.json`, from `scripts/compare_fhc.py`: our manifest against the listing.
- `outputs/SHA256SUMS`: the checksums of all of the above.
- **Raw copies on the cluster:** `/pscratch/sd/j/josephrb/measurement-paper/data-survey/`.
