"""Controls for COVFIX PG's tune support and its executable (state/2d-closeout/covfix-20261122/COVFIX-DECLARATION.md
sections 4.1-4.2): pg_lib.py, pg_generate.sh, and the PG additions to gen5d_v3.py, run_gevgen_v3.sh,
setup_genie_v3.sh and fd_f1_prep.py. No GENIE, ROOT or real product is used: pg_generate.sh runs end to end against a
throwaway git deploy whose pipeline steps are stubs that record their arguments.

Run: python3 -B -m pytest -q nd-unfolding/tests/test_covfix_pg.py
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
from unittest import mock

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent
GENIE = REPO / "3d-unfolding" / "genie"
RECORD_DIR = REPO / "docs/orchestration/state/2d-closeout/covfix-20261122/pg/record"
for p in (str(ND), str(ND / "pv-ladder"), str(GENIE)):
    if p not in sys.path:
        sys.path.insert(1, p)
import fd_f1_prep as PREP  # noqa: E402
import gen5d_v3 as V3  # noqa: E402
import pg_lib  # noqa: E402

RECORD = json.loads((RECORD_DIR / "PG-RECORD.json").read_text())
BASE = 1_234_567_890
PG_TUNES = ("G21_11a_00_000", "G18_02a_00_000")


def qualifier(t):
    return t.replace("_", "") + "-k250-e1000"


def seeds(base=BASE, u1="G18_02a_00_000", **over):
    d = {"tunes": [{"u": 0, "name": "G21_11a_00_000", "task_seeds": [base + k for k in range(7)]},
                   {"u": 1, "name": u1, "task_seeds": [base + 10_000 + k for k in range(7)]}]}
    for k, v in over.items():
        u, field = k.split("_", 1)
        d["tunes"][int(u[1])][field] = v
    return d


def quiet(fn, *a, **k):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = fn(*a, **k)
    return rc, out.getvalue(), err.getvalue()


class Seeds(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="pg-seeds-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def load(self, d):
        p = self.tmp / "seeds.json"
        p.write_text(json.dumps(d) if not isinstance(d, str) else d)
        return pg_lib.load_seeds(p)

    def test_valid(self):
        t = self.load(seeds())
        self.assertEqual([(u, n) for u, n, _ in t], [(0, "G21_11a_00_000"), (1, "G18_02a_00_000")])
        self.assertEqual(t[1][2][0], BASE + 10_000)
        for old in ("G18_02b_02_11b", "G18_02a_02_11b"):               # rev 12: no fallback, and not in the product
            with self.assertRaises(pg_lib.Refusal):
                self.load(seeds(u1=old))
        with self.assertRaises(pg_lib.Refusal):
            self.load(seeds(u0_name="G21_11b_00_000"))
        rev = seeds()
        rev["tunes"].reverse()
        self.assertEqual([u for u, _, _ in self.load(rev)], [0, 1])
        top = 2_000_000_000 - 1
        self.assertEqual(self.load(seeds(base=top))[1][2][-1], top + 10_006)   # the declared ceiling holds

    def test_refusals_name_the_rule_not_the_seed(self):
        bad = {
            "not json": "{",
            "extra key": dict(seeds(), extra=1),
            "one tune": {"tunes": seeds()["tunes"][:1]},
            "u repeated": seeds(u1_u=0),
            "u0 wrong tune": seeds(u0_name="G18_10a_02_11b"),
            "u1 spent tune": seeds(u1="AR23_20i_00_000"),
            "six seeds": seeds(u0_task_seeds=[BASE + k for k in range(6)]),
            "string seed": seeds(u0_task_seeds=[str(BASE)] + [BASE + k for k in range(1, 7)]),
            "bool seed": seeds(u0_task_seeds=[True] + [BASE + k for k in range(1, 7)]),
            "gap": seeds(u0_task_seeds=[BASE + k for k in (0, 1, 2, 3, 4, 5, 7)]),
            "stride": seeds(u1_task_seeds=[BASE + 10_001 + k for k in range(7)]),
            "base low": seeds(base=999_999_999),
            "base high": seeds(base=2_000_000_000),
            "ceiling": seeds(base=2 ** 31 - 10_005),
            "extra field": seeds(u0_extra=1),
        }
        for what, d in bad.items():
            with self.subTest(what), self.assertRaises(pg_lib.Refusal) as cm:
                self.load(d)
            msg = str(cm.exception)
            self.assertIsNone(re.search(r"\d{7,}", msg), f"{what}: the refusal prints a number: {msg}")

    def test_the_ceiling_rule_itself(self):
        # a seed exactly at 2**31 - 1 is refused by the ceiling rule, before the base-range rule sees it
        with self.assertRaises(pg_lib.Refusal) as cm:
            self.load(seeds(base=2 ** 31 - 1 - 10_006))
        self.assertIn("2**31 - 1", str(cm.exception))
        self.assertFalse(pg_lib._int(True))
        self.assertTrue(pg_lib._int(7))

    def test_queue(self):
        (self.tmp / "seeds.json").write_text(json.dumps(seeds()))
        out = self.tmp / "queue.txt"
        rc, so, se = quiet(pg_lib.main, ["queue", "--seeds", str(self.tmp / "seeds.json"), "--out", str(out)])
        self.assertEqual(rc, 0)
        lines = out.read_text().splitlines()
        self.assertEqual(len(lines), 14)
        self.assertEqual(lines[0], f"G21_11a_00_000 {BASE} u0/t0")
        self.assertEqual(lines[13], f"G18_02a_00_000 {BASE + 10_006} u1/t6")
        self.assertNotIn(str(BASE)[:7], so + se)
        rc, so, se = quiet(pg_lib.main, ["queue", "--seeds", str(self.tmp / "seeds.json"), "--out", str(out)])
        self.assertEqual(rc, 2)                                         # refuses to overwrite
        (self.tmp / "seeds.json").write_text(json.dumps(seeds(base=5)))
        rc, so, se = quiet(pg_lib.main, ["queue", "--seeds", str(self.tmp / "seeds.json"), "--out",
                                         str(self.tmp / "q2.txt")])
        self.assertEqual(rc, 2)
        self.assertFalse((self.tmp / "q2.txt").exists())

    def test_products(self):
        (self.tmp / "seeds.json").write_text(json.dumps(seeds()))
        argv = ["products", "--workdir", str(self.tmp), "--seeds", str(self.tmp / "seeds.json")]
        self.assertEqual(quiet(pg_lib.main, argv)[0], 2)               # nothing to list yet
        for t in ("genie_v3_g21", "genie_v3_g18_02a"):
            for rel in (f"out/prep/bridged/{t}.json", f"out/prep/ratios/L-5D-PV/{t}.json", f"out/gen5d/{t}_xsec5d.npz"):
                (self.tmp / rel).parent.mkdir(parents=True, exist_ok=True)
                (self.tmp / rel).write_text("x")
        checks = list(pg_lib.CHECKS) + [f"out/trace_check_{r}_{t}.json" for r in ("reduce", "graphs", "coverage")
                                        for t in PG_TUNES] + [f"out/work/u{u}/t{k}/{n}.json" for u in (0, 1)
                                                              for k in range(7) for n in ("trace_check", "trace_check_gntpc")] + [
            f"out/{c}_{t}.json" for c in ("exe_check", "reduce_check", "coverage_check") for t in PG_TUNES] + [
            "out/argv_check.json", "out/messenger_check.json", "out/revision_start.json", "out/revision_end.json",
            "out/revision_compare.json"]
        for c in checks:
            (self.tmp / c).parent.mkdir(parents=True, exist_ok=True)
            (self.tmp / c).write_text('{"check": "x", "pass": true}\n' if "trace" not in c else '{\n "pass": true\n}\n')
        self.assertEqual(len(checks), 3 + 2 * (6 + 14) + 5)
        for broken in ('{"pass": false}\n', "not json\n"):          # a failed or unreadable check refuses
            (self.tmp / checks[5]).write_text(broken)
            self.assertEqual(quiet(pg_lib.main, argv)[0], 2)
        (self.tmp / checks[5]).unlink()                               # so does a missing one
        self.assertEqual(quiet(pg_lib.main, argv)[0], 2)
        (self.tmp / checks[5]).write_text('{\n "pass": true\n}\n')
        self.assertEqual(quiet(pg_lib.main, argv)[0], 0)
        rec = json.loads((self.tmp / "PRODUCTS.json").read_text())
        self.assertEqual(len(rec["checks"]), 48)
        self.assertTrue(all(rec["checks"].values()))
        self.assertEqual([(p["u"], p["truth"], p["bridged"]) for p in rec["products"]],
                         [(0, "genie_v3_g21", "out/prep/bridged/genie_v3_g21.json"),
                          (1, "genie_v3_g18_02a", "out/prep/bridged/genie_v3_g18_02a.json")])
        self.assertEqual(quiet(pg_lib.main, argv)[0], 2)               # refuses to overwrite


class Consistency(unittest.TestCase):
    """The tune names, qualifiers and truth names agree across every file that carries them."""

    def test_names(self):
        self.assertEqual((pg_lib.U0,) + pg_lib.U1, PG_TUNES)
        for t in PG_TUNES:                                 # both are candidates in the offline record, and novel
            self.assertEqual(RECORD["tunes"][t]["role"], "candidate")
            self.assertTrue(RECORD["novelty"][t]["novel"])
        self.assertEqual(sorted(pg_lib.TRUTH.values()), sorted(PREP.PG_TRUTHS))
        self.assertEqual(PREP.PG_U0, pg_lib.TRUTH[pg_lib.U0])
        self.assertEqual(PREP.PG_U1, tuple(pg_lib.TRUTH[t] for t in pg_lib.U1))
        self.assertEqual(pg_lib.RUNG, PREP.RUNG)
        for t in PG_TUNES:
            self.assertIn(t, V3.TUNES)
            self.assertIn(t, PREP.PG_TRUTHS[pg_lib.TRUTH[t]])
            self.assertIn(qualifier(t), V3.TUNES[t])

    def test_qualifier_cases(self):
        run = (GENIE / "run_gevgen_v3.sh").read_text()
        setup = (GENIE / "setup_genie_v3.sh").read_text()
        gen = (GENIE / "pg_generate.sh").read_text()
        for t in PG_TUNES:
            q = qualifier(t)
            self.assertRegex(run, rf"\n\s*{t}\)\s+Q={q} ;;")
            self.assertRegex(setup, rf"\n\s*{t}\)\s+export GENIE_XSEC_QUAL={q.replace('-', ':')} ;;")
            self.assertRegex(gen, rf"\n\s*{t}\) N={pg_lib.TRUTH[t]} ;;")
        # pg_generate.sh derives the source qualifier as the probe does
        self.assertIn("Q=$(echo \"$T\" | tr -d '_')-k250-e1000", gen)

    def test_f1_is_unchanged(self):
        self.assertEqual(sorted(PREP.TRUTHS), ["genie_v3_ar23", "genie_v3_g18"])
        self.assertEqual(sorted(V3.SPLINE_PINS), ["AR23_20i_00_000", "G18_10a_02_11b"])
        self.assertFalse(set(V3.PG_SPLINE_PINS) & set(V3.SPLINE_PINS))

    def test_layout_is_f1b_primes(self):
        gen = (GENIE / "pg_generate.sh").read_text()
        b3 = (ND / "sbatch_fd_f1b3.sh").read_text()
        self.assertIn("NT=7; NEV=160000; P=14; TO=5115", gen)
        self.assertIn("NT=7; NEV=160000", b3)
        self.assertEqual(pg_lib.N_TASKS, 7)
        for x in ("/usr/bin/time -v -o", 'timeout "$TO"', "|| exit 255", 'xargs -P "$P" -L 1'):
            self.assertIn(x, gen)
            self.assertIn(x, b3)

    def test_pg_pins_are_the_records(self):
        self.assertEqual(sorted(V3.PG_SPLINE_PINS), sorted(PG_TUNES))
        for t in PG_TUNES:
            c = RECORD["splines"][t]
            self.assertEqual(V3.PG_SPLINE_PINS[t], (c["spline_sha256"], c["readme_sha256"],
                                                    c["readme_version_lines"][0]))
        m = json.loads((RECORD_DIR / "G2111a-members.json").read_text())["members"]
        d = "genie_xsec/v3_04_00/NULL/G2111a00000-k250-e1000/data/"
        self.assertEqual((m[d + "gxspl-NUsmall.xml"]["sha256"], m[d + "README"]["sha256"]),
                         V3.PG_SPLINE_PINS["G21_11a_00_000"][:2])

    def test_pg_pins_json_is_b1s_receipt(self):
        """pg_pins.json holds the director's pins (2026-11-26), each equal to B1's committed receipt."""
        pins = json.loads((GENIE / "pg_pins.json").read_text())
        res = [ln for ln in (RECORD_DIR.parent / "probe/pg-probe.out").read_text().splitlines()
               if ln.startswith("PG-PROBE-RESULT ")]
        self.assertEqual(len(res), 1)
        b1 = json.loads(res[0][len("PG-PROBE-RESULT "):])
        self.assertEqual(b1["verdict"], "GO")
        tools = b1["tools"]
        self.assertTrue(tools["strace"]["rpm_match"] and tools["awk"]["rpm_match"])
        self.assertEqual(pins["strace_path"], tools["strace"]["path"])
        self.assertEqual(pins["strace_sha256"], tools["strace"]["sha256"])
        self.assertEqual(pins["dbconfig_sha256"], b1["xsec"]["dbconfig"]["sha256"])
        self.assertEqual(pins["system_tools"], {tools["awk"]["path"]: tools["awk"]["sha256"]})
        self.assertEqual((pins["strace_sha256"], pins["dbconfig_sha256"], pins["system_tools"]),
                         ("2c77c18f0493d18f51d6fb11fad9e1a87904a2d2e1247ad2e8b11b2a4a775b87",
                          "accaf71bb0ae10ddd1df30c2b3af8099312e0f5e59ab66d1f42cbab1f00b2950",
                          {"/usr/bin/gawk": "bd00f0bfa560356118968c0c3fca325276e60e4b3bb76a4eee8ddbab96405101"}))

    def test_one_private_products_path(self):
        want = "/pscratch/sd/j/josephrb/covfix-pg/products"
        import pg_verify
        self.assertEqual(pg_verify.PRIVATE_PRODUCTS, want)
        self.assertIn(f"PG_PRIVATE_PRODUCTS={want}\n", (GENIE / "run_gevgen_v3.sh").read_text())
        self.assertIn(f'export PRODUCTS="{want}:${{PRODUCTS}}"', (GENIE / "setup_genie_v3.sh").read_text())
        self.assertIn(f"PRIV={want} ", (GENIE / "pg_generate.sh").read_text())


class Gen5dV3Pins(unittest.TestCase):
    def test_spline_check_refuses_an_unpinned_tune(self):
        tmp = Path(tempfile.mkdtemp(prefix="pg-v3-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        import gzip
        spl = '<genie_xsec_spline_list version="3.00"><genie_tune name="G21_11a_00_000">' \
              '<spline name="genie::X;tgt:1000060120;y">1</spline></genie_tune></genie_xsec_spline_list>'
        (tmp / "src.xml").write_text(spl)
        (tmp / "red.xml.gz").write_bytes(gzip.compress(spl.encode()))
        (tmp / "README").write_text("version v3_04_00 qualifier G2111a00000:k250:e1000\n")
        argv = ["spline-check", "--tune", "G21_11a_00_000", "--source", str(tmp / "src.xml"), "--reduced",
                str(tmp / "red.xml.gz"), "--readme", str(tmp / "README"), "--out", str(tmp / "c.json")]
        with mock.patch.dict(V3.PG_SPLINE_PINS, {}, clear=True):
            self.assertEqual(quiet(V3.main, argv)[0], 1)
        self.assertIn("no pinned spline file", json.loads((tmp / "c.json").read_text())["refused"][0])
        pin = (hashlib.sha256((tmp / "src.xml").read_bytes()).hexdigest(),
               hashlib.sha256((tmp / "README").read_bytes()).hexdigest(),
               "version v3_04_00 qualifier G2111a00000:k250:e1000")
        with mock.patch.dict(V3.PG_SPLINE_PINS, {"G21_11a_00_000": pin}):
            self.assertEqual(quiet(V3.main, argv)[0], 0)


class PrepPG(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="pg-prep-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.base = json.loads((ND / "pv-ladder/config.json").read_text())

    def test_config(self):
        for u1 in PREP.PG_U1:
            cfg = PREP.f1_config(self.base, {"genie_v3_g21": ("/a", "a" * 64), u1: ("/b", "b" * 64)}, "pg")
            self.assertEqual(sorted(cfg["vertices"]), sorted(["genie_v3_g21", u1]))
            self.assertIn("pg", cfg)
            self.assertNotIn("f1", cfg)
            for k in ("schema", "ratio", "rungs", "reference", "declaration"):
                self.assertEqual(cfg[k], self.base[k], k)
        for bad in ({"genie_v3_g21": ("/a", "a")},
                    {"genie_v3_g18_02b": ("/a", "a"), "genie_v3_g18_02a": ("/b", "b")},
                    {"genie_v3_g21": ("/a", "a"), "genie_v3_g18_02b": ("/b", "b")},
                    {"genie_v3_g21": ("/a", "a"), "genie_v3_g18_02b": ("/b", "b"), "genie_v3_g18_02a": ("/c", "c")},
                    {"genie_v3_g21": ("/a", "a"), "genie_v3_g18": ("/b", "b")}):
            with self.subTest(sorted(bad)), self.assertRaises(SystemExit):
                PREP.f1_config(self.base, bad, "pg")
        with self.assertRaises(SystemExit):
            PREP.f1_config(self.base, {"genie_v3_g21": ("/a", "a"), "genie_v3_g18_02a": ("/b", "b")}, "f1")
        with self.assertRaises(SystemExit):
            PREP.f1_config(self.base, {}, "other")

    def test_main_pg(self):
        import numpy as np
        import pvl_lib as L
        n = int(np.prod([len(L.FINE[a]) - 1 for a in L.AXES5]))
        preds = {}
        for k in ("genie_v3_g21", "genie_v3_g18_02a"):
            p = self.tmp / f"{k}.npz"
            p.write_bytes(k.encode())
            preds[k] = p

        def fake_ratios(argv):
            out = Path(argv[argv.index("--out") + 1]) / PREP.RUNG
            out.mkdir(parents=True)
            cfg = json.loads(Path(argv[argv.index("--config") + 1]).read_text())
            for k in cfg["vertices"]:
                (out / f"{k}.json").write_text(json.dumps(
                    {"schema": L.RATIO_SCHEMA, "vertex": k, "label": k, "axes": list(L.AXES5), "r": [1.0] * n,
                     "k": 1.0}))
            return 0
        argv = ["--truth-set", "pg"] + [x for k, p in preds.items()
                                        for x in ("--pred", f"{k}={p}={hashlib.sha256(p.read_bytes()).hexdigest()}")]
        with mock.patch.object(PREP.pvl_ratios, "main", fake_ratios):
            rc, _, _ = quiet(PREP.main, argv + ["--out", str(self.tmp / "o")])
        self.assertEqual(rc, 0)
        self.assertTrue((self.tmp / "o/config-pg.json").exists())
        self.assertFalse((self.tmp / "o/config-f1.json").exists())
        for k in preds:
            self.assertTrue((self.tmp / f"o/bridged/{k}.json").exists())


# ---------------------------------------------------------------------------------------------- pg_generate.sh, stubbed

STUB_RUN = r'''#!/bin/bash
echo "run_gevgen_v3 $*" >> "$PG_STUB_LOG"
echo "trace-env $1 fd=${PG_STRACE_FD:-} dir=${PG_TRACE_DIR:+set}" >> "$PG_STUB_LOG"
case "$1" in
  reduce) mkdir -p "$3"; echo s > "$3/$2_CH.xml.gz"; echo t > "$PG_TRACE_DIR/reduce_$2.trace" ;;
  graphs) cp "$PG_STUB_ROOT" "$4"; echo l > "${4%.root}.log"; echo t > "$PG_TRACE_DIR/graphs_$2.trace" ;;
  genie) mkdir -p "$6"; cd "$6"; echo "[v3] genie $2 N=$4 seed=$5"; echo l > gevgen.log; echo l > gntpc.log
         echo t > "$PG_TRACE_DIR/gevgen.trace"; echo t > "$PG_TRACE_DIR/gntpc.trace"
         echo st > "genie-mcjob-$5.status"; echo "core $(ulimit -c)" >> "$PG_STUB_LOG"
         [ -z "$PG_STUB_LEAK" ] || echo x > "leak-$5.txt"
         [ -z "$PG_STUB_ORPHAN" ] || [ "$5" != "${PG_STUB_ORPHAN}" ] || { ( sleep 60 & echo $! > "$PG_STUB_ORPHAN_PID" ) ; }
         [ -z "$PG_STUB_ORPHAN_CD" ] || [ "$5" != "$PG_STUB_ORPHAN_CD" ] || { ( cd / && exec sleep 60 ) & echo $! > "$PG_STUB_ORPHAN_PID"; }
         [ -n "$PG_STUB_SLOW" ] && { sleep "$PG_STUB_SLOW"; [ -z "$PG_STUB_MARK" ] || echo late >> "$PG_STUB_MARK"; }
         [ "$5" = "${PG_STUB_FAIL_SEED:-none}" ] && { echo ghep > "gntp.$5.ghep.root"; exit 1; }
         [ "$5" = "${PG_STUB_NOGST_SEED:-none}" ] || cp "$PG_STUB_GST" genie_v3.gst.root
         [ -z "$PG_STUB_KEEP_GHEP" ] || echo ghep > "gntp.$5.ghep.root"
         cp "$PG_STUB_ROOT" input-flux.root
         [ -z "$PG_STUB_UNLISTABLE" ] || chmod a-r .
         [ "$5" != "${PG_STUB_LOCK_SEED:-none}" ] || chmod 0555 . ;;
  coverage) mkdir -p "$4"; cd "$4"; echo "Need xsec spline for a" > gevgen.log; echo st > genie-mcjob-123456789.status
         cp "${PG_STUB_GHEP:-$PG_STUB_ROOT}" gntp.123456789.ghep.root; cp "$PG_STUB_ROOT" input-flux.root
         echo t > "$PG_TRACE_DIR/coverage.trace"
         [ -z "$PG_STUB_COVERAGE_EXTRA" ] || echo x > extra.root ;;
esac
'''
STUB_V3 = r'''import sys, os, json
log = open(os.environ["PG_STUB_LOG"], "a"); log.write("gen5d_v3 " + " ".join(sys.argv[1:]) + "\n")
log.write("TMPDIR " + os.environ.get("TMPDIR", "") + "\n")
a = sys.argv[1:]
def arg(k): return a[a.index(k) + 1]
if a[0] == "make-flux": open(arg("--out"), "wb").write(open(os.environ["PG_STUB_ROOT"], "rb").read())
elif a[0] == "spline-check": open(arg("--out"), "w").write(json.dumps({"reduced": {"sha256": "r" * 64}}))
elif a[0] == "flux-check": sys.exit(int(os.environ.get("PG_STUB_FLUXCHECK_RC", "0")))
elif a[0] == "convert":
    open(arg("--out"), "w").write("npz")
    if not os.environ.get("PG_STUB_NO_META"): open(arg("--out")[:-4] + ".meta.json", "w").write("{}")
''' + "PG_SPLINE_PINS = " + repr({"G21_11a_00_000": ("a" * 64, "b" * 64, "v"), "G18_02a_00_000": ("c" * 64, "d" * 64, "v")}) + "\n"
STUB_VERIFY = r'''import sys, os
log = open(os.environ["PG_STUB_LOG"], "a"); log.write("pg_verify " + " ".join(sys.argv[1:]) + "\n"); log.flush()
a = sys.argv[1:]
if a[0] == "drain":                                   # the real scan and drain, the code under test
    os.execv(sys.executable, [sys.executable, "-I", "-B", "{real}"] + a)
if a[0] == "trace-check":
    opened = "false" if os.environ.get("PG_STUB_NO_SPLINE") else "true"
    prog = {"reduce": "awk", "graphs": "gspl2root", "gntpc": "gntpc"}.get(a[a.index("--role") + 1], "gevgen")
    ex = '[{"path": "/b/%s", "real": "/b/%s", "sha256": "%s", "bound_by": "genie manifest"}]' % (prog, prog, "3" * 64)
    open(a[a.index("--out") + 1], "w").write('{"pass": true, "initial_opened_spline": %s, "gated": [], "execs": %s}'
                                             % (opened, ex))
fail = os.environ.get("PG_STUB_VERIFY_FAIL")
if fail and fail in " ".join(a):
    print('{"pass": false}'); sys.exit(1)
if a[0] == "messenger":
    open(a[a.index("--out") + 1], "x").write("messenger")
if a[0] == "revision":
    n = sum(1 for ln in open(os.environ["PG_STUB_LOG"]) if ln.startswith("pg_verify revision"))
    rev = "2" if os.environ.get("PG_STUB_REVISION_CHANGE") and n >= 2 else "1"
    print('{"pass": true, "revision": "%s", "root_hash": "h"}' % rev); sys.exit(0)
if a[0] == "revision-compare":
    import json as _j
    st, en = (_j.load(open(a[a.index(k) + 1])) for k in ("--start", "--end"))
    ok = st.get("revision") == en.get("revision")
    print('{"pass": %s}' % ("true" if ok else "false")); sys.exit(0 if ok else 1)
if a[0] == "host-check":
    n = 2 if os.environ.get("PG_STUB_TWO_HOST") else 3
    print('{"pass": true, "checks": {%s}}' % ", ".join('"h%d": true' % i for i in range(n))); sys.exit(0)
if a[0] == "shape-check" and os.environ.get("PG_STUB_BAD_RECORD"):      # a broken earlier deletion record
    open(os.path.join(os.path.dirname(a[a.index("--traces") + 1]), "deleted.json"), "w").write("{")
if a[0] == "shape-check" and os.environ.get("PG_STUB_PRIOR"):           # an earlier record of the wrong shape
    open(os.path.join(os.path.dirname(a[a.index("--traces") + 1]), "deleted.json"), "w").write(os.environ["PG_STUB_PRIOR"])
if a[0] == "shape-check" and os.environ.get("PG_STUB_UNREADABLE"):     # after hadd: the gst unreadable at deletion
    os.chmod(os.path.join(os.path.dirname(a[a.index("--traces") + 1]), "work/t0/genie_v3.gst.root"), 0)
if a[0] == "shape-check":
    n = 3 if os.environ.get("PG_STUB_THREE_SHAPES") else 4
    print('{"pass": true, "checks": {%s}}' % ", ".join('"s%d": true' % i for i in range(n))); sys.exit(0)
print('{"pass": true}')
'''
STRACE = "#!/bin/sh\necho strace-stub\n"
STUB_PREP = r'''import sys, os
log = open(os.environ["PG_STUB_LOG"], "a"); log.write("fd_f1_prep " + " ".join(sys.argv[1:]) + "\n")
a = sys.argv[1:]
out = a[a.index("--out") + 1]
for i, x in enumerate(a):
    if x == "--pred":
        n = a[i + 1].split("=")[0]
        for d in ("bridged", "ratios/L-5D-PV"):
            os.makedirs(os.path.join(out, d), exist_ok=True)
            open(os.path.join(out, d, n + ".json"), "w").write(n)
for f in ("config-pg.json", "f1-prep-SHA256SUMS", "ratios/L-5D-PV/ratios.json"):
    open(os.path.join(out, f), "w").write("x")
if os.environ.get("PG_STUB_WRITE_DEPLOY"):
    open(os.path.join(os.environ["PG_STUB_DEPLOY"], "stray.txt"), "w").write("x")
'''
STUB_ENV = '''export PATH="$PG_STUB_BIN:$PATH"\nexport TMPDIR=/tmp/elsewhere   # as setup_salloc_env.sh does\n''' + r'''
SD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
case "$PG_STUB_ENV" in        # the two build-tree setups git does not carry, as bash reports a missing source
  tolerated|extra|conda|clobber)
    echo "$SD/setup_salloc_env.sh: line 18: $SD/unbinned_unfolding/build/setup.sh: No such file or directory" >&2
    echo "$SD/setup_salloc_env.sh: line 21: $SD/MINERvA101/opt/bin/setup.sh: No such file or directory" >&2 ;;
esac
case "$PG_STUB_ENV" in
  extra) echo "conda: a warning nobody expected" >&2 ;;
  missing-other) echo "$SD/setup_salloc_env.sh: line 30: $SD/other/setup.sh: No such file or directory" >&2 ;;
  conda) export HOST=x86_64-conda-linux-gnu CC=x86_64-conda-linux-gnu-cc BUILD=x86_64-conda-linux-gnu ;;
  clobber) PRIV=/elsewhere ;;
esac
[ -z "$PG_STUB_DIRTY_AT" ] || [ "$1" != "$PG_STUB_DIRTY_AT" ] || touch "$SD/dirty-from-$1"   # a write into the deploy
'''
PY311 = '''#!/bin/bash
[ "$1" = "-V" ] && { echo "Python 3.11.14"; exit 0; }
exec {py} "$@"
'''
HADD = '''#!/bin/bash
echo "hadd $*" >> "$PG_STUB_LOG"; o=$1; shift
case "$o" in *"${PG_STUB_HADD_FAIL:-none}"*) exit 1 ;; esac
case "$o" in *"${PG_STUB_HADD_SLOW:-none}"*) sleep 3; echo late > "$PG_STUB_MARK" ;; esac
cp "$1" "$o"     # one ROOT file stands in for the merge
'''
TIMEOUT = '''#!/bin/bash
# GNU timeout (coreutils timeout.c): unless --foreground, it calls setpgid(0, 0), so the command runs in a new
# process group of its own, inside the caller's session
echo "timeout $1" >> "$PG_STUB_LOG"; shift
exec {py} -I -c 'import os, sys; os.setpgid(0, 0); os.execvp(sys.argv[1], sys.argv[1:])' "$@"
'''
TIMEV = '''#!/bin/bash
[ "$1" = "-v" ] && [ "$2" = "-o" ] || exit 9
o=$3; shift 3; "$@"; rc=$?; echo "Exit status: $rc" > "$o"; exit $rc
'''


class Generate(unittest.TestCase):
    """pg_generate.sh against a throwaway git deploy with stubbed pipeline steps."""

    def setUp(self):
        self.tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix="pg-gen-", dir="/tmp")))   # W must be physical
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.dep = self.tmp / "deploy"
        g = self.dep / "3d-unfolding/genie"
        g.mkdir(parents=True)
        (self.dep / "nd-unfolding").mkdir()
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        timev = self.bin / "timev"
        src = (GENIE / "pg_generate.sh").read_text()
        self.assertEqual(src.count("/usr/bin/time -v -o"), 1)
        self.assertEqual(src.count("PY=/usr/bin/python3.11"), 1)
        (g / "pg_generate.sh").write_text(src.replace("/usr/bin/time -v -o", f"{timev} -v -o").replace(
            "PY=/usr/bin/python3.11", f"PY={sys.executable}"))
        shutil.copy(GENIE / "pg_lib.py", g / "pg_lib.py")
        (g / "pg_verify.py").write_text(STUB_VERIFY.replace("{real}", str(GENIE / "pg_verify.py")))
        rec = self.dep / "docs/orchestration/state/2d-closeout/covfix-20261122/pg/record"
        rec.mkdir(parents=True)
        (rec / "G2111a-members.json").write_text(json.dumps({"members": {"genie_xsec": {"type": "dir"}}}))
        for n in ("PG-RECORD.json", "genie-manifest.json"):
            (rec / n).write_text("{}")
        self.gst_tpl, self.root_tpl = self.tmp / "tpl.gst.root", self.tmp / "tpl.root"   # real ROOT layouts
        self.gst_tpl.write_bytes(root_file([_key("TFile", "genie_v3.gst.root", "", b"top", codec=None),
                                            _basket("iev", "gst", b"pad" * 40),
                                            _key("TTree", "gst", "GENIE Summary Event Tree", b"tree" * 30),
                                            _key("TList", "StreamerInfo", "Doubly linked list", b"streamer" * 20)]))
        self.root_tpl.write_bytes(root_file([_key("TH1D", "h", "flux", b"bins" * 30)]))
        self.ghep_tpl = self.tmp / "tpl.ghep.root"   # GENIE's run number (gevgen -r, the seed) in its header, written first
        self.ghep_tpl.write_bytes(_ghep(123456789, None))                   # stored: R1
        self.ghep_tpl_z = self.tmp / "tpl-z.ghep.root"
        self.ghep_tpl_z.write_bytes(_ghep(123456789, b"ZL"))
        (rec / "root-schemas.json").write_text(json.dumps({"gst": pg_lib.root_schema(str(self.gst_tpl)),
                                                           "gst_merged": pg_lib.root_schema(str(self.gst_tpl))}))
        (g / "run_gevgen_v3.sh").write_text(STUB_RUN)
        (g / "setup_genie_v3.sh").write_text('export PATH="$PG_STUB_BIN:$PATH"\n')
        (g / "gen5d_v3.py").write_text(STUB_V3)
        (self.dep / "nd-unfolding/fd_f1_prep.py").write_text(STUB_PREP)
        (self.dep / "setup_salloc_env.sh").write_text(STUB_ENV)
        for name, body in (("python3", PY311.replace("{py}", sys.executable)), ("hadd", HADD), ("timev", TIMEV),
                           ("gevgen", "#!/bin/sh\n"), ("gspl2root", "#!/bin/sh\n")):
            (self.bin / name).write_text(body)
            (self.bin / name).chmod(0o755)
        self.sysbin = self.tmp / "sysbin"            # what /usr/bin gives on Perlmutter and not on macOS
        self.sysbin.mkdir()
        (self.sysbin / "timeout").write_text(TIMEOUT.replace("{py}", sys.executable))
        (self.sysbin / "timeout").chmod(0o755)
        (self.sysbin / "strace").write_text(STRACE)
        (g / "pg_pins.json").write_text(json.dumps({"strace_path": str(self.sysbin / "strace"),
                                                    "strace_sha256": "e" * 64, "dbconfig_sha256": "f" * 64,
                                                    "system_tools": {"/usr/bin/gawk": "a" * 64}}))
        git = ["git", "-C", str(self.dep), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(git[:3] + ["init", "-q"], check=True)
        subprocess.run(git + ["add", "-A"], check=True)
        subprocess.run(git + ["commit", "-qm", "stub"], check=True)
        self.pin = subprocess.run(git[:3] + ["rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        self.W = self.tmp / "W"
        (self.W / "tmp").mkdir(parents=True)
        (self.W / "tmp").chmod(0o700)
        (self.W / "seeds.json").write_text(json.dumps(seeds()))
        self.log = self.tmp / "stub.log"

    def run_gen(self, cwd=None, args=None, **env):
        e = {"PATH": f"/usr/bin:/bin:/usr/sbin:/sbin:{self.sysbin}", "HOME": str(self.tmp), "TMPDIR": str(self.W / "tmp"),
             "PG_DEPLOY_PIN": self.pin, "PG_STUB_LOG": str(self.log), "PG_STUB_BIN": str(self.bin),
             "PG_STUB_DEPLOY": str(self.dep), "PG_STUB_GST": str(self.gst_tpl), "PG_STUB_ROOT": str(self.root_tpl)}
        e.update(env)
        argv = args if args is not None else ["--workdir", str(self.W), "--seeds", str(self.W / "seeds.json")]
        return subprocess.run(["bash", str(self.dep / "3d-unfolding/genie/pg_generate.sh")] + argv,
                              cwd=cwd or self.W, env=e, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    def test_end_to_end(self):
        p = self.run_gen()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        out = p.stdout + p.stderr
        for s in seeds()["tunes"][0]["task_seeds"] + seeds()["tunes"][1]["task_seeds"]:
            self.assertNotIn(str(s), out)
        self.assertNotIn(str(self.W), out)
        self.assertIn("[pg] the deploy unchanged: pass", out)
        self.assertIn("[pg] the required inventory: pass", out)
        tenv = [ln for ln in self.log.read_text().splitlines() if ln.startswith("trace-env ")]
        self.assertEqual(len(tenv), 2 + 2 + 2 + 14)                 # reduce, graphs, coverage, tasks: all on fd 9
        self.assertTrue(all(ln.endswith(" fd=9 dir=set") for ln in tenv), tenv)
        self.assertEqual(pg_lib.inventory_problems(str(self.W), pg_lib.inventory()), [])
        checks = json.loads((self.W / "PRODUCTS.json").read_text())["checks"]
        self.assertEqual(len(checks), 3 + 2 * (6 + 2 * 7) + 5)
        self.assertTrue(all(checks.values()))
        self.assertIn("[pg] generation: pass (14 gst)", out)
        log = self.log.read_text().splitlines()
        gen = [ln.split() for ln in log if ln.startswith("run_gevgen_v3 genie")]
        self.assertEqual(len(gen), 14)
        want = {(t["name"], str(s), f"u{t['u']}/t{k}") for t in seeds()["tunes"] for k, s in enumerate(t["task_seeds"])}
        got = {(g[2], g[5], g[6].split("/work/")[1]) for g in gen}
        self.assertEqual(got, want)
        self.assertTrue(all(g[4] == "160000" for g in gen))
        self.assertTrue(all(g[3].endswith("/out/splines") for g in gen))
        self.assertEqual(sum(ln == "timeout 5115" for ln in log), 14)
        self.assertEqual(sorted(ln.split()[2] for ln in log if ln.startswith("run_gevgen_v3 reduce")),
                         ["G18_02a_00_000", "G21_11a_00_000"])
        checks = [ln for ln in log if ln.startswith("gen5d_v3 spline-check")]
        self.assertEqual(len(checks), 2)
        self.assertIn("/pscratch/sd/j/josephrb/covfix-pg/products/genie_xsec/v3_04_00/NULL/G2111a00000-k250-e1000/"
                      "data/gxspl-NUsmall.xml", checks[0])
        self.assertIn("/cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/v3_04_00/NULL/G1802a00000-k250-e1000/"
                      "data/README", checks[1])
        ver = [ln.split() for ln in log if ln.startswith("pg_verify ")]
        self.assertEqual([v[1] for v in ver[:2]], ["tool-check", "revision"])     # the CVMFS revision right after strace
        self.assertEqual([v[1] for v in ver if v[1] == "revision"], ["revision", "revision"])   # and at the end
        self.assertEqual([v[1] for v in ver if v[1] == "node-record"], ["node-record"])
        rc_ = next(v for v in ver if v[1] == "revision-compare")                 # the end revision against the start,
        self.assertEqual(sum(x == "--trace-check" for x in rc_), 2 * 7 * 2 + 3 * 2)   # with every trace check's files
        gn = [v for v in ver if v[1] == "trace-check" and v[v.index("--role") + 1] == "gntpc"]
        self.assertEqual(len(gn), 14)
        for v in gn:                                                             # B4: its own task's GHEP
            self.assertEqual(v[v.index("--ghep-from-trace") + 1], v[v.index("--cwd") + 1] + "/gevgen.trace")
        ph = [v for v in ver if v[1] == "pin-hash"]                              # Q1: every pin, at both ends
        self.assertEqual(len(ph), 2)
        for v in ph:
            self.assertEqual(v[v.index("--manifest") + 1].rsplit("/", 1)[1], "genie-manifest.json")
            self.assertEqual(v[v.index("--products") + 1], "/cvmfs/larsoft.opensciencegrid.org/products")
            self.assertEqual(sum(x == "--pin" for x in v), 2)                    # slot 2's spline and README
        at = [i for i, v in enumerate(ver) if v[1] == "pin-hash"]
        tc = [i for i, v in enumerate(ver) if v[1] == "trace-check"]
        self.assertLess(at[0], min(tc))                                          # before anything is traced,
        self.assertGreater(at[1], max(tc))                                       # and after the last trace check
        self.assertTrue(any(v[1] == "drain" for v in ver))
        ver = [v for v in ver if v[1] not in ("revision", "node-record", "revision-compare", "pin-hash", "drain")]
        self.assertEqual([v[1] for v in ver[:5]], ["tool-check", "members-check", "tool-check", "exe-check", "exe-check"])
        for v in ver[3:5]:                                        # the programs as each tune's setup resolves them
            self.assertEqual([v[i + 1].rsplit("/", 1)[1] for i, x in enumerate(v) if x == "--path"], ["gevgen", "gspl2root"])
        last_exe = max(i for i, ln in enumerate(log) if ln.startswith("pg_verify exe-check"))
        self.assertLess(last_exe, next(i for i, ln in enumerate(log) if ln.startswith("run_gevgen_v3")))
        for v in ver[3:5]:
            self.assertIn("--ld-library-path", v)
            self.assertIn("--system-path", v)
            self.assertEqual(v[v.index("--system-path") + 1], "/usr/bin/awk")
        self.assertEqual(log.index(" ".join(ver[0])), 0)                           # strace is the first step
        self.assertIn("--self-test", ver[0])
        self.assertIn("--fd", ver[0])
        self.assertEqual(ver[0][ver[0].index("--fd") + 1], "9")                 # checked through the descriptor
        self.assertNotIn("--path", ver[0])
        self.assertEqual(ver[0][ver[0].index("--sha256") + 1], "e" * 64)
        self.assertEqual(ver[2][ver[2].index("--sha256") + 1], "f" * 64)
        tc = [v for v in ver if v[1] == "trace-check"]
        self.assertEqual(sorted(v[v.index("--role") + 1] for v in tc),
                         ["coverage"] * 2 + ["gevgen"] * 14 + ["gntpc"] * 14 + ["graphs"] * 2 + ["reduce"] * 2)
        first_gen_i = next(i for i, ln in enumerate(self.log.read_text().splitlines()) if ln.startswith("run_gevgen_v3 genie"))
        cov_i = [i for i, ln in enumerate(self.log.read_text().splitlines()) if "--role coverage" in ln]
        self.assertTrue(cov_i and max(cov_i) < first_gen_i)                      # coverage before any sealed seed
        for v in tc:                                                             # GXMLPATH and the system pins, always
            role = v[v.index("--role") + 1]
            self.assertEqual("--messenger" in v, role == "coverage")              # the messenger is pinned in the check
            if role == "coverage":
                self.assertTrue(v[v.index("--messenger") + 1].endswith("/out/Messenger_pg.xml"))
            self.assertEqual("--output" in v, role == "graphs")
            self.assertIn("--gxmlpath", v)
            self.assertEqual(v[v.index("--system-pin") + 1], "/usr/bin/gawk=" + "a" * 64)
        first_gen = next(i for i, ln in enumerate(log) if ln.startswith("run_gevgen_v3 genie"))
        last_pre = max(i for i, ln in enumerate(log) if ln.startswith("pg_verify trace-check") and "--role graphs" in ln)
        self.assertLess(last_pre, first_gen)                                    # conditions 2 and 3 before generation
        red = next(v for v in tc if v[v.index("--role") + 1] == "reduce" and "G21_11a_00_000" in v)
        self.assertEqual(red[red.index("--spline-sha256") + 1], "a" * 64)
        self.assertIn("/covfix-pg/products/genie_xsec/", red[red.index("--spline") + 1])
        self.assertNotIn("--pin", red)                                          # slot 1: its members pin it
        x2 = "/cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/v3_04_00/NULL/G1802a00000-k250-e1000/data"
        for v in (v for v in tc if "G18_02a_00_000" in v):                      # slot 2: exact pins at CVMFS's paths
            pins = [v[i + 1] for i, x in enumerate(v) if x == "--pin"]
            self.assertEqual(pins, [f"{x2}/gxspl-NUsmall.xml={'c' * 64}", f"{x2}/README={'d' * 64}"])
        fc = [ln for ln in log if ln.startswith("gen5d_v3 flux-check")][0]
        self.assertEqual(len(re.findall(r"/work/u[01]/t\d", fc)), 14)
        conv = [ln for ln in log if ln.startswith("gen5d_v3 convert")]
        self.assertEqual(sorted(re.search(r"--tune (\S+)", c).group(1) for c in conv),
                         ["G18_02a_00_000", "G21_11a_00_000"])
        prep = [ln for ln in log if ln.startswith("fd_f1_prep")][0]
        self.assertIn("--truth-set pg", prep)
        self.assertRegex(prep, r"--pred genie_v3_g21=\S+/out/gen5d/genie_v3_g21_xsec5d\.npz=[0-9a-f]{64}")
        self.assertRegex(prep, r"--pred genie_v3_g18_02a=\S+genie_v3_g18_02a_xsec5d\.npz=[0-9a-f]{64}")
        rec = json.loads((self.W / "PRODUCTS.json").read_text())
        self.assertEqual([x["truth"] for x in rec["products"]], ["genie_v3_g21", "genie_v3_g18_02a"])
        tmpdirs = {ln.split(" ", 1)[1] for ln in log if ln.startswith("TMPDIR ")}
        self.assertEqual(tmpdirs, {str(self.W / "tmp")})              # re-exported after every activation
        for u in (0, 1):
            for k in range(7):
                self.assertIn("[v3] genie", (self.W / f"out/work/u{u}/t{k}/task.log").read_text())
        self.assertEqual(list(self.W.rglob("genie-mcjob-*")), [])
        self.assertEqual(len(list(self.W.rglob("gevgen.status"))), 14)
        sums = (self.W / "out/PG-SHA256SUMS").read_text()
        for f in ("./flux_phi_t_0_100.root", "./graphs_G21_11a_00_000.root", "./spline_check_G18_02a_00_000.json",
                  "./gen5d/genie_v3_g21_xsec5d.npz", "./prep/bridged/genie_v3_g21.json", "./work/u1/t6/genie_v3.gst.root"):
            self.assertIn(f"  {f}\n", sums)
        self.assertNotIn("./logs/", sums)
        self.assertNotIn("PG-SHA256SUMS", sums)
        names = [str(q.relative_to(self.W)) for q in self.W.rglob("*")]
        for s in seeds()["tunes"][0]["task_seeds"] + seeds()["tunes"][1]["task_seeds"]:
            self.assertFalse([n for n in names if str(s) in n], f"seed {s} in a file name")
        self.assertEqual(subprocess.run(["git", "-C", str(self.dep), "status", "--porcelain", "--ignored",
                                         "--untracked-files=all"], capture_output=True, text=True).stdout, "")
        self.assertEqual(sorted(x.name for x in self.tmp.iterdir()),                # the ROOT templates are the test's
                         ["W", "bin", "deploy", "stub.log", "sysbin", "tpl-z.ghep.root", "tpl.ghep.root", "tpl.gst.root", "tpl.root"])

    def refused(self, p, rc=2):
        self.assertEqual(p.returncode, rc, p.stdout + p.stderr)
        self.assertFalse((self.W / "out").exists() and rc == 2)
        self.assertFalse(self.log.exists() and rc == 2)

    def test_refusals(self):
        self.refused(self.run_gen(cwd=self.tmp))                                 # cwd is not W
        self.refused(self.run_gen(TMPDIR="/tmp"))                                # TMPDIR is not W/tmp
        self.refused(self.run_gen(PG_DEPLOY_PIN="0" * 40))                       # another commit
        self.refused(self.run_gen(PG_DEPLOY_PIN=""))
        self.refused(self.run_gen(args=["--workdir", str(self.W), "--seeds", str(self.tmp / "s.json")]))
        self.refused(self.run_gen(args=["--workdir", "W", "--seeds", "W/seeds.json"]))
        self.refused(self.run_gen(args=["--workdir", str(self.W), "--seeds", str(self.W / "seeds.json"), "-x"]))
        (self.dep / "setup_salloc_env.sh").write_text(STUB_ENV + "# modified\n")
        self.refused(self.run_gen())                                             # a modified tracked file
        subprocess.run(["git", "-C", str(self.dep), "checkout", "-q", "--", "."], check=True)
        (self.W / "PRODUCTS.json").write_text("{}")
        self.refused(self.run_gen())                                             # an earlier attempt's output
        os.remove(self.W / "PRODUCTS.json")
        self.assertEqual(self.run_gen().returncode, 0)

    def test_bad_seeds_stop_before_any_step(self):
        (self.W / "seeds.json").write_text(json.dumps(seeds(base=5)))
        p = self.run_gen()
        self.assertEqual(p.returncode, 1)
        self.assertIn("[pg] STOP: seeds.json", p.stdout)
        self.assertEqual({ln.split()[0] for ln in self.log.read_text().splitlines()}, {"pg_verify"})   # checks only

    def no_seed_in_any_name(self):
        names = [q.name for q in self.W.rglob("*")]
        for t in seeds()["tunes"]:
            for x in t["task_seeds"]:
                self.assertEqual([n for n in names if str(x) in n], [], f"seed {x} in a file name")
        self.assertEqual([n for n in names if n.startswith("genie-mcjob")], [])

    def test_a_failed_task_stops_and_leaves_no_seed_in_a_name(self):
        p = self.run_gen(PG_STUB_FAIL_SEED=str(BASE + 10_003))
        self.assertEqual(p.returncode, 1)
        self.assertIn("[pg] STOP: generation", p.stdout)
        self.assertNotIn(str(BASE + 10_003), p.stdout + p.stderr)
        self.assertFalse((self.W / "PRODUCTS.json").exists())
        self.no_seed_in_any_name()
        self.assertTrue((self.W / "out/work/u1/t3/gntp.ghep.root").exists())     # kept, under a seed-free name
        self.assertEqual(len(list(self.W.rglob("gevgen.status"))), 14)

    def test_a_missing_gst_stops_before_any_conversion(self):
        p = self.run_gen(PG_STUB_NOGST_SEED=str(BASE + 10_006))
        self.assertEqual(p.returncode, 1)
        self.assertIn("[pg] STOP: u1 has 6 of 7 gst files", p.stdout)
        self.assertFalse([ln for ln in self.log.read_text().splitlines() if ln.startswith(("hadd", "gen5d_v3 convert"))])
        self.no_seed_in_any_name()

    def test_a_stop_ends_the_other_background_steps(self):
        mark = self.tmp / "late-marker"
        p = self.run_gen(PG_STUB_HADD_FAIL="genie_v3_g21_ALL", PG_STUB_HADD_SLOW="genie_v3_g18_02a_ALL",
                         PG_STUB_MARK=str(mark))
        self.assertEqual(p.returncode, 1)
        self.assertIn("[pg] STOP: hadd or conversion", p.stdout)
        import time
        time.sleep(4.5)
        self.assertFalse(mark.exists(), "the sibling hadd kept running after the STOP")

    def test_tasks_rename_their_own_files_if_the_script_is_killed(self):
        import signal
        import time
        e = {"PATH": f"/usr/bin:/bin:/usr/sbin:/sbin:{self.sysbin}", "HOME": str(self.tmp),
             "TMPDIR": str(self.W / "tmp"), "PG_DEPLOY_PIN": self.pin, "PG_STUB_LOG": str(self.log),
             "PG_STUB_BIN": str(self.bin), "PG_STUB_DEPLOY": str(self.dep), "PG_STUB_SLOW": "2",
             "PG_STUB_GST": str(self.gst_tpl), "PG_STUB_ROOT": str(self.root_tpl)}
        proc = subprocess.Popen(["bash", str(self.dep / "3d-unfolding/genie/pg_generate.sh"), "--workdir", str(self.W),
                                 "--seeds", str(self.W / "seeds.json")], cwd=self.W, env=e, stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t0 = time.time()
        while len(list(self.W.rglob("genie-mcjob-*.status"))) < 14 and time.time() - t0 < 20:
            time.sleep(0.05)
        self.assertEqual(len(list(self.W.rglob("genie-mcjob-*.status"))), 14)
        os.kill(proc.pid, signal.SIGKILL)                      # no trap runs; the tasks carry on
        proc.wait()
        t0 = time.time()
        while len(list(self.W.rglob("task.time"))) < 14 and time.time() - t0 < 20:
            time.sleep(0.05)
        time.sleep(0.5)
        self.no_seed_in_any_name()

    def test_a_term_during_generation_ends_every_task(self):
        import signal
        import time
        mark = self.tmp / "late-marker"
        e = {"PATH": f"/usr/bin:/bin:/usr/sbin:/sbin:{self.sysbin}", "HOME": str(self.tmp),
             "TMPDIR": str(self.W / "tmp"), "PG_DEPLOY_PIN": self.pin, "PG_STUB_LOG": str(self.log),
             "PG_STUB_BIN": str(self.bin), "PG_STUB_DEPLOY": str(self.dep), "PG_STUB_SLOW": "3", "PG_STUB_MARK": str(mark),
             "PG_STUB_GST": str(self.gst_tpl), "PG_STUB_ROOT": str(self.root_tpl)}
        out = open(self.tmp / "term.out", "w")
        proc = subprocess.Popen(["bash", str(self.dep / "3d-unfolding/genie/pg_generate.sh"), "--workdir", str(self.W),
                                 "--seeds", str(self.W / "seeds.json")], cwd=self.W, env=e, stdin=subprocess.DEVNULL,
                                stdout=out, stderr=subprocess.DEVNULL)
        t0 = time.time()
        while len(list(self.W.rglob("genie-mcjob-*.status"))) < 14 and time.time() - t0 < 20:
            time.sleep(0.05)
        os.kill(proc.pid, signal.SIGTERM)
        self.assertEqual(proc.wait(timeout=25), 143)                      # no 30 s stall on a zombie job
        out.close()
        self.assertNotIn("outlived their trees", (self.tmp / "term.out").read_text())   # the walk, not the backstop
        time.sleep(4)
        self.assertFalse(mark.exists(), "a task kept running after the script ended")
        self.no_seed_in_any_name()

    def test_round3_stops(self):
        for env, msg in (({"PG_STUB_REVISION_CHANGE": "1"}, "[pg] STOP: the CVMFS revision changed and a file"),
                         ({"PG_STUB_COVERAGE_EXTRA": "1"}, "[pg] STOP: the coverage run's outputs (G21_11a_00_000): unexpected extra.root"),
                         ({"PG_STUB_LEAK": "1"}, "[pg] STOP: the publish set and its leak scan")):
            with self.subTest(msg):
                for d in ("out", "run", "PRODUCTS.json"):
                    q = self.W / d
                    shutil.rmtree(q) if q.is_dir() else q.unlink() if q.exists() else None
                if self.log.exists():
                    self.log.unlink()
                p = self.run_gen(**env)
                self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
                self.assertIn(msg, p.stdout)
                if "leak" in msg:
                    self.assertFalse((self.W / "out/PG-PUBLISH-SHA256SUMS").exists())
                    for t_ in seeds()["tunes"]:                          # the refusal names no seed
                        self.assertFalse(any(str(x) in (self.W / "out/logs/publish.log").read_text()
                                             for x in t_["task_seeds"]))

    def test_round3_refusals(self):
        p = self.run_gen(PYTHONPATH="/x")
        self.assertEqual(p.returncode, 2)
        self.assertIn("refusing: PYTHONPATH is set", p.stderr)
        link = self.tmp / "Wlink"
        link.symlink_to(self.W)
        p = self.run_gen(cwd=link, args=["--workdir", str(link), "--seeds", str(link / "seeds.json")],
                         TMPDIR=str(link / "tmp"))
        self.assertEqual(p.returncode, 2)
        self.assertIn("W must be its own physical path", p.stderr)
        (self.dep / ".git/info").mkdir(parents=True, exist_ok=True)
        (self.dep / ".git/info/exclude").write_text("*.pyc\n")
        (self.dep / "3d-unfolding/genie/x.pyc").write_text("x")              # an ignored file in the deploy
        p = self.run_gen()
        self.assertEqual(p.returncode, 2)
        self.assertIn("the deploy is not the pinned commit, or is modified", p.stderr)

    def test_unfilled_system_pins_refuse(self):
        g = self.dep / "3d-unfolding/genie/pg_pins.json"
        d = json.loads(g.read_text())
        d["system_tools"] = {}
        g.write_text(json.dumps(d))
        git = ["git", "-C", str(self.dep), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(git + ["commit", "-qam", "unpin"], check=True)
        pin = subprocess.run(git[:3] + ["rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        p = self.run_gen(PG_DEPLOY_PIN=pin)
        self.assertEqual(p.returncode, 2)
        self.assertIn("pg_pins.json is not filled (R1)", p.stderr)

    def test_round4_refusals(self):
        for v in ("GXMLPATHS", "GALGCONF"):                                       # GENIE's other XML lookups
            p = self.run_gen(**{v: "/evil"})
            self.assertEqual((p.returncode, f"refusing: {v} is set" in p.stderr), (2, True), p.stderr)
        t = self.W / "tmp"
        t.chmod(0o755)
        p = self.run_gen()
        self.assertEqual((p.returncode, "W/tmp must be a real directory" in p.stderr), (2, True), p.stderr)
        t.chmod(0o700)
        t.rename(self.W / "tmp-real")
        t.symlink_to(self.W / "tmp-real")
        p = self.run_gen()
        self.assertEqual((p.returncode, "W/tmp must be a real directory" in p.stderr), (2, True), p.stderr)
        t.unlink()
        (self.W / "tmp-real").rename(t)
        gs = self.tmp / "gitstub"                                                 # git status itself fails: its Nth call
        gs.mkdir()
        (gs / "git").write_text('#!/bin/bash\ncase " $* " in *" status "*) n=$(( $(cat "$PG_GIT_N" 2>/dev/null || echo 0) + 1 ))\n'
                                '  echo $n > "$PG_GIT_N"; [ "$n" != "$PG_GIT_FAIL_AT" ] || exit 128 ;; esac\n'
                                'exec /usr/bin/git "$@"\n')
        (gs / "git").chmod(0o755)
        for at, rc, where in (("1", 2, "stderr"), ("2", 2, "stderr"), ("3", 1, "stdout")):   # the check, the record, setup
            with self.subTest(at):
                for d in ("out", "run"):
                    shutil.rmtree(self.W / d, ignore_errors=True)
                (self.tmp / "git.n").unlink(missing_ok=True)
                p = self.run_gen(PATH=f"{gs}:/usr/bin:/bin:/usr/sbin:/sbin:{self.sysbin}", PG_GIT_FAIL_AT=at,
                                 PG_GIT_N=str(self.tmp / "git.n"))
                self.assertEqual((p.returncode, "git status failed" in getattr(p, where)), (rc, True), p.stdout + p.stderr)
        for d in ("out", "run"):
            shutil.rmtree(self.W / d, ignore_errors=True)
        rec = self.dep / "docs/orchestration/state/2d-closeout/covfix-20261122/pg/record/root-schemas.json"
        git = ["git", "-C", str(self.dep), "-c", "user.name=t", "-c", "user.email=t@t"]
        schema = json.loads(rec.read_text())["gst"]
        for i, body in enumerate(({"gst": None, "gst_merged": None}, {"gst": schema, "gst_merged": None})):
            rec.write_text(json.dumps(body))                                 # unset, or hadd's kind missing
            subprocess.run(git + ["commit", "-qam", f"unset {i}"], check=True)
            pin = subprocess.run(git[:3] + ["rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
            p = self.run_gen(PG_DEPLOY_PIN=pin)
            self.assertEqual((p.returncode, "root-schemas.json lacks B3's gst or gst_merged schema" in p.stderr),
                             (2, True), p.stderr)

    def test_the_scan_spares_this_shells_parents(self):
        script = self.dep / "3d-unfolding/genie/pg_generate.sh"
        e = {"PATH": f"/usr/bin:/bin:/usr/sbin:/sbin:{self.sysbin}", "HOME": str(self.tmp), "TMPDIR": str(self.W / "tmp"),
             "PG_DEPLOY_PIN": self.pin, "PG_STUB_LOG": str(self.log), "PG_STUB_BIN": str(self.bin),
             "PG_STUB_DEPLOY": str(self.dep), "PG_STUB_GST": str(self.gst_tpl), "PG_STUB_ROOT": str(self.root_tpl),
             }
        for fail, rc in ((None, 0), ("members-check", 1)):
            with self.subTest(fail=fail):
                for x in self.W.iterdir():                                  # a fresh W for each run
                    shutil.rmtree(x) if x.is_dir() else x.unlink() if x.name != "seeds.json" else None
                (self.W / "tmp").mkdir(mode=0o700)
                ev = dict(e, **({"PG_STUB_VERIFY_FAIL": fail} if fail else {}))
                p = subprocess.run(["bash", "-c", f'cd "{self.W}" && bash "{script}" --workdir "{self.W}" --seeds '
                                    f'"{self.W}/seeds.json"; echo "parent alive $?"'], cwd=self.tmp, env=ev,
                                   stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=120)
                self.assertIn(f"parent alive {rc}", p.stdout, p.stdout + p.stderr)   # its cwd is W: not killed,
                self.assertNotIn("outside this run", p.stdout)                      # and not a false STOP

    def test_a_process_outside_the_run_with_its_cwd_in_w_stops_and_lives(self):
        sib = subprocess.Popen(["sleep", "60"], cwd=self.W)                 # the parent's tee, say: not ours to kill
        self.addCleanup(lambda: (sib.kill(), sib.wait()))
        p = self.run_gen()
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("[pg] cleanup: 1 processes outside this run have a cwd in W (not killed)", p.stdout)
        self.assertIn("[pg] STOP: a process outlived its step before publication", p.stdout)
        self.assertIsNone(sib.poll())
        self.assertFalse((self.W / "out/PG-PUBLISH-SHA256SUMS").exists())

    def test_cores_off_and_the_final_snapshot_published(self):
        import resource
        old = resource.getrlimit(resource.RLIMIT_CORE)                      # a soft limit above 0, as a node may set
        resource.setrlimit(resource.RLIMIT_CORE, (min(1 << 20, old[1]) if old[1] >= 0 else 1 << 20, old[1]))
        self.addCleanup(resource.setrlimit, resource.RLIMIT_CORE, old)
        p = self.run_gen()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        cores = [ln for ln in self.log.read_text().splitlines() if ln.startswith("core ")]
        self.assertEqual(sorted(set(cores)), ["core 0"])                     # Q2: every task, no core
        self.assertEqual(len(cores), 14)
        listed = [ln.split("  ", 1)[1] for ln in (self.W / "out/PG-PUBLISH-SHA256SUMS").read_text().splitlines()]
        self.assertIn("run/deploy-status-after.txt", listed)                # B14: scanned and listed
        self.assertIn("out/pin_hash_start.json", listed)
        self.assertIn("out/pin_hash_end.json", listed)

    def test_a_write_into_the_deploy_during_publication_stops(self):
        p = self.run_gen(PG_STUB_DIRTY_AT="l")                               # the publish step's environment
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("[pg] STOP: the deploy changed (publish)", p.stdout)
        self.assertFalse((self.W / "out/PG-PUBLISH-SHA256SUMS").exists())

    def test_an_orphan_that_left_w_is_killed_by_its_group(self):
        import time
        pidf = self.tmp / "orphan.pid"
        p = self.run_gen(PG_STUB_ORPHAN_CD=str(seeds()["tunes"][0]["task_seeds"][2]), PG_STUB_ORPHAN_PID=str(pidf))
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertLess(p.stdout.index("outlived their trees"), p.stdout.index("the publish set and its leak scan: pass"))
        self.assertRegex(p.stdout, r"\[pg\] cleanup: the survivors ended after [0-9]+ polls \(0\.5 s each, 30 s at most\)")
        pid = int(pidf.read_text())
        time.sleep(0.5)
        alive = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True).stdout.strip()
        self.assertTrue(alive in ("",) or alive.startswith("Z"), f"orphan {pid} (cwd /) still running: {alive}")

    def test_a_failed_rename_stops_without_a_path(self):
        seed = seeds()["tunes"][0]["task_seeds"][3]
        self.addCleanup(lambda: [os.chmod(d, 0o755) for d in self.W.rglob("t*") if d.is_dir()])
        p = self.run_gen(PG_STUB_LOCK_SEED=str(seed))
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        out = p.stdout + p.stderr
        self.assertIn("[pg] STOP: seedfree: a seed-named file could not be renamed", p.stdout)
        self.assertIn("[pg] STOP: seedfree could not rename every seed-named file", p.stdout)     # the trap's own
        self.assertNotIn(str(self.W), out)
        for t_ in seeds()["tunes"]:
            self.assertFalse(any(str(x) in out for x in t_["task_seeds"]))

    def test_an_orphaned_task_process_is_killed(self):
        import time
        pidf = self.tmp / "orphan.pid"
        p = self.run_gen(PG_STUB_ORPHAN=str(seeds()["tunes"][0]["task_seeds"][0]), PG_STUB_ORPHAN_PID=str(pidf))
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        pid = int(pidf.read_text())
        time.sleep(0.5)
        alive = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True).stdout.strip()
        self.assertTrue(alive in ("",) or alive.startswith("Z"), f"orphan {pid} still running: {alive}")

    def test_alive_does_not_count_a_zombie(self):
        # pg_generate.sh's own alive(), on a real zombie: a parent that never waits on its exited child. (In the run
        # itself bash reaps its jobs and init its orphans, so the guard is exercised here, directly.)
        import time
        src = (GENIE / "pg_generate.sh").read_text()
        fn = src[src.index("alive() {"):src.index("\n}\n", src.index("alive() {")) + 3]
        p = subprocess.Popen([sys.executable, "-c", "import os, time\npid = os.fork()\nif pid == 0:\n    os._exit(0)\n"
                              "print(pid, flush=True)\ntime.sleep(20)"], stdout=subprocess.PIPE, text=True)
        self.addCleanup(p.kill)
        child = int(p.stdout.readline())
        time.sleep(0.5)
        st = subprocess.run(["ps", "-o", "stat=", "-p", str(child)], capture_output=True, text=True).stdout.strip()
        self.assertTrue(st.startswith("Z"), st)                               # a real zombie
        rc = subprocess.run(["bash", "-c", fn + f"\nalive {child}"]).returncode
        self.assertEqual(rc, 1)
        self.assertEqual(subprocess.run(["bash", "-c", fn + f"\nalive {p.pid}"]).returncode, 0)     # its live parent

    def test_an_untracked_file_in_the_deploy_refuses(self):
        (self.dep / "3d-unfolding/genie/sitecustomize.py").write_text("x")
        p = self.run_gen()
        self.assertEqual(p.returncode, 2)
        self.assertIn("the deploy is not the pinned commit, or is modified", p.stderr)

    def test_flux_check_failure_stops(self):
        p = self.run_gen(PG_STUB_FLUXCHECK_RC="1")
        self.assertEqual(p.returncode, 1)
        self.assertIn("[pg] STOP: the sampled-spectrum check (NOWIDTH)", p.stdout)

    def test_a_write_into_the_deploy_stops(self):
        p = self.run_gen(PG_STUB_WRITE_DEPLOY="1")
        self.assertEqual(p.returncode, 1)
        self.assertIn("[pg] STOP: the deploy changed (after)", p.stdout)

    def test_a_missing_inventory_file_stops(self):
        p = self.run_gen(PG_STUB_NO_META="1")
        self.assertEqual(p.returncode, 1)
        self.assertIn("[pg] STOP: the required inventory", p.stdout)
        self.assertIn("out/gen5d/genie_v3_g21_xsec5d.meta.json: 0 files, not 1",
                      (self.W / "out/logs/inventory.log").read_text())
        self.assertFalse((self.W / "out/PG-PUBLISH-SHA256SUMS").exists())       # a STOP after publish withdraws it
        self.assertFalse((self.W / "out/leak_scan.json").exists())

    def test_inventory_rules(self):
        req = pg_lib.inventory()
        pats = [r["pattern"] for r in req]
        self.assertEqual(len(pats), len(set(pats)))
        self.assertTrue(all(not p.startswith("/") and ".." not in p.split("/") and r["count"] >= 1
                            for p, r in zip(pats, req)))
        self.assertNotIn("gntp.ghep.root", " ".join(pats))
        self.assertIn({"pattern": "out/work/u0/t*/gevgen.log", "count": 7}, req)
        self.assertIn({"pattern": "out/gen5d/genie_v3_g21_xsec5d.npz", "count": 1}, req)
        rc, so, _ = quiet(pg_lib.main, ["inventory"])
        self.assertEqual((rc, json.loads(so)), (0, req))
        w = Path(tempfile.mkdtemp(prefix="pg-inv-"))
        self.addCleanup(shutil.rmtree, w, ignore_errors=True)
        for r in req:                                              # exactly the required files
            for k in range(r["count"]):
                q = w / r["pattern"].replace("t*", f"t{k}")
                q.parent.mkdir(parents=True, exist_ok=True)
                q.write_text("x")
        self.assertEqual(pg_lib.inventory_problems(str(w), req), [])
        (w / "out/work/u0/t7").mkdir()
        (w / "out/work/u0/t7/gevgen.log").write_text("x")          # one too many
        self.assertEqual(pg_lib.inventory_problems(str(w), req), ["out/work/u0/t*/gevgen.log: 8 files, not 7"])
        (w / "out/work/u0/t7/gevgen.log").unlink()
        (w / "PRODUCTS.json").unlink()
        (w / "PRODUCTS.json").symlink_to(w / "seeds.json")          # a link is not a file
        self.assertEqual(pg_lib.inventory_problems(str(w), req), ["PRODUCTS.json: 0 files, not 1"])

    def test_a_failed_strace_check_stops_before_any_step(self):
        p = self.run_gen(PG_STUB_VERIFY_FAIL="--self-test")
        self.assertEqual(p.returncode, 1)
        self.assertIn("[pg] STOP: strace", p.stdout)
        self.assertEqual([ln.split()[:2] for ln in self.log.read_text().splitlines()],
                         [["pg_verify", "tool-check"], ["pg_verify", "drain"]])          # then only the cleanup's scan

    def test_unfilled_pins_refuse(self):
        g = self.dep / "3d-unfolding/genie"
        (g / "pg_pins.json").write_text(json.dumps({"strace_path": "/usr/bin/strace", "strace_sha256": None,
                                                    "dbconfig_sha256": "f" * 64}))
        subprocess.run(["git", "-C", str(self.dep), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam", "p"],
                       check=True)
        pin = subprocess.run(["git", "-C", str(self.dep), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        self.refused(self.run_gen(PG_DEPLOY_PIN=pin))

    def test_a_failed_members_or_dbconfig_check_stops(self):
        for fail, msg in (("members-check", "slot 1's private product"), ("f" * 64, "slot 1's UPS database file"),
                          ("exe-check", "gevgen, gspl2root, awk and LD_LIBRARY_PATH")):
            with self.subTest(fail):
                for d in ("out", "run"):
                    shutil.rmtree(self.W / d, ignore_errors=True)
                p = self.run_gen(PG_STUB_VERIFY_FAIL=fail)
                self.assertEqual(p.returncode, 1)
                self.assertIn(f"[pg] STOP: {msg}", p.stdout)
                self.assertFalse([ln for ln in self.log.read_text().splitlines() if ln.startswith("run_gevgen_v3")])
                self.log.unlink()

    def test_a_program_that_does_not_resolve_stops(self):
        os.remove(self.bin / "gspl2root")
        p = self.run_gen()
        self.assertEqual(p.returncode, 1)
        self.assertIn("[pg] STOP: resolve gevgen and gspl2root (G21_11a_00_000)", p.stdout)
        self.assertFalse([ln for ln in self.log.read_text().splitlines() if ln.startswith(("run_gevgen_v3", "pg_verify exe"))])

    def test_a_failed_trace_check_stops(self):
        for fail, msg, gen in (("--role graphs", "trace check (graphs", False), ("--role reduce", "trace check (reduce", False),
                               ("--role coverage", "trace check (coverage", False), ("--role gevgen", "trace check (gevgen", True),
                               ("--role gntpc", "trace check (gntpc", True), ("coverage-log", "spline coverage", False),
                               ("reduce-check", "reduce completeness", False), ("argv-check", "the coverage argv", False),
                               ("messenger", "the coverage messenger", False)):
            with self.subTest(fail):
                for d in ("out", "run"):
                    shutil.rmtree(self.W / d, ignore_errors=True)
                p = self.run_gen(PG_STUB_VERIFY_FAIL=fail)
                self.assertEqual(p.returncode, 1, p.stdout)
                self.assertIn(f"[pg] STOP: {msg}", p.stdout)
                ran = [ln for ln in self.log.read_text().splitlines() if ln.startswith("run_gevgen_v3 genie")]
                self.assertEqual(bool(ran), gen)
                self.assertFalse((self.W / "PRODUCTS.json").exists())
                self.log.unlink()


class Replay(unittest.TestCase):
    """pg_replay.sh (B3's driver) against the same stubbed deploy (Generate's setUp, none of its tests)."""

    def setUp(self):
        Generate.setUp(self)
        src = (GENIE / "pg_replay.sh").read_text()
        self.assertEqual(src.count("PY=/usr/bin/python3.11"), 1)
        (self.dep / "3d-unfolding/genie/pg_replay.sh").write_text(src.replace("PY=/usr/bin/python3.11", f"PY={sys.executable}"))
        self.R = self.tmp / "R"
        self.R.mkdir()

    def run_replay(self, **env):
        e = {"PATH": f"/usr/bin:/bin:/usr/sbin:/sbin:{self.sysbin}", "HOME": str(self.tmp), "TMPDIR": str(self.W / "tmp"),
             "PG_STUB_LOG": str(self.log), "PG_STUB_BIN": str(self.bin), "PG_STUB_DEPLOY": str(self.dep),
             "PG_STUB_GST": str(self.gst_tpl), "PG_STUB_ROOT": str(self.root_tpl), "PG_STUB_GHEP": str(self.ghep_tpl)}
        e.update(env)
        return subprocess.run(["bash", str(self.dep / "3d-unfolding/genie/pg_replay.sh"), "--workdir", str(self.R)],
                              cwd=self.R, env=e, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    def test_the_replay(self):
        import resource
        old = resource.getrlimit(resource.RLIMIT_CORE)
        resource.setrlimit(resource.RLIMIT_CORE, (min(1 << 20, old[1]) if old[1] >= 0 else 1 << 20, old[1]))
        self.addCleanup(resource.setrlimit, resource.RLIMIT_CORE, old)
        p = self.run_replay()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        log = self.log.read_text().splitlines()
        self.assertTrue(log[0].startswith("pg_verify tool-check") and "--self-test" in log[0])
        gen = [ln.split() for ln in log if ln.startswith("run_gevgen_v3 genie")]
        self.assertEqual(len(gen), 1)
        self.assertEqual(gen[0][2:6], ["G21_11a_00_000", str(self.R / "splines"), "100", "123456789"])
        tenv = [ln for ln in log if ln.startswith("trace-env ")]
        self.assertEqual(len(tenv), 6)                        # reduce x2, graphs, coverage x2, genie: all on fd 9
        self.assertTrue(all(ln.endswith(" fd=9 dir=set") for ln in tenv))
        roles = [ln.split("--role ")[1].split()[0] for ln in log if ln.startswith("pg_verify trace-check")]
        self.assertEqual(sorted(roles), ["coverage", "coverage", "gevgen", "gntpc", "graphs", "reduce", "reduce"])
        rc_ = next(ln.split() for ln in log if ln.startswith("pg_verify revision-compare"))
        self.assertEqual(sum(x == "--trace-check" for x in rc_), 7)                # every file the replay read
        order = [ln.split()[1] for ln in log if ln.startswith("run_gevgen_v3 ")]
        self.assertLess(order.index("coverage"), order.index("genie"))          # coverage before the gevgen
        s2 = [ln for ln in log if ln.startswith("pg_verify trace-check") and "--tune G18_02a_00_000" in ln]
        x2 = "/cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/v3_04_00/NULL/G1802a00000-k250-e1000/data"
        self.assertEqual(len(s2), 2)                                            # slot 2's reduce and coverage
        self.assertIn(f"--spline {x2}/gxspl-NUsmall.xml --spline-sha256 {'c' * 64} ", s2[0])
        for ln in s2:
            self.assertIn(f"--pin {x2}/gxspl-NUsmall.xml={'c' * 64} --pin {x2}/README={'d' * 64} ", ln)
            self.assertIn(f"--xsec-data {x2} ", ln)
        self.assertTrue(any(ln.startswith("pg_verify tool-check --fd 9 ") for ln in log))
        self.assertTrue(any(ln.startswith("pg_verify host-check --fd 9 ") for ln in log))
        cov = [ln for ln in log if ln.startswith("pg_verify trace-check") and "--role coverage" in ln]
        self.assertTrue(cov and all(f"--messenger {self.R}/Messenger_pg.xml" in ln for ln in cov))   # pinned in the check
        self.assertTrue(all("--script" in ln and "--reduced" in ln for ln in log if ln.startswith("pg_verify coverage-log")))
        rec = json.loads((self.R / "replay.json").read_text())
        self.assertTrue(rec["pass"])
        self.assertEqual(len(rec["checks"]), 24)
        self.assertEqual(rec["schema"], "covfix-pg-replay-run/4")
        self.assertEqual(rec["gst_merged_schema"], pg_lib.root_schema(str(self.gst_tpl)))   # hadd's (B6)
        gone = json.loads((self.R / "deleted.json").read_text())
        self.assertEqual(sorted(gone["merged"]), ["genie_v3_g21_ALL.gst.root"])
        self.assertFalse(list((self.R / "gst").iterdir()))
        dec = gone["t0"]["genie_v3.gst.root"]["decoded"]
        self.assertEqual((dec["holds_seed"], dec["name_holds_seed"]), (False, False))
        cov = gone["coverage_slot1"]["gntp.ghep.root"]["decoded"]                # gntp.123456789.ghep.root
        self.assertEqual((cov["holds_seed"], cov["name_holds_seed"]), (True, True))         # K6: the control found it
        self.assertTrue({"inflated", "int32-object"} & set(cov["hits"]), cov["hits"])   # an int64 run number holds the int32
        self.assertGreater(cov["bytes_inflated"], 0)                                     # R1: the keys after the header
        self.assertEqual(cov["seed_objects"], [{"class": "genie::NtpMCTreeHeader", "inflated": False, "kind": "int32-object"}])
        self.assertEqual([ln for ln in log if ln.startswith("core ")], ["core 0"])        # Q2
        gntpc = next(ln for ln in log if ln.startswith("pg_verify trace-check") and "--role gntpc" in ln).split()
        self.assertEqual(gntpc[gntpc.index("--ghep-from-trace") + 1], str(self.R / "work/t0/gevgen.trace"))
        self.assertEqual(sum(ln.startswith("pg_verify pin-hash") for ln in log), 2)          # Q1, both ends
        self.assertEqual(rec["gst_schema"], pg_lib.root_schema(str(self.gst_tpl)))        # the schema every gst must match
        self.assertEqual(sorted(rec["revision"]), ["end", "start"])
        self.assertEqual(rec["execs"]["trace_check_gntpc.json"][0]["path"], "/b/gntpc")
        self.assertEqual((len(rec["real_shapes"]), len(rec["host"])), (4, 3))
        self.assertEqual(len(rec["spline_opened"]), 6)
        gone = json.loads((self.R / "deleted.json").read_text())
        self.assertEqual(sorted(gone), ["coverage_slot1", "coverage_slot2", "merged", "t0"])
        self.assertEqual(sorted(gone["t0"]), ["genie_v3.gst.root", "gevgen.status", "input-flux.root"])
        self.assertEqual(sorted(gone["coverage_slot1"]), ["gevgen.log", "gevgen.status", "gntp.ghep.root", "input-flux.root"])
        for d, ends in (("work/t0", (".root", ".status")), ("coverage/G21_11a_00_000", (".root", ".status", ".log")),
                        ("coverage/G18_02a_00_000", (".root", ".status", ".log"))):    # t0's logs stay: a public seed
            self.assertEqual([q.name for q in (self.R / d).iterdir() if q.name.endswith(ends)], [])
        self.assertNotIn("123456789", json.dumps(gone))
        g = gone["t0"]["genie_v3.gst.root"]                                    # C4's control: the gst decoded too
        self.assertEqual((g["decoded"]["holds_seed"], g["schema"]), (False, rec["gst_schema"]))

    def install(self, name):
        import importlib.util
        spec = importlib.util.spec_from_file_location(name.replace("-", "_"), REPO / f"docs/orchestration/state/2d-closeout/covfix-20261122/pg/install/{name}.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_the_drivers_records_pass_both_validators(self):
        for name, tpl, inflated in (("the header stored", self.ghep_tpl, False), ("the header compressed", self.ghep_tpl_z, True)):
            with self.subTest(name):                                         # R1: GENIE's header, either way
                shutil.rmtree(self.R)
                self.R.mkdir()
                p = self.run_replay(PG_STUB_GHEP=str(tpl))
                self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
                r = json.loads((self.R / "replay.json").read_text())
                d = json.loads((self.R / "deleted.json").read_text())
                node, launcher = self.install("pg-replay-g2111a"), self.install("pg-node-launch")
                self.assertEqual(node.deleted_problems(d, r), [])            # K2: t0 has no GHEP: the wrapper removed it
                self.assertEqual(launcher._deleted_problems(d, r), [])
                self.assertEqual(list((self.R / "work/t0").glob("gntp.*.ghep.root")), [])
                self.assertIn("[replay] t0's GHEP removed by the wrapper: pass", p.stdout)
                self.assertEqual({x["inflated"] for x in d["coverage_slot2"]["gntp.ghep.root"]["decoded"]["seed_objects"]},
                                 {inflated})

    def test_an_unlistable_t0_stops(self):
        t0 = self.R / "work/t0"
        self.addCleanup(lambda: t0.exists() and os.chmod(t0, 0o755))
        p = self.run_replay(PG_STUB_UNLISTABLE="1")                          # codex 10: an ls error is no absence
        self.assertEqual(p.returncode, 1, p.stdout)
        self.assertIn("[replay] STOP: t0's directory could not be listed", p.stdout)

    def test_a_control_without_the_seed_stops_at_both_validators(self):
        p = self.run_replay(PG_STUB_GHEP=str(self.root_tpl))                 # a GHEP whose bytes lack the seed
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        r = json.loads((self.R / "replay.json").read_text())
        d = json.loads((self.R / "deleted.json").read_text())
        for problems in (self.install("pg-replay-g2111a").deleted_problems(d, r),
                         self.install("pg-node-launch")._deleted_problems(d, r)):
            self.assertTrue(problems and all("control" in x for x in problems), problems)

    def test_a_left_ghep_in_t0_stops(self):
        p = self.run_replay(PG_STUB_KEEP_GHEP="1")
        self.assertEqual(p.returncode, 1, p.stdout)
        self.assertIn("[replay] STOP: the wrapper left t0's GHEP", p.stdout)

    def test_a_prior_record_of_the_wrong_shape(self):
        for bad in ("[]", '{"t0": null}'):
            with self.subTest(bad):
                shutil.rmtree(self.R)
                self.R.mkdir()
                p = self.run_replay(PG_STUB_PRIOR=bad)
                self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
                gone = json.loads((self.R / "deleted.json").read_text())
                self.assertEqual(gone["_prior"], "unreadable")
                self.assertIn("genie_v3.gst.root", gone["t0"])
                self.assertFalse((self.R / "work/t0/genie_v3.gst.root").exists())

    def test_an_unreadable_event_file_is_still_deleted(self):
        p = self.run_replay(PG_STUB_UNREADABLE="1")
        self.assertEqual(p.returncode, 1, p.stdout)
        self.assertIn("[replay] STOP: deleting the event and status files", p.stdout)
        self.assertFalse((self.R / "work/t0/genie_v3.gst.root").exists())
        self.assertEqual(json.loads((self.R / "deleted.json").read_text())["t0"]["genie_v3.gst.root"],
                         {"error": "unreadable: PermissionError"})

    def test_a_broken_record_or_an_unexpected_error_still_deletes(self):
        import struct
        p = self.run_replay(PG_STUB_BAD_RECORD="1")
        self.assertEqual(p.returncode, 0, p.stdout)
        gone = json.loads((self.R / "deleted.json").read_text())
        self.assertEqual(gone["_prior"], "unreadable")                        # kept, and the node refuses it
        self.assertIn("genie_v3.gst.root", gone["t0"])
        shutil.rmtree(self.R)
        self.R.mkdir()
        bad = self.tmp / "bad.gst.root"                                       # its last key's names run off the file
        body = struct.pack(">ihiIhh", 18, 4, 0, 0, 18, 1)
        bad.write_bytes(b"root" + struct.pack(">iii", 62206, 100, 100 + len(body)) + b"\0" * 84 + body)
        p = self.run_replay(PG_STUB_GST=str(bad))
        self.assertEqual(p.returncode, 1, p.stdout)
        self.assertIn("[replay] STOP: deleting the event and status files", p.stdout)
        gone = json.loads((self.R / "deleted.json").read_text())
        self.assertEqual(gone["t0"]["genie_v3.gst.root"]["decoded"], {"error": "root-key"})   # named, not a crash
        self.assertFalse((self.R / "work/t0/genie_v3.gst.root").exists())
        self.assertFalse((self.R / "gst/genie_v3_g21_ALL.gst.root").exists())

    def test_a_stop_still_deletes_the_events(self):
        p = self.run_replay(PG_STUB_VERIFY_FAIL="--role gntpc")           # after the gevgen, before the record
        self.assertEqual(p.returncode, 1, p.stdout)
        self.assertIn("[replay] STOP: trace check (gntpc)", p.stdout)
        gone = json.loads((self.R / "deleted.json").read_text())        # the trap ran on the STOP
        self.assertIn("genie_v3.gst.root", gone["t0"])
        self.assertEqual([q.name for q in (self.R / "work/t0").iterdir() if q.name.endswith((".root", ".status"))], [])

    def test_stops(self):
        for fail, msg in (("--self-test", "strace"), ("members-check", "slot 1's private product"),
                          ("--role reduce", "trace check (reduce)"), ("--role graphs", "trace check (graphs)"),
                          ("--role gevgen", "trace check (gevgen)")):
            with self.subTest(fail):
                shutil.rmtree(self.R)
                self.R.mkdir()
                if self.log.exists():
                    self.log.unlink()
                p = self.run_replay(PG_STUB_VERIFY_FAIL=fail)
                self.assertEqual(p.returncode, 1, p.stdout)
                self.assertIn(f"[replay] STOP: {msg}", p.stdout)
                self.assertFalse((self.R / "replay.json").exists())

    def test_the_environment_rules(self):
        for mode, rc in (("tolerated", 0), ("conda", 0), ("extra", 1), ("clobber", 1), ("missing-other", 1)):
            with self.subTest(mode):
                shutil.rmtree(self.R)
                self.R.mkdir()
                if self.log.exists():
                    self.log.unlink()
                p = self.run_replay(PG_STUB_ENV=mode)
                self.assertEqual(p.returncode, rc, p.stdout + p.stderr)
                if rc == 0:
                    chk = json.loads((self.R / "env_check_a.json").read_text())
                    self.assertEqual((len(chk["tolerated"]), chk["other"]), (2, []))
                    tmp = {ln.split(" ", 1)[1] for ln in self.log.read_text().splitlines() if ln.startswith("TMPDIR ")}
                    self.assertEqual(tmp, {str(self.W / "tmp")})             # restored after the activation
                else:
                    self.assertIn("[replay] STOP: flux file or spline check", p.stdout)

    def test_a_missing_interpreter_refuses(self):
        for f in ("pg_replay.sh", "pg_generate.sh"):
            with self.subTest(f):
                q = self.dep / "3d-unfolding/genie" / f
                q.write_text(q.read_text().replace(f"PY={sys.executable}", "PY=/nonexistent/python3.11"))
                if f == "pg_replay.sh":
                    p = self.run_replay()
                else:
                    p = subprocess.run(["bash", str(q), "--workdir", str(self.W), "--seeds", str(self.W / "seeds.json")],
                                       cwd=self.W, env={"PATH": "/usr/bin:/bin", "TMPDIR": str(self.W / "tmp"),
                                                        "PG_DEPLOY_PIN": "x"}, capture_output=True, text=True)
                self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
                self.assertIn("/nonexistent/python3.11 is missing", p.stderr)

    def test_no_driver_variable_is_one_conda_sets(self):
        import re
        for f in ("pg_replay.sh", "pg_generate.sh"):
            src = (GENIE / f).read_text()
            for v in ("HOST", "CC", "BUILD", "CFLAGS", "LDFLAGS", "CXX", "AR", "LD"):
                self.assertFalse(re.search(rf"(\$\{{?{v}\b|^\s*{v}=)", src, re.M), (f, v))

    def test_a_replay_record_that_fails_stops(self):
        for k in ("PG_STUB_NO_SPLINE", "PG_STUB_THREE_SHAPES", "PG_STUB_TWO_HOST"):   # each exits 0; the record falls short
            with self.subTest(k):
                shutil.rmtree(self.R)
                self.R.mkdir()
                p = self.run_replay(**{k: "1"})
                self.assertEqual(p.returncode, 1, p.stdout)
                self.assertIn("[replay] STOP: the replay rc=1", p.stdout)
        empty = self.tmp / "empty.gst.root"
        empty.write_bytes(root_file([]))                                     # decodes, but its schema has no keys
        shutil.rmtree(self.R)
        self.R.mkdir()
        p = self.run_replay(PG_STUB_GST=str(empty))
        self.assertEqual(p.returncode, 1, p.stdout)
        self.assertIn("[replay] STOP: the replay rc=1", p.stdout)
        self.assertEqual(json.loads((self.R / "replay.json").read_text())["gst_schema"], {"keys": [], "streamer_sha256": None})

    def test_shape_and_slot2_failures_stop(self):
        for fail, msg in (("--role reduce --tune G18_02a_00_000", "trace check (slot 2's reduce)"),
                          ("shape-check", "the four real-shape"), ("host-check", "the three host checks"),
                          ("--role coverage --tune G21_11a", "trace check (coverage)"),
                          ("--role coverage --tune G18", "trace check (slot 2's coverage)"),
                          ("--role gntpc", "trace check (gntpc)"), ("coverage-log", "spline coverage (slot 1)"),
                          ("reduce-check", "reduce completeness"), ("argv-check", "the coverage argv"),
                          ("messenger", "the coverage messenger"), ("revision", "the CVMFS revision (start)")):
            with self.subTest(fail):
                shutil.rmtree(self.R)
                self.R.mkdir()
                p = self.run_replay(PG_STUB_VERIFY_FAIL=fail)
                self.assertEqual(p.returncode, 1, p.stdout)
                self.assertIn(f"[replay] STOP: {msg}", p.stdout)

    def test_loader_and_shell_hooks_refuse(self):
        for v in ("LD_PRELOAD", "LD_AUDIT", "BASH_ENV", "ENV"):
            with self.subTest(v):
                p = self.run_replay(**{v: "/x"})
                self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
                self.assertIn(f"refusing: {v} is set", p.stderr)
                p = Generate.run_gen(self, **{v: "/x"})
                self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
                self.assertIn(f"refusing: {v} is set", p.stderr)

    def test_refusals(self):
        (self.R / "x").write_text("x")
        self.assertEqual(self.run_replay().returncode, 2)                 # not empty
        p = subprocess.run(["bash", str(self.dep / "3d-unfolding/genie/pg_replay.sh"), "--workdir", "rel"],
                           cwd=self.tmp, capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main()


class Leak(unittest.TestCase):
    """pg_lib's leak scan: every outgoing file's path and bytes, for each seed's decimal and hex forms."""

    def setUp(self):
        self.tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix="pg-leak-", dir="/tmp")))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.seed = 1_234_567_890

    def test_planted_seeds_are_found(self):
        w = self.tmp
        (w / "out/traces").mkdir(parents=True)
        cases = {"out/x_1234567890.txt": b"clean",                                  # in a filename
                 "out/graphs_T.log": b"line one\n[v3] run 1234567890 done\n",         # in a log line
                 "out/traces/reduce_T.trace": b'7 openat(AT_FDCWD, "gntp.1234567890.ghep.root", O_RDONLY) = 3\n',
                 "out/hex_lower.bin": format(self.seed, "x").encode(), "out/hex_upper.bin": format(self.seed, "X").encode(),
                 "out/padded.txt": b"run 0001234567890", "out/clean.txt": b"nothing here 123456789"}
        for rel, data in cases.items():
            (w / rel).write_bytes(data)
        hits = pg_lib.leak_hits(str(w), sorted(cases), [self.seed])
        self.assertEqual(sorted(r for r, _ in hits if r), sorted(set(cases) - {"out/x_1234567890.txt", "out/clean.txt"}))
        self.assertEqual([where for r, where in hits if r is None], ["path"])        # the path hit is not repeated

    def test_a_seed_across_a_chunk_boundary(self):
        (self.tmp / "big.bin").write_bytes(b"x" * ((1 << 20) - 4) + b"1234567890")
        self.assertEqual(pg_lib.leak_hits(str(self.tmp), ["big.bin"], [self.seed]), [("big.bin", "bytes")])

    def test_seed_bearing_files_never_publish(self):
        for rel, sb in (("out/work/u0/t3/gevgen.trace", True), ("out/work/u1/t0/task.time", True),
                        ("out/logs/xargs.log", True), ("run/queue.txt", True), ("out/PG-SHA256SUMS", True),
                        ("out/work/u0/t3/trace_check.json", False), ("out/gen5d/genie_v3_g21_xsec5d.npz", False)):
            with self.subTest(rel):
                self.assertEqual(pg_lib.seed_bearing(rel), sb)


def _tstr(s):
    b = s.encode()
    return bytes([len(b)]) + b


def _key(cls, name, title, obj, codec=b"ZL", split=1):
    """One ROOT TKey record (key version 4): the object compressed in `split` blocks by codec, or stored if codec None."""
    import lzma
    import struct
    import zlib
    if codec is None:
        data = obj
    else:
        parts, step, data = [], max(1, -(-len(obj) // split)), b""
        for i in range(0, len(obj), step):
            chunk = obj[i:i + step]
            body = {b"XZ": lambda x: lzma.compress(x), b"L4": lambda x: b"\0" * 8 + zlib.compress(x, 9),
                    b"ZS": lambda x: __import__("zstandard").ZstdCompressor().compress(x)}.get(
                        codec, lambda x: zlib.compress(x, 9))(chunk)            # ZL, or any other tag's stand-in
            data += codec + b"\x01" + len(body).to_bytes(3, "little") + len(chunk).to_bytes(3, "little") + body
    names = _tstr(cls) + _tstr(name) + _tstr(title)
    keylen = 4 + 2 + 4 + 4 + 2 + 2 + 4 + 4 + len(names)
    head = struct.pack(">ihiIhhii", keylen + len(data), 4, len(obj), 0, keylen, 1, 0, 0) + names
    return head + data


def _basket(name, title, obj, codec=b"ZL", split=1):
    """A TBasket record as ROOT writes it: the basket's own fields (fVersion, fBufferSize, fNevBufSize, fNevBuf,
    fLast and a flag: 19 bytes) follow the key's strings, inside fKeylen."""
    import struct
    k = _key("TBasket", name, title, obj, codec=codec, split=split)
    nbytes, keylen = struct.unpack(">i", k[:4])[0], struct.unpack(">h", k[14:16])[0]
    ext = struct.pack(">hiiiib", 3, 32000, 8, 1, keylen + 19 + len(obj), 0)
    return struct.pack(">ihiIhh", nbytes + 19, 4, len(obj), 0, keylen + 19, 1) + k[18:keylen] + ext + k[keylen:]


HDR_DIRS = b"/cvmfs/larsoft.opensciencegrid.org/products/genie/v3_04_00/Linux64bit+3.10-2.17-e26-prof/config " * 3


def _ghep(seed, header_codec):
    """A GHEP as GENIE's NtpWriter writes it (NtpWriter.cxx:83-125): the file's own key, then NtpMCTreeHeader (its
    runnu and runseed, the seed as Long_t) first, then the configuration and environment folders, then the tree."""
    s8 = seed.to_bytes(8, "big")
    return root_file([_key("TFile", f"gntp.{seed}.ghep.root", "", b"top", codec=None),
                      _key("genie::NtpMCTreeHeader", "header", "GENIE output tree header",
                           b"\x00\x01fmt0cvs" + s8 + s8 + b"tune G21_11a_00_000 tuneDir " + HDR_DIRS, codec=header_codec),
                      _key("TFolder", "gconfig", "GENIE configs", b"cfg" * 60),
                      _key("TFolder", "genv", "GENIE user environment", b"env" * 60),
                      _basket("gmcrec", "gtree", b"evt" * 80),
                      _key("TTree", "gtree", "GENIE MC Truth TTree, Format: [NtpMCEventRecord]", b"tree" * 30)])


def root_file(keys, gap=False):
    """A ROOT file (version 62206, small): its header, then the keys from fBEGIN = 100, a free gap if asked, fEND."""
    import struct
    body = b"".join(keys)
    if gap:
        body = body[:0] + struct.pack(">i", -12) + b"\0" * 8 + body
    begin = 100
    end = begin + len(body)
    head = b"root" + struct.pack(">iii", 62206, begin, end)
    return head + b"\0" * (begin - len(head)) + body


class Leak4(unittest.TestCase):
    """Round 4 (C4, the director and cov2d): the export allowlist, the int64 and int32 forms, ROOT's compressed
    objects inflated, an unknown codec a STOP, the gst schema against B3's, and the sums file scanned."""
    SEED = 1_234_567_890

    def setUp(self):
        self.tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix="pg-leak4-", dir="/tmp")))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def put(self, rel, data):
        p = self.tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return rel

    def test_int64_stops_and_int32_is_only_counted(self):
        import struct
        a = self.put("out/a.bin", b"x" + struct.pack(">q", self.SEED) + b"y")
        b = self.put("out/b.bin", b"x" + struct.pack("<q", self.SEED))
        c = self.put("out/c.bin", b"x" + struct.pack(">i", self.SEED) + struct.pack("<i", self.SEED))
        hits, stats = pg_lib.leak_scan(str(self.tmp), [a, b, c], [self.SEED])
        self.assertEqual(sorted(r for r, _ in hits), [a, b])
        self.assertEqual(stats["int32_count"], 4)                   # each int64 form holds an int32 one too
        self.assertGreater(stats["int32_expected"], 0)

    def test_root_objects_are_inflated_and_scanned(self):
        seed = str(self.SEED).encode()
        for codec in (b"ZL", b"XZ", b"ZS"):
            with self.subTest(codec):
                f = self.put(f"out/{codec.decode()}.root", root_file([
                    _key("TFile", "x.root", "", b"top", codec=None),
                    _key("TBasket", "iev", "gst", b"pad" * 50 + seed + b"pad" * 50, codec=codec, split=3)], gap=True))
                hits, stats = pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])
                if codec != b"ZS":                                            # zstd keeps short literals verbatim
                    self.assertNotIn(seed, (self.tmp / f).read_bytes())        # only inflated bytes show it
                    self.assertEqual(hits, [(f, "inflated")])
                    self.assertEqual(stats["codecs"], {codec.decode(): 3})
                else:
                    self.assertEqual([r for r, _ in hits], [f])
                    self.assertEqual(len(list(pg_lib.root_keys(str(self.tmp / f)))[1][4]), 3)
        clean = self.put("out/clean.root", root_file([_key("TBasket", "iev", "gst", b"pad" * 100)]))
        self.assertEqual(pg_lib.leak_scan(str(self.tmp), [clean], [self.SEED])[0], [])

    def test_an_unknown_codec_or_a_broken_file_stops(self):
        for name, data, code in (
                ("codec", root_file([_key("TBasket", "iev", "gst", b"pad" * 100, codec=b"QQ")]), "root-codec"),
                ("truncated", root_file([_key("TBasket", "iev", "gst", b"pad" * 100)])[:-7], "root-"),
                ("header", b"notroot" + b"\0" * 100, "root-header")):
            with self.subTest(name):
                f = self.put(f"out/{name}.root", data)
                with self.assertRaises(pg_lib.Refusal) as cm:
                    pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])
                self.assertTrue(str(cm.exception).startswith(code), str(cm.exception))

    def test_a_missing_codec_module_stops(self):
        f = self.put("out/l4.root", root_file([_key("TBasket", "iev", "gst", b"pad" * 100, codec=b"L4")]))
        with mock.patch.dict(sys.modules, {"lz4": None, "lz4.block": None}), self.assertRaises(pg_lib.Refusal) as cm:
            pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])
        self.assertTrue(str(cm.exception).startswith("root-codec-unavailable"), str(cm.exception))

    def gst(self, branches=("iev", "neu"), streamer=b"streamers v1"):
        return root_file([_key("TFile", "genie_v3.gst.root", "", b"top", codec=None)]
                         + [_key("TBasket", b, "gst", b"pad" * 40) for b in branches]
                         + [_key("TTree", "gst", "GENIE Summary Event Tree", b"tree" * 30),
                            _key("TList", "StreamerInfo", "Doubly linked list", streamer)])

    def test_the_gst_schema(self):
        f = self.put("out/work/u0/t0/genie_v3.gst.root", self.gst())
        s = pg_lib.root_schema(str(self.tmp / f))
        self.assertIn(["TTree", "gst", "GENIE Summary Event Tree"], s["keys"])
        self.assertIn(["TBasket", "neu", "gst"], s["keys"])
        self.assertFalse([k for k in s["keys"] if k[0] == "TFile"])            # the file's own name is not schema
        g = self.put("out/gst/genie_v3_g21_ALL.gst.root", self.gst())
        self.assertEqual(pg_lib.root_schema(str(self.tmp / g)), s)
        self.assertEqual(pg_lib.schema_problems(str(self.tmp), [f, g], {"gst": s, "gst_merged": s}), [])
        self.assertEqual(pg_lib.schema_problems(str(self.tmp), [f, g], {"gst": s}),            # hadd's has its own
                         ["root-schema-unset: no gst_merged schema is recorded from B3"])
        for name, data in (("a new branch", self.gst(branches=("iev", "neu", "seed"))),
                           ("other streamers", self.gst(streamer=b"streamers v2"))):
            with self.subTest(name):
                self.put(f, data)
                self.assertEqual([p.split(":")[0] for p in pg_lib.schema_problems(str(self.tmp), [f], {"gst": s})],
                                 ["root-schema"])
        self.assertTrue(pg_lib.schema_problems(str(self.tmp), [f], {"gst": None})[0].startswith("root-schema-unset"))

    def workdir(self, base=BASE, extra=(), name="W"):
        w = self.tmp / name
        (w / "out/logs").mkdir(parents=True)
        (w / "seeds.json").write_text(json.dumps(seeds(base)))
        (w / "out/argv_check.json").write_text('{"pass": true}\n')
        (w / "out/logs/publish.log").write_text("log\n")                    # seed-bearing: kept in W, not listed
        for rel in extra:
            (w / rel).write_text("x\n")
        return w

    def publish(self, w, schema=None):
        sp = self.tmp / "schemas.json"
        sp.write_text(json.dumps(schema or {"gst": None}))
        return quiet(pg_lib.main, ["publish", "--workdir", str(w), "--seeds", str(w / "seeds.json"),
                                   "--schemas", str(sp)])

    def test_publish_lists_only_the_allowlist(self):
        w = self.workdir()
        rc, out, err = self.publish(w)
        self.assertEqual(rc, 0, err)
        listed = [ln.split("  ", 1)[1] for ln in (w / pg_lib.PUBLISH_SUMS).read_text().splitlines()]
        self.assertEqual(listed, ["out/argv_check.json", "out/leak_scan.json"])
        scan = json.loads((w / "out/leak_scan.json").read_text())
        self.assertEqual(scan["files"], 1)
        self.assertNotIn(str(BASE), (w / "out/leak_scan.json").read_text())
        w2 = self.workdir(extra=("out/extra.txt",), name="W2")
        rc, out, err = self.publish(w2)
        self.assertEqual(rc, 2)
        self.assertIn("unlisted", err)
        self.assertNotIn("extra.txt", err)                                   # a name in W could hold a seed
        self.assertFalse((w2 / pg_lib.PUBLISH_SUMS).exists())

    def test_an_allowlisted_file_holding_a_seed_is_refused(self):
        w = self.workdir()
        (w / "out/argv_check.json").write_text(json.dumps({"pass": True, "n": BASE + 3}) + "\n")
        rc, out, err = self.publish(w)
        self.assertEqual(rc, 2, err)
        self.assertIn("leak scan: 1 outgoing files hold a seed", err)
        self.assertNotIn(str(BASE + 3), err)
        self.assertFalse((w / pg_lib.PUBLISH_SUMS).exists() or (w / pg_lib.LEAK_SCAN).exists())

    def test_the_sums_file_is_scanned(self):
        import hashlib as h
        body = '{"pass": true}\n'
        d = h.sha256(body.encode()).hexdigest()
        base = next(int(d[i:i + 8], 16) for i in range(57) if 1_000_000_000 <= int(d[i:i + 8], 16) < 1_999_990_000)
        w = self.workdir(base=base)
        rc, out, err = self.publish(w)
        self.assertEqual(rc, 2, err)
        self.assertIn("the publish sums", err)
        self.assertFalse((w / pg_lib.PUBLISH_SUMS).exists())


class Leak5(Leak4):
    """Round 5 (B5-B7, the director's GO 2026-11-25), in ROOT's own record format: keys and free gaps tile
    [fBEGIN, fEND) exactly with nothing after it, a gap's old compressed record is read, each codec consumes exactly
    its block; the path and bytes are scanned apart; int32 STOPs outside basket payloads; gzip and zip are inflated."""

    def gap_file(self, old_record, end_extra=0):
        """A ROOT file whose first record was freed: ROOT overwrites only its length with the negative gap size."""
        import struct
        live = _key("TBasket", "iev", "gst", b"pad" * 40)
        gap = struct.pack(">i", -len(old_record)) + old_record[4:]
        body = gap + live
        begin = 100
        head = b"root" + struct.pack(">iii", 62206, begin, begin + len(body) + end_extra)
        return head + b"\0" * (begin - len(head)) + body

    def test_a_free_gap_keeps_and_is_read(self):
        seed = str(self.SEED).encode()
        f = self.put("out/g.root", self.gap_file(_key("TNamed", "old", "x", b"run " + seed * 3)))
        self.assertEqual(pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])[0], [(f, "inflated")])
        f = self.put("out/g2.root", self.gap_file(_key("TNamed", "old", "x", b"nothing here" * 3)))
        self.assertEqual(pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])[0], [])

    def test_the_records_tile_the_file(self):
        import struct
        ok = root_file([_key("TBasket", "iev", "gst", b"pad" * 40)])
        for name, data, code in (("bytes after fEND", ok + b"tail", "root-tail"),
                                 ("a gap past fEND", ok[:100] + struct.pack(">i", -10 ** 6) + ok[104:], "root-gap"),
                                 ("a key past fEND", ok[:100] + struct.pack(">i", len(ok)) + ok[104:], "root-key")):
            with self.subTest(name):
                f = self.put(f"out/{name.replace(' ', '_')}.root", data)
                with self.assertRaises(pg_lib.Refusal) as cm:
                    pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])
                self.assertTrue(str(cm.exception).startswith(code), str(cm.exception))

    def test_a_block_is_exactly_one_stream(self):
        import struct
        import zlib
        obj = b"pad" * 40
        z = zlib.compress(obj, 9) + b"junk"                                  # a seed could ride after the stream
        data = b"ZL\x08" + len(z).to_bytes(3, "little") + len(obj).to_bytes(3, "little") + z
        names = _tstr("TBasket") + _tstr("iev") + _tstr("gst")
        keylen = 26 + len(names)
        key = struct.pack(">ihiIhhii", keylen + len(data), 4, len(obj), 0, keylen, 1, 0, 0) + names + data
        f = self.put("out/junk.root", root_file([key]))
        with self.assertRaises(pg_lib.Refusal) as cm:
            pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])
        self.assertTrue(str(cm.exception).startswith("root-block"), str(cm.exception))

    def test_int32_stops_outside_basket_payloads(self):
        import struct
        i32 = struct.pack(">i", self.SEED)
        small = b"\0\1" + i32 + b"\0" * 20                                    # ROOT stores what does not compress
        for codec, obj in ((None, small), (b"ZL", small * 8)):
            with self.subTest(codec=codec):
                f = self.put("out/obj.root", root_file([_key("TParameter<int>", "run", "x", obj, codec=codec)]))
                self.assertEqual(pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])[0], [(f, "int32-object")])
        f = self.put("out/bsk.root", root_file([_key("TBasket", "E", "gst", b"\x11" * 30 + i32 + b"\x11" * 30)]))   # not an int64
        hits, stats = pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])
        self.assertEqual(hits, [])                                            # a float32 there is only counted
        self.assertGreaterEqual(stats["int32_count"], 1)

    def test_the_path_and_the_bytes_are_scanned_apart(self):
        f = self.put(f"out/gntp.{self.SEED}.ghep.root", root_file([_key("TNamed", "x", "y", b"run %d " % self.SEED * 20)]))
        hits, _ = pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])
        self.assertEqual(hits, [(None, "path"), (f, "inflated")])
        g = self.put(f"out/gntp.{self.SEED}.x.root", root_file([_key("TNamed", "x", "y", b"nothing")]))
        self.assertEqual(pg_lib.leak_scan(str(self.tmp), [g], [self.SEED])[0], [(None, "path")])

    def test_gzip_and_zip_are_inflated_and_other_containers_stop(self):
        import bz2
        import gzip
        import io
        import numpy as np
        f = self.put("out/splines/G21_11a_00_000_CH.xml.gz", gzip.compress(b"<x>%d</x>" % self.SEED))
        self.assertEqual(pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])[0], [(f, "inflated")])
        b = io.BytesIO()
        np.savez_compressed(b, run=np.array([self.SEED], dtype=">i8"))      # a packed int64, deflated
        f = self.put("out/gen5d/genie_v3_g21_xsec5d.npz", b.getvalue())
        self.assertEqual(pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])[0], [(f, "inflated")])
        b = io.BytesIO()
        np.savez(b, x=np.zeros(4))                                          # gen5d_v3's own np.savez: stored
        f = self.put("out/gen5d/clean.npz", b.getvalue())
        self.assertEqual(pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])[0], [])
        f = self.put("out/x.json", bz2.compress(b"{}"))
        with self.assertRaises(pg_lib.Refusal) as cm:
            pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])
        self.assertTrue(str(cm.exception).startswith("container-unread"))

    def test_hadds_output_is_the_merged_kind(self):
        src = (GENIE / "pg_generate.sh").read_text()
        self.assertIn('hadd "$O/gst/${N}_ALL.gst.root"', src)                 # the name pg_generate gives hadd's output
        import fnmatch
        for n in ("genie_v3_g21", "genie_v3_g18_02a"):
            self.assertTrue(fnmatch.fnmatchcase(f"out/gst/{n}_ALL.gst.root", "out/gst/*_ALL.gst.root"))


class Leak6(Leak5):
    """Round 5's confirm read (the director's GO): a key's blocks use all of its bytes; a freed record kept in a gap
    is read as strictly as a live one, with its class; a codec missing for a gap's block is a STOP; the schema is the
    live keys'; B3's control is decoded even when the raw bytes already hit (K3, K4, K6)."""

    def test_a_keys_bytes_after_its_blocks_stop(self):
        import struct
        import zlib
        key = _key("TNamed", "x", "y", b"pad" * 40)
        z = zlib.compress(b"run %d" % self.SEED, 9)
        extra = b"ZL\x08" + len(z).to_bytes(3, "little") + len(b"run %d" % self.SEED).to_bytes(3, "little") + z
        key = struct.pack(">i", len(key) + len(extra)) + key[4:] + extra   # a block past the object's size
        f = self.put("out/extra.root", root_file([key]))
        with self.assertRaises(pg_lib.Refusal) as cm:
            pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])
        self.assertTrue(str(cm.exception).startswith("root-block"), str(cm.exception))

    def test_a_freed_record_is_read_strictly(self):
        old = bytearray(_key("TNamed", "old", "x", b"run " * 30))
        old[-3] ^= 0xFF                                                     # its compressed stream broken
        f = self.put("out/bad-gap.root", self.gap_file(bytes(old)))
        with self.assertRaises(pg_lib.Refusal) as cm:
            pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])
        self.assertTrue(str(cm.exception).startswith("root-block"), str(cm.exception))

    def test_a_missing_codec_in_a_gap_stops(self):
        import struct
        from unittest import mock
        block = b"L4\x01" + (20).to_bytes(3, "little") + (40).to_bytes(3, "little") + b"\0" * 20
        for name, gap in (("a freed record", self.gap_file(_key("TNamed", "old", "x", b"run " * 30, codec=b"L4"))),
                          ("bytes that are no record", None)):
            with self.subTest(name):
                if gap is None:
                    raw = b"\xff" * 20 + block
                    live = _key("TBasket", "iev", "gst", b"pad" * 40)
                    body = struct.pack(">i", -(4 + len(raw))) + raw + live
                    gap = b"root" + struct.pack(">iii", 62206, 100, 100 + len(body)) + b"\0" * 84 + body
                f = self.put("out/l4-gap.root", gap)
                with mock.patch.dict(sys.modules, {"lz4": None, "lz4.block": None}):
                    with self.assertRaises(pg_lib.Refusal) as cm:
                        pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])
                self.assertTrue(str(cm.exception).startswith("root-codec-unavailable"), str(cm.exception))

    def test_a_freed_basket_keeps_its_class(self):
        import struct
        i32 = struct.pack(">i", self.SEED)
        f = self.put("out/old-basket.root", self.gap_file(_key("TBasket", "E", "gst", b"\x11" * 30 + i32 + b"\x11" * 30)))
        hits, stats = pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])
        self.assertEqual(hits, [])                                          # a basket's payload: only counted
        self.assertGreaterEqual(stats["int32_count"], 1)

    def test_the_schema_is_the_live_keys(self):
        live = root_file([_key("TBasket", "iev", "gst", b"pad" * 40)])
        freed = self.gap_file(_key("TList", "StreamerInfo", "x", b"si" * 40))
        self.assertEqual(pg_lib.root_schema(str(self.tmp / self.put("out/a.root", live))),
                         pg_lib.root_schema(str(self.tmp / self.put("out/b.root", freed))))

    def test_the_control_is_decoded_after_a_raw_hit(self):
        f = self.put(f"out/gntp.{self.SEED}.ghep.root",
                     root_file([_key("TFile", f"gntp.{self.SEED}.ghep.root", "", b"top", codec=None),
                                _key("TTree", "gtree", "GENIE", b"runnu %d " % self.SEED * 20)]))
        hits, st = pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])
        self.assertEqual((hits, st["bytes_inflated"]), ([(None, "path"), (f, "bytes")], 0))   # production: raw STOP
        hits, st = pg_lib.leak_scan(str(self.tmp), [f], [self.SEED], decode_all=True)
        self.assertEqual(st["hits"], ["bytes", "inflated", "path"])
        self.assertGreater(st["bytes_inflated"], 0)


class Leak7(Leak6):
    """Round 6's confirm read (the director's ruling, 2026-11-26): B3's control scans every key and records each seed
    object's class and whether it was inflated (R1); a freed TBasket, its fKeylen holding the basket's fields, keeps
    its class (R3); a gap candidate whose method byte is not ROOT's is no header (R4)."""

    def test_a_stored_header_written_first(self):
        f = self.put("out/hdr.root", root_file([
            _key("genie::NtpMCTreeHeader", "header", "h", b"fmt" + self.SEED.to_bytes(8, "big") * 2, codec=None),
            _key("TFolder", "gconfig", "c", b"cfg" * 60)]))
        hits, st = pg_lib.leak_scan(str(self.tmp), [f], [self.SEED], decode_all=True)
        self.assertEqual(hits, [(f, "bytes")])                              # its int64 run number, raw
        self.assertGreater(st["bytes_inflated"], 0)                         # the keys after the header were inflated
        self.assertEqual(st["seed_objects"], [{"class": "genie::NtpMCTreeHeader", "inflated": False, "kind": "int32-object"}])

    def test_a_compressed_header(self):
        f = self.put("out/hdr-z.root", root_file([
            _key("genie::NtpMCTreeHeader", "header", "h", b"fmt" + self.SEED.to_bytes(8, "big") * 2 + HDR_DIRS)]))
        hits, st = pg_lib.leak_scan(str(self.tmp), [f], [self.SEED], decode_all=True)
        self.assertEqual(st["seed_objects"], [{"class": "genie::NtpMCTreeHeader", "inflated": True, "kind": "int32-object"},
                                              {"class": "genie::NtpMCTreeHeader", "inflated": True, "kind": "inflated"}])   # the int64: both forms
        self.assertGreater(st["bytes_inflated"], 0)

    def test_the_control_scans_every_key(self):
        f = self.put("out/two.root", root_file([                            # both compressed: no raw hit
            _key("genie::NtpMCTreeHeader", "header", "h", b"fmt" + self.SEED.to_bytes(8, "big") + HDR_DIRS),
            _key("TNamed", "later", "x", b"run %d " % self.SEED * 20)]))
        hits, st = pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])          # production: the first hit STOPs
        self.assertEqual(hits, [(f, "int32-object")])
        self.assertEqual(st["seed_objects"], [{"class": "genie::NtpMCTreeHeader", "inflated": True, "kind": "int32-object"},
                                              {"class": "genie::NtpMCTreeHeader", "inflated": True, "kind": "inflated"}])
        hits, st = pg_lib.leak_scan(str(self.tmp), [f], [self.SEED], decode_all=True)
        self.assertEqual(st["seed_objects"], [{"class": "genie::NtpMCTreeHeader", "inflated": True, "kind": "int32-object"},
                                              {"class": "genie::NtpMCTreeHeader", "inflated": True, "kind": "inflated"},
                                              {"class": "TNamed", "inflated": True, "kind": "inflated"}])
        self.assertEqual(st["hits"], ["inflated", "int32-object"])

    def test_no_seed_no_seed_objects(self):
        f = self.put("out/clean.root", root_file([_basket("iev", "gst", b"pad" * 100)]))
        self.assertEqual(pg_lib.leak_scan(str(self.tmp), [f], [self.SEED], decode_all=True)[1]["seed_objects"], [])

    def test_a_freed_real_basket_keeps_its_class(self):
        import struct
        i32 = struct.pack(">i", self.SEED)
        for codec in (b"ZL", None):
            with self.subTest(codec=codec):
                f = self.put("out/old-real-basket.root",
                             self.gap_file(_basket("E", "gst", b"\x11" * 30 + i32 + b"\x11" * 30, codec=codec)))
                hits, stats = pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])
                self.assertEqual(hits, [])                                  # a basket's payload: only counted
                self.assertGreaterEqual(stats["int32_count"], 1)
        f = self.put("out/old-real-basket2.root", self.gap_file(_basket("E", "gst", b"run %d" % self.SEED * 3)))
        self.assertEqual(pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])[0], [(f, "inflated")])

    def test_a_live_real_basket(self):
        import struct
        f = self.put("out/real-basket.root", root_file([_basket("E", "gst", b"\x11" * 30 + struct.pack(">i", self.SEED))]))
        self.assertEqual(pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])[0], [])

    def test_a_gap_candidate_without_roots_method_byte(self):
        import struct
        from unittest import mock
        for method, stops in ((b"\x00", False), (b"\x01", True)):
            with self.subTest(method=method):
                raw = b"\xff" * 20 + b"ZS" + method + (20).to_bytes(3, "little") + (40).to_bytes(3, "little") + b"\0" * 20
                live = _key("TBasket", "iev", "gst", b"pad" * 40)
                body = struct.pack(">i", -(4 + len(raw))) + raw + live
                f = self.put("out/zs-gap.root", b"root" + struct.pack(">iii", 62206, 100, 100 + len(body)) + b"\0" * 84 + body)
                with mock.patch.dict(sys.modules, {"zstandard": None}):
                    if stops:
                        with self.assertRaises(pg_lib.Refusal) as cm:
                            pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])
                        self.assertTrue(str(cm.exception).startswith("root-codec-unavailable"), str(cm.exception))
                    else:
                        try:
                            got, err = pg_lib.leak_scan(str(self.tmp), [f], [self.SEED])[0], None
                        except pg_lib.Refusal as e:   # failed outside the handler: no chained import error
                            got, err = None, str(e)
                        if err is not None:
                            self.fail(f"a candidate without ROOT's method byte STOPped: {err}")
                        self.assertEqual(got, [])
