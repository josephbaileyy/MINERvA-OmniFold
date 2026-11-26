#!/usr/bin/env python3
"""V_F (C_e^infl) Phase 2 (FD-VF-ADDITION-DECLARATION.md section 4): the fetch list, and the local recomputes.

fetch-list: the exact pscratch files Phase 2's three cluster-input recomputes read (section 4.2), each with its
committed pin, the committed line that records it, its size from the 2026-11-25 input check (#1327), the code line
that reads it, and the recompute it serves:
- xk: GENCMP X step K replayed through fd_xcov_steps.cmd_k / k_compute under PRODUCTS["g2r"] (the director's route (1),
  2026-11-26). The run-directory files come from xk's own run directory, cov2d-xk-g2r-20261116/run, pinned by its
  NODE-SHA256.txt (each equal to the original gencmp-x-20261102 file's pin, asserted). universes_full.root is never
  listed: only V1 opens it (fd_xcov_steps.py cmd_v1);
- prr: route2.json and route2.npz (prr_read's grade inputs for the IBU records);
- rsn: the NuE flux constraint is shared with xk (one fetch).
V0's and V1's records and the MINOS rescale are committed and read locally. Every row is asserted against #1327's
EXISTS record and its pin source; any disagreement refuses.

Run: python3 -B fd_vf_p2.py fetch-list [--out FILE]"""
import argparse
import hashlib
import io
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                           cwd=Path(__file__).resolve().parent, check=True).stdout.strip())
FD = Path("docs/orchestration/state/measurement-paper/5d-community-20261024/fd")
XK = FD / "receipts-cov2d/g2r/xk"
CHECK = Path("docs/orchestration/state/ben-b-20261124/blocks5d-20261124/vf-input-check-20261125/run/vf_inputs_check.tsv")
PS = "/pscratch/sd/j/josephrb/"
ORIGINAL = PS + "gencmp-x-20261102/"
RUN = PS + "cov2d-xk-g2r-20261116/run/"
STEPS = "nd-unfolding/fd_xcov_steps.py:"
READERS = {"g2r_universes_dir": "604", "cv2d": "533", "playlist": "531", "q2d": "531", "s5": "531",
           "s1_assembly,s1_npz": "538", "flux_constraint": "595,104", "boot_native_receipt": "420",
           "staged_flux_source": "614"}
XK_LOCAL = {"minos_rescaled", "v0", "v1", "universes_identity_check"}    # committed, or never read by K
NEVER = ("universes_full.root", "bkg_dump.npz")                          # never fetched or hashed
# the mapped list (codex-school, 2026-11-26), less the NuE constraint (FD-VF BINDING 2b, the director's ruling 1): its
# /pscratch path runs through a symlinked directory (MParamFiles; attempt 1's STOP), and a byte-identical copy is committed
NUE_PATH = PS + "MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt"
NUE_LOCAL = ("docs/orchestration/state/ben-b-20261124/blocks5d-20261124/run-20261124/session/records/fetch-b5d/"
             "sorted_NuEConstraint_FHC_RHC_IMD.txt", "e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2")
# the MINOS rescale: never fetched (committed; fetch-list excludes its role, XK_LOCAL); K reads it through the remap, so
# its exact /pscratch path maps to the committed copy, pinned at xcov/INPUTS.sha256:13 and NODE-SHA256.txt:233
MINOS_PATH = PS + "2d-closeout-c04repair-20261012/build/minos_rescaled.npz"
MINOS_LOCAL = ("docs/orchestration/state/2d-closeout/c04-repair/products/minos_rescaled.npz",
               "8912376ef2a6cfce8bed515cc945d9d5778cf5c838154a685435c3c7ce25416d")
LOCAL_COPIES = {NUE_PATH: NUE_LOCAL, MINOS_PATH: MINOS_LOCAL}
N_ROWS, N_BYTES = 402, 1595650936 - 25403
HEADER = ("path", "sha256", "pin_source", "size_bytes", "reader_file_line", "recompute")


class Stop(SystemExit):
    def __init__(self, why):
        super().__init__(f"STOP fetch-list: {why}")


def pins(rel: Path, prefix: str = "") -> dict:
    """A sha256 list's rows: {prefix + path: (sha256, "file:line")}."""
    out = {}
    for i, row in enumerate((ROOT / rel).read_text().splitlines(), 1):
        f = row.split()
        if f and re.fullmatch(r"[0-9a-f]{64}", f[0]):
            out[prefix + f[-1]] = (f[0], f"{rel}:{i}")
    return out


def fetch_rows() -> list:
    node = pins(XK / "run/node/NODE-SHA256.txt")
    archive = pins(FD / "xcov/run/hpss/files.sha256", PS)
    external = pins(XK / "INPUTS-g2r.sha256") | pins(FD / "gencmp-e/INPUTS.sha256") | pins(FD / "xcov/INPUTS.sha256")
    prr = pins(FD / "receipts-prr/ibu/attempt3/cluster/log-ibu/SHA256SUMS", PS + "fd-prr-20261108/")
    rows = []
    lines = (ROOT / CHECK).read_text().splitlines()
    if lines[0].split("\t") != ["phase", "readout", "role", "path", "pinned_sha256", "found_sha256", "size", "mtime",
                                "status", "note"]:
        raise Stop("the input check's header changed")
    for row in lines[1:]:
        _, names, role, path, pin, found, size, _, status, _ = row.split("\t")
        if path in prr:
            src = prr[path]
            reader = "nd-unfolding/prior_retention/prr_read.py:" + ("399" if path.endswith(".npz") else "396")
            recompute = "prr"
        elif "xk" in names.split(",") and role not in XK_LOCAL:
            recompute = "xk"
            if path.startswith(ORIGINAL):
                rel = path[len(ORIGINAL):]
                a, n = archive.get(path), node.get("run/" + rel)
                if a is None or n is None or not (a[0] == n[0] == pin):
                    raise Stop(f"{path}: the original's pin, the run copy's and the check's differ")
                src, path = n, RUN + rel                      # xk's own run directory (declaration 4.2)
            else:
                if path not in external:
                    raise Stop(f"{path}: no committed pin")
                src = external[path]
            if role == "boot_xcov_dir":
                reader = STEPS + ("662" if path.endswith(".json") else "666,667")
            elif role == "re2_laterals_and_replicas_dir":
                reader = STEPS + ("623" if "/S3_" in path else "668")
            else:
                reader = STEPS + READERS[role]
            if role in ("flux_constraint", "s1_assembly,s1_npz"):
                recompute = "xk,rsn"
                reader += ",nd-unfolding/rsn/rsn_regrade.py:" + ("244" if role == "flux_constraint" else "245")
        else:
            continue
        if status != "EXISTS" or not (pin == found == src[0]) or not size.isdigit():
            raise Stop(f"{path}: not an EXISTS row equal to its pin ({status}, {size})")
        if any(path.endswith(x) for x in NEVER) or Path(path).name == "data_b-_j-.npz":
            raise Stop(f"{path}: a file the fetch never reads")
        if path in LOCAL_COPIES:                      # held locally at its pin: not fetched
            if pin != LOCAL_COPIES[path][1] or sha256_file(ROOT / LOCAL_COPIES[path][0]) != pin:
                raise Stop(f"{path}: the committed copy is not its pin")
            continue
        rows.append((path, pin, src[1], size, reader, recompute))
    rows.sort()
    if len(rows) != len({r[0] for r in rows}) or len(rows) != N_ROWS or sum(int(r[3]) for r in rows) != N_BYTES:
        raise Stop(f"{len(rows)} rows, {sum(int(r[3]) for r in rows)} bytes: not the mapped {N_ROWS}, {N_BYTES}")
    return rows


def cmd_fetch_list(a) -> int:
    rows = fetch_rows()
    text = "\t".join(HEADER) + "\n" + "".join("\t".join(r) + "\n" for r in rows)
    if a.out:
        if a.out.exists():
            raise Stop(f"{a.out} exists")
        a.out.write_text(text)
    else:
        sys.stdout.write(text)
    by = {}
    for r in rows:
        by.setdefault(r[5], [0, 0])
        by[r[5]][0] += 1
        by[r[5]][1] += int(r[3])
    print(f"fetch-list: {len(rows)} files, {sum(int(r[3]) for r in rows)} bytes; "
          + "; ".join(f"{k} {n} files {b} bytes" for k, (n, b) in sorted(by.items()))
          + f"; sha256 {hashlib.sha256(text.encode()).hexdigest()}", file=sys.stderr)
    return 0


# ---------------------------------------------------------------- p2: the local recomputes (declaration section 4.1)

import json  # noqa: E402

import numpy as np  # noqa: E402

D5 = "docs/orchestration/state/measurement-paper/5d-community-20261024"
P2_OUT = Path(f"{D5}/fd/with-vf/p2")
VF_DP = (f"{D5}/fd/with-vf/data-product/fd_data_product_vf.json", "1a37b0820017f9e5")
OLD_DP_NOPL = (f"{D5}/fd/data-product/fd_data_product.json", "b79556f0")
OLD_DP_CPL = (f"{D5}/fd/with-cpl/data-product/fd_data_product_cpl.json", "d6752d2c")
REPORTED_F = "C_total_plus_C_resp_plus_C_PL5D_plus_DeltaC_e"
WITHOUT_F = "C_total_plus_C_resp_plus_DeltaC_e"
# each OLD matrix name and its V_F counterpart (declaration section 1)
VF_NAME = {"C_total_plus_C_resp": WITHOUT_F, "C_total_plus_C_resp_plus_C_PL5D": REPORTED_F}


def pinned_json(rel_pin):
    rel, pin = rel_pin
    raw = (ROOT / rel).read_bytes()
    h = hashlib.sha256(raw).hexdigest()
    if not h.startswith(pin):
        raise Stop(f"{rel}: sha256 {h[:16]}, pinned {pin}")
    return json.loads(raw), h


# P's tolerance where the producer's input was round-tripped through its readout (V_g from sigma_Vg/f): declared 1e-10;
# on this platform (macOS, numpy 1.26.4 / OpenBLAS) the producers' own checks land at ~2e-10. PENDING the director's
# ruling (2026-11-26); until it, 1e-9, and every field's achieved difference is recorded
RTOL_ROUNDTRIP = 1e-9


P_ACHIEVED = {}         # the largest achieved p difference per control, when p is checked by function identity


def p_control(name, reproduced, committed, rtol=0.0, scale=None, p_fun=None):
    """P (section 6): the producer's arithmetic on the OLD matrix reproduces every field it will replace. rtol = 0 is
    exact equality (bit-identical inputs); otherwise each float must satisfy |a - b| <= rtol * scale(path, b), where
    scale defaults to |b|. Returns the largest achieved relative difference."""
    worst = [0.0, ""]

    def walk(a, b, path):
        if isinstance(b, dict):
            if not isinstance(a, dict) or set(a) != set(b):
                raise Stop(f"P {name}: {path} keys differ")
            pid = p_fun is not None and {"p", "chi2", "ndf"} <= set(b)
            if pid:            # A4 item 3: p by the producer's own function on the committed chi2, bitwise, and printed
                if p_fun(b["chi2"], b["ndf"]) != b["p"] and not (b["p"] == 0.0 and b.get("p_below_floor")):
                    raise Stop(f"P {name}: {path}: the producer's p function on the committed chi2 is not its p")
                if printed_p(a["p"]) != printed_p(b["p"]):
                    raise Stop(f"P {name}: {path}/p prints {printed_p(a['p'])}, committed {printed_p(b['p'])}")
                r = abs(a["p"] - b["p"]) / abs(b["p"]) if b["p"] else abs(a["p"] - b["p"])
                P_ACHIEVED[name] = max(P_ACHIEVED.get(name, 0.0), r)
            for k in b:
                if pid and k == "p":
                    continue
                walk(a[k], b[k], f"{path}/{k}")
        elif isinstance(b, list):
            if not isinstance(a, list) or len(a) != len(b):
                raise Stop(f"P {name}: {path} lengths differ")
            for i, (x, y) in enumerate(zip(a, b)):
                walk(x, y, f"{path}[{i}]")
        elif isinstance(b, float) and not isinstance(b, bool) and rtol > 0:
            sc = abs(b) if scale is None else scale(path, b)
            r = abs(a - b) / sc if sc else abs(a - b)
            if r > worst[0]:
                worst[:] = [r, path]
            if r > rtol:
                raise Stop(f"P {name}: {path} = {a!r}, committed {b!r} (relative {r:.3g} > {rtol:g})")
        elif a != b:
            raise Stop(f"P {name}: {path} = {a!r}, committed {b!r}")
    walk(reproduced, committed, "")
    print(f"PASS control P {name}: the OLD matrix reproduces the committed readout "
          f"({'exactly' if rtol == 0 else f'max relative {worst[0]:.3g} at {worst[1]}, tolerance {rtol:g}'})", flush=True)
    return worst[0]


# eav: step0_metric.py's arithmetic (docs/orchestration/state/eavail-switch-pricing-20261031/step0/step0_metric.py:19-28),
# with the matrices passed explicitly (its "endswith plus_C_PL5D" selection would pick the old matrix)
EAV_DIR = "docs/orchestration/state/eavail-switch-pricing-20261031/step0"
EAV_OUT = (f"{EAV_DIR}/step0_metric.txt", "3e8bd546")
EAV_STEP0 = (f"{EAV_DIR}/step0.json", "c284a6b3")
EAV_STEP0B = (f"{EAV_DIR}/step0b.json", "d0ea2797")   # cluster-outputs-sha256.txt:4


def eav_metric(f, mats, shifts):
    out = {}
    for name, rel in shifts.items():
        d = np.asarray(rel, float) * f
        o = {}
        for mn, M in mats.items():
            y = np.linalg.solve(np.linalg.cholesky(M), d)
            o[mn] = {"norm_sqrt_dCinvd": float(np.sqrt(y @ y)), "dCinvd": float(y @ y),
                     "per_cell_over_sigma": [round(float(v), 4) for v in d / np.sqrt(np.diag(M))],
                     "max_abs_over_sigma": float(np.max(np.abs(d / np.sqrt(np.diag(M))))),
                     "quadrature_of_per_cell": float(np.sqrt(np.sum((d / np.sqrt(np.diag(M))) ** 2)))}
        out[name] = o
    return out


def p2_eav(vf):
    committed, h = pinned_json(EAV_OUT)
    s0, _ = pinned_json(EAV_STEP0)
    s0b, _ = pinned_json(EAV_STEP0B)
    shifts = {"prior_level": s0["truth_denom"]["cells_rel_change"],
              "first_order_unfolded": s0b["a_unfolded_cells_rel_change"]}
    dpn, _ = pinned_json(OLD_DP_NOPL)
    dpc, _ = pinned_json(OLD_DP_CPL)
    f = np.asarray(dpn["f"], float)
    old = {"C_total_plus_C_resp": np.asarray(dpn["matrices"]["C_total_plus_C_resp"], float),
           "C_total_plus_C_resp_plus_C_PL5D": np.asarray(dpc["matrices"]["C_total_plus_C_resp_plus_C_PL5D"], float)}
    p_control("eav", json.loads(json.dumps(eav_metric(f, old, shifts))), committed)
    if not np.array_equal(np.asarray(vf["f"], float), f):
        raise Stop("eav: the V_F product's f is not the data product's")
    new = eav_metric(f, {VF_NAME[k]: np.asarray(vf["matrices"][VF_NAME[k]], float) for k in old}, shifts)
    patch = {"readout": EAV_OUT[0], "readout_sha256": h,
             "replaced": [f"/{s}/{k}" for s in shifts for k in old],
             "by": [f"/{s}/{VF_NAME[k]}" for s in shifts for k in old],
             "matrices": [VF_NAME[k] for k in old], "control_P": "PASS"}
    return dict(new, vf_patch=patch)


# e2: fd_gencmp_e2.chi2_rows and reading, imported unchanged, on e2.json's committed S arrays and E-1's Stage G records
# (g, V_g = (sigma_Vg_over_f f)^2), with C_rest + DeltaC_e; the composition of cmd_chi2 (fd_gencmp_e2.py) carried over
E2 = (f"{D5}/fd/gencmp-e2/rerun1/chi2/e2.json", "0aa73ebf")
E1_OLD = {"with": (f"{D5}/fd/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_readout.json", "a19009e0"),
          "nopl": (f"{D5}/fd/gencmp-e/rerun1/chain/chdefs/nopl/readout/fd_g_readout.json", "d9a1ce38")}
E1_VF = {"with": (f"{D5}/fd/with-vf/readout/vf-with-E/fd_g_readout.json", "7034a08e"),
         "nopl": (f"{D5}/fd/with-vf/readout/vf-nopl-E/fd_g_readout.json", "eefe1c6d")}
CPL_BLOCK = (f"{D5}/fd/with-cpl/block/cpl_block.npz", "d9aa32fd")


def e2_compose(E2M, readouts, f, rests, S_c, S_ch, S_n):
    res = {}
    for arm, C_rest in rests.items():
        r1 = readouts[arm]
        carbon, chm, c43 = (E2M.chi2_rows(r1, f, C_rest, S) for S in (S_c, S_ch, S_n))
        res[arm] = {name: {k: {"carbon": carbon[name][k], "CH": chm[name][k], "delta": chm[name][k] - carbon[name][k],
                               "carbon_seed43": c43[name][k], "delta_noise": c43[name][k] - carbon[name][k]}
                           for k in ("total", "shape_only")} for name in carbon}
    cells = [v[k] for arm in res.values() for v in arm.values() for k in ("total", "shape_only")]
    dmax = float(max(abs(c["delta"]) for c in cells))
    dnoise = float(max(abs(c["delta_noise"]) for c in cells))
    dflag = float(max(abs(res["with"][p]["total"]["delta"]) for p in E2M.CORNER))
    return {"chi2": res, "delta_max_abs": dmax, "delta_noise_max_abs": dnoise, "reading": E2M.reading(dmax, dnoise),
            "delta_flag_value": dflag, "delta_flag_exceeded": dflag > E2M.DELTA_FLAG}


def npz_pinned(rel_pin):
    rel, pin = rel_pin
    raw = (ROOT / rel).read_bytes()
    if not hashlib.sha256(raw).hexdigest().startswith(pin):
        raise Stop(f"{rel}: not its pinned bytes")
    import io
    return np.load(io.BytesIO(raw), allow_pickle=False)


def p2_e2(vf):
    sys.path.insert(0, str(ROOT / "nd-unfolding"))
    import fd_gencmp_e2 as E2M
    committed, h = pinned_json(E2)
    S_c, S_ch, S_n = (np.asarray(committed[k], float) for k in ("S_carbon", "S_CH", "S_carbon_seed43"))
    blk = npz_pinned(CPL_BLOCK)
    dpc, _ = pinned_json(OLD_DP_CPL)
    f = np.asarray(blk["f"], float)
    Ce = np.asarray(dpc["matrices"]["C_e"], float)
    Cr, Cpl = np.asarray(blk["C_resp"], float), np.asarray(blk["C_PL5D"], float)
    old_rests = {"with": Ce + Cr + Cpl, "nopl": Ce + Cr}
    old = e2_compose(E2M, {a: pinned_json(E1_OLD[a])[0] for a in E1_OLD}, f, old_rests, S_c, S_ch, S_n)
    want = {"chi2": committed["chi2"], "delta_max_abs": committed["delta_max_abs"],
            "delta_noise_max_abs": committed["delta_noise_max_abs"], "reading": committed["reading"],
            "delta_flag_value": committed["delta_flag"]["value"],
            "delta_flag_exceeded": committed["delta_flag"]["exceeded"]}
    chi2_scale = lambda path, b: (abs(committed["chi2"][path.split("/")[2]][path.split("/")[3]][path.split("/")[4]]  # noqa: E731
                                      ["carbon"]) if path.startswith("/chi2/") else
                                  max(abs(v[k]["carbon"]) for arm in committed["chi2"].values() for v in arm.values()
                                      for k in ("total", "shape_only")))
    achieved = p_control("e2", json.loads(json.dumps(old, default=float)), want, RTOL_ROUNDTRIP, chi2_scale)
    if not np.array_equal(np.asarray(vf["f"], float), f):
        raise Stop("e2: the V_F product's f is not the block's")
    dF = np.asarray(vf["matrices"]["DeltaC_e"], float)
    new = e2_compose(E2M, {a: pinned_json(E1_VF[a])[0] for a in E1_VF}, f,
                     {a: C + dF for a, C in old_rests.items()}, S_c, S_ch, S_n)
    out = json.loads(json.dumps(committed))
    out.update(chi2=new["chi2"], delta_max_abs=new["delta_max_abs"], delta_noise_max_abs=new["delta_noise_max_abs"],
               reading=new["reading"])
    out["delta_flag"] = dict(out["delta_flag"], value=new["delta_flag_value"], exceeded=new["delta_flag_exceeded"])
    out["vf_patch"] = {"readout": E2[0], "readout_sha256": h,
                       "replaced": ["/chi2", "/delta_max_abs", "/delta_noise_max_abs", "/reading", "/delta_flag/value",
                                    "/delta_flag/exceeded"],
                       "matrices": {"with": "C_e + C_resp + C_PL5D + DeltaC_e + C_model(S)",
                                    "nopl": "C_e + C_resp + DeltaC_e + C_model(S)"},
                       "stage_g_readouts": {a: E1_VF[a][0] for a in E1_VF}, "control_P": "PASS",
                       "control_P_tolerance": {"rtol": RTOL_ROUNDTRIP, "scale": "each chi2's carbon value",
                                               "achieved_max": achieved,
                                               "why": "V_g round-tripped from sigma_Vg/f (declaration section 6, P)"}}
    return out


# gover, cr: each quadrant's sigma16 = sqrt(a^T C a + sum of its unreported boxes squared) (fd_gencmp.cmd_overlap's
# arithmetic, fd_gencmp.py:525-531), and fd_gencmp.rule, imported unchanged, on the committed d, S and 2D sigma
GOVER = (f"{D5}/fd/gencmp/readout/overlap.json", "82b3528a")
CR = (f"{D5}/fd/receipts-cov2d/g2r/cr/run/node/g2r/overlap_refined.json", "0734cf4a")
RTOL_EXACT = 1e-12      # bit-identical inputs (declaration section 6, P)


def overlap_fields(GC, rec, R_rep, R_nopl):
    """The C_rep-dependent fields of one quadrant record, from its cells, boxes and committed d / 2D sigma."""
    a16 = np.zeros(16)
    a16[[int(c[1:]) for c in rec["cells"]]] = 1.0
    box2 = sum(v ** 2 for v in rec["unreported_boxes_P5"].values())
    s_rep = float(np.sqrt(float(np.sqrt(a16 @ R_rep @ a16)) ** 2 + box2))
    s_nopl = float(np.sqrt(float(np.sqrt(a16 @ R_nopl @ a16)) ** 2 + box2))
    out = {"sigma16_reported": s_rep, "sigma16_without_C_PL5D": s_nopl}
    d2 = rec["2D"]
    if "sigma" in d2:
        out["2D"] = {**GC.rule(d2["d"], s_rep, d2["sigma"]),
                     "printed_only_without_C_PL5D": GC.rule(d2["d"], s_nopl, d2["sigma"])}
    out["3D"] = GC.rule(rec["3D"]["d"], s_rep, None)
    return out


def committed_overlap_fields(rec, fields):
    """The same fields as the committed record holds them."""
    out = {k: rec[k] for k in ("sigma16_reported", "sigma16_without_C_PL5D")}
    if "2D" in fields:
        out["2D"] = {k: rec["2D"][k] for k in fields["2D"] if k != "printed_only_without_C_PL5D"}
        out["2D"]["printed_only_without_C_PL5D"] = {k: rec["2D"]["printed_only_without_C_PL5D"][k]
                                                     for k in fields["2D"]["printed_only_without_C_PL5D"]}
    out["3D"] = {k: rec["3D"][k] for k in fields["3D"]}
    return out


def merge(dst, src):
    for k, v in src.items():
        if isinstance(v, dict):
            merge(dst[k], v)
        else:
            dst[k] = v


def p2_overlap(name, rel_pin, vf):
    sys.path.insert(0, str(ROOT / "nd-unfolding"))
    import fd_gencmp as GC
    committed, h = pinned_json(rel_pin)
    dpc, _ = pinned_json(OLD_DP_CPL)
    R_old = (np.asarray(dpc["matrices"]["C_total_plus_C_resp_plus_C_PL5D"], float),
             np.asarray(dpc["matrices"]["C_total_plus_C_resp"], float))
    R_new = (np.asarray(vf["matrices"][REPORTED_F], float), np.asarray(vf["matrices"][WITHOUT_F], float))
    out = json.loads(json.dumps(committed))
    achieved, replaced = 0.0, []
    for q, rec in committed["quadrants"].items():
        old = overlap_fields(GC, rec, *R_old)
        achieved = max(achieved, p_control(f"{name} {q}", json.loads(json.dumps(old)),
                                           committed_overlap_fields(rec, old), RTOL_EXACT))
        new = overlap_fields(GC, rec, *R_new)
        merge(out["quadrants"][q], new)
        replaced += [f"/quadrants/{q}/{k}" for k in ("sigma16_reported", "sigma16_without_C_PL5D")]
        replaced += [f"/quadrants/{q}/2D/{k}" for k in new.get("2D", {})] + [f"/quadrants/{q}/3D/{k}" for k in new["3D"]]
    out["vf_patch"] = {"readout": rel_pin[0], "readout_sha256": h, "replaced": replaced,
                       "matrices": {"reported": REPORTED_F, "without_C_PL5D": WITHOUT_F}, "control_P": "PASS",
                       "control_P_tolerance": {"rtol": RTOL_EXACT, "achieved_max": achieved,
                                               "why": "bit-identical committed inputs"}}
    return out


# gdefs, gch, gnat: every chi2 is an embedded fd_g_compare.compare record (cells, f, g, sigma_Vg_over_f) under
# "reported" and "without_C_PL5D"; each is recomputed by compare, imported unchanged, with V_g = (sigma_Vg_over_f f)^2 on
# its cells and the matrices fd_gencmp.result builds (C_e + C_model_abs + C_resp [+ C_PL5D]), then + DeltaC_e
GDEFS = (f"{D5}/fd/gencmp/readout/defs.json", "544f4f43")
GCH = (f"{D5}/fd/gencmp/readout/ch.json", "cd111b8e")
GNAT = (f"{D5}/fd/gencmp/readout/native.json", "df48fbeb")
PAIR = ("reported", "without_C_PL5D")
NAMES_OLD = {"reported": "C_total + C_resp + C_PL5D", "without_C_PL5D": "C_total + C_resp"}
NAMES_VF = {"reported": "C_total + C_resp + C_PL5D + DeltaC_e", "without_C_PL5D": "C_total + C_resp + DeltaC_e"}


def gencmp_matrices(vf):
    blk = npz_pinned(CPL_BLOCK)
    dpc, _ = pinned_json(OLD_DP_CPL)
    f = np.asarray(blk["f"], float)
    Ct = sum(np.asarray(dpc["matrices"][k], float) for k in ("C_e", "C_model_abs"))
    Cr, Cpl = np.asarray(blk["C_resp"], float), np.asarray(blk["C_PL5D"], float)
    old = {"reported": Ct + Cr + Cpl, "without_C_PL5D": Ct + Cr}
    dF = np.asarray(vf["matrices"]["DeltaC_e"], float)
    if not np.array_equal(np.asarray(vf["f"], float), f):
        raise Stop("the V_F product's f is not the block's")
    return f, old, {k: M + dF for k, M in old.items()}


def pair_paths(x, path=""):
    if isinstance(x, dict):
        if all(k in x and isinstance(x[k], dict) and "sigma_Vg_over_f" in x[k] for k in PAIR):
            yield path, x
            return
        for k, v in x.items():
            yield from pair_paths(v, f"{path}/{k}")


def recompare(FG, f, rec, M, name):
    cells = [int(c[1:]) for c in rec["cells"]]
    g, Vg = np.zeros(f.size), np.zeros(f.size)
    g[cells] = rec["g"]
    Vg[cells] = (np.asarray(rec["sigma_Vg_over_f"], float) * f[cells]) ** 2
    return json.loads(json.dumps(FG.compare(f, g, Vg, M, cells, name)))


def printed_p(p):
    """p as the note prints it: make_values_fived16.p_tex (two significant figures, scientific below 1e-3) and its
    paper form (paper_prec's "<10^k" / "=x"), both imported unchanged."""
    sys.path.insert(0, str(ROOT / "docs/analysis-note"))
    import make_values_fived16 as MV
    t = MV.p_tex(p)
    return t, tuple(sorted(MV.paper_prec("f0-x-p", t).values()))


def p_compare_record(FG, label, old, committed):
    """P on one compare record: chi2 at RTOL_ROUNDTRIP (V_g round-tripped); p by function identity, exactly
    (chi2_sf(committed chi2, ndf) == committed p, bitwise), its achieved difference only recorded; every other field at
    RTOL_EXACT. Returns (chi2 achieved, p achieved)."""
    worst = [0.0, 0.0]
    for part in ("total", "shape_only"):
        a, b = old[part], committed[part]
        if FG.chi2_sf(b["chi2"], b["ndf"]) != b["p"]:
            raise Stop(f"P {label}/{part}: chi2_sf(committed chi2) is not the committed p")
        worst[0] = max(worst[0], abs(a["chi2"] - b["chi2"]) / abs(b["chi2"]))
        worst[1] = max(worst[1], abs(a["p"] - b["p"]) / abs(b["p"]) if b["p"] else abs(a["p"] - b["p"]))
        if worst[0] > RTOL_ROUNDTRIP:
            raise Stop(f"P {label}/{part}: chi2 relative {worst[0]:.3g} > {RTOL_ROUNDTRIP:g}")
        if printed_p(a["p"]) != printed_p(b["p"]):           # the director's printed-value check (2026-11-26)
            raise Stop(f"P {label}/{part}: p prints {printed_p(a['p'])}, committed {printed_p(b['p'])}")
        p_control(f"{label}/{part}", {k: v for k, v in a.items() if k not in ("chi2", "p")},
                  {k: v for k, v in b.items() if k not in ("chi2", "p")}, RTOL_EXACT)
    p_control(label, {k: v for k, v in old.items() if k not in ("total", "shape_only")},
              {k: v for k, v in committed.items() if k not in ("total", "shape_only")}, RTOL_EXACT)
    return worst


def p2_compare(name, rel_pin, vf, extra=None):
    sys.path.insert(0, str(ROOT / "nd-unfolding"))
    import fd_g_compare as FG
    committed, h = pinned_json(rel_pin)
    f, old_M, new_M = gencmp_matrices(vf)
    out = json.loads(json.dumps(committed))
    chi2_w = p_w = 0.0
    replaced = []
    for path, pair in pair_paths(committed):
        dst = out
        for k in path.strip("/").split("/"):
            dst = dst[k]
        for k in PAIR:
            old = recompare(FG, f, pair[k], old_M[k], NAMES_OLD[k])
            cw, pw = p_compare_record(FG, f"{name}{path}/{k}", old, pair[k])
            chi2_w, p_w = max(chi2_w, cw), max(p_w, pw)
            dst[k] = recompare(FG, f, pair[k], new_M[k], NAMES_VF[k])
            replaced.append(f"{path}/{k}")
    patch = {"readout": rel_pin[0], "readout_sha256": h, "replaced": replaced, "matrices": NAMES_VF,
             "control_P": "PASS",
             "control_P_tolerance": {"chi2": {"rtol": RTOL_ROUNDTRIP, "achieved_max": chi2_w,
                                              "why": "V_g round-tripped from sigma_Vg/f (amendment A4)"},
                                     "p": {"check": "chi2_sf(committed chi2, ndf) == committed p, bitwise; the "
                                                    "reproduced p prints the committed p's strings (p_tex, paper form)",
                                           "achieved_max": p_w, "why": "derived from chi2 through chi2_sf"},
                                     "other_fields": {"rtol": RTOL_EXACT}}}
    if extra:
        extra(committed, out, f, old_M, new_M, patch)
    out["vf_patch"] = patch
    return out


def gdefs_extra(committed, out, f, old_M, new_M, patch):
    """gdefs' sigma-ratio fields (fd_gencmp.cmd_defs :337-346) and its 2 x 2 table (:369). delta_over_sigma is recomputed
    from the embedded definitions' g; the seed spreads and the W-/axis-/mass-only ratios are rescaled by
    sigma_old / sigma_new (their numerators are not serialized); the seed flag is re-read with SEED_SPREAD_FLAG."""
    import fd_gencmp as GC
    s_old, s_new = np.sqrt(np.diag(old_M["reported"])), np.sqrt(np.diag(new_M["reported"]))
    replaced, flags = [], []
    for gen, grec in committed["generators"].items():
        for t, rec in grec.items():
            if not (isinstance(rec, dict) and "delta_over_sigma" in rec):
                continue
            cells = [int(c[1:]) for c in rec["cells"]]
            g0 = np.asarray(rec["generator_definitions"]["g"], float)
            g1 = np.asarray(rec["analysis_definitions"]["g"], float)
            p_control(f"gdefs {gen}/{t} delta_over_sigma", ((g1 - g0) / s_old[cells]).tolist(), rec["delta_over_sigma"],
                      RTOL_EXACT)
            dst = out["generators"][gen][t]
            dst["delta_over_sigma"] = ((g1 - g0) / s_new[cells]).tolist()
            ratio = s_old[cells] / s_new[cells]
            for k in [k for k in rec if k.endswith("_delta_over_sigma")] + ["seed_spread_over_sigma"]:
                dst[k] = (np.asarray(rec[k], float) * ratio).tolist()
                replaced.append(f"/generators/{gen}/{t}/{k}")
            dst["seed_spread_flag"] = bool(np.any(np.asarray(dst["seed_spread_over_sigma"]) > GC.SEED_SPREAD_FLAG))
            if rec["seed_spread_flag"] != dst["seed_spread_flag"]:
                flags.append(f"{gen}/{t}: {rec['seed_spread_flag']} -> {dst['seed_spread_flag']}")
            replaced += [f"/generators/{gen}/{t}/delta_over_sigma", f"/generators/{gen}/{t}/seed_spread_flag"]
    # Table IV's corner (CH, analysis definitions) for the four GENCMP predictions: E-1's control XC makes Stage G's chdefs
    # chain this computation (make_values_fived16.table4 asserts it at 1e-12). Phase 1 computed the V_F Stage G on
    # login02, so the corner takes those records, after this Mac's recompute agrees with them within A4's 1e-9
    corner_w = 0.0
    for mat, rel_pin in (("reported", E1_VF["with"]), ("without_C_PL5D", E1_VF["nopl"])):
        sg = {q["name"]: q for q in pinned_json(rel_pin)[0]["predictions"]}
        for n in ("genie_cv", "genie_mec", "nuwro", "gibuu"):
            dst = out["generators"][n]["CH"]["analysis_definitions"]["chi2"]
            mine, theirs = dst[mat], {k: sg[n][k] for k in dst[mat]}
            for part in ("total", "shape_only"):
                r = abs(mine[part]["chi2"] / theirs[part]["chi2"] - 1)
                corner_w = max(corner_w, r)
                if r > RTOL_ROUNDTRIP or mine[part]["matrix"] != theirs[part]["matrix"]:
                    raise Stop(f"XC gdefs {n}/{mat}/{part}: the recompute and Phase 1's Stage G differ ({r:.3g})")
            if not np.array_equal(mine["g"], theirs["g"]) or mine["cells"] != theirs["cells"]:
                raise Stop(f"XC gdefs {n}/{mat}: g or cells differ from Phase 1's Stage G")
            dst[mat] = json.loads(json.dumps(theirs))
    patch["table_iv_corner"] = {"source": {"reported": E1_VF["with"][0], "without_C_PL5D": E1_VF["nopl"][0]},
                                "check": "this recompute within 1e-9 of Phase 1's V_F Stage G (E-1 control XC)",
                                "achieved_max": corner_w}
    table = {g: {t: {dfn: GC.summary(out["generators"][g][t][dfn]["chi2"])
                     for dfn in ("generator_definitions", "analysis_definitions")}
                 for t in ("carbon", "CH") if t in out["generators"][g]} for g in out["generators"]}
    old_table = {g: {t: {dfn: GC.summary(committed["generators"][g][t][dfn]["chi2"])
                         for dfn in ("generator_definitions", "analysis_definitions")}
                     for t in ("carbon", "CH") if t in committed["generators"][g]} for g in committed["generators"]}
    p_control("gdefs table_2x2", old_table, committed["table_2x2"], RTOL_EXACT)
    out["table_2x2"] = table
    patch["replaced"] += replaced + ["/table_2x2"]
    patch["sigma_ratio_fields"] = ("seed_spread_over_sigma and *_delta_over_sigma rescaled by sigma_old/sigma_new on "
                                   "their cells (numerators not serialized); delta_over_sigma recomputed from g")
    patch["seed_spread_flag_changes"] = flags


# e2sens: x_e2_sens.py's arithmetic (gencmp-e2/rerun1/sens/x_e2_sens.py:26-55) with fd_gencmp_e2's functions, on e2's
# committed S arrays (its S_carbon is cmodel_5d.json's S bitwise, the script's own control) and C_rest + DeltaC_e
E2SENS = (f"{D5}/fd/gencmp-e2/rerun1/sens/x_e2_sens.out.txt", "223f3f88")


def e2sens_compute(E2M, readouts, f, rests, S_c, S_ch):
    out = {"chi2": {}, "sigma": {}}
    sig = lambda C: np.sqrt(np.diag(C))  # noqa: E731
    Mc, Mch = E2M.model_abs(f, S_c), E2M.model_abs(f, S_ch)
    for arm, C_rest in rests.items():
        r1 = readouts[arm]
        carbon, ch = E2M.chi2_rows(r1, f, C_rest, S_c), E2M.chi2_rows(r1, f, C_rest, S_ch)
        removed = E2M.chi2_rows(r1, f, C_rest, np.zeros_like(S_c))
        doubled = E2M.chi2_rows(r1, f, C_rest + Mc, S_c)
        out["chi2"][arm] = {q: {k: {"removed": removed[q][k], "carbon": carbon[q][k], "doubled": doubled[q][k],
                                    "CH": ch[q][k]} for k in ("total", "shape_only")} for q in E2M.CORNER}
        sc, sch = sig(C_rest + Mc), sig(C_rest + Mch)
        rel = sch / sc - 1
        i = int(np.argmax(np.abs(rel)))
        out["sigma"][f"{arm}_total"] = {"max_abs_rel_change": float(abs(rel[i])), "signed": float(rel[i]), "cell": i,
                                        "sigma_over_f_carbon": float(sc[i] / f[i]),
                                        "sigma_over_f_CH": float(sch[i] / f[i]), "per_cell_rel_change": rel.tolist()}
    mc, mch = sig(Mc) / f, sig(Mch) / f
    d = mch - mc
    i, j = int(np.argmax(np.abs(d))), int(np.argmax(np.abs(mch / mc - 1)))
    out["sigma"]["C_model"] = {"max_abs_change_over_f": float(abs(d[i])), "signed_change_over_f": float(d[i]), "cell": i,
                               "sigma_over_f_carbon": float(mc[i]), "sigma_over_f_CH": float(mch[i]),
                               "max_abs_rel_change": float(abs(mch[j] / mc[j] - 1)), "cell_rel": j,
                               "per_cell_sigma_over_f_carbon": mc.tolist(), "per_cell_sigma_over_f_CH": mch.tolist(),
                               "n_cells": int(f.size), "cells_with_zero_carbon_sigma": int((mc == 0).sum())}
    return out


def p2_e2sens(vf):
    sys.path.insert(0, str(ROOT / "nd-unfolding"))
    import fd_gencmp_e2 as E2M
    rel, pin = E2SENS
    raw = (ROOT / rel).read_bytes()
    h = hashlib.sha256(raw).hexdigest()
    if not h.startswith(pin):
        raise Stop(f"{rel}: not its pinned bytes")
    text = raw.decode()
    committed = json.loads(text[text.index("\n{") + 1:])
    e2, _ = pinned_json(E2)
    S_c, S_ch = np.asarray(e2["S_carbon"], float), np.asarray(e2["S_CH"], float)
    blk = npz_pinned(CPL_BLOCK)
    dpc, _ = pinned_json(OLD_DP_CPL)
    f = np.asarray(blk["f"], float)
    Ce = np.asarray(dpc["matrices"]["C_e"], float)
    Cr, Cpl = np.asarray(blk["C_resp"], float), np.asarray(blk["C_PL5D"], float)
    rests = {"with": Ce + Cr + Cpl, "nopl": Ce + Cr}
    old = json.loads(json.dumps(e2sens_compute(E2M, {a: pinned_json(E1_OLD[a])[0] for a in E1_OLD}, f, rests, S_c, S_ch)))
    chi2_scale = lambda path, b: abs(committed["chi2"][path.split("/")[1]][path.split("/")[2]]  # noqa: E731
                                     [path.split("/")[3]]["carbon"])     # path /<arm>/<prediction>/<kind>/<field>
    w_chi2 = p_control("e2sens chi2", old["chi2"], committed["chi2"], RTOL_ROUNDTRIP, chi2_scale)
    w_sig = p_control("e2sens sigma", old["sigma"], committed["sigma"], RTOL_EXACT)
    dF = np.asarray(vf["matrices"]["DeltaC_e"], float)
    new = e2sens_compute(E2M, {a: pinned_json(E1_VF[a])[0] for a in E1_VF}, f,
                         {a: C + dF for a, C in rests.items()}, S_c, S_ch)
    out = dict(committed, chi2=new["chi2"], sigma=new["sigma"])
    out["vf_patch"] = {"readout": rel, "readout_sha256": h, "replaced": ["/chi2", "/sigma"],
                       "matrices": {"with": "C_e + C_resp + C_PL5D + DeltaC_e + C_model(S)",
                                    "nopl": "C_e + C_resp + DeltaC_e + C_model(S)"}, "control_P": "PASS",
                       "control_P_tolerance": {"chi2": {"rtol": RTOL_ROUNDTRIP, "scale": "each chi2's carbon value",
                                                        "achieved_max": w_chi2, "why": "amendment A4"},
                                               "sigma": {"rtol": RTOL_EXACT, "achieved_max": w_sig}},
                       "note": "controls and env are the committed run's; the V_F values are this recompute's"}
    head = text[:text.index("\n{")]             # the receipt's form, as make_values_fived16.e2_values parses it
    return {"_text": head + "\n" + json.dumps(out, indent=1) + "\n", "vf_patch": out["vf_patch"]}


# V-ATLAS: valid_region.readings, imported unchanged, on its six inputs with I1 = Phase 1's V_F with-block F0b and I4 =
# the V_F data product, whose reported matrix is given under valid_region's COV_KEY name in this process's copy
VR_DIR = "docs/orchestration/state/2d-closeout/valid-region-20261107"
VATLAS = (f"{VR_DIR}/receipts/read/readout.json", "91bb604e")
VF_F0B_WITH = (f"{D5}/fd/with-vf/readout/vf-with-S/fd_f0b_readout.json", "432243e1")


def p2_vatlas(vf):
    sys.path.insert(0, str(ROOT / VR_DIR))
    import valid_region as VR
    committed, h = pinned_json(VATLAS)
    pins = VR.read_pins(ROOT)
    d = VR.load_inputs(ROOT)
    for key, rel in VR.INPUTS.items():
        if not sha256_file(ROOT / rel) == pins[rel] == committed["inputs_sha256"][key]:
            raise Stop(f"V-ATLAS {key}: not the pinned input")
    old = json.loads(json.dumps(VR.readings(d)))
    w = p_control("V-ATLAS", old, committed["readings"], RTOL_EXACT)
    dv = dict(d)
    dv["I1"] = pinned_json(VF_F0B_WITH)[0]
    i4 = json.loads(json.dumps(vf))
    i4["matrices"][VR.COV_KEY] = i4["matrices"][REPORTED_F]
    dv["I4"] = i4
    out = json.loads(json.dumps(committed))
    out["readings"] = json.loads(json.dumps(VR.readings(dv)))
    out["vf_patch"] = {"readout": VATLAS[0], "readout_sha256": h, "replaced": ["/readings"],
                       "inputs": {"I1": VF_F0B_WITH[0], "I4": VF_DP[0] + f" (its {REPORTED_F} under {VR.COV_KEY})"},
                       "matrices": {"reported": REPORTED_F}, "control_P": "PASS",
                       "control_P_tolerance": {"rtol": RTOL_EXACT, "achieved_max": w}}
    return out


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# prr: prr_read's grade functions, imported unchanged. Its grade matrices (grade_matrices, with its own C-CT control)
# get + DeltaC_e/ff; the (e) records are regraded from their committed r with N = 0; the IBU records from route2.npz's
# estimates against its own truths (C-IBU held them equal to (e)'s to 1e-12); then readings() re-reads PR-1..PR-3
PRR = (f"{D5}/fd/receipts-prr/read/cluster/readout.json", "9238f22b")
FETCHED = {"route2.json": ("fd-prr-20261108/route2/route2.json", "ac6b1940659c6ae4"),
           "route2.npz": ("fd-prr-20261108/route2/route2.npz", "759be4ab28cc1095")}


def fetched(fetch_dir, name):
    rel, pin = FETCHED[name]
    path = Path(fetch_dir) / rel
    if not path.is_file() or not sha256_file(path).startswith(pin):
        raise Stop(f"fetched {rel}: missing or not its pinned bytes")
    return path


def p2_prr(vf, fetch_dir):
    sys.path.insert(0, str(ROOT / "nd-unfolding/prior_retention"))
    import prr_read as PR
    import prr_ibu as RI
    committed, h = pinned_json(PRR)
    mats_old, f, _ = PR.grade_matrices(ROOT)
    dFr = np.asarray(vf["matrices"]["DeltaC_e"], float) / np.outer(f, f)
    mats_new = {t: M + dFr for t, M in mats_old.items()}
    out = json.loads(json.dumps(committed))
    q_old, q_new, w = {}, {}, 0.0
    for key, rec in committed["table"].items():
        lv, t, sd = key.split("/")
        r = np.asarray(rec["r"], float)
        g_old = json.loads(json.dumps(PR.table_ii(r, mats_old[t])))
        w = max(w, p_control(f"prr (e) {key}", g_old, rec["grade"], RTOL_EXACT))
        g_new = json.loads(json.dumps(PR.table_ii(r, mats_new[t])))
        out["table"][key]["grade"] = g_new
        q_old[(lv, t, int(sd[1:]))] = dict(rec, grade=g_old)
        q_new[(lv, t, int(sd[1:]))] = dict(rec, grade=g_new)
    rec2 = json.loads(fetched(fetch_dir, "route2.json").read_text())
    with np.load(fetched(fetch_dir, "route2.npz"), allow_pickle=False) as z:
        arr = {k: np.asarray(z[k]) for k in z.files if k != "meta"}
    ks = [int(k) for k in rec2["ks"]]
    qi_old, qi_new, wi = {}, {}, 0.0
    for t, sd in RI.experiments():
        key = f"{t}_s{sd}"
        F, xt = arr[f"{key}__F_{RI.VARIANT}"], np.asarray(arr[f"{key}__X_true"], float)
        for i, k in enumerate(ks):
            ck = f"K{k}/{t}/s{sd}"
            r = np.asarray(F[i], float) / xt - 1
            g_old = json.loads(json.dumps(PR.table_ii(r, mats_old[t])))
            wi = max(wi, p_control(f"prr IBU {ck}", g_old, committed["ibu"][ck]["grade"], RTOL_IBU))
            g_new = json.loads(json.dumps(PR.table_ii(r, mats_new[t])))
            out["ibu"][ck]["grade"] = g_new
            qi_old[(k, t, sd)] = dict(committed["ibu"][ck], grade=g_old)
            qi_new[(k, t, sd)] = dict(committed["ibu"][ck], grade=g_new)
    p_control("prr readings", json.loads(json.dumps(PR.readings(q_old, qi_old))), committed["readings"], RTOL_EXACT)
    out["readings"] = json.loads(json.dumps(PR.readings(q_new, qi_new)))
    out["vf_patch"] = {"readout": PRR[0], "readout_sha256": h,
                       "replaced": ["/table/*/grade", "/ibu/*/grade", "/readings"],
                       "matrices": "each truth's F0b grade matrix (prr_read.grade_matrices) + DeltaC_e/ff",
                       "fetched": {k: v[0] for k, v in FETCHED.items()}, "control_P": "PASS",
                       "control_P_tolerance": {"(e)": {"rtol": RTOL_EXACT, "achieved_max": w},
                                               "IBU": {"rtol": RTOL_IBU, "achieved_max": wi,
                                                       "why": "route2's truths, equal to (e)'s to 1e-12 (C-IBU)"}}}
    return out


# rsnregrade, rsn: rsn_regrade.run()'s composition (rsn/rsn_regrade.py:233-294) with its functions imported unchanged, X
# then X_F = X + DeltaC_e; NC-R reproduces the committed F1 (OLD) and Phase 1's V_F F1 (V_F); then rsn_read.read, with
# the V_F F1's sigma under rsn_read.SIGMA_KEY's name in this process's copy
RSN_DIR = f"{D5}/fd/referee-sensitivity-20261111"
RSN_REGRADE = (f"{RSN_DIR}/connect-post/run-20261112/regrade.json", "cb5f5d17")
RSN_READOUT = (f"{RSN_DIR}/connect-post/run-20261112/rsn_readout.json", "6291f48d")
RSN_CMODEL_NPZ = (f"{RSN_DIR}/connect-post/run-20261112/cmodel/rsn_cmodel.npz", "faa9d01f")
RSN_CMODEL_JSON = (f"{RSN_DIR}/connect-post/run-20261112/cmodel/rsn_cmodel.json", "9d2d315f")
RSN_PREP = (f"{RSN_DIR}/connect1/run-20261112/prep.json", "db61ae8c")        # inputs.tsv (#1327)
F1_TABLE = ("docs/orchestration/state/ben-b-20261124/selection-20261124/record/selection/fd_f1_experiments.npz", "997c7dae")
NUE = ("docs/orchestration/state/ben-b-20261124/blocks5d-20261124/run-20261124/session/records/fetch-b5d/"
       "sorted_NuEConstraint_FHC_RHC_IMD.txt", "e38ad7d28354d071")
VF_F1_WITH = (f"{D5}/fd/with-vf/readout/vf-with-S/fd_f1_readout.json", "bd36a2aa")
OLD_F1_WITH = (f"{D5}/fd/with-cpl/readout/fd_f1_readout.json", "5ccc89e5")
FETCHED["s1_assembly.npz"] = ("s1-20261024/s1_assembly.npz", "db000707780d4d6d")


def p2_rsn(vf, fetch_dir):
    sys.path.insert(0, str(ROOT / "nd-unfolding/rsn"))
    import rsn_regrade as RG
    import rsn_read as RR
    R = RG.R
    reg_c, hg = pinned_json(RSN_REGRADE)
    read_c, hr = pinned_json(RSN_READOUT)
    for rel_pin in (F1_TABLE, RSN_CMODEL_NPZ, NUE):
        if not sha256_file(ROOT / rel_pin[0]).startswith(rel_pin[1]):
            raise Stop(f"{rel_pin[0]}: not its pinned bytes")
    s1p = fetched(fetch_dir, "s1_assembly.npz")
    TR = RG.truths(RG.F1_PREP_SUMS)
    RG.require(RG.F1_PREP_SUMS, RG.PINS["f1_prep_sums"], "f1_prep_sums")
    with np.load(ROOT / F1_TABLE[0], allow_pickle=False) as z:
        table = {k: z[k] for k in z.files}
    w_all = R.sa.flux_weights(ROOT / NUE[0])
    with np.load(s1p, allow_pickle=False) as z:
        f = np.asarray(z["f"], float)
        Ce, Cstat = np.asarray(z["C_e"], float), np.asarray(z["C_stat"], float)
    with np.load(ROOT / CPL_BLOCK[0], allow_pickle=False) as z:
        Cx = np.asarray(z[RG.EXTRA_KEY], float)
    if not np.array_equal(np.asarray(vf["f"], float), f):
        raise Stop("rsn: the V_F product's f is not S1's")
    ff = np.outer(f, f)
    Ce_rel, Cstat_rel = Ce / ff, Cstat / ff
    S0 = np.asarray(json.loads(RG.CMODEL_JSON.read_text())["S"], float)
    est, ctrl = RG.estimates(TR, table, w_all)
    with np.load(ROOT / RSN_CMODEL_NPZ[0], allow_pickle=False) as z:
        arms = {k[2:]: np.asarray(z[k], float) for k in z.files if k.startswith("S_")}
    cm, _ = pinned_json(RSN_CMODEL_JSON)

    def regrade(Cx_rel, f1):
        out = {name: RG.grade_all(TR, est, ctrl, S, Ce_rel, Cstat_rel, Cx_rel) for name, S in arms.items()}
        RG.reproduce(out["nominal"], ctrl, f1)                       # NC-R
        if "G6" in out:
            RG.invariant_g6(out["nominal"], out["G6"], S0, arms["G6"])  # C-INV
        return {"offset_control_7": ctrl, "arms": out, "wr_directions": RG.wr_directions(cm, Ce_rel, S0, Cx_rel)}

    f1_old, f1_vf = pinned_json(OLD_F1_WITH)[0], pinned_json(VF_F1_WITH)[0]
    old = json.loads(json.dumps(regrade(Cx / ff, f1_old)))
    pf = R.chi2_sf_even                       # the producer's p function (fd_f0_regrade.grade)
    w1 = p_control("rsnregrade", old, {k: reg_c[k] for k in old}, RTOL_EXACT, p_fun=pf)
    new = json.loads(json.dumps(regrade((Cx + np.asarray(vf["matrices"]["DeltaC_e"], float)) / ff, f1_vf)))
    prep, _ = pinned_json(RSN_PREP)
    i0 = json.loads(RR.I0.read_text())
    cmodel = json.loads(RR.CMODEL_JSON.read_text())
    rd_old = json.loads(json.dumps(RR.read(prep, cm, dict(reg_c, **old), i0, cmodel, f1_old)))
    w2 = p_control("rsn", rd_old, read_c, RTOL_EXACT, p_fun=pf)
    f1_alias = json.loads(json.dumps(f1_vf))
    f1_alias[RR.SIGMA_KEY] = f1_alias["relative_sigma_plus_C_resp + C_PL5D + DeltaC_e"]
    rd_new = json.loads(json.dumps(RR.read(prep, cm, dict(reg_c, **new), i0, cmodel, f1_alias)))
    reg_out = dict(json.loads(json.dumps(reg_c)), **new)
    reg_out["vf_patch"] = {"readout": RSN_REGRADE[0], "readout_sha256": hg,
                           "replaced": ["/arms", "/wr_directions", "/offset_control_7"],
                           "matrices": "X_F = C_resp_plus_C_PL5D_plus_DeltaC_e (relative)",
                           "NC-R": "the nominal arm reproduces Phase 1's V_F F1 (" + VF_F1_WITH[0] + ")",
                           "fetched": FETCHED["s1_assembly.npz"][0], "control_P": "PASS",
                           "control_P_tolerance": {"rtol": RTOL_EXACT, "achieved_max": w1,
                                                   "p": {"check": "fd_f0_regrade.chi2_sf_even(committed chi2, ndf) "
                                                         "== committed p, bitwise; printed strings equal (A4 item 3)",
                                                         "achieved_max": P_ACHIEVED.get("rsnregrade", 0.0)}}}
    read_out = dict(rd_new)
    read_out["vf_patch"] = {"readout": RSN_READOUT[0], "readout_sha256": hr, "replaced": ["/"],
                            "inputs": {"regrade": "rsnregrade.vf.json", "f1": VF_F1_WITH[0] + f" (its sigma under "
                                       f"{RR.SIGMA_KEY})"}, "control_P": "PASS",
                            "control_P_tolerance": {"rtol": RTOL_EXACT, "achieved_max": w2,
                                                    "p": {"check": "as rsnregrade's (A4 item 3)",
                                                          "achieved_max": P_ACHIEVED.get("rsn", 0.0)}}}
    return {"rsnregrade": reg_out, "rsn": read_out}


# xk: GENCMP X step K replayed through fd_xcov_steps.cmd_k (route (1); the director's rulings (i)-(iii), 2026-11-26):
# (i) in this process fd_gencmp.read_noatime maps the exact prefix /pscratch/sd/j/josephrb/ to the verified fetch, fails
#     closed, and logs every remapped read; (ii) K runs in a local run directory of hardlinks to the fetched run copy plus
#     the committed V0/V1 records, its file list and shas recorded before and after; (iii) for V_F, read_committed returns
#     the block with C_total_plus_C_resp_plus_C_PL5D := C_rep,F and cr.vf.json for CR_G2R, nothing else differing
XK_K = (f"{D5}/fd/receipts-cov2d/g2r/xk/run/node/run/k/k.json", "204e4c89")
XK_V0 = (f"{D5}/fd/xcov/run/v0-a1/v0.json", None)
XK_V1 = (f"{D5}/fd/xcov/run/v1-a2/v1.json", None)
PS_PREFIX = "/pscratch/sd/j/josephrb/"
XK_ENV_FIELDS = ("inputs", "atime_deviations")    # what records the run's paths and atimes, not a number


def dir_listing(d: Path) -> dict:
    return {str(q.relative_to(d)): sha256_file(q) for q in sorted(d.rglob("*")) if q.is_file()}


def xk_replay(XS, GC, fetch_dir: Path, run_dir: Path, subst: dict, log: list, calls: list):
    """One cmd_k replay under the remap; subst maps a read_committed path to the bytes to return instead."""
    import types
    orig_read, orig_rc = GC.read_noatime, XS.read_committed
    fetch_dir = Path(fetch_dir).resolve()

    def remapped(path):
        s_ = str(path)
        if not s_.startswith(PS_PREFIX):
            return orig_read(path)
        q = (ROOT / LOCAL_COPIES[s_][0]) if s_ in LOCAL_COPIES else fetch_dir / s_[len(PS_PREFIX):]
        if q.is_symlink() or not q.is_file():
            raise Stop(f"xk remap: {s_} -> {q} is missing or not a regular file")
        data = q.read_bytes()
        log.append((s_, len(data), hashlib.sha256(data).hexdigest()))
        return data, True

    def committed(path):
        raw = subst[str(path)] if str(path) in subst else orig_rc(path)
        calls.append((str(path), hashlib.sha256(raw).hexdigest()))
        return raw

    GC.read_noatime, XS.read_committed = remapped, committed
    try:
        rc = XS.cmd_k(types.SimpleNamespace(run_dir=run_dir, products="g2r", own_only=False))
    finally:
        GC.read_noatime, XS.read_committed = orig_read, orig_rc
    return rc


def xk_run_dir(fetch_dir: Path, dest: Path) -> dict:
    """The local run directory: hardlinks to the fetched run copy, plus V0's and V1's committed records."""
    src = Path(fetch_dir) / "cov2d-xk-g2r-20261116/run"
    if dest.exists():
        raise Stop(f"{dest} exists")
    for q in sorted(src.rglob("*")):
        if q.is_file():
            t = dest / q.relative_to(src)
            t.parent.mkdir(parents=True, exist_ok=True)
            os.link(q, t)
    import shutil
    for rel_pin, sub in ((XK_V0, "v0-a1/v0.json"), (XK_V1, "v1-a2/v1.json")):
        (dest / sub).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel_pin[0], dest / sub)
    return dir_listing(dest)


def p2_xk(vf, fetch_dir):
    import os as _os  # noqa: F401
    sys.path.insert(0, str(ROOT / "nd-unfolding"))
    import fd_gencmp as GC
    import fd_xcov_steps as XS
    committed, h = pinned_json(XK_K)
    node = pins(XK / "run/node/NODE-SHA256.txt")
    for rel_pin, key in ((XK_V0, "run/v0-a1/v0.json"), (XK_V1, "run/v1-a2/v1.json")):
        if sha256_file(ROOT / rel_pin[0]) != node[key][0]:
            raise Stop(f"{rel_pin[0]}: not the run copy's {key} ({node[key][1]})")
    work = Path(fetch_dir).resolve().parent / (Path(fetch_dir).name + "-xk")
    rec = {}
    for arm in ("old", "vf"):
        run_dir = work / arm
        before = xk_run_dir(fetch_dir, run_dir)
        subst = {}
        if arm == "vf":
            raw = (ROOT / CPL_BLOCK[0]).read_bytes()
            with np.load(io.BytesIO(raw), allow_pickle=False) as z:
                arrs = {k: np.asarray(z[k]) for k in z.files}
            arrs["C_total_plus_C_resp_plus_C_PL5D"] = np.asarray(vf["matrices"][REPORTED_F], float)
            buf = io.BytesIO()
            np.savez(buf, **arrs)
            subst[str(XS.CPL_BLOCK)] = buf.getvalue()
            subst[str(XS.CR_G2R)] = rec["cr_vf_bytes"]
        log, calls = [], []
        rc = xk_replay(XS, GC, fetch_dir, run_dir, subst, log, calls)
        after = dir_listing(run_dir)
        changed = sorted(k for k in before if after.get(k) != before[k])
        added = sorted(set(after) - set(before))
        # K adds its readout under k/ and its own staging copies under inputs/ (fd_xcov_steps.stage), each of which
        # must be the bytes of a logged remapped read, at its pin
        logged = {Path(p_).name: s_ for p_, _, s_ in log}
        stray = [k for k in added if not (k.startswith("k/") or (k.startswith("inputs/") and k.count("/") == 1
                                                                  and logged.get(k[7:]) == after[k]))]
        if changed or stray or rc != 0:
            raise Stop(f"xk {arm}: rc {rc}; K changed {changed} or added {stray} outside k/ and its staging copies")
        out = json.loads((run_dir / "k/k.json").read_text())
        rec[arm] = {"out": out, "log": log, "calls": calls, "before": before, "added": added,
                    "subst_sha256": {k: hashlib.sha256(v).hexdigest() for k, v in subst.items()}}
        if arm == "old":
            want = {k: v for k, v in committed.items() if k not in XK_ENV_FIELDS}
            got = {k: v for k, v in out.items() if k not in XK_ENV_FIELDS}
            rec["old"]["achieved"] = p_control("xk", got, want, RTOL_EXACT)
            rec["cr_vf_bytes"] = (json.dumps(p2_overlap("cr", CR, vf), indent=1) + "\n").encode()
    lst = {r[0]: (int(r[3]), r[1]) for r in fetch_rows() if "xk" in r[5]}
    lst.update({k: ((ROOT / v[0]).stat().st_size, v[1]) for k, v in LOCAL_COPIES.items()})   # the committed copies
    for arm in ("old", "vf"):
        got = {p_: (n, s_) for p_, n, s_ in rec[arm]["log"]}
        if set(got) - set(lst) or any(got[k] != lst[k] for k in got):
            raise Stop(f"xk {arm}: a remapped read is not a bound fetch-list entry")
    unread = sorted(set(lst) - {p_ for p_, _, _ in rec["old"]["log"]})   # listed for xk, not read by this replay
    # (iii): the two replays differ only in the two substituted read_committed returns
    co, cv = rec["old"]["calls"], rec["vf"]["calls"]
    if [c[0] for c in co] != [c[0] for c in cv]:
        raise Stop("xk: the V_F replay's read_committed call sequence is not the OLD one")
    differ = sorted({a[0] for a, b in zip(co, cv) if a[1] != b[1]})
    if differ != sorted(rec["vf"]["subst_sha256"]):
        raise Stop(f"xk: the replays differ in read_committed returns {differ}, not exactly the two substituted")
    if sorted(rec["old"]["log"]) != sorted(rec["vf"]["log"]):
        raise Stop("xk: the replays' remapped reads differ")
    out = dict(rec["vf"]["out"])
    out["vf_patch"] = {"readout": XK_K[0], "readout_sha256": h, "replaced": ["every field but " + ", ".join(XK_ENV_FIELDS)],
                       "route": "fd_xcov_steps.cmd_k replayed (products g2r), rulings (i)-(iii)",
                       "substituted": rec["vf"]["subst_sha256"],
                       "remapped_reads": len(rec["old"]["log"]), "listed_xk_entries_not_read": unread,
                       "remapped_bytes": sum(n for _, n, _ in rec["old"]["log"]),
                       "run_dir_before": {a: len(rec[a]["before"]) for a in ("old", "vf")},
                       "run_dir_added": {a: rec[a]["added"] for a in ("old", "vf")},
                       "control_P": "PASS",
                       "control_P_tolerance": {"rtol": RTOL_EXACT, "achieved_max": rec["old"]["achieved"],
                                               "excluded": list(XK_ENV_FIELDS)}}
    receipt = {"remapped_reads": rec["old"]["log"], "read_committed_old": co, "read_committed_vf": cv,
               "run_dir_before": rec["old"]["before"]}
    out["vf_patch"]["receipt_sha256"] = hashlib.sha256(json.dumps(receipt, sort_keys=True).encode()).hexdigest()
    return {"xk": out, "xk-receipt": dict(receipt, vf_patch={"readout": "xk replay receipt", "control_P": "PASS",
                                                             "replaced": []})}


RTOL_IBU = 1e-11        # the director's ruling 2 (2026-11-26): route2's truths are recorded equal to (e)'s B0 truths at
                        # <= 1e-12 (C-IBU), not bit-identical; outputs graded against them at 1e-11 (A4)
P2_FETCH = {"prr": p2_prr, "rsn": p2_rsn, "xk": p2_xk}


P2 = {"eav": p2_eav, "e2": p2_e2, "e2sens": p2_e2sens, "vatlas": p2_vatlas, "gch": lambda vf: p2_compare("gch", GCH, vf),
      "gdefs": lambda vf: p2_compare("gdefs", GDEFS, vf, gdefs_extra),
      "gnat": lambda vf: p2_compare("gnat", GNAT, vf), "gover": lambda vf: p2_overlap("gover", GOVER, vf),
      "cr": lambda vf: p2_overlap("cr", CR, vf)}


def cmd_p2(a) -> int:
    vf, vh = pinned_json(VF_DP)
    out = ROOT / P2_OUT if a.out_dir is None else a.out_dir
    if out.exists():
        raise Stop(f"{out} exists (no overwrite)")
    results = {}
    names = a.only or (list(P2) + (list(P2_FETCH) if a.fetch_dir else []))
    for name in names:
        if name in P2_FETCH:
            if not a.fetch_dir:
                raise Stop(f"{name} needs --fetch-dir (the verified fetch)")
            r = P2_FETCH[name](vf, a.fetch_dir)
            results.update(r if "vf_patch" not in r else {name: r})
        else:
            results[name] = P2[name](vf)
    out.mkdir(parents=True)
    for name, r in results.items():
        if "_text" in r:                            # a text receipt keeps its form (e2sens)
            (out / f"{name}.vf.txt").write_text(r["_text"])
            print(f"[p2] {name}: {out / (name + '.vf.txt')}", flush=True)
            continue
        r["vf_patch"]["vf_data_product_sha256"] = vh
        (out / f"{name}.vf.json").write_text(json.dumps(r, indent=1) + "\n")
        print(f"[p2] {name}: {out / (name + '.vf.json')}", flush=True)
    return 0


# ---------------------------------------------------------------- the fetch connect's script and the local check

REMOTE_PY = Path(f"{D5}/fd/receipts-vf/p2/fetch_vfp2_remote.py")
WRAPPER = """#!/bin/bash
# V_F Phase 2 fetch (FD-VF BINDING 2), one login02 session: `ssh saul.nersc.gov "ssh -o BatchMode=yes login02 'bash -s'"
# < fetch-vfp2.sh > vfp2.tar`. The remote reader and the bound list are embedded below as base64 (no here-document, no
# temporary file); each is checked against its sha256 on the node; the reader streams a tar of the listed files to
# stdout through O_NOATIME. Writes nothing on the cluster. Exit 2: refused before any read; 9: a read stopped.
stop() {{ echo "STOP: $*" >&2; exit 2; }}          # a fixed code: nothing inherited can turn a refusal into 0
h=$(hostname) && [ "$h" = login02 ] || stop "not login02 (${{h:-hostname failed}})"
PYB='{py_b64}'
LISTB='{list_b64}'
# each digest is of the raw decoded stream (no command substitution, which would drop trailing newlines or NULs)
s1=$(printf '%s' "$PYB" | base64 -d | sha256sum) && [ "${{s1%% *}}" = {py_sha} ] || stop "reader sha ${{s1%% *}}"
s2=$(printf '%s' "$LISTB" | base64 -d | sha256sum) && [ "${{s2%% *}}" = {list_sha} ] || stop "list sha ${{s2%% *}}"
py=$(printf '%s' "$PYB" | base64 -d) && [ -n "$py" ] || stop "decode reader"
[ -x /usr/bin/python3 ] || stop "no /usr/bin/python3"
echo "fetch start $(date -u +%FT%TZ) on $h; reader {py_sha}; list {list_sha}" >&2
printf '%s' "$LISTB" | base64 -d | /usr/bin/python3 -I -c "$py"
rc=$?
echo "fetch end $(date -u +%FT%TZ) rc=$rc" >&2
exit $rc
"""


def cmd_fetch_script(a) -> int:
    """Writes the wrapper with the remote reader and the list embedded; prints its sha256."""
    import base64
    py = (ROOT / REMOTE_PY).read_bytes().decode()
    lst = a.list.read_bytes().decode()          # raw bytes: no newline translation (a CRLF list must refuse)
    for t in (py, lst):
        if not t.endswith("\n") or t.endswith("\n\n"):
            raise Stop("an embedded text must end with exactly one newline (the wrapper re-adds it)")
    expect = "\t".join(HEADER) + "\n" + "".join("\t".join(r) + "\n" for r in fetch_rows())
    if lst != expect:
        raise Stop("the list is not fetch-list's output, byte for byte")
    text = WRAPPER.format(py_b64=base64.b64encode(py.encode()).decode(), py_sha=hashlib.sha256(py.encode()).hexdigest(),
                          list_b64=base64.b64encode(lst.encode()).decode(),
                          list_sha=hashlib.sha256(lst.encode()).hexdigest())
    if a.out.exists():
        raise Stop(f"{a.out} exists")
    a.out.write_text(text)
    print(f"wrapper {a.out}: sha256 {hashlib.sha256(text.encode()).hexdigest()}; reader "
          f"{hashlib.sha256(py.encode()).hexdigest()}; list {hashlib.sha256(lst.encode()).hexdigest()}", file=sys.stderr)
    return 0


PAX_KEYS = {b"path", b"mtime", b"size"}       # the only keys the reader's tarfile.PAX_FORMAT stream can carry


def pax_records(data: bytes, name: str) -> None:
    """A PAX extension's data must be exactly a sequence of "<len> <key>=<value>\n" records covering every byte, and
    hold a path record (the only reason the reader writes one)."""
    if not data:
        raise Stop(f"tar member {name!r}: an empty PAX extension")
    keys = set()
    i = 0
    while i < len(data):
        sp = data.find(b" ", i)
        if sp < 0 or not data[i:sp].isdigit():
            raise Stop(f"tar member {name!r}: a malformed PAX record length")
        n = int(data[i:sp])
        rec = data[i:i + n]
        if n <= sp - i + 1 or len(rec) != n or not rec.endswith(b"\n") or b"\0" in rec:
            raise Stop(f"tar member {name!r}: a malformed PAX record")
        key, eq, value = rec[sp - i + 1:-1].partition(b"=")
        if not eq or key not in PAX_KEYS or (key == b"path" and not value):
            raise Stop(f"tar member {name!r}: a PAX record with key {key!r} (only {sorted(PAX_KEYS)})")
        keys.add(key)
        i += n
    if b"path" not in keys:
        raise Stop(f"tar member {name!r}: a PAX extension without a path record")


def cmd_fetch_verify(a) -> int:
    """Extracts the fetched tar into a new directory, refusing any member not in the list, a link, an absolute or ..
    path, a size or a sha256 that is not the list's, or a listed file that is missing."""
    import tarfile
    expect = "\t".join(HEADER) + "\n" + "".join("\t".join(r) + "\n" for r in fetch_rows())
    if a.list.read_bytes() != expect.encode():
        raise Stop("the list is not fetch-list's output, byte for byte")
    rows = [r.split("\t") for r in expect.split("\n")[1:] if r]
    want = {r[0][len(PS):]: (r[1], int(r[3])) for r in rows}
    if a.dest.exists():
        raise Stop(f"{a.dest} exists")
    raw = Path(a.tar).read_bytes()
    a.dest.mkdir(parents=True)
    seen, end = set(), 0

    def zero(a_, b_, what):
        if raw[a_:b_].count(0) != b_ - a_:
            raise Stop(f"tar: nonzero padding {what}")
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as tf:
        for m in tf:
            # the whole layout: each member starts where the previous one ended (tarfile's offset is the first header
            # of the member, a PAX extension's if it has one); a PAX extension is one 'x' header, its data and zero
            # padding, ending exactly at the file's own header
            if m.offset != end:
                raise Stop(f"tar member {m.name!r}: unexpected bytes before it")
            if m.offset_data - 512 != m.offset:
                h = tarfile.TarInfo.frombuf(raw[m.offset:m.offset + 512], tarfile.ENCODING, "surrogateescape")
                pend = m.offset + 512 + -(-h.size // 512) * 512
                if h.type != tarfile.XHDTYPE or h.size <= 0 or pend != m.offset_data - 512:
                    raise Stop(f"tar member {m.name!r}: its extension is not one PAX record")
                pax_records(raw[m.offset + 512:m.offset + 512 + h.size], m.name)
                zero(m.offset + 512 + h.size, pend, f"after the PAX extension of {m.name!r}")
            end = m.offset_data + -(-m.size // 512) * 512
            zero(m.offset_data + m.size, end, f"after the data of {m.name!r}")
            n = m.name
            if not m.isfile() or n.startswith("/") or ".." in n.split("/") or n not in want or n in seen:
                raise Stop(f"tar member {n!r}: not a listed regular file, or repeated")
            data = tf.extractfile(m).read()
            sha, size = want[n]
            if len(data) != size or hashlib.sha256(data).hexdigest() != sha:
                raise Stop(f"{n}: size {len(data)} sha256 {hashlib.sha256(data).hexdigest()[:16]}, listed {size} {sha[:16]}")
            q = a.dest / n
            q.parent.mkdir(parents=True, exist_ok=True)
            q.write_bytes(data)
            seen.add(n)
    if seen != set(want):
        raise Stop(f"{len(set(want) - seen)} listed files missing from the tar")
    tail = raw[end:]       # the archive must end in at least two zero blocks and hold nothing after its members
    if len(tail) < 1024 or tail.count(0) != len(tail):
        raise Stop(f"the tar does not end cleanly after its last member ({len(tail)} trailing bytes, not all zero)")
    print(f"fetch-verify: {len(seen)} files, each the list's size and sha256, under {a.dest}", file=sys.stderr)
    return 0


def build_args(argv=None):
    ap = argparse.ArgumentParser(prog="fd_vf_p2.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch-list")
    f.add_argument("--out", type=Path)
    w = sub.add_parser("fetch-script")
    w.add_argument("--list", type=Path, required=True)
    w.add_argument("--out", type=Path, required=True)
    v = sub.add_parser("fetch-verify")
    v.add_argument("--tar", type=Path, required=True)
    v.add_argument("--list", type=Path, required=True)
    v.add_argument("--dest", type=Path, required=True)
    q = sub.add_parser("p2")
    q.add_argument("--out-dir", type=Path)
    q.add_argument("--only", nargs="+", choices=sorted(P2) + ["prr", "rsn", "xk"])
    q.add_argument("--fetch-dir", type=Path, help="the verified fetch (fetch-verify's --dest)")
    return ap.parse_args(argv)


def main(argv=None) -> int:
    a = build_args(argv)
    return {"fetch-list": cmd_fetch_list, "fetch-script": cmd_fetch_script, "fetch-verify": cmd_fetch_verify,
            "p2": cmd_p2}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
