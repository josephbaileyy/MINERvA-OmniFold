"""The LL5D null's expected atime-moved set, fixed before the run (the director's ruling (a), 2026-11-14).

At 4231b14d, ll5d_b.null_step first opens products through the atime watch, then hashes them with a plain open:
  - remade (ll5d_b.py:426-456) via _cells/_x (:417-418, :366-368 → fd_1b_inv.open_noatime) opens, per reading in
    READINGS (ll5d.py:75): central T, seed T, every block item of bands_of(reading) (sa.EXPECT[band] items), and stat
    1..50 (STAT_REPLICAS, :63);
  - products_digest (:468-478) then plain-reads every `{TAG}_{truth}_*.npz` in --unfolds whose role (the third
    underscore field) is in BLOCK_ROLES (:481).
A path can move only if the watch recorded it AND the digest read it plainly, so the expected moved set is
opened ∩ digested. This script imports the bound module (no reimplementation) from a git archive of 4231b14d and
computes, per truth:
  opened   = the remade paths, from bands_of, sa.EXPECT, STAT_REPLICAS and product_name;
  digested = the digest's glob and role filter applied to a NAME LIST of the products directory, either a real one
             (names only; nothing is opened) or a file with one name per line.
It prints both sets' sizes, the intersection's size and sha256 (over the sorted full paths joined by "\\n" with a
trailing "\\n"), and writes the set itself to <out>.
    python3 -I -B expected_moved.py --code <archive>/nd-unfolding --unfolds-dir /pscratch/sd/j/josephrb/ll5d-unfolds-r2 \
        --names <names file> --truth g18 --out expected_moved_g18.txt
"""
import argparse
import hashlib
import sys
from pathlib import Path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--code", type=Path, required=True)
    ap.add_argument("--unfolds-dir", required=True, help="the --unfolds path the null will be given (paths are built on it)")
    ap.add_argument("--names", type=Path, required=True, help="the products directory's file names, one per line")
    ap.add_argument("--truth", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    sys.path.insert(0, str(a.code))
    import ll5d_b as b   # noqa: E402
    import ll5d          # noqa: E402
    sa = b.sa
    T, U = a.truth, a.unfolds_dir.rstrip("/")
    opened = set()
    for rd in ll5d.READINGS:
        opened.add(b.product_name(T, "central", "T"))
        opened.add(b.product_name(T, "seed", "T"))
        for band in b.bands_of(rd):
            for i in range(sa.EXPECT[band]):
                opened.add(b.product_name(T, "block", f"{band}_{i}"))
        for s in b.STAT_REPLICAS:
            opened.add(b.product_name(T, "stat", str(s)))
    names = [ln.strip() for ln in a.names.read_text().splitlines() if ln.strip()]
    prefix = f"{b.TAG}_{T}_"
    digested = {n for n in names if n.startswith(prefix) and n.endswith(".npz") and ".partial-" not in n
                and n.split("_")[2] in b.BLOCK_ROLES}
    missing = sorted(opened - set(names))
    inter = sorted(f"{U}/{n}" for n in opened & digested)
    body = "".join(p + "\n" for p in inter)
    a.out.write_text(body)
    print(f"truth={T} readings={list(ll5d.READINGS)} opened={len(opened)} digested={len(digested)} "
          f"opened_not_in_dir={len(missing)} expected_moved={len(inter)} sha256={hashlib.sha256(body.encode()).hexdigest()}")
    print(f"digested_not_opened={sorted(digested - opened)[:10]}{' ...' if len(digested - opened) > 10 else ''} "
          f"({len(digested - opened)})")
    if missing:
        print(f"OPENED-BUT-ABSENT {missing[:10]} ({len(missing)}): the null would refuse on a missing product")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
