"""Tests of flux1_inventory.py on a fixture tree (macOS or Linux; Python >= 3.8 for the audit hook).
Run: python3 -B test_inventory.py. O_NOATIME is passed as 0 where the platform lacks it."""
import contextlib
import io
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flux1_inventory as inv  # noqa: E402

OPENED = []


def hook(event, args):
    if event == "open" and args and isinstance(args[0], (str, bytes)):
        OPENED.append((os.fsdecode(args[0]), args[1] if len(args) > 1 else None))


sys.addaudithook(hook)


def build(top):
    root = os.path.join(top, "root")
    for d in ("clone/a/b", "run/original-inputs", "run/mat-data/X", ".rpd-private/h"):
        os.makedirs(os.path.join(root, d))
    for f, data in (("clone/a/b/x.py", b"x" * 10), ("clone/README", b"r"), ("run/flux-factors-1A.npz", b"n" * 7),
                    ("run/original-inputs/abc-file.root", b"o" * 5), (".rpd-private/h/prestage.json", b"{}"),
                    ("job.out", b"")):
        with open(os.path.join(root, f), "wb") as fh:
            fh.write(data)
    os.symlink("../original-inputs/abc-file.root", os.path.join(root, "run/mat-data/X/file.root"))
    return root


def run(root):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = inv.main(root=root, require_login=False, noatime=getattr(os, "O_NOATIME", 0))
    return rc, buf.getvalue()


class T(unittest.TestCase):
    def test_inventory_lists_without_reading_files(self):
        with tempfile.TemporaryDirectory() as top:
            root = build(top)
            del OPENED[:]
            rc, out = run(root)
            self.assertEqual(rc, 0, out)
            self.assertIn("INVENTORY :: DONE", out)
            files = [p for p, _ in OPENED if os.path.isfile(p)]
            self.assertEqual(files, [], "a file's contents were opened")
            self.assertIn("entry\tf\t7\trun/flux-factors-1A.npz\t", out)
            self.assertIn("entry\tl\t32\trun/mat-data/X/file.root\t../original-inputs/abc-file.root", out)
            self.assertNotIn("x.py", out)                       # clone/ is summarized
            self.assertIn("clone/ entries 5 (d=3 f=2) bytes 11", out)
            self.assertIn("problems 0", out)

    def test_digest_is_stable_and_moves_with_any_change(self):
        with tempfile.TemporaryDirectory() as top:
            root = build(top)
            d1 = run(root)[1].split("listing-sha256 ")[-1].split()[0]
            self.assertEqual(d1, run(root)[1].split("listing-sha256 ")[-1].split()[0])
            with open(os.path.join(root, "clone/a/new"), "wb") as fh:
                fh.write(b"")
            self.assertNotEqual(d1, run(root)[1].split("listing-sha256 ")[-1].split()[0])

    def test_reports_symlink_outside_root(self):
        with tempfile.TemporaryDirectory() as top:
            root = build(top)
            os.symlink("/etc/hosts", os.path.join(root, "run/out-link"))
            rc, out = run(root)
            self.assertEqual(rc, 0)
            self.assertIn("PROBLEM symlink pointing outside the root: run/out-link -> /etc/hosts", out)
            self.assertIn("problems 1", out)

    def test_stops_on_symlinked_or_missing_root(self):
        with tempfile.TemporaryDirectory() as top:
            root = build(top)
            link = os.path.join(top, "rootlink")
            os.symlink(root, link)
            self.assertEqual(run(link)[0], 4)
            self.assertEqual(run(os.path.join(top, "absent"))[0], 4)

    def test_stops_off_a_login_node(self):
        with tempfile.TemporaryDirectory() as top:
            root = build(top)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = inv.main(root=root, require_login=True, noatime=getattr(os, "O_NOATIME", 0))
            self.assertEqual(rc, 4)
            self.assertIn("STOP: not a login node", buf.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
