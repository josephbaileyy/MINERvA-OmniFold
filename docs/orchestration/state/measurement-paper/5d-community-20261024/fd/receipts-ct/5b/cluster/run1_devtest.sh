# 5B development test run (FD-CT-5B-DECLARATION.md section 11; director's go-ahead 2026-10-30): the deploy's unit
# tests once, in a scratch clone at the branch head, on a login node. No job, nothing to CFS, no period output read.
set -o pipefail   # NOT set -u (conda activation)
PIN=${1:?pin}
T=/pscratch/sd/j/josephrb/fd-ct-5b-dev-20261030
[ -e "$T" ] && { echo "refusing: $T exists"; exit 2; }
mkdir -p "$T/logs" "$T/tmp"
D=$T/clone
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$D" && git -C "$D" fetch --quiet origin ct-5b-declaration \
  && git -C "$D" checkout --quiet --detach "$PIN" || { echo "clone failed"; exit 3; }
R=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-ct/5b
{ date -u +%FT%TZ; hostname; echo "head $(git -C "$D" rev-parse HEAD)"
  echo "porcelain_ignored_lines $(git -C "$D" status --porcelain --ignored | wc -l)"
  cd "$D" && sha256sum nd-unfolding/fd_ct_period_inputs.py nd-unfolding/fd_ct_periods.py nd-unfolding/tests/test_fd_ct_periods.py \
    nd-unfolding/submit_fd_ct.sh nd-unfolding/fd_ct_readers.py $R/make_5b_tables.py $R/*.tsv $R/flux/*.root; } > "$T/logs/dev.log" 2>&1
cd "$D/nd-unfolding/tests" && TMPDIR=$T/tmp env -u PYTHONPATH /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3 -B -m unittest -v \
  test_fd_ct_periods test_fd_ct_readers test_fd_ct_closure test_fd_f0_regrade test_s1_assemble > "$T/logs/dev-tests.log" 2>&1
echo "tests rc=$?" >> "$T/logs/dev.log"
grep -E "^Ran |^OK|^FAILED" "$T/logs/dev-tests.log" >> "$T/logs/dev.log"
grep -c "skipped" "$T/logs/dev-tests.log" | sed 's/^/skipped_lines /' >> "$T/logs/dev.log"
grep -E "RootReaders|RealUnfold" "$T/logs/dev-tests.log" >> "$T/logs/dev.log"
echo "porcelain_ignored_lines_after_tests $(git -C "$D" status --porcelain --ignored | wc -l)" >> "$T/logs/dev.log"
cat "$T/logs/dev.log"
