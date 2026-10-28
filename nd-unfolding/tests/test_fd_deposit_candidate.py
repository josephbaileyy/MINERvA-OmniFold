"""Controls for fd_deposit_candidate (fd/deposit-candidate/README.md), on the committed data product and Stage G
readout, which are read, never written.

* End to end: build then check passes P0-P6; the covariance and correlation CSVs are the data product's files byte for
  byte; the committed package is what build writes.
* Planted defects: each is re-stamped in deposit.json's files_sha256 (or re-pinned) so that it reaches the control it
  targets, and each test asserts that control's clause in the STOP.
* Invocation: as written (-I -B, cwd outside nd-unfolding).
With DEPOSIT_TARGETED_ONLY=1 the committed-bytes test is skipped: every file embeds the code's sha256, so that test
fails on any source change, and the mutant run (receipts-deposit/mutants.py) must count only the targeted kills."""
import csv
import os
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
import fd_deposit_candidate as D  # noqa: E402

REPO = ND.parent
FD = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
DP = FD / "data-product/fd_data_product.json"
GR = FD / "readout/fd_g_readout.json"
PKG = FD / "deposit-candidate"


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch("sys.stdout", out), mock.patch("sys.stderr", err):
        rc = D.main(argv)
    return rc, out.getvalue(), err.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.pkg = self.tmp / "pkg"
        rc, _, err = run(["build", "--data-product", str(DP), "--g-readout", str(GR), "--out-dir", str(self.pkg)])
        self.assertEqual(rc, 0, err)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def check(self, dp=DP, gr=GR):
        return run(["check", "--package", str(self.pkg), "--data-product", str(dp), "--g-readout", str(gr)])

    def restamp(self, name):
        js = json.loads((self.pkg / "deposit.json").read_text())
        js["files_sha256"][name] = hashlib.sha256((self.pkg / name).read_bytes()).hexdigest()
        (self.pkg / "deposit.json").write_text(json.dumps(js, indent=1) + "\n")

    def edit_csv(self, name, row, col, fn):
        rows = list(csv.reader(io.StringIO((self.pkg / name).read_text())))
        rows[row][col] = fn(rows[row][col])
        buf = io.StringIO()
        csv.writer(buf, lineterminator="\n").writerows(rows)
        (self.pkg / name).write_text(buf.getvalue())
        self.restamp(name)

    def edit_json(self, name, fn):
        p = self.pkg / name
        js = json.loads(p.read_text())
        fn(js)
        p.write_text(json.dumps(js, indent=1) + "\n")

    def edit_reference(self, fn):
        p = self.pkg / D.REFERENCE
        js = json.loads(p.read_text())
        fn(js)
        p.write_text(json.dumps(js, indent=1) + "\n")

    def assertStops(self, clause, **kw):
        rc, _, err = self.check(**kw)
        self.assertEqual(rc, 1)
        self.assertIn(clause, err)


class EndToEnd(Base):
    def test_build_then_check_passes_every_control(self):
        rc, out, err = self.check()
        self.assertEqual(rc, 0, err)
        res = json.loads(out[out.index('{\n "controls'):])
        self.assertEqual(res["controls_passed"], ["P0", "P1", "P2", "P3", "P4", "P6", "P5", "P7"])
        self.assertEqual(len(res["chi2"]), 10)
        self.assertLessEqual(res["chi2_worst_rel_diff"], D.CHI2_TOL)

    def test_the_matrix_csvs_are_the_data_products_files_byte_for_byte(self):
        for mine, theirs in (("covariance.csv", "fd_data_product_C_total_plus_C_resp.csv"),
                             ("correlation.csv", "fd_data_product_corr_C_total_plus_C_resp.csv")):
            self.assertEqual((self.pkg / mine).read_bytes(), (FD / "data-product" / theirs).read_bytes())

    @unittest.skipIf(os.environ.get("DEPOSIT_TARGETED_ONLY") == "1", "targeted-only mutant run")
    def test_the_committed_package_is_what_build_writes(self):
        for n in (*D.FILES, D.REFERENCE):
            self.assertEqual((PKG / n).read_bytes(), (self.pkg / n).read_bytes(), n)

    def test_the_measurement_does_not_name_the_reference_file(self):
        js = json.loads((self.pkg / "deposit.json").read_text())
        self.assertNotIn(D.REFERENCE, js["files_sha256"])
        self.assertNotIn(D.REFERENCE, (self.pkg / "deposit.json").read_text())

    def test_the_reference_holds_five_predictions_and_gibuus_eight_cells(self):
        js = json.loads((self.pkg / D.REFERENCE).read_text())
        self.assertEqual(js["label"], "reference predictions used for the paper's chi2; not part of the measurement")
        self.assertEqual([p["name"] for p in js["predictions"]],
                         ["genie_cv", "genie_mec", "nuwro", "gibuu", "mnvtune_v1"])
        self.assertEqual({p["name"]: len(p["cells"]) for p in js["predictions"]},
                         {"genie_cv": 16, "genie_mec": 16, "nuwro": 16, "gibuu": 8, "mnvtune_v1": 16})

    def test_the_gibuu_subset_is_r00_r03_and_r08_r11(self):
        js = json.loads((self.pkg / "deposit.json").read_text())
        self.assertEqual(js["gibuu_subset"], ["R00", "R01", "R02", "R03", "R08", "R09", "R10", "R11"])

    def test_the_unreported_boxes_are_2_6_10_14(self):
        js = json.loads((self.pkg / "deposit.json").read_text())
        self.assertEqual([u["h2_box"] for u in js["unreported_h2_boxes"]], [2, 6, 10, 14])

    def test_the_measurement_checks_alone_without_the_reference_or_the_readout(self):
        (self.pkg / D.REFERENCE).unlink()
        rc, out, err = run(["check", "--package", str(self.pkg), "--data-product", str(DP), "--measurement-only"])
        self.assertEqual(rc, 0, err)
        res = json.loads(out[out.index('{\n "controls'):])
        self.assertEqual(res["controls_passed"], ["P0", "P1", "P2", "P3", "P4", "P7"])
        self.assertIn("measurement only", res["mode"])

    def test_measurement_only_still_refuses_a_measurement_defect(self):
        self.edit_csv("covariance.csv", 3, 5, lambda x: repr(float(np.nextafter(float(x), np.inf))))
        rc, _, err = run(["check", "--package", str(self.pkg), "--data-product", str(DP), "--measurement-only"])
        self.assertEqual(rc, 1)
        self.assertIn("the covariance from covariance.csv and deposit.json is the data product's", err)

    def test_measurement_only_refuses_a_descriptive_defect(self):
        self.edit_json("deposit.json", lambda js: js["labels"].update(status="DEPOSITED"))
        rc, _, err = run(["check", "--package", str(self.pkg), "--data-product", str(DP), "--measurement-only"])
        self.assertEqual(rc, 1)
        self.assertIn("every field of deposit.json (but code_sha256) is what build writes", err)

    def test_build_refuses_to_overwrite(self):
        rc, _, err = run(["build", "--data-product", str(DP), "--g-readout", str(GR), "--out-dir", str(self.pkg)])
        self.assertEqual(rc, 1)
        self.assertIn("no overwrite", err)


class Defects(Base):
    def test_p0_an_unstamped_edit(self):
        p = self.pkg / "covariance.csv"
        p.write_text(p.read_text().replace("R00,", "R00 ,", 1))
        self.assertStops("covariance.csv's sha256 is deposit.json's")

    def test_p0_another_data_product(self):
        alt = self.tmp / "dp.json"
        alt.write_text(DP.read_text() + " ")
        self.assertStops("data_product sha256 is the pin", dp=alt)

    def test_p1_a_box_edge(self):
        self.edit_csv("cells.csv", 1, 3, lambda x: "0.8")          # R00's pt_hi 0.7 -> 0.8
        self.assertStops("R00's box and H2 boxes are the data product's")

    def test_p1_two_rows_swapped(self):
        rows = (self.pkg / "cells.csv").read_text().splitlines(keepends=True)
        rows[1], rows[2] = rows[2], rows[1]
        (self.pkg / "cells.csv").write_text("".join(rows))
        self.restamp("cells.csv")
        self.assertStops("list R00-R15 in order")

    def test_p1_a_box_wider_than_its_h2_boxes(self):
        dp = json.loads(DP.read_text())
        dp["cells"][0]["box"]["pt"] = [0.0, 0.8]                  # R00's boxes 0 and 1 end at p_T 0.7
        alt = self.tmp / "dp.json"
        alt.write_text(json.dumps(dp))
        shutil.rmtree(self.pkg)
        with mock.patch.dict(D.PINS, {"data_product": D.sha256(alt)}):
            self.assertEqual(run(["build", "--data-product", str(alt), "--g-readout", str(GR), "--out-dir",
                                  str(self.pkg)])[0], 0)
            self.assertStops("R00's box is exactly the union of its H2 boxes", dp=alt)

    def test_p1_boxes_whose_bounding_box_is_the_cell_but_that_leave_a_hole(self):
        dp = json.loads(DP.read_text())
        assert dp["cells"][9]["h2_boxes"] == [17, 19, 21, 23]
        dp["cells"][9]["h2_boxes"] = [17, 23]                  # their bounding box is still R09's box
        alt = self.tmp / "dp.json"
        alt.write_text(json.dumps(dp))
        shutil.rmtree(self.pkg)
        with mock.patch.dict(D.PINS, {"data_product": D.sha256(alt)}):
            self.assertEqual(run(["build", "--data-product", str(alt), "--g-readout", str(GR), "--out-dir",
                                  str(self.pkg)])[0], 0)
            self.assertStops("R09's box is exactly the union of its H2 boxes", dp=alt)

    def test_p1_a_box_that_is_not_its_h2_boxes(self):
        with mock.patch.dict(D.H2_EDGES, {"W": [0.0, 1.4, 100.0]}):
            self.assertStops("is exactly the union of its H2 boxes")

    def test_p2_one_ulp_in_one_covariance_entry(self):
        self.edit_csv("covariance.csv", 3, 5, lambda x: repr(float(np.nextafter(float(x), np.inf))))
        self.assertStops("the covariance from covariance.csv and deposit.json is the data product's")

    def test_p2_one_ulp_in_f(self):
        self.edit_csv("cells.csv", 5, 13, lambda x: repr(float(np.nextafter(float(x), np.inf))))
        self.assertStops("f from cells.csv and deposit.json is the data product's")

    def test_p2_one_ulp_in_the_correlation(self):
        self.edit_csv("correlation.csv", 2, 7, lambda x: repr(float(np.nextafter(float(x), -np.inf))))
        self.assertStops("the correlation from correlation.csv and deposit.json is the data product's")

    def test_p3_an_asymmetric_reported_matrix(self):
        dp = json.loads(DP.read_text())
        dp["matrices"]["C_total_plus_C_resp"][2][9] *= 1 + 1e-9
        alt = self.tmp / "dp.json"
        alt.write_text(json.dumps(dp))
        shutil.rmtree(self.pkg)
        with mock.patch.dict(D.PINS, {"data_product": D.sha256(alt)}):
            self.assertEqual(run(["build", "--data-product", str(alt), "--g-readout", str(GR), "--out-dir",
                                  str(self.pkg)])[0], 0)
            self.assertStops("is symmetric to 1e-12 of its largest entry", dp=alt)

    def test_p3_the_sigma_column(self):
        self.edit_csv("cells.csv", 4, 14, lambda x: repr(float(x) * 1.001))
        self.assertStops("sigma in cells.csv and deposit.json is sqrt(diag)")

    def test_p4_a_gibuu_flag(self):
        self.edit_csv("cells.csv", 5, 12, lambda x: "1")           # R04 has p_parallel 4.5-60
        self.assertStops("GiBUU's subset is the eight cells with p_parallel's upper edge 4.5 GeV/c")

    def test_p4_stage_gs_gibuu_cells_differ(self):
        gr = json.loads(GR.read_text())
        gib = next(p for p in gr["predictions"] if p["name"] == "gibuu")
        gib["cells"] = [c if c != "R11" else "R12" for c in gib["cells"]]
        alt = self.tmp / "gr.json"
        alt.write_text(json.dumps(gr))
        shutil.rmtree(self.pkg)
        with mock.patch.dict(D.PINS, {"g_readout": D.sha256(alt)}):
            self.assertEqual(run(["build", "--data-product", str(DP), "--g-readout", str(alt), "--out-dir",
                                  str(self.pkg)])[0], 0)
            self.assertStops("GiBUU's subset is Stage G's eight cells", gr=alt)

    def test_p5_a_stage_g_chi2_off_by_more_than_the_tolerance(self):
        gr = json.loads(GR.read_text())
        gr["predictions"][2]["shape_only"]["chi2"] *= 1 + 1e-8
        alt = self.tmp / "gr.json"
        alt.write_text(json.dumps(gr))
        shutil.rmtree(self.pkg)
        with mock.patch.dict(D.PINS, {"g_readout": D.sha256(alt)}):
            self.assertEqual(run(["build", "--data-product", str(DP), "--g-readout", str(alt), "--out-dir",
                                  str(self.pkg)])[0], 0)
            self.assertStops("nuwro shape_only chi2 from the package is Stage G's", gr=alt)

    def test_p6_a_reference_chi2_that_is_not_the_readouts(self):
        self.edit_reference(lambda js: js["predictions"][2]["stage_g"]["total"].update(chi2=1.0))
        self.assertStops("nuwro: Stage G's chi2 and ndf are the readout's")

    def test_p6_one_ulp_in_a_reference_g(self):
        def f(js):
            g = js["predictions"][1]["g_cm2_per_nucleon"]
            g[6] = float(np.nextafter(g[6], np.inf))
        self.edit_reference(f)
        self.assertStops("genie_mec: cells, g and sigma_Vg_over_f are the readout's")

    def test_p6_one_ulp_in_a_reference_v_g(self):
        def f(js):
            v = js["predictions"][3]["V_g_cm4_per_nucleon2"]
            v[2] = float(np.nextafter(v[2], -np.inf))
        self.edit_reference(f)
        self.assertStops("gibuu: V_g is (sigma_Vg_over_f f)^2")

    def test_p6_a_source_digest(self):
        self.edit_reference(lambda js: js["predictions"][0].update(source_sha256="0" * 64))
        self.assertStops("genie_cv: source, sha256 and label are fd_g_compare's")

    def test_p6_two_predictions_swapped(self):
        def f(js):
            p = js["predictions"]
            p[0], p[1] = p[1], p[0]
        self.edit_reference(f)
        self.assertStops("it holds Stage G's five predictions, in order")

    def test_p6_the_label_that_keeps_it_apart(self):
        self.edit_reference(lambda js: js.update(label="the measurement"))
        self.assertStops("labelled apart from the measurement")

    def test_p6_gibuu_on_sixteen_cells(self):
        gr = json.loads(GR.read_text())
        self.edit_reference(lambda js: js["predictions"][3].update(cells=gr["cells"]))
        self.assertStops("gibuu: cells, g and sigma_Vg_over_f are the readout's")

    def test_p6_a_source_that_is_not_fd_g_compares(self):
        spec = [dict(s) for s in D.G.PREDICTIONS]
        spec[0]["sha256"] = "0" * 64
        with mock.patch.object(D.G, "PREDICTIONS", tuple(spec)):
            self.assertStops("genie_cv: source, sha256 and label are fd_g_compare's")

    def test_p7_the_status(self):
        def f(js):
            js["labels"]["status"] = "DEPOSITED, DOI 10.0000/x"
        self.edit_json("deposit.json", f)
        self.assertStops("every field of deposit.json (but code_sha256) is what build writes")

    def test_p7_a_unit(self):
        self.edit_json("deposit.json", lambda js: js["axes"][0].update(unit="MeV/c"))
        self.assertStops("every field of deposit.json (but code_sha256) is what build writes")

    def test_p7_the_covariance_name(self):
        self.edit_json("deposit.json", lambda js: js.update(covariance_of="C_total"))
        self.assertStops("every field of deposit.json (but code_sha256) is what build writes")

    def test_p7_not_citable_for_removed(self):
        self.edit_json("deposit.json", lambda js: js["labels"].pop("not_citable_for"))
        self.assertStops("every field of deposit.json (but code_sha256) is what build writes")

    def test_p7_the_gibuu_domain_label(self):
        self.edit_reference(lambda js: js["predictions"][3].update(domain="all sixteen cells"))
        self.assertStops("every field of predictions-reference.json (but code_sha256) is what build writes")

    def test_p7_the_reference_status(self):
        self.edit_reference(lambda js: js.update(status="part of the measurement"))
        self.assertStops("every field of predictions-reference.json (but code_sha256) is what build writes")

    def test_p7_a_stage_g_matrix_name(self):
        self.edit_reference(lambda js: js["predictions"][0]["stage_g"]["total"].update(matrix="C_total"))
        self.assertStops("every field of predictions-reference.json (but code_sha256) is what build writes")

    def test_p7_a_csv_byte_that_parses_the_same(self):
        p = self.pkg / "covariance.csv"
        p.write_text(p.read_text().replace("\n", "\r\n", 1))
        self.restamp("covariance.csv")
        self.assertStops("covariance.csv is what build writes, byte for byte")

    def test_p0_the_reference_file_missing(self):
        (self.pkg / D.REFERENCE).unlink()
        self.assertStops("predictions-reference.json exists")

    def test_p5_stage_gs_f_differs(self):
        gr = json.loads(GR.read_text())
        gr["predictions"][0]["f"][3] = float(np.nextafter(gr["predictions"][0]["f"][3], np.inf))
        alt = self.tmp / "gr.json"
        alt.write_text(json.dumps(gr))
        shutil.rmtree(self.pkg)
        with mock.patch.dict(D.PINS, {"g_readout": D.sha256(alt)}):
            self.assertEqual(run(["build", "--data-product", str(DP), "--g-readout", str(alt), "--out-dir",
                                  str(self.pkg)])[0], 0)
            self.assertStops("Stage G's f is the package's", gr=alt)


class Invocation(unittest.TestCase):
    def test_as_written(self):
        with tempfile.TemporaryDirectory() as t:
            p = subprocess.run([sys.executable, "-I", "-B", str(ND / "fd_deposit_candidate.py"), "check", "--package",
                                str(PKG), "--data-product", str(DP), "--g-readout", str(GR)],
                               cwd=t, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn('"controls_passed"', p.stdout)


if __name__ == "__main__":
    unittest.main()
