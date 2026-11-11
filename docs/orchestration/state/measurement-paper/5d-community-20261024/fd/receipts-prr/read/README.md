# FD-PRR: the PRR read (receipt)

The valid-region lane ran this on 2026-11-09, on the director's go for `prr_read_connect.sh` at sha256
42716ca4f7eee3523ad2f85f93c080ed4dec9874dc4237622cc08bc27d30ad47. It follows FD-PRR BINDING 1 addendum A4 ruling 1:
the read runs from M_A4 = cb13a6443a457bd3887d1c421723dfcdb1909ec8, from a fresh clone (addendum A2 §6), after all five
jobs completed. `prr_read.py` (d7c7c2c0…, A2's bytes) ran unchanged and printed `{"verdict": "COMPLETE"}`, rc 0.

**No reading is quoted in this receipt.** The readings (PR-1 to PR-3, R-ID, R-SUP, C-IBU and the composite labels) are
in `cluster/readout.json` and `cluster/readout.txt`. By binding 1 ruling 8 they go to the director, who reads them and
reports to Joseph before any wording.

- **readout.json** sha256 9238f22bfe29685e33c1d5bb46da3938a3ebfdc93a54575a4fe99de3a7af9ead, 372,128 bytes.
- **readout.txt** sha256 8175033c7fcbd61e73b93defec7aceb484d30cc3757f4b089b21a3b0b32809e3, 34,386 bytes.

**The regenerated index files** are `RESULTS-INDEX.tsv`, `RESULTS-POPULATION.tsv`,
`docs/analysis-note/records_results_index.tex` and `records_estimators.tex`.
- readout.json joins the results population (6 metric rows). This PR therefore carries those four files as
  `tools/registry/results_index.py --write` generated them.
- Their new rows are generated machine listings of committed metrics, marked UNATTRIBUTED. They are not paper or note
  text and carry no wording. This follows the director's ruling of 2026-11-09 (option (a)), the same path as FD-STAB's
  readout.
- The keys and location of readout.json are as prr_read wrote them.

CITABLE FOR: that the PRR read ran as bound and completed; the two outputs' sha256 and bytes; the connect's checks.
NOT CITABLE FOR: any reading or wording, until the director's read and report to Joseph.
<!-- absence-ok: a scoping statement of what this receipt quotes, under binding 1 ruling 8 -->

## The session (`lane/read-session.txt`; the connect's log is `cluster/connect-read.log.txt`)

- **The session.** One foreground ssh session on login24, from 2026-11-09T23:34:28Z to 23:35:49Z, with ssh rc 0 read
  unpiped.
  - The connect was staged in /dev/shm and checked at its sha256. It removed that copy at exit.
  - iris's m3246 row was printed first.
  - The connect's own copy is `cluster/prr_read.sh`, byte for byte the approved script; its done file is `0`.
- **Preconditions and the log** (lines of `cluster/connect-read.log.txt`):
  - `squeue --me` (lines 4-6) lists only the two ll5d_gate jobs; no prr_* job.
  - prr_ibu attempt 3 is COMPLETED (line 7).
  - The five DONE receipts (lines 8-12): dry 15 of 15, iter 44 of 44, cap 29 of 29, misc 93 of 93, ibu rc 0.
- **The deploy** at `$OUT/deploy-read`:
  - HEAD cb13a644, with 0 porcelain --ignored lines before (line 13) and after (line 39);
  - the six FD-PRR files OK (lines 14-19);
  - the declaration and addendums A1 to A4 at their bound sha256 (lines 20-24);
  - BINDING-1.md at origin/main 4ad8b858 at 634cded3… (line 25);
  - route 2's products OK against `log-ibu/SHA256SUMS` (lines 26-27).
- **The read** (lines 28-31). `prr_read.main(["--run", $OUT, "--repo", $D, "--out", $OUT/read])` ran under root_6_28's
  python 3.11.14 with -I -B, nice 19, ionice idle, every thread cap at 1 and PYTHONHASHSEED=0.
  - The call was wrapped in `ref_g1.read_guards(ref_g1.PROTECTED, ($D, $OUT), root=False)`, so a plain Python read
    under /pscratch or /global/cfs outside the deploy and `$OUT` would have been refused. None was.
  - prr_read checks its own committed inputs (`INPUT_PINS`, `prr_read.py:428`).
  - `$OUT/read/` holds exactly readout.json and readout.txt, at the sha256 above (lines 32-38). The connect ended rc 0
    at 23:35:49Z (lines 40-41).
- **The fetch.** scp of the two outputs and the connect's log, done file and script copy into a new empty directory.
  Each sha256 matches the log's. `clone-read.log` is empty.
- **Renames.** The two names git ignores carry ".txt" (`RENAMES.tsv`). Their contents are unchanged.

## The guard, checked locally first (`lane/guarded_fixture_read.py`, `lane/guarded-fixture-read.log.txt`)

The check ran at 0 node-h, in a clean clone at M_A4, on test_prr's planted EndToEnd fixture (the plants of
`../a2/fixture_read.py`). `ref_g1.PROTECTED` was widened over the fixture's temp root and the clone's parent.
- The guarded call printed `{"verdict": "COMPLETE"}`, rc 0.
- A control plain read outside the allowed roots was refused.
- Its readout.json (8781f633…) and readout.txt (6c920311…) are byte-identical to the same read without the guard
  (`../a2/fixture_read.py`).
