"""Round 3 of the PRD read: the move and the measurement framing. OLD->NEW pairs by sentence (paper body), the two
abstracts whole (old and new), and the title options. Printed text, values resolved, references numbered."""
import difflib, importlib.util, re, sys
S = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/796e7ecc-51d8-4fd5-a926-09de706955fd/scratchpad"
A = S + "/wt-con/docs/analysis-note"; X = S + "/xmodel/prd5d-r3"
spec = importlib.util.spec_from_file_location("cl", S + "/wt-con/docs/orchestration/state/2d-closeout/stageF/methods/fived16/check_ledger.py")
cl = importlib.util.module_from_spec(spec); spec.loader.exec_module(cl)
vals = dict(re.findall(r"\\@namedef\{fv@([^}]*)\}\{(.*)\}$", open(A + "/values_fived16.tex").read(), re.M))
refs = {k: v.replace("\\,", " ") for k, v in re.findall(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", open(A + "/main_paper.aux").read())}
nrefs = dict(re.findall(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}", open(A + "/main_note.aux").read()))
newcmd = {}
for f in ("values.tex", "values_inference.tex"):
    newcmd.update(re.findall(r"\\newcommand\{\\(\w+)\}\{([^{}]*)\}", open(A + "/" + f).read()))
def txt(s):
    s = re.sub(r"\\fvval\{([^}]*)\}", lambda m: vals[m.group(1)], s)
    s = re.sub(r"\\nsec\{([^}]*)\}", lambda m: "Ref. [14], Sec. " + nrefs.get(m.group(1), "?"), s)
    s = re.sub(r"\\napp\{([^}]*)\}", lambda m: "Ref. [14], App. " + nrefs.get(m.group(1), "?"), s)
    s = re.sub(r"\\ref\*?\{([^}]*)\}", lambda m: refs.get(m.group(1), nrefs.get(m.group(1), "?")), s)
    s = re.sub(r"\\cite\{[^}]*\}", "[ref]", s)
    s = re.sub(r"\\SI(range)?\{([^}]*)\}(\{([^}]*)\})?\{\\percent\}", lambda m: (m.group(2) + "–" + m.group(4) if m.group(1) else m.group(2)) + "%", s)
    s = re.sub(r"\\SI\{([^}]*)\}\{([^}]*)\}", r"\1 \2", s)
    s = re.sub(r"\\(\w+)\{\}", lambda m: newcmd.get(m.group(1), m.group(0)), s)
    s = re.sub(r"\\(\w+)\b", lambda m: newcmd.get(m.group(1), m.group(0)), s)
    s = re.sub(r"\\emph\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\(sub)*section\*?\{([^}]*)\}", r"[\2] ", s)
    s = re.sub(r"\\label\{[^}]*\}", "", s)
    s = re.sub(r"\\pcell\{[^}]*\}\{([^}]*)\}", r"\1", s)
    for a, b in [(r"\pT", "p_T"), (r"\pPar", "p_∥"), (r"\Eavail", "E_avail"), (r"C_{\mathrm{total}}", "C_total"), (r"C_{\mathrm{resp}}", "C_resp"),
                 (r"C_{\mathrm{model}}", "C_model"), (r"\chi^{2}", "χ²"), (r"\chi^2", "χ²"), (r"\nu_{\mu}", "ν_μ"), (r"q_{3}", "q_3"), (r"\geq", "≥"),
                 (r"\,\%", " %"), (r"\%", "%"), (r"\,", " "), ("~", " "), ("--", "–"), ("$", ""), (r"\pm", "±"), (r"\times", "×"), (r"\\", " ")]:
        s = s.replace(a, b)
    s = re.sub(r"\\includegraphics(\[[^]]*\])?\{[^}]*\}", "[figure]", s)
    s = re.sub(r"\\begin\{tabular\}\{[^}]*\}", "", s)
    s = re.sub(r"\\(begin|end)\{[^}]*\}(\[[^]]*\])?", "", s)
    s = re.sub(r"\\setlength\{[^}]*\}\{[^}]*\}", "", s)
    s = re.sub(r"\\(centering|scriptsize|footnotesize|toprule|midrule|bottomrule|noindent)\b", "", s)
    s = re.sub(r"\\caption\{", "Caption: ", s)
    for a, b in [(r"\approx", "≈"), (r"\nu", "ν"), (r"\sqrt", "√"), (r"\qquad", " "), (r"\sigma", "σ"), (r"\le", "≤"), (r"\ge", "≥"), (r"\mathrm", ""), (r"\operatorname", "")]:
        s = s.replace(a, b)
    left = re.findall(r"\\[A-Za-z]+", s)
    if left: print("  leftover commands:", sorted(set(left)))
    s = re.sub(r"\\[A-Za-z]+", "", s).replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip()
old = cl.sentences(cl.printed(open(S + "/5d/paper_body.pre-move.tex").read()))
new = cl.sentences(cl.printed(open(A + "/paper_body.tex").read()))
sm = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
pairs = []
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op == "equal": continue
    o = " ".join(old[i1:i2]); n = " ".join(new[j1:j2])
    if "FIVED16" in o + n or "tabular" in o + n and len(o + n) > 3000: pass
    pairs.append((txt(o) if o else "(nothing)", txt(n) if n else "(removed; the material is in the companion note)"))
def abst(p):
    t = open(p).read(); a = t.index("\\begin{abstract}"); b = t.index("\\end{abstract}")
    return txt("\n".join(l for l in t[a + 16:b].splitlines() if not l.lstrip().startswith("%")))
PA_old, PA_new = abst(S + "/5d/main_paper.pre-framing.tex"), abst(A + "/main_paper.tex")
NA_old, NA_new = abst(S + "/5d/main_note.pre-framing.tex"), abst(A + "/main_note.tex")
titles = ["Performance and limitations of multidimensional OmniFold unfolding with MINERvA open data (current)",
          "Simultaneous measurement of the ν_μ charged-current inclusive cross section on hydrocarbon in five observables from MINERvA open data",
          "Charged-current inclusive ν_μ cross section on hydrocarbon in muon kinematics, available energy, three-momentum transfer and hadronic invariant mass from MINERvA open data",
          "Five-dimensional ν_μ charged-current inclusive cross section measured with unbinned unfolding of MINERvA open data"]
body = "".join(f"P{i+1:02d}.\n   OLD: {o}\n   NEW: {n}\n\n" for i, (o, n) in enumerate(pairs))
doc = ("BACKGROUND. The paper is being reframed from a methods study to a measurement led by its sixteen-cell five-observable cross section, and it now presents only "
       "the two final estimators (a two-observable estimator and a joint-test estimator); earlier estimator variants and the results resting on them moved to the "
       "companion note, with pointers, except findings the paper's argument needs, which stay described in words.\n\n"
       f"PART A. The paper abstract.\nOLD ({len(PA_old.split())} words): {PA_old}\nNEW ({len(PA_new.split())} words): {PA_new}\n\n"
       f"PART B. The companion note's abstract.\nOLD ({len(NA_old.split())} words): {NA_old}\nNEW ({len(NA_new.split())} words): {NA_new}\n\n"
       "PART C. Title options for the paper:\n" + "".join(f"T{i}. {t}\n" for i, t in enumerate(titles)) + "\n"
       f"PART D. The changed passages of the paper body ({len(pairs)}), each OLD -> NEW:\n\n" + body)
assert "\\" not in doc.replace("\\n", ""), re.findall(r"\\[A-Za-z]+", doc)[:8]
open(X + "/input.txt", "w").write(doc)
print(len(pairs), "pairs;", len(doc.split()), "words; paper abstract", len(PA_old.split()), "->", len(PA_new.split()), "; note", len(NA_old.split()), "->", len(NA_new.split()))
