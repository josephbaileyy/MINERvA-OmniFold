"""C2-EFF local verifier: unpack and check the fetched tar (laptop only; reads nothing on the cluster).

usage: python3 -I -B c2_fetch_verify.py OUT_DIR LISTING CENTRAL_SHA256

OUT_DIR holds fetch.tar (from c2_fetch.sh). LISTING is read-2's committed inputs-listing.txt (sizes by stat).
CENTRAL_SHA256 is c2_central.npz's sha256 from the committed units-centrals/c2_central.done.

Writes OUT_DIR/files/{units,inputs}/... (exclusive creates; OUT_DIR/files must not exist) and OUT_DIR/SHA256SUMS.
Prints "VERIFY OK 903" and exits 0 only if every check passes; any failure prints "VERIFY-REFUSED: ..." and exits 9.
"""
import hashlib
import json
import os
import sys
import tarfile

N_REP = 300
UNITS = ["c2_replica_b%d" % b for b in range(1, N_REP + 1)] + ["c2_central"]
INPUTS = ["%03d_xsec.root" % i for i in range(1, N_REP + 2)]
EXPECTED = [f"units/{u}{e}" for u in UNITS for e in (".npz", ".done")] + [f"inputs/{n}" for n in INPUTS]
N_FILES = len(EXPECTED)
KS = [1, 2, 3, 4, 5, 10, 15, 20]
LISTING_PREFIX = "/pscratch/sd/j/josephrb/ref-c2c1-20261106/read-2/inputs/"


class Refused(Exception):
    pass


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def read_tar(path: str) -> dict:
    data = {}
    with tarfile.open(path, mode="r:") as t:
        for m in t:
            if not m.isreg():
                raise Refused(f"tar member {m.name!r} is not a regular file")
            if m.name in data:
                raise Refused(f"tar member {m.name!r} appears twice")
            if m.name != "MANIFEST.tsv" and m.name not in EXPECTED_SET:
                raise Refused(f"unexpected tar member {m.name!r}")
            f = t.extractfile(m)
            b = f.read()
            if len(b) != m.size:
                raise Refused(f"{m.name}: short read")
            data[m.name] = b
    return data


def parse_manifest(b: bytes) -> dict:
    lines = b.decode().splitlines()
    if not lines or not lines[0].startswith("# host ") or lines[1] != \
            "name\tsize\tsha256\tatime_ns_before\tatime_ns_after\tmtime_ns":
        raise Refused("MANIFEST.tsv has no header")
    rows = {}
    for ln in lines[2:]:
        p = ln.split("\t")
        if len(p) != 6:
            raise Refused(f"MANIFEST row {ln!r} has {len(p)} fields")
        rows[p[0]] = {"size": int(p[1]), "sha256": p[2], "atime_before": int(p[3]), "atime_after": int(p[4])}
    if sorted(rows) != sorted(EXPECTED) or len(lines) - 2 != N_FILES:
        raise Refused("MANIFEST names are not the expected 903")
    return rows


def listing_sizes(path: str) -> dict:
    sizes = {}
    with open(path) as f:
        for ln in f:
            size, p = ln.split()
            if not p.startswith(LISTING_PREFIX):
                raise Refused(f"listing path {p!r} is not under read-2/inputs")
            sizes[p[len(LISTING_PREFIX):]] = int(size)
    return sizes


def check(out: str, listing: str, central_sha: str) -> list:
    import numpy as np
    tar = os.path.join(out, "fetch.tar")
    data = read_tar(tar)
    if "MANIFEST.tsv" not in data:
        raise Refused("no MANIFEST.tsv: the remote side did not finish")
    rows = parse_manifest(data.pop("MANIFEST.tsv"))
    if sorted(data) != sorted(EXPECTED):
        raise Refused("the tar does not hold exactly the 903 expected files")
    for n in EXPECTED:
        r = rows[n]
        if len(data[n]) != r["size"] or sha(data[n]) != r["sha256"]:
            raise Refused(f"{n}: size or sha256 differs from the remote manifest")
        if r["atime_before"] != r["atime_after"]:
            raise Refused(f"{n}: atime moved on the cluster")
    for u in UNITS:
        d = json.loads(data[f"units/{u}.done"].decode())
        if d.get("unit") != u or d.get("verdict") != "PASS" or d.get("sha256") != sha(data[f"units/{u}.npz"]):
            raise Refused(f"{u}: done-marker is not PASS for this npz")
    if sha(data["units/c2_central.npz"]) != central_sha:
        raise Refused("c2_central.npz is not the committed one")
    sizes = listing_sizes(listing)
    for n in INPUTS:
        if sizes.get(n) != len(data[f"inputs/{n}"]):
            raise Refused(f"inputs/{n}: size {len(data[f'inputs/{n}'])} is not the committed listing's {sizes.get(n)}")
    import io
    for u in UNITS:
        z = np.load(io.BytesIO(data[f"units/{u}.npz"]), allow_pickle=False)
        if [int(k) for k in z["ks"]] != KS:
            raise Refused(f"{u}: ks {list(z['ks'])} is not {KS}")
        x = np.asarray(z["xsec"])
        if x.shape != (len(KS), 224) or not np.all(np.isfinite(x)):
            raise Refused(f"{u}: xsec shape {x.shape} or non-finite values")
    files = os.path.join(out, "files")
    os.mkdir(files)
    for sub in ("units", "inputs"):
        os.mkdir(os.path.join(files, sub))
    for n in EXPECTED:
        with open(os.path.join(files, n), "xb") as f:
            f.write(data[n])
    with open(os.path.join(out, "SHA256SUMS"), "x") as f:
        f.writelines(f"{rows[n]['sha256']}  files/{n}\n" for n in sorted(EXPECTED))
    return EXPECTED


EXPECTED_SET = set(EXPECTED)


def main(argv) -> int:
    if len(argv) != 4:
        print("VERIFY-REFUSED: usage: c2_fetch_verify.py OUT_DIR LISTING CENTRAL_SHA256")
        return 9
    try:
        n = check(argv[1], argv[2], argv[3])
    except (Refused, OSError, ValueError, KeyError, tarfile.TarError) as e:
        print(f"VERIFY-REFUSED: {type(e).__name__}: {e}")
        return 9
    print(f"VERIFY OK {len(n)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
