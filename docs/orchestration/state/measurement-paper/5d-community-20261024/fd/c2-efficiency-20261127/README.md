# C2-EFF receipt: IBU K=10 against OmniFold on the same bootstrap draws, and against MINERvA's StatOnlyCovariance (tier3-design, 2026-11-27)

**Authority:**
- Joseph agreed to item 3a's follow-up on 2026-11-27, relayed by the director.
- The director read `c2_fetch.sh` (75e8a588) and `c2_fetch_remote.py` (c43de0fc) and gave a GO for one run.
- cov2d acknowledged the fetch at 22:39:39Z.
- limitation-resolver received START and END.

**MEASURES:** descriptive bootstrap widths (√tr of the replica covariance) on the 205 published bins:
- REF-C2C1's binned IBU (c2), at each iteration count, against OmniFold E_R on the same 300 three-stream draws (Q_R's statistical replicas);
- each of those against MINERvA's StatOnlyCovariance.

**CANNOT AUTHORIZE:** any note or paper wording, any change to a covariance, or any cause. The draws resample data, signal MC and background MC together. What StatOnlyCovariance contains is not established (item 3a). So the comparison with StatOnly sets unlike source sets side by side, as far as is known. The IBU is REF-C2C1's, not MINERvA's analysis code.

## Files

| file | sha256 |
|---|---|
| `c2_fetch.sh` (the launch driver) | `75e8a5884a13b54ec45b7ae57449b2a2fd25445d601fb159dc4744e4539d5eea` |
| `c2_fetch_remote.py` (the remote reader, piped on stdin) | `c43de0fcbe66cad4a6fdd7ef43a0c0c0a714cd32b4eba8519abf45b736e16274` |
| `c2_fetch_verify.py` (the laptop verifier) | `22583d1d58d48dd313ed66dfda0725c7240df2ebcb88cf3736fcb6ed14883284` |
| `c2_eff.py` (the analysis) | `fc798e7965cd796b028bb76cc623114335179e1ec822ff333083d2ccb88e92de` |
| `test_c2_fetch.py` (22 tests, `receipts/test_c2_fetch.txt`) | `25c90faad35b767bc310f1d76f97ba0d03ea1e01abb674b45e394eb0bda4b62c` |
| `test_c2_eff.py` (15 tests, `receipts/test_c2_eff.txt`) | `ab5525c2d0daf4892652d6d523107d3f091b83df5ee197ab094fd9bde3d3fca3` |
| `run/c2_eff.json` (the record) | `ba42af02b7035b8bdebe359055d0533e65a9244a4aa03bf101e31e7c21208080` |

## The fetch (`fetch/`)

- **Where and when:** one login-node read on login27, 2026-11-27T22:41:30Z to 22:41:33Z. The wrapper ran from 22:40:55Z to 22:41:33Z.
- **The fence:** sacct only, clear at 22:41:27Z with 0 rows of mine pending or running (`fence.txt` is empty, `fence.err` is empty, rc 0).
- **What was read:** 903 files, through O_RDONLY|O_NOATIME|O_NOFOLLOW:
  - `/pscratch/sd/j/josephrb/ref-c2c1-20261106/units/c2_replica_b1..b300` and `c2_central` (.npz, .done);
  - `…/read-2/inputs/001..301_xsec.root`.
- **What the remote side recorded:** `remote.err` reads `FETCH-DONE 903 files`, rc 0. `MANIFEST.tsv` is the remote manifest. In every row atime_ns before equals atime_ns after.
- **Nothing was written on NERSC.**
- **The laptop verifier** (`verify.out`) reads `VERIFY OK 903`:
  - every member matches the manifest;
  - every .done is PASS and carries its npz's sha256;
  - `c2_central.npz` equals the committed `units-centrals/c2_central.done` sha256 (929d0e78…);
  - each xsec.root size equals read-2's committed `inputs-listing.txt`.
- **Also:** `001_xsec.root`'s sha256 is `a5c13fc3…`, E_R's central sha256 in `2d-unfolding/ref_c2c1/config.json`.
- **The tar** (28 MB) is not committed. Its sha256 is in `fetch.tar.sha256`, and the sha256 of each unpacked file is in `SHA256SUMS`.
- **Where the fetched data lives:** the tar and its unpacked files are kept outside the repo at `/Users/josephbailey/c2eff-data/c2eff-run1/`. They were moved from the session scratchpad on 2026-11-27 at the director's request. After the move, fetch.tar's sha256 was 7f46eb31…, SHA256SUMS checked 903 of 903, and the tree matched the original. The scratchpad copy was then deleted.

## The analysis (`run/`)

`c2_eff.py` ran locally with BLAS threads capped at 1: rc 0, stdout `C2-EFF OK`, stderr empty. Every control passed:
- C-PIN;
- C-FETCH;
- C-META: each replica's meta names its unit, bootstrap_seed = b and 77d76cfc's config, and its own controls passed;
- C-CELLS: the committed `cells.root` set equals the release stat file's positive diagonal, 205 cells;
- C-STAT: rel 3.8e-9;
- C-AXES;
- C-QR: rel 3.8e-9. s_OF/s_STAT reproduces RE-2's 0.4066643573220531, so the 300 OmniFold files are Q_R's statistical replicas on the same cells;
- C-FINITE.

The readings are in `run/c2_eff.json`. They went to the director first.

## Mutants (follow-up)

`mutants_c2_eff.py` (`991ed06cf45ff7cc42d355407bd29f531c9018d4fdd83653e8884f837f3c808a`) applies one exact-text edit per mutant to a temp-dir copy, never to the files in place. Each mutant must make its suite fail:
- 20 mutants of `c2_eff.py`, run against `test_c2_eff.py`;
- 18 mutants of `c2_fetch_remote.py` and `c2_fetch_verify.py`, run against `test_c2_fetch.py`'s Fetch class.

The baseline passed, and **38 of 38 were killed** (`receipts/mutation.txt`, `9b63d675…`). The five source files hashed identically before and after the campaign. The wrapper `c2_fetch.sh` is not mutated: its tests need the git worktree, and it is pinned by sha and ran once.

## C2-CORR: correlation structure, spectra and paired differences (follow-up)

**Authority:**
- Joseph's yes of 2026-11-27, relayed by the director: items (1) and (2), local, 0 node-h, descriptive, numbers to the director first.
- The note figure and the headline keys follow Joseph's "can we try both the sentence and figure?" of 2026-11-27, via the director.
- The director approved the driver change (4f1047d9) and the producer (template a7f043cb) before they ran.

**CANNOT AUTHORIZE:** any note wording, the figure's placement or caption (rewrite-helper with Joseph), any change to a covariance, or any cause. The record's caveats apply:
- the draws resample MC and background as well as data;
- StatOnly's contents are not established;
- the IBU is REF-C2C1's;
- the small eigenvalues of a 300-replica sample covariance carry their own sampling noise.

**The driver:** `c2_corr.py` (`4f1047d94fa8186f91a68decf7cae5e17ead9c685b14c54729ba4ed9ddca4a4c`) reads C2-EFF's verified fetch from `/Users/josephbailey/c2eff-data/c2eff-run1/`. It imports `c2_eff.py` unchanged and runs its full control set first, C-QR included. It adds these controls:
- **C-PAIR:** on the full 224-cell vectors, with rank 75, it reproduces read-2's committed T: K10 to 4e-16 relative and K5 to 3e-15. That ties the per-replica pairing and both ensembles to the bound read.
- **C-ID:** the trace identity, to 1e-10.
- **C-PSD** and **C-CORR**.

**What it computes,** on the 205 published bins:
- (1) for C_IBU(K) at every K, C_OF and StatOnly: off-diagonal correlation summaries, eigenvalue spectra, top-k trace shares, participation ratios, and the principal-angle cosines between leading eigenvectors;
- (2) per K, the paired difference covariance Cov(IBU(K) − OF) on the same draws, the cross-covariance and the per-cell correlations;
- a flat `headline` block of 20 values a note sentence may bind. Each is copied from the record's own fields.

**Tests:**
- `test_c2_corr.py` (`c93d7300…`): 17 tests, OK (`receipts/test_c2_corr.txt`);
- `test_c2_corr_figure.py` (`f75bb794…`): 10 tests, OK (`receipts/test_c2_corr_figure.txt`).

**The run** (`run-corr/`): local, rc 0, `C2-CORR OK`, stderr empty.
- The record is `run-corr/c2_corr.json` (`a084016f876e2faf6dd7064a95c1de8396527c4e401519058fff6f7c9a392a0d`).
- A first run of the driver before the headline block (`e6d94347…`) gave record `5be4884f…`. With `headline` removed, this record equals that one, key for key and value for value.
- The readings went to the director first.

**The note figure:**
- `c2_corr_figure.py` (`a8dfd306c79adf538c3d088f09e3a0b50e83e2b8f1b3d0f75c034710c3744b34`) draws `docs/analysis-note/figures/c2_corr_spectra.pdf` (`f7ac9a0e8ebd64aeaddd3da9944ba301c7d48747ff6389332695baf21537b18f`).
- It uses the record's `figure_spectra` only, and refuses unless the record's sha256 is `a084016f…` and every control passed.
- **Style:** the note's print style at 0.49 of the text width. OmniFold is red solid, the published covariance black dashed, and IBU bluish green #009E73 dash-dot (the note has no IBU series identity yet). The legend is the director's three strings, above the axes.
- `run-corr/figure_choice.txt` records the two rejected legend placements. `run-corr/c2_corr_spectra_render.png` is the render the director accepted.
- A redraw into a temporary path is byte-identical to the committed PDF (`receipts/figure_reproduction.txt`).
