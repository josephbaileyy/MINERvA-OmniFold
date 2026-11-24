"""Tests for covfix_seal, covfix_pg and covfix_sealcheck (COVFIX-DECLARATION.md rev 11.4 section 4.2). Real gpg on
synthetic files; a fake generator stands in for tune-generator's command. No secret of the study is used.

  python3 -B -m unittest -v test_covfix_seal.py
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import covfix_pg as pg
import covfix_seal as cs
import covfix_sealcheck as sc

PW = "a" * 64                      # a synthetic passphrase
BASE = 1_234_567_890
FRAME = f"{PW}\n{BASE}\n".encode()
ATT = "0123456789abcdef0123456789abcdef"
DECLARED_ENCRYPT = ("gpg --batch --yes --pinentry-mode loopback --passphrase-fd 3 --no-symkey-cache --symmetric "
                    "--cipher-algo AES256 --s2k-digest-algo SHA512 --force-mdc")
DECLARED_DECRYPT = "gpg --batch --pinentry-mode loopback --passphrase-fd 3 --no-symkey-cache --decrypt"

GEN = r'''#!{py}
import json, os, sys
a = sys.argv
w = a[a.index("--workdir") + 1]
seeds = json.load(open(a[a.index("--seeds") + 1]))
mode = os.environ.get("FAKE_MODE", "ok")
open(os.path.join(w, "marker"), "w").write("ran")
os.makedirs(os.path.join(w, "out", "G21"), exist_ok=True)
open(os.path.join(w, "out", "G21", "ratio.json"), "w").write(json.dumps({{"f_MEC": 0.1234, "k": 1.07}}))
open(os.path.join(w, "env.json"), "w").write(json.dumps(sorted(os.environ)))
open(os.path.join(w, "tmpdir.txt"), "w").write(os.environ.get("TMPDIR", ""))
open(os.path.join(w, "seen_seeds.json"), "w").write(json.dumps(seeds))
print("convert: f_MEC=0.1234 p=0.5 n_in_grid=42")
print("gevgen log line", file=sys.stderr)
if mode != "noproducts":
    open(os.path.join(w, "PRODUCTS.json"), "w").write(json.dumps(["out/G21/ratio.json"]))
if mode == "symlink":
    os.symlink("/etc/hosts", os.path.join(w, "link"))
if mode == "leak":
    open(os.path.join(os.environ["SCRATCH"], "tmp", "leak.json"), "w").write(
        open(os.path.join(w, "out", "G21", "ratio.json")).read())
open(os.path.join(w, "genie-mcjob-%d.status" % seeds["tunes"][1]["task_seeds"][6]), "w").write("done")
sys.exit(3 if mode == "fail" else 0)
'''


def write_gen(d: Path) -> Path:
    p = d / "gen.py"
    p.write_text(GEN.format(py=sys.executable))
    p.chmod(p.stat().st_mode | stat.S_IXUSR)
    return p


def write_spec(d: Path, gen: Path, sha: str | None = None, env_keep=("FAKE_MODE", "PATH")) -> Path:
    s = d / "spec.json"
    s.write_text(json.dumps({"command": [str(gen)], "command_sha256": sha or hashlib.sha256(gen.read_bytes()).hexdigest(),
                             "tunes": ["G21_11b_00_000", "G18_02b_02_11b"], "env_keep": list(env_keep)}))
    return s


SEED_RANGE = (1_000_000_000, 2_000_020_063)


def published_problems(text: str, rels: list[str]) -> list[str]:
    """Any W path component, or any decimal token in the seed range, in published text."""
    comps = {c for r in rels for c in r.split("/")}
    out = []
    for tok in re.findall(r"[A-Za-z0-9_.\-]+", text):
        if tok in comps or tok.removesuffix(".gpg") in comps:
            out.append(f"path component {tok}")
    for m in re.finditer(r"(?<![0-9a-f])[0-9]{10}(?![0-9a-f])", text):
        if SEED_RANGE[0] <= int(m.group()) <= SEED_RANGE[1]:
            out.append(f"seed-range decimal {m.group()}")
    return out


class Frame(unittest.TestCase):
    def test_pg_frame(self):
        self.assertEqual(cs.read_frame(FRAME, True), (PW, BASE))

    def test_pg_frame_refusals(self):
        for bad in (f"{PW.upper()}\n{BASE}\n", f"{PW}\n{BASE}", f"{PW}\n{BASE}\n\n", f"{PW}\n0{BASE}\n",
                    f"{PW[:-1]}\n{BASE}\n", f"{PW}\n999999999\n", f"{PW}\n2000000000\n", f"{PW}\n"):
            with self.subTest(bad=bad[-14:]), self.assertRaises(cs.Refusal):
                cs.read_frame(bad.encode(), True)

    def test_pv_frame(self):
        self.assertEqual(cs.read_frame(f"{PW}\n".encode(), False), (PW, None))
        with self.assertRaises(cs.Refusal):
            cs.read_frame(FRAME, False)

    def test_seed_range_edges(self):
        self.assertEqual(cs.read_frame(f"{PW}\n1000000000\n".encode(), True)[1], 1_000_000_000)
        self.assertEqual(cs.read_frame(f"{PW}\n1999999999\n".encode(), True)[1], 1_999_999_999)


class Seeds(unittest.TestCase):
    def test_formula(self):
        s = cs.task_seeds(BASE, ["A", "B"])["tunes"]
        self.assertEqual([t["u"] for t in s], [0, 1])
        self.assertEqual(s[0]["task_seeds"], [BASE + i for i in range(7)])
        self.assertEqual(s[1]["task_seeds"], [BASE + 10_000 + i for i in range(7)])

    def test_declared_maximum_is_below_the_limit(self):
        top = cs.task_seeds(1_999_999_999, ["A", "B"])["tunes"][1]["task_seeds"][-1]
        self.assertEqual(top, 2_000_010_005)
        self.assertLess(top, 2 ** 31 - 1)

    def test_limit_refused(self):
        with self.assertRaises(cs.Refusal):
            cs.task_seeds(2 ** 31 - 1 - 10_006, ["A", "B"])     # u=1, i=6 reaches exactly 2^31 - 1
        cs.task_seeds(2 ** 31 - 1 - 10_007, ["A", "B"])         # one below: accepted


class Gpg(unittest.TestCase):
    def test_declared_flags(self):
        self.assertEqual(" ".join(cs.GPG_ENCRYPT), DECLARED_ENCRYPT)
        self.assertEqual(" ".join(cs.GPG_DECRYPT), DECLARED_DECRYPT)

    def test_round_trip_and_wrong_passphrase(self):
        ct = cs.gpg_run(cs.GPG_ENCRYPT, PW, b"payload")
        self.assertNotIn(b"payload", ct)
        self.assertEqual(cs.gpg_run(cs.GPG_DECRYPT, PW, ct), b"payload")
        with self.assertRaises(cs.Refusal):
            cs.gpg_run(cs.GPG_DECRYPT, "b" * 64, ct)

    def test_gnupg_home_short_node_local_and_removed(self):
        made = []
        real = cs.new_gnupg_home

        def spy():
            h = real()
            made.append((h, stat.S_IMODE(os.stat(h).st_mode)))
            return h
        with tempfile.TemporaryDirectory() as home, mock.patch.dict(os.environ, {"HOME": home, "TMPDIR": "/" + "x" * 120}), \
                mock.patch.object(cs, "new_gnupg_home", spy):
            cs.gpg_run(cs.GPG_DECRYPT, PW, cs.gpg_run(cs.GPG_ENCRYPT, PW, b"p"))
            self.assertFalse(os.path.exists(os.path.join(home, ".gnupg")))     # ~/.gnupg never created
        for h, mode in made:
            self.assertLess(len(h), 80)
            self.assertEqual(mode, 0o700)
            self.assertTrue(h.startswith(("/dev/shm/", "/tmp/")))
            self.assertFalse(os.path.exists(h))                                # removed after use

    def test_passphrase_pipe_on_fd_3(self):
        saved = os.dup(3) if self._fd_open(3) else None
        try:
            if saved is not None:
                os.close(3)
            ct = cs.gpg_run(cs.GPG_ENCRYPT, PW, b"fd3")                 # os.pipe() now returns fd 3 for the read end
            self.assertEqual(cs.gpg_run(cs.GPG_DECRYPT, PW, ct), b"fd3")
        finally:
            if saved is not None:
                os.dup2(saved, 3)
                os.close(saved)

    @staticmethod
    def _fd_open(fd):
        try:
            os.fstat(fd)
            return True
        except OSError:
            return False

    def test_long_home_refused(self):
        with mock.patch.object(cs.tempfile, "mkdtemp", return_value="/tmp/" + "y" * 80), \
                mock.patch.object(cs.os, "chmod"), mock.patch.object(cs.shutil, "rmtree") as rm:
            with self.assertRaises(cs.Refusal):
                cs.new_gnupg_home()
            rm.assert_called_once()

    def test_tampered_ciphertext_refused(self):
        ct = bytearray(cs.gpg_run(cs.GPG_ENCRYPT, PW, b"payload" * 100))
        ct[-5] ^= 0xFF
        with self.assertRaises(cs.Refusal):
            cs.gpg_run(cs.GPG_DECRYPT, PW, bytes(ct))


class Base(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.d = Path(self._td.name)
        self.w = self.d / "w"
        self.w.mkdir()
        self.s = self.d / "sealed"

    def tearDown(self):
        self._td.cleanup()

    def files(self, **kw):
        for rel, data in kw.items():
            p = self.w / rel.replace("__", "/")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)


class Seal(Base):
    def test_seal_layout_manifest_and_seal_file(self):
        self.files(a=b"alpha", sub__b=b"beta")
        r = cs.seal(self.w, self.s, PW)
        self.assertEqual(r["n_products"], 2)
        self.assertEqual(r["hashes"], {"p0001": hashlib.sha256(b"alpha").hexdigest(),
                                       "p0002": hashlib.sha256(b"beta").hexdigest()})
        man = json.loads(cs.gpg_run(cs.GPG_DECRYPT, PW, (self.s / "PG-MANIFEST.json.gpg").read_bytes()))
        self.assertEqual(man, {"products": r["hashes"], "paths": {"p0001": "a", "p0002": "sub/b"}})
        for name, want in man["products"].items():                        # the reference role's loop
            plain = cs.gpg_run(cs.GPG_DECRYPT, PW, (self.s / (name + ".gpg")).read_bytes())
            self.assertEqual(hashlib.sha256(plain).hexdigest(), want)
        lines = (self.s / "PG-SEAL.sha256").read_text().splitlines()
        names = [ln.split("  ", 1)[1] for ln in lines]
        self.assertEqual(names, sorted(["p0001.gpg", "p0002.gpg", "PG-MANIFEST.json.gpg"]))
        self.assertEqual(sorted(os.listdir(self.s)), sorted(["p0001.gpg", "p0002.gpg", "PG-MANIFEST.json.gpg",
                                                             "PG-SEAL.sha256"]))
        for ln in lines:
            h, name = ln.split("  ", 1)
            self.assertEqual(hashlib.sha256((self.s / name).read_bytes()).hexdigest(), h)
        self.assertNotIn(r["hashes"]["p0001"], (self.s / "PG-SEAL.sha256").read_text())   # plaintext hashes unpublished
        self.assertEqual(cs.content_scan([self.s], set(r["hashes"].values())), [])

    def test_break_on_round_trip_mismatch(self):
        self.files(a=b"alpha")
        real = cs.gpg_run

        def fake(argv, pw, payload, gpg="gpg"):
            out = real(argv, pw, payload, gpg)
            return out + b"x" if argv is cs.GPG_DECRYPT else out
        with mock.patch.object(cs, "gpg_run", fake), self.assertRaises(cs.Break):
            cs.seal(self.w, self.s, PW)

    def test_break_on_a_product_round_trip_alone(self):
        self.files(a=b"alpha", b=b"beta")
        real = cs.gpg_run
        calls = {"n": 0}

        def fake(argv, pw, payload, gpg="gpg"):
            out = real(argv, pw, payload, gpg)
            if argv is cs.GPG_DECRYPT:
                calls["n"] += 1
                if calls["n"] == 1:                                       # the first product only
                    return out + b"x"
            return out
        with mock.patch.object(cs, "gpg_run", fake), self.assertRaises(cs.Break):
            cs.seal(self.w, self.s, PW)

    def test_break_on_manifest_mismatch(self):
        self.files(a=b"alpha")
        real = cs.gpg_run
        calls = {"n": 0}

        def fake(argv, pw, payload, gpg="gpg"):
            out = real(argv, pw, payload, gpg)
            if argv is cs.GPG_DECRYPT:
                calls["n"] += 1
                if calls["n"] == 2:                                       # the manifest's decrypt
                    return out + b" "
            return out
        with mock.patch.object(cs, "gpg_run", fake), self.assertRaises(cs.Break):
            cs.seal(self.w, self.s, PW)

    def test_refusals(self):
        with self.assertRaises(cs.Refusal):
            cs.seal(self.w, self.s, PW)                                   # empty
        os.symlink("/etc/hosts", self.w / "l")
        with self.assertRaises(cs.Refusal) as e:
            cs.seal(self.w, self.d / "s3", PW)
        self.assertNotIn("l", str(e.exception).split())                   # no work-dir name in the message
        with self.assertRaises(cs.Refusal):
            cs.product_ids(10_000)
        self.assertEqual(cs.product_ids(2), ["p0001", "p0002"])

    def test_a_product_named_like_the_manifest_is_just_an_id(self):
        self.files(**{"PG-MANIFEST.json": b"x"})
        r = cs.seal(self.w, self.s, PW)
        self.assertEqual(list(r["hashes"]), ["p0001"])

    def test_nothing_published_names_a_path_or_a_seed(self):
        seed = 1_999_999_999 + 10_006
        self.files(**{f"genie-mcjob-{seed}.status": b"s", "G18_02b_02_11b__gntp.1999999999.gst.root": b"g"})
        cs.seal(self.w, self.s, PW)
        rels = cs.enumerate_files(self.w)
        published = (self.s / "PG-SEAL.sha256").read_text() + "\n".join(cs.enumerate_files(self.s))
        self.assertEqual(published_problems(published, rels), [])
        self.assertTrue(published_problems(f"x genie-mcjob-{seed}.status", rels))   # the check itself bites
        self.assertTrue(published_problems("gntp.1999999999.gst.root", ["gntp.1999999999.gst.root"]))

    def test_existing_ciphertext_not_overwritten(self):
        self.files(a=b"alpha")
        (self.s).mkdir()
        (self.s / "p0001.gpg").write_bytes(b"old")
        with self.assertRaises(FileExistsError):
            cs.seal(self.w, self.s, PW)

    def test_delete_plaintext(self):
        self.files(a=b"1", sub__deep__b=b"2")
        os.symlink("/etc/hosts", self.w / "l")
        os.symlink("/etc", self.w / "dl")
        self.assertEqual(cs.delete_plaintext(self.w), 4)
        self.assertEqual(list(self.w.iterdir()), [])
        self.assertTrue(Path("/etc/hosts").exists())

    def test_content_scan_skips_a_special_root(self):
        fifo = self.d / "fifo"
        os.mkfifo(fifo)
        self.assertEqual(cs.content_scan([fifo], {"0" * 64}), [])

    def test_content_scan(self):
        self.files(a=b"alpha", b=b"beta")
        os.symlink(self.w / "b", self.w / "lnk")
        hits = cs.content_scan([self.w, self.d / "nowhere", self.w / "b"], {hashlib.sha256(b"beta").hexdigest()})
        self.assertEqual(hits, [str(self.w / "b"), str(self.w / "b")])          # a file root is scanned; links skipped


class SealCheck(Base):
    def sealed(self):
        self.files(a=b"alpha", b=b"beta")
        cs.seal(self.w, self.s, PW)
        return (self.s / "PG-SEAL.sha256").read_text()

    def test_ok_missing_extra_mismatched(self):
        text = self.sealed()
        self.assertTrue(cs.seal_check(self.s, text)["ok"])
        (self.s / "extra.gpg").write_bytes(b"e")
        r = cs.seal_check(self.s, text)
        self.assertEqual((r["ok"], r["extra"]), (False, ["extra.gpg"]))
        os.remove(self.s / "extra.gpg")
        (self.s / "p0001.gpg").write_bytes(b"tampered")
        self.assertEqual(cs.seal_check(self.s, text)["mismatched"], ["p0001.gpg"])
        os.remove(self.s / "p0001.gpg")
        self.assertEqual(cs.seal_check(self.s, text)["missing"], ["p0001.gpg"])

    def test_malformed_seal(self):
        m = f"{'0' * 64}  PG-MANIFEST.json.gpg\n"
        for bad in ("nothex  a.gpg\n" + m, f"{'0' * 64}  a.gpg\n{'0' * 64}  a.gpg\n" + m, f"{'0' * 64}  a.gpg\n"):
            with self.subTest(bad=bad[:20]), self.assertRaises(cs.Refusal):
                cs.parse_seal(bad)

    def test_cli(self):
        text = self.sealed()
        sf = self.d / "seal.txt"
        sf.write_text(text)
        sha = hashlib.sha256(text.encode()).hexdigest()
        out = io.StringIO()
        self.assertEqual(sc.main(["--sealed", str(self.s), "--seal-file", str(sf), "--seal-sha256", sha], out), 0)
        self.assertTrue(json.loads(out.getvalue())["ok"])
        out = io.StringIO()
        self.assertEqual(sc.main(["--sealed", str(self.s), "--seal-file", str(sf), "--seal-sha256", "0" * 64], out), 1)
        self.assertIn("pinned", json.loads(out.getvalue())["refused"])
        out = io.StringIO()
        self.assertEqual(sc.main(["--sealed", str(self.s), "--seal-file", str(self.d / "none")], out), 1)
        self.assertFalse(json.loads(out.getvalue())["ok"])


class Reader(Base):
    def sealed(self):
        self.files(a=b"alpha", sub__b=b"beta")
        cs.seal(self.w, self.s, PW)
        return cs.parse_seal((self.s / "PG-SEAL.sha256").read_text())

    def test_reads_through_the_seal(self):
        sm = self.sealed()
        man = cs.open_manifest(self.s, sm, PW)
        self.assertEqual(man["paths"], {"p0001": "a", "p0002": "sub/b"})
        self.assertEqual(cs.read_product(self.s, sm, man, "p0002", PW), b"beta")

    def test_tampered_bytes_break_before_any_decrypt(self):
        sm = self.sealed()
        man = cs.open_manifest(self.s, sm, PW)
        (self.s / "p0001.gpg").write_bytes(b"other bytes")
        with mock.patch.object(cs, "gpg_run") as g, self.assertRaises(cs.Break):
            cs.read_product(self.s, sm, man, "p0001", PW)
        g.assert_not_called()

    def test_missing_is_a_break_unreadable_is_a_role_failure(self):
        sm = self.sealed()
        man = cs.open_manifest(self.s, sm, PW)
        os.remove(self.s / "p0001.gpg")
        with self.assertRaises(cs.Break):
            cs.read_product(self.s, sm, man, "p0001", PW)
        p = self.s / "p0002.gpg"
        p.chmod(0)
        try:
            with self.assertRaises(cs.Refusal) as e:
                cs.read_product(self.s, sm, man, "p0002", PW)
            self.assertNotIsInstance(e.exception, cs.Break)
        finally:
            p.chmod(0o600)
        with self.assertRaises(cs.Break):
            cs.read_ciphertext(self.s, sm, "p9999.gpg")                   # not in the seal

    def test_manifest_checks(self):
        sm = self.sealed()
        with self.assertRaises(cs.Refusal):
            cs.open_manifest(self.s, sm, "b" * 64)                         # wrong passphrase: a role failure
        extra = dict(sm, **{"p0003.gpg": "0" * 64})
        with self.assertRaises(cs.Break):
            cs.open_manifest(self.s, extra, PW)                            # the seal lists an id the manifest lacks
        for bad in (b"not json", json.dumps({"products": {}}).encode(), json.dumps([1]).encode()):
            with self.subTest(bad=bad[:12]):
                d = self.d / ("s" + str(abs(hash(bad))))
                d.mkdir()
                ct = cs.gpg_run(cs.GPG_ENCRYPT, PW, bad)
                (d / "PG-MANIFEST.json.gpg").write_bytes(ct)
                with self.assertRaises(cs.Break):
                    cs.open_manifest(d, {"PG-MANIFEST.json.gpg": hashlib.sha256(ct).hexdigest()}, PW)

    def test_plaintext_not_its_manifest_hash_is_a_break(self):
        sm = self.sealed()
        man = cs.open_manifest(self.s, sm, PW)
        bad = dict(man, products=dict(man["products"], p0001="0" * 64))
        with self.assertRaises(cs.Break):
            cs.read_product(self.s, sm, bad, "p0001", PW)


class PG(Base):
    def go(self, mode="ok", frame=FRAME, sha=None, attempt=ATT, env_keep=("FAKE_MODE", "PATH"), **env):
        gen = write_gen(self.d)
        spec = write_spec(self.d, gen, sha, env_keep)
        out = io.StringIO()
        with mock.patch.dict(os.environ, {"FAKE_MODE": mode, "SECRETISH": "should-not-pass", **env}):
            rc = pg.main(["--covfix-attempt", attempt, "--workdir", str(self.w), "--sealed", str(self.s),
                          "--gen-spec", str(spec)], stdin=io.BytesIO(frame), stdout=out)
        return rc, out.getvalue()

    def unseal(self, rel):
        man = json.loads(cs.gpg_run(cs.GPG_DECRYPT, PW, (self.s / "PG-MANIFEST.json.gpg").read_bytes()))
        pid = {v: k for k, v in man["paths"].items()}[rel]
        return cs.gpg_run(cs.GPG_DECRYPT, PW, (self.s / (pid + ".gpg")).read_bytes())

    def test_success(self):
        rc, out = self.go()
        self.assertEqual(rc, 0, out)
        lines = out.strip().splitlines()
        self.assertEqual(lines[-1], f"covfix-receipt {ATT}")
        summary = json.loads(lines[0])
        self.assertEqual((summary["generation_rc0"], summary["products_json"], summary["scan_hits"]), (True, True, 0))
        for secret in (PW, str(BASE), "f_MEC", "0.1234", "n_in_grid"):
            self.assertNotIn(secret, out)
        self.assertEqual(list(self.w.iterdir()), [])                      # plaintext deleted
        self.assertIn(b"f_MEC=0.1234", self.unseal("capture/stdout.log"))  # physics only inside the seal
        self.assertIn(b"gevgen log line", self.unseal("capture/stderr.log"))
        self.assertEqual(self.unseal("capture/rc.txt"), b"0\n")
        seeds = json.loads(self.unseal("seeds.json"))
        self.assertEqual(seeds, cs.task_seeds(BASE, ["G21_11b_00_000", "G18_02b_02_11b"]))
        env = json.loads(self.unseal("env.json"))
        self.assertNotIn("SECRETISH", env)
        self.assertEqual(self.unseal("tmpdir.txt").decode(), str(self.w / "tmp"))
        # LC_CTYPE: the child interpreter's own PEP 538 locale coercion, not passed by the binary
        self.assertTrue(set(env) <= {"FAKE_MODE", "PATH", "TMPDIR", "LC_CTYPE"}, env)
        self.assertEqual(published_problems((self.s / "PG-SEAL.sha256").read_text() + out,
                                            ["genie-mcjob-%d.status" % (BASE + 10_006), "seeds.json", "capture", "tmpdir.txt"]), [])
        self.assertTrue(cs.seal_check(self.s, (self.s / "PG-SEAL.sha256").read_text())["ok"])

    def test_generation_failure_still_seals(self):
        rc, out = self.go("fail")
        self.assertEqual(rc, 1)
        self.assertNotIn("covfix-receipt", out)
        self.assertFalse(json.loads(out.splitlines()[0])["generation_rc0"])
        self.assertEqual(self.unseal("capture/rc.txt"), b"3\n")
        self.assertEqual(list(self.w.iterdir()), [])

    def test_no_products_json(self):
        rc, out = self.go("noproducts")
        self.assertEqual(rc, 1)
        self.assertFalse(json.loads(out.splitlines()[0])["products_json"])

    def test_symlink_from_generator_is_refused_and_trapped(self):
        rc, out = self.go("symlink")
        self.assertEqual(rc, 1)
        s = json.loads(out.splitlines()[0])
        self.assertIn("non-regular", s["refused"])
        self.assertGreater(s["trap_deleted"], 0)
        self.assertEqual(list(self.w.iterdir()), [])

    def test_command_sha_mismatch_does_not_run(self):
        rc, out = self.go(sha="0" * 64)
        self.assertEqual(rc, 1)
        self.assertIn("sha256", json.loads(out.splitlines()[0])["refused"])
        self.assertFalse((self.w / "marker").exists())
        self.assertFalse(self.s.exists())

    def test_frame_and_attempt_refusals(self):
        rc, out = self.go(frame=f"{PW}\n".encode())
        self.assertEqual(rc, 1)
        self.assertFalse(json.loads(out.splitlines()[0])["frame_ok"])
        self.assertNotIn(PW, out)
        rc, out = self.go(attempt="XYZ")
        self.assertEqual(rc, 1)
        self.assertIn("32 lowercase hex", out)

    def test_dirs_refused(self):
        (self.w / "x").write_text("x")
        rc, out = self.go()
        self.assertIn("empty", json.loads(out.splitlines()[0])["refused"])
        os.remove(self.w / "x")
        self.s.mkdir()
        rc, out = self.go()
        self.assertIn("must not exist", json.loads(out.splitlines()[0])["refused"])

    def test_break_exit_and_line(self):
        real = cs.gpg_run

        def fake(argv, pw, payload, gpg="gpg"):
            out = real(argv, pw, payload, gpg)
            return out + b"x" if argv is cs.GPG_DECRYPT else out
        with mock.patch.object(cs, "gpg_run", fake):
            rc, out = self.go()
        self.assertEqual(rc, 66)
        self.assertEqual(out.strip().splitlines()[-1], f"covfix-break {ATT}")
        self.assertEqual(list(self.w.iterdir()), [])

    def test_scratch_tmp_leak_is_caught(self):
        st = self.d / "scratch"
        (st / "tmp").mkdir(parents=True)
        (st / "tmp" / "old").write_text("pre-existing")
        rc, out = self.go("leak", env_keep=("FAKE_MODE", "PATH", "SCRATCH"), SCRATCH=str(st))
        s = json.loads(out.splitlines()[0])
        self.assertEqual(rc, 1)
        self.assertEqual((s["scratch_tmp_new_entries"], s["scan_hits"]), (1, 1))
        self.assertNotIn("covfix-receipt", out)

    def test_trap_failure_is_recorded(self):
        with mock.patch.object(cs, "seal", side_effect=cs.Refusal("x")), \
                mock.patch.object(cs, "delete_plaintext", side_effect=OSError("busy")):
            rc, out = self.go()
        s = json.loads(out.splitlines()[0])
        self.assertEqual((rc, s["trap_deleted"]), (1, "failed"))

    def test_scan_hit_fails(self):
        with mock.patch.object(cs, "content_scan", return_value=["/x"]):
            rc, out = self.go()
        self.assertEqual(rc, 1)
        self.assertEqual(json.loads(out.splitlines()[0])["scan_hits"], 1)

    def test_spec_validation(self):
        gen = write_gen(self.d)
        good = json.loads(write_spec(self.d, gen).read_text())
        for bad in ({**good, "extra": 1}, {**good, "tunes": ["one"]}, {**good, "command": []},
                    {**good, "env_keep": ["TMPDIR"]}, {**good, "command_sha256": "x"}, [1]):
            with self.subTest(bad=str(bad)[:40]):
                p = self.d / "bad.json"
                p.write_text(json.dumps(bad))
                with self.assertRaises(cs.Refusal):
                    pg.load_spec(p)
        with self.assertRaises(cs.Refusal):
            pg.load_spec(self.d / "absent.json")
        p = self.d / "nocmd.json"
        p.write_text(json.dumps({**good, "command": [str(self.d / "absent")]}))
        with self.assertRaises(cs.Refusal):
            pg.load_spec(p)


if __name__ == "__main__":
    unittest.main()
