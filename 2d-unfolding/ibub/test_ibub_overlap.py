#!/usr/bin/env python3
"""Tests for ``ibub_overlap.py`` (IBUB-DECLARATION.md section 8). The clean phases read CLEAR, with exactly the
declared allowed pairs. Each of these stops: a write into a cov2d tree, an acked read that lands on another lane's
path, a write into the ibuchi root, a plain read of cov2d's tree, and an OUT_ROOT that is not this lane's.

Needs only the repository (the MSR and rpd tools it imports are read from it).
    cd 2d-unfolding/ibub && python -B -m unittest -v test_ibub_overlap
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ibub_overlap as ov  # noqa: E402


class Overlap(unittest.TestCase):
    def test_both_phases_are_clear_with_only_the_declared_allowances(self):
        for phase, n_allowed in (("run", 5), ("readout", 6)):
            rc, lines = ov.check(phase, ov.N_ROOT, ov.REPO)
            with self.subTest(phase=phase):
                self.assertEqual(rc, 0, "\n".join(lines))
                allowed = [ln for ln in lines if ln.startswith("OVERLAP ALLOWED")]
                self.assertEqual(len(allowed), n_allowed, "\n".join(allowed))
                self.assertTrue(all("read (cov2d-acked)" in ln or "(interpreter)" in ln for ln in allowed))

    def stops(self, phase="run", **patch):
        with mock.patch.multiple(ov, **patch):
            rc, lines = ov.check(phase, ov.N_ROOT, ov.REPO)
        self.assertEqual(rc, 3, "\n".join(lines))
        return [ln for ln in lines if ln.startswith("OVERLAP HIT")]

    def test_a_write_into_cov2ds_tree_stops(self):
        hits = self.stops(WRITES={"run": [ov.N_ROOT, f"{ov.O}/out/extra"], "readout": []})
        self.assertTrue(any("write" in h and "cov2d" in h for h in hits))

    def test_an_acked_read_on_another_lanes_path_stops(self):
        hits = self.stops(ACKED_RUN=ov.ACKED_RUN + ["/pscratch/sd/j/josephrb/rpd-reco-flux2-20261122/x"])
        self.assertTrue(any("rpd flux2 write root" in h for h in hits))

    def test_a_plain_read_of_cov2ds_tree_stops(self):
        hits = self.stops(READS_RUN=ov.READS_RUN + [f"{ov.O}/pseudo/G18/a/cells.npz"])
        self.assertTrue(any("ours read " in h for h in hits))

    def test_a_write_into_the_ibuchi_root_stops(self):
        self.stops(WRITES={"run": [ov.N_ROOT, "/pscratch/sd/j/josephrb/ibuchi-evloop-20261123/x"], "readout": []})

    def test_a_write_into_lr_p0s_root_stops(self):
        hits = self.stops(WRITES={"run": [ov.N_ROOT, "/pscratch/sd/j/josephrb/rpd-reco-p0-20261123/x"], "readout": []})
        self.assertTrue(any("rpd-reco P0" in h for h in hits))

    def test_a_write_under_an_msr_root_stops(self):
        self.stops(WRITES={"run": [ov.N_ROOT, "/pscratch/sd/j/josephrb/msr-b-20261123/x"], "readout": []})

    def test_it_runs_as_a_script(self):
        import subprocess
        r = subprocess.run([sys.executable, "-B", str(HERE / "ibub_overlap.py"), "run", ov.N_ROOT], capture_output=True,
                           text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("OVERLAP: CLEAR", r.stdout)

    def test_the_cli_refuses_another_out_root_or_phase(self):
        self.assertEqual(ov.main(["run", "/pscratch/sd/j/josephrb/other"]), 2)
        self.assertEqual(ov.main(["write", ov.N_ROOT]), 2)
        self.assertEqual(ov.main(["run", ov.N_ROOT]), 0)
        with self.assertRaises(ValueError):
            ov.ours("other", ov.N_ROOT)


if __name__ == "__main__":
    unittest.main()
