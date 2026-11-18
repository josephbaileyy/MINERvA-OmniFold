#!/usr/bin/env python3
"""PILOT-FB §5: the gates' outcome, S1-S3 and the one outcome by precedence. Numpy only (plus RS1's bound analyzer).

Declaration: .../rounding-stability-20261106/pilot-fb/PILOT-FB-DECLARATION.md rev 3 (§5, §5.1, §5.2, §6), bound by
PILOT-FB-BINDING-1 at M_PFB 522ac0b6.

    fb_pilot_analyze.py --runs ROOT --a0-refs DIR --job-status JSON --edges DIR --out JSON
                        [--rs1-sums P --s5c-contract P --h2-definition P --sigma-receipt P]
    fb_pilot_analyze.py round1 --runs ROOT --a0-refs DIR --edges DIR   (the job's round-1 gate: G1, J, G2, G3, identity)

ROOT holds runs/A0R (RS1's A0 float32 base, tag rs1_A0), runs/E1 (base and jitters 1-20, tag pfb_E1), runs/E2 and
runs/E3 (bases). DIR holds O_NOATIME copies of RS1's A0 products, checked against RS1's committed runs-SHA256SUMS.

The outcome, first that applies (§5.2): INPUTS CHANGED; RUN REFUSED; INFEASIBLE; INCOMPLETE (an operational
interruption, the time limit or the round-1 wall-projection stop, as the job status records; and any product missing
that no gate failure explains); NOT REPRODUCED; JITTER NOT APPLIED; PREMISE FAILED (naming G2, G3 or identity);
INVALID. Otherwise the seven rows over S1 x S2 x S3. Every outcome reports what statistics could be computed; under a
gate outcome they are labelled NOT READ.

MEASURES: the declared statistics of recorded products. CANNOT AUTHORIZE: any note or paper wording, or a change to
the reported estimator; the outcome goes to Joseph and Ben as an option.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
_REPO = _ND.parent
FD = _REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
RS1_SUMS = FD / "rounding-stability-20261106/receipts/full-a1/read/runs-SHA256SUMS"
RS1_READ = FD / "rounding-stability-20261106/receipts/full-a1/read/rs1_read.json"
SIGMA_RECEIPT = _REPO / "docs/orchestration/state/s5e/cand/assess_receipt.json"
CONTRACT = _REPO / "docs/orchestration/state/s5c/contract.json"
H2_DEFINITION = _ND / "pv-ladder/readouts/h2_definition.json"
SCHEMA = "pilot-fb-analysis/1"
SEEDS = tuple(range(1, 21))
BOOT_SEED = 20261117
BARS = (0.3, 1.0)
SETS = ("E1", "E2", "E3")
GATE_ORDER = ("INPUTS CHANGED", "RUN REFUSED", "INFEASIBLE", "INCOMPLETE", "NOT REPRODUCED", "JITTER NOT APPLIED",
              "PREMISE FAILED", "INVALID")
S1_LABEL = {"R": "REMOVED", "P": "REDUCED", "C": "NOT REMOVED", "INCONCLUSIVE": "INCONCLUSIVE"}
ROWS = (  # (number, condition, outcome) in precedence order; §5.2
    (1, lambda s1, s2, s3: s1 == "NOT REMOVED", "NOT A REMEDY"),
    (2, lambda s1, s2, s3: s2 == "STAB_FAIL", "NOT AN OPTION AS DECLARED"),
    (3, lambda s1, s2, s3: s1 == "INCONCLUSIVE", "NO OPTION STATEMENT"),
    (4, lambda s1, s2, s3: s1 == "REMOVED" and s3 == "POLICY-STABLE", "OPTION A"),
    (5, lambda s1, s2, s3: s1 == "REMOVED" and s3 == "POLICY-SENSITIVE", "OPTION B"),
    (6, lambda s1, s2, s3: s1 == "REDUCED" and s3 == "POLICY-STABLE", "OPTION C"),
    (7, lambda s1, s2, s3: s1 == "REDUCED" and s3 == "POLICY-SENSITIVE", "OPTION D"),
)
LIMITS = ("one pseudo-experiment and 20 jitters; the remedy's removal measured for E1 only; three tested policies are a "
          "sample, not a bound, and E3 also changes resolution; admissibility is against this protocol's jitter only; "
          "bias, coverage and the data result are untested; each next step (bias at the F0b truths, coverage, a data run) "
          "is declared separately")


def sha256_path(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def product(path: Path) -> tuple[np.ndarray, dict]:
    z = np.load(path, allow_pickle=False)
    return np.asarray(z["xsec_flat"]), json.loads(str(z["meta"]))


def name(tag: str, j) -> str:
    return f"{tag}_b-_j{'-' if j is None else j}.npz"


def expected() -> dict:
    """{(set, seed): path relative to ROOT} for every product the run must hold."""
    out = {("A0R", None): f"runs/A0R/{name('rs1_A0', None)}"}
    out.update({("E1", j): f"runs/E1/{name('pfb_E1', j)}" for j in (None, *SEEDS)})
    out.update({(s, None): f"runs/{s}/{name(f'pfb_{s}', None)}" for s in ("E2", "E3")})
    return out


def rs1_pins(sums: Path) -> dict:
    """{rs1 A0 product file name: sha256} from RS1's committed runs-SHA256SUMS."""
    out = {}
    for ln in Path(sums).read_text().splitlines():
        sha, p = ln.split()
        if p.startswith("runs/A0/") and p.endswith(".npz"):
            out[p.split("/", 2)[2]] = sha
    return out


def pair_statistic(F: np.ndarray, base: np.ndarray, sigma: np.ndarray) -> dict:
    """S2, s5e's A3 statistic on the 10 disjoint pairs (1, 2) ... (19, 20) (FD-STAB-DECLARATION.md:158-165)."""
    z = np.abs(F / base - 1.0) / sigma
    pairs = [np.maximum(z[2 * p], z[2 * p + 1]) for p in range(len(SEEDS) // 2)]
    med = np.array([np.median(m) for m in pairs])
    mx = np.array([np.max(m) for m in pairs])
    return {"mean_median": float(med.mean()), "mean_max": float(mx.mean()),
            "se_median": float(med.std(ddof=1) / math.sqrt(len(med))), "se_max": float(mx.std(ddof=1) / math.sqrt(len(mx)))}


def policy_statistic(bases: dict, sigma: np.ndarray) -> dict:
    """S3 over the three float32 bases: per pair d_ab,j = |F_a/F_b - 1| / sigma_j."""
    d = {f"{a}-{b}": np.abs(bases[a] / bases[b] - 1.0) / sigma for a, b in (("E1", "E2"), ("E1", "E3"), ("E2", "E3"))}
    allmax = np.max(np.vstack(list(d.values())), axis=0)
    res = np.maximum(d["E1-E3"], d["E2-E3"])
    return {"median": float(np.median(allmax)), "max": float(np.max(allmax)),
            "place": {"median": float(np.median(d["E1-E2"])), "max": float(np.max(d["E1-E2"]))},
            "res": {"median": float(np.median(res)), "max": float(np.max(res))}}


def invalid_reasons(Fs: dict, sigma: np.ndarray, s1: dict | None) -> list:
    bad = []
    if sigma.ndim != 1 or not np.all(np.isfinite(sigma)) or np.any(sigma <= 0):
        bad.append("a sigma_j is non-finite or <= 0")
    for k, F in Fs.items():
        if not np.all(np.isfinite(F)):
            bad.append(f"{k}: a non-finite functional")
    if "E1_jit" in Fs and np.any(Fs["E1_jit"].mean(axis=0) == 0):
        bad.append("a zero mean in S1")
    for k in ("E1_base", "E2_base", "E3_base"):
        if k in Fs and np.any(Fs[k] == 0):
            bad.append(f"a zero denominator in S2 or S3 ({k})")
    if s1 is not None and s1.get("invalid"):
        bad.append("S1's own INVALID: more than 10 % of functionals excluded")
    return bad


def s1_reading(r: dict) -> str:
    lo, hi = r["interval_90"]
    if not (math.isfinite(lo) and math.isfinite(hi)):
        return "INCONCLUSIVE"
    return S1_LABEL[r["reading"]]


def statement(row: int, s3: dict) -> str:
    first = {4: "reduces the rounding spread to at most 10 % of (e)'s (S1 band R)",
             6: "reduces the rounding spread to between 10 % and 70 % of (e)'s (S1 band P)"}
    lead = ("On this pseudo-experiment, fixing every LightGBM model's bin edges once, from the unperturbed inputs, "
            + first[4 if row in (4, 5) else 6] + ".")
    if row in (4, 6):
        return (lead + f" Across the three tested binning policies the result moves by at most {s3['max']:.3g} pseudo-data "
                f"σ (placement alone: {s3['place']['max']:.3g}).")
    crossed = [w for w, v, bar in (("median", s3["median"], BARS[0]), ("maximum", s3["max"], BARS[1])) if v > bar]
    which = " and ".join(f"{w} {s3['median' if w == 'median' else 'max']:.3g} beyond {BARS[0] if w == 'median' else BARS[1]}"
                         for w in crossed)
    return (lead + f" The result depends on the tested binning policy: S3's {which} pseudo-data σ (placement alone: "
            f"median {s3['place']['median']:.3g}, maximum {s3['place']['max']:.3g}; resolution: median "
            f"{s3['res']['median']:.3g}, maximum {s3['res']['max']:.3g}).")


def gate_records(root: Path, have: dict) -> dict:
    """J, G2, G3 and identity from every remedy product's sidecar; a missing sidecar is a failure."""
    out = {"J": [], "G2": [], "G3": [], "identity": []}
    for (s, j), rel in have.items():
        if s == "A0R":
            continue
        side = (root / rel).with_name((root / rel).name[:-4] + ".pfb.json")
        if not side.is_file():
            for g in out:
                out[g].append(f"{s}/{j}: no gate sidecar")
            continue
        rec = json.loads(side.read_text())
        if rec.get("set") != s or rec.get("jitter_seed") != j:
            for g in out:
                out[g].append(f"{s}/{j}: the sidecar names {rec.get('set')}/{rec.get('jitter_seed')}")
            continue
        for g in out:
            if not rec["gates"][g]["pass"]:
                out[g].append(f"{s}/{j}")
    return out


def gates(root: Path, a0_refs: Path, rs1_sums: Path, sigma_receipt: Path) -> dict:
    """G4, presence, G1 and the per-product gates, on what exists."""
    import rounding_mechanism_analyze as ra
    exp = expected()
    have = {k: v for k, v in exp.items() if (root / v).is_file()}
    pins = rs1_pins(rs1_sums)
    want = [name("rs1_A0", None)] + [name("rs1_A0", s) for s in SEEDS]
    g4 = [f for f in want if not (a0_refs / f).is_file() or sha256_path(a0_refs / f) != pins.get(f)]
    if sha256_path(sigma_receipt) != ra.SIGMA_RECEIPT_SHA256:
        g4.append("the sigma receipt")
    g1 = None
    if ("A0R", None) in have and (a0_refs / name("rs1_A0", None)).is_file():
        x, _ = product(root / have[("A0R", None)])
        r, _ = product(a0_refs / name("rs1_A0", None))
        g1 = bool(x.dtype == r.dtype and x.shape == r.shape and x.tobytes() == r.tobytes())
    return {"have": have, "missing": sorted(f"{s}/{j}" for s, j in exp if (s, j) not in have), "G4_failing": g4,
            "G1": g1, "per_product": gate_records(root, have)}


def first_gate(status: dict, g: dict) -> tuple[str | None, str]:
    if g["G4_failing"]:
        return "INPUTS CHANGED", f"not at their pins: {g['G4_failing']}"
    if status.get("refused"):
        return "RUN REFUSED", status["refused"]
    if status.get("prep") == "INFEASIBLE":
        return "INFEASIBLE", status.get("prep_detail", "")
    if status.get("interrupted"):
        return "INCOMPLETE", status["interrupted"]
    if g["G1"] is False:
        return "NOT REPRODUCED", "A0R's xsec_flat is not bitwise RS1's pinned A0 base"
    if g["per_product"]["J"]:
        return "JITTER NOT APPLIED", ", ".join(g["per_product"]["J"])
    for k in ("G2", "G3", "identity"):
        if g["per_product"][k]:
            return f"PREMISE FAILED ({k})", ", ".join(g["per_product"][k])
    if g["missing"] or g["G1"] is None:
        return "INCOMPLETE", f"products missing with no gate failure: {g['missing']}"
    return None, ""


def statistics(root: Path, have: dict, a0_refs: Path, U: np.ndarray, sigma: np.ndarray) -> dict:
    import rounding_mechanism_analyze as ra
    k153 = slice(0, 153)
    F = {k: U @ product(root / v)[0].astype(np.float64) for k, v in have.items()}
    A0 = {s: U @ product(a0_refs / name("rs1_A0", s))[0].astype(np.float64) for s in (None, *SEEDS)}
    out: dict = {}
    Fs = {}
    if all(("E1", s) in F for s in (None, *SEEDS)):
        Fs["E1_jit"] = np.array([F[("E1", s)][k153] for s in SEEDS])
        Fs["E1_base"] = F[("E1", None)][k153]
    for s in ("E2", "E3"):
        if (s, None) in F:
            Fs[f"{s}_base"] = F[(s, None)][k153]
    a0_jit = np.array([A0[s][k153] for s in SEEDS])
    s1 = None
    if "E1_jit" in Fs:
        rng = np.random.default_rng(BOOT_SEED)
        s1 = ra.spread_ratio(Fs["E1_jit"], a0_jit, rng)
        out["S1"] = dict(s1, reading=s1_reading(s1))
        cells = slice(153, 169)
        e1c = np.array([F[("E1", s)][cells] for s in SEEDS])
        out["readouts_cells16"] = {"S1": ra.spread_ratio(e1c, np.array([A0[s][cells] for s in SEEDS]),
                                                         np.random.default_rng(BOOT_SEED))}
        out["readouts_e1_jitters_bitwise_equal_base"] = int(sum(
            product(root / have[("E1", s)])[0].tobytes() == product(root / have[("E1", None)])[0].tobytes() for s in SEEDS))
    out["INVALID"] = invalid_reasons(Fs, sigma, s1)
    if out["INVALID"]:
        return out
    if "E1_jit" in Fs:
        out["S2"] = pair_statistic(Fs["E1_jit"], Fs["E1_base"], sigma)
        out["S2"]["reading"] = "STAB_PASS" if out["S2"]["mean_median"] <= BARS[0] and out["S2"]["mean_max"] <= BARS[1] \
            else "STAB_FAIL"
    if all(f"{s}_base" in Fs for s in SETS):
        out["S3"] = policy_statistic({s: Fs[f"{s}_base"] for s in SETS}, sigma)
        out["S3"]["reading"] = "POLICY-STABLE" if out["S3"]["median"] <= BARS[0] and out["S3"]["max"] <= BARS[1] \
            else "POLICY-SENSITIVE"
        out["readouts_shift_from_e"] = {s: {"median": float(np.median(np.abs(Fs[f"{s}_base"] / A0[None][k153] - 1) / sigma)),
                                            "max": float(np.max(np.abs(Fs[f"{s}_base"] / A0[None][k153] - 1) / sigma))}
                                        for s in SETS}
    rs1 = json.loads(RS1_READ.read_text())["readouts"]["A0_pair_statistic_10_pairs"]
    out["readouts_rs1_A0_pair_statistic"] = {**rs1, "source": "rs1_read.json readouts.A0_pair_statistic_10_pairs"}
    return out


def outcome(stats: dict) -> dict:
    s1 = stats["S1"]["reading"]
    s2 = stats["S2"]["reading"]
    s3 = stats["S3"]["reading"]
    for row, cond, label in ROWS:
        if cond(s1, s2, s3):
            rec = {"row": row, "outcome": label, "S1": s1, "S2": s2, "S3": s3}
            if row in (4, 5, 6, 7):
                rec["statement"] = statement(row, stats["S3"])
                rec["limits"] = LIMITS
            elif row == 1:
                rec["statement"] = "Fixed edges, as declared, do not remove the rounding spread on this pseudo-experiment."
            elif row == 2:
                rec["statement"] = (f"Under fixed edges, the result still moves beyond the stability bars under the "
                                    f"protocol's jitters (S2 = {stats['S2']['mean_median']:.3g} / "
                                    f"{stats['S2']['mean_max']:.3g}). S1 reads {s1}.")
            else:
                rec["statement"] = None
            return rec
    raise AssertionError("the seven rows partition the sixteen combinations")


def analyze(root: Path, a0_refs: Path, status: dict, edges: Path, rs1_sums: Path = RS1_SUMS,
            sigma_receipt: Path = SIGMA_RECEIPT, contract: Path = CONTRACT, h2: Path = H2_DEFINITION,
            U: np.ndarray | None = None) -> dict:
    g = gates(root, a0_refs, rs1_sums, sigma_receipt)
    out = {"schema": SCHEMA, "label": "PILOT-FB readings (PILOT-FB-DECLARATION.md rev 3 §5); an option for Joseph and "
                                      "Ben; no note or paper wording", "gates": {k: v for k, v in g.items() if k != "have"}}
    gate, why = first_gate(status, g)
    sigma = np.asarray(json.loads(Path(sigma_receipt).read_text())["sigma_rel_pct"], float) / 100.0
    if U is None:
        import rounding_mechanism_probe as rmp
        U = rmp.functional_matrix(contract, h2)
    if U.shape[0] != 169:
        raise SystemExit(f"{U.shape[0]} rows in the functional matrix, not 153 + 16")
    stats = {}
    if gate not in ("INPUTS CHANGED", "RUN REFUSED", "INFEASIBLE"):
        stats = statistics(root, g["have"], a0_refs, U, sigma)
    if (Path(edges) / "INDEX.json").is_file():
        idx = json.loads((Path(edges) / "INDEX.json").read_text())
        out["readouts_edges"] = {s: {r: [{k: q[k] for k in ("z", "n", "admissible")} for q in v["features"]]
                                     for r, v in cfg["roles"].items()} for s, cfg in idx["sets"].items()}
    if gate is None and stats.get("INVALID"):
        gate, why = "INVALID", "; ".join(stats["INVALID"])
    if gate is not None:
        out["outcome"] = {"outcome": gate, "why": why}
        out["statistics_NOT_READ"] = stats
        return out
    out["statistics"] = stats
    out["outcome"] = outcome(stats)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", type=Path, required=True)
    ap.add_argument("--a0-refs", type=Path, required=True)
    ap.add_argument("--job-status", type=Path, required=True)
    ap.add_argument("--edges", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--rs1-sums", type=Path, default=RS1_SUMS)
    ap.add_argument("--s5c-contract", type=Path, default=CONTRACT)
    ap.add_argument("--h2-definition", type=Path, default=H2_DEFINITION)
    ap.add_argument("--sigma-receipt", type=Path, default=SIGMA_RECEIPT)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"[FAIL] refusing to overwrite {a.out}")
    status = json.loads(a.job_status.read_text())
    out = analyze(a.runs, a.a0_refs, status, a.edges, a.rs1_sums, a.sigma_receipt, a.s5c_contract, a.h2_definition)
    a.out.write_text(json.dumps(out, indent=1, ensure_ascii=False, allow_nan=False) + "\n")
    print(json.dumps({"outcome": out["outcome"]}, ensure_ascii=False))
    return 0


def round1_main(argv) -> int:
    """The job's round-1 gate: exit 0 if G1, J, G2, G3 and identity pass on the round-1 products, else 3."""
    ap = argparse.ArgumentParser(prog="fb_pilot_analyze.py round1")
    ap.add_argument("--runs", type=Path, required=True)
    ap.add_argument("--a0-refs", type=Path, required=True)
    ap.add_argument("--rs1-sums", type=Path, default=RS1_SUMS)
    ap.add_argument("--sigma-receipt", type=Path, default=SIGMA_RECEIPT)
    a = ap.parse_args(argv)
    g = gates(a.runs, a.a0_refs, a.rs1_sums, a.sigma_receipt)
    round1 = {("A0R", None), ("E1", None), ("E2", None), ("E3", None), *(("E1", s) for s in (1, 2, 3, 4))}
    missing = sorted(f"{s}/{j}" for s, j in round1 if (s, j) not in g["have"])
    fails = {k: v for k, v in g["per_product"].items() if v}
    ok = not g["G4_failing"] and g["G1"] is True and not fails and not missing
    print(json.dumps({"round1": "PASS" if ok else "STOP", "G4_failing": g["G4_failing"], "G1": g["G1"],
                      "failing": fails, "missing": missing}))
    return 0 if ok else 3


if __name__ == "__main__":
    if sys.argv[1:2] == ["round1"]:
        sys.exit(round1_main(sys.argv[2:]))
    sys.exit(main())
