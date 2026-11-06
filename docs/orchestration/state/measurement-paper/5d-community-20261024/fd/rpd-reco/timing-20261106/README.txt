RPD-RECO login measurements, 2026-11-06 (the director's request): the run environment, uproot's read of the MAT histogram
classes, and the timing record for fd_rpd_reco.py's --timing-record. Run by limitation-resolver on login04 at 0 node-h,
with OMP/MKL/OPENBLAS/NUMEXPR/VECLIB = 1 and nice 19. No job ran, and no declared RPD-RECO input or COV2D input was
opened. fd_rpd_reco.py was imported at #848's head 10731ed3 (blob 51c40c7e) and never run as a program. Full sha256 of
each file: SHA256SUMS.txt.

THE TIMING RECORD: timing.json, sha256 303850f72136ca1a6090d6537c406e08a85484f1ff8315ebd46eb4772765f097, in the schema the
director approved. seconds_per_draw = 3.879e-7 is S, from one real-size chunk of fd_rpd_reco.aggregate itself at the
full real-pass shape (kind "signal", bins given, no partition). That shape is 65,536 rows; 201 replica passes, of which 200
draw and replica 0 is nominal; 5 weight variants; and every axis, for 23,115 bincounts per chunk. The arrays are
synthetic, in the real shapes.
- S is the marginal chunk: (min of 5 two-chunk calls - min of 5 one-chunk calls) / (200 x 65,536), so the fixed
  per-sample setup (the 200 SeedSequence generators) cancels and the per-row work (energy statistics, axis assignment,
  flux ratios) stays in. The one-chunk call including setup gives 3.796e-7.
- THE AXES DIFFER FROM THE REQUEST'S COUNT (21): the code at 10731ed3 has 23 real-pass axes (fd_rpd_reco.py:1029-1071,
  axis_assignments). They are step; pz, pmu, theta, pt, eavail, q3, W; cells; the 12 conditional
  {eavail, q3, W}@{0,1,2,3}; and rate@0, rate@1. The record follows the code. bootstrap_replicas is 200 drawing replicas;
  the loop also runs replica 0 (np.ones) through the same bincounts (:1185-1190).
- Informational, not in the record: the data kind at the same full shape (23 axes, 1 weight) costs 1.069e-7 per draw.
  The raw draws alone, numpy.random.default_rng(SeedSequence([20261104, 11, r + 1])).poisson(1, 65536) for r = 0..199 as
  aggregate makes them (:1093-1095, :1189), are PCG64 at a min of 27.06 ns per draw. (coverage-5b-audit measured 31.3 ns
  under /usr/bin/python3, numpy 1.17.3.)
- Planning, draws x S x 1.5. The rows are the 12 playlists' MC signal rows, 32,846,302, and the measured rows, 4,091,707,
  both from RPD job A's logs (receipts-rpd/run/jobA, "MCgen(...)", "measured(...)"). The latter equals the code's
  data_rows_estimate. Background rows are not in those logs, so these figures are lower bounds.
    d2-predict   200 x MC                 = 6.57e9 draws   -> 1.06 h
    c0           200 x 21 x (MC + data)   = 1.551e11 draws -> 25.08 h   ABOVE 11 h
    total, as runtime_estimate counts it  = 1.617e11 draws -> 26.14 h
  The full-shape S overstates c0's 20 partition passes, which run 11 axes and one variant (:1124-1129, :1199). That
  lighter shape was not timed here.

THE ENVIRONMENT: /global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python3, which resolves to
/global/u2/j/josephrb/.conda/envs/omnifold_py310/bin/python3.10. It has Python 3.10.19, numpy 2.2.6, scipy 1.15.3 and
uproot 5.6.9, and it is the only one with all three of the envs surveyed: every ~/.conda/envs/*, the NERSC Miniforge base
and /usr/bin/python3. root_6_28 has no uproot. /usr/bin/python3
(3.6.15, numpy 1.17.3) has no scipy or uproot. cernroot and the NERSC base env have no numpy.

UPROOT ON THE MAT CLASSES (uproot-run.out, uproot.json; probe-run.out, probe.json):
- TH1D: READS. runEventLoopMC_PB.root is the repository's committed copy (fd/receipts-ct/5b/flux/), staged from git, so
  there was no pscratch read. Its pTmu_reweightedflux_integrated, class TH1D, reads as Model_TH1D_v3 with 14 bins, edges
  0 .. 4.5. fd_rpd_reco.read_flux_histogram on it is ok. That file holds no MnvH1D.
- PlotUtils::MnvH1D: DOES NOT READ. flux_E_cvweighted, class PlotUtils::MnvH1D, in the MAT flux file
  flux-gen2thin-pdg-14-minervame1M_rearrangedUniverses.root fails at the object access itself, with "ValueError: need at
  least one array to concatenate". Neither the MnvH1D nor its TH1D base reads, and fd_rpd_reco.read_flux_histogram fails
  on it the same way. That file is the antineutrino flux of the declared family. It is not among the nine C-N candidates
  (all pdg 14), not a declared RPD-RECO input, and not read by the numu COV2D analysis. It was copied once per run by
  O_NOATIME (sha256 d9704aa4...), and its atime was unchanged across both runs (1792508612). FluxReweighter.cxx:944
  reads flux_E_cvweighted as an MnvH1D for every flux-file read (below), so the same failure is expected on the declared
  spectra. Not measured here.
- The first probe run (rpd_probe.py 20bf54e8, whose output is not kept) stopped on an AppleDouble ._ file that macOS tar
  had added. The kept run is rpd_probe.py 4cdda635, which skips dot-files. Its class test missed "PlotUtils::MnvH1D", so
  rpd_uproot_probe.py (176ccc8d) is the follow-up that measured that class.

MAT FluxReweighter (read by O_NOATIME, for Codex's config R1):
- Two checkouts, /pscratch/sd/j/josephrb/MINERvA101/MAT and /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/MAT, both
  at main 35097b65ab1680db8058f9ede18fecffdc3a1ea3 (origin https://github.com/MinervaExpt/MAT.git), with byte-identical
  PlotUtils/FluxReweighter.cxx (sha256 4576346db5e7a9e3673253bfc89f38bd2ca1dc260f24ebe66df055069990bbbc).
- File and histogram selection: FluxReweighter::GetFluxMnvH1D (FluxReweighter.cxx:883-945).
  - :907 sets the suffix "_rearrangedUniverses" for ME playlists when the nu-e constraint is applied.
  - :933-938 build the path "$PLOTUTILSROOT/data/flux/flux-<fluxVersion>-pdg<nuPDG>-<playlistString><suffix>.root".
  - :940 picks the histogram, "flux_E_cvweighted" (or "flux_E_unweighted" for the generated flux).
  - :944 reads it with GetMnvH1D.
- The playlist-to-file mapping is playlistString (:1938-1990): 1A-1F -> minervame1D; 1G, 1L, 1M -> minervame1M;
  1N-1P -> minervame1N.
- The per-playlist constructors (:42-187) give gen2thin and g4numiv6.
- Runtime evidence in records, though not from the RPD runs: the phase-1 MP1 event-loop checks
  (measurement-paper/phase1/mp1/receipts/checks/mp1s0_*_600176xx.out) print "FRW: this is the flux file I'm using:
  .../MINERvA-OmniFold/MINERvA101/opt/lib/data/flux/flux-gen2thin-pdg14-minervame1D_rearrangedUniverses.root" and its
  siblings. The RPD flux files (fd-rpd-20261103/flux/) were made from MINERvA101/Documents/baseline_flux, whose producing
  run's log is not in these records.

Files: the two staged copies the probes read: runEventLoopMC_PB.root (c64637d5, identical to fd/receipts-ct/5b/flux/'s)
and flux-gen2thin-pdg-14-minervame1M_rearrangedUniverses.root (d9704aa4, re-copied by O_NOATIME for this receipt, atime
1792508612 before and after); timing.json; rpd_probe.py (4cdda635), its wrapper rpd_probe_login.sh (a684240a), and its output probe-run.out and
probe.json; rpd_uproot_probe.py (176ccc8d), its wrapper rpd_uproot_login.sh (705d2618), and its output uproot-run.out and
uproot.json.
