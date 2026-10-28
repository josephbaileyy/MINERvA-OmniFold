"""Build the d2 rater inputs, blind and in both orders, from the sources and options.py (nothing retyped).

usage: python3 -I make_battery.py <worktree> <outdir>

Battery A, the abstracts (item 2): the printed abstract and the candidates of candidates.json, under neutral labels,
plus P02 as the control (ACCEPT 3 of 3 in PRD reads r4, r5 and r6).
Battery B, the options (items 3, 4, 6 and 7): each option's forms under neutral labels, plus a register control whose
second form is colloquial by construction.
"fwd" lists each item's forms in one order and "rev" in the reverse; the KEY files map labels to forms and are not
given to any rater."""
import json
import re
import sys
from pathlib import Path

W = Path(sys.argv[1]).resolve()
O = Path(sys.argv[2])
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parent / "final-draft"))
sys.path.insert(0, str(D))
import texplain as X  # noqa: E402
import options as OP  # noqa: E402

X.init(W)
C = json.loads((D / "candidates.json").read_text())
LAB = "XYZ"


def P(tex, doc="paper"):
    return X.plain(tex, doc)


def abstract_plain(name, doc):
    t = X.src(name)
    return P(t.split("\\begin{abstract}")[1].split("\\end{abstract}")[0], doc)


def para(name, start, end, doc="paper"):
    t = X.src(name)
    i = t.index(start)
    return t[i:t.index(end, i) + len(end)]


def sub(text, pairs):
    for old, new in pairs:
        assert text.count(old) == 1, old[:50]
        text = text.replace(old, new)
    return text


# ---- battery B's forms, each as printed text ------------------------------------------------------------------------
flux_k = para("paper_body.tex", OP.FLUX["start"], OP.FLUX["end"])
flux_r = sub(flux_k, OP.FLUX["R"])
rel_k = para("app_release.tex", OP.REL9["K"], OP.REL9["end"], "note")
rel_d = rel_k.replace(OP.REL9["K"], OP.REL9["D"])
r14_k = " … ".join(k for k, _ in OP.R14["pairs"])
r14_s = " … ".join(s for _, s in OP.R14["pairs"])
for k, _ in OP.R14["pairs"]:
    assert k in X.src("app_release.tex"), f"R1-R4 base text no longer prints: {k!r}"
da_k = para("main_paper.tex", OP.DA["start"], OP.DA["end"])
h1 = para("paper_body.tex", r"Two GENIE~v3 tunes,", "so interval widths cannot be tested.")
assert OP.R11["K"] in h1 and OP.O3["K"] in X.src("paper_body.tex") and OP.DEPCAP["K"] in X.src("paper_body.tex")
ITEMS = [  # (id, question, context, {form id: printed text})
    ("B1", OP.ALIGN["q"], OP.ALIGN["context"], {k: v for k, v in OP.ALIGN["forms"].items()}),
    ("B2", OP.FLUX["q"], "Sec. V B of the paper, which compares the result with generator predictions through χ².",
     {"K": P(flux_k), "R": P(flux_r)}),
    ("B3", OP.O3["q"], "In the validation section, after the residual under a generator-sized truth change is reported.",
     {"K": P(OP.O3["K"]), "Q": P(OP.O3["Q"])}),
    ("B4", OP.REL9["q"], "The appendix describes a release package of the analysis.", {"K": P(rel_k, "note"), "D": P(rel_d, "note")}),
    ("B5", OP.R14["q"], "Four phrases of the release appendix (shown joined by …). The note reports two five-observable results.",
     {"K": P(r14_k, "note"), "S": P(r14_s, "note")}),
    ("B6", OP.DEPCAP["q"], "The last sentence of the caption of the paper's sixteen-cell result table.",
     {"K": P(OP.DEPCAP["K"]), "D": P(OP.DEPCAP["D"])}),
    ("B7", OP.DA["q"], "The paper's Data Availability section.", {"K": P(da_k), "T": P(OP.DA["T"])}),
    ("B8", OP.DEPDA["q"], "The paper's Data Availability section.", {"K": P(OP.DEPDA["K"]), "D": P(OP.DEPDA["D"])}),
    ("B9", OP.R11["q"], "A paragraph of the paper's fake-data section; the two forms differ only in a sentence after the |z| clause.",
     {"K": P(h1), "C": P(h1.replace(OP.R11["K"], OP.R11["C"]))}),
    ("B0", OP.CONTROL["q"], "A sentence of the paper's results section.", {"X": OP.CONTROL["X"], "Y": OP.CONTROL["Y"]}),
]

HEAD_B = """Do not use any tools, commands or files: everything you need is in this message. Answer directly, in text, in full.

You are an experienced copy editor and referee for Physical Review D (PRD). For each numbered item below, a manuscript on a neutrino cross-section measurement (or its companion technical note, where the item says so) could print one of the labelled forms. Choose the form a PRD referee and reader would prefer: the register, clarity and conventions of published PRD measurement papers. Do not judge whether a statement is true or whether the analysis is sound, and do not propose new wording.

Answer in exactly this format, one block per item, in the order listed:
Bn: CHOICE: <the label you choose>
RANKING: <all labels, best first>
STRENGTH: <1 slight, 2 clear, 3 strong>
REASON: <one sentence>
End with a line: END
"""
HEAD_A = """Do not use any tools, commands or files: everything you need is in this message. Answer directly, in text, in full.

You are an experienced copy editor and referee for Physical Review D (PRD). Below is the current abstract of a manuscript on a neutrino cross-section measurement, and of its companion technical note, each with candidate replacements. Choose the candidate you would print as the abstract: its length, content and register should be those typical of published PRD measurement papers (for the note: of long technical documents of the field). Do not judge whether a statement is true or whether the analysis is sound, and do not propose new wording. Item P02 is a separate sentence of the paper: rule on it as ACCEPT (print NEW), DENY (keep OLD) or SHORTEN (give a shorter form).

Answer in exactly this format:
A1 (paper): CHOICE: <label>
RANKING: <all labels, best first>
REASON: <one sentence>
A2 (note): CHOICE: <label>
RANKING: <all labels, best first>
REASON: <one sentence>
P02: VERDICT: <ACCEPT, DENY or SHORTEN>
SHORTER-FORM: <the shorter form, or ->
REASON: <one sentence>
END
"""

O.mkdir(parents=True, exist_ok=True)
p02 = re.search(r"^(P02 \(paper\)\. OLD: .*\nNEW: .*)$", (D.parent / "prd-read/r6/input.txt").read_text(), re.M).group(1)
for order in ("fwd", "rev"):
    key = {}
    # battery A
    txt = [HEAD_A]
    for item, doc, f, cands in (("A1", "paper", "main_paper.tex", C["paper"]["candidates"]),
                                ("A2", "note", "main_note.tex", C["note"]["candidates"])):
        names = list(cands)[::(1 if order == "fwd" else -1)]
        key[item] = {LAB[i]: n for i, n in enumerate(names)}
        txt.append(f"{item} ({'paper abstract' if doc == 'paper' else 'technical note abstract'}). CURRENT: {abstract_plain(f, doc)}")
        for i, n in enumerate(names):
            c = cands[n]
            txt.append(f"Candidate {LAB[i]} ({c['words']} words): {P(c['tex'], doc)}")
        txt.append("")
    txt.append(p02)
    (O / f"A-{order}.txt").write_text("\n\n".join(txt) + "\n", encoding="utf-8")
    # battery B
    txt = [HEAD_B]
    for iid, q, ctx, forms in ITEMS:
        names = list(forms)[::(1 if order == "fwd" else -1)]
        key[iid] = {LAB[i] if len(forms) <= 3 else str(i): n for i, n in enumerate(names)}
        txt.append(f"{iid}. {q} Context: {ctx}")
        for i, n in enumerate(names):
            txt.append(f"Form {LAB[i]}: {forms[n]}")
        txt.append("")
    (O / f"B-{order}.txt").write_text("\n\n".join(txt) + "\n", encoding="utf-8")
    (O / f"KEY-{order}.json").write_text(json.dumps(key, indent=1) + "\n")
print("wrote", sorted(p.name for p in O.iterdir()))
