#!/usr/bin/env python3
"""Clause (c) RERUN: assemble one arm's INPUT pair from the shared base payload + per-leg identity.

The payload is built once (`build_base.py`) and copied, because every arm except the negative-diagonal
one uses the SAME matrices -- so the arms differ in exactly the scalars under test and nothing else.
That is the point: an arm that also changed the payload could not attribute its own refusal.

THE BASENAMES ARE PINNED AND THE DIRECTORIES ARE NOT. `mii_anchor_comparator.CONFIG_SOURCES` requires
basename(--uthrow) == "unified_throw_cov_5d.root" and basename(--combined) ==
"uq_universe_5d_covariance_combined_bkgaware.root". Member scoping inserts DIRECTORIES and preserves
basenames (`lib_member_resume._mr_insert`), which is what makes those two keys usable as a contract at
all -- so putting each arm under its own directory is the same transformation a real member applies.
"""
import argparse
import os
import shutil

LEG_IDENTITY_KEYS = ("estimator_seed", "est_seed_offset", "est_seed_offset_declared")


def stamp_leg(path, seed, offset, declared):
    """Add this leg's THREE identity scalars, as genuine TParameter("int") -- the producers' own type.

    `seed=None` models a leg that carries no `estimator_seed` at all (a leg predating the stamp), which
    is a state the writer must tolerate and the GATE must refuse for a declared member. `declared=None`
    models a leg predating the offset pair entirely.
    """
    import ROOT
    f = ROOT.TFile.Open(path, "UPDATE")
    if not f or f.IsZombie() or not f.IsWritable():
        raise SystemExit(f"[FAIL] cannot reopen {path} UPDATE")
    try:
        already = [k for k in LEG_IDENTITY_KEYS if f.Get(k)]
        if already:
            raise SystemExit(f"[FAIL] {path} already carries {already}; ROOT would append a second "
                             "cycle rather than replace. Rebuild the variant instead.")
        f.cd()
        if seed is not None:
            ROOT.TParameter("int")("estimator_seed", int(seed)).Write()
        if declared is not None:
            ROOT.TParameter("int")("est_seed_offset", int(offset)).Write()
            ROOT.TParameter("int")("est_seed_offset_declared", int(declared)).Write()
        wrote = {k: (f.Get(k).GetVal() if f.Get(k) else None) for k in LEG_IDENTITY_KEYS}
    finally:
        f.Close()
    print(f"[variant]   {os.path.basename(path)} leg keys read back: {wrote}")


def _int_or_none(s):
    return None if s.lower() in ("none", "absent", "") else int(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--dest", required=True, help="the arm's uq_5d/<arm> directory")
    ap.add_argument("--combined-variant", choices=("pos", "neg"), default="pos")
    for leg in ("g1", "g2"):
        ap.add_argument(f"--{leg}-seed", default="none", type=str)
        ap.add_argument(f"--{leg}-offset", default="0", type=str)
        ap.add_argument(f"--{leg}-declared", default="none", type=str)
    a = ap.parse_args()

    outd = os.path.join(a.dest, "universe_stage2_5d_bkgaware")
    os.makedirs(outd, exist_ok=True)
    uthrow = os.path.join(a.dest, "unified_throw_cov_5d.root")
    combined = os.path.join(outd, "uq_universe_5d_covariance_combined_bkgaware.root")
    shutil.copy2(os.path.join(a.base, "uthrow_payload.root"), uthrow)
    shutil.copy2(os.path.join(a.base, f"combined_payload_{a.combined_variant}.root"), combined)
    print(f"[variant] {a.dest}  combined-variant={a.combined_variant}")
    # g2 is the UNIFIED THROW leg, g1 the COMBINED intermediate -- seed_offset_policy.LEG_BASELINES
    # gives g2 baseline 1000 (unified_throw_cov) and g1 baseline 42 (sweep_bank_5d).
    stamp_leg(uthrow, _int_or_none(a.g2_seed), int(a.g2_offset), _int_or_none(a.g2_declared))
    stamp_leg(combined, _int_or_none(a.g1_seed), int(a.g1_offset), _int_or_none(a.g1_declared))


if __name__ == "__main__":
    main()
