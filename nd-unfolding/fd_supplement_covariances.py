#!/usr/bin/env python3
"""The Supplemental Material's three covariance files (DECISION-20261031-joseph-three-covariance-files-and-1b-diagnosis.md
item 1): the reported total C_total + C_resp + C_PL,5D, marked as the reported matrix; the total without the run-period
block, C_total + C_resp; and C_PL,5D alone. Each is a byte copy of the 5B addition's committed data-product CSV
(fd/with-cpl/data-product/), labelled and hashed in supplement-covariances.json, beside the deposit candidate's
covariance.csv (fd/with-cpl/deposit-candidate/). Nothing is deposited.

``build`` copies the three files and writes the manifest; ``check`` refuses (exit 1) unless every control holds:
* S0  the data product is the pinned bytes, and each source CSV's sha256 is the one the data product records;
* S1  each package file is its source's bytes (so its sha256 is the manifest's, by S0 and S5);
* S2  each file's matrix is the data product's matrix of that key, bit for bit;
* S3  the files differ only by C_PL,5D: reported = without + C_PL,5D, bit for bit;
* S4  exactly one file is marked reported, and it is byte-identical to the package's covariance.csv;
* S5  the manifest is what ``build`` writes (every field but code_sha256);
* S6  SUPPLEMENT-COVARIANCES.md names every file with its sha256 and says which one is reported.

MEASURES: nothing; copies of committed matrices, with their checks.
CANNOT AUTHORIZE: an upload, a deposit, a DOI, a release, or paper text.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
from fd_deposit_candidate import STATUS, Stop, read_matrix_csv, report, sha256  # noqa: E402

DATA_PRODUCT_SHA256 = "d6752d2c64aad4426375c03a3171a7015f031e2027928cf89aea6cd3bbb84d50"
SOURCE = "fd/with-cpl/data-product/fd_data_product_cpl.json"
MANIFEST = "supplement-covariances.json"
README = "SUPPLEMENT-COVARIANCES.md"
REPORTED, WITHOUT, BLOCK = "C_total_plus_C_resp_plus_C_PL5D", "C_total_plus_C_resp", "C_PL5D"
# (package file, data-product matrix key, label)
FILES = (
    ("covariance-reported.csv", REPORTED,
     "the reported covariance, C_total + C_resp + C_PL,5D = C_e + C_model_abs + C_resp + C_PL,5D"),
    ("covariance-without-C_PL5D.csv", WITHOUT,
     "the reported covariance without the run-period block: C_total + C_resp = C_e + C_model_abs + C_resp"),
    ("covariance-C_PL5D.csv", BLOCK, "the run-period block C_PL,5D alone"),
)


def source_csv(key: str) -> str:
    return f"fd_data_product_cpl_{key}.csv"


def manifest(dp: dict, sources: dict[str, bytes]) -> dict:
    return {"schema": "fd-supplement-covariances/1", "status": STATUS,
            "what": "the 5D result's covariance on R00-R15 in (cm^2/nucleon)^2, three ways; the files differ only by "
                    "C_PL,5D: reported = without + C_PL,5D, bit for bit",
            "reported": FILES[0][0],
            "files": [{"name": n, "matrix": k, "label": lab, "reported": k == REPORTED,
                       "sha256": dp["files_sha256"][source_csv(k)], "source": source_csv(k)} for n, k, lab in FILES],
            "source": {"data_product": SOURCE, "sha256": DATA_PRODUCT_SHA256},
            "code_sha256": {"fd_supplement_covariances.py": sha256(Path(__file__).resolve())}}


def load(dp_path: Path) -> tuple[dict, dict[str, bytes]]:
    report("S0", "the data product is the pinned bytes", sha256(dp_path) == DATA_PRODUCT_SHA256, sha256(dp_path))
    dp = json.loads(dp_path.read_text())
    sources = {}
    for _, k, _ in FILES:
        p = dp_path.parent / source_csv(k)
        report("S0", f"{p.name} is the data product's recorded bytes", sha256(p) == dp["files_sha256"][source_csv(k)])
        sources[k] = p.read_bytes()
    return dp, sources


def check(pkg: Path, dp_path: Path) -> dict:
    dp, sources = load(dp_path)
    man = json.loads((pkg / MANIFEST).read_text())
    M = {}
    for n, k, _ in FILES:
        b = (pkg / n).read_bytes()
        report("S1", f"{n} is its source's bytes", b == sources[k])
        M[k] = read_matrix_csv(b.decode())
        report("S2", f"{n} is the data product's {k} bit for bit", np.array_equal(M[k], np.array(dp["matrices"][k], float)))
    report("S3", "reported = without + C_PL5D, bit for bit", np.array_equal(M[REPORTED], M[WITHOUT] + M[BLOCK]))
    marked = [r["name"] for r in man["files"] if r["reported"]]
    report("S4", "exactly one file is marked reported, the reported total", marked == [FILES[0][0]] == [man["reported"]])
    report("S4", "the reported file is the package's covariance.csv", (pkg / FILES[0][0]).read_bytes()
           == (pkg / "covariance.csv").read_bytes())
    want = manifest(dp, sources)
    report("S5", "the manifest is what build writes", {k: v for k, v in man.items() if k != "code_sha256"}
           == {k: v for k, v in want.items() if k != "code_sha256"})
    text = (pkg / README).read_text()
    report("S6", "the README names every file, its sha256 and the reported one",
           all(n in text and r["sha256"] in text for (n, _, _), r in zip(FILES, man["files"]))
           and f"`{FILES[0][0]}` is the reported matrix" in text)
    return {"ok": True, "package": str(pkg), "files": {r["name"]: r["sha256"] for r in man["files"]}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("build", "check"):
        p = sub.add_parser(name)
        p.add_argument("--data-product", type=Path, required=True)
        p.add_argument("--package", type=Path, required=True)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "build":
            dp, sources = load(a.data_product)
            report("S0", "no supplement file exists (no overwrite)",
                   not any((a.package / n).exists() for n in [*(f[0] for f in FILES), MANIFEST]))
            for n, k, _ in FILES:
                tmp = a.package / (n + ".partial")
                tmp.write_bytes(sources[k])
                os.replace(tmp, a.package / n)
            (a.package / MANIFEST).write_text(json.dumps(manifest(dp, sources), indent=1) + "\n")
        else:
            print(json.dumps(check(a.package, a.data_product), indent=1))
    except Stop as e:
        print(f"[STOP] {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
