# RECORD — the director's rulings on the 12 conditional rows not deferred in #501/#502 (2026-10-29)

The close-items session proposed these dispositions after batches A and B of backlog candidate 1. The director ruled
them on 2026-10-29. Measured at `1d25acd9e`.

## Deferred

| item | trigger |
|---|---|
| OI-2 | a recorded Joseph decision to quote a scalar-FPS (extended-fiducial) covariance |
| OI-32 | a recorded Joseph decision to quote a fine-grid full-covariance chi-square (it needs a 187-universe compute decision) |
| OI-34 | a recorded Joseph decision authorizing a new scalar unified-throw construction |
| OI-3 | PET being reconsidered for publication (Joseph's decision) |
| OI-37 | an FPS covariance adoption being scheduled (Joseph's decision) |
| OI-121 | OI-126 being reconsidered (estimator-equivalence plus coverage, DECISION-20260902 R6) |
| OI-132 | anyone needing to quote the OI-132 split, or to grade a data-only C_stat family |

OI-2, OI-32 and OI-34 touch publication. On the director's ruling, each trigger fires only on a recorded Joseph decision:
- FPS is quoted as central values only (`DECISION-20261026-joseph-fps-scope-r04-sensitivity-and-tex-reflow.md` §1.2:
  *"No covariance is quoted for it"*);
- the Ascencio comparison is central values only (`app_history.tex:292-297`);
- the successor proposal is a NO-GO for new compute.

OI-121's two hits mention it: `docs/known-issues/ISSUE-46-…` (where it was found), and
`RULING-20260817-lanec-oi126-branch-set-not-exhaustive.md:193` (*"OI-121/OI-122 do not reopen"*).

## OI-40 — retired, as moot

Its condition was *"after the corresponding full-event PET and adopted UQ products become quotable"*. Both halves are
settled:
- **The UQ half fired.** The adopted products are in the note: the scalar-5D trunk `3d7465f6…` and its projection
  `835828bf…` (`values.tex`, `sec_5d.tex`), and Q (`app_statmethods.tex:346`).
- **The PET half cannot fire.** PET is diagnostic under `DECISION-20260902` R6 and the 2026-08-20 ruling, and the
  PET note says so (`pet_note.tex:35`).

Dependency check: 0 hits.

## OI-60 — the re-run half deferred; the retrospective close stays on Joseph's queue

The row has two halves:
- **the prospective re-run**, which rides *"the next Gate-5 re-issue whenever one happens for an independent reason"*
  (151 A100-h, not purchasable at the current grant);
- **the retrospective close**, *"RECOMMENDED DISPOSITION, not taken here (PET lane's and Joseph's)"*.

So the deferral does not hide the close, the row is **not** deferred. It stays active with owner `joseph` and queue
`WAITING-JOSEPH`, for the retrospective close. Its prefix records that the re-run half is deferred to the next Gate-5
re-issue. Dependency check: 0 hits.

## Unchanged

- **OI-35** stays WAITING-JOSEPH as it is: requesting NEUT access is his.
- **OI-188** goes to owner `joseph`, `WAITING-JOSEPH`, on the director's second ruling of 2026-10-29. The register had
  shown it `NOW` and unassigned, and that mismatch was reported, then ruled. The record that makes continuing his decision
  is `DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md` R5 (`:143`): *"Continuing past the stop requires a
  fresh decision; continuation is not the default."* The row itself says *"(d) → Joseph, since it touches a ruling he
  confirmed directly."*

## OI-47 — retired, as superseded by the per-session worktree practice

On the director's second ruling of 2026-10-29, option (a). Lanes no longer run as harness background jobs whose
isolation that key would set. Each session makes its own `git worktree` (`docs/LOCAL_CHECKOUTS_AND_STORAGE.md`;
`CONVENTION-lane-worktrees.md`). **Option (b), writing the key into a Claude settings file, is not taken. No one edits
a Claude settings file for this.** The trigger (*"the next natural lane restart"*) has fired many times. Measured
read-only on 2026-10-29, reading only the key named here:
- `CLAUDE_CONFIG_DIR` is `/Users/josephbailey/.claude-school`;
- `worktree.bgIsolation` is **absent** from `~/.claude/settings.json`, `~/.claude-school/settings.json` and
  `~/.claude-personal/settings.json`, and no project `.claude/settings*.json` exists;
- `~/.claude-school/jobs/` holds **no** job directories;
- the only job state anywhere is `~/.claude-personal/jobs/76a4b8ef/state.json` (2026-08-25): `"bgIsolation": "none"`.

No credential or auth file was opened, and nothing outside the checkout was edited. Dependency check: one hit,
`AUTHORIZATION-20260812-hpss-copy-and-delegation.md:96`, which scheduled the fix for that restart. It is a mention, and
nothing waits on OI-47 staying active.

No row text is deleted. Each changed row gains a dated prefix pointing here.
