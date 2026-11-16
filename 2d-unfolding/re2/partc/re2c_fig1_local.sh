#!/bin/bash
# RE-2 part C, C10: Fig. 1 on the laptop, in the recorded environment (RE2-DECLARATION-C.md §3.8):
#     bash re2c_fig1_local.sh control <workdir> <python>               the K1: must reproduce 71a2ea48... byte for byte
#     bash re2c_fig1_local.sh refined <workdir> <python> <partc dir>   Fig. 1 from E_R and Q_R; outputs copied to
#                                                                       <partc dir>/fig1/ on the cluster
# The control is the refined arm on amendment 3's part C directory ($B/partc-r2, RE2-PARTC-A3-REPORT.md), with its
# chain.json pinned to the one amendment 3's redraw read, and it must reproduce that redraw's fig1_validation.pdf
# (run/partc_a3/RUN-fig1.txt; the copy docs/analysis-note/make_figures.sh installs). It never writes to the cluster.
# It replaces the purity arm, whose K1 (82665808, drawn with make_figs 9c4dbf24) no longer holds since 0b13b747 moved
# make_figs to 4e18c266 (fd/receipts-cov2d/g2r/re2shapes/fig1/README.md, under 5d-community-20261024).
# <python> is the uv venv's interpreter: python 3.12.2, matplotlib 3.11.2, numpy 2.5.4 (RUN-fig1.txt), checked here.
# Every input is fetched from the cluster and checked against its digest in <partc dir>/chain.json (chain of
# custody). The inset's \uqMedian is written from budget_Q.json at 2 decimals, as make_fig1_q.py requires. Writes
# RUN-fig1.txt (environment, script digest, commit, argv, input and output digests) beside the outputs. <workdir> must
# not exist.
set -eo pipefail
ARM=$1; W=$2; PY=$3; C=${4:-}
HERE=$(cd "$(dirname "$0")" && pwd); REPO=$(cd "$HERE/../../.." && pwd)
A3=/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partc-r2
case "$ARM" in
    control) [ -z "$C" ] || { echo "control: takes no part C directory (it reads $A3)"; exit 2; }; C=$A3 ;;
    refined) [ -n "$C" ] || { echo "refined: name the part C directory"; exit 2; } ;;
    *) echo "arm: control or refined, not '$ARM'"; exit 2 ;;
esac
[ ! -e "$W" ] || { echo "$W exists"; exit 2; }
"$PY" -c "import sys, matplotlib, numpy; assert (sys.version.split()[0], matplotlib.__version__, numpy.__version__) \
== ('3.12.2', '3.11.2', '2.5.4'), (sys.version, matplotlib.__version__, numpy.__version__)" \
    || { echo "not the recorded environment"; exit 2; }
mkdir -p "$W/in"; cd "$W"
S=saul.nersc.gov
sha() { shasum -a 256 "$1" | cut -d' ' -f1; }
want() { [ "$(sha "$1")" = "$2" ] || { echo "$1: sha256 $(sha "$1") != $2"; exit 3; }; }
scp -q "$S:/pscratch/sd/j/josephrb/pub-release-20261006/figs/fig_arrays.npz" in/
want in/fig_arrays.npz 72394a2b4eff9f14b01903ff97525bcb690c2adee58ccaf573a8d95139b415b8
scp -q "$S:$C/chain.json" in/
if [ "$ARM" = control ]; then want in/chain.json 81dcf2d0367d931eaee272bf3be9392a9e355c48f477eaf41dab56ba64ed3231; fi
for f in outA/cov2d_Q_205.npz outA/budget_Q.json outA/SHA256SUMS s5/production_cov.npz \
         playlist/playlist_term.npz combination/combination.json reduce.json; do scp -q "$S:$C/$f" in/; done
ch() { python3 -c "import json, sys; print(json.load(open('in/chain.json'))[sys.argv[1]])" "$1"; }
want in/cov2d_Q_205.npz "$(ch cov2d_Q_205)"; want in/budget_Q.json "$(ch budget_Q)"
want in/production_cov.npz "$(ch production_cov)"; want in/playlist_term.npz "$(ch playlist_npz)"
want in/combination.json "$(ch combination_json)"; want in/reduce.json "$(ch reduce)"
python3 -c "import json; c = json.load(open('in/chain.json')); json.dump({'reduce': c['reduce'], \
's5_npz': c['production_cov'], 'playlist_npz': c['playlist_npz'], 'combination': c['combination_json']}, \
open('in/pins.json', 'w'), indent=1)"
REDUCE=$W/in/reduce.json
EXTRA=(--arm refined --pins-json in/pins.json)
python3 -c "import json; print('\\\\newcommand{\\\\uqMedian}{%.2f}' % json.load(open('in/budget_Q.json'))['Q']['median_pct'])" \
    > in/uqmedian.tex
ARGS=(--npz in/fig_arrays.npz --reduce "$REDUCE" --make-figs "$REPO/publication/release/figs/make_figs.py"
      --values in/uqmedian.tex --tmp tmp --outdir out --cov in/cov2d_Q_205.npz --s5-npz in/production_cov.npz
      --playlist-npz in/playlist_term.npz --combination in/combination.json --budget in/budget_Q.json
      --step-a-sums in/SHA256SUMS "${EXTRA[@]}")
"$PY" -I "$HERE/re2c_fig1.py" "${ARGS[@]}" > fig1_run.log 2>&1
{
    echo "# Fig. 1, re2c_fig1_local.sh $ARM, $(date -u +%FT%TZ), host $(hostname)"
    echo "env: $("$PY" -c "import sys, matplotlib, numpy; print('python', sys.version.split()[0], 'matplotlib', \
matplotlib.__version__, 'numpy', numpy.__version__)") ($PY)"
    echo "commit: $(git -C "$REPO" rev-parse HEAD) clean=$([ -z "$(git -C "$REPO" status --porcelain)" ] && echo yes || echo no)"
    echo "script: $(sha "$HERE/re2c_fig1.py")  2d-unfolding/re2/partc/re2c_fig1.py"
    echo "argv: python -I re2c_fig1.py ${ARGS[*]}"
    echo "inputs:"; for f in in/*; do echo "$(sha "$f")  $f"; done
    echo "$(sha "$REDUCE")  reduce: $REDUCE"
    echo "$(sha "$REPO/publication/release/figs/make_figs.py")  publication/release/figs/make_figs.py"
    echo "outputs:"; for f in out/*; do echo "$(sha "$f")  $f"; done
} > RUN-fig1.txt
cat RUN-fig1.txt
if [ "$ARM" = control ]; then
    want out/fig1_validation.pdf 71a2ea488ab758a466d40b7d5a7a061ebd95b1cdb90a79427c3da968238b6427
    echo "K1: fig1_validation.pdf reproduces 71a2ea48 (amendment 3's refined Fig. 1) byte for byte; no cluster write"
else
    ssh -o BatchMode=yes "$S" "mkdir -p $C/fig1 && [ -z \"\$(ls -A $C/fig1)\" ]" || { echo "$C/fig1 is not empty"; exit 4; }
    scp -q out/* RUN-fig1.txt fig1_run.log in/uqmedian.tex in/pins.json "$S:$C/fig1/"
    echo "copied to $S:$C/fig1/"
fi
