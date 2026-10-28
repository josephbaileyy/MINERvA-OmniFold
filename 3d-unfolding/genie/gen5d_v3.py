#!/usr/bin/env python3
"""F1's GENIE v3 truth predictions (state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION.md section 2):
the gen5d/v1 5D density of one GENIE v3 tune, from events generated on phi_t directly.

  make-flux  --phi-t-dir D --out F.root   flux_numu with content = phi_t density x bin width on every phi_t bin
                                          (0-100 GeV). TH1::GetRandom picks a bin by content and E uniformly inside
                                          it, so gevgen -e 0,100 -f F,flux_numu,NOWIDTH samples phi_t exactly. The
                                          ",NOWIDTH" is required: GENIE v3.04.00's gEvGen.cxx multiplies every bin of
                                          a variable-width histogram by its width otherwise (v2.12.10c, which the
                                          50-100 GeV supplement used, does not). Refuses to overwrite.
             Controls (the director's flux ruling): phi_t.npz is the pinned file and phi_t.json's own record of it;
             phi_t is the nu-e-constrained CV flux the data normalisation uses (phi_t.json's definition names the
             constrainer); and the file's integral, sum of its contents, equals the data normalisation's hFluxCV
             (baseline_flux/flux_integral_universes_MEFHC.root, pinned, bin 1) to 1e-12 relative.
  flux-check --flux F --work W [W ...]
             each gevgen work directory's input-flux.root histogram "spectrum", the one gevgen actually samples, must
             equal F's contents and edges bit for bit (the NOWIDTH control).
  spline-check --tune T --source S --reduced R --readme M --out J.json
             the reduced spline file's own header must name the tune (<genie_tune name=...>) and the spline-list
             format; its C12 and H1 splines must be exactly the source's; the source and README must be the pinned
             files, and the README's version line the pinned line (G18_10a_02_11b's says v3_02_00, AR23_20i_00_000's
             v3_04_00).
  convert    --tune T --gst G --graphs X --flux F --out O.npz
             the events through gen_to_xsec5d.py's GENIE extraction and genie_cv binning, unchanged (imported), and
             the strict sampling test of gen5d_flux_reweight.py (imported): the CC events' E_nu must follow
             phi_t x sigma_CC of the tune's own splines (X, gspl2root of the same reduced file). Exit 1, nothing
             written, if the test fails, an axis has a non-finite value, or the reader parity has a mismatch.

Normalisation: genie_to_xsec3d.py's sigma_CC/13 x N_bin / N_CC (gen_to_xsec5d's genie_cv convention). F1 uses the
prediction only through pvl_ratios.py's gated shape ratio, which is k-normalised, so any global factor cancels.

MEASURES: one generator's 5D prediction. CANNOT AUTHORIZE: anything.
"""
import argparse
import array
import datetime
import json
import os
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

TUNES = {"G18_10a_02_11b": "GENIE v3.04.00 G18_10a_02_11b (genie_xsec v3_04_00 G1810a0211b-k250-e1000, whose README "
                            "says the splines were made by v3_02_00)",
         "AR23_20i_00_000": "GENIE v3.04.00 AR23_20i_00_000 (genie_xsec v3_04_00 AR2320i00000-k250-e1000)"}
# (gxspl-NUsmall.xml sha256, README sha256, the README's version line), measured on login25 2026-10-27
SPLINE_PINS = {
    "G18_10a_02_11b": ("1b4b0b37fc8c11acbf00884a94d0a3bda519d9c458f2c916573ef3d673a3ee35",
                       "abfca258817a3f7d8169cdd2dbf9349a025ab38312435c718347598b53f16726",
                       "version v3_02_00 qualifier G1810a0211b:k250:e1000"),
    "AR23_20i_00_000": ("185d7d8a4674b5df445fcadea3d17232804390c8421d563aa402c6ee743a0bbb",
                        "744cba18f82cc5fe4805cd8be120e5f7e5f7b36f657f4cc9f2118e69c803bcb2",
                        "version v3_04_00 qualifier AR2320i00000:k250:e1000")}
E_LO, E_HI = 0.0, 100.0
PHI_T_SHA256 = "bbcbade310d90e1ae487dde9d982e85cfe16fae35bba09dbde7db2dc99274ec5"   # gen5d_fluxfix/phi_t.npz
HFLUXCV = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root"
HFLUXCV_SHA256 = "5eecae84509ba8ededbe8fdee63508d8e36cd057cc0547a940383f80248580eb"
INTEGRAL_TOL = 1e-12


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def flux_contents(edges, phi_t):
    """content_i = phi_t_i x w_i on every bin (phi_t covers 0-100 GeV)."""
    edges, phi_t = np.asarray(edges, float), np.asarray(phi_t, float)
    if edges.size != phi_t.size + 1 or edges[0] != E_LO or edges[-1] != E_HI or np.any(np.diff(edges) <= 0):
        raise SystemExit(f"phi_t's edges do not span [{E_LO}, {E_HI}] in increasing bins")
    return phi_t * np.diff(edges)


def check_phi_t(sha: str, meta: dict) -> None:
    """The flux ruling's first two controls: the pinned phi_t, defined as the nu-e-constrained CV flux."""
    if sha != PHI_T_SHA256 or meta.get("schema") != "gen5d-fluxfix-phi-t/v1" or meta.get("npz_sha256") != sha:
        raise SystemExit(f"not the pinned phi_t (sha256 {PHI_T_SHA256}) with its own record")
    if "nuE constraint true" not in meta.get("definition", ""):
        raise SystemExit("phi_t.json does not define phi_t as the nu-e-constrained CV flux")


def check_integral(contents, hcv: float) -> float:
    rel = abs(float(np.sum(contents)) - hcv) / hcv
    if not rel <= INTEGRAL_TOL:
        raise SystemExit(f"the flux integral differs from hFluxCV by {rel:.3e} relative")
    return rel


def same_spectrum(edges, contents, e2, c2) -> bool:
    return bool(np.array_equal(np.asarray(edges, float), np.asarray(e2, float))
                and np.array_equal(np.asarray(contents, float), np.asarray(c2, float)))


def cmd_flux_check(a):
    import gen5d_flux_reweight as gfr
    ROOT = gfr.import_root()
    edges, c = gfr.read_th1(ROOT, a.flux, "flux_numu")
    bad = []
    for w in a.work:
        p = os.path.join(w, "input-flux.root")
        if not os.path.exists(p):
            bad.append(f"{p}: missing")
            continue
        e2, c2 = gfr.read_th1(ROOT, p, "spectrum")
        if not same_spectrum(edges, c, e2, c2):
            bad.append(f"{p}: the sampled spectrum is not the flux file's contents")
    print(json.dumps({"checked": len(a.work), "refused": bad}))
    return 1 if bad else 0


def cmd_make_flux(a):
    import gen5d_flux_reweight as gfr
    if os.path.exists(a.out):
        raise SystemExit(f"refusing to overwrite {a.out}")
    z, meta, p = gfr.load_phi_t(a.phi_t_dir)
    check_phi_t(gfr.sha256(p), meta)
    if gfr.sha256(a.hfluxcv) != HFLUXCV_SHA256:
        raise SystemExit(f"{a.hfluxcv} is not the pinned hFluxCV file")
    edges = np.asarray(z["edges"], float)
    c = flux_contents(edges, z["phi_t_density"])
    ROOT = gfr.import_root()
    fh = ROOT.TFile.Open(a.hfluxcv)
    h = fh.Get("hFluxCV") if fh else None
    if not h:
        raise SystemExit(f"no hFluxCV in {a.hfluxcv}")
    hcv = float(h.GetBinContent(1))
    fh.Close()
    rel = check_integral(c, hcv)
    f = ROOT.TFile.Open(a.out, "RECREATE")
    h = ROOT.TH1D("flux_numu", "phi_t x width on [0,100] GeV;E_{#nu} (GeV);per-bin flux", c.size,
                  array.array("d", edges))
    for i, v in enumerate(c, start=1):
        h.SetBinContent(i, float(v))
    h.SetDirectory(f)
    h.Write()
    f.Close()
    e2, c2 = gfr.read_th1(ROOT, a.out, "flux_numu")
    if not (np.array_equal(e2, edges) and np.array_equal(c2, c)):
        raise SystemExit("the written flux does not read back as phi_t x width")
    gfr.dump_json({"created_utc": now(), "file": gfr.file_record(a.out, "F1 flux (content = phi_t x width, 0-100 GeV)"),
                   "definition": "content_i = phi_t_i * w_i on every phi_t bin", "phi_t_npz": gfr.file_record(p, "phi_t"),
                   "control": {"hFluxCV": gfr.file_record(a.hfluxcv, "the data normalisation's flux integral"),
                               "hFluxCV_bin1": hcv, "sum_contents": float(c.sum()), "rel_diff": rel,
                               "tolerance": INTEGRAL_TOL, "phi_t_definition": meta["definition"]},
                   "code": {"path": str(Path(__file__).resolve()), "sha256": gfr.sha256(Path(__file__).resolve())}},
                  os.path.splitext(a.out)[0] + ".json")
    print(a.out)
    return 0


def spline_header(text: str) -> dict:
    """The tune and format a GENIE spline XML names in its own header, and its C12 and H1 spline names."""
    import re
    tune = re.search(r'<genie_tune name="([^"]+)">', text)
    fmt = re.search(r'<genie_xsec_spline_list version="([^"]+)"', text)
    names = re.findall(r'<spline name="([^"]+)"', text)
    keep = sorted(n for n in names if "tgt:1000060120;" in n or "tgt:1000010010;" in n)
    return {"tune": tune.group(1) if tune else None, "format": fmt.group(1) if fmt else None, "ch_splines": keep,
            "n_splines": len(names)}


def cmd_spline_check(a):
    import gzip
    import hashlib
    src = Path(a.source).read_text(errors="replace")
    red = gzip.decompress(Path(a.reduced).read_bytes()).decode(errors="replace")
    hs, hr = spline_header(src), spline_header(red)
    version = [ln.strip() for ln in Path(a.readme).read_text().splitlines() if ln.strip().startswith("version ")]
    bad = []
    if hr["tune"] != a.tune or hs["tune"] != a.tune:
        bad.append(f"header tunes {hs['tune']} / {hr['tune']}, not {a.tune}")
    if hr["format"] != hs["format"] or hr["format"] is None:
        bad.append(f"spline-list formats {hs['format']} / {hr['format']}")
    if hr["ch_splines"] != hs["ch_splines"] or hr["n_splines"] != len(hr["ch_splines"]) or not hr["ch_splines"]:
        bad.append("the reduced file's splines are not exactly the source's C12 and H1 splines")
    if len(version) != 1:
        bad.append(f"the README has {len(version)} version lines")
    pin = SPLINE_PINS[a.tune]
    if len(version) == 1 and version[0] != pin[2]:
        bad.append(f"the README's version line {version[0]!r} is not the pinned {pin[2]!r}")
    if hashlib.sha256(Path(a.source).read_bytes()).hexdigest() != pin[0]:
        bad.append("the source spline file is not the pinned one")
    if hashlib.sha256(Path(a.readme).read_bytes()).hexdigest() != pin[1]:
        bad.append("the README is not the pinned one")
    rec = {"tune": a.tune, "source": {"path": a.source, "sha256": hashlib.sha256(Path(a.source).read_bytes()).hexdigest()},
           "reduced": {"path": a.reduced, "sha256": hashlib.sha256(Path(a.reduced).read_bytes()).hexdigest()},
           "header": {k: hr[k] for k in ("tune", "format", "n_splines")}, "n_ch_splines_source": len(hs["ch_splines"]),
           "readme_version_line": version[0] if len(version) == 1 else version,
           "note": "the spline XML names its tune and format only, not a GENIE version; the README line is the "
                   "product's own statement of the version that made the splines", "refused": bad}
    Path(a.out).write_text(json.dumps(rec, indent=1) + "\n")
    print(json.dumps({k: rec[k] for k in ("tune", "header", "readme_version_line", "refused")}))
    return 1 if bad else 0


def problems(rng, diag, sampling):
    bad = [f"{ax}: {r['n_nonfinite']} non-finite" for ax, r in rng.items() if r["n_nonfinite"]]
    if diag["reader_parity"]["n_mismatch"] or not diag["reader_parity"]["n_checked"]:
        bad.append(f"reader parity {diag['reader_parity']}")
    if not sampling["pass"]:
        bad.append("the strict sampling test failed")
    return bad


def cmd_convert(a):
    import gen5d_flux_reweight as gfr
    import gen_to_xsec5d as g5
    if os.path.exists(a.out):
        raise SystemExit(f"refusing to overwrite {a.out}")
    ROOT = gfr.import_root()
    ev, norm, diag = g5.extract_genie(a.gst, False, a.graphs, a.flux, "flux_numu", a.parity_n)
    x5, v5, nevt5, _, _, _ = g5.build("genie_cv", ev, norm)
    d = ROOT.RDataFrame("gst", a.gst).AsNumpy(["cc", "Ev"])
    E_cc = np.asarray(d["Ev"], float)[np.asarray(d["cc"]).astype(bool)]
    edges, contents = gfr.read_th1(ROOT, a.flux, "flux_numu")
    sampling = gfr.sampling_test(E_cc, edges, contents, E_LO, E_HI, gfr.SigmaCC(ROOT, a.graphs, "CH"), True,
                                 f"{a.tune}: CC events")
    rng = {ax: {"n_nonfinite": int((~np.isfinite(ev[ax])).sum()), "n_below": int((ev[ax] < g5.EDGES[ax][0]).sum()),
                "n_above": int((ev[ax] > g5.EDGES[ax][-1]).sum()),
                "min": float(np.nanmin(ev[ax])), "max": float(np.nanmax(ev[ax]))} for ax in g5.AXES}
    bad = problems(rng, diag, sampling)
    if bad:
        print(json.dumps({"refused": bad, "sampling": {k: sampling[k] for k in ("pass", "n_events", "n_outside_generation_bins")}}))
        return 1
    code = [Path(__file__).resolve(), Path(g5.__file__).resolve(), Path(gfr.__file__).resolve()]
    meta = {
        "schema": "gen5d/v1", "created_utc": now(), "generator": f"genie_v3_{a.tune}", "generator_label": TUNES[a.tune],
        "quantity": "d5sigma/(dpT dp|| dEavail dq3 dW), cm^2/nucleon/(GeV/c)^2/GeV^3",
        "axes": list(g5.AXES), "shape": list(g5.SHAPE), "order": "C", "edges": {x: g5.EDGES[x].tolist() for x in g5.AXES},
        "phase_space": "as gen_to_xsec5d.py (truth muon pT in [0,4.5], p|| in [1.5,60], theta_mu < 20 deg, CC)",
        "flux": "phi_t sampled directly on 0-100 GeV (gen5d_v3.py make-flux); no flux reweight",
        "normalisation": dict(norm, use="F1 reads this prediction only through a k-normalised shape ratio; a global "
                                        "factor cancels"),
        "range_accounting": rng, "n_in_phase_space": int(ev["pt"].size), "n_events_in_grid": int(nevt5.sum()),
        "diagnostics": diag, "sampling_test": sampling,
        "inputs": [gfr.file_record(a.gst, "events"), gfr.file_record(a.graphs, "sigma_CC graphs (gspl2root)"),
                   gfr.file_record(a.flux, "flux (phi_t x width)")],
        "code": {"files": [{"path": str(p), "sha256": gfr.sha256(p)} for p in code]},
        "environment": gfr.environment(), "argv": sys.argv,
    }
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    np.savez(a.out, xsec_flat=x5.reshape(-1), sumw2_flat=v5.reshape(-1), nevt_flat=nevt5.reshape(-1),
             n_events=np.int64(nevt5.sum()), **{f"edges_{x}": g5.EDGES[x] for x in g5.AXES},
             shape=np.asarray(g5.SHAPE), meta_json=np.asarray(json.dumps(meta, default=str)))
    gfr.dump_json(meta, os.path.splitext(a.out)[0] + ".meta.json")
    print(json.dumps({"wrote": a.out, "sha256": gfr.sha256(a.out), "n_in_grid": int(nevt5.sum()),
                      "f_MEC": norm["f_MEC"], "sampling_p": sampling["across_bins_content_proportional"]["p"]}))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make-flux")
    m.add_argument("--phi-t-dir", required=True)
    m.add_argument("--out", required=True)
    m.add_argument("--hfluxcv", default=HFLUXCV)
    fc = sub.add_parser("flux-check")
    fc.add_argument("--flux", required=True)
    fc.add_argument("--work", nargs="+", required=True)
    k = sub.add_parser("spline-check")
    k.add_argument("--tune", required=True, choices=sorted(TUNES))
    for x in ("source", "reduced", "readme", "out"):
        k.add_argument(f"--{x}", required=True)
    c = sub.add_parser("convert")
    c.add_argument("--tune", required=True, choices=sorted(TUNES))
    for k in ("gst", "graphs", "flux", "out"):
        c.add_argument(f"--{k}", required=True)
    c.add_argument("--parity-n", type=int, default=20000)
    a = ap.parse_args(argv)
    return {"make-flux": cmd_make_flux, "flux-check": cmd_flux_check, "spline-check": cmd_spline_check,
            "convert": cmd_convert}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
