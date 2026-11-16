# BINDING 1: V-HALF, the per-cell bias-half validity rule (director, 2026-11-09)

**Binds** [`DECLARATION.md`](DECLARATION.md) and its code, as merged in PR #992 (`cd8e16fe`) and its follow-up PR #995
at **M_VH = `ae0ec71400c50ed9c23308891852e9e06db48c18`**. The audited heads are `fd0ed5f1` (#992) and `f65e2a07`
(#995, a delta audit against `cd8e16fe`); every file below is identical at `f65e2a07` and M_VH.

| file | sha256 (prefix) |
|---|---|
| `DECLARATION.md` | `594851a2a83256dc` |
| `v_half.py` | `8a1cdbe7da7d8af4` |
| `test_v_half.py` | `d2d28b9f38f422c9` |
| `mutate_v_half.py` | `09a10bc79152f198` |
| `mutants.txt` | `36696b3920deed16` |
| `INPUTS.sha256` (H1) | `7ee797131963da0e` |
| `nd-unfolding/pv-ladder/readouts/h2_definition.json` (the cell definition; see ruling 4) | `b67907615fe2e903` |

**Under:** `DECISION-20261109-joseph-bias-half-rule.md` (the rule, items 1–4; item 5 left to Joseph), FD-PRR BINDING 1
addenda A2 (the readout emits d) and A3 (M_A3 = `06657cff`).

## What the director checked

- coverage-5b-audit's GO on #992 at `fd0ed5f1`, with no blockers
  (https://github.com/josephbaileyy/MINERvA-OmniFold/pull/992#issuecomment-6747215128):
  - the rule matches the decision's items 1–3: the 1 % floor (inclusive, two-sided); exactly the 12 graded truths, in
    §3's order, from the real H1; GiBUU's exclusion print-only; "the rule applies at no truth" never valid; the
    unresolved class the K = 2 noise band; σ_m checked by finite difference for every sign of r and d;
  - the H2 keys are exactly those `prr_read.py` writes at `cf76aec7` (:282-285, :449-450);
  - the decision's licence list is carried word for word in §10 and in LICENCE;
  - item 5 is left to Joseph.
- coverage-5b-audit's delta GO on #995 at `f65e2a07`, with no blockers
  (https://github.com/josephbaileyy/MINERvA-OmniFold/pull/995#issuecomment-6747660660):
  - `v_half.py`'s diff from `ce07a6f0` is exactly C-PRR's length-16 check on d, b and r, and LICENCE carrying §10 in
    full;
  - 37 tests pass; 41 of 41 mutants are killed, the rerun byte-identical to `mutants.txt`; against `ce07a6f0`, exactly
    the two new code tests fail; the read without `PRR-READOUT.sha256` exits 4 with no output directory;
  - the two #992 survivors (the sgn(d) and |r| terms of the d-derivative) are now killed.
- The director ran `test_v_half.py` from a `git archive` of M_VH (`PYTHONHASHSEED=0`, own TMPDIR): 37 passed.

## Rulings

1. **V-HALF is bound at M_VH.** The read runs only after an addendum to this binding commits `PRR-READOUT.sha256`,
   naming H2 by path and sha256: the committed `readout.json` of the FD-PRR read made from M_A3's `prr_read.py`, after
   prr_ibu has completed. The code does not constrain that path, so the addendum is the control. No other readout may be
   named.
2. **The read is local, at 0 node-h,** by the valid-region lane, from a fresh clone at M_VH (or the addendum's merge)
   with empty porcelain. Its output and receipts go in as a PR. The report gives each cell's class with its inputs and
   the print-only sections, as declared, and goes to the director, then to Joseph.
3. **The licences are the declaration's §10,** carried by LICENCE. In particular, V-HALF is NOT CITABLE FOR coverage, a
   measurement, the cause of any failure, V-HALF as ATLAS's or the advisor's exact rule, a failing cell as excluded,
   wrong or unreported, or any paper or note sentence without the PRD-referee read and Joseph.
4. **Cell order.** H2 carries no cell labels, so V-HALF cannot check the order of d, b and r; it checks their length
   (16). The order rests on `prr_read`'s M16, built from the same `h2_definition.json` as F0b's, pinned above. The read
   addendum re-checks that pin at the PRR read's commit.
5. **The advisor's consequence** (modifying the observable or binning if a cell fails) is not decided here. It comes to
   Joseph with the result (the decision's item 5).
6. The audit's held low (b's length check is not exercised by a test on its own; immaterial, since b = r(1+d) refuses
   any wrong-length b that V-HALF reads) is on the follow-up list.

Nothing is submitted, deposited or tagged.

## Binding 1, addendum R1: H2 named; the read may run (director, 2026-11-09)

**Names H2** (ruling 1): [`PRR-READOUT.sha256`](PRR-READOUT.sha256) is committed with one line, the FD-PRR read's
committed readout by path and sha256:

`9238f22bfe29685e33c1d5bb46da3938a3ebfdc93a54575a4fe99de3a7af9ead  docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-prr/read/cluster/readout.json`

**What the director checked:**
- The readout was made by `prr_read.py` at M_A4 `cb13a644` (FD-PRR BINDING 1 addendum A4, ruling 1; its bytes
  `d7c7c2c0…` are A2's). It ran from a fresh clone, verdict COMPLETE, after prr_ibu attempt 3 (61057142) completed with
  C-IBU true. The receipt is PR #1006, merged at `64ec2061`. The file on main hashes to `9238f22b…`, as the session
  recorded.
- **Ruling 4's re-check:** `nd-unfolding/pv-ladder/readouts/h2_definition.json` is `b67907615fe2e903…` at M_A4 and on
  main, the pin above, so prr_read's M16 and F0b's cell definition are the same file.
- No other readout is named, and none may be.

**Ruling:** the V-HALF read runs as ruling 2 states: local, at 0 node-h, from a fresh clone at this addendum's merge,
with empty porcelain. Its output and receipts go in as a PR, and the report goes to the director and then to Joseph.

Nothing is submitted, deposited or tagged.
