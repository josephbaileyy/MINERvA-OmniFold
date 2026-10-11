#!/usr/bin/env python3
"""No-fit Linux probe of the package's child-free steps, for a login node (no training, no job).

    cd <checkout>/2d-unfolding && source <setup> && \\
    python <checkout>/nd-unfolding/mnv_guarded_run.py --expect-root <checkout> --inventory INV --label probe -- \\
        <checkout>/docs/.../xr-linux/xr/tests/linux_login_probe.py OUT.json

Under the OI-136 guard and inside ``xr_run.LaunchSpy`` it runs the frozen environment check (with
the child-free runtime record), the thread plan for the preflight kind (on a login node it is
expected to refuse: the node is not a 12-CPU allocation), the launch-window controls
(``find_library("c")`` and loky's physical-core query must be refused) and the fixture writer
into a temporary directory, timing each. It calls no driver and fits nothing. It is a diagnostic
for the admission review, not part of any run's path.
"""
import json
import sys
import tempfile
import time
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
t0 = time.perf_counter()
import xr_run  # noqa: E402

out = {"import_xr_run_s": time.perf_counter() - t0, "platform": sys.platform}
runs = json.loads((PKG / "manifest" / "runs.json").read_text())
spy = xr_run.LaunchSpy()
with spy:
    t = time.perf_counter()
    try:
        out["environment"] = xr_run.check_environment(runs["environment"])
        out["environment_status"] = "ok"
    except xr_run.BackendRefusal as exc:
        out["environment_status"] = f"refused: {exc}"
    out["environment_s"] = time.perf_counter() - t
    try:
        out["thread_plan"] = xr_run.thread_plan(runs["kinds"]["preflight"])
    except xr_run.BackendRefusal as exc:
        out["thread_plan"] = f"refused: {exc}"
    t = time.perf_counter()
    import importlib.util
    fx = runs["preflight"]["fixture"]
    spec = importlib.util.spec_from_file_location("xr_probe_maker", xr_run.REPO / fx["maker"])
    maker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(maker)
    with tempfile.TemporaryDirectory() as d:
        info = maker.write_fixture(str(Path(d) / "omni.root"), rows=fx["rows"], extra=fx["extra"], seed=fx["seed"])
        maker.write_flux(str(Path(d) / "flux.root"))
    out["fixture_write"] = {"s": time.perf_counter() - t, "bytes": info["bytes"]}
out["launches_in_window"] = spy.calls
out["launch_controls"] = xr_run.launch_controls()
out["total_s"] = time.perf_counter() - t0
Path(sys.argv[1]).write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
print(json.dumps({k: out[k] for k in ("environment_status", "thread_plan", "launches_in_window", "total_s")},
                 default=str, indent=1))
print("launch controls met:", out["launch_controls"]["met"],
      {k: [c["argv"] for c in v["launches"]] for k, v in out["launch_controls"]["probes"].items()})
