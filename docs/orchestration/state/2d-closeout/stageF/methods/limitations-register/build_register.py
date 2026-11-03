"""build_register.py -- build the note's limitations register from the coded inventories and items.tsv.

usage: python3 -I build_register.py NOTEDIR AUX OUTDIR [--self-test]

Population: every row of kind (b) deviation, (c) untested/omitted or (d) scope in the caveat re-measure's note
inventories (../caveat-remeasure-20261102/inv/ours-note-{body,app}.tsv, coded on main 108040f8 under the caveat study's
CODEBOOK.md), plus every row of kind (a) history or (e) process whose label items.tsv maps (a coder's kind does not
decide whether a sentence states a limitation: the note's deposit status was coded (e)). Unmapped (a)/(e) labels are
listed, by label, in limitations-detail.json as excluded.

items.tsv maps every issue label of that population to exactly one register item and gives its class, status, route
and paper q-id. The build FAILS if:
  - a label of the population is mapped to no item, or to two, or items.tsv names a label the population lacks;
  - an item's home statement is not found in the TeX (under 80% of its tokens);
  - a route cites a record (DECISION-, OUTCOME-, RECORD-, ..., *REPORT.md, KNOWN_ISSUES n, VLnnn, OI-nn) that does
    not exist in the repository;
  - a class or status is outside the register's vocabulary.
An item's home is the first located statement, in note order, of its PRIMARY label (the first label items.tsv lists)
outside the abstract, executive summary and summary (main_note.tex, sec_execsummary.tex, sec_summary.tex); failing
that, of any of its labels outside them; failing that, its first located statement. The item's quote is the home's.
AUX is the built main_note.aux, read for section numbers.
Writes OUTDIR/limitations.json (the register's fields) and OUTDIR/limitations-detail.json (every statement's location).
"""
import collections
import csv
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
INV = HERE.parent / "caveat-remeasure-20261102" / "inv"
CLS = {"K", "M", "R"}
STATUS = {"closed", "fix decided", "in progress", "open", "inherent"}
SUMMARY_FILES = {"main_note", "sec_execsummary", "sec_summary"}
SEC = re.compile(r"\\(section|subsection|subsubsection)\*?\{(.+?)\}\s*(?:\\label\{([^}]+)\})?")
REC = re.compile(r"((?:DECISION|OUTCOME|RECORD|CORRECTION|FINDING|AUTHORIZATION|DELIVERY|AMENDMENT)-[0-9]{8}"
                 r"[A-Za-z0-9._-]*\.md|[A-Za-z0-9_.-]*REPORT[A-Za-z0-9_.-]*\.md|DECISION_RECORD-[A-Za-z0-9_.-]+\.md)")


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def repo_root():
    return Path(subprocess.run(["git", "-C", str(HERE), "rev-parse", "--show-toplevel"], capture_output=True,
                               text=True, check=True).stdout.strip())


def missing_records(route, root, tracked, ki, vl, oi):
    bad = []
    for r in REC.findall(route):
        name = r.split("/")[-1]
        hits = [p for p in tracked if p.endswith("/" + name) or p == name]
        if "/" in r:
            hits = [p for p in hits if p.endswith(r)]
        if not hits:
            bad.append(r)
    bad += [f"KNOWN_ISSUES {n}" for n in re.findall(r"KNOWN_ISSUES (\d+)", route) if n not in ki]
    bad += [v for v in re.findall(r"\bVL\d{2,3}\b", route) if v not in vl]
    bad += [o for o in re.findall(r"\bOI-\d+\b", route) if o not in oi]
    return bad


MACROS = {r"\\Eavail": "E_avail", r"\\pT": "pT", r"\\pPar": "p∥", r"\\S": "§"}
INPUT = re.compile(r"\\input\{([^}]+)\}")


def clean_title(t):
    for k, v in MACROS.items():
        t = re.sub(k + r"(?![A-Za-z])", v, t)
    return re.sub(r"\s+", " ", re.sub(r"\\[A-Za-z]+|[{}$_^]", lambda m: "_" if m.group() == "_" else "", t)).strip()


def sections(notedir, files, aux):
    """Section path in force at each (file, line), walking main_note.tex's \\input tree in reading order, so a file
    \\input inside a section inherits that section."""
    nums = dict(re.findall(r"\\newlabel\{([^}]+)\}\{\{([^}]*)\}", aux.read_text(errors="replace"))) if aux else {}
    out, cur = {}, []

    def walk(f):
        nonlocal cur
        path = Path(notedir) / f"{f}.tex"
        if f not in files or not path.exists():
            return
        lines = path.read_text(encoding="utf-8").split("\n")
        for i, line in enumerate(lines, 1):
            code = re.sub(r"(?<!\\)%.*", "", line)
            m = SEC.search(code)
            if m:
                lvl = ["section", "subsection", "subsubsection"].index(m.group(1))
                lab = m.group(3) or (re.search(r"\\label\{([^}]+)\}", lines[i]) or [None, ""])[1] if i < len(lines) else ""
                num = nums.get(lab or "", "")
                pre = (f"App. {num} " if num and num[0].isalpha() else f"§{num} " if num else "")
                cur = cur[:lvl] + [pre + clean_title(m.group(2))]
            out[(f, i)] = " > ".join(cur)
            for c in INPUT.findall(code):
                walk(c.removesuffix(".tex"))

    walk("main_note")
    return out


def section_at(secmap, f, line):
    return secmap.get((f, line), "")


def build(notedir, aux, outdir, items_tsv=HERE / "items.tsv", inv=INV):
    loc = _mod(HERE / "locate.py", "locate")
    stream, raw = loc.stream_of(notedir)
    idx = collections.defaultdict(list)
    toks = [s[0] for s in stream]
    for k in range(len(toks) - 3):
        idx[tuple(toks[k:k + 4])].append(k)
    files = loc.closure(notedir)
    order_of = {f: n for n, f in enumerate(files)}
    secmap = sections(notedir, files, Path(aux) if aux else None)

    items, label_to = [], {}
    errors = []
    with open(items_tsv, encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE):
            items.append(r)
            if r["cls"] not in CLS or r["status"] not in STATUS:
                errors.append(f"{r['key']}: class/status outside vocabulary: {r['cls']!r} {r['status']!r}")
            for lab in r["labels"].split("; "):
                lab = lab.strip()
                if lab in label_to:
                    errors.append(f"label mapped twice: {lab!r} ({label_to[lab]}, {r['key']})")
                label_to[lab] = r["key"]

    rows, excluded, every = [], collections.Counter(), set()
    for part in ("ours-note-body", "ours-note-app"):
        with open(Path(inv) / f"{part}.tsv", encoding="utf-8") as fh:
            for r in csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE):
                lab = r["issue"].strip().lower()
                every.add(lab)
                if r["kind"] not in "bcd" and lab not in label_to:
                    excluded[(r["kind"], lab)] += 1
                    continue
                r["part"] = part
                rows.append(r)
    pop = {r["issue"].strip().lower() for r in rows if r["kind"] in "bcd"}
    errors += [f"(b)/(c)/(d) label mapped to no item: {x!r}" for x in sorted(pop - set(label_to))]
    errors += [f"label in items.tsv, absent from the inventories: {x!r}" for x in sorted(set(label_to) - every)]

    root = repo_root()
    tracked = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True,
                             check=True).stdout.split("\n")
    ki = set(re.findall(r"^\| *(\d+) *\|", (root / "KNOWN_ISSUES.md").read_text(), re.M))
    vl = set(re.findall(r"\bVL\d{2,3}\b", (root / "VALIDATION_LEDGER.md").read_text()))
    oi = set(re.findall(r"\bOI-\d+\b", (root / "docs" / "OPEN_ITEMS.md").read_text()))

    by_item = collections.defaultdict(list)
    for r in rows:
        k = label_to.get(r["issue"].strip().lower())
        if k is None:
            continue
        f, line, cov = loc.locate(r["quote"], stream, idx)
        by_item[k].append({"part": r["part"], "n": int(r["n"]), "kind": r["kind"], "loc_kind": r["loc"],
                           "issue": r["issue"], "quote": r["quote"], "tex": f"{f}.tex:{line}" if f else None,
                           "file": f, "line": line, "coverage": cov})

    reg, detail = [], {}
    for it in items:
        st = by_item.get(it["key"], [])
        found = [s for s in st if s["file"] and s["coverage"] >= 0.8]
        found.sort(key=lambda s: (order_of[s["file"]], s["line"]))
        primary = it["labels"].split("; ")[0].strip()
        home = next((s for s in found if s["file"] not in SUMMARY_FILES and s["issue"].strip().lower() == primary),
                    next((s for s in found if s["file"] not in SUMMARY_FILES), found[0] if found else None))
        if home is None:
            errors.append(f"{it['key']}: no statement found in the TeX")
            continue
        bad = missing_records(it["route"], root, tracked, ki, vl, oi)
        if bad:
            errors.append(f"{it['key']}: route cites records not in the repository: {bad}")
        reg.append({"key": it["key"], "q": it["q"].replace(" ", ", "), "doc": "note", "loc": home["tex"],
                    "section": section_at(secmap, home["file"], home["line"]), "quote": home["quote"],
                    "cls": it["cls"], "status": it["status"], "route": it["route"], "line": home["line"],
                    "_order": (order_of[home["file"]], home["line"])})
        detail[it["key"]] = {"statements": len(st), "labels": sorted({s["issue"].lower() for s in st}),
                             "locations": sorted({s["tex"] for s in found},
                                                 key=lambda t: (order_of[t.split(".tex")[0]], int(t.split(":")[1]))),
                             "unlocated_or_partial": [{"quote": s["quote"], "best": s["tex"], "token_share": s["coverage"]}
                                                      for s in st if not (s["file"] and s["coverage"] >= 0.8)]}
    if errors:
        print("BUILD FAILED:\n  " + "\n  ".join(errors))
        sys.exit(1)
    reg.sort(key=lambda r: r["_order"])
    out = []
    for n, r in enumerate(reg, 1):
        rid = f"n{n:02d}"
        detail[rid] = dict(detail.pop(r["key"]), key=r["key"])
        out.append({"id": rid, "q": r["q"], "doc": "note", "loc": r["loc"], "section": r["section"],
                    "quote": r["quote"], "cls": r["cls"], "status": r["status"], "route": r["route"],
                    "line": r["line"], "order": 100 + n})
    outdir = Path(outdir)
    (outdir / "limitations.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    (outdir / "limitations-detail.json").write_text(json.dumps(
        {"population": {"rows": len(rows), "bcd_labels": len(pop),
                        "excluded_a_e_labels": [{"kind": k, "label": lab, "statements": n}
                                                for (k, lab), n in sorted(excluded.items())]},
         "items": detail}, indent=1, ensure_ascii=False) + "\n")
    c = collections.Counter(r["cls"] for r in out)
    s = collections.Counter(r["status"] for r in out)
    print(f"{len(out)} items from {len(rows)} statements ({len(pop)} (b)/(c)/(d) labels, plus mapped (a)/(e)); "
          f"excluded: {sum(excluded.values())} (a)/(e) rows under {len(excluded)} labels; class {dict(c)}; "
          f"status {dict(s)}; with a paper q-id: {sum(bool(r['q']) for r in out)}")


def self_test():
    import tempfile
    d = Path(tempfile.mkdtemp())
    (d / "main_note.tex").write_text("\\input{sec_a}\n")
    (d / "sec_a.tex").write_text("\\section{Results}\\label{sec:r}\nThe band is not validated for high W at all.\n"
                                 "We assume the flux shape is fixed by the prior here.\n")
    inv = d / "inv"; inv.mkdir()
    hdr = "n\tkind\tloc\tpolarity\tquant\tassigned\tissue\tquote\n"
    (inv / "ours-note-body.tsv").write_text(hdr + "1\tc\tinline\tneg\tno\tno\tband\tThe band is not validated for high W at all.\n"
                                            "2\ta\tinline\tpos\tno\tno\thist\tWe assume the flux shape is fixed by the prior here.\n")
    (inv / "ours-note-app.tsv").write_text(hdr)
    ok = True
    for route, want in (("KNOWN_ISSUES 85.", 0), ("DECISION-20990101-nobody-invented-record.md", 1)):
        (d / "items.tsv").write_text(f"key\tq\tcls\tstatus\troute\tlabels\nband\tq01\tR\topen\t{route}\tband\n")
        try:
            import contextlib, io
            with contextlib.redirect_stdout(io.StringIO()):
                build(d, None, d, d / "items.tsv", inv)
            code = 0
        except SystemExit as e:
            code = e.code
        ok &= code == want
    (d / "items.tsv").write_text("key\tq\tcls\tstatus\troute\tlabels\nband\tq01\tR\topen\t-\tother label\n")
    try:
        import contextlib, io
        with contextlib.redirect_stdout(io.StringIO()):
            build(d, None, d, d / "items.tsv", inv)
        ok = False
    except SystemExit as e:
        ok &= e.code == 1
    print("SELF-TEST ::", "PASS" if ok else "FAIL", "(an existing KNOWN_ISSUES row passes; an invented record fails "
          "the build; an unmapped population label fails the build; kind (a) is excluded)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    self_test() if "--self-test" in sys.argv else build(*sys.argv[1:4])
