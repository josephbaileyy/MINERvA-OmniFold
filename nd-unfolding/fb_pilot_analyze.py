#!/usr/bin/env python3
"""PILOT-FB §5: the gates' outcome, S1-S3 and the one outcome by precedence. Numpy only (plus RS1's bound analyzer).

Declaration: .../rounding-stability-20261106/pilot-fb/PILOT-FB-DECLARATION.md rev 3 (§5, §5.1, §5.2, §6), bound by
PILOT-FB-BINDING-1 at M_PFB 522ac0b6.

    fb_pilot_analyze.py --runs ROOT --stage STAGE --job-status JSON --job ID --deploy D --pin SHA --out JSON
    fb_pilot_analyze.py round1 --runs ROOT --stage STAGE --deploy D --pin SHA     (the job's round-1 gate)
    fb_pilot_analyze.py slurm-limit --timelimit HH:MM:SS                           (the job's own --time check)

ROOT is the run root the job created (runs/A0R with tag rs1_A0, runs/E1 base and jitters 1-20, runs/E2 and runs/E3
bases; edges/). STAGE holds the connect's O_NOATIME copies: a0-refs/ (RS1's A0 products) and the sigma receipt.

G4, re-verified here (one gate, two checks; the connect is the first): RS1's A0 copies against RS1's committed
runs-SHA256SUMS, the sigma receipt copy against its pin, of_inputs_5d.npz and bkg_dump.npz against RS1's declared
digests (read with O_NOATIME where the platform has it), and the deploy at its pinned commit, clean.

Each remedy product's sidecar must name that product by sha256, its set and seed, the edges INDEX.json the run used
and the deploy's code; the analysis then trusts its gate records.

The outcome, first that applies (§5.2): INPUTS CHANGED (G4, or a task's input-digest exit 4); RUN REFUSED (the root
was not fresh, or a task's grid-membership exit 5); INFEASIBLE (G0); INCOMPLETE (an operational interruption, a
crashed task, the time limit or the wall-projection stop; and any product missing that no gate failure explains);
NOT REPRODUCED; JITTER NOT APPLIED; PREMISE FAILED (naming G2, G3 or identity); INVALID. Otherwise the seven rows.
Every outcome reports what statistics could be computed (base-only statistics need no jitter); under a gate outcome
they are labelled NOT READ. Non-finite numbers are written as null, with their place listed.

MEASURES: the declared statistics of recorded products. CANNOT AUTHORIZE: any note or paper wording, or a change to
the reported estimator; the outcome goes to Joseph and Ben as an option.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
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
CONTRACT = _REPO / "docs/orchestration/state/s5c/contract.json"
H2_DEFINITION = _ND / "pv-ladder/readouts/h2_definition.json"
SIGMA_NAME = "assess_receipt.json"
NPZ = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz"
BKG = "/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz"
CODE_FILES = ("fb_pilot_probe.py", "fb_pilot_edges.py", "fb_pilot_gates.py")
SCHEMA = "pilot-fb-analysis/2"
SEEDS = tuple(range(1, 21))
BOOT_SEED = 20261117
BARS = (0.3, 1.0)
SETS = ("E1", "E2", "E3")
TIME_LIMIT_S = 3000  # --time=0:50:00 (§7): 0.833 node-h on one exclusive node, under the 0.9 cap
S1_LABEL = {"R": "REMOVED", "P": "REDUCED", "C": "NOT REMOVED", "INCONCLUSIVE": "INCONCLUSIVE", "INVALID": "INVALID"}
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


def sha256_path(p: Path, noatime: bool = False) -> str:
    """sha256 of a file; with noatime, opened O_NOATIME where the platform has it (Linux), so an atime watch on the
    file does not move."""
    flags = os.O_RDONLY | (getattr(os, "O_NOATIME", 0) if noatime else 0)
    try:
        fd = os.open(p, flags)
    except PermissionError:
        fd = os.open(p, os.O_RDONLY)  # O_NOATIME needs ownership; a non-owner falls back to a plain read
    h = hashlib.sha256()
    with os.fdopen(fd, "rb") as fh:
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


ROUND1 = {("A0R", None), ("E1", None), ("E2", None), ("E3", None), *(("E1", s) for s in (1, 2, 3, 4))}


def rs1_pins(sums: Path) -> dict:
    out = {}
    for ln in Path(sums).read_text().splitlines():
        sha, p = ln.split()
        if p.startswith("runs/A0/") and p.endswith(".npz"):
            out[p.split("/", 2)[2]] = sha
    return out


def slurm_limit_ok(text: str) -> bool:
    """The job's own TimeLimit (scontrol's [D-]HH:MM:SS or MM:SS) must be at most --time=0:50:00 (§7)."""
    m = re.fullmatch(r"(?:(\d+)-)?(?:(\d+):)?(\d+):(\d+)", text.strip())
    if not m:
        return False
    d, h, mi, s = (int(v) if v else 0 for v in m.groups())
    return 0 < ((d * 24 + h) * 60 + mi) * 60 + s <= TIME_LIMIT_S


def json_safe(obj, path="", spots=None):
    """Non-finite floats become None, each place recorded in spots (never a favourable number)."""
    if spots is None:
        spots = []
    if isinstance(obj, float) and not math.isfinite(obj):
        spots.append(path)
        return None
    if isinstance(obj, dict):
        return {k: json_safe(v, f"{path}/{k}", spots) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_safe(v, f"{path}[{i}]", spots) for i, v in enumerate(obj)]
    return obj


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
    if r.get("invalid") or r.get("reading") == "INVALID":
        return "INVALID"
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
        return (lead + f" Across the three tested binning policies the result moves by at most {s3['max']:.3g} in "
                f"pseudo-data σ (placement alone: S3-place, {s3['place']['max']:.3g}).")
    crossed = [w for w, v, bar in (("median", s3["median"], BARS[0]), ("maximum", s3["max"], BARS[1])) if v > bar]
    which = " and ".join(f"{w} {s3['median' if w == 'median' else 'max']:.3g} beyond {BARS[0] if w == 'median' else BARS[1]}"
                         for w in crossed)
    return (lead + f" The result depends on the tested binning policy: S3's {which} in pseudo-data σ (placement alone: "
            f"S3-place, median {s3['place']['median']:.3g}, maximum {s3['place']['max']:.3g}; resolution: S3-res, median "
            f"{s3['res']['median']:.3g}, maximum {s3['res']['max']:.3g}).")


def code_shas(deploy: Path) -> dict:
    return {f: sha256_path(Path(deploy) / "nd-unfolding" / f) for f in CODE_FILES}


def deploy_problem(deploy: Path | None, pin: str | None) -> str | None:
    if deploy is None:
        return "no deploy given"
    try:
        head = subprocess.run(["git", "-C", str(deploy), "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(deploy), "status", "--porcelain", "--untracked-files=no"],
                               capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        return f"the deploy is not a readable git checkout ({exc})"
    if head != pin or dirty:
        return f"the deploy is at {head} ({'dirty' if dirty else 'clean'}), not {pin} clean"
    return None


def gate_records(root: Path, have: dict, index_sha: str | None, code: dict | None) -> dict:
    """J, G2, G3 and identity from every remedy product's sidecar, once the sidecar is bound to that product."""
    out = {"J": [], "G2": [], "G3": [], "identity": [], "binding": []}
    for (s, j), rel in have.items():
        if s == "A0R":
            continue
        p = root / rel
        side = p.with_name(p.name[:-4] + ".pfb.json")
        tag = f"{s}/{j}"
        if not side.is_file():
            out["binding"].append(f"{tag}: no gate sidecar")
            continue
        rec = json.loads(side.read_text())
        _, meta = product(p)
        blk = meta.get("pilot_fb") or {}
        why = None
        if rec.get("product") != p.name or rec.get("product_sha256") != sha256_path(p):
            why = "the sidecar does not name this product's sha256"
        elif (rec.get("set"), rec.get("jitter_seed")) != (s, j) or (blk.get("set"), blk.get("jitter_seed")) != (s, j):
            why = f"set/seed: sidecar {rec.get('set')}/{rec.get('jitter_seed')}, meta {blk.get('set')}/{blk.get('jitter_seed')}"
        elif index_sha is not None and (rec.get("edges_index_sha256") != index_sha or blk.get("edges_index_sha256") != index_sha):
            why = "the sidecar or meta names another edges INDEX.json"
        elif code is not None and (rec.get("code_sha256") != code or blk.get("code_sha256") != code):
            why = "the sidecar or meta names code other than the deploy's"
        if why:
            out["binding"].append(f"{tag}: {why}")
            continue
        for g in ("J", "G2", "G3", "identity"):
            if not rec["gates"][g]["pass"]:
                out[g].append(tag)
    return out


def gates(root: Path, stage: Path, deploy: Path | None = None, pin: str | None = None, rs1_sums: Path = RS1_SUMS,
          npz: str = NPZ, bkg: str = BKG, check_inputs: bool = True) -> dict:
    """G4 (the analysis's check), presence, G1 and the per-product gates, on what exists."""
    import rounding_mechanism_analyze as ra
    import rounding_mechanism_probe as rmp
    exp = expected()
    have = {k: v for k, v in exp.items() if (root / v).is_file()}
    pins = rs1_pins(rs1_sums)
    refs = Path(stage) / "a0-refs"
    want = [name("rs1_A0", None)] + [name("rs1_A0", s) for s in SEEDS]
    g4 = [f for f in want if not (refs / f).is_file() or sha256_path(refs / f) != pins.get(f)]
    sig = Path(stage) / SIGMA_NAME
    if not sig.is_file() or sha256_path(sig) != ra.SIGMA_RECEIPT_SHA256:
        g4.append("the sigma receipt copy")
    if check_inputs:
        for path, want_sha in ((npz, rmp.STABILITY["npz_sha256"]), (bkg, rmp.STABILITY["bkg_sha256"])):
            if not Path(path).is_file() or sha256_path(Path(path), noatime=True) != want_sha:
                g4.append(f"the input {Path(path).name}")
    dp = deploy_problem(deploy, pin)
    if dp:
        g4.append(dp)
    idx = Path(root) / "edges" / "INDEX.json"
    index_sha = sha256_path(idx) if idx.is_file() else None
    code = code_shas(deploy) if deploy is not None and not dp else None
    g1 = None
    if ("A0R", None) in have and (refs / name("rs1_A0", None)).is_file():
        x, _ = product(root / have[("A0R", None)])
        r, _ = product(refs / name("rs1_A0", None))
        g1 = bool(x.dtype == r.dtype and x.shape == r.shape and x.tobytes() == r.tobytes())
    return {"have": have, "missing": sorted(f"{s}/{j}" for s, j in exp if (s, j) not in have), "G4_failing": g4,
            "G1": g1, "per_product": gate_records(root, have, index_sha, code)}


def first_gate(status: dict, g: dict) -> tuple[str | None, str]:
    if g["G4_failing"] or status.get("inputs_changed"):
        return "INPUTS CHANGED", status.get("inputs_changed") or f"not at their pins: {g['G4_failing']}"
    if status.get("refused"):
        return "RUN REFUSED", status["refused"]
    if status.get("prep") == "INFEASIBLE":
        return "INFEASIBLE", status.get("prep_detail", "")
    if status.get("interrupted"):
        return "INCOMPLETE", status["interrupted"]
    if status.get("task_failures"):
        return "INCOMPLETE", f"tasks failed: {status['task_failures']}"
    if g["G1"] is False:
        return "NOT REPRODUCED", "A0R's xsec_flat is not bitwise RS1's pinned A0 base"
    if g["per_product"]["J"]:
        return "JITTER NOT APPLIED", ", ".join(g["per_product"]["J"])
    if g["per_product"]["binding"]:  # an unbound sidecar cannot vouch for its product: identity, first of PREMISE FAILED
        return "PREMISE FAILED (identity)", "; ".join(g["per_product"]["binding"])
    for k in ("G2", "G3", "identity"):
        if g["per_product"][k]:
            return f"PREMISE FAILED ({k})", ", ".join(g["per_product"][k])
    if g["missing"] or g["G1"] is None:
        return "INCOMPLETE", f"products missing with no gate failure: {g['missing']}"
    return None, ""


def statistics(root: Path, have: dict, refs: Path, U: np.ndarray, sigma: np.ndarray, edges: Path | None = None) -> dict:
    """Every statistic the products allow, each with its own inputs: base-only S3 and shifts need no jitter."""
    import rounding_mechanism_analyze as ra
    k153, cells = slice(0, 153), slice(153, 169)
    F = {k: U @ product(root / v)[0].astype(np.float64) for k, v in have.items()}
    A0 = {s: U @ product(refs / name("rs1_A0", s))[0].astype(np.float64) for s in (None, *SEEDS)}
    out: dict = {"INVALID": {}}
    jit_ok = all(("E1", s) in F for s in (None, *SEEDS))
    bases_ok = all((s, None) in F for s in SETS)
    if jit_ok:
        Fs = {"E1_jit": np.array([F[("E1", s)][k153] for s in SEEDS]), "E1_base": F[("E1", None)][k153]}
        s1 = ra.spread_ratio(Fs["E1_jit"], np.array([A0[s][k153] for s in SEEDS]), np.random.default_rng(BOOT_SEED))
        out["S1"] = dict(s1, reading=s1_reading(s1))
        out["INVALID"]["S1_S2"] = invalid_reasons(Fs, sigma, s1)
        if not out["INVALID"]["S1_S2"]:
            out["S2"] = pair_statistic(Fs["E1_jit"], Fs["E1_base"], sigma)
            out["S2"]["reading"] = "STAB_PASS" if out["S2"]["mean_median"] <= BARS[0] and out["S2"]["mean_max"] <= BARS[1] \
                else "STAB_FAIL"
        e1c = np.array([F[("E1", s)][cells] for s in SEEDS])
        out["readouts_cells16_S1"] = ra.spread_ratio(e1c, np.array([A0[s][cells] for s in SEEDS]),
                                                     np.random.default_rng(BOOT_SEED))
        base_bytes = product(root / have[("E1", None)])[0].tobytes()
        out["readouts_e1_jitters_bitwise_equal_base"] = int(sum(product(root / have[("E1", s)])[0].tobytes() == base_bytes
                                                                for s in SEEDS))
    if bases_ok:
        Fb = {f"{s}_base": F[(s, None)][k153] for s in SETS}
        out["INVALID"]["S3"] = invalid_reasons(Fb, sigma, None)
        if not out["INVALID"]["S3"]:
            out["S3"] = policy_statistic({s: Fb[f"{s}_base"] for s in SETS}, sigma)
            out["S3"]["reading"] = "POLICY-STABLE" if out["S3"]["median"] <= BARS[0] and out["S3"]["max"] <= BARS[1] \
                else "POLICY-SENSITIVE"
            out["readouts_shift_from_e"] = {
                s: {"median": float(np.median(np.abs(Fb[f"{s}_base"] / A0[None][k153] - 1) / sigma)),
                    "max": float(np.max(np.abs(Fb[f"{s}_base"] / A0[None][k153] - 1) / sigma))} for s in SETS}
            cb = {s: F[(s, None)][cells] for s in SETS}
            if all(np.all(np.isfinite(v)) and np.all(v != 0) for v in cb.values()):
                one = np.ones(16)
                out["readouts_cells16_S3"] = policy_statistic(cb, one)  # relative shifts on the cells, not in sigma
    out["readouts_time"] = {f"{s}/{j}": product(root / v)[1].get("seconds_unfold") for (s, j), v in have.items()}
    out["readouts_gate_seconds"] = {}
    for (s, j), v in have.items():
        side = (root / v).with_name((root / v).name[:-4] + ".pfb.json")
        if side.is_file():
            out["readouts_gate_seconds"][f"{s}/{j}"] = json.loads(side.read_text()).get("gate_seconds")
    if edges is not None and (Path(edges) / "INDEX.json").is_file():
        idx = json.loads((Path(edges) / "INDEX.json").read_text())
        e1, e2 = idx["sets"]["E1"]["roles"], idx["sets"]["E2"]["roles"]
        out["readouts_e1_e2_edges"] = {
            r: [{"identical": int(len(set(a["edges"]) & set(b["edges"]))), "n": len(a["edges"]),
                 "median_abs_difference": float(np.median(np.abs(np.subtract(a["edges"], b["edges"]))))}
                for a, b in zip(e1[r]["features"], e2[r]["features"])] for r in e1}
        out["readouts_edges"] = {s: {r: [{k: q[k] for k in ("z", "n", "admissible")} for q in v["features"]]
                                     for r, v in cfg["roles"].items()} for s, cfg in idx["sets"].items()}
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


def analyze(root: Path, stage: Path, status: dict, job: str, deploy: Path | None = None, pin: str | None = None,
            U: np.ndarray | None = None, check_inputs: bool = True, contract: Path = CONTRACT,
            h2: Path = H2_DEFINITION) -> dict:
    out = {"schema": SCHEMA, "label": "PILOT-FB readings (PILOT-FB-DECLARATION.md rev 3 §5); an option for Joseph and "
                                      "Ben; no note or paper wording", "job": job}
    if str(status.get("job")) != str(job):
        raise SystemExit(f"[FAIL] the job status names job {status.get('job')!r}, not {job!r}")
    g = gates(root, stage, deploy, pin, check_inputs=check_inputs)
    out["gates"] = {k: v for k, v in g.items() if k != "have"}
    gate, why = first_gate(status, g)
    sigma = np.asarray(json.loads((Path(stage) / SIGMA_NAME).read_text())["sigma_rel_pct"], float) / 100.0
    if U is None:
        import rounding_mechanism_probe as rmp
        U = rmp.functional_matrix(contract, h2)
    if U.shape[0] != 169:
        raise SystemExit(f"{U.shape[0]} rows in the functional matrix, not 153 + 16")
    stats = {} if gate == "INPUTS CHANGED" else statistics(root, g["have"], Path(stage) / "a0-refs", U, sigma,
                                                           Path(root) / "edges")
    if gate is None:
        bad = [r for v in stats.get("INVALID", {}).values() for r in v]
        if bad or "S2" not in stats or "S3" not in stats:
            gate, why = "INVALID", "; ".join(bad) or "a statistic could not be formed"
    if gate is not None:
        out["outcome"] = {"outcome": gate, "why": why}
        out["statistics_NOT_READ"] = stats
    else:
        out["statistics"] = stats
        out["outcome"] = outcome(stats)
    spots: list = []
    safe = json_safe(out, "", spots)
    safe["non_finite_written_as_null"] = spots
    return safe


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", type=Path, required=True)
    ap.add_argument("--stage", type=Path, required=True)
    ap.add_argument("--job-status", type=Path, required=True)
    ap.add_argument("--job", required=True)
    ap.add_argument("--deploy", type=Path, required=True)
    ap.add_argument("--pin", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"[FAIL] refusing to overwrite {a.out}")
    status = json.loads(a.job_status.read_text())
    out = analyze(a.runs, a.stage, status, a.job, a.deploy, a.pin)
    a.out.write_text(json.dumps(out, indent=1, ensure_ascii=False, allow_nan=False) + "\n")
    print(json.dumps({"outcome": out["outcome"]}, ensure_ascii=False))
    return 0


def round1_main(argv) -> int:
    """The job's round-1 gate: exit 0 if G4, G1, the bindings, J, G2, G3 and identity pass on the round-1 products."""
    ap = argparse.ArgumentParser(prog="fb_pilot_analyze.py round1")
    ap.add_argument("--runs", type=Path, required=True)
    ap.add_argument("--stage", type=Path, required=True)
    ap.add_argument("--deploy", type=Path, required=True)
    ap.add_argument("--pin", required=True)
    a = ap.parse_args(argv)
    g = gates(a.runs, a.stage, a.deploy, a.pin)
    missing = sorted(f"{s}/{j}" for s, j in ROUND1 if (s, j) not in g["have"])
    fails = {k: v for k, v in g["per_product"].items() if v}
    ok = not g["G4_failing"] and g["G1"] is True and not fails and not missing
    print(json.dumps({"round1": "PASS" if ok else "STOP", "G4_failing": g["G4_failing"], "G1": g["G1"],
                      "failing": fails, "missing": missing}))
    return 0 if ok else 3


def slurm_main(argv) -> int:
    ap = argparse.ArgumentParser(prog="fb_pilot_analyze.py slurm-limit")
    ap.add_argument("--timelimit", required=True)
    a = ap.parse_args(argv)
    return 0 if slurm_limit_ok(a.timelimit) else 3


if __name__ == "__main__":
    if sys.argv[1:2] == ["round1"]:
        sys.exit(round1_main(sys.argv[2:]))
    if sys.argv[1:2] == ["slurm-limit"]:
        sys.exit(slurm_main(sys.argv[2:]))
    sys.exit(main())
