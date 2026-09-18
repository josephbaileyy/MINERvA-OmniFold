#!/usr/bin/env python3
"""First tests for `project_cov_nd.py` -- there were none, and it is the projector that would
produce M1, the only map the one deferred publication claim can be built from.

WHY A ROOT STUB. No interpreter available here has ROOT, and the defect these tests exist to catch
lives entirely on the write/read-back path, so a test that skipped ROOT would skip the hazard. The
stub stores objects in memory AND writes real bytes to the real path, so `_sha256_file` digests
something that exists. `test_readback_failure_raises` is the one that matters: it makes the stored
array differ from the array it was written from -- exactly the "write did not land" case that the
old in-memory-only digest could not detect -- and requires the writer to refuse.

`_verify_canonical_edges` is stubbed out: it imports the ROOT-dependent unfolding modules purely to
assert the hardcoded edges have not drifted, which is a different property with its own failure mode
and is not what these tests are about.
"""
import hashlib
import json
import os
import pickle
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

_STORE = {}          # path -> {key: obj}
_CURRENT = [None]    # the directory objects attach to at construction, as ROOT does


class _H1:
    def __init__(self, name, title, n, lo, hi):
        self.name, self.n = name, int(n)
        self.v = np.zeros(int(n), float)
        self._dir = _CURRENT[0]
    def SetBinContent(self, i, x): self.v[i - 1] = float(x)
    def GetBinContent(self, i): return float(self.v[i - 1])
    def GetNbinsX(self): return self.n
    def Write(self):
        if self._dir is not None:
            _STORE[self._dir][self.name] = self


class _H2:
    def __init__(self, name, title, nx, xlo, xhi, ny, ylo, yhi):
        self.name, self.nx, self.ny = name, int(nx), int(ny)
        self.v = np.zeros((int(nx), int(ny)), float)
        self._dir = _CURRENT[0]
    def SetBinContent(self, i, j, x): self.v[i - 1, j - 1] = float(x)
    def GetNbinsX(self): return self.nx
    def GetNbinsY(self): return self.ny
    def GetArray(self):
        pad = np.zeros((self.ny + 2, self.nx + 2), float)
        pad[1:self.ny + 1, 1:self.nx + 1] = self.v.T
        return np.ascontiguousarray(pad).data
    def Write(self):
        if self._dir is not None:
            _STORE[self._dir][self.name] = self


class _Scalar:
    def __init__(self, name, val): self.name, self.val = name, val; self._dir = _CURRENT[0]
    def Write(self):
        if self._dir is not None:
            _STORE[self._dir][self.name] = self


class _File:
    def __init__(self, path, mode): self.path, self.mode = path, mode
    def Get(self, key): return _STORE.get(self.path, {}).get(key)
    def Close(self):
        if self.mode == "RECREATE":
            _CURRENT[0] = None
            with open(self.path, "wb") as fh:          # real bytes, so the digest is of something
                pickle.dump({k: getattr(o, "v", getattr(o, "val", None))
                             for k, o in _STORE[self.path].items()}, fh)


class _TFile:
    @staticmethod
    def Open(path, mode=None):
        if mode == "RECREATE":
            _STORE[path] = {}
            _CURRENT[0] = path
        return _File(path, mode)


class _ROOT:
    TFile = _TFile
    TH1D = _H1
    TH2D = _H2
    @staticmethod
    def TParameter(_kind):
        return lambda name, val: _Scalar(name, val)
    @staticmethod
    def TNamed(name, title): return _Scalar(name, title)


def _write_src(path, key, arr2d_or_1d, is2d):
    _STORE[path] = {}
    prev, _CURRENT[0] = _CURRENT[0], path
    if is2d:
        n = arr2d_or_1d.shape[0]
        h = _H2(key, "", n, 0, n, n, 0, n)
        h.v = np.asarray(arr2d_or_1d, float).copy()
    else:
        h = _H1(key, "", arr2d_or_1d.size, 0, arr2d_or_1d.size)
        h.v = np.asarray(arr2d_or_1d, float).copy()
    h.Write()
    _CURRENT[0] = prev
    with open(path, "wb") as fh:
        pickle.dump({key: h.v}, fh)


class ProjectCovNDReceipt(unittest.TestCase):
    """The grid is the real one: pt 14 x pz 16 x eavail 7 x q3 7 x W 6 = 65,856 dense."""

    def setUp(self):
        _STORE.clear(); _CURRENT[0] = None
        sys.modules["ROOT"] = _ROOT
        import project_cov_nd as P
        self.P = P
        self._real_verify = P._verify_canonical_edges
        P._verify_canonical_edges = lambda: None
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        self.P._verify_canonical_edges = self._real_verify
        sys.modules.pop("ROOT", None)

    def _run(self, keep="eavail,W", mutate_stored=None, run_class=None, question=None):
        P = self.P
        src_shape = tuple(len(P.AXIS_EDGES[a]) - 1 for a in ("pt", "pz", "eavail", "q3", "W"))
        n_dense = int(np.prod(src_shape))
        rng = np.random.default_rng(3)
        xcv = np.zeros(n_dense)
        rep = rng.choice(n_dense, size=400, replace=False)
        xcv[rep] = rng.uniform(1e-40, 1e-38, size=400)
        nrep = int((xcv > 0).sum())
        A = rng.normal(size=(nrep, nrep)); C = A @ A.T

        cov = os.path.join(self.tmp, "cov.root"); cv = os.path.join(self.tmp, "cv.root")
        out = os.path.join(self.tmp, "out.root")
        _write_src(cov, "hCov", C, True)
        _write_src(cv, "hXSecND_flat", xcv, False)

        argv = ["project_cov_nd.py", "--src-cov", cov, "--src-hist", "hCov", "--src-cv", cv,
                "--src-axes", "pt,pz,eavail,q3,W", "--keep-axes", keep, "--out", out]
        if run_class is not None:
            argv += ["--run-class", run_class]
        if question is not None:
            argv += ["--acceptance-question", question]
        old = sys.argv[:]
        sys.argv = argv
        try:
            if mutate_stored is not None:
                real_close = _File.Close
                def patched(self_f):
                    real_close(self_f)
                    if self_f.mode == "RECREATE" and "hRowIndex" in _STORE.get(self_f.path, {}):
                        mutate_stored(_STORE[self_f.path]["hRowIndex"])
                _File.Close = patched
                try:
                    P.main()
                finally:
                    _File.Close = real_close
            else:
                P.main()
        finally:
            sys.argv = old
        return out

    def test_happy_path_writes_row_index_and_digests(self):
        out = self._run()
        with open(out + ".receipt.json") as fh:
            rec = json.load(fh)
        for k in ("proj_sha256", "src_cov_sha256", "src_cv_sha256", "M_content_sha256",
                  "row_index_sha256_readback", "row_index_key", "dst_mask_basis",
                  "weight_basis", "paired_central_estimate", "n_empty"):
            self.assertIn(k, rec, f"receipt is missing {k}")
        self.assertEqual(rec["row_index_key"], "hRowIndex")
        self.assertIn("hRowIndex", _STORE[out], "the row-index array was never written")
        # WAS `assertEqual(rec["status"][:9], "CANDIDATE")`, which asserted a CONSTANT: every
        # product carried that string whatever it was, so the field discriminated nothing. An
        # unsupplied class now records the explicit sentinel -- present, never omitted.
        self.assertEqual(rec["run_class"], "UNDECLARED")
        self.assertEqual(rec["acceptance_question"], "UNDECLARED")
        self.assertTrue(rec["status"].startswith("UNDECLARED"), rec["status"])

    def test_proj_digest_is_of_the_bytes_on_disk(self):
        """A digest of the in-memory object would pass this too, so it is checked against the file."""
        out = self._run()
        with open(out + ".receipt.json") as fh:
            rec = json.load(fh)
        h = hashlib.sha256()
        with open(out, "rb") as fh:
            h.update(fh.read())
        self.assertEqual(rec["proj_sha256"], h.hexdigest())

    def test_row_labels_are_the_destination_dense_indices(self):
        out = self._run()
        stored = _STORE[out]["hRowIndex"].v.astype(np.int64)
        self.assertTrue(np.all(np.diff(stored) > 0), "row labels must be strictly increasing")
        n_dst = _STORE[out]["n_dst"].val
        self.assertEqual(stored.size, n_dst)
        self.assertLess(stored.max(), 7 * 6, "eavail x W has 42 dense cells")

    def test_readback_failure_raises(self):
        """THE ONE THAT MATTERS: stored array != array written -> the writer must refuse.
        This is the case the old in-memory-only digest could not detect."""
        with self.assertRaises(SystemExit) as cm:
            self._run(mutate_stored=lambda h: h.v.__setitem__(0, h.v[0] + 1))
        self.assertIn("hRowIndex", str(cm.exception))

    def test_truncated_write_also_raises(self):
        """Opposite-direction control: a short write, not a wrong value."""
        def trunc(h):
            h.v = h.v[:-1]; h.n -= 1
        with self.assertRaises(SystemExit) as cm:
            self._run(mutate_stored=trunc)
        self.assertIn("hRowIndex", str(cm.exception),
                      "must fail FOR THE READBACK REASON, not incidentally")

    def test_weights_are_products_of_dropped_axis_widths(self):
        """The convention that makes the destination a differential density in the kept axes."""
        P = self.P
        src_axes = ["pt", "pz", "eavail", "q3", "W"]
        src_shape = tuple(len(P.AXIS_EDGES[a]) - 1 for a in src_axes)
        flat = np.array([np.ravel_multi_index((2, 3, 4, 1, 2), src_shape)])
        dst_shape = (7, 6)
        dst_index_of = -np.ones(int(np.prod(dst_shape)), dtype=int)
        dst_index_of[np.ravel_multi_index((4, 2), dst_shape)] = 0
        M, dropped = P.build_projection(src_axes, ["eavail", "W"], flat, src_shape,
                                        dst_shape, dst_index_of)
        expect = (np.diff(P.AXIS_EDGES["pt"])[2] * np.diff(P.AXIS_EDGES["pz"])[3]
                  * np.diff(P.AXIS_EDGES["q3"])[1])
        self.assertAlmostEqual(M[0, 0], expect, places=12)
        self.assertEqual(dropped, 0)

    def test_orphan_source_cell_is_dropped_and_counted(self):
        P = self.P
        src_axes = ["pt", "pz", "eavail", "q3", "W"]
        src_shape = tuple(len(P.AXIS_EDGES[a]) - 1 for a in src_axes)
        flat = np.array([np.ravel_multi_index((2, 3, 4, 1, 2), src_shape)])
        dst_shape = (7, 6)
        dst_index_of = -np.ones(int(np.prod(dst_shape)), dtype=int)   # nothing reported
        M, dropped = P.build_projection(src_axes, ["eavail", "W"], flat, src_shape,
                                        dst_shape, dst_index_of)
        self.assertEqual(dropped, 1)
        self.assertEqual(M.shape[0], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)


class RunClassLabel(unittest.TestCase):
    """The run-class label, added 2026-09-18 under Joseph's diagnostic-projection grant.

    The grant is CONDITIONAL: provisional projections from the preserved candidate covariance are
    authorized "labeled diagnostic and non-adopted, with separate outputs and receipts". Before
    this, `status` was a CONSTANT STRING -- every product said `CANDIDATE` whatever it was -- so
    there was no field in the product or the receipt that could tell a diagnostic product from a
    publication-path one, and the separation the grant requires would have rested on the output
    path alone.

    `test_statuses_are_pairwise_distinct` is the one that matters: it is the guard against the
    field silently becoming a constant again, which is the exact state this change repaired. A
    test that only checked "diagnostic says DIAGNOSTIC" would pass a writer that also said
    DIAGNOSTIC for a publication product.
    """

    setUp = ProjectCovNDReceipt.setUp
    tearDown = ProjectCovNDReceipt.tearDown
    _run = ProjectCovNDReceipt._run

    def _receipt(self, **kw):
        out = self._run(**kw)
        with open(out + ".receipt.json") as fh:
            return out, json.load(fh)

    def test_candidate_class_reproduces_the_former_constant(self):
        """No regression for `sbatch_project_5d_to_4d_candidate_gpu.sh`, which is a candidate run.

        That launcher self-describes as a "DRY-RUN (validation only, NOT a quotable result) ->
        candidate path", so `candidate` is not a new meaning invented for it -- it is what the old
        constant meant, and declaring it keeps its product's recorded class unchanged.
        """
        _out, rec = self._receipt(run_class="candidate")
        self.assertEqual(rec["run_class"], "candidate")
        self.assertEqual(rec["status"][:9], "CANDIDATE")

    def test_diagnostic_class_is_labelled_non_adopted(self):
        _out, rec = self._receipt(run_class="diagnostic", question="tau: corner chi2 movement")
        self.assertEqual(rec["run_class"], "diagnostic")
        self.assertEqual(rec["acceptance_question"], "tau: corner chi2 movement")
        self.assertIn("NON-ADOPTED", rec["status"])
        self.assertIn("PROVISIONAL", rec["status"])
        self.assertNotIn("CANDIDATE", rec["status"])

    def test_diagnostic_without_a_question_refuses(self):
        """The grant is scoped to resolving a NAMED acceptance question, so an unnamed one is
        outside it. A default would have put the run inside the grant by omission."""
        with self.assertRaises(SystemExit) as cm:
            self._run(run_class="diagnostic")
        self.assertIn("--acceptance-question", str(cm.exception))

    def test_whitespace_only_question_refuses(self):
        """`--acceptance-question '  '` is an unnamed question wearing a name."""
        with self.assertRaises(SystemExit) as cm:
            self._run(run_class="diagnostic", question="   ")
        self.assertIn("--acceptance-question", str(cm.exception))

    def test_statuses_are_pairwise_distinct(self):
        """MUTATION GUARD. Collapse `status` back to a constant and this is the test that fails."""
        seen = {}
        for cls, q in (("diagnostic", "q"), ("candidate", None),
                       ("publication", None), (None, None)):
            _out, rec = self._receipt(run_class=cls, question=q)
            seen[cls or "UNDECLARED"] = rec["status"]
        self.assertEqual(len(set(seen.values())), 4,
                         f"status must discriminate the classes, got {seen}")

    def test_label_travels_inside_the_product_not_only_the_sidecar(self):
        """A diagnostic product moved out of its diagnostic directory, or stripped of its
        sidecar, must still say what it is. A path is the weakest possible binding, and this same
        writer already learned that for row labels under OI-129."""
        out, rec = self._receipt(run_class="diagnostic", question="tau")
        for key in ("runClass", "runClassStatus", "acceptanceQuestion"):
            self.assertIn(key, _STORE[out], f"{key} was not written into the product")
            self.assertIn(key, rec["run_class_keys_in_product"])
        self.assertEqual(_STORE[out]["runClass"].val, "diagnostic")
        self.assertIn("NON-ADOPTED", _STORE[out]["runClassStatus"].val)
        self.assertEqual(_STORE[out]["acceptanceQuestion"].val, "tau")

    def test_undeclared_keys_are_present_rather_than_omitted(self):
        """`combine_cov_nd.py`'s design choice, applied here: a missing key reads as "not
        checked", an explicit UNDECLARED reads as "the writer was never told"."""
        out, rec = self._receipt()
        self.assertIn("runClass", _STORE[out])
        self.assertEqual(_STORE[out]["runClass"].val, "UNDECLARED")
        self.assertEqual(rec["run_class"], "UNDECLARED")


if __name__ == "__main__":
    unittest.main()
