<!-- codex-school2 (gpt-6.2-sol, high), the round-6 confirm read of b9642de9 -> 8e699eb3, run 2026-11-28 13:31:56-13:35:05Z,
rc 0, 101,208 tokens. Verbatim; its links are relative to the read's input directory (code/, receipts/). -->
<!-- absence-ok: verbatim third-party read report; the reader's findings about this lane's code, not claims that a result does not exist -->
**NO-GO**

- **1 — FIXED.** The ledger splits scripts only at LF and rejects embedded separators in directive lines before claiming the reservation. [covfix_ledger.py:393](code/covfix_ledger.py:393)
- **2 — Deferral consistent.** An older policy followed by a torn append still refuses. Only the diagnostic differs. [covfix_ledger.py:216](code/covfix_ledger.py:216)
- **3 — FIXED.** A `comm` truncated mid-UTF-8 is escaped, so the cgroup check still produces its refusal inventory. [covfix_pg.py:206](code/covfix_pg.py:206)
- **4 — FIXED.** Both binaries are verified on every `gpg_run` call before the SIGTERM hold. Cleanup uses the path verified at entry. [covfix_seal.py:199](code/covfix_seal.py:199)
- **5 — PARTIAL.** A file-read error is counted, the inventory is reduced to its count, and the scratch scan runs. An error during traversal can still discard hashes already collected. [covfix_pg.py:354](code/covfix_pg.py:354), [covfix_pg.py:468](code/covfix_pg.py:468), [covfix_pg.py:545](code/covfix_pg.py:545)
- **6 — FIXED.** The JSON parser rejects duplicate keys at every object depth in the same bytes that were hashed. [covfix_pg.py:124](code/covfix_pg.py:124), [covfix_pg.py:135](code/covfix_pg.py:135)
- **7 — Deferral consistent.** The mutable manifest maps have no PG publication caller. The affected gate belongs to PV. [covfix_seal.py:519](code/covfix_seal.py:519), [covfix_seal.py:595](code/covfix_seal.py:595)
- **8 — FIXED.** A verified allowlisted digest is exempt from seed and digit-run scans when it occupies a whole 64-hex token. Text outside those tokens remains scanned. [covfix_seal.py:629](code/covfix_seal.py:629)
- **9 — FIXED.** The spec rejects `SCRATCH` in both environment lists, and the parent still uses it to locate the spill scan. [covfix_pg.py:153](code/covfix_pg.py:153), [covfix_pg.py:267](code/covfix_pg.py:267)
- **10 — FIXED.** The docstring cites rev 12 §4.2 and describes the wrapper’s exclusive `salloc` node. [covfix_pg.py:1](code/covfix_pg.py:1), [covfix_pg.py:30](code/covfix_pg.py:30)
- **FOLLOWUPS 3 — Classification consistent.** The walk-error fallback runs after PG has already failed and still attempts the scratch scan. [covfix_pg.py:543](code/covfix_pg.py:543)

### Blocking defects

- **Major — A lasting `gpgconf` update can pass PG’s pin gate.** If a site package update replaces `gpgconf` with a compatible build during the final manifest decrypt, round 6 executes the replacement at cleanup. Successful cleanup lets PG issue a receipt because there is no later pin check. An in-memory simulation reproduced seal success in round 6 and refusal in round 5. [covfix_seal.py:199](code/covfix_seal.py:199), [covfix_seal.py:257](code/covfix_seal.py:257), [covfix_seal.py:367](code/covfix_seal.py:367)

### non-blocking

- A mid-walk error can leave a scratch sums file behind. If the trap hashes a readable file and then reaches an inaccessible directory, it loses the digest it needs to identify the spill. PG still refuses. [covfix_pg.py:358](code/covfix_pg.py:358), [covfix_pg.py:545](code/covfix_pg.py:545)
- All six receipt headers match the supplied file hashes. The PG mutation receipt gives two different start times for its reported run. [PG mutation receipt:3](receipts/pg/mutation.txt:3), [PG mutation receipt:12](receipts/pg/mutation.txt:12)