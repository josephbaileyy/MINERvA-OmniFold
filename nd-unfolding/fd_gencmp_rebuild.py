#!/usr/bin/env python3
"""GENCMP step B rebuild (state/measurement-paper/5d-community-20261024/FD-GENCMP-DECLARATION.md section 1, section 3
and the chain of section 5): the truth-level 5D generator predictions on the 65,856-cell fine grid (C order pt, pz,
eavail, q3, W), rebuilt from the event records in the generators' own definitions and in the analysis definitions.

MP-5's GENIE check (measurement-paper/phase1/mp5/mp5_genie.py) generalised to every sample:

* ``gen``       n = z and the generator's own W: control B0, the frozen product reproduced bitwise (xsec and sumw2),
                and the restated event reader aligned bitwise with the frozen extractor (MP-5's G1, extended).
* ``wonly``     n = z, analysis W (struck-nucleon M, W^2 < 0 dropped); control B2 is read on its main part.
* ``ana_s<s>``  one drawn n per entry for each seed in fd_gencmp_kin.SEEDS (MP-5's per-E_nu-bin pool draw), beam-frame
                pT, p_par and phase-space decision, analysis W, W^2 < 0 dropped before histogramming.
* ``axisonly``  drawn n (SEEDS[0]) with the generator's W convention (fixed M, W = 0 clamp): MP-5's check build.
* ``ana_mn``    gibuu_C12 only: as ana_s<SEEDS[0]> with M = M_n (the present convention), to bound the M choice.

Normalisation, flux-fix weights and the 50-100 GeV supplement are the frozen chain's (gen5d_flux_reweight.build_genie,
build_weighted_nuwro, flux_weights, r_of; mp3c_build.weights, build; mp3b_build.flat_arrays). Restated, each with a
bitwise control: MP-5's lepton/phase-space/W statements (generalised), the GiBUU per-file event statements (with px,
py, E_mu kept and before the phase-space mask), the GENIE supplement formula (two lines of
gen5d_flux_supplement.cmd_supplement), the flux-fix constants A and B (cmd_reweight), and mp3c_build.gibuu_density
(it opens its files by path).

I/O (section 1): every input is checked against INPUTS.sha256 before use; /pscratch files are read through
os.open(O_RDONLY | O_NOATIME) with atime compared; ROOT files are served to the frozen code as TMemFiles over those
bytes (MemROOT, installed as the ``ROOT`` global of every frozen module), so the frozen RDataFrame paths run unchanged
and any ROOT read of an unverified path is refused. Outputs only under --out, which must not exist. Before any module
of the frozen code tree is imported, every .py file of --gen5d-tree-src is copied through the same pinned reader into
<out>/frozen_tree (INPUTS family H; an unpinned, absent or mismatched file refuses with exit 2) and imported from there.

Outputs: <out>/<sample>_<variant>.npz (xsec_flat, sumw2_flat, nevt_flat float64 (65856,), meta_json) and
<out>/rebuild.json. No variant file of a sample is written before its B0 passes, and none after a B2 stop.
rebuild.json["status"][sample] = {"B0": bool, "B2": "pass"|"stop"|"n/a", "complete": bool, "variants_written": [...]},
complete meaning B0 passed, B2 did not stop and every declared variant was written. B2 stops genie_cv or nuwro_C12 if
its wonly main-part in-phase-space count differs from M4-W's, or its W^2 < 0 fraction is outside a factor 2 of M4-W's.
Exit 0 every sample complete; 3 a sample stopped (B0, B2, input refusal, error); 2 refused to start.

MEASURES: the rebuilt products and controls B0, B1 (printed), B2. CANNOT AUTHORIZE: a Table IV number, a claim or
paper text, or a reading of the products (the declaration's CANNOT AUTHORIZE).
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import io
import json
import multiprocessing as mp
import os
import resource
import sys
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
_REPO = HERE.parent
for _p in (str(HERE), str(_REPO / "measurement-paper" / "phase1" / "mp3b"),
           str(_REPO / "measurement-paper" / "phase1" / "mp3c")):
    if _p not in sys.path:
        sys.path.append(_p)
import numpy as np  # noqa: E402

import fd_gencmp_kin as kin  # noqa: E402
import gen5d_flux_reweight as gfr  # noqa: E402
import gen5d_flux_supplement as sup  # noqa: E402
import mp3b_build as mp3b  # noqa: E402
import mp3c_build as mp3c  # noqa: E402
import mp5_genie as mp5  # noqa: E402

PSCRATCH = "/pscratch/"
INPUTS = _REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/gencmp/INPUTS.sha256"
MP3B_GEN = "/pscratch/sd/j/josephrb/measurement-paper/phase1/mp3b/runA/gen"
MP3C_PROD = "/pscratch/sd/j/josephrb/measurement-paper/phase1/mp3c/prod"
POOL_DIR = "/pscratch/sd/j/josephrb/measurement-paper/phase1/mp5/run/pool"
P1 = _REPO / "docs/orchestration/state/measurement-paper/phase1"
MP3B_NPZ = str(P1 / "mp3b/runA/out_r2/build_k1/mp3b_fine_nuwro.npz")
MP3C_NPZ = str(P1 / "mp3c/out_b/eval_frozen/mp3c_fine_gibuu_frozen.npz")
N_FINE = 65856
SAMPLES = ("genie_cv", "genie_mec", "nuwro_C12", "nuwro_H", "gibuu_C12", "gibuu_H")
# M4-W (state/2d-closeout/stageF/methods/m4-w/probe_gen.json): in-phase-space events with W^2 < 0 under the analysis W,
# n = z, the < 50 GeV sample only; B2 compares the same population (wonly, main part)
M4W_REF = {"genie_cv": (29, 938141), "nuwro_C12": (37, 1261997)}
# MP-5 REPORT.md:26-27, the measured nu-to-beam angle (printed beside B1; its pool-level summary is not committed)
MP5_ALPHA_MRAD = {"median": 1.03, "r68": [0.50, 1.92], "max": 6.9,
                  "source": "docs/orchestration/state/measurement-paper/phase1/mp5/REPORT.md:26-27"}
_G5 = None          # gen_to_xsec5d, for the GiBUU pool workers (set before the fork)


class InputRefused(Exception):
    """An input that is not pinned, differs from its pin, or cannot be read under the section 1 rule."""


# ---------------------------------------------------------------- inputs (section 1)


def read_pins(files, root: Path = _REPO) -> dict[str, str]:
    """{absolute path: sha256} from INPUTS.sha256-format files; repository-relative paths resolve against root."""
    pins: dict[str, str] = {}
    for f in files:
        for line in Path(f).read_text().splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            digest, p = s.split(None, 1)
            if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
                raise ValueError(f"{f}: not a sha256 line: {line!r}")
            p = os.path.normpath(p.strip() if os.path.isabs(p.strip()) else os.path.join(root, p.strip()))
            if pins.get(p, digest) != digest:
                raise ValueError(f"{p}: two different pins")
            pins[p] = digest
    return pins


def _read_all(fd: int) -> bytes:
    chunks = []
    while True:
        b = os.read(fd, 1 << 26)
        if not b:
            return b"".join(chunks)
        chunks.append(b)


def read_noatime(path: str) -> tuple[bytes, dict]:
    """The file's bytes through an O_NOATIME descriptor (required on /pscratch) and the atime before and after."""
    p = os.path.abspath(path)
    flag = getattr(os, "O_NOATIME", 0)
    on_ps = p.startswith(PSCRATCH)
    if on_ps and not flag:
        raise InputRefused(f"{p}: O_NOATIME is not available here")
    st0 = os.stat(p)
    try:
        fd, used = os.open(p, os.O_RDONLY | flag), bool(flag)
    except PermissionError:
        if on_ps:
            raise InputRefused(f"{p}: O_NOATIME open refused (not the owner)") from None
        fd, used = os.open(p, os.O_RDONLY), False
    try:
        buf = _read_all(fd)
    finally:
        os.close(fd)
    st1 = os.stat(p)
    return buf, {"path": p, "bytes": len(buf), "sha256": hashlib.sha256(buf).hexdigest(), "o_noatime": used,
                 "atime_ns_before": st0.st_atime_ns, "atime_ns_after": st1.st_atime_ns,
                 "atime_unchanged": st0.st_atime_ns == st1.st_atime_ns}


def read_pinned(path: str, want: str | None) -> tuple[bytes, dict]:
    p = os.path.abspath(path)
    if want is None:
        raise InputRefused(f"{p}: not in the pinned inputs")
    buf, rec = read_noatime(p)
    rec.update(sha256_pinned=want, sha256_match=rec["sha256"] == want)
    if not rec["sha256_match"]:
        raise InputRefused(f"{p}: sha256 {rec['sha256']} differs from the pinned {want}", rec)
    return buf, rec


class Inputs:
    """Every read checked against its pin and logged (digest, O_NOATIME, atime before/after)."""

    def __init__(self, pins: dict[str, str]):
        self.pins = dict(pins)
        self.records: list[dict] = []
        self.meta_pins: list[dict] = []

    def log(self, rec: dict) -> None:
        self.records.append(rec)

    def read(self, path: str) -> bytes:
        p = os.path.abspath(path)
        try:
            buf, rec = read_pinned(p, self.pins.get(p))
        except InputRefused as e:
            if len(e.args) > 1:
                self.log(e.args[1])
            raise
        self.log(rec)
        return buf

    def pin_from_meta(self, path: str, record: dict | None, source: str) -> None:
        """A pin for a file INPUTS.sha256 lacks, taken from a verified product's own input record (--allow-meta-pin)."""
        p = os.path.abspath(path)
        if p in self.pins or not record or os.path.abspath(record.get("path", "")) != p or not record.get("sha256"):
            return
        self.pins[p] = record["sha256"]
        self.meta_pins.append({"path": p, "sha256": record["sha256"], "source": source})

    def deviations(self) -> list[str]:
        return [r["path"] for r in self.records if not r["atime_unchanged"]]


def tmemfile(root, name: str, buf: bytes):
    """A TMemFile over a copy of buf (TMemFile(name, buffer, size, option) copies at construction)."""
    errs = []
    for make in (lambda: buf, lambda: bytearray(buf)):
        try:
            f = root.TMemFile(name, make(), len(buf), "READ")
        except Exception as e:  # noqa: BLE001 -- the next form is tried, then refused
            errs.append(repr(e))
            continue
        if f and not f.IsZombie():
            return f
        errs.append("zombie")
    raise InputRefused(f"{name}: the verified bytes do not open as a TMemFile ({errs})")


class _MemTFile:
    def __init__(self, mem: "MemROOT"):
        self._mem = mem

    def Open(self, path, option: str = "READ", *rest):  # noqa: N802 -- ROOT's name
        if str(option).upper() not in ("", "READ"):
            raise InputRefused(f"{path}: {option} through the input proxy")
        return self._mem.open(path)

    def __call__(self, *a, **k):
        raise InputRefused("TFile constructed directly; only TFile.Open reads are served")

    def __getattr__(self, name):
        return getattr(self._mem._root.TFile, name)


class MemROOT:
    """ROOT with TFile.Open(path) and RDataFrame(tree, path) served from bytes the Inputs reader verified."""

    def __init__(self, root):
        self.__dict__.update(_root=root, _bufs={}, _open=[], TFile=_MemTFile(self))

    def __getattr__(self, name):
        return getattr(self._root, name)

    def __setattr__(self, name, value):
        setattr(self._root, name, value)

    def add(self, path: str, buf: bytes) -> None:
        self._bufs[os.path.abspath(path)] = buf

    def release(self) -> None:
        self._open.clear()
        self._bufs.clear()

    def open(self, path):
        p = os.path.abspath(str(path))
        if p not in self._bufs:
            raise InputRefused(f"{p}: a ROOT read outside the verified inputs")
        f = tmemfile(self._root, p, self._bufs[p])
        self._open.append(f)
        return f

    def RDataFrame(self, *args):  # noqa: N802 -- ROOT's name
        if len(args) == 2 and isinstance(args[1], (str, os.PathLike)):
            f = self.open(args[1])
            t = f.Get(str(args[0]))
            if not t:
                raise InputRefused(f"tree {args[0]} not in {args[1]}")
            self._open.append(t)
            return self._root.RDataFrame(t)
        return self._root.RDataFrame(*args)


def install_memroot(root, mem: MemROOT, roots) -> list[str]:
    """Replace the ``ROOT`` global of every imported module under roots (the frozen code) that holds the real ROOT."""
    done, roots = [], [str(Path(r).resolve()) + os.sep for r in roots]
    for name, m in list(sys.modules.items()):
        f = getattr(m, "__file__", None) if m is not None else None
        if f and any(str(Path(f).resolve()).startswith(r) for r in roots) and getattr(m, "ROOT", None) is root:
            m.ROOT = mem
            done.append(name)
    return sorted(done)


# ---------------------------------------------------------------- the per-entry record and its selection


@dataclass
class Part:
    """One file group of a sample (main, supp): per-entry arrays and the frozen chain's statements for it.
    lepton is (px, py, pz) in the generator frame, or (pt, None, pz) where the azimuth is not stored (NuWro)."""
    name: str
    cc: np.ndarray
    enu: np.ndarray
    emu: np.ndarray
    eavail: np.ndarray
    lepton: tuple
    hitnuc: np.ndarray | None
    ps: Callable            # (cc, pt, pz) -> bool per entry
    wgen: Callable          # (sel, (qx, qy, qz), costh, axis_is_z) -> generator-convention W of sel
    q3: Callable            # keep -> q3 of keep
    build: Callable         # (keep, cols) -> (xsec, sumw2, nevt), flat
    diag: Callable | None = None
    info: dict = field(default_factory=dict)

    @property
    def n(self) -> int:
        return int(self.cc.size)


@dataclass(frozen=True)
class Variant:
    name: str
    seed: int | None        # None: n = z
    w: str                  # "gen" or "ana"
    m_fixed: float | None = None


def variants(sample: str) -> list[Variant]:
    v = [Variant("gen", None, "gen"), Variant("wonly", None, "ana")]
    v += [Variant(f"ana_s{s}", s, "ana") for s in kin.SEEDS]
    v.append(Variant("axisonly", kin.SEEDS[0], "gen"))
    if sample == "gibuu_C12":
        v.append(Variant("ana_mn", kin.SEEDS[0], "ana", kin.CVU_M_N))
    return v


def directions(sample: str, part: Part, seed: int, pools) -> tuple[np.ndarray, np.ndarray]:
    """MP-5's draw for every CC entry from draws(seed, '<sample>:<part>'); non-CC entries keep n = z."""
    u, phi = kin.draws(seed, f"{sample}:{part.name}", part.n)
    n = kin.unit_z(part.n)
    m = part.cc
    n[m] = kin.draw_directions(u[m], part.enu[m], pools, kin.ENU_BINS_GEV)
    return n, phi


def select(p: Part, n=None, phi=None, w: str = "gen", m_fixed: float | None = None):
    """(keep, cols, counts): the in-phase-space entries (entry order) and their 5D coordinates in the beam frame of n
    (n = None: the generator axis). w = 'ana' drops W^2 < 0 entries before anything is histogrammed."""
    px, py, pz = p.lepton
    if py is None:
        px, py, pz = kin.lepton_from_pt_pz(px, pz, np.zeros(p.n) if phi is None else phi)
    nn = kin.unit_z(p.n) if n is None else n
    q = kin.rotate(np.asarray(px, float), np.asarray(py, float), np.asarray(pz, float), nn)
    pt, pzb, costh = kin.beam_frame(px, py, pz, nn)
    sel = np.flatnonzero(p.ps(p.cc, pt, pzb))
    if w == "gen":
        W, keep = p.wgen(sel, q, costh, n is None), sel
        n_drop = 0
    else:
        if m_fixed is not None:
            M = m_fixed
        else:
            M = kin.struck_mass(p.hitnuc[sel] if p.hitnuc is not None else np.zeros(sel.size, int))
        W = kin.w_analysis(p.enu[sel], p.emu[sel], costh[sel], M)
        ok = ~np.isnan(W)
        keep, W, n_drop = sel[ok], W[ok], int((~ok).sum())
    cols = {"pt": pt[keep], "pz": pzb[keep], "eavail": p.eavail[keep], "q3": p.q3(keep), "W": W}
    return keep, cols, {"n_entries": p.n, "n_cc": int(p.cc.sum()), "n_in_ps": int(sel.size),
                        "n_W2_negative_dropped": n_drop, "n_kept": int(keep.size)}


def assemble(sample: str, parts: list[Part], var: Variant, pools, cache: dict):
    """The variant's product: per part select then the part's frozen builder; parts add in order (main + supp)."""
    x = v = nev = None
    counts, cols_of = {}, {}
    for p in parts:
        n = phi = None
        if var.seed is not None:
            key = (var.seed, p.name)
            if key not in cache:
                cache[key] = directions(sample, p, var.seed, pools)
            n, phi = cache[key]
        keep, cols, cnt = select(p, n, phi, var.w, var.m_fixed)
        xp, vp, np_ = (np.asarray(a, float).reshape(-1) for a in p.build(keep, cols))
        if p.diag is not None:
            cnt.update(p.diag(keep))
        counts[p.name], cols_of[p.name] = cnt, (keep, cols)
        x, v, nev = (xp, vp, np_) if x is None else (x + xp, v + vp, nev + np_)
    return x, v, nev, counts, cols_of


# ---------------------------------------------------------------- the three event readers


def _ps_vector(g5) -> Callable:
    """extract_nuwro's / extract_gibuu's in-phase-space mask (gen_to_xsec5d.py), with the CC gate."""
    PT, PZ, MAX = g5.EDGES["pt"], g5.EDGES["pz"], g5.u3d.u2d.MAX_MUON_THETA_RAD

    def ps(cc, pt, pz):
        with np.errstate(invalid="ignore"):
            return (cc & np.isfinite(pt) & np.isfinite(pz) & (pt >= PT[0]) & (pt <= PT[-1]) & (pz >= PZ[0])
                    & (pz <= PZ[-1]) & (np.arctan2(pt, pz) < MAX))
    return ps


def _ps_genie(g5) -> Callable:
    """extract_genie's / mp5_genie.events' per-entry in_truth_phase_space loop."""
    in_ps = g5.u3d.u2d.in_truth_phase_space
    lo_t, hi_t, lo_z, hi_z = g5.PT[0], g5.PT[-1], g5.PZ[0], g5.PZ[-1]

    def ps(cc, pt, pz):
        return np.fromiter((c and in_ps(float(a), float(b), lo_t, hi_t, lo_z, hi_z)
                            for c, a, b in zip(cc.tolist(), pt.tolist(), pz.tolist())), dtype=bool, count=cc.size)
    return ps


def genie_part(name: str, d: dict, g5, build: Callable, info: dict) -> Part:
    Ev, pxv, pyv, pzv, El = (np.asarray(d[k]) for k in ("Ev", "pxv", "pyv", "pzv", "El"))
    pxl, pyl, pzl = (np.asarray(d[k]) for k in ("pxl", "pyl", "pzl"))
    w_true = g5.gew.w_true

    def wgen(sel, q, costh, axis_z):
        qx, qy, qz = q
        return np.fromiter((w_true((a, b, c, e), (f, g, h, i)) for a, b, c, e, f, g, h, i in
                            zip(Ev[sel].tolist(), pxv[sel].tolist(), pyv[sel].tolist(), pzv[sel].tolist(),
                                El[sel].tolist(), qx[sel].tolist(), qy[sel].tolist(), qz[sel].tolist())),
                           dtype=float, count=sel.size)

    def q3(keep):
        return g5.q3_true(Ev[keep], pxv[keep], pyv[keep], pzv[keep], El[keep], pxl[keep], pyl[keep], pzl[keep])[1]

    return Part(name, np.asarray(d["cc"]).astype(bool), Ev, El, np.asarray(d["eav5d"]), (pxl, pyl, pzl),
                np.asarray(d["hitnuc"]), _ps_genie(g5), wgen, q3, build,
                info={**info, "mec": np.asarray(d["mec"]).astype(bool),
                      "nu_along_z": bool(np.all(pxv == 0) and np.all(pyv == 0))})


def nuwro_part(name: str, d: dict, g5, build: Callable, info: dict) -> Part:
    enu, emu = d["Enu"], d["Enu"] - d["q0"]          # extract_nuwro: Emu = Enu - q0
    Wst, q3 = d["W"], d["q3"]

    def wgen(sel, q, costh, axis_z):
        if axis_z:
            return Wst[sel]
        return np.nan_to_num(kin.w_analysis(enu[sel], emu[sel], costh[sel], kin.GEN_M_FIXED), nan=0.0)

    return Part(name, d["cc"].astype(bool), enu, emu, d["eavail"], (d["pt"], None, d["pz"]), d["hitnuc"],
                _ps_vector(g5), wgen, lambda keep: q3[keep], build, info=info)


def nuwro_arrays(mem, files) -> tuple[dict, float]:
    """mp3b_build.flat_arrays over the files in order, concatenated; N_total summed as extract_nuwro sums it."""
    acc, n_total = {k: [] for k in mp3b.FLAT_BRANCHES}, 0
    for fn in files:
        d, nt = mp3b.flat_arrays(mem, fn)
        n_total += int(nt)
        for k in mp3b.FLAT_BRANCHES:
            acc[k].append(d[k])
    return {k: np.concatenate(v) for k, v in acc.items()}, float(n_total)


def gibuu_entries(g5, d: np.ndarray) -> dict:
    """gen5d_flux_supplement.gibuu_events' per-file statements (= extract_gibuu's) before the phase-space mask, with the
    muon's px, py, pz, E and E_nu kept per event: the rows of events with a muon and perweight > 0."""
    gib3d, gibew = g5.gib3d, g5.gibew
    MASS_PI, MASS_P, MUON_IDS = gib3d.MASS_PI, gib3d.MASS_P, gibew.MUON_IDS
    if d.ndim == 1:
        d = d[None, :]
    run = d[:, 0].astype(np.int64); ev = d[:, 1].astype(np.int64)  # noqa: E702
    pid = d[:, 2].astype(int); ch = d[:, 3].astype(int)  # noqa: E702
    pw = d[:, 4]; E = d[:, 8]; px = d[:, 9]; py = d[:, 10]; pz = d[:, 11]  # noqa: E702
    enu = d[:, 14]
    key = run * 10_000_000 + ev
    ukey, inv = np.unique(key, return_inverse=True)
    nev = ukey.size
    lep = np.isin(pid, MUON_IDS)
    out = {k: np.full(nev, np.nan) for k in ("px", "py", "pz", "emu", "enu")}
    w_e = np.zeros(nev)
    li = inv[lep]
    out["px"][li] = px[lep]; out["py"][li] = py[lep]; out["pz"][li] = pz[lep]  # noqa: E702
    out["emu"][li] = E[lep]; out["enu"][li] = enu[lep]; w_e[li] = pw[lep]  # noqa: E702
    had = (pw != 0) & (~lep)
    econ = np.zeros(d.shape[0])
    m = had & (pid == 1) & (ch == 1);           econ[m] = E[m] - MASS_P  # noqa: E702
    m = had & (pid == 101) & (np.abs(ch) == 1); econ[m] = E[m] - MASS_PI  # noqa: E702
    m = had & (pid == 101) & (ch == 0);         econ[m] = E[m]  # noqa: E702
    m = had & (pid == 999);                     econ[m] = E[m]  # noqa: E702
    ea_e = np.zeros(nev)
    np.add.at(ea_e, inv, econ)
    _, q3_e = g5.q3_true(out["enu"], 0.0, 0.0, out["enu"], out["emu"], out["px"], out["py"], out["pz"])
    ok = np.isfinite(np.hypot(out["px"], out["py"])) & (w_e > 0)
    return {**{k: v[ok] for k, v in out.items()}, "w": w_e[ok], "eavail": ea_e[ok], "q3": q3_e[ok],
            "n_events": int(nev)}


def gibuu_wgen(gibew, pz, emu, enu) -> np.ndarray:
    """extract_gibuu's W (fixed M_N, theta from pz / p(E), 0 where W^2 <= 0), for any pz."""
    M_N, M_MU = gibew.M_NUCLEON, gibew.M_MU
    pmu = np.sqrt(np.clip(emu**2 - M_MU**2, 0, None))
    with np.errstate(invalid="ignore", divide="ignore"):
        costh = np.clip(pz / pmu, -1.0, 1.0)
        theta = np.arccos(costh)
        q2 = 4.0 * enu * emu * np.sin(theta / 2.0) ** 2
        w2 = M_N**2 + 2.0 * (enu - emu) * M_N - q2
        return np.where(w2 > 0, np.sqrt(np.clip(w2, 0, None)), 0.0)


def gibuu_part(name: str, e: dict, g5, hit: int | None, build: Callable, diag: Callable, info: dict) -> Part:
    gibew = g5.gibew

    def wgen(sel, q, costh, axis_z):
        return gibuu_wgen(gibew, q[2][sel], e["emu"][sel], e["enu"][sel])

    hitnuc = None if hit is None else np.full(e["w"].size, hit)
    return Part(name, np.ones(e["w"].size, bool), e["enu"], e["emu"], e["eavail"], (e["px"], e["py"], e["pz"]),
                hitnuc, _ps_vector(g5), wgen, lambda keep: e["q3"][keep], build, diag=diag, info=info)


def gibuu_density(flux_text: str, jobcard_text: str):
    """mp3c_build.gibuu_density (cmd_gibuu's phi_gibuu) on verified text; that function opens both files by path."""
    fl = np.loadtxt(io.StringIO(flux_text), comments="#")
    Eg, fg = fl[:, 0], fl[:, 1]
    step = float(np.median(np.diff(Eg)))
    if not np.allclose(np.diff(Eg), step):
        raise SystemExit("GiBUU flux points not equally spaced")
    cut_lo, cut_hi = 0.0, 20.0
    for line in jobcard_text.splitlines():
        s = line.split("!")[0].strip()
        if s.startswith("Enu_upper_cut"):
            cut_hi = float(s.split("=")[1])
        if s.startswith("Enu_lower_cut"):
            cut_lo = float(s.split("=")[1])
    fcut = np.where((Eg >= cut_lo) & (Eg <= cut_hi), fg, 0.0)
    g_edges = np.concatenate([Eg - 0.5 * step, [Eg[-1] + 0.5 * step]])
    g_edges[0] = max(g_edges[0], 0.0)
    phi_g = fcut / (step * fcut.sum())
    return g_edges, fcut, phi_g, (cut_lo, cut_hi), step


def _gibuu_job(job):
    """Pool worker: one FinalEvents.dat read under the section 1 rule, parsed once for the rebuild and once by the
    frozen extract_gibuu (the alignment reference)."""
    path, want = job
    buf, rec = read_pinned(path, want)
    text = buf.decode("ascii")
    del buf
    ent = gibuu_entries(_G5, np.loadtxt(io.StringIO(text), comments="#"))
    ref, _, _ = _G5.extract_gibuu([io.StringIO(text)])
    return rec, ent, {k: ref[k] for k in ("pt", "pz", "eavail", "q3", "W", "weight_raw")}


# ---------------------------------------------------------------- per-sample loaders


@dataclass
class Ctx:
    g5: object
    mem: MemROOT
    inputs: Inputs
    phi: tuple              # (edges, phi_t density, Phi_t)
    nproc: int = 32
    allow_meta_pin: bool = False
    chnative: tuple = ((), ())


def sample_files(ctx: Ctx, name: str) -> dict:
    """The event files of a sample: fixed paths of the frozen chain, or lists taken from the pins (sorted, as the
    frozen chain's sorted(glob)); the counts are checked."""
    G, pins = gfr.DEFAULTS["genie_dir"], ctx.inputs.pins

    def from_pins(pattern, n):
        got = sorted(p for p in pins if fnmatch.fnmatch(p, pattern))
        if len(got) != n:
            raise InputRefused(f"{pattern}: {len(got)} pinned files, expected {n}")
        return got

    if name in ("genie_cv", "genie_mec"):
        gst = "genie_mefhc_cv_ALL.gst.root" if name == "genie_cv" else "genie_mefhc_mec_ALL.gst.root"
        return {"main": [os.path.join(G, gst)], "supp": [sup.SUPP_FILES[name]]}
    if name == "nuwro_C12":
        return {"main": from_pins(os.path.join(gfr.DEFAULTS["gen5d_dir"], "nuwro_flat5d", "nuwro_flat5d_p*.root"), 8),
                "supp": [sup.SUPP_FILES["nuwro"]]}
    if name == "nuwro_H":
        return {"main": from_pins(f"{MP3B_GEN}/H_main/c*/a*/flat5d.root", 25),
                "supp": from_pins(f"{MP3B_GEN}/H_supp/c*/a*/flat5d.root", 5)}
    if name == "nuwro_CHnative":
        return {"main": [os.path.abspath(p) for p in ctx.chnative[0]],
                "supp": [os.path.abspath(p) for p in ctx.chnative[1]]}
    if name == "gibuu_C12":
        return {"main": from_pins(os.path.join(G, "work_gibuu_arr", "task*", "FinalEvents.dat"), 80)}
    if name == "gibuu_H":
        return {"main": from_pins(f"{MP3C_PROD}/task*/FinalEvents.dat", 80)}
    raise ValueError(name)


TARGETS = {   # B0's frozen products (path, xsec key, sumw2 key)
    "genie_cv": (os.path.join(sup.OUT, "genie_cv_xsec5d_full.npz"), "xsec_flat", "sumw2_flat"),
    "genie_mec": (os.path.join(sup.OUT, "genie_mec_xsec5d_full.npz"), "xsec_flat", "sumw2_flat"),
    "nuwro_C12": (os.path.join(sup.OUT, "nuwro_cv_xsec5d_full.npz"), "xsec_flat", "sumw2_flat"),
    "gibuu_C12": (os.path.join(sup.OUT, "gibuu_cv_xsec5d_fluxfix.npz"), "xsec_flat", "sumw2_flat"),
    "nuwro_H": (MP3B_NPZ, "xsec_H", "sumw2_H"),
    "gibuu_H": (MP3C_NPZ, "xsec_H", "sumw2_H"),
}


def load_npz(inputs: Inputs, path: str) -> dict:
    with np.load(io.BytesIO(inputs.read(path)), allow_pickle=False) as z:
        return {k: np.asarray(z[k]) for k in z.files}


def load_genie(ctx: Ctx, name: str, files: dict, tmeta: dict):
    g5, mem = ctx.g5, ctx.mem
    edges, phi_t, Phi_t = ctx.phi
    mec_mode = name == "genie_mec"
    G = gfr.DEFAULTS["genie_dir"]
    aux = {"main": (os.path.join(G, "xsec_graphs.root"), os.path.join(G, "flux_mefhc_numu.root")),
           "supp": (sup.GRAPHS_100, sup.FLUX_SUPP)}
    for p in [files["main"][0], files["supp"][0], *aux["main"], *aux["supp"]]:
        mem.add(p, ctx.inputs.read(p))
    dV5 = g5.widths(*g5.AXES)
    AX, E5 = g5.AXES, g5.EDGES
    parts, refs, checks = [], {}, {}
    for which in ("main", "supp"):
        path, (graphs, flux) = files[which][0], aux[which]
        d = mem.RDataFrame("gst", path).Define("eav5d", g5.EAVAIL_CPP).AsNumpy(mp5.RAW)
        d = {k: np.asarray(v) for k, v in d.items()}
        cc, mec = d["cc"].astype(bool), d["mec"].astype(bool)
        pop = (cc & ~mec) if mec_mode else cc
        if which == "main":
            e_s, c_s = gfr.read_th1(mem, flux, "flux_numu")
            lo, hi = gfr.GEN_RANGE[name]
            _, rbin, rng = gfr.flux_weights(e_s, c_s, phi_t, Phi_t, lo, hi)
            r_all = gfr.r_of(d["Ev"], e_s, rbin, rng)
            I = gfr.SigmaCC(mem, graphs, "CH").bin_integrals(e_s)
            A = float(np.sum(np.where(rng, phi_t / Phi_t, 0.0) * I))      # cmd_reweight: sigma_t50
            B = float(np.sum(r_all[pop]))                                  # cmd_reweight: Bsum

            def build(keep, cols, r_all=r_all, A=A, B=B):
                x, v = gfr.build_genie(g5, name, cols, r_all[keep], A, B, dV5)
                return x, v, g5.hist([cols[a] for a in AX], None, [E5[a] for a in AX])
            info = {"sigma_CC_t_lt50_per_nucleon_cm2": A, "sum_r_normalising_population": B, "N_pop": int(pop.sum())}
        else:
            sn = tmeta["supplement"]["normalisation"]
            S, N_pop, pe = sn["S_50_100_cm2"], sn["N_normalising_population"], sn["per_event_xsec_cm2"]
            checks["supp_N_pop_equals_product_meta"] = int(pop.sum()) == int(N_pop)

            def build(keep, cols, S=S, N_pop=N_pop, pe=pe):
                nevt = g5.hist([cols[a] for a in AX], None, [E5[a] for a in AX])
                x = S * (nevt / N_pop) / dV5 if name == "genie_cv" else nevt * pe / dV5    # cmd_supplement
                return x, nevt * (pe ** 2) / dV5 ** 2, nevt
            info = {"S_50_100_cm2": S, "N_normalising_population": N_pop, "per_event_xsec_cm2": pe}
        parts.append(genie_part(which, d, g5, build, info))
        checks[f"{which}_nu_along_z"] = parts[-1].info["nu_along_z"]
        refs[which] = g5.extract_genie(path, mec_mode, graphs, flux, "flux_numu", 0)[0]
    return parts, refs, checks


def load_nuwro(ctx: Ctx, name: str, files: dict, tmeta: dict | None):
    g5, mem = ctx.g5, ctx.mem
    edges, phi_t, Phi_t = ctx.phi
    flux_main = os.path.join(gfr.DEFAULTS["genie_dir"], "flux_mefhc_numu_nuwro.root")
    if not files["main"]:
        raise InputRefused(f"{name}: no main files")
    for p in [*files["main"], *files["supp"], flux_main] + ([sup.FLUX_SUPP] if files["supp"] else []):
        mem.add(p, ctx.inputs.read(p))
    dV5 = g5.widths(*g5.AXES)
    AX, E5 = g5.AXES, g5.EDGES
    parts, refs, checks = [], {}, {}
    for which in ("main", "supp"):
        if not files[which]:
            continue
        d, N_total = nuwro_arrays(mem, files[which])
        if which == "main":
            e_s, c_s = gfr.read_th1(mem, flux_main, "flux_numu")
            _, rbin, rng = gfr.flux_weights(e_s, c_s, phi_t, Phi_t, mp3b.LO_MAIN, mp3b.HI_MAIN)
            r_all = gfr.r_of(d["Enu"], e_s, rbin, rng)
            info = {"N_total": N_total, "flux_fix": "r(E) on [0.5, 50] GeV"}
        else:
            e2, c2 = gfr.read_th1(mem, sup.FLUX_SUPP, "flux_numu")
            _, rbin2, rng2 = gfr.flux_weights(e2, c2, phi_t, Phi_t, sup.LO, sup.HI)
            r_const = float(np.sum((phi_t * np.diff(edges))[rng2]) / Phi_t)
            checks["supp_r_is_constant"] = bool(np.allclose(rbin2[rng2], r_const, rtol=1e-12, atol=0))
            if tmeta is not None:
                checks["supp_r_constant_equals_product_meta"] = (
                    r_const == tmeta["supplement"]["normalisation"]["r_constant"])
            r_all = np.full(d["Enu"].size, r_const)
            info = {"N_total": N_total, "r_constant": r_const}
        weight = d["weight"]

        def build(keep, cols, r_all=r_all, N_total=N_total, weight=weight):
            x, v = gfr.build_weighted_nuwro(g5, {**cols, "weight_raw": weight[keep], "scale": 1.0}, r_all[keep],
                                            N_total, dV5)
            return x, v, g5.hist([cols[a] for a in AX], None, [E5[a] for a in AX])
        parts.append(nuwro_part(which, d, g5, build, info))
        ref, _, _ = g5.extract_nuwro(files[which], files[which])
        checks[f"{which}_N_total_equals_extract_nuwro"] = float(ref["divisor"]) == N_total
        refs[which] = ref
        parts[-1].info["weight"] = weight
    return parts, refs, checks


def load_gibuu(ctx: Ctx, name: str, files: dict, tmeta: dict | None):
    g5 = ctx.g5
    edges, phi_t, Phi_t = ctx.phi
    jobcard, flux = gfr.DEFAULTS["gibuu_jobcard"], gfr.DEFAULTS["gibuu_flux"]
    if ctx.allow_meta_pin and flux not in ctx.inputs.pins:
        fz = tmeta if name == "gibuu_C12" else json.loads(
            str(load_npz(ctx.inputs, TARGETS["gibuu_C12"][0])["meta_json"]))
        ctx.inputs.pin_from_meta(flux, fz.get("gibuu_sampled_density", {}).get("flux_file"),
                                 f"{TARGETS['gibuu_C12'][0]} meta gibuu_sampled_density.flux_file")
    g_edges, _, phi_g, cut, step = gibuu_density(ctx.inputs.read(flux).decode("ascii"),
                                                 ctx.inputs.read(jobcard).decode("ascii"))
    jobs = [(p, ctx.inputs.pins.get(p)) for p in files["main"]]
    with mp.get_context("fork").Pool(max(1, min(ctx.nproc, len(jobs)))) as pool:
        res = pool.map(_gibuu_job, jobs)
    for rec, _, _ in res:
        ctx.inputs.log(rec)
    keys = ("px", "py", "pz", "emu", "enu", "w", "eavail", "q3")
    e = {k: np.concatenate([r[1][k] for r in res]) for k in keys}
    ref = {k: np.concatenate([r[2][k] for r in res]) for k in ("pt", "pz", "eavail", "q3", "W", "weight_raw")}
    M = float(len(files["main"]))
    r_all, _ = mp3c.weights({"enu": e["enu"]}, g_edges, phi_g, edges, phi_t, Phi_t)
    w = e["w"]

    def build(keep, cols):
        return mp3c.build(g5, {**cols, "w": w[keep]}, M, r_all[keep])

    def diag(keep):
        return {"zero_flux_event": bool(mp3c.weights({"enu": e["enu"][keep]}, g_edges, phi_g, edges, phi_t,
                                                     Phi_t)[1])}
    hit = kin.PDG_P if name == "gibuu_H" else None
    part = gibuu_part("main", e, g5, hit, build, diag,
                      {"M_files": M, "n_events": int(sum(r[1]["n_events"] for r in res)), "cut_GeV": list(cut),
                       "flux_step_GeV": step, "weight": w,
                       "struck_M": "M_p (free proton)" if hit else "M_nucleon (no struck nucleon recorded)"})
    return [part], {"main": ref}, {}


LOADERS = {"genie_cv": load_genie, "genie_mec": load_genie, "nuwro_C12": load_nuwro, "nuwro_H": load_nuwro,
           "nuwro_CHnative": load_nuwro, "gibuu_C12": load_gibuu, "gibuu_H": load_gibuu}


# ---------------------------------------------------------------- controls


def alignment(parts: list[Part], cols_of: dict, refs: dict) -> dict:
    """The restated reader's gen selection against the frozen extractor's in-phase-space arrays, bitwise."""
    out = {}
    for p in parts:
        keep, cols = cols_of[p.name]
        ref = refs[p.name]
        mine = dict(cols)
        if "weight" in p.info:
            mine["weight_raw"] = p.info["weight"][keep]
        if "mec" in p.info:
            mine["is_mec"] = p.info["mec"][keep]
        out[p.name] = {k: bool(np.array_equal(mine[k], np.asarray(ref[k]))) for k in mine if k in ref}
    return out


def b2_rule(n_neg: int, n_ps: int, ref: tuple[int, int]) -> dict:
    """B2: the W^2 < 0 fraction within a factor 2 of M4-W's (both directions; a zero fraction fails)."""
    f, f_ref = n_neg / n_ps if n_ps else float("nan"), ref[0] / ref[1]
    ratio = f / f_ref
    return {"n_W2_negative": n_neg, "n_in_ps": n_ps, "fraction": f, "m4w": list(ref), "m4w_fraction": f_ref,
            "ratio": ratio, "rule": "0.5 <= fraction / M4-W fraction <= 2", "pass": bool(0.5 <= ratio <= 2.0)}


def _q(x: np.ndarray, w: np.ndarray | None = None) -> dict:
    if w is None:
        p = np.quantile(x, [0.16, 0.5, 0.84])
    else:
        o = np.argsort(x)
        c = np.cumsum(w[o]) / np.sum(w)
        p = np.interp([0.16, 0.5, 0.84], c, x[o])
    return {"median": float(p[1]), "r68": [float(p[0]), float(p[2])], "max": float(x.max())}


def b1_summary(pools) -> dict:
    """B1: angle(z, n) in mrad over MP-5's pools, recomputed (unweighted, and w_truth-weighted as drawn)."""
    al = [1e3 * np.arctan2(np.hypot(P[:, 0], P[:, 1]), P[:, 2]) for P in pools]
    a, w = np.concatenate(al), np.concatenate([P[:, 3] for P in pools])
    return {"all_bins": {"n": int(a.size), "unweighted": _q(a), "w_truth_weighted": _q(a, w)},
            "per_bin": [{"bin_GeV": [kin.ENU_BINS_GEV[b], kin.ENU_BINS_GEV[b + 1]], "n": int(x.size),
                         "unweighted": _q(x) if x.size else None} for b, x in enumerate(al)],
            "mp5_recorded": MP5_ALPHA_MRAD,
            "note": "printed, not gated: MP-5's pool-level alpha summary (mp5_tune.json direction_pool) is not "
                    "committed; "
                    "the recorded values are the measured nu-to-beam angle as REPORT.md section 1 states it"}


def _jsonable(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def write_variant(out: Path, sample: str, variant: str, x, v, n, meta: dict) -> dict:
    arrs = {"xsec_flat": x, "sumw2_flat": v, "nevt_flat": n}
    for k, a in arrs.items():
        if a.dtype != np.float64 or a.shape != (N_FINE,):
            raise ValueError(f"{sample}_{variant} {k}: {a.dtype} {a.shape}")
    p = out / f"{sample}_{variant}.npz"
    np.savez(p, **arrs, meta_json=np.asarray(json.dumps(meta, default=_jsonable)))
    return {"path": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}


# ---------------------------------------------------------------- the run


def is_complete(stat: dict, declared: list[Variant]) -> bool:
    """B0 passed, B2 did not stop, and every declared variant was written, in order."""
    return bool(stat["B0"] and stat["B2"] != "stop" and stat["variants_written"] == [v.name for v in declared])


class Run:
    def __init__(self, ctx: Ctx, out: Path, pool_dir: str):
        self.ctx, self.out, self.pool_dir = ctx, out, pool_dir
        self.pools = None
        self.res: dict = {"status": {}, "B0": {}, "B1": None, "B2": {}, "samples": {}, "outputs": {}}
        self.gen: dict = {}

    def load_pools(self):
        if self.pools is None:
            self.pools = [np.load(io.BytesIO(self.ctx.inputs.read(os.path.join(self.pool_dir, f"pool_b{b}.npy"))),
                                  allow_pickle=False) for b in range(len(kin.ENU_BINS_GEV) - 1)]
            self.res["B1"] = b1_summary(self.pools)
            print("B1", json.dumps(self.res["B1"]["all_bins"]), "MP-5:", json.dumps(MP5_ALPHA_MRAD), flush=True)
        return self.pools

    def sample(self, name: str) -> bool:
        """One sample's variants in order. Nothing is written before B0 passes; a B2 stop writes nothing further.
        status[name] = {B0, B2 ('pass'|'stop'|'n/a'), complete, variants_written}."""
        st = self.res["samples"].setdefault(name, {"status": "running"})
        stat = self.res["status"].setdefault(name, {"B0": False, "B2": "n/a", "complete": False,
                                                     "variants_written": []})
        ctx = self.ctx
        tgt = TARGETS.get(name)
        target = load_npz(ctx.inputs, tgt[0]) if tgt else None
        tmeta = json.loads(str(target["meta_json"])) if target is not None and "meta_json" in target else None
        files = sample_files(ctx, name)
        try:
            parts, refs, checks = LOADERS[name](ctx, name, files, tmeta)
        finally:
            ctx.mem.release()
        dV = ctx.g5.widths(*ctx.g5.AXES).reshape(-1)
        cache: dict = {}
        declared = variants(name)
        for var in declared:
            pools = self.load_pools() if var.seed is not None else None
            x, v, n, counts, cols_of = assemble(name, parts, var, pools, cache)
            meta = {"schema": "fd-gencmp-rebuild/1", "sample": name, "variant": var.name,
                    "axis": "generator (+z)" if var.seed is None else f"drawn per entry, seed {var.seed}",
                    "W": ("generator convention" if var.w == "gen" else
                          (f"analysis, M = {var.m_fixed!r}, W^2 < 0 dropped" if var.m_fixed is not None else
                           "analysis, struck-nucleon M, W^2 < 0 dropped")),
                    "files": files, "parts": counts, "normalisation": {p.name: {k: val for k, val in p.info.items()
                                                                                 if not isinstance(val, np.ndarray)}
                                                                        for p in parts},
                    "sigma_in_grid_cm2": float(x @ dV),
                    "declaration": "FD-GENCMP-DECLARATION.md section 3"}
            print(name, var.name, json.dumps(counts, default=_jsonable), flush=True)
            if var.name == "gen":
                b0 = self.b0(name, parts, refs, checks, cols_of, counts, target, tgt, x, v, n)
                meta["B0"] = b0
                stat["B0"] = b0["pass"]
                if not b0["pass"]:
                    st.update(status="STOP", stage="B0", reason="B0 failed; no variant written")
                    return False
                self.gen[name] = (x, v)
            if var.name == "wonly":
                b2 = self.b2(name, counts)
                stat["B2"] = "n/a" if "rule" not in b2 else ("pass" if b2["pass"] else "stop")
                if stat["B2"] == "stop":
                    st.update(status="STOP", stage="B2", reason=b2["stop_reason"])
                    return False
            self.res["outputs"][f"{name}_{var.name}"] = write_variant(self.out, name, var.name, x, v, n, meta)
            stat["variants_written"].append(var.name)
        stat["complete"] = is_complete(stat, declared)
        st["status"] = "done" if stat["complete"] else "STOP"
        return stat["complete"]

    def b2(self, name: str, counts: dict) -> dict:
        """B2 on wonly's main part (M4-W's population: n = z, < 50 GeV, in phase space). For genie_cv and nuwro_C12
        the in-phase-space count must equal M4-W's exactly and the W^2 < 0 fraction be within a factor 2 of its."""
        c = counts["main"]
        b2 = {"main": {"n_W2_negative": c["n_W2_negative_dropped"], "n_in_ps": c["n_in_ps"],
                       "fraction": c["n_W2_negative_dropped"] / max(c["n_in_ps"], 1)},
              "all_parts": {k: c_["n_W2_negative_dropped"] / max(c_["n_in_ps"], 1) for k, c_ in counts.items()}}
        if name in M4W_REF:
            ref = M4W_REF[name]
            b2["rule"] = b2_rule(c["n_W2_negative_dropped"], c["n_in_ps"], ref)
            b2["population_matches_m4w"] = c["n_in_ps"] == ref[1]
            b2["pass"] = bool(b2["population_matches_m4w"] and b2["rule"]["pass"])
            if not b2["population_matches_m4w"]:
                b2["stop_reason"] = f"population: {c['n_in_ps']} in-phase-space events, M4-W measured {ref[1]}"
            elif not b2["rule"]["pass"]:
                b2["stop_reason"] = (f"W^2 < 0 fraction {b2['rule']['fraction']:.3e} is {b2['rule']['ratio']:.3f} x "
                                     f"M4-W's {b2['rule']['m4w_fraction']:.3e}, outside a factor 2")
        self.res["B2"][name] = b2
        print("B2", name, json.dumps(b2), flush=True)
        return b2

    def b0(self, name, parts, refs, checks, cols_of, counts, target, tgt, x, v, n) -> dict:
        al = alignment(parts, cols_of, refs)
        diag_ok = all(not c.get("zero_flux_event", False) for c in counts.values())
        b0 = {"alignment_with_frozen_extractor": al, "checks": checks, "no_zero_flux_event": diag_ok}
        ok = all(a and all(a.values()) for a in al.values()) and all(checks.values()) and diag_ok
        if target is not None:
            b0.update(target={"path": tgt[0], "keys": list(tgt[1:])},
                      xsec_bitwise=bool(np.array_equal(x, target[tgt[1]])),
                      sumw2_bitwise=bool(np.array_equal(v, target[tgt[2]])),
                      xsec=gfr.compare_arrays(x, np.asarray(target[tgt[1]], float)),
                      sumw2=gfr.compare_arrays(v, np.asarray(target[tgt[2]], float)))
            nk = "nevt_flat" if tgt[1] == "xsec_flat" else "nevt_H"
            if nk in target:
                b0["nevt_reported"] = gfr.compare_arrays(n, np.asarray(target[nk], float))
            ok = ok and b0["xsec_bitwise"] and b0["sumw2_bitwise"]
        else:
            b0["target"] = None
            b0["note"] = "no frozen product exists; B0 is the reader's alignment with the frozen extractor only"
        b0["pass"] = bool(ok)
        self.res["B0"][name] = b0
        print("B0", name, json.dumps({k: b0.get(k) for k in ("xsec_bitwise", "sumw2_bitwise", "pass")}), flush=True)
        return b0

    def ch_b0(self) -> None:
        """B0 for step A's CH combinations: (12/13) x_C12 + (1/13) x_H from the two rebuilt gen products."""
        for gen, path in (("nuwro", MP3B_NPZ), ("gibuu", MP3C_NPZ)):
            c, h = self.gen.get(f"{gen}_C12"), self.gen.get(f"{gen}_H")
            if c is None or h is None or not (self.res["B0"][f"{gen}_C12"]["pass"]
                                              and self.res["B0"][f"{gen}_H"]["pass"]):
                continue
            ref = load_npz(self.ctx.inputs, path)
            x = mp3b.F_C * c[0] + mp3b.F_H * h[0]
            v = mp3b.F_C ** 2 * c[1] + mp3b.F_H ** 2 * h[1]
            r = {"target": {"path": path, "keys": ["xsec_CH", "sumw2_CH"]},
                 "xsec_bitwise": bool(np.array_equal(x, ref["xsec_CH"])),
                 "sumw2_bitwise": bool(np.array_equal(v, ref["sumw2_CH"]))}
            r["pass"] = r["xsec_bitwise"] and r["sumw2_bitwise"]
            self.res["B0"][f"{gen}_CH"] = r


def module_digests(roots) -> tuple[dict, list]:
    out, reads = {}, []
    roots = [str(Path(r).resolve()) for r in roots]
    for name, m in sorted(sys.modules.items()):
        f = getattr(m, "__file__", None) if m is not None else None
        if not f or not f.endswith(".py"):
            continue
        p = str(Path(f).resolve())
        if any(p.startswith(r + os.sep) for r in roots):
            buf, rec = read_noatime(p)
            out[name] = {"file": p, "sha256": rec["sha256"]}
            if p.startswith(PSCRATCH):
                reads.append(rec)
    return out, reads


def run_samples(run: Run, samples, after=None) -> int:
    """Each sample in turn; an error or a stop ends that sample only. 0 every sample complete, else 3."""
    rc = 0
    for s in samples:
        try:
            if not run.sample(s):
                rc = 3
        except (Exception, SystemExit) as e:  # noqa: BLE001 -- one sample stops, the others continue
            run.res["status"].setdefault(s, {"B0": False, "B2": "n/a", "complete": False, "variants_written": []})
            run.res["status"][s]["complete"] = False
            run.res["samples"].setdefault(s, {}).update(status="STOP", stage="error", reason=repr(e),
                                                        traceback=traceback.format_exc())
            print("STOP", s, repr(e), flush=True)
            rc = 3
        finally:
            run.ctx.mem.release()
        if after is not None:
            after()
    return rc


def copy_frozen_tree(src: str, dst: Path, inputs: Inputs) -> dict:
    """Every .py file of the frozen code tree, read through the pinned O_NOATIME reader and written to dst under the
    same relative path (declaration section 9; INPUTS family H). Refuses an unpinned .py, a pinned .py the tree lacks,
    and any digest mismatch; __pycache__ and non-.py files are not copied."""
    srcp = os.path.abspath(src)
    found = []
    for root, dirs, names in os.walk(srcp):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        found += [os.path.join(root, f) for f in sorted(names) if f.endswith(".py")]
    pinned = sorted(p for p in inputs.pins if p.startswith(srcp + os.sep) and p.endswith(".py"))
    if not found:
        raise InputRefused(f"{srcp}: no .py file")
    if sorted(found) != pinned:
        raise InputRefused(f"{srcp}: unpinned .py {sorted(set(found) - set(pinned))}, "
                           f"pinned but absent {sorted(set(pinned) - set(found))}")
    files = {}
    for f in found:
        buf = inputs.read(f)
        rel = os.path.relpath(f, srcp)
        t = dst / rel
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_bytes(buf)
        files[rel] = hashlib.sha256(t.read_bytes()).hexdigest()
    return {"src": srcp, "dst": str(dst), "files": files}


def build_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True, help="output directory; must not exist")
    ap.add_argument("--samples", default=",".join(SAMPLES), help="comma list (default: the six of section 3)")
    ap.add_argument("--inputs", type=Path, action="append", default=None,
                    help=f"pin file(s) in INPUTS.sha256 format (default {INPUTS.relative_to(_REPO)}); repeat to add "
                         "step D's pins")
    ap.add_argument("--pool-dir", default=POOL_DIR)
    ap.add_argument("--gen5d-tree-src", default=gfr.DEFAULTS["gen5d_tree"],
                    help="the frozen code tree the gen5d build ran from; its .py files are copied (pinned, O_NOATIME) "
                         "into <out>/frozen_tree and imported from there")
    ap.add_argument("--gen5d-tree", default=None, help=argparse.SUPPRESS)     # tests only: import from here instead
    ap.add_argument("--nproc", type=int, default=32, help="processes for the GiBUU ASCII reads")
    ap.add_argument("--allow-meta-pin", action="store_true",
                    help="pin the GiBUU flux file (absent from INPUTS.sha256) from the verified frozen GiBUU product's "
                         "own input record")
    ap.add_argument("--nuwro-chnative-main", nargs="+", default=[], help="step D: native-CH NuWro flat5d files")
    ap.add_argument("--nuwro-chnative-supp", nargs="+", default=[], help="step D: its 50-100 GeV supplement flat5d")
    a = ap.parse_args(argv)
    a.samples = [s for s in a.samples.split(",") if s]
    if bool(a.nuwro_chnative_main) != bool(a.nuwro_chnative_supp):
        ap.error("--nuwro-chnative-main and --nuwro-chnative-supp go together")
    if a.nuwro_chnative_main and "nuwro_CHnative" not in a.samples:
        a.samples.append("nuwro_CHnative")
    bad = [s for s in a.samples if s not in LOADERS or (s == "nuwro_CHnative" and not a.nuwro_chnative_main)]
    if bad:
        ap.error(f"unknown or unconfigured samples {bad}")
    return a


def main(argv=None) -> int:
    global _G5
    t0 = time.time()
    a = build_args(argv)
    if os.path.lexists(a.out):
        print(f"REFUSED: {a.out} exists", flush=True)
        return 2
    if str(a.out.resolve()).startswith("/global/cfs/"):
        print("REFUSED: nothing is written to CFS (declaration section 6)", flush=True)
        return 2
    pin_files = a.inputs or [INPUTS]
    try:
        pins = read_pins(pin_files)
    except (OSError, ValueError) as e:
        print(f"REFUSED: pins unreadable: {e}", flush=True)
        return 2
    a.out.mkdir(parents=True)
    res = {"schema": "fd-gencmp-rebuild/1", "argv": sys.argv if argv is None else ["fd_gencmp_rebuild.py", *argv],
           "pin_files": {str(p): hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in pin_files}}
    inputs = Inputs(pins)
    rc = 0
    run = None
    try:
        res["frozen_tree"] = copy_frozen_tree(a.gen5d_tree_src, a.out / "frozen_tree", inputs)
    except (OSError, InputRefused) as e:
        res.update(error=repr(e))
        print("REFUSED: frozen tree", repr(e), flush=True)
        _dump(a.out, res, None, inputs, t0, 2)
        return 2
    tree = a.gen5d_tree or str(a.out / "frozen_tree")
    try:
        ROOT = gfr.import_root()
        g5 = gfr.load_g5(tree)
        _G5 = g5
        mem = MemROOT(ROOT)
        res["memroot_installed_in"] = install_memroot(ROOT, mem, [_REPO, tree])
        res["environment"] = gfr.environment()
        res["code"], res["code_reads_on_pscratch"] = module_digests([_REPO, tree])
        z = np.load(io.BytesIO(inputs.read(os.path.join(sup.OUT, "phi_t.npz"))), allow_pickle=False)
        ctx = Ctx(g5, mem, inputs, (z["edges"], z["phi_t_density"], float(z["Phi_t"])), a.nproc, a.allow_meta_pin,
                  (tuple(a.nuwro_chnative_main), tuple(a.nuwro_chnative_supp)))
        run = Run(ctx, a.out, a.pool_dir)
        rc = run_samples(run, a.samples, lambda: _dump(a.out, res, run, inputs, t0, None))
        run.ch_b0()
    except (Exception, SystemExit) as e:  # noqa: BLE001 -- recorded, then refused
        res.update(error=repr(e), traceback=traceback.format_exc())
        print("REFUSED", repr(e), flush=True)
        rc = 2
    _dump(a.out, res, run, inputs, t0, rc)
    print("REBUILD", json.dumps(run.res["status"] if run else {}),
          "exit", rc, flush=True)
    return rc


def _dump(out: Path, res: dict, run, inputs: Inputs, t0: float, rc) -> None:
    s, c = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    res.update(run.res if run else {})
    res.update(inputs_read=inputs.records, pins_from_verified_meta=inputs.meta_pins,
               atime_deviations=inputs.deviations(), wall_s=time.time() - t0,
               cpu_s=s.ru_utime + s.ru_stime + c.ru_utime + c.ru_stime, maxrss_kb=s.ru_maxrss, exit=rc)
    (out / "rebuild.json").write_text(json.dumps(res, indent=1, default=_jsonable) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
