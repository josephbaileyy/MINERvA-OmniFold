#!/usr/bin/env python3
"""REPAIR-7 item 4: the sweeps cannot go stale against themselves.

The recorded-fields inventory was committed saying 66 fields / 22 gates while its own generator
reported 82 / 24, and the pipeline document said 22/324 while the tool said 23/326. The artifact
drifted from its generator INSIDE the round that created it -- the exact failure the artifact
existed to prevent, and the verifier found it rather than the author.

A prose document cannot be diffed against a script, so each sweep now emits a machine-readable
`summary()`, the summary is committed as a snapshot, and these tests regenerate and compare.
Staleness is now a red test on the author's machine instead of a finding on someone else's.

Updating the snapshot is deliberate: run this file with `--update` and commit the diff, which
puts the number change in the review where a reader can see it.
"""
import json
import sys
import unittest
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ND))

SNAPSHOT = ND.parent / "docs/orchestration/state/p4-sweep-snapshots.json"


def _current():
    import importlib
    import tools_p4_sweep_pipeline_rc as pipe
    importlib.reload(pipe)
    # the recorded-fields tool prints at import; capture and discard that
    import contextlib, io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        import tools_p4_sweep_recorded_fields as rec
        importlib.reload(rec)
    return {"pipeline": pipe.summary(), "recorded_fields": rec.summary()}


class SweepSnapshots(unittest.TestCase):

    def test_snapshot_exists(self):
        self.assertTrue(SNAPSHOT.exists(),
                        f"missing {SNAPSHOT}; run this file with --update and commit it")

    def test_pipeline_sweep_matches_its_snapshot(self):
        cur = _current()["pipeline"]
        snap = json.loads(SNAPSHOT.read_text())["pipeline"]
        self.assertEqual(cur["n_shell_files"], snap["n_shell_files"],
                         "shell-file count drifted; re-run with --update and commit")
        self.assertEqual(cur["n_candidates"], snap["n_candidates"],
                         "candidate count drifted; re-run with --update and commit")

    def test_no_LIVE_pipeline_instances(self):
        """The claim the document makes. If a shell file without pipefail acquires one of the
        three shapes, this goes red rather than the claim quietly becoming false."""
        cur = _current()["pipeline"]
        self.assertEqual(cur["live_instances"], 0,
                         "a pipeline-rc instance exists in a file WITHOUT pipefail -- the "
                         "'no live instances' claim in the inventory is no longer true")

    def test_recorded_fields_sweep_matches_its_snapshot(self):
        cur = _current()["recorded_fields"]
        snap = json.loads(SNAPSHOT.read_text())["recorded_fields"]
        self.assertEqual(cur["n_fields"], snap["n_fields"],
                         "recorded-but-unchecked field count drifted; --update and commit")
        self.assertEqual(cur["n_gates"], snap["n_gates"],
                         "named-gate count drifted; --update and commit")

    def test_new_unchecked_fields_are_surfaced_by_name(self):
        """Counts alone would let one field appear as another disappears."""
        cur = set(_current()["recorded_fields"]["fields"])
        snap = set(json.loads(SNAPSHOT.read_text())["recorded_fields"]["fields"])
        self.assertEqual(cur - snap, set(), f"NEW recorded-but-unchecked field(s): {cur - snap}")
        self.assertEqual(snap - cur, set(), f"field(s) no longer detected: {snap - cur}")

    def test_the_inventory_document_quotes_the_snapshot_numbers(self):
        """The document is prose, but its headline counts must agree with the snapshot."""
        doc = (ND.parent / "docs/orchestration/REPAIR6-RECORDED-NOT-CHECKED-INVENTORY.md").read_text()
        snap = json.loads(SNAPSHOT.read_text())
        nf, ng = snap["recorded_fields"]["n_fields"], snap["recorded_fields"]["n_gates"]
        self.assertIn(f"**{nf} fields**", doc,
                      f"the document does not quote the current field count ({nf})")
        self.assertIn(f"**{ng} named\ngates**".replace("\n", " "), doc.replace("\n", " "),
                      f"the document does not quote the current gate count ({ng})")


def _update():
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps(_current(), indent=2, sort_keys=True) + "\n")
    print(f"snapshot written: {SNAPSHOT}")


if __name__ == "__main__":
    if "--update" in sys.argv:
        _update()
    else:
        unittest.main(verbosity=2)
