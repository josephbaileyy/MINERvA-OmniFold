"""The frozen comparison design, machine-readable, fixed BEFORE comparative results.

Item 13 requires arm identities, checkpoint/input/code hashes, preprocessing,
caps, training recipes, tuning grids, event splits, seeds, endpoints, regional
definitions, thresholds, inference and stopping rules frozen before anything
comparative is measured. Freezing them in prose alone has failed in this lane
before -- a threshold that lives only in a document gets re-read differently --
so they live here, with tests, and the document quotes this file.

Nothing here is a result. Every number is either ratified policy (Joseph,
2026-09-20), a measured input pinned by hash, or a derived quantity whose
derivation is stated.
"""

from __future__ import annotations

from typing import Any

# --------------------------------------------------------------------------- #
# Arms
# --------------------------------------------------------------------------- #
OURS_INCUMBENT = {
    "name": "ours_incumbent",
    "role": "PROMOTED_INCUMBENT",
    "architecture": "vendored omnifold.net.PET",
    "num_heads": 2, "num_transformer": 2, "projection_dim": 32, "K": 3,
    "token_cap": 12,
    "batch_size": 512,
    "optimizer": "engine Adam with the annealed policy",
    "initialization": "scratch, per-seed",
}

THEIRS_COMPLETE = {
    "name": "theirs_complete",
    "role": "CANDIDATE",
    "architecture": "OmniLearned PET2, preset small",
    "use_int": False, "local_int": False,          # the V1-paper flags
    "input_dim": 4, "pid": True, "pid_dim": 8,
    "add_info": True, "add_dim": 5,
    "conditional": True, "cond_dim": 16,
    "num_coord": 2, "K": 10, "num_classes": 1,
    "token_cap": 33,
    "batch_size": 2048,
    "optimizer": "TorchAdamW(1e-4, wd 0.01) + warmup/cosine + global-norm clip 1.0",
    "initialization": "best_model_pretrain_s.pt via load_pretrained_omnilearned",
}

# --------------------------------------------------------------------------- #
# Hashes. An arm without these is not the arm that was frozen.
# --------------------------------------------------------------------------- #
PINNED_HASHES = {
    "checkpoint_best_model_pretrain_s.pt":
        "7e8331b0953303502fcc64461e8e2332a7582184c8e3592db2e27d752612b1bc",
    "pretrained_state_npz":
        "2480f269064b4d69f323d8681acc776526cec20a89e7cea8c2338004551231b5",
    "inventory_receipt_G2_FPS_MEFHC_P12":
        "d466a0c18deaafa2ae645002c8dbc9b9879476adb45a40a85c0bae9e0129d25e",
    "identity_sidecar":
        "01e07412b253ff496c30025cc71a9185b166a00892b1e1b4c8bce714ddd5f95c",
    "order_hash_module_fullevent_fps_dataloader":
        "e1402370cdb8bd63",       # prefix; the sidecar records the same
}

# --------------------------------------------------------------------------- #
# Execution path (F10, ratified as T2 on 2026-09-20)
# --------------------------------------------------------------------------- #
EXECUTION = {
    "flat_projection": True,
    "jit_compile": True,
    "precision_policy": {"tf32_enabled": False, "determinism_enabled": True,
                         "mixed_precision_policy": "float32", "floatx": "float32"},
    "device": "one A100-SXM4-40GB",
    "gradient_accumulation": "available at micro-batch 512; NOT required at 33/2048",
    "measured_peak_gib": 21.7,
    "measured_microseconds_per_example": 410.6,
    "measured_under": "tf32 disabled, determinism enabled, job 58586142",
}

# --------------------------------------------------------------------------- #
# Which step each arm differs at. Decided 2026-09-20; see
# THEIRS_TRUTH_SIDE-20260920.md for the three readings and why this one.
# --------------------------------------------------------------------------- #
#
# His complete arm is defined by a RECO-OBJECT vocabulary -- blobs, prongs,
# photons, a muon, with dE/dx, positions and times. Truth particles have none of
# those, so "his configuration at step 2" is not something his paper determines;
# his paper does not run OmniFold. The alternatives both invent something of his:
# putting truth particles through his schema needs a PDG-to-code map that exists
# nowhere in his repository, and running his backbone on our truth features
# changes his input width.
#
# So THE STEP-2 NETWORK IS IDENTICAL FOR BOTH ARMS -- the production PET on the
# production truth cloud -- and the arms differ only at step 1.
STEP_SCOPE = {
    "step1_reco": "the arms DIFFER: ours is the production cluster cloud, theirs "
                  "is the complete PET2-small arm over typed objects",
    "step2_gen": "the arms are IDENTICAL: the production PET on the production "
                 "truth cloud, same weights initialisation policy, same recipe",
    "what_the_comparison_therefore_means": (
        "a comparison of the RECO-SIDE representation and architecture, with the "
        "truth-side estimator held fixed"),
    "what_it_cannot_speak_to": (
        "his configuration's behaviour on the truth side, because that "
        "configuration does not exist -- his vocabulary has no truth analogue. "
        "Any recommendation states this limit in the conclusion, not a footnote"),
    "why_not_the_alternatives": (
        "reading B invents a PDG-to-code mapping he never defined; reading C "
        "changes his input width and so is not his configuration either"),
}

# --------------------------------------------------------------------------- #
# Endpoint and scoring
# --------------------------------------------------------------------------- #
ENDPOINT = {
    "injection": "truth E_avail, clipped exponential tilt",
    "amplitude": 0.35,
    "clip": 3.0,
    "primary_score": "seven-bin E_avail recovery",
    "bin_edges_gev": [0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0],
    "recovery": "fraction of the injected L1 displacement recovered; L1 = 2 x TV",
}

# --------------------------------------------------------------------------- #
# Thresholds, ratified 2026-09-20 as METHODOLOGICAL DECISION TOLERANCES for this
# comparison -- not as established physics facts.
# --------------------------------------------------------------------------- #
THRESHOLDS = {
    "adequacy_fraction_of_reference": 0.80,
    "non_inferiority_delta": 0.02,
    "switching_delta": 0.04,
    "regional_fraction_of_regional_reference": 0.60,
    "status": "ratified methodological tolerances, not physics facts",
    "report_when_theirs_better_but_retained": (
        "a result where his arm scores better and ours is retained under the "
        "switching policy is reported AS THAT, explicitly. Non-inferiority is "
        "not superiority"
    ),
}

# --------------------------------------------------------------------------- #
# Regions. Defined on the underlying reporting cells, never on the marginal.
# --------------------------------------------------------------------------- #
REGIONS = {
    "defined_on": "(pT, p_parallel) reporting cells, 15 x 19 = 285",
    "bands_by_cell_acceptance": [
        ["low_acceptance", 0.0, 0.05],
        ["poor", 0.05, 0.25],
        ["moderate", 0.25, 0.50],
        ["good", 0.50, 1.0000001],
    ],
    "scoreable_if_displacement_share_at_least": 0.02,
    "floor": "0.60 x THAT REGION's own reference, never a global one",
    "low_acceptance_handling": (
        "RETAINED in the analysis. Mass, injected displacement and each arm's "
        "recovery are reported separately. The acceptance reference is not an "
        "impossibility bound and these regions are not called unresolvable"
    ),
    "unscoreable_handling": (
        "a region carrying less than the displacement share is reported with its "
        "mass and displacement and is NOT gated, because a recovery fraction over "
        "negligible displacement is noise. The exempt mass is reported so the "
        "exemption is auditable"
    ),
}

# --------------------------------------------------------------------------- #
# Splits, seeds and the bounded tuning grid
# --------------------------------------------------------------------------- #
SPLITS = {
    "policy": "disjoint by event, assigned once from the frozen split seed",
    "split_seed": 20260920,
    "fractions": {"tuning": 0.20, "pilot": 0.20, "final": 0.60},
    "disjointness": "tuning ∩ pilot = tuning ∩ final = pilot ∩ final = empty",
    "assignment": (
        "by a hash of the event identity (source, run, subrun, gate, occurrence), "
        "so the same event lands in the same split for BOTH arms and across reruns"
    ),
}

SEEDS = {
    "tuning": [17, 29, 43, 59],
    "pilot": [71, 89, 101, 113],
    "final": [127, 139, 151, 163, 179, 191, 211, 223],
    "paired": "both arms use the SAME seed list; a pair shares its seed",
}

# One axis, four points, identical for both arms. A larger grid would give the
# arm with more hyperparameters an advantage that is not a property of the
# architecture, and the fairness axis is equal example presentations.
TUNING_GRID = {
    "axis": "base learning rate",
    "points": [5e-5, 1e-4, 2e-4, 4e-4],
    "same_for_both_arms": True,
    "selected_on": "the tuning split ONLY",
    "selection_statistic": "mean seven-bin E_avail recovery over the tuning seeds",
    "trials_per_arm": 4,
    "note": ("his reference learning rate 1e-4 is one of the four points, so the "
             "grid contains his published setting rather than only neighbours"),
}

# --------------------------------------------------------------------------- #
# Inference and stopping
# --------------------------------------------------------------------------- #
INFERENCE = {
    "statistic": "paired difference d = recovery(ours) - recovery(theirs), per seed",
    "interval": "two-sided t interval, n-1 degrees of freedom",
    "confidence": 0.95,
    "sizing": "n solved iteratively from the pilot's upper one-sided 80 % bound on sigma",
    "pilot_observations_in_final_inference": False,
    "pilot_exclusion_reason": (
        "the pilot chooses n. Reusing its observations in the interval that n was "
        "chosen for would make the interval conditional on its own width"
    ),
}

STOPPING_RULES = (
    "any port check fails => stop; the arm is not his configuration",
    "neither arm is eligible => NO_SELECTION, report both arms' failures",
    "the required n exceeds the remaining budget => report the comparison as "
    "underpowered at the frozen delta; do NOT widen delta",
    "a prerequisite artifact is missing => stop and hand off naming it; do not "
    "substitute a scratch arm for the pretrained one",
)

NOT_AUTHORIZED = (
    "publication adoption, covariance construction, systematic evaluation, "
    "central-value change, Gate-6 action, or sending anything to Ben. PET remains "
    "diagnostic method development, and nothing here discharges OI-71."
)


def frozen() -> dict[str, Any]:
    """The whole frozen design, for a receipt."""
    return {
        "frozen_on": "2026-09-20",
        "arms": {"ours": OURS_INCUMBENT, "theirs": THEIRS_COMPLETE},
        "step_scope": STEP_SCOPE,
        "pinned_hashes": PINNED_HASHES,
        "execution": EXECUTION,
        "endpoint": ENDPOINT,
        "thresholds": THRESHOLDS,
        "regions": REGIONS,
        "splits": SPLITS,
        "seeds": SEEDS,
        "tuning_grid": TUNING_GRID,
        "inference": INFERENCE,
        "stopping_rules": list(STOPPING_RULES),
        "not_authorized": NOT_AUTHORIZED,
    }
