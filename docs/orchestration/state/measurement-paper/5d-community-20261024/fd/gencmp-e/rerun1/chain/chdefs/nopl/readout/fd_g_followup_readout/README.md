# Pointers for this `fd_g_followup_readout.json` (GENCMP amendment E report, rerun1)

As `fd/readout/fd_g_followup_readout/README.md` explains for the committed readout: G-FOLLOWUP's item 5 lists 20 key
paths that name S1's data-replica input files (`data_b<b>_j<100+b>.npz`, b = 1-20). `verify_receipt_artifacts.py` reads
each name as a cited artifact, and resolves it through this companion directory.

Each file here is a relative symlink to S1's tracked copy, `../../../../../../../../s1/readout/s1_assembly/<name>`. They are pointers to S1's
tracked inputs, not outputs of this run, and the run read none of them.
