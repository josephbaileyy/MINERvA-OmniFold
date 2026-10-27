#!/usr/bin/env python3
"""Cross-count the consolidation's sites against the cost list (director, 2026-10-27).

usage: check_sites.py COST_LIST.md SITES.tsv [LEDGER.md]
       check_sites.py --self-test

COST_LIST.md is note-n3/content-reduction.md. SITES.tsv is this PR's disposition table, one row per [C] site:
  row  file  line  disposition  ledger
with disposition one of applied, kept (guardrail), excluded (a ruling) or merged (already merged before this PR).

The cost list is parsed here without the extraction regex that once dropped 6 of 60 sites: the text of each row (from
its "### R<nn>." heading to the next) is split into bullets at every "- [" marker, and every bullet that begins
"- [C]" is one site: the FIRST file:line reference in it (a run of letters, digits and "_" ending ".tex", then ":"
and digits). Later references in the same bullet name its homes or neighbours, not further sites (each site has its
own bullet in the cost list). The check fails unless the disposition table holds exactly that set of (row, file, first line), no
more and no less, every disposition is one of the four, and every applied or kept site names a ledger row. Given LEDGER.md (this PR's
ledger.md), it also fails on a named ledger row that the ledger does not hold, and on a ledger row that no site names.
"""
import csv
import re
import sys

DISPOSITIONS = {"applied", "kept", "excluded", "merged"}


def cost_list_sites(text: str) -> set[tuple[str, str, str]]:
    sites = set()
    rows = ("\n" + text).split("\n### R")[1:]
    for chunk in rows:
        rid = "R" + chunk[:2]
        body = chunk.split("\n## ")[0]
        for bullet in body.split("- [")[1:]:
            if not bullet.startswith("C]"):
                continue
            k = 0
            while True:
                k = bullet.find(".tex:", k)
                if k < 0:
                    break
                start = k
                while start > 0 and (bullet[start - 1].isalnum() or bullet[start - 1] == "_"):
                    start -= 1
                name = bullet[start:k] + ".tex"
                j = k + 5
                digits = ""
                while j < len(bullet) and bullet[j].isdigit():
                    digits += bullet[j]; j += 1
                if digits and start < k:
                    sites.add((rid, name, digits))
                    break
                k += 5
    return sites


def check(cost_text: str, table_rows: list[dict], ledger_text: str | None = None) -> list[str]:
    want = cost_list_sites(cost_text)
    fails = []
    have = set()
    for r in table_rows:
        key = (r["row"], r["file"], r["line"])
        if key in have:
            fails.append(f"duplicate disposition row {key}")
        have.add(key)
        if r["disposition"] not in DISPOSITIONS:
            fails.append(f"{key}: disposition {r['disposition']!r} is not one of {sorted(DISPOSITIONS)}")
        if r["disposition"] in {"applied", "kept"} and not r.get("ledger", "").strip():
            fails.append(f"{key}: an {r['disposition']} site must name its ledger row")
    for k in sorted(want - have):
        fails.append(f"MISSING: the cost list's [C] site {k} has no disposition")
    for k in sorted(have - want):
        fails.append(f"EXTRA: {k} is not a [C] site of the cost list")
    if ledger_text is not None:
        ids = set(re.findall(r"^\| (R\d+[a-z]) \|", ledger_text, re.M))
        named = {r["ledger"].strip() for r in table_rows if r.get("ledger", "").strip()}
        for k in sorted(named - ids):
            fails.append(f"a site names ledger row {k}, which the ledger does not hold")
        for k in sorted(ids - named):
            fails.append(f"ledger row {k} is named by no site")
    return fails


def self_test() -> int:
    doc = ("### R01. a\n- [keep] `a.tex:1` x\n- [C] `b.tex:2` y (home `a.tex:1`)\n- [C] `c_3d.tex:30` z\n- [D] `d.tex:4`\n"
           "### R02. b\n- [C] `sec_5d.tex:77-78` w (shared)\n")
    good = [{"row": "R01", "file": "b.tex", "line": "2", "disposition": "applied", "ledger": "R01a"},
            {"row": "R01", "file": "c_3d.tex", "line": "30", "disposition": "kept", "ledger": "R01b"},
            {"row": "R02", "file": "sec_5d.tex", "line": "77", "disposition": "excluded", "ledger": ""}]
    cases = [("complete table", good, False),
             ("a site dropped (the 6-of-60 failure)", good[:2], True),
             ("an extra site", good + [{"row": "R02", "file": "x.tex", "line": "9", "disposition": "applied",
                                        "ledger": "R02b"}], True),
             ("a [D] site counted as [C]", good + [{"row": "R01", "file": "d.tex", "line": "4",
                                                   "disposition": "applied", "ledger": "R01c"}], True),
             ("a digit-bearing file name dropped", [good[0], good[2]], True),
             ("an applied site with no ledger row", [dict(good[0], ledger="")] + good[1:], True),
             ("an unknown disposition", [dict(good[0], disposition="moved")] + good[1:], True)]
    led = "| R01a | f |\n| R01b | f |\n"
    cases = [(n, r, s, None) for n, r, s in cases] + [
        ("ledger and sites agree", good, False, led),
        ("a site names an absent ledger row", good, True, "| R01a | f |\n"),
        ("a ledger row no site names", good, True, led + "| R02c | f |\n")]
    ok = True
    for name, rows, should_fail, ledger in cases:
        got = bool(check(doc, rows, ledger))
        print(f"  {'ok  ' if got == should_fail else 'FAIL'} {name}: {'fails' if got else 'passes'}")
        ok &= got == should_fail
    print(f"CHECK-SITES SELF-TEST :: {'PASS' if ok else 'FAIL'} ({len(cases)} cases)")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    cost, table = argv[:2]
    ledger = open(argv[2], encoding="utf-8").read() if len(argv) > 2 else None
    rows = list(csv.DictReader(open(table, encoding="utf-8"), delimiter="\t"))
    fails = check(open(cost, encoding="utf-8").read(), rows, ledger)
    want = cost_list_sites(open(cost, encoding="utf-8").read())
    counts = {d: sum(1 for r in rows if r["disposition"] == d) for d in sorted(DISPOSITIONS)}
    for f in fails:
        print("  FAIL " + f)
    print(f"CHECK-SITES :: {'PASS' if not fails else 'FAIL'} (cost list [C] sites {len(want)}; table {len(rows)}: "
          + ", ".join(f"{k} {v}" for k, v in counts.items()) + ")")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
