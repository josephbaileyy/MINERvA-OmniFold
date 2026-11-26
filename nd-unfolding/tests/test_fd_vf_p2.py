"""Tests of fd_vf_p2.py: the fetch list, the fetch connect's reader and wrapper (dry runs against a local fake tree),
the local verifier, control P, the local recomputes end to end, the xk replay's remap (rulings (i)-(iii)), the
committed prr/rsn/xk copies, and (opt-in, VF_P2_FETCH) their byte reproduction from the verified fetch."""
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
        self.assertEqual((len(rows), sum(int(r[3]) for r in rows)), (402, 1595625533))
        self.assertNotIn(P.NUE_PATH, [r[0] for r in rows])                      # held locally (binding 2b)
        self.assertEqual(P.sha256_file(REPO / P.NUE_LOCAL[0]), P.NUE_LOCAL[1])
        paths = [r[0] for r in rows]
        self.assertFalse([p for p in paths if p.endswith(("universes_full.root", "bkg_dump.npz", "data_b-_j-.npz"))])
        self.assertTrue(all(p.startswith(P.PS) for p in paths))
        self.assertEqual(sum(1 for p in paths if p.startswith(P.RUN)), 110)        # xk's own run directory
        self.assertFalse([p for p in paths if p.startswith(P.ORIGINAL)])
        self.assertIn(("/pscratch/sd/j/josephrb/fd-prr-20261108/route2/route2.npz"), paths)

    def test_a_changed_count_or_total_refuses(self):
        for k, v in (("N_ROWS", 401), ("N_BYTES", 1)):
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
        self.assertIn(b"pre-flight", r.stderr)
        self.assertIn(b"is a symlink", r.stderr)
        self.assertEqual(r.stdout, b"")                    # refused before any byte was streamed
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
        self.assertIn(b"pre-flight", r.stderr)
        self.assertIn(b"is a symlink", r.stderr)
        self.assertEqual(r.stdout, b"")
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
        self.assertEqual(r.stdout, b"")
        fifo.unlink()

    def test_the_pre_flight_lists_every_offender_before_streaming_anything(self):
        rels = list(self.f.files)
        lst = self.f.list_text()
        for rel in rels[:2]:                              # two offenders: a symlinked final file, a missing file
            q = self.f.files[rel]
            real = q.with_name(q.name + ".real")
            q.rename(real)
        q0 = self.f.files[rels[0]]
        q0.symlink_to(q0.with_name(q0.name + ".real"))
        r = subprocess.run([sys.executable, "-I", str(self.f.reader)], input=lst.encode(), capture_output=True)
        self.assertEqual(r.returncode, 9, r.stderr)
        self.assertIn(b"2 offender(s)", r.stderr)
        self.assertEqual(r.stdout, b"")

    def test_a_symlinked_base_stops(self):
        link = self.f.t / "baselink"
        link.symlink_to(self.f.base)
        src = self.f.reader.read_text().replace(f'BASE = "{self.f.base}/"', f'BASE = "{link}/"')
        rd = self.f.t / "reader2.py"
        rd.write_text(src)
        lst = self.f.list_text().replace(f"{self.f.base}/", f"{link}/")
        before = os.lstat(link).st_atime_ns
        r = subprocess.run([sys.executable, "-I", str(rd)], input=lst.encode(), capture_output=True)
        self.assertEqual(r.returncode, 9, r.stderr)
        self.assertIn(b"pre-flight, before any file was opened", r.stderr)
        self.assertIn(b"not a plain directory", r.stderr)
        self.assertEqual(r.stdout, b"")
        self.assertEqual(os.lstat(link).st_atime_ns, before)

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
        # an extension header declaring size -1 (or 0) inserted before a short-named member: tarfile reads no data
        # and yields the listed member, so only fetch-verify's own guards can refuse it
        with tarfile.open(fileobj=io.BytesIO(bytes(raw)), mode="r:") as tf:
            m0 = next(x for x in tf if x.name != long)
        for size_field in (b"\xff" * 12, b"%011o\0" % 0):
            hdr = bytearray(tarfile.TarInfo("PaxHeader").tobuf(tarfile.USTAR_FORMAT))
            hdr[156:157] = b"x"
            hdr[124:136] = size_field
            hdr[148:156] = b" " * 8
            hdr[148:156] = b"%06o\0 " % sum(hdr)
            bad = bytes(raw[:m0.offset]) + bytes(hdr) + bytes(raw[m0.offset:])
            with tarfile.open(fileobj=io.BytesIO(bad), mode="r:") as tf:     # tarfile accepts it
                self.assertIn(m0.name, [x.name for x in tf])
            self.tar.write_bytes(bad)
            self.verify()
        for rec in (b"5 =a\n", b"8 zz=yy\n"):             # an empty key; a key the reader never writes
            bad = bytearray(raw)
            assert size + len(rec) <= -(-size // 512) * 512
            bad[pos + 512 + size:pos + 512 + size + len(rec)] = rec
            bad[pos + 124:pos + 136] = b"%011o\0" % (size + len(rec))
            bad[pos + 148:pos + 156] = b" " * 8
            bad[pos + 148:pos + 156] = b"%06o\0 " % sum(bad[pos:pos + 512])
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

    def test_a_p_written_as_zero_below_the_floor_needs_the_function_below_the_floor(self):
        rec = {"chi2": 400.0, "ndf": 16, "p": 0.0, "p_below_floor": True}
        with mock.patch("sys.stdout"):
            P.p_control("x", dict(rec), dict(rec), P.RTOL_EXACT, p_fun=lambda c, n: 1e-40)
            for pv in (0.02, 1e-30, 1e-12):
                with self.assertRaises(P.Stop):
                    P.p_control("x", dict(rec), dict(rec), P.RTOL_EXACT, p_fun=lambda c, n, pv=pv: pv)
            with self.assertRaises(P.Stop):         # no floor flag: bitwise identity only
                P.p_control("x", dict(rec, p_below_floor=False), dict(rec, p_below_floor=False), P.RTOL_EXACT,
                            p_fun=lambda c, n: 1e-40)
        sys.path.insert(0, str(REPO / "nd-unfolding"))
        import fd_f0_regrade
        self.assertEqual(P.P_FLOOR, fd_f0_regrade.P_FLOOR)

    def test_gch_keeps_1e_12_on_chi2_and_the_round_trip_fields_1e_9(self):
        self.assertEqual(P.CHI2_EXACT, {"gch"})
        real = P.pinned_json

        def bad(rel_pin):
            d, h = real(rel_pin)
            if rel_pin == P.GCH:
                path, pair = next(iter(P.pair_paths(d)))
                dst = d
                for k in path.strip("/").split("/"):
                    dst = dst[k]
                dst["reported"]["total"]["chi2"] *= 1 + 5e-10
            return d, h
        with mock.patch.object(P, "pinned_json", bad), mock.patch("sys.stdout"), self.assertRaises(P.Stop):
            P.p2_compare("gch", P.GCH, real(P.VF_DP)[0])

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
        self.assertEqual(self.out["gch"]["vf_patch"]["control_P_tolerance"]["chi2"]["rtol"], 1e-12)
        for name in ("gdefs", "gnat"):
            self.assertEqual(self.out[name]["vf_patch"]["control_P_tolerance"]["chi2"]["rtol"], 1e-9, name)
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


class XkReplay(unittest.TestCase):
    """Rulings (i)-(iii) of A4 on stand-in modules: the remap, its log, the substitution and the restore."""

    def setUp(self):
        self.t = Path(tempfile.mkdtemp(prefix="vfp2-xk-"))
        (self.t / "fetch/a").mkdir(parents=True)
        (self.t / "fetch/a/x.bin").write_bytes(b"remote bytes")
        self.reads, self.committed_reads = [], []

    def tearDown(self):
        shutil.rmtree(self.t, ignore_errors=True)

    def fakes(self, paths, committed=("c/block.npz",)):
        import types
        GC, XS = types.SimpleNamespace(), types.SimpleNamespace()
        GC.read_noatime = lambda path: (self.reads.append(str(path)) or (b"local:" + str(path).encode(), True))
        XS.read_committed = lambda path: (self.committed_reads.append(str(path)) or b"committed:" + str(path).encode())

        def cmd_k(args):
            self.seen = [GC.read_noatime(q)[0] for q in paths] + [XS.read_committed(q) for q in committed]
            return 0
        XS.cmd_k = cmd_k
        return GC, XS

    def test_the_prefix_maps_to_the_fetch_and_every_read_is_logged(self):
        GC, XS = self.fakes([P.PS_PREFIX + "a/x.bin", "/elsewhere/y"])
        orig = (GC.read_noatime, XS.read_committed)
        log, calls = [], []
        self.assertEqual(P.xk_replay(XS, GC, self.t / "fetch", self.t / "run", {}, log, calls), 0)
        self.assertEqual(self.seen[0], b"remote bytes")
        self.assertEqual(self.seen[1], b"local:/elsewhere/y")              # outside the prefix: the original reader
        self.assertEqual(log, [(P.PS_PREFIX + "a/x.bin", 12, hashlib.sha256(b"remote bytes").hexdigest())])
        self.assertEqual((GC.read_noatime, XS.read_committed), orig)        # restored

    def test_a_missing_or_symlinked_fetched_file_stops_and_restores(self):
        (self.t / "fetch/a/l.bin").symlink_to(self.t / "fetch/a/x.bin")
        for name in ("missing.bin", "l.bin"):
            GC, XS = self.fakes([P.PS_PREFIX + "a/" + name])
            orig = (GC.read_noatime, XS.read_committed)
            with self.assertRaises(P.Stop):
                P.xk_replay(XS, GC, self.t / "fetch", self.t / "run", {}, [], [])
            self.assertEqual((GC.read_noatime, XS.read_committed), orig, name)

    def test_the_two_local_copies_map_to_their_committed_files(self):
        for remote, (rel, pin) in P.LOCAL_COPIES.items():
            GC, XS = self.fakes([remote])
            log = []
            P.xk_replay(XS, GC, self.t / "fetch", self.t / "run", {}, log, [])
            self.assertEqual(log[0][0], remote)
            self.assertTrue(log[0][2].startswith(pin), remote)
            self.assertEqual(self.seen[0], (REPO / rel).read_bytes())

    def test_only_the_substituted_committed_reads_change(self):
        GC, XS = self.fakes([], committed=("c/block.npz", "c/other.json"))
        calls = []
        P.xk_replay(XS, GC, self.t / "fetch", self.t / "run", {"c/block.npz": b"V_F"}, [], calls)
        self.assertEqual(self.seen, [b"V_F", b"committed:c/other.json"])
        self.assertEqual([c[0] for c in calls], ["c/block.npz", "c/other.json"])
        self.assertEqual(calls[0][1], hashlib.sha256(b"V_F").hexdigest())

    def test_the_run_directory_is_hardlinks_plus_the_committed_v0_v1_and_never_overwrites(self):
        src = self.t / "fetch/cov2d-xk-g2r-20261116/run/boot"
        src.mkdir(parents=True)
        (src / "r.json").write_text("{}")
        listing = P.xk_run_dir(self.t / "fetch", self.t / "run")
        self.assertEqual(sorted(listing), ["boot/r.json", "v0-a1/v0.json", "v1-a2/v1.json"])
        self.assertEqual(os.stat(self.t / "run/boot/r.json").st_ino, os.stat(src / "r.json").st_ino)
        self.assertEqual((self.t / "run/v0-a1/v0.json").read_bytes(), (REPO / P.XK_V0[0]).read_bytes())
        with self.assertRaises(P.Stop):
            P.xk_run_dir(self.t / "fetch", self.t / "run")

    def test_xk_tolerance_and_group_figures(self):
        self.assertEqual(P.RTOL_XK, 1e-7)
        want = {"shares": {"a": [2.0, 4.0]}, "crosses": {"b": 1.0}, "n": 3}
        with mock.patch("sys.stdout"):
            P.p_control("xk", {"shares": {"a": [2.0, 4.0 * (1 + 5e-8)]}, "crosses": {"b": 1.0}, "n": 3}, want, P.RTOL_XK)
            for bad in ({"shares": {"a": [2.0, 4.0 * (1 + 2e-7)]}, "crosses": {"b": 1.0}, "n": 3},
                        {"shares": {"a": [2.0, 4.0]}, "crosses": {"b": 1.0}, "n": 4}):
                with self.assertRaises(P.Stop):
                    P.p_control("xk", bad, want, P.RTOL_XK)
        g = P.group_stats({"shares": {"a": [2.0, 4.0 + 4e-8]}, "crosses": {"b": 1.0}}, want)
        self.assertAlmostEqual(g["shares"]["max_relative"], 1e-8, delta=1e-15)
        self.assertAlmostEqual(g["shares"]["max_over_group_magnitude"], 1e-8, delta=1e-15)
        self.assertEqual(g["crosses"]["max_relative"], 0.0)


WITH_VF = REPO / P.D5 / "fd/with-vf/p2"


class CommittedFetchCopies(unittest.TestCase):
    """The committed prr, rsn and xk V_F copies: their pins, tolerances and V_F matrix are A4's."""

    def load(self, name):
        return json.loads((WITH_VF / f"{name}.vf.json").read_text())

    def test_each_copy_pins_its_committed_readout(self):
        for name, rel_pin in (("prr", P.PRR), ("rsnregrade", P.RSN_REGRADE), ("rsn", P.RSN_READOUT), ("xk", P.XK_K)):
            vp = self.load(name)["vf_patch"]
            self.assertEqual(vp["readout"], rel_pin[0], name)
            self.assertEqual(vp["readout_sha256"], P.sha256_file(REPO / rel_pin[0]), name)
            self.assertTrue(vp["readout_sha256"].startswith(rel_pin[1]), name)

    def test_tolerances_are_a4s_and_achieved_within_them(self):
        t = self.load("prr")["vf_patch"]["control_P_tolerance"]
        self.assertEqual((t["(e)"]["rtol"], t["IBU"]["rtol"]), (P.RTOL_EXACT, P.RTOL_IBU))
        self.assertEqual((P.RTOL_EXACT, P.RTOL_IBU), (1e-12, 1e-11))
        self.assertLessEqual(t["(e)"]["achieved_max"], 1e-12)
        self.assertLessEqual(t["IBU"]["achieved_max"], 1e-11)
        for name in ("rsn", "rsnregrade"):
            t = self.load(name)["vf_patch"]["control_P_tolerance"]
            self.assertEqual(t["rtol"], 1e-12, name)
            self.assertLessEqual(t["achieved_max"], 1e-12, name)
        t = self.load("xk")["vf_patch"]["control_P_tolerance"]
        self.assertEqual(t["rtol"], 1e-7)
        self.assertLessEqual(t["achieved_max"], 1e-7)
        self.assertLessEqual(set(P.XK_GROUPS), set(t["by_group"]))
        self.assertLessEqual(max(g["max_relative"] for g in t["by_group"].values()), t["achieved_max"])

    def test_xk_substitutes_exactly_the_reported_vf_block_and_cr(self):
        vp = self.load("xk")["vf_patch"]
        self.assertEqual(len(vp["substituted"]), 2)
        # the CR substitute is p2_overlap("cr")'s record as K read it: cr.vf.json without the vf_data_product_sha256
        # that cmd_p2 adds when it writes the copy; K reads only its "quadrants" (fd_xcov_steps.py:536)
        with mock.patch("sys.stdout"):
            rec = P.p2_overlap("cr", P.CR, P.pinned_json(P.VF_DP)[0])
        sub = (json.dumps(rec, indent=1) + "\n").encode()
        self.assertIn(hashlib.sha256(sub).hexdigest(), vp["substituted"].values())
        cr = json.loads((WITH_VF / "cr.vf.json").read_text())
        self.assertEqual(json.loads(sub)["quadrants"], cr["quadrants"])
        cr["vf_patch"].pop("vf_data_product_sha256")
        self.assertEqual(json.loads(sub), cr)

    def test_prr_names_the_old_subtree_it_does_not_replace(self):
        vp = self.load("prr")["vf_patch"]
        self.assertEqual(sorted(vp["not_replaced"]), ["/table_ii_committed_beside_B0"])
        old = P.pinned_json(P.PRR)[0]["table_ii_committed_beside_B0"]
        self.assertEqual(self.load("prr")["table_ii_committed_beside_B0"], old)

    def test_fetched_inputs_are_named_by_their_exact_remote_paths(self):
        f = self.load("prr")["vf_patch"]["fetched"]
        self.assertEqual(f, {k: P.PS + v[0] for k, v in P.FETCHED.items()})
        self.assertEqual(self.load("rsnregrade")["vf_patch"]["fetched"], P.PS + P.FETCHED["s1_assembly.npz"][0])


FETCH = os.environ.get("VF_P2_FETCH")


@unittest.skipUnless(FETCH and Path(FETCH).is_dir(), "set VF_P2_FETCH to the verified fetch tree to rerun prr/rsn/xk")
class FetchRecompute(unittest.TestCase):
    """Opt-in: prr, rsn and (with VF_P2_XK=1) xk rerun from the verified fetch reproduce the committed copies byte for
    byte."""

    def test_the_committed_copies_reproduce(self):
        only = ["prr", "rsn"] + (["xk"] if os.environ.get("VF_P2_XK") == "1" else [])
        t = Path(tempfile.mkdtemp(prefix="vfp2-fetch-"))
        try:
            with mock.patch("sys.stdout"):
                self.assertEqual(run(["p2", "--only", *only, "--fetch-dir", FETCH, "--out-dir", str(t / "out")]), 0)
            got = sorted(q.name for q in (t / "out").iterdir())
            self.assertTrue(got)
            for name in got:
                self.assertEqual((t / "out" / name).read_bytes(), (WITH_VF / name).read_bytes(), name)
        finally:
            shutil.rmtree(t, ignore_errors=True)


class ReadingsControlD(unittest.TestCase):
    """vf_readings' executable control D: which changes are events, the keyed sweep, and the named rulings."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(REPO / P.D5 / "fd/receipts-vf/readings"))
        import vf_readings
        cls.R = vf_readings

    def test_events_are_weakenings_only(self):
        d = self.R.d_event
        self.assertTrue(d("/truths[name=q3]/listed", False, True))
        self.assertIsNone(d("/truths[name=q3]/listed", True, False))
        self.assertTrue(d("/x/grade/cells_abs_z_gt_2", ["R02"], ["R02", "R07"]))
        self.assertIsNone(d("/x/grade/cells_abs_z_gt_2", ["R02", "R07"], ["R02"]))
        self.assertTrue(d("/triggers/all_graded/truths_p_lt_0.01", 1, 2))
        self.assertTrue(d("/x/A3", True, False))
        self.assertTrue(d("/readings/V-ATLAS/valid", ["R00", "R01"], ["R00"]))
        self.assertTrue(d("/q/outcome", "agree", "agree below a correlation"))
        self.assertIsNone(d("/q/outcome", "agree below a correlation", "agree"))
        self.assertTrue(d("/q/outcome", "agree", "disagree"))
        self.assertTrue(d("/triggers/listed[truth=W3]/p_lt_0.01", None, True))       # a truth newly listed
        self.assertIsNone(d("/triggers/listed[truth=W3]/p_lt_0.01", True, None))     # a truth unlisted
        self.assertIsNone(d("/modes_by_chi2[0]/mode", 3, 9))                         # not a decision-rule leaf

    def test_a_reordered_record_list_is_no_change(self):
        a = {"listed": [{"truth": "q3", "cells": []}, {"truth": "A7", "cells": ["R02"]}]}
        b = {"listed": [{"truth": "A7", "cells": ["R02"]}, {"truth": "q3", "cells": []}]}
        self.assertEqual(dict(self.R.leaves(a)), dict(self.R.leaves(b)))

    def test_the_tool_exits_1_on_an_unruled_event_and_0_with_the_rulings(self):
        t = Path(tempfile.mkdtemp(prefix="vfr-"))
        saved = self.R.RULINGS
        try:
            with mock.patch("sys.stdout"):
                self.assertEqual(self.R.main(["--out-dir", str(t / "a")]), 0)
                self.R.RULINGS = saved[1:]
                self.assertEqual(self.R.main(["--out-dir", str(t / "b")]), 1)
            self.assertIn("STOP: 2 unruled", (t / "b/vf_readings.md").read_text())
        finally:
            self.R.RULINGS = saved
            shutil.rmtree(t, ignore_errors=True)

    def test_rulings_cover_only_what_they_name(self):
        r = self.R.ruling_for
        old = ["A7_nuwro", "W3", "stage0c_gibuu"]
        self.assertTrue(r("prr", "/readings/PR-3/C25/new_flags", old, old + ["q3"]))
        self.assertIsNone(r("prr", "/readings/PR-3/C25/new_flags", old, old + ["q3", "W1"]))
        self.assertIsNone(r("prr", "/readings/PR-3/K2/new_flags", old, old + ["q3"]))
        p = "/quadrants/QD/2D/printed_only_without_C_PL5D/outcome"
        for name in ("cr", "gover"):
            self.assertTrue(r(name, p, "agree", "agree below a correlation"))
        self.assertIsNone(r("cr", p, "agree", "disagree"))
        self.assertIsNone(r("cr", "/quadrants/QA/2D/printed_only_without_C_PL5D/outcome", "agree",
                            "agree below a correlation"))
        self.assertIsNone(r("cr", "/quadrants/QD/2D/outcome", "agree", "agree below a correlation"))


if __name__ == "__main__":
    unittest.main()
