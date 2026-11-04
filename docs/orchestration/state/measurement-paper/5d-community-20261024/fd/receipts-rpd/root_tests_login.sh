#!/bin/bash
# RPD part 2: the test suites on a login node, each in the environment its steps run in (FD-RPD-DECLARATION-PART2.md
# sections 2 and 3; binding 2 A1), from a /dev/shm clone of the head. 0 node-h, no job (sbatch/srun/salloc shadowed by
# refusing shims). No set -u (it aborts both activations). The clone is deleted at the end.
#   A. root_6_28 by prefix (stage, verify-staged, check-mat-setup, the readers), asserted MAT-free: test_fd_rpd
#      test_fd_ct_periods test_fd_ct_readers, and test_fd_rpd_mat's ZeroLoops on the staged zero loops (job A's
#      root_6_28 reads) under -I, as the steps run.
#   B. the shared checkout's MAT environment (flux), its six setup scripts digested first (check-mat-setup):
#      test_fd_rpd; mat_environment in flux's own invocation (env -u PYTHONPATH python3 -I -B); and test_fd_rpd_mat
#      whole under -I. The setup scripts are sourced read-only; TMPDIR is re-exported.
# Every suite must end "OK" with nothing skipped. On pscratch it reads the MAT setup and library files and, under $R,
# only the staged copies (re-hashed first by the tests); it writes nothing outside the clone.
# Run as: ssh saul.nersc.gov bash -s <sha> < root_tests_login.sh
H=$1
case "$H" in [0-9a-f]*) [ ${#H} = 40 ] || { echo "STOP: need a 40-hex sha"; exit 9; } ;; *) echo "STOP: need a sha"; exit 9 ;; esac
R=/pscratch/sd/j/josephrb/fd-rpd-20261103
MATENV=/pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh
echo "node $(hostname)"
date -u +%FT%TZ
[ "$(df -Pk /dev/shm | awk 'NR == 2 { print $4 }')" -gt 8388608 ] || { echo "STOP: under 8 GiB free in /dev/shm"; exit 9; }
[ -e "$R/staged/STAGED.json" ] || { echo "STOP: no staging record under $R"; exit 9; }
W=$(mktemp -d /dev/shm/rpd-root-XXXXXX) || exit 9
echo "clone dir $W"
cleanup() { cd /; case "$W" in /dev/shm/rpd-root-??????) rm -rf -- "$W" ;; esac; [ -e "$W" ] && echo "clone NOT deleted" || echo "clone deleted"; }
trap cleanup EXIT
echo "squeue --me before:"; squeue --me -h -o "%i %j %T" ; echo "squeue rc=$?"
git clone -q --depth 1 --branch code/rpd-a1-20261103 https://github.com/josephbaileyy/MINERvA-OmniFold.git "$W/repo" \
  || { echo "STOP: clone failed"; exit 3; }
cd "$W/repo" || exit 9
[ "$(git rev-parse HEAD)" = "$H" ] || { echo "STOP: HEAD $(git rev-parse HEAD) is not $H"; exit 9; }
echo "HEAD $(git rev-parse HEAD)"
echo "porcelain before: [$(git status --porcelain)]"
mkdir "$W/shim" "$W/tmp"
for x in sbatch srun salloc; do printf '#!/bin/sh\necho "REFUSED: %s called" >&2\nexit 97\n' "$x" > "$W/shim/$x"; chmod 755 "$W/shim/$x"; done
T=$W/repo/nd-unfolding/tests

suite() {   # suite <label> <python3 args...>: runs in the current environment, from the tests directory; must end "OK"
  local label=$1; shift
  echo "=== $label: python3 $*"
  (cd "$T" && env -u PYTHONPATH python3 "$@") > "$W/$label.log" 2>&1
  local r=$?
  cat "$W/$label.log"
  [ $r = 0 ] && [ "$(tail -1 "$W/$label.log")" = "OK" ] || { [ $r = 0 ] && r=8; echo "$label: not OK with nothing skipped"; }
  echo "$label unittest rc=$r"
  return $r
}

rc=0
(   # A. root_6_28 by prefix
  eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
  conda activate "$HOME/.conda/envs/root_6_28" || { echo "STOP: activation failed"; exit 2; }
  export PATH="$W/shim:$PATH" TMPDIR="$W/tmp" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 FD_RPD_R="$R"
  echo "A: python $(command -v python3) $(python3 -V 2>&1); PLOTUTILSROOT=[$PLOTUTILSROOT]; sbatch resolves to $(command -v sbatch)"
  [ -z "$PLOTUTILSROOT$MINERVA_PREFIX" ] || { echo "STOP: environment A carries MAT"; exit 2; }
  a=0
  suite A-suites -B -m unittest -v test_fd_rpd test_fd_ct_periods test_fd_ct_readers || a=1
  suite A-zeroloops -I -B -m unittest discover -v -s "$T" -t "$T" -p test_fd_rpd_mat.py -k ZeroLoops || a=1
  exit $a
) || rc=1
(   # B. the shared checkout's MAT environment, its setup scripts digested before they are sourced
  (eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
   conda activate "$HOME/.conda/envs/root_6_28" && env -u PYTHONPATH python3 -I -B "$W/repo/nd-unfolding/fd_rpd_inputs.py" \
     check-mat-setup --r "$R") || { echo "STOP: check-mat-setup refused"; exit 7; }
  source "$MATENV" > "$W/matenv.log" 2>&1
  export PATH="$W/shim:$PATH" TMPDIR="$W/tmp" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 FD_RPD_R="$R"
  echo "B: python $(command -v python3) $(python3 -V 2>&1); PLOTUTILSROOT=[$PLOTUTILSROOT]; MINERVA_PREFIX=[$MINERVA_PREFIX]; sbatch resolves to $(command -v sbatch)"
  echo "B: setup log lines $(wc -l < "$W/matenv.log")"; grep -i "no such file\|error" "$W/matenv.log" | head -5
  b=0
  suite B-test_fd_rpd -B -m unittest -v test_fd_rpd || b=1
  echo "=== B-probe: mat_environment in flux's invocation"
  env -u PYTHONPATH python3 -I -B -c "import json, sys; sys.path.insert(0, '$W/repo/nd-unfolding'); import fd_rpd_inputs as ri; \
e = ri.mat_environment(); print(json.dumps({'mapped_mat_files': e['mapped_mat_files'], 'symlink': e['symlink']}))" \
    || { echo "B-probe: refused"; b=1; }
  suite B-mat -I -B -m unittest discover -v -s "$T" -t "$T" -p test_fd_rpd_mat.py || b=1
  exit $b
) || rc=1
cd "$W/repo" || exit 9
echo "porcelain after: [$(git status --porcelain)]"
echo "squeue --me after:"; squeue --me -h -o "%i %j %T" ; echo "squeue rc=$?"
date -u +%FT%TZ
echo "overall rc=$rc"
exit $rc
