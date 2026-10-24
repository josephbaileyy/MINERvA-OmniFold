#!/bin/bash
# RE-2 part C, C10: Fig. 1 on the laptop, in the recorded environment (RE2-DECLARATION-C.md §3.8):
#     bash re2c_fig1_local.sh purity  <workdir> <python>               the K1: must reproduce 82665808... byte for byte
#     bash re2c_fig1_local.sh refined <workdir> <python> <partc dir>   Fig. 1 from E_R and Q_R; outputs copied to
#                                                                       <partc dir>/fig1/ on the cluster
# <python> is the uv venv's interpreter: python 3.12.2, matplotlib 3.11.2, numpy 2.5.4 (RUN-fig1.txt), checked here.
# Every input is fetched from the cluster and checked against its digest: the purity ones against RUN-fig1.txt's,
# the refined ones against <partc dir>/chain.json (chain of custody). The inset's \uqMedian is written from the same
# arm's budget_Q.json at 2 decimals, as make_fig1_q.py requires. Writes RUN-fig1.txt (environment, script digest,
# commit, argv, input and output digests) beside the outputs. <workdir> must not exist.
set -eo pipefail
ARM=$1; W=$2; PY=$3; C=${4:-}
HERE=$(cd "$(dirname "$0")" && pwd); REPO=$(cd "$HERE/../../.." && pwd)
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
ST=$REPO/docs/orchestration/state/2d-closeout
if [ "$ARM" = purity ]; then
    RB=/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageF-rebuild-20261018/outA
    for f in cov2d_Q_205.npz budget_Q.json SHA256SUMS; do scp -q "$S:$RB/$f" in/; done
    scp -q "$S:/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-production-20261015/results/s5/production_cov.npz" in/
    scp -q "$S:/global/cfs/cdirs/m3246/josephrb/2d-closeout-playlist-term-20261016/playlist_term.npz" in/
    want in/cov2d_Q_205.npz 771e49a5510ff15fa522b73ab49b18329c2a58f092efb12a26aee39949168ced
    want in/budget_Q.json e7e3f24cc0ca3f2788925c5d1add94a4ee5f7bc19d1959933c120d700303b5fb
    want in/production_cov.npz 6689d2fc2a795a72e66ee953a32d94c7906dd81a866771979f379c5f163a9ddc
    want in/playlist_term.npz c1723cb5e185ae7a6176fbbe523432ab87877c8cddcfe721eaed71f0a43b9476
    cp "$ST/playlist-term/outputs/combination/combination.json" in/
    REDUCE=$ST/../next-preparation-20261009/two-d-path/operands/remote_reduce.json
    EXTRA=()
else
    [ -n "$C" ] || { echo "refined: name the part C directory"; exit 2; }
    scp -q "$S:$C/chain.json" in/
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
fi
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
if [ "$ARM" = purity ]; then
    want out/fig1_validation.pdf 82665808e99056b1f79754647d7640078dffe94fc667691a979a22769022a0fb
    echo "K1: fig1_validation.pdf reproduces 82665808 byte for byte"
else
    ssh -o BatchMode=yes "$S" "mkdir -p $C/fig1 && [ -z \"\$(ls -A $C/fig1)\" ]" || { echo "$C/fig1 is not empty"; exit 4; }
    scp -q out/* RUN-fig1.txt fig1_run.log in/uqmedian.tex in/pins.json "$S:$C/fig1/"
    echo "copied to $S:$C/fig1/"
fi
