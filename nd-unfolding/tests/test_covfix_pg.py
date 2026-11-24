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
        checks = list(pg_lib.CHECKS) + [f"out/trace_check_{r}_{t}.json" for r in ("reduce", "graphs")
                                        for t in PG_TUNES] + [f"out/work/u{u}/t{k}/trace_check.json"
                                                              for u in (0, 1) for k in range(7)] + [
            f"out/exe_check_{t}.json" for t in PG_TUNES]
        for c in checks:
            (self.tmp / c).parent.mkdir(parents=True, exist_ok=True)
            (self.tmp / c).write_text('{"check": "x", "pass": true}\n' if "trace" not in c else '{\n "pass": true\n}\n')
        self.assertEqual(len(checks), 23)
        for broken in ('{"pass": false}\n', "not json\n"):          # a failed or unreadable check refuses
            (self.tmp / checks[5]).write_text(broken)
            self.assertEqual(quiet(pg_lib.main, argv)[0], 2)
        (self.tmp / checks[5]).unlink()                               # so does a missing one
        self.assertEqual(quiet(pg_lib.main, argv)[0], 2)
        (self.tmp / checks[5]).write_text('{\n "pass": true\n}\n')
        self.assertEqual(quiet(pg_lib.main, argv)[0], 0)
        rec = json.loads((self.tmp / "PRODUCTS.json").read_text())
        self.assertEqual(len(rec["checks"]), 23)
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
  graphs) echo g > "$4"; echo l > "${4%.root}.log"; echo t > "$PG_TRACE_DIR/graphs_$2.trace" ;;
  genie) mkdir -p "$6"; cd "$6"; echo "[v3] genie $2 N=$4 seed=$5"; echo l > gevgen.log; echo l > gntpc.log
         echo t > "$PG_TRACE_DIR/gevgen.trace"
         echo st > "genie-mcjob-$5.status"
         [ -n "$PG_STUB_SLOW" ] && sleep "$PG_STUB_SLOW"
         [ "$5" = "${PG_STUB_FAIL_SEED:-none}" ] && { echo ghep > "gntp.$5.ghep.root"; exit 1; }
         [ "$5" = "${PG_STUB_NOGST_SEED:-none}" ] || echo gst > genie_v3.gst.root
         echo f > input-flux.root ;;
esac
'''
STUB_V3 = r'''import sys, os, json
log = open(os.environ["PG_STUB_LOG"], "a"); log.write("gen5d_v3 " + " ".join(sys.argv[1:]) + "\n")
log.write("TMPDIR " + os.environ.get("TMPDIR", "") + "\n")
a = sys.argv[1:]
def arg(k): return a[a.index(k) + 1]
if a[0] == "make-flux": open(arg("--out"), "w").write("flux")
elif a[0] == "spline-check": open(arg("--out"), "w").write(json.dumps({"reduced": {"sha256": "r" * 64}}))
elif a[0] == "flux-check": sys.exit(int(os.environ.get("PG_STUB_FLUXCHECK_RC", "0")))
elif a[0] == "convert":
    open(arg("--out"), "w").write("npz")
    if not os.environ.get("PG_STUB_NO_META"): open(arg("--out")[:-4] + ".meta.json", "w").write("{}")
''' + "PG_SPLINE_PINS = " + repr({"G21_11a_00_000": ("a" * 64, "b" * 64, "v"), "G18_02a_00_000": ("c" * 64, "d" * 64, "v")}) + "\n"
STUB_VERIFY = r'''import sys, os
log = open(os.environ["PG_STUB_LOG"], "a"); log.write("pg_verify " + " ".join(sys.argv[1:]) + "\n")
a = sys.argv[1:]
if a[0] == "trace-check":
    opened = "false" if os.environ.get("PG_STUB_NO_SPLINE") else "true"
    open(a[a.index("--out") + 1], "w").write('{"pass": true, "initial_opened_spline": %s, "gated": []}' % opened)
fail = os.environ.get("PG_STUB_VERIFY_FAIL")
if fail and fail in " ".join(a):
    print('{"pass": false}'); sys.exit(1)
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
STUB_ENV = '''export PATH="$PG_STUB_BIN:$PATH"\nexport TMPDIR=/tmp/elsewhere   # as setup_salloc_env.sh does\n'''
PY311 = '''#!/bin/bash
[ "$1" = "-V" ] && { echo "Python 3.11.14"; exit 0; }
exec {py} "$@"
'''
HADD = '''#!/bin/bash
echo "hadd $*" >> "$PG_STUB_LOG"; o=$1; shift
case "$o" in *"${PG_STUB_HADD_FAIL:-none}"*) exit 1 ;; esac
case "$o" in *"${PG_STUB_HADD_SLOW:-none}"*) sleep 3; echo late > "$PG_STUB_MARK" ;; esac
cat "$@" > "$o"
'''
TIMEOUT = '''#!/bin/bash
echo "timeout $1" >> "$PG_STUB_LOG"; shift; exec "$@"
'''
TIMEV = '''#!/bin/bash
[ "$1" = "-v" ] && [ "$2" = "-o" ] || exit 9
o=$3; shift 3; "$@"; rc=$?; echo "Exit status: $rc" > "$o"; exit $rc
'''


class Generate(unittest.TestCase):
    """pg_generate.sh against a throwaway git deploy with stubbed pipeline steps."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="pg-gen-", dir="/tmp"))
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
        (g / "pg_generate.sh").write_text(src.replace("/usr/bin/time -v -o", f"{timev} -v -o"))
        shutil.copy(GENIE / "pg_lib.py", g / "pg_lib.py")
        (g / "pg_verify.py").write_text(STUB_VERIFY)
        rec = self.dep / "docs/orchestration/state/2d-closeout/covfix-20261122/pg/record"
        rec.mkdir(parents=True)
        (rec / "G2111a-members.json").write_text(json.dumps({"members": {"genie_xsec": {"type": "dir"}}}))
        for n in ("PG-RECORD.json", "genie-manifest.json"):
            (rec / n).write_text("{}")
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
        (self.sysbin / "timeout").write_text(TIMEOUT)
        (self.sysbin / "timeout").chmod(0o755)
        (self.sysbin / "strace").write_text(STRACE)
        (g / "pg_pins.json").write_text(json.dumps({"strace_path": str(self.sysbin / "strace"),
                                                    "strace_sha256": "e" * 64, "dbconfig_sha256": "f" * 64}))
        git = ["git", "-C", str(self.dep), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(git[:3] + ["init", "-q"], check=True)
        subprocess.run(git + ["add", "-A"], check=True)
        subprocess.run(git + ["commit", "-qm", "stub"], check=True)
        self.pin = subprocess.run(git[:3] + ["rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        self.W = self.tmp / "W"
        (self.W / "tmp").mkdir(parents=True)
        (self.W / "seeds.json").write_text(json.dumps(seeds()))
        self.log = self.tmp / "stub.log"

    def run_gen(self, cwd=None, args=None, **env):
        e = {"PATH": f"/usr/bin:/bin:/usr/sbin:/sbin:{self.sysbin}", "HOME": str(self.tmp), "TMPDIR": str(self.W / "tmp"),
             "PG_DEPLOY_PIN": self.pin, "PG_STUB_LOG": str(self.log), "PG_STUB_BIN": str(self.bin),
             "PG_STUB_DEPLOY": str(self.dep)}
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
        self.assertEqual(len(tenv), 2 + 2 + 14)                     # every pipeline step traced, on descriptor 9
        self.assertTrue(all(ln.endswith(" fd=9 dir=set") for ln in tenv), tenv)
        self.assertEqual(pg_lib.inventory_problems(str(self.W), pg_lib.inventory()), [])
        checks = json.loads((self.W / "PRODUCTS.json").read_text())["checks"]
        self.assertEqual(len(checks), 3 + 2 * (3 + 7))
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
        self.assertEqual([v[1] for v in ver[:5]], ["tool-check", "members-check", "tool-check", "exe-check", "exe-check"])
        for v in ver[3:5]:                                        # the programs as each tune's setup resolves them
            self.assertEqual([v[i + 1].rsplit("/", 1)[1] for i, x in enumerate(v) if x == "--path"], ["gevgen", "gspl2root"])
        self.assertLess(log.index(" ".join(ver[4])), next(i for i, ln in enumerate(log) if ln.startswith("run_gevgen_v3")))
        self.assertEqual(log.index(" ".join(ver[0])), 0)                           # strace is the first step
        self.assertIn("--self-test", ver[0])
        self.assertTrue(ver[0][ver[0].index("--path") + 1].endswith("/9"))       # checked through the descriptor
        self.assertEqual(ver[0][ver[0].index("--sha256") + 1], "e" * 64)
        self.assertEqual(ver[2][ver[2].index("--sha256") + 1], "f" * 64)
        tc = [v for v in ver if v[1] == "trace-check"]
        self.assertEqual(sorted(v[v.index("--role") + 1] for v in tc), ["gevgen"] * 14 + ["graphs"] * 2 + ["reduce"] * 2)
        first_gen = next(i for i, ln in enumerate(log) if ln.startswith("run_gevgen_v3 genie"))
        last_pre = max(i for i, ln in enumerate(log) if ln.startswith("pg_verify trace-check") and "--role graphs" in ln)
        self.assertLess(last_pre, first_gen)                                    # conditions 2 and 3 before generation
        red = next(v for v in tc if v[v.index("--role") + 1] == "reduce" and "G21_11a_00_000" in v)
        self.assertEqual(red[red.index("--spline-sha256") + 1], "a" * 64)
        self.assertIn("/covfix-pg/products/genie_xsec/", red[red.index("--spline") + 1])
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
        self.assertEqual(sorted(x.name for x in self.tmp.iterdir()), ["W", "bin", "deploy", "stub.log", "sysbin"])

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
             "PG_STUB_BIN": str(self.bin), "PG_STUB_DEPLOY": str(self.dep), "PG_STUB_SLOW": "2"}
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
        self.assertEqual([ln.split()[:2] for ln in self.log.read_text().splitlines()], [["pg_verify", "tool-check"]])

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
                          ("exe-check", "gevgen and gspl2root against the manifest")):
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
                               ("--role gevgen", "trace check (gevgen", True)):
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
        shutil.copy(GENIE / "pg_replay.sh", self.dep / "3d-unfolding/genie/pg_replay.sh")
        self.R = self.tmp / "R"
        self.R.mkdir()

    def run_replay(self, **env):
        e = {"PATH": f"/usr/bin:/bin:/usr/sbin:/sbin:{self.sysbin}", "HOME": str(self.tmp), "TMPDIR": str(self.W / "tmp"),
             "PG_STUB_LOG": str(self.log), "PG_STUB_BIN": str(self.bin), "PG_STUB_DEPLOY": str(self.dep)}
        e.update(env)
        return subprocess.run(["bash", str(self.dep / "3d-unfolding/genie/pg_replay.sh"), "--workdir", str(self.R)],
                              cwd=self.R, env=e, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    def test_the_replay(self):
        p = self.run_replay()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        log = self.log.read_text().splitlines()
        self.assertTrue(log[0].startswith("pg_verify tool-check") and "--self-test" in log[0])
        gen = [ln.split() for ln in log if ln.startswith("run_gevgen_v3 genie")]
        self.assertEqual(len(gen), 1)
        self.assertEqual(gen[0][2:6], ["G21_11a_00_000", str(self.R / "splines"), "100", "123456789"])
        tenv = [ln for ln in log if ln.startswith("trace-env ")]
        self.assertEqual(len(tenv), 3)
        self.assertTrue(all(ln.endswith(" fd=9 dir=set") for ln in tenv))
        self.assertEqual(sorted(ln.split("--role ")[1].split()[0] for ln in log if "trace-check" in ln),
                         ["gevgen", "graphs", "reduce"])
        rec = json.loads((self.R / "replay.json").read_text())
        self.assertTrue(rec["pass"])
        self.assertEqual(len(rec["checks"]), 7)
        gone = json.loads((self.R / "deleted.json").read_text())
        self.assertEqual(sorted(gone), ["genie_v3.gst.root", "gevgen.status", "input-flux.root"])
        self.assertEqual([q.name for q in (self.R / "work/t0").iterdir() if q.name.endswith((".root", ".status"))], [])
        self.assertNotIn("123456789", json.dumps(gone))

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

    def test_a_replay_record_that_fails_stops(self):
        p = self.run_replay(PG_STUB_NO_SPLINE="1")                 # every check exits 0, but no spline open is shown
        self.assertEqual(p.returncode, 1, p.stdout)
        self.assertIn("[replay] STOP: the replay", p.stdout)

    def test_refusals(self):
        (self.R / "x").write_text("x")
        self.assertEqual(self.run_replay().returncode, 2)                 # not empty
        p = subprocess.run(["bash", str(self.dep / "3d-unfolding/genie/pg_replay.sh"), "--workdir", "rel"],
                           cwd=self.tmp, capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main()
