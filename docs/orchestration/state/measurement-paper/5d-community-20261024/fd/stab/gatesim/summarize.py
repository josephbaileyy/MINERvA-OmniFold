"""Per (noise, alpha, B2 factor): outcomes of sweep.txt's seeds. A stop within the first 16 queue lines is EARLY, a
later one MIDRUN; SLURM is a run that met Slurm's limit. Prints the largest spend of a mid-run stop and of an early one."""
import collections
import sys

agg = collections.defaultdict(list)
for line in open(sys.argv[1]):
    r = line.split()
    out, spent = r[7], float(r[8].split("=")[1])
    if out.startswith("STOP@"):
        out = "EARLY" if int(out[5:].split("/")[0]) <= 16 else "MIDRUN"
    agg[tuple(r[:3])].append((out.replace("SLURM_KILL", "SLURM"), spent))
print("noise alpha B2  outcomes  max mid-run spend")
for k, v in sorted(agg.items(), key=lambda kv: tuple(map(float, kv[0]))):
    c = collections.Counter(o for o, _ in v)
    mid = max((s for o, s in v if o == "MIDRUN"), default=None)
    print(*k, dict(sorted(c.items())), "" if mid is None else f"{mid:.2f}")
early = [s for v in agg.values() for o, s in v if o == "EARLY"]
print(f"largest early-stop spend: {max(early):.2f} over {len(early)} early stops")
