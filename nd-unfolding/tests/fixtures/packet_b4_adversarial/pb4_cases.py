#!/usr/bin/env python3
"""Packet PB4 adversarial cases — component-manifest variants and an output collector.

Authored by the oversight session, independent of the PB4 fix, per Packet B constraint 3.

FORM, and why it differs from PB1/PB2/PB3
-----------------------------------------
PB4's inputs are component manifests, which reference scratch paths and ROOT sha256s -- stable,
unlike PB2's repo blobs -- so they can be static. But half of what PB4 asserts is about OUTPUTS
(does the projected manifest carry the marker, does the projected ROOT carry it, does a consumer
refuse). Those are observations, not inputs.

So this ships two modes:
    --emit-variants   writes the input component-manifest variants
    --collect         dumps a normalised observation record of what a projection produced

The fix author asked to stay blind on which cases accept and which reject, so this deliberately
contains NO expected outcomes. It observes and reports; the oversight session holds the key and
judges the dump. A checker with expectations inside it could not be blind.

THE DEFECT, per the author's reading (which corrects the verdict's phrasing)
---------------------------------------------------------------------------
`p4_project_4d.py` greps clean for `component_manifest`, `publication_gate_rejects_this` and
`NON_ADOPTABLE`. The projector has never read the component manifest, so the marker is not dropped
in transit -- it is never fetched. A missing INPUT, not a missing copy.

Usage:
    python3 pb4_cases.py --emit-variants --real <std_component_manifest.json> --out <dir>
    python3 pb4_cases.py --collect --proj-manifest <path> --proj-root-keys <path-or-'-'> \
                         --adopter-rc <int> --variant <L..Q> [--sidecar-present 0|1]
"""
import argparse, copy, hashlib, json, sys
from pathlib import Path

MARKER = "publication_gate_rejects_this"

# Variant ids are opaque on purpose. What each perturbs is stated; what each SHOULD produce is not.
VARIANTS = {
    "L": "parent manifest carries the marker as written by the builder (unmodified)",
    "M": f"parent manifest sets {MARKER} to false explicitly",
    "N": "no component manifest beside the candidate at all (delete it before projecting)",
    "O": f"parent manifest present, marker true, but candidate_sha256 names a DIFFERENT candidate",
    "P": f"parent manifest omits the {MARKER} key entirely -- the field is absent, not false",
    "Q": "post-projection: project from the L parent, then DELETE the projected sidecar manifest, "
         "leaving only the projected ROOT. Tests whether the ROOT-side copy is load-bearing.",
}


def emit(real_path: Path, outdir: Path) -> None:
    real = json.loads(real_path.read_text())
    outdir.mkdir(parents=True, exist_ok=True)
    written = []

    def put(vid, obj):
        p = outdir / f"std_component_manifest.PB4_{vid}.json"
        obj = copy.deepcopy(obj)
        obj["_fixture"] = {
            "packet": "PB4", "variant": vid,
            "authored_by": "oversight session (independent of the fix)",
            "perturbation": VARIANTS[vid],
            "expected_outcome": "WITHHELD",
        }
        p.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        written.append((vid, p.name, sha))

    # L -- unmodified. Marker present and true, as the builder writes it.
    assert real.get(MARKER) is True, f"real manifest does not carry {MARKER}=true; check the source"
    put("L", real)

    # M -- explicitly false. A genuinely clean parent.
    m = copy.deepcopy(real); m[MARKER] = False
    m.pop("non_adoptable_reason", None)
    put("M", m)

    # N -- no file. Emitted as a marker file only; the operator deletes the manifest before running.
    (outdir / "PB4_N.DELETE_THE_MANIFEST").write_text(
        "PB4_N: run the projection with NO std_component_manifest.json beside the candidate.\n"
        "There is no JSON to supply for this variant; its content is the file's absence.\n")
    written.append(("N", "PB4_N.DELETE_THE_MANIFEST", "n/a"))

    # O -- marker true, but the manifest describes a different candidate.
    o = copy.deepcopy(real)
    o["candidate_sha256"] = hashlib.sha256(b"a different candidate entirely").hexdigest()
    put("O", o)

    # P -- the key is ABSENT rather than false. Distinct from M: an older manifest predating the
    # convention looks exactly like this, which is KNOWN_ISSUES #24's shape one level down.
    p = copy.deepcopy(real); p.pop(MARKER, None); p.pop("non_adoptable_reason", None)
    put("P", p)

    # Q -- no input variant; a post-projection manipulation. Recorded for completeness.
    (outdir / "PB4_Q.POST_PROJECTION").write_text(
        "PB4_Q: project from the PB4_L parent, then delete the projected sidecar manifest,\n"
        "leaving only the projected ROOT. Then run the consumer. Reported via --collect with\n"
        "--sidecar-present 0.\n")
    written.append(("Q", "PB4_Q.POST_PROJECTION", "n/a"))

    print(f"{'variant':8s} {'file':52s} sha256")
    for vid, name, sha in written:
        print(f"{vid:8s} {name:52s} {sha[:16] if sha != 'n/a' else 'n/a'}")
    print("\nexpected outcomes are WITHHELD -- report observations via --collect and the oversight "
          "session judges against its key")


def collect(a) -> None:
    """Dump a normalised observation. No judgement -- that is deliberate."""
    obs = {"variant": a.variant, "perturbation": VARIANTS.get(a.variant, "?")}

    if a.proj_manifest and a.proj_manifest != "-" and Path(a.proj_manifest).exists():
        man = json.loads(Path(a.proj_manifest).read_text())
        obs["projected_manifest"] = {
            "present": True,
            "marker_key_present": MARKER in man,
            "marker_value": man.get(MARKER, None),
            "records_parent_sha": man.get("candidate_sha256") or man.get("parent_candidate_sha256"),
            "has_reason_field": "non_adoptable_reason" in man,
        }
    else:
        obs["projected_manifest"] = {"present": False}

    if a.proj_root_keys and a.proj_root_keys != "-" and Path(a.proj_root_keys).exists():
        keys = [k.strip() for k in Path(a.proj_root_keys).read_text().splitlines() if k.strip()]
        marker_keys = [k for k in keys
                       if MARKER in k or "NON_ADOPTABLE" in k.upper() or "REJECT" in k.upper()]
        obs["projected_root"] = {"n_keys": len(keys), "marker_bearing_keys": marker_keys}
    else:
        obs["projected_root"] = {"keys_supplied": False}

    obs["projection_refused"] = (a.proj_manifest in (None, "-")
                                 or not Path(str(a.proj_manifest)).exists())
    obs["adopter_rc"] = a.adopter_rc
    obs["adopter_refused"] = (a.adopter_rc != 0) if a.adopter_rc is not None else None
    obs["sidecar_present_at_consume"] = (None if a.sidecar_present is None
                                         else bool(a.sidecar_present))

    print(json.dumps(obs, indent=2, sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-variants", action="store_true")
    ap.add_argument("--real")
    ap.add_argument("--out")
    ap.add_argument("--collect", action="store_true")
    ap.add_argument("--variant")
    ap.add_argument("--proj-manifest")
    ap.add_argument("--proj-root-keys", help="file with one ROOT key per line, or '-'")
    ap.add_argument("--adopter-rc", type=int)
    ap.add_argument("--sidecar-present", type=int, choices=(0, 1))
    a = ap.parse_args()

    if a.emit_variants:
        if not (a.real and a.out):
            ap.error("--emit-variants needs --real and --out")
        emit(Path(a.real), Path(a.out))
    elif a.collect:
        if not a.variant:
            ap.error("--collect needs --variant")
        collect(a)
    else:
        ap.error("pick --emit-variants or --collect")
    return 0


if __name__ == "__main__":
    sys.exit(main())
