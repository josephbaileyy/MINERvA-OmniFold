#!/usr/bin/env python3
"""Is `rescale_flux_universes.py`'s correction really an IDENTITY? Test it on production throws.

The tool's docstring claims the J28 correction is exact, not an approximation:

    x_corrected[i_pt, ...] = x_saved[i_pt, ...] / r_u[i_pt],   r_u = Phi_u / Phi_CV

because flux normalisation enters only at final extraction and `extract_cross_section_nd` divides by
the flux along pT alone. That claim has never been checked against an independent computation -- the
whole J28 remediation rests on it, and the ledger quarantine is lifted on its strength.

An accidental experiment now makes it checkable. Regenerating the lost throws re-ran array task 30,
which covers throws 120-123. So throws 120 and 121 exist in TWO independent forms:

  * `uq_5d/rescaled_20260806/uthrow5d_slab_30.npz` -- the OLD Phi_CV-normalised throw, corrected
    post-hoc by the rescale tool;
  * `uq_5d/uthrow_slabs_5d_sb/uthrow5d_slab_30.npz` -- the SAME throw (same RNG stream, hence the same
    knob draws g_b and the same flux universe u, since `unified_throw_cov.py:222-223` seeds per global
    throw index) recomputed from scratch by a driver that now divides by Phi_u natively.

If the rescale is an identity these must agree to floating-point noise. If they disagree, the post-hoc
correction is wrong and every rescaled number is suspect. This is the strongest available check on it
and it costs nothing.
"""
import numpy as np

OLD_RESCALED = "uq_5d/rescaled_20260806/uthrow5d_slab_30.npz"
NEW_NATIVE = "uq_5d/uthrow_slabs_5d_sb/uthrow5d_slab_30.npz"


def load(path):
    with np.load(path, allow_pickle=True) as d:
        return {
            "xs": np.asarray(d["xs"], float),
            "throws": np.atleast_1d(d["throws"]).ravel().astype(int),
            "flux_u": np.atleast_1d(d["flux_u"]).ravel().astype(int),
            "stamped": "flux_normalized" in d.files and int(d["flux_normalized"]) == 1,
        }


def main():
    a, b = load(OLD_RESCALED), load(NEW_NATIVE)
    print(f"post-hoc rescaled : throws {a['throws'].tolist()} flux_u {a['flux_u'].tolist()} "
          f"stamped={a['stamped']}")
    print(f"natively corrected: throws {b['throws'].tolist()} flux_u {b['flux_u'].tolist()} "
          f"stamped={b['stamped']}")

    shared = [t for t in a["throws"] if t in set(b["throws"].tolist())]
    if not shared:
        raise SystemExit("no throw present in both forms yet -- wait for task 30 to write more")
    print(f"\nthrows present in BOTH forms: {shared}")

    ok = True
    for t in shared:
        ia = int(np.where(a["throws"] == t)[0][0])
        ib = int(np.where(b["throws"] == t)[0][0])
        # The same throw must have drawn the same flux universe, or the RNG is not
        # reproducible per index and the comparison is meaningless.
        if a["flux_u"][ia] != b["flux_u"][ib]:
            print(f"  throw {t}: FLUX UNIVERSE DIFFERS ({a['flux_u'][ia]} vs {b['flux_u'][ib]}) -- "
                  f"the RNG is not per-index reproducible; comparison invalid")
            ok = False
            continue
        xa, xb = a["xs"][ia], b["xs"][ib]
        nz = (np.abs(xa) > 0) | (np.abs(xb) > 0)
        denom = np.maximum(np.abs(xa), np.abs(xb))
        rel = np.zeros_like(xa)
        rel[nz] = np.abs(xa[nz] - xb[nz]) / denom[nz]
        print(f"  throw {t} (flux_u={a['flux_u'][ia]}): "
              f"max|rel diff| = {rel.max():.3e}   median = {np.median(rel[nz]):.3e}   "
              f"bins compared = {int(nz.sum())}")
        if rel.max() > 1e-9:
            worst = int(np.argmax(rel))
            print(f"      worst bin {worst}: rescaled {xa[worst]:.9e} vs native {xb[worst]:.9e}")
            ok = False

    print("\n" + ("IDENTITY CONFIRMED on production throws (agreement at float noise)"
                  if ok else "*** RESCALE IS NOT AN IDENTITY -- every rescaled number is suspect ***"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
