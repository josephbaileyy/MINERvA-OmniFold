"""The measured leg's size, in one place and with the scope it may not be quoted without.

Two modules need this number -- `training_recipe` derives the example budget from
it and `calibrate_cost` turns that budget into GPU-hours -- and it must not exist
twice. `calibrate_cost` also has to import it WITHOUT importing TensorFlow, which
is why this is its own module rather than a constant inside the recipe: the recipe
imports TF at module level to build optimizers, and the cost driver chooses its
Keras backend before TF is loaded.

The value is a reading, not an estimate. What makes it conditional is not its
precision but its PROVENANCE: it is the data leg of the five-dimensional
point-cloud OmniFold input, and this campaign runs the fullevent schema, whose
data leg has never been dumped at scale.
"""

from __future__ import annotations

# `nd-unfolding/products/pet/bkgsub/of_inputs_pc_fullcloud_bkgsub_5d.provenance.json`
# records it three independent ways -- `n_data_expected`,
# `data_alignment_gate.n_rows_extracted` (exact, 0 mismatched rows against its
# reference) and `weight_gate.n` -- all 4,091,707.
MEASURED_DATA_LEG_ROWS = 4_091_707

DATA_LEG_EVIDENCE = {
    "rows": MEASURED_DATA_LEG_ROWS,
    "source": ("nd-unfolding/products/pet/bkgsub/"
               "of_inputs_pc_fullcloud_bkgsub_5d.provenance.json"),
    "fields": ("n_data_expected, corroborated independently by "
               "data_alignment_gate.n_rows_extracted (exact, 0 mismatches) and "
               "weight_gate.n"),
    "source_root": "runEventLoopOmniFold_PC_MEFHC_fullcloud.root",
    "scope": ("the FIVE-DIMENSIONAL point-cloud OmniFold input. This campaign runs "
              "the FULLEVENT schema, whose data leg has never been dumped at scale, "
              "so this is a neighbouring product's reading and not this one's"),
    "corroboration": ("the event-identity export counts 4,119,797 rows in the data "
                      "tree, 0.7 % above this product's post-gate count, which is "
                      "the direction and roughly the size a selection should move it"),
    "what_it_changes": ("n_data = n_mc = 2e6 gives 153.6 M presentations per "
                        "evaluation; n_data = 4.09e6 gives 193.8 M, a factor 1.26. "
                        "Every absolute GPU-hour figure inherits that factor; no "
                        "RATIO does"),
}


def data_leg_estimate() -> tuple[int, str]:
    """The measured leg's size and the scope it may never be quoted without."""
    return DATA_LEG_EVIDENCE["rows"], DATA_LEG_EVIDENCE["scope"]
