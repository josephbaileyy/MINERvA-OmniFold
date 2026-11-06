#!/bin/bash
# REF-C2C1 step two, stage 1 of 4: the staging (REF-C2C1-BINDING-2.md ruling 2.1; #814 at main 410c4868; code at
# M = 77d76cfc), on a data-transfer node (dtn01), 0 node-h, under the binding's fixed conditional sequence. It:
#   - refuses before writing anything if the staging root (config.json inputs.staging.root at M) or its parent exists;
#   - stats (no read) the two CFS sources (config.json inputs.CV_source, MC_source): owner, mode, atime;
#   - copies each once, by an O_NOATIME read, into the root under config.json's staged names, the sha256 taken in the
#     same pass (written "xb", never over a file), then re-reads each copy against its pin (CV_sha256 43f8cc16,
#     MC_sha256 d40aea69), as ref_c2c1.copy_noatime does;
#   - prints the real O_NOATIME evidence: the flag's value and the platform, each source's owner, the digest through
#     the noatime open, and each source's atime before and after (a moved atime is a STOP).
# The COV2D fence is checked from saul.nersc.gov immediately before launch (a DTN has no squeue). Writes only the two
# copies under the root and stage.json, stage.log, stage.done and this script's copy under $O/logs-stage. No set -u.
# Launched from a /dev/shm copy of itself (its path is $1), which it deletes at exit.
SELF=$1
O=/pscratch/sd/j/josephrb/ref-c2c1-20261106
ROOT=$O/stage
L=$O/logs-stage
CV=/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root
MC=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/fig_products/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root
PY=$HOME/.conda/envs/root_6_28/bin/python3
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
case "$(hostname)" in dtn*) ;; *) bail ;; esac
[ ! -e "$O" ] && [ -x "$PY" ] && [ -f "$CV" ] && [ -f "$MC" ] || bail
mkdir -p "$ROOT" "$L" || bail
exec > "$L/stage.log" 2>&1
finish() { echo "ref-c2c1 stage rc=$1"; date -u +%FT%TZ; echo "$1" > "$L/stage.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "stage script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$L/refc2c1_stage_dtn.sh"
export OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
nice -n 19 ionice -c3 env -u PYTHONPATH "$PY" -I -B - "$L" "$ROOT" "$CV" "$MC" <<'PYEOF'
import hashlib, json, os, platform, pwd, socket, sys, time
from pathlib import Path
L, ROOT, CV, MC = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
PIN = {"CV": "43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df",
       "MC": "d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316"}
NAME = {"CV": "runEventLoopOmniFold_MEFHC.root", "MC": "runEventLoopMC_MEFHC.root"}
utc = lambda t: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def stat(p):
    st = os.stat(p)
    return {"owner": pwd.getpwuid(st.st_uid).pw_name, "mode": oct(st.st_mode & 0o777), "bytes": st.st_size,
            "atime": st.st_atime, "atime_utc": utc(st.st_atime)}


def copy_noatime(src, dest):
    """One O_NOATIME read of src, written "xb" to dest; the digest of the same pass (ref_c2c1.copy_noatime's rule)."""
    h, n = hashlib.sha256(), 0
    with os.fdopen(os.open(str(src), os.O_RDONLY | os.O_NOATIME), "rb") as fh, open(dest, "xb") as fo:
        while block := fh.read(1 << 24):
            h.update(block); fo.write(block); n += len(block)
    return h.hexdigest(), n


def sha256(p):  # the copy is this run's own file
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        while block := fh.read(1 << 24):
            h.update(block)
    return h.hexdigest()


if not hasattr(os, "O_NOATIME"):
    print("STOP: O_NOATIME is not available on this platform"); sys.exit(4)
rec = {"schema": "ref-c2c1-stage/1", "host": socket.gethostname(), "uid": os.getuid(),
       "user": pwd.getpwuid(os.getuid()).pw_name, "platform": platform.platform(), "python": sys.version,
       "O_NOATIME": os.O_NOATIME, "root": str(ROOT), "started_utc": utc(time.time()), "files": {}}
print(f"O_NOATIME = {os.O_NOATIME} ({oct(os.O_NOATIME)}) on {rec['platform']}; running as {rec['user']} uid {rec['uid']}")
ok = {}
for key, src in (("CV", CV), ("MC", MC)):
    before = stat(src)
    dest = ROOT / NAME[key]
    try:
        digest, n = copy_noatime(src, dest)
    except PermissionError as e:
        print(f"STOP: {key}: the O_NOATIME open of {src} raised {e} (owner {before['owner']})"); sys.exit(4)
    after = stat(src)
    copy = sha256(dest)
    f = {"source": str(src), "copy": str(dest), "source_before": before, "source_after": after,
         "atime_moved": before["atime"] != after["atime"], "digest_through_noatime_open": digest, "bytes": n,
         "copy_reread_sha256": copy, "pin": PIN[key]}
    f["pass"] = (digest == copy == PIN[key]) and not f["atime_moved"] and before["owner"] == rec["user"]
    rec["files"][key] = f; ok[key] = f["pass"]
    print(f"{key}: owner {before['owner']} mode {before['mode']} bytes {n}; atime before {before['atime_utc']} "
          f"after {after['atime_utc']} (moved: {f['atime_moved']}); sha256 through the noatime open {digest}; "
          f"copy re-read {copy}; pin {PIN[key]}; pass {f['pass']}")
rec |= {"verdict": "PASS" if all(ok.values()) else "FAIL", "written_utc": utc(time.time())}
(L / "stage.json").write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
print(json.dumps({"verdict": rec["verdict"], "stage_json_sha256": sha256(L / "stage.json")}))
sys.exit(0 if all(ok.values()) else 1)
PYEOF
rc=$?
echo "stage python rc=$rc"
ls -l "$ROOT"
[ $rc = 0 ] || { echo "STOP: staging did not pass (final; to the director)"; finish 4; }
finish 0
