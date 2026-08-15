"""OI-120(c): no-truth-leakage through the PRODUCTION loader, tested by PERTURBATION.

Lane D. READ-ONLY with respect to the campaign: reads the NPZ, writes only a receipt.

WHY NOT THE FORM THAT WAS SPECIFIED. The task as dispatched was "run the production loader on
the real NPZ and check its output with assert_no_truth_leakage". That would prove nothing, and
the reason is measurable rather than arguable:

  fullevent_fps_dataloader.py:1241  event_reco, ... = build_event_features(reco_blocks, ...)
  fullevent_fps_dataloader.py:1247  assert_no_truth_leakage(event_reco, reco_blocks, ...)

The production loader ALREADY makes that call, six lines after building the object, with nothing
touching it in between. And its PURITY statement rebuilds event_reco from the same blocks with
the same code (producer :487-490 vs checker :543-545 are the same three lines), so it compares a
function against a re-execution of itself and CANNOT FAIL. Its docstring at :529 says of that
rebuild "Anything the truth arrays contributed would show up here" -- it would not; the rebuild
never reads the truth arrays. Statements 1 (schema) and 3 (dissimilarity) DO have power. The one
named PURITY has been empty in production on every Gate-5 training.

THE FORM RUN HERE. Re-derivation cannot test purity when the input's provenance IS the
derivation. A perturbation can, and needs no independent provenance at all:

    run the production loader twice on the real input, identical except that a TRUTH array is
    perturbed on the second pass, and require event_reco to be BIT-IDENTICAL.

Two passes differing only in the variable the claim says is irrelevant. It cannot pass by
construction.

PREDECLARED ARMS. P0 is not optional -- without it, "hashes matched" is indistinguishable from
"my perturbation never reached the loader".

  P0  CONTROL: perturb a RECO array          event_reco MUST CHANGE   (proves the probe has power)
      NB: the expectation string must be "CHANGED", matching the verdict vocabulary below. The
      first run had "CHANGE" and scored a correctly-firing control as a FAILURE -- a label bug,
      but one that would have read as "the probe has no power" and voided every arm under it.
  P1  perturb truth_scalars (scale)          event_reco must be IDENTICAL
  P2  permute truth_scalars rows             event_reco must be IDENTICAL
  P3  perturb part_gen (truth cloud)         event_reco must be IDENTICAL
  P4  perturb w_truth                        event_reco must be IDENTICAL

Every arm asserts the array ACTUALLY CHANGED before its result is scored (BEN-181): a
perturbation that did not perturb turns "no leakage" into "no test". An arm the loader REFUSES
is reported as refused, not as a pass -- a fail-closed guard rejecting the perturbation is a
real outcome and it is not evidence of purity.
"""
import gc
import hashlib
import json
import os
import sys

import numpy as np

REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
NPZ = os.path.join(REPO, "nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz")
sys.path.insert(0, os.path.join(REPO, "nd-unfolding/pet"))
sys.path.insert(0, os.path.join(REPO, "nd-unfolding"))

MAX_EVENTS = int(os.environ.get("LEGC_MAX_EVENTS", "0")) or None   # 0/unset -> full inventory

_real_load = np.load
_state = {"perturb": None, "hits": 0, "changed": {}}


class PerturbedNpz:
    """Proxy an NpzFile, substituting perturbed arrays for named keys.

    Records, per key, whether the substitution ACTUALLY changed the array. A proxy that silently
    returned the original would make every downstream 'identical' result meaningless.
    """

    def __init__(self, real, perturb):
        self._real, self._perturb = real, perturb

    @property
    def files(self):
        return self._real.files

    def __contains__(self, k):
        return k in self._real.files

    def __getitem__(self, k):
        a = self._real[k]
        fn = (self._perturb or {}).get(k)
        if fn is None:
            return a
        b = fn(np.array(a, copy=True))
        _state["changed"][k] = bool(not np.array_equal(np.asarray(a), np.asarray(b)))
        _state["hits"] += 1
        return b

    def close(self):
        self._real.close()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self._real.close()


def _patched_load(path, *a, **k):
    z = _real_load(path, *a, **k)
    if str(path) == NPZ and _state["perturb"] is not None:
        return PerturbedNpz(z, _state["perturb"])
    return z


def hash_arr(a):
    a = np.ascontiguousarray(np.asarray(a))
    h = hashlib.sha256()
    h.update(str(a.dtype).encode())
    h.update(str(a.shape).encode())
    h.update(a.tobytes())
    return h.hexdigest()


class _Captured(Exception):
    """Raised to stop the loader once event_reco exists. Not an error."""


def run_pass(label, perturb):
    """One production loader pass, stopped at the point event_reco is constructed.

    WHY STOPPING THERE IS THE RIGHT OBJECT AND NOT A SHORTCUT. In
    fullevent_fps_dataloader.build_fullevent_loaders, `event_reco` is assigned ONCE at :1241,
    inspected by assert_no_truth_leakage at :1247, and attached to the loader at :1351 as
    `reco_evt=event_reco`. Verified by reading every occurrence in that range: it is never
    reassigned, subsetted or rescaled in between. So the array captured here IS the array the
    production loader emits and IS the array the purity claim is about.

    Stopping also removes two dependencies that have nothing to do with the property: the ROOT
    target refinement and the vendored `omnifold.dataloader` import at :1336 (which needs
    TensorFlow -- no Perlmutter interpreter carries both). Everything BEFORE :1241 -- the NPZ
    read, schema gates, block assembly, sentinel handling and pass_reco masking -- is the
    production path and is exercised in full.
    """
    import fullevent_fps_dataloader as fe
    fe.np.load = _patched_load
    _state["perturb"] = perturb
    _state["hits"] = 0
    _state["changed"] = {}
    grabbed = {}
    real_bef = fe.build_event_features

    def _hook(*a, **k):
        out = real_bef(*a, **k)
        grabbed["event_reco"] = np.array(out[0], copy=True)
        grabbed["event_truth_shape"] = list(np.asarray(out[1]).shape)
        raise _Captured()

    fe.build_event_features = _hook
    try:
        fe.build_fullevent_loaders(NPZ, max_events=MAX_EVENTS, seed=0)
        res = {"ok": False, "refused": "loader returned without building event_reco"}
    except _Captured:
        er = grabbed["event_reco"]
        res = {"ok": True, "sha256": hash_arr(er), "shape": list(er.shape),
               "dtype": str(er.dtype), "proxy_hits": _state["hits"],
               "arrays_actually_changed": dict(_state["changed"])}
        del er
    except Exception as exc:                                        # noqa: BLE001
        res = {"ok": False, "refused": f"{type(exc).__name__}: {str(exc)[:240]}"}
    finally:
        res.setdefault("proxy_hits", _state["hits"])
        res.setdefault("arrays_actually_changed", dict(_state["changed"]))
        fe.build_event_features = real_bef
        fe.np.load = _real_load
        _state["perturb"] = None
        grabbed.clear()
        gc.collect()
    print(f"[legc] {label}: {str(res.get('sha256', res.get('refused')))[:72]}"
          f"  hits={res['proxy_hits']} changed={res['arrays_actually_changed']}", flush=True)
    return res


def scale(f):
    return lambda a: (a.astype(np.float64) * f).astype(a.dtype) if a.dtype.kind == "f" else a


def permute_rows(a):
    rng = np.random.default_rng(20260814)
    idx = rng.permutation(a.shape[0])
    return a[idx]


ARMS = [
    ("P0", "CONTROL: reco_scalars scaled x1.01 -> event_reco MUST CHANGE",
     {"reco_scalars": scale(1.01)}, "CHANGED"),
    ("P1", "truth_scalars scaled x1.05", {"truth_scalars": scale(1.05)}, "IDENTICAL"),
    ("P2", "truth_scalars rows permuted", {"truth_scalars": permute_rows}, "IDENTICAL"),
    ("P3", "part_gen (truth cloud) scaled x1.05", {"part_gen": scale(1.05)}, "IDENTICAL"),
    ("P4", "w_truth scaled x1.05", {"w_truth": scale(1.05)}, "IDENTICAL"),
]


def main():
    print("=== OI-120(c): no-truth-leakage through the PRODUCTION loader, by perturbation ===")
    print(f"npz        : {NPZ}")
    print(f"max_events : {MAX_EVENTS or 'FULL inventory'}")
    if MAX_EVENTS:
        print("*** SMOKE TEST: subsetted. Plumbing check only, NOT the proof. ***")

    base = run_pass("BASE (unperturbed)", None)
    if not base["ok"]:
        print(f"[legc] baseline pass FAILED: {base['refused']}")
        print("\n<<<RECEIPT_JSON>>>")
        print(json.dumps({"baseline": base, "VERDICT": "UNRESOLVED"}, indent=1, sort_keys=True))
        return

    results = {}
    for aid, desc, perturb, expect in ARMS:
        r = run_pass(f"{aid} {desc}", perturb)
        keys = list(perturb)
        really_changed = all(r["arrays_actually_changed"].get(k) for k in keys)
        if not r["ok"]:
            verdict, ok = "REFUSED", None
        elif not really_changed:
            # `None`, not `False`. `False` means "arm ran and CONTRADICTED its predeclaration" and is
            # the ONLY value that may produce LEAKAGE below; the scoring filter at :237 excludes on
            # `is not None`, so a `False` here made a perturbation that never ran indistinguishable
            # from a detected leak. Job 56975592 printed LEAKAGE off three bit-identical truth arms
            # for exactly this reason. VOID is excluded like REFUSED -- see :41-44.
            verdict, ok = "VOID (perturbation did not perturb)", None
        else:
            same = r["sha256"] == base["sha256"]
            verdict = "IDENTICAL" if same else "CHANGED"
            ok = (verdict == expect)
        results[aid] = {"desc": desc, "expected": expect, "observed": verdict,
                        "as_predeclared": ok, "detail": r}
        print(f"  [{aid}] expect={expect:10s} observed={verdict:34s} "
              f"{'as predeclared' if ok else ('REFUSED' if ok is None else '*** NO ***')}")

    p0 = results.get("P0", {})
    powered = p0.get("as_predeclared") is True
    truth_arms = [v for k, v in results.items() if k != "P0"]
    scored = [v for v in truth_arms if v["as_predeclared"] is not None]
    clean = all(v["as_predeclared"] for v in scored) if scored else False

    if not powered:
        verdict = ("UNRESOLVED -- the P0 control did not fire, so this probe has no demonstrated "
                   "power to detect a change in event_reco and NO arm below means anything")
    elif not scored:
        verdict = "UNRESOLVED -- the loader refused every truth perturbation; nothing was tested"
    elif clean:
        verdict = (f"NO TRUTH LEAKAGE DEMONSTRATED on {len(scored)} of {len(truth_arms)} truth "
                   f"perturbations, through the production loader"
                   + ("" if not MAX_EVENTS else " -- SMOKE TEST ONLY"))
    else:
        verdict = "LEAKAGE -- event_reco changed when only a truth array changed"

    print(f"\n=== {verdict} ===")
    print("\n<<<RECEIPT_JSON>>>")
    print(json.dumps({
        "what": "OI-120(c): purity of event_reco tested by perturbation, production loader",
        "SMOKE_TEST": bool(MAX_EVENTS), "max_events": MAX_EVENTS,
        "npz": NPZ, "baseline": base, "arms": results,
        "p0_control_fired": powered, "VERDICT": verdict,
        "SPECIFIED_FORM_DECLINED": (
            "The dispatched form -- run the production loader and call assert_no_truth_leakage on "
            "its output -- was NOT run. The loader already makes that exact call at :1247 on the "
            "object built at :1241, and its PURITY statement re-derives with the producing code "
            "(:487-490 vs :543-545), so it cannot fail. Running it again at full scale would have "
            "produced a green guaranteed before the job started."),
        "SCOPE_LIMITS": [
            "Tests PURITY of event_reco with respect to the perturbed truth arrays only. An arm "
            "the loader REFUSED tested nothing and is reported as refused, not as a pass.",
            "Bit-identity is the criterion; no tolerance is involved or appropriate.",
            "Says nothing about statements 1 and 3 of assert_no_truth_leakage, which have their "
            "own (real) power and are exercised elsewhere.",
        ],
    }, indent=1, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
