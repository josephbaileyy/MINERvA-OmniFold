"""C0 for RE-2-shapes (the director, 2026-11-14): the identity run against partc-r2, file by file, by SHA256SUMS.

The identity run is re2c_run.sh's refined arm with the driver in mode identity, on a deploy at partc-r2's own commit.
re2c_determinism.py (re2's comparator, the one behind partc_r2/determinism_dry_amend2.json) compares the two trees
first. Its output is the --determinism record. This script then classifies every line of the two SHA256SUMS:
  bitwise        the same digest in both;
  path-pairs     the comparator proved the file equal after the path pairs (its digest pair, reason "equal" or
                 "json-rule"), or it is a ROOT file paired through its byte-equal npz twin ("root-twin");
  values_table.tsv / values_table.json must be BITWISE (the director's M2): the comparator skips them (its
                 SKIP_NAMES, a reason that held only for partc vs partc-r2); here both runs use the same spec at B, and
                 partc-r2's two files hold no path, host or time. A differing digest is OTHER.
  scratch:<rule> the period selftest's mkdtemp directory, the one named exception (below);
  skipped:<why>  a category the comparator skips and C0 accepts: logs/, mpl/, *.root (twin-backed: a differing twin
                 shows in the comparator's differences), *.pdf (its PNG twin is compared);
  SHA256SUMS     the file itself, which lists the skipped files' digests (it is never in either list);
  OTHER          anything else, or a file in only one list: a STOP to the director.
The period selftest's scratch (re2c_analyze_periods.py:376 at B: tempfile.mkdtemp(dir=f"{NS}/tmp"), never removed) sits
under periods_ns/tmp/tmpXXXXXXXX/ in each run, and re2c_run.sh:199 excludes only ./tmp/*, so both SHA256SUMS list it
under different random names (coverage-5b-audit blocker 1; the director's B1). The exception matches only that exact
path and the five files partc-r2's own directory holds; each list must hold exactly one such directory, whose name is
replaced by "<mkdtemp>" before the lists are joined (a missing or extra file is then one-sided: OTHER). Each file's
rule, from a read-only O_NOATIME probe of partc (tmp8lbdy9iq) against partc-r2 (tmp6hw50588), 2026-11-15:
  id.txt, inj.txt  bitwise;
  id.json          equal once the path pairs and then c0's mkdtemp name -> partc-r2's are applied to c0's bytes;
  inj.json         the same, plus inj.root's digest (it records inj.root's path and sha256) -> partc-r2's;
  inj.root         not deterministic (TFile creation time): accepted, but its listed digest must be the sha256 that
                   the same run's inj.json records for it, in each run.
Any other line under periods_ns/tmp/ is OTHER. The two random names are recorded.
Two named rules (the director's ruling (a2), 2026-11-15, after the first run's C0 STOP):
  R1  receipts/receipt_model_chi2.json is compared field by field (parsed JSON, c0's bytes after the path pairs) with
      only repo_commit set aside, beside the comparator's FIELD_SKIP pair (generated_utc, host). repo_commit is
      `git -C REPO rev-parse HEAD` with REPO = $MNV_REPO (receipt_model_chi2_2d.py:56, :307-308 at B), and re2c_run.sh
      sets MNV_REPO=$A, the shared /pscratch/sd/j/josephrb/MINERvA-OmniFold checkout, whose HEAD moved after partc-r2
      (32e403b8 -> ed3590ea). Every other field, the chi2 values included, must be equal. When R1 holds, the
      comparator's differ entry for this file is accepted.
  R2  the comparator's only_stopped set is accepted only when it equals, by name, FIG1_LATER (the 8 files the later
      Fig. 1 steps added to partc-r2's directory), each absent from partc-r2's committed SHA256SUMS. Any other
      only_stopped file, or any one of the 8 listed in that SHA256SUMS, is a STOP.
Exit 0 only if no line is OTHER, the two lists name the same files after that replacement, and the comparator's own
differences are at most SHA256SUMS. Otherwise 1.
    python3 -I c0_sums.py --comparator re2c_determinism.py --determinism c0-determinism.json \
        --partc-r2 <dir> --c0 <dir> --path-pair NEW=OLD [--path-pair ...] --out c0-sums.json
"""
import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

SCRATCH = re.compile(r"^(periods_ns/tmp/)(tmp[a-z0-9_]{8})(/(?:id\.json|id\.txt|inj\.json|inj\.root|inj\.txt))$")
VALUES = ("values_table.tsv", "values_table.json")
RECEIPT = "receipts/receipt_model_chi2.json"
RECEIPT_SET_ASIDE = ("generated_utc", "host", "repo_commit")   # the comparator's FIELD_SKIP pair + repo_commit (R1)
FIG1_LATER = frozenset(f"{d}/{f}" for d in ("fig1", "fig1-a2-cabbbbc3")
                       for f in ("RUN-fig1.txt", "fig1_run.log", "pins.json", "uqmedian.tex"))   # R2


def sums(path):
    """{rel: digest} with the one mkdtemp directory's name replaced, and that name (None if absent)."""
    out, names = {}, set()
    for ln in open(path).read().splitlines():
        d, rel = ln.split(None, 1)
        rel = rel[2:] if rel.startswith("./") else rel
        m = SCRATCH.match(rel)
        if m:
            names.add(m.group(2))
            rel = m.group(1) + "<mkdtemp>" + m.group(3)
        if rel in out:
            raise SystemExit(f"{path}: {rel} listed twice")
        out[rel] = d
    if len(names) > 1:
        raise SystemExit(f"{path}: {len(names)} mkdtemp directories under periods_ns/tmp: {sorted(names)}")
    return out, (names.pop() if names else None)


def real(root, rel, name):
    return Path(root, rel.replace("<mkdtemp>", name))


def receipt(a, pp):
    """R1: receipt_model_chi2.json equal field by field with only RECEIPT_SET_ASIDE set aside."""
    b = Path(a.c0, RECEIPT).read_bytes()
    for new, old in pp:
        b = b.replace(new, old)
    ja, jb = json.loads(Path(a.partc_r2, RECEIPT).read_bytes()), json.loads(b)
    for k in RECEIPT_SET_ASIDE:
        ja.pop(k, None)
        jb.pop(k, None)
    if ja == jb:
        return "R1 (receipt equal without repo_commit and the comparator's FIELD_SKIP pair)"
    diff = sorted(k for k in set(ja) | set(jb) if ja.get(k) != jb.get(k))
    return f"OTHER (receipt fields differ beyond repo_commit: {diff})"


def recorded(doc, suffix):
    """Every sha256 that inj.json records beside a "path" ending in suffix, at any depth."""
    out = set()
    if isinstance(doc, dict):
        if isinstance(doc.get("path"), str) and doc["path"].endswith(suffix) and "sha256" in doc:
            out.add(doc["sha256"])
        for v in doc.values():
            out |= recorded(v, suffix)
    elif isinstance(doc, list):
        for v in doc:
            out |= recorded(v, suffix)
    return out


def scratch(rel, a, pp, s, r, s_tmp, r_tmp):
    """The class of one differing line in the selftest's mkdtemp directory (rules in the module docstring)."""
    f = rel.rsplit("/", 1)[1]
    root = "periods_ns/tmp/<mkdtemp>/inj.root"
    if f in ("id.txt", "inj.txt"):
        return "OTHER (scratch: must be bitwise)"
    if f == "inj.root":
        okr = all(recorded(json.loads(real(t, "periods_ns/tmp/<mkdtemp>/inj.json", n).read_text()),
                           f"/periods_ns/tmp/{n}/inj.root") == {lst[root]}
                  for t, n, lst in ((a.partc_r2, s_tmp, s), (a.c0, r_tmp, r)))
        return "scratch (inj.root: TFile time; digest = its run's inj.json record)" if okr else "OTHER (scratch: inj.root digest not its inj.json's)"
    b = real(a.c0, rel, r_tmp).read_bytes()
    for new, old in pp:
        b = b.replace(new, old)
    b = b.replace(r_tmp.encode(), s_tmp.encode())
    if f == "inj.json":
        b = b.replace(r[root].encode(), s[root].encode())
    if hashlib.sha256(b).hexdigest() == s[rel] == hashlib.sha256(real(a.partc_r2, rel, s_tmp).read_bytes()).hexdigest():
        return f"scratch ({f}: equal after the path pairs and the mkdtemp name" + (", inj.root digest)" if f == "inj.json" else ")")
    return f"OTHER (scratch: {f} differs after normalization)"


def main():
    ap = argparse.ArgumentParser()
    for k in ("--comparator", "--determinism", "--partc-r2", "--c0", "--out"):
        ap.add_argument(k, required=True)
    ap.add_argument("--path-pair", action="append", default=[])
    a = ap.parse_args()
    spec = importlib.util.spec_from_file_location("re2c_determinism", a.comparator)
    det = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(det)
    pp = [tuple(x.encode() for x in p.split("=", 1)) for p in a.path_pair]
    rec = json.load(open(a.determinism))
    pairs = rec["digest_pairs"]
    (s, s_tmp), (r, r_tmp) = sums(f"{a.partc_r2}/SHA256SUMS"), sums(f"{a.c0}/SHA256SUMS")
    rows, counts = {}, {}
    for rel in sorted(set(s) | set(r)):
        if rel not in s or rel not in r:
            cls = "OTHER (only in " + ("partc-r2" if rel in s else "c0") + ")"
        elif s[rel] == r[rel]:
            cls = "bitwise"
        elif rel.split("/")[-1] in VALUES:
            cls = "OTHER (values table differs)"
        elif rel == RECEIPT:
            cls = receipt(a, pp)
        elif rel.startswith("periods_ns/tmp/<mkdtemp>/"):
            cls = scratch(rel, a, pp, s, r, s_tmp, r_tmp)
        elif r[rel] in pairs and pairs[r[rel]]["stopped"] == s[rel]:
            cls = "path-pairs (" + pairs[r[rel]]["reason"] + ")"
        elif det.skipped(rel):
            cls = "skipped: " + det.skipped(rel)
        else:
            cls = "OTHER"
        rows[rel] = cls
        key = cls if cls.startswith(("skipped", "scratch")) else cls.split(" (")[0]
        counts[key] = counts.get(key, 0) + 1
    other = sorted(k for k, v in rows.items() if v.startswith("OTHER"))
    det_differ = [d["file"] for d in rec["differ"]]
    r1 = rows.get(RECEIPT, "").startswith("R1")
    r2 = set(rec["only_stopped"]) == FIG1_LATER and not (FIG1_LATER & set(s))
    det_extra = ([] if r2 else rec["only_stopped"]) + rec["only_rerun"] + rec["root_untabled"] + \
        [f for f in det_differ if f != "SHA256SUMS" and not (f == RECEIPT and r1)]
    ok = not other and not det_extra and set(s) == set(r)
    res = {"schema": "re2shapes-c0/4", "R1_receipt": r1, "R2_only_stopped_fig1_later": r2, "verdict": "PASS" if ok else "STOP", "n_lines": {"partc-r2": len(s), "c0": len(r)},
           "mkdtemp": {"partc-r2": s_tmp, "c0": r_tmp}, "path_pairs": a.path_pair,
           "counts": counts, "other": other, "comparator": {"verdict": rec["verdict"], "differ": det_differ,
                                                           "only_stopped": rec["only_stopped"], "only_rerun": rec["only_rerun"],
                                                           "root_untabled": rec["root_untabled"],
                                                           "compared": rec["compared"], "equal": rec["equal"]},
           "rows": rows}
    open(a.out, "w").write(json.dumps(res, indent=1) + "\n")
    print(f"C0 {res['verdict']}: lines {len(s)}/{len(r)} mkdtemp {s_tmp}/{r_tmp} counts {json.dumps(counts, sort_keys=True)} "
          f"other {other} comparator {rec['verdict']} differ {det_differ} extra {det_extra}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
