#!/bin/bash
# RPL check (i): the source of the muon-energy shifts, quoted by file:line@sha (fd/runperiod-loc-20261110/RPL-DECLARATION.md,
# inputs row "(i) the band's size"; the director's yes, 2026-11-11: one source file by explicit path, read-only). One
# Perlmutter login node, foreground, 0 node-h. Reads exactly one source file,
#   /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/MAT-MINERvA/universes/MuonSystematics.cxx
# (the path that stageB/verify-c04-x01/VERIFICATION.md:41 and c04-repair/REPORT.md cite), plus the checkout's HEAD
# commit id from .git/HEAD and the one ref file or packed-refs it names. Every read is os.open(O_RDONLY | O_NOATIME),
# with EPERM raised and never retried plainly, and stat before and after must be unchanged (else STOP, exit 8). An
# unresolved commit id is recorded as a note, not a STOP: the file's sha256 is the digest the quote carries. No git
# command runs and no directory is listed. Writes the file, line-numbered, with its sha256 to $OUT; refuses if $OUT
# exists.
# Launched from a /dev/shm copy of itself, whose path is $1; it deletes that copy at exit.
SELF=$1
OUT=/pscratch/sd/j/josephrb/rpl-matsrc-20261111
C=/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/MAT-MINERvA
bail() { rm -f -- "$SELF"; exit 9; }
[ ! -e "$OUT" ] || bail
mkdir -p "$OUT/logs" || bail
exec > "$OUT/logs/matsrc.log" 2>&1
finish() { echo "rpl matsrc rc=$1 $(date -u +%FT%TZ)"; echo "$1" > "$OUT/logs/matsrc.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) start=$(date -u +%FT%TZ)"
echo "script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"; cp "$SELF" "$OUT/logs/rpl_matsrc.sh"
mkdir -p "$OUT/work" && cd "$OUT/work" || finish 9
nice -n 19 /usr/bin/python3 -I - "$C" "$OUT" <<'PY'
import hashlib, json, os, sys
C, OUT = sys.argv[1:3]
SRC = "universes/MuonSystematics.cxx"


def read(path):
    s0 = os.stat(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOATIME)      # EPERM raises here; there is no plain retry
    with os.fdopen(fd, "rb") as f:
        b = f.read()
    s1 = os.stat(path)
    same = (s0.st_size, s0.st_mtime_ns, s0.st_atime_ns) == (s1.st_size, s1.st_mtime_ns, s1.st_atime_ns)
    return b, {"path": path, "bytes": s0.st_size, "mtime_ns": s0.st_mtime_ns, "stat_unchanged": same,
               "sha256": hashlib.sha256(b).hexdigest()}


rec = {"schema": "rpl-matsrc/1", "stop": []}
b, rec["source"] = read(f"{C}/{SRC}")
with open(f"{OUT}/MuonSystematics.cxx.numbered.txt", "w") as o:
    lines = b.decode("utf-8", "replace").split("\n")
    if lines and lines[-1] == "":
        lines.pop()                                    # the final newline ends line n; it is not a line n + 1
    for i, line in enumerate(lines, 1):
        o.write(f"{i:6d}\t{line}\n")
try:                                                  # the commit id is a note; the file's sha256 is the digest
    h, rec["git_HEAD"] = read(f"{C}/.git/HEAD")
    head = h.decode().strip()
    rec["git_HEAD"]["text"] = head
    if head.startswith("ref: "):
        ref = head[5:]
        rp = f"{C}/.git/{ref}"
        if os.path.exists(rp):
            r, rec["git_ref"] = read(rp)
            rec["commit"] = r.decode().strip()
        else:
            r, rec["git_ref"] = read(f"{C}/.git/packed-refs")
            hits = [l.split()[0] for l in r.decode().splitlines() if l.endswith(" " + ref)]
            rec["commit"] = hits[0] if len(hits) == 1 else None
    else:
        rec["commit"] = head
except OSError as e:
    rec["git_error"] = str(e)
for k in ("source", "git_HEAD", "git_ref"):
    if k in rec and not rec[k]["stat_unchanged"]:
        rec["stop"].append(f"{k}: stat changed")
json.dump(rec, open(f"{OUT}/matsrc.json", "w"), indent=1)
print("source", rec["source"]["sha256"], rec["source"]["bytes"], "commit", rec.get("commit"))
print("MATSRC", "STOP" if rec["stop"] else "OK", rec["stop"])
sys.exit(8 if rec["stop"] else 0)
PY
rc=$?
cd "$OUT" && rmdir work 2>/dev/null
(cd "$OUT" && sha256sum matsrc.json MuonSystematics.cxx.numbered.txt 2>/dev/null; tar czf post.tar.gz matsrc.json MuonSystematics.cxx.numbered.txt logs/rpl_matsrc.sh 2>/dev/null; sha256sum post.tar.gz)
finish $rc
