"""Declared members, their outcomes, and outputs that are never overwritten.

Not specific to N2. A plan is the ordered list of members fixed before any runs; its digest goes
into every member record and into the result. Each member ends in exactly one state:

* ``ok`` -- its result record exists, names this member and this plan, and passed its checks;
* ``failed`` -- its failure record exists (exit status, reason), or its result failed a check;
* ``missing`` -- neither record exists.

``ledger`` reports every declared member in plan order. Nothing here drops a member, and the only
way to a statistic is ``require_complete``, so a summary over the successful subset cannot be
produced by accident.
"""

import hashlib
import json
import os
import tempfile
from pathlib import Path


class MemberError(RuntimeError):
    """A plan, record or output requirement failed."""


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def plan_digest(members):
    return hashlib.sha256(canonical(members).encode()).hexdigest()


def write_new(path, text):
    """Publish ``text`` at ``path`` atomically, refusing if anything is already there.

    The bytes go to a temporary file in the same directory, which is then hard-linked to ``path``;
    ``link`` fails when the name exists, so two writers cannot both succeed and nothing is
    overwritten, even between a check and the write.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(text)
        try:
            os.link(tmp, path)
        except FileExistsError:
            raise MemberError(f"{path} already exists; refusing to overwrite it") from None
    finally:
        os.unlink(tmp)
    return path


def result_path(outroot, member_id):
    return Path(outroot) / "members" / f"{member_id}.result.json"


def failure_path(outroot, member_id):
    return Path(outroot) / "members" / f"{member_id}.failed.json"


def record_failure(outroot, member_id, digest, status, reason):
    return write_new(failure_path(outroot, member_id),
                     canonical({"member": member_id, "plan_sha256": digest, "status": status,
                                "reason": reason}))


def ledger(members, outroot, digest, check=None):
    """``[(member, state, detail)]`` for every declared member, in plan order.

    ``check(member, record)`` may raise to mark an existing result ``failed``; its message is kept.
    A member with both a result and a failure record is ``failed``: the contradiction is reported,
    not resolved in favour of the result.
    """
    out = []
    for m in members:
        res, fail = result_path(outroot, m["id"]), failure_path(outroot, m["id"])
        if fail.exists():
            detail = json.loads(fail.read_text())
            if res.exists():
                detail = dict(detail, contradiction="a result record exists as well")
            out.append((m, "failed", detail))
            continue
        if not res.exists():
            out.append((m, "missing", None))
            continue
        try:
            rec = json.loads(res.read_text())
            if rec.get("member") != m["id"] or rec.get("plan_sha256") != digest:
                raise MemberError(f"record names member {rec.get('member')!r} of plan "
                                  f"{rec.get('plan_sha256')!r}")
            if rec.get("spec") != m:
                raise MemberError("record's member spec differs from the plan's")
            if check is not None:
                check(m, rec)
        except (MemberError, ValueError, KeyError) as exc:
            out.append((m, "failed", {"reason": str(exc)}))
            continue
        out.append((m, "ok", rec))
    return out


def summary(entries):
    counts = {s: 0 for s in ("ok", "failed", "missing")}
    for _, state, _ in entries:
        counts[state] += 1
    return {"counts": counts,
            "not_ok": [{"member": m["id"], "state": s, "detail": d}
                       for m, s, d in entries if s != "ok"]}


def require_complete(entries):
    """The ok records in plan order, or ``MemberError`` naming every member that is not ok."""
    bad = [(m["id"], s) for m, s, _ in entries if s != "ok"]
    if bad:
        raise MemberError(f"{len(bad)} of {len(entries)} declared members are not ok: {bad}")
    return [rec for _, _, rec in entries]
