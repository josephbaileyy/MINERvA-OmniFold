#!/bin/bash
# Figs. 2 and 3 redraws (README.md): two arms each and their checks; writes runs/fig2/CHECKS.txt, runs/fig3/CHECKS.txt.
#   [INSTALL=1] bash run_fig23.sh <worktree> <base commit>
# Fig. 2: arm 0 = note-figfix-20261120's recipe (compose_fig2_edges.py), arm 1 = tools/compose_fig2_pubratio.py; both
#   under capture_palette.py and remap_anc.py, in figenv/rootmpl3108, BLAS threads 1 (as figfix ran it).
# Fig. 3: arm 0 = note-figstyle-20261117's pull_full arm 1 recipe (palette_run.py, remap_anc.py,
#   compare_to_paper_fullcov.py --sd-label), arm 1 = tools/compose_fig3_inset.py on that chain; env -i, empty HOME.
set -u
W=$1; BASE=$2
M=$W/docs/orchestration/state/2d-closeout/stageF/methods; N=$M/note-fig23-20261121; T=$M/note-figstyle-20261117/tools
V=$HOME/cov2d-work/figenv/rootmpl3108; PY=$V/bin/python3; P=$HOME/miniconda3/bin/python3
X=$HOME/cov2d-work/figfetch/er-anc/xsec.root; A=$HOME/cov2d-work/figfetch/anc
FR=${FIGRUN:-$HOME/cov2d-work/figrun}/fig23; ok=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ins() { git -C "$W" show "$BASE:docs/analysis-note/figures/$1.pdf" > "$2"; }
sha() { shasum -a 256 "$1" | cut -c1-64; }

# ---------------- Fig. 2
CK=$N/runs/fig2/CHECKS.txt; : > "$CK"; L() { echo "$*" | tee -a "$CK"; }
L "# Fig. 2 (fig:xsec) lower panels as OmniFold / published ($(date -u +%Y-%m-%dT%H:%M:%SZ)): bash tools/run_fig23.sh <wt> $BASE"
L "# ROOT $($PY -c 'import ROOT;print(ROOT.gROOT.GetVersion())' 2>/dev/null), $($PY -c 'import matplotlib,numpy;print("matplotlib",matplotlib.__version__,"numpy",numpy.__version__)'); inputs xsec.root $(sha $X | cut -c1-8), cov_ptpl_minerva_inclusive_6GeV.root $(sha $A/cov_ptpl_minerva_inclusive_6GeV.root | cut -c1-8)"
L "# compose_fig2_pubratio.py sha256 $(sha $N/tools/compose_fig2_pubratio.py); arm 0 compose_fig2_edges.py sha256 $(sha $M/note-figfix-20261120/tools/compose_fig2_edges.py)"
for arm in arm0 arm1; do
  rm -rf "$FR/f2-$arm" "$N/runs/fig2/$arm"; mkdir -p "$FR/f2-$arm"
  tool=$M/note-figfix-20261120/tools/compose_fig2_edges.py; [ $arm = arm1 ] && tool=$N/tools/compose_fig2_pubratio.py
  $PY $T/capture_palette.py "$N/runs/fig2/$arm/capture" $T/remap_anc.py $A "$tool" $X $A "$FR/f2-$arm/out" > "$FR/f2-$arm/log.txt" 2>&1 \
    || { L "FAIL fig2 $arm: $(tail -1 $FR/f2-$arm/log.txt)"; ok=0; }
  # keep only the two projections' captures (the run also draws the slice figures, not touched here)
  find "$N/runs/fig2/$arm/capture" -type f ! -name 'MEFHC_5iter_xsec_proj_p*' -delete
done
L "== arm 0 against the installed files at $BASE"
for f in MEFHC_5iter_xsec_proj_pt MEFHC_5iter_xsec_proj_pz; do
  ins $f "$FR/inst.pdf"; $P -I $T/bytes_but_date.py "$FR/inst.pdf" "$FR/f2-arm0/out/$f.pdf" 2>&1 | sed "s#inst.pdf#$f.pdf#" | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
done
L "== arm 1 against arm 0 (captures): the upper panel and every other item equal; in the lower panel only the ratio points, their bars and caps, and the reference line's colour differ"
$P - "$N/runs/fig2" 2>&1 <<'PY' | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
import json, sys
from collections import Counter
from pathlib import Path
import numpy as np
d = Path(sys.argv[1]); bad = 0
for stem in ("MEFHC_5iter_xsec_proj_pt", "MEFHC_5iter_xsec_proj_pz"):
    for ext in ("pdf", "png"):
        c0, c1 = d / f"arm0/capture/{stem}.{ext}", d / f"arm1/capture/{stem}.{ext}"
        i0, i1 = json.load(open(f"{c0}.json")), json.load(open(f"{c1}.json"))
        same = [(a["kind"], a["axes"]) for a in i0] == [(a["kind"], a["axes"]) for a in i1]
        diff = [k for k, (a, b) in enumerate(zip(i0, i1)) if a["hash"] != b["hash"]]
        top = [k for k in diff if i0[k]["axes"] == 0]
        dh = [k for k in diff if i0[k]["dhash"] != i1[k]["dhash"]]   # data changes (colours left out)
        col = [k for k in diff if k not in dh]                         # colour-only changes
        good = same and not top and len(col) == 1 and i0[col[0]]["kind"] == "line" and len(dh) >= 3
        t0 = json.load(open(f"{c0}.texts")); t1 = json.load(open(f"{c1}.texts"))
        want = Counter((s, "This work / published" if x == "This work / prior" else x) for s, x in t0["texts"])   # .texts flatten line breaks
        got = Counter((s, x) for s, x in t1["texts"])
        # the lower panel's y tick labels follow the new (0.9, 1.1) range
        st = {k: v for k, v in (want - got).items()}, {k: v for k, v in (got - want).items()}
        print(f"  {'ok' if good else 'FAIL'} {stem}.{ext}: {len(i0)} items, same order {same}; upper panel differs in {top}; "
              f"lower panel: {len(dh)} items with new data, {len(col)} colour-only (the reference line)")
        print(f"     strings: arm 0 only {sorted(st[0].items())}; arm 1 only {sorted(st[1].items())}; overlaps arm 0 "
              f"{len(t0.get('text_overlaps', []))}, arm 1 {len(t1.get('text_overlaps', []))}")
        lab_ok = ("This work / published" in [x for _, x in t1["texts"]]) and not any(x == "This work / prior" for _, x in t1["texts"])
        bad |= not (good and lab_ok and len(t1.get("text_overlaps", [])) <= len(t0.get("text_overlaps", [])))
print("FIG2-CAPTURES ::", "PASS" if not bad else "FAIL"); sys.exit(bad)
PY
cp "$FR/f2-arm1/out/compose_fig2_pubratio.json" "$N/runs/fig2/" 2>/dev/null || ok=0
L "== the new lower panels (runs/fig2/compose_fig2_pubratio.json)"
$P - "$N/runs/fig2/compose_fig2_pubratio.json" 2>&1 <<'PY' | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok=0
import json, sys
import numpy as np
d = json.load(open(sys.argv[1])); bad = 0
for k, v in d.items():
    f, p, r = map(np.asarray, (v["omnifold"], v["published"], v["ratio_to_published"]))
    exact = np.array_equal(r, f / p)
    print(f"  {k}: {len(r)} bins; ratio = f/p exactly {exact}; range {r.min():.4f}..{r.max():.4f}; y range {v['ylim_before']} -> "
          f"{v['ylim_after']}; edge check after {v['edge_check_after']}")
    bad |= not exact or any(v["edge_check_after"].values())
print("FIG2-VALUES ::", "PASS" if not bad else "FAIL"); sys.exit(bad)
PY
if [ "${INSTALL:-0}" = 1 ] && [ $ok = 1 ]; then for f in MEFHC_5iter_xsec_proj_pt MEFHC_5iter_xsec_proj_pz; do
  cp "$FR/f2-arm1/out/$f.pdf" "$W/docs/analysis-note/figures/"; L "installed $f.pdf sha256 $(sha $W/docs/analysis-note/figures/$f.pdf) (arm 1: $(sha $FR/f2-arm1/out/$f.pdf))"; done; fi
L "RUN-FIG2 :: $([ $ok = 1 ] && echo PASS || echo FAIL)"

# ---------------- Fig. 3
ok3=1; CK=$N/runs/fig3/CHECKS.txt; : > "$CK"
L "# Fig. 3 (fig:pull) inset relabeled ($(date -u +%Y-%m-%dT%H:%M:%SZ)): bash tools/run_fig23.sh <wt> $BASE"
L "# compose_fig3_inset.py sha256 $(sha $N/tools/compose_fig3_inset.py); arm 0 recipe note-figstyle-20261117 pull_full arm 1 (palette_run.py sha256 $(sha $T/palette_run.py))"
for arm in arm0 arm1; do
  rm -rf "$FR/f3-$arm" "$N/runs/fig3/$arm"; mkdir -p "$FR/f3-$arm/o" "$FR/home" "$FR/mpl"
  wrap=(); [ $arm = arm1 ] && wrap=("$N/tools/compose_fig3_inset.py")
  (cd "$FR/f3-$arm/o" && env -i PATH="$V/bin:/usr/bin:/bin" HOME="$FR/home" MPLCONFIGDIR="$FR/mpl" PYTHONDONTWRITEBYTECODE=1 \
     OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 Q3_FIG3_JSON="$N/runs/fig3/compose_fig3_inset.json" \
     python3 $T/capture_palette.py "$N/runs/fig3/$arm/capture" ${wrap[@]+"${wrap[@]}"} $T/palette_run.py $T/remap_anc.py $A \
     $W/2d-unfolding/compare_to_paper_fullcov.py --ours $X --out-prefix "$FR/f3-$arm/o/MEFHC_5iter" --style restyle-2026-10 \
     --print-font --sd-label > "$FR/f3-$arm/log.txt" 2>&1) || { L "FAIL fig3 $arm: $(tail -1 $FR/f3-$arm/log.txt)"; ok3=0; }
done
L "== arm 0 against the installed file at $BASE"
ins MEFHC_5iter_pull_full "$FR/inst.pdf"; $P -I $T/bytes_but_date.py "$FR/inst.pdf" "$FR/f3-arm0/o/MEFHC_5iter_pull_full.pdf" 2>&1 | sed "s#inst.pdf#MEFHC_5iter_pull_full.pdf#" | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok3=0
L "== arm 1 against arm 0 (captures): every data item equal; texts differ only in the inset and the histogram's y tick labels"
$P - "$N/runs/fig3" 2>&1 <<'PY' | tee -a "$CK"; [ "${PIPESTATUS[0]}" = 0 ] || ok3=0
import json, sys
from collections import Counter
from pathlib import Path
d = Path(sys.argv[1]); bad = 0
for ext in ("pdf", "png"):
    c0, c1 = d / f"arm0/capture/MEFHC_5iter_pull_full.{ext}", d / f"arm1/capture/MEFHC_5iter_pull_full.{ext}"
    i0, i1 = json.load(open(f"{c0}.json")), json.load(open(f"{c1}.json"))
    eq = [a["hash"] for a in i0] == [b["hash"] for b in i1]
    t0 = json.load(open(f"{c0}.texts")); t1 = json.load(open(f"{c1}.texts"))
    a0 = Counter(x for _, x in t0["texts"]); a1 = Counter(x for _, x in t1["texts"])
    only0, only1 = sorted((a0 - a1).elements()), sorted((a1 - a0).elements())
    inset_ok = any("chi^2$/ndf paper = 2.27" in x for x in only0) and any(x.endswith("descriptive distance\nper bin = 2.27") or x.endswith("descriptive distance per bin = 2.27") for x in only1)
    rest0 = [x for x in only0 if "ndf paper" not in x]; rest1 = [x for x in only1 if "descriptive distance" not in x]
    ticks_only = all(x.replace(".", "").replace("−", "").replace("-", "").isdigit() for x in rest0 + rest1)
    print(f"  {'ok' if eq and inset_ok and ticks_only else 'FAIL'} MEFHC_5iter_pull_full.{ext}: {len(i0)} data items equal {eq}; "
          f"inset relabeled with the value kept {inset_ok}; other strings that differ (tick labels only: {ticks_only}): "
          f"arm 0 {rest0}, arm 1 {rest1}; canvas {t0['size_in']} -> {t1['size_in']}; overlaps {len(t0.get('text_overlaps', []))} -> {len(t1.get('text_overlaps', []))}")
    bad |= not (eq and inset_ok and ticks_only and t0["size_in"] == t1["size_in"]
                and len(t1.get("text_overlaps", [])) <= len(t0.get("text_overlaps", [])))
print("FIG3-CAPTURES ::", "PASS" if not bad else "FAIL"); sys.exit(bad)
PY
L "== the inset record (runs/fig3/compose_fig3_inset.json): $($P -c "import json;d=json.load(open('$N/runs/fig3/compose_fig3_inset.json'));print('value',d['value'],'; histogram y range',[round(x,2) for x in d['ylim_before']],'->',[round(x,2) for x in d['ylim_after']],'; tallest bar',d['tallest_bar'])")"
L "page size: $(pdfinfo "$FR/f3-arm1/o/MEFHC_5iter_pull_full.pdf" | /usr/bin/grep 'Page size' | tr -s ' ') (make_figures.sh asserts 327.6 x 165.6)"
pdfinfo "$FR/f3-arm1/o/MEFHC_5iter_pull_full.pdf" | /usr/bin/grep -q '327.6 x 165.6' || ok3=0
if [ "${INSTALL:-0}" = 1 ] && [ $ok3 = 1 ]; then
  cp "$FR/f3-arm1/o/MEFHC_5iter_pull_full.pdf" "$W/docs/analysis-note/figures/"
  L "installed MEFHC_5iter_pull_full.pdf sha256 $(sha $W/docs/analysis-note/figures/MEFHC_5iter_pull_full.pdf) (arm 1: $(sha $FR/f3-arm1/o/MEFHC_5iter_pull_full.pdf))"; fi
L "RUN-FIG3 :: $([ $ok3 = 1 ] && echo PASS || echo FAIL)"
[ $ok = 1 ] && [ $ok3 = 1 ]
