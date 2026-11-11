"""LL5D amendment A1b.1 (ll5d_ctl.py): the procedure controls' bitwise check against S1's committed products. Each rule
is tested in the direction it acts and the other: equal bytes PASS; one flipped ulp, a dtype change or a shape change
FAIL; a reference whose digest differs, or a missing file, is INVALID; the pins match the committed files.

    python3 -B nd-unfolding/tests/test_ll5d_ctl.py
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import numpy as np

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent
sys.path.insert(1, str(ND))

import fd_1b_inv as inv  # noqa: E402
import ll5d_b  # noqa: E402
import ll5d_ctl as ctl  # noqa: E402


def write_npz(path: Path, x: np.ndarray, **extra) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    np.savez(buf, xsec_flat=x, **extra)
    path.write_bytes(buf.getvalue())
    return hashlib.sha256(buf.getvalue()).hexdigest()


class Fixture(unittest.TestCase):
    """A temporary repository with four synthetic references and a products directory holding exact copies of their
    xsec_flat; REFERENCES is pointed at the synthetic files and their digests."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ll5d-ctl-")
        root = Path(self.tmp.name)
        self.repo, self.unf = root / "repo", root / "unfolds"
        rng = np.random.default_rng(7)
        self.x, refs = {}, {}
        for k, c in enumerate(ll5d_b.CONTROLS):
            x = rng.normal(size=48) * 10.0 ** k
            rel = f"s1/ref_{c}.npz"
            refs[c] = (rel, write_npz(self.repo / rel, x, shape=np.array([2, 24])))
            write_npz(self.unf / ll5d_b.product_name("data", "control", c), x.copy(), meta=np.array("{}"))
            self.x[c] = x
        self.patches = [mock.patch.object(ctl, "REFERENCES", refs), mock.patch.object(inv, "NOATIME_FLAG", 0)]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def product(self, c: str) -> Path:
        return self.unf / ll5d_b.product_name("data", "control", c)

    def run_main(self, out: Path, moved=()) -> int:
        """main(), with the atime sidecar fixed: a test host's plain reads (the flag patched to 0) can move atimes."""
        still = {"files": {}, "moved": list(moved)}
        with redirect_stdout(io.StringIO()), mock.patch.object(inv, "atime_check", lambda: still):
            return ctl.main(["--unfolds", str(self.unf), "--repo", str(self.repo), "--out", str(out)])


class Bitwise(Fixture):
    def test_equal_bytes_pass(self):
        rec = ctl.controls(self.unf, self.repo)
        self.assertEqual(rec["verdict"], "PASS")
        self.assertEqual(rec["failed"], [])
        self.assertEqual(sorted(rec["controls"]), sorted(ll5d_b.CONTROLS))
        for r in rec["controls"].values():
            self.assertTrue(r["equal"])
            self.assertEqual(r["elements_differing"], 0)

    def test_one_flipped_ulp_fails(self):
        """The director's REQUIRED case: one element moved by one ulp in one control reads FAIL."""
        x = self.x["Flux_0"].copy()
        x[17] = np.nextafter(x[17], np.inf)
        write_npz(self.product("Flux_0"), x)
        rec = ctl.controls(self.unf, self.repo)
        self.assertEqual(rec["verdict"], "FAIL")
        self.assertEqual(rec["failed"], ["Flux_0"])
        self.assertEqual(rec["controls"]["Flux_0"]["elements_differing"], 1)
        self.assertTrue(all(rec["controls"][c]["equal"] for c in ll5d_b.CONTROLS if c != "Flux_0"))

    def test_a_dtype_change_fails_even_with_equal_values(self):
        """The reference holds float32-exact values in float64 and the product the same values in float32: every value
        is equal, and only the dtype differs."""
        x64 = self.x["MaRES_0"].astype(np.float32).astype(np.float64)
        rel, _ = ctl.REFERENCES["MaRES_0"]
        sha = write_npz(self.repo / rel, x64)
        write_npz(self.product("MaRES_0"), x64.astype(np.float32))
        with mock.patch.dict(ctl.REFERENCES, {"MaRES_0": (rel, sha)}):
            rec = ctl.controls(self.unf, self.repo)
        self.assertEqual(rec["verdict"], "FAIL")
        self.assertFalse(rec["controls"]["MaRES_0"]["same_dtype"])
        self.assertEqual(rec["controls"]["MaRES_0"]["elements_differing"], 0)

    def test_a_shape_change_fails_with_the_same_bytes(self):
        write_npz(self.product("GEANT_Pion_0"), self.x["GEANT_Pion_0"].reshape(2, 24))
        rec = ctl.controls(self.unf, self.repo)
        self.assertEqual(rec["verdict"], "FAIL")
        self.assertFalse(rec["controls"]["GEANT_Pion_0"]["same_shape"])

    def test_the_comparison_is_of_xsec_flat_only(self):
        """Another array in the product (its meta) does not enter: the procedure's product is xsec_flat."""
        write_npz(self.product("setA_b1"), self.x["setA_b1"].copy(), meta=np.array('{"other": 1}'))
        self.assertEqual(ctl.controls(self.unf, self.repo)["verdict"], "PASS")


class Refusals(Fixture):
    def test_a_reference_digest_mismatch_is_invalid(self):
        rel, _ = ctl.REFERENCES["MaRES_0"]
        with mock.patch.dict(ctl.REFERENCES, {"MaRES_0": (rel, "0" * 64)}):
            with self.assertRaises(ctl.Refusal):
                ctl.controls(self.unf, self.repo)

    def test_a_missing_product_is_invalid(self):
        self.product("Flux_0").unlink()
        with self.assertRaises(ctl.Refusal):
            ctl.controls(self.unf, self.repo)

    def test_a_missing_reference_is_invalid(self):
        (self.repo / ctl.REFERENCES["setA_b1"][0]).unlink()
        with self.assertRaises(ctl.Refusal):
            ctl.controls(self.unf, self.repo)

    def test_the_references_must_be_exactly_the_declared_controls(self):
        three = dict(list(ctl.REFERENCES.items())[:3])
        with mock.patch.object(ctl, "REFERENCES", three):
            with self.assertRaises(ctl.Refusal):
                ctl.controls(self.unf, self.repo)


class ExitCodes(Fixture):
    def test_pass_fail_and_invalid_codes_and_records(self):
        out = Path(self.tmp.name) / "c1.json"
        self.assertEqual(self.run_main(out), 0)
        self.assertEqual(json.loads(out.read_text())["verdict"], "PASS")
        x = self.x["setA_b1"].copy()
        x[0] = np.nextafter(x[0], -np.inf)
        write_npz(self.product("setA_b1"), x)
        out2 = Path(self.tmp.name) / "c2.json"
        self.assertEqual(self.run_main(out2), ctl.RC_FAIL)
        self.assertEqual(json.loads(out2.read_text())["failed"], ["setA_b1"])
        self.product("setA_b1").unlink()
        out3 = Path(self.tmp.name) / "c3.json"
        self.assertEqual(self.run_main(out3), ctl.RC_INVALID)
        self.assertFalse(out3.exists())
        self.assertEqual(json.loads(out3.with_suffix(".invalid.json").read_text())["verdict"], "INVALID")

    def test_an_atime_move_ors_in_8(self):
        out = Path(self.tmp.name) / "c.json"
        self.assertEqual(self.run_main(out, moved=["x"]), ll5d_b.ll5d.ATIME_RC)
        self.assertEqual(json.loads(out.read_text())["atime"]["moved"], ["x"])

    def test_it_refuses_to_overwrite_its_record(self):
        out = Path(self.tmp.name) / "c.json"
        out.write_text("{}")
        with self.assertRaises(ctl.Refusal):
            self.run_main(out)


class NoAtime(Fixture):
    def test_every_read_goes_through_o_noatime(self):
        """Each of the eight files (four products, four references) is opened through fd_1b_inv.open_noatime, and no
        file under the fixture is opened for reading any other way."""
        via, plain = [], []
        real_noatime, real_open = inv.open_noatime, open

        def noatime(path):
            via.append(str(path))
            return real_noatime(path)

        def guard_open(file, mode="r", *args, **kw):
            if "r" in mode and str(file).startswith(self.tmp.name):
                plain.append(str(file))
            return real_open(file, mode, *args, **kw)

        with mock.patch.object(inv, "open_noatime", noatime), mock.patch("builtins.open", guard_open):
            ctl.controls(self.unf, self.repo)
        self.assertEqual(plain, [])
        self.assertEqual(len(via), 8)
        self.assertEqual(len(set(via)), 8)


class Pins(unittest.TestCase):
    def test_the_pins_are_the_committed_files_and_s1s_sha256sums(self):
        sums = {}
        for line in (REPO / ctl.S1_DIR / "SHA256SUMS").read_text().splitlines():
            h, _, name = line.partition("  ")
            sums[name.strip()] = h
        for c, (rel, want) in ctl.REFERENCES.items():
            p = REPO / rel
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), want, c)
            self.assertEqual(sums[Path(rel).name], want, c)
            with np.load(p, allow_pickle=False) as z:
                self.assertEqual((z["xsec_flat"].dtype.str, z["xsec_flat"].ndim), ("<f8", 1), c)

    def test_the_set_a_reference_is_replica_1_at_jitter_101(self):
        rel, _ = ctl.REFERENCES["setA_b1"]
        with np.load(REPO / rel, allow_pickle=False) as z:
            m = json.loads(str(z["meta"]))
        self.assertEqual((m["construction"], m["bootstrap_seed"], m["jitter_seed"]), ("data", 1, 101))

    def test_each_universe_reference_is_that_universe(self):
        for c in ("MaRES_0", "Flux_0", "GEANT_Pion_0"):
            rel, _ = ctl.REFERENCES[c]
            with np.load(REPO / rel, allow_pickle=False) as z:
                m = json.loads(str(z["meta"]))
            self.assertEqual(m["universe"], c.rpartition("_")[0] + ":" + c.rpartition("_")[2], c)


if __name__ == "__main__":
    unittest.main(verbosity=1)
