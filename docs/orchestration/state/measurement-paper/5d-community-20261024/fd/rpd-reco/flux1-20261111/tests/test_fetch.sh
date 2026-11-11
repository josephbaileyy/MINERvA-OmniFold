#!/bin/bash
# Run rpd_flux1_fetch.sh against fixtures, with the literal roots and MAT_PYTHON substituted in a test copy only.
SP=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/7e3f49f7-e8e4-452d-b380-399d4f6c529e/scratchpad
D=$SP/wtrc/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/flux1-20261111
T=$SP/flux1/t
PY=$SP/venvlint/bin/python
for mode in unfinished full leak orphan nopriv fpword big; do
  W=$T/$mode; mkdir -p $W/shm
  $PY -I $D/tests/build_fixture.py $W/root $mode $SP/chk848/nd-unfolding > $W/build.out 2>&1 || { echo "build failed $mode"; cat $W/build.out; continue; }
  sed -e "s#/pscratch/sd/j/josephrb/rpd-reco-flux-20261111#$W/root#g" -e "s#/dev/shm/limres-rpd-flux1-fetch#$W/shm/fetch#g" \
      -e "s#/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3#$PY#g" $D/rpd_flux1_fetch.sh > $W/fetch.sh
  cp $W/fetch.sh $W/self.sh
  PATH=$D/tests/shim:$PATH bash $W/fetch.sh $W/self.sh > $W/out.txt 2>&1
  rc=$?
  tb=$(grep -c '== TAR BEGIN' $W/out.txt)
  echo "MODE $mode rc=$rc tar=$tb self_removed=$([ -e $W/self.sh ] && echo no || echo yes) shm_left=$(ls $W/shm)"
  grep -E '^(STOP|NOT FINISHED|C3 CHECK|REDACTION CHECK|check rc|c3 check rc|send files|C3 not)' $W/out.txt | sed 's/^/   /'
  if [ "$tb" -eq 1 ]; then
    mkdir $W/untar; sed -n '/== TAR BEGIN/,/== TAR END/p' $W/out.txt | sed '1d;$d' | /usr/bin/base64 -d | tar -x -C $W/untar
    (cd $W/untar && /usr/bin/find . -type f | sort | sed 's/^/   sent: /')
  fi
done
