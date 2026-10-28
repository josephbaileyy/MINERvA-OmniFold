G=/cvmfs/larsoft.opensciencegrid.org/products/genie/v3_04_00
ls $G | head; SRC=$(ls -d $G/source* $G/src 2>/dev/null | head -1); echo SRC=$SRC
F=$(find $G -name gEvGen.cxx 2>/dev/null | head -1); echo F=$F
[ -n "$F" ] && grep -n "NOWIDTH\|Width\|width" "$F" | head -20
C=$(find $G -maxdepth 4 -type d -name AR23_20i 2>/dev/null | head -1); echo C=$C
ls $C | head; grep -rhoiE "Nieves[A-Za-z]*|SuSAv2[A-Za-z]*|ZExp[A-Za-z]*" $C 2>/dev/null | sort | uniq -c | head -20
C2=$(find $G -maxdepth 4 -type d -name G18_10a 2>/dev/null | head -1); echo C2=$C2
grep -rhoiE "Nieves[A-Za-z]*|SuSAv2[A-Za-z]*|ZExp[A-Za-z]*|Empirical[A-Za-z]*" $C2 2>/dev/null | sort | uniq -c | head -20
