#!/usr/bin/env python3
"""Z-SPECIFIC reproducibility configuration for the LightGBM estimator.

Joseph, 2026-09-07: *"Include a Z-specific reproducibility configuration, after checking the actual
LightGBM backend and version. Preserve all existing non-Z defaults and validated reproduction
paths."*

WHAT WAS CHECKED, AND WHAT THE CHECK FOUND
------------------------------------------
⚠ **THIS SECTION WAS REWRITTEN 2026-09-07: THE BACKEND IS NOW MEASURED, NOT UNKNOWN.** Joseph
authorized the verification; it was done by READING the campaign environment, installing nothing.

`import lightgbm` still fails **in this laptop interpreter**, and every local test therefore runs
against fixtures. But the interpreter that matters is the one the unfold runs in --
`run_p4_unfold_std.sh` calls `python3` with `import ROOT` available, so the chain runs under the
`root_6_28` conda prefix, and `omnifold_nn_core.make_estimators:144` imports LightGBM lazily
inside it. That environment was read directly on a login node (`login07`, no scheduler, no
training, no file written into the checkout):

  * **LightGBM `4.6.0`**, Python `3.11.14`,
    `~/.conda/envs/root_6_28/lib/python3.11/site-packages/lightgbm/`.
  * `_ConfigAliases._get_all_param_aliases()` **exists and answers**: a dict of **140** canonical
    parameters over a **307**-name universe. This module's primary accessor is correct.
  * `_ConfigAliases.aliases` is **`None`** on this build, so the fallback accessor is NOT
    exercised here. It is kept for older builds and must be read as untested against 4.6.0.
  * **`0` entries have an empty alias list; `70` of 140 are self-only.** So the round-3 method,
    which tested `not aliases`, would have found **zero** alias-free parameters on the real
    backend and reported its third control UNAVAILABLE -- on the campaign build, not merely on a
    fixture. The correction was larger than the fixture suggested.
  * The facts three review rounds turned on, now read from the table rather than argued:
    `deterministic -> ['deterministic']`, `force_row_wise -> ['force_row_wise']`,
    `force_col_wise -> ['force_col_wise']`, and
    `is_unbalance -> ['is_unbalance', 'unbalance', 'unbalanced_sets']`.
  * The negative control echoes back as `['z_probe_...']`, confirming on the real build the
    behaviour that made `bool(get(name))` certify everything.
  * `LGBMClassifier(deterministic=True, force_row_wise=True, num_threads=1)` constructs and
    `get_params()` returns all three -- **and that establishes NOTHING**, which is the third time
    this module has been fooled by an echo. Measured with the control I should have run first:
    `LGBMClassifier(z_bogus_not_a_param_9f2c=42).get_params()` returns `42` for that key just as
    happily. The sklearn wrapper STORES arbitrary keyword parameters, so `get_params()` is
    wrapper storage and not native execution of the setting -- the same defect as
    `_ConfigAliases.get()` echoing an unknown name, one layer up. **Recognition rests on the
    PARAMETER TABLE observation above and on nothing else**, and the reproducibility caveat is
    undiminished: that a knob is recognised does not show the run is reproducible.

**THE REVIEWED MODULE ITSELF WAS RUN AGAINST THAT BACKEND**, byte-identical -- sha256
`76e9867cf384e8775bba4f808ef44343191c0ffba6f29333a1a1ce96c69267ce`, verified on both ends -- with
only a two-line `z_contract` shim supplying `ZContractError`, which no probe logic touches.
`probe_backend()` returned all three controls behaving (negative False, positive True, alias-free
True on `alpha`, independent of Z's knobs), all three knobs recognised, and **`z_lgbm_overlay()`
ACCEPTED for the first time** at version `4.6.0`. See `MEASURED_BACKEND`.

`z_lgbm_overlay()` still REFUSES wherever a live probe has not confirmed the backend -- including
this laptop. That discipline is unchanged and is the same as `z_contract.Boundary`: an unverified
value that could change a production artifact is withheld at the point of use, not defaulted.

Nothing was installed to obtain this. Installing LightGBM locally would have answered a question
about macOS rather than about the campaign, which is the venue error this repository has made
before.

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
    # What the recognition method was, and how its controls behaved. On the receipt so a reader
    # can see WHICH table answered and whether it was interrogable, not just the verdict.
    controls: dict = field(default_factory=dict)

    def describe(self) -> dict:
        return {"available": self.available, "version": self.version, "error": self.error,
                "recognised_knobs": dict(self.recognised_knobs),
                "controls": dict(self.controls)}


# The knobs Z would pin, each with the reason it is on the list. Values are Z's PROPOSAL; nothing
# here is applied, and none of these is an acceptance boundary.
# ⚠ `deterministic` and `force_row_wise` are defined upstream with EMPTY alias lists. That fact
# broke the first two recognition methods (review findings 5 and, again, round 3 finding 2): an
# alias-free parameter is indistinguishable from an unknown one if you only look at what
# `_ConfigAliases.get()` returns. Recognition reads the parameter TABLE now. See `_parameter_table`.
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
# exists in any build this campaign could be using. It also HAS aliases upstream, which is why it
# alone was not enough -- see `_ALIAS_FREE_CONTROL_NOTE`.
_POSITIVE_CONTROL = "num_leaves"

_ALIAS_FREE_CONTROL_NOTE = (
    "third control, added in round 3: a parameter with no aliases BEYOND ITS OWN NAME. It is "
    "chosen FROM THE TABLE rather than named here, so it cannot go stale against a version that "
    "changes which parameters have aliases. Any recognition method that infers existence from the "
    "SHAPE of an alias set fails this control while passing the other two -- which is exactly how "
    "the previous two methods survived review.")


def _extra_aliases(canonical, aliases):
    """The aliases of `canonical` OTHER THAN ITSELF, or None if the entry is not a sequence.

    ⚠ ROUND-4 FINDING 2. The round-3 control tested `not aliases`, i.e. an EMPTY list. That is the
    shape of the C++ JSON dump, but LightGBM 4.5.0's PYTHON accessor PREPENDS the canonical name
    to its own alias list, so an alias-free parameter comes back as `[name]` and never as `[]`.
    Measured against a source-shaped table holding three alias-free parameters: recognition and
    the overlay both succeeded, and the control reported UNAVAILABLE -- so the one control that
    exists to catch this defect class silently did not run.

    A control that stops controlling without saying so is worse than no control, and it is this
    repository's catalogued shape: a green state reachable without the work being done.

    Subtracting the canonical name answers the question under BOTH shapes, which matters because
    which accessor answered is not something this module can verify from here.
    """
    if not isinstance(aliases, (set, frozenset, list, tuple)):
        return None
    return {str(a) for a in aliases} - {str(canonical)}

# How to reach the build's own parameter table, best first. `_get_all_param_aliases()` is the
# C-API dump (`LGBM_DumpParamAliases`), i.e. the table LightGBM itself is configured from;
# `.aliases` is the dict some builds expose directly.
#
# ⚠ THESE ACCESSOR NAMES ARE NOT VERIFIED IN THIS INTERPRETER -- LightGBM is not installed here
# (see the module docstring). They are taken from upstream. The failure direction is deliberate:
# if none of them resolves to a non-empty dict, the probe reports the table unreadable, every
# knob comes back `None`, and `z_lgbm_overlay` REFUSES. A wrong guess here cannot certify
# anything; it can only withhold. Verifying them is part of the outstanding production check.
_TABLE_ACCESSORS = (
    ("_ConfigAliases._get_all_param_aliases()", lambda a: a._get_all_param_aliases()),
    ("_ConfigAliases.aliases", lambda a: a.aliases),
)


def _parameter_table(aliases):
    """`(table, source)` -- the build's canonical -> aliases map -- or `(None, why_not)`.

    ⚠ ROUND-3 FINDING 2. The two previous methods both interrogated `_ConfigAliases.get(name)`
    and tried to read existence off the RESULT:

      * `bool(get(name))` -- true for everything, because an unknown name is echoed back.
      * `get(name) != {name}` -- false for every ALIAS-FREE parameter, and LightGBM 4.5.0 defines
        `deterministic` and `force_row_wise` with empty alias lists. Measured: both of Z's own
        determinism knobs came back "unrecognised" and the overlay refused a valid configuration.

    Both are inferences about a lookup's return SHAPE. Neither is a membership test. The table
    itself is the only thing that answers the question asked, so this reads the table.
    """
    for source, fetch in _TABLE_ACCESSORS:
        try:
            t = fetch(aliases)
        except Exception:
            continue
        if isinstance(t, dict) and t:
            return t, source
    return None, ("this build exposes no readable parameter table (tried "
                  + ", ".join(s for s, _ in _TABLE_ACCESSORS) + ")")


def _parameter_universe(table):
    """Every name the table admits: canonical keys AND aliases, since either may be passed."""
    universe = set()
    for canonical, aliases in table.items():
        universe.add(str(canonical))
        if isinstance(aliases, (set, frozenset, list, tuple)):
            universe |= {str(a) for a in aliases}
    return universe


def probe_backend() -> BackendProbe:
    """Import LightGBM and report what is actually there, WITH THREE CONTROLS. Never raises.

    The question is "does this build have a parameter called X", and it is answered by looking X
    up in the build's own parameter table (`_parameter_table`). Two earlier methods tried to infer
    it from the shape of an alias lookup and both were wrong, in opposite directions -- one
    certified every name, the next refused every alias-free one.

    THE CONTROLS, and what each one is for:

      * NEGATIVE -- a name that cannot exist. Catches a method that echoes its query back, which
        is how `bool(get(name))` certified invented parameters.
      * POSITIVE -- `num_leaves`, which the production estimator already passes. Catches a table
        that is present but empty, truncated, or shaped differently than assumed.
      * ALIAS-FREE -- chosen FROM the table: a parameter whose alias list is empty. Catches a
        method that mistakes "no aliases" for "no such parameter", which is the round-3 finding.
        Unavailable if the table defines no such parameter; that is recorded, not treated as a
        pass, and it is not treated as a failure either -- absence of the fixture is not evidence.

    If any available control misbehaves, EVERY knob comes back `None` and the overlay refuses. The
    controls guard the method, not the knobs, so a method that cannot be trusted about the control
    is not trusted about anything.
    """
    try:
        import lightgbm  # noqa: F401
    except Exception as exc:                       # ImportError, or a broken install
        return BackendProbe(available=False, version=None, error=f"{type(exc).__name__}: {exc}",
                            recognised_knobs={k: None for k in Z_REPRO_KNOBS})

    version = getattr(lightgbm, "__version__", None)
    blind = {k: None for k in Z_REPRO_KNOBS}
    aliases = getattr(getattr(lightgbm, "basic", None), "_ConfigAliases", None)
    if aliases is None:
        return BackendProbe(available=True, version=version, recognised_knobs=blind,
                            error="this build exposes no _ConfigAliases parameter table")

    table, source = _parameter_table(aliases)
    if table is None:
        return BackendProbe(available=True, version=version, recognised_knobs=blind,
                            error=source, controls={"table_source": None})

    universe = _parameter_universe(table)
    alias_free = sorted(str(k) for k, v in table.items()
                        if _extra_aliases(k, v) == set())
    # Prefer an alias-free parameter that is NOT one of Z's own knobs, so the control asks an
    # INDEPENDENT question. If the only alias-free names in the table are the knobs themselves the
    # control still runs, but it is then answering the same question as the knob check and says so.
    independent = [k for k in alias_free if k not in Z_REPRO_KNOBS]
    af_name = (independent or alias_free or [None])[0]
    controls = {
        "table_source": source,
        "table_parameters": len(table),
        "universe_size": len(universe),
        "negative": {"name": _NEGATIVE_CONTROL, "want": False,
                     "got": _NEGATIVE_CONTROL in universe},
        "positive": {"name": _POSITIVE_CONTROL, "want": True,
                     "got": _POSITIVE_CONTROL in universe},
        "alias_free": ({"name": af_name, "want": True, "got": af_name in universe,
                        "n_alias_free_in_table": len(alias_free),
                        "independent_of_Z_knobs": af_name not in Z_REPRO_KNOBS}
                       if af_name is not None else
                       {"name": None, "status": "UNAVAILABLE -- no parameter in this table has an "
                                                "alias set consisting of its own name alone, so "
                                                "this control could not be run",
                        "note": _ALIAS_FREE_CONTROL_NOTE}),
    }
    misbehaving = [c for c in ("negative", "positive", "alias_free")
                   if "want" in controls[c] and controls[c]["got"] is not controls[c]["want"]]
    if misbehaving:
        return BackendProbe(
            available=True, version=version, recognised_knobs=blind, controls=controls,
            error=("recognition method is not discriminating; misbehaving controls "
                   + repr(misbehaving) + " against table " + repr(source)))

    return BackendProbe(available=True, version=version, error=None, controls=controls,
                        recognised_knobs={k: (k in universe) for k in Z_REPRO_KNOBS})


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


# ------------------------------------------------------------------- the measured backend ------
# A TIMESTAMPED OBSERVATION, not a current state. It records what one read of one environment
# returned; it does not assert that the environment is still that way, and nothing in this module
# consults it to decide anything. `probe_backend()` is what decides, at the point of use.
MEASURED_BACKEND = {
    "observed_utc": "2026-09-07",
    "host": "login07 (saul.nersc.gov login node -- no scheduler, no training, read-only)",
    "environment": "~/.conda/envs/root_6_28  -- the prefix run_p4_unfold_std.sh runs the chain in",
    "python": "3.11.14",
    "lightgbm_version": "4.6.0",
    "lightgbm_path": "~/.conda/envs/root_6_28/lib/python3.11/site-packages/lightgbm/",
    "accessor_that_answered": "_ConfigAliases._get_all_param_aliases()",
    "accessor_absent_on_this_build": "_ConfigAliases.aliases is None",
    "table_parameters": 140,
    "universe_size": 307,
    "n_alias_free": 70,
    "n_empty_alias_list": 0,          # why the round-3 method found none on the real backend
    "knobs_recognised": {"deterministic": True, "force_row_wise": True, "num_threads": True},
    # NOT "accepted": `get_params()` echoes an arbitrary kwarg identically (measured with
    # `z_bogus_not_a_param_9f2c=42`). This records only that the wrapper STORED them.
    "knobs_stored_by_sklearn_wrapper": {"deterministic": True, "force_row_wise": True,
                                        "num_threads": 1},
    "wrapper_storage_is_not_execution": (
        "LGBMClassifier stores arbitrary keyword parameters, so get_params() is not an "
        "acceptance test. The negative control z_bogus_not_a_param_9f2c=42 round-trips too. "
        "Recognition rests on the parameter table, not on this field."),
    "overlay_verdict": "ACCEPTED",
    # ⚠ THE DIGEST IS OF THE MODULE AS RUN, WHICH IS NOT THIS FILE ANY MORE. It resolves to
    # `nd-unfolding/z_reproducibility.py` at commit 8212de00 -- the reviewed, merged revision --
    # and this docstring was rewritten afterwards to record what that run found. A reader who
    # shas the working copy will get a different value, correctly. Cite the pair, never the
    # digest alone.
    "module_sha256_run_there":
        "76e9867cf384e8775bba4f808ef44343191c0ffba6f29333a1a1ce96c69267ce",
    "module_revision_run_there": "8212de00:nd-unfolding/z_reproducibility.py",
    "caveats": (
        "One host, one read, one date. The login node is not a compute node and this says nothing "
        "about the allocation's threading. It also does NOT verify that a Z run would reproduce -- "
        "it verifies that the knobs exist, are recognised and are accepted, which is the "
        "precondition for pinning them and not evidence that pinning them suffices."),
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
