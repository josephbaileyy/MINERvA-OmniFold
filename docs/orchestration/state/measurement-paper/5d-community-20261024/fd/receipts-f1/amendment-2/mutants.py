"""F1 amendment 2: planted defects in the single-wave gate, its launcher and the f1b3 submission stage, each run
against nd-unfolding/tests/test_fd_f1_amend2.py in place, one at a time, the file restored (sha256 checked) after each.
Usage: python3 -I -B mutants.py <repo root> [ids...]"""
import hashlib, os, subprocess, sys
from pathlib import Path
R = Path(sys.argv[1]).resolve()
B, L, S = "nd-unfolding/fd_f1_budget3.py", "nd-unfolding/sbatch_fd_f1b3.sh", "nd-unfolding/submit_fd_f1.sh"
MUTANTS = [
    (1, B, "task = load + N_EVENTS * t", "task = load + B2.N_TASK * t"),
    (2, B, 't = max(v["per_event_s_descriptive"]', 't = min(v["per_event_s_descriptive"]'),
    (3, B, 'load = max(v["load_s_descriptive"]', 'load = min(v["load_s_descriptive"]'),
    (4, B, "wall = WAVES * task + FIXED_S", "wall = WAVES * task"),
    (5, B, 'mem = P * max(v["max_rss_kib"]', 'mem = max(v["max_rss_kib"]'),
    (6, B, "mem_ok = mem <= MEM_FRACTION * NODE_MEM_KIB", "mem_ok = mem <= NODE_MEM_KIB"),
    (7, B, "go = mem_ok and fits and within and capped", "go = fits and within and capped"),
    (8, B, "go = mem_ok and fits and within and capped", "go = mem_ok and within and capped"),
    (9, B, "go = mem_ok and fits and within and capped", "go = mem_ok and fits and capped"),
    (10, B, "go = mem_ok and fits and within and capped", "go = mem_ok and fits and within"),
    (11, B, "limit_min = int(-(-(wall * WALL_MARGIN) // 60))", "limit_min = int(wall // 60)"),
    (12, B, "total = spent_node_h + wall / 3600.0 + F1C_NODE_H", "total = spent_node_h + wall / 3600.0"),
    (13, B, "worst = spent_node_h + limit_min / 60.0 + F1C_LIMIT_H", "worst = spent_node_h + limit_min / 60.0"),
    (14, B, "SPENT_NODE_H = 0.408333", "SPENT_NODE_H = 0.307500"),
    (15, B, "F1B_MAX_S = 57 * 60", "F1B_MAX_S = 90 * 60"),
    (16, B, "TIMEOUT_FACTOR = 3.0", "TIMEOUT_FACTOR = 30.0"),
    (17, B, "return list(range(b + 1, b + 1 + N_TASKS_PER_TUNE))", "return list(range(b, b + N_TASKS_PER_TUNE))"),
    (18, B, "N_EVENTS = 160_000", "N_EVENTS = 17_500"),
    (19, B, "if not sums.is_file() or sha256(sums) != sums_sha256:", "if not sums.is_file():"),
    (20, B, "        if sha256(root / rel) != h:", "        if False:"),
    (21, B, "    if sorted(listed) != on_disk:", "    if False:"),
    (22, B, "if not (t > 0 and load > 0):", "if False:"),
    (23, B, 'with open(a.out, "x") as f:', 'with open(a.out, "w") as f:'),
    (24, B, 'return 0 if d["decision"] == "GO" else 3', "return 0"),
    (25, L, '[ "$P" = 14 ]', '[ "$P" -gt 0 ]'),
    (26, L, 'F="$OUT/f1b3"', 'F="$OUT/f1b"'),
    (27, L, "2>&1 || exit 255' < \"$F/queue.txt\"", "2>&1' < \"$F/queue.txt\""),
    (28, L, 'task_s$1.time" timeout "$TO"', 'task_s$1.time"'),
    (29, L, "NT=7; NEV=160000", "NT=7; NEV=17500"),
    (30, L, "declare -A BASE=([G18_10a_02_11b]=60000 [AR23_20i_00_000]=61000)", "declare -A BASE=([G18_10a_02_11b]=60100 [AR23_20i_00_000]=61100)"),
    (31, L, '[ ! -e "$F" ] || { echo "[f1b3] refusing: $F exists" >&2; exit 2; }', 'true'),
    (32, L, "grep -q '\"decision\": \"GO\"' \"$B3\" 2>/dev/null ||", "true ||"),
    (33, L, '[ -n "$TO" ] && [ "$TO" -gt 0 ] ||', 'true ||'),
    (34, L, 'if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then', 'if false; then'),
    (35, S, '[ "$S" = "FAILED|3:0" ] ||', 'true ||'),
    (36, S, '[ "$K" -gt 0 ] && [ "$K" -le $((487802 * 1024 * 3 / 4)) ] || { echo "refusing: re-pilot batch MaxRSS $R exceeds 75 % of the node" >&2; exit 2; }\n    mkdir "$OUT/gate3"', '[ "$K" -ge 0 ] || exit 2\n    mkdir "$OUT/gate3"'),
    (37, S, '[ ! -e "$OUT/gate3" ] && [ ! -e "$OUT/f1b3" ] ||', 'true ||'),
    (38, S, '--priced-node-h "$PRICED" --ceiling-node-h "$CEIL" --out "$B"', '--priced-node-h "$CEIL" --ceiling-node-h "$CEIL" --out "$B"'),
    (39, S, '--time="$T" --job-name=fd_f1b3', '--time=02:00:00 --job-name=fd_f1b3'),
    (41, L, '> "$F/f1b3-SHA256SUMS"\nneed $? "the sums file"', '> "$F/f1b3-SHA256SUMS"'),
    (42, L, '( cd "$A" && sha256sum -c "$A2/reused.sha256" ) > /dev/null 2>&1 ||', 'true ||'),
    (40, S, '|| { cat "$OUT/gate3/budget3.log" >&2; echo "refusing: $B is not GO" >&2; exit 2; }\n    grep -q \'"decision": "GO"\' "$B" ||', '|| true\n    true ||'),
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
        p = subprocess.run([sys.executable, "-I", "-B", str(R / "nd-unfolding/tests/test_fd_f1_amend2.py")],
                           capture_output=True, text=True, timeout=600, env=os.environ)
    finally:
        f.write_bytes(orig)
    assert hashlib.sha256(f.read_bytes()).hexdigest() == sha, f"{rel} not restored"
    (killed if p.returncode else survived).append(mid)
    print(mid, "KILLED" if p.returncode else "SURVIVED", rel, repr(old[:60]), flush=True)
print("total", len(killed) + len(survived), "killed", len(killed), "survived", survived)
