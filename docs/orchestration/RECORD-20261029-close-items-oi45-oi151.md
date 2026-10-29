# RECORD — OI-45 done and retired; OI-151 to Joseph's queue (2026-10-29)

Both items are applied on the director's rulings of 2026-10-29, which answered the close-items
session's proposals.

## OI-45 — (a) and (b), then retired

**(a)** `CONVENTION-receipt-ingredients.md` gains a section, "Who made a receipt". A receipt's author is
the author of its adding commit, `git log --diff-filter=A --format='%h %an <%ae> %cs' -- <path>`. No
author field goes into the JSON, because a self-reported name cannot be checked and duplicates git.
Measured over the 30 days to 2026-10-28:

- none of the 576 state JSON files added carries an author or committer key;
- of the 154 commits that added them, **144 named a lane** and **10 used the shared default**
  *"MINERvA-OmniFold agent (unattributed)"*.

**(b)** `receipt_author.py --check` runs in the pre-commit hook **only**. CI cannot change who
authored an existing commit. It refuses a commit that adds a `docs/orchestration/state/*.json` when
the identity the commit will carry (`git var GIT_AUTHOR_IDENT`, which sees `-c user.name`, the
environment and the config) is the shared default. The refusal prints the fix:
`git -c user.name="<your lane>" -c user.email="<lane>@minerva-omnifold.invalid" commit ...`.

`--self-test` makes real commits through a real hook in a throwaway repository, 7/7. It **refuses** an
unattributed commit that adds a receipt; the message carries the `-c user.name` fix, and the receipt
does not land. It **passes**:
- a lane identity given by `-c`;
- a lane identity given by the environment;
- an unattributed commit adding a non-receipt;
- an unattributed edit to an existing receipt.

Retired, since both parts are done. Dependency check: 0 hits for `OI-45`.

## OI-151 — owner Joseph, WAITING-JOSEPH

`usagectl` refuses the laptop's symlinked codex homes. Measured on 2026-10-28 with
`validate_account_home` only, calling no provider:

- codex-personal, codex-school and codex-waker are refused through `~/codex-homes/*` symlinks;
- codex-school2's home is absent at the declared path;
- claude-school-legacy is known dead here.

The refusal is deliberate. Joseph's `0d6c4dcf4` (2026-07-18, "Harden live usage dispatch gate") and
`test_usagectl.py:352-363` assert that even a symlink to a directory inside the same home is refused.

Joseph's options:

- **(B)** Invert the links on the laptop, so the real directories move to
  `~/codex-homes/{personal,school,school2}` and the `~/.codex-*` paths become symlinks to them. This
  needs no code and no `profiles.json` edit, and it is reversible, but it touches his credential
  directories.
- **(C)** Accept that the laptop is not a usage host. The dashboard already says NOT ASSESSABLE there.

**The director recommends (C)**, unless Joseph wants laptop quota readings. No session touches any
credential directory.

## The queue floor — `policy.json` `current_work_min` 10 → 1

The director ruled on 2026-10-28: *"the queue floor may drop below 10 as items finish; there is no
standing list."* `control_plane_lint.py:495-497` enforced the floor from `policy.json`, so retiring
OI-45 failed the lint (*"active work has 9 rows; minimum is 10"*). The value is lowered to **1**, not
0, so the lint still refuses an empty queue, which would mean routing had failed, not that the work
was done. The cap (15) and the self-test's own floor (`control_plane_lint.py:742`) are unchanged.
