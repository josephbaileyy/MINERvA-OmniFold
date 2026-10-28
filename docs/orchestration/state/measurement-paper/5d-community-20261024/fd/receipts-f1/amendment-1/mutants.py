"""F1 amendment 1: planted defects in the re-pilot gate and the new scripts, each run against
nd-unfolding/tests/test_fd_f1_amend.py in place, one at a time, the file restored (sha256 checked) after each.
Usage: python3 -I -B mutants.py <repo root> [ids...]"""
import hashlib, subprocess, sys
from pathlib import Path
R = Path(sys.argv[1]).resolve()
B, A, BB, S = ("nd-unfolding/fd_f1_budget2.py", "nd-unfolding/sbatch_fd_f1a2.sh", "nd-unfolding/sbatch_fd_f1b2.sh",
               "nd-unfolding/submit_fd_f1.sh")
MUTANTS = [
    (1, B, "wall = WAVES * max(", "wall = max("),
    (2, B, 'mem = P * max(v["max_rss_kib"]', 'mem = max(v["max_rss_kib"]'),
    (3, B, '"max_rss_kib": max(x["maxrss_kib"] for x in r["long"] + r["short"])', '"max_rss_kib": max(x["maxrss_kib"] for x in r["long"])'),
    (4, B, "mem_ok = mem <= MEM_FRACTION * NODE_MEM_KIB", "mem_ok = mem <= NODE_MEM_KIB"),
    (5, B, "go = mem_ok and fits and within and capped", "go = fits and within and capped"),
    (6, B, "go = mem_ok and fits and within and capped", "go = mem_ok and within and capped"),
    (7, B, "go = mem_ok and fits and within and capped", "go = mem_ok and fits and capped"),
    (8, B, "go = mem_ok and fits and within and capped", "go = mem_ok and fits and within"),
    (9, B, "limit_min = int(-(-(wall * WALL_MARGIN) // 60))", "limit_min = int(wall // 60)"),
    (10, B, 'if r["exit"] != 0:', "if False:"),
    (11, B, "        if extra:", "        if False:"),
    (12, B, '"long": list(range(b + 1, b + 1 + N_LONG))', '"long": list(range(b, b + N_LONG))'),
    (13, B, "return parts[0] * 60 + parts[1]", "return parts[0] + parts[1]"),
    (14, B, "P = 16 ", "P = 64 "),
    (15, B, "F1B_MAX_S = 55 * 60", "F1B_MAX_S = 90 * 60"),
    (16, B, 'd["repilot_job_id"] = a.job_id', "pass"),
    (17, A, 'run "$T" long 17500 "$s"', 'run "$T" long 3000 "$s"'),
    (18, A, "SPENT=0.307500", "SPENT=0.104722"),
    (19, A, "declare -A BASE2=([G18_10a_02_11b]=60100 [AR23_20i_00_000]=61100)", "declare -A BASE2=([G18_10a_02_11b]=60000 [AR23_20i_00_000]=61000)"),
    (20, A, "graphs_[A-Za-z0-9_]+\\.root)$'", "graphs_[A-Za-z0-9_]+\\.(root|log))$'"),
    (21, A, '--job-id "$SLURM_JOB_ID"', '--job-id 0'),
    (22, BB, '[ "$P" = 16 ]', '[ "$P" -gt 0 ]'),
    (23, BB, 'F="$OUT/f1b2"', 'F="$OUT/f1b"'),
    (24, BB, "2>&1 || exit 255' < \"$F/queue.txt\"", "2>&1' < \"$F/queue.txt\""),
    (25, S, '--time=00:20:00 --job-name=fd_f1a2', '--time=00:40:00 --job-name=fd_f1a2'),
    (26, S, '"$OUT" "$PRICED" "$CEIL" ;;', '"$OUT" "$PRICED" "$PRICED" ;;'),
    (27, S, '[ "$K" -gt 0 ] && [ "$K" -le $((487802 * 1024 * 3 / 4)) ]', '[ "$K" -ge 0 ]'),
    (28, S, '[ -n "$J" ] || { echo "refusing: no repilot_job_id in $B" >&2; exit 2; }', 'true'),
    (29, S, 'if(u=="G")n*=1048576', 'if(u=="G")n*=1'),
]
ONLY = {int(x) for x in sys.argv[2:]}
killed, survived = [], []
for mid, rel, old, new in MUTANTS:
    if ONLY and mid not in ONLY:
        continue
    f = R / rel
    orig = f.read_bytes(); sha = hashlib.sha256(orig).hexdigest(); text = orig.decode()
    if text.count(old) != 1:
        print(mid, "NOT APPLICABLE", rel, flush=True); survived.append(mid); continue
    try:
        f.write_text(text.replace(old, new, 1))
        p = subprocess.run([sys.executable, "-I", "-B", str(R / "nd-unfolding/tests/test_fd_f1_amend.py")],
                           capture_output=True, text=True, timeout=600)
    finally:
        f.write_bytes(orig)
    assert hashlib.sha256(f.read_bytes()).hexdigest() == sha, f"{rel} not restored"
    (killed if p.returncode else survived).append(mid)
    print(mid, "KILLED" if p.returncode else "SURVIVED", rel, repr(old[:60]), flush=True)
print("total", len(killed) + len(survived), "killed", len(killed), "survived", survived)
