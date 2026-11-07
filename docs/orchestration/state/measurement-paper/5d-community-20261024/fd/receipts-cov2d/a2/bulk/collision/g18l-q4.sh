O=/pscratch/sd/j/josephrb/cov2d-run-20261104
for p in 'walls.G18_U*' 'walls.AR23_U*' 'walls.G18_B*' 'walls.AR23_B*' 'walls.G18_T*' 'walls.AR23_T*' 'walls.G18_L*' 'walls.AR23_L*' 'walls.pilot*'; do
  cat $O/$p 2>/dev/null | awk -v p="$p" -F'\t' '{d=$3-$2; n++; s+=d; if(d>mx)mx=d; if(mn==""||d<mn)mn=d; if($4!=0)bad++} END {printf "%-16s n=%d mean=%.0f min=%d max=%d bad=%d\n", p, n, s/n, mn, mx, bad+0}'
done
grep -P '^(X_G18|L_G18_BeamAngleX_0|U_G18_Flux_0|B_G18_001|T_G18_5720000)\t' $O/walls.pilot.*.tsv
echo "== job start to first run (preflight+check), from logs"
for f in $O/logs/cov2d-G18_L-60895948.out $O/logs/cov2d-G18_Ua-60895562.out $O/logs/cov2d-G18_Ba-60895949.out $O/logs/cov2d-G18_Ta-60895956.out; do echo "$(basename $f) $(grep -m1 -o 'start [0-9T:-]*Z' $f)"; done
sacct -X -n -P -j 60895948,60895562,60895949,60895956 -o JobID,Start
ls -la $O/inputs 2>/dev/null | head -2; stat -c '%s %n' /pscratch/sd/j/josephrb/cov2d-inputs-20261104/runEventLoopOmniFold_MEFHC.root /pscratch/sd/j/josephrb/cov2d-inputs-20261104/laterals/runEventLoopOmniFold_5D_MEFHC_active_BeamAngleX_0.root
