#!/usr/bin/env python3
"""Per-period 2D benchmark: delete the operand copies under a ledger row (the director's ruling of 2026-11-07: keep the
copies until the outcome record is merged, then delete them under a ledger row with each digest, path and an rc-0
removal, as REF-C2C1 stage 4 did, #846).

Scope, by literal path only (TARGETS below, generated from the committed receipts):
  .../per-period-benchmark-20261106/read/copies           the 39 O_NOATIME operand copies + copies.json + verify.json
                                                           (receipts/read/verify.json, SHA256SUMS)
connect1/smoke-copies (2 smoke-test copies) is NOT in scope: the director's GO named the 39 read copies only.
copies.json and verify.json are byte-identical to the committed receipts/read/ copies (SHA256SUMS) and are removed so
the directory can be removed. The originals, the code deploys, the receipts R/ dirs and every other path are not touched.

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

LEDGER = "/pscratch/sd/j/josephrb/per-period-benchmark-20261106/delete-ledger"
TARGETS = {
    "/pscratch/sd/j/josephrb/per-period-benchmark-20261106/read/copies": {
        "ER__xsec.root": "a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef",
        "copies.json": "5e3dd182079ae73d00ec0e650214d24399bb6a79b047541c75868058304c6156",
        "cov_ptpl_minerva_inclusive_6GeV.root": "6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3",
        "pu_CTRL_s42__xsec.root": "a6d3a69119aba5636401371d9f119b30a8be9da154f85ac90b25d0bc41507a8a",
        "pu_PA_b01__xsec.root": "32806b61e6800f9b157143ccd33b92e64f88c8dfa5bfaa62444d014795dbf5b4",
        "pu_PA_b02__xsec.root": "c555a4a22c62966dcf6de2f3dff497e9033e13b97cdc3d7d7907006ea7ddb5c6",
        "pu_PA_b03__xsec.root": "f927a3e66aa13394fe802faf3c73fccbda7c88830d3dd420e3f9822d9e960d95",
        "pu_PA_b04__xsec.root": "ae68f5c44f072724f61f3aed47a43a21ad636f263c4f564917288db06478ebda",
        "pu_PA_b05__xsec.root": "107de3388d522f462d28d7e722acd8ff1691a225c207200ac6f332dcf57d4718",
        "pu_PA_b06__xsec.root": "24f00a80343adfe58d1c1a2fd35749e48cdb5893fe2c0fdf0542a10817dcee80",
        "pu_PA_b07__xsec.root": "5c9c9adebe1205f0268569d76f881ad3e31155048daebd3c1f0f58b4592b1ce8",
        "pu_PA_b08__xsec.root": "7f442829abff9922e6cc08f0572c7bd742be2f0d272cfe641a3f7edcb8b71564",
        "pu_PA_b09__xsec.root": "575ace0ad5e441bffeaa2f881a09dc3e3867de4178e5005fe6a3f64ad874ca3a",
        "pu_PA_b10__xsec.root": "029ebe4ab60908bc7898d70511fd643c85e19103d4d242838e903d993fc10a82",
        "pu_PA_s42__xsec.root": "c2fb12944635294777030c98fd97503b8016be8c89b16ec70b5cadd0cec84131",
        "pu_PA_s43__xsec.root": "4515dd3bc1ac8b3b37821bc7a69f823428c8202b3d5b946d97345b5818a5e3a5",
        "pu_PB_b01__xsec.root": "34fe5c49f28a9a7e907c363a7995f7fb4c3a13707ce568409a1f02a1ea5b1ac8",
        "pu_PB_b02__xsec.root": "35c3753b0d66b8e86e3cbdf226fb205af56ae0d5f3156a9f2dac64ba5b7f9d04",
        "pu_PB_b03__xsec.root": "7a43976fc2bd25f32744ba81d0d843b335eed76d8d71cee83d4dd26ccd9b5aac",
        "pu_PB_b04__xsec.root": "ca1fa2db02eaad43cfd1cc5b97011a9b0a34e7db0ff5e991c0311e636ce724cd",
        "pu_PB_b05__xsec.root": "bc975f6efe9f0dc1f6e0a85e4b202d491241ea188177b0249e87739e35044cf7",
        "pu_PB_b06__xsec.root": "18c53b300133322cb4897267f39bf5ae158aeef4e30c1c45b500f03086acc23d",
        "pu_PB_b07__xsec.root": "338af18f283a42267c65862d2c9e0d9d9ab5b430dcad42cb31ece182eb409bbf",
        "pu_PB_b08__xsec.root": "ff5e678a848e40bc2a146ec905f76e1e7ab7c1e8f6c859991caf93b008b88b42",
        "pu_PB_b09__xsec.root": "98986966d2056047b9d1a9687e941a5e679003a23b8ee30874071fe64f4247f9",
        "pu_PB_b10__xsec.root": "914b755cafa9a4afa9fdbf6abdeb199b64841ffcbf84e304a1bf927459ee75c0",
        "pu_PB_s42__xsec.root": "356b1293a227b318f552faf725e25796ef77fdc4fed301684f2844dfb74d24dc",
        "pu_PB_s43__xsec.root": "2f1b82322818d589579addcc50367e4bcf3ba9b370f6caef49339379bad9ecf1",
        "pu_PC_b01__xsec.root": "c3eb171cc83aca648dbc569e6a4eaeddec4d1f50fc61b628f137b9bafbcde522",
        "pu_PC_b02__xsec.root": "28f52d118f61717e57c5ee57d9ecda719139c2017ce8d72d880b9a5f0ba90d78",
        "pu_PC_b03__xsec.root": "32c3186f9da97eff9686fd7ced01350ab27a3e6c6f57acb3738d42ec66903ed5",
        "pu_PC_b04__xsec.root": "b079a3316c6e56b031110dbb82a2cbf30322d67fbb6f4e819ee1cacf3c0991d5",
        "pu_PC_b05__xsec.root": "290c6a2bc7f58705f5d45b7ff6cf94ad43e5dfee61c7bdc0381439c280d6a737",
        "pu_PC_b06__xsec.root": "2e47fef20e0e7c770c952a00ab8966e07191b000b93250885e82cdaeca39468e",
        "pu_PC_b07__xsec.root": "dbcf7781cab3ce41565b2c0accfbc955bf9dc1025c85a44541e3f22a3ef1f8e8",
        "pu_PC_b08__xsec.root": "cb0dddcc40d8fe12cdae1d95353a1d3a6db6556f42ae9e38b3c09a91a9b5346f",
        "pu_PC_b09__xsec.root": "284109be1f37542ffec5d3418b24917e7f7b1c62087ee59a69213c61c3fca989",
        "pu_PC_b10__xsec.root": "fe61b6f9194acf6ce000f1931e10749d2d7eef064b8d72bac7cabd830e52e8f2",
        "pu_PC_s42__xsec.root": "ea4a4d16cfc66170b37933a883cef3c905f685f5234c11d9ef0854a8439c7cbc",
        "pu_PC_s43__xsec.root": "0ca364aa2a1789b85fcce7bc09873558671491428f61d3c5b98177300df09896",
        "verify.json": "1b9e6feaa47ecffbc042fff851961549e67d64920374a422bd4b1f79f0ccad15",
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
