#!/bin/bash
# The figure round of 2026-11-21 (README.md): Figs. 2 and 3 redrawn (two arms each), the stamp stripped from ten more.
#   [INSTALL=1] bash run_round.sh <worktree> <base commit>
set -u
W=$1; BASE=$2
M=$W/docs/orchestration/state/2d-closeout/stageF/methods; N=$M/note-figround-20261121; T=$M/note-figstyle-20261117/tools
V=$HOME/cov2d-work/figenv/rootmpl3108; PY=$V/bin/python3; P=$HOME/miniconda3/bin/python3; PE=$HOME/cov2d-work/figenv/pdfedit/bin/python
X=$HOME/cov2d-work/figfetch/er-anc/xsec.root; A=$HOME/cov2d-work/figfetch/anc; FR=${FIGRUN:-$HOME/cov2d-work/figrun}/round
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
sha() { shasum -a 256 "$1" | cut -c1-64; }
ins() { git -C "$W" show "$BASE:docs/analysis-note/figures/$1.pdf" > "$2"; }
okall=1

# ---------------- Fig. 2
ok=1; CK=$N/runs/fig2/CHECKS.txt; mkdir -p $N/runs/fig2; : > "$CK"; L() { echo "$*" | tee -a "$CK"; }
L "# Fig. 2 round ($(date -u +%Y-%m-%dT%H:%M:%SZ)): bash tools/run_round.sh <wt> $BASE; compose_fig2_round.py sha256 $(sha $N/tools/compose_fig2_round.py)"
L "# arm 0: note-fig23-20261121/tools/compose_fig2_pubratio.py (sha256 $(sha $M/note-fig23-20261121/tools/compose_fig2_pubratio.py)), the installed recipe"
for arm in arm0 arm1; do
  rm -rf "$FR/f2-$arm" "$N/runs/fig2/$arm"; mkdir -p "$FR/f2-$arm"
  tool=$M/note-fig23-20261121/tools/compose_fig2_pubratio.py; [ $arm = arm1 ] && tool=$N/tools/compose_fig2_round.py
  FIG2_ROUND_JSON=$N/runs/fig2/compose_fig2_round.json $PY $T/capture_palette.py "$N/runs/fig2/$arm/capture" $T/remap_anc.py $A "$tool" $X $A "$FR/f2-$arm/out" > "$FR/f2-$arm/log.txt" 2>&1 \
    || { L "FAIL fig2 $arm: $(tail -1 $FR/f2-$arm/log.txt)"; ok=0; }
  find "$N/runs/fig2/$arm/capture" -type f ! -name 'MEFHC_5iter_xsec_proj_p*' -delete
done
L "== arm 0 against the installed files at $BASE"
for f in MEFHC_5iter_xsec_proj_pt MEFHC_5iter_xsec_proj_pz; do
  ins $f "$FR/inst.pdf"; $P -I $T/bytes_but_date.py "$FR/inst.pdf" "$FR/f2-arm0/out/$f.pdf" 2>&1 | sed "s#inst.pdf#$f.pdf#" | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
done
L "== arm 1 against arm 0: every data item equal (full hashes); words = arm 0's minus the stamp (and, in p_T, the legend), tick labels may change with the size; sizes; overlaps"
$P - "$N/runs/fig2" 2>&1 <<'PY' | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
import json, sys
from collections import Counter
from pathlib import Path
d = Path(sys.argv[1]); bad = 0
for stem in ("MEFHC_5iter_xsec_proj_pt", "MEFHC_5iter_xsec_proj_pz"):
    for ext in ("pdf", "png"):
        c0, c1 = d / f"arm0/capture/{stem}.{ext}", d / f"arm1/capture/{stem}.{ext}"
        i0, i1 = json.load(open(f"{c0}.json")), json.load(open(f"{c1}.json"))
        eq = [a["hash"] for a in i0] == [b["hash"] for b in i1]
        t0, t1 = json.load(open(f"{c0}.texts")), json.load(open(f"{c1}.texts"))
        s0, s1 = Counter(" ".join(x.split()) for _, x in t0["texts"]), Counter(" ".join(x.split()) for _, x in t1["texts"])
        num = lambda x: x.replace("$\\mathdefault{", "").replace("}$", "").replace("−", "-").replace(".", "").lstrip("-").isdigit()
        gone = sorted(x for x in (s0 - s1).elements() if not num(x)); new = sorted(x for x in (s1 - s0).elements() if not num(x))
        nticks = len([x for x in list((s0 - s1).elements()) + list((s1 - s0).elements()) if num(x)])
        legend = ["This work (OmniFold)", "Published (PRD 104, 092007)", "Tune v1: our simulation (the prior)", "Tune v1: published prediction"]
        want_gone = sorted([x for x in s0 if x.startswith("MINERvA ME FHC")] + (legend if stem.endswith("_pt") else []))
        sz = sorted({round(s, 2) for s, _ in t1["texts"]})
        # overlaps: compose_fig2_round.py's own check at its final draw gates them (it stops the run on any); the capture's
        # count below is reported only: after a PDF save it measures the auto-placed y labels, placed with the PDF
        # renderer's metrics, with the screen renderer's, and reports the two-line lower label on the tick labels where
        # the file has a gap (measured from the PDF itself in the next step)
        ok = eq and gone == want_gone and not new
        print(f"  {'ok' if ok else 'FAIL'} {stem}.{ext}: {len(i0)} data items equal {eq}; strings removed {gone}; added {new}; "
              f"tick labels changed {nticks}; sizes (figure pt) {sz}; overlaps {len(t0.get('text_overlaps', []))} -> {len(t1.get('text_overlaps', []))}")
        bad |= not ok
print("FIG2-ROUND-CAPTURES ::", "PASS" if not bad else "FAIL"); sys.exit(bad)
PY
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
L "# Fig. 3 round ($(date -u +%Y-%m-%dT%H:%M:%SZ)): compose_fig3_round.py sha256 $(sha $N/tools/compose_fig3_round.py)"
L "# arm 0: note-fig23-20261121/tools/compose_fig3_inset.py on the palette chain (the installed recipe); arm 1: compose_fig3_round.py on the same chain"
for arm in arm0 arm1; do
  rm -rf "$FR/f3-$arm" "$N/runs/fig3/$arm"; mkdir -p "$FR/f3-$arm/o" "$FR/home" "$FR/mpl"
  tool=$M/note-fig23-20261121/tools/compose_fig3_inset.py; [ $arm = arm1 ] && tool=$N/tools/compose_fig3_round.py
  (cd "$FR/f3-$arm/o" && env -i PATH="$V/bin:/usr/bin:/bin" HOME="$FR/home" MPLCONFIGDIR="$FR/mpl" PYTHONDONTWRITEBYTECODE=1 \
     OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 FIG3_ROUND_JSON="$N/runs/fig3/compose_fig3_round.json" Q3_FIG3_JSON="$FR/f3-$arm/inset.json" \
     python3 $T/capture_palette.py "$N/runs/fig3/$arm/capture" "$tool" $T/palette_run.py $T/remap_anc.py $A \
     $W/2d-unfolding/compare_to_paper_fullcov.py --ours $X --out-prefix "$FR/f3-$arm/o/MEFHC_5iter" --style restyle-2026-10 \
     --print-font --sd-label > "$FR/f3-$arm/log.txt" 2>&1) || { L "FAIL fig3 $arm: $(tail -1 $FR/f3-$arm/log.txt)"; ok=0; }
done
L "== arm 0 against the installed file at $BASE"
ins MEFHC_5iter_pull_full "$FR/inst.pdf"; $P -I $T/bytes_but_date.py "$FR/inst.pdf" "$FR/f3-arm0/o/MEFHC_5iter_pull_full.pdf" 2>&1 | sed "s#inst.pdf#MEFHC_5iter_pull_full.pdf#" | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
L "== arm 1 against arm 0: data items equal except the bar edges (style only), the map's colour limits and the colour bar"
$P - "$N/runs/fig3" 2>&1 <<'PY' | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
import json, sys
from collections import Counter
from pathlib import Path
import numpy as np
d = Path(sys.argv[1]); bad = 0
for ext in ("pdf", "png"):
    c0, c1 = d / f"arm0/capture/MEFHC_5iter_pull_full.{ext}", d / f"arm1/capture/MEFHC_5iter_pull_full.{ext}"
    i0, i1 = json.load(open(f"{c0}.json")), json.load(open(f"{c1}.json"))
    z0, z1 = np.load(f"{c0}.npz"), np.load(f"{c1}.npz")
    same = [(a["kind"], a["axes"]) for a in i0] == [(a["kind"], a["axes"]) for a in i1]
    diff = [k for k, (a, b) in enumerate(zip(i0, i1)) if a["hash"] != b["hash"]]
    kinds = Counter((i0[k]["kind"], i0[k]["axes"]) for k in diff)
    bars_ok = all(i0[k]["xhash"] == i1[k]["xhash"] for k in diff if i0[k]["kind"] == "patch")   # geometry equal, style not
    img = [k for k in diff if i0[k]["kind"] == "image"]
    img_ok = all(np.array_equal(np.ma.filled(np.ma.masked_array(z0[f"i{k}.array"], z0.get(f"i{k}.array.mask", False)), np.nan),
                                np.ma.filled(np.ma.masked_array(z1[f"i{k}.array"], z1.get(f"i{k}.array.mask", False)), np.nan), equal_nan=True)
                 for k in img)
    other = [k for k in diff if i0[k]["kind"] not in ("patch", "image") and i0[k]["axes"] != 2]
    t0, t1 = json.load(open(f"{c0}.texts")), json.load(open(f"{c1}.texts"))
    s0, s1 = Counter(x for _, x in t0["texts"]), Counter(x for _, x in t1["texts"])
    gone = sorted((s0 - s1).elements()); new = sorted((s1 - s0).elements())
    num = lambda x: x.replace("$\\mathdefault{", "").replace("}$", "").replace("−", "-").replace(".", "").lstrip("-").isdigit()
    gone_words = [x for x in gone if not num(x)]; new_words = [x for x in new if not num(x)]
    ok = same and bars_ok and img_ok and not other and new_words == [] and sorted(gone_words) == sorted(
        [x for x in s0 if x.startswith("MINERvA ME FHC") or "descriptive distance" in x or "ndf paper" in x])
    if ext == "pdf": ok = ok and not t1.get("text_overlaps") and t0["size_in"] == t1["size_in"]
    print(f"  {'ok' if ok else 'FAIL'} MEFHC_5iter_pull_full.{ext}: {len(i0)} items, same order {same}; differing items {dict(kinds)}; "
          f"bar geometry equal {bars_ok}; map array equal {img_ok}; other data changes {other}; words removed {gone_words}; "
          f"words added {new_words}; tick labels changed {len([x for x in gone + new if num(x)])}; sizes (figure pt) "
          f"{sorted({round(s, 2) for s, _ in t1['texts']})}; canvas {t1['size_in']}; overlaps {len(t0.get('text_overlaps', []))} -> {len(t1.get('text_overlaps', []))}")
    bad |= not ok
print("FIG3-ROUND-CAPTURES ::", "PASS" if not bad else "FAIL"); sys.exit(bad)
PY
L "page size: $(pdfinfo "$FR/f3-arm1/o/MEFHC_5iter_pull_full.pdf" | /usr/bin/grep 'Page size' | tr -s ' ') (make_figures.sh asserts 327.6 x 165.6); printed scale 468/327.6 = 1.4286"
pdfinfo "$FR/f3-arm1/o/MEFHC_5iter_pull_full.pdf" | /usr/bin/grep -q '327.6 x 165.6' || ok=0
[ "${INSTALL:-0}" = 1 ] && [ $ok = 1 ] && { cp "$FR/f3-arm1/o/MEFHC_5iter_pull_full.pdf" "$W/docs/analysis-note/figures/"; L "installed MEFHC_5iter_pull_full.pdf sha256 $(sha $W/docs/analysis-note/figures/MEFHC_5iter_pull_full.pdf)"; }
L "RUN-FIG3-ROUND :: $([ $ok = 1 ] && echo PASS || echo FAIL)"; [ $ok = 1 ] || okall=0

# ---------------- the stamp, stripped from ten more figures
ok=1; CK=$N/runs/stamp/CHECKS.txt; mkdir -p $N/runs/stamp; : > "$CK"
L "# stamp strip ($(date -u +%Y-%m-%dT%H:%M:%SZ)): strip_stamp.py sha256 $(sha $N/tools/strip_stamp.py), figenv/pdfedit (pikepdf $($PE -c 'import pikepdf;print(pikepdf.__version__)')); inputs: the installed files at $BASE"
mkdir -p "$FR/stamp"
for f in q3_excess_projection nn_vs_gbdt_full mode_decomp_mec_eavail_central MEFHC_5iter_xsec_paper_pt_slices MEFHC_5iter_xsec_paper_pz_slices generators_vs_unfolded_band_central eavailW_band eavail_marginal_vs_paper_pull_full control_plots control_corner; do
  ins $f "$FR/stamp/in-$f.pdf"
  $PE "$N/tools/strip_stamp.py" "$FR/stamp/in-$f.pdf" "$FR/stamp/$f.pdf" "$N/runs/stamp/$f.json" 2>&1 | sed "s#in-$f.pdf#$f.pdf#" | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
  [ "${INSTALL:-0}" = 1 ] && [ -f "$FR/stamp/$f.pdf" ] && { cp "$FR/stamp/$f.pdf" "$W/docs/analysis-note/figures/$f.pdf"; L "  installed $f.pdf sha256 $(sha $W/docs/analysis-note/figures/$f.pdf)"; }
done
L "== no figure the note includes still prints the stamp"
n=0; for f in $(cd $W/docs/analysis-note && python3 - <<'PY'
import re
order=["sec_intro","sec2_method","sec3_twod","sec4_higherdim","sec5_multidim","sec6_conclusions","appA_methods","appB_negweight","appC_supplementary","appD_reproducibility"]
s=set()
for f in order:
    t="\n".join(l for l in open(f+".tex").read().splitlines() if not l.lstrip().startswith("%"))
    s.update(m.split("/")[-1].replace(".pdf","") for m in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", t))
print(" ".join(sorted(s)))
PY
); do src=$W/docs/analysis-note/figures/$f.pdf; [ "${INSTALL:-0}" = 1 ] || { [ -f "$FR/stamp/$f.pdf" ] && src=$FR/stamp/$f.pdf; }
  case $f in MEFHC_5iter_xsec_proj_pt|MEFHC_5iter_xsec_proj_pz) src=$FR/f2-arm1/out/$f.pdf;; MEFHC_5iter_pull_full) src=$FR/f3-arm1/o/$f.pdf;; esac
  if pdftotext "$src" - 2>/dev/null | tr '\n' ' ' | /usr/bin/grep -q 'ME FHC'; then L "  STILL STAMPED: $f"; n=$((n+1)); ok=0; fi; done
L "  included figures still stamped: $n"
L "RUN-STAMP :: $([ $ok = 1 ] && echo PASS || echo FAIL)"; [ $ok = 1 ] || okall=0
[ $okall = 1 ]
