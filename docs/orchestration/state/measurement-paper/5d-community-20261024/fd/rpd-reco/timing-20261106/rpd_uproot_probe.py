"""Follow-up to rpd_probe.py (4cdda635), whose class test (startswith "MnvH1D") skipped "PlotUtils::MnvH1D": does uproot
read a MAT PlotUtils::MnvH1D (the flux files' class) at all, or only its TH1D base? On the same staged non-input copy.
    python3 -I -B rpd_uproot_probe.py DIR    Prints one JSON record."""
import json, os, sys
from pathlib import Path
D = Path(sys.argv[1]); sys.path.insert(0, str(D))
import numpy as np, uproot  # noqa: E401,E402
import fd_rpd_reco as R  # noqa: E402  (10731ed3, imported, never run)
out = {"interpreter": sys.executable, "resolved_interpreter": os.path.realpath(sys.executable),
       "python": sys.version.split()[0], "numpy": np.__version__, "uproot": uproot.__version__, "files": {}}
for n in sorted(os.listdir(D)):
    if not n.endswith(".root") or n.startswith("."):
        continue
    rec = {}
    with uproot.open(D / n) as f:
        for key, cls in sorted(f.classnames().items()):
            if "TH1" not in cls and "MnvH1D" not in cls:
                continue
            e = {"class": cls}
            try:
                obj = f[key]
                e["uproot_type"] = type(obj).__name__
                e["mro"] = [c.__name__ for c in type(obj).__mro__][:8]
                e["bases"] = [type(b).__name__ for b in getattr(obj, "bases", [])]
                e["own_members"] = sorted(getattr(obj, "_members", {}).keys())
                e["all_members_sample"] = sorted(obj.all_members.keys())[:60]
                values, edges = obj.to_numpy(flow=False)
                e.update(to_numpy=True, n_bins=int(values.size), edges=edges.tolist(), values=values.tolist())
            except Exception as ex:
                e.update(to_numpy=False, error=f"{type(ex).__name__}: {ex}"[:500])
            try:
                r = R.read_flux_histogram(D / n, key.split(";")[0])
                e["fd_rpd_reco_read_flux_histogram"] = {"ok": True, "n_bins": len(r["values"]), "integral": r["integral"]}
            except Exception as ex:
                e["fd_rpd_reco_read_flux_histogram"] = {"ok": False, "error": f"{type(ex).__name__}: {ex}"[:300]}
            rec[key] = e
    out["files"][n] = rec
print(json.dumps(out, default=float))
