# RECORD — OI-136: the ratchets were red and ran nowhere; classified, wired into CI, deferred (2026-10-28)

The close-items session owns `OI-136` (promoted by the director on 2026-10-28). This record
applies the director's ruling of the same day on the plan proposed to it. It changes no
analysis code and repairs no file: every fail-open file found is either an immutable record or
hash-bound.

## What was measured, at `412db651d`

`docs/orchestration/state/probe-oi136-sys-path-hijack-20260826.py` (read-only, exit 0, both
controls held): 211 `.py` files contain the hardcoded cluster root; **20 are FAIL-OPEN**, 82 insert
a path that is not rooted, and 109 have no `insert(0, …)`.

`AGENTS.md` said 9 remain and the fail-open ratchet pinned 16. Neither was current:

- The 9 are the files `AGENTS.md` named in September: three probe records, the published 2D arm and
  five receipt-bound files. They are still in the set.
- The 2026-10-09 classification added seven frozen October records, giving the ratchet's 16
  (`KNOWN_ISSUES.md` row 89).
- **Four more landed 2026-10-12..17** and are on neither ratchet's list. Dropping them from the
  measured 20 reproduces the recorded 16-file digest `7aa29431…` exactly, so nothing else moved.

| File | Added | What pins its bytes (sha256 prefix searched over the tree) |
|---|---|---|
| `docs/orchestration/state/2d-closeout/stageB/diagnostics/p5/driver_p5.py` | 2026-10-12 | `f71b5759…`: its `SHA256SUMS`, `DESIGN.md`, `analyze_p5.py`, `result/report_s4{2,3}.json` |
| `docs/orchestration/state/2d-closeout/stageC/pilot/p1/driver_p1.py` | 2026-10-13 | `3056e625…`: `AUTHORIZATION-20261013-2d-closeout-stageC-pilot-binding.md`, `AUTHORIZATION-20261015-2d-closeout-stageC-production-binding.md`, `2d-unfolding/re2/partc/re2c_analyze.py`, `evidence/results/p1*.json` |
| `docs/orchestration/state/2d-closeout/stageC/pilot/p2g2/driver_g2.py` | 2026-10-13 | `eb258cad…`: `AUTHORIZATION-20261013-2d-closeout-stageC-pilot-binding.md`, `pilot/manifest.json`, `analyze_g2.py`, `evidence/results/g2_s4{2,3}.json` |
| `2d-unfolding/driver_p1.py` | 2026-10-17 (`fa11e3fd4`) | byte-identical to the stage C p1 driver, `3056e625…`, so the same pins |

**Why nobody saw it.** Both OI-136 suites existed and would have fired:
`test_oi136_failopen_inventory_ratchet.py` (exact set and digest) and
`test_oi136_rooted_insert_ratchet.py` (every rooted insert listed, with a reason). Neither ran in the
hook or CI. `KNOWN_ISSUES.md` row 89 recorded this as "Not done: the hook does not run these
suites" after the same thing had happened with nine files in 2026-10-03..06. It happened again
within a week.

## What this change does

1. **Classifies** the four in both suites, with a new reason class `closeout_bound` in
   `test_oi136_rooted_insert_ratchet.py` and the constants 16 → 20 (`547508b3…`) in
   `test_oi136_failopen_inventory_ratchet.py`, naming each file. No listed file changed.
2. **Wires both suites into CI** (`.github/workflows/record-checks.yml`). The hook declines them
   on time and says so in its declined list.
3. **`AGENTS.md`:** the count *"and 9 remain (three probe records, …)"* is replaced by a pointer to
   `KNOWN_UNREPAIRED` in the rooted ratchet. The paragraph's rule "never quote a count from here" is
   kept.
4. **`KNOWN_ISSUES.md` row 89** gains a dated note at the head of its state cell. The earlier text is
   kept.

The director asked for a forward-only check with a reasoned exception line, tested in both
directions. The rooted ratchet already is that check, so no second implementation was written. Its
own tests cover the three cases:

- `test_no_file_outside_the_named_set_feeds_a_rooted_insert` fires on a new fail-open file;
- `test_the_scanner_is_SILENT_on_a_derived_root` passes a self-relative insert;
- `test_every_listed_file_carries_a_reason` refuses an exception with no reason.

It judges every tracked `.py` (`git ls-files`), not only the files a commit adds. That is stricter:
a new file outside the list fails whichever commit added it. The fail-open ratchet also reads
untracked files in the working tree.

## OI-136 — deferred

The remaining fail-open files are all exceptions with a reason: probe records, frozen records, the
published 2D arm under Joseph's 2026-08-23 ruling, receipt-bound files and the four close-out
drivers. None can be edited without voiding a record or a binding.

**Trigger.** Reactivate at the next re-issue of the bindings that pin these files, and repair the
insert in that re-issue. Reactivate as well if either ratchet goes red in CI with a new file.
