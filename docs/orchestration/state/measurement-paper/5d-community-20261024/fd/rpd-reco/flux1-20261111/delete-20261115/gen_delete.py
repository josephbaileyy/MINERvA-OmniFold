#!/usr/bin/env python3
"""Generate flux1_delete.py (step B) on the Mac from committed inputs and the held-out prestage.json.

usage: python3 gen_delete.py <prestage.json> <out flux1_delete.py>     (run from the top of a checkout)

Inputs, each checked:
- step A's inventory output, stepA/inventory/session.out: every entry's kind, bytes and path, the listing digest;
- prestage.json (held out of git; sha256 99528ac8..., listed in ../run-61206960/README.md): each staged copy's
  recorded sha256, its original's path and the original's stat_before;
- the committed files that the records' digests come from (../run-61206960/records/, ../production-config.ready.json,
  ../tools/fence_overlap.py);
- git at 763ab4dd for the 5 originals that were files of the job's /dev/shm repository copy.
The scope is the director's of 2026-11-15: delete the clone, the 69 staged copies and the records; keep the 12 factor
products, run/flux-extract.json, run/prestage.json and .rpd-private/ in place.
flux1_delete.py gets step A's listing() and canon() verbatim (by AST), so both compute the same digest.
"""
import ast
import hashlib
import json
import os
import subprocess
import sys

HERE = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/flux1-20261111"
ROOT = "/pscratch/sd/j/josephrb/rpd-reco-flux-20261111"
PRESTAGE_SHA = "99528ac8e1d2cc918cde01db73f0ba946e7ff3b473ce09fc614e24615772d3b7"
CLONE_SHA = "9a85268d4f113460ef94c682f15ca7578534ffc7ce46da1348eefd6d848fd71f"
TREE_SHA = "6e9a273506598728091867436ef2fa562f3418f9726175d2d43bfb0ddce6ee89"
REPO_SHM = "/dev/shm/limres-rpd-flux1/repo/"
GIT_PIN = "763ab4ddcea2d2d3dce56138f8aa7ae7fab4bbe6"
KEEP_FILES = [f"run/flux-factors-{p}.npz" for p in ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O",
                                                     "1P")] + ["run/flux-extract.json", "run/prestage.json"]
KEEP_TREES = [".rpd-private"]
DELETE_TREES = ["clone", "run/original-inputs", "run/mat-data", "run/prepare-check", "run/staged", "run/real-mnv-check",
                "run/tmp", "tools"]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def git_bytes(ref, path):
    return subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, check=True).stdout


def main(prestage_path, out):
    pb = open(prestage_path, "rb").read()
    assert sha(pb) == PRESTAGE_SHA, "prestage.json is not the run's (sha256)"
    pre = json.loads(pb)
    inv = {}
    tree_sha = None
    for line in open(f"{HERE}/delete-20261115/stepA/inventory/session.out"):
        if line.startswith("entry\t"):
            _, k, s, r, t = line.rstrip("\n").split("\t")
            inv[r] = (k, int(s))
        if line.startswith("tree entries"):
            tree_sha = line.split("listing-sha256 ")[1].split()[0]
            n_entries = int(line.split()[2])
        if line.startswith("clone/ entries"):
            assert line.split("listing-sha256 ")[1].split()[0] == CLONE_SHA
    assert tree_sha == TREE_SHA and n_entries == 24422, (tree_sha, n_entries)

    rel = lambda p: p[len(ROOT) + 1:]
    staged, originals, shm = {}, {}, {}
    for v in pre["files"].values():
        staged[rel(v["staged"])] = v["sha256"]
        if v["original"].startswith(REPO_SHM):
            shm[rel(v["staged"])] = (v["original"][len(REPO_SHM):], v["sha256"])
        else:
            sb = v["stat_before"]
            originals[rel(v["staged"])] = (v["original"], sb["bytes"], sb["mtime_ns"])
    for v in pre["mat_dependencies"]:
        staged[rel(v["staged"])] = v["sha256"]
        sb = v["stat_before"]
        originals[rel(v["staged"])] = (v["original"], sb["bytes"], sb["mtime_ns"])
    assert len(staged) == 69 and len(shm) == 5 and len(originals) == 64, (len(staged), len(shm), len(originals))
    # the 5 repository originals are committed: their recorded digests equal git's blobs at the clone pin
    gitcheck = []
    for r, (path, want) in sorted(shm.items()):
        got = sha(git_bytes(GIT_PIN, path))
        assert got == want, (path, got, want)
        gitcheck.append(f"{r} = {GIT_PIN[:8]}:{path} sha256 {got}")

    # records: every other file outside the kept set and the clone, with its committed counterpart
    REC = f"{HERE}/run-61206960/records"
    by_original_name = {os.path.basename(v["original"]): v["sha256"] for v in pre["files"].values()}
    explicit = {
        "production-config.ready.json": f"{HERE}/production-config.ready.json",
        "run/prepare-check/staged/config.json": f"{HERE}/production-config.ready.json",
        "tools/fence_overlap.py": f"{HERE}/tools/fence_overlap.py",
        "run/staged/config.json": f"{REC}/run/extract-config.json",
        "run/staged/prestage-reference.json": f"{REC}/run/prestage-reference.json",
    }
    records, sources = {}, {}
    for r, (k, s) in sorted(inv.items()):
        if k != "f" or r in KEEP_FILES or r.split("/")[0] in KEEP_TREES or r in staged:
            continue
        if r.startswith("run/prepare-check/staged/") and r != "run/prepare-check/staged/config.json":
            name = r.split("/")[-1].split("-", 1)[1]
            records[r], sources[r] = by_original_name[name], f"prestage.json files: the original named {name}"
            continue
        src = explicit.get(r, f"{REC}/{r}")
        b = open(src, "rb").read()
        assert len(b) == s, (r, src, len(b), s)
        records[r], sources[r] = sha(b), src
    files = [r for r, (k, _) in inv.items() if k == "f"]     # step A prints every entry outside clone/
    assert not any(r.startswith("clone/") for r in inv), "step A's entries include clone/"
    assert len(files) == len(records) + len(staged) + len(KEEP_FILES) + 1, "a file outside clone/ is unclassified"
    for r in KEEP_FILES:
        assert inv[r][0] == "f", r
    keep_after = sorted(["run", ".rpd-private"] + KEEP_FILES + [r for r in inv if r.startswith(".rpd-private/")])

    src = open(f"{HERE}/delete-20261115/flux1_inventory.py").read()
    tree = ast.parse(src)
    funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("listing", "canon")]
    assert len(funcs) == 2
    lines = src.splitlines()
    shared = "\n\n\n".join("\n".join(lines[f.lineno - 1:f.end_lineno]) for f in funcs)

    body = TEMPLATE.replace("@@SHARED@@", shared)
    consts = {
        "ROOT": ROOT, "TREE_SHA": TREE_SHA, "TREE_ENTRIES": n_entries, "CLONE_SHA": CLONE_SHA,
        "DELETE_TREES": DELETE_TREES, "KEEP_AFTER": keep_after,
        "STAGED": dict(sorted(staged.items())), "ORIGINALS": dict(sorted(originals.items())),
        "RECORDS": dict(sorted(records.items())),
        "DELETE_FILES": sorted(r for r in list(records) if r.split("/")[0] != "tools" and not any(
            r.startswith(t + "/") for t in DELETE_TREES)),
    }
    body = body.replace("@@CONSTS@@", "\n".join(f"{k} = {v!r}" for k, v in consts.items()))
    open(out, "w").write(body)
    print(f"generated {out}: sha256 {sha(open(out, 'rb').read())}")
    print(f"staged copies {len(staged)} (originals on pscratch {len(originals)}, repository originals {len(shm)}); "
          f"records {len(records)}; clone/ by its listing digest {CLONE_SHA[:16]}; kept files {len(KEEP_FILES) + 1}")
    print(f"delete trees {DELETE_TREES}; delete files {len(consts['DELETE_FILES'])}; keep after {len(keep_after)} entries")
    for g in gitcheck:
        print("git check: " + g)
    for r in sorted(sources):
        print(f"record {r}  <-  {sources[r]}  {records[r][:16]}")
    return 0


TEMPLATE = r'''#!/usr/bin/env python3
"""RPD-RECO flux connect 1, cleanup step B: delete the clone, the 69 staged copies and the records from the run's
pscratch root, and keep the 12 factor products, run/flux-extract.json, run/prestage.json and .rpd-private/ in place
(the director's scope, 2026-11-15). Generated by gen_delete.py; Python >= 3.6, stdlib only.

Order. Nothing is removed unless every check passes:
1. a login node; ROOT a directory, not a symlink; O_NOATIME available;
2. the whole listing (step A's listing() and canon(), verbatim) has step A's digest and entry count, and clone/'s own
   listing has step A's clone digest;
3. every staged copy's sha256, read with O_NOATIME, equals its recorded digest, and each pscratch original's lstat
   (no read) shows the recorded stat_before size and mtime_ns;
4. every record's sha256, read with O_NOATIME, equals its committed counterpart's.
Then the DELETE_FILES are removed by literal path, then the DELETE_TREES (shutil.rmtree, which does not follow
symlinks). After, the remaining listing must be exactly KEEP_AFTER.
Exit: 0 done and verified; 4 STOP with nothing removed; 8 the remaining tree is not KEEP_AFTER; 9 a removal failed.
Usage: /usr/bin/python3 -B flux1_delete.py
"""
import hashlib
import os
import shutil
import socket
import stat
import sys
import time

@@CONSTS@@


@@SHARED@@


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha_noatime(path, noatime):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | noatime)
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


def main(root=ROOT, require_login=True, noatime=None, originals=None):
    originals = ORIGINALS if originals is None else originals
    if noatime is None:
        noatime = getattr(os, "O_NOATIME", None)
        if noatime is None:
            print("STOP: os.O_NOATIME is not available")
            return 4
    host = socket.gethostname()
    print("delete host %s python %s start %s root %s" % (host, sys.version.split()[0], now(), root))
    if require_login and not host.startswith("login"):
        print("STOP: not a login node: %s" % host)
        return 4
    if not os.path.lexists(root) or not stat.S_ISDIR(os.lstat(root).st_mode):
        print("STOP: %s is missing or not a directory" % root)
        return 4
    entries, problems = listing(root, noatime)
    got = hashlib.sha256(canon(entries).encode()).hexdigest()
    clone = [e for e in entries if e[0] == "clone" or e[0].startswith("clone/")]
    cgot = hashlib.sha256(canon(clone).encode()).hexdigest()
    print("listing entries %d sha256 %s (step A %d %s); clone sha256 %s (step A %s); problems %d"
          % (len(entries), got, TREE_ENTRIES, TREE_SHA, cgot, CLONE_SHA, len(problems)))
    if got != TREE_SHA or len(entries) != TREE_ENTRIES or cgot != CLONE_SHA or problems:
        print("STOP: the tree is not step A's; nothing removed")
        return 4
    bad = 0
    for r, want in sorted(STAGED.items()):
        g = sha_noatime(os.path.join(root, r), noatime)
        ok = g == want
        line = "staged %s sha256 %s %s" % (r, g, "OK" if ok else "DIFFERS from %s" % want)
        if r in originals:
            o, size, mtime = originals[r]
            try:
                st = os.lstat(o)
                ook = stat.S_ISREG(st.st_mode) and st.st_size == size and st.st_mtime_ns == mtime
                line += "; original %s %s" % (o, "present, size and mtime as recorded" if ook else
                                              "CHANGED (size %d mtime %d)" % (st.st_size, st.st_mtime_ns))
            except OSError as e:
                ook = False
                line += "; original %s MISSING (%s)" % (o, e.strerror)
            ok = ok and ook
        else:
            line += "; original committed in git (gen_delete.py's check)"
        bad += not ok
        print(line)
    for r, want in sorted(RECORDS.items()):
        g = sha_noatime(os.path.join(root, r), noatime)
        bad += g != want
        print("record %s sha256 %s %s" % (r, g, "OK" if g == want else "DIFFERS from %s" % want))
    if bad:
        print("STOP: %d check(s) failed; nothing removed" % bad)
        return 4
    print("checks passed: %d staged copies, %d records, at %s" % (len(STAGED), len(RECORDS), now()))
    failed = 0
    for r in DELETE_FILES:
        try:
            os.remove(os.path.join(root, r))
            print("removed file %s" % r)
        except OSError as e:
            failed += 1
            print("REMOVE FAILED %s: %s" % (r, e.strerror))
    for t in DELETE_TREES:
        errs = []
        shutil.rmtree(os.path.join(root, t), onerror=lambda f, p, e: errs.append((p, str(e[1]))))
        failed += len(errs)
        print("removed tree %s%s" % (t, "" if not errs else "; %d errors, first %s" % (len(errs), errs[0])))
    if failed:
        print("removal errors: %d" % failed)
        return 9
    after, _ = listing(root, noatime)
    names = sorted(e[0] for e in after)
    ok = names == sorted(KEEP_AFTER)
    print("after: %d entries, %s; %s" % (len(names), "exactly the kept set" if ok else "NOT the kept set",
                                       ", ".join(names)))
    print("DELETE :: %s end %s" % ("DONE" if ok else "INCOMPLETE", now()))
    return 0 if ok else 8


if __name__ == "__main__":
    sys.exit(main())
'''

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
