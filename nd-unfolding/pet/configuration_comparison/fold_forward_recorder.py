"""Record the fold-forward ratio every time MultiFold produces a push, including the last one.

`OI-125`'s finding is that the closure drivers compute no fold-forward ratio at all
(`git grep fold_forward` over both closure drivers returns nothing), so the
comparison's V2 control has nothing to read. The nominal driver does compute one,
at `train_fullevent_nominal.py:576-577`, from `push` AFTER `Unfold()` -- the
end-of-run scalar, and the source of the `0.736746` that the whole `OI-71`/`OI-125`
argument rests on.

WHY THIS IS A NEW FILE. Two constraints, both external. The pinned driver must not
be edited, and the existing instrumentation
(`closure_foldforward_instrumented.py:115`) hooks `RunStep1`, which is the wrong
hook: with `niter = 3` it captures the push CONSUMED by steps 1 of iterations 0, 1
and 2 -- that is, the pushes produced before the loop and by `RunStep2(0)` and
`RunStep2(1)`. The push produced by `RunStep2(2)` is consumed by nothing and
recorded by no row. Reading "the last recorded row" instead therefore answers a
different question and, measured, flips the sign of `ratio - 1`. VL134 had to be
reconstructed from `weights_push` and `dump_rows_b` for exactly this reason, and is
a reconstruction rather than a recorded value.

So this recorder hooks `RunStep2`, which is where a push is PRODUCED, and labels
every row with whether a later step 1 consumes it. The end-of-run row -- the one
comparable to the nominal's `0.736746` -- is then a recorded value rather than a
reconstruction.

The ratio itself is transcribed from the driver, not re-derived:

    sum(w_reco[pass_reco] * push[pass_reco]) / sum(w_reco[pass_reco])

NOT CITABLE FOR any recovery or adoption claim. This records a diagnostic.
"""

from __future__ import annotations

from typing import Any, Callable

import numpy as np


def fold_forward_ratio(
    w_reco: np.ndarray, push: np.ndarray, pass_reco: np.ndarray
) -> float:
    """The driver's reco-leg fold-forward ratio, fail-closed on a bad population.

    Transcribed from `train_fullevent_nominal.py:576-577`. The three guards are the
    driver's own: a ratio over zero `pass_reco` rows is undefined, and arrays that
    are not row-aligned silently compute something that is not this quantity.
    """
    w_reco = np.asarray(w_reco, dtype=np.float64)
    push = np.asarray(push, dtype=np.float64)
    pass_reco = np.asarray(pass_reco).astype(bool)
    if not (w_reco.shape == push.shape == pass_reco.shape):
        raise ValueError(
            f"not row-aligned: w_reco {w_reco.shape}, push {push.shape}, "
            f"pass_reco {pass_reco.shape} (fail closed)"
        )
    if w_reco.ndim != 1:
        raise ValueError(f"expected one row per event, got shape {w_reco.shape}")
    if not pass_reco.any():
        raise ValueError("no pass_reco rows; the fold-forward ratio is undefined")
    denominator = float(w_reco[pass_reco].sum())
    if denominator == 0.0:
        raise ValueError("pass_reco weight sums to zero; the ratio is undefined")
    return float((w_reco[pass_reco] * push[pass_reco]).sum() / denominator)


class FoldForwardRecorder:
    """Wrap a `MultiFold` and record the ratio of every push it produces.

    Attaching replaces `RunStep1` and `RunStep2` on the INSTANCE, not the class, so
    two unfoldings in one process cannot contaminate each other and nothing on disk
    changes. `detach()` restores the originals; the object is also a context
    manager, because a recorder left attached after an exception would keep
    appending rows to a run nobody is reading.
    """

    def __init__(
        self, multifold: Any, w_reco: np.ndarray, pass_reco: np.ndarray, label: str = ""
    ) -> None:
        self.multifold = multifold
        self.w_reco = np.asarray(w_reco, dtype=np.float64)
        self.pass_reco = np.asarray(pass_reco).astype(bool)
        self.label = label
        self.rows: list[dict[str, Any]] = []
        self._saved: dict[str, Callable[..., Any]] = {}
        self._was_instance_attribute: dict[str, bool] = {}

    def __enter__(self) -> "FoldForwardRecorder":
        return self.attach()

    def __exit__(self, *exc: Any) -> None:
        self.detach()

    def attach(self) -> "FoldForwardRecorder":
        if self._saved:
            raise RuntimeError("already attached")
        for name in ("RunStep1", "RunStep2"):
            if not hasattr(self.multifold, name):
                raise AttributeError(
                    f"{type(self.multifold).__name__} has no {name}; this recorder is "
                    "written against MultiFold's two-step loop and must not guess"
                )
            self._saved[name] = getattr(self.multifold, name)
            self._was_instance_attribute[name] = name in vars(self.multifold)

        def run_step_1(iteration: int, *args: Any, **kwargs: Any) -> Any:
            # Snapshot BEFORE the call: this is the push step 1 consumes, which is
            # what the RunStep1 hook was capturing all along. Recorded explicitly as
            # a consumption so nobody mistakes it for a production.
            self._record(iteration, "consumed_by_step1", self._push())
            return self._saved["RunStep1"](iteration, *args, **kwargs)

        def run_step_2(iteration: int, *args: Any, **kwargs: Any) -> Any:
            result = self._saved["RunStep2"](iteration, *args, **kwargs)
            self._record(iteration, "produced_by_step2", self._push())
            return result

        self.multifold.RunStep1 = run_step_1
        self.multifold.RunStep2 = run_step_2
        return self

    def detach(self) -> None:
        """Restore the engine, including removing the attributes we created.

        Reassigning the saved bound method would leave an INSTANCE attribute
        shadowing the class method forever. That is functionally equivalent but not
        a restore, and it makes "is this engine instrumented?" unanswerable by
        inspection.
        """
        for name, original in self._saved.items():
            if self._was_instance_attribute.get(name):
                setattr(self.multifold, name, original)
            else:
                vars(self.multifold).pop(name, None)
        self._saved.clear()
        self._was_instance_attribute.clear()

    def _push(self) -> np.ndarray | None:
        push = getattr(self.multifold, "weights_push", None)
        return None if push is None else np.asarray(push, dtype=np.float64).copy()

    def _record(self, iteration: int, occasion: str, push: np.ndarray | None) -> None:
        row: dict[str, Any] = {"iteration": int(iteration), "occasion": occasion}
        if push is None:
            row["ratio"] = None
            row["note"] = "weights_push not yet created"
        else:
            row["ratio"] = fold_forward_ratio(self.w_reco, push, self.pass_reco)
        self.rows.append(row)

    def end_of_run_ratio(self) -> float:
        """The push left after `Unfold()` -- the quantity comparable to the nominal.

        This is the row the `RunStep1` hook could never produce. If no `RunStep2`
        ever ran, there is no such quantity and saying so is better than returning
        the last thing that happens to be in the list.
        """
        produced = [r for r in self.rows if r["occasion"] == "produced_by_step2"]
        if not produced:
            raise RuntimeError(
                "no push was produced; RunStep2 never ran, so there is no end-of-run "
                "fold-forward ratio to report"
            )
        return float(produced[-1]["ratio"])

    def summary(self) -> dict[str, Any]:
        """Everything a reader needs to avoid quoting the wrong row."""
        produced = [r for r in self.rows if r["occasion"] == "produced_by_step2"]
        consumed = [r for r in self.rows if r["occasion"] == "consumed_by_step1"]
        return {
            "label": self.label,
            "definition": (
                "sum(w_reco[pass_reco] * push[pass_reco]) / sum(w_reco[pass_reco]), "
                "transcribed from train_fullevent_nominal.py:576-577"
            ),
            "rows": list(self.rows),
            "pushes_produced": len(produced),
            "pushes_consumed_by_a_later_step1": len(consumed),
            "end_of_run_ratio": produced[-1]["ratio"] if produced else None,
            "end_of_run_is_recorded_not_reconstructed": bool(produced),
            "pushes_produced_but_never_consumed": max(0, len(produced) - max(0, len(consumed) - 1)),
            "reading": (
                "quote end_of_run_ratio. The last 'consumed_by_step1' row is a "
                "DIFFERENT quantity -- the push entering the final step 1 -- and "
                "substituting it was measured flipping the sign of (ratio - 1)."
            ),
            "n_pass_reco": int(self.pass_reco.sum()),
            "scope": "diagnostic; not a recovery or adoption claim",
        }
