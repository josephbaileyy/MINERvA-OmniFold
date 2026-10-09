#!/usr/bin/env bash
# G12 (PRD release audit ea939701): regenerate the release's sufficient inputs from DURABLE copies only, with the
# frozen extractor and frozen code unchanged. Run on a Perlmutter login node (bwrap, user namespaces).
#
# The adapter is a reconstructed directory layout, not a code change: bubblewrap makes the whole host read-only,
# mounts an EMPTY tmpfs over the live campaign directory /pscratch/sd/j/josephrb/s5p-20260926 (so nothing on the
# purgeable original can be read), and binds the durable copies at their original absolute paths. The frozen design
# files, the frozen code and the extractor therefore see exactly the paths they recorded.
#
#   bash reproduce_from_durable.sh setup <dir with deploy-e9372b75.tgz, deploy-51648245.tgz, recovery-union-links.tsv.gz,
#                                          resolution-design.json (git: docs/orchestration/state/s5p/recovery/phaseC/)>
#   bash reproduce_from_durable.sh run frozen|recovery-union
#   bash reproduce_from_durable.sh figs        # the figure arrays: the exporter's own options point at durable copies
#
# For the figure arrays no sandbox is needed: export_fig_arrays.py takes --analysis-root/--genfig/--mnvtune5d, so a
# small directory of links to the durable sources (the CFS shutdown-stage copies, the home evidence epoch, git) is
# the whole adapter. Its code root is a clean fetch of the export commit 556d6dde.
set -euo pipefail
G=$(readlink -f "${G12_ROOT:-$HOME/g12-20261008}")   # real path: bwrap will not mkdir through a symlinked home
S=/pscratch/sd/j/josephrb/s5p-20260926
ARCH=/global/cfs/cdirs/m3246/josephrb/s5p-archive-20261006                        # s5p product archive (CFS)
PRES=/global/cfs/cdirs/m3246/josephrb/prd-release-preservation-20261008/pscratch/sd/j/josephrb/s5p-20260926
EXTRACTOR=/global/cfs/cdirs/m3246/josephrb/prd-release-preservation-20261008/pscratch/sd/j/josephrb/pub-release-20261006/tools/extract_inference_sufficient.py
EXTRACTOR_SHA=6ff1d6df7a9a2e61a27b548af4ebf68e36bec6066ed330dcd910c17193c32aea
RD_SHA=f93bdb88d08316040a89ee983810b1ca19ab1d7367e769544587f45856dfafbe   # = the RC4 union manifest's design_sha256

case "${1:-}" in
  setup)
    IN=$2; mkdir -p "$G"/deploy-e9372b75 "$G"/deploy-51648245 "$G"/union "$G"/out
    tar -xzf "$IN/deploy-e9372b75.tgz" -C "$G/deploy-e9372b75"     # git archive e9372b75 (frozen design deploy)
    tar -xzf "$IN/deploy-51648245.tgz" -C "$G/deploy-51648245"     # git archive 51648245 (recovery-union deploy)
    gzip -dc "$IN/recovery-union-links.tsv.gz" | tail -n +2 | while IFS=$'\t' read -r rel target; do
      mkdir -p "$G/union/$(dirname "$rel")"; ln -s "$target" "$G/union/$rel"      # the original link farm, verbatim
    done
    cp "$IN/resolution-design.json" "$G/resolution-design.json"          # committed after 51648245 (11a266c6)
    /usr/bin/python3.11 -m venv "$G/venv"
    "$G/venv/bin/pip" install -q numpy==1.26.4 scipy==1.16.3       # the RC4-tested Linux versions
    "$G/venv/bin/pip" freeze > "$G/venv-freeze.txt"
    ;;
  run)
    group=$2
    [ "$(sha256sum "$EXTRACTOR" | cut -d' ' -f1)" = "$EXTRACTOR_SHA" ] || { echo "extractor digest mismatch"; exit 3; }
    [ "$(sha256sum "$G/resolution-design.json" | cut -d' ' -f1)" = "$RD_SHA" ] || { echo "resolution-design digest mismatch"; exit 3; }
    if [ "$group" = frozen ]; then
      deploy=$S/deploy/e9372b75; design=docs/orchestration/state/s5p/prod/design.json; label=frozen
    else   # the label the original union extraction recorded in its manifest
      deploy=$S/deploy/51648245; design=$S/recovery/resolution-design.json; label="recovery-union (a), report-only"
    fi
    o="$G/out/$group${OUT_SUFFIX:-}"; mkdir -p "$o"     # OUT_SUFFIX: keep repeated runs (e.g. a BLAS-thread test) apart
    bwrap --ro-bind / / --dev /dev --proc /proc --tmpfs "$S" \
      --ro-bind "$ARCH/runs/prod" "$S/runs/prod" \
      --ro-bind "$PRES/runs/s2" "$S/runs/s2" --ro-bind "$PRES/runs/s3" "$S/runs/s3" --ro-bind "$PRES/runs/s3v" "$S/runs/s3v" \
      --ro-bind "$ARCH/stage3" "$S/stage3" \
      --ro-bind "$ARCH/gen5d" "$S/gen5d" --ro-bind "$ARCH/gen5d_fluxfix" "$S/gen5d_fluxfix" \
      --ro-bind "$ARCH/recovery/recovery" "$S/recovery/recovery" --ro-bind "$G/union" "$S/recovery/union" \
      --ro-bind "$G/resolution-design.json" "$S/recovery/resolution-design.json" \
      --ro-bind "$G/deploy-e9372b75" "$S/deploy/e9372b75" --ro-bind "$G/deploy-51648245" "$S/deploy/51648245" \
      --bind "$o" "$o" --chdir "$deploy" \
      /usr/bin/time -v "$G/venv/bin/python" "$EXTRACTOR" --deploy "$deploy" --design "$design" \
        --v "$S/stage3/V/V-s3v.npz" --out "$o/inference_sufficient.npz" --group "$label"
    ;;
  figs)
    C=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/fig_products
    E=/global/homes/j/josephrb/evidence/repository-epochs/preparation-2026-09-24-bf34a12c/trunk-baseline/MINERvA-OmniFold
    R=$G/figrepo; L=$G/fig-analysis-root
    if [ ! -d "$R/.git" ]; then
      git init -q "$R" && git -C "$R" fetch -q --depth 1 https://github.com/josephbaileyy/MINERvA-OmniFold \
        556d6dde97c73d446f5d86d3ef31bd9db7ce83ab && git -C "$R" checkout -q FETCH_HEAD
    fi
    mkdir -p "$L/2d-unfolding/minerva_paper_anc" "$L/nd-unfolding/products/5d" "$G/out/figs"
    ln -sfn "$C/2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter.root" "$L/2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter.root"
    ln -sfn "$C/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root" "$L/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root"
    ln -sfn "$R/2d-unfolding/minerva_paper_anc/model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt" "$L/2d-unfolding/minerva_paper_anc/model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt"
    ln -sfn "$C/nd/products/5d/excess_eavail_W.root" "$L/nd-unfolding/products/5d/excess_eavail_W.root"
    ln -sfn "$E/nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root" "$L/nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root"
    set +u   # root_6_28's activate.d scripts reference unset variables
    eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
    conda activate "$HOME/.conda/envs/root_6_28"
    set -u
    cd "$R" && /usr/bin/time -v python3 publication/release/figs/export_fig_arrays.py --code-root "$R" --analysis-root "$L" \
      --genfig "$ARCH/stage7/genfig/3d-unfolding/genie" --mnvtune5d "$ARCH/gen5d/mnvtune_v1_xsec5d.npz" \
      --out "$G/out/figs/fig_arrays.npz"
    ;;
  *) echo "usage: $0 setup <dir> | run frozen|recovery-union | figs" >&2; exit 2 ;;
esac
