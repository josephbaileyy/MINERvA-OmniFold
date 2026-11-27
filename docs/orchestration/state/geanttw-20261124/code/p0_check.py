#!/usr/bin/env python3
"""P0's controls C0a–C0f (DECLARATION.md §4 P0.4), read on a login node after both 1L jobs end.

    python3 -I p0_check.py --B B --deploy B/deploy --ref REF_COPY.root --ref-sha SHA256 [--json OUT]

Inputs, all under B (the declared layout):
  run/p0/<build>/runEventLoopOmniFold_GEANTTW_<build>_1L.root and run/p0/<build>/strace.<build>.1L, for pin and pat;
  run/p0/build.log; the deploy's 2d-unfolding/playlist_manifests/1L_{MC,Data}.txt; REF_COPY, the O_NOATIME copy of
  MP-1 S1's 1L zero loop, whose sha256 must equal --ref-sha (read by the caller from the committed manifest).
Each control prints `C0x PASS|FAIL <evidence>`; exit 0 only if every control and every build.log CHECK passes.

  C0a  each strace shows libMAT.so and libMAT-MINERvA.so opened, every such open resolves under that build's
       prefix-<build>/lib, and no successful open resolves to a .so under the production opt/lib.
  C0b  in the patched dump, BOTH mc_signal_reco and mc_truth_denom carry w_truth and all six targets; in each of the
       two trees every target differs from w_truth (bitwise) in at least one entry; every target is finite and > 0.
  C0c  in the pinned dump, the same trees carry them, and every target equals w_truth bitwise in every entry.
  C0d  dumpcmp(pin, pat) passes with exactly the six targets exempt.
  C0e  every successful open, placed by the path strace -y gives its descriptor (the binary runs in B's work dir,
       so its own opens are relative) and resolved through symlinks, lies in B (not through a symlink out of it) or in an allowed
       family: the 1L manifests' AnaTuples (exact paths), the production opt/lib/data, opt/etc/MParamFiles/data and
       opt/etc/MATFluxAndReweightFiles trees (each resolved through its symlinks), the conda ROOT env, or a system root.
       The director's C0e ruling of 2026-11-26 adds three environment families, each tied to how it was opened:
       Lmod's tree by a child process only (not the binary's own, which is the log's first successful open), seven
       library directories as an O_DIRECTORY open only, and two exact files (ENV_CHILD_ROOT, ENV_DIRS, ENV_FILES).
       Everything else FAILs and is listed, and so does a relative open strace gives no path for.
  C0f  dumpcmp(reference, pin) passes, allowing only the GEANT universe branches as extras; the reference copy's
       sha256 equals --ref-sha.
The allowed families are fixed here. Only the tests' smoke mode (GEANTTW_SMOKE_B set and equal to --B) may replace
the production opt and conda paths, through GEANTTW_TEST_PROD_OPT and GEANTTW_TEST_CONDA.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
import uproot

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("dumpcmp", HERE / "dumpcmp.py")
dumpcmp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dumpcmp)

TARGETS = [f"w_truth_GEANT_{b}_{i}" for b in ("Neutron", "Pion", "Proton") for i in (0, 1)]
TARGET_RE = r"w_truth_GEANT_(Neutron|Pion|Proton)_[01]"
UNIVERSE_RE = r"w_(truth|reco|bkg)_GEANT_(Neutron|Pion|Proton)_[01]"
TREES = ("mc_signal_reco", "mc_truth_denom")
CHECKS = ("DIFF_EQUALS_UPSTREAM", "SOURCE_PROVENANCE", "RPATH_CLEAN", "LIBMAT_IDENTICAL", "LIBMATMINERVA_DIFFER")
PROD_OPT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt"
CONDA = "/global/homes/j/josephrb/.conda/envs/root_6_28"
SYSTEM = ("/usr/", "/lib/", "/lib64/", "/etc/", "/proc/", "/sys/", "/dev/")
# Environment reads P0's jobs made, allowed by the director's C0e ruling of 2026-11-26 after their attribution
# (../c0e-attribution/): each no wider than what was seen, and only when opened the way it was seen opened.
ENV_CHILD_ROOT = "/opt/cray/pe/lmod"   # Lmod, by a child process only (a bash sourcing init/bash; Lua's addto)
ENV_DIRS = (   # library directories, as an O_DIRECTORY open only (the main process's library search)
    "/global/common/software/nersc9/darshan/3.4.6-gcc-13.2.1/lib",
    "/opt/cray/libfabric/2.3.1/lib64",
    "/opt/cray/pe/papi/7.3.0.1/lib",
    "/opt/nvidia/hpc_sdk/Linux_x86_64/26.5/cuda/13.2/extras/CUPTI/lib64",
    "/opt/nvidia/hpc_sdk/Linux_x86_64/26.5/cuda/13.2/nvvm/lib64",
    "/opt/nvidia/hpc_sdk/Linux_x86_64/26.5/cuda/13.2/targets/x86_64-linux/lib",
    "/opt/nvidia/hpc_sdk/Linux_x86_64/26.5/math_libs/13.2/targets/x86_64-linux/lib",
)
ENV_FILES = (   # exact files, by path: clang's CUDA detection in cling, and NSS's user lookup
    "/opt/nvidia/hpc_sdk/Linux_x86_64/26.5/cuda/13.2/targets/x86_64-linux/include/cuda.h",
    "/var/lib/sss/mc/passwd",
)
# strace -f -y: a dirfd argument may carry its path (AT_FDCWD</cwd>, 3</dir>), and a returned descriptor carries the
# path the kernel resolved (= 5</abs/path>).
OPEN = re.compile(r'^(?:\[pid\s+)?(\d+)?\]?\s*(?:open|openat)\((?:(?:[A-Z_]+|-?\d+)(?:<[^>]*>)?,\s*)?"([^"]+)".*?'
                  r'(?:= (-?\d+)(?:<([^>]*)>)?|<unfinished \.\.\.>)')
RESUMED = re.compile(r'^(?:\[pid\s+)?(\d+)?\]?\s*<\.\.\. (?:open|openat) resumed>.*= (-?\d+)(?:<([^>]*)>)?')
FLAGS = re.compile(r'"[^"]*",\s*([A-Z0-9_|]+)')   # an open's flags, after its path
UNRESOLVED = "UNRESOLVED-RELATIVE:"


def _opened(path, fdpath):
    """The opened file: the kernel's path from -y when strace gives one, else the argument if absolute. A relative
    argument with no -y path cannot be placed (the opener's cwd is not in the log), so it is marked unresolved and
    no control can pass it."""
    if fdpath:
        return fdpath
    return path if path.startswith("/") else UNRESOLVED + path


def real(p):
    """realpath for a placed path; an unresolved one is returned as it is, never resolved against this cwd."""
    return os.path.realpath(p) if p.startswith("/") else p


def opens_detail(strace_path):
    """(pid, opened, flags) of every open/openat in an strace -f -y log that returned a descriptor (>= 0): the
    line's pid, the opened file (see _opened) and the call's flags, split on '|' (a resumed call keeps its own)."""
    out, pending = [], {}
    for line in Path(strace_path).read_text(errors="replace").splitlines():
        s = line.strip()
        m = OPEN.match(s)
        if m:
            pid, path, rc, fdpath = m.group(1), m.group(2), m.group(3), m.group(4)
            f = FLAGS.search(s)
            flags = set(f.group(1).split("|")) if f else set()
            if rc is None:
                pending[pid] = (path, flags)
            elif int(rc) >= 0:
                out.append((pid, _opened(path, fdpath), flags))
            continue
        r = RESUMED.match(s)
        if r and r.group(1) in pending:
            path, flags = pending.pop(r.group(1))
            if int(r.group(2)) >= 0:
                out.append((r.group(1), _opened(path, r.group(3)), flags))
    return out


def successful_opens(strace_path):
    """The opened file (see _opened) of every open/openat in an strace -f -y log that returned a descriptor (>= 0)."""
    return [p for _, p, _ in opens_detail(strace_path)]


def env_plumbing(r, child, directory):
    """Whether r is one of the environment reads C0e's ruling allows (ENV_*), opened the way it was seen opened:
    Lmod's tree by a child process only, the library directories as an O_DIRECTORY open only, the two files by path."""
    if child and any(under(r, root) for root in _forms(ENV_CHILD_ROOT)):
        return True
    if directory and r in {f for d in ENV_DIRS for f in _forms(d)}:
        return True
    return r in {f for p in ENV_FILES for f in _forms(p)}


def _forms(p):
    """p as written and resolved here (a system path can be a symlink on the machine that runs the tests)."""
    return {p, os.path.realpath(p)}


def under(path, root):
    root = root.rstrip("/") + "/"
    return path == root[:-1] or path.startswith(root)


def c0a(B, prod_opt):
    ev = []
    ok = True
    for b in ("pin", "pat"):
        opens = successful_opens(Path(B) / "run/p0" / b / f"strace.{b}.1L")
        own = os.path.realpath(Path(B) / f"prefix-{b}" / "lib")
        for lib in ("libMAT.so", "libMAT-MINERvA.so"):
            hits = [real(p) for p in opens if os.path.basename(p) == lib or
                    os.path.basename(p).startswith(lib + ".")]
            if not hits:
                ok = False
                ev.append(f"{b}: {lib} never opened")
            for h in hits:
                if not under(h, own):
                    ok = False
                    ev.append(f"{b}: {lib} opened from {h}")
        prod = [real(p) for p in opens
                if under(real(p), os.path.realpath(Path(prod_opt) / "lib")) and ".so" in os.path.basename(p)]
        if prod:
            ok = False
            ev.append(f"{b}: production libraries opened: {sorted(set(prod))}")
    return ok, ev or ["both builds open libMAT.so and libMAT-MINERvA.so from their own prefix only"]


def _branch(tree, name):
    return tree[name].array(library="np")


def c0bc(path, patched):
    """C0b (patched=True) or C0c (patched=False) on one dump."""
    ev, ok = [], True
    with uproot.open(path) as f:
        for t in TREES:
            if t not in f:
                ok = False
                ev.append(f"{t} missing")
                continue
            have = set(f[t].keys())
            missing = [b for b in ["w_truth"] + TARGETS if b not in have]
            if missing:
                ok = False
                ev.append(f"{t}: missing {missing}")
                continue
            cv = dumpcmp._bits(_branch(f[t], "w_truth"))
            for name in TARGETS:
                x = _branch(f[t], name)
                n = int((dumpcmp._bits(x) != cv).sum())
                if patched:
                    if n == 0:
                        ok = False
                        ev.append(f"{t}: {name} never differs from w_truth")
                    if not (np.all(np.isfinite(x)) and np.all(x > 0)):
                        ok = False
                        ev.append(f"{t}: {name} has non-finite or non-positive values")
                elif n:
                    ok = False
                    ev.append(f"{t}: {name} differs from w_truth in {n} entries")
                ev.append(f"{t}: {name} differs in {n}/{len(x)}")
    return ok, ev


def c0e(B, deploy, prod_opt, conda):
    allowed_files = set()
    for kind in ("MC", "Data"):
        for p in (Path(deploy) / "2d-unfolding/playlist_manifests" / f"1L_{kind}.txt").read_text().split():
            allowed_files.add(os.path.realpath(p))
    families = [os.path.realpath(Path(prod_opt) / "lib/data"), os.path.realpath(Path(prod_opt) / "etc/MParamFiles/data"),
                os.path.realpath(Path(prod_opt) / "etc/MATFluxAndReweightFiles"),
                os.path.realpath(conda)] + sorted({os.path.realpath(r) for r in SYSTEM} | set(SYSTEM))
    rB = os.path.realpath(B)
    bad, outside = [], set()
    for b in ("pin", "pat"):
        opens = opens_detail(Path(B) / "run/p0" / b / f"strace.{b}.1L")
        main = opens[0][0] if opens else None   # strace starts the binary, so its first successful open is the binary's
        for pid, p, flags in opens:
            r = real(p)
            if under(r, rB):
                continue
            outside.add(r)
            if r in allowed_files or any(under(r, fam) for fam in families):
                continue
            if env_plumbing(r, pid != main, "O_DIRECTORY" in flags):
                continue
            bad.append(r)
    ev = [f"{len(outside)} distinct files opened outside B"] + [f"NOT ALLOWED {x}" for x in sorted(set(bad))]
    return not bad, ev, sorted(outside)


def build_checks(B):
    log = Path(B) / "run/p0/build.log"
    lines = log.read_text().splitlines() if log.exists() else []
    got = {ln.split()[1]: ln.split()[2] for ln in lines if ln.startswith("CHECK ") and len(ln.split()) == 3}
    bad = [c for c in CHECKS if got.get(c) != "PASS"]
    return not bad, [f"CHECK {c} {got.get(c, 'MISSING')}" for c in CHECKS]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--B", required=True)
    ap.add_argument("--deploy", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--ref-sha", required=True)
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    prod_opt, conda = PROD_OPT, CONDA
    if os.environ.get("GEANTTW_SMOKE_B") and os.environ["GEANTTW_SMOKE_B"] == a.B:
        prod_opt = os.environ.get("GEANTTW_TEST_PROD_OPT", prod_opt)
        conda = os.environ.get("GEANTTW_TEST_CONDA", conda)
    dump = {b: Path(a.B) / "run/p0" / b / f"runEventLoopOmniFold_GEANTTW_{b}_1L.root" for b in ("pin", "pat")}
    res = {}
    res["build.log"] = build_checks(a.B)
    res["C0a"] = c0a(a.B, prod_opt)
    res["C0b"] = c0bc(dump["pat"], True)
    res["C0c"] = c0bc(dump["pin"], False)
    rep_d = dumpcmp.compare(dump["pin"], dump["pat"], exempt=TARGET_RE)
    judged_out = {(t, n) for t, i in rep_d["trees"].items() for n, v in i["branches"].items() if not v["judged"]}
    want = {(t, n) for t in TREES for n in TARGETS}
    ok_d = rep_d["verdict"] == "PASS" and judged_out == want
    res["C0d"] = (ok_d, rep_d["problems"][:20] + ([] if judged_out == want else
                  [f"exempt set {sorted(judged_out)} is not the six targets in {TREES}"]))
    ok_e, ev_e, outside = c0e(a.B, a.deploy, prod_opt, conda)
    res["C0e"] = (ok_e, ev_e)
    h = hashlib.sha256(Path(a.ref).read_bytes()).hexdigest()
    rep_f = dumpcmp.compare(a.ref, dump["pin"], allow_extra=UNIVERSE_RE)
    res["C0f"] = (h == a.ref_sha and rep_f["verdict"] == "PASS",
                  [f"reference sha256 {h} {'==' if h == a.ref_sha else '!='} {a.ref_sha}"] + rep_f["problems"][:20])
    allok = True
    for k, (ok, ev) in res.items():
        allok &= ok
        print(f"{k} {'PASS' if ok else 'FAIL'} {ev[0] if ev else ''}")
        for e in ev[1:]:
            print(f"    {e}")
    if a.json:
        Path(a.json).write_text(json.dumps({"controls": {k: {"pass": ok, "evidence": ev} for k, (ok, ev) in res.items()},
                                            "opened_outside_B": outside, "verdict": "PASS" if allok else "FAIL"},
                                           indent=1))
    print(f"P0 {'PASS' if allok else 'FAIL'}")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
