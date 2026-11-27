# #1308 reads and dispositions

**agy (gemini-4-hydrogen-high), on #1308's code at aafa9e6e.** Ran 2026-11-24, 13:52–13:55 local. The verdict is
**GO**, with five findings, all NON-BLOCKING and none BLOCKING. The prompt, model and report are in `agy/`; the report's
sha256 is `30d21829b90e514f0b8504928250ec624edafb769f77fd3edd90124bb9c1978c`. The head is now ebef89c5. That commit
only merges main d71d3f35; no file under `nd-unfolding/` changed, so the read applies unchanged.

The read covers the director's focus: C-JOIN part 1 (`true_energies`, `spot_rows`), C-JOIN part 2
(`omnifile_spot_check`, its placement as the first use of flux4's output in `p0`, and spot rows read from flux4's
record), and the C-E controls reading the product's `energy`. It found the C-E gates (`CE1_MIN`, `CE3_MEDIAN`,
`CE3_Q99`) unchanged.

Dispositions of the two concrete points in its findings:
1. **`identities = np.array(identities)` (`fd_rpd_reco.py` near `:2231`) copies the ~1.05 GB `mc_id` array once,
   briefly.** Accepted as is. This is memory on a login step that the price already covers, not a correctness
   issue. A follow-up could avoid the copy.
2. **A malformed `meta["playlists"]` or a non-numeric spot list would raise `TypeError`, not `Refused`.** Accepted as
   fail-closed. `main()` catches `Refused`, `OSError`, `ValueError`, `KeyError` and `ImportError` (`fd_rpd_reco.py`
   near `:3562`). A `TypeError` ends the step with a traceback and a nonzero exit, writing no `<step>.json`, so the
   next step refuses. What is lost is the `<step>.STOP.json` receipt for that case. A follow-up could add `TypeError`
   to the caught tuple, with a test and a mutant.

**codex-school2:** did not run. Its directory is empty: it was queued behind COVFIX on 11-24 and then ran out of
quota. The director ruled on 2026-11-26 that one Gemini read is the read for #1308.
