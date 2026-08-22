#!/usr/bin/env python3
"""Clause (c) RERUN: a SYNTHETIC archive at production dimension, cloned from a stamped member.

WHY THIS EXISTS, AND THE SCOPE IT CARRIES. Stage 1 asks "does the k=0 member reproduce the archive?".
Arm 1 is required to PASS the COMPLETE gate, so the member's payload must EQUAL the archive's. There
are exactly two ways to get that: reproduce the real 892 MB archive's payload, which needs the real
inputs and therefore the 41.44 GB intermediate this verification will not touch; or compare against an
archive built to hold the member's own payload. This is the second.

SO WHAT ARM 1 VERIFIES IS THE GATE, NOT THE ARCHIVE. A pass here says every check in the complete gate
can be satisfied simultaneously by a product the real path produced -- it says NOTHING about whether
any real member reproduces the real archive's physics, and no reader may take it that way.

FAITHFUL IN THE ONE WAY THAT MATTERS FOR THE KEY MAP: the real archive
(`uq_universe_5d_covariance_combined_bkgaware_uthrow.root`, 892195314 B, written 2026-07-14) carries
EXACTLY these four keys -- measured, not assumed -- so this clone carries exactly four too. Every
other classified key stays member-only and goes down the PREDATES_ARCHIVE branch exactly as it does
against the real file, which is the branch OI-147 is about.
"""
import argparse

ARCHIVE_KEYS = ("hCov_combined5d_total_uthrow", "hInflation_g", "sqrt_tr_old", "sqrt_tr_new")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--member", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError
    ROOT.TH1.AddDirectory(False)
    fin = ROOT.TFile.Open(a.member)
    if not fin or fin.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {a.member}")
    fout = ROOT.TFile.Open(a.out, "RECREATE")
    for name in ARCHIVE_KEYS:
        obj = fin.Get(name)
        if not obj:
            raise SystemExit(f"[FAIL] {a.member} carries no {name}; cannot build the archive clone")
        fout.cd()
        # ROOT-side copy: no numpy round-trip, so the archive's bytes ARE the member's bytes for
        # these four keys and the payload digests agree by construction rather than by arithmetic.
        obj.Write(name)
        print(f"[archive]   cloned {name} ({obj.ClassName()})")
    fout.Close()
    fin.Close()
    print(f"[archive] wrote {a.out} with {len(ARCHIVE_KEYS)} keys")


if __name__ == "__main__":
    main()
