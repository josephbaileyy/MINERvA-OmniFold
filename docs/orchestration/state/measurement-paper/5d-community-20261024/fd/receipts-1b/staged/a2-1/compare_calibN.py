#!/usr/bin/env python3
"""1B A2.1: the large-sample calibration's rerun at the final H1 code against job 60783756's record (the director's
ruling of 2026-11-04). Fixed before the rerun, from a walk of d4a4739e's 2,671 leaves (calibN-keys.txt):

* --old must be job 60783756's record: its json, npz and out must hash to OLD_SHA256, or nothing is compared;
* calibration.npz must be bitwise equal (numpy writes its zip entries at a fixed 1980 timestamp);
* calibration.json must be equal, as canonical bytes, after deleting exactly the EXCLUDE paths, each of which must
  exist in both records. The new fd_1b_mc.py digest is not merely deleted: it must be the --expect-mc-sha256 given;
* calibration.out's C2-CALIBRATION line must be equal byte for byte.

The walk found no deploy head, commit, path, job id, hostname, timestamp or argv field, so none is excluded. Any
other difference is a STOP to the director. Exit 0 PASS, 2 STOP."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

# environment, not result: the file atimes at read time, the wall clock, and the one digest the H1 edit changes.
# Each is a path of segments ("*" matches one key: the atime keys are file paths, which hold dots and slashes).
EXCLUDE = (("atime", "files", "*", "atime_ns_first"), ("atime", "files", "*", "atime_ns_now"),
           ("timing", "seconds"), ("timing", "set_seconds_measured"), ("timing", "projected_seconds"),
           ("code_sha256", "fd_1b_mc.py"))


# job 60783756's record (a2-1/calibN-run at 20b5fab6): --old must be these bytes, or nothing is compared (the audit's
# finding at 48ca04a1: an altered old copy and a matching new one would otherwise PASS)
OLD_SHA256 = {"calibration.json": "d4a4739e59ffdd6a84f8422b48084ad0e381534d64fea44f126276aad3f92c1e",
              "calibration.npz": "9047a6f730ca41cda8a0c6d7b60aac19ba10c04f8ab6a6b13a279a5835291a70",
              "calibration.out": "965062ddb6fcd98a7ba8c7f50e20074005e0334b85ecb5bd9916999b048c3d58"}


def leaves(o, path=()):
    """Every leaf as (path tuple, value); a list holding no dict or list is one leaf, as the walk counted it."""
    if isinstance(o, dict):
        if not o:
            yield path, o
        for k, v in o.items():
            yield from leaves(v, path + (k,))
    elif isinstance(o, list) and any(isinstance(x, (dict, list)) for x in o):
        for i, v in enumerate(o):
            yield from leaves(v, path + (str(i),))
    else:
        yield path, o


def excluded(path: tuple) -> tuple | None:
    """The EXCLUDE entry a leaf path matches, segment by segment."""
    for pat in EXCLUDE:
        if len(pat) == len(path) and all(seg == "*" or seg == key for seg, key in zip(pat, path)):
            return pat
    return None


def stripped(rec: dict) -> tuple[dict, dict]:
    """(the record with the excluded leaves deleted, {pattern: matches}); the deletion walks the same paths."""
    rec = json.loads(json.dumps(rec))
    hits = {p: 0 for p in EXCLUDE}
    for path, _ in list(leaves(rec)):
        pat = excluded(path)
        if pat:
            hits[pat] += 1
            node = rec
            for k in path[:-1]:
                node = node[k] if isinstance(node, dict) else node[int(k)]
            del node[path[-1]]
    return rec, hits


def compare(old: Path, new: Path, expect_mc: str) -> list[str]:
    bad = sorted(n for n, h in OLD_SHA256.items() if hashlib.sha256((old / n).read_bytes()).hexdigest() != h)
    if bad:
        return [f"--old is not job 60783756's record: {bad} differ from OLD_SHA256; nothing compared"]
    stops = []
    for name in ("calibration.npz",):
        a, b = (hashlib.sha256((d / name).read_bytes()).hexdigest() for d in (old, new))
        if a != b:
            stops.append(f"{name} differs: {a} vs {b}")
    ro, rn = (json.loads((d / "calibration.json").read_text()) for d in (old, new))
    if rn.get("code_sha256", {}).get("fd_1b_mc.py") != expect_mc:
        stops.append(f"the rerun's fd_1b_mc.py digest is {rn.get('code_sha256', {}).get('fd_1b_mc.py')}, "
                     f"not the H1 code's {expect_mc}")
    (so, ho), (sn, hn) = stripped(ro), stripped(rn)
    for pat in EXCLUDE:
        if not ho[pat] or not hn[pat]:
            stops.append(f"exclusion {'.'.join(pat)} matched nothing in {'the old' if not ho[pat] else 'the new'} record")
    if ho != hn:
        stops.append(f"the exclusions matched different counts: {ho} vs {hn}")
    co, cn = (json.dumps(s, sort_keys=True, separators=(",", ":")).encode() for s in (so, sn))
    if co != cn:
        lo, ln = dict(leaves(so)), dict(leaves(sn))
        diff = sorted(".".join(p) for p in set(lo) | set(ln) if lo.get(p, KeyError) != ln.get(p, KeyError))
        stops.append(f"calibration.json differs at {len(diff)} leaves outside the exclusions: {diff[:20]}")
    lines = [[x for x in (d / "calibration.out").read_bytes().splitlines() if x.startswith(b"C2-CALIBRATION")]
             for d in (old, new)]
    if len(lines[0]) != 1 or lines[0] != lines[1]:
        stops.append(f"the C2-CALIBRATION line differs: {lines[0]} vs {lines[1]}")
    return stops


def walk(old: Path) -> int:
    """calibN-keys.txt: every leaf path of the old record, list indices and atime file keys collapsed to "*", with
    its count, an example value and whether EXCLUDE deletes it."""
    from collections import Counter
    rec = json.loads((old / "calibration.json").read_text())
    ls = list(leaves(rec))

    def shape(path):
        return tuple("*" if (k.isdigit() or path[:2] == ("atime", "files") and i == 2) else k for i, k in enumerate(path))
    n = Counter(shape(p) for p, _ in ls)
    print(f"calibration.json sha256 {hashlib.sha256((old / 'calibration.json').read_bytes()).hexdigest()}: "
          f"{len(ls)} leaves, {len(n)} shapes")
    for sh in sorted(n):
        ex = next(v for p, v in ls if shape(p) == sh)
        tag = "EXCLUDED" if any(excluded(p) for p, _ in ls if shape(p) == sh) else "compared"
        print(f"{tag}  {n[sh]:4d}  {'.'.join(sh)} = {json.dumps(ex)[:80]}")
    return 0


def self_test(old: Path) -> int:
    """Both directions on copies of the old record: each excluded field changed (and the digest set to the expected
    value) must PASS; each kept field, the npz, the verdict line and the digest must STOP. Prints one row each."""
    import shutil
    import tempfile
    rec0 = json.loads((old / "calibration.json").read_text())
    mc0 = rec0["code_sha256"]["fd_1b_mc.py"]
    first_file = next(iter(rec0["atime"]["files"]))

    def case(edit_json=None, edit_npz=False, edit_out=False, expect=mc0, old_too=False):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as d_old:
            new = Path(d)
            for name in ("calibration.json", "calibration.npz", "calibration.out"):
                shutil.copyfile(old / name, new / name)
            if edit_json:
                rec = json.loads((new / "calibration.json").read_text())
                edit_json(rec)
                (new / "calibration.json").write_text(json.dumps(rec))
            if edit_npz:
                raw = bytearray((new / "calibration.npz").read_bytes())
                raw[-30] ^= 1
                (new / "calibration.npz").write_bytes(bytes(raw))
            if edit_out:
                (new / "calibration.out").write_bytes((new / "calibration.out").read_bytes().replace(b"s=0.92", b"s=0.93"))
            base = old
            if old_too:                                  # the same edit to a copy of old: only OLD_SHA256 stops it
                base = Path(d_old)
                for name in ("calibration.json", "calibration.npz", "calibration.out"):
                    shutil.copyfile(new / name, base / name)
            return compare(base, new, expect)

    def put(*path, value):
        def f(rec):
            node = rec
            for k in path[:-1]:
                node = node[k]
            node[path[-1]] = value
        return f
    passes = {"identical": case(),
              "every atime value": case(lambda r: [v.update(atime_ns_first=1, atime_ns_now=2)
                                                    for v in r["atime"]["files"].values()]),
              "timing.seconds": case(put("timing", "seconds", value=1.0)),
              "timing.set_seconds_measured": case(put("timing", "set_seconds_measured", value=1.0)),
              "timing.projected_seconds": case(put("timing", "projected_seconds", value=1.0)),
              "fd_1b_mc.py digest, as expected": case(put("code_sha256", "fd_1b_mc.py", value="e" * 64), expect="e" * 64)}
    stops = {"rule.s": case(put("rule", "s", value=0.93)),
             "rule.grid[100].union": case(lambda r: r["rule"]["grid"][100].update(union=0.5)),
             "a power placement": case(lambda r: r["power"]["g18"]["concentrated"]["4_cells_10pct"]["placements"][0]
                                       .__setitem__(0, 1)),
             "timing.workers": case(put("timing", "workers", value=32)),
             "timing.fine_cells_kept": case(put("timing", "fine_cells_kept", value=1)),
             "atime.moved": case(put("atime", "moved", value=[first_file])),
             "an atime file key dropped": case(lambda r: r["atime"]["files"].pop(first_file)),
             "an atime file key renamed, count kept": case(lambda r: r["atime"]["files"].__setitem__(
                 first_file + ".renamed", r["atime"]["files"].pop(first_file))),
             "fd_1b_c2.py digest": case(put("code_sha256", "fd_1b_c2.py", value="0" * 64)),
             "an added key": case(put("host", value="nid0")),
             "fd_1b_mc.py digest, not expected": case(put("code_sha256", "fd_1b_mc.py", value="e" * 64)),
             "npz one byte": case(edit_npz=True),
             "verdict line": case(edit_out=True),
             "an altered old copy, matched by the new": case(put("rule", "s", value=0.5), old_too=True),
             "an altered old npz, matched by the new": case(edit_npz=True, old_too=True)}
    bad = 0
    for name, got in passes.items():
        bad += bool(got)
        print(f"{'ok  ' if not got else 'FAIL'} PASS expected: {name}{'' if not got else ' -> ' + got[0][:120]}")
    for name, got in stops.items():
        bad += not got
        print(f"{'ok  ' if got else 'FAIL'} STOP expected: {name}{' -> ' + got[0][:120] if got else ''}")
    print(f"self-test {'PASS' if not bad else 'FAIL'}: {len(passes)} pass cases, {len(stops)} stop cases")
    return 0 if not bad else 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--old", type=Path, required=True, help="job 60783756's run copy")
    p.add_argument("--new", type=Path, help="the rerun's copy")
    p.add_argument("--expect-mc-sha256", help="fd_1b_mc.py's sha256 at the H1 commit")
    p.add_argument("--self-test", action="store_true", help="both directions on copies of --old")
    p.add_argument("--walk", action="store_true", help="print every leaf path of --old (calibN-keys.txt)")
    a = p.parse_args(argv)
    if a.walk:
        return walk(a.old)
    if a.self_test:
        return self_test(a.old)
    if a.new is None or a.expect_mc_sha256 is None:
        p.error("--new and --expect-mc-sha256 are required unless --self-test or --walk")
    stops = compare(a.old, a.new, a.expect_mc_sha256)
    for s in stops:
        print(f"STOP {s}")
    print("PASS" if not stops else f"STOP ({len(stops)})")
    return 0 if not stops else 2


if __name__ == "__main__":
    sys.exit(main())
