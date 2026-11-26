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
N_ROWS, N_BYTES = 403, 1595650936                                        # the mapped list (codex-school, 2026-11-26)
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


def p_control(name, reproduced, committed, rtol=0.0, scale=None):
    """P (section 6): the producer's arithmetic on the OLD matrix reproduces every field it will replace. rtol = 0 is
    exact equality (bit-identical inputs); otherwise each float must satisfy |a - b| <= rtol * scale(path, b), where
    scale defaults to |b|. Returns the largest achieved relative difference."""
    worst = [0.0, ""]

    def walk(a, b, path):
        if isinstance(b, dict):
            if not isinstance(a, dict) or set(a) != set(b):
                raise Stop(f"P {name}: {path} keys differ")
            for k in b:
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
    return out


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
    for name in (a.only or list(P2)):
        results[name] = P2[name](vf)
    out.mkdir(parents=True)
    for name, r in results.items():
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
stop() {{ echo "STOP: $*" >&2; exit "${{STOP_RC:-2}}"; }}
h=$(hostname) && [ "$h" = login02 ] || stop "not login02 (${{h:-hostname failed}})"
PYB='{py_b64}'
LISTB='{list_b64}'
py=$(printf '%s' "$PYB" | base64 -d) && [ -n "$py" ] || stop "decode reader"
list=$(printf '%s' "$LISTB" | base64 -d) && [ -n "$list" ] || stop "decode list"
s1=$(printf '%s\n' "$py" | sha256sum) && [ "${{s1%% *}}" = {py_sha} ] || stop "reader sha ${{s1%% *}}"
s2=$(printf '%s\n' "$list" | sha256sum) && [ "${{s2%% *}}" = {list_sha} ] || stop "list sha ${{s2%% *}}"
[ -x /usr/bin/python3 ] || stop "no /usr/bin/python3"
echo "fetch start $(date -u +%FT%TZ) on $h; reader {py_sha}; list {list_sha}" >&2
printf '%s\n' "$list" | /usr/bin/python3 -I -c "$py"
rc=$?
echo "fetch end $(date -u +%FT%TZ) rc=$rc" >&2
exit $rc
"""


def cmd_fetch_script(a) -> int:
    """Writes the wrapper with the remote reader and the list embedded; prints its sha256."""
    import base64
    py = (ROOT / REMOTE_PY).read_text()
    lst = a.list.read_text()
    for t in (py, lst):
        if not t.endswith("\n") or t.endswith("\n\n"):
            raise Stop("an embedded text must end with exactly one newline (the wrapper re-adds it)")
    rows = lst.splitlines()
    if rows[0] != "\t".join(HEADER) or len(rows) - 1 != N_ROWS:
        raise Stop("the list is not fetch-list's")
    text = WRAPPER.format(py_b64=base64.b64encode(py.encode()).decode(), py_sha=hashlib.sha256(py.encode()).hexdigest(),
                          list_b64=base64.b64encode(lst.encode()).decode(),
                          list_sha=hashlib.sha256(lst.encode()).hexdigest())
    if a.out.exists():
        raise Stop(f"{a.out} exists")
    a.out.write_text(text)
    print(f"wrapper {a.out}: sha256 {hashlib.sha256(text.encode()).hexdigest()}; reader "
          f"{hashlib.sha256(py.encode()).hexdigest()}; list {hashlib.sha256(lst.encode()).hexdigest()}", file=sys.stderr)
    return 0


def cmd_fetch_verify(a) -> int:
    """Extracts the fetched tar into a new directory, refusing any member not in the list, a link, an absolute or ..
    path, a size or a sha256 that is not the list's, or a listed file that is missing."""
    import tarfile
    rows = [r.split("\t") for r in a.list.read_text().splitlines()[1:]]
    want = {r[0][len(PS):]: (r[1], int(r[3])) for r in rows}
    if a.dest.exists():
        raise Stop(f"{a.dest} exists")
    a.dest.mkdir(parents=True)
    seen = set()
    with tarfile.open(a.tar, mode="r|") as tf:
        for m in tf:
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
    q.add_argument("--only", nargs="+", choices=sorted(P2))
    return ap.parse_args(argv)


def main(argv=None) -> int:
    a = build_args(argv)
    return {"fetch-list": cmd_fetch_list, "fetch-script": cmd_fetch_script, "fetch-verify": cmd_fetch_verify,
            "p2": cmd_p2}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
