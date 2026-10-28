source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh > /dev/null 2>&1
python3 -V
H=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root
python3 -c "
import ROOT
f=ROOT.TFile.Open('$H'); print([k.GetName() for k in f.GetListOfKeys()][:12]); h=f.Get('hFluxCV'); print('hFluxCV', bool(h), h.GetNbinsX() if h else None, repr(h.GetBinContent(1)) if h else None)
"
