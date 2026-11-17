"""Fake ROOT for a local identity test of make_control_plots.py: deterministic histograms per (name, column)."""
import zlib, numpy as np
gErrorIgnoreLevel = 0; kError = 3000
def EnableImplicitMT(n): pass
class _P:
    def __init__(s, v): s.v = v
    def GetVal(s): return s.v
class TFile:
    @staticmethod
    def Open(p): return TFile()
    def Get(s, k): return _P({"dataPOTUsed": 1.057e21, "mcPOTUsed": 3.5e21}[k])
    def Close(s): pass
class _H1:
    def __init__(s, n, key):
        r = np.random.default_rng(zlib.crc32(key.encode())); s.c = 1e5*np.exp(-np.arange(n)/3)*(1+0.1*r.random(n))+5; s.e = np.sqrt(s.c)
    def GetNbinsX(s): return len(s.c)
    def GetBinContent(s, i): return float(s.c[i-1])
    def GetBinError(s, i): return float(s.e[i-1])
class _H2:
    def __init__(s, n, key):
        r = np.random.default_rng(zlib.crc32(key.encode())); s.m = (np.eye(n)*0.6+0.2*np.eye(n,k=1))*1000*(1+0.1*r.random((n,n)))
    def GetBinContent(s, i, j): return float(s.m[i-1, j-1])
class _R:
    def __init__(s, v): s.v = v
    def GetValue(s): return s.v
class _M1:
    def __init__(s, name, t, n, e): s.n = n; s.name = name
class _M2:
    def __init__(s, name, t, n, e, n2, e2): s.n = n; s.name = name
class RDF:
    TH1DModel = _M1; TH2DModel = _M2
class RDataFrame:
    def __init__(s, tree, f): s.tree = tree
    def Filter(s, c): return s
    def Histo1D(s, m, col, w=None): return _R(_H1(m.n, s.tree+col))
    def Histo2D(s, m, a, b, w=None): return _R(_H2(m.n, s.tree+a+b))
