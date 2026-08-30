"""Tests for dashboard_serve, the local viewer.

The tailnet fixtures are trimmed from real `tailscale status --json` output captured on
this laptop 2026-08-30, not written to match the parser.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dashboard_serve as ds

RUNNING = {
    "BackendState": "Running",
    "MagicDNSSuffix": "tail29db9c.ts.net",
    "Self": {
        "DNSName": "josephs-macbook-pro-2.tail29db9c.ts.net.",
        "TailscaleIPs": ["100.69.110.31", "fd7a:115c:a1e0::df01:6ecb"],
        "OS": "macOS",
    },
    "Peer": {
        "k1": {"DNSName": "iphone-14.tail29db9c.ts.net.", "OS": "iOS", "Online": True,
               "TailscaleIPs": ["100.69.21.66"]},
    },
}


class TailnetEndpointTest(unittest.TestCase):
    def test_binds_to_the_tailnet_ipv4_not_a_wildcard(self):
        # The whole security argument: it must NOT be 0.0.0.0, or the page also appears
        # on whatever untrusted network the laptop is joined to.
        ip, host, error = ds.tailnet_endpoint(RUNNING)
        self.assertEqual(ip, "100.69.110.31")
        self.assertNotIn(ip, ("0.0.0.0", "::"))
        self.assertEqual(error, "")

    def test_returns_the_magicdns_name_without_its_trailing_dot(self):
        _, host, _ = ds.tailnet_endpoint(RUNNING)
        self.assertEqual(host, "josephs-macbook-pro-2.tail29db9c.ts.net")

    def test_prefers_ipv4_over_the_ipv6_address(self):
        ip, _, _ = ds.tailnet_endpoint(RUNNING)
        self.assertNotIn(":", ip)

    def test_a_stopped_backend_is_refused_rather_than_bound(self):
        stopped = dict(RUNNING, BackendState="Stopped")
        ip, host, error = ds.tailnet_endpoint(stopped)
        self.assertIsNone(ip)
        self.assertIn("Stopped", error)

    def test_a_node_with_no_ipv4_is_refused(self):
        odd = dict(RUNNING, Self={"DNSName": "x.", "TailscaleIPs": ["fd7a:115c::1"]})
        ip, host, error = ds.tailnet_endpoint(odd)
        self.assertIsNone(ip)
        self.assertIn("no tailnet IPv4", error)

    def test_a_missing_self_node_does_not_raise(self):
        ip, host, error = ds.tailnet_endpoint({"BackendState": "Running"})
        self.assertIsNone(ip)
        self.assertTrue(error)


class FetchTest(unittest.TestCase):
    def test_a_missing_binary_reports_where_it_looked(self):
        saved = ds.TAILSCALE_BINARIES
        ds.TAILSCALE_BINARIES = ("/nonexistent/tailscale",)
        try:
            status, error = ds.tailscale_status()
        finally:
            ds.TAILSCALE_BINARIES = saved
        self.assertIsNone(status)
        self.assertIn("/nonexistent/tailscale", error)

    def test_an_unreadable_remote_returns_an_error_not_an_exception(self):
        payload, error = ds.fetch_remote("nosuchhost.invalid", "/nope", 5.0)
        self.assertIsNone(payload)
        self.assertTrue(error)


if __name__ == "__main__":
    unittest.main(verbosity=2)


class PeerDescriptionTest(unittest.TestCase):
    def test_an_online_peer_is_reported_plainly(self):
        self.assertEqual(ds.describe_peers(RUNNING), ["iphone-14 (iOS): online"])

    def test_a_backgrounded_phone_is_not_reported_as_a_problem(self):
        # Measured: iOS reports Online=false and drops `tailscale ping` while
        # backgrounded, then serves the page fine when you open the browser.
        asleep = dict(RUNNING, Peer={"k1": dict(RUNNING["Peer"]["k1"], Online=False)})
        line = ds.describe_peers(asleep)[0]
        self.assertIn("backgrounded", line)
        self.assertIn("will still reach this page", line)

    def test_an_offline_laptop_is_reported_as_offline(self):
        peer = {"DNSName": "other-mac.x.ts.net.", "OS": "macOS", "Online": False}
        self.assertEqual(ds.describe_peers({"Peer": {"k": peer}}), ["other-mac (macOS): offline"])

    def test_an_empty_tailnet_says_so(self):
        self.assertEqual(ds.describe_peers({}), ["no other devices on this tailnet"])
