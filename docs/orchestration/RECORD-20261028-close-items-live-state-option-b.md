# RECORD — LIVE-STATE: unread waker state renders as NO EVIDENCE; watch list pruned; OI-73 retired (2026-10-28)

The close-items session owns `OI-73`. This record applies the director's ruling of 2026-10-28
on the LIVE-STATE regeneration: option **(B)**, a Mac render plus a code fix. Option (A), reading
the canonical cluster checkout's waker state, was **not authorized**. It also records the
watch-list prune and the retirement of OI-73.

## The defect, and a correction to #469

#469 regenerated `LIVE-STATE.md` from a fresh clone on `login28`. The close-items session
reported that "all 14 probed rows read MEASURED". That was true only of the rows labelled MEASURED.
The **wake** rows were not measured: a fresh clone has no waker state directory, which is untracked
and lives in the canonical cluster checkout.
Search: `wakerctl (watches|events): NO EVIDENCE` (2 lines); `Last tick: never on unknown` (1); `close-items-livestate` (1) in docs/orchestration/LIVE-STATE.md @ e6303c49e

That render, now on `main`:

- read **`Last tick: never on unknown`**. A file that could not be read was rendered as the state
  "never".
- embedded the throwaway clone's absolute path (`…/close-items-livestate-20261029T021909Z/…`, 1
  occurrence), from the freshness check's message about a file inside that missing directory.

## The fix (`generate_live_state.py`)

- `_state_dir_readable()`, beside the existing watch-store and events-dir checks. When the waker
  state dir cannot be read, `tick_line()` renders **`Last tick: **NO EVIDENCE**`**: no tick receipt
  was read and no tick time is claimed. The scrontab and scron-job findings stay, since they are
  per-user scheduler measurements; a real one, such as "the managed scrontab block is absent", keeps
  the row LOUD. A finding about a file inside the unreadable dir is dropped, because it is not a
  measurement. No checkout path is printed.
- The wake section never records an unread tick into `live-state-last-known.json`, and it carries
  the last known value as attributed history instead.
- When a LOUD verdict coexists with a NO EVIDENCE source, the dashboard adds **"⚠ NOT A COMPLETE
  READING"**, so an UNHEALTHY line cannot be read as a full measurement.

**Tests.** `docs/orchestration/test_generate_live_state_unread_state.py`:

- an absent state dir with a healthy schedule gives NO EVIDENCE, with no "never" and no path;
- an absent state dir with an absent scrontab block gives LOUD on the scheduler finding, with no
  "never", no path, and no freshness finding;
- **control:** a readable state dir with no receipt still reads `Last tick: never on unknown`, which
  is a real reading;
- end to end: UNHEALTHY plus "NOT A COMPLETE READING", no path, and nothing recorded.

Three of the four fail on the old generator, and the control passes on both. The five existing
live-state suites still pass (72 tests).

## The render

On the Mac, in the PR's worktree, in write mode. The wake rows read NO EVIDENCE / UNKNOWN. There is
no host-local path in the file (searched for `/private`, `/Users`, `/tmp`, `/pscratch`).
`live-state-last-known.json` is unchanged, because this host measured nothing that the store records.
`--check-freshness` is FRESH. The next regeneration replaces #469's clone-path line, and this one
does.

## The watch-list prune

`state/live-state.json`'s `jobs` list is emptied. All eight watched jobs were terminal when measured
on `login28` on 2026-10-28: `57266000_[0-0]` `FAILED=1`, and the seven k=0 arrays
`57527866`–`57527875` `COMPLETE`. Their receipts are unchanged. A read-only render from a clone of
the prune branch on `login37` confirmed the config, and its output was not committed: it carried
the same defect.

## OI-73 — retired

Its terminal criterion is *"LIVE-STATE.md regenerated and `--check-freshness` reports FRESH at that
commit"*. That is met here, with the defect above fixed, so the regeneration does not carry a junk
path or an unread "never". It was the owner assignment two Joseph decisions waited on
(`DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md:234`,
`DECISION-20260906-joseph-authorizes-z-specification-only.md:120`). The regeneration they withheld
is done: #469, corrected here. Both decisions keep their text, and the row's text is kept with a
dated prefix.

**Still true, and not OI-73's:** `scrontab` on `login28` showed no `wakerctl`-managed block, so
nothing schedules `wakerctl tick`. That is a supervision fact for whoever runs campaigns, not a
dashboard defect.

## OI-139 — promoted (the director's standing list, second)

It replaces OI-73 to keep the promoted queue at `current_work_min` = 10. Its next action is to
propose one of the row's three remedy shapes, cheapest first.
