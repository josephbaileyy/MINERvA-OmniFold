"""CENTER2D local verifier: unpack and check the fetched tar (laptop only; reads nothing on the cluster).

usage: python3 -I -B center2d_fetch_verify.py OUT_DIR EXPECTED_TSV

OUT_DIR holds fetch.tar (from center2d_fetch.sh). EXPECTED_TSV is `center2d.py expected`'s output: label, sha256, path,
one row per fetched file, every digest taken from a committed record.

Writes OUT_DIR/files/<label> (exclusive creates; OUT_DIR/files must not exist) and OUT_DIR/SHA256SUMS. Prints
"VERIFY OK 16" and exits 0 only if every check passes; any failure prints "VERIFY-REFUSED: ..." and exits 9.
"""
import hashlib
import os
import sys
import tarfile

N_FILES = 16
HEADER = "name\tsize\tsha256\tatime_ns_before\tatime_ns_after\tmtime_ns"


class Refused(Exception):
    pass


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def read_expected(path: str) -> dict:
    out = {}
    with open(path) as f:
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) != 3 or len(p[1]) != 64 or p[0] in out:
                raise Refused(f"expected row {ln!r} is malformed or repeated")
            if p[0].startswith("/") or ".." in p[0].split("/"):
                raise Refused(f"expected label {p[0]!r} is not a plain relative name")
            out[p[0]] = p[1]
    if len(out) != N_FILES:
        raise Refused(f"expected lists {len(out)} files, not {N_FILES}")
    return out


def read_tar(path: str, names: set) -> dict:
    data = {}
    with tarfile.open(path, mode="r:") as t:
        for m in t:
            if not m.isreg():
                raise Refused(f"tar member {m.name!r} is not a regular file")
            if m.name in data:
                raise Refused(f"tar member {m.name!r} appears twice")
            if m.name != "MANIFEST.tsv" and m.name not in names:
                raise Refused(f"unexpected tar member {m.name!r}")
            b = t.extractfile(m).read()
            if len(b) != m.size:
                raise Refused(f"{m.name}: short read")
            data[m.name] = b
    return data


def parse_manifest(b: bytes, names: set) -> dict:
    lines = b.decode().splitlines()
    if len(lines) < 2 or not lines[0].startswith("# host ") or lines[1] != HEADER:
        raise Refused("MANIFEST.tsv has no header")
    rows = {}
    for ln in lines[2:]:
        p = ln.split("\t")
        if len(p) != 6 or p[0] in rows:
            raise Refused(f"MANIFEST row {ln!r} is malformed or repeated")
        rows[p[0]] = {"size": int(p[1]), "sha256": p[2], "atime_before": int(p[3]), "atime_after": int(p[4])}
    if set(rows) != names:
        raise Refused("MANIFEST names are not the expected 16")
    return rows


def check(out: str, expected_tsv: str) -> list:
    exp = read_expected(expected_tsv)
    names = set(exp)
    data = read_tar(os.path.join(out, "fetch.tar"), names)
    if "MANIFEST.tsv" not in data:
        raise Refused("no MANIFEST.tsv: the remote side did not finish")
    rows = parse_manifest(data.pop("MANIFEST.tsv"), names)
    if set(data) != names:
        raise Refused("the tar does not hold exactly the 16 expected files")
    for n in sorted(names):
        r = rows[n]
        if len(data[n]) != r["size"] or sha(data[n]) != r["sha256"]:
            raise Refused(f"{n}: size or sha256 differs from the remote manifest")
        if r["atime_before"] != r["atime_after"]:
            raise Refused(f"{n}: atime moved on the cluster")
        if sha(data[n]) != exp[n]:
            raise Refused(f"{n}: sha256 {sha(data[n])} is not the committed {exp[n]}")
    files = os.path.join(out, "files")
    os.mkdir(files)
    for n in sorted(names):
        os.makedirs(os.path.join(files, os.path.dirname(n)), exist_ok=True)
        with open(os.path.join(files, n), "xb") as f:
            f.write(data[n])
    with open(os.path.join(out, "SHA256SUMS"), "x") as f:
        f.writelines(f"{rows[n]['sha256']}  files/{n}\n" for n in sorted(names))
    return sorted(names)


def main(argv) -> int:
    if len(argv) != 3:
        print("VERIFY-REFUSED: usage: center2d_fetch_verify.py OUT_DIR EXPECTED_TSV")
        return 9
    try:
        n = check(argv[1], argv[2])
    except (Refused, OSError, ValueError, KeyError, UnicodeDecodeError, tarfile.TarError) as e:
        print(f"VERIFY-REFUSED: {type(e).__name__}: {e}")
        return 9
    print(f"VERIFY OK {len(n)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
