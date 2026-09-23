"""Field names in the nominal-driver weights npz whose old names were misleading.

KNOWN_ISSUES #33. `train_fullevent_nominal.py` stored the loader's TARGET class ratio R under the
top-level key `step1_class_ratio`. That value is copied from the input, so it always equals R and says
nothing about what step 1 achieved; beside real measurements such as `cap_saturation_frac` it was
misread as one. From 2026-09-23 the driver writes it as `step1_class_ratio_target`. Artifacts written
earlier carry only the old key, so readers go through `step1_class_ratio_target()`, which accepts
either.

No numpy or TensorFlow import, so validators and tests can use it without either.
"""

STEP1_CLASS_RATIO_TARGET_KEY = "step1_class_ratio_target"
LEGACY_STEP1_CLASS_RATIO_KEY = "step1_class_ratio"


def step1_class_ratio_target_key(files):
    """Return the key an artifact stores the target R under, or None if it has neither.

    `files` is `NpzFile.files` or any container of key names. The new key wins if both are present.
    """
    names = set(files)
    for key in (STEP1_CLASS_RATIO_TARGET_KEY, LEGACY_STEP1_CLASS_RATIO_KEY):
        if key in names:
            return key
    return None


def step1_class_ratio_target(npz):
    """The target R stored in a nominal weights npz, as a float. Raises KeyError if absent."""
    key = step1_class_ratio_target_key(npz.files)
    if key is None:
        raise KeyError(f"artifact stores neither {STEP1_CLASS_RATIO_TARGET_KEY!r} nor the legacy "
                       f"{LEGACY_STEP1_CLASS_RATIO_KEY!r}")
    value = npz[key]
    try:
        value = value.reshape(-1)[0]
    except AttributeError:
        pass
    return float(value)
