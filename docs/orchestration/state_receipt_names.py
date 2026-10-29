#!/usr/bin/env python3
"""Guard: a NEW state receipt named with a scheduler-state word must say when that was true.

    python3 docs/orchestration/state_receipt_names.py --check          # the gate (pre-commit): staged additions
    python3 docs/orchestration/state_receipt_names.py --base REF       # CI: files added since merge-base(REF, HEAD)
    python3 docs/orchestration/state_receipt_names.py --existing       # report the inherited matches; judges nothing
    python3 docs/orchestration/state_receipt_names.py --self-test      # both directions, in a throwaway repository

WHY (OI-139). Fourteen receipts under docs/orchestration/state/ carry `active` in their filename.
Re-measured on 2026-10-28, every one describes a finished job (13 COMPLETED, 57266000 FAILED, 56935552
CANCELLED/FAILED), and a filename cannot be corrected, because paths are provenance. A state word in a
name is true only when it is written, so a new one must carry the time it was true.

WHAT IT CHECKS. A `.json` file this change ADDS anywhere under docs/orchestration/state/ whose name,
split on `-`, `_` and `.`, has a token `active`, `live` or `armed`, must hold a top-level
`recorded_at_utc` that is a non-empty string. Token matching, not substring: `deliverable` and
`inactive` do not match. Existing files are never judged. The check reads only the paths a change
adds, so the 14 inherited names cannot turn it red (`--existing` lists them).

WHAT IT DOES NOT DO. It does not check that the time is right, or look inside keys. Key words such as
`active` mostly name physics here (active-universe laterals), so a key lint would mostly fire on
vocabulary (OI-139's record).
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCOPE = "docs/orchestration/state/"
STATE_WORDS = {"active", "live", "armed"}
TIMESTAMP_KEY = "recorded_at_utc"


def git(*args, cwd=REPO):
    # A throwaway repository must not inherit the hook's GIT_INDEX_FILE, GIT_DIR or work tree.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")} if cwd != REPO else None
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True,
                          env=env).stdout


def in_scope(path):
    return path.startswith(SCOPE) and path.endswith(".json")


def names_a_state(path):
    stem = path.rsplit("/", 1)[-1][: -len(".json")]
    return bool(STATE_WORDS & set(re.split(r"[-_.]", stem.lower())))


def problem(path, text):
    """None if the receipt passes, else the reason it does not."""
    if not names_a_state(path):
        return None
    try:
        data = json.loads(text)
    except ValueError:
        return f"{path}: names a state but is not valid JSON, so no `{TIMESTAMP_KEY}` can be read"
    value = data.get(TIMESTAMP_KEY) if isinstance(data, dict) else None
    if isinstance(value, str) and value.strip():
        return None
    return (f"{path}: its name asserts a scheduler state ({'/'.join(sorted(STATE_WORDS))}) but it "
            f"has no top-level `{TIMESTAMP_KEY}`, so a reader cannot tell when that was true")


def judge(paths, read, cwd=REPO):
    added = [p for p in paths if in_scope(p)]
    found = [msg for p in added if (msg := problem(p, read(p, cwd)))]
    return added, found


def staged_additions(cwd=REPO):
    return git("diff", "--cached", "--name-only", "--diff-filter=A", cwd=cwd).split()


def base_additions(base, cwd=REPO):
    mb = git("merge-base", base, "HEAD", cwd=cwd).strip()
    return git("diff", "--name-only", "--diff-filter=A", mb, "HEAD", cwd=cwd).split()


def read_index(path, cwd=REPO):
    return git("show", f":{path}", cwd=cwd)


def read_head(path, cwd=REPO):
    return git("show", f"HEAD:{path}", cwd=cwd)


def report(added, found, label):
    for msg in found:
        print(f"  FAIL {msg}")
    print(f"STATE-RECEIPT-NAMES :: {label}: {len(added)} added state json judged; "
          f"{len(found)} name a state without `{TIMESTAMP_KEY}`; existing files are not judged")
    return 1 if found else 0


def existing(cwd=REPO):
    tracked = [p for p in git("ls-files", SCOPE, cwd=cwd).split() if in_scope(p)]
    named = [p for p in tracked if names_a_state(p)]
    for p in named:
        print(f"  inherited, not judged: {p}")
    print(f"STATE-RECEIPT-NAMES :: {len(named)} of {len(tracked)} tracked state json name a state; "
          "none is judged")
    return 0


def self_test():
    with tempfile.TemporaryDirectory(prefix="state-receipt-names-") as tmp:
        repo = Path(tmp)
        g = lambda *a: git("-c", "core.hooksPath=/dev/null", "-c", "user.name=t", "-c", "user.email=t@t",
                           *a, cwd=repo)
        g("init", "-q")
        state = repo / SCOPE
        state.mkdir(parents=True)
        old = SCOPE + "gate-array-active-1.json"
        (repo / old).write_text('{"job": 1}\n')
        g("add", "."); g("commit", "-q", "-m", "base")
        # untouched existing file with no timestamp: never judged
        silent_existing = judge(staged_additions(repo), read_index, repo)[1] == []
        # new state-named file without a timestamp: fires
        bad = SCOPE + "k0-array-active-2.json"
        (repo / bad).write_text('{"job": 2}\n'); g("add", bad)
        fires = [m for m in judge(staged_additions(repo), read_index, repo)[1] if bad in m]
        # the same file carrying the timestamp: silent
        (repo / bad).write_text('{"job": 2, "recorded_at_utc": "2026-10-28T00:00:00Z"}\n'); g("add", bad)
        silent_with_ts = judge(staged_additions(repo), read_index, repo)[1] == []
        # an empty timestamp is not a timestamp
        (repo / bad).write_text('{"job": 2, "recorded_at_utc": " "}\n'); g("add", bad)
        fires_empty = len(judge(staged_additions(repo), read_index, repo)[1]) == 1
        # token, not substring: these names assert nothing
        for name in ("deliverable-3.json", "inactive-lanes.json", "relive_notes.json"):
            (repo / SCOPE / name).write_text("{}\n"); g("add", SCOPE + name)
        (repo / bad).write_text('{"job": 2, "recorded_at_utc": "2026-10-28T00:00:00Z"}\n'); g("add", bad)
        silent_tokens = judge(staged_additions(repo), read_index, repo)[1] == []
        # CI mode: the same rules over what HEAD adds since a base
        g("commit", "-q", "-m", "add")
        base_ok = judge(base_additions("HEAD~1", repo), read_head, repo)[1] == []
        (repo / SCOPE / "live-watch-4.json").write_text('{"x": 1}\n'); g("add", "."); g("commit", "-q", "-m", "bad")
        base_fires = len(judge(base_additions("HEAD~2", repo), read_head, repo)[1]) == 1
        # an edit to the inherited file is a modification, not an addition: not judged
        (repo / old).write_text('{"job": 1, "note": "edited"}\n'); g("add", old)
        silent_modified = judge(staged_additions(repo), read_index, repo)[1] == []
    checks = {"existing file not judged": silent_existing, "new state name without timestamp fires": bool(fires),
              "same file with timestamp silent": silent_with_ts, "empty timestamp fires": fires_empty,
              "token not substring": silent_tokens, "CI base mode silent when clean": base_ok,
              "CI base mode fires on a bad addition": base_fires, "modified inherited file not judged": silent_modified}
    for name, ok in checks.items():
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    print(f"STATE-RECEIPT-NAMES SELF-TEST :: {'PASS' if all(checks.values()) else 'FAIL'}")
    return 0 if all(checks.values()) else 1


def main(argv):
    if argv == ["--check"]:
        return report(*judge(staged_additions(), read_index), "staged")
    if len(argv) == 2 and argv[0] == "--base":
        return report(*judge(base_additions(argv[1]), read_head), f"since merge-base with {argv[1]}")
    if argv == ["--existing"]:
        return existing()
    if argv == ["--self-test"]:
        return self_test()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
