"""Read-only: recompute the tracker fiducial nucleon count with MAT's TargetUtils (2d-closeout A-2)."""
import ROOT
for lib in ("libMAT", "libMAT-MINERvA"):
    print(lib, ROOT.gSystem.Load(lib))
tu = ROOT.PlotUtils.TargetUtils.Get()
for isMC in (True, False):
    n = tu.GetTrackerNNucleons(5980.0, 8422.0, isMC, 850.0)
    print(f"isMC={isMC} GetTrackerNNucleons(5980,8422,apothem=850) = {n!r}")
print("driver constant 3.2352943296224835e+30")
