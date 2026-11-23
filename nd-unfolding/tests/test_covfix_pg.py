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
PROBE_DIR = REPO / "docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe"
for p in (str(ND), str(ND / "pv-ladder"), str(GENIE)):
    if p not in sys.path:
        sys.path.insert(1, p)
import fd_f1_prep as PREP  # noqa: E402
import gen5d_v3 as V3  # noqa: E402
import pg_lib  # noqa: E402

_spec = importlib.util.spec_from_file_location("pg_probe", PROBE_DIR / "pg-probe.py")
PROBE = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(PROBE)

BASE = 1_234_567_890
PG_TUNES = ("G21_11b_00_000", "G18_02b_02_11b", "G18_02a_02_11b")


def seeds(base=BASE, u1="G18_02b_02_11b", **over):
    d = {"tunes": [{"u": 0, "name": "G21_11b_00_000", "task_seeds": [base + k for k in range(7)]},
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
        self.assertEqual([(u, n) for u, n, _ in t], [(0, "G21_11b_00_000"), (1, "G18_02b_02_11b")])
        self.assertEqual(t[1][2][0], BASE + 10_000)
        self.assertEqual(self.load(seeds(u1="G18_02a_02_11b"))[1][1], "G18_02a_02_11b")
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
        self.assertEqual(lines[0], f"G21_11b_00_000 {BASE} u0/t0")
        self.assertEqual(lines[13], f"G18_02b_02_11b {BASE + 10_006} u1/t6")
        self.assertNotIn(str(BASE)[:7], so + se)
        rc, so, se = quiet(pg_lib.main, ["queue", "--seeds", str(self.tmp / "seeds.json"), "--out", str(out)])
        self.assertEqual(rc, 2)                                         # refuses to overwrite
        (self.tmp / "seeds.json").write_text(json.dumps(seeds(base=5)))
        rc, so, se = quiet(pg_lib.main, ["queue", "--seeds", str(self.tmp / "seeds.json"), "--out",
                                         str(self.tmp / "q2.txt")])
        self.assertEqual(rc, 2)
        self.assertFalse((self.tmp / "q2.txt").exists())

    def test_products(self):
        (self.tmp / "seeds.json").write_text(json.dumps(seeds(u1="G18_02a_02_11b")))
        argv = ["products", "--workdir", str(self.tmp), "--seeds", str(self.tmp / "seeds.json")]
        self.assertEqual(quiet(pg_lib.main, argv)[0], 2)               # nothing to list yet
        for t in ("genie_v3_g21", "genie_v3_g18_02a"):
            for rel in (f"out/prep/bridged/{t}.json", f"out/prep/ratios/L-5D-PV/{t}.json", f"out/gen5d/{t}_xsec5d.npz"):
                (self.tmp / rel).parent.mkdir(parents=True, exist_ok=True)
                (self.tmp / rel).write_text("x")
        self.assertEqual(quiet(pg_lib.main, argv)[0], 0)
        rec = json.loads((self.tmp / "PRODUCTS.json").read_text())
        self.assertEqual([(p["u"], p["truth"], p["bridged"]) for p in rec["products"]],
                         [(0, "genie_v3_g21", "out/prep/bridged/genie_v3_g21.json"),
                          (1, "genie_v3_g18_02a", "out/prep/bridged/genie_v3_g18_02a.json")])
        self.assertEqual(quiet(pg_lib.main, argv)[0], 2)               # refuses to overwrite


class Consistency(unittest.TestCase):
    """The tune names, qualifiers and truth names agree across every file that carries them."""

    def test_names(self):
        self.assertEqual((pg_lib.U0,) + pg_lib.U1, (PROBE.SLOT1, PROBE.SLOT2, PROBE.SLOT2_FALLBACK))
        self.assertEqual(sorted(pg_lib.TRUTH.values()), sorted(PREP.PG_TRUTHS))
        self.assertEqual(PREP.PG_U0, pg_lib.TRUTH[pg_lib.U0])
        self.assertEqual(PREP.PG_U1, tuple(pg_lib.TRUTH[t] for t in pg_lib.U1))
        self.assertEqual(pg_lib.RUNG, PREP.RUNG)
        for t in PG_TUNES:
            self.assertIn(t, V3.TUNES)
            self.assertIn(t, PREP.PG_TRUTHS[pg_lib.TRUTH[t]])
            self.assertIn(PROBE.qualifier(t), V3.TUNES[t])

    def test_qualifier_cases(self):
        run = (GENIE / "run_gevgen_v3.sh").read_text()
        setup = (GENIE / "setup_genie_v3.sh").read_text()
        gen = (GENIE / "pg_generate.sh").read_text()
        for t in PG_TUNES:
            q = PROBE.qualifier(t)
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

    def test_pg_pins_match_the_probe(self):
        out = PROBE_DIR / "pg-probe.out"
        if not out.exists():
            self.skipTest("pending: PG's probe has not run (pg-probe.out absent)")
        line = [ln for ln in out.read_text().splitlines() if ln.startswith("PG-PROBE-RESULT ")]
        rec = json.loads(line[-1].split(" ", 1)[1])
        chosen = [t for t in rec["decision"]["chosen"].values() if t]
        self.assertTrue(chosen)
        for t in chosen:
            c = rec["catalog"][t]
            self.assertEqual(V3.PG_SPLINE_PINS[t], (c["spline_sha256"], c["readme_sha256"],
                                                    c["readme_version_lines"][0]))


class Gen5dV3Pins(unittest.TestCase):
    def test_spline_check_refuses_an_unpinned_tune(self):
        tmp = Path(tempfile.mkdtemp(prefix="pg-v3-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        import gzip
        spl = '<genie_xsec_spline_list version="3.00"><genie_tune name="G21_11b_00_000">' \
              '<spline name="genie::X;tgt:1000060120;y">1</spline></genie_tune></genie_xsec_spline_list>'
        (tmp / "src.xml").write_text(spl)
        (tmp / "red.xml.gz").write_bytes(gzip.compress(spl.encode()))
        (tmp / "README").write_text("version v3_04_00 qualifier G2111b00000:k250:e1000\n")
        argv = ["spline-check", "--tune", "G21_11b_00_000", "--source", str(tmp / "src.xml"), "--reduced",
                str(tmp / "red.xml.gz"), "--readme", str(tmp / "README"), "--out", str(tmp / "c.json")]
        with mock.patch.dict(V3.PG_SPLINE_PINS, {}, clear=True):
            self.assertEqual(quiet(V3.main, argv)[0], 1)
        self.assertIn("no pinned spline file", json.loads((tmp / "c.json").read_text())["refused"][0])
        pin = (hashlib.sha256((tmp / "src.xml").read_bytes()).hexdigest(),
               hashlib.sha256((tmp / "README").read_bytes()).hexdigest(),
               "version v3_04_00 qualifier G2111b00000:k250:e1000")
        with mock.patch.dict(V3.PG_SPLINE_PINS, {"G21_11b_00_000": pin}):
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
                    {"genie_v3_g21": ("/a", "a"), "genie_v3_g18_02b": ("/b", "b"), "genie_v3_g18_02a": ("/c", "c")},
                    {"genie_v3_g21": ("/a", "a"), "genie_v3_g18": ("/b", "b")}):
            with self.subTest(sorted(bad)), self.assertRaises(SystemExit):
                PREP.f1_config(self.base, bad, "pg")
        with self.assertRaises(SystemExit):
            PREP.f1_config(self.base, {"genie_v3_g21": ("/a", "a"), "genie_v3_g18_02b": ("/b", "b")}, "f1")
        with self.assertRaises(SystemExit):
            PREP.f1_config(self.base, {}, "other")

    def test_main_pg(self):
        import numpy as np
        import pvl_lib as L
        n = int(np.prod([len(L.FINE[a]) - 1 for a in L.AXES5]))
        preds = {}
        for k in ("genie_v3_g21", "genie_v3_g18_02b"):
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
case "$1" in
  reduce) mkdir -p "$3"; echo s > "$3/$2_CH.xml.gz" ;;
  graphs) echo g > "$4" ;;
  genie) mkdir -p "$6"; cd "$6"; echo "[v3] genie $2 N=$4 seed=$5"
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
elif a[0] == "spline-check": open(arg("--out"), "w").write("{}")
elif a[0] == "flux-check": sys.exit(int(os.environ.get("PG_STUB_FLUXCHECK_RC", "0")))
elif a[0] == "convert": open(arg("--out"), "w").write("npz")
'''
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
        (g / "run_gevgen_v3.sh").write_text(STUB_RUN)
        (g / "gen5d_v3.py").write_text(STUB_V3)
        (self.dep / "nd-unfolding/fd_f1_prep.py").write_text(STUB_PREP)
        (self.dep / "setup_salloc_env.sh").write_text(STUB_ENV)
        for name, body in (("python3", PY311.replace("{py}", sys.executable)), ("hadd", HADD), ("timev", TIMEV)):
            (self.bin / name).write_text(body)
            (self.bin / name).chmod(0o755)
        self.sysbin = self.tmp / "sysbin"            # what /usr/bin gives on Perlmutter and not on macOS
        self.sysbin.mkdir()
        (self.sysbin / "timeout").write_text(TIMEOUT)
        (self.sysbin / "timeout").chmod(0o755)
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
                         ["G18_02b_02_11b", "G21_11b_00_000"])
        checks = [ln for ln in log if ln.startswith("gen5d_v3 spline-check")]
        self.assertEqual(len(checks), 2)
        self.assertIn("/G2111b00000-k250-e1000/data/gxspl-NUsmall.xml", checks[0])
        self.assertIn("/G1802b0211b-k250-e1000/data/README", checks[1])
        fc = [ln for ln in log if ln.startswith("gen5d_v3 flux-check")][0]
        self.assertEqual(len(re.findall(r"/work/u[01]/t\d", fc)), 14)
        conv = [ln for ln in log if ln.startswith("gen5d_v3 convert")]
        self.assertEqual(sorted(re.search(r"--tune (\S+)", c).group(1) for c in conv),
                         ["G18_02b_02_11b", "G21_11b_00_000"])
        prep = [ln for ln in log if ln.startswith("fd_f1_prep")][0]
        self.assertIn("--truth-set pg", prep)
        self.assertRegex(prep, r"--pred genie_v3_g21=\S+/out/gen5d/genie_v3_g21_xsec5d\.npz=[0-9a-f]{64}")
        self.assertRegex(prep, r"--pred genie_v3_g18_02b=\S+genie_v3_g18_02b_xsec5d\.npz=[0-9a-f]{64}")
        rec = json.loads((self.W / "PRODUCTS.json").read_text())
        self.assertEqual([x["truth"] for x in rec["products"]], ["genie_v3_g21", "genie_v3_g18_02b"])
        tmpdirs = {ln.split(" ", 1)[1] for ln in log if ln.startswith("TMPDIR ")}
        self.assertEqual(tmpdirs, {str(self.W / "tmp")})              # re-exported after every activation
        for u in (0, 1):
            for k in range(7):
                self.assertIn("[v3] genie", (self.W / f"out/work/u{u}/t{k}/task.log").read_text())
        self.assertEqual(list(self.W.rglob("genie-mcjob-*")), [])
        self.assertEqual(len(list(self.W.rglob("gevgen.status"))), 14)
        sums = (self.W / "out/PG-SHA256SUMS").read_text()
        for f in ("./flux_phi_t_0_100.root", "./graphs_G21_11b_00_000.root", "./spline_check_G18_02b_02_11b.json",
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
        self.assertFalse(self.log.exists())

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
        p = self.run_gen(PG_STUB_HADD_FAIL="genie_v3_g21_ALL", PG_STUB_HADD_SLOW="genie_v3_g18_02b_ALL",
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

    def test_fallback_tune(self):
        (self.W / "seeds.json").write_text(json.dumps(seeds(u1="G18_02a_02_11b")))
        p = self.run_gen()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        rec = json.loads((self.W / "PRODUCTS.json").read_text())
        self.assertEqual(rec["products"][1]["tune"], "G18_02a_02_11b")


if __name__ == "__main__":
    unittest.main()
