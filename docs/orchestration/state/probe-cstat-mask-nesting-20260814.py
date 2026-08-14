"""Is the PET reported mask NESTED inside the canonical FPS mask? Settled by set containment.

C's spec (REQUIREMENTS-20260814 sec 0.1) records 262 vs 266 as an unresolved discrepancy:
"consistent with the PET mask being the FPS mask minus 4 more, but I have not verified nesting
because the PET mask's indices are not recorded in any artifact."

They are now -- state/pet-nominal-reported-cells-20260814.json, measured off the nominal product.
Both masks are 285-cell, C-order (pt-major), so the indices are directly comparable.
"""
import json
import pathlib

R = pathlib.Path("/Users/josephbailey/local-research/MINERvA-OmniFold/.claude/worktrees/lane-d")

fps = json.loads((R / "nd-unfolding/active_universe_5d/fps/covariance/"
                  "fps_reported_mask.json").read_text())
pet = json.loads((R / "docs/orchestration/state/"
                  "pet-nominal-reported-cells-20260814.json").read_text())

assert fps["ravel_order"] == "C", fps["ravel_order"]
assert fps["n_total"] == pet["grid"]["n_cells"] == 285

F = set(fps["reported_indices"])                       # 266 reported
P = set(range(285)) - set(pet["zero_cells_flat_indices"])   # 262 reported
NPP = pet["grid"]["n_pparallel_bins"]

print(f"FPS reported : {len(F)} / 285   (zeros {285 - len(F)})")
print(f"PET reported : {len(P)} / 285   (zeros {285 - len(P)})")


def cells(s):
    return sorted((i // NPP, i % NPP) for i in s)


print(f"\nPET subset of FPS?  {P <= F}")
print(f"FPS subset of PET?  {F <= P}")
print(f"\nin FPS but NOT PET ({len(F - P)}): {cells(F - P)}")
print(f"in PET but NOT FPS ({len(P - F)}): {cells(P - F)}")
print(f"reported by neither ({len(set(range(285)) - F - P)}): "
      f"{cells(set(range(285)) - F - P)}")

nested = P <= F
print(f"\n=== NESTED: {nested} ===")
if nested:
    print(f"The PET reported set is the FPS set minus exactly {len(F - P)} cells.")
    print("C's inference was right, and it is now verified rather than consistent-with.")
else:
    print("NOT nested -- the two masks disagree in BOTH directions. Adopting either as the")
    print("common mask silently changes the reported domain relative to the other.")

out = {
    "what": "is the PET reported mask nested inside the canonical FPS mask?",
    "question_from": "REQUIREMENTS-20260814-cstat-assembly-conventions.md sec 0.1 (lane C)",
    "fps_mask": {"source": "nd-unfolding/active_universe_5d/fps/covariance/fps_reported_mask.json",
                 "n_reported": len(F), "fingerprint": fps["fingerprint"],
                 "ravel_order": fps["ravel_order"]},
    "pet_mask": {"source": "docs/orchestration/state/pet-nominal-reported-cells-20260814.json",
                 "n_reported": len(P),
                 "note": "derived as (xsec > 0) on the only committed PET full-event extraction, "
                         "a NONQUOTABLE-DIAGNOSTIC; nominal, and the mask is drawn per replica"},
    "pet_is_subset_of_fps": bool(P <= F),
    "fps_is_subset_of_pet": bool(F <= P),
    "in_fps_not_pet": {"n": len(F - P), "cells_i_pt_i_pp": cells(F - P)},
    "in_pet_not_fps": {"n": len(P - F), "cells_i_pt_i_pp": cells(P - F)},
    "reported_by_neither": {"n": len(set(range(285)) - F - P),
                            "cells_i_pt_i_pp": cells(set(range(285)) - F - P)},
    "verdict": "NESTED" if nested else "NOT NESTED -- masks disagree in both directions",
}
print("\n<<<RECEIPT_JSON>>>")
print(json.dumps(out, indent=1, sort_keys=True))
