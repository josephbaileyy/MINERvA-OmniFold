"""COVFIX's ST3/ST6 reservation ledger (COVFIX-DECLARATION.md rev 11.4 section 3.3: "ST3 and ST6, one reservation
ledger"). One append-only JSONL file in the campaign directory, serialized under flock, keyed by allocation job ID.
All accounting is in integer node-seconds.

  init        creates the ledger once (exclusively), with the bound policy as its first entry ({group: cap}, {phase:
              group}, the ceiling; every cap a whole number of node-seconds), and fsyncs the file and its directory.
              Every later open must name the same policy; an absent ledger is refused, never re-created.
  intent      before any submission: a random 128-bit intent ID, the phase and the reservation (nodes x --time, the
              time rounded up to whole minutes) are persisted and fsynced; the job name is covfix_<phase>_<intent>.
              Refused while any earlier intent has no recorded job ID.
  submit      sbatch --parsable --job-name --nodes --time=HH:MM:SS --no-requeue, the job ID recorded, then one read-only
              `scontrol show job` checked for the job's TimeLimit, JobName and QOS; a mismatch scancels the job and
              records a STOP. Never squeue.
  reconcile   from sacct allocation rows (JobID, JobName, State, NNodes, ElapsedRaw): an intent with no job ID is
              matched by its full job name, phase included (exactly one job; several or none keep it unresolved). A
              terminal job's charge, NNodes x ElapsedRaw node-seconds, is recorded once, only from non-negative integer
              counters that agree across every row for that job. Anything uncertain keeps the reservation open.
  gate        atomic under the flock: reconciled charges + open reservations + the new reservation must stay within
              the phase's cap group and within the ceiling.
  accept      each expected toy of a (phase, arm) is accepted exactly once, with its verified product's sha256 and the
              job ID of a submitted intent of the same phase.
  replay      the state is rebuilt from the ledger, refusing any invalid transition (a second policy, a duplicate intent,
              a second submission or charge, a duplicate acceptance, an unknown kind).

MEASURES: nothing. CANNOT AUTHORIZE: a submission; it only refuses one that would not fit or does not match.
"""
from __future__ import annotations

import contextlib
import fcntl
import json
import math
import os
import re
import secrets
import subprocess
from pathlib import Path

LEDGER, LOCK = "LEDGER.jsonl", "LEDGER.lock"
TERMINAL = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "OUT_OF_MEMORY", "NODE_FAIL", "PREEMPTED", "BOOT_FAIL",
            "DEADLINE"}
PHASE = re.compile(r"[a-z0-9]{1,16}")
JOB_NAME = re.compile(r"covfix_([a-z0-9]{1,16})_([0-9a-f]{32})")
JOBID = re.compile(r"[0-9]+")
UINT = re.compile(r"[0-9]+")


class Refusal(Exception):
    """The ledger refuses: nothing was appended (except a STOP record, where stated)."""


def reservation_ns(nodes: int, time_limit_s: int) -> int:
    if not (type(nodes) is int and nodes >= 1 and type(time_limit_s) is int and time_limit_s >= 1):
        raise Refusal("nodes and the time limit must be positive integers")
    return nodes * math.ceil(time_limit_s / 60) * 60


def hhmmss(seconds: int) -> str:
    """Explicit HH:MM:SS (hours may exceed 24); never H:MM, which Slurm reads as minutes:seconds."""
    return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


def slurm_seconds(text: str) -> int | None:
    """scontrol's TimeLimit ([D-]HH:MM:SS or MM:SS) in seconds, or None if not parseable."""
    m = re.fullmatch(r"(?:([0-9]+)-)?(?:([0-9]+):)?([0-9]+):([0-9]+)", text)
    if not m:
        return None
    d, h, mi, s = (int(g) if g else 0 for g in m.groups())
    return ((d * 24 + h) * 60 + mi) * 60 + s


def sacct_state(raw: str) -> str:
    """sacct prints e.g. 'CANCELLED by 12345'; the first word is the state."""
    return raw.split()[0] if raw.split() else ""


def _ns(cap) -> int:
    if not (isinstance(cap, (int, float)) and math.isfinite(cap) and cap > 0) or (cap * 3600) != int(cap * 3600):
        raise Refusal("a cap or ceiling must be a finite positive whole number of node-seconds")
    return int(cap * 3600)


class Ledger:
    def __init__(self, campaign_dir: Path, caps: dict, groups: dict, ceiling: float):
        """caps: {group: node-h}; groups: {phase: group}; ceiling: the pinned total (541.50 at binding 1)."""
        self.dir = Path(campaign_dir)
        if not (isinstance(caps, dict) and isinstance(groups, dict) and caps and groups):
            raise Refusal("caps and groups must be non-empty mappings")
        if any(not PHASE.fullmatch(p) for p in groups) or set(groups.values()) - set(caps):
            raise Refusal("a phase name is invalid or maps to a group with no cap")
        self.caps = {g: _ns(c) for g, c in caps.items()}
        self.groups, self.ceiling = dict(groups), _ns(ceiling)
        self.policy = {"caps_ns": self.caps, "groups": self.groups, "ceiling_ns": self.ceiling}

    # ------------------------------------------------------------------------------------------------ storage
    @contextlib.contextmanager
    def locked(self):
        if not self.dir.is_dir():
            raise Refusal("the campaign directory does not exist")
        with open(self.dir / LOCK, "a") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)

    def init(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        with self.locked():
            try:
                fd = os.open(self.dir / LEDGER, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError as e:
                raise Refusal("the ledger already exists") from e
            try:
                os.write(fd, (json.dumps({"kind": "policy", **self.policy}, sort_keys=True) + "\n").encode())
                os.fsync(fd)
            finally:
                os.close(fd)
            dfd = os.open(self.dir, os.O_RDONLY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)

    def _entries(self) -> list:
        p = self.dir / LEDGER
        if not p.exists():
            raise Refusal("the ledger is not initialized")
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
        es = self._entries()
        if not es or es[0].get("kind") != "policy" or {k: es[0].get(k) for k in self.policy} != \
                json.loads(json.dumps(self.policy)):
            raise Refusal("the ledger's policy is absent or is not this policy")
        intents, toys, jobs = {}, {}, set()
        for e in es[1:]:
            k = e.get("kind")
            if k == "intent" and e.get("intent") not in intents and e.get("phase") in self.groups:
                intents[e["intent"]] = {"phase": e["phase"], "reservation": e["reservation"], "job": None,
                                        "charge": None, "stop": None}
            elif k == "submitted" and e.get("intent") in intents and intents[e["intent"]]["job"] is None \
                    and e.get("job") not in jobs:
                intents[e["intent"]]["job"] = e["job"]
                jobs.add(e["job"])
            elif k == "reconciled" and e.get("intent") in intents and intents[e["intent"]]["job"] == e.get("job") \
                    and intents[e["intent"]]["charge"] is None:
                intents[e["intent"]]["charge"] = e["charge"]
            elif k == "stop" and e.get("intent") in intents:
                intents[e["intent"]]["stop"] = e["reason"]
            elif k == "accepted" and (e.get("phase"), e.get("arm"), e.get("toy")) not in toys:
                toys[(e["phase"], e["arm"], e["toy"])] = {"sha256": e["sha256"], "job": e["job"]}
            else:
                raise Refusal(f"an invalid ledger transition ({k!r})")
        return {"intents": intents, "toys": toys}

    def totals(self, st: dict, group: str | None = None) -> dict:
        spent = held = 0
        for it in st["intents"].values():
            if group is not None and self.groups[it["phase"]] != group:
                continue
            if it["charge"] is None:
                held += it["reservation"]
            else:
                spent += it["charge"]
        return {"spent_ns": spent, "held_ns": held}

    # --------------------------------------------------------------------------------------------- operations
    def new_intent(self, phase: str, nodes: int, time_limit_s: int) -> dict:
        """Gate and persist an intent. Returns {"intent", "job_name", "phase", "nodes", "time_limit_s", "gate"}."""
        if not PHASE.fullmatch(phase) or phase not in self.groups:
            raise Refusal(f"unknown phase {phase!r}")
        res = reservation_ns(nodes, time_limit_s)
        with self.locked():
            st = self.state()
            unrecorded = [i for i, it in st["intents"].items() if it["job"] is None]
            if unrecorded:
                raise Refusal(f"{len(unrecorded)} intent(s) have no job ID: reconcile from sacct first")
            group = self.groups[phase]
            tot, gt = self.totals(st), self.totals(st, group)
            gate = {"total_ns": tot["spent_ns"] + tot["held_ns"] + res, "ceiling_ns": self.ceiling, "group": group,
                    "group_total_ns": gt["spent_ns"] + gt["held_ns"] + res, "cap_ns": self.caps[group]}
            if gate["total_ns"] > self.ceiling or gate["group_total_ns"] > self.caps[group]:
                raise Refusal(f"the gate refuses: {gate}")
            intent = secrets.token_hex(16)
            self._append({"kind": "intent", "intent": intent, "phase": phase, "nodes": nodes,
                          "time_limit_s": time_limit_s, "reservation": res})
        return {"intent": intent, "job_name": f"covfix_{phase}_{intent}", "phase": phase, "nodes": nodes,
                "time_limit_s": time_limit_s, "gate": gate}

    def record_submission(self, intent: str, job: str) -> None:
        if not JOBID.fullmatch(str(job)):
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

    def submit(self, it: dict, script: str, sbatch: str, scontrol: str, scancel: str, qos: str = "regular",
               qos_pattern: str = r"regular(_[0-9]+)?", extra: tuple = ()) -> str:
        """Submit an intent's job and verify it with one read-only scontrol. Returns the job ID."""
        if it["time_limit_s"] % 60:
            raise Refusal("the time limit must be whole minutes, so scontrol's TimeLimit can match it exactly")
        argv = [sbatch, "--parsable", f"--job-name={it['job_name']}", f"--nodes={it['nodes']}",
                f"--time={hhmmss(it['time_limit_s'])}", f"--qos={qos}", "--no-requeue", *extra, script]
        r = subprocess.run(argv, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=300)
        m = re.fullmatch(r"([0-9]+)(;\S+)?", r.stdout.strip())
        if r.returncode != 0 or not m:
            raise Refusal("sbatch did not return a job ID: the intent stays open until reconciled from sacct")
        job = m.group(1)
        self.record_submission(it["intent"], job)
        s = subprocess.run([scontrol, "show", "job", job], capture_output=True, text=True, stdin=subprocess.DEVNULL,
                           timeout=120)
        fields = dict(re.findall(r"(\w+)=(\S*)", s.stdout)) if s.returncode == 0 else {}
        problems = []
        if slurm_seconds(fields.get("TimeLimit", "")) != it["time_limit_s"]:
            problems.append("TimeLimit")
        if fields.get("JobName") != it["job_name"]:
            problems.append("JobName")
        if not re.fullmatch(qos_pattern, fields.get("QOS", "")):
            problems.append("QOS")
        if problems:
            subprocess.run([scancel, job], capture_output=True, stdin=subprocess.DEVNULL, timeout=120)
            with self.locked():
                self._append({"kind": "stop", "intent": it["intent"], "job": job,
                              "reason": f"scontrol mismatch: {problems}; scancelled"})
            raise Refusal(f"STOP: job {job}'s {problems} do not match; it was scancelled")
        return job

    def reconcile(self, rows: list[dict]) -> dict:
        """rows: sacct allocation rows. Returns counts of what was recorded and what stays open."""
        out = {"matched": 0, "charged": 0, "unresolved": [], "open": 0}
        with self.locked():
            st = self.state()
            by_name: dict = {}
            by_job: dict = {}
            for r in rows:
                if not JOBID.fullmatch(str(r.get("JobID", ""))):
                    continue
                by_job.setdefault(str(r["JobID"]), []).append(r)
                m = JOB_NAME.fullmatch(r.get("JobName", ""))
                if m:
                    by_name.setdefault((m.group(1), m.group(2)), set()).add(str(r["JobID"]))
            for iid, it in st["intents"].items():
                if it["job"] is None:
                    cands = by_name.get((it["phase"], iid), set())
                    used = {x["job"] for x in st["intents"].values()}
                    if len(cands) == 1 and next(iter(cands)) not in used:
                        job = next(iter(cands))
                        self._append({"kind": "submitted", "intent": iid, "job": job, "via": "sacct job name"})
                        it["job"] = job
                        out["matched"] += 1
                    else:
                        out["unresolved"].append(iid)
                        continue
                if it["charge"] is None:
                    rs = by_job.get(it["job"], [])
                    sigs = {(sacct_state(r.get("State", "")), str(r.get("NNodes", "")), str(r.get("ElapsedRaw", "")),
                             r.get("JobName", "")) for r in rs}
                    if len(sigs) != 1:
                        out["open"] += 1
                        continue
                    state, nn, el, name = next(iter(sigs))
                    if state in TERMINAL and UINT.fullmatch(nn) and UINT.fullmatch(el) and int(nn) >= 1 \
                            and name == f"covfix_{it['phase']}_{iid}":
                        charge = int(nn) * int(el)
                        self._append({"kind": "reconciled", "intent": iid, "job": it["job"], "state": state,
                                      "charge": charge})
                        out["charged"] += 1
                    else:
                        out["open"] += 1
        return out

    def accept(self, phase: str, arm: str, toy: str, sha256: str, expected: set, job: str) -> None:
        if toy not in expected:
            raise Refusal(f"toy {toy!r} is not expected in {phase}/{arm}")
        if not re.fullmatch(r"[0-9a-f]{64}", sha256):
            raise Refusal("a product sha256 is 64 lowercase hex")
        with self.locked():
            st = self.state()
            if not any(it["job"] == str(job) and it["phase"] == phase for it in st["intents"].values()):
                raise Refusal("the product's job is not a submitted intent of this phase")
            if (phase, arm, toy) in st["toys"]:
                raise Refusal(f"toy {toy!r} of {phase}/{arm} is already accepted")
            self._append({"kind": "accepted", "phase": phase, "arm": arm, "toy": toy, "sha256": sha256,
                          "job": str(job)})

    def complete(self, phase: str, arm: str, expected: set) -> dict:
        with self.locked():
            got = {t for (p, a, t) in self.state()["toys"] if (p, a) == (phase, arm)}
        return {"complete": got == set(expected), "missing": sorted(set(expected) - got), "n": len(got)}
