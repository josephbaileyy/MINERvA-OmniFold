"""Independent, opt-in PyTorch PET2-family experiments for MINERvA OmniFold.

This package intentionally has no import-time dependency on ROOT, TensorFlow, or
PyTorch.  Model/training modules import PyTorch lazily and report an explicit
unavailable outcome when it is absent.
"""

from .contracts import (
    CanonicalDataset,
    MeasuredInventory,
    SignalInventory,
    TokenBatch,
)
from .features import ArmManifest, FeatureCapabilities, build_arm_manifest

__all__ = [
    "ArmManifest",
    "CanonicalDataset",
    "FeatureCapabilities",
    "MeasuredInventory",
    "SignalInventory",
    "TokenBatch",
    "build_arm_manifest",
]

__version__ = "0.1.0-experimental"
