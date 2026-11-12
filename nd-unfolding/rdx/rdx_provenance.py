#!/usr/bin/env python3
"""RDX stage 0's pre-build provenance (RDX-DECLARATION.md rev 3 §2 C1, D5), on a login node before any build.

    rdx_provenance.py --s0-manifest S0/build/MANIFEST.sha256 --canon-src SRC --opt-lib OPT/lib --synced TREE [--out x]

GATED (a failure exits 1, and no build may follow):
- the six pins of build_mp1_s0.sh:28-34 hold on the canonical source, and equal S0's MANIFEST rows for src_base;
- every OPT/lib/*.so equals the MANIFEST row of the same basename, and the MANIFEST lists no .so that OPT/lib lacks.
LISTED (not gated): every difference between the synced tree's file digests and S0's src_base rows.
Exit 0 PASS, 1 FAIL, 2 could not check.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import rdx_common as C  # noqa: E402

PINS = {  # build_mp1_s0.sh:28-34
    "runEventLoopOmniFold.cpp": "57792e42fe3f5a663016f94b91a5631fc50349135c92b35a08eaefcb85812be3",
    "event/CVUniverse.h": "900d7368d6184d503399bd99c0fd30085212df0327b8be374182495b85a3677d",
    "cuts/MaxPtMu.h": "ae4adeb3a5ff0e2f8cab46a4dd9dc40d7b42da6b936311d776fdb7612e2d73ca",
    "CMakeLists.txt": "d77791ad0e866704d70ab5cf3db0c0c3c7a5aed0218c144c20f86081ad6814b0",
    "cuts/MaxPzMu.h": "c50f6b5ae4e95e85de3f7a50b704232ead767231c1604951a597e9faafb3e56c",
    "systematics/Systematics.h": "1bdfa4f028e7e5f3d4e39a60d2cadc0c05b366fd12ff345d5183177a9b555086",
}
ROW = re.compile(r"^([0-9a-f]{64})  (.+)$")


def manifest(path: Path) -> tuple[dict, dict]:
    """(src_base rows {relative path: sha}, .so rows {basename: sha}) of S0's MANIFEST.sha256."""
    src, so = {}, {}
    for line in Path(path).read_text().splitlines():
        m = ROW.match(line)
        if not m:
            continue
        sha, p = m.groups()
        if p.startswith("src_base/"):
            src[p[len("src_base/"):]] = sha
        elif p.endswith(".so"):
            if Path(p).name in so and so[Path(p).name] != sha:
                raise C.CheckError(f"S0's MANIFEST lists {Path(p).name} twice with different digests")
            so[Path(p).name] = sha
    if not src or not so:
        raise C.CheckError("S0's MANIFEST has no src_base rows or no .so rows")
    return src, so


def tree_digests(root: Path) -> dict:
    root = Path(root)
    return {str(p.relative_to(root)): C.sha256(p) for p in sorted(root.rglob("*"))
            if p.is_file() and ".git" not in p.relative_to(root).parts}


def check(s0_manifest: Path, canon: Path, opt_lib: Path, synced: Path) -> dict:
    bad = []
    src, so = manifest(s0_manifest)
    for rel, pin in PINS.items():
        got = C.sha256(Path(canon) / rel)
        if got != pin:
            bad.append(f"canonical {rel} is {got}, pinned {pin}")
        if src.get(rel) != pin:
            bad.append(f"S0's MANIFEST src_base/{rel} is {src.get(rel)}, pinned {pin}")
    libs = {p.name: C.sha256(p) for p in sorted(Path(opt_lib).glob("*.so"))}
    for name, sha in libs.items():
        if so.get(name) != sha:
            bad.append(f"opt/lib/{name} is {sha}; S0's MANIFEST has {so.get(name)}")
    for name in sorted(set(so) - set(libs)):
        bad.append(f"S0's MANIFEST lists {name}, which opt/lib lacks")
    syn = tree_digests(synced)
    diff = {"changed": sorted(k for k in set(syn) & set(src) if syn[k] != src[k]),
            "only_in_synced": sorted(set(syn) - set(src)), "only_in_s0": sorted(set(src) - set(syn))}
    return {"mode": "rdx-provenance", "pins": PINS, "so_checked": len(libs), "synced_vs_s0_src_base": diff,
            "failures": bad, "verdict": "PASS" if not bad else "FAIL"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--s0-manifest", type=Path, required=True)
    ap.add_argument("--canon-src", type=Path, required=True)
    ap.add_argument("--opt-lib", type=Path, required=True)
    ap.add_argument("--synced", type=Path, required=True)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    try:
        res = check(a.s0_manifest, a.canon_src, a.opt_lib, a.synced)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"verdict": "COULD_NOT_CHECK", "error": repr(exc)}))
        return 2
    text = json.dumps(res, indent=1)
    print(text)
    if a.out:
        a.out.write_text(text + "\n")
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
