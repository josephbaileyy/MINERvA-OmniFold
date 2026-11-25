"""COVFIX's ST3/ST6 reservation ledger (COVFIX-DECLARATION.md rev 11.4 section 3.3: "ST3 and ST6, one reservation
ledger"). One append-only JSONL file in the campaign directory, serialized under flock, keyed by allocation job ID.
All accounting is in integer node-seconds.

  init        creates the ledger once (exclusively), with the bound policy as its first entry ({group: cap}, {phase:
              group}, the ceiling, the expected toy ids per (phase, arm), and the fixed lines such as the synthetic
              test's 2.0 and the u2-draw's 1.0 node-h; every amount a whole number of node-seconds), and fsyncs the file,
              its directory and any directory it created. Every later open must name the same policy; an absent ledger
              is refused, never re-created.
  fixed line  held in its group from init until one intent draws on it (the intent's reservation must fit within it);
              the intent then holds and is charged in its place.
  amendment   a group's cap changed by an entry that carries the director's committed sha (40 hex), e.g. PV's re-price.
  intent      before any submission: a random 128-bit intent ID, the phase and the reservation (nodes x --time, the
              time rounded up to whole minutes) are persisted and fsynced; the job name is covfix_<phase>_<intent>.
              Refused while any earlier intent has no recorded job ID.
  claim       once per intent, under the flock, rechecking the gate (spent + held, this intent included, within its
              group's cap and the ceiling).
  submit      the intent is claimed before sbatch; argv is built from the ledger's stored reservation (--parsable
              --job-name --nodes --time=HH:MM:SS --qos --no-requeue, plus allowlisted extra flags only). The script is
              read once, every #SBATCH directive in it must be on the same allowlist (no --array, --nodes, ...), and its
              bytes go to sbatch on stdin, with every SBATCH_* and SLURM_* variable removed from sbatch's environment.
              The job ID is recorded (idempotently, so a reconcile that recorded it first is not an error), then one
              read-only `scontrol show job` is checked for TimeLimit, JobName, QOS, NumNodes, Requeue=0 and no array
              fields; a pass records "verified", a mismatch scancels the job and records a STOP that says whether the
              scancel succeeded. An sbatch that returns no job ID keeps the reservation held and records a STOP.
              Never squeue.
  reconcile   from sacct allocation rows (JobID, JobName, State, NNodes, ElapsedRaw): an intent with no job ID is
              matched by its full job name, phase included (exactly one job; several or none keep it unresolved). A
              terminal job's charge, NNodes x ElapsedRaw node-seconds, is recorded once, only from non-negative integer
              counters that agree across every row for that job. A zero ElapsedRaw releases the hold (charge 0) only on
              CANCELLED with Start None; any other terminal state with zero ElapsedRaw is charged the full reservation.
              Every charge persists its sacct row as evidence. A job matched by name is recorded as "recovered" (never
              verified, so none of its products can be accepted). Job IDs are canonical decimal strings. Anything
              uncertain keeps the reservation open.
  gate        atomic under the flock: reconciled charges + open reservations + the new reservation must stay within
              the phase's cap group and within the ceiling.
  accept      each toy of a (phase, arm) in the bound policy is accepted exactly once, with its product's sha256 (the
              connect hashes the product; the ledger cannot read cluster files) and the job ID of a verified intent of
              the same phase.
  amendment   refused below the group's spent + held.
  replay      the state is rebuilt from the ledger, refusing any transition the live API would refuse: a second policy,
              an intent or an amendment that breaks the gate, a submission without a claim, a job ID that is not a
              canonical decimal string or is already bound, a second charge, a zero charge without its evidence, an
              acceptance without a verified job or with a malformed sha256, and an unknown kind.

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
EXTRA_OK = re.compile(r"--(account|constraint|output|error|cpus-per-task|ntasks-per-node|mem)=\S+|--exclusive")
HEX64 = re.compile(r"[0-9a-f]{64}")
SCRUB = ("SBATCH_", "SLURM_")


def _canon_str(job) -> bool:
    """A recorded job ID: a str of canonical decimal digits."""
    return type(job) is str and JOBID.fullmatch(job) is not None and job == str(int(job))


def _released(ev) -> bool:
    """The only evidence that releases a hold: one sacct row, CANCELLED, Start None, ElapsedRaw 0."""
    return isinstance(ev, dict) and sacct_state(str(ev.get("State", ""))) == "CANCELLED" \
        and str(ev.get("Start", "")) == "None" and str(ev.get("ElapsedRaw", "")) == "0"


def canon_job(job) -> str:
    """A job ID as canonical decimal digits (no leading zeros); refused if not numeric."""
    if not JOBID.fullmatch(str(job)):
        raise Refusal("a job ID is numeric")
    return str(int(str(job)))


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
    def __init__(self, campaign_dir: Path, caps: dict, groups: dict, ceiling: float, toys: dict, fixed: dict):
        """caps: {group: node-h}; groups: {phase: group}; ceiling: the pinned total; toys: {phase: {arm: [toy ids]}};
        fixed: {name: {"group": group, "node_h": amount}}."""
        self.dir = Path(campaign_dir)
        if not (isinstance(caps, dict) and isinstance(groups, dict) and caps and groups):
            raise Refusal("caps and groups must be non-empty mappings")
        if any(not PHASE.fullmatch(p) for p in groups) or set(groups.values()) - set(caps):
            raise Refusal("a phase name is invalid or maps to a group with no cap")
        ok_toys = isinstance(toys, dict) and all(
            ph in groups and isinstance(arms, dict) and arms and all(
                isinstance(a, str) and a and isinstance(ids, list) and ids and all(isinstance(t, str) and t for t in ids)
                and len(set(ids)) == len(ids) for a, ids in arms.items()) for ph, arms in toys.items())
        ok_fixed = isinstance(fixed, dict) and all(
            isinstance(n, str) and PHASE.fullmatch(n) and isinstance(f, dict) and set(f) == {"group", "node_h"}
            and f["group"] in caps for n, f in fixed.items())
        if not (ok_toys and ok_fixed):
            raise Refusal("the toy sets or the fixed lines are malformed")
        self.caps = {g: _ns(c) for g, c in caps.items()}
        self.groups, self.ceiling = dict(groups), _ns(ceiling)
        self.toys = {ph: {a: list(ids) for a, ids in arms.items()} for ph, arms in toys.items()}
        self.fixed = {n: {"group": f["group"], "ns": _ns(f["node_h"])} for n, f in fixed.items()}
        self.policy = {"caps_ns": self.caps, "groups": self.groups, "ceiling_ns": self.ceiling, "toys": self.toys,
                       "fixed": self.fixed}

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
        created = [d for d in [self.dir, *self.dir.parents] if not d.exists()]
        self.dir.mkdir(parents=True, exist_ok=True)
        for d in reversed(created):                    # make each new directory entry durable in its parent
            pfd = os.open(d.parent, os.O_RDONLY)
            try:
                os.fsync(pfd)
            finally:
                os.close(pfd)
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
        st = {"intents": {}, "toys": {}, "caps": dict(self.caps), "fixed_open": set(self.fixed)}
        intents, toys, caps, jobs = st["intents"], st["toys"], st["caps"], set()
        for e in es[1:]:
            k = e.get("kind")
            it = intents.get(e.get("intent"))
            fx = e.get("fixed")
            if k == "intent" and e.get("intent") not in intents and e.get("phase") in self.groups \
                    and type(e.get("nodes")) is int and type(e.get("time_limit_s")) is int \
                    and e.get("reservation") == reservation_ns(e["nodes"], e["time_limit_s"]) \
                    and (fx is None or (fx in st["fixed_open"]
                                        and self.fixed[fx]["group"] == self.groups[e["phase"]]
                                        and e["reservation"] <= self.fixed[fx]["ns"])) \
                    and self._fits(st, e["phase"], e["reservation"], fx):
                intents[e["intent"]] = {"phase": e["phase"], "nodes": e["nodes"], "time_limit_s": e["time_limit_s"],
                                        "reservation": e["reservation"], "job": None, "charge": None, "stop": None,
                                        "claimed": False, "verified": False, "fixed": fx}
                if fx is not None:
                    st["fixed_open"].discard(fx)
            elif k == "amendment" and e.get("group") in caps and type(e.get("cap_ns")) is int and e["cap_ns"] > 0 \
                    and re.fullmatch(r"[0-9a-f]{40}", str(e.get("director_sha", ""))) \
                    and e["cap_ns"] >= sum(self.totals(st, e["group"]).values()):
                caps[e["group"]] = e["cap_ns"]
            elif k == "claimed" and it is not None and not it["claimed"] and it["job"] is None and it["stop"] is None:
                it["claimed"] = True
            elif k in ("submitted", "recovered") and it is not None and it["claimed"] and it["job"] is None \
                    and _canon_str(e.get("job")) and e["job"] not in jobs:
                it["job"] = e["job"]
                jobs.add(e["job"])
            elif k == "verified" and it is not None and it["job"] is not None and e.get("job") == it["job"] \
                    and not it["verified"] and it["stop"] is None:
                it["verified"] = True
            elif k == "reconciled" and it is not None and it["job"] is not None and it["job"] == e.get("job") \
                    and it["charge"] is None and type(e.get("charge")) is int and e["charge"] >= 0 \
                    and (e["charge"] > 0 or _released(e.get("evidence"))):
                it["charge"] = e["charge"]
            elif k == "stop" and it is not None and isinstance(e.get("reason"), str):
                it["stop"] = e["reason"]
            elif k == "accepted" and (e.get("phase"), e.get("arm"), e.get("toy")) not in toys \
                    and e.get("toy") in self.toys.get(e.get("phase"), {}).get(e.get("arm"), []) \
                    and HEX64.fullmatch(str(e.get("sha256", ""))) and _canon_str(e.get("job")) \
                    and any(x["job"] == e["job"] and x["phase"] == e["phase"] and x["verified"]
                            for x in intents.values()):
                toys[(e["phase"], e["arm"], e["toy"])] = {"sha256": e["sha256"], "job": e["job"]}
            else:
                raise Refusal(f"an invalid ledger transition ({k!r})")
        return st

    def _fits(self, st: dict, phase: str, res: int, fixed: str | None) -> bool:
        """The gate: spent + held + res (less the fixed line it replaces) within the group's cap and the ceiling."""
        group = self.groups[phase]
        credit = self.fixed[fixed]["ns"] if fixed is not None else 0
        tot, gt = self.totals(st), self.totals(st, group)
        return tot["spent_ns"] + tot["held_ns"] + res - credit <= self.ceiling \
            and gt["spent_ns"] + gt["held_ns"] + res - credit <= st["caps"][group]

    def totals(self, st: dict, group: str | None = None) -> dict:
        spent = held = 0
        for n in st["fixed_open"]:
            if group is None or self.fixed[n]["group"] == group:
                held += self.fixed[n]["ns"]
        for it in st["intents"].values():
            if group is not None and self.groups[it["phase"]] != group:
                continue
            if it["charge"] is None:
                held += it["reservation"]
            else:
                spent += it["charge"]
        return {"spent_ns": spent, "held_ns": held}

    # --------------------------------------------------------------------------------------------- operations
    def new_intent(self, phase: str, nodes: int, time_limit_s: int, fixed: str | None = None) -> dict:
        """Gate and persist an intent; with `fixed`, the intent draws on that fixed line instead of new headroom.
        Returns {"intent", "job_name", "phase", "nodes", "time_limit_s", "gate"}."""
        if not PHASE.fullmatch(phase) or phase not in self.groups:
            raise Refusal(f"unknown phase {phase!r}")
        res = reservation_ns(nodes, time_limit_s)
        with self.locked():
            st = self.state()
            unrecorded = [i for i, it in st["intents"].items() if it["job"] is None]
            if unrecorded:
                raise Refusal(f"{len(unrecorded)} intent(s) have no job ID: reconcile from sacct first")
            group = self.groups[phase]
            credit = 0
            if fixed is not None:
                if fixed not in st["fixed_open"] or self.fixed[fixed]["group"] != group or res > self.fixed[fixed]["ns"]:
                    raise Refusal("the fixed line is unknown, used, of another group, or smaller than the reservation")
                credit = self.fixed[fixed]["ns"]           # the line's hold is replaced by the intent's
            tot, gt = self.totals(st), self.totals(st, group)
            gate = {"total_ns": tot["spent_ns"] + tot["held_ns"] + res - credit, "ceiling_ns": self.ceiling,
                    "group": group, "group_total_ns": gt["spent_ns"] + gt["held_ns"] + res - credit,
                    "cap_ns": st["caps"][group]}
            if not self._fits(st, phase, res, fixed):
                raise Refusal(f"the gate refuses: {gate}")
            intent = secrets.token_hex(16)
            self._append({"kind": "intent", "intent": intent, "phase": phase, "nodes": nodes,
                          "time_limit_s": time_limit_s, "reservation": res, "fixed": fixed})
        return {"intent": intent, "job_name": f"covfix_{phase}_{intent}", "phase": phase, "nodes": nodes,
                "time_limit_s": time_limit_s, "gate": gate}

    def record_submission(self, intent: str, job: str) -> None:
        """Record a claimed intent's job ID. Idempotent for the same job (a reconcile may have recorded it first)."""
        job = canon_job(job)
        with self.locked():
            st = self.state()
            it = st["intents"].get(intent)
            if it is None:
                raise Refusal("unknown intent")
            if it["job"] == job:
                return
            if it["job"] is not None:
                raise Refusal("the intent already has another job ID")
            if not it["claimed"]:
                raise Refusal("the intent was never claimed")
            if any(x["job"] == job for x in st["intents"].values()):
                raise Refusal("the job ID is already recorded for another intent")
            self._append({"kind": "submitted", "intent": intent, "job": job})

    def claim(self, intent: str) -> dict:
        """Claim an intent once, rechecking the gate with its reservation held. Returns the intent's record."""
        with self.locked():
            st = self.state()
            it = st["intents"].get(intent)
            if it is None:
                raise Refusal("unknown intent")
            if it["claimed"] or it["job"] is not None or it["stop"] is not None:
                raise Refusal("the intent is already claimed, submitted or stopped")
            if it["time_limit_s"] % 60:
                raise Refusal("the time limit must be whole minutes, so scontrol's TimeLimit can match it exactly")
            group = self.groups[it["phase"]]
            tot, gt = self.totals(st), self.totals(st, group)
            if sum(tot.values()) > self.ceiling or sum(gt.values()) > st["caps"][group]:
                raise Refusal("the gate refuses at the claim: spent + held exceeds the cap or the ceiling")
            self._append({"kind": "claimed", "intent": intent})
        return it

    @staticmethod
    def _script(script: str) -> bytes:
        """The job script's bytes, read once; every #SBATCH directive must be on the allowlist."""
        try:
            with open(script, "rb") as fh:
                data = fh.read()
        except OSError as e:
            raise Refusal("the job script cannot be read") from e
        for line in data.decode("utf-8", "replace").splitlines():
            words = line.strip().split()
            if words and words[0] == "#SBATCH":
                bad = [w for w in words[1:] if not EXTRA_OK.fullmatch(w)]
                if bad or len(words) == 1:
                    raise Refusal(f"a #SBATCH directive is not allowed: {bad or line.strip()}")
        return data

    def submit(self, intent: str, script: str, sbatch: str, scontrol: str, scancel: str, qos: str = "regular",
               qos_pattern: str = r"regular(_[0-9]+)?", extra: tuple = ()) -> str:
        """Claim the intent, submit its job from the ledger's stored reservation, and verify it with one read-only
        scontrol. Returns the job ID."""
        bad = [x for x in extra if not EXTRA_OK.fullmatch(x)]
        if bad:
            raise Refusal(f"an extra sbatch flag is not allowed: {bad}")
        body = self._script(script)
        it = self.claim(intent)
        env = {k: v for k, v in os.environ.items() if not k.startswith(SCRUB)}
        job_name = f"covfix_{it['phase']}_{intent}"
        argv = [sbatch, "--parsable", f"--job-name={job_name}", f"--nodes={it['nodes']}",
                f"--time={hhmmss(it['time_limit_s'])}", f"--qos={qos}", "--no-requeue", *extra]
        try:
            r = subprocess.run(argv, capture_output=True, input=body, env=env, timeout=300)
            m = re.fullmatch(r"([0-9]+)(;\S+)?", r.stdout.decode("utf-8", "replace").strip())
            ok = r.returncode == 0 and m
        except (OSError, subprocess.SubprocessError):
            ok = False
        if not ok:
            with self.locked():
                self._append({"kind": "stop", "intent": intent, "reason": "sbatch returned no job ID; held"})
            raise Refusal("STOP: sbatch did not return a job ID; the reservation stays held until reconciled")
        job = canon_job(m.group(1))
        self.record_submission(intent, job)
        try:
            s = subprocess.run([scontrol, "show", "job", job], capture_output=True, text=True, env=env,
                               stdin=subprocess.DEVNULL, timeout=120)
            fields = dict(re.findall(r"(\w+)=(\S*)", s.stdout)) if s.returncode == 0 else {}
        except (OSError, subprocess.SubprocessError):
            fields = {}
        problems = []
        if slurm_seconds(fields.get("TimeLimit", "")) != it["time_limit_s"]:
            problems.append("TimeLimit")
        if fields.get("JobName") != job_name:
            problems.append("JobName")
        if not re.fullmatch(qos_pattern, fields.get("QOS", "")):
            problems.append("QOS")
        if fields.get("NumNodes") != str(it["nodes"]):
            problems.append("NumNodes")
        if fields.get("Requeue") != "0":
            problems.append("Requeue")
        if "ArrayJobId" in fields or "ArrayTaskId" in fields:
            problems.append("Array")
        if problems:
            try:
                cancelled = subprocess.run([scancel, job], capture_output=True, env=env, stdin=subprocess.DEVNULL,
                                           timeout=120).returncode == 0
            except (OSError, subprocess.SubprocessError):
                cancelled = False
            how = "scancelled" if cancelled else "scancel failed; the job may run"
            with self.locked():
                self._append({"kind": "stop", "intent": intent, "job": job,
                              "reason": f"scontrol mismatch: {problems}; {how}"})
            raise Refusal(f"STOP: job {job}'s {problems} do not match; {how}")
        with self.locked():
            self._append({"kind": "verified", "intent": intent, "job": job})
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
                jid = canon_job(r["JobID"])
                by_job.setdefault(jid, []).append(r)
                m = JOB_NAME.fullmatch(r.get("JobName", ""))
                if m:
                    by_name.setdefault((m.group(1), m.group(2)), set()).add(jid)
            for iid, it in st["intents"].items():
                if it["job"] is None:
                    cands = by_name.get((it["phase"], iid), set())
                    used = {x["job"] for x in st["intents"].values()}
                    if it["claimed"] and len(cands) == 1 and next(iter(cands)) not in used:
                        job = next(iter(cands))
                        self._append({"kind": "recovered", "intent": iid, "job": job, "via": "sacct job name"})
                        it["job"] = job
                        out["matched"] += 1
                    else:
                        out["unresolved"].append(iid)
                        continue
                if it["charge"] is None:
                    rs = by_job.get(it["job"], [])
                    sigs = {(sacct_state(r.get("State", "")), str(r.get("NNodes", "")), str(r.get("ElapsedRaw", "")),
                             r.get("JobName", ""), str(r.get("Start", ""))) for r in rs}
                    if len(sigs) != 1:
                        out["open"] += 1
                        continue
                    state, nn, el, name, start = next(iter(sigs))
                    if state in TERMINAL and UINT.fullmatch(nn) and UINT.fullmatch(el) and int(nn) >= 1 \
                            and name == f"covfix_{it['phase']}_{iid}":
                        charge = int(nn) * int(el)
                        if charge == 0 and not _released(rs[0]):
                            charge = it["reservation"]              # zero elapsed, not shown never-started: the full hold
                        self._append({"kind": "reconciled", "intent": iid, "job": it["job"], "state": state,
                                      "charge": charge, "evidence": dict(rs[0])})
                        out["charged"] += 1
                    else:
                        out["open"] += 1
        return out

    def amend_cap(self, group: str, node_h: float, director_sha: str) -> None:
        """A group's cap changed under the director's committed sha (e.g. PV's re-price)."""
        if group not in self.caps or not re.fullmatch(r"[0-9a-f]{40}", str(director_sha)):
            raise Refusal("an amendment names a known group and the director's 40-hex commit sha")
        cap = _ns(node_h)
        with self.locked():
            st = self.state()
            if cap < sum(self.totals(st, group).values()):
                raise Refusal("an amendment below the group's spent + held is refused")
            self._append({"kind": "amendment", "group": group, "cap_ns": cap, "director_sha": director_sha})

    def accept(self, phase: str, arm: str, toy: str, sha256: str, job: str) -> None:
        if toy not in self.toys.get(phase, {}).get(arm, []):
            raise Refusal(f"toy {toy!r} is not in the policy's {phase}/{arm}")
        if not re.fullmatch(r"[0-9a-f]{64}", sha256):
            raise Refusal("a product sha256 is 64 lowercase hex")
        with self.locked():
            st = self.state()
            job = canon_job(job)
            if not any(it["job"] == job and it["phase"] == phase and it["verified"] for it in st["intents"].values()):
                raise Refusal("the product's job is not a verified submission of this phase")
            if (phase, arm, toy) in st["toys"]:
                raise Refusal(f"toy {toy!r} of {phase}/{arm} is already accepted")
            self._append({"kind": "accepted", "phase": phase, "arm": arm, "toy": toy, "sha256": sha256,
                          "job": job})

    def complete(self, phase: str, arm: str) -> dict:
        expected = set(self.toys.get(phase, {}).get(arm, []))
        if not expected:
            raise Refusal(f"no toy set is bound for {phase}/{arm}")
        with self.locked():
            got = {t for (p, a, t) in self.state()["toys"] if (p, a) == (phase, arm)}
        return {"complete": got == expected, "missing": sorted(expected - got), "n": len(got)}
