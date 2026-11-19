#!/usr/bin/env python3
"""PILOT-FB §5: the gates' outcome, S1-S3 and the one outcome by precedence. Numpy only (plus RS1's bound analyzer).

Declaration: .../rounding-stability-20261106/pilot-fb/PILOT-FB-DECLARATION.md rev 3 (§5, §5.1, §5.2, §6), bound by
PILOT-FB-BINDING-1 at M_PFB 522ac0b6.

    fb_pilot_analyze.py --runs ROOT --stage STAGE --job-status JSON --job ID --deploy D --pin SHA --out JSON
    fb_pilot_analyze.py round1 --runs ROOT --stage STAGE --deploy D --pin SHA --job ID   (the job's round-1 gate)
    fb_pilot_analyze.py slurm-limit --timelimit HH:MM:SS                                (the job's own --time check)
    fb_pilot_analyze.py smoke-receipt write|check --stage STAGE --pin SHA --local true|false --trace LOG [--exclude F]
    fb_pilot_analyze.py stage-check --stage STAGE                                       (the job's stage inventory)
    fb_pilot_analyze.py lgbm-check --prefix ENV_PREFIX                     (the job's LightGBM version and location)

ROOT is the run root the job created (runs/A0R with tag rs1_A0, runs/E1 base and jitters 1-20, runs/E2 and runs/E3
bases; edges/). STAGE holds RS1's A0 products (a0-refs/) and the sigma receipt, copied there by the connect; this tree
does not make those copies. The analysis requires each to be a plain file (not a symlink or a hard link, so no read
here can reach a protected original) at its pin.

The job status (ROOT/job-status.json, or STAGE/job-<id>.refused.json) must name this job, the pin and the declared
root; a status recording a refusal before the root was created has no outcome. Every product must record this job in
its meta (slurm_job); a product of another job means the root was not this job's alone, which is RUN REFUSED.

G4, re-verified here (one gate, two checks; the connect is the first): RS1's A0 copies against RS1's committed
runs-SHA256SUMS, the sigma receipt copy against its pin, of_inputs_5d.npz and bkg_dump.npz against RS1's declared
digests (read with O_NOATIME where the platform has it), and the deploy at its pinned commit, clean.

Each remedy product's sidecar must name that product by sha256, its set and seed, the run's edges INDEX.json and the
deploy's code, and its gate bits must equal the product meta's gates_pass; the analysis then trusts its gate records.
The run's edges/INDEX.json must exist and every file it lists must hash as it records; a missing or unreadable INDEX,
sidecar or meta fails the binding, never skips it. An unreadable product counts as missing.

The outcome, first that applies (§5.2): INPUTS CHANGED (G4, or a task's input-digest exit 4); RUN REFUSED (the root
was not fresh, or a task's grid-membership exit 5); INFEASIBLE (G0); INCOMPLETE (an operational interruption, a
crashed task, the time limit or the wall-projection stop; and any product missing or unreadable that no gate failure
explains);
NOT REPRODUCED; JITTER NOT APPLIED; PREMISE FAILED (naming G2, G3 or identity); INVALID. Otherwise the seven rows.
Every outcome after INPUTS CHANGED reports what statistics could be computed (base-only statistics need no jitter;
S2 needs no valid S1); under a gate outcome they are labelled NOT READ. INPUTS CHANGED is returned before any product,
the sigma copy or the functional matrix is read for statistics. Non-finite numbers are written as null, with their
place listed.

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
import time
import zipfile
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
SCHEMA = "pilot-fb-analysis/3"
SEEDS = tuple(range(1, 21))
BOOT_SEED = 20261117
BARS = (0.3, 1.0)
SETS = ("E1", "E2", "E3")
TIME_LIMIT_S = 3000  # --time=0:50:00 (§7): 0.833 node-h on one exclusive node, under the 0.9 cap
ROOT_DECLARED = "/pscratch/sd/j/josephrb/pfb-20261117"
STAGE_DECLARED = "/pscratch/sd/j/josephrb/pfb-20261117-stage"
RS1_A0_ORIGINALS = Path("/pscratch/sd/j/josephrb/rs1-a1-20261107/runs/A0")  # RS1's protected A0 products (RS1-BINDING-2)
SIGMA_REL = "docs/orchestration/state/s5e/cand/assess_receipt.json"  # the protected sigma receipt, in a checkout
CONDA = "/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda"  # setup_salloc_env.sh runs it
SHA_HEX = re.compile(r"[0-9a-f]{64}")
ROLES = ("clf1", "reg", "clf2", "ref")  # fb_pilot_edges.ROLES
GATES = ("J", "G2", "G3", "identity")
UNREADABLE = (OSError, ValueError, KeyError, TypeError, AttributeError, EOFError, zipfile.BadZipFile)
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
    file does not move. Used with noatime only for the two raw inputs, whose plain read §7 allows: a non-owner's
    EPERM falls back to that plain read."""
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


def safe_sha(p: Path, noatime: bool = False) -> str | None:
    """sha256, or None if the file cannot be read (a G4 or binding failure, never an exception)."""
    try:
        return sha256_path(p, noatime)
    except OSError:
        return None


def stage_copy_problem(p: Path, stage: Path, originals: tuple = ()) -> str | None:
    """A stage copy must be a plain file of its own, physically inside the stage: no symlink in any component below
    the stage, the leaf included (a symlinked directory would reach the originals), no hard link, and not the inode of
    any protected original that exists here."""
    p = Path(p)
    lexical = os.path.join(os.path.realpath(stage), os.path.relpath(os.path.abspath(p), os.path.abspath(stage)))
    if os.path.realpath(p) != lexical:
        return "a path component is a symlink"
    if not p.is_file():
        return "absent"
    st = p.stat()
    if st.st_nlink != 1:
        return "a hard link"
    for o in originals:
        try:
            so = os.stat(o)
        except OSError:
            continue
        if (so.st_dev, so.st_ino) == (st.st_dev, st.st_ino):
            return f"the protected original itself ({o})"
    return None


def product(path: Path) -> tuple[np.ndarray, dict]:
    """(xsec_flat, meta); a meta that is not a JSON object raises ValueError, so it is classified as unreadable."""
    z = np.load(path, allow_pickle=False)
    x, meta = np.asarray(z["xsec_flat"]), json.loads(str(z["meta"]))
    if not isinstance(meta, dict):
        raise ValueError(f"the meta is a JSON {type(meta).__name__}, not an object")
    return x, meta


def write_new(path: Path, text: str) -> None:
    """Create a file that must not exist, opened O_CREAT | O_EXCL | O_NOFOLLOW: no existing file, hard link or symlink
    at the path is ever written through."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, "w") as fh:
        fh.write(text)


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
    if s1 is not None and "E1_jit" in Fs and np.any(Fs["E1_jit"].mean(axis=0) == 0):
        bad.append("a zero mean in S1")
    for k in ("E1_base", "E2_base", "E3_base"):
        if k in Fs and np.any(Fs[k] == 0):
            bad.append(f"a zero denominator in S2 or S3 ({k})")
    if s1 is not None and s1.get("invalid"):
        bad.append("S1's own INVALID: more than 10 % of functionals excluded")
    return bad


def s2_reading(st: dict) -> str:
    """S2's bars include equality (§5)."""
    return "STAB_PASS" if st["mean_median"] <= BARS[0] and st["mean_max"] <= BARS[1] else "STAB_FAIL"


def s3_reading(st: dict) -> str:
    """S3's bars include equality (§5)."""
    return "POLICY-STABLE" if st["median"] <= BARS[0] and st["max"] <= BARS[1] else "POLICY-SENSITIVE"


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


GIT = ("git", "-c", "core.fsmonitor=false")


def git_env() -> dict:
    """git reads no system or global config (code 6, F3): its own and HOME's configuration cannot run hooks here."""
    return {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}


def module_problem(module_file: str, prefix: str) -> str | None:
    """The module must resolve under the declared environment prefix (code 6, F3): a user-site or stray copy fails."""
    f, pre = os.path.realpath(module_file), os.path.realpath(prefix)
    return None if f.startswith(pre + os.sep) else f"{f} is not under the declared prefix {pre}"


def deploy_problem(deploy: Path | None, pin: str | None) -> str | None:
    if deploy is None:
        return "no deploy given"
    try:
        head = subprocess.run([*GIT, "-C", str(deploy), "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True, env=git_env()).stdout.strip()
        dirty = subprocess.run([*GIT, "--no-optional-locks", "-C", str(deploy), "status", "--porcelain",
                                "--untracked-files=no"],
                               capture_output=True, text=True, check=True, env=git_env()).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        return f"the deploy is not a readable git checkout ({exc})"
    if head != pin or dirty:
        return f"the deploy is at {head} ({'dirty' if dirty else 'clean'}), not {pin} clean"
    return None


def gate_records(root: Path, have: dict, index_sha: str | None, code: dict | None) -> dict:
    """J, G2, G3 and identity from every remedy product's sidecar, once the sidecar is bound to that product. A missing
    INDEX (index_sha None) or deploy code (code None) fails every binding: absent evidence never skips a check."""
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
        try:
            rec = json.loads(side.read_text())
            _, meta = product(p)
            blk = meta.get("pilot_fb")
            if not isinstance(rec, dict) or not isinstance(blk, dict) or not isinstance(rec.get("gates"), dict):
                raise ValueError("the sidecar, the meta's pilot_fb block or the sidecar's gates is not a JSON object")
            bits = {g: rec["gates"][g]["pass"] for g in GATES}
        except UNREADABLE as exc:
            out["binding"].append(f"{tag}: the sidecar or the product's meta is unreadable ({exc!r})")
            continue
        why = None
        if rec.get("product") != p.name or rec.get("product_sha256") != safe_sha(p):
            why = "the sidecar does not name this product's sha256"
        elif (rec.get("set"), rec.get("jitter_seed")) != (s, j) or (blk.get("set"), blk.get("jitter_seed")) != (s, j):
            why = f"set/seed: sidecar {rec.get('set')}/{rec.get('jitter_seed')}, meta {blk.get('set')}/{blk.get('jitter_seed')}"
        elif index_sha is None:
            why = "the run's edges/INDEX.json is missing or unreadable"
        elif rec.get("edges_index_sha256") != index_sha or blk.get("edges_index_sha256") != index_sha:
            why = "the sidecar or meta names another edges INDEX.json"
        elif code is None or rec.get("code_sha256") != code or blk.get("code_sha256") != code:
            why = "the sidecar or meta names code other than the deploy's"
        elif bits != blk.get("gates_pass"):
            why = f"the sidecar's gate bits {bits} are not the product meta's gates_pass {blk.get('gates_pass')}"
        if why:
            out["binding"].append(f"{tag}: {why}")
            continue
        for g in GATES:
            if bits[g] is not True:
                out[g].append(tag)
    return out


def edges_problems(edges: Path) -> tuple[str | None, list]:
    """(INDEX.json's sha256 or None, problems): the run's INDEX must exist, list the three sets' four roles, and every
    file it lists must hash as it records."""
    idx = Path(edges) / "INDEX.json"
    if not idx.is_file():
        return None, ["edges: the run's INDEX.json is missing"]
    sha = safe_sha(idx)
    bad = []
    try:
        import fb_pilot_edges as E
        index = json.loads(idx.read_text())
        if index.get("schema") != "pfb-edges/1":
            bad.append(f"edges: INDEX.json's schema is {index.get('schema')!r}, not 'pfb-edges/1'")
        if type(index.get("K")) is not float or index.get("K") != E.K:  # exact types: a JSON false is not 0.0
            bad.append(f"edges: INDEX.json's K is {index.get('K')!r}, not {E.K!r}")
        for s, c in index["sets"].items():
            want_p = E.SETS.get(s, {})
            for f in ("max_bin", "offset"):
                if type(c.get(f)) is not type(want_p.get(f)) or c.get(f) != want_p.get(f):
                    bad.append(f"edges: {s}'s {f} is {c.get(f)!r}, not the declared {want_p.get(f)!r}")
        if set(index["sets"]) != set(SETS) or any(set(c["roles"]) != set(ROLES) for c in index["sets"].values()):
            bad.append("edges: INDEX.json does not list the three sets' four roles")
        for s, c in index["sets"].items():
            for r, v in c["roles"].items():
                want, rec_sha = f"{s}_{r}.json", v.get("sha256")
                if v.get("file") != want:
                    bad.append(f"edges: {s}/{r} names the file {v.get('file')!r}, not {want}")
                    continue
                if not (isinstance(rec_sha, str) and SHA_HEX.fullmatch(rec_sha)):
                    bad.append(f"edges: {want}'s recorded sha256 {rec_sha!r} is not a sha256")
                    continue
                got = safe_sha(Path(edges) / want)
                if got is None or got != rec_sha:
                    bad.append(f"edges: {want} is not the file INDEX.json records")
                feats = v.get("features")
                if not (isinstance(feats, list) and len(feats) == 5
                        and all(isinstance(q, dict) and isinstance(q.get("edges"), list) for q in feats)):
                    bad.append(f"edges: {s}/{r} does not record five features' edges")
    except UNREADABLE as exc:
        bad.append(f"edges: INDEX.json is unreadable ({exc!r})")
    return (None if sha is None else sha), bad


def g4_failing(stage: Path, deploy: Path | None, pin: str | None, rs1_sums: Path | None = None, npz: str = NPZ,
               bkg: str = BKG, check_inputs: bool = True, a0_originals: Path | None = None) -> list:
    """G4, the analysis's check: the A0 copies and the sigma copy (plain files at their pins), the two inputs, and the
    deploy at its pin, clean. An unreadable file fails its check; nothing here raises on a bad file."""
    import rounding_mechanism_analyze as ra
    import rounding_mechanism_probe as rmp
    pins = rs1_pins(RS1_SUMS if rs1_sums is None else rs1_sums)
    refs = Path(stage) / "a0-refs"
    g4 = []
    a0o = RS1_A0_ORIGINALS if a0_originals is None else Path(a0_originals)
    for f in [name("rs1_A0", None)] + [name("rs1_A0", s) for s in SEEDS]:
        why = stage_copy_problem(refs / f, stage, (a0o / f,)) \
            or (None if safe_sha(refs / f) == pins.get(f) else "not at its pin")
        if why:
            g4.append(f"{f} ({why})")
    sig = Path(stage) / SIGMA_NAME
    sig_originals = tuple(Path(d) / SIGMA_REL for d in (deploy, _REPO) if d is not None)
    why = stage_copy_problem(sig, stage, sig_originals)
    if why or safe_sha(sig) != ra.SIGMA_RECEIPT_SHA256:
        g4.append("the sigma receipt copy" + (f" ({why})" if why else ""))
    if check_inputs:
        for path, want_sha in ((npz, rmp.STABILITY["npz_sha256"]), (bkg, rmp.STABILITY["bkg_sha256"])):
            if not Path(path).is_file() or safe_sha(Path(path), noatime=True) != want_sha:
                g4.append(f"the input {Path(path).name}")
    dp = deploy_problem(deploy, pin)
    if dp:
        g4.append(dp)
    return g4


def gates(root: Path, stage: Path, deploy: Path | None = None, pin: str | None = None, job: str | None = None,
          rs1_sums: Path | None = None, npz: str = NPZ, bkg: str = BKG, check_inputs: bool = True,
          a0_originals: Path | None = None) -> dict:
    """G4 first; if it fails, nothing else is read. Then presence (an unreadable product is missing), each product's
    job, the run's edges, G1 and the per-product gates, on what exists."""
    exp = expected()
    g4 = g4_failing(stage, deploy, pin, rs1_sums, npz, bkg, check_inputs, a0_originals)
    if g4:
        return {"have": {}, "missing": sorted(f"{s}/{j}" for s, j in exp), "unreadable": [], "foreign": [],
                "G4_failing": g4, "G1": None, "edges": [], "per_product": {k: [] for k in (*GATES, "binding")},
                "not_read": "G4 failed: no product, sidecar or edges file was read"}
    have, unreadable, foreign, xs = {}, [], [], {}
    for k, v in exp.items():
        if not (Path(root) / v).is_file():
            continue
        try:
            x, meta = product(Path(root) / v)
        except UNREADABLE as exc:
            unreadable.append(f"{k[0]}/{k[1]}: {exc!r}")
            continue
        have[k] = v
        if str(meta.get("slurm_job")) != str(job) or meta.get("slurm_job") is None:
            foreign.append(f"{k[0]}/{k[1]}: job {meta.get('slurm_job')!r}")
        xs[k] = x
    index_sha, edges = edges_problems(Path(root) / "edges")
    code = code_shas(deploy)
    per = gate_records(Path(root), have, index_sha, code)
    per["binding"] = edges + per["binding"]
    g1 = None
    ref0 = Path(stage) / "a0-refs" / name("rs1_A0", None)
    if ("A0R", None) in have:  # G4 passed: ref0 is a plain stage copy at its pin
        x, (r, _) = xs[("A0R", None)], product(ref0)
        g1 = bool(x.dtype == r.dtype and x.shape == r.shape and x.tobytes() == r.tobytes())
    return {"have": have, "missing": sorted(f"{s}/{j}" for s, j in exp if (s, j) not in have), "unreadable": unreadable,
            "foreign": foreign, "G4_failing": [], "G1": g1, "edges": edges, "per_product": per}


def first_gate(status: dict, g: dict) -> tuple[str | None, str]:
    if g["G4_failing"] or status.get("inputs_changed"):
        return "INPUTS CHANGED", status.get("inputs_changed") or f"not at their pins: {g['G4_failing']}"
    if status.get("refused"):
        return "RUN REFUSED", status["refused"]
    if g.get("foreign"):  # products this job did not write: the root was not this job's alone
        return "RUN REFUSED", f"products of another job in the root: {g['foreign']}"
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
        return "INCOMPLETE", (f"products missing with no gate failure: {g['missing']}"
                              + (f"; unreadable: {g['unreadable']}" if g.get("unreadable") else ""))
    return None, ""


def statistics(root: Path, have: dict, refs: Path, U: np.ndarray, sigma: np.ndarray, edges: Path | None = None) -> dict:
    """Every statistic the products allow, each with its own inputs: base-only S3 and each base's shift need no
    jitter, and S2 needs no valid S1 (S1's own INVALID suppresses S1's reading only)."""
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
        out["INVALID"]["S1"] = invalid_reasons({"E1_jit": Fs["E1_jit"]}, sigma, s1)
        out["INVALID"]["S2"] = invalid_reasons(Fs, sigma, None)
        if not out["INVALID"]["S2"]:
            out["S2"] = pair_statistic(Fs["E1_jit"], Fs["E1_base"], sigma)
            out["S2"]["reading"] = s2_reading(out["S2"])
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
            out["S3"]["reading"] = s3_reading(out["S3"])
        cb = {s: F[(s, None)][cells] for s in SETS}
        if all(np.all(np.isfinite(v)) and np.all(v != 0) for v in cb.values()):
            # §6 names S3 on R00-R15, but the pseudo-data sigma is defined on the 153 functionals only (the sigma
            # receipt has 153 entries): this readout is the relative |F_a / F_b - 1| on the cells, not S3 in sigma
            out["readouts_cells16_relative_policy_shift"] = dict(policy_statistic(cb, np.ones(16)), units=(
                "relative |F_a/F_b - 1|, not in pseudo-data sigma (none is defined on the 16 cells)"))
    sig_ok = sigma.ndim == 1 and np.all(np.isfinite(sigma)) and np.all(sigma > 0)
    a0b = A0[None][k153]
    out["readouts_shift_from_e"] = {}
    for s in SETS:  # each base's shift from (e) needs only that base
        if (s, None) in F and sig_ok and np.all(np.isfinite(F[(s, None)][k153])) and np.all(np.isfinite(a0b)) \
                and np.all(a0b != 0):
            d = np.abs(F[(s, None)][k153] / a0b - 1) / sigma
            out["readouts_shift_from_e"][s] = {"median": float(np.median(d)), "max": float(np.max(d))}
    out["readouts_time"] = {}
    for (s, j), v in have.items():
        try:
            out["readouts_time"][f"{s}/{j}"] = product(root / v)[1].get("seconds_unfold")
        except UNREADABLE:
            out["readouts_time"][f"{s}/{j}"] = None
    out["readouts_gate_seconds_in_unfold"] = {}
    out["readouts_gate_seconds_scope"] = ("seconds each unfold spent in its own gate captures and checks; excludes this "
                                          "analysis's aggregate checks, the sidecar binding and the job's round-1 gate")
    for (s, j), v in have.items():
        side = (root / v).with_name((root / v).name[:-4] + ".pfb.json")
        try:
            out["readouts_gate_seconds_in_unfold"][f"{s}/{j}"] = json.loads(side.read_text()).get("gate_seconds")
        except UNREADABLE:
            out["readouts_gate_seconds_in_unfold"][f"{s}/{j}"] = None
    try:
        if edges is not None and (Path(edges) / "INDEX.json").is_file():
            idx = json.loads((Path(edges) / "INDEX.json").read_text())
            e1, e2 = idx["sets"]["E1"]["roles"], idx["sets"]["E2"]["roles"]
            out["readouts_e1_e2_edges"] = {
                r: [{"identical": int(len(set(a["edges"]) & set(b["edges"]))), "n": len(a["edges"]),
                     "median_abs_difference": float(np.median(np.abs(np.subtract(a["edges"], b["edges"]))))}
                    for a, b in zip(e1[r]["features"], e2[r]["features"])] for r in e1}
            out["readouts_edges"] = {s: {r: [{k: q[k] for k in ("z", "n", "admissible")} for q in v["features"]]
                                         for r, v in cfg["roles"].items()} for s, cfg in idx["sets"].items()}
    except UNREADABLE as exc:
        out["readouts_edges_unreadable"] = repr(exc)
    try:  # a display-only readout: its failure never removes the statistics computed above
        rs1 = json.loads(Path(RS1_READ).read_text())["readouts"]["A0_pair_statistic_10_pairs"]
        out["readouts_rs1_A0_pair_statistic"] = {**rs1, "source": "rs1_read.json readouts.A0_pair_statistic_10_pairs"}
    except UNREADABLE as exc:
        out["readouts_rs1_A0_pair_statistic_unreadable"] = repr(exc)
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


def status_problem(status: dict, job: str, pin: str | None, status_path: Path | None, runs: Path, stage: Path,
                   root_declared: str = ROOT_DECLARED) -> str | None:
    """The status must be this job's, at this pin, for the declared root, read from where the job writes it."""
    if not isinstance(status, dict):
        return f"the job status is a JSON {type(status).__name__}, not an object"
    if str(status.get("job")) != str(job):
        return f"the job status names job {status.get('job')!r}, not {job!r}"
    if status.get("pin") != pin:
        return f"the job status names pin {status.get('pin')!r}, not {pin!r}"
    if status.get("root") != root_declared:
        return f"the job status names root {status.get('root')!r}, not the declared {root_declared}"
    if os.path.realpath(runs) != root_declared:
        return f"the root read, {os.path.realpath(runs)}, is not the status's and declared root {root_declared}"
    if status_path is not None:
        where = {Path(runs).resolve() / "job-status.json", Path(stage).resolve() / f"job-{job}.refused.json"}
        if Path(status_path).resolve() not in where:
            return f"the job status {status_path} is not {' or '.join(sorted(map(str, where)))}"
    if status.get("preflight_refused"):
        return f"no outcome: the job refused before creating the run root ({status['preflight_refused']})"
    return None


def analyze(root: Path, stage: Path, status: dict, job: str, deploy: Path | None = None, pin: str | None = None,
            U: np.ndarray | None = None, check_inputs: bool = True, contract: Path = CONTRACT,
            h2: Path = H2_DEFINITION, status_path: Path | None = None, root_declared: str = ROOT_DECLARED) -> dict:
    out = {"schema": SCHEMA, "label": "PILOT-FB readings (PILOT-FB-DECLARATION.md rev 3 §5); an option for Joseph and "
                                      "Ben; no note or paper wording", "job": job}
    bad = status_problem(status, job, pin, status_path, root, stage, root_declared)
    if bad:
        raise SystemExit(f"[FAIL] {bad}")
    g = gates(root, stage, deploy, pin, job, check_inputs=check_inputs)
    out["gates"] = {k: v for k, v in g.items() if k != "have"}
    gate, why = first_gate(status, g)
    stats: dict = {}
    if gate != "INPUTS CHANGED":  # G4 passed, so the sigma and A0 copies are at their pins
        try:
            sigma = np.asarray(json.loads((Path(stage) / SIGMA_NAME).read_text())["sigma_rel_pct"], float) / 100.0
            if U is None:
                import rounding_mechanism_probe as rmp
                U = rmp.functional_matrix(contract, h2)
            if U.shape[0] != 169:
                raise ValueError(f"{U.shape[0]} rows in the functional matrix, not 153 + 16")
            stats = statistics(root, g["have"], Path(stage) / "a0-refs", U, sigma, Path(root) / "edges")
        except UNREADABLE as exc:
            stats = {"not_formed": repr(exc)}
            if gate is None:
                gate, why = "INVALID", f"a statistic could not be formed ({exc!r})"
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
    why = out_problem(a.out, a.stage, a.runs)
    if why:
        raise SystemExit(f"[FAIL] {why}")
    try:
        status = json.loads(a.job_status.read_text())
    except UNREADABLE as exc:
        raise SystemExit(f"[FAIL] the job status {a.job_status} is unreadable ({exc!r})")
    out = analyze(a.runs, a.stage, status, a.job, a.deploy, a.pin, status_path=a.job_status)
    write_new(a.out, json.dumps(out, indent=1, ensure_ascii=False, allow_nan=False) + "\n")
    print(json.dumps({"outcome": out["outcome"]}, ensure_ascii=False))
    return 0


def out_problem(out: Path, stage: Path, runs: Path) -> str | None:
    """The analysis writes only a new file directly or deeper under the stage or the run root, physically."""
    out = Path(out)
    if os.path.lexists(out):
        return f"refusing to overwrite {out}"
    parent = os.path.realpath(os.path.dirname(os.path.abspath(out)))
    for base in (stage, runs):
        b = os.path.realpath(base)
        if parent == b or parent.startswith(b + os.sep):
            return None
    return f"--out {out} is not under the stage {stage} or the run root {runs}"


def round1_main(argv) -> int:
    """The job's round-1 gate: exit 0 if G4, G1, the bindings, J, G2, G3 and identity pass on the round-1 products."""
    ap = argparse.ArgumentParser(prog="fb_pilot_analyze.py round1")
    ap.add_argument("--runs", type=Path, required=True)
    ap.add_argument("--stage", type=Path, required=True)
    ap.add_argument("--deploy", type=Path, required=True)
    ap.add_argument("--pin", required=True)
    ap.add_argument("--job", required=True)
    a = ap.parse_args(argv)
    g = gates(a.runs, a.stage, a.deploy, a.pin, a.job)
    missing = sorted(f"{s}/{j}" for s, j in ROUND1 if (s, j) not in g["have"])
    fails = {k: v for k, v in g["per_product"].items() if v}
    ok = not g["G4_failing"] and g["G1"] is True and not fails and not missing and not g["foreign"]
    print(json.dumps({"round1": "PASS" if ok else "STOP", "G4_failing": g["G4_failing"], "G1": g["G1"],
                      "failing": fails, "missing": missing, "unreadable": g["unreadable"], "foreign": g["foreign"]}))
    return 0 if ok else 3


TRACE_LINE = re.compile(r"^\++@([^@]*)@")  # bash 3.2 can drop the space PS4 ends with


def setup_closure(trace: Path, exclude: tuple = ()) -> dict:
    """{path: sha256} of every file the sourced setup ran from, read from its xtrace (PS4 '+@${BASH_SOURCE[0]}@ '),
    and the conda executable it runs (CONDA) where it exists; the calling script itself is excluded."""
    paths = set()
    for ln in Path(trace).read_text(errors="replace").splitlines():
        m = TRACE_LINE.match(ln)
        if m and m.group(1):
            paths.add(m.group(1))
    ex = {os.path.realpath(e) for e in exclude}
    out = {}
    for q in sorted(paths) + ([CONDA] if os.path.isfile(CONDA) else []):
        r = os.path.realpath(q)
        if r in ex or not os.path.isfile(r):
            continue
        out[r] = safe_sha(Path(r))
    return out


def post_setup_env(environ=None) -> list:
    """The names the sourced setup leaves exported, without the per-run ones (Slurm's, PFB_, the shell's own)."""
    env = os.environ if environ is None else environ
    return sorted(k for k in env if not (k.startswith(("SLURM_", "PFB_")) or k in ("PWD", "OLDPWD", "SHLVL", "_")))


def smoke_receipt(stage: Path, pin: str, local: bool, closure: dict | None = None, env_names: list | None = None) -> dict:
    """What the login-node smoke records, and the job requires: its stage, pin, mode, INDEX.json's sha256, the
    sourced setup's file closure, and the names the setup leaves exported."""
    idx = Path(stage) / "smoke-edges" / "INDEX.json"
    senv = Path(stage) / "smoke-setup-env.txt"
    return {"schema": "pfb-smoke/4", "stage": str(stage), "pin": pin, "local_test": bool(local),
            "index_sha256": safe_sha(idx) if idx.is_file() else None, "setup_closure": closure or {},
            "post_setup_env": post_setup_env() if env_names is None else env_names,
            "setup_env_sha256": safe_sha(senv) if senv.is_file() else None}


def smoke_receipt_problem(rec: dict, stage: Path, pin: str, local: bool, closure: dict | None = None,
                          env_names: list | None = None) -> str | None:
    if not isinstance(rec, dict):
        return "the smoke receipt is not a JSON object"
    want = smoke_receipt(stage, pin, local, closure, env_names)
    if want["index_sha256"] is None:
        return "the stage holds no smoke-edges/INDEX.json"
    diff = [k for k in ("schema", "stage", "pin", "local_test", "index_sha256", "setup_closure", "post_setup_env",
                        "setup_env_sha256") if rec.get(k) != want[k]]
    return f"the smoke receipt differs in {diff}" if diff else None


STAGE_FILES = re.compile(r"(slurm-\d+\.(out|err)|job-(\d+|local)\.(refused\.json|env\.log))")
SMOKE_TOP = ("smoke-receipt.json", "smoke-env.log", "smoke.log", "smoke-setup-env.txt", SIGMA_NAME)
SMOKE_OPTIONAL = ("smoke-sbatch.txt",)  # a production smoke writes it; a local test without sbatch does not
EDGE_FILES = {f"{s}_{r}.json" for s in SETS for r in ROLES} | {"INDEX.json"}


def stage_problems(stage: Path) -> list:
    """The job's inventory of the stage the smoke created: only the expected entries, every file a plain file of its
    own (no symlink, no hard link), every directory a real one: a0-refs/ (the 21 A0 copies), smoke-edges/ (INDEX and
    the twelve edge files), smoke-unused/ (empty), the smoke's files and the sigma copy, and Slurm's and the jobs'
    own logs and refusal records."""
    stage = Path(stage)
    want_dirs = {"a0-refs": {name("rs1_A0", None)} | {name("rs1_A0", s) for s in SEEDS}, "smoke-edges": EDGE_FILES,
                 "smoke-unused": set()}
    bad = []

    def plain(p: Path) -> str | None:
        st = os.lstat(p)
        if not os.path.isfile(p) or os.path.islink(p):
            return "not a plain file"
        return "a hard link" if st.st_nlink != 1 else None

    for e in sorted(os.listdir(stage)):
        p = stage / e
        if os.path.islink(p):
            bad.append(f"{e}: a symlink")
        elif e in want_dirs:
            if not os.path.isdir(p):
                bad.append(f"{e}: not a directory")
                continue
            got = set(os.listdir(p))
            if got != want_dirs[e]:
                bad.append(f"{e}/: extra {sorted(got - want_dirs[e])}, missing {sorted(want_dirs[e] - got)}")
            for f in sorted(got & want_dirs[e]):
                why = os.path.islink(p / f) and "a symlink" or plain(p / f)
                if why:
                    bad.append(f"{e}/{f}: {why}")
        elif e in SMOKE_TOP or e in SMOKE_OPTIONAL or STAGE_FILES.fullmatch(e):
            why = plain(p)
            if why:
                bad.append(f"{e}: {why}")
        else:
            bad.append(f"{e}: not an expected stage entry")
    for e in SMOKE_TOP + tuple(want_dirs):
        if not os.path.lexists(stage / e):
            bad.append(f"{e}: missing")
    return bad


def smoke_main(argv) -> int:
    """write: the smoke's last step (exit 9 if the INDEX it must hash is absent or the receipt exists); check: the
    job's (exit 3). Both take the setup closure from their own xtrace (--trace, the env log) minus the calling script."""
    ap = argparse.ArgumentParser(prog="fb_pilot_analyze.py smoke-receipt")
    ap.add_argument("action", choices=("write", "check"))
    ap.add_argument("--stage", type=Path, required=True)
    ap.add_argument("--pin", required=True)
    ap.add_argument("--local", choices=("true", "false"), required=True)
    ap.add_argument("--trace", type=Path, required=True)
    ap.add_argument("--exclude", default="")
    a = ap.parse_args(argv)
    local = a.local == "true"
    p = a.stage / "smoke-receipt.json"
    try:
        closure = setup_closure(a.trace, (a.exclude,) if a.exclude else ())
    except UNREADABLE as exc:
        print(f"the setup trace {a.trace} is unreadable ({exc!r})", file=sys.stderr)
        return 9 if a.action == "write" else 3
    if a.action == "write":
        rec = smoke_receipt(a.stage, a.pin, local, closure)
        if rec["index_sha256"] is None:
            print("[pfb-smoke] no receipt: INDEX.json absent", file=sys.stderr)
            return 9
        try:
            write_new(p, json.dumps(dict(rec, host=os.uname()[1], utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())),
                                    indent=1) + "\n")
        except OSError as exc:
            print(f"[pfb-smoke] no receipt: {exc}", file=sys.stderr)
            return 9
        print(json.dumps({k: v for k, v in rec.items() if k != "setup_closure"} | {"setup_closure_files": len(closure)}))
        return 0
    try:
        why = smoke_receipt_problem(json.loads(p.read_text()), a.stage, a.pin, local, closure)
    except UNREADABLE as exc:
        why = f"the smoke receipt is unreadable ({exc!r})"
    if why:
        print(why, file=sys.stderr)
        return 3
    return 0


def lgbm_main(argv) -> int:
    """The job's environment check, run as the tasks run (nd-unfolding first on sys.path): LightGBM 4.6.0, imported
    from under the declared environment prefix; numpy and the interpreter recorded."""
    ap = argparse.ArgumentParser(prog="fb_pilot_analyze.py lgbm-check")
    ap.add_argument("--prefix", required=True)
    a = ap.parse_args(argv)
    import lightgbm
    rec = {"lightgbm": lightgbm.__version__, "lightgbm_file": os.path.realpath(lightgbm.__file__),
           "numpy": np.__version__, "numpy_file": os.path.realpath(np.__file__), "python": sys.version.split()[0],
           "executable": sys.executable, "prefix": a.prefix, "user_site_disabled": bool(sys.flags.no_user_site)}
    why = None if lightgbm.__version__ == "4.6.0" else f"LightGBM is {lightgbm.__version__}, not 4.6.0"
    why = why or module_problem(lightgbm.__file__, a.prefix)
    rec["problem"] = why
    print(json.dumps(rec))
    return 3 if why else 0


def stage_main(argv) -> int:
    ap = argparse.ArgumentParser(prog="fb_pilot_analyze.py stage-check")
    ap.add_argument("--stage", type=Path, required=True)
    a = ap.parse_args(argv)
    bad = stage_problems(a.stage)
    for b in bad:
        print(b, file=sys.stderr)
    return 3 if bad else 0


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
    if sys.argv[1:2] == ["smoke-receipt"]:
        sys.exit(smoke_main(sys.argv[2:]))
    if sys.argv[1:2] == ["stage-check"]:
        sys.exit(stage_main(sys.argv[2:]))
    if sys.argv[1:2] == ["lgbm-check"]:
        sys.exit(lgbm_main(sys.argv[2:]))
    sys.exit(main())
