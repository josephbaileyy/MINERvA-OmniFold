#!/usr/bin/env python3
"""Serve the dashboard locally, reading status.json over SSH on demand.

This is the delivery path when the project science gateway is declined: nothing is
published, no shared project resource is consumed, and no long-running process sits on a
login node.  The collector still runs under `scrontab` on the cluster; this only reads
the snapshot it already wrote.

    python3 dashboard_serve.py                       # http://127.0.0.1:8899
    python3 dashboard_serve.py --bind 0.0.0.0        # also reachable from a phone

`--bind 0.0.0.0` exposes the page to your local network (or your Tailscale/VPN
interface).  It is off by default because the snapshot names jobs, nodes and sessions,
and this server has no authentication of any kind.

The page fetches `/status.json` on its own refresh cycle, and each fetch runs one
`ssh <host> cat <path>`.  There is deliberately no local polling loop and no cached copy
on disk: the only state is on the cluster, so the page cannot show a stale file that
outlived the thing that produced it.  With the ControlMaster in `~/.ssh/config` the
round trip is well under a second.
"""

from __future__ import annotations

import argparse
import http.server
import json
import shutil
import socketserver
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_REMOTE = (
    "/pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration/state/"
    "dashboard/status.json"
)


def fetch_remote(host: str, remote_path: str, timeout: float) -> tuple[bytes | None, str]:
    """Read the snapshot over SSH.  Returns (payload, error)."""
    argv = ["ssh", "-o", "BatchMode=yes", f"-o=ConnectTimeout={int(timeout)}", host,
            f"cat {remote_path}"]
    try:
        done = subprocess.run(argv, capture_output=True, timeout=timeout + 15, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, f"{type(exc).__name__}: {exc}"
    if done.returncode != 0:
        return None, (done.stderr.decode("utf-8", "replace").strip()[:300]
                      or f"ssh exited {done.returncode}")
    try:
        json.loads(done.stdout)
    except json.JSONDecodeError as exc:
        return None, f"remote file is not JSON: {exc}"
    return done.stdout, ""


def make_handler(host: str, remote_path: str, timeout: float):
    class Handler(http.server.BaseHTTPRequestHandler):
        # Quieten the default one-line-per-request logging; the page polls.
        def log_message(self, fmt, *args):
            pass

        def _send(self, code: int, body: bytes, content_type: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            # The page cache-busts too, but a phone browser is persistent about this.
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):  # noqa: N802  (http.server's required spelling)
            path = self.path.split("?", 1)[0]
            if path in ("/", "/index.html", "/dashboard.html"):
                page = HERE / "dashboard.html"
                try:
                    self._send(200, page.read_bytes(), "text/html; charset=utf-8")
                except OSError as exc:
                    self._send(500, f"cannot read {page}: {exc}".encode(), "text/plain")
                return
            if path == "/status.json":
                payload, error = fetch_remote(host, remote_path, timeout)
                if payload is None:
                    # A JSON body with an explicit error, so the page renders its
                    # "cannot reach status.json" banner rather than a blank panel.
                    self._send(502, json.dumps({"error": error}).encode(), "application/json")
                else:
                    self._send(200, payload, "application/json")
                return
            self._send(404, b"not found", "text/plain")

    return Handler


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--host", default="saul.nersc.gov", help="SSH host holding the snapshot")
    parser.add_argument("--remote-path", default=DEFAULT_REMOTE)
    parser.add_argument("--port", type=int, default=8899)
    parser.add_argument(
        "--bind", default="127.0.0.1",
        help="0.0.0.0 to reach it from a phone on the same network or VPN (no auth!)",
    )
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()

    if shutil.which("ssh") is None:
        print("no ssh on PATH", file=sys.stderr)
        return 2
    if not (HERE / "dashboard.html").exists():
        print(f"dashboard.html is not beside this script ({HERE})", file=sys.stderr)
        return 2

    payload, error = fetch_remote(args.host, args.remote_path, args.timeout)
    if payload is None:
        # Fail loudly at startup rather than serving a page that 502s forever.
        print(f"cannot read {args.host}:{args.remote_path}\n  {error}", file=sys.stderr)
        print("\nIs the collector installed and has it run yet?", file=sys.stderr)
        return 1
    print(f"snapshot OK ({len(payload)} bytes) from {args.host}")
    if args.bind not in ("127.0.0.1", "localhost", "::1"):
        print(f"WARNING: serving on {args.bind} with NO authentication.")
    print(f"  http://{'127.0.0.1' if args.bind == '0.0.0.0' else args.bind}:{args.port}/")
    with Server((args.bind, args.port), make_handler(args.host, args.remote_path, args.timeout)) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
