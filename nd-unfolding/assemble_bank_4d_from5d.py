#!/usr/bin/env python3
"""Assemble uq_4d/corrected/bank_uthrow_4d/ from the surviving 5D throw bank.

The 4D unified-throw bank (bank_uthrow_4d) and its 3D source (bank_uthrow) were
deleted in cleanup, and no 4D `_universes_full` omnifile exists -- so the June
assemble_bank_4d.py (which read the 3D bank + a now-gone td_q3.npz) cannot run.
But bank_uthrow_5d survives and is event-aligned to of_inputs_4d.npz:

  * bank_uthrow_5d/cv.npz w_truth / w_reco are BYTE-IDENTICAL to of_inputs_4d
    (max|diff|=0, same 32,849,103-event ordering), and MCgen pt/pz/Eavail columns
    and the pt/pz/Eavail/q3 edges match exactly (14/16/7/7 bins).
  * the 372 per-event universe-ratio weight arrays (sig_<band>_{t,r}_<idx>.npy,
    sig_flux_{t,r}_<u>.npy, td_flux_<u>.npy) are BINNING-INDEPENDENT (they reweight
    events, not bins) -> reused verbatim as symlinks.

So the 4D throw bank is the 5D bank with the W axis dropped. Two coordinate views
are taken from of_inputs_4d (NOT the 5D bank) to stay bit-consistent with the
frozen 4D central unfold:
  * MCgen/MCreco/measured : 4D (pt,pz,Eavail,q3) columns from of_inputs_4d
    (the 5D bank's q3 has 1327 extra NaNs and a per-dimension measured target).
  * measured / measured_weights : the 4D data target from of_inputs_4d.
The truth-denom per-event arrays (td_pt/pz/ea/q3/td_w) come from the 5D bank
(of_inputs_4d only stores the binned denom_nd); truth is dimension-agnostic and
the CV-reproduces-central check below proves the binning is consistent.

  python assemble_bank_4d_from5d.py   # -> uq_4d/corrected/bank_uthrow_4d/{cv.npz, symlinks}
"""
import os
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
SRC5 = f"{_REPO}/nd-unfolding/bank_uthrow_5d"
DST = f"{_REPO}/nd-unfolding/uq_4d/corrected/bank_uthrow_4d"
OF4 = f"{_REPO}/nd-unfolding/of_inputs_4d.npz"


def main():
    os.makedirs(DST, exist_ok=True)
    z4 = np.load(OF4, allow_pickle=True)
    b5 = np.load(os.path.join(SRC5, "cv.npz"), allow_pickle=True)

    # --- alignment guards (fail loudly rather than silently misbin) ---
    assert z4["w_truth"].shape == b5["w_truth"].shape, "event-count mismatch 4d vs bank5"
    assert np.abs(z4["w_truth"].astype(np.float64) - b5["w_truth"].astype(np.float64)).max() == 0, \
        "w_truth ordering drift: 5D weight arrays are NOT event-aligned to of_inputs_4d"
    assert np.abs(z4["w_reco"].astype(np.float64) - b5["w_reco"].astype(np.float64)).max() == 0, \
        "w_reco ordering drift"
    for i in range(4):
        e4 = np.asarray(z4[f"edges_{i}"], float)
        e5 = np.asarray(b5[f"edges_{i}"], float)
        assert e4.shape == e5.shape and np.allclose(e4, e5), f"edge drift axis {i}"
    for i in range(3):  # pt,pz,eavail MCgen columns must be identical (q3 taken from 4D)
        assert np.abs(z4["MCgen"][:, i].astype(np.float64)
                      - b5["MCgen"][:, i].astype(np.float64)).max() == 0, f"MCgen col {i} drift"

    MCgen = z4["MCgen"].astype(np.float32)     # (N,4) pt,pz,eavail,q3 -- frozen 4D coords
    MCreco = z4["MCreco"].astype(np.float32)
    measured = z4["measured"].astype(np.float32)                 # (Nd,4)
    measured_weights = z4["measured_weights"].astype(np.float64)  # 4D data target

    out = dict(
        MCgen=MCgen, MCreco=MCreco,
        measured=measured, measured_weights=measured_weights,
        pass_reco=z4["pass_reco"], pass_truth=z4["pass_truth"],
        w_truth=z4["w_truth"], w_reco=z4["w_reco"],
        # truth-denom per-event arrays from the 5D bank (truth is dimension-agnostic)
        td_pt=b5["td_pt"], td_pz=b5["td_pz"], td_ea=b5["td_ea"],
        td_q3=b5["td_q3"], td_w=b5["td_w"],
        flux=z4["flux"], data_pot=z4["data_pot"], n_nucleons=z4["n_nucleons"],
        edges_0=np.asarray(z4["edges_0"], float), edges_1=np.asarray(z4["edges_1"], float),
        edges_2=np.asarray(z4["edges_2"], float), edges_3=np.asarray(z4["edges_3"], float))
    np.savez(os.path.join(DST, "cv.npz"), **out)
    print(f"[4d-bank] wrote cv.npz: MCgen{MCgen.shape} measured{measured.shape} "
          f"edges={[len(out[f'edges_{i}'])-1 for i in range(4)]}")

    # symlink the binning-independent per-event weight arrays from the 5D bank
    n = 0
    for fn in sorted(os.listdir(SRC5)):
        if (fn.startswith("sig_") or fn.startswith("td_")) and fn.endswith(".npy"):
            link = os.path.join(DST, fn)
            if os.path.islink(link) or os.path.exists(link):
                os.remove(link)
            os.symlink(os.path.join(SRC5, fn), link)
            n += 1
    print(f"[4d-bank] symlinked {n} per-event weight arrays from {SRC5}")


if __name__ == "__main__":
    main()
