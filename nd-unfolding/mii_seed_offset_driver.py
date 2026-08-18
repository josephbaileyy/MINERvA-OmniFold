#!/usr/bin/env python3
"""Four-leg estimator-seed offset scan driver for M(ii) (spec (B), option (ii) OFFSET).

WHAT THIS IS FOR. Under spec (B), `M(ii)` -- the magnitude of what varying the estimator seed would
have contributed -- is a JOINT measurement on the composite, so all four `C_syst` legs must vary
COHERENTLY in one run. Lane C ruled option (ii): each leg moves from ITS OWN baseline by a common
offset `k`, preserving which legs share estimator noise with which. The baselines are not shared:

    g1 (baseline   42)   sweep_bank_5d, bootstrap_nd, seedscan_split
    g2 (baseline 1000)   unified_throw_cov

A FLAG IS CAPABILITY; A LAUNCHER DIFF IS NOT A LAUNCHER. All four modules accepted an estimator seed
before this file existed and no single run could drive them coherently -- the nearest existing driver
reached three of four and `sweep_bank_5d.py` was in none of them. Integration is the deliverable.

HOW COHERENCE IS GUARANTEED, and it is deliberately NOT this driver's responsibility. Each of the six
targeted launchers carries its own baseline literal and computes

    EST_SEED=$(( <its own baseline> + ${MNV_EST_SEED_OFFSET:-0} ))

so the driver passes ONE number and every leg adds it to its own baseline. The driver cannot break the
grouping because it never names a seed value, and `MNV_EST_SEED_OFFSET` unset -- the default --
reproduces the archive exactly. That is requirement (4) made structural instead of expected.

REQUIREMENT (5), lane D's, and the one that would have silently spent the whole scan: `--draw-seed`
stays the literal `1000` for every `k`. Only the estimator seed moves. Passing `1000+k` to both flags
is the natural implementation and it gives every scan member a different THROW ENSEMBLE, so the spread
measured is estimator noise convolved with ensemble noise -- `C_syst` re-measured with extra steps,
looking entirely normal. The combine guard cannot catch it: it compares each slab's `draw_seed`
against THIS combine's `--draw-seed`, and every member runs its own combine, so `1000/1000` and
`1005/1005` both pass. PER-MEMBER COHERENCE IS NOT ENSEMBLE COHERENCE. Enforced by
`seed_offset_policy.assert_draw_seed_is_pinned` over the launcher sources, against a CONSTANT.

THIS FILE DOES NOT SUBMIT. There is no `sbatch` call in it and no code path that reaches one. It emits
a plan and validates it; submission is a separate deliberate act by a separate party, which is how the
authorization was written. `--check` exits non-zero on any violation and is the whole interface.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import seed_offset_policy as policy

#: leg -> the launcher the scan drives. Other launchers of the same modules are UNCHANGED and still
#: carry their literals, so a scan that does not go through these six is not this scan.
LEG_LAUNCHERS = {
    "sweep_bank_5d":     ["sbatch_sweep_bank_5d_run_bkgaware_gpu.sh"],
    "unified_throw_cov": ["sbatch_uthrow_run_5d_fast.sh",
                          "sbatch_uthrow_block_5d.sh",
                          "sbatch_uthrow_combine_5d_fast.sh"],
    "bootstrap_nd":      ["sbatch_bootstrap_5d_gpu.sh"],
    "seedscan_split":    ["sbatch_seedscan_split_5d.sh"],
}

OFFSET_ENV = "MNV_EST_SEED_OFFSET"
HERE = os.path.dirname(os.path.abspath(__file__))


def launcher_sources():
    out = {}
    for paths in LEG_LAUNCHERS.values():
        for rel in paths:
            full = os.path.join(HERE, rel)
            if not os.path.exists(full):
                raise SystemExit(f"[FAIL] targeted launcher missing: {rel}")
            with open(full, encoding="utf-8") as fh:
                out[rel] = fh.read()
    return out


def assert_offset_hook_present(sources):
    """Every targeted launcher must read the offset env and must not hardcode the estimator seed.

    Without this the driver would export a variable nothing reads, the scan would run entirely at
    baseline, and every member would agree -- a null result produced by the plumbing rather than by
    the physics, which is the most expensive way for this to fail.
    """
    bad = []
    for rel, text in sources.items():
        if OFFSET_ENV not in text:
            bad.append(f"{rel}: does not read ${OFFSET_ENV}; it would run at baseline for every k")
        if "--estimator-seed ${EST_SEED}" not in text:
            bad.append(f"{rel}: does not pass --estimator-seed ${{EST_SEED}}")
    if bad:
        raise SystemExit("[FAIL] the offset hook is not wired:\n  " + "\n  ".join(bad))
    return True


def archive_expansion(sources):
    """What each launcher's `EST_SEED` expands to at k=0, read out of the launcher itself."""
    got = {}
    for leg, paths in LEG_LAUNCHERS.items():
        for rel in paths:
            for line in sources[rel].split("\n"):
                s = line.strip()
                if s.startswith("EST_SEED=$(("):
                    base = s.split("$((", 1)[1].split("+", 1)[0].strip()
                    got.setdefault(leg, set()).add(int(base))
    return {leg: sorted(v) for leg, v in got.items()}


def assert_k0_reproduces_the_archive(sources):
    """REQUIREMENT (4), and it is two-sided on purpose.

    The launcher's baseline is compared against `policy.LEG_BASELINES`, an INDEPENDENT table -- so
    changing either side fails. A reproduction check that only notices changes on one side is
    comparing a value against itself (`BEN-423`, which caught three lanes today).
    """
    got = archive_expansion(sources)
    expected = {leg: [base] for leg, (_g, base) in policy.LEG_BASELINES.items()
                if leg in LEG_LAUNCHERS}
    if got != expected:
        raise SystemExit(
            "[FAIL] at k=0 the launchers do NOT reproduce the archive baselines.\n"
            f"  launchers say: {got}\n  archive table says: {expected}\n"
            "  k=0 is the anchor every scan point is measured against, and option (ii) was chosen "
            "over (i) precisely because it HAS one.")
    return expected


def build_plan(offsets):
    sources = launcher_sources()
    assert_offset_hook_present(sources)
    policy.assert_draw_seed_is_pinned(sources)
    baselines = policy.group_baselines()
    checked = policy.assert_offset_grid_is_alias_free(baselines, offsets)
    archive = assert_k0_reproduces_the_archive(sources)
    plan = []
    for k in sorted({int(x) for x in offsets}):
        for leg, paths in LEG_LAUNCHERS.items():
            grp, base = policy.LEG_BASELINES[leg]
            for rel in paths:
                plan.append({"k": k, "leg": leg, "group": grp,
                             "estimator_seed": base + k,
                             "draw_seed": policy.ARCHIVE_DRAW_SEED if leg == "unified_throw_cov" else None,
                             "launcher": rel,
                             "env": {OFFSET_ENV: str(k)},
                             "command": f"{OFFSET_ENV}={k} sbatch {rel}"})
    return {"offsets": sorted({int(x) for x in offsets}),
            "group_baselines": baselines,
            "archive_k0": archive,
            "aliasing_pairs_checked": checked,
            "members": plan,
            "submitted": False,
            "note": "PLAN ONLY. This driver contains no sbatch call and no submission path."}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offsets", required=True,
                    help="comma-separated offset grid, e.g. 0,1,2,3 (k=0 is the archive anchor)")
    ap.add_argument("--out", default=None, help="write the plan JSON here")
    ap.add_argument("--check", action="store_true",
                    help="validate only; exit non-zero on any violation")
    a = ap.parse_args(argv)
    offsets = [int(x) for x in a.offsets.split(",") if x.strip() != ""]
    plan = build_plan(offsets)
    print(f"[mii] offsets={plan['offsets']}  groups={plan['group_baselines']}  "
          f"aliasing pairs checked={plan['aliasing_pairs_checked']}")
    print(f"[mii] k=0 archive anchor verified two-sided: {plan['archive_k0']}")
    print(f"[mii] --draw-seed pinned to the literal {policy.ARCHIVE_DRAW_SEED} in every targeted launcher")
    if not a.check:
        for m in plan["members"]:
            ds = "" if m["draw_seed"] is None else f"  draw={m['draw_seed']}"
            print(f"   k={m['k']:>5}  {m['group']}  est={m['estimator_seed']:<6}{ds}  {m['command']}")
    print(f"[mii] {len(plan['members'])} launcher invocations planned. NOTHING SUBMITTED: this driver "
          f"has no sbatch call.")
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(plan, fh, indent=2, sort_keys=True)
            fh.write("\n")
        print(f"[mii] wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
