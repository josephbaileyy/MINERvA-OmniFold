"""Join local stat and remote `xrdfs ls -l` listings by basename; print per-playlist size agreement."""
import os, sys, collections
OUT = sys.argv[1]
tot = collections.Counter()
for p in "1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P".split():
    rem = {}
    for line in open(os.path.join(OUT, f"remote_ls_{p}.txt")):
        f = line.split()
        if len(f) >= 5 and f[-1].endswith(".root"):
            rem[os.path.basename(f[-1])] = (int(f[3]), f[1] + " " + f[2])
    loc = {}
    for line in open(os.path.join(OUT, f"local_stat_{p}.txt")):
        f = line.split()
        loc[os.path.basename(f[0])] = (int(f[1]), f[2])
    same = [n for n in loc if n in rem and rem[n][0] == loc[n][0]]
    diff = [n for n in loc if n in rem and rem[n][0] != loc[n][0]]
    ratios = [rem[n][0] / loc[n][0] for n in diff]
    rmt = sorted({rem[n][1][:10] for n in rem}); lmt = sorted({loc[n][1] for n in loc})
    print(f"{p}: local={len(loc)} remote={len(rem)} only_local={len(set(loc)-set(rem))} only_remote={len(set(rem)-set(loc))} "
          f"same_size={len(same)} diff_size={len(diff)} ratio_min={min(ratios) if ratios else None} ratio_max={max(ratios) if ratios else None} "
          f"remote_mtime_dates={rmt[0] if rmt else None}..{rmt[-1] if rmt else None} local_mtime_dates={lmt[0]}..{lmt[-1]}")
    tot.update(local=len(loc), same=len(same), diff=len(diff))
print("TOTAL", dict(tot))
