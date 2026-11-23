#!/bin/bash
# pg-probe-launch.sh <sha256 of pg-probe.py> -- run PG's stat-only probe (COVFIX-DECLARATION.md section 4.1) once on a
# Perlmutter login node, from this laptop. Refuses unless pg-probe.py is exactly the expected bytes and pg-probe.out
# does not exist yet. The probe travels on ssh's stdin (`python3.11 -I -B -`), so nothing is deployed or written on the
# cluster except the probe's own throwaway GNUPGHOME under $SCRATCH, which it removes. Output: pg-probe.out here.
# Run only on the director's GO for this exact launcher and probe.
set -o pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S="$HERE/pg-probe.py"; O="$HERE/pg-probe.out"; HOST=saul.nersc.gov
WANT="${1:?expected sha256 of pg-probe.py}"
GOT=$(shasum -a 256 "$S" | cut -c1-64)
[ "$GOT" = "$WANT" ] || { echo "STOP: $S is $GOT, not $WANT" >&2; exit 3; }
[ ! -e "$O" ] && [ ! -e "$O.partial" ] || { echo "STOP: $O already exists" >&2; exit 3; }
{ echo "# pg-probe.py sha256 $GOT"; echo "# launched $(date -u +%FT%TZ) from $(hostname -s) to $HOST"; } > "$O.partial"
ssh -o BatchMode=yes "$HOST" '/usr/bin/python3.11 -I -B -' < "$S" >> "$O.partial" 2>&1
RC=$?
echo "# rc $RC at $(date -u +%FT%TZ)" >> "$O.partial"
mv "$O.partial" "$O"
echo "probe rc=$RC; $(shasum -a 256 "$O" | cut -c1-64)  $O"
exit $RC
