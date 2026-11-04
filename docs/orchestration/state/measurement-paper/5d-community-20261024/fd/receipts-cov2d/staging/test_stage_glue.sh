#!/bin/bash
# The connect's glue on fake trees: the pinned digests are replaced by the fakes' own, lfs and hostname are stubbed.
set -u
mkbin() { mkdir -p /stub; printf '#!/bin/bash\necho dtn01.nersc.gov\n' > /stub/hostname
  printf '#!/bin/bash\necho "Disk quotas for usr root"\necho "  Filesystem kbytes quota limit grace files quota limit grace"\necho "  /pscratch %s 1000000000 1500000000 - 1 2 3 -"\n' "$1" > /stub/lfs
  chmod +x /stub/*; }
setup() {  # $1 a variant: ok | sums | partb
  rm -rf /pscratch /global; CFS=/global/cfs/cdirs/m3246/josephrb
  mkdir -p /pscratch/sd/j/josephrb $CFS/two-d-followup-20261010/xr-input $CFS/2d-closeout-stageC-inputs-20261012/active_universe_5d_standard_merged
  A=$CFS/2d-closeout-stageC-inputs-20261012/active_universe_5d_standard_merged
  head -c 2000000 /dev/urandom > $CFS/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root
  : > $A/SHA256SUMS
  for lat in BeamAngleX_0 BeamAngleX_1 BeamAngleY_0 BeamAngleY_1 MuonResolution_0 MuonResolution_1 Muon_Energy_MINERvA_0 Muon_Energy_MINERvA_1 Muon_Energy_MINOS_0 Muon_Energy_MINOS_1; do
    f=runEventLoopOmniFold_5D_MEFHC_active_$lat.root; head -c 1500000 /dev/urandom > $A/$f; (cd $A && sha256sum $f >> SHA256SUMS); done
  cp /t/connect-stage.sh /t/c.sh
  sed -i "s/^CV_SHA=.*/CV_SHA=$(sha256sum $CFS/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root | cut -c1-64)/" /t/c.sh
  [ "$1" = sums ] || sed -i "s/^LAT_SUMS_SHA=.*/LAT_SUMS_SHA=$(sha256sum $A/SHA256SUMS | cut -c1-64)/" /t/c.sh
  while read -r h f; do lat=${f#runEventLoopOmniFold_5D_MEFHC_active_}; lat=${lat%.root}
    [ "$1" = partb ] && [ "$lat" = MuonResolution_1 ] && h=$(printf '%064d' 0)
    sed -i "s/^  \[$lat\]=[0-9a-f]*/  [$lat]=$h/" /t/c.sh; done < $A/SHA256SUMS
}
run() { PATH=/stub:$PATH bash /t/c.sh; echo "rc=$?"; L=/pscratch/sd/j/josephrb/cov2d-inputs-20261104/stage
  grep -E "^STOP|^STAGE|projected|manifest:|SHA256SUMS sha256|STAGE PASS|copies" $L/connect-stage.log | cut -c1-140
  [ -f $L/inputs.stat ] && echo "record rows=$(grep -c . $L/inputs.stat) perms=$(stat -c %a $L/inputs.stat) laterals_ro=$(stat -c %a /pscratch/sd/j/josephrb/cov2d-inputs-20261104/laterals/* | sort -u | tr '\n' ' ')"; }
echo "### A: everything agrees, quota 50 %"; mkbin 500000000; setup ok; run
echo "### B: quota at 89.99 % before staging"; mkbin 899990000; setup ok; run
echo "### C: SHA256SUMS not the pinned file"; mkbin 500000000; setup sums; run
echo "### D: SHA256SUMS disagrees with part B on one lateral"; mkbin 500000000; setup partb; run
echo "### F: quota projected 89.99 % (just under)"; mkbin 899900000; setup ok; run
echo "### E: rerun into an existing directory"; mkbin 500000000; PATH=/stub:$PATH bash /t/c.sh; echo "rc=$?"
