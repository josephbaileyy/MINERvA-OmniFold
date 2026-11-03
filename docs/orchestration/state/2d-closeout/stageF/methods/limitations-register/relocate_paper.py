"""relocate_paper.py -- re-locate the register's paper rows (Q01-Q44) in the current paper.

usage: python3 -I relocate_paper.py PAPERDIR AUX OUT.json [--self-test]

paper-rows.tsv gives, per row, the literal phrases that state it (`phrases`, |-separated, the first is its home), the
phrases of wording that must NO LONGER print (`gone`), and the row's class, status, quote and route. Phrases are
matched in the comment-stripped TeX of main_paper.tex and paper_body.tex. The run FAILS if:
  - a `phrases` entry prints nowhere (the row says its statement prints and it does not);
  - a `gone` entry still prints (the row says the wording left and it did not);
  - a route cites a record absent from the repository (build_register.missing_records);
  - a class or status is outside the register's vocabulary (the class may carry a parenthesised qualifier).
loc lists every line any phrase prints on, the home first; section is the home's, numbered from AUX (the built
main_paper.aux). Writes OUT.json in the register's shape (id, q, doc, loc, section, quote, cls, status, route, line,
order) plus `prints`, the gone wording where there is some.
"""
import csv
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = ("main_paper", "paper_body")
SEC = re.compile(r"\\(section|subsection|subsubsection)\*?\{(.+?)\}")


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def lines_of(paperdir):
    return {f: [re.sub(r"(?<!\\)%.*", "", l) for l in (Path(paperdir) / f"{f}.tex").read_text(encoding="utf-8").split("\n")]
            for f in FILES}


def sections(text, aux):
    nums = dict(re.findall(r"\\newlabel\{([^}]+)\}\{\{([^}]*)\}", Path(aux).read_text(errors="replace"))) if aux else {}
    out, cur = {}, []
    L = text["paper_body"]
    for i, l in enumerate(L, 1):
        m = SEC.search(l)
        if m:
            lvl = ["section", "subsection", "subsubsection"].index(m.group(1))
            lab = (re.search(r"\\label\{([^}]+)\}", l) or (re.search(r"\\label\{([^}]+)\}", L[i]) if i < len(L) else None))
            num = nums.get(lab.group(1), "") if lab else ""
            title = re.sub(r"\s+", " ", re.sub(r"\\[A-Za-z]+|[{}$~]", " ", m.group(2))).strip()
            cur = cur[:lvl] + [(num.replace("\\,", " ") + " " if num else "") + title]
        out[i] = " > ".join(cur)
    return out


def hits(text, phrase):
    return [(f, i) for f in FILES for i, l in enumerate(text[f], 1) if phrase in l]


def relocate(paperdir, aux, out, table=HERE / "paper-rows.tsv"):
    reg = _mod(HERE / "build_register.py", "build_register")
    text = lines_of(paperdir)
    secs = sections(text, aux)
    root = reg.repo_root()
    tracked = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True,
                             check=True).stdout.split("\n")
    ki = set(re.findall(r"^\| *(\d+) *\|", (root / "KNOWN_ISSUES.md").read_text(), re.M))
    vl = set(re.findall(r"\bVL\d{2,3}\b", (root / "VALIDATION_LEDGER.md").read_text()))
    oi = set(re.findall(r"\bOI-\d+\b", (root / "docs" / "OPEN_ITEMS.md").read_text()))
    errors, rows = [], []
    with open(table, encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE):
            if r["cls"].split(" ")[0] not in reg.CLS or r["status"] not in reg.STATUS:
                errors.append(f"{r['q']}: class/status outside vocabulary")
            found = []
            for p in r["phrases"].split("|"):
                h = hits(text, p)
                if not h:
                    errors.append(f"{r['q']}: phrase prints nowhere: {p!r}")
                found += [x for x in h if x not in found]
            for p in filter(None, r["gone"].split("|")):
                if hits(text, p):
                    errors.append(f"{r['q']}: wording said to be gone still prints: {p!r} at {hits(text, p)}")
            bad = reg.missing_records(r["route"], root, tracked, ki, vl, oi)
            if bad:
                errors.append(f"{r['q']}: route cites records not in the repository: {bad}")
            if not found:
                continue
            home = next((x for x in found if x[0] == "paper_body"), found[0])
            rest = sorted(set(found) - {home}, key=lambda x: (FILES.index(x[0]), x[1]))
            loc, prev = f"{home[0]}.tex:{home[1]}", home[0]
            for x in rest:  # name the file again whenever it changes, so no bare line reads as the wrong file
                loc += f", {x[1]}" if x[0] == prev else f", {x[0]}.tex:{x[1]}"
                prev = x[0]
            rows.append({"id": r["q"].lower(), "q": r["q"], "doc": "paper", "loc": loc,
                         "section": secs.get(home[1], "") if home[0] == "paper_body" else "Front matter / abstract",
                         "quote": r["quote"], "cls": r["cls"], "status": r["status"], "route": r["route"],
                         "line": home[1], "order": home[1],
                         "prints": "yes" + (f"; no longer prints: {r['gone'].replace('|', '; ')}" if r["gone"] else "")})
    if errors:
        print("RELOCATE FAILED:\n  " + "\n  ".join(errors))
        sys.exit(1)
    Path(out).write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(rows)} paper rows re-located; status " +
          str({s: sum(r["status"] == s for r in rows) for s in sorted({r['status'] for r in rows})}))


def self_test():
    import contextlib, io, tempfile
    d = Path(tempfile.mkdtemp())
    (d / "main_paper.tex").write_text("\\input{paper_body}\n")
    (d / "paper_body.tex").write_text("\\section{Data}\\label{sec:d}\nThe cause is not known.\n% no correction to CH\n")
    ok = True
    for phr, gone, want in (("cause is not known", "no correction to CH", 0), ("cause is not known", "cause is", 1),
                            ("a sentence that left", "", 1)):
        (d / "t.tsv").write_text("q\tphrases\tgone\tcls\tstatus\tquote\troute\n"
                                 f"Q01\t{phr}\t{gone}\tK\tinherent\tx\tKNOWN_ISSUES 85\n")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                relocate(d, None, d / "o.json", d / "t.tsv")
            code = 0
        except SystemExit as e:
            code = e.code
        ok &= code == want
    print("SELF-TEST ::", "PASS" if ok else "FAIL", "(a printing phrase passes and a commented-out gone phrase does "
          "not count as printing; a gone phrase that prints fails; a phrase that prints nowhere fails)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    self_test() if "--self-test" in sys.argv else relocate(*sys.argv[1:4])
