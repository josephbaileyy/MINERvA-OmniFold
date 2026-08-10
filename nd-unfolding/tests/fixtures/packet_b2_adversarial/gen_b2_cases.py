#!/usr/bin/env python3
"""Packet B2 adversarial endpoint-receipt cases — GENERATED AT TEST TIME, not committed as JSON.

Authored by the oversight session, independent of the B2 fix, per Packet B constraint 3.

WHY A GENERATOR AND NOT STATIC FIXTURES
---------------------------------------
B1's fixtures could be static because they perturb band sets and content hashes recorded INSIDE
the manifest — nothing in the repo changes them. B2's cases reference REPO BLOBS, which change
whenever any surface module is committed. A static receipt carrying 15 hardcoded blobs would,
after the next commit to any one of them, mismatch on SEVERAL paths at once. The must-reject
cases would still reject — but for the wrong reason, and the test would be green while no longer
isolating the defect it was written for. That is a test that cannot fail in the direction that
matters, which is the family this lane has spent a week removing.

So each case is built from HEAD's true blobs and then perturbed in exactly one way.

WHAT IS BLIND HERE
------------------
Not the perturbation targets — they are readable below, and knowing them does not help write a
correct check. What is withheld is **which cases must be ACCEPTED and which must be REJECTED**.
For B2 that is the property that matters, because the live hazard is over-rejection: a new check
demanding a field that correct existing artifacts do not carry is exactly how `code_rev == HEAD`
and `verifier_crosscheck` each blocked correct data in this lane (KNOWN_ISSUES #24).

The surface is derived here by an INDEPENDENT AST traversal rather than by importing
`p4_lib.standard_p4_execution_surface()`, deliberately: a generator that imports the code under
test cannot disagree with it. If the two disagree, that disagreement is itself a finding.

Usage:  python3 gen_b2_cases.py --repo <root> --out <dir>
"""
import argparse, ast, json, subprocess
from pathlib import Path

DIRS = ("nd-unfolding", "2d-unfolding", "unbinned_unfolding/python", ".")
ENTRYPOINTS = ("nd-unfolding/p4_evidence.py", "nd-unfolding/p4_build_components.py",
               "nd-unfolding/p4_validate_active_lateral.py", "nd-unfolding/p4_project_4d.py",
               "nd-unfolding/p4_check_receipt.py", "nd-unfolding/p4_check_verifier_token.py",
               "nd-unfolding/unfold_nd_omnifold_unbinned.py")
DRIVER = "nd-unfolding/unfold_nd_omnifold_unbinned.py"

# The field name is INCIDENTAL. If the fix records per-path blobs under a different key, rename it
# here or in the consuming test -- what is adversarial is which path is perturbed and how.
BLOB_FIELD = "surface_blobs"

# A real produced receipt, verbatim from
# active_universe_5d/standard/unfolds/5d_xsec_MEFHC_5iter_lgbm_uni_full_BeamAngleX_0.root.done
BASE = {
    "tag": "BeamAngleX_0",
    "mode": "produced",
    "root_sha256": "4c2ce06071004a93b5cb79bb91e0c95a0db2c3eba33b69b559023545136f9118",
    "merged_sha256": "38b9fc307eabd864cd0fd663679b51fb2e6d064672410af6b3cf8b0a7e161ed5",
    "central5d_sha256": "630306e20e4e175bde8b459174842a58e4f4b5a694b8a5018e730a952820aec8",
    "config_hash": "4b41fab90a83df08b57361cec4e769447815afe4f751c9f57848a022bf06a382",
    "bkg_mode": "purity",
    "bkg_mode_basis": "passed explicitly to the driver by this launcher",
    "code_rev": "42268b6dfa2e60a0e4bd491b11ad9b11d0228273",
    "unfold_blob": "dc74c38f8ec7b5f6723fa231630e9fc43e7a93f0",
    "t": "2026-08-08T14:02:13Z",
}


def surface_and_driver_reach(repo):
    tracked = set(subprocess.check_output(["git", "ls-files"], cwd=repo, text=True).splitlines())

    def resolve(mod):
        for d in DIRS:
            cand = f"{d}/{mod.replace('.', '/')}.py".lstrip("./")
            if cand in tracked:
                return cand
        return None

    def imports_of(rel):
        out = []
        try:
            tree = ast.parse((Path(repo) / rel).read_text(errors="replace"))
        except Exception:
            return out
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                out += [r for r in (resolve(a.name) for a in n.names) if r]
            elif isinstance(n, ast.ImportFrom) and n.module:
                r = resolve(n.module)
                if r:
                    out.append(r)
        return out

    def reach(seeds, max_depth=6):
        seen, frontier = set(), list(seeds)
        for _ in range(max_depth):
            nxt = []
            for rel in frontier:
                if rel in seen or rel not in tracked:
                    continue
                seen.add(rel)
                nxt += [r for r in imports_of(rel) if r not in seen]
            frontier = nxt
            if not frontier:
                break
        return seen

    return reach(ENTRYPOINTS), reach([DRIVER]), set(imports_of(DRIVER))


def head_blob(repo, path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], cwd=repo,
                                   text=True).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    repo, out = a.repo, Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    surface, from_driver, direct = surface_and_driver_reach(repo)
    blobs = {p: head_blob(repo, p) for p in sorted(surface)}
    transitive_only = sorted((from_driver - direct) - {DRIVER})
    not_via_driver = sorted(surface - from_driver)

    WRONG = "0" * 40

    def base_with_blobs():
        r = dict(BASE)
        r[BLOB_FIELD] = dict(blobs)
        r["unfold_blob"] = blobs[DRIVER]
        r["code_rev"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo,
                                                text=True).strip()
        return r

    cases = {}

    # L -- a DIRECT import of the driver differs. The packet's named example.
    r = base_with_blobs(); r[BLOB_FIELD]["unbinned_unfolding/python/omnifold.py"] = WRONG
    cases["L"] = (r, "unbinned_unfolding/python/omnifold.py differs (direct import of the driver)")

    # M -- a TRANSITIVE-ONLY member differs. Separates "binds the executed set" from "binds the
    # driver's direct imports". There is exactly one such module, so this case is forced.
    assert len(transitive_only) == 1, transitive_only
    r = base_with_blobs(); r[BLOB_FIELD][transitive_only[0]] = WRONG
    cases["M"] = (r, f"{transitive_only[0]} differs (reached only transitively from the driver)")

    # N -- every recorded blob MATCHES, but one surface path is omitted from the record.
    # B1's omission hazard one level up: internally consistent about an incomplete set.
    r = base_with_blobs(); r[BLOB_FIELD].pop("nd-unfolding/xsec_nd.py")
    cases["N"] = (r, "nd-unfolding/xsec_nd.py omitted from the record; all recorded blobs match")

    # O -- a LEGACY receipt with no per-path record at all. This is the shape of every
    # `mode: produced` receipt currently on scratch.
    cases["O"] = (dict(BASE), "legacy receipt: no per-path blob record; pre-fix shape verbatim")

    # P -- a surface member NOT REACHABLE from the unfold driver differs.
    # p4_project_4d.py is never executed while an endpoint ROOT is produced, so it cannot have
    # affected that ROOT.
    assert "nd-unfolding/p4_project_4d.py" in not_via_driver, not_via_driver
    r = base_with_blobs(); r[BLOB_FIELD]["nd-unfolding/p4_project_4d.py"] = WRONG
    cases["P"] = (r, "nd-unfolding/p4_project_4d.py differs (in the surface, NOT reachable from "
                     "the unfold driver)")

    for vid, (rec, desc) in cases.items():
        rec["_fixture"] = {"packet": "B2", "variant": vid,
                           "authored_by": "oversight session (independent of the fix)",
                           "expected_outcome": "WITHHELD",
                           "perturbation": desc}
        p = out / f"endpoint_receipt.B2_{vid}.json"
        p.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
        print(f"{vid}: {desc}")

    print(f"\nsurface={len(surface)} from_driver={len(from_driver)} "
          f"direct={len(direct)} transitive_only={transitive_only} "
          f"not_via_driver={len(not_via_driver)}")
    print("expected outcomes are WITHHELD -- the oversight session holds them")


if __name__ == "__main__":
    main()
