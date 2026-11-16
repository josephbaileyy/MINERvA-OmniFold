#!/bin/bash
# Fig. 1 version B' (DECISION-20261116-joseph-paper-batch.md item 15), on the laptop only: no ssh, no scp, no cluster
# read or write. Two arms, each re2c_fig1.py (the refined arm, as re2c_fig1_local.sh runs it) with the current
# make_figs.py, then the drawn-data identity check (fig1_identity.py) against make_figs.py 4e18c266 on the same arrays:
#   a  route A's inputs: each must equal its digest in ../route-a/RUN-fig1.txt, and chain.json, combination.json,
#      reduce.json and SHA256SUMS must also equal the committed copies under ../../run2/g2r/. The old producer must
#      redraw ../route-a's fig1_validation.pdf (1ead58a2) byte for byte.
#   c  amendment 3's inputs (the control's): each must equal its digest in ../control/RUN-fig1.txt. The old producer
#      must redraw amendment 3's Fig. 1 (71a2ea48) byte for byte. Its new fig1_validation.pdf is the control arm's K1.
# In both arms fig2 and fig3 must equal ../route-a's committed copies byte for byte. The repository must be clean.
# Writes <workdir>/{old,a,c}/ and <workdir>/RUN-bprime.txt.
#   bash run_bprime.sh <workdir> <python> <route A inputs dir> <amendment 3 inputs dir>
set -eo pipefail
W=$1; PY=$2; INA=$(cd "$3" && pwd); INC=$(cd "$4" && pwd)
HERE=$(cd "$(dirname "$0")" && pwd); REPO=$(git -C "$HERE" rev-parse --show-toplevel)
P=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/g2r/re2shapes
MF=$REPO/publication/release/figs/make_figs.py
[ ! -e "$W" ] || { echo "$W exists"; exit 2; }
"$PY" -c "import sys, matplotlib, numpy; assert (sys.version.split()[0], matplotlib.__version__, numpy.__version__) \
== ('3.12.2', '3.11.2', '2.5.4'), (sys.version, matplotlib.__version__, numpy.__version__)" \
    || { echo "not the recorded environment"; exit 2; }
[ -z "$(git -C "$REPO" status --porcelain)" ] || { echo "the repository is not clean"; exit 2; }
sha() { shasum -a 256 "$1" | cut -d' ' -f1; }
want() { [ "$(sha "$1")" = "$2" ] || { echo "$1: sha256 $(sha "$1") != $2"; exit 3; }; }
mkdir -p "$W/old"; W=$(cd "$W" && pwd)
git -C "$REPO" show 7fc9ce93fcbcf4014055fb167fb0f04ab2a78b2c:publication/release/figs/make_figs.py > "$W/old/make_figs.py"
want "$W/old/make_figs.py" 4e18c26681fc86dcfef2861c7c0126aa2df4839376d967b18f08a7d77664ee67
FIG2=57f3cc601281950cf9251b04a627efa3e0d803eca6620178839c48f9d4b0782a
FIG3=e9d1bb01fc79e061b95b6e058a2aa2a03275429db5c4531b5e3d9ec63d65fa93
arm() {  # arm <a|c> <inputs dir> <reference RUN-fig1.txt> <old fig1 sha256>
    local A=$1 IN=$2 REF=$3 OLD=$4
    mkdir -p "$W/$A/in"; cd "$W/$A"
    sed -n '/^inputs:/,/^outputs:/p' "$REF" | grep '  in/' | while read -r d p; do
        cp "$IN/${p#in/}" in/; want "$p" "$d"; done
    [ "$(ls in | wc -l | tr -d ' ')" = "$(grep -c '  in/' "$REF")" ] || { echo "$A: input count"; exit 3; }
    if [ "$A" = a ]; then
        for f in chain.json reduce.json combination/combination.json outA/SHA256SUMS; do
            cmp -s "in/$(basename "$f")" "$REPO/$P/run2/g2r/$f" || { echo "a: in/$(basename "$f") != committed $f"; exit 3; }
        done
    fi
    ARGS=(--npz in/fig_arrays.npz --reduce "$W/$A/in/reduce.json" --make-figs "$MF" --values in/uqmedian.tex --tmp tmp
          --outdir out --cov in/cov2d_Q_205.npz --s5-npz in/production_cov.npz --playlist-npz in/playlist_term.npz
          --combination in/combination.json --budget in/budget_Q.json --step-a-sums in/SHA256SUMS
          --arm refined --pins-json in/pins.json)
    "$PY" -I "$REPO/2d-unfolding/re2/partc/re2c_fig1.py" "${ARGS[@]}" > fig1_run.log 2>&1 || { echo "$A: re2c_fig1.py rc $?"; exit 4; }
    {
        echo "# Fig. 1 version B', run_bprime.sh arm $A, $(date -u +%FT%TZ), host $(hostname)"
        echo "env: $("$PY" -c "import sys, matplotlib, numpy; print('python', sys.version.split()[0], 'matplotlib', \
matplotlib.__version__, 'numpy', numpy.__version__)") ($PY)"
        echo "commit: $(git -C "$REPO" rev-parse HEAD) clean=$([ -z "$(git -C "$REPO" status --porcelain)" ] && echo yes || echo no)"
        echo "script: $(sha "$REPO/2d-unfolding/re2/partc/re2c_fig1.py")  2d-unfolding/re2/partc/re2c_fig1.py"
        echo "argv: python -I re2c_fig1.py ${ARGS[*]}"
        echo "inputs:"; for f in in/*; do echo "$(sha "$f")  $f"; done
        echo "$(sha "$MF")  publication/release/figs/make_figs.py"
        echo "outputs:"; for f in out/*; do echo "$(sha "$f")  $f"; done
        echo "$(sha tmp/fig_arrays_q.npz)  tmp/fig_arrays_q.npz"
    } > RUN-fig1.txt
    want out/fig2_joint_localization.pdf $FIG2; want out/fig3_generator_context.pdf $FIG3
    "$PY" -I "$HERE/fig1_identity.py" --arrays tmp/fig_arrays_q.npz --values in/uqmedian.tex --old "$W/old/make_figs.py" \
        --new "$MF" --outdir identity --old-fig1 "$OLD" --new-fig1 "$(sha out/fig1_validation.pdf)" --fig2 $FIG2 \
        --fig3 $FIG3 > identity.log 2>&1 || { rc=$?; grep -v 'timestamp seems very low' identity.log; echo "$A: identity rc $rc"; exit 5; }
    grep -v 'timestamp seems very low' identity.log
}
arm a "$INA" "$REPO/$P/fig1/route-a/RUN-fig1.txt" 1ead58a2223ecf88f3de505d7cbcca76ab306af49814ea7c9d50ec0f2c373e0c
arm c "$INC" "$REPO/$P/fig1/control/RUN-fig1.txt" 71a2ea488ab758a466d40b7d5a7a061ebd95b1cdb90a79427c3da968238b6427
cd "$W"
{
    echo "# run_bprime.sh $(sha "$HERE/run_bprime.sh"), fig1_identity.py $(sha "$HERE/fig1_identity.py")"
    echo "old make_figs.py: $(sha old/make_figs.py) (7fc9ce93:publication/release/figs/make_figs.py)"
    for A in a c; do echo "$A: $(sha $A/out/fig1_validation.pdf)  fig1_validation.pdf; identity $(tail -1 $A/identity.log)"; done
} | tee RUN-bprime.txt
echo "BPRIME PASS: both arms drawn, fig2 and fig3 unchanged, identity PASS in both; no cluster access"
