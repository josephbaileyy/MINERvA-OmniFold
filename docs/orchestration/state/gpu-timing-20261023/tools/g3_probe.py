"""gpu-timing-20261023 G3 probe: does the analysis environment's LightGBM train with device_type <argv[1]>?
Two boosting rounds on 200 synthetic rows; prints TRAINED or the error. A crash (no output, rc != 0) is reported as such."""
import sys

import lightgbm as lgb
import numpy as np

dev = sys.argv[1]
print("lightgbm", lgb.__version__, "device_type", dev, flush=True)
X = np.random.default_rng(0).normal(size=(200, 3))
y = (X[:, 0] > 0).astype(int)
try:
    lgb.train({"objective": "binary", "device_type": dev, "verbose": 1, "num_iterations": 2}, lgb.Dataset(X, y))
    print(dev, "TRAINED", flush=True)
except Exception as e:  # noqa: BLE001 - the probe reports any refusal as a fact
    print(dev, "ERROR", type(e).__name__, str(e)[:300], flush=True)
