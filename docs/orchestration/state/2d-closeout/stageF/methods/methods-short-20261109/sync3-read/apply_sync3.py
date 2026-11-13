r"""Sync six Supplement paragraphs to the note's round-3 text (#952 at acf934d71), the director's ruling of 2026-11-10.
For each pair, the note paragraph (comments kept out of the printed text) replaces the Supplement's, with the note's
cross-references converted: a label the Supplement carries stays Sec.~\ref{...} / Table~\ref{...}; any other becomes
Ref.~\cite{AnalysisNote2026}, Sec./App./Table~\ref*{N-...}. The provenance comment names acf934d71 (#952)."""
import re, subprocess, sys
from pathlib import Path
wt = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(wt / "docs/orchestration/state/2d-closeout/stageF/methods/methods-short-20261109"))
import check_supp_sync as cs
REV = "acf934d71"
SP = wt / "docs/analysis-note/supplemental_body.tex"
supp = SP.read_text()
labs = set(re.findall(r"\\label\{([^}]+)\}", supp))
want = {("sec_experiment.tex", "sec:selection", 2): 1, ("sec_method.tex", "sec:method-config", 7): 3,
        ("sec_fived16.tex", "sec:fived16-cov", 3): 4, ("sec_fived16.tex", "sec:fived16-pl", 0): 5,
        ("sec_fived16.tex", "sec:fived16-pl", 3): 6, ("sec_systematics.tex", "sec:uq-combine", 0): 7}

def flat(p):
    return re.sub(r"^\\label\{[^}]*\}\s*", "", re.sub(r"\s+", " ", cs.strip(p)).strip())

def conv(t):
    def one(kind, lab):
        if lab in labs:
            return {"S": "Sec.", "App": "Sec.", "Table": "Table"}[kind] + "~\\ref{" + lab + "}"
        return "Ref.~\\cite{AnalysisNote2026}, " + {"S": "Sec.", "App": "App.", "Table": "Table"}[kind] + "~\\ref*{N-" + lab + "}"
    t = re.sub(r"\\S\\ref\{([^}]+)\}", lambda m: one("S", m.group(1)), t)
    t = re.sub(r"App\.~\\ref\{([^}]+)\}", lambda m: one("App", m.group(1)), t)
    t = re.sub(r"Table~\\ref\{([^}]+)\}", lambda m: one("Table", m.group(1)), t)
    assert "\\S\\ref" not in t and not re.search(r"(?<!\*)\\ref\{(?!(%s)\})" % "|".join(map(re.escape, labs)), t), t[:200]
    return t

lines = supp.split("\n")
done = []
for it in sorted(cs.items(supp), key=lambda x: -x["line"]):
    k = (it["file"], it["label"], it["n"])
    if k not in want:
        continue
    tgt = cs.show(wt, REV, f"docs/analysis-note/{it['file']}")
    paras = cs.note_paras(tgt, it["label"])
    q, r = cs.best(paras, it["n"], cs.norm(cs.strip(it["text"])))
    i = tgt.index("\\label{%s}" % it["label"])
    raw = [b for b in re.split(r"\n\s*\n", tgt[i:]) if flat(b) == paras[q]]
    assert len(raw) == 1, (k, len(raw))
    printed = "\n".join(l for l in raw[0].split("\n") if not l.lstrip().startswith("%"))
    notecomments = [l for l in raw[0].split("\n") if l.lstrip().startswith("%")]
    new = conv(printed.strip())
    # the Supplement's paragraph: its source comment at it["line"], then comment lines, then the body to a blank line
    s0 = it["line"] - 1
    j = s0 + 1
    while lines[j].lstrip().startswith("%"):
        j += 1
    e = j
    while e < len(lines) and lines[e].strip() and not lines[e].lstrip().startswith("%"):
        e += 1
    src = lines[s0]
    m = re.match(r"(% source: \S+, note label \S+, paragraph )\d+ \(", src)
    assert m
    lines[s0] = (f"{m.group(1)}{it['n']} (synced 2026-11-10 to the note's round-3 text at {REV} (#952), the director's ruling on check 12; "
                 f"the note's paragraph {q} there; cross-references in the Supplement's form; earlier: {src[len(m.group(0)):]}")
    extra = [c for c in notecomments if "Search:" in c or "absence-ok" in c]
    if want[k] == 7:
        extra.append("% absence-ok: as the note reports (sec_systematics.tex sec:uq-combine at acf934d71); implementation "
                     "unified_throw_cov.py; scoped to the note's statement of its unified-throw study, not a claim that a result does not exist")
    lines[j:e] = extra + new.split("\n")
    done.append((want[k], it["line"], q, round(r, 2)))
SP.write_text("\n".join(lines))
print(sorted(done))
