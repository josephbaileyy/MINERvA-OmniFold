#!/bin/bash
# EVW2D: the HPSS copy of the accepted products, on a Perlmutter login node, after the post. EVW5D's evw5d_hpss.sh,
# adapted. Launched from a private /dev/shm copy of itself by evw2d_deposit.sh, whose path is $1 (only read; the
# launcher's wrapper deletes it). It archives only when:
#   - the lane root and $LANE/out are real directories reached through no link;
#   - $LANE/post.pass (which the post publishes last, only on PASS) is exactly this job, the bound config digest and
#     the bound products digest, and $LANE/out/SHA256SUMS has the bound digest;
#   - deploy_C's evw2d.py (the checker) is the approved bytes;
#   - a private snapshot of SHA256SUMS and evw2d.done is taken, with the bound digest; and the checker passes on the
#     products: evw2d.accepted(out), SHA256SUMS's digest the bound one, run.json's config digest and slurm_job the
#     bound ones (root_6_28, as in the job and the post).
# Every pin and the file list come from the snapshot: the products SHA256SUMS lists, SHA256SUMS and evw2d.done, and
# nothing else (the directory's listing must equal it). htar with CRC and verify, then hsi hashcreate and hashverify;
# then the WHOLE archive is retrieved into a private mktemp directory in /dev/shm, every file compared with its pin and
# the count with the list, and the checker run on the retrieved copy. The scratch manifest and marker must still equal
# the snapshot. Any miss makes the exit 1. The retrieved copy is removed file by file, by the names in the pinned list
# only, then its directories by rmdir (no glob, no rm -r). Nothing on scratch is removed and nothing is written on CFS.
# Receipts in $LANE/hpss, tarred to $LANE/hpss.tar.gz (written under a partial name, then renamed).
SELF=$1
LANE=__LANE_ROOT__
EVW_SHA=__EVW2D_PY_SHA256__
CFG_SHA=__CONFIG_SHA256__
BOUND=__PRODUCTS_SHA256SUMS_SHA256__
JOBID=__JOB_ID__
P=${LANE%/*}                    # the lane root is BINDING 1's (/pscratch/sd/j/josephrb/evw2d-<yyyymmdd>)
R=${LANE##*/}
E=$LANE/out
O=$LANE/hpss
DM=$LANE/deploy_M
DC=$LANE/deploy_C
H=/home/j/josephrb/mnv-$R
TAR=$H/$R.tar
set -o noclobber
export LC_ALL=C
bail() { echo "STOP (nothing archived): $*"; exit 9; }
for v in "$LANE" "$EVW_SHA" "$CFG_SHA" "$BOUND" "$JOBID"; do case "$v" in *__*) bail "a pin is not filled in";; esac; done
case "$R" in evw2d-20[0-9][0-9][0-9][0-9][0-9][0-9]) ;; *) bail "the lane root $LANE is not <dir>/evw2d-<yyyymmdd>";; esac
for d in "$LANE" "$E"; do
  [ -d "$d" ] && [ ! -L "$d" ] && [ "$(cd "$d" && pwd -P)" = "$d" ] || bail "$d is not a real directory"
done
for f in "$O" "$LANE/hpss.tar.gz" "$LANE/hpss.tar.gz.partial"; do [ ! -e "$f" ] && [ ! -L "$f" ] || bail "$f exists"; done
want=$(printf 'job=%s\nconfig_sha256=%s\nproducts_SHA256SUMS_sha256=%s' "$JOBID" "$CFG_SHA" "$BOUND")
[ -f "$LANE/post.pass" ] && [ ! -L "$LANE/post.pass" ] || bail "no post.pass"
pp=$(cat "$LANE/post.pass") && [ "$pp" = "$want" ] || bail "post.pass does not name this job, config and products"
s=$(sha256sum "$E/SHA256SUMS" | cut -d' ' -f1) && [ "$s" = "$BOUND" ] || bail "SHA256SUMS is not the bound one"
W=$DC/2d-unfolding/evw2d/evw2d.py
w=$(sha256sum "$W" | cut -d' ' -f1) && [ -f "$W" ] && [ ! -L "$W" ] && [ "$w" = "$EVW_SHA" ] || bail "the checker is not the approved bytes"
mkdir "$O" || bail "mkdir $O"
exec > "$O/hpss.log" 2>&1
umask 077
echo "node $(hostname) $(date -u +%FT%TZ) hpss sha256 $(sha256sum "$SELF" | cut -d' ' -f1) bound $BOUND job $JOBID"
cp "$SELF" "$O/evw2d_hpss.sh" || { echo "FAILED: the script copy"; exit 1; }
fin() { echo "hpss rc=$1 $(date -u +%FT%TZ)"
  if tar czf "$LANE/hpss.tar.gz.partial" -C "$LANE" hpss && mv -- "$LANE/hpss.tar.gz.partial" "$LANE/hpss.tar.gz"; then :
  else echo "FAILED: the archive of the receipts"; exit 1; fi
  exit "$1"; }
stop() { echo "STOP: $*"; fin 1; }
# a private snapshot of the manifest and the marker: every pin and the file list come from it
mkdir "$O/snapshot" || stop "mkdir snapshot"
cp -p "$E/SHA256SUMS" "$E/evw2d.done" "$O/snapshot/" || stop "snapshot"
s=$(sha256sum "$O/snapshot/SHA256SUMS" | cut -d' ' -f1) && [ "$s" = "$BOUND" ] || stop "the snapshot manifest is not the bound one"
done_sha=$(sha256sum "$O/snapshot/evw2d.done" | cut -d' ' -f1) || stop "the marker's digest"
checker() {   # checker <product dir> <tag>: prints ACCEPTED only if every check holds
  ( set +o noclobber   # the setup runs as in the job; this script's own redirects stay exclusive outside it
    source "$DM/setup_salloc_env.sh" > "$O/env-$2.log" 2>&1 || exit 96
    [ "$(command -v python3)" = "$HOME/.conda/envs/root_6_28/bin/python3" ] || exit 98
    cd "$O" || exit 95
    PYTHONDONTWRITEBYTECODE=1 python3 -B -c "import hashlib, json, sys
sys.path.insert(0, sys.argv[1]); import evw2d
from pathlib import Path
out = Path(sys.argv[2])
r = evw2d.accepted(out)
run = json.loads((out / 'run.json').read_text())
sums = hashlib.sha256((out / 'SHA256SUMS').read_bytes()).hexdigest()
ok = (r['pass'] is True and sums == sys.argv[3] and run.get('config_sha256') == sys.argv[4]
      and str(run.get('slurm_job')) == sys.argv[5])
print(json.dumps({'pass': r['pass'], 'sums': sums, 'config_sha256': run.get('config_sha256'),
                  'slurm_job': run.get('slurm_job')}), file=sys.stderr)
print('ACCEPTED' if ok else 'REFUSED'); sys.exit(0 if ok else 1)" \
      "$DC/2d-unfolding/evw2d" "$1" "$BOUND" "$CFG_SHA" "$JOBID" 2> "$O/checker-$2.err" )
}
acc=$(checker "$E" scratch); arc=$?; echo "checker on scratch: $acc rc=$arc"; cat "$O/checker-scratch.err"
[ "$arc" -eq 0 ] && [ "$acc" = ACCEPTED ] || stop "the checker refused the products on scratch (rc $arc)"
d=$(sha256sum "$E/evw2d.done" | cut -d' ' -f1) && [ "$d" = "$done_sha" ] || stop "the marker changed during the check"
{ sed 's|^\([0-9a-f]\{64\}\)  |\1  '"$R"'/out/|' "$O/snapshot/SHA256SUMS"
  echo "$BOUND  $R/out/SHA256SUMS"; echo "$done_sha  $R/out/evw2d.done"; } | sort -k2 > "$O/pinned.sha256" || stop "pins"
cut -c67- "$O/pinned.sha256" > "$O/htar_files.txt" || stop "the file list"
nf=$(( $(wc -l < "$O/pinned.sha256") ))
[ "$nf" -ge 6 ] || stop "the pinned list has $nf entries"
( cd "$P" && find "$R/out" \( -type f -o -type l -o -type d \) ! -path "$R/out" | sort ) > "$O/listing.txt" || stop "listing"
cmp -s "$O/htar_files.txt" "$O/listing.txt" || stop "the directory holds entries outside the verified set"
echo "files: $nf"; cat "$O/pinned.sha256"
hpssquota > "$O/quota-before.txt" 2>&1
cd "$P" || stop "cd $P"
hsi -q "mkdir -p $H" 2>&1 || stop "hsi mkdir $H"
hsi -q "ls $TAR" > "$O/hsi-ls-before.txt" 2>&1 && stop "$TAR exists"
htar -Hcrc -Hverify=1 -cvf "$TAR" -L "$O/htar_files.txt" > "$O/htar.log" 2>&1; r=$?; echo "htar rc=$r"; tail -3 "$O/htar.log"
[ "$r" -eq 0 ] || stop "htar rc $r"
hsi -q "hashcreate $TAR" > "$O/hashcreate.log" 2>&1; hc=$?; echo "hashcreate rc=$hc"
hsi -q "hashverify $TAR" > "$O/hashverify.log" 2>&1; hv=$?; echo "hashverify rc=$hv"; cat "$O/hashverify.log"
hsi -q "ls -l $TAR ${TAR}.idx" 2>&1 | tail -2
bad=0
[ "$hc" -eq 0 ] && [ "$hv" -eq 0 ] || bad=1
T=$(mktemp -d /dev/shm/jrb-evw2d-retrieve.XXXXXX) || stop "mktemp"
echo "retrieving into $T"
( cd "$T" && htar -xf "$TAR" < /dev/null ) > "$O/retrieve-htar.log" 2>&1; xr=$?; echo "htar -xf rc=$xr"
[ "$xr" -eq 0 ] || bad=1
( cd "$T" && sha256sum --strict -c "$O/pinned.sha256" ) > "$O/retrieve.log" 2>&1 || bad=1
cat "$O/retrieve.log"
ne=$(grep -c ': OK$' "$O/retrieve.log"); nall=$(( $(cd "$T" && find . -type f | wc -l) ))
echo "retrieved and equal to their pins: $ne of $nf; files retrieved: $nall"
[ "$ne" -eq "$nf" ] && [ "$nall" -eq "$nf" ] || bad=1
racc=$(checker "$T/$R/out" retrieved); rr=$?; echo "checker on the retrieved copy: $racc rc=$rr"; cat "$O/checker-retrieved.err"
[ "$rr" -eq 0 ] && [ "$racc" = ACCEPTED ] || bad=1
# the retrieved copy: the pinned names only, then the directories htar made, deepest first
while IFS= read -r n; do rm -f -- "$T/$n"; done < "$O/htar_files.txt"
rmdir -- "$T/$R/out" "$T/$R" "$T" || { echo "the retrieved copy left files in $T"; bad=1; }
for f in SHA256SUMS evw2d.done; do
  cmp -s "$E/$f" "$O/snapshot/$f" || { echo "the scratch $f changed during the archive"; bad=1; }
done
hpssquota > "$O/quota-after.txt" 2>&1
grep -h "HPSS" "$O/quota-before.txt" "$O/quota-after.txt"
fin "$bad"
