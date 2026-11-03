"""remeasure.py -- re-measure the caveat density of the paper and the note with the 10-25 caveat study's own code.

usage: python3 -I remeasure.py --work DIR [--repo DIR] [--inv DIR] [--no-build] [--allow-stale] [--self-test]

One command, four steps:
  1. build main_paper and main_note from REPO/docs/analysis-note in a copy under WORK (latexmk -g; one more pass if
     the log reports unresolved references; still unresolved fails);
  2. pdftotext, then blind with the study's own tools/blindcount.py (paper) and tools/blind_note.py (note), and split
     the note at "Guide to the appendices" into the two parts the study coded separately;
  3. DENSITY: run the study's tools/tally.py, imported unchanged with its WORDS, SETS, H and T pointed at this run,
     over the inventories in INV (default: inv/ beside this file). Only ours-paper and ours-note are tallied; the
     nine comparators are quoted from the study's committed tables/rates.md, whose blinded texts are not committed;
  4. SURVIVAL (a separate, mechanical measure, NOT density): how many rows of the study's 10-25 inventories and of
     INV still verify against the current text. It sees removals only; a caveat added since coding is invisible to it.

The density in step 3 is valid only for the text the inventories were coded on. INV/CODED-ON.sha256 records the
blinded texts' hashes at coding time. If a current blinded text differs, the density for that document is printed as
STALE and the run exits 3 (exit 0 with --allow-stale). Re-code it under the study's CODEBOOK.md with the prompt in
CODER-PROMPT.md, put the TSV in INV, and record the new hash with --record-coded DOC (only that document's hash).
An INV may hold the paper's inventory alone; only the documents it holds are tallied and checked.

The study gives its coder-to-coder spread as about +-25% in row count (caveat-study/REPORT.md sec. 2.4): a change
smaller than that is not a measured change.
"""
import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent / "caveat-study"
TOOLS = STUDY / "tools"
PARTS = {"ours-paper": ["ours-paper"], "ours-note": ["ours-note-body", "ours-note-app"]}
BASELINE = {"ours-paper": {"words": 8785, "distinct_per_1k": 10.02, "rows_per_issue": 2.28, "all_per_1k": 22.88},
            "ours-note": {"words": 53018, "distinct_per_1k": 8.41, "rows_per_issue": 2.17, "all_per_1k": 18.24}}


def run(cmd, cwd, check=True):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, errors="replace")
    if check and p.returncode:
        sys.exit(f"FAILED ({p.returncode}): {' '.join(map(str, cmd))}\n{p.stdout[-2000:]}\n{p.stderr[-2000:]}")
    return p


def build(repo, work):
    src, dst = repo / "docs" / "analysis-note", work / "build"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("archive"))
    for t in ("main_note", "main_paper"):  # the paper's N- references resolve through main_note.aux (xr)
        for attempt in (1, 2):
            run(["latexmk"] + (["-g"] if attempt == 1 else []) + ["-pdf", "-interaction=nonstopmode", f"{t}.tex"],
                dst, check=False)
            log = (dst / f"{t}.log")
            if not log.exists():
                sys.exit(f"FAILED: no {t}.log, so the reference check read nothing")
            if "There were undefined references" not in log.read_text(errors="replace"):
                break
        else:
            sys.exit(f"FAILED: {t} still has undefined references after a second pass")
        if not (dst / f"{t}.pdf").exists():
            sys.exit(f"FAILED: {t}.pdf was not written")
    return dst / "main_paper.pdf", dst / "main_note.pdf"


def abstract_start(lines):
    """The paper's abstract is the first non-blank line after revtex's '(Dated' line."""
    d = next(i for i, l in enumerate(lines) if l.startswith("(Dated"))
    first = next(l for l in lines[d + 1:] if l.strip())
    return "^" + re.escape(first.strip()[:40])


TOKS = re.compile(r"[a-z]+")
STOP = re.compile(r"^\s*(\[\d+\]|\d+\.\s|[A-Z][A-Z ,\-]+$)|^\s*$|\f")


def limitation_items(paper_body: str) -> list[list[str]]:
    """The paper's Limitations list (sec:limitations, its enumerate): each item's first six alphabetic tokens."""
    code = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in paper_body.split("\n"))
    i = code.find("\\label{sec:limitations}")
    if i < 0:
        return []
    seg = code[i:]
    b, e = seg.find("\\begin{enumerate}"), seg.find("\\end{enumerate}")
    if b < 0 or e < b:
        return []
    out = []
    for it in seg[b:e].split("\\item")[1:]:
        # the anchor stops at the first macro that prints content (a value, a reference): its printed tokens are unknown
        cut = re.search(r"\\(fvval|ref|nsec|cite|SI|num|eqref)\b", it)
        t = it[:cut.start()] if cut else it
        out.append(TOKS.findall(re.sub(r"\\[A-Za-z]+", " ", t).lower())[:6])
    return out


def numbered_start(lines: list[str], n: int, anchor: list[str]) -> int | None:
    """The line where item n begins: it reads "n. " and its tokens, with the next two lines', start with the anchor.
    A bare token match is not enough: an item's opening words can recur elsewhere (the list's own introduction)."""
    a = " ".join(anchor)
    return next((i for i, l in enumerate(lines) if re.match(rf"^\s*{n}\.\s", l)
                 and " ".join(TOKS.findall(" ".join(lines[i:i + 3]).lower())).startswith(a)), None)


def restore_displaced_items(blind_lines: list[str], txt_lines: list[str], items: list[list[str]]):
    """pdftotext can place a Limitations item after ACKNOWLEDGMENTS or among the references in a two-column layout,
    where blindcount.py's rule drops it as acknowledgment or reference text. Each item that does not begin as a
    numbered line of the blinded text is restored from the raw text: its numbered line and the lines that follow, up to
    a blank line, a reference entry, an all-capitals heading or the next numbered item. Returns (lines, restored item
    numbers). An item still absent afterwards is an error: the measured text would be missing a body paragraph."""
    lines, restored = list(blind_lines), []
    for n, anchor in enumerate(items, 1):
        if not anchor or numbered_start(lines, n, anchor) is not None:
            continue
        start = numbered_start(txt_lines, n, anchor)
        if start is None:
            raise SystemExit(f"FAILED: Limitations item {n} is in neither the blinded nor the raw paper text")
        block = [txt_lines[start]]
        for l in txt_lines[start + 1:]:
            if STOP.search(l):
                break
            block.append(l)
        lines += [""] + block
        restored.append(n)
    missing = [n for n, a in enumerate(items, 1) if a and numbered_start(lines, n, a) is None]
    if missing:
        raise SystemExit(f"FAILED: Limitations items {missing} still absent after restoration")
    return lines, restored


def blind_words(lines: list[str]) -> int:
    """blindcount.py's own rule: tokens holding a letter or digit."""
    return sum(1 for w in " ".join(lines).split() if re.search(r"[A-Za-z0-9]", w))


def blind(work, paper_pdf, note_pdf, repo=None):
    for d in ("txt", "blind"):
        (work / d).mkdir(exist_ok=True)
    run(["pdftotext", str(paper_pdf), "txt/ours-paper.txt"], work)
    run(["pdftotext", str(note_pdf), "txt/ours-note.txt"], work)
    start = abstract_start((work / "txt/ours-paper.txt").read_text(errors="replace").split("\n"))
    out_p = run([sys.executable, "-I", str(TOOLS / "blindcount.py"), "ours-paper", start], work).stdout
    out_n = run([sys.executable, "-I", str(TOOLS / "blind_note.py"), "txt/ours-note.txt", "blind/ours-note.txt"],
                work).stdout
    words = {"ours-paper": int(re.search(r"words=(\d+)", out_p).group(1)),
             "ours-note": int(re.search(r"words=(\d+)", out_n).group(1))}
    restored = []
    if repo is not None:
        body = (Path(repo) / "docs" / "analysis-note" / "paper_body.tex").read_text(encoding="utf-8")
        bp = work / "blind/ours-paper.txt"
        lines, restored = restore_displaced_items(bp.read_text(errors="replace").split("\n"),
                                                  (work / "txt/ours-paper.txt").read_text(errors="replace").split("\n"),
                                                  limitation_items(body))
        if restored:
            bp.write_text("\n".join(lines))
            words["ours-paper"] = blind_words(lines)
            print(f"restored displaced Limitations items {restored}; paper words now {words['ours-paper']}")
    words["_restored_limitation_items"] = restored
    note = (work / "blind/ours-note.txt").read_text(errors="replace").split("\n")
    g = next(i for i, l in enumerate(note) if re.match(r"Guide to the appendices$", l))
    (work / "blind/ours-note-body.txt").write_text("\n".join(note[:g]))
    (work / "blind/ours-note-app.txt").write_text("\n".join(note[g:]))
    print(out_p.strip()); print(out_n.strip())
    return words


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_tally():
    spec = importlib.util.spec_from_file_location("caveat_tally", TOOLS / "tally.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def coded_on(inv):
    p = inv / "CODED-ON.sha256"
    if not p.exists():
        return {}
    return {l.split()[1]: l.split()[0] for l in p.read_text().splitlines() if l.strip()}


def stats(rows, words):
    iss = len({(r["kind"], r["issue"].lower()) for r in rows})
    w = words / 1000
    return {"rows": len(rows), "distinct": iss, "all_per_1k": round(len(rows) / w, 2),
            "distinct_per_1k": round(iss / w, 2), "rows_per_issue": round(len(rows) / iss, 2) if iss else 0}


def survival(tally, inv_dir, work, words):
    """Rows of the inventories in inv_dir (H/inv layout) that still verify against the current blinded texts."""
    tally.H, tally.T = inv_dir.parent, work
    out = {}
    for doc in PARTS:
        rows, bad = tally.load(doc)
        if rows is None:
            continue
        s = stats(rows, words[doc])
        s["dropped"] = len(bad)
        out[doc] = s
    return out


def comparators():
    out = []
    for l in (STUDY / "tables/rates.md").read_text().splitlines():
        c = [x.strip() for x in l.strip("|").split("|")]
        if len(c) > 13 and c[0] in ("P", "N"):
            out.append({"set": c[0], "doc": c[1], "distinct_per_1k": float(c[13]), "rows_per_issue": float(c[12])})
    return out


def main(a):
    work = Path(a.work).resolve(); work.mkdir(parents=True, exist_ok=True)
    repo = Path(a.repo).resolve()
    inv = Path(a.inv).resolve()
    if a.no_build:
        paper_pdf, note_pdf = work / "build/main_paper.pdf", work / "build/main_note.pdf"
    else:
        paper_pdf, note_pdf = build(repo, work)
    words = blind(work, paper_pdf, note_pdf, repo)
    restored = words.pop("_restored_limitation_items")
    head = run(["git", "-C", str(repo), "rev-parse", "HEAD"], repo, check=False).stdout.strip() or "unknown"
    now = {p: sha(work / "blind" / f"{p}.txt") for parts in PARTS.values() for p in parts}
    if a.record_coded:  # only the documents named: an uncoded document must never inherit a fresh hash
        coded = coded_on(inv)
        coded.update({p: now[p] for doc in a.record_coded for p in PARTS[doc]})
        (inv / "CODED-ON.sha256").write_text("".join(f"{coded[p]}  {p}\n" for p in sorted(coded)))
        print(f"recorded coded-on hashes for {a.record_coded} at {head}")
    coded = coded_on(inv)

    if inv.name != "inv":
        sys.exit("--inv must be a directory named inv/ (tally.py reads H/inv)")
    tally = load_tally()
    tally.H, tally.T = inv.parent, work
    tally.WORDS.update(words)
    tally.SETS = {d: [d] for d in PARTS if all((inv / f"{p}.tsv").exists() for p in PARTS[d])}
    stale = {doc: [p for p in PARTS[doc] if coded.get(p) != now[p]] for doc in tally.SETS}
    out = inv.parent / "tables"
    tally.main()  # writes inv.parent/tables/rates.md, placement.md, dropped-*.txt

    density = {}
    for doc in tally.SETS:
        rows, bad = tally.load(doc)
        density[doc] = dict(stats(rows, words[doc]), dropped=len(bad), stale=stale[doc], words=words[doc])
    surv = {"10-25 inventories (caveat-study/inv)": survival(load_tally(), STUDY / "inv", work, words)}
    summary = {"repo_head": head, "words": words, "restored_limitation_items": restored, "blinded_sha256": now, "density": density, "baseline_10_25": BASELINE,
               "survival_mechanical_not_density": surv, "comparators": comparators(),
               "coder_spread": "about +-25% in row count (caveat-study/REPORT.md sec. 2.4)"}
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")

    print(f"\n== caveat density at {head[:12]} (study code; coder spread about +-25%) ==")
    for doc, d in density.items():
        b = BASELINE[doc]
        flag = "  STALE: coded on a different text; this counts only coded caveats still present" if d["stale"] else ""
        print(f"{doc}: {d['words']:,} words; distinct /1k {d['distinct_per_1k']} (10-25: {b['distinct_per_1k']}); "
              f"rows per issue {d['rows_per_issue']} (10-25: {b['rows_per_issue']}); all /1k {d['all_per_1k']}; "
              f"dropped quotes {d['dropped']}{flag}")
    for k, v in surv.items():
        for doc, s in v.items():
            print(f"SURVIVAL (mechanical, not density) {k} {doc}: {s['rows']} rows still verify (after the study's "
                  f"merge rule), {s['dropped']} coded rows no longer verify")
    rng = {s: [c["distinct_per_1k"] for c in summary["comparators"] if c["set"] == s] for s in "PN"}
    print(f"comparators distinct /1k: P {min(rng['P'])}-{max(rng['P'])}, N {min(rng['N'])}-{max(rng['N'])}")
    print(f"wrote {out}/summary.json and the study-format tables beside it")
    if any(stale.values()) and not a.allow_stale:  # only the documents this INV holds inventories for
        print("EXIT 3: a density above is STALE; re-code that document (CODER-PROMPT.md), then --record-coded")
        sys.exit(3)


def self_test():
    ok = True
    lines = ["Title", "(Dated: November 2, 2026)", "", "We measure (the) cross section [x].", "I. INTRO"]
    rx = abstract_start(lines)
    ok &= bool(re.search(rx, lines[3])) and not re.search(rx, lines[4])
    t = load_tally()
    rc = subprocess.run([sys.executable, "-I", str(TOOLS / "tally.py"), "--self-test"], capture_output=True, text=True)
    ok &= rc.returncode == 0
    ok &= stats([{"kind": "c", "issue": "A"}, {"kind": "c", "issue": "a"}, {"kind": "d", "issue": "a"}], 1000) == \
        {"rows": 3, "distinct": 2, "all_per_1k": 3.0, "distinct_per_1k": 2.0, "rows_per_issue": 1.5}
    ok &= hasattr(t, "load") and hasattr(t, "main")
    body = ("\\subsection{Limitations}\\label{sec:limitations}\n\\begin{enumerate}\n\\item No reported interval has validated coverage.\n"
            "\\item Four of the sixteen cells, \\fvval{x}, have low stability.\n\\item The note's calibrated tests reject hybrid nulls.\n"
            "\\end{enumerate}\n")
    items = limitation_items(body)
    ok &= [i[:3] for i in items] == [["no", "reported", "interval"], ["four", "of", "the"], ["the", "note", "s"]]
    blind_ok = ["Limitations", "1. No reported interval has validated coverage.", "2. Four of the sixteen cells, R02, have",
                "low stability.", "3. The note's calibrated tests reject hybrid nulls."]
    ok &= restore_displaced_items(blind_ok, [], items) == (blind_ok, [])  # silent when every item is present
    raw = ["ACKNOWLEDGMENTS", "We thank.", "3. The note's calibrated tests reject", "hybrid nulls.", "",
           "[1] G. D'Agostini, A method", "2. Four of the sixteen cells, R02, have", "low stability.", "[2] A. Author"]
    lines, rest = restore_displaced_items(["Apart from the low stability of four of the sixteen cells (below), the",
                                           "principal ones are these."] + blind_ok[1:2], raw, items)
    ok &= rest == [2, 3] and "low stability." in lines and "hybrid nulls." in lines and "[2] A. Author" not in lines
    try:
        restore_displaced_items(blind_ok[:2], ["ACKNOWLEDGMENTS"], items)
        ok = False
    except SystemExit:
        pass
    print("SELF-TEST ::", "PASS" if ok else "FAIL", "(abstract start found and anchored; tally self-test; issue "
          "counting case-folds labels per kind; a displaced Limitations item is restored, a present one left alone, "
          "a lost one fails)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--work", help="scratch directory: build/, txt/, blind/")
    ap.add_argument("--repo", default=str(HERE.parents[6]), help="repository checkout (default: this file's)")
    ap.add_argument("--inv", default=str(HERE / "inv"), help="directory named inv/ holding ours-*.tsv")
    ap.add_argument("--no-build", action="store_true", help="reuse WORK/build/main_{paper,note}.pdf")
    ap.add_argument("--allow-stale", action="store_true", help="exit 0 even if an inventory is stale")
    ap.add_argument("--record-coded", nargs="+", choices=sorted(PARTS), metavar="DOC",
                    help="record the current blinded text of DOC (ours-paper, ours-note) as the text DOC was coded on")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
    if not a.work:
        ap.error("--work is required")
    main(a)
