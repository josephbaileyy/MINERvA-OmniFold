"""COVFIX's ST3/ST6 reservation ledger (COVFIX-DECLARATION.md rev 11.4 section 3.3: "ST3 and ST6, one reservation
ledger"). One append-only JSONL file in the campaign directory, serialized under flock, keyed by allocation job ID.

  intent      before any submission: a random 128-bit intent ID, the phase and the reservation are persisted (fsync);
              the job name is covfix_<phase>_<intent>. Refused while any earlier intent has no recorded job ID.
  submitted   after sbatch: the job ID for the intent.
  reconcile   from sacct rows (JobID, JobName, State, NNodes, ElapsedRaw): an intent with no job ID is matched by its
              job name (exactly one job; several, or none, keep it open and unresolved); a terminal job's charge,
              NNodes x ElapsedRaw / 3600 node-h, is recorded once. Anything uncertain keeps the reservation open.
  gate        atomic under the flock: reconciled charges + open reservations + the new reservation must stay within
              the phase's cap group and within the pinned ceiling.
  accept      each expected toy ID of a (phase, arm) is accepted exactly once, with its verified product's sha256.

Reservations are nodes x --time, the time rounded up to whole minutes (allocation-level walltime rounding).
MEASURES: nothing. CANNOT AUTHORIZE: a submission; it only refuses one that would not fit.
"""
from __future__ import annotations

import contextlib
import fcntl
import json
import math
import os
import re
import secrets
from pathlib import Path

LEDGER, LOCK = "LEDGER.jsonl", "LEDGER.lock"
TERMINAL = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "OUT_OF_MEMORY", "NODE_FAIL", "PREEMPTED", "BOOT_FAIL",
            "DEADLINE"}
PHASE = re.compile(r"[a-z0-9]{1,16}")
JOB_NAME = re.compile(r"covfix_([a-z0-9]{1,16})_([0-9a-f]{32})")
EPS = 1e-9                     # node-h: the gate's comparison slack for float sums


class Refusal(Exception):
    """The ledger refuses: nothing was appended."""


def reservation_nodeh(nodes: int, time_limit_s: int) -> float:
    if not (isinstance(nodes, int) and nodes >= 1 and isinstance(time_limit_s, int) and time_limit_s >= 1):
        raise Refusal("nodes and the time limit must be positive integers")
    return nodes * math.ceil(time_limit_s / 60) / 60.0


def sacct_state(raw: str) -> str:
    """sacct prints e.g. 'CANCELLED by 12345'; the first word is the state."""
    return raw.split()[0] if raw.split() else ""


class Ledger:
    def __init__(self, campaign_dir: Path, caps: dict, groups: dict, ceiling: float):
        """caps: {group: node-h}; groups: {phase: group}; ceiling: the pinned total (541.50 at binding 1)."""
        self.dir = Path(campaign_dir)
        self.caps, self.groups, self.ceiling = dict(caps), dict(groups), float(ceiling)
        if set(self.groups.values()) - set(self.caps):
            raise Refusal("a phase maps to a group with no cap")

    # ------------------------------------------------------------------------------------------------ storage
    @contextlib.contextmanager
    def locked(self):
        self.dir.mkdir(parents=True, exist_ok=True)
        with open(self.dir / LOCK, "a") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)

    def _entries(self) -> list:
        p = self.dir / LEDGER
        if not p.exists():
            return []
        out = []
        for i, line in enumerate(p.read_text().splitlines(), 1):
            try:
                out.append(json.loads(line))
            except ValueError as e:
                raise Refusal(f"ledger line {i} is not JSON") from e
        return out

    def _append(self, entry: dict) -> None:
        with open(self.dir / LEDGER, "a") as fh:
            fh.write(json.dumps(entry, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    # -------------------------------------------------------------------------------------------------- state
    def state(self) -> dict:
        intents, toys = {}, {}
        for e in self._entries():
            k = e.get("kind")
            if k == "intent":
                intents[e["intent"]] = {"phase": e["phase"], "reservation": e["reservation"], "job": None,
                                        "charge": None}
            elif k == "submitted":
                intents[e["intent"]]["job"] = e["job"]
            elif k == "reconciled":
                intents[e["intent"]]["charge"] = e["charge"]
            elif k == "accepted":
                toys[(e["phase"], e["arm"], e["toy"])] = e["sha256"]
            else:
                raise Refusal(f"unknown ledger entry kind {k!r}")
        return {"intents": intents, "toys": toys}

    def totals(self, st: dict, group: str | None = None) -> dict:
        spent = held = 0.0
        for it in st["intents"].values():
            if group is not None and self.groups[it["phase"]] != group:
                continue
            if it["charge"] is None:
                held += it["reservation"]
            else:
                spent += it["charge"]
        return {"spent": spent, "held": held}

    # --------------------------------------------------------------------------------------------- operations
    def new_intent(self, phase: str, nodes: int, time_limit_s: int) -> dict:
        """Gate and persist an intent. Returns {"intent", "job_name", "reservation", "gate"}."""
        if not PHASE.fullmatch(phase) or phase not in self.groups:
            raise Refusal(f"unknown phase {phase!r}")
        res = reservation_nodeh(nodes, time_limit_s)
        with self.locked():
            st = self.state()
            unrecorded = [i for i, it in st["intents"].items() if it["job"] is None]
            if unrecorded:
                raise Refusal(f"{len(unrecorded)} intent(s) have no job ID: reconcile from sacct first")
            group = self.groups[phase]
            tot, gt = self.totals(st), self.totals(st, group)
            gate = {"total": tot["spent"] + tot["held"] + res, "ceiling": self.ceiling,
                    "group": group, "group_total": gt["spent"] + gt["held"] + res, "cap": self.caps[group]}
            if gate["total"] > self.ceiling + EPS or gate["group_total"] > self.caps[group] + EPS:
                raise Refusal(f"the gate refuses: {gate}")
            intent = secrets.token_hex(16)
            self._append({"kind": "intent", "intent": intent, "phase": phase, "nodes": nodes,
                          "time_limit_s": time_limit_s, "reservation": res})
        return {"intent": intent, "job_name": f"covfix_{phase}_{intent}", "reservation": res, "gate": gate}

    def record_submission(self, intent: str, job: str) -> None:
        if not re.fullmatch(r"[0-9]+", str(job)):
            raise Refusal("a job ID is numeric")
        with self.locked():
            st = self.state()
            if intent not in st["intents"]:
                raise Refusal("unknown intent")
            if st["intents"][intent]["job"] is not None:
                raise Refusal("the intent already has a job ID")
            if any(it["job"] == str(job) for it in st["intents"].values()):
                raise Refusal("the job ID is already recorded for another intent")
            self._append({"kind": "submitted", "intent": intent, "job": str(job)})

    def reconcile(self, rows: list[dict]) -> dict:
        """rows: sacct allocation rows {"JobID", "JobName", "State", "NNodes", "ElapsedRaw"}. Returns counts of what
        was recorded and what stays open."""
        out = {"matched": 0, "charged": 0, "unresolved": [], "open": 0}
        with self.locked():
            st = self.state()
            by_name: dict = {}
            for r in rows:
                m = JOB_NAME.fullmatch(r.get("JobName", ""))
                if m and re.fullmatch(r"[0-9]+", str(r.get("JobID", ""))):
                    by_name.setdefault(m.group(2), []).append(r)
            by_job = {str(r.get("JobID")): r for r in rows}
            for iid, it in st["intents"].items():
                if it["job"] is None:
                    cands = by_name.get(iid, [])
                    if len(cands) == 1 and str(cands[0]["JobID"]) not in {x["job"] for x in st["intents"].values()}:
                        self._append({"kind": "submitted", "intent": iid, "job": str(cands[0]["JobID"]),
                                      "via": "sacct job name"})
                        it["job"] = str(cands[0]["JobID"])
                        out["matched"] += 1
                    else:
                        out["unresolved"].append(iid)
                        continue
                if it["charge"] is None:
                    r = by_job.get(it["job"])
                    if r is not None and sacct_state(r.get("State", "")) in TERMINAL:
                        try:
                            charge = int(r["NNodes"]) * int(r["ElapsedRaw"]) / 3600.0
                        except (KeyError, ValueError):
                            out["open"] += 1
                            continue
                        self._append({"kind": "reconciled", "intent": iid, "job": it["job"],
                                      "state": sacct_state(r["State"]), "charge": charge})
                        out["charged"] += 1
                    else:
                        out["open"] += 1
        return out

    def accept(self, phase: str, arm: str, toy: str, sha256: str, expected: set) -> None:
        if toy not in expected:
            raise Refusal(f"toy {toy!r} is not expected in {phase}/{arm}")
        if not re.fullmatch(r"[0-9a-f]{64}", sha256):
            raise Refusal("a product sha256 is 64 lowercase hex")
        with self.locked():
            if (phase, arm, toy) in self.state()["toys"]:
                raise Refusal(f"toy {toy!r} of {phase}/{arm} is already accepted")
            self._append({"kind": "accepted", "phase": phase, "arm": arm, "toy": toy, "sha256": sha256})

    def complete(self, phase: str, arm: str, expected: set) -> dict:
        got = {t for (p, a, t) in self.state()["toys"] if (p, a) == (phase, arm)}
        return {"complete": got == set(expected), "missing": sorted(set(expected) - got), "n": len(got)}
