# Pointers for `fd_g_followup_readout.json` (2026-10-26)

**By** the measurement session, at the director's ruling (a) on the G-FOLLOWUP report's commit, 2026-10-26.

**Why these links exist.** G-FOLLOWUP's item 5 searched the key names of every pinned product.
- The readout's `r04.item5_search.matches` lists the key paths it matched, and 20 of them name S1's data-replica input
  files: `meta / inputs_sha256 / data_b<b>_j<100+b>.npz`, for b = 1–20, in S1's readout and npz.
- `verify_receipt_artifacts.py` reads each such name as an artifact the readout cites, and resolves it through this
  companion directory.

**What they are.** Each of the 20 files here is a relative symlink to S1's tracked copy,
`../../../s1/readout/s1_assembly/<name>`, committed with the S1 report. The target's sha256 equals S1's
`meta.inputs_sha256` value for that name; the table is in the report's PR.
- They are pointers to S1's tracked inputs, not new deliverables.
- The G-FOLLOWUP run read none of them. Item 5 reads key names only, and no data tuple was read.

**CITABLE FOR:** where the file names in item 5's matches resolve.

**NOT CITABLE FOR:** any G-FOLLOWUP number.
