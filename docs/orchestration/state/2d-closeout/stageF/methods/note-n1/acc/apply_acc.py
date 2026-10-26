"""Accuracy fixes (unscored): which results use the purity weight. Apply to <docs/analysis-note dir>; --check only reports."""
import sys
from pathlib import Path
D = Path(sys.argv[1]); check = "--check" in sys.argv
EDITS = {
 "sec_intro.tex": [(
  "or refined after unfolding without rerunning it. Background subtraction is the\n        exception: a per-reco-bin $(D-B)/D$ purity weight is fixed\n        \\emph{before} training (\\S\\ref{sec:method-algo}).",
  "or refined after unfolding without rerunning it. Background subtraction is\n        unbinned too in the 2D result and its covariance and in the 3D and 4D central\n        values, which use refined negative-weight subtraction (\\S\\ref{sec:method-algo}).\n        The five-dimensional central value and its covariance, and the extended-fiducial\n        value, use the binned purity weight, a per-reco-bin $(D-B)/D$ weight fixed\n        \\emph{before} training.\n        % Accuracy fix (unscored; director ruling 2026-10-26): scope of the purity weight as in sec_method.tex\n        % sec:method-algo and app_negweight.tex \"Scope of the numbers\"; the earlier text made purity the general exception.")],
 "sec_method.tex": [
  ("\\paragraph{Background subtraction (the one binned step).}\nAll selected data events enter step 1;",
   "\\paragraph{Background subtraction.}\n% Accuracy fix (unscored; director ruling 2026-10-26): the heading and the first sentence describe the binned purity\n% subtraction, which is not the treatment of every quoted result (scope at the end of this paragraph). Mechanism: the\n% drivers' --bkg-mode purity path (2d-unfolding/unfold_2d_omnifold_unbinned.py:1362-1377 and :1825-1870 @ ddf16f10; nd-unfolding/unfold_nd_omnifold_unbinned.py:619-630 and :900-1030 @ ddf16f10).\nIn the binned purity subtraction, all selected data events enter step 1;"),
  ("\\item \\textbf{Fake-free step-1 training.} Step 1 targets the purity-weighted background-subtracted data of\n        \\S\\ref{sec:method-algo}.",
   "\\item \\textbf{Fake-free step-1 training.} Step 1 targets the background-subtracted data of\n        \\S\\ref{sec:method-algo}, purity-weighted or with background simulation injected at negative weight\n        (refined to non-negative weights in the refined configurations).\n        % Accuracy fix (unscored; director ruling 2026-10-26): the list covers every production run, and the 2D result\n        % and the 3D and 4D central values use refined negative-weight subtraction (sec:method-algo). Mechanism:\n        % 2d-unfolding/unfold_2d_omnifold_unbinned.py:1362-1377 and :1825-1870 @ ddf16f10; nd-unfolding/unfold_nd_omnifold_unbinned.py:619-630 and :900-1030 @ ddf16f10.\n        % In the negative-weight modes the signal fakes are injected with the background (2d-unfolding/unfold_2d_omnifold_unbinned.py:1846-1858 @ ddf16f10)."),
 ],
 "sec_validation.tex": [(
  "split-sample width check from repeated-sampling coverage. With the MC sample,\nbinning maps and purity correction held fixed,",
  "split-sample width check from repeated-sampling coverage.\n% Accuracy fix (unscored; director ruling 2026-10-26): the 2D result now uses refined negative-weight subtraction\n% (sec:method-algo), so the condition names the background subtraction, not the purity correction.\nWith the MC sample,\nbinning maps and background subtraction held fixed,")],
 "app_negweight.tex": [
  ("Background subtraction in \\S\\ref{sec:method-algo} is the only step that uses\nanalysis binning before final histogramming.",
   "Binned purity subtraction (\\S\\ref{sec:method-algo}) is the only step that uses\nanalysis binning before final histogramming.\n% Accuracy fix (unscored; director ruling 2026-10-26): scoped to the purity method, which not every quoted result uses;\n% the negative-weight modes restrict the data to the analysis window but use no reco-bin weight (2d-unfolding/unfold_2d_omnifold_unbinned.py:1362-1377 and :1825-1870 @ ddf16f10; nd-unfolding/unfold_nd_omnifold_unbinned.py:619-630 and :900-1030 @ ddf16f10)."),
  ("Unbinned subtraction reproduces the binned correction used for the results wherever it is well determined.",
   "Unbinned subtraction reproduces the binned correction wherever it is well determined.\n% Accuracy fix (unscored; director ruling 2026-10-26): \"used for the results\" dropped; the 2D result now uses the\n% refined form (sec:negweight-footing).\n"),
  ("Binned purity remains the default for this note's reproduction measurement.\nNegative-weight injection is the validated unbinned cross-check and\n\\emph{designated} extended-fiducial baseline (\\S\\ref{sec:fps}),",
   "The 2D result and its covariance and the 3D and 4D central values use its refined form\n(\\S\\ref{sec:method-algo}); binned purity remains the treatment of the five-dimensional central\nvalue and its covariance and of the extended-fiducial value.\n% Accuracy fix (unscored; director ruling 2026-10-26): \"Binned purity remains the default for this note's reproduction\n% measurement\" was stale; scope as in sec:method-algo and \"Scope of the numbers\" above.\n% Accuracy fix ACC9 (unscored; director ruling 2026-10-26): \"the validated unbinned cross-check\" dropped. Beside the\n% scope above it read as if the 2D result's treatment were only a cross-check. Table tab:estimators-matrix (sec_method.tex)\n% gives no negative-weight configuration a cross-check role (its one cross-check, (b), is purity-based), and the drivers' --bkg-mode\n% {purity, negweight, negweight-refined} designates none (2d-unfolding/unfold_2d_omnifold_unbinned.py:1362-1377 @ ddf16f10;\n% nd-unfolding/unfold_nd_omnifold_unbinned.py:619-630 @ ddf16f10). The 2D validation stays in this paragraph's first sentence.\nNegative-weight injection is the\n\\emph{designated} extended-fiducial baseline (\\S\\ref{sec:fps}),"),
 ],
 "app_codebase.tex": [(
  "applies\n        purity-weight background subtraction (\\S\\ref{sec:method-algo}),",
  "applies\n        the background subtraction its background-mode option selects (by default the\n        purity weight; \\S\\ref{sec:method-algo}),\n        % Accuracy fix (unscored; director ruling 2026-10-26): the option is --bkg-mode {purity, negweight,\n        % negweight-refined}, default purity (2d-unfolding/unfold_2d_omnifold_unbinned.py:1362-1377 and :1825-1870 @ ddf16f10; nd-unfolding/unfold_nd_omnifold_unbinned.py:619-630 and :900-1030 @ ddf16f10);\n        % the 2D result uses the refined negative-weight mode (sec:negweight-footing).")],
}
import re
def printed(x):  # what LaTeX prints, roughly: comments removed, whitespace collapsed
    return re.sub(r"\s+", " ", re.sub(r"(?<!\\)%[^\n]*", "", x)).strip()
bad = 0
for f, pairs in EDITS.items():
    p = D / f; t = p.read_text(); expect = printed(t)
    for a, b in pairs:
        n = t.count(a)
        if n != 1: print(f"MISS {f}: {n} x {a[:70]!r}"); bad += 1; continue
        i = t.index(a) + len(a)
        # a replacement ending in a comment line must end the line, or it comments out the text after it
        if re.search(r"(?<!\\)%[^\n]*$", b) and t[i:i + 1] not in ("\n", ""): b = b + "\n"
        t = t.replace(a, b)
        pa, pb = printed(a), printed(b)
        if expect.count(pa) != 1: print(f"PRINTED-MISS {f}: {pa[:70]!r}"); bad += 1; continue
        expect = expect.replace(pa, pb)
    # guard: the printed text changes by exactly the edits' printed text, nothing else
    if printed(t) != expect:
        import difflib
        d = [l for l in difflib.ndiff(expect.split(". "), printed(t).split(". ")) if l[:1] in "+-"]
        print(f"PRINTED-DRIFT {f}:", *d[:4], sep="\n  "); bad += 1
    if not check and not bad: p.write_text(t)
print("ACC ::", "FAIL" if bad else "OK", f"({sum(len(v) for v in EDITS.values())} edits)")
sys.exit(1 if bad else 0)
