"""PET final-design study: driver inputs for a replicate or BANK draw, built as the predecessor builds them.

PROVENANCE. A copy of `nd-unfolding/pet/improvement_campaign/confirm/replicate_inputs.py` (git blob
`32fcc47c5963cfabc0eac107acbd0e0278a08f27`, study branch commit `e5a1e004`), modified minimally for
PROTOCOL-20260925. Every modification is marked `[pfd]`; everything unmarked is the predecessor's
code, unchanged (a test compares those functions' source with the predecessor's module):

* paths: the module lives in `final_design/runner/`; `CAMPAIGN` still names the predecessor's
  campaign directory (its protocol, records and Phase E modules);
* `refuse_pool`: pool R is always refused, and a predecessor pool selection is limited to the
  replicates the predecessor already drew (`DRAWN`), so it cannot touch a bank-FB/RB row;
* `refuse_bank` / `bank_selection` (protocol section 3): pseudodata = a uniformly random subset,
  without replacement, of the pseudodata bank (DEV, FB or RB); prior = a random subset of DEV
  disjoint from the pseudodata; both by identity hashes salted with
  `pet-final-design-20260925/<stage>/<replicate>/{pseudo|prior}`. FB and RB are refused unless the
  study protocol carries an `### Amendment ... FB release` / `... RB release` heading;
* the `null` distortion (no truth distortion; target = the undistorted pseudodata truth);
* bootstrap members (protocol section 9): Poisson(1) event weights keyed by (seed, member, side,
  event identity), and per-member estimator seeds.

The original module docstring follows.

---

PET driver inputs for a replicate draw from an event pool, built as `closure_data.py` builds them.

A confirmatory run (PROTOCOL-20260922 section 5) unfolds a fresh PRIOR sample and a fresh, distorted
PSEUDODATA sample drawn from a pool (section 3), not the historical halves. This module does three
things and nothing else:

1. **Selects the rows.** `replicate_selection` draws (pool, replicate) with `phase_e/replicates.py`
   (identity-hashed, prior and pseudodata disjoint within a replicate, replicates of one family
   disjoint event draws). `historical_selection` replays the historical halves with the historical
   functions, for the positive control. Pools P (PILOT) and F (FINAL) are refused unless the
   protocol in the checkout carries its Amendment 2 (the candidate freeze).
2. **Loads those rows exactly as the historical loader does.** `load_signal_rows` is the mc-only
   branch of `fullevent_fps_dataloader.build_fullevent_loaders` with its subsample `imc` replaced by
   the given rows: the same helper functions, in the same order, on the same members, and the same
   `DataLoader` normalization. It differs in one respect, on purpose: the historical loader also
   reads the real-data members `measured_scalars` / `data_muon` / `data_vertex` to build a data
   event block that the mc-only closure then discards. Here the inventory is opened through
   `authorization_scope.SignalOnlyNpz`, which refuses every real-data member, and the discarded
   block is built from a stand-in (the MC rows' own reco blocks). The step-1 and step-2 arrays do
   not depend on that block (`build_event_features` forms its normalization from the MC reco rows
   only), which the positive control checks byte for byte.
3. **Assembles the closure** exactly as `closure_data.build_closure_inputs` does (its lines for the
   ours arm): pseudodata = the pseudodata rows passing reco and truth, weighted `w_reco x d`; prior =
   every prior row with both weight legs and both pass flags. `d` is the distortion weight,
   normalized to unit mean over the pseudodata's truth-passing rows. The development distortion
   (`dev`) is the HISTORICAL tilt with its standardization frozen at the historical constants, read
   from the historical record; every other distortion is a truth-weight distortion of
   `phase_e/distortions.py`, by id.

Only signal-MC simulation is read. PET is diagnostic method development.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent                                   # [pfd] final_design/
CAMPAIGN = STUDY.parent / "improvement_campaign"      # [pfd] the predecessor's campaign
PHASE_E = CAMPAIGN / "phase_e"
for _p in (CAMPAIGN, PHASE_E):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import authorization_scope as scope  # noqa: E402
import distortions as dist  # noqa: E402
import replicates as rp  # noqa: E402

SCHEMA = "pet-final-design-inputs/1"                  # [pfd]
PROTOCOL = CAMPAIGN / "PROTOCOL-20260922.md"
POPULATIONS_JSON = CAMPAIGN / "phase_b" / "scalar" / "results" / "populations.json"
DEV = "dev"
FAMILY = "confirm-historical-size-v1"
# PROTOCOL section 5.3 (fresh prior 600,130 rows, fresh pseudodata 600,111 rows). NOTE: the
# executed historical closure used the opposite assignment -- its pseudodata (half A) held 600,130
# truth-passing rows and its prior (half B) 600,111 (`populations.json` census); both halves had
# 600,143 rows. The protocol's sizes are kept; the 19-event difference is recorded, not hidden.
N_PRIOR, N_PSEUDO = 600_130, 600_111
SEALED_POOLS = ("P", "F")
AMENDMENT_2 = re.compile(r"^#{2,4} Amendment 2\b", re.MULTILINE)
# [pfd] PROTOCOL-20260925 section 3: banks, access rules and draw salts.
STUDY_PROTOCOL = STUDY / "PROTOCOL-20260925.md"
BANK_MANIFEST = STUDY / "banks" / "BANK_MANIFEST.json"
STUDY_SALT = "pet-final-design-20260925"
BANK_CODES = {"DEV": 0, "FB": 1, "RB": 2}
BANK_RELEASE = {"FB": re.compile(r"^### Amendment .* FB release", re.MULTILINE),
                "RB": re.compile(r"^### Amendment .* RB release", re.MULTILINE)}
REFUSED_POOLS = ("R",)                                # the reserve bank RB, never via --pool
# The predecessor's scored draws of FAMILY (historical sizes): the only pool selections allowed.
DRAWN = {"P": range(3), "F": range(12), "S": range(1), "T": range(2)}
NULL = "null"
SIGNAL_MEMBERS = ("edges_0", "edges_1", "petSchemaVersion", "pass_reco", "pass_truth",
                  "part_reco", "reco_view", "reco_time", "part_gen", "reco_scalars",
                  "truth_scalars", "reco_muon", "reco_vertex", "w_truth", "w_reco",
                  "sig_identity_hash")


def sha256_bytes(a: Any) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def sha256_file(path: Path | str) -> str:
    return rp.sha256_file(path)


# ------------------------------------------------------------------------------------------- #
# Guards
# ------------------------------------------------------------------------------------------- #
def refuse_sealed_pool(pool: str, protocol: Path = PROTOCOL) -> dict[str, Any]:
    """Pools P and F are PILOT and FINAL: no row of them is read before the candidate freeze
    (protocol section 5.1), which the orchestrator records as Amendment 2 of the protocol. The
    check reads the protocol file of THIS checkout, so a pinned compute checkout without the
    amendment cannot open P or F."""
    if pool not in rp.POOL_CODES:
        raise SystemExit(f"[confirm] unknown pool {pool!r}")
    if pool not in SEALED_POOLS:
        return {"pool": pool, "sealed": False}
    text = Path(protocol).read_text()
    if not AMENDMENT_2.search(text):
        raise scope.ScopeViolation(
            f"pool {pool} is sealed (PILOT/FINAL) until the candidate freeze; {protocol} carries "
            "no 'Amendment 2' heading")
    return {"pool": pool, "sealed": True, "protocol": str(protocol),
            "protocol_sha256": sha256_file(protocol), "amendment_2_present": True}


def refuse_pool(pool: str, replicate: int, family: str = FAMILY, n_prior: int = N_PRIOR,
                n_pseudo: int = N_PSEUDO, protocol: Path = PROTOCOL) -> dict[str, Any]:
    """[pfd] A predecessor pool selection is allowed only for a draw the predecessor already
    made and scored (family FAMILY at the historical sizes, replicates `DRAWN`): any other draw
    could read a never-drawn row (bank FB). Pool R (bank RB) is always refused. Then the
    predecessor's own sealed-pool guard (P/F need its Amendment 2, which it carries)."""
    if pool in REFUSED_POOLS:
        raise scope.ScopeViolation(f"pool {pool} is the study's reserve bank RB; it is never "
                                   "opened through --pool (use --bank-draw ... --pseudo-bank RB "
                                   "after an RB-release amendment)")
    if (family, int(n_prior), int(n_pseudo)) != (FAMILY, N_PRIOR, N_PSEUDO) \
            or int(replicate) not in DRAWN.get(pool, ()):
        raise scope.ScopeViolation(
            f"pool {pool} replicate {replicate} (family {family}, {n_prior}+{n_pseudo}) is not a "
            f"predecessor-drawn selection {dict((k, list(v)) for k, v in DRAWN.items())}; it could "
            "read final-bank rows (PROTOCOL-20260925 section 3)")
    return refuse_sealed_pool(pool, protocol)


def _protocol_is_committed(protocol: Path) -> dict[str, Any]:
    """[pfd] The release must be COMMITTED (section 3): if the protocol lies in a git work tree,
    refuse uncommitted or untracked changes to it."""
    import subprocess
    d = str(Path(protocol).resolve().parent)
    inside = subprocess.run(["git", "-C", d, "rev-parse", "--is-inside-work-tree"],
                            capture_output=True, text=True)
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return {"git": "not in a git work tree"}
    tracked = subprocess.run(["git", "-C", d, "ls-files", "--error-unmatch",
                              str(Path(protocol).resolve())], capture_output=True, text=True)
    status = subprocess.run(["git", "-C", d, "status", "--porcelain", "--",
                             str(Path(protocol).resolve())], capture_output=True, text=True)
    if tracked.returncode != 0 or status.stdout.strip():
        raise scope.ScopeViolation(f"{protocol} has uncommitted changes or is untracked; a bank "
                                   "release counts only once committed")
    head = subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True)
    return {"git": "committed", "head": head.stdout.strip()}


def refuse_bank(bank: str, protocol: Path = STUDY_PROTOCOL) -> dict[str, Any]:
    """[pfd] DEV is open. FB is refused until the study protocol carries a heading
    `### Amendment ... FB release` (committed after the final set is frozen, section 8); RB until
    one `### Amendment ... RB release` (section 11 or a predeclared check). The check reads the
    protocol of THIS checkout, so a pinned checkout without the amendment cannot open the bank."""
    if bank not in BANK_CODES:
        raise SystemExit(f"[design] unknown bank {bank!r}; known {sorted(BANK_CODES)}")
    if bank == "DEV":
        return {"bank": bank, "sealed": False}
    text = Path(protocol).read_text()
    hit = BANK_RELEASE[bank].search(text)
    if hit is None:
        raise scope.ScopeViolation(
            f"bank {bank} is sealed: {protocol} carries no '### Amendment ... {bank} release' "
            "heading (PROTOCOL-20260925 section 3)")
    git = _protocol_is_committed(protocol)
    return {"bank": bank, "sealed": True, "released_by": hit.group(0),
            "protocol": str(protocol), "protocol_sha256": sha256_file(protocol), "git": git}


RELEASE_LISTING = re.compile(r"^RELEASED-MANIFEST\s+(FB|RB)\s+(\S+)\s+([0-9a-f]{64})\s*$",
                             re.MULTILINE)


def check_release_listing(bank: str, config_hash: str, bank_draw: str, distortion: str,
                          bootstrap_member: int | None, protocol: Path = STUDY_PROTOCOL
                          ) -> dict[str, Any]:
    """[pfd] Row-level release (review ec475e7b): a FB/RB run is allowed only if a manifest the
    committed protocol lists as `RELEASED-MANIFEST <bank> <path relative to final_design> <sha256>`
    exists in this checkout with that exact sha256 and contains a row with this config hash,
    selection `BANK:<bank>:<stage>:<rep>`, distortion and bootstrap member. DEV needs none."""
    if bank == "DEV":
        return {"bank": bank, "listed": None}
    text = Path(protocol).read_text()
    listings = [(b, rel, sha) for b, rel, sha in RELEASE_LISTING.findall(text) if b == bank]
    if not listings:
        raise scope.ScopeViolation(f"bank {bank}: the protocol lists no RELEASED-MANIFEST for it")
    selection = f"BANK:{bank}:{bank_draw}"
    member = None if bootstrap_member is None else str(int(bootstrap_member))
    for _b, rel, sha in listings:
        path = Path(protocol).resolve().parent / rel
        if not path.exists() or sha256_file(path) != sha:
            raise scope.ScopeViolation(f"released manifest {rel} missing or its sha256 differs "
                                       "from the protocol's listing")
        for line in path.read_text().splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            f = line.split("\t")
            if len(f) < 7 or f[2] != config_hash or f[3] != selection or f[4] != distortion:
                continue
            m = re.search(r"--bootstrap-member\s+(\d+)", f[6])
            if (m.group(1) if m else None) == member:
                return {"bank": bank, "listed": {"manifest": rel, "sha256": sha, "row": f[0]}}
    raise scope.ScopeViolation(f"bank {bank}: no released manifest lists config {config_hash[:12]}, "
                               f"{selection}, {distortion}, bootstrap member {member}")


# ------------------------------------------------------------------------------------------- #
# Distortions
# ------------------------------------------------------------------------------------------- #
def _frozen_design() -> Any:
    spec = importlib.util.spec_from_file_location("_frozen_design_for_confirm",
                                                  scope.FROZEN_DESIGN_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def historical_tilt_spec(populations_json: Path = POPULATIONS_JSON) -> dict[str, Any]:
    """The development tilt's constants, READ from the historical record, never retyped.

    Amplitude and clip: `configuration_comparison/frozen_design.ENDPOINT` (the frozen design).
    Standardization (p50, IQR of true E_avail over half A's truth-passing rows): the historical
    run's own tilt spec, replayed by B1 bit-identically to the recorded `tilt_a`
    (`phase_b/scalar/results/populations.json`, `tilt_spec_half_A`). Refuses if the two records
    disagree on amplitude or clip, or if Phase E's frozen D1 constants differ from them."""
    fd = _frozen_design()
    record = json.loads(Path(populations_json).read_text())
    b1 = record["tilt_spec_half_A"]
    amplitude, clip_z = float(fd.ENDPOINT["amplitude"]), float(fd.ENDPOINT["clip"])
    if float(b1["amplitude"]) != amplitude or float(b1["clip_z"]) != clip_z:
        raise SystemExit(f"[confirm] historical tilt spec {b1} disagrees with frozen_design "
                         f"(amplitude {amplitude}, clip {clip_z})")
    p50, iqr = float(b1["pt_p50"]), float(b1["pt_iqr"])
    if (p50, iqr, clip_z) != (dist.D1_P50_GEV, dist.D1_IQR_GEV, dist.TILT_CLIP_Z):
        raise SystemExit("[confirm] phase_e D1 constants differ from the historical tilt spec")
    return {"name": DEV, "form": "exp(A*clip((E-p50)/IQR, -Z, +Z)) / mean over the pseudodata's "
                                 "truth-passing rows",
            "amplitude": amplitude, "clip_z": clip_z, "p50": p50, "iqr": iqr,
            "historical_pre_normalization_mean": float(b1["pre_normalization_mean"]),
            "sources": {"frozen_design": "nd-unfolding/pet/configuration_comparison/"
                                          "frozen_design.py:ENDPOINT",
                        "frozen_design_sha256": sha256_file(scope.FROZEN_DESIGN_PATH),
                        "tilt_spec": "nd-unfolding/pet/improvement_campaign/phase_b/scalar/"
                                     "results/populations.json:tilt_spec_half_A",
                        "tilt_spec_sha256": sha256_file(populations_json)}}


def development_tilt_raw(eavail: np.ndarray, spec: Mapping[str, Any]) -> np.ndarray:
    """exp(A * clip((E - p50)/IQR, -Z, Z)), the operations of the historical
    `closure_powered_truth_reweight.clipped_exponential_tilt` in the same order, with its
    standardization frozen. Non-finite E is refused (the historical function would propagate it)."""
    e = np.asarray(eavail, dtype=np.float64)
    if not np.isfinite(e).all():
        raise SystemExit("[confirm] non-finite true E_avail on a truth-passing row")
    z = np.clip((e - float(spec["p50"])) / float(spec["iqr"]), -float(spec["clip_z"]),
                float(spec["clip_z"]))
    return np.exp(float(spec["amplitude"]) * z)


def unit_mean(raw: np.ndarray) -> tuple[np.ndarray, float]:
    """raw / mean(raw), as the historical tilt normalizes (unweighted mean over the rows given)."""
    mean = float(raw.mean())
    if not (np.isfinite(mean) and mean > 0):
        raise SystemExit(f"[confirm] distortion normalization is {mean!r}")
    w = raw / mean
    if not np.all(np.isfinite(w)) or np.any(w < 0):
        raise SystemExit("[confirm] distortion weight is non-finite or negative")
    return w, mean


@dataclass
class DistortionSpec:
    """A named truth-weight distortion: `dev` (the historical development tilt) or a
    `phase_e/distortions.py` truth-weight id."""
    name: str
    record: dict[str, Any]
    raw: Callable[[Mapping[str, np.ndarray]], np.ndarray]
    needs_species: bool = False
    reco_energy_scale: float | None = None   # R1 (amendment 3 item 3): pseudodata only
    muon_momentum_scale: float | None = None  # [pfd] R2: pseudodata only

    def content_hash(self) -> str:
        return hashlib.sha256(json.dumps(self.record, sort_keys=True, default=repr)
                              .encode()).hexdigest()


def get_distortion(name: str, endpoint_amplitude: float | None = None,
                   endpoint_clip: float | None = None) -> DistortionSpec:
    if name == DEV:
        spec = historical_tilt_spec()
        if endpoint_amplitude is not None and (float(endpoint_amplitude), float(endpoint_clip)) \
                != (spec["amplitude"], spec["clip_z"]):
            raise SystemExit(f"[confirm] the RunConfig endpoint ({endpoint_amplitude}, "
                             f"{endpoint_clip}) is not the historical tilt")
        return DistortionSpec(DEV, spec, lambda t: development_tilt_raw(t["eavail"], spec))
    if name == NULL:                                  # [pfd] no truth distortion
        return DistortionSpec(NULL, {"name": NULL, "form": "no truth distortion: weight 1 on "
                                     "every pseudodata row; target = the undistorted "
                                     "pseudodata truth"},
                              lambda t: np.ones(len(t["eavail"]), dtype=np.float64))
    registry = dist.registry()
    if "+" in name or (name in registry and registry[name].family in ("R1", "R2")):
        return _r1_distortion(name, registry)
    if "*" in name:                                   # [pfd] product of truth-weight distortions
        parts = [get_distortion(x) for x in name.split("*")]
        if any(x.reco_energy_scale is not None or x.muon_momentum_scale is not None
               for x in parts):
            raise SystemExit(f"[confirm] {name}: a product takes truth-weight factors only")

        def raw(t: Mapping[str, np.ndarray], parts=parts) -> np.ndarray:
            w = np.ones(len(t["eavail"]), dtype=np.float64)
            for x in parts:
                w = w * np.asarray(x.raw(t), np.float64)
            return w
        return DistortionSpec(name, {"name": name, "form": "product of the factors' raw weights, "
                                     "then unit mean over the pseudodata's truth-passing rows",
                                     "factors": [x.record for x in parts]},
                              raw, needs_species=any(x.needs_species for x in parts))
    if name not in registry:
        raise SystemExit(f"[confirm] unknown distortion {name!r}")
    d = registry[name]
    if d.kind != "truth_weight":
        raise SystemExit(f"[confirm] {name} is a reco-response distortion; the PET replicate path "
                         "implements truth-weight distortions only (not approximated, refused)")
    return DistortionSpec(name, {"name": name, "phase_e_spec": d.spec(),
                                 "phase_e_hash": d.content_hash(),
                                 "normalization": "unit mean over the pseudodata's truth-passing "
                                                  "rows"},
                          lambda t: np.asarray(d.truth_weight(t), np.float64),
                          needs_species=d.family == "D4")


def _r1_distortion(name: str, registry: Mapping[str, Any]) -> DistortionSpec:
    """R1 on the PET path (PROTOCOL amendment 3, item 3): every stored reco cluster energy and the
    reco E_avail of the PSEUDODATA are multiplied by the factor, at the raw-array level (the
    inventory's `part_reco[..., 0]` and `reco_scalars[:, eavail]`, before the loader builds the
    cloud). Muon quantities, reco q3, the prior and the selection are unchanged (so, unlike
    Phase E1's R1, reco q3 is NOT recomputed from the scaled recoil). Alone, or combined with a
    truth-weight distortion as `R1_x<s>+<truth id>`; the truth target is the truth part's."""
    reco_id, _, truth_id = name.partition("+")
    if reco_id not in registry or registry[reco_id].family not in ("R1", "R2"):
        raise SystemExit(f"[confirm] {name}: only R1 and R2 are implemented on the PET path "
                         "(R3 refused, not approximated)")
    family = registry[reco_id].family
    factor = float(dict(registry[reco_id].params)["scale"])
    if truth_id:
        truth = get_distortion(truth_id)
        if truth.reco_energy_scale is not None or truth.muon_momentum_scale is not None:
            raise SystemExit(f"[confirm] {name}: two reco distortions")
    else:
        truth = DistortionSpec("none", {"name": "none"}, lambda t: np.ones(len(t["eavail"])))
    applied = ("pseudodata part_reco[...,0] and reco_scalars[:,eavail] x factor on reco-passing "
               "rows; muon, q3, prior and selection unchanged (amendment 3 item 3)"
               if family == "R1" else
               "[pfd] pseudodata reco muon momentum x factor at fixed angle on reco-passing rows: "
               "reco_scalars pt, pparallel x s; reco_muon px, py, pz x s, E -> sqrt(E^2 + "
               "(s^2 - 1) p^2), q/p / s; reco q3 recomputed from the scaled muon and the "
               "unchanged recoil q0 (phase_e R2); E_avail, tokens, prior and selection unchanged")
    record = {"name": name, "reco": {"id": reco_id, "phase_e_spec": registry[reco_id].spec(),
                                     "applied": applied, "factor": factor},
              "truth": truth.record}
    return DistortionSpec(name, record, truth.raw, needs_species=truth.needs_species,
                          reco_energy_scale=factor if family == "R1" else None,
                          muon_momentum_scale=factor if family == "R2" else None)


# ------------------------------------------------------------------------------------------- #
# Row selection
# ------------------------------------------------------------------------------------------- #
@dataclass
class Selection:
    mode: str                       # "replicate" | "historical"
    load_rows: np.ndarray           # the rows the loader materializes (sorted, unique)
    prior_rows: np.ndarray          # sorted
    pseudo_rows: np.ndarray         # sorted
    record: dict[str, Any] = field(default_factory=dict)


def _sorted_unique(rows: np.ndarray, label: str) -> np.ndarray:
    rows = np.asarray(rows, dtype=np.int64)
    if rows.size and (np.any(np.diff(rows) <= 0) or rows[0] < 0):
        raise SystemExit(f"[confirm] {label} rows are not sorted, unique and non-negative")
    return rows


def replicate_selection(pool: str, replicate: int, *, pools_npz: Path, manifest: Path,
                        identity_sidecar: Path, n_prior: int = N_PRIOR, n_pseudo: int = N_PSEUDO,
                        family: str = FAMILY, protocol: Path = PROTOCOL) -> Selection:
    guard = refuse_pool(pool, replicate, family, n_prior, n_pseudo, protocol)   # [pfd]
    codes, pool_record = rp.load_pool_codes(pools_npz, manifest)
    manifest_doc = json.loads(Path(manifest).read_text())
    sidecar_sha = sha256_file(identity_sidecar)
    if sidecar_sha != manifest_doc["inputs"]["identity_npz"]["sha256"]:
        raise SystemExit("[confirm] identity sidecar sha256 differs from the pool manifest")
    with np.load(identity_sidecar, mmap_mode="r") as blob:
        identity_all = np.asarray(blob["sig_event_id"]).astype(np.int64)
    if identity_all.shape[0] != codes.size:
        raise SystemExit("[confirm] identity sidecar and pool codes disagree in length")
    rows = rp.pool_rows(codes, pool)
    design = rp.ReplicateDesign(pool=pool, family=family, n_prior=int(n_prior),
                                n_pseudo=int(n_pseudo), disjoint=True)
    reps, draw = rp.draw_replicates(design, [int(replicate)], rows, identity_all[rows])
    rep = reps[0]
    prior, pseudo = np.sort(rep.prior_rows), np.sort(rep.pseudo_rows)
    if np.intersect1d(prior, pseudo).size:
        raise AssertionError("prior and pseudodata share rows")
    record = {"mode": "replicate", "pool_guard": guard, "pools": pool_record,
              "identity_sidecar": str(identity_sidecar), "identity_sidecar_sha256": sidecar_sha,
              "draw": draw, "replicate": rep.record(),
              "prior_rows_sha256": rp.rows_digest(prior),
              "pseudo_rows_sha256": rp.rows_digest(pseudo),
              "prior_identity_sha256": sha256_bytes(identity_all[prior]),
              "pseudo_identity_sha256": sha256_bytes(identity_all[pseudo])}
    return Selection("replicate", np.union1d(prior, pseudo), prior, pseudo, record)


def load_bank_codes(banks_npz: Path, manifest: Path = BANK_MANIFEST
                    ) -> tuple[np.ndarray, dict[str, Any]]:
    """[pfd] The per-inventory-row bank codes, after checking `banks.npz` against the committed
    `BANK_MANIFEST.json` (file sha256, bank-code sha256, per-bank counts and sorted-row digests)."""
    doc = json.loads(Path(manifest).read_text())
    got = sha256_file(banks_npz)
    if got != doc["output"]["banks_npz_sha256"]:
        raise SystemExit(f"[design] banks npz sha256 {got} != manifest "
                         f"{doc['output']['banks_npz_sha256']}")
    with np.load(banks_npz, allow_pickle=False) as blob:
        codes = np.asarray(blob["bank_code"], dtype=np.int8)
    if hashlib.sha256(codes.tobytes()).hexdigest() != doc["output"]["bank_code_sha256"]:
        raise SystemExit("[design] bank_code digest differs from the manifest")
    for name, info in doc["banks"].items():
        if int(info["code"]) != BANK_CODES[name]:
            raise SystemExit(f"[design] bank {name} has code {info['code']} in the manifest")
        rows = np.flatnonzero(codes == BANK_CODES[name])
        if rows.size != int(info["count"]) or rp.rows_digest(rows) != info["sorted_rows_sha256"]:
            raise SystemExit(f"[design] bank {name} rows differ from the manifest")
    record = {"banks_npz": str(banks_npz), "banks_npz_sha256": got,
              "bank_manifest": str(manifest), "bank_manifest_sha256": sha256_file(manifest),
              "bank_manifest_code_commit": doc.get("code", {}).get("commit"),
              "counts": {k: int(v["count"]) for k, v in doc["banks"].items()},
              "identity_sidecar_sha256": doc["inputs"]["identity_sidecar_sha256"]}
    return codes, record


def _salt_order(identity: np.ndarray, rows: np.ndarray, salt: str) -> np.ndarray:
    """[pfd] Positions of `rows` sorted by (identity hash under `salt`, row)."""
    return rp._order(rp.uniform_hash(identity, rp.seed_from_salt(salt)), rows)


def bank_draw_salts(stage: str, replicate: int) -> dict[str, str]:
    """[pfd] The two salts of a bank draw (protocol section 3)."""
    if not stage or "/" in stage or ":" in stage or stage != stage.strip():
        raise SystemExit(f"[design] stage name {stage!r} must be non-empty, without '/' or ':'")
    if int(replicate) < 0:
        raise SystemExit("[design] replicate ids must be >= 0")
    base = f"{STUDY_SALT}/{stage}/{int(replicate)}"
    return {"pseudo": f"{base}/pseudo", "prior": f"{base}/prior"}


def draw_from_banks(codes: np.ndarray, identity_all: np.ndarray, stage: str, replicate: int,
                    pseudo_bank: str, n_prior: int = N_PRIOR, n_pseudo: int = N_PSEUDO
                    ) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """[pfd] (prior rows, pseudodata rows), both sorted, and the draw record. Pseudodata: the
    `n_pseudo` lowest-hash rows of the pseudodata bank; prior: the `n_prior` lowest-hash rows of DEV
    minus the pseudodata (a different salt), so the two are disjoint and each is a uniformly random
    subset without replacement. Identity-keyed: independent of row order and of other draws."""
    salts = bank_draw_salts(stage, replicate)
    codes = np.asarray(codes, dtype=np.int8)
    bank_rows = np.flatnonzero(codes == BANK_CODES[pseudo_bank]).astype(np.int64)
    if bank_rows.size < n_pseudo:
        raise SystemExit(f"[design] bank {pseudo_bank} holds {bank_rows.size} rows < {n_pseudo}")
    pos = _salt_order(identity_all[bank_rows], bank_rows, salts["pseudo"])[:int(n_pseudo)]
    pseudo = np.sort(bank_rows[pos])
    dev = np.flatnonzero(codes == BANK_CODES["DEV"]).astype(np.int64)
    keep = np.ones(dev.size, dtype=bool)
    if pseudo_bank == "DEV":
        keep[np.searchsorted(dev, pseudo)] = False
    candidates = dev[keep]
    if candidates.size < n_prior:
        raise SystemExit(f"[design] DEV minus the pseudodata holds {candidates.size} < {n_prior}")
    pos = _salt_order(identity_all[candidates], candidates, salts["prior"])[:int(n_prior)]
    prior = np.sort(candidates[pos])
    if np.intersect1d(prior, pseudo).size:
        raise AssertionError("prior and pseudodata share rows")
    if not (np.all(codes[pseudo] == BANK_CODES[pseudo_bank])
            and np.all(codes[prior] == BANK_CODES["DEV"])):
        raise AssertionError("a drawn row is outside its bank")
    record = {"stage": stage, "replicate": int(replicate), "pseudo_bank": pseudo_bank,
              "prior_bank": "DEV", "salts": salts,
              "seeds": {k: rp.seed_from_salt(v) for k, v in salts.items()},
              "n_pseudo_bank_rows": int(bank_rows.size), "n_prior_candidates": int(candidates.size),
              "n_prior": int(prior.size), "n_pseudo": int(pseudo.size),
              "pseudo_sampling_fraction": float(pseudo.size / bank_rows.size)}
    return prior, pseudo, record


def bank_selection(stage: str, replicate: int, pseudo_bank: str, *, banks_npz: Path,
                   identity_sidecar: Path, bank_manifest: Path = BANK_MANIFEST,
                   n_prior: int = N_PRIOR, n_pseudo: int = N_PSEUDO,
                   protocol: Path = STUDY_PROTOCOL) -> Selection:
    """[pfd] A study draw (protocol section 3): see `draw_from_banks`. The bank guard runs before
    any file is read."""
    guard = refuse_bank(pseudo_bank, protocol)
    codes, bank_record = load_bank_codes(banks_npz, bank_manifest)
    sidecar_sha = sha256_file(identity_sidecar)
    if sidecar_sha != bank_record["identity_sidecar_sha256"]:
        raise SystemExit("[design] identity sidecar sha256 differs from the bank manifest")
    with np.load(identity_sidecar, mmap_mode="r") as blob:
        identity_all = np.asarray(blob["sig_event_id"]).astype(np.int64)
    if identity_all.shape[0] != codes.size:
        raise SystemExit("[design] identity sidecar and bank codes disagree in length")
    prior, pseudo, draw = draw_from_banks(codes, identity_all, stage, replicate, pseudo_bank,
                                          n_prior, n_pseudo)
    record = {"mode": "bank", "bank_guard": guard, "banks": bank_record,
              "identity_sidecar": str(identity_sidecar), "identity_sidecar_sha256": sidecar_sha,
              "draw": draw,
              "prior_rows_sha256": rp.rows_digest(prior),
              "pseudo_rows_sha256": rp.rows_digest(pseudo),
              "prior_identity_sha256": sha256_bytes(identity_all[prior]),
              "pseudo_identity_sha256": sha256_bytes(identity_all[pseudo])}
    return Selection("bank", np.union1d(prior, pseudo), prior, pseudo, record)


def rows_in_bank(rows: np.ndarray, banks_npz: Path, bank_manifest: Path = BANK_MANIFEST,
                 bank: str = "DEV") -> dict[str, Any]:
    """[pfd] Refuse unless every row lies in `bank` (used on predecessor pool selections)."""
    codes, record = load_bank_codes(banks_npz, bank_manifest)
    rows = np.asarray(rows, dtype=np.int64)
    outside = int((codes[rows] != BANK_CODES[bank]).sum())
    if outside:
        raise scope.ScopeViolation(f"{outside} selected rows lie outside bank {bank}")
    return {"bank": bank, "n_rows": int(rows.size), "outside": 0, "banks": record}


def historical_selection(mods: Mapping[str, Any], events: Any, inputs_npz: Path,
                         identity_sidecar: Path) -> Selection:
    """The historical halves, replayed with the historical functions in `closure_data`'s order:
    the loader's subsample draw, `stage_splits`, `deterministic_halves`. Half A (tilted) is the
    pseudodata, half B the prior. The load set is the historical 2M subsample, so the loader's
    normalization statistics are the historical ones."""
    cp, rae, ss = mods["cp"], mods["rae"], mods["ss"]
    with np.load(inputs_npz, allow_pickle=False) as d:
        n = int(np.asarray(scope.SignalOnlyNpz(d)["pass_reco"]).shape[0])
    need = int(events.max_events)
    # `build_fullevent_loaders`: imc = sort(default_rng(seed).choice(N, min(max_events, N))).
    imc = np.sort(np.random.default_rng(int(events.subsample_seed))
                  .choice(n, min(need, n), replace=False))
    identity = rae._identity_of(np, identity_sidecar, imc)
    stage_pos = ss.rows_for_stage(identity, events.stage)
    half = (int(events.half_size) if events.half_size is not None
            else ss.usable_half_size(identity, events.stage))
    ja, jb = cp.deterministic_halves(stage_pos.size, half=half, seed=int(events.split_seed))
    pseudo, prior = imc[stage_pos[ja]], imc[stage_pos[jb]]
    record = {"mode": "historical", "subsample_seed": int(events.subsample_seed),
              "max_events": need, "stage": events.stage, "split_seed": int(events.split_seed),
              "half_size": half, "load_rows_sha256": rp.rows_digest(imc),
              "prior_rows_sha256": rp.rows_digest(prior),
              "pseudo_rows_sha256": rp.rows_digest(pseudo)}
    return Selection("historical", imc.astype(np.int64), _sorted_unique(prior, "prior"),
                     _sorted_unique(pseudo, "pseudodata"), record)


# ------------------------------------------------------------------------------------------- #
# The loader, on given rows
# ------------------------------------------------------------------------------------------- #
@dataclass
class LoadedRows:
    mc: Any                         # the engine DataLoader over `rows`
    rows: np.ndarray
    coord_reco: tuple
    coord_gen: tuple
    meta: dict[str, Any]
    truth_scalars: np.ndarray       # as stored (float32), per loaded row
    reco_scalars: np.ndarray
    pdg: np.ndarray                 # part_gen[..., 4] as stored, per loaded row
    w_truth_raw: np.ndarray         # float32 as stored
    w_reco_raw: np.ndarray
    keys_read: list[str]


def load_signal_rows(ffd: Any, DataLoader: type, inputs_npz: Path, rows: np.ndarray, *,
                     feature_names: Any = None, truth_feature_names: Any = None,
                     reco_energy_scale: tuple[np.ndarray, float] | None = None,
                     muon_momentum_scale: tuple[np.ndarray, float] | None = None) -> LoadedRows:
    """`build_fullevent_loaders(..., bkg_mode="mc-only")` with `imc = rows`, reading signal-MC
    members only (see the module docstring for the one deliberate difference).

    `reco_energy_scale = (scale_rows, factor)`: R1 -- multiply the raw stored cluster energies
    (`part_reco[..., 0]`, MeV) and reco E_avail of those inventory rows that pass reco by the
    factor BEFORE the cloud is built; nothing else changes."""
    feature_names = ffd.DEFAULT_EVT_FEATURES if feature_names is None else feature_names
    truth_feature_names = (ffd.DEFAULT_TRUTH_EVT_FEATURES if truth_feature_names is None
                           else truth_feature_names)
    imc = _sorted_unique(rows, "load")
    raw = np.load(inputs_npz, allow_pickle=True)
    d = scope.SignalOnlyNpz(raw)
    try:
        ffd.assert_extended_fps_edges(d["edges_0"], d["edges_1"])
        if str(np.asarray(d["petSchemaVersion"]).item() if "petSchemaVersion" in d.files
               else "") != "g2-fullevent-v1":
            raise ValueError("[confirm] input is not a g2-fullevent-v1 schema NPZ")
        n = np.asarray(d["pass_reco"]).shape[0]
        if imc.size == 0 or imc[-1] >= n:
            raise SystemExit(f"[confirm] rows outside the inventory ({n} rows)")
        need = {ffd._EVT_SPEC[f][0] for f in feature_names} | {ffd._EVT_SPEC[f][0]
                                                               for f in truth_feature_names}
        required = (["reco_muon"] if "muon" in need else []) + \
                   (["reco_vertex"] if "vertex" in need else []) + ["reco_view", "reco_time"]
        missing = [k for k in required if k not in d.files]
        if missing:
            raise ValueError(f"[confirm] the event-feature schema needs {missing}")

        def _tok(key: str) -> Any:
            return None if key not in d.files else np.asarray(d[key])[imc]

        part_reco = np.asarray(d["part_reco"])[imc]
        reco_scalars = np.asarray(d["reco_scalars"])[imc]
        pass_reco = np.asarray(d["pass_reco"])[imc]
        scaled = None
        if reco_energy_scale is not None:
            scale_rows, factor = reco_energy_scale
            scaled = np.isin(imc, np.asarray(scale_rows, np.int64)) & np.asarray(pass_reco, bool)
            f = part_reco.dtype.type(factor)
            part_reco[scaled, :, 0] = part_reco[scaled, :, 0] * f
            col = ffd.SCALAR_COLS["eavail"]
            reco_scalars[scaled, col] = reco_scalars[scaled, col] * reco_scalars.dtype.type(factor)
        mscaled = None
        reco_muon = np.asarray(d["reco_muon"])[imc] if "reco_muon" in d.files else None
        if muon_momentum_scale is not None:           # [pfd] R2
            scale_rows, factor = muon_momentum_scale
            mscaled = np.isin(imc, np.asarray(scale_rows, np.int64)) & np.asarray(pass_reco, bool)
            reco_scalars, reco_muon = apply_muon_scale(ffd, reco_scalars, reco_muon, mscaled,
                                                       float(factor))
        reco_cloud, coord_reco = ffd.build_reco_cloud(part_reco,
                                                      _tok("reco_view"), _tok("reco_time"))
        part_gen = np.asarray(d["part_gen"])[imc]
        gen_cloud, coord_gen = ffd.build_truth_cloud(part_gen)
        truth_scalars = np.asarray(d["truth_scalars"])[imc]
        pass_truth = np.asarray(d["pass_truth"])[imc]
        reco_blocks = ffd.evt_blocks(
            scalars=reco_scalars,
            muon=reco_muon,
            vertex=(np.asarray(d["reco_vertex"])[imc] if "reco_vertex" in d.files else None))
        truth_blocks = ffd.evt_blocks(scalars=truth_scalars)
        # The data event block is built and discarded by the mc-only loader; its statistics do
        # not enter the MC blocks. Stand-in: this sample's own reco-passing MC rows.
        sel = np.asarray(pass_reco, bool)
        stand_in = {k: (None if v is None else np.asarray(v)[sel]) for k, v in reco_blocks.items()}
        event_reco, event_truth, _discarded, meta = ffd.build_event_features(
            reco_blocks, truth_blocks, stand_in, feature_names,
            pass_reco=pass_reco, pass_truth=pass_truth, truth_feature_names=truth_feature_names)
        meta["data_scalar_source"] = "NOT READ: stand-in = the loaded MC rows' reco blocks"
        meta["reco_cloud_cols"] = list(ffd.RECO_CLOUD_COLS[:reco_cloud.shape[-1]])
        meta["token_view_time_read"] = reco_cloud.shape[-1] == len(ffd.RECO_CLOUD_COLS)
        ffd.assert_no_truth_leakage(event_reco, reco_blocks, truth_blocks, feature_names,
                                    pass_reco=pass_reco, truth_feature_names=truth_feature_names)
        w_truth_full = np.asarray(d["w_truth"]).astype(np.float32)
        w_reco_full = np.asarray(d["w_reco"]).astype(np.float32)
        if w_reco_full.shape != w_truth_full.shape:
            raise ValueError("[confirm] w_reco and w_truth are not row-aligned")
        meta["bkg_mode"] = "mc-only"
        meta["input_identity_hashes"] = {"sig": ffd._verify_stored_identity(
            d, "sig_identity_hash", (w_truth_full, np.asarray(d["pass_truth"])), "signal")}
        meta["bootstrap"] = None
        w_truth, w_reco = w_truth_full[imc], w_reco_full[imc]
        mc = DataLoader(reco=reco_cloud, gen=gen_cloud, pass_reco=pass_reco,
                        pass_gen=pass_truth, weight=w_truth, weight_reco=w_reco, normalize=True,
                        normalization_factor=ffd.STEP1_MC_NORMALIZATION, reco_evt=event_reco,
                        gen_evt=event_truth, rank=0, size=1)
        meta["mc_only"] = True
        meta["muon_momentum_scale"] = (None if mscaled is None else
                                       {"factor": float(muon_momentum_scale[1]),
                                        "rows_scaled": int(mscaled.sum())})
        meta["reco_energy_scale"] = (None if scaled is None else
                                     {"factor": float(reco_energy_scale[1]),
                                      "rows_scaled": int(scaled.sum())})
        keys = list(d.keys_read)
    finally:
        d.close()
    unexpected = sorted(set(keys) - set(SIGNAL_MEMBERS))
    if unexpected:
        raise SystemExit(f"[confirm] the loader read unexpected members {unexpected}")
    return LoadedRows(mc, imc, tuple(coord_reco), tuple(coord_gen), meta, truth_scalars,
                      reco_scalars, part_gen[..., 4], w_truth, w_reco, keys)


# ------------------------------------------------------------------------------------------- #
# The closure
# ------------------------------------------------------------------------------------------- #
def truth_mapping(ffd: Any, truth_scalars: np.ndarray, pdg: np.ndarray | None) -> dict:
    cols = ffd.SCALAR_COLS
    t = np.asarray(truth_scalars, dtype=np.float64)
    out = {"pt": t[:, cols["pt"]], "ppar": t[:, cols["pparallel"]],
           "eavail": t[:, cols["eavail"]], "q3": t[:, cols["q3"]]}
    if pdg is not None:
        out.update({f"n_{k}": v for k, v in dist.count_species(pdg).items()})
    return out


def _subset(m: Mapping[str, np.ndarray], idx: np.ndarray) -> dict[str, np.ndarray]:
    return {k: np.asarray(v)[idx] for k, v in m.items()}


def assemble_closure(ffd: Any, loaded: LoadedRows, selection: Selection,
                     distortion: DistortionSpec, ClosureInputs: type) -> tuple[Any, dict]:
    """`closure_data.build_closure_inputs` (ours arm) on the selected rows. Returns the
    `ClosureInputs` and the per-row scoring arrays (`replicate_arrays.npz`)."""
    imc = loaded.rows
    mc = loaded.mc
    ia = np.searchsorted(imc, selection.pseudo_rows)
    ib = np.searchsorted(imc, selection.prior_rows)
    if not (np.array_equal(imc[ia], selection.pseudo_rows)
            and np.array_equal(imc[ib], selection.prior_rows)):
        raise SystemExit("[confirm] selected rows are not in the load set")
    if np.intersect1d(ia, ib).size:
        raise SystemExit("[confirm] prior and pseudodata overlap")
    reco, reco_evt = np.asarray(mc.reco), np.asarray(mc.reco_evt)
    gen, gen_evt = np.asarray(mc.gen), np.asarray(mc.gen_evt)
    pr = np.asarray(mc.pass_reco).astype(bool)
    pg = np.asarray(mc.pass_gen).astype(bool)
    w_truth = np.asarray(mc.weight, dtype=np.float64)
    w_reco = np.asarray(mc.weight_reco, dtype=np.float64)

    truth = truth_mapping(ffd, loaded.truth_scalars,
                          loaded.pdg if distortion.needs_species else None)
    pg_a = pg[ia]
    raw_a = distortion.raw(_subset(truth, ia[pg_a]))
    tilt_on_truth, mean_a = unit_mean(raw_a)
    tilt_a = np.ones(ia.size, dtype=np.float64)
    tilt_a[pg_a] = tilt_on_truth
    s1_a = pr[ia] & pg_a
    s1_b = pr[ib] & pg[ib]
    pdata = {"reco": reco[ia][s1_a], "reco_evt": reco_evt[ia][s1_a],
             "weight": ((w_reco[ia] * tilt_a)[s1_a]).astype(np.float32),
             "rows": imc[ia][s1_a].astype(np.int64)}
    mcb = {"reco": reco[ib], "reco_evt": reco_evt[ib], "gen": gen[ib], "gen_evt": gen_evt[ib],
           "pass_reco": s1_b, "pass_gen": pg[ib],
           "weight": w_truth[ib].astype(np.float32),
           "weight_reco": w_reco[ib].astype(np.float32),
           "rows": imc[ib].astype(np.int64)}

    # The oracle anchor: the exact distortion function on the PRIOR's truth-passing rows,
    # normalized the same way (unit mean over those rows).
    pg_b = pg[ib]
    oracle_b = np.ones(ib.size, dtype=np.float64)
    oracle_b[pg_b], mean_b = unit_mean(distortion.raw(_subset(truth, ib[pg_b])))

    tilt_spec = dict(distortion.record)
    tilt_spec.update({"pre_normalization_mean": mean_a, "n_injected_rows": int(pg_a.sum()),
                      "applied_on": "pass_truth rows of the pseudodata only",
                      "oracle_prior_pre_normalization_mean": mean_b})
    meta = {
        "n_evt_reco": int(loaded.meta["n_evt_reco"]), "n_evt_truth": int(loaded.meta["n_evt_truth"]),
        "coord_reco": tuple(int(c) for c in loaded.coord_reco),
        "coord_gen": tuple(int(c) for c in loaded.coord_gen),
        "half_size": None, "stage_rows": None, "split_census": None,
        "tilt_spec": tilt_spec,
        "dump_rows_a": imc[ia].astype(np.int64), "dump_rows_b": imc[ib].astype(np.int64),
        "tilt_a": tilt_a, "pass_gen_a": pg_a, "mc_indices": imc.astype(np.int64),
        "substitution": None, "step1_mc_normalization": ffd.STEP1_MC_NORMALIZATION,
        "selection": selection.record, "distortion": distortion.name,
        "distortion_hash": distortion.content_hash(), "members_read": loaded.keys_read,
    }
    cols = ffd.SCALAR_COLS
    ts = np.asarray(loaded.truth_scalars, np.float64)
    rs = np.asarray(loaded.reco_scalars, np.float64)
    arrays = {
        "pseudo_rows": imc[ia].astype(np.int64), "prior_rows": imc[ib].astype(np.int64),
        "pseudo_pass_truth": pg_a, "prior_pass_truth": pg_b,
        "pseudo_pass_reco": pr[ia], "prior_pass_reco": pr[ib],
        "pseudo_truth": ts[ia][:, [cols["pt"], cols["pparallel"], cols["eavail"], cols["q3"]]],
        "prior_truth": ts[ib][:, [cols["pt"], cols["pparallel"], cols["eavail"], cols["q3"]]],
        "pseudo_reco_eavail": rs[ia][:, cols["eavail"]],
        "prior_reco_eavail": rs[ib][:, cols["eavail"]],
        "pseudo_w_truth": np.asarray(loaded.w_truth_raw, np.float64)[ia],
        "prior_w_truth": np.asarray(loaded.w_truth_raw, np.float64)[ib],
        "pseudo_w_reco": np.asarray(loaded.w_reco_raw, np.float64)[ia],
        "prior_w_reco": np.asarray(loaded.w_reco_raw, np.float64)[ib],
        "pseudo_distortion": tilt_a, "prior_oracle": oracle_b,
    }
    return ClosureInputs(arm="ours", pdata=pdata, mc=mcb, meta=meta), arrays


def historical_cr() -> Any:
    """`characterize_regions`, loaded through Phase E's blob-checked historical import."""
    import common as cm
    return cm.historical()["cr"]


def region_codes(cr: Any, pt: np.ndarray, ppar: np.ndarray, populations_npz: Path) -> np.ndarray:
    """Historical region of each event's truth (pT, p||) cell under the historical acceptance map
    (B1's cached copy of `report_campaign.build_endpoint`'s map), as Phase E codes it."""
    import common as cm
    got = sha256_file(populations_npz)
    if got != cm.B1_POPULATIONS_SHA256:
        raise SystemExit(f"[confirm] B1 populations.npz sha256 {got} differs from the committed one")
    with np.load(populations_npz, allow_pickle=False) as b1:
        acceptance = np.asarray(b1["map_acceptance"], float)
        edges_pt = np.asarray(b1["edges_pt"], float)
        edges_pz = np.asarray(b1["edges_pz"], float)
    labels, _cell = cr.region_labels_for_events(pt, ppar, edges_pt, edges_pz, acceptance)
    return np.array([cm.REGION_CODES[x] for x in labels], dtype=np.int8)


def compare_inputs(np_: Any, ours: Any, reference: Any) -> dict[str, Any]:
    """Byte comparison of every array the engine receives (and the row lists)."""
    out: dict[str, Any] = {}
    for side in ("pdata", "mc"):
        a, b = getattr(ours, side), getattr(reference, side)
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                out[f"{side}.{key}"] = "missing"
                continue
            x, y = np_.asarray(a[key]), np_.asarray(b[key])
            out[f"{side}.{key}"] = bool(x.dtype == y.dtype and x.shape == y.shape
                                        and sha256_bytes(x) == sha256_bytes(y))
    for key in ("dump_rows_a", "dump_rows_b", "tilt_a", "pass_gen_a", "coord_reco", "coord_gen"):
        x, y = np_.asarray(ours.meta[key]), np_.asarray(reference.meta[key])
        out[f"meta.{key}"] = bool(x.shape == y.shape and x.dtype == y.dtype
                                  and sha256_bytes(x) == sha256_bytes(y))
    out["all_equal"] = all(v is True for v in out.values())
    return out


MUON_COLS = {"px": 0, "py": 1, "pz": 2, "E": 3, "qp": 5}   # fullevent_fps_dataloader.MUON_COLS


def r2_scalars(pt: np.ndarray, ppar: np.ndarray, q3: np.ndarray, s: float
               ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """[pfd] R2 on reco scalars (GeV): p -> s p at fixed angle, q3 recomputed from the scaled
    muon and the unchanged recoil q0 (phase_e distortions.muon_scale)."""
    q0, _bad = dist.recoil_q0(pt, ppar, q3)
    pt2, ppar2 = s * pt, s * ppar
    return pt2, ppar2, dist.reco_q3(pt2, ppar2, q0)


def apply_muon_scale(ffd: Any, reco_scalars: np.ndarray, reco_muon: np.ndarray | None,
                     rows: np.ndarray, s: float) -> tuple[np.ndarray, np.ndarray | None]:
    """[pfd] R2 at the raw-array level on the masked rows (reco-passing pseudodata)."""
    rs = np.array(reco_scalars, copy=True)
    c = ffd.SCALAR_COLS
    pt, ppar, q3 = (rs[rows, c[k]].astype(np.float64) for k in ("pt", "pparallel", "q3"))
    pt2, ppar2, q32 = r2_scalars(pt, ppar, q3, s)
    for k, v in (("pt", pt2), ("pparallel", ppar2), ("q3", q32)):
        rs[rows, c[k]] = v.astype(rs.dtype)
    mu = None
    if reco_muon is not None:
        mu = np.array(reco_muon, copy=True)
        p2 = sum(mu[rows, MUON_COLS[k]].astype(np.float64) ** 2 for k in ("px", "py", "pz"))
        E = mu[rows, MUON_COLS["E"]].astype(np.float64)
        for k in ("px", "py", "pz"):
            mu[rows, MUON_COLS[k]] = (mu[rows, MUON_COLS[k]] * s).astype(mu.dtype)
        mu[rows, MUON_COLS["E"]] = np.sqrt(np.maximum(E ** 2 + (s ** 2 - 1.0) * p2, 0.0)
                                           ).astype(mu.dtype)
        mu[rows, MUON_COLS["qp"]] = (mu[rows, MUON_COLS["qp"]] / s).astype(mu.dtype)
    return rs, mu


def scaled_reader(np_: Any, read: Callable, r1: tuple[np.ndarray, float] | None,
                  r2: tuple[np.ndarray, float] | None = None) -> Callable:
    """The B2 arms' reco-scalar reader with R1 applied to reco E_avail of the pseudodata rows
    (the arms read reco scalars straight from the inventory, bypassing the loader)."""
    if r1 is None and r2 is None:
        return read
    if r2 is not None:                                # [pfd] R2: pt, pparallel, q3 of the rows
        r2_rows, r2_s = np_.asarray(r2[0], np_.int64), float(r2[1])

        def wrapped2(which: str, column: str, rows: Any) -> Any:
            vals = np_.array(read(which, column, rows), dtype=np_.float64, copy=True)
            if which == "reco" and column in ("pt", "pparallel", "q3"):
                hit = np_.isin(np_.asarray(rows, np_.int64), r2_rows)
                r = np_.asarray(rows)[hit]
                pt, ppar, q3 = (read("reco", k, r) for k in ("pt", "pparallel", "q3"))
                ok = q3 > -999      # the dump's miss sentinel is never scaled
                new = dict(zip(("pt", "pparallel", "q3"), r2_scalars(pt, ppar, q3, r2_s)))
                v = vals[hit]
                v[ok] = new[column][ok].astype(np_.float32).astype(np_.float64)
                vals[hit] = v
            return vals
        return wrapped2
    rows_scaled, factor = np_.asarray(r1[0], np_.int64), float(r1[1])

    def wrapped(which: str, column: str, rows: Any) -> Any:
        vals = read(which, column, rows)
        if which == "reco" and column == "eavail":
            vals = np_.array(vals, dtype=np_.float64, copy=True)
            hit = np_.isin(np_.asarray(rows, np_.int64), rows_scaled)
            # the float32 product, as the loader scales the stored float32 column
            vals[hit] = (vals[hit].astype(np_.float32) * np_.float32(factor)).astype(np_.float64)
        return vals

    return wrapped


# ------------------------------------------------------------------------------------------- #
# [pfd] Bootstrap members (PROTOCOL-20260925 section 9)
# ------------------------------------------------------------------------------------------- #
BOOTSTRAP_SALT = f"{STUDY_SALT}/bootstrap"
MEMBER_SEED_SALT = f"{STUDY_SALT}/bootstrap-estimator-seed"
_POISSON_KMAX = 40


def poisson1_quantile(u: np.ndarray) -> np.ndarray:
    """Poisson(1) by inversion of a uniform in [0, 1): the smallest k with CDF(k) > u."""
    k = np.arange(_POISSON_KMAX + 1)
    pmf = np.exp(-1.0) / np.cumprod(np.concatenate([[1.0], k[1:].astype(np.float64)]))
    cdf = np.cumsum(pmf)
    cdf[-1] = np.inf           # u < 1 always lands (the tail beyond k=40 is < 1e-48)
    return np.searchsorted(cdf, np.asarray(u, np.float64), side="right").astype(np.float64)


def bootstrap_counts(identity: np.ndarray, seed: int, member: int, side: str) -> np.ndarray:
    """Poisson(1) weight per event, a function of (seed, member, side, event identity) only: a
    member is reproducible, independent of row order, and prior/pseudodata draws are independent
    (different salts)."""
    if side not in ("prior", "pseudo"):
        raise ValueError(f"side {side!r}")
    salt = f"{BOOTSTRAP_SALT}/{int(seed)}/{int(member)}/{side}"
    return poisson1_quantile(rp.uniform_hash(identity, rp.seed_from_salt(salt)))


def member_seed(seed: int, member: int, field_name: str) -> int:
    """An estimator seed of bootstrap member `member`: sha256(salt/field/seed/member) ->
    [1, 2^31 - 1], so each step's training and validation-split seeds stay decoupled."""
    h = hashlib.sha256(f"{MEMBER_SEED_SALT}/{field_name}/{int(seed)}/{int(member)}".encode())
    return int.from_bytes(h.digest()[:4], "big") % (2 ** 31 - 1) + 1


def bootstrap_config(config: Any, member: int) -> tuple[Any, dict[str, Any]]:
    """The RunConfig of a member: the four estimator seeds replaced by `member_seed` of each."""
    import dataclasses
    seeds: dict[str, Any] = {}

    def step(s: Any, label: str) -> Any:
        new, new_val = member_seed(s.seed, member, f"{label}.seed"), \
            member_seed(s.validation.seed, member, f"{label}.validation.seed")
        seeds[label] = {"seed": [int(s.seed), new],
                        "validation.seed": [int(s.validation.seed), new_val]}
        return dataclasses.replace(s, seed=new,
                                   validation=dataclasses.replace(s.validation, seed=new_val))
    out = config.replace(step1=step(config.step1, "step1"), step2=step(config.step2, "step2"))
    return out, {"member": int(member), "seeds_config_to_member": seeds,
                 "config_hash": config.content_hash(), "member_config_hash": out.content_hash()}


def identity_of_rows(identity_sidecar: Path, rows: np.ndarray) -> np.ndarray:
    with np.load(identity_sidecar, mmap_mode="r") as blob:
        return np.asarray(blob["sig_event_id"]).astype(np.int64)[np.asarray(rows, np.int64)]


def apply_bootstrap(inputs: Any, arrays: dict[str, np.ndarray], identity_pseudo: np.ndarray,
                    identity_prior: np.ndarray, seed: int, member: int) -> dict[str, Any]:
    """Multiply the engine's event weights by Poisson(1) counts BEFORE the DataLoaders normalize
    them: the pseudodata weights (`inputs.pdata['weight']`, its reco&truth-passing rows) and both
    prior weight legs (`inputs.mc['weight']`, `['weight_reco']`). `identity_*` are aligned with
    `arrays['pseudo_rows']` / `arrays['prior_rows']`.

    Scoring arrays: the pseudodata arrays stay UNRESAMPLED (the score target is the replicate's
    own undistorted-or-distorted pseudodata truth); the prior's `prior_w_truth`/`prior_w_reco`
    carry the member's resampled weights (the member's unfolded histogram is prior weight x count x
    push), with the unresampled legs kept beside them (`*_unresampled`). The Poisson weights are
    stored as `prior_bootstrap_weight` / `pseudo_bootstrap_weight` (convention agreed with the
    analysis lane); the score target never includes `pseudo_bootstrap_weight`."""
    ks_pseudo = bootstrap_counts(identity_pseudo, seed, member, "pseudo")
    ks_prior = bootstrap_counts(identity_prior, seed, member, "prior")
    rows_a, rows_b = arrays["pseudo_rows"], arrays["prior_rows"]
    if not (np.array_equal(inputs.meta["dump_rows_a"], rows_a)
            and np.array_equal(inputs.mc["rows"], rows_b)):
        raise SystemExit("[design] bootstrap: row order differs between inputs and arrays")
    pos = np.searchsorted(rows_a, inputs.pdata["rows"])
    if not np.array_equal(rows_a[pos], inputs.pdata["rows"]):
        raise SystemExit("[design] bootstrap: pseudodata rows are not in the draw")
    before = {"pdata.weight": sha256_bytes(inputs.pdata["weight"]),
              "mc.weight": sha256_bytes(inputs.mc["weight"]),
              "mc.weight_reco": sha256_bytes(inputs.mc["weight_reco"])}
    inputs.pdata["weight"] = (np.asarray(inputs.pdata["weight"], np.float64)
                              * ks_pseudo[pos]).astype(np.float32)
    inputs.mc["weight"] = (np.asarray(inputs.mc["weight"], np.float64) * ks_prior
                           ).astype(np.float32)
    inputs.mc["weight_reco"] = (np.asarray(inputs.mc["weight_reco"], np.float64) * ks_prior
                                ).astype(np.float32)
    arrays["prior_w_truth_unresampled"] = arrays["prior_w_truth"]
    arrays["prior_w_reco_unresampled"] = arrays["prior_w_reco"]
    arrays["prior_w_truth"] = arrays["prior_w_truth"] * ks_prior
    arrays["prior_w_reco"] = arrays["prior_w_reco"] * ks_prior
    arrays["prior_bootstrap_weight"] = ks_prior
    arrays["pseudo_bootstrap_weight"] = ks_pseudo
    after = {"pdata.weight": sha256_bytes(inputs.pdata["weight"]),
             "mc.weight": sha256_bytes(inputs.mc["weight"]),
             "mc.weight_reco": sha256_bytes(inputs.mc["weight_reco"])}

    def stats(k: np.ndarray) -> dict[str, Any]:
        return {"n": int(k.size), "mean": float(k.mean()), "var": float(k.var()),
                "n_zero": int((k == 0).sum()), "max": int(k.max()),
                "sha256": sha256_bytes(k)}
    return {"member": int(member), "seed": int(seed), "salt": BOOTSTRAP_SALT,
            "applied": "Poisson(1) x pdata.weight, mc.weight, mc.weight_reco before the "
                       "DataLoaders normalize",
            "counts_pseudo": stats(ks_pseudo), "counts_prior": stats(ks_prior),
            "weight_digests_before": before, "weight_digests_after": after,
            "scorer": {"target": "UNRESAMPLED pseudodata truth x distortion",
                       "prior_w_truth/prior_w_reco": "resampled (x prior count); unresampled "
                                                     "legs in *_unresampled"}}
