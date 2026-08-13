"""`snapshot_array_code.sh`: does it actually prevent the Gate-6 code split, and can it FAIL?

Every case is two-sided. A verifier that only ever passes is the vacuous-coverage shape, and this
campaign has shipped two of them -- so each protection below is exercised in the direction that must
succeed AND the direction that must refuse.

The failure this exists to prevent, measured: Gate 6 array 56834281 ran five members on two code
identities because the driver and the annealed estimator were copied onto the cluster tree between
member 4's start and member 5's. Snapshotting removes the race; a per-member sha guard would only
have detected it, one member at a time, after the earlier members had already run.
"""
import json
import os
import subprocess
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(_HERE, "..", "pet", "snapshot_array_code.sh")


def run(*args, cwd=None):
    return subprocess.run(["bash", SCRIPT, *args], capture_output=True, text=True, cwd=cwd)


def write(path, text):
    with open(path, "w") as f:
        f.write(text)
    return path


class SnapshotCreate(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.d = self.td.name
        self.a = write(os.path.join(self.d, "driver.py"), "print('driver v1')\n")
        self.b = write(os.path.join(self.d, "estimator.py"), "print('estimator v1')\n")
        self.snap = os.path.join(self.d, "snap")

    def tearDown(self):
        self.td.cleanup()

    def test_create_then_verify_passes(self):
        c = run("create", self.snap, self.a, self.b)
        self.assertEqual(c.returncode, 0, c.stderr)
        v = run("verify", self.snap)
        self.assertEqual(v.returncode, 0, v.stderr)
        self.assertIn("verified 2 file(s)", v.stdout)

    def test_the_manifest_records_every_file_with_its_sha(self):
        run("create", self.snap, self.a, self.b)
        m = json.load(open(os.path.join(self.snap, "code", "MANIFEST.json")))
        self.assertEqual(m["n_files"], 2)
        self.assertEqual({e["basename"] for e in m["files"]}, {"driver.py", "estimator.py"})
        for e in m["files"]:
            self.assertRegex(e["sha256"], r"^[0-9a-f]{64}$")
            self.assertGreater(e["size"], 0)

    def test_members_exec_a_real_copy_not_a_symlink(self):
        """A symlink would follow the repo file and reintroduce the race it exists to remove."""
        run("create", self.snap, self.a, self.b)
        p = os.path.join(self.snap, "code", "driver.py")
        self.assertTrue(os.path.isfile(p))
        self.assertFalse(os.path.islink(p))

    def test_editing_the_SOURCE_after_snapshot_does_not_change_the_snapshot(self):
        """This is the whole point: the Gate-6 split was a source edit reaching a running array."""
        run("create", self.snap, self.a, self.b)
        write(self.a, "print('driver v2 -- the mid-array copy')\n")
        v = run("verify", self.snap)
        self.assertEqual(v.returncode, 0, "the snapshot must be unaffected by a source edit")
        self.assertEqual(open(os.path.join(self.snap, "code", "driver.py")).read(),
                         "print('driver v1')\n")

    # ---- the directions that must REFUSE ---------------------------------------------------
    def test_second_create_refuses(self):
        """A second create would silently re-point a running array at different code."""
        self.assertEqual(run("create", self.snap, self.a, self.b).returncode, 0)
        c2 = run("create", self.snap, self.a, self.b)
        self.assertNotEqual(c2.returncode, 0)
        self.assertIn("refusing to overwrite", c2.stderr)

    def test_basename_collision_refuses_before_copying(self):
        """Two files with one basename would overwrite each other and the manifest would claim
        both -- the HPSS flat-destination collision, in a code snapshot."""
        sub = os.path.join(self.d, "other")
        os.makedirs(sub)
        dup = write(os.path.join(sub, "driver.py"), "print('a different driver')\n")
        c = run("create", self.snap, self.a, dup)
        self.assertNotEqual(c.returncode, 0)
        self.assertIn("distinct basenames", c.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.snap, "code", "MANIFEST.json")),
                         "it must refuse BEFORE writing a manifest")

    def test_missing_source_file_refuses(self):
        c = run("create", self.snap, os.path.join(self.d, "absent.py"))
        self.assertNotEqual(c.returncode, 0)
        self.assertIn("not a file", c.stderr)

    def test_verify_refuses_when_the_snapshot_was_altered(self):
        """THE POWER TEST. If this passes on a tampered snapshot the verifier is decoration."""
        run("create", self.snap, self.a, self.b)
        write(os.path.join(self.snap, "code", "driver.py"), "print('tampered')\n")
        v = run("verify", self.snap)
        self.assertNotEqual(v.returncode, 0, "a modified snapshot MUST fail verification")
        self.assertIn("altered since create", v.stderr)

    def test_verify_refuses_when_a_snapshot_file_is_deleted(self):
        run("create", self.snap, self.a, self.b)
        os.remove(os.path.join(self.snap, "code", "estimator.py"))
        v = run("verify", self.snap)
        self.assertNotEqual(v.returncode, 0)

    def test_verify_refuses_with_no_manifest(self):
        os.makedirs(os.path.join(self.snap, "code"), exist_ok=True)
        v = run("verify", self.snap)
        self.assertNotEqual(v.returncode, 0)
        self.assertIn("no manifest", v.stderr)

    def test_verify_refuses_an_EMPTY_manifest(self):
        """A verifier that reports success over zero files is the vacuous-stage shape, and this
        campaign has shipped it twice. Hand-craft the degenerate manifest and require a refusal."""
        code = os.path.join(self.snap, "code")
        os.makedirs(code, exist_ok=True)
        write(os.path.join(code, "MANIFEST.json"),
              json.dumps({"created_utc": "x", "files": [], "n_files": 0}))
        v = run("verify", self.snap)
        self.assertNotEqual(v.returncode, 0)
        self.assertIn("zero files", v.stderr)

    def test_verify_refuses_when_n_files_disagrees_with_the_list(self):
        """A manifest whose own count contradicts its contents cannot be trusted either way."""
        run("create", self.snap, self.a, self.b)
        p = os.path.join(self.snap, "code", "MANIFEST.json")
        m = json.load(open(p))
        m["n_files"] = 5
        write(p, json.dumps(m))
        v = run("verify", self.snap)
        self.assertNotEqual(v.returncode, 0)
        self.assertIn("n_files", v.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
