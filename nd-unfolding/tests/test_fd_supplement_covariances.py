"""Controls for the Supplemental Material's three covariance files (fd_supplement_covariances.py), in both directions:
the committed package passes, and each control fails a copy built to break it."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))

import fd_deposit_candidate as fdc  # noqa: E402
import fd_supplement_covariances as sup  # noqa: E402

FD = ND.parent / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/with-cpl"
DP = FD / "data-product/fd_data_product_cpl.json"
PKG = FD / "deposit-candidate"


class Supplement(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fd-sup-"))
        self.dp_dir = self.tmp / "data-product"
        shutil.copytree(DP.parent, self.dp_dir)
        self.pkg = self.tmp / "pkg"
        shutil.copytree(PKG, self.pkg)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def check(self, dp=None, pkg=None):
        with mock.patch("sys.stdout"), mock.patch("sys.stderr"):
            return sup.main(["check", "--data-product", str(dp or self.dp_dir / DP.name), "--package", str(pkg or self.pkg)])

    def test_the_committed_package_passes(self):
        self.assertEqual(self.check(DP, PKG), 0)
        man = json.loads((PKG / sup.MANIFEST).read_text())
        self.assertEqual([f["name"] for f in man["files"] if f["reported"]], ["covariance-reported.csv"])
        self.assertEqual((PKG / "covariance-reported.csv").read_bytes(), (PKG / "covariance.csv").read_bytes())
        old = FD.parent / "deposit-candidate/covariance.csv"  # the covariance reported before the 5B addition
        self.assertEqual((PKG / "covariance-without-C_PL5D.csv").read_bytes(), old.read_bytes())

    def test_build_writes_the_committed_bytes_and_never_overwrites(self):
        fresh = self.tmp / "fresh"
        fresh.mkdir()
        shutil.copy(PKG / "covariance.csv", fresh / "covariance.csv")
        shutil.copy(PKG / sup.README, fresh / sup.README)
        with mock.patch("sys.stdout"):
            self.assertEqual(sup.main(["build", "--data-product", str(DP), "--package", str(fresh)]), 0)
        for n, _, _ in sup.FILES:
            self.assertEqual((fresh / n).read_bytes(), (PKG / n).read_bytes())
        self.assertEqual(self.check(DP, fresh), 0)
        with mock.patch("sys.stdout"), mock.patch("sys.stderr"):
            self.assertEqual(sup.main(["build", "--data-product", str(DP), "--package", str(fresh)]), 1)

    def test_a_changed_file_or_a_wrong_data_product_refuses(self):
        # the same values written differently: the matrix still matches (S2), only the byte copy (S1) can refuse
        p = self.pkg / "covariance-C_PL5D.csv"
        p.write_bytes(p.read_bytes().replace(b"1.698549800076996e-82", b"1.6985498000769960e-82", 1))
        self.assertTrue(np.array_equal(fdc.read_matrix_csv(p.read_text()), fdc.read_matrix_csv((PKG / p.name).read_text())))
        with self.assertRaisesRegex(fdc.Stop, "S1"), mock.patch("sys.stdout"):
            sup.check(self.pkg, self.dp_dir / DP.name)
        p.write_bytes(p.read_bytes().replace(b"e-82", b"e-81", 1))
        self.assertEqual(self.check(), 1)
        self.assertEqual(self.check(self.dp_dir / "fd_data_product_cpl_cells.csv", PKG), 1)  # not the pinned bytes

    def test_files_that_do_not_differ_only_by_the_block_refuse(self):
        # a data product whose reported matrix is not without + C_PL5D: S0-S2 hold (re-pinned), S3 must refuse
        dpj = json.loads((self.dp_dir / DP.name).read_text())
        C = np.array(dpj["matrices"][sup.REPORTED], float)
        C[0, 0] *= 1 + 1e-12
        dpj["matrices"][sup.REPORTED] = C.tolist()
        text = fdc.matrix_csv(C)
        (self.dp_dir / sup.source_csv(sup.REPORTED)).write_text(text)
        dpj["files_sha256"][sup.source_csv(sup.REPORTED)] = fdc.sha256(self.dp_dir / sup.source_csv(sup.REPORTED))
        (self.dp_dir / DP.name).write_text(json.dumps(dpj))
        for n, _, _ in sup.FILES:
            (self.pkg / n).unlink()
        (self.pkg / sup.MANIFEST).unlink()
        with mock.patch.object(sup, "DATA_PRODUCT_SHA256", fdc.sha256(self.dp_dir / DP.name)), \
                mock.patch("sys.stdout"), mock.patch("sys.stderr"):
            self.assertEqual(sup.main(["build", "--data-product", str(self.dp_dir / DP.name), "--package", str(self.pkg)]), 0)
            out = sup.main(["check", "--data-product", str(self.dp_dir / DP.name), "--package", str(self.pkg)])
        self.assertEqual(out, 1)
        with mock.patch.object(sup, "DATA_PRODUCT_SHA256", fdc.sha256(self.dp_dir / DP.name)), \
                self.assertRaisesRegex(fdc.Stop, "S3"), mock.patch("sys.stdout"):
            sup.check(self.pkg, self.dp_dir / DP.name)

    def test_a_csv_that_is_not_the_data_products_matrix_refuses(self):
        # the data product's JSON says one thing and its recorded CSV another: only S2 can see it
        dpj = json.loads((self.dp_dir / DP.name).read_text())
        dpj["matrices"][sup.BLOCK][0][0] *= 1 + 1e-12
        (self.dp_dir / DP.name).write_text(json.dumps(dpj))
        with mock.patch.object(sup, "DATA_PRODUCT_SHA256", fdc.sha256(self.dp_dir / DP.name)), \
                self.assertRaisesRegex(fdc.Stop, "S2"), mock.patch("sys.stdout"):
            sup.check(self.pkg, self.dp_dir / DP.name)

    def test_a_second_reported_mark_or_a_departing_manifest_refuses(self):
        man = json.loads((self.pkg / sup.MANIFEST).read_text())
        man["files"][1]["reported"] = True
        (self.pkg / sup.MANIFEST).write_text(json.dumps(man))
        with self.assertRaisesRegex(fdc.Stop, "S4"), mock.patch("sys.stdout"):
            sup.check(self.pkg, self.dp_dir / DP.name)
        man["files"][1]["reported"] = False
        man["what"] = "something else"
        (self.pkg / sup.MANIFEST).write_text(json.dumps(man))
        with self.assertRaisesRegex(fdc.Stop, "S5"), mock.patch("sys.stdout"):
            sup.check(self.pkg, self.dp_dir / DP.name)

    def test_a_reported_file_that_is_not_covariance_csv_refuses(self):
        shutil.copy(self.pkg / "covariance-without-C_PL5D.csv", self.pkg / "covariance.csv")
        with self.assertRaisesRegex(fdc.Stop, "S4"), mock.patch("sys.stdout"):
            sup.check(self.pkg, self.dp_dir / DP.name)

    def test_a_readme_missing_a_digest_or_the_reported_mark_refuses(self):
        r = self.pkg / sup.README
        text = r.read_text()
        for broken in (text.replace("03babead4dff1bf19980319a867c9b830a5b7f85896792edc6f07a62c6e991c9", "03babead"),
                       text.replace("`covariance-reported.csv` is the reported matrix", "see the table")):
            r.write_text(broken)
            with self.assertRaisesRegex(fdc.Stop, "S6"), mock.patch("sys.stdout"):
                sup.check(self.pkg, self.dp_dir / DP.name)


if __name__ == "__main__":
    unittest.main()
