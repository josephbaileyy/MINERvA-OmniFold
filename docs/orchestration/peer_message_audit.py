#!/usr/bin/env python3
"""Join peer-to-peer session messages across local transcripts: was it DELIVERED, was it ANSWERED?

WHY (BEN-440). Two lanes spent an hour disagreeing about whether a message had been delivered, and
NEITHER ENDPOINT COULD SETTLE IT. The sender had `{"success": true, ...}` from `SendMessage`, which
means *enqueued*, not *read*. The recipient had a transcript in which it could not tell "never
arrived" from "arrived and I did not act on it". Both endpoints were blind in the same direction, so
comparing their two accounts could not converge -- and it did not: the sender inferred a channel
defect, the recipient inferred a lost message, and BOTH inferences were wrong.

The information was never missing. It was missing FROM EITHER ENDPOINT. Every lane on this campaign
runs on one machine, so both jsonls are on local disk and **both sides record the same `msg_id`** --
sender in the `SendMessage` tool_result, recipient in `origin.msg_id`. A third reader can just join
them. That is this script. It replaces an argument between two partial accounts with one command.

TWO REPORTS, and they answer different questions:

  DELIVERY  -- for each outbound message, does its `msg_id` appear as an arrival in some transcript?
               An undelivered id is a real channel failure. Measured 2026-08-18 on the mediator's 14
               sends to this lane: 14/14 delivered, so the channel defect that was asserted is
               affirmatively ABSENT rather than merely unproven.

  REPLY     -- for each arrival, did the receiving session later `SendMessage` back to that sender?
               An arrival with no reply is the failure that DID happen: the lane answered its census
               in terminal text, which the asker cannot read, and looked capped for 65 minutes.

REPORT, NOT A GATE, and it must not become a pre-commit check: most arrivals legitimately need no
reply, and a transcript is not in the tree, so a committer who did nothing wrong could not make it
pass -- the admitting rule at `.githooks/pre-commit:11` (lane D, `OI-64`). `--fail-on-undelivered`
is opt-in for the one sub-report that IS a genuine invariant.

A NULL HERE IS ABOUT THE SEARCH, NOT THE WORLD (`BEN-389`). "Not delivered" means "no transcript in
the scanned directory records this id" -- a recipient in another project dir, on another machine, or
in the cloud produces the same null. Widen with --transcripts before believing it.

Usage:
  python3 docs/orchestration/peer_message_audit.py                      # both reports, this repo's dir
  python3 docs/orchestration/peer_message_audit.py --session <uuid>     # focus one lane
  python3 docs/orchestration/peer_message_audit.py --unanswered-only
  python3 docs/orchestration/peer_message_audit.py --fail-on-undelivered
Exit: 0 ok / 2 undelivered found (only with --fail-on-undelivered) / 3 usage error.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

OK, UNDELIVERED, USAGE = 0, 2, 3

PROJECT_SLUG = "-Users-josephbailey-local-research-MINERvA-OmniFold"


def default_roots() -> list[Path]:
    """Every Claude home on this machine AND every lane worktree's own project dir.

    SCAN WIDER THAN YOU THINK YOU NEED TO. This default is not caution, it is three measured
    misses -- and every one of them surfaced as a FALSE "undelivered", i.e. as a channel failure
    that did not exist. That is the exact error this script exists to stop an endpoint making, and
    the script made it three times before its first commit:

      1. ONE HOME, NOT ALL. First run: 7/7 of this lane's sends reported UNDELIVERED. All 7 had
         arrived. The recipient runs out of `~/.claude-personal`; this lane runs out of
         `~/.claude-school`. A co-located peer looked unreachable.
      2. ONE RECORD SHAPE, NOT BOTH. An arrival appears top-level OR nested under `attachment`;
         handling only the first found 8 of 14 real arrivals. A join that silently sees 57% of one
         side reads as loss on the other.
      3. THE BARE SLUG, NOT THE WORKTREES. Global run: 610 of 1015 sends UNDELIVERED. Lanes
         B/C/D/E each work in a `git worktree`, and a worktree gets its OWN projects directory --
         so the peers most likely to be messaged were precisely the ones not being scanned.

    One shape three times: the scan was narrower than the population, and the narrow scan reported
    a defect in the world rather than its own scope (`BEN-389`). Narrow deliberately with
    --transcripts; never narrow by accident.
    """
    roots: list[Path] = []
    for home in sorted(Path.home().glob(".claude*")):
        proj = home / "projects"
        if not proj.is_dir():
            continue
        # the repo's own dir AND every `--claude-worktrees-*` sibling belonging to this repo
        roots.extend(sorted(d for d in proj.glob(PROJECT_SLUG + "*") if d.is_dir()))
    return roots


def _iter_records(path: Path):
    with path.open(errors="replace") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield lineno, json.loads(line)
            except json.JSONDecodeError:
                continue  # a partially-flushed tail line is normal on a live session


def scan(path: Path) -> tuple[list[dict], list[dict]]:
    """Return (outbound, inbound) for one transcript.

    Outbound is a SendMessage tool_use joined to its tool_result by `tool_use_id` -- the id lives in
    the RESULT, not the call, so an unjoined call is a send whose fate is unknown rather than a send
    that failed. Inbound is the structured `origin` block, not a regex over escaped body text.
    """
    pending: dict[str, dict] = {}
    outbound: list[dict] = []
    inbound: list[dict] = []

    for lineno, rec in _iter_records(path):
        ts = rec.get("timestamp", "")

        # An arrival appears EITHER top-level OR nested under `attachment` -- both shapes are real
        # and the first cut of this script only handled the first, finding 8 of 14 real arrivals.
        # A join that silently sees 57% of one side reads as loss on the other.
        origin = rec.get("origin") or (rec.get("attachment") or {}).get("origin") or {}
        if origin.get("kind") == "peer" and origin.get("msg_id"):
            inbound.append({
                "session": path.stem, "line": lineno, "ts": ts,
                "msg_id": origin["msg_id"], "peer": origin.get("name", "?"),
                "body": (origin.get("body") or "").strip().replace("\n", " ")[:70],
            })

        content = (rec.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use" and block.get("name") == "SendMessage":
                inp = block.get("input") or {}
                pending[block.get("id", "")] = {
                    "session": path.stem, "line": lineno, "ts": ts,
                    "to": inp.get("to", "?"), "summary": (inp.get("summary") or "")[:70],
                }
            elif block.get("type") == "tool_result" and block.get("tool_use_id") in pending:
                call = pending.pop(block["tool_use_id"])
                text = block.get("content")
                if isinstance(text, list):
                    text = " ".join(c.get("text", "") for c in text if isinstance(c, dict))
                try:
                    call["msg_id"] = json.loads(text or "{}").get("msg_id")
                except (json.JSONDecodeError, TypeError):
                    call["msg_id"] = None
                outbound.append(call)

    for call in pending.values():      # calls with no result: fate UNKNOWN, not failed
        call.setdefault("msg_id", None)  # keep the record shape uniform, or callers must guess
        outbound.append(call)
    return outbound, inbound


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Join peer messages across session transcripts (BEN-440).")
    ap.add_argument("--transcripts", type=Path, action="append",
                    help="transcript dir (repeatable); default = every Claude home on this machine")
    ap.add_argument("--session", help="restrict the REPLY report to one session id (prefix ok)")
    ap.add_argument("--peer", help="restrict both reports to one peer name")
    ap.add_argument("--unanswered-only", action="store_true")
    ap.add_argument("--fail-on-undelivered", action="store_true")
    args = ap.parse_args(argv)

    roots = args.transcripts or default_roots()
    missing = [r for r in roots if not r.is_dir()]
    if missing:
        print(f"[peer-audit] not a directory: {missing[0]}", file=sys.stderr)
        return USAGE
    if not roots:
        print("[peer-audit] no Claude home holds this project", file=sys.stderr)
        return USAGE

    files = sorted(f for r in roots for f in r.glob("*.jsonl"))
    if not files:
        print(f"[peer-audit] no *.jsonl under {[str(r) for r in roots]}", file=sys.stderr)
        return USAGE
    print(f"[peer-audit] roots: {', '.join(str(r.parent.parent.name) for r in roots)}")

    all_out: list[dict] = []
    all_in: list[dict] = []
    for f in files:
        o, i = scan(f)
        all_out.extend(o)
        all_in.extend(i)

    arrived = {m["msg_id"]: m for m in all_in}
    print(f"[peer-audit] {len(files)} transcripts, {len(all_out)} sends, {len(all_in)} arrivals")

    # ---- DELIVERY -------------------------------------------------------------------------
    considered = [m for m in all_out if not args.peer or m["to"] == args.peer]
    undelivered = [m for m in considered if m.get("msg_id") and m["msg_id"] not in arrived]
    no_receipt = [m for m in considered if not m.get("msg_id")]
    print(f"[peer-audit] DELIVERY  {len(considered) - len(undelivered) - len(no_receipt)}"
          f"/{len(considered)} joined to an arrival"
          f"   undelivered={len(undelivered)}  no-send-receipt={len(no_receipt)}")
    for m in undelivered:
        print(f"[peer-audit]   UNDELIVERED {m['ts'][:23]} -> {m['to']}  {m['msg_id']}  {m['summary']}")
        print("[peer-audit]     (a recipient outside this directory produces the same null)")

    # ---- REPLY ----------------------------------------------------------------------------
    by_session: dict[str, list[dict]] = {}
    for m in all_out:
        by_session.setdefault(m["session"], []).append(m)

    # A reply must land BEFORE THE NEXT ARRIVAL FROM THAT PEER. The naive predicate -- "any later
    # send to this peer" -- marked the census ANSWERED because a reply came 65 minutes later, and
    # that reply was to the follow-up asking why nobody had answered. So the first cut of this check
    # scored a clean pass on the single incident it was written to detect. A stopping condition that
    # a later, unrelated event can satisfy measures nothing (`BEN-247`).
    seen: dict[tuple[str, str], list[dict]] = {}
    for m in sorted(all_in, key=lambda r: r["ts"]):
        seen.setdefault((m["session"], m["peer"]), []).append(m)

    focus = [m for m in all_in
             if (not args.session or m["session"].startswith(args.session))
             and (not args.peer or m["peer"] == args.peer)]
    unanswered = []
    for msg in sorted(focus, key=lambda r: r["ts"]):
        thread = seen[(msg["session"], msg["peer"])]
        idx = thread.index(msg)
        deadline = thread[idx + 1]["ts"] if idx + 1 < len(thread) else "9999"
        replies = [o for o in by_session.get(msg["session"], [])
                   if o["to"] == msg["peer"] and msg["ts"] < o["ts"] < deadline]
        if replies:
            if not args.unanswered_only:
                print(f"[peer-audit]   answered   {msg['ts'][:19]} <- {msg['peer']:22} "
                      f"reply {replies[0]['ts'][11:19]}  {msg['body'][:44]}")
        else:
            unanswered.append(msg)
            tail = "  (superseded by the peer's next message)" if deadline != "9999" else ""
            print(f"[peer-audit]   NO REPLY   {msg['ts'][:19]} <- {msg['peer']:22} "
                  f"{msg['body'][:44]}{tail}")
    print(f"[peer-audit] REPLY     {len(focus) - len(unanswered)}/{len(focus)} arrivals answered "
          f"on-channel; {len(unanswered)} never answered by SendMessage")
    print("[peer-audit] REPORT ONLY -- not a gate; see the module docstring for why.")

    if args.fail_on_undelivered and undelivered:
        return UNDELIVERED
    return OK


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
