"""Tests for pg-probe.py and pg-probe-launch.sh on stub CVMFS trees (no cluster, no GENIE, no generated content).

Run: python3 -I -B -m unittest test_pg_probe -v   (from this directory)
"""
import hashlib
import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ.get("PG_REPO_ROOT") or HERE.parents[6])
_spec = importlib.util.spec_from_file_location("pg_probe", HERE / "pg-probe.py")
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)

SPENT_CLS = {"G18_10a_02_11b": ("NievesQELCCPXSec", "NievesSimoVacasMECPXSec"),
             "AR23_20i_00_000": ("NievesQELCCPXSec", "SuSAv2MECPXSec")}
NEW = {"G21_11b_00_000": ("SuSAv2QELPXSec", "SuSAv2MECPXSec"),
       "G18_02b_02_11b": ("LwlynSmithQELCCPXSec", "EmpiricalMECPXSec"),
       "G18_02a_02_11b": ("LwlynSmithQELCCPXSec", "EmpiricalMECPXSec")}


def model_xml(qel, mec, extra=""):
    return (f'<alg_conf>\n <param_set name="Default">\n'
            f'  <param type="alg" name="XSecModel@genie::EventGenerator/QEL-CC"> genie::{qel}/Default </param>\n'
            f'  <param type="alg" name="XSecModel@genie::EventGenerator/MEC-CC">genie::{mec}/Default</param>\n'
            f'{extra} </param_set>\n</alg_conf>\n')


class Stub:
    """A stub genie_xsec product and GENIE config tree."""

    def __init__(self, root, tunes=None, absent=(), noconfig=()):
        self.root = Path(root)
        self.xsec, self.config, self.ups = self.root / "xsec", self.root / "config", self.root / "ups"
        self.tunes = dict(SPENT_CLS, **NEW) if tunes is None else tunes
        self.pins = {}
        for t, (qel, mec) in self.tunes.items():
            if t not in absent:
                d = self.xsec / P.qualifier(t) / "data"
                d.mkdir(parents=True)
                (d / "gxspl-NUsmall.xml").write_text(f"<genie_tune name=\"{t}\">splines of {t}</genie_tune>\n")
                ver = f"version v3_04_00 qualifier {P.qualifier(t).replace('-', ':')}"
                (d / "README").write_text(f"made for {t}\n{ver}\n")
                self.pins[t] = (hashlib.sha256((d / "gxspl-NUsmall.xml").read_bytes()).hexdigest(),
                                hashlib.sha256((d / "README").read_bytes()).hexdigest(), ver)
            if t not in noconfig:
                c = self.config / P.cmc(t)
                c.mkdir(parents=True, exist_ok=True)
                (c / "ModelConfiguration.xml").write_text(model_xml(qel, mec))
        (self.xsec / "SomeOther-k250-e1000").mkdir(parents=True, exist_ok=True)
        self.ups.mkdir(parents=True)
        (self.ups / "genie_xsec.table").write_text('Flavor=NULL\nQualifiers="G2111b00000:k250:e1000"\n'
                                                   '  envSet(GENIE_XSEC_TUNE, G21_11b_00_000)\nother line\n')

    def run(self, gpg_rec=None, **kw):
        orig = P.gpg_check
        P.gpg_check = lambda gpg=None, scratch=None: gpg_rec or {"pass": True}
        try:
            return P.probe(str(self.xsec), str(self.config), str(self.ups), spent_pins=self.pins,
                           spent_classes=SPENT_CLS, **kw)
        finally:
            P.gpg_check = orig


class Decision(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_go_with_02b(self):
        r = Stub(self.tmp).run()
        self.assertEqual(r["verdict"], "GO", r["stops"])
        self.assertEqual(r["decision"]["chosen"], {"u0": "G21_11b_00_000", "u1": "G18_02b_02_11b"})
        self.assertIs(r["decision"]["fallback_taken"], False)
        self.assertEqual(r["decision"]["overlap_with_spent"]["G21_11b_00_000"],
                         {"ccqe": [], "2p2h": ["AR23_20i_00_000"]})
        self.assertTrue(r["decision"]["02a_02b_same_classes"])
        self.assertTrue(any("QEL-CC" in ln and "SuSAv2QELPXSec" in ln for ln in r["classes"]["G21_11b_00_000"]["lines"]))
        self.assertTrue(any("MEC-CC" in ln for ln in r["classes"]["G21_11b_00_000"]["lines"]))
        self.assertIn("SomeOther-k250-e1000", r["qualifiers"])
        self.assertTrue(any("GENIE_XSEC_TUNE" in ln for ln in r["ups"]))
        self.assertFalse(any("other line" in ln for ln in r["ups"]))

    def test_fallback_only_on_absence(self):
        r = Stub(self.tmp, absent=("G18_02b_02_11b",)).run()
        self.assertEqual(r["verdict"], "GO", r["stops"])
        self.assertEqual(r["decision"]["chosen"]["u1"], "G18_02a_02_11b")
        self.assertIs(r["decision"]["fallback_taken"], True)

    def test_02b_excluded_excludes_02a(self):
        t = dict(SPENT_CLS, **NEW)
        t["G18_02b_02_11b"] = ("NievesQELCCPXSec", "SuSAv2MECPXSec")
        r = Stub(self.tmp, tunes=t).run()
        self.assertEqual(r["verdict"], "STOP")
        self.assertIsNone(r["decision"]["chosen"]["u1"])
        self.assertTrue(any(s.startswith("slot 2:") for s in r["stops"]))

    def test_new_pairing_of_spent_classes_is_excluded(self):
        t = dict(SPENT_CLS, **NEW)
        t["G21_11b_00_000"] = ("NievesQELCCPXSec", "SuSAv2MECPXSec")
        r = Stub(self.tmp, tunes=t).run()
        self.assertEqual(r["verdict"], "STOP")
        self.assertIsNone(r["decision"]["chosen"]["u0"])

    def test_cross_slot_class_counts_as_spent(self):
        # a CCQE class spelled like a spent 2p2h class is in the pooled spent set; the other class still qualifies
        t = dict(SPENT_CLS, **NEW)
        t["G21_11b_00_000"] = ("SuSAv2MECPXSec", "NievesQELCCPXSec")
        r = Stub(self.tmp, tunes=t).run()
        self.assertEqual(r["decision"]["status"]["G21_11b_00_000"],
                         "excluded (both classes used by a spent tune)")

    def test_one_novel_class_suffices(self):
        t = dict(SPENT_CLS, **NEW)
        t["G18_02b_02_11b"] = ("NievesQELCCPXSec", "EmpiricalMECPXSec")
        r = Stub(self.tmp, tunes=t).run()
        self.assertEqual(r["decision"]["chosen"]["u1"], "G18_02b_02_11b")

    def test_slot1_absent_stops(self):
        r = Stub(self.tmp, absent=("G21_11b_00_000",)).run()
        self.assertEqual(r["verdict"], "STOP")
        self.assertIn("slot 1: G21_11b_00_000 absent", r["stops"])

    def test_both_02_absent_stops(self):
        r = Stub(self.tmp, absent=("G18_02b_02_11b", "G18_02a_02_11b")).run()
        self.assertEqual(r["verdict"], "STOP")

    def test_present_without_config_is_unresolved_not_fallback(self):
        r = Stub(self.tmp, noconfig=("G18_02b_02_11b",)).run()
        self.assertEqual(r["verdict"], "STOP")
        self.assertEqual(r["decision"]["status"]["G18_02b_02_11b"], "unresolved")
        self.assertIsNone(r["decision"]["chosen"]["u1"])

    def test_incomplete_02b_is_a_stop_not_a_fallback(self):
        s = Stub(self.tmp)
        os.remove(s.xsec / P.qualifier("G18_02b_02_11b") / "data" / "README")
        r = s.run()
        self.assertEqual(r["verdict"], "STOP")
        self.assertTrue(r["decision"]["status"]["G18_02b_02_11b"].startswith("incomplete"))
        self.assertIsNone(r["decision"]["chosen"]["u1"])

    def test_fallback_whose_classes_differ_from_02b_stops(self):
        t = dict(SPENT_CLS, **NEW)
        t["G18_02a_02_11b"] = ("LwlynSmithQELCCPXSec", "SuSAv2MECPXSec")
        r = Stub(self.tmp, tunes=t, absent=("G18_02b_02_11b",)).run()
        self.assertIs(r["decision"]["02a_02b_same_classes"], False)
        self.assertEqual(r["verdict"], "STOP")
        self.assertIn("slot 2: 02a's configured classes differ from 02b's, against section 4.1's premise", r["stops"])

    def test_spent_pin_control(self):
        s = Stub(self.tmp)
        s.pins["AR23_20i_00_000"] = ("0" * 64,) + s.pins["AR23_20i_00_000"][1:]
        r = s.run()
        self.assertEqual(r["verdict"], "STOP")
        self.assertIn("control: AR23_20i_00_000's catalog is not F1's pins", r["stops"])

    def test_spent_version_line_control(self):
        s = Stub(self.tmp)
        s.pins["G18_10a_02_11b"] = s.pins["G18_10a_02_11b"][:2] + ("version v3_02_00 qualifier x",)
        self.assertEqual(s.run()["verdict"], "STOP")

    def test_spent_class_control(self):
        t = dict(SPENT_CLS, **NEW)
        t["G18_10a_02_11b"] = ("NievesQELCCPXSec", "EmpiricalMECPXSec")
        r = Stub(self.tmp, tunes=t).run()
        self.assertIn("control: G18_10a_02_11b's parsed classes are not FD-F1-REPORT 1.3's", r["stops"])

    def test_gpg_failure_stops(self):
        r = Stub(self.tmp).run(gpg_rec={"pass": False})
        self.assertEqual(r["verdict"], "STOP")
        self.assertIn("gpg: the tool or its pinned round trip failed", r["stops"])

    def test_missing_product_stops(self):
        s = Stub(self.tmp)
        shutil.rmtree(s.xsec)
        self.assertEqual(s.run()["verdict"], "STOP")


class Parsing(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_names(self):
        self.assertEqual(P.qualifier("G18_10a_02_11b"), "G1810a0211b-k250-e1000")
        self.assertEqual(P.qualifier("AR23_20i_00_000"), "AR2320i00000-k250-e1000")
        self.assertEqual(P.qualifier("G21_11b_00_000"), "G2111b00000-k250-e1000")
        self.assertEqual(P.cmc("G18_02b_02_11b"), "G18_02b")
        self.assertEqual(P.class_name(" genie::SuSAv2QELPXSec/Default "), "SuSAv2QELPXSec")

    def test_comments_are_ignored(self):
        x = model_xml("SuSAv2QELPXSec", "SuSAv2MECPXSec",
                      '<!-- <param type="alg" name="XSecModel@genie::EventGenerator/QEL-CC"> genie::Old/Default'
                      ' </param> -->\n')
        self.assertEqual(P.xsec_models(x)["QEL-CC"], ["genie::SuSAv2QELPXSec/Default"])

    def test_duplicate_entry_is_unresolved(self):
        s = Stub(self.tmp)
        f = s.config / "G21_11b" / "ModelConfiguration.xml"
        f.write_text(model_xml("SuSAv2QELPXSec", "SuSAv2MECPXSec",
                               '  <param type="alg" name="XSecModel@genie::EventGenerator/QEL-CC">genie::X/Default'
                               '</param>\n'))
        r = s.run()
        self.assertEqual(r["decision"]["status"]["G21_11b_00_000"], "unresolved")
        self.assertEqual(r["verdict"], "STOP")

    def test_tune_subdir_overrides_cmc(self):
        s = Stub(self.tmp)
        sub = s.config / "G18_02b" / "G18_02b_02_11b"
        sub.mkdir()
        (sub / "ModelConfiguration.xml").write_text(
            '<alg_conf><param type="alg" name="XSecModel@genie::EventGenerator/MEC-CC">genie::SuSAv2MECPXSec/Default'
            '</param></alg_conf>')
        (sub / "notes.txt").write_text('name="XSecModel@genie::EventGenerator/QEL-CC"')
        rec = P.model_classes(str(s.config), "G18_02b_02_11b")
        self.assertEqual((rec["ccqe"], rec["2p2h"]), ("LwlynSmithQELCCPXSec", "SuSAv2MECPXSec"))
        self.assertTrue(rec["sources"]["2p2h"].endswith("G18_02b_02_11b/ModelConfiguration.xml"))
        self.assertEqual(len(rec["files"]), 2)

    def test_context_lines_without_xsecmodel_are_kept(self):
        s = Stub(self.tmp)
        f = s.config / "G21_11b" / "ModelConfiguration.xml"
        f.write_text(model_xml("SuSAv2QELPXSec", "SuSAv2MECPXSec", '  <param name="Tune-MEC-CC-Scale">1.0</param>\n'))
        rec = P.model_classes(str(s.config), "G21_11b_00_000")
        self.assertTrue(any("Tune-MEC-CC-Scale" in ln for ln in rec["lines"]))
        self.assertEqual(rec["2p2h"], "SuSAv2MECPXSec")

    def test_peer_tune_dir_overrides_and_conflicts(self):
        s = Stub(self.tmp)
        peer = s.config / "G18_02b_02_11b"
        peer.mkdir()
        mec = ('<alg_conf><param type="alg" name="XSecModel@genie::EventGenerator/MEC-CC">genie::{}/Default'
               '</param></alg_conf>')
        (peer / "ModelConfiguration.xml").write_text(mec.format("SuSAv2MECPXSec"))
        rec = P.model_classes(str(s.config), "G18_02b_02_11b")
        self.assertEqual((rec["ccqe"], rec["2p2h"], rec["problems"]), ("LwlynSmithQELCCPXSec", "SuSAv2MECPXSec", []))
        self.assertEqual(rec["tune_dirs"], [str(peer)])
        nested = s.config / "G18_02b" / "G18_02b_02_11b"
        nested.mkdir()
        (nested / "X.xml").write_text(mec.format("EmpiricalMECPXSec"))
        rec = P.model_classes(str(s.config), "G18_02b_02_11b")
        self.assertTrue(any("disagree" in x for x in rec["problems"]), rec["problems"])
        self.assertFalse(P.resolved(rec))

    def test_other_slots_are_not_read_as_qel(self):
        x = ('<param type="alg" name="XSecModel@genie::EventGenerator/QEL-NC">genie::A/Default</param>'
             '<param type="alg" name="XSecModel@genie::EventGenerator/QEL-CC-CHARM">genie::B/Default</param>')
        self.assertEqual(P.xsec_models(x), {"QEL-CC": [], "MEC-CC": []})

    def test_catalog_reads_only_named_files(self):
        s = Stub(self.tmp)
        c = P.catalog(str(s.xsec), "G21_11b_00_000")
        self.assertEqual(c["readme_version_lines"], ["version v3_04_00 qualifier G2111b00000:k250:e1000"])
        self.assertEqual(c["spline_sha256"], s.pins["G21_11b_00_000"][0])

    def test_probe_writes_nothing_in_cwd(self):
        s = Stub(self.tmp)
        cwd = Path(self.tmp) / "cwd"
        cwd.mkdir()
        old = os.getcwd()
        os.chdir(cwd)
        try:
            s.run()
        finally:
            os.chdir(old)
        self.assertEqual(list(cwd.iterdir()), [])


class Constants(unittest.TestCase):
    def test_spent_pins_are_f1s(self):
        src = (REPO / "3d-unfolding/genie/gen5d_v3.py").read_text()
        block = src[src.index("SPLINE_PINS = {"):src.index("E_LO, E_HI")]
        for t, (a, b, v) in P.SPENT_PINS.items():
            self.assertIn(f'"{t}": ("{a}",', block)
            self.assertIn(f'"{b}",', block)
            self.assertIn(f'"{v}"', block)

    def test_spent_classes_are_f1_reports(self):
        rep = (REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/FD-F1-REPORT.md").read_text()
        sec = rep[rep.index("### 1.3"):rep.index("### 1.4")]
        self.assertIn("G18_10a_02_11b's 2p2h is `NievesSimoVacasMECPXSec`", sec)
        self.assertIn("Both truths use `NievesQELCCPXSec` for CCQE. AR23_20i_00_000's 2p2h is `SuSAv2MECPXSec`", sec)
        self.assertEqual(P.SPENT_CLASSES, SPENT_CLS)

    def test_flags_are_section_42s(self):
        decl = (REPO / "docs/orchestration/state/2d-closeout/covfix-20261122/COVFIX-DECLARATION.md").read_text()
        enc = re.search(r"encrypt: `gpg ([^`]+)`", decl).group(1).split()
        dec = re.search(r"decrypt: `gpg ([^`]+)`", decl).group(1).split()
        self.assertEqual(P.ENCRYPT, enc)
        self.assertEqual(P.DECRYPT, dec)

    def test_tunes(self):
        self.assertEqual(P.SPENT, ("G18_10a_02_11b", "AR23_20i_00_000"))
        self.assertEqual((P.SLOT1, P.SLOT2, P.SLOT2_FALLBACK), ("G21_11b_00_000", "G18_02b_02_11b", "G18_02a_02_11b"))


@unittest.skipUnless(shutil.which("gpg"), "no gpg")
class Gpg(unittest.TestCase):
    """The real local gpg. GNUPGHOME must be short (gpg-agent's socket path limit), so /tmp is used."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(dir="/tmp")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_round_trip_and_controls(self):
        r = P.gpg_check(scratch=self.tmp)
        self.assertTrue(r["pass"], r)
        self.assertNotEqual(r["tampered_decrypt_rc"], 0)
        self.assertNotEqual(r["wrong_passphrase_decrypt_rc"], 0)
        self.assertTrue(r["agents_before_kill"], "agent detection has no positive control")
        self.assertEqual(r["agents_after_kill"], [])
        self.assertTrue(r["user_gnupg_unchanged"])
        self.assertEqual(os.listdir(self.tmp), [])

    def fake_gpg(self):
        """A gpg that 'encrypts' by XOR and never checks integrity or the passphrase."""
        fake = Path(self.tmp) / "bin"
        fake.mkdir()
        g = fake / "gpg"
        g.write_text(f"#!{sys.executable}\nimport sys\nif '--version' in sys.argv: print('fake'); sys.exit(0)\n"
                     "d = sys.stdin.buffer.read(); sys.stdout.buffer.write(bytes(b ^ 0x55 for b in d))\n")
        g.chmod(0o755)
        return str(g)

    def test_a_gpg_without_integrity_fails(self):
        r = P.gpg_check(gpg=self.fake_gpg(), scratch=self.tmp)
        self.assertTrue(r["round_trip_equal"] and r["ciphertext_differs"])
        self.assertEqual(r["tampered_decrypt_rc"], 0)
        self.assertFalse(r["pass"])

    def test_a_surviving_agent_fails(self):
        orig = P._agents
        try:
            P._agents = lambda home: ["4242"]
            r = P.gpg_check(scratch=self.tmp)
        finally:
            P._agents = orig
        self.assertEqual(r["agents_after_kill"], ["4242"])
        self.assertFalse(r["pass"])

    def honest_gpg(self, gpgconf_rc=0):
        """A gpg with integrity and passphrase checks (an HMAC) but no agent, and a gpgconf exiting gpgconf_rc."""
        d = Path(self.tmp) / "hbin"
        d.mkdir()
        g = d / "gpg"
        g.write_text(f"#!{sys.executable}\n" + """import hashlib, hmac, os, sys
if '--version' in sys.argv: print('honest'); sys.exit(0)
pw = os.read(3, 1000).strip()
d = sys.stdin.buffer.read()
if '--symmetric' in sys.argv:
    sys.stdout.buffer.write(hmac.new(pw, d, hashlib.sha256).digest() + bytes(b ^ 0x55 for b in d)); sys.exit(0)
tag, body = d[:32], bytes(b ^ 0x55 for b in d[32:])
if not hmac.compare_digest(tag, hmac.new(pw, body, hashlib.sha256).digest()): sys.exit(2)
sys.stdout.buffer.write(body)
""")
        g.chmod(0o755)
        c = d / "gpgconf"
        c.write_text(f"#!/bin/sh\nexit {gpgconf_rc}\n")
        c.chmod(0o755)
        return str(g)

    def test_honest_gpg_passes(self):
        r = P.gpg_check(gpg=self.honest_gpg(), scratch=self.tmp)
        self.assertTrue(r["pass"], r)
        self.assertEqual(r["agents_before_kill"], [])

    def test_failed_kill_fails(self):
        r = P.gpg_check(gpg=self.honest_gpg(gpgconf_rc=1), scratch=self.tmp)
        self.assertEqual(r["gpgconf_kill_rc"], 1)
        self.assertFalse(r["pass"])

    def test_a_blind_agent_check_fails(self):
        orig = P._agents
        try:
            seen = []
            P._agents = lambda home: seen.append(home) or (None if len(seen) == 1 else [])
            r = P.gpg_check(gpg=self.honest_gpg(), scratch=self.tmp)
            self.assertEqual(len(seen), 2)
        finally:
            P._agents = orig
        self.assertFalse(r["pass"])

    def test_a_touched_user_gnupg_fails(self):
        orig, calls = P._tree_state, []
        try:
            P._tree_state = lambda path: calls.append(path) or {"mtime_ns": len(calls), "entries": []}
            r = P.gpg_check(gpg=self.honest_gpg(), scratch=self.tmp)
        finally:
            P._tree_state = orig
        self.assertEqual(calls, [os.path.expanduser("~/.gnupg")] * 2)
        self.assertFalse(r["user_gnupg_unchanged"])
        self.assertFalse(r["pass"])

    def test_fd3_already_open_fails_cleanly(self):
        if P._fd_open(3):
            self.skipTest("fd 3 is open in this test process")
        fd = os.open(os.devnull, os.O_RDONLY)
        if fd != 3:
            os.dup2(fd, 3)
            os.close(fd)
        try:
            r = P.gpg_check(gpg=self.honest_gpg(), scratch=self.tmp)
            self.assertTrue(P._fd_open(3), "the probe closed an fd it did not own")
        finally:
            os.close(3)
        self.assertFalse(r["pass"])
        self.assertIn("fd 3 is already open", r["problem"])
        self.assertEqual([n for n in os.listdir(self.tmp) if n.startswith("pgprobegnupg")], [])

    def test_a_failing_ps_is_not_read_as_no_agents(self):
        d = Path(self.tmp) / "psbin"
        d.mkdir()
        (d / "ps").write_text("#!/bin/sh\necho '4242 gpg-agent --homedir /h/x'\nexit 1\n")
        (d / "ps").chmod(0o755)
        old = os.environ["PATH"]
        os.environ["PATH"] = f"{d}:{old}"
        try:
            self.assertIsNone(P._agents("/h/x"))
        finally:
            os.environ["PATH"] = old
        (d / "ps").write_text("#!/bin/sh\necho '4242 gpg-agent --homedir /h/x'\necho '7 bash'\n")
        os.environ["PATH"] = f"{d}:{old}"
        try:
            self.assertEqual(P._agents("/h/x"), ["4242"])
        finally:
            os.environ["PATH"] = old

    def test_no_gpg(self):
        orig = shutil.which
        try:
            P.shutil.which = lambda *a, **k: None
            r = P.gpg_check(scratch=self.tmp)
        finally:
            P.shutil.which = orig
        self.assertFalse(r["pass"])
        self.assertEqual(r["problem"], "no gpg on PATH")


class Launcher(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        for n in ("pg-probe.py", "pg-probe-launch.sh"):
            shutil.copy(HERE / n, self.tmp / n)
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        ssh = self.bin / "ssh"
        ssh.write_text(f"#!/bin/sh\necho \"$@\" > {self.tmp}/ssh-args\ncat > {self.tmp}/ssh-stdin\n"
                       "echo PG-PROBE-RESULT stub\nexit 3\n")
        ssh.chmod(0o755)
        self.sha = hashlib.sha256((self.tmp / "pg-probe.py").read_bytes()).hexdigest()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def launch(self, sha):
        env = dict(os.environ, PATH=f"{self.bin}:{os.environ['PATH']}")
        return subprocess.run(["bash", str(self.tmp / "pg-probe-launch.sh"), sha], env=env, capture_output=True,
                              text=True)

    def test_wrong_sha_refuses_without_ssh(self):
        p = self.launch("0" * 64)
        self.assertEqual(p.returncode, 3)
        self.assertFalse((self.tmp / "ssh-args").exists())
        self.assertFalse((self.tmp / "pg-probe.out").exists())

    def test_existing_output_refuses(self):
        (self.tmp / "pg-probe.out").write_text("old\n")
        p = self.launch(self.sha)
        self.assertEqual(p.returncode, 3)
        self.assertFalse((self.tmp / "ssh-args").exists())
        self.assertEqual((self.tmp / "pg-probe.out").read_text(), "old\n")

    def test_runs_the_exact_bytes_and_keeps_rc(self):
        p = self.launch(self.sha)
        self.assertEqual(p.returncode, 3, p.stderr)
        self.assertEqual((self.tmp / "ssh-args").read_text().split(),
                         ["-o", "BatchMode=yes", "saul.nersc.gov", "/usr/bin/python3.11", "-I", "-B", "-"])
        self.assertEqual((self.tmp / "ssh-stdin").read_bytes(), (self.tmp / "pg-probe.py").read_bytes())
        out = (self.tmp / "pg-probe.out").read_text()
        self.assertIn(f"# pg-probe.py sha256 {self.sha}", out)
        self.assertIn("PG-PROBE-RESULT stub", out)
        self.assertIn("# rc 3 at", out)
        self.assertFalse((self.tmp / "pg-probe.out.partial").exists())


if __name__ == "__main__":
    unittest.main()
