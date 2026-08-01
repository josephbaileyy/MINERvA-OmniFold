#!/usr/bin/env python3
"""Emit a small SYNTHETIC g2-fullevent-v1 NPZ so the full-event code path can be exercised
without the real 9.9 GB G2 dump.

WHY THIS EXISTS: `fullevent_fps_dataloader.build_fullevent_loaders` fail-closes on any input
that is not `g2-fullevent-v1` (dataloader ~L497). The only such file is
`/pscratch/.../G2_FPS_MEFHC_P12.npz`, which is unreachable during the 2026-07-22..08-03
Perlmutter maintenance. So between those dates NOTHING on Delta can reach the Gate-4 / P5A
code path. This generator produces a contract-valid stand-in so the launcher, the dataloader,
the Gate-2 validator and the closure can be smoke-run against real code paths.

WHAT THIS IS NOT: the numbers are drawn from a random generator. Nothing produced from this
fixture is a physics result. Every file carries `synthetic_fixture=1` and a
`synthetic_provenance` string; downstream consumers should refuse to publish anything whose
input carries that marker. Do not commit weights trained on this into products/pet/ without
`synthetic` in the filename.

The write goes through `fullevent_dump_contract.write_fullevent_npz_atomic`, so the fixture
is validated by the SAME gates as a real dump (schema markers, complete 36-key manifest,
inventory alignment, identity hashes, no-purity-fallback). If those gates change, this
generator fails loudly rather than emitting a stale-shaped file.

Login-safe: numpy only, no TensorFlow, no ROOT.

Usage:
  python3 make_synthetic_g2_fullevent.py --out /tmp/G2_SYNTH.npz --n-sig 20000 --n-data 4000
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import fullevent_dump_contract as fdc          # noqa: E402
import fullevent_fps_dataloader as fe          # noqa: E402

# Token-cloud column contracts, mirrored from the dataloader docstrings. The clouds are stored
# in DUMP units (MeV / mm); `_scale_clean` divides by 1000 downstream. Padding sentinel is
# energy(col 0) == 0, so padded tokens must be exactly zero.
_PDG_CHOICES = np.array([211, -211, 2212, 2112, 111, 22], dtype=np.float32)


def _clouds(rng, n, tokens, ncol):
    """(n, tokens, ncol) cloud with a per-row random real-token count and zero padding."""
    a = np.zeros((n, tokens, ncol), dtype=np.float32)
    nreal = rng.integers(1, tokens + 1, size=n)
    for i in range(n):                          # explicit loop: fixtures are small, clarity wins
        k = int(nreal[i])
        a[i, :k, 0] = rng.uniform(5.0, 500.0, k)          # E (MeV), strictly > 0 => real token
        if ncol == 3:                                     # recoil: E, pos, z
            a[i, :k, 1] = rng.uniform(-1000.0, 1000.0, k)  # pos (mm)
            a[i, :k, 2] = rng.uniform(4000.0, 9000.0, k)   # z (mm)
        else:                                             # truth: E, px, py, pz, pdg
            a[i, :k, 1] = rng.normal(0.0, 200.0, k)        # px (MeV)
            a[i, :k, 2] = rng.normal(0.0, 200.0, k)        # py (MeV)
            a[i, :k, 3] = rng.uniform(0.0, 2000.0, k)      # pz (MeV)
            a[i, :k, 4] = rng.choice(_PDG_CHOICES, k)      # pdg
    return a, nreal


def _apply_sentinel(arr, pass_reco, minos_col=None):
    """Stamp the dump's !pass_reco convention onto a reco-side block.

    `dump_pointcloud_inputs.reco_scalar_row` / `reco_muon_row` / `reco_vertex_row` write
    -9999 on every row with no reconstructed muon (minos_ok gets 0, not -9999). Before
    2026-08-01 this generator filled plausible values on every row, so the fixture never
    exercised the masked-normalization path that the whole event-feature block depends on --
    and, since the reduced schema read only clean columns, nothing noticed. Widening the block
    makes that path load-bearing on eleven more columns, so the fixture has to be faithful."""
    if pass_reco is None:
        return arr
    miss = ~np.asarray(pass_reco, bool)
    arr[miss, :] = fe.SENTINEL
    if minos_col is not None:
        arr[miss, minos_col] = 0.0
    return arr


def _scalars(rng, n, pass_reco=None):
    """(n,4) = pt, p_parallel, eavail, q3 in GeV, drawn strictly INSIDE the canonical extended
    FPS grid so the domain-retention guards keep every row (they fail closed on out-of-domain).
    GeV, not MeV: the P5A record quotes raw reco_norm_mean 0.73 / 6.09 GeV.

    `pass_reco` (reco-side inventories only) stamps the -9999 miss sentinel."""
    s = np.zeros((n, 4), dtype=np.float32)
    s[:, 0] = rng.uniform(0.05, 4.0, n)          # pt   (grid tops out at 30.0)
    s[:, 1] = rng.uniform(1.6, 20.0, n)          # p||  (grid spans 0 .. 120.0)
    s[:, 2] = rng.uniform(0.0, 3.0, n)           # eavail
    s[:, 3] = rng.uniform(0.0, 2.5, n)           # q3
    return _apply_sentinel(s, pass_reco)


def _muon(rng, n, pass_reco=None):
    """(n,7) = px, py, pz, E, phi, qp, minos_ok -- the EXACT order of
    `dump_pointcloud_inputs.RECO_MUON_BRANCHES`, which is what produced the real G2 dump.

    This was a 6-column [px,py,pz,E,charge,quality] PLACEHOLDER until 2026-08-01, and the
    docstring said so. It survived because the dump contract's `assert_inventory_alignment`
    checks the muon block's ROW count and never its width, and no consumer read the columns --
    so a fixture that disagreed with the dumper about what column 4 means passed every gate.
    Now that `fullevent_fps_dataloader` reads the block, the width is checked where it is
    consumed (`assert_evt_block_widths`) and this layout is pinned against the dumper's own
    constant by `test_fullevent_schema.py`."""
    m = np.zeros((n, 7), dtype=np.float32)
    m[:, 0] = rng.normal(0.0, 500.0, n)                       # px (MeV)
    m[:, 1] = rng.normal(0.0, 500.0, n)                       # py (MeV)
    m[:, 2] = rng.uniform(1500.0, 20000.0, n)                 # pz (MeV)
    m[:, 3] = np.sqrt(m[:, 0] ** 2 + m[:, 1] ** 2 + m[:, 2] ** 2 + 105.66 ** 2)   # E (MeV)
    # phi spans the FULL (-pi, pi] so the fixture actually exercises the wrap the loader's
    # (cos, sin) encoding exists for; a [0, 1) placeholder would not.
    m[:, 4] = np.arctan2(m[:, 1], m[:, 0])                    # phi (rad), consistent with px,py
    m[:, 5] = -1.0 / np.maximum(m[:, 3], 1.0)                 # qp = charge/p (negative muon)
    m[:, 6] = (rng.random(n) < 0.97).astype(np.float32)       # minos_ok, mostly matched
    return _apply_sentinel(m, pass_reco, minos_col=6)


def _vertex(rng, n, pass_reco=None):
    """(n,3) = x,y,z (mm) inside a tracker-like fiducial volume
    (`dump_pointcloud_inputs.RECO_VERTEX_BRANCHES` order)."""
    v = np.zeros((n, 3), dtype=np.float32)
    v[:, 0] = rng.uniform(-850.0, 850.0, n)
    v[:, 1] = rng.uniform(-850.0, 850.0, n)
    v[:, 2] = rng.uniform(5990.0, 8340.0, n)
    return _apply_sentinel(v, pass_reco)


def _view_time(rng, n, tokens, nreal):
    """Per-token view id and hit time; length must equal the cloud token dim P (contract L88-95)."""
    view = np.zeros((n, tokens), dtype=np.int8)
    time = np.zeros((n, tokens), dtype=np.float32)
    for i in range(n):
        k = int(nreal[i])
        view[i, :k] = rng.integers(1, 4, k)                # X/U/V
        time[i, :k] = rng.uniform(-50.0, 50.0, k)          # ns, relative
    return view, time


def build(n_sig, n_data, n_bkg, tokens, seed, fingerprint):
    rng = np.random.default_rng(seed)

    part_reco, nreal_s = _clouds(rng, n_sig, tokens, 3)
    part_gen, _ = _clouds(rng, n_sig, tokens, 5)
    measured_pc, nreal_d = _clouds(rng, n_data, tokens, 3)
    bkg_part_reco, nreal_b = _clouds(rng, n_bkg, tokens, 3)

    reco_view, reco_time = _view_time(rng, n_sig, tokens, nreal_s)
    data_view, data_time = _view_time(rng, n_data, tokens, nreal_d)
    bkg_view, bkg_time = _view_time(rng, n_bkg, tokens, nreal_b)

    # pass fractions chosen to match the observed full-stats run (pass_reco ~0.418). Drawn BEFORE
    # the reco-side blocks so their -9999 miss sentinels land on the same rows the dump would put
    # them on -- the masked-normalization path is only exercised if the two agree.
    pass_reco = rng.random(n_sig) < 0.418
    pass_truth = rng.random(n_sig) < 0.99
    w_truth = rng.lognormal(0.0, 0.15, n_sig).astype(np.float32)
    w_reco = rng.lognormal(0.0, 0.15, n_sig).astype(np.float32)
    w_bkg = rng.lognormal(0.0, 0.20, n_bkg).astype(np.float32)   # POSITIVE; loader negates it
    bkg_indices = np.arange(n_bkg, dtype=np.int64)

    data_pot, mc_pot = 1.0e20, 1.0e21                             # => pot_scale 0.1

    arrays = {
        # ---- reco (signal MC): the ONLY inventory with misses, hence the only one sentinelled ----
        "part_reco": part_reco, "reco_scalars": _scalars(rng, n_sig, pass_reco),
        "reco_muon": _muon(rng, n_sig, pass_reco),
        "reco_vertex": _vertex(rng, n_sig, pass_reco),
        "reco_view": reco_view, "reco_time": reco_time,
        # ---- data: every row is reconstructed by construction, so no sentinel ----
        "measured_pc": measured_pc, "measured_scalars": _scalars(rng, n_data),
        "data_muon": _muon(rng, n_data), "data_vertex": _vertex(rng, n_data),
        "data_view": data_view, "data_time": data_time,
        # ---- truth ----
        "part_gen": part_gen,
        # ---- background MC: reco-selected and domain-gated at dump time, so no sentinel ----
        "bkg_part_reco": bkg_part_reco, "bkg_reco_scalars": _scalars(rng, n_bkg),
        "bkg_muon": _muon(rng, n_bkg), "bkg_vertex": _vertex(rng, n_bkg),
        "bkg_view": bkg_view, "bkg_time": bkg_time, "w_bkg": w_bkg,
        "bkg_indices": bkg_indices,
        # ---- audit-only generator labels (never classifier features) ----
        "bkg_nuPDG": rng.choice(np.array([14, -14, 12], np.int32), n_bkg),
        "bkg_current": rng.choice(np.array([1, 2], np.int32), n_bkg),
        "bkg_inttype": rng.choice(np.array([1, 2, 3, 4], np.int32), n_bkg),
        # ---- globals ----
        "edges_0": fe.CANONICAL_PT_EDGES, "edges_1": fe.CANONICAL_PPARALLEL_EDGES,
        "pass_reco": pass_reco, "pass_truth": pass_truth,
        "w_truth": w_truth, "w_reco": w_reco, "truth_scalars": _scalars(rng, n_sig),
        "petSchemaVersion": np.asarray("g2-fullevent-v1"),
        "hasFullEventSchema": np.asarray(1), "fullPhaseSpace": np.asarray(1),
        "estimator_fingerprint": np.asarray(fingerprint),
        "data_pot": np.asarray(data_pot), "mc_pot": np.asarray(mc_pot),
        # ---- SYNTHETIC MARKERS (not part of the G2 contract; refuse to publish on these) ----
        "synthetic_fixture": np.asarray(1),
        "synthetic_provenance": np.asarray(
            f"make_synthetic_g2_fullevent.py seed={seed} n_sig={n_sig} n_data={n_data} "
            f"n_bkg={n_bkg} tokens={tokens} -- RANDOM DATA, NOT A PHYSICS RESULT"),
    }

    # Identity hashes over the SAME stable-order evidence the loader recomputes
    # (dataloader _verify_stored_identity / contract assert_identity_consistency).
    arrays["sig_identity_hash"] = np.asarray(
        fe.inventory_order_hash(arrays["w_truth"], arrays["pass_truth"]))
    arrays["data_identity_hash"] = np.asarray(
        fe.inventory_order_hash(arrays["measured_pc"]))
    arrays["bkg_identity_hash"] = np.asarray(
        fe.inventory_order_hash(arrays["w_bkg"], arrays["bkg_indices"]))
    return arrays


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", required=True, help="output .npz path")
    p.add_argument("--n-sig", type=int, default=20000, help="signal-MC rows")
    p.add_argument("--n-data", type=int, default=4000, help="data rows")
    p.add_argument("--n-bkg", type=int, default=1500, help="background-MC rows")
    p.add_argument("--tokens", type=int, default=40, help="cloud token dim P")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--fingerprint", default="pet-fullevent-fps-v1",
                   help="estimator_fingerprint to stamp; the launcher gate expects the default")
    p.add_argument("--bkg-mode", default="negweight-refined",
                   choices=("negweight-refined", "purity"))
    p.add_argument("--receipt", default=None, help="optional path for a JSON receipt")
    a = p.parse_args()

    arrays = build(a.n_sig, a.n_data, a.n_bkg, a.tokens, a.seed, a.fingerprint)
    # Runs schema + manifest + alignment + identity + no-purity-fallback gates, THEN writes.
    fdc.write_fullevent_npz_atomic(a.out, arrays, bkg_mode=a.bkg_mode)

    h = hashlib.sha256()
    with open(a.out, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    size = os.path.getsize(a.out)
    receipt = {
        "schema": "synthetic-g2-fullevent-fixture-v1",
        "path": os.path.abspath(a.out), "sha256": h.hexdigest(), "size_bytes": size,
        "n_sig": a.n_sig, "n_data": a.n_data, "n_bkg": a.n_bkg, "tokens": a.tokens,
        "seed": a.seed, "estimator_fingerprint": a.fingerprint, "bkg_mode": a.bkg_mode,
        "members": sorted(arrays.keys()),
        "IS_SYNTHETIC": True,
        "warning": "RANDOM DATA. Plumbing/launch-path validation only. Never a physics result.",
    }
    print(json.dumps(receipt, indent=2))
    if a.receipt:
        with open(a.receipt, "w") as fh:
            json.dump(receipt, fh, indent=2)
    print(f"\n[synthetic-g2] wrote {a.out} ({size/1e6:.1f} MB)", file=sys.stderr)
    print(f"[synthetic-g2] sha256 {h.hexdigest()}", file=sys.stderr)
    print("[synthetic-g2] SYNTHETIC -- do not publish anything derived from this file.",
          file=sys.stderr)


if __name__ == "__main__":
    main()
