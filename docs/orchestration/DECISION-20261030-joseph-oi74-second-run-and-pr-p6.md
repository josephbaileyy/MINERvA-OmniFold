# DECISION 2026-10-30 (later) — Joseph: move the 4 byte-identical untracked files aside and fast-forward; retire the old verifier's row rules

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- **OI-74.** The bound fast-forward (`state/oi74-canonical-ff-20261030/`, #551, report #553) stopped at STOP 26 and rolled
  back cleanly, so the tree is where it started. Four untracked, not-ignored files sit at paths `main` adds:
  - `docs/orchestration/dashboard.html`
  - `docs/orchestration/dashboard_collector.py`
  - `docs/orchestration/test_dashboard_collector.py`
  - `nd-unfolding/tests/test_cstat_100rep.py`

  All four are byte-identical to `main`'s blobs. The binding forbade touching untracked files.
- **PR-P6 (OI-148's residual).** `docs/open-items/verify_open_items_restructure.py` cannot pass on today's table. It
  requires contiguous `OI-1..OI-N` ids, and at `9fbdc5d78` three more row rules fail on 135, 39 and 38 rows (#557).
  Nothing runs its `main`. The live column check is now in the hook and CI (#548).

> OI-74: the checkout update stopped safely (rolled back) because 4 untracked files sit where main adds files. All 4 are byte-identical to main's versions (3 dashboard files, 1 test). Let the next run move those 4 aside into the same dated folder, then fast-forward?

Joseph's answer, verbatim:

> Yes, move the 4 aside (Recommended)

sha256 of the text plus a final newline begins `4fc5310396305201`.

> PR-P6: an old table-format verifier (verify_open_items_restructure.py) can't pass: it requires contiguous OI ids, and about 135/39/38 rows fail three other row rules. Nothing runs it. What should happen?

Joseph's answer, verbatim:

> Retire its row rules (Recommended)

sha256 of the text plus a final newline begins `f6d333dcbef1186d`.

## What is decided

1. **A second fast-forward run is allowed** under a new declaration that the director binds. The option offered read: "A
   new declaration I bind: only those 4 byte-identical files move aside (with checksums), then the ff-only merge
   recreates them from main. Nothing else is touched."
   - Each of the four must still hash equal to the fetched `main`'s blob just before it is moved. Otherwise it is a STOP.
   - It moves into the existing dated aside directory, `/pscratch/sd/j/josephrb/oi74-ff-20261030`, under its own
     subdirectory with SHA256SUMS. The two live-state files stay where the first run put them.
   - A rollback restores all six files on any STOP after the first write.
   - Every other precondition and step of the first declaration stands.
2. **The old verifier's row rules are retired.** The option offered read: "The live column check (now in the hook and
   CI) covers table shape; record the old row rules as retired. No ids renumbered, no rows rewritten." The close-items
   session records the retirement beside `verify_open_items_restructure.py`'s row rules, and beside PR-J10 and PR-P6 in
   `PUBLICATION-READINESS-20260822.md` and `POST_PUBLICATION_REORG_PLAN.md:262`, without editing those documents. It
   then retires OI-148.

## Not changed

- Every claim and number. Nothing is submitted, deposited or tagged.
