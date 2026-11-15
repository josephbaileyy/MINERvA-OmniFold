"""C0 for RE-2-shapes (the director, 2026-11-14): the identity run against partc-r2, file by file, by SHA256SUMS.

The identity run is re2c_run.sh's refined arm with the driver in mode identity, on a deploy at partc-r2's own commit.
re2c_determinism.py (re2's comparator, the one behind partc_r2/determinism_dry_amend2.json) compares the two trees
first. Its output is the --determinism record. This script then classifies every line of the two SHA256SUMS:
  bitwise        the same digest in both;
  path-pairs     the comparator proved the file equal after the path pairs (its digest pair, reason "equal" or
                 "json-rule"), or it is a ROOT file paired through its byte-equal npz twin ("root-twin");
  skipped:<why>  a category the comparator skips, by the comparator's own skipped() (logs/, mpl/, tmp, *.root,
                 *.pdf, values_table.*), which is the determinism record's list;
  SHA256SUMS     the file itself, which lists the skipped files' digests (it is never in either list);
  OTHER          anything else, or a file in only one list: a STOP to the director.
Exit 0 only if no line is OTHER, the two lists name the same files, and the comparator's own differences are at most
SHA256SUMS. Otherwise 1.
    python3 -I c0_sums.py --comparator re2c_determinism.py --determinism c0-determinism.json \
        --partc-r2 <dir> --c0 <dir> --out c0-sums.json
"""
import argparse
import importlib.util
import json
import sys


def sums(path):
    out = {}
    for ln in open(path).read().splitlines():
        d, rel = ln.split(None, 1)
        out[rel[2:] if rel.startswith("./") else rel] = d
    return out


def main():
    ap = argparse.ArgumentParser()
    for k in ("--comparator", "--determinism", "--partc-r2", "--c0", "--out"):
        ap.add_argument(k, required=True)
    a = ap.parse_args()
    spec = importlib.util.spec_from_file_location("re2c_determinism", a.comparator)
    det = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(det)
    rec = json.load(open(a.determinism))
    pairs = rec["digest_pairs"]
    s, r = sums(f"{a.partc_r2}/SHA256SUMS"), sums(f"{a.c0}/SHA256SUMS")
    rows, counts = {}, {}
    for rel in sorted(set(s) | set(r)):
        if rel not in s or rel not in r:
            cls = "OTHER (only in " + ("partc-r2" if rel in s else "c0") + ")"
        elif s[rel] == r[rel]:
            cls = "bitwise"
        elif r[rel] in pairs and pairs[r[rel]]["stopped"] == s[rel]:
            cls = "path-pairs (" + pairs[r[rel]]["reason"] + ")"
        elif det.skipped(rel):
            cls = "skipped: " + det.skipped(rel)
        else:
            cls = "OTHER"
        rows[rel] = cls
        key = cls.split(" (")[0] if not cls.startswith("skipped") else cls
        counts[key] = counts.get(key, 0) + 1
    other = sorted(k for k, v in rows.items() if v.startswith("OTHER"))
    det_differ = [d["file"] for d in rec["differ"]]
    det_extra = rec["only_stopped"] + rec["only_rerun"] + rec["root_untabled"] + [f for f in det_differ if f != "SHA256SUMS"]
    ok = not other and not det_extra and set(s) == set(r)
    res = {"schema": "re2shapes-c0/1", "verdict": "PASS" if ok else "STOP", "n_lines": {"partc-r2": len(s), "c0": len(r)},
           "counts": counts, "other": other, "comparator": {"verdict": rec["verdict"], "differ": det_differ,
                                                           "only_stopped": rec["only_stopped"], "only_rerun": rec["only_rerun"],
                                                           "root_untabled": rec["root_untabled"],
                                                           "compared": rec["compared"], "equal": rec["equal"]},
           "rows": rows}
    open(a.out, "w").write(json.dumps(res, indent=1) + "\n")
    print(f"C0 {res['verdict']}: lines {len(s)}/{len(r)} counts {json.dumps(counts, sort_keys=True)} "
          f"other {other} comparator {rec['verdict']} differ {det_differ} extra {det_extra}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
