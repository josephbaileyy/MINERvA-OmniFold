#!/bin/bash
# RE-2: durable HPSS copy of J0's and part B's products and records, by RE2-DECLARATION-B.md §8 (R9 (a)).
#     bash re2_hpss.sh            (on a Perlmutter login node; hsi authenticates there)
# Steps, each logged to $W/logs/<n>-<step>.log with its exit status captured unpiped in $W/logs/rc.tsv:
#   1 bundle: one tar of the member list, a manifest of each member's sha256, and the bundle's sha256
#   2 put -c on (bundle, manifest, bundle digest)   3 migrate -R   4 ls -V: every object's bytes at the tape level
#   5 hashverify -R, and its path set against hashlist -R, both non-empty
#   6 recovery: get into a fresh directory, bundle sha256, untar into another fresh directory, every member
#     re-hashed, path sets diffed both ways (both non-empty), every ROOT file opened; the check is first shown to
#     fail on a tampered member, a missing member, an extra member and an empty manifest
#   7 du of the archive directory against the three objects' sizes, and hpssquota before and after
# Refuses if $W or the HPSS directory already exists. Any failed step stops the script with its own exit code.
set -eo pipefail
B=/pscratch/sd/j/josephrb/2d-closeout-re2-20261023
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold
NAME=re2-2d-rebuild-20261024
H=/home/j/josephrb/mnv-$NAME
W=$B/hpss
[ ! -e "$W" ] || { echo "$W exists"; exit 2; }
if hsi -q "ls -d $H" > /dev/null 2>&1; then echo "$H exists on HPSS"; exit 2; fi
mkdir -p "$W/logs"; cd "$W"
TAR=$NAME.tar
log() { echo "$(date -u +%FT%TZ) $*" | tee -a "$W/logs/steps.log"; }
rc() { printf '%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$1" "$2" >> "$W/logs/rc.tsv"; [ "$2" = 0 ] || { log "step $1 rc=$2"; exit 10; }; }
log "start host=$(hostname) script_sha256=$(sha256sum "$0" | cut -d' ' -f1)"
hpssquota > logs/0-quota-before.log 2>&1 && rc 0-quota-before 0 || rc 0-quota-before $?

# 1. The bundle. Members are paths relative to $B: J0's and part B's outputs and every record beside them.
(cd "$B" && find submissions.log j0 partb -type f | LC_ALL=C sort) > members.list
n=$(wc -l < members.list); log "1 members=$n"
[ "$(grep -c '/xsec.root$' members.list)" = 678 ] || { log "1 expected 678 xsec.root (34 J0 + 644 part B)"; exit 11; }
(cd "$B" && xargs -d '\n' sha256sum -- < "$W/members.list") > members.sha256
tar -C "$B" -cf "$TAR" --no-recursion -T members.list
tar -tf "$TAR" | LC_ALL=C sort | diff - members.list > logs/1-bundle.log 2>&1 && rc 1-bundle-list 0 || rc 1-bundle-list $?
sha256sum "$TAR" > "$TAR.sha256"
log "1 bundle $(stat -c %s "$TAR") B sha256=$(cut -d' ' -f1 "$TAR.sha256") manifest=$(sha256sum members.sha256 | cut -d' ' -f1)"

# 2. Put with a stored md5.
hsi -q "mkdir -p $H; cd $H; put -c on $TAR : $TAR; put -c on members.sha256 : members.sha256; put -c on $TAR.sha256 : $TAR.sha256" \
    > logs/2-put.log 2>&1 && rc 2-put 0 || rc 2-put $?

# 3. Migrate to tape.
hsi -q "migrate -R $H" > logs/3-migrate.log 2>&1 && rc 3-migrate 0 || rc 3-migrate $?

# 4. Residency: the "(tape)" level must hold each object's full size. DISK in the mode line is a class of service.
for i in $(seq 1 60); do
    ok=1
    for f in "$TAR" members.sha256 "$TAR.sha256"; do
        want=$(stat -c %s "$f")
        got=$(hsi -q "ls -V $H/$f" 2>&1 | awk '/^ *1 \(tape\)/ {print $NF}')
        [ "$got" = "$want" ] || ok=0
    done
    [ $ok = 1 ] && break
    sleep 60
done
for f in "$TAR" members.sha256 "$TAR.sha256"; do hsi -q "ls -V $H/$f"; done > logs/4-lsV.log 2>&1 || true
[ $ok = 1 ] && rc 4-tape-resident 0 || rc 4-tape-resident 1

# 5. hashverify recomputes each object's md5 (it reads every byte); the OK set must equal the stored-hash set.
set +e; hsi -q "hashverify -R $H" > logs/5-hashverify.log 2>&1; r=$?; set -e; rc 5-hashverify $r
hsi -q "hashlist -R $H" > logs/5-hashlist.log 2>&1 && rc 5-hashlist 0 || rc 5-hashlist $?
awk '$2 == "(md5)" && $3 == "OK" {sub(/:$/, "", $1); n = split($1, p, "/"); print p[n]}' logs/5-hashverify.log | sort > logs/5-ok.set
awk '$2 == "md5" {n = split($3, p, "/"); print p[n]}' logs/5-hashlist.log | sort > logs/5-stored.set
[ "$(wc -l < logs/5-ok.set)" = 3 ] && [ "$(wc -l < logs/5-stored.set)" = 3 ] && diff logs/5-ok.set logs/5-stored.set \
    && rc 5-coverage 0 || rc 5-coverage 1

# 6. Recovery into fresh directories.
verify_tree() {  # verify_tree <dir> <manifest>: every manifest member re-hashes, and the path sets agree both ways
    local d=$1 m=$2
    [ -s "$m" ] || { echo "empty manifest"; return 3; }
    (cd "$d" && sha256sum --quiet -c "$m") || { echo "a member's sha256 differs"; return 4; }
    (cd "$d" && find . -type f | sed 's#^\./##' | LC_ALL=C sort) > "$W/logs/6-got.set"
    sed 's/^[0-9a-f]\{64\}  //' "$m" | LC_ALL=C sort > "$W/logs/6-want.set"
    [ -s "$W/logs/6-got.set" ] && [ -s "$W/logs/6-want.set" ] || { echo "an empty path set"; return 5; }
    diff "$W/logs/6-want.set" "$W/logs/6-got.set" || { echo "path sets differ"; return 6; }
}
G=$W/recover-get; X=$W/recover-tree; mkdir "$G" "$X"
[ -z "$(ls -A "$G")" ] && [ -z "$(ls -A "$X")" ] || { log "6 recovery directories not empty"; exit 12; }
hsi -q "cd $H; lcd $G; get $TAR; get members.sha256; get $TAR.sha256" > logs/6-get.log 2>&1 && rc 6-get 0 || rc 6-get $?
(cd "$G" && sha256sum -c "$TAR.sha256") > logs/6-bundle-sha.log 2>&1 && rc 6-bundle-sha 0 || rc 6-bundle-sha $?
cmp "$G/members.sha256" members.sha256 && rc 6-manifest-same 0 || rc 6-manifest-same 1
tar -C "$X" -xf "$G/$TAR"
verify_tree "$X" "$G/members.sha256" > logs/6-verify.log 2>&1 && rc 6-verify 0 || rc 6-verify $?
# The check fails in each direction it acts on (on a scratch copy of the recovered tree).
T=$W/control; neg() {  # neg <name> <expected rc> <setup command>
    rm -rf "$T"; cp -a "$X" "$T"; cp "$G/members.sha256" "$W/control.sha256"; eval "$3"
    set +e; verify_tree "$T" "$W/control.sha256" >> logs/6-controls.log 2>&1; local r=$?; set -e
    echo "control $1 rc=$r (want $2)" >> logs/6-controls.log; [ "$r" = "$2" ] && rc "6-control-$1" 0 || rc "6-control-$1" 1
}
first=$(head -1 members.list)
neg tampered 4 "chmod u+w \"\$T/$first\"; printf x >> \"\$T/$first\""
neg missing 4 "rm -f \"\$T/$first\""
neg extra 6 "touch \"\$T/partb/extra-file\""
neg empty-manifest 3 ": > \"\$W/control.sha256\""
rm -rf "$T" "$W/control.sha256"
# Open every ROOT file and read its keys.
source "$A/setup_salloc_env.sh" > /dev/null 2>&1   # root_6_28 (set -u would abort its activation)
python - "$X" > logs/6-root-open.log 2>&1 <<'EOF' && rc 6-root-open 0 || rc 6-root-open $?
import pathlib, sys
import ROOT
files = sorted(pathlib.Path(sys.argv[1]).rglob("*.root"))
recovered = getattr(ROOT.TFile, "kRecovered", None)
bad = []
for p in files:
    f = ROOT.TFile.Open(str(p))
    if not f or f.IsZombie() or (recovered is not None and f.TestBit(recovered)) or f.GetListOfKeys().GetSize() == 0:
        bad.append(str(p))
    if f:
        f.Close()
print(f"opened {len(files)} ROOT files, {len(bad)} bad")
for b in bad:
    print("BAD", b)
sys.exit(0 if files and not bad else 1)
EOF

# 7. Reconcile: the archive directory holds exactly the three objects' bytes.
hsi -q "du $H" > logs/7-du.log 2>&1 && rc 7-du 0 || rc 7-du $?
want=$(( $(stat -c %s "$TAR") + $(stat -c %s members.sha256) + $(stat -c %s "$TAR.sha256") ))
hsi -q "ls -l $H" > logs/7-ls.log 2>&1
got=$(awk '$1 ~ /^-/ {s += $5} END {print s}' logs/7-ls.log)
echo "objects=$(grep -c '^-' logs/7-ls.log) bytes=$got want=$want" >> logs/7-du.log
[ "$got" = "$want" ] && [ "$(grep -c '^-' logs/7-ls.log)" = 3 ] && rc 7-reconcile 0 || rc 7-reconcile 1
hpssquota > logs/7-quota-after.log 2>&1 && rc 7-quota-after 0 || rc 7-quota-after $?
rm -rf "$G" "$X"
log "end: all steps rc=0"
