"""Check the READY candidate against #848's code at a4c3e556, offline.

usage: check_candidate.py CONFIG PROPOSED_CONFIG REPO   (REPO: any checkout holding commit a4c3e556)
"""
import csv
import hashlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path

S = "a4c3e556e7ccf915d103eaeba77ab31ed06b98cc"
config_path, proposed_path, repo = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]


def blob(rel: str) -> bytes:
    return subprocess.run(["git", "-C", repo, "show", f"{S}:{rel}"], capture_output=True, check=True).stdout


raw = config_path.read_bytes()
cfg = json.loads(raw)
proposed = json.loads(proposed_path.read_bytes())
print("config sha256", hashlib.sha256(raw).hexdigest())
print("serializer reproduces the file:", (json.dumps(cfg, indent=1, sort_keys=True) + "\n").encode() == raw)
print("'${' in the file:", b"${" in raw)
changed = []


def walk(a, b, path="$"):
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a) | set(b)):
            walk(a.get(key), b.get(key), f"{path}.{key}")
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for index, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}[{index}]")
    elif a != b:
        changed.append((path, a, b))


walk(proposed, cfg)
for path, a, b in changed:
    print("changed from the proposal:", path, json.dumps(a), "->", json.dumps(b))
with tempfile.TemporaryDirectory() as tmp:
    for name in ("fd_rpd_reco.py", "fd_rpd_inputs.py", "fd_rpd_reco_custody.py"):
        (Path(tmp) / name).write_bytes(blob(f"nd-unfolding/{name}"))
    sys.path.insert(0, tmp)
    import fd_rpd_reco as r

    print("fd_rpd_reco.py sha256", hashlib.sha256((Path(tmp) / "fd_rpd_reco.py").read_bytes()).hexdigest())
    print("placeholder_paths:", r.placeholder_paths(cfg))
    print("configuration_status:", cfg["configuration_status"])
    for key in ("pins", "h2", "inventory", "constants", "mat_dependencies"):
        rel = cfg[key]["path"].split("/dev/shm/limres-rpd-flux1/repo/", 1)[1]
        data = blob(rel)
        print(f"bound {key}: sha256 equal at {S[:8]}:", hashlib.sha256(data).hexdigest() == cfg[key]["sha256"], rel)
        if key == "inventory":
            rows = list(csv.DictReader(io.StringIO(data.decode()), delimiter="\t"))
    for group, spec in cfg["flux_selection"].items():
        hits = [x for x in rows if x["playlist_label"] == group and x["relative_path"] == spec["relative_path"]]
        print(f"selection {group}: inventory rows {len(hits)}, sha256 {hits[0]['sha256'] if hits else None}")
    print("flux_selection_digest", r.flux_selection_digest(cfg))
    run = cfg["flux_extract"]["path"].rsplit("/", 1)[0]
    print("run directory", run, "; custody receipt in the same run:", cfg["flux_custody"]["path"].rsplit("/", 1)[0] == run)
