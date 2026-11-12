#!/usr/bin/env python3
"""Mutation check of RDX's launcher-tranche tests (test_rdx_stages.py), with rdx_mutation.py's harness.

Each mutation plants one declared defect in a copy of one tranche-2 file and must make the NAMED test fail. Exit 0 only
if the unmutated suite passes with the expected test count and every mutation is killed by its named test.

    python3 -B nd-unfolding/rdx/rdx_mutation_stages.py [--only LABEL_SUBSTRING] [--jobs N]
"""
import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ND = HERE.parent
REPO = ND.parent
FILES = ("rdx_cap.py", "rdx_merge.py", "rdx_paths.py", "sbatch_rdx_evloop.sh", "sbatch_rdx_merge.sh", "sbatch_rdx_arms.sh",
         "rdx_connect.sh", "rdx_connect_launch.sh", "rdx_tasks.tsv", "rdx_common.py", "rdx_dump.py", "test_rdx_stages.py")
CP, MG, PA, EV, SM, AR, CN, LA, TT = FILES[:9]
EXPECTED_TESTS = 14
MUTATIONS = [
    ("unlisted submissions ignored", CP, '        if kv["id"] not in listed:\n', "        if False:\n",
     "test_spent_held_unlisted_and_the_wanted_ceiling"),
    ("shared rate 0.03", CP, "SHARED_RATE = 0.0391", "SHARED_RATE = 0.03", "test_the_job_kinds"),
    ("cap 3.0", CP, "CAP = 2.5", "CAP = 3.0", "test_the_job_kinds"),
    ("rdx_s1 allowed for any playlist", CP, '(m.group(1) == "2" or m.group(2) == "1A")', "True", "test_the_job_kinds"),
    ("held unfinished jobs ignored", CP, "            held += int(limit_min) * 60 / 3600.0 * rate\n",
     "            pass\n", "test_spent_held_unlisted_and_the_wanted_ceiling"),
    ("the wanted ceiling not added", CP, "    total = spent + held + want\n", "    total = spent + held\n",
     "test_over_the_cap_and_unusable_inputs_refuse"),
    ("sums set unchecked", MG, "    if set(out) != want:\n", "    if False:\n", "test_the_sums_must_list_exactly_the_twelve_loops"),
    ("k1 failures dropped", MG, "    failed = sorted(", "    failed = [] or sorted([]) if True else sorted(",
     "test_k1_passes_only_when_every_key_matches"),
    ("k1 MP-1 pins unchecked", MG, 'if C.sha256(mp1_npz) != CT.MP1_ZERO["lat_npz"] or C.sha256(mp1_bkg) != CT.MP1_ZERO["lat_bkg"]:',
     "if False:", "test_k1_passes_only_when_every_key_matches"),
    ("policy: exact paths only", PA, '    return p == r or p.startswith(r.rstrip("/") + "/")', "    return p == r",
     "test_the_policy_check"),
    ("policy: of_inputs_5d dropped", PA, '    "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz",\n', "",
     "test_the_never_read_list_names_the_ll5d_inputs_and_cov2ds_cv"),
    ("stage pin unchecked", PA, "        if sha != pin:\n", "        if False:\n", "test_atime_stage_and_manifest"),
    ("atime: a missing file passes", PA, "            missing.append(p)\n", "            pass\n",
     "test_atime_stage_and_manifest"),
    ("1M limit 5:45", EV, "1M) LIMIT=4:45:00", "1M) LIMIT=5:45:00", "test_the_event_loop_limits_are_the_declared_rule_everywhere"),
    ("connect 1D limit 3:00", CN, "\n1D 3:30:00\n", "\n1D 3:00:00\n", "test_the_event_loop_limits_are_the_declared_rule_everywhere"),
    ("event loop fence without rsn_", EV, "/^(cov2d|t2a|ll5d|e96data|rpd_|rsn_)/')\n[[ -z \"${hit}\" ]] || { say \"REFUSE: fenced jobs are queued or running: ${hit}\"",
     "/^(cov2d|t2a|ll5d|e96data|rpd_)/')\n[[ -z \"${hit}\" ]] || { say \"REFUSE: fenced jobs are queued or running: ${hit}\"",
     "test_every_launcher_fences_the_six_prefixes"),
    ("arms fence without e96data", AR, "/^(cov2d|t2a|ll5d|e96data|rpd_|rsn_)/", "/^(cov2d|t2a|ll5d|rpd_|rsn_)/",
     "test_every_launcher_fences_the_six_prefixes"),
    ("X1p permute seed 20261114", TT, "X1p\tS3a\twide\t20261113", "X1p\tS3a\twide\t20261114", "test_the_task_table_is_the_declarations"),
    ("X0t not a transfer", TT, "X0t\tS3b\tstd\t-\tnone\tratio\tyes", "X0t\tS3b\tstd\t-\tnone\tratio\tno",
     "test_the_task_table_is_the_declarations"),
    ("X1g at the q3 tilt", TT, "X1g\tS3b\twide\t-\tnone\ta7_gibuu", "X1g\tS3b\twide\t-\tnone\tq3",
     "test_the_task_table_is_the_declarations"),
    ("policy path misspelled", CN, "rpd-reco/prologue5-20261108/policy-config.json", "rpd-reco/prologue5-20261107/policy-config.json",
     "test_every_repo_path_the_launchers_name_exists_at_head"),
    ("merge job's flux path misspelled", SM, "receipts-ct/5b/flux/runEventLoopMC_ALL.root", "receipts-ct/5b/flux/runEventLoopMC_all.root",
     "test_every_repo_path_the_launchers_name_exists_at_head"),
    ("c1 ignores the walk probe", CN, '  [ $rp -eq 0 ] && grep -q \'"verdict": "PASS"\' "$OUT/checks/walk_probe.json" 2>/dev/null \\\n    || stop',
     '  true \\\n    || stop', "test_c1_stops_on_the_walk_probe_and_s2_requires_its_pass"),
    ("s2 does not require the probe", CN, "for c in align_1A truthx_rows_1A walk_probe; do", "for c in align_1A truthx_rows_1A; do",
     "test_c1_stops_on_the_walk_probe_and_s2_requires_its_pass"),
    ("the connect changed under its pin", CN, "# RDX's connect (RDX-DECLARATION.md", "# RDX connect (RDX-DECLARATION.md",
     "test_the_launcher_pins_the_connect_script"),
]

def mirror(root: Path) -> Path:
    """A tree at root/repo mirroring REPO by symlinks, with real copies of the RDX files. Returns its rdx/."""
    repo = root / "repo"
    repo.mkdir()
    for e in REPO.iterdir():
        if e.name != "nd-unfolding":
            (repo / e.name).symlink_to(e)
    nd = repo / "nd-unfolding"
    nd.mkdir()
    for e in ND.iterdir():
        if e.name != "rdx":
            (nd / e.name).symlink_to(e)
    rd = nd / "rdx"
    rd.mkdir()
    for e in HERE.iterdir():
        if e.name not in FILES:
            (rd / e.name).symlink_to(e)
    for f in FILES:
        (rd / f).write_bytes((HERE / f).read_bytes())
    return rd


def run_suite(rd: Path) -> tuple[int, str]:
    p = subprocess.run([sys.executable, "-B", "-m", "unittest", "nd-unfolding/rdx/test_rdx_stages.py"], cwd=rd.parents[1],
                       capture_output=True, text=True, timeout=3600)
    return p.returncode, p.stdout + p.stderr


def failing(out: str) -> set[str]:
    return set(re.findall(r"^(?:FAIL|ERROR): (\w+)", out, re.M))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--jobs", type=int, default=1, help="mutants run at once (each in its own mirrored tree)")
    a = ap.parse_args(argv)
    with tempfile.TemporaryDirectory() as d:
        rc, out = run_suite(mirror(Path(d)))
    ran = re.search(r"^Ran (\d+) tests?", out, re.M)
    if rc != 0 or not ran or int(ran.group(1)) != EXPECTED_TESTS:
        print(f"UNMUTATED SUITE: rc {rc}, ran {ran.group(1) if ran else '?'} of {EXPECTED_TESTS} expected tests\n" + out[-3000:])
        return 1
    print(f"unmutated suite: {ran.group(1)} tests OK, in the mirrored tree")
    todo = [m for m in MUTATIONS if not a.only or a.only in m[0]]
    ok, n = True, len(todo)

    def one(m):
        label, fname, old, new, test = m
        src = (HERE / fname).read_text()
        if src.count(old) != 1:
            return label, test, None, f"anchor occurs {src.count(old)} times"
        with tempfile.TemporaryDirectory() as d:
            rd = mirror(Path(d))
            (rd / fname).write_text(src.replace(old, new))
            _, out = run_suite(rd)
        return label, test, failing(out), ""

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for label, test, fails, why in ex.map(one, todo):
            if fails is None:
                print(f"MUTATION NOT APPLIED  {label}: {why}", flush=True)
                ok = False
                continue
            killed = test in fails
            ok &= killed
            print(f"{'KILLED' if killed else 'SURVIVED':8s}  {label:48s} by {test}"
                  + ("" if killed else f"  (failing: {sorted(fails)})"), flush=True)
    print("MUTATION CHECK ::", "PASS" if ok else "FAIL", f"({n} mutations)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
