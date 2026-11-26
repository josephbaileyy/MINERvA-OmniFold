# (b) part 1: the frozen selection of R00–R15 (receipt; tier3-design, 2026-11-24)

**Result** (accepted by the director, 2026-11-24): **13 measured**, 5 of them discriminating, and **3 exploratory**
(R03, R07, R11).
- **The frozen measured set, k = 13:** R00, R01, R02, R04, R05, R06, R08, R09, R10, R12, R13, R14, R15.
- **Discriminating** (measured and max U ≤ 0.5·S_g): R00, R04, R05, R09, R14.
- **The labels are frozen.** Nothing reruns the selection without a declared amendment (the director's ruling). They
  were sent to cov2d for rev 12 §4.5's simulation.

**The rule:** `B-SEL-DECLARATION.md` rev 1, sha256 `04debd573c7b6a0ad57feb61266384515d4ca2b597d0047cf80aeea303faf8db`,
bound by `BSEL-BINDING-1.md` (#1311, merge `71162ed94d28ce4670ad0f5ea1e4ae658bab1926`).
- The estimator is E_R / B0, frozen after S2R failed.
- κ = 1 on U = |β| + 1.96·SE in Tune v1 units, at the worst of 14 spent truths; a cell that flips across row 4's 80
  split replacements is exploratory.
- Simulation only: no seal, no sealed output, no data. The rule was introduced after the data were seen, and that is
  disclosed.

BSEL-BINDING-1 ruling 2's "nice" is a wording error by the director; the bound read script has none (director's
message, 2026-11-24).

## The record (`record/`)

- `selection.json` sha256 `4d4205d4cb5e5b98a9aacc18e792a074dfbfa7f8aa05cb11f7f8bfb35d44c634`.
- `selection.txt` sha256 `fc046e4ddd987e32313a05547fc54ea54396ed01f93e65b7ecee9ef8f3901d63`.
- Both came from `nd-unfolding/bsel/bsel_select.py` (sha256 `251d2d8bf52af337094614d275d430759bf6460271e28f297139b9c724cdf638`),
  run locally on the fetched copies. A rerun reproduced both byte for byte.
- **Controls passed:**
  - C-PIN: the 5 committed inputs and the 6 fetched copies;
  - C-TAB: the tables reproduce the readouts' bias and noise_sigma to 1e-12 for all 14 truths, and closure_nuwro's
    product reproduces r with N = 0;
  - C-R: R > 0, and R = 1 exactly at nominal and A7_mnvtune;
  - C-SG;
  - C-SPLIT;
  - C-LEAK: no absolute value in the record.
- **Cross-check:** S_g's minimum (2.09%, R01), its maximum (20.35%, R02) and S_g⁺'s maximum (42.51%, R02) equal the
  figures in Joseph's spec (B-SPEC-DRAFT.md §1).

**Disclosure: one code fix before any output.**
- The first run STOPped at C-SG. The code had required GiBUU's prediction to have 16 cells, while gencmp-e's readout
  gives its 8 supported cells.
- The fix maps those values onto R00–R03 and R08–R11, and STOPs unless the readout's cell list is exactly those eight.
  That is the declaration's §2 and §4 as written.
- No reading had been computed. The declaration is unchanged. The director ruled the fix within §2 and §4.

**Checks** (`record/checks/`):
- `tests.txt`: test_bsel.py, 31 OK.
- `line-trace.txt`: 199/204 statement lines hit. The 5 unhit are docstrings and the `__main__` exit.
- `mutants.txt`: 20 of 20 hand mutants killed (`mutants.py`).

## The read (`run-20261124/`)

- **On the director's GO,** with the bound launcher `bsel_launch.sh` a0fc824f and read `bsel_read.sh` 199cc946, taken
  from 71162ed9.
- **Acks** (each UTC time from the peer's `date -u`): limitation-resolver 21:58:12Z, cov2d 21:58:19Z, director-helper-3
  21:59:07Z (IBUB 61924744).
  - The window ended at 22:13:12Z: the oldest ack + 900 s, computed with date (`lane/wend.txt`).
  - limitation-resolver was told right before the connect, and all three got END messages after it.
- **login38, 21:59:28Z to 21:59:56Z.** The node staged sha256 199cc946…, with ssh rc 0, script rc 0 and done 0. The
  fence (sacct) was clear.
- **All six sources** were present on pscratch, so none had been purged. Each pin read, each pinned copy, and each
  stat (size, mtime, atime, inode) checked true (`session/connect-bsel.log.txt`).
- **The tar:** `fetch-bsel.tar` sha256 `f6e67b9e0d3ec5c4eab4a3b641509473a985120a2d4f3b1d8bb270974a3e5575`, 2,918,400 B,
  equal to the node log's.
  - The tar is not committed, and neither are the six fetched .npz copies (git ignores .npz).
  - Their sha256 are in `session/records/fetch-bsel/RECORDS.SHA256SUMS`, checked under `--strict` (6 lines for 6 files).
- **The pscratch root** `/pscratch/sd/j/josephrb/bsel-20261124` is static. Removing it is Joseph's call.
- **Renames:** 4 git-ignored names carry ".txt" (`run-20261124/RENAMES.tsv`, with each file's sha256).

**The six fetched inputs are committed** in `record/selection/`, by `git add -f` on these explicit paths only (the
director's ruling (a), 2026-11-24). selection.json names them by bare filename, and the receipt checker resolves a bare
name in the receipt-stem directory. Each copy's sha256 equals its pin in the declaration and its line in the tar's
RECORDS.SHA256SUMS. **All six are simulation only, with no data rows and nothing from a sealed product:**
- the two experiment tables hold only F0's and F1's pseudo-experiment relative residuals (`r_*`, `seed_*`, `flux_*`,
  `names`);
- the four closures are `pvl-unfold/1` MC closures (`closure: true`): unfolded simulation and its MC truth.

**The regenerated index files.** `results_index.py --write` lists 19 generated rows from selection.json. They are
keyed under the `closure_nuwro` truth name, because a JSON key named like a metric joins the results population.
They are marked UNATTRIBUTED, as the S2R, T3 and FD-PRR readouts were (the director's ruling of 2026-11-09,
option (a)). They are selection quantities (R, β, U), not results.

**CITABLE FOR:** the frozen labels and the rule that made them, and the controls and checks above.
**NOT CITABLE FOR:** any data statement, any held-out claim, any covariance validation, any note wording.
