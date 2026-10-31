# RECORD — OI-62 retired; OI-143 and OI-9 deferred to named triggers, register-only (2026-10-31)

**By** the close-items session, on the director's ruling of 2026-10-31, after reading the three traced records.
Verbatim: *"all three proposals are accepted … OI-62: retire it, with (b)'s question recorded unasked. Leave the
whose_row.py:677-678 comment as noted. OI-143(b): close decision 1, and defer the residual on your trigger. Skip the
ratification question. OI-9: defer, with your owner shape recorded."*

**CITABLE FOR:** the register changes to the three rows and the record each rests on.

**NOT CITABLE FOR:** any new measurement. The grounds are the three traced records. Nothing was run, and the cluster
was not touched.
<!-- absence-ok: a scoping statement about this record's own method -->

**Register-only:**
- OI-62 is set to `retired`, with owner `close_items`, as OI-148 was.
- OI-143 and OI-9 are set to `deferred`, with owner `unassigned`, as the 2026-10-29 deferrals were.

Each row's authority is its section here. Each OPEN_ITEMS row gets a dated prefix, and the text below the prefix is
left as it stood.

## 1. OI-62 retired

**Ground:** [`RECORD-20261031-close-items-oi62-traced.md`](RECORD-20261031-close-items-oi62-traced.md) (#577).
- (a) is Joseph's decision of 2026-08-13.
- (b)'s block table and `--check-oi-ids` have been in force since 2026-08-14, and they pass.
- (c)'s condition, agents committing as Joseph, was 0 of 1,314 commits since 2026-10-01.

**Recorded, not asked:** *"Should `OI-*` ids keep lane blocks, or move to lane-prefixed ids (`OI-A64`)?"* It is worth
Joseph's time only if a new id collision appears, or if he wants the format changed.

**Left as noted:** `whose_row.py:677-678` still calls (c) *"WAITING-USER"*. It is a comment and changes no behaviour.

## 2. OI-143 deferred

**Ground:** [`RECORD-20261031-close-items-oi143b-traced.md`](RECORD-20261031-close-items-oi143b-traced.md) (#578).

**Decision 1 is closed as answered.** The question was whether the gate should exclude `tests/fixtures/**`. The
semantic `_fixture` holdout of `ea1a3fd6a` and `9bf92bdee` answers it: 12 fixtures, with pinned integrity. On the
director's ruling, no ratification question goes to Joseph.

**The residual is deferred.** It is the migration of the cluster's untracked-receipt bindings, and the
`train_fullevent_nominal.py` / job `56534116` mismatch. Trigger: *"the hash-binding gate is to be run in the canonical
checkout, or that checkout's untracked receipts are to be removed or purged."* The traced record's limit stands: only
a cluster read can say whether any untracked receipt is the only record of a binding.

## 3. OI-9 deferred

**Ground:** [`RECORD-20261031-close-items-oi9-traced.md`](RECORD-20261031-close-items-oi9-traced.md) (#580).

**Trigger:** *"a run of `run_p4_standard.sh` stage 3 (`p4_evidence.py`) is declared, or a defect is reported in its
merged-audit checks."*

**The owner shape, recorded for when it fires** (the traced record's §3):
- one code lane that can run Python with ROOT, plus one read-only cluster read, in one PR, with no physics change;
- a pure per-endpoint blocker function, called from `p4_evidence.py:208-283`;
- ROOT-free tests in both directions, built from the committed `p4_merged_audit.json`;
- `COUNT_CONSUMERS` re-pointed;
- read-only ROOT parity against the receipt.

## 4. Dependency check

The traced records' checks stand. At `11ada353f`:
- Search: `git grep -n 'OI-62'` @ `11ada353f`. Beyond the traced record and its CATALOG row: the six comments it lists (`.githooks/pre-commit:241`, `whose_row.py` ×5). None routes open work.
- Search: `git grep -n 'OI-143'` @ `11ada353f`. Beyond the traced record and its CATALOG row: the seven history hits it lists (`verify_hash_bindings.py` ×6, the DESIGN format note). None routes open work.
- Search: `git grep -n -E 'OI-9([^0-9]|$)'` @ `11ada353f`. Only the traced record and its CATALOG row. None routes open work.

Each search excludes `OPEN_ITEMS.md` and the generated views.
<!-- absence-ok: the searches and sha are named in this section -->
