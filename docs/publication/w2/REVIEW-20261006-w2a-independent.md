# Independent review of W2a (recoil-response universe): verdict CLEARS WITH CHANGES (2026-10-06)

**CITABLE FOR:** the review's target, verdict, findings and the changes required before W2b. This is the publication
lane's checked restatement of the reviewer's report, not a verbatim transcript.
**NOT CITABLE FOR:** any W2b result.

| | |
|---|---|
| reviewer | a fresh, read-only Opus 5.5 subagent with no prior context. It worked in a detached worktree `MINERvA-OmniFold-w2-review` at `35241cbd` and left it clean. |
| target | `study/w2-recoil-response-20261006`: `4afeb108` (code and scripts), `a661bd75` (checker fix), `35241cbd` (report, ledger, checks) |
| verdict | **CLEARS WITH CHANGES.** There is no blocking defect in the universe or patch. Three changes to the W2b launcher and orchestration are required; none touches the reviewed binary (mod md5 `f3e9c97b…`). |
| deviation | The reviewer briefly copied a verification script to `/pscratch/sd/j/josephrb/tmp/`, then deleted it without running it. Everything else ran over stdin. No other remote write. |

## Independent evidence the reviewer produced

**Full-1A shifted outputs against the production 1A CV omnifile**
(`nd-unfolding/runEventLoopOmniFold_5D_1A_universes_full_bkgaware.root`):
- the entry counts are equal in all four trees;
- every branch other than reco E_avail, q3 and W is identical, including all of the data tree, truth, weights and POT;
- reco E_avail = s × production, with relative error ≤ 2.3e-16 on 1,736,833 signal and 52,626 background rows.

**Q² coupling, smoke subset.** q3 was predicted from the muon kinematics with E_ν = E_μ + s·q0. It matches within
2.5e-10 GeV on every passing row, including the rows clipped to W = 0.

**Accounting and identity.** The ledger matches sacct exactly: 0.0985 node-h. The omnifile and data-product sha256
values match.

## Findings

| id | severity | finding | disposition |
|---|---|---|---|
| F1 | SHOULD-FIX (required for W2b) | The 4 h limit is too short for 1M (projected 10,497–13,205 s; historical up to 17,729 s) | C1 |
| F2 | SHOULD-FIX | The comparer's q0 identity q3² + W² = (q0 + M)² cannot see the Q² term. The implementation is correct by the reviewer's independent check. | State it in the W2b report |
| F3 | NOTE | The `sim_pass` UChar_t read as an object array makes `astype(bool)` all True. The counts are right only because of the −9999 sentinel filter. | Fix if the comparer is reused |
| F4 | NOTE | The q0 check passes vacuously with 0 valid rows | Add a floor if reused |
| F5 | NOTE | The band is unsafe with `MNV101_DUMP_UNIVERSES` or `MNV101_DUMP_POINTCLOUD` (E_avail shadow; cluster energies unscaled). The launcher's unset list is the only guard. | C2 |
| F6 | NOTE | The simplification scales `NewEavail` (linear, exact) and the calibrated `recoil_E` output separately. Under the exploratory label this is acceptable. MAT's per-particle response map is commented out. | State it with the W2b result |
| F7 | NOTE | The report's "4.91e12 B" MC total should be 1.0534e13 B. The 1A share 0.0671 is correct, so the projection is unaffected. | Correct the text |
| F8 | NOTE | MaxRSS counts page cache and cannot show memory headroom | Never quote MaxRSS as headroom |
| F9 | NOTE | Build gaps: unchecked rsync; the final diff does not fail the script; unpinned gitignored inputs and MAT libraries. No drift was seen for 1A. | Record |
| F10 | NOTE | Downstream: the lateral dump should accept the omnifile with the 1A…1P merge order. The δ = 0 control is unlikely to be bitwise, and the fallback criterion is likely to pass. Evaluate is fine. | — |

## Changes required before W2b

- **C1:** set per-playlist time limits (1M ≥ 6 h; 1F, 1D, 1G ≥ 5 h). Before submission, require that Σ(limit × 10/256)
  plus the recorded spend is ≤ 8.0. This lane computed the worst-case reservation at those limits: 6.211 node-h for
  the event loops, 6.645 including spend, dumps and unfolds. That is ≤ 8.0.
- **C2:** the W2b launcher keeps the W2a unset list and refuses `MNV101_DUMP_UNIVERSES` and `MNV101_DUMP_POINTCLOUD`
  whenever δ is set.
- **C3:** the W2b design copy differs from the frozen design **only** in `data_central`, shown by a committed key-diff.
  Use the 1A…1P merge order and the reviewed binary `f3e9c97b`.

## Gate status (Joseph 2026-10-06, item 4)

- **Review clears the implementation:** yes, with C1–C3 as preconditions on the W2b run.
- **Measured cost fits the 8 node-h ceiling:** yes. That is 0.0985 measured, a projected total of 2.5–3.1, and a
  worst-case reservation of 6.65.
- **After D2:** yes. The resolution `11a266c6` and `b354cdf7` and the cross-check `00009056` are committed.

**W2b may proceed** once C1–C3 are implemented and checked by this lane before submission. A failed control or
stopping gate stops the study. It does not authorize a larger budget or another variation.
