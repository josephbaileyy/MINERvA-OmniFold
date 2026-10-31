# RECORD — OI-62 traced: (a) is Joseph's, (b) has been in force since 2026-08-14, and (c)'s condition is gone (2026-10-31)

**By** the close-items session, on the director's order of 2026-10-31. Read-only: it uses `git log`, `git grep` and
one run of `whose_row.py --check-oi-ids`, all at `efd014670`.

**CITABLE FOR:** what governs each of OI-62's three parts at `efd014670`, and the commit-identity counts in §2.

**NOT CITABLE FOR:**
- which convention Joseph would prefer for `OI-*` ids;
- who wrote any particular commit. The counts read author fields, which are self-declared.
<!-- absence-ok: scoping statements about what this record's own measurements cover -->

**PROPOSES:** retiring OI-62, with (b)'s convention question recorded in the row and not asked (§3). The register is
not changed here; the ruling is the director's.

## 1. What the row waits on

OI-62 is `WAITING-USER`, owner *"orchestration / Joseph"*, dated 2026-08-13. Its own last sentence: *"Joseph decides
(a), (b)'s convention and (c)'s enforcement."*
- **(a)** May lanes self-allocate `BEN-*` blocks?
- **(b)** `OI-*` ids have no block table and no addressing convention. Decide on per-lane blocks, a `Lane X` trailer,
  or *"OI ids are append-only and unowned"*.
- **(c)** The enabling condition: *"three parties commit as `Joseph Bailey <josephrb@stanford.edu>`"*.

## 2. Each part, traced

**(a) is decided.** Joseph's words are in the row: *"Let the lanes self allocated BEN ids"*, committed in `551d16c66`
(2026-08-13, *"Joseph's two decisions: lanes self-allocate BEN ids …"*). The row's own state cell says (a) is
RESOLVED.

**(b) has a mechanism that has been in force for 2.5 months. Only the preference between blocks and prefixes is
still open.**
- `e4db2e269` (2026-08-14, lane A) added the `OI-*` block table at the top of `OPEN_ITEMS.md`. It also added the
  block arm of `whose_row.py --check-oi-ids`, the hook's check *"OPEN_ITEMS OI ids"* (`.githooks/pre-commit:248`).
- The table now holds twelve allocated blocks: the six it was created with, and six self-allocated between 2026-08-21
  and 2026-09-24, each in the commit of its first filing. The newest id is `OI-193`,
  filed on 2026-09-26 (`5683e329e`).
- The check run at `efd014670`: *"142 data rows, 142 OI ids, 2 duplicated, 2 waived"*, `OI-IDS :: PASS`. The only
  duplicates are `OI-64` and `OI-65`, both from 2026-08-13, before the table existed. Both are waived in
  `whose_row.OI_ID_WAIVERS`. This counts the duplicates in the file now. A collision that was renumbered away would
  not show here.
- **What stays open**, in the row's words: *"whether `OI-*` should use lane blocks AT ALL rather than lane-prefixed
  ids (`OI-A64`)"*. The row also says: *"If he prefers prefixes, the ids allocated under this table remain valid
  unique integers and nothing becomes wrong."* The table's own header says the same: *"remains formally Joseph's
  call"* (`OPEN_ITEMS.md:80-81`).
- Search: `git log --grep='lane-prefixed\|OI-62' -i` @ `efd014670`. No later commit records a decision by Joseph on
  this preference.
<!-- absence-ok: the search and sha are named in this paragraph -->

**(c)'s enabling condition is gone.** Non-merge commits on `efd014670`, counted with `git log --no-merges --since`
by author email:

| since | commits | as `josephrb@stanford.edu` | as the shared default `agent-unattributed@…` |
|---|---|---|---|
| 2026-08-01 | 4,857 | 447 | 1,224 |
| 2026-09-01 | 2,864 | 7 | 1,021 |
| 2026-10-01 | 1,314 | **0** | 47 |

- The shared default is no longer Joseph's identity. It is `MINERvA-OmniFold agent (unattributed)`, the name that
  `receipt_author.py:28` refuses.
- Per-commit identity is playbook rule PB-18, active: *"Concurrent lanes use isolated worktrees and per-commit
  identities."*
- The hook refuses an unattributed commit that adds a state receipt. That is `receipt_author.py --check`, from OI-45,
  done and retired on 2026-10-29
  ([`RECORD-20261029-close-items-oi45-oi151.md`](RECORD-20261029-close-items-oi45-oi151.md)).
- **What remains:** 47 of 1,314 commits since 2026-10-01 (3.6%) carry the shared default. That is an attribution gap,
  not the condition the row names. `whose_row.py:689` keeps its own conditional TODO for it (*"if OI-62(c) is
  resolved such that every committer carries a lane identity … Revisit then, not before"*). That TODO lives in the
  code and does not need the row.

**The addressing symptom.** Four rows still carry a dead sibling link `[OI-NN](#)`: OI-52, OI-120, OI-122 and OI-80
(`OPEN_ITEMS.md:182, 202, 204, 205`). The row records that only a row's author reshapes it. Retiring OI-62 changes
none of them.

## 3. The proposal

**Retire OI-62.**
- (a) is Joseph's decision, already made.
- (b)'s mechanism is in force, enforced by the hook and passing.
- (c)'s named condition, agents committing as Joseph, measured zero since 2026-10-01.

What is left is a preference that the row itself says breaks nothing whichever way it goes.

**Record (b)'s question in the retirement row, unasked**, as was done for OI-54: *"Should `OI-*` ids keep lane
blocks, or move to lane-prefixed ids (`OI-A64`)?"* It is worth Joseph's time only if a new id collision appears, or
if he wants the format changed.

**The alternative,** if the director prefers to keep it open: narrow OI-62 to that one question, owner Joseph.

**Dependency check.** Search: `git grep -n 'OI-62'` @ `efd014670`, excluding `OPEN_ITEMS.md` and the generated
views. Six hits, all comments or docstrings:
- `.githooks/pre-commit:241`;
- `whose_row.py:647, 677, 689, 722, 729`.

They describe (b) as *"still Joseph's call"*, which stays true if the question is recorded unasked. `whose_row.py:677-678`
calls (c) *"WAITING-USER"*. A retirement would make that phrase stale. It is a comment and changes no behaviour, so
this record notes it rather than editing the file.
<!-- absence-ok: the search and sha are named in this paragraph -->

Inside `OPEN_ITEMS.md`, other rows cite OI-62 as history: OI-148, OI-152, OI-144, OI-58 and OI-64. One cites it as a
route: OI-2 split its scalar-FPS remainder *"once `OI-*` has a block table"*. That trigger was met on 2026-08-14.
OI-2 itself is `deferred` under
[`RECORD-20261029-close-items-conditional-proposals-ruled.md`](RECORD-20261029-close-items-conditional-proposals-ruled.md),
so nothing waits on OI-62 there.
