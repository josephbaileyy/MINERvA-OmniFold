#!/usr/bin/env python3
"""Fresh-checkout reproduction harness for the already-final s5p components.

Scope (declared in ``scope.py``): the flux-repaired generator predictions and their input identities, the
deliverable generator figures and numbers built from them (VL156-VL160), and the pre-freeze quantities of the
joint-test design (F2, F4, M1, V, the null-T units, the development power, the study-P envelope); and (tier D) the
final joint result's committed outputs, replayed from the preserved calibration and power products.

Tiers, never merged in the report:

* **A, replay**: every digest the committed receipts record, re-measured on the preserved bytes; the committed
  producers compared with the copies that ran; committed numbers recomputed from the stored products; the
  harness's own lane pins of inputs no receipt digests (a separate basis, never historical provenance).
* **B, derived regeneration**: the committed producers re-run from THIS checkout into a fresh output directory on
  the preserved inputs, and their outputs compared with the committed receipts, logs and figures.
* **C, full scientific regeneration**: declared with its dependency and reported NOT_RUN (event generation,
  flux reweighting from events, production unfolding).
* **D, final joint result**: the frozen evaluator (``s5p_joint.py evaluate``) and the label step replayed from THIS
  checkout on the lane-pinned calibration/power products and compared with the committed outputs; the identities the
  joint receipts record; the independent recomputation's report recorded by digest (never graded).

Every row carries a ``basis`` saying what its agreement rests on: a digest the producing campaign recorded
(historical provenance), a digest this harness newly recorded (``pin``), a recomputation or a regeneration against
a committed receipt, or code identity. The seven declared differences (``scope.py``) are declared by BOTH their
recorded and observed digests and are listed individually, apart from the exact matches.

Usage::

    python3 reproduction/s5p/repro_s5p.py list
    python3 reproduction/s5p/repro_s5p.py pin --config CONFIG --out PINS.json [--extend OLD_PINS.json]
    python3 reproduction/s5p/repro_s5p.py stage --config CONFIG --pins PINS.json --to DIR
    python3 reproduction/s5p/repro_s5p.py run --config CONFIG [--tiers A,B,C,D] [--pins PINS.json]
    python3 reproduction/s5p/repro_s5p.py scan-trace --trace STRACE.txt --expect-prefix DIR

Every input location comes from the config (``config.example.json``); recorded absolute paths are identities that
are re-rooted, never read. The output directory must be new and outside the checkout, every configured root and
every recorded root. Exit status of ``run``: 0 only if tiers A, B and D all ran, every A/B row reproduced (exactly,
within tolerance, or as a declared difference), the joint replay reproduced, and every other D row passed or is one
of D's two declared non-grades (the independent report recorded as INFO, the not-yet-existing joint figures
PENDING); 1 on any MISMATCH or harness ERROR (in any tier); 2 otherwise (an input, the environment, a pins file or a
tier was missing: nothing is reported reproduced that was not measured).

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
import traceback
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
DECLARED = "DECLARED_DIFFERENCE"          # a known difference, declared by recorded AND observed digest, still measured
MISMATCH = "MISMATCH"
ERROR = "ERROR"                           # the harness itself failed on this check
INPUT_MISSING = "INPUT_MISSING"
ENV_MISSING = "ENV_MISSING"
NOT_RUN = "NOT_RUN"
PENDING = "PENDING"
INFO = "INFO"
PASSING = {REPRODUCED, WITHIN_TOL, DECLARED}
FAILING = {MISMATCH, ERROR}
# Tier-D rows that are declared non-grades, never reproductions: the independent report is recorded (INFO), and the
# joint figures do not exist yet (PENDING). Any other non-passing D row keeps the exit code from 0.
D_NON_GRADES = {"joint:independent-verification": INFO, "joint:figures": PENDING}
HEX64 = re.compile(r"^[0-9a-f]{64}$")

# What a row's agreement rests on. Receipt-recorded digests are the producing campaign's historical provenance;
# lane pins were recorded by this harness and prove only constancy since they were measured.
BASIS_RECEIPT_PIN = "committed file vs scope.py pin"
BASIS_RECORDED = "receipt-recorded digest (historical provenance)"
BASIS_RECORDED_GIT = "receipt-recorded digest, bytes read from git history (scratch copy removed)"
BASIS_LANE = "lane-pinned digest (newly recorded by this harness; NOT historical provenance)"
BASIS_CODE = "code identity vs recorded code"
BASIS_RECOMPUTED = "recomputed from preserved products vs committed receipt"
BASIS_COVERAGE = "coverage of the receipts' recorded digests"
BASIS_REGENERATED = "regenerated by this checkout's producer vs committed receipt/log/figure"
BASIS_PROVENANCE = "import provenance of a producer run"
BASIS_DECLARED_ONLY = "declared, not run"
BASIS_JOINT = "final joint result slot"


@dataclass
class Result:
    check: str
    tier: str
    status: str
    basis: str
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


def under(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(prefix.rstrip("/") + "/")


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
            if under(recorded, prefix):
                return self.local_roots[name] / recorded[len(prefix):].lstrip("/")
        return None

    def split(self, recorded: str) -> tuple[str, str] | None:
        """``(root name, relative path)`` of a recorded absolute path."""
        for name, prefix in self._order:
            if under(recorded, prefix):
                return name, recorded[len(prefix):].lstrip("/")
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


def compare(expected, observed, tol: float, path: str = "") -> tuple[str, list]:
    """Recursive comparison: REPRODUCED if every leaf is equal, WITHIN_TOL if some float differs by at most
    ``tol`` (relative), else MISMATCH with the first differences."""
    diffs = []
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
        if not (math.isfinite(e) and math.isfinite(o)):
            diffs.append({"at": p, "expected": e, "observed": o})
            worst[0] = MISMATCH
            return
        rel = abs(e - o) / max(abs(e), abs(o))
        if rel <= tol:
            if worst[0] == REPRODUCED:
                worst[0] = WITHIN_TOL
            diffs.append({"at": p, "expected": e, "observed": o, "rel": rel, "within_tol": True})
        else:
            diffs.append({"at": p, "expected": e, "observed": o, "rel": rel})
            worst[0] = MISMATCH

    def walk(e, o, p):
        if isinstance(e, dict) and isinstance(o, dict):
            if set(e) != set(o):
                diffs.append({"at": p, "keys_only_expected": sorted(set(e) - set(o), key=str),
                              "keys_only_observed": sorted(set(o) - set(e), key=str)})
                worst[0] = MISMATCH
            for k in sorted(set(e) & set(o), key=str):
                walk(e[k], o[k], f"{p}.{k}")
        elif isinstance(e, (list, tuple)) and isinstance(o, (list, tuple)):
            if len(e) != len(o):
                diffs.append({"at": p, "expected_len": len(e), "observed_len": len(o)})
                worst[0] = MISMATCH
            for i, (x, y) in enumerate(zip(e, o)):
                walk(x, y, f"{p}[{i}]")
        elif isinstance(e, (dict, list, tuple)) or isinstance(o, (dict, list, tuple)):
            diffs.append({"at": p, "expected_type": type(e).__name__, "observed_type": type(o).__name__})
            worst[0] = MISMATCH
        else:
            leaf(e, o, p)

    walk(expected, observed, path)
    hard = [d for d in diffs if not d.get("within_tol")]
    return worst[0], (hard or diffs)[:20]


def compare_arrays(expected: dict, observed: dict, tol: float) -> tuple[str, list]:
    """Named arrays: bitwise first, then relative tolerance on FINITE floats. Non-finite values (NaN, +-inf) must
    sit in the same places with the same values; an empty comparison is a MISMATCH, never a pass."""
    if not expected and not observed:
        return MISMATCH, [{"why": "nothing to compare"}]
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
            fe, fo = np.isfinite(e), np.isfinite(o)
            same_nonfinite = np.array_equal(fe, fo) and np.array_equal(e[~fe], o[~fo], equal_nan=True)
            if not same_nonfinite:
                diffs.append({"array": k, "nonfinite_differs": True})
                status = MISMATCH
                continue
            a, b = e[fe], o[fo]
            scale = np.maximum(np.abs(a), np.abs(b))
            rel = np.where(scale > 0, np.abs(a - b) / np.where(scale > 0, scale, 1.0), 0.0)
            m = float(rel.max()) if rel.size else 0.0
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


def worst_of(*statuses: str) -> str:
    for s in (ERROR, MISMATCH, INPUT_MISSING, ENV_MISSING, DECLARED, WITHIN_TOL):
        if s in statuses:
            return s
    return REPRODUCED


def npz_arrays(path) -> dict:
    with np.load(path, allow_pickle=False) as z:
        return {k: np.asarray(z[k]) for k in z.files}


def declared_digests(obj, trail: tuple = ()):
    """Every (recorded path, sha256, json trail) a receipt declares, in the shapes the s5p receipts use:
    {path, sha256}; {copy_of, sha256}; {K: path, K_sha256: digest}; {"/abs/path": digest}; {"docs/...": {sha256}};
    and a code tree {code_root_on_cluster: root, files: {relative path: digest}}."""
    if isinstance(obj, dict):
        if isinstance(obj.get("path"), str) and is_hex64(obj.get("sha256")):
            yield obj["path"], obj["sha256"], trail
        if isinstance(obj.get("copy_of"), str) and is_hex64(obj.get("sha256")):
            yield obj["copy_of"], obj["sha256"], trail
        root = obj.get("code_root_on_cluster")
        if isinstance(root, str) and isinstance(obj.get("files"), dict):
            for rel, v in obj["files"].items():
                if is_hex64(v):
                    yield f"{root.rstrip('/')}/{rel}", v, trail + ("files", rel)
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


def all_hex(obj, trail: tuple = ()):
    """Every 64-hex string value in a JSON document, with its trail."""
    if isinstance(obj, dict):
        items = obj.items()
    elif isinstance(obj, list):
        items = enumerate(obj)
    else:
        return
    for k, v in items:
        if is_hex64(v):
            yield trail + (k,), v
        yield from all_hex(v, trail + (k,))


def get_path(obj, keys):
    for k in keys:
        obj = obj[k]
    return obj


def git(*args, text=True):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=text)


def git_has_commit(commit: str) -> bool:
    return git("cat-file", "-e", f"{commit}^{{commit}}").returncode == 0


def git_blob_sha256(commit: str, rel: str) -> str | None:
    """sha256 of ``rel`` as committed at ``commit`` in the checkout's history (None if absent there)."""
    r = git("show", f"{commit}:{rel}", text=False)
    return hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 else None


def git_commit_with_blob(rel: str, want: str) -> str | None:
    """The newest commit whose ``rel`` hashes to ``want`` (reported as context; never a declaration)."""
    for c in git("log", "--format=%H", "--", rel).stdout.split():
        if git_blob_sha256(c, rel) == want:
            return c
    return None


def export_of(recorded: str) -> tuple[str, str] | None:
    """(commit, relative path) of a recorded copy inside a scratch code export (scope.CODE_EXPORTS)."""
    for prefix, commit in S.CODE_EXPORTS.items():
        if recorded.startswith(prefix):
            return commit, recorded[len(prefix):]
    return None


# ----------------------------------------------------------------------------------------------- the run

class Harness:
    def __init__(self, config: dict, pins: dict | None, pins_path: Path | None = None):
        self.config = config
        self.roots = Roots(config["roots"])
        self.out = Path(config["out_dir"]).resolve()
        self.pins = pins
        self.pins_path = pins_path
        self.results: list[Result] = []
        self._sha: dict[str, str] = {}
        self.provenance: dict[str, dict] = {}
        self.python = sys.executable
        self.compared = {"producer": set(), "design": set(), "V": set(), "stage1": set()}  # for the coverage row

    # -- bookkeeping
    def add(self, check, tier, status, basis, **detail):
        self.results.append(Result(check, tier, status, basis, detail))
        return status

    def guarded(self, fn, check, tier, basis):
        """Run one check; a harness exception becomes an ERROR row instead of aborting the report."""
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 -- recorded in the report, never swallowed
            self.add(check, tier, ERROR, basis, error=repr(exc), traceback=traceback.format_exc()[-3000:])

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
        check_out_dir(self.out, [REPO] + list(self.roots.local_roots.values()), recorded_roots())
        self.out.mkdir(parents=True, exist_ok=True)
        (self.out / "logs").mkdir()

    # -- producers
    def launch(self, name: str, producer: str, argv: list[str], cwd: Path, log: Path, extra_env: dict | None = None) -> int:
        """Run a checkout producer through _launch.py (import provenance), stdout+stderr merged into ``log``
        the way a shell redirect does, with PYTHONPATH cleared so only the checkout's own layout resolves."""
        rec = self.out / "provenance" / f"{name}.json"
        rec.parent.mkdir(parents=True, exist_ok=True)
        cwd.mkdir(parents=True, exist_ok=True)
        env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP")}
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["MPLBACKEND"] = "Agg"
        env.update(extra_env or {})
        cmd = [self.python, str(HERE / "_launch.py"), "--record", str(rec), "--", str(REPO / producer), *argv]
        with open(log, "w") as fh:
            rc = subprocess.run(cmd, cwd=cwd, env=env, stdout=fh, stderr=subprocess.STDOUT).returncode
        if not rec.exists():
            self.provenance[name] = {"argv": cmd, "cwd": str(cwd), "returncode": rc, "record": None, "log": str(log)}
            self.add(f"provenance:{name}", B, MISMATCH, BASIS_PROVENANCE, returncode=rc,
                     why="the producer exited without the launcher's import record (os._exit or a signal): its "
                         "imports were not inspected")
            return rc
        info = json.loads(rec.read_text())
        env_dirs = [Path(p).resolve() for p in (info.get("prefix"), info.get("base_prefix"), info.get("user_site")) if p]
        foreign, project = [], []
        for m in info["modules"]:
            mp = Path(m)
            if REPO in mp.parents:
                project.append(str(mp.relative_to(REPO)))
            elif not any(d in mp.parents for d in env_dirs):
                foreign.append(m)
        self.provenance[name] = {"argv": cmd, "cwd": str(cwd), "returncode": rc, "project_modules": project,
                                 "foreign_modules": foreign, "n_modules": len(info["modules"]), "log": str(log),
                                 "extra_env": extra_env or {}}
        if foreign:
            self.add(f"provenance:{name}", B, MISMATCH, BASIS_PROVENANCE, foreign_modules=foreign,
                     why="the producer imported code from outside the checkout under test (OI-136)")
        return rc

    # ------------------------------------------------------------------------------------------- tier A
    def tier_a(self):
        for fn, check, basis in ((self.a_receipt_pins, "receipts", BASIS_RECEIPT_PIN),
                                 (self.a_digests, "digests", BASIS_RECORDED),
                                 (self.a_producers, "producers", BASIS_CODE),
                                 (self.a_prediction_totals, "sigma", BASIS_RECOMPUTED),
                                 (self.a_pairdiff_summaries, "pairdiff-summary", BASIS_RECOMPUTED),
                                 (self.a_v_receipt, "V", BASIS_RECOMPUTED),
                                 (self.a_unrecorded_pins, "pins", BASIS_LANE)):
            self.guarded(fn, check, A, basis)

    def a_receipt_pins(self):
        for rel, want in S.RECEIPTS.items():
            p = REPO / rel
            if not p.exists():
                self.add(f"receipt:{rel}", A, INPUT_MISSING, BASIS_RECEIPT_PIN, why="committed receipt absent from the checkout")
                continue
            got = self.digest(p)
            self.add(f"receipt:{rel}", A, REPRODUCED if got == want else MISMATCH, BASIS_RECEIPT_PIN, expected=want, observed=got,
                     why=None if got == want else f"the checkout's receipt is not the one scope.py was written against ({S.SOURCE_COMMIT[:8]})")

    def a_digests(self):
        seen = {}
        for rel in S.DIGEST_SOURCES:
            doc = json.loads((REPO / rel).read_text())
            for path, want, trail in declared_digests(doc):
                seen.setdefault((path, want), []).append(f"{rel}:{'.'.join(map(str, trail))}")
        self.recorded_digests = {want for _, want in seen}
        for (path, want), where in sorted(seen.items()):
            lp = self.local(path)
            base = {"recorded": path, "expected": want, "declared_by": where[:4], "n_declarations": len(where)}
            check = f"digest:{path}"
            if lp is None:
                self.add(check, A, INPUT_MISSING, BASIS_RECORDED, **base, why="recorded under no configured root")
            elif not lp.exists():
                ex = export_of(path)
                if ex is None:
                    self.add(check, A, INPUT_MISSING, BASIS_RECORDED, **base, local=str(lp))
                elif not git_has_commit(ex[0]):
                    self.add(check, A, INPUT_MISSING, BASIS_RECORDED_GIT, **base, local=str(lp),
                             why=f"scratch copy removed and the checkout lacks commit {ex[0]} (a shallow clone?)")
                else:
                    blob = git_blob_sha256(*ex)
                    self.add(check, A, REPRODUCED if blob == want else MISMATCH, BASIS_RECORDED_GIT, **base,
                             observed=blob, mode=f"git blob {ex[1]} at {ex[0]}")
            elif lp.is_dir():
                self.add(check, A, MISMATCH, BASIS_RECORDED, **base, local=str(lp), why="a directory where a file digest is recorded")
            else:
                got = self.digest(lp)
                if got == want:
                    self.add(check, A, REPRODUCED, BASIS_RECORDED, **base)
                    continue
                decl = S.DECLARED_DIFFERENCES.get(path)
                if decl and decl[0] == want and decl[1] == got:
                    self.add(check, A, DECLARED, BASIS_RECORDED, **base, observed=got, why=decl[2])
                else:
                    self.add(check, A, MISMATCH, BASIS_RECORDED, **base, observed=got, local=str(lp),
                             declared=None if not decl else {"recorded": decl[0], "observed": decl[1]},
                             why="differs from the recorded digest" + (" and from its declaration" if decl else ""))

    def a_producers(self):
        """The checkout's producers against the code that produced the committed outputs."""
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
                self.compared["producer"].add(want)
                if (name, want) not in seen:
                    seen.add((name, want))
                    self._producer(name, want, f"{Path(f).relative_to(REPO)}:{'.'.join(keys)}")
        for rel in sorted({run["producer"] for run in S.FIGURE_RUNS.values()}):
            self._deploy_identity(f"producer:{rel}", A, rel)

    def _deploy_identity(self, check, tier, rel, commit=S.FIGURE_DEPLOY_COMMIT, what="the deploy the figures ran from"):
        """A checkout file against the git blob of the deploy commit a recorded run used (its scratch export may be
        gone; the commit is the identity)."""
        if not git_has_commit(commit):
            self.add(check, tier, INPUT_MISSING, BASIS_CODE, why=f"the checkout lacks commit {commit} (a shallow clone?)")
            return
        want = git_blob_sha256(commit, rel)
        got = self.digest(REPO / rel)
        if want is None:
            self.add(check, tier, MISMATCH, BASIS_CODE, observed=got, why=f"{rel} did not exist at {commit}, {what}")
            return
        self.add(check, tier, REPRODUCED if want == got else MISMATCH, BASIS_CODE, expected=want, observed=got,
                 against=f"git blob at {commit[:8]}, {what}")

    def _producer(self, name, want, source):
        """REPRODUCED if the checkout's producer is the code that ran; DECLARED_DIFFERENCE only if scope.py declares
        this (recorded, checkout) digest pair; MISMATCH otherwise. An older committed blob with the recorded digest is
        reported as context and never turns a difference into a declared one."""
        rel = S.PRODUCER_FILES[name]
        got = self.digest(REPO / rel)
        self.compared["producer"].add(want)
        if got == want:
            self.add(f"producer:{rel}@{want[:8]}", A, REPRODUCED, BASIS_CODE, expected=want, against=source)
            return
        older = git_commit_with_blob(rel, want)
        decl = S.DECLARED_CODE.get((name, want))
        detail = {"expected": want, "observed": got, "against": source, "recorded_code_is_blob_at": older}
        if decl and decl[0] == got:
            self.add(f"producer:{rel}@{want[:8]}", A, DECLARED, BASIS_CODE, **detail, why=decl[1])
        else:
            self.add(f"producer:{rel}@{want[:8]}", A, MISMATCH, BASIS_CODE, **detail,
                     why="the checkout's producer is not the recorded code, and scope.py declares no such difference")

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
                self.add(f"sigma:{path}", A, INPUT_MISSING, BASIS_RECOMPUTED, local=str(lp))
                continue
            x, e = g2r.load(lp)
            total = float((x * np.einsum("a,b,c,d,f->abcdf", *[np.diff(k) for k in e])).sum())
            for label, want, tol in exps:
                st, diffs = compare(want, total, tol, label)
                self.add(f"sigma:{label}", A, st, BASIS_RECOMPUTED, expected=want, observed=total, tolerance=tol,
                         product=path, diffs=diffs)

    def a_pairdiff_summaries(self):
        """F2/F4/M1 summary statistics recomputed from the stored D npz (s5p_pairdiff's formulas)."""
        for f in sorted(glob.glob(str(REPO / S.S5P / "stage3/[fm][124]/*.json"))):
            rec = json.loads(Path(f).read_text())
            lp = self.local(rec["out"]["path"])
            name = str(Path(f).relative_to(REPO))
            if lp is None or not lp.exists():
                self.add(f"pairdiff-summary:{name}", A, INPUT_MISSING, BASIS_RECOMPUTED, local=str(lp))
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
            self.add(f"pairdiff-summary:{name}", A, st, BASIS_RECOMPUTED, expected=exp, observed=obs, diffs=diffs)

    def a_v_receipt(self):
        rec = json.loads((REPO / S.S5P / "stage3/V/V-receipt.json").read_text())
        lp = self.local(rec["path"])
        if lp is None or not lp.exists():
            self.add("V:receipt-fields", A, INPUT_MISSING, BASIS_RECOMPUTED, local=str(lp))
            return
        z = npz_arrays(lp)
        meta = json.loads(str(z["meta"]))
        obs = {"n": int(z["n"]), "shrinkage": float(z["shrinkage"]), "meta": meta}
        exp = {"n": rec["n"], "shrinkage": rec["shrinkage"], "meta": rec["meta"]}
        st, diffs = compare(exp, obs, S.TOL_SAME_CODE)
        self.add("V:receipt-fields", A, st, BASIS_RECOMPUTED, diffs=diffs)
        draft = self.digest(REPO / S.S5P / "prod-draft/design.json")
        frozen = json.loads((REPO / S.S5P / "prod/design.json").read_text())
        self.compared["design"].add(meta["design_sha256"])
        self.compared["V"].add(frozen.get("v_sha256"))
        self.add("V:built-from-committed-draft-design", A, REPRODUCED if meta["design_sha256"] == draft else MISMATCH,
                 BASIS_RECOMPUTED, expected=meta["design_sha256"], observed=draft)
        self.add("V:frozen-design-pins-V", A, REPRODUCED if frozen.get("v_sha256") == rec["sha256"] else MISMATCH,
                 BASIS_RECOMPUTED, expected=rec["sha256"], observed=frozen.get("v_sha256"))

    def a_unrecorded_pins(self):
        if self.pins is None:
            self.add("pins:unrecorded-inputs", A, NOT_RUN, BASIS_LANE,
                     why=f"no --pins file given (see `pin`; the committed one is {S.PINS_FILE}): the unrecorded inputs are unchecked")
            return
        for group, entries in self.pins["groups"].items():
            utc = pin_measured_utc(self.pins, group)
            for spec, want in entries.items():
                lp = self.roots.spec(spec)
                if not lp.exists():
                    self.add(f"pin:{spec}", A, INPUT_MISSING, BASIS_LANE, group=group, local=str(lp))
                    continue
                got = self.digest(lp)
                self.add(f"pin:{spec}", A, REPRODUCED if got == want["sha256"] else MISMATCH, BASIS_LANE, group=group,
                         expected=want["sha256"], observed=got, pinned_utc=utc)
        for group, specs in S.UNRECORDED_INPUT_GLOBS.items():
            now_found = set(self._expand(specs))
            pinned = set(self.pins["groups"].get(group, {}))
            self.add(f"pin-population:{group}", A, REPRODUCED if now_found == pinned and pinned else MISMATCH, BASIS_LANE,
                     n_found=len(now_found), n_pinned=len(pinned), only_now=sorted(now_found - pinned)[:20],
                     only_pinned=sorted(pinned - now_found)[:20])

    def _expand(self, specs):
        for spec in specs:
            name, rel = spec.split(":", 1)
            root = self.roots.local_roots[name]
            for p in sorted(glob.glob(str(root / rel))):
                if ".partial" not in Path(p).name:
                    yield f"{name}:{Path(p).relative_to(root)}"

    def coverage(self, tier_b_ran: bool, tier_d_ran: bool = True):
        """Every 64-hex value in the digest sources was compared: file digests by a digest row, the classified
        non-file digests by the check scope.NON_FILE_DIGEST_KEYS names (run after tiers A, B and D)."""
        unclassified, uncompared = [], []
        for rel in S.DIGEST_SOURCES:
            for trail, v in all_hex(json.loads((REPO / rel).read_text())):
                if v in getattr(self, "recorded_digests", set()):
                    continue
                kinds = [S.NON_FILE_DIGEST_KEYS[k] for k in trail if isinstance(k, str) and k in S.NON_FILE_DIGEST_KEYS]
                where = f"{rel}:{'.'.join(map(str, trail))}"
                if not kinds:
                    unclassified.append(where)
                elif v not in self.compared[kinds[-1]]:
                    uncompared.append({"at": where, "kind": kinds[-1]})
        status = REPRODUCED if not unclassified and not uncompared else MISMATCH
        if status == MISMATCH and not unclassified and not (tier_b_ran and tier_d_ran):
            status = NOT_RUN  # the remaining values are compared only by tier-B or tier-D rows
        self.add("coverage:receipt-digests", A, status,
                 BASIS_COVERAGE, n_file_digests=len(getattr(self, "recorded_digests", ())),
                 unclassified=unclassified[:20], uncompared=uncompared[:20],
                 note="tier-B design/V/stage1 and tier-D design comparisons count only when that tier ran")

    # ------------------------------------------------------------------------------------------- tier B
    def tier_b(self):
        try:
            import ROOT  # noqa: F401
            self.have_root = True
        except Exception as exc:  # the analysis env (root_6_28) is required for ROOT producers only
            self.have_root = False
            self.root_error = repr(exc)
        self.pred_dir = self.out / "preds"
        self.pred_dir.mkdir(parents=True, exist_ok=True)
        for fn, check in ((self.b_rootpreds, "rootpred"), (self.b_figures, "figure"), (self.b_pairdiff, "pairdiff"),
                          (self.b_prefreeze, "prefreeze"), (self.b_build_v, "V:build-v"), (self.b_envelope, "envelope"),
                          (self.b_module_identity, "module")):
            self.guarded(fn, check, B, BASIS_REGENERATED)

    def _need_root(self, check) -> bool:
        if not self.have_root:
            self.add(check, B, ENV_MISSING, BASIS_REGENERATED, why=f"PyROOT not importable in {self.python}: {self.root_error}")
        return self.have_root

    def _missing(self, paths) -> list[str]:
        return [str(p) for p in paths if p is None or not Path(p).exists()]

    def b_rootpreds(self):
        for f in sorted(glob.glob(str(REPO / S.GC / "*_xsec*.json"))):
            side = json.loads(Path(f).read_text())
            name = Path(side["out"]).name
            check = f"rootpred:{name}"
            if not self._need_root(check):
                continue
            src, stored = self.local(side["input"]["path"]), self.local(side["out"])
            miss = self._missing([src, stored])
            if miss:
                self.add(check, B, INPUT_MISSING, BASIS_REGENERATED, missing=miss)
                continue
            out = self.pred_dir / name
            rc = self.launch(f"rootpred-{name}", "3d-unfolding/genie/gen5d_to_rootpreds.py",
                             ["--npz", str(src), "--kind", side["kind"], "--label", side["label"], "--out", str(out)],
                             self.pred_dir, self.out / "logs" / f"rootpred-{name}.log")
            sidecar = out.with_suffix(".json")
            if rc != 0 or not out.exists() or not sidecar.exists():
                self.add(check, B, MISMATCH, BASIS_REGENERATED, returncode=rc, why="producer failed or wrote no sidecar")
                continue
            mine = json.loads(sidecar.read_text())
            exp = {"total": side["total_sigma_cm2_per_nucleon"], "input_sha256": side["input"]["sha256"], "code_sha256": side["code_sha256"]}
            obs = {"total": mine["total_sigma_cm2_per_nucleon"], "input_sha256": mine["input"]["sha256"], "code_sha256": mine["code_sha256"]}
            st1, d1 = compare(exp, obs, 0.0)
            e_dump, o_dump = root_dump(stored), root_dump(out)
            n_hist = sum(1 for k in e_dump if k.endswith(".content"))
            st2, d2 = compare_arrays(e_dump, o_dump, 0.0)
            st3 = REPRODUCED if n_hist > 0 else MISMATCH
            self.add(check, B, worst_of(st1, st2, st3), BASIS_REGENERATED, sidecar_diffs=d1, histogram_diffs=d2,
                     n_histograms_compared=n_hist, objects=[str(x) for x in e_dump.get("__objects__", [])],
                     stored=str(stored), regenerated=str(out), stored_sha256=self.digest(stored), regenerated_sha256=sha256(out),
                     note="every key's class, and every histogram's contents, errors and edges, compared bitwise; "
                          "ROOT file bytes embed a creation time/UUID")

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
                self.add(check, B, INPUT_MISSING, BASIS_REGENERATED, missing=missing)
                continue
            log = run_dir / f"{name}.log"
            rc = self.launch(f"figure-{name}", run["producer"], argv, run_dir, log)
            want = normalize_log((REPO / run["log"]).read_text(), None, None)
            got = normalize_log(log.read_text(), str(run_dir), genfig_recorded)
            text_status = REPRODUCED if want == got and want else MISMATCH
            text_diff = None if want == got else first_line_diff(want, got)
            figs = {}
            for produced, committed in run["figures"].items():
                pf = run_dir / produced
                figs[produced] = compare_pdf(REPO / committed, pf) if pf.exists() else {"status": MISMATCH, "why": "not produced"}
            st = worst_of(REPRODUCED if rc == 0 else MISMATCH, text_status, *[v["status"] for v in figs.values()])
            self.add(check, B, st, BASIS_REGENERATED, returncode=rc, log_compare=text_status, log_lines_compared=len(want),
                     log_first_diff=text_diff, figures=figs, log=str(log), committed_log=run["log"], note=run.get("note"))

    def b_pairdiff(self):
        stage1 = REPO / S.S5P / "stage1/stage1_inspect.json"
        s5c = REPO / "docs/orchestration/state/s5c/contract.json"
        for f in sorted(glob.glob(str(REPO / S.S5P / "stage3/[fm][124]/*.json"))):
            rec = json.loads(Path(f).read_text())
            rel = Path(f).relative_to(REPO)
            check = f"pairdiff:{rel}"
            run_dir = self.out / "pairdiff" / rel.parent.name / rel.stem
            ins = [(self.local(p["a"]), self.local(p["b"])) for p in rec["inputs"]]
            stored = self.local(rec["out"]["path"])
            miss = self._missing([x for pair in ins for x in pair] + [stored])
            if miss:
                self.add(check, B, INPUT_MISSING, BASIS_REGENERATED, missing=miss[:10])
                continue
            for side, idx in (("a", 0), ("b", 1)):
                (run_dir / side).mkdir(parents=True, exist_ok=True)
                for pair in ins:
                    link = run_dir / side / pair[idx].name
                    if link.is_symlink() and Path(os.readlink(link)) != pair[idx]:
                        raise RuntimeError(f"two {side}-inputs share the name {link.name}")
                    if not link.is_symlink():
                        link.symlink_to(pair[idx])
            out = run_dir / f"{rel.stem}.npz"
            rc = self.launch(f"pairdiff-{rel.parent.name}-{rel.stem}", "nd-unfolding/s5p_pairdiff.py",
                             ["--a", str(run_dir / "a" / "*.npz"), "--b", str(run_dir / "b" / "*.npz"),
                              "--stage1", str(stage1), "--s5c-contract", str(s5c), "--label", rec["label"], "--out", str(out)],
                             REPO, run_dir / "pairdiff.log")
            if rc != 0 or not out.exists():
                self.add(check, B, MISMATCH, BASIS_REGENERATED, returncode=rc, why="producer failed", log=str(run_dir / "pairdiff.log"))
                continue
            mine = json.loads(out.with_suffix(".json").read_text())
            keys = ("label", "n_pairs", "cells", "median_abs_D_over_fB", "max_abs_D_over_fB", "median_abs_D_over_se")
            st1, d1 = compare({k: rec[k] for k in keys}, {k: mine[k] for k in keys}, S.TOL_SAME_CODE)
            pairs_exp = [(p["a_sha256"], p["b_sha256"]) for p in rec["inputs"]]
            pairs_obs = [(p["a_sha256"], p["b_sha256"]) for p in mine["inputs"]]
            st3 = REPRODUCED if pairs_exp == pairs_obs and pairs_exp else MISMATCH
            st2, d2 = compare_arrays(npz_arrays(stored), npz_arrays(out), S.TOL_SAME_CODE)
            self.add(check, B, worst_of(st1, st2, st3), BASIS_REGENERATED, summary_diffs=d1, array_diffs=d2, pairing=st3,
                     regenerated=str(out), code_recorded=rec["code_sha256"], code_now=mine["code_sha256"],
                     note="code identity is reported by the tier-A producer rows, not folded into this row")

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

    def _design_inputs(self, design: dict) -> list:
        """Every file a design names that build-v / prefreeze read."""
        files = [p for pair in design["lateral_endpoints"].values() for p in pair] + list(design["data_jitters"])
        files += [design["data_central"]] + [n["prediction"] for n in design["nulls"].values()]
        files += [s["path"] for s in design.get("process_shift", {}).values() if "path" in s]
        files += [s["path"] for s in design.get("m1_shift", {}).values() if "path" in s]
        return files

    def b_prefreeze(self):
        design = self._design(f"{S.S5P}/prod-draft/design.json")
        dj = json.loads(design.read_text())
        vrec = json.loads((REPO / S.S5P / "stage3/V/V-receipt.json").read_text())
        V = self.local(vrec["path"])
        for cmd in ("units", "devpower"):
            check = f"prefreeze:{cmd}"
            rec = json.loads((REPO / S.S5P / f"stage3/prefreeze/{cmd}.json").read_text())
            inputs_obj = self.roots.rebase(rec["inputs"])
            needed = self._design_inputs(dj) + [V]
            if cmd == "units":
                needed += [p for g in inputs_obj["generators"].values() for p in g.values()]
            else:
                globs = [inputs_obj["null_glob"]] + list(inputs_obj["alternatives"].values())
                needed += [f"{g} (no match)" for g in globs if not glob.glob(g)]
            miss = self._missing(needed)
            if miss:
                self.add(check, B, INPUT_MISSING, BASIS_REGENERATED, missing=miss[:10])
                continue
            run_dir = self.out / "prefreeze"
            run_dir.mkdir(parents=True, exist_ok=True)
            inputs = run_dir / f"{cmd}-inputs.json"
            inputs.write_text(json.dumps(inputs_obj) + "\n")
            out = run_dir / f"{cmd}.json"
            rc = self.launch(f"prefreeze-{cmd}", "nd-unfolding/s5p_prefreeze.py",
                             [cmd, "--design", str(design), "--v", str(V), "--inputs", str(inputs), "--out", str(out)],
                             REPO, run_dir / f"{cmd}.log")
            if rc != 0 or not out.exists():
                self.add(check, B, MISMATCH, BASIS_REGENERATED, returncode=rc, log=str(run_dir / f"{cmd}.log"))
                continue
            mine = json.loads(out.read_text())
            keys = ("design_sha256", "v_sha256", "code_sha256", "result")
            exp = {k: rec[k] for k in keys}
            self.compared["design"].add(rec["design_sha256"])
            self.compared["V"].add(rec["v_sha256"])
            relocated = design != REPO / f"{S.S5P}/prod-draft/design.json"
            if relocated:
                exp["design_sha256"] = sha256(design)  # the re-rooted copy; its source is pinned in tier A
            st, diffs = compare(exp, {k: mine[k] for k in keys}, S.TOL_SAME_CODE)
            self.add(check, B, st, BASIS_REGENERATED, diffs=diffs, regenerated=str(out), design=str(design), relocated_design=relocated)

    def b_build_v(self):
        check = "V:build-v"
        design = self._design(f"{S.S5P}/prod-draft/design.json")
        dj = json.loads(design.read_text())
        vrec = json.loads((REPO / S.S5P / "stage3/V/V-receipt.json").read_text())
        stored = self.local(vrec["path"])
        miss = self._missing(self._design_inputs(dj) + [stored])
        n_ens = len([p for p in glob.glob(dj["v_ensemble_glob"]) if ".partial" not in Path(p).name])
        if miss or n_ens != dj["v_ensemble_n"]:
            self.add(check, B, INPUT_MISSING, BASIS_REGENERATED, missing=miss[:10], v_ensemble_found=n_ens,
                     v_ensemble_declared=dj["v_ensemble_n"])
            return
        run_dir = self.out / "V"
        run_dir.mkdir(parents=True, exist_ok=True)
        out = run_dir / "V-s3v.npz"
        rc = self.launch("build-v", "nd-unfolding/s5p_joint.py", ["build-v", "--design", str(design), "--out", str(out)],
                         REPO, run_dir / "build-v.log")
        if rc != 0 or not out.exists():
            self.add(check, B, MISMATCH, BASIS_REGENERATED, returncode=rc, log=str(run_dir / "build-v.log"))
            return
        e, o = npz_arrays(stored), npz_arrays(out)
        me, mo = json.loads(str(e.pop("meta"))), json.loads(str(o.pop("meta")))
        me = self.roots.rebase(me)
        if design != REPO / f"{S.S5P}/prod-draft/design.json":
            me["design_sha256"] = sha256(design)
        st1, d1 = compare_arrays(e, o, S.TOL_SAME_CODE)
        st2, d2 = compare(me, mo, S.TOL_SAME_CODE)
        self.add(check, B, worst_of(st1, st2), BASIS_REGENERATED, array_diffs=d1, meta_diffs=d2, arrays_compared=sorted(e),
                 stored_sha256=self.digest(stored), regenerated_sha256=sha256(out), regenerated=str(out),
                 note="arrays compared; np.savez archive bytes carry write times")

    def b_envelope(self):
        check = "envelope"
        rec = json.loads((REPO / S.S5P / "stage3/envelope-receipt.json").read_text())
        conv = self.roots.spec("s5p:runs/s2/conv")
        needed = [self.local(p) for p in rec["products"]] + [conv / "k_b0_w3.npz"]
        needed += [conv / n if (conv / n).exists() else conv / f"{n}.partial.npz" for n in ("k_b0_gibuu.npz", "k_b0_w1.npz")]
        w2 = self.roots.spec("s5e:runs/cand/assess/W2")
        miss = self._missing(needed) + ([str(w2)] if not glob.glob(str(w2 / "*.npz")) else [])
        if miss:
            self.add(check, B, INPUT_MISSING, BASIS_REGENERATED, missing=miss[:10])
            return
        run_dir = self.out / "envelope"
        run_dir.mkdir(parents=True, exist_ok=True)
        out = run_dir / "envelope-receipt.json"
        rc = self.launch("envelope", "nd-unfolding/s5p_envelope.py",
                         ["--runs", str(self.roots.spec("s5p:runs")), "--s5e-runs", str(self.roots.spec("s5e:runs")),
                          "--stage1", str(REPO / S.S5P / "stage1/stage1_inspect.json"),
                          "--s5c-contract", str(REPO / "docs/orchestration/state/s5c/contract.json"), "--out", str(out)],
                         REPO, run_dir / "envelope.log")
        if rc != 0 or not out.exists():
            self.add(check, B, MISMATCH, BASIS_REGENERATED, returncode=rc, log=str(run_dir / "envelope.log"))
            return
        mine = json.loads(out.read_text())
        exp = self.roots.rebase(rec)
        self.compared["stage1"].add(rec["stage1_sha256"])
        self.compared["producer"].update(rec["code_sha256"].values())
        for key in sorted(set(exp) | set(mine)):
            if key not in exp or key not in mine:
                self.add(f"{check}:{key}", B, MISMATCH, BASIS_REGENERATED, why="block present on one side only")
                continue
            if key in ("bias_sources", "linearity"):
                for sub in sorted(set(exp[key]) | set(mine[key])):
                    st, diffs = compare(exp[key].get(sub), mine[key].get(sub), S.TOL_SAME_CODE)
                    why = None
                    path = S.ENVELOPE_DECLARED_FIELDS.get((key, sub))
                    if path is not None and st == MISMATCH:
                        rec_sha, obs_sha, why = S.DECLARED_DIFFERENCES[path]
                        only = diffs == [{"at": ".sha256", "expected": rec_sha, "observed": obs_sha}]
                        st = DECLARED if only else MISMATCH
                        if not only:
                            why = "differs beyond the declared sha256 change"
                    self.add(f"{check}:{key}.{sub}", B, st, BASIS_REGENERATED, diffs=diffs, why=why)
            else:
                st, diffs = compare(exp[key], mine[key], S.TOL_SAME_CODE)
                self.add(f"{check}:{key}", B, st, BASIS_REGENERATED, diffs=diffs)

    def b_module_identity(self):
        """Every checkout module a tier-B figure producer imported, against the deploy export it ran from."""
        mods = sorted({m for k, v in self.provenance.items() if k.startswith(("figure-", "rootpred-"))
                       for m in v.get("project_modules", [])})
        for rel in mods:
            if not rel.startswith("reproduction/"):
                self._deploy_identity(f"module:{rel}", B, rel)

    # ------------------------------------------------------------------------------------------- tiers C, D
    def tier_c(self):
        for key, entry in S.NOT_REGENERATED.items():
            self.add(f"not-regenerated:{key}", C, NOT_RUN, BASIS_DECLARED_ONLY, **entry)

    def tier_d(self):
        self.guarded(self._tier_d, "joint", D, BASIS_JOINT)

    def _tier_d(self):
        committed = REPO / S.JOINT["committed_result"]
        status_dir = self.roots.spec("s5p:runs/prod/status")
        finals = {n: (status_dir / f"{n}-final.json").exists() for n in S.JOINT["nulls"]}
        facts = {"committed_result_present": committed.exists(), "final_status_present": finals,
                 "terminal_condition": S.JOINT["terminal_condition"]}
        if not committed.exists():
            self.add("joint:final-result", D, PENDING, BASIS_JOINT, **facts,
                     why="the committed joint result is absent from this checkout; nothing about it is reproduced")
            return
        if not all(finals.values()):
            self.add("joint:final-status", D, INPUT_MISSING, BASIS_JOINT, **facts, local=str(status_dir),
                     why="a sequential-calibration final status the evaluator reads is missing")
            return
        for fn, check in ((self.d_receipt_identities, "joint:receipt-identities"),
                          (self.d_seed_states_copy, "joint:seed-states-copy"),
                          (self.d_frozen_code, "joint:frozen-module"),
                          (self.d_replay, "joint:replay"),
                          (self.d_independent, "joint:independent-verification")):
            self.guarded(fn, check, D, BASIS_JOINT)
        self.add("joint:figures", D, PENDING, BASIS_JOINT, figures=S.JOINT["figures"],
                 why="no joint-result figure exists yet (the note's Stage-7 text is not written); FIGURE_RUNS has no "
                     "joint entry, so no figure of the joint result is reproduced")

    def _joint_docs(self) -> dict:
        return {k: json.loads((REPO / S.JOINT[k]).read_text())
                for k in ("committed_result", "robust_labels", "missing_sensitivity", "seed_states_copy")}

    def d_receipt_identities(self):
        """The design, V and evaluator-output digests every joint receipt and status file records, against the frozen
        design, the frozen V and the committed evaluator output; and the final B of every null and the n of every
        power set against the products the lane pins counted."""
        ev_sha = S.RECEIPTS[S.JOINT["committed_result"]]
        design_sha = S.RECEIPTS[S.JOINT["design"]]
        v_sha = json.loads((REPO / S.JOINT["v_receipt"]).read_text())["sha256"]
        docs = self._joint_docs()
        ev, lab, sens, seeds = (docs[k] for k in ("committed_result", "robust_labels", "missing_sensitivity", "seed_states_copy"))
        exp, obs = {}, {}

        def pair(key, want, got):
            exp[key], obs[key] = want, got
        for name, doc, keys in (("joint-evaluate", ev, ("design_sha256", "v_sha256")),
                                ("robust-labels", lab, ("design_sha256", "evaluate_sha256")),
                                ("missing-sensitivity", sens, ("design_sha256", "evaluate_sha256")),
                                ("seed-states", seeds, ("design_sha256", "v_sha256"))):
            for k in keys:
                pair(f"{name}.{k}", {"design_sha256": design_sha, "v_sha256": v_sha, "evaluate_sha256": ev_sha}[k], doc.get(k))
        status_dir = self.roots.spec("s5p:runs/prod/status")
        pinned = self.pins["groups"] if self.pins else {}
        cal = pinned.get("joint calibration ensembles (final B; partials excluded)", {})
        pow_ = pinned.get("joint power ensembles (partials excluded)", {})
        for n in S.JOINT["nulls"]:
            st = json.loads((status_dir / f"{n}-final.json").read_text())
            pair(f"status:{n}.design_sha256", design_sha, st.get("design_sha256"))
            pair(f"status:{n}.v_sha256", v_sha, st.get("v_sha256"))
            pair(f"status:{n}.stop", True, st.get("stop"))
            for side in ("total", "shape"):
                pair(f"B:{n}:{side} (evaluated vs status)", st.get("B"), ev["decisions"][f"{n}:{side}"]["B"])
            if self.pins:
                pair(f"B:{n} (status vs lane-pinned products)", st.get("B"),
                     sum(1 for s in cal if s.startswith(f"s5p:runs/prod/cal/{n}/")))
        if self.pins:
            for key, entry in ev["power"].items():
                if key != "levels":
                    pair(f"n:{key} (evaluated vs lane-pinned products)", entry.get("n"),
                         sum(1 for s in pow_ if s.startswith(f"s5p:runs/prod/pow/{key}/")))
        self.compared["design"].add(design_sha)
        self.compared["V"].add(v_sha)
        st, diffs = compare(exp, obs, 0.0)
        self.add("joint:receipt-identities", D, st, BASIS_JOINT, n_compared=len(exp), diffs=diffs,
                 counts_against_pins=bool(self.pins),
                 note="identities only: equal digests and counts say which objects were used, not that the result is right")

    def d_seed_states_copy(self):
        """The committed seed-states copy, with its log prefix removed, must be the original whose sha256 the
        missing-seed sensitivity records."""
        raw = (REPO / S.JOINT["seed_states_copy"]).read_bytes()
        prefix = b'"log": "' + S.JOINT["seed_states_log_prefix"].encode()
        n = raw.count(prefix)
        original = raw.replace(prefix, b'"log": "')
        want = self._joint_docs()["missing_sensitivity"]["seed_states_sha256"]
        got = hashlib.sha256(original).hexdigest()
        n_tasks = len(json.loads(raw)["tasks"])
        self.add("joint:seed-states-copy", D, REPRODUCED if got == want and n == n_tasks else MISMATCH, BASIS_RECOMPUTED,
                 expected=want, observed=got, prefixed_values=n, tasks=n_tasks,
                 against=f"{S.JOINT['missing_sensitivity']}:seed_states_sha256")

    def d_frozen_code(self):
        for rel in S.JOINT["frozen_modules"]:
            self._deploy_identity(f"joint:frozen-module:{rel}", D, rel, S.FROZEN_ADMISSION_COMMIT,
                                  "the frozen admission (the evaluation deploy verified byte identity to it)")

    def d_replay(self):
        """``s5p_joint.py evaluate`` from this checkout on the preserved products, then the label step
        (``s5p_robust_labels.py``) on that output; both compared with the committed files at the same-code tolerance."""
        design = self._design(S.JOINT["design"])
        dj = json.loads(design.read_text())
        vrec = json.loads((REPO / S.JOINT["v_receipt"]).read_text())
        V = self.local(vrec["path"])
        globs = [n["calibration_glob"] for n in dj["nulls"].values()] + [p["glob"] for p in dj.get("power", {}).values()]
        status = [n["calibration_n"]["sequential_status"] for n in dj["nulls"].values()
                  if isinstance(n["calibration_n"], dict)]
        miss = self._missing(self._design_inputs(dj) + [V] + status) + [g for g in globs if not glob.glob(g)]
        if miss:
            self.add("joint:replay", D, INPUT_MISSING, BASIS_JOINT, missing=miss[:10])
            return
        docs = self._joint_docs()
        run_dir = self.out / "joint"
        run_dir.mkdir(parents=True, exist_ok=True)
        out = run_dir / "joint-evaluate.json"
        rc = self.launch("joint-evaluate", "nd-unfolding/s5p_joint.py",
                         ["evaluate", "--design", str(design), "--v", str(V), "--out", str(out)],
                         REPO, run_dir / "evaluate.log", extra_env=S.JOINT["thread_env"])
        if rc != 0 or not out.exists():
            self.add("joint:replay", D, MISMATCH, BASIS_JOINT, returncode=rc, log=str(run_dir / "evaluate.log"))
            return
        relocated = design != REPO / S.JOINT["design"]
        expected = self.roots.rebase(docs["committed_result"])
        if relocated:
            expected["design_sha256"] = sha256(design)
        st, diffs = compare(expected, json.loads(out.read_text()), S.TOL_SAME_CODE)
        got_sha = sha256(out)
        self.add("joint:replay", D, st, BASIS_JOINT, diffs=diffs, regenerated=str(out), regenerated_sha256=got_sha,
                 committed_sha256=S.RECEIPTS[S.JOINT["committed_result"]], tolerance=S.TOL_SAME_CODE,
                 bitwise=got_sha == S.RECEIPTS[S.JOINT["committed_result"]], relocated_design=relocated,
                 thread_env=S.JOINT["thread_env"],
                 note="a replay of the frozen evaluator; it verifies the committed file, not the statistics")
        labels = run_dir / "robust-labels.json"
        rc = self.launch("joint-robust-labels", "nd-unfolding/s5p_robust_labels.py",
                         ["--evaluate", str(out), "--design", str(design), "--out", str(labels)],
                         REPO, run_dir / "robust-labels.log")
        if rc != 0 or not labels.exists():
            self.add("joint:replay-labels", D, MISMATCH, BASIS_JOINT, returncode=rc, log=str(run_dir / "robust-labels.log"))
        else:
            exp_l = dict(docs["robust_labels"], evaluate=str(out), evaluate_sha256=got_sha)
            if relocated:
                exp_l["design_sha256"] = sha256(design)
            st, diffs = compare(exp_l, json.loads(labels.read_text()), S.TOL_SAME_CODE)
            self.add("joint:replay-labels", D, st, BASIS_JOINT, diffs=diffs, regenerated=str(labels),
                     note="the label step run on the replayed evaluator output (its input path and digest are therefore "
                          "this run's; the committed labels' input digest is checked by joint:receipt-identities)")
        mods = sorted({m for k in ("joint-evaluate", "joint-robust-labels")
                       for m in self.provenance.get(k, {}).get("project_modules", [])})
        for rel in mods:
            if not rel.startswith("reproduction/"):
                self._deploy_identity(f"joint:module:{rel}", D, rel, S.JOINT["evaluation_deploy_commit"],
                                      "the clean deploy the joint evaluation ran from")

    def d_independent(self):
        """Record the independent recomputation's report by digest. Its verdict is NOT read or graded here; the only
        check is that it is the report the recording cites (a different report at the route is a MISMATCH)."""
        indep = self.config.get("joint", {}).get("independent_compare")
        want = S.JOINT["independent_compare_sha256"]
        if not indep or not Path(indep).is_file():
            self.add("joint:independent-verification", D, INPUT_MISSING, BASIS_JOINT, report=indep, cited_sha256=want,
                     why="no independent recomputation report at the configured route (config joint.independent_compare)")
            return
        got = sha256(indep)
        if got != want:
            self.add("joint:independent-verification", D, MISMATCH, BASIS_JOINT, report=indep, sha256=got,
                     cited_sha256=want, why=f"not the report {S.JOINT['independent_compare_cited_by']} cites")
            return
        self.add("joint:independent-verification", D, INFO, BASIS_JOINT, report=indep, sha256=got,
                 cited_by=S.JOINT["independent_compare_cited_by"],
                 why="recorded by digest (it is the report the recording cites); read and judge the independent "
                     "lane's own report: this harness does not grade it")

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
        env["checkout"] = {"path": str(REPO), "head": git("rev-parse", "HEAD").stdout.strip(),
                           "status_at_start": getattr(self, "status_at_start", None),
                           "status_at_end": git("status", "--porcelain").stdout.splitlines(),
                           "scope_source_commit": S.SOURCE_COMMIT}
        env["checkout"]["clean"] = not env["checkout"]["status_at_start"] and not env["checkout"]["status_at_end"]
        return env

    def record_start(self):
        self.status_at_start = git("status", "--porcelain").stdout.splitlines()

    def exit_code(self, tiers) -> int:
        rows = self.results
        if any(r.status in FAILING for r in rows):
            return 1
        ab = [r for r in rows if r.tier in (A, B)]
        if not {"A", "B", "D"} <= set(tiers) or not ab or any(r.status not in PASSING for r in ab):
            return 2
        d = [r for r in rows if r.tier == D]
        if not any(r.check == "joint:replay" and r.status in PASSING for r in d):
            return 2
        if any(r.status not in PASSING and D_NON_GRADES.get(r.check) != r.status for r in d):
            return 2
        return 0

    def write_report(self, tiers) -> int:
        code = self.exit_code(tiers)
        summary: dict = {}
        for r in self.results:
            key = f"{r.tier} | {r.basis}"
            summary.setdefault(key, {}).setdefault(r.status, 0)
            summary[key][r.status] += 1
        declared = [asdict(r) for r in self.results if r.status == DECLARED]
        pins_info = None
        if self.pins is not None:
            pins_info = {"path": str(self.pins_path) if self.pins_path else None,
                         "sha256": sha256(self.pins_path) if self.pins_path else None,
                         "measured_utc": self.pins.get("measured_utc"), "host": self.pins.get("host"),
                         "n_files": sum(len(v) for v in self.pins["groups"].values()),
                         "group_measured_utc": {g: pin_measured_utc(self.pins, g) for g in self.pins["groups"]},
                         "extends": self.pins.get("extends")}
        report = {"schema": "s5p-reproduction-report/2", "tiers_run": [{"A": A, "B": B, "C": C, "D": D}[t] for t in tiers],
                  "exit_code": code, "environment": self.environment(), "config": self.config, "pins_file": pins_info,
                  "relocated": not self.roots.identity(), "n_declared_expected": S.N_DECLARED,
                  "summary_by_tier_and_basis": summary, "declared_differences": declared,
                  "provenance": self.provenance, "results": [asdict(r) for r in self.results]}
        (self.out / "report.json").write_text(json.dumps(report, indent=1, default=str) + "\n")
        (self.out / "report.md").write_text(render_md(report))
        print(json.dumps({"out": str(self.out), "exit_code": code, "declared_differences": len(declared),
                          "summary": summary}, indent=1))
        return code


# ----------------------------------------------------------------------------------------------- helpers

def recorded_roots() -> list[str]:
    return [v for v in S.RECORDED_ROOTS.values()]


def check_out_dir(out: Path, forbidden: list, lexical: list = ()) -> None:
    """A run writes only to a new directory outside the checkout, every configured root and every recorded root
    (so it can neither dirty the tree under test nor touch the preserved campaign products). ``forbidden`` paths
    are resolved; ``lexical`` ones (the recorded roots) are compared as strings only, so a relocated run makes no
    filesystem access under them at all."""
    raw = os.path.normpath(os.path.abspath(out))
    out = Path(out).resolve()
    for f in forbidden:
        f = Path(f).resolve()
        if out == f or f in out.parents:
            raise SystemExit(f"{out} is inside {f}; choose a fresh directory outside the checkout and every input root")
    for f in lexical:
        if under(str(out), f) or under(raw, f):
            raise SystemExit(f"{out} is inside the recorded root {f}; choose a fresh directory outside it")
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"{out} exists and is not empty; every run writes a fresh directory")


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
    """Every key of a ROOT file with its class (``__objects__``), and every histogram's contents and errors incl.
    under/overflow and its edges, as named arrays."""
    import ROOT
    ROOT.gROOT.SetBatch(True)
    f = ROOT.TFile.Open(str(path))
    out, objects = {}, []
    for key in f.GetListOfKeys():
        obj = key.ReadObj()
        name = key.GetName()
        objects.append(f"{name}:{obj.ClassName()}")
        if not obj.InheritsFrom("TH1"):
            continue
        n = obj.GetNcells()
        out[f"{name}.content"] = np.array([obj.GetBinContent(i) for i in range(n)])
        out[f"{name}.error"] = np.array([obj.GetBinError(i) for i in range(n)])
        for ax, a in (("x", obj.GetXaxis()), ("y", obj.GetYaxis()), ("z", obj.GetZaxis())):
            out[f"{name}.edges_{ax}"] = np.array([a.GetBinLowEdge(i) for i in range(1, a.GetNbins() + 2)])
    f.Close()
    out["__objects__"] = np.array(sorted(objects))
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


def _row(r: dict, width: int = 500) -> str:
    d = {k: v for k, v in r["detail"].items() if v not in (None, [], {}) and k != "traceback"}
    return f"- `{r['check']}` ({r['tier']}; {r['basis']}): " + json.dumps(d, default=str)[:width]


def render_md(rep: dict) -> str:
    env, res = rep["environment"], rep["results"]
    by = lambda *sts: [r for r in res if r["status"] in sts]  # noqa: E731
    pins = rep.get("pins_file")
    lines = ["# s5p reproduction report", "",
             f"- checkout `{env['checkout']['path']}` at `{env['checkout']['head']}` (clean before and after: "
             f"{env['checkout']['clean']}); scope written against `{env['checkout']['scope_source_commit'][:12]}`",
             f"- {env['host']}, Python {env['python']}, numpy {env['numpy']}, ROOT {env['ROOT']}, matplotlib {env['matplotlib']}, {env['utc']}",
             f"- input roots: {json.dumps(rep['config']['roots'])} (relocated from the recorded locations: {rep['relocated']})",
             "- lane pins: " + (f"`{pins['path']}` sha256 `{pins['sha256']}`, {pins['n_files']} files, measured "
                                 f"{pins['measured_utc']} on {pins['host']}" if pins else "none given")
             + (f"; groups copied from `{pins['extends']['path']}` keep its measurement time "
                f"{pins['extends']['measured_utc']}" if pins and pins.get("extends") else ""),
             f"- tiers run: {', '.join(rep['tiers_run'])}; exit code **{rep['exit_code']}** "
             "(0 = every tier-A/B row reproduced exactly, within tolerance, or as a declared difference)", "",
             "Tiers are separate claims: A replays preserved products, B regenerates derived products from the checkout, "
             "C is NOT run, D replays the final joint result's frozen evaluator and label step from the checkout and "
             "records the independent report by digest (it does not grade it).", "",
             "## Summary by tier and basis", "", "| tier and basis | status | count |", "|---|---|---|"]
    for key, cs in sorted(rep["summary_by_tier_and_basis"].items()):
        for st, n in sorted(cs.items()):
            lines.append(f"| {key} | {st} | {n} |")
    fails = by(MISMATCH, ERROR, INPUT_MISSING, ENV_MISSING)
    lines += ["", f"## Failures, errors and missing inputs ({len(fails)})", ""] + ([_row(r, 900) for r in fails] or ["none"])
    decl = by(DECLARED)
    lines += ["", f"## Declared differences ({len(decl)} of {rep['n_declared_expected']} declared): measured, NOT exact matches", "",
              "Each is declared in `scope.py` by its recorded AND its observed digest; any other value would be a MISMATCH.", ""]
    for r in decl:
        d = r["detail"]
        lines.append(f"- `{r['check']}` ({r['tier']}; {r['basis']})")
        lines.append(f"  - recorded `{d.get('expected', '')}`, observed `{d.get('observed', '')}`" if "expected" in d
                     else f"  - differences: `{json.dumps(d.get('diffs'))}`")
        lines.append(f"  - {d.get('why')}")
    if not decl:
        lines.append("none")
    tol = by(WITHIN_TOL)
    lines += ["", f"## Within tolerance ({len(tol)}): not bitwise", ""] + ([_row(r) for r in tol] or ["none"])
    lane = [r for r in res if r["basis"] == BASIS_LANE]
    groups: dict = {}
    for r in lane:
        g = r["detail"].get("group") or r["check"].split(":", 1)[-1]
        groups.setdefault(g, {}).setdefault(r["status"], 0)
        groups[g][r["status"]] += 1
    lines += ["", "## Newly recorded digests (lane pins): constancy since the pin, NOT historical provenance", "",
              "No producer recorded these digests. A match proves the bytes are unchanged since the pin was measured; "
              "what ties them to production is tier B regenerating committed outputs from them.", ""]
    lines += [f"- {g}: {json.dumps(c)}" for g, c in sorted(groups.items())] or ["none"]
    later = by(NOT_RUN, PENDING, INFO)
    lines += ["", f"## Not run, pending, informational ({len(later)})", ""] + ([_row(r, 400) for r in later] or ["none"])
    lines += ["", "## Exact matches, by basis", ""]
    exact: dict = {}
    for r in by(REPRODUCED):
        exact.setdefault(r["basis"], []).append(r)
    for basis, rows in sorted(exact.items()):
        lines += ["", f"### {basis} ({len(rows)})", ""]
        for r in rows:
            mode = r["detail"].get("mode")
            lines.append(f"- `{r['check']}` ({r['tier']})" + (f" [{mode}]" if mode else ""))
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------------------------------------------- CLI

def cmd_list() -> int:
    print(f"scope written against {S.SOURCE_COMMIT} (frozen admission {S.FROZEN_ADMISSION_COMMIT})\n")
    print(f"tier A replay: {len(S.RECEIPTS)} committed receipts/logs/figures pinned; every recorded digest in "
          f"{len(S.DIGEST_SOURCES)} JSON receipts (with a coverage row); producer identity; prediction totals; F2/F4/M1 "
          f"summaries; V fields; lane pins of unrecorded inputs ({sum(len(v) for v in S.UNRECORDED_INPUT_GLOBS.values())} globs)")
    print("tier B regenerate: 8 prediction ROOT files; figure runs " + ", ".join(S.FIGURE_RUNS)
          + "; 17 F2/F4/M1 pair differences; prefreeze units and devpower; V (build-v); the study-P envelope")
    print("tier C NOT run:")
    for k, v in S.NOT_REGENERATED.items():
        print(f"  {k}: {v['what']} -- {v['why_not_run']}")
    print(f"tier D joint: {len([k for k in S.RECEIPTS if '/stage7/joint/' in k])} committed joint outputs; replay of "
          f"s5p_joint.py evaluate and s5p_robust_labels.py; receipt identities; frozen-module and deploy identity; "
          f"the independent report recorded by digest; joint figures: {len(S.JOINT['figures'])} (none exist yet). "
          f"Terminal: {S.JOINT['terminal_condition']}")
    print(f"\ndeclared differences ({S.N_DECLARED}):")
    for k, (rec, obs, why) in S.DECLARED_DIFFERENCES.items():
        print(f"  digest {k}: {rec[:8]} -> {obs[:8]}")
    for (name, rec), (obs, why) in S.DECLARED_CODE.items():
        print(f"  producer {name}: {rec[:8]} -> {obs[:8]}")
    for (key, sub), path in S.ENVELOPE_DECLARED_FIELDS.items():
        print(f"  envelope {key}.{sub}: sha256 of {Path(path).name}")
    return 0


def pin_measured_utc(pins: dict, group: str) -> str | None:
    """When a group's digests were measured: a group copied by ``pin --extend`` keeps its source file's time."""
    ext = pins.get("extends")
    if ext and group in ext.get("groups", []):
        return ext.get("measured_utc")
    return pins.get("measured_utc")


def cmd_pin(config: dict, out: Path, extend: Path | None = None) -> int:
    """Measure the sha256 of every file the scope's unrecorded-input globs name. With ``extend``, every group that
    file already pins is copied verbatim (keeping that file's measurement time, recorded under ``extends``) and only
    the groups it lacks are measured, so a constancy claim is never silently restarted."""
    if out.exists():
        raise SystemExit(f"refusing to overwrite {out}")
    roots = Roots(config["roots"])
    h = Harness(config, None)
    old = json.loads(extend.read_text()) if extend else {"groups": {}}
    stale = sorted(set(old["groups"]) - set(S.UNRECORDED_INPUT_GLOBS))
    if stale:
        raise SystemExit(f"{extend} pins groups the scope no longer declares: {stale}")
    if old.get("extends"):
        raise SystemExit(f"{extend} is itself an extension; extend its source instead")
    groups, copied = {}, []
    for group, specs in S.UNRECORDED_INPUT_GLOBS.items():
        if group in old["groups"]:
            groups[group] = old["groups"][group]
            copied.append(group)
            continue
        groups[group] = {}
        for spec in h._expand(specs):
            p = roots.spec(spec)
            groups[group][spec] = {"sha256": sha256(p), "bytes": p.stat().st_size}
    doc = {"schema": "s5p-reproduction-pins/2" if extend else "s5p-reproduction-pins/1", "measured_utc": now(),
           "host": platform.node(),
           "measured_by": "reproduction/s5p/repro_s5p.py pin (lane-measured; no producer recorded these digests)",
           "roots": {k: str(v) for k, v in roots.local_roots.items()}}
    if extend:
        rel = extend.resolve()
        doc["extends"] = {"path": str(rel.relative_to(REPO)) if REPO in rel.parents else str(rel),
                          "sha256": sha256(extend), "measured_utc": old.get("measured_utc"), "host": old.get("host"),
                          "groups": copied}
    doc["groups"] = groups
    out.write_text(json.dumps(doc, indent=1) + "\n")
    print(json.dumps({g: len(v) for g, v in groups.items()} | {"copied_groups": len(copied)}))
    return 0


def cmd_stage(config: dict, pins: dict, to: Path) -> int:
    """Copy exactly the inputs the scope declares (every receipt-recorded file digest, every lane-pinned file) from
    the configured roots into ``to/<root>/<relative path>``, verifying each copy's digest against the source. A
    relocated run on ``to`` then fails with INPUT_MISSING wherever the declared inventory is incomplete. Reads only;
    nothing is written outside ``to``."""
    roots = Roots(config["roots"])
    to = to.resolve()
    check_out_dir(to, [REPO] + list(roots.local_roots.values()), recorded_roots())
    files = {}
    for rel in S.DIGEST_SOURCES:
        for path, want, _ in declared_digests(json.loads((REPO / rel).read_text())):
            sp = roots.split(path)
            if sp is not None:
                files.setdefault(sp, set()).add(("receipt", want))
    for group, entries in pins["groups"].items():
        for spec, want in entries.items():
            name, rel = spec.split(":", 1)
            files.setdefault((name, rel), set()).add(("lane-pin", want["sha256"]))
    to.mkdir(parents=True, exist_ok=True)
    manifest, absent, nbytes = [], [], 0
    for (name, rel), bases in sorted(files.items()):
        src = roots.local_roots[name] / rel
        if not src.is_file():
            absent.append(f"{name}:{rel}")
            continue
        dst = to / name / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        s_src, s_dst = sha256(src), sha256(dst)
        if s_src != s_dst:
            raise SystemExit(f"copy of {src} changed its digest")
        nbytes += dst.stat().st_size
        manifest.append({"root": name, "rel": rel, "sha256": s_dst, "bytes": dst.stat().st_size,
                         "bases": sorted(b for b, _ in bases), "matches_declared": sorted({w == s_dst for _, w in bases})})
    for name in S.RECORDED_ROOTS:
        (to / name).mkdir(exist_ok=True)
    doc = {"schema": "s5p-reproduction-staging/1", "created_utc": now(), "host": platform.node(),
           "from_roots": config["roots"], "roots": {k: str(to / k) for k in S.RECORDED_ROOTS},
           "n_files": len(manifest), "bytes": nbytes, "absent_at_source": absent, "files": manifest}
    (to / "staging-manifest.json").write_text(json.dumps(doc, indent=1) + "\n")
    print(json.dumps({k: doc[k] for k in ("roots", "n_files", "bytes")} | {"absent_at_source": len(absent)}, indent=1))
    return 0


_QUOTED = re.compile(r'"(/[^"]*)"')


def cmd_scan_trace(trace: Path, expect_prefix: str) -> int:
    """Every path an strace %file trace touched under a RECORDED root (a relocated run must touch none). Exit 0 if
    none and the trace demonstrably saw the run (it touched ``expect_prefix``); 1 on any recorded-root access; 2 if
    the trace saw nothing under ``expect_prefix`` (it could not have looked)."""
    prefixes = [v for k, v in S.RECORDED_ROOTS.items()]
    hits, seen, n_lines = {}, 0, 0
    with open(trace, errors="replace") as fh:
        for line in fh:
            n_lines += 1
            for p in _QUOTED.findall(line):
                if under(p, expect_prefix):
                    seen += 1
                for pre in prefixes:
                    if under(p, pre):
                        hits.setdefault(p, line.strip()[:300])
    code = 1 if hits else (2 if seen == 0 else 0)
    print(json.dumps({"trace": str(trace), "lines": n_lines, "accesses_under_expected_prefix": seen,
                      "recorded_root_paths_touched": len(hits), "examples": dict(list(hits.items())[:20]),
                      "exit_code": code}, indent=1))
    return code


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    p = sub.add_parser("pin")
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--extend", type=Path, default=None, help="copy the groups this pins file has; measure the rest")
    s = sub.add_parser("stage")
    s.add_argument("--config", type=Path, required=True)
    s.add_argument("--pins", type=Path, required=True)
    s.add_argument("--to", type=Path, required=True)
    t = sub.add_parser("scan-trace")
    t.add_argument("--trace", type=Path, required=True)
    t.add_argument("--expect-prefix", required=True)
    r = sub.add_parser("run")
    r.add_argument("--config", type=Path, required=True)
    r.add_argument("--tiers", default="A,B,C,D")
    r.add_argument("--pins", type=Path, default=None)
    a = ap.parse_args(argv)
    if a.cmd == "list":
        return cmd_list()
    if a.cmd == "scan-trace":
        return cmd_scan_trace(a.trace, a.expect_prefix)
    config = json.loads(a.config.read_text())
    if a.cmd == "pin":
        return cmd_pin(config, a.out, a.extend)
    if a.cmd == "stage":
        return cmd_stage(config, json.loads(a.pins.read_text()), a.to)
    tiers = [t.strip().upper() for t in a.tiers.split(",") if t.strip()]
    if set(tiers) - set("ABCD"):
        raise SystemExit(f"unknown tiers {tiers}")
    h = Harness(config, json.loads(a.pins.read_text()) if a.pins else None, a.pins.resolve() if a.pins else None)
    h.record_start()
    h.prepare_out()
    shutil.copy(a.config, h.out / "config.json")
    for tier, fn in (("A", h.tier_a), ("B", h.tier_b), ("C", h.tier_c), ("D", h.tier_d)):
        if tier in tiers:
            fn()
    if "A" in tiers:
        h.guarded(lambda: h.coverage("B" in tiers, "D" in tiers), "coverage:receipt-digests", A, BASIS_COVERAGE)
    return h.write_report(tiers)


if __name__ == "__main__":
    raise SystemExit(main())
