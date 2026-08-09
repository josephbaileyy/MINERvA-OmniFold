"""Quarantine harness for a NON-QUOTABLE diagnostic full-event extraction.

WHY THIS EXISTS. The full-event extractor became runnable on 2026-08-08 when the BEN-043 checkpoint
fix made Gate A/B bit-exact and `check_subsample_agreement` stopped failing closed at 0.866. Running
it is information we need whatever Gate-4 says -- it has never been exercised on real input, so its
first run is as much a test of the extractor as of the physics. But the fold-forward deficit is
untouched: the reco-weighted mean of push is 0.736746 against R = 1.124080, so the cross section this
produces is knowingly ~34% low. Branch C of PREDECLARATION-20260808 governs: no product is quoted
while any leg is red.

So the product is created deliberately and made unquotable by construction, following the pattern
`fps_build_control_manifest.py` established for the purity controls: a separate namespace, a marker
in the filename, and a manifest that self-declares `publication_gate_rejects_this`.

THE FLAG IS EARNED, NOT ASSERTED. This is the part worth reading. Writing
`publication_gate_rejects_this: true` into a JSON is a claim, and this repo has already been bitten
by trusting a claimed boolean -- `check_powered_closure`'s own docstring records that its first
version accepted `is_powered_closure` and `recovery_criteria_met` as evidence of the thing they were
naming, and BEN-043 was a checkpoint whose contract said one thing while the bytes said another. So
`require_quotable` does not read the flag. It RECOMPUTES the fold-forward deviation from the weights
artifact and rejects on the physics, which means:

  * hand-flipping the flag to false does not make the product quotable;
  * copying the manifest into the publication namespace does not either;
  * renaming the file to drop the marker does not either.

`build_diagnostic_manifest` proves all three by laundering a copy of its own manifest -- publication
schema, publication namespace, marker stripped -- and requiring the gate to reject it anyway. If that
laundered copy ever passes, the builder dies instead of writing. That is the power test BEN-070 rule
(3) asks for, applied to a gate whose whole job is to say no.

FROZEN docstring rule 2 is the governing convention here and it is why this works: "Everything
compared against FROZEN is read from the ARTIFACT (or recomputed from the G2 dump), never copied out
of FROZEN. A self-comparison is not a check."
"""
import hashlib
import json
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

DIAGNOSTIC_SCHEMA = "pet-fullevent-diagnostic-quarantine-v1"
DIAGNOSTIC_LABEL = "nonquotable-diagnostic"
QUARANTINE_DIRNAME = "fullevent_diagnostic_nonquotable"
FILENAME_MARKER = "NONQUOTABLE-DIAGNOSTIC"

# The publication-side names this product is deliberately NOT. Kept here so the laundering power test
# can construct a maximally-publication-looking manifest without importing the validator (which pulls
# in the dataloader and is not login-safe).
PUBLICATION_SCHEMA = "pet-fullevent-fps-xsec-v1"
PUBLICATION_LABEL = "publication"

# Read from validate_pet_nominal_gate4.FROZEN["tolerances"]["fold_forward_ratio_dev_max"]. Duplicated
# as a literal ONLY so this module stays importable on a login node; `require_quotable` cross-checks
# it against the validator's own value whenever that import succeeds, and dies on disagreement rather
# than silently using a stale copy.
FOLD_FORWARD_DEV_MAX = 0.05


class NonQuotableError(RuntimeError):
    """Raised by `require_quotable` when a product must not be quoted."""


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _npz_scalar(z, key):
    v = np.asarray(z[key]).ravel()
    if v.size != 1:
        raise NonQuotableError(f"{key}: expected a scalar, got shape {np.asarray(z[key]).shape}")
    return float(v[0])


def _frozen_tolerance():
    """The validator's own tolerance if importable, else the local literal.

    Returns (value, source). A disagreement is a hard error: a quarantine gate running on a stale
    copy of the number it enforces is the BEN-072 defect (a gate mis-specified against the thing it
    reproduces), and this module exists to be trusted about a negative.
    """
    try:
        import validate_pet_nominal_gate4 as g4  # noqa: WPS433 (optional, not login-safe)
    except Exception:
        return FOLD_FORWARD_DEV_MAX, "local-literal (validator not importable here)"
    theirs = float(g4.FROZEN["tolerances"]["fold_forward_ratio_dev_max"])
    if theirs != FOLD_FORWARD_DEV_MAX:
        raise NonQuotableError(
            f"fold_forward_ratio_dev_max drift: this module has {FOLD_FORWARD_DEV_MAX}, "
            f"validate_pet_nominal_gate4.FROZEN has {theirs}. Fix the literal here; do not "
            f"proceed on a stale tolerance.")
    return theirs, "validate_pet_nominal_gate4.FROZEN"


def measured_fold_forward_dev(weights_npz):
    """Recompute |(sum_w_push_reco/sum_w_reco)/R - 1| from the ARTIFACT, not from any report.

    Same arithmetic as `validate_pet_nominal_gate4._ratio_dev`, on the same three artifact keys the
    nominal driver writes. R comes from the artifact's own `target.step1_class_ratio`, so a product
    built against a different R is measured against that R rather than against a remembered one.
    """
    with np.load(weights_npz, allow_pickle=True) as z:
        # An absent key must fail CLOSED with a reason, not escape as a bare KeyError that a caller
        # might catch as "no measurement available" and treat as benign.
        for key in ("fold_forward_sum_w_push_reco", "fold_forward_sum_w_reco", "target"):
            if key not in z.files:
                raise NonQuotableError(
                    f"{weights_npz}: required key '{key}' is absent, so the fold-forward deviation "
                    f"cannot be recomputed. A product whose physics cannot be measured is not "
                    f"quotable.")
        num = _npz_scalar(z, "fold_forward_sum_w_push_reco")
        den = _npz_scalar(z, "fold_forward_sum_w_reco")
        target = z["target"]
        try:
            target = target.item()
        except Exception:
            pass
        if not isinstance(target, dict) or "step1_class_ratio" not in target:
            raise NonQuotableError(f"{weights_npz}: target.step1_class_ratio is missing")
        R = float(target["step1_class_ratio"])
    if not (den and R):
        return float("inf"), num, den, R
    return abs((num / den) / R - 1.0), num, den, R


def require_quotable(manifest, weights_npz):
    """Raise NonQuotableError unless this product could legitimately be quoted.

    FOUR INDEPENDENT GROUNDS, and the physics one is deliberately checked FIRST and separately so it
    alone is sufficient. The other three are hygiene: they make the product self-describing, but they
    are all defeatable by an editor and none of them is what actually protects the record.
    """
    dev, num, den, R = measured_fold_forward_dev(weights_npz)
    tol, tol_src = _frozen_tolerance()

    # GROUND 1 -- the physics, recomputed from the artifact. Sufficient on its own.
    if not (dev <= tol):
        raise NonQuotableError(
            f"fold-forward deviation {dev:.6f} exceeds {tol:g} (from {tol_src}) by "
            f"{dev / tol:.1f}x: reco-weighted mean of push = {num / den:.6f} against R = {R:.6f}. "
            f"The cross section built from these weights is low by ~{100.0 * dev:.1f}%. "
            f"NOT QUOTABLE on the physics alone, independent of how this manifest is labelled.")

    # GROUNDS 2-4 -- self-description. Reached only if the physics ever comes into tolerance.
    if manifest.get("schema") == DIAGNOSTIC_SCHEMA:
        raise NonQuotableError(f"manifest schema is {DIAGNOSTIC_SCHEMA} (a diagnostic, not a result)")
    if manifest.get("label") == DIAGNOSTIC_LABEL:
        raise NonQuotableError(f"manifest label is {DIAGNOSTIC_LABEL}")
    for key in ("xsec_path", "push_path", "manifest_path"):
        p = str(manifest.get(key) or "")
        if QUARANTINE_DIRNAME in p or FILENAME_MARKER in os.path.basename(p):
            raise NonQuotableError(f"{key}={p} is in the quarantine namespace / carries the marker")
    return True


def _assert_rejects(manifest, weights_npz, why):
    """Require `require_quotable` to reject, and return the reason it gave."""
    try:
        require_quotable(manifest, weights_npz)
    except NonQuotableError as exc:
        return str(exc)
    raise SystemExit(f"[quarantine] FATAL: publication gate did NOT reject {why}. "
                     f"Refusing to write a manifest whose non-quotability is unproven.")


def build_diagnostic_manifest(*, weights_npz, xsec_npz, push_npz, xsec_summary, out_path,
                              inputs_npz, job_id=None, extra=None):
    """Build, prove, and write the read-only non-quotable manifest.

    The proof is the point. Two rejections are recorded:
      * `rejection_reason` -- the gate refusing this manifest as written;
      * `rejection_reason_laundered` -- the gate refusing a copy that has been made to look as much
        like a publication product as possible (publication schema and label, marker stripped from
        every path, quarantine directory rewritten). If that copy passed, the marker would be doing
        the work and the physics would not be, and this builder dies instead of writing.
    """
    dev, num, den, R = measured_fold_forward_dev(weights_npz)
    tol, tol_src = _frozen_tolerance()

    manifest = {
        "schema": DIAGNOSTIC_SCHEMA,
        "label": DIAGNOSTIC_LABEL,
        "purpose": ("first exercise of the full-event extractor on real input. Diagnostic only: the "
                    "fold-forward deficit is unrepaired, so this cross section is knowingly low by "
                    "~34%. Branch C of PREDECLARATION-20260808-gate4-and-d2-fraction.md governs -- "
                    "no product is quoted while any leg is red."),
        "job_id": job_id,
        "manifest_path": os.path.abspath(out_path),
        "xsec_path": os.path.abspath(xsec_npz),
        "push_path": os.path.abspath(push_npz),
        "xsec_summary_path": os.path.abspath(xsec_summary),
        "weights_path": os.path.abspath(weights_npz),
        "inputs_path": os.path.abspath(inputs_npz),
        "xsec_sha256": _sha256_file(xsec_npz),
        "push_sha256": _sha256_file(push_npz),
        "weights_sha256": _sha256_file(weights_npz),
        "inputs_sha256": _sha256_file(inputs_npz),
        "fold_forward": {
            "sum_w_push_reco": num,
            "sum_w_reco": den,
            "reco_weighted_mean_push": (num / den) if den else None,
            "R": R,
            "deviation": dev,
            "tolerance": tol,
            "tolerance_source": tol_src,
            "exceeds_tolerance_by": (dev / tol) if tol else None,
            "recomputed_from": "the weights artifact, not from any report or summary",
        },
    }
    if extra:
        manifest.update(extra)

    manifest["rejection_reason"] = _assert_rejects(manifest, weights_npz, "this manifest as written")

    laundered = json.loads(json.dumps(manifest))
    laundered["schema"] = PUBLICATION_SCHEMA
    laundered["label"] = PUBLICATION_LABEL
    for key in ("xsec_path", "push_path", "manifest_path", "xsec_summary_path"):
        laundered[key] = (str(laundered.get(key) or "")
                          .replace(QUARANTINE_DIRNAME, "fullevent_nominal")
                          .replace(FILENAME_MARKER + ".", "")
                          .replace(FILENAME_MARKER, ""))
    manifest["rejection_reason_laundered"] = _assert_rejects(
        laundered, weights_npz,
        "a LAUNDERED copy (publication schema+label, marker stripped, quarantine path rewritten)")
    manifest["publication_gate_rejects_this"] = True
    manifest["publication_gate_rejects_this_on_physics_alone"] = True

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    if os.path.exists(out_path):
        os.chmod(out_path, 0o644)
    with open(out_path, "w") as fh:
        json.dump(manifest, fh, indent=2, default=str)
        fh.write("\n")
    os.chmod(out_path, 0o444)

    print(f"[quarantine] wrote {out_path} (read-only)  label={DIAGNOSTIC_LABEL}")
    print(f"[quarantine] fold-forward dev {dev:.6f} > tol {tol:g} by {dev / tol:.1f}x "
          f"({tol_src}) -> NOT QUOTABLE on the physics alone")
    print(f"[quarantine] gate rejects as-written: {manifest['rejection_reason'][:96]}...")
    print(f"[quarantine] gate rejects LAUNDERED : {manifest['rejection_reason_laundered'][:96]}...")
    return manifest
