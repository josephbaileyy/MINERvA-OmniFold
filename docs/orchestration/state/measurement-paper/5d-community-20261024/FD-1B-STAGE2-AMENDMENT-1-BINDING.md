# Binding: 1B stage 2, amendment 1, the quarantine, job 2a-r and the charged ceiling (2026-10-31)

**By** the paper-tighten lane, as director.

**Under** `FD-1B-STAGE2-BINDING.md` (#587). A failed job is a STOP, and a rerun needs an amendment. 2a's STOP was the
half-MC truth guard, fixed in #602.

**Binds** [`FD-1B-STAGE2-AMENDMENT-1.md`](FD-1B-STAGE2-AMENDMENT-1.md), merged in PR #608. Its file sha256 begins
`f42eeab29f3326b7`, and main after the merge is `833288c4`.

**AUTHORIZES:**
- steps A1–A6 as written;
- the quarantine `mv` of the two pre-fix half pilots, `fd1b_pilot_half_s2600000.npz` (d7b6d020…) and `…s2600004.npz`
  (a19f14db…), into `$B/quarantine/`, with their sha256 checked after the move. They are not deleted;
- **job 2a-r**, once: 1 node, 1:00, cap 1.00, 12 unfolds (8 half pilots, then 2p2h_0, 2p2h_1, 2p2h_2 and AGKYxF1pi_0);
- then gate 2 from the fixed code.

**CANNOT AUTHORIZE:** 2b or 2c without their gates and the director's go; any stage-3 job; deleting a product; a rerun
after a STOP.

## 1. What the director checked at the PR head `eb715d8b`

- `test_fd_1b` and `test_fd_f1`, locally: **Ran 101 tests, OK**.
- `fd_1b_tasks.JOBS` has `2a-r`, and `CHARGED_NODE_S` holds 2a-0's and 2a's ledgered charges: 834 s, and 6,022, 6,046
  and 6,037 s.
- The mutation receipt: 8 of 8 killed. A07 restores the cap-sum reading and is caught.

## 2. Rulings

1. **The ceiling rule changes from the stage-2 binding's sum of caps.** An ended job counts at its ledgered charge,
   NNodes × Elapsed, held to the committed `LEDGER.psv` by a test. An unended job counts at its cap.
   - Stage 2 is 0.232 + 5.029 + 1.00 + 5.00 + 9.00 = 20.26 node-h, within 23.00.
   - A charge above its cap refuses, and an ended job is never resubmitted.
2. **12 unfolds, not 10,** so the 8-toy half set is one code. The pre-fix pair is quarantined, not deleted.
3. **Gate 2 runs from the fixed code** (`$SC2`/`$TK2`). 2b and 2c stay as bound, scored by the fixed scorer.
4. **The stage-2 report states the half-MC defect as found in the field:** why no fixture caught it, and that both
   reviews missed it.

Tell the director before each connect and before submitting 2a-r. The steps may start once this record is on `main`.
