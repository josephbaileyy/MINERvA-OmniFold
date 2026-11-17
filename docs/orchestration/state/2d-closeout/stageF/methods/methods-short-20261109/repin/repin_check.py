"""Count every new source in repin_list.tsv at a #977 head (argv[1]). Run from any checkout of the repo. Writes nothing.
LaTeX comments (an unescaped % to the end of the line) are stripped and whitespace runs collapse, as the re-pinned build
will read. resource rows must count 1; fd16row rows must each be a row of tab:fd16 with \\newline read as a space; keys
rows must each be printed (\\fvval{key} at least once); term rows (old|new) need new printed and old absent;
drop and code rows are listed only. Exit 1 if any resource,
fd16row, keys or term check fails, or any guard (GEN16, MACRO, PENDING, CODEMAP, LABELMAP) does.
argv[2], optional: a label map to check in place of the head's committed label-map.tsv (a what-if or a plant)."""
import hashlib, os, re, subprocess, sys, tempfile

N = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = {"paper": "paper_body.tex", "supplement": "supplemental_body.tex", "abstract": "main_paper.tex"}


def text(doc):
    raw = subprocess.run(["git", "show", f"{N}:docs/analysis-note/{DOCS[doc]}"], capture_output=True, text=True,
                         check=True).stdout
    return re.sub(r"\s+", " ", re.sub(r"(?m)(?<!\\)%.*$", "", raw)).strip()


norm = lambda s: re.sub(r"\s+", " ", s).strip()
cache, bad = {}, 0
rows = [l.split("\t") for l in open(os.path.join(HERE, "repin_list.tsv")).read().splitlines()
        if l and not l.startswith("#") and not l.startswith("id\t")]
print(f"#977 head {N}; {len(rows)} rows")
for rid, ruled, resp, sites, action, doc, quote, note in rows:
    if action in ("resource", "code") and doc in DOCS and quote != "-":
        t = cache.setdefault(doc, text(doc))
        c = t.count(norm(quote))
        ok = c == 1
        bad += (not ok) and action == "resource"
        print(f"{'OK ' if ok else 'BAD'} {rid:6} {action:8} {doc:10} count={c}  {quote[:70]}")
    elif action == "fd16row":
        t = cache.setdefault(doc, text(doc))
        i = t.find(r"\label{tab:fd16}")
        b, e = t.rfind(r"\begin{table", 0, i), t.find(r"\end{table", i)
        tab = re.sub(r"\\newline\s*", " ", t[b:e]) if i >= 0 else ""
        for q in quote.split("|"):
            ok = bool(re.search(r"(^|\\\\|\\midrule|\\toprule)\s*" + re.escape(q) + r"\s*&", tab))
            bad += not ok
            print(f"{'OK ' if ok else 'BAD'} {rid:6} fd16row  {doc:10} {q}")
    elif action == "term":
        t = cache.setdefault(doc, text(doc))
        old, new = quote.split("|")
        co, cn = t.lower().count(old.lower()), t.lower().count(new.lower())
        ok = cn >= 1 and co == 0
        bad += not ok
        print(f"{'OK ' if ok else 'BAD'} {rid:6} term     {doc:10} old={co} new={cn}  {old} -> {new}")
    elif action == "keys":
        t = cache.setdefault(doc, text(doc))
        for k in quote.split("|"):
            c = t.count("\\fvval{%s}" % k)
            ok = c >= 1
            bad += not ok
            print(f"{'OK ' if ok else 'BAD'} {rid:6} keys     {doc:10} printed={c}  \\fvval{{{k}}}")
    else:
        print(f"--  {rid:6} {action:8} {sites}  {note[:80]}")
# The director's standing order: if tab:gen16 is touched at any head, STOP to the director. #981 binds tab-gen16.csv to
# that label. The table block (from \begin{table to \end{table around the label, raw text) is pinned by sha256.
GEN16_SHA = "d41ae276e681fc6477c61ee7ec106ce28f132449f6a01b55ea3dbfde5be2a51d"   # re-pinned at ed2b57a3c (director, 11-16):
# 697699e0d changed only \scriptsize to \small and added a comment; rows, values, caption, label byte-identical.
# Before: 65b02f09daacba48..., unchanged from 1ccb08c29 to 0cb2bf172.
raw = subprocess.run(["git", "show", f"{N}:docs/analysis-note/{DOCS['supplement']}"], capture_output=True, text=True,
                     check=True).stdout
i = raw.find(r"\label{tab:gen16}")
blk = raw[raw.rfind(r"\begin{table", 0, i):raw.find(r"\end{table", i)] if i >= 0 else ""
sha = hashlib.sha256(blk.encode()).hexdigest()
ok = raw.count(r"\label{tab:gen16}") == 1 and sha == GEN16_SHA
bad += not ok
print(f"{'OK ' if ok else 'BAD'} GEN16  labels={raw.count(chr(92) + 'label{tab:gen16}')} block_sha={sha[:16]}"
      + ("" if ok else "  tab:gen16 CHANGED: STOP to the director and re-measure"))
# #981 checks these values.tex macros against its records (c.macro and BENCH's ("macro", m) at 91f9cb615). A macro
# check only binds if the paper still prints the macro: if the paper switches to a key, values.tex can keep the old
# value and #981's check passes on a number nothing prints. Each macro must be printed (\m not followed by a letter,
# after comment stripping, in the paper, Supplement and abstract together), or its re-sourced key (RESOURCED, with
# its row) must be printed as \fvval{key}.
MACROS = ["chiPaper", "fluxBand", "pullRMS", "ratioTot", "sigTwoD", "uqIntegral", "uqMedian"]
RESOURCED = {"uqMedian": ("q2d-sigma-med", "RP42"), "uqIntegral": ("q2d-sigma-int", "RP42"),
             "fluxBand": ("q2d-fluxband", "RP42")}
alltext = " ".join(cache.setdefault(d, text(d)) for d in DOCS)
for m in MACROS:
    n = len(re.findall(r"\\" + m + r"(?![A-Za-z])", alltext))
    alt, row = RESOURCED.get(m, (None, None))
    k = alltext.count(r"\fvval{" + alt + "}") if alt else 0
    ok = n >= 1 or k >= 1
    bad += not ok
    print(f"{'OK ' if ok else 'BAD'} MACRO  \\{m} printed {n}" + (f"; \\fvval{{{alt}}} printed {k} ({row})" if alt else "")
          + ("" if ok else "  #981 checks this macro but nothing prints it: re-source the check to the printed key"))
# #981 (91f9cb615) hard-codes its pending results (build_package.py PENDING: FD-PRR, LL5D, V-HALF) and writes a
# pending/<name>.txt "Not yet available" file for each, whatever the paper's producer says. Each maps to a producer
# group whose state values_fived16.tex records (\@namedef{fvg@<group>}{PENDING|FILLED}). A FILLED group that #981
# still marks pending would ship a stale "not yet available" note, and no build check sees it. Each FILLED group must
# have the re-pin row that fills it (FILLS).
PENDING_MAP = {"FD-PRR": "prr", "LL5D": "ll5d", "V-HALF": "vhalf"}
FILLS = {"FD-PRR": "RP43", "LL5D": "RP43", "V-HALF": "RP43"}
vf = subprocess.run(["git", "show", f"{N}:docs/analysis-note/values_fived16.tex"], capture_output=True, text=True,
                    check=True).stdout
for name, grp in PENDING_MAP.items():
    m = re.findall(r"\\@namedef\{fvg@" + grp + r"\}\{([A-Z]+)\}", vf)
    state = m[0] if len(m) == 1 else "UNKNOWN (%d definitions)" % len(m)
    ok = state == "PENDING" or (state == "FILLED" and name in FILLS)
    bad += not ok
    print(f"{'OK ' if ok else 'BAD'} PENDING #981 {name} -> group {grp}: {state}"
          + (f" ({FILLS[name]} fills it at the re-pin)" if state == "FILLED" and name in FILLS else "")
          + ("" if ok else "  #981 would ship a stale pending note: add the row that fills it"))
# RP44: the code-location map #981's README gains (codemap.tsv). Each entry's file must have its pinned sha256 at its
# commit, and its anchor must lie inside its cited lines. The Supplement's tab:codemap block is pinned by sha256 while
# it exists: a change means RP44's map must be re-checked against it; once journal-editor cuts it, RP44 is the source.
CODEMAP_TABLE_SHA = "0b9ab61090d432517a6dee76a94f04b8d4f4cedcf8d22e4c90c929cbf8f81be6"   # at 1515a6abe (journal-editor shortened the caption; the 13 rows equal f03dbd758's, 11de5b17)
cm = [l.split("\t") for l in open(os.path.join(HERE, "codemap.tsv")).read().splitlines()
      if l and not l.startswith("#") and not l.startswith("step\t")]
nbad = 0
for step, path, commit, lines, want, anchor in cm:
    b = subprocess.run(["git", "show", f"{commit}:{path}"], capture_output=True, check=True).stdout
    a, z = map(int, lines.split("-"))
    seg = b"\n".join(b.split(b"\n")[a - 1:z]).decode()
    ok = hashlib.sha256(b).hexdigest() == want and anchor in seg
    nbad += not ok
    if not ok:
        print(f"BAD CODEMAP {path}:{lines} @{commit} ({step}): sha or anchor differs")
bad += nbad
print(f"{'OK ' if not nbad else 'BAD'} CODEMAP {len(cm)} entries: every file at its pinned sha256 and every anchor in its lines")
i = raw.find(r"\label{tab:codemap}")
if i < 0:
    print("OK  CODEMAP tab:codemap is cut from the Supplement; RP44's map is the source")
else:
    blk = raw[raw.rfind(r"\begin{table", 0, i):raw.find(r"\end{table", i)]
    tsha = hashlib.sha256(blk.encode()).hexdigest()
    ok = raw.count(r"\label{tab:codemap}") == 1 and tsha == CODEMAP_TABLE_SHA
    bad += not ok
    print(f"{'OK ' if ok else 'BAD'} CODEMAP tab:codemap block_sha={tsha[:16]}"
          + ("" if ok else "  tab:codemap CHANGED: re-check RP44's map against it"))
# RP45: #981's README prints each file's table, figure or section number from methods-short-20261109/label-map.tsv at
# PAPER_REF, and its build checks only that each label exists. The map must equal what make_label_map.py writes from a
# fresh build of the head's paper and Supplement (git archive of docs/analysis-note, latexmk), or #981 prints stale
# numbers. Each label #981 names (its build at PKG_REF) that differs is listed; any other differing row is counted.
PKG_REF = "91f9cb615"
LM = "docs/orchestration/state/2d-closeout/stageF/methods/methods-short-20261109/label-map.tsv"
MLM = "docs/orchestration/state/2d-closeout/stageF/methods/methods-short-20261109/make_label_map.py"
bp = subprocess.run(["git", "show", f"{PKG_REF}:docs/orchestration/state/2d-closeout/stageF/methods/result-package-20261109/"
                     "build_package.py"], capture_output=True, text=True, check=True).stdout
used = sorted(set(re.findall(r'"((?:sec|tab|fig|eq|app|supp):[A-Za-z0-9-]+)"', bp)))
committed = (open(sys.argv[2]).read() if len(sys.argv) > 2 else
             subprocess.run(["git", "show", f"{N}:{LM}"], capture_output=True, text=True, check=True).stdout)
with tempfile.TemporaryDirectory() as td:
    arc = subprocess.run(["git", "archive", N, "docs/analysis-note", MLM], capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", td], input=arc, check=True)
    an = os.path.join(td, "docs/analysis-note")
    rcs = [subprocess.run(["latexmk", "-pdf", "-g", "-interaction=nonstopmode", "-halt-on-error", f], cwd=an,
                          capture_output=True).returncode for f in ("main_paper.tex", "main_supplement.tex")]
    fresh = None
    if rcs == [0, 0]:
        out = os.path.join(td, "label-map.tsv")
        subprocess.run([sys.executable, "-B", os.path.join(td, MLM), os.path.join(an, "main_paper.aux"),
                        os.path.join(an, "main_supplement.aux"), out], capture_output=True, check=True)
        fresh = open(out).read()
if fresh is None:
    bad += 1
    print(f"BAD LABELMAP the head's paper or Supplement did not build (latexmk rc {rcs}): the map cannot be checked")
else:
    rd = lambda t: {r.split("\t")[0]: tuple(r.split("\t")[1:]) for r in t.splitlines()[1:] if r}
    cm_, fr_ = rd(committed), rd(fresh)
    nd = [a for a in used if cm_.get(a) != fr_.get(a)]
    other = [a for a in set(cm_) | set(fr_) if a not in used and cm_.get(a) != fr_.get(a)]
    for a in nd:
        print(f"BAD LABELMAP {a}: the map has {cm_.get(a)}, a fresh build prints {fr_.get(a)}")
    bad += bool(nd or other)
    print(f"{'OK ' if not (nd or other) else 'BAD'} LABELMAP {len(used)} labels #981 names, {len(nd)} stale; "
          f"{len(other)} other rows differ ({len(cm_)} in the map, {len(fr_)} in a fresh build)"
          + ("" if not (nd or other) else "  regenerate label-map.tsv at the head (make_label_map.py)"))
print("REPIN-CHECK", "PASS" if not bad else f"FAIL ({bad})")
sys.exit(1 if bad else 0)
