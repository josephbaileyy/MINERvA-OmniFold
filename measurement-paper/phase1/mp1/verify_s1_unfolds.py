#!/usr/bin/env python3
"""MP1-A S1 unfold verification (deferred step 1; read-only).

For each task of tables/unfold-all.tsv:
  - the lateral inputs it names still hash to the --expect-*-sha256 it carried;
  - its s5c log, read in full, holds nothing but the known sklearn feature-name warning pairs, one result line with
    rc 0, the oi136 inventory receipt and the s5c start/end lines with rc=0;
  - its env.log equals W2b's (the same deploy, the same two missing optional setup scripts);
  - its inventory names the deploy's s5p_numerics.py by its on-disk sha256, with nothing outside the expected root;
  - the product exists, loads, and is finite; its sha256 is recorded.
Also re-hashes the dump inputs named by tables/dump-all.tsv, when present. Exit 0 = every check passes.
    verify_s1_unfolds.py <NS> <W2b dir> <out.json> [<table under NS/tables> <expected task count>]
"""
from __future__ import annotations

import glob
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np

NS = Path(sys.argv[1])
W2B = Path(sys.argv[2])
OUT = Path(sys.argv[3])
TABLE = sys.argv[4] if len(sys.argv) > 4 else "unfold-all.tsv"   # the noise-floor study passes its own table
N_EXPECT = int(sys.argv[5]) if len(sys.argv) > 5 else 11

KNOWN = (
    re.compile(r"^/\S+/sklearn/utils/validation\.py:\d+: UserWarning: X does not have valid feature names, but "
               r"LGBM(Classifier|Regressor) was fitted with feature names$"),
    re.compile(r"^  warnings\.warn\($"),
    re.compile(r"^\[oi136(-inv)?\] "),
)


def sha256(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def rows(table: Path):
    for line in table.read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        f = line.split("\t")
        yield f[0], f[1:]


def opt(argv, name):
    return argv[argv.index(name) + 1]


res = {"unfolds": {}, "dump_inputs": {}, "failures": []}
fail = res["failures"]
w2b_env = (W2B / "unfold-run/logs/w2b_unfold_rrzero.env.log").read_text()

for name, argv in rows(NS / "tables" / TABLE):
    r = {}
    for key, exp in (("--npz", "--expect-npz-sha256"), ("--bkg", "--expect-bkg-sha256")):
        p = opt(argv, key)
        got = sha256(p)
        r[key] = {"path": p, "sha256": got, "expected": opt(argv, exp), "ok": got == opt(argv, exp)}
        if not r[key]["ok"]:
            fail.append(f"{name}: {key} digest")
    logs = [p for p in glob.glob(str(NS / "unfold-run-task*.log")) if f"name={name} " in Path(p).read_text()]
    r["logs"] = logs
    if len(logs) != 1:
        fail.append(f"{name}: {len(logs)} task logs")
    else:
        text = Path(logs[0]).read_text().splitlines()
        other = [ln for ln in text if not any(k.search(ln) for k in KNOWN)]
        results = [json.loads(ln) for ln in other if ln.startswith("{")]
        s5c = [ln for ln in other if ln.startswith("[s5c] ")]
        rest = [ln for ln in other if not (ln.startswith("{") or ln.startswith("[s5c] "))]
        r["log_lines"] = len(text)
        r["result"] = results
        r["s5c"] = s5c
        r["unexplained_lines"] = rest
        if rest:
            fail.append(f"{name}: {len(rest)} unexplained log lines")
        if len(results) != 1 or results[0].get("rc") != 0:
            fail.append(f"{name}: result line")
        if len(s5c) != 2 or " start=" not in s5c[0] or f"name={name} rc=0 end=" not in s5c[1]:
            fail.append(f"{name}: s5c start/end")
    env = (NS / f"unfold-run/logs/{name}.env.log").read_text()
    r["env_log_equals_w2b"] = env == w2b_env
    if env != w2b_env:
        fail.append(f"{name}: env.log differs from W2b's")
    inv = [json.loads(ln) for ln in (NS / f"unfold-run/inventory/{name}.jsonl").read_text().splitlines() if ln.strip()]
    top = inv[0]
    script_now = sha256(top["script"])
    r["inventory"] = {"records": len(inv), "script": top["script"], "script_sha256": top["script_sha256"],
                      "script_sha256_on_disk": script_now, "allow_is_empty": top["allow_is_empty"],
                      "guard_installed": top["guard_installed"]}
    outside = [x.get("outside_expect_root") for x in inv if "outside_expect_root" in x]
    r["inventory"]["outside_expect_root"] = outside
    if script_now != top["script_sha256"] or not top["allow_is_empty"] or not top["guard_installed"] or any(outside):
        fail.append(f"{name}: inventory")
    pairs = [x for x in argv if x.startswith("--pairs=")]   # S1 and the noise floor pass -:-, the jitter study -:<J>
    b, j = (pairs[0].split("=", 1)[1] if pairs else "-:-").split(":")
    prod = Path(opt(argv, "--out")) / f"{opt(argv, '--tag')}_b{b}_j{j}.npz"
    r["product"] = str(prod)
    if not prod.is_file():
        fail.append(f"{name}: product missing")
    else:
        r["product_sha256"] = sha256(prod)
        with np.load(prod, allow_pickle=False) as z:
            keys = sorted(z.files)
            nonfinite = {k: int(np.size(z[k]) - np.isfinite(z[k]).sum()) for k in keys
                         if np.issubdtype(z[k].dtype, np.floating)}
        r["product_keys"] = keys
        r["product_nonfinite"] = {k: v for k, v in nonfinite.items() if v}
        if r["product_nonfinite"]:
            fail.append(f"{name}: non-finite product entries")
        if results and results[0].get("out") != prod.name:
            fail.append(f"{name}: result names {results[0].get('out')}")
    res["unfolds"][name] = r

for name, argv in (rows(NS / "tables/dump-all.tsv") if (NS / "tables/dump-all.tsv").is_file() else ()):
    p = opt(argv, "--omnifile")
    res["dump_inputs"][name] = {"omnifile": p, "exists": Path(p).is_file(),
                                "out": opt(argv, "--out"), "out_sha256": sha256(opt(argv, "--out")),
                                "out_bkg": opt(argv, "--out-bkg"), "out_bkg_sha256": sha256(opt(argv, "--out-bkg"))}

res["n_unfolds"] = len(res["unfolds"])
if res["n_unfolds"] != N_EXPECT:
    fail.append(f"{res['n_unfolds']} unfold tasks, expected {N_EXPECT}")
res["verdict"] = "PASS" if not fail else "FAIL"
OUT.write_text(json.dumps(res, indent=1) + "\n")
print(json.dumps({"verdict": res["verdict"], "failures": fail,
                  "products": {k: v.get("product_sha256", "")[:12] for k, v in res["unfolds"].items()}}, indent=1))
sys.exit(0 if not fail else 1)
