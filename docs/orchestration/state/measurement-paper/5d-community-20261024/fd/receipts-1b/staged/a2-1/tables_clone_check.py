#!/usr/bin/env python3
"""1B A2.1: the stage 1 tables generator on a fresh clone, through its real CLI (the director's request before binding
3; the audit's Q3 at 1295f7e4). Local only, 0 compute.

In a scratch directory: a fresh clone of --repo, detached at --rev. In the clone, a pins file is committed at
fd_1b_mc.GATE_PIN (the path read from the clone's own code) for a stand-in gate record, as binding 3 will commit the
real one; that commit is local and never pushed. Then, for each plug-in setting, ``make_stage1_tables.py`` runs as a
subprocess of the clone's own interpreter path, and a second subprocess, importing the clone's fd_1b_mc, parses every
written step with fd_1b_mc's own parser. The checks:
* the counts: s1-0 8 steps; s1-0b 3 (5 with the plug-in); the bulk 1,054 (1,581), on 6 (9) one-node jobs of 8
  lanes, at most 22 per lane; one receipt step;
* no product path is written twice, and none under two rules; each rule writes only to {W}/stage1/unf/<rule>-<est>;
* every bulk step is 'nature' and carries the gate pair given; no s1-0 or s1-0b step carries a gate; every unfold and
  the receipt carry the CV tdw pair.
Exit 0 PASS, 2 FAIL."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

GEN = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/staged/stage1/tables/make_stage1_tables.py"
EXPECT = {"no": {"s1-0": 8, "s1-0b": 3, "s1-bulk": 1054, "nodes": 6},
          "yes": {"s1-0": 8, "s1-0b": 5, "s1-bulk": 1581, "nodes": 9}}
PARSE = r'''
import json, sys
from pathlib import Path
from unittest import mock
co, out = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(co / "nd-unfolding"))
import fd_1b_mc as mc
assert Path(mc.__file__).resolve().is_relative_to(co.resolve()), mc.__file__
class Stop(Exception):
    pass
def parse(argv):
    got = []
    def grab(a):
        got.append(a)
        raise Stop
    guard = ["fd_1b_noatime_guard.py", "--declared", "--", "nd-unfolding/fd_1b_mc.py"]   # every row is guarded
    assert argv[:len(guard)] == guard, argv[:5]
    with mock.patch.object(mc, "run_unfold", grab), mock.patch.object(mc, "receipt", grab):
        try:
            mc.main(argv[len(guard):])
        except Stop:
            pass
    assert len(got) == 1, argv[:8]
    return got[0]
res = {}
for job in ("s1-0", "s1-0b", "s1-bulk", "receipt"):
    rows = []
    for ln in (out / f"{job}-steps.tsv").read_text().splitlines():
        if ln.startswith("#"):
            continue
        lane, _, *argv = ln.split("\t")
        a = parse(argv)
        rec = {"lane": lane, "cmd": a.cmd, "cv_tdw": [str(a.cv_tdw), a.expect_cv_tdw_sha256]}
        if a.cmd == "unfold":
            rec.update(rule=a.clip_rule, out=str(a.out), estimator=a.estimator,
                       gate=[None if a.clip_gate is None else str(a.clip_gate), a.expect_clip_gate_sha256],
                       paths=[str(a.out / mc.product_name(a.tag, a.truth, a.role, it)) for it in a.items.split(",")])
        rows.append(rec)
    res[job] = rows
res["tasks_bulk"] = sum(1 for ln in (out / "tasks-s1-bulk.tsv").read_text().splitlines() if not ln.startswith("#"))
print(json.dumps(res))
'''


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise SystemExit(f"FAIL: {cmd[:4]} exited {r.returncode}: {r.stderr.strip()[-400:]}")
    return r.stdout


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--repo", type=Path, required=True, help="the repository to clone (read only)")
    p.add_argument("--rev", required=True)
    p.add_argument("--work", type=Path, required=True, help="a new scratch directory")
    a = p.parse_args(argv)
    a.work.mkdir(parents=True)
    co = a.work / "clone"
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    git = ["git", "-c", "user.name=tables-clone-check", "-c", "user.email=tables-clone-check@invalid"]
    run(git + ["clone", "-q", "--no-checkout", str(a.repo), str(co)])
    run(git + ["-C", str(co), "checkout", "-q", "--detach", a.rev])
    head = run(git + ["-C", str(co), "rev-parse", "HEAD"]).strip()
    rel = run([sys.executable, "-B", "-c", "import sys; sys.path.insert(0, sys.argv[1]); import fd_1b_mc as mc; "
               "print(mc.GATE_PIN.relative_to(mc._ND.parent).as_posix()); print(mc.TOY_SEEDS['g18'][0])",
               str(co / "nd-unfolding")], env=env).split()
    pin_rel, clip_seed = rel[0], rel[1]
    gate = a.work / "gate-standin.json"
    gate.write_text('{"schema": "fd-1b-c2-gate/1", "note": "a stand-in: the generator reads only its digest"}\n')
    sha = hashlib.sha256(gate.read_bytes()).hexdigest()
    (co / pin_rel).write_text(sha + "\n")
    run(git + ["-C", str(co), "add", pin_rel])
    run(git + ["-C", str(co), "commit", "-q", "-m", "local only: a stand-in pins file"])
    fails, report = [], {"rev": head, "pin": pin_rel, "gate_sha256": sha}

    def check(cond, msg):
        if not cond:
            fails.append(msg)
    for plugin, ex in EXPECT.items():
        out = a.work / f"tables-{plugin}"
        out.mkdir()
        cmd = [sys.executable, "-B", str(co / GEN), str(co), str(out), "--plugin", plugin,
               "--flux-table-sha256", "f" * 64, "--estimator", "R", "--clip-seed", clip_seed,
               "--clip-gate", str(gate), "--expect-clip-gate-sha256", sha]
        if plugin == "yes":
            cmd += ["--push-sha256", "e" * 64]
        printed = run(cmd, env=env, cwd=a.work)
        res = json.loads(run([sys.executable, "-B", "-c", PARSE, str(co), str(out)], env=env, cwd=a.work))
        cv = None
        by_rule, seen = {"data": set(), "nature": set()}, set()
        for job in ("s1-0", "s1-0b", "s1-bulk"):
            rows = res[job]
            check(len(rows) == ex[job], f"{plugin} {job}: {len(rows)} steps, not {ex[job]}")
            for r in rows:
                cv = cv or r["cv_tdw"]
                check(r["cv_tdw"] == cv and None not in r["cv_tdw"], f"{plugin} {job}: a step's CV tdw pair {r['cv_tdw']}")
                want_rule = "nature" if job == "s1-bulk" else "data"
                check(r["rule"] == want_rule, f"{plugin} {job}: rule {r['rule']}")
                check(r["gate"] == ([str(gate), sha] if want_rule == "nature" else [None, None]),
                      f"{plugin} {job}: gate pair {r['gate']}")
                check(Path(r["out"]).name == f"{r['rule']}-{r['estimator']}", f"{plugin} {job}: out {r['out']}")
                for path in r["paths"]:
                    check(path not in seen, f"{plugin}: {path} written twice")
                    seen.add(path)
                    by_rule[r["rule"]].add(path)
        check(not by_rule["data"] & by_rule["nature"], f"{plugin}: a path under both rules")
        lanes = [r["lane"] for r in res["s1-bulk"]]
        check(max(lanes.count(x) for x in set(lanes)) <= 22, f"{plugin}: a lane over 22")
        check(res["tasks_bulk"] == 8 * ex["nodes"], f"{plugin}: {res['tasks_bulk']} bulk lanes, not {8 * ex['nodes']}")
        check(len(res["receipt"]) == 1 and res["receipt"][0]["cmd"] == "receipt" and res["receipt"][0]["cv_tdw"] == cv,
              f"{plugin}: the receipt step {res['receipt']}")
        report[plugin] = {"steps": {j: len(res[j]) for j in ("s1-0", "s1-0b", "s1-bulk", "receipt")},
                          "bulk_lanes": res["tasks_bulk"], "most_per_lane": max(lanes.count(x) for x in set(lanes)),
                          "paths": {r: len(v) for r, v in by_rule.items()},
                          "names_in_both_rules": len({Path(x).name for x in by_rule["data"]}
                                                     & {Path(x).name for x in by_rule["nature"]}),
                          "dirs": sorted({str(Path(x).parent) for v in by_rule.values() for x in v}),
                          "cv_tdw": cv, "generator_printed": printed.strip().splitlines()[0]}
    print(json.dumps(report, indent=1))
    for f in fails:
        print(f"FAIL {f}")
    print("PASS" if not fails else f"FAIL ({len(fails)})")
    return 0 if not fails else 2


if __name__ == "__main__":
    sys.exit(main())
