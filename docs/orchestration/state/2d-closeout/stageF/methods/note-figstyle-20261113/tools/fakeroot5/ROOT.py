"""A stand-in for PyROOT for the family-5 identity test (tools/identity_family5.py). TFile.Open(path).Get(name) returns
a TH2 whose deterministic synthetic contents depend on the file name, on the FPS extended grid (15 x 19 cells), or the paper grid (14 x 16) for a file named *ctrl*."""
import zlib
import numpy as np
kError = 3000
gErrorIgnoreLevel = 0
class _G:
    def SetBatch(s, b): pass
gROOT = _G()
class _H2:
    def __init__(s, m): s.m = m
    def __bool__(s): return True
    def GetNbinsX(s): return s.m.shape[0]
    def GetNbinsY(s): return s.m.shape[1]
    def GetBinContent(s, i, j): return float(s.m[i - 1, j - 1])
class _P:
    def __init__(s, v): s.v = v
    def __bool__(s): return True
    def GetVal(s): return s.v
class _H1:
    def __init__(s, c): s.c = c
    def GetNbinsX(s): return len(s.c)
    def GetBinContent(s, i): return float(s.c[i - 1])
class TFile:
    def __init__(s, p): s.p = str(p)
    @staticmethod
    def Open(p): return TFile(p)
    def Get(s, k):
        if k in ("dataPOTUsed", "mcPOTUsed"):
            return _P({"dataPOTUsed": 1.057e21, "mcPOTUsed": 3.5e21}[k])
        if k == "hUnfoldND_flat":   # q3_excess_projection.py: the 4D grid, 14 x 16 x 7 x 7 = 10976 cells
            x = np.arange(10976)
            return _H1(0.53 * (1 + 0.5 * np.sin(x / 37.0)))   # near the prior's total, so the ratio straddles 1
        seed = zlib.crc32((s.p.rsplit("/", 1)[-1] + k).encode()) % 1000
        nx, ny = (14, 16) if "ctrl" in s.p.lower() else (15, 19)   # the control unfold is on the paper grid
        i, j = np.meshgrid(np.arange(nx), np.arange(ny), indexing="ij")
        m = 1e-39 * np.exp(-0.2 * i - 0.15 * j) * (1 + 0.2 * np.sin(i * 0.9 + j * 0.4 + seed / 100.0))
        m[(i == nx - 1) & (j < 2)] = 0.0
        return _H2(m)
    def Close(s): pass


# A minimal RDataFrame for fps_acceptance.py: Define and Filter chain, Sum and Histo2D return deterministic results that
# depend on the tree name and the filter chain.
def EnableImplicitMT(n=0): pass
class _V:
    def __init__(s, v): s.v = v
    def GetValue(s): return s.v
class _RH2(_H2):
    def GetValue(s): return s
class _Model:
    def __init__(s, name, title, nx, xe, ny, ye): s.nx, s.ny = nx, ny
class _RDF:
    TH2DModel = _Model
RDF = _RDF()
class RDataFrame:
    def __init__(s, tree, path=None, chain=""): s.tree, s.chain = tree, chain
    def Define(s, name, expr): return RDataFrame(s.tree, chain=s.chain + "|D" + name)
    def Filter(s, expr): return RDataFrame(s.tree, chain=s.chain + "|F" + expr)
    def Sum(s, col):
        return _V(1e6 * (1 + (zlib.crc32((s.tree + s.chain).encode()) % 1000) / 1000.0) / (1 + s.chain.count("|F")))
    def AsNumpy(s, cols):   # q3_excess_projection.py: truth-pass kinematics of 20000 synthetic events
        r = np.random.default_rng(1234)
        n = 20000
        v = {"MC": r.uniform(0, 1.8, n), "MC_pz": r.uniform(1.5, 25, n), "MC_eavail": r.exponential(0.3, n),
             "MC_q3": r.uniform(0.0, 1.5, n), "w_truth": r.uniform(0.5, 1.5, n)}
        return {c: v[c] for c in cols}
    def Histo2D(s, model, x, y, w):
        i, j = np.meshgrid(np.arange(model.nx), np.arange(model.ny), indexing="ij")
        m = 1e4 * np.exp(-0.25 * i - 0.1 * np.abs(j - 9))
        if "sim_pass" in s.chain:
            m = m * (0.05 + 0.6 / (1 + np.exp(i - 9)))
            m[(i < 2) & (j < 2)] = 0.0
        return _RH2(m)
