"""RE-2 part C's rollup (re2c_rollup.py, unchanged) run on COV2D-G2R's corrected universe products.

COV2D-G2R rebuilt only the systematic-universe block. D1 (DECISION-20261114-joseph-d1-g2r-adopted.md) adopts the rebuilt
covariance as the reported 2D covariance, and the director asked for it in RE-2's own shapes through re2's own code.
This driver imports re2c_rollup.py from the deploy it runs in, patches two of its call-time globals, and calls its own
main() with the arguments it was given (re2c_run.sh's refined-arm rollup arguments). Nothing in re2c_rollup.py is
edited. The patches:
  ro.partb_sums: part B's committed digests (the function's own result), with each of the 175 J2 universe entries
      "U_<band>_<i>/xsec.root" replaced by the digest of G2R's product A_<band>_<i>, taken from G2R's committed
      products.tsv (fd/receipts-cov2d/g2r/readout/data/products.tsv.txt, sha256 PRODUCTS_SHA below; its 175 rows of
      role "g2r"; staged beside the driver and passed as --products-tsv). Every other digest is part B's.
  ro.Path:  pathlib.Path, except that the one call O() makes for a J2 universe, Path(f"{NS_R}/out", "U_<band>_<i>",
      "xsec.root"), returns G2R's /pscratch/sd/j/josephrb/cov2d-g2r-20261112/out/A_<band>_<i>/xsec.root. Every other
      call passes through unchanged (the rollup makes no isinstance check against Path and uses no Path attribute).
So the rollup still checks each G2R product's sha256 against that digest (re2c_rollup.py:459-460) and applies its own
mode guard (:461-463) to it. Everything else it reads (the S3 laterals, the normalization, stat, c08, the analysis gate,
the PINs) is unchanged.
Mode "identity" (control C0) installs the same two patches with an identity mapping: part B's own U_* digests and
paths. It must reproduce partc-r2's products.
A sidecar (--sidecar, a path outside the run's <outdir>, so that the identity run's tree and its SHA256SUMS stay
partc-r2's file set) records the mode, the mapping, the redirect counts and the sha256 values of the driver, the rollup
and products.tsv.
In mode g2r the driver exits 3 unless exactly 175 Path calls were redirected (each J2 universe once).
    python3 re2c_rollup_g2r.py --driver-mode {g2r|identity} --deploy D --products-tsv T --sidecar J <re2c_rollup.py arguments>
D is the deploy (re2c_run.sh's $D), from which re2c_rollup.py is imported; T must have sha256 PRODUCTS_SHA.
"""
import hashlib
import importlib.util
import json
import pathlib
import sys

PRODUCTS = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/g2r/readout/data/products.tsv.txt"
PRODUCTS_SHA = "a0f86fe191d6e02e4d4a9f9616dff6edaa2fadfb4384e9d56c333a92f771b8cf"
G2R_OUT = "/pscratch/sd/j/josephrb/cov2d-g2r-20261112/out"


def sha(p) -> str:
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def main(argv) -> int:
    rest = list(argv)
    opt = {}
    for k in ("--driver-mode", "--deploy", "--products-tsv", "--sidecar"):
        i = rest.index(k)
        opt[k] = rest[i + 1]
        del rest[i:i + 2]
    mode, deploy, tsv = opt["--driver-mode"], pathlib.Path(opt["--deploy"]), pathlib.Path(opt["--products-tsv"])
    if mode not in ("g2r", "identity"):
        raise SystemExit(f"--driver-mode {mode}")
    here = pathlib.Path(__file__).resolve()
    roll = deploy / "2d-unfolding" / "re2" / "partc" / "re2c_rollup.py"
    spec = importlib.util.spec_from_file_location("re2c_rollup", roll)
    ro = importlib.util.module_from_spec(spec)
    sys.modules["re2c_rollup"] = ro
    sys.argv = [str(roll)] + rest
    spec.loader.exec_module(ro)
    if sha(tsv) != PRODUCTS_SHA:
        raise SystemExit(f"{tsv} is not {PRODUCTS_SHA}")
    rows = [ln.split("\t") for ln in tsv.read_text().splitlines() if ln.strip()]
    g2r = {}
    for label, path, digest, role, uni in rows:
        if role != "g2r":
            continue
        band, idx = uni.split(":")
        assert label == f"A_{band}_{idx}" and path == f"{G2R_OUT}/{label}/xsec.root", (label, path, uni)
        g2r[f"U_{band}_{idx}"] = (digest, path)
    if len(g2r) != 175:
        raise SystemExit(f"products.tsv holds {len(g2r)} g2r rows, not 175")
    orig_sums, OrigPath, out_ns = ro.partb_sums, pathlib.Path, f"{ro.NS_R}/out"
    hits = {}

    def partb_sums():
        s = orig_sums()
        u = {k for k in s if k.startswith("U_")}
        if {k[:-len("/xsec.root")] for k in u} != set(g2r):
            raise SystemExit("part B's U_* labels are not G2R's 175")
        if mode == "g2r":
            for lab, (digest, _) in g2r.items():
                s[f"{lab}/xsec.root"] = digest
        return s

    def path(*a):
        if mode == "g2r" and len(a) == 3 and a[0] == out_ns and a[2] == "xsec.root" and a[1] in g2r:
            hits[a[1]] = hits.get(a[1], 0) + 1
            return OrigPath(g2r[a[1]][1])
        return OrigPath(*a)

    ro.partb_sums, ro.Path = partb_sums, path
    side_path = OrigPath(opt["--sidecar"])
    side = {"schema": "re2c-rollup-g2r-driver/1", "mode": mode, "driver_sha256": sha(here), "rollup_sha256": sha(roll),
            "products_tsv": PRODUCTS, "products_tsv_staged": str(tsv), "products_tsv_sha256": PRODUCTS_SHA, "g2r_out": G2R_OUT, "n_mapped": len(g2r),
            "mapping": {k: {"digest": v[0], "path": v[1]} for k, v in sorted(g2r.items())} if mode == "g2r" else {}}
    rc = ro.main()
    rc = rc if isinstance(rc, int) else 0
    side["rollup_rc"] = rc
    side["redirected"] = {"n_labels": len(hits), "n_calls": sum(hits.values())}
    side_path.write_text(json.dumps(side, indent=1) + "\n")
    print(f"G2R-DRIVER mode={mode} rollup_rc={rc} redirected labels={len(hits)} calls={sum(hits.values())}")
    if mode == "g2r" and (len(hits) != 175 or sum(hits.values()) != 175):
        return 3
    if mode == "identity" and hits:
        return 3
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
