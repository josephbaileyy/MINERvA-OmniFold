#!/bin/bash
# RPD part 2: test_fd_rpd (ROOT tests included), then part 2 section 2's other two suites, on a login node, from a
# /dev/shm clone of the head (the director's permission of 2026-11-03). 0 node-h, no job (sbatch/srun/salloc shadowed
# by refusing shims), no pscratch or CFS read: root_6_28 is activated by prefix from $HOME, TMPDIR is the clone's
# directory. No set -u (it aborts the activation). The clone is deleted at the end.
# Run as: ssh saul.nersc.gov bash -s <sha> < root_tests_login.sh
H=$1
case "$H" in [0-9a-f]*) [ ${#H} = 40 ] || { echo "STOP: need a 40-hex sha"; exit 9; } ;; *) echo "STOP: need a sha"; exit 9 ;; esac
echo "node $(hostname)"
date -u +%FT%TZ
df -Pk /dev/shm | awk 'NR == 2 { print "dev/shm free GiB " int($4 / 1048576) }'
[ "$(df -Pk /dev/shm | awk 'NR == 2 { print $4 }')" -gt 8388608 ] || { echo "STOP: under 8 GiB free in /dev/shm"; exit 9; }
W=$(mktemp -d /dev/shm/rpd-root-XXXXXX) || exit 9
echo "clone dir $W"
cleanup() { cd /; case "$W" in /dev/shm/rpd-root-??????) rm -rf -- "$W" ;; esac; [ -e "$W" ] && echo "clone NOT deleted" || echo "clone deleted"; }
trap cleanup EXIT
echo "squeue --me before:"; squeue --me -h -o "%i %j %T" ; echo "squeue rc=$?"
git clone -q --depth 1 --branch code/rpd-part2-20261102 https://github.com/josephbaileyy/MINERvA-OmniFold.git "$W/repo" \
  || { echo "STOP: clone failed"; exit 3; }
cd "$W/repo" || exit 9
[ "$(git rev-parse HEAD)" = "$H" ] || { echo "STOP: HEAD $(git rev-parse HEAD) is not $H"; exit 9; }
echo "HEAD $(git rev-parse HEAD)"
echo "porcelain before: [$(git status --porcelain)]"
mkdir "$W/shim" "$W/tmp"
for x in sbatch srun salloc; do printf '#!/bin/sh\necho "REFUSED: %s called" >&2\nexit 97\n' "$x" > "$W/shim/$x"; chmod 755 "$W/shim/$x"; done
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28" || { echo "STOP: activation failed"; exit 2; }
export PATH="$W/shim:$PATH" TMPDIR="$W/tmp" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
echo "python $(command -v python3) $(python3 -V 2>&1); sbatch resolves to $(command -v sbatch)"
python3 -I -B -c "import ROOT, numpy, scipy; print('ROOT', ROOT.gROOT.GetVersion(), 'numpy', numpy.__version__, 'scipy', scipy.__version__)"
python3 -I -B -c "import uproot" 2>&1 | tail -1
cd nd-unfolding/tests || exit 9
rc=0
for suite in test_fd_rpd test_fd_ct_periods test_fd_ct_readers; do
  echo "=== $suite"
  env -u PYTHONPATH python3 -B -m unittest -v $suite > "$W/$suite.log" 2>&1
  r=$?
  cat "$W/$suite.log"
  echo "$suite unittest rc=$r"
  [ $r = 0 ] || rc=$r
done
cd "$W/repo" || exit 9
echo "porcelain after: [$(git status --porcelain)]"
echo "squeue --me after:"; squeue --me -h -o "%i %j %T" ; echo "squeue rc=$?"
date -u +%FT%TZ
exit $rc
