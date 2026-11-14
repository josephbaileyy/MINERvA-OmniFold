"""Synthetic reproduction of the LL5D null's atime deviation (the audit's (a) requirement, the director's ruling).

Run on a Perlmutter login node, in a FRESH directory under the lane's own pscratch namespace (never an LL5D path),
with the bound modules imported from a git archive of 4231b14d (nothing reimplemented):
  0. byte-only control: write a file, sleep 2 s, read it plainly, stat it. The filesystem must move atime on a plain
     read; if it does not, the test is INCONCLUSIVE (exit 3), not a pass.
  1. the null's order on synthetic products: write N products named as ll5d_b.product_name gives (truth "g18", roles
     central/seed/block/stat), clear fd_1b_inv.OPENED, open each through fd_1b_inv.open_noatime (as remade's _x does,
     ll5d_b.py:366-368), sleep 2 s, call the bound ll5d_b.products_digest (:468-478), then fd_1b_inv.atime_check().
     It must report moved == exactly the opened set.
  2. the mutant: the same, with s5n_pseudo.sha256_path replaced by fd_1b_inv.sha256_noatime for the digest. It must
     report moved == [] and the same digest value (sha256 over the same bytes).
Every created file and the directory are removed at the end by explicit names, and the removal is printed.
    python3 -I -B test_null_order.py <code dir with nd-unfolding> <fresh work dir under pscratch>
"""
import os
import sys
import time
from pathlib import Path


def main(code: Path, work: Path) -> int:
    sys.path.insert(0, str(code / "nd-unfolding"))
    import numpy as np
    import fd_1b_inv as inv
    import ll5d_b as b
    import s5n_pseudo
    assert not work.exists(), f"{work} exists"
    work.mkdir()
    made = []
    try:
        ctl = work / "control.bin"
        ctl.write_bytes(b"x" * 4096); made.append(ctl)
        a0 = os.stat(ctl).st_atime_ns
        time.sleep(2)
        ctl.read_bytes()
        a1 = os.stat(ctl).st_atime_ns
        print(f"control: atime before {a0} after a plain read {a1} moved={a1 != a0}")
        if a1 == a0:
            print("NULL-ORDER TEST INCONCLUSIVE: this filesystem does not move atime on a plain read")
            return 3
        names = [b.product_name("g18", "central", "T"), b.product_name("g18", "seed", "T"),
                 b.product_name("g18", "block", "Flux_0"), b.product_name("g18", "block", "2p2h_0"),
                 b.product_name("g18", "stat", "1"), b.product_name("g18", "stat", "2")]
        res = {}
        for label in ("bound", "mutant"):
            d = work / label
            d.mkdir(); made.append(d)
            paths = []
            for n in names:
                p = d / n
                np.savez_compressed(p, xsec_flat=np.arange(5.0), meta="{}")
                paths.append(p); made.append(p)
            time.sleep(2)
            inv.OPENED.clear()
            for p in paths:
                with inv.open_noatime(p) as fh:
                    fh.read()
            time.sleep(2)
            orig = s5n_pseudo.sha256_path
            if label == "mutant":
                s5n_pseudo.sha256_path = inv.sha256_noatime
            try:
                dig = b.products_digest(d, "g18", b.BLOCK_ROLES)
            finally:
                s5n_pseudo.sha256_path = orig
            chk = inv.atime_check()
            res[label] = (dig, sorted(chk["moved"]))
            print(f"{label}: digest {dig} watched {len(chk['files'])} moved {len(chk['moved'])}")
        want = sorted(str(work / "bound" / n) for n in names)
        ok_bound = res["bound"][1] == want
        print(f"bound: moved == the opened set: {ok_bound}")
        print(f"mutant: moved empty: {res['mutant'][1] == []}")
        # the digest covers names + bytes; the two dirs hold identical bytes and names, so the values must be equal
        same_digest_bytes = res["mutant"][0] == res["bound"][0]
        print(f"digest equal between bound and mutant (same names and bytes): {same_digest_bytes}")
        ok = ok_bound and res["mutant"][1] == [] and same_digest_bytes
        print("NULL-ORDER TEST", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    finally:
        for p in sorted(made, key=lambda q: len(str(q)), reverse=True):
            try:
                (p.rmdir() if p.is_dir() else p.unlink())
            except OSError as exc:
                print(f"removal failed {p}: {exc}")
        try:
            work.rmdir()
        except OSError as exc:
            print(f"removal failed {work}: {exc}")
        print(f"removed {len(made)} entries and {work}; left={work.exists()}")


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
