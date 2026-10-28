set -u
P=/pscratch/sd/j/josephrb
echo "host=$(hostname) date=$(date -u +%FT%TZ)"
echo "== atime, oldest per group (purge is by access age)"
for g in "$P/MINERvA-OmniFold/nd-unfolding/runEventLoopOmniFold_5D_*_universes_full_bkgaware.root" "$P/measurement-paper/phase1/mp1/s1/evloop/*/*.root" "$P/measurement-paper/phase1/mp1/s1/merged/*" "$P/measurement-paper/phase1/mp1/s1/lateral/*" "$P/measurement-paper/phase1/mp1/s1/unf/*" "$P/w2-recoil-20261006/w2b/evloop/*/*" "$P/w2-recoil-20261006/w2b/merged/*" "$P/w2-recoil-20261006/w2b/lateral/*" "$P/w2-recoil-20261006/w2b/unf/*" "$P/tmp-playlist-term-20261016/out/*" "$P/s5p-20260926/runs/prod/cal" ; do
  n=$(ls -d $g 2>/dev/null | wc -l); oldest=$(stat -c '%X %x %n' $g 2>/dev/null | sort -n | head -1 | cut -d' ' -f2-); echo "$n files | oldest atime: $oldest"
done
echo "== du (apparent) per group"
du -sh --apparent-size $P/measurement-paper/phase1/mp1/s1/{evloop,merged,lateral,unf} $P/w2-recoil-20261006/w2b/{evloop,merged,lateral,unf} 2>&1
echo "== HPSS recursive names, filtered"
hsi -q "ls -R /home/j/josephrb" 2>&1 | grep -i -E 'mp1|w2b|w2-|universes|playlist|s5p-archive|lat_|zero|^/home' | head -60
