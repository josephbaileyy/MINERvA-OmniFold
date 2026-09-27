"""Controls for s5p_pairdiff.key_of: products pair by their pseudo seed; a trace whose meta records
pseudo_seed null (or none at all) pairs by order."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5p_pairdiff as pd  # noqa: E402


class Tests(unittest.TestCase):
    def test_key_of(self):
        with tempfile.TemporaryDirectory() as d:
            a, b, c = (Path(d) / n for n in ("a.npz", "b.npz", "c.npz"))
            np.savez(a, xsec_flat=np.ones(2), meta=json.dumps({"pseudo_seed": 7}))
            np.savez(b, xsec_flat=np.ones(2), meta=json.dumps({"pseudo_seed": None}))
            np.savez(c, xsec_flat=np.ones(2))
            self.assertEqual(pd.key_of(str(a)), 7)
            self.assertEqual(pd.key_of(str(b)), str(b))
            self.assertEqual(pd.key_of(str(c)), str(c))


if __name__ == "__main__":
    unittest.main()
