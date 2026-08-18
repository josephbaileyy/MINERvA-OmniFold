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

import launcher_argv_probe as probe
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

OFFSET_ENV = policy.OFFSET_ENV

#: launcher -> the env dicts that select EVERY branch it can take. The observed-argv probe refuses to
#: run with fewer cases than the launcher has branches, so this table cannot silently under-cover.
#: `sbatch_uthrow_block_5d.sh` needs both T==0 (knobs) and T!=0 (flux chunk) -- the T!=0 branch is the
#: one that shipped broken, and a single-case probe would have cleared it.
PROBE_CASES = {
    # task 0 reads an EMPTY universe and exits 0 by design -- this launcher's array is 1-BASED
    # (`sed -n "${SLURM_ARRAY_TASK_ID}p"`). Declared, not inferred, so "no command observed" is
    # never silently excused; 1 and 3 are the two branches that actually run the command.
    "sbatch_sweep_bank_5d_run_bkgaware_gpu.sh": [{"SLURM_ARRAY_TASK_ID": 1}, {"SLURM_ARRAY_TASK_ID": 3},
                                                 {"SLURM_ARRAY_TASK_ID": 0, "_expect_command": False}],
    "sbatch_uthrow_run_5d_fast.sh":             [{"SLURM_ARRAY_TASK_ID": 0}, {"SLURM_ARRAY_TASK_ID": 7}],
    "sbatch_uthrow_block_5d.sh":                [{"SLURM_ARRAY_TASK_ID": 0}, {"SLURM_ARRAY_TASK_ID": 3}],
    "sbatch_uthrow_combine_5d_fast.sh":         [{"SLURM_ARRAY_TASK_ID": 0}, {"SLURM_ARRAY_TASK_ID": 1}],
    "sbatch_bootstrap_5d_gpu.sh":               [{"SLURM_ARRAY_TASK_ID": 0}, {"SLURM_ARRAY_TASK_ID": 9}],
    "sbatch_seedscan_split_5d.sh":              [{"SLURM_ARRAY_TASK_ID": 0}, {"SLURM_ARRAY_TASK_ID": 5}],
}
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
    """CHEAP PRECONDITION ONLY -- NOT VERIFICATION, and it must not be reported as if it were.

    This reads the TEXT. It passed identically on the fixed launcher and on the one whose `else`
    branch expanded `${EST_SEED}` to nothing, so it is not evidence either way about whether the hook
    WORKS. Kept because a missing hook is worth catching in milliseconds; the gate is
    `assert_offset_reaches_every_branch` below, which executes the launcher and reads the argv.
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


def assert_offset_reaches_every_branch(offset=7):
    """THE GATE. Execute each launcher with `python3`/`sbatch` stubbed and read the OBSERVED argv.

    Three earlier checks all read the ASSIGNMENT -- the text, the `EST_SEED=$((` line, and that
    line's arithmetic -- and all three passed on a launcher that could not execute its majority
    branch. One blind spot three times, not three blind spots. This is the only form that reads the
    USE, and it caught the defect when pointed at the pre-fix file.
    """
    for launcher, cases in PROBE_CASES.items():
        env_cases = [dict(c, **{OFFSET_ENV: offset}) for c in cases]
        probe.assert_estimator_seed_is_an_integer_in_every_branch(launcher, env_cases)
    return {lnk: len(cs) for lnk, cs in PROBE_CASES.items()}


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
    missing = [leg for leg in LEG_LAUNCHERS if leg not in got]
    if missing:
        raise SystemExit(
            f"[FAIL] no `EST_SEED=$((` assignment was PARSED for {missing}. This function reads the "
            "assignment by string, so a launcher writing the arithmetic differently is silently "
            "ABSENT from the result rather than wrong -- and the k=0 control would then pass over a "
            "leg it never read. Same vacuity as a search that matched nothing.")
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
    assert_offset_hook_present(sources)              # cheap precondition, NOT verification
    policy.assert_draw_seed_is_pinned(sources)
    probed = assert_offset_reaches_every_branch()     # the gate: observed argv, every branch
    baselines = policy.group_baselines()
    checked = policy.assert_offset_grid_is_alias_free(baselines, offsets)
    # BEN-463: the clean-offset predicate, wired now that C has ruled the exemption's FORM. The
    # two archive coincidences are exempt via a (group, range, seed) ALLOWLIST rather than a
    # `j != 0` skip, so a THIRD coincidence at the anchor -- e.g. from a later --array widening --
    # still fails. A member skip would have passed it silently.
    clean_checked = policy.assert_offsets_are_clean(offsets)
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
    return {"probe_cases_run": probed,
            "clean_offset_combinations_checked": clean_checked,
            "offsets": sorted({int(x) for x in offsets}),
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
    print(f"[mii] clean-offset predicate: {plan['clean_offset_combinations_checked']} combinations "
          f"checked, exemptions = the {len(policy.COINCIDENCE_ALLOWLIST)} ARCHIVE coincidences only")
    print(f"[mii] OBSERVED-ARGV probe passed on every branch: {plan['probe_cases_run']}")
    print( "[mii]   (the textual hook check is a precondition, not evidence: it passed on the "
           "launcher whose else-branch expanded the seed to nothing)")
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
