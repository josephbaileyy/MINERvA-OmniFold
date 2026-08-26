"""Fail when a receipt names a deliverable artifact that git is not carrying.

WHY THIS EXISTS. `.gitignore:29` excludes `*.npz` (and `:30` `*.h5`, `:2` `*.root`). A lane
produces a binary deliverable, commits its receipt, and git silently drops the object -- leaving a
tracked receipt that describes a file nobody else can obtain. **Three occurrences in two days,
every one caught by a person checking and never by anything failing.** That is the signature of a
missing check rather than of careless lanes.

WHY NOT JUST UN-IGNORE `*.npz`. That trades this trap for the opposite one: a multi-GB array
committed by accident, which is far more expensive and far harder to undo. Per `CLAUDE.md` --
*"prefer the executable form of any rule you are tempted to write down"* -- the fix is a check,
not a `.gitignore` edit and not a convention document. `.gitignore` is deliberately untouched.

THE RULE, and it is narrow on purpose:

    A receipt under docs/orchestration/state/ names a path under docs/orchestration/state/
    that git does not track  ->  FAIL.

Scoped to the DELIVERABLE AREA because that is where the trap lives. Measured on this tree: of
351 artifact-like paths named across those receipts, **349 point at cluster or scratch products
that are not supposed to be in git**, and 2 point into the deliverable area. Widening the rule to
all named paths would fire on all 349 and be turned off within a day; narrowing it to the
deliverable area gives zero false positives here and still catches every historical case.

Absolute paths under the cluster checkout are rewritten to repo-relative first, so a receipt that
records `/pscratch/.../MINERvA-OmniFold/docs/orchestration/state/x.npz` is caught too.

Exit 0 clean, 1 on findings, 2 if it could not run.
"""
import argparse
import json
import os
import re
import subprocess
import sys

#: Absolute-path prefixes that name A CHECKOUT OF THIS REPO and must be stripped before the
#: deliverable-area test. This used to be a one-element tuple hardcoding the checkout that was
#: canonical until 2026-08-25. That went FAIL-OPEN the moment the canonical checkout moved
#: (DECISION-20260825-joseph-gate2-fail-and-four-rulings.md ruling 4, forward-only redesignation):
#: a receipt written from the new checkout named an absolute path that matched no prefix, was left
#: absolute, failed `rel.startswith(AREA)`, and was SILENTLY NOT CHECKED. A hardcoded list of
#: checkout locations rots every time a checkout moves, and it rots in the direction that stops
#: checking, so the list is now derived rather than written down.
HISTORICAL_REPO_PREFIXES = (
    "/pscratch/sd/j/josephrb/MINERvA-OmniFold/",   # canonical until 2026-08-25; still named by
                                                   # receipts already committed, so it must keep
                                                   # normalising or this repair is a regression
)
AREA = "docs/orchestration/state/"
#: Last-resort marker. Any ABSOLUTE path containing this normalises on it, so a checkout nobody
#: listed -- a worktree, a fresh clone, the next redesignation -- is still checked. Failing this
#: way is fail-CLOSED: the worst case is checking a path we did not have to, which is visible,
#: rather than skipping one we did, which is not.
_AREA_MARKER = "/" + AREA
EXT = (".npz", ".npy", ".h5", ".hdf5", ".root", ".pkl", ".parquet")
PATHLIKE = re.compile(r"[\w./\-]+(?:" + "|".join(re.escape(e) for e in EXT) + r")\b")


def _run(args, cwd=None):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def repo_root():
    out = _run(["git", "rev-parse", "--show-toplevel"]).strip()
    return out or os.getcwd()


_PREFIX_CACHE = {}


def repo_prefixes(root=None):
    """Every absolute prefix that means "a checkout of this repo", longest first.

    Derived from the CURRENT checkout plus the historical ones, rather than written down, because
    the written-down version is what went fail-open. Longest-first so a nested path cannot be
    stripped by a shorter prefix that happens to also match.
    """
    root = root or repo_root()
    if root not in _PREFIX_CACHE:
        prefixes = {os.path.join(root, "")}
        prefixes.update(HISTORICAL_REPO_PREFIXES)
        _PREFIX_CACHE[root] = tuple(sorted(prefixes, key=len, reverse=True))
    return _PREFIX_CACHE[root]


def normalise(p, root=None):
    """Absolute paths inside ANY checkout of this repo -> repo-relative. Others unchanged."""
    for pref in repo_prefixes(root):
        if p.startswith(pref):
            return p[len(pref):]
    if p.startswith("/"):
        i = p.rfind(_AREA_MARKER)
        if i != -1:
            return p[i + 1:]
    return p


def named_artifacts(text, root=None):
    """Deliverable-area artifact paths named anywhere in a receipt's text."""
    out = set()
    for m in PATHLIKE.findall(text):
        rel = normalise(m, root)
        if not rel.startswith("/") and rel.startswith(AREA):
            out.add(rel)
    return out


def scan(rev=None, root=None):
    """Return (findings, n_receipts, n_paths). `rev` evaluates a historical commit instead
    of the working tree -- needed to demonstrate the check against the cases that motivated it."""
    root = root or repo_root()
    if rev:
        tracked = set(_run(["git", "ls-tree", "-r", rev, "--name-only"], root).split("\n"))
        receipts = [f for f in tracked if f.startswith(AREA) and f.endswith(".json")]

        def read(f):
            return _run(["git", "show", f"{rev}:{f}"], root)
    else:
        tracked = set(_run(["git", "ls-files"], root).split("\n"))
        receipts = sorted(f for f in tracked if f.startswith(AREA) and f.endswith(".json"))

        def read(f):
            try:
                with open(os.path.join(root, f), encoding="utf-8", errors="replace") as fh:
                    return fh.read()
            except OSError:
                return ""

    findings, n_paths = [], 0
    for f in receipts:
        for rel in sorted(named_artifacts(read(f), root)):
            n_paths += 1
            if rel not in tracked:
                findings.append({"receipt": f, "artifact": rel,
                                 "why": "named by a tracked receipt, absent from git"})
    return findings, len(receipts), n_paths


def historical_cases(root=None):
    """Would this have caught the occurrences that motivated it? Measured, not assumed.

    A check that cannot be shown to fire on the cases it was built for is not evidence, so this
    is reported as its own result rather than asserted in a docstring.
    """
    root = root or repo_root()
    cases = [
        ("87046fe^", "lane B's C_stat: receipt committed, .npz gitignored",
         "GATE5_CSTAT_N50.npz"),
        ("849b70f^", "lane D's cross-check, the commit before the artifact landed",
         "LANED_CSTAT_CROSSCHECK.npz"),
    ]
    out = []
    for rev, desc, needle in cases:
        ok = _run(["git", "rev-parse", "--verify", "--quiet", rev], root).strip()
        if not ok:
            out.append({"rev": rev, "desc": desc, "fires": None, "why": "revision not resolvable"})
            continue
        f, _, _ = scan(rev=rev, root=root)
        hit = [x for x in f if needle in x["artifact"]]
        out.append({"rev": rev, "desc": desc, "fires": bool(hit),
                    "findings_at_rev": len(f), "matching": hit[:3]})
    return out


def self_test(root=None):
    """Positive control: a synthetic receipt naming an untracked deliverable MUST be caught.
    A detector that has never detected anything is not evidence."""
    fake = "docs/orchestration/state/__selftest_nonexistent__/OBJECT.npz"
    caught = bool(named_artifacts(json.dumps({"artifact": {"path": fake}})))
    tracked = set(_run(["git", "ls-files"], root or repo_root()).split("\n"))
    return {"synthetic_path_extracted": caught, "and_is_untracked": fake not in tracked,
            "control_fires": bool(caught and fake not in tracked)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rev", help="evaluate a git revision instead of the working tree")
    ap.add_argument("--historical", action="store_true",
                    help="report whether this fires on the cases that motivated it")
    ap.add_argument("--json", action="store_true", help="emit a JSON receipt")
    a = ap.parse_args(argv)

    root = repo_root()
    ctl = self_test(root)
    findings, n_receipts, n_paths = scan(rev=a.rev, root=root)
    hist = historical_cases(root) if a.historical else None

    if a.json:
        print(json.dumps({"findings": findings, "n_receipts": n_receipts,
                          "n_deliverable_paths": n_paths, "control": ctl,
                          "historical": hist, "rev": a.rev or "working tree"},
                         indent=1, sort_keys=True))
    else:
        where = a.rev or "working tree"
        print(f"RECEIPT-ARTIFACTS :: {n_receipts} receipts scanned at {where}, "
              f"{n_paths} deliverable-area artifact path(s), {len(findings)} missing")
        if not ctl["control_fires"]:
            print("  *** the positive control did not fire; this check is not evidence ***")
        for x in findings:
            print(f"  FAIL {x['artifact']}\n       named by {x['receipt']} but not tracked. "
                  f"If it is a deliverable, `git add -f` it; .gitignore:29 excludes *.npz.")
        if hist:
            print("\n  -- would it have caught the cases that motivated it? --")
            for h in hist:
                v = {True: "FIRES", False: "does NOT fire", None: "unresolvable"}[h["fires"]]
                print(f"    {h['rev']:12s} {v:14s} {h['desc']}")
    if not ctl["control_fires"]:
        return 2
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
