#!/usr/bin/env python3
"""The quarantine gate must reject on the PHYSICS, and must still be able to say yes.

`pet_diagnostic_quarantine.require_quotable` exists to make the 2026-08-09 diagnostic extraction
unquotable by construction. Two failure modes would make it worthless, and both have precedent in
this repo:

  1. **It rejects only because of its own labels.** Then the marker is doing the work, the physics is
     not, and copying the manifest into the publication namespace launders the product. BEN-043 and
     `check_powered_closure`'s first version are both cases of a claimed field being trusted over the
     bytes; `test_rejects_laundered_*` is the guard.
  2. **It can never say yes.** A gate that always returns False is not evidence of anything -- it is
     the BEN-070/071 family (a check whose threshold puts it beyond reach) seen from the other side,
     and it is exactly the defect that made the original `recovery >= 0.80` bar unsatisfiable: 0.80
     absolute sits ABOVE the 0.618228 acceptance-limited ceiling, so no estimator could ever have
     passed it. `test_accepts_when_physics_is_in_tolerance` is the power proof.

The fixtures build a real .npz with the three artifact keys and a `target` dict, so the arithmetic
under test is the arithmetic that runs on the production artifact.
"""
import json
import os
import sys
import tempfile
import unittest

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PET = os.path.join(ND, "pet")
if PET not in sys.path:
    sys.path.insert(0, PET)

import pet_diagnostic_quarantine as q  # noqa: E402

R_NOMINAL = 1.1240802949941018
# The measured 2026-08-08 nominal: reco-weighted mean of push 0.736746 against R -> dev 0.344577.
NOMINAL_NUM = 736746.2709517315
NOMINAL_DEN = 1000000.0282607947


def _weights_npz(path, *, num, den, R=R_NOMINAL, drop_target=False):
    payload = {
        "fold_forward_sum_w_push_reco": np.asarray(num, float),
        "fold_forward_sum_w_reco": np.asarray(den, float),
        "fold_forward_n_pass_reco": np.asarray(837671.0, float),
    }
    if not drop_target:
        payload["target"] = np.asarray({"step1_class_ratio": R, "target_mode": "negweight-refined"},
                                       dtype=object)
    np.savez(path, **payload)
    return path


def _manifest(tmp, *, schema=q.DIAGNOSTIC_SCHEMA, label=q.DIAGNOSTIC_LABEL, quarantined=True):
    d = os.path.join(tmp, q.QUARANTINE_DIRNAME if quarantined else "fullevent_nominal")
    stem = (q.FILENAME_MARKER + ".xsec") if quarantined else "xsec"
    return {
        "schema": schema,
        "label": label,
        "manifest_path": os.path.join(d, stem + ".manifest.json"),
        "xsec_path": os.path.join(d, stem + ".npz"),
        "push_path": os.path.join(d, stem + ".push.npz"),
    }


class QuarantineGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def _w(self, **kw):
        return _weights_npz(os.path.join(self.tmp, "w.npz"), **kw)

    # ---------------- ground 1: the physics, which must be sufficient alone ----------------

    def test_rejects_on_measured_fold_forward_deficit(self):
        w = self._w(num=NOMINAL_NUM, den=NOMINAL_DEN)
        with self.assertRaises(q.NonQuotableError) as cm:
            q.require_quotable(_manifest(self.tmp), w)
        self.assertIn("fold-forward deviation", str(cm.exception))
        self.assertIn("NOT QUOTABLE on the physics alone", str(cm.exception))

    def test_rejects_laundered_manifest_on_physics_alone(self):
        """Publication schema + label, marker stripped, quarantine path rewritten -> still rejected.

        This is the test that matters. If it ever fails, the gate is protecting the record with a
        filename rather than with a number.
        """
        w = self._w(num=NOMINAL_NUM, den=NOMINAL_DEN)
        clean = _manifest(self.tmp, schema=q.PUBLICATION_SCHEMA, label=q.PUBLICATION_LABEL,
                          quarantined=False)
        self.assertNotIn(q.QUARANTINE_DIRNAME, json.dumps(clean))
        self.assertNotIn(q.FILENAME_MARKER, json.dumps(clean))
        with self.assertRaises(q.NonQuotableError) as cm:
            q.require_quotable(clean, w)
        self.assertIn("fold-forward deviation", str(cm.exception))

    def test_measured_deviation_matches_validator_arithmetic(self):
        w = self._w(num=NOMINAL_NUM, den=NOMINAL_DEN)
        dev, num, den, R = q.measured_fold_forward_dev(w)
        expected = abs((NOMINAL_NUM / NOMINAL_DEN) / R_NOMINAL - 1.0)
        self.assertAlmostEqual(dev, expected, places=12)
        self.assertAlmostEqual(dev, 0.344577, places=5)
        self.assertEqual((num, den), (NOMINAL_NUM, NOMINAL_DEN))

    def test_R_is_read_from_the_artifact_not_remembered(self):
        """A product built against a different R is measured against THAT R."""
        w = self._w(num=736746.0, den=1000000.0, R=0.736746)
        dev, _, _, R = q.measured_fold_forward_dev(w)
        self.assertAlmostEqual(R, 0.736746, places=9)
        self.assertLess(dev, 1e-6)

    def test_missing_target_is_an_error_not_a_pass(self):
        w = self._w(num=NOMINAL_NUM, den=NOMINAL_DEN, drop_target=True)
        with self.assertRaises(q.NonQuotableError):
            q.measured_fold_forward_dev(w)

    # ---------------- the power proof: the gate must be able to say yes ----------------

    def test_accepts_when_physics_is_in_tolerance(self):
        """POWER PROOF. Without this, every assertion above is satisfied by `return False`.

        A gate that cannot pass is the same defect class as a gate that cannot fail, and it is what
        made `recovery >= 0.80` unsatisfiable against a 0.618228 ceiling.
        """
        w = self._w(num=NOMINAL_DEN * R_NOMINAL, den=NOMINAL_DEN)  # fold-forward exactly satisfied
        clean = _manifest(self.tmp, schema=q.PUBLICATION_SCHEMA, label=q.PUBLICATION_LABEL,
                          quarantined=False)
        self.assertTrue(q.require_quotable(clean, w))

    def test_at_tolerance_boundary_the_gate_moves(self):
        """Just inside passes, just outside rejects -- the threshold is where it claims to be."""
        clean = _manifest(self.tmp, schema=q.PUBLICATION_SCHEMA, label=q.PUBLICATION_LABEL,
                          quarantined=False)
        inside = NOMINAL_DEN * R_NOMINAL * (1.0 - 0.9 * q.FOLD_FORWARD_DEV_MAX)
        outside = NOMINAL_DEN * R_NOMINAL * (1.0 - 1.1 * q.FOLD_FORWARD_DEV_MAX)
        self.assertTrue(q.require_quotable(clean, self._w(num=inside, den=NOMINAL_DEN)))
        with self.assertRaises(q.NonQuotableError):
            q.require_quotable(clean, self._w(num=outside, den=NOMINAL_DEN))

    # ---------------- grounds 2-4: self-description, reached only past the physics ----------------

    def test_diagnostic_schema_rejected_even_with_good_physics(self):
        w = self._w(num=NOMINAL_DEN * R_NOMINAL, den=NOMINAL_DEN)
        m = _manifest(self.tmp, label=q.PUBLICATION_LABEL, quarantined=False)
        with self.assertRaises(q.NonQuotableError) as cm:
            q.require_quotable(m, w)
        self.assertIn(q.DIAGNOSTIC_SCHEMA, str(cm.exception))

    def test_quarantine_namespace_rejected_even_with_good_physics(self):
        w = self._w(num=NOMINAL_DEN * R_NOMINAL, den=NOMINAL_DEN)
        m = _manifest(self.tmp, schema=q.PUBLICATION_SCHEMA, label=q.PUBLICATION_LABEL,
                      quarantined=True)
        with self.assertRaises(q.NonQuotableError) as cm:
            q.require_quotable(m, w)
        self.assertIn("quarantine namespace", str(cm.exception))

    # ---------------- the builder ----------------

    def test_builder_writes_readonly_and_records_both_rejections(self):
        w = self._w(num=NOMINAL_NUM, den=NOMINAL_DEN)
        for name in ("xsec.npz", "push.npz", "sum.json", "in.npz"):
            with open(os.path.join(self.tmp, name), "wb") as fh:
                fh.write(b"x")
        out = os.path.join(self.tmp, q.QUARANTINE_DIRNAME,
                           f"{q.FILENAME_MARKER}.manifest.json")
        man = q.build_diagnostic_manifest(
            weights_npz=w,
            xsec_npz=os.path.join(self.tmp, "xsec.npz"),
            push_npz=os.path.join(self.tmp, "push.npz"),
            xsec_summary=os.path.join(self.tmp, "sum.json"),
            inputs_npz=os.path.join(self.tmp, "in.npz"),
            out_path=out, job_id="test")
        self.assertTrue(man["publication_gate_rejects_this"])
        self.assertTrue(man["publication_gate_rejects_this_on_physics_alone"])
        self.assertIn("fold-forward deviation", man["rejection_reason"])
        self.assertIn("fold-forward deviation", man["rejection_reason_laundered"])
        self.assertEqual(oct(os.stat(out).st_mode)[-3:], "444")
        on_disk = json.load(open(out))
        self.assertEqual(on_disk["schema"], q.DIAGNOSTIC_SCHEMA)
        self.assertAlmostEqual(on_disk["fold_forward"]["deviation"], 0.344577, places=5)
        self.assertGreater(on_disk["fold_forward"]["exceeds_tolerance_by"], 6.0)

    def test_builder_refuses_to_write_if_gate_would_accept(self):
        """If the physics ever comes into tolerance, the builder must NOT quietly emit a
        'non-quotable' manifest whose non-quotability is false."""
        w = self._w(num=NOMINAL_DEN * R_NOMINAL, den=NOMINAL_DEN)
        for name in ("xsec.npz", "push.npz", "sum.json", "in.npz"):
            with open(os.path.join(self.tmp, name), "wb") as fh:
                fh.write(b"x")
        out = os.path.join(self.tmp, "out", "m.json")
        with self.assertRaises(SystemExit) as cm:
            q.build_diagnostic_manifest(
                weights_npz=w,
                xsec_npz=os.path.join(self.tmp, "xsec.npz"),
                push_npz=os.path.join(self.tmp, "push.npz"),
                xsec_summary=os.path.join(self.tmp, "sum.json"),
                inputs_npz=os.path.join(self.tmp, "in.npz"),
                out_path=out)
        self.assertIn("did NOT reject", str(cm.exception))
        self.assertFalse(os.path.exists(out))


if __name__ == "__main__":
    unittest.main()
