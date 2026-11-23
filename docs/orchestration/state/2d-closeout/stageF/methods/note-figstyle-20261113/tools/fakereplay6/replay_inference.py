"""A stand-in for publication/release/replay_inference.py for the family-6 identity test (tools/identity_family6.py):
statistics() returns deterministic total and shape statistics from the rows of F, as the real one's signature does."""
import numpy as np
def statistics(F, mu, var, V, dom, seed0, draw=True, seeds=None):
    F = np.atleast_2d(F)
    q = ((F - mu) ** 2 / var)[:, dom]
    tt = q.sum(axis=1) + 1.0
    ts = 0.6 * tt + 0.1 * np.abs(F[:, dom].sum(axis=1))
    return tt, ts
