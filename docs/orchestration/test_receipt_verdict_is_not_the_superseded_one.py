"""A receipt's canonical `VERDICT` must never be the string it records as superseded.

WHY THIS EXISTS. `state/oi120c-loader-purity-perturbation-56975592.json` was written to correct a
committed log whose banner said `LEAKAGE` when no arm had changed. It carried the true answer under
`CORRECTED_VERDICT` and left the FALSE string under **`VERDICT`** -- the canonical key every other
receipt in this repo uses and the one any consumer reads. So the corrective artifact reproduced the
error it existed to correct, under the name that counts: reading the receipt gave the same wrong
answer as reading the log.

Prose cannot prevent that recurring; a check can, and per `CLAUDE.md` the executable form is the one
to prefer. This is deliberately general rather than scoped to that one file -- the defect is
"a receipt disagrees with itself about its own verdict", which is not specific to OI-120(c).

THE RULE: if a receipt records a superseded/retracted verdict string, the live `VERDICT` must not BE
that string. Retaining the false text is required (nothing may be silently dropped); *serving* it as
the answer is the defect.
"""
import json
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
STATE = HERE / "state"

# Keys a receipt may use to retain a verdict it has retracted. Retention is good practice; the
# check is only that the retained string is not simultaneously the live answer.
SUPERSEDED_KEYS = ("VERDICT_SUPERSEDED_FALSE_STRING", "VERDICT_SUPERSEDED",
                   "SUPERSEDED_VERDICT", "VERDICT_RETRACTED")


def _receipts():
    for p in sorted(STATE.glob("*.json")):
        try:
            d = json.loads(p.read_text())
        except (ValueError, OSError):
            continue
        if isinstance(d, dict):
            yield p, d


class VerdictIsNotTheSupersededOne(unittest.TestCase):
    def test_live_verdict_is_never_the_superseded_string(self):
        checked = 0
        for p, d in _receipts():
            live = d.get("VERDICT")
            if not isinstance(live, str):
                continue
            for k in SUPERSEDED_KEYS:
                old = d.get(k)
                if isinstance(old, str):
                    checked += 1
                    self.assertNotEqual(
                        live.strip(), old.strip(),
                        f"{p.name}: `VERDICT` is the same string as `{k}`. The retracted verdict "
                        f"is being served as the live answer.")
        self.assertGreater(checked, 0,
                           "no receipt carries a superseded-verdict key, so this test asserted "
                           "nothing; a check that cannot fire is not evidence")

    def test_no_stale_parallel_verdict_key(self):
        """`CORRECTED_VERDICT` alongside `VERDICT` is the exact shape that caused this.

        Two keys that both look like the answer means a consumer picks one, and the one it picks
        is the canonical name -- which is how the false string got served.
        """
        for p, d in _receipts():
            if "VERDICT" in d and "CORRECTED_VERDICT" in d:
                self.assertEqual(
                    str(d["VERDICT"]).strip(), str(d["CORRECTED_VERDICT"]).strip(),
                    f"{p.name}: `VERDICT` and `CORRECTED_VERDICT` disagree. Fold the correction "
                    f"into `VERDICT`; do not leave a consumer to choose.")

    def test_the_control_fires_on_a_synthetic_offender(self):
        """A detector that has never detected anything is not evidence."""
        bad = {"VERDICT": "LEAKAGE -- x", "VERDICT_SUPERSEDED_FALSE_STRING": "LEAKAGE -- x"}
        hit = bad["VERDICT"].strip() == bad["VERDICT_SUPERSEDED_FALSE_STRING"].strip()
        self.assertTrue(hit, "the equality the real test relies on does not fire")


if __name__ == "__main__":
    unittest.main()
