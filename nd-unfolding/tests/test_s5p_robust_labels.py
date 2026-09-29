"""Controls for s5p_robust_labels (the A7 ruling): a primary rejection is 'robust' only if the kappa = 3 Holm
re-run also rejects it, 'not robust' otherwise (undetermined or not rejected); every non-rejection is 'not
applicable'; the label file never overwrites and leaves the frozen field as the evaluator wrote it."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5p_robust_labels as rl  # noqa: E402


def d(**kw):
    return {k: {"decision": v} for k, v in kw.items()}


class Tests(unittest.TestCase):
    def test_each_branch(self):
        prim = d(a="rejected", b="rejected", c="rejected", e="undetermined", f="not rejected", g="not rejected")
        rob = d(a="rejected", b="undetermined", c="not rejected", e="undetermined", f="not rejected", g="rejected")
        out = rl.labels(prim, rob)
        self.assertEqual(out, {"a": rl.ROBUST, "b": rl.NOT_ROBUST, "c": rl.NOT_ROBUST,
                               "e": rl.NA, "f": rl.NA, "g": rl.NA})

    def test_frozen_boolean_differs_only_off_rejections(self):
        prim = d(a="rejected", b="rejected", f="not rejected", e="undetermined")
        rob = d(a="rejected", b="undetermined", f="not rejected", e="not rejected")
        frozen = {k: prim[k]["decision"] == rob[k]["decision"] for k in prim}  # s5p_joint's field
        out = rl.labels(prim, rob)
        for k in prim:
            if prim[k]["decision"] == "rejected":
                self.assertEqual(frozen[k], out[k] == rl.ROBUST)
            else:
                self.assertEqual(out[k], rl.NA)
        self.assertTrue(frozen["f"])  # the frozen boolean says True for a non-rejection; the ruling says n/a

    def test_on_the_real_holm_output(self):
        # both fields are written by s5p_inference.holm_determined in the frozen evaluator; feed its real output
        import s5p_inference as si
        src = (Path(__file__).resolve().parents[1] / "s5p_joint.py").read_text()
        self.assertIn('res["decisions"] = si.holm_determined(claims', src)
        self.assertIn('res["decisions_robust_kappa"] = si.holm_determined(robust', src)
        claims = {"x:total": {"p": 1 / 2000, "k": 0, "B": 1999}, "y:total": {"p": 1 / 2000, "k": 0, "B": 1999},
                  "z:total": {"p": 0.5, "k": 999, "B": 1999}}
        robust = {"x:total": {"p": 1 / 2000, "k": 0, "B": 1999}, "y:total": {"p": 0.02, "k": 39, "B": 1999},
                  "z:total": {"p": 0.6, "k": 1199, "B": 1999}}
        prim, rob = si.holm_determined(claims, 0.05), si.holm_determined(robust, 0.05)
        self.assertEqual([prim[k]["decision"] for k in ("x:total", "y:total", "z:total")],
                         ["rejected", "rejected", "not rejected"])
        self.assertEqual(rl.labels(prim, rob), {"x:total": rl.ROBUST, "y:total": rl.NOT_ROBUST, "z:total": rl.NA})

    def test_mismatched_test_sets_are_refused(self):
        with self.assertRaises(SystemExit):
            rl.labels(d(a="rejected"), d(b="rejected"))

    def test_cli_writes_separately_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as t:
            ev = Path(t) / "joint-evaluate.json"
            body = {"decisions": d(a="rejected", f="not rejected"),
                    "decisions_robust_kappa": d(a="not rejected", f="not rejected"),
                    "robust_to_the_sub_fine_residual": {"a": False, "f": True}}
            ev.write_text(json.dumps(body))
            before = ev.read_bytes()
            out = Path(t) / "labels.json"
            self.assertEqual(rl.main(["--evaluate", str(ev), "--out", str(out)]), 0)
            self.assertEqual(ev.read_bytes(), before)
            res = json.loads(out.read_text())
            self.assertEqual(res["labels"], {"a": rl.NOT_ROBUST, "f": rl.NA})
            self.assertEqual(res["frozen_field_unchanged"], {"a": False, "f": True})
            with self.assertRaises(SystemExit):
                rl.main(["--evaluate", str(ev), "--out", str(out)])


if __name__ == "__main__":
    unittest.main()
