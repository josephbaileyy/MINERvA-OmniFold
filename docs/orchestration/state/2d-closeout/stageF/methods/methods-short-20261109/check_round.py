#!/usr/bin/env python3
"""Check the short methods paper's round (methods-short-20261109) against its work order and ledgers.

  1. VARIANTS. Every pending key of make_values_fived16.PENDING that a sentence depends on is written once per class:
     at each site (one paragraph of paper_body.tex or main_paper.tex), the classes of its \\fvcase{key}{class}{...}
     equal the key's declared class set, minus the classes declared EMPTY below (a class that prints nothing). Every
     \\fvcase key is declared, and every \\fvcase sits inside an \\fvgroup of the key's own group.
  2. NO NUMBER IN A VARIANT. The text of every \\fvcase, with \\fvval{...}, \\ref{...} and \\cite{...} removed, has no
     digit: filling a result writes no number that the readout does not supply.
  3. EVERY KEY DEFINED. Every \\fvval key of the paper and the Supplement is defined in values_fived16.tex. A key
     inside a pending \\fvgroup is never expanded, so the build cannot catch a missing one; this does.
  4. NUMERALS. Every numeral the paper prints (comments stripped; \\fvval, \\ref, \\cite, \\label, \\includegraphics and
     pointer arguments removed) is printed by the base (round 5, BASE) too, or is in NEW_NUMERALS with its source.
  5. ONCE / GONE. The new sentences the ledger records print exactly once (ONCE); the claims the decision excludes,
     and the internal labels the editor's read lists, print nowhere in the paper (GONE).
  6. SEC4 TESTS. test_check_sec4_receipts.py passes (the director, 2026-11-09; the hook does not run it).
  7. FILL TEST (--fill-test, slow). The paper is built once per class index: every pending key set to its i-th
     class (cyclically), and the like-for-like group to the i-th of make_values_fived16.ll5d_fill_cases(), which
     are consistent with its derived keys and between them reach every class; so every variant is typeset at least
     once. Each build must succeed with no "[PENDING", no "??", no undefined reference, and no printed class name
     (check 8).
  8. NO CLASS NAME IN PRINT (printed_class_names; run by the fill test and by preread-outcomes/build_cases.py on
     every build). A filled build prints no raw class name (any class with a hyphen, in either spelling, or "na"),
     and never "joseph" outside the author line, the email and the repository URL (the director, 2026-11-09, item 8).
  8. STYLE REPORT (printed, never a failure; the director, 2026-11-09). The rate per 1,000 words of each pattern of
     style_metrics.py, vendored unchanged from the director's field baseline (sha256 8bf224280556ea41), against the
     field's per-paper maximum in style-baseline.json (11 human-written papers before November 2022, 78,599 words).
     A pattern above the field maximum is marked ABOVE. It runs on the round's blind manuscript, the blind Supplement and VARIANTS.txt
     (preread-outcomes/, or --printed FILE ...).
  9. FIGURES. The bias-by-cell figure agrees with the current paper: figures/methods_short/make_figures.py's
     check_against(paper_body, values_tex), the figures lane's own function, checks Table 2's truth order, the
     outline threshold (trig-z) and every plotted maximum |z| against values_fived16.tex. A changed figure input
     (its sha256 pins) fails too.
  10. ABSTRACT LENGTH (Joseph, 2026-11-09, via the director: the typical length, 200-250 words). Every rendered case of
     the abstract (abstract_text: the source with \\fvgroup/\\fvcase resolved and \\fvval from the values), all of them
     before the fill and the built one after it, must print at most ABSTRACT_MAX_WORDS = 250 words. The range in words
     and characters is reported, and no case may repeat a run of ABSTRACT_REPEAT = 8 words (the director, on the
     independent read of 74db4ea97). arXiv's 1,920 characters apply to a separate metadata abstract, written at
     submission (REPORT.md, "Follow-up: before submission"). No rendered case may print a phrase of ABSTRACT_BANNED
     (" only at ", which attaches a restriction to the tunes rather than to the noun).
  12. SUPPLEMENT-NOTE SYNC (report only; the director, 2026-11-10). check_supp_sync.py pairs each note-copied Supplement
     paragraph (its "% source:" comment) with its note source, three-way against the Supplement's seed commit, and
     reports any difference that no restyled/adapted/fixed comment explains, or a note paragraph that changed since the
     seed (--note-rev REV compares against the note lane's head).
  11. FREE TEXT (journal-editor, 2026-11-09). A filled free-text value (a PENDING key with no class set, such as
     ll5d-clip-record or ll5d-route-record) prints inside prose, so it may not contain a FREE_TEXT_BANNED term: gate,
     record, readout, receipt, lane, binding, declaration, a DECISION/OUTCOME name, a date, an .md file, or a PR number.
  13. NOTE RELEASE (the director, 2026-11-10, journal-editor's cross-document review X1). The paper's and the Supplement's
     pointers into the note print the numbers of note_release_labels.tex (make_note_labels.py), not of this branch's own
     copy of the note. The file must name NOTE_RELEASE_REV, the note revision named for release; main_paper.tex and
     main_supplement.tex must \\input it and load no \\externaldocument[N-]; and every note label they and the two bodies
     cite must be in it. The fill test also rebuilds the file from the note at NOTE_RELEASE_REV (make_note_labels.py
     --check) and fails unless it is byte-identical. Changing the release revision means changing NOTE_RELEASE_REV and
     rerunning make_note_labels.py --rev, in one commit.
NOTE (printed on every run; not checked here). The figures sit where the blind rater copy passes its hold-diff check
(rater-calibration/make_rater_copy.sh). A float near section 7 split the long section 7 hold ("A citable home ...")
across a page break, and the copy failed. Any reflow of sections 6-7 (a float moved, a caption or paragraph
lengthened) can split it again: rebuild the rater copy after one (ledger.md, "Figures 1 and 2").
usage: check_round.py <worktree> [--base SHA] [--fill-test] [--printed FILE ...] [--note-rev REV]   (exit 1 on any failure)
       check_round.py <worktree> --self-test                  (each planted defect must be caught)"""
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = "bc8673186"
HERE = Path(__file__).resolve().parent
NOTE = "docs/analysis-note"
ROOT = HERE.parents[6]          # the worktree that holds this file (check 13's self-test copies its drivers)
FILES = ["paper_body.tex", "main_paper.tex"]
# classes that print nothing by design (variants.md, the rows marked EMPTY)
EMPTY = {**{f"prr-label-{l}-{t}": {"not"} for l in ("fir", "info", "impl", "obs", "stat", "unattr") for t in ("gibuu", "q3")},
         **{f"ll5d-{t}-{r}": {"na"} for t in ("g18", "ar23") for r in ("minus2", "all")},
         **{f"ll5d-{t}-{r}-{x}": {"none", "na"} for t in ("g18", "ar23") for r in ("minus2", "all")
            for x in ("weak", "over", "clip")},
         "ll5d-route": {"direct", "na"},
         "ll5d-abs-minus2": {"na"}, "ll5d-abs-all": {"na"}, "ll5d-abs-close": {"scope", "na"},
         **{f"ll5d-{x}": {"none", "na"} for x in ("anypass", "cellflags", "anyweak", "anyover")}}
# numerals the paper prints that the base does not, each with its source (ledger rows)
NEW_NUMERALS = {"4.5": "group A item 6 (#1025): the signal phase space, pT < 4.5 GeV/c, Supplement S1 (sec:selection) and ref. MINERvA:2021owq",
                "42": "ledger Figure 3: a3_rounding_shifts.csv (PR #1008, sha256 9ac8f7d8), 42 EW rows of its 153 (109 J, 42 EW, two totals)",
                "39": "ledger Figures: app_statmethods_nd.tex:25, the 39 EW cells of the prior-response figure (J 109 and H2 27 are in the base)",
                "285": "L-12b: re2 partc-r2 receipts/figs/tension_report.txt:55, 1.391 x 205 = 285.2 (in [285.05, 285.26])",
                "136": "L-12b: the note's sec_results.tex:128 (chi2 = 136 on the 73 best-determined directions)",
                "0.05": "L-27: FD-PRR-DECLARATION.md:281-286, the bar delta_F = max(0.05, 9.03 s_F)",
                "9.03": "L-27: FD-PRR-DECLARATION.md:281-286 (the two-sided Student-t quantile on 4 degrees of freedom at 0.01/12)",
                "0.01": "L-27: FD-PRR-DECLARATION.md:282-284 (the familywise rate 0.01 over the 12 primary readings)",
                "0.10": "P-9: LL5D-DECLARATION.md:486, the test's resolution, about 0.10 in coverage per cell",
                "0.08": "P-9: LL5D-DECLARATION.md:486, the test's resolution, about 0.08 jointly (0.10 per cell)",
                "0.025": "P-9: LL5D-DECLARATION.md:471-472, :482, the size per (truth, reading): 0.025 over the cells, 0.025 joint",
                "99.7": "L-28: r5:176's bar 39.04 at the null's 0.997 quantile, printed as the 99.7th percentile (round 6, the editor's B8)"}
ONCE = [
    "and their cross-covariance is unavailable, so the significance of their difference cannot be calibrated.",
    "The five-observable estimator is the baseline this study characterizes",
    "We report the ensemble average as a tested mitigation of the instability.",
    "That test is a next step.",
    "The grading rules and their timing are stated with the individual tests; comparisons without a grading rule are descriptive.",
]
# validat...: the affirmative claim decision item 6 (:74) forbids; its denial, "does not validate ...", is allowed
GONE = [r"stabili[sz]ed variant", r"(?<!not )validat\w* the (full|five-observable) distribution", r"detector[- ]inadequa",
        r"locali[sz]ed in", r"\bE_?\{?96", r"\bFD-PRR\b", r"\bLL5D\b", r"\bV-HALF\b", r"\bV-ATLAS\b", r"\bV-PRIOR\b",
        r"\bCOV2D\b", r"\bRS1\b", r"\bENS1\b", r"\bFD-STAB\b", r"BIAS_WORSE", r"Stage~?0c", r"\bPR-[123]",
        r"\bdeclared\b", r"joint-test estimator", r"\\chi\^\{2\}/205", r"tracks the same bias", r"natural next step",
        r"\b187 universes"]   # the July sweep's count; Q's universe block is the key cov2d-nuniv (director, 2026-11-10)


def load_mv(wt):
    spec = importlib.util.spec_from_file_location("mv", wt / NOTE / "make_values_fived16.py")
    mv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mv)
    return mv


def strip_comments(t):
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", l) for l in t.split("\n"))


def braced(t, i):
    """The content of the brace group opening at t[i] == '{', and the index after it."""
    assert t[i] == "{", t[i:i + 20]
    d, j = 1, i + 1
    while d:
        d += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 1:j - 1], j


def macro_calls(t, name, nargs):
    """(start, [args]) for every \\name{..}{..} call in t."""
    out = []
    for m in re.finditer(r"\\" + name + r"(?![A-Za-z])", t):
        j, args = m.end(), []
        for _ in range(nargs):
            a, j = braced(t, j)
            args.append(a)
        out.append((m.start(), j, args))
    return out


def check_variants(texts, pending, groups):
    fails = []
    for f, t in texts.items():
        t = strip_comments(t)
        spans = [(s, e, a[0]) for s, e, a in macro_calls(t, "fvgroup", 2)]
        for ln, line in enumerate(re.split(r"\n\s*\n", t), 1):     # a site is one paragraph
            sites = {}
            for _, _, (k, c, _) in macro_calls(line, "fvcase", 3):
                sites.setdefault(k, set()).add(c)
            for k, cs in sites.items():
                if k not in pending:
                    fails.append(f"{f} paragraph {ln}: \\fvcase key {k} is not declared in PENDING")
                    continue
                want = set(pending[k][1] or ()) - EMPTY.get(k, set())
                if cs != want:
                    fails.append(f"{f} paragraph {ln}: {k} has variants {sorted(cs)}, its declared classes are {sorted(want)}")
        for s, _, (k, _, _) in macro_calls(t, "fvcase", 3):
            g = pending.get(k, (None,))[0]
            if not any(a <= s < b and gg == g for a, b, gg in spans):
                fails.append(f"{f}: \\fvcase{{{k}}} is not inside an \\fvgroup{{{g}}}")
        for _, _, (g, _) in macro_calls(t, "fvgroup", 2):
            if g not in groups:
                fails.append(f"{f}: \\fvgroup{{{g}}} is not a declared group")
    return fails


def check_no_number(texts):
    fails = []
    for f, t in texts.items():
        for _, _, (k, c, body) in macro_calls(strip_comments(t), "fvcase", 3):
            b = re.sub(r"\\(fvval|ref|cite|label)\{[^}]*\}", "", body)
            b = re.sub(r"\\(ssecc?|nsec|napp|stab)\{[^}]*\}(\{[^}]*\})?", "", b)   # pointers to sections, not numbers
            b = re.sub(r"\\fvcase\{[^}]*\}\{[^}]*\}", "", b)          # a nested variant's key and class
            b = re.sub(r"_\{?\d\}?", "", b)                             # a symbol's subscript, as in $q_3$
            if re.search(r"\d", b):
                fails.append(f"{f}: the variant {k}={c} prints a number: {body[:80]!r}")
    return fails


def check_keys(texts, values_tex):
    have = set(re.findall(r"\\@namedef\{fv@([^}]+)\}", values_tex))
    fails = []
    for f, t in texts.items():
        for k in set(re.findall(r"\\fvval\{([^}]+)\}", strip_comments(t))):
            if k not in have:
                fails.append(f"{f}: \\fvval{{{k}}} is not defined in values_fived16.tex")
    return fails


def numerals(t):
    t = strip_comments(t)
    t = "\n".join(l for l in t.split("\n") if not re.match(r"\s*\\begin\{tabular\*?\}", l))   # column widths
    t = re.sub(r"\d+(?:\.\d+)?\s*(?:pt|cm|mm|em|ex|in|bp)\b", " ", t)     # TeX lengths (\tabcolsep{2.25pt}, \hspace{5pt})
    t = re.sub(r"\\(fvval|ref\*?|nsec|napp|cite|label|eqref|includegraphics|fvpending|fvgroup|ssecc?|stab)(\[[^]]*\])?\{[^}]*\}(\{[^}]*\})?", " ", t)
    t = re.sub(r"\\fvcase\{[^}]*\}\{[^}]*\}", " ", t)
    t = re.sub(r"\\(begin|end)\{[^}]*\}(\{[^}]*\})?", " ", t)
    t = re.sub(r"\\[A-Za-z]+", " ", t)
    return set(re.findall(r"\d+(?:\.\d+)?", t))


def check_numerals(cur, base):
    have = set().union(*(numerals(t) for t in base.values()))
    new = set().union(*(numerals(t) for t in cur.values())) - have - set(NEW_NUMERALS)
    return [f"a numeral new to the base, with no source: {n}" for n in sorted(new)]


def check_once_gone(cur):
    fails = []
    body = re.sub(r"\s+", " ", " ".join(strip_comments(t) for t in cur.values()))
    for s in ONCE:
        n = body.count(s)
        if n != 1:
            fails.append(f"ONCE: printed {n} times: {s[:70]!r}")
    for g in GONE:
        m = re.search(g, body)
        if m:
            fails.append(f"GONE: {g!r} prints: ...{body[max(0, m.start() - 40):m.end() + 40]}...")
    return fails


LABELS = GONE[4:]   # the internal labels (not the claim phrases): checked in the printed pending-group names too


def check_printed_names(values_tex):
    """Round 6 (the editor's C4): the pending groups' names print in the paper, so the internal labels must not be in them."""
    fails = []
    for g, name in re.findall(r"\\@namedef\{fvgd@([^}]+)\}\{([^}]*)\}", values_tex):
        for pat in LABELS:
            if re.search(pat, name):
                fails.append(f"values_fived16.tex: the pending group {g} prints the internal label {pat!r}: {name!r}")
    return fails


def check_dates(texts):
    """Round 6 (the director's item 2): no ISO date in the printed paper or Supplement (comments stripped)."""
    fails = []
    for f, t in texts.items():
        for m in re.finditer(r"\b(19|20)\d\d-\d\d-\d\d\b", strip_comments(t)):
            fails.append(f"{f}: an internal date prints: {m.group(0)}")
    return fails


def check_sec4_tests(wt):
    """The director, 2026-11-09: test_check_sec4_receipts.py's cases bind printed sentences of the paper and the
    Supplement, and the pre-commit hook does not run them, so two went stale unnoticed. Run them here."""
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "test_check_sec4_receipts.py"], cwd=wt / NOTE,
                       capture_output=True, text=True, errors="replace")
    return [] if r.returncode == 0 else [f"test_check_sec4_receipts.py fails: {r.stdout.strip().splitlines()[-1]}"]


# Typed literals that a protected span keeps but a build-checked key also prints (the director, 2026-11-10, on the
# interim round's batch 2): the B0 sentences' "the quoted 2.6 statistical standard deviations" is protected by
# check_restyle, so it stays typed, and must equal the key that §6.1's observation and Table 2 print.
LITERAL_KEYS = [("paper_body.tex", r"the quoted ([0-9.]+) statistical standard deviations is the largest shift", "s5e-round-max"),
                # T1-1: the protected B0 span's sixteen-cell rounding spread, typed, against RS1 R0's keys (rs1_r0.json 724f0c3a)
                ("paper_body.tex", r"it is a median \\SI\{([0-9.]+)\}\{\\percent\} of the cross section", "rnd16-median"),
                ("paper_body.tex", r"of the cross section \(\\SIrange\{([0-9.]+)\}\{[0-9.]+\}\{\\percent\}\)", "rnd16-min"),
                ("paper_body.tex", r"of the cross section \(\\SIrange\{[0-9.]+\}\{([0-9.]+)\}\{\\percent\}\)", "rnd16-max"),
                # T1-3: S6's 132-direction reading, typed because #981's quote Q23 quotes it, against the per-period read
                ("supplemental_body.tex", r"In the ([0-9]+) poorly determined directions, the combination of the other two", "pp-kbar"),
                ("supplemental_body.tex", r"than the three-group combination, by ([0-9.]+) per direction", "pp-dbar")]


def check_literal_keys(texts, values_tex, entries=None):
    have = dict(re.findall(r"\\@namedef\{fv@([^}]+)\}\{([^{}]*)\}", values_tex))
    fails = []
    for f, pat, key in (LITERAL_KEYS if entries is None else entries):
        got = re.findall(pat, re.sub(r"\s+", " ", strip_comments(texts[f])))
        if len(got) != 1:
            fails.append(f"{f}: the literal for {key} is found {len(got)} times (expected 1)")
        elif key not in have or got[0] != have[key]:
            fails.append(f"{f}: the typed {got[0]} differs from \\fvval{{{key}}} = {have.get(key)!r}")
    return fails


# The note revision named for release (the director, 2026-11-10: "building against #952's note (acf934d71)"); #952's head
# moved to 3257d7c61 the same day with no change to any label (all 217 compared), so the named revision stands until the
# director names another.
NOTE_RELEASE_REV = "acf934d71fce0e4805615b9b9aceb4ea3bdae444"


def check_note_release(d, release=None):
    """Check 13 on the directory d (a docs/analysis-note): the label file names the release revision, the two drivers
    read it and no main_note.aux, and every cited note label is in it."""
    release = release or NOTE_RELEASE_REV
    fails = []
    lab = d / "note_release_labels.tex"
    if not lab.exists():
        return ["note release: note_release_labels.tex is missing (make_note_labels.py --rev " + release[:12] + ")"]
    text = lab.read_text()
    m = re.match(r"% note revision: ([0-9a-f]{40})", text)
    if not m or m.group(1) != release:
        fails.append(f"note release: note_release_labels.tex is from the note at {m.group(1)[:12] if m else '?'}, "
                     f"but the revision named for release is {release[:12]}")
    for f in ("main_paper.tex", "main_supplement.tex"):
        s = strip_comments((d / f).read_text())
        if r"\input{note_release_labels}" not in s:
            fails.append(f"note release: {f} does not \\input{{note_release_labels}}")
        if re.search(r"\\externaldocument\[N-\]", s):
            fails.append(f"note release: {f} still reads the note's labels through \\externaldocument[N-]")
    have = set(re.findall(r"\\newlabel\{N-([^}]+)\}", text))
    spec = importlib.util.spec_from_file_location("make_note_labels", d / "make_note_labels.py")
    mnl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mnl)
    missing = sorted(mnl.cited(d) - have)
    if missing:
        fails.append(f"note release: cited note labels missing from note_release_labels.tex: {missing}")
    return fails


def run(wt, base):
    mv = load_mv(wt)
    cur = {f: (wt / NOTE / f).read_text() for f in FILES}
    old = {f: subprocess.run(["git", "-C", str(wt), "show", f"{base}:{NOTE}/{f}"], capture_output=True, text=True,
                             check=True).stdout for f in FILES}
    supp = (wt / NOTE / "supplemental_body.tex").read_text()
    fails = (check_variants(cur, mv.PENDING, mv.PENDING_GROUPS) + check_no_number(cur)
             + check_keys({**cur, "supplemental_body.tex": supp}, (wt / NOTE / "values_fived16.tex").read_text())
             + check_numerals(cur, old) + check_once_gone(cur)
             + check_printed_names((wt / NOTE / "values_fived16.tex").read_text())
             + check_dates({**cur, "supplemental_body.tex": supp})
             + check_sec4_tests(wt) + check_figures(wt) + check_abstract(wt)
             + check_free_text(mv.PENDING, mv.VERDICTS)
             + check_literal_keys({**cur, "supplemental_body.tex": supp}, (wt / NOTE / "values_fived16.tex").read_text())
             + check_note_release(wt / NOTE))
    return fails


IDENT = ("Joseph Bailey", "josephrb@stanford.edu", "josephbaileyy")   # the author line, the email, the repository URL


def printed_class_names(txt, mv):
    """Check 8 on one build's pdftotext: the raw class names and 'joseph' that print, if any."""
    t = re.sub(r"-\n(?=[a-z])", "-", txt)                 # keep a compound's hyphen at a line break
    t = re.sub(r"\s+", " ", t)
    for s in IDENT:
        t = t.replace(s, " ")
    words = {w for k in getattr(mv, "WORDS", {}) for w in mv.WORDS[k].values()}
    names = {c for _, cls in mv.PENDING.values() if cls for c in cls if "-" in c}
    pats = sorted({re.escape(s) for c in names for s in (c, c.replace("-", " ")) if s not in words})
    found = [m.group(0) for p in pats for m in re.finditer(r"(?<![\w-])" + p + r"(?![\w-])", t)]
    found += re.findall(r"(?<![\w-])na(?![\w-])", t)
    found += re.findall(r"(?i)joseph", t)
    return sorted(set(found))


def style_report(paths):
    """Check 8: each file's pattern rates against the field maximum; returns the printed lines (never a failure)."""
    sm = importlib.util.spec_from_file_location("style_metrics", HERE / "style_metrics.py")
    mod = importlib.util.module_from_spec(sm)
    sm.loader.exec_module(mod)
    base = json.loads((HERE / "style-baseline.json").read_text())["patterns"]
    lines = []
    for p in paths:
        r = mod.score(Path(p).read_text())
        above = []
        lines.append(f"STYLE (report only) {Path(p).name}: {r['words']} words")
        for k, e in r["patterns"].items():
            fmax = base[k]["field_max"]
            mark = "ABOVE" if e["per_1000"] > fmax else ""
            if mark:
                above.append(k)
            lines.append(f"  {k:24s} ours {e['per_1000']:6.2f} ({e['count']:3d})  field max {fmax:5.2f}  pooled "
                         f"{base[k].get('field_pooled', float('nan')):5.2f}  {mark}")
        lines.append(f"  above the field maximum: {', '.join(above) if above else 'none'}")
    return lines


def style_report_text(text):
    """The style counts for one text (the self-test's check of the vendored script)."""
    sm = importlib.util.spec_from_file_location("style_metrics", HERE / "style_metrics.py")
    mod = importlib.util.module_from_spec(sm)
    sm.loader.exec_module(mod)
    return {k: e["count"] for k, e in mod.score(text)["patterns"].items()}


# words a free-text value may not print (journal-editor, 2026-11-09: they are internal, and the value prints inside prose)
FREE_TEXT_BANNED = (r"\bgates?\b", r"\brecords?\b", r"\breadouts?\b", r"\breceipts?\b", r"\blanes?\b", r"\bbindings?\b",
                    r"\bdeclar\w*", r"DECISION-", r"\b20\d\d-\d\d-\d\d\b", r"\bOUTCOME-", r"\.md\b", r"\bPR\s*#?\d+", r"#\d{3,}")


def check_free_text(pending, verdicts):
    """Every filled free-text value (a PENDING key with no class set) prints no FREE_TEXT_BANNED term."""
    out = []
    for k, (g, classes) in pending.items():
        if classes is None and k in verdicts:
            for pat in FREE_TEXT_BANNED:
                m = re.search(pat, str(verdicts[k]), re.I)
                if m:
                    out.append(f"the free-text value {k} prints {m.group(0)!r}: {str(verdicts[k])[:80]!r}")
    return out


def check_figures(wt):
    """Check 9: the figures lane's check of its plotted data against the current paper."""
    path = wt / NOTE / "figures/methods_short/make_figures.py"
    if not path.exists():
        return ["figures/methods_short/make_figures.py is missing"]
    try:
        spec = importlib.util.spec_from_file_location("make_figures", path)
        mf = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mf)
        return [f"figures: {f}" for f in mf.check_against((wt / NOTE / "paper_body.tex").read_text(),
                                                          (wt / NOTE / "values_fived16.tex").read_text())]
    except Exception as exc:                       # a changed pinned input raises ValueError
        return [f"figures: {exc}"]


ABSTRACT_MAX_WORDS = 250  # words, on every rendered case (Joseph, 2026-11-09, via the director: the typical length, 200-250 words)
ARXIV_ABSTRACT_MAX = 1920  # arXiv's metadata field: a separate abstract written at submission (REPORT.md, before submission)
ABSTRACT_REPEAT = 8   # no rendered case may repeat a run of this many words (the director, 2026-11-09, on the 74db4ea97 read)


def repeated_clauses(text, n=None):
    """Every run of n (ABSTRACT_REPEAT) words, case and punctuation ignored, that occurs twice or more in text."""
    n = n or ABSTRACT_REPEAT
    w = re.findall(r"[a-z0-9%.]+(?:[-'’][a-z0-9]+)*", text.lower())
    seen, out = set(), set()
    for i in range(len(w) - n + 1):
        g = " ".join(w[i:i + n])
        (out if g in seen else seen).add(g)
    return out


# phrases no rendered case may print: "only at" attaches the restriction to the tunes, not the noun (journal-editor, 2026-11-09)
ABSTRACT_BANNED = (" only at ",)


def abstract_text(main_tex, values_tex, ver):
    """The abstract as it prints for the classes ver: \\fvgroup and \\fvcase resolved, \\fvval from ver or values."""
    vals = dict(re.findall(r"\\@namedef\{fv@([^}]+)\}\{(.*)\}\s*$", values_tex, re.M))
    s = strip_comments(main_tex)
    s = s[s.index(r"\begin{abstract}") + len(r"\begin{abstract}"):s.index(r"\end{abstract}")]
    assert r"\fvgroupalt" not in s, "abstract_text does not resolve \\fvgroupalt"
    pat = re.compile(r"\\(fvgroup|fvcase|fvval)(?![A-Za-z])")

    def render(t):
        out, i = [], 0
        while True:
            m = pat.search(t, i)
            if not m:
                return "".join(out + [t[i:]])
            out.append(t[i:m.start()])
            j, args = m.end(), []
            for _ in range({"fvgroup": 2, "fvcase": 3, "fvval": 1}[m.group(1)]):
                a, j = braced(t, j)
                args.append(a)
            if m.group(1) == "fvgroup":
                out.append(render(args[1]))
            elif m.group(1) == "fvcase":
                out.append(render(args[2]) if ver[args[0]] == args[1] else "")
            else:
                out.append(str(ver.get(args[0], vals[args[0]])))
            i = j

    t = render(s)
    t = re.sub(r"\\SI\{([^}]*)\}\{\\percent\}", r"\1%", t).replace(r"\%", "%").replace("~", " ")
    t = re.sub(r"\\[A-Za-z]+\*?", "", t).replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", t).strip()


def abstract_cases(mv):
    """Every consistent filling of the abstract's pending keys: each PR-2a pair; each ll5d campaign, and on a graded
    campaign each route and each pair of per-variant pairs (ll5d-abs-close derived as ll5d_derived derives it)."""
    pairs = [p for p in mv.LL5D_PAIR if p != "na"]
    ll5d = [{"ll5d-campaign": c, "ll5d-route": "na", "ll5d-abs-minus2": "na", "ll5d-abs-all": "na", "ll5d-abs-close": "na"}
            for c in mv.LL5D_C if c != "graded"]
    for route in (r for r in mv.LL5D_ROUTE if r != "na"):
        for a in pairs:
            for b in pairs:
                ll5d.append({"ll5d-campaign": "graded", "ll5d-route": route, "ll5d-abs-minus2": a, "ll5d-abs-all": b,
                             "ll5d-abs-close": "none" if a == b == "i-i" else "scope"})
    return [{"prr-abs": p, **v} for p in mv.PRR_ABS for v in ll5d]


def abstract_gate(main_tex, values_tex, cases, verdicts):
    """(failures, report lines). Every rendered case consistent with what is filled (all of them before the fill, the
    one built case after it) must print at most ABSTRACT_MAX_WORDS words and no ABSTRACT_BANNED phrase. The report
    gives the range in words and characters."""
    s = strip_comments(main_tex)
    keys = {a[0] for _, _, a in macro_calls(s[s.index(r"\begin{abstract}"):s.index(r"\end{abstract}")], "fvcase", 3)}
    live = [verdicts] if keys <= set(verdicts) else [c for c in cases if all(verdicts.get(k, v) == v for k, v in c.items())]
    texts = [abstract_text(main_tex, values_tex, c) for c in live]
    fails = sorted({f"a rendered abstract case contains {p!r}" for x in texts for p in ABSTRACT_BANNED if p in x})
    rep = sorted({g for x in texts for g in repeated_clauses(x)})
    if rep:
        fails.append(f"a rendered abstract case repeats a clause of {ABSTRACT_REPEAT} or more words: {rep[0]!r}"
                     + (f" (and {len(rep) - 1} more)" if len(rep) > 1 else ""))
    w = [len(x.split()) for x in texts]
    ch = [len(x) for x in texts]
    over = [i for i, n in enumerate(w) if n > ABSTRACT_MAX_WORDS]
    if over:
        k = max(over, key=lambda i: w[i])
        fails.append(f"{len(over)} rendered abstract case(s) over {ABSTRACT_MAX_WORDS} words; the longest, {w[k]} words: {live[k]}")
    k = max(range(len(w)), key=lambda i: w[i])
    state = "filled" if keys <= set(verdicts) else f"pending: {', '.join(sorted(keys - set(verdicts)))}"
    return fails, [f"ABSTRACT ({state}) over {len(live)} rendered case(s): {min(w)} to {max(w)} words, {min(ch)} to "
                   f"{max(ch)} characters (fails above {ABSTRACT_MAX_WORDS} words; the longest is {live[k]}). The arXiv "
                   f"metadata abstract ({ARXIV_ABSTRACT_MAX} characters) is written at submission."]


def check_abstract(wt):
    mv = load_mv(wt)
    fails, lines = abstract_gate((wt / NOTE / "main_paper.tex").read_text(), (wt / NOTE / "values_fived16.tex").read_text(),
                                 abstract_cases(mv), dict(mv.VERDICTS))
    for line in lines:
        print(line)
    return fails


def fill_test(wt):
    """Build the paper once per class index, every pending key at its i-th class; every build must be clean."""
    mv = load_mv(wt)
    n = max(len(c) for _, c in mv.PENDING.values() if c)
    fails = []
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "docs/analysis-note"
        shutil.copytree(wt / NOTE, d, ignore=shutil.ignore_patterns("archive", "main_*.pdf", "*.aux", "*.log", "*.fls", "*.fdb_latexmk"))
        (Path(td) / "docs/orchestration").mkdir(parents=True)
        (Path(td) / "docs/orchestration/state").symlink_to(wt / "docs/orchestration/state")
        r = subprocess.run([sys.executable, "-I", str(wt / NOTE / "make_note_labels.py"), "--check", NOTE_RELEASE_REV],
                           capture_output=True, text=True, errors="replace")   # check 13: the note at the release revision
        print(r.stdout.strip()[-300:])
        if r.returncode:
            fails.append("note release: note_release_labels.tex is not what make_note_labels.py --rev "
                         f"{NOTE_RELEASE_REV[:12]} writes")
        base_vals = (d / "values_fived16.tex").read_text()
        head = base_vals.split("\n")
        ll5d, prr = mv.ll5d_fill_cases(), mv.prr_fill_cases()
        for i in range(max(n, len(ll5d), len(prr))):
            ver = {}
            for k, (g, cls) in mv.PENDING.items():
                ver[k] = cls[i % len(cls)] if cls else f"X{k.split('-')[-1]}"
            ver.update(ll5d[i % len(ll5d)])
            ver.update(prr[i % len(prr)])
            lines = [l for l in head if not re.match(r"\\@namedef\{fv(g|gd|c)@", l)
                     and not any(l.startswith(rf"\@namedef{{fv@{k}}}") for k in mv.PENDING)]
            end = lines.index(r"\makeatother")
            pl = [l.replace("FILLED", "FILLED") for l in mv.pending_lines(ver)]
            (d / "values_fived16.tex").write_text("\n".join(lines[:end] + pl + lines[end:]))
            for f in d.glob("main_paper.*"):
                if f.suffix != ".tex":
                    f.unlink()
            r = subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main_paper.tex"],
                               cwd=d, capture_output=True, text=True, errors="replace")
            if r.returncode:
                fails.append(f"fill test {i}: main_paper build failed; see {d}/main_paper.log")
                continue
            txt = subprocess.run(["pdftotext", "main_paper.pdf", "-"], cwd=d, capture_output=True, text=True, errors="replace").stdout
            log = (d / "main_paper.log").read_text(errors="replace")
            for bad, what in (("[PENDING", "a pending marker"), ("??", "an unresolved reference")):
                if bad in txt:
                    fails.append(f"fill test {i}: the text prints {what}")
            if re.search(r"undefined (references|citations)|Reference .* undefined", log):
                fails.append(f"fill test {i}: undefined references")
            bad = printed_class_names(txt, mv)
            if bad:
                fails.append(f"fill test {i}: a class name prints: {bad}")
            print(f"fill test {i}: built, {len(txt.split())} words")
    return fails


def self_test():
    pend = {"k": ("g", ("a", "b")), "e": ("g", ("x", "y"))}
    EMPTY["e"] = {"y"}
    good = {"f": r"\fvgroup{g}{\fvcase{k}{a}{one}\fvcase{k}{b}{two} \fvcase{e}{x}{three}}"}
    cases = [
        ("a missing variant", {"f": r"\fvgroup{g}{\fvcase{k}{a}{one}}"}, check_variants),
        ("an undeclared variant", {"f": r"\fvgroup{g}{\fvcase{k}{a}{1}\fvcase{k}{b}{2}\fvcase{k}{c}{3}}"}, check_variants),
        ("a case outside its group", {"f": r"\fvcase{k}{a}{one}\fvcase{k}{b}{two}"}, check_variants),
    ]
    ok = not check_variants(good, pend, {"g"}) and not check_no_number(good)
    for name, t, fn in cases:
        if not fn(t, pend, {"g"}):
            print("self-test: NOT CAUGHT", name)
            ok = False
    if not check_no_number({"f": r"\fvgroup{g}{\fvcase{k}{a}{in 3 cells}}"}):
        print("self-test: NOT CAUGHT a number in a variant"); ok = False
    if check_no_number({"f": r"\fvgroup{g}{\fvcase{k}{a}{in cells \fvval{k-cells} (section~\ref{s:1})}}"}):
        print("self-test: a key or a reference was taken for a number"); ok = False
    if not check_keys({"f": r"\fvval{nope}"}, r"\@namedef{fv@yes}{1}"):
        print("self-test: NOT CAUGHT an undefined key"); ok = False
    if not check_numerals({"f": "a 7.77 here"}, {"f": "a 7.7 here"}):
        print("self-test: NOT CAUGHT a new numeral"); ok = False
    if check_numerals({"f": "\\setlength{\\tabcolsep}{2.25pt}\n  \\begin{tabular*}{\\textwidth}{p{3.0cm}l}\nx"}, {"f": "x"}):
        print("self-test: a TeX length or a tabular* column spec was taken for a printed numeral"); ok = False
    if not check_numerals({"f": "a 2.25 here, \\hspace{5pt}"}, {"f": "here"}):
        print("self-test: NOT CAUGHT a printed numeral beside a length"); ok = False
    if not check_once_gone({"f": "the stabilised variant " + " ".join(ONCE)}):
        print("self-test: NOT CAUGHT a GONE phrase"); ok = False
    if not check_printed_names(r"\@namedef{fvgd@x}{LL5D, the test}"):
        print("self-test: NOT CAUGHT an internal label in a printed group name"); ok = False
    if not check_dates({"f": "until 2026-10-11; "}) or check_dates({"f": "% 2026-10-11 in a comment"}):
        print("self-test: the date check is wrong"); ok = False
    vt = "\\@namedef{fv@s5e-round-max}{2.6}"
    lit = "the quoted %s statistical standard deviations is the largest shift"
    one = LITERAL_KEYS[:1]
    if check_literal_keys({"paper_body.tex": lit % "2.6"}, vt, one) or not check_literal_keys({"paper_body.tex": lit % "2.5"}, vt, one) \
            or not check_literal_keys({"paper_body.tex": "no literal"}, vt, one):
        print("self-test: the literal-key check is wrong"); ok = False
    if not check_once_gone({"f": "the benchmark validates the five-observable distribution " + " ".join(ONCE)}):
        print("self-test: NOT CAUGHT an affirmative validation claim"); ok = False
    if not check_once_gone({"f": "the test not only validates the five-observable distribution " + " ".join(ONCE)}):
        print("self-test: NOT CAUGHT 'not only validates', an affirmative claim behind a 'not'"); ok = False
    if check_once_gone({"f": "it does not validate the five-observable distribution. " + " ".join(ONCE)}):
        print("self-test: GONE flags the denial that decision item 6 asks for"); ok = False
    if not check_once_gone({"f": " ".join(ONCE[1:])}):
        print("self-test: NOT CAUGHT a missing ONCE sentence"); ok = False
    class _MV:
        PENDING = {"k": ("g", ("under-cells", "no-effect", "covers"))}
        WORDS = {"k": {"no-effect": "no effect"}}
    if printed_class_names("the test covers; the factor has no effect. Joseph Bailey, josephrb@stanford.edu", _MV):
        print("self-test: check 8 flags a printed word or the author line"); ok = False
    for planted in ("it under cells here", "it under-\ncells here", "the status to joseph", "na, na", "under-cells"):
        if not printed_class_names(planted, _MV):
            print("self-test: NOT CAUGHT a printed class name:", repr(planted)); ok = False
    sr = style_report_text("The test grades bias, not coverage. It holds.")
    if sr.get("1_comma_not") != 1:
        print("self-test: the style report misses a ', not' contrast"); ok = False
    am = r"\begin{abstract}A test. \fvgroup{g}{\fvcase{k}{a}{" + "word " * 260 + r"}\fvcase{k}{b}{short}} \fvval{v} fits.\end{abstract}"
    av = r"\@namedef{fv@v}{96}"
    if not abstract_gate(am, av, [{"k": "a"}, {"k": "b"}], {"k": "a"})[0]:
        print("self-test: NOT CAUGHT a filled abstract over the limit"); ok = False
    if abstract_gate(am, av, [{"k": "a"}, {"k": "b"}], {"k": "b"})[0]:
        print("self-test: the abstract gate fails a short filled case"); ok = False
    if not abstract_gate(am, av, [{"k": "a"}, {"k": "b"}], {})[0]:
        print("self-test: NOT CAUGHT an unfilled case over the word limit"); ok = False
    if not abstract_gate(am.replace("{short}", "{cells only at one tune}"), av, [{"k": "a"}, {"k": "b"}], {})[0]:
        print("self-test: NOT CAUGHT an 'only at' in a rendered case"); ok = False
    rp = r"\begin{abstract}It finds no under-coverage at one tune and an invalid reading here and no under-coverage at one tune and an invalid reading there.\end{abstract}"
    if not abstract_gate(rp, av, [{}], {})[0]:
        print("self-test: NOT CAUGHT a repeated 8-word clause"); ok = False
    if repeated_clauses("one two three four five six seven, then one two three four five six eight"):
        print("self-test: the repeated-clause check flags a 7-word repeat"); ok = False
    if abstract_text(am, av, {"k": "b"}) != "A test. short 96 fits.":
        print("self-test: abstract_text misrenders:", repr(abstract_text(am, av, {"k": "b"}))); ok = False
    ms = subprocess.run([sys.executable, "-I", str(HERE.parent / "rater-calibration/tools/multiset_check.py"), "--self-test"],
                        capture_output=True, text=True)
    if ms.returncode:
        print("self-test: the rater copy's multiset_check.py fails its own self-test:", ms.stdout.strip()[-200:]); ok = False
    fp = {"x-record": ("g", None), "x-class": ("g", ("a",))}
    for planted in ("the gate sample", "the readout says", "see DECISION-20261109-joseph-x.md", "on 2026-11-09", "the lane's receipt"):
        if not check_free_text(fp, {"x-record": planted}):
            print("self-test: NOT CAUGHT a banned term in a free-text value:", repr(planted)); ok = False
    if check_free_text(fp, {"x-record": "the largest offset, 0.04 in R06, below its bound of 0.10", "x-class": "a"}):
        print("self-test: the free-text check flags clean journal prose"); ok = False
    with tempfile.TemporaryDirectory() as td:          # check 13: each planted defect in a copy of the four drivers
        d = Path(td)
        for f in ("make_note_labels.py", "note_release_labels.tex", "main_paper.tex", "main_supplement.tex",
                  "paper_body.tex", "supplemental_body.tex"):
            shutil.copy(ROOT / NOTE / f, d / f)
        if check_note_release(d):
            print("self-test: check 13 flags the committed note labels:", check_note_release(d)); ok = False
        lab = (d / "note_release_labels.tex").read_text()
        plants = [("another revision named", lambda: check_note_release(d, "0" * 40)),
                  ("a driver back on main_note.aux", lambda: ((d / "main_paper.tex").write_text(
                      (ROOT / NOTE / "main_paper.tex").read_text().replace(r"\input{note_release_labels}",
                                                                           r"\externaldocument[N-]{main_note}")),
                      check_note_release(d))[1]),
                  ("a cited label missing", lambda: ((d / "main_paper.tex").write_text((ROOT / NOTE / "main_paper.tex").read_text()),
                      (d / "note_release_labels.tex").write_text(re.sub(r"\\newlabel\{N-tab:pl-added\}.*\n", "", lab)),
                      check_note_release(d))[2])]
        for name, fn in plants:
            if not fn():
                print("self-test: check 13 NOT CAUGHT:", name); ok = False
    del EMPTY["e"]
    print("self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    wt = Path(argv[0]).resolve()
    base = argv[argv.index("--base") + 1] if "--base" in argv else BASE
    fails = run(wt, base)
    if "--printed" in argv:
        printed = [a for a in argv[argv.index("--printed") + 1:] if not a.startswith("--")]
    else:
        po = HERE / "preread-outcomes"
        printed = [po / "manuscript.blind.txt", po / "supplement.blind.txt", po / "VARIANTS.txt"]
    for line in style_report([p for p in printed if Path(p).exists()]):
        print(line)
    try:                    # the Supplement-note sync report (check_supp_sync.py; the director, 2026-11-10): never a failure
        spec = importlib.util.spec_from_file_location("check_supp_sync", HERE / "check_supp_sync.py")
        sync = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sync)
        sync.run(wt, argv[argv.index("--note-rev") + 1] if "--note-rev" in argv else None)
    except Exception as exc:
        print(f"SUPP-SYNC :: not run ({exc})")
    if "--fill-test" in argv:
        fails += fill_test(wt)
    print("NOTE a reflow of sections 6-7 can split the section 7 hold across a page break and fail the blind rater"
          " copy's hold-diff check: rebuild it (make_rater_copy.sh) after any such change")
    for f in fails:
        print("FAIL", f)
    print(f"CHECK-ROUND methods-short :: {'PASS' if not fails else 'FAIL'} ({len(fails)} failures)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
