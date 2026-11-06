# COV2D jobs: shared settings, sourced by each job with the deploy in $C (a clean checkout at $M, the commit binding 2
# names).
# The staged $CV and laterals (staging record inputs.stat, sha256 3614ebad...; the director's re-hash rule) and the
# pseudo-data files are checked by cov2d_jobs.py check before any run; $UNI is stat-checked against part B's record.
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold                # the shared checkout: $UNI, flux files, the MAT build
O=${COV2D_O:-/pscratch/sd/j/josephrb/cov2d-run-20261104}   # this lane's namespace (tests set COV2D_O)
STAGE=/pscratch/sd/j/josephrb/cov2d-inputs-20261104
export CV=$STAGE/runEventLoopOmniFold_MEFHC.root ACT=$STAGE/laterals
STATS=$STAGE/stage/inputs.stat
STATS_SHA=3614ebadf9cb1b95340b80129e6e743e780a7979cf6392d9d64d7b56ffa02adf
export UNI=$A/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root
export MC=$A/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root
export FLUXU=$A/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root
CFSACT=/global/cfs/cdirs/m3246/josephrb/2d-closeout-stageC-inputs-20261012/active_universe_5d_standard_merged   # the CFS originals
export K2A=/pscratch/sd/j/josephrb/cov2d-2a/writer_control.root   # (2a)'s kept file, re-checked (7eb39088) by the pilot
PY310=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
CJ=$C/2d-unfolding/cov2d/jobs/cov2d_jobs.py
pseudo_dir() {  # a truth's pseudo-data directory. AR23 reruns into a new one (A2): its first run, STOP #2, stays in pseudo/AR23
    case "$1" in AR23) echo "$O/pseudo/AR23-a2" ;; *) echo "$O/pseudo/$1" ;; esac
}

cov2d_preflight() {  # a clean deploy at $M; the pinned MAT environment (RPD's binding 2 A1 standard); in-job resets
    [ -n "${C:-}" ] && [ -n "${M:-}" ] || { echo "[cov2d] C and M must be exported"; exit 2; }
    [ "$(git -C "$C" rev-parse HEAD)" = "$M" ] && [ -z "$(git -C "$C" status --porcelain)" ] \
        || { echo "[cov2d] deploy $C is not a clean checkout at $M"; exit 2; }
    "$PY310" -B -c "import sys; sys.path.insert(0, '$C/nd-unfolding'); import fd_rpd_inputs as r; r.run_check_mat_setup(None)" \
        || { echo "[cov2d] the MAT setup scripts are not the pinned ones"; exit 7; }
    source "$A/setup_salloc_env.sh" > /dev/null 2>&1   # root_6_28 + MAT (set -u would abort its activation)
    set -u
    # reset everything a submitting shell or the setup script may have set (E3: TMPDIR leaked through sbatch)
    export TMPDIR=$O/tmp/${SLURM_JOB_ID:-local} PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
    export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1   # as part B (re2_env.sh)
    unset LOKY_MAX_CPU_COUNT
    mkdir -p "$TMPDIR" "$O/out" "$O/logs" "$O/inventory"
    python -B -c "import sys; sys.path.insert(0, '$C/nd-unfolding'); import fd_rpd_inputs as r, json; \
print(json.dumps(r.mat_environment()))" > "$O/logs/mat-${SLURM_JOB_ID:-local}.json" \
        || { echo "[cov2d] not the pinned MAT environment"; exit 7; }
    [ "$(python -B -c "import sys; sys.path.insert(0, '$C/2d-unfolding/cov2d/jobs'); import cov2d_jobs as j; print(j.noatime_sha256('$STATS'))")" \
        = "$STATS_SHA" ] || { echo "[cov2d] the staging record is not 3614ebad..."; exit 4; }
}
