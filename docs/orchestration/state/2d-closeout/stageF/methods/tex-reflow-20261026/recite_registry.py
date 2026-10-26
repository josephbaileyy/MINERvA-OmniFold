#!/usr/bin/env python3
"""Re-cite registry rows whose cited line was joined by the TeX reflow.

    recite_registry.py REPO BASE_SRC_DIR MAP.json

For each row of ALIASES, ESTIMATORS, UNRESOLVED-NAMES, ATTRIBUTION, STATUS and WAIVERS whose source is a reflowed
docs/analysis-note/*.tex file:
  * the OLD line is the unique line of the pre-reflow file (BASE_SRC_DIR) with the row's digest; zero or several
    such lines is an error, because the row did not resolve before the reflow;
  * the NEW line is the reflow map's image of it;
  * the new line must contain the row's quote, and its digest must be unique in the new file;
  * the row's line and digest are rewritten; nothing else in the row changes.
Prints every rewrite as `table row: source old -> new, digest old -> new`. Exits 1 on any error and writes nothing.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

TABLES = ("ALIASES", "ESTIMATORS", "UNRESOLVED-NAMES", "ATTRIBUTION", "STATUS", "WAIVERS")


def digest(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def main(argv: list[str]) -> int:
    repo, base_dir, mapf = Path(argv[0]), Path(argv[1]), Path(argv[2])
    maps = json.loads(mapf.read_text())
    errs, plans = [], {}
    for t in TABLES:
        p = repo / "docs/orchestration/registry" / f"{t}.tsv"
        lines = p.read_text().split("\n")
        head = lines[0].split("\t")
        if "defining_source" in head:
            cs, cl, cq, ch = (head.index(c) for c in ("defining_source", "defining_line", "defining_quote",
                                                     "defining_line_sha256"))
        else:
            cs, cl, cq, ch = (head.index(c) for c in ("source", "line", "quote", "line_sha256"))
        out = list(lines)
        for k, raw in enumerate(lines[1:], start=1):
            if not raw.strip():
                continue
            row = raw.split("\t")
            src = row[cs]
            name = src.rsplit("/", 1)[-1]
            if not src.startswith("docs/analysis-note/") or name not in maps:
                continue
            old_lines = (base_dir / name).read_text().split("\n")
            hits = [i for i, l in enumerate(old_lines) if digest(l) == row[ch]]
            if len(hits) != 1:
                errs.append(f"{t} row {k}: {src}: {len(hits)} pre-reflow lines have digest {row[ch]}")
                continue
            old = hits[0]
            new = maps[name][old]  # 1-based
            new_lines = (repo / src).read_text().split("\n")
            nl = new_lines[new - 1]
            if row[cq] not in nl:
                errs.append(f"{t} row {k}: {src}:{new} lacks the quote {row[cq]!r}")
                continue
            nd = digest(nl)
            if sum(digest(l) == nd for l in new_lines) != 1:
                errs.append(f"{t} row {k}: {src}:{new}: digest {nd} is not unique in the new file")
                continue
            if (int(row[cl]), row[ch]) == (new, nd):
                continue
            print(f"{t} row {k}: {src} {row[cl]} (pre-reflow line {old + 1}) -> {new}, digest {row[ch]} -> {nd}")
            row[cl], row[ch] = str(new), nd
            out[k] = "\t".join(row)
        plans[p] = out
    for e in errs:
        print("ERROR " + e)
    if errs:
        return 1
    for p, out in plans.items():
        p.write_text("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
