"""Production pin audit for covfix_p0: the declared sha256 values, and that every committed pinned input exists with
its pinned bytes. Reads (hashes) the committed records; runs no P0 reading on them.

  python3 -B -m unittest -v test_covfix_p0_pins.py
"""
from __future__ import annotations

import unittest

import covfix_p0 as p0


class Pins(unittest.TestCase):
    def test_declared_shas(self):
        self.assertEqual(p0.Q_REP_SHA, "ff66b91d6d2c574a1786b057ce7566e8ed7184700a45b989fa41ae0eb8cb0295")
        self.assertEqual(p0.C_MODEL_SHA, "11fe68188bd31a35103f5eb4708bd6a7cdab8965164680caa6671c509dcd3470")
        self.assertEqual(p0.G2R_SHA, {"AR23": "c060cb40232e0112ec440951f94841e87fc98b542a165eed2c8242898508a70a",
                                      "G18": "55ad7cc4faa4680b49391a9d68f52fcaa707150bd1300915063d66a16be9bfbe"})

    def test_committed_inputs_match(self):
        for k, (path, want) in p0.PINS.items():
            with self.subTest(k):
                self.assertTrue(path.is_file(), k)
                self.assertEqual(p0.sha256(path), want, k)


if __name__ == "__main__":
    unittest.main()
