echo "host=$(hostname) $(date -u +%FT%TZ)"
X=/cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/v3_04_00/NULL
sha256sum $X/G1810a0211b-k250-e1000/data/gxspl-NUsmall.xml $X/G1810a0211b-k250-e1000/data/README $X/AR2320i00000-k250-e1000/data/gxspl-NUsmall.xml $X/AR2320i00000-k250-e1000/data/README
H=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root
sha256sum $H
G=/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix/genie_cv_xsec5d_full.npz; sha256sum $G
env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -B -c "
import ROOT
f=ROOT.TFile.Open('$H'); print([k.GetName() for k in f.GetListOfKeys()][:20]); h=f.Get('hFluxCV'); print('hFluxCV', bool(h), h.GetNbinsX() if h else None, h.GetBinContent(1) if h else None)
"
ls -la /global/homes/j/josephrb/.genie_compatlibs/ | head
ls /pscratch/sd/j/josephrb/ | grep -i f1; df -h /pscratch 2>/dev/null | tail -1
which hsi htar hpssquota; ls /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh
