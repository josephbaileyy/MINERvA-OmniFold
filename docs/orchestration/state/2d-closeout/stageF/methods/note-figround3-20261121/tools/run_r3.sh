#!/bin/bash
# Round 3 of 2026-11-21 (README.md): Figs. 2 and 3 redrawn, two arms each.
#   [INSTALL=1] bash run_r3.sh <worktree> <base commit>
set -u
W=$1; BASE=$2
M=$W/docs/orchestration/state/2d-closeout/stageF/methods; N=$M/note-figround3-20261121; T=$M/note-figstyle-20261117/tools
V=$HOME/cov2d-work/figenv/rootmpl3108; PY=$V/bin/python3; P=$HOME/miniconda3/bin/python3; PE=$HOME/cov2d-work/figenv/pdfedit/bin/python
X=$HOME/cov2d-work/figfetch/er-anc/xsec.root; A=$HOME/cov2d-work/figfetch/anc; FR=${FIGRUN:-$HOME/cov2d-work/figrun}/r3
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
sha() { shasum -a 256 "$1" | cut -c1-64; }
ins() { git -C "$W" show "$BASE:docs/analysis-note/figures/$1.pdf" > "$2"; }
okall=1

# ---------------- Fig. 2
ok=1; CK=$N/runs/fig2/CHECKS.txt; mkdir -p $N/runs/fig2; : > "$CK"; L() { echo "$*" | tee -a "$CK"; }
L "# Fig. 2 round 3 ($(date -u +%Y-%m-%dT%H:%M:%SZ)): bash tools/run_r3.sh <wt> $BASE; compose_fig2_r3.py sha256 $(sha $N/tools/compose_fig2_r3.py)"
L "# arm 0: note-figround-20261121/tools/compose_fig2_round.py (sha256 $(sha $M/note-figround-20261121/tools/compose_fig2_round.py)), the installed recipe"
for arm in arm0 arm1; do
  rm -rf "$FR/f2-$arm" "$N/runs/fig2/$arm"; mkdir -p "$FR/f2-$arm"
  tool=$M/note-figround-20261121/tools/compose_fig2_round.py; [ $arm = arm1 ] && tool=$N/tools/compose_fig2_r3.py
  FIG2_ROUND_JSON="$FR/f2-$arm-r2.json" FIG2_R3_JSON=$N/runs/fig2/compose_fig2_r3.json $PY $T/capture_palette.py "$N/runs/fig2/$arm/capture" $T/remap_anc.py $A "$tool" $X $A "$FR/f2-$arm/out" > "$FR/f2-$arm/log.txt" 2>&1 \
    || { L "FAIL fig2 $arm: $(tail -1 $FR/f2-$arm/log.txt)"; ok=0; }
  find "$N/runs/fig2/$arm/capture" -type f ! -name 'MEFHC_5iter_xsec_proj_p*' -delete
done
L "== arm 0 against the installed files at $BASE"
for f in MEFHC_5iter_xsec_proj_pt MEFHC_5iter_xsec_proj_pz; do
  ins $f "$FR/inst.pdf"; $P -I $T/bytes_but_date.py "$FR/inst.pdf" "$FR/f2-arm0/out/$f.pdf" 2>&1 | sed "s#inst.pdf#$f.pdf#" | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
done
L "== arm 1 against arm 0: every data item equal with colours left out (dhash); full hashes differ only in the published-prediction line (colour); strings differ only in the two legend renames (p_par)"
$P - "$N/runs/fig2" 2>&1 <<'PY2' | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
import json, sys
from collections import Counter
from pathlib import Path
d = Path(sys.argv[1]); bad = 0
REN = {"Tune v1: our simulation (the prior)": "Tune v1 prior (this work)", "Tune v1: published prediction": "Tune v1 published prediction"}
for stem in ("MEFHC_5iter_xsec_proj_pt", "MEFHC_5iter_xsec_proj_pz"):
    for ext in ("pdf", "png"):
        c0, c1 = d / f"arm0/capture/{stem}.{ext}", d / f"arm1/capture/{stem}.{ext}"
        i0, i1 = json.load(open(f"{c0}.json")), json.load(open(f"{c1}.json"))
        deq = [a["dhash"] for a in i0] == [b["dhash"] for b in i1]
        diff = [i0[k]["label"] for k in range(len(i0)) if i0[k]["hash"] != i1[k]["hash"]]
        t0, t1 = json.load(open(f"{c0}.texts")), json.load(open(f"{c1}.texts"))
        want = Counter(REN.get(x, x) for _, x in t0["texts"]); got = Counter(x for _, x in t1["texts"])
        ok = deq and diff == ["Tune v1: published prediction"] and want == got
        print(f"  {'ok' if ok else 'FAIL'} {stem}.{ext}: {len(i0)} items, colour-free data equal {deq}; colour changed in {diff}; "
              f"strings = arm 0's with the renames {want == got}; overlaps {len(t0.get('text_overlaps', []))} -> {len(t1.get('text_overlaps', []))} (reported; see README)")
        bad |= not ok
print("FIG2-R3-CAPTURES ::", "PASS" if not bad else "FAIL"); sys.exit(bad)
PY2
L "== the lower label clears the lower tick labels in the PDF itself (pdftotext word boxes: the label's right edge left of the ticks' left edge)"
for f in MEFHC_5iter_xsec_proj_pt MEFHC_5iter_xsec_proj_pz; do
  g=$(pdftotext -bbox "$FR/f2-arm1/out/$f.pdf" - | $P -c "
import re,sys
w=[(float(a),float(c),t) for a,c,t in re.findall(r'<word xMin=\"([-\d.]+)\" yMin=\"[-\d.]+\" xMax=\"([-\d.]+)\" yMax=\"[-\d.]+\">([^<]*)</word>', sys.stdin.read())]
lab=[x for x in w if x[2] in ('This','work','/','published') and x[0]<40]; tk=[x for x in w if x[2] in ('0.95','1.00','1.05')]
print(round(min(x[0] for x in tk)-max(x[1] for x in lab),2) if lab and tk else 'NA')")
  L "  $f: gap $g pt"; $P -c "import sys; sys.exit(0 if '$g'!='NA' and float('$g')>0 else 1)" || ok=0
done
L "== printed sizes (0.49 textwidth = 229.32 pt over the saved page width)"
for f in MEFHC_5iter_xsec_proj_pt MEFHC_5iter_xsec_proj_pz; do
  w=$(pdfinfo "$FR/f2-arm1/out/$f.pdf" | awk '/Page size/{print $3}')
  L "  $f: page width $w pt, scale $($P -c "print(round(229.32/$w,4))"); labels $($P -c "import json;d=json.load(open('$N/runs/fig2/arm1/capture/$f.pdf.texts'));s=max(x for x,_ in d['texts']);print(round(s*229.32/$w,2))") pt, ticks $($P -c "import json;d=json.load(open('$N/runs/fig2/arm1/capture/$f.pdf.texts'));s=min(x for x,_ in d['texts']);print(round(s*229.32/$w,2))") pt printed"
done
[ "${INSTALL:-0}" = 1 ] && [ $ok = 1 ] && for f in MEFHC_5iter_xsec_proj_pt MEFHC_5iter_xsec_proj_pz; do cp "$FR/f2-arm1/out/$f.pdf" "$W/docs/analysis-note/figures/"; L "installed $f.pdf sha256 $(sha $W/docs/analysis-note/figures/$f.pdf)"; done
L "RUN-FIG2-ROUND :: $([ $ok = 1 ] && echo PASS || echo FAIL)"; [ $ok = 1 ] || okall=0

# ---------------- Fig. 3
ok=1; CK=$N/runs/fig3/CHECKS.txt; mkdir -p $N/runs/fig3; : > "$CK"
L "# Fig. 3 round 3 ($(date -u +%Y-%m-%dT%H:%M:%SZ)): compose_fig3_r3.py sha256 $(sha $N/tools/compose_fig3_r3.py)"
L "# arm 0: note-figround-20261121/tools/compose_fig3_round.py on the palette chain (the installed recipe); arm 1: compose_fig3_r3.py on the same chain"
for arm in arm0 arm1; do
  rm -rf "$FR/f3-$arm" "$N/runs/fig3/$arm"; mkdir -p "$FR/f3-$arm/o" "$FR/home" "$FR/mpl"
  tool=$M/note-figround-20261121/tools/compose_fig3_round.py; [ $arm = arm1 ] && tool=$N/tools/compose_fig3_r3.py
  (cd "$FR/f3-$arm/o" && env -i PATH="$V/bin:/usr/bin:/bin" HOME="$FR/home" MPLCONFIGDIR="$FR/mpl" PYTHONDONTWRITEBYTECODE=1 \
     OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 FIG3_ROUND_JSON="$FR/f3-$arm/r2.json" FIG3_R3_JSON="$N/runs/fig3/compose_fig3_r3.json" \
     python3 $T/capture_palette.py "$N/runs/fig3/$arm/capture" "$tool" $T/palette_run.py $T/remap_anc.py $A \
     $W/2d-unfolding/compare_to_paper_fullcov.py --ours $X --out-prefix "$FR/f3-$arm/o/MEFHC_5iter" --style restyle-2026-10 \
     --print-font --sd-label > "$FR/f3-$arm/log.txt" 2>&1) || { L "FAIL fig3 $arm: $(tail -1 $FR/f3-$arm/log.txt)"; ok=0; }
done
L "== arm 0 against the installed file at $BASE"
ins MEFHC_5iter_pull_full "$FR/inst.pdf"; $P -I $T/bytes_but_date.py "$FR/inst.pdf" "$FR/f3-arm0/o/MEFHC_5iter_pull_full.pdf" 2>&1 | sed "s#inst.pdf#MEFHC_5iter_pull_full.pdf#" | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
L "== arm 1 against arm 0: every data item equal (full hashes); strings equal apart from the histogram's x tick labels; overlaps"
$P - "$N/runs/fig3" 2>&1 <<'PY3' | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
import json, sys
from collections import Counter
from pathlib import Path
d = Path(sys.argv[1]); bad = 0
num = lambda x: x.replace("$\\mathdefault{", "").replace("}$", "").replace("−", "-").replace(".", "").lstrip("-").isdigit()
for ext in ("pdf", "png"):
    c0, c1 = d / f"arm0/capture/MEFHC_5iter_pull_full.{ext}", d / f"arm1/capture/MEFHC_5iter_pull_full.{ext}"
    i0, i1 = json.load(open(f"{c0}.json")), json.load(open(f"{c1}.json"))
    eq = [a["hash"] for a in i0] == [b["hash"] for b in i1]
    t0, t1 = json.load(open(f"{c0}.texts")), json.load(open(f"{c1}.texts"))
    s0, s1 = Counter(x for _, x in t0["texts"]), Counter(x for _, x in t1["texts"])
    words = sorted(x for x in (s0 - s1) + (s1 - s0) if not num(x))
    ok = eq and not words and not (ext == "pdf" and t1.get("text_overlaps"))
    print(f"  {'ok' if ok else 'FAIL'} MEFHC_5iter_pull_full.{ext}: {len(i0)} data items equal {eq}; words changed {words}; tick labels changed "
          f"{len([x for x in list((s0 - s1).elements()) + list((s1 - s0).elements()) if num(x)])}; overlaps {len(t0.get('text_overlaps', []))} -> {len(t1.get('text_overlaps', []))}")
    bad |= not ok
print("FIG3-R3-CAPTURES ::", "PASS" if not bad else "FAIL"); sys.exit(bad)
PY3
L "page size: $(pdfinfo "$FR/f3-arm1/o/MEFHC_5iter_pull_full.pdf" | /usr/bin/grep 'Page size' | tr -s ' ') (cropped to content; was 327.6 x 165.6); printed sizes and scale: $($P -c "import json;d=json.load(open('$N/runs/fig3/compose_fig3_r3.json'));print(d['printed_sizes_pt'],'pt at scale',round(d['printed_scale'],4))")"
[ "${INSTALL:-0}" = 1 ] && [ $ok = 1 ] && { cp "$FR/f3-arm1/o/MEFHC_5iter_pull_full.pdf" "$W/docs/analysis-note/figures/"; L "installed MEFHC_5iter_pull_full.pdf sha256 $(sha $W/docs/analysis-note/figures/MEFHC_5iter_pull_full.pdf)"; }
L "RUN-FIG3-ROUND :: $([ $ok = 1 ] && echo PASS || echo FAIL)"; [ $ok = 1 ] || okall=0

[ $okall = 1 ]
