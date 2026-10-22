# Reverse outline, before (origin/main b603f9cf)

One sentence per printed paragraph. Ids are used in `ledger.md` and `changes.md`.

## app_release.tex (App. G, "Result package and reproduction limits", 1,495 words of source)

- **R0** Intro: rebuilding the PDFs reproduces no result; the internal records hold the digests; the appendix
  distinguishes the local replay package from the broader release, names fixed identities and the reproduction limits.
- **R0h** PROTECTED: the deposit snapshot hold (code paths in G and H refer to the deposited snapshot).
- **R1** Release status: RC7 exists with README, checksums, verifier; [PROTECTED: own verifier reproduces every
  recorded value and checked figure number]; the 16 MB package reproduces the joint-test p values, decisions,
  robustness, power, lost-seed resolution (a), coarse projections, L2 ratios, and regenerates three figure sets;
  RC7 predates the LightGBM change so its 2D curve is exact-split, the article's 2D figure was regenerated separately;
  not deposited or tagged; the schema is a specification, not a claim about RC7; fixed identities do not qualify.
- **R2** (scope) The public ancillary files supply the published inputs for the comparisons to Ref. MINERvA:2021owq.
- **R3** They do not reproduce the 2D uncertainty; RC7 replays the higher-dimensional inference from sufficient inputs
  but not extraction, event-level unfolding, closure/bias/covariance-status, the 2D uncertainty and coverage figures,
  low-recoil comparisons, recoil response, proxy rate; the multiplier scan is recomputable but not in RC7's own
  verification; products archived (2.3 GB); an earlier package version had an independent empty-directory replay;
  event processing needs the earlier AnaTuple production, event-loop outputs and generator samples.
- **R4** SHA256 for all 2,374 AnaTuples is "now" recorded; RC7 "still" carries names and sizes; the 2026-10-10
  record verifies copies of 1,885 data/flux/parameter files; 489 simulation AnaTuples hashed, not copied; internal
  preservation is not a public deposit and does not make the event-level analysis reproducible from the package.
- **R5** Schema lead: the broader package must contain every item; check marks point to bin edges and the records.
- **R6** Ten schema items (edges, ordering, central values, covariances, masks, M, generator predictions,
  provenance, worked example, four measurements); "adopted", "digest".
- **R7** Bin edges: the one thing a digest cannot give; five axes; catch bins; 19 unreported cells.
- **R8** Worked example lead ("Readers should be able to run ...") and six steps.
- **R9** Undeclared acceptance field: the receipt records UNDECLARED; must be retained "because a silent default
  would let the data format make a scientific choice" (P1N quote, META/BOOK).

## app_codebase.tex (App. H, "Codebase layout and terminology", 259 words of source)

- **C1** Four components "named in italics throughout the note" (event loop, omnifiles, driver, engine), with paths;
  backend list in code names (`exact`, `hist`).
- **C2** PET code supports future work, produces no result.
- **C3** Scripts call training-seed variation `seedscan`, "retaining the code name as provenance"; same variance
  source; the quoted block is built by the "2D closeout production rollup", not by `seedscan`.
- **C4** Code identifiers cited in the note: event loop file and trees, flux histogram; extraction function and
  `xsec_nd.py`; figure scripts.
