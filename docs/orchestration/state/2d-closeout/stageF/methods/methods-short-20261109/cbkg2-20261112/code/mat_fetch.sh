#!/bin/bash
# #977 C-BKG-2, the Mac side (pattern: cbkg_fetch.sh ecec7721, approved 2026-11-12). One ssh session: saul, a hop to NODE; stdin carries
# mat_remote.sh; on NODE the /dev/shm copy's sha256 must equal the pinned one or NODE deletes it and exits 8 before
# anything runs. The tar comes back on stdout into a new empty directory; ssh's rc is read unpiped.
# rc 0: under python -I the tar must hold exactly the four declared members (regular files, written by name); the
# manifest's two inputs must carry their pins (base_cv c76256a4, work_proxy 42ce788b), whole, stat unchanged; the
# summary's control and the closure must pass, and every source file read must keep its stat (manifest ok); any
# failure: nothing is kept. The line-by-line comparison of mat_source.json with port 1 is done afterwards, locally.
# rc 5, 6 or 7 (control, probe (a), probe (b) STOP): nothing is unpacked; the tar's JSON members are printed from memory
# for the STOP report and the tar is kept as the record. Any other non-zero rc: nothing is unpacked.
# Usage: bash mat_fetch.sh <new empty dir> <login node>
F=${1:?new empty dir}; NODE=${2:?login node}
HERE=$(cd "$(dirname "$0")" && pwd)
S="$HERE/mat_remote.sh"; SHA=4819fb424d72ae982c87821d3acae4a916c2c9ba2dda8cb15a900c0cbf6a19e8
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local remote-half script is not the pinned one"; exit 8; }
R="f=/dev/shm/matbkg977.\$\$.sh; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\" >&2; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\" >&2; bash \"\$f\" \"\$f\"; r=\$?; echo \"script rc=\$r\" >&2; exit \$r"
ssh -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 saul.nersc.gov \
  "ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/session.tar" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
grep -E '^(node |session |squeue|sacct|rpd_|FENCE|FILE |READ |SOURCE|CONTROL|B |MATBKG|FAILED|STOP|script rc)' "$F/session.err" | cut -c1-600
shasum -a 256 "$F/session.tar"
if [ $rc = 5 ] || [ $rc = 6 ] || [ $rc = 7 ]; then
  /usr/bin/python3 -I - "$F/session.tar" <<'PY'
import sys, tarfile
with tarfile.open(sys.argv[1], "r:") as tf:
    for m in tf.getmembers():
        if m.isreg() and m.name.endswith(".json"):
            print(f"--- {m.name} (from the tar, not extracted)"); print(tf.extractfile(m).read().decode()[:20000])
PY
  echo "STOP: rc=$rc; nothing unpacked; the tar is the record"; exit $rc
fi
[ $rc = 0 ] || { echo "STOP: the remote half exited $rc; nothing is unpacked"; exit $rc; }
mkdir "$F/files" || exit 9
/usr/bin/python3 -I - "$F/session.tar" "$F/files" <<'PY'
import hashlib, json, sys, tarfile
from pathlib import Path
tar, dest = sys.argv[1], Path(sys.argv[2])
names = {"manifest.json", "mat_source.json", "cbkg2_hists.npz", "cbkg2_summary.json"}
PINS = {"/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s0/evloop/base_cv.root": "c76256a495d2deb7c213c2f8203b284bea640d90e697c495f5e11cedc830846b",
        "/pscratch/sd/j/josephrb/tmp-playlist-coverage-20261014/work_proxy.npz": "42ce788bb28919c098041f14b5a4fb8b22aca06aa7f962ca38dd398149f23621"}
def stop(msg):
    for p in dest.iterdir():
        p.unlink()
    print("STOP: " + msg); sys.exit(7)
with tarfile.open(tar, "r:") as tf:
    ms = tf.getmembers()
    if {m.name for m in ms} != names or len(ms) != len(names) or not all(m.isreg() for m in ms):
        stop(f"the tar holds {[m.name for m in ms]}, not the four declared regular files")
    for m in ms:
        assert m.name in names
        (dest / m.name).write_bytes(tf.extractfile(m).read())
man = json.loads((dest / "manifest.json").read_text())
got = {r["path"]: r for r in man["inputs"]}
if set(got) != set(PINS) or any(got[p]["sha256"] != PINS[p] or not got[p]["stat_unchanged"] or not got[p]["whole"] for p in PINS) or not man["ok"]:
    stop(f"an input failed its pin/stat/whole check, or manifest ok={man.get('ok')}")
s = json.loads((dest / "cbkg2_summary.json").read_text())
if not (s["control"]["pass"] and s["closure_pass"]):
    stop("the control or a closure did not pass")
for n in sorted(names):
    print(f"OK  {n} {hashlib.sha256((dest / n).read_bytes()).hexdigest()}")
print("CONTROL", json.dumps(s["control"]))
print("classes", {k: v for k, v in s.items() if k.startswith("frac") or k == "boundary_1mm"})
print("MATBKG-977 OK (now compare mat_source.json with port 1 line by line)")
PY
