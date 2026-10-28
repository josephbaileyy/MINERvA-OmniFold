#!/usr/bin/env python3
"""F1c's step and lane tables (state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION.md section 4), written
from the committed f1-prep-SHA256SUMS, for one node of eight lanes (sbatch_timing_packed.sh -> s5c_array.sh ->
fd_f1_lane.py).

* closure steps: per truth, the NuWro closure's pvl_unfold.py line (sbatch_pvl.sh) with the truth's pvl-ratio/1 file
  and its committed sha256: arm e, all features, the noise-free signal-only closure, seed 42, 32 threads, 5 iterations.
* pseudo-experiment steps: per truth, 20 Poisson experiments on half the MC, F0's row 1 W2 line
  (state/s5e/cand-assess-tasks.tsv aW2_s804000) with only --eavail-ratio (the bridged ratio), --pseudo-seeds and
  --out changed: candidate R, negweight-refined background, truth ratio_nd at amplitude 1.
* lanes (FD-PLAN.md section 5.2's packing): lanes 0-1 run one truth's closure and then 4 of its experiments; lanes
  2-4 and 5-7 run 6, 6 and 4 experiments of the G18 and AR23 truths.

``manifest`` writes the F1 product manifest the grader reads (fd_f0_regrade.py --f1-products-sums): exactly the two
closures closure/f1_closure_<truth>.npz and the 40 products pe/<truth>/ratio_nd_a1_s<seed>.npz, with their sha256,
relative to the F1c output root. It refuses a missing product, any other file in those directories (a .partial
from a crashed write, a stray product) or another directory under pe/.

    fd_f1_tasks.py tables --sums ... --prep ... --runs ... --table-dir ... --out-dir ...
    fd_f1_tasks.py manifest --runs <F1c products root> --out <manifest>

MEASURES: nothing. CANNOT AUTHORIZE: anything.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

NPZ = ("/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz",
       "07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f")
BKG = ("/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz",
       "2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955")
SEEDS = {"genie_v3_g18": 806000, "genie_v3_ar23": 807000}   # 20 each; no earlier product uses 806000-807019
N_PE = 20
# (lane, truth, closure first?, first seed offset, number of experiments)
LANES = ((0, "genie_v3_g18", True, 0, 4), (1, "genie_v3_ar23", True, 0, 4),
         (2, "genie_v3_g18", False, 4, 6), (3, "genie_v3_g18", False, 10, 6), (4, "genie_v3_g18", False, 16, 4),
         (5, "genie_v3_ar23", False, 4, 6), (6, "genie_v3_ar23", False, 10, 6), (7, "genie_v3_ar23", False, 16, 4))


def load_sums(path: Path) -> dict[str, str]:
    out = {}
    for line in path.read_text().splitlines():
        sha, rel = line.split("  ", 1)
        out[rel[2:] if rel.startswith("./") else rel] = sha
    return out


def steps(sums_path: Path, prep: str, runs: str) -> list[list[str]]:
    sums = load_sums(sums_path)
    for name in SEEDS:
        for rel in (f"ratios/L-5D-PV/{name}.json", f"bridged/{name}.json"):
            if rel not in sums:
                raise SystemExit(f"[FAIL] {sums_path} lists no {rel}")
    out = []
    for lane, name, closure, off, n in LANES:
        if closure:
            rel = f"ratios/L-5D-PV/{name}.json"
            out.append([str(lane), f"f1_closure_{name}", "pv-ladder/pvl_unfold.py", "--rung", "L-5D-PV", "--arm", "e",
                        "--features", "all", "--ratio", f"{prep}/{rel}", "--expect-ratio-sha256", sums[rel], "--closure",
                        "--npz", NPZ[0], "--expect-npz-sha256", NPZ[1], "--bkg", BKG[0], "--expect-bkg-sha256", BKG[1],
                        "--estimator-seed", "42", "--threads", "32", "--iters", "5",
                        "--out", f"{runs}/closure/f1_closure_{name}.npz"])
        a = SEEDS[name] + off
        out.append([str(lane), f"f1_pe_{name}_s{a}", "s5e_candidate.py", "--candidate", "R", "--", "--npz", NPZ[0],
                    "--bkg", BKG[0], "--expect-npz-sha256", NPZ[1], "--expect-bkg-sha256", BKG[1],
                    "--bkg-mode", "negweight-refined", "--truth", "ratio_nd", "--amplitude", "1.0",
                    "--eavail-ratio", f"{prep}/bridged/{name}.json", "--pseudo-seeds", f"{a}:{a + n - 1}",
                    "--out", f"{runs}/pe/{name}"])
    return out


def check_plan() -> None:
    """Every truth's 20 seeds exactly once, one closure per truth, eight lanes."""
    for name, s0 in SEEDS.items():
        got = sorted(s0 + off + i for _, t, _, off, n in LANES if t == name for i in range(n))
        if got != list(range(s0, s0 + N_PE)):
            raise SystemExit(f"[FAIL] the lane plan does not cover {name}'s 20 seeds once")
        if sum(1 for _, t, c, _, _ in LANES if t == name and c) != 1:
            raise SystemExit(f"[FAIL] {name} needs exactly one closure")
    if sorted(x[0] for x in LANES) != list(range(8)):
        raise SystemExit("[FAIL] the plan needs lanes 0-7 once each")


def expected_products() -> list[str]:
    out = [f"closure/f1_closure_{name}.npz" for name in sorted(SEEDS)]
    out += [f"pe/{name}/ratio_nd_a1_s{s}.npz" for name, s0 in sorted(SEEDS.items()) for s in range(s0, s0 + N_PE)]
    return sorted(out)


def manifest(runs: Path) -> str:
    want = expected_products()
    have = sorted(str(p.relative_to(runs)) for d in [runs / "closure", *sorted((runs / "pe").glob("*"))]
                  for p in (d.iterdir() if d.is_dir() else [d]))
    if have != want:
        extra, missing = sorted(set(have) - set(want)), sorted(set(want) - set(have))
        raise SystemExit(f"[FAIL] {runs}: {len(extra)} unexpected ({extra[:3]}) and {len(missing)} missing products")
    return "".join(f"{hashlib.sha256((runs / r).read_bytes()).hexdigest()}  ./{r}\n" for r in want)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["manifest"]:
        mp = argparse.ArgumentParser(prog="fd_f1_tasks.py manifest")
        mp.add_argument("--runs", type=Path, required=True)
        mp.add_argument("--out", type=Path, required=True)
        m = mp.parse_args(argv[1:])
        text = manifest(m.runs)
        with open(m.out, "x") as f:
            f.write(text)
        print(json.dumps({"products": len(text.splitlines())}))
        return 0
    if argv[:1] != ["tables"]:
        raise SystemExit("usage: fd_f1_tasks.py {tables|manifest} ...")
    ap = argparse.ArgumentParser(prog="fd_f1_tasks.py tables", description=__doc__.split("\n", 1)[0])
    ap.add_argument("--sums", type=Path, required=True, help="the committed f1-prep-SHA256SUMS")
    ap.add_argument("--prep", required=True, help="the prep directory on pscratch the sums are relative to")
    ap.add_argument("--runs", required=True, help="the F1c output root on pscratch")
    ap.add_argument("--table-dir", required=True, help="where the committed tables will sit in the deploy")
    ap.add_argument("--out-dir", type=Path, required=True)
    a = ap.parse_args(argv[1:])
    check_plan()
    rows = steps(a.sums, a.prep, a.runs)
    sha = hashlib.sha256(a.sums.read_bytes()).hexdigest()
    head = f"# F1c ({{}}), from {a.sums.name} sha256 {sha}; FD-F1-DECLARATION.md section 4\n"
    lanes = [["f1c_lane%d" % k, "fd_f1_lane.py", "--steps", f"{a.table_dir}/f1c-steps.tsv", "--lane", str(k)]
             for k in range(8)]
    for fn, lines, what in (("f1c-steps.tsv", rows, "steps"), ("tasks-f1c.tsv", lanes, "lanes")):
        p = a.out_dir / fn
        if p.exists():
            raise SystemExit(f"[FAIL] refusing to overwrite {p}")
        p.write_text(head.format(what) + "".join("\t".join(x) + "\n" for x in lines))
    print(json.dumps({"steps": len(rows), "lanes": len(lanes)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
