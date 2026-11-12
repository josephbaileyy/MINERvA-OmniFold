"""RDX tranche-2 tests (RDX-DECLARATION.md §3, §5): the cap gate, the merge's sums and K1, the path checks, and the
launchers' tables against the declaration.

    python3 -m unittest -v nd-unfolding/rdx/test_rdx_stages.py
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ND = HERE.parent
ROOT = ND.parent
for p in (str(HERE), str(ND)):
    if p not in sys.path:
        sys.path.insert(0, p)
if not hasattr(os, "O_NOATIME"):  # macOS: the flag is Linux's; 0 makes the open plain, and the tests keep atime >= mtime
    os.O_NOATIME = 0
import rdx_cap as CAP  # noqa: E402
import rdx_merge as MG  # noqa: E402
import rdx_paths as PA  # noqa: E402

DECL = ROOT / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/redump-f12i-20261112/RDX-DECLARATION.md"
N_SIG = {"1A": 1736833, "1B": 469084, "1C": 894027, "1D": 2595088, "1E": 2165554, "1F": 2919699, "1G": 2484197,
         "1L": 232123, "1M": 3583806, "1N": 2042233, "1O": 593359, "1P": 782010}  # proxy_hists_meta.json
FENCE = ("cov2d", "t2a", "ll5d", "e96data", "rpd_", "rsn_")
POLICY_PATH_TOKEN = "<policy>"
LATER = {"nd-unfolding/rdx/rdx-inputs-SHA256SUMS"}
FLOOR = {"BUILD", "HOST", "CC", "CXX", "CPP", "AR", "LD", "NM", "RANLIB", "STRIP", "PREFIX", "CFLAGS", "CXXFLAGS",
         "LDFLAGS", "CPPFLAGS"}  # the hand list, a floor under the measured setup_salloc_env.exports  # the one declared path that is written later, by stage 3's pin


def sacct(*rows):
    return ["|".join(str(x) for x in r) for r in rows]


class Cap(unittest.TestCase):
    def test_the_job_kinds(self):
        self.assertEqual(CAP.kind("rdx_s1_1A"), "shared")
        self.assertEqual(CAP.kind("rdx_s2_1M"), "shared")
        self.assertIsNone(CAP.kind("rdx_s1_1B"))
        self.assertIsNone(CAP.kind("rdx_s2_9Z"))
        for n in ("rdx_s2_merge", "rdx_s3_a", "rdx_s3_b"):
            self.assertEqual(CAP.kind(n), "exclusive")
        self.assertEqual((CAP.CAP, CAP.SHARED_RATE), (2.5, 0.0391))

    def test_spent_held_unlisted_and_the_wanted_ceiling(self):
        rows = sacct(("100", "rdx_s1_1A", "COMPLETED", 3600, 1, 135), ("101", "rdx_s2_1B", "RUNNING", 100, 1, 60),
                     ("102", "rdx_s3_a", "COMPLETED", 1200, 1, 22), ("103", "other_job", "COMPLETED", 9e5, 1, 60))
        log = ["SUBMIT id=101 name=rdx_s2_1B limit=1:00:00 utc=x", "SUBMIT id=104 name=rdx_s2_1C limit=1:15:00 utc=x"]
        r = CAP.recompute(rows, log, "rdx_s3_b", "0:22:00")
        self.assertAlmostEqual(r["spent"], 0.0391 + 1200 / 3600)
        self.assertAlmostEqual(r["held"], 0.0391 + 1.25 * 0.0391)
        self.assertEqual(r["unlisted_ids"], ["104"])
        self.assertAlmostEqual(r["want_ceiling"], 22 / 60)
        self.assertTrue(r["pass"])

    def test_over_the_cap_and_unusable_inputs_refuse(self):
        rows = sacct(("1", "rdx_s3_a", "COMPLETED", 8000, 1, 22))
        self.assertFalse(CAP.recompute(rows, [], "rdx_s3_b", "0:22:00")["pass"])
        with self.assertRaises(CAP.Unusable):
            CAP.recompute(sacct(("1", "rdx_bogus", "COMPLETED", 1, 1, 1)), [], "rdx_s3_a", "0:22:00")
        with self.assertRaises(CAP.Unusable):
            CAP.recompute(sacct(("1", "rdx_s3_a", "PENDING", 0, 1, "UNLIMITED")), [], "rdx_s3_b", "0:22:00")
        with self.assertRaises(CAP.Unusable):
            CAP.recompute([], ["SUBMIT id=9 limit=1:00:00"], "rdx_s3_b", "0:22:00")


class MergeAndK1(unittest.TestCase):
    def test_the_sums_must_list_exactly_the_twelve_loops(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "s"
            lines = [f"{'a' * 64}  {MG.LOOP.format(pl)}" for pl in MG.PLAYLISTS]
            p.write_text("\n".join(lines) + "\n")
            self.assertEqual(len(MG.read_sums(p)), 12)
            p.write_text("\n".join(lines[:-1]) + "\n")
            with self.assertRaises(SystemExit):
                MG.read_sums(p)
            p.write_text("\n".join(lines + [f"{'b' * 64}  extra.root"]) + "\n")
            with self.assertRaises(SystemExit):
                MG.read_sums(p)

    def test_k1_passes_only_when_every_key_matches(self):
        with tempfile.TemporaryDirectory() as d:
            files = {}
            for n in ("lat", "latb", "mp1", "mp1b"):
                files[n] = Path(d) / f"{n}.npz"
                np.savez(files[n], x=np.arange(3))
            saved = dict(MG.CT.MP1_ZERO)
            MG.CT.MP1_ZERO.update(lat_npz=MG.C.sha256(files["mp1"]), lat_bkg=MG.C.sha256(files["mp1b"]))
            try:
                good = lambda p, q, keys: {k: True for k in keys}  # noqa: E731
                r = MG.k1(files["lat"], files["latb"], files["mp1"], files["mp1b"], compare=good)
                self.assertEqual(r["verdict"], "PASS")
                bad = lambda p, q, keys: {k: k != "w_truth" for k in keys}  # noqa: E731
                r = MG.k1(files["lat"], files["latb"], files["mp1"], files["mp1b"], compare=bad)
                self.assertEqual((r["verdict"], r["failed_keys"]), ("FAIL", ["npz:w_truth"]))
                MG.CT.MP1_ZERO["lat_npz"] = "0" * 64
                with self.assertRaises(SystemExit):
                    MG.k1(files["lat"], files["latb"], files["mp1"], files["mp1b"], compare=good)
            finally:
                MG.CT.MP1_ZERO.clear()
                MG.CT.MP1_ZERO.update(saved)


class Paths(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.d = Path(self.td.name)
        self.cfg = self.d / "policy.json"
        self.cfg.write_text(json.dumps({"cov2d_protected_paths": ["/p/x/flux.txt", "/p/cov2d-run"]}))

    def tearDown(self):
        self.td.cleanup()

    def test_the_policy_check(self):
        self.assertEqual(PA.policy(self.cfg, ["/p/x", "/p/other"])["verdict"], "CLEAR")
        for bad in ("/p/x/flux.txt", "/p/cov2d-run/a/b", PA.NEVER_READ[0], PA.NEVER_READ[3] + "/f.root"):
            with self.subTest(bad):
                self.assertEqual(PA.policy(self.cfg, [bad])["verdict"], "REFUSED")
        self.assertEqual(PA.policy(self.cfg, ["/p/cov2d-run2"])["verdict"], "CLEAR")
        empty = self.d / "e.json"
        empty.write_text("{}")
        with self.assertRaises(ValueError):
            PA.policy(empty, ["/x"])

    def test_the_never_read_list_names_the_ll5d_inputs_and_cov2ds_cv(self):
        joined = "\n".join(PA.NEVER_READ)
        for s in ("of_inputs_5d.npz", "bkg_dump.npz", "runEventLoopOmniFold_MEFHC.root", "universes_full.root"):
            self.assertIn(s, joined)

    def test_atime_stage_and_manifest(self):
        src = self.d / "src.bin"
        src.write_bytes(b"abc" * 1000)
        st = os.stat(src)
        os.utime(src, (st.st_mtime + 10, st.st_mtime))  # atime after mtime: a plain read cannot move it
        self.assertEqual(PA.atime([str(src)])["verdict"], "PRESENT")
        self.assertEqual(PA.atime([str(src), str(self.d / "gone")])["verdict"], "MISSING")
        pin = hashlib.sha256(src.read_bytes()).hexdigest()
        r = PA.stage(str(self.d / "stage"), [(str(src), pin)])
        self.assertEqual(r["verdict"], "STAGED")
        self.assertEqual((self.d / "stage/src.bin").read_bytes(), src.read_bytes())
        with self.assertRaises(ValueError):
            PA.stage(str(self.d / "stage"), [(str(src), pin)])
        r = PA.stage(str(self.d / "stage2"), [(str(src), "0" * 64)])
        self.assertEqual(r["verdict"], "REFUSED")
        self.assertFalse((self.d / "stage2/src.bin").exists())
        (self.d / "tree/sub").mkdir(parents=True)
        for rel in ("a.txt", "sub/b.txt"):
            f = self.d / "tree" / rel
            f.write_bytes(rel.encode())
            s2 = os.stat(f)
            os.utime(f, (s2.st_mtime + 10, s2.st_mtime))
        out = self.d / "m.sha256"
        PA.manifest(str(self.d / "tree"), str(out))
        self.assertEqual(out.read_text().splitlines(),
                         [f"{hashlib.sha256(b'a.txt').hexdigest()}  a.txt", f"{hashlib.sha256(b'sub/b.txt').hexdigest()}  sub/b.txt"])
        with self.assertRaises(ValueError):
            PA.manifest(str(self.d / "tree"), str(out))


def limit_rule(pl: str) -> str:
    """§5: 1.5 x the projection at S1's 1A rate scaled by the May signal count, up to 15 minutes, at least one hour."""
    t = 5242.0 * N_SIG[pl] / N_SIG["1A"] / 3600
    q = max(1.0, math.ceil(1.5 * t * 4) / 4)
    return f"{int(q)}:{int(round((q - int(q)) * 60)):02d}:00"


class Tables(unittest.TestCase):
    def test_the_event_loop_limits_are_the_declared_rule_everywhere(self):
        evl = (HERE / "sbatch_rdx_evloop.sh").read_text()
        con = (HERE / "rdx_connect.sh").read_text()
        for pl in N_SIG:
            want = limit_rule(pl)
            self.assertIn(f"{pl}) LIMIT={want} ;;", evl, pl)
            if pl != "1A":
                self.assertIn(f"\n{pl} {want}\n", con, pl)
        self.assertIn("submit rdx_s1_1A 2:15:00", con)
        self.assertAlmostEqual(sum(CAP.SHARED_RATE * sum(int(x) * f for x, f in zip(limit_rule(p).split(":"), (1, 1 / 60, 1 / 3600)))
                                   for p in N_SIG if p != "1A"), 26.0 * CAP.SHARED_RATE, places=6)

    def test_every_launcher_fences_the_six_prefixes(self):
        for f in ("sbatch_rdx_evloop.sh", "sbatch_rdx_merge.sh", "sbatch_rdx_arms.sh", "rdx_connect.sh"):
            text = (HERE / f).read_text()
            m = re.findall(r"\^\(([a-z0-9_|]+)\)", text)
            self.assertTrue(m, f)
            for alt in m:
                self.assertTrue(set(FENCE) <= set(alt.split("|")), (f, alt))

    def test_the_task_table_is_the_declarations(self):
        rows = [ln.split("\t") for ln in (HERE / "rdx_tasks.tsv").read_text().splitlines() if ln and not ln.startswith("#")]
        decl = DECL.read_text()
        sec = decl[decl.index("## 4. The arms"):decl.index("**NC-X.**")]
        drows = [[c.strip() for c in ln.strip("|").split("|")] for ln in sec.splitlines() if re.match(r"^\| X", ln)]
        self.assertEqual([r[0] for r in rows], [r[0] for r in drows])
        prev = ""
        for r, d in zip(rows, drows):
            task, job, features, permute, weight, truth, transfer, closure, inputs, _ = r
            if d[5].startswith("the same closure"):
                d[5] = prev
            prev = d[5]
            self.assertEqual(job, d[1], task)
            self.assertEqual(features, d[2].split(",")[0].strip(), task)
            self.assertEqual(permute != "-", "permuted" in d[2], task)
            if permute != "-":
                self.assertIn(permute, d[2] if "seed" in d[2] else "seed 20261113", task)
            self.assertEqual(weight == "w_push_w_truth", d[3] == "w_push · w_truth", task)
            self.assertEqual(transfer == "yes", d[4].startswith("yes"), task)
            self.assertEqual(closure == "yes", "closure" in d[5], task)
            self.assertEqual(truth, "a7_gibuu" if "GiBUU" in d[5] else "q3" if "q3" in d[5] else "ratio", task)
            self.assertEqual(inputs == "lat_zero", "lat_zero" in d[5], task)
        self.assertEqual(sum(r[1] == "S3a" for r in rows), 8)
        self.assertEqual(sum(r[1] == "S3b" for r in rows), 7)

    def test_every_repo_path_the_launchers_name_exists_at_head(self):
        """B1's root cause: a hard-coded repo path that does not exist (the smoke stubbed it into its own tiny repo)."""
        import subprocess
        alias = {'"$R/': '"nd-unfolding/rdx/', "$R/": "nd-unfolding/rdx/", "${H}/": "nd-unfolding/rdx/", "$H/": "nd-unfolding/rdx/",
                 "$DEP/$POLICY_REL": POLICY_PATH_TOKEN, "${D}/": "", "$D/": "", "$DEP/": "", "${DEPLOY}/": "", "$DEPLOY/": ""}
        roots = r"(?:docs/orchestration|nd-unfolding|2d-unfolding|publication|measurement-paper|setup_salloc_env\.sh)"
        found = set()
        for f in ("rdx_connect.sh", "sbatch_rdx_evloop.sh", "sbatch_rdx_merge.sh", "sbatch_rdx_arms.sh"):
            text = (HERE / f).read_text()
            pol = re.search(r"^POLICY_REL=(\S+)$", text, re.M)
            if pol:
                found.add(pol.group(1))
            for k, v in alias.items():
                text = text.replace(k, v)
            for m in re.finditer(r"(?<![A-Za-z0-9_./\-])(" + roots + r"[A-Za-z0-9_./\-]*)", text):
                tok = m.group(1).rstrip(".")
                if any(c in tok for c in "${}*") or tok.endswith("/"):
                    continue
                found.add(tok)
        found |= {f"2d-unfolding/playlist_manifests/{pl}_{k}.txt" for pl in N_SIG for k in ("Data", "MC")}
        self.assertIn("nd-unfolding/rdx/rdx_paths.py", found)
        self.assertTrue(any("policy-config.json" in t for t in found))
        exists = lambda t: subprocess.run(["git", "cat-file", "-e", f"HEAD:{t}"], cwd=ROOT,  # noqa: E731
                                          capture_output=True).returncode == 0
        missing = [t for t in sorted(found - LATER) if not exists(t)]
        self.assertEqual(missing, [])
        self.assertTrue(LATER <= found)
        self.assertFalse(any(exists(t) for t in LATER))  # committed only at stage 3's pin (section 2c)

    def test_c1_stops_on_the_walk_probe_and_s2_requires_its_pass(self):
        con = (HERE / "rdx_connect.sh").read_text()
        c1 = con[con.index("\nc1)\n"):con.index("\ns2)\n")]
        probe = c1.index("rdx_probe_walk.py")
        self.assertIn("rp=$?", c1[probe:probe + 200])
        self.assertIn('[ $rp -eq 0 ] && grep -q \'"verdict": "PASS"\' "$OUT/checks/walk_probe.json"', c1)
        self.assertLess(c1.index("[ $rp -eq 0 ]"), c1.index("STAGE 1 CHECKS PASS"))
        s2 = con[con.index("\ns2)\n"):con.index("\nc2)\n")]
        self.assertIn("for c in align_1A truthx_rows_1A walk_probe; do", s2)

    def test_no_launcher_variable_is_one_the_env_setup_exports(self):
        """The s0 STOP of 2026-11-12: conda's activation (setup_salloc_env.sh) set BUILD, clobbering the connect's."""
        measured = {ln.strip() for ln in (HERE / "setup_salloc_env.exports").read_text().splitlines() if ln.strip()}
        self.assertIn("BUILD", measured)
        self.assertGreaterEqual(len(measured), 80)
        banned = measured | FLOOR
        assign = re.compile(r"(?:^|[\s;(&|{])(?:local\s+|export\s+|declare\s+-?\w*\s+)?([A-Za-z_][A-Za-z0-9_]*)=")
        hits = {}
        for f in ("rdx_connect.sh", "sbatch_rdx_evloop.sh", "sbatch_rdx_merge.sh", "sbatch_rdx_arms.sh"):
            names = set()
            for ln in (HERE / f).read_text().splitlines():
                code = ln.split("#", 1)[0] if not ln.lstrip().startswith("#!") else ""
                names |= set(assign.findall(code))
                for m in re.finditer(r"\bread\s+(?:-r\s+)?((?:[A-Za-z_][A-Za-z0-9_]*\s*)+)", code):
                    names |= set(m.group(1).split())
                names |= set(re.findall(r"\bfor\s+([A-Za-z_][A-Za-z0-9_]*)\s+in\b", code))
            bad = sorted(names & banned)
            if bad:
                hits[f] = bad
        self.assertEqual(hits, {})

    def test_the_event_loop_job_allows_the_connects_b(self):
        con = (HERE / "rdx_connect.sh").read_text()
        b = re.search(r"^B=(\S+)", con, re.M).group(1)
        self.assertTrue(b.endswith("rdx-20261112b"))
        self.assertIn(f'[[ "${{B}}" == {b} || -n "${{RDX_SMOKE}}" ]]', (HERE / "sbatch_rdx_evloop.sh").read_text())

    def test_the_launcher_pins_the_connect_script(self):
        sha = hashlib.sha256((HERE / "rdx_connect.sh").read_bytes()).hexdigest()
        self.assertIn(f'SHA={sha}', (HERE / "rdx_connect_launch.sh").read_text())


if __name__ == "__main__":
    unittest.main()
