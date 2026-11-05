#!/bin/bash
# REF-C2C1 C-DRAW, step A of 2 (REF-C2C1-BINDING-1.md ruling 4; the director's ruling 3(b), 2026-11-05), on a
# data-transfer node (dtn01), 0 node-h. It stages what the C-DRAW job reads, and nothing else:
#   - a fresh copy of E_R's 2D CV omnifile from CFS ($CV) into $O/inputs/, by an O_NOATIME read, checked against
#     43f8cc16 (re2_env.sh CV_SHA; the digest part B's deleted staged copy held, deletions.tsv row 2). The job reads it
#     from pscratch, as part B's runs did, and deletes it after the run with a ledger row;
#   - an O_NOATIME copy of the RECORDED replica S1_001 (part B out/S1_001/xsec.root, 2ea9b7d2, SHA256SUMS.J4a.1) into
#     $O/recorded/, so the comparison opens a copy and never the recorded product itself;
#   - the baseline flux $MC (d40aea69), read O_NOATIME and checked, which the job reads in place;
#   - the director's calendar item 4: whether a CFS copy of $MC exists, by a read-only name search of
#     /global/cfs/cdirs/m3246/josephrb (maxdepth 5); each candidate's sha256 by O_NOATIME read. HPSS waits for 11-06.
# Writes only under a NEW $O: stage.json (verdict PASS only if the three files equal their pins), stage.log,
# stage.done. Step B (cdraw_submit_login.sh) requires stage.json by its sha256. No set -u. Any stop is final.
# Launched from a /dev/shm copy of itself (its path is $1), which it deletes at exit.
SELF=$1
O=/pscratch/sd/j/josephrb/ref-c2c1-20261105/cdraw
CV=/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root
MC=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root
REC=/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb/out/S1_001/xsec.root
PY=$HOME/.conda/envs/root_6_28/bin/python3
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
case "$(hostname)" in dtn*) ;; *) bail ;; esac
[ ! -e "$O" ] && [ -x "$PY" ] || bail
mkdir -p "$O/inputs" "$O/recorded" || bail
exec > "$O/stage.log" 2>&1
finish() { echo "cdraw stage rc=$1"; date -u +%FT%TZ; echo "$1" > "$O/stage.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "stage script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$O/cdraw_stage_dtn.sh"
echo "== CFS name search for runEventLoopMC_MEFHC.root (read-only)"
find /global/cfs/cdirs/m3246/josephrb -maxdepth 5 -name 'runEventLoopMC_MEFHC.root' -type f 2>/dev/null | sort > "$O/mc_cfs_candidates.txt"
cat "$O/mc_cfs_candidates.txt"
export OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
nice -n 19 ionice -c3 env -u PYTHONPATH "$PY" -I -B - "$O" "$CV" "$MC" "$REC" <<'PYEOF'
import hashlib, json, os, socket, sys, time
from pathlib import Path
O, CV, MC, REC = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
PIN = {"cv": "43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df",
       "mc": "d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316",
       "rec": "2ea9b7d241363c231ce25715b7bfd0ddd4ec2406c59972ecaaa6fb6e05462377"}


def read(p, copy_to=None):
    st = os.stat(p)
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    h, n = hashlib.sha256(), 0
    out = open(copy_to, "xb") if copy_to else None
    with os.fdopen(fd, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b); n += len(b)
            if out:
                out.write(b)
    if out:
        out.close()
    return {"path": str(p), "sha256": h.hexdigest(), "bytes": n, "atime_utc": time.strftime("%FT%TZ", time.gmtime(st.st_atime))}


rec = {"schema": "ref-c2c1-cdraw-stage/1", "host": socket.gethostname(), "started_utc": time.strftime("%FT%TZ", time.gmtime())}
cv_copy = O / "inputs/runEventLoopOmniFold_MEFHC.root"
rec["cv_source"] = read(CV, cv_copy)
rec["cv_copy"] = read(cv_copy)                    # re-read the copy itself, so the job reads checked bytes
rec["mc"] = read(MC)
rec_copy = O / "recorded/S1_001_xsec.root"
rec["recorded_source"] = read(REC, rec_copy)
rec["recorded_copy"] = read(rec_copy)
ok = {"cv": rec["cv_source"]["sha256"] == rec["cv_copy"]["sha256"] == PIN["cv"],
      "mc": rec["mc"]["sha256"] == PIN["mc"],
      "recorded": rec["recorded_source"]["sha256"] == rec["recorded_copy"]["sha256"] == PIN["rec"]}
cands = [l for l in (O / "mc_cfs_candidates.txt").read_text().splitlines() if l.strip()]
rec["mc_cfs_candidates"] = [read(Path(c)) | {"equals_pin": None} for c in cands]
for c in rec["mc_cfs_candidates"]:
    c["equals_pin"] = c["sha256"] == PIN["mc"]
rec["mc_cfs_copy_exists"] = any(c["equals_pin"] for c in rec["mc_cfs_candidates"])
rec |= {"pins": PIN, "checks": ok, "verdict": "PASS" if all(ok.values()) else "FAIL",
        "written_utc": time.strftime("%FT%TZ", time.gmtime()), "written_epoch": time.time()}
(O / "stage.json").write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
print(json.dumps({"checks": ok, "mc_cfs_copy_exists": rec["mc_cfs_copy_exists"], "candidates": len(cands)}))
print(json.dumps({"verdict": rec["verdict"], "sha256": hashlib.sha256((O / "stage.json").read_bytes()).hexdigest()}))
sys.exit(0 if all(ok.values()) else 1)
PYEOF
rc=$?
echo "stage python rc=$rc"
[ $rc = 0 ] || { echo "STOP: a staged file is not its pin (final; to the director)"; finish 4; }
finish 0
