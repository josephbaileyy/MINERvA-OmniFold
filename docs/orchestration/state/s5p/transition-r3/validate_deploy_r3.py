#!/usr/bin/env python3
"""s5p transition r3: validate a candidate deploy against ``transition-r3/plan.json`` (read-only).

Exit 0 only if every assertion holds:
- HEAD is exactly --expect-sha, and the tracked tree is clean;
- ``nd-unfolding/`` differs from the running deploy's commit 55a41765 only by non-production report-step files, and
  the frozen modules are byte-identical to 4f5a613f;
- the budget is revision --expect-revision:
  - revision 6 must be byte-identical to deploy c754f3cd's (ledger-bound b9260acd...);
  - revision 7 must carry production 234.647, verification/repair 68.287 (20% of the pool), CPU stages summing to the
    341.434 pool, a cumulative envelope of 376.52, the other CPU stages and the GPU pool unchanged from revision 6,
    and no PREPARED marker;
- ``prod/queues-r3/`` holds exactly the plan's six files. Each is a header, then the wait line of its planned label,
  then the source queues-r2 lines from that wait line byte for byte, with every ``--throttle`` equal to the plan's.

MEASURES: the deploy's fitness as a runner source. CANNOT AUTHORIZE: starting runners or a rebind.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REV6_SHA256 = "b9260acd2fbd4a8bd444a197f5377f5af7d9d5d625720a5d1fc101411790c254"
ALLOWED_ND = {"nd-unfolding/s5p_robust_labels.py", "nd-unfolding/tests/test_s5p_robust_labels.py",
              "nd-unfolding/s5p_missing_sensitivity.py", "nd-unfolding/tests/test_s5p_missing_sensitivity.py"}
FROZEN = ["nd-unfolding/s5p_joint.py", "nd-unfolding/s5p_inference.py", "nd-unfolding/s5p_seqstop.py"]
Q = "docs/orchestration/state/s5p/prod"
B = "docs/orchestration/state/s5p/budget.json"


def git(d: Path, *args: str) -> tuple[int, str]:
    p = subprocess.run(["git", "-C", str(d), *args], capture_output=True, text=True)
    return p.returncode, p.stdout


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--deploy", type=Path, required=True)
    ap.add_argument("--expect-sha", required=True)
    ap.add_argument("--expect-revision", type=int, choices=(6, 7), required=True)
    a = ap.parse_args()
    d, bad = a.deploy, []

    def check(ok: bool, what: str) -> None:
        print(("PASS " if ok else "FAIL ") + what)
        if not ok:
            bad.append(what)

    rc, head = git(d, "rev-parse", "HEAD")
    check(rc == 0 and head.strip() == a.expect_sha, f"HEAD {head.strip()[:12]} == {a.expect_sha[:12]}")
    rc, st = git(d, "status", "--porcelain", "--untracked-files=no")
    check(rc == 0 and st.strip() == "", "tracked tree clean")
    rc, nd = git(d, "diff", "--name-only", "55a41765", "HEAD", "--", "nd-unfolding")
    extra = set(nd.split()) - ALLOWED_ND
    check(rc == 0 and not extra, f"nd-unfolding vs 55a41765 only report-step files (extra: {sorted(extra)})")
    rc, _ = git(d, "diff", "--quiet", "4f5a613f", "HEAD", "--", *FROZEN)
    check(rc == 0, "frozen modules byte-identical to 4f5a613f")

    braw = (d / B).read_bytes()
    b = json.loads(braw)
    rc, r6raw = git(d, "show", f"c754f3cd:{B}")
    r6 = json.loads(r6raw)
    check(b.get("revision") == a.expect_revision, f"budget revision {b.get('revision')} == {a.expect_revision}")
    if a.expect_revision == 6:
        check(hashlib.sha256(braw).hexdigest() == REV6_SHA256, "budget byte-identical to revision 6 (b9260acd...)")
    else:
        c, c6 = b["pools"]["cpu"], r6["pools"]["cpu"]
        s, s6 = c["stages"], c6["stages"]
        check(abs(s["production"] - 234.647) < 1e-9, f"production {s['production']} == 234.647")
        check(abs(s["verification_repair"] - 68.287) < 1e-9, f"verification_repair {s['verification_repair']} == 68.287")
        check(abs(sum(s.values()) - 341.434) < 1e-9 and abs(c["campaign_cap_node_hours"] - 341.434) < 1e-9,
              f"stage sum {sum(s.values()):.3f} == pool {c['campaign_cap_node_hours']} == 341.434")
        check(abs(s["verification_repair"] / c["campaign_cap_node_hours"] - 0.2) < 1e-4, "verification/repair is 20% of the pool")
        check(abs(c["carried_forward"]["envelope_node_hours"] - 376.52) < 1e-9, f"cumulative envelope {c['carried_forward']['envelope_node_hours']} == 376.52")
        check(c["carried_forward"]["prior_charged_node_hours"] == c6["carried_forward"]["prior_charged_node_hours"], "prior charges unchanged")
        check({k: v for k, v in s.items() if k not in ("production", "verification_repair")}
              == {k: v for k, v in s6.items() if k not in ("production", "verification_repair")}, "other CPU stages unchanged")
        check(b["pools"]["gpu"] == r6["pools"]["gpu"], "GPU pool unchanged")
        check(c.get("concurrency_nodes") == c6.get("concurrency_nodes"), "concurrency unchanged")
        check("PREPARED" not in b.get("revision_reason", ""), "live revision text")

    plan = json.loads((d / "docs/orchestration/state/s5p/transition-r3/plan.json").read_text())
    qdir = d / Q / "queues-r3"
    names = sorted(p.name for p in qdir.glob("*.q")) if qdir.is_dir() else []
    check(names == sorted(plan["lanes"]), f"queues-r3 holds exactly the plan's six files ({names})")
    for name, lane in plan["lanes"].items():
        p = qdir / name
        if not p.exists():
            continue
        new = p.read_text().splitlines()
        src = (d / Q / plan["source_dir"] / name).read_text().splitlines()
        lab, thr = lane["label"], lane["throttle"]
        w = [i for i, ln in enumerate(src) if ln.startswith("until out=$(squeue") and f"-n s5p-{lab} " in ln]
        ok_head = len(new) > 1 and new[0].startswith("# ") and new[1].startswith(f"until out=$(squeue -h --me -n s5p-{lab} ")
        ok_body = len(w) == 1 and new[1:] == src[w[0]:]
        thr_vals = {int(x) for x in re.findall(r"--throttle (\d+) ", "\n".join(new))}
        if not thr_vals:  # a queue whose remaining lines submit nothing (power's last wait) carries no throttle
            thr_vals = {thr}
        check(ok_head and ok_body and thr_vals == {thr}, f"{name}: header, wait line {lab}, body byte-identical, throttle {sorted(thr_vals)} == [{thr}]")
    print("VALID" if not bad else f"INVALID ({len(bad)} failed)")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
