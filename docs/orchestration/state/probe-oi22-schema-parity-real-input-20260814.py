"""OI-22 leg (a1): sha256 bind + schema parity, ON THE REAL PUBLICATION INPUT.

Memory-bounded BY CONSTRUCTION: reads each member's .npy HEADER only, plus the
0-dimensional marker scalars. The 29.03 GB of array payload is never materialised.

REUSES the production contract rather than restating it -- REQUIRED_KEYS and
assert_g2_schema are imported from fullevent_dump_contract, whose sha256 is recorded
in the receipt alongside the NPZ's.

POSITIVE CONTROLS, predeclared before the run. Each check is re-run against a
DELIBERATELY BROKEN COPY of the observed metadata; the file is never touched. A check
that cannot be made to fail is not evidence (BEN-173/BEN-185), and a green schema
report with no demonstrated failing direction is exactly what this leg exists to avoid.

  C1 marker control     petSchemaVersion -> 'g2-fullevent-v0'   assert_g2_schema MUST raise
  C2 marker control     hasFullEventSchema -> 0                  assert_g2_schema MUST raise
  C3 required-key       drop one REQUIRED_KEY from observed      subset check MUST fail
  C4 row-count control  perturb one signal-block row count       consistency MUST fail
"""
import hashlib
import json
import os
import sys
import zipfile

import numpy as np

REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
NPZ = os.path.join(REPO, "nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz")
sys.path.insert(0, os.path.join(REPO, "nd-unfolding/pet"))
import fullevent_dump_contract as C  # noqa: E402


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def headers(path):
    """(name -> {dtype, shape}) from .npy headers only. No payload is read."""
    out = {}
    z = zipfile.ZipFile(path)
    for n in z.namelist():
        with z.open(n) as f:
            ver = np.lib.format.read_magic(f)
            shape, _fortran, dtype = np.lib.format._read_array_header(f, ver)
        out[n[:-4] if n.endswith(".npy") else n] = {"dtype": str(dtype), "shape": list(shape)}
    return out


def markers(path):
    """Load ONLY the 0-dim scalar markers assert_g2_schema needs. Bytes: negligible."""
    z = np.load(path, allow_pickle=False)
    m = {}
    for k in ("petSchemaVersion", "hasFullEventSchema", "fullPhaseSpace",
              "estimator_fingerprint", "sig_identity_hash", "data_identity_hash"):
        if k in z.files:
            v = z[k]
            m[k] = v.item() if v.shape == () else v.tolist()
    z.close()
    return m


def missing_required(obs_keys):
    return sorted(set(C.REQUIRED_KEYS) - set(obs_keys))


def rowcounts(hdr, keys):
    return {k: hdr[k]["shape"][0] for k in keys if k in hdr and hdr[k]["shape"]}


def consistent(counts):
    return len(set(counts.values())) <= 1


def control(label, expectation, fn):
    """Run a deliberately-broken variant. `fn` returns True if the check REJECTED it."""
    fired = False
    detail = ""
    try:
        fired = bool(fn())
    except Exception as exc:                       # a raise IS the rejection for C1/C2
        fired, detail = True, f"{type(exc).__name__}: {str(exc)[:110]}"
    ok = fired is True
    print(f"  [{label}] expected={expectation}  fired={fired}  "
          f"{'as predeclared' if ok else '*** DID NOT FIRE ***'}")
    if detail:
        print(f"      {detail}")
    return ok, detail


print("=== OI-22 leg (a1): schema parity on the real publication input ===\n")

st = os.stat(NPZ)
print(f"object   : {NPZ}")
print(f"size     : {st.st_size} bytes")
print("hashing 9.9 GB, one streaming pass ...")
digest = sha256_file(NPZ)
print(f"sha256   : {digest}")

hdr = headers(NPZ)
mk = markers(NPZ)
obs = sorted(hdr)
print(f"members  : {len(obs)}")

# ---- the three parity statements -------------------------------------------------
miss = missing_required(obs)
schema_ok = C.assert_g2_schema(mk)

SIG = [k for k in ("part_reco", "part_gen", "reco_scalars", "reco_muon", "reco_vertex",
                   "reco_view", "reco_time", "truth_scalars", "pass_reco", "pass_truth",
                   "w_truth", "w_reco") if k in hdr]
DAT = [k for k in ("measured_pc", "measured_scalars", "data_muon", "data_vertex",
                   "data_view", "data_time") if k in hdr]
BKG = [k for k in ("bkg_part_reco", "bkg_reco_scalars", "bkg_muon", "bkg_vertex",
                   "bkg_view", "bkg_time", "w_bkg") if k in hdr]
cs, cd, cb = rowcounts(hdr, SIG), rowcounts(hdr, DAT), rowcounts(hdr, BKG)

print("\n-- results --")
print(f"  markers            : {mk.get('petSchemaVersion')} / "
      f"hasFullEventSchema={mk.get('hasFullEventSchema')} / "
      f"fullPhaseSpace={mk.get('fullPhaseSpace')}  -> assert_g2_schema PASS={schema_ok}")
print(f"  REQUIRED_KEYS      : {len(C.REQUIRED_KEYS)} required, missing={miss or 'none'}")
print(f"  signal row counts  : {sorted(set(cs.values()))}  consistent={consistent(cs)}  "
      f"({len(cs)} blocks)")
print(f"  data   row counts  : {sorted(set(cd.values()))}  consistent={consistent(cd)}  "
      f"({len(cd)} blocks)")
print(f"  bkg    row counts  : {sorted(set(cb.values()))}  consistent={consistent(cb)}  "
      f"({len(cb)} blocks)")

print("\n-- positive controls (broken COPIES of the metadata; the file is untouched) --")
ctl = {}
bad1 = dict(mk); bad1["petSchemaVersion"] = "g2-fullevent-v0"
ctl["C1"] = control("C1 petSchemaVersion wrong", "raise", lambda: C.assert_g2_schema(bad1))
bad2 = dict(mk); bad2["hasFullEventSchema"] = 0
ctl["C2"] = control("C2 hasFullEventSchema=0 ", "raise", lambda: C.assert_g2_schema(bad2))
dropped = C.REQUIRED_KEYS[0]
ctl["C3"] = control(f"C3 drop '{dropped}'      ", "detect",
                    lambda: bool(missing_required([k for k in obs if k != dropped])))
badc = dict(cs); badc[SIG[0]] = cs[SIG[0]] + 1
ctl["C4"] = control("C4 row count perturbed  ", "detect", lambda: not consistent(badc))

controls_ok = all(v[0] for v in ctl.values())
parity_ok = (not miss) and schema_ok and consistent(cs) and consistent(cd) and consistent(cb)
digest_ok = digest == "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"

receipt = {
    "what": "OI-22 leg (a1): sha256 bind + schema parity on the REAL publication input",
    "produced_by": "Lane D (verifier), read-only; nothing written into any pinned tree",
    "object": {"path": NPZ, "size_bytes": st.st_size, "sha256_measured": digest,
               "sha256_receipt_g2_gate1b": "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba7"
                                           "71c8f2a29625",
               "sha256_matches_receipt": digest_ok},
    "code_bound": {"repo": REPO, "head": None,
                   "fullevent_dump_contract.py.sha256": sha256_file(
                       os.path.join(REPO, "nd-unfolding/pet/fullevent_dump_contract.py"))},
    "members": {"count": len(obs), "headers": hdr},
    "parity": {"markers": mk, "assert_g2_schema": bool(schema_ok),
               "required_keys_total": len(C.REQUIRED_KEYS), "required_keys_missing": miss,
               "row_counts": {"signal": cs, "data": cd, "background": cb},
               "row_counts_consistent": {"signal": consistent(cs), "data": consistent(cd),
                                         "background": consistent(cb)}},
    "positive_controls": {k: {"fired": v[0], "detail": v[1]} for k, v in ctl.items()},
    "verdict": {"schema_parity_on_real_input": "PROVED" if (parity_ok and controls_ok
                                                            and digest_ok) else "NOT PROVED",
                "all_controls_fired": controls_ok, "digest_binds": digest_ok},
    "scope_limits": [
        "Row-count consistency is NECESSARY, NOT SUFFICIENT for event-by-event alignment -- "
        "build_bkgsub_pointcloud_input.py states the principle: equal counts alone are NOT proof.",
        "This closes SCHEMA PARITY only. Order and alignment are untouched here.",
        "No-truth-leakage is NOT closed by this run -- see the re-scope in the report.",
    ],
}
print("\n=== VERDICT: schema parity on real input = "
      f"{receipt['verdict']['schema_parity_on_real_input']} "
      f"(controls {sum(v[0] for v in ctl.values())}/4, digest_binds={digest_ok}) ===")
print("\n<<<RECEIPT_JSON>>>")
print(json.dumps(receipt, indent=1, sort_keys=True))
