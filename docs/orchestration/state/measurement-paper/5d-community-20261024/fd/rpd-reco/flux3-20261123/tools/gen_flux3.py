"""Generate the flux rerun at 6896e787 (rpd_flux3) from flux2's committed package, by counted replacements.

usage: python3 -I -B gen_flux3.py REPO
  REPO  a checkout of this repository with S (6896e787, #1251's merge) in its history; pinned files are read at S
        through `git show`, never from the working tree.

The director's ruling (A) of 2026-11-23: flux2's custody receipt binds custody 867822e3 (binding 2's, with the
squeue call), and P0 at 6896e787 requires the receipt's custody sha to equal the checkout's (fd_rpd_reco.py:1994-2013),
so the flux stage is rerun at 6896e787, whose custody (634670b3) reads sacct only. Everything from flux3 on runs on it.
  1. root ROOT, clone S, the pin list with custody 634670b3 and three test pins (test_fd_rpd_reco.py and
     fd_rpd_reco_fence_mutation.py at their new shas, fd_rpd_reco_mutation.py at binding 2's f2612369, unchanged at S),
     job rpd_flux3 (an rpd* name the fences watch), shared QOS, --time 01:00:00;
  2. the config: flux2's 7ebc2aa9 with only the two record paths moved to ROOT;
  3. the fetch records whether the 12 factor products are byte-identical to flux2's (run-61806073's records), and
     exits 15 if any differs (a STOP to the director, not a reading);
  4. the launcher's connect requires cov2d's ack file (ACK-UTC first line, at most 6 h old), as P0's does;
  5. the step-2 sacct fence tightens flux2's block: an empty or padded JobName, or an empty State, refuses, and the
     family match is case-insensitive (P0 finding 8, the director's acceptance).
Without job.rc, the fetch uses sacct's state only from a successful call with one row for the job. Every
replacement must match its stated count.
"""

from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
FLUX2 = OUT.parent / "flux2-20261122"
RUN2 = FLUX2 / "run-61806073"
OLD_ROOT = "/pscratch/sd/j/josephrb/rpd-reco-flux2-20261122"
ROOT = "/pscratch/sd/j/josephrb/rpd-reco-flux3-20261123"
OLD_S = "763ab4ddcea2d2d3dce56138f8aa7ae7fab4bbe6"
S = "6896e7871421469ce72c6b93188d2d1a55c82ec6"
SHA = {
    "config": "7ebc2aa9e254ec99535fab2416617e069f3a97621fa69c1c44b24b31a38c4fa9",
    "connect": "7a362f34dd00b2422c91ff542366d9cc120c8dedbde730da5592b171bac73fd2",
    "fetch": "d8f780c917b873a888ce2dd55d8f16f813018a5d4fd87211f24e5d23dea750fc",
    "launch": "c744061e6a1cbd589a032e91e81d3178b066faa336097a935e4f294486408487",
    "fence": "68e4033c8d4cbabe01ea6fdd1645f4ddfb42098a52a5d38c653f708cd80d1553",
    "extract": "e9ca74c7c42c60d1913104b95eaea26b239d87d3c984ed0d005de6ee400f8744",
    "old_custody": "867822e3cbf7063088717565d2be4e68ae3625cb24ce468255d98ba8fd59bdb5",
    "new_custody": "634670b33af6900eb9feb2c01748b0f107950e110382780db37b874ab77160d8",
    "mutation_harness": "f2612369997204d966107071fd6e9c0dc36aa75d3b7dd32a5e65212d27bd0eb3",
}
ADDED_PINS = (
    "nd-unfolding/tests/test_fd_rpd_reco.py",
    "nd-unfolding/tests/fd_rpd_reco_fence_mutation.py",
    "nd-unfolding/tests/fd_rpd_reco_mutation.py",
)
SACCT_OLD_MALFORMED = """  NF != 3 || $1 !~ /^[0-9]+([_+].*)?$/ { print "malformed: " $0; bad = 1; next }\n"""
SACCT_NEW_MALFORMED = (
    """  NF != 3 || $1 !~ /^[0-9]+([_+].*)?$/ || $2 == "" || $2 ~ /^[[:space:]]|[[:space:]]$/ || $3 !~ /[^[:space:]]/ """
    """{ print "malformed: " $0; bad = 1; next }\n"""
)
SACCT_OLD_FAMILY = (
    """  $2 ~ /^(cov2d|t2a|rpd)/ { n++; if (!(w[1] in term)) bad = 1 }\n"""
)
SACCT_NEW_FAMILY = (
    """  tolower($2) ~ /^(cov2d|t2a|rpd)/ { n++; if (!(w[1] in term)) bad = 1 }\n"""
)
FETCH_IDENTITY_ANCHOR = '  mrc=$?\nfi\necho "== 3. the protected read"\n'
FETCH_EXIT_ANCHOR = '[ "$mrc" -eq 0 ] && [ "$prc" -eq 0 ] && finish 0\n'
FETCH_EXIT_NEW = (
    '[ "$idbad" -eq 0 ] || { echo "STOP: $idbad factor product(s) differ from flux2\'s; a STOP to the director, '
    'not a reading; the records were sent"; finish 15; }\n'
)
# Without job.rc, sacct's state counts only from a successful call with exactly one row for the job (codex-school2,
# flux3 read, blocking 3); otherwise completion cannot be established and the fetch exits 10 (it can be run again).
FETCH_SACCT_OLD = 'if [ ! -f job.rc ]; then\n  case "$state" in\n'
FETCH_SACCT_NEW = r"""if [ ! -f job.rc ]; then
  parsed=$(printf '%s\n' "$acct" | awk -F'|' -v j="$jid" '$1 "" == j "" { n++; if (NF == 12 && $3 ~ /[^[:space:]]/) { ok++; split($3, w, " "); st = w[1]; nd = $8 } } END { if (n == 1 && ok == 1) { print st "|" nd; exit 0 } exit 1 }')
  urc=$?
  if [ "$arc" -ne 0 ] || [ "$urc" -ne 0 ] || [ -z "$parsed" ]; then
    echo "NOT FINISHED (cannot tell): no job.rc; the finish needs sacct rc 0 (got $arc), a parse rc 0 (got $urc) and exactly one well-formed row for job $jid"
    rm -f -- "$SELF"; exit 10
  fi
  state=${parsed%%|*}
  nodes=${parsed#*|}
  case "$state" in
"""
LAUNCH_ACK_ANCHOR = '[ "$(shasum -a 256 "$S" | cut -d\' \' -f1)" = "$SHA" ]'
LAUNCH_ACK = """if [ "$MODE" = connect ]; then
  ACK=${2:-}
  [ -n "$ACK" ] && [ -f "$ACK" ] || { echo "STOP: connect needs cov2d's ack file (ack.txt) as its fourth argument"; exit 9; }
  A="$F/ack.txt"
  bad_ack() { rm -f -- "$A"; echo "STOP: $1"; exit 9; }
  # One byte-exact snapshot: the copy made here is what is validated below and what stays in the session record.
  cp "$ACK" "$A" || bad_ack "ack.txt could not be copied into the session"
  LC_ALL=C tr -d '\\000' < "$A" | cmp -s - "$A" || bad_ack "ack.txt contains NUL bytes"
  first=$(head -n 1 "$A")
  [[ $first =~ ^ACK-UTC\\ ([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z)$ ]] || bad_ack "ack.txt's first line is not 'ACK-UTC <YYYY-MM-DDTHH:MM:SSZ>'"
  when=${BASH_REMATCH[1]}
  ack_s=$(TZ=UTC date -j -f '%Y-%m-%dT%H:%M:%SZ' "$when" +%s 2>/dev/null) || bad_ack "ack.txt's time does not parse: $when"
  [ "$(TZ=UTC date -j -r "$ack_s" +%Y-%m-%dT%H:%M:%SZ)" = "$when" ] || bad_ack "ack.txt's time is not a real UTC time: $when"
  [[ $ack_s =~ ^[0-9]+$ ]] || bad_ack "ack.txt's time did not convert: $when"
  now=$(date -u +%s) && [[ $now =~ ^[0-9]+$ ]] || bad_ack "the clock could not be read"
  age=$(( now - ack_s ))
  [ "$age" -ge -300 ] || bad_ack "ack.txt's time is in the future: $when"
  [ "$age" -le 21600 ] || bad_ack "cov2d's ack is older than 6 h ($when, $age s)"
  [ "$(sed -n '2,$p' "$A" | grep -c '[^[:space:]]')" -ge 1 ] || bad_ack "ack.txt carries no ack text after its first line"
  echo "cov2d ack $when (age $age s), recorded byte for byte in the session as ack.txt"
fi
"""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dump(config: dict) -> bytes:
    return (
        json.dumps(config, indent=1, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode()


def replace(text: str, old: str, new: str, count: int, what: str) -> str:
    found = text.count(old)
    assert (
        found == count
    ), f"{what}: {found} occurrences of {old[:70]!r}, expected {count}"
    return text.replace(old, new)


def git_show(repo: Path, path: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repo), "show", f"{S}:{path}"], check=True, capture_output=True
    ).stdout


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


def main() -> int:
    repo = Path(sys.argv[1])
    old = {
        "config": (FLUX2 / "production-config.ready.json").read_bytes(),
        "connect": (FLUX2 / "rpd_flux2_connect.sh").read_bytes(),
        "fetch": (FLUX2 / "rpd_flux2_fetch.sh").read_bytes(),
        "launch": (FLUX2 / "rpd_flux2_launch.sh").read_bytes(),
        "fence": (FLUX2 / "tools" / "fence_overlap.py").read_bytes(),
    }
    for key, data in old.items():
        assert sha(data) == SHA[key], key
    extract = (RUN2 / "records/run/flux-extract.json").read_bytes()
    assert sha(extract) == SHA["extract"]
    products = json.loads(extract)["factor_products"]
    assert len(products) == 12

    # 1. The config: flux2's, with the two record paths moved to ROOT.
    config = json.loads(old["config"])
    assert dump(config) == old["config"]
    new = json.loads(old["config"])
    for key in ("flux_extract", "flux_custody"):
        assert (
            new[key]["path"].startswith(OLD_ROOT + "/run/")
            and new[key]["sha256"] is None
        ), key
        new[key]["path"] = ROOT + new[key]["path"][len(OLD_ROOT) :]
    a, b = leaves(config), leaves(new)
    assert set(a) == set(b) and {k for k in a if a[k] != b[k]} == {
        "/flux_extract/path",
        "/flux_custody/path",
    }
    cfg = dump(new)

    # 2. The pins at S.
    pins_text = old["connect"].decode()
    assert (
        pins_text.count(f"{SHA['old_custody']} nd-unfolding/fd_rpd_reco_custody.py")
        == 2
    )
    custody_at_s = sha(git_show(repo, "nd-unfolding/fd_rpd_reco_custody.py"))
    assert custody_at_s == SHA["new_custody"], custody_at_s
    added = []
    for path in ADDED_PINS:
        added.append(f"{sha(git_show(repo, path))} {path}")
    assert added[2].startswith(SHA["mutation_harness"]), added[2]
    first = pins_text.index("done <<'PINS'\n") + len("done <<'PINS'\n")
    block = pins_text[first : pins_text.index("PINS\n", first)]
    for row in block.splitlines():
        want, path = row.split(" ", 1)
        if path == "nd-unfolding/fd_rpd_reco_custody.py":
            continue
        got = sha(git_show(repo, path))
        assert got == want, f"{path} at S is {got}, binding 2 pinned {want}"

    # 3. The fence copy.
    fence = replace(
        old["fence"].decode(),
        f'WRITE_ROOTS = ("{OLD_ROOT}",',
        f'WRITE_ROOTS = ("{ROOT}",',
        1,
        "fence root",
    ).encode()

    # 4. The connect.
    connect = old["connect"].decode()
    connect = replace(connect, b64(old["config"]), b64(cfg), 1, "connect config blob")
    connect = replace(connect, b64(old["fence"]), b64(fence), 1, "connect fence blob")
    connect = replace(connect, SHA["config"], sha(cfg), 3, "connect config sha")
    connect = replace(
        connect,
        SHA["config"][:8] + "...",
        sha(cfg)[:8] + "...",
        1,
        "connect config label",
    )
    connect = replace(connect, SHA["fence"], sha(fence), 1, "connect fence sha")
    connect = replace(connect, OLD_S, S, 2, "connect clone sha")
    connect = replace(connect, OLD_S[:8], S[:8], 2, "connect clone sha label")
    connect = replace(connect, OLD_ROOT, ROOT, 38, "connect root")
    connect = replace(
        connect,
        '"20261122" a fixed label',
        '"20261123" a fixed label',
        1,
        "connect root label",
    )
    connect = replace(connect, "rpd_flux2", "rpd_flux3", 13, "connect job name")
    connect = replace(connect, "rpd-flux2", "rpd-flux3", 1, "connect finish label")
    connect = replace(
        connect,
        f"{SHA['old_custody']} nd-unfolding/fd_rpd_reco_custody.py",
        f"{SHA['new_custody']} nd-unfolding/fd_rpd_reco_custody.py",
        2,
        "connect custody pin",
    )
    mat_pin = (
        "b056487e592e7704c2a98c14243b26f44c82821382837a263b75c169859cce0b docs/orchestration/state/"
        "measurement-paper/5d-community-20261024/fd/rpd-reco/code-audit-fix-20261106/MAT-DATA-DEPENDENCIES.json\nPINS\n"
    )
    connect = replace(
        connect,
        mat_pin,
        mat_pin[: -len("PINS\n")] + "\n".join(added) + "\nPINS\n",
        2,
        "connect pins",
    )
    connect = replace(
        connect, "and 11 sha256s", "and 14 sha256s", 1, "connect pin count"
    )
    connect = replace(
        connect, SACCT_OLD_MALFORMED, SACCT_NEW_MALFORMED, 1, "sacct malformed"
    )
    connect = replace(connect, SACCT_OLD_FAMILY, SACCT_NEW_FAMILY, 1, "sacct family")
    connect = replace(
        connect,
        "The launcher's fence mode runs cov2d_fence.sh first;",
        "The launcher's fence mode is refused (this step replaces it);",
        1,
        "connect fence-mode comment",
    )
    connect = replace(
        connect,
        "# RPD-RECO flux rerun rpd_flux3 (generated from flux connect 1 revision 2):",
        "# RPD-RECO flux rerun rpd_flux3 (generated from rpd_flux2 at 6896e787, the director's ruling (A), 2026-11-23):",
        1,
        "connect header",
    )
    body = connect.replace("generated from rpd_flux2 at 6896e787", "")
    for bad in ("squeue", OLD_ROOT, OLD_S, "rpd_flux2"):
        assert bad not in body, (bad, body.count(bad))

    # 5. The fetch.
    fetch = old["fetch"].decode()
    fetch = replace(fetch, OLD_ROOT, ROOT, 9, "fetch root")
    fetch = replace(fetch, "rpd_flux2", "rpd_flux3", 4, "fetch job name")
    fetch = replace(fetch, "rpd-flux2", "rpd-flux3", 18, "fetch labels")
    identity = "".join(f"{products[p]['sha256']} {p}\n" for p in sorted(products))
    fetch = replace(
        fetch,
        FETCH_IDENTITY_ANCHOR,
        "  mrc=$?\nfi\n"
        "echo \"== 2b. identity with flux2's factor products (run-61806073's records; the director's ruling (A))\"\n"
        "idbad=0\n"
        "while read -r want pl; do\n"
        "  got=$(sha256sum \"run/flux-factors-$pl.npz\" 2>/dev/null | cut -d' ' -f1)\n"
        '  if [ "$got" = "$want" ]; then echo "flux2-identical $pl $got"; else echo "DIFFERS FROM FLUX2 $pl [$got] '
        '(flux2 $want)"; idbad=$((idbad + 1)); fi\n'
        "done <<'FLUX2'\n" + identity + "FLUX2\n"
        'echo "FLUX2 IDENTITY: $((12 - idbad))/12 byte-identical"\n'
        'echo "== 3. the protected read"\n',
        1,
        "fetch identity",
    )
    fetch = replace(
        fetch,
        FETCH_EXIT_ANCHOR,
        FETCH_EXIT_NEW + FETCH_EXIT_ANCHOR,
        1,
        "fetch identity exit",
    )
    fetch = replace(fetch, FETCH_SACCT_OLD, FETCH_SACCT_NEW, 1, "fetch sacct rc")
    fetch = replace(
        fetch,
        '-v j="$jid" \'$1 == j {print',
        '-v j="$jid" \'$1 "" == j "" {print',
        2,
        "fetch string ids",
    )
    fetch = replace(
        fetch,
        '[$(printf \'%s\\n\' "$acct" | awk -F\'|\' -v j="$jid" \'$1 "" == j "" {print $8}\')]',
        "[$nodes]",
        1,
        "fetch node list from the one checked row",
    )
    fetch = replace(
        fetch,
        "# RPD-RECO flux rerun rpd_flux3 (generated from flux connect 1 revision 2), the fetch:",
        "# RPD-RECO flux rerun rpd_flux3 (generated from rpd_flux2 at 6896e787, the director's ruling (A), 2026-11-23), the fetch:",
        1,
        "fetch header",
    )
    fetch = replace(
        fetch,
        "the fetch then exits 11 (protected read), 12 (product mismatch) or 13 (both). A failed tar or base64 exits 14.",
        "the fetch then exits 11 (protected read), 12 (product mismatch) or 13 (both). A failed tar or base64 exits 14.\n"
        "#      A factor product that is not byte-identical to flux2's (step 2b) exits 15, after the records are sent.",
        1,
        "fetch exit list",
    )
    body = fetch.replace("generated from rpd_flux2 at 6896e787", "")
    assert (
        "squeue" not in body
        and OLD_ROOT not in body
        and "rpd_flux2" not in body
        and "rpd-flux2" not in body
    )

    # 6. The launcher.
    launch = old["launch"].decode()
    launch = replace(
        launch, SHA["connect"], sha(connect.encode()), 1, "launch connect sha"
    )
    launch = replace(launch, SHA["fetch"], sha(fetch.encode()), 1, "launch fetch sha")
    launch = replace(launch, OLD_ROOT, ROOT, 1, "launch root")
    launch = replace(launch, "rpd_flux2", "rpd_flux3", 10, "launch names")
    launch = replace(launch, "rpd-flux2", "rpd-flux3", 1, "launch staging")
    launch = replace(
        launch,
        "#        bash rpd_flux3_launch.sh connect <new empty session dir> <login node>   (prepares and submits job rpd_flux3)",
        "#        bash rpd_flux3_launch.sh connect <new empty session dir> <login node> <ack.txt>   (submits job rpd_flux3)",
        1,
        "launch usage",
    )
    launch = replace(
        launch, LAUNCH_ACK_ANCHOR, LAUNCH_ACK + LAUNCH_ACK_ANCHOR, 1, "launch ack guard"
    )
    launch = replace(
        launch,
        "# RPD-RECO flux rerun rpd_flux3 (generated from flux connect 1 revision 2):",
        "# RPD-RECO flux rerun rpd_flux3 (generated from rpd_flux2 at 6896e787, the director's ruling (A), 2026-11-23):",
        1,
        "launch header",
    )
    body = launch.replace("generated from rpd_flux2 at 6896e787", "")
    assert "squeue" not in body and "rpd_flux2" not in body and "rpd-flux2" not in body

    outputs = {
        "production-config.ready.json": cfg,
        "tools/fence_overlap.py": fence,
        "rpd_flux3_connect.sh": connect.encode(),
        "rpd_flux3_fetch.sh": fetch.encode(),
        "rpd_flux3_launch.sh": launch.encode(),
    }
    for name, data in outputs.items():
        (OUT / name).write_bytes(data)
        print(sha(data), name)
    print("pins added:", *added, sep="\n  ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
