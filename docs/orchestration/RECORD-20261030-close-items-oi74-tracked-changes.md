# RECORD — addendum to the OI-74 re-measurement: the canonical checkout's two tracked changes are its live-state outputs (2026-10-30)

**By** the close-items session, on the director's order of 2026-10-30: name the two tracked changes before OI-74 goes
to Joseph, by a dated addendum. The connect the director approved: `git status --porcelain --untracked-files=no`,
plus `git diff --stat` for those paths only, with `GIT_OPTIONAL_LOCKS=0`. No file contents, no writes.

**An addendum beside its record, not inside it.** The record it adds to,
[`RECORD-20261030-close-items-oi74-canonical-drift.md`](RECORD-20261030-close-items-oi74-canonical-drift.md) (#541),
is ARCHIVAL, and `MANIFEST.tsv` marks it `immutable` `yes` (`generate_manifest.py:327-345`). So it is left unchanged.
Its §1 count of 2 tracked changes stands; this record names them.

**CITABLE FOR:** the two paths, their status codes and their `diff --stat` line counts at 2026-10-30T16:18Z.

**NOT CITABLE FOR:**
- what the changed lines say. No file contents were read;
- who or what wrote the changes, or when. No mtimes were read;
- an authorization to discard, stash, commit or overwrite them.
<!-- absence-ok: scoping statements about this record's own read, which the director limited to status and diff --stat -->

## The measurement

**One ssh to `saul.nersc.gov`,** answered by `login37` from 16:18:08Z to 16:18:09Z
([`state/oi74-canonical-drift-20261030/connect-session-2.txt`](state/oi74-canonical-drift-20261030/connect-session-2.txt),
sha256 `0308d376c5d171d1…`, which holds the script and its output). HEAD was still `32e403b84`. Both git calls
returned rc 0.

| path | status | `git diff --stat` |
|---|---|---|
| `docs/orchestration/LIVE-STATE.md` | ` M`: changed in the working tree, not staged | 18 lines changed |
| `docs/orchestration/state/live-state-last-known.json` | ` M`: changed in the working tree, not staged | 84 lines changed |

In all, 50 insertions and 52 deletions over the two files.

## What the two paths are

**Both are the outputs of `generate_live_state.py`.** At the checkout's own HEAD `32e403b84`,
`docs/orchestration/generate_live_state.py:24` sets `DEFAULT_OUTPUT = HERE / "LIVE-STATE.md"` and `:41` sets
`LAST_KNOWN_PATH = HERE / "state" / "live-state-last-known.json"`. So the changes match a regeneration of the live
state in that checkout. `AGENTS.md` routes *"What is happening now?"* to running that generator on Perlmutter from
canonical main. Which run wrote them was not measured.
<!-- absence-ok: a scoping statement about this record's own read; mtimes were outside the approved connect -->

**Neither is a `.py` or `.sh` file.** The checkout's tracked changes are a generated view, not edited code.

## What it means for a reconciliation

**A fast-forward would collide with both.** Main has changed both paths since `32e403b84`. Counted locally at
`origin/main` `91a27ad1b`, with `git rev-list --count 32e403b84..origin/main -- <path>`:
- `LIVE-STATE.md`: 3 commits;
- `live-state-last-known.json`: 2 commits.

git refuses a merge that would overwrite an uncommitted change to a file the incoming commits touch. So precondition 1
of the 2026-10-30 record, disposition the two tracked changes first, is a real step, not a formality. Whether to
discard them as a stale generated view or keep them first is Joseph's call with the reconciliation. Neither is
proposed here.
