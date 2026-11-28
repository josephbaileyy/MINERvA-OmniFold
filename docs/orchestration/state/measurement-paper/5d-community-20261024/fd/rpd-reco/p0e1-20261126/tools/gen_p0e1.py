"""Generate e1's P0 package (p0e1) at 2415e8d6 from the bound P0 package (p0-20261123), by counted replacements.

usage: python3 -I -B gen_p0e1.py REPO
  REPO  a checkout of this repository with S (2415e8d6, #1308's merge) in its history; pinned files are read at S
        through `git show`, never from the working tree.

RPD-RECO amendment 1 (#1300), its code (#1308) and flux4 (job 62051670, records run-62051670): P0 is P0 as bound under
FD-RPD-RECO-BINDING-2-ADDENDUM-3, now reading flux4's records and products. C-JOIN part 2 (omnifile_spot_check) is in
the bound code's p0 step. The director accepted this plan on 2026-11-26, with these declared changes:
  1. the clone moves to S, and P0's 14 pins move as flux4's did: only #1308's four files change (flux4's connect is the
     reference, and each pin is re-read at S);
  2. the config is flux4's f53a86f6 with exactly flux_extract/sha256 and flux_custody/sha256 filled from run-62051670.
     Against P0's 3b2afde4, the leaf diff is asserted to be the two record paths, the two digests and the added
     true_energy block;
  3. the in-place inputs (tools/p0_expected.json "inputs") are flux4's extract, custody record and 12 factor products,
     with run-62051670's committed sha256s;
  4. the fences: flux4's sacct block (geanttw* added; asserted equal to flux4's connect), flux4's three-lane ack guard
     in the launcher (cov2d, tier3-design, minerva-lib), and the overlap fence copied from flux4's at the new root,
     also listing the 12 omnifiles that p0 stages. The runner, supervisor, deadline and RSS cap are unchanged;
  5. the retention stat (default (a)) also stats, never opens, the 12 RDX omnifiles and the true-energy sidecar,
     compared with the size and inode the sidecar probe recorded on 2026-11-26 (sidecar-probe-20261126/run-20261126/
     probe.json); p0_checks.py's code is unchanged except its wording;
  6. ibu-chi is messaged before the connect but is not in the ack file (default (b)).
Every replacement must match its stated count. flux3's and flux4's generators are loaded (sha256-pinned) for their
launcher ack blocks.
"""

from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
RECO = OUT.parent
P0 = RECO / "p0-20261123"
FLUX4 = RECO / "flux4-20261126"
RUN4 = FLUX4 / "run-62051670"
PROBE = RECO / "sidecar-probe-20261126" / "run-20261126" / "probe.json"
OLD_ROOT = "/pscratch/sd/j/josephrb/rpd-reco-p0-20261123"
ROOT = "/pscratch/sd/j/josephrb/rpd-reco-p0e1-20261126"
OLD_FLUX = "/pscratch/sd/j/josephrb/rpd-reco-flux3-20261123"
FLUX_ROOT = "/pscratch/sd/j/josephrb/rpd-reco-flux4-20261126"
OLD_S = "6896e7871421469ce72c6b93188d2d1a55c82ec6"
S = "2415e8d66d1a9160e724d426eaeb54d458d4b4f7"
SHA = {
    # the bound P0 package (FD-RPD-RECO-BINDING-2-ADDENDUM-3)
    "config": "3b2afde495d630cc44df730e3e1acf12e0c332953e9fa298fa979f2e2e39b057",
    "connect": "6a1bed9547b7a462b3ccdbbe05c34f322a27980be085d2996eb89950a25da678",
    "fetch": "12626af6f6ff5d765b602ebd0f012f2e3d6f8d3f1fa60969b0f8bd4d4e022b6a",
    "launch": "b70998fffa5de0f585ef3e60e24b17c7ba166bc10e718d13187e424928e4e366",
    "fence": "23d0ffc7bf89a4b81a33b081fa7377401dec33634372d5ed5b106bee6c4fd22b",
    "checks": "93d0de8bda48a00eeba4edab306590146f5c1d807bed701be021bdfb0b864fcc",
    "expected": "bb175e948fff89fc1e3097b0aaf5107e5e796bc05e1f4892e0d00b07b2a5b6b6",
    "supervise": "6ad0f68fb309a7b83adc0f65ed709e5e2412e650e115075fe41ebbc7a070134f",
    # the bound flux4 package (RPD-FLUX4-BINDING) and its generators
    "flux4_config": "f53a86f6dec50965d1d45cb77bcfc904228ebd96ffa18eb9f87babeb53d1ba1d",
    "flux4_connect": "8989815086ec0ed771d333b109d3ef627e85dbfebe9d76d7b51f6336fe637215",
    "flux4_fence": "1371a21a867739b6250175fe5fd7667f6175d055d115b5079d66f9b9070fc512",
    "gen4": "73d02cd0e364c85c9ce75bea214a8f93df62b155179c206847ce8b6903ba0d4a",
    "gen3": "f760c20d8c739ba4cf1a181ef1a970fad48e6c80ba207c8ffc1376f26527eccc",
    # flux4's committed records (run-62051670) and the sidecar probe's record
    "extract": "060d4401f0e1bec69a84b005e0c7ba54f69c3f894c1382f9ce2a098b7b2663c0",
    "custody": "819bb7b9775c1bfe570185881290ab229e82d3ad7ad328b9cde3215a811c78c2",
    "probe": "ba176426f57a4a59d7209729516140d3f71ff3e3b25297b7471e616f5d1b8ddd",
    "reco_module": "12f68102d38ec042d791b9edeb59ba96bdcda74c54dc37e5880c0922b0fbb9ec",
    "custody_module": "6428deadb6bf6c4a5bde968d33eba2870b3e503a3a8110bfca431326c349776c",
}
DIGEST = "75c2a1f4435494bf0e2c5bf4d27631781e65bd738c889c667183778e254792e8"
PLAYLISTS = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")
SIDECAR = "/pscratch/sd/j/josephrb/rdx-20261112b/out/dumps/truthx_RDX_ALL.npz"
OMNI = "/pscratch/sd/j/josephrb/rdx-20261112b/out/evloop/runEventLoopOmniFold_RDX_{}.root"

CONNECT_HEADER_OLD = (
    "# RPD-RECO P0 (rpd_p0): the login-node connect. P0 is login-only at 0 node-h, with no job (FD-RPD-RECO-DECLARATION\n"
    "# section 5, BINDING-1 ruling 3). It reads flux3's records and products (run-61861637) in place. It runs only on the\n"
)
CONNECT_HEADER_NEW = (
    "# RPD-RECO P0 for e1 (rpd_p0; RPD-RECO amendment 1, generated from p0-20261123 at 2415e8d6): the login-node connect.\n"
    "# P0 is login-only at 0 node-h, with no job (FD-RPD-RECO-DECLARATION section 5, BINDING-1 ruling 3). C-JOIN part 2\n"
    "# runs in its p0 step. It reads flux4's records and products (run-62051670) in place. It runs only on the\n"
)
LAUNCH_HEADER_OLD = (
    "# RPD-RECO P0 (rpd_p0, generated from the flux3 launcher): the Mac-side launcher, in rpd_mnv_check2_launch.sh's"
    " pattern. connect requires cov2d's fresh ack file, kept byte for byte in the local session record."
)
LAUNCH_HEADER_NEW = (
    "# RPD-RECO P0 for e1 (rpd_p0, generated from p0-20261123's launcher with flux4's ack guard): the Mac-side launcher,"
    " in rpd_mnv_check2_launch.sh's pattern. connect requires the three-lane ack file (cov2d, tier3-design,"
    " minerva-lib), kept byte for byte in the local session record."
)
FENCE_OMNIFILES_OLD = (
    '    if isinstance(config.get("true_energy"), dict):  # prepare stages it at 2415e8d6 (#1308)\n'
    '        reads.append(("true_energy", config["true_energy"]["path"]))\n'
)
FENCE_OMNIFILES_NEW = FENCE_OMNIFILES_OLD + (
    '        for playlist, spec in sorted(config["true_energy"]["omnifiles"].items()):  # p0 stages each (C-JOIN part 2)\n'
    '            reads.append((f"omnifile {playlist}", spec["path"]))\n'
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dump(value: dict) -> bytes:
    return (json.dumps(value, indent=1, sort_keys=True, ensure_ascii=True) + "\n").encode()


def replace(text: str, old: str, new: str, count: int, what: str) -> str:
    found = text.count(old)
    assert found == count, f"{what}: {found} occurrences of {old[:70]!r}, expected {count}"
    return text.replace(old, new)


def lift(text: str, start: str, end: str) -> str:
    """The block of TEXT from the one line starting START through the first line after it starting END."""
    lines = text.splitlines(keepends=True)
    first = [i for i, line in enumerate(lines) if line.startswith(start)]
    assert len(first) == 1, (start, first)
    last = [i for i, line in enumerate(lines) if i >= first[0] and line.startswith(end)]
    assert last, (start, end)
    return "".join(lines[first[0] : last[0] + 1])


def git_show(repo: Path, path: str) -> bytes:
    return subprocess.run(["git", "-C", str(repo), "show", f"{S}:{path}"], check=True, capture_output=True).stdout


def leaves(value: object, path: str = "") -> dict[str, object]:
    if isinstance(value, dict):
        out: dict[str, object] = {}
        for key, item in value.items():
            out.update(leaves(item, f"{path}/{key}"))
        return out
    if isinstance(value, list):
        out = {}
        for index, item in enumerate(value):
            out.update(leaves(item, f"{path}/{index}"))
        return out
    return {path: value}


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def load(path: Path, key: str):
    assert sha(path.read_bytes()) == SHA[key], key
    spec = importlib.util.spec_from_file_location(key, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    repo = Path(sys.argv[1])
    old = {
        "config": (P0 / "production-config.ready.json").read_bytes(),
        "connect": (P0 / "rpd_p0_connect.sh").read_bytes(),
        "fetch": (P0 / "rpd_p0_fetch.sh").read_bytes(),
        "launch": (P0 / "rpd_p0_launch.sh").read_bytes(),
        "fence": (P0 / "tools" / "fence_overlap.py").read_bytes(),
        "checks": (P0 / "tools" / "p0_checks.py").read_bytes(),
        "expected": (P0 / "tools" / "p0_expected.json").read_bytes(),
        "supervise": (P0 / "tools" / "p0_supervise.py").read_bytes(),
        "flux4_config": (FLUX4 / "production-config.ready.json").read_bytes(),
        "flux4_connect": (FLUX4 / "rpd_flux4_connect.sh").read_bytes(),
        "flux4_fence": (FLUX4 / "tools" / "fence_overlap.py").read_bytes(),
        "extract": (RUN4 / "records" / "run" / "flux-extract.json").read_bytes(),
        "custody": (RUN4 / "records" / "run" / "flux-custody.json").read_bytes(),
        "probe": PROBE.read_bytes(),
    }
    for key, data in old.items():
        assert sha(data) == SHA[key], key
    gen3 = load(RECO / "flux3-20261123" / "tools" / "gen_flux3.py", "gen3")
    gen4 = load(FLUX4 / "tools" / "gen_flux4.py", "gen4")
    receipt = json.loads(old["custody"])
    assert receipt["status"] == "PASS" and receipt["custody_code_sha256"] == SHA["custody_module"]
    assert receipt["code_sha256"] == SHA["reco_module"] and receipt["extract_sha256"] == SHA["extract"]
    extract = json.loads(old["extract"])
    assert extract["status"] == "PASS" and extract["selection_sha256"] == DIGEST
    assert extract["code_sha256"] == SHA["reco_module"] and extract["true_energy"]["status"] == "PASS"

    # 1. The config: flux4's, with the two record digests filled (P0's own change to flux3's config, repeated).
    flux4_config = json.loads(old["flux4_config"])
    assert dump(flux4_config) == old["flux4_config"], "the JSON format does not reproduce f53a86f6"
    new = json.loads(old["flux4_config"])
    for key, digest in (("flux_extract", SHA["extract"]), ("flux_custody", SHA["custody"])):
        assert new[key]["sha256"] is None and new[key]["path"].startswith(FLUX_ROOT + "/run/"), key
        new[key]["sha256"] = digest
    a, b = leaves(flux4_config), leaves(new)
    assert set(a) == set(b) and {k for k in a if a[k] != b[k]} == {"/flux_extract/sha256", "/flux_custody/sha256"}
    p0_config = json.loads(old["config"])
    c = leaves(p0_config)
    changed = {k for k in c if k in b and c[k] != b[k]}
    assert set(c) <= set(b) and changed == {
        "/flux_extract/path",
        "/flux_extract/sha256",
        "/flux_custody/path",
        "/flux_custody/sha256",
    }, sorted(changed)
    assert {k for k in b if k not in c} == {k for k in b if k.startswith("/true_energy/")}
    cfg = dump(new)
    module = git_show(repo, "nd-unfolding/fd_rpd_reco.py")
    assert sha(module) == SHA["reco_module"]

    # 2. The expected inputs (flux4's records and products, in place) and the stat table: P0's 27 plus the 12
    #    omnifiles and the sidecar, at the sizes and inodes the sidecar probe recorded.
    inputs = {new["flux_extract"]["path"]: SHA["extract"], new["flux_custody"]["path"]: SHA["custody"]}
    for playlist, product in sorted(extract["factor_products"].items()):
        assert product["path"] == f"{FLUX_ROOT}/run/flux-factors-{playlist}.npz", product["path"]
        inputs[product["path"]] = product["sha256"]
    assert len(inputs) == 14
    stat = dict(json.loads(old["expected"])["stat"])
    assert len(stat) == 27 and not any(p.startswith("/pscratch/sd/j/josephrb/rdx-") for p in stat)
    probe = json.loads(old["probe"])
    side = probe["sidecar"]
    assert side["path"] == SIDECAR and side["sha256_matches"] is True and side["size_matches_read"] is True
    stat[SIDECAR] = {"bytes": side["size"], "inode": side["inode"]}
    listed = {entry["path"]: entry for entry in probe["stat_only"]}
    for playlist in PLAYLISTS:
        entry = listed[OMNI.format(playlist)]
        assert type(entry["size"]) is int and type(entry["inode"]) is int, playlist
        stat[entry["path"]] = {"bytes": entry["size"], "inode": entry["inode"]}
    assert len(stat) == 40
    pinned = {p: new["true_energy"]["omnifiles"][p]["path"] for p in PLAYLISTS}
    assert all(path in stat for path in pinned.values()) and new["true_energy"]["path"] in stat
    expected = dump({"inputs": inputs, "stat": stat})

    # 3. p0_checks.py: its code unchanged; its wording names flux4's records and the probe's stat values.
    checks = old["checks"].decode()
    checks = replace(
        checks,
        "inputs  Reads each of flux3's records and factor products that P0 reads in place (EXPECTED_JSON \"inputs\": path ->\n"
        "        sha256, from the committed run-61861637 records)",
        "inputs  Reads each of flux4's records and factor products that P0 reads in place (EXPECTED_JSON \"inputs\": path ->\n"
        "        sha256, from the committed run-62051670 records)",
        1,
        "checks inputs doc",
    )
    checks = replace(
        checks,
        "stat    Stats (never opens) the three selected gen2thin flux files and the 24 dumps (EXPECTED_JSON \"stat\": path ->\n"
        "        {bytes, inode}, from S1's survey of 2026-11-22) and prints each one's bytes, atime, mtime and inode, then the\n"
        "        earliest purge exposure (atime + PURGE_DAYS days, the oldest first). A missing file, or bytes or an inode\n"
        "        different from S1's, exits 3.",
        "stat    Stats (never opens) the three selected gen2thin flux files, the 24 dumps, the 12 RDX omnifiles and the\n"
        "        true-energy sidecar (EXPECTED_JSON \"stat\": path -> {bytes, inode}; S1's survey of 2026-11-22 for the\n"
        "        first 27, the sidecar probe of 2026-11-26 for the other 13) and prints each one's bytes, atime, mtime and\n"
        "        inode, then the earliest purge exposure (atime + PURGE_DAYS days, the oldest first). A missing file, or\n"
        "        bytes or an inode different from the record, exits 3.",
        1,
        "checks stat doc",
    )
    checks = replace(checks, '"same as S1"', '"same as recorded"', 1, "checks verdict")
    checks = replace(checks, 'f"DIFFERS from S1 (bytes', 'f"DIFFERS from the record (bytes', 1, "checks differs")
    assert "flux3" not in checks and "61861637" not in checks and "S1's survey" in checks
    checks_bytes = checks.encode()
    supervise = old["supervise"]

    # 4. The fence copy: flux4's, at the new root, also listing the omnifiles p0 stages.
    fence = replace(
        old["flux4_fence"].decode(), f'WRITE_ROOTS = ("{FLUX_ROOT}",', f'WRITE_ROOTS = ("{ROOT}",', 1, "fence root"
    )
    fence = replace(fence, FENCE_OMNIFILES_OLD, FENCE_OMNIFILES_NEW, 1, "fence omnifiles")
    fence = replace(
        fence,
        "flux_source; the true-energy sidecar (true_energy.path, staged by prepare since #1308); every path in the\n",
        "flux_source; the true-energy sidecar (true_energy.path, staged by prepare since #1308) and the 12 RDX\n"
        "omnifiles (true_energy.omnifiles, staged by p0 for C-JOIN part 2); every path in the\n",
        1,
        "fence docstring",
    )
    fence = replace(
        fence,
        "run before the job is submitted.",
        "run before anything is started.",
        1,
        "fence docstring P0",
    ).encode()

    # 5. The connect.
    connect = old["connect"].decode()
    connect = replace(connect, b64(old["config"]), b64(cfg), 1, "connect config blob")
    connect = replace(connect, b64(old["fence"]), b64(fence), 1, "connect fence blob")
    connect = replace(connect, b64(old["checks"]), b64(checks_bytes), 1, "connect checks blob")
    connect = replace(connect, b64(old["expected"]), b64(expected), 1, "connect expected blob")
    assert connect.count(b64(supervise)) == 1, "connect supervisor blob"
    connect = replace(connect, CONNECT_HEADER_OLD, CONNECT_HEADER_NEW, 1, "connect header")
    connect = replace(connect, SHA["config"], sha(cfg), 2, "connect config sha")
    connect = replace(connect, SHA["fence"], sha(fence), 1, "connect fence sha")
    connect = replace(connect, SHA["checks"], sha(checks_bytes), 1, "connect checks sha")
    connect = replace(connect, SHA["expected"], sha(expected), 1, "connect expected sha")
    connect = replace(connect, OLD_S, S, 2, "connect clone sha")
    connect = replace(connect, OLD_ROOT, ROOT, 54, "connect root")
    flux4_connect = old["flux4_connect"].decode()
    p0_pins = connect[connect.index("done <<'PINS'\n") + len("done <<'PINS'\n") :]
    p0_pins = p0_pins[: p0_pins.index("PINS\n")]
    f4_pins = flux4_connect[flux4_connect.index("done <<'PINS'\n") + len("done <<'PINS'\n") :]
    f4_pins = f4_pins[: f4_pins.index("PINS\n")]
    moved = 0
    for mine, theirs in zip(p0_pins.splitlines(keepends=True), f4_pins.splitlines(keepends=True), strict=True):
        assert mine.split(" ", 1)[1] == theirs.split(" ", 1)[1], (mine, theirs)
        want, path = theirs.split()
        assert sha(git_show(repo, path)) == want, f"{path} at S is not flux4's pin {want}"
        if mine != theirs:
            connect = replace(connect, mine, theirs, 2, f"connect pin {path}")
            moved += 1
    assert moved == 4, moved
    connect = replace(connect, "(cov2d|t2a|rpd)", "(cov2d|t2a|rpd|geanttw)", 1, "sacct family")
    connect = replace(connect, "cov2d/t2a/rpd", "cov2d/t2a/rpd/geanttw", 2, "sacct family labels")
    connect = replace(connect, "cov2d*, t2a*, rpd* refuse", "cov2d*, t2a*, rpd*, geanttw* refuse", 1, "fence title")
    sacct_start, sacct_end = 'echo "== 2. the fence', 'echo "FENCE: clear"'
    assert lift(connect, sacct_start, sacct_end) == lift(flux4_connect, sacct_start, sacct_end), "flux4's sacct block"
    connect = replace(
        connect,
        "#   2. the sacct fence (any unended cov2d*, t2a* or rpd* job refuses; flux3's tightened block, byte for byte);",
        "#   2. the sacct fence (any unended cov2d*, t2a*, rpd* or geanttw* job refuses; flux4's block, byte for byte);",
        1,
        "connect header fence",
    )
    connect = replace(
        connect,
        "#   5. P0's in-place inputs: flux3's extract, custody record and 12 factor products, read with O_NOATIME and checked\n"
        "#      against the committed run-61861637 records (tools/p0_checks.py inputs);",
        "#   5. P0's in-place inputs: flux4's extract, custody record and 12 factor products, read with O_NOATIME and checked\n"
        "#      against the committed run-62051670 records (tools/p0_checks.py inputs);",
        1,
        "connect header inputs",
    )
    connect = replace(
        connect,
        "#   6. a fresh stat (never an open) of the three gen2thin flux files and the 24 dumps, compared with S1's bytes and\n"
        "#      inodes, with the earliest purge exposure printed (tools/p0_checks.py stat, recorded in stat-p0.txt);",
        "#   6. a fresh stat (never an open) of the three gen2thin flux files, the 24 dumps, the 12 RDX omnifiles and the\n"
        "#      true-energy sidecar, compared with the recorded bytes and inodes (S1's for the first 27, the sidecar probe's\n"
        "#      for the 13), with the earliest purge exposure printed (tools/p0_checks.py stat, recorded in stat-p0.txt);",
        1,
        "connect header stat",
    )
    connect = replace(
        connect,
        "P0's in-place inputs (flux3's records and factor products, O_NOATIME)",
        "P0's in-place inputs (flux4's records and factor products, O_NOATIME)",
        1,
        "connect step 5 title",
    )
    connect = replace(connect, "flux3-inputs.txt", "flux4-inputs.txt", 2, "connect inputs record")
    connect = replace(
        connect,
        'echo "== 6. a fresh stat of the gen2thin flux files and the dumps (against S1)"',
        'echo "== 6. a fresh stat of the gen2thin flux files, the dumps, the omnifiles and the sidecar (against the records)"',
        1,
        "connect step 6 title",
    )
    connect = replace(
        connect,
        "STOP: a file is missing, or its bytes or inode differ from S1's",
        "STOP: a file is missing, or its bytes or inode differ from the record",
        1,
        "connect step 6 stop",
    )
    body = connect.replace(CONNECT_HEADER_NEW, "")
    for bad in ("squeue", "sbatch", OLD_ROOT, OLD_S, "flux3", "61861637", OLD_FLUX, SHA["config"]):
        assert bad not in body, (bad, body.count(bad))
    python_calls = [line for line in connect.splitlines() if '"$PY"' in line or '"$MAT_PYTHON"' in line]
    assert python_calls and all(" -B " in line for line in python_calls), python_calls

    # 6. The fetch.
    fetch = old["fetch"].decode()
    fetch = replace(fetch, OLD_ROOT, ROOT, 3, "fetch root")
    fetch = replace(fetch, "flux3-inputs.txt", "flux4-inputs.txt", 2, "fetch inputs record")
    for bad in ("squeue", "python", OLD_ROOT, "flux3"):
        assert bad not in fetch, (bad, fetch.count(bad))

    # 7. The launcher: P0's, re-pinned, with flux4's three-lane ack guard in place of flux3's one-lane guard.
    launch = old["launch"].decode()
    launch = replace(launch, LAUNCH_HEADER_OLD, LAUNCH_HEADER_NEW, 1, "launch header")
    launch = replace(launch, SHA["connect"], sha(connect.encode()), 1, "launch connect sha")
    launch = replace(launch, SHA["fetch"], sha(fetch.encode()), 1, "launch fetch sha")
    launch = replace(launch, OLD_ROOT, ROOT, 1, "launch root")
    launch = replace(launch, gen3.LAUNCH_ACK, gen4.LAUNCH_ACK3, 1, "launch ack guard")
    body = launch.replace(LAUNCH_HEADER_NEW, "")
    for bad in ("squeue", "flux3", "cov2d's ack", OLD_ROOT):
        assert bad not in body, (bad, body.count(bad))

    outputs = {
        "production-config.ready.json": cfg,
        "tools/p0_expected.json": expected,
        "tools/p0_checks.py": checks_bytes,
        "tools/p0_supervise.py": supervise,
        "tools/fence_overlap.py": fence,
        "rpd_p0_connect.sh": connect.encode(),
        "rpd_p0_fetch.sh": fetch.encode(),
        "rpd_p0_launch.sh": launch.encode(),
    }
    for name, data in outputs.items():
        (OUT / name).write_bytes(data)
        print(sha(data), name)
    assert connect.count("<<'RUNNER'\n") == 1 and connect.count("\nRUNNER\n") == 1
    runner = connect.split("<<'RUNNER'\n", 1)[1].split("\nRUNNER\n", 1)[0] + "\n"
    print(sha(runner.encode()), "(runner, as the connect's heredoc writes it)")
    print("flux_selection_digest", DIGEST, "(flux4's extract records it)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
