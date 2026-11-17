# Follow-up list while Ben reviews the paper and Supplement (opened 2026-11-16)

Items to look at during Ben's read. None blocks sending him the draft. Each needs its own decision before it changes
the paper. Source: `DECISION-20261116-joseph-paper-batch.md` item 44, and the director's carried lows.

| # | item | why | owner | state |
|---|---|---|---|---|
| 1 | Fig. 3 as a heatmap of the recovered fraction (or bias) over (E_avail, W), beside or instead of the 42-cell sequence | the online review: the flattened axis hides the pattern | director → helper-3 / cov2d (figure producer and re-pin) | open (Joseph, item 44) |
| 2 | The note figure MEFHC_5iter_pull_full.pdf prints "rms = 0.54", which is a standard deviation | item 16's relabel. A redraw needs a login-node identity run, and the change to compare_to_paper_fullcov.py touches pinned receipts | director | open |
| 3 | `re2-integration/check_ledger.py` full mode crashes on the missing result_status_rows.tex | predates the batch (57147f2b8, 10-28); --figures passes | helper-3 | **crash fixed** on prep/after-ben-20261117 (2026-11-17): RETIRED_FILES declares the deleted file, and its row W7-t1 is reported RETIRED. Full mode now runs and shows **134 stale rows**: the RE-2 ledger of 10-31 against today's text. The self-test fails for the same reason. Retire the ledger or re-pin it: a decision for the director |
| 4 | The paper's pointers into the note: NOTE_RELEASE_REV moves again after the note cutdown, with the object check | the cutdown renumbers the note | helper-3 | **done** on prep/after-ben-20261117 (2026-11-17): NOTE_RELEASE_REV moved 8342963c1 -> 87cee1c86. Of the 49 cited labels, only N-sec:cov1b-gate changed number (B.6 -> B.5, same title and text). Three titles changed "measurement" to "result". The hold's search terms gave the same counts. The cover sheet is updated |
| 5 | RDX lows: r1, r2, p1–p4 | binding addenda J3 and J4 | tier3-design | open |
