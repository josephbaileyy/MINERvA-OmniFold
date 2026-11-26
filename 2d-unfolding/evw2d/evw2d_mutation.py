#!/usr/bin/env python3
"""EVW2D's mutants (EVW2D-DECLARATION.md §5): each replaces one exact span of ``evw2d.py`` (it must occur exactly once)
and the full suite ``test_evw2d.py`` must then fail: pytest exit 1 with at least one named failing test, never a
collection error. Each case records its failing tests, the first error line and the mutant's sha256. A control with no
mutation must pass. Each mutant runs on a copy of the evw2d directory, imported by the suite through
``EVW2D_MUTANT``; the checkout is not written. The driver tree must be clean (``git status --ignored``) before the
campaign and after every case, or the campaign fails. Each worker has its own sparse git worktree of the driver tree
at the pinned commit (made at the start, removed at the end), so no case can taint another's. A kill needs pytest
exit 1 and a named failing test, and is not counted when the first error is an import or syntax error; each case
records its kind ("failed": an assertion or refusal inside a test; "error": a test's setup raised; "none": no
test failed).

    EVW2D_DRIVER_TREE=/path/to/tree python3 evw2d_mutation.py PYTHON OUT_JSON [WORKERS]
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import queue
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "evw2d.py"
TESTS = HERE / "test_evw2d.py"

MUTANTS = [
    ('KEY_WRECO_BOUND', '(wr0 < 1e4)', '(wr0 <= 1e4)'),
    ('KEY_WTRUTH_SIGN', '(wt0 >= 0)', '(wt0 > -1)'),
    ('KEY_RECO_TOP_EDGE', '(rp <= pt_hi)', '(rp < pt_hi)'),
    ('KEY_NO_THETA', 'driver.in_truth_phase_space(a, b, pt_lo, pt_hi, pz_lo, pz_hi)', '(pt_lo <= a <= pt_hi and pz_lo <= b <= pz_hi)'),
    ('KEY_RECO_NEEDS_PASS', 'keep = good_w & (tru_ok | (passed & rec_ok))', 'keep = good_w & (tru_ok | rec_ok)'),
    ('KEY_TRUTH_SENTINEL', '"truth_pt": np.where(np.isfinite(tp), tp, -9999.0)', '"truth_pt": tp'),
    ('KEY_RECO_SENTINEL', '"reco_pt": np.where(pr, rp[keep], -9999.0)', '"reco_pt": rp[keep]'),
    ('KEY_POT', '"w_truth": wt0[keep] * pot_scale', '"w_truth": wt0[keep]'),
    ('KEY_ENTRY_NUMBERS', 'return {"entry": cols["entry"][keep],', 'return {"entry": np.flatnonzero(keep) + 1,'),
    ('KEY_BOUNDS', 'bounds = (pt_edges[0], pt_edges[-1], pz_edges[0], pz_edges[-1])', 'bounds = (pt_edges[0], pt_edges[-2], pz_edges[0], pz_edges[-1])'),
    ('KEY_EQUAL', '"pass": bool(all(equal.values()) and increasing and fits)}', '"pass": bool(increasing and fits)}'),
    ('KEY_INCREASING', '"pass": bool(all(equal.values()) and increasing and fits)}', '"pass": bool(all(equal.values()) and fits)}'),
    ('KEY_UINT32', 'e.max() < 2 ** 32', 'e.max() < 2 ** 40'),
    ('KEY_FLOAT_BITS', 'return bool(np.array_equal(a.view(np.uint64), b.view(np.uint64)))', 'return bool(np.array_equal(a, b))'),
    ('KEY_DTYPE', '    if types != want:\n', '    if False:\n'),
    ('KEY_SIM_PASS_DTYPE', 'want = {k: ("UChar_t" if k == "sim_pass" else "Double_t") for k in SIGNAL_BRANCHES}', 'want = {k: (types[k] if k == "sim_pass" else "Double_t") for k in SIGNAL_BRANCHES}'),
    ('KEY_IMPLICIT_MT', 'if ROOT.ROOT.IsImplicitMTEnabled():', 'if False:'),
    ('TABLE_UNFOLDED', '"w_unfolded": step2.astype(np.float64) * w_prior}', '"w_unfolded": step2.astype(np.float64)}'),
    ('TABLE_ENTRY', 'return {"entry": indep["entry"][d["pt_mask"]].astype(np.uint32),', 'return {"entry": indep["entry"][:int(d["pt_mask"].sum())].astype(np.uint32),'),
    ('FLUX_ULP', 'spread <= ulp)}', 'spread <= 2 * ulp)}'),
    ('FLUX_COUNT', 'if f.shape != (14,) or not np.all(np.isfinite(f)):', 'if not np.all(np.isfinite(f)):'),
    ('FLUX_SCALAR_ON_FAIL', '    if flux_ok:\n        constants["phi_m2_per_POT"]', '    if True:\n        constants["phi_m2_per_POT"]'),
    ('COMPLETE_SORT', 'i = np.lexsort(tuple(np.ascontiguousarray(x).view(np.uint64) for x in s[::-1]))', 'i = np.arange(s[0].size)'),
    ('COMPLETE_VALUE_SORT', 'j = np.lexsort(tuple(np.ascontiguousarray(x).view(np.uint64) for x in d[::-1]))', 'j = np.lexsort(d[::-1])'),
    ('COMPLETE_ALL_COLUMNS', 'equal = all(same_bits(a[i], b[j]) for a, b in zip(s, d))', 'equal = same_bits(s[0][i], d[0][j])'),
    ('CMAP_TOL', 'kind = ("pass" if pos.any() and zeros and dev <= CMAP_ATOL else', 'kind = ("pass" if pos.any() and zeros and dev <= 1e3 * CMAP_ATOL else'),
    ('CMAP_ZERO_CELLS', 'kind = ("pass" if pos.any() and zeros and dev <= CMAP_ATOL else', 'kind = ("pass" if pos.any() and dev <= CMAP_ATOL else'),
    ('CMAP_SKIPPED', '    if not findings:\n        controls["C-CMAP"]', '    if False:\n        controls["C-CMAP"]'),
    ('XSEC_CM2', '* dpz[iy])) * cm2_per_m2', '* dpz[iy]))'),
    ('XSEC_ZERO_FLUX', 'if flux_i > 0 and n_nucleons > 0', 'if n_nucleons > 0'),
    ('XSEC_CELL_ORDER', 'return np.bincount((ip * ny + iz)[ok]', 'return np.bincount((iz * nx + ip)[ok]'),
    ('XSEC_EVENT_C', 'return np.divide(num, den, out=np.zeros_like(num), where=den != 0)', 'return np.divide(den, num, out=np.zeros_like(num), where=num != 0)'),
    ('XSEC_FLUX_INDEX', 'flux_i = float(flux_bins[ix])', 'flux_i = float(flux_bins[0])'),
    ('FLOW_SIDE', 'ix = np.searchsorted(pe, np.asarray(pt, np.float64), side="right")', 'ix = np.searchsorted(pe, np.asarray(pt, np.float64), side="left")'),
    ('EXACT_RTOL', '"pass": bool(nz.any() and rel <= rtol and zeros)}', '"pass": bool(nz.any() and rel <= 10 * rtol and zeros)}'),
    ('EXACT_ZEROS', '"pass": bool(nz.any() and rel <= rtol and zeros)}', '"pass": bool(nz.any() and rel <= rtol)}'),
    ('EXACT_NONEMPTY', '"pass": bool(nz.any() and rel <= rtol and zeros)}', '"pass": bool(rel <= rtol and zeros)}'),
    ('FILE_META', '"meta": meta_back == written, ', '"meta": True, '),
    ('FILE_ENTRIES', '"entries": same_bits(e, indep["entry"][indep["pass_truth"]]),', '"entries": True,'),
    ('FILE_TRUTH_PT', '"truth_pt": in_range and same_bits(back["truth_pt"], cols["MC"][e]),', '"truth_pt": True,'),
    ('FILE_UNFOLDED', '"w_unfolded": same_bits(back["w_unfolded"], rows["w_unfolded"]),', '"w_unfolded": True,'),
    ('FILE_DTYPES', '"dtypes": back["entry"].dtype == np.uint32 and', '"dtypes": True or'),
    ('FLOW_TOL', '"pass": bool(nz.any() and rel <= FLOW_RTOL and np.all(mine[~nz] == 0))}\n    return {**res', '"pass": bool(nz.any() and rel <= 1.0 and np.all(mine[~nz] == 0))}\n    return {**res'),
    ('FLOW_TRUTH_HIST', 'for name, col in (("hUnfold2D", "w_unfolded"), ("hTruth2D", "w_prior")):', 'for name, col in (("hUnfold2D", "w_unfolded"),):'),
    ('RUN_SAVED_CONSTANTS', 'k = meta_back["constants"]  # the exactness tests use the saved constants', 'k = meta["constants"]  # the exactness tests use the saved constants'),
    ('RUN_NO_FALLBACK', '    if fallback:  # the declared fallback', '    if False:  # the declared fallback'),
    ('RUN_COMPLETE_IS_FATAL', '    soft = {"C-COMPLETE"} | ({"C-CMAP"} if "C-CMAP" in findings else set())', '    soft = set()'),
    ('RUN_SELF_AGAINST_ER', 'self_exact = exact(ours, interior(made["hXSec2D"], nx, ny), EXACT_RTOL)', 'self_exact = exact(ours, refs["er"], EXACT_RTOL)'),
    ('SELF_FILE_DRIVER', '"pass": bool(self_exact["pass"] and file_equals_driver)}', '"pass": bool(self_exact["pass"])}'),
    ('RUN_PAPER_EDGES', 'controls["C-EXACT-PAPER"] = exact(from_file(k["validated_grids"]["paper"], k["analysis_pz_edges"]),', 'controls["C-EXACT-PAPER"] = exact(ours,'),
    ('RUN_REC_NAMES', '    controls["C-REC"] = rec.verify(SEAMS)\n    phase("controls")', '    controls["C-REC"] = rec.verify(SEAMS[:2])\n    phase("controls")'),
    ('RUN_REQUIRE', '    rec.require(SEAMS)\n', '\n'),
    ('RUN_CPUS', 'if cpus != int(cfg["cpus"]):', 'if False:'),
    ('RUN_THREADS', 'if threads != cfg["thread_env"]:', 'if False:'),
    ('RUN_OUT_EXISTS', '    if out.exists():\n        raise GateFailure(f"{out} exists")', '    if False:\n        raise GateFailure(f"{out} exists")'),
    ('RUN_PINS_AFTER', '"pass": after == cfg["driver_tree"]["code_sha256"] == tree_sha and not caches}', '"pass": not caches}'),
    ('RUN_DONE_COMPLETE', 'verdict = "PASS" if passed and acc["pass"] else "FAIL"', 'verdict = "PASS" if passed else "FAIL"'),
    ('RUN_POT_META', '"data_pot": float(data_pot), "mc_pot": float(pot[1])', '"data_pot": float(data_pot), "mc_pot": float(pot[0])'),
    ('REF_GRIDS', 'if refs[k].dtype != np.float64 or not same_bits(refs[k], np.asarray(v, np.float64)):', 'if refs[k].dtype != np.float64:'),
    ('REF_PIN', 'if hashlib.sha256(raw).hexdigest() != cfg["references"]["sha256"]:', 'if False:'),
    ('REC_OUT_UNCHANGED', 'good = args_ok and now_out == c["out_digest"]', 'good = args_ok'),
    ('REC_ARGS_UNCHANGED', 'good = args_ok and now_out == c["out_digest"]', 'good = now_out == c["out_digest"]'),
    ('REC_TWICE', '            if name in self.calls:\n                raise', '            if False:\n                raise'),
    ('REC_IDENTITY', '            return out\n        recorded.__wrapped__', '            return tuple(list(out)) if isinstance(out, tuple) else out\n        recorded.__wrapped__'),
    ('REC_DICT_COPY', '            return out\n        recorded.__wrapped__', '            return dict(out) if isinstance(out, dict) else out\n        recorded.__wrapped__'),
    ('REC_REQUIRE', '        if missing:\n            raise GateFailure', '        if False:\n            raise GateFailure'),
    ('DIGEST_SHAPE', 'h.update(f"nd{a.dtype.str}{a.shape}".encode())', 'h.update(f"nd{a.dtype.str}".encode())'),
    ('BIND_DECLARATION', '    if got != dec:\n', '    if False:\n'),
    ('BIND_UNBOUND', '    if not dec:\n', '    if False:\n'),
    ('BIND_SCRATCH', '    if not under(lane, SCRATCH_PREFIX) or Path(lane).resolve() == Path(SCRATCH_PREFIX).resolve():', '    if False:'),
    ('BIND_SCRATCH_EQUAL', ' or Path(lane).resolve() == Path(SCRATCH_PREFIX).resolve():', ':'),
    ('BIND_UNDER_LANE', 'if not under(p, lane) or Path(p).resolve() == Path(lane).resolve():', 'if Path(p).resolve() == Path(lane).resolve():'),
    ('BIND_PLAIN_NAME', 'if not name or Path(name).name != name or name in (".", ".."):', 'if not name:'),
    ('BIND_OUT_INSIDE', 'if not under(out, lane) or Path(out).resolve() == Path(lane).resolve():', 'if Path(out).resolve() == Path(lane).resolve():'),
    ('BIND_OUT_EQUALS_LANE', 'if not under(out, lane) or Path(out).resolve() == Path(lane).resolve():', 'if not under(out, lane):'),
    ('ALLOC_NODES', 'nodes != str(SLURM_NODES)', 'nodes is None'),
    ('ALLOC_JOB', 'if (not job.isdigit() or not step.isdigit()', 'if (not step.isdigit()'),
    ('MAIN_ALLOCATION', '        alloc = check_allocation()\n', '        alloc = {}\n'),
    ('MAIN_PYTHON_B', '    if not sys.dont_write_bytecode:', '    if False:'),
    ('MAIN_RUNNER_REFUSAL', '        gate_errors = (GateFailure, R.GateFailure, OSError)\n', '\n'),
    ('PIN_TREE', '        if d != pins[rel]:', '        if False:'),
    ('PIN_PYCACHE', '        if (root / rel / "__pycache__").exists():', '        if False:'),
    ('STAGE_DIGEST', '            if got != cfg["inputs"][f"{key}_sha256"]:\n                raise GateFailure(f"the staged {key} has sha256 {got[:12]}, not its pin")\n            os.chmod', '            if False:\n                raise GateFailure(f"the staged {key} has sha256 {got[:12]}, not its pin")\n            os.chmod'),
    ('STAGE_EXISTS', 'stale = [p.name for p in root.iterdir() if p.name == dest.name or p.name.startswith(dest.name + ".partial")]', 'stale = [p.name for p in root.iterdir() if p.name == dest.name]'),
    ('STAGE_CLEANUP', '        finally:\n            part.unlink(missing_ok=True)\n', '        finally:\n            pass\n'),
    ('STAGE_OWN_PARTIAL', '        except FileExistsError:\n', '        except ZeroDivisionError:\n'),
    ('STAGE_UNIQUE', '.partial.{socket.gethostname()}.{os.getpid()}.{secrets.token_hex(8)}', '.partial.{os.getpid()}'),
    ('STAGE_READ_ONLY', '            os.chmod(part, 0o444)\n', '            pass\n'),
    ('STAGED_DIGEST', '            got = held_sha256(fh)\n            if got != cfg', '            got = held_sha256(fh)\n            if False and got != cfg'),
    ('STAGED_HELD_OPEN', '            if identity(fh.fileno()) != before:', '            if False:'),
    ('HELD_READ', 'cols = read_signal_tree(held_path(verified["CV"]))', 'cols = read_signal_tree(staged(cfg)["CV"])'),
    ('BIND_CONFIG_SHA', '    if parsed_sha256 != config_sha256:', '    if False:'),
    ('BIND_REVIEWED', '        if got_v != want_v:', '        if False:'),
    ('BIND_REPO_INSIDE', ',\n                    ("this checkout", REPO)):', '):'),
    ('BIND_STRICT', 'if not under(p, lane) or Path(p).resolve() == Path(lane).resolve():', 'if not under(p, lane):'),
    ('INTERP_PYCACHE', '    if getattr(sys, "pycache_prefix", None):', '    if False:'),
    ('INTERP_PRELOAD', '    if loaded:\n', '    if False:\n'),
    ('CHECKOUT_HEAD', 'if head.returncode != 0 or head.stdout.strip() != cfg["driver_tree"]["commit"]:', 'if head.returncode != 0:'),
    ('CHECKOUT_CLEAN', 'if st.returncode != 0 or st.stdout.strip():', 'if st.returncode != 0:'),
    ('ALLOC_STEP', ' or not step.isdigit() or int(step) >= SLURM_RESERVED_STEPS\n            or nodes', '\n            or nodes'),
    ('ALLOC_STEP_NUMERIC', 'not step.isdigit() or int(step) >= SLURM_RESERVED_STEPS', 'not step or (step.isdigit() and int(step) >= SLURM_RESERVED_STEPS)'),
    ('ALLOC_HOST', ' or not host.startswith(COMPUTE_HOST_PREFIX)):', '):'),
    ('MAIN_CHECKOUT', '        commit = check_checkout(cfg)\n', '        commit = cfg["driver_tree"]["commit"]\n'),
    ('MAIN_INTERPRETER', '        check_interpreter()\n', '\n'),
    ('STAGE_ROOT_RO', '    os.chmod(root, 0o555)\n    return out', '    return out'),
    ('CSTAGE_SAME', 'same = identity(path) == verified[key]["identity"]', 'same = True'),
    ('GIT_ENV', '    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}', '    env = dict(os.environ)'),
    ('GIT_TOPLEVEL', '    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != tree:', '    if top.returncode != 0:'),
    ('PINS_LINK', '        if (root / rel).resolve() != root / rel or not (root / rel).is_file():', '        if False:'),
    ('SAMEBITS_DTYPE', '    if a.shape != b.shape or a.dtype != b.dtype:', '    if a.shape != b.shape:'),
    ('DENOM_META', '        checks["denominator_meta"] = den_meta_back == DENOM_META', '        checks["denominator_meta"] = True'),
    ('MANIFEST_LATE', '    record = {"schema": "evw2d-run/1", "controls_verdict"', '    files.update({n: sha256(out / n) for n in ("constants.json", "xsec.root")})\n    record = {"schema": "evw2d-run/1", "controls_verdict"'),
    ('RUN_SAVED_GRIDS', 'ours = from_file(k["analysis_pt_edges"], k["analysis_pz_edges"])', 'ours = from_file(pt_edges, pz_edges)'),
    ('FILE_SAVED_SELECTOR', 'str(meta_back.get("constants", {}).get("completeness", ""))', 'meta["constants"]["completeness"]'),
    ('RUN_SAVED_SELECTOR', 'den_used = den_back if "event-level" in k["completeness"] else None', 'den_used = den_back'),
    ('CLEANUP_CONFIG', '    if rec.get("config_sha256") != config_sha256:', '    if False:'),
    ('CLEANUP_FILES', ' or same_file_key(identity(path)) != same_file_key(ran.get("identity", {})) or not (\n                got == ran.get("sha256") == pin):', ':'),
    ('CLEANUP_NODEV', 'same_file_key(identity(path)) != same_file_key(ran.get("identity", {}))', 'identity(path) != ran.get("identity", {})'),
    ('LEDGER_NLINK', ' or st.st_nlink != 1:', ':'),
    ('ACCEPT_FALLBACK', '\n          and fallback_matches)', ')'),
    ('REFS_ONE_BUFFER', 'with np.load(io.BytesIO(raw), allow_pickle=False) as z:', 'with np.load(path, allow_pickle=False) as z:'),
    ('XSEC_EARLY', 'files["xsec.root"] = xsec_sha', 'files["xsec.root"] = sha256(out / "xsec.root")'),
    ('ALLOC_RESERVED', ' or int(step) >= SLURM_RESERVED_STEPS', ''),
    ('STAGED_LINK', 'if not under(path, root) or path.is_symlink():', 'if not under(path, root):'),
    ('CLEANUP_SYMLINK', 'got = None if path.is_symlink() else R.sha256_noatime(path)', 'got = R.sha256_noatime(path)'),
    ('CLEANUP_NOFOLLOW', ' | os.O_CREAT | os.O_NOFOLLOW, 0o644)', ' | os.O_CREAT, 0o644)'),
    ('CMAP_REFILL', ' and all(refill.values()) else "stop")', ' else "stop")'),
    ('CMAP_REFILL_NUM', '"numerator": same_bits(num_g, th2_global(h_num, nx, ny))', '"numerator": True'),
    ('CMAP_REFILL_DEN', '"denominator": same_bits(den_g, th2_global(h_den, nx, ny))', '"denominator": True'),
    ('CMAP_REFILL_MAP', '"map": same_bits(', '"map": True or same_bits('),
    ('CSTAGE_RO', 'ro = (os.stat(staging_root(cfg)).st_mode & 0o222) == 0', 'ro = True'),
    ('KEY_EARLY_STOP', 'if not controls["C-KEY"]["pass"]:  # no valid key', 'if False:  # no valid key'),
    ('FILE_CONSTANTS', '"constants_json": constants_back == written,', '"constants_json": True,'),
    ('FILE_DENOM', 'checks["denominator"] = all(', 'checks["denominator"] = True or all('),
    ('TABLE_SWAP', '"truth_pz": d["truth_pz"], "w_prior": d["w_prior"], "w_unfolded": d["w_unfolded"]}', '"truth_pz": d["truth_pz"], "w_prior": d["w_prior"], "w_unfolded": d["w_unfolded"][np.r_[1, 0, 2:d["w_unfolded"].size]]}'),
    ('CMAP_ROUNDING_BAND', '"rounding" if pos.any() and zeros and dev <= CMAP_ROUNDING and', '"rounding" if pos.any() and zeros and dev <= 1e3 * CMAP_ROUNDING and'),
    ('CMAP_SOFT', 'if controls["C-CMAP"]["kind"] == "rounding":', 'if controls["C-CMAP"]["kind"] != "pass":'),
    ('CMAP_EVENT_SKIP', '    if fallback:\n        controls["C-CMAP-EVENT"]', '    if False:\n        controls["C-CMAP-EVENT"]'),
    ('DONE_ATOMIC', 'tmp = out / ".evw2d.done.tmp"', 'tmp = out / "evw2d.done"'),
    ('ACCEPT_PRESENT', '"present": present == expected | {"SHA256SUMS"} | set(beside),', '"present": True,'),
    ('ACCEPT_MANIFEST', '"manifest": listed == files,', '"manifest": True,'),
    ('ACCEPTED_DONE', 'ok = (done.get("verdict") == "PASS" and', 'ok = (True and'),
    ('CLEANUP_ACCEPTED', '    if not acc["pass"]:\n        raise GateFailure(f"{out} is not an accepted product', '    if False:\n        raise GateFailure(f"{out} is not an accepted product'),
    ('CFLUX_FINITE_ULP', '"pass": bool(np.isfinite(ulp) and ', '"pass": bool('),
    ('REF_KEYS', 'if sorted(refs) != sorted([*want, "er", "paper", "meta"]):', 'if False:'),
    ('REF_VECTOR_DTYPE', 'if refs[k].dtype != np.float64 or refs[k].shape', 'if refs[k].shape'),
    ('PINS_CACHE_AFTER', ' and not caches}', '}'),
]


def apply(src: str, old: str, new: str) -> str:
    n = src.count(old)
    if n != 1:
        raise SystemExit(f"a mutant's span occurs {n} times, not once: {old[:60]!r}")
    return src.replace(old, new)


SPARSE = ("/2d-unfolding/re2/", "/2d-unfolding/ref_c2c1/", "/unbinned_unfolding/python/")
GIT_ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0")


def tree_dirt(tree) -> list[str]:
    """Anything in a driver tree that is not its committed content (a bytecode cache, a stray file)."""
    p = subprocess.run(["git", "-C", str(tree), "status", "--porcelain", "--ignored"], capture_output=True,
                       text=True, env=GIT_ENV, check=True)
    return p.stdout.splitlines()


def make_trees(n: int, commit: str, base: Path) -> list[Path]:
    """One sparse git worktree of the driver tree per worker, at the pinned commit: no case can taint another's."""
    trees = []
    for i in range(n):
        t = base / f"w{i}"
        subprocess.run(["git", "-C", str(HERE), "worktree", "add", "-q", "--no-checkout", "--detach", str(t), commit],
                       check=True, env=GIT_ENV)
        subprocess.run(["git", "-C", str(t), "sparse-checkout", "set", "--no-cone", *SPARSE], check=True, env=GIT_ENV)
        subprocess.run(["git", "-C", str(t), "checkout", "-q"], check=True, env=GIT_ENV)
        head = subprocess.run(["git", "-C", str(t), "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
        if head != commit or tree_dirt(t):
            raise SystemExit(f"worker tree {t} is not a clean checkout of {commit}")
        trees.append(t)
    return trees


def remove_trees(trees) -> None:
    for t in trees:
        subprocess.run(["git", "-C", str(HERE), "worktree", "remove", "--force", str(t)], env=GIT_ENV)


ENVIRONMENT_ERRORS = ("ModuleNotFoundError", "ImportError", "SyntaxError", "IndentationError")


def run_one(name, old, new, python, timeout, tree):
    # beside this checkout, like the worker trees: C-BIND requires the module's own checkout inside the tests' lane root
    td = Path(tempfile.mkdtemp(prefix=f"evw2d_mut_{name}_", dir=os.environ.get("EVW2D_TREES_DIR", str(HERE.parents[2]))))
    d = td / "2d-unfolding" / "evw2d"
    d.mkdir(parents=True)
    for f in ("config.json", "references.npz"):
        shutil.copy(HERE / f, d / f)
    dec = json.loads((HERE / "config.json").read_text())["declaration"]  # C-BIND reads it under the copy's REPO
    (td / dec).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(HERE.parents[1] / dec, td / dec)
    src = SRC.read_text()
    (d / "evw2d.py").write_text(apply(src, old, new) if old is not None else src)
    env = dict(os.environ, EVW2D_MUTANT=str(d / "evw2d.py"), PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="2",
               EVW2D_DRIVER_TREE=str(tree))
    t0 = time.time()
    try:
        p = subprocess.run([python, "-B", "-m", "pytest", "-x", "-q", "-rfE", "-p", "no:cacheprovider", str(TESTS)],
                           env=env, capture_output=True, text=True, timeout=timeout, cwd=td)
        lines = (p.stdout + p.stderr).splitlines()
        rc = p.returncode
        failed = [x.split(" ", 1)[0] + " " + x.split(" - ")[0].split("::", 1)[-1]
                  for x in lines if x.startswith(("FAILED ", "ERROR "))]
        reason = next((x.strip() for x in lines if x.startswith("E   ")), "")
        tail = lines[-2:]
    except subprocess.TimeoutExpired:
        rc, failed, reason, tail = "timeout", [], "", []
    mutant_sha = hashlib.sha256((d / "evw2d.py").read_bytes()).hexdigest()
    dirt = tree_dirt(tree)
    shutil.rmtree(td, ignore_errors=True)
    kind = ("environment" if any(x in reason for x in ENVIRONMENT_ERRORS) else
            "failed" if any(t.startswith("FAILED") for t in failed) else "error" if failed else "none")
    return {"name": name, "rc": rc, "killed": rc == 1 and bool(failed) and kind != "environment", "kind": kind,
            "failed_tests": failed,
            "first_error_line": reason[:300], "mutant_sha256": mutant_sha, "tree_dirt_after": dirt,
            "seconds": round(time.time() - t0, 1),
            "tail": tail}


def main(argv):
    python, out = argv[0], Path(argv[1])
    workers = int(argv[2]) if len(argv) > 2 else 4
    src = SRC.read_text()
    for name, old, new in MUTANTS:
        apply(src, old, new)
    if len({m[0] for m in MUTANTS}) != len(MUTANTS):
        raise SystemExit("mutant names repeat")
    only = set(filter(None, os.environ.get("EVW2D_ONLY", "").split(",")))  # a quick subset; the receipt runs all
    chosen = [m for m in MUTANTS if not only or m[0] in only]
    commit = json.loads((HERE / "config.json").read_text())["driver_tree"]["commit"]
    base = Path(tempfile.mkdtemp(prefix="evw2d-trees-", dir=os.environ.get("EVW2D_TREES_DIR", str(HERE.parents[2]))))
    trees = make_trees(workers, commit, base)
    try:
        return campaign(chosen, python, out, workers, trees)
    finally:
        remove_trees(trees)
        shutil.rmtree(base, ignore_errors=True)


def campaign(chosen, python, out, workers, trees):
    pool = queue.Queue()
    for t in trees:
        pool.put(t)

    def with_tree(n, o, w):
        t = pool.get()
        try:
            return run_one(n, o, w, python, 3600, t)
        finally:
            pool.put(t)
    control = with_tree("CONTROL", None, None)
    if control["rc"] != 0:  # a failing control makes every kill meaningless: stop before the mutants
        out.write_text(json.dumps({"control": control, "control_pass": False}, indent=1) + "\n")
        print(json.dumps({"control_pass": False, "control": control}))
        return 1
    results = []
    with cf.ThreadPoolExecutor(workers) as ex:
        futs = [ex.submit(with_tree, n, o, w) for n, o, w in chosen]
        for f in cf.as_completed(futs):
            r = f.result()
            print(json.dumps(r), flush=True)
            results.append(r)
    results.sort(key=lambda r: r["name"])
    killed = [r["name"] for r in results if r["killed"]]
    record = {"evw2d_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
              "tests_sha256": hashlib.sha256(TESTS.read_bytes()).hexdigest(),
              "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "declaration_sha256": hashlib.sha256((HERE.parents[1] / json.loads((HERE / "config.json").read_text())
                                                    ["declaration"]).read_bytes()).hexdigest(),
              "driver_tree_commit": json.loads((HERE / "config.json").read_text())["driver_tree"]["commit"],
              "control": control, "control_pass": control["rc"] == 0,
              "mutants": len(MUTANTS), "run": len(chosen), "killed": len(killed),
              "not_killed": [r for r in results if not r["killed"]],
              "tree_clean": not any(tree_dirt(t) for t in trees) and not any(r["tree_dirt_after"]
                                                                              for r in [control, *results]),
              "kinds": {k: sum(1 for r in results if r["kind"] == k) for k in ("failed", "error", "environment", "none")},
              "results": results}
    out.write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps({k: record[k] for k in ("control_pass", "tree_clean", "mutants", "run", "killed")}))
    return 0 if (record["control_pass"] and record["tree_clean"]
                 and len(killed) == len(MUTANTS) == len(chosen)) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
