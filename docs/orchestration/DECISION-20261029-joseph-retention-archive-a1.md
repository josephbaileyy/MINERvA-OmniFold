# DECISION 2026-10-29 — Joseph: archive the three pscratch-only products to HPSS

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- The coverage session's retention proposal
  (`state/measurement-paper/5d-community-20261024/FD-PSCRATCH-RETENTION-PROPOSAL.md`, PR #467) measured the director's
  pscratch list, read-only. It found:
  - no listed directory is exposed by NERSC's 8-week rule before about 2026-12-17; scratch is 85 % full, so a
    fullness purge stays possible;
  - about 21.6 GB of the list is git clones at commits on `main`;
  - three products are pinned by digest but held in neither git nor HPSS:
    - F0's per-experiment table, `fd_f0_experiments.npz` (`7384c651…`, 1,068,642 B);
    - `cmodel_5d.npz` (`3008d8f6…`);
    - the pv-ladder's frozen reweights under `prep/` and its 30 products.
- The director offered three options: archive the three products; delete the re-clonable clones; keep the rest as it
  is.

Joseph's answer, verbatim, the only option he selected:

> Archive 3 products to HPSS (Recommended)

sha256 of the text plus a final newline begins `9bc48b306c0d1d41`.

## What is decided

1. **One HPSS archive (A1) holds the three products,** about 25 MB:
   - F0's per-experiment table (F0b's copy is byte-identical);
   - `cmodel_5d.npz`;
   - the pv-ladder's `prep/` and `products/`.

   Each file is hashed against its committed pin or sums before the tar. It follows `stage0_preserve.sh`: `hsi put`,
   `hashcreate`, `hashverify`, a get-back and a sha256 compare.
2. **F0's per-experiment table is also committed to git,** beside F0's readout, at 1.07 MB, with its sha256 checked
   against `7384c651…`. The option offered included this.
3. **The clones are not deleted.** The options to delete them, and to keep the rest unchanged, were not selected, so
   nothing is deleted. Access dates are re-checked before mid-December.
4. **The coverage session carries out items 1 and 2** and reports with the HPSS path, the tar digest and the verification.

## Not changed

- Nothing on pscratch is deleted.
- Nothing is submitted, deposited or tagged.
