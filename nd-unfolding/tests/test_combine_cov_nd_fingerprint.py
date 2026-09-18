#!/usr/bin/env python3
"""`combine_cov_nd.py` stored ONE TH2D and nothing else, so `ESTIMATOR_REGISTRY.md:17-22`'s
reject-on-mismatch rule was UNEXECUTABLE against the scalar stat and ML components -- five of nine
fingerprint fields were absent, not mismatched. A rule cannot run without operands. That is a WRITER
gap, and these are the first tests that it is closed.

The load-bearing design choice under test: an unsupplied field is recorded as the literal
"UNDECLARED", NOT omitted. A missing key reads as "not checked"; an explicit UNDECLARED reads as
"the writer was never told". Those are different findings and a consumer must be able to tell them
apart, so `test_unsupplied_fields_are_UNDECLARED_not_absent` asserts the key is present AND carries
the sentinel.

Also under test: the ensemble-count scalar the audit records as missing, so a reader can obtain N
from the product rather than inferring it from a launcher range.

ROOT is stubbed because no interpreter here has it and the gap is entirely on the write path.
"""
import json
import os
import pickle
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

_STORE, _CUR = {}, [None]


class _H1:
    def __init__(s, name, title, n, lo, hi):
        s.name, s.n, s.v, s._d = name, int(n), np.zeros(int(n)), _CUR[0]
    def SetBinContent(s, i, x): s.v[i - 1] = float(x)
    def GetBinContent(s, i): return float(s.v[i - 1])
    def GetNbinsX(s): return s.n
    def Write(s):
        if s._d: _STORE[s._d][s.name] = s


class _H2(_H1):
    def __init__(s, name, title, nx, a, b, ny, c, d):
        s.name, s.nx, s.ny, s._d = name, int(nx), int(ny), _CUR[0]
        s.v = np.zeros((int(nx), int(ny)))
    def SetBinContent(s, i, j, x): s.v[i - 1, j - 1] = float(x)


class _S:
    def __init__(s, name, val): s.name, s.val, s._d = name, val, _CUR[0]
    def Write(s):
        if s._d: _STORE[s._d][s.name] = s


class _F:
    def __init__(s, p, m): s.p, s.m = p, m
    def Get(s, k): return _STORE.get(s.p, {}).get(k)
    def Close(s):
        if s.m == "RECREATE":
            _CUR[0] = None
            with open(s.p, "wb") as fh:
                pickle.dump({k: getattr(o, "v", getattr(o, "val", None))
                             for k, o in _STORE[s.p].items()}, fh)


class _ROOT:
    class gROOT:
        @staticmethod
        def SetBatch(_): pass
    class TFile:
        @staticmethod
        def Open(p, m=None):
            if m == "RECREATE": _STORE[p] = {}; _CUR[0] = p
            return _F(p, m)
    TH1D, TH2D = _H1, _H2
    @staticmethod
    def TParameter(_k): return lambda n, v: _S(n, v)
    @staticmethod
    def TNamed(n, t): return _S(n, t)


class CombineCovFingerprint(unittest.TestCase):
    N_REP, N_BINS = 12, 40

    def setUp(self):
        _STORE.clear(); _CUR[0] = None
        sys.modules["ROOT"] = _ROOT
        import combine_cov_nd
        self.M = combine_cov_nd
        self.tmp = tempfile.mkdtemp()
        rng = np.random.default_rng(11)
        self.cv = np.zeros(self.N_BINS); self.cv[5:33] = rng.uniform(1e-39, 1e-38, 28)
        _STORE[os.path.join(self.tmp, "cv.root")] = {}
        cvp = os.path.join(self.tmp, "cv.root")
        _CUR[0] = cvp
        h = _H1("hXSecND_flat", "", self.N_BINS, 0, self.N_BINS); h.v = self.cv.copy(); h.Write()
        _CUR[0] = None
        with open(cvp, "wb") as fh: pickle.dump({"hXSecND_flat": self.cv}, fh)
        self.cvp = cvp
        for i in range(1, self.N_REP + 1):
            np.savez(os.path.join(self.tmp, f"res_{i:03d}.npz"),
                     xsec_flat=self.cv + rng.normal(0, 1e-40, self.N_BINS),
                     replica_id=np.array(i), shape=np.array([self.N_BINS]))

    def tearDown(self): sys.modules.pop("ROOT", None)

    def _run(self, extra=()):
        out = os.path.join(self.tmp, "cov.root")
        argv = ["combine_cov_nd.py", "--glob", os.path.join(self.tmp, "res_*.npz"),
                "--cv", self.cvp, "--tag", "stat5d", "--out", out,
                "--expected-ids", f"1-{self.N_REP}", *extra]
        old = sys.argv[:]; sys.argv = argv
        try: self.M.main()
        finally: sys.argv = old
        with open(out + ".receipt.json") as fh: return out, json.load(fh)

    def test_unsupplied_fields_are_UNDECLARED_not_absent(self):
        """The distinction the whole design turns on: present-and-sentinel, never missing."""
        out, rec = self._run()
        for f in self.M._SUPPLIED:
            self.assertIn(f, rec["fingerprint"], f"{f} is ABSENT; it must be present as UNDECLARED")
            self.assertEqual(rec["fingerprint"][f], self.M._UNDECLARED)
            self.assertIn(f"fingerprint_{f}", _STORE[out],
                          f"{f} must travel IN the product, not only in the sidecar")
        self.assertEqual(sorted(rec["fingerprint_undeclared"]), sorted(self.M._SUPPLIED))

    def test_supplied_fields_are_recorded_and_drop_out_of_undeclared(self):
        out, rec = self._run(extra=["--estimator-id", "omnifold-5d-lgbm", "--iters", "5",
                                    "--estimator-seed", "42"])
        self.assertEqual(rec["fingerprint"]["estimator_id"], "omnifold-5d-lgbm")
        self.assertEqual(rec["fingerprint"]["estimator_seed"], "42")
        self.assertNotIn("estimator_id", rec["fingerprint_undeclared"])
        self.assertIn("train_frac", rec["fingerprint_undeclared"])

    def test_ensemble_count_scalar_is_stored(self):
        """The audit: 'the writer still stores no ensemble-count scalar.'"""
        out, rec = self._run()
        self.assertEqual(rec["n_members"], self.N_REP)
        self.assertEqual(_STORE[out]["n_members"].val, self.N_REP)
        self.assertIn(f"N-1 = {self.N_REP - 1}", _STORE[out]["divisor"].val)

    def test_row_index_binds_rows_to_dense_grid_bins(self):
        out, rec = self._run()
        rows = _STORE[out]["hRowIndex"].v.astype(np.int64)
        np.testing.assert_array_equal(rows, np.flatnonzero(self.cv > 0))
        self.assertEqual(rec["n_reported"], int((self.cv > 0).sum()))

    def test_digests_cover_every_replica_and_the_product(self):
        out, rec = self._run()
        self.assertEqual(len(rec["replica_sha256"]), self.N_REP)
        self.assertEqual(len(rec["product_sha256"]), 64)
        self.assertEqual(sorted(rec["member_ids"]), list(range(1, self.N_REP + 1)))

    def test_status_does_not_claim_adoptability(self):
        _, rec = self._run()
        self.assertIn("CANDIDATE", rec["status"])
        self.assertIn("not adoption", rec["status"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
