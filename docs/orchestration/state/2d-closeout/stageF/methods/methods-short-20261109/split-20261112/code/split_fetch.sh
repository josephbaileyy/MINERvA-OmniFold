#!/bin/bash
# #977 row 4.2 split probe, the Mac side (pattern: pscr_fetch.sh 9401337b). One ssh session: saul, a hop to NODE;
# stdin carries split_remote.sh; on NODE the /dev/shm copy's sha256 must equal the pinned one or NODE deletes it and
# exits 8 before anything runs. The tar comes back on stdout into a new empty directory; ssh's rc is read unpiped.
# rc 0: under python -I the tar must hold exactly the four declared members (regular files, written by name), and the
# manifest's 13 inputs must equal pl_shas.txt (the twelve per-playlist files' shas from proxy_hists_meta.json
# a71186e1) and work_proxy's 42ce788b, each stat unchanged and whole; any mismatch: nothing is kept.
# rc 6 or 7 (probe (a) or (b) STOP): nothing is unpacked; the tar's manifest and branch list are printed from memory
# for the STOP report, and the tar is kept as the record. Any other non-zero rc: nothing is unpacked.
# Usage: bash split_fetch.sh <new empty dir> <login node> <pl_shas.txt>
F=${1:?new empty dir}; NODE=${2:?login node}; PLS=${3:?pl_shas.txt}
HERE=$(cd "$(dirname "$0")" && pwd)
S="$HERE/split_remote.sh"; SHA=6784499d2a7d1b70e26c39bfc1da5e0dc663b32ff17dc4033781eb705f02ded9
[ -d "$F" ] && [ -z "$(ls -A "$F")" ] || { echo "STOP: $F is not a new empty directory"; exit 9; }
case "$NODE" in login[0-9][0-9]) ;; *) echo "STOP: '$NODE' is not a login node name"; exit 9;; esac
[ "$(shasum -a 256 "$S" | cut -d' ' -f1)" = "$SHA" ] || { echo "STOP: the local remote-half script is not the pinned one"; exit 8; }
[ "$(shasum -a 256 "$PLS" | cut -d' ' -f1)" = "fc729d1a2633e55675b4dc110c7e4f321b3b3d4edfd835ef9561f6e0e450cdbd" ] || { echo "STOP: pl_shas.txt is not the pinned one"; exit 8; }
R="f=/dev/shm/split977.\$\$.sh; umask 077; cat > \"\$f\"; h=\$(sha256sum \"\$f\" | cut -d' ' -f1); if [ \"\$h\" != $SHA ]; then rm -f -- \"\$f\"; echo \"STOP: /dev/shm copy sha256 \$h is not $SHA\" >&2; exit 8; fi; echo \"node \$(hostname) staged sha256 \$h\" >&2; bash \"\$f\" \"\$f\"; r=\$?; echo \"script rc=\$r\" >&2; exit \$r"
ssh -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=15 -o ServerAliveCountMax=8 saul.nersc.gov \
  "ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no $NODE $(printf '%q' "$R")" \
  < "$S" > "$F/session.tar" 2> "$F/session.err"
rc=$?
echo "ssh rc=$rc"
grep -E '^(node |session |squeue|sacct|FENCE|FILE |READ |A |C |SPLIT|FAILED|STOP|script rc)' "$F/session.err" | cut -c1-400
shasum -a 256 "$F/session.tar"
if [ $rc = 6 ] || [ $rc = 7 ]; then
  /usr/bin/python3 -I - "$F/session.tar" <<'PY'
import json, sys, tarfile
with tarfile.open(sys.argv[1], "r:") as tf:
    for n in ("manifest.json", "branches.json", "split_summary.json"):
        try:
            m = tf.getmember(n)
        except KeyError:
            continue
        if m.isreg():
            print(f"--- {n} (from the tar, not extracted)")
            print(tf.extractfile(m).read().decode()[:20000])
PY
  echo "STOP: probe rc=$rc; nothing unpacked; the tar is the record"; exit $rc
fi
[ $rc = 0 ] || { echo "STOP: the remote half exited $rc; nothing is unpacked"; exit $rc; }
mkdir "$F/files" || exit 9
/usr/bin/python3 -I - "$F/session.tar" "$F/files" "$PLS" <<'PY'
import hashlib, json, sys, tarfile
from pathlib import Path
tar, dest, pls = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
names = {"manifest.json", "branches.json", "split_hists.npz", "split_summary.json"}
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
want = {}
for line in open(pls):
    h, p = line.split(); want[p] = h
want["/pscratch/sd/j/josephrb/tmp-playlist-coverage-20261014/work_proxy.npz"] = \
    "42ce788bb28919c098041f14b5a4fb8b22aca06aa7f962ca38dd398149f23621"
got = {r["path"]: r for r in man["inputs"]}
if set(got) != set(want):
    stop(f"manifest inputs {sorted(got)} differ from the {len(want)} declared")
bad = [p for p in want if got[p]["sha256"] != want[p] or not got[p]["stat_unchanged"] or not got[p]["whole"]]
if bad or not man["ok"]:
    stop(f"{len(bad)} inputs failed sha/stat/whole: {bad}; manifest ok={man['ok']}")
summ = json.loads((dest / "split_summary.json").read_text())
if not all(s["control"]["pass"] for s in summ.values()):
    stop("a per-playlist control failed")
for n in sorted(names):
    print(f"OK  {n} {hashlib.sha256((dest / n).read_bytes()).hexdigest()}")
print(f"OK  {len(want)} inputs: sha, stat unchanged, whole; 12 per-playlist controls pass")
print("SPLIT-977 OK")
PY
