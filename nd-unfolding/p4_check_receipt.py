#!/usr/bin/env python3
"""Endpoint-receipt gate for run_p4_unfold_std.sh's resume path (repair-4, verifier defect 2).

Exit 0 iff the receipt is complete and every recorded identity matches the live/committed one;
otherwise print `RECEIPT-REJECT :: <reason>` and exit 1, which makes the launcher re-run the
endpoint transactionally instead of skipping it.

Deliberately a separate CLI rather than inline `python3 -c` in the launcher: the previous skip
logic was an unreadable one-liner, and a gate that cannot be unit-tested is the defect this
whole repair round exists to remove. ROOT-free -- content validity of the ROOT itself is the
launcher's `valid_root`, this is the provenance half.

Usage:
  p4_check_receipt.py --receipt R.done --tag BAND_EP --root OUT.root --merged MERGED.root
"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p4_lib as P

REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
ND = f"{REPO}/nd-unfolding"
CEN5 = f"{ND}/products/5d/xsec_5d_MEFHC_5iter_lgbm.root"
RECDIR = f"{REPO}/docs/orchestration/state/merged-input-hashes/p4-merged-20260718"


def committed_merged_sha(merged_path):
    """The orchestrator receipt's committed hash for this merged file, after its own live
    size+integer-mtime check. Never re-hashes 53.8 GB."""
    live = {}
    for b in P.BANDS:
        for ep in P.ENDPOINTS:
            rel = (f"nd-unfolding/active_universe_5d/standard/merged/"
                   f"runEventLoopOmniFold_5D_MEFHC_active_{b}_{ep}.root")
            ap = f"{REPO}/{rel}"
            st = os.stat(ap)
            live[rel] = (st.st_size, int(st.st_mtime))
    rec = P.validate_orchestrator_merged_receipt(RECDIR, live)
    base = os.path.basename(merged_path)
    for p, h in rec["merged_sha256"].items():
        if os.path.basename(p) == base:
            return h
    raise P.P4GateError(f"{base} not in the orchestrator merged receipt")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--merged", required=True)
    a = ap.parse_args()
    try:
        if not os.path.exists(a.receipt) or os.path.getsize(a.receipt) == 0:
            raise P.P4GateError("receipt absent or empty")
        try:
            rec = json.load(open(a.receipt))
        except Exception as e:
            raise P.P4GateError(f"receipt is not valid JSON ({e})")
        cfg = P.P4Config(); cfg.validate()
        P.validate_endpoint_receipt(
            rec, tag=a.tag,
            root_sha256=P.sha256_file(a.root),
            merged_sha256=committed_merged_sha(a.merged),
            central5d_sha256=P.sha256_file(CEN5),
            config_hash=cfg.hash(),
            bkg_mode=cfg.bkg_mode)
    except P.P4GateError as e:
        print(f"RECEIPT-REJECT :: {e}"); sys.exit(1)
    except Exception as e:                      # never let an unexpected error read as PASS
        print(f"RECEIPT-REJECT :: unexpected {type(e).__name__}: {e}"); sys.exit(1)
    print(f"RECEIPT-OK :: {a.tag}")
    sys.exit(0)


if __name__ == "__main__":
    main()
