"""reprice.py -- re-price R-P9 (secondary results moved whole to the note) from the measured 77 at 97e30dda.

usage: python3 -I reprice.py --src DIR --inv DIR --work DIR [--only K[,K...]] [--combo K+K+...]... [--self-test]

  --src   a directory holding docs/analysis-note at 97e30dda, with main_note already built (its aux is reused)
  --inv   the paper's inventory directory coded at 97e30dda (after-711-97e30dda/inv: ours-paper.tsv, CODED-ON.sha256)
  --work  scratch; one sub-directory per candidate or combination

Each candidate is a set of edits to paper_body.tex (and, for the abstract variant, main_paper.tex): the moved text is
deleted, every sentence elsewhere that cites it is cut or re-pointed, and one pointer sentence is added. The edited copy
is built and blinded by remeasure.py, exactly as the paper was measured, and tallied with --allow-stale against the
inventory coded at 97e30dda:
  - a statement leaves the paper when its quote no longer verifies against the edited blinded text;
  - a distinct caveat (kind, issue label) leaves only when every one of its statements has left. That is the study's
    unit: a caveat restated elsewhere stays, however much of it moves;
  - words are the edited text's own blinded count.
Two corrections for page layout, which a move changes and the study's tools read:
  - a quote the study's verifier drops is checked against the SOURCE (paper_body.tex and the abstract, references
    and values removed): if its tokens are still there as before, a float or a renumbered section letter broke the
    printed quote, and the statement stays ("statements_layout_artifact");
  - blindcount.py cuts the back matter from the ACKNOWLEDGMENTS heading, so acknowledgments text that layout places
    before its own heading is counted as body text. Lines of the base paper's back matter (less any line the base's
    blinded text keeps) are removed and the words recounted by blindcount's rule ("leaked_back_matter_lines").
What this cannot see is a caveat the edits ADD (the pointer sentences and the re-pointed clauses). Those sentences
are listed by --pointers, to be coded blind under the study's codebook; their count is added separately
(adjudication.json).

Each edit's anchor must occur exactly once, or the run stops. An edit marked optional is skipped only when its anchor
lies in text another candidate in the same run has deleted.
"""
import argparse
import csv
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REMEASURE = HERE.parent / "remeasure.py"
PB, MP = "paper_body.tex", "main_paper.tex"

# key: what moves, then the edits. ("range", start-line prefix, end-line prefix, replacement) deletes the lines from
# the one starting with the first prefix up to, not including, the one starting with the second, and puts the
# replacement there. ("sub", old, new[, "optional"]) replaces one exact occurrence.
CANDIDATES = {
    "IIIA": {
        "moves": "III A: the reporting definitions of a five-observable measurement, the 10% precision target and the "
                 "model-dependence envelope",
        "edits": [
            ("range", PB, r"\subsection{Reporting definitions and the precision target}", r"\subsection{Reporting cells}", ""),
            ("sub", PB, "is reported separately from those reporting definitions: the joint-test estimator's data result on 16 cells, R00--R15.",
             "is reported as the joint-test estimator's data result on 16 cells, R00--R15. Other reporting definitions of a "
             "five-observable measurement, with their precision, are studied in \\nsec{sec:gbdt-model-dependence}."),
            ("sub", PB, " The envelope of Sec.~\\ref{sec:uncertainty-status} instead reweights the prior used to unfold the data.", ""),
            ("sub", PB, "Unlike the envelope of Sec.~\\ref{sec:uncertainty-status}, its model term is a covariance built from three generator shifts.",
             "Its model term is a covariance built from three generator shifts."),
            ("sub", PB, "The second is the envelope of Sec.~\\ref{sec:uncertainty-status}, which tracks the same bias.",
             "The second is the envelope of the note's precision-target study, which tracks the same bias "
             "(\\nsec{sec:gbdt-model-dependence})."),
        ],
    },
    "IVBC": {
        "moves": "IV B and IV C: the two-dimensional benchmark against the published result (with Fig. 1) and the "
                 "two-dimensional covariance; the limitation sentence on that covariance; the abstract is unchanged",
        "edits": [
            ("range", PB, r"\subsection{Two-dimensional benchmark}", r"\subsection{Normalization and closure}",
             "The reproduction of the published two-dimensional measurement~\\cite{MINERvA:2021owq}, an end-to-end test "
             "of the unfolding, and its covariance are given in Ref.~\\cite{AnalysisNote2026}, "
             "Secs.~\\ref*{N-sec:results-compare} and~\\ref*{N-sec:results-uq}.\n\n"),
            ("sub", PB, "We first reproduce the published double-differential cross section $d^{2}\\sigma/(d\\pT\\,d\\pPar)$~\\cite{MINERvA:2021owq} as an end-to-end test of the unfolding,",
             "The reproduction of the published double-differential cross section $d^{2}\\sigma/(d\\pT\\,d\\pPar)$~\\cite{MINERvA:2021owq}, "
             "an end-to-end test of the unfolding, is given in the companion note,"),
            ("sub", PB, "gives the two-dimensional central value and its covariance (Sec.~\\ref{sec:repro2d}).",
             "gives the two-dimensional central value and its covariance (\\nsec{sec:results-uq})."),
            ("sub", PB, "through the two-dimensional reproduction, ", "through "),
            ("sub", PB, "from the reproduction of the published two-dimensional measurement to the fake-data tests of the sixteen-cell result",
             "including the fake-data tests of the sixteen-cell result"),
            ("sub", PB, "The two-dimensional result is therefore reusable, and the sixteen-cell result can be used for the comparison that follows.",
             "The sixteen-cell result can therefore be used for the comparison that follows."),
            ("sub", PB, " The two-dimensional covariance has not been independently validated and gives no calibrated significance for generator comparisons; an earlier statistical band of that result undercovered in its tails in a coverage test at fixed truth (\\nsec{sec:coverage}), and the coverage of the current statistical block and of the total covariance has not been tested.", ""),
            ("sub", PB, "nor the size of either run-period block", "nor the size of the run-period block"),
        ],
    },
    "IVC": {
        "moves": "IV C alone: the two-dimensional covariance (IV B and Fig. 1 stay)",
        "edits": [
            ("range", PB, r"\subsection{Two-dimensional covariance}", r"\subsection{Normalization and closure}",
             "The covariance of the two-dimensional result, its comparison with the published uncertainty and its model "
             "term are given in Ref.~\\cite{AnalysisNote2026}, Secs.~\\ref*{N-sec:results-uq} and~\\ref*{N-sec:uq-combine}.\n\n"),
            ("sub", PB, "The band of this analysis is the four-block covariance of Sec.~\\ref{sec:uq2d}, without $C_{\\mathrm{model}}$.",
             "The band of this analysis is the four-block covariance of \\nsec{sec:results-uq}, without $C_{\\mathrm{model}}$."),
        ],
    },
    "IVDbkg": {
        "moves": "IV D's closure with backgrounds (purity-based and negative-weight subtraction) and Fig. 2; the "
                 "normalization paragraph stays",
        "edits": [
            ("range", PB, "With purity-based background subtraction in a deterministic LightGBM estimator", r"\subsection{Generator-sized truth changes}",
             "The closure of these estimators with backgrounds included, under purity-based and unbinned negative-weight "
             "subtraction, is given in \\nsec{sec:closure-map} and \\napp{sec:negweight-footing}.\n\n"),
            ("sub", PB, " At nominal truth this variant's largest residual is \\SI{0.39}{\\percent} (the squares of Fig.~\\ref{fig:bkg-residual}a).",
             " At nominal truth this variant's largest residual is \\SI{0.39}{\\percent} (\\nsec{sec:closure-map}).", "optional"),
            ("sub", PB, "background-subtraction tests, ", ""),
        ],
    },
    "IVE": {
        "moves": "IV E: the generator-sized truth changes (with Fig. 3) and the coverage of an earlier estimator",
        "edits": [
            ("range", PB, r"\subsection{Generator-sized truth changes}", r"\subsection{Sensitivity to input rounding}",
             "The recovery of generator-sized changes of the truth, and the interval coverage of an earlier estimator, "
             "are given in Ref.~\\cite{AnalysisNote2026}, Secs.~\\ref*{N-sec:val-departure} and~\\ref*{N-sec:coverage-5d}.\n\n"),
            ("sub", PB, "The first is the residual under a generator-sized change of the truth in Sec.~\\ref{sec:departure}, which we interpret as regularization bias.",
             "The first is the residual under a generator-sized change of the truth, which we interpret as regularization "
             "bias (\\nsec{sec:val-departure})."),
            ("sub", PB, "recovery of generator-sized truth changes, ", ""),
            ("sub", PB, "the held-out shape tests of Fig.~\\ref{fig:deformation}b and the precision study.",
             "the held-out shape tests of \\nsec{sec:val-departure} and the precision study."),
        ],
    },
    "IVF": {
        "moves": "IV F: the sensitivity to input rounding",
        "edits": [
            ("range", PB, r"\subsection{Sensitivity to input rounding}", r"\subsection{Fake-data tests of the sixteen-cell result}",
             "The estimator's response to rounding-level changes of its inputs is given in \\nsec{sec:val-departure}.\n\n"),
        ],
    },
    "VC": {
        "moves": "V C: the descriptive comparisons of the three- and four-observable central values, and the pointer to "
                 "the earlier purity-subtracted five-observable map",
        "edits": [
            ("range", PB, r"\subsection{Descriptive comparison of the central values}", r"\section{Discussion and conclusions}", ""),
            ("sub", PB, ", and we also give three- and four-observable central values.",
             ". The three- and four-observable central values are given in the companion note~\\cite{AnalysisNote2026}."),
        ],
    },
    "ABS2D": {
        "moves": "the abstract's sentence on the two-dimensional reproduction (with IVBC only)",
        "requires": ["IVBC"],
        "edits": [
            ("sub", MP, " The unfolding reproduces the published muon-kinematic cross-section integral within about 1\\%, with a correlated shape difference.", ""),
        ],
    },
}
EXCLUSIVE = [{"IVBC", "IVC"}]


def apply_edits(src_dir: Path, keys: list[str]) -> dict[str, str]:
    """Return {file: edited text} for the candidates in keys; stop on an anchor that is missing or repeated."""
    for k in keys:
        miss = [r for r in CANDIDATES[k].get("requires", []) if r not in keys]
        if miss:
            sys.exit(f"{k} requires {miss}")
    for ex in EXCLUSIVE:
        if len(ex & set(keys)) > 1:
            sys.exit(f"{sorted(ex)} are alternatives, not a combination")
    text = {f: (src_dir / f).read_text(encoding="utf-8") for f in (PB, MP)}
    edits = [(k, e) for k in keys for e in CANDIDATES[k]["edits"]]
    for k, e in [x for x in edits if x[1][0] == "range"]:
        _, f, start, end, repl = e
        lines = text[f].split("\n")
        s = [i for i, l in enumerate(lines) if l.startswith(start)]
        t = [i for i, l in enumerate(lines) if l.startswith(end)]
        if len(s) != 1 or len(t) != 1 or t[0] <= s[0]:
            sys.exit(f"{k}: range anchors {start!r} .. {end!r} found {len(s)} and {len(t)} times")
        text[f] = "\n".join(lines[:s[0]] + ([repl] if repl else []) + lines[t[0]:])
    for k, e in [x for x in edits if x[1][0] == "sub"]:
        f, old, new = e[1], e[2], e[3]
        n = text[f].count(old)
        if n == 0 and len(e) > 4 and e[4] == "optional":
            continue
        if n != 1:
            sys.exit(f"{k}: anchor found {n} times: {old[:80]!r}")
        text[f] = text[f].replace(old, new)
    return text


def pointer_sentences(keys: list[str]) -> list[str]:
    """The text each candidate adds: the replacement of every edit, which the inventory cannot have coded."""
    out = []
    for k in keys:
        for e in CANDIDATES[k]["edits"]:
            new = e[4] if e[0] == "range" else e[3]
            if new.strip():
                out.append(new.strip())
    return out


def measure(src: Path, inv: Path, work: Path, keys: list[str], remeasure: Path = REMEASURE) -> dict:
    name = "+".join(keys) or "base"
    d = work / name
    if d.exists():
        shutil.rmtree(d)
    repo = d / "repo"
    shutil.copytree(src / "docs" / "analysis-note", repo / "docs" / "analysis-note",
                    ignore=shutil.ignore_patterns("archive"))
    for f, t in apply_edits(src / "docs" / "analysis-note", keys).items():
        (repo / "docs" / "analysis-note" / f).write_text(t, encoding="utf-8")
    shutil.copytree(inv, d / "run" / "inv")
    p = subprocess.run([sys.executable, "-I", str(remeasure), "--work", str(d / "w"), "--repo", str(repo),
                        "--inv", str(d / "run" / "inv"), "--allow-stale"], capture_output=True, text=True)
    if p.returncode:
        sys.exit(f"{name}: remeasure failed\n{p.stdout[-3000:]}\n{p.stderr[-3000:]}")
    s = json.loads((d / "run" / "tables" / "summary.json").read_text())["density"]["ours-paper"]
    tally = load_tally(remeasure)
    tally.H, tally.T = d / "run", d / "w"
    kept, bad = tally.load("ours-paper")
    rows = {r["n"]: r for r in csv.DictReader(open(inv / "ours-paper.tsv"), delimiter="\t", quoting=csv.QUOTE_NONE)}
    base_src = source_tokens(src / "docs" / "analysis-note")
    new_src = source_tokens(repo / "docs" / "analysis-note")
    layout, gone = [], []
    for part, n, why, _ in bad:
        q = tokens(rows[n]["quote"])
        (layout if run_len(q, new_src) >= run_len(q, base_src) else gone).append(n)
    keep = kept + [dict(rows[n]) for n in layout]
    left = {(r["kind"].strip(), r["issue"].strip().lower()) for r in keep}
    allc = {(r["kind"].strip(), r["issue"].strip().lower()) for r in rows.values()}
    if len({(r["kind"].strip(), r["issue"].strip().lower()) for r in kept}) != s["distinct"]:
        sys.exit(f"{name}: my count of the tally's rows disagrees with the tally")
    words, leaked = unleaked_words(src_txt_lines(work), d / "w", remeasure)
    return {"keys": keys, "words": words, "words_as_blinded": s["words"], "leaked_back_matter_lines": leaked,
            "distinct": len(left), "distinct_per_1k": round(len(left) / words * 1000, 2),
            "tally_as_printed": {"distinct": s["distinct"], "distinct_per_1k": s["distinct_per_1k"]},
            "statements_gone": sorted(gone, key=int), "statements_layout_artifact": sorted(layout, key=int),
            "caveats_gone": sorted(f"({a}) {b}" for a, b in allc - left)}


BACK_MATTER = re.compile(r"^(ACKNOWLEDG|Acknowledg)")
REFS = re.compile(r"^(\[1\]( |$)|References$|REFERENCES$)")


def src_txt_lines(work: Path) -> set[str]:
    """The acknowledgments and data-availability lines of the BASE paper's raw text, less every line the base's
    blinded text keeps (Limitations items that layout displaced there, which remeasure.py restores). TeX breaks a
    paragraph's lines independently of the page, so these lines recur verbatim in every edit."""
    txt = (work / "base" / "w" / "txt" / "ours-paper.txt").read_text(errors="replace").split("\n")
    kept = {l.strip() for l in (work / "base" / "w" / "blind" / "ours-paper.txt").read_text(errors="replace").split("\n")}
    a = next(i for i, l in enumerate(txt) if BACK_MATTER.match(l.lstrip("\f")))
    b = next(i for i, l in enumerate(txt) if i > a and REFS.match(l.lstrip("\f")))
    return {l.strip() for l in txt[a:b] if len(l.strip()) > 25} - kept


def unleaked_words(back: set[str], w: Path, remeasure: Path) -> tuple[int, int]:
    """Blinded words without back matter that page layout placed before its own heading, where the study's
    blindcount.py (which cuts from the heading) cannot remove it."""
    spec = importlib.util.spec_from_file_location("remeasure", remeasure)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    lines = (w / "blind" / "ours-paper.txt").read_text(errors="replace").split("\n")
    keep = [l for l in lines if l.strip() not in back]
    (w / "leaked-back-matter.txt").write_text("\n".join(l for l in lines if l.strip() in back) + "\n")
    return m.blind_words(keep), len(lines) - len(keep)


def tokens(s: str) -> list[str]:
    return re.findall(r"[a-z]+", s.lower())


def source_tokens(note_dir: Path) -> str:
    """The letter tokens of paper_body.tex and the abstract, with references, values and macros removed, so that a
    quote's survival does not depend on page layout or on section letters that a move renumbers."""
    body = (note_dir / PB).read_text(encoding="utf-8")
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", (note_dir / MP).read_text(encoding="utf-8"), re.S)
    out = []
    for l in (m.group(1) if m else "").split("\n") + body.split("\n"):
        if l.lstrip().startswith("%"):
            continue
        l = re.sub(r"\\(fvval|ref|nsec|napp|cite|label|eqref|SI|si|num)\*?\{[^}]*\}(\{[^}]*\})?", " ", l)
        l = re.sub(r"\\[A-Za-z]+", " ", l)
        out.append(" ".join(tokens(l)))
    return " " + " | ".join(out) + " "


def run_len(q: list[str], src: str) -> int:
    """The longest contiguous run of the quote's tokens found in the source token stream."""
    for L in range(len(q), 0, -1):
        if any(" " + " ".join(q[j:j + L]) + " " in src for j in range(len(q) - L + 1)):
            return L
    return 0


def load_tally(remeasure: Path):
    spec = importlib.util.spec_from_file_location("caveat_tally", remeasure.parent.parent / "caveat-study" / "tools" / "tally.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        (t / PB).write_text("a\n\\subsection{X}\nx one\n\\subsection{Y}\ny two. Gone here.\n")
        (t / MP).write_text("abs\n")
        saved = dict(CANDIDATES)
        CANDIDATES.clear()
        CANDIDATES.update({"K": {"moves": "x", "edits": [("range", PB, "\\subsection{X}", "\\subsection{Y}", "ptr\n"),
                                                         ("sub", PB, " Gone here.", "")]},
                           "R": {"moves": "r", "edits": [("sub", PB, "missing", "", "optional")]},
                           "B": {"moves": "b", "edits": [("sub", PB, "nothing like this", "")]}})
        try:
            out = apply_edits(t, ["K"])[PB]
            assert out == "a\nptr\n\n\\subsection{Y}\ny two.\n", repr(out)
            assert apply_edits(t, ["R"])[PB] == (t / PB).read_text()  # optional, absent: skipped
            try:
                apply_edits(t, ["B"])
                raise AssertionError("a missing required anchor must stop the run")
            except SystemExit:
                pass
        finally:
            CANDIDATES.clear()
            CANDIDATES.update(saved)
    print("self-test: range delete with pointer, optional skip, missing anchor stops: ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--src"); ap.add_argument("--inv"); ap.add_argument("--work")
    ap.add_argument("--only", default=",".join(k for k in CANDIDATES if not CANDIDATES[k].get("requires")))
    ap.add_argument("--combo", action="append", default=[])
    ap.add_argument("--out")
    ap.add_argument("--remeasure", default=str(REMEASURE), help="remeasure.py (default: beside this directory)")
    ap.add_argument("--pointers", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.pointers:
        print(json.dumps({k: pointer_sentences([k]) for k in CANDIDATES}, indent=1, ensure_ascii=False))
        return
    src, inv, work = Path(a.src).resolve(), Path(a.inv).resolve(), Path(a.work).resolve()
    runs = [[]] + [[k] for k in a.only.split(",") if k] + [c.split("+") for c in a.combo]
    res = []
    for keys in runs:
        r = measure(src, inv, work, keys, Path(a.remeasure))
        print(f"{'+'.join(keys) or 'base':28s} words {r['words']:5d} (leaked {r['leaked_back_matter_lines']:2d})  layout artifacts {len(r['statements_layout_artifact']):2d}  "
              f"distinct {r['distinct']:2d}  per 1k {r['distinct_per_1k']:5.2f}  gone: {r['caveats_gone']}", flush=True)
        res.append(r)
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
