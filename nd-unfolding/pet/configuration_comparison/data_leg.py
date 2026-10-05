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

# MEASURED ON THE FULLEVENT SCHEMA, 2026-09-19. `G2_FPS_MEFHC_P12_RECEIPT.json`
# (sha256 d466a0c1...29d25e), the production dump's own receipt, records
# `inventory_rows.data = 4,116,128`, and the loader uses that leg in full:
# `fullevent_fps_dataloader.py:486,494` states "data; all rows pass_reco", so no
# further selection reduces it.
#
# This REPLACES the neighbouring 5-D point-cloud product's 4,091,707, which is kept
# below only as the corroboration it turned out to be -- it was 0.6 % low, which is
# about the right size for a different product's gate.
MEASURED_DATA_LEG_ROWS = 4_116_128
NEIGHBOURING_PRODUCT_ROWS = 4_091_707

DATA_LEG_EVIDENCE = {
    "rows": MEASURED_DATA_LEG_ROWS,
    "source": ("/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/"
               "G2_FPS_MEFHC_P12_RECEIPT.json"),
    "source_sha256": "d466a0c18deaafa2ae645002c8dbc9b9879476adb45a40a85c0bae9e0129d25e",
    "fields": "inventory_rows.data",
    "companion_rows": {"signal": 49_152_885, "background": 564_591},
    "scope": ("the FULLEVENT schema this campaign runs -- the production dump's own "
              "receipt, not a neighbouring product. The loader consumes the leg in "
              "full: `fullevent_fps_dataloader.py:486,494` states \"data; all rows "
              "pass_reco\", so no later selection reduces it"),
    "corroboration": (
        "three independent readings within 0.6 %: this dump's 4,116,128; the 5-D "
        "point-cloud product's 4,091,707 (a different product, post-gate); and the "
        "event-identity export's 4,119,797 raw rows in the data tree. The ordering "
        "raw > this dump > 5-D gate is the direction selections should move it"),
    "supersedes": ("the 5-D point-cloud reading of 4,091,707, which was carried as a "
                   "narrowing of the caveat and is now replaced by a measurement of "
                   "the right schema"),
    "what_it_changes": ("n_data = n_mc = 2e6 gives 153.6 M presentations per "
                        "evaluation; n_data = 4,116,128 gives 194.2 M, a factor "
                        "1.2645. Every absolute GPU-hour figure inherits that "
                        "factor; no RATIO does"),
}


def data_leg_estimate() -> tuple[int, str]:
    """The measured leg's size and the scope it may never be quoted without."""
    return DATA_LEG_EVIDENCE["rows"], DATA_LEG_EVIDENCE["scope"]
