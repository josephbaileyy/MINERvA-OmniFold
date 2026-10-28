OUT=/pscratch/sd/j/josephrb/fd-f1-20261027; F=$OUT/f1b
sacct -P -j 60417614 -o JobID,JobName,State,ExitCode,Start,End,Elapsed,MaxRSS,AllocTRES%70,ReqMem
echo "== job log"; cat $OUT/logs/fd_f1b_60417614.out
echo "== f1b dir"; ls $F $F/logs 2>/dev/null | head -40; ls $F/gst $F/gen5d 2>/dev/null
echo "== gst counts"; for T in G18_10a_02_11b AR23_20i_00_000; do echo "$T $(ls $F/work/$T/s*/genie_v3.gst.root 2>/dev/null | wc -l) gst, $(ls -d $F/work/$T/s* 2>/dev/null | wc -l) dirs"; done
echo "== flux check"; cat $F/logs/flux_check.log 2>/dev/null
for T in G18_10a_02_11b AR23_20i_00_000; do echo "== hadd/convert $T"; tail -5 $F/logs/hadd_$T.log 2>/dev/null; tail -15 $F/logs/convert_$T.log 2>/dev/null; done
echo "== a gen log"; tail -5 $F/logs/gen_G18_10a_02_11b_s60001.log 2>/dev/null; grep -l -i "kill\|memory\|error" $F/logs/gen_* 2>/dev/null | head
du -sh $F/work $F/gst 2>/dev/null; ls -la $F/gst 2>/dev/null
