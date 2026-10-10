#!/usr/bin/env python3
"""Write ``manifest/expected-code.json``: the sha256 of every file an SB1 launch depends on.

    python3 make_manifest.py            # writes the manifest (and the proposal's derived fields)
    python3 make_manifest.py --check    # exit 1 unless both committed files are current

Three groups, all checked at HEAD by ``sb1_admit.py``: ``modules``, exactly the files
``sb1_run.py`` executes (and strict mode requires ``--expect`` to state); ``guard``, the OI-136
wrapper and its shim; ``launch``, the scripts and the frozen plan. The manifest names contents,
not a commit, so the package commit that carries it can be named by the admission record.

It also refreshes the fields of ``launch/ADMISSION-PROPOSAL.json`` that are derived from files
(``code.modules``, ``launch_spec_sha256``, the job ceilings from ``results/costs.json``), so the
proposal cannot carry a stale digest; every other field of the proposal is left as written.
"""

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
PKG = HERE.relative_to(REPO).as_posix()
N2 = "2d-unfolding/uq/coverage_fixed_truth/n2"
MODULES = (f"{PKG}/sb1_run.py", f"{PKG}/branch_select.py", f"{N2}/__init__.py", f"{N2}/execution.py",
           "2d-unfolding/unfold_2d_omnifold_unbinned.py", "unbinned_unfolding/python/omnifold.py")
GUARD = ("nd-unfolding/mnv_guarded_run.py", "nd-unfolding/mnv_guard_shim/sitecustomize.py",
         "nd-unfolding/mnv_guard_shim/scan_argv.py", "nd-unfolding/mnv_guard_shim/wrapper_exec.py")
LAUNCH = tuple(f"{PKG}/{p}" for p in (
    "sb1_admit.py", "sb1_hash.py", "sb1_verify.py", "launch/launch-spec.json",
    "launch/sb1_submit.sh", "launch/sb1_hash.sbatch", "launch/sb1_unfold.sbatch",
    "launch/sb1_identity.sbatch", "launch/sb1_cv.sbatch"))


def digests(paths):
    return {p: hashlib.sha256((REPO / p).read_bytes()).hexdigest() for p in paths}


def build():
    shim_bin = sorted(p.relative_to(REPO).as_posix()
                      for p in (REPO / "nd-unfolding/mnv_guard_shim/bin").rglob("*") if p.is_file())
    return {"schema": "sb1-expected-code/1",
            "note": "contents only; the admission record names the commit (sb1_admit.py)",
            "modules": digests(MODULES), "guard": digests(GUARD + tuple(shim_bin)),
            "launch": digests(LAUNCH)}


def proposal(manifest):
    path = HERE / "launch" / "ADMISSION-PROPOSAL.json"
    prop = json.loads(path.read_text())
    costs = json.loads((HERE / "results" / "costs.json").read_text())
    prop["code"]["modules"] = manifest["modules"]
    prop["launch_spec_sha256"] = manifest["launch"][f"{PKG}/launch/launch-spec.json"]
    prop["jobs"] = [{"id": j["id"], "ceiling_node_h": j["ceiling_node_h"]} for j in costs["jobs"]]
    return path, json.dumps(prop, indent=1) + "\n"


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    out = HERE / "manifest" / "expected-code.json"
    manifest = build()
    text = json.dumps(manifest, indent=1, sort_keys=True) + "\n"
    ppath, ptext = proposal(manifest)
    if "--check" in argv:
        ok = (out.read_text() if out.exists() else "") == text and ppath.read_text() == ptext
        print("manifest current" if ok else "manifest or proposal OUT OF DATE")
        return 0 if ok else 1
    out.parent.mkdir(exist_ok=True)
    out.write_text(text)
    ppath.write_text(ptext)
    print(f"wrote {out.relative_to(REPO)} and {ppath.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
