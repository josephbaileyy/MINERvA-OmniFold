# COV2D-G2R jobs: shared settings (addendum J1), sourced by each job and by the submit script, with the deploy in $C (a
# clean checkout at $M, the commit J1 binds). COV2D's own settings are reused unchanged ($A, $UNI, $MC, $FLUXU, $PY310,
# the pinned MAT environment); only the namespace is this lane's.
# Test hooks: G2R_O (the namespace) and G2R_TEST_STUB (a directory standing in for $A, $PY310 and COV2D's namespace).
# Both are refused on any NERSC machine (NERSC_HOST is set on its login and compute nodes), so neither can reach a job.
if [ -n "${NERSC_HOST:-}" ] && { [ -n "${G2R_O:-}" ] || [ -n "${G2R_TEST_STUB:-}" ]; }; then
    echo "[g2r] G2R_O or G2R_TEST_STUB is set on $NERSC_HOST: test hooks never run here"; exit 2
fi
COV2D_O=${G2R_O:-/pscratch/sd/j/josephrb/cov2d-g2r-20261112}
source "$C/2d-unfolding/cov2d/jobs/cov2d_env.sh"               # sets O=$COV2D_O
GJ=$C/2d-unfolding/cov2d/g2r/jobs/g2r_jobs.py
export MAP=$O/prepare/g2r_map.npz
COV2D_RUN=/pscratch/sd/j/josephrb/cov2d-run-20261104           # COV2D's namespace: the tunes' realizations (read only)
if [ -n "${G2R_TEST_STUB:-}" ]; then
    A=$G2R_TEST_STUB/A PY310=$G2R_TEST_STUB/py310 COV2D_RUN=$G2R_TEST_STUB/cov2d-run
    export UNI=$A/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root
    export MC=$A/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root
    export FLUXU=$A/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root
fi
PRE=$O/deploy-pre                                              # the environment test's pre-patch deploy, at PRE_M
# P5's per-playlist omnifiles in hadd order (stageB/diagnostics/p5/sbatch_p5.sh), for the prepare's block sizes
P5_BLOCKS=""
for p in 1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P; do P5_BLOCKS="$P5_BLOCKS $A/2d-unfolding/runEventLoopOmniFold_${p}_universes_full.root"; done

g2r_data_dir() {  # a point's realization directory (COV2D's: AR23's rerun, A2, is AR23-a2); the data point has none
    case "$1" in G18) echo "$COV2D_RUN/pseudo/G18/b" ;; AR23) echo "$COV2D_RUN/pseudo/AR23-a2/b" ;; data) echo "" ;;
        *) echo "[g2r] unknown point $1" >&2; return 2 ;; esac
}

g2r_deploy_ok() {  # g2r_deploy_ok <dir> <commit>: a clean checkout at the commit
    [ "$(git -C "$1" rev-parse HEAD 2>/dev/null)" = "$2" ] && [ -z "$(git -C "$1" status --porcelain)" ]
}

g2r_preflight() {  # COV2D's preflight without its staging-record check (G2R reads no staged copy)
    [ -n "${C:-}" ] && [ -n "${M:-}" ] || { echo "[g2r] C and M must be exported"; exit 2; }
    g2r_deploy_ok "$C" "$M" || { echo "[g2r] deploy $C is not a clean checkout at $M"; exit 2; }
    "$PY310" -B -c "import sys; sys.path.insert(0, '$C/nd-unfolding'); import fd_rpd_inputs as r; r.run_check_mat_setup(None)" \
        || { echo "[g2r] the MAT setup scripts are not the pinned ones"; exit 7; }
    source "$A/setup_salloc_env.sh" > /dev/null 2>&1   # root_6_28 + MAT (set -u would abort its activation)
    set -u
    export TMPDIR=$O/tmp/${SLURM_JOB_ID:-local} PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
    export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1   # as part B and COV2D
    unset LOKY_MAX_CPU_COUNT
    mkdir -p "$TMPDIR" "$O/out" "$O/logs" "$O/inventory"
    python -B -c "import sys; sys.path.insert(0, '$C/nd-unfolding'); import fd_rpd_inputs as r, json; \
print(json.dumps(r.mat_environment()))" > "$O/logs/mat-${SLURM_JOB_ID:-local}.json" \
        || { echo "[g2r] not the pinned MAT environment"; exit 7; }
}

g2r_slurm_ok() {  # g2r_slurm_ok <limit>: QOS regular and the job's TimeLimit
    local info
    info=$(scontrol show job "$SLURM_JOB_ID")
    grep -q "QOS=regular" <<<"$info" || { echo "[g2r] QOS is not regular"; exit 2; }
    grep -q "TimeLimit=$1 " <<<"$info" || { echo "[g2r] TimeLimit is not $1"; exit 2; }
}
