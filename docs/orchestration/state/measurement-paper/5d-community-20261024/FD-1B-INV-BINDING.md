# BINDING: the 1B gate-D investigation (director, 2026-11-01)

**Binds** [`FD-1B-INV-DECLARATION.md`](FD-1B-INV-DECLARATION.md) (revision 2), with `nd-unfolding/fd_1b_inv.py` and
`nd-unfolding/tests/test_fd_1b_inv.py`, as merged in PR #641 at **M = `b1c615f12fca5f8597d34750b2c074f1fd7b2cdd`** (PR head
`0e4cc38e4a614005d56b55be8aaa9a47ada025a6`).

**Under** `DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md` (#640), item 1 (1B reopened as an
investigation of gate D's mismatch) and item 2 (compute).

## What the director checked

- **The review.** coverage-5b-audit reviewed the declaration (B1, B2, M1–M4 and minors), then the code at
  `26f9cf01`, then the N1, N2, N4 and N6 fixes at `0e4cc38e` (its delta check is posted on the PR). All blocking findings are fixed. N3 is a
  requirement on I1's amendment. N5 (a runtime audit hook) was optional and is not done.
- **The tests.** At `0e4cc38e`, `tests/test_fd_1b_inv.py`, `test_fd_1b.py` and `test_fd_1b_diag.py` ran locally
  (`python3 -B -m pytest`, own TMPDIR): 127 passed. The mutation receipt (`fd/receipts-1b/inv/mutation.out`) kills 27
  of 27, and it names the committed code's digests.
- **Nothing read or connected.** Before this binding, the lane has opened no product and made no connect.

## Rulings

1. **The steps, their order and their caps are bound.**
   - I0 runs on login37 at 0 node-h.
   - I1 (cap 4.0) runs only if I0 reads any cell SUPPORTED or OPEN, and only after its own amendment is bound. That
     amendment holds the jitter code and argv, and it defines I1's verdict over all 11 cells (N3).
   - I2-0 (cap 1.0), then the I2 bulk (cap 14.0), run unless I1 reads SUPPORTED in every cell. The bulk is submitted
     only after `fd_1b_inv.py walls` reads PASS. A REPRICE is an amendment.
   - The caps total 19.0 node-h. Nodes × elapsed is reported per step.
2. **Rule H2 as revised is bound** (§4, §5): noise-consistency on both sides at 4× each side's floor, the point and
   upper floors, the three-way reading per failing cell, and I1 before any O3.
3. **The I0 fallback is bound** (§4). With the receipt's triangle-bound floor, a cell that would read SUPPORTED reads
   OPEN, and REJECTED stands.
4. **Rule I2 and its outcome map are bound** (§6), with three conditions:
   - (a) **F_prior → H1 → O1.** An O1 under H1 means gate D compared unlike objects. It does not validate S1's
     interaction block, and the report must not read that way. The report names, as a question for Joseph, whether
     the reported intervals should carry var(r) and leave the prior part to C_model. It prints B beside M in the data's
     frame, and it does not answer that question.
   - (b) **F_truth (surviving over S1-resolved bands) → H3 → O1.** The report states that a truth-dependent block is
     expected in kind. The finding is its size beyond the carry.
   - (c) **F_src → H4 → O2.** An O2 headline authorizes nothing by itself. Any change to the reported covariance
     comes to Joseph as a priced proposal, because it changes every σ and χ² in the paper.
   - The account and refute levels (at least 8 of 15 to account, 3 or fewer to refute) are bound, read per mechanism
     and never pooled.
5. **No outcome authorizes new toys, a change to gate D, the window or M_d, or a coverage ensemble.** Each needs its
   own declaration and binding.
6. **The read scheme is bound** (§8):
   - `O_NOATIME` everywhere this lane reads pscratch, with staged copies for I0;
   - EPERM raised, never retried with a plain read;
   - the atime sidecar, with a non-zero exit if an atime moves;
   - a moved atime is reported as a deviation, unprompted, and not restored.
7. **The connects are authorized.**
   - **First:** `stat` of every input named in §4 and §8, and an `iris` balance read, before anything runs. A missing
     or exposed input is reported to the director with the fallback that applies, before any step.
   - **Jobs:** I0 on a login node, `nice -n 19`. Jobs for I2-0 and the bulk use `-A m3246 -q regular -C cpu --exclusive
     --no-requeue` through the committed packer, from a fresh clone detached at M with empty porcelain.
   - **Not allowed:** CFS writes, GPU, premium QOS, any limit of 12 h or more, and edits to any existing checkout.
   - **HPSS:** `$V = $P/fd-1b-inv-20261101` gets an HPSS copy at each step's end, verified.
8. **The reports.** Each step's report gives its readouts, its rule's per-cell reading, the outcome it supports, its
   cost measured, and any deviation. A report proposes no repair beyond naming the outcome.

## Fixed, unchanged

Gate D's verdict and readout (`e1838c0a…`), the diagnosis's NOT LOCALIZED (#634), the [0.9, 1.1] window, the tested
matrix C_total + C_resp without the run-period block, and the paper's two 1B disclosures, which stay true until a report
changes what they can say. Nothing is submitted, deposited or tagged.
