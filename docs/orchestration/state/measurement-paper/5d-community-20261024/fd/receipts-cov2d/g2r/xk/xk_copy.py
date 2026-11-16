"""xk's run directories (the director's design ruling 1, 2026-11-16): digest-checked copies of the records the original
GENCMP X run's K read from its run directory. V0, V1 and BOOT read no 2D covariance product, so they are reused, not
rerun. The copied set is exactly what fd_xcov_steps.cmd_k / k_compute read from --run-dir (line numbers in
nd-unfolding/fd_xcov_steps.py at sha256 060db550):
  v0-a1/v0.json                 (cmd_k :451, boot_state)
  v1-a2/v1.json                 (v1_state :428)
  boot/native/lane_*.json       (boot_state :417)
  boot/xcov/*                   (boot_state :421; the paired replicas, k_compute :661-667)
  inputs/of_inputs_5d.npz       (k_compute :614, flux5; the other inputs/ files K re-stages itself, digest-checked)
Each file is read O_NOATIME from the original run directory and written to every destination, and must equal its
sha256 in fd/xcov/run/hpss/files.sha256 (the committed list of that run directory, paths under gencmp-x-20261102/).
A file listed there but absent, a digest mismatch, or an existing destination file is a refusal (exit 2).
    python3 xk_copy.py --source /pscratch/sd/j/josephrb/gencmp-x-20261102 --hpss-list <files.sha256> --dest D1 [--dest D2]
"""
import argparse
import hashlib
import os
import sys

PREFIX = "gencmp-x-20261102/"
WANT = ("v0-a1/v0.json", "v1-a2/v1.json")
GLOBS = ("boot/native/lane_", "boot/xcov/")
NPZ = "inputs/of_inputs_5d.npz"


def read(p):
    fd = os.open(p, os.O_RDONLY | getattr(os, "O_NOATIME", 0))
    try:
        chunks = []
        while True:
            b = os.read(fd, 1 << 22)
            if not b:
                break
            chunks.append(b)
    finally:
        os.close(fd)
    return b"".join(chunks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--hpss-list", required=True)
    ap.add_argument("--dest", action="append", required=True)
    a = ap.parse_args()
    listed = {}
    for ln in open(a.hpss_list).read().splitlines():
        t = ln.split()
        if len(t) >= 3 and t[-1].startswith(PREFIX):
            listed[t[-1][len(PREFIX):]] = t[0]
    rels = [r for r in WANT + (NPZ,)] + sorted(r for r in listed
                                               if r.startswith(GLOBS[1]) or (r.startswith(GLOBS[0]) and r.endswith(".json")))
    missing = [r for r in WANT + (NPZ,) if r not in listed]
    if missing:
        print(f"XK-COPY REFUSED: not in the committed list: {missing}")
        return 2
    n = 0
    for r in rels:
        data = read(os.path.join(a.source, r))
        got = hashlib.sha256(data).hexdigest()
        if got != listed[r]:
            print(f"XK-COPY REFUSED: {r}: sha256 {got} != committed {listed[r]}")
            return 2
        for d in a.dest:
            dst = os.path.join(d, r)
            if os.path.exists(dst):
                print(f"XK-COPY REFUSED: {dst} exists")
                return 2
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, "wb") as f:
                f.write(data)
        n += 1
    print(f"XK-COPY OK: {n} files to {len(a.dest)} destination(s), each equal to fd/xcov/run/hpss/files.sha256")
    return 0


if __name__ == "__main__":
    sys.exit(main())
