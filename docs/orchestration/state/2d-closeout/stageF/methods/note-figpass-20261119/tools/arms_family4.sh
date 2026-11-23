#!/bin/bash
# The two arms of the family-4 label fixes (chunk C), and their checks.
#   bash arms_family4.sh <worktree> <base commit> <figure stem> [...]
# Arm 0: note-figstyle-20261117/tools/palette_family4.py (the installed files' recipe); arm 1: tools/fix_family4.py.
# Both under capture_palette.py, env -i, an empty HOME, matplotlib 3.10.8 (figenv/mpl3108). Then, for each figure named:
#   arm 0's PDF against the file installed at the base: bytes_but_date.py and raster.py;
#   arm 1 against arm 0: fig-restyle-20261031/tools/compare.py with no restyle tables (every data item's full hash);
#   the drawn strings, equal after the declared edits (texts.tsv replacements; labels.tsv additions), whitespace normalized.
# Exit 0 only if every check passes.
set -u
W=$1; BASE=$2; shift 2
R=$W/docs/orchestration/state/2d-closeout/stageF/methods; N=$R/note-figpass-20261119; PT=$R/note-figstyle-20261117/tools
PK=$R/note-figstyle-20261113/runs/family4/pickles; V=/Users/josephbailey/cov2d-work/figenv/mpl3108
FIGRUN=${FIGRUN:-/Users/josephbailey/cov2d-work/figrun}; P=/Users/josephbailey/miniconda3/bin/python3
ok=1
for arm in arm0 arm1; do
  O=$FIGRUN/fp-f4fix/$arm; C=$FIGRUN/fp-f4fix/cap-$arm
  [ -e "$O" ] && find "$O" -type f -delete; [ -e "$C" ] && find "$C" -type f -delete; mkdir -p "$O" "$C"
  if [ $arm = arm0 ]; then cmd=("$PT/palette_family4.py" "$PK" "$O"); else cmd=("$N/tools/fix_family4.py" "$PK" "$O" "$@"); fi
  (cd "$O" && env -i PATH="$V/bin:/usr/bin:/bin" HOME="$FIGRUN/home" MPLCONFIGDIR="$FIGRUN/mplcfg-mpl3108" PYTHONDONTWRITEBYTECODE=1 \
     python3 "$PT/capture_palette.py" "$C" "${cmd[@]}" > "$O/log.txt" 2>&1) || { echo "FAIL $arm: $(tail -2 "$O/log.txt" | tr '\n' ' ')"; ok=0; }
  D=$N/runs/f4fix/$arm/capture/f4fix; mkdir -p "$D"; find "$D" -type f -delete
  for f in "$@"; do cp "$C/$f".pdf.* "$C/$f".png.* "$D/" 2>/dev/null; done
done
for f in "$@"; do
  inst=$(mktemp); git -C "$W" show "$BASE:docs/analysis-note/figures/$f.pdf" > "$inst"
  echo "== $f: arm 0 against the file installed at $BASE"
  "$P" -I "$PT/bytes_but_date.py" "$inst" "$FIGRUN/fp-f4fix/arm0/$f.pdf" || ok=0
  echo "raster: $("$P" -I "$R/fig-restyle-20261031/tools/raster.py" "$inst" "$FIGRUN/fp-f4fix/arm0/$f.pdf")"; rm -f "$inst"
done
echo "== arm 1 against arm 0"
"$P" -I "$R/fig-restyle-20261031/tools/compare.py" "$N/runs/f4fix/arm0" "$N/runs/f4fix/arm1" || ok=0
"$P" - "$N" "$@" <<'PY' || ok=0
import json, sys
from collections import Counter
from pathlib import Path
n, figs = Path(sys.argv[1]), sys.argv[2:]
def rows(name):
    p = n / name
    return [l.split("\t") for l in p.read_text().splitlines()[2:] if l.strip() and not l.startswith("#")] if p.exists() else []
fixes, adds = {}, {}
for r in rows("texts.tsv"):
    fixes.setdefault(r[0], []).append((r[1].replace("\\n", "\n"), r[2].replace("\\n", "\n")))
for r in rows("labels.tsv"):
    adds.setdefault(r[0], []).append(r[3])
ws = lambda t: " ".join(t.split())
import re
def norm(t):
    """A tick label compared by its value ("$\\mathdefault{1.20}$" and "1.2" are one tick); other text as is."""
    u = t.replace("$", "").replace("\\mathdefault{", "").replace("}", "").replace("\u2212", "-").strip()
    try:
        return f"<tick {float(u):g}>"
    except ValueError:
        return t
OFFSET = re.compile(r"\\times\\mathdefault\{10\^\{.(\d+)\}\}")
bad = 0
for f in figs:
    a = json.loads((n / "runs/f4fix/arm0/capture/f4fix" / f"{f}.pdf.texts").read_text())
    b = json.loads((n / "runs/f4fix/arm1/capture/f4fix" / f"{f}.pdf.texts").read_text())
    def fixed(t):
        t = ws(t)
        for old, new in fixes.get(f, []):
            t = t.replace(ws(old), ws(new))
        return t
    sa = Counter(norm(fixed(t)) for _, t in a["texts"]) + Counter(norm(ws(t)) for t in adds.get(f, []))
    sb = Counter(norm(ws(t)) for _, t in b["texts"])
    # an added y label takes the axis's power of ten as the other labels do (palette_lib.power_of_ten): arm 0's offset
    # text ("x10^-38") becomes "$10^{-38}$ " inside that label in arm 1; that one move is accepted, nothing else
    for t in list(sa):
        m = OFFSET.search(t)
        if m:
            e = m.group(1)
            for lab in adds.get(f, []):
                if " (" not in lab:   # an "above" text, not a label with a unit
                    continue
                i = lab.rindex(" (")
                moved = ws(lab[:i] + " ($10^{-" + e + "}$ " + lab[i + 2:])
                if sb[moved] and sa[ws(lab)]:
                    sa[t] -= 1; sa[ws(lab)] -= 1; sa[moved] += 1
                    print(f"  accepted: the offset {t!r} moved into the added label {moved!r}")
    sa = +sa
    extra, missing = sb - sa, sa - sb
    if extra or missing:
        print(f"strings {f}: arm 1 only {sorted(extra)}; arm 0 only {sorted(missing)}"); bad = 1
    else:
        print(f"strings {f}: equal after the declared edits ({sum(sb.values())} drawn strings)")
    print(f"  overlaps arm 0 {len(a['text_overlaps'])}, arm 1 {len(b['text_overlaps'])}")
sys.exit(bad)
PY
echo "ARMS-FAMILY4 :: $([ $ok = 1 ] && echo PASS || echo FAIL)"
[ $ok = 1 ]
