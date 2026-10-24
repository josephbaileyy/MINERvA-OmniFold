# RE-2 part B: shared settings, sourced by each job with the deploy in $C and the declared sha in $RE2_SHA.
# It sources part A's re2_env.sh (inputs, digests, re2_preflight, re2_check) unchanged, then sets part B's own
# namespace, tables and checks (RE2-DECLARATION-B.md §4). The CV omnifile and the 10 laterals are read from the
# copies the DTN preflight staged on pscratch ($O/inputs), whose digests are the declared CFS files' own; a compute
# node reads CFS through DVS at ~10 MB/s (RE2-J0-REPORT.md D1).
source "$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/launch/re2_env.sh"
O=$B/partb
RUNS=$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partb_runs.tsv
JOBS=$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/partb_jobs.tsv
CFS_CV=$CV
CFS_ACT=/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-inputs-20261012/active_universe_5d_standard_merged
export CV=$O/inputs/runEventLoopOmniFold_MEFHC.root      # staged copy of $CFS_CV (same sha256, CV_SHA)
export ACT=$O/inputs/laterals                            # staged copies of the 10 active laterals
export P
STATS=$O/preflight/inputs.stat     # "sha256 size mtime inode path", written on a DTN by re2b_dtn_hash.sh
ROOM=84.5245                       # 90 - J0's 5.4755 (RE2-J0-REPORT.md §1)
EXCLUDE=nid004074,nid004078        # the period-test nodes whose replicas timed out (RE2-PLAN §4.2)
declare -A UNI_SHA_OF=([uni]=220c479efa9751116fd396ea32398de5631f8b755e6b16a94ce090975f011418)

re2b_limit() {  # re2b_limit <job>: the declared limit from partb_jobs.tsv
    awk -F'\t' -v j="$1" 'NR > 1 && $1 == j {print $10}' "$JOBS"
}

re2b_stat_check() {  # re2b_stat_check <path> <declared sha256>
    # A DTN-hashed input (RE2-DECLARATION-B.md §4.2): its recorded sha256 must be the declared one; then size,
    # mtime and inode (`stat -c '%s %Y %i'`; the device number differs by mount and is not compared) must equal
    # the record. Any difference forces a full re-hash here, and a hash mismatch refuses the job.
    local path=$1 want=$2 rec got
    rec=$(awk -v p="$path" '$5 == p' "$STATS")
    [ "$(printf '%s\n' "$rec" | grep -c .)" = 1 ] || { echo "[re2b] $path: not exactly one row in $STATS"; exit 5; }
    set -- $rec
    [ "$1" = "$want" ] || { echo "[re2b] $path: recorded sha256 $1 != declared $want"; exit 5; }
    if [ "$(stat -c '%s %Y %i' "$path")" = "$2 $3 $4" ]; then
        echo "[re2b] $path: stat matches the DTN record; no re-hash"
    else
        echo "[re2b] $path: stat $(stat -c '%s %Y %i' "$path") != recorded $2 $3 $4; re-hashing"
        got=$(sha256sum "$path" | cut -d' ' -f1)
        [ "$got" = "$want" ] || { echo "[re2b] $path sha256 $got != $want; refused"; exit 4; }
        echo "[re2b] $path: re-hash matches"
    fi
}

LAT_SUMS_SHA=73775251f377a35b86c5d9433d1db63d65267525b9261f773064a1e9d17764f6   # $CFS_ACT/SHA256SUMS
LATERALS="BeamAngleX_0 BeamAngleX_1 BeamAngleY_0 BeamAngleY_1 MuonResolution_0 MuonResolution_1
          Muon_Energy_MINERvA_0 Muon_Energy_MINERvA_1 Muon_Energy_MINOS_0 Muon_Energy_MINOS_1"
re2b_lateral_sha() {  # re2b_lateral_sha <file name>: its row of the CFS SHA256SUMS (whose own digest is pinned)
    awk -v f="$1" '$2 == f {print $1}' "$CFS_ACT/SHA256SUMS"
}

re2b_check_inputs() {  # re2b_check_inputs <job class>: what that job's runs read
    re2_check "$MC" "$MC_SHA"
    case "$1" in
        J1|J4|J6) re2b_stat_check "$CV" "$CV_SHA" ;;
        J2) re2b_stat_check "$UNI" "${UNI_SHA_OF[uni]}"; re2_check "$FLUXU" "$FLUXU_SHA" ;;
        J7) re2b_stat_check "$UNI" "${UNI_SHA_OF[uni]}"; re2_check "$FLUXU" "$FLUXU_SHA"
            re2b_stat_check "$CV" "$CV_SHA" ;;
        J3) re2_check "$CFS_ACT/SHA256SUMS" "$LAT_SUMS_SHA"
            local lat f
            for lat in $LATERALS; do
                f=runEventLoopOmniFold_5D_MEFHC_active_$lat.root
                re2b_stat_check "$ACT/$f" "$(re2b_lateral_sha "$f")"
            done ;;
        J8) local per
            for per in ALL PA PB PC; do
                re2_check "$P/inputs/runEventLoopOmniFold_$per.root" "${PU_OMNI_SHA[$per]}"
                re2_check "$P/flux/runEventLoopMC_$per.root" "${PU_FLUX_SHA[$per]}"
            done ;;
        *) echo "[re2b] no input check for $1"; exit 2 ;;
    esac
}
# The period inputs (sbatch_period_unfold.sh:28-39); part A's PU_SHAS holds ALL and PA only.
declare -A PU_OMNI_SHA=([ALL]=a7a4bcb359ddb4764e0baf9922ab35e6bfbb3e4e2fd9b03d152514f02ea6b3e9
    [PA]=1d2f5b3712169c2eeca0739a9e391ea05b547153444a23a06a0b7cffa93ac948
    [PB]=200fd1dd18df3f907443caf1217ffbfe580b24e638cbbfff333d39cecfc85004
    [PC]=eedbb5dc0f8bf6d1314e36ccc8f08760f2e59687988db55974ee54d377cc9224)
declare -A PU_FLUX_SHA=([ALL]=e3dc9e63bc8db07ab545cee6d8b227cdaa7f8249c657cc1a60119020dd6a86de
    [PA]=927f5af214b15935c1093b83c7e703730b8a5993b5e8f43f60a56eb8f07963fe
    [PB]=c64637d58961c4681f83611ab79f057f741329398cde00df175fac28dad15f0d
    [PC]=95c45a5f91f1fc356bfde74b463e1a24a70d698d8693a766773a6a37c3bdfafc)
