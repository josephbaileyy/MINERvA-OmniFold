#!/usr/bin/env python3
"""Serve the dashboard locally, reading status.json over SSH on demand.

This is the delivery path when the project science gateway is declined: nothing is
published, no shared project resource is consumed, and no long-running process sits on a
login node.  The collector still runs under `scrontab` on the cluster; this only reads
the snapshot it already wrote.

    python3 dashboard_serve.py                       # http://127.0.0.1:8899
    python3 dashboard_serve.py --bind 0.0.0.0        # also reachable from a phone

`--tailscale` binds to the tailnet address ONLY, so the page is reachable from your other
Tailscale devices and from nothing else -- not from the coffee-shop wifi you are on.
That is the difference from `--bind 0.0.0.0`, which exposes it on every interface.  This
server has no authentication of any kind, so which interface it listens on IS the access
control.  Tailscale carries it over WireGuard, so plain HTTP here is encrypted in
transit; it is not encrypted if you use `--bind 0.0.0.0` on a normal LAN.

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
import threading
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


def collect_local(timeout: float = 30.0) -> tuple[dict | None, str]:
    """Run the collector's local-only mode on THIS machine.

    LLM sessions can only be seen where they run, so the cluster snapshot cannot carry
    them.  Reusing `dashboard_collector.py --local-only` keeps one implementation of the
    scan and of the Source/age bookkeeping rather than a second copy here.
    """
    argv = [sys.executable, str(HERE / "dashboard_collector.py"), "--local-only"]
    try:
        done = subprocess.run(argv, capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, f"{type(exc).__name__}: {exc}"
    if done.returncode != 0:
        return None, (done.stderr.decode("utf-8", "replace").strip()[:300]
                      or f"exited {done.returncode}")
    try:
        return json.loads(done.stdout), ""
    except json.JSONDecodeError as exc:
        return None, f"--local-only printed non-JSON: {exc}"


def merge_local(cluster: dict, local: dict | None, local_error: str) -> dict:
    """Add the locally-measured panels to the cluster snapshot.

    Both halves keep their own `measured_on` and their own age, so the page never
    implies that one host observed everything.  A failed local collection becomes a
    FAILED SOURCE rather than an absent panel -- absence would render as "no local
    sessions", which is a claim we did not measure.
    """
    merged = dict(cluster)
    merged["sources"] = list(cluster.get("sources") or [])
    if local is None:
        merged["sources"].append({
            "name": "local_llm_sessions", "ok": False, "age_seconds": None,
            "error": local_error or "local collection failed", "stale": None,
            "stale_after_seconds": None, "detail": {}, "measured_on": "this device",
        })
        merged["local_sessions"] = None
        return merged
    merged["sources"].extend(local.get("sources") or [])
    merged["local_sessions"] = local.get("local_sessions")
    return merged


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
                    return
                try:
                    cluster = json.loads(payload)
                except json.JSONDecodeError as exc:
                    self._send(502, json.dumps({"error": str(exc)}).encode(), "application/json")
                    return
                local, local_error = collect_local()
                merged = merge_local(cluster, local, local_error)
                self._send(200, json.dumps(merged).encode(), "application/json")
                return
            self._send(404, b"not found", "text/plain")

    return Handler


TAILSCALE_BINARIES = (
    "tailscale",
    "/usr/local/bin/tailscale",
    "/opt/homebrew/bin/tailscale",
    "/Applications/Tailscale.app/Contents/MacOS/Tailscale",
)


def tailscale_status() -> tuple[dict | None, str]:
    """Parse `tailscale status --json`, trying the usual install locations."""
    for candidate in TAILSCALE_BINARIES:
        binary = candidate if candidate.startswith("/") else shutil.which(candidate)
        if not binary or not Path(binary).exists():
            continue
        try:
            done = subprocess.run([binary, "status", "--json"],
                                  capture_output=True, timeout=20, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return None, f"{binary}: {type(exc).__name__}: {exc}"
        if done.returncode != 0:
            return None, f"{binary} status exited {done.returncode}: " \
                         f"{done.stderr.decode('utf-8', 'replace').strip()[:200]}"
        try:
            return json.loads(done.stdout), ""
        except json.JSONDecodeError as exc:
            return None, f"{binary} status printed non-JSON: {exc}"
    return None, "no tailscale binary found (looked in: " + ", ".join(TAILSCALE_BINARIES) + ")"


def tailnet_endpoint(status: dict) -> tuple[str | None, str | None, str]:
    """(IPv4 to bind, MagicDNS hostname, error) for this machine on the tailnet.

    Binds to the IPv4 specifically rather than 0.0.0.0: the whole point of choosing
    Tailscale over `--bind 0.0.0.0` is that the listener must not appear on any other
    network the laptop happens to be joined to.
    """
    state = status.get("BackendState")
    if state != "Running":
        return None, None, f"Tailscale backend is {state!r}, not 'Running' -- is it connected?"
    self_node = status.get("Self") or {}
    addresses = self_node.get("TailscaleIPs") or []
    ipv4 = next((a for a in addresses if ":" not in a), None)
    if not ipv4:
        return None, None, f"no tailnet IPv4 for this machine (got {addresses})"
    host = (self_node.get("DNSName") or "").rstrip(".") or None
    return ipv4, host, ""


MOBILE_OS = {"iOS", "android"}


def describe_peers(status: dict) -> list[str]:
    """One line per tailnet peer, without turning a sleeping phone into an alarm.

    A backgrounded iOS/Android client reports Online=false and does not answer
    `tailscale ping`, yet it connects fine the moment you open a browser on it -- the
    handset wakes its tunnel on demand.  Printing a bare "0 devices online" would read
    as a broken tailnet when nothing is wrong, so the mobile case is named explicitly.
    """
    lines = []
    for peer in sorted((status.get("Peer") or {}).values(),
                       key=lambda p: (p.get("DNSName") or "")):
        name = (peer.get("DNSName") or "?").rstrip(".").split(".")[0]
        host_os = peer.get("OS") or "?"
        if peer.get("Online"):
            lines.append(f"{name} ({host_os}): online")
        elif host_os in MOBILE_OS:
            lines.append(f"{name} ({host_os}): reported offline -- normal while the app is "
                         f"backgrounded; it will still reach this page when you open it")
        else:
            lines.append(f"{name} ({host_os}): offline")
    return lines or ["no other devices on this tailnet"]


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main() -> int:
    # Line-buffer stdout: this script is often run backgrounded with output
    # redirected, and its startup banner carries the URL to open on the phone.
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, OSError):
        pass

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--host", default="saul.nersc.gov", help="SSH host holding the snapshot")
    parser.add_argument("--remote-path", default=DEFAULT_REMOTE)
    parser.add_argument("--port", type=int, default=8899)
    parser.add_argument(
        "--bind", default="127.0.0.1",
        help="0.0.0.0 to reach it from a phone on the same network (no auth, and not "
             "encrypted -- prefer --tailscale)",
    )
    parser.add_argument(
        "--tailscale", action="store_true",
        help="bind to this machine's tailnet address only, and print the URL to open "
             "on your other Tailscale devices",
    )
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()

    if shutil.which("ssh") is None:
        print("no ssh on PATH", file=sys.stderr)
        return 2
    if not (HERE / "dashboard.html").exists():
        print(f"dashboard.html is not beside this script ({HERE})", file=sys.stderr)
        return 2

    binds, magic_host = [args.bind], None
    if args.tailscale:
        status, error = tailscale_status()
        if status is None:
            print(f"--tailscale: {error}", file=sys.stderr)
            return 2
        tailnet_ip, magic_host, error = tailnet_endpoint(status)
        if tailnet_ip is None:
            print(f"--tailscale: {error}", file=sys.stderr)
            return 2
        # Loopback as well as the tailnet address, so the machine running the server can
        # still use http://127.0.0.1 -- binding the tailnet IP alone made localhost
        # refuse the connection, which is a surprising way to lose the local view.
        # Loopback adds no exposure: it is reachable only from this machine.
        binds = ["127.0.0.1", tailnet_ip]
        print(f"tailnet {status.get('MagicDNSSuffix', '?')}:")
        for peer in describe_peers(status):
            print(f"  {peer}")

    payload, error = fetch_remote(args.host, args.remote_path, args.timeout)
    if payload is None:
        # Fail loudly at startup rather than serving a page that 502s forever.
        print(f"cannot read {args.host}:{args.remote_path}\n  {error}", file=sys.stderr)
        print("\nIs the collector installed and has it run yet?", file=sys.stderr)
        return 1
    print(f"snapshot OK ({len(payload)} bytes) from {args.host}")
    if args.tailscale:
        print("serving on this machine and on the tailnet (no other network):")
        if magic_host:
            print(f"  http://{magic_host}:{args.port}/       <- other devices (phone, PC)")
        for address in binds:
            print(f"  http://{address}:{args.port}/")
    elif binds[0] in ("127.0.0.1", "localhost", "::1"):
        print(f"  http://{binds[0]}:{args.port}/")
    else:
        print(f"WARNING: serving on {binds[0]} with NO authentication and no encryption.")
        print(f"  http://{binds[0]}:{args.port}/")

    handler = make_handler(args.host, args.remote_path, args.timeout)
    servers = []
    try:
        for address in binds:
            try:
                servers.append(Server((address, args.port), handler))
            except OSError as exc:
                print(f"cannot bind {address}:{args.port}: {exc}", file=sys.stderr)
        if not servers:
            return 1
        for httpd in servers[1:]:
            threading.Thread(target=httpd.serve_forever, daemon=True).start()
        try:
            servers[0].serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")
    finally:
        for httpd in servers:
            httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
