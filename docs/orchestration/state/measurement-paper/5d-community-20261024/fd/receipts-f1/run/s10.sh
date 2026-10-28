# Step 10 (FD-F1-BINDING.md section 4.5, through FD-F1-BINDING-AMENDMENT-2.md section 4.3): the F1c deploy at the F1c
# pin (the first receipt commit, a child of the bound pin 5f5e392c changing only fd/receipts-f1/), then F1c by the
# bound submit stage only if every check holds. Login node. Never touches $OUT/f1b or $OUT/f1b2.
OUT=/pscratch/sd/j/josephrb/fd-f1-20261027
BOUND=5f5e392c4be9c6f8bb035a72d4a60f7dd8be8803
PIN=741ad029e63732cfe6b7db07568bb2af86e47ebd
D4=$OUT/deploy/f1c
R=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-f1/run
date -u +%FT%TZ; hostname
for x in $D4 $OUT/f1c; do [ -e "$x" ] && { echo "STOP: $x exists"; exit 3; }; done
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold $D4 && git -C $D4 checkout --quiet --detach $PIN; echo "clone rc=$?"
H=$(git -C $D4 rev-parse HEAD); echo "HEAD $H"
N=$(git -C $D4 status --porcelain --ignored | wc -l); echo "porcelain_ignored_lines $N"
echo "parent $(git -C $D4 rev-parse HEAD^)"
X=$(git -C $D4 diff --name-only $BOUND $PIN | grep -vc "^docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-f1/"); echo "files outside fd/receipts-f1/ since the bound pin: $X"
git -C $D4 diff --stat $BOUND $PIN | tail -1
T=$D4/$R/f1c/tasks-f1c.tsv; S=$D4/$R/f1c/f1c-steps.tsv
echo "tables: $(sha256sum $T | cut -c1-64) tasks-f1c.tsv, $(sha256sum $S | cut -c1-64) f1c-steps.tsv"
( cd $OUT/f1b3/prep && sha256sum -c $D4/$R/cluster/f1b3/prep/f1-prep-SHA256SUMS ); echo "F1b' prep against the pin's f1-prep-SHA256SUMS rc=$?"
[ "$H" = "$PIN" ] && [ "$N" -eq 0 ] && [ "$X" -eq 0 ] || { echo "STOP: deploy checks failed"; exit 3; }
bash $D4/nd-unfolding/submit_fd_f1.sh f1c $D4 $PIN $OUT $T; echo "submit rc=$?"
