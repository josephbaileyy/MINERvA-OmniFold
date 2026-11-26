#!/usr/bin/env python3
"""Helpers for pg_generate.sh, COVFIX PG's generation of its two validation truths
(state/2d-closeout/covfix-20261122/COVFIX-DECLARATION.md sections 4.1-4.2). Standard library only.

  queue    --seeds W/seeds.json --out W/run/queue.txt
           validate seeds.json and write one line per gevgen task: "<tune> <seed> u<u>/t<k>". Never prints a seed:
           every refusal names the rule, not the value.
  products --workdir W --seeds W/seeds.json
           write W/PRODUCTS.json, the relative paths of the ratio files PV uses, after checking they exist, with the
           pass of every verification step (strace, slot 1's product and UPS file, every trace check).
  inventory [--workdir W]
           print the required inventory, [{"pattern": glob relative to W, "count": n}], in covfix_pg.py's gen-spec
           form (fnmatchcase, '*' crossing '/'). With --workdir, check that each pattern matches exactly n regular
           files under W, following no link, and exit 1 if not.
  publish  --workdir W --seeds W/seeds.json --schemas root-schemas.json
           the export allowlist (the inventory less the seed-bearing; any other file outside W/tmp refuses), each file
           scanned for every seed's decimal, hex and int64 forms, raw and in every ROOT object inflated (an unknown or
           unavailable codec refuses), int32 forms counted only; every gst's schema equal to B3's; then
           out/leak_scan.json and out/PG-PUBLISH-SHA256SUMS, each scanned too (RULINGS-A2.md, round 4, C4).
  leak-scan --file F --seed 123456789 [--schema]
           B3's positive control on a public-seed file.

seeds.json is {"tunes": [{"u": 0, "name": "G21_11a_00_000", "task_seeds": [7 ints]},
                         {"u": 1, "name": "G18_02a_00_000", "task_seeds": [7 ints]}]}.
Section 4.2's rule: tune u's task seed = base + 10_000 u + task index, with the base uniform in [1e9, 2e9), and no
seed at or above 2**31 - 1 (run_gevgen_v3.sh passes it to both --seed and -r). The base itself is not given, so the
checks are: u0's first seed in [1e9, 2e9); consecutive seeds within a tune; u1's first = u0's first + 10_000; every
seed below 2**31 - 1.

MEASURES: nothing. CANNOT AUTHORIZE: anything.
"""
import argparse
import fnmatch
import hashlib
import json
import mmap
import os
import re
import struct
import sys
from pathlib import Path

N_TASKS = 7
U_STRIDE = 10_000
BASE_LO, BASE_HI = 1_000_000_000, 2_000_000_000
SEED_CEIL = 2 ** 31 - 1
U0 = "G21_11a_00_000"                                   # slot 1, from a sha-pinned private copy of the product
U1 = ("G18_02a_00_000",)                                 # slot 2, from CVMFS
TRUTH = {"G21_11a_00_000": "genie_v3_g21", "G18_02a_00_000": "genie_v3_g18_02a"}   # fd_f1_prep.PG_TRUTHS keys
RUNG = "L-5D-PV"                                         # fd_f1_prep.RUNG


class Refusal(Exception):
    pass


def _int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def load_seeds(path):
    """The validated tunes, sorted by u: [(u, name, [seeds])]. Raises Refusal naming the rule only."""
    try:
        d = json.loads(Path(path).read_text())
    except (OSError, ValueError):
        raise Refusal("seeds.json is missing or not JSON") from None
    if not isinstance(d, dict) or set(d) != {"tunes"} or not isinstance(d["tunes"], list) or len(d["tunes"]) != 2:
        raise Refusal("seeds.json must be {\"tunes\": [two entries]}")
    out = []
    for t in d["tunes"]:
        if not isinstance(t, dict) or set(t) != {"u", "name", "task_seeds"}:
            raise Refusal("each tune entry must have exactly u, name and task_seeds")
        if not _int(t["u"]) or not isinstance(t["name"], str) or not isinstance(t["task_seeds"], list):
            raise Refusal("u must be an int, name a string, task_seeds a list")
        out.append((t["u"], t["name"], t["task_seeds"]))
    out.sort(key=lambda x: x[0])
    if [u for u, _, _ in out] != [0, 1]:
        raise Refusal("the tunes must be u = 0 and u = 1, once each")
    if out[0][1] != U0:
        raise Refusal(f"u0 must be {U0}")
    if out[1][1] not in U1:
        raise Refusal(f"u1 must be one of {', '.join(U1)}")
    for u, _, s in out:
        if len(s) != N_TASKS or not all(_int(x) for x in s):
            raise Refusal(f"u{u} must have {N_TASKS} integer task seeds")
        if any(b - a != 1 for a, b in zip(s, s[1:])):
            raise Refusal(f"u{u}'s task seeds are not consecutive (base + 10000 u + task index)")
        if any(x >= SEED_CEIL for x in s):
            raise Refusal(f"u{u} has a task seed at or above 2**31 - 1")
    if not BASE_LO <= out[0][2][0] < BASE_HI:
        raise Refusal("u0's first task seed is outside the declared base range [1e9, 2e9)")
    if out[1][2][0] - out[0][2][0] != U_STRIDE:
        raise Refusal("u1's first task seed is not u0's plus 10000")
    return out


def cmd_queue(a):
    tunes = load_seeds(a.seeds)
    if os.path.exists(a.out):
        raise Refusal("the queue file already exists")
    lines = [f"{name} {s} u{u}/t{k}\n" for u, name, seeds in tunes for k, s in enumerate(seeds)]
    Path(a.out).write_text("".join(lines))
    print(f"[pg_lib] queue: {len(lines)} tasks, tunes {[name for _, name, _ in tunes]}")
    return 0


def products(workdir, tunes):
    rec = {"schema": "covfix-pg-products/1", "products": []}
    for u, name, _ in tunes:
        t = TRUTH[name]
        p = {"u": u, "tune": name, "truth": t, "bridged": f"out/prep/bridged/{t}.json",
             "ratio": f"out/prep/ratios/{RUNG}/{t}.json", "prediction": f"out/gen5d/{t}_xsec5d.npz"}
        for k in ("bridged", "ratio", "prediction"):
            if not (Path(workdir) / p[k]).is_file():
                raise Refusal(f"u{u}: the {k} file is missing")
        rec["products"].append(p)
    return rec


CHECKS = ("out/tool_check_strace.json", "out/members_check_G21_11a_00_000.json", "out/dbconfig_check.json")


def inventory(tunes=None):
    """[{pattern, count}]: every file pg_generate.sh leaves under W on success, with its fixed count. Optional files
    (gntp.ghep.root, kept only after a failed gntpc) are not listed: covfix_pg.py seals them as extras."""
    tunes = tunes or [U0] + list(U1)
    req = []

    def add(p, n=1):
        req.append({"pattern": p, "count": n})
    for u, t in enumerate(tunes):
        n = TRUTH[t]
        for p in (f"out/splines/{t}_CH.xml.gz", f"out/spline_check_{t}.json", f"out/graphs_{t}.root",
                  f"out/graphs_{t}.log", f"out/gst/{n}_ALL.gst.root", f"out/gen5d/{n}_xsec5d.npz",
                  f"out/gen5d/{n}_xsec5d.meta.json", f"out/prep/bridged/{n}.json", f"out/prep/ratios/{RUNG}/{n}.json",
                  f"out/logs/reduce_{t}.log", f"out/logs/graphs_{t}.log", f"out/logs/hadd_u{u}.log",
                  f"out/logs/convert_u{u}.log", f"out/logs/env-c_u{u}.log", f"out/traces/reduce_{t}.trace",
                  f"out/traces/graphs_{t}.trace", f"out/trace_check_reduce_{t}.json", f"out/trace_check_graphs_{t}.json",
                  f"out/exe_check_{t}.json", f"run/exe_{t}.txt", f"out/logs/exe_{t}.log", f"out/reduce_check_{t}.json",
                  f"out/coverage_check_{t}.json", f"out/trace_check_coverage_{t}.json", f"out/coverage/{t}/coverage.trace",
                  f"out/logs/coverage_{t}.log", f"run/gxmlpath_{t}.txt", f"run/ld_library_path_{t}.txt", f"run/awk_{t}.txt"):
            add(p)
        for f in ("task.time", "task.log", "gevgen.log", "gntpc.log", "genie_v3.gst.root", "input-flux.root",
                  "gevgen.status", "gevgen.trace", "trace_check.json", "gntpc.trace", "trace_check_gntpc.json"):
            add(f"out/work/u{u}/t*/{f}", N_TASKS)
    for p in ("seeds.json", "PRODUCTS.json", "out/PG-SHA256SUMS", PUBLISH_SUMS, LEAK_SCAN, "out/flux_phi_t_0_100.root",
              "out/argv_check.json", "out/messenger_check.json", "out/Messenger_pg.xml", "out/revision_start.json",
              "out/revision_end.json", "out/revision_compare.json", "out/node_check.json", "out/pin_hash_start.json",
              "out/pin_hash_end.json",
              "out/prep/config-pg.json", "out/prep/f1-prep-SHA256SUMS", f"out/prep/ratios/{RUNG}/ratios.json",
              "run/queue.txt", "run/truths.txt", "run/deploy-status-before.txt", "run/deploy-status-setup.txt",
              "run/deploy-status-after.txt") + CHECKS:
        add(p)
    for lg in ("queue", "flux_and_splines", "xargs", "flux_check", "prep", "products", "sums", "trace_check",
               "tool_check_strace", "members_check", "dbconfig_check", "inventory", "env-q", "env-a1", "env-fc",
               "env-p", "env-w", "env-i", "env-l", "reduce_check", "coverage", "revision", "publish", "node", "pin_hash"):
        add(f"out/logs/{lg}.log")
    return req


def inventory_problems(workdir, req):
    files = []
    for d, dirs, names in os.walk(workdir, followlinks=False):
        for x in names:
            q = os.path.join(d, x)
            if os.path.isfile(q) and not os.path.islink(q):
                files.append(os.path.relpath(q, workdir))
    return [f"{r['pattern']}: {n} files, not {r['count']}" for r in req
            for n in [sum(fnmatch.fnmatchcase(f, r["pattern"]) for f in files)] if n != r["count"]]


def cmd_inventory(a):
    req = inventory()
    if a.workdir is None:
        print(json.dumps(req, indent=1))
        return 0
    probs = inventory_problems(a.workdir, req)
    print(json.dumps({"check": "inventory", "pass": not probs, "n_patterns": len(req), "problems": probs}))
    return 0 if not probs else 1


def cmd_products(a):
    out = Path(a.workdir) / "PRODUCTS.json"
    if out.exists():
        raise Refusal("PRODUCTS.json already exists")
    rec = products(a.workdir, load_seeds(a.seeds))
    globs = ("out/**/trace_check*.json", "out/exe_check_*.json", "out/reduce_check_*.json", "out/coverage_check_*.json",
             "out/argv_check.json", "out/messenger_check.json", "out/revision_*.json")
    checks = list(CHECKS) + sorted({str(q.relative_to(a.workdir)) for g in globs for q in Path(a.workdir).glob(g)})
    rec["checks"] = {}
    for c in checks:
        try:
            text = (Path(a.workdir) / c).read_text()
            try:
                d = json.loads(text)                            # trace checks: one JSON document
            except ValueError:
                d = json.loads(text.splitlines()[-1])           # tool and members checks: their one-line result
            ok = d.get("pass") is True
        except (OSError, ValueError, IndexError, AttributeError):
            ok = False
        rec["checks"][c] = ok
    # per tune: exe, the reduce, graphs and coverage traces, reduce and coverage checks, and each task's gevgen and gntpc
    # traces; once: the argv, the messenger, the revision at the start and the end, and their comparison
    if len(checks) != len(CHECKS) + (1 + len(U1)) * (6 + 2 * N_TASKS) + 5 or not all(rec["checks"].values()):
        raise Refusal("a verification step did not pass, or is missing")
    out.write_text(json.dumps(rec, indent=1) + "\n")
    print(f"[pg_lib] products: {len(rec['products'])} truths")
    return 0


# ------------------------------------------------------------------------- the seed (codex 11; the director's ruling)

# Files that hold the sealed seed, or could be searched for it, and so never leave W: gevgen names its outputs by the
# run number, which is the seed, so every trace and log of a task carries it; their hashes would let a reader search
# the seed space, so the published sums omit them. PG-SHA256SUMS (all files) stays in W for the seal.
SEED_BEARING = ("seeds.json", "run/queue.txt", "out/PG-SHA256SUMS", "out/work/u*/t*/gevgen.trace",
                "out/work/u*/t*/gntpc.trace", "out/work/u*/t*/gevgen.log", "out/work/u*/t*/gntpc.log",
                "out/work/u*/t*/task.log", "out/work/u*/t*/task.time", "out/work/u*/t*/gevgen.status",
                "out/work/u*/t*/gntp.ghep.root", "out/logs/*")
PUBLISH_SUMS = "out/PG-PUBLISH-SHA256SUMS"
LEAK_SCAN = "out/leak_scan.json"


def seed_forms(seed):
    """The byte strings whose presence STOPs a publication: decimal (any zero-padding contains it), hex in both cases,
    and the 8-byte integer in both byte orders (a chance match is about 28 B / 2**64: none)."""
    return sorted({str(seed).encode(), format(seed, "x").encode(), format(seed, "X").encode(),
                   struct.pack(">q", seed), struct.pack("<q", seed)})


def seed_int32_forms(seed):
    """The 4-byte forms, only counted (cov2d, the director): 28 patterns match random bytes about 28 B / 2**32 times,
    and a big-endian seed near 1.0e9 reads as a float32 in the dense kinematic range, so a hit is no evidence."""
    return sorted({struct.pack(">i", seed), struct.pack("<i", seed)})


# ROOT files: every object a TKey stores compressed is inflated and scanned too. The keys are walked from fBEGIN to
# fEND (a negative length is a free gap); a compressed object is a run of blocks, each a 9-byte header (a 2-byte
# codec, the method, 3-byte little-endian compressed and uncompressed sizes) then its bytes. Any other codec, a missing
# codec module, or a record that does not parse is a STOP: an unread object could hold a seed.

def _codec(tag, body, usize):
    import lzma
    import zlib
    try:
        if tag in (b"ZL", b"XZ"):          # the whole block is one stream, with nothing after it
            d = zlib.decompressobj() if tag == b"ZL" else lzma.LZMADecompressor()
            out = d.decompress(body)
            if not d.eof or d.unused_data:
                raise Refusal(f"root-block: a {tag.decode()} block is not exactly one complete stream")
            return out
        if tag == b"L4":
            try:
                import lz4.block
                import xxhash
            except ImportError:
                raise Refusal("root-codec-unavailable: an LZ4 block and no lz4 or xxhash module")
            if xxhash.xxh64(body[8:]).digest() != body[:8]:                    # ROOT's 8-byte XXH64 of the payload
                raise Refusal("root-block: an LZ4 block's checksum does not match")
            return lz4.block.decompress(body[8:], uncompressed_size=usize)
        if tag == b"ZS":
            try:
                import zstandard
            except ImportError:
                raise Refusal("root-codec-unavailable: a ZSTD block and no zstandard module")
            d = zstandard.ZstdDecompressor().decompressobj()
            out = d.decompress(body)
            if d.unused_data or not getattr(d, "eof", True):
                raise Refusal("root-block: a ZS block is not exactly one complete frame")
            return out
    except Refusal:
        raise
    except Exception as e:
        raise Refusal(f"root-block: a {tag.decode('latin-1')!r} block does not inflate ({type(e).__name__})")
    raise Refusal(f"root-codec: a block in codec {tag.decode('latin-1')!r}, which this scan does not read")


def _blocks(data, objlen):
    """(object, [codecs], bytes used): an object's blocks from the start of data, inflated until objlen bytes are
    out; any block that does not inflate exactly is a STOP."""
    parts, codecs, q, n = [], [], 0, 0
    while n < objlen:
        if q + 9 > len(data):
            raise Refusal("root-block: an object's blocks end early")
        tag = bytes(data[q:q + 2])
        csize = int.from_bytes(data[q + 3:q + 6], "little")
        usize = int.from_bytes(data[q + 6:q + 9], "little")
        if q + 9 + csize > len(data):
            raise Refusal("root-block: a block runs past its key")
        x = _codec(tag, bytes(data[q + 9:q + 9 + csize]), usize)
        if len(x) != usize:
            raise Refusal("root-block: a block inflates to the wrong size")
        parts.append(x)
        codecs.append(tag.decode("latin-1"))
        n += usize
        q += 9 + csize
    if n != objlen:
        raise Refusal("root-block: an object inflates to the wrong size")
    return b"".join(parts), codecs, q


TAGS = (b"ZL", b"XZ", b"L4", b"ZS")


def _freed_record(gap, j):
    """(class, name, title, object, codecs, end) of the freed key whose header begins at gap[j] (ROOT overwrote only
    its 4-byte length), or None when the bytes there are not one whole key. Its blocks are read strictly: once the
    header parses, a block that does not inflate is a STOP, as in a live key."""
    if j + 14 > len(gap):
        return None
    kv, objlen, _, keylen, _ = struct.unpack(">hiIhh", gap[j:j + 14])
    if kv not in (4, 1004) or objlen <= 0 or keylen < 26:
        return None
    o = j + 14 + (16 if kv > 1000 else 8)
    try:
        cls, o = _tstring(gap, o)
        name, o = _tstring(gap, o)
        title, o = _tstring(gap, o)
    except Refusal:
        return None
    if o - j + 4 != keylen or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_:<>, ]*", cls):
        return None
    data = gap[o:]
    if data[:2] in TAGS and len(data) >= 9 and o + 9 + int.from_bytes(data[3:6], "little") <= len(gap):
        obj, codecs, q = _blocks(data, objlen)
        return cls, name, title, obj, codecs, o + q
    if objlen <= len(data):                                  # stored as it is: its bytes were scanned raw
        return cls, name, title, bytes(data[:objlen]), [], o + objlen
    return None


def _gap_blocks(gap):
    """[(class, name, title, object, codecs)]: what a free gap still holds. A gap keeps the records it replaced:
    each whole one (its key header intact after the overwritten length) is read like a live key, with its class;
    in bytes that are no whole record, every ROOT block header whose block inflates is read too (a header that does
    not inflate is not one), and a well-formed header whose codec module is missing is a STOP."""
    out, j = [], 0
    while j < len(gap):
        r = _freed_record(gap, j)
        if r is None:
            break
        out.append(r[:5])
        j = r[5]
        if j + 4 <= len(gap):                                # the next freed record keeps its own length
            j += 4
    rest, i = gap[j:], 0
    while True:
        m = re.search(rb"ZL|XZ|L4|ZS", rest[i:])
        if not m:
            return out
        q = i + m.start()
        i = q + 1
        if q + 9 > len(rest):
            continue
        csize, usize = int.from_bytes(rest[q + 3:q + 6], "little"), int.from_bytes(rest[q + 6:q + 9], "little")
        if not csize or not usize or q + 9 + csize > len(rest):
            continue
        try:
            x = _codec(rest[q:q + 2], rest[q + 9:q + 9 + csize], usize)
        except Refusal as e:
            if str(e).startswith("root-codec-unavailable"):
                raise
            continue
        if len(x) == usize:
            out.append(("(free)", "", "", x, [rest[q:q + 2].decode()]))
            i = q + 9 + csize


def _tstring(buf, o):
    if o >= len(buf):
        raise Refusal("root-key: a key's names run past the file")
    n = buf[o]
    o += 1
    if n == 255:
        if o + 4 > len(buf):
            raise Refusal("root-key: a key's names run past the file")
        n = struct.unpack(">i", buf[o:o + 4])[0]
        o += 4
    if n < 0 or o + n > len(buf):
        raise Refusal("root-key: a key's names run past the file")
    return bytes(buf[o:o + n]).decode("latin-1"), o + n


def root_keys(path, free=True):
    """Yield (class, name, title, the object's bytes (inflated, or as stored), the codecs inflated: [] if stored):
    every live key's, and with free, what each free gap still holds (its freed records, with their classes)."""
    with open(path, "rb") as fh:
        size = os.fstat(fh.fileno()).st_size
        if size < 20:
            raise Refusal("root-header: too short for a ROOT file")
        buf = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
        try:
            if buf[:4] != b"root":
                raise Refusal("root-header: not a ROOT file")
            version, begin = struct.unpack(">ii", buf[4:12])
            end = struct.unpack(">q" if version >= 1000000 else ">i", buf[12:20 if version >= 1000000 else 16])[0]
            if not (0 < begin <= end <= size):
                raise Refusal("root-header: its key range is outside the file")
            if end != size:
                raise Refusal("root-tail: bytes follow the last key (fEND)")
            pos = begin
            while pos < end:
                if pos + 4 > end:
                    raise Refusal("root-key: a key runs past fEND")
                nbytes = struct.unpack(">i", buf[pos:pos + 4])[0]
                if nbytes < 0:              # a free gap: what it held stays in its bytes, so its old blocks are read
                    if pos - nbytes > end:
                        raise Refusal("root-gap: a free gap runs past fEND")
                    if free:
                        yield from _gap_blocks(bytes(buf[pos + 4:pos - nbytes]))
                    pos -= nbytes
                    continue
                if nbytes < 18 or pos + nbytes > end:
                    raise Refusal("root-key: a key's length is impossible")
                kv, objlen, _, keylen, _ = struct.unpack(">hiIhh", buf[pos + 4:pos + 18])
                o = pos + 18 + (16 if kv > 1000 else 8)
                cls, o = _tstring(buf, o)
                name, o = _tstring(buf, o)
                title, o = _tstring(buf, o)
                if not (o - pos <= keylen <= nbytes) or objlen < 0:
                    raise Refusal("root-key: a key header does not parse")
                data, codecs = buf[pos + keylen:pos + nbytes], []
                obj = bytes(data)
                if objlen > len(data):                        # compressed: inflate every block
                    obj, codecs, q = _blocks(data, objlen)
                    if q != len(data):                        # fNbytes is the key's header and its blocks, exactly
                        raise Refusal("root-block: a key holds bytes after its object's blocks")
                yield cls, name, title, obj, codecs
                pos += nbytes
        finally:
            buf.close()


def root_schema(path):
    """{keys: sorted [class, name, title] without the file's own records, streamer_sha256}: what B3's gst fixes."""
    keys, streamer = set(), None
    for cls, name, title, obj, _ in root_keys(path, free=False):   # live keys only: free space is no schema
        if cls == "TFile":
            continue
        keys.add((cls, name, title))
        if cls == "TList" and name == "StreamerInfo":
            streamer = hashlib.sha256(obj).hexdigest()
    return {"keys": [list(k) for k in sorted(keys)], "streamer_sha256": streamer}


def schema_problems(workdir, files, schemas):
    """[problems]: every outgoing gst has B3's gst schema (its trees, branches and streamer info), which must be set."""
    probs = []
    for rel in files:
        if not rel.endswith(".gst.root"):
            continue
        kind = "gst_merged" if fnmatch.fnmatchcase(rel, "out/gst/*_ALL.gst.root") else "gst"   # hadd's, or gntpc's
        want = (schemas or {}).get(kind)
        if not want:
            return [f"root-schema-unset: no {kind} schema is recorded from B3"]
        if root_schema(os.path.join(workdir, rel)) != want:
            probs.append(f"root-schema: {rel} differs from B3's {kind}")
    return probs


def seed_bearing(rel):
    return any(fnmatch.fnmatchcase(rel, g) for g in SEED_BEARING)


def _count(buf, forms):
    return sum(buf.count(f) for f in forms)


CONTAINERS = {b"BZh": "bzip2", b"\xfd7zXZ\x00": "xz", b"\x28\xb5\x2f\xfd": "zstd"}


def _members(p):
    """[(where, inflated bytes)] of a gzip file or every member of a zip (an npz); [] for anything else; a compressed
    container of another kind is a STOP, since its bytes cannot be read here."""
    import gzip
    import zipfile
    with open(p, "rb") as fh:
        head = fh.read(6)
    for magic, kind in CONTAINERS.items():
        if head.startswith(magic):
            raise Refusal(f"container-unread: a {kind} file, which this scan does not read")
    try:
        if head.startswith(b"\x1f\x8b"):
            with gzip.open(p, "rb") as f:
                return [("gzip", f.read())]
        if head.startswith(b"PK\x03\x04"):
            with zipfile.ZipFile(p) as z:
                return [("zip", z.read(n)) for n in z.namelist()]
    except (OSError, EOFError, zipfile.BadZipFile, NotImplementedError) as e:
        raise Refusal(f"container-unread: a compressed file does not inflate ({type(e).__name__})")
    return []


def leak_scan(workdir, files, seeds, decode_all=False):
    """([(relpath or None, where)], stats): each outgoing file whose path (None, "path": the path is not repeated),
    bytes, a ROOT object's inflated bytes, or a gzip or zip member holds a STOP form of any seed. int32 forms are a
    STOP in every ROOT object but a TBasket's payload, and only counted (against their chance expectation) in
    baskets and raw bytes. The path and the bytes are scanned apart. With decode_all (B3's positive control) a
    ROOT file is decoded even after a raw hit, and stats["hits"] names every kind found. Never prints a seed."""
    forms = [f for s in seeds for f in seed_forms(s)]
    f32 = [f for s in seeds for f in seed_int32_forms(s)]
    width = max(len(f) for f in forms + f32)
    hits, stats = [], {"files": len(files), "bytes_raw": 0, "bytes_inflated": 0, "int32_count": 0, "codecs": {},
                       "objects_int32_checked": 0}
    kinds = set()
    for rel in files:
        if any(f in rel.encode() for f in forms):
            hits.append((None, "path"))
            kinds.add("path")
        p, hit = os.path.join(workdir, rel), None
        with open(p, "rb") as fh:
            tail = b""
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                buf = tail + chunk
                stats["bytes_raw"] += len(chunk)
                stats["int32_count"] += _count(buf, f32) - _count(tail, f32)
                if hit is None and any(f in buf for f in forms):
                    hit = "bytes"
                tail = buf[-(width - 1):]
            fh.seek(0)
            is_root = fh.read(4) == b"root" or rel.endswith(".root")   # a .root that is not one refuses there
        if hit:
            kinds.add(hit)
        found = None
        if (hit is None or decode_all) and is_root:
            for cls, _, _, obj, codecs in root_keys(p):
                for c in codecs:
                    stats["codecs"][c] = stats["codecs"].get(c, 0) + 1
                if codecs:                                 # inflated (a stored object's bytes were scanned raw)
                    stats["bytes_inflated"] += len(obj)
                    stats["int32_count"] += _count(obj, f32)
                if cls != "TBasket":                       # a small object: a 4-byte seed there is no chance hit
                    stats["objects_int32_checked"] += 1
                    if any(f in obj for f in f32):
                        found = "int32-object"
                        break
                if not codecs:
                    continue
                if any(f in obj for f in forms):
                    found = "inflated"
                    break
        elif hit is None:
            for kind, data in _members(p):
                stats["codecs"][kind] = stats["codecs"].get(kind, 0) + 1
                stats["bytes_inflated"] += len(data)
                stats["int32_count"] += _count(data, f32)
                if any(f in data for f in forms):
                    found = "inflated"
                    break
        if found:
            kinds.add(found)
        hit = hit or found
        if hit:
            hits.append((rel, hit))
    stats["hits"] = sorted(kinds)
    stats["int32_patterns"] = len(f32)
    stats["int32_expected"] = len(f32) * (stats["bytes_raw"] + stats["bytes_inflated"]) / 2 ** 32
    return hits, stats


def leak_hits(workdir, files, seeds):
    return leak_scan(workdir, files, seeds)[0]


def export_allowlist(tunes=None):
    """The globs that may leave W: the inventory's patterns, less the seed-bearing (fnmatchcase, '*' crossing '/')."""
    return [r["pattern"] for r in inventory(tunes)
            if r["pattern"] not in (PUBLISH_SUMS, LEAK_SCAN) and not seed_bearing(r["pattern"])]


def cmd_publish(a):
    """The outgoing set is exactly the files the allowlist names (any other file outside W/tmp, seed-bearing ones
    aside, is a STOP); each is scanned, the scan's counts are written and scanned, then the sums, and they too."""
    w = Path(a.workdir)
    out = w / PUBLISH_SUMS
    if out.exists() or (w / LEAK_SCAN).exists():
        raise Refusal("the publish sums already exist")
    seeds = [s for _, _, ss in load_seeds(a.seeds) for s in ss]
    allow = export_allowlist()
    files, unlisted = [], 0
    for d, dirs, names in os.walk(w, followlinks=False):
        for x in names:
            q = os.path.join(d, x)
            rel = os.path.relpath(q, w)
            if os.path.islink(q) or not os.path.isfile(q):
                raise Refusal("a link or special file in W")
            if seed_bearing(rel) or rel.startswith("tmp/"):
                continue
            if any(fnmatch.fnmatchcase(rel, g) for g in allow):
                files.append(rel)
            else:
                unlisted += 1
    if unlisted:
        raise Refusal(f"{unlisted} unlisted files in W: the export allowlist does not name them")
    files.sort()
    hits, stats = leak_scan(w, files, seeds)
    if hits:
        raise Refusal(f"leak scan: {len(hits)} outgoing files hold a seed ({sum(1 for r, _ in hits if r is None)} "
                      f"in their path)")
    probs = schema_problems(w, files, json.load(open(a.schemas)))
    if probs:
        raise Refusal(f"{probs[0].split(':')[0]}: {len(probs)} gst files differ from B3's schema or it is unset")
    (w / LEAK_SCAN).write_text(json.dumps(dict(stats, schema="covfix-pg-leak-scan/1"), indent=1, sort_keys=True) + "\n")
    files.append(LEAK_SCAN)
    if leak_scan(w, [LEAK_SCAN], seeds)[0]:
        raise Refusal("leak scan: the scan's own record holds a seed")
    lines = []
    for rel in sorted(files):
        h = hashlib.sha256()
        with open(w / rel, "rb") as fh:
            for b in iter(lambda: fh.read(1 << 20), b""):
                h.update(b)
        lines.append(f"{h.hexdigest()}  {rel}\n")
    out.write_text("".join(lines))
    if leak_scan(w, [PUBLISH_SUMS], seeds)[0]:
        out.unlink()
        raise Refusal("leak scan: the publish sums hold a seed (a hash contains one); nothing is published")
    print(f"[pg_lib] publish: {len(files)} files scanned clean; {PUBLISH_SUMS} written")
    return 0


def cmd_leak_scan(a):
    """B3's positive control: one file's STOP-form hits and int32 count for a public seed (never a sealed one)."""
    hits, stats = leak_scan(os.path.dirname(a.file) or ".", [os.path.basename(a.file)], [a.seed])
    out = dict(stats, holds_seed=bool(hits), where=[x for _, x in hits])
    if a.schema:
        out["schema"] = root_schema(a.file)
    print(json.dumps(out, sort_keys=True))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("queue")
    q.add_argument("--seeds", required=True)
    q.add_argument("--out", required=True)
    p = sub.add_parser("products")
    p.add_argument("--workdir", required=True)
    p.add_argument("--seeds", required=True)
    i = sub.add_parser("inventory")
    i.add_argument("--workdir")
    b = sub.add_parser("publish")
    b.add_argument("--workdir", required=True)
    b.add_argument("--seeds", required=True)
    b.add_argument("--schemas", required=True)
    s = sub.add_parser("leak-scan")
    s.add_argument("--file", required=True)
    s.add_argument("--seed", type=int, required=True)
    s.add_argument("--schema", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "leak-scan" and a.seed != 123456789:
        ap.error("leak-scan takes only the public seed")
    try:
        return {"queue": cmd_queue, "products": cmd_products, "inventory": cmd_inventory,
                "publish": cmd_publish, "leak-scan": cmd_leak_scan}[a.cmd](a)
    except Refusal as e:
        print(f"[pg_lib] refusing: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
