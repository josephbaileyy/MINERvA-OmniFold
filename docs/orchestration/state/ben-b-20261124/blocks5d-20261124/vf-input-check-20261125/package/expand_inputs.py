#!/usr/bin/env python3
"""Build inputs.tsv for the V_F input-existence check from codex-school's p1.tsv / p2.tsv extractions.

Every pin is checked mechanically: an explicit row's sha256 must appear verbatim in the committed file it cites (at
REV); an expanded row's pin is read from the committed manifest itself. Rows are deduplicated by (path, pin); a path
read by any Phase 1 readout is Phase 1. Output columns: phase, readouts, role, path, pin, size, source.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REV = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
REPO = Path.home() / "s2r-wt"
FD = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
PS = "/pscratch/sd/j/josephrb"
HEX = re.compile(r"^[0-9a-f]{64}$")
P1 = {"dp", "g", "g0", "diag", "fup", "sens2", "fboot", "f0", "f0b", "f1", "s1npz", "cresp"}


def show(path: str) -> str:
    r = subprocess.run(["git", "-C", str(REPO), "show", f"{REV}:{path}"], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"STOP: cannot read {path} at {REV}")
    return r.stdout


def sums(path: str, lo=None, hi=None, root=None, sel=None):
    """(sha, absolute path, size or NONE) from a committed 'sha [size] path' manifest, lines lo..hi (1-based)."""
    out = []
    for i, line in enumerate(show(path).splitlines(), 1):
        if lo and (i < lo or i > hi):
            continue
        f = line.split()
        if len(f) < 2 or not HEX.match(f[0]):
            continue
        size = f[1] if len(f) == 3 and f[1].isdigit() else "NONE"
        p = f[-1].lstrip("*")
        if not p.startswith("/"):
            p = f"{root.rstrip('/')}/{p}"
        if sel and not sel(p):
            continue
        out.append((f[0], p, size))
    return out


def expand(ro, role, path, src):
    """The member files of one manifest-range or directory row."""
    m = re.match(r"^([A-Za-z0-9_.\-]+)\[(\d+)-(\d+)\]$", role)
    if m:
        name, lo, hi = m.group(1), int(m.group(2)), int(m.group(3))
        man = {"stage0_inventory": ("docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/INVENTORY.sha256", None),
               "s5p_archive": ("docs/orchestration/state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt", f"{PS}/s5p-20260926"),
               "f1_products": (f"{FD}/receipts-f1/run/cluster/manifest/f1-products-SHA256SUMS", f"{PS}/fd-f1-20261027/f1c")}[name]
        return [(s, p, z, f"{man[0]}:{lo}-{hi}") for s, p, z in sums(man[0], lo, hi, man[1])]
    m = re.match(r"^(D16-[A-Za-z0-9_]+\.json)\[inputs\.a\]$", role)
    if m:
        jp = f"docs/orchestration/state/s5p/stage3/f4/{m.group(1)}"
        d = json.loads(show(jp))
        return [(x["a_sha256"], x["a"], "NONE", jp) for x in d["inputs"]]
    key = (ro, role)
    if key == ("gdefs", "rebuild_dir"):
        d = json.loads(show(f"{FD}/gencmp/readout/rebuild_b.json"))["outputs"]
        return [(v["sha256"], v["path"], "NONE", f"{FD}/gencmp/readout/rebuild_b.json") for v in d.values()]
    if key == ("gnat", "rebuild_dir"):
        d = json.loads(show(f"{FD}/gencmp/readout/rebuild_d.json"))["outputs"]
        keep = [k for k in d if k == "nuwro_CHnative_gen" or re.match(r"^nuwro_(C12|H|CHnative)_ana_s\d+$", k)]
        return [(d[k]["sha256"], d[k]["path"], "NONE", f"{FD}/gencmp/readout/rebuild_d.json") for k in keep]
    if key == ("xk", "g2r_universes_dir"):
        return [(s, p, z, f"{FD}/receipts-cov2d/g2r/xk/INPUTS-g2r.sha256:6-180") for s, p, z in
                sums(f"{FD}/receipts-cov2d/g2r/xk/INPUTS-g2r.sha256", 6, 180)]
    if key == ("xk", "re2_laterals_and_replicas_dir"):
        kp = f"{FD}/receipts-cov2d/g2r/xk/run/node/run/k/k.json"
        d = json.loads(show(kp))["inputs"]
        return [(v["sha256"], p, "NONE", kp) for p, v in d.items()
                if p.startswith(f"{PS}/2d-closeout-re2-20261023/partb/out/") and re.search(r"/(S3_|S1_)", p)]
    if key == ("xk", "boot_xcov_dir"):
        return [(s, p, z, f"{FD}/xcov/run/hpss/files.sha256") for s, p, z in
                sums(f"{FD}/xcov/run/hpss/files.sha256", root=PS, sel=lambda q: "/boot/xcov/" in q)]
    if key == ("ct3b", "closures_dir"):
        return [(s, p, z, f"{FD}/receipts-ct/3b/run/preserve/INVENTORY.sha256") for s, p, z in
                sums(f"{FD}/receipts-ct/3b/run/preserve/INVENTORY.sha256", sel=lambda q: "/closures/" in q)]
    if key == ("ct3b", "mp1_unfolds_dir"):
        return [(s, p, z, f"{FD}/receipts-ct/preserve/INVENTORY.sha256:23-33") for s, p, z in
                sums(f"{FD}/receipts-ct/preserve/INVENTORY.sha256", 23, 33)]
    if key == ("prr", "unfolds_dir"):
        return [(s, p, z, f"{FD}/receipts-prr/misc/cluster/log-misc/SHA256SUMS") for s, p, z in
                sums(f"{FD}/receipts-prr/misc/cluster/log-misc/SHA256SUMS", root=f"{PS}/fd-prr-20261108")]
    if key == ("prr", "route2_dir"):
        return [(s, p, z, f"{FD}/receipts-prr/ibu/attempt3/cluster/log-ibu/SHA256SUMS") for s, p, z in
                sums(f"{FD}/receipts-prr/ibu/attempt3/cluster/log-ibu/SHA256SUMS", root=f"{PS}/fd-prr-20261108")]
    if key == ("e96d", "runs_dir"):
        mp = f"{FD}/e96-data-20261110/receipts/a1-run-20261112/cluster/full/log-full/SHA256SUMS.txt"
        return [(s, p, z, mp) for s, p, z in sums(mp, root=f"{PS}/e96data-a1")]
    if key == ("refg1", "batch_units_dir"):
        return [(s, p, z, f"{FD}/receipts-ref-g1/batch/SHA256SUMS") for s, p, z in
                sums(f"{FD}/receipts-ref-g1/batch/SHA256SUMS", root=f"{PS}/ref-g1-20261105/batch/units",
                     sel=lambda q: not q.endswith("/gibu1.npz"))]
    if key in (("refg1", "e_replicas_dir"), ("refg1", "e_universes_dir")):
        rp = f"{FD}/receipts-ref-g1/a1-read/readout.json"
        d = json.loads(show(rp))["staged_sha256"]
        return [(v, p, "NONE", rp) for p, v in d.items() if p.startswith(path.rstrip("/") + "/")]
    return None


def main() -> int:
    raw = []
    for f in ("p1.tsv", "p2.tsv"):
        for line in (HERE / f).read_text().splitlines():
            if line.strip():
                c = line.split("\t")
                assert len(c) == 6, line
                raw.append(c)
    rows, problems = {}, []
    cache = {}
    for ro, role, path, pin, size, src in raw:
        if role == "LOCAL":
            continue
        members = expand(ro, role, path, src)
        if members is None:
            if not path.startswith(("/pscratch", "/global", "/home/j")):
                problems.append(f"not a NERSC path: {ro} {role} {path}")
                continue
            if pin != "NONE":
                cf = src.rsplit(":", 1)[0]
                if cf not in cache:
                    cache[cf] = show(cf)
                if pin not in cache[cf]:
                    problems.append(f"PIN NOT IN CITED FILE: {ro} {role} {pin[:12]} {cf}")
                    continue
            members = [(pin, path, size, src)]
        for s, p, z, sr in members:
            k = (p, s)
            r = rows.setdefault(k, {"phase": "P2", "readouts": set(), "roles": set(), "size": z, "src": sr})
            r["readouts"].add(ro)
            r["roles"].add(re.sub(r"\[.*", "", role))
            if ro in P1:
                r["phase"] = "P1"
            if r["size"] == "NONE" and z != "NONE":
                r["size"] = z
    paths = {}
    for (p, s) in rows:
        paths.setdefault(p, set()).add(s)
    for p, ss in paths.items():
        if len(ss) > 1:
            problems.append(f"TWO PINS FOR ONE PATH: {p} {sorted(x[:12] for x in ss)}")
    out = []
    for (p, s), r in sorted(rows.items(), key=lambda kv: (kv[1]["phase"], kv[0][0])):
        out.append("\t".join([r["phase"], ",".join(sorted(r["readouts"])), ",".join(sorted(r["roles"])), p,
                              s if s else "NONE", r["size"], r["src"]]))
    (HERE / "inputs.tsv").write_text("\n".join(out) + "\n")
    n1 = sum(1 for x in out if x.startswith("P1\t")); n2 = len(out) - n1
    print(f"inputs.tsv: {len(out)} rows (P1 {n1}, P2 {n2}); unpinned {sum(1 for x in out if x.split(chr(9))[4] == 'NONE')}")
    for x in problems:
        print("PROBLEM", x)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
