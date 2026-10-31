# Pointers for the with-block `fd_g_followup_readout.json` (2026-10-31)

**By** the measurement session, as the committed readout's companion does
([`../../../readout/fd_g_followup_readout/README.md`](../../../readout/fd_g_followup_readout/README.md), the director's
ruling (a) of 2026-10-26).

**Why these links exist.** G-FOLLOWUP's item 5 searched the key names of every pinned product. With the block, its
`r04.item5_search.matches` again lists S1's data-replica input names, `meta / inputs_sha256 / data_b<b>_j<100+b>.npz` for
b = 1–20. `verify_receipt_artifacts.py` reads each name as a cited artifact and resolves it through this companion
directory.

**What they are.** Each of the 20 files is a relative symlink to S1's tracked copy,
`../../../../s1/readout/s1_assembly/<name>`. These are the same targets as the committed companion's links.
- They are pointers to S1's tracked inputs, not new deliverables.
- The run read none of them.

**CITABLE FOR:** where the file names in item 5's matches resolve.

**NOT CITABLE FOR:** any number.
