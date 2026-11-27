# MinervaExpt upstream audit against our MAT pins (2026-11-24)

Lane: `minerva-lib`. Zero compute: read-only `gh api` calls against the public MinervaExpt repos, plus
reads of this repo at `origin/main` `b2fae8e2f`. The question, from Joseph: have any changes to the
MINERvA libraries been critical to our results?

**Verdict.** No upstream change since our pins touches our central values or our selection. One
change, MAT-MINERvA `3e411c0d`, alters how the three `GEANT_*` systematic bands are built. Its effect
on those bands is **NOT MEASURED**.

Raw evidence: `upstream-compare.txt`, produced by `capture.sh` (each command is echoed above its
output). Every hash below is copied from that file.

## 1. Pins

| Library | Pin | Committed | Where the pin is recorded |
|---|---|---|---|
| MAT | `35097b65ab1680db8058f9ede18fecffdc3a1ea3` | 2025-10-09 | `docs/orchestration/state/2d-closeout/stageB/REPORT.md:77`; `docs/orchestration/state/2d-closeout/c04-repair/review/VERIFICATION.md:10` |
| MAT-MINERvA | `50d7631416d1c93edd4db6886a2ca29da64fee60` | 2025-10-09 | `docs/orchestration/state/2d-closeout/stageB/REPORT.md:77`; `docs/orchestration/state/2d-closeout/stageF/methods/M4-W-RECORD.md:32` |
| MINERvA-101-Cross-Section | none: our copy is a modified local fork under `MINERvA101/MINERvA-101-Cross-Section/` | | |
| UnfoldUtils, GENIEXSecExtract | none recorded in this repo | | |

These pins were read from the cluster checkout by those records. This audit did not re-read the
cluster checkout. It did not measure which source the installed `libMAT.so` was built from either.
That row is still `NOT CHECKED` at `c04-repair/review/VERIFICATION.md:145`.

## 2. Compare ranges and every upstream commit

**MAT**, `35097b65ab1680db8058f9ede18fecffdc3a1ea3...main`: `status=ahead ahead_by=2 behind_by=0`.

| Commit | Date | Change | Effect on our results |
|---|---|---|---|
| `664055af46f448767d92e9e6fb6474032aef542d` | 2026-05-30 | updates `.rootlogon.C` | none: ROOT macro setup |
| `5d066e7a87086acc3ed4bf4f6695e604c9410b5f` | 2026-06-01 | adds PlotUtils to `$PYTHONPATH` | none: environment setup |

The 2026-11-20 push to MAT is on branch `alhart_CCInclusiveNuMuTargets` (`d75a2edc4c1a80c81139d9336b6c6ea216b96f00`),
not `main`. It was not examined further.

**MAT-MINERvA**, `50d7631416d1c93edd4db6886a2ca29da64fee60...main`: `status=ahead ahead_by=3 behind_by=0`.

| Commit | Date | Change | Effect on our results |
|---|---|---|---|
| `3e411c0d3a6f598aa2072c6729790e4701e4089d` | 2026-03-02 | GEANT hadron weights now also apply to truth events | **changes how 3 systematic bands are built**: §3 |
| `c20ad220e95f55b4ef2e9426c56dd2a3800f7533` | 2026-03-05 | `#include <cmath>` in 3 files, for ROOT 6.30+ | none: compile fix |
| `5bf46c535afaafb9328b7b2bff091ad90c87c479` | 2026-09-23 | new `weighters/ZExpansionReweighter.h` (+44), off unless used | none: we construct no such reweighter and set `SetZExpansionFaReweight(false)` (`MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp:1702`) |

**MINERvA-101-Cross-Section**, `main` commits since 2025-06-01 (there is no pin, so this is a date
window, not a compare range). Commits that touch analysis logic:

| Commit | Date | Change | Effect on our results |
|---|---|---|---|
| `48a52760b191b657a21b97faaa394d77767b16d1` | 2026-03-02 | `IsMinosMatchMuon()` changed from `has_interaction_vertex == 1` to `isMinosMatchTrack == 1` | none now: our fork has made the same match since 2026-04-25 (`MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h:107`) and adds the `minos_trk_is_ok == 1` bit. This is the "pre-MINOS-fix" issue of the old 1D outputs. |
| `85b3d5fe4f762ae8a43b4308af03bf6f49b8c10f` | 2026-02-20 | fills truth flux universes in `runEventLoop.cpp` when systematics are off | none: only that path changes, and we run with systematics on (`runEventLoopOmniFold.cpp:1789`) |

The other commits in the window change READMEs, playlists, file lists, CMake, plot labels and ROOT or
Python setup.

**UnfoldUtils**, `main` since 2025-06-01: `f9099cd3f446083055b151add7811afc193b8393` (CMake minimum)
and `a2bbe41ca914e1d9f196782c3d2b299163fcbf05` (AlmaLinux 9 merge). The range `f9099cd3...a2bbe41c`
changes `CMakeLists.txt` (+4 −4), `dict/UnfoldUtilsDict.{h,xml}` (+1 −1 each) and
`MinervaUnfold/MnvUnfold.cxx` (+2 −0). The commit message says it removes TUnfold references. Build-only.

**GENIEXSecExtract**, `main` since 2025-06-01: `3ecf9175af0baf7177a5e12cd92705acc2467d81` (CMake minimum)
and `0e679adc0669ffcf97a879b64584d37a92962f78` (TF1 functor compatibility with ROOT 6.40). Build-only.

## 3. The finding: `3e411c0d`, GEANT hadron truth weighting

**What upstream changed.** The commit comments out `if( T::IsTruth() ) return 1;` in
`GeantHadronUniverse<T>::GetGeantHadronWeight()` and `GeantHadronUniverse<T>::GetWeightRatioToCV()`
(`universes/GeantHadronSystematics.cxx`). It also comments out `if(univ.IsTruth()) return 1;` in
`weighters/GeantNeutronCVReweighter.h`. The upstream comment says the weight "should be applied to
the efficiency denominator to combat biasing from the reweight". It is dated 10/09/2024; the commit
was authored 2025-10-17 and merged 2026-03-02. The full patch is in `upstream-compare.txt`.

**What our pin does.** At `50d76314` the early returns are present. So the `GEANT_Neutron`,
`GEANT_Pion` and `GEANT_Proton` universes return weight ratio 1 for every truth-tree event. Our dump
fills truth-mode universe weights by calling `model.GetWeight` on the truth-tree universes with
`CVUniverse::SetTruth(true)` (`MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp:1221-1230`).
Those universes come from `GetStandardSystematics(options.m_truth)` (`runEventLoopOmniFold.cpp:1789`).
In our products, those three bands therefore vary the reco side and leave the efficiency denominator
at weight 1.

**Central value: unaffected.** Our MnvTune v1 model is built from `FluxAndCVReweighter`,
`GENIEReweighter`, `LowRecoil2p2hReweighter`, `MINOSEfficiencyReweighter` and `RPAReweighter`
(`MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp:1745-1750`). It contains no
`GeantNeutronCVReweighter`. Neither `GeantNeutronCV` nor `GeantHadron` appears anywhere in that file
(0 matches at `b2fae8e2f`). The CV weight therefore does not go through either changed code path.

**2D reproduction.** The 2021 paper predates the change, so our treatment of these bands matches the
one it would have used. This is an inference from the dates. The paper's code was not read.

**Effect on the three bands: NOT MEASURED.** The following is reasoning, not a measurement. Weighting
the denominator too cancels any change in the weight's overall size between numerator and denominator.
So under current upstream practice the three bands would most likely shrink, and ours would be
slightly conservative. Neither the direction nor the size has been computed.

**Scale, for context only.** The three bands are minor. In the PET lateral cross-check, `GEANT_Neutron`
(√tr 5.6e-40) is about 5 times below `MinosEfficiency` (2.7e-39) (`VALIDATION_LEDGER.md:1765`).
That is a different product, so this is not a statement about the 2D or 5D budgets.

**Not a candidate for the Tune v1 truth discrepancy.** That comparison is at truth level, and neither
side applies a GEANT weight there.

## 4. Status of the follow-ups

- Wording in the note or article: Joseph's, through the rewrite-helper lane. Not drafted here.
- Quantification: one event-loop pass with the three GEANT truth bands, built against MAT-MINERvA
  without the early return, then a re-projection of those bands. **NOT AUTHORIZED.** It needs a
  priced proposal to the director and a GO first.
