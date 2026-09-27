"""Controls for s5p_production: every null's batches cover exactly its declared seed range once; power tables
carry the alternative; overlapping seed ranges are refused; each calibration queue alternates controller and
wait lines and ends with a stop assertion; the design's calibration counts come from the controllers."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5p_production as sp  # noqa: E402


def spec(base1=1220000):
    return {"ns": "/ns", "products_root": "/ns/runs/prod", "common_args": ["--npz", "x.npz"],
            "geometry": {"batch": 200, "per_line": 10, "max": 1999},
            "controller": {"v": "/ns/V.npz", "status_dir": "/ns/runs/prod/status"},
            "queue": {"budget": "b.json", "ledger": "l.jsonl", "stage": "production", "pool": "cpu", "qos": "shared",
                      "throttle": 3, "timelimit_h": 2, "billing": 32, "logs": "/ns/logs", "products": "/ns/runs/prod/tasks"},
            "nulls": {"MnvTune_v1": {"hypothesis": "h0.json", "prediction": "p0.npz", "seed_base": 1200000},
                      "NuWro_21_09": {"hypothesis": "h1.json", "prediction": "p1.npz", "seed_base": base1}},
            "power": {"P1": {"ratio": "w3.json", "truth": "ratio_nd", "amplitudes": [1.0, 0.5], "n": 200, "seed_base": 1450000}},
            "evaluator": {"alpha_family": 0.05, "shift_coefficients": [0.0, 0.5, 1.0]}}


def seeds(rows):
    out = []
    for r in rows:
        f = r.split("\t")
        a, b = (int(x) for x in f[f.index("--pseudo-seeds") + 1].split(":"))
        out.extend(range(a, b + 1))
    return out


class Tests(unittest.TestCase):
    def test_tables_queues_and_design(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "spec.json").write_text(json.dumps(spec()))
            out = Path(d) / "prod"
            self.assertEqual(sp.main(["--spec", f"{d}/spec.json", "--out", str(out)]), 0)
            for key, base in (("MnvTune_v1", 1200000), ("NuWro_21_09", 1220000)):
                rows = [r for b in range(10) for r in (out / f"tables/cal-{key}-b{b}.tsv").read_text().splitlines()[1:]]
                self.assertEqual(seeds(rows), list(range(base, base + 1999)))
                q = [ln for ln in (out / f"queues/cal-{key}.q").read_text().splitlines() if not ln.startswith("#")]
                self.assertEqual(len(q), 21)
                self.assertTrue(all("s5p_seqstop.py" in q[2 * b] and "squeue" in q[2 * b + 1] for b in range(10)))
                self.assertIn("exit 9", q[-1])
            pw = (out / "tables/pow-P1_a0.5.tsv").read_text().splitlines()[1:]
            self.assertEqual(len(seeds(pw)), 200)
            self.assertIn("--alternative-amplitude\t0.5", pw[0])
            des = json.loads((out / "design.json").read_text())
            self.assertEqual(des["nulls"]["NuWro_21_09"]["calibration_n"]["sequential_status"], "/ns/runs/prod/status/NuWro_21_09-final.json")
            self.assertEqual(set(des["power"]), {"P1_a1.0", "P1_a0.5"})

    def test_overlapping_seed_ranges_are_refused(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "spec.json").write_text(json.dumps(spec(base1=1201000)))
            with self.assertRaises(SystemExit):
                sp.main(["--spec", f"{d}/spec.json", "--out", f"{d}/prod"])
            self.assertFalse((Path(d) / "prod").exists())


if __name__ == "__main__":
    unittest.main()
