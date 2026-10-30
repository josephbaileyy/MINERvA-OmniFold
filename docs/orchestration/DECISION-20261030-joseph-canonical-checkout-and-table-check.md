# DECISION 2026-10-30 (later) — Joseph: reconcile the canonical cluster checkout; wire the open-items column check and reset the cap

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- **OI-74.** The close-items session measured the canonical cluster checkout `/pscratch/sd/j/josephrb/MINERvA-OmniFold`
  read-only (`RECORD-20261030-close-items-oi74-*`, PRs #541, #543).
  - It is at `32e403b84` (2026-08-29), an ancestor of `main`, 3,692 commits behind and 0 ahead.
  - Two tracked files are changed, both outputs of the live-state generator: `docs/orchestration/LIVE-STATE.md` and
    `docs/orchestration/state/live-state-last-known.json`.
  - 214 launchers hard-code that path, and KI 89's toy imports code from it.
- **OI-148.** The close-items session repaired two rows' cell structure, format only (#538). `check_open_items_columns.py`
  passes now, but nothing invokes it. The long-line ratchet fails at 147 lines over 400 bytes, against a pin of 112.

> OI-74: bring the main cluster checkout (/pscratch/.../MINERvA-OmniFold) up to current main?

Joseph's answer, verbatim:

> Yes, under preconditions (Recommended)

sha256 of the text plus a final newline begins `e0a05393f4ff156b`.

> OI-148: the open-items table checks. What should happen?

Joseph's answer, verbatim:

> Wire it, reset the cap (Recommended)

sha256 of the text plus a final newline begins `beee994aea1e507c`.

## What is decided

1. **The canonical checkout is fast-forwarded to `main`, under preconditions.** The option offered read: "A session
   declares it and I bind it: confirm no job is reading the tree, keep the two generated live-state files aside in a
   dated copy, fast-forward from the github remote, re-check HEAD and status. No other change."
   - The close-items session declares it, and the director binds it before anything is written.
   - **Preconditions, each a STOP if it fails:** `squeue --me` shows no job running or pending that reads the tree; the
     porcelain shows exactly the two tracked changes measured on 2026-10-30, and nothing else tracked; HEAD is still
     `32e403b84`.
   - **Then:**
     - copy the two files aside into a dated directory outside the tree, on pscratch, with their sha256;
     - restore them to HEAD;
     - `git fetch github`, then `git merge --ff-only github/main`.
     - Re-measure HEAD, which must equal the fetched `main`, and the porcelain, which must show the same untracked count
       or fewer.
   - Nothing else in the tree is touched. The untracked files stay, and no job is launched.
2. **The open-items column check is wired into the commit hook and CI,** and **the long-line ratchet pin is reset to
   147.** The pin can only fall from here. The option offered read: "Run the column check in the commit hook and CI so
   it can't silently break again, and set the long-line cap to today's 147 so it can only go down from here." The
   close-items session makes both changes in one PR, with a two-direction test of the wiring.

## Not changed

- Every claim and number. Nothing is submitted, deposited or tagged.
