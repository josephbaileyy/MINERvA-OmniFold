"""F1 amendment 1: planted defects in the re-pilot gate and the new scripts, each run against
nd-unfolding/tests/test_fd_f1_amend.py in place, one at a time, the file restored (sha256 checked) after each.
Usage: python3 -I -B mutants.py <repo root> [ids...]"""
import hashlib, subprocess, sys
from pathlib import Path
R = Path(sys.argv[1]).resolve()
B, A, BB, S = ("nd-unfolding/fd_f1_budget2.py", "nd-unfolding/sbatch_fd_f1a2.sh", "nd-unfolding/sbatch_fd_f1b2.sh",
               "nd-unfolding/submit_fd_f1.sh")
MUTANTS = [
    (1, B, "t = (long_w - short_w) / (N2 - N1)", "t = long_w / N2"),
    (2, B, "load = short_w - N1 * t", "load = 0.0"),
    (3, B, '"task_wall_s": load + N_TASK * t', '"task_wall_s": N_TASK * t'),
    (4, B, "max(0.0, slope) * (N_TASK - N2)", "0.0 * (N_TASK - N2)"),
    (5, B, "fit_ok\": bool(t > 0 and load >= 0)", "fit_ok\": bool(t > 0)"),
    (6, B, "mem = P * max(", "mem = max("),
    (7, B, "mem_ok = mem <= MEM_FRACTION * NODE_MEM_KIB", "mem_ok = mem <= NODE_MEM_KIB"),
    (8, B, "wall = WAVES * max(", "wall = max("),
    (9, B, "go = fit_ok and mem_ok and fits and within and capped", "go = fit_ok and fits and within and capped"),
    (10, B, "capped = worst <= ceiling_node_h", "capped = True"),
    (11, B, "within = total <= priced_node_h", "within = True"),
    (12, B, "limit_min = int(-(-(wall * WALL_MARGIN) // 60))", "limit_min = int(wall // 60)"),
    (13, B, 'if r["exit"] != 0:', "if False:"),
    (14, B, "        if extra:", "        if False:"),
    (15, B, "longs = list(range(b + 1, b + 1 + N_LONG))", "longs = list(range(b, b + N_LONG))"),
    (16, B, 'return parts[0] * 60 + parts[1]', 'return parts[0] + parts[1]'),
    (17, A, 'run "$T" long 3000 "$s"', 'run "$T" long 2000 "$s"'),
    (18, A, "SPENT=0.307500", "SPENT=0.104722"),
    (19, A, "declare -A BASE2=([G18_10a_02_11b]=60100 [AR23_20i_00_000]=61100)", "declare -A BASE2=([G18_10a_02_11b]=60000 [AR23_20i_00_000]=61000)"),
    (20, A, "graphs_[A-Za-z0-9_]+\\.root)$'", "graphs_[A-Za-z0-9_]+\\.(root|log))$'"),
    (21, BB, '[ "$P" = 64 ]', '[ "$P" -gt 0 ]'),
    (22, BB, 'F="$OUT/f1b2"', 'F="$OUT/f1b"'),
    (23, S, '--time=00:20:00 --job-name=fd_f1a2', '--time=00:40:00 --job-name=fd_f1a2'),
    (24, S, '"$OUT" "$PRICED" "$CEIL" ;;', '"$OUT" "$PRICED" "$PRICED" ;;'),
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
