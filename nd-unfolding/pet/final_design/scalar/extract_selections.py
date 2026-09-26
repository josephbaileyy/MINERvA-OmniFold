"""Extract compact per-selection scalar arrays for the scalar/AUSSIE matched comparison (cluster).

For each predecessor selection -- pool T replicates 0 and 1 (the PET STRESS runs) and pool F
replicates 0 and 1 (the PET FINAL runs) of family `confirm-historical-size-v1` -- this reads the
C-arm run directories' `replicate_arrays.npz` (prior/pseudodata rows, pass flags, truth scalars,
reco E_avail, weights, regions, per-case distortion and oracle weights), then gathers at exactly
those inventory rows:

* from the inventory: `reco_scalars` (reco p_T, p_par, E_avail, q3), `truth_scalars`, `w_truth`,
  `w_reco`, `pass_reco`, `pass_truth` -- signal-MC members only, by an explicit allow-list;
  `data_*`, `measured_*` and `bkg_*` members are refused by name before any byte is read;
* from `row_features.npz`: the stored-cluster count and energy sum (`rc_n_valid`, `rc_E_sum`) and the
  truncated-cloud species counts (`tr_n_p`, `tr_n_n`, `tr_n_pipm`, `tr_n_pi0`, `tr_n_other`).

Every gathered column that `replicate_arrays.npz` also carries is cross-checked (exact, NaN-aware);
for R1 cases the run's pseudodata reco E_avail must equal the inventory value times the float32
factor on reco-passing rows and the inventory value elsewhere. The rows must be identical across
every case directory of a selection. A difference is a refusal.

Standalone on purpose (numpy + zipfile only), so it runs from a copied, blob-identified file on a
compute node without a checkout. Simulation only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import zipfile
from pathlib import Path

import numpy as np

SCHEMA = "pfd-scalar/selection-extract/1"
INVENTORY_MEMBERS = ("reco_scalars", "truth_scalars", "w_truth", "w_reco", "pass_reco",
                     "pass_truth")
REFUSED_PREFIXES = ("data_", "measured_", "bkg_")
ROW_FEATURES = ("rc_n_valid", "rc_E_sum", "tr_n_p", "tr_n_n", "tr_n_pipm", "tr_n_pi0",
                "tr_n_other", "pass_reco", "pass_truth")
CONFIRM = "/pscratch/sd/j/josephrb/pet-improvement-20260922/confirm"
STRESS_CASES = ("D1_m0.350", "D2_bump_c0.3", "D4c_p_up", "D4d_n_up", "D5_nuwro",
                "R1_x1.05_D1_p0.350")
R1_FACTOR = {"R1_x1.05_D1_p0.350": 1.05}
CHUNK_ROWS = 2_000_000


def selection_dirs(confirm: Path, selection: str) -> dict[str, Path]:
    """case name -> C-arm run directory, for one selection (T0, T1, F0, F1)."""
    if selection[0] == "T":
        return {c: confirm / "stress" / f"stress-C-{selection}-{c}" for c in STRESS_CASES}
    if selection[0] == "F":
        return {"dev": confirm / "final" / f"final-C-{selection}"}
    raise SystemExit(f"unknown selection {selection!r}")


def git_blob_sha1(path: Path) -> str:
    data = Path(path).read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def sha256_file(path: Path, chunk: int = 1 << 24) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def _check_member(name: str) -> None:
    if name.startswith(REFUSED_PREFIXES) or name not in INVENTORY_MEMBERS:
        raise PermissionError(f"inventory member {name!r} is not an allowed simulation member")


def gather_member(zf: zipfile.ZipFile, name: str, rows: np.ndarray) -> np.ndarray:
    """The member's values at the sorted unique ``rows``, streamed chunk by chunk."""
    _check_member(name)
    fh = zf.open(name + ".npy")
    version = np.lib.format.read_magic(fh)
    shape, fortran, dtype = np.lib.format._read_array_header(fh, version)
    if fortran:
        raise ValueError(f"{name}: Fortran order")
    row_items = int(np.prod(shape[1:])) if len(shape) > 1 else 1
    row_bytes = row_items * dtype.itemsize
    out = np.empty((rows.size,) + tuple(shape[1:]), dtype=dtype)
    done = 0
    while done < shape[0]:
        n = min(CHUNK_ROWS, shape[0] - done)
        buf = fh.read(n * row_bytes)
        if len(buf) != n * row_bytes:
            raise IOError(f"{name}: short read at row {done}")
        lo, hi = np.searchsorted(rows, [done, done + n])
        if hi > lo:
            chunk = np.frombuffer(buf, dtype=dtype).reshape((n,) + tuple(shape[1:]))
            out[lo:hi] = chunk[rows[lo:hi] - done]
        done += n
    return out


def same(a: np.ndarray, b: np.ndarray) -> bool:
    a, b = np.asarray(a), np.asarray(b)
    if a.shape != b.shape:
        return False
    if a.dtype.kind == "f" or b.dtype.kind == "f":
        a64, b64 = a.astype(np.float64), b.astype(np.float64)
        return bool(np.array_equal(a64, b64, equal_nan=True))
    return bool(np.array_equal(a, b))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inventory", type=Path, required=True)
    ap.add_argument("--expect-inventory-sha256", default=None)
    ap.add_argument("--row-features", type=Path, required=True)
    ap.add_argument("--confirm", type=Path, default=Path(CONFIRM))
    ap.add_argument("--selections", nargs="+", default=["T0", "T1", "F0", "F1"])
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    t0 = time.time()
    if not str(a.out.resolve()).startswith("/pscratch/sd/j/josephrb/pet-final-design-20260925/"
                                           "impl-scalar"):
        raise SystemExit("output must be under the impl-scalar namespace")
    a.out.mkdir(parents=True, exist_ok=True)
    receipt: dict = {"schema": SCHEMA, "script": str(Path(__file__).resolve()),
                     "script_blob_sha1": git_blob_sha1(Path(__file__)),
                     "inventory": str(a.inventory), "row_features": str(a.row_features),
                     "inventory_members_read": list(INVENTORY_MEMBERS),
                     "row_feature_columns_read": list(ROW_FEATURES), "selections": {}}
    if a.expect_inventory_sha256:
        got = sha256_file(a.inventory)
        if got != a.expect_inventory_sha256:
            raise SystemExit(f"inventory sha256 {got} != {a.expect_inventory_sha256}")
        receipt["inventory_sha256"] = got

    # ---- per-selection run arrays (rows, flags, cases) ----------------------------------- #
    sel_arrays: dict[str, dict] = {}
    for s in a.selections:
        dirs = selection_dirs(a.confirm, s)
        base = None
        cases, digests = {}, {}
        for case, d in dirs.items():
            f = d / "replicate_arrays.npz"
            digests[case] = {"path": str(f), "sha256": sha256_file(f)}
            with np.load(f) as z:
                arr = {k: np.asarray(z[k]) for k in z.files}
            ident = json.loads((d / "run_identity.json").read_text()) \
                if (d / "run_identity.json").exists() else {}
            digests[case]["distortion"] = ident.get("distortion")
            if base is None:
                base = arr
            else:
                for k in arr:
                    if k in ("pseudo_distortion", "prior_oracle", "pseudo_reco_eavail"):
                        continue
                    if not same(arr[k], base[k]):
                        raise SystemExit(f"{s}: {case} differs from the first case on {k}")
            cases[case] = {"pseudo_distortion": arr["pseudo_distortion"],
                           "prior_oracle": arr["prior_oracle"],
                           "pseudo_reco_eavail": arr["pseudo_reco_eavail"]}
        sel_arrays[s] = {"base": base, "cases": cases, "digests": digests}
        print(f"[{s}] {len(cases)} case dirs read, {time.time() - t0:.0f}s", flush=True)

    all_rows = np.unique(np.concatenate(
        [np.concatenate([v["base"]["prior_rows"], v["base"]["pseudo_rows"]])
         for v in sel_arrays.values()]).astype(np.int64))

    # ---- inventory and row features at those rows ------------------------------------------ #
    inv: dict[str, np.ndarray] = {}
    with zipfile.ZipFile(a.inventory) as zf:
        for name in INVENTORY_MEMBERS:
            inv[name] = gather_member(zf, name, all_rows)
            print(f"[inventory] {name} {inv[name].shape}, {time.time() - t0:.0f}s", flush=True)
    rf: dict[str, np.ndarray] = {}
    with np.load(a.row_features) as z:
        for name in ROW_FEATURES:
            rf[name] = np.asarray(z[name])[all_rows]
    for flag in ("pass_reco", "pass_truth"):
        if not np.array_equal(rf[flag].astype(bool), inv[flag].astype(bool)):
            raise SystemExit(f"row_features {flag} disagrees with the inventory")

    # ---- per selection: cross-check and write --------------------------------------------- #
    for s, v in sel_arrays.items():
        b = v["base"]
        out: dict[str, np.ndarray] = {}
        checks: dict[str, bool] = {}
        weight_ratio: dict[str, dict[str, float]] = {}
        for side in ("prior", "pseudo"):
            rows = b[f"{side}_rows"].astype(np.int64)
            pos = np.searchsorted(all_rows, rows)
            g = {k: val[pos] for k, val in inv.items()}
            h = {k: val[pos] for k, val in rf.items()}
            checks[f"{side}_truth"] = same(g["truth_scalars"][:, [0, 1, 2, 3]], b[f"{side}_truth"])
            for w in ("w_truth", "w_reco"):
                # replicate_arrays carries the weights AFTER the engine DataLoader normalized them
                # in place (one constant per run); require a constant ratio to the inventory
                ratio = b[f"{side}_{w}"] / g[w].astype(np.float64)
                spread = float(np.abs(ratio / ratio[0] - 1.0).max())
                weight_ratio[f"{side}_{w}"] = {"ratio": float(ratio[0]), "max_rel_spread": spread}
                checks[f"{side}_{w}_constant_ratio"] = bool(np.isfinite(ratio).all()
                                                            and spread < 1e-6)
            checks[f"{side}_pass_reco"] = same(g["pass_reco"].astype(bool), b[f"{side}_pass_reco"])
            checks[f"{side}_pass_truth"] = same(g["pass_truth"].astype(bool),
                                                b[f"{side}_pass_truth"])
            out[f"{side}_rows"] = rows
            out[f"{side}_reco_scalars"] = g["reco_scalars"].astype(np.float32)
            out[f"{side}_truth_scalars"] = g["truth_scalars"].astype(np.float32)
            # the weights the predecessor's PET scorer used (bit-identical pairing)
            out[f"{side}_w_truth"] = b[f"{side}_w_truth"].astype(np.float64)
            out[f"{side}_w_reco"] = b[f"{side}_w_reco"].astype(np.float64)
            out[f"{side}_pass_reco"] = g["pass_reco"].astype(bool)
            out[f"{side}_pass_truth"] = g["pass_truth"].astype(bool)
            out[f"{side}_region"] = b[f"{side}_region"].astype(np.int8)
            for k in ROW_FEATURES[:7]:
                out[f"{side}_{k}"] = h[k]
        # reco E_avail: prior always, pseudodata per case (R1 scales it)
        pos_p = np.searchsorted(all_rows, b["prior_rows"])
        checks["prior_reco_eavail"] = same(inv["reco_scalars"][pos_p, 2], b["prior_reco_eavail"])
        pr_ps = out["pseudo_pass_reco"]
        inv_eav = out["pseudo_reco_scalars"][:, 2]
        for case, c in v["cases"].items():
            factor = R1_FACTOR.get(case)
            if factor is None:
                expect = inv_eav
            else:
                expect = inv_eav.copy()
                expect[pr_ps] = expect[pr_ps] * np.float32(factor)
            checks[f"case_{case}_pseudo_reco_eavail"] = same(expect, c["pseudo_reco_eavail"])
            out[f"case__{case}__pseudo_distortion"] = c["pseudo_distortion"].astype(np.float64)
            out[f"case__{case}__prior_oracle"] = c["prior_oracle"].astype(np.float64)
        bad = [k for k, ok in checks.items() if not ok]
        if bad:
            raise SystemExit(f"[{s}] cross-checks failed: {bad}")
        path = a.out / f"selection_{s}.npz"
        np.savez_compressed(path, **out)
        receipt["selections"][s] = {
            "output": str(path), "output_sha256": sha256_file(path),
            "cases": sorted(v["cases"]), "r1_factors": {k: R1_FACTOR[k] for k in v["cases"]
                                                        if k in R1_FACTOR},
            "replicate_arrays": v["digests"], "cross_checks": checks,
            "weights_source": "replicate_arrays.npz (engine-normalized in place); ratio to "
                              "the inventory weights recorded",
            "weight_ratio_to_inventory": weight_ratio,
            "n_prior": int(out["prior_rows"].size), "n_pseudo": int(out["pseudo_rows"].size)}
        print(f"[{s}] wrote {path}, {time.time() - t0:.0f}s", flush=True)
    receipt["seconds"] = round(time.time() - t0, 1)
    (a.out / "extract_receipt.json").write_text(json.dumps(receipt, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
