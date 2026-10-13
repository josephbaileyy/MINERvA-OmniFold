#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=7600M
#SBATCH --time=02:00:00
#SBATCH --array=0-12
#SBATCH --output=/pscratch/sd/j/josephrb/2d-closeout-stageB-diag-20261012/p4/out/slurm_%A_%a.out
#SBATCH --error=/pscratch/sd/j/josephrb/2d-closeout-stageB-diag-20261012/p4/out/slurm_%A_%a.err
# Job names must be 2dc_B4_<tag>, so submit 13 single-task jobs (DRAFT: not submitted):
#   TAGS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P ctl1L)
#   for i in $(seq 0 12); do sbatch --job-name=2dc_B4_${TAGS[$i]} --array=$i sbatch_p4.sh; done
#
# P4 G1 census (grant AUTHORIZATION-20261012-2d-closeout-stageB-diagnostics.md, sha256 ac1bce59...).
#   tasks 0-11: PATCHED binary, census ON, production CV configuration, one playlist each
#   task 12   : UNPATCHED copy on 1L (the no-op control at playlist scale; compared to task 7's main output)
# sbatch runs a COPY of this script, so every path is absolute (never BASH_SOURCE / $0).
# No `set -u` before the root_6_28 activation (ADDR2LINE). No comma-carrying --export values.
set -eo pipefail
NS=/pscratch/sd/j/josephrb/2d-closeout-stageB-diag-20261012/p4
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
MAN=$REPO/2d-unfolding/playlist_manifests
PATCHED_SHA=d1a7cf346bed88d60e7edc360ca4836ee46a968dc6a7abd4400e066bc4a9c9e0   # reviewed (REVIEW.md f2cc6aaf)
UNPATCHED_SHA=1ab7525e41c4a16eba728ac29dac8bfdcbfa792cc16bb8ca2ba141a24eb950ae
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P 1L)
T=${SLURM_ARRAY_TASK_ID:?array task}
PL=${PLAYLISTS[$T]}

source $REPO/setup_salloc_env.sh >/dev/null 2>&1
if [ "$T" -eq 12 ]; then
  TAG=ctl1L; BIN=$NS/build/unpatched/runEventLoopOmniFold; WANT=$UNPATCHED_SHA
else
  TAG=$PL; BIN=$NS/build/patched/runEventLoopOmniFold; WANT=$PATCHED_SHA
fi
[ "$SLURM_JOB_NAME" = "2dc_B4_$TAG" ] || { echo "REFUSE: job name '$SLURM_JOB_NAME' != 2dc_B4_$TAG"; exit 2; }
OUT=$NS/out/$TAG
mkdir -p "$OUT"
[ ! -e "$OUT/runEventLoopOmniFold.root" ] || { echo "REFUSE: $OUT already has an output"; exit 2; }
GOT=$(sha256sum "$BIN" | cut -c1-64)
[ "$GOT" = "$WANT" ] || { echo "REFUSE: $BIN sha256 $GOT != $WANT"; exit 2; }
unset MNV101_DUMP_UNIVERSES MNV101_ACTIVE_UNIVERSE MNV101_TRUTH_ONLY MNV101_DISABLE_TRUTH_MISSES \
      MNV101_FULL_PHASE_SPACE MNV101_DUMP_POINTCLOUD MNV101_DUMP_COMPONENTS MNV101_SKIP_SYST \
      MNV101_G1_CENSUS MNV101_G1_CENSUS_SELFTEST
[ "$T" -eq 12 ] || export MNV101_G1_CENSUS=$OUT/g1_census.root

{
  echo "task=$T tag=$TAG playlist=$PL job=$SLURM_JOB_ID node=$(hostname) start=$(date -u +%FT%TZ)"
  echo "bin=$BIN sha256=$GOT"
  echo "script $(sha256sum "$0")"
  sha256sum "$MAN/${PL}_Data.txt" "$MAN/${PL}_MC.txt"
  env | grep '^MNV101_' || true
} > "$OUT/provenance.txt"

cd "$OUT"
rc=0
/usr/bin/time -v "$BIN" "$MAN/${PL}_Data.txt" "$MAN/${PL}_MC.txt" > run.log 2> run.err || rc=$?
echo "rc=$rc end=$(date -u +%FT%TZ)" >> provenance.txt
[ "$rc" -eq 0 ] || exit "$rc"
if [ "$T" -ne 12 ]; then
  [ -s g1_census.root ] || { echo "REFUSE: no census file"; exit 3; }
fi
sha256sum runEventLoopOmniFold.root $( [ -e g1_census.root ] && echo g1_census.root ) >> provenance.txt
