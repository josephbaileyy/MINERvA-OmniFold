# COVFIX P0, pre-W1 part: the run (cov2d, 2026-11-23)

Under COVFIX-BINDING-1 ruling 2, on the director's GO of 2026-11-23. Local, 0 node-h.

- **Code:** branch `cov2d/covfix-p0-20261123` at `f5b1ac9a2051519c6b07d05dfdbdcd64cd70395a`, in a clean worktree.
  - `covfix_core.py`: `851dca65542f3f01ddbb4c9df2f1c39118e9c74e54ccf0a7e588361a1cc176f2`
  - `covfix_p0.py`: `307a510de70b6c19b9cd6bf3b0c996a63654131233089623ba4f4d0c41ea7104`
  - The record's own `code_sha256` field carries both.
- **The code's chain:**
  - receipts in `../code-receipts/`: 95 tests OK; 100 % of lines and branches traced; 78/78 mutants killed;
  - reads in `../reads/`: codex-school2 round 4 GO, agy round 4 GO, and the fresh-eyes agy pass GO.
- **Step 1, the production pin audit** (`pins-audit.txt`): `test_covfix_p0_pins.py`, rc 0. It reads only hashes.
- **Step 2, the run:** `env.txt` holds the command. It ran from 21:11:37Z to 21:11:39Z (`start_utc.txt`, `end_utc.txt`),
  with rc 0 (`rc.txt`) and empty stderr. `stdout.txt` reads `{"status": "done (pre-W1 part)"}`.
- **The record:** `p0.json`, written by exclusive creation. The sha256 of every file here is in `SHA256SUMS.txt`.
- **Inputs:** every input was checked by sha256 at load, from the same bytes that were parsed:
  - Q_rep `ff66b91d…`, a laptop copy;
  - G2R blocks G18 `55ad7cc4…` and AR23 `c060cb40…`, laptop copies whose shas are listed in
    `receipts-cov2d/g2r/readout/<T>/README.md:32`;
  - the committed E_<T>, blocks_<T> and score_<T>, `cmodel_2d.json` and IBUKT A2's `readout.json`, pinned in
    `covfix_p0.PINS`.
  - The record's `inputs` section lists every path and sha.
- **Scope:** the readings that need §3.1's second carry vector, round(λ⁺), are marked "pending W1".

**CITABLE FOR:** what P0's pre-W1 part computed from the committed spent records.
**NOT CITABLE FOR:** any validation (§3.1: "These validate nothing"), any coverage statement, any note wording.
