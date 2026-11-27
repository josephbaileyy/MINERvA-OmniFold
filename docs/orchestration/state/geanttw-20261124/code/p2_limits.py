#!/usr/bin/env python3
"""P2's per-playlist time limits (p2p3/AMENDMENT-P2P3.md A2), from P0's measured wall and each playlist's MC bytes.

    python3 p2_limits.py --repo REPO [--check FILE]

    limit_PL = ceil_to_minute(3 x 435 s x MCbytes_PL / MCbytes_1L), at least 00:30:00

435 s is P0's patched 1L job under strace (receipts-p0, job 62042575). The MC bytes are the sums of each playlist
manifest's rows in ANATUPLE-SHA256.tsv. Every manifest path must have a row. It prints one "PL HH:MM:SS" line per
P2 playlist (1L is excluded, because P0's output is reused), or with --check it refuses unless FILE is exactly that
text.
"""
import argparse
import math
import sys
from pathlib import Path

P0_WALL_S = 435
FACTOR = 3
FLOOR_S = 1800
ROOT = "/pscratch/sd/j/josephrb/minerva/minerva_large_files/"
PLAYLISTS = ("1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P")
TSV = "publication/release/preservation/anatuple-checksums/ANATUPLE-SHA256.tsv"


def mc_bytes(repo):
    rows = {}
    for ln in (Path(repo) / TSV).read_text().splitlines():
        f = ln.split("\t")
        if len(f) == 4 and len(f[0]) == 64:
            rows[f[3]] = int(f[1])
    out = {}
    for pl in PLAYLISTS:
        paths = (Path(repo) / "2d-unfolding/playlist_manifests" / f"{pl}_MC.txt").read_text().split()
        if not paths:
            raise SystemExit(f"REFUSE: {pl}_MC.txt is empty")
        missing = [p for p in paths if not p.startswith(ROOT) or p[len(ROOT):] not in rows]
        if missing:
            raise SystemExit(f"REFUSE: {pl}: {len(missing)} manifest paths have no ANATUPLE row, e.g. {missing[0]}")
        out[pl] = sum(rows[p[len(ROOT):]] for p in paths)
    return out


def limits_text(repo):
    b = mc_bytes(repo)
    lines = []
    for pl in PLAYLISTS:
        if pl == "1L":
            continue
        s = max(FLOOR_S, math.ceil(FACTOR * P0_WALL_S * b[pl] / b["1L"] / 60) * 60)
        lines.append(f"{pl} {s // 3600:02d}:{s % 3600 // 60:02d}:00")
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True)
    ap.add_argument("--check")
    a = ap.parse_args(argv)
    text = limits_text(a.repo)
    if a.check is not None:
        if Path(a.check).read_text() != text:
            print(f"REFUSE: {a.check} is not the limits this repo gives")
            return 1
        print(f"OK {a.check}")
        return 0
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
