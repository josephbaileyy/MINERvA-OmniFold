#!/usr/bin/env python3
"""Synthetic N2 member: a numpy world with a known answer, for testing the harness only.

No OmniFold, no ROOT, no real input. Arm T member ``e`` returns ``m * (1 + sigma_T z_e)``; arm B
member ``r`` returns ``t_1 * (1 + b_over_t sigma_T z_r)`` around arm T's first set ``t_1``, so the
harness should find ``M`` near ``b_over_t``. Its sidecar lists the identities it "handed over":
the training fold as bank and background template, reservoir keys as pseudo-data. The world file
(``inputs.synthetic_world`` of a synthetic admission) can also name members to contaminate (one
reservoir key added to the bank) or to fail (exit 1 before writing).
"""

import argparse
import json
import sys
from pathlib import Path

_SELF_BYTES = Path(__file__).read_bytes()

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE.parent))

from n2 import design, execution as gx, identity, members as mb  # noqa: E402
from n2 import harness  # noqa: E402


def values(world, member):
    m = np.random.default_rng(world["mean_seed"]).uniform(1.0, 3.0, design.N_REPORTED_BINS)
    s = world["sigma_T"]
    t = lambda seed: m * (1 + s * np.random.default_rng(seed).standard_normal(m.size))
    if member["arm"] == "T":
        return t(member["data_seed"])
    z = np.random.default_rng(member["boot_seed"]).standard_normal(m.size)
    return t(member["data_seed"]) * (1 + world["b_over_t"] * s * z)


def main():
    ap = argparse.ArgumentParser()
    for name in ("--admission", "--member", "--plan-sha256", "--out"):
        ap.add_argument(name, required=True)
    ap.add_argument("--expect")
    ap.add_argument("--require-provenance", action="store_true")
    a = ap.parse_args()
    try:
        exp = gx.load_expectations(a.expect)
        records = [gx.file_record(__file__, _SELF_BYTES, REPO)] + [
            gx.bootstrap_record(sys.modules[n], REPO)
            for n in ("n2", "n2.execution", "n2.design", "n2.identity", "n2.members", "n2.harness")]
        prov = gx.finalize(REPO, records, exp, a.require_provenance)
        adm = harness.check_admission(a.admission)
        if not adm["synthetic"]:
            raise gx.ProvenanceRefusal("the synthetic producer refuses a real admission")
        if a.require_provenance and "split_manifest" not in exp["inputs"]:
            raise gx.ProvenanceRefusal("strict provenance needs the split manifest's digest")
        inputs = {"split_manifest": gx.input_record(adm["inputs"]["split_manifest"]["path"],
                                                    exp["inputs"].get("split_manifest"))}
        gx.refuse_existing(a.out)
    except (gx.ProvenanceRefusal, harness.AdmissionError) as exc:
        print(f"[REFUSED] {exc}", file=sys.stderr)
        sys.exit(gx.REFUSAL_EXIT)
    member = json.loads(a.member)
    world = json.loads(Path(adm["inputs"]["synthetic_world"]["path"]).read_text())
    if member["id"] in world.get("fail", []):
        print(f"[synthetic] {member['id']} fails by design", file=sys.stderr)
        sys.exit(1)
    folds = identity.fold_keys(harness.load_fold_tables(adm["inputs"]["fold_tables"]["path"]))
    bank = sorted(folds["mc_signal_reco"]["training"])
    reservoir = sorted(folds["mc_signal_reco"]["reservoir"])
    if member["id"] in world.get("contaminate", []):
        bank = bank + reservoir[:1]
    sidecar = {"bank": bank, "background_template": sorted(folds["mc_background"]["training"]),
               "pseudo_data": reservoir}
    mb.write_new(a.out, json.dumps({
        "member": member["id"], "plan_sha256": a.plan_sha256, "spec": member,
        "estimator": member["estimator"], "values": values(world, member).tolist(),
        "sidecar": sidecar, "provenance": dict(gx.recheck(REPO, prov), inputs=inputs,
                                               environment=gx.environment_record())}))


if __name__ == "__main__":
    main()
