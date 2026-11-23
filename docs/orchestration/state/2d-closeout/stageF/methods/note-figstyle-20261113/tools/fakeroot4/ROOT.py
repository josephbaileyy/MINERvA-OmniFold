"""A stand-in for PyROOT for the family-4 identity test (tools/identity_family4.py): one TH1, hXSec_eavail, with
deterministic synthetic contents on the 3D analysis's E_avail edges ending in the [3,100] GeV catch bin."""
import numpy as np
EDGES = [0.0, 0.04, 0.08, 0.12, 0.16, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0, 3.0, 100.0]
class _Ax:
    def GetBinLowEdge(s, i): return EDGES[i - 1]
    def GetBinUpEdge(s, i): return EDGES[i]
class _H:
    def __init__(s):
        n = len(EDGES) - 1; x = np.arange(1, n + 1)
        s.c = 1e-39 * np.exp(-0.3 * x) * (1 + 0.1 * np.sin(x)); s.e = 0.05 * s.c
    def GetNbinsX(s): return len(EDGES) - 1
    def GetXaxis(s): return _Ax()
    def GetBinContent(s, i): return float(s.c[i - 1])
    def GetBinError(s, i): return float(s.e[i - 1])
class TFile:
    @staticmethod
    def Open(p): return TFile()
    def Get(s, k):
        assert k == "hXSec_eavail", k
        return _H()
    def Close(s): pass
class _G:
    def SetBatch(s, b): pass
gROOT = _G()
