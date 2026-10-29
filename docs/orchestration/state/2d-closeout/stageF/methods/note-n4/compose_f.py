#!/usr/bin/env python3
"""Batch F of note round n4: the front-matter fold (outline sec. 1; director's rulings 1 and 2, 2026-10-28).

usage: compose_f.py <worktree> [--check]

The fold is composed from the sources at PRE_F (the branch after batch C). Every sentence it keeps is cut out of
those sources by its first and last words (K), and each cut must match exactly once, so nothing kept is retyped. Only
the connecting text below is new. --check recomposes and exits 0 only if the tree already holds the result.

What it writes:
- sec_execsummary.tex: one page. The framing paragraph; one paragraph per result, each pointing to its body home;
  the one list of principal limitations, which is sec_summary.tex's list moved here. The frozen 2D sentence
  (check_ledger.FROZEN[2]) is the list's 2D sentence. The readiness sentence (FROZEN[6]) moves verbatim from the
  status table into the 2D paragraph (ruling 2).
- result_status_rows.tex: deleted, together with the status table.
- sec_summary.tex: the conclusions the ES does not state; the limitations paragraph becomes a pointer, and keeps
  the frozen sentence FROZEN[3] (ruling 2's recorded exception). Outlook and "Reusing" are unchanged.
- sec_3d.tex: the Valencia 2p2h citations, which only the ES carried, move to the model's body home.
- sec_intro.tex: Scope keeps the positive scope and points to the list; the Topic->Section table is cut; the
  companion-article sentence closes "Analysis strategy"."""
import subprocess
import sys
from pathlib import Path

PRE_F = "a2e89c5f"
A = "docs/analysis-note/"


def show(wt, name):
    return subprocess.run(["git", "-C", str(wt), "show", f"{PRE_F}:{A}{name}"], capture_output=True, text=True,
                          check=True).stdout


def K(src, start, end):
    """The exact source text from `start` through `end`, which must occur once, inside one source line."""
    i = src.find(start)
    assert i >= 0 and src.find(start, i + 1) < 0, f"start not found once: {start[:60]!r}"
    j = src.find(end, i)
    assert j >= 0, f"end not found after start: {end[:60]!r}"
    out = src[i:j + len(end)]
    assert "\n" not in out, f"cut spans a line break: {start[:60]!r}"
    return out


def line_with(src, start):
    ls = [l for l in src.splitlines() if l.startswith(start)]
    assert len(ls) == 1, (start, len(ls))
    return ls[0]


def compose(wt):
    es, su, intro, rs = (show(wt, f) for f in ("sec_execsummary.tex", "sec_summary.tex", "sec_intro.tex",
                                                  "result_status_rows.tex"))
    # --- kept sentences, cut from PRE_F ---
    frame = line_with(es, "We apply \\emph{unbinned machine-learning unfolding}")
    repro_head = K(es, "Unbinned $d^{2}\\sigma/(d\\pT\\,d\\pPar)$ reproduces", "with a correlated shape difference.")
    ready = K(rs, "Whether it is ready for publication", "has not been established.")
    repro_uq = K(es, "A separately constructed uncertainty is comparable", "against \\SI{\\uqPaperIntegral}{\\percent}.")
    repro_cm = K(es, "A generator-shape model-dependence component, reported beside", "(\\S\\ref{sec:uq-2d-scope}).")
    repro_lgbm = K(es, "LightGBM was chosen over the exact-split estimator", "(\\S\\ref{sec:method-config}).")
    repro_chi = K(es, "Against the full published covariance,", "(\\S\\ref{sec:results-tension}).")
    nd_marg = K(es, "In configuration (a), the 4D and 5D marginal-normalization", "a comparison across configurations (\\S\\ref{sec:3d}).")
    nd_bump = K(es, "The 3D and 4D injected-bump closures, of configuration (a)", "close $q_{3}$ to \\SI{1.1}{\\percent}.")
    nd_closure = K(es, "Neither closure is graded", "Table~\\ref{tab:closure-map}).")
    low = K(es, "All four truth-level generators, GENIE~", "\\cite{MINERvA:2016lowrecoil,MINERvA:2022incl}.")
    high1 = K(es, "In cell-integrated terms, most of the positive difference", "much of it at $W\\ge\\SI{1.8}{GeV}$.")
    high2 = K(es, "The high-$\\Eavail$, high-$W$ region carries the largest regularization bias", "measured in \\S\\ref{sec:5d}.")
    high_ratio = K(es, "In ratio, the excess also extends to low $W$.", "low $W$.")
    high3 = K(es, "The four external generators also fall below the data in this corner", "(\\S\\ref{sec:eavailw-band}).")
    high4 = K(es, "The NuWro and GiBUU ratios contain an uncorrected carbon-versus-CH target difference (\\S", "eavailw-generators}).")
    jt1 = K(es, "Calibrated tests of hybrid null hypotheses for five predictions", "reject all ten under six stated conditions.")
    jt_fwer = K(es, "The family-wise error rate is controlled at 5\\%", "(\\S\\ref{sec:joint5d-fwer}).")
    jt_excl = K(es, "The rejections are not physical exclusions", "(\\S\\ref{sec:joint5d-projections}).")
    jt_rec1 = K(es, "The pseudo-experiments lost to time limits", "has been observed.")
    jt_rec2 = K(es, "No recovered draw changes a decision", "(\\S\\ref{sec:joint5d-lost}).")
    jt_ch1 = K(es, "Correcting the carbon-only NuWro and GiBUU predictions", "moves both toward the data.")
    jt_ch2 = K(es, "In this descriptive re-evaluation, NuWro's total-test rejection", "(\\S\\ref{sec:joint5d-ch}).")
    meth = K(es, "The standard covariance sums single-source systematic matrices", "(\\S\\ref{sec:uq-combine}).")
    fps = K(es, "Removing truth-muon cuts, with the fiducial volume", "which form tier~2 (\\S\\ref{sec:fps}).")
    nd_w = K(es, "Reconstructed $W$ is fixed by $(\\pT,\\pPar,q_{3})$", "(\\S\\ref{sec:eavailw-definitions}).")
    meth1 = K(es, "The standard covariance sums single-source systematic matrices", "cross-source response terms.")
    es_lim = line_with(es, "\\paragraph{Principal limitations:}")
    es_2d = K(es, "The quoted 2D statistical block has had no coverage test;", "\\S\\ref{sec:coverage}).")
    lim_su = line_with(su, "\\paragraph{Principal limitations.}")
    lim_rest = K(lim_su, "The generator comparisons of \\S\\S", "(\\S\\ref{sec:joint5d-response}).")
    purity = K(su, "Pseudo-experiments with backgrounds reveal a purity-subtraction bias", "no uncertainty quoted for it includes the bias.")
    fd16_abs = K(show(wt, "main_note.tex"), "reported in sixteen cells with a covariance", "is \\fvval{sigmed-C_total_resp}\\%.")
    fd16_gen = K(show(wt, "main_note.tex"), "Three external generator predictions compared on all sixteen cells", "\\fvval{g-gibuu-total-chi2int}.")
    es_search_repro = line_with(es, "  % Search: source of the shape difference;")
    es_search_3d = line_with(es, "  % Search: threshold near 3D, 4D, closure,")
    es_lim_comments = "\n".join(l for l in es.split("\\paragraph{Principal limitations:}")[1].splitlines()[1:] if l.startswith("%"))
    # --- the new executive summary ---
    new_es = "\n".join([
        "\\section*{Executive summary}",
        "\\addcontentsline{toc}{section}{Executive summary}",
        "\\label{sec:execsummary}",
        "",
        "% Note round n4 (DECISION-20261028-joseph-protections-n4-release-retrospective.md item 2; note-n4/outline.md, "
        "rulings 1-2): folded to about a page as the note's single results summary, with the one list of principal "
        "limitations, moved here from sec_summary.tex. Each result points to its body home, where every fact the fold "
        "removed still prints (note-n4/ledger.md, batch F); the status table and its rows file are cut. The sentences "
        "frozen until Joseph's inventory decision (outline sec. 4) are kept byte-identical. The earlier text and its "
        "source comments are in git history at 371cccec.",
        frame,
        "",
        "\\paragraph{Results:}",
        "% Ruling of 2026-10-28 on the length conflict: (b)+(c). Each result is its headline sentence with a pointer to its "
        "body home; the limitations paragraph is the ES's pointer list as it stood at the base, with the frozen 2D "
        "sentence. Every limitation prints at its body home (note-n4/ledger.md, batch F).",
        "\\begin{itemize}[itemsep=2pt, parsep=0pt, topsep=2pt]",
        "  \\item \\textbf{Sixteen-cell five-observable cross section.} The cross section in $\\pT$, $\\pPar$, $\\Eavail$, $q_{3}$ and $W$ is "
        + fd16_abs + " " + fd16_gen.replace("\\fvval{g-gibuu-total-chi2int}.", "\\fvval{g-gibuu-total-chi2int} (\\S\\ref{sec:fived16-gen})."),
        "  \\item \\textbf{Reproduction.} " + repro_head.replace("shape difference.", "shape difference (\\S\\ref{sec:results}).") + " " + ready + " " + repro_lgbm,
        "  \\item \\textbf{Unbinned 3D/4D/5D central values.} Adding $\\Eavail$, $q_{3}$ and $W$ gives simultaneous unfolds, "
        "and the 3D, 4D and configuration-(a) five-dimensional unfolds are reported as central values. " + nd_marg + " " + nd_w,
        "  \\item \\textbf{Descriptive comparisons of the central values.} "
        + " ".join([low.replace("MINERvA:2022incl}.", "MINERvA:2022incl} (\\S\\ref{sec:3d-models}, \\S\\ref{sec:3d-2p2h})."),
                    high1.replace("much of it at $W\\ge\\SI{1.8}{GeV}$.", "much of it at $W\\ge\\SI{1.8}{GeV}$ (\\S\\ref{sec:eavailw-map})."), high2, high3]),
        "  \\item \\textbf{Application: joint five-dimensional generator tests.} "
        + " ".join([jt1.replace("six stated conditions.", "six stated conditions (\\S\\ref{sec:joint5d-conditions})."),
                    jt_excl, jt_rec1, jt_rec2, jt_ch1, jt_ch2]),
        "  \\item \\textbf{A methodological finding.} " + meth,
        "  \\item \\textbf{A preliminary extended-fiducial study.} Removing truth-muon cuts, with the fiducial volume and "
        "MINOS-based selection kept, puts about \\SI{6}{\\percent} of the scalar 2D rate in newly acceptance-supported cells "
        "(part of tier~1) and about \\SI{28}{\\percent} in low- or zero-efficiency cells (tier~2; \\S\\ref{sec:fps}).",
        "\\end{itemize}",
        "",
        es_lim.replace("\\paragraph{Principal limitations:}", "\\paragraph{Principal limitations:}\\label{sec:execsummary-limitations}")
        .replace(" The others are stated with their results:", " No result's intervals have validated coverage (two dimensions: \\S\\ref{sec:uq-2d-scope}; "
                 "five dimensions: \\S\\ref{sec:coverage-5d}; the sixteen cells: \\S\\ref{sec:fived16-fd}). The others are stated with their results:"),
        es_lim_comments,
        "",
    ])
    # --- sec_summary.tex ---
    su_l4 = line_with(su, "\\paragraph{Summary.}")
    bullets_start = su.index(su_l4)
    items_end = su.index("\\end{itemize}", bullets_start) + len("\\end{itemize}")
    old_block = su[bullets_start:items_end]
    b3 = line_with(su, "  \\item Pseudo-experiments with backgrounds reveal")
    b3_rest = K(b3, "The refined negative-weight subtraction, which the sixteen-cell result uses", "(App.~\\ref{app:negweight}).")
    b4 = line_with(su, "  \\item As an application, joint tests calibrated")
    b4_design = K(b4, "Their design was fixed before any production pseudo-experiment", "(\\S\\ref{sec:joint5d-frozen}).")
    b4_tests = K(b4, "The tests are not physical exclusions, recover established discrepancies", "beyond matched coarse projections.")
    b4_search = line_with(su, "        % Search: power comparison;")
    new_block = "\n".join([
        "\\paragraph{Summary.} The executive summary (p.~\\pageref{sec:execsummary}) gives each result with its scope and "
        "lists the principal limitations. Two further conclusions follow from the body.",
        "% Note round n4, P2N revision (ruling 3: the wording revised once inside the structure; note-n4/REPORT.md).",
        "% Note round n4 (ruling 1): only the conclusions the executive summary does not state; the rest of the former",
        "% bullets print there or at their body homes (note-n4/ledger.md, batch F). Earlier text: git history, 371cccec.",
        "\\begin{itemize}[itemsep=2pt]",
        "  \\item " + b3_rest.replace("largely removes it.", "largely removes the bias that purity-based background subtraction leaves in the highest-$W$ cells (\\S\\ref{sec:val-negweight})."),
        "  \\item " + b4_design.replace("Their design", "The joint tests' design") + " "
        + b4_tests.replace("The tests are not physical exclusions, recover established discrepancies, and show",
                           "The tests recover established discrepancies and show")[:-1] + " (\\S\\ref{sec:joint5d}).",
        b4_search,
        "\\end{itemize}",
    ])
    assert su.count(old_block) == 1
    su2 = su.replace(old_block, new_block)
    su_f4 = K(lim_su, "The quoted two-dimensional statistical block has had no coverage test", "\\S\\ref{sec:coverage}).")
    su2 = su2.replace(lim_su, "\\paragraph{Principal limitations.} The executive summary lists the principal limitations "
                      "(p.~\\pageref{sec:execsummary-limitations}), each with the section that states it. " + su_f4)
    su2 = su2.replace(su2[su2.index("% Register round n1 (S2; caveat-study R-N1;"):su2.index("\\paragraph{Outlook.}")],
                      "% Note round n4 (ruling 1): the list moved to the executive summary, with its source comments. The\n"
                      "% frozen 2D sentence stays here until Joseph's inventory decision (ruling 2, the recorded exception).\n"
                      + line_with(su, "% Search: held-out simulation;") + "\n\n")
    # --- sec_intro.tex ---
    scope = line_with(intro, "\\paragraph{Scope.}")
    sc1 = K(scope, "\\paragraph{Scope.} The results hold for one implementation", "observables and deformations tested.")
    sc_tail = K(scope, "The generator tests of \\S\\ref{sec:joint5d} evaluate hybrid", "No result in this note depends on it.")
    intro2 = intro.replace(scope, sc1 + " The principal limitations are listed in the executive summary "
                           "(p.~\\pageref{sec:execsummary-limitations}). " + sc_tail)
    strat = line_with(intro, "\\paragraph{Analysis strategy.}")
    companion = K(line_with(intro, "\\paragraph{Roadmap.}"), "The companion journal article is a shortened account", "the detail it omits.")
    intro2 = intro2.replace(strat, strat + " " + companion.replace("these sections give", "this note gives"))
    r0 = intro2.index("\\paragraph{Roadmap.}")
    r1 = intro2.index("\\end{center}", r0) + len("\\end{center}")
    intro2 = intro2[:r0] + ("% Note round n4 (ruling 1): the Roadmap paragraph and its Topic -> Section table are cut; the table "
                            "held pointers and one fact, \"protocol implemented, not yet run\", which prints in "
                            "app_response_mismatch.tex and sec_validation.tex. The companion-article sentence closes "
                            "\"Analysis strategy\". Earlier text: git history, 371cccec.") + intro2[r1:]
    td = show(wt, "sec_3d.tex")
    nsv = "The Nieves--Simo--Vacas MEC channel is present in the splines"
    assert td.count(nsv) == 1
    td2 = td.replace(nsv, "The Nieves--Simo--Vacas MEC channel~\\cite{Nieves:2011pp,Gran:2013kda} is present in the splines")
    # Two limitations that only the old ES (the 2D shape difference's source) and the old §12 list and §1 Scope (the
    # sixteen-cell coverage) stated get body homes, in printed wording: the paper's sentence (paper_body.tex) and the
    # note abstract's (main_note.tex), each with the Search line that supports it at its first home.
    rs_ = show(wt, "sec_results.tex")
    band = "and LightGBM with seeds 1--10 gives 2.64--2.75."
    assert rs_.count(band) == 1
    rs2 = rs_.replace(band, band + " Beyond this methodological band, the source of the shape difference has not been identified.", 1)
    tl = [l for l in rs2.splitlines() if band in l][0]
    rs2 = rs2.replace(tl, tl + "\n% Search: source of the shape difference; source has not been identified (note sources: this sentence, "
                      "paper_body.tex sec:repro2d and primer_body.tex; App. sec:tension attributes about one chi-square unit to the "
                      "estimator's implicit regularization, the band named here) @ 03e98d3d. Note round n4: the home of the former "
                      "executive-summary sentence (note-n4/ledger.md, batch F).")
    fv = show(wt, "sec_fived16.tex")
    bt = "and the detector response is not probed."
    line = [l for l in fv.splitlines() if "This is a bias test, not a coverage test" in l]
    assert len(line) == 1 and line[0].count(bt) == 1
    ab = show(wt, "main_note.tex")
    cov = K(ab, "The coverage of the result's intervals has not been validated;", "has not been validated;")[:-1] + "."
    abs_search = line_with(ab, "% Search: coverage of the sixteen-cell intervals;")
    fv2 = fv.replace(line[0], line[0].replace(bt, bt + " " + cov) + "\n" + abs_search + " Note round n4: the body home of the abstract's sentence (note-n4/ledger.md, batch F).")
    return {"sec_results.tex": rs2, "sec_fived16.tex": fv2, "sec_3d.tex": td2, "sec_execsummary.tex": new_es, "sec_summary.tex": su2, "sec_intro.tex": intro2, "result_status_rows.tex": None}


def main():
    wt = Path(sys.argv[1]).resolve()
    D = wt / A
    out = compose(wt)
    if "--check" in sys.argv:
        bad = [f for f, t in out.items() if (t is None and (D / f).exists()) or (t is not None and (D / f).read_text() != t)]
        print("compose_f --check:", "OK" if not bad else f"DIFFERS {bad}")
        return 1 if bad else 0
    for f, t in out.items():
        if t is None:
            (D / f).unlink(missing_ok=True)
        else:
            (D / f).write_text(t)
    print("compose_f: wrote", ", ".join(f for f, t in out.items() if t is not None), "; deleted",
          ", ".join(f for f, t in out.items() if t is None))
    return 0


if __name__ == "__main__":
    sys.exit(main())
