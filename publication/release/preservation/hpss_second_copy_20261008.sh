#!/usr/bin/env bash
# HPSS second copy of the s5p product archive (2.3 GB) and the adopted z-cv.npz (0.9 GB), corrections record G9;
# Joseph authorized it 2026-10-08. Run on a Perlmutter login node (hsi/htar). The CFS sources are only read; the
# verification streams each object back from HPSS and compares sha256 with the source checksums (no local copy).
#
#   bash hpss_second_copy_20261008.sh put      # htar the archive (with CRCs), hsi put z-cv.npz
#   bash hpss_second_copy_20261008.sh verify   # stream both back and check every digest
set -euo pipefail
CFS=/global/cfs/cdirs/m3246/josephrb
H=/home/j/josephrb/prd-release-preservation-20261008
ZCV=$CFS/prd-release-preservation-20261008/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/z_pilot_20260916_a5/z-cv.npz
ZCV_SHA=3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5
HERE=$(cd "$(dirname "$0")" && pwd)
case "${1:-}" in
  put)
    hsi -q "mkdir -p $H"
    (cd $CFS && htar -cvf $H/s5p-archive-20261006.tar -Hcrc s5p-archive-20261006 > /dev/null)
    echo "$ZCV_SHA  $(sha256sum "$ZCV" | cut -d' ' -f1)" | awk '$1!=$2{print "z-cv source digest mismatch"; exit 1}'
    hsi -q "put $ZCV : $H/z-cv.npz"
    hsi -q "ls -l $H"
    ;;
  verify)
    got=$(hsi -q "get - : $H/z-cv.npz" | sha256sum | cut -d' ' -f1)
    [ "$got" = "$ZCV_SHA" ] && echo "z-cv.npz: read-back sha256 $got OK" || { echo "z-cv.npz: read-back $got != $ZCV_SHA"; exit 1; }
    meta=$(mktemp)   # the archive's own SHA256SUMS and files.txt are not in its list; hash the CFS copies
    (cd $CFS/s5p-archive-20261006 && sha256sum SHA256SUMS files.txt) > "$meta"
    hsi -q "get - : $H/s5p-archive-20261006.tar" | python3 "$HERE/verify_tar_stream.py" \
      $CFS/s5p-archive-20261006/SHA256SUMS s5p-archive-20261006 "$meta"
    rm -f "$meta"
    ;;
  *) echo "usage: $0 put|verify" >&2; exit 2 ;;
esac
