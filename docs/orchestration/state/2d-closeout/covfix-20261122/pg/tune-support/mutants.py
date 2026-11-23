"""Hand mutants of COVFIX PG's tune support: each must make nd-unfolding/tests/test_covfix_pg.py fail.

Run: python3 -B mutants.py > mutants.log   (from this directory). Each mutant runs in a throwaway copy of the files
the suite reads; nothing here is edited.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[7]
PROBE = "docs/orchestration/state/2d-closeout/covfix-20261122/pg/probe"
G, N = "3d-unfolding/genie", "nd-unfolding"
M = [  # (file, old, new, what it breaks)
    (f"{G}/pg_lib.py", "if any(b - a != 1 for a, b in zip(s, s[1:])):", "if False:", "consecutive seeds"),
    (f"{G}/pg_lib.py", "if out[1][2][0] - out[0][2][0] != U_STRIDE:", "if False:", "u stride"),
    (f"{G}/pg_lib.py", "if any(x >= SEED_CEIL for x in s):", "if any(x > SEED_CEIL for x in s):", "seed ceiling"),
    (f"{G}/pg_lib.py", "if not BASE_LO <= out[0][2][0] < BASE_HI:", "if not BASE_LO <= out[0][2][0]:", "base range"),
    (f"{G}/pg_lib.py", "return isinstance(x, int) and not isinstance(x, bool)", "return isinstance(x, int)",
     "bool seeds"),
    (f"{G}/pg_lib.py", 'raise Refusal(f"u{u}\'s task seeds are not consecutive (base + 10000 u + task index)")',
     'raise Refusal(f"u{u}\'s task seeds {s} are not consecutive")', "a refusal prints the seeds"),
    (f"{G}/pg_lib.py", "    if out[1][1] not in U1:", "    if out[1][1] in ():", "u1 tune set"),
    (f"{G}/pg_lib.py", "    if os.path.exists(a.out):\n", "    if False:\n", "queue overwrite"),
    (f"{G}/pg_lib.py", 'f"{name} {s} u{u}/t{k}\\n"', 'f"{name} {s} u{u}/s{s}\\n"', "seed in the work-dir name"),
    (f"{G}/pg_lib.py", '            if not (Path(workdir) / p[k]).is_file():', '            if False:',
     "products existence"),
    (f"{G}/pg_generate.sh", 'NT=7; NEV=160000; P=14; TO=5115', 'NT=7; NEV=17500; P=14; TO=5115', "events per task"),
    (f"{G}/pg_generate.sh", '[ "$TMPDIR" = "$W/tmp" ] && [ -d "$TMPDIR" ] ||', 'true ||', "TMPDIR check"),
    (f"{G}/pg_generate.sh", '[ "$(cd "$W" && pwd -P)" = "$(pwd -P)" ] ||', 'true ||', "cwd check"),
    (f"{G}/pg_generate.sh", '[ "$head_sha" = "$PG_DEPLOY_PIN" ] && [ "$dirty" -eq 0 ] ||', '[ "$dirty" -eq 0 ] ||',
     "pin check"),
    (f"{G}/pg_generate.sh", 'for d in out run PRODUCTS.json; do', 'for d in out run; do', "PRODUCTS.json overwrite"),
    (f"{G}/pg_generate.sh", '  export TMPDIR="$W/tmp" PYTHONDONTWRITEBYTECODE=1\n', '', "TMPDIR re-export"),
    (f"{G}/pg_generate.sh", 'mv -f "$f" "$d/gevgen.status"', 'true', "status rename"),
    (f"{G}/pg_generate.sh", 'mv -f "$f" "$d/gntp.ghep.root"', 'true', "leftover GHEP rename"),
    (f"{G}/pg_generate.sh", 'rc=$?; seedfree "$O/work/$2"; [ "$rc"', 'rc=$?; [ "$rc"', "per-task rename"),
    (f"{G}/pg_generate.sh", 'trap cleanup EXIT\n', '', "no cleanup on a STOP"),
    (f"{G}/pg_generate.sh", "find . -type f ! -path './logs/*'", "find gst gen5d prep work splines -type f ! -path './logs/*'",
     "sums omit top-level products"),
    (f"{G}/pg_generate.sh", 'for u in 0 1; do   # every tune', 'for u in; do   # every tune', "counts after conversions start"),
    (f"{G}/pg_generate.sh", 'deploy_unchanged after\n', '', "final deploy check"),
    (f"{G}/pg_generate.sh", '--truth-set pg "${args[@]}"', '"${args[@]}"', "prep truth set"),
    (f"{G}/pg_generate.sh", '    G18_02b_02_11b) N=genie_v3_g18_02b ;;', '    G18_02b_02_11b) N=genie_v3_g18 ;;',
     "truth name map"),
    (f"{G}/pg_generate.sh", 'need $? "the sampled-spectrum check (NOWIDTH)"', 'true', "flux-check rc ignored"),
    (f"{G}/pg_generate.sh", '> "$O/work/$2/task.log" 2>&1; rc=$?', '; rc=$?', "task output not in task.log"),
    (f"{G}/pg_generate.sh", 'echo "[pg] STOP: $2 rc=$1"; exit 1;', 'echo "[pg] STOP: $2 rc=$1"; exit 0;', "STOP exit"),
    (f"{G}/run_gevgen_v3.sh", "      G18_02a_02_11b)  Q=G1802a0211b-k250-e1000 ;;\n", "", "reduce qualifier"),
    (f"{G}/setup_genie_v3.sh", "G21_11b_00_000)  export GENIE_XSEC_QUAL=G2111b00000:k250:e1000",
     "G21_11b_00_000)  export GENIE_XSEC_QUAL=G2111b00000-k250-e1000", "setup qualifier"),
    (f"{G}/gen5d_v3.py", '        bad.append(f"no pinned spline file, README or version line for {a.tune}")\n', '',
     "unpinned tune accepted"),
    (f"{G}/gen5d_v3.py", '"G18_02a_02_11b": "GENIE v3.04.00 G18_02a_02_11b (genie_xsec v3_04_00 G1802a0211b-k250-e1000)"',
     '"G18_02a_02_11b": "GENIE v3.04.00 G18_02a_02_11b"', "label qualifier"),
    (f"{N}/fd_f1_prep.py", "if len(preds) != 2 or PG_U0 not in preds or len(set(preds) & set(PG_U1)) != 1:",
     "if PG_U0 not in preds:", "PG truth-set check"),
    (f"{N}/fd_f1_prep.py", '    cfg_path = a.out / f"config-{a.truth_set}.json"', '    cfg_path = a.out / "config-f1.json"',
     "config name"),
    (f"{N}/fd_f1_prep.py", "    for name in sorted(preds):", "    for name in sorted(TRUTHS):", "bridge loop"),
]


def sandbox():
    tmp = Path(tempfile.mkdtemp(prefix="pg-mut-"))
    shutil.copytree(REPO / G, tmp / G)
    shutil.copytree(REPO / N / "pv-ladder", tmp / N / "pv-ladder")
    for p in (REPO / N).iterdir():
        if p.is_file() and p.suffix in (".py", ".sh"):
            shutil.copy(p, tmp / N / p.name)
    (tmp / N / "tests").mkdir()
    for n in ("test_covfix_pg.py", "conftest.py"):
        shutil.copy(REPO / N / "tests" / n, tmp / N / "tests" / n)
    shutil.copytree(REPO / PROBE, tmp / PROBE)
    return tmp


def run(tmp):
    return subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider",
                           f"{N}/tests/test_covfix_pg.py"], cwd=tmp, capture_output=True, text=True)


def main():
    tmp = sandbox()
    try:
        base = run(tmp)
        print(f"unmutated: rc {base.returncode} ({base.stdout.strip().splitlines()[-1]})")
        if base.returncode:
            return 1
    finally:
        shutil.rmtree(tmp)
    killed = 0
    for i, (f, old, new, what) in enumerate(M, 1):
        tmp = sandbox()
        try:
            src = (tmp / f).read_text()
            if src.count(old) != 1:
                print(f"M{i:02d} NOT-APPLICABLE ({src.count(old)} matches): {what}")
                continue
            (tmp / f).write_text(src.replace(old, new))
            ok = run(tmp).returncode != 0
            killed += ok
            print(f"M{i:02d} {'KILLED' if ok else 'SURVIVED'}: {what} [{f}]")
        finally:
            shutil.rmtree(tmp)
    print(f"{killed} of {len(M)} killed")
    return 0 if killed == len(M) else 1


if __name__ == "__main__":
    raise SystemExit(main())
