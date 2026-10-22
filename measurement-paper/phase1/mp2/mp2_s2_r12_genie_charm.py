"""R12 readout (binding addendum 14 §4, 0 node-h): the GENIE CV and MEC gst `charm` flag's share of the in-grid rate.
Entries in harmonize's order (main gst, then the 50-100 GeV supplement); events_<G>.npz carries j into that order."""
import hashlib, json, sys
import numpy as np, uproot
D = "/pscratch/sd/j/josephrb/measurement-paper/phase1/mp2/s2"
G = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/3d-unfolding/genie"
S5P = "/pscratch/sd/j/josephrb/s5p-20260926"
FILES = {"genie_cv": [f"{G}/genie_mefhc_cv_ALL.gst.root", f"{S5P}/gen5d_fluxfix/supp/genie_cv/genie_supp_cv.gst.root"],
         "genie_mec": [f"{G}/genie_mefhc_mec_ALL.gst.root", f"{S5P}/gen5d_fluxfix/supp/genie_mec/genie_supp_mec.gst.root"]}
def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
rec = json.load(open(f"{D}/harm_a/s2_harmonize.json"))
out = {"schema": "mp2-s2-r12-genie-charm/1", "rule": "addendum 14 §4: GENIE gst `charm` flag, share of the in-grid harmonized rate (sum c)", "generators": {}}
for g, fl in FILES.items():
    ev_p = f"{D}/harm_a/events_{g}.npz"
    if sha256(ev_p) != rec["outputs"][f"events_{g}.npz"]:
        raise SystemExit(f"{ev_p} differs from harmonize's record")
    flags, sizes, cc = [], [], []
    for f in fl:
        t = uproot.open(f)["gst"]
        a = t.arrays(["charm", "cc"], library="np")
        flags.append(a["charm"].astype(bool)); cc.append(a["cc"].astype(bool)); sizes.append(t.num_entries)
    ch, ccv = np.concatenate(flags), np.concatenate(cc)
    ev = np.load(ev_p)
    j, c, tgt = ev["j"], ev["c"], ev["tgt"]
    if j.max() >= ch.size:
        raise SystemExit(f"{g}: j beyond the entries")
    m = ch[j]
    out["generators"][g] = {"files": {f: {"sha256": sha256(f), "entries": n} for f, n in zip(fl, sizes)},
                            "events_npz": {"path": ev_p, "sha256": rec["outputs"][f"events_{g}.npz"]},
                            "n_entries": int(ch.size), "n_charm_entries": int(ch.sum()), "n_charm_cc": int((ch & ccv).sum()),
                            "n_in_grid": int(j.size), "n_in_grid_charm": int(m.sum()),
                            "in_grid_rate_share_charm": float(c[m].sum() / c.sum()),
                            "in_grid_rate_share_charm_excl_tgt0": float(c[m & (tgt != 0)].sum() / c[tgt != 0].sum())}
print(json.dumps(out["generators"], indent=1))
open(f"{D}/r12_genie_charm.json", "w").write(json.dumps(out, indent=1) + "\n")
