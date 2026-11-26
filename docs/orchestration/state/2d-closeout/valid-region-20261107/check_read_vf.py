#!/usr/bin/env python3
"""Control for valid_region_vf.py's run (receipts/read-vf/): its controls all pass, its six inputs are the V_F pins
(INPUTS-vf.sha256), its code is valid_region_vf.py, and its readings equal fd/with-vf/p2/vatlas.vf.json's "readings"
exactly (fd_vf_p2.p2_vatlas ran valid_region.readings on the same inputs, its reported matrix given under the old key).

usage: python3 -B check_read_vf.py --repo <worktree>      exit 0 only if every check holds
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

D = "docs/orchestration/state/2d-closeout/valid-region-20261107"
READOUT = f"{D}/receipts/read-vf/readout.json"
VATLAS = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/with-vf/p2/vatlas.vf.json"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    R = Path(ap.parse_args().repo)
    r = json.loads((R / READOUT).read_text())
    v = json.loads((R / VATLAS).read_text())
    pins = {ln.split(None, 1)[1].strip(): ln.split()[0] for ln in (R / D / "INPUTS-vf.sha256").read_text().splitlines()
            if ln.strip()}
    sys.path.insert(0, str(R / D))
    import valid_region_vf as VF
    checks = [
        ("every control passes", bool(r["controls"]) and all(c["pass"] for c in r["controls"])),
        ("six inputs, each the V_F pin and the file's digest",
         len(VF.INPUTS) == 6 and all(r["inputs_sha256"][k] == pins[rel] == sha(R / rel) for k, rel in VF.INPUTS.items())),
        ("code_sha256 is valid_region_vf.py's", r["code_sha256"] == sha(R / D / "valid_region_vf.py")),
        ("readings present", "readings" in r and bool(r["readings"])),
        ("readings equal vatlas.vf.json's exactly", r.get("readings") == v["readings"]),
    ]
    for name, ok in checks:
        print(f"{'OK  ' if ok else 'FAIL'} {name}")
    return 0 if all(ok for _, ok in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
