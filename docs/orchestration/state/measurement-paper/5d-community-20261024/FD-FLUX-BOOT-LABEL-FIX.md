# The 3D tool's band-record label, corrected (2026-10-28)

**By** the paper-tighten lane, as director, under Joseph's standing rule "fix it now and re-pin with a record".

**What was wrong.** `nd-unfolding/fd_flux_boot.py:70`'s `LABEL`, carried on all 10 band records of the 3D readout
(`fd/readout/fd_flux_boot_readout.json`, `b7b5652c…`), read "descriptive band on the reported χ²'s
flux-correlation dependence, not an alternative result". That is sensitivity wording. It contradicts the readout's own
`labels.band` ("estimation uncertainty, not sensitivity") and `FD-FLUX-BOOT-BINDING.md` ruling 2.
`FD-FLUX-BOOT-REPORT.md` §2 ruled that `labels.band` governs that readout and left the constant to the director.
The measurement session's handoff lists it as open item 1 (`HANDOFF-20261028-measurement-session.md` §5).

**The fix.**
- `LABEL` now reads "estimation uncertainty, not sensitivity: the scatter of the reported chi2 when the flux
  correlations are re-estimated from the 100 weighted universes; not an interval for the chi2 under the true
  correlations".
- A new test, `Pure.test_the_band_records_label_agrees_with_labels_band`, requires both phrases, requires
  `labels.band` to begin with the first, and forbids "dependence". Restoring the old wording into the constant was
  caught by it.
- `test_fd_flux_boot`: **Ran 34 tests, OK**, locally with `-B` and a TMPDIR.

**New digests:** `fd_flux_boot.py` `cbd5ac9c215382d9…` (was `f82bd4f4…`) and `test_fd_flux_boot.py` `5b585d378fee6c15…` (was
`00b3ba42…`). Any future 3D run pins these, and its deploy suite counts 208 tests, not 207.

**Not changed.**
- The bound 3D run, its deploy pin `91312bc8` and its readout `b7b5652c`. That readout keeps the old label, and
  `labels.band` governs it, as `FD-FLUX-BOOT-REPORT.md` §2 says.
- No number. The tool's arithmetic is untouched: only the string constant and one test change.
