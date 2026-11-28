# COVFIX PG seal and ledger: dispositions of codex-school2's round-6 confirm read (cov2d, after round 6)

The confirm read of b9642de9 -> 8e699eb3 (`REPORT.md`, codex-school2, gpt-6.2-sol at high effort, 101,208 tokens)
returned NO-GO on one item it ranked "Major". It found seven folded rows FIXED and one PARTIAL. It found both
deferrals and FOLLOWUPS item 3 consistent with the director's scope rule. Round 6 was the last round. Under the
director's ruling of 2026-11-27, only a finding that could change a published number or a gate's acceptance, or
falsely STOP a correct run, blocks.

<!-- absence-ok: each row states what this lane's own code does, as the read found it, not a claim that a result does not exist -->
| the read's finding | disposition |
|---|---|
| Rows 1, 3, 4, 6, 8, 9 and 10 FIXED | Nothing to do. |
| Row 5 PARTIAL: an error while walking W, as opposed to reading one file, still drops the hashes the trap had already collected; the reader's non-blocking item 1 adds that a scratch sums file can then be left behind | PG refuses that run either way (fail-closed). The director ruled it non-blocking (2026-11-28): `../../FOLLOWUPS.md` item 5. |
| Deferrals 2 and 7, and FOLLOWUPS item 3: consistent with the scope rule | Nothing to do. |
| "Major": gpgconf is verified at gpg_run's entry and cleanup runs that verified path, so a gpgconf replaced on disk during the final gpg call runs at cleanup and PG issues its receipt (round 5's cleanup-time verify refused) | The director ruled it non-blocking on 2026-11-28, not a fold: the replaced gpgconf only shuts down the agent on a throwaway home after gpg has written the ciphertext; PV checks the sealed bytes with its own pinned gpg, so no product or number depends on it; a lasting replacement is refused at the next gpg_run's entry. His condition: the record must not claim more than the code does. The README's pin-gate section now states the window in plain words. No text claimed that every exec is verified at exec time: covfix_seal.py's Tools docstring already says each binary is hashed at construction and at the start of every gpg_run, and discloses the window after the hash. `../../FOLLOWUPS.md` item 4. |
| Non-blocking 2: the PG mutation receipt gives two start times | Both are right and mean different things. Line 3 is the run's start, `Fri Nov 27 21:22:02 UTC 2026`, written just before launch. The header line `# start: 2026-11-28T12:50:44Z` is the time receipts-r5.sh wrote the header, after the run had finished. The receipt stays as written (the director, 2026-11-28). |

**The window, in plain words** (as the director worded it): gpgconf is verified at gpg_run's entry, not at the
cleanup exec. A replacement during the final gpg call goes undetected in that run. Cleanup runs it on the throwaway
home only, and the next run's entry verify refuses it. The sealed bytes are checked by PV's own pinned gpg.

No code changed after the round-6 receipts: the receipted bytes at 8e699eb3 are the PG chain's final bytes.
