#!/usr/bin/env python3
"""MP-2 S2, R12 (binding addendum 14 §4): GiBUU's charmed hadrons are decayed before any feature or product.

Decayer: PYTHIA 6.426's decay tables, as GENIE 2.12.10's PythiaDecayer uses them (UPS pythia v6_4_28k gcc640-prof
libPythia6.so, the library the frozen GENIE samples linked), with GENIE's decayer flags: MSTJ(22) = 1 and pi0 stable
(MDCY(pi0,1) = 0), PYTHIA defaults otherwise. The table is recorded by its PYUPDA(1) dump's sha256.

Each charmed parent is placed alone in PYJETS with GiBUU's four-momentum (its mass from E^2 - p^2) and decayed by
PYEXEC, which cascades (MSTJ(22) = 1) until only species with MDCY(KC,1) = 0 remain. PYTHIA's generator is reseeded
before every parent from numpy default_rng([2026102134, 0x4348]), one integer in [0, 900000000) per parent, in the
declared order (the caller's entry order, then list order): MRPY(1) = that integer, MRPY(2) = 0. The decay is in the
generator frame, before the whole-event rotation.

Fail-closed checks; each is recorded with a pass flag, and the caller takes the branch from the flags alone:
  table      for every species decayed, its channels' BRAT sum to 1 to 1e-6; the dump's sha256 is the declared one
  decay      per parent, the products' four-momentum equals the parent's to 1e-9 relative to the parent's energy;
             PYTHIA's error counter MSTU(23) does not move
  no charm   no product carries a charm quark
  species    every product is a species found in Tune's C+H in-grid lists
"""
from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

LIBGFORTRAN = "/cvmfs/larsoft.opensciencegrid.org/products/gcc/v6_4_0/Linux64bit+3.10-2.17/lib64/libgfortran.so.3"
LIBPYTHIA6 = "/cvmfs/larsoft.opensciencegrid.org/products/pythia/v6_4_28k/Linux64bit+3.10-2.17-gcc640-prof/lib/libPythia6.so"
LIBPYTHIA6_SHA = "670555a48da4aa7e369bc918a9d5e82565bd409b8f1a5bd49c2a02a887d72cbd"
TABLE_DUMP_SHA = "6e0fbd89ea709d5a2f9cc6fc2d959f28ad188a56f4ff6bb6a4f8cc6283ee2cb4"   # PYUPDA(1), PYTHIA defaults
RNG_SEED = [2026102134, 0x4348]
BR_TOL, P4_TOL = 1e-6, 1e-9
MRPY_MAX = 900_000_000
# GiBUU (ID, charge) -> PDG for the charmed hadrons (GiBUU 2019 code/database/IdTable.f90, sha256 67b31fd5...:
# 56 Lambda_c+, 57 Sigma_c, 58 Sigma_c*, 59 Xi_c, 60 Xi_c*, 61 Omega_c; 108 eta_c, 109 J/psi, 114 D (D0, D+),
# 115 Dbar (D-, Dbar0), 116 D*, 117 D*bar, 118 D_s+, 119 D_s-, 120 D_s*+, 121 D_s*-). Each is asserted against
# PYTHIA's own name for the code before use.
GIBUU_CHARM = {(56, 1): (4122, "Lambda_c+"), (57, 0): (4112, "Sigma_c0"), (57, 1): (4212, "Sigma_c+"),
               (57, 2): (4222, "Sigma_c++"), (58, 0): (4114, "Sigma*_c0"), (58, 1): (4214, "Sigma*_c+"),
               (58, 2): (4224, "Sigma*_c++"), (59, 0): (4132, "Xi_c0"), (59, 1): (4232, "Xi_c+"),
               (60, 0): (4314, "Xi*_c0"), (60, 1): (4324, "Xi*_c+"), (61, 0): (4332, "Omega_c0"),
               (108, 0): (441, "eta_c"), (109, 0): (443, "J/psi"),
               (114, 0): (421, "D0"), (114, 1): (411, "D+"), (115, -1): (-411, "D-"), (115, 0): (-421, "Dbar0"),
               (116, 0): (423, "D*0"), (116, 1): (413, "D*+"), (117, -1): (-413, "D*-"), (117, 0): (-423, "D*bar0"),
               (118, 1): (431, "D_s+"), (119, -1): (-431, "D_s-"), (120, 1): (433, "D*_s+"), (121, -1): (-433, "D*_s-")}
GIBUU_CHARM_IDS = {56, 57, 58, 59, 60, 61, 108, 109, 114, 115, 116, 117, 118, 119, 120, 121}


def sha256(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def has_charm(kf: np.ndarray) -> np.ndarray:
    """A hadron code (|kf| < 1e6) with a charm quark digit, or a charm (anti)quark itself."""
    a = np.abs(np.asarray(kf, np.int64))
    had = a < 1_000_000
    q = [(a // 10) % 10, (a // 100) % 10, (a // 1000) % 10]
    return (a == 4) | (had & ((q[0] == 4) | (q[1] == 4) | (q[2] == 4)))


_DUMP = (f"import ctypes; ctypes.CDLL({LIBGFORTRAN!r}, mode=ctypes.RTLD_GLOBAL); "
         f"py = ctypes.CDLL({LIBPYTHIA6!r}, mode=ctypes.RTLD_GLOBAL); "
         "m, u = ctypes.c_int(1), ctypes.c_int(31); py.pyupda_(ctypes.byref(m), ctypes.byref(u))")


class _PYJETS(ctypes.Structure):
    _fields_ = [("n", ctypes.c_int), ("npad", ctypes.c_int), ("k", ctypes.c_int * 20000),
                ("p", ctypes.c_double * 20000), ("v", ctypes.c_double * 20000)]


class _PYDAT1(ctypes.Structure):
    _fields_ = [("mstu", ctypes.c_int * 200), ("paru", ctypes.c_double * 200), ("mstj", ctypes.c_int * 200),
                ("parj", ctypes.c_double * 200)]


class _PYDAT3(ctypes.Structure):
    _fields_ = [("mdcy", ctypes.c_int * 1500), ("mdme", ctypes.c_int * 16000), ("brat", ctypes.c_double * 8000),
                ("kfdp", ctypes.c_int * 40000)]


class _PYDATR(ctypes.Structure):
    _fields_ = [("mrpy", ctypes.c_int * 6), ("rrpy", ctypes.c_double * 100)]


class Pythia6Decayer:
    MAXN = 4000

    def __init__(self, workdir: Path):
        if sha256(LIBPYTHIA6) != LIBPYTHIA6_SHA:
            raise SystemExit(f"STOP: {LIBPYTHIA6} is not the declared build")
        ctypes.CDLL(LIBGFORTRAN, mode=ctypes.RTLD_GLOBAL)
        self.py = py = ctypes.CDLL(LIBPYTHIA6, mode=ctypes.RTLD_GLOBAL)
        py.pycomp_.restype = ctypes.c_int
        self.J = _PYJETS.in_dll(py, "pyjets_")
        self.D1 = _PYDAT1.in_dll(py, "pydat1_")
        self.D3 = _PYDAT3.in_dll(py, "pydat3_")
        self.DR = _PYDATR.in_dll(py, "pydatr_")
        self.record = {"library": {"path": LIBPYTHIA6, "sha256": LIBPYTHIA6_SHA},
                       "libgfortran": {"path": LIBGFORTRAN, "sha256": sha256(LIBGFORTRAN)}}
        # the table as shipped (BLOCK DATA defaults of this library): PYUPDA(1) writes it to Fortran unit 31. A child
        # process dumps it and exits, so gfortran has flushed fort.31 before it is hashed (an open unit is not)
        with tempfile.TemporaryDirectory(dir=workdir) as td:
            subprocess.run([sys.executable, "-I", "-c", _DUMP], cwd=td, check=True, stdout=subprocess.DEVNULL)
            dump_sha = sha256(Path(td) / "fort.31")
        self.record["table_dump_sha256"] = dump_sha
        self.record["table_dump_is_declared"] = dump_sha == TABLE_DUMP_SHA
        if dump_sha != TABLE_DUMP_SHA:
            raise SystemExit(f"STOP: PYTHIA6 table dump {dump_sha} is not the declared {TABLE_DUMP_SHA}")
        self.D3.mdcy[self.kc(111) - 1] = 0              # GENIE: pi0 stable
        self.D1.mstj[21] = 1                            # MSTJ(22) = 1, as PythiaDecayer::Decay sets it
        self.record["flags"] = {"MSTJ(22)": 1, "MDCY(pi0,1)": 0, "otherwise": "PYTHIA 6.426 defaults"}
        for (gid, q), (kf, name) in GIBUU_CHARM.items():
            got = self.name(kf)
            if got != name:
                raise SystemExit(f"STOP: GiBUU ({gid},{q}) -> {kf}: PYTHIA calls it {got!r}, not {name!r}")
        self.reset()

    def reset(self):
        """A fresh generator from the declared seed, for a call over the declared order."""
        self.rng = np.random.default_rng(RNG_SEED)
        self.decayed_kc: set[int] = set()

    def kc(self, kf: int) -> int:
        x = ctypes.c_int(int(kf))
        return int(self.py.pycomp_(ctypes.byref(x)))

    def name(self, kf: int) -> str:
        buf = ctypes.create_string_buffer(16)
        x = ctypes.c_int(int(kf))
        self.py.pyname_(ctypes.byref(x), buf, ctypes.c_int(16))
        return buf.value.decode().strip()

    def br_sum(self, kc: int) -> float:
        i0, n = self.D3.mdcy[500 + kc - 1], self.D3.mdcy[1000 + kc - 1]
        return float(sum(self.D3.brat[i - 1] for i in range(i0, i0 + n)))

    def decay(self, kf: int, E: float, px: float, py: float, pz: float):
        """One parent (GeV). Returns (kf, E, px, py, pz) arrays of its stable products, the relative four-momentum
        residual, and whether PYTHIA's error counter moved."""
        J, M = self.J, self.MAXN
        self.DR.mrpy[0] = int(self.rng.integers(0, MRPY_MAX))
        self.DR.mrpy[1] = 0
        err0 = self.D1.mstu[22]
        J.n = 1
        for c in range(5):
            J.k[c * M] = 0
            J.v[c * M] = 0.0
        J.k[0], J.k[M] = 1, int(kf)
        m2 = E * E - (px * px + py * py + pz * pz)
        J.p[0], J.p[M], J.p[2 * M], J.p[3 * M], J.p[4 * M] = px, py, pz, E, float(np.sqrt(max(m2, 0.0)))
        self.py.pyexec_()
        n = J.n
        ks = np.array([J.k[i] for i in range(n)])
        kfs = np.array([J.k[M + i] for i in range(n)], np.int64)
        P = np.array([[J.p[c * M + i] for c in range(4)] for i in range(n)])
        for i in np.nonzero(ks >= 11)[0]:
            self.decayed_kc.add(self.kc(kfs[i]))
        fin = (ks >= 1) & (ks <= 10)
        s = P[fin].sum(axis=0)
        resid = float(np.max(np.abs(s - np.array([px, py, pz, E]))) / E)
        return kfs[fin], P[fin, 3], P[fin, 0], P[fin, 1], P[fin, 2], resid, bool(self.D1.mstu[22] != err0)


_DECAYER = None


def decayer(workdir: Path) -> Pythia6Decayer:
    """One decayer per process: the library is loaded and its table dumped (before GENIE's flags) once."""
    global _DECAYER
    if _DECAYER is None:
        _DECAYER = Pythia6Decayer(workdir)
    else:
        _DECAYER.reset()
    return _DECAYER


def decay_entries(ent: dict, pid_charge: tuple[np.ndarray, np.ndarray], tune_species: set[int], workdir: Path):
    """Replace every charmed hadron in the ragged final-state lists of ent (fs_pdg, fs_E, fs_px, fs_py, fs_pz in MeV,
    fs_offsets) by its PYTHIA6 decay products, in entry order then list order. pid_charge: the GiBUU (ID, charge) of
    each list entry. Returns (new ent, the pre-decay lists kept as fs0_*, the check record)."""
    pid, ch = pid_charge
    off = ent["fs_offsets"]
    n_ev = off.size - 1
    row = np.repeat(np.arange(n_ev), np.diff(off))
    is_c = np.isin(pid, list(GIBUU_CHARM_IDS))
    unknown = sorted({(int(a), int(b)) for a, b in zip(pid[is_c], ch[is_c]) if (int(a), int(b)) not in GIBUU_CHARM})
    rec = {"rng_seed": RNG_SEED, "n_parents": int(is_c.sum()), "n_events_with_charm": int(np.unique(row[is_c]).size),
           "unknown_charm_codes": [list(u) for u in unknown]}
    if unknown:
        rec["checks"] = {"known_codes": False}
        return None, rec
    dec = decayer(workdir)
    rec["decayer"] = dec.record
    parents = np.nonzero(is_c)[0]
    prod, worst, n_err, species, mix = {}, 0.0, 0, {}, {}
    for idx in parents.tolist():
        kf = GIBUU_CHARM[(int(pid[idx]), int(ch[idx]))][0]
        mix[kf] = mix.get(kf, 0) + 1
        k, E, x, y, z, r, err = dec.decay(kf, ent["fs_E"][idx] / 1000.0, ent["fs_px"][idx] / 1000.0,
                                          ent["fs_py"][idx] / 1000.0, ent["fs_pz"][idx] / 1000.0)
        worst, n_err = max(worst, r), n_err + int(err)
        prod[idx] = (k, 1000.0 * E, 1000.0 * x, 1000.0 * y, 1000.0 * z)
        for v in k.tolist():
            species[v] = species.get(v, 0) + 1
    br = {int(c): dec.br_sum(c) for c in sorted(dec.decayed_kc)}          # every species PYTHIA decayed, parents included
    br_bad = {c: s for c, s in br.items() if abs(s - 1.0) > BR_TOL}
    out_species = np.fromiter(species, np.int64)
    rec["parent_mix"] = {str(k): v for k, v in sorted(mix.items())}
    rec["product_species"] = {str(k): v for k, v in sorted(species.items())}
    rec["checks"] = {
        "known_codes": True,
        "table_declared": bool(dec.record["table_dump_is_declared"]),
        "br_sum_per_decayed_species": {"n_species": len(br), "max_abs_dev": float(max(abs(v - 1.0) for v in br.values())) if br else None,
                                       "tol": BR_TOL, "failing_kc": {str(c): v for c, v in br_bad.items()}, "pass": bool(br) and not br_bad},
        "four_momentum": {"max_rel_residual": worst, "tol": P4_TOL, "pass": worst <= P4_TOL},
        "pythia_errors": {"n_parents_with_error": n_err, "pass": n_err == 0},
        "no_charm": {"n_charm_products": int(has_charm(out_species).sum()) if out_species.size else 0},
        "tune_species": {"not_in_tune": sorted(int(s) for s in species if s not in tune_species)},
    }
    rec["checks"]["no_charm"]["pass"] = rec["checks"]["no_charm"]["n_charm_products"] == 0
    rec["checks"]["tune_species"]["pass"] = not rec["checks"]["tune_species"]["not_in_tune"]
    rec["pass"] = all(v["pass"] for v in rec["checks"].values() if isinstance(v, dict)) and rec["checks"]["table_declared"]
    # rebuild the ragged lists: each parent replaced in place by its products
    cnt = np.diff(off).astype(np.int64)
    for idx, (k, *_r) in prod.items():
        cnt[row[idx]] += k.size - 1
    new_off = np.concatenate([[0], np.cumsum(cnt)]).astype(np.int64)
    cols = {c: [] for c in ("fs_pdg", "fs_E", "fs_px", "fs_py", "fs_pz")}
    pos = 0
    for idx in parents.tolist() + [off[-1]]:
        if idx > pos:
            for c in cols:
                cols[c].append(np.asarray(ent[c][pos:idx]))
        if idx < off[-1]:
            k, E, x, y, z = prod[idx]
            for c, v in zip(cols, (k, E, x, y, z)):
                cols[c].append(np.asarray(v, np.int64 if c == "fs_pdg" else float))
        pos = idx + 1
    new = dict(ent)
    for c in cols:
        new[c] = np.concatenate(cols[c]).astype(ent[c].dtype)
        new["fs0_" + c[3:]] = ent[c]
    new["fs_offsets"], new["fs0_offsets"] = new_off, off
    if new["fs_pdg"].size != new_off[-1]:
        raise SystemExit("STOP: the rebuilt lists do not match their offsets")
    # event-level: every event's summed four-momentum is unchanged (to the per-decay tolerance)
    r0 = np.repeat(np.arange(n_ev), np.diff(off))
    r1 = np.repeat(np.arange(n_ev), np.diff(new_off))
    ev_res = max(float(np.max(np.abs(np.bincount(r1, new[c], n_ev) - np.bincount(r0, ent[c], n_ev))) /
                       max(1.0, float(np.max(np.bincount(r0, ent["fs_E"], n_ev))))) for c in ("fs_E", "fs_px", "fs_py", "fs_pz"))
    rec["checks"]["event_four_momentum"] = {"max_abs_residual_over_max_event_E": ev_res, "tol": P4_TOL, "pass": ev_res <= P4_TOL}
    rec["pass"] = rec["pass"] and rec["checks"]["event_four_momentum"]["pass"]
    return new, rec
