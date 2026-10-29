#!/usr/bin/env python3
"""Build b<k>-ledger.md (``--build``) and run the r21 batch checks (a)-(d) against b<k>.tex.

usage: python3 -I -B check_batch.py b1|b2|b3|b4 [--build]

(a) every atom of every batch row occurs in printed(b<k>.tex);
(b) every `after` (read back from b<k>-ledger.md) occurs in printed(b<k>.tex) and contains its row's atoms;
(c) every numeral of printed(b<k>.tex) lies inside an occurrence of some batch atom, after removing the arguments of
    \\label, \\ref, \\ref*, \\cite, \\nsec, \\napp, \\fvval, \\begin and \\end; numerals left over are listed, split
    into symbol indices (a digit that is a sub/superscript of a symbol, such as q_{3}) and anything else;
(d) every GATE atom of the batch rows occurs exactly once; each of the eight bound GATE phrases is counted both
    literally and as a pattern with any \\SI value (expected: once each in b2, zero in b1, b3 and b4); the FROZEN sentence
    occurs as its own sentence the expected number of times (b1: 1, b2-b4: 0).
(s) headings and labels in outline order; b1 opens with F001.
Exit 1 on any failure.
"""
import re
import sys
from pathlib import Path

WT = Path("/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/"
          "796e7ecc-51d8-4fd5-a926-09de706955fd/scratchpad/wt-con")
sys.path.insert(0, str(WT / "docs/orchestration/state/2d-closeout/stageF/methods/note-n4"))
from check_ledger import printed, sentences  # noqa: E402

R21 = WT / "docs/orchestration/state/2d-closeout/stageF/methods/r21"
OUT = Path(__file__).resolve().parent
FROZEN = "Interval coverage has not been validated."
GATES = [r"with a median statistical uncertainty of \SI{0.676}{\percent}",
         r"biased by up to \SI{4}{\percent} in simulation", r"reduces it to below \SI{0.3}{\percent}",
         r"leaving up to \SI{1}{\percent} in some joint cells", r"differ by at most \SI{1.4}{\percent}",
         r"by up to \SI{74}{\percent} at high $W$", r"it is \SIrange{16}{31}{\percent} in the most affected",
         r"within the quoted total uncertainty in about half of those cells"]
BATCH = {
    "b1": dict(
        sections=["I", "II", "III", "III.A", "III.B"],
        headings=[r"\section{Introduction}", r"\section{Data, simulation, and observables}",
                  r"\section{Cross-section extraction}",
                  r"\subsection{Reporting definitions and the precision target}", r"\subsection{Reporting cells}"],
        labels=["sec:intro", "sec:data", "eq:eavail", "sec:method", "tab:estimators", "sec:uncertainty-status"],
        frozen=1, gates=0),
    "b2": dict(
        sections=["IV", "IV.A", "IV.B", "IV.C", "IV.D", "IV.E", "IV.F", "IV.G", "IV.H"],
        headings=[r"\section{Uncertainties and validation}", r"\subsection{The reported covariance}",
                  r"\subsection{Two-dimensional benchmark}", r"\subsection{Two-dimensional covariance}",
                  r"\subsection{Normalization and closure}", r"\subsection{Generator-sized truth changes}",
                  r"\subsection{Coverage}", r"\subsection{Estimator stability}",
                  r"\subsection{Fake-data tests of the sixteen-cell result}"],
        labels=["sec:validation", "sec:cov16", "sec:repro2d", "sec:repro2d-pub", "fig:validation", "sec:uq2d",
                "sec:closure", "fig:bkg-residual", "sec:departure", "fig:deformation", "sec:coverage",
                "sec:cov5d", "sec:fd16", "tab:fd16"],
        frozen=0, gates=1),
    "b3": dict(
        sections=["V", "V.A", "V.B", "V.C"],
        headings=[r"\section{The sixteen-cell cross section}", r"\subsection{Result}",
                  r"\subsection{Comparison on the sixteen reported cells}",
                  r"\subsection{Descriptive comparison of the central values}"],
        labels=["sec:result16", "tab:result16", "sec:gen16", "fig:ratio16", "tab:gen16", "sec:central"],
        frozen=0, gates=0),
    "b4": dict(
        sections=["VI", "VI.A"],
        headings=[r"\section{Discussion and conclusions}", r"\subsection{Limitations}"],
        labels=["sec:conclusions", "sec:limits", "sec:limitations"],
        frozen=0, gates=0),
}
LEAD = [r"\\label\{(?:sec|tab|fig):[^}]*\}", r"\\(?:sub)?section\{[^}]*\}", r"\\end\{(?:table|figure)\*?\}",
        r"\\begin\{(?:table|figure)\*?\}\[[a-z]*\]", r"\\centering", r"\\includegraphics\[[^]]*\]\{[^}]*\}", r"\\begin\{enumerate\}", r"\\item"]
TAIL = re.compile(r"\\end\{enumerate\}|\\item\b|\\begin\{tabular\}|\\end\{(?:table|figure)\*?\}|\\(?:sub)?section\{|\\begin\{(?:table|figure)")


def ledger_rows(sections):
    """(line, id, section, atoms, status) for the batch rows of fact-ledger.md, in file order."""
    out = []
    for line in (R21 / "fact-ledger.md").read_text().splitlines():
        if not re.match(r"\| F\d{3} \|", line):
            continue
        c = [x.strip() for x in line.strip().strip("|").split(" | ")]
        if len(c) != 7:
            raise SystemExit(f"cannot parse ledger row: {line[:80]}")
        if c[1] in sections or (c[0] == "F001" and "I" in sections):
            out.append((line, c[0], c[1], [a.strip()[1:-1] for a in c[3].split(" && ")], c[5]))
    return out


def trim(s, atoms):
    first = min(s.index(a) for a in atoms)
    last = max(s.index(a) + len(a) for a in atoms)
    cut = 0
    for rx in LEAD:
        for m in re.finditer(rx, s):
            if m.end() <= first:
                cut = max(cut, m.end())
    m = TAIL.search(s, last)
    return s[cut:m.start() if m else len(s)].strip()


def after_for(atoms, sents, text, lo, hi):
    """The sentence of the row's (sub)section holding all atoms, trimmed of headings, labels and float matter. If no
    single sentence holds them, two consecutive sentences (reported as such)."""
    pos = lambda s: text.find(s) + min(s.index(a) for a in atoms)
    hits = [s for s in sents if all(a in s for a in atoms) and lo <= pos(s) < hi]
    if len(hits) == 1:
        return trim(hits[0], atoms), 1
    if not hits:
        pairs = [sents[i] + " " + sents[i + 1] for i in range(len(sents) - 1)]
        hits = [s for s in pairs if all(a in s for a in atoms) and s in text and lo <= pos(s) < hi]
        if len(hits) == 1:
            return trim(hits[0], atoms), 2
    return None, len(hits)


def build(cfg, rows, text, ledger_out, name):
    sents = sentences(text)
    heads = [text.find(h) for h in cfg["headings"]]
    lines = [
        f"# {name} ledger: the rows of {', '.join(cfg['sections'])}" + (" and F001" if name == "b1" else "")
        + ", with `after`",
        "",
        "Rows are copied unchanged from `r21/fact-ledger.md`; the last column, `after`, is added. `after` is the",
        f"sentence of `{name}.tex` that states the row's fact, in printed form (`%` comments removed, whitespace",
        "collapsed), as split by `sentences` of note-n4/check_ledger.py, with any leading heading, `\\label` or float",
        "matter that the mechanical split attaches to it cut off. STRUCTURE rows carry `—`. A literal `|` inside",
        "`after` is written `\\|` (the GFM table escape); unescape it before matching. Spans that contain a double",
        "backtick are fenced with three backticks.",
        "",
        "| id | section | fact | atoms | base | status | base text | after |",
        "|---|---|---|---|---|---|---|---|",
    ]
    bad, two = [], []
    for line, rid, sec, atoms, status in rows:
        if status == "STRUCTURE":
            cell = "—"
        else:
            k = cfg["sections"].index(sec)
            lo = heads[k] if rid != "F001" else 0
            hi = min([h for h in heads[k + 1:] if h >= 0] or [len(text)])
            a, n = after_for(atoms, sents, text, lo, hi)
            if a is None:
                bad.append(f"{rid}: {n} sentences hold all atoms"); cell = "MISSING"
            else:
                if n == 2:
                    two.append(rid)
                cell = (f"``` {a} ```" if "``" in a else f"`{a}`").replace("|", r"\|")
        lines.append(line.rstrip() + f" {cell} |")
    ledger_out.write_text("\n".join(lines) + "\n")
    return bad, two


def read_afters(ledger_out):
    out = {}
    for line in ledger_out.read_text().splitlines():
        m = re.match(r"\| (F\d{3}) \|", line)
        if not m:
            continue
        cell = re.split(r"(?<!\\)\|", line.strip().strip("|"))[-1].strip().replace(r"\|", "|")
        if cell != "—":
            out[m.group(1)] = cell[4:-4] if cell.startswith("``` ") else cell[1:-1]
    return out


def main():
    name = sys.argv[1]
    cfg = BATCH[name]
    tex, ledger_out = OUT / f"{name}.tex", OUT / f"{name}-ledger.md"
    rows = ledger_rows(cfg["sections"])
    text = printed(tex.read_text())
    fails = []
    if "--build" in sys.argv:
        bad, two = build(cfg, rows, text, ledger_out, name)
        fails += [f"(build) {b}" for b in bad]
        print("after spans two sentences:", two or "none")
    print(f"{name} rows: {len(rows)} ({sum(r[4] != 'STRUCTURE' for r in rows)} non-STRUCTURE)")

    n_atoms = 0
    for _l, rid, _s, atoms, _st in rows:
        for a in atoms:
            n_atoms += 1
            if a not in text:
                fails.append(f"(a) {rid}: atom not printed: {a[:90]!r}")
    print(f"(a) atoms checked: {n_atoms}, missing: {sum(f.startswith('(a)') for f in fails)}")

    afters, nb = read_afters(ledger_out), 0
    for _l, rid, _s, atoms, st in rows:
        if st == "STRUCTURE":
            continue
        nb += 1
        a = afters.get(rid)
        if a is None:
            fails.append(f"(b) {rid}: no after"); continue
        if a not in text:
            fails.append(f"(b) {rid}: after not in printed({name}.tex): {a[:90]!r}")
        for at in atoms:
            if at not in a:
                fails.append(f"(b) {rid}: after lacks atom {at[:60]!r}")
    print(f"(b) afters checked: {nb}, failures: {sum(f.startswith('(b)') for f in fails)}")

    t = text
    for at in sorted({a for r in rows for a in r[3]}, key=len, reverse=True):
        t = t.replace(at, " \x00 ")
    t = re.sub(r"\\(?:label|ref\*?|cite|nsec|napp|fvval|begin|end)\{[^}]*\}", " ", t)
    idx, other = [], []
    for m in re.finditer(r"\d+(?:\.\d+)?", t):
        ctx = t[max(0, m.start() - 12):m.end() + 6]
        (idx if re.search(r"[_^]\{?[^}\s]*$", t[max(0, m.start() - 12):m.start()]) else other).append(ctx)
    print(f"(c) numerals outside every atom: {len(other)} non-index; {len(idx)} symbol indices")
    for ctx in other:
        fails.append(f"(c) numeral outside atoms: {ctx!r}")
    print("    symbol indices:", sorted({re.sub(r'\s+', ' ', c.strip()) for c in idx}))

    gate_rows = [r for r in rows if r[4] == "GATE"]
    ctx_counts = []
    for _l, rid, _s, atoms, _st in gate_rows:
        for a in atoms:
            n = text.count(a)
            if any(g in a for g in GATES):          # the bound phrase itself: exactly once
                if n != 1:
                    fails.append(f"(d) {rid}: bound GATE atom prints {n}x: {a!r}")
            else:                                    # a context atom of a GATE row: must print, count reported
                ctx_counts.append(f"{rid} {a!r}: {n}x")
                if n == 0:
                    fails.append(f"(d) {rid}: GATE context atom missing: {a!r}")
    print(f"(d) GATE rows in the batch: {len(gate_rows)} ({', '.join(r[1] for r in gate_rows) or '-'}); "
          f"bound atoms each print exactly once: {not any(f.startswith('(d)') for f in fails)}")
    if ctx_counts:
        print("    context atoms of GATE rows (not bound phrases):", "; ".join(ctx_counts))
    lit = [text.count(g) for g in GATES]
    pat = [len(re.findall(re.sub(r"\\\\SI(range)?\\\{[^}]*\\\}(\\\{[^}]*\\\})?",
                                 lambda m: r"\\SI" + (m.group(1) or "") + r"\{[^}]*\}" + (r"\{[^}]*\}" if m.group(2) else ""),
                                 re.escape(g)), text)) for g in GATES]
    print(f"    bound GATE phrases, literal counts {lit}; any-value pattern counts {pat}; expected {cfg['gates']} each")
    if any(c != cfg["gates"] for c in lit + pat):
        fails.append(f"(d) GATE phrase counts differ from {cfg['gates']}: {lit} {pat}")
    own = sentences(text).count(FROZEN)
    print(f"    FROZEN: printed {text.count(FROZEN)}x, as its own sentence {own}x; expected {cfg['frozen']}")
    if text.count(FROZEN) != cfg["frozen"] or own != cfg["frozen"]:
        fails.append("(d) FROZEN count wrong")

    pos = [text.find(h) for h in cfg["headings"]]
    lpos = [text.find(r"\label{" + l + "}") for l in cfg["labels"]]
    if -1 in pos or pos != sorted(pos):
        fails.append(f"(s) headings missing or out of order: {pos}")
    if -1 in lpos or lpos != sorted(lpos):
        fails.append(f"(s) labels missing or out of order: {lpos}")
    msg = f"(s) headings in order: {-1 not in pos and pos == sorted(pos)}; labels in order: {-1 not in lpos and lpos == sorted(lpos)}"
    if name == "b1":
        f001 = next(r for r in rows if r[1] == "F001")[3]
        ok = text.startswith(" ".join(f001))
        msg += f"; F001 opens the file: {ok}"
        if not ok:
            fails.append("(s) b1.tex does not open with F001")
    print(msg)

    for f in fails:
        print("  FAIL", f)
    print("RESULT:", "PASS" if not fails else f"FAIL ({len(fails)})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
