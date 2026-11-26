#!/usr/bin/env python3
"""V_F (C_e^infl) Phase 2 (FD-VF-ADDITION-DECLARATION.md section 4): the fetch list, and the local recomputes.

fetch-list: the exact pscratch files Phase 2's three cluster-input recomputes read (section 4.2), each with its
committed pin, the committed line that records it, its size from the 2026-11-25 input check (#1327), the code line
that reads it, and the recompute it serves:
- xk: GENCMP X step K replayed through fd_xcov_steps.cmd_k / k_compute under PRODUCTS["g2r"] (the director's route (1),
  2026-11-26). The run-directory files come from xk's own run directory, cov2d-xk-g2r-20261116/run, pinned by its
  NODE-SHA256.txt (each equal to the original gencmp-x-20261102 file's pin, asserted). universes_full.root is never
  listed: only V1 opens it (fd_xcov_steps.py cmd_v1);
- prr: route2.json and route2.npz (prr_read's grade inputs for the IBU records);
- rsn: the NuE flux constraint is shared with xk (one fetch).
V0's and V1's records and the MINOS rescale are committed and read locally. Every row is asserted against #1327's
EXISTS record and its pin source; any disagreement refuses.

Run: python3 -B fd_vf_p2.py fetch-list [--out FILE]"""
import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                           cwd=Path(__file__).resolve().parent, check=True).stdout.strip())
FD = Path("docs/orchestration/state/measurement-paper/5d-community-20261024/fd")
XK = FD / "receipts-cov2d/g2r/xk"
CHECK = Path("docs/orchestration/state/ben-b-20261124/blocks5d-20261124/vf-input-check-20261125/run/vf_inputs_check.tsv")
PS = "/pscratch/sd/j/josephrb/"
ORIGINAL = PS + "gencmp-x-20261102/"
RUN = PS + "cov2d-xk-g2r-20261116/run/"
STEPS = "nd-unfolding/fd_xcov_steps.py:"
READERS = {"g2r_universes_dir": "604", "cv2d": "533", "playlist": "531", "q2d": "531", "s5": "531",
           "s1_assembly,s1_npz": "538", "flux_constraint": "595,104", "boot_native_receipt": "420",
           "staged_flux_source": "614"}
XK_LOCAL = {"minos_rescaled", "v0", "v1", "universes_identity_check"}    # committed, or never read by K
NEVER = ("universes_full.root", "bkg_dump.npz")                          # never fetched or hashed
N_ROWS, N_BYTES = 403, 1595650936                                        # the mapped list (codex-school, 2026-11-26)
HEADER = ("path", "sha256", "pin_source", "size_bytes", "reader_file_line", "recompute")


class Stop(SystemExit):
    def __init__(self, why):
        super().__init__(f"STOP fetch-list: {why}")


def pins(rel: Path, prefix: str = "") -> dict:
    """A sha256 list's rows: {prefix + path: (sha256, "file:line")}."""
    out = {}
    for i, row in enumerate((ROOT / rel).read_text().splitlines(), 1):
        f = row.split()
        if f and re.fullmatch(r"[0-9a-f]{64}", f[0]):
            out[prefix + f[-1]] = (f[0], f"{rel}:{i}")
    return out


def fetch_rows() -> list:
    node = pins(XK / "run/node/NODE-SHA256.txt")
    archive = pins(FD / "xcov/run/hpss/files.sha256", PS)
    external = pins(XK / "INPUTS-g2r.sha256") | pins(FD / "gencmp-e/INPUTS.sha256") | pins(FD / "xcov/INPUTS.sha256")
    prr = pins(FD / "receipts-prr/ibu/attempt3/cluster/log-ibu/SHA256SUMS", PS + "fd-prr-20261108/")
    rows = []
    lines = (ROOT / CHECK).read_text().splitlines()
    if lines[0].split("\t") != ["phase", "readout", "role", "path", "pinned_sha256", "found_sha256", "size", "mtime",
                                "status", "note"]:
        raise Stop("the input check's header changed")
    for row in lines[1:]:
        _, names, role, path, pin, found, size, _, status, _ = row.split("\t")
        if path in prr:
            src = prr[path]
            reader = "nd-unfolding/prior_retention/prr_read.py:" + ("399" if path.endswith(".npz") else "396")
            recompute = "prr"
        elif "xk" in names.split(",") and role not in XK_LOCAL:
            recompute = "xk"
            if path.startswith(ORIGINAL):
                rel = path[len(ORIGINAL):]
                a, n = archive.get(path), node.get("run/" + rel)
                if a is None or n is None or not (a[0] == n[0] == pin):
                    raise Stop(f"{path}: the original's pin, the run copy's and the check's differ")
                src, path = n, RUN + rel                      # xk's own run directory (declaration 4.2)
            else:
                if path not in external:
                    raise Stop(f"{path}: no committed pin")
                src = external[path]
            if role == "boot_xcov_dir":
                reader = STEPS + ("662" if path.endswith(".json") else "666,667")
            elif role == "re2_laterals_and_replicas_dir":
                reader = STEPS + ("623" if "/S3_" in path else "668")
            else:
                reader = STEPS + READERS[role]
            if role in ("flux_constraint", "s1_assembly,s1_npz"):
                recompute = "xk,rsn"
                reader += ",nd-unfolding/rsn/rsn_regrade.py:" + ("244" if role == "flux_constraint" else "245")
        else:
            continue
        if status != "EXISTS" or not (pin == found == src[0]) or not size.isdigit():
            raise Stop(f"{path}: not an EXISTS row equal to its pin ({status}, {size})")
        if any(path.endswith(x) for x in NEVER) or Path(path).name == "data_b-_j-.npz":
            raise Stop(f"{path}: a file the fetch never reads")
        rows.append((path, pin, src[1], size, reader, recompute))
    rows.sort()
    if len(rows) != len({r[0] for r in rows}) or len(rows) != N_ROWS or sum(int(r[3]) for r in rows) != N_BYTES:
        raise Stop(f"{len(rows)} rows, {sum(int(r[3]) for r in rows)} bytes: not the mapped {N_ROWS}, {N_BYTES}")
    return rows


def cmd_fetch_list(a) -> int:
    rows = fetch_rows()
    text = "\t".join(HEADER) + "\n" + "".join("\t".join(r) + "\n" for r in rows)
    if a.out:
        if a.out.exists():
            raise Stop(f"{a.out} exists")
        a.out.write_text(text)
    else:
        sys.stdout.write(text)
    by = {}
    for r in rows:
        by.setdefault(r[5], [0, 0])
        by[r[5]][0] += 1
        by[r[5]][1] += int(r[3])
    print(f"fetch-list: {len(rows)} files, {sum(int(r[3]) for r in rows)} bytes; "
          + "; ".join(f"{k} {n} files {b} bytes" for k, (n, b) in sorted(by.items()))
          + f"; sha256 {hashlib.sha256(text.encode()).hexdigest()}", file=sys.stderr)
    return 0


def build_args(argv=None):
    ap = argparse.ArgumentParser(prog="fd_vf_p2.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch-list")
    f.add_argument("--out", type=Path)
    return ap.parse_args(argv)


def main(argv=None) -> int:
    a = build_args(argv)
    return {"fetch-list": cmd_fetch_list}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
