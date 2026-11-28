"""Generate e1's d2-predict + step0 package (d2s0e1) from the bound d2s0 package (d2s0-20261124), by counted replacements.

usage: python3 -I -B gen_d2s0e1.py

RPD-RECO amendment 1: after e1's P0 (p0e1, run-20261127, C-JOIN part 2 PASS), the chain reruns d2-predict + step0,
where C-E3 is retested with true Eν. The d2s0 package is P0's machinery with P0's two run records as predecessors
(d2s0-20261124/README.md). This package changes it exactly as p0e1 changed P0, and points it at p0e1:
  1. the clone moves to S = 2415e8d6; the 14 pins become p0e1's (only #1308's four files move);
  2. the config is p0e1's f92d034d (require_predecessors compares it with P0's records);
  3. the in-place inputs are p0e1's 14 (flux4's records and products) plus p0e1's run/pins.json and run/p0.json, at
     the committed run-20261127 values; the stage loop copies those two records from p0e1's root;
  4. the fences: flux4's sacct block (geanttw* added) and three-lane ack guard, as in p0e1; the overlap fence is
     p0e1's at the new root;
  5. the retention stat is p0e1's 40 (S1's 27 plus the 12 omnifiles and the sidecar), with p0e1's wording in the
     checks tool;
  6. the runner, supervisor, deadlines, RSS cap and fetch are otherwise d2s0's.
Every input is asserted at its sha256 and every replacement at its count. A rerun reproduces every output byte for
byte.
"""

from __future__ import annotations

import base64
import gzip
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
RECO = OUT.parent
D2S0 = RECO / "d2s0-20261124"
P0E1 = RECO / "p0e1-20261126"
P0E1_RECORDS = P0E1 / "run-20261127" / "records" / "run"
OLD_ROOT = "/pscratch/sd/j/josephrb/rpd-reco-d2s0-20261124"
ROOT = "/pscratch/sd/j/josephrb/rpd-reco-d2s0e1-20261127"
OLD_P0_ROOT = "/pscratch/sd/j/josephrb/rpd-reco-p0-20261123"
P0_ROOT = "/pscratch/sd/j/josephrb/rpd-reco-p0e1-20261126"
P0E1_FENCE_ROOT = P0_ROOT
OLD_S = "6896e7871421469ce72c6b93188d2d1a55c82ec6"
S = "2415e8d66d1a9160e724d426eaeb54d458d4b4f7"
SHA = {
    # the bound d2s0 package (d2s0-20261124)
    "connect": "8bf94bb0244bf341c2fd883a03e01b22a3fffea32131d41834819012e8e4f783",
    "fetch": "55227af2fa4d0a4b526e2224ee6736b8cfdb5aea1c16bcfb698abefcfd79b287",
    "launch": "e2bde947866807baf7a5ee92c5ec3842e9c6e96f68abc58e74fc08a92b426e61",
    "checks": "d3ff48f98cd797434c213730b9cf6b8bae6904be2b352f499efa1bb29086a506",
    "expected": "17a13256bac006c87703249989d4504af3144523a4797b95a51ee4a88699b509",
    "fence": "33ba39c3ac65e5ca0c6f1c1657fb41a6edbda4af11b94bc3242892774b1c4e21",
    "supervise": "6ad0f68fb309a7b83adc0f65ed709e5e2412e650e115075fe41ebbc7a070134f",
    "config": "3b2afde495d630cc44df730e3e1acf12e0c332953e9fa298fa979f2e2e39b057",
    "old_p0_record": "8ed2faf71a3966ed832831ba669c093235aa39c00fda515edecfd6b60a34be10",
    "old_pins_record": "52fc41f41cf17954ceddab8c581aa327a62d160c059cbee8bf2941c1880e5c8a",
    # the bound p0e1 package (RPD-P0E1-BINDING) and its records (run-20261127)
    "p0e1_config": "f92d034df0db5bf487f689b0efc1eb8862396303647fa1172ad5e6eaa3f4c47a",
    "p0e1_connect": "5016f37822af9c43e52b8fe9379757306c8dd47948115d9dad566d88ab242434",
    "p0e1_expected": "c9d5e9567eba82818616c2b25c0162f113026e5feec8d2971dbe8f18d5f3dee9",
    "p0e1_fence": "940fb7598c782c77c2b3dd0e677f80568f0fdb31fd033e8e8988404049f38810",
    "p0_record": "ab8d3600e7955e0afa0f0affaedeab7d394bff9010c4d1f9e7a011c9d2290c4c",
    "pins_record": "2a22bdbfc2af1891d2db13e1b49c4e53c063296002b3a2fd1e240850dad121a8",
    "pins_gz": "7b7dedf76d6ccaf0be26d193ce4829f3585a7c81764a20ca1b6877d3d16a1b9c",
    "gen4": "73d02cd0e364c85c9ce75bea214a8f93df62b155179c206847ce8b6903ba0d4a",
    "gen3": "f760c20d8c739ba4cf1a181ef1a970fad48e6c80ba207c8ffc1376f26527eccc",
}
RECO_MODULE = "12f68102d38ec042d791b9edeb59ba96bdcda74c54dc37e5880c0922b0fbb9ec"

HEADER_OLD = (
    "# RPD-RECO d2-predict and step0 (rpd_d2s0): the login-node connect, generated from P0's bound connect (6a1bed95) by\n"
    "# tools/gen_d2s0.py."
)
HEADER_NEW = (
    "# RPD-RECO d2-predict and step0 for e1 (rpd_d2s0; RPD-RECO amendment 1, C-E3 retested with true Eν): the login-node\n"
    "# connect, generated from d2s0-20261124's bound connect (8bf94bb0) by tools/gen_d2s0e1.py."
)
FETCH_HEADER_OLD = "# RPD-RECO d2-predict and step0 (rpd_d2s0, generated from P0's fetch), the fetch:"
FETCH_HEADER_NEW = "# RPD-RECO d2-predict and step0 for e1 (rpd_d2s0, generated from d2s0-20261124's fetch), the fetch:"
LAUNCH_HEADER_OLD = (
    "# RPD-RECO d2-predict and step0 (rpd_d2s0, generated from P0's launcher): the Mac-side launcher, in"
    " rpd_mnv_check2_launch.sh's pattern. connect requires cov2d's fresh ack file, kept byte for byte in the local"
    " session record."
)
LAUNCH_HEADER_NEW = (
    "# RPD-RECO d2-predict and step0 for e1 (rpd_d2s0, generated from d2s0-20261124's launcher with flux4's ack guard):"
    " the Mac-side launcher, in rpd_mnv_check2_launch.sh's pattern. connect requires the three-lane ack file (cov2d,"
    " tier3-design, minerva-lib), kept byte for byte in the local session record."
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def dump(value: dict) -> bytes:
    return (json.dumps(value, indent=1, sort_keys=True, ensure_ascii=True) + "\n").encode()


def replace(text: str, old: str, new: str, count: int, what: str) -> str:
    found = text.count(old)
    assert found == count, f"{what}: {found} occurrences of {old[:70]!r}, expected {count}"
    return text.replace(old, new)


def lift(text: str, start: str, end: str) -> str:
    lines = text.splitlines(keepends=True)
    first = [i for i, line in enumerate(lines) if line.startswith(start)]
    assert len(first) == 1, (start, first)
    last = [i for i, line in enumerate(lines) if i >= first[0] and line.startswith(end)]
    assert last, (start, end)
    return "".join(lines[first[0] : last[0] + 1])


def pins_block(connect: str) -> str:
    start = connect.index("done <<'PINS'\n") + len("done <<'PINS'\n")
    return connect[start : connect.index("PINS\n", start)]


def runner_of(connect: str) -> str:
    assert connect.count("<<'RUNNER'\n") == 1 and connect.count("\nRUNNER\n") == 1
    return connect.split("<<'RUNNER'\n", 1)[1].split("\nRUNNER\n", 1)[0] + "\n"


def load(path: Path, key: str):
    assert sha(path.read_bytes()) == SHA[key], key
    spec = importlib.util.spec_from_file_location(key, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    old = {
        "connect": (D2S0 / "rpd_d2s0_connect.sh").read_bytes(),
        "fetch": (D2S0 / "rpd_d2s0_fetch.sh").read_bytes(),
        "launch": (D2S0 / "rpd_d2s0_launch.sh").read_bytes(),
        "checks": (D2S0 / "tools" / "d2s0_checks.py").read_bytes(),
        "expected": (D2S0 / "tools" / "d2s0_expected.json").read_bytes(),
        "fence": (D2S0 / "tools" / "fence_overlap.py").read_bytes(),
        "supervise": (D2S0 / "tools" / "p0_supervise.py").read_bytes(),
        "config": (D2S0 / "production-config.ready.json").read_bytes(),
        "p0e1_config": (P0E1 / "production-config.ready.json").read_bytes(),
        "p0e1_connect": (P0E1 / "rpd_p0_connect.sh").read_bytes(),
        "p0e1_expected": (P0E1 / "tools" / "p0_expected.json").read_bytes(),
        "p0e1_fence": (P0E1 / "tools" / "fence_overlap.py").read_bytes(),
        "p0_record": (P0E1_RECORDS / "p0.json").read_bytes(),
        "pins_gz": (P0E1_RECORDS / "pins.json.gz").read_bytes(),
    }
    for key, data in old.items():
        assert sha(data) == SHA[key], key
    pins_record = gzip.decompress(old["pins_gz"])
    assert sha(pins_record) == SHA["pins_record"]
    p0 = json.loads(old["p0_record"])
    pins = json.loads(pins_record)
    assert p0["step"] == "p0" and p0["status"] == "PASS" and p0["dry_run"] is False
    assert p0["predecessor_sha256"] == SHA["pins_record"] and p0["code_sha256"] == RECO_MODULE
    assert p0["config_sha256"] == SHA["p0e1_config"] and p0["result"]["C-JOIN"]["part2"]["status"] == "PASS"
    assert pins["step"] == "pins" and pins["status"] == "PASS" and pins["dry_run"] is False
    assert pins["config_sha256"] == SHA["p0e1_config"] and pins["code_sha256"] == RECO_MODULE
    gen3 = load(RECO / "flux3-20261123" / "tools" / "gen_flux3.py", "gen3")
    gen4 = load(RECO / "flux4-20261126" / "tools" / "gen_flux4.py", "gen4")
    # d2s0's config is P0's, unchanged; p0e1's config is the one p0e1's records name.
    cfg = old["p0e1_config"]

    # 1. The expected values: p0e1's 14 inputs and 40 stat entries, plus p0e1's two run records.
    p0e1_expected = json.loads(old["p0e1_expected"])
    d2s0_expected = json.loads(old["expected"])
    assert set(d2s0_expected["inputs"]) - {f"{OLD_P0_ROOT}/run/p0.json", f"{OLD_P0_ROOT}/run/pins.json"} == set(
        json.loads((RECO / "p0-20261123" / "tools" / "p0_expected.json").read_text())["inputs"]
    ), "d2s0's inputs are P0's 14 plus P0's two records"
    inputs = dict(p0e1_expected["inputs"])
    inputs[f"{P0_ROOT}/run/p0.json"] = SHA["p0_record"]
    inputs[f"{P0_ROOT}/run/pins.json"] = SHA["pins_record"]
    assert len(inputs) == 16 and len(p0e1_expected["stat"]) == 40
    expected = dump({"inputs": inputs, "stat": p0e1_expected["stat"]})

    # 2. The checks tool: d2s0's, with flux4's records, p0e1's records and the probe's stat values in its wording.
    checks = old["checks"].decode()
    checks = replace(
        checks,
        "inputs  Reads each in-place input (EXPECTED_JSON \"inputs\": path -> sha256): flux3's records and factor products, from\n"
        "        the committed run-61861637 records, and P0's run/pins.json and run/p0.json, from the committed P0 records.",
        "inputs  Reads each in-place input (EXPECTED_JSON \"inputs\": path -> sha256): flux4's records and factor products, from\n"
        "        the committed run-62051670 records, and p0e1's run/pins.json and run/p0.json, from the committed run-20261127\n"
        "        records.",
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
    assert "flux3" not in checks and "61861637" not in checks
    checks_bytes = checks.encode()

    # 3. The fence copy: p0e1's, at the new root.
    fence = replace(
        old["p0e1_fence"].decode(), f'WRITE_ROOTS = ("{P0E1_FENCE_ROOT}",', f'WRITE_ROOTS = ("{ROOT}",', 1, "fence root"
    ).encode()

    # 4. The connect.
    connect = old["connect"].decode()
    connect = replace(connect, b64(old["config"]), b64(cfg), 1, "connect config blob")
    connect = replace(connect, b64(old["fence"]), b64(fence), 1, "connect fence blob")
    connect = replace(connect, b64(old["checks"]), b64(checks_bytes), 1, "connect checks blob")
    connect = replace(connect, b64(old["expected"]), b64(expected), 1, "connect expected blob")
    assert connect.count(b64(old["supervise"])) == 1, "connect supervisor blob"
    connect = replace(connect, HEADER_OLD, HEADER_NEW, 1, "connect header")
    connect = replace(connect, SHA["config"], sha(cfg), 2, "connect config sha")
    connect = replace(connect, SHA["fence"], sha(fence), 1, "connect fence sha")
    connect = replace(connect, SHA["checks"], sha(checks_bytes), 1, "connect checks sha")
    connect = replace(connect, SHA["expected"], sha(expected), 1, "connect expected sha")
    connect = replace(connect, OLD_S, S, 1, "connect clone sha")
    connect = replace(connect, OLD_ROOT, ROOT, 51, "connect root")
    connect = replace(connect, f"{OLD_P0_ROOT}/run/$f", f"{P0_ROOT}/run/$f", 1, "connect stage source")
    connect = replace(connect, SHA["old_pins_record"], SHA["pins_record"], 1, "connect stage pins sha")
    connect = replace(connect, SHA["old_p0_record"], SHA["p0_record"], 1, "connect stage p0 sha")
    p0e1_connect = old["p0e1_connect"].decode()
    mine, theirs = pins_block(connect), pins_block(p0e1_connect)
    moved = 0
    for a, b in zip(mine.splitlines(keepends=True), theirs.splitlines(keepends=True), strict=True):
        assert a.split(" ", 1)[1] == b.split(" ", 1)[1], (a, b)
        if a != b:
            connect = replace(connect, a, b, 2, f"connect pin {b.split()[1]}")
            moved += 1
    assert moved == 4, moved
    connect = replace(connect, "(cov2d|t2a|rpd)", "(cov2d|t2a|rpd|geanttw)", 1, "sacct family")
    connect = replace(connect, "cov2d/t2a/rpd", "cov2d/t2a/rpd/geanttw", 2, "sacct family labels")
    connect = replace(connect, "cov2d*, t2a*, rpd* refuse", "cov2d*, t2a*, rpd*, geanttw* refuse", 1, "fence title")
    start, end = 'echo "== 2. the fence', 'echo "FENCE: clear"'
    assert lift(connect, start, end) == lift(p0e1_connect, start, end), "p0e1's (flux4's) sacct block"
    connect = replace(
        connect,
        "#   2. the sacct fence (P0's block, flux3's tightened one, byte for byte);",
        "#   2. the sacct fence (p0e1's block, flux4's: cov2d*, t2a*, rpd*, geanttw*, byte for byte);",
        1,
        "connect header fence",
    )
    connect = replace(
        connect,
        "#      inputs): flux3's extract, custody record and 12 factor products, and P0's run/pins.json and run/p0.json. Then\n"
        "#      P0's two records are staged",
        "#      inputs): flux4's extract, custody record and 12 factor products, and p0e1's run/pins.json and run/p0.json.\n"
        "#      Then p0e1's two records are staged",
        1,
        "connect header inputs",
    )
    connect = replace(
        connect,
        "#   6. a fresh stat (never an open) of the three gen2thin flux files and the 24 dumps against S1 (stat-d2s0.txt);",
        "#   6. a fresh stat (never an open) of the three gen2thin flux files, the 24 dumps, the 12 RDX omnifiles and the\n"
        "#      true-energy sidecar against the records (S1's 27, the sidecar probe's 13) (stat-d2s0.txt);",
        1,
        "connect header stat",
    )
    connect = replace(
        connect,
        "#   4. the READY config (P0's, unchanged), written from this script",
        "#   4. the READY config (p0e1's, unchanged), written from this script",
        1,
        "connect header config",
    )
    connect = replace(
        connect,
        "the in-place inputs (flux3's records and products, P0's two records, O_NOATIME); P0's records staged",
        "the in-place inputs (flux4's records and products, p0e1's two records, O_NOATIME); p0e1's records staged",
        1,
        "connect step 5 title",
    )
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
    # The DRY_RUN_SCOPE citation in the header moves with the code: :3058-3062 at 7302cc1d, :3391-3395 at S (agy note).
    connect = replace(connect, "(fd_rpd_reco.py DRY_RUN_SCOPE, :3058-3062)", "(fd_rpd_reco.py DRY_RUN_SCOPE, :3391-3395 at S)", 1, "connect DRY_RUN_SCOPE cite")
    body = connect.replace(HEADER_NEW, "")
    for bad in ("squeue", "sbatch", OLD_ROOT, OLD_P0_ROOT, OLD_S, "flux3", "61861637", SHA["config"],
                SHA["old_p0_record"], SHA["old_pins_record"]):
        assert bad not in body, (bad, body.count(bad))
    assert runner_of(connect) == runner_of(old["connect"].decode()).replace(OLD_ROOT, ROOT).replace(
        SHA["config"], sha(cfg)
    ), "the runner changes only by its root and the config digest"
    python_calls = [line for line in connect.splitlines() if '"$PY"' in line or '"$MAT_PYTHON"' in line]
    assert python_calls and all(" -B " in line for line in python_calls), python_calls

    # 5. The fetch.
    fetch = old["fetch"].decode()
    fetch = replace(fetch, FETCH_HEADER_OLD, FETCH_HEADER_NEW, 1, "fetch header")
    fetch = replace(fetch, OLD_ROOT, ROOT, 3, "fetch root")
    for bad in ("squeue", "python", OLD_ROOT, "flux3"):
        assert bad not in fetch, (bad, fetch.count(bad))

    # 6. The launcher: d2s0's, re-pinned, with flux4's three-lane ack guard.
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
        "tools/d2s0_expected.json": expected,
        "tools/d2s0_checks.py": checks_bytes,
        "tools/p0_supervise.py": old["supervise"],
        "tools/fence_overlap.py": fence,
        "rpd_d2s0_connect.sh": connect.encode(),
        "rpd_d2s0_fetch.sh": fetch.encode(),
        "rpd_d2s0_launch.sh": launch.encode(),
    }
    for name, data in outputs.items():
        (OUT / name).write_bytes(data)
        print(sha(data), name)
    print(sha(runner_of(connect).encode()), "(runner, as the connect's heredoc writes it)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
