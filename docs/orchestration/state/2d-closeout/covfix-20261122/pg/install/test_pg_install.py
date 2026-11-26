"""Tests for pg-install-g2111a.py (B2) on a stub tarball: no cluster, no SciSoft download.

Run: python3 -I -B test_pg_install.py -v   (from this directory)
"""
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
DBCONFIG_PIN = "accaf71bb0ae10ddd1df30c2b3af8099312e0f5e59ab66d1f42cbab1f00b2950"   # the director's pin of B1's receipt (2026-11-26)


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


I = load("pg_install", HERE / "pg-install-g2111a.py")
BR = load("build_record", HERE.parent / "record" / "build_record.py")
Q = "genie_xsec/v3_04_00/NULL/Q"
# the real shape: no container member (SciSoft's tarball starts at genie_xsec/v3_04_00)
ENTRIES = [("genie_xsec/v3_04_00", "dir", None), ("genie_xsec/v3_04_00/NULL", "dir", None),
           (Q, "dir", None), (f"{Q}/data", "dir", None), (f"{Q}/data/gxspl-NUsmall.xml", "file", b"<spl/>\n" * 100),
           (f"{Q}/data/gxspl-FNALsmall.xml", "sym", "gxspl-NUsmall.xml"), (f"{Q}/data/README", "file", b"readme\n"),
           (f"{Q}/ups", "dir", None), (f"{Q}/ups/genie_xsec.table", "file", b"table\n")]


def make_tar(path, entries):
    with tarfile.open(path, "w:bz2") as tf:
        for name, kind, x in entries:
            ti = tarfile.TarInfo(name)
            if kind == "file":
                ti.size, ti.mode = len(x), 0o644
                tf.addfile(ti, io.BytesIO(x))
                continue
            ti.type = {"dir": tarfile.DIRTYPE, "sym": tarfile.SYMTYPE}[kind]
            ti.mode = 0o755
            if kind == "sym":
                ti.linkname = x
            tf.addfile(ti)


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Install(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix="pgi-", dir="/tmp")))
        self.addCleanup(self.clean)
        self.tar = self.tmp / "src.tar.bz2"
        make_tar(self.tar, ENTRIES)
        self.members = BR.members(str(self.tar))
        self.dbc = self.tmp / "dbconfig"
        self.dbc.write_text("FILE = DBCONFIG\n")
        self.root = self.tmp / "scratch/covfix-pg/products"

    def clean(self):
        for d, _, _ in os.walk(self.tmp):
            os.chmod(d, 0o755)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def install(self, tar=None, **kw):
        src = tar or self.tar

        def fetch(url, out):
            shutil.copy(src, out)
            return 0
        args = dict(root=str(self.root), url="https://x/t.tar.bz2", tarball_sha=sha(self.tar.read_bytes()),
                    members=self.members, dbconfig_src=str(self.dbc), dbconfig_sha=sha(self.dbc.read_bytes()),
                    ident=lambda: {"pass": True}, fetch=fetch, scratch=str(self.tmp / "scratch") + "/")
        args.update(kw)
        return I.install(**args)

    def test_go(self):
        r = self.install()
        self.assertEqual(r["verdict"], "GO", r["stops"])
        self.assertEqual(sorted(os.listdir(self.root)), [".upsfiles", "genie_xsec"])   # the download is gone
        self.assertEqual(I.check_tree(str(self.root), self.members, readonly=True), [])
        self.assertEqual((self.root / ".upsfiles/dbconfig").read_text(), "FILE = DBCONFIG\n")
        self.assertEqual(os.readlink(self.root / f"{Q}/data/gxspl-FNALsmall.xml"), "gxspl-NUsmall.xml")
        for p in (self.root / f"{Q}/data/README", self.root / f"{Q}/data", self.root / ".upsfiles/dbconfig"):
            self.assertFalse(os.lstat(p).st_mode & 0o222, p)
        self.assertIn("install_utc", r)

    def test_a_changed_download_is_removed_and_stops(self):
        bad = self.tmp / "bad.tar.bz2"
        make_tar(bad, ENTRIES[:-1])
        r = self.install(tar=bad)
        self.assertEqual(r["verdict"], "STOP")
        self.assertTrue(r["stops"][0].startswith("download-sha: "), r["stops"])
        self.assertEqual(os.listdir(self.root / "dl"), [])

    def test_a_member_that_differs_from_its_pin_extracts_nothing(self):
        for i, change in enumerate((lambda m: m[f"{Q}/data/README"].update(sha256="0" * 64),
                                    lambda m: m.pop(f"{Q}/ups/genie_xsec.table"),
                                    lambda m: m.update({f"{Q}/data/extra": {"type": "file", "sha256": "0" * 64}}),
                                    lambda m: m[f"{Q}/data/gxspl-FNALsmall.xml"].update(target="README"),
                                    lambda m: m[f"{Q}/data"].update(type="file"))):
            with self.subTest(i):
                self.clean()
                self.setUp()
                m = json.loads(json.dumps(self.members))
                change(m)
                r = self.install(members=m)
                self.assertEqual(r["stops"], ["members: the tarball's members differ from the pins; nothing was extracted"])
                self.assertTrue(r["scan_problems"])
                self.assertFalse((self.root / "genie_xsec").exists())

    def test_a_stray_file_in_the_product_stops(self):
        def fetch(url, out):
            shutil.copy(self.tar, out)
            (self.root / "stray").write_text("x")             # something else writes into the product directory
            return 0
        r = self.install(fetch=fetch)
        self.assertEqual(r["verdict"], "STOP")
        self.assertTrue(any("holds" in p for p in r["tree_problems"]), r["tree_problems"])

    def test_dbconfig_must_be_the_pinned_one(self):
        r = self.install(dbconfig_sha="0" * 64)
        self.assertEqual(r["verdict"], "STOP")
        self.assertTrue(r["stops"][0].startswith("dbconfig-sha: "), r["stops"])
        self.assertFalse((self.root / ".upsfiles").exists())

    def test_refusals_write_nothing(self):
        for name, kw, code in (("identity", dict(ident=lambda: {"pass": False}), "identity: "),
                               ("no dbconfig pin", dict(dbconfig_sha=None), "dbconfig-unpinned: "),
                               ("not on scratch", dict(scratch="/pscratch/"), "root-place: ")):
            with self.subTest(name):
                r = self.install(**kw)
                self.assertTrue(r["stops"][0].startswith(code), r["stops"])
                self.assertFalse((self.tmp / "scratch").exists())                 # nothing at all was written
        self.root.mkdir(parents=True)
        r = self.install()
        self.assertTrue(r["stops"][0].startswith("root-exists: "), r["stops"])
        self.assertEqual(os.listdir(self.root), [])

    def test_a_root_beside_scratch_is_refused(self):
        (self.tmp / "scratch").mkdir()                          # an existing ancestor above scratch, a root not on it
        r = self.install(root=str(self.tmp / "other/covfix-pg/products"))
        self.assertTrue(r["stops"][0].startswith("root-place: "), r["stops"])
        self.assertFalse((self.tmp / "other").exists())

    def test_scratch_is_checked_on_the_real_path(self):
        (self.tmp / "elsewhere").mkdir()
        (self.tmp / "scratch").symlink_to(self.tmp / "elsewhere")              # lexically on scratch, really not
        r = self.install()
        self.assertTrue(r["stops"][0].startswith("root-place: "), r["stops"])
        self.assertEqual(os.listdir(self.tmp / "elsewhere"), [])        # refused before anything was created

    def test_the_real_listing_installs(self):
        # the real G2111a listing's names, types and link targets (synthetic bytes): no container member
        real = json.loads((HERE.parent / "record/G2111a-members.json").read_text())["members"]
        self.assertNotIn("genie_xsec", real)
        entries = [(n, {"file": "file", "dir": "dir", "symlink": "sym"}[m["type"]],
                    n.encode() if m["type"] == "file" else m.get("target")) for n, m in sorted(real.items())]
        tar = self.tmp / "real.tar.bz2"
        make_tar(tar, entries)
        members = BR.members(str(tar))
        self.assertEqual({k: v["type"] for k, v in members.items()}, {k: v["type"] for k, v in real.items()})
        r = self.install(tar=tar, members=members, tarball_sha=sha(tar.read_bytes()))
        self.assertEqual(r["verdict"], "GO", r["stops"])
        self.assertEqual(I.check_tree(str(self.root), members, readonly=True), [])

    def test_a_writable_container_fails(self):
        self.assertEqual(self.install()["verdict"], "GO")
        os.chmod(self.root / "genie_xsec", 0o755)
        self.assertIn("tree-container: genie_xsec is not a read-only directory",
                      I.check_tree(str(self.root), self.members, readonly=True))

    def test_a_missing_or_file_upsfiles_is_a_problem(self):
        self.assertEqual(self.install()["verdict"], "GO")
        up = self.root / ".upsfiles"
        os.chmod(self.root, 0o755)
        os.chmod(up, 0o755)
        (up / "dbconfig").unlink()
        up.rmdir()
        self.assertIn("upsfiles: .upsfiles is missing", I.check_tree(str(self.root), self.members, readonly=True))
        up.write_text("x")
        self.assertIn("upsfiles: .upsfiles is not a directory", I.check_tree(str(self.root), self.members, readonly=True))

    def test_upsfiles_must_hold_only_dbconfig(self):
        self.assertEqual(self.install()["verdict"], "GO")
        up = self.root / ".upsfiles"
        os.chmod(up, 0o755)
        (up / "extra").write_text("x")
        self.assertTrue(any(p.startswith("upsfiles: ") for p in I.check_tree(str(self.root), self.members, True)))

    def test_an_unexpected_exception_is_its_own_reason(self):
        m = dict(self.members, **{"genie_xsec/v3_04_00": "dir"})          # a malformed pin: str, not a record
        r = self.install(members=m)
        self.assertEqual(r["stops"], ["internal-error: TypeError"])

    def test_check_tree_finds_changes(self):
        self.assertEqual(self.install()["verdict"], "GO")
        d = self.root / f"{Q}/data"
        os.chmod(d, 0o755)
        (d / "ModelConfiguration.xml").write_text("x")
        os.chmod(d / "README", 0o644)
        probs = I.check_tree(str(self.root), self.members, readonly=True)
        self.assertTrue(any(p.startswith("extra: ") for p in probs))
        self.assertTrue(any(p.endswith("README: writable") for p in probs))
        (d / "README").write_text("other\n")
        self.assertTrue(any("README: sha256 differs" in p for p in I.check_tree(str(self.root), self.members, False)))


RP = load("pg_replay", HERE / "pg-replay-g2111a.py")
EA = load("embed_archive", HERE / "embed_archive.py")
GOOD_REPLAY = dict(RP.IDENTITY, **{
    "pass": True, "checks": {n: True for n in RP.REPLAY_CHECKS}, "spline_opened": {n: True for n in RP.SPLINE_TRACES},
    "gated": {n: [{"path": f"/p/{b}", "sha256": "0" * 64, "pinned_by": "genie manifest"} for b in RP.GATED[n] or ("x.so",)]
              for n in RP.TRACES},
    "real_shapes": {k: True for k in RP.SHAPES}, "host": {k: True for k in RP.HOST_CHECKS},
    "coverage_log_sha256": {"coverage_check.json": "1" * 64, "coverage_check_slot2.json": "2" * 64},
    "execs": {n: [{"path": f"/b/{RP.PROGRAM[n]}", "real": f"/b/{RP.PROGRAM[n]}", "sha256": "3" * 64,
                   "bound_by": "genie manifest"}] for n in RP.TRACES},
    "revision": {"start": {"revision": "7", "root_hash": "h"}, "end": {"revision": "7", "root_hash": "h"}},
    "gst_schema": {"keys": [["TTree", "gst", "t"]], "streamer_sha256": "4" * 64},
    "gst_merged_schema": {"keys": [["TTree", "gst", "t"]], "streamer_sha256": "5" * 64}})
REC = {"sha256": "a" * 64, "bytes": 10, "holds_public_seed": False}
ROOTREC = dict(REC, decoded={"holds_seed": False, "name_holds_seed": False, "int32_count": 0, "codecs": {"ZL": 2},
                              "bytes_inflated": 9, "hits": [], "seed_objects": []})
SEED_OBJ = {"class": "genie::NtpMCTreeHeader", "inflated": False, "kind": "int32-object"}   # R1: GENIE's header, stored
CONTROL = dict(REC, holds_public_seed=True, decoded=dict(ROOTREC["decoded"], holds_seed=True, name_holds_seed=True,
                                                         hits=["bytes", "int32-object", "path"],
                                                         seed_objects=[SEED_OBJ]))   # the seed, decoded
RUN = {"gevgen.status": REC, "input-flux.root": ROOTREC}       # what each run leaves (t0's GHEP the wrapper removes)
COV = dict(RUN, **{"gevgen.log": REC, "gntp.ghep.root": CONTROL})
GOOD_DELETED = {"t0": dict(RUN, **{"genie_v3.gst.root": dict(ROOTREC, schema=GOOD_REPLAY["gst_schema"])}),
                "coverage_slot1": COV, "coverage_slot2": COV,
                "merged": {"genie_v3_g21_ALL.gst.root": dict(ROOTREC, schema=GOOD_REPLAY["gst_merged_schema"])}}
class NodeLaunch(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix="pgl-", dir="/tmp")))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.L = load("pg_node_launch", HERE / "pg-node-launch.py")
        self.script = self.tmp / "pg-install-g2111a.py"          # the real script, with its dbconfig pin
        src = (HERE / "pg-install-g2111a.py").read_text()
        self.assertEqual(src.count(f'DBCONFIG_SHA256 = "{DBCONFIG_PIN}"'), 1)
        self.script.write_text(src)
        self.sha = sha(self.script.read_bytes())
        self.pins = self.L.script_pins(self.script.read_bytes())
        self.go = {"schema": "covfix-pg-install/1", "verdict": "GO", "stops": [], "root": self.pins["ROOT"],
                   "tarball_sha256_pin": self.pins["TARBALL_SHA256"], "tarball_sha256": self.pins["TARBALL_SHA256"],
                   "n_members_pinned": len(I.MEMBERS["members"]), "dbconfig_sha256": DBCONFIG_PIN, "scan_problems": [],
                   "tree_problems": [], "identity": {"pass": True}, "install_utc": "t"}

    def launch(self, body, sha_=None, script=None):
        s = self.tmp / "ssh"
        s.write_text(f"#!/bin/sh\necho \"$@\" > {self.tmp}/args\ncat > {self.tmp}/stdin\n{body}\n")
        s.chmod(0o755)
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return self.L.main([str(script or self.script), sha_ or self.sha], ssh=str(s))

    def emit(self, rec, rc):
        f = self.tmp / f"r{len(list(self.tmp.iterdir()))}.txt"
        f.write_text("x\nPG-RESULT " + json.dumps(rec) + "\n")
        return f"cat {f}; exit {rc}"

    def test_receipts(self):
        out = Path(str(self.script) + ".out")
        go = self.go
        self.assertEqual(self.launch(self.emit(go, 0)), 0)
        self.assertEqual((self.tmp / "stdin").read_bytes(), self.script.read_bytes())
        for i, (rec, rc) in enumerate(((dict(go, schema="covfix-pg-replay/1"), 0), (dict(go, stops=["x"]), 0),
                                       (dict(go, verdict="STOP"), 3), (go, 3), ({"verdict": "GO"}, 0),
                                       (dict(go, root="/elsewhere"), 0))):                # a payload off its pins
            with self.subTest(i):
                out.unlink()
                self.assertEqual(self.launch(self.emit(rec, rc)), 4)
        out.unlink()
        self.assertEqual(self.launch(self.emit(dict(go, verdict="STOP", stops=["x"]), 3)), 3)

    def test_install_payloads(self):
        for k, v in (("root", "/elsewhere"), ("tarball_sha256", "0" * 64), ("n_members_pinned", 16),
                     ("dbconfig_sha256", "e" * 64), ("scan_problems", ["x"]), ("tree_problems", None),
                     ("identity", {"pass": 1}), ("install_utc", None)):
            with self.subTest(k):
                self.assertNotEqual(self.L.payload_problems(dict(self.go, **{k: v}), "covfix-pg-install/1", self.pins), [])
        self.assertEqual(self.L.payload_problems(self.go, "covfix-pg-install/1", self.pins), [])
        ok, why = self.L.validate("PG-RESULT " + json.dumps(dict(self.go, root="/x")), 0, "covfix-pg-install/1", self.pins)
        self.assertEqual((ok, why), (False, "payload: ['root or tarball pin']"))

    def test_replay_payloads(self):
        blobs = {"a": "0" * 40, "b": "1" * 40}
        pins = {"COMMIT": "c" * 40, "ARCHIVE_SHA256": "a" * 64, "BLOBS_JSON": json.dumps(blobs)}
        rec = {"schema": "covfix-pg-replay/1", "verdict": "GO", "stops": [], "commit": "c" * 40,
               "archive_sha256_pin": "a" * 64, "archive_sha256": "a" * 64, "n_blobs": 2, "n_files_checked": 2,
               "driver_rc": 0, "identity": {"pass": True}, "deleted": GOOD_DELETED,
               "replay": dict(GOOD_REPLAY)}
        self.assertEqual(self.L.payload_problems(rec, "covfix-pg-replay/1", pins), [])
        r2 = json.loads(json.dumps(rec))
        r2["replay"]["checks"] = {}
        for name, bad, want in (("commit", dict(rec, commit="d" * 40), "commit, archive pin or blob count"),
                                ("driver rc", dict(rec, driver_rc=1), "a GO without its archive, blobs, driver rc or identity"),
                                ("empty checks", r2, "replay checks"),
                                ("deleted", dict(rec, deleted={}), "deleted names"),
                                ("driver rc False", dict(rec, driver_rc=False),
                                 "a GO without its archive, blobs, driver rc or identity"),
                                ("blob count True", dict(rec, n_blobs=True), "commit, archive pin or blob count"),
                                ("no gated", dict(rec, replay={k: v for k, v in GOOD_REPLAY.items() if k != "gated"}),
                                 "replay gated files"),
                                ("a bool size", dict(rec, deleted=dict(GOOD_DELETED, t0=dict(GOOD_DELETED["t0"], **{
                                    "genie_v3.gst.root": dict(GOOD_DELETED["t0"]["genie_v3.gst.root"], bytes=True)}))),
                                 "deleted t0/genie_v3.gst.root"),
                                ("another seed", dict(rec, replay=dict(GOOD_REPLAY, seed=99)), "replay identity seed"),
                                ("a seed as text", dict(rec, replay=dict(GOOD_REPLAY, seed="123456789")),
                                 "replay identity seed"),
                                ("another tune", dict(rec, replay=dict(GOOD_REPLAY, tune="G18_02a_00_000")),
                                 "replay identity tune"),
                                ("gntpc ran gevgen first", dict(rec, replay=dict(GOOD_REPLAY, execs=dict(
                                    GOOD_REPLAY["execs"], **{"trace_check_gntpc.json": GOOD_REPLAY["execs"][
                                        "trace_check_gevgen.json"]}))), "replay execs"),
                                ("an unbound exec", dict(rec, replay=dict(GOOD_REPLAY, execs=dict(
                                    GOOD_REPLAY["execs"], **{"trace_check_gevgen.json": [dict(
                                        GOOD_REPLAY["execs"]["trace_check_gevgen.json"][0], bound_by=None)]}))),
                                 "replay execs"),
                                ("an exec without its hash", dict(rec, replay=dict(GOOD_REPLAY, execs=dict(
                                    GOOD_REPLAY["execs"], **{"trace_check_gevgen.json": [dict(
                                        GOOD_REPLAY["execs"]["trace_check_gevgen.json"][0], sha256="3" * 63)]}))),
                                 "replay execs"),
                                ("no revision", dict(rec, replay=dict(GOOD_REPLAY, revision={})), "replay revision values"),
                                ("the messenger not gated", dict(rec, replay=dict(GOOD_REPLAY, gated=dict(
                                    GOOD_REPLAY["gated"], **{"trace_check_coverage.json": [
                                        x for x in GOOD_REPLAY["gated"]["trace_check_coverage.json"]
                                        if "Messenger" not in x["path"]]}))),
                                 "replay gated trace_check_coverage.json: Messenger_pg.xml"),
                                ("no gst schema", dict(rec, replay=dict(GOOD_REPLAY, gst_schema=None)),
                                 ["replay gst schema", "deleted t0/genie_v3.gst.root: schema differs from the record's"]),
                                ("no merged schema", dict(rec, replay=dict(GOOD_REPLAY, gst_merged_schema=None)),
                                 ["replay gst merged schema",
                                  "deleted merged/genie_v3_g21_ALL.gst.root: schema differs from the record's"]),
                                ("a schema unlike the deleted gst's", dict(rec, replay=dict(GOOD_REPLAY, gst_schema=dict(
                                    GOOD_REPLAY["gst_schema"], streamer_sha256="6" * 64))),
                                 "deleted t0/genie_v3.gst.root: schema differs from the record's"),
                                ("a merged run missing", dict(rec, deleted={k: v for k, v in GOOD_DELETED.items()
                                                                            if k != "merged"}), "deleted names"),
                                ("a coverage file missing", dict(rec, deleted=dict(GOOD_DELETED, coverage_slot2={
                                    "gevgen.log": REC})), "deleted names"),
                                ("an unknown pin", dict(rec, replay=dict(GOOD_REPLAY, gated=dict(GOOD_REPLAY["gated"], **{
                                    "trace_check_gntpc.json": [{"path": "/p/x.so", "sha256": "0" * 64,
                                                                "pinned_by": "trust me"}]}))), "replay gated files"),
                                ("an unknown binding", dict(rec, replay=dict(GOOD_REPLAY, execs=dict(GOOD_REPLAY["execs"], **{
                                    "trace_check_gntpc.json": [dict(GOOD_REPLAY["execs"]["trace_check_gntpc.json"][0],
                                                                    bound_by="trust me")]}))), "replay execs"),
                                ("the name and bytes not apart", dict(rec, deleted=dict(GOOD_DELETED, coverage_slot1=dict(
                                    COV, **{"gntp.ghep.root": dict(REC, decoded={
                                        "holds_seed": True, "int32_count": 0, "codecs": {}, "bytes_inflated": 9,
                                        "hits": ["inflated"], "seed_objects": [dict(SEED_OBJ, inflated=True, kind="inflated")]
                                    })}))),   # only name_holds_seed missing
                                 "deleted coverage_slot1/gntp.ghep.root"),
                                ("a GHEP in t0", dict(rec, deleted=dict(GOOD_DELETED, t0=dict(
                                    GOOD_DELETED["t0"], **{"gntp.ghep.root": ROOTREC}))), "deleted names"),
                                ("the control not found", dict(rec, deleted=dict(GOOD_DELETED, coverage_slot2=dict(
                                    COV, **{"gntp.ghep.root": ROOTREC}))),
                                 "deleted coverage_slot2/gntp.ghep.root: the control's seed was not found decoded"),
                                ("the control found only raw", dict(rec, deleted=dict(GOOD_DELETED, coverage_slot1=dict(
                                    COV, **{"gntp.ghep.root": dict(CONTROL, decoded=dict(CONTROL["decoded"], **{"hits": ["bytes", "path"]}))}))),
                                 "deleted coverage_slot1/gntp.ghep.root: the control's seed was not found decoded"),
                                ("the control only in a stored object", dict(rec, deleted=dict(GOOD_DELETED, coverage_slot1=dict(
                                    COV, **{"gntp.ghep.root": dict(CONTROL, decoded=dict(CONTROL["decoded"], **{"bytes_inflated": 0, "hits": ["int32-object", "path"]}))}))),
                                 "deleted coverage_slot1/gntp.ghep.root: the control's seed was not found decoded"),
                                ("the control decoded but not held", dict(rec, deleted=dict(GOOD_DELETED, coverage_slot1=dict(
                                    COV, **{"gntp.ghep.root": dict(CONTROL, decoded=dict(CONTROL["decoded"], **{"holds_seed": False}))}))),
                                 "deleted coverage_slot1/gntp.ghep.root: the control's seed was not found decoded"),
                                ("a decode without its hits", dict(rec, deleted=dict(GOOD_DELETED, t0=dict(
                                    GOOD_DELETED["t0"], **{"input-flux.root": dict(ROOTREC, decoded=dict(
                                        ROOTREC["decoded"], hits=None))}))), "deleted t0/input-flux.root"),
                                ("a decode without its seed objects", dict(rec, deleted=dict(GOOD_DELETED, t0=dict(
                                    GOOD_DELETED["t0"], **{"input-flux.root": dict(ROOTREC, decoded=dict(
                                        ROOTREC["decoded"], seed_objects=None))}))), "deleted t0/input-flux.root"),
                                ("a seed object of the wrong shape", dict(rec, deleted=dict(GOOD_DELETED, coverage_slot1=dict(
                                    COV, **{"gntp.ghep.root": dict(CONTROL, decoded=dict(CONTROL["decoded"], seed_objects=[
                                        dict(SEED_OBJ, inflated="no")]))}))), "deleted coverage_slot1/gntp.ghep.root"),
                                ("a seed object of no kind", dict(rec, deleted=dict(GOOD_DELETED, coverage_slot1=dict(
                                    COV, **{"gntp.ghep.root": dict(CONTROL, decoded=dict(CONTROL["decoded"], seed_objects=[
                                        dict(SEED_OBJ, kind="bytes")]))}))), "deleted coverage_slot1/gntp.ghep.root"),
                                ("a seed object without its class", dict(rec, deleted=dict(GOOD_DELETED, coverage_slot1=dict(
                                    COV, **{"gntp.ghep.root": dict(CONTROL, decoded=dict(CONTROL["decoded"], seed_objects=[
                                        {"inflated": False, "kind": "int32-object"}]))}))), "deleted coverage_slot1/gntp.ghep.root"),
                                ("the control with no seed object", dict(rec, deleted=dict(GOOD_DELETED, coverage_slot2=dict(
                                    COV, **{"gntp.ghep.root": dict(CONTROL, decoded=dict(CONTROL["decoded"], seed_objects=[]))}))),
                                 "deleted coverage_slot2/gntp.ghep.root: the control's seed was not found decoded"),
                                ("a gst not decoded", dict(rec, deleted=dict(GOOD_DELETED, t0=dict(GOOD_DELETED["t0"], **{
                                    "genie_v3.gst.root": dict(REC, schema=GOOD_REPLAY["gst_schema"])}))),
                                 "deleted t0/genie_v3.gst.root"),
                                ("no gst schema in deleted", dict(rec, deleted=dict(GOOD_DELETED, t0=dict(
                                    GOOD_DELETED["t0"], **{"genie_v3.gst.root": ROOTREC}))),
                                 ["deleted t0/genie_v3.gst.root: schema differs from the record's",
                                  "deleted t0/genie_v3.gst.root"])):
            with self.subTest(name):
                self.assertEqual(self.L.payload_problems(bad, "covfix-pg-replay/1", pins),
                                 want if isinstance(want, list) else [want])
        for k in ("REPLAY_CHECKS", "TRACES", "SPLINE_TRACES", "SHAPES", "HOST_CHECKS", "DELETABLE", "IDENTITY",
                  "PROGRAM", "GATED"):
            self.assertEqual(getattr(self.L, k), getattr(RP, k), k)                # one schema, in both places

    def test_refusals_and_options(self):
        self.assertEqual(self.launch("exit 0", sha_="0" * 64), 5)
        other = self.tmp / "other.py"
        other.write_text("x")
        self.assertEqual(self.launch("exit 0", sha_=sha(b"x"), script=other), 5)        # not a reviewed node script
        Path(str(self.script) + ".out").write_text("old")
        self.assertEqual(self.launch("exit 0"), 5)
        PL = load("pg_probe_launch", HERE.parent / "probe" / "pg-probe-launch.py")
        self.assertEqual((self.L.SSH_OPTS, self.L.REMOTE, self.L.HOST), (PL.SSH_OPTS, PL.REMOTE, PL.HOST))


DRIVER = """#!/bin/bash
[ "$1" = --workdir ] || exit 2
echo "[replay] stub $PG_STUB_RC"
mkdir -p "$2/work/t0" "$2/coverage/G21_11a_00_000" "$2/coverage/G18_02a_00_000" "$2/gst"
printf '%s' "${PG_STUB_REPLAY:-$GOOD_REPLAY}" > "$2/replay.json"
printf '%s' "${PG_STUB_DELETED:-$GOOD_DELETED}" > "$2/deleted.json"
[ -z "$PG_STUB_STRAGGLER" ] || { sleep 30 > /dev/null 2>&1 & }
[ -z "$PG_STUB_LEFT" ] || echo x > "$2/${PG_STUB_LEFT_DIR:-work/t0}/$PG_STUB_LEFT"
exit ${PG_STUB_RC:-0}
"""


class Replay(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix="pgr-", dir="/tmp")))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        r = self.repo = self.tmp / "repo"
        (r / "3d-unfolding/genie").mkdir(parents=True)
        (r / "3d-unfolding/genie/pg_replay.sh").write_text(DRIVER)
        (r / "3d-unfolding/genie/pg_replay.sh").chmod(0o755)
        (r / "3d-unfolding/genie/gen5d_v3.py").write_text("x = 1\n")
        (r / "setup_salloc_env.sh").write_text("true\n")
        git = ["git", "-C", str(r), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(git[:3] + ["init", "-q"], check=True)
        subprocess.run(git + ["add", "-A"], check=True)
        subprocess.run(git + ["commit", "-qm", "c"], check=True)
        self.paths = ["3d-unfolding/genie", "setup_salloc_env.sh"]
        self.commit = subprocess.run(git[:3] + ["rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        self.data, self.blobs = EA.build(self.commit, r, self.paths)
        self.seen = []

    def run_replay(self, data=None, blobs=None, env=None, **kw):
        import base64

        def run(argv, **k):
            self.seen.append(argv)
            k["env"] = dict(k["env"], GOOD_REPLAY=json.dumps(GOOD_REPLAY), GOOD_DELETED=json.dumps(GOOD_DELETED),
                            **(env or {}))
            return RP._run(argv[5:], **k)                 # without nice and timeout, which macOS lacks; the pid kept
        import datetime as dt
        self.calls = getattr(self, "calls", 0) + 1                # a distinct replay directory per call
        args = dict(now=dt.datetime(2026, 11, 25, 0, 0, self.calls, tzinfo=dt.timezone.utc),
                    parent=str(self.tmp / "scratch"), archive_b64=base64.b64encode(data or self.data).decode(),
                    archive_sha=sha(self.data), blobs=self.blobs if blobs is None else blobs, commit=self.commit,
                    ident=lambda: {"pass": True}, run=run, home=str(self.tmp))
        args.update(kw)
        return RP.replay(**args)

    def assert_stop(self, r, text):
        self.assertEqual(r["verdict"], "STOP", r)
        self.assertTrue(any(text in x for x in r["stops"]), r["stops"])

    def test_go(self):
        r = self.run_replay()
        self.assertEqual(r["verdict"], "GO", r["stops"])
        self.assertEqual(r["n_files_checked"], 3)
        self.assertEqual(self.seen[0][:5], ["/usr/bin/nice", "-n", "19", "/usr/bin/timeout", str(RP.WALL_CAP_S)])
        self.assertEqual(r["driver_lines"], ["[replay] stub "])
        self.assertTrue(r["replay"]["pass"])
        self.assertEqual(sorted(os.listdir(r["replay_dir"])), ["deploy", "driver.log", "run", "tmp"])

    def test_the_archive_and_the_blobs(self):
        import gzip
        import tarfile as tf_
        bad = gzip.compress(b"x" * 100)
        r = self.run_replay(data=bad)
        self.assert_stop(r, "the archive differs from its pin")
        self.assertFalse((self.tmp / "scratch").exists())                         # nothing written
        r = self.run_replay(blobs=dict(self.blobs, **{"3d-unfolding/genie/gen5d_v3.py": "0" * 40}))
        self.assert_stop(r, "blob differs")
        r = self.run_replay(blobs=dict(self.blobs, **{"extra.txt": "0" * 40}))
        self.assert_stop(r, "missing: extra.txt")
        bl = dict(self.blobs)
        bl.pop("setup_salloc_env.sh")
        r = self.run_replay(blobs=bl)
        self.assert_stop(r, "is not a pinned blob")
        buf = io.BytesIO()
        with tf_.open(fileobj=buf, mode="w") as t:
            ti = tf_.TarInfo("3d-unfolding/genie/link")
            ti.type, ti.linkname = tf_.SYMTYPE, "/etc/passwd"
            t.addfile(ti)
        lnk = gzip.compress(buf.getvalue())
        r = self.run_replay(data=lnk, archive_sha=sha(lnk))
        self.assert_stop(r, "neither a directory nor a regular file")
        for d in (self.tmp / "scratch").iterdir():
            self.assertFalse((d / "driver.log").exists())                        # the driver never ran

    def test_the_runners_own_result_passes_the_launcher(self):
        r = self.run_replay()                                                 # B3: the record, whole, both sides
        self.assertEqual(r["verdict"], "GO", r["stops"])
        self.assertEqual(r["replay"], GOOD_REPLAY)
        L = load("pg_node_launch", HERE / "pg-node-launch.py")
        pins = {"COMMIT": self.commit, "ARCHIVE_SHA256": sha(self.data), "BLOBS_JSON": json.dumps(self.blobs)}
        self.assertEqual(L.validate("PG-RESULT " + json.dumps(r), 0, "covfix-pg-replay/1", pins), (True, "verdict GO"))

    def test_files_left_on_any_exit_are_removed_and_stop(self):
        for env in ({"PG_STUB_RC": "4", "PG_STUB_LEFT": "gntp.123456789.ghep.root"},
                    {"PG_STUB_LEFT": "genie_v3_g21_ALL.gst.root", "PG_STUB_LEFT_DIR": "gst"}):
            with self.subTest(env=env):
                r = self.run_replay(env=env)
                self.assertEqual(r["left"], 1)
                self.assert_stop(r, "event or status files were left, now removed")
                d = Path(r["replay_dir"]) / "run" / env.get("PG_STUB_LEFT_DIR", "work/t0")
                self.assertFalse((d / env["PG_STUB_LEFT"]).exists())

    def test_refusals_and_driver_failures(self):
        import datetime as dt
        now = dt.datetime(2026, 11, 24, 12, 0, 0, tzinfo=dt.timezone.utc)
        (self.tmp / "scratch/replay-20261124T120000Z").mkdir(parents=True)
        self.assert_stop(self.run_replay(now=now), "already exists")
        self.assert_stop(self.run_replay(ident=lambda: {"pass": False}), "identity")
        self.assert_stop(self.run_replay(commit="", archive_b64=""), "not embedded")
        self.assert_stop(self.run_replay(env={"PG_STUB_RC": "4"}), "exited 4")
        for name, env, code in (
                ("pass false", {"PG_STUB_REPLAY": json.dumps(dict(GOOD_REPLAY, **{"pass": False}))}, "replay-record"),
                ("an empty checks map", {"PG_STUB_REPLAY": json.dumps(dict(GOOD_REPLAY, checks={}))}, "replay-record"),
                ("a check missing", {"PG_STUB_REPLAY": json.dumps(dict(GOOD_REPLAY, checks={
                    n: True for n in RP.REPLAY_CHECKS[:-1]}))}, "replay-record"),
                ("three shapes", {"PG_STUB_REPLAY": json.dumps(dict(GOOD_REPLAY, real_shapes={"a": True, "b": True,
                                                                                               "c": True}))}, "replay-record"),
                ("a spline open false", {"PG_STUB_REPLAY": json.dumps(dict(GOOD_REPLAY, spline_opened=dict(
                    GOOD_REPLAY["spline_opened"], **{"trace_check_gevgen.json": False})))}, "replay-record"),
                ("no gated files", {"PG_STUB_REPLAY": json.dumps(dict(GOOD_REPLAY, gated={}))}, "replay-record"),
                ("one run's gated list empty", {"PG_STUB_REPLAY": json.dumps(dict(GOOD_REPLAY, gated=dict(
                    GOOD_REPLAY["gated"], **{"trace_check_gevgen.json": []})))}, "replay-record"),
                ("no gst in deleted", {"PG_STUB_DELETED": json.dumps(dict(GOOD_DELETED, t0={"gevgen.status": REC}))},
                 "deleted-record"),
                ("another name deleted", {"PG_STUB_DELETED": json.dumps(dict(GOOD_DELETED, t0=dict(
                    GOOD_DELETED["t0"], **{"x.root": REC})))}, "deleted-record"),
                ("a run missing", {"PG_STUB_DELETED": json.dumps({"t0": GOOD_DELETED["t0"]})}, "deleted-record"),
                ("a bool size", {"PG_STUB_DELETED": json.dumps(dict(GOOD_DELETED, t0=dict(
                    GOOD_DELETED["t0"], **{"gevgen.status": dict(REC, bytes=True)})))}, "deleted-record"),
                ("a negative size", {"PG_STUB_DELETED": json.dumps(dict(GOOD_DELETED, t0=dict(
                    GOOD_DELETED["t0"], **{"gevgen.status": dict(REC, bytes=-1)})))}, "deleted-record"),
                ("another seed", {"PG_STUB_REPLAY": json.dumps(dict(GOOD_REPLAY, seed=99))}, "replay-record"),
                ("a seed as text", {"PG_STUB_REPLAY": json.dumps(dict(GOOD_REPLAY, seed="123456789"))}, "replay-record"),
                ("arbitrary shape names", {"PG_STUB_REPLAY": json.dumps(dict(GOOD_REPLAY, real_shapes={
                    f"s{i}": True for i in range(4)}))}, "replay-record"),
                ("a null gated record", {"PG_STUB_REPLAY": json.dumps(dict(GOOD_REPLAY, gated={
                    n: [None] for n in RP.TRACES}))}, "replay-record"),
                ("no host checks", {"PG_STUB_REPLAY": json.dumps({k: v for k, v in GOOD_REPLAY.items() if k != "host"})},
                 "replay-record"),
                ("no coverage log hashes", {"PG_STUB_REPLAY": json.dumps(dict(GOOD_REPLAY, coverage_log_sha256={}))},
                 "replay-record"),
                ("a coverage log left", {"PG_STUB_LEFT": "gevgen.log", "PG_STUB_LEFT_DIR": "coverage/G21_11a_00_000"},
                 "deleted-record"),
                ("an event file left", {"PG_STUB_LEFT": "gntp.123456789.ghep.root"}, "deleted-record"),
                ("an unknown pin", {"PG_STUB_REPLAY": json.dumps(dict(GOOD_REPLAY, gated=dict(GOOD_REPLAY["gated"], **{
                    "trace_check_gntpc.json": [{"path": "/p/x.so", "sha256": "0" * 64, "pinned_by": "trust me"}]})))},
                 "replay-record"),
                ("an unknown binding", {"PG_STUB_REPLAY": json.dumps(dict(GOOD_REPLAY, execs=dict(GOOD_REPLAY["execs"], **{
                    "trace_check_gntpc.json": [dict(GOOD_REPLAY["execs"]["trace_check_gntpc.json"][0],
                                                    bound_by="trust me")]})))}, "replay-record"),
                ("no merged schema", {"PG_STUB_REPLAY": json.dumps(dict(GOOD_REPLAY, gst_merged_schema=None))},
                 "replay-record"),
                ("a coverage file missing", {"PG_STUB_DELETED": json.dumps(dict(GOOD_DELETED, coverage_slot2={
                    "gevgen.log": REC}))}, "deleted-record"),
                ("a deleted schema unlike the record's", {"PG_STUB_DELETED": json.dumps(dict(GOOD_DELETED, merged={
                    "genie_v3_g21_ALL.gst.root": dict(ROOTREC, schema=GOOD_REPLAY["gst_schema"])}))}, "deleted-record"),
                ("the name and bytes not apart", {"PG_STUB_DELETED": json.dumps(dict(GOOD_DELETED, coverage_slot1=dict(
                    COV, **{"gntp.ghep.root": dict(REC, decoded={
                        "holds_seed": True, "int32_count": 0, "codecs": {}, "bytes_inflated": 9, "hits": ["inflated"],
                        "seed_objects": [dict(SEED_OBJ, inflated=True, kind="inflated")]})})))},   # only name_holds_seed missing
                 "deleted-record"),
                ("a GHEP in t0", {"PG_STUB_DELETED": json.dumps(dict(GOOD_DELETED, t0=dict(
                    GOOD_DELETED["t0"], **{"gntp.ghep.root": ROOTREC})))}, "deleted-record"),
                ("the control not found", {"PG_STUB_DELETED": json.dumps(dict(GOOD_DELETED, coverage_slot1=dict(
                    COV, **{"gntp.ghep.root": ROOTREC})))}, "deleted-record"),
                ("the control found only raw", {"PG_STUB_DELETED": json.dumps(dict(GOOD_DELETED, coverage_slot2=dict(COV, **{
                    "gntp.ghep.root": dict(CONTROL, decoded=dict(CONTROL["decoded"], **{"hits": ["bytes", "path"]}))})))}, "deleted-record"),
                ("the control only in a stored object", {"PG_STUB_DELETED": json.dumps(dict(GOOD_DELETED, coverage_slot2=dict(COV, **{
                    "gntp.ghep.root": dict(CONTROL, decoded=dict(CONTROL["decoded"], **{"bytes_inflated": 0, "hits": ["int32-object", "path"]}))})))}, "deleted-record"),
                ("the control decoded but not held", {"PG_STUB_DELETED": json.dumps(dict(GOOD_DELETED, coverage_slot2=dict(COV, **{
                    "gntp.ghep.root": dict(CONTROL, decoded=dict(CONTROL["decoded"], **{"holds_seed": False}))})))}, "deleted-record"),
                ("a decode without its hits", {"PG_STUB_DELETED": json.dumps(dict(GOOD_DELETED, coverage_slot2=dict(COV, **{
                    "gntp.ghep.root": dict(CONTROL, decoded=dict(CONTROL["decoded"], **{"hits": None}))})))}, "deleted-record"),
                ("a decode without its seed objects", {"PG_STUB_DELETED": json.dumps(dict(GOOD_DELETED, t0=dict(GOOD_DELETED["t0"], **{
                    "input-flux.root": dict(ROOTREC, decoded=dict(ROOTREC["decoded"], seed_objects=None))})))}, "deleted-record"),
                ("a seed object of the wrong shape", {"PG_STUB_DELETED": json.dumps(dict(GOOD_DELETED, coverage_slot2=dict(COV, **{
                    "gntp.ghep.root": dict(CONTROL, decoded=dict(CONTROL["decoded"], seed_objects=[dict(SEED_OBJ, inflated="no")]))})))},
                 "deleted-record"),
                ("a seed object of no kind", {"PG_STUB_DELETED": json.dumps(dict(GOOD_DELETED, coverage_slot2=dict(COV, **{
                    "gntp.ghep.root": dict(CONTROL, decoded=dict(CONTROL["decoded"], seed_objects=[dict(SEED_OBJ, kind="bytes")]))})))},
                 "deleted-record"),
                ("a seed object without its class", {"PG_STUB_DELETED": json.dumps(dict(GOOD_DELETED, coverage_slot2=dict(COV, **{
                    "gntp.ghep.root": dict(CONTROL, decoded=dict(CONTROL["decoded"], seed_objects=[
                        {"inflated": False, "kind": "int32-object"}]))})))}, "deleted-record"),
                ("the control with no seed object", {"PG_STUB_DELETED": json.dumps(dict(GOOD_DELETED, coverage_slot2=dict(COV, **{
                    "gntp.ghep.root": dict(CONTROL, decoded=dict(CONTROL["decoded"], seed_objects=[]))})))}, "deleted-record"),
                ("a straggler in the driver's session", {"PG_STUB_STRAGGLER": "1"}, "quiesce")):
            with self.subTest(name):
                self.assert_stop(self.run_replay(env=env), f"Stop: {code}: ")

    def test_embed_refuses_links(self):
        (self.repo / "3d-unfolding/genie/l").symlink_to("gen5d_v3.py")
        git = ["git", "-C", str(self.repo), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(git + ["add", "-A"], check=True)
        subprocess.run(git + ["commit", "-qm", "l"], check=True)
        with self.assertRaises(SystemExit):
            EA.build("HEAD", self.repo, self.paths)


class Quiesce(unittest.TestCase):
    """K8: the driver's session is KILLed until two scans in a row find it empty, for at most 30 s."""

    def setUp(self):
        self.RP = load("pg_replay_g2111a", HERE / "pg-replay-g2111a.py")

    def test_a_straggler_is_killed_and_the_session_rescanned(self):
        seq, killed = iter([[5], [5], [], []]), []
        n, quiet = self.RP.quiesce(9, scan=lambda: next(seq), kill=lambda q, s: killed.append(q),
                                   clock=lambda: 0.0, sleep=lambda d: None)
        self.assertEqual((n, quiet, killed), (1, True, [5, 5]))

    def test_a_session_that_never_empties(self):
        t = [0.0]
        n, quiet = self.RP.quiesce(9, scan=lambda: [5], kill=lambda q, s: None, clock=lambda: t[0],
                                   sleep=lambda d: t.__setitem__(0, t[0] + d))
        self.assertEqual((n, quiet), (1, False))

    def test_an_empty_session_needs_two_scans(self):
        seq = iter([[], [7], [], []])
        n, quiet = self.RP.quiesce(9, scan=lambda: next(seq), kill=lambda q, s: None, clock=lambda: 0.0,
                                   sleep=lambda d: None)
        self.assertEqual((n, quiet), (1, True))

    def test_the_real_scan_finds_a_session(self):
        child = subprocess.Popen(["sleep", "30"], start_new_session=True)
        self.addCleanup(lambda: (child.kill(), child.wait()))
        self.assertEqual(self.RP.session_pids(child.pid), [child.pid])


class Constants(unittest.TestCase):
    def test_embedded_members_are_the_records(self):
        rec = json.loads((HERE.parent / "record/G2111a-members.json").read_text())
        self.assertEqual(I.MEMBERS, rec)
        self.assertEqual(I.TARBALL_SHA256, rec["tarball_sha256"])
        self.assertTrue(I.URL.endswith("/" + rec["tarball"]))
        self.assertEqual(I.ROOT, "/pscratch/sd/j/josephrb/covfix-pg/products")
        import sys
        sys.path.insert(1, str(HERE.parents[6] / "3d-unfolding/genie"))
        import pg_verify
        self.assertEqual(I.ROOT, pg_verify.PRIVATE_PRODUCTS)
        self.assertEqual(I.DBCONFIG_SHA256, DBCONFIG_PIN)          # filled only from the director's pin
        res = [ln for ln in (HERE.parent / "probe/pg-probe.out").read_text().splitlines()
               if ln.startswith("PG-PROBE-RESULT ")]
        self.assertEqual(len(res), 1)                              # B1's receipt, the pin's source
        b1 = json.loads(res[0][len("PG-PROBE-RESULT "):])
        self.assertEqual(b1["verdict"], "GO")
        self.assertEqual(b1["xsec"]["dbconfig"], {"path": I.DBCONFIG_SRC, "sha256": DBCONFIG_PIN})


class Quiesce7(Quiesce):
    """Round 6's confirm read (R2, the director's ruling): /proc/PID/stat holds the command name as raw bytes."""

    def test_a_name_that_is_not_utf8(self):
        child = subprocess.Popen(["sleep", "30"], start_new_session=True)
        self.addCleanup(lambda: (child.kill(), child.wait()))
        proc = Path(tempfile.mkdtemp(prefix="pg-proc-"))
        self.addCleanup(shutil.rmtree, proc, ignore_errors=True)
        (proc / "self").mkdir()
        (proc / str(child.pid)).mkdir()
        (proc / str(child.pid) / "stat").write_bytes(b"%d (\xff\xfe) x) S 1 %d %d 0" % (child.pid, child.pid, child.pid))
        self.assertEqual(self.RP.session_pids(child.pid, proc=str(proc)), [child.pid])


if __name__ == "__main__":
    unittest.main()
