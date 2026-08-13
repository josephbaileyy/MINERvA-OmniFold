# HANDOFF — Session D (verifier), 2026-08-13, at `87fc5ba`

**Why this exists, stated honestly rather than compliantly.** A Codex relay recommended handing this
lane off to a fresh verifier, citing 4.24 MB / 612 assistant messages / **64 compaction markers**.
**The marker figure is void — see `BEN-165`; every lane has exactly two compactions and both of mine
are manual.** I am writing this anyway, because the lane is at a clean seam and a handoff record makes
the decision cheap in either direction. **That is the correct response to an UNRESOLVED verdict: remove
the cost of the choice rather than pretend to have made it.**

Per this repo's convention, every fact below lives somewhere else and is **pointed at, not restated**.

**Nothing is in flight.** No job, no cluster write, no pending delegate. Working tree clean, `lane-d`
and `origin/main` at the same commit.

## What this lane owns

- **BEN block `160-189`.** Allocated: 160–165. Next is 166. Recompute before allocating; the header
  says why.
- `docs/orchestration/VERDICTS-20260811-session-D.md` — V1…V20. **Three-branch verdicts always:
  PASS / BLOCK / UNRESOLVED, and UNRESOLVED is never re-read as the nearer of the other two.**
- Long-form: `FINDING-20260812-nested-conflict-markers-false-pass.md` (BEN-162),
  `FINDING-20260812-exit-contract-drifted-into-prose.md` (BEN-163),
  `FINDING-20260812-session-health-metric-counts-its-own-subject.md` (BEN-165).
- **Only a row's author reshapes it** (`CONVENTION-lane-worktrees.md`). Mine are shortest-first now:
  162 → 703, 163 → 693, 164 → 918, 165 → 930. The file maximum is `BEN-204` and is not mine.

## Open, and each says what it would take to close

| item | state |
|---|---|
| **Five routed shapes, UNJUDGED** | in the accepted triage order: (v) fail-open on missing `--gen`, `overlay_eavailW_band.py:97-98`; (i) non-resolving `see <block>.<key>` pointers; (iv) BEN-110's PSD claim; (iii) BEN-109 is not a detector; (ii) needs an execution-history harness |
| **`BEN-091` is stale** | 14 unswept `state/` receipts, no revision anchor. The shelf-life rule is the finding; the sweep is the work |
| **Thirteen commits unaudited by me** | post-hoc contents read only; the last audit covered ten of mine, one absorption found (`BEN-094` scope correction) |
| **`BEN-138`** | declined by me, left with C. Not orphaned — owned elsewhere |
| **Ledger freeze** | never formally closed with the lanes (`HANDOFF-20260813-0030Z-session-A.md`). A's to close. `V20` passes the VL re-id and does **not** cover the freeze |
| **S2b and S4c** | ship DECLARED-NOT-RUN, Joseph approved, in my wording |

## Discipline that cost something to learn — carry it or re-earn it

- **Commit as this lane, per invocation**, never by writing shared `.git/config`:
  `git -c user.email="lane-d-verifier@mnv.local" -c user.name="Lane D (verifier)"`.
- **`-F <file>`, never `-m`**, for any message with backticks or newlines, and read it back with
  `git log -1 --format=%B`. Re-resolve every sha after an amend. `BEN-164`, both halves.
- **Post-hoc contents read after every commit**, and `git log --oneline -S'<text>'` for the other
  direction. It is the only technique that ever caught an absorption at the moment it happened.
- **Read-only tooling is the lane's constraint, not a suggestion.** Reproduce in a temp dir; write only
  to `docs/orchestration/`. Every result in the three long-form files above was established without
  modifying a tracked file.
- **Route to Session A. This lane does not mail Joseph.**

## The two things a successor will otherwise re-derive

**A remedy applied to the site of the last failure is not applied to the class.** Four instances in two
days — `BEN-084(B)`, `BEN-094(i)`, `BEN-162`, `BEN-163` — and the last one crosses artifacts: the code
was repaired and its published contract was not. Pair it with B's `BEN-117`: *a unit check on a
predicate cannot see a short-circuit that skips it.* Together they give the actual rule — **the battery
is the form set across the input space AND the call path, and neither implies the other.**

**A false confession is more durable than a false accusation**, because its cost to the confessor reads
as verification already done. `BEN-160`, `BEN-161`. This is the close-out lesson for Joseph and it is
the one I would not want dropped.

## What I got wrong, since a handoff that only lists findings is an advertisement

Overstated one commit's severity and was refuted by A. Wrote a false justification into `BEN-096` that
C then quoted into a commit body. Recommended a `git config` write that would have edited shared state.
Misattributed `BEN-115` to A when it is B's. Absorbed C's `BEN-137` row into `7b26803`. Asserted "no
self-applied instrument closed a gap tonight" when six of my own rows refute it, and a peer adopted it
over its own hedged version. **Every one of these was caught by a peer, not by me** — which is the
argument for keeping the cross-lane review protocol whatever happens to the sessions.
