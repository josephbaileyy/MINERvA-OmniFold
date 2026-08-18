#!/usr/bin/env python3
"""Tests for `oi_owner_report.py`'s classifier (BEN-395, extended by BEN-442).

Both directions for every bucket. The terminal and role-name rules are new and each one REDUCES or
RE-LABELS the reported backlog, so each gets a test that it fires AND a test that it does not --
a narrowing without a negative test looks free to widen later.
"""

from __future__ import annotations

import unittest

import oi_owner_report as oi


class ClassifyTest(unittest.TestCase):
    def test_a_named_lane_is_routable(self) -> None:
        self.assertEqual(oi.classify(" lane D ", "OPEN"), "routable")
        self.assertEqual(oi.classify(" C (PET) ", "OPEN"), "routable")
        self.assertEqual(oi.classify(" Joseph ", "OPEN"), "routable")

    def test_explicit_unowned_wins_over_everything(self) -> None:
        self.assertEqual(oi.classify(" **UNOWNED** — area: PET ", "OPEN"), "explicitly-unowned")

    def test_terminal_state_needs_no_owner(self) -> None:
        for state in ("DISCHARGED 2026-08-13", "**SUPERSEDED** 2026-08-13", "CLOSED 2026-08-17",
                      "WITHDRAWN the same hour", "RESOLVED 2026-08-13", "DEFERRED by Joseph",
                      "PREMISE FALSE 2026-08-13"):
            self.assertEqual(oi.classify(" storage ", state), "terminal-no-owner-needed", state)

    def test_a_live_row_is_not_terminal_just_for_saying_closed_later(self) -> None:
        """The direction the rule must NOT act: nearly every long row mentions 'closed' somewhere.

        Only the state cell's OPENING declares the state, which is why TERMINAL anchors with ^.
        """
        live = "OPEN — this was nearly closed 2026-08-14 but the discharge did not hold"
        self.assertEqual(oi.classify(" storage ", live), "area-only")

    def test_role_name_with_no_holder_is_its_own_bucket(self) -> None:
        for cell in (" cluster freeze owner ", " event-loop owner ", " PET input owner "):
            self.assertEqual(oi.classify(cell, "OPEN"), "role-named-no-holder", cell)

    def test_a_bare_area_is_not_a_role_name(self) -> None:
        self.assertEqual(oi.classify(" storage ", "OPEN"), "area-only")
        self.assertEqual(oi.classify(" PET diagnostics ", "OPEN"), "area-only")

    def test_a_real_owner_ending_in_owner_is_still_routable(self) -> None:
        """`Joseph` outranks the role-name rule -- routable is tested before role-named."""
        self.assertEqual(oi.classify(" Joseph, the cluster freeze owner ", "OPEN"), "routable")

    def test_a_pointer_to_another_row_is_routable(self) -> None:
        """A row that delegates to another row's owner IS routable -- one hop, but a defined one."""
        self.assertEqual(oi.classify(" see `OI-122` — **routable via `OI-122`** ", "OPEN"), "routable")

    def test_a_bare_cross_reference_is_not_an_owner(self) -> None:
        """The direction it must NOT act: mentioning another item is not delegating to it."""
        self.assertEqual(oi.classify(" storage, cf. OI-122 ", "OPEN"), "area-only")

    def test_state_is_optional_and_defaults_to_not_terminal(self) -> None:
        self.assertEqual(oi.classify(" storage "), "area-only")


if __name__ == "__main__":
    unittest.main(verbosity=2)
