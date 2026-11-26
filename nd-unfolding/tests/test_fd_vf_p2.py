"""Tests of fd_vf_p2.py: the fetch list, the fetch connect's reader and wrapper (dry runs against a local fake tree),
the local verifier, control P, and the local recomputes end to end."""
import base64
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import fd_vf_p2 as P  # noqa: E402

REPO = P.ROOT
REMOTE = REPO / P.REMOTE_PY


def run(argv):
    return P.main(argv)


class FetchList(unittest.TestCase):
    def test_the_list_is_the_mapped_one(self):
        rows = P.fetch_rows()
        self.assertEqual((len(rows), sum(int(r[3]) for r in rows)), (403, 1595650936))
        paths = [r[0] for r in rows]
        self.assertFalse([p for p in paths if p.endswith(("universes_full.root", "bkg_dump.npz", "data_b-_j-.npz"))])
        self.assertTrue(all(p.startswith(P.PS) for p in paths))
        self.assertEqual(sum(1 for p in paths if p.startswith(P.RUN)), 110)        # xk's own run directory
        self.assertFalse([p for p in paths if p.startswith(P.ORIGINAL)])
        self.assertIn(("/pscratch/sd/j/josephrb/fd-prr-20261108/route2/route2.npz"), paths)

    def test_a_changed_count_or_total_refuses(self):
        for k, v in (("N_ROWS", 402), ("N_BYTES", 1)):
            with mock.patch.object(P, k, v), self.assertRaises(P.Stop):
                P.fetch_rows()

    def test_a_pin_that_disagrees_refuses(self):
        real = P.pins

        def bad(rel, prefix=""):
            out = real(rel, prefix)
            if str(rel).endswith("NODE-SHA256.txt"):
                k = next(k for k in out if k.startswith("run/boot/"))
                out[k] = ("0" * 64, out[k][1])
            return out
        with mock.patch.object(P, "pins", bad), self.assertRaises(P.Stop):
            P.fetch_rows()

    def test_an_existing_output_refuses(self):
        with tempfile.TemporaryDirectory() as t:
            out = Path(t) / "l.tsv"
            out.write_text("x")
            with self.assertRaises(P.Stop), mock.patch("sys.stdout"):
                run(["fetch-list", "--out", str(out)])


class Fake:
    """A fake /pscratch tree: the reader with its BASE moved there, a small list of files in it."""

    def __init__(self, n=3):
        self.t = Path(tempfile.mkdtemp(prefix="vfp2-"))
        self.base = self.t / "ps/"
        self.files = {}
        for i in range(n):
            rel = f"d{i}/f{i}.bin"
            q = self.base / rel
            q.parent.mkdir(parents=True, exist_ok=True)
            q.write_bytes(os.urandom(1000 + i))
            self.files[rel] = q
        self.reader = self.t / "reader.py"
        src = REMOTE.read_text().replace('BASE = "/pscratch/sd/j/josephrb/"', f'BASE = "{self.base}/"')
        if not hasattr(os, "O_NOATIME"):          # macOS: test-only, the production reader requires it (tested below)
            src = src.replace("os.O_RDONLY | os.O_NOATIME | os.O_NOFOLLOW | os.O_NONBLOCK",
                              "os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK").replace(
                'if not hasattr(os, "O_NOATIME"):', "if False:")
        self.reader.write_text(src)

    def list_text(self, tamper=None):
        rows = ["\t".join(P.HEADER)]
        for rel, q in self.files.items():
            b = q.read_bytes()
            sha, size = hashlib.sha256(b).hexdigest(), len(b)
            if tamper == rel + ":sha":
                sha = "0" * 64
            if tamper == rel + ":size":
                size += 1
            rows.append("\t".join([f"{self.base}/{rel}", sha, "pin", str(size), "reader", "xk"]))
        return "\n".join(rows) + "\n"

    def rows(self):
        return [tuple(r.split("\t")) for r in self.list_text().splitlines()[1:]]

    def read(self, tamper=None):
        return subprocess.run([sys.executable, "-I", str(self.reader)], input=self.list_text(tamper).encode(),
                              capture_output=True)

    def close(self):
        shutil.rmtree(self.t, ignore_errors=True)


class Reader(unittest.TestCase):
    def setUp(self):
        self.f = Fake()

    def tearDown(self):
        self.f.close()

    def test_the_reader_streams_every_listed_file_and_verify_accepts_it(self):
        r = self.f.read()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(b"fetch done: 3 files", r.stderr)
        tar, lst, dest = self.f.t / "x.tar", self.f.t / "l.tsv", self.f.t / "dest"
        tar.write_bytes(r.stdout)
        lst.write_text(self.f.list_text())
        with mock.patch.object(P, "PS", f"{self.f.base}/"), mock.patch.object(P, "fetch_rows", self.f.rows):
            self.assertEqual(run(["fetch-verify", "--tar", str(tar), "--list", str(lst), "--dest", str(dest)]), 0)
        for rel, q in self.f.files.items():
            self.assertEqual((dest / rel).read_bytes(), q.read_bytes())

    def test_a_size_or_sha_that_is_not_the_lists_stops(self):
        rel = next(iter(self.f.files))
        for t in (rel + ":size", rel + ":sha"):
            r = self.f.read(t)
            self.assertEqual(r.returncode, 9, t)
            self.assertIn(b"STOP fetch", r.stderr)

    def test_a_listed_symlink_or_an_excluded_name_stops(self):
        rel = next(iter(self.f.files))
        q = self.f.files[rel]
        real = q.with_name("real.bin")
        q.rename(real)
        q.symlink_to(real)
        lst = self.f.list_text().replace(f"\t{len(b'')}\t", "\t")      # sizes/shas follow the link target
        r = subprocess.run([sys.executable, "-I", str(self.f.reader)], input=lst.encode(), capture_output=True)
        self.assertEqual(r.returncode, 9, r.stderr)
        self.assertIn(b"O_NOFOLLOW", r.stderr)
        q.unlink()
        real.rename(q)
        bad = self.f.list_text().replace(f"{self.f.base}/d0/f0.bin", f"{self.f.base}/d0/universes_full.root")
        r = subprocess.run([sys.executable, "-I", str(self.f.reader)], input=bad.encode(), capture_output=True)
        self.assertEqual(r.returncode, 9)
        self.assertIn(b"never reads", r.stderr)

    def test_a_symlinked_parent_directory_or_a_fifo_stops(self):
        rel = next(iter(self.f.files))
        q = self.f.files[rel]
        d = q.parent
        lst = self.f.list_text()                          # built before the link exists: no read through it
        real = d.with_name(d.name + "-real")
        d.rename(real)
        d.symlink_to(real)
        before = os.lstat(d).st_atime_ns
        r = subprocess.run([sys.executable, "-I", str(self.f.reader)], input=lst.encode(), capture_output=True)
        self.assertEqual(r.returncode, 9, r.stderr)
        self.assertIn(b"not a plain directory", r.stderr)
        self.assertEqual(os.lstat(d).st_atime_ns, before)
        d.unlink()
        real.rename(d)
        fifo = q.with_name("fifo")
        os.mkfifo(fifo)
        lst = "\t".join(P.HEADER) + "\n" + "\t".join([str(fifo), "0" * 64, "pin", "0", "reader", "xk"]) + "\n"
        r = subprocess.run([sys.executable, "-I", str(self.f.reader)], input=lst.encode(), capture_output=True,
                           timeout=20)
        self.assertEqual(r.returncode, 9, r.stderr)
        self.assertIn(b"not a regular file", r.stderr)
        fifo.unlink()

    def test_a_symlinked_base_stops(self):
        link = self.f.t / "baselink"
        link.symlink_to(self.f.base)
        src = self.f.reader.read_text().replace(f'BASE = "{self.f.base}/"', f'BASE = "{link}/"')
        rd = self.f.t / "reader2.py"
        rd.write_text(src)
        lst = self.f.list_text().replace(f"{self.f.base}/", f"{link}/")
        r = subprocess.run([sys.executable, "-I", str(rd)], input=lst.encode(), capture_output=True)
        self.assertEqual(r.returncode, 9, r.stderr)
        self.assertIn(b"not a plain directory", r.stderr)

    def test_a_path_outside_the_base_or_a_bad_header_stops(self):
        bad = self.f.list_text().replace(f"{self.f.base}/d0", "/etc/d0")
        r = subprocess.run([sys.executable, "-I", str(self.f.reader)], input=bad.encode(), capture_output=True)
        self.assertEqual(r.returncode, 9)
        r = subprocess.run([sys.executable, "-I", str(self.f.reader)], input=b"x\ty\n", capture_output=True)
        self.assertEqual(r.returncode, 9)

    def test_the_reader_opens_with_o_noatime_and_refuses_without_it(self):
        src = REMOTE.read_text()
        self.assertIn("os.O_RDONLY | os.O_NOATIME | os.O_NOFOLLOW | os.O_NONBLOCK", src)
        self.assertIn("os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=d", src)
        if not hasattr(os, "O_NOATIME"):
            r = subprocess.run([sys.executable, "-I", str(REMOTE)], input=b"", capture_output=True)
            self.assertEqual(r.returncode, 2)
            self.assertIn(b"no O_NOATIME", r.stderr)


class Verify(unittest.TestCase):
    def setUp(self):
        self.f = Fake(2)
        self.tar, self.lst, self.dest = self.f.t / "x.tar", self.f.t / "l.tsv", self.f.t / "dest"
        self.lst.write_text(self.f.list_text())

    def tearDown(self):
        self.f.close()

    def write_tar(self, members):
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as t:
            for name, data, kind in members:
                ti = tarfile.TarInfo(name)
                if kind == "sym":
                    ti.type, ti.linkname = tarfile.SYMTYPE, "/etc/passwd"
                    t.addfile(ti)
                else:
                    ti.size = len(data)
                    t.addfile(ti, io.BytesIO(data))
        self.tar.write_bytes(buf.getvalue())

    def verify(self):
        with mock.patch.object(P, "PS", f"{self.f.base}/"), mock.patch.object(P, "fetch_rows", self.f.rows), \
                self.assertRaises(P.Stop):
            run(["fetch-verify", "--tar", str(self.tar), "--list", str(self.lst), "--dest", str(self.dest)])
        shutil.rmtree(self.dest, ignore_errors=True)

    def good(self):
        return [(rel, q.read_bytes(), "file") for rel, q in self.f.files.items()]

    def test_extra_missing_tampered_or_linked_members_refuse(self):
        g = self.good()
        for members in (g + [("extra.bin", b"x", "file")], g[:1], [(g[0][0], b"tampered", "file"), g[1]],
                        g + [("d0/link", b"", "sym")], [("../x", b"x", "file")] + g):
            self.write_tar(members)
            self.verify()

    def test_same_length_tampering_and_a_listed_name_symlink_refuse(self):
        g = self.good()
        n0, d0, _ = g[0]
        self.write_tar([(n0, bytes([d0[0] ^ 1]) + d0[1:], "file"), g[1]])
        self.verify()
        self.write_tar([(n0, b"", "sym"), g[1]])
        self.verify()

    def test_a_malformed_or_concatenated_tar_refuses(self):
        self.write_tar(self.good())
        raw = self.tar.read_bytes()
        last_end = max(i for i in range(0, len(raw), 512) if raw[i:i + 512] != bytes(512)) + 512
        for bad in (raw[:last_end],                                   # no end blocks
                    raw[:last_end] + b"garbage" + bytes(2048),        # a corrupt next header
                    raw + raw):                                        # a second archive after the terminator
            self.tar.write_bytes(bad)
            self.verify()

    def test_a_list_that_is_not_the_bound_one_refuses(self):
        self.write_tar(self.good())
        good = self.lst.read_bytes()
        for bad in (good.replace(b"\n", b"\r\n"), good + good.split(b"\n", 1)[1]):
            self.lst.write_bytes(bad)
            self.verify()
        self.lst.write_bytes(good)

    def test_nonzero_pax_extension_padding_refuses(self):
        long = "d" + "x" * 120 + "/f.bin"                 # longer than 100 bytes: a PAX extension record
        q = self.f.base / long
        q.parent.mkdir(parents=True)
        q.write_bytes(b"payload")
        self.f.files[long] = q
        self.lst.write_text(self.f.list_text())
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w", format=tarfile.PAX_FORMAT) as t:
            for rel, qq in self.f.files.items():
                ti = tarfile.TarInfo(rel)
                ti.size = qq.stat().st_size
                t.addfile(ti, io.BytesIO(qq.read_bytes()))
        raw = bytearray(buf.getvalue())
        self.tar.write_bytes(bytes(raw))
        with mock.patch.object(P, "PS", f"{self.f.base}/"), mock.patch.object(P, "fetch_rows", self.f.rows):
            self.assertEqual(run(["fetch-verify", "--tar", str(self.tar), "--list", str(self.lst), "--dest",
                                  str(self.dest)]), 0)
        shutil.rmtree(self.dest)
        with tarfile.open(fileobj=io.BytesIO(bytes(raw)), mode="r:") as tf:
            m = next(x for x in tf if x.name == long)
        pos = m.offset                                    # the member's first header: its PAX extension
        self.assertEqual(raw[pos + 156:pos + 157], b"x")
        size = tarfile.TarInfo.frombuf(bytes(raw[pos:pos + 512]), tarfile.ENCODING, "surrogateescape").size
        bad = bytearray(raw)
        bad[pos + 512 + size + 1] = 1
        self.tar.write_bytes(bytes(bad))
        self.verify()
        bad = bytearray(raw)                # a complete record, then a NUL and garbage inside the declared size
        assert size + 3 <= -(-size // 512) * 512
        bad[pos + 512 + size:pos + 512 + size + 3] = b"\0zz"
        bad[pos + 124:pos + 136] = b"%011o\0" % (size + 3)
        bad[pos + 148:pos + 156] = b" " * 8
        bad[pos + 148:pos + 156] = b"%06o\0 " % sum(bad[pos:pos + 512])
        with tarfile.open(fileobj=io.BytesIO(bytes(bad)), mode="r:") as tf:     # tarfile itself accepts it
            self.assertIn(long, [x.name for x in tf])
        self.tar.write_bytes(bytes(bad))
        self.verify()

    def test_nonzero_padding_after_a_member_refuses(self):
        self.write_tar(self.good())
        raw = bytearray(self.tar.read_bytes())
        with tarfile.open(fileobj=io.BytesIO(bytes(raw)), mode="r:") as tf:
            last = list(tf)[-1]
        raw[last.offset_data + last.size] = 1
        self.tar.write_bytes(bytes(raw))
        self.verify()

    def test_the_good_tar_is_accepted(self):
        self.write_tar(self.good())
        with mock.patch.object(P, "PS", f"{self.f.base}/"), mock.patch.object(P, "fetch_rows", self.f.rows):
            self.assertEqual(run(["fetch-verify", "--tar", str(self.tar), "--list", str(self.lst), "--dest",
                                  str(self.dest)]), 0)

    def test_an_existing_destination_refuses(self):
        self.write_tar(self.good())
        self.dest.mkdir()
        self.verify()


class Wrapper(unittest.TestCase):
    """The wrapper's gates, run locally with shims for hostname, sha256sum and /usr/bin/python3's path."""

    def setUp(self):
        self.f = Fake(2)
        self.t = self.f.t
        self.bin = self.t / "bin"
        self.bin.mkdir()
        for name, body in (("hostname", 'echo "${FAKE_HOST:-login02}"'), ("sha256sum", 'shasum -a 256 "$@"')):
            (self.bin / name).write_text(f"#!/bin/bash\n{body}\n")
            (self.bin / name).chmod(0o755)
        lst = self.t / "l.tsv"
        lst.write_text(self.f.list_text())
        self.lst = lst

    def tearDown(self):
        self.f.close()

    def wrapper(self, mutate=None):
        out = self.t / "w.sh"
        out.unlink(missing_ok=True)                       # the test's own previous wrapper
        with mock.patch.object(P, "REMOTE_PY", self.f.reader), mock.patch.object(P, "fetch_rows", self.f.rows), \
                mock.patch("sys.stderr"):
            P.cmd_fetch_script(P.build_args(["fetch-script", "--list", str(self.lst), "--out", str(out)]))
        s = out.read_text().replace("/usr/bin/python3", sys.executable)
        if mutate:
            s = mutate(s)
        out.write_text(s)
        return out

    def run_w(self, w, **env):
        e = {"PATH": f"{self.bin}:/usr/bin:/bin", **env}
        return subprocess.run(["bash", str(w)], capture_output=True, env=e)

    def test_the_wrapper_streams_the_tar(self):
        r = self.run_w(self.wrapper())
        self.assertEqual(r.returncode, 0, r.stderr)
        with tarfile.open(fileobj=io.BytesIO(r.stdout), mode="r|") as t:
            self.assertEqual(sorted(m.name for m in t), sorted(self.f.files))

    def test_another_host_refuses_before_any_read_even_with_an_inherited_stop_rc(self):
        for env in ({}, {"STOP_RC": "0"}):
            r = self.run_w(self.wrapper(), FAKE_HOST="login37", **env)
            self.assertEqual((r.returncode, r.stdout), (2, b""), env)

    def test_a_payload_with_an_added_trailing_byte_refuses(self):
        import base64 as b64
        for field in ("PYB", "LISTB"):
            for extra in (b"\n", b"\0"):
                def m(s, field=field, extra=extra):
                    i = s.index(f"{field}='") + len(field) + 2
                    j = s.index("'", i)
                    return s[:i] + b64.b64encode(b64.b64decode(s[i:j]) + extra).decode() + s[j:]
                r = self.run_w(self.wrapper(m))
                self.assertEqual((r.returncode, r.stdout), (2, b""), (field, extra))

    def test_a_crlf_list_refuses(self):
        self.lst.write_bytes(self.f.list_text().replace("\n", "\r\n").encode())
        with self.assertRaises(P.Stop):
            self.wrapper()

    def test_a_list_that_is_not_fetch_lists_refuses(self):
        self.lst.write_text(self.f.list_text().replace("\txk\n", "\tprr\n", 1))
        with self.assertRaises(P.Stop):
            self.wrapper()

    def test_a_tampered_payload_refuses(self):
        for field in ("PYB", "LISTB"):
            def m(s, field=field):
                i = s.index(f"{field}='") + len(field) + 2
                c = "A" if s[i + 40] != "A" else "B"
                return s[:i + 40] + c + s[i + 41:]
            r = self.run_w(self.wrapper(m))
            self.assertEqual(r.returncode, 2, (field, r.stderr))
            self.assertEqual(r.stdout, b"")

    def test_the_wrapper_writes_no_file_and_uses_no_here_document(self):
        s = self.wrapper().read_text()
        self.assertNotIn("<<", s)
        self.assertNotIn(">/", s.replace(">&2", ""))


class Control(unittest.TestCase):
    def test_p_refuses_a_value_off_by_more_than_its_tolerance(self):
        P.p_control("x", {"a": 1.0, "b": [2.0]}, {"a": 1.0, "b": [2.0]})
        for got in ({"a": 1.0 + 1e-15, "b": [2.0]}, {"a": 1.0, "b": [2.0, 3.0]}, {"a": 1.0}):
            with self.assertRaises(P.Stop), mock.patch("sys.stdout"):
                P.p_control("x", got, {"a": 1.0, "b": [2.0]})
        with mock.patch("sys.stdout"):
            P.p_control("x", {"a": 1.0 + 5e-10}, {"a": 1.0}, 1e-9)
        with self.assertRaises(P.Stop), mock.patch("sys.stdout"):
            P.p_control("x", {"a": 1.0 + 2e-9}, {"a": 1.0}, 1e-9)

    def test_printed_p_tells_apart_what_the_note_prints(self):
        self.assertEqual(P.printed_p(1.23e-5), P.printed_p(1.2300000001e-5))
        self.assertNotEqual(P.printed_p(1.24e-5), P.printed_p(1.26e-5))


class Recompute(unittest.TestCase):
    """The local recomputes: each passes P on the OLD matrix, then writes its V_F copy with vf_patch."""

    @classmethod
    def setUpClass(cls):
        cls.t = Path(tempfile.mkdtemp(prefix="vfp2-out-"))
        with mock.patch("sys.stdout"):
            assert run(["p2", "--out-dir", str(cls.t / "out")]) == 0
        cls.out = {p.stem.split(".")[0]: json.loads(p.read_text()) for p in (cls.t / "out").glob("*.vf.json")}
        for q in (cls.t / "out").glob("*.vf.txt"):
            txt = q.read_text()
            cls.out[q.stem.split(".")[0]] = json.loads(txt[txt.index("\n{") + 1:])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.t, ignore_errors=True)

    def test_every_local_recompute_wrote_a_copy_that_passed_p(self):
        self.assertEqual(sorted(self.out), sorted(P.P2))
        for name, r in self.out.items():
            self.assertEqual(r["vf_patch"]["control_P"], "PASS", name)
            self.assertTrue(r["vf_patch"]["replaced"], name)

    def test_the_round_trip_tolerance_is_a4s_and_used_only_where_named(self):
        self.assertEqual(P.RTOL_ROUNDTRIP, 1e-9)
        for name in ("eav", "gover", "cr", "vatlas"):
            tol = self.out[name]["vf_patch"].get("control_P_tolerance", {})
            self.assertNotEqual(tol.get("rtol"), 1e-9, name)

    def test_the_table_iv_corner_is_phase_1s_stage_g(self):
        g = self.out["gdefs"]
        sg = {q["name"]: q for q in P.pinned_json(P.E1_VF["with"])[0]["predictions"]}
        for n in ("genie_cv", "genie_mec", "nuwro", "gibuu"):
            rec = g["generators"][n]["CH"]["analysis_definitions"]["chi2"]["reported"]
            self.assertEqual(rec["total"]["chi2"], sg[n]["total"]["chi2"])
            self.assertEqual(g["table_2x2"][n]["CH"]["analysis_definitions"]["reported"]["total"], sg[n]["total"]["chi2"])

    def test_a_larger_matrix_never_raises_a_chi2(self):
        for name in ("gdefs", "gch", "gnat"):
            old = P.pinned_json({"gdefs": P.GDEFS, "gch": P.GCH, "gnat": P.GNAT}[name])[0]
            for path, pair in P.pair_paths(old):
                dst = self.out[name]
                for k in path.strip("/").split("/"):
                    dst = dst[k]
                for k in P.PAIR:
                    for part in ("total", "shape_only"):
                        self.assertLessEqual(dst[k][part]["chi2"], pair[k][part]["chi2"], (name, path, k, part))

    def test_a_perturbed_committed_value_refuses_p(self):
        real = P.pinned_json

        def bad(rel_pin):
            d, h = real(rel_pin)
            if rel_pin == P.GOVER:
                q = next(iter(d["quadrants"]))
                d["quadrants"][q]["sigma16_reported"] *= 1 + 1e-9
            return d, h
        with mock.patch.object(P, "pinned_json", bad), mock.patch("sys.stdout"), self.assertRaises(P.Stop):
            P.p2_overlap("gover", P.GOVER, real(P.VF_DP)[0])


if __name__ == "__main__":
    unittest.main()
