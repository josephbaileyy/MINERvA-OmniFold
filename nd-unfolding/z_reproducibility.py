#!/usr/bin/env python3
"""Z-SPECIFIC reproducibility configuration for the LightGBM estimator.

Joseph, 2026-09-07: *"Include a Z-specific reproducibility configuration, after checking the actual
LightGBM backend and version. Preserve all existing non-Z defaults and validated reproduction
paths."*

WHAT WAS CHECKED, AND WHAT THE CHECK FOUND
------------------------------------------
`import lightgbm` **fails in this interpreter** -- the package is absent -- and no version is pinned
anywhere in the repository (searched `*.txt`, `*.yml`, `*.yaml`, `*.cfg`, `*.toml`, `*.sh`; the only
hits are prose comments about thread behaviour). `setup_salloc_env.sh` activates a conda prefix
`root_6_28` whose contents are not in this checkout.

**So the actual backend and version CANNOT be established from here, and this module does not
guess.** `z_lgbm_overlay()` REFUSES unless a live probe has confirmed the backend and recognised
every knob it is about to set. That is the same discipline as `z_contract.Boundary`: an unverified
value that could change a production artifact is withheld at the point of use, not defaulted.

Installing LightGBM to answer the question would CHANGE the environment rather than read it, which
is not an evidence errand -- the same rule §7 item 1 applies to `uproot`.

WHY PINNING IS THE POINT (§3.7a route (i))
------------------------------------------
`omnifold_nn_core.make_estimators:143-148` builds
`LGBMClassifier(n_estimators=100, num_leaves=8, learning_rate=0.1, verbose=-1)` and sets
`random_state` from the seed -- and **nothing else**. No thread count, no determinism flag, no
histogram-construction mode. The module's own docstring (`:203-204`) says LightGBM at these settings
is *"**nearly** deterministic in `seed` alone"*; the word is its author's.

The repository has measured the consequence twice, on a different subject:

  * `run_p4_unfold_std.sh:17-23` / KNOWN_ISSUES #24 -- **0/10 sha256 match** on a clean re-unfold,
    contents agreeing to **1.9e-11 per bin** and **2.6e-14 on the integral**, attributed to
    *"LightGBM/OpenMP reduction order"*.
  * Several launchers record that LightGBM **ignores `OMP_NUM_THREADS`** and over-spawns
    (`run_4d_replicas_packed.sh:20-21`, `uq_fps/corrected/run_fps_uq_packed.sh:3-5`), which is why
    the thread count must be pinned as an ESTIMATOR PARAMETER and not as an environment variable.

Those figures are **TRANSFERRED** -- standard-P4's chain, not Z's 5D bank -- and they are candidate
inputs to `B`, never a substitute for measuring it.

WHAT THIS MODULE DOES NOT DO
----------------------------
It does not import, monkeypatch or mutate `omnifold_nn_core`, and it changes no default any
existing caller sees. `make_estimators` is untouched; `p4_lib.REPRO_RTOL_PER_BIN` /
`REPRO_RTOL_INTEGRAL` and `p4_lib.check_reproducibility` are untouched and remain the validated
reproduction path for the standard chain. The overlay is a dict a Z-specific caller passes; nothing
here applies it to anything.

**And applying it is a scientific act, not a hygiene one.** Pinning the reduction order changes the
numbers Z produces relative to the historical chain. That divergence must be declared with Z's
build, which is why `z_lgbm_overlay` returns its rationale alongside the knobs and why the receipt
carries both.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from z_contract import ZContractError


@dataclass(frozen=True)
class BackendProbe:
    """What a live import of the estimator backend actually reported."""

    available: bool
    version: Optional[str] = None
    error: Optional[str] = None
    recognised_knobs: dict = field(default_factory=dict)   # knob -> True / False / None

    def describe(self) -> dict:
        return {"available": self.available, "version": self.version, "error": self.error,
                "recognised_knobs": dict(self.recognised_knobs)}


# The knobs Z would pin, each with the reason it is on the list. Values are Z's PROPOSAL; nothing
# here is applied, and none of these is an acceptance boundary.
Z_REPRO_KNOBS = {
    "deterministic": (True,
                      "LightGBM's own switch for reproducible histogram construction. The module "
                      "docstring's 'nearly deterministic in seed alone' is what this addresses."),
    "force_row_wise": (True,
                       "deterministic histogram building requires a fixed construction mode; "
                       "without one the reduction order is chosen at runtime."),
    "num_threads": (1,
                    "the estimator parameter, NOT OMP_NUM_THREADS, which this repository has "
                    "measured LightGBM to ignore. Thread count sets reduction order, so an "
                    "unpinned count makes the CV a property of the allocation."),
}


# A name that cannot be a LightGBM parameter. The probe asks about it too: if the backend
# "recognises" it, the recognition METHOD is not discriminating and every answer it gives is
# worthless. See `probe_backend`.
_NEGATIVE_CONTROL = "z_probe_definitely_not_a_lightgbm_parameter_9f2c"
# A parameter the production estimator already passes (`omnifold_nn_core:145`), so it certainly
# exists in any build this campaign could be using.
_POSITIVE_CONTROL = "num_leaves"


def _alias_membership(aliases, name):
    """Is `name` a real parameter, by this build's alias table? `None` if unanswerable.

    `_ConfigAliases.get(name)` returns a SET. For a real parameter it contains the canonical name
    and its aliases; for an unknown name LightGBM 4.x returns `{name}` -- the query echoed back.
    So `bool(...)` is true for everything, which is review finding 5. Membership has to be tested
    against the echo, and even that is only trustworthy if the controls below behave.
    """
    try:
        s = aliases.get(name)
    except Exception:
        return None
    if not isinstance(s, (set, frozenset, list, tuple)):
        return None
    s = set(s)
    if not s:
        return False
    return s != {name}          # a bare echo is not recognition


def probe_backend() -> BackendProbe:
    """Import LightGBM and report what is actually there, WITH CONTROLS. Never raises.

    ⚠ REVIEW FINDING 5. The first version used `bool(_ConfigAliases.get(knob))`, which is not a
    membership test: LightGBM 4.5.0 echoes an unknown name straight back, so every knob -- real or
    invented -- came back "recognised". A recognition test that cannot fail certifies anything.

    Two controls now run alongside the real questions, and BOTH must behave or the whole probe is
    reported unverified:

      * a NEGATIVE control -- a name that cannot exist. If it is "recognised", the method is
        echoing and no answer from it means anything.
      * a POSITIVE control -- `num_leaves`, which the production estimator already passes. If it
        is NOT recognised, the method is blind and, again, no answer means anything.

    A probe that cannot discriminate returns `None` for every knob, which the overlay refuses. That
    is the intended outcome on any build whose alias table echoes.
    """
    try:
        import lightgbm  # noqa: F401
    except Exception as exc:                       # ImportError, or a broken install
        return BackendProbe(available=False, version=None, error=f"{type(exc).__name__}: {exc}",
                            recognised_knobs={k: None for k in Z_REPRO_KNOBS})

    version = getattr(lightgbm, "__version__", None)
    aliases = getattr(getattr(lightgbm, "basic", None), "_ConfigAliases", None)
    if aliases is None or not hasattr(aliases, "get"):
        return BackendProbe(available=True, version=version,
                            error="this build exposes no interrogable parameter table",
                            recognised_knobs={k: None for k in Z_REPRO_KNOBS})

    neg = _alias_membership(aliases, _NEGATIVE_CONTROL)
    pos = _alias_membership(aliases, _POSITIVE_CONTROL)
    if neg is not False or pos is not True:
        return BackendProbe(
            available=True, version=version,
            error=(f"recognition method is not discriminating: negative control "
                   f"{_NEGATIVE_CONTROL!r} -> {neg!r} (want False), positive control "
                   f"{_POSITIVE_CONTROL!r} -> {pos!r} (want True)"),
            recognised_knobs={k: None for k in Z_REPRO_KNOBS})

    return BackendProbe(available=True, version=version, error=None,
                        recognised_knobs={k: _alias_membership(aliases, k)
                                          for k in Z_REPRO_KNOBS})


def z_lgbm_overlay(probe: Optional[BackendProbe] = None) -> dict:
    """The Z-only LightGBM parameter overlay, or REFUSE.

    Returns `{"params": {...}, "rationale": {...}, "backend": {...}}`. Raises `ZContractError` if
    the backend is absent, or if any knob could not be confirmed against the installed build --
    because setting an unrecognised parameter is silently ignored by LightGBM, which would produce
    a run that BELIEVES it is pinned and is not. That failure is worse than refusing: it is a green
    reproducibility claim over an unpinned estimator.
    """
    probe = probe_backend() if probe is None else probe
    if not probe.available:
        raise ZContractError(
            "Z reproducibility overlay REFUSED: the LightGBM backend could not be imported "
            f"({probe.error}), so its version and parameter set are unknown. This module does not "
            "guess a determinism configuration -- an unrecognised LightGBM parameter is silently "
            "ignored, which would yield a run that reports itself pinned while its reduction order "
            "still varies with the allocation. Re-run this probe in the campaign environment.")
    # ⚠ REVIEW FINDING 5, SECOND HALF. The first version iterated over `probe.recognised_knobs`,
    # so a probe carrying an EMPTY map had nothing to disagree with and sailed through. The
    # required set is `Z_REPRO_KNOBS`; absence of evidence is now iterated over explicitly.
    unverified = [k for k in Z_REPRO_KNOBS if probe.recognised_knobs.get(k) is not True]
    if unverified:
        raise ZContractError(
            f"Z reproducibility overlay REFUSED: knobs {sorted(unverified)} carry no positive "
            f"evidence against LightGBM {probe.version!r} "
            f"(probe error: {probe.error!r}). Every required knob needs its own confirmation -- a "
            "silently-ignored parameter is indistinguishable from a set one, and a missing entry "
            "is not a passing one.")
    if not probe.version or not str(probe.version).strip():
        raise ZContractError(
            "Z reproducibility overlay REFUSED: the backend reported no version. The knobs are "
            "version-dependent, and a configuration that cannot name the build it was verified "
            "against is not reproducible in the sense this module exists to provide.")
    return {
        "params": {k: v for k, (v, _) in Z_REPRO_KNOBS.items()},
        "rationale": {k: r for k, (_, r) in Z_REPRO_KNOBS.items()},
        "backend": probe.describe(),
        "declares_divergence_from_historical_chain": True,
        "divergence_note": (
            "Pinning reduction order changes Z's numbers relative to the unpinned historical "
            "chain. This is a deliberate, declared divergence, not a bug fix, and Z's receipt "
            "must carry it so a later comparison is not read as disagreement between subjects."),
    }


def transferred_repro_evidence() -> dict:
    """Candidate inputs to `B`, all TRANSFERRED from a different subject. Never a boundary.

    Kept here rather than in `z_contract` precisely so nobody can reach them through the boundary
    registry: these are measurements about the standard-P4 chain, and `B` for Z is unestablished.
    """
    from z_contract import P4_REPRO_RTOL_PER_BIN, P4_REPRO_RTOL_INTEGRAL
    return {
        "subject": "standard-P4 5D unfold chain -- NOT Z's 5D bank",
        "class": "TRANSFERRED",
        "measured_floor_per_bin": 1.9e-11,
        "measured_floor_integral": 2.6e-14,
        "source": "run_p4_unfold_std.sh:17-23 / KNOWN_ISSUES #24 (0/10 sha256 match on a clean "
                  "re-unfold; attributed to LightGBM/OpenMP reduction order)",
        "declared_tolerance_per_bin": P4_REPRO_RTOL_PER_BIN,
        "declared_tolerance_integral": P4_REPRO_RTOL_INTEGRAL,
        "declared_tolerance_source": "p4_lib:88-100, set by Joseph 2026-08-07 and widened "
                                     "2026-08-08 from measured spread",
        "why_this_is_a_precedent_and_not_a_boundary": (
            "It is the B <= S shape already worked once: a floor was measured, a tolerance was "
            "declared roughly two orders above it, and the margin was argued (52x per-bin, 32x "
            "integral) rather than read off an endpoint. Z needs its own B and its own S; this is "
            "the worked example, not the answer."),
    }
