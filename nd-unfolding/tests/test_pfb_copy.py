#!/usr/bin/env python3
"""Tests of PILOT-FB's copy connect, revision 2 (pfb_copy_remote.py, pfb_copy_launch.sh; PILOT-FB-BINDING-1 addendum
C1, ruling 3 step 3; the copy-connect read's K1-K8). The copy runs against a scratch root through the test-only entry
(tests/pfb_copy_testentry.py) with a stub sacct and test pins; the production entry, the bootstrap, the strict verify
and the launcher are tested as they ship. Each guard in the direction it acts and in the other. Imports: fb_pilot_analyze
and rounding_mechanism_analyze (the pins and the analysis's own copy check), which import rounding_mechanism_probe."""
import ast
import errno
import hashlib
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
REMOTE = ND / "pfb_copy_remote.py"
LAUNCH = ND / "pfb_copy_launch.sh"
ENTRY = ND / "tests" / "pfb_copy_testentry.py"
sys.path.insert(0, str(ND))
sys.path.insert(0, str(ND / "tests"))
import pfb_copy_remote as C  # noqa: E402
import pfb_copy_testentry as TE  # noqa: E402
import fb_pilot_analyze as A  # noqa: E402

GIT_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "HOME": "/tmp"}


def launcher_value(name: str) -> str:
    return re.search(rf"^{name}=([0-9a-f]+)$|; {name}=([0-9a-f]+)$", LAUNCH.read_text(), re.M).group(0).split("=")[-1]


class Base(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.d = Path(self._t.name).resolve()
        self.stage = self.d / "stage"
        self.stage.mkdir()
        self.a0 = self.d / "rs1" / "runs" / "A0"
        self.a0.mkdir(parents=True)
        self.deploy = self.d / "deploy"
        (self.deploy / Path(C.SIGMA_REL).parent).mkdir(parents=True)
        pins = {}
        for n in C.A0_PINS:
            p = self.a0 / n
            p.write_bytes(n.encode() * 7)
            pins[n] = hashlib.sha256(p.read_bytes()).hexdigest()
        sig = self.deploy / C.SIGMA_REL
        sig.write_text('{"sigma_rel_pct": [1.0]}')
        pins[C.SIGMA_NAME] = hashlib.sha256(sig.read_bytes()).hexdigest()
        for cmd in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x"]):
            subprocess.run(["/usr/bin/git", "-C", str(self.deploy), *cmd], check=True, env=GIT_ENV)
        self.pin = subprocess.run(["/usr/bin/git", "-C", str(self.deploy), "rev-parse", "HEAD"], capture_output=True,
                                  text=True, env=GIT_ENV).stdout.strip()
        for p in list(self.a0.iterdir()) + [sig]:  # atime after mtime, so a relatime platform leaves it alone
            mt = p.stat().st_mtime_ns
            os.utime(p, ns=(mt + 10 ** 12, mt))
        (self.d / "pins.json").write_text(json.dumps(pins))
        self.pins = pins
        self.receipt()
        (self.d / "bin").mkdir()
        self.sacct("")

    def tearDown(self):
        self._t.cleanup()

    def receipt(self, **over):
        p = self.stage / "smoke-receipt.json"
        if p.is_symlink() or p.exists():
            p.unlink()
        rec = {"stage": str(self.stage), "pin": self.pin, "local_test": False, "index_sha256": "a" * 64, **over}
        p.write_text(json.dumps(rec))

    def sacct(self, rows: str, rc: int = 0, second: str = None):
        s = self.d / "bin" / "sacct"
        body = f"printf '%b' {json.dumps(rows)}\nexit {rc}\n"
        if second is not None:
            n = self.d / "sacct_calls"
            body = (f"c=$(cat {n} 2>/dev/null || echo 0); echo $((c + 1)) > {n}\n"
                    f"if [ \"$c\" -ge 1 ]; then printf '%b' {json.dumps(second)}; exit 0; fi\n" + body)
        s.write_text("#!/bin/bash\n" + body)
        s.chmod(0o755)

    def cfg(self):
        return TE.config(self.d)

    def run_entry(self, deploy=None):
        return subprocess.run([sys.executable, str(ENTRY), str(self.d), str(deploy or self.deploy)], capture_output=True,
                              text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})

    def copy_inprocess(self, deploy=None):
        out = io.StringIO()
        rc = C.copy(self.cfg(), str(deploy or self.deploy), out=out)
        return rc, out.getvalue()

    def assert_nothing_written(self, stage=None):
        self.assertEqual(sorted(p.name for p in (stage or self.stage).iterdir()), ["smoke-receipt.json"])


class Copy(Base):
    def test_the_pins_and_declared_paths(self):
        self.assertEqual(C.A0_PINS, {n: s for n, s in A.rs1_pins(A.RS1_SUMS).items()
                                     if n in {A.name("rs1_A0", None)} | {A.name("rs1_A0", j) for j in A.SEEDS}})
        self.assertEqual(len(C.A0_PINS), 21)
        import rounding_mechanism_analyze as ra
        self.assertEqual(C.SIGMA_SHA256, ra.SIGMA_RECEIPT_SHA256)
        self.assertEqual(C.SIGMA_REL, A.SIGMA_REL)
        self.assertEqual((C.STAGE_DECLARED, C.A0_DIR_DECLARED), (A.STAGE_DECLARED, str(A.RS1_A0_ORIGINALS)))
        cfg = C.production_config()
        self.assertEqual((cfg.stage, cfg.sacct, cfg.require_noatime, len(cfg.pins)),
                         (C.STAGE_DECLARED, "/usr/bin/sacct", True, 22))

    def test_a_clear_copy_makes_plain_new_files_inside_the_stage(self):
        before = {p.name: p.stat() for p in self.a0.iterdir()}
        r = self.run_entry()
        self.assertEqual(r.returncode, 0, r.stderr)
        man = json.loads(r.stdout)
        self.assertEqual(len(man["files"]), 22)
        self.assertEqual(man["smoke"]["pin"], self.pin)
        for n in C.A0_PINS:
            q = self.stage / "a0-refs" / n
            st = os.lstat(q)
            self.assertTrue(q.is_file() and not q.is_symlink() and st.st_nlink == 1)
            self.assertNotEqual((st.st_dev, st.st_ino), (before[n].st_dev, before[n].st_ino), "a new inode")
            self.assertEqual(q.read_bytes(), (self.a0 / n).read_bytes())
            self.assertEqual(before[n].st_atime_ns, (self.a0 / n).stat().st_atime_ns, "the source's atime is unchanged")
            self.assertIsNone(A.stage_copy_problem(q, self.stage, (self.a0 / n,)), "the analysis accepts the copy")
        self.assertIsNone(A.stage_copy_problem(self.stage / C.SIGMA_NAME, self.stage, (self.deploy / C.SIGMA_REL,)))
        self.assertTrue(all(f["moved"] == [] and f["problems"] == [] and f["copy_fd_path"] == f["copy"]
                            for f in man["files"]))
        self.assertEqual(sorted(p.name for p in self.stage.iterdir()), ["a0-refs", C.SIGMA_NAME, "smoke-receipt.json"])

    def test_the_stage_must_hold_the_smoke_receipt_and_no_copies(self):
        (self.stage / "smoke-receipt.json").unlink()
        rc, _ = self.copy_inprocess()
        self.assertEqual(rc, 2)
        self.assertEqual(list(self.stage.iterdir()), [])
        self.receipt()
        (self.stage / "a0-refs").mkdir()
        self.assertEqual(self.copy_inprocess()[0], 2)
        (self.stage / "a0-refs").rmdir()
        (self.stage / C.SIGMA_NAME).symlink_to(self.d / "nowhere")
        self.assertEqual(self.copy_inprocess()[0], 2, "even a dangling link at the sigma copy's place")
        (self.stage / C.SIGMA_NAME).unlink()
        self.assertEqual(self.copy_inprocess(deploy="relative/deploy")[0], 2)
        self.assertEqual(self.copy_inprocess(deploy=self.d / "nogit")[0], 2, "the deploy must be a git checkout")
        self.assert_nothing_written()

    def test_a_source_off_its_pin_or_a_link_refuses_before_any_write(self):
        n = sorted(C.A0_PINS)[3]
        (self.a0 / n).write_bytes(b"changed")
        self.assertEqual(self.copy_inprocess()[0], 4)
        self.assert_nothing_written()
        (self.a0 / n).unlink()
        real = self.d / "elsewhere.npz"
        real.write_bytes(n.encode() * 7)
        (self.a0 / n).symlink_to(real)
        self.assertEqual(self.copy_inprocess()[0], 5)
        self.assert_nothing_written()
        (self.a0 / n).unlink()
        self.assertEqual(self.copy_inprocess()[0], 5)
        self.assert_nothing_written()

    def test_the_remote_script_is_python_3_6_and_runs_no_job(self):
        ast.parse(REMOTE.read_text(), feature_version=(3, 6))
        text = REMOTE.read_text()
        for word in ('"sbatch"', '"srun"', '"salloc"', '"squeue"', "sbatch ", "squeue "):
            self.assertNotIn(word, text)
        self.assertIn('SACCT_DECLARED = "/usr/bin/sacct"', text)


class K1Snapshot(Base):
    """K1: one snapshot, verified at the endpoint."""

    def bootstrap(self, stdin_bytes, sha=None, stdin=None):
        boot = launcher_value("BOOT")
        cmd = ["/usr/bin/python3", "-I", "-S", "-c", "import sys;exec(bytes.fromhex(sys.argv[1]))", boot,
               sha or launcher_value("SHA"), str(self.deploy)]
        if stdin is not None:
            return subprocess.run(cmd, stdin=stdin, capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"})
        return subprocess.run(cmd, input=stdin_bytes, capture_output=True, env={"PATH": "/usr/bin:/bin"})

    def test_tampered_bytes_exit_10_and_write_nothing(self):
        good = REMOTE.read_bytes()
        self.assertEqual(hashlib.sha256(good).hexdigest(), launcher_value("SHA"), "the launcher pins the shipped script")
        r = self.bootstrap(good.replace(b"MEASURES: nothing", b"MEASURES: nothin!"))
        self.assertEqual(r.returncode, 10, r.stderr)
        self.assertIn(b"not the pinned one", r.stderr)
        with open(os.devnull, "rb") as nul:
            r = self.bootstrap(None, stdin=nul)
        self.assertEqual(r.returncode, 10)
        self.assertIn("not a pipe or socket", r.stderr)
        r = self.bootstrap(good)  # the pinned bytes run: the production entry refuses on this laptop
        if hasattr(os, "O_NOATIME"):
            self.assertEqual(r.returncode, 2, r.stderr)
            self.assertIn(b"is not an absolute path under /pscratch/sd/j/josephrb/", r.stderr)
        else:
            self.assertEqual(r.returncode, 3, r.stderr)
            self.assertIn(b"refusing: this platform has no O_NOATIME", r.stderr)
        self.assert_nothing_written()

    def test_the_launcher_captures_once_and_sends_the_capture(self):
        text = LAUNCH.read_text()
        self.assertEqual(text.count('cat "$S"'), 1, "one read of the script")
        self.assertIn("CAP=$(cat \"$S\" && printf x)", text)
        self.assertIn("got=$(printf '%s' \"$CAP\" | shasum -a 256", text)
        self.assertIn("< <(printf '%s' \"$CAP\") > \"$F/copy-manifest.json\"", text, "ssh sends the capture")
        self.assertIn("python3 -I -S - verify \"$F/copy-manifest.json\" < <(printf '%s' \"$CAP\")", text)
        boot = bytes.fromhex(launcher_value("BOOT")).decode()
        self.assertIn("hashlib.sha256(b).hexdigest() != sys.argv[2]", boot)
        self.assertIn("exec(compile(b, \"pfb_copy_remote.py\", \"exec\")", boot)
        self.assertIn("stat.S_ISFIFO(mode) or stat.S_ISSOCK(mode)", boot)
        d = self.d / "launch"
        d.mkdir()
        shutil.copy(LAUNCH, d / "pfb_copy_launch.sh")
        (d / "pfb_copy_remote.py").write_bytes(REMOTE.read_bytes() + b"\n# altered\n")
        out = self.d / "session"
        out.mkdir()
        r = subprocess.run(["bash", str(d / "pfb_copy_launch.sh"), str(out), "login27", "/pscratch/sd/j/josephrb/dep"],
                           capture_output=True, text=True, env={**os.environ, "PATH": "/usr/bin:/bin:/sbin"})
        self.assertEqual(r.returncode, 8)
        self.assertIn("the captured copy script is not the approved one", r.stdout)


class K2Descriptors(Base):
    """K2: descriptor-anchored writes at the literal declared stage."""

    def test_a_symlink_swapped_in_for_the_stage_refuses_with_no_write(self):
        real = self.d / "real-stage"
        os.replace(self.stage, real)
        self.stage.symlink_to(real)
        self.assertEqual(self.copy_inprocess()[0], 2)
        self.assertEqual(sorted(p.name for p in real.iterdir()), ["smoke-receipt.json"])

    def test_a_stage_under_a_symlinked_parent_is_not_the_literal_path(self):
        os.replace(self.stage, self.d / "elsewhere")
        (self.d / "elsewhere-parent").mkdir()
        os.replace(self.d / "elsewhere", self.d / "elsewhere-parent" / "stage")
        (self.d / "link").symlink_to(self.d / "elsewhere-parent")
        cfg = self.cfg()._replace(stage=str(self.d / "link" / "stage"))
        p = self.d / "elsewhere-parent" / "stage" / "smoke-receipt.json"
        p.write_text(json.dumps({"stage": cfg.stage, "pin": self.pin, "local_test": False, "index_sha256": "a" * 64}))
        rc = C.copy(cfg, str(self.deploy), out=io.StringIO())
        self.assertEqual(rc, 2)
        self.assertEqual(sorted(x.name for x in (self.d / "elsewhere-parent" / "stage").iterdir()), ["smoke-receipt.json"])


class K3NoTestHooks(Base):
    def test_the_production_entry_refuses_any_test_switch(self):
        for var in ("PFB_COPY_TEST_ROOT", "PFB_COPY_ANYTHING"):
            env = {"PATH": "/usr/bin:/bin", var: str(self.d)}
            r = subprocess.run([sys.executable, "-I", str(REMOTE), str(self.deploy)], capture_output=True, text=True,
                               env=env)
            self.assertEqual(r.returncode, 2, var)
            self.assertIn("test switches are set in a production run", r.stderr)
            r = subprocess.run([sys.executable, "-I", str(REMOTE), "verify", str(self.d / "m.json")],
                               capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, 2)
        self.assertFalse((self.d / "sacct_calls").exists())
        self.assertNotIn("TEST", "".join(ln for ln in REMOTE.read_text().splitlines() if "environ" in ln
                                         and "PFB_COPY_" not in ln))
        self.assert_nothing_written()


class K4StatIntegrity(Base):
    def torn(self, action):
        target = self.a0 / sorted(C.A0_PINS)[5]
        target_ino = target.stat().st_ino
        real = C._read_all

        def read_all(fd):  # the action happens while the target's descriptor is open, after its bytes were read
            data = real(fd)
            if not read_all.done and os.fstat(fd).st_ino == target_ino:
                read_all.done = True
                action(target)
            return data
        read_all.done = False
        with mock.patch.object(C, "_read_all", read_all):
            return self.copy_inprocess()

    def test_a_chmod_during_the_read_refuses(self):
        rc, _ = self.torn(lambda t: os.chmod(t, 0o600))
        self.assertEqual(rc, 8)
        self.assert_nothing_written()

    def test_a_path_swap_during_the_read_refuses(self):
        def swap(t):
            tmp = t.with_name(t.name + ".new")
            tmp.write_bytes(t.read_bytes())
            os.replace(tmp, t)
        rc, _ = self.torn(swap)
        self.assertEqual(rc, 8)
        self.assert_nothing_written()


class K5Fence(Base):
    def test_blank_fields_a_failed_sacct_and_an_absent_sacct_refuse(self):
        for rows, rc in (("61||RUNNING\n", 0), ("61|pfb_run|\n", 0), ("|pfb_run|RUNNING\n", 0), ("", 1),
                         ("62|cov2d_a|COMPLETING\n", 0)):
            self.sacct(rows, rc)
            self.assertEqual(self.copy_inprocess()[0], 9, rows)
            self.assert_nothing_written()
        (self.d / "bin" / "sacct").unlink()
        self.assertEqual(self.copy_inprocess()[0], 9, "sacct absent")
        self.assert_nothing_written()

    def test_a_fence_that_becomes_active_after_the_copy_is_a_stop(self):
        self.sacct("", second="63|pfb_run|RUNNING\n")
        rc, out = self.copy_inprocess()
        self.assertEqual(rc, 9)
        man = json.loads(out)
        self.assertFalse(man["fence_after"]["clear"])
        self.assertIn("a0-refs", [p.name for p in self.stage.iterdir()], "the copies stay for the director")


class K6StrictVerify(Base):
    def production_manifest(self):
        rc, out = self.copy_inprocess()
        self.assertEqual(rc, 0)
        man = json.loads(out)
        dep = "/pscratch/sd/j/josephrb/pfb-deploy"
        man.update(stage=C.STAGE_DECLARED, a0_dir=C.A0_DIR_DECLARED, deploy=dep, o_noatime=True)
        man["smoke"]["stage"] = C.STAGE_DECLARED
        for key in ("fence", "fence_after"):
            man[key]["command"] = man[key]["command"].replace(str(self.d / "bin" / "sacct"), "/usr/bin/sacct")
        for f in man["files"]:
            n = f["name"]
            pin = C.A0_PINS.get(n) or C.SIGMA_SHA256
            f.update(sha256=pin, copy_sha256=pin, pin=pin,
                     source=(C.A0_DIR_DECLARED + "/" + n) if n != C.SIGMA_NAME else dep + "/" + C.SIGMA_REL,
                     copy=C.STAGE_DECLARED + ("/a0-refs/" + n if n != C.SIGMA_NAME else "/" + C.SIGMA_NAME))
            f["copy_fd_path"] = f["copy"]
        return man

    def test_verify_requires_every_typed_field(self):
        man = self.production_manifest()
        self.assertEqual(C.verify_problems(man), [])
        mutations = (
            ("the report's mutation: one file's two stat records and copy inode removed",
             lambda m: [m["files"][3].pop(k) for k in ("source_fstat_before", "source_fstat_after", "copy_inode")]),
            ("a source path not the declared one", lambda m: m["files"][2].update(source="/pscratch/x/rs1_A0_b-_j-.npz")),
            ("a copy path not the declared one", lambda m: m["files"][2].update(copy="/tmp/x")),
            ("equal inodes", lambda m: m["files"][2].update(copy_inode=m["files"][2]["source_inode"])),
            ("two links", lambda m: m["files"][2].update(copy_nlink=2)),
            ("a moved stat", lambda m: m["files"][2]["source_fstat_after"].update(st_ctime_ns=1)),
            ("a boolean in a stat record", lambda m: m["files"][2]["source_fstat_before"].update(st_nlink=True)),
            ("a path that did not identify the descriptor", lambda m: m["files"][2].update(source_path_inodes=[[0, 0], [0, 0]])),
            ("a missing pin", lambda m: m["files"][2].pop("pin")),
            ("a fence row with a blank field", lambda m: m["fence"]["rows"].append("61||RUNNING")),
            ("an active fence row", lambda m: m["fence_after"]["rows"].append("62|pfb_run|RUNNING")),
            ("no post-copy fence", lambda m: m.pop("fence_after")),
            ("another sacct", lambda m: m["fence"].update(command="sacct -X")),
            ("no smoke binding", lambda m: m.pop("smoke")),
            ("a smoke pin not the deploy's", lambda m: m["smoke"].update(pin="0" * 40)),
            ("a STOP recorded", lambda m: m.update(stop="I/O: ENOSPC")),
            ("21 files", lambda m: m["files"].pop()),
            ("no O_NOATIME", lambda m: m.update(o_noatime=False)))
        for why, edit in mutations:
            m = json.loads(json.dumps(man))
            edit(m)
            self.assertTrue(C.verify_problems(m), why)


class K7IOErrors(Base):
    def test_enospc_on_the_last_copy_is_an_explicit_stop_with_a_partial_manifest(self):
        real = C._write_all
        n_written = []

        def write_all(fd, data):
            n_written.append(1)
            if len(n_written) == 22:
                raise OSError(errno.ENOSPC, "No space left on device")
            return real(fd, data)
        with mock.patch.object(C, "_write_all", write_all):
            rc, out = self.copy_inprocess()
        self.assertEqual(rc, 6)
        man = json.loads(out)
        self.assertIn("No space left on device", man["stop"])
        self.assertEqual(len(man["created"]), 23, "a0-refs/ and the 22 files it opened, the last one partial")
        self.assertTrue((self.stage / C.SIGMA_NAME).exists(), "the partial state stays in place")
        self.assertEqual(len(list((self.stage / "a0-refs").iterdir())), 21)
        self.assertTrue(C.verify_problems(man), "a stopped manifest never verifies")

    def test_an_o_noatime_permission_error_is_exit_3(self):
        real_open = os.open

        def guarded(path, flags, *a, **k):
            if str(path).startswith(str(self.a0)) and flags & 0x40000:
                raise PermissionError(errno.EPERM, "Operation not permitted")
            return real_open(path, flags, *a, **k)
        with mock.patch.object(C.os, "O_NOATIME", 0x40000, create=True), mock.patch.object(C.os, "open", guarded):
            rc, _ = self.copy_inprocess()
        self.assertEqual(rc, 3)
        self.assert_nothing_written()


class K8SmokeBinding(Base):
    def test_the_smoke_receipt_binds_stage_pin_and_index(self):
        for over, why in (({"stage": "/pscratch/other"}, "stage"), ({"pin": "0" * 40}, "pin"),
                          ({"local_test": True}, "production"), ({"index_sha256": None}, "INDEX"),
                          ({"index_sha256": "x"}, "INDEX")):
            self.receipt(**over)
            self.assertEqual(self.copy_inprocess()[0], 2, why)
            self.assert_nothing_written()
        (self.stage / "smoke-receipt.json").write_text("not json")
        self.assertEqual(self.copy_inprocess()[0], 2)
        (self.stage / "smoke-receipt.json").unlink()
        (self.d / "r.json").write_text(json.dumps({"stage": str(self.stage), "pin": self.pin, "local_test": False,
                                                   "index_sha256": "a" * 64}))
        (self.stage / "smoke-receipt.json").symlink_to(self.d / "r.json")
        self.assertEqual(self.copy_inprocess()[0], 2, "a symlinked receipt")
        (self.stage / "smoke-receipt.json").unlink()
        os.link(self.d / "r.json", self.stage / "smoke-receipt.json")
        self.assertEqual(self.copy_inprocess()[0], 2, "a hard-linked receipt")
        (self.stage / "smoke-receipt.json").unlink()
        self.receipt()
        self.assertEqual(self.copy_inprocess()[0], 0)


class Launcher(unittest.TestCase):
    def run_launch(self, *args):
        return subprocess.run(["bash", str(LAUNCH), *args], capture_output=True, text=True,
                              env={**os.environ, "PATH": "/usr/bin:/bin"})

    def test_the_launcher_checks_its_arguments_and_hop(self):
        text = LAUNCH.read_text()
        self.assertIn(f"SHA={hashlib.sha256(REMOTE.read_bytes()).hexdigest()}\n", text)
        dep = "/pscratch/sd/j/josephrb/pfb-deploy"
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_launch(d, "saul", dep).returncode, 9)
            for bad in ("/global/homes/j/josephrb/deploy", "relative", "/pscratch/sd/j/josephrb/../x",
                        "/pscratch/sd/j/josephrb/a b"):
                r = self.run_launch(d, "login27", bad)
                self.assertEqual(r.returncode, 9, bad)
            Path(d, "x").write_text("x")
            self.assertEqual(self.run_launch(d, "login27", dep).returncode, 9)
        body = text.split("# Usage")[1]
        for word in ("sbatch", "srun", "salloc", "squeue", "/global/"):
            self.assertNotIn(word, body)
        hop = text.split("\nHOP=(", 1)[1].split(")", 1)[0]
        for opt in ("ControlPath=none", "StrictHostKeyChecking=yes", "UpdateHostKeys=no"):
            self.assertIn(opt, hop)
        self.assertIn("INNER=\"/usr/bin/python3 -I -S -c 'import sys;exec(bytes.fromhex(sys.argv[1]))' $BOOT $SHA $DEPLOY\"",
                      text)


if __name__ == "__main__":
    unittest.main()
