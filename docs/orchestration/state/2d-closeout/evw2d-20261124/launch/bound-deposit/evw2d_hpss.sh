#!/bin/bash
# EVW2D: the HPSS copy of the accepted products, on a Perlmutter login node, after the post. EVW5D's evw5d_hpss.sh,
# adapted. Launched from a private /dev/shm copy of itself by evw2d_deposit.sh, whose path is $1 (only read; the
# launcher's wrapper deletes it). Before it writes anything:
#   - the lane root and $LANE/out are real directories reached through no link, and the six names (the four products,
#     SHA256SUMS, evw2d.done) are regular files, not links;
#   - $LANE/post.pass (which the post publishes last, only on PASS) is exactly this job, the bound config digest and
#     the bound products digest; $LANE/out/SHA256SUMS has the bound digest and evw2d.done the bound marker digest;
#   - deploy_C's evw2d.py (the checker) is the approved bytes.
# Then: a private snapshot of SHA256SUMS and evw2d.done (both with their bound digests) gives every pin and the file
# list, and out/ must hold exactly those six files. The checker passes on scratch: it executes the very bytes it hashed
# (no import, no cache), then evw2d.accepted(out), SHA256SUMS's and evw2d.done's digests, run.json's config digest and
# slurm_job the bound ones (root_6_28, as in the job and the post). /dev/shm must have room for the retrieval.
# The HPSS directory is listed (the listing must succeed) and must hold none of the archive's names. The archive is
# written under a part name: scratch is re-hashed against the pins just before htar; htar -Hcrc -Hverify=1; hsi
# hashcreate and hashverify; the WHOLE archive is retrieved into a private mktemp directory in /dev/shm, every file
# compared with its pin, the counts with the list, and the checker run on the retrieved copy; scratch is re-hashed
# against the pins, the six names checked again as regular files, and its manifest and marker compared with the
# snapshot, and `htar -tf` of the part archive must list every pinned name. Only when every check holds are the index
# and then the archive renamed (hsi mv) to the final names, so the final .tar never appears without its index; then both
# final names must list and the final pair read back (htar -tf), or each is renamed back to the part name and the
# directory listed. Otherwise the part names stay (or whichever names
# the log reports), for the director. The retrieved copy
# is removed file by file, by the pinned names only, then its directories by rmdir (no glob, no rm -r). Nothing on
# scratch is removed and nothing is written on CFS. Receipts in $LANE/hpss, tarred to $LANE/hpss.tar.gz (written
# under a partial name, then renamed). Exit 0 only if the final archive is in place and verified; 9 = stopped before
# writing; 1 = stopped or failed after.
SELF=$1
LANE=/pscratch/sd/j/josephrb/evw2d-20261126
EVW_SHA=6106b23a8b6c5cb9c27acd8480329f6bc180f5c90f9af3ba82a92c9507e64887
CFG_SHA=bee02d38e8141a8780ba2c838007ebdd0663af1b195f3291ba71239e3f26e7ec
BOUND=e60867ef66eb47172a0e90140abc7a366d780dfc3aa3f9beb426a40a48d1416e
DONE_SHA=830d7d7641c1a5bca96fda4bde47094cf047abc8df183304aa99986414e1f133
JOBID=62022231
P=${LANE%/*}                    # the lane root is BINDING 1's (/pscratch/sd/j/josephrb/evw2d-<yyyymmdd>)
R=${LANE##*/}
E=$LANE/out
O=$LANE/hpss
DM=$LANE/deploy_M
DC=$LANE/deploy_C
H=/home/j/josephrb/mnv-$R
TAR=$H/$R.tar
TARP=$H/$R.tar.part
NAMES="SHA256SUMS constants.json evw2d.done run.json weights.npz xsec.root"
set -o noclobber
export LC_ALL=C
bail() { echo "STOP (nothing archived): $*"; exit 9; }
for v in "$LANE" "$EVW_SHA" "$CFG_SHA" "$BOUND" "$DONE_SHA" "$JOBID"; do case "$v" in *__*) bail "a pin is not filled in";; esac; done
case "$R" in evw2d-20[0-9][0-9][0-9][0-9][0-9][0-9]) ;; *) bail "the lane root $LANE is not <dir>/evw2d-<yyyymmdd>";; esac
hex64() { case "$1" in *[!0-9a-f]*|"") return 1;; esac; [ ${#1} -eq 64 ]; }
for v in "$EVW_SHA" "$CFG_SHA" "$BOUND" "$DONE_SHA"; do hex64 "$v" || bail "a digest pin is not 64 hex: '$v'"; done
case "$JOBID" in *[!0-9]*|"") bail "the job pin is not a number: '$JOBID'";; esac
for d in "$LANE" "$E"; do
  [ -d "$d" ] && [ ! -L "$d" ] && [ "$(cd "$d" && pwd -P)" = "$d" ] || bail "$d is not a real directory"
done
for n in $NAMES; do [ -f "$E/$n" ] && [ ! -L "$E/$n" ] || bail "$E/$n is not a regular file"; done
for f in "$O" "$LANE/hpss.tar.gz" "$LANE/hpss.tar.gz.partial"; do [ ! -e "$f" ] && [ ! -L "$f" ] || bail "$f exists"; done
want=$(printf 'job=%s\nconfig_sha256=%s\nproducts_SHA256SUMS_sha256=%s' "$JOBID" "$CFG_SHA" "$BOUND")
[ -f "$LANE/post.pass" ] && [ ! -L "$LANE/post.pass" ] || bail "no post.pass"
pp=$(cat "$LANE/post.pass") && [ "$pp" = "$want" ] || bail "post.pass does not name this job, config and products"
s=$(sha256sum "$E/SHA256SUMS" | cut -d' ' -f1) && [ "$s" = "$BOUND" ] || bail "SHA256SUMS is not the bound one"
s=$(sha256sum "$E/evw2d.done" | cut -d' ' -f1) && [ "$s" = "$DONE_SHA" ] || bail "evw2d.done is not the bound one"
W=$DC/2d-unfolding/evw2d/evw2d.py
w=$(sha256sum "$W" | cut -d' ' -f1) && [ -f "$W" ] && [ ! -L "$W" ] && [ "$w" = "$EVW_SHA" ] || bail "the checker is not the approved bytes"
mkdir "$O" || bail "mkdir $O"
exec > "$O/hpss.log" 2>&1
umask 077
echo "node $(hostname) $(date -u +%FT%TZ) hpss sha256 $(sha256sum "$SELF" | cut -d' ' -f1) bound $BOUND done $DONE_SHA job $JOBID"
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
s=$(sha256sum "$O/snapshot/evw2d.done" | cut -d' ' -f1) && [ "$s" = "$DONE_SHA" ] || stop "the snapshot marker is not the bound one"
checker() {   # checker <product dir> <tag>: prints ACCEPTED only if every check holds
  ( set +o noclobber   # the setup runs as in the job; this script's own redirects stay exclusive outside it
    source "$DM/setup_salloc_env.sh" > "$O/env-$2.log" 2>&1 || exit 96
    [ "$(command -v python3)" = "$HOME/.conda/envs/root_6_28/bin/python3" ] || exit 98
    cd "$O" || exit 95
    PYTHONDONTWRITEBYTECODE=1 python3 -B -c "import hashlib, json, sys, types
src = open(sys.argv[1], 'rb').read()
if hashlib.sha256(src).hexdigest() != sys.argv[3]:
    print('REFUSED'); sys.exit(1)
evw2d = types.ModuleType('evw2d'); evw2d.__file__ = sys.argv[1]; sys.modules['evw2d'] = evw2d
exec(compile(src, sys.argv[1], 'exec'), evw2d.__dict__)   # the very bytes hashed: no import, no cache
from pathlib import Path
out = Path(sys.argv[2])
r = evw2d.accepted(out)
run = json.loads((out / 'run.json').read_text())
sums = hashlib.sha256((out / 'SHA256SUMS').read_bytes()).hexdigest()
done = hashlib.sha256((out / 'evw2d.done').read_bytes()).hexdigest()
ok = (r['pass'] is True and sums == sys.argv[4] and done == sys.argv[5] and run.get('config_sha256') == sys.argv[6]
      and str(run.get('slurm_job')) == sys.argv[7])
print(json.dumps({'verdict': 'ACCEPTED' if ok else 'REFUSED', 'accepted_pass': r['pass'], 'sums': sums,
                  'done': done, 'config_sha256': run.get('config_sha256'), 'slurm_job': run.get('slurm_job')}),
      file=sys.stderr)
print('ACCEPTED' if ok else 'REFUSED'); sys.exit(0 if ok else 1)" \
      "$W" "$1" "$EVW_SHA" "$BOUND" "$DONE_SHA" "$CFG_SHA" "$JOBID" 2> "$O/checker-$2.err" )
}
acc=$(checker "$E" scratch); arc=$?; echo "checker on scratch: $acc rc=$arc"; cat "$O/checker-scratch.err"
[ "$arc" -eq 0 ] && [ "$acc" = ACCEPTED ] || stop "the checker refused the products on scratch (rc $arc)"
{ sed 's|^\([0-9a-f]\{64\}\)  |\1  '"$R"'/out/|' "$O/snapshot/SHA256SUMS"
  echo "$BOUND  $R/out/SHA256SUMS"; echo "$DONE_SHA  $R/out/evw2d.done"; } | sort -k2 > "$O/pinned.sha256" || stop "pins"
cut -c67- "$O/pinned.sha256" > "$O/htar_files.txt" || stop "the file list"
nf=$(( $(wc -l < "$O/pinned.sha256") ))
[ "$nf" -eq 6 ] || stop "the pinned list has $nf entries, not 6"
( cd "$P" && find "$R/out" \( -type f -o -type l -o -type d \) ! -path "$R/out" | sort ) > "$O/listing.txt" || stop "listing"
cmp -s "$O/htar_files.txt" "$O/listing.txt" || stop "the directory holds entries outside the verified set"
echo "files: $nf"; cat "$O/pinned.sha256"
need=0
for n in $NAMES; do
  sz=$(stat -c %s "$E/$n") || stop "cannot size $E/$n"
  case "$sz" in ''|*[!0-9]*) stop "the size of $E/$n is '$sz'";; esac
  need=$(( need + sz ))
done
avail=$(df -Pk /dev/shm | awk 'NR == 2 { print $4 }')
case "$avail" in ''|*[!0-9]*) stop "cannot read /dev/shm's free space";; esac
echo "retrieval needs $need bytes; /dev/shm has $(( avail * 1024 )) free"
[ $(( avail * 1024 )) -ge $(( need + need / 10 + 67108864 )) ] || stop "/dev/shm has no room for the retrieval"
hpssquota > "$O/quota-before.txt" 2>&1
cd "$P" || stop "cd $P"
hsi -q "mkdir -p $H" 2>&1 || stop "hsi mkdir $H"
hsi -q "ls -l $H" > "$O/hsi-ls-before.txt" 2>&1 || stop "hsi could not list $H"
cat "$O/hsi-ls-before.txt"
grep -Eq "(^|[[:space:]/])$R\.tar(\.part)?(\.idx)?\$" "$O/hsi-ls-before.txt"; g=$?
case "$g" in
  0) stop "$H already holds an archive name";;
  1) echo "no archive name in $H";;
  *) stop "could not read the listing (grep rc $g)";;
esac
( cd "$P" && sha256sum --strict -c "$O/pinned.sha256" ) > "$O/scratch-before.log" 2>&1 || stop "scratch differs from the pins"
htar -Hcrc -Hverify=1 -cvf "$TARP" -L "$O/htar_files.txt" > "$O/htar.log" 2>&1; r=$?; echo "htar rc=$r"; tail -3 "$O/htar.log"
[ "$r" -eq 0 ] || stop "htar rc $r; the part name $TARP is left"
bad=0
hsi -q "hashcreate $TARP" > "$O/hashcreate.log" 2>&1; hc=$?; echo "hashcreate rc=$hc"
hsi -q "hashverify $TARP" > "$O/hashverify.log" 2>&1; hv=$?; echo "hashverify rc=$hv"; cat "$O/hashverify.log"
[ "$hc" -eq 0 ] && [ "$hv" -eq 0 ] || bad=1
T=$(mktemp -d /dev/shm/jrb-evw2d-retrieve.XXXXXX) || stop "mktemp"
echo "retrieving into $T"
( cd "$T" && htar -xf "$TARP" < /dev/null ) > "$O/retrieve-htar.log" 2>&1; xr=$?; echo "htar -xf rc=$xr"
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
( cd "$P" && sha256sum --strict -c "$O/pinned.sha256" ) > "$O/scratch-after.log" 2>&1 || { echo "scratch changed during the archive"; bad=1; }
for n in $NAMES; do [ -f "$E/$n" ] && [ ! -L "$E/$n" ] || { echo "$E/$n is no longer a regular file"; bad=1; }; done
for f in SHA256SUMS evw2d.done; do
  cmp -s "$E/$f" "$O/snapshot/$f" || { echo "the scratch $f changed during the archive"; bad=1; }
done
# the part archive must read back through its index, listing every pinned name, before anything is renamed
htar -tf "$TARP" < /dev/null > "$O/htar-tf.log" 2>&1; tr=$?; echo "htar -tf rc=$tr"
nl=0; while IFS= read -r n; do awk -v n="$n" '$NF == n { f = 1 } END { exit !f }' "$O/htar-tf.log" && nl=$(( nl + 1 )); done < "$O/htar_files.txt"
echo "the archive lists $nl of $nf pinned names"
[ "$tr" -eq 0 ] && [ "$nl" -eq "$nf" ] || { echo "FAILED: the archive does not read back"; bad=1; }
if [ "$bad" -eq 0 ]; then
  if ! hsi -q "mv ${TARP}.idx ${TAR}.idx" > "$O/hsi-mv.log" 2>&1; then
    echo "FAILED: the index rename; the archive and its index stay at the part name $TARP"; bad=1
  elif ! hsi -q "mv $TARP $TAR" >> "$O/hsi-mv.log" 2>&1; then
    echo "FAILED: the archive rename; the index is at ${TAR}.idx and the archive at $TARP"; bad=1
  else
    hsi -q "ls -l $TAR ${TAR}.idx" > "$O/hsi-ls-after.txt" 2>&1; la=$?; cat "$O/hsi-ls-after.txt"
    htar -tf "$TAR" < /dev/null > "$O/htar-tf-final.log" 2>&1; tf=$?; echo "htar -tf (final) rc=$tf"
    fl=0; while IFS= read -r n; do awk -v n="$n" '$NF == n { f = 1 } END { exit !f }' "$O/htar-tf-final.log" && fl=$(( fl + 1 )); done < "$O/htar_files.txt"
    echo "the final archive lists $fl of $nf pinned names"
    if [ "$la" -eq 0 ] && grep -Eq "(^|[[:space:]/])$R\.tar\$" "$O/hsi-ls-after.txt" \
       && grep -Eq "(^|[[:space:]/])$R\.tar\.idx\$" "$O/hsi-ls-after.txt" && [ "$tf" -eq 0 ] && [ "$fl" -eq "$nf" ]; then
      echo "renamed to $TAR"
    else
      echo "FAILED: the final pair does not list and read back; renaming each back to the part name"; bad=1
      hsi -q "mv $TAR $TARP" >> "$O/hsi-mv.log" 2>&1; ra=$?; echo "archive rename back rc=$ra"
      hsi -q "mv ${TAR}.idx ${TARP}.idx" >> "$O/hsi-mv.log" 2>&1; ri=$?; echo "index rename back rc=$ri"
      hsi -q "ls -l $H" > "$O/hsi-ls-end.txt" 2>&1; echo "listing of $H after the rename back (rc $?):"; cat "$O/hsi-ls-end.txt"
    fi
  fi
else
  echo "a check failed: the archive stays at the part name $TARP"
fi
hpssquota > "$O/quota-after.txt" 2>&1
grep -h "HPSS" "$O/quota-before.txt" "$O/quota-after.txt"
fin "$bad"
