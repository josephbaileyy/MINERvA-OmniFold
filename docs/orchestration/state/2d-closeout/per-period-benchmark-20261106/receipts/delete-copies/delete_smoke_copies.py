#!/usr/bin/env python3
"""Per-period 2D benchmark: delete the operand copies under a ledger row (the director's ruling of 2026-11-07: keep the
copies until the outcome record is merged, then delete them under a ledger row with each digest, path and an rc-0
removal, as REF-C2C1 stage 4 did, #846).

Scope, by literal path only (TARGETS below, from receipts/connect1/smoke.json): the SECOND ledger row,
  .../per-period-benchmark-20261106/connect1/smoke-copies   the 2 smoke-test copies (the director's GO of 2026-11-07).
The first row (read/copies, 41 files) ran as delete_copies.py; this file is that code with only TARGETS and LEDGER changed.
The originals, the code deploys, the receipts R/ dirs and every other path are not touched.

Order: refuse unless on a login node and the ledger dir is new; for EVERY root, the entries must be exactly its
declared files, all regular, and each file's sha256 by an O_NOATIME read must equal its declared digest; only when every
root passes is anything removed (os.remove per literal path, then os.rmdir); after, each path must be absent.
Exit: 0 deleted and verified absent; 4 STOP, nothing deleted; 8 something still present; 9 a removal failed.
Usage: /usr/bin/python3 delete_copies.py            (production; Python >= 3.6, stdlib only)
"""
import hashlib
import json
import os
import socket
import sys
import time

LEDGER = "/pscratch/sd/j/josephrb/per-period-benchmark-20261106/delete-ledger-smoke"
TARGETS = {
    "/pscratch/sd/j/josephrb/per-period-benchmark-20261106/connect1/smoke-copies": {
        "cov_ptpl_minerva_inclusive_6GeV.root": "6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3",
        "pu_PA_b01__xsec.root": "32806b61e6800f9b157143ccd33b92e64f88c8dfa5bfaa62444d014795dbf5b4",
    },
}


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + ".%03dZ" % (int(time.time() * 1000) % 1000)


def sha_noatime(path, flag):
    fd = os.open(path, os.O_RDONLY | flag)
    h = hashlib.sha256()
    try:
        while True:
            b = os.read(fd, 1 << 22)
            if not b:
                break
            h.update(b)
    finally:
        os.close(fd)
    return h.hexdigest()


def run(targets, ledger, flag, require_login=True):
    """Returns (rc, record). Writes record to ledger/ledger.json and a log to ledger/ledger.log."""
    if require_login and not socket.gethostname().startswith("login"):
        return 4, {"stop": "not a login node: %s" % socket.gethostname()}
    if os.path.exists(ledger):
        return 4, {"stop": "ledger dir exists: %s" % ledger}
    os.makedirs(ledger)
    log = open(os.path.join(ledger, "ledger.log"), "w")
    rec = {"host": socket.gethostname(), "python": sys.version.split()[0], "start": now(), "roots": {}}

    def say(s):
        log.write(s + "\n")
        log.flush()

    def finish(rc):
        rec["rc"], rec["end"] = rc, now()
        say("rc %d at %s" % (rc, rec["end"]))
        log.close()
        with open(os.path.join(ledger, "ledger.json"), "w") as fh:
            json.dump(rec, fh, indent=1)
            fh.write("\n")
        return rc, rec

    say("node %s %s python %s" % (rec["host"], rec["start"], rec["python"]))
    # ---- every check first; nothing is removed unless every root passes
    for root, want in targets.items():
        r = {"declared": want, "before": [], "measured": {}}
        rec["roots"][root] = r
        if not os.path.isdir(root):
            say("STOP: %s is not a directory" % root)
            return finish(4)
        for name in sorted(os.listdir(root)):
            p = os.path.join(root, name)
            st = os.lstat(p)
            kind = "f" if os.path.isfile(p) and not os.path.islink(p) else ("d" if os.path.isdir(p) else "other")
            r["before"].append([kind, st.st_size, name])
            say("before %s %s %d %s" % (root, kind, st.st_size, name))
        names = sorted(n for k, _, n in r["before"])
        if names != sorted(want) or any(k != "f" for k, _, _ in r["before"]):
            r["unexpected"] = sorted(set(names) - set(want))
            r["missing"] = sorted(set(want) - set(names))
            say("STOP: %s holds something other than exactly its %d declared files: unexpected %s, missing %s"
                % (root, len(want), r["unexpected"], r["missing"]))
            return finish(4)
        for name, digest in sorted(want.items()):
            got = sha_noatime(os.path.join(root, name), flag)
            r["measured"][name] = got
            say("sha256 (O_NOATIME) %s/%s %s declared %s %s" % (root, name, got, digest, "OK" if got == digest else "DIFFERS"))
            if got != digest:
                say("STOP: a digest differs; nothing deleted")
                return finish(4)
    # ---- the deletion, by literal path
    for root, want in targets.items():
        r = rec["roots"][root]
        r["removed"] = []
        for name in sorted(want):
            p = os.path.join(root, name)
            t = now()
            try:
                os.remove(p)
            except OSError as e:
                say("%s rm FAILED %s: %s" % (t, p, e))
                return finish(9)
            r["removed"].append([t, p])
            say("%s rm %s" % (t, p))
        t = now()
        try:
            os.rmdir(root)
        except OSError as e:
            say("%s rmdir FAILED %s: %s" % (t, root, e))
            return finish(9)
        r["rmdir"] = [t, root]
        say("%s rmdir %s" % (t, root))
    # ---- after
    left = []
    for root, want in targets.items():
        for p in [os.path.join(root, n) for n in sorted(want)] + [root]:
            present = os.path.lexists(p)
            say("after %s %s" % ("STILL PRESENT" if present else "absent", p))
            if present:
                left.append(p)
    rec["still_present"] = left
    return finish(8 if left else 0)


if __name__ == "__main__":
    flag = getattr(os, "O_NOATIME", None)
    if flag is None:
        print("REFUSED: no os.O_NOATIME on this platform", file=sys.stderr)
        sys.exit(4)
    rc, _ = run(TARGETS, LEDGER, flag)
    sys.exit(rc)
