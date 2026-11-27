"""Price C-JOIN part 2 (omnifile_spot_check, fd_rpd_reco.py:2307-2414 at S = 2415e8d6) at full scale: peak RSS and time.

usage: python3 -I -B part2_probe.py REPO FIXTURE_DIR make   (writes the fixture: one playlist at 1M's size)
       python3 -I -B part2_probe.py REPO FIXTURE_DIR run    (12 passes over it: an upper bound for the 12 playlists)

The fixture is one playlist at the largest playlist's size, 1M, with 5,916,895 rows (flux4's true-energy record,
run-62051670):
  - omni.root: tree mc_signal_reco with the six OMNIFILE_BRANCHES, all 8-byte, written by uproot. The real branches
    are doubles or narrower, so this is an upper bound for the arrays read;
  - lat.npz: MCgen float32 (rows, 5), the dump's float32 layout;
  - factors.npz: energy, factor_1D, factor_1M, outside_1D and outside_1M, all float64 (an upper bound).

Each pass follows part 2's read pattern for one playlist:
  - inputs.key("lat_<PL>.npz", "MCgen"), kept for the pass;
  - pinned_flux_factors, which loads the product's arrays together and checks them;
  - the bound uproot_tree_reader (imported from fd_rpd_reco.py at S, never the working tree);
  - 66 spot lookups, each a three-mask np.flatnonzero over all rows.
Arrays are rebound each pass, never deleted, as omnifile_spot_check does, so two passes' arrays can coexist briefly.
It does not price the staging copy (stage_copy, an O_NOATIME read, hash and write of each omnifile). That is priced
from flux4's measured staging rate in RESULT.txt.
"""

from __future__ import annotations

import importlib.util
import resource
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

S = "2415e8d66d1a9160e724d426eaeb54d458d4b4f7"
ROWS = 5_916_895  # 1M, the largest playlist (run-62051670 true-energy record)
SPOTS = 66
BRANCHES = ("truthx_run", "truthx_subrun", "truthx_evt", "MC", "MC_pz", "truthx_enu")


def bound_module(repo: Path):
    source = subprocess.run(
        ["git", "-C", str(repo), "show", f"{S}:nd-unfolding/fd_rpd_reco.py"], check=True, capture_output=True
    ).stdout
    directory = Path(tempfile.mkdtemp(prefix="part2-probe-"))
    path = directory / "fd_rpd_reco.py"
    path.write_bytes(source)
    spec = importlib.util.spec_from_file_location("fd_rpd_reco_at_S", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    assert module.OMNIFILE_TREE == "mc_signal_reco" and tuple(module.OMNIFILE_BRANCHES) == BRANCHES
    return module


def make(directory: Path) -> None:
    import uproot

    rng = np.random.default_rng(20261126)
    run = rng.integers(10000, 30000, ROWS).astype(np.int64)
    subrun = rng.integers(1, 100, ROWS).astype(np.int64)
    event = np.arange(ROWS, dtype=np.int64)  # unique (run, subrun, event) per entry
    columns = {
        "truthx_run": run,
        "truthx_subrun": subrun,
        "truthx_evt": event,
        "MC": rng.uniform(0, 20, ROWS),
        "MC_pz": rng.uniform(0, 20, ROWS),
        "truthx_enu": rng.uniform(500, 50000, ROWS),
    }
    with uproot.recreate(directory / "omni.root") as handle:
        handle["mc_signal_reco"] = columns
    np.savez(directory / "lat.npz", MCgen=rng.uniform(0, 20, (ROWS, 5)).astype(np.float32))
    np.savez(
        directory / "factors.npz",
        energy=rng.uniform(0.5, 50, ROWS),
        factor_1D=rng.uniform(0, 2, ROWS),
        factor_1M=rng.uniform(0, 2, ROWS),
        outside_1D=rng.uniform(0, 1, ROWS),
        outside_1M=rng.uniform(0, 1, ROWS),
    )
    for name in ("omni.root", "lat.npz", "factors.npz"):
        print(name, (directory / name).stat().st_size, "bytes")


def run(module, directory: Path) -> None:
    chosen = np.unique(np.concatenate([[0, ROWS - 1], np.linspace(1, ROWS - 2, SPOTS - 2).astype(np.int64)]))
    started = time.monotonic()
    reads = []
    for _ in range(12):
        with np.load(directory / "lat.npz") as archive:
            truth = np.asarray(archive["MCgen"])
        with np.load(directory / "factors.npz") as archive:
            product = {k: archive[k] for k in ("energy", "factor_1D", "factor_1M", "outside_1D", "outside_1M")}
        assert all(np.all(np.isfinite(v)) for v in product.values())
        assert len(product["energy"]) == len(truth) == ROWS
        begin = time.monotonic()
        branches = module.uproot_tree_reader(directory / "omni.root", module.OMNIFILE_TREE, module.OMNIFILE_BRANCHES)
        reads.append(time.monotonic() - begin)
        r = np.asarray(branches["truthx_run"], dtype=np.int64)
        s = np.asarray(branches["truthx_subrun"], dtype=np.int64)
        e = np.asarray(branches["truthx_evt"], dtype=np.int64)
        for row in chosen:
            key = (r[row], s[row], e[row])
            entries = np.flatnonzero((r == key[0]) & (s == key[1]) & (e == key[2]))
            assert len(entries) == 1
            _ = np.float64(branches["truthx_enu"][entries[0]]) / 1000.0
            _ = np.float32(np.float64(branches["MC"][entries[0]])) == truth[row, 0]
        # no del: omnifile_spot_check reassigns these per playlist, so the previous pass's arrays stay
        # referenced until each name is rebound (the agy read's note); this probe keeps that pattern
    total = time.monotonic() - started
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    scale = 1 if sys.platform == "darwin" else 1024  # ru_maxrss: bytes on macOS, KiB on Linux
    print(f"passes 12, rows per pass {ROWS}, spots per pass {len(chosen)}")
    print(f"uproot read seconds per pass: min {min(reads):.2f} max {max(reads):.2f}")
    print(f"total seconds {total:.1f}")
    print(f"peak RSS bytes {peak * scale} = {peak * scale / 1e9:.3f} GB")


def main() -> int:
    repo, directory, mode = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    if mode == "make":
        make(directory)
        return 0
    import numpy, uproot

    print(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {sys.platform}, python {sys.version.split()[0]}, "
          f"numpy {numpy.__version__}, uproot {uproot.__version__}")
    baseline = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == "darwin" else 1024)
    module = bound_module(repo)
    print(f"baseline after imports, peak RSS bytes {baseline}")
    run(module, directory)
    return 0


if __name__ == "__main__":
    sys.exit(main())
