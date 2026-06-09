#!/usr/bin/env python3
"""Assemble bank_uthrow_4d/ : the 4D (pt,pz,eavail,q3) sibling of bank_uthrow.

The unified-throw bank is 3D; the published systematic covariance is 4D (q3 added).
The per-event universe-weight arrays (sig_<band>_{t,r}_<idx>.npy, td_<band>_<idx>.npy,
flux) are binning-INDEPENDENT -- they reweight events, not bins -- so the 4D bank reuses
them verbatim (symlinks). Only the COORDINATE/binning arrays in cv.npz change:

  MCgen, MCreco  : +q3 column from the PC cloud (verified bit-identical to the bank rows)
  measured, measured_weights : the 4D data + 4D training weights from of_inputs_4d.npz
  td_pt/pz/ea/q3, td_w       : the 4D truth-denom from dump_td_q3.py (ordering-proofed)
  edges_3, flux, data_pot, n_nucleons : 4D edges + the (pt-axis) flux/POT/nucleons

  python assemble_bank_4d.py    # writes bank_uthrow_4d/cv.npz + symlinks weights
"""
import os
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
SRC = f"{_REPO}/nd-unfolding/bank_uthrow"
DST = f"{_REPO}/nd-unfolding/bank_uthrow_4d"


def main():
    os.makedirs(DST, exist_ok=True)
    cv = np.load(os.path.join(SRC, "cv.npz"), allow_pickle=True)
    pc = np.load(f"{_REPO}/nd-unfolding/of_inputs_pc.npz", allow_pickle=True)
    z4 = np.load(f"{_REPO}/nd-unfolding/of_inputs_4d.npz")
    tdq = np.load(os.path.join(SRC, "td_q3.npz"))

    # --- alignment guards (fail loudly rather than silently misbin) ---
    assert np.abs(cv["w_truth"] - pc["w_truth"]).max() == 0, "bank<->PC w_truth drift"
    assert np.abs(cv["MCgen"][:, 2].astype(np.float64)
                  - pc["truth_scalars"][:, 2].astype(np.float64)).max() == 0, "eavail drift"
    assert np.abs(cv["td_w"].astype(np.float64) - tdq["td_w"].astype(np.float64)).max() < 1e-6, \
        "td_q3 ordering does not match the bank"
    assert cv["measured"].shape[0] == z4["measured"].shape[0], "measured count mismatch"
    assert np.abs(cv["measured"][:, 2].astype(np.float64)
                  - z4["measured"][:, 2].astype(np.float64)).max() == 0, "measured eavail drift"

    q3_truth = pc["truth_scalars"][:, 3].astype(np.float32)
    q3_reco = pc["reco_scalars"][:, 3].astype(np.float32)
    MCgen = np.column_stack([cv["MCgen"], q3_truth]).astype(np.float32)
    MCreco = np.column_stack([cv["MCreco"], q3_reco]).astype(np.float32)
    measured = z4["measured"].astype(np.float32)              # (Nd,4) pt,pz,ea,q3
    measured_weights = z4["measured_weights"].astype(np.float64)

    out = dict(
        MCgen=MCgen, MCreco=MCreco,
        measured=measured, measured_weights=measured_weights,
        pass_reco=cv["pass_reco"], pass_truth=cv["pass_truth"],
        w_truth=cv["w_truth"], w_reco=cv["w_reco"],
        td_pt=tdq["td_pt"], td_pz=tdq["td_pz"], td_ea=tdq["td_ea"],
        td_q3=tdq["td_q3"], td_w=tdq["td_w"],
        flux=cv["flux"], data_pot=cv["data_pot"], n_nucleons=cv["n_nucleons"],
        edges_0=cv["edges_0"], edges_1=cv["edges_1"], edges_2=cv["edges_2"],
        edges_3=z4["edges_3"].astype(np.float64))
    np.savez(os.path.join(DST, "cv.npz"), **out)
    print(f"[4d-bank] wrote cv.npz: MCgen{MCgen.shape} measured{measured.shape} "
          f"edges={[len(out[f'edges_{i}'])-1 for i in range(4)]}")

    # symlink the binning-independent weight arrays
    n = 0
    for fn in os.listdir(SRC):
        if fn.startswith("sig_") or fn.startswith("td_") or fn == "flux_univ_ratio.npy":
            if fn == "td_q3.npz":
                continue
            link = os.path.join(DST, fn)
            if os.path.islink(link) or os.path.exists(link):
                os.remove(link)
            os.symlink(os.path.join(SRC, fn), link)
            n += 1
    print(f"[4d-bank] symlinked {n} weight arrays from {SRC}")


if __name__ == "__main__":
    main()
