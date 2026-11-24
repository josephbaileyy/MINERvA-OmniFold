"""Tests for pg-probe.py (rev 3) and pg-probe-launch.py on stub CVMFS trees: no cluster, no GENIE, no generated
content. Includes the counterexamples of codex-school2's reads 1 and 2 (CODEX2-READ-1.md, CODEX2-READ-2.md).

Run: python3 -I -B test_pg_probe.py -v   (from this directory)
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ.get("PG_REPO_ROOT") or HERE.parents[6])


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


P = load("pg_probe", "pg-probe.py")
LAUNCH = load("pg_probe_launch", "pg-probe-launch.py")

SPENT_CLS = {"G18_10a_02_11b": ("NievesQELCCPXSec", "NievesSimoVacasMECPXSec2016"),
             "AR23_20i_00_000": ("NievesQELCCPXSec", "SuSAv2MECPXSec")}
QEL = {"G18_10a_02_11b": "genie::NievesQELCCPXSec/Dipole", "AR23_20i_00_000": "genie::NievesQELCCPXSec/ZExp",
       "G21_11b_00_000": "genie::HybridXSecAlgorithm/SuSAv2-QEL", "G18_02b_02_11b": "genie::LwlynSmithQELCCPXSec/Dipole",
       "G18_02a_02_11b": "genie::LwlynSmithQELCCPXSec/Dipole"}
MEC = {"G18_10a_02_11b": "genie::NievesSimoVacasMECPXSec2016/Default", "AR23_20i_00_000": "genie::SuSAv2MECPXSec/Default",
       "G21_11b_00_000": "genie::SuSAv2MECPXSec/Default", "G18_02b_02_11b": "genie::EmpiricalMECPXSec2015/Default",
       "G18_02a_02_11b": "genie::EmpiricalMECPXSec2015/Default"}
# The classes and param_sets registered at R-3_04_00 that the stub uses (config/<Class>.xml, master_config.xml).
CLASSES = {"NievesQELCCPXSec": ("Default", "Dipole", "ZExp"), "NievesSimoVacasMECPXSec2016": ("Default",),
           "SuSAv2MECPXSec": ("Default",), "SuSAv2QELPXSec": ("Default",), "LwlynSmithQELCCPXSec": ("Default", "Dipole"),
           "EmpiricalMECPXSec2015": ("Default",), "RosenbluthPXSec": ("Default",)}
HYBRID = """<?xml version="1.0" encoding="ISO-8859-1"?>
<alg_conf>
  <param_set name="Default"> </param_set>
  <param_set name="SuSAv2-QEL">
    <param type="alg" name="DefaultXSecAlg"> genie::SuSAv2QELPXSec/Default </param>
    <param type="alg" name="XSecAlg@Interaction=nu:14;tgt:1000000010;N:2112;proc:Weak[CC],QES;">
      genie::LwlynSmithQELCCPXSec/Dipole </param>
    <param type="alg" name="XSecAlg@Interaction=nu:11;tgt:1000010010;N:2212;proc:EM,QES;"> genie::RosenbluthPXSec/Default </param>
  </param_set>
</alg_conf>
"""
LWLYN_BRANCH = "genie::LwlynSmithQELCCPXSec/Dipole"


def model_xml(qel, mec, extra="", set_name="Default", root="global_param_list"):
    return (f'<?xml version="1.0" encoding="ISO-8859-1"?>\n<{root}>\n <param_set name="{set_name}">\n'
            f'  <param type="alg" name="XSecModel@genie::EventGenerator/QEL-CC"> {qel} </param>\n'
            f'  <!-- <param type="alg" name="XSecModel@genie::EventGenerator/MEC-CC"> genie::Old/Default </param> -->\n'
            f'  <param type="alg" name="XSecModel@genie::EventGenerator/MEC-CC">{mec}</param>\n'
            f'  <param type="alg" name="XSecModel@genie::EventGenerator/RES-CC"> genie::X/Default </param>\n'
            f'{extra} </param_set>\n</{root}>\n')


def spline_xml(tune):
    return (f'<?xml version="1.0" encoding="ISO-8859-1"?>\n<genie_xsec_spline_list version="3.00" uselog="1">\n'
            f'<genie_tune name="{tune}">\n<spline name="x" nknots="1"> <knot> <E> 1 </E> <xsec> 2 </xsec> </knot>'
            f' </spline>\n</genie_tune>\n</genie_xsec_spline_list>\n')


def fake_ident():
    return {"host": "login31", "checks": {}, "pass": True}


class Stub:
    """A stub CVMFS repository: a genie_xsec product (NULL/, ups/) and a genie product (ups/, config/)."""

    def __init__(self, root, absent=(), qel=None, mec=None):
        Path(root).mkdir(parents=True)
        self.root = Path(os.path.realpath(root))
        self.xp, self.gp = self.root / "genie_xsec", self.root / "genie"
        self.xsec, self.config = self.xp / "NULL", self.gp / "config"
        self.qel, self.mec = dict(QEL, **(qel or {})), dict(MEC, **(mec or {}))
        self.pins, table = {}, ["FILE=TABLE", "PRODUCT=genie_xsec"]
        self.config.mkdir(parents=True)
        self.classes = {"HybridXSecAlgorithm": None}
        (self.config / "HybridXSecAlgorithm.xml").write_text(HYBRID)
        for c, sets in CLASSES.items():
            self.register(c, *sets)
        for t in P.ALL_TUNES:
            q = P.qualifier(t)
            qc = q.replace("-", ":")
            if t not in absent:
                d = self.xsec / q / "data"
                d.mkdir(parents=True)
                (d / "gxspl-NUsmall.xml").write_text(spline_xml(t))
                ver = f"version v3_04_00 qualifier {qc}"
                (d / "README").write_text(f"GENIE splines\n   {ver}\n")
                self.pins[t] = (self.sha(d / "gxspl-NUsmall.xml"), self.sha(d / "README"), ver)
                table += ["Flavor=NULL", f'Qualifiers="{qc}"', "  Action=setup",
                          f"    envSet(GENIE_XSEC_TUNE, {t})"]
            c = self.config / P.cmc(t)
            c.mkdir(exist_ok=True)
            (c / "ModelConfiguration.xml").write_text(model_xml(self.qel[t], self.mec[t]))
            (c / t).mkdir(exist_ok=True)
            (c / t / "CommonParam.xml").write_text("<alg_conf/>\n")
        (self.xsec / "SomeOther-k250-e1000").mkdir(parents=True, exist_ok=True)
        table += ["Flavor=NULL", 'Qualifiers="SomeOther:k250:e1000"']
        (self.xp / "ups").mkdir(parents=True)
        self.table = self.xp / "ups" / "genie_xsec.table"
        self.table.write_text("\n".join(table) + "\n")
        (self.gp / "ups").mkdir(parents=True)
        (self.gp / "ups" / "genie.table").write_text("FILE=TABLE\nPRODUCT=genie\nenvSet(GENIE, ${UPS_PROD_DIR})\n")
        self.mounts = f"cvmfs2 {self.root} fuse ro 0 0\n"

    def register(self, cls, *sets):
        """Add genie::<cls> to master_config.xml, with config/<cls>.xml holding the named param_sets."""
        self.classes[cls] = sets
        (self.config / f"{cls}.xml").write_text(
            '<?xml version="1.0"?>\n<alg_conf>\n' + "".join(f' <param_set name="{s}"> </param_set>\n' for s in sets)
            + "</alg_conf>\n")
        self.write_master()

    def write_master(self, extra=""):
        (self.config / "master_config.xml").write_text(
            '<?xml version="1.0" encoding="ISO-8859-1"?>\n<genie_config>\n'
            + "".join(f'   <config alg="genie::{c}">   {c}.xml   </config>\n' for c in self.classes)
            + extra + "</genie_config>\n")

    @staticmethod
    def sha(p):
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()

    @property
    def roots(self):
        return (str(self.xp), str(self.gp))

    def run(self, gpg_rec=None, ident=fake_ident, roots=None, mounts=None):
        return P.probe(str(self.xsec), str(self.table), str(self.gp / "ups/genie.table"), str(self.config),
                       roots or self.roots, ident=ident, gpg=lambda: gpg_rec or {"pass": True}, spent_pins=self.pins,
                       spent_classes=SPENT_CLS, repo=str(self.root), mounts=lambda: mounts or self.mounts)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp())

    def tearDown(self):
        for d, _, fs in os.walk(self.tmp):
            os.chmod(d, 0o700)
        shutil.rmtree(self.tmp)

    def stub(self, sub="s", **kw):
        return Stub(Path(self.tmp) / sub, **kw)


class Decision(Base):
    def test_go_with_02b(self):
        r = self.stub().run()
        self.assertEqual(r["verdict"], "GO", r["stops"])
        self.assertEqual(r["schema"], "covfix-pg-probe/3")
        d = r["decision"]
        self.assertEqual(d["chosen"], {"u0": "G21_11b_00_000", "u1": "G18_02b_02_11b"})
        self.assertIs(d["fallback_taken"], False)
        self.assertEqual(d["eligibility"]["G18_02a_02_11b"], "not considered: 02b is present")
        g21 = r["classes"]["G21_11b_00_000"]
        self.assertEqual((g21["ccqe"], g21["2p2h"]), ("SuSAv2QELPXSec", "SuSAv2MECPXSec"))
        self.assertEqual(g21["components"]["ccqe"], ["LwlynSmithQELCCPXSec", "RosenbluthPXSec", "SuSAv2QELPXSec"])
        src = g21["sources"]["ccqe"]
        self.assertEqual((src["raw"], src["alg"]), ("genie::HybridXSecAlgorithm/SuSAv2-QEL",
                                                    ["HybridXSecAlgorithm", "SuSAv2-QEL"]))
        self.assertTrue(src["hybrid"]["file"].endswith("config/HybridXSecAlgorithm.xml"))
        self.assertEqual(src["hybrid"]["default"]["set"], "Default")
        self.assertEqual([b["set"] for b in src["hybrid"]["branches"]], ["Dipole", "Default"])
        self.assertTrue(g21["sources"]["2p2h"]["registry"]["file"].endswith("config/SuSAv2MECPXSec.xml"))
        self.assertEqual(d["overlap_with_spent_pool"]["G21_11b_00_000"],
                         {"SuSAv2QELPXSec": [], "LwlynSmithQELCCPXSec": [], "RosenbluthPXSec": [],
                          "SuSAv2MECPXSec": ["AR23_20i_00_000"]})
        self.assertEqual(d["novelty"]["G21_11b_00_000"]["branches"]["ccqe"],
                         {"LwlynSmithQELCCPXSec": True, "RosenbluthPXSec": True, "SuSAv2QELPXSec": True})
        self.assertEqual(d["spent_pool"], ["NievesQELCCPXSec", "NievesSimoVacasMECPXSec2016", "SuSAv2MECPXSec"])
        self.assertTrue(d["02a_02b_same_classes"])
        self.assertIn("SomeOther-k250-e1000", r["qualifiers"])
        self.assertEqual(r["catalog"]["G21_11b_00_000"]["status"], "present")
        self.assertEqual(r["catalog"]["G21_11b_00_000"]["readme_version"], "v3_04_00")
        self.assertTrue(r["roots_verified"]["pass"])

    def test_fallback_only_on_confirmed_absence(self):
        r = self.stub(absent=("G18_02b_02_11b",)).run()
        self.assertEqual(r["verdict"], "GO", r["stops"])
        self.assertEqual(r["decision"]["chosen"]["u1"], "G18_02a_02_11b")
        self.assertIs(r["decision"]["fallback_taken"], True)
        self.assertEqual(r["catalog"]["G18_02b_02_11b"]["status"], "absent")

    def test_02b_excluded_excludes_02a(self):
        r = self.stub(qel={"G18_02b_02_11b": "genie::NievesQELCCPXSec/Dipole"},
                      mec={"G18_02b_02_11b": "genie::SuSAv2MECPXSec/Default"}).run()
        self.assertEqual(r["verdict"], "STOP")
        self.assertIsNone(r["decision"]["chosen"]["u1"])
        self.assertIs(r["decision"]["fallback_taken"], False)
        self.assertEqual(r["decision"]["eligibility"]["G18_02a_02_11b"], "not considered: 02b is present")

    def test_new_pairing_of_spent_classes_is_excluded(self):
        r = self.stub(qel={"G18_02b_02_11b": "genie::NievesQELCCPXSec/Default"},
                      mec={"G18_02b_02_11b": "genie::NievesSimoVacasMECPXSec2016/Default"}).run()
        self.assertEqual(r["verdict"], "STOP")
        self.assertEqual(r["decision"]["eligibility"]["G18_02b_02_11b"], "not eligible: both classes in the spent pool")

    def test_cross_slot_class_counts_as_spent(self):
        r = self.stub(qel={"G18_02b_02_11b": "genie::SuSAv2MECPXSec/Default"},
                      mec={"G18_02b_02_11b": "genie::NievesQELCCPXSec/Default"}).run()
        self.assertEqual(r["decision"]["eligibility"]["G18_02b_02_11b"], "not eligible: both classes in the spent pool")

    def test_one_novel_class_suffices(self):
        r = self.stub(qel={"G18_02b_02_11b": "genie::NievesQELCCPXSec/Dipole"}).run()
        self.assertEqual(r["decision"]["chosen"]["u1"], "G18_02b_02_11b")

    def test_overlap_is_against_the_pool_not_the_slot(self):
        r = self.stub(mec={"G18_02b_02_11b": "genie::NievesQELCCPXSec/Default"}).run()
        self.assertEqual(r["decision"]["chosen"]["u1"], "G18_02b_02_11b")
        self.assertEqual(r["decision"]["overlap_with_spent_pool"]["G18_02b_02_11b"]["NievesQELCCPXSec"],
                         ["G18_10a_02_11b", "AR23_20i_00_000"])

    def test_branch_disagreement_is_a_director_stop(self):
        # codex read 2, blocking 1: a novel default with a spent branch, which the tune-wide ORs passed
        s = self.stub(qel={"G18_02b_02_11b": "genie::HybridXSecAlgorithm/SuSAv2-QEL"})
        (s.config / "HybridXSecAlgorithm.xml").write_text(HYBRID.replace(LWLYN_BRANCH, "genie::NievesQELCCPXSec/Dipole"))
        r = s.run()
        self.assertEqual(r["verdict"], "STOP")
        self.assertIn("branches disagree", r["decision"]["eligibility"]["G18_02b_02_11b"])
        self.assertIsNone(r["decision"]["novelty"]["G18_02b_02_11b"]["novel"])

    def test_g21_with_a_plain_ccqe_is_not_section_41s(self):
        # codex read 2, blocking 1: plain LwlynSmith with the expected MEC class returned GO
        r = self.stub(qel={"G21_11b_00_000": "genie::LwlynSmithQELCCPXSec/Dipole"}).run()
        self.assertEqual(r["verdict"], "STOP")
        self.assertIsNone(r["decision"]["chosen"]["u0"])
        self.assertIn("not section 4.1's configuration", r["decision"]["eligibility"]["G21_11b_00_000"])

    def test_g21_hybrid_with_a_spent_branch_stops(self):
        # codex read 2, blocking 1: a novel SuSAv2 default with a spent Nieves branch
        s = self.stub()
        (s.config / "HybridXSecAlgorithm.xml").write_text(HYBRID.replace(LWLYN_BRANCH, "genie::NievesQELCCPXSec/Dipole"))
        r = s.run()
        self.assertEqual(r["verdict"], "STOP")
        self.assertIsNone(r["decision"]["chosen"]["u0"])
        self.assertIn("branches disagree", r["decision"]["eligibility"]["G21_11b_00_000"])

    def test_g21_needs_the_declared_hybrid_set_and_default(self):
        s = self.stub(qel={"G21_11b_00_000": "genie::HybridXSecAlgorithm/Other"})
        (s.config / "HybridXSecAlgorithm.xml").write_text(HYBRID.replace('name="SuSAv2-QEL"', 'name="Other"'))
        self.assertIn("not section 4.1's", s.run()["decision"]["eligibility"]["G21_11b_00_000"])
        s = self.stub("b")
        (s.config / "HybridXSecAlgorithm.xml").write_text(HYBRID.replace("genie::SuSAv2QELPXSec/Default",
                                                                         "genie::LwlynSmithQELCCPXSec/Default"))
        self.assertIn("not section 4.1's", s.run()["decision"]["eligibility"]["G21_11b_00_000"])

    def test_g21_needs_the_declared_2p2h_and_overlap(self):
        r = self.stub(mec={"G21_11b_00_000": "genie::EmpiricalMECPXSec2015/Default"}).run()
        self.assertIn("not section 4.1's", r["decision"]["eligibility"]["G21_11b_00_000"])
        # a spent G18_10a whose 2p2h hybrid also carries SuSAv2MEC: the overlap is no longer AR23's alone
        s = self.stub("b", mec={"G18_10a_02_11b": "genie::HybridXSecAlgorithm/MEC"})
        (s.config / "HybridXSecAlgorithm.xml").write_text(HYBRID.replace(
            "</alg_conf>", '  <param_set name="MEC">\n    <param type="alg" name="DefaultXSecAlg">'
                           'genie::NievesSimoVacasMECPXSec2016/Default</param>\n    <param type="alg" name='
                           '"XSecAlg@Interaction=nu:14;tgt:1000060120;proc:Weak[CC],MEC;">genie::SuSAv2MECPXSec/Default'
                           '</param>\n  </param_set>\n</alg_conf>'))
        r = s.run()
        self.assertTrue(r["decision"]["controls"]["G18_10a_02_11b: classes equal R-3_04_00's"])
        self.assertIn("used by ['G18_10a_02_11b', 'AR23_20i_00_000']",
                      r["decision"]["eligibility"]["G21_11b_00_000"])

    def test_g21_2p2h_must_be_susav2mec_itself(self):
        s = self.stub(qel={"AR23_20i_00_000": "genie::HybridXSecAlgorithm/AR"},
                      mec={"G21_11b_00_000": "genie::FooMECPXSec/Default"})
        s.register("FooMECPXSec", "Default")
        (s.config / "HybridXSecAlgorithm.xml").write_text(HYBRID.replace(
            "</alg_conf>", '  <param_set name="AR">\n    <param type="alg" name="DefaultXSecAlg">'
                           'genie::NievesQELCCPXSec/ZExp</param>\n    <param type="alg" name='
                           '"XSecAlg@Interaction=nu:14;tgt:1000060120;proc:Weak[CC],QES;">genie::FooMECPXSec/Default'
                           '</param>\n  </param_set>\n</alg_conf>'))
        r = s.run()
        self.assertTrue(r["decision"]["controls"]["AR23_20i_00_000: classes equal R-3_04_00's"])
        self.assertIn("2p2h ['FooMECPXSec'] used by ['AR23_20i_00_000']", r["decision"]["eligibility"]["G21_11b_00_000"])

    def test_slot1_absent_stops(self):
        r = self.stub(absent=("G21_11b_00_000",)).run()
        self.assertIn("slot 1: G21_11b_00_000 not eligible: catalog absent", r["stops"])

    def test_both_02_absent_stops(self):
        r = self.stub(absent=("G18_02b_02_11b", "G18_02a_02_11b")).run()
        self.assertEqual(r["verdict"], "STOP")
        self.assertIsNone(r["decision"]["chosen"]["u1"])

    def test_fallback_whose_classes_differ_is_not_chosen(self):
        r = self.stub(absent=("G18_02b_02_11b",), mec={"G18_02a_02_11b": "genie::SuSAv2MECPXSec/Default"}).run()
        d = r["decision"]
        self.assertIs(d["02a_02b_same_classes"], False)
        self.assertEqual(r["verdict"], "STOP")
        self.assertIsNone(d["chosen"]["u1"])
        self.assertIs(d["fallback_taken"], False)
        self.assertIn("differ from 02b", d["eligibility"]["G18_02a_02_11b"])

    def test_fallback_with_unresolved_02b_config_is_not_chosen(self):
        for i, text in enumerate(("<broken", model_xml("genie::NoSuchClass/Default", MEC["G18_02b_02_11b"]))):
            with self.subTest(i):
                s = self.stub(f"f{i}", absent=("G18_02b_02_11b",))
                (s.config / "G18_02b/ModelConfiguration.xml").write_text(text)
                r = s.run()
                self.assertEqual(r["verdict"], "STOP")
                self.assertIsNone(r["decision"]["chosen"]["u1"])
                self.assertIsNone(r["decision"]["02a_02b_same_classes"])
                self.assertIn("premise cannot be checked", r["decision"]["eligibility"]["G18_02a_02_11b"])

    def test_spent_controls(self):
        s = self.stub("a")
        s.pins["AR23_20i_00_000"] = ("0" * 64,) + s.pins["AR23_20i_00_000"][1:]
        self.assertIn("control: AR23_20i_00_000's catalog is not F1's pins", s.run()["stops"])
        s = self.stub("b")
        s.pins["G18_10a_02_11b"] = s.pins["G18_10a_02_11b"][:2] + ("version x",)
        self.assertEqual(s.run()["verdict"], "STOP")
        s = self.stub("c", mec={"G18_10a_02_11b": "genie::NievesSimoVacasMECPXSec/Default"})
        s.register("NievesSimoVacasMECPXSec", "Default")
        r = s.run()
        self.assertTrue(P.resolved(r["classes"]["G18_10a_02_11b"]))
        self.assertIn("control: G18_10a_02_11b's resolved classes are not R-3_04_00's", r["stops"])

    def test_gpg_failure_stops(self):
        self.assertIn("gpg: the tool or its pinned round trip failed", self.stub().run(gpg_rec={"pass": False})["stops"])

    def test_identity_failure_reads_nothing(self):
        s = self.stub()
        called = []
        r = P.probe(str(s.xsec), str(s.table), str(s.gp / "ups/genie.table"), str(s.config), s.roots,
                    ident=lambda: {"host": "nid001", "checks": {}, "pass": False},
                    gpg=lambda: called.append(1) or {"pass": True}, spent_pins=s.pins, spent_classes=SPENT_CLS,
                    repo=str(s.root), mounts=lambda: called.append(2) or s.mounts)
        self.assertEqual(r["verdict"], "STOP")
        self.assertEqual(r["stops"], ["identity: not a Perlmutter login node; nothing was read"])
        for k in ("qualifiers", "catalog", "classes", "gpg", "roots_verified"):
            self.assertNotIn(k, r)
        self.assertEqual(called, [])

    def test_missing_product_stops(self):
        s = self.stub()
        shutil.rmtree(s.xsec)
        self.assertEqual(s.run()["verdict"], "STOP")


class Catalog(Base):
    """codex 1.2 and 2.3: absent, present and unresolved are kept apart, from structural and exact matches."""

    def entry(self, s, t="G18_02b_02_11b"):
        return s.xsec / P.qualifier(t) / "data"

    def test_listed_but_unreadable_02b_is_unresolved_not_absent(self):
        s = self.stub()
        q = s.xsec / P.qualifier("G18_02b_02_11b")
        shutil.rmtree(q)
        q.symlink_to(Path(self.tmp) / "nowhere")
        r = s.run()
        self.assertEqual(r["catalog"]["G18_02b_02_11b"]["status"], "unresolved")
        self.assertIsNone(r["decision"]["chosen"]["u1"])
        self.assertIs(r["decision"]["fallback_taken"], False)
        self.assertEqual(r["verdict"], "STOP")

    def test_declared_in_ups_but_not_listed_is_unresolved(self):
        s = self.stub()
        shutil.rmtree(s.xsec / P.qualifier("G18_02b_02_11b"))
        r = s.run()
        self.assertEqual(r["catalog"]["G18_02b_02_11b"]["status"], "unresolved")
        self.assertEqual(r["verdict"], "STOP")

    def test_spline_header_rules(self):
        t = "G18_02b_02_11b"
        good = spline_xml(t)
        for i, text in enumerate((
                f'<genie_xsec_spline_list>\n<!-- <genie_tune name="{t}"> -->\n</genie_xsec_spline_list>\n',
                good.replace(f'name="{t}"', 'name="G18_02a_02_11b"'),
                good.replace("<genie_xsec_spline_list", "<other").replace("</genie_xsec_spline_list>", "</other>"),
                good.replace("</genie_tune>", f'</genie_tune>\n<genie_tune name="{t}"></genie_tune>'),
                good.replace("<spline ", f'<genie_tune name="x"/><spline ').replace(f'<genie_tune name="{t}">',
                                                                                     "<genie_tune>"),
                good.replace("<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n",
                             '<?xml version="1.0"?>\n<!DOCTYPE g [<!ENTITY e "x">]>\n'),
                good[:-30],
                "")):
            with self.subTest(i):
                s = self.stub(f"s{i}")
                (self.entry(s) / "gxspl-NUsmall.xml").write_text(text)
                r = s.run()
                self.assertEqual(r["catalog"][t]["status"], "unresolved", r["catalog"][t])
                self.assertEqual(r["verdict"], "STOP")

    def test_spline_nested_tune_name_is_not_the_header(self):
        s = self.stub()
        (self.entry(s) / "gxspl-NUsmall.xml").write_text(
            spline_xml("G18_02b_02_11b").replace('<spline name="x"', '<spline name="x"><genie_tune name="y"/></spline>'
                                                                     '<spline name="z"'))
        self.assertEqual(s.run()["catalog"]["G18_02b_02_11b"]["spline_tunes"], ["G18_02b_02_11b"])

    def test_ups_tune_mismatch(self):
        s = self.stub()
        s.table.write_text(s.table.read_text().replace("envSet(GENIE_XSEC_TUNE, G21_11b_00_000)",
                                                       "envSet(GENIE_XSEC_TUNE, X)"))
        self.assertEqual(s.run()["catalog"]["G21_11b_00_000"]["status"], "unresolved")

    def test_readme_qualifier_is_a_whole_field(self):
        qc = "G2111b00000:k250:e1000"
        for i, line in enumerate(("version v3_04_00 qualifier other", f"version v3_04_00 qualifier {qc}:extra",
                                  f"version v3_04_00 qualifier X{qc}", f"version v3_04_00 qualifier {qc} extra",
                                  f"version 3_04_00 qualifier {qc}", f"version v3_04_00 {qc}")):
            with self.subTest(line):
                s = self.stub(f"r{i}")
                (self.entry(s, "G21_11b_00_000") / "README").write_text(line + "\n")
                self.assertEqual(s.run()["catalog"]["G21_11b_00_000"]["status"], "unresolved")

    def test_02b_under_another_qualifier_is_not_absent(self):
        for i, how in enumerate(("listing", "ups-name", "ups-tune")):
            with self.subTest(how):
                s = self.stub(f"o{i}", absent=("G18_02b_02_11b",))
                if how == "listing":
                    (s.xsec / "G1802b0211b-k500-e1000").mkdir()
                elif how == "ups-name":
                    s.table.write_text(s.table.read_text() + 'Flavor=NULL\nQualifiers="G1802b0211b:k500:e1000"\n')
                else:
                    s.table.write_text(s.table.read_text() + 'Flavor=NULL\nQualifiers="x:y"\n'
                                                             '  envSet(GENIE_XSEC_TUNE, G18_02b_02_11b)\n')
                r = s.run()
                self.assertEqual(r["catalog"]["G18_02b_02_11b"]["status"], "unresolved")
                self.assertIs(r["decision"]["fallback_taken"], False)
                self.assertEqual(r["decision"]["eligibility"]["G18_02a_02_11b"],
                                 "not considered: 02b's presence is unresolved")
                self.assertEqual(r["verdict"], "STOP")

    def test_02b_with_a_second_entry_is_unresolved(self):
        s = self.stub()
        (s.xsec / "G1802b0211b-k500-e1000").mkdir()
        self.assertEqual(s.run()["catalog"]["G18_02b_02_11b"]["status"], "unresolved")

    def test_other_tunes_entries_do_not_touch_02b(self):
        s = self.stub(absent=("G18_02b_02_11b",))
        (s.xsec / "G1802b0011b-k250-e1000").mkdir()
        r = s.run()
        self.assertEqual(r["catalog"]["G18_02b_02_11b"]["status"], "absent")
        self.assertEqual(r["verdict"], "GO", r["stops"])

    def test_ups_table_rules(self):
        self.assertEqual(P.ups_table('Qualifiers="a:b"\n envSet(GENIE_XSEC_TUNE, T1)\nQualifiers="c"\n'),
                         {"a:b": "T1", "c": None})
        with self.assertRaises(P.Unresolved):
            P.ups_table('Qualifiers="a"\nQualifiers="a"\n')
        with self.assertRaises(P.Unresolved):
            P.ups_table('Qualifiers="a"\nenvSet(GENIE_XSEC_TUNE, T1)\nenvSet(GENIE_XSEC_TUNE, T2)\n')


class Roots(Base):
    """codex 1.4 and 2.4: the product roots themselves are verified before any content read."""

    def assert_refused(self, r):
        self.assertEqual(r["verdict"], "STOP")
        self.assertFalse(r["roots_verified"]["pass"])
        self.assertTrue(r["stops"][0].startswith("roots: "))
        for k in ("qualifiers", "catalog", "classes"):
            self.assertNotIn(k, r)

    def test_a_root_relocated_outside_the_repository(self):
        s = self.stub()
        elsewhere = Path(self.tmp) / "elsewhere"
        shutil.move(str(s.xp), str(elsewhere))
        s.xp.symlink_to(elsewhere)
        self.assert_refused(s.run())

    def test_a_root_relocated_inside_the_repository_is_followed(self):
        s = self.stub()
        moved = s.root / "moved"
        shutil.move(str(s.xp), str(moved))
        s.xp.symlink_to(moved)
        r = s.run()
        self.assertEqual(r["verdict"], "GO", r["stops"])
        self.assertEqual(r["roots_verified"]["resolved"][str(s.xp)], str(moved))

    def test_mount_rules(self):
        s = self.stub()
        self.assert_refused(s.run(mounts=f"/dev/x {s.root} ext4 rw 0 0\n"))
        self.assert_refused(s.run(mounts="/dev/x / ext4 rw 0 0\n"))
        self.assert_refused(s.run(mounts=f"cvmfs2 {s.root} fuse ro 0 0\ntmpfs {s.gp} tmpfs rw 0 0\n"))
        self.assert_refused(s.run(mounts="srv:/ / nfs rw 0 0\n"))
        self.assertTrue(s.run(mounts=f"/dev/x / ext4 rw 0 0\ncvmfs {s.root.parent} dvs ro 0 0\n")["roots_verified"]["pass"])

    def test_a_root_relocated_beside_the_repository_on_the_same_mount(self):
        s = self.stub()
        elsewhere = s.root.parent / "other-repo"
        shutil.move(str(s.xp), str(elsewhere))
        s.xp.symlink_to(elsewhere)
        self.assert_refused(s.run(mounts=f"cvmfs {s.root.parent} dvs ro 0 0\n"))

    def test_the_repository_must_be_its_own_real_path(self):
        s = self.stub()
        link = Path(self.tmp) / "link"
        link.symlink_to(s.root)
        r = P.probe(str(s.xsec), str(s.table), str(s.gp / "ups/genie.table"), str(s.config), s.roots, ident=fake_ident,
                    gpg=lambda: {"pass": True}, spent_pins=s.pins, spent_classes=SPENT_CLS, repo=str(link),
                    mounts=lambda: f"cvmfs2 {link} fuse ro 0 0\n")
        self.assert_refused(r)

    def test_a_root_that_is_not_a_directory(self):
        s = self.stub()
        f = s.root / "file"
        f.write_text("x")
        self.assert_refused(s.run(roots=(str(f), str(s.gp))))


class Boundary(Base):
    """codex 1.4: reads stay beneath the verified roots, regular files only."""

    def test_spline_link_outside_the_roots(self):
        s = self.stub()
        outside = Path(self.tmp) / "outside.xml"
        outside.write_text(spline_xml("G21_11b_00_000"))
        f = s.xsec / P.qualifier("G21_11b_00_000") / "data/gxspl-NUsmall.xml"
        f.unlink()
        f.symlink_to(outside)
        r = s.run()
        self.assertEqual(r["catalog"]["G21_11b_00_000"]["status"], "unresolved")
        self.assertTrue(any("outside the approved roots" in x for x in r["catalog"]["G21_11b_00_000"]["problems"]))

    def test_config_link_outside_the_roots(self):
        s = self.stub()
        outside = Path(self.tmp) / "mc.xml"
        outside.write_text(model_xml("genie::LwlynSmithQELCCPXSec/Dipole", "genie::EmpiricalMECPXSec2015/Default"))
        f = s.config / "G18_02b/ModelConfiguration.xml"
        f.unlink()
        f.symlink_to(outside)
        r = s.run()
        self.assertFalse(P.resolved(r["classes"]["G18_02b_02_11b"]))
        self.assertEqual(r["verdict"], "STOP")

    def test_non_regular_config(self):
        s = self.stub()
        (s.config / "G18_02b/G18_02b_02_11b/ModelConfiguration.xml").mkdir()
        r = s.run()
        self.assertTrue(any("not a regular file" in x for x in r["classes"]["G18_02b_02_11b"]["problems"]))

    def test_lookup_rules(self):
        s = self.stub()
        self.assertTrue(P.is_regular(str(s.config / "master_config.xml"), s.roots))
        for bad in (s.config / "nothing.xml", s.config / "G18_02b"):
            with self.assertRaises(P.Unresolved):
                P.is_regular(str(bad), s.roots)
        (s.config / "dangling.xml").symlink_to(s.config / "gone.xml")
        with self.assertRaises(P.Unresolved):
            P.is_regular(str(s.config / "dangling.xml"), s.roots)
        self.assertTrue(P._absent(str(s.config / "nothing")))
        self.assertFalse(P._absent(str(s.config / "dangling.xml")))

    def test_read_file_refuses_a_fifo_and_an_escape(self):
        s = self.stub()
        f = s.config / "fifo.xml"
        os.mkfifo(f)
        with self.assertRaises(P.Unresolved):
            P.read_file(str(f), s.roots)
        with self.assertRaises(P.Unresolved):
            P.read_file(str(s.config / ".." / ".." / ".." / "x"), s.roots)

    def test_reads_are_relative_to_the_verified_root(self):
        s = self.stub()
        seen = []
        orig = P.os.open

        def spy(path, flags, mode=0o777, *, dir_fd=None):
            seen.append((path, dir_fd))
            return orig(path, flags, mode, dir_fd=dir_fd)
        P.os.open = spy
        try:
            P.read_file(str(s.config / "master_config.xml"), s.roots)
        finally:
            P.os.open = orig
        self.assertEqual(seen[0], (str(s.gp), None))
        self.assertEqual(seen[1][0], "config/master_config.xml")
        self.assertIsNotNone(seen[1][1])


class Config(Base):
    """codex 1.1 and 2.2: structural parsing, GENIE's file selection and registry, STOP on anything unexpected."""

    def classes(self, s, t="G18_02b_02_11b", ups=""):
        return P.model_classes(str(s.config), ups, t, s.roots)

    def test_blank_value_is_unresolved_not_novel(self):
        rec = self.classes(self.stub(qel={"G18_02b_02_11b": "   "}))
        self.assertFalse(P.resolved(rec))
        self.assertTrue(any("empty value" in x for x in rec["problems"]))

    def test_unregistered_class_or_set_is_unresolved_not_novel(self):
        # codex read 2, blocking 2: genie::NoSuchClass/NoSuchSet counted as novel
        for i, (q, why) in enumerate((("genie::NoSuchClass/NoSuchSet", "0 entries for genie::NoSuchClass"),
                                      ("genie::NoSuchClass", "0 entries for genie::NoSuchClass"),
                                      ("genie::LwlynSmithQELCCPXSec/NoSuchSet", "0 param_set named 'NoSuchSet'"),
                                      ("genie::LwlynSmithQELCCPXSec/ZExp", "0 param_set named 'ZExp'"))):
            with self.subTest(q):
                s = self.stub(f"n{i}", qel={"G18_02b_02_11b": q})
                r = s.run()
                rec = r["classes"]["G18_02b_02_11b"]
                self.assertFalse(P.resolved(rec))
                self.assertTrue(any(why in x for x in rec["problems"]), rec["problems"])
                self.assertEqual(r["decision"]["eligibility"]["G18_02b_02_11b"], "not eligible: configuration unresolved")
                self.assertEqual(r["verdict"], "STOP")

    def test_unregistered_hybrid_leaf_is_unresolved(self):
        for i, leaf in enumerate(("genie::NoSuchClass/Default", "genie::LwlynSmithQELCCPXSec/NoSuchSet")):
            with self.subTest(leaf):
                s = self.stub(f"l{i}")
                (s.config / "HybridXSecAlgorithm.xml").write_text(HYBRID.replace(LWLYN_BRANCH, leaf))
                self.assertFalse(P.resolved(self.classes(s, "G21_11b_00_000")))
        s = self.stub("d")
        (s.config / "HybridXSecAlgorithm.xml").write_text(HYBRID.replace("genie::SuSAv2QELPXSec/Default",
                                                                         "genie::SuSAv2QELPXSec/Other"))
        self.assertFalse(P.resolved(self.classes(s, "G21_11b_00_000")))

    def test_registry_rules(self):
        s = self.stub("dup")
        s.write_master('   <config alg="genie::EmpiricalMECPXSec2015"> Other.xml </config>\n')
        self.assertTrue(any("2 entries" in x for x in self.classes(s)["problems"]))
        s = self.stub("gone")
        (s.config / "EmpiricalMECPXSec2015.xml").unlink()
        self.assertTrue(any("no EmpiricalMECPXSec2015.xml" in x for x in self.classes(s)["problems"]))
        s = self.stub("root")
        (s.config / "EmpiricalMECPXSec2015.xml").write_text('<global_param_list><param_set name="Default"/>'
                                                            '</global_param_list>')
        self.assertFalse(P.resolved(self.classes(s)))
        s = self.stub("two")
        s.register("EmpiricalMECPXSec2015", "Default", "Default")
        self.assertTrue(any("2 param_set named 'Default'" in x for x in self.classes(s)["problems"]))
        s = self.stub("mroot")
        (s.config / "master_config.xml").write_text("<alg_conf/>")
        self.assertTrue(any("root <alg_conf>" in x for x in self.classes(s)["problems"]))

    def test_tune_directory_registry_file_replaces_the_default(self):
        s = self.stub()
        (s.config / "G18_02b/G18_02b_02_11b/EmpiricalMECPXSec2015.xml").write_text(
            '<alg_conf><param_set name="Other"/></alg_conf>')
        rec = self.classes(s)
        self.assertTrue(any("0 param_set named 'Default'" in x for x in rec["problems"]))

    def test_an_unreadable_directory_does_not_fall_through(self):
        # codex read 2, blocking 2: lexists() turned a failed lookup into a search of the next directory
        s = self.stub()
        d = s.config / "G18_02b/G18_02b_02_11b"
        os.chmod(d, 0)
        try:
            rec = self.classes(s)
        finally:
            os.chmod(d, 0o700)
        self.assertFalse(P.resolved(rec))
        s = self.stub("b")
        shutil.rmtree(d := s.config / "G18_02b/G18_02b_02_11b")
        d.symlink_to(Path(self.tmp) / "missing")
        self.assertFalse(P.resolved(self.classes(s)))
        s = self.stub("c")
        shutil.rmtree(s.config / "G18_02b/G18_02b_02_11b")
        self.assertTrue(P.resolved(self.classes(s)))

    def test_an_unsearchable_directory_does_not_fall_through(self):
        s = self.stub()
        cmcd = s.config / "G18_02b"
        (cmcd / "ModelConfiguration.xml").rename(s.config / "ModelConfiguration.xml")
        self.assertTrue(P.resolved(self.classes(s)))
        os.chmod(cmcd, 0o400)
        try:
            rec = self.classes(s)
        finally:
            os.chmod(cmcd, 0o700)
        self.assertFalse(P.resolved(rec), rec)

    def test_character_reference_is_decoded(self):
        s = self.stub(qel={"G18_02b_02_11b": "genie::&#78;ievesQELCCPXSec/Dipole"},
                      mec={"G18_02b_02_11b": "genie::SuSAv2&#77;ECPXSec/Default"})
        self.assertEqual((self.classes(s)["ccqe"], self.classes(s)["2p2h"]), ("NievesQELCCPXSec", "SuSAv2MECPXSec"))
        self.assertEqual(s.run()["decision"]["eligibility"]["G18_02b_02_11b"],
                         "not eligible: both classes in the spent pool")

    def test_malformed_xml(self):
        s = self.stub()
        (s.config / "G18_02b/ModelConfiguration.xml").write_text(model_xml("genie::A/B", "genie::C/D")[:-20])
        self.assertTrue(any("malformed XML" in x for x in self.classes(s)["problems"]))

    def test_doctype_is_refused(self):
        s = self.stub()
        x = model_xml("genie::A/B", "genie::C/D").replace("<global_param_list>",
                                                          '<!DOCTYPE g [<!ENTITY e "N">]>\n<global_param_list>')
        (s.config / "G18_02b/ModelConfiguration.xml").write_text(x)
        self.assertTrue(any("DOCTYPE" in x for x in self.classes(s)["problems"]))

    def test_inactive_set_supplies_nothing(self):
        s = self.stub()
        (s.config / "G18_10a/ModelConfiguration.xml").write_text(
            model_xml("genie::NievesQELCCPXSec/Dipole", "genie::NievesSimoVacasMECPXSec2016/Default",
                      set_name="Other"))
        r = s.run()
        self.assertFalse(P.resolved(r["classes"]["G18_10a_02_11b"]))
        self.assertIn("control: G18_10a_02_11b's resolved classes are not R-3_04_00's", r["stops"])

    def test_a_second_set_is_ignored(self):
        s = self.stub()
        x = model_xml("genie::LwlynSmithQELCCPXSec/Dipole", "genie::EmpiricalMECPXSec2015/Default")
        x = x.replace("</global_param_list>", ' <param_set name="Other">\n  <param type="alg" name='
                      '"XSecModel@genie::EventGenerator/QEL-CC">genie::Q/Default</param>\n </param_set>\n'
                      '</global_param_list>')
        (s.config / "G18_02b/ModelConfiguration.xml").write_text(x)
        self.assertEqual(self.classes(s)["ccqe"], "LwlynSmithQELCCPXSec")

    def test_two_default_sets(self):
        s = self.stub()
        x = model_xml("genie::A/B", "genie::C/D")
        (s.config / "G18_02b/ModelConfiguration.xml").write_text(
            x.replace("</global_param_list>", ' <param_set name="Default"/>\n</global_param_list>'))
        self.assertTrue(any("2 param_set" in x for x in self.classes(s)["problems"]))

    def test_duplicate_parameter(self):
        s = self.stub()
        (s.config / "G18_02b/ModelConfiguration.xml").write_text(model_xml(
            "genie::A/B", "genie::C/D", '  <param type="alg" name="XSecModel@genie::EventGenerator/QEL-CC">genie::E/F'
                                        '</param>\n'))
        self.assertTrue(any("twice" in x for x in self.classes(s)["problems"]))

    def test_wrong_root_type_and_value_form(self):
        s = self.stub()
        s.register("A", "Default", "B")
        s.register("C", "D")
        f = s.config / "G18_02b/ModelConfiguration.xml"
        f.write_text(model_xml("genie::A/B", "genie::C/D", root="alg_conf"))
        self.assertTrue(any("root <alg_conf>" in x for x in self.classes(s)["problems"]))
        f.write_text(model_xml("genie::A/B", "genie::C/D").replace(
            'type="alg" name="XSecModel@genie::EventGenerator/QEL-CC"',
            'type="string" name="XSecModel@genie::EventGenerator/QEL-CC"'))
        self.assertTrue(any("not alg" in x for x in self.classes(s)["problems"]))
        for bad in ("genie::A/B/C", "A/B", "genie::A B/C", "genie::/B", "genie::A/B C"):
            f.write_text(model_xml(bad, "genie::C/D"))
            with self.subTest(bad):
                self.assertFalse(P.resolved(self.classes(s)))
        f.write_text(model_xml("genie::A/B", "genie::C/D"))
        self.assertEqual(self.classes(s)["sources"]["ccqe"]["registry"]["set"], "B")
        f.write_text(model_xml("genie::A", "genie::C/D"))
        rec = self.classes(s)
        self.assertEqual((rec["ccqe"], rec["sources"]["ccqe"]["alg"]), ("A", ["A", "Default"]))

    def test_tune_directory_file_replaces_the_cmc_file(self):
        s = self.stub()
        s.register("TuneQEL", "Default")
        s.register("TuneMEC", "Default")
        (s.config / "G18_02b/G18_02b_02_11b/ModelConfiguration.xml").write_text(
            model_xml("genie::TuneQEL/Default", "genie::TuneMEC/Default"))
        rec = self.classes(s)
        self.assertEqual((rec["ccqe"], rec["2p2h"]), ("TuneQEL", "TuneMEC"))
        self.assertTrue(rec["file"].endswith("G18_02b/G18_02b_02_11b/ModelConfiguration.xml"))

    def test_other_xml_in_the_tune_directory_is_not_an_override(self):
        s = self.stub()
        (s.config / "G18_02b/G18_02b_02_11b/Extra.xml").write_text(model_xml("genie::X/Y", "genie::Z/W"))
        self.assertEqual(self.classes(s)["ccqe"], "LwlynSmithQELCCPXSec")

    def test_default_path_is_the_last_resort(self):
        s = self.stub()
        s.register("RootQEL", "Default")
        s.register("RootMEC", "Default")
        (s.config / "G18_02b/ModelConfiguration.xml").unlink()
        (s.config / "ModelConfiguration.xml").write_text(model_xml("genie::RootQEL/Default", "genie::RootMEC/Default"))
        self.assertEqual(self.classes(s)["ccqe"], "RootQEL")

    def test_search_path_variables_in_the_genie_table_stop(self):
        s = self.stub()
        (s.gp / "ups/genie.table").write_text("envSet(GXMLPATH, /somewhere)\n")
        r = s.run()
        self.assertTrue(all(not P.resolved(r["classes"][t]) for t in P.ALL_TUNES))
        self.assertEqual(r["verdict"], "STOP")

    def test_hybrid_refusals(self):
        for i, text in enumerate((HYBRID.replace('name="DefaultXSecAlg"', 'name="Other"'),
                                  HYBRID.replace('name="SuSAv2-QEL"', 'name="X"'),
                                  HYBRID.replace(LWLYN_BRANCH, "  "))):
            with self.subTest(i):
                s = self.stub(f"h{i}")
                (s.config / "HybridXSecAlgorithm.xml").write_text(text)
                self.assertFalse(P.resolved(self.classes(s, "G21_11b_00_000")))
        s = self.stub("x")
        (s.config / "HybridXSecAlgorithm.xml").write_text(HYBRID.replace(
            "  </param_set>\n</alg_conf>", '    <param type="alg" name="Other">genie::Z/Default</param>\n  </param_set>\n</alg_conf>'))
        self.assertFalse(P.resolved(self.classes(s, "G21_11b_00_000")))
        s = self.stub("m")
        del s.classes["HybridXSecAlgorithm"]
        s.write_master()
        self.assertFalse(P.resolved(self.classes(s, "G21_11b_00_000")))
        s = self.stub("r")
        (s.config / "HybridXSecAlgorithm.xml").write_text(HYBRID.replace("alg_conf", "global_param_list"))
        self.assertFalse(P.resolved(self.classes(s, "G21_11b_00_000")))


class Constants(unittest.TestCase):
    def test_spent_pins_are_f1s(self):
        src = (REPO / "3d-unfolding/genie/gen5d_v3.py").read_text()
        block = src[src.index("SPLINE_PINS = {"):src.index("E_LO, E_HI")]
        for t, (a, b, v) in P.SPENT_PINS.items():
            self.assertIn(f'"{t}": ("{a}",', block)
            self.assertIn(f'"{b}",', block)
            self.assertIn(f'"{v}"', block)
            self.assertTrue(P.VERSION_LINE.fullmatch(v))

    def test_spent_classes(self):
        self.assertEqual(P.SPENT_CLASSES, SPENT_CLS)

    def test_f1_report_names_are_grep_prefixes_of_the_classes(self):
        rep = (REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/FD-F1-REPORT.md").read_text()
        sec = rep[rep.index("### 1.3"):rep.index("### 1.4")]
        names = set(re.findall(r"`([A-Za-z0-9]+PXSec)`", sec))
        self.assertEqual(names, {"NievesSimoVacasMECPXSec", "NievesQELCCPXSec", "SuSAv2MECPXSec"})
        for pair in P.SPENT_CLASSES.values():
            for c in pair:
                self.assertTrue(c in names or any(c.startswith(n) and c[len(n):].isdigit() for n in names), c)
        self.assertNotIn("NievesSimoVacasMECPXSec2016", names)

    def test_flags_are_section_42s(self):
        decl = (REPO / "docs/orchestration/state/2d-closeout/covfix-20261122/COVFIX-DECLARATION.md").read_text()
        self.assertEqual(P.ENCRYPT, re.search(r"encrypt: `gpg ([^`]+)`", decl).group(1).split())
        self.assertEqual(P.DECRYPT, re.search(r"decrypt: `gpg ([^`]+)`", decl).group(1).split())

    def test_tunes_and_names(self):
        self.assertEqual((P.SLOT1, P.SLOT2, P.SLOT2_FALLBACK), ("G21_11b_00_000", "G18_02b_02_11b", "G18_02a_02_11b"))
        self.assertEqual(P.qualifier("G21_11b_00_000"), "G2111b00000-k250-e1000")
        self.assertEqual(P.cmc("G18_02b_02_11b"), "G18_02b")
        self.assertEqual(P.ROOTS[0], P.CVMFS_REPO + "/products/genie_xsec/v3_04_00")
        self.assertEqual((LAUNCH.SCHEMA, LAUNCH.TUNES), (P.SCHEMA, P.ALL_TUNES))

    def test_identity_rules(self):
        r = P.identity()
        self.assertFalse(r["pass"])                                  # this laptop is not a login node
        self.assertEqual(sorted(r["checks"]), ["/global/common", "/pscratch", "CVMFS products", "hostname login<NN>"])

    def test_mount_fs(self):
        m = "tmpfs /tmp tmpfs rw 0 0\n/dev/x / ext4 rw 0 0\nlus /pscratch lustre rw 0 0\n"
        self.assertEqual(P.mount_fs("/tmp/x", m), "tmpfs")
        self.assertEqual(P.mount_fs("/pscratch/sd/j", m), "lustre")
        self.assertEqual(P.mount_fs("/home", m), "ext4")
        self.assertEqual(P.mount_fs("/tmpx", m), "ext4")
        self.assertEqual(P.mount_entry("/tmp/x", m), ("/tmp", "tmpfs", "tmpfs"))

    def test_zbase32_vectors_from_gnupg(self):
        # common/t-zb32.c at gnupg-2.2.27
        for bits, data, want in ((1, b"\x00", "y"), (1, b"\x80", "o"), (2, b"\x40", "e"), (2, b"\xc0", "a"),
                                 (10, b"\x00\x00", "yy"), (10, b"\x80\x80", "on"), (20, b"\x8b\x88\x80", "tqre"),
                                 (24, b"\xf0\xbf\xc7", "6n9hq"), (24, b"\xd4\x7a\x04", "4t7ye"),
                                 (30, b"\xf5\x57\xbd\x0c", "6im54d"), (40, b"\x01" * 5, "yryonyeb"),
                                 (15, b"\x01\x01", "yry"), (80, b"\x01" * 10, "yryonyebyryonyeb"),
                                 (15, b"\x81\x81", "ogy"), (16, b"\x81\x81", "ogyo"), (20, b"\x81\x81\x81", "ogya"),
                                 (64, b"\x81" * 8, "ogyadycbogyan"),
                                 (160, bytes.fromhex("80615870f5bad690333686d0f2ad85ac1e42b367"),
                                  "oboioh8izmmjyc3so5exfmcfioxrfc58")):
            self.assertEqual(P.zb32(data, bits), want, (bits, data))

    def test_socketdir_for(self):
        sd = P.socketdir_for("/tmp/pgprobeabc", 1234)
        self.assertTrue(sd.startswith("/run/user/1234/gnupg/d."))
        self.assertEqual(len(sd.rsplit(".", 1)[1]), 24)
        self.assertEqual(sd, "/run/user/1234/gnupg/d." + _zb32_groups(hashlib.sha1(b"/tmp/pgprobeabc").digest()[:15]))


def _zb32_groups(b):
    """An independent zbase32 of whole 5-byte groups, transcribed from zb32_encode's straight-line code."""
    a, out = "ybndrfg8ejkmcpqxot1uwisza345h769", ""
    for i in range(0, len(b), 5):
        s = b[i:i + 5]
        out += "".join(a[x] for x in (s[0] >> 3, ((s[0] & 7) << 2) | (s[1] >> 6), (s[1] & 63) >> 1,
                                       ((s[1] & 1) << 4) | (s[2] >> 4), ((s[2] & 15) << 1) | (s[3] >> 7),
                                       (s[3] & 127) >> 2, ((s[3] & 3) << 3) | (s[4] >> 5), s[4] & 31))
    return out


HONEST = r"""import hashlib, hmac, os, sys
open(MARK, 'a').write(' '.join(sys.argv[1:]) + '\n')
if '--version' in sys.argv: print('honest'); sys.exit(0)
pw = os.read(3, 1000).strip()
d = sys.stdin.buffer.read()
def pkt(tag, body): return (bytes([0xC0 | tag, len(body)]) if len(body) < 192 else bytes([0xC0 | tag, 255]) + len(body).to_bytes(4, 'big')) + body
if '--symmetric' in sys.argv:
    body = bytes(b ^ 0x55 for b in d) + hmac.new(pw, d, hashlib.sha256).digest()
    sys.stdout.buffer.write(pkt(3, b'\x04\x09\x03') + pkt(SEIPD_TAG, b'\x01' + body)); sys.exit(0)
b = d[5:]
body = b[6:] if b[1] == 255 else b[2:]
data, tag = bytes(x ^ 0x55 for x in body[1:-32]), body[-32:]
want = hmac.new(pw, data, hashlib.sha256).digest()
if hmac.compare_digest(tag, want):
    sys.stdout.buffer.write(data); sys.exit(0)
CRASH
if want[:-1] == tag[:-1]:
    sys.stderr.write('gpg: WARNING: encrypted message has been manipulated!\n'); sys.exit(2)
sys.stderr.write('gpg: decryption failed: Bad session key\n'); sys.exit(2)
""".replace("SEIPD_TAG", "18")

GPGCONF = r"""import hashlib, os, sys
h = os.environ['GNUPGHOME']
def zb(b):
    a, out = 'ybndrfg8ejkmcpqxot1uwisza345h769', ''
    for i in range(0, len(b), 5):
        s = b[i:i + 5]
        out += ''.join(a[x] for x in (s[0] >> 3, ((s[0] & 7) << 2) | (s[1] >> 6), (s[1] & 63) >> 1,
                                      ((s[1] & 1) << 4) | (s[2] >> 4), ((s[2] & 15) << 1) | (s[3] >> 7),
                                      (s[3] & 127) >> 2, ((s[3] & 3) << 3) | (s[4] >> 5), s[4] & 31))
    return out
sd = h if BASE is None else f'{BASE}/{os.getuid()}/gnupg/d.' + zb(hashlib.sha1(h.encode()).digest()[:15])
if '--list-dirs' in sys.argv:
    if sd != h and not os.path.isdir(sd):
        os.mkdir(sd, 0o700)
    print(LISTING)
if '--remove-socketdir' in sys.argv and REMOVE and sd != h:
    os.rmdir(sd)
sys.exit(KILL_RC if '--kill' in sys.argv else LIST_RC if '--list-dirs' in sys.argv else 0)
"""


def fake_bins(tmp, gpg_body=HONEST, conf_rc=0, agent_out="D 4242\\nOK\\n", dirs=None, base=None, remove=True,
              listing=None, list_rc=0):
    d = Path(tmp) / "fbin"
    d.mkdir(exist_ok=True)
    mark = Path(tmp) / "gpg-calls"
    (d / "gpg").write_text(f"#!{sys.executable}\nMARK = {str(mark)!r}\n" + gpg_body.replace("CRASH", ""))
    listing = listing or (repr(dirs) if dirs is not None else
                          "f'homedir:{h}\\nsocketdir:{sd}\\nagent-socket:{sd}/S.gpg-agent\\nagent-ssh-socket:{sd}/S.gpg-agent.ssh'")
    (d / "gpgconf").write_text(f"#!{sys.executable}\n" + GPGCONF.replace("BASE", repr(base)).replace(
        "LISTING", listing).replace("REMOVE", repr(remove)).replace("KILL_RC", str(conf_rc)).replace("LIST_RC", str(list_rc)))
    (d / "gpg-connect-agent").write_text(f"#!/bin/sh\nprintf '{agent_out}'\n")
    for n in ("gpg", "gpgconf", "gpg-connect-agent"):
        (d / n).chmod(0o755)
    return {n: str(d / n) for n in ("gpg", "gpgconf", "gpg-connect-agent")}


class GpgFakes(Base):
    """codex 1.7, 1.8 and 2.6 with fake executables: each check fails on its own."""

    MOUNTS = "tmpfs / tmpfs rw 0 0\n"

    def check(self, bins, mounts=None, base=None):
        return P.gpg_check(bins=bins, parent=self.tmp, mounts_text=mounts or self.MOUNTS,
                           run_base=base or os.path.join(self.tmp, "run"))

    def run_base(self):
        base = os.path.join(self.tmp, "run")
        os.makedirs(os.path.join(base, str(os.getuid())), mode=0o700)
        os.mkdir(os.path.join(base, str(os.getuid()), "gnupg"), 0o700)
        return base

    def gpg_called(self):
        return (Path(self.tmp) / "gpg-calls").exists()

    def test_honest_fake_passes(self):
        r = self.check(fake_bins(self.tmp))
        self.assertTrue(r["pass"], r)
        self.assertEqual(r["agent_pid"], 4242)
        self.assertIsNone(r["socketdir_outside_home"])
        self.assertTrue(r["socketdir_absent"])

    def test_a_verified_run_user_socket_dir_is_used_and_removed(self):
        base = self.run_base()
        r = self.check(fake_bins(self.tmp, base=base), base=base)
        self.assertTrue(r["pass"], r)
        self.assertEqual(r["socketdir_outside_home"], r["canonical_socketdir"])
        self.assertTrue(r["canonical_socketdir"].startswith(f"{base}/{os.getuid()}/gnupg/d."))
        self.assertEqual(r["remove_socketdir_rc"], 0)
        self.assertEqual(os.listdir(os.path.join(base, str(os.getuid()), "gnupg")), [])

    def test_a_socket_dir_left_behind_fails(self):
        base = self.run_base()
        r = self.check(fake_bins(self.tmp, base=base, remove=False), base=base)
        self.assertFalse(r["socketdir_absent"])
        self.assertFalse(r["pass"])

    def test_cleanup_runs_when_the_crypto_check_fails(self):
        base = self.run_base()
        r = self.check(fake_bins(self.tmp, HONEST.replace("if '--symmetric' in sys.argv:", "if False:"), base=base),
                       base=base)
        self.assertIn("problem", r)
        self.assertTrue(r["socketdir_absent"])
        self.assertEqual(os.listdir(os.path.join(base, str(os.getuid()), "gnupg")), [])
        self.assertFalse(r["pass"])

    def test_an_unverified_socket_dir_stops_before_gpg_runs(self):
        base = self.run_base()
        g = os.path.join(base, str(os.getuid()), "gnupg")
        for name, sd in (("another hash", g + "/d.yyyy"), ("elsewhere", "/var/x")):
            with self.subTest(name):
                expr = "'homedir:' + h + " + repr(f"\nsocketdir:{sd}\nagent-socket:{sd}/S.gpg-agent")
                r = self.check(fake_bins(self.tmp, base=base, listing=expr), base=base)
                self.assertFalse(r["confined"], r.get("gpgconf_dirs"))
                self.assertEqual(r["gpgconf_dirs"]["socketdir"], sd)
                self.assertFalse(self.gpg_called())
                self.assertFalse(r["pass"])

    def test_a_failing_list_dirs_stops_before_gpg_runs(self):
        r = self.check(fake_bins(self.tmp, list_rc=2))
        self.assertFalse(r["confined"])
        self.assertFalse(self.gpg_called())
        self.assertFalse(r["pass"])

    def test_check_sockets_rules(self):
        base, uid = self.run_base(), os.getuid()
        home = os.path.join(self.tmp, "home")
        os.mkdir(home, 0o700)
        sd = P.socketdir_for(home, uid, base)
        os.mkdir(sd, 0o700)
        ok = {"homedir": home, "socketdir": sd, "agent-socket": sd + "/S.gpg-agent", "dirmngr-socket": sd + "/S.dirmngr"}
        m = self.MOUNTS
        self.assertEqual(P.check_sockets(ok, home, uid, m, base), (True, sd, []))
        inhome = {"homedir": home, "socketdir": home, "agent-socket": home + "/S.gpg-agent"}
        self.assertEqual(P.check_sockets(inhome, home, uid, m, base), (True, None, []))
        bad = [dict(ok, homedir="/x"), dict(ok, **{"dirmngr-socket": "/x/S.dirmngr"}),
               {k: v for k, v in ok.items() if k != "agent-socket"},
               dict(inhome, **{"agent-extra-socket": sd + "/S.gpg-agent.extra"})]
        for i, dirs in enumerate(bad):
            with self.subTest(i):
                self.assertFalse(P.check_sockets(dirs, home, uid, m, base)[0])
        self.assertFalse(P.check_sockets(ok, home, uid + 1, m, base)[0])          # another uid's hash and path
        self.assertFalse(P.check_sockets(ok, home, uid, "/dev/x / ext4 rw 0 0\n", base)[0])
        os.chmod(sd, 0o750)
        self.assertFalse(P.check_sockets(ok, home, uid, m, base)[0])
        os.chmod(sd, 0o700)
        os.chmod(os.path.dirname(sd), 0o755)
        self.assertFalse(P.check_sockets(ok, home, uid, m, base)[0])
        os.chmod(os.path.dirname(sd), 0o700)
        other = os.path.join(os.path.dirname(sd), "d.yyyyyyyyyyyyyyyyyyyyyyyy")
        os.mkdir(other, 0o700)
        self.assertFalse(P.check_sockets(dict(ok, socketdir=other, **{"agent-socket": other + "/S.gpg-agent",
                                                                       "dirmngr-socket": other + "/S.dirmngr"}),
                                         home, uid, m, base)[0])
        link = os.path.join(self.tmp, "runlink")
        os.symlink(base, link)
        lsd = P.socketdir_for(home, uid, link)                               # sd itself, reached through the link
        self.assertTrue(os.path.isdir(lsd))
        self.assertFalse(P.check_sockets({"homedir": home, "socketdir": lsd, "agent-socket": lsd + "/S.gpg-agent"},
                                         home, uid, m, link)[0])
        os.rmdir(sd)
        real = os.path.join(self.tmp, "realsd")
        os.mkdir(real, 0o700)
        os.symlink(real, sd)
        self.assertFalse(P.check_sockets(ok, home, uid, m, base)[0])

    def test_a_crashing_gpg_is_not_a_refusal(self):
        r = self.check(fake_bins(self.tmp, HONEST.replace("CRASH", "os.kill(os.getpid(), 11)")))
        self.assertLess(r["tampered"]["rc"], 0)
        self.assertFalse(r["pass"])

    def test_a_refusal_without_evidence_fails(self):
        r = self.check(fake_bins(self.tmp, HONEST.replace("encrypted message has been manipulated", "some error")))
        self.assertEqual(r["tampered"]["rc"], 2)
        self.assertFalse(r["tampered"]["evidence"])
        self.assertFalse(r["pass"])

    def test_a_wrong_passphrase_refused_without_evidence_fails(self):
        r = self.check(fake_bins(self.tmp, HONEST.replace("Bad session key", "something")))
        self.assertFalse(r["wrong_passphrase"]["evidence"])
        self.assertFalse(r["pass"])

    def test_a_wrong_passphrase_accepted_fails(self):
        body = HONEST.replace("sys.stderr.write('gpg: decryption failed: Bad session key\\n'); sys.exit(2)",
                              "sys.stderr.write('gpg: decryption failed: Bad session key\\n'); sys.exit(0)")
        self.assertNotEqual(body, HONEST)
        r = self.check(fake_bins(self.tmp, body))
        self.assertEqual(r["wrong_passphrase"]["rc"], 0)
        self.assertFalse(r["pass"])

    def test_mode_700_is_required(self):
        bins = fake_bins(self.tmp)
        orig = P.os.chmod
        try:
            P.os.chmod = lambda p, m, **kw: orig(p, 0o755, **kw)
            r = self.check(bins)
        finally:
            P.os.chmod = orig
        self.assertEqual(r["gnupghome_mode"], "0o755")
        self.assertFalse(r["pass"])

    def test_a_closed_stdin_is_reopened(self):
        if P._fd_open(3):
            self.skipTest("fd 3 is open in this test process")
        bins = fake_bins(self.tmp)
        saved = 57
        os.dup2(0, saved)                 # a high fd, so that the saved copy does not itself sit on 3
        os.close(0)                       # otherwise a pipe's read end lands on 0 and its write end on 3
        try:
            r = self.check(bins)
        finally:
            os.dup2(saved, 0)
            os.close(saved)
        self.assertEqual(r["std_fds_reopened"], [0])
        self.assertTrue(r["pass"], r.get("problem"))

    def test_not_seipd(self):
        r = self.check(fake_bins(self.tmp, HONEST.replace("pkt(18,", "pkt(9,")))
        self.assertIn("not SKESK + SEIPD", r["problem"])
        self.assertFalse(r["pass"])

    def test_unconfined_sockets_fail(self):
        r = self.check(fake_bins(self.tmp, dirs="homedir:/elsewhere\nsocketdir:/elsewhere\n"
                                                "agent-socket:/elsewhere/S.gpg-agent"))
        self.assertFalse(r["confined"])
        self.assertFalse(self.gpg_called())
        self.assertFalse(r["pass"])

    def test_failed_kill_fails(self):
        r = self.check(fake_bins(self.tmp, conf_rc=1))
        self.assertEqual(r["gpgconf_kill_rc"], 1)
        self.assertFalse(r["pass"])

    def test_unknown_agent_fails(self):
        r = self.check(fake_bins(self.tmp, agent_out="ERR no agent\\n"))
        self.assertIsNone(r["agent_pid"])
        self.assertFalse(r["pass"])

    def test_surviving_agent_fails(self):
        p = subprocess.Popen(["sleep", "30"])
        try:
            r = self.check(fake_bins(self.tmp, agent_out=f"D {p.pid}\\nOK\\n"))
        finally:
            p.kill()
            p.wait()
        self.assertFalse(r["agent_gone"])
        self.assertFalse(r["pass"])

    def test_network_parent_is_refused(self):
        r = self.check(fake_bins(self.tmp), mounts="lus / lustre rw 0 0\n")
        self.assertIn("not a node-local filesystem", r["problem"])
        self.assertEqual([n for n in os.listdir(self.tmp) if n.startswith("pgprobe")], [])

    def test_missing_executable(self):
        bins = fake_bins(self.tmp)
        bins["gpg-connect-agent"] = None
        self.assertEqual(self.check(bins)["problem"], "an approved gpg executable is missing")

    def test_fd3_already_open_fails_cleanly(self):
        if P._fd_open(3):
            self.skipTest("fd 3 is open in this test process")
        fd = os.open(os.devnull, os.O_RDONLY)
        if fd != 3:
            os.dup2(fd, 3)
            os.close(fd)
        try:
            r = self.check(fake_bins(self.tmp))
            self.assertTrue(P._fd_open(3))
        finally:
            os.close(3)
        self.assertIn("fd 3 is already open", r["problem"])
        self.assertEqual([n for n in os.listdir(self.tmp) if n.startswith("pgprobe")], [])

    def test_tamper_hits_the_last_seipd_byte(self):
        ct = bytes([0xC3, 3, 4, 9, 3, 0xD2, 5, 1, 10, 11, 12, 13])
        bad = P.tamper_seipd(ct)
        self.assertEqual((bad[:-1], bad[-1]), (ct[:-1], ct[-1] ^ 1))
        with self.assertRaises(ValueError):
            P.tamper_seipd(bytes([0xC3, 3, 4, 9, 3, 0xD2, 5, 2, 10, 11, 12, 13]))      # SEIPD v2
        with self.assertRaises(ValueError):
            P.tamper_seipd(bytes([0xC3, 3, 4, 9, 3, 0xD2, 9, 1, 10]))                 # truncated
        # partial body lengths, as gpg 2.4 streams SEIPD: a 2-byte chunk (0xE1), then a definite 3-byte tail
        ct = bytes([0xC3, 3, 4, 9, 3, 0xD2, 0xE1, 1, 20, 3, 30, 31, 32])
        self.assertEqual(P.packets(ct)[1][0], 18)
        bad = P.tamper_seipd(ct)
        self.assertEqual((bad[:-1], bad[-1]), (ct[:-1], 32 ^ 1))


@unittest.skipUnless(all(shutil.which(n) for n in ("gpg", "gpgconf", "gpg-connect-agent")), "no gpg")
class RealGpg(unittest.TestCase):
    """The local gpg (macOS, GnuPG 2.4.8), with a short /tmp parent: gpg-agent's socket path limit."""

    def setUp(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp(dir="/tmp"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_round_trip_and_controls(self):
        bins = {n: shutil.which(n) for n in ("gpg", "gpgconf", "gpg-connect-agent")}
        r = P.gpg_check(bins=bins, parent=self.tmp, mounts_text=f"x {self.tmp} tmpfs rw 0 0\n")
        self.assertTrue(r["pass"], r)
        self.assertEqual(r["packet_tags"], [3, 18])
        self.assertEqual((r["tampered"]["rc"], r["tampered"]["evidence"]), (2, True))
        self.assertEqual((r["wrong_passphrase"]["rc"], r["wrong_passphrase"]["evidence"]), (2, True))
        self.assertIsNotNone(r["agent_pid"])
        self.assertTrue(r["agent_gone"])
        self.assertTrue(r["socketdir_absent"])
        self.assertEqual(os.listdir(self.tmp), [])


class Launcher(Base):
    def setUp(self):
        super().setUp()
        self.t = Path(self.tmp)
        self.probe = self.t / "pg-probe.py"
        self.probe.write_bytes((HERE / "pg-probe.py").read_bytes())
        self.out = self.t / "pg-probe.out"
        self.sha = hashlib.sha256(self.probe.read_bytes()).hexdigest()

    def launch(self, body, sha=None):
        s = self.t / "ssh"
        s.write_text(f"#!/bin/sh\necho \"$@\" > {self.t}/args\ncat > {self.t}/stdin\n{body}\n")
        s.chmod(0o755)
        so = io.StringIO()
        with contextlib.redirect_stdout(so), contextlib.redirect_stderr(io.StringIO()):
            rc = LAUNCH.main([sha or self.sha], ssh=str(s), probe_path=str(self.probe), out_path=str(self.out))
        self.printed = so.getvalue()
        return rc

    def go_record(self, **kw):
        stub = Stub(Path(tempfile.mkdtemp(dir=self.tmp)) / "stub", **kw)
        g = P.gpg_check(bins=fake_bins(self.tmp), parent=self.tmp, mounts_text="tmpfs / tmpfs rw 0 0\n",
                        run_base=os.path.join(self.tmp, "run"))
        rec = stub.run(gpg_rec=g)
        self.assertEqual(rec["verdict"], "GO", rec["stops"])
        return rec

    def emit(self, rec, rc):
        """A fake ssh body printing rec as the probe would: report() for a full record, else the result line."""
        fd, f = tempfile.mkstemp(dir=self.tmp, suffix=".receipt")
        os.close(fd)
        so = io.StringIO()
        with contextlib.redirect_stdout(so):
            if "catalog" in rec and all(t in rec["catalog"] for t in P.ALL_TUNES):
                P.report(rec)
            else:
                print("verdict line\nPG-PROBE-RESULT " + json.dumps(rec, sort_keys=True))
        Path(f).write_text(so.getvalue())
        return f"cat {f}; exit {rc}"

    def test_valid_stop_and_go(self):
        stop = {"schema": P.SCHEMA, "verdict": "STOP", "identity": {"pass": False}, "stops": ["identity: x"]}
        self.assertEqual(self.launch(self.emit(stop, 3)), 3)
        self.assertEqual((self.t / "stdin").read_bytes(), self.probe.read_bytes())
        args = (self.t / "args").read_text()
        self.assertTrue(args.startswith("-F /dev/null "))
        for o in ("ForwardAgent=no", "StrictHostKeyChecking=yes", "ControlPath=none", "BatchMode=yes",
                  "ClearAllForwardings=yes", "PermitLocalCommand=no", "IdentitiesOnly=yes"):
            self.assertIn(o, args)
        self.assertTrue(args.rstrip().endswith("saul.nersc.gov env -i PATH=/usr/bin:/bin LC_ALL=C "
                                               "/usr/bin/python3.11 -I -S -B -"))
        self.assertIn("receipt valid: verdict STOP", self.out.read_text())
        self.out.unlink()
        self.assertEqual(self.launch(self.emit(self.go_record(), 0)), 0, self.out.read_text()[-400:])
        self.out.unlink()
        self.assertEqual(self.launch(self.emit(self.go_record(absent=("G18_02b_02_11b",)), 0)), 0)

    def test_an_incomplete_go_is_invalid(self):
        # codex read 2, blocking 5: a bare {"verdict": "GO"} with exit 0 was accepted
        good = self.go_record()

        def without(*keys):
            r = json.loads(json.dumps(good))
            x = r
            for k in keys[:-1]:
                x = x[k]
            del x[keys[-1]]
            return r

        def setting(value, *keys):
            r = json.loads(json.dumps(good))
            x = r
            for k in keys[:-1]:
                x = x[k]
            x[keys[-1]] = value
            return r
        cases = [{"verdict": "GO"}, {"schema": P.SCHEMA, "verdict": "GO", "stops": [], "identity": {"pass": True}},
                 setting("covfix-pg-probe/2", "schema"), without("roots_verified"), without("gpg", "socketdir_absent"),
                 setting(1, "gpg", "pass"), setting(1, "gpg", "decrypt_rc"), setting(False, "gpg", "agent_gone"),
                 setting(["x"], "stops"), setting(["x"], "decision", "stops"), without("catalog", "G18_02a_02_11b"),
                 setting(False, "decision", "controls", "AR23_20i_00_000: catalog equals F1's pins"),
                 setting(True, "decision", "fallback_taken"), setting("G18_02a_02_11b", "decision", "chosen", "u1"),
                 setting(None, "decision", "chosen", "u0"), setting("x", "decision", "eligibility", "G21_11b_00_000"),
                 without("catalog", "G21_11b_00_000", "spline_sha256"), without("catalog", "G18_02b_02_11b",
                                                                                "readme_version"),
                 setting(["p"], "classes", "G21_11b_00_000", "problems"), setting(False, "identity", "pass")]
        for i, rec in enumerate(cases):
            with self.subTest(i):
                if self.out.exists():
                    self.out.unlink()
                self.assertEqual(self.launch(self.emit(rec, 0)), 4)
                self.assertIn("receipt INVALID", self.out.read_text())

    def test_invalid_receipts_are_kept(self):
        go = json.dumps({"verdict": "GO"})
        stop = {"schema": P.SCHEMA, "verdict": "STOP", "identity": {}, "stops": ["x"]}
        self.assertEqual(self.launch(self.emit(stop, 3)), 3)              # the complete record alone is valid
        self.out.unlink()
        for i, body in enumerate((f"echo 'PG-PROBE-RESULT {go}'; exit 3", 'exit 0',
                                  f"echo 'PG-PROBE-RESULT {go}'; echo tail; exit 0", 'echo "PG-PROBE-RESULT {"; exit 0',
                                  f"echo 'PG-PROBE-RESULT {go}'; echo 'PG-PROBE-RESULT {go}'; exit 0", 'exit 255',
                                  self.emit({"schema": P.SCHEMA, "verdict": "STOP", "identity": {}, "stops": []}, 3),
                                  self.emit({"schema": P.SCHEMA, "verdict": "STOP", "identity": {}, "stops": ["x"]}, 0),
                                  self.emit(stop, 3).replace("; exit 3", "; echo tail; exit 3"),
                                  self.emit(stop, 3).replace("; exit 3", "; " + self.emit(stop, 3)))):
            with self.subTest(i):
                if self.out.exists():
                    self.out.unlink()
                self.assertEqual(self.launch(body), 4)
                self.assertIn("receipt INVALID", self.out.read_text())

    def test_refusals_before_ssh(self):
        self.assertEqual(self.launch("exit 0", sha="0" * 64), 5)
        self.assertFalse((self.t / "args").exists())
        self.out.symlink_to(self.t / "elsewhere")
        self.assertEqual(self.launch("exit 0"), 5)
        self.assertFalse((self.t / "elsewhere").exists())
        self.out.unlink()
        self.out.write_text("old\n")
        self.assertEqual(self.launch("exit 0"), 5)
        self.assertEqual(self.out.read_text(), "old\n")
        self.assertFalse((self.t / "args").exists())

    def test_the_sent_bytes_are_the_hashed_bytes(self):
        stop = {"schema": P.SCHEMA, "verdict": "STOP", "identity": {}, "stops": ["x"]}
        self.assertEqual(self.launch(self.emit(stop, 3)), 3)
        self.assertEqual(hashlib.sha256((self.t / "stdin").read_bytes()).hexdigest(), self.sha)
        self.assertIn(f"# pg-probe.py sha256 {self.sha}", self.out.read_text())

    def test_the_footer_hash_is_read_through_the_reserved_descriptor(self):
        # codex read 2, blocking 5: the footer re-hashed the pathname. Here the path is moved while ssh runs.
        stop = {"schema": P.SCHEMA, "verdict": "STOP", "identity": {}, "stops": ["x"]}
        moved = self.t / "moved.out"
        self.assertEqual(self.launch(f"mv {self.out} {moved}; " + self.emit(stop, 3)), 3)
        self.assertFalse(self.out.exists())
        digest = hashlib.sha256(moved.read_bytes()).hexdigest()
        self.assertIn(f"{digest}  {self.out}", self.printed)


if __name__ == "__main__":
    unittest.main()
