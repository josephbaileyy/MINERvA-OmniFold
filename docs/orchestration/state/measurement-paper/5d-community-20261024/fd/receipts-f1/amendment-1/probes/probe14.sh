G=/cvmfs/larsoft.opensciencegrid.org/products/genie/v3_04_00/Linux64bit+3.10-2.17-e20-prof/GENIE-Generator
echo "== sacct F1a steps"; sacct -P -j 60415571 -o JobID,State,Elapsed,MaxRSS,MaxRSSTask,NTasks
echo "== FindConfig (the WARN's source)"; sed -n 140,175p $G/src/Framework/Algorithm/Algorithm.cxx
echo "== who configures EventGeneratorListAssembler"; grep -rn "EventGeneratorListAssembler" $G/src --include=*.cxx | head -20
echo "== tune generator lists"
for t in G18_10a/G18_10a_02_11b AR23_20i; do echo "--- $t"; ls $G/config/$t; done
for f in $G/config/G18_10a/TuneGeneratorList.xml $G/config/AR23_20i/TuneGeneratorList.xml $G/config/TuneGeneratorList.xml $G/config/EventGeneratorListAssembler.xml; do echo "--- $f"; [ -f $f ] && grep -v "^\s*$" $f | head -80; done
ls $G/config/G18_10a/; ls $G/config/G18_10a/G18_10a_02_11b
