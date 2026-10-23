#!/usr/bin/env python3
"""What is this estimator, and where is every result on it?

    whatis.py "<name>" [--repo DIR] [--per-file N] [--no-grep] [--list]

<name> is any registered alias ("configuration (e)", "R", "B0", "--candidate R", "negweight-refined",
"s5p data unfold", "400/31", ...) or a registry id. The tool resolves it against
docs/orchestration/registry/ESTIMATORS.tsv and ALIASES.tsv and prints, for each estimator it names:
  1. the definition and the defining record (file:line), and every alias with the line it is read from;
  2. every RESULTS-INDEX.tsv row attributed to it, grouped by receipt;
  3. a repository-wide `git grep -P` over the tracked tree for EVERY alias pattern of that estimator (not only
     the one typed), hits grouped by file, with the alias each line matched.
A name that resolves to more than one estimator is reported as AMBIGUOUS, with each reading, before anything is
searched: one name meaning two estimators is the defect this registry exists to expose.
--list prints every estimator and alias. Exit 0 if the name resolved, 2 if it did not.

Absence claims: a statement that no result exists for an estimator must cite the search behind it; the line this
tool prints last ("Search: ... @ <sha>") is the form RECORDS-RULES.md requires.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reglib  # noqa: E402

INDEX_TSV = f"{reglib.REGISTRY_DIR}/RESULTS-INDEX.tsv"


def grep(repo: Path, pattern: str) -> list[tuple[str, int, str]]:
    out = subprocess.run(["git", "-C", str(repo), "grep", "--cached", "-n", "-I", "-P", "-e", pattern],
                         capture_output=True, env=reglib.git_env())
    if out.returncode not in (0, 1):
        raise RuntimeError(f"git grep -P {pattern!r} failed: {out.stderr.decode(errors='replace')}")
    res = []
    for line in out.stdout.decode("utf-8", errors="replace").splitlines():
        parts = line.split(":", 2)
        if len(parts) == 3 and parts[1].isdigit():
            res.append((parts[0], int(parts[1]), parts[2]))
    return res


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("name", nargs="?")
    ap.add_argument("--repo", type=Path, default=None)
    ap.add_argument("--per-file", type=int, default=3, help="hit lines printed per file (all are counted)")
    ap.add_argument("--no-grep", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--distinctive", action="store_true",
                    help="grep only aliases no other estimator shares and that are not bare iteration counts")
    a = ap.parse_args(argv)
    repo = reglib.repo_root(a.repo or Path.cwd())
    index = reglib.Index(repo)
    ests = reglib.read_tsv(index, reglib.ESTIMATORS)
    als = reglib.read_tsv(index, reglib.ALIASES)
    by_id = {e["id"]: e for e in ests}
    if a.list or not a.name:
        for e in ests:
            print(f"{e['id']}: {e['summary']}")
            for al in als:
                if al["estimator"] == e["id"]:
                    print(f"    {al['kind']:<16} {al['alias']}   [{al['source']}:{al['line']}]")
        return 0
    hits = reglib.resolve(a.name, ests, als)
    unres = reglib.unresolved(a.name, reglib.read_tsv(index, reglib.UNRESOLVED)) if index.has(reglib.UNRESOLVED) else []
    for u in unres:
        print(f"UNRESOLVED NAMING: {u['name']!r} also occurs at {u['source']}:{u['line']} in a sense the sources do "
              f"not map to any registered estimator: {u['why']}")
    if not hits:
        print(f"UNRESOLVED: {a.name!r} is not a registered id or alias. `whatis.py --list` prints every alias. "
              "If it names an estimator a record prints, add it to ALIASES.tsv with its source line.")
        return 2
    if len(hits) > 1:
        print(f"AMBIGUOUS: {a.name!r} names {len(hits)} registered estimators:")
        for eid, why in hits.items():
            print(f"  {eid}: {by_id[eid]['summary']}")
            for w in why:
                print(f"      because: {w}")
        print("Each reading is reported below. Quote the registry id, not this name.\n")
    idx_rows = reglib.read_tsv_text(index.text(INDEX_TSV) or "") if index.has(INDEX_TSV) else []
    head = reglib.git(repo, "rev-parse", "--short=12", "HEAD").decode().strip()
    for eid in hits:
        e = by_id[eid]
        print(f"=== {eid}")
        print(f"  {e['summary']}")
        print(f"  defined: {e['defining_source']}:{e['defining_line']}   code: {e['code_path']}")
        mine = [al for al in als if al["estimator"] == eid]
        shared = defaultdict(list)
        for al in als:
            if al["estimator"] != eid:
                shared[al["pattern"]].append(al["estimator"])
        print(f"  aliases ({len(mine)}):")
        for al in mine:
            also = sorted(set(shared.get(al["pattern"], [])))
            flag = f"   ** SHARED with {', '.join(also)}: this alias alone does not identify the estimator" if also else ""
            print(f"    {al['kind']:<16} {al['alias']}   [{al['source']}:{al['line']}]{flag}")
        rows = [r for r in idx_rows if r["estimator"] == eid]
        by_src = defaultdict(list)
        for r in rows:
            by_src[r["source"]].append(r)
        print(f"  results index: {len(rows)} rows in {len(by_src)} receipts attributed to {eid}")
        for src, rs in sorted(by_src.items()):
            metrics = sorted({r["metric"] for r in rs})
            statuses = sorted({r["status"] for r in rs})
            print(f"    {src}: {len(rs)} rows; metrics {', '.join(metrics)}; status {', '.join(statuses)}")
        if a.no_grep:
            continue
        files: dict[str, list[tuple[int, str, str]]] = defaultdict(list)
        searched = [al for al in mine if not (a.distinctive and (shared.get(al["pattern"]) or al["kind"] == "iterations"))]
        print(f"  per-alias hits ({len(searched)} of {len(mine)} patterns searched):")
        for al in searched:
            got = grep(repo, al["pattern"])
            print(f"    {len(got):>6} lines  {al['alias']}   /{al['pattern']}/")
            for path, ln, text in got:
                files[path].append((ln, al["alias"], text))
        pop = {r["source"] for r in idx_rows}
        attributed_to = defaultdict(set)
        for r in idx_rows:
            attributed_to[r["source"]].add(r["estimator"])
        unattributed = sorted(p for p in files if p in pop and p not in by_src)
        total = sum(len({(ln) for ln, _, _ in v}) for v in files.values())
        print(f"  repository grep ({len(searched)} alias patterns, staged tree): {total} lines in "
              f"{len(files)} files")
        for path in sorted(files):
            lines = sorted({(ln, text) for ln, _, text in files[path]})
            names = sorted({al for _, al, _ in files[path]})
            print(f"    {path}: {len(lines)} lines [{'; '.join(names)}]")
            for ln, text in lines[:a.per_file]:
                print(f"        {ln}: {text.strip()[:150]}")
        if unattributed:
            print(f"  receipts in the results index that mention an alias of {eid} but have no row attributed to it "
                  f"({len(unattributed)}); read them before saying a result does not exist:")
            for p in unattributed:
                print(f"    {p}  (rows attributed to: {', '.join(sorted(attributed_to[p]))})")
        print(f"  Search: {'; '.join(al['alias'] for al in searched)} @ {head}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
