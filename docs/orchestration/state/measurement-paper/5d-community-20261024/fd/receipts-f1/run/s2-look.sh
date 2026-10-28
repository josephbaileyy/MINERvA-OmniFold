OUT=/pscratch/sd/j/josephrb/fd-f1-20261027; F=$OUT/f1a
sacct -X -P -j 60415571 -o JobID,JobName,State,ExitCode,Start,End,Elapsed,Timelimit,AllocTRES%60
ls $OUT/logs; tail -20 $OUT/logs/fd_f1a_60415571.out
cat $F/budget.json
cat $F/logs/flux_check.log; tail -3 $F/logs/flux_and_splines.log
for T in G18_10a_02_11b AR23_20i_00_000; do echo "== $T"; cat $F/spline_check_$T.json | head -30; tail -2 $F/logs/convert_$T.log; cat $F/pilot/wall_$T.txt; done
