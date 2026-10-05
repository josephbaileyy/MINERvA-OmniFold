"""The R4 branch/source manifest, enumerated and committed BEFORE extraction.

Joseph authorized R4 on 2026-09-20: "read the enumerated 21 typed-object branches
and the precisely enumerated source branches needed for Gregor's event globals,
for the selected comparison inventories. Commit the branch/source manifest before
extraction."

So this file is the manifest, and it is machine-readable so the extractor can be
held to it rather than trusted against it. Two sets, kept apart because they were
authorized by different sentences and enumerated from different evidence:

* `TYPED_OBJECT_BRANCHES` -- the 21 from
  `EXTRACTION_IDENTITY_CONTRACT-20260918.md` §3, measured by
  `authorization_scope.typed_object_gap` as the set `REQUIRED_BRANCHES` lacks.
* `GLOBAL_SOURCE_BRANCHES` -- read out of Gregor's own preprocessing, function by
  function, because they were never enumerated anywhere. Each entry records WHICH
  of his 16 conditioning columns it feeds, so a reader can check the count rather
  than take it.

**His 16 globals decompose as 10 + 6**, and the 10 as 7 + 3:

    get_global_features            -> 7  (log muon_fuzz, log muon_iso_blobs,
                                          log hadron_recoil, log passive_id,
                                          log passive_od, log passive_sum,
                                          improved_nmichel)
    compute_extra_global_features  -> 3  (muon present 0/1, diphoton invariant
                                          mass, charged-pion prong count)
    energy sums per PID            -> 6  (log sum E over pid in 2,3,4,5,6,7)
                                    = 16 = GLOBAL_COND_BASE_DIM(10) + e_sum_dim(6)

`cond_dim = args.ol_num_cond + e_sum_dim` at `src/scripts/train.py:1081`, with
`--ol-num-cond` defaulting to 10 and `e_sum_dim = 6 if args.include_E_sum`. That
is the arithmetic behind the 16 the freeze pins, and it is now derived rather
than asserted.

The six energy sums need NO new branch: they are sums over the typed objects'
own energy and PID, which the 21 already cover.

NOT AN AUTHORIZATION BY ITSELF. This enumerates what R4 covers; it does not
enlarge it, and `authorization_scope.py` remains the enforcement.
"""

from __future__ import annotations

from typing import Any

# EXTRACTION_IDENTITY_CONTRACT-20260918.md §3, from `typed_object_gap`.
TYPED_OBJECT_BRANCHES: tuple[str, ...] = (
    "MasterAnaDev_BlobIs3D",
    "MasterAnaDev_BlobNClusters",
    "MasterAnaDev_BlobT",
    "MasterAnaDev_BlobTPos",
    "MasterAnaDev_BlobTotalE",
    "MasterAnaDev_BlobX",
    "MasterAnaDev_BlobY",
    "MasterAnaDev_BlobZ",
    "gamma1_dEdx",
    "gamma1_direction",
    "gamma1_time",
    "gamma2_dEdx",
    "gamma2_direction",
    "gamma2_time",
    "prong_dEdXMean",
    "prong_part_E",
    "prong_part_charge",
    "prong_part_mass",
    "prong_part_pid",
    "prong_part_pos",
    "prong_part_score",
)

# Read from `gregorkrz/minerva-ml` at fc9a099d, file by file. `feeds` names the
# conditioning column(s) each branch supports; `via` is the function that reads it.
GLOBAL_SOURCE_BRANCHES: dict[str, dict[str, Any]] = {
    "muon_fuzz_energy": {
        "via": "src/dataset/preprocessing.py:get_global_features",
        "feeds": ["global[0] = log(muon_fuzz_energy + 1e-5), negatives clipped to 0"],
    },
    "muon_iso_blobs_energy": {
        "via": "src/dataset/preprocessing.py:get_global_features",
        "feeds": ["global[1] = log(muon_iso_blobs_energy + 1e-5), negatives clipped"],
    },
    "MasterAnaDev_hadron_recoil": {
        "via": "src/dataset/preprocessing.py:get_global_features",
        "feeds": ["global[2] = log(E_recoil + 1e-5), negatives clipped"],
    },
    "part_response_total_recoil_passive_allNonMuonClusters_id": {
        "via": "src/dataset/preprocessing.py:get_global_features",
        "feeds": ["global[3] = log(id/10000 + 1e-3)",
                  "global[5] = log((id + od)/10000 + 1e-3)"],
    },
    "part_response_total_recoil_passive_allNonMuonClusters_od": {
        "via": "src/dataset/preprocessing.py:get_global_features",
        "feeds": ["global[4] = log(od/10000 + 1e-3)",
                  "global[5] = log((id + od)/10000 + 1e-3)"],
    },
    "improved_nmichel": {
        "via": "src/dataset/preprocessing.py:get_global_features",
        "feeds": ["global[6] = N_michel, unscaled"],
    },
    "gamma1_E": {"via": "src/dataset/preprocessing.py:get_photons",
                 "feeds": ["global[8] = diphoton invariant mass when exactly 2 reco photons"]},
    "gamma1_px": {"via": "get_photons", "feeds": ["global[8]"]},
    "gamma1_py": {"via": "get_photons", "feeds": ["global[8]"]},
    "gamma1_pz": {"via": "get_photons", "feeds": ["global[8]"]},
    "gamma2_E": {"via": "get_photons", "feeds": ["global[8]"]},
    "gamma2_px": {"via": "get_photons", "feeds": ["global[8]"]},
    "gamma2_py": {"via": "get_photons", "feeds": ["global[8]"]},
    "gamma2_pz": {"via": "get_photons", "feeds": ["global[8]"]},
}

# `compute_extra_global_features` also needs the MINOS-matched muon COUNT for
# global[7], and the charged-pion prong count for global[9]. The prong count comes
# from `prong_part_pid`, already in the typed set. The muon count comes from
# `get_muons(..., only_keep_minos_matched=True)`, whose reads are listed here so
# the manifest is complete even though only the COUNT is used.
MUON_COUNT_SOURCE_BRANCHES: tuple[str, ...] = (
    "MasterAnaDev_muon_E", "MasterAnaDev_muon_Px", "MasterAnaDev_muon_Py",
    "MasterAnaDev_muon_Pz", "muon_corrected_p", "muon_phi", "muon_theta",
    "muon_thetaX", "muon_thetaY", "muon_trackVertexTime", "truth_reco_has_muon",
)

GLOBAL_COLUMNS: tuple[str, ...] = (
    "log muon_fuzz_energy", "log muon_iso_blobs_energy", "log hadron_recoil",
    "log passive_id", "log passive_od", "log passive_sum", "improved_nmichel",
    "muon_present_0_or_1", "diphoton_invariant_mass", "charged_pion_prong_count",
    "log sum E pid=2 (blob)", "log sum E pid=3 (prong 3)",
    "log sum E pid=4 (prong 8)", "log sum E pid=5 (prong 13)",
    "log sum E pid=6 (agg blob)", "log sum E pid=7 (agg prong)",
)

ENERGY_SUM_PIDS: tuple[int, ...] = (2, 3, 4, 5, 6, 7)

# HIS OWN KEY LISTS, read from `src/dataset/preprocessing.py:836-859`, so that
# what we build can be compared against what he builds rather than against our
# reading of his paper.
HIS_PRONG_KEYS: tuple[str, ...] = (
    "prong_part_pos", "prong_part_E", "prong_part_score", "prong_part_mass",
    "prong_part_charge", "prong_part_pid", "prong_part_dEdXMean",
)
HIS_BLOB_KEYS: tuple[str, ...] = (
    "MasterAnaDev_BlobX", "MasterAnaDev_BlobY", "MasterAnaDev_BlobZ",
    "MasterAnaDev_BlobT", "MasterAnaDev_BlobTPos", "MasterAnaDev_BlobTotalE",
)

# ONE OF HIS KEYS DOES NOT EXIST IN OUR TUPLES, measured 2026-09-20 against
# MasterAnaDev_mc_AnaTuple_run00110000_Playlist.root:
#
#     prong_part_dEdXMean   ABSENT
#     prong_dEdXMean        PRESENT
#
# The extraction contract's 21-branch enumeration had the right name; his key
# list does not match this tuple vintage. So his preprocessing cannot be
# reproduced verbatim on our data for that one column, and the substitution is a
# CONFIGURATION DIFFERENCE to declare rather than a detail to paper over: either
# `prong_dEdXMean` is the same quantity renamed, which we have not established,
# or the column differs.
HIS_KEY_NOT_IN_OUR_TUPLES = "prong_part_dEdXMean"
OUR_SUBSTITUTE = "prong_dEdXMean"
SUBSTITUTION_STATUS = (
    "DECLARED, NOT VERIFIED. The two names have not been shown to carry the same "
    "quantity. Until they are, his arm built on our tuples differs from his arm "
    "built on his in exactly this column, and any recommendation must say so"
)

# Two branches the contract enumerates are NOT in his key lists at all:
# `MasterAnaDev_BlobIs3D` and `MasterAnaDev_BlobNClusters`. They are available
# and he does not use them, so his arm does not get them either.
IN_OUR_MANIFEST_BUT_NOT_HIS = ("MasterAnaDev_BlobIs3D", "MasterAnaDev_BlobNClusters")

INVENTORIES: tuple[str, ...] = ("mc_signal_reco", "mc_background", "data")

SYMMETRY_REQUIREMENT = (
    "every branch in this manifest is read for EVERY inventory in `INVENTORIES`, "
    "or for none. Reading a global for signal and not for background would make "
    "the arms' inputs differ by inventory, and the difference would look like a "
    "physics effect"
)

PRESERVATION_REQUIREMENT = (
    "selection, weights and event identity are carried through unchanged: the "
    "extraction adds columns to the existing row set and never re-selects. Row "
    "order is the inventory's, bound by the identity sidecar's order hash"
)


def manifest() -> dict[str, Any]:
    """The whole manifest, for a receipt."""
    return {
        "authorized": "R4, Joseph 2026-09-20",
        "typed_object_branches": list(TYPED_OBJECT_BRANCHES),
        "typed_object_count": len(TYPED_OBJECT_BRANCHES),
        "global_source_branches": GLOBAL_SOURCE_BRANCHES,
        "global_source_count": len(GLOBAL_SOURCE_BRANCHES),
        "muon_count_source_branches": list(MUON_COUNT_SOURCE_BRANCHES),
        "global_columns": list(GLOBAL_COLUMNS),
        "global_column_count": len(GLOBAL_COLUMNS),
        "energy_sum_pids": list(ENERGY_SUM_PIDS),
        "inventories": list(INVENTORIES),
        "symmetry_requirement": SYMMETRY_REQUIREMENT,
        "preservation_requirement": PRESERVATION_REQUIREMENT,
        "derivation": (
            "cond_dim = ol_num_cond (default 10) + e_sum_dim (6 if include_E_sum) "
            "= 16, from src/scripts/train.py:1081 and :871-874; the 10 is "
            "GLOBAL_COND_BASE_DIM at src/constants/dataset.py:5, decomposing as "
            "7 from get_global_features and 3 from compute_extra_global_features"
        ),
    }


def total_new_branches() -> int:
    """How many branches R4 actually opens, counted once each."""
    return len(set(TYPED_OBJECT_BRANCHES)
               | set(GLOBAL_SOURCE_BRANCHES)
               | set(MUON_COUNT_SOURCE_BRANCHES))
