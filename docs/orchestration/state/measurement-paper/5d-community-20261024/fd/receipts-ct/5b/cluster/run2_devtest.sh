# 5B development test RERUN (director's approval 2026-10-30): the same five modules in the same clone, root_6_28
# activated by prefix (the first run's bare interpreter segfaulted on import ROOT, rc 139). No job, nothing to CFS.
set -o pipefail   # NOT set -u (conda activation)
PIN=${1:?pin}
T=/pscratch/sd/j/josephrb/fd-ct-5b-dev-20261030
D=$T/clone
[ -d "$D" ] || { echo "no clone"; exit 2; }
[ -e "$T/logs/dev2.log" ] && { echo "refusing: rerun log exists"; exit 2; }
{ date -u +%FT%TZ; hostname; echo "head_before $(git -C "$D" rev-parse HEAD)"
  echo "porcelain_ignored_lines_before $(git -C "$D" status --porcelain --ignored | wc -l)"
  git -C "$D" fetch --quiet origin ct-5b-declaration && git -C "$D" checkout --quiet --detach "$PIN"
  echo "head $(git -C "$D" rev-parse HEAD)"
  echo "porcelain_ignored_lines $(git -C "$D" status --porcelain --ignored | wc -l)"
  cd "$D" && sha256sum nd-unfolding/fd_ct_period_inputs.py nd-unfolding/fd_ct_periods.py nd-unfolding/tests/test_fd_ct_periods.py \
    nd-unfolding/submit_fd_ct.sh nd-unfolding/fd_ct_readers.py
  echo 'activation: eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"; conda activate $HOME/.conda/envs/root_6_28'
} > "$T/logs/dev2.log" 2>&1
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
{ echo "python $(command -v python3) $(python3 -V 2>&1)"; python3 -c "import ROOT, lightgbm; print('ROOT', ROOT.gROOT.GetVersion(), 'lightgbm', lightgbm.__version__)" 2>&1 | tail -1; } >> "$T/logs/dev2.log"
cd "$D/nd-unfolding/tests" && TMPDIR=$T/tmp env -u PYTHONPATH python3 -B -m unittest -v \
  test_fd_ct_periods test_fd_ct_readers test_fd_ct_closure test_fd_f0_regrade test_s1_assemble > "$T/logs/dev2-tests.log" 2>&1
echo "tests rc=$?" >> "$T/logs/dev2.log"
grep -E "^Ran |^OK|^FAILED" "$T/logs/dev2-tests.log" >> "$T/logs/dev2.log"
grep -E "skipped" "$T/logs/dev2-tests.log" >> "$T/logs/dev2.log"
grep -E "RootReaders|RealUnfold|BareInterpreter" "$T/logs/dev2-tests.log" >> "$T/logs/dev2.log"
echo "porcelain_ignored_lines_after_tests $(git -C "$D" status --porcelain --ignored | wc -l)" >> "$T/logs/dev2.log"
cat "$T/logs/dev2.log"
