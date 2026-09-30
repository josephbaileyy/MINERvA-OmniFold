#!/usr/bin/env python3
"""s5p transition r2: validate a candidate deploy (read-only; exit 0 only if every assertion holds).

Asserts, for a clone at --deploy:
- HEAD is exactly --expect-sha, and the tracked tree is clean;
- ``nd-unfolding/`` differs from the running deploy's commit 55a41765 only by the non-production
  ``s5p_robust_labels.py`` and its test, and the frozen modules are byte-identical to 4f5a613f;
- the budget is revision --expect-revision. Revision 5 must be byte-identical to 55a41765's copy. Revision 6 must
  have production 209.647, stages summing to the campaign cap 310.184, verification/repair 62.037, the other CPU
  stages and the GPU pool unchanged from revision 5;
- ``prod/queues-r2/`` holds exactly the six expected files. Each is a '#' header, then the wait line of its expected
  label, then the source queue's lines from that wait line byte for byte, and every ``--throttle`` equals the
  lane's throttle.

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

REV5_SHA256 = "f29db38996103c9a42757c6c686257dce9024177c769266a769695dd7fb6e865"
ALLOWED_ND = {"nd-unfolding/s5p_robust_labels.py", "nd-unfolding/tests/test_s5p_robust_labels.py"}
FROZEN = ["nd-unfolding/s5p_joint.py", "nd-unfolding/s5p_inference.py", "nd-unfolding/s5p_seqstop.py"]
Q = "docs/orchestration/state/s5p/prod"
LANES = {  # queues-r2 file: (source queue, label, throttle)
    "pow.q": ("queues-r1/pow.q", "s5p_pow_p3_a1p0", 3),
    "cal-MnvTune_v1.q": ("queues-r1/cal-MnvTune_v1.q", "s5p_cal_mnvtune_v1_b2", 3),
    "cal-GENIE_2_12_10_CV.q": ("queues-r1/cal-GENIE_2_12_10_CV.q", "s5p_cal_genie_2_12_10_cv_b2", 3),
    "cal-GENIE_2_12_10_MEC.q": ("queues-r1/cal-GENIE_2_12_10_MEC.q", "s5p_cal_genie_2_12_10_mec_b2", 3),
    "cal-NuWro_21_09.q": ("queues/cal-NuWro_21_09.q", "s5p_cal_nuwro_21_09_b2", 2),
    "cal-GiBUU_2019.q": ("queues/cal-GiBUU_2019.q", "s5p_cal_gibuu_2019_b2", 2),
}


def git(d: Path, *args: str) -> tuple[int, str]:
    p = subprocess.run(["git", "-C", str(d), *args], capture_output=True, text=True)
    return p.returncode, p.stdout


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--deploy", type=Path, required=True)
    ap.add_argument("--expect-sha", required=True)
    ap.add_argument("--expect-revision", type=int, choices=(5, 6), required=True)
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
    check(rc == 0 and not extra, f"nd-unfolding vs 55a41765 only the robust-label files (extra: {sorted(extra)})")
    rc, _ = git(d, "diff", "--quiet", "4f5a613f", "HEAD", "--", *FROZEN)
    check(rc == 0, "frozen modules byte-identical to 4f5a613f")

    bpath = d / "docs/orchestration/state/s5p/budget.json"
    braw = bpath.read_bytes()
    b = json.loads(braw)
    rc, r5raw = git(d, "show", "55a41765:docs/orchestration/state/s5p/budget.json")
    r5 = json.loads(r5raw)
    check(b.get("revision") == a.expect_revision, f"budget revision {b.get('revision')} == {a.expect_revision}")
    if a.expect_revision == 5:
        check(hashlib.sha256(braw).hexdigest() == REV5_SHA256, "budget byte-identical to revision 5 (f29db389...)")
    else:
        s, s5 = b["pools"]["cpu"]["stages"], r5["pools"]["cpu"]["stages"]
        cap = b["pools"]["cpu"]["campaign_cap_node_hours"]
        check(abs(s["production"] - 209.647) < 1e-9, f"production {s['production']} == 209.647")
        check(abs(sum(s.values()) - 310.184) < 1e-9 and abs(cap - 310.184) < 1e-9, f"stage sum {sum(s.values()):.3f} == cap {cap} == 310.184")
        check(abs(s["verification_repair"] - 62.037) < 1e-9, f"verification_repair {s['verification_repair']} == 62.037")
        others = {k: v for k, v in s.items() if k != "production"}
        check(others == {k: v for k, v in s5.items() if k != "production"}, "other CPU stages unchanged from revision 5")
        check(b["pools"]["gpu"] == r5["pools"]["gpu"], "GPU pool unchanged from revision 5")
        check(b["pools"]["cpu"]["carried_forward"] == r5["pools"]["cpu"]["carried_forward"], "carried-forward envelope unchanged")
        check("PREPARED" not in b.get("revision_reason", ""), "live revision text (no PREPARED marker)")

    qdir = d / Q / "queues-r2"
    names = sorted(p.name for p in qdir.glob("*.q")) if qdir.is_dir() else []
    check(names == sorted(LANES), f"queues-r2 holds exactly the six expected files ({names})")
    for name, (src, label, thr) in LANES.items():
        p = qdir / name
        if not p.exists():
            continue
        new = p.read_text().splitlines()
        srcl = (d / Q / src).read_text().splitlines()
        w = [i for i, ln in enumerate(srcl) if ln.startswith("until out=$(squeue") and f"-n s5p-{label} " in ln]
        ok_head = len(new) > 1 and new[0].startswith("# ") and new[1].startswith(f"until out=$(squeue -h --me -n s5p-{label} ")
        ok_body = len(w) == 1 and new[1:] == srcl[w[0]:]
        thr_vals = {int(x) for x in re.findall(r"--throttle (\d+) ", "\n".join(new))}
        check(ok_head and ok_body and thr_vals == {thr}, f"{name}: header, wait line {label}, body byte-identical, throttle {sorted(thr_vals)} == [{thr}]")
    print("VALID" if not bad else f"INVALID ({len(bad)} failed)")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
