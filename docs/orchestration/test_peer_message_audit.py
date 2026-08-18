#!/usr/bin/env python3
"""Tests for `peer_message_audit.py` (BEN-440).

THREE OF THESE TESTS ARE REGRESSIONS FOR DEFECTS THE SCRIPT SHIPPED WITH AND I FOUND BY RUNNING IT
ON REAL DATA -- one per false "undelivered". They are written in the direction the filter acts AND
the direction it does not, per this repo's rule that a narrowing gets a test showing it does NOT
fire, or widening it later looks free.

The sharpest is `test_reply_after_next_arrival_is_not_a_reply`. The first cut asked "any later send
to this peer?", which scored the census incident ANSWERED -- the reply it matched was 65 minutes
late and was answering the follow-up that asked why nobody had answered. A check that passes on the
one incident it was written to detect is worse than no check, because it certifies the failure.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import peer_message_audit as pma


def _tx(path: Path, records: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n")


def send(ts: str, to: str, tuid: str, msg_id: str | None) -> list[dict]:
    call = {"timestamp": ts, "message": {"content": [
        {"type": "tool_use", "id": tuid, "name": "SendMessage",
         "input": {"to": to, "summary": "s"}}]}}
    if msg_id is None:
        return [call]
    result = {"timestamp": ts, "message": {"content": [
        {"type": "tool_result", "tool_use_id": tuid,
         "content": [{"type": "text", "text": json.dumps({"success": True, "msg_id": msg_id})}]}]}}
    return [call, result]


def arrival(ts: str, peer: str, msg_id: str, nested: bool = False) -> dict:
    origin = {"kind": "peer", "msg_id": msg_id, "name": peer, "body": "hello"}
    return ({"timestamp": ts, "type": "attachment", "attachment": {"origin": origin}}
            if nested else {"timestamp": ts, "type": "user", "origin": origin})


class ScanTest(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = Path(tempfile.mkdtemp())

    def test_outbound_joins_its_receipt(self) -> None:
        p = self.dir / "a.jsonl"
        _tx(p, send("2026-01-01T00:00:00Z", "peer", "t1", "m-1"))
        out, _ = pma.scan(p)
        self.assertEqual([(o["to"], o["msg_id"]) for o in out], [("peer", "m-1")])

    def test_send_without_a_result_is_reported_with_no_msg_id(self) -> None:
        """Fate unknown != failed. It must not be counted as undelivered."""
        p = self.dir / "a.jsonl"
        _tx(p, send("2026-01-01T00:00:00Z", "peer", "t1", None))
        out, _ = pma.scan(p)
        self.assertEqual(len(out), 1)
        self.assertIsNone(out[0]["msg_id"])

    def test_arrival_top_level_origin(self) -> None:
        p = self.dir / "a.jsonl"
        _tx(p, [arrival("2026-01-01T00:00:00Z", "peer", "m-1")])
        _, inb = pma.scan(p)
        self.assertEqual([(i["peer"], i["msg_id"]) for i in inb], [("peer", "m-1")])

    def test_arrival_nested_under_attachment(self) -> None:
        """REGRESSION (defect 2): handling only the top-level shape found 8 of 14 real arrivals."""
        p = self.dir / "a.jsonl"
        _tx(p, [arrival("2026-01-01T00:00:00Z", "peer", "m-1", nested=True)])
        _, inb = pma.scan(p)
        self.assertEqual([i["msg_id"] for i in inb], ["m-1"])

    def test_non_peer_origin_is_not_an_arrival(self) -> None:
        """The direction the filter does NOT act: a non-peer origin must not be counted."""
        p = self.dir / "a.jsonl"
        _tx(p, [{"timestamp": "2026-01-01T00:00:00Z",
                 "origin": {"kind": "user", "msg_id": "m-1", "name": "someone"}}])
        _, inb = pma.scan(p)
        self.assertEqual(inb, [])

    def test_malformed_line_is_skipped_not_fatal(self) -> None:
        p = self.dir / "a.jsonl"
        p.write_text('{"broken": \n' + json.dumps(arrival("2026-01-01T00:00:00Z", "p", "m-1")) + "\n")
        _, inb = pma.scan(p)
        self.assertEqual([i["msg_id"] for i in inb], ["m-1"])


class ReportTest(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = Path(tempfile.mkdtemp())

    def _run(self, *extra: str) -> int:
        return pma.main(["--transcripts", str(self.dir), *extra])

    def test_delivered_send_is_not_undelivered(self) -> None:
        _tx(self.dir / "a.jsonl", send("2026-01-01T00:00:00Z", "b", "t1", "m-1"))
        _tx(self.dir / "b.jsonl", [arrival("2026-01-01T00:00:01Z", "a", "m-1")])
        self.assertEqual(self._run("--fail-on-undelivered"), pma.OK)

    def test_undelivered_send_fails_only_when_asked(self) -> None:
        _tx(self.dir / "a.jsonl", send("2026-01-01T00:00:00Z", "b", "t1", "m-lost"))
        self.assertEqual(self._run(), pma.OK)                        # report mode
        self.assertEqual(self._run("--fail-on-undelivered"), pma.UNDELIVERED)

    def test_reply_before_next_arrival_counts(self) -> None:
        _tx(self.dir / "a.jsonl",
            [arrival("2026-01-01T00:00:00Z", "peer", "m-1")]
            + send("2026-01-01T00:00:05Z", "peer", "t1", "r-1")
            + [arrival("2026-01-01T00:00:09Z", "peer", "m-2")])
        self.assertEqual(self._run(), pma.OK)

    def test_reply_after_next_arrival_is_not_a_reply(self) -> None:
        """REGRESSION (defect 3), and the incident itself.

        m-1 arrives, is never answered, the peer follows up with m-2, and only THEN does a send go
        out. The naive predicate ("any later send") called m-1 answered. It was not.
        """
        _tx(self.dir / "a.jsonl",
            [arrival("2026-01-01T00:00:00Z", "peer", "m-1"),
             arrival("2026-01-01T01:00:00Z", "peer", "m-2")]
            + send("2026-01-01T01:00:05Z", "peer", "t1", "r-1"))
        _, inb = pma.scan(self.dir / "a.jsonl")
        self.assertEqual(len(inb), 2)
        out, _ = pma.scan(self.dir / "a.jsonl")
        thread = sorted(inb, key=lambda r: r["ts"])
        deadline = thread[1]["ts"]
        replies = [o for o in out if thread[0]["ts"] < o["ts"] < deadline]
        self.assertEqual(replies, [], "a send after the follow-up is not a reply to the original")

    def test_usage_error_on_missing_dir(self) -> None:
        self.assertEqual(pma.main(["--transcripts", str(self.dir / "nope")]), pma.USAGE)


class RootsTest(unittest.TestCase):
    def test_default_roots_include_lane_worktrees(self) -> None:
        """REGRESSION (defect 1+3): one home / bare slug reported 610 of 1015 sends undelivered."""
        roots = pma.default_roots()
        homes = {r.parent.parent.name for r in roots}
        self.assertGreater(len(homes), 1, "must scan every Claude home, not just this session's")
        self.assertTrue(any("worktrees-lane" in r.name for r in roots),
                        "must scan each lane worktree's own projects dir")


if __name__ == "__main__":
    unittest.main(verbosity=2)
