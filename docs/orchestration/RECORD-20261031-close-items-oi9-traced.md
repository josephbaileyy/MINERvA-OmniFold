# RECORD — OI-9 traced: still a live code task, reached only by a re-run of P4 stage 3 (2026-10-31)

**By** the close-items session, on the director's order of 2026-10-31. Read-only: `git log`, `git grep` and `git
show`, at `efd014670`. No code was written or run, and the director said not to take the code.

**CITABLE FOR:** what OI-9 asks, why it is still undone at `efd014670`, what runs the code it concerns, and an owner
shape for doing it.

**NOT CITABLE FOR:**
- whether the merged-audit checks are correct. Nothing here re-assessed them;
- whether standard P4 will be re-run.
<!-- absence-ok: scoping statements about what this record covers -->

**PROPOSES:** deferring OI-9 to a named trigger, with the owner shape in §3 for when it fires. The register is not
changed here; the ruling is the director's.

## 1. What the row asks

OI-9 is `OPEN` (queue `NOW`), owner *"UNOWNED — offered to lane D 2026-08-18, declined"*, dated 2026-08-12.
- Blocker: *"Native-miss and merged-audit checks are testable only in the ROOT environment."*
- Next action: *"Extract a ROOT-free metadata checker and wire p4_evidence.py to call it in the same change."*
- Lane D declined because the ask *"is a code change end to end"*, and its dispatch was to write findings only.

## 2. Why it is still undone

**The checks are still inline in a module that imports ROOT at top level.**
- `nd-unfolding/p4_evidence.py:22` is `import ROOT`.
- The merged audit is top-level loop code at `:208-283`. It reads each merged endpoint with `ROOT.TFile.Open`
  (`:218`), then asserts on the values in the same loop: zombie and recovered, tree entries, POT, band and index
  identity, the native-miss flag and count (`:250-270`), census, and selection migration.
- So nothing can import the checks without ROOT, and the module runs its work at import.

**A ROOT-free checker did once exist, and was deleted.** `p4_evidence.py:241-243`: *"the strengthened comparison was
put in check_merged_metadata -- which has no production caller. The comparison now lives HERE, in the path that
actually runs."* `a1b7632f7` (2026-08-09, *"Repair-7 items 1-3 … delete the dead path"*) removed it, three days before
OI-9 was filed. OI-9 asks for the other half: a checker that production calls.

**The later commits to `p4_evidence.py` did not do it:**
- `d4a22e21e` (2026-08-12) de-rooted the repository path, not the ROOT import;
- `adc7df18c` (2026-08-28) removed unused imports;
- `e2632ac73` and `c05c64a99` (2026-09-21) changed seed gates;
- `036f507e4` (2026-09-23) made `STOP_AFTER=audit` truthful.

**What tests reach the checks today.** `tests/test_evloop_tparameter_merge_modes.py:44-45` asserts by regex that
`p4_evidence.py` still reads `hasTruthOnlyMisses` as a merged count. It reads the source and does not run the check.

**What runs it.** One caller: `nd-unfolding/run_p4_standard.sh:99`, stage 3,
`python3 p4_evidence.py`. Search: `git grep -n 'p4_evidence\.py'` over `*.sh` @ `efd014670`. The other hits are
comments.
<!-- absence-ok: the search and sha are named in this paragraph -->

**Where its product reaches.** The merged-audit receipt `active_universe_5d/standard/evidence/p4_merged_audit.json`
was last changed on 2026-08-22 (`0f1b7b8db`). OI-7's reach check: *"no live unstruck note macro descends from the
standard-P4 chain"*. Its product is a candidate projected 4D covariance, and the note withholds the 4D budget.

**A usable fixture already exists.** That receipt holds, for all ten endpoints, every field the checks read:
- `zombie`, `recovered` and `tree_entries`;
- `mcPOT` and `dataPOT`;
- `band_meta` and `idx_meta`;
- `hasTruthOnlyMisses` and `nTruthOnlyMisses`;
- `census` and `selection_migration_abs`.

`BeamAngleX_0`, for example, carries `hasTruthOnlyMisses` 12 and `nTruthOnlyMisses` 8,999,007, the post-`hadd`
values that `:244-249` describe. So a ROOT-free test can be built from the producer's own output, as PB-16 asks, and
not from the rule under test.

## 3. The proposal

**Defer OI-9**, trigger: *"a run of `run_p4_standard.sh` stage 3 (`p4_evidence.py`) is declared, or a defect is
reported in its merged-audit checks."* The code task is real, but its only caller is stage 3, whose merged-audit
receipt was last changed on 2026-08-22, and its product reaches no live quoted number. Doing it now would add a code change with no
consumer.

**The owner shape, for when the trigger fires.** One code lane, one PR, no physics change:
- **Who:** a lane that can write code and run Python with ROOT. The parity step needs read access to the ten merged
  endpoint ROOTs, which are on the cluster.
- **The change:**
  - a new pure function, for example in `p4_lib.py`, that takes one endpoint's already-read values (the fields
    listed in §2) and returns its blocker strings;
  - `p4_evidence.py:208-283` keeps the ROOT reads and calls that function in place of the inline `need(...)` calls.
- **The tests**, ROOT-free and in both directions, built from `p4_merged_audit.json`:
  - all ten endpoints give no blocker;
  - each mutation fires its blocker: the pre-merge `in (0, 1)` reading of the flag, flag/count disagreement, a flag
    above 12, an index mismatch;
  - `COUNT_CONSUMERS` in `test_evloop_tparameter_merge_modes.py` is re-pointed to the new site.
- **The parity check:** a read-only ROOT run of the audit section gives the same per-endpoint records and blockers
  as the committed receipt.
- **Its terminal criterion:** the PR is merged with the tests green and the parity shown.

**The alternative,** if the director prefers to keep it on the `NOW` queue: assign that owner shape now. It needs one cluster
read for the parity step.

**Dependency check.** Search: `git grep -n -E 'OI-9([^0-9]|$)'` @ `efd014670`, excluding `OPEN_ITEMS.md` and the
generated views. No hits outside the row itself. Nothing routes open work to OI-9.
<!-- absence-ok: the search and sha are named in this paragraph -->
