#!/usr/bin/env python3
"""Guard: a commit that ADDS a state receipt must not carry the shared, unattributed git identity.

    python3 docs/orchestration/receipt_author.py --check       # the gate (pre-commit only)
    python3 docs/orchestration/receipt_author.py --self-test   # both directions, real commits in a throwaway repo

WHY (OI-45). A receipt's author is the author of the commit that added it
(`git log --diff-filter=A --format='%an <%ae>' -- <path>`). A field inside the JSON would be
self-reported and could not be checked. Over the 30 days to 2026-10-28, 144 of the 154 commits that
added a state receipt named a lane, and 10 used the shared checkout's default identity, which names
no one.

WHAT IT CHECKS. If the staged index ADDS a `.json` under docs/orchestration/state/, the identity this
commit will be authored as (`git var GIT_AUTHOR_IDENT`, which sees `-c user.name`, the environment and
the config) must not be the shared default. Every committer can always pass it: pass your own
identity. It runs in the hook only. CI cannot change who authored a commit that already exists.

WHAT IT DOES NOT DO. It does not check that the name is truthful, or judge edits to existing receipts.
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SCOPE = "docs/orchestration/state/"
SHARED_NAME = "MINERvA-OmniFold agent (unattributed)"
FIX = ('git -c user.name="<your lane>" -c user.email="<lane>@minerva-omnifold.invalid" commit ...  '
       "(or export GIT_AUTHOR_NAME and GIT_AUTHOR_EMAIL)")


def git(*args, cwd=None, env=None):
    return subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True,
                          check=True).stdout


def author_name(cwd=None, env=None):
    ident = git("var", "GIT_AUTHOR_IDENT", cwd=cwd, env=env).strip()
    return re.sub(r"\s*<[^>]*>\s+\d+\s+[-+]\d{4}$", "", ident)


def added_receipts(cwd=None, env=None):
    names = git("diff", "--cached", "--name-only", "--diff-filter=A", cwd=cwd, env=env).split()
    return [p for p in names if p.startswith(SCOPE) and p.endswith(".json")]


def check(cwd=None, env=None):
    added = added_receipts(cwd, env)
    name = author_name(cwd, env)
    if added and name == SHARED_NAME:
        print(f"  FAIL this commit adds {len(added)} state receipt(s) ({', '.join(added[:3])}"
              f"{' ...' if len(added) > 3 else ''}) authored as the shared identity '{SHARED_NAME}',")
        print("       which names no one. A receipt's author is the author of the commit that adds it.")
        print(f"  fix: {FIX}")
        print(f"RECEIPT-AUTHOR :: {len(added)} added receipt(s); author is the shared default -- REFUSED")
        return 1
    print(f"RECEIPT-AUTHOR :: {len(added)} added receipt(s); author '{name}'"
          f"{'' if added else ' (nothing to judge)'}")
    return 0


def self_test():
    """Real commits through a real pre-commit hook in a throwaway repository, both directions."""
    with tempfile.TemporaryDirectory(prefix="receipt-author-") as tmp:
        root = Path(tmp)
        repo, hooks = root / "repo", root / "hooks"
        hooks.mkdir()
        (hooks / "pre-commit").write_text(f"#!/bin/bash\nexec {sys.executable} {Path(__file__).resolve()} --check\n")
        (hooks / "pre-commit").chmod(0o755)
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        g = lambda *a, e=env: subprocess.run(["git", "-c", f"core.hooksPath={hooks}", *a], cwd=repo,
                                              env=e, capture_output=True, text=True)
        subprocess.run(["git", "init", "-q", str(repo)], env=env, check=True)
        g("config", "user.name", SHARED_NAME)
        g("config", "user.email", "agent-unattributed@minerva-omnifold.invalid")
        (repo / SCOPE).mkdir(parents=True)

        def commit(path, *extra, e=env):
            (repo / path).write_text("{}\n")
            g("add", path, e=e)
            r = g(*extra, "commit", "-q", "-m", path, e=e)
            if r.returncode != 0:
                g("reset", "-q", e=e)
                (repo / path).unlink()
            return r

        refused = commit(SCOPE + "a-1.json")
        lane = commit(SCOPE + "b-2.json", "-c", "user.name=close-items", "-c", "user.email=ci@x.invalid")
        lane_env = commit(SCOPE + "c-3.json", e=dict(env, GIT_AUTHOR_NAME="envlane",
                                                      GIT_AUTHOR_EMAIL="e@x.invalid"))
        not_state = commit("notes.json")
        (repo / SCOPE / "b-2.json").write_text('{"edited": true}\n')
        g("add", SCOPE + "b-2.json")
        edit = g("commit", "-q", "-m", "edit")
        checks = {
            "unattributed commit adding a receipt is refused": refused.returncode != 0,
            # git hands a hook's output to the committer on stderr
            "refusal message gives the -c user.name fix":
                'git -c user.name="<your lane>"' in refused.stdout + refused.stderr,
            "the refused receipt did not land": "a-1.json" not in g("ls-files").stdout,
            "a lane identity via -c passes": lane.returncode == 0,
            "a lane identity via the environment passes": lane_env.returncode == 0,
            "unattributed commit adding a non-receipt passes": not_state.returncode == 0,
            "unattributed edit to an existing receipt passes": edit.returncode == 0,
        }
    for name, ok in checks.items():
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    print(f"RECEIPT-AUTHOR SELF-TEST :: {'PASS' if all(checks.values()) else 'FAIL'}")
    return 0 if all(checks.values()) else 1


def main(argv):
    if argv == ["--check"]:
        return check()
    if argv == ["--self-test"]:
        return self_test()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
