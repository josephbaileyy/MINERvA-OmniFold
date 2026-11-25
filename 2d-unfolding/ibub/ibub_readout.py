#!/usr/bin/env python3
"""IBUB's readout at one tune (IBUB-DECLARATION.md sections 2 and 4-6), on a login node at 0 node-h.

It reads:
- OmniFold's 300 stored toy outputs, COV2D's committed records and the tune's truth_xsec.npz, every one through
  ``cov2d_readout.Run``. That is COV2D's own harness: an open audit that refuses any plain open under /pscratch or
  /global/cfs, private O_NOATIME copies checked against their digests, and the atime ledger.
- the IBU units' products, checked against their done-markers' digests.

It then makes three things:
- C-OF, C-TRUTH, C-COMPLETE, C-DATA and C-CELLS (section 5);
- the readings of section 4, on the pre-surrogate errors, at K = 10 and at K = 5;
- the descriptive readouts of section 6.

The COV2D code is imported unchanged: ``cov2d_score.errors`` and ``lateral_deltas``, ``cov2d_readouts.bias`` and
``spread_alone``, and ``cov2d_readout``'s ``Run``, ``completeness``, ``plan``, ``inventory_paths``, ``read_pinned`` and
``read_provenance``.

  python ibub_readout.py --truth G18 --units DIR --out DIR --job ID --job-m COMMIT --records DIR [--run-dir O]

It writes ``ibub_<T>.json`` (the record, through ``Run.finish``) and ``ibub_<T>_errors.npz`` (the per-toy errors).

MEASURES: the declared readings at one tune. CANNOT AUTHORIZE: any statement beyond section 7; the readings go to
the director.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from statistics import NormalDist

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for p in (HERE, REPO / "2d-unfolding" / "cov2d", REPO / "nd-unfolding"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import cov2d as c  # noqa: E402
import cov2d_blocks as cb  # noqa: E402
import cov2d_readout as rd  # noqa: E402
import cov2d_readouts as cr  # noqa: E402
import cov2d_score as cs  # noqa: E402
import ibub_unit as iu  # noqa: E402

NX, NY = 14, 16
SCHEMA = "ibub-readout/1"


# ------------------------------------------------------------------------------------------- the tests (section 4)


def test_matrix(flat, area) -> tuple[np.ndarray, list]:
    """W (cells x tests) and the tests' labels: each reported cell, then the 14 p_T bands, the 16 p_par bands and the
    total, each band the area-weighted integral of its reported cells (section 4)."""
    flat, area = np.asarray(flat), np.asarray(area, np.float64)
    n = flat.size
    cols, labels = [np.eye(n)], [f"cell:{int(g)}" for g in flat]
    for name, key, count in (("pt", flat // NY, NX), ("pz", flat % NY, NY)):
        for b in range(count):
            m = key == b
            if not m.any():
                raise c.Refusal(f"band {name}:{b} has no reported cell")
            cols.append(np.where(m, area, 0.0)[:, None])
            labels.append(f"{name}:{b}")
    cols.append(area[:, None])
    labels.append("total")
    return np.hstack(cols), labels


def z_star(alpha: float, tests: int) -> float:
    return NormalDist().inv_cdf(1 - alpha / 2 / tests)


def bootstrap_counts(n: int, B: int, seed: list) -> np.ndarray:
    """(B, n): how often each toy index is drawn in each of B resamples with replacement, from default_rng(seed)."""
    idx = np.random.default_rng(seed).integers(0, n, size=(B, n))
    counts = np.zeros((B, n))
    np.add.at(counts, (np.arange(B)[:, None], idx), 1.0)
    return counts


def ratio(a, b) -> np.ndarray:
    """a / b elementwise; where b is 0 it is 0 if a is 0, else +-inf with a's sign (never a silent NaN)."""
    a, b = np.broadcast_arrays(np.asarray(a, np.float64), np.asarray(b, np.float64))
    out = np.divide(a, b, out=np.zeros(a.shape), where=b != 0)
    zero = (b == 0) & (a != 0)
    out[zero] = np.copysign(np.inf, a[zero])
    return out


def per_test(Y: np.ndarray, counts: np.ndarray, zs: float, xt: np.ndarray, sigma: np.ndarray) -> dict:
    """The mean over the toys of Y (toys x tests), its toy-bootstrap SE (the same resamples for every caller), the
    analytic SE, and the mean in % of the mean truth, in sigma and in SE."""
    n = Y.shape[0]
    mean = Y.mean(axis=0)
    se_boot = (counts @ Y / n).std(axis=0, ddof=1)
    se_an = Y.std(axis=0, ddof=1) / np.sqrt(n)
    z = ratio(mean, se_boot)
    return {"mean": mean, "se_boot": se_boot, "se_analytic": se_an, "rel_pct": 100 * ratio(mean, xt),
            "in_sigma": ratio(mean, sigma), "z": z, "resolved": np.abs(z) > zs}


def hotelling(D: np.ndarray) -> dict:
    """Descriptive only (section 4): T^2 = n dbar' S^-1 dbar on the cells, with S the paired differences' sample
    covariance (ddof 1), F = (n - p) / (p (n - 1)) T^2 against F(p, n - p), and S's condition number printed beside
    it, as declared. No conditioning cutoff is applied (the codex read: none is declared). A solve that numpy refuses
    as singular is recorded as not computable."""
    from scipy import stats
    n, p = D.shape
    S = np.cov(D, rowvar=False, ddof=1)
    dbar = D.mean(axis=0)
    cond = float(np.linalg.cond(S))
    none = {"T2": None, "F": None, "p_value": None, "df": [p, n - p], "cond_S": cond, "read_by": "nothing"}
    try:
        t2 = float(n * dbar @ np.linalg.solve(S, dbar))
    except np.linalg.LinAlgError as e:
        return dict(none, why=f"S is singular ({e})")
    F = (n - p) / (p * (n - 1)) * t2
    return {"T2": t2, "F": F, "p_value": float(stats.f.sf(F, p, n - p)) if n > p else None, "df": [p, n - p],
            "cond_S": cond, "read_by": "nothing"}


def statistics(E_of: np.ndarray, E_ibu: np.ndarray, x_true: np.ndarray, W: np.ndarray, labels: list, C_T: np.ndarray,
               counts: np.ndarray, alpha: float, n_cells: int) -> dict:
    """Section 4 at one K: each method's bias per test, the paired difference (the truth cancels toy by toy), and the
    rule over the family of all tests."""
    from scipy import stats
    n, tests = E_of.shape[0], W.shape[1]
    zs = z_star(alpha, tests)
    xt = (x_true @ W).mean(axis=0)
    sigma = np.sqrt(np.einsum("ct,cd,dt->t", W, C_T, W))
    Y = {"OF": E_of @ W, "IBU": E_ibu @ W}
    m = {k: per_test(v, counts, zs, xt, sigma) for k, v in Y.items()}
    d = per_test(Y["IBU"] - Y["OF"], counts, zs, xt, sigma)
    d["resolution_rel_pct"] = 100 * zs * ratio(d["se_boot"], np.abs(xt))
    d["unpaired_ratio"] = ratio(np.abs(m["IBU"]["mean"] - m["OF"]["mean"]),
                                np.sqrt(m["IBU"]["se_boot"] ** 2 + m["OF"]["se_boot"] ** 2))
    flagged = [i for i in range(tests) if abs(d["z"][i]) > zs]
    cells = slice(0, n_cells)
    summary = {}
    for k in ("OF", "IBU"):
        r = m[k]["rel_pct"][cells]
        summary[k] = {"rms_rel_pct": float(np.sqrt(np.mean(r ** 2))), "median_abs_rel_pct": float(np.median(np.abs(r))),
                      "bias_resolved": [labels[i] for i in range(tests) if m[k]["resolved"][i]]}
    summary["cells_ibu_smaller_abs_bias"] = int(np.sum(np.abs(m["IBU"]["mean"][cells]) < np.abs(m["OF"]["mean"][cells])))
    ba = ratio(d["se_boot"], d["se_analytic"])
    return {
        "reading": "DIFFER" if flagged else "NOT RESOLVED APART",
        "differ_at": [{"test": labels[i], "d": float(d["mean"][i]), "se_boot": float(d["se_boot"][i]),
                       "z": float(d["z"][i]), "sign": "IBU above OF" if d["mean"][i] > 0 else "IBU below OF"}
                      for i in flagged],
        "z_star": zs, "t_quantile_299": float(stats.t.ppf(1 - alpha / 2 / tests, n - 1)), "tests": tests, "alpha": alpha,
        "labels": labels, "mean_truth": xt.tolist(), "sigma": sigma.tolist(),
        "method": {k: {q: np.asarray(v).tolist() for q, v in m[k].items()} for k in m},
        "difference": {q: np.asarray(v).tolist() for q, v in d.items()},
        "summary": summary,
        "bootstrap_over_analytic_se": {"median": float(np.median(ba)), "min": float(np.min(ba)), "max": float(np.max(ba))},
        "hotelling": hotelling(Y["IBU"][:, cells] - Y["OF"][:, cells]),
    }


# ------------------------------------------------------------------------------------------- the controls (section 5)


def c_of(E_post: np.ndarray, C_T: np.ndarray, C_model_abs: np.ndarray, score: dict, tol: float = 1e-12) -> dict:
    """C-OF: COV2D's bias and spread_alone readouts, rebuilt from the stored outputs and the recorded surrogates, equal
    the committed record's. p_hat is a count and must agree exactly; the other fields agree to tol."""
    sigma = np.sqrt(np.diag(C_T))
    got = {"bias": cr.bias(E_post, sigma), **cr.spread_alone(E_post, C_T, C_model_abs)}
    want = {"bias": score["bias"], **{k: score["spread_alone"][k] for k in ("p_hat", "pull_mean", "pull_sd")}}
    out = {}
    for k in ("bias", "pull_mean", "pull_sd", "p_hat"):
        a, b = np.asarray(got[k], np.float64), np.asarray(want[k], np.float64)
        diff = float(np.max(np.abs(a - b))) if a.shape == b.shape else float("inf")
        out[k] = {"max_abs_diff": diff, "pass": bool(diff == 0.0 if k == "p_hat" else diff <= tol)}
    out["pass"] = all(v["pass"] for v in out.values())
    return out


def read_inv(inv: dict, path) -> tuple[bytes, str]:
    """One O_NOATIME read of ``path``; its sha256 goes into the readout's inventory of graded bytes."""
    data, got = cb.read_noatime(path)
    inv[str(path)] = got
    return data, got


def pinned_inv(inv: dict, path, want: str) -> bytes:
    """``rd.read_pinned`` (one O_NOATIME read, equal to ``want`` or a c.Refusal), with the digest into the inventory."""
    data = rd.read_pinned(path, want)
    inv[str(path)] = want
    return data


def copy_inv(inv: dict, run, src, want: str, name: str) -> Path:
    """``run.copy`` (one O_NOATIME read, equal to ``want`` or a c.Refusal), with the digest into the inventory. Every
    graded product goes through here, so the reading names the exact bytes it graded."""
    dst = run.copy(src, want, name)
    inv[str(src)] = want
    return dst


def ibu_products(run, units: Path, truth: str, shas: dict, ks_want: list, rep: np.ndarray, cells, cfg: dict,
                 bound: dict, inv: dict) -> dict:
    """C-COMPLETE, C-TRUTH's IBU side, C-DATA and C-CELLS over the tune's IBU toy units, and their cross sections at
    K = 10 (hXSec2D) and K = 5 (the npz row), on the 205 cells.

    - **Absent** (missing, the tune reads INCOMPLETE): no marker, or a marker whose verdict is not PASS. This alone
      never makes the tune INVALID.
    - **A problem** (the tune reads INVALID, and the unit is also missing): a marker that is unreadable or a symlink,
      or names another unit, job or deploy, whatever its verdict; a product that is a symlink or not at its marker's
      digest; an unreadable npz or meta; another K scan; a marker in ``units`` for a unit that neither tune nor the
      references declares (as ``ibub_unit.complete``'s undeclared markers); or a PASS unit naming another toy, data
      file, job, deploy, runner or config, or lacking or failing a declared control.
    - **C-CELLS counts each artifact on its own,** as soon as that artifact verifies, whatever the unit's verdict:
      K = 10 from the ROOT hXSec2D, K = 5 from the npz row. A non-finite K = 10 npz row fails C-K10 (``max_rel`` is
      inf); it is never counted twice.

    ``bound`` holds the job id, the deploy commit and the runner's and config's sha256, which every unit must carry."""
    c2 = cfg["c2"]
    missing, problems, x10, x5, k10 = [], [], [], [], []
    known = {f"toy_{t}_{s}" for t in ("G18", "AR23") for s in c.TOY_SEEDS[t]} | set(iu.REFERENCE_UNITS)
    present = {f[:-len(".done")] for f in os.listdir(units) if f.endswith(".done")}
    problems += [f"{name}: a marker for an undeclared unit" for name in sorted(present - known)]
    nonfinite = {"K10": 0, "K5": 0}
    for s in c.TOY_SEEDS[truth]:
        name = f"toy_{truth}_{s}"
        if any((units / f"{name}.{ext}").is_symlink() for ext in ("done", "root", "npz")):
            missing.append(s)
            problems.append(f"{name}: its marker or a product is a symlink")
            continue
        try:
            marker = json.loads(read_inv(inv, units / f"{name}.done")[0])
        except OSError:
            missing.append(s)
            continue
        except ValueError as e:            # a truncated or empty marker (JSONDecodeError is a ValueError)
            missing.append(s)
            problems.append(f"{name}: its done-marker is not readable JSON ({e})")
            continue
        if not isinstance(marker, dict) or (marker.get("unit"), marker.get("seed")) != (name, s):
            missing.append(s)
            problems.append(f"{name}: its done-marker names {marker.get('unit') if isinstance(marker, dict) else marker!r}")
            continue
        if (str(marker.get("job")), marker.get("deploy_head")) != (str(bound["slurm_job"]), bound["deploy_head"]):
            missing.append(s)                # whatever its verdict: a marker from another job or deploy is a problem
            problems.append(f"{name}: its marker's job/deploy {marker.get('job')}/{marker.get('deploy_head')} "
                            f"is not the bound {bound['slurm_job']}/{bound['deploy_head']}")
            continue
        h = row10 = row5 = z = meta = root = None
        try:                                # each artifact verifies and counts on its own
            root = copy_inv(inv, run, units / f"{name}.root", marker["root_sha256"], f"{name}.root")
            h = np.asarray(cells.vec(root), np.float64)
            nonfinite["K10"] += int((~np.isfinite(h)).sum())
        except (c.Refusal, OSError, KeyError) as e:
            problems.append(f"{name}: its ROOT product is not its marker's ({e})")
        try:
            npz = copy_inv(inv, run, units / f"{name}.npz", marker["sha256"], f"{name}.npz")
            z = np.load(npz)
            meta = json.loads(str(z["meta"]))
            if not isinstance(meta, dict):
                raise ValueError("its meta is not a JSON object")
            if list(z["ks"]) != ks_want:
                problems.append(f"{name}: K scan {list(z['ks'])}")
                z = None
            else:
                row10 = np.asarray(z["xsec"][ks_want.index(c2["primary"])], np.float64)[rep]
                row5 = np.asarray(z["xsec"][ks_want.index(c2["second"])], np.float64)[rep]
                nonfinite["K5"] += int((~np.isfinite(row5)).sum())
        except (c.Refusal, OSError, KeyError, ValueError) as e:
            problems.append(f"{name}: its npz or meta is not readable at its marker's digest ({e})")
            z = None
        if marker.get("verdict") != "PASS":
            missing.append(s)               # absent from the reading; INCOMPLETE unless something else fails
            continue
        if h is None or z is None:
            missing.append(s)
            continue
        if (meta.get("kind"), meta.get("tune"), meta.get("seed")) != ("toy", truth, s):
            problems.append(f"{name}: meta names {meta.get('kind')} {meta.get('tune')} {meta.get('seed')}")
        if meta.get("data_sha256") != shas[s] or marker.get("data_sha256") != shas[s]:
            problems.append(f"{name}: its data file is not toy {s}'s")
        prov = rd.read_provenance(root)
        if prov.get("dataFileSha256") != shas[s]:
            problems.append(f"{name}: dataFileSha256 {prov.get('dataFileSha256')} is not toy {s}'s")
        ctl = meta.get("controls") if isinstance(meta.get("controls"), dict) else {}
        if set(ctl) != iu.CONTROLS["toy"]:
            problems.append(f"{name}: controls {sorted(ctl)} are not the declared {sorted(iu.CONTROLS['toy'])}")
        if not all(isinstance(v, dict) and v.get("pass") is True for v in ctl.values()):
            problems.append(f"{name}: a unit control failed")
        for k in ("slurm_job", "runner_sha256", "config_sha256", "deploy_head"):
            if str(meta.get(k)) != str(bound[k]):
                problems.append(f"{name}: {k} {meta.get(k)} is not the bound {bound[k]}")
        k10.append(iu.max_rel(row10, h))
        x10.append(h)
        x5.append(row5)
    out = {"missing": missing, "problems": problems, "nonfinite": nonfinite}
    if not missing:
        x10, x5 = np.stack(x10), np.stack(x5)
        out.update(x10=x10, x5=x5, k10_vs_root_max_rel=float(max(k10)),
                   negative={"K10": int((x10 < 0).sum()), "K5": int((x5 < 0).sum())})
    return out


def job_code(job_m: str) -> dict:
    """The job's own runner and config, by sha256, from the job's commit ``job_m`` (``--job-m``). The readout may run
    at a later commit. Every unit and the barrier must carry the job's code, not the readout's. ``job_m`` must be a
    40-hex commit that is an ancestor of the readout's HEAD. These are plain git reads of the repository, made before
    Run installs the open audit."""
    if not (isinstance(job_m, str) and len(job_m) == 40 and all(ch in "0123456789abcdef" for ch in job_m)):
        raise c.Refusal(f"--job-m {job_m!r} is not a 40-hex commit")
    anc = subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", job_m, "HEAD"], capture_output=True)
    if anc.returncode != 0:
        raise c.Refusal(f"--job-m {job_m} is not an ancestor of the readout's HEAD (git rc {anc.returncode})")
    out = {}
    for key, rel in (("runner_sha256", "2d-unfolding/ibub/ibub_unit.py"), ("config_sha256", "2d-unfolding/ibub/config.json")):
        blob = subprocess.run(["git", "-C", str(REPO), "cat-file", "blob", f"{job_m}:{rel}"], capture_output=True)
        if blob.returncode != 0:
            raise c.Refusal(f"{rel} is not readable at --job-m {job_m}")
        out[key] = hashlib.sha256(blob.stdout).hexdigest()
    return out


def reference_products(run, units: Path, bound: dict, barrier: dict, inv: dict) -> str | None:
    """Both references, verified, as the barrier names them (codex2 read 3, item 1). For each reference unit, all of
    these must hold:
    - its marker names it, reads PASS and is the bound job's at the bound deploy;
    - the barrier names it passing, with srun rc 0, at the marker's digests;
    - its npz and ROOT products are not symlinks and are, as read now through O_NOATIME (``run.copy``), at those
      digests;
    - the npz's own meta names the same unit, kind, job, deploy, runner and config, and its controls are exactly the
      declared ones (C-REP or C-REP-D, and C-SIM on central), each passing.
    Returns None when both hold, else why."""
    bu = barrier.get("units") if isinstance(barrier.get("units"), dict) else {}
    for u in iu.REFERENCE_UNITS:
        r = bu.get(u) if isinstance(bu.get(u), dict) else {}
        if (units / f"{u}.done").is_symlink():
            return f"{u}'s marker is a symlink"
        try:
            m = json.loads(read_inv(inv, units / f"{u}.done")[0])
        except (OSError, ValueError) as e:
            return f"{u}'s marker is not readable ({e})"
        if not isinstance(m, dict) or (m.get("unit"), m.get("verdict")) != (u, "PASS") \
                or (str(m.get("job")), m.get("deploy_head")) != (str(bound["slurm_job"]), bound["deploy_head"]):
            return f"{u}'s marker is not the bound job's PASS for {u}"
        rc = r.get("srun_rc")
        if not (r.get("pass") is True and type(rc) is int and rc == 0      # a JSON false is not rc 0
                and (r.get("npz_sha256"), r.get("root_sha256")) == (m.get("sha256"), m.get("root_sha256"))):
            return f"refcheck.json's {u} is not a passing reference at its marker's digests"
        try:
            got = {}
            for ext, key in (("npz", "sha256"), ("root", "root_sha256")):
                src = units / f"{u}.{ext}"
                if src.is_symlink():
                    raise c.Refusal(f"{src} is a symlink")
                got[ext] = copy_inv(inv, run, src, m[key], f"ref_{u}.{ext}")
            meta = json.loads(str(np.load(got["npz"])["meta"]))
            if not isinstance(meta, dict):
                raise ValueError("its meta is not a JSON object")
        except (c.Refusal, OSError, KeyError, ValueError) as e:
            return f"{u}'s products are not at the barrier's digests ({e})"
        if (meta.get("unit"), meta.get("kind"), str(meta.get("slurm_job")), meta.get("deploy_head")) != \
                (u, u, str(bound["slurm_job"]), bound["deploy_head"]):
            return f"{u}'s npz meta names {meta.get('unit')}/{meta.get('kind')}/{meta.get('slurm_job')}/{meta.get('deploy_head')}"
        for k in ("runner_sha256", "config_sha256"):
            if meta.get(k) != bound[k]:
                return f"{u}'s npz meta has {k} {meta.get(k)}, not the job's {bound[k]}"
        ctl = meta.get("controls") if isinstance(meta.get("controls"), dict) else {}
        if set(ctl) != iu.CONTROLS[u] or not all(isinstance(v, dict) and v.get("pass") is True for v in ctl.values()):
            return f"{u}'s controls {sorted(ctl)} are not the declared {sorted(iu.CONTROLS[u])}, each passing"
    return None


# sacct States that end a job. Anything else (PENDING, RUNNING, REQUEUED, SUSPENDED, any other) or no row is not
# terminal, and the readout STOPs before it reads anything else (the director's ruling of 2026-11-24).
TERMINAL = {"COMPLETED", "FAILED", "TIMEOUT", "CANCELLED", "OUT_OF_MEMORY", "NODE_FAIL"}


def sacct_state(records: Path, job: str) -> dict:
    """The job's sacct row from the fetch (``sacct-<job>.txt``, `sacct -j <job> -X -P -o JobID,JobName,State,ExitCode`,
    checked against its RECORDS.SHA256SUMS line), classified in code. It reads only those two files. Raises
    c.Refusal (a STOP: nothing is read or graded) unless exactly one row is the job's, as ibub_run, in a terminal
    State. "CANCELLED by <uid>" reads CANCELLED."""
    rel = f"sacct-{job}.txt"
    try:
        sums = cb.read_noatime(records / "RECORDS.SHA256SUMS")[0].decode()
        data, got = cb.read_noatime(records / rel)
    except (OSError, UnicodeDecodeError) as e:
        raise c.Refusal(f"STOP: the fetch's sacct record is not readable ({e})")
    want = [ln[:64] for ln in sums.splitlines() if ln[64:] == f"  {rel}"]
    if want != [got]:
        raise c.Refusal(f"STOP: {rel} is not at its RECORDS.SHA256SUMS line")
    rows = [r.split("|") for r in data.decode(errors="replace").splitlines()]
    mine = [r for r in rows if r and r[0] == str(job)]
    if len(mine) != 1 or len(mine[0]) < 4:
        raise c.Refusal(f"STOP: sacct has {len(mine)} rows for job {job} (a missing row is never read as finished)")
    _, name, state, code = mine[0][:4]
    word = state.split()[0] if state.split() else ""
    if name != "ibub_run" or word not in TERMINAL:
        raise c.Refusal(f"STOP: job {job} ({name}) is {state!r}, not terminal")
    return {"JobName": name, "State": state, "ExitCode": code}


def scontrol_key(text: str, key: str) -> str:
    """The job's own key rule: the first space- or line-separated token ``key=...``, its value ('' if none)."""
    for tok in text.replace(" ", "\n").split("\n"):
        if tok.startswith(key + "="):
            return tok[len(key) + 1:]
    return ""


QOS = {"regular", "regular_1"}      # the declared QOS and Perlmutter's recorded spelling of it, exactly


def allocation_ok(text: str, lanes: int = 4, mem_mb: int = 114688, cpus: int = 64) -> str | None:
    """The batch's scontrol record, re-parsed as the job parses it: JobName=ibub_run, QOS in exactly {regular,
    regular_1} (Perlmutter records --qos=regular as regular_1, receipts-cov2d/a2/bulk/complete/connect-complete-1.log.txt:78),
    TimeLimit=11:29:00, NumNodes=1, OverSubscribe=NO, and AllocTRES fitting four steps of 112G and 64 CPUs. Returns
    None when it holds, else why."""
    if scontrol_key(text, "QOS") not in QOS:
        return f"QOS is {scontrol_key(text, 'QOS')!r}, not one of {{regular, regular_1}}"
    for k, v in (("JobName", "ibub_run"), ("TimeLimit", "11:29:00"), ("NumNodes", "1"), ("OverSubscribe", "NO")):
        if scontrol_key(text, k) != v:
            return f"{k} is {scontrol_key(text, k)!r}, not {v}"
    tres = dict(t.partition("=")[::2] for t in scontrol_key(text, "AllocTRES").split(",") if "=" in t)
    mem, cpu = tres.get("mem", ""), tres.get("cpu", "")
    unit = {"M": 1, "G": 1024}.get(mem[-1:])
    amem = int(mem[:-1]) * unit if unit and mem[:-1].isdigit() else None
    if amem is None or not cpu.isdigit():
        return f"the allocation is not readable from AllocTRES {scontrol_key(text, 'AllocTRES')!r}"
    if lanes * mem_mb > amem or lanes * cpus > int(cpu):
        return f"{lanes} steps do not fit (mem {amem}M, cpu {cpu})"
    return None


# the job's line once every allocation check holds (jobs/ibub_job.sbatch, `say "allocation: ..."`)
ALLOCATION_LINE = "[ibub] allocation: ibub_run regular 11:29:00 1 node exclusive;"


def fetched_records(records: Path, job: str) -> dict:
    """The readout connect's fetch of the job's records: {relative path: bytes}, every RECORDS.SHA256SUMS line
    verified by an O_NOATIME read. The fetch must list the records the job-wide checks read. Raises c.Refusal."""
    try:
        raw = cb.read_noatime(records / "RECORDS.SHA256SUMS")[0].decode()
    except (OSError, UnicodeDecodeError) as e:
        raise c.Refusal(f"RECORDS.SHA256SUMS is not readable in {records} ({e})")
    out = {}
    for line in raw.splitlines():
        want, sep, rel = line.partition("  ")
        if not (sep and len(want) == 64 and all(ch in "0123456789abcdef" for ch in want)) or not rel \
                or rel.startswith("/") or ".." in Path(rel).parts or rel in out:
            raise c.Refusal(f"RECORDS.SHA256SUMS has a malformed or repeated line {line!r}")
        try:
            data, got = cb.read_noatime(records / rel)
        except OSError as e:
            raise c.Refusal(f"the fetched record {rel} is not readable ({e})")
        if got != want:
            raise c.Refusal(f"the fetched record {rel} is {got}, not RECORDS.SHA256SUMS's {want}")
        out[rel] = data
    need = {"units/refcheck.json", "stage/stage.json", f"logs/scontrol-batch-{job}.txt", f"slurm/ibub_run-{job}.out",
            f"sacct-{job}.txt"}
    if need - set(out):
        raise c.Refusal(f"the fetch lacks {sorted(need - set(out))}")
    return out


def terminal_state(recs: dict) -> dict:
    """Disclosed beside the readings, whatever it is, and never a gate (the director's ruling of 2026-11-24): whether
    IBUB-DONE was published (its sha256, stage, rc and completion verdict), and complete.json's verdict. sacct's State
    and ExitCode join it in ``readout``, from ``sacct_state``."""
    done = recs.get("IBUB-DONE")
    out = {"ibub_done": None}
    if done is not None:
        try:
            d = json.loads(done)
        except ValueError:
            d = {}
        d = d if isinstance(d, dict) else {}
        out["ibub_done"] = {"sha256": hashlib.sha256(done).hexdigest(), "stage": d.get("stage"), "rc": d.get("rc"),
                            "completion": (d.get("completion") or {}).get("verdict")
                            if isinstance(d.get("completion"), dict) else None}
    try:
        comp = json.loads(recs["logs/complete.json"]) if "logs/complete.json" in recs else None
    except ValueError:
        comp = None
    out["complete_json"] = comp.get("verdict") if isinstance(comp, dict) else None
    return out


def job_wide(run, units: Path, records: Path, bound: dict, inv: dict) -> dict:
    """The job-wide prerequisites (the director's ruling of 2026-11-24). If any fails or is missing, neither tune is
    graded and the reason is named:
    - the fetch verifies (``fetched_records``);
    - stage.json reads PASS;
    - the allocation: the batch's stdout carries the job's allocation line exactly once, and its scontrol record
      names this job and, re-parsed here (``allocation_ok``), is the declared allocation;
    - the barrier: the fetched refcheck.json is units/refcheck.json byte for byte, the bound job's PASS at the bound
      deploy by the job's runner, both references passing with srun rc 0, and central_df against central (C-REP)
      passing;
    - both references verified (``reference_products``);
    - IBUB-DONE, if published, is the bound job's at the bound deploy at stage toys, and binds that barrier.
    The job's terminal state is disclosed (``terminal_state``) and never gates: each tune is then graded by C-COMPLETE
    alone."""
    job = str(bound["slurm_job"])
    try:
        recs = fetched_records(records, job)
    except c.Refusal as e:
        return {"pass": False, "why": str(e)}
    out = {"terminal": terminal_state(recs), "records": len(recs),
           "records_sha256sums_sha256": hashlib.sha256(cb.read_noatime(records / "RECORDS.SHA256SUMS")[0]).hexdigest()}
    inv[str(records / "RECORDS.SHA256SUMS")] = out["records_sha256sums_sha256"]
    for rel, data in recs.items():                    # every fetched record, at the digest its sums line verified
        inv[str(records / rel)] = hashlib.sha256(data).hexdigest()

    def fail(why: str) -> dict:
        return {"pass": False, "why": why, **out}
    if (units / "refcheck.json").is_symlink():
        return fail("units/refcheck.json is a symlink")
    try:
        st = json.loads(recs["stage/stage.json"])
        b = json.loads(recs["units/refcheck.json"])
        braw, bsha = read_inv(inv, units / "refcheck.json")
    except (OSError, ValueError) as e:
        return fail(f"stage.json or refcheck.json is not readable ({e})")
    if not (isinstance(st, dict) and st.get("verdict") == "PASS"):
        return fail("stage.json does not read PASS")
    lines = recs[f"slurm/ibub_run-{job}.out"].decode(errors="replace").splitlines()
    if sum(ln.startswith(ALLOCATION_LINE) for ln in lines) != 1:
        return fail("the batch's stdout does not carry the allocation line exactly once")
    scon = recs[f"logs/scontrol-batch-{job}.txt"].decode(errors="replace")
    if scontrol_key(scon, "JobId") != job:
        return fail(f"the batch's scontrol record names job {scontrol_key(scon, 'JobId')!r}, not {job}")
    why = allocation_ok(scon)
    if why is not None:
        return fail(f"the batch's scontrol record: {why}")
    if braw != recs["units/refcheck.json"]:
        return fail("the fetched refcheck.json is not units/refcheck.json")
    if not isinstance(b, dict):
        return fail("refcheck.json is not a JSON object")
    want = {"verdict": "PASS", "job": job, "deploy_head": bound["deploy_head"], "runner_sha256": bound["runner_sha256"]}
    got = {k: (str(b.get(k)) if k == "job" else b.get(k)) for k in want}
    if got != want:
        return fail(f"refcheck.json is {got}, not {want}")
    cdc = b.get("central_df_vs_central")
    if not (isinstance(cdc, dict) and cdc.get("pass") is True):
        return fail("C-REP: refcheck.json's central_df against central does not pass")
    why = reference_products(run, units, bound, b, inv)
    if why is not None:
        return fail(why)
    if "IBUB-DONE" in recs:
        try:
            d = json.loads(recs["IBUB-DONE"])
        except ValueError:
            d = None
        comp = d.get("completion") if isinstance(d, dict) else None
        if not isinstance(d, dict) or (str(d.get("job")), d.get("M"), d.get("stage")) != (job, bound["deploy_head"], "toys"):
            return fail("IBUB-DONE is not the bound job's, at the bound deploy, at stage toys")
        if isinstance(comp, dict) and comp.get("barrier_sha256") not in (None, bsha):
            return fail(f"IBUB-DONE binds barrier {comp.get('barrier_sha256')}, refcheck.json is {bsha}")
    return {"pass": True, "barrier_sha256": bsha, **out}


def check_write_root(root) -> str:
    """The declared readout root (config.json readout.write_root) must already be a real directory at exactly its
    declared path (codex2 read 3, item 2): absolute; neither it nor any ancestor a symlink; owned by this user; not
    writable by group or others. Returns it."""
    root = str(root)
    if not os.path.isabs(root):
        raise c.Refusal(f"the readout root {root} is not absolute")
    try:
        st = os.lstat(root)
    except OSError as e:
        raise c.Refusal(f"the readout root {root} does not exist ({e})")
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
        raise c.Refusal(f"the readout root {root} is not a real directory")
    if os.path.realpath(root) != os.path.normpath(root):
        raise c.Refusal(f"the readout root {root} resolves to {os.path.realpath(root)}")
    if st.st_uid != os.getuid() or st.st_mode & 0o022:
        raise c.Refusal(f"the readout root {root} is not this user's private directory "
                        f"(uid {st.st_uid}, mode {stat.S_IMODE(st.st_mode):o})")
    return os.path.normpath(root)


def guard_off_tree(path, what: str) -> None:
    """``path`` (resolved) must not lie under a guarded tree, where the open audit refuses every plain open."""
    real = os.path.realpath(path)
    for g in (os.path.realpath(x) for x in cb.GUARDED):
        if real == g or real.startswith(g + os.sep):
            raise c.Refusal(f"{what} {path} resolves under {g}: the open audit refuses every plain open there")


def publish(out: Path, name: str, rec: dict) -> None:
    (out / name).write_text(json.dumps(rd.jsonable(rec), indent=1, sort_keys=True))


def guard_in_root(path, root, what: str) -> None:
    """``path`` (resolved) must lie under the declared readout write root (config.json readout.write_root, which
    ibub_overlap.py lists among the readout's writes). No other destination is written."""
    real, r = os.path.realpath(path), os.path.realpath(root)
    if not (real == r or real.startswith(r + os.sep)):
        raise c.Refusal(f"{what} {path} resolves to {real}, outside the declared readout root {r}")


# ------------------------------------------------------------------------------------------- the readout


@contextlib.contextmanager
def private_tmp(tmp_root: str):
    """A temporary directory under ``tmp_root``, with tempfile's default pointed there too while it is open, so no
    library's temporary file lands anywhere else. Both are restored on exit."""
    saved, tempfile.tempdir = tempfile.tempdir, tmp_root
    try:
        with tempfile.TemporaryDirectory(dir=tmp_root) as td:
            yield td
    finally:
        tempfile.tempdir = saved


def check_out(out: Path, root: str) -> None:
    """``out`` must be absent, and its parent a real directory under the declared root at exactly its own path (no
    symlink on the way), checked before anything is created beside it (codex2 read 3, item 2)."""
    if out.exists() or out.is_symlink():
        raise c.Refusal(f"--out {out} exists")
    parent = os.path.abspath(out.parent)
    try:
        st = os.lstat(parent)
    except OSError as e:
        raise c.Refusal(f"--out's parent {parent} does not exist ({e})")
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode) or os.path.realpath(parent) != os.path.normpath(parent):
        raise c.Refusal(f"--out's parent {parent} is not a real directory at its own path")
    guard_in_root(parent, root, "--out's parent")


def readout(truth: str, units: Path, out: Path, run_dir: str, job: str, job_m: str, records: Path) -> dict:
    """The declared readings at one tune. Every control failure or refusal is recorded (INVALID or INCOMPLETE, with
    its reason and no reading). Everything is first built in a private staging directory beside ``out``: the audit's
    record (Run.finish, whose atime, open-audit and module checks run there), then, only if that reads PASS, the
    readings and the errors npz. The staging directory then becomes ``out`` by one atomic rename. ``out`` never
    exists partly written, and a PASS record never exists without its npz, whose sha256 it names.

    Before anything is written, the declared root (config.json readout.write_root) must be a real, private directory
    at its own path (``check_write_root``), ``out`` must be absent with its parent a real directory under that root
    (``check_out``), and the temporary root (TMPDIR, else the declared root) must lie under it. ``job_m`` is the job's
    commit (``--job-m``): every unit, the barrier and IBUB-DONE must carry its deploy and its runner and config.
    ``records`` is the readout connect's fetch of the job's records (``--records``), which ``job_wide`` reads."""
    # every plain read of the repository happens here, before Run installs the open audit
    cfg = iu.load_config()
    iu.check_code(cfg)
    rcfg, pins = cfg["readout"], cfg["cov2d_records"][truth]
    root = check_write_root(rcfg["write_root"])
    tmp_root = os.environ.get("TMPDIR") or root
    for path, what in ((out, "--out"), (tmp_root, "the temporary root")):
        guard_off_tree(path, what)
        guard_in_root(path, root, what)
    check_out(out, root)
    terminal = sacct_state(records, str(job))       # STOP unless the job has ended: before any other read
    bound = {"slurm_job": str(job), "deploy_head": job_m, **job_code(job_m)}
    try:                        # a pinned input that fails is recorded below, through the diagnostic path (item 4)
        shas, rep_cfg, pre = iu.toy_shas(cfg, truth), iu.reported_cells(cfg), None
    except (c.Refusal, iu.GateFailure, OSError, ValueError, KeyError) as e:
        shas = rep_cfg = None
        pre = f"{type(e).__name__}: {e}"
    own = {"schema": SCHEMA, "units": str(units), "config_sha256": iu.rc.sha256(iu.CONFIG),
           "readout_sha256": iu.rc.sha256(Path(__file__).resolve()), "unit_sha256": iu.rc.sha256(Path(iu.__file__)),
           "job": str(job), "job_m": job_m, "job_runner_sha256": bound["runner_sha256"],
           "job_config_sha256": bound["config_sha256"], "sacct": terminal}
    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.staging-", dir=out.parent))     # private until the rename
    guard_in_root(stage, root, "the staging directory")
    name = f"ibub_{truth}.json"

    def publish_stage() -> None:
        os.rename(stage, out)

    with private_tmp(tmp_root) as td:     # the private copies, as phase_score's
        run = rd.Run(truth, run_dir, Path(td))
        rec = run.rec
        rec.update(own)
        inv = rec["inventory"] = {}                     # every graded byte: path -> sha256, each from its one read
        if pre is None:     # read before the audit by toy_shas and reported_cells, each equal to its pin or refused
            inv[str(REPO / cfg["toys"][truth]["pseudo_b"])] = cfg["toys"][truth]["pseudo_b_sha256"]
            inv[str(REPO / cfg["cells"]["blocks"])] = cfg["cells"]["blocks_sha256"]

        def invalid(why: str) -> dict:
            rec["controls_failed"].append(why)
            final = run.finish(stage, name)
            publish_stage()
            return final
        try:
            try:
                if pre is not None:
                    raise c.Refusal(f"a pinned input: {pre}")
                B = dict(np.load(io.BytesIO(pinned_inv(inv, REPO / pins["blocks"], pins["blocks_sha256"]))))
                score = json.loads(pinned_inv(inv, REPO / pins["score"], pins["score_sha256"]))
                er = copy_inv(inv, run, f"{run.ro.NS_R}/out/ER/xsec.root", run.ro.partb_sums()["ER/xsec.root"],
                              "ER.root")                  # as Run.er_cells, with the digest inventoried
                cells = run.ro.Cells(er)
                rep = np.asarray(cells.rep, bool)
                if not (np.array_equal(rep, B["rep"].astype(bool)) and np.array_equal(rep, rep_cfg)):
                    return invalid("C-TRUTH: E_R's cells differ from the blocks record's or the config's")
                flat = [int(i) for i in np.flatnonzero(rep)]
                comp = rd.completeness(truth)               # read_pinned: equal to its pin or refused
                inv[str(rd.COMPLETENESS[0])] = rd.COMPLETENESS[1]
                pl = rd.plan(truth, comp)
                if pl["toy"] != [f"T_{truth}_{s}" for s in c.TOY_SEEDS[truth]]:
                    return invalid("C-TRUTH: the OmniFold labels are not the declared seeds in order")
                files = {lab: copy_inv(inv, run, f"{run_dir}/out/{lab}/xsec.root", comp[lab]["sha256"], f"{lab}.root")
                         for lab in pl["toy"]}
                x_of = np.stack([cells.vec(files[lab]) for lab in pl["toy"]])
                tpath = rd.inventory_paths(run_dir, truth)["truth_xsec_npz"]
                run.watch(tpath)                                  # the truth file joins the atime ledger
                txs = np.load(io.BytesIO(pinned_inv(inv, tpath, pins["truth_xsec_sha256"])))
                pa = json.loads(pinned_inv(inv, rd.REC / "pseudo" / truth / "pseudo_a.json", rd.PSEUDO_A_SHA[truth]))
                ratio_rec = json.loads(pinned_inv(inv, *rd.C2_RECORD))
                weakened = c.weakened_cells(ratio_rec["b"][truth]["variance_ratio"]["option_1_clipped"],
                                            ratio_rec["efficiency"]["cells205"])
            except c.Refusal as e:                    # an input off its pin, or a plan refusal: recorded, no reading
                rec["refused"] = str(e)
                return invalid(f"refused: {e}")
            except (OSError, ValueError, KeyError) as e:   # an input absent or unreadable: recorded, with its name
                rec["refused"] = f"{type(e).__name__}: {e}"
                return invalid(f"an input is absent or unreadable: {e}")
            natures = pa["natures"]
            nseeds = [int(s) for s in txs["seeds"]]
            if nseeds != [n["seed"] for n in natures]:
                return invalid("C-TRUTH: truth_xsec.npz's rows are not pseudo_a's natures in order")
            if [n["seed"] for n in natures if n["role"] == "toy"] != list(c.TOY_SEEDS[truth]):
                return invalid("C-TRUTH: pseudo_a's toys are not the declared seeds in order")
            xs = np.asarray(txs["xsec"], np.float64).reshape(len(nseeds), -1)[:, rep]
            x_true = xs[[nseeds.index(s) for s in c.TOY_SEEDS[truth]]]
            bands = {k[len("band__"):]: v for k, v in B.items() if k.startswith("band__")}
            deltas = cs.lateral_deltas(bands, B["minos_x"])
            E_post, _ = cs.errors(x_of, x_true, natures, deltas, B["C_T"])
            E_of = x_of - x_true
            rec["C-OF"] = c_of(E_post, B["C_T"], B["C_model_abs"], score["readouts"])
            if not rec["C-OF"]["pass"]:
                rec["controls_failed"].append("C-OF")
            rec["C-JOB"] = job_wide(run, units, records, bound, inv)
            rec["job_terminal"] = {"sacct": {k: rec["sacct"][k] for k in ("State", "ExitCode")},   # disclosed,
                                   **(rec["C-JOB"].get("terminal") or {})}                # whatever it is
            if not rec["C-JOB"]["pass"]:
                rec["controls_failed"].append(f"C-JOB: a job-wide prerequisite fails ({rec['C-JOB']['why']})")
            ibu = ibu_products(run, units, truth, shas, list(cfg["c2"]["scan"]), rep, cells, cfg, bound, inv)
            rec["C-COMPLETE"] = {"units": len(c.TOY_SEEDS[truth]) - len(ibu["missing"]), "missing": ibu["missing"]}
            rec["C-DATA"] = {"problems": ibu["problems"]}
            if ibu["problems"]:
                rec["controls_failed"].append(f"C-DATA/C-TRUTH: {len(ibu['problems'])} problems")
            rec["C-CELLS"] = {"nonfinite": ibu["nonfinite"], "negative": ibu.get("negative"),
                              "pass": ibu["nonfinite"] == {"K10": 0, "K5": 0}}
            if not rec["C-CELLS"]["pass"]:
                rec["controls_failed"].append("C-CELLS")
            if ibu["missing"]:                          # C-COMPLETE, per tune as declared; never the job's status
                if not rec["controls_failed"]:
                    rec["verdict"] = "INCOMPLETE"
                final = run.finish(stage, name)
                publish_stage()
                return final
            rec["C-K10"] = {"max_rel": ibu["k10_vs_root_max_rel"], "rtol": rcfg["k10_vs_root_rtol"],
                            "pass": ibu["k10_vs_root_max_rel"] <= rcfg["k10_vs_root_rtol"]}
            if not rec["C-K10"]["pass"]:
                rec["controls_failed"].append("C-K10")
            if rec["controls_failed"]:
                final = run.finish(stage, name)
                publish_stage()
                return final
            W, labels = test_matrix(flat, cells.area)
            if W.shape[1] != rcfg["tests"]:
                return invalid(f"{W.shape[1]} tests, not the declared {rcfg['tests']}")
            boot_seed = [rcfg["bootstrap_seed"], rcfg["tune_index"][truth]]
            counts = bootstrap_counts(len(x_true), rcfg["bootstrap_B"], boot_seed)
            E5, E10 = ibu["x5"] - x_true, ibu["x10"] - x_true
            readings = {f"K{k}": statistics(E_of, E, x_true, W, labels, B["C_T"], counts, rcfg["alpha"], len(flat))
                        for k, E in ((10, E10), (5, E5))}
            sigma = np.sqrt(np.diag(B["C_T"]))
            named = {}
            for g in score["grade"]["flagged_cells"]:
                i = flat.index(int(g))
                named[str(g)] = {f"K{k}": {"b_OF": float(E_of[:, i].mean()), "b_IBU": float(E[:, i].mean()),
                                           "d": float((E - E_of)[:, i].mean())} for k, E in ((10, E10), (5, E5))}
            pending = {
                "bootstrap": {"B": rcfg["bootstrap_B"], "seed": boot_seed},
                "readings": readings,
                "reading": {k: v["reading"] for k, v in readings.items()},
                "descriptive": {
                    "surrogate_realized_mean_in_sigma": ((E_post - E_of).mean(axis=0) / sigma).tolist(),
                    "cov2d_flagged_cells": named,
                    "weakened_cells": weakened}}
            arrays = dict(seeds=np.array(list(c.TOY_SEEDS[truth])), flat=np.array(flat), E_of=E_of, E_ibu10=E10,
                          E_ibu5=E5, x_true=x_true, x_of=x_of)
        except Exception:
            cb.AUDIT is not None and cb.AUDIT.uninstall()
            raise
        final = run.finish(stage, name)            # the atime, open-audit and module checks; STOP outranks a reading
        if final["verdict"] == "PASS":
            npz_name = f"ibub_{truth}_errors.npz"
            np.savez_compressed(stage / npz_name, **arrays)
            final.update(pending, errors_npz=npz_name, errors_npz_sha256=iu.rc.sha256(stage / npz_name))
            publish(stage, name, final)
        publish_stage()                            # the whole result appears at once
        return final


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--truth", required=True, choices=sorted(c.TOY_SEEDS))
    ap.add_argument("--units", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--run-dir", default=rd.RUN_DIR)
    ap.add_argument("--job", required=True, help="the bound job's id, which every unit must have run under")
    ap.add_argument("--job-m", required=True, help="the job's commit (IBUB-DONE's M), whose runner and config bind")
    ap.add_argument("--records", type=Path, required=True,
                    help="the readout connect's fetch of the job's records, with RECORDS.SHA256SUMS")
    a = ap.parse_args(argv)
    try:
        rec = readout(a.truth, a.units, a.out, a.run_dir, a.job, a.job_m, a.records)
    except c.Refusal as e:                         # refused before any record: nothing was graded or written
        print(f"IBUB-READOUT {a.truth} REFUSED: {e}")
        return 4
    print(f"IBUB-READOUT {a.truth} {rec['verdict']} reading={rec.get('reading')} "
          f"controls_failed={len(rec['controls_failed'])} stops={len(rec['stop'])}")
    return 0 if rec["verdict"] == "PASS" else 3


if __name__ == "__main__":
    sys.exit(main())
