"""Tests for c2_corr_figure.py on a synthetic record. run: python3 -I -B test_c2_corr_figure.py"""
import hashlib
import importlib.util
import json
import os
import shutil
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("c2_corr_figure", os.path.join(HERE, "c2_corr_figure.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def record(**over):
    rec = {"status": "OK", "controls": {"C-PAIR": {"pass": True}}, "c2_eff_controls": {"C-QR": {"pass": True}},
           "figure_spectra": {k: [float(x) for x in np.logspace(-80 - i, -89 - i, 205)]
                              for i, k in enumerate(("C_IBU_K10", "C_OF", "StatOnly"))}}
    rec.update(over)
    return rec


class Figure(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="c2corrfig-")

    def tearDown(self):
        shutil.rmtree(self.d)

    def write(self, rec):
        p = os.path.join(self.d, "rec.json")
        b = json.dumps(rec).encode()
        open(p, "wb").write(b)
        return p, hashlib.sha256(b).hexdigest()

    def test_legend_strings_are_the_directors(self):
        self.assertEqual([s[1] for s in m.SERIES], ["IBU, ten iterations (same bootstrap draws)",
                                                    "OmniFold (statistical covariance)",
                                                    "MINERvA published statistical covariance"])
        self.assertNotIn("StatOnly", " ".join(s[1] for s in m.SERIES))

    def test_note_series_identities(self):
        style = {s[0]: (s[2], s[3]) for s in m.SERIES}
        self.assertEqual(style["C_OF"], ("#FF0000", "-"))
        self.assertEqual(style["StatOnly"], ("#000000", "--"))

    def test_plots_the_record_values_unchanged(self):
        rec = record()
        p, sha = self.write(rec)
        loaded = m.load(p, sha)
        fig = m.draw(loaded, os.path.join(self.d, "f.pdf"), keep=True)
        lines = fig.axes[0].get_lines()
        self.assertEqual(len(lines), 3)
        for line, (key, label, *_rest) in zip(lines, m.SERIES):
            self.assertEqual(line.get_label(), label)
            self.assertEqual(list(line.get_ydata()), rec["figure_spectra"][key])
            self.assertEqual(list(line.get_xdata()), list(range(1, 206)))
        self.assertEqual([t.get_text() for t in fig.axes[0].get_legend().get_texts()], [s[1] for s in m.SERIES])

    def test_pdf_is_deterministic(self):
        p, sha = self.write(record())
        rec = m.load(p, sha)
        a, b = os.path.join(self.d, "a.pdf"), os.path.join(self.d, "b.pdf")
        m.draw(rec, a)
        m.draw(rec, b)
        self.assertEqual(open(a, "rb").read(), open(b, "rb").read())
        self.assertEqual(open(a, "rb").read(5), b"%PDF-")

    def test_wrong_sha_refuses(self):
        p, sha = self.write(record())
        with self.assertRaisesRegex(m.Refused, "sha256"):
            m.load(p, "0" * 64)

    def test_failed_control_refuses(self):
        p, sha = self.write(record(controls={"C-PAIR": {"pass": False}}))
        with self.assertRaisesRegex(m.Refused, "control"):
            m.load(p, sha)

    def test_stop_status_refuses(self):
        p, sha = self.write(record(status="STOP"))
        with self.assertRaisesRegex(m.Refused, "status"):
            m.load(p, sha)

    def test_unsorted_or_short_spectrum_refuses(self):
        rec = record()
        rec["figure_spectra"]["C_OF"][10], rec["figure_spectra"]["C_OF"][11] = \
            rec["figure_spectra"]["C_OF"][11], rec["figure_spectra"]["C_OF"][10]
        p, sha = self.write(rec)
        with self.assertRaisesRegex(m.Refused, "descending"):
            m.load(p, sha)
        rec = record()
        rec["figure_spectra"]["StatOnly"] = rec["figure_spectra"]["StatOnly"][:204]
        p, sha = self.write(rec)
        with self.assertRaisesRegex(m.Refused, "205"):
            m.load(p, sha)

    def test_nonpositive_eigenvalue_refuses(self):
        rec = record()
        rec["figure_spectra"]["C_IBU_K10"][-1] = 0.0
        p, sha = self.write(rec)
        with self.assertRaisesRegex(m.Refused, "non-positive"):
            m.load(p, sha)

    def test_main_refuses_existing_output(self):
        out = os.path.join(self.d, "x.pdf")
        open(out, "w").close()
        self.assertEqual(m.main(["--out", out]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
