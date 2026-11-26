# RPD-RECO amendment 1's read-only sidecar probe (amendment sections 2 and 8; the director's GO to write it,
# 2026-11-26), run on login02 by sidecar-probe.sh. V_F Phase 2's fetch pattern (fd/receipts-vf/p2/fetch_vfp2_remote.py):
#   1. a pre-flight lstat of every component below BASE of every path, before any file is opened (lstat moves no
#      atime and reads no link): any symlink, non-directory parent or non-regular final file refuses; a missing file is
#      reported (the purge risk) and the probe exits 9 after the report;
#   2. the 12 omnifiles and lat_zero: stat only (lstat; never opened), reporting size, mtime, atime and the purge
#      exposure (atime + 56 days);
#   3. the sidecar only: opened O_NOATIME|O_NOFOLLOW|O_NONBLOCK through a no-symlink descriptor walk, fstat'ed as a
#      regular file, streamed through sha256 and closed; its atime (lstat before and after) must not move; the digest
#      must be the pinned one.
# Nothing is written on the cluster: the report is one JSON object on stdout, messages go to stderr. Exit 0: every path
# present, the sidecar's digest the pin and its atime unchanged; 9: anything else after the report; 2: refused before
# any read. Python 3.6 compatible (the login node's /usr/bin/python3).
import hashlib
import json
import os
import stat
import sys
import time

BASE = "/pscratch/sd/j/josephrb/"
SIDECAR = BASE + "rdx-20261112b/out/dumps/truthx_RDX_ALL.npz"
SIDECAR_SHA256 = "641ba34c5ebde6d1881c705b862fab144a6fbb8a58ef3d84e59f1c8ba030a79e"
PLAYLISTS = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")
STAT_ONLY = tuple(BASE + "rdx-20261112b/out/evloop/runEventLoopOmniFold_RDX_%s.root" % pl for pl in PLAYLISTS) + (
    BASE + "measurement-paper/phase1/mp1/s1/lateral/lat_zero.npz",)
PURGE_DAYS = 56


def stop(why, rc=2):
    sys.stderr.write("STOP probe: %s\n" % why)
    sys.stderr.flush()
    sys.exit(rc)


def utc(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def preflight(path):
    """lstat each component below BASE. Returns (status, lstat result or None, detail): "ok" for a regular final file
    under plain directories, "missing" when a component does not exist, "refused" for a symlink or a wrong type."""
    if not path.startswith(BASE) or ".." in path.split("/"):
        return "refused", None, "not under %s" % BASE
    cur = BASE.rstrip("/")
    parts = path[len(BASE):].split("/")
    for i, comp in enumerate(parts):
        cur = cur + "/" + comp
        try:
            st = os.lstat(cur)
        except FileNotFoundError:
            return "missing", None, "%s does not exist" % cur
        except OSError as e:
            return "refused", None, "%s: %s" % (cur, e.strerror)
        if stat.S_ISLNK(st.st_mode):
            return "refused", None, "%s is a symlink" % cur
        last = i == len(parts) - 1
        if last and not stat.S_ISREG(st.st_mode):
            return "refused", None, "%s is not a regular file" % cur
        if not last and not stat.S_ISDIR(st.st_mode):
            return "refused", None, "%s is not a directory" % cur
        if last:
            return "ok", st, ""
    return "refused", None, "empty path"


def stat_row(path, st):
    return {"path": path, "size": st.st_size, "mtime": utc(st.st_mtime), "atime": utc(st.st_atime),
            "purge_exposure_from": utc(st.st_atime + PURGE_DAYS * 86400), "inode": st.st_ino}


def open_nofollow(path):
    """Each directory O_DIRECTORY|O_NOFOLLOW relative to its parent's descriptor; the file O_NOATIME|O_NOFOLLOW|
    O_NONBLOCK. A symlink anywhere below BASE refuses."""
    parts = path[len(BASE):].split("/")
    try:
        d = os.open(BASE.rstrip("/"), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as e:
        stop("cannot open %s: %s" % (BASE, e), 9)
    try:
        for comp in parts[:-1]:
            try:
                nd = os.open(comp, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=d)
            except OSError as e:
                stop("%s: directory component %r: %s" % (path, comp, e), 9)
            os.close(d)
            d = nd
        try:
            return os.open(parts[-1], os.O_RDONLY | os.O_NOATIME | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=d)
        except OSError as e:
            stop("cannot open %s O_NOATIME|O_NOFOLLOW: %s" % (path, e), 9)
    finally:
        os.close(d)


def main():
    if not hasattr(os, "O_NOATIME"):
        stop("this platform has no O_NOATIME")
    try:
        bst = os.lstat(BASE.rstrip("/"))
    except OSError as e:
        stop("%s: %s" % (BASE, e.strerror))
    if stat.S_ISLNK(bst.st_mode) or not stat.S_ISDIR(bst.st_mode):
        stop("%s is not a plain directory" % BASE)
    report = {"schema": "rpd-reco-sidecar-probe/1", "started": utc(time.time()), "stat_only": [], "sidecar": None}
    ok = True
    pre = [(p, preflight(p)) for p in STAT_ONLY + (SIDECAR,)]       # every path before any file is opened
    refused = ["%s: %s" % (p, r[2]) for p, r in pre if r[0] == "refused"]
    if refused:
        stop("pre-flight, before any file was opened: %d refused:\n  %s" % (len(refused), "\n  ".join(refused)))
    for path, (status, st, detail) in pre[:-1]:
        if status == "ok":
            report["stat_only"].append(stat_row(path, st))
        else:
            report["stat_only"].append({"path": path, "missing": detail})
            ok = False
    status, st0, detail = pre[-1][1]
    if status != "ok":
        report["sidecar"] = {"path": SIDECAR, "missing": detail}
        ok = False
    else:
        fd = open_nofollow(SIDECAR)
        try:
            st = os.fstat(fd)
            if not stat.S_ISREG(st.st_mode) or st.st_ino != st0.st_ino:
                stop("%s changed between the pre-flight and the open" % SIDECAR, 9)
            h, n = hashlib.sha256(), 0
            while True:
                b = os.read(fd, 1 << 22)
                if not b:
                    break
                h.update(b)
                n += len(b)
        finally:
            os.close(fd)
        st1 = os.lstat(SIDECAR)
        digest = h.hexdigest()
        row = stat_row(SIDECAR, st0)
        row.update({"bytes_read": n, "sha256": digest, "sha256_pinned": SIDECAR_SHA256,
                    "sha256_matches": digest == SIDECAR_SHA256, "atime_after": utc(st1.st_atime),
                    "atime_unchanged": st1.st_atime == st0.st_atime, "size_matches_read": n == st0.st_size})
        report["sidecar"] = row
        ok = ok and row["sha256_matches"] and row["atime_unchanged"] and row["size_matches_read"]
    report["verdict"] = "PASS" if ok else "FAIL"
    sys.stdout.write(json.dumps(report, indent=1, sort_keys=True) + "\n")
    sys.stdout.flush()
    sys.exit(0 if ok else 9)


if __name__ == "__main__":
    main()
