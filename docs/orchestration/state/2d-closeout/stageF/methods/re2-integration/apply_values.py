#!/usr/bin/env python3
"""Apply RE-2 part C's regenerated values (values_table.tsv) to docs/analysis-note/, and write their ledger rows.

usage: apply_values.py <worktree> [--base REF] [--dry-run] [--ledger-out FILE]

The table is re2/run/partc_r2/partc-r2/values_table.tsv (250 rows). Only rows whose status is "control PASS" are
applied; the 8 new products have no printed site, \\fpsAbove (46) failed its control, and `ro-fps` cites
VALIDATION_LEDGER.md, which is not a deliverable (its printed site, sec_fps.tex, is wording item W3). Nothing is typed
by hand: each old and new string is the table's `printed` and `refined_rendered` field.

  - a values.tex macro row (`N/values.tex:\\name`) is applied once, at its definition, which must be unique and carry
    exactly the printed value;
  - any other row (`N/<file>:<line>`) is applied on that line, as the line reads at BASE (the tree the table was
    anchored on has the same deliverable sources). The printed characters must occur on the line as a whole number
    token (not inside a longer number). If a line holds more occurrences of the token than rows that cite it, the row
    is AMBIGUOUS and is not applied: it is reported for handling by hand.

Every source file is checked to equal its BASE version before anything is written, so a second run refuses instead of
compounding. --dry-run writes nothing and prints the plan. --ledger-out writes one "V" ledger row per applied row
(kind, id, file, base line, old printed, new printed, new context, old context or "-", source, source row id, source
field), read by check_ledger.py.
"""
import csv
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
TABLE_REL = "re2/run/partc_r2/partc-r2/values_table.tsv"  # relative to stageF/methods
TABLE = HERE.parent / TABLE_REL
NOTE = "docs/analysis-note"
WIN = 24  # characters of context kept on each side of a value in its ledger row


def token_re(tok):
    return re.compile(r"(?<![0-9.])" + re.escape(tok) + r"(?![0-9])")


def strip_comment(line):
    return re.sub(r"(?<!\\)%.*", "", line)


def collapse(t):
    return re.sub(r"\s+", " ", t).strip()


def git_show(wt, base, rel):
    return subprocess.run(["git", "-C", str(wt), "show", f"{base}:{rel}"], capture_output=True, text=True,
                          check=True).stdout


def load_rows():
    with open(TABLE, newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def window(line, start, length):
    """The comment-stripped context of a value at [start, start+length) in `line`, whitespace collapsed."""
    code = strip_comment(line)
    if start + length > len(code):
        raise ValueError("value inside a comment")
    return collapse(code[max(0, start - WIN): start + length + WIN])


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    base, ledger_out = "origin/main", None
    if "--base" in args:
        i = args.index("--base"); base = args[i + 1]; del args[i:i + 2]
    if "--ledger-out" in args:
        i = args.index("--ledger-out"); ledger_out = Path(args[i + 1]); del args[i:i + 2]
    wt = Path(args[0]).resolve()
    rows = load_rows()
    applied, skipped, problems = [], [], []
    by_file = defaultdict(list)
    for r in rows:
        if r["status"] != "control PASS":
            skipped.append((r["id"], r["status"] or "new product"))
            continue
        if not r["where"].startswith("N/"):
            skipped.append((r["id"], f"site {r['where']} is not a deliverable (handled as wording)"))
            continue
        f, _, loc = r["where"][2:].rpartition(":")
        by_file[f].append((loc, r))

    new_text, ledger = {}, []
    for f, items in sorted(by_file.items()):
        rel = f"{NOTE}/{f}"
        cur = (wt / rel).read_text()
        if cur != git_show(wt, base, rel):
            print(f"REFUSE: {rel} differs from {base}; this script applies to the base text only"); sys.exit(2)
        lines = cur.split("\n")
        macros = [(loc, r) for loc, r in items if loc.startswith("\\")]
        numbered = defaultdict(list)
        for loc, r in items:
            if not loc.startswith("\\"):
                numbered[int(loc)].append(r)
        for loc, r in macros:
            pat = re.compile(r"\\newcommand\{" + re.escape(loc) + r"\}\{([^}]*)\}")
            hits = [(i, m) for i, l in enumerate(lines) for m in [pat.search(strip_comment(l))] if m]
            if len(hits) != 1 or hits[0][1].group(1) != r["printed"]:
                problems.append((r["id"], f"macro {loc}: {len(hits)} definitions / value mismatch")); continue
            i, m = hits[0]
            old_def, new_def = m.group(0), m.group(0).replace("{" + r["printed"] + "}", "{" + r["refined_rendered"] + "}")
            changed = r["printed"] != r["refined_rendered"]
            if changed:
                l = lines[i].replace(old_def, new_def, 1)
                if "%" in l[len(new_def):]:
                    head, _, tail = l.partition("%")
                    l = (f"{head}% RE-2 E_R/Q_R {float(r['refined_value']):.6g} (re2-integration/ledger.tsv row "
                         f"{r['id']}); was {r['printed']}:{tail}")
                lines[i] = l
            ledger.append(["V", r["id"], f, str(i + 1), r["printed"], r["refined_rendered"], new_def,
                           old_def if changed else "-", TABLE_REL, r["id"], "refined_rendered"])
            applied.append((r["id"], f, i + 1, r["printed"], r["refined_rendered"]))
        for ln, rs in sorted(numbered.items()):
            line = lines[ln - 1]
            code = strip_comment(line)
            toks = defaultdict(list)
            for r in rs:
                toks[r["printed"]].append(r)
            spans, ok_rows = [], []
            for tok, trs in toks.items():
                occ = [m for m in token_re(tok).finditer(code)]
                if not occ and tok.startswith("-"):  # the sign printed as $-$ or outside \SI
                    occ = [m for m in token_re(tok[1:]).finditer(code)]
                    trs_tok = tok[1:]
                else:
                    trs_tok = tok
                news = {r["refined_rendered"].lstrip("-") if trs_tok != tok else r["refined_rendered"] for r in trs}
                if not occ:
                    for r in trs:
                        problems.append((r["id"], f"{f}:{ln}: {tok!r} not on the line"))
                    continue
                if len(occ) > len(trs) and len(news) == 1 and next(iter(news)) == trs_tok:
                    # unchanged value printed more often than cited: nothing is written, the rows still verify
                    pass
                elif len(occ) != len(trs) or len(news) != 1:
                    for r in trs:
                        problems.append((r["id"], f"{f}:{ln}: AMBIGUOUS, {len(occ)} occurrences of {tok!r} for "
                                                  f"{len(trs)} rows with new values {sorted(news)}"))
                    continue
                new = next(iter(news))
                for k, m in enumerate(occ):
                    spans.append((m.start(), m.end(), trs_tok, new, trs[min(k, len(trs) - 1)]))
                ok_rows += trs
            spans.sort()
            # rebuild the line and remember where each value lands in it
            out, pos, where_new = [], 0, []
            for s, e, old, new, r in spans:
                out.append(line[pos:s]); where_new.append((sum(map(len, out)), new, s, old, r)); out.append(new); pos = e
            out.append(line[pos:])
            nline = "".join(out)
            seen = set()
            for sn, new, so, old, r in where_new:
                if r["id"] in seen:
                    continue
                seen.add(r["id"])
                changed = old != new
                ledger.append(["V", r["id"], f, str(ln), r["printed"], r["refined_rendered"],
                               window(nline, sn, len(new)), window(line, so, len(old)) if changed else "-",
                               TABLE_REL, r["id"], "refined_rendered"])
                applied.append((r["id"], f, ln, r["printed"], r["refined_rendered"]))
            lines[ln - 1] = nline
        new_text[rel] = "\n".join(lines)

    for rid, why in problems:
        print(f"PROBLEM {rid}: {why}")
    for rid, why in skipped:
        print(f"skip    {rid}: {why}")
    nchg = sum(1 for a in applied if a[3] != a[4])
    print(f"APPLY :: {len(applied)} rows verified at their site ({nchg} changed, {len(applied) - nchg} unchanged at "
          f"printed precision); {len(skipped)} skipped by status/site; {len(problems)} problems")
    if dry:
        return 1 if problems else 0
    for rel, t in new_text.items():
        (wt / rel).write_text(t)
    if ledger_out:
        with open(ledger_out, "w") as fh:
            for row in ledger:
                fh.write("\t".join(row) + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
