# The director's rulings during the F1 run, confirmed (2026-10-28)

**By** the paper-tighten lane, as director.

**Under** `FD-F1-BINDING.md` and its amendments 1 and 2 (PRs #429, #435, #445).

**Confirms** the five rulings that [`FD-F1-REPORT.md`](FD-F1-REPORT.md) §6 (PR #446) quotes as R1–R5. They were given by
message to the measurement session on 2026-10-28. The director compared §6 with the messages as sent, and the
quotations are faithful. This record is the rulings' authority, in place of the report's transcription.

- **R1:** the F1c deploy pin may fail `generate_manifest.py --check`, since the path rule governs the pin and the six
  gates govern main. The pin is a child of `5f5e392c` changing only `fd/receipts-f1/`. It is pushed on its own branch
  and merged with a merge commit. The deploy is at `$OUT/deploy/f1c`.
- **R2:** the pin commit holds back the two gen5d `*.meta.json` files and `config-f1.json`. Each is identified there by
  sha256, none is read by F1c, and their later committed bytes match.
- **R3:** `k1_p5_rerun.npz` (95,311 B) is committed with `git add -f` beside `config-f1.json`, its sha256 equal to the §8
  pin and the cluster original. The hook passes with no override. The director's checker-fix follow-up was withdrawn:
  the checker's receipt-local preference is policy, not a bug.
- **R4:** the F1c products are under `$OUT/f1c/closure/` and `$OUT/f1c/pe/` rather than `f1c/products/`. This is a path
  deviation, with no move after the fact, checked by a full `find` and a 42-name manifest.
- **R5:** the empty first launch did nothing, its 0-byte files are kept as evidence, and the real body ran only after
  its sha256 matched.

**One more ruling, on the review's M1.** `FD-F1-BINDING.md` §4.8 and the declaration's §5 require the grader's held-out
tally, while `FD-F1-BINDING.md` ruling 2 forbids counting the two truths as independent tests.
- The report keeps the tally, labelled "context only", beside per-record counts. It states the four records as two
  truths and their closures.
- That satisfies both, and it is accepted.

**The director's own check of the report's headline,** from the readout (`cbe411a9…`, unchanged between `eeff25b5` and
the merged head `7115dbfb`):
- recomputed with the deposit candidate's C_total + C_resp and each record's stored bias;
- the closures' χ² reproduce exactly: 11.440 for G18 and 16.050 for AR23;
- the ensembles agree to within the effect of a diagonal-only noise term: 11.805 against 11.836, and 16.685 against
  16.863;
- every largest |z| matches, at the same cell: 0.623 at R11, 0.608 at R11, 0.644 at R07 and 0.600 at R07.

## Not changed

- F1 is a bias test at two GENIE-family truths, not a coverage test. Its printed form goes through the paper lane's
  step (c), the PRD read and the truth column, then to Joseph.
- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.
