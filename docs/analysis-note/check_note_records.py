#!/usr/bin/env python3
"""Inventory the analysis note's record appendices at a BASE tree and probe that a NEW tree lost none of them.

DECISION-20261021-joseph-da-and-note-records.md item 2: the analysis note posted as supplementary material is not a
records ledger. Its record appendices (provenance, superseded values and withdrawn results, and the record parts of
the release and codebase appendices) leave the posted build for the separately built, never-posted records document
main_records.tex. This script proves that the move lost nothing and left nothing behind.

usage:
  check_note_records.py inventory <base-note-dir> <out.json> [--sha SHA]   # freeze the base inventory
  check_note_records.py probe <base-note-dir | inventory.json> <new-note-dir> [--ledger LEDGER.md]
  check_note_records.py --self-test <base-note-dir | inventory.json> <new-note-dir> [--ledger LEDGER.md]

The base is docs/analysis-note at the commit before the move (or the inventory frozen from it); the new tree is the
same directory after it. The new tree carries main_records.tex, whose \\input closure is the records document, and
main_note.tex, whose closure is the posted note. Everything is derived from the sources; the only hand-entered facts
are the line ranges of the record parts of the release and codebase appendices (RECORD_RANGES), and the inventory
fails if a range no longer starts with its heading. The ledger defaults to <new-note-dir>/records-move-ledger.md.

Inventory (base):                                    Probes (new):
  I1 every \\label in the four appendix files          P1 each label defined exactly once over note+records,
                                                         and no record label left in the posted note
  I2 every App. G tag (table rows and see-below)       P2 every tag still in the records' app_provenance.tex
  I3 every \\dead{} body in app_history.tex (multiset)  P3 the same multiset in the records closure; zero \\dead
                                                         in the posted note's closure
  I4 every \\repopath in App. G                         P4 every one still in the records closure
  I5 every printed paragraph of G, J and the record    P5 each RECORD paragraph verbatim (normalized) in the
     ranges of H and I (comment-stripped, collapsed)     records closure and NOT in the posted note; each READER
                                                         paragraph in the note, unless the ledger lists its hash
  I6 every printed pointer into App. G (note closure)  P6 every App. G tag pointer survives: in the posted note
                                                         as a \\cite{NoteRecords2026} naming the same tag, or, if
                                                         its paragraph moved, as the same \\ref in the records;
                                                         a file with a whole-appendix pointer still cites it
                                                     P7 every ledger row carries a probe, and every probe holds:
                                                         N:<file>::<text> prints in the posted note's <file>,
                                                         X:<file>::<text> no longer prints there,
                                                         R:<file>::<text> prints in the records closure's <file>

--self-test first requires the probe to be SILENT on the given (base, new) pair -- the delivered move -- and then
plants one defect at a time in a copy of the new tree (a dropped strike, a dropped and an edited record paragraph, a
record paragraph left in the note, an edited reader paragraph, a renamed tag, a lost path, a G and a J label left in
the note, a struck value in the note, a lost tag pointer, a false ledger probe) and requires the named probe to fire
on each. Exit 0 only if every plant fires and the real pair is silent.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path

COMMENT = re.compile(r"(?<!\\)%[^\n]*")
APPS = ("app_provenance", "app_release", "app_codebase", "app_history")
# Line ranges (1-based, inclusive) of the RECORD parts of Apps. H and I at the base (4ba0dd2f): the identity table
# and the construction and audit record of the release appendix, and the test-suite discipline of the codebase
# appendix. The inventory refuses a base on which a range no longer starts with its heading.
RECORD_RANGES = {"app_release": [(122, 173, r"\subsection{Identities already fixed}"),
                                 (244, 287, r"\subsection{Construction and audit record")],
                 "app_codebase": [(55, 72, r"\paragraph{Test-suite discipline")]}
# A record range that moved keeps its pointers in this file of the records document.
MOVED_TO = {"app_release_records.tex": "app_release.tex", "app_codebase_records.tex": "app_codebase.tex"}
CITE = "NoteRecords2026"
LEDGER = "records-move-ledger.md"


def printed(text: str) -> str:
    return COMMENT.sub("", text)


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def closure(driver: Path) -> list[Path]:
    out, seen = [], set()

    def walk(p: Path) -> None:
        if p in seen or not p.exists():
            return
        seen.add(p)
        out.append(p)
        for name in re.findall(r"\\(?:input|include)\{([^}]+)\}", printed(p.read_text(errors="replace"))):
            walk(p.parent / (name if name.endswith(".tex") else name + ".tex"))
    walk(driver)
    return out


def paragraphs(text: str) -> list[str]:
    """Printed paragraphs: blank-line separated, comments removed, whitespace collapsed, >= 8 words."""
    paras = [norm(p) for p in re.split(r"\n\s*\n", printed(text))]
    return [p for p in paras if len(p.split()) >= 8]


def dead_bodies(text: str) -> list[str]:
    t, out = printed(text), []
    for m in re.finditer(r"\\dead\s*\{", t):
        i, depth = m.end() - 1, 0
        for j in range(i, len(t)):
            depth += {"{": 1, "}": -1}.get(t[j], 0)
            if depth == 0:
                out.append(norm(t[i + 1:j]))
                break
    return out


def g_tags(prov: str) -> list[str]:
    p = printed(prov)
    return sorted(set(re.findall(r"^\\texttt\{([a-z0-9-]+)\} &", p, re.M))
                  | set(re.findall(r"\\item\[\\texttt\{([a-z0-9-]+)\}", p)))


def pointers(files: list[Path], tags: set[str], target: str) -> Counter:
    """(file, tag) counts of printed pointers of form `target` over `files`; a pointer naming no tag is (whole)."""
    c: Counter = Counter()
    for f in files:
        t = printed(f.read_text(errors="replace"))
        for m in re.finditer(target, t):
            win = t[m.end():m.end() + 260]
            stop = min([x for x in (win.find(")"), win.find(". ")) if x >= 0] or [len(win)])
            named = [x for x in re.findall(r"\\texttt\{([a-z0-9-]+)\}", win[:stop]) if x in tags] or ["(whole)"]
            for x in named:
                c[(MOVED_TO.get(f.name, f.name), x)] += 1
    return c


def inventory(base: Path) -> dict:
    src = {a: (base / f"{a}.tex").read_text(errors="replace") for a in APPS}
    lines = {a: src[a].splitlines() for a in APPS}
    rec, rdr = [], []
    for a in APPS:
        if a in ("app_provenance", "app_history"):
            rec += paragraphs(src[a])
            continue
        taken: set[int] = set()
        for lo, hi, head in RECORD_RANGES.get(a, []):
            if not lines[a][lo - 1].startswith(head):
                raise SystemExit(f"FAIL {a}.tex:{lo} does not start with {head!r}; the record range moved")
            taken |= set(range(lo, hi + 1))
            rec += paragraphs("\n".join(lines[a][lo - 1:hi]))
        rdr += paragraphs("\n".join(l for n, l in enumerate(lines[a], 1) if n not in taken))
    tags = g_tags(src["app_provenance"])
    ptr = pointers(closure(base / "main_note.tex"), set(tags), r"\\ref\{app:provenance\}")
    rec_labels = re.findall(r"\\label\{([^}]+)\}", printed(src["app_provenance"] + src["app_history"]))
    for a, ranges in RECORD_RANGES.items():
        for lo, hi, _ in ranges:
            rec_labels += re.findall(r"\\label\{([^}]+)\}", printed("\n".join(lines[a][lo - 1:hi])))
    return {
        "labels": sorted(l for a in APPS for l in re.findall(r"\\label\{([^}]+)\}", printed(src[a]))),
        "record_labels": sorted(rec_labels),
        "tags": tags,
        "dead": sorted(dead_bodies(src["app_history"])),
        "repopaths": sorted(set(re.findall(r"\\repopath\{([^}]+)\}", printed(src["app_provenance"])))),
        "record_paragraphs": rec,
        "reader_paragraphs": rdr,
        "g_pointers": {f"{f}|{t}": n for (f, t), n in sorted(ptr.items())},
    }


def load_base(base: Path) -> dict:
    if base.is_file():
        inv = json.loads(base.read_text())
        return {k: v for k, v in inv.items() if not k.startswith("_")}
    return inventory(base)


def ledger_rows(ledger: Path) -> list[tuple[str, list[str]]]:
    """(row id, probes) for every table row whose first cell starts with `L`."""
    rows = []
    if not ledger.exists():
        return rows
    for line in ledger.read_text().splitlines():
        if not line.startswith("| L"):
            continue
        cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip()[1:-1])]
        probes = [p.strip().strip("`") for p in cells[-2].split(" && ")] if len(cells) >= 2 else []
        rows.append((cells[0], [p for p in probes if p]))
    return rows


def probe_fails(inv: dict, new: Path, ledger: Path) -> list[str]:
    fails: list[str] = []
    note = closure(new / "main_note.tex")
    recs = closure(new / "main_records.tex")
    if len(recs) <= 1:
        return ["P0 main_records.tex absent or inputs nothing; there is no records closure to probe"]
    ntext = {p.name: printed(p.read_text(errors="replace")) for p in note}
    rtext = {p.name: printed(p.read_text(errors="replace")) for p in recs}
    nall, rall = norm(" ".join(ntext.values())), norm(" ".join(rtext.values()))
    # P1 labels
    defs = Counter(l for d in (ntext, rtext) for t in d.values() for l in re.findall(r"\\label\{([^}]+)\}", t))
    for l in inv["labels"]:
        if defs[l] != 1:
            fails.append(f"P1 label {l} defined {defs[l]} times over note+records (want exactly 1)")
    for l in inv["record_labels"]:
        for n, t in ntext.items():
            if f"\\label{{{l}}}" in t:
                fails.append(f"P1 record label {l} is still defined in the posted note ({n})")
    # P2/P4 tags and paths
    prov = rtext.get("app_provenance.tex", "")
    fails += [f"P2 tag {t} missing from the records' app_provenance.tex" for t in inv["tags"]
              if not re.search(r"\\texttt\{" + re.escape(t) + r"\}", prov)]
    fails += [f"P4 repository path {p} missing from the records closure" for p in inv["repopaths"]
              if f"\\repopath{{{p}}}" not in rall]
    # P3 struck values
    got = Counter(b for t in rtext.values() for b in dead_bodies(t))
    want = Counter(inv["dead"])
    if got - want or want - got:
        fails.append(f"P3 \\dead multiset changed: lost {dict(want - got)}, added {dict(got - want)}")
    leaked = {n: dead_bodies(t) for n, t in ntext.items() if dead_bodies(t)}
    if leaked:
        fails.append(f"P3 the posted note's closure still strikes values: {leaked}")
    # P5 paragraphs
    for p in inv["record_paragraphs"]:
        if p not in rall:
            fails.append(f"P5 RECORD paragraph not verbatim in the records closure: {p[:90]!r}")
        if p in nall:
            fails.append(f"P5 RECORD paragraph still printed in the posted note: {p[:90]!r}")
    rewritten = ledger.read_text() if ledger.exists() else ""
    for p in inv["reader_paragraphs"]:
        h = hashlib.sha256(p.encode()).hexdigest()[:12]
        if p not in nall and h not in rewritten:
            fails.append(f"P5 READER paragraph {h} neither in the note nor in the ledger as REWRITE: {p[:90]!r}")
    # P6 pointers
    tags = set(inv["tags"])
    after = pointers(note, tags, r"\\cite\{" + CITE + r"\}") + pointers(recs, tags, r"\\ref\{app:provenance\}")
    whole_files = set()
    for key, n in inv["g_pointers"].items():
        f, t = key.split("|")
        if t == "(whole)":
            whole_files.add(f)
        elif after[(f, t)] < n:
            fails.append(f"P6 {f}: {n} pointer(s) to tag {t} before, {after[(f, t)]} after ({CITE} citation in "
                         f"the note, or the same reference in the records)")
    for f in sorted(whole_files):
        if f in ntext and f"\\cite{{{CITE}}}" not in ntext[f] and not any(k[0] == f for k in after):
            fails.append(f"P6 {f}: carried a whole-appendix pointer to App. G and cites {CITE} nowhere after")
    # P7 ledger probes
    for rid, probes in ledger_rows(ledger):
        if not probes:
            fails.append(f"P7 ledger row {rid} carries no probe")
        for pr in probes:
            m = re.match(r"([NXR]):([\w.]+)::(.+)$", pr, re.S)
            if not m:
                fails.append(f"P7 ledger row {rid}: malformed probe {pr[:80]!r}")
                continue
            kind, fname, text = m.groups()
            pool = rtext if kind == "R" else ntext
            body = norm(pool.get(fname, ""))
            if fname not in pool:
                fails.append(f"P7 ledger row {rid}: {fname} is not in the {'records' if kind == 'R' else 'note'} "
                             "closure")
            elif (kind == "X") == (norm(text) in body):
                fails.append(f"P7 ledger row {rid}: probe {kind}:{fname}::{text[:60]!r} does not hold")
    return fails


def report(inv: dict, fails: list[str]) -> str:
    return (f"RECORDS-MOVE :: {'PASS' if not fails else 'FAIL'} ({len(inv['labels'])} labels, {len(inv['tags'])} "
            f"tags, {len(inv['dead'])} struck bodies, {len(inv['repopaths'])} paths, {len(inv['record_paragraphs'])} "
            f"record and {len(inv['reader_paragraphs'])} reader paragraphs, {sum(inv['g_pointers'].values())} App. G "
            f"pointers; {len(fails)} failure(s))")


def probe(base: Path, new: Path, ledger: Path) -> int:
    inv = load_base(base)
    fails = probe_fails(inv, new, ledger)
    for f in fails:
        print("  FAIL " + f)
    print(report(inv, fails))
    return 1 if fails else 0


# ---------------------------------------------------------------------------------------------------------------
# Self-test: silent on the delivered move, and each planted defect fires its own probe.

def _drop_paragraph(path: Path, head: str) -> None:
    t = path.read_text()
    i = t.index(head)
    j = t.find("\n\n", i)
    path.write_text(t[:i] + t[j if j >= 0 else len(t):])


PLANTS = [
    # (name, probe that must fire, file, old, new)  -- old=None appends `new`; a callable edits the file
    ("dropped strike", "P3 \\dead multiset", "app_history.tex", r"$\dead{0.406}$", "$0.406$"),
    ("dropped record paragraph", "P5 RECORD paragraph not verbatim", "app_release_records.tex",
     lambda p: _drop_paragraph(p, r"\paragraph{Conditioning.}"), None),
    ("edited record paragraph", "P5 RECORD paragraph not verbatim", "app_codebase_records.tex",
     "as five rules rather than", "as six rules rather than"),
    ("record paragraph left in the note", "P5 RECORD paragraph still printed", "app_codebase.tex",
     lambda p: p.write_text(p.read_text() + "\n" + (p.parent / "app_codebase_records.tex").read_text()), None),
    ("edited reader paragraph", "P5 READER paragraph", "app_release.tex",
     "The pseudo-experiment products are archived", "The pseudo-experiment products are stored"),
    ("renamed tag (every occurrence)", "P2 tag joint-5d", "app_provenance.tex",
     lambda p: p.write_text(p.read_text().replace(r"\texttt{joint-5d}", r"\texttt{joint-5e}")), None),
    ("lost repository path", "P4 repository path", "app_provenance.tex", r"\repopath{", r"\texttt{"),
    ("G label left in the note", "P1 record label tab:prov-paths", "app_guide.tex", None,
     "\n\\label{tab:prov-paths}\n"),
    ("J label left in the note", "P1 record label app:history-errata", "app_guide.tex", None,
     "\n\\label{app:history-errata}\n"),
    ("struck value in the note", "P3 the posted note's closure still strikes", "sec_intro.tex", None,
     "\nWas $\\dead{9.876}$.\n"),
    ("lost tag pointer", "P6 sec_joint.tex", "sec_joint.tex", r"\cite{NoteRecords2026}", r"\cite{AnalysisNote2026}"),
    ("false ledger probe", "P7 ledger row", LEDGER, None,
     "\n| L99 | planted | - | `N:sec_intro.tex::this sentence is not printed anywhere` | planted |\n"),
]


def self_test(base: Path, new: Path, ledger: Path) -> int:
    inv = load_base(base)
    failures, fired = [], 0
    real = probe_fails(inv, new, ledger)
    if real:
        failures.append(f"the delivered move is not silent ({len(real)} failure(s)): {real[:3]}")
    with tempfile.TemporaryDirectory() as d:
        for name, want, fname, old, repl in PLANTS:
            work = Path(d) / re.sub(r"\W+", "-", name)
            shutil.copytree(new, work, ignore=shutil.ignore_patterns("*.pdf", "*.aux", "*.log", "*.bcf", "*.bbl",
                                                                     "*.fls", "*.fdb_latexmk", "*.out", "*.toc",
                                                                     "*.run.xml", "*.blg", "figures", "archive",
                                                                     "release-package-*", "__pycache__"))
            led = work / LEDGER if ledger == new / LEDGER else Path(d) / (work.name + ".ledger.md")
            if led != work / LEDGER:
                shutil.copyfile(ledger, led)
            target = led if fname == LEDGER else work / fname
            text = target.read_text()
            if callable(old):
                old(target)
            elif old is None:
                target.write_text(text + repl)
            elif old not in text:
                failures.append(f"{name}: UNAPPLIED, anchor {old!r} not found in {fname}")
                continue
            else:
                target.write_text(text.replace(old, repl, 1))
            got = probe_fails(inv, work, led)
            if not any(f.startswith(want) for f in got):
                failures.append(f"{name}: expected a failure starting {want!r}, got {got[:3]}")
            else:
                fired += 1
                print(f"  fired  {name:36} -> {next(f for f in got if f.startswith(want))[:100]}")
    for f in failures:
        print("  FAIL " + f)
    print(f"RECORDS-MOVE SELF-TEST :: {'PASS' if not failures else 'FAIL'} (delivered move silent: {not real}; "
          f"{fired} of {len(PLANTS)} planted defects fired their probe)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    args = list(argv)
    ledger = None
    if "--ledger" in args:
        i = args.index("--ledger")
        ledger = Path(args[i + 1])
        del args[i:i + 2]
    if len(args) >= 3 and args[0] == "inventory":
        inv = inventory(Path(args[1]))
        if "--sha" in args:
            inv = {"_base_sha": args[args.index("--sha") + 1],
                   "_derived_by": "docs/analysis-note/check_note_records.py inventory", **inv}
        Path(args[2]).write_text(json.dumps(inv, indent=1) + "\n")
        print({k: (len(v) if not isinstance(v, str) else v) for k, v in inv.items()})
        return 0
    if len(args) == 3 and args[0] in ("probe", "--self-test"):
        base, new = Path(args[1]), Path(args[2])
        ledger = ledger or new / LEDGER
        return (probe if args[0] == "probe" else self_test)(base, new, ledger)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
