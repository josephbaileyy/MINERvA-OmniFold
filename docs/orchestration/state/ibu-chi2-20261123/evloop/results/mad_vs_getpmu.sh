# login02, read-only on this lane's merged output; run 2026-11-24 after ibuchi_ana
cd /pscratch/sd/j/josephrb/ibuchi-evloop-20261123/work && python3 -c '
import ROOT
f = "../out/runEventLoopOmniFold_MEFHC.root"
for t in ["data", "mc_background", "mc_signal_reco"]:
    d = ROOT.RDataFrame(t, f).Filter("mu_p_total>0")
    n = d.Count(); nd = d.Filter("abs(mu_mad_p-mu_p_total)>1e-6*mu_p_total").Count()
    nm = d.Filter("mu_mad_p<=0").Count(); mx = d.Define("r", "abs(mu_mad_p-mu_p_total)").Max("r")
    print(t, n.GetValue(), nd.GetValue(), nm.GetValue(), mx.GetValue())'
