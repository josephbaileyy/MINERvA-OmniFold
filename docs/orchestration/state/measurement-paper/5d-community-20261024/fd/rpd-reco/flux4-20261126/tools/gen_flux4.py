"""Generate the true-Eν flux rerun at 2415e8d6 (rpd_flux4) from flux3's committed package, by counted replacements.

usage: python3 -I -B gen_flux4.py REPO
  REPO  a checkout of this repository with S (2415e8d6, #1308's merge) in its history; pinned files are read at S
        through `git show`, never from the working tree.

RPD-RECO amendment 1 (#1300) and its code (#1308): the flux factors are evaluated at true Eν from RDX's truthx
sidecar, with C-JOIN part 1 in flux-extract. The director accepted these defaults on 2026-11-26:
  1. the clone moves to S; every one of flux3's 14 pins is re-read at S, and only the files #1308 changed may move;
  2. the config: flux3's d797183b with the two record paths moved to ROOT and a new `true_energy` block (the sidecar's
     path and sha256, lat_zero's sha256 as `npz_sha256`, and the 12 RDX omnifiles with c2's sha256s); the leaf diff is
     asserted to be exactly that;
  3. the fetch drops flux3's byte identity with flux2 (step 2b: the factors now change by design) and checks flux4's own
     true_energy join record instead: status PASS, the pinned sidecar and lat_zero digests, the spot rows for all 12
     playlists, and each product's `energy` column finite, positive and of its block's length; a miss exits 15 after
     the records are sent (a STOP to the director, not a reading);
  4. the step-2 sacct fence also watches geanttw* jobs (no e1 connect while a geanttw_ job is live), and the
     launcher's connect takes one ack file of three lines, ACK-UTC <time> <lane>, for cov2d, tier3-design and
     minerva-lib, each at most 6 h old, under flux3's byte-exact guard.
Every replacement must match its stated count. flux3's generator is loaded (sha256-pinned) for its block constants.
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
FLUX3 = OUT.parent / "flux3-20261123"
OLD_ROOT = "/pscratch/sd/j/josephrb/rpd-reco-flux3-20261123"
ROOT = "/pscratch/sd/j/josephrb/rpd-reco-flux4-20261126"
OLD_S = "6896e7871421469ce72c6b93188d2d1a55c82ec6"
S = "2415e8d66d1a9160e724d426eaeb54d458d4b4f7"
SHA = {
    "config": "d797183bb5d459285224e4ee4d3fc8a0cc6cd64b136745ebf182bd716800e229",
    "connect": "0a50f7db15df9bb31fe574c588a43c7f455609bb5f34e0e5acadd66aa062fbb4",
    "fetch": "40645b69f02ee67db830fc9f95e3c69bf79cf46a9db4fbada26ce9da7ccf0f2e",
    "launch": "91ae3a6a35c97040cfc444b4b91b29e63682ae80bd9221f1a2e71e85470459f6",
    "fence": "f6541713e2cd4c8b342da5b76f59eec0662555e1cbe97da9ad95a52995594b35",
    "gen3": "f760c20d8c739ba4cf1a181ef1a970fad48e6c80ba207c8ffc1376f26527eccc",
}
# The pins #1308 may move (its diff: the code, the custody, the tests and the mutation harness); any other pin must be
# unchanged at S.
MAY_MOVE = {
    "nd-unfolding/fd_rpd_reco.py",
    "nd-unfolding/fd_rpd_reco_custody.py",
    "nd-unfolding/tests/test_fd_rpd_reco.py",
    "nd-unfolding/tests/fd_rpd_reco_mutation.py",
}
PLAYLISTS = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")
SIDECAR = "/pscratch/sd/j/josephrb/rdx-20261112b/out/dumps/truthx_RDX_ALL.npz"
SIDECAR_SHA = "641ba34c5ebde6d1881c705b862fab144a6fbb8a58ef3d84e59f1c8ba030a79e"
LAT_ZERO_SHA = "6ca02c3d8b09dfd168b5184c03d433a7bd65749f5f6fc4cefecdbed7b6ce052f"
OMNI = "/pscratch/sd/j/josephrb/rdx-20261112b/out/evloop/runEventLoopOmniFold_RDX_{}.root"
C2 = (
    "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/redump-f12i-20261112/run-c2-20261117/"
    "c2.session.txt"
)
OLD_HEADER = "rpd_flux3 (generated from rpd_flux2 at 6896e787, the director's ruling (A), 2026-11-23)"
NEW_HEADER = "rpd_flux4 (generated from the flux3 package at 2415e8d6, RPD-RECO amendment 1, the director's acceptance 2026-11-26)"
assert "rpd_flux3" not in NEW_HEADER and "6896e787" not in NEW_HEADER

SIDECAR_BYTES = 2364943114  # the sidecar probe's lstat and bytes read (sidecar-probe-20261126/run-20261126/probe.json)
SIDECAR_STAT = (
    'echo "== 5b. the true-energy sidecar, stat only (amendment 1 section 8; never opened, and a symlink refuses)"\n'
    f"sz=$(stat -c '%F|%s' {SIDECAR}) || {{ echo \"STOP: {SIDECAR} cannot be stat'ed (purged or moved?)\"; finish 3; }}\n"
    'echo "sidecar $sz"\n'
    f'[ "$sz" = "regular file|{SIDECAR_BYTES}" ] || {{ echo "STOP: the sidecar is not a regular file of {SIDECAR_BYTES} bytes"; finish 3; }}\n'
)
FETCH_TRUE_ENERGY = r"""echo "== 2b. the true-energy join record (C-JOIN part 1, amendment 1; in place of flux3's product identity check)"
"$MAT_PYTHON" -I -c '
import json, sys
import numpy as np
side, lat = sys.argv[1], sys.argv[2]
pls = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")
bad = []
try:
    te = json.load(open("run/flux-extract.json")).get("true_energy") or {}
except Exception as e:
    te = {}
    bad.append("flux-extract.json unreadable: %s" % e)
src = te.get("source") or {}
blocks = te.get("block_rows") or {}
spots = te.get("spots") or {}
if te.get("status") != "PASS":
    bad.append("status %r" % te.get("status"))
if src.get("sha256") != side:
    bad.append("source sha256 %r is not the pinned sidecar" % src.get("sha256"))
if src.get("npz_sha256") != lat:
    bad.append("npz_sha256 %r is not lat_zero" % src.get("npz_sha256"))
if sorted(spots) != sorted(pls) or sorted(blocks) != sorted(pls):
    bad.append("spot rows or block rows do not name the 12 playlists")
for pl in pls:
    s = spots.get(pl) or {}
    n = len(s.get("rows", []))
    if n < 2 or any(len(s.get(k, [])) != n for k in ("run", "subrun", "event", "energy_GeV")):
        bad.append("%s: spot rows malformed" % pl)
    try:
        with np.load("run/flux-factors-%s.npz" % pl, allow_pickle=False) as z:
            e = np.asarray(z["energy"]) if "energy" in z.files else None
    except Exception as x:
        e = None
        bad.append("%s: product unreadable: %s" % (pl, x))
    if e is None or e.ndim != 1 or e.dtype != np.float64 or len(e) != blocks.get(pl):
        bad.append("%s: energy column missing, not float64, or not %r rows" % (pl, blocks.get(pl)))
    elif not (np.all(np.isfinite(e)) and np.all(e > 0)):
        bad.append("%s: energy column not finite and positive" % pl)
    else:
        print("true-energy %s rows %d spots %d median %.4f GeV" % (pl, len(e), n, float(np.median(e))))
print("TRUE_ENERGY RECORD: " + ("PASS" if not bad else "FAIL: " + "; ".join(bad)))
sys.exit(1 if bad else 0)
' """ + SIDECAR_SHA + " " + LAT_ZERO_SHA + r"""
terc=$?
echo "true-energy record check rc=$terc"
echo "== 3. the protected read"
"""
FETCH_TRUE_ENERGY_EXIT = (
    '[ "$terc" -eq 0 ] || { echo "STOP: the true-energy join record did not hold; a STOP to the director, not a '
    'reading; the records were sent"; finish 15; }\n'
)

LAUNCH_ACK3 = r"""if [ "$MODE" = connect ]; then
  ACK=${2:-}
  [ -n "$ACK" ] && [ -f "$ACK" ] || { echo "STOP: connect needs the three-lane ack file (ack.txt) as its fourth argument"; exit 9; }
  A="$F/ack.txt"
  bad_ack() { rm -f -- "$A"; echo "STOP: $1"; exit 9; }
  # One byte-exact snapshot: the copy made here is what is validated below and what stays in the session record.
  cp "$ACK" "$A" || bad_ack "ack.txt could not be copied into the session"
  LC_ALL=C tr -d '\000' < "$A" | cmp -s - "$A" || bad_ack "ack.txt contains NUL bytes"
  now=$(date -u +%s) && [[ $now =~ ^[0-9]+$ ]] || bad_ack "the clock could not be read"
  n=0
  for lane in cov2d tier3-design minerva-lib; do  # the overlap owner, the sidecar's owner, geanttw's lane, in order
    n=$((n + 1))
    line=$(sed -n "${n}p" "$A")
    [[ $line =~ ^ACK-UTC\ ([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z)\ ([a-z0-9-]+)$ ]] || bad_ack "ack.txt line $n is not 'ACK-UTC <YYYY-MM-DDTHH:MM:SSZ> $lane'"
    when=${BASH_REMATCH[1]}
    who=${BASH_REMATCH[2]}
    [ "$who" = "$lane" ] || bad_ack "ack.txt line $n names '$who', not $lane"
    ack_s=$(TZ=UTC date -j -f '%Y-%m-%dT%H:%M:%SZ' "$when" +%s 2>/dev/null) || bad_ack "ack.txt line $n's time does not parse: $when"
    [ "$(TZ=UTC date -j -r "$ack_s" +%Y-%m-%dT%H:%M:%SZ)" = "$when" ] || bad_ack "ack.txt line $n's time is not a real UTC time: $when"
    [[ $ack_s =~ ^[0-9]+$ ]] || bad_ack "ack.txt line $n's time did not convert: $when"
    age=$(( now - ack_s ))
    [ "$age" -ge -300 ] || bad_ack "$lane's ack time is in the future: $when"
    [ "$age" -le 21600 ] || bad_ack "$lane's ack is older than 6 h ($when, $age s)"
    echo "$lane ack $when (age $age s)"
  done
  [ "$(sed -n '4,$p' "$A" | grep -c '[^[:space:]]')" -ge 1 ] || bad_ack "ack.txt carries no ack text after its three ACK-UTC lines"
  echo "three acks recorded byte for byte in the session as ack.txt"
fi
"""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dump(config: dict) -> bytes:
    return (json.dumps(config, indent=1, sort_keys=True, ensure_ascii=True) + "\n").encode()


def replace(text: str, old: str, new: str, count: int, what: str) -> str:
    found = text.count(old)
    assert found == count, f"{what}: {found} occurrences of {old[:70]!r}, expected {count}"
    return text.replace(old, new)


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


def omnifile_pins(repo: Path) -> dict[str, dict[str, str]]:
    """The 12 omnifile sha256s from RDX's c2 record at S (its lines 1150-1161, the amendment's pins)."""
    lines = git_show(repo, C2).decode().splitlines()
    rows = lines[1149:1161]
    pins = {}
    for playlist, row in zip(PLAYLISTS, rows):
        digest, name = row.split()
        assert name == f"runEventLoopOmniFold_RDX_{playlist}.root" and len(digest) == 64, (playlist, row)
        pins[playlist] = {"path": OMNI.format(playlist), "sha256": digest}
    return pins


def main() -> int:
    repo = Path(sys.argv[1])
    old = {
        "config": (FLUX3 / "production-config.ready.json").read_bytes(),
        "connect": (FLUX3 / "rpd_flux3_connect.sh").read_bytes(),
        "fetch": (FLUX3 / "rpd_flux3_fetch.sh").read_bytes(),
        "launch": (FLUX3 / "rpd_flux3_launch.sh").read_bytes(),
        "fence": (FLUX3 / "tools" / "fence_overlap.py").read_bytes(),
    }
    for key, data in old.items():
        assert sha(data) == SHA[key], key
    gen3_path = FLUX3 / "tools" / "gen_flux3.py"
    assert sha(gen3_path.read_bytes()) == SHA["gen3"], "gen_flux3.py"
    spec = importlib.util.spec_from_file_location("gen_flux3", gen3_path)
    gen3 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen3)

    # 1. The config: flux3's, with the two record paths moved to ROOT and the true_energy block added.
    config = json.loads(old["config"])
    assert dump(config) == old["config"] and "true_energy" not in config
    new = json.loads(old["config"])
    for key in ("flux_extract", "flux_custody"):
        assert new[key]["path"].startswith(OLD_ROOT + "/run/") and new[key]["sha256"] is None, key
        new[key]["path"] = ROOT + new[key]["path"][len(OLD_ROOT) :]
    new["true_energy"] = {
        "path": SIDECAR,
        "sha256": SIDECAR_SHA,
        "npz_sha256": LAT_ZERO_SHA,
        "omnifiles": omnifile_pins(repo),
    }
    a, b = leaves(config), leaves(new)
    changed = {k for k in a if k in b and a[k] != b[k]}
    added = set(b) - set(a)
    assert set(a) <= set(b) and changed == {"/flux_extract/path", "/flux_custody/path"}, changed
    assert added == {"/true_energy/path", "/true_energy/sha256", "/true_energy/npz_sha256"} | {
        f"/true_energy/omnifiles/{p}/{k}" for p in PLAYLISTS for k in ("path", "sha256")
    }, sorted(added)
    cfg = dump(new)

    # 2. The pins at S: every one of flux3's 14 re-read; only #1308's files may move.
    connect = old["connect"].decode()
    first = connect.index("done <<'PINS'\n") + len("done <<'PINS'\n")
    block = connect[first : connect.index("PINS\n", first)]
    rows = [row.split(" ", 1) for row in block.splitlines()]
    assert len(rows) == 14, len(rows)
    moved = {}
    for want, path in rows:
        got = sha(git_show(repo, path))
        if got != want:
            assert path in MAY_MOVE, f"{path} at S is {got}; flux3 pinned {want}, and #1308 does not change it"
            moved[path] = (want, got)
    assert set(moved) == MAY_MOVE, sorted(moved)

    # 3. The fence copy.
    fence = replace(
        old["fence"].decode(), f'WRITE_ROOTS = ("{OLD_ROOT}",', f'WRITE_ROOTS = ("{ROOT}",', 1, "fence root"
    )
    # custody prepare at S also stages the true-energy sidecar (fd_rpd_reco_custody.py at 2415e8d6, the TRUE_ENERGY_PIN
    # block): the fence must list it among the originals it checks against cov2d's protected paths (rule (c)).
    fence = replace(
        fence,
        "flux_source; every path in the pins file;",
        "flux_source; the true-energy sidecar (true_energy.path, staged by prepare since #1308); every path in the\n"
        "pins file;",
        1,
        "fence docstring",
    )
    fence = replace(
        fence,
        '    for line in local(config["pins"]["path"]).read_text().splitlines():\n',
        '    if isinstance(config.get("true_energy"), dict):  # prepare stages it at 2415e8d6 (#1308)\n'
        '        reads.append(("true_energy", config["true_energy"]["path"]))\n'
        '    for line in local(config["pins"]["path"]).read_text().splitlines():\n',
        1,
        "fence true-energy original",
    ).encode()

    # 4. The connect.
    connect = replace(connect, b64(old["config"]), b64(cfg), 1, "connect config blob")
    connect = replace(connect, b64(old["fence"]), b64(fence), 1, "connect fence blob")
    connect = replace(connect, OLD_HEADER, NEW_HEADER, 1, "connect header")
    connect = replace(connect, SHA["config"], sha(cfg), 3, "connect config sha")
    connect = replace(connect, SHA["config"][:8] + "...", sha(cfg)[:8] + "...", 1, "connect config label")
    connect = replace(connect, SHA["fence"], sha(fence), 1, "connect fence sha")
    connect = replace(connect, OLD_S, S, 2, "connect clone sha")
    connect = replace(connect, OLD_S[:8], S[:8], 2, "connect clone sha label")
    connect = replace(connect, OLD_ROOT, ROOT, 38, "connect root")
    connect = replace(connect, '"20261123" a fixed label', '"20261126" a fixed label', 1, "connect root label")
    connect = replace(connect, "rpd_flux3", "rpd_flux4", 12, "connect job name")
    connect = replace(connect, "rpd-flux3", "rpd-flux4", 1, "connect finish label")
    for path, (want, got) in moved.items():
        connect = replace(connect, f"{want} {path}\n", f"{got} {path}\n", 2, f"connect pin {path}")
    connect = replace(connect, "(cov2d|t2a|rpd)", "(cov2d|t2a|rpd|geanttw)", 1, "sacct family")
    connect = replace(connect, "cov2d/t2a/rpd", "cov2d/t2a/rpd/geanttw", 2, "sacct family labels")
    connect = replace(connect, "cov2d*, t2a*, rpd* refuse", "cov2d*, t2a*, rpd*, geanttw* refuse", 1, "fence title")
    # Amendment 1 section 8: "The flux4 and P0 connects stat each one first." The sidecar, stat only (no open, so no
    # atime moves), must exist as a regular file of the size the probe read (2026-11-26) before the job is written.
    connect = replace(connect, 'echo "== 6. the job"\n', SIDECAR_STAT + 'echo "== 6. the job"\n', 1, "connect sidecar stat")
    connect = replace(
        connect,
        "named cov2d*, t2a* or rpd* refuses (ruling (a));",
        "named cov2d*, t2a*, rpd* or geanttw* refuses (ruling (a); geanttw*, the director 2026-11-26);",
        1,
        "connect header fence families",
    )
    connect = replace(
        connect,
        "#   6. the job script, written from this script, then sbatch;",
        "#   5b. the true-energy sidecar, stat only (amendment 1 section 8): a regular file of the probe's size, else STOP;\n"
        "#   6. the job script, written from this script, then sbatch;",
        1,
        "connect header step 5b",
    )
    body = connect.replace(NEW_HEADER, "")
    for bad in ("squeue", OLD_ROOT, OLD_S, "rpd_flux3", "rpd-flux3", "flux2"):
        assert bad not in body, (bad, body.count(bad))

    # 5. The fetch.
    fetch = old["fetch"].decode()
    fetch = replace(fetch, OLD_HEADER, NEW_HEADER, 1, "fetch header")
    fetch = replace(fetch, OLD_ROOT, ROOT, 9, "fetch root")
    fetch = replace(fetch, "rpd_flux3", "rpd_flux4", 3, "fetch job name")
    fetch = replace(fetch, "rpd-flux3", "rpd-flux4", 18, "fetch labels")
    i = fetch.index('echo "== 2b. identity with flux2')
    j = fetch.index('echo "== 3. the protected read"\n') + len('echo "== 3. the protected read"\n')
    assert fetch.count('echo "== 2b.') == 1 and fetch[i:j].count("\n") == 21, fetch[i:j].count("\n")
    fetch = fetch[:i] + FETCH_TRUE_ENERGY + fetch[j:]
    fetch = replace(fetch, gen3.FETCH_EXIT_NEW, FETCH_TRUE_ENERGY_EXIT, 1, "fetch identity exit")
    fetch = replace(
        fetch,
        "#      A factor product that is not byte-identical to flux2's (step 2b) exits 15, after the records are sent.",
        "#      A true-energy join record that does not hold (step 2b: status PASS, the pinned sidecar and lat_zero\n"
        "#      digests, spot rows for the 12 playlists, each product's energy column) exits 15, after the records are sent.",
        1,
        "fetch exit list",
    )
    body = fetch.replace(NEW_HEADER, "")
    for bad in ("squeue", OLD_ROOT, "rpd_flux3", "rpd-flux3", "flux2", "FLUX2", "idbad"):
        assert bad not in body, (bad, body.count(bad))

    # 6. The launcher.
    launch = old["launch"].decode()
    launch = replace(launch, OLD_HEADER, NEW_HEADER, 1, "launch header")
    launch = replace(launch, SHA["connect"], sha(connect.encode()), 1, "launch connect sha")
    launch = replace(launch, SHA["fetch"], sha(fetch.encode()), 1, "launch fetch sha")
    launch = replace(launch, OLD_ROOT, ROOT, 1, "launch root")
    launch = replace(launch, "rpd_flux3", "rpd_flux4", 9, "launch names")
    launch = replace(launch, "rpd-flux3", "rpd-flux4", 1, "launch staging")
    launch = replace(launch, gen3.LAUNCH_ACK, LAUNCH_ACK3, 1, "launch ack guard")
    body = launch.replace(NEW_HEADER, "")
    for bad in ("squeue", "rpd_flux3", "rpd-flux3", "flux2", "cov2d's ack"):
        assert bad not in body, (bad, body.count(bad))

    outputs = {
        "production-config.ready.json": cfg,
        "tools/fence_overlap.py": fence,
        "rpd_flux4_connect.sh": connect.encode(),
        "rpd_flux4_fetch.sh": fetch.encode(),
        "rpd_flux4_launch.sh": launch.encode(),
    }
    for name, data in outputs.items():
        (OUT / name).write_bytes(data)
        print(sha(data), name)
    print("pins moved at S:", *(f"{p}: {w[:8]} -> {g[:8]}" for p, (w, g) in sorted(moved.items())), sep="\n  ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
