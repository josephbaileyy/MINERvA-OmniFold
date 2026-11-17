#!/usr/bin/env python3
r"""Report how the Supplement's note-copied paragraphs compare with their note sources (the director, 2026-11-10).

usage: check_supp_sync.py <worktree> [--note-rev REV] [--diff N]

Every Supplement paragraph under a "% source: <file>, note label <label>, paragraph <n> (<kind>...)" comment is paired
with its note source: the paragraph after \label{<label>} in docs/analysis-note/<file>, taken at the worktree and, with
--note-rev, at that git revision too (the note lane's head, for example). Paragraphs are counted from 0. Because the
copier's count can be off by one where a label sits in its own paragraph, the pair is the best match among n-2..n+2.
Cross-reference forms (the Supplement's "Ref. [note], Sec. \ref*{N-x}" against the note's "\S\ref{x}") are reduced to
one token on both sides before comparing.

It is three-way: the Supplement now and at its seed commit (SEED), and the note at the seed and at the target (REV,
else the worktree). Each paragraph gets one status:
  same          the Supplement text equals the note's, word for word after that reduction, and neither side moved;
  seed-adapted  neither side moved since the seed, but the seeded copy already differed (an adaptation at seeding);
  explained     the Supplement changed since the seed, and its comment says "restyled", "adapted" or "fixed 20..",
                each logged in ledger.md (the Supplement's style integration, the meaning check, the round-2 mapping);
  UNEXPLAINED   the Supplement changed since the seed under a comment that still says "verbatim": a stale label, or an
                unlogged edit;
  NOTE-CHANGED  the note's source paragraph changed between the seed and the target: review the Supplement copy against
                the note's new text;
  synced        the note's paragraph changed, and the Supplement has followed it (it is closer to the new note text than
                to the old);
  UNPAIRED      its source file or label is missing.
This is a report, never a failure. It prints a summary line, and with --diff N the word-level differences of up to N
flagged paragraphs.
"""
import difflib
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

NOTE = "docs/analysis-note"


def strip(t):
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", line) for line in t.split("\n"))


def note_paras(text, label):
    s = strip(text)
    i = s.find(r"\label{%s}" % label)
    if i < 0:
        return None
    out = []
    for p in re.split(r"\n\s*\n", s[i:]):
        p = re.sub(r"^\\label\{[^}]*\}\s*", "", re.sub(r"\s+", " ", p).strip())
        if p:
            out.append(p)
    return out


def norm(t):
    t = re.sub(r"Ref\.~\\cite\{AnalysisNote2026\},\s*(?:Sec|Secs|App|Fig|Figs|Table|Eq)\.~\\ref\*\{N-([^}]*)\}", r" <\1> ", t)
    t = re.sub(r"\\ref\*?\{(?:N-)?([^}]*)\}", r" <\1> ", t)
    t = re.sub(r"\\label\{[^}]*\}", "", t)
    t = re.sub(r"(\\S|\bSecs?\.~|\bApp\.~|\bFigs?\.~|\bTable~|\bEq\.~|\b[Ss]ections?~|\bappendix~|\bfigure~|\btable~)", " ", t)
    t = re.sub(r"Ref\.~\\cite\{AnalysisNote2026\}", "", t)
    return re.sub(r"\s+", " ", t).strip().lower().split()


def ratio(a, b):
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def items(supp_text):
    lines = supp_text.split("\n")
    out = []
    for i, line in enumerate(lines):
        m = re.search(r"% source: (\S+), note label (\S+), paragraph (\d+) \(([^)]*)", line)
        if not m:
            continue
        j = i + 1
        while j < len(lines) and lines[j].lstrip().startswith("%"):
            j += 1
        body = []
        while j < len(lines) and lines[j].strip() and not lines[j].lstrip().startswith("%"):
            body.append(lines[j])
            j += 1
        out.append({"line": i + 1, "file": m.group(1), "label": m.group(2), "n": int(m.group(3)), "kind": m.group(4),
                    "text": " ".join(body)})
    return out


def best(paras, n, body):
    cands = [q for q in range(max(0, n - 2), min(len(paras), n + 3))]
    if not cands:
        return None, 0.0
    q = max(cands, key=lambda k: ratio(norm(paras[k]), body))
    return q, ratio(norm(paras[q]), body)


def show(wt, rev, rel):
    r = subprocess.run(["git", "-C", str(wt), "show", f"{rev}:{rel}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


SEED = "9680db24e"   # the Supplement's seeding commit (round 5, seed_supplemental_body.py, 2026-11-08)


def run(wt, note_rev=None, ndiff=0, seed=SEED):
    """Three-way: the Supplement now and at the seed, the note at the seed and at the target (note_rev, else the
    worktree). Each difference is attributed to the side that moved."""
    wt = Path(wt)
    seed_items = {(it["file"], it["label"], it["n"]): it for it in items(show(wt, seed, f"{NOTE}/supplemental_body.tex") or "")}
    rows, flagged = [], []
    for it in items((wt / NOTE / "supplemental_body.tex").read_text()):
        key = (it["file"], it["label"], it["n"])
        tgt_text = show(wt, note_rev, f"{NOTE}/{it['file']}") if note_rev else ((wt / NOTE / it["file"]).read_text()
                                                                               if (wt / NOTE / it["file"]).exists() else None)
        seed_note = show(wt, seed, f"{NOTE}/{it['file']}")
        tp = note_paras(tgt_text, it["label"]) if tgt_text else None
        sp = note_paras(seed_note, it["label"]) if seed_note else None
        if tp is None or sp is None:
            rows.append((it, "UNPAIRED", None)); continue
        body = norm(it["text"])
        q_seed, r_copy = best(sp, it["n"], body)                       # the Supplement now against the note at the seed
        s_old = seed_items.get(key)
        supp_moved = s_old is None or norm(s_old["text"]) != body       # the Supplement changed since the seed
        q_t, r_note = best(tp, it["n"], norm(sp[q_seed]))              # the note's seed paragraph against the target
        note_moved = r_note < 1.0
        it["note_seed"], it["note_tgt"], it["supp_seed"] = sp[q_seed], tp[q_t], (s_old or {}).get("text", "")
        logged = re.search(r"restyled|adapted|fixed 20", it["kind"]) is not None
        if note_moved:   # followed when the Supplement is now closer to the note's new paragraph than to its old one
            status = "synced" if ratio(norm(tp[q_t]), body) > ratio(norm(sp[q_seed]), body) else "NOTE-CHANGED"
        elif not supp_moved:
            status = "same" if r_copy == 1.0 else "seed-adapted"
        else:
            status = "explained" if logged else "UNEXPLAINED"
        rows.append((it, status, r_copy))
        if status in ("UNEXPLAINED", "NOTE-CHANGED"):
            flagged.append((it, status))
    c = Counter(s for _, s, _ in rows)
    for it, s, r in rows:
        if s not in ("same", "seed-adapted"):
            print(f"{s:12s} supp:{it['line']:<4d} {it['file']}:{it['label']}#{it['n']} ({it['kind'][:40]})")
    for it, s in flagged[:ndiff]:
        a, b = (norm(it["note_seed"]), norm(it["note_tgt"])) if s == "NOTE-CHANGED" else (norm(it["supp_seed"]), norm(it["text"]))
        print(f"--- supp:{it['line']} " + ("the note, seed -> target" if s == "NOTE-CHANGED" else "the Supplement, seed -> now"))
        for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if op != "equal":
                print(f"    {op}: [{' '.join(a[i1:i2])[:150]}] -> [{' '.join(b[j1:j2])[:150]}]")
    print(f"SUPP-SYNC :: {len(rows)} note-copied paragraphs against the note at {note_rev or 'the worktree'} (seed {seed}): "
          + ", ".join(f"{k} {v}" for k, v in sorted(c.items())) + " (report only)")
    return rows


if __name__ == "__main__":
    a = sys.argv[1:]
    rev = a[a.index("--note-rev") + 1] if "--note-rev" in a else None
    nd = int(a[a.index("--diff") + 1]) if "--diff" in a else 0
    run(a[0], rev, nd)
