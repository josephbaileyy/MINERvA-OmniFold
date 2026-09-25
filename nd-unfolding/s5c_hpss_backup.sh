#!/bin/bash
# D3 durable HPSS backup of the nine sole-copy scalar-5D objects, then a full restore from tape.
#
# Authority: docs/orchestration/AUTHORIZATION-20260924-scalar5d-campaign-activation.md row S8 (D3).
# MEASURES: whether each of the nine objects in the list file (a) still has its recorded size and
#   SHA-256 on /pscratch, (b) is written once to HPSS and resident on tape, and (c) restores from HPSS
#   to a fresh directory with the recorded SHA-256.
# CANNOT AUTHORIZE: any scientific use, re-verification or adoption of these bytes; deleting or moving
#   the originals (this script never writes, moves or deletes an original).
#
# Submitted only through nd-unfolding/s5c_meter.py (xfer QOS). Usage:
#   s5c_hpss_backup.sh <list.tsv> <hpss_dir> <out_dir>
# Exit: 0 all nine restored and equal; 10 a source changed (nothing written to HPSS);
#   11 HPSS quota or size refusal; 12 put failed; 13 not tape-resident after migration;
#   14 restore or digest mismatch; 2 usage.

LIST=${1:?list.tsv}
ARCH=${2:?hpss dir}
OUT=${3:?out dir}
PREFIX=/pscratch/sd/j/josephrb/
CAP_BYTES=$((64 * 1024 * 1024 * 1024))
RESTORE="$OUT/restore"
LOG="$OUT/steps.tsv"

if [ -e "$OUT" ] && [ -n "$(ls -A "$OUT" 2>/dev/null)" ]; then
    echo "refusing: $OUT exists and is not empty" >&2
    exit 2
fi
mkdir -p "$OUT" "$RESTORE"
exec > >(tee -a "$OUT/job.log") 2>&1
stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }
step() { printf '%s\t%s\n' "$(stamp)" "$*" >> "$LOG"; echo "[$(stamp)] $*"; }
step "START job=${SLURM_JOB_ID:-none} host=$(hostname) list=$LIST arch=$ARCH"

mapfile -t ROWS < <(grep -v '^#' "$LIST" | grep -v '^[[:space:]]*$')
if [ "${#ROWS[@]}" -ne 9 ]; then
    step "REFUSE list has ${#ROWS[@]} objects, expected 9"
    exit 2
fi

# 1. Quota and size.
TOTAL=0
for row in "${ROWS[@]}"; do
    size=$(printf '%s' "$row" | cut -f2)
    TOTAL=$((TOTAL + size))
done
/global/common/software/nersc/bin/hpssquota > "$OUT/hpssquota-before.txt" 2>&1
step "TOTAL_BYTES $TOTAL cap $CAP_BYTES"
if [ "$TOTAL" -gt "$CAP_BYTES" ]; then
    step "REFUSE total exceeds the D3 64 GiB cap"
    exit 11
fi

# 2. Source identity recheck (nothing is written to HPSS unless all nine match).
: > "$OUT/source-check.tsv"
bad=0
for row in "${ROWS[@]}"; do
    want=$(printf '%s' "$row" | cut -f1)
    size=$(printf '%s' "$row" | cut -f2)
    path=$(printf '%s' "$row" | cut -f3)
    got_size=$(stat -c %s "$path" 2>/dev/null || echo MISSING)
    got_sha=$(sha256sum "$path" 2>/dev/null | cut -d' ' -f1)
    ok=no
    [ "$got_size" = "$size" ] && [ "$got_sha" = "$want" ] && ok=yes
    [ "$ok" = yes ] || bad=$((bad + 1))
    printf '%s\t%s\t%s\t%s\t%s\n' "$path" "$size" "$got_size" "$got_sha" "$ok" >> "$OUT/source-check.tsv"
    step "SOURCE $ok $path"
done
if [ "$bad" -ne 0 ]; then
    step "REFUSE $bad source(s) differ from the manifest; nothing written to HPSS"
    exit 10
fi

# 3. Put, refusing to overwrite an existing HPSS path.
: > "$OUT/put.tsv"
for row in "${ROWS[@]}"; do
    path=$(printf '%s' "$row" | cut -f3)
    rel=${path#"$PREFIX"}
    dst="$ARCH/$rel"
    if hsi -q "ls $dst" > /dev/null 2>&1; then
        step "REFUSE $dst already exists in HPSS"
        exit 12
    fi
    hsi -q "mkdir -p $(dirname "$dst")" > /dev/null 2>&1
    hsi -q "put $path : $dst" > "$OUT/put-$(basename "$rel").log" 2>&1
    rc=$?
    printf '%s\t%s\t%s\n' "$path" "$dst" "$rc" >> "$OUT/put.tsv"
    step "PUT rc=$rc $dst"
    [ "$rc" -eq 0 ] || exit 12
done

# 4. Migrate to tape and purge the disk-cache copy, then prove tape residency per object.
hsi -q "migrate -R -P $ARCH" > "$OUT/migrate.log" 2>&1
step "MIGRATE rc=$?"
deadline=$(( $(date +%s) + 4 * 3600 ))
while :; do
    resident=0
    : > "$OUT/residency.tsv"
    for row in "${ROWS[@]}"; do
        size=$(printf '%s' "$row" | cut -f2)
        path=$(printf '%s' "$row" | cut -f3)
        dst="$ARCH/${path#"$PREFIX"}"
        hsi -q "ls -V $dst" > "$OUT/lsV.tmp" 2>&1
        # ls -V row: " 1 (tape)   <VV count>   <stripe width>  <bytes at level>"
        tape_bytes=$(awk '$2 == "(tape)" {print $5; exit}' "$OUT/lsV.tmp")
        printf '%s\t%s\t%s\n' "$dst" "$size" "${tape_bytes:-0}" >> "$OUT/residency.tsv"
        [ "${tape_bytes:-0}" = "$size" ] && resident=$((resident + 1))
    done
    step "RESIDENT $resident/9 on tape"
    [ "$resident" -eq 9 ] && break
    if [ "$(date +%s)" -gt "$deadline" ]; then
        step "FAIL not all objects tape-resident after 4 h"
        exit 13
    fi
    hsi -q "migrate -R -P $ARCH" >> "$OUT/migrate.log" 2>&1
    sleep 300
done
cp "$OUT/lsV.tmp" "$OUT/lsV-last.txt"
hsi -q "purge -R $ARCH" > "$OUT/purge.log" 2>&1
step "PURGE rc=$?"
hsi -q "ls -lR $ARCH" > "$OUT/hsi-ls-lR.txt" 2>&1

# 5. Restore all nine to the fresh directory and verify SHA-256.
: > "$OUT/restore.tsv"
bad=0
for row in "${ROWS[@]}"; do
    want=$(printf '%s' "$row" | cut -f1)
    path=$(printf '%s' "$row" | cut -f3)
    rel=${path#"$PREFIX"}
    dst="$ARCH/$rel"
    local_copy="$RESTORE/$rel"
    mkdir -p "$(dirname "$local_copy")"
    hsi -q "get $local_copy : $dst" > "$OUT/get-$(basename "$rel").log" 2>&1
    rc=$?
    got=$(sha256sum "$local_copy" 2>/dev/null | cut -d' ' -f1)
    ok=no
    [ "$rc" -eq 0 ] && [ "$got" = "$want" ] && ok=yes
    [ "$ok" = yes ] || bad=$((bad + 1))
    printf '%s\t%s\t%s\t%s\t%s\n' "$dst" "$local_copy" "$rc" "$got" "$ok" >> "$OUT/restore.tsv"
    step "RESTORE $ok rc=$rc $rel"
done
/global/common/software/nersc/bin/hpssquota > "$OUT/hpssquota-after.txt" 2>&1
if [ "$bad" -ne 0 ]; then
    step "FAIL $bad restore(s) failed or differ; restored copies kept for diagnosis"
    exit 14
fi

# 6. The restored copies have served their purpose; the originals are untouched.
restored_bytes=$(du -sb "$RESTORE" | cut -f1)
rm -rf "$RESTORE"
step "DONE all 9 restored and SHA-256-equal; removed $restored_bytes restored bytes from the campaign namespace"
exit 0
