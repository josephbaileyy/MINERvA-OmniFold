"""Tests for pg-probe.py (rev 2) and pg-probe-launch.py on stub CVMFS trees: no cluster, no GENIE, no generated
content. Includes the counterexamples of codex-school2's read 1 (CODEX2-READ-1.md).

Run: python3 -I -B test_pg_probe.py -v   (from this directory)
"""
import contextlib
import hashlib
import importlib.util
import io
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
HYBRID = """<?xml version="1.0" encoding="ISO-8859-1"?>
<alg_conf>
  <param_set name="Default"> </param_set>
  <param_set name="SuSAv2-QEL">
    <param type="alg" name="DefaultXSecAlg"> genie::SuSAv2QELPXSec/Default </param>
    <param type="alg" name="XSecAlg@Interaction=nu:14;tgt:1000000010;N:2112;proc:Weak[CC],QES;"> genie::LwlynSmithQELCCPXSec/Dipole </param>
  </param_set>
</alg_conf>
"""
MASTER = """<?xml version="1.0" encoding="ISO-8859-1"?>
<genie_config>
  <config alg="genie::HybridXSecAlgorithm">   HybridXSecAlgorithm.xml   </config>
  <config alg="genie::NievesQELCCPXSec">  NievesQELCCPXSec.xml </config>
</genie_config>
"""


def model_xml(qel, mec, extra="", set_name="Default", root="global_param_list"):
    return (f'<?xml version="1.0" encoding="ISO-8859-1"?>\n<{root}>\n <param_set name="{set_name}">\n'
            f'  <param type="alg" name="XSecModel@genie::EventGenerator/QEL-CC"> {qel} </param>\n'
            f'  <!-- <param type="alg" name="XSecModel@genie::EventGenerator/MEC-CC"> genie::Old/Default </param> -->\n'
            f'  <param type="alg" name="XSecModel@genie::EventGenerator/MEC-CC">{mec}</param>\n'
            f'  <param type="alg" name="XSecModel@genie::EventGenerator/RES-CC"> genie::X/Default </param>\n'
            f'{extra} </param_set>\n</{root}>\n')


def fake_ident():
    return {"host": "login31", "checks": {}, "pass": True}


class Stub:
    """A stub genie_xsec product (NULL/, ups/) and genie product (ups/, config/)."""

    def __init__(self, root, absent=(), qel=None, mec=None):
        self.root = Path(root)
        self.xp, self.gp = self.root / "genie_xsec", self.root / "genie"
        self.xsec, self.config = self.xp / "NULL", self.gp / "config"
        self.qel, self.mec = dict(QEL, **(qel or {})), dict(MEC, **(mec or {}))
        self.pins, table = {}, ["FILE=TABLE", "PRODUCT=genie_xsec"]
        self.config.mkdir(parents=True)
        (self.config / "master_config.xml").write_text(MASTER)
        (self.config / "HybridXSecAlgorithm.xml").write_text(HYBRID)
        for t in P.ALL_TUNES:
            q = P.qualifier(t)
            qc = q.replace("-", ":")
            if t not in absent:
                d = self.xsec / q / "data"
                d.mkdir(parents=True)
                (d / "gxspl-NUsmall.xml").write_text(f'<?xml version="1.0"?>\n<genie_xsec_spline_list version="3.00">\n'
                                                      f'<genie_tune name="{t}">\n<spline name="x"/>\n</genie_tune>\n'
                                                      f'</genie_xsec_spline_list>\n')
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
        (self.xp / "ups" / "genie_xsec.table").write_text("\n".join(table) + "\n")
        (self.gp / "ups").mkdir(parents=True)
        (self.gp / "ups" / "genie.table").write_text("FILE=TABLE\nPRODUCT=genie\nenvSet(GENIE, ${UPS_PROD_DIR})\n")

    @staticmethod
    def sha(p):
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()

    @property
    def roots(self):
        return (str(self.xp), str(self.gp))

    def run(self, gpg_rec=None, ident=fake_ident):
        return P.probe(str(self.xsec), str(self.xp / "ups/genie_xsec.table"), str(self.gp / "ups/genie.table"),
                       str(self.config), self.roots, ident=ident,
                       gpg=lambda: gpg_rec or {"pass": True}, spent_pins=self.pins, spent_classes=SPENT_CLS)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def stub(self, sub="s", **kw):
        return Stub(Path(self.tmp) / sub, **kw)


class Decision(Base):
    def test_go_with_02b(self):
        r = self.stub().run()
        self.assertEqual(r["verdict"], "GO", r["stops"])
        d = r["decision"]
        self.assertEqual(d["chosen"], {"u0": "G21_11b_00_000", "u1": "G18_02b_02_11b"})
        self.assertIs(d["fallback_taken"], False)
        self.assertEqual(d["eligibility"]["G18_02a_02_11b"], "not considered: 02b is present")
        g21 = r["classes"]["G21_11b_00_000"]
        self.assertEqual((g21["ccqe"], g21["2p2h"]), ("SuSAv2QELPXSec", "SuSAv2MECPXSec"))
        self.assertEqual(g21["components"]["ccqe"], ["LwlynSmithQELCCPXSec", "SuSAv2QELPXSec"])
        self.assertEqual(g21["sources"]["ccqe"]["raw"], "genie::HybridXSecAlgorithm/SuSAv2-QEL")
        self.assertTrue(g21["sources"]["ccqe"]["hybrid"]["file"].endswith("config/HybridXSecAlgorithm.xml"))
        self.assertEqual(d["overlap_with_spent_pool"]["G21_11b_00_000"],
                         {"SuSAv2QELPXSec": [], "LwlynSmithQELCCPXSec": [], "SuSAv2MECPXSec": ["AR23_20i_00_000"]})
        self.assertEqual(d["spent_pool"], ["NievesQELCCPXSec", "NievesSimoVacasMECPXSec2016", "SuSAv2MECPXSec"])
        self.assertTrue(d["02a_02b_same_classes"])
        self.assertIn("SomeOther-k250-e1000", r["qualifiers"])
        self.assertEqual(r["catalog"]["G21_11b_00_000"]["status"], "present")

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
        r = self.stub(qel={"G21_11b_00_000": "genie::NievesQELCCPXSec/Default"},
                      mec={"G21_11b_00_000": "genie::NievesSimoVacasMECPXSec2016/Default"}).run()
        self.assertEqual(r["verdict"], "STOP")
        self.assertIsNone(r["decision"]["chosen"]["u0"])

    def test_cross_slot_class_counts_as_spent(self):
        r = self.stub(qel={"G21_11b_00_000": "genie::SuSAv2MECPXSec/Default"},
                      mec={"G21_11b_00_000": "genie::NievesQELCCPXSec/Default"}).run()
        self.assertEqual(r["decision"]["eligibility"]["G21_11b_00_000"], "not eligible: both classes in the spent pool")

    def test_one_novel_class_suffices(self):
        r = self.stub(qel={"G18_02b_02_11b": "genie::NievesQELCCPXSec/Dipole"}).run()
        self.assertEqual(r["decision"]["chosen"]["u1"], "G18_02b_02_11b")

    def test_overlap_is_against_the_pool_not_the_slot(self):
        r = self.stub(mec={"G18_02b_02_11b": "genie::NievesQELCCPXSec/Default"}).run()
        self.assertEqual(r["decision"]["chosen"]["u1"], "G18_02b_02_11b")
        self.assertEqual(r["decision"]["overlap_with_spent_pool"]["G18_02b_02_11b"]["NievesQELCCPXSec"],
                         ["G18_10a_02_11b", "AR23_20i_00_000"])

    def test_component_disagreement_is_a_director_stop(self):
        s = self.stub()
        (s.config / "HybridXSecAlgorithm.xml").write_text(HYBRID.replace("genie::SuSAv2QELPXSec/Default",
                                                                         "genie::NievesQELCCPXSec/Default"))
        r = s.run()
        self.assertEqual(r["verdict"], "STOP")
        self.assertIn("disagree", r["decision"]["eligibility"]["G21_11b_00_000"])

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
        s = self.stub(absent=("G18_02b_02_11b",))
        (s.config / "G18_02b/ModelConfiguration.xml").write_text("<broken")
        r = s.run()
        self.assertEqual(r["verdict"], "STOP")
        self.assertIsNone(r["decision"]["chosen"]["u1"])
        self.assertIn("premise cannot be checked", r["decision"]["eligibility"]["G18_02a_02_11b"])

    def test_spent_controls(self):
        s = self.stub("a")
        s.pins["AR23_20i_00_000"] = ("0" * 64,) + s.pins["AR23_20i_00_000"][1:]
        self.assertIn("control: AR23_20i_00_000's catalog is not F1's pins", s.run()["stops"])
        s = self.stub("b")
        s.pins["G18_10a_02_11b"] = s.pins["G18_10a_02_11b"][:2] + ("version x",)
        self.assertEqual(s.run()["verdict"], "STOP")
        r = self.stub("c", mec={"G18_10a_02_11b": "genie::NievesSimoVacasMECPXSec/Default"}).run()
        self.assertIn("control: G18_10a_02_11b's resolved classes are not R-3_04_00's", r["stops"])

    def test_gpg_failure_stops(self):
        self.assertIn("gpg: the tool or its pinned round trip failed", self.stub().run(gpg_rec={"pass": False})["stops"])

    def test_identity_failure_reads_nothing(self):
        s = self.stub()
        called = []
        r = P.probe(str(s.xsec), str(s.xp / "ups/genie_xsec.table"), str(s.gp / "ups/genie.table"), str(s.config),
                    s.roots, ident=lambda: {"host": "nid001", "checks": {}, "pass": False},
                    gpg=lambda: called.append(1) or {"pass": True}, spent_pins=s.pins, spent_classes=SPENT_CLS)
        self.assertEqual(r["verdict"], "STOP")
        self.assertEqual(r["stops"], ["identity: not a Perlmutter login node; nothing was read"])
        for k in ("qualifiers", "catalog", "classes", "gpg"):
            self.assertNotIn(k, r)
        self.assertEqual(called, [])

    def test_missing_product_stops(self):
        s = self.stub()
        shutil.rmtree(s.xsec)
        self.assertEqual(s.run()["verdict"], "STOP")


class Catalog(Base):
    """codex 2: absent, present and unresolved are kept apart."""

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

    def test_wrong_tune_spline_and_empty_spline(self):
        s = self.stub()
        d = s.xsec / P.qualifier("G18_02b_02_11b") / "data"
        (d / "gxspl-NUsmall.xml").write_text('<genie_tune name="G18_02a_02_11b">\n')
        self.assertIn("the spline header names G18_02a_02_11b", s.run()["catalog"]["G18_02b_02_11b"]["problems"])
        (d / "gxspl-NUsmall.xml").write_text("")
        r = s.run()
        self.assertIn("empty spline file", r["catalog"]["G18_02b_02_11b"]["problems"])
        self.assertEqual(r["verdict"], "STOP")

    def test_ups_tune_mismatch(self):
        s = self.stub()
        t = s.xp / "ups/genie_xsec.table"
        t.write_text(t.read_text().replace("envSet(GENIE_XSEC_TUNE, G21_11b_00_000)", "envSet(GENIE_XSEC_TUNE, X)"))
        self.assertEqual(s.run()["catalog"]["G21_11b_00_000"]["status"], "unresolved")

    def test_readme_must_name_the_qualifier(self):
        s = self.stub()
        (s.xsec / P.qualifier("G21_11b_00_000") / "data/README").write_text("version v3_04_00 qualifier other\n")
        self.assertEqual(s.run()["catalog"]["G21_11b_00_000"]["status"], "unresolved")

    def test_ups_table_rules(self):
        self.assertEqual(P.ups_table('Qualifiers="a:b"\n envSet(GENIE_XSEC_TUNE, T1)\nQualifiers="c"\n'),
                         {"a:b": "T1", "c": None})
        with self.assertRaises(P.Unresolved):
            P.ups_table('Qualifiers="a"\nQualifiers="a"\n')
        with self.assertRaises(P.Unresolved):
            P.ups_table('Qualifiers="a"\nenvSet(GENIE_XSEC_TUNE, T1)\nenvSet(GENIE_XSEC_TUNE, T2)\n')


class Boundary(Base):
    """codex 4: reads stay beneath the approved roots, regular files only."""

    def test_spline_link_outside_the_roots(self):
        s = self.stub()
        outside = Path(self.tmp) / "outside.xml"
        outside.write_text('<genie_tune name="G21_11b_00_000">\n')
        f = s.xsec / P.qualifier("G21_11b_00_000") / "data/gxspl-NUsmall.xml"
        f.unlink()
        f.symlink_to(outside)
        r = s.run()
        self.assertEqual(r["catalog"]["G21_11b_00_000"]["status"], "unresolved")
        self.assertTrue(any("outside the approved roots" in x for x in r["catalog"]["G21_11b_00_000"]["problems"]))

    def test_config_link_outside_the_roots(self):
        s = self.stub()
        outside = Path(self.tmp) / "mc.xml"
        outside.write_text(model_xml("genie::A/Default", "genie::B/Default"))
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

    def test_is_file_rules(self):
        s = self.stub()
        self.assertTrue(P.is_file(str(s.config / "master_config.xml"), s.roots))
        self.assertFalse(P.is_file(str(s.config / "nothing.xml"), s.roots))
        with self.assertRaises(P.Unresolved):
            P.is_file(str(s.config / "G18_02b"), s.roots)                  # a directory
        (s.config / "dangling.xml").symlink_to(s.config / "gone.xml")
        with self.assertRaises(P.Unresolved):
            P.is_file(str(s.config / "dangling.xml"), s.roots)

    def test_read_file_refuses_a_fifo_and_an_escape(self):
        s = self.stub()
        f = s.config / "fifo.xml"
        os.mkfifo(f)
        with self.assertRaises(P.Unresolved):
            P.read_file(str(f), s.roots)
        with self.assertRaises(P.Unresolved):
            P.read_file(str(s.config / ".." / ".." / ".." / "x"), s.roots)


class Config(Base):
    """codex 1: structural parsing, GENIE's file selection, the active set, STOP on anything unexpected."""

    def classes(self, s, t="G18_02b_02_11b", ups=""):
        return P.model_classes(str(s.config), ups, t, s.roots)

    def test_blank_value_is_unresolved_not_novel(self):
        rec = self.classes(self.stub(qel={"G18_02b_02_11b": "   "}))
        self.assertFalse(P.resolved(rec))
        self.assertTrue(any("empty value" in x for x in rec["problems"]))

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
        f.write_text(model_xml("genie::A", "genie::C/D"))
        self.assertEqual(self.classes(s)["ccqe"], "A")

    def test_tune_directory_file_replaces_the_cmc_file(self):
        s = self.stub()
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
                                  HYBRID.replace("genie::LwlynSmithQELCCPXSec/Dipole", "  "))):
            with self.subTest(i):
                s = self.stub(f"h{i}")
                (s.config / "HybridXSecAlgorithm.xml").write_text(text)
                self.assertFalse(P.resolved(self.classes(s, "G21_11b_00_000")))
        s = self.stub("x")
        (s.config / "HybridXSecAlgorithm.xml").write_text(HYBRID.replace(
            "  </param_set>\n</alg_conf>", '    <param type="alg" name="Other">genie::Z/Default</param>\n  </param_set>\n</alg_conf>'))
        self.assertFalse(P.resolved(self.classes(s, "G21_11b_00_000")))
        s = self.stub("m")
        (s.config / "master_config.xml").write_text(MASTER.replace("genie::HybridXSecAlgorithm", "genie::Nope"))
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


HONEST = r"""import hashlib, hmac, os, sys
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


def fake_bins(tmp, gpg_body=HONEST, conf_rc=0, agent_out="D 4242\\nOK\\n", dirs=None):
    d = Path(tmp) / "fbin"
    d.mkdir(exist_ok=True)
    (d / "gpg").write_text(f"#!{sys.executable}\n" + gpg_body.replace("CRASH", ""))
    if dirs is None:
        lst = ("    h = os.environ['GNUPGHOME']\n"
               "    print(f'homedir:{h}\\nsocketdir:{h}\\nagent-socket:{h}/S.gpg-agent')\n")
    else:
        lst = f"    print({dirs!r})\n"
    (d / "gpgconf").write_text(f"#!{sys.executable}\nimport os, sys\nif '--list-dirs' in sys.argv:\n{lst}"
                               f"sys.exit({conf_rc} if '--kill' in sys.argv else 0)\n")
    (d / "gpg-connect-agent").write_text(f"#!/bin/sh\nprintf '{agent_out}'\n")
    for n in ("gpg", "gpgconf", "gpg-connect-agent"):
        (d / n).chmod(0o755)
    return {n: str(d / n) for n in ("gpg", "gpgconf", "gpg-connect-agent")}


class GpgFakes(Base):
    """codex 7 and 8 with fake executables: each check fails on its own."""

    MOUNTS = "tmpfs / tmpfs rw 0 0\n"

    def check(self, bins, mounts=None):
        return P.gpg_check(bins=bins, parent=self.tmp, mounts_text=mounts or self.MOUNTS)

    def test_honest_fake_passes(self):
        r = self.check(fake_bins(self.tmp))
        self.assertTrue(r["pass"], r)
        self.assertEqual(r["agent_pid"], 4242)

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

    def test_confinement_rules(self):
        h = os.path.realpath(self.tmp)
        ok = {"homedir": h, "socketdir": h, "agent-socket": h + "/S.gpg-agent"}
        self.assertEqual(P.confinement(ok, h, 1000), (True, None))
        run = {"homedir": h, "socketdir": "/run/user/1000/gnupg/d.abc123",
               "agent-socket": "/run/user/1000/gnupg/d.abc123/S.gpg-agent"}
        self.assertEqual(P.confinement(run, h, 1000), (True, "/run/user/1000/gnupg/d.abc123"))
        self.assertFalse(P.confinement(run, h, 1001)[0])
        self.assertFalse(P.confinement(dict(ok, homedir="/x"), h, 1000)[0])
        self.assertFalse(P.confinement(dict(ok, **{"agent-socket": "/x/S"}), h, 1000)[0])
        self.assertFalse(P.confinement(dict(ok, socketdir="/var/x", **{"agent-socket": "/var/x/S"}), h, 1000)[0])

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
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return LAUNCH.main([sha or self.sha], ssh=str(s), probe_path=str(self.probe), out_path=str(self.out))

    def test_valid_stop_and_go(self):
        self.assertEqual(self.launch('echo x; echo \'PG-PROBE-RESULT {"verdict": "STOP"}\'; exit 3'), 3)
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
        self.assertEqual(self.launch('echo \'PG-PROBE-RESULT {"verdict": "GO"}\'; exit 0'), 0)

    def test_invalid_receipts_are_kept(self):
        for i, body in enumerate(('echo \'PG-PROBE-RESULT {"verdict": "GO"}\'; exit 3',
                                  'exit 0',
                                  'echo \'PG-PROBE-RESULT {"verdict": "GO"}\'; echo tail; exit 0',
                                  'echo "PG-PROBE-RESULT {"; exit 0',
                                  'echo \'PG-PROBE-RESULT {"verdict": "GO"}\'; '
                                  'echo \'PG-PROBE-RESULT {"verdict": "GO"}\'; exit 0',
                                  'exit 255')):
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
        self.assertEqual(self.launch('echo \'PG-PROBE-RESULT {"verdict": "STOP"}\'; exit 3'), 3)
        self.assertEqual(hashlib.sha256((self.t / "stdin").read_bytes()).hexdigest(), self.sha)
        self.assertIn(f"# pg-probe.py sha256 {self.sha}", self.out.read_text())


if __name__ == "__main__":
    unittest.main()
