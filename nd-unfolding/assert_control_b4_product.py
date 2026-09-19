#!/usr/bin/env python3
"""Assert on the artifact the guard-set control's produce arm (B4) generates. Zero new compute.

The advisor asked for two properties, and the reason is the shape this campaign keeps hitting --
`grep -i adopt`, rc 1's keyword match, `variant` in a docstring, `--run-class` passed zero times,
and the exception the publication launcher could not pass. Each existed and did nothing.

  (i)  `publication-under-exception` reaches the OUTPUT metadata of the projected M1, not only the
       source's. A product that does not carry the token is indistinguishable, to a downstream
       consumer or a reader, from one projected off an adoptable trunk.
  (ii) the product is consistent with the CV source rather than the mean.

⚠ ON (ii), AND STATED RATHER THAN PAPERED OVER. The control produces only the cv arm -- the mean
arm REFUSES, which is the point of the control -- so there is no mean-sourced M1 to difference
against. (ii) is therefore asserted BY IDENTITY, which is decisive: the receipt's source digest
must equal z-cv.npz's measured sha256, and the declared and measured variants must both be "cv".
The projected sqrt-trace is REPORTED as a disclosure, not thresholded: a 42-cell marginalization of
a 10694^2 matrix has no predicted value to compare against without producing the mean-sourced twin,
and inventing a tolerance to make it look checked is the failure this whole campaign is about.
"""
from __future__ import annotations

import glob
import json
import sys

Z_CV_SHA = "3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5"
Z_MEAN_SHA = "61b7a4939bd40459452e232d4a5cec3c0b19ad7a21715452f7bb3bc9e0c72dd2"
EXPECTED_TOKEN = "publication-under-exception"


def check(receipt_path: str) -> list[str]:
    d = json.load(open(receipt_path))
    fails = []

    def want(cond, msg):
        if not cond:
            fails.append(msg)

    blob = json.dumps(d)
    src = d.get("src_metadata", {})

    # (i) the token must be on the OUTPUT, not merely inherited in the source block
    out_fields = {k: v for k, v in d.items() if k != "src_metadata"}
    want(EXPECTED_TOKEN in json.dumps(out_fields),
         f"(i) {EXPECTED_TOKEN!r} is absent from the OUTPUT metadata; present in src_metadata "
         f"only = {EXPECTED_TOKEN in json.dumps(src)}. A product that does not carry the token "
         f"reads as one projected off an adoptable trunk.")

    # the historical evidence must survive verbatim alongside it
    want(str(src.get("adoptable")).lower() == "false",
         f"src_metadata.adoptable is {src.get('adoptable')!r}, expected false preserved verbatim")

    # (ii) identity: this product came from the cv variant and not the mean
    want(d.get("src_variant_declared") == "cv",
         f"src_variant_declared = {d.get('src_variant_declared')!r}, expected 'cv'")
    want(d.get("src_variant_measured") == "cv",
         f"src_variant_measured = {d.get('src_variant_measured')!r}, expected 'cv'")
    want(Z_MEAN_SHA not in blob,
         "the receipt names z-mean.npz's digest; the product is not cv-sourced")
    want(Z_CV_SHA in blob,
         "the receipt does not name z-cv.npz's measured digest")
    return fails


def main(argv) -> int:
    pats = argv[1:] or ["/pscratch/sd/j/josephrb/zdet-DIAGNOSTIC-20260918/guardset-control/"
                        "B4_CONTROL_NOT_THE_DELIVERABLE.root.receipt.json"]
    paths = [p for pat in pats for p in sorted(glob.glob(pat))]
    if not paths:
        print(f"[FAIL] no B4 receipt matched {pats}. The produce arm did not produce.")
        return 2
    rc = 0
    for p in paths:
        print(f"=== {p}")
        d = json.load(open(p))
        for k in ("runClass", "runClassStatus", "src_variant_declared", "src_variant_measured"):
            if k in d:
                print(f"    {k:24s} {str(d[k])[:140]}")
        for k in ("trace", "sqrt_trace", "proj_sha256"):
            if k in d:
                print(f"    {k:24s} {d[k]}")
        fails = check(p)
        for f in fails:
            print(f"    *** FAIL {f}")
        print(f"    RESULT: {'PASS' if not fails else str(len(fails)) + ' FAILED'}")
        rc = rc or (0 if not fails else 1)
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
