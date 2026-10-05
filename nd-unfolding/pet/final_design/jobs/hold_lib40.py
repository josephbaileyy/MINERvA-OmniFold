"""Hold the row flocks of the released-but-unused library rows (D4c up / D3 +0.35 draws 40-59; Amendment 3f) so
lanes launched with the full s4s_a3e list skip them. Releases on exit."""
import fcntl, os, re, sys, time
B = "/pscratch/sd/j/josephrb/pet-final-design-20260925"; M = sys.argv[1]; hours = float(sys.argv[2])
held = []
for line in open(f"{M}/nd-unfolding/pet/final_design/runs/s4s_a3e.tsv"):
    if line.startswith("#") or not line.strip(): continue
    n = line.split("\t")[0]
    if int(re.search(r"-FB(\d+)-", n).group(1)) < 40: continue
    d = f"{B}/s4s/{n}"; os.makedirs(d, exist_ok=True)
    fd = os.open(f"{d}/.flock", os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o660)
    try: fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB); held.append(n)
    except BlockingIOError: os.close(fd)
print(f"held {len(held)}", flush=True); time.sleep(hours * 3600)
