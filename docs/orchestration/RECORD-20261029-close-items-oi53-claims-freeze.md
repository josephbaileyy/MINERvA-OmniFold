# RECORD — `CLAIMS.md` frozen, and OI-53 retired as moot (2026-10-29)

**By** the close-items session, carrying out Joseph's decision
[`DECISION-20261029-joseph-freeze-claims-md.md`](DECISION-20261029-joseph-freeze-claims-md.md) (#516), on the director's
order. Measured at `origin/main` `82e4957ae`.

## What changed

- **The classification.** `MANIFEST-overrides.tsv` moves `docs/orchestration/CLAIMS.md` from LIVE / open to
  ARCHIVAL / terminal, the class its twelve detail files `CLAIM-CLM-001.md` … `CLAIM-CLM-012.md` already carry.
- **A dated header line.** `CLAIMS.md` gains a blockquote under its title, in the form the archived `MIGRATION-*`
  records use (`> **ARCHIVAL/INDEX-ONLY (2026-07-19).** …`). It names the decision and the commit the rows stand at,
  `b8a0e117e` (2026-08-18).
- **Nothing else in `CLAIMS.md`.** Every row, status, verifier field and detail link is byte-identical. The diff is the
  five added lines.
- **Not changed:** `ROW-OWNERS.tsv`, whose twelve CLM rows stay `UNASSIGNED`. The decision does not ask for an edit
  there, and the banner says why the cells stay as they are.

## OI-53 — retired, as moot

**The row asked for** an adjudication of who owns the twelve `CLM` rows. Joseph chose option A of the packet
([`DECISION-PACKET-20261029-oi53-clm-row-ownership.md`](DECISION-PACKET-20261029-oi53-clm-row-ownership.md) §6): freeze the
ledger, so no owner is needed. With no row to edit, the question has no remaining object. A future claim, or an edit
to a frozen row, would need its own record and an owner decided then.

## Every CLM citation still resolves

Search: `git grep -P "CLM-0(0[1-9]|1[0-2])(?![0-9])"` and markdown links to `CLAIMS.md` or `CLAIM-CLM-0NN.md` across the
tree, excluding `MANIFEST.tsv`, @ `82e4957ae`.

- **By id:** 110 files cite the ids, 444 mentions in all, every one of `CLM-001` … `CLM-012`. Each id still has its row
  in `CLAIMS.md` and its detail file, and freezing moves neither.
- **Other ids:** the only other `CLM-` numbers in the tree are `CLM-900`, `901`, `902` and `999`, which are
  `whose_row.py`'s own self-test fixtures.
- **By link:** 35 files name `CLAIMS.md` or a detail file. Of those, 3 hold 20 markdown links to them. All 20 resolve,
  and none carries an anchor that the banner could shift.
- **Re-checked on this commit's tree:** 111 files and 451 mentions, the added ones being this record's own; 20 links
  in 3 files, all resolving.
- **The note's citations,** `app_history_pet.tex:27` and `:77` and `values.tex:100` (CLM-010, CLM-012), name ids, not
  paths or anchors. They resolve as before.
- **Code that names a row:** `nd-unfolding/pet/extract_fullevent_fps.py:53`, `:500` and `:527`, and
  `nd-unfolding/tests/test_fullevent_extract.py:368`, cite *"CLAIMS.md CLM-011"* in prose.
- **Code that reads the file:** `whose_row.py --check-owners` matches table rows that begin `| CLM-NNN |` (`:805`,
  `:814`). Every `ROW-OWNERS.tsv` row needs its `CLAIMS.md` row, and every `CLAIMS.md` row needs an owner entry. The
  banner adds no table row, and the check passes. `generate_manifest.py:296` only names the file's kind, `ledger`.

## Dependency check

Search: `git grep -P "OI-53(?![0-9])"` over `KNOWN_ISSUES.md`, `docs/known-issues/`, the DECISION, RULING,
AUTHORIZATION and OPERATIVE records, `docs/publication/`, `docs/analysis-note/` and `measurement-paper/` @ `82e4957ae`.

Result: the only hits are #516's decision record and the packet, both of which are about this retirement. Across the
whole tree, the other hits are the register (`OPEN_ITEMS.md`, `work-items.tsv`), its derived views and `CATALOG.md`.

The hook and CI checks of `whose_row.py` (`--check-owners`, `--self-test`, `--check-ledger-ids`, `--check-oi-ids`)
pass on this commit; see the PR.
