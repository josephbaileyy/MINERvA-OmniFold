# OOFVC r2: dispositions

The r2 reads were of commit 6aba1d3b (inputs in `inputs.sha256`).
- **codex-school `gpt-6.2-sol`, high:** 5 BLOCKERs and 2 NONBLOCKERs, NO-GO. It used 121,086 tokens; the account went
  from 15% to 14% weekly.
- **agy `gemini-4-hydrogen-high`:** GO. Every r1 disposition checks out, and its one NONBLOCKER is codex #1.

All items were fixed in the commit that adds this file (declaration revision 5).

| # | reader | finding | disposition |
|---|---|---|---|
| c1, a2 | both | `n.npz` (and the records) were outside every digest, so a copied N file could score | Fixed. Each unit process records the digest of every file it wrote (done-marker, npz, root, record, `n.npz`) in its pins file. The scorer re-hashes them all and requires `n.npz` for each c2 unit. Mutant: SCORE_OUTPUTS |
| c2 | codex | An R run with another seed, or a c2-only change to the data or flux, could pass | Fixed. Each unit's argv must equal E_R's (the two input file names, then E_R's options), with R adding exactly the minerva suffix. C-FIX now covers the c2 pair as well as the E_R pair. Mutant: SCORE_FIX |
| c3 | codex | A NaN `w_truth` on a row reconstructed outside the grid aborted the load, and C-MOVE expected a row the background loader never filled to leave it | Fixed. `w_truth` may be non-finite in the rows file, and the signal rule drops it from an appended row. C-MOVE counts only rows the background loader filled (0 ≤ w < 1e6) |
| c4 | codex | Pins were compared with the scorer's checkout, and the staged-input and join digests were not checked | Fixed. The lane's files are compared with `--tool-commit` (`git show`), the staged inputs with 43f8cc16… and d40aea69…. C-JOIN-RECORD requires the omnifile and split.json digests and the four PASS controls |
| c5 | codex | The timing gate counted names, not playlists | Fixed. Each of the twelve playlists the array runs must have its entry-count line |
| c6 | codex | §1.2 still described the old duplicate rule | Fixed in the declaration |
| c7 | codex | The remaining r1 dispositions check out | No change |
