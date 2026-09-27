"""Controls for s5p_alt_ratios: a 5D prediction built as a product of a (pT, p_parallel, E_avail) shape and a
(q3, W) shape gives back exactly the 3D shape ratio s5e_deform.ratio_from_contents gives on the 3D contents."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5e_deform as sd  # noqa: E402
import s5p_alt_ratios as sa  # noqa: E402

EDGES = {"pt": [0, 1, 3.0], "pz": [0, 2, 3, 5.0], "eavail": [0, 0.5, 2.0], "q3": [0, 1, 2.0], "W": [0, 1.5, 4.0]}


def write(path, x):
    np.savez(path, xsec_flat=x.ravel(), **{f"edges_{a}": np.asarray(e, float) for a, e in EDGES.items()})


class Tests(unittest.TestCase):
    def test_marginal_ratio_equals_the_3d_ratio(self):
        rng = np.random.default_rng(0)
        a3, b3 = rng.uniform(0.5, 2, (2, 3, 2)), rng.uniform(0.5, 2, (2, 3, 2))
        qw = rng.uniform(0.5, 2, (2, 2))
        with tempfile.TemporaryDirectory() as d:
            write(Path(d) / "n.npz", np.einsum("abc,de->abcde", a3, qw))
            write(Path(d) / "m.npz", np.einsum("abc,de->abcde", b3, qw))
            self.assertEqual(sa.main(["--kind", "pt_pz_eavail", "--numerator", f"{d}/n.npz", "--denominator", f"{d}/m.npz",
                                      "--label", "t", "--out", f"{d}/r.json"]), 0)
            got = np.asarray(json.loads((Path(d) / "r.json").read_text())["shape_ratio"])
        vol = np.einsum("a,b,c->abc", *[np.diff(EDGES[k]) for k in ("pt", "pz", "eavail")])
        want, _ = sd.ratio_from_contents(a3, b3, vol)
        np.testing.assert_allclose(got, want.ravel(), rtol=1e-12)


if __name__ == "__main__":
    unittest.main()
