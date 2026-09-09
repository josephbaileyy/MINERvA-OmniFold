"""SPEC §6: do the projection-matrix builders agree? A CHECK, not a study.

Neither implementation takes precedence. This reports agreement or disagreement and
nothing else. It adopts nothing and designates nothing.
"""
import hashlib, sys
import numpy as np
sys.path.insert(0, "nd-unfolding")
import project_cov_nd as pcn
import p4_lib

AXES = ["pt", "pz", "eavail", "q3", "W"]
EDGES = [np.asarray(pcn.AXIS_EDGES[a], float) for a in AXES]
NB = [e.size - 1 for e in EDGES]
DROP = 4                                   # W, the 5D->4D projection
KEEP = [a for i, a in enumerate(AXES) if i != DROP]
NB_LOW = [n for i, n in enumerate(NB) if i != DROP]
TOTAL_HIGH, TOTAL_LOW = int(np.prod(NB)), int(np.prod(NB_LOW))

def masks(seed, frac):
    """A reported-bin mask on the high grid, and the low mask it IMPLIES.

    The low mask is derived rather than chosen, because builder 1 REFUSES a high bin whose
    low image is unreported. Choosing them independently would test the refusal, not the map.
    """
    rng = np.random.default_rng(seed)
    mh = rng.random(TOTAL_HIGH) < frac
    idx = np.unravel_index(np.nonzero(mh)[0], tuple(NB))
    low_coords = tuple(idx[i] for i in range(5) if i != DROP)
    ml = np.zeros(TOTAL_LOW, bool)
    ml[np.ravel_multi_index(low_coords, tuple(NB_LOW))] = True
    return mh, ml

def build_one(mh, ml):
    return p4_lib.build_projection_M(EDGES, DROP, mh, ml)

def build_two(mh, ml):
    src_report = np.nonzero(mh)[0]
    dst_index_of = np.full(TOTAL_LOW, -1, dtype=np.int64)
    dst_index_of[np.nonzero(ml)[0]] = np.arange(int(ml.sum()))
    M, dropped = pcn.build_projection(AXES, KEEP, src_report, tuple(NB), tuple(NB_LOW),
                                      dst_index_of)
    return M, dropped

def digest(M):
    return hashlib.sha256(np.ascontiguousarray(M, dtype=np.float64).tobytes()).hexdigest()

print("grid %s = %d high, %d low; drop axis %d (%s)" % (NB, TOTAL_HIGH, TOTAL_LOW, DROP, AXES[DROP]))
print()
for seed, frac in ((7, 0.02), (11, 0.05), (23, 0.10)):
    mh, ml = masks(seed, frac)
    try:
        M1 = build_one(mh, ml)
    except Exception as e:
        print("seed %-3d frac %.2f : builder1 RAISED %s: %s" % (seed, frac, type(e).__name__, str(e)[:70]))
        continue
    M2, dropped = build_two(mh, ml)
    same_shape = M1.shape == M2.shape
    print("seed %-3d frac %.2f : reported high %6d  low %5d  M %s / %s  dropped_by_2 %d"
          % (seed, frac, int(mh.sum()), int(ml.sum()), M1.shape, M2.shape, dropped))
    if not same_shape:
        print("        SHAPES DIFFER -- elementwise comparison not defined"); continue
    d = np.abs(M1 - M2)
    exact = bool(np.array_equal(M1, M2))
    print("        max|M1-M2| = %.3e   exact-equal %s   sha1 %s   sha2 %s"
          % (d.max(), exact, digest(M1)[:16], digest(M2)[:16]))
    if not exact:
        nz = np.nonzero(d)
        print("        %d differing entries; first at (%d,%d): %r vs %r"
              % (nz[0].size, nz[0][0], nz[1][0], M1[nz[0][0], nz[1][0]], M2[nz[0][0], nz[1][0]]))
