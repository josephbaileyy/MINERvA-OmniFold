#!/usr/bin/env python3
"""Fresh-checkout reproduction harness for the already-final s5p components.

Scope (declared in ``scope.py``): the flux-repaired generator predictions and their input identities, the
deliverable generator figures and numbers built from them (VL156-VL160), and the pre-freeze quantities of the
joint-test design (F2, F4, M1, V, the null-T units, the development power, the study-P envelope). The final joint
result is a declared slot (tier D) that stays PENDING until its terminal products exist.

Tiers, never merged in the report:

* **A, replay**: every digest the committed receipts record, re-measured on the preserved bytes; the committed
  producers compared with the copies that ran; committed numbers recomputed from the stored products.
* **B, derived regeneration**: the committed producers re-run from THIS checkout into a fresh output directory on
  the preserved inputs, and their outputs compared with the committed receipts, logs and figures.
* **C, full scientific regeneration**: declared with its dependency and reported NOT_RUN (event generation,
  flux reweighting from events, production unfolding).
* **D, final joint result**: PENDING until the terminal products are committed and independently verified.

Usage::

    python3 reproduction/s5p/repro_s5p.py list
    python3 reproduction/s5p/repro_s5p.py pin --config CONFIG --out PINS.json
    python3 reproduction/s5p/repro_s5p.py run --config CONFIG [--tiers A,B,C,D] [--pins PINS.json]

Every input location comes from the config (``config.example.json``); recorded absolute paths are identities that
are re-rooted, never read. The output directory must be new and outside the checkout and every input root.
Exit status of ``run``: 0 if every tier-A/B check reproduced, 1 on any mismatch, 2 if an input or the
environment was missing (nothing is reported reproduced that was not measured).

MEASURES: agreement of regenerated/replayed values with the committed ones. CANNOT AUTHORIZE: any physics claim,
adoption or release; agreement verifies the calculation, not its scientific adequacy.
"""
from __future__ import annotations

import argparse
import datetime
import glob
import hashlib
import json
import math
import os
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True  # the checkout under test must stay clean
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import scope as S  # noqa: E402

A, B, C, D = "A-replay", "B-regenerate", "C-not-regenerated", "D-joint"
REPRODUCED = "REPRODUCED"                 # bitwise / exact equality
WITHIN_TOL = "REPRODUCED_WITHIN_TOLERANCE"
MISMATCH = "MISMATCH"
DECLARED = "DECLARED_DIFFERENCE"          # a known, documented non-reproducible record (still measured)
INPUT_MISSING = "INPUT_MISSING"
ENV_MISSING = "ENV_MISSING"
NOT_RUN = "NOT_RUN"
PENDING = "PENDING"
INFO = "INFO"
FAILING = {MISMATCH}
MISSING = {INPUT_MISSING, ENV_MISSING}
HEX64 = re.compile(r"^[0-9a-f]{64}$")


@dataclass
class Result:
    check: str
    tier: str
    status: str
    detail: dict = field(default_factory=dict)


# ----------------------------------------------------------------------------------------------- utilities

def sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def is_hex64(v) -> bool:
    return isinstance(v, str) and bool(HEX64.match(v))


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


class Roots:
    """Configured input roots; maps a recorded absolute path onto them (longest recorded prefix wins)."""

    def __init__(self, configured: dict):
        missing = sorted(set(S.RECORDED_ROOTS) - set(configured))
        if missing:
            raise SystemExit(f"config roots missing: {missing}")
        for k, v in configured.items():
            if not Path(v).is_absolute():
                raise SystemExit(f"config root {k} must be an absolute path, got {v!r}")
        self.configured = dict(configured)
        self.local_roots = {k: Path(v) for k, v in configured.items()}
        self._order = sorted(S.RECORDED_ROOTS.items(), key=lambda kv: -len(kv[1]))

    def local(self, recorded: str) -> Path | None:
        for name, prefix in self._order:
            if recorded == prefix or recorded.startswith(prefix + "/"):
                return self.local_roots[name] / recorded[len(prefix):].lstrip("/")
        return None

    def spec(self, spec: str) -> Path:
        """``name:relative/path`` onto the configured root."""
        name, rel = spec.split(":", 1)
        return self.local_roots[name] / rel

    def rebase(self, obj):
        """Every string that starts with a recorded prefix, re-rooted (for designs and expected values)."""
        if isinstance(obj, dict):
            return {self.rebase(k) if isinstance(k, str) else k: self.rebase(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self.rebase(v) for v in obj]
        if isinstance(obj, str):
            p = self.local(obj)
            return str(p) if p is not None else obj
        return obj

    def identity(self) -> bool:
        """True when every configured root IS the recorded location (the designs then need no re-rooting)."""
        return all(self.configured[k].rstrip("/") == v for k, v in S.RECORDED_ROOTS.items())


def compare(expected, observed, tol: float, path: str = "", out: list | None = None) -> tuple[str, list]:
    """Recursive comparison: REPRODUCED if every leaf is equal, WITHIN_TOL if some float differs by at most
    ``tol`` (relative), else MISMATCH with the first differences."""
    diffs = [] if out is None else out
    worst = [REPRODUCED]

    def leaf(e, o, p):
        if isinstance(e, bool) or isinstance(o, bool) or not isinstance(e, (int, float)) or not isinstance(o, (int, float)):
            if e != o or type(e) is not type(o) and bool in (type(e), type(o)):  # True == 1 in Python
                diffs.append({"at": p, "expected": e, "observed": o})
                worst[0] = MISMATCH
            return
        e, o = float(e), float(o)
        if e == o or (math.isnan(e) and math.isnan(o)):
            return
        rel = abs(e - o) / max(abs(e), abs(o))
        if rel <= tol:
            if worst[0] == REPRODUCED:
                worst[0] = WITHIN_TOL
            if len(diffs) < 50:
                diffs.append({"at": p, "expected": e, "observed": o, "rel": rel, "within_tol": True})
        else:
            diffs.append({"at": p, "expected": e, "observed": o, "rel": rel})
            worst[0] = MISMATCH

    def walk(e, o, p):
        if isinstance(e, dict) and isinstance(o, dict):
            if set(e) != set(o):
                diffs.append({"at": p, "keys_only_expected": sorted(set(e) - set(o)), "keys_only_observed": sorted(set(o) - set(e))})
                worst[0] = MISMATCH
            for k in sorted(set(e) & set(o), key=str):
                walk(e[k], o[k], f"{p}.{k}")
        elif isinstance(e, (list, tuple)) and isinstance(o, (list, tuple)):
            if len(e) != len(o):
                diffs.append({"at": p, "expected_len": len(e), "observed_len": len(o)})
                worst[0] = MISMATCH
            for i, (x, y) in enumerate(zip(e, o)):
                walk(x, y, f"{p}[{i}]")
        else:
            leaf(e, o, p)

    walk(expected, observed, path)
    return worst[0], [d for d in diffs if not d.get("within_tol")][:20] or diffs[:20]


def compare_arrays(expected: dict, observed: dict, tol: float) -> tuple[str, list]:
    """Named arrays: bitwise first, then relative tolerance on floats."""
    diffs, status = [], REPRODUCED
    for k in sorted(set(expected) | set(observed)):
        if k not in expected or k not in observed:
            diffs.append({"array": k, "present_only_in": "expected" if k in expected else "observed"})
            status = MISMATCH
            continue
        e, o = np.asarray(expected[k]), np.asarray(observed[k])
        if e.shape != o.shape or e.dtype.kind != o.dtype.kind:
            diffs.append({"array": k, "expected": f"{e.dtype}{e.shape}", "observed": f"{o.dtype}{o.shape}"})
            status = MISMATCH
        elif e.dtype.kind in "fc":
            if np.array_equal(e, o, equal_nan=True):
                continue
            scale = np.maximum(np.abs(e), np.abs(o))
            rel = np.where(scale > 0, np.abs(e - o) / np.where(scale > 0, scale, 1), 0.0)
            rel = np.where(np.isnan(e) & np.isnan(o), 0.0, rel)
            m = float(np.nanmax(rel)) if rel.size else 0.0
            if m <= tol:
                status = WITHIN_TOL if status == REPRODUCED else status
                diffs.append({"array": k, "max_rel": m, "within_tol": True})
            else:
                diffs.append({"array": k, "max_rel": m})
                status = MISMATCH
        elif not np.array_equal(e, o):
            diffs.append({"array": k, "differs": True})
            status = MISMATCH
    return status, diffs


def npz_arrays(path) -> dict:
    with np.load(path, allow_pickle=False) as z:
        return {k: np.asarray(z[k]) for k in z.files}


def declared_digests(obj, trail: tuple = ()):
    """Every (recorded path, sha256, json trail) a receipt declares, in the shapes the s5p receipts use:
    {path, sha256}; {copy_of, sha256}; {K: path, K_sha256: digest}; {"/abs/path": digest}."""
    if isinstance(obj, dict):
        if isinstance(obj.get("path"), str) and is_hex64(obj.get("sha256")):
            yield obj["path"], obj["sha256"], trail
        if isinstance(obj.get("copy_of"), str) and is_hex64(obj.get("sha256")):
            yield obj["copy_of"], obj["sha256"], trail
        for k, v in obj.items():
            if isinstance(v, str) and is_hex64(obj.get(f"{k}_sha256")):
                yield v, obj[f"{k}_sha256"], trail + (k,)
            if isinstance(k, str) and is_hex64(v) and (k.startswith("/") or k.startswith("docs/")):
                yield k, v, trail + (k,)
            if isinstance(k, str) and k.startswith("docs/") and isinstance(v, dict) and is_hex64(v.get("sha256")):
                yield k, v["sha256"], trail + (k,)
            yield from declared_digests(v, trail + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from declared_digests(v, trail + (i,))


def get_path(obj, keys):
    for k in keys:
        obj = obj[k]
    return obj


def git_blob_sha256(commit: str, rel: str) -> str | None:
    """sha256 of ``rel`` as committed at ``commit`` in the checkout's history (None if absent there)."""
    r = subprocess.run(["git", "-C", str(REPO), "show", f"{commit}:{rel}"], capture_output=True)
    return hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 else None


def git_commit_with_blob(rel: str, want: str) -> str | None:
    """The newest commit whose ``rel`` hashes to ``want`` (a recorded producer digest), if any."""
    log = subprocess.run(["git", "-C", str(REPO), "log", "--format=%H", "--", rel], capture_output=True, text=True)
    for c in log.stdout.split():
        if git_blob_sha256(c, rel) == want:
            return c
    return None


_DEPLOY = re.compile(r"^/pscratch/sd/j/josephrb/s5p-20260926/deploy/([0-9a-f]{7,40})/(.+)$")


# ----------------------------------------------------------------------------------------------- the run

class Harness:
    def __init__(self, config: dict, pins: dict | None):
        self.config = config
        self.roots = Roots(config["roots"])
        self.out = Path(config["out_dir"]).resolve()
        self.pins = pins
        self.results: list[Result] = []
        self._sha: dict[str, str] = {}
        self.provenance: dict[str, dict] = {}
        self.python = sys.executable

    # -- bookkeeping
    def add(self, check, tier, status, **detail):
        self.results.append(Result(check, tier, status, detail))
        return status

    def digest(self, p: Path) -> str:
        key = str(p)
        if key not in self._sha:
            self._sha[key] = sha256(p)
        return self._sha[key]

    def local(self, recorded: str) -> Path | None:
        if recorded.startswith("/"):
            return self.roots.local(recorded)
        return REPO / recorded

    def prepare_out(self):
        check_out_dir(self.out, [REPO] + list(self.roots.local_roots.values()))
        self.out.mkdir(parents=True, exist_ok=True)
        (self.out / "logs").mkdir()

    # -- producers
    def launch(self, name: str, producer: str, argv: list[str], cwd: Path, log: Path) -> int:
        """Run a checkout producer through _launch.py (import provenance), stdout+stderr merged into ``log``
        the way a shell redirect does, with PYTHONPATH cleared so only the checkout's own layout resolves."""
        rec = self.out / "provenance" / f"{name}.json"
        rec.parent.mkdir(parents=True, exist_ok=True)
        cwd.mkdir(parents=True, exist_ok=True)
        env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP")}
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["MPLBACKEND"] = "Agg"
        cmd = [self.python, str(HERE / "_launch.py"), "--record", str(rec), "--", str(REPO / producer), *argv]
        with open(log, "w") as fh:
            rc = subprocess.run(cmd, cwd=cwd, env=env, stdout=fh, stderr=subprocess.STDOUT).returncode
        info = json.loads(rec.read_text()) if rec.exists() else {"modules": []}
        env_dirs = [Path(p).resolve() for p in (info.get("prefix"), info.get("base_prefix"), info.get("user_site")) if p]
        foreign, project = [], []
        for m in info["modules"]:
            mp = Path(m)
            if REPO in mp.parents:
                project.append(str(mp.relative_to(REPO)))
            elif not any(d in mp.parents for d in env_dirs):
                foreign.append(m)
        self.provenance[name] = {"argv": cmd, "cwd": str(cwd), "returncode": rc, "project_modules": project,
                                 "foreign_modules": foreign, "log": str(log)}
        if foreign:
            self.add(f"provenance:{name}", B, MISMATCH, foreign_modules=foreign,
                     why="the producer imported code from outside the checkout under test (OI-136)")
        return rc

    # ------------------------------------------------------------------------------------------- tier A
    def tier_a(self):
        self.a_receipt_pins()
        self.a_digests()
        self.a_producers()
        self.a_prediction_totals()
        self.a_pairdiff_summaries()
        self.a_v_receipt()
        self.a_unrecorded_pins()

    def a_receipt_pins(self):
        for rel, want in S.RECEIPTS.items():
            p = REPO / rel
            if not p.exists():
                self.add(f"receipt:{rel}", A, INPUT_MISSING, why="committed receipt absent from the checkout")
                continue
            got = self.digest(p)
            self.add(f"receipt:{rel}", A, REPRODUCED if got == want else MISMATCH, expected=want, observed=got,
                     why=None if got == want else f"the checkout's receipt is not the one scope.py was written against ({S.SOURCE_COMMIT[:8]})")

    def a_digests(self):
        seen = {}
        for rel in S.DIGEST_SOURCES:
            doc = json.loads((REPO / rel).read_text())
            for path, want, trail in declared_digests(doc):
                seen.setdefault((path, want), []).append(f"{rel}:{'.'.join(map(str, trail))}")
        for (path, want), where in sorted(seen.items()):
            lp = self.local(path)
            base = {"recorded": path, "expected": want, "declared_by": where[:4], "n_declarations": len(where)}
            if lp is None:
                self.add(f"digest:{path}", A, INPUT_MISSING, **base, why="recorded under no configured root")
            elif not lp.exists():
                m = _DEPLOY.match(path)
                blob = git_blob_sha256(m.group(1), m.group(2)) if m else None
                if blob == want:
                    self.add(f"digest:{path}", A, REPRODUCED, **base, mode=f"git blob {m.group(2)} at {m.group(1)}",
                             why="the scratch export copy was removed; the recorded bytes are that commit's blob")
                else:
                    self.add(f"digest:{path}", A, INPUT_MISSING, **base, local=str(lp), git_blob=blob)
            elif lp.is_dir():
                self.add(f"digest:{path}", A, INFO, **base, local=str(lp), why="a directory; its files are pinned by `pin`")
            else:
                got = self.digest(lp)
                if got == want:
                    self.add(f"digest:{path}", A, REPRODUCED, **base)
                else:
                    status = DECLARED if path in S.DECLARED_DIFFERENCES else MISMATCH
                    self.add(f"digest:{path}", A, status, **base, observed=got, local=str(lp),
                             why=S.DECLARED_DIFFERENCES.get(path))

    def a_producers(self):
        """The checkout's producers against the copies that produced the committed outputs."""
        seen = set()
        for rel in S.DIGEST_SOURCES:
            for path, want, _ in declared_digests(json.loads((REPO / rel).read_text())):
                name = Path(path).name
                if name in S.PRODUCER_FILES and ("/code/" in path or "/deploy/" in path) and (name, want) not in seen:
                    seen.add((name, want))
                    self._producer(name, want, f"copy {path}")
        for pattern, keys, name in S.PRODUCER_SHA_FIELDS:
            for f in sorted(glob.glob(str(REPO / pattern))):
                want = get_path(json.loads(Path(f).read_text()), keys)
                if (name, want) not in seen:
                    seen.add((name, want))
                    self._producer(name, want, f"{Path(f).relative_to(REPO)}:{'.'.join(keys)}")
        for rel in sorted({run["producer"] for run in S.FIGURE_RUNS.values()}):
            self._deploy_identity(f"producer:{rel}", A, rel)

    def _deploy_identity(self, check, tier, rel):
        """A checkout file against the figures' deploy commit (the scratch export itself was removed)."""
        want = git_blob_sha256(S.FIGURE_DEPLOY_COMMIT, rel)
        if want is None:
            self.add(check, tier, INFO, why=f"{rel} does not exist at {S.FIGURE_DEPLOY_COMMIT} (or the checkout has no history)")
            return
        got = self.digest(REPO / rel)
        self.add(check, tier, REPRODUCED if want == got else MISMATCH, expected=want, observed=got,
                 against=f"git blob at {S.FIGURE_DEPLOY_COMMIT}, the deploy the figures ran from")

    def _producer(self, name, want, source):
        """REPRODUCED if the checkout's producer is the code that ran; DECLARED_DIFFERENCE if that code is an older
        committed version (or declared in scope.py) -- tier B then shows whether today's code still reproduces
        its outputs; MISMATCH if the recorded code is nowhere."""
        rel = S.PRODUCER_FILES[name]
        got = self.digest(REPO / rel)
        if got == want:
            self.add(f"producer:{rel}", A, REPRODUCED, expected=want, against=source)
            return
        older = git_commit_with_blob(rel, want)
        declared = S.DECLARED_CODE.get((name, want))
        if older:
            self.add(f"producer:{rel}@{want[:8]}", A, DECLARED, expected=want, observed=got, against=source,
                     why=f"the recorded code is the committed blob at {older[:10]}; the checkout carries a later version")
        elif declared:
            self.add(f"producer:{rel}@{want[:8]}", A, DECLARED, expected=want, observed=got, against=source,
                     why=S.DECLARED_DIFFERENCES[declared])
        else:
            self.add(f"producer:{rel}@{want[:8]}", A, MISMATCH, expected=want, observed=got, against=source,
                     why="the recorded code is neither the checkout's producer nor any committed version of it")

    def a_prediction_totals(self):
        """Integrated sigma of each 5D prediction recomputed with gen5d_to_rootpreds' arithmetic, against the
        generator-context sidecars (same arithmetic: exact) and the flux-fix receipts (other code: tolerance)."""
        sys.path.insert(0, str(REPO / "3d-unfolding/genie"))
        import gen5d_to_rootpreds as g2r
        expected = {}
        for f in sorted(glob.glob(str(REPO / S.GC / "*_xsec*.json"))):
            side = json.loads(Path(f).read_text())
            expected.setdefault(side["input"]["path"], []).append(
                (f"{Path(f).name}:total_sigma_cm2_per_nucleon", side["total_sigma_cm2_per_nucleon"], 0.0))
        v1 = json.loads((REPO / S.S5P / "gen5d/gen5d-fluxfix.json").read_text())
        for k, p in v1["products"].items():
            expected.setdefault(p["npz"], []).append((f"gen5d-fluxfix.json:{k}.after_fix_5d_grid",
                                                      p["integrated_sigma_cm2"]["after_fix_5d_grid"], S.TOL_CROSS_CODE))
        v2 = json.loads((REPO / S.S5P / "gen5d/gen5d-fluxfix-2.json").read_text())
        for k, p in v2["products"].items():
            key = "after" if "after" in p["integrated_sigma_cm2"] else "full"
            expected.setdefault(p["npz"], []).append((f"gen5d-fluxfix-2.json:{k}.{key}",
                                                      p["integrated_sigma_cm2"][key], S.TOL_CROSS_CODE))
        for path, exps in sorted(expected.items()):
            lp = self.local(path)
            if lp is None or not lp.exists():
                self.add(f"sigma:{path}", A, INPUT_MISSING, local=str(lp))
                continue
            x, e = g2r.load(lp)
            total = float((x * np.einsum("a,b,c,d,f->abcdf", *[np.diff(k) for k in e])).sum())
            for label, want, tol in exps:
                st, diffs = compare(want, total, tol, label)
                self.add(f"sigma:{label}", A, st, expected=want, observed=total, tolerance=tol, product=path, diffs=diffs)

    def a_pairdiff_summaries(self):
        """F2/F4/M1 summary statistics recomputed from the stored D npz (s5p_pairdiff's formulas)."""
        for f in sorted(glob.glob(str(REPO / S.S5P / "stage3/[fm][124]/*.json"))):
            rec = json.loads(Path(f).read_text())
            lp = self.local(rec["out"]["path"])
            name = str(Path(f).relative_to(REPO))
            if lp is None or not lp.exists():
                self.add(f"pairdiff-summary:{name}", A, INPUT_MISSING, local=str(lp))
                continue
            z = npz_arrays(lp)
            D, se, fB = z["D_J"], z["se_J"], z["f_B_mean"]
            ok = fB > 0
            obs = {"n_pairs": int(z["d_pairs"].shape[0]), "cells": int(z["names"].size),
                   "median_abs_D_over_fB": float(np.median(np.abs(D[ok]) / fB[ok])),
                   "max_abs_D_over_fB": float(np.max(np.abs(D[ok]) / fB[ok])),
                   "median_abs_D_over_se": None if z["d_pairs"].shape[0] < 2 else
                   float(np.median(np.abs(D) / np.where(se > 0, se, np.inf)))}
            exp = {k: rec[k] for k in obs}
            st, diffs = compare(exp, obs, S.TOL_SAME_CODE)
            self.add(f"pairdiff-summary:{name}", A, st, expected=exp, observed=obs, diffs=diffs)

    def a_v_receipt(self):
        rec = json.loads((REPO / S.S5P / "stage3/V/V-receipt.json").read_text())
        lp = self.local(rec["path"])
        if lp is None or not lp.exists():
            self.add("V:receipt-fields", A, INPUT_MISSING, local=str(lp))
            return
        z = npz_arrays(lp)
        meta = json.loads(str(z["meta"]))
        obs = {"n": int(z["n"]), "shrinkage": float(z["shrinkage"]), "meta": meta}
        exp = {"n": rec["n"], "shrinkage": rec["shrinkage"], "meta": rec["meta"]}
        st, diffs = compare(exp, obs, S.TOL_SAME_CODE)
        self.add("V:receipt-fields", A, st, diffs=diffs)
        draft = self.digest(REPO / S.S5P / "prod-draft/design.json")
        frozen = json.loads((REPO / S.S5P / "prod/design.json").read_text())
        self.add("V:built-from-committed-draft-design", A, REPRODUCED if meta["design_sha256"] == draft else MISMATCH,
                 expected=meta["design_sha256"], observed=draft)
        self.add("V:frozen-design-pins-V", A, REPRODUCED if frozen.get("v_sha256") == rec["sha256"] else MISMATCH,
                 expected=rec["sha256"], observed=frozen.get("v_sha256"))

    def a_unrecorded_pins(self):
        if self.pins is None:
            self.add("unrecorded-inputs", A, NOT_RUN, why="no --pins file given (see `pin`)")
            return
        for group, entries in self.pins["groups"].items():
            for spec, want in entries.items():
                lp = self.roots.spec(spec)
                if not lp.exists():
                    self.add(f"pin:{spec}", A, INPUT_MISSING, group=group, local=str(lp))
                    continue
                got = self.digest(lp)
                self.add(f"pin:{spec}", A, REPRODUCED if got == want["sha256"] else MISMATCH, group=group,
                         expected=want["sha256"], observed=got, pinned_utc=self.pins["measured_utc"])
        for group, specs in S.UNRECORDED_INPUT_GLOBS.items():
            now_found = set(self._expand(specs))
            pinned = set(self.pins["groups"].get(group, {}))
            if now_found != pinned:
                self.add(f"pin-population:{group}", A, MISMATCH, only_now=sorted(now_found - pinned)[:20],
                         only_pinned=sorted(pinned - now_found)[:20])

    def _expand(self, specs):
        for spec in specs:
            name, rel = spec.split(":", 1)
            root = self.roots.local_roots[name]
            for p in sorted(glob.glob(str(root / rel))):
                if ".partial" not in Path(p).name:
                    yield f"{name}:{Path(p).relative_to(root)}"

    # ------------------------------------------------------------------------------------------- tier B
    def tier_b(self):
        try:
            import ROOT  # noqa: F401
            self.have_root = True
        except Exception as exc:  # the analysis env (root_6_28) is required for ROOT producers only
            self.have_root = False
            self.root_error = repr(exc)
        self.b_rootpreds()
        self.b_figures()
        self.b_pairdiff()
        self.b_prefreeze()
        self.b_build_v()
        self.b_envelope()
        self.b_module_identity()

    def _need_root(self, check) -> bool:
        if not self.have_root:
            self.add(check, B, ENV_MISSING, why=f"PyROOT not importable in {self.python}: {self.root_error}")
        return self.have_root

    def b_rootpreds(self):
        self.pred_dir = self.out / "preds"
        self.pred_dir.mkdir(parents=True, exist_ok=True)
        for f in sorted(glob.glob(str(REPO / S.GC / "*_xsec*.json"))):
            side = json.loads(Path(f).read_text())
            name = Path(side["out"]).name
            check = f"rootpred:{name}"
            if not self._need_root(check):
                continue
            src = self.local(side["input"]["path"])
            if src is None or not src.exists():
                self.add(check, B, INPUT_MISSING, local=str(src))
                continue
            out = self.pred_dir / name
            rc = self.launch(f"rootpred-{name}", "3d-unfolding/genie/gen5d_to_rootpreds.py",
                             ["--npz", str(src), "--kind", side["kind"], "--label", side["label"], "--out", str(out)],
                             self.pred_dir, self.out / "logs" / f"rootpred-{name}.log")
            if rc != 0 or not out.exists():
                self.add(check, B, MISMATCH, returncode=rc, why="producer failed")
                continue
            mine = json.loads(out.with_suffix(".json").read_text())
            exp = {"total": side["total_sigma_cm2_per_nucleon"], "input_sha256": side["input"]["sha256"], "code_sha256": side["code_sha256"]}
            obs = {"total": mine["total_sigma_cm2_per_nucleon"], "input_sha256": mine["input"]["sha256"], "code_sha256": mine["code_sha256"]}
            st1, d1 = compare(exp, obs, 0.0)
            stored = self.local(side["out"])
            if stored is None or not stored.exists():
                self.add(check, B, INPUT_MISSING, sidecar=st1, why="the campaign's stored ROOT file is absent", local=str(stored))
                continue
            st2, d2 = compare_arrays(root_dump(stored), root_dump(out), 0.0)
            st = MISMATCH if MISMATCH in (st1, st2) else (WITHIN_TOL if WITHIN_TOL in (st1, st2) else REPRODUCED)
            self.add(check, B, st, sidecar_diffs=d1, histogram_diffs=d2, stored=str(stored), regenerated=str(out),
                     stored_sha256=self.digest(stored), regenerated_sha256=sha256(out),
                     note="histogram contents, errors and edges compared bitwise; ROOT file bytes embed a creation time/UUID")

    def _argv(self, template: list[str], run_dir: Path) -> list[str]:
        def sub(tok):
            tok = tok.replace("{rp}", str(self.pred_dir)).replace("{out}", str(run_dir))
            tok = re.sub(r"\{a:([^}]*)\}", lambda m: str(self.roots.spec("analysis:" + m.group(1))), tok)
            return re.sub(r"\{s:([^}]*)\}", lambda m: str(self.roots.spec("s5p:" + m.group(1))), tok)
        return [sub(t) for t in template]

    def b_figures(self):
        genfig_recorded = S.RECORDED_ROOTS["s5p"] + "/" + S.GENFIG.split(":", 1)[1]
        for name, run in S.FIGURE_RUNS.items():
            check = f"figure:{name}"
            if not self._need_root(check):
                continue
            run_dir = self.out / "figures" / name
            argv = self._argv(run["argv"], run_dir)
            missing = [p for p in input_paths(argv) if run_dir not in Path(p).parents and not Path(p).exists()]
            if missing:
                self.add(check, B, INPUT_MISSING, missing=missing)
                continue
            log = run_dir / f"{name}.log"
            rc = self.launch(f"figure-{name}", run["producer"], argv, run_dir, log)
            want = normalize_log((REPO / run["log"]).read_text(), None, None)
            got = normalize_log(log.read_text(), str(run_dir), genfig_recorded)
            text_status = REPRODUCED if want == got else MISMATCH
            text_diff = None if want == got else first_line_diff(want, got)
            figs = {}
            for produced, committed in run["figures"].items():
                pf = run_dir / produced
                if not pf.exists():
                    figs[produced] = {"status": MISMATCH, "why": "not produced"}
                    continue
                figs[produced] = compare_pdf(REPO / committed, pf)
            fig_status = MISMATCH if any(v["status"] == MISMATCH for v in figs.values()) else (
                WITHIN_TOL if any(v["status"] == WITHIN_TOL for v in figs.values()) else REPRODUCED)
            st = MISMATCH if rc != 0 or MISMATCH in (text_status, fig_status) else (
                WITHIN_TOL if WITHIN_TOL in (text_status, fig_status) else REPRODUCED)
            self.add(check, B, st, returncode=rc, log_compare=text_status, log_first_diff=text_diff,
                     figures=figs, log=str(log), committed_log=run["log"], note=run.get("note"))

    def b_pairdiff(self):
        stage1 = REPO / S.S5P / "stage1/stage1_inspect.json"
        s5c = REPO / "docs/orchestration/state/s5c/contract.json"
        for f in sorted(glob.glob(str(REPO / S.S5P / "stage3/[fm][124]/*.json"))):
            rec = json.loads(Path(f).read_text())
            rel = Path(f).relative_to(REPO)
            check = f"pairdiff:{rel}"
            run_dir = self.out / "pairdiff" / rel.parent.name / rel.stem
            ins = [(self.local(p["a"]), self.local(p["b"])) for p in rec["inputs"]]
            miss = [str(x) for pair in ins for x in pair if x is None or not x.exists()]
            if miss:
                self.add(check, B, INPUT_MISSING, missing=miss[:10])
                continue
            for side, idx in (("a", 0), ("b", 1)):
                (run_dir / side).mkdir(parents=True, exist_ok=True)
                for pair in ins:
                    link = run_dir / side / pair[idx].name
                    if not link.exists():
                        link.symlink_to(pair[idx])
            out = run_dir / f"{rel.stem}.npz"
            rc = self.launch(f"pairdiff-{rel.parent.name}-{rel.stem}", "nd-unfolding/s5p_pairdiff.py",
                             ["--a", str(run_dir / "a" / "*.npz"), "--b", str(run_dir / "b" / "*.npz"),
                              "--stage1", str(stage1), "--s5c-contract", str(s5c), "--label", rec["label"], "--out", str(out)],
                             REPO, run_dir / "pairdiff.log")
            if rc != 0 or not out.exists():
                self.add(check, B, MISMATCH, returncode=rc, why="producer failed", log=str(run_dir / "pairdiff.log"))
                continue
            mine = json.loads(out.with_suffix(".json").read_text())
            keys = ("label", "n_pairs", "cells", "median_abs_D_over_fB", "max_abs_D_over_fB", "median_abs_D_over_se")
            st1, d1 = compare({k: rec[k] for k in keys}, {k: mine[k] for k in keys}, S.TOL_SAME_CODE)
            pairs_exp = [(p["a_sha256"], p["b_sha256"]) for p in rec["inputs"]]
            pairs_obs = [(p["a_sha256"], p["b_sha256"]) for p in mine["inputs"]]
            st3 = REPRODUCED if pairs_exp == pairs_obs else MISMATCH
            stored = self.local(rec["out"]["path"])
            st2, d2 = compare_arrays(npz_arrays(stored), npz_arrays(out), S.TOL_SAME_CODE) if stored and stored.exists() else (INPUT_MISSING, [])
            sts = (st1, st2, st3)
            st = MISMATCH if MISMATCH in sts else INPUT_MISSING if INPUT_MISSING in sts else WITHIN_TOL if WITHIN_TOL in sts else REPRODUCED
            self.add(check, B, st, summary_diffs=d1, array_diffs=d2, pairing=st3, regenerated=str(out),
                     code_recorded=rec["code_sha256"], code_now=mine["code_sha256"])

    def _design(self, rel: str) -> Path:
        """The committed design, re-rooted onto the configured roots (byte-identical when the roots are the
        recorded ones)."""
        src = REPO / rel
        if self.roots.identity():
            return src
        dst = self.out / "inputs" / rel.replace("/", "__")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(self.roots.rebase(json.loads(src.read_text())), indent=1) + "\n")
        return dst

    def b_prefreeze(self):
        design = self._design(f"{S.S5P}/prod-draft/design.json")
        vrec = json.loads((REPO / S.S5P / "stage3/V/V-receipt.json").read_text())
        V = self.local(vrec["path"])
        for cmd in ("units", "devpower"):
            check = f"prefreeze:{cmd}"
            rec = json.loads((REPO / S.S5P / f"stage3/prefreeze/{cmd}.json").read_text())
            run_dir = self.out / "prefreeze"
            run_dir.mkdir(parents=True, exist_ok=True)
            inputs = run_dir / f"{cmd}-inputs.json"
            inputs.write_text(json.dumps(self.roots.rebase(rec["inputs"])) + "\n")
            out = run_dir / f"{cmd}.json"
            rc = self.launch(f"prefreeze-{cmd}", "nd-unfolding/s5p_prefreeze.py",
                             [cmd, "--design", str(design), "--v", str(V), "--inputs", str(inputs), "--out", str(out)],
                             REPO, run_dir / f"{cmd}.log")
            if rc != 0 or not out.exists():
                self.add(check, B, MISMATCH if V and V.exists() else INPUT_MISSING, returncode=rc, log=str(run_dir / f"{cmd}.log"))
                continue
            mine = json.loads(out.read_text())
            keys = ("design_sha256", "v_sha256", "code_sha256", "result")
            exp = {k: rec[k] for k in keys}
            if design != REPO / f"{S.S5P}/prod-draft/design.json":
                exp["design_sha256"] = sha256(design)  # the re-rooted copy; its source is pinned in tier A
            st, diffs = compare(exp, {k: mine[k] for k in keys}, S.TOL_SAME_CODE)
            self.add(check, B, st, diffs=diffs, regenerated=str(out), design=str(design))

    def b_build_v(self):
        check = "V:build-v"
        design = self._design(f"{S.S5P}/prod-draft/design.json")
        vrec = json.loads((REPO / S.S5P / "stage3/V/V-receipt.json").read_text())
        stored = self.local(vrec["path"])
        run_dir = self.out / "V"
        run_dir.mkdir(parents=True, exist_ok=True)
        out = run_dir / "V-s3v.npz"
        rc = self.launch("build-v", "nd-unfolding/s5p_joint.py", ["build-v", "--design", str(design), "--out", str(out)],
                         REPO, run_dir / "build-v.log")
        if rc != 0 or not out.exists():
            self.add(check, B, MISMATCH, returncode=rc, log=str(run_dir / "build-v.log"))
            return
        e, o = npz_arrays(stored), npz_arrays(out)
        me, mo = json.loads(str(e.pop("meta"))), json.loads(str(o.pop("meta")))
        me = self.roots.rebase(me)
        if design != REPO / f"{S.S5P}/prod-draft/design.json":
            me["design_sha256"] = sha256(design)
        st1, d1 = compare_arrays(e, o, S.TOL_SAME_CODE)
        st2, d2 = compare(me, mo, S.TOL_SAME_CODE)
        st = MISMATCH if MISMATCH in (st1, st2) else WITHIN_TOL if WITHIN_TOL in (st1, st2) else REPRODUCED
        self.add(check, B, st, array_diffs=d1, meta_diffs=d2, stored_sha256=self.digest(stored), regenerated_sha256=sha256(out),
                 regenerated=str(out), note="arrays compared; np.savez archive bytes carry write times")

    def b_envelope(self):
        check = "envelope"
        rec = json.loads((REPO / S.S5P / "stage3/envelope-receipt.json").read_text())
        run_dir = self.out / "envelope"
        run_dir.mkdir(parents=True, exist_ok=True)
        out = run_dir / "envelope-receipt.json"
        rc = self.launch("envelope", "nd-unfolding/s5p_envelope.py",
                         ["--runs", str(self.roots.spec("s5p:runs")), "--s5e-runs", str(self.roots.spec("s5e:runs")),
                          "--stage1", str(REPO / S.S5P / "stage1/stage1_inspect.json"),
                          "--s5c-contract", str(REPO / "docs/orchestration/state/s5c/contract.json"), "--out", str(out)],
                         REPO, run_dir / "envelope.log")
        if rc != 0 or not out.exists():
            self.add(check, B, MISMATCH, returncode=rc, log=str(run_dir / "envelope.log"))
            return
        mine = json.loads(out.read_text())
        exp = self.roots.rebase(rec)
        for key in exp:
            if isinstance(exp[key], dict) and key in ("bias_sources", "linearity"):
                for sub in exp[key]:
                    st, diffs = compare(exp[key][sub], mine[key].get(sub), S.TOL_SAME_CODE)
                    source = S.ENVELOPE_DECLARED_FIELDS.get((key, sub))
                    if source is not None and st == MISMATCH:
                        st = DECLARED
                    self.add(f"{check}:{key}.{sub}", B, st, diffs=diffs,
                             why=S.DECLARED_DIFFERENCES[source] if source else None)
            else:
                st, diffs = compare(exp[key], mine.get(key), S.TOL_SAME_CODE)
                self.add(f"{check}:{key}", B, st, diffs=diffs)

    def b_module_identity(self):
        """Every checkout module a tier-B figure producer imported, against the deploy export it ran from."""
        mods = sorted({m for k, v in self.provenance.items() if k.startswith(("figure-", "rootpred-")) for m in v["project_modules"]})
        for rel in mods:
            if not rel.startswith("reproduction/"):
                self._deploy_identity(f"module:{rel}", B, rel)

    # ------------------------------------------------------------------------------------------- tiers C, D
    def tier_c(self):
        for key, entry in S.NOT_REGENERATED.items():
            self.add(f"not-regenerated:{key}", C, NOT_RUN, **entry)

    def tier_d(self):
        committed = REPO / S.JOINT["committed_result"]
        status_dir = self.roots.spec("s5p:runs/prod/status")
        finals = {n: (status_dir / f"{n}-final.json").exists() for n in S.JOINT["nulls"]}
        indep = self.config.get("joint", {}).get("independent_compare")
        facts = {"committed_result_present": committed.exists(), "final_status_present": finals,
                 "independent_compare": indep, "independent_compare_present": bool(indep) and Path(indep).exists(),
                 "terminal_condition": S.JOINT["terminal_condition"]}
        if not committed.exists() or not all(finals.values()):
            self.add("joint:final-result", D, PENDING, **facts,
                     why="the terminal joint products do not exist yet; nothing about the joint result is reproduced")
            return
        design = self._design(S.JOINT["design"])
        vrec = json.loads((REPO / S.JOINT["v_receipt"]).read_text())
        rec = json.loads(committed.read_text())
        pins = {"design_sha256": S.RECEIPTS[S.JOINT["design"]], "v_sha256": vrec["sha256"]}
        st0, d0 = compare(pins, {k: rec.get(k) for k in pins}, 0.0)
        run_dir = self.out / "joint"
        run_dir.mkdir(parents=True, exist_ok=True)
        out = run_dir / "joint-evaluate.json"
        rc = self.launch("joint-evaluate", "nd-unfolding/s5p_joint.py",
                         ["evaluate", "--design", str(design), "--v", str(self.local(vrec["path"])), "--out", str(out)],
                         REPO, run_dir / "evaluate.log")
        if rc != 0 or not out.exists():
            self.add("joint:replay", D, MISMATCH, returncode=rc, log=str(run_dir / "evaluate.log"), **facts)
            return
        st, diffs = compare(self.roots.rebase(rec), json.loads(out.read_text()), S.TOL_SAME_CODE)
        self.add("joint:pins", D, st0, diffs=d0)
        self.add("joint:replay", D, st, diffs=diffs, regenerated=str(out), **facts,
                 note="a replay of the production evaluator; it verifies the committed file, not the statistics")
        if not facts["independent_compare_present"]:
            self.add("joint:independent-verification", D, PENDING, **facts,
                     why="no independent recomputation report at the configured route")
        else:
            self.add("joint:independent-verification", D, INFO, report=indep, sha256=sha256(indep),
                     why="read and judge the independent lane's own report; this harness does not grade it")

    # ------------------------------------------------------------------------------------------- report
    def environment(self) -> dict:
        env = {"python": sys.version.split()[0], "executable": sys.executable, "numpy": np.__version__,
               "host": platform.node(), "utc": now()}
        try:
            import ROOT
            env["ROOT"] = ROOT.gROOT.GetVersion()
        except Exception:
            env["ROOT"] = None
        try:
            import matplotlib
            env["matplotlib"] = matplotlib.__version__
        except Exception:
            env["matplotlib"] = None
        git = lambda *a: subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout.strip()
        env["checkout"] = {"path": str(REPO), "head": git("rev-parse", "HEAD"),
                           "status_at_start": getattr(self, "status_at_start", None),
                           "status_at_end": git("status", "--porcelain").splitlines(),
                           "scope_source_commit": S.SOURCE_COMMIT}
        env["checkout"]["clean"] = not env["checkout"]["status_at_start"] and not env["checkout"]["status_at_end"]
        return env

    def record_start(self):
        self.status_at_start = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain"],
                                              capture_output=True, text=True).stdout.splitlines()

    def write_report(self, tiers) -> int:
        counts: dict = {}
        for r in self.results:
            counts.setdefault(r.tier, {}).setdefault(r.status, 0)
            counts[r.tier][r.status] += 1
        ab = [r for r in self.results if r.tier in (A, B)]
        d_fail = [r for r in self.results if r.tier == D and r.status in FAILING]
        code = 1 if any(r.status in FAILING for r in ab) or d_fail else 2 if any(r.status in MISSING for r in ab) else 0
        report = {"schema": "s5p-reproduction-report/1", "tiers_run": tiers, "exit_code": code,
                  "environment": self.environment(), "config": self.config, "counts": counts,
                  "provenance": self.provenance, "results": [asdict(r) for r in self.results]}
        (self.out / "report.json").write_text(json.dumps(report, indent=1, default=str) + "\n")
        (self.out / "report.md").write_text(render_md(report))
        print(json.dumps({"out": str(self.out), "exit_code": code, "counts": counts}, indent=1))
        return code


# ----------------------------------------------------------------------------------------------- helpers

def check_out_dir(out: Path, forbidden: list) -> None:
    """A run writes only to a new directory outside the checkout and every input root (so it can neither
    dirty the tree under test nor touch the preserved campaign products)."""
    out = Path(out).resolve()
    for f in forbidden:
        f = Path(f).resolve()
        if out == f or f in out.parents:
            raise SystemExit(f"out_dir {out} is inside {f}; choose a fresh directory outside the checkout and every input root")
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"out_dir {out} exists and is not empty; every run writes a fresh directory")


def input_paths(argv: list[str]) -> list[str]:
    """The file paths inside producer arguments: ``/path``, ``LABEL:/path`` and ``/path:histogram``."""
    out = []
    for tok in argv:
        i = tok.find("/")
        if i < 0 or (i > 0 and tok[i - 1] != ":"):
            continue
        p = tok[i:]
        head, sep, tail = p.rpartition(":")
        out.append(head if sep and "/" not in tail else p)
    return out


def root_dump(path) -> dict:
    """Every histogram in a ROOT file as named arrays: contents and errors incl. under/overflow, and edges."""
    import ROOT
    ROOT.gROOT.SetBatch(True)
    f = ROOT.TFile.Open(str(path))
    out = {}
    for key in f.GetListOfKeys():
        obj = key.ReadObj()
        if not obj.InheritsFrom("TH1"):
            continue
        n = obj.GetNcells()
        name = key.GetName()
        out[f"{name}.content"] = np.array([obj.GetBinContent(i) for i in range(n)])
        out[f"{name}.error"] = np.array([obj.GetBinError(i) for i in range(n)])
        for ax, a in (("x", obj.GetXaxis()), ("y", obj.GetYaxis()), ("z", obj.GetZaxis())):
            out[f"{name}.edges_{ax}"] = np.array([a.GetBinLowEdge(i) for i in range(1, a.GetNbins() + 2)])
        out[f"{name}.class"] = np.array(obj.ClassName())
    f.Close()
    return out


_ENV_LINE = re.compile(r"^(Info|Warning) in <")


def normalize_log(text: str, run_dir: str | None, recorded_dir: str | None) -> list[str]:
    """A producer's log reduced to what the producer printed: ROOT Info/Warning lines (environment-dependent:
    rootmap warnings exist only under the full analysis environment) and the capture's ``[stderr]`` separator
    dropped, trailing blank lines removed, and this run's directory written as the recorded one."""
    lines = []
    for ln in text.splitlines():
        if _ENV_LINE.match(ln) or ln.strip() == "[stderr]":
            continue
        if run_dir is not None:
            ln = ln.replace(run_dir, recorded_dir)
        lines.append(ln.rstrip())
    while lines and not lines[-1]:
        lines.pop()
    return lines


def first_line_diff(want: list[str], got: list[str]) -> dict:
    for i, (w, g) in enumerate(zip(want, got)):
        if w != g:
            return {"line": i + 1, "expected": w, "observed": g}
    return {"line": min(len(want), len(got)) + 1, "expected_lines": len(want), "observed_lines": len(got)}


_PDF_VOLATILE = re.compile(rb"/(CreationDate|ModDate) *\([^)]*\)|/ID *\[[^\]]*\]|<xmp:(Create|Modify|Metadata)Date>[^<]*<")


def compare_pdf(committed: Path, produced: Path) -> dict:
    """Bitwise, else bitwise after blanking the PDF's creation/modification dates and document ID (the only
    fields a deterministic producer changes between runs)."""
    a, b = committed.read_bytes(), produced.read_bytes()
    if a == b:
        return {"status": REPRODUCED, "mode": "bitwise"}
    na, nb = _PDF_VOLATILE.sub(b"", a), _PDF_VOLATILE.sub(b"", b)
    if na == nb:
        return {"status": REPRODUCED, "mode": "bitwise except creation date / document ID",
                "committed_sha256": hashlib.sha256(a).hexdigest(), "produced_sha256": hashlib.sha256(b).hexdigest()}
    return {"status": MISMATCH, "mode": "content differs", "committed_bytes": len(a), "produced_bytes": len(b),
            "committed_sha256": hashlib.sha256(a).hexdigest(), "produced_sha256": hashlib.sha256(b).hexdigest()}


def render_md(rep: dict) -> str:
    env = rep["environment"]
    lines = ["# s5p reproduction report", "",
             f"- checkout `{env['checkout']['path']}` at `{env['checkout']['head']}` (clean before and after: {env['checkout']['clean']}); "
             f"scope written against `{env['checkout']['scope_source_commit'][:12]}`",
             f"- {env['host']}, Python {env['python']}, numpy {env['numpy']}, ROOT {env['ROOT']}, matplotlib {env['matplotlib']}, {env['utc']}",
             f"- tiers run: {', '.join(rep['tiers_run'])}; exit code **{rep['exit_code']}**", "",
             "Tiers are separate claims: A replays preserved products, B regenerates derived products from the "
             "checkout, C is NOT run, D (the final joint result) is PENDING until its terminal products exist.", "",
             "| tier | status | count |", "|---|---|---|"]
    for tier, cs in sorted(rep["counts"].items()):
        for st, n in sorted(cs.items()):
            lines.append(f"| {tier} | {st} | {n} |")
    lines += ["", "## Every result that is not REPRODUCED", ""]
    for r in rep["results"]:
        if r["status"] != REPRODUCED:
            d = {k: v for k, v in r["detail"].items() if v not in (None, [], {})}
            lines.append(f"- **{r['status']}** `{r['check']}` ({r['tier']}): "
                         + json.dumps(d, default=str)[:600])
    lines += ["", "## Reproduced checks", ""]
    for r in rep["results"]:
        if r["status"] == REPRODUCED:
            lines.append(f"- `{r['check']}` ({r['tier']})")
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------------------------------------------- CLI

def cmd_list() -> int:
    print(f"scope written against {S.SOURCE_COMMIT} (frozen admission {S.FROZEN_ADMISSION_COMMIT})\n")
    print(f"tier A replay: {len(S.RECEIPTS)} committed receipts/logs/figures pinned; every recorded digest in "
          f"{len(S.DIGEST_SOURCES)} JSON receipts; producer identity; prediction totals; F2/F4/M1 summaries; V fields; "
          f"unrecorded-input pins ({sum(len(v) for v in S.UNRECORDED_INPUT_GLOBS.values())} globs)")
    print("tier B regenerate: 8 prediction ROOT files; figure runs " + ", ".join(S.FIGURE_RUNS)
          + "; 17 F2/F4/M1 pair differences; prefreeze units and devpower; V (build-v); the study-P envelope")
    print("tier C NOT run:")
    for k, v in S.NOT_REGENERATED.items():
        print(f"  {k}: {v['what']} -- {v['why_not_run']}")
    print(f"tier D joint: PENDING until {S.JOINT['terminal_condition']}")
    print("\ndeclared differences:")
    for k, v in S.DECLARED_DIFFERENCES.items():
        print(f"  {k}: {v}")
    return 0


def cmd_pin(config: dict, out: Path) -> int:
    if out.exists():
        raise SystemExit(f"refusing to overwrite {out}")
    roots = Roots(config["roots"])
    h = Harness(config, None)
    groups = {}
    for group, specs in S.UNRECORDED_INPUT_GLOBS.items():
        groups[group] = {}
        for spec in h._expand(specs):
            p = roots.spec(spec)
            groups[group][spec] = {"sha256": sha256(p), "bytes": p.stat().st_size}
    doc = {"schema": "s5p-reproduction-pins/1", "measured_utc": now(), "host": platform.node(),
           "measured_by": "reproduction/s5p/repro_s5p.py pin (lane-measured; no producer recorded these digests)",
           "roots": {k: str(v) for k, v in roots.local_roots.items()}, "groups": groups}
    out.write_text(json.dumps(doc, indent=1) + "\n")
    print(json.dumps({g: len(v) for g, v in groups.items()}))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    p = sub.add_parser("pin")
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    r = sub.add_parser("run")
    r.add_argument("--config", type=Path, required=True)
    r.add_argument("--tiers", default="A,B,C,D")
    r.add_argument("--pins", type=Path, default=None)
    a = ap.parse_args(argv)
    if a.cmd == "list":
        return cmd_list()
    config = json.loads(a.config.read_text())
    if a.cmd == "pin":
        return cmd_pin(config, a.out)
    tiers = [t.strip().upper() for t in a.tiers.split(",") if t.strip()]
    if set(tiers) - set("ABCD"):
        raise SystemExit(f"unknown tiers {tiers}")
    h = Harness(config, json.loads(a.pins.read_text()) if a.pins else None)
    h.record_start()
    h.prepare_out()
    shutil.copy(a.config, h.out / "config.json")
    for t, fn in (("A", h.tier_a), ("B", h.tier_b), ("C", h.tier_c), ("D", h.tier_d)):
        if t in tiers:
            fn()
    return h.write_report([{"A": A, "B": B, "C": C, "D": D}[t] for t in tiers])


if __name__ == "__main__":
    raise SystemExit(main())
