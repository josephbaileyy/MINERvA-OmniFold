#!/usr/bin/env python3
"""nw_verify.py: the laptop half of the negweight input fetch. It reads the payload tar that nw_remote.sh streamed, in
either mode, and writes ONLY the two inputs of negweight_ratio_2d.pdf into a new directory, each checked against its
inventory sha256 (docs/orchestration/state/negweight-hpss-20260821/inventory.tsv:6 purity, :2 negweight).

usage: python3 -I nw_verify.py <mode pscratch|hpss> <payload.tar> <new output dir>

hpss mode: the payload must also equal negweight_runs_8.tar as archived (size 460800, sha256 4d18d466..., the
durability record's objects[] entry and recovery/step2_objects.txt:3). Nothing else in it is extracted.
Checks, each failing closed (exit 1, nothing left in the output directory):
- each wanted member appears exactly once, as a regular file, under its repo-relative name (an optional "./" prefix
  is stripped); no other member is read;
- its bytes have the inventory size and sha256;
- the output directory did not exist before.
"""
import hashlib
import os
import sys
import tarfile

WANT = {
    "2d-unfolding/HANDOFF_bkg_negweight/runs/2d_xsec_purity_seed1_hist5.root":
        (55578, "e8adc1179e3d85bec32f3a9842e5e2ce3366981f9246c251c7e9bdf72ffff91e"),
    "2d-unfolding/HANDOFF_bkg_negweight/runs/2d_xsec_negweight_seed1_hist5.root":
        (55565, "2624448dd7608bb33c43fbb8ff4648a4d7b4831515a698212d000079ac0083c8"),
}
HPSS_TAR = (460800, "4d18d46650a03a47942d3033b36276433af3a2a48d6a56482081232be1249291")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def verify(mode, payload, outdir):
    if mode not in ("pscratch", "hpss"):
        return [f"mode must be pscratch or hpss, got {mode!r}"], {}
    if os.path.lexists(outdir):
        return [f"{outdir} exists"], {}
    raw = open(payload, "rb").read()
    errs = []
    if mode == "hpss" and (len(raw), sha(raw)) != HPSS_TAR:
        errs.append(f"payload is not negweight_runs_8.tar as archived: size {len(raw)} sha256 {sha(raw)}")
        return errs, {}
    got = {}
    with tarfile.open(payload, mode="r:") as tf:
        for m in tf.getmembers():
            name = m.name[2:] if m.name.startswith("./") else m.name
            if name not in WANT:
                continue
            if name in got:
                errs.append(f"{name}: more than one member"); continue
            if not m.isreg():
                errs.append(f"{name}: not a regular file"); continue
            got[name] = tf.extractfile(m).read()
    for name, (size, want) in WANT.items():
        if name not in got:
            errs.append(f"{name}: missing from the payload"); continue
        b = got[name]
        if (len(b), sha(b)) != (size, want):
            errs.append(f"{name}: size {len(b)} sha256 {sha(b)}, want {size} {want}")
    if errs:
        return errs, {}
    os.makedirs(outdir)
    rows = {}
    for name, b in got.items():
        dst = os.path.join(outdir, os.path.basename(name))
        with open(dst, "wb") as f:
            f.write(b)
        rows[os.path.basename(name)] = sha(open(dst, "rb").read())
    with open(os.path.join(outdir, "SHA256SUMS"), "w") as f:
        for n in sorted(rows):
            f.write(f"{rows[n]}  {n}\n")
    return [], rows


def main(argv):
    if len(argv) != 3:
        print(__doc__.split("\n\n")[1]); return 2
    errs, rows = verify(*argv)
    for e in errs:
        print("FAIL " + e)
    for n, h in sorted(rows.items()):
        print(f"ok   {n} {h}")
    print("NW-VERIFY :: " + ("PASS" if not errs else "FAIL"))
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
