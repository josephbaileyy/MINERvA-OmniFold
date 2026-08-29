#!/usr/bin/env python3
"""Render the hash-bound proposal for the authorized Gate-6 GAP 1 run."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "docs/orchestration/state/gate6-full-inventory-proposal-20260830.json"
SOURCES = (
    "nd-unfolding/mnv_guarded_run.py",
    "nd-unfolding/pet/extract_fullevent_fps.py",
    "nd-unfolding/pet/fullevent_fps_dataloader.py",
    "nd-unfolding/pet/gate6_full_inventory_root_remap.py",
    "nd-unfolding/pet/submit_gate6_full_inventory_members.sh",
)
MEMBER_HASHES = [
    "3e08850d44f773bb50f5cb132a7a1d4d672e0ab15f1d38d785a4eddbf5179b2e",
    "5b8e129f9dba90659ed0fc17f322499ea41fea505add57ab957ad209152f1c13",
    "f6087581e320d1bfce1a968e62c737d8fac346dedb94836f7fe173980a5b55e8",
    "04759d0a07f120bda112b87222b0a91fd0e98a2ce402be12d37f30d06a2a0bfd",
    "4120a5483255847e9dceb79dc5796dd820fca419cfba8adddabc42924d82eff1",
]
PROHIBITIONS = [
    "do_not_select_passing_subset",
    "do_not_construct_C_ML",
    "do_not_move_central",
    "do_not_start_leg_2",
    "do_not_retry_unchanged",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_proposal() -> dict:
    return {
        "schema": "gate6-gap1-full-inventory-proposal-v1",
        "contract_id": "GATE6-GAP1-FULL-INVENTORY-20260830",
        "status": "AUTHORIZED_CONDITIONAL_READY",
        "launchable": True,
        "authorization": {
            "authorized_by": "Joseph",
            "authorized_on": "2026-08-30",
            "authorization_source": "Joseph's explicit GAP 1 conditional authorization in the active task",
            "exactly_five_evaluations": True,
            "no_retraining": True,
            "a100_hour_ceiling": 5.0,
            "unchanged_retry_authorized": False,
        },
        "measurement": {
            "input_rows": 49_152_885,
            "pass_truth_rows": 49_150_928,
            "members": 5,
            "inference_rows_total": 245_764_425,
            "quantity": "like-for-like full-inventory member normalization and extended-FPS spectra",
        },
        "input": {
            "relative_path": "nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz",
            "bytes": 9_897_374_636,
            "sha256": "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625",
        },
        "member_artifacts": [
            {
                "member": member,
                "relative_path": (
                    "nd-unfolding/pet/fullevent_ml_ensemble/"
                    f"member_{member}/pet_fullevent_ml_member{member}_weights.npz"
                ),
                "sha256": digest,
                "training_indices": 2_000_000,
            }
            for member, digest in enumerate(MEMBER_HASHES, 1)
        ],
        "source_hashes": {name: sha256(REPO / name) for name in SOURCES},
        "resources": {
            "gpu_array": "1-5%5",
            "gpus_per_task": 1,
            "gpu_wall_hours_per_task": 1,
            "allocated_a100_hours": 5.0,
            "historical_expected_a100_hours": 1.21,
            "historical_observed_max_envelope_a100_hours": 1.54,
            "cpu_array": "1-5%5",
            "cpu_only": True,
        },
        "prohibitions_applied": {key: True for key in PROHIBITIONS},
        "cannot_authorize": [
            "a member re-verdict or selection of a passing subset",
            "construction of C_ML",
            "movement or replacement of the central value",
            "Leg 2",
            "an unchanged retry or any additional compute",
            "a publication claim",
        ],
        "C_ML": None,
        "publication_result": False,
    }


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(build_proposal(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
