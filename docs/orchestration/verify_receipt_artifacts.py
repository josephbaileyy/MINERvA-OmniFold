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

BARE FILENAMES AND LOG EVIDENCE (KNOWN_ISSUES 48, 2026-09-23). `.out`, `.err` and `.log` count as
artifact extensions too. A citation with no directory (for example "centring_n50.out") is RESOLVED
rather than dropped. It is tried in this order:
  1. the receipt's own directory, and its companion directory `<receipt stem>/`;
  2. the receipt's DECLARED run directories (string fields such as `run_root`, `member_root`,
     `family_root`, `out_dir`, `*_dir`, `dir`);
  3. the same basename cited WITH a directory elsewhere in the same receipt.
Each citation ends in exactly one state:
  TRACKED       resolved to a tracked file (green);
  MISSING       a candidate directory in the deliverable area is tracked (it holds tracked files)
                but does not carry the file. This is the `.gitignore` trap, exit 1;
  OFF-AREA      resolved to a declared run directory outside the deliverable area (a cluster
                product, out of scope for the reason above). Counted, not checked;
  BY-PATH       the same file is also cited with a directory, and that path is what gets checked;
  UNRESOLVED    none of the above. This is a separate non-green state and is never counted as green.

Exit 0 clean, 1 on MISSING, 2 if it could not run, 3 if the UNRESOLVED set differs from the pinned
inventory (`UNRESOLVED_COUNT`/`UNRESOLVED_SHA256`), or, with `--strict`, if ANY citation is
UNRESOLVED. The pinned inventory exists so that citations committed before 2026-09-23 do not block
every commit. They are still printed as UNRESOLVED on every run, and a NEW one fails.
"""
import argparse
import hashlib
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
EXT = (".npz", ".npy", ".h5", ".hdf5", ".root", ".pkl", ".parquet", ".out", ".err", ".log")
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


#: String fields whose value is a RUN DIRECTORY that a bare filename may live in. Listed explicitly:
#: code roots and data roots are checkouts, not the directory a log was written to.
DECLARED_DIR_KEY = re.compile(
    r"(?i)^(?:dir|[a-z0-9_]*_dir|run_root|member_root|member_output_root|family_root|"
    r"output_root|logs?_root|evidence_root)$")

#: The UNRESOLVED citations already committed when bare-filename resolution landed (2026-09-23),
#: stored as a count and a sha256 over the sorted "receipt<TAB>citation<NL>" rows. The default mode
#: fails (exit 3) when the set CHANGES, whether a citation is added or removed. Re-derive the values
#: with `--list-unresolved`, and change them only in the same commit as the receipt change that
#: caused the difference.
#: Measured 2026-09-23 on the tree based on f8d6f276: 169 receipts, bare citations TRACKED 9 /
#: MISSING 0 / OFF-AREA 29 / BY-PATH 7 / UNRESOLVED 64.
#: 64 -> 66 on 2026-09-23 with the Gate-4 launch-code re-issue (KNOWN_ISSUES rows 28/38/33, Joseph's
#: 2026-09-23 ruling). The successor p3f-pet-gate4-launch-code-gate-20260923.json carries forward
#: 20260813's narrative fields verbatim, so it repeats 20260813's two bare citations. ADDED exactly:
#:   state/p3f-pet-gate4-launch-code-gate-20260923.json  pet_fullevent_floor_weights.npz
#:   state/p3f-pet-gate4-launch-code-gate-20260923.json  pet_fullevent_nominal_weights.npz
#: Nothing was removed: the retired 20260813 keeps its citations.
UNRESOLVED_COUNT = 66
UNRESOLVED_SHA256 = "49916d2832740f06163191d8dc960454ab85ae5bbb3aa9d5623b62b7d88e3020"


def bare_citations(text):
    """Artifact-extension tokens with NO directory component, named anywhere in a receipt."""
    return {m for m in PATHLIKE.findall(text) if "/" not in m}


def declared_dirs(text):
    """Values of DECLARED_DIR_KEY string fields anywhere in the receipt's JSON."""
    try:
        doc = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return []
    out, stack = [], [doc]
    while stack:
        o = stack.pop()
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and v and DECLARED_DIR_KEY.match(str(k)):
                    out.append(v)
                elif isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(o, list):
            stack.extend(o)
    return sorted(set(out))


def classify_bare(receipt, name, text, tracked, tracked_dirs, root=None):
    """Resolve ONE bare citation. Returns (state, resolved_to)."""
    here = os.path.dirname(receipt)
    stem = receipt[:-len(".json")] if receipt.endswith(".json") else receipt
    # The flat state/ directory always holds tracked files, so it can only resolve a citation;
    # it is never evidence that the file is MISSING. A receipt's own subdirectory is.
    area_candidates = [(here, here.rstrip("/") + "/" != AREA), (stem, True)]
    offarea = []
    for d in declared_dirs(text):
        rel = normalise(d.rstrip("/"), root)
        if rel.startswith("/"):
            offarea.append(d)
        elif (rel + "/").startswith(AREA):
            area_candidates.append((rel, True))
        else:
            offarea.append(d)
    for d, _ in area_candidates:
        cand = os.path.join(d, name)
        if cand in tracked:
            return "TRACKED", cand
    for d, specific in area_candidates:
        if specific and d in tracked_dirs:
            return "MISSING", os.path.join(d, name)
    if offarea:
        return "OFF-AREA", os.path.join(offarea[0], name)
    for m in PATHLIKE.findall(text):
        if "/" in m and os.path.basename(m) == name:
            return "BY-PATH", m
    return "UNRESOLVED", None


def unresolved_digest(rows):
    payload = "".join(f"{r}\t{n}\n" for r, n in sorted(rows)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def scan_full(rev=None, root=None):
    """Every citation in every state/*.json receipt, classified. `rev` evaluates a historical
    commit instead of the working tree. That is needed to show the check against the cases that
    motivated it."""
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

    tracked_dirs = {os.path.dirname(t) for t in tracked if t}
    findings, unresolved, states, n_paths = [], [], {}, 0
    for f in sorted(receipts):
        text = read(f)
        for rel in sorted(named_artifacts(text, root)):
            n_paths += 1
            if rel not in tracked:
                findings.append({"receipt": f, "artifact": rel,
                                 "why": "named by a tracked receipt, absent from git"})
        for name in sorted(bare_citations(text)):
            state, where = classify_bare(f, name, text, tracked, tracked_dirs, root)
            states[state] = states.get(state, 0) + 1
            if state == "MISSING":
                findings.append({"receipt": f, "artifact": where,
                                 "why": f"bare citation {name!r}; the receipt's evidence directory "
                                        f"is tracked but does not carry it"})
            elif state == "UNRESOLVED":
                unresolved.append((f, name))
    return {"findings": findings, "n_receipts": len(receipts), "n_paths": n_paths,
            "bare_states": states, "unresolved": unresolved,
            "unresolved_sha256": unresolved_digest(unresolved)}


def scan(rev=None, root=None):
    """Return (findings, n_receipts, n_paths); see `scan_full` for the classified detail."""
    r = scan_full(rev=rev, root=root)
    return r["findings"], r["n_receipts"], r["n_paths"]


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
        ("e7aea2c9^", "nine .out evidence files cited by BARE filename, dropped by .gitignore",
         "centring_n50.out"),
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
    # Bare-citation controls on a synthetic tree: one green case, plus MISSING and UNRESOLVED.
    rcpt = AREA + "__selftest__.json"
    t_tracked = {AREA + "__selftest__/probe.py", AREA + "__selftest__/kept.out"}
    t_dirs = {os.path.dirname(x) for x in t_tracked}
    body = json.dumps({"evidence": {"kept.out": {}, "dropped.out": {}}})
    bare = {n: classify_bare(rcpt, n, body, t_tracked, t_dirs)[0] for n in ("kept.out", "dropped.out")}
    lost = classify_bare(AREA + "__elsewhere__.json", "lost.err",
                         json.dumps({"x": "lost.err"}), t_tracked, t_dirs)[0]
    bare_ok = bare == {"kept.out": "TRACKED", "dropped.out": "MISSING"} and lost == "UNRESOLVED"
    return {"synthetic_path_extracted": caught, "and_is_untracked": fake not in tracked,
            "bare_states": dict(bare, **{"lost.err": lost}),
            "control_fires": bool(caught and fake not in tracked and bare_ok)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rev", help="evaluate a git revision instead of the working tree")
    ap.add_argument("--historical", action="store_true",
                    help="report whether this fires on the cases that motivated it")
    ap.add_argument("--json", action="store_true", help="emit a JSON receipt")
    ap.add_argument("--strict", action="store_true",
                    help="exit 3 on ANY unresolved citation, not only on a change to the pinned set")
    ap.add_argument("--list-unresolved", action="store_true",
                    help="print every UNRESOLVED citation and the set's count/sha256")
    a = ap.parse_args(argv)

    root = repo_root()
    ctl = self_test(root)
    r = scan_full(rev=a.rev, root=root)
    findings, unresolved = r["findings"], r["unresolved"]
    hist = historical_cases(root) if a.historical else None
    pinned = (len(unresolved) == UNRESOLVED_COUNT and r["unresolved_sha256"] == UNRESOLVED_SHA256)
    # A historical --rev is compared with nothing: the pin describes the working tree.
    unresolved_fails = bool(unresolved) and (a.strict or (not pinned and not a.rev))

    if a.json:
        print(json.dumps({"findings": findings, "n_receipts": r["n_receipts"],
                          "n_deliverable_paths": r["n_paths"], "bare_states": r["bare_states"],
                          "unresolved": [{"receipt": f, "citation": n} for f, n in unresolved],
                          "unresolved_sha256": r["unresolved_sha256"],
                          "unresolved_matches_pinned_inventory": pinned,
                          "control": ctl, "historical": hist, "rev": a.rev or "working tree"},
                         indent=1, sort_keys=True))
    else:
        where = a.rev or "working tree"
        st = r["bare_states"]
        print(f"RECEIPT-ARTIFACTS :: {r['n_receipts']} receipts scanned at {where}, "
              f"{r['n_paths']} deliverable-area artifact path(s), {len(findings)} missing")
        print("  bare-filename citations: " + ", ".join(
            f"{k} {st.get(k, 0)}" for k in ("TRACKED", "MISSING", "OFF-AREA", "BY-PATH", "UNRESOLVED")))
        if unresolved:
            tag = ("pinned inventory, UNCHANGED" if pinned else
                   f"DIFFERS from the pinned inventory ({UNRESOLVED_COUNT} / "
                   f"{(UNRESOLVED_SHA256 or 'none')[:12]})")
            print(f"  NOT GREEN: {len(unresolved)} citation(s) UNRESOLVED -- NOT CHECKED ({tag}); "
                  f"sha256 {r['unresolved_sha256'][:12]}. `--list-unresolved` names them.")
        if a.list_unresolved or (unresolved and not pinned and not a.rev):
            for f, n in unresolved:
                print(f"    UNRESOLVED {n}  <- {f}")
            print(f"  UNRESOLVED_COUNT = {len(unresolved)}\n"
                  f"  UNRESOLVED_SHA256 = \"{r['unresolved_sha256']}\"")
        if not ctl["control_fires"]:
            print("  *** the positive control did not fire; this check is not evidence ***")
        for x in findings:
            print(f"  FAIL {x['artifact']}\n       named by {x['receipt']} but not tracked "
                  f"({x['why']}). If it is a deliverable, `git add -f` it; .gitignore excludes "
                  f"*.npz/*.out/*.err/*.log.")
        if hist:
            print("\n  -- would it have caught the cases that motivated it? --")
            for h in hist:
                v = {True: "FIRES", False: "does NOT fire", None: "unresolvable"}[h["fires"]]
                print(f"    {h['rev']:12s} {v:14s} {h['desc']}")
    if not ctl["control_fires"]:
        return 2
    if findings:
        return 1
    return 3 if unresolved_fails else 0


if __name__ == "__main__":
    sys.exit(main())
