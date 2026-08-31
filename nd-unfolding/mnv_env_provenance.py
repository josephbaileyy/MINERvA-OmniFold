#!/usr/bin/env python3
"""Record the submission environment, and compare a later environment against that record.

WHY THIS EXISTS -- `OI-179` defect 3, and it is load-bearing for TWO failure classes, not one.

On 2026-08-30 the seven k=0 arms died in 8-15 s because the submission never exported
`MNV_ENV_SYSTEM_PREFIXES`, which `lib_mnv_env_pathcheck.sh:37-41` specifies the submitter must
declare. That omission was only PROVABLE because
`RECORD-20260830-k0-quarantine-and-seven-arm-submission.md` section 5 happened to quote the eight
`export` lines it did use. Nothing emitted the environment; the record's rigor was aimed entirely at
git state -- porcelain and a status digest re-read at five timestamps with the recipe named -- and
never at the surface that actually stopped the run.

AND THE SECOND CLASS IS WHY A PROBE RATHER THAN A CONVENTION. `OI-179` defect 1: the allowlist
documented at `PACKET-20260823:122` was correct when written and went stale because `$HOME/bin` was
CREATED on 2026-08-26, three days later. `/etc/profile:171` adds it to `PATH` conditionally on the
directory existing, so a `mkdir` silently invalidated a documented, tested control **with no edit to
any file this campaign tracks, pins or reviews**. No source-line detector can ever reach that -- there
is no source. A recorded-and-compared environment is the only instrument that can observe it.

THE ONE TRAP THIS FILE MUST NOT FALL INTO, stated because the campaign just paid for it.
`OI-179` defect 2 was a fixture that derived its expected allowlist from `os.environ` and then handed
it to the guard that checks `os.environ` -- an expectation that cannot disagree with its subject.
**So `check` compares against a RECORDED BASELINE FILE and never against the ambient environment.**
If the baseline is missing, `check` REFUSES (exit 2) rather than falling back to "compare the
environment with itself", which would always pass and would read as coverage.

WHAT THIS DELIBERATELY DOES NOT DO. It does not decide whether a difference is acceptable; it reports
what moved and exits nonzero. It emits no verdict about any gate. It is not a launcher and it edits
nothing: it is a separate tool invoked at submission time, chosen over inlining the emitter into the
eight `sbatch_*` launchers precisely so that no pinned launcher changes and neither the `F-14` /
7.0.7 coupling nor `OI-123` pin supersession applies.

Python 3.7+ (the floor the sibling preflight tools already assert).

EXIT: 0 clean / 2 could not look / 3 measured drift.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time

SEARCH_VARS = ("PATH", "PYTHONPATH", "LD_LIBRARY_PATH")

EXIT_OK, EXIT_CANNOT_LOOK, EXIT_DRIFT = 0, 2, 3


def _mnv_vars(env):
    """Every `MNV_*` name, sorted. Sorted so the digest does not depend on dict ordering."""
    return {k: env[k] for k in sorted(env) if k.startswith("MNV_")}


def snapshot(env=None):
    """The environment facts that decide whether a launcher can start.

    `HOME` is included because `--export=ALL,HOME=...` is how the launchers pass it and because the
    home directory is what `/etc/profile` conditionally adds to `PATH`.
    """
    env = os.environ if env is None else env
    snap = {
        "recorded_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "host": platform.node(),
        "home": env.get("HOME", "<unset>"),
        "mnv": _mnv_vars(env),
        "search_paths": {v: [e for e in env.get(v, "").split(":") if e] for v in SEARCH_VARS},
    }
    snap["digest"] = _digest(snap)
    return snap


def _digest(snap):
    """A digest over the COMPARED fields only.

    `recorded_utc` and `host` are excluded on purpose: two identical environments recorded a minute
    apart on different login nodes must produce the same digest, or the digest measures the clock
    instead of the environment.
    """
    payload = {"home": snap["home"], "mnv": snap["mnv"], "search_paths": snap["search_paths"]}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def emit(path, env=None):
    snap = snapshot(env)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(snap, fh, indent=2, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    return snap


def _diff(base, now):
    """Ordered, human-readable differences. Order matters for PATH, so lists compare as lists."""
    out = []
    if base.get("home") != now.get("home"):
        out.append("HOME: %s -> %s" % (base.get("home"), now.get("home")))
    bm, nm = base.get("mnv", {}), now.get("mnv", {})
    for k in sorted(set(bm) | set(nm)):
        if bm.get(k) != nm.get(k):
            out.append("%s: %s -> %s" % (k, bm.get(k, "<unset>"), nm.get(k, "<unset>")))
    bs, ns = base.get("search_paths", {}), now.get("search_paths", {})
    for v in SEARCH_VARS:
        b, n = bs.get(v, []), ns.get(v, [])
        if b == n:
            continue
        gained = [e for e in n if e not in b]
        lost = [e for e in b if e not in n]
        if gained:
            out.append("%s GAINED %d entr(ies): %s" % (v, len(gained), ", ".join(gained)))
        if lost:
            out.append("%s LOST %d entr(ies): %s" % (v, len(lost), ", ".join(lost)))
        if not gained and not lost:
            out.append("%s REORDERED (same members, different order, which changes what shadows what)"
                       % v)
    return out


def check(path, env=None):
    """Compare the live environment against a RECORDED baseline. Never against itself."""
    if not os.path.isfile(path):
        print("[env-provenance] COULD NOT LOOK: no baseline at %s." % path, file=sys.stderr)
        print("[env-provenance]   REFUSING rather than comparing the environment with itself: an",
              file=sys.stderr)
        print("[env-provenance]   expectation derived from its own subject cannot disagree with it",
              file=sys.stderr)
        print("[env-provenance]   (OI-179 defect 2).", file=sys.stderr)
        return EXIT_CANNOT_LOOK
    try:
        with open(path, encoding="utf-8") as fh:
            base = json.load(fh)
    except (OSError, ValueError) as exc:
        print("[env-provenance] COULD NOT LOOK: baseline unreadable: %s" % exc, file=sys.stderr)
        return EXIT_CANNOT_LOOK

    now = snapshot(env)
    diffs = _diff(base, now)
    if not diffs:
        print("[env-provenance] OK: environment matches %s (digest %s)" % (path, now["digest"][:16]))
        return EXIT_OK
    print("[env-provenance] DRIFT: %d difference(s) against %s" % (len(diffs), path), file=sys.stderr)
    print("[env-provenance]   baseline recorded %s on %s"
          % (base.get("recorded_utc", "<unknown>"), base.get("host", "<unknown>")), file=sys.stderr)
    for d in diffs:
        print("[env-provenance]   %s" % d, file=sys.stderr)
    print("[env-provenance]   A GAINED search-path entry is how OI-179 defect 1 happened: a mkdir",
          file=sys.stderr)
    print("[env-provenance]   put $HOME/bin on PATH with no edit to any tracked file.", file=sys.stderr)
    return EXIT_DRIFT


def self_test():
    """Arms in BOTH directions, and the refusal arm, because a one-directional check waves the other.

    Run in-process with synthetic environments rather than by mutating `os.environ`, so the test
    cannot be satisfied by the ambient environment it is meant to be independent of.
    """
    import tempfile
    ok = True

    def arm(label, got, want):
        nonlocal ok
        good = got == want
        ok = ok and good
        print("  %-58s %s" % (label, "OK" if good else "*** FAIL (got %r want %r) ***" % (got, want)))

    base_env = {"HOME": "/home/u", "MNV_ENV_ROOT": "/env", "PATH": "/usr/bin:/bin"}
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "prov.json")
        emit(p, base_env)

        arm("identical environment is CLEAN", check(p, dict(base_env)), EXIT_OK)

        gained = dict(base_env, PATH="/home/u/bin:/usr/bin:/bin")
        arm("a GAINED PATH entry is DRIFT (the OI-179 defect-1 shape)",
            check(p, gained), EXIT_DRIFT)

        lost = dict(base_env, PATH="/usr/bin")
        arm("a LOST PATH entry is DRIFT", check(p, lost), EXIT_DRIFT)

        reordered = dict(base_env, PATH="/bin:/usr/bin")
        arm("a REORDERED PATH is DRIFT (order decides what shadows what)",
            check(p, reordered), EXIT_DRIFT)

        dropped = {k: v for k, v in base_env.items() if k != "MNV_ENV_ROOT"}
        arm("a DROPPED MNV_* variable is DRIFT", check(p, dropped), EXIT_DRIFT)

        added = dict(base_env, MNV_ENV_SYSTEM_PREFIXES="/usr /bin")
        arm("an ADDED MNV_* variable is DRIFT (the omission this file exists for)",
            check(p, added), EXIT_DRIFT)

        arm("a MISSING baseline REFUSES rather than passing",
            check(os.path.join(d, "absent.json"), dict(base_env)), EXIT_CANNOT_LOOK)

        s1 = snapshot(base_env)
        time.sleep(1.1)
        s2 = snapshot(base_env)
        arm("the digest ignores clock and host", s1["digest"] == s2["digest"], True)
        # AND THE DIGEST MUST DISCRIMINATE, or the arm above is satisfied by a digest over nothing.
        # Found by sabotage: replacing the digest payload with `{}` left every other arm GREEN,
        # because they all compare via `_diff` and none of them touched the digest. A value that is
        # computed, printed into records, and asserted only for STABILITY is a datum nobody has shown
        # can disagree -- so both directions are pinned here.
        arm("the digest CHANGES when the environment changes",
            snapshot(base_env)["digest"] != snapshot(gained)["digest"], True)
        arm("the digest is EQUAL for two equal environments",
            snapshot(base_env)["digest"] == snapshot(dict(base_env))["digest"], True)
        # THIS ARM WAS WRITTEN WRONG FIRST TIME AND THE ERROR IS KEPT VISIBLE: it read
        # `s1[...] != s2[...] or True`, which is ALWAYS True -- an unfalsifiable assertion inside the
        # tool built to detect unfalsifiable assertions. It is a real comparison now. Without it the
        # digest arm above proves nothing, because two snapshots taken in the same second would have
        # equal digests trivially.
        arm("the two snapshots were taken at genuinely different times",
            s1["recorded_utc"] != s2["recorded_utc"], True)

    print("self-test PASSED" if ok else "self-test FAILED")
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit", metavar="PATH", help="record the current environment to PATH")
    g.add_argument("--check", metavar="PATH", help="compare the current environment against PATH")
    g.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return EXIT_OK if self_test() else EXIT_DRIFT
    if a.emit:
        snap = emit(a.emit)
        print("[env-provenance] wrote %s: %d MNV_* var(s), %s search-path entr(ies), digest %s"
              % (a.emit, len(snap["mnv"]),
                 sum(len(v) for v in snap["search_paths"].values()), snap["digest"][:16]))
        return EXIT_OK
    return check(a.check)


if __name__ == "__main__":
    sys.exit(main())
