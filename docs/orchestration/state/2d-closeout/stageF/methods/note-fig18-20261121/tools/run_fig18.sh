#!/bin/bash
# Fig. 18 (fig:3dmodels) redrawn with ratio panels (README.md): two arms and the checks.
#   [INSTALL=1] bash run_fig18.sh <worktree> <base commit>
# Arm 0: the installed recipe, note-figpass-20261119/tools/fix_family4.py, then note-figround-20261121/tools/strip_stamp.py;
# arm 1: tools/compose_fig18.py. Both under capture_palette.py, env -i, matplotlib 3.10.8 (figenv/mpl3108).
# Exit 0 only if every check passes.
set -u
W=$1; BASE=$2
M=$W/docs/orchestration/state/2d-closeout/stageF/methods; N=$M/note-fig18-20261121; T=$M/note-figstyle-20261117/tools
PK=$M/note-figstyle-20261113/runs/family4/pickles; V=$HOME/cov2d-work/figenv/mpl3108
P=$HOME/miniconda3/bin/python3; PE=$HOME/cov2d-work/figenv/pdfedit/bin/python; FR=${FIGRUN:-$HOME/cov2d-work/figrun}/fig18
F=generators_vs_unfolded_band_central
sha() { shasum -a 256 "$1" | cut -c1-64; }
ok=1; CK=$N/runs/fig18/CHECKS.txt; mkdir -p "$N/runs/fig18"; : > "$CK"; L() { echo "$*" | tee -a "$CK"; }
L "# Fig. 18 ($(date -u +%Y-%m-%dT%H:%M:%SZ)): bash tools/run_fig18.sh <wt> $BASE; compose_fig18.py sha256 $(sha $N/tools/compose_fig18.py)"
L "# arm 0: fix_family4.py sha256 $(sha $M/note-figpass-20261119/tools/fix_family4.py), then strip_stamp.py sha256 $(sha $M/note-figround-20261121/tools/strip_stamp.py)"
for arm in arm0 arm1; do
  rm -rf "$FR/$arm" "$N/runs/fig18/$arm"; mkdir -p "$FR/$arm/o" "$FR/home" "$FR/mpl"
  if [ $arm = arm0 ]; then cmd=("$M/note-figpass-20261119/tools/fix_family4.py" "$PK" "$FR/$arm/o" "$F")
  else cmd=("$N/tools/compose_fig18.py" "$PK" "$FR/$arm/o"); fi
  (cd "$FR/$arm/o" && env -i PATH="$V/bin:/usr/bin:/bin" HOME="$FR/home" MPLCONFIGDIR="$FR/mpl" PYTHONDONTWRITEBYTECODE=1 \
     python3 "$T/capture_palette.py" "$N/runs/fig18/$arm/capture" "${cmd[@]}" > "$FR/$arm/log.txt" 2>&1) \
     || { L "FAIL $arm: $(tail -3 "$FR/$arm/log.txt" | tr '\n' ' ')"; ok=0; }
done
/usr/bin/grep '^\[fig18\]' "$FR/arm1/log.txt" | tee -a "$CK"
[ -f "$FR/arm1/o/compose_fig18.json" ] && cp "$FR/arm1/o/compose_fig18.json" "$N/runs/fig18/compose_fig18.json"

L "== arm 0 against the installed file at $BASE (fix_family4.py's output against note-figpass-20261119/figs, then stamp-stripped against docs/analysis-note/figures)"
git -C "$W" show "$BASE:docs/orchestration/state/2d-closeout/stageF/methods/note-figpass-20261119/figs/$F.pdf" > "$FR/figpass.pdf"
$P -I "$T/bytes_but_date.py" "$FR/figpass.pdf" "$FR/arm0/o/$F.pdf" 2>&1 | sed "s#figpass.pdf#figpass/$F.pdf#" | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
mkdir -p "$FR/stamp"; cp "$FR/arm0/o/$F.pdf" "$FR/stamp/in-$F.pdf"
$PE "$M/note-figround-20261121/tools/strip_stamp.py" "$FR/stamp/in-$F.pdf" "$FR/stamp/$F.pdf" "$FR/stamp/$F.json" > "$FR/stamp/log.txt" 2>&1 \
  || { L "FAIL strip_stamp on arm 0: $(tail -2 "$FR/stamp/log.txt" | tr '\n' ' ')"; ok=0; }
git -C "$W" show "$BASE:docs/analysis-note/figures/$F.pdf" > "$FR/installed.pdf"
L "installed at $BASE: sha256 $(sha "$FR/installed.pdf")"
# strip_stamp's pikepdf output carries a trailer /ID computed from the content, date included, so a fresh arm 0 (new
# date) strips to a file that differs from the installed one in the date and the /ID. Two checks close the chain:
# (1) strip_stamp on the committed figpass file reproduces the installed file byte for byte;
# (2) the stripped arm 0 differs from the installed file only inside /CreationDate and the trailer /ID.
mkdir -p "$FR/stamp-committed"; cp "$FR/figpass.pdf" "$FR/stamp-committed/in-$F.pdf"
$PE "$M/note-figround-20261121/tools/strip_stamp.py" "$FR/stamp-committed/in-$F.pdf" "$FR/stamp-committed/$F.pdf" "$FR/stamp-committed/$F.json" > "$FR/stamp-committed/log.txt" 2>&1 \
  || { L "FAIL strip_stamp on the committed figpass file"; ok=0; }
if cmp -s "$FR/stamp-committed/$F.pdf" "$FR/installed.pdf"; then L "(1) strip_stamp(figpass/$F.pdf as committed) = installed/$F.pdf: byte-identical"
else L "(1) FAIL strip_stamp(figpass/$F.pdf as committed) differs from the installed file"; ok=0; fi
$P - "$FR/installed.pdf" "$FR/stamp/$F.pdf" 2>&1 <<'PY' | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
import re, sys
a, b = (open(p, "rb").read() for p in sys.argv[1:3])
if len(a) != len(b):
    print(f"(2) FAIL sizes {len(a)} vs {len(b)}"); sys.exit(1)
spans = []
for pat in (rb"/CreationDate \(D:[^)]*\)", rb"/ID \[<[0-9a-f]+><[0-9a-f]+>\]"):
    ma, mb = [m.span() for m in re.finditer(pat, a)], [m.span() for m in re.finditer(pat, b)]
    if len(ma) != 1 or ma != mb:
        print(f"(2) FAIL {pat!r}: {ma} vs {mb}"); sys.exit(1)
    spans += ma
diff = [i for i in range(len(a)) if a[i] != b[i]]
out = [i for i in diff if not any(s <= i < e for s, e in spans)]
print(f"(2) stripped arm 0 against installed: {len(diff)} differing bytes, {len(out)} outside /CreationDate and /ID")
sys.exit(1 if out else 0)
PY

L "== data unchanged, read from the two captures (independent of the tool's own readback): every arm-1 step height equals"
L "   arm 0's value for that generator and bin, every data point equals arm 0's, every ratio step equals arm 0's generator / data"
$P - "$N/runs/fig18" "$F" 2>&1 <<'PY' | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
import json, sys
from pathlib import Path
import numpy as np
d, F = Path(sys.argv[1]), sys.argv[2]
GENS = ("GENIE-CV", "Tune-v1", "NuWro", "GiBUU")
bad = 0
def load(arm):
    p = d / f"{arm}/capture/{F}.pdf"
    return json.load(open(f"{p}.json")), np.load(f"{p}.npz")
j0, z0 = load("arm0"); j1, z1 = load("arm1")
def heights(v, edges):
    """Step heights from a StepPatch outline: the y of the horizontal segment over each bin."""
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        hit = {v[i, 1] for i in range(len(v) - 1) if v[i, 0] == a and v[i + 1, 0] == b and v[i, 1] == v[i + 1, 1]}
        if len(hit) != 1:
            raise SystemExit(f"no unique step over [{a}, {b}]: {hit}")
        out.append(hit.pop())
    return np.asarray(out)
for c in range(3):
    bad_before = bad
    lines0 = {a["label"]: z0[f"i{a['i']}.xy"] for a in j0 if a["kind"] == "line" and a["axes"] == c}
    x0, dat0 = lines0["_nolegend_"][:, 0], lines0["_nolegend_"][:, 1]
    top = [a for a in j1 if a["axes"] == c]; bot = [a for a in j1 if a["axes"] == c + 3]
    pt = [a for a in top if a["kind"] == "patch"]; pb = [a for a in bot if a["kind"] == "patch"]
    dl = [a for a in top if a["kind"] == "line"]
    if len(pt) != 4 or len(pb) != 4 or len(dl) != 1:
        print(f"  FAIL panel {c}: {len(pt)} top steps, {len(pb)} ratio steps, {len(dl)} data lines"); bad = 1; continue
    xy1 = z1[f"i{dl[0]['i']}.xy"]
    keep = np.isin(x0, xy1[:, 0])
    if not (np.array_equal(xy1[:, 0], x0[keep]) and np.array_equal(xy1[:, 1], dat0[keep])):
        print(f"  FAIL panel {c}: data points differ"); bad = 1
    v = z1[f"i{pt[0]['i']}.vertices"]
    edges = np.unique(v[:, 0])
    if len(edges) != keep.sum() + 1:
        print(f"  FAIL panel {c}: {len(edges)} edges for {keep.sum()} drawn bins"); bad = 1; continue
    for k, g in enumerate(GENS):
        col0 = z1[f"i{pt[k]['i']}.edge"]
        if c == 0 and pt[k]["label"] != g:
            print(f"  FAIL panel 0: step {k} is labelled {pt[k]['label']!r}, expected {g}"); bad = 1
        ref = [a for a in j1 if a["axes"] == 0 and a["kind"] == "patch" and a["label"] == g][0]
        if not np.array_equal(col0, z1[f"i{ref['i']}.edge"]) or not np.array_equal(z1[f"i{pb[k]['i']}.edge"], col0):
            print(f"  FAIL panel {c}: {g}'s colour is not the same in its step, its ratio and panel 0's legend entry"); bad = 1
        g0 = lines0[g][:, 1][keep]
        h = heights(z1[f"i{pt[k]['i']}.vertices"], edges)
        rh = heights(z1[f"i{pb[k]['i']}.vertices"], edges)
        if not np.array_equal(h, g0):
            print(f"  FAIL panel {c} {g}: step heights differ from arm 0"); bad = 1
        if not np.array_equal(rh, g0 / dat0[keep]):
            print(f"  FAIL panel {c} {g}: ratio steps differ from arm 0's generator / data"); bad = 1
    print(f"  panel {c}: {keep.sum()} of {len(x0)} bins drawn (left off: x = {x0[~keep].tolist()}); "
          + ("4 generators, their ratios and the data equal arm 0's bitwise" if bad == bad_before else "FAILED (above)"))
print("FIG18-DATA ::", "PASS" if not bad else "FAIL"); sys.exit(bad)
PY

L "== drawn strings: arm 1's, and no stamp"
$P - "$N/runs/fig18" "$F" 2>&1 <<'PY' | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
import json, sys
from collections import Counter
from pathlib import Path
d, F = Path(sys.argv[1]), sys.argv[2]
t0 = json.load(open(d / f"arm0/capture/{F}.pdf.texts")); t1 = json.load(open(d / f"arm1/capture/{F}.pdf.texts"))
s0, s1 = Counter(x for _, x in t0["texts"]), Counter(x for _, x in t1["texts"])
num = lambda x: x.replace("$\\mathdefault{", "").replace("}$", "").replace("−", "-").replace(".", "").lstrip("-").isdigit()
print(f"  arm 0 only (words): {sorted(x for x in s0 - s1 if not num(x))}")
print(f"  arm 1 only (words): {sorted(x for x in s1 - s0 if not num(x))}")
stamp = [x for x in s1 if "POT" in x or "FHC" in x]
print(f"  stamp in arm 1: {stamp}; capture overlaps (reported, not a gate; README) pdf {len(t0['text_overlaps'])} -> {len(t1['text_overlaps'])}")
sys.exit(1 if stamp else 0)
PY
L "== no overlapping words in the PDF itself (pdftotext -bbox; a pair counts only if it overlaps by more than 0.05 pt both ways)"
pdftotext -bbox "$FR/arm1/o/$F.pdf" - > "$FR/arm1/words.html"
$P - "$FR/arm1/words.html" 2>&1 <<'PY' | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
import re, sys
w = [(float(a), float(b), float(c), float(e), t) for a, b, c, e, t in re.findall(
    r'<word xMin="([-\d.]+)" yMin="([-\d.]+)" xMax="([-\d.]+)" yMax="([-\d.]+)">([^<]*)</word>', open(sys.argv[1]).read())]
touch, ov = [], []
for i, p in enumerate(w):
    for q in w[i + 1:]:
        dx, dy = min(p[2], q[2]) - max(p[0], q[0]), min(p[3], q[3]) - max(p[1], q[1])
        if dx > 0.05 and dy > 0.05:
            ov.append((p[4], q[4], round(dx, 2), round(dy, 2)))
        elif dx >= 0 and dy >= 0:
            touch.append((p[4], q[4]))
print(f"  {len(w)} words; overlapping pairs {ov}; touching only (a subscript at its base glyph): {touch}")
sys.exit(1 if ov else 0)
PY
L "page: $(pdfinfo "$FR/arm1/o/$F.pdf" | /usr/bin/grep 'Page size' | tr -s ' '); printed at \\textwidth = 468 pt, scale $($P -c "print(round(468/$(pdfinfo "$FR/arm1/o/$F.pdf" | awk '/Page size/{print $3}'),4))") (fonts print at note_print_style's 8.3/8.5/9.3 pt)"
[ "${INSTALL:-0}" = 1 ] && [ $ok = 1 ] && { cp "$FR/arm1/o/$F.pdf" "$W/docs/analysis-note/figures/$F.pdf"; L "installed $F.pdf sha256 $(sha "$W/docs/analysis-note/figures/$F.pdf")"; }
L "RUN-FIG18 :: $([ $ok = 1 ] && echo PASS || echo FAIL)"
[ $ok = 1 ]
