#!/usr/bin/env python3
"""Write DRAFTS.md: every reworded paragraph of the RE-2 integration, as it reads before and after, with context.

usage: make_drafts.py <worktree> [--base REF] [--out FILE]

For each changed deliverable (docs/analysis-note/*.tex against BASE), the source is cut into paragraphs (blocks
separated by blank lines) after removing LaTeX comments. A changed paragraph whose text differs only in numbers is a
mechanical value change (ledger.tsv V rows) and is skipped. Every other changed paragraph is a wording draft: it is
listed with the draft ids whose ledger F rows print inside it, the file and line where it starts now, the paragraph
before and after the edit, the paragraph before it and the paragraph after it (as they read now), and the F rows'
sources. The text is copied from the files, verbatim except for removed comments; nothing is retyped.
"""
import difflib
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE_DEFAULT = "104c69a365e7e63734062ad642924cdf6b9a96ea"
NOTE = "docs/analysis-note"
ITEMS = {  # draft item -> what it is (the work order's W1-W10; X = found in the sweep)
    "W1": "C_model beside Q_R",
    "W2": "the comparison with MINERvA's published result",
    "W3": "RO-FPS: the control no longer reproduces the 2D total",
    "W4": "the S2 diagnostic (sec_systematics.tex:101)",
    "W5": "\\fpsAbove",
    "W6": "hand sites of re2c_values_unmatched.tsv",
    "W7": "the adopted refined 2D result and the configuration labels",
    "W8": "the shift-versus-bias count",
    "W9": "the rank of the published covariance",
    "W10": "the Fig. 1 plotting code",
    "X": "sites found in the stale-value sweep (outside re2c_values_unmatched.tsv)",
    "FIG": "the refined 2D figures (installed from RE-2 part C)",
}


WAIVER = ("<!-- absence-ok: quoted deliverable text, copied verbatim for review; this record makes no absence "
          "claim of its own -->")
OPEN = [
    "**The tension-mode localization** (`sec_results.tex`, \"The four leading modes in the highest-pPar bins are all "
    "poorly determined directions (lambda/lambda_max <~ 4e-9)\" and the next clause; `app_statmethods.tex` sec:tension, "
    "\"its leading poorly determined modes in the highest-pPar bins\"). The refined `tension_report.txt` does not say "
    "which modes lie in the highest-pPar bins, and its leading modes include 3.5e-9 and 9.4e-9, so the bound cannot be "
    "checked. Hand site 4 of the 22; left as printed.",
    "**The refined 2D figures are installed** (open site 2 of the first batch, now resolved): the 16 PDFs of RE-2 part C "
    "that the note, paper and primer include (RE2-DECLARATION-C sec. 7), each checked against partc-r2/SHA256SUMS, "
    "committed under re2-integration/figs/ and pinned in make_figures.sh (ledger G rows). Not regenerated: "
    "`paper_validation_residual.pdf`, a crop of `MEFHC_5iter_pull_full.pdf` that make_figures.sh writes but no "
    "deliverable includes; it still holds the purity crop.",
    "**The label (f) is not in the registry**: `check_registry.py` LABEL_PATTERNS match (a)-(e) only, so \"(f)\" prints "
    "unchecked; `ALIASES.tsv` needs \"(f)\" and \"configuration (f)\" for `a-refined-400-31`, and the summaries of "
    "`a-refined-400-31` (\"adopted only when RE-2's rebuilt result is\") and `a-central-lgbm` need the registry "
    "owner's update. Whether to print a new letter at all is a wording decision.",
    "**The background-treatment revisit**: DECISION-20261023 (second) item 2 records the revisit \"as carried out\" with "
    "the refined treatment \"used in every dimension\"; the 5D result still uses purity, and that item leaves the "
    "reading to the director's confirmation with Joseph. The drafts drop \"the revisit ... is in progress\" and state "
    "the 2D and 5D facts only.",
    "**`app_history.tex` (records document, not posted)**: 29 values were applied to its current-value column, but those "
    "rows' superseded-by and source columns still describe Q (2026-10-17) and stageF/rebuild; striking the Q values "
    "(\\dead) and naming Q_R changes the containment check's literal set and is not done here.",
    "**Source comments** beside now-refined numbers still cite purity sources (for example paper_body.tex's \"Block "
    "values: stageF/rebuild/outputs/outA/budget_Q.json.gz (universe 5.969, ...)\"); the ledger is the refined values' "
    "provenance. Non-printing cleanup.",
    "**`VALIDATION_LEDGER.md:1614`** (row ro-fps) is outside this lane's file set and is not edited; the printed RO-FPS "
    "sentence is W3.",
    "**`\\fpsAbove`** stays defined, marked not printed: VALIDATION_LEDGER.md:1617 (\"+46% vs restricted\") names no "
    "operand, and 4.502/3.0730 - 1 = 46.50 % (RE2-PARTC-REPORT sec. 4).",
    "**The standalone MINERvA-OmniFold-Analysis-Note repository** is not synchronized (after approval, by the decision's "
    "order).",
    "**\"eightfold\"** (hand site 1) is kept for the refined 7.8x (tension_report.txt:10); \"nearly eightfold\" is the "
    "reviewer's call.",
]


def strip(text):
    out = []
    for l in text.split("\n"):
        if l.lstrip().startswith("%"):
            continue  # a whole-line comment is not part of the paragraph (and does not end it)
        out.append(re.sub(r"(?<!\\)%.*", "", l).rstrip())
    return out


def blocks(text):
    """[(first source line, paragraph text)] over the comment-stripped source; line numbers are the file's."""
    raw = text.split("\n")
    res, cur, start = [], [], None
    for i, l in enumerate(raw, 1):
        if l.lstrip().startswith("%"):
            continue
        code = re.sub(r"(?<!\\)%.*", "", l).rstrip()
        if code.strip() == "":
            if cur:
                res.append((start, "\n".join(cur))); cur = []
            continue
        if not cur:
            start = i
        cur.append(code)
    if cur:
        res.append((start, "\n".join(cur)))
    return res


def norm(t):
    return re.sub(r"\s+", " ", t.strip())


def numless(t):
    return re.sub(r"-?\d+(?:\.\d+)?(?:e-?\d+)?", "#", norm(t))


def ledger_f_rows():
    rows = []
    for l in (HERE / "ledger.tsv").read_text().splitlines():
        c = l.split("\t")
        if c and c[0] == "F" and len(c) == 7:
            rows.append(dict(id=c[1], file=c[2], new=c[3], old=c[4], src=c[5], lit=c[6]))
    return rows


def main():
    args = sys.argv[1:]
    base, out = BASE_DEFAULT, HERE / "DRAFTS.md"
    if "--base" in args:
        i = args.index("--base"); base = args[i + 1]; del args[i:i + 2]
    if "--out" in args:
        i = args.index("--out"); out = Path(args[i + 1]); del args[i:i + 2]
    wt = Path(args[0]).resolve()
    changed = subprocess.run(["git", "-C", str(wt), "diff", "--name-only", base, "--", f"{NOTE}/*.tex"],
                             capture_output=True, text=True, check=True).stdout.split()
    frows = ledger_f_rows()
    mrows = [dict(id=c[1], macro=c[2], src=c[3], key=c[4], scale=c[5], fmt=c[6])
             for c in (l.split("\t") for l in (HERE / "ledger.tsv").read_text().splitlines()) if c[0] == "M"]
    entries, skipped = [], 0
    for rel in sorted(changed):
        f = rel.split("/")[-1]
        old_text = subprocess.run(["git", "-C", str(wt), "show", f"{base}:{rel}"], capture_output=True, text=True,
                                  check=True).stdout
        new_text = (wt / rel).read_text()
        ob, nb = blocks(old_text), blocks(new_text)
        sm = difflib.SequenceMatcher(a=[norm(t) for _, t in ob], b=[norm(t) for _, t in nb], autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                continue
            # pair each new paragraph with its most similar old one in the range (ratio >= 0.4), else it is added
            used, pairs = set(), []
            for j in range(j1, j2):
                best, bi = 0.0, None
                for i in range(i1, i2):
                    if i in used:
                        continue
                    r = difflib.SequenceMatcher(a=norm(ob[i][1]), b=norm(nb[j][1]), autojunk=False).ratio()
                    if r > best:
                        best, bi = r, i
                if bi is not None and best >= 0.4:
                    used.add(bi); pairs.append((bi, j))
                else:
                    pairs.append((None, j))
            pairs += [(i, None) for i in range(i1, i2) if i not in used]
            for i, j in pairs:
                olds = [ob[i][1]] if i is not None else []
                news = [nb[j][1]] if j is not None else []
                if olds and news and numless(olds[0]) == numless(news[0]):
                    skipped += 1
                    continue
                ids = sorted({r["id"] for r in frows if r["file"] == f and any(norm(r["new"]) in norm(t) for t in news)})
                if j is not None:
                    line, before = nb[j][0], nb[j - 1][1] if j > 0 else "(start of file)"
                    after = nb[j + 1][1] if j + 1 < len(nb) else "(end of file)"
                else:
                    line, before, after = None, "(removed paragraph)", "(removed paragraph)"
                entries.append(dict(file=f, line=line, olds=olds, news=news, ids=ids, before=before, after=after))
    lines = [
        "# RE-2 integration: the wording drafts (2026-10-24, paper-tighten lane)",
        "",
        "**Status: approved by Joseph on 2026-10-24** (`DECISION-20261024-joseph-approve-integration-wording-s1-compute-preserve.md`). Each draft went to the director, then to the outside",
        "reviewer with the paragraphs around it, then to Joseph (DECISION-20261024-joseph-adopt-re2-2d-refined.md item 3).",
        "",
        "Generated by `make_drafts.py` from the branch's `docs/analysis-note/` against base",
        f"`{base}`: every changed paragraph whose words changed, not only its numbers. The text is copied",
        "from the files with LaTeX comments removed. The facts of each draft, with their sources, are the F rows of",
        "`ledger.tsv` (checked by `check_ledger.py`); the ids below are those rows' ids. Paragraphs whose only change is a",
        f"regenerated number ({skipped} of them) are the V rows of the ledger and are not repeated here.",
        "",
        "## Index",
        "",
        "| draft | item | file:line | ledger F rows |",
        "|---|---|---|---|",
    ]
    for k, e in enumerate(entries, 1):
        items = sorted({re.match(r"(W\d+|X|FIG)", i).group(1) for i in e["ids"]}) or ["(none)"]
        lines.append(f"| D{k:02d} | {', '.join(f'{i} ({ITEMS.get(i, i)})' for i in items)} | `{e['file']}:{e['line']}` | "
                     f"{', '.join(e['ids']) or 'none: see the note under the entry'} |")
    for k, e in enumerate(entries, 1):
        lines += ["", f"## D{k:02d}: `{e['file']}:{e['line']}`", ""]
        lines.append(f"**Ledger F rows:** {', '.join(e['ids']) or 'none'}.")
        if not e["ids"]:
            lines.append("No F row prints inside this paragraph; its change is a label or connective. Review it with "
                         "the neighbouring drafts.")
        def fence(text):  # a quoted source paragraph; the waiver keeps the absence-claim check off quoted text
            return ["```latex", *text.split("\n"), "```", WAIVER]
        lines += ["", "**Old:**", "", *fence("\n\n".join(e["olds"]) or "(no paragraph: added)"),
                  "", "**New:**", "", *fence("\n\n".join(e["news"]) or "(removed)"),
                  "", "**Context, the paragraph before (as it reads now):**", "", *fence(e["before"]),
                  "", "**Context, the paragraph after (as it reads now):**", "", *fence(e["after"]),
                  "", "**Sources of the facts in it:**", ""]
        for r in frows:
            if r["id"] in e["ids"]:
                lines.append(f"- {r['id']}: `{r['src']}`: \"{r['lit']}\"")
        for r in mrows:
            if any("\\" + r["macro"] + "}" in t for t in e["news"]):
                lines.append(f"- {r['id']} (macro `\\{r['macro']}`): `{r['src']}` `{r['key']}` x {r['scale']}, "
                             f"format `{r['fmt']}`")
        if not e["ids"]:
            lines.append("- (none)")
    lines += ["", "## Open sites", "",
              "Sites this batch does not resolve. Each needs a source, a product, or a decision that is not this lane's.", ""]
    lines += [f"{k}. {t}" for k, t in enumerate(OPEN, 1)]
    out.write_text("\n".join(lines) + "\n")
    print(f"DRAFTS :: {len(entries)} wording drafts, {skipped} value-only paragraphs skipped -> {out}")


main()
