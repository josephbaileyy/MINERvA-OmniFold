#!/usr/bin/env python3
"""Seed docs/analysis-note/supplemental_body.tex from the analysis note's own text (round 5, 2026-11-08).

One-time extraction record, not a build step: it copies the named paragraphs of the note's sections verbatim
(comments stripped), drops figure environments, and rewrites every cross-reference that does not resolve inside
the Supplement into a numbered pointer to the note (xr-hyper prefix N-). The Supplement is then trimmed and edited
by hand; after that, supplemental_body.tex is the source and this script is only the record of where each block
came from.

usage: python3 -I seed_supplemental_body.py <analysis-note dir> <out.tex>
"""
import re
import sys

NOTE = sys.argv[1]
OUT = sys.argv[2]
FILES = ["sec_experiment.tex", "sec_eavailw.tex", "sec_3d.tex", "sec_method.tex", "app_negweight.tex",
         "sec_fived16.tex", "sec_systematics.tex", "sec_joint.tex", "sec_validation.tex"]
LEV = {"section": 1, "subsection": 2, "subsubsection": 3, "paragraph": 4}


def section_paragraphs(label):
    for f in FILES:
        s = open(f"{NOTE}/{f}", encoding="utf-8").read()
        i = s.find("\\label{%s}" % label)
        if i < 0:
            continue
        heads = list(re.finditer(r"\\(section|subsection|subsubsection|paragraph)\*?\{", s[:i]))
        h = heads[-1]
        lev = LEV[h.group(1)]
        end = len(s)
        for m in re.finditer(r"\\(section|subsection|subsubsection|paragraph|appendix)\*?\{?", s[i:]):
            g = m.group(1)
            if g == "appendix" or LEV.get(g, 9) <= lev:
                end = i + m.start()
                break
        text = s[h.start():end]
        # Split the RAW text into paragraphs, strip comments from each, and keep the paragraph's own
        # "% Search:" and "% absence-ok" lines (and those of comment-only paragraphs that follow it), so that a
        # copied paragraph carries the note's search record or waiver for its absence claims.
        paras, metas = [], []
        for raw in re.split(r"\n\s*\n", text):
            meta = [ln.strip() for ln in raw.split("\n") if re.match(r"^\s*%\s*(Search:|absence-ok)", ln)]
            lines = [ln for ln in raw.split("\n") if not re.match(r"^\s*%", ln)]
            body = "\n".join(re.sub(r"(?<!\\)%.*$", "", ln) for ln in lines).strip()
            if body:
                paras.append(body)
                metas.append(meta)
            elif metas:
                metas[-1].extend(meta)
        return f, list(zip(paras, metas))
    raise SystemExit(f"label {label} not found")


CSV = r"""% Source: make_supplemental.py's docstring (the three files and their content) at this commit; the files are
% generated only from the pinned data product and checked by make_supplemental.py --check.
\paragraph{Machine-readable files.} Three files accompany this Supplement. \texttt{xsec16\_cells.csv} gives the lower and upper edge of each of the sixteen cells R00--R15 on each axis. \texttt{xsec16\_cross\_section.csv} gives each cell's cross section, its uncertainty and its relative uncertainty. \texttt{xsec16\_covariance.csv} gives the reported covariance $C_{\mathrm{total}}+C_{\mathrm{resp}}+C_{\mathrm{PL,5D}}$ as a $16\times16$ matrix. The three files are generated from the same data product as the tables of this Supplement and of the paper, and reproduce the printed boxes, cross sections, relative uncertainties and correlation matrix to the printed precision."""
IBU = r"""% Sources: REF-G1-DECLARATION.md sec. 0, sec. 2, sec. 3.1 and sec. 4 R1 @ 49d82424 (the sixteen-cell comparison);
% REF-C2C1-DECLARATION.md sec. 1.3, sec. 1.4 and sec. 2 @ c2ec419a (the two-dimensional comparisons). Each number
% below is that record's declared constant; the results print in the paper, Sec. ibu.
The paper's three comparisons with a binned iterative Bayesian unfolding (IBU) were each declared, with their statistic, null and readings, before they ran. IBU is a cross-check in all three: it enters neither the reported result nor its covariance.

\paragraph{The sixteen-cell comparison.} The IBU is D'Agostini's, with the background template folded in as a known additive term in reconstructed space. It uses the same data, simulation, background template and weight-only systematic universes as the joint-test estimator. Its reconstructed bins are the fine five-observable cells inside the reconstruction window, its truth grid is the coarse grid whose unions are the cells R00--R15, its prior is the simulation's own truth, and it runs at five iterations (iterations 1--4, 10 and 20 are printed and read by nothing). Each of its 50 bootstrap replicas and each systematic universe is paired with the joint-test estimator's product made from the same draw or the same weights. The difference $\Delta=f_{\mathrm{IBU}}-f$ on the sixteen cells has the covariance $C_\Delta=C_{\Delta,\mathrm{stat}}+C_{\Delta,\mathrm{univ}}+C_{\Delta,\mathrm{norm}}$: the sample covariance of the paired replica differences, the reported covariance's estimators applied to the paired universe differences, and the 1.4\,\% normalization applied to $\Delta$. The model, lateral, response and run-period blocks are not in it. The statistic is $T=\Delta^{\top}C_\Delta^{-1}\Delta$. Because $C_{\Delta,\mathrm{stat}}$ is estimated from 50 replicas in 16 dimensions, $T$ is not read against $\chi^2_{16}$: its bars are the 0.95 and 0.997 quantiles of a parametric bootstrap of $10^{6}$ draws at the realized block composition, in which each draw resamples the replica covariance from 50 Gaussian vectors and the flux block from 100, holds the other bands fixed, and recomputes the normalization block from its own difference. No step of the bootstrap reads the realized $\Delta$. In the replica-only limit it reproduces Hotelling's distribution, which is checked before the bars are used.

\paragraph{The two-dimensional comparisons.} The second comparison runs a D'Agostini IBU (RooUnfold's implementation) on the two-dimensional result's own inputs and grid, at the published analysis's ten iterations, with five iterations reported beside it. The third runs the joint-test estimator on the same inputs: the two-dimensional pipeline with LightGBM's four determinism settings added to every learner it builds, refinement included, and nothing else changed. In both, each replica of the difference $\delta$ between the two results is formed on the same bootstrap draws, $C_\delta$ is the replicas' sample covariance, and the statistic is $T_\delta=\delta^{\top}C_\delta^{+}\delta$, with $C_\delta^{+}$ the pseudo-inverse truncated to the $\lfloor N/4\rfloor$ leading eigenmodes, because $N$ replicas cannot support all bins. The null is exact agreement, and it is empirical: leave-one-out over the $N$ replicas, each replica's $T$ computed about the mean of the others with $C_\delta^{+}$ from the others at the same rank. The bars are that null's 95th percentile and its maximum, so ``differ'' (above the maximum) means that a difference is detectable at this noise, not that it is large. For the IBU comparison the descriptive ratio $\rho$ is the IBU result's $\chi^2/\mathrm{ndf}$ against the published result under the published covariance divided by that of the two-dimensional result, computed on each paired replica as well as on the data."""
REPLACE = [
    ("as used in the companion journal article.", "as used in the paper."),
    ("The companion journal article distinguishes", "The paper distinguishes"),
    ("They are restated here in the terms of this note,", "They are restated here,"),
    ("the purity-subtracted 2D comparisons of this section and", "the purity-subtracted 2D comparisons of"),
    # the internal records document is not posted: point to the note section that cites it instead
    (r"(Ref.~\cite{NoteRecords2026}, \recentry{mp5-truth-axis})",
     r"(Ref.~\cite{AnalysisNote2026}, Sec.~\ref*{N-sec:eavailw-axis})"),
    (r"(Ref.~\cite{NoteRecords2026}, \recentry{coverage-fixed-truth})",
     r"(Ref.~\cite{AnalysisNote2026}, Sec.~\ref*{N-sec:coverage})"),
]

# (section title, supplement label, [(note label, [paragraph indices])], extra LaTeX appended after the copies)
PLAN = [
    ("Signal definition and event selection", "supp:selection",
     [("sec:selection", [0, 1, 2])], ""),
    ("The five observables", "supp:observables",
     [("sec:eavailw-definitions", [1, 2, 3, 4, 5, 6]), ("sec:eavail-definition", [0, 2])], ""),
    ("Binning and the sixteen reporting cells", "supp:cells",
     [("sec:method-binning", [0, 1]), ("sec:fived16-result", [0, 1])], CSV),
    ("Algorithm, background treatment and estimator configurations", "supp:estimators",
     [("sec:method-algo", [1, 2, 3]), ("sec:method-config", [5, 6, 7, 8]),
      ("app:negweight", [1, 4, 5, 36])], ""),
    ("The reported five-observable covariance", "supp:cov16",
     [("sec:fived16-cov", [0, 1, 3, 4, 5, 6, 7]), ("sec:fived16-pl", [0, 1, 3])], ""),
    ("The two-dimensional covariance", "supp:cov2d",
     [("sec:uq-combine", [0, 2, 3, 5])], ""),
    ("Joint tests: grid, support rule, statistics, calibration and conditions", "supp:joint",
     [("sec:joint5d-design", [1, 2, 3, 4]), ("sec:joint5d-calibration", [1, 2, 3]),
      ("sec:joint5d-conditions", [1, 2, 3, 4])], ""),
    ("Comparisons with binned iterative Bayesian unfolding", "supp:ibu", [], IBU),
    ("Designs of the coverage and fake-data tests", "supp:tests",
     [("sec:coverage", [0, 1, 2, 10]), ("sec:fived16-fd", [0, 3, 6])], ""),
]

blocks = []
supp_labels = set()
for title, slab, picks, extra in PLAN:
    supp_labels.add(slab)
    body = [f"\\section{{{title}}}\n\\label{{{slab}}}"]
    for nlab, idx in picks:
        f, paras = section_paragraphs(nlab)
        first = True
        for k in idx:
            p, meta = paras[k]
            if first:
                # keep the note's own label on the first copied block, so pointers to it resolve here
                if "\\label{%s}" % nlab not in p:
                    p = "\\label{%s}\n" % nlab + p
                first = False
            p = re.sub(r"\\(sub)*section\*?\{[^}]*\}\s*", "", p)
            p = re.sub(r"\\begin\{figure\}.*?\\end\{figure\}", "", p, flags=re.S).strip()
            if not p:
                continue
            carried = ("\n" + "\n".join(meta)) if meta else ""
            body.append(f"% source: {f}, note label {nlab}, paragraph {k} (verbatim, comments stripped; its search"
                        f" record or waiver carried from the note){carried}\n{p}")
    if extra:
        body.append(extra)
    blocks.append("\n\n".join(body))
tex = "\n\n".join(blocks)
for a, b in REPLACE:
    assert tex.count(a) == 1, a
    tex = tex.replace(a, b)
supp_labels |= set(re.findall(r"\\label\{([^}]+)\}", tex))
# section labels copied with their headings are gone; any \label left names an equation or table kept here

NOTE_CITE = r"Ref.~\cite{AnalysisNote2026}"
KIND = {"tab": "Table", "fig": "Fig.", "eq": "Eq.", "app": "App."}


def note_ptr(label, word=None):
    w = word or KIND.get(label.split(":")[0], "Sec.")
    if label.startswith("eq"):
        return f"{NOTE_CITE}, Eq.~(\\ref*{{N-{label}}})"
    return f"{NOTE_CITE}, {w}~\\ref*{{N-{label}}}"


def sub_ref(m):
    pre, cmd, lab = m.group(1) or "", m.group(2), m.group(3)
    if lab in supp_labels:
        if pre.strip().startswith("\\S"):
            return f"Sec.~\\{cmd}{{{lab}}}"
        return f"{pre}\\{cmd}{{{lab}}}"
    word = None
    p = pre.strip().rstrip("~").strip()
    if p in ("Table", "Tables"):
        word = "Table"
    elif p in ("Fig.", "Figs.", "Figure"):
        word = "Fig."
    elif p in ("App.", "Appendix"):
        word = "App."
    elif p in ("Eq.", "Eqs.") or cmd == "eqref":
        word = "Eq."
    elif p.startswith("\\S") or p in ("Sec.", "Secs.", "Section"):
        word = "Sec."
    return note_ptr(lab, word)


tex = re.sub(r"((?:\\S\\S|\\S|Tables?|Figs?\.|Figure|App\.|Appendix|Eqs?\.|Secs?\.|Section)~?\s*)?\\(ref|eqref)\{([^}]+)\}",
             sub_ref, tex)
open(OUT, "w", encoding="utf-8").write(
    "% supplemental_body.tex: the Supplemental Material of the methods paper (round 5 draft, 2026-11-08).\n"
    "% Seeded by docs/orchestration/state/2d-closeout/stageF/methods/round5-20261108/seed_supplemental_body.py\n"
    "% from the analysis note's text; each block names its source. Numbers print through the values*.tex macros.\n\n"
    + tex + "\n")
print(f"wrote {OUT}: {len(tex.split())} words, {len(PLAN)} sections")
