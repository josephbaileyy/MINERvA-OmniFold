"""A stand-in for PyROOT for the family-3 identity test (tools/identity_family3.py): two TH2s with deterministic
synthetic contents, hRel2D (14 x 16, the pT x p|| grid, with some empty bins) and hCov2D_reported (205 x 205, positive
definite)."""
import numpy as np
class _H2:
    def __init__(s, m): s.m = m
    def GetNbinsX(s): return s.m.shape[0]
    def GetNbinsY(s): return s.m.shape[1]
    def GetBinContent(s, i, j): return float(s.m[i - 1, j - 1])
def _rel():
    i, j = np.meshgrid(np.arange(14), np.arange(16), indexing="ij")
    m = 0.02 + 0.01 * np.sin(i + 0.7 * j) ** 2
    m[(i > 11) & (j < 3)] = 0.0
    return m
def _cov():
    x = np.arange(205); a = np.exp(-np.abs(x[:, None] - x[None, :]) / 9.0)
    return a * np.outer(1 + 0.3 * np.cos(x / 7.0), 1 + 0.3 * np.cos(x / 7.0)) * 1e-80
class TFile:
    @staticmethod
    def Open(p): return TFile()
    def Get(s, k): return _H2({"hRel2D": _rel(), "hCov2D_reported": _cov()}[k])
    def Close(s): pass
class _G:
    def SetBatch(s, b): pass
gROOT = _G()
