B=/pscratch/sd/j/josephrb/fd-1b-20261030; D=$B/deploy/stage2
echo "host=$(hostname) now=$(date -u +%Y-%m-%dT%H:%M:%SZ) deploy_head=$(git -C $D rev-parse HEAD)"
env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I - > $B/score/pilot-walls-pregate.json <<'PY'
import json, statistics, sys
sys.path.insert(0, "/pscratch/sd/j/josephrb/fd-1b-20261030/deploy/stage2/nd-unfolding")
import numpy as np
import fd_1b_tasks as ft
rows, missing = [], []
for job in ("2a-0", "2a"):
    for arm, mode, x in ft.expand(job):
        p = ft.product_path(arm, mode, x)
        if not p.exists():
            missing.append(p.name); continue
        m = json.loads(str(np.load(p, allow_pickle=False)["meta"]))
        rows.append({"job": job, "product": p.name, "arm": arm, "mode": mode, "seconds_load": m["seconds_load"],
                     "seconds_unfold": m["seconds_unfold"], "peak_rss_kib": m["peak_rss_kib"], "numpy": m.get("numpy_version")})
pilot = sorted(r["seconds_unfold"] for r in rows if (r["arm"], r["mode"]) == ("pilot", "toy"))
out = {"label": "DERIVATION, pre-gate readout (not walls --after 2a)", "present": len(rows), "missing": missing,
       "pilot_n": len(pilot), "pilot_median_seconds_unfold": statistics.median(pilot), "pilot_min": pilot[0], "pilot_max": pilot[-1],
       "pilot_limit_s": 1.25 * ft.TOY_UNIT_S, "largest_peak_rss_kib": max(r["peak_rss_kib"] for r in rows),
       "rss_limit_kib": ft.RSS_LIMIT_KIB, "numpy_versions": sorted({r["numpy"] for r in rows}),
       "derivation_seconds_unfold": [min(r["seconds_unfold"] for r in rows if r["mode"] == "derivation"),
                                     statistics.median(r["seconds_unfold"] for r in rows if r["mode"] == "derivation"),
                                     max(r["seconds_unfold"] for r in rows if r["mode"] == "derivation")],
       "half_seconds_unfold": [r["seconds_unfold"] for r in rows if (r["arm"], r["mode"]) == ("pilot", "half")],
       "products": rows}
print(json.dumps(out, indent=1))
PY
echo "rc=$?"
env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I -c "import json; d=json.load(open('$B/score/pilot-walls-pregate.json')); d.pop('products'); print(json.dumps(d))"
