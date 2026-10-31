# Binding: 1B with 4A, stage 2, the derivation runs, gate D and the nominal control (2026-10-31)

**By** the paper-tighten lane, as director.

**Under** `DECISION-20261030-joseph-fund-1b-with-4a.md` (#540) and `FD-1B-BINDING.md` (#556).

**Binds** [`FD-1B-STAGE2-DECLARATION.md`](FD-1B-STAGE2-DECLARATION.md), merged in PR #585. Its file sha256 begins
`6a054423ddd61006`, and main after the merge is `b43d9f23`.

**AUTHORIZES:**
- L1–L5 as the declaration writes them, including the records PR;
- **job 2a-0** (1 node, 1:00, cap 1.00 node-h), then **job 2a** (3 nodes, 2:40, cap 8.00) after 2a-0's re-price check;
- then **2b** (cap 5.00) and **2c** (cap 9.00), each after its gate and a message to the director and his "go".

Stage 2 is capped at **23.00 node-h** in all. Every job uses QOS regular, `--exclusive --no-requeue`, CPU only, and
nothing goes to CFS.

**CANNOT AUTHORIZE:**
- any stage-3 job or coverage toy;
- the same-seed rerun of §5.1, which needs an amendment;
- a GPU or premium QOS;
- any change to the reported matrix, a claim or wording;
- a rerun or repair after a STOP.

## 1. What the director checked at the PR head `54e3647a`

- The declared modules, locally: `test_fd_1b` and `test_fd_f1`, **Ran 91 tests, OK**.
- `fd_1b_tasks.JOBS` has 2a-0 (1 node), 2a (3), 2b (2), 2c (3), 3i (3) and 3f (5) nodes. The submit lines come through
  the committed packer, with `--exclusive --no-requeue`.
- The independent review's dispositions on #585: 20 fixed, 1 moot and 1 needing no change, with the 2 blockers among
  the fixed.

## 2. Rulings

1. **The split of 2a is accepted** as ruled on 2026-10-31.
2. **The load-aware re-price trigger is accepted:** re-price if 2L + 9w > 7,680 s (0.8 × 2:40) or if RSS exceeds
   44,040,192 KiB. It is tighter than the first form. A re-price comes to the director before 2a is submitted.
3. **The watcher is removed, and the time limit is the enforced cap.** Cancelling at 1.25 × projection would have
   killed the very measurement 2a-0 exists for.
4. **The carried lateral reading, Δ_b ⊙ x_T/f,** and 4A carrying no verdict at the test arms are recorded as the
   stage-1 binding's intended reading.
5. **A failed job is a STOP,** reported unrepaired.
6. **The run pin is R,** the records branch's head cut from #585's merge M. `git diff --name-only M R` may list only L3's
   paths. The records PR merges on the director's review without a new binding.

## 3. Conditions

- Tell the director before each connect and each submission.
- Gate D's verdict, the re-price result and the nominal control's record come to the director as they land.

The steps may start once this record is on `main`.
