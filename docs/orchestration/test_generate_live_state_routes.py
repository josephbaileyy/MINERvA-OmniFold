"""Regression tests for structured LIVE-STATE routing and OI-181."""

from __future__ import annotations

import hashlib
import json
import pathlib
import tempfile
import unittest

import generate_live_state
from generate_live_state import (
    ALLOWED_ROUTE_QUEUES,
    Route,
    RouteSnapshot,
    inspect_route_registry,
    render,
    validate_config,
)


WORK_HEADER = (
    "item\tsource_record\tlifecycle\tqueue\tpromotion\towner_id\timpact\turgency"
    "\tartifact\tnext_action\tauthority\tterminal_criterion\tevidence\tstate_digest\n"
)
INVENTORY_HEADER = (
    "source_record\tlifecycle\tqueue\tclassification_rule\tsource_row_sha256"
    "\tstate_prefix\n"
)
OPEN_ROW = "| OI-181 | OPEN | owner | blocker | action | detail | 2026-09-02 |"


def register_row(
    item: str = "OI-181",
    source: str = "OI-181",
    *,
    lifecycle: str = "active",
    queue: str = "NOW",
    promotion: str = "promoted",
) -> str:
    """One 14-column register row in the frozen interface (INTEGRATION-20260903 §1.1)."""
    return (
        f"{item}\t{source}\t{lifecycle}\t{queue}\t{promotion}\tlane_c\tinfrastructure\tP1"
        f"\t-\tignored\trecord\tcommit\tdocs/OPEN_ITEMS.md (`{source}`)\tsha256:deadbeef\n"
    )


def write_registry(
    directory: pathlib.Path,
    *,
    open_row: str = OPEN_ROW,
    state_prefix: str = "OPEN",
    rows: str | None = None,
    inventory_lifecycle: str = "active",
) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    """Write the smallest internally consistent route registry."""
    work_items = directory / "work-items.tsv"
    source_inventory = directory / "source-record-inventory.tsv"
    open_items = directory / "OPEN_ITEMS.md"
    work_items.write_text(
        WORK_HEADER + (register_row() if rows is None else rows),
        encoding="utf-8",
    )
    digest = hashlib.sha256(open_row.encode()).hexdigest()
    source_inventory.write_text(
        INVENTORY_HEADER
        + f"OI-181\t{inventory_lifecycle}\tNOW\tdeclared\t{digest}"
        + f"\t{state_prefix}\n",
        encoding="utf-8",
    )
    open_items.write_text(open_row + "\n", encoding="utf-8")
    return work_items, source_inventory, open_items


def minimal_config() -> dict:
    return {
        "schema_version": 2,
        "measurement_ttl_seconds": {
            "compute": 300,
            "wake": 300,
            "provider_capacity": 3600,
        },
        "route_registry": {
            "work_items": "work-items.tsv",
            "source_inventory": "source-record-inventory.tsv",
            "open_items": "OPEN_ITEMS.md",
        },
        "evidence_routes": [{"label": "Open items", "path": "OPEN_ITEMS.md"}],
        "jobs": [],
        "wake": {"waker": True},
    }


class RouteRegistryHealthTests(unittest.TestCase):
    def inspect(self, paths: tuple[pathlib.Path, pathlib.Path, pathlib.Path]):
        work_items, source_inventory, open_items = paths
        return inspect_route_registry(
            work_items_path=work_items,
            source_inventory_path=source_inventory,
            open_items_path=open_items,
        )

    def test_positive_sources_produce_a_structured_route(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot = self.inspect(write_registry(pathlib.Path(directory)))
        self.assertEqual(snapshot.health, "HEALTHY")
        self.assertEqual(snapshot.routes, (Route("OI-181", "NOW", "OI-181"),))

    def test_stale_inventory_hash_withholds_routes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            paths = write_registry(root)
            paths[2].write_text(OPEN_ROW.replace("OPEN", "RULED") + "\n")
            snapshot = self.inspect(paths)
        self.assertEqual(snapshot.health, "STALE")
        self.assertEqual(snapshot.routes, ())
        self.assertIn("source row hash mismatch", snapshot.detail)

    def test_unavailable_registry_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            snapshot = inspect_route_registry(
                work_items_path=root / "missing-work-items.tsv",
                source_inventory_path=root / "missing-inventory.tsv",
                open_items_path=root / "missing-open-items.md",
            )
        self.assertEqual(snapshot.health, "UNAVAILABLE")
        self.assertEqual(snapshot.routes, ())

    def test_contradictory_source_prefix_withholds_routes(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot = self.inspect(
                write_registry(pathlib.Path(directory), state_prefix="RULED")
            )
        self.assertEqual(snapshot.health, "CONTRADICTORY")
        self.assertEqual(snapshot.routes, ())
        self.assertIn("state prefix contradicts", snapshot.detail)


class FrozenRegisterInterfaceTests(unittest.TestCase):
    """The generator consumes the register exactly as frozen on 2026-09-03."""

    def inspect(self, paths):
        work_items, source_inventory, open_items = paths
        return inspect_route_registry(
            work_items_path=work_items,
            source_inventory_path=source_inventory,
            open_items_path=open_items,
        )

    def test_queue_vocabulary_is_bound_to_policy_json(self):
        policy_path = (
            pathlib.Path(generate_live_state.__file__).resolve().parent
            / "control-plane"
            / "policy.json"
        )
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        self.assertEqual(ALLOWED_ROUTE_QUEUES, frozenset(policy["routing"]["queues"]))

    def test_backlog_rows_are_inventory_not_routes(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot = self.inspect(
                write_registry(pathlib.Path(directory), rows=register_row(promotion="backlog"))
            )
        self.assertEqual(snapshot.health, "HEALTHY")
        self.assertEqual(snapshot.routes, ())

    def test_retired_record_is_skipped_not_contradictory(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot = self.inspect(
                write_registry(
                    pathlib.Path(directory),
                    rows=register_row(lifecycle="retired", queue="-", promotion="-"),
                    inventory_lifecycle="retired",
                )
            )
        self.assertEqual(snapshot.health, "HEALTHY")
        self.assertEqual(snapshot.routes, ())

    def test_register_lifecycle_contradicting_inventory_withholds_routes(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot = self.inspect(
                write_registry(pathlib.Path(directory), inventory_lifecycle="retired")
            )
        self.assertEqual(snapshot.health, "CONTRADICTORY")
        self.assertIn("register lifecycle", snapshot.detail)
        self.assertEqual(snapshot.routes, ())

    def test_sub_item_row_inherits_lifecycle_and_declares_its_own_queue(self):
        rows = register_row(promotion="backlog") + register_row(
            "OI-181(a)", lifecycle="-", queue="WAITING-JOSEPH"
        )
        with tempfile.TemporaryDirectory() as directory:
            snapshot = self.inspect(write_registry(pathlib.Path(directory), rows=rows))
        self.assertEqual(snapshot.health, "HEALTHY")
        self.assertEqual(snapshot.routes, (Route("OI-181(a)", "WAITING-JOSEPH", "OI-181"),))

    def test_new_blocked_tokens_are_valid_and_unknown_tokens_are_not(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            accepted = self.inspect(
                write_registry(root, rows=register_row("OI-181(a)", lifecycle="-", queue="BLOCKED-INTERNAL"))
            )
            rejected = self.inspect(
                write_registry(root, rows=register_row("OI-181(a)", lifecycle="-", queue="SOMEDAY"))
            )
        self.assertEqual(accepted.health, "HEALTHY")
        self.assertEqual(accepted.routes[0].queue, "BLOCKED-INTERNAL")
        self.assertEqual(rejected.health, "CONTRADICTORY")
        self.assertIn("invalid declared queue", rejected.detail)

    def test_removed_queue_override_column_is_refused(self):
        legacy = (
            "item\tsource_record\tqueue_override\towner_id\timpact\turgency"
            "\tnext_action\tevidence\nOI-181\tOI-181\t-\tlane_c\tx\tP1\ty\tz\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            paths = write_registry(root)
            paths[0].write_text(legacy, encoding="utf-8")
            snapshot = self.inspect(paths)
        self.assertEqual(snapshot.health, "UNAVAILABLE")
        self.assertIn("queue_override", snapshot.detail)


class AuthoredProseRegressionTests(unittest.TestCase):
    def test_stale_json_prose_cannot_overwrite_the_structured_route(self):
        marker = "STALE JSON SAYS THE GRADE IS UNLANDED"
        config = minimal_config()
        config["current_dag_node"] = marker
        config["state"] = marker
        config["next_authorized_action"] = marker
        with self.assertRaisesRegex(ValueError, "legacy authored operational prose"):
            validate_config(config)

        rendered = render(
            config,
            {},
            {"profiles": {}, "accounts": {}, "warnings": []},
            1,
            [],
            {"head": "abc1234", "dirty_count": 0, "host": "test-host"},
            {"waker_status": {"watches": [], "events": [], "last_tick": {}}},
            "2026-09-02T12:00:00Z",
            route_snapshot=RouteSnapshot(
                "HEALTHY",
                "one current route",
                (Route("OI-181", "NOW", "OI-181"),),
            ),
        )
        self.assertNotIn(marker, rendered)
        self.assertIn("[`OI-181`](../OPEN_ITEMS.md)", rendered)


if __name__ == "__main__":
    unittest.main()
