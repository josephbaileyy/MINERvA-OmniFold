# RE-2 J0: shared settings, sourced by each job with the deploy path in $C and the declared sha in $RE2_SHA.
# Inputs are the existing ME-FHC files every 2D product was made from (RE2-DECLARATION.md §3).
B=/pscratch/sd/j/josephrb/2d-closeout-re2-20261023
O=$B/j0
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold
RUNS=$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/j0_runs.tsv
export CV=/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root
CV_SHA=43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df
export MC=$A/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root
MC_SHA=d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316
export UNI=$A/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root
UNI_STAT="171117087867 1783523295 882725391507234642"   # size mtime inode, as Stage C's preflight recorded after its hash 220c479e
export FLUXU=$A/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root
FLUXU_SHA=5eecae84509ba8ededbe8fdee63508d8e36cd057cc0547a940383f80248580eb
export LATBAX0=/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-inputs-20261012/active_universe_5d_standard_merged/runEventLoopOmniFold_5D_MEFHC_active_BeamAngleX_0.root
LATBAX0_SHA=38b9fc307eabd864cd0fd663679b51fb2e6d064672410af6b3cf8b0a7e161ed5
P=/pscratch/sd/j/josephrb/2d-closeout-period-unfold-20261014
export PUALL=$P/inputs/runEventLoopOmniFold_ALL.root PUPA=$P/inputs/runEventLoopOmniFold_PA.root
export PUFALL=$P/flux/runEventLoopMC_ALL.root PUFPA=$P/flux/runEventLoopMC_PA.root
PU_SHAS="a7a4bcb359ddb4764e0baf9922ab35e6bfbb3e4e2fd9b03d152514f02ea6b3e9 1d2f5b3712169c2eeca0739a9e391ea05b547153444a23a06a0b7cffa93ac948 e3dc9e63bc8db07ab545cee6d8b227cdaa7f8249c657cc1a60119020dd6a86de 927f5af214b15935c1093b83c7e703730b8a5993b5e8f43f60a56eb8f07963fe"

re2_preflight() {  # the deploy is a clean checkout at the declared sha
    [ -n "${C:-}" ] && [ -n "${RE2_SHA:-}" ] || { echo "[re2] C and RE2_SHA must be exported"; exit 2; }
    [ "$(git -C "$C" rev-parse HEAD)" = "$RE2_SHA" ] || { echo "[re2] deploy HEAD is not $RE2_SHA"; exit 2; }
    [ -z "$(git -C "$C" status --porcelain)" ] || { echo "[re2] deploy is not clean"; exit 2; }
    source "$A/setup_salloc_env.sh"   # root_6_28 (set -u would abort its activation)
    set -u
    export TMPDIR=$B/tmp PYTHONUNBUFFERED=1
    mkdir -p "$TMPDIR" "$O/out" "$O/logs" "$O/inventory"
}

re2_check() {  # re2_check <path> <sha256>
    local got; got=$(sha256sum "$1" | cut -d' ' -f1)
    [ "$got" = "$2" ] || { echo "[re2] $1 sha256 $got != $2"; exit 4; }
}

re2_check_inputs() {  # every input the job's runs read
    re2_check "$CV" "$CV_SHA"; re2_check "$MC" "$MC_SHA"; re2_check "$FLUXU" "$FLUXU_SHA"
    [ "$(stat -c '%s %Y %i' "$UNI")" = "$UNI_STAT" ] || { echo "[re2] universe omnifile size/mtime/inode changed"; exit 4; }
    local i=0 f
    for f in "$PUALL" "$PUPA" "$PUFALL" "$PUFPA"; do i=$((i + 1)); re2_check "$f" "$(echo $PU_SHAS | cut -d' ' -f$i)"; done
}
