#!/bin/bash
# COVFIX rev 12 u=2 calibration inputs: one read-only fetch (director's go, 2026-11-24).
# One login node (a private ssh master), O_NOATIME reads streamed to the laptop, nothing written on the cluster.
set -eu
S=$(cd "$(dirname "$0")" && pwd)
OUT=$HOME/cov2d-work/u2-calib
D=/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix
NAMES=(genie_cv_xsec5d_full.npz genie_mec_xsec5d_full.npz nuwro_cv_xsec5d_full.npz gibuu_cv_xsec5d_fluxfix.npz)
PINS=(cfa42210dfe9cadc8e9460333316a639bd719c9ae52ab1144be900372a9adcc2
      c179855df6e42a5b8bab1f839aae675c53a5150f132649c855356ad75f26790f
      475a2871304db23efedbd5ab42a32d91c7f1d295b6dd0c907c46aa6d81c48070
      48917692ee1295902db3bec34d6c80e368f020ae7924dabbda7e996c461cca18)
CM=$HOME/.ssh/cm-cov2d-%C
SSH=(ssh -o ControlMaster=auto -o ControlPath="$CM" -o ControlPersist=120 -o BatchMode=yes saul.nersc.gov)
if [ -e "$OUT/inputs" ]; then echo "STOP: $OUT/inputs exists"; exit 2; fi
mkdir -p "$OUT/inputs"
L=$OUT/fetch.log
paths=""; for n in "${NAMES[@]}"; do paths="$paths $D/$n"; done
echo "laptop_start_utc $(date -u +%FT%TZ)" > "$L"
"${SSH[@]}" "echo host \$(hostname); echo remote_utc \$(date -u +%FT%TZ); sacct -u josephrb -X -n -s R,PD -S \$(date -d '-1 day' +%F) -o JobID%22,JobName%40,State%12" < /dev/null >> "$L"
"${SSH[@]}" "echo host \$(hostname); stat -c 'before %n %s atime=%X mtime=%Y' $paths" < /dev/null >> "$L"
rc=0
i=0
for n in "${NAMES[@]}"; do
  t=$OUT/inputs/.part-$n
  "${SSH[@]}" "/usr/bin/python3 - $D/$n" < "$S/reader.py" > "$t"
  got=$(shasum -a 256 "$t" | cut -d' ' -f1)
  if [ "$got" = "${PINS[$i]}" ]; then mv "$t" "$OUT/inputs/$n"; echo "sha OK $n $got $(stat -f %z "$OUT/inputs/$n")" >> "$L"
  else rm -f "$t"; echo "sha MISMATCH $n got $got pin ${PINS[$i]}" >> "$L"; rc=3; fi
  i=$((i + 1))
done
"${SSH[@]}" "echo host \$(hostname); stat -c 'after %n %s atime=%X mtime=%Y' $paths; echo remote_utc_end \$(date -u +%FT%TZ)" < /dev/null >> "$L"
ssh -o ControlPath="$CM" -O exit saul.nersc.gov 2>/dev/null || true
for n in "${NAMES[@]}"; do
  b=$(/usr/bin/grep "^before $D/$n " "$L" | sed 's/^before //'); a=$(/usr/bin/grep "^after $D/$n " "$L" | sed 's/^after //')
  if [ -n "$b" ] && [ "$b" = "$a" ]; then echo "atime unchanged $n" >> "$L"; else echo "ATIME MOVED OR UNREAD $n" >> "$L"; rc=4; fi
done
hosts=$(/usr/bin/grep -c '^host ' "$L"); uniq=$(/usr/bin/grep '^host ' "$L" | sort -u | wc -l | tr -d ' ')
echo "host lines $hosts distinct $uniq" >> "$L"; [ "$uniq" = 1 ] || rc=5
echo "laptop_end_utc $(date -u +%FT%TZ) rc=$rc" >> "$L"
cat "$L"
exit $rc
