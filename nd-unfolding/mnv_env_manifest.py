#!/usr/bin/env python3
"""Generate and verify the digest-bound manifest for the k=0 activation closure.

WHAT IT BINDS, and why the closure and not the activator. Gate-1 round 4 established that
`setup_salloc_env.sh` is 24 committed lines that source files ABSENT from any A-2-satisfying tree.
Binding the activator alone moves the trust boundary one hop; this binds the COMPLETE TRANSITIVE
CLOSURE -- hop 0 the activator, hop 1 the two setup scripts it sources, hop 2 the three MAT scripts
below `MINERvA101/opt/bin/setup.sh`, and the conda `activate.d/*.sh` that activation executes.
Measured, not assumed: hop 3 is empty (`setup_MAT.sh`, `setup_MAT-MINERvA.sh`,
`setup_UnfoldUtils.sh` each contain zero `source` lines).

WHY THE RUNTIME FORMAT IS TSV AND NOT THIS FILE'S JSON. The runtime verifier is
`mnv_env_preflight.sh`, pure bash, because it runs BEFORE the activator and the activator is what
provides a modern interpreter -- the pre-conda `/usr/bin/python3` on saul is 3.6.15 and this file
would not parse there. Bash has no JSON parser, and one written for the purpose would be a second
thing to trust. So this tool emits a line-oriented TSV the verifier reads with `read`, plus a JSON
identity record for the Gate-1 evidence.

THE TWO ARTIFACTS ARE BOUND TO EACH OTHER: the JSON carries the sha256 OF THE TSV, so an edited TSV
is detectable even though the thing that reads it at run time cannot parse JSON.

EXIT: 0 ok, 2 could not look, 3 measured violation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

OK_EXIT, CANNOT_CHECK_EXIT, VIOLATION_EXIT = 0, 2, 3
SCHEMA = "mnv_env_manifest/1"

#: (role, base, relative path). Derived by MEASUREMENT on 2026-08-23 and re-derived by
#: `--discover`, never hand-maintained: a list written from reading the source agrees with the
#: source by construction and disagrees with the shell silently.
CLOSURE = [
    ("activator", "env_root", "setup_salloc_env.sh"),
    ("hop1", "env_root", "unbinned_unfolding/build/setup.sh"),
    ("hop1", "env_root", "MINERvA101/opt/bin/setup.sh"),
    ("hop2", "env_root", "MINERvA101/opt/bin/setup_MAT.sh"),
    ("hop2", "env_root", "MINERvA101/opt/bin/setup_MAT-MINERvA.sh"),
    ("hop2", "env_root", "MINERvA101/opt/bin/setup_UnfoldUtils.sh"),
]

SOURCE_RE = re.compile(r"^\s*(?:source|\.)\s+(\S+)", re.M)


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def discover(env_root: str) -> list[tuple[str, str]]:
    """Walk the closure from the activator and report what it ACTUALLY sources.

    This is the anti-drift arm: if the closure grows a member, the declared CLOSURE list and this
    walk disagree, and the disagreement is the finding. It resolves `${SCRIPT_DIR}` and
    `${INSTALL_DIR}` because those are the only two indirections the real files use -- anything
    else is reported unresolved rather than silently skipped, since a source line nobody can
    resolve is exactly the hole this package exists to close.
    """
    found: list[tuple[str, str]] = []
    unresolved: list[str] = []
    seen = set()
    queue = [("activator", "setup_salloc_env.sh")]
    while queue:
        hop, rel = queue.pop(0)
        if rel in seen:
            continue
        seen.add(rel)
        p = os.path.join(env_root, rel)
        found.append((hop, rel))
        if not os.path.isfile(p):
            continue
        text = open(p, encoding="utf-8", errors="replace").read()
        for m in SOURCE_RE.finditer(text):
            raw = m.group(1)
            if text[:m.start()].rsplit("\n", 1)[-1].lstrip().startswith("#"):
                continue
            sub = (raw.replace('"', "").replace("'", "")
                      .replace("${SCRIPT_DIR}/", "").replace("$SCRIPT_DIR/", "")
                      .replace("${INSTALL_DIR}/", "MINERvA101/opt/")
                      .replace("$INSTALL_DIR/", "MINERvA101/opt/"))
            if "$" in sub:
                unresolved.append(f"{rel}: {raw}")
                continue
            queue.append(("hop", sub))
    if unresolved:
        for u in unresolved:
            print(f"[env-manifest] UNRESOLVED source line: {u}", file=sys.stderr)
    return found


def conda_scripts(prefix: str) -> list[str]:
    d = os.path.join(prefix, "etc", "conda", "activate.d")
    if not os.path.isdir(d):
        return []
    # `.sh` ONLY: bash activation never executes the .csh/.fish siblings, and binding a file that
    # cannot run would be a pin that cannot fail.
    return sorted(f"etc/conda/activate.d/{n}" for n in os.listdir(d) if n.endswith(".sh"))


def build(env_root: str, conda_prefix: str) -> tuple[list[tuple[str, str, str, str]], list[str]]:
    rows: list[tuple[str, str, str, str]] = []
    problems: list[str] = []

    declared = {rel for _r, _b, rel in CLOSURE}
    walked = {rel for _hop, rel in discover(env_root)}
    for extra in sorted(walked - declared):
        problems.append(f"the closure walk found a member the declared CLOSURE list does not name: {extra}")
    for missing in sorted(declared - walked):
        problems.append(f"the declared CLOSURE list names a member the walk did not reach: {missing}")

    for role, base, rel in CLOSURE:
        p = os.path.join(env_root, rel)
        if not os.path.isfile(p):
            problems.append(f"MISSING from the env root: {rel}")
            continue
        rows.append((role, base, rel, sha256(p)))
    for rel in conda_scripts(conda_prefix):
        rows.append(("conda-activate", "conda_prefix", rel, sha256(os.path.join(conda_prefix, rel))))
    return rows, problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="mnv_env_manifest.py", description=__doc__.splitlines()[0])
    ap.add_argument("--env-root", required=True)
    ap.add_argument("--conda-prefix", required=True)
    ap.add_argument("--write-tsv", help="the runtime manifest mnv_env_preflight.sh reads")
    ap.add_argument("--write-json", help="the identity record for the Gate-1 evidence")
    ap.add_argument("--check", action="store_true", help="verify without writing")
    a = ap.parse_args(sys.argv[1:] if argv is None else argv)

    for d, name in ((a.env_root, "--env-root"), (a.conda_prefix, "--conda-prefix")):
        if not os.path.isdir(d):
            print(f"[env-manifest] COULD NOT LOOK: {name} is not a directory: {d}", file=sys.stderr)
            return CANNOT_CHECK_EXIT

    rows, problems = build(a.env_root, a.conda_prefix)
    if problems:
        for p in problems:
            print(f"[env-manifest] VIOLATION: {p}", file=sys.stderr)
        return VIOLATION_EXIT
    if not rows:
        print("[env-manifest] COULD NOT LOOK: zero closure members resolved", file=sys.stderr)
        return CANNOT_CHECK_EXIT

    tsv = "".join("\t".join(r) + "\n" for r in rows)
    print(f"[env-manifest] {len(rows)} closure member(s): "
          f"{sum(1 for r in rows if r[1] == 'env_root')} under the env root, "
          f"{sum(1 for r in rows if r[1] == 'conda_prefix')} conda activate.d")
    if a.check:
        return OK_EXIT

    if a.write_tsv:
        with open(a.write_tsv, "w", encoding="utf-8") as fh:
            fh.write(tsv)
        print(f"[env-manifest] wrote {a.write_tsv}")
    if a.write_json:
        rec = {
            "schema": SCHEMA,
            "env_root": os.path.realpath(a.env_root),
            "conda_prefix": os.path.realpath(a.conda_prefix),
            "entry_count": len(rows),
            # binds the TSV the shell verifier actually reads -- see the module docstring
            "tsv_sha256": hashlib.sha256(tsv.encode()).hexdigest(),
            # ABSOLUTE paths, deliberately. A relative `path` beside a `sha256` is exactly the
            # shape docs/orchestration/verify_hash_bindings.py collects as a repo binding -- and it
            # did: it resolved `setup_salloc_env.sh` against the REPO and compared the repo's copy
            # against the ENV ROOT's digest, reporting a MISMATCH that was really a mis-resolution.
            # Absolute paths make these off-repo artifacts unresolvable to that collector, which is
            # the truth: they are outside every checkout by construction. The TSV the shell reads is
            # unaffected -- it carries base + relative path and resolves them itself.
            "entries": [{"role": r, "base": b,
                         "path": os.path.join(os.path.realpath(a.env_root) if b == "env_root"
                                              else os.path.realpath(a.conda_prefix), p),
                         "relpath": p, "sha256": s} for r, b, p, s in rows],
        }
        with open(a.write_json, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, indent=2, sort_keys=True)
        print(f"[env-manifest] wrote {a.write_json}  tsv_sha256={rec['tsv_sha256']}")
    return OK_EXIT


if __name__ == "__main__":
    raise SystemExit(main())
