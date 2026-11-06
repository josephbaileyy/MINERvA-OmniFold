#!/bin/bash
# REF-C2C1 step two, stage 3a: the reported cells (REF-C2C1-BINDING-2.md ruling section, the insertion ruled
# 2026-11-06, #825 at main 1aa805b5; code at M = 77d76cfc), on a login node, 0 node-h, under the binding's fixed
# conditional sequence. From a fresh clean clone at M (porcelain --ignored 0, the binding's 8 blobs):
#   ref_c2c1_read.py cells --out $R/cells.root
# in root_6_28. write_cells reads only the publication's precision ROOT (config.json publication.path, sha256
# 6c6dce72...), as an O_NOATIME copy staged into $R/cells-inputs/ under read_guards, and no unit product. The new read
# directory $R must not exist; 3b's read later stages into $R/inputs/. The publication is stat'd (no read) before and
# after: a moved atime is a STOP. The fence is a recorded line (the director's ruling of 2026-11-06 for guarded readers).
# Porcelain --ignored before and after. Writes only under $R (cells.root, cells-inputs/, cells.log, cells.json,
# cells.done, this script's copy) and $O/deploy-cells. No set -u. Launched from a /dev/shm copy of itself ($1), which it
# deletes at exit.
SELF=$1
O=/pscratch/sd/j/josephrb/ref-c2c1-20261106
R=$O/read
D=$O/deploy-cells
M=77d76cfc2d621f8faa010b75006811868494652a
PUB=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
case "$(hostname)" in login*) ;; *) bail ;; esac
[ -d "$O" ] && [ ! -e "$R" ] && [ ! -e "$D" ] && [ -x "$PY" ] && [ -f "$PUB" ] || bail
mkdir -p "$R" || bail
exec > "$R/cells.log" 2>&1
finish() { echo "ref-c2c1 cells rc=$1"; date -u +%FT%TZ; echo "$1" > "$R/cells.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "cells script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$R/refc2c1_cells_login.sh"
echo "fence, recorded: squeue -u josephrb at $(date -u +%FT%TZ):"; squeue -u josephrb -h -o '%i|%j|%T|%M|%l' | sed 's/^/  /'
pb=$(stat -c '%U %a %X %s %n' "$PUB"); echo "publication before (stat): $pb"
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$R/clone-cells.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$M:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
128b4e00505f82153d1d400a482b7b1a5a3d56be 2d-unfolding/ref_c2c1/ref_c2c1.py
e51367aa3d9d68b8c89f76cd7f556c70bd4a226f 2d-unfolding/ref_c2c1/ref_c2c1_read.py
96dbbaa223a3dec4ceba80686f07721e87ec9045 2d-unfolding/ref_c2c1/config.json
0d2f1a2445fe22130be94635cabb280837be4edb 2d-unfolding/ref_c2c1/test_ref_c2c1.py
0e80efd2d927390e4360cf10134e5b74e7554deb 2d-unfolding/ref_c2c1/ref_c2c1_mutation.py
f2711d4ea81141205f6ef8a450707051713faf20 2d-unfolding/ref_c2c1/run_suite.py
f4dbaf1fe57bcf4ab0f128d70c1725aa64ae8d29 2d-unfolding/ref_c2c1/run_tests.sh
990ec7894a982709298ce3550ffa3fa1e73fe1b9 2d-unfolding/ref_c2c1/test_run_suite.py
BLOBS
echo "bound blobs: 8 checked, $bad mismatches"; [ "$bad" -eq 0 ] || { echo "STOP: bound bytes"; finish 9; }
(
  eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
  conda activate "$HOME/.conda/envs/root_6_28" || { echo "STOP: activation failed"; exit 2; }
  export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
  echo "interpreter $PY: $("$PY" -c 'import sys; print(sys.version.replace(chr(10), " "))')"
  cd "$D" && nice -n 19 "$PY" -B 2d-unfolding/ref_c2c1/ref_c2c1_read.py cells --out "$R/cells.root" > "$R/cells.json"
)
rc=$?
echo "cells rc=$rc; stdout: $(cat "$R/cells.json")"
[ -s "$R/cells.root" ] && echo "cells.root sha256 $(sha256sum "$R/cells.root" | cut -d' ' -f1) bytes $(stat -c %s "$R/cells.root")"
echo "staged: $(ls "$R/cells-inputs" 2>/dev/null | tr '\n' ' ')"
pa=$(stat -c '%U %a %X %s %n' "$PUB"); echo "publication after (stat): $pa"
[ "$pa" = "$pb" ] && echo "publication: atime not moved" || { echo "STOP: the publication's stat changed"; rc=8; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
git -C "$D" status --porcelain --ignored | head -10
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
finish $rc
