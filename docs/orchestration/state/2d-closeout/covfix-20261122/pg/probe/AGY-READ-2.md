# PG probe rev 2: agy read 2 and its dispositions

agy (Gemini 3.8 Flash (High), `--sandbox`) did a sandboxed, read-only read of copies of these files:
- `pg-probe.py`, `pg-probe-launch.py`, `test_pg_probe.py`, `mutants.py`;
- `LINE-TRACE.md`, `CODEX2-READ-1.md`;
- §4.1–§4.2 of the declaration.

Its input files' sha256 were unchanged after the read. It judged codex-school2's 8 blocking items fixed, except a gap in item 3 that it raised as finding 1. The findings are restated below by the PG session, which also owns each disposition.

| # | finding, restated | disposition |
|---|---|---|
| 1 | a confirmed-absent 02b whose GENIE configuration does not resolve leaves the 02a premise unchecked (`same_02` is None), and 02a would be chosen | **Fixed.** The fallback now needs `same_02 is True`; an unresolved 02b configuration makes 02a not eligible, a STOP. `test_fallback_with_unresolved_02b_config_is_not_chosen`; mutant "02a fallback with an unchecked premise" |
| 2 | the "wrong passphrase accepted" test still exits 2 | **Fixed.** That test became `test_a_wrong_passphrase_refused_without_evidence_fails`. A new `test_a_wrong_passphrase_accepted_fails` has the fake exit 0 |
| 3 | repo-relative paths break the tests when run from a copy | **Partly.** `mutants.py` now honours `PG_REPO_ROOT`, as the tests already did. The constant checks read the repo's own F1 and declaration files on purpose, so they are not skipped |
| 4 | mode 700 is recorded, not required | **Fixed.** It is part of `pass`. `test_mode_700_is_required`; mutant "mode not required" |
| 5 | with a low standard fd closed, the pipe's write end can land on fd 3 and be clobbered | **Fixed.** `gpg_check` first reopens any closed fd 0–2 on `/dev/null`, and records it in `std_fds_reopened`. `test_a_closed_stdin_is_reopened`; mutant "closed standard fds not reopened" |
