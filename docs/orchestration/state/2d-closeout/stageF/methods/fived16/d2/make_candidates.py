"""Draft the d2 abstract candidates from the printed abstracts' own sentences (DECISION-20261028-joseph-final-draft-d
item 2; the director's work order of 2026-10-28).

usage: python3 -I make_candidates.py <worktree> [--show]

Every candidate is a sequence of whole sentences of the abstract as it prints at the worktree; nothing is reworded
except the one subject fix named in EDITS (the note's "Its principal result" loses its antecedent when the metatext
sentence before it leaves). So no sentence that stays is weakened, which is the guardrail. Each candidate is measured:
- words, by recount.py's rule (\\fvval resolved, whitespace tokens);
- the register study's markers (register-prd-study/tools: tex2prose.convert, qcount.markers), counting the sentences
  that carry a SCOPE, COND or STATUS marker.
The caps, from the measured corpus (d2/MEASURE.md): at most 1 marked sentence, with at most 1 marker; the paper 120-150 words; the note
110-190 words (no longer than the two long-document anchors, 184 and 190). Under
the marker caps only two whole-sentence note candidates exist (d2/MEASURE.md). METATEXT lists the phrases no candidate may carry. A candidate outside a cap stops the run."""
import json
import re
import sys
from pathlib import Path

W = Path(sys.argv[1]).resolve()
A = W / "docs/analysis-note"
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parent.parent / "register-prd-study/tools"))
import tex2prose as TP  # noqa: E402
from qcount import markers, WORD  # noqa: E402

VALS = dict(re.findall(r"\\@namedef\{fv@([^}]*)\}\{([^}]*)\}", (A / "values_fived16.tex").read_text()))
METATEXT = ["As an illustration", "This note documents", "The note also gives", "This paper", "this note", "In this note",
            "We describe", "is described", "are described"]
CAPS = {"paper": (120, 150), "note": (110, 190)}
MAX_MARKED = 1          # sentences with a SCOPE, COND or STATUS marker (corpus maximum: 1 of 60 sentences)
MAX_PER_SENTENCE = 1    # markers in any one sentence (corpus: no sentence carries two; register-prd-study REPORT.md 2.2)
EDITS = {}   # v1 changed the note's "Its principal result is"; v2 opens with the paper's sentence instead (below)
# v2 (the truth column of d2's first read): without the metatext sentence, the note's "principal result" sentence
# no longer names the measurement (MINERvA, nu_mu CC inclusive, OmniFold). Each note candidate therefore opens with
# the paper abstract's first sentence ("P0"), printed wording that names it, in place of the note's sentences 0-1.
# the candidates, as indices into the printed abstract's sentences (listed by --show)
CANDIDATES = {
    "paper": {"PA": [0, 1, 2, 3], "PB": [0, 1, 3, 5], "PC": [0, 1, 3, 6]},
    "note": {"NA": ["P0", 2, 3, 4], "ND": ["P0", 2, 4, 5]},
}


def abstract_src(name):
    t = (A / name).read_text(encoding="utf-8")
    a = t[t.index("\\begin{abstract}") + 16:t.index("\\end{abstract}")]
    a = "\n".join(l for l in a.splitlines() if not l.lstrip().startswith("%"))
    return re.sub(r"\s+", " ", a).strip()


def sentences(a):
    # split at ". " before a capital letter; the abstracts hold no abbreviation that ends a token this way
    return [s.strip() for s in re.split(r"(?<=\.)\s+(?=[A-Z])", a) if s.strip()]


def words(tex):
    return len(re.sub(r"\\fvval\{([^}]*)\}", lambda m: VALS[m.group(1)], tex).split())


def marked(tex):
    out = []
    for s in TP.sentences(TP.convert(tex)):
        kinds = [y[2] for y in markers(s) if y[2] in ("STATUS", "COND", "SCOPE")]
        if kinds:
            out.append((s[:60], kinds))
    return out


result = {}
P0 = sentences(abstract_src("main_paper.tex"))[0]
for doc, f in (("paper", "main_paper.tex"), ("note", "main_note.tex")):
    S = sentences(abstract_src(f))
    if "--show" in sys.argv:
        for i, s in enumerate(S):
            print(doc, i, words(s), "w,", "marked" if marked(s) else "-", "|", s[:90])
    result[doc] = {"sentences": S, "candidates": {}}
    for name, idx in CANDIDATES[doc].items():
        tex = " ".join(P0 if i == "P0" else S[i] for i in idx)
        for old, new in EDITS.get(doc, []):
            if tex.startswith(old):
                tex = new + tex[len(old):]
        w, m = words(tex), marked(tex)
        lo, hi = CAPS[doc]
        assert lo <= w <= hi, f"{name}: {w} words, outside {lo}-{hi}"
        assert len(m) <= MAX_MARKED, f"{name}: {len(m)} marked sentences: {m}"
        assert all(len(k) <= MAX_PER_SENTENCE for _, k in m), f"{name}: a sentence carries {m}"
        bad = [p for p in METATEXT if p in tex]
        assert not bad, f"{name}: metatext {bad}"
        dropped = [i for i in range(len(S)) if i not in idx and not (i in (0, 1) and "P0" in idx)]
        if "P0" in idx:
            dropped = [0, 1] + dropped     # the note's opening two sentences, replaced by the paper's first
        result[doc]["candidates"][name] = {"sentences": idx, "dropped": dropped, "tex": tex, "words": w,
                                           "marked": [k for _, k in m]}
        print(f"{name}: sentences {idx}, {w} words, marked {[k for _, k in m]}, drops {dropped}")
(D / "candidates.json").write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("wrote", (D / "candidates.json").relative_to(W))
