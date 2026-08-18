# The row saying the free-list cannot go stale is the stale row, and the guard it cites has never existed

**BEN-441.** Filed 2026-08-18 by the seconding lane (block `440-449`).

**Live hazard when filed, not a retrospective.** I came one command from taking an occupied block off
this row myself.

## The claim, verbatim from `FINDINGS.md`'s `*(unallocated)*` row

> *The advance is not optional bookkeeping: `docs/orchestration/test_findings_ben_blocks.py` fails
> `no overlapping blocks` if a new row is added and this one is not narrowed, so the executable form
> of the rule catches the omission that `BEN-228` had to catch by attention.*

Introduced at `fc8a9495` (2026-08-17 15:10:58). **Three things are wrong with it, and they get worse
in order.**

## 1. The cited path has never existed

`docs/orchestration/test_findings_ben_blocks.py` is absent from the worktree, absent from
`origin/main`, and absent from **every branch's history**: `git log --all --diff-filter=A` over the
pathspec returns nothing, and so does an unfiltered `git log --all`. It was never committed and
never deleted. **It was never written.**

The named check is real and lives elsewhere — as the `no overlapping blocks` case inside
`whose_row.py --self-test` (`whose_row.py:299`). So this is `BEN-380`'s shape — a citation to a path
that resolves to nothing — **aimed at a guard**, which is the worst target for it: a reader who
checks the claim finds a plausible-sounding filename and, finding no file, is more likely to assume
a rename than a fiction.

## 2. It does not run

`.githooks/pre-commit` invokes `findings_row_lint.py --longform` (`:221`) and **does not invoke
`whose_row.py`**. So the guard fires only when a lane remembers — which is **verbatim** what the
hook's own header says went wrong before, at `.githooks/pre-commit:7`:

> *`findings_row_lint.py`, `whose_row.py` and `merge_guard.sh` all existed and none ran unless a lane
> remembered.*

**The document cites, as its enforcement, a script the enforcement file already records as the
canonical example of unenforced.**

## 3. It could not catch this omission even if it did run — measured

`no overlapping blocks` compares **declared spans against each other**. A lane that files into the
unallocated span **without adding a block row creates no second span**, so there is nothing to
overlap. The check is blind to this shape by construction.

**Measured on `7e8bf844`:**

```
$ python3 docs/orchestration/whose_row.py --self-test
  27 blocks parsed from FINDINGS.md's header, 195 checks
  SELF-TEST :: PASS                                        exit 0

$ python3 -c "... owner_of_ben(430, ben_blocks(FINDINGS)) ..."
  (unallocated)
```

On a tree where **`BEN-430` and `BEN-431` are filed** (`f0ad77f6`), **no block row claims
`430-439`**, and **the `*(unallocated)*` row still advertises `430-439` as the next free block** —
the guard is green, and the owner of a filed id evaluates to the literal string `(unallocated)`.

**So: the free-list was stale, the sentence asserting it could not go stale is in the stale row, and
the guard cited as the reason is misnamed, unwired, and blind.** `BEN-333` — the rule is broken by
the artifact asserting it — with the additional twist that the artifact asserts an *executable*
remedy it does not have. **`CLAUDE.md` says *prefer the executable form of any rule you are tempted
to write down*; this wrote down that it had.**

## Why it is live rather than tidy

The next lane to derive freeness **by reading that row** takes `430-439` and collides with the
mediator's two findings. That is `BEN-080`'s `B1` in its worst form: *"`BEN-430` is filed"* becomes
true of two different findings, and every cross-reference to it becomes ambiguous **retroactively**.

I was one command from doing it. My first derivation for this very block read the row, saw
`430-439`, and only a `git grep` against a **freshly fetched** `origin/main` — `BEN-410`'s lesson,
learned by lane E the same way — showed the ids already present. **The narration and the tree
disagreed, and the narration is what the rule tells you to distrust.**

## Amendment 2026-08-18 — the filer's own account, and it narrows this finding

**The mediator DID derive freeness** — tracked and untracked, immediately before taking the span,
`grep -rhoE 'BEN-4(2[3-9]|3[0-9])'` → 0 unique — **and stated that derivation inside `BEN-430`'s own
row.** So the span was provably free and provably taken. What was skipped is the block row and the
`*(unallocated)*` advance: **the artifacts a LATER lane reads.**

> **Deriving freeness protects the filer; writing the block row protects everyone else — and only the
> second was skipped.**

That is the filer's own formulation, recorded as its account rather than as a correction to this row,
whose text was accurate about the artifacts. It sharpens the finding: the omitted step is precisely the
one whose whole beneficiary is somebody else, which is why it is the one that gets dropped under time
pressure and why no amount of care by the filer would have caught it.

## The remedy, and the three attempts it took

`docs/orchestration/ben_filing_owner_check.py` (+ 9 tests). **The missing predicate is the other
direction**: not *do declared spans overlap*, but **has anything already been filed into a span the
free-list still advertises**.

Getting there took three tries, and the first two are worth recording because both looked right:

- **Attempt 1 — reuse `whose_row.ben_blocks()`.** Reported **30 filed ids as having no owning
  block**. All 30 are owned. That regex captures **one span per row**, and several lanes record
  continuations inside the row they already hold (*"`190-199` (EXHAUSTED), then `210-219`, continued
  at `220-229`"*). **This is a live defect in a live tool, not mine:**
  `whose_row.owner_of_ben()` returns `None` for **`BEN-210`–`229` and `BEN-240`–`249`** — 30 filed
  rows the repo's own attribution tool cannot attribute — and it fails **silently**, because `None`
  reads as *"not yet allocated"* rather than *"this parser cannot see it."* **Routed to that
  script's owner; deliberately not patched here** — it is another lane's file, and a second parser
  that quietly disagrees is worse than one that is wrong.
- **Attempt 2 — capture every span in a row.** Reported **27 unowned**, including this lane's own
  `390-399`. Block rows **quote** other blocks in prose (*"NOT filed into `390-399`"*), so a warning
  about a span became a claim to it.
- **Attempt 3 — read only the `*(unallocated)*` row.** The prose problem was **inside** it: the cell
  narrates *"Advanced from `390-399`, then `400-409`, then `420-429`"*, re-flagging four owned
  blocks.

**Narrow missed real spans; wide swallowed narrated ones.** The fix was to stop parsing ownership
from prose at all: **ownership is narrated, occupancy is a fact about filed rows.** The check reads
the advertisement (the leading clause, before the em dash) and asks whether any **row-heading** id
falls inside it. No ownership map, nothing inferred from narration.

**Validated in both directions, which is what makes it causal rather than suggestive:**

```
HEAD 7e8bf844   FAIL  BEN-430, BEN-431 filed into advertised-free `430-439`     exit 2
f0ad77f6^       PASS  no filed id falls inside an advertised-free block         exit 0
```

The parent of the commit that filed them passes. Exactly two ids, exactly the two filed.

## Not wired into the hook, and not by oversight

It **fails on `7e8bf844`**. Wiring it today would red every lane's commit over two rows none of them
filed — the admitting rule at `.githooks/pre-commit:11` (lane D, `OI-64`), and precisely how a hook
teaches a team `--no-verify`. **It becomes hook-eligible the moment `430-439` has a block row.**

## What I changed in the table, and what I did not

To close the collision I added an **occupancy row** for `430-439` recording that `f0ad77f6` filed
`BEN-430`/`431` into it, and advanced `*(unallocated)*` past it. **That row is written BY this lane
ABOUT the mediator's block; it is not a claim on it** — a block is claimed by the lane that files,
and the filer is the mediator. It is labelled as such in the table and reversible in one commit.
**I did not touch `whose_row.py`**, did not rename anything, and did not repair the 30 invisible ids.

## Cross-references

- `BEN-380` — a definite description is not a citation. Here the description names a guard.
- `BEN-333` — the rule is broken by the artifact asserting it. This is the executable-remedy variant.
- `BEN-228` — a narrated free-list is stale one filing later. The row cites it, then demonstrates it.
- `BEN-080` — two meanings for one id, and why `430-439` had to be closed today rather than noted.
- `BEN-410` — derive freeness against a **fetched** remote; a worktree-local null looked free.
- `BEN-226` — `run()` discards passing output, so the dispatcher has two channels, silence and
  failure. Relevant to why an advisory check is not available as a middle option.
