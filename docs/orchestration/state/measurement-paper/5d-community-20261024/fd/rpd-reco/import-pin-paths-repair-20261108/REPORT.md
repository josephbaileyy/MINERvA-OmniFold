# RPD-RECO: added and missing ROOT import pins

The [round-2/C3 audit](https://github.com/josephbaileyy/MINERvA-OmniFold/pull/848#issuecomment-6718925944) is **NO-GO at `dfd94296`** on two test-and-text blockers. It reproduced 226 tests, the 226-test control and 195 killed mutants, and found the production logic correct. Its R06 counterexample showed that the tests did not establish validation when an import adds a pin or never sets it. The prior verification counts remain historical evidence, not closure of this finding.

The repair is tested at `225d894939b2c02fab8946d12a35c1c038168d2e`. Production predicates are unchanged: PRODUCTION-AST-CHECK.json compares all eight production/instrument files with the audited baseline. The sole production-file edit corrects a comment's source range. The held lows R01, R12, R18 and R22, and the missing-dependency child's inheritance, are not repaired here.

## 848-R2-C1: exercise all pin-presence paths

The new test starts with all three pinned keys absent, matching the production pre-ROOT shape. A simulated ROOT import sets the three values, with one selected defect. For each key it covers:

| Case | Expected result |
| --- | --- |
| Absent before import, added with the wrong value | MAT_IMPORT_ENVIRONMENT; exact expected/observed values and added diff |
| Absent before import, never set | MAT_IMPORT_ENVIRONMENT; observed null, with no invented added/changed entry |
| Wrong before import and left unchanged | MAT_IMPORT_ENVIRONMENT; exact wrong value, despite an empty changed set |
| Absent before import, added with the correct value | PASS; all three added values and an empty invalid-pin map |

The three keys are CLING_STANDARD_PCH, CPPYY_API_PATH and CPPYY_NO_ROOT_FILTER, with expected values `none`, `none` and `1`. The twelve cases use the actual checked_prepared_mat path and root_import_record. They assert the complete added/removed/changed diff and unexpected map, as well as the named refusal and exact invalid-pin record. The prior changed-value and ROOTSYS cases remain.

REQUIRED_IMPORT_PIN_CHANGED_ONLY reproduces audit R06 by appending `key in diff["changed"]` to the invalid-value predicate. The harness requires exactly one mutated AST site. This mutant must be killed by the added/missing/unchanged cases; the full suite also retains all earlier 195 required mutants.

## 848-R2-C2: correct raw-file line numbers

The pinned ROOT v6-28-12 Python file still has SHA-256 `871cfb70674a74f6b10a1352e2563734c6e95221d4ced0c6780ddb9abd5ca7eb`. Counting raw-file lines from one gives assignments at **14, 17 and 20**. The correct citation is [ROOT/__init__.py:14–20](https://github.com/root-project/root/blob/v6-28-12/bindings/pyroot/pythonizations/python/ROOT/__init__.py#L14-L20).

The custody code comment, the prior REPORT's source table and ROOT-SOURCE-IDENTITIES.json now use that range. The prior packet's SHA256SUMS is rebuilt for the corrected text/line metadata; its historical runner transcripts and source-at-issue identities are preserved. This packet carries the corrected source identity and fresh exact-head source bindings.

## Local verification and next gate

The suite printed **238 passed in 162.50s**, the full comment-only custody control printed **238 passed in 163.10s**, and the harness printed **196 required, 196 executed, 196 killed, complete/all_killed true**. All returned 0; every mutant pytest returned 1 through test failure with no collection errors. Formatting, lint, strict production typing and both shell syntax checks passed. The source commit passed 21 repository checks. Before/after source hashes were identical throughout verification. The raw report's credential-value/fingerprint scan passed.

Owner: Codex2 for this bounded repair and local verification; independent reviewer: coverage-5b-audit; native executor: limitation-resolver. The decision is whether the two requested blockers are closed. Terminal condition: committed exact-head receipts and the delta audit; review budget: this repair and concrete findings. No native-read, import, launch, exclusion, C3 custody, scientific, RNG, pricing or resource predicate changes are made.

After audit GO, the authorized native lane repeats the data-free prologue, which must pass the environment guard and reach the classifier. The real MnvH1D and full flux-connect gates remain separate. The production config remains DRAFT. This authoring lane made no cluster contact or production run.
