#!/usr/bin/env python3
"""RE-2 part C, amendment 1: the key schema of the refined records the values spec reads, taken from a real refined
run (RE2-BINDING-C amendment 1, condition 1).

    python3 -I re2c_refined_schema.py --refined-dir <re2c_run.sh refined outdir> --out refined_schema.json

For every source in re2c_values.SOURCES that has a refined file, it records the file's sha256 and:
  json  every key path, with each leaf's type (number, string, bool, null) and each list's length; a string value
        is kept verbatim only when it says something was not computed or run, so the schema shows which fields the
        refined arm leaves empty (S5-22's bkg_separable is the case that stopped the bound run);
  text  the printout with every number that has a decimal point (with or without an exponent) replaced by 1.0.
        The line structure the spec's regexes read stays, and the measured values go. Integers and integer-mantissa
        labels stay, because the regexes anchor on counts such as "ndf = 205" and rcond labels such as "1e-04".
test_re2c.py builds its stand-in refined tree from this schema, checks that the tree's schema equals the
committed one, and requires every spec row to resolve or be listed as unmatched. No measured non-integer value is
recorded; integers (counts, ranks, modes kept) are, as the structure the regexes need.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import re2c_values as V  # noqa: E402

FLOAT = re.compile(r"(?<![\w.])[-+]?(?:\d+\.\d*|\.\d+)(?:[eE][-+]?\d+)?(?![\w.])")
EMPTY = re.compile(r"not (computed|run)", re.I)


def schema(v):
    """The type skeleton of a JSON value."""
    if isinstance(v, dict):
        return {k: schema(x) for k, x in v.items()}
    if isinstance(v, list):
        return {"__list__": [schema(x) for x in v]}
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, (int, float)):
        return "number"
    if v is None:
        return "null"
    return f"string:{v}" if EMPTY.search(v) else "string"


def mask(text):
    return FLOAT.sub("1.0", text)


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def build(refined_dir):
    out = {}
    for key, (_, rel) in sorted(V.SOURCES.items()):
        if rel is None:
            continue
        p = Path(refined_dir) / rel
        rec = {"file": rel, "sha256": sha256(p)}
        if p.suffix == ".json":
            rec["kind"], rec["schema"] = "json", schema(json.loads(p.read_text()))
        else:
            rec["kind"], rec["template"] = "text", mask(p.read_text())
        out[key] = rec
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--refined-dir", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    doc = {"schema": "re2c-refined-schema/1", "refined_dir": a.refined_dir, "sources": build(a.refined_dir)}
    Path(a.out).write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: v["sha256"][:16] for k, v in doc["sources"].items()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
