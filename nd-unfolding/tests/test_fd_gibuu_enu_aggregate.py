"""Controls for fd_gibuu_enu_aggregate, on the committed GiBUU E_nu coverage readout.

* Committed: each written share is recomputed here from the readout's by_pz keys, and asserted to the percentages
  the director's request quotes (2 dp); the committed output is byte-identical to a fresh run.
* Planted defects: one per check of C0-C3, each refusing with its own clause and nothing written.
* Invocation: as written (-I -B, cwd outside nd-unfolding), it writes the committed bytes."""
import copy
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
import fd_gibuu_enu_aggregate as A  # noqa: E402

REPO = ND.parent
READOUT = REPO / "nd-unfolding/pv-ladder/readouts/gibuu_enu_coverage.json"
OUT = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_gibuu_enu_aggregate.json"
PIN = "9ee26883e32e85cd72e083022ef4c42440370665b17bdec0c272596f9650813c"
# percentages, 2 dp: (in-PS share at 4.5-60, its E_nu > 20 share, the 1.5-4.5 band's E_nu > 20 share)
QUOTED = {"genie_cv": (51.15, 11.71, 0.83), "nuwro": (51.55, 12.59, 0.77)}


def readout():
    return json.loads(READOUT.read_text())


def recompute(g):
    hi = [b for b in g["by_pz"] if b["pz"][0] >= 4.5]
    s = sum(b["share_of_in_ps"] for b in hi)
    return s, sum(b["share_of_in_ps"] * b["share_E_gt_20"] for b in hi) / s


def run_on(r, out: Path, pin=None):
    src = out.parent / "readout.json"
    src.write_text(json.dumps(r))
    pin = pin or hashlib.sha256(src.read_bytes()).hexdigest()
    so, se = io.StringIO(), io.StringIO()
    with redirect_stdout(so), redirect_stderr(se):
        rc = A.run(A.build_args(["--readout", str(src), "--out", str(out)]), pin=pin)
    return rc, so.getvalue() + se.getvalue()


class Committed(unittest.TestCase):
    def setUp(self):
        self.r = readout()
        self.out = json.loads(OUT.read_text())

    def test_pins(self):
        self.assertEqual(hashlib.sha256(READOUT.read_bytes()).hexdigest(), PIN)
        self.assertEqual(A.PIN, PIN)
        self.assertEqual(self.out["inputs_sha256"], {"gibuu_enu_coverage": PIN})
        self.assertTrue(self.out["labels"]["source"].startswith("nd-unfolding/pv-ladder/readouts/gibuu_enu_coverage.json,"))
        self.assertEqual(self.out["code_sha256"]["fd_gibuu_enu_aggregate.py"],
                         hashlib.sha256((ND / "fd_gibuu_enu_aggregate.py").read_bytes()).hexdigest())

    def test_shares_from_keys(self):
        for name, (s_pct, e_pct, low_pct) in QUOTED.items():
            g, o = self.r["generators"][name], self.out["generators"][name]
            s, e = recompute(g)
            self.assertAlmostEqual(o["pz_4.5_60"]["share_of_in_ps"], s, delta=1e-15)
            self.assertAlmostEqual(o["pz_4.5_60"]["share_E_gt_20"], e, delta=1e-15)
            self.assertEqual(o["pz_1.5_4.5"]["share_of_in_ps"], g["by_pz"][0]["share_of_in_ps"])
            self.assertEqual(o["pz_1.5_4.5"]["share_E_gt_20"], g["by_pz"][0]["share_E_gt_20"])
            self.assertEqual(round(100 * o["pz_4.5_60"]["share_of_in_ps"], 2), s_pct)
            self.assertEqual(round(100 * o["pz_4.5_60"]["share_E_gt_20"], 2), e_pct)
            self.assertEqual(round(100 * o["pz_1.5_4.5"]["share_E_gt_20"], 2), low_pct)
            self.assertEqual(o["pz_4.5_60"]["bands"], [[4.5, 6.0], [6.0, 10.0], [10.0, 20.0], [20.0, 60.0]])
            self.assertEqual(o["pz_1.5_4.5"]["keys"], [f"generators.{name}.by_pz[0].share_of_in_ps",
                                                       f"generators.{name}.by_pz[0].share_E_gt_20"])
            self.assertEqual(o["pz_4.5_60"]["keys"], [f"generators.{name}.by_pz[{i}].{k}" for i in (1, 2, 3, 4)
                                                      for k in ("share_of_in_ps", "share_E_gt_20")])
            self.assertEqual(o["generation_range_gev"], g["generation_range_gev"])

    def test_labels(self):
        L = self.out["labels"]
        self.assertEqual(self.out["schema"], "fd-gibuu-enu-aggregate/1")
        self.assertTrue(L["not"].startswith("not a GiBUU number"))
        self.assertIn("GENIE CV's and NuWro's share", L["what"])
        self.assertIn("GiBUU 2019's sample, which stops at E_nu = 20 GeV", L["what"])
        self.assertIn("FD-DIRECTOR-RULINGS.md section 5", L["for"])

    def test_fresh_run_is_committed_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "o.json"
            so = io.StringIO()
            with redirect_stdout(so):
                rc = A.run(A.build_args(["--out", str(out)]))
            self.assertEqual(rc, 0)
            self.assertEqual(out.read_bytes(), OUT.read_bytes())


def plant_digest(r):
    return r, "0" * 64


def plant(path, value):
    def f(r):
        r = copy.deepcopy(r)
        *head, last = path
        node = r
        for k in head:
            node = node[k]
        node[last] = value(node[last]) if callable(value) else value
        return r, None
    return f


G = ("generators", "genie_cv")
DEFECTS = [
    ("C0: readout sha256 is the pin", plant_digest),
    ("C0: schema gibuu-enu-coverage/1", plant(("schema",), "gibuu-enu-coverage/2")),
    ("C0: e_cut_gev 20.0", plant(("e_cut_gev",), 10.0)),
    ("C0: generators", plant(("generators", "gibuu"), {})),
    ("C1: genie_cv: bands tile 1.5-60.0", plant(G + ("by_pz", 2, "pz"), [6.5, 10.0])),
    ("C1: genie_cv: 4.5 is an edge and 1.5-4.5 is one band",
     plant(G + ("by_pz",), lambda b: [{**b[0], "pz": [1.5, 3.0]}, {**b[1], "pz": [3.0, 6.0]}] + b[2:])),
    ("C2: nuwro: share_of_in_ps sums to 1", plant(("generators", "nuwro", "by_pz", 1, "share_of_in_ps"),
                                                    lambda v: v + 1e-6)),
    ("C2: genie_cv: n_events sum to n_in_ps", plant(G + ("n_in_ps",), lambda v: v + 1)),
    ("C3: genie_cv: bands recombine to share_E_gt_20_all_in_ps",
     plant(G + ("by_pz", 3, "share_E_gt_20"), lambda v: v + 1e-6)),
]


class Planted(unittest.TestCase):
    def test_each_refuses(self):
        for clause, f in DEFECTS:
            with self.subTest(clause), tempfile.TemporaryDirectory() as d:
                r, pin = f(readout())
                out = Path(d) / "o.json"
                rc, text = run_on(r, out, pin)
                self.assertEqual(rc, 1, text)
                self.assertIn(f"REFUSED: {clause}", text)
                self.assertFalse(out.exists())

    def test_unplanted_passes(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "o.json"
            rc, text = run_on(readout(), out)
            self.assertEqual(rc, 0, text)
            self.assertNotIn("FAIL", text)
            self.assertEqual(text.count("PASS"), 4 + 2 * 5)


class Invocation(unittest.TestCase):
    def test_as_written(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "o.json"
            p = subprocess.run([sys.executable, "-I", "-B", str(ND / "fd_gibuu_enu_aggregate.py"), "--out", str(out)],
                               cwd=d, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(out.read_bytes(), OUT.read_bytes())


if __name__ == "__main__":
    unittest.main()
