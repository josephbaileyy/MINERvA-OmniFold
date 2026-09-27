"""Hold the row flocks of withdrawn rows (stopped X4 arm; H2S1 K5 final-bank rows withdrawn by Amendments 3c/3d)
so that lanes still carrying older priority lists skip them. Runs on a login node; releases on exit."""
import fcntl, glob, os, sys, time
B = "/pscratch/sd/j/josephrb/pet-final-design-20260925"
M = sys.argv[1]; hours = float(sys.argv[2])
rows = []
def names(manifest, pred=lambda n: True):
    for line in open(f"{M}/nd-unfolding/pet/final_design/runs/{manifest}"):
        if line.startswith("#") or not line.strip(): continue
        n = line.split("\t")[0]
        if pred(n): yield n
rows += [(f"{B}/dev3X", n) for n in names("dev3X.tsv")]
rows += [(f"{B}/s3p", n) for n in names("s3x.tsv")]
rows += [(f"{B}/s4f", n) for n in names("s4f_a2.tsv", lambda n: "-H2S1K5-" in n)]
rows += [(f"{B}/s4s", n) for n in names("s4s_a2.tsv", lambda n: "-H2S1K5-" in n)]
held, skipped = [], []
for out, n in rows:
    d = f"{out}/{n}"
    if open(f"{d}/status.txt").read().strip() == "COMPLETE" if os.path.exists(f"{d}/status.txt") else False:
        continue
    os.makedirs(d, exist_ok=True)
    fd = os.open(f"{d}/.flock", os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o660)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB); held.append(n)
    except BlockingIOError:
        os.close(fd); skipped.append(n)      # a job holds it now (running); leave it
print(f"held {len(held)} rows, {len(skipped)} busy (left alone)", flush=True)
with open(f"{B}/withdrawn_rows_held.txt", "w") as f:
    f.write("\n".join(held) + "\n")
time.sleep(hours * 3600)
