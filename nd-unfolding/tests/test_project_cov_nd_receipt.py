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
    # `IsZombie` exists on the real `TFile` and was missing here, so the stub could not exercise
    # the projector's open-failure guard at all. A fixture that omits part of the interface it
    # stands in for cannot fail where the real thing would. `_zombie_paths` lets a test make one
    # open fail, which is the negative control for that guard.
    _zombie_paths = set()

    def __init__(self, path, mode): self.path, self.mode = path, mode
    def IsZombie(self): return self.path in _File._zombie_paths
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
        _File._zombie_paths.clear()   # shared class state; one test must not poison the next

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


class NpzInputPath(unittest.TestCase):
    """The projector can read the container its own subject was written in.

    `z_build.py::_write_product` writes `.npz` when the output path ends in `.npz` and ROOT `TH2D`s
    otherwise. The pilot that produced the candidate scalar-5D covariance -- job 58454524, products
    at `uq_5d/z_pilot_20260916_a5/` -- wrote NPZ, so this projector could not read its subject. The
    gap was in the READER, not in the product.

    ⚠ I ASSERTED THOSE PRODUCTS DID NOT EXIST, three ways, and all three were the same operand
    error: a covering search scoped to `*.root`, a directory inspection of the FAILED attempt `a3`
    instead of the successful `a5`, and `sacct` reporting this CLI's completion code 2 as `FAILED`.
    Verified since: 3 of 3 digests re-measured from the products in place equal
    `zpilot-20260916/outcome-58454524/product-digests.txt`. **UNSEARCHED is not ABSENT.**

    THE FIXTURES ARE WRITTEN BY THE PRODUCER. `z_build._write_product` builds every `.npz` here, so
    these tests cannot pass against a container shape only this test believes in. That function
    imports cleanly without ROOT, which is why it is usable as the fixture writer.
    """

    setUp = ProjectCovNDReceipt.setUp
    tearDown = ProjectCovNDReceipt.tearDown

    def _grid(self):
        P = self.P
        shape = tuple(len(P.AXIS_EDGES[a]) - 1 for a in ("pt", "pz", "eavail", "q3", "W"))
        n = int(np.prod(shape))
        rng = np.random.default_rng(11)
        xcv = np.zeros(n)
        rep = np.sort(rng.choice(n, size=300, replace=False))
        xcv[rep] = rng.uniform(1e-40, 1e-38, size=300)
        rows = np.nonzero(xcv > 0)[0].astype(np.int64)
        A = rng.normal(size=(rows.size, rows.size))
        C = A @ A.T
        return xcv, rows, C

    def _write_source(self, path, *, row_index=None, metadata=None):
        """Built with `z_build._write_product`, the real writer, not by hand."""
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        import z_build
        xcv, rows, C = self._grid()
        arrays = {
            "hCov_combined5d_total_uthrow": C,
            "hXSecND_flat": xcv,
            "hSupportMask": (xcv > 0).astype(float),
        }
        if row_index is not None:
            arrays["hRowIndex5D"] = np.asarray(row_index, np.int64)
        meta = {"variant": "cv", "adoptable": False,
                "scientific_acceptance": "NON-PASSING",
                "manifest_sha256": "f" * 64,
                "code_identity": {"revision": "fb9ec3560fd6d62295dffc81b5694c9e26667d5b"}}
        if metadata is not None:
            meta.update(metadata)
        z_build._write_product(Path(path), arrays, meta)
        return rows

    def _run_npz(self, src, extra=()):
        P = self.P
        out = os.path.join(self.tmp, "out.root")
        argv = ["project_cov_nd.py", "--src-cov", src,
                "--src-hist", "hCov_combined5d_total_uthrow", "--src-cv", src,
                "--src-axes", "pt,pz,eavail,q3,W", "--keep-axes", "eavail,W",
                "--out", out] + list(extra)
        old, sys.argv = sys.argv[:], argv
        try:
            P.main()
        finally:
            sys.argv = old
        with open(out + ".receipt.json") as fh:
            return out, json.load(fh)

    def test_projects_from_an_npz_source(self):
        src = os.path.join(self.tmp, "z-cv.npz")
        rows = self._write_source(src, row_index=None)
        _out, rec = self._run_npz(src)
        self.assertEqual(rec["src_container"], "npz")
        self.assertEqual(rec["src_reported"], rows.size)
        self.assertEqual(rec["n_dst"], 42)

    def test_producer_row_index_is_used_and_cross_checked(self):
        src = os.path.join(self.tmp, "z-cv.npz")
        rows = self._write_source(src, row_index=None)
        _o, rec_derived = self._run_npz(src)
        self.assertIn("producer index not present", rec_derived["src_row_index_basis"])
        src2 = os.path.join(self.tmp, "z-cv2.npz")
        self._write_source(src2, row_index=rows)
        _o2, rec_both = self._run_npz(src2)
        self.assertIn("REQUIRED equal", rec_both["src_row_index_basis"])
        self.assertIn("both present and identical", rec_both["src_row_index_basis"])

    def test_disagreeing_row_index_refuses(self):
        """Two statements of the row order that disagree cannot both bind the rows, and choosing
        one would be a guess. This is the check the cross-check exists to be."""
        src = os.path.join(self.tmp, "z-bad.npz")
        rows = self._write_source(src, row_index=None)
        bad = rows.copy()
        bad[0] = bad[0] + 1                       # one row label moved
        self._write_source(src, row_index=bad)
        with self.assertRaises(SystemExit) as cm:
            self._run_npz(src)
        self.assertIn("hRowIndex5D", str(cm.exception))
        self.assertIn("does NOT equal", str(cm.exception))

    def test_source_metadata_is_carried_into_the_receipt(self):
        """SOURCE BINDING: the projection must not be readable without the standing of what it
        was projected from."""
        src = os.path.join(self.tmp, "z-cv.npz")
        self._write_source(src, row_index=None)
        _out, rec = self._run_npz(src)
        md = rec["src_metadata"]
        self.assertIs(md["adoptable"], False)
        self.assertEqual(md["scientific_acceptance"], "NON-PASSING")
        self.assertEqual(md["variant"], "cv")
        self.assertEqual(md["manifest_sha256"], "f" * 64)
        self.assertEqual(md["code_identity"]["revision"],
                         "fb9ec3560fd6d62295dffc81b5694c9e26667d5b")

    def test_non_adoptable_source_refuses_a_publication_class_product(self):
        """Enforced on the DATA, not the output path, so it holds however the run is invoked."""
        src = os.path.join(self.tmp, "z-cv.npz")
        self._write_source(src, row_index=None)
        with self.assertRaises(SystemExit) as cm:
            self._run_npz(src, extra=["--run-class", "publication"])
        self.assertIn("adoptable: false", str(cm.exception))
        self.assertIn("non-adopted trunk", str(cm.exception))

    def test_non_adoptable_source_permits_a_diagnostic_product(self):
        """The guard must not fire on the run it is meant to allow."""
        src = os.path.join(self.tmp, "z-cv.npz")
        self._write_source(src, row_index=None)
        _out, rec = self._run_npz(src, extra=["--run-class", "diagnostic",
                                              "--acceptance-question", "tau, on the candidate"])
        self.assertEqual(rec["run_class"], "diagnostic")
        self.assertIn("NON-ADOPTED", rec["status"])

    def test_adoptable_source_permits_publication_class(self):
        """The opposite direction: the guard keys on the SOURCE, not on the word publication."""
        src = os.path.join(self.tmp, "z-ok.npz")
        self._write_source(src, row_index=None,
                           metadata={"adoptable": True, "scientific_acceptance": "PASSING"})
        _out, rec = self._run_npz(src, extra=["--run-class", "publication"])
        self.assertEqual(rec["run_class"], "publication")

    def test_missing_key_in_npz_names_what_is_there(self):
        src = os.path.join(self.tmp, "z-cv.npz")
        self._write_source(src, row_index=None)
        P = self.P
        out = os.path.join(self.tmp, "o2.root")
        argv = ["project_cov_nd.py", "--src-cov", src, "--src-hist", "hNoSuchKey",
                "--src-cv", src, "--src-axes", "pt,pz,eavail,q3,W",
                "--keep-axes", "eavail,W", "--out", out]
        old, sys.argv = sys.argv[:], argv
        try:
            with self.assertRaises(SystemExit) as cm:
                P.main()
        finally:
            sys.argv = old
        self.assertIn("hNoSuchKey", str(cm.exception))
        self.assertIn("hCov_combined5d_total_uthrow", str(cm.exception), "it must list what IS there")


class TheDigestBoundAdoptionException(unittest.TestCase):
    """Recognising an explicitly authorized exception WITHOUT a force flag and WITHOUT editing
    the candidate's historical metadata.

    The source records `adoptable: false`, so `--run-class publication` refuses. The refusal is
    liftable only by a record that NAMES THIS SOURCE'S MEASURED sha256 — so the operand is a path
    to evidence, never a boolean, and the same record cannot authorize a different product.

    ⚠ Two properties are as important as the lift itself:
      * `src_metadata` keeps `adoptable: false` and `scientific_acceptance: NON-PASSING` VERBATIM.
        The historical rejection is preserved, not rewritten.
      * the effective class becomes `publication-under-exception`, a distinct token, so a reader
        cannot mistake the product for one projected from an adoptable trunk.
    """

    setUp = ProjectCovNDReceipt.setUp
    tearDown = ProjectCovNDReceipt.tearDown
    _grid = NpzInputPath._grid
    _write_source = NpzInputPath._write_source

    def _run_pub(self, src, exception=None):
        P = self.P
        out = os.path.join(self.tmp, "pub.root")
        argv = ["project_cov_nd.py", "--src-cov", src,
                "--src-hist", "hCov_combined5d_total_uthrow", "--src-cv", src,
                "--src-axes", "pt,pz,eavail,q3,W", "--keep-axes", "eavail,W",
                "--out", out, "--run-class", "publication"]
        if exception:
            argv += ["--adoption-exception", exception]
        old, sys.argv = sys.argv[:], argv
        try:
            P.main()
        finally:
            sys.argv = old
        with open(out + ".receipt.json") as fh:
            return out, json.load(fh)

    def _src_and_digest(self):
        src = os.path.join(self.tmp, "z-cv.npz")
        self._write_source(src, row_index=None)
        return src, self.P._sha256_file(src)

    def test_without_an_exception_the_refusal_stands(self):
        src, _ = self._src_and_digest()
        with self.assertRaises(SystemExit) as cm:
            self._run_pub(src)
        self.assertIn("--adoption-exception", str(cm.exception))

    def test_a_missing_record_refuses(self):
        src, _ = self._src_and_digest()
        with self.assertRaises(SystemExit) as cm:
            self._run_pub(src, os.path.join(self.tmp, "nope.md"))
        self.assertIn("no adoption-exception record", str(cm.exception))

    def test_a_record_not_naming_the_digest_refuses(self):
        """The anti-force-flag property: a record that authorizes nothing in particular
        authorizes everything, so it must be refused."""
        src, _ = self._src_and_digest()
        rec = os.path.join(self.tmp, "exc_generic.md")
        with open(rec, "w") as fh:
            fh.write("I authorize a publication exception for the scalar-5D candidate.\n")
        with self.assertRaises(SystemExit) as cm:
            self._run_pub(src, rec)
        self.assertIn("does not contain the measured sha256", str(cm.exception))
        self.assertIn("general waiver", str(cm.exception))

    def test_a_record_naming_a_DIFFERENT_digest_refuses(self):
        src, _ = self._src_and_digest()
        rec = os.path.join(self.tmp, "exc_wrong.md")
        with open(rec, "w") as fh:
            fh.write("authorized for sha256 " + "b" * 64 + "\n")
        with self.assertRaises(SystemExit) as cm:
            self._run_pub(src, rec)
        self.assertIn("does not contain the measured sha256", str(cm.exception))

    def test_a_matching_record_permits_the_projection(self):
        src, digest = self._src_and_digest()
        rec = os.path.join(self.tmp, "exc_ok.md")
        with open(rec, "w") as fh:
            fh.write("Candidate-specific exception.\nauthorized src_cov sha256: %s\n" % digest)
        _out, r = self._run_pub(src, rec)
        self.assertEqual(r["run_class"], "publication-under-exception")
        self.assertEqual(r["adoption_exception"]["authorized_src_cov_sha256"], digest)
        self.assertIn("record_sha256", r["adoption_exception"])

    def test_the_historical_rejection_is_PRESERVED_verbatim(self):
        """The load-bearing property. The exception must not edit the evidence it excepts."""
        src, digest = self._src_and_digest()
        rec = os.path.join(self.tmp, "exc_ok.md")
        with open(rec, "w") as fh:
            fh.write("authorized src_cov sha256: %s\n" % digest)
        _out, r = self._run_pub(src, rec)
        self.assertIs(r["src_metadata"]["adoptable"], False)
        self.assertEqual(r["src_metadata"]["scientific_acceptance"], "NON-PASSING")

    def test_the_status_discloses_the_exception_and_that_evidence_is_still_owed(self):
        src, digest = self._src_and_digest()
        rec = os.path.join(self.tmp, "exc_ok.md")
        with open(rec, "w") as fh:
            fh.write("authorized src_cov sha256: %s\n" % digest)
        _out, r = self._run_pub(src, rec)
        self.assertIn("DIGEST-BOUND EXCEPTION", r["status"])
        self.assertIn("still records", r["status"])
        self.assertIn("the exception unblocks the route, it does not supply the evidence",
                      r["status"])

    def test_there_is_no_general_force_flag(self):
        import pathlib
        text = pathlib.Path(self.P.__file__).read_text()
        for bad in ("--force", "--no-verify", "--skip-adoption", "MNV_FORCE"):
            self.assertNotIn(bad, text, f"a general bypass appeared: {bad}")
