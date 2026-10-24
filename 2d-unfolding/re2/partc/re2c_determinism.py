#!/usr/bin/env python3
"""RE-2 part C, amendment 1: the rerun's products against the stopped run's, byte for byte (condition 2: a stop).

    python3 -I re2c_determinism.py --stopped $B/partc --rerun $B/partc-r2 \\
        --path-pair /2d-closeout-re2-20261023/partc-r2/=/2d-closeout-re2-20261023/partc/ \\
        --path-pair /deploy-<new>/=/deploy-e079ff05/ --out determinism.json

Every file the two runs share is compared byte for byte, after the rerun's bytes have each --path-pair applied (its
output namespace and its deploy, which records name). Excluded, each named in the result:
  logs/, tmp/, mpl/       run logs (times, durations, paths), scratch and caches;
  *.root                  TFile records its creation time; each ROOT product's matrices are compared through the
                          npz written beside it from the same arrays (production_cov.npz, cov2d_Q_205.npz), and
                          its read-back is a stop inside build_q (A4);
  *.pdf                   matplotlib stamps a creation date into a PDF; each figure's PNG twin is compared;
  values_table.*          the one step whose input (the spec) the amendment changed.
Files that only one run has: the rerun may add chain.json and SHA256SUMS, which the stopped run never reached; any
other one-sided file is a difference. Exit 0 only if no shared file differs and no other file is one-sided.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

SKIP_DIRS = ("logs", "tmp", "mpl")
SKIP_SUFFIX = (".root", ".pdf")
SKIP_NAMES = ("values_table.tsv", "values_table.json")
RERUN_ONLY_OK = ("chain.json", "SHA256SUMS")


def files(root):
    out = {}
    for p in sorted(Path(root).rglob("*")):
        if p.is_file():
            rel = p.relative_to(root).as_posix()
            out[rel] = p
    return out


def skipped(rel):
    first = rel.split("/", 1)[0]
    if first in SKIP_DIRS:
        return "run logs, scratch or caches"
    if rel.endswith(".root"):
        return "ROOT: TFile creation time; compared through its npz twin"
    if rel.endswith(".pdf"):
        return "PDF: creation date; compared through its PNG twin"
    if rel.split("/")[-1] in SKIP_NAMES:
        return "the values table: its spec is what the amendment changed"
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stopped", required=True)
    ap.add_argument("--rerun", required=True)
    ap.add_argument("--path-pair", action="append", default=[], help="NEW=OLD, applied to the rerun's bytes")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    pairs = [tuple(x.encode() for x in pp.split("=", 1)) for pp in a.path_pair]
    s, r = files(a.stopped), files(a.rerun)
    res = {"compared": 0, "equal": 0, "differ": [], "skipped": {}, "only_stopped": [], "only_rerun": [],
           "path_pairs": a.path_pair}
    for rel in sorted(set(s) | set(r)):
        why = skipped(rel)
        if why:
            res["skipped"].setdefault(why, 0)
            res["skipped"][why] += 1
            continue
        if rel not in r:
            res["only_stopped"].append(rel)
            continue
        if rel not in s:
            if rel.split("/")[-1] not in RERUN_ONLY_OK:
                res["only_rerun"].append(rel)
            continue
        b = r[rel].read_bytes()
        for new, old in pairs:
            b = b.replace(new, old)
        res["compared"] += 1
        if b == s[rel].read_bytes():
            res["equal"] += 1
        else:
            res["differ"].append({"file": rel, "stopped": hashlib.sha256(s[rel].read_bytes()).hexdigest(),
                                  "rerun_normalized": hashlib.sha256(b).hexdigest()})
    res["verdict"] = "PASS" if res["compared"] and not (res["differ"] or res["only_stopped"] or res["only_rerun"]) \
        else "FAIL"
    Path(a.out).write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: res[k] for k in ("verdict", "compared", "equal", "skipped")} |
                     {"differ": [d["file"] for d in res["differ"]], "only_stopped": res["only_stopped"],
                      "only_rerun": res["only_rerun"]}, indent=1))
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
