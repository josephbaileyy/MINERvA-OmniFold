#!/usr/bin/env python3
"""RE-2 part C, amendment 1: the rerun's products against the stopped run's, byte for byte (condition 2: a stop).

    python3 -I re2c_determinism.py --stopped $B/partc --rerun $B/partc-r2 \\
        --path-pair /2d-closeout-re2-20261023/partc-r2/=/2d-closeout-re2-20261023/partc/ \\
        --path-pair /deploy-<new>/=/deploy-e079ff05/ --out determinism.json

Every file the two runs share is compared byte for byte, after the rerun's bytes have each --path-pair applied (its
output namespace and its deploy, which records name). Excluded, each named in the result:
  logs/, mpl/, and any path with a `tmp` component
                          run logs (times, durations, paths), caches, and scratch: the period selftest writes into
                          a mkdtemp directory with a random name (periods_ns/tmp/tmp*/); its verdict is in
                          periods/selftest.json, which is compared;
  *.root                  TFile records its creation time. Each ROOT product's matrices are compared through the
                          npz written from the same arrays: s5/uq_production_covariance.root through
                          s5/production_cov.npz (re2c_rollup.py writes both from the same blocks, and build_q's A2
                          stops unless the ROOT total, universe and every band equal the npz's to 1e-12 of the
                          matrix maximum, re2c_build_q.py:387-393);
                          outA/uq_adopted_covariance.root, block_stat.root, block_c08.root and block_playlist.root
                          through outA/cov2d_Q_205.npz's Q, stat, c08 and C_PL (re2c_build_q.py:704-706, 713-715),
                          and build_q's read-back (A4, :678-692, :710) stops unless each ROOT matrix equals its array
                          exactly. block_stat.root's hRel2D is sqrt(diag stat) / x of the same arrays;
  *.pdf                   matplotlib stamps a creation date into a PDF; each figure's PNG twin is compared;
  values_table.*          the one step whose input (the spec) the amendment changed;
  named JSON fields       the receipts record when, where and from which commit they ran:
                          receipt_model_chi2.json's generated_utc and host, RECEIPT-agreement-windows.json's
                          hostname and git_head_at_run; the rest of each file is compared exactly, as parsed JSON.
Files that only one run has: the rerun may add chain.json and SHA256SUMS, which the stopped run never reached; any
other one-sided file is a difference. Exit 0 only if no shared file differs and no other file is one-sided.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

SKIP_DIRS = ("logs", "mpl")
FIELD_SKIP = {"receipts/receipt_model_chi2.json": ("generated_utc", "host"),
              "receipts/RECEIPT-agreement-windows.json": ("hostname", "git_head_at_run")}
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
    parts = rel.split("/")
    if parts[0] in SKIP_DIRS:
        return "run logs or caches"
    if any(q == "tmp" for q in parts[:-1]):
        return "scratch (a tmp component; the period selftest's mkdtemp directory has a random name)"
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
        a_ = s[rel].read_bytes()
        if rel in FIELD_SKIP:   # compared as parsed JSON without the named run-context fields
            ja, jb = json.loads(a_), json.loads(b)
            for k in FIELD_SKIP[rel]:
                ja.pop(k, None)
                jb.pop(k, None)
            res.setdefault("fields_excluded", {})[rel] = list(FIELD_SKIP[rel])
            same = ja == jb
        else:
            same = b == a_
        if same:
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
