Local diagnostic of truth-vertex feed-in to the published-IBU comparison
26 November 2026

Inputs are from receipts/precharge-testC-run-20261126 at
411ac910e5f9913b49d120764033b0815c7b6339. This is an exploratory replay.
The recorded Test C criteria and results stand on their own.

From this directory, reproduce replay.txt and true_40_60.csv with
OPENBLAS_NUM_THREADS=1 python3 compare.py /path/to/receipt-checkout > replay.txt
The local run used Python 3.12 with NumPy, pandas and uproot.

The 2021 MINERvA comparison loop fills the selected 2D numerator in true muon
coordinates after isMCSelected and isSignal. The generated denominator calls
isEfficiencyDenom. The 2021 MAT helpers put true vertex, muon angle and minimum
longitudinal momentum in phase space and charged current and flavor in signal.
The v0 release reports agreement for CCQENu AnaTuples. The later tutorial also
shows selected signal filling its migration and the complementary background.
The primary publication describes angular feed-in in its Figure 5 efficiency.
These are evidence for a reproduction convention. Final-production histogram
parity has yet to be established.

https://github.com/MinervaExpt/MINERvA-101-Cross-Section/blob/bb6c1634d0aa2f1f3456c9a6be1fedb0492d6686/runEventLoop.cpp#L203-L232
https://github.com/MinervaExpt/MINERvA-101-Cross-Section/releases/tag/v0
https://github.com/MinervaExpt/MAT-MINERvA/blob/f790cc794/calculators/CCInclusiveSignal.h
https://github.com/MinervaExpt/MAT/blob/0111c79de/PlotUtils/Cutter.cxx
https://github.com/MinervaExpt/MINERvA-101-Cross-Section/blob/5fdc3f86cc86f4efe0d7740e1cd308d8651b7a0b/runEventLoop.cpp#L134-L158
https://arxiv.org/abs/2106.16210

The reproduction uses the released axes and the signed ten-iteration IBU.
The baseline reproduces the receipt's unfolded counts cell by cell. The
intervention moves selected negative-sign MC rows with a true vertex outside
the fiducial volume and an in-grid true muon from background to migration and
selected counts. Generated denominators, observed data and exposures stay
fixed. Each playlist has sufficient recorded background in each destination.
Total selected MC in each destination is conserved. Use the full-sample ratio
of summed POT to match the archived replay.

The three groups of rows in replay.txt are baseline, the change confined to
the true 40–60 GeV/c column, and the change extended to all in-grid true muons.
Each uses either the in-grid or the selected-anywhere efficiency numerator.
The added rows are restricted by the saved scan to reco longitudinal momentum
at least 20 GeV/c and reco transverse momentum below 4.5 GeV/c. The existing
in-grid and selected-anywhere counts include their original full acceptance.
True overflow, other missing rows and true-angle-only feed-in are not
reclassified. Thus the extended replay is still partial. The last three
columns printed in each row are observed negative tracks minus the fold of
the published spectrum in the reco 40–60, 60–80 and at-least-80 bands. They
use the same conventions as inputs/replay/replay.py in the receipt.

Figure 5 is used only for a comparison. Its expected selected yield here is
its digitized efficiency multiplied by OUR generated denominator in each true
cell. It is not an official selected event count. No efficiency is tuned and
no parameters are fitted. The diagnostic ratios and chi-squares are central
comparisons without propagated uncertainties. Production, including OmniFold,
has not been changed.
