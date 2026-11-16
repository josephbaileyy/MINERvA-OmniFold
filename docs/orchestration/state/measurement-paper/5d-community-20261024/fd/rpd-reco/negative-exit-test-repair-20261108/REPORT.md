# RPD-RECO R4-C1: negative-check after-exit custody coverage

The [audit addendum](https://github.com/josephbaileyy/MINERvA-OmniFold/pull/848#issuecomment-6726147013) is **NO-GO at `e9d57527` on one test-only blocker**, 848-R4-C1. C1's implementation is correct and independently closed; the addendum found that replacing the negative-check path's shared after-exit checker with bare path classification passed all 288 tests. This packet closes that coverage gap without changing production.

The repair is tested at `4fb2add1871c95b203e7ec0a3ff38f1424d281c8`. PRODUCTION-BYTE-CHECK.json verifies all eight producer, custody/prologue, reused instrument, shell and real-class-check files byte-for-byte against `e9d57527`. Only the contract tests and mutation harness change. The separately held Y07/Y25, execve and pymon-source lows are not repaired here.

## Drive the actual negative-check path

The two cases call the real `missing_dependency_check`, using its digest-pinned, owner-only prepare/reference mechanism and its real policy staging. The fixture's child launch alone is substituted: it checks the staged dependency was withheld, writes the expected MAT_DATA_STAGE refusal and supplies a trace containing one successful open of a suffixless ELF under a declared platform root. The staged dependency is restored before the custody check, as production requires.

Bare `classify_trace` is asserted to PASS the same input in both cases. Thus the unpinned case can refuse only through the shared after-exit library inspection:

| Case | Required result |
| --- | --- |
| Unpinned suffixless ELF | Custody refusal; public `missing-dependency-trace.STOP.json`; exact library class, reason, path/resolved path, PID and raw line; policy and trace digests; prepared null and observed stat; no fingerprint map; no PASS receipt |
| Pinned counterpart | PASS with the exact observed library pin in the trace check; expected MAT_DATA_STAGE receipt retained; no trace STOP |

Both cases verify that the child path was reached exactly once, the clone cwd was passed, and the withheld staged file is restored with its bytes and no holding file left behind. The unpinned case also compares the complete exported violations with the propagated exception's values, so an unrelated early refusal or an unwritten STOP cannot satisfy it.

## Required mutant and exact-head evidence

REQUIRED_NEGATIVE_AFTER_EXIT_CHECK reproduces Y30 at [fd_rpd_reco_custody.py:1703 @ 0fbbbf84](https://github.com/josephbaileyy/MINERvA-OmniFold/blob/0fbbbf8448f16e9e18741a330e1dd9d8cb35f88b/nd-unfolding/fd_rpd_reco_custody.py#L1703). It replaces exactly the one `classify_trace_with_stop(...)` call inside `missing_dependency_check` with `classify_trace(trace.read_text().splitlines(), trace_policy)`. The mutation bypasses both the after-exit check and the public trace STOP writer. Its required selector is the new unpinned negative-path case, which must be killed by that bypass.

The suite printed **290 passed in 272.73s**. The full comment-only custody control printed **290 passed in 311.14s**. The harness printed **229 required, 229 executed, 229 killed, complete/all_killed true**, preserving all prior 228 required mutants. All runners returned 0; every mutant pytest returned 1 through test failure, without collection errors. Formatting, lint, strict production typing and shell syntax checks passed. All before/after source hashes match throughout the completed runs, and the source commit passed 21 repository checks.

Verification is serial under the producer's five existing thread settings, set to `1` before NumPy imports. Assertions, selectors and timeout limits retain their definitions. The runner's stdout/stderr are unmodified. MUTATIONS.json carries reversible receipt annotations only; VERIFICATION and SOURCE-IDENTITIES bind the exact source and raw report.

## Boundaries and next gate

Owner: Codex2 for this bounded test repair; independent reviewer: coverage-5b-audit; native executor: limitation-resolver. The decision is whether the negative path's existing after-exit refusal and public STOP are now enforced by tests. Terminal condition: exact-head receipts and delta audit; review budget: this finding and separately identified concrete addenda. No production source, scientific, environment, monitoring, C3, RNG, resource, input or output policy changes occur.

The production template stays DRAFT. No cluster contact or production run occurred. Native prologue rerun 5 and the real-MnvH1D/full-connect gates remain pending the director's releases after GO. Private canonical prepare retention and its deletion-ledger rule remain unchanged.
