# Pointers for this `fd_g_followup_readout.json` (V_F Phase 1, 2026-11-26)

**By** tier3-design, following the with-block companion
(`fd/with-cpl/readout/fd_g_followup_readout/README.md`, the director's ruling (a) of 2026-10-26).

**Why these links exist.** G-FOLLOWUP's item 5 searched the key names of every pinned product. Its
`r04.item5_search.matches` lists S1's data-replica input names, `meta / inputs_sha256 / data_b<b>_j<100+b>.npz` for
b = 1–20. `verify_receipt_artifacts.py` reads each name as a cited artifact and resolves it through this companion
directory.

**What they are.** Each of the 20 files is a relative symlink to S1's tracked copy in `s1/readout/s1_assembly/`.
- They are pointers to S1's tracked inputs, not new deliverables.
- The run read none of them.
- They were added after the fetch, so they are not in `run.sha256`.

**CITABLE FOR:** where the file names in item 5's matches resolve.

**NOT CITABLE FOR:** any number.
