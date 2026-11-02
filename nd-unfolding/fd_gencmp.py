#!/usr/bin/env python3
"""GENCMP (state/measurement-paper/5d-community-20261024/FD-GENCMP-DECLARATION.md): the readers for steps 0, A, C and
D, and the readout of step B. Step B's rebuild itself is fd_gencmp_rebuild.py.

Subcommands, each writing one JSON readout and refusing to overwrite it:

* ``a1``      (login node) step A's control A1: the committed C12 arrays against the frozen products, bitwise.
* ``ch``      (local) step A, Q08: NuWro and GiBUU corrected to CH, x_CH = (12/13) x_C + (1/13) x_H, from the committed
              fine-grid products, on Table IV's cells and both covariances (FD-G's integration and chi2, imported).
* ``defs``    (local or login node) step B's readout, Q10: the rebuilt products in the generator and analysis
              definitions, per cell and in chi2, the five-seed spread, the W-only and axis-only parts, the 2 x 2 table.
* ``overlap`` (login node) step C, Q26: the sixteen cells summed per (pT, p_par) quadrant against the 2D and 3D results.
* ``native``  (local or login node) step D: native NuWro-on-CH against step A's combination.

The comparison is FD-G's: X = U x with U S1's functional matrix (s1_assemble.fine_map, functional_matrix),
V_g = U^2 sumw2, total and shape-only chi2 from fd_g_compare.compare. The reported matrix is
C_total + C_resp + C_PL,5D, its variant C_total + C_resp (Table IV's two column groups). f and the blocks come from the
committed with-block product (fd/with-cpl/block/cpl_block.npz, fd/with-cpl/data-product/fd_data_product_cpl.json).

Every pscratch or CFS input is opened with O_NOATIME and its atime compared before and after (``read_noatime``), and
every input is checked against fd/gencmp/INPUTS.sha256 before use.

MEASURES: arithmetic on the declared inputs. CANNOT AUTHORIZE: any reading of the numbers, a Table IV change, a claim or
paper text (the declaration's CANNOT AUTHORIZE).
"""
from __future__ import annotations

import argparse
import hashlib
import io
import itertools
import json
import os
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
_REPO = _ND.parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_g_compare as fg  # noqa: E402  (compare, GIBUU_CELLS, Stop, report)
import s1_assemble as sa  # noqa: E402  (fine_map, functional_matrix; sa.s1 = s5p_stage1_inspect)

N_FINE, N_CELLS = fg.N_FINE, fg.N_CELLS
ALL_CELLS = list(range(N_CELLS))
GIBUU_CELLS = list(fg.GIBUU_CELLS)
F_C, F_H = 12.0 / 13.0, 1.0 / 13.0          # mp3b_build.py:74, mp3c_build.py:57; the same expression order (:602, :277)
TOL_A0 = 1e-9
TOL = 1e-12
SEED_SPREAD_FLAG = 0.2                       # declaration section 3
D_SUMZ2_MAX, D_ZMAX = 32.0, 3.5              # declaration section 5: chi2_16 0.99 quantile, and the per-cell bound
VL173_2D_INTEGRAL = 3.0730e-38               # VALIDATION_LEDGER.md VL173, five figures
TOTAL_3D = 3.079e-38                         # 3d-unfolding/3D_OMNIFOLD_STATUS.md headline, "Total sigma (3D integral)", four figures
FROZEN_NUWRO = "/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix/nuwro_cv_xsec5d_full.npz"
FROZEN_GIBUU = "/pscratch/sd/j/josephrb/s5p-20260926/gen5d_fluxfix/gibuu_cv_xsec5d_fluxfix.npz"
FD = _REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024"
P1 = _REPO / "docs/orchestration/state/measurement-paper/phase1"
INPUTS = FD / "fd/gencmp/INPUTS.sha256"
DEFINITION = _ND / "pv-ladder/readouts/h2_definition.json"
CMODEL = _ND / "pv-ladder/readouts/cmodel_5d.json"
BLOCK = FD / "fd/with-cpl/block/cpl_block.npz"
DATA_PRODUCT = FD / "fd/with-cpl/data-product/fd_data_product_cpl.json"
READOUT_REPORTED = FD / "fd/with-cpl/readout/fd_g_readout.json"    # C_total + C_resp + C_PL5D + V_g
READOUT_NOPL = FD / "fd/readout/fd_g_readout.json"                 # C_total + C_resp + V_g
NUWRO_NPZ = P1 / "mp3b/runA/out_r2/build_k1/mp3b_fine_nuwro.npz"
GIBUU_NPZ = P1 / "mp3c/out_b/eval_frozen/mp3c_fine_gibuu_frozen.npz"
GIBUU_ALT_NPZ = P1 / "mp3c/out_b/eval_alt/mp3c_fine_gibuu_alt.npz"
GENIE_H_NPZ = P1 / "mp3a/out/build/mp3a_fine_genie_cv.npz"
LABELS = {
    "nuwro_CH": "NuWro 21.09 C12 + NuWro free-proton, 12:1 per nucleon; four hydrogen chunks rerun on alternate seeds, "
                "supplement FLAGGED (MP3-B section 2)",
    "gibuu_CH": "B3 (sampling closure) failed on hydrogen; a post-hoc bias check of its premise passed at <= 0.1 sigma_c; "
                "46% of the hydrogen sample is DIS that does not conserve energy (binding addendum 9 section 4)",
    "genie_H": "mixed: carbon of this generator + GENIE CV hydrogen (13 x MP3-A xsec_H1); a sensitivity, never the "
               "primary; adds no covariance block. GENIE's hydrogen sample is thin (MP3-B section 6: B4 not met, 21 "
               "cells above 1/3, worst 1.41), so this spread is largely that sample's own noise",
    "gibuu_alt": "GiBUU CH with MP3-C's alternative (post-hoc bias check) weight; printed beside the primary",
}
QUADRANTS = {   # declaration section 4; checked against the definition by quadrant_cells()
    "QA": {"pt": (0.0, 0.7), "pz": (1.5, 4.5), "cells": [0, 1, 2, 3], "unreported": [2, 6]},
    "QB": {"pt": (0.0, 0.7), "pz": (4.5, 60.0), "cells": [4, 5, 6, 7], "unreported": [10, 14]},
    "QC": {"pt": (0.7, 4.5), "pz": (1.5, 4.5), "cells": [8, 9, 10, 11], "unreported": []},
    "QD": {"pt": (0.7, 4.5), "pz": (4.5, 60.0), "cells": [12, 13, 14, 15], "unreported": []},
}
Stop, report = fg.Stop, fg.report


# ---------------------------------------------------------------- inputs


def load_pins(path: Path = INPUTS) -> dict[str, str]:
    """{absolute path: sha256} from INPUTS.sha256; repository-relative paths are resolved against the repository."""
    pins = {}
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        digest, p = line.split(None, 1)
        p = p.strip()
        pins[str(Path(p) if p.startswith("/") else _REPO / p)] = digest
    return pins


def read_noatime(path: Path) -> tuple[bytes, bool]:
    """The file's bytes through an O_NOATIME descriptor, and whether its atime is unchanged. A pscratch file is refused
    where O_NOATIME does not exist, since a plain read moves its purge clock."""
    if str(path).startswith("/pscratch/") and not hasattr(os, "O_NOATIME"):
        raise Stop("0", f"{path}: O_NOATIME is unavailable here, and a plain read would move the file's atime")
    before = os.stat(path).st_atime_ns
    flags = os.O_RDONLY | getattr(os, "O_NOATIME", 0)
    with os.fdopen(os.open(path, flags), "rb") as fh:
        data = fh.read()
    return data, os.stat(path).st_atime_ns == before


class Inputs:
    """Reads each declared input once, checks it against its pin, and records digest and atime."""

    def __init__(self, pins: dict[str, str] | None = None):
        self.pins = load_pins() if pins is None else pins
        self.record: dict[str, dict] = {}

    def bytes(self, path: Path) -> bytes:
        key = str(Path(path) if Path(path).is_absolute() else _REPO / path)
        if key not in self.pins:
            raise Stop("0", f"{path} is not in INPUTS.sha256")
        data, atime_ok = read_noatime(Path(path))
        got = hashlib.sha256(data).hexdigest()
        self.record[key] = {"sha256": got, "pinned": self.pins[key], "atime_unchanged": atime_ok}
        if got != self.pins[key]:
            raise Stop("0", f"{path}: sha256 {got} != pinned {self.pins[key]}")
        return data

    def npz(self, path: Path) -> dict[str, np.ndarray]:
        with np.load(io.BytesIO(self.bytes(path)), allow_pickle=False) as z:
            return {k: np.asarray(z[k]) for k in z.files}

    def json(self, path: Path) -> dict:
        return json.loads(self.bytes(path))

    def atime_deviations(self) -> list[str]:
        return [k for k, v in self.record.items() if not v["atime_unchanged"]]


# ---------------------------------------------------------------- the comparison


def cell_matrix() -> np.ndarray:
    return sa.functional_matrix(sa.fine_map(DEFINITION))


def result(inp: Inputs) -> dict:
    """f and Table IV's two matrices from the committed with-block product, with their consistency checks."""
    blk, dp, cm = inp.npz(BLOCK), inp.json(DATA_PRODUCT), inp.json(CMODEL)
    f = np.asarray(blk["f"], float)
    Ce, Cma = (np.asarray(dp["matrices"][k], float) for k in ("C_e", "C_model_abs"))
    Cr, Cpl = np.asarray(blk["C_resp"], float), np.asarray(blk["C_PL5D"], float)
    Ct = Ce + Cma
    rep, nopl = Ct + Cr + Cpl, Ct + Cr
    scale = np.abs(np.diag(rep)).max()
    report("R", "f is cmodel_5d.json's x, P5's integrals (to 1e-12)", np.allclose(f, cm["x"], rtol=TOL, atol=0))
    report("R", "C_total + C_resp + C_PL5D equals the block's sum (to 1e-12 of the largest variance)",
           np.allclose(rep, blk["C_total_plus_C_resp_plus_C_PL5D"], rtol=0, atol=TOL * scale))
    return {"f": f, "reported": rep, "nopl": nopl}


def integrate(U: np.ndarray, x: np.ndarray, s2: np.ndarray, cells: list[int]) -> tuple[np.ndarray, np.ndarray]:
    """FD-G's rule: g = U x and V_g = U^2 sumw2 on ``cells`` only; zero elsewhere."""
    g, Vg = np.zeros(N_CELLS), np.zeros(N_CELLS)
    Uc = U[cells]
    g[cells] = Uc @ np.asarray(x, float)
    Vg[cells] = (Uc ** 2) @ np.asarray(s2, float)
    return g, Vg


def chi2_pair(R: dict, g: np.ndarray, Vg: np.ndarray, cells: list[int]) -> dict:
    if not (np.all(g[cells] > 0) and np.all(Vg[cells] >= 0)):
        raise Stop("A2", "a cell integral is not positive or V_g is negative")
    return {"reported": fg.compare(R["f"], g, Vg, R["reported"], cells, "C_total + C_resp + C_PL5D"),
            "without_C_PL5D": fg.compare(R["f"], g, Vg, R["nopl"], cells, "C_total + C_resp")}


def summary(c: dict) -> dict:
    return {k: {kk: c[k][kk]["chi2"] for kk in ("total", "shape_only")} for k in c}


def combine(xc, sc, xh, sh) -> tuple[np.ndarray, np.ndarray]:
    """x_CH = (12/13) x_C + (1/13) x_H and its sumw2, in mp3b_build.py's floating-point order."""
    return F_C * np.asarray(xc, float) + F_H * np.asarray(xh, float), F_C ** 2 * np.asarray(sc, float) + F_H ** 2 * np.asarray(sh, float)


def write(out: Path, readout: dict) -> None:
    if out.exists():
        raise Stop("-", f"refusing to overwrite {out}")
    readout["code_sha256"] = {Path(m.__file__).name: hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()
                              for m in (sys.modules[__name__], fg, sa, sa.s1)}
    readout["argv"] = [str(x) for x in sys.argv]
    tmp = out.with_name(out.name + ".partial")
    tmp.write_text(json.dumps(readout, indent=1, default=float) + "\n")
    os.replace(tmp, out)
    print(json.dumps({"wrote": str(out), "sha256": hashlib.sha256(out.read_bytes()).hexdigest()}), flush=True)


# ---------------------------------------------------------------- step A


def cmd_a1(a) -> int:
    """A1: the committed C12 arrays equal the frozen products on pscratch, bitwise."""
    inp = Inputs()
    rows = {}
    for name, npz, frozen in (("nuwro", NUWRO_NPZ, a.nuwro_frozen), ("gibuu", GIBUU_NPZ, a.gibuu_frozen)):
        c, z = inp.npz(npz), inp.npz(frozen)
        rows[name] = {k: bool(np.array_equal(c[f"{k}_C12_frozen"], z[f"{k}_flat"])) for k in ("xsec", "sumw2")}
    ok = all(all(v.values()) for v in rows.values())
    write(a.out, {"schema": "fd-gencmp-a1/1", "pass": ok, "bitwise": rows, "inputs": inp.record,
                  "atime_deviations": inp.atime_deviations()})
    report("A1", "the committed C12 arrays equal the frozen products bitwise", ok, json.dumps(rows))
    return 0


def cmd_ch(a) -> int:
    inp = Inputs()
    a1 = json.loads(Path(a.a1_json).read_text())
    seen = {v.get("sha256") for v in a1.get("inputs", {}).values()}
    need = [inp.pins[str(p)] for p in (NUWRO_NPZ, GIBUU_NPZ)] + [inp.pins[k] for k in (FROZEN_NUWRO, FROZEN_GIBUU)
                                                                if k in inp.pins]
    a1_ok = a1.get("pass") is True and len(need) == 4 and set(need) <= seen
    report("A1", "the A1 readout passed, on these npz files and frozen products (matched by digest, not by path)", a1_ok)
    U, R = cell_matrix(), result(inp)
    nw, gb, gba, ge = (inp.npz(p) for p in (NUWRO_NPZ, GIBUU_NPZ, GIBUU_ALT_NPZ, GENIE_H_NPZ))
    committed = {k: {p["name"]: p for p in inp.json(path)["predictions"]}
                 for k, path in (("reported", READOUT_REPORTED), ("without_C_PL5D", READOUT_NOPL))}

    def committed_chi2(name, key, part):
        return committed[key][name][part]["chi2"]

    gens = {"nuwro": (nw, ALL_CELLS), "gibuu": (gb, GIBUU_CELLS)}
    out = {}
    for name, (z, cells) in gens.items():
        xc, sc = z["xsec_C12_frozen"], z["sumw2_C12_frozen"]
        g, Vg = integrate(U, xc, sc, cells)
        carbon = chi2_pair(R, g, Vg, cells)
        for key in carbon:
            for part in ("total", "shape_only"):
                got, want = carbon[key][part]["chi2"], committed_chi2(name, key, part)
                report("A0", f"{name} carbon {key} {part} chi2 reproduces the committed G readout to {TOL_A0}",
                       abs(got / want - 1) <= TOL_A0, f"{got!r} vs {want!r}")
        xch, sch = combine(xc, sc, z["xsec_H"], z["sumw2_H"])
        report("A", f"{name}: the CH arrays equal the committed xsec_CH, sumw2_CH bitwise",
               np.array_equal(xch, z["xsec_CH"]) and np.array_equal(sch, z["sumw2_CH"]))
        gch, Vch = integrate(U, xch, sch, cells)
        rows = {"carbon": {"chi2": carbon, "g": g[cells].tolist()},
                "CH": {"chi2": chi2_pair(R, gch, Vch, cells), "g": gch[cells].tolist(), "label": LABELS[f"{name}_CH"]}}
        xm, sm = F_C * np.asarray(xc, float) + np.asarray(ge["xsec_H1"], float), \
            F_C ** 2 * np.asarray(sc, float) + np.asarray(ge["sumw2_H1"], float)
        gm, Vm = integrate(U, xm, sm, cells)
        rows["CH_genie_hydrogen"] = {"chi2": chi2_pair(R, gm, Vm, cells), "g": gm[cells].tolist(), "label": LABELS["genie_H"]}
        if name == "gibuu":
            xa, sa_ = gba["xsec_CH"], gba["sumw2_CH"]
            ga, Va = integrate(U, xa, sa_, cells)
            rows["CH_alt_weight"] = {"chi2": chi2_pair(R, ga, Va, cells), "g": ga[cells].tolist(), "label": LABELS["gibuu_alt"]}
        rows["r_c"] = (gch[cells] / g[cells]).tolist()
        rows["delta_chi2_CH_minus_carbon"] = {k: {p: rows["CH"]["chi2"][k][p]["chi2"] - carbon[k][p]["chi2"]
                                                  for p in ("total", "shape_only")} for k in carbon}
        rows["cells"] = [f"R{c:02d}" for c in cells]
        out[name] = rows
    write(a.out, {"schema": "fd-gencmp-ch/1", "step": "A (Q08)", "controls_passed": ["A0", "A1", "A2", "R"],
                  "generators": out, "inputs": inp.record, "atime_deviations": inp.atime_deviations(),
                  "not": "no reading, Table IV change or paper text; Joseph decides (FD-GENCMP section 7)"})
    for name in out:
        for k in ("carbon", "CH", "CH_genie_hydrogen") + (("CH_alt_weight",) if name == "gibuu" else ()):
            print(f"[A] {name:6s} {k:18s} {json.dumps(summary(out[name][k]['chi2']))}", flush=True)
    return 0


# ---------------------------------------------------------------- step B readout


def load_rebuilt(d: Path, sample: str, variant: str) -> tuple[np.ndarray, np.ndarray]:
    with np.load(d / f"{sample}_{variant}.npz", allow_pickle=False) as z:
        return np.asarray(z["xsec_flat"], float), np.asarray(z["sumw2_flat"], float)


def seed_mean(d: Path, sample: str, seeds) -> tuple[np.ndarray, np.ndarray, list[np.ndarray]]:
    xs = [load_rebuilt(d, sample, f"ana_s{s}") for s in seeds]
    return np.mean([x for x, _ in xs], axis=0), np.mean([v for _, v in xs], axis=0), [x for x, _ in xs]


def rebuild_status(rb: dict) -> dict:
    """Per sample: B0, B2 and complete, from rebuild.json's status record; a sample without one is not complete."""
    out = {}
    for s, st in rb.get("status", {}).items():
        out[s] = {"B0": st.get("B0") is True, "B2": st.get("B2"), "complete": st.get("complete") is True}
    return out


def cmd_defs(a) -> int:
    import fd_gencmp_kin as kin
    inp = Inputs()
    U, R = cell_matrix(), result(inp)
    sig = np.sqrt(np.diag(R["reported"]))
    rb = json.loads((a.rebuild_dir / "rebuild.json").read_text())
    status = rebuild_status(rb)
    b0 = {s: st["B0"] for s, st in status.items()}
    out, d = {}, a.rebuild_dir

    def build(sample, cells):
        """{'gen': (x, s2), 'ana': (x, s2), 'seeds': [x...], 'wonly': ..., 'axisonly': ...}, or None unless the sample is
        complete (B0 passed, B2 did not stop, every variant written)."""
        if not status.get(sample, {}).get("complete"):
            return None
        r = {"gen": load_rebuilt(d, sample, "gen")}
        x, v, xs = seed_mean(d, sample, kin.SEEDS)
        r["ana"], r["seeds"] = (x, v), xs
        r["wonly"], r["axisonly"] = load_rebuilt(d, sample, "wonly"), load_rebuilt(d, sample, "axisonly")
        if (d / f"{sample}_ana_mn.npz").exists():
            r["ana_mn"] = load_rebuilt(d, sample, "ana_mn")
        return r

    def readout(parts, cells):
        g0, V0 = integrate(U, *parts["gen"], cells)
        g1, V1 = integrate(U, *parts["ana"], cells)
        seeds = np.array([integrate(U, x, np.zeros(N_FINE), cells)[0][cells] for x in parts["seeds"]])
        spread = seeds.std(axis=0, ddof=1) / sig[cells]
        rec = {"cells": [f"R{c:02d}" for c in cells],
               "generator_definitions": {"chi2": chi2_pair(R, g0, V0, cells), "g": g0[cells].tolist()},
               "analysis_definitions": {"chi2": chi2_pair(R, g1, V1, cells), "g": g1[cells].tolist()},
               "delta_over_sigma": ((g1 - g0)[cells] / sig[cells]).tolist(),
               "delta_pct": (100 * (g1 / np.where(g0 > 0, g0, 1) - 1)[cells]).tolist(),
               "seed_spread_over_sigma": spread.tolist(),
               "seed_spread_flag": bool(np.any(spread > SEED_SPREAD_FLAG)),
               "seed_spread_flag_rule": f"any cell's five-seed SD of the integral above {SEED_SPREAD_FLAG} of its reported "
                                        "sigma is reported; the mean stays the primary (declaration section 3)"}
        for part in ("wonly", "axisonly") + (("ana_mn",) if "ana_mn" in parts else ()):
            gp, _ = integrate(U, *parts[part], cells)
            rec[f"{part}_delta_over_sigma"] = ((gp - g0)[cells] / sig[cells]).tolist()
        return rec

    for name, cells in (("genie_cv", ALL_CELLS), ("genie_mec", ALL_CELLS)):
        p = build(name, cells)
        out[name] = {"B0": b0.get(name), **({} if p is None else {"CH": readout(p, cells)})}
    for gen, cells in (("nuwro", ALL_CELLS), ("gibuu", GIBUU_CELLS)):
        pc, ph = build(f"{gen}_C12", cells), build(f"{gen}_H", cells)
        rec = {"B0": {"C12": b0.get(f"{gen}_C12"), "H": b0.get(f"{gen}_H")}}
        if pc is not None:
            rec["carbon"] = readout(pc, cells)
        if pc is not None and ph is not None:
            ch = {k: combine(*pc[k], *ph[k]) for k in ("gen", "ana", "wonly", "axisonly")}
            ch["seeds"] = [F_C * xc + F_H * xh for xc, xh in zip(pc["seeds"], ph["seeds"])]
            if "ana_mn" in pc:          # carbon's M_n variant with hydrogen's first-seed analysis product (M_p)
                ch["ana_mn"] = combine(*pc["ana_mn"], *load_rebuilt(d, f"{gen}_H", f"ana_s{kin.SEEDS[0]}"))
            ref = inp.npz(NUWRO_NPZ if gen == "nuwro" else GIBUU_NPZ)
            report("B0", f"{gen}: the rebuilt CH combination in the generator definitions equals step A's bitwise",
                   np.array_equal(ch["gen"][0], ref["xsec_CH"]) and np.array_equal(ch["gen"][1], ref["sumw2_CH"]))
            rec["CH"] = readout(ch, cells)
            rec["CH"]["label"] = LABELS[f"{gen}_CH"]
        out[gen] = rec
    table = {g: {t: {dfn: summary(out[g][t][dfn]["chi2"]) for dfn in ("generator_definitions", "analysis_definitions")}
                 for t in ("carbon", "CH") if t in out[g]} for g in out}
    write(a.out, {"schema": "fd-gencmp-defs/1", "step": "B (Q10)", "rebuild_json_sha256":
                  hashlib.sha256((a.rebuild_dir / "rebuild.json").read_bytes()).hexdigest(),
                  "status": status, "not_read": sorted(k for k, v in status.items() if not v["complete"]),
                  "generators": out, "table_2x2": table, "inputs": inp.record,
                  "candidate": "the corner 'CH, analysis definitions' is the candidate for Table IV, which only Joseph "
                               "can adopt",
                  "not": "no reading, Table IV change or paper text (FD-GENCMP section 7)"})
    print("[B] " + json.dumps(table), flush=True)
    return 0


# ---------------------------------------------------------------- step C


def enumerate_eavail_regions(defn: dict) -> list[dict]:
    """Every (pT, p_par, E_avail) box on the H2 edges, spanning all q3 and W, whose boxes are a union of reported cells
    (unreported boxes allowed) and whose E_avail range is not the whole axis."""
    E = sa.s1.H2_EDGES
    m = np.asarray(defn["h2_to_reporting_cell"], int)
    box_of = {}
    for b in range(32):
        i = np.unravel_index(b, (2,) * 5)
        box_of[b] = dict(zip(sa.s1.AXES, i))
    intervals = {a: [(0, 1), (1, 2), (0, 2)] for a in ("pt", "pz", "eavail")}
    found = []
    for ipt, ipz, iea in itertools.product(intervals["pt"], intervals["pz"], intervals["eavail"]):
        if iea == (0, 2):
            continue
        inside = {b for b, ix in box_of.items()
                  if ipt[0] <= ix["pt"] < ipt[1] and ipz[0] <= ix["pz"] < ipz[1] and iea[0] <= ix["eavail"] < iea[1]}
        cells = {int(m[b]) for b in inside if m[b] >= 0}
        whole = all({b for b in range(32) if m[b] == c} <= inside for c in cells)
        if cells and whole:
            found.append({"pt": [E["pt"][ipt[0]], E["pt"][ipt[1]]], "pz": [E["pz"][ipz[0]], E["pz"][ipz[1]]],
                          "eavail": [E["eavail"][iea[0]], E["eavail"][iea[1]]], "cells": sorted(cells)})
    return found


def quadrant_cells(defn: dict) -> dict:
    """The reported cells and unreported boxes of each quadrant, read from the definition."""
    m = np.asarray(defn["h2_to_reporting_cell"], int)
    got = {}
    for q, Q in QUADRANTS.items():
        cells = sorted(c["id"] for c in defn["reporting_cells"]
                       if tuple(c["box"]["pt"]) == Q["pt"] and tuple(c["box"]["pz"]) == Q["pz"])
        boxes = quadrant_boxes(Q)
        got[q] = {"cells": cells, "unreported": [b for b in boxes if m[b] < 0], "boxes": boxes}
    return got


def quadrant_boxes(Q: dict) -> list[int]:
    """The eight H2 boxes (C order over pt, pz, E_avail, q3, W, two bins each) in a quadrant."""
    E = sa.s1.H2_EDGES
    out = []
    for b in range(32):
        ix = np.unravel_index(b, (2,) * 5)
        if (E["pt"][ix[0]], E["pt"][ix[0] + 1]) == Q["pt"] and (E["pz"][ix[1]], E["pz"][ix[1] + 1]) == Q["pz"]:
            out.append(b)
    return out


def rule(d: float, s16: float, slow: float | None) -> dict:
    """The declared outcome rule (section 4) over rho in [0, 1]; with no lower-dimensional sigma, the sigma_16 scale."""
    if slow is None:
        return {"outcome": ("agree at the sigma_16 scale (descriptive)" if abs(d) <= 2 * s16
                            else "differ at the sigma_16 scale (descriptive)"), "d_over_sigma16": d / s16}
    lo, hi = 2 * abs(s16 - slow), 2 * np.sqrt(s16 ** 2 + slow ** 2)
    rho_star = (s16 ** 2 + slow ** 2 - d * d / 4) / (2 * s16 * slow)
    if abs(d) <= lo:
        out = "agree"
    elif abs(d) <= hi:
        out = "agree below a correlation"
    else:
        out = "differ"
    return {"outcome": out, "bound_any_rho": lo, "bound_rho0": hi, "rho_star": float(rho_star),
            "z_rho0": d / np.sqrt(s16 ** 2 + slow ** 2)}


def root_hist(data: bytes, name: str):
    import uproot
    with uproot.open(io.BytesIO(data)) as f:
        h = f[name]
        return h.values(flow=False), [ax.edges() for ax in h.axes]


def cmd_overlap(a) -> int:
    inp = Inputs()
    defn = inp.json(DEFINITION)
    U, R = cell_matrix(), result(inp)
    f = R["f"]
    qc = quadrant_cells(defn)
    report("C", "each quadrant's cells and unreported boxes are the declared ones (section 4 table)",
           all(qc[q]["cells"] == QUADRANTS[q]["cells"] and qc[q]["unreported"] == QUADRANTS[q]["unreported"]
               and len(qc[q]["boxes"]) == 8 for q in qc),
           json.dumps(qc))
    regions = enumerate_eavail_regions(defn)
    report("C", "no (pT, p_par, E_avail) region with an inner E_avail edge is a union of reported cells (one would need an "
                "amendment before it is compared)", not regions, json.dumps(regions))
    p5 = np.asarray(inp.npz(a.p5)["xsec_flat"], float)
    report("C0", "P5's integrals over the sixteen cells equal f (to 1e-12)", np.allclose(U @ p5, f, rtol=TOL, atol=0))
    tune = np.asarray(inp.npz(a.mnvtune)["xsec_flat"], float)
    cmap, _ = sa.s1.coarse_map(sa.s1.H2_EDGES)
    vol = sa.s1.fine_volume()

    def box_integral(x, b):
        return float((x * vol)[cmap == b].sum())

    # the 2D side
    cv, (e_pt, e_pz) = root_hist(inp.bytes(a.cv2d), "hXSec2D")
    qz, pt_ = inp.npz(a.q2d), inp.npz(a.playlist)
    cells2d, area, Q = np.asarray(pt_["cells"], int), np.asarray(qz["area"], float), np.asarray(qz["total_plus_C_PL"], float)
    flat = cv.ravel(order="C")
    w2 = np.outer(np.diff(e_pt), np.diff(e_pz)).ravel(order="C")
    report("C1", "the quadrant edges are bin edges of the 2D grid",
           all(np.any(np.isclose(e_pt, v)) for v in (0.0, 0.7, 4.5)) and all(np.any(np.isclose(e_pz, v)) for v in (1.5, 4.5, 60.0)))
    report("C", "Q's area is the 2D bin area on its 205 cells (to 1e-12)", np.allclose(area, w2[cells2d], rtol=TOL, atol=0))
    rel_sig = np.sqrt(np.diag(Q)) / np.asarray(qz["cells_x_EU"], float)
    report("C", "Q is in the units of x: median sqrt(diag)/x in [0.01, 0.5]", 0.01 <= np.median(rel_sig) <= 0.5,
           f"median {np.median(rel_sig)}")
    total2d = float((flat[cells2d] * area).sum())
    report("C3", "the 2D integral reproduces VL173's 3.0730e-38 to five figures",
           abs(total2d - VL173_2D_INTEGRAL) <= 0.00005e-38, f"{total2d!r}")
    ipt, ipz = np.unravel_index(cells2d, cv.shape)
    cpt, cpz = 0.5 * (e_pt[ipt] + e_pt[ipt + 1]), 0.5 * (e_pz[ipz] + e_pz[ipz + 1])
    all_pt, all_pz = np.unravel_index(np.arange(flat.size), cv.shape)
    apt, apz = 0.5 * (e_pt[all_pt] + e_pt[all_pt + 1]), 0.5 * (e_pz[all_pz] + e_pz[all_pz + 1])

    # the 3D side
    cv3, (f_pt, f_pz, f_ea) = root_hist(inp.bytes(a.cv3d), "hXSec3D")
    report("C1", "the quadrant edges are bin edges of the 3D grid",
           all(np.any(np.isclose(f_pt, v)) for v in (0.0, 0.7, 4.5)) and all(np.any(np.isclose(f_pz, v)) for v in (1.5, 4.5, 60.0)))
    v3 = np.einsum("i,j,k->ijk", np.diff(f_pt), np.diff(f_pz), np.diff(f_ea))
    total3d = float((cv3 * v3).sum())
    report("C3", "the 3D integral reproduces the 3D status headline 3.079e-38 to four figures",
           abs(total3d - TOTAL_3D) <= 0.0005e-38, f"{total3d!r}")
    c3pt, c3pz = 0.5 * (f_pt[:-1] + f_pt[1:]), 0.5 * (f_pz[:-1] + f_pz[1:])
    proj_C, (_, _) = root_hist(inp.bytes(a.proj3d), "hCov_proj_pt_pz_eavail")
    proj_idx, _ = root_hist(inp.bytes(a.proj3d), "hRowIndex")
    proj_idx = np.asarray(np.rint(proj_idx), int)
    report("C", "PROJ3D's row index is unique and inside the 14 x 16 x 7 grid",
           proj_idx.min() >= 0 and proj_idx.max() < v3.size and np.unique(proj_idx).size == proj_idx.size)
    pv = v3.ravel(order="C")[proj_idx]
    ppt, ppz, _ = np.unravel_index(proj_idx, v3.shape)

    rows = {}
    for q, Qd in QUADRANTS.items():
        a16 = np.zeros(N_CELLS)
        a16[Qd["cells"]] = 1.0
        S16 = float(a16 @ f)
        s_rep, s_nopl = float(np.sqrt(a16 @ R["reported"] @ a16)), float(np.sqrt(a16 @ R["nopl"] @ a16))
        boxes = {str(b): box_integral(p5, b) for b in Qd["unreported"]}
        add = sum(boxes.values())
        S16 += add
        s_rep, s_nopl = float(np.sqrt(s_rep ** 2 + sum(v ** 2 for v in boxes.values()))), \
            float(np.sqrt(s_nopl ** 2 + sum(v ** 2 for v in boxes.values())))
        inq = (Qd["pt"][0] < cpt) & (cpt < Qd["pt"][1]) & (Qd["pz"][0] < cpz) & (cpz < Qd["pz"][1])
        allq = (Qd["pt"][0] < apt) & (apt < Qd["pt"][1]) & (Qd["pz"][0] < apz) & (apz < Qd["pz"][1])
        covered = set(np.flatnonzero(allq & (flat > 0))) <= set(cells2d[inq].tolist())
        aq = np.where(inq, area, 0.0)
        S2 = float(aq @ flat[cells2d])
        rec = {"cells": [f"R{c:02d}" for c in Qd["cells"]], "S16": S16, "sigma16_reported": s_rep,
               "sigma16_without_C_PL5D": s_nopl, "unreported_boxes_P5": boxes,
               "unreported_share_P5": add / S16 if Qd["unreported"] else 0.0,
               "unreported_share_MnvTune": (sum(box_integral(tune, b) for b in Qd["unreported"])
                                            / sum(box_integral(tune, b) for b in qc[q]["boxes"])) if Qd["unreported"] else 0.0,
               "label": ("includes unreported boxes at their central value, +-100%" if Qd["unreported"] else "complete")}
        if covered:
            s2 = float(np.sqrt(aq @ Q @ aq))
            rec["2D"] = {"S": S2, "sigma": s2, "d": S16 - S2, "d_pct": 100 * (S16 / S2 - 1), **rule(S16 - S2, s_rep, s2),
                         "primary": "the reported matrix C_total + C_resp + C_PL5D (declaration section 4)",
                         "printed_only_without_C_PL5D": {
                             **rule(S16 - S2, s_nopl, s2),
                             "label": "printed only, no outcome is read from it: the sixteen-cell matrix without "
                                      "C_PL5D against Q, which includes C_PL; not a like-for-like pair"}}
        else:
            rec["2D"] = {"label": "Q does not cover this quadrant; no 2D comparison is formed"}
        m3 = ((Qd["pt"][0] < c3pt) & (c3pt < Qd["pt"][1]))[:, None, None] & \
             ((Qd["pz"][0] < c3pz) & (c3pz < Qd["pz"][1]))[None, :, None]
        S3 = float((cv3 * v3 * m3).sum())
        rec["3D"] = {"S": S3, "d": S16 - S3, "d_pct": 100 * (S16 / S3 - 1), **rule(S16 - S3, s_rep, None)}
        pm = (Qd["pt"][0] < c3pt[ppt]) & (c3pt[ppt] < Qd["pt"][1]) & (Qd["pz"][0] < c3pz[ppz]) & (c3pz[ppz] < Qd["pz"][1])
        ap = np.where(pm, pv, 0.0)
        var_p = float(ap @ proj_C @ ap)
        rec["3D"]["descriptive_PROJ3D"] = {
            "variance": var_p, "sigma": float(np.sqrt(var_p)) if var_p >= 0 else None,
            "negative_variance": var_p < 0,
            "label": "unadopted trunk projection, receiving-cells population, not paired with the 3D central value "
                     "(OUTCOME-20260922 sections 4-5); descriptive only, no outcome is read from it"}
        rows[q] = rec
    write(a.out, {"schema": "fd-gencmp-overlap/1", "step": "C (Q26)", "quadrants": rows,
                  "eavail_regions_formable": regions,
                  "diagnostic_cv_over_Q_x_max_rel": float(np.max(np.abs(flat[cells2d] / np.asarray(qz["cells_x_EU"], float) - 1))),
                  "total_2d": total2d, "total_3d": total3d,
                  "rule": "agree: |d| <= 2|s16 - slow|; agree below a correlation: <= 2 sqrt(s16^2 + slow^2), rho* printed; "
                          "differ otherwise (a new problem, to the director and Joseph). 3D: the sigma_16 scale only, "
                          "descriptive, never a validation in either direction",
                  "inputs": inp.record, "atime_deviations": inp.atime_deviations()})
    for q, r in rows.items():
        print(f"[C] {q} 2D {r['2D'].get('outcome', r['2D'].get('label'))}; 3D {r['3D']['outcome']}", flush=True)
    return 0


# ---------------------------------------------------------------- step D


def native_rule(gA, VA, gD, VD, cells) -> dict:
    z = (gD - gA)[cells] / np.sqrt(VA[cells] + VD[cells])
    sumz2, zmax = float(z @ z), float(np.abs(z).max())
    return {"z": z.tolist(), "sum_z2": sumz2, "max_abs_z": zmax,
            "agree": bool(sumz2 < D_SUMZ2_MAX and zmax <= D_ZMAX),
            "rule": f"agree: sum z^2 over the cells < {D_SUMZ2_MAX} (chi2_16 0.99 quantile) and no |z| > {D_ZMAX}"}


def cmd_native(a) -> int:
    """Step D in both definitions. The primary route is the generator definitions; the analysis route is always formed
    when its three samples are complete, and printed beside it (declaration section 5)."""
    import fd_gencmp_kin as kin
    inp = Inputs()
    U, R = cell_matrix(), result(inp)
    status = rebuild_status(json.loads((a.rebuild_dir / "rebuild.json").read_text()))
    report("D", "nuwro_CHnative is complete in the rebuild (B0 alignment passed, every variant written)",
           status.get("nuwro_CHnative", {}).get("complete") is True, json.dumps(status.get("nuwro_CHnative")))
    nw = inp.npz(NUWRO_NPZ)
    gA, VA = integrate(U, nw["xsec_CH"], nw["sumw2_CH"], ALL_CELLS)
    xD, sD = load_rebuilt(a.rebuild_dir, "nuwro_CHnative", "gen")
    gD, VD = integrate(U, xD, sD, ALL_CELLS)
    rec = {"generator_definitions": {"role": "primary: this route's rule decides 'agree' (declaration section 5)",
                                     "rule": native_rule(gA, VA, gD, VD, ALL_CELLS),
                                     "native_chi2": chi2_pair(R, gD, VD, ALL_CELLS),
                                     "combination_chi2": chi2_pair(R, gA, VA, ALL_CELLS)}}
    if all(status.get(k, {}).get("complete") for k in ("nuwro_C12", "nuwro_H")):
        pc = seed_mean(a.rebuild_dir, "nuwro_C12", kin.SEEDS)
        ph = seed_mean(a.rebuild_dir, "nuwro_H", kin.SEEDS)
        xa, sa_, _ = seed_mean(a.rebuild_dir, "nuwro_CHnative", kin.SEEDS)
        g1, V1 = integrate(U, *combine(pc[0], pc[1], ph[0], ph[1]), ALL_CELLS)
        g2, V2 = integrate(U, xa, sa_, ALL_CELLS)
        rec["analysis_definitions"] = {"role": "printed beside the primary; a disagreement here is reported and named in "
                                               "the paper's clause (section 7)",
                                       "rule": native_rule(g1, V1, g2, V2, ALL_CELLS),
                                       "native_chi2": chi2_pair(R, g2, V2, ALL_CELLS)}
    else:
        rec["analysis_definitions"] = {"not_formed": "nuwro_C12 or nuwro_H is not complete in the rebuild"}
    rec["agree"] = rec["generator_definitions"]["rule"]["agree"]
    rec["paper_uses"] = ("step A's combination in every outcome (declaration section 5); a disagreement is reported with "
                         "both numbers and goes to the director and Joseph")
    write(a.out, {"schema": "fd-gencmp-native/1", "step": "D (Q08)", **rec, "status": status, "inputs": inp.record,
                  "atime_deviations": inp.atime_deviations()})
    ana = rec["analysis_definitions"].get("rule", {}).get("agree", "not formed")
    print(f"[D] agree (generator definitions, primary): {rec['agree']}; analysis definitions: {ana}", flush=True)
    return 0


# ---------------------------------------------------------------- CLI


def build_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("a1")
    s.add_argument("--nuwro-frozen", type=Path, required=True)
    s.add_argument("--gibuu-frozen", type=Path, required=True)
    s.add_argument("--out", type=Path, required=True)
    s = sub.add_parser("ch")
    s.add_argument("--a1-json", type=Path, required=True)
    s.add_argument("--out", type=Path, required=True)
    s = sub.add_parser("defs")
    s.add_argument("--rebuild-dir", type=Path, required=True)
    s.add_argument("--out", type=Path, required=True)
    s = sub.add_parser("overlap")
    for k in ("p5", "mnvtune", "cv2d", "q2d", "playlist", "cv3d", "proj3d", "out"):
        s.add_argument(f"--{k}", type=Path, required=True)
    s = sub.add_parser("native")
    s.add_argument("--rebuild-dir", type=Path, required=True)
    s.add_argument("--out", type=Path, required=True)
    return p.parse_args(argv)


def main(argv=None) -> int:
    a = build_args(argv)
    return {"a1": cmd_a1, "ch": cmd_ch, "defs": cmd_defs, "overlap": cmd_overlap, "native": cmd_native}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
