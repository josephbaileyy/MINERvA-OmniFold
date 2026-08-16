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

    def test_the_snapshot_RECORDS_the_corpus_so_an_omission_is_a_visible_diff(self):
        """repair-10 #8's unnamed half. The summary used to record only the sweep's OUTPUT, so the
        committed snapshot named no swept module -- `grep -c p4_lib` returned 0 exactly as
        `grep -c p4_check_verifier_token` did -- and a corpus omission was invisible in the artifact
        that exists to catch drift. With the corpus recorded, adding or dropping a module is a
        snapshot diff that `--update` puts in front of a reviewer.
        """
        cur = _current()["recorded_fields"]
        snap = json.loads(SNAPSHOT.read_text())["recorded_fields"]
        self.assertIn("corpus", snap,
                      "the snapshot records no corpus; re-run with --update and commit")
        self.assertEqual(cur["corpus"], snap["corpus"],
                         "the sweep corpus drifted from its snapshot -- a module was added to or "
                         "removed from MODULES/SHELL without regenerating. Re-run with --update so "
                         "the scope change appears in review (repair-10 #8).")
        self.assertEqual(snap["corpus"]["declared_but_absent_from_disk"], [],
                         "the sweep declares a file that is not on disk, so it silently sweeps less "
                         "than its list claims")
        self.assertIn("p4_check_verifier_token.py", snap["corpus"]["modules"],
                      "the module that AUTHORIZES stages 4-6 is not in the recorded corpus "
                      "(repair-10 #8)")

    def test_the_sweep_corpus_COVERS_every_p4_file_on_the_execution_surface(self):
        """repair-10 defect #8, generalised so it cannot recur silently.

        `#8` was that `p4_check_verifier_token.py` -- the module authorizing stages 4-6 -- was absent
        from the recorded-fields sweep, so the gate deciding whether covariance construction may
        proceed was the one file the drift-watcher did not watch. Adding it fixes that instance;
        this test fixes the CLASS, because `MODULES`/`SHELL` are a hand-maintained index of a
        machine-derivable fact and go stale silently (`BEN-228`) -- as the tool's own docstring
        records: *"Last round's sweep was a pass I performed and it missed an item on its own list."*

        The authority is `p4_lib.standard_p4_execution_surface()`, not a second hardcoded list, so a
        new `p4_*` file added to the surface is swept by default or turns this red. Only the `p4_*`
        and `run_p4_*` entries are required: the surface also carries engine/math modules
        (`uq_math.py`, `xsec_nd.py`, …) that write no manifest fields and are out of this sweep's
        stated scope.
        """
        import importlib, contextlib, io
        import p4_lib as P
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            import tools_p4_sweep_recorded_fields as rec
            importlib.reload(rec)
        swept = set(rec.MODULES) | set(rec.SHELL)
        surface = {Path(p).name for p in P.standard_p4_execution_surface()}
        required = {n for n in surface
                    if (n.startswith("p4_") and n.endswith(".py"))
                    or (n.startswith("run_p4_") and n.endswith(".sh"))}
        missing = sorted(required - swept)
        self.assertEqual(missing, [],
                         f"these files are on the standard-P4 execution surface but are NOT swept "
                         f"for recorded-field drift: {missing}. The sweep is how drift becomes "
                         f"visible, so a surface file missing from it is unwatched. Add it to "
                         f"MODULES/SHELL in tools_p4_sweep_recorded_fields.py, or -- if it is "
                         f"deliberately out of scope -- record WHY beside the list, the way the "
                         f"_fps variant's exclusion is recorded (repair-10 #8, BEN-228).")

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

    def test_shell_json_inventory_includes_unquoted_printf_values(self):
        """PB2 receipts emit JSON objects/scalars through unquoted ``%s`` slots.

        The inventory used to require a quote immediately after the colon, so it
        silently omitted both fields even though the production launcher wrote
        them.  Test the extraction set rather than the unchecked-field report:
        later data-flow-aware classification may correctly remove these fields
        from the latter without making the writer inventory incomplete again.
        """
        import contextlib
        import importlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            import tools_p4_sweep_recorded_fields as rec
            importlib.reload(rec)
        for field in ("receipt_schema", "surface_blobs"):
            with self.subTest(field=field):
                self.assertIn(field, rec.written)
                self.assertIn("run_p4_unfold_std.sh", rec.written[field])

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
