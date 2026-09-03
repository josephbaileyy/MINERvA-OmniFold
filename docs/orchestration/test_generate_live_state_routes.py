"""Regression tests for structured LIVE-STATE routing and OI-181."""

from __future__ import annotations

import hashlib
import pathlib
import tempfile
import unittest

from generate_live_state import (
    Route,
    RouteSnapshot,
    inspect_route_registry,
    render,
    validate_config,
)


WORK_HEADER = (
    "item\tsource_record\tqueue_override\towner_id\timpact\turgency"
    "\tnext_action\tevidence\n"
)
INVENTORY_HEADER = (
    "source_record\tlifecycle\tqueue\tclassification_rule\tsource_row_sha256"
    "\tstate_prefix\n"
)
OPEN_ROW = "| OI-181 | OPEN | owner | blocker | action | detail | 2026-09-02 |"


def write_registry(
    directory: pathlib.Path,
    *,
    open_row: str = OPEN_ROW,
    state_prefix: str = "OPEN",
) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    """Write the smallest internally consistent route registry."""
    work_items = directory / "work-items.tsv"
    source_inventory = directory / "source-record-inventory.tsv"
    open_items = directory / "OPEN_ITEMS.md"
    work_items.write_text(
        WORK_HEADER
        + "OI-181\tOI-181\t-\tlane_c\tinfrastructure\tP1\tignored"
        "\tdocs/OPEN_ITEMS.md (`OI-181`)\n",
        encoding="utf-8",
    )
    digest = hashlib.sha256(open_row.encode()).hexdigest()
    source_inventory.write_text(
        INVENTORY_HEADER
        + f"OI-181\tactive\tNOW\tsafe-default-active\t{digest}"
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
