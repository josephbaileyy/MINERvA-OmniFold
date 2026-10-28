# Step 9 (FD-F1-BINDING.md section 4.4, through FD-F1-BINDING-AMENDMENT-2.md section 4.3): the first receipt commit,
# the F1c deploy pin. Run locally from the root of a worktree at the bound pin 5f5e392c, after s9-look.sh's records
# were fetched into cluster/ and verified by sha256. It writes the two F1c tables from the committed
# f1-prep-SHA256SUMS, with F1b''s prep on pscratch, the F1c output root $OUT/f1c and the table directory inside the
# F1c deploy $OUT/deploy/f1c (accepted by the director: absent beforehand, HEAD = this commit, porcelain 0).
# This commit changes only paths under fd/receipts-f1/: no MANIFEST.tsv and no LEDGER.tsv, so generate_manifest.py
# --check fails at it (the receipts are manifest rows); the report branch regenerates the manifest after it.
# By the director's ruling, the two gen5d *.meta.json files and prep/config-f1.json are not in this commit (their
# results-index rows and an uncommitted npz they cite need paths outside fd/receipts-f1/); f1b3-SHA256SUMS here
# identifies all three by sha256, and their bytes land in the report branch's next commit. No F1c step reads them.
R=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-f1/run
OUT=/pscratch/sd/j/josephrb/fd-f1-20261027
mkdir -p $R/f1c
python3 -I -B nd-unfolding/fd_f1_tasks.py tables --sums $R/cluster/f1b3/prep/f1-prep-SHA256SUMS --prep $OUT/f1b3/prep \
  --runs $OUT/f1c --table-dir $OUT/deploy/f1c/$R/f1c --out-dir $R/f1c > $R/f1c/tables.log 2>&1
