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


P2 = {"eav": p2_eav, "e2": p2_e2, "gover": lambda vf: p2_overlap("gover", GOVER, vf),
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


def build_args(argv=None):
    ap = argparse.ArgumentParser(prog="fd_vf_p2.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch-list")
    f.add_argument("--out", type=Path)
    q = sub.add_parser("p2")
    q.add_argument("--out-dir", type=Path)
    q.add_argument("--only", nargs="+", choices=sorted(P2))
    return ap.parse_args(argv)


def main(argv=None) -> int:
    a = build_args(argv)
    return {"fetch-list": cmd_fetch_list, "p2": cmd_p2}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
