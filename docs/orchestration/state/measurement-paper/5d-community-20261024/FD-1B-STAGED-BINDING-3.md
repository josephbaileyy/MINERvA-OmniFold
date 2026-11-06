# FD-1B STAGED BINDING 3: stage 1 on configuration (e), the two held-out tunes (director, 2026-11-06)

**Binds** amendment 2.1's §11, *Binding 3: the declaration (a fixed conditional sequence)*, in
`FD-1B-STAGED-ADDENDUM-A2-1.md`, sha256 `ef4a57e0c98e36bea80742a4f26f453ba80b62b6c248fa331233ae5b178e39e5`. The text and
code bound are those on branch `decl/1b-staged-a2-1-20261103` at:

**M = `6d93dd4284c1d378836ba275923d490f0f6c62f3`**

The deploy for stages 3–7 is M3, the branch commit after M that adds only the gate pin (below). The branch is never merged
into main before the campaign ends (ruling 4).

## What it binds

**The five gate files**, by the sha256 that `gate_code_digests()` records and `check_clip_gate` requires:

| file | sha256 |
|---|---|
| `nd-unfolding/fd_1b_c2.py` | `522d7edd71643df61d0c5ef5a7488834e664eb36d20c3e0c0b46e10a5808f02f` |
| `nd-unfolding/fd_1b_mc.py` | `062628b69976f730d9d394e64ecf6f93d9952654306471ac0119542c6b07dd67` |
| `2d-unfolding/cov2d/cov2d.py` | `0d852a6992398b6b1ba7956b2e8d74accc2b6f1aa7b7909a6ef7d6d7f0dcd756` |
| `…/fd/receipts-cov2d/clip/clip_probe2.py` | `b95c562916091b910a5ca8d874d83296035690cb8784db3d318b2f07fed28182` |
| `nd-unfolding/fd_1b_toys.py` | `869a65c3bcce1a3b56ecd197ecdf3b6cf2741e0611f91b582c3064f67967bc08` |

The director re-hashed each at M.

**Also bound:**
- the guarded launcher `nd-unfolding/fd_1b_noatime_guard.py`, `ee20534c20504aa1335bad4e75be067c0465c7faaa60d2a14a47abb81e22f60c`;
- the 300-draw pins `nd-unfolding/fd_1b_cal300_pins.json`, `f6edf4b0116d2ef0058bb790ddc94c1d678ce8d5b798825069f7b343c03bab31`;
- the merged gate record `gate.json`, `6a832bf0692864aefb5f7e97e22f3c8025d87679561463358550dc12b090b062` (stage 2, below);
- stage 3's connects at M: `b3/connect-receipt.sh` (`f2b5b2cb…`) and `b3/connect-receipt-readout.sh` (`322216ef…`).

**The estimator is configuration (e),** unchanged (`OUTCOME-20261105-fd-stab-none-pass.md`: B4 NONE_PASS, terminal).

## What the director checked

- **Stages 1 and 2 have already passed** under the director's go of 2026-11-05, as the declaration's priced prerequisites.
  - c2check, G18 (60880987): PASS, option (1), 17,563 s.
  - c2check, AR23 (60880988): PASS, option (1), 17,905 s.
  - c2check-merge: C2-GATE-MERGED PASS, gate.json `6a832bf0`.
  - 0 of 1,147 declared-input atimes moved. Spent: 9.85 node-h.
- **The full mutation receipt** at the frozen code `9b87a85c`, plan 387: 370 of 370 applicable killed, 15 not applicable,
  2 equivalent with proving tests, and all 7 REQUIRED killed. It re-runs at M for the test-only change (EXPECTED_B3) and
  comes with stage 3's report.
- **The audit** (coverage-5b-audit):
  - §11's B1–B5 are closed: the no-plug-in path, the price, stage records identified by path, job, head, pin and sha,
    undeclared scripts waiting for a read, and guard_scan failing on empty populations;
  - P1 is closed under ruling (i);
  - stage 3's two connects raise no blocker; the auditor verified all 14 blobs at M.

## Rulings

1. **Binding 3 is the no-plug-in path:** G18 and AR23 only, with a bulk of 6 jobs. Whether the plug-in truth belongs in 1B
   is deferred to Joseph's publication-scope decision. Adding it later would need its own binding: S1-0 with the
   capture, all three c2checks with the push, and a new pin, at about 120 node-h or more. Binding 3's bulk products would
   not resume under that.
2. **The price.**
   - The ceiling is **72.0 CPU node-h** at caps for this population, and about 9.85 of it is spent.
   - The director reports it to Joseph as within the standing grant. It is far below half the balance.
   - Every job is under 12 h, and every `--time` is written HH:MM:SS with the TimeLimit check.
3. **A fixed conditional sequence for stages 3–7** (§11). Each stage proceeds when the previous stage's PASS record,
   identified by path, job id, deploy head, pin sha and logged sha256, is committed on the branch. Anything else, meaning
   a STOP, INVALID, REPRICE or refusal, stops and comes to the director. coverage-5b reports each connect's sha256 and
   result as it goes, without waiting for a go, except where a stage's script is not yet written: per B4, a new script
   waits for an audit read and the director's go.
   - **3:** the gate pin committed as M3, then the receipt connect and its readout.
   - **4:** S1-0 and its walls and controls, then S1-0b and its walls, then clipcheck.
   - **5:** the smoke run: 10 rows from the real bulk table, two per mode across both truths, one repeated for resume.
   - **6:** the bulk, in waves of up to 3 jobs, each wave's walls PASS before the next. **Stage 6 waits for both** the
     smoke PASS record and the auditor's committed acknowledgement.
   - **7:** per truth, n1, null, readout and report.
4. **Deploys.** Every stage from 3 deploys M3, a branch commit, never a merge with main.
   - Each connect checks all five gate files, the guard and the pins file before launch, and refuses on any difference.
   - The five gate files are frozen.
   - The branch merges into main only after stage 7, as a records merge with no runs.
5. **The read guard.**
   - Every 1B entry runs through `fd_1b_noatime_guard.py`.
   - guard_scan refuses an unguarded or indirect launch line, and fails on an empty population.
   - **Stated residuals:**
     - the entry mains do not themselves refuse when unguarded;
     - RealFlag runs only on Linux;
     - the smoke run cannot run the full readout on a subset;
     - the stat window spans whole jobs, so another lane's read could cause a fail-closed stop. That is a low risk, held.
6. **The COV2D fence** binds 1B's connects as well. No plain read of a COV2D input while a cov2d-* job runs.
7. **Unchanged:** amendment 2 and A2.1's other sections, the clip rule (#718), the large-sample variance gate (#729), and
   paper wording only through the paper lane, a PRD-referee read and Joseph.

Nothing is submitted, deposited or tagged.
