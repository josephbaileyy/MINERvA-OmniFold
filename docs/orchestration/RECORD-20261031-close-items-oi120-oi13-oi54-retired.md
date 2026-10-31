# RECORD — OI-120, OI-13 and OI-54 retired, register-only (2026-10-31)

**By** the close-items session, on the director's ruling of 2026-10-31, given after merging #566, #567 and #568.
Verbatim: *"Retire all three, register-only, as proposed: OI-120 (decided on 08-14, with (b) living in OI-22's own
deferral), OI-13 (superseded; KNOWN_ISSUES 40 WONTFIX; PET diagnostic), and OI-54 (stale). On OI-54's limit, record
the one-line question in its retirement row, unasked. It's not worth Joseph's time unless a sign of that session
appears."*

**CITABLE FOR:** the retirement of the three rows, the record each rests on, and the re-run of each dependency check
at `8be020466`.

**NOT CITABLE FOR:** any new measurement. The grounds are the three traced records. Nothing was run, and no session
was messaged.
<!-- absence-ok: a scoping statement about this record's own method -->

**Register-only:** each row is set to `retired`, with no queue, owner `close_items` and its section here as
authority, as OI-148 was. Its OPEN_ITEMS row gets a dated prefix; the text below the prefix is left as it stood.

## 1. OI-120 retired

**Ground:** [`RECORD-20261030-close-items-oi120-traced.md`](RECORD-20261030-close-items-oi120-traced.md) (#566).
Joseph decided all three parts on 2026-08-14 (*"For item four: a) yes, and yes do b) and c)"*). Parts (a) and (c) ran
that day. Part (b), the alignment proof, is OI-22's own next action, under OI-22's 2026-10-29 deferral. Retiring
OI-120 removes no route to it.

**Dependency check, re-run.** Search: `git grep -n -l 'OI-120'` @ `8be020466`, excluding `OPEN_ITEMS.md` and the generated views. The hits are the ones the traced record lists, plus that record and its CATALOG row. Each is history of (a) or (c), or a test pinned to (c)'s receipt. None routes open work to OI-120.

## 2. OI-13 retired

**Ground:** [`RECORD-20261030-close-items-oi13-traced.md`](RECORD-20261030-close-items-oi13-traced.md) (#567).
- The retired-bar self-report is `KNOWN_ISSUES` 40, `WONTFIX`.
- The gate, `validate_pet_nominal_gate4.check_powered_closure`, reads the adopted bar.
- PET has been diagnostic since 2026-08-20.

**PR-J9.** `PUBLICATION-READINESS-20260822.md` PR-J9 lists OI-13 among the items *"Standing, unanswered, and each is
his"*. That clause is answered here, beside the document, which is not edited. PR-J9's other items are untouched.

**Dependency check, re-run.** Search: `git grep -n -E 'OI-13([^0-9]|$)'` @ `8be020466`, excluding `OPEN_ITEMS.md` and the generated views. The only route is PR-J9 (`:421-426`), answered above. The other hits are the traced record and its CATALOG row.

## 3. OI-54 retired, stale

**Ground:** [`RECORD-20261030-close-items-oi54-traced.md`](RECORD-20261030-close-items-oi54-traced.md) (#568). Session
`98d9c5` and the row's owner were not among the live sessions listed on 2026-10-30, and no record after 2026-08-12
mentions the session.

**The limit, recorded and not asked.** The listing may not show a session run under another account. On the
director's ruling, the one-line question goes in the retirement row, unasked:
*"Is the interactive session `minerva-omnifold-07` (`98d9c5`), from 2026-08-13, still running anywhere?"* It is
worth Joseph's time only if a sign of that session appears.

**Dependency check, re-run.** Search: `git grep -n -E 'OI-54([^0-9]|$)'` @ `8be020466`, excluding `OPEN_ITEMS.md` and the generated views. One hit beyond the traced record and its CATALOG row: `FINDINGS-ARCHIVE-2026-08.md:38`, BEN-142, which names OI-54 as history. Nothing routes open work to OI-54.
