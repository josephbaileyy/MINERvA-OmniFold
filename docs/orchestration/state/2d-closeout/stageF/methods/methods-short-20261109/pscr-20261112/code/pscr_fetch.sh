#!/bin/bash
# #977 read-only pscratch session, the Mac side (pattern: T2B's t2b_fetch.sh). One ssh session: saul.nersc.gov, then
# a hop to NODE; stdin carries pscr_remote.sh through both hops; on NODE the /dev/shm copy's sha256 must equal the
# pinned one, or NODE deletes it and exits 8 before anything runs. The tar comes back on stdout into a new empty
# directory; ssh's rc is read unpiped. Then, locally, under python -I: the tar must hold exactly the five declared
# member names as regular files, written by name (never by tar path); work_proxy.npz must hash to coverage.json:9's
# sha; the manifest's 100 assess products must equal INVENTORY.sha256 (path and sha) and OF5D must equal
# inputs-sha256.txt:1; every input stat_unchanged and whole. Any mismatch or non-zero remote rc: nothing is kept.
# Usage: bash pscr_fetch.sh <new empty dir> <login node, e.g. login27> <w_inventory.sha256>
F=${1:?new empty dir}; NODE=${2:?login node}; INV=${3:?w_inventory.sha256}
HERE=$(cd "$(dirname "$0")" && pwd)
S="$HERE/pscr_remote.sh"; SHA=9513d080d4e34ca5bb072b56314502c916a857ba12216dfdc437d2ce4fd239a3
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local remote-half script is not the pinned one"; exit 8; }
[ "$(shasum -a 256 "$INV" | cut -d' ' -f1)" = "a08ae0eb2648761d0dd1d003e1c463b4beaf697074daf8cff5eaf5c530bc4b52" ] || { echo "STOP: the inventory file is not the pinned one"; exit 8; }
R="f=/dev/shm/pscr977.\$\$.sh; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\" >&2; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\" >&2; bash \"\$f\" \"\$f\"; r=\$?; echo \"script rc=\$r\" >&2; exit \$r"
ssh -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 saul.nersc.gov \
  "ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/session.tar" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
grep -v -E '^(\*|  |Lawrence|contract|property|Users|expectation|Any or all|intercepted|to authorized|as well|By using|recording|of Lawrence|Unauthorized|disciplinary|this system|conditions|stated|$)' "$F/session.err"
shasum -a 256 "$F/session.tar"
[ $rc = 0 ] || { echo "STOP: the remote half exited $rc; nothing is unpacked"; exit $rc; }
mkdir "$F/files" || exit 9
/usr/bin/python3 -I - "$F/session.tar" "$F/files" "$INV" <<'PY'
import hashlib, json, sys, tarfile
from pathlib import Path
tar, dest, inv = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
names = {"work_proxy.npz", "w_truth.npz", "w_truth_meta.json", "f53.json", "manifest.json"}
def stop(msg, code=7):
    for p in dest.iterdir():
        p.unlink()
    print("STOP: " + msg); sys.exit(code)
with tarfile.open(tar, "r:") as tf:
    ms = tf.getmembers()
    if {m.name for m in ms} != names or len(ms) != len(names) or not all(m.isreg() for m in ms):
        stop(f"the tar holds {[m.name for m in ms]}, not the five declared regular files")
    for m in ms:
        assert m.name in names
        (dest / m.name).write_bytes(tf.extractfile(m).read())
wp = hashlib.sha256((dest / "work_proxy.npz").read_bytes()).hexdigest()
if wp != "42ce788bb28919c098041f14b5a4fb8b22aca06aa7f962ca38dd398149f23621":
    stop(f"work_proxy.npz sha256 {wp}")
man = json.loads((dest / "manifest.json").read_text())
got = {r["path"]: r for r in man["inputs"]}
want = {}
for line in open(inv):
    h, p = line.split()
    want[p] = h
want["/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz"] = \
    "07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f"
want["/pscratch/sd/j/josephrb/tmp-playlist-coverage-20261014/work_proxy.npz"] = wp
if set(got) != set(want):
    stop(f"manifest inputs {len(got)} differ from the {len(want)} declared")
bad = [p for p in want if got[p]["sha256"] != want[p] or not got[p]["stat_unchanged"] or not got[p]["whole"]]
if bad or not man["ok"]:
    stop(f"{len(bad)} inputs failed sha/stat/whole: {bad[:5]}; manifest ok={man['ok']}")
f53 = json.loads((dest / "f53.json").read_text())
if not f53["control_r4_match"]:
    stop("F5.3 control: unweighted fractions differ from r4_migration.json")
for n in sorted(names):
    print(f"OK  {n} {hashlib.sha256((dest / n).read_bytes()).hexdigest()}")
print(f"OK  {len(want)} inputs: sha, stat unchanged, whole; F5.3 control matches r4_migration.json")
print("PSCR-977 OK")
PY
