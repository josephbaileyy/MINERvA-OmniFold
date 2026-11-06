"""RPD-RECO login measurements (the director's request of 2026-11-06), at 0 node-h: (1) the environment and uproot's read
of the histogram classes RPD-RECO's flux files use, on two non-input files staged in /dev/shm; (2) the cost of the Poisson
draws as fd_rpd_reco.py (10731ed3) makes them, and of one real-size chunk of its own `aggregate` at the full real-pass
shape, on synthetic arrays. Nothing here opens a declared RPD-RECO input or a COV2D input.

    python3 -I -B rpd_probe.py DIR      (DIR holds fd_rpd_reco.py, h2_definition.json and the staged ROOT copies)
Prints one JSON record.
"""
import json
import os
import sys
import time
from pathlib import Path

D = Path(sys.argv[1])
sys.path.insert(0, str(D))
import numpy as np  # noqa: E402
import scipy  # noqa: E402
import uproot  # noqa: E402

import fd_rpd_reco as R  # noqa: E402  (10731ed3, imported, never run)

REPS = 5
out = {"interpreter": sys.executable, "python": sys.version.split()[0], "numpy": np.__version__,
       "scipy": scipy.__version__, "uproot": uproot.__version__,
       "env": {k: os.environ.get(k) for k in R.THREAD_KEYS}, "nice": os.nice(0),
       "affinity": sorted(os.sched_getaffinity(0))}


# ---------------------------------------------------------------------------------------- (1) uproot on MAT histograms
def describe(path: Path) -> dict:
    rec = {"file": path.name, "keys": {}}
    with uproot.open(path) as f:
        for key, cls in sorted(f.classnames().items()):
            entry = {"class": cls}
            if cls.startswith(("TH1", "MnvH1D")):
                try:
                    obj = f[key]
                    entry["uproot_type"] = type(obj).__name__
                    entry["bases"] = [type(b).__name__ for b in getattr(obj, "bases", [])]
                    entry["own_members"] = sorted(getattr(obj, "_members", {}).keys())[:40]
                    values, edges = obj.to_numpy(flow=False)
                    entry.update(read=True, n_bins=int(values.size), edges=edges.tolist(), values=values.tolist())
                except Exception as e:  # recorded, not raised: whether the class reads at all is the question
                    entry.update(read=False, error=f"{type(e).__name__}: {e}"[:400])
            rec["keys"][key] = entry
    return rec


out["uproot_reads"] = [describe(D / n) for n in sorted(os.listdir(D)) if n.endswith(".root") and not n.startswith(".")]
# the run's own reader, on each 1D histogram that read
out["fd_rpd_reco_read_flux_histogram"] = {}
for f in out["uproot_reads"]:
    for key, e in f["keys"].items():
        if e.get("read") and e.get("n_bins"):
            name = key.split(";")[0]
            try:
                r = R.read_flux_histogram(D / f["file"], name)
                out["fd_rpd_reco_read_flux_histogram"][f"{f['file']}:{name}"] = {
                    "ok": True, "n_bins": int(len(r["values"])), "integral": r["integral"]}
            except Exception as ex:
                out["fd_rpd_reco_read_flux_histogram"][f"{f['file']}:{name}"] = {"ok": False, "error": str(ex)[:300]}


# ---------------------------------------------------------------------------------------- (2a) the raw Poisson draws
def raw_poisson() -> dict:
    """As aggregate makes them (fd_rpd_reco.py:1093-1095, :1189): one Generator per replica from
    SeedSequence([20261104, 11, replica + 1]), each drawing poisson(1, CHUNK_ROWS) per chunk; here one chunk's 200."""
    times = []
    for _ in range(REPS):
        gens = [np.random.default_rng(np.random.SeedSequence([20261104, 11, r + 1])) for r in range(R.BOOTSTRAPS)]
        t = time.perf_counter()
        for g in gens:
            g.poisson(1, R.CHUNK_ROWS)
        times.append(time.perf_counter() - t)
    n = R.BOOTSTRAPS * R.CHUNK_ROWS
    return {"api": "numpy.random.default_rng(SeedSequence([20261104, 11, r + 1])).poisson(1, 65536), r = 0..199",
            "bit_generator": type(np.random.default_rng().bit_generator).__name__, "draws_per_rep": n,
            "seconds_per_rep": times, "min_seconds_per_draw": min(times) / n}


# ---------------------------------------------------------------------------------------- (2b) one chunk of aggregate
class Stub:
    """Inputs as aggregate uses them: .started and .samples(data=...). Synthetic rows only."""

    def __init__(self, samples):
        self.started, self._s = time.monotonic(), samples

    def samples(self, *, data):
        yield from self._s


def synthetic(kind: str, rows: int, seed: int):
    rng = np.random.default_rng(seed)
    v = np.column_stack([rng.uniform(0, 2.5, rows), rng.uniform(1.5, 25, rows), rng.uniform(0, 1.2, rows),
                         rng.uniform(0.05, 2.5, rows), rng.uniform(0.9, 2.2, rows)])
    w = rng.uniform(0.5, 1.5, rows)
    truth = None
    if kind == "signal":
        truth = v * rng.uniform(0.95, 1.05, v.shape)
    return R.Sample(playlist="1D", kind=kind, values=v, weights=w, truth=truth)


def bins() -> dict:
    """step0's shapes (fd_rpd_reco.py:1003-1015): pz, pmu on PZ_EDGES, pt on PT_EDGES; theta, eavail, q3, W on
    [-inf, 9 distinct deciles, inf]; the declared H2 definition; a theta median."""
    dec = lambda lo, hi: np.r_[-np.inf, np.linspace(lo, hi, 9), np.inf]  # noqa: E731
    return {"axes": {"pz": R.PZ_EDGES, "pmu": R.PZ_EDGES, "pt": R.PT_EDGES, "theta": dec(0.02, 0.4),
                     "eavail": dec(0.05, 1.0), "q3": dec(0.2, 2.0), "W": dec(1.0, 2.0)},
            "theta_median": 0.15, "h2": json.loads((D / "h2_definition.json").read_text())}


def p0_record() -> dict:
    edges = np.linspace(0, 120, 241)
    vals = lambda s: 1e-6 * (1 + s * np.exp(-((edges[:-1] - 3) ** 2) / 4))  # noqa: E731 (all positive)
    spec = {k: {"edges": edges, "values": vals(s), "integral": float(np.sum(vals(s) * np.diff(edges)))}
            for k, s in (("1D", 50.0), ("1M", 55.0), ("1N", 52.0))}
    return {"spectra": spec}


def time_aggregate(kind: str, rows: int) -> list[float]:
    times = []
    b, p = bins(), p0_record()
    for rep in range(REPS):
        s = synthetic(kind, rows, 100 + rep)
        t = time.perf_counter()
        hist, _ = R.aggregate(Stub([s]), p, b, data=(kind == "data"))
        times.append(time.perf_counter() - t)
    return times, {k: (v["N"].shape if kind == "data" else v["P"].shape) for k, v in hist.items()}


def chunk_cost(kind: str) -> dict:
    one, shapes = time_aggregate(kind, R.CHUNK_ROWS)
    two, _ = time_aggregate(kind, 2 * R.CHUNK_ROWS)
    n = R.BOOTSTRAPS * R.CHUNK_ROWS
    variants = 1 if kind == "data" else 5
    return {"kind": kind, "rows_per_chunk": R.CHUNK_ROWS, "replicas": R.BOOTSTRAPS + 1, "draws_per_chunk": n,
            "axes": len(shapes), "variants": variants, "bincounts_per_chunk": (R.BOOTSTRAPS + 1) * len(shapes) * variants,
            "accumulator_shapes": {k: list(v) for k, v in shapes.items()},
            "seconds_1_chunk": one, "seconds_2_chunks": two,
            "S_per_draw_marginal_chunk": (min(two) - min(one)) / n,
            "per_draw_including_setup_1_chunk": min(one) / n}


out["raw_poisson"] = raw_poisson()
out["aggregate_full_shape_mc"] = chunk_cost("signal")   # the real pass, MC: every axis, all 5 variants
out["aggregate_data_informational"] = chunk_cost("data")  # the real pass, data: every axis, 1 weight
print(json.dumps(out, default=float))
