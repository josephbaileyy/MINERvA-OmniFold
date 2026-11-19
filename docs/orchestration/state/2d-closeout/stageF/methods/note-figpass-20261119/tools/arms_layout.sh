#!/bin/bash
# The two arms of one locally drawn note figure for the layout pass, and their checks (README.md, "The method").
#   bash arms_layout.sh <worktree> <family> <venv> <base commit> <stem> <extra PYTHONPATH or -> <producer> [args,
#                       with @OUT@ for the arm's output directory]
# Arm 0 runs the producer under the palette pass's palette_run.py (the edits that drew the installed file); arm 1
# under this record's layout_run.py (the same edits, then layout_lib's). With ARM0=plain (a figure the palette pass
# left as its producer drew it), arm 0 is the plain producer and arm 1 skips the palette edits (LAYOUT_PALETTE=0). Both under capture_palette.py, env -i, an
# empty HOME, the venv given, BLAS threads 1. Then:
#   arm 0's <stem>.pdf against the file installed at the base: bytes_but_date.py and raster.py (or, with
#   INSTALLED_FROM=<path in the base>, against that file; or, with INSTALLED_STRINGS=1, arm 0's drawn strings against the
#   installed PDF's text, for a figure its producer no longer draws byte for byte);
#   arm 1 against arm 0: fig-restyle-20261031/tools/compare.py with no restyle tables, so every item's full hash
#   (data, colours, line styles) must be equal; and the multiset of drawn strings must be equal, after texts.tsv's
#   declared wording fixes are made on arm 0's;
#   per arm: the canvas size, the smallest and median text size, and capture_any.py's text overlaps.
# Arm outputs go to $FIGRUN/fp-<family>/{arm0,arm1}; captures to runs/<family>/{arm0,arm1}/capture/<family>/.
# Exit 0 only if every check passes.
set -u
W=$1; FAM=$2; VENV=$3; BASE=$4; STEM=$5; XP=$6; shift 6
R=$W/docs/orchestration/state/2d-closeout/stageF/methods; N=$R/note-figpass-20261119; PT=$R/note-figstyle-20261117/tools
FIGRUN=${FIGRUN:-/Users/josephbailey/cov2d-work/figrun}
P=/Users/josephbailey/miniconda3/bin/python3
PP=""; [ "$XP" != - ] && PP=$XP
ok=1
for arm in arm0 arm1; do
  O=$FIGRUN/fp-$FAM/$arm; C=$N/runs/$FAM/$arm/capture/$FAM
  [ -e "$O" ] && find "$O" -type f -delete; [ -e "$C" ] && find "$C" -type f -delete
  mkdir -p "$O" "$FIGRUN/home" "$FIGRUN/mplcfg-$(basename "$VENV")"
  args=(); for a in "$@"; do args+=("${a//@OUT@/$O}"); done
  if [ $arm = arm0 ]; then wrap="$PT/palette_run.py"; else wrap="$N/tools/layout_run.py"; fi
  wrapargs=("$wrap"); lp=1
  if [ "${ARM0:-palette}" = plain ]; then lp=0; [ $arm = arm0 ] && wrapargs=(); fi   # a figure the palette pass left as drawn
  (cd "$O" && env -i PATH="$VENV/bin:/usr/bin:/bin" HOME="$FIGRUN/home" MPLCONFIGDIR="$FIGRUN/mplcfg-$(basename "$VENV")" \
     LAYOUT_PALETTE=$lp PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
     PYTHONPATH="$PP" python3 "$PT/capture_palette.py" "$C" ${wrapargs[@]+"${wrapargs[@]}"} "${args[@]}" \
     > "$O/log.txt" 2>&1) || { echo "FAIL $FAM $arm: rc $? ($(tail -2 "$O/log.txt" | tr '\n' ' '))"; ok=0; }
done
if [ -n "${INSTALLED_STRINGS:-}" ]; then   # the producer no longer draws the installed file byte for byte (RE-1 K3 for
  # Fig. 17: same values and text, other geometry): arm 0's drawn strings must be the installed PDF's text instead
  inst=$(mktemp); git -C "$W" show "$BASE:docs/analysis-note/figures/$STEM.pdf" > "$inst"
  echo "== $FAM ($STEM): arm 0's drawn strings against the text of the file installed at $BASE (pdftotext)"
  pdftotext -raw "$inst" - > "$inst.txt"
  "$P" - "$inst.txt" "$N/runs/$FAM/arm0/capture/$FAM/$STEM.pdf.texts" <<'PY' || ok=0
import json, re, sys
inst = open(sys.argv[1], encoding="utf-8", errors="replace").read()
# the installed file's words (two letters or more) and decimal values (the annotation's numbers); integers are tick
# labels, which pdftotext joins with superscripts and strips of minus signs, so they are not compared
tok = lambda t: set(re.findall(r"[A-Za-z]{2,}|\d+\.\d+", t))
want = tok(inst)
got = set().union(*(tok(t) for _, t in json.load(open(sys.argv[2]))["texts"]))
miss = sorted(want - got)
print(f"installed words and decimals: {len(want)} (decimals {sorted(w for w in want if '.' in w)}); "
      f"missing from arm 0's drawn strings: {miss}")
sys.exit(0 if not miss else 1)
PY
  rm -f "$inst" "$inst.txt"
else
inst=$(mktemp)
if [ -n "${INSTALLED_FROM:-}" ]; then git -C "$W" show "$BASE:$INSTALLED_FROM" > "$inst"; src=$INSTALLED_FROM
else git -C "$W" show "$BASE:docs/analysis-note/figures/$STEM.pdf" > "$inst"; src=docs/analysis-note/figures/$STEM.pdf; fi
echo "== $FAM ($STEM): arm 0 against $src at $BASE"
"$P" -I "$PT/bytes_but_date.py" "$inst" "$FIGRUN/fp-$FAM/arm0/$STEM.pdf" || ok=0
echo "raster: $("$P" -I "$R/fig-restyle-20261031/tools/raster.py" "$inst" "$FIGRUN/fp-$FAM/arm0/$STEM.pdf")" || ok=0
rm -f "$inst"
fi
echo "== $FAM: arm 1 against arm 0"
c0=$(cd "$N/runs/$FAM/arm0/capture/$FAM" 2>/dev/null && ls *.json 2>/dev/null | sort | tr "\n" " ")
c1=$(cd "$N/runs/$FAM/arm1/capture/$FAM" 2>/dev/null && ls *.json 2>/dev/null | sort | tr "\n" " ")
[ -n "$c0" ] && [ "$c0" = "$c1" ] && echo "captures: $c0" \
  || { echo "FAIL captures: arm 0 [$c0], arm 1 [$c1] (none, or not the same files)"; ok=0; }
"$P" -I "$R/fig-restyle-20261031/tools/compare.py" "$N/runs/$FAM/arm0" "$N/runs/$FAM/arm1" || ok=0
"$P" - "$N/runs/$FAM" "$FAM" "$N/texts.tsv" <<'PY' || ok=0
import json, statistics, sys
from collections import Counter
from pathlib import Path
d, fam = Path(sys.argv[1]), sys.argv[2]
fixes = {}   # texts.tsv: the declared wording fixes arm 1 makes; arm 0's strings are compared after them
tp = Path(sys.argv[3])
if tp.exists():
    for ln in tp.read_text().splitlines()[2:]:
        if ln.strip() and not ln.startswith("#"):
            f, old, new = ln.split("\t")[:3]
            fixes.setdefault(f, []).append((old.replace("\\n", "\n"), new.replace("\\n", "\n")))
bad = 0
for p in sorted((d / "arm0" / "capture" / fam).glob("*.pdf.texts")):
    q = d / "arm1" / "capture" / fam / p.name
    if not q.exists():
        print(f"FAIL {p.name}: no arm 1 capture"); bad = 1; continue
    a, b = json.loads(p.read_text()), json.loads(q.read_text())
    stem = p.name[:-len(".pdf.texts")]
    def fixed(t):
        for old, new in fixes.get(stem, []):
            t = t.replace(old, new)
        return t
    def ws(t):   # the capture's strings: line breaks may be stored as spaces, so whitespace is compared normalized
        return " ".join(t.split())
    sa, sb = Counter(ws(fixed(t)) for _, t in a["texts"]), Counter(ws(t) for _, t in b["texts"])
    if sa != sb:
        print(f"FAIL strings {stem}: arm 0 only {sorted((sa - sb).elements())}, arm 1 only {sorted((sb - sa).elements())}")
        bad = 1
    else:
        print(f"strings {stem}: equal ({sum(sa.values())} drawn strings)")
    for arm, x in (("arm 0", a), ("arm 1", b)):
        s = [z for z, _ in x["texts"]]
        print(f"  {arm}: canvas {x['size_in'][0]:.3f} x {x['size_in'][1]:.3f} in; font size min {min(s):.2f}, "
              f"median {statistics.median(s):.2f} pt; text overlaps {len(x['text_overlaps'])}"
              + ("" if arm == "arm 0" or not x["text_overlaps"] else f" {[o[:2] for o in x['text_overlaps']]}"))
sys.exit(bad)
PY
echo "ARMS-LAYOUT $FAM :: $([ $ok = 1 ] && echo PASS || echo FAIL)"
[ $ok = 1 ]
