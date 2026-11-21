#!/usr/bin/env python3
"""Mac side of cov2d_arrays_login.sh: decode the npz from the connect's stdout, re-check its sha256, and compare its
arrays with the committed export's record of them.

usage: python3 decode_c2a.py <connect stdout> <out npz> [<committed cov2d_Q_205.json.gz>]

Refuses (exit 1) unless: the stdout holds exactly one base64 block between the markers; the decoded bytes have the
sha256 the connect printed and the bound 7153b194...; the npz's arrays have the names, dtypes and shapes the committed
export lists; and each matrix's sqrt(trace) equals the export's to 1e-12 relative. Standard library only (zipfile
and the .npy header); writes only <out npz>, which must not exist.
"""
import ast
import base64
import gzip
import hashlib
import io
import json
import math
import re
import struct
import sys
import zipfile
from pathlib import Path

WANT = "7153b194b95c27f80db5997bdde35fe2475f2b1c40c9ff456edd409850cf47d2"
EXPORT = ("docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partc_r2/partc-r2/outA/cov2d_Q_205.json.gz")


def npy_arrays(raw):
    """{name: (dtype, shape, flat values)} for an uncompressed or deflated .npz of little-endian float64/int64 arrays."""
    out = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        for name in z.namelist():
            b = z.read(name)
            if b[:6] != b"\x93NUMPY":
                raise SystemExit(f"DECODE: {name} is not a .npy member")
            major = b[6]
            hlen, off = (struct.unpack("<H", b[8:10])[0], 10) if major == 1 else (struct.unpack("<I", b[8:12])[0], 12)
            hdr = ast.literal_eval(b[off:off + hlen].decode("latin1"))
            if hdr["fortran_order"] or hdr["descr"] not in ("<f8", "<i8"):
                raise SystemExit(f"DECODE: {name} has an unexpected layout {hdr}")
            n = math.prod(hdr["shape"]) if hdr["shape"] else 1
            vals = struct.unpack(f"<{n}{'d' if hdr['descr'] == '<f8' else 'q'}", b[off + hlen:off + hlen + 8 * n])
            out[name.removesuffix(".npy")] = ("float64" if hdr["descr"] == "<f8" else "int64", list(hdr["shape"]), vals)
    return out


def main(argv):
    if len(argv) not in (2, 3):
        print(__doc__)
        return 2
    text, dest = Path(argv[0]).read_text(), Path(argv[1])
    if dest.exists():
        raise SystemExit(f"DECODE: {dest} exists; refusing to overwrite")
    blocks = re.findall(r"^== BEGIN cov2d_Q_205\.npz base64\n(.*?)^== END cov2d_Q_205\.npz base64$", text, re.M | re.S)
    if len(blocks) != 1:
        raise SystemExit(f"DECODE: {len(blocks)} base64 blocks in the stdout, not 1")
    raw = base64.b64decode("".join(blocks[0].split()), validate=True)
    printed = re.search(r"^read (\d+) bytes; sha256 ([0-9a-f]{64})", text, re.M)
    got = hashlib.sha256(raw).hexdigest()
    if not printed or int(printed[1]) != len(raw) or printed[2] != got or got != WANT:
        raise SystemExit(f"DECODE: sha256 {got} / {len(raw)} bytes; cluster printed {printed and printed.groups()}; "
                         f"bound {WANT}")
    print(f"sha256 {got} ({len(raw)} bytes): equals the cluster's and the bound digest")
    exp_path = Path(argv[2]) if len(argv) == 3 else Path(EXPORT)
    exp = json.loads(gzip.decompress(exp_path.read_bytes()))
    arrs = npy_arrays(raw)
    if sorted(arrs) != sorted(exp["arrays"]):
        raise SystemExit(f"DECODE: arrays {sorted(arrs)}, the export lists {sorted(exp['arrays'])}")
    for k, meta in exp["arrays"].items():
        dt, shape, vals = arrs[k]
        if dt != meta["dtype"] or shape != meta["shape"]:
            raise SystemExit(f"DECODE: {k} is {dt} {shape}, the export lists {meta['dtype']} {meta['shape']}")
        if "sqrt_trace" in meta:
            n = shape[0]
            st = math.sqrt(sum(vals[i * n + i] for i in range(n)))
            if abs(st / meta["sqrt_trace"] - 1) > 1e-12:
                raise SystemExit(f"DECODE: {k} sqrt(trace) {st!r}, the export {meta['sqrt_trace']!r}")
        print(f"  {k}: {dt} {shape}" + (f", sqrt(trace) equals the export's" if "sqrt_trace" in meta else ""))
    dest.write_bytes(raw)
    print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
