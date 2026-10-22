# RE-1 run 2: shared settings, sourced by each job with the deploy path in $C (absolute; set at submission).
# Inputs are the existing ME-FHC products every deliverable was made from (RE1-AMENDMENT-DECLARATION.md §3).
B=/pscratch/sd/j/josephrb/methods-paper/re1-20261022
O=$B/out
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold
OMNI2D=$A/2d-unfolding/runEventLoopOmniFold_MEFHC.root;       OMNI2D_SHA=43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df
FLUX=$A/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root; FLUX_SHA=d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316
OMNI3D=$A/3d-unfolding/runEventLoopOmniFold_MEFHC_3D.root;    OMNI3D_SHA=7db0c27c8ba25395285fbac237700c390fedd43314c485af1c8b01f86e4dd4bd
OMNI4D=$A/nd-unfolding/runEventLoopOmniFold_4D_MEFHC.root;    OMNI4D_SHA=5a1a7b9df2bb07bcc00b710a5b0d3d553bd7f76bbe8306004e43aba1c7179a40
NPZ5D=$A/nd-unfolding/of_inputs_5d.npz;                       NPZ5D_SHA=07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f
BKG5D=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz; BKG5D_SHA=2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955
P5=/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data/data_b-_j-.npz; P5_SHA=fb5cc6798b97b5902ad8f0fecbc49990271f7772f98d3063c1dc8596340e680c

re1_preflight() {  # the deploy is a clean checkout at the declared sha, and every pinned input matches
    [ -n "${C:-}" ] && [ -n "${RE1_SHA:-}" ] || { echo "[re1] C and RE1_SHA must be exported"; exit 2; }
    [ "$(git -C "$C" rev-parse HEAD)" = "$RE1_SHA" ] || { echo "[re1] deploy HEAD is not $RE1_SHA"; exit 2; }
    [ -z "$(git -C "$C" status --porcelain)" ] || { echo "[re1] deploy is not clean"; exit 2; }
    source "$A/setup_salloc_env.sh"   # the root_6_28 environment (set -u would abort its activation)
    set -u
    export TMPDIR=$B/tmp PYTHONUNBUFFERED=1
    mkdir -p "$TMPDIR" "$O" "$B/logs"
}

re1_check() {  # re1_check <path> <sha256>
    local got; got=$(sha256sum "$1" | cut -d' ' -f1)
    [ "$got" = "$2" ] || { echo "[re1] $1 sha256 $got != $2"; exit 4; }
}

# Every Python run goes through the OI-136 guard with this deploy as the only admitted tree.
re1_py() {  # re1_py <label> <script relative to $C> [args...]
    local label=$1 script=$2; shift 2
    python "$C/nd-unfolding/mnv_guarded_run.py" --expect-root "$C" --label "$label" \
        --inventory "$O/inventory/$label.jsonl" -- "$C/$script" "$@"
}
