#!/usr/bin/env python3
"""Z's prospective unified-throw precursor: ONE output namespace, declared populations, receipts.

Z derives its OWN unified throw (`SPEC` §1.3a). G's throw at
`uq_5d/unified_throw_cov_5d_fluxfix_20260806_full160.root` is a DIFFERENT product and must not be
substituted for it, so the precursor's four arms -- dump, block, run, combine -- are a fresh
production and every path they touch has to be fresh too.

WHAT THIS MODULE IS FOR, and each item names the defect it closes:

  (c) ONE EXPLICIT NAMESPACE, SHARED BY ALL FOUR ARMS, AND FRESHNESS IS A REFUSAL. Today the arms
      DISAGREE about where products live. `sbatch_uthrow_block_5d.sh:317-321` writes
      `block_slabs_5d_sb` when a member offset is declared and `block_slabs_5d` when it is not,
      while `sbatch_uthrow_combine_5d_fast.sh:333` reads `block_slabs_5d_sb` UNCONDITIONALLY --
      and `lib_member_resume.sh:145-149`'s `mr_dir_prefix` returns its argument UNCHANGED when
      undeclared, so nothing re-aligns them. I measured both namespaces populated:
      `block_slabs_5d` holds 8 products, `block_slabs_5d_sb` holds 36, from separate campaigns.
      An UNDECLARED precursor therefore writes 21 fresh block slabs and its combine consumes 36
      foreign ones -- and because the glob MATCHES it does not fail closed. The launcher's own
      comment concedes the wrong literal is *"a PRE-EXISTING defect needing its own change and its
      own authorization"*.
      ⚠ AND FILE-IDENTITY VALIDATION CANNOT CLOSE THIS, measured rather than assumed. A foreign
      namespace holds the SAME BASENAMES, so `unified_throw_cov.check_slab_population` passes on it
      -- I ran that case and it passed. Namespace freshness and file identity are two guards over
      two different populations and NEITHER SUBSUMES THE OTHER: identity catches a stale or extra
      member inside the right directory, freshness catches the right members in the wrong one.

  (c') "NOTHING LANDS IN `mii/`" BECOMES A REFUSAL. `lib_member_resume.sh:84` prepends
      `mii/member_kNNNNNN` to every product path whenever `MNV_EST_SEED_OFFSET` is set
      (`:230`, `_mr_insert` at `:120-135`). So the precursor keeping out of the member axis holds
      today only because nobody exported that variable -- an assumption, not a guard.

  (f) RECEIPT-LAST COMPLETION. These arms have no receipt artifact. Their provenance is IN-PRODUCT
      (`unified_throw_cov.py` `TParameter`s, `_atomic_savez`'s tmp-then-rename) which is good
      provenance and is NOT a receipt: it cannot say the product was completed, nor by which run.
      `write_receipt` refuses to write unless the product already exists and OPENS, so a receipt is
      evidence that the product landed rather than a declaration made in parallel with it.
      ⚠ NO `os._exit` ANYWHERE IN THIS MODULE OR IN EITHER PRODUCER ENTRYPOINT -- checked, and kept
      that way deliberately: `os._exit` skips `finally`, and a receipt written from a `finally` that
      never runs is the bypassed-record hazard this ordering exists to avoid.

DERIVED, NOT RETYPED. The expected file populations come from each launcher's OWN `#SBATCH --array`
line (`parse_sbatch_arm`), never from a range literal in this file. A retyped layout is a second
implementation of the arm and the two can disagree; and a declaration derived from the launcher
cannot be right about a population the launcher will not produce.
"""

from __future__ import annotations

import argparse
import glob as globmod
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# Same rooted-insert idiom, and the same reason (OI-136), as `unified_throw_cov_5d.py:39-42` and
# `z_contract.py:53-56`: a hardcoded cluster root decides the executing tree before any guard
# starts, and `PYTHONPATH` cannot outrank `sys.path[0]`. NO ABSOLUTE FALLBACK -- a fallback is the
# hardcode wearing a flag and would restore the defect on the one tree where it matters.
_REPO = str(Path(__file__).resolve().parents[1])
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)


class PrecursorError(RuntimeError):
    """Fail-closed refusal. Never swallowed; the CLI turns it into a non-zero exit."""


#: The environment variable naming the one shared namespace. MANDATORY, NO DEFAULT.
#: A default is the hardcode wearing a flag (`sbatch_uthrow_run_5d_fast.sh:29-31`), and here it
#: would be worse than usual: the plausible default values are exactly the six populated archive
#: namespaces, so a defaulted precursor would write into a previous campaign's directory.
NAMESPACE_ENV = "MNV_Z_PRECURSOR_NS"

#: The member-axis variable whose mere PRESENCE relocates every product under `mii/`.
MEMBER_OFFSET_ENV = "MNV_EST_SEED_OFFSET"

#: A namespace is one path segment. `..` and `/` are refused rather than normalized, because a
#: normalized traversal still names a directory outside the namespace and would do it silently.
NAMESPACE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")

#: Arm name -> (subdirectory under the namespace, product glob inside it).
#: The COMBINE arm's product is a single file, so its glob is that file's name.
ARM_LAYOUT = {
    "dump": ("bank_uthrow_5d", "*.np[yz]"),
    "block": ("block_slabs_5d", "block5d_*.npz"),
    "run": ("uthrow_slabs_5d", "uthrow5d_slab_*.npz"),
    "combine": (".", "unified_throw_cov_5d.root"),
}

#: The four launchers, by PATH. Pinned by path and not by stem because siblings differ in BOTH
#: population and wall ceiling: `sbatch_uthrow_run_5d.sh` declares `0-19%10` / `12:00:00` while
#: `sbatch_uthrow_run_5d_fast.sh` declares `0-39%40` / `06:00:00`. Reading the wrong one gives a
#: well-formed answer about the wrong arm.
ARM_LAUNCHERS = {
    "dump": "nd-unfolding/sbatch_uthrow_dump_5d.sh",
    "block": "nd-unfolding/sbatch_uthrow_block_5d.sh",
    "run": "nd-unfolding/sbatch_uthrow_run_5d_fast.sh",
    "combine": "nd-unfolding/sbatch_uthrow_combine_5d_fast.sh",
}


def require(condition, message):
    """Fail-closed. Same idiom and the same reason as `z_contract.require`."""
    if not condition:
        raise PrecursorError(message)


# ------------------------------------------------------------------------ (c) the namespace ----
def resolve_namespace(environ=None):
    """The one namespace value, from the environment, with NO default.

    Parameters
    ----------
    environ : mapping, optional
        Defaults to `os.environ`. Injectable so a test does not have to mutate the real
        environment -- asserting over a shared namespace around a unit blames other processes.

    Returns
    -------
    str
        The validated namespace segment.

    Raises
    ------
    PrecursorError
        If unset, empty, or not a single well-formed path segment.
    """
    env = os.environ if environ is None else environ
    value = env.get(NAMESPACE_ENV)
    require(value is not None,
            f"{NAMESPACE_ENV} is unset. It has NO DEFAULT on purpose: every plausible default is "
            f"one of the populated archive namespaces, so a defaulted precursor would write its "
            f"fresh products into a previous campaign's directory and its combine would read that "
            f"campaign's back. Name the namespace explicitly.")
    require(value.strip() == value and value != "",
            f"{NAMESPACE_ENV}={value!r} is empty or padded; a whitespace-padded segment names a "
            f"different directory than it reads as")
    require(NAMESPACE_RE.match(value) is not None,
            f"{NAMESPACE_ENV}={value!r} is not a single path segment matching "
            f"{NAMESPACE_RE.pattern}. A '/' or a '..' is refused rather than normalized: a "
            f"normalized traversal still names a directory outside the namespace, silently.")
    require(value not in {".", ".."}, f"{NAMESPACE_ENV}={value!r} names its own parent")
    return value


def arm_directory(data_root, namespace, arm):
    """The one directory an arm writes into, under the single shared namespace.

    Resolved only when `data_root` is already absolute: resolving a relative root would anchor it
    to the caller's working directory, and the launchers `cd` into the data root before calling
    this, so an answer silently rooted at the CWD would name a plausible wrong directory.
    """
    require(arm in ARM_LAYOUT, f"unknown arm {arm!r}; known arms are {sorted(ARM_LAYOUT)}")
    sub, _glob = ARM_LAYOUT[arm]
    base = Path(data_root) / "nd-unfolding" / "uq_5d" / namespace
    directory = base if sub == "." else base / sub
    return str(directory.resolve() if Path(data_root).is_absolute() else directory)


def namespace_plan(data_root, namespace=None, environ=None):
    """Every arm's directory and product glob, from the ONE namespace value.

    Returns
    -------
    dict
        ``{"namespace": str, "arms": {arm: {"dir":…, "glob":…, "product_glob":…}}}``.
    """
    ns = resolve_namespace(environ) if namespace is None else namespace
    arms = {}
    for arm, (_sub, pattern) in ARM_LAYOUT.items():
        directory = arm_directory(data_root, ns, arm)
        arms[arm] = {"dir": directory, "glob": pattern,
                     "product_glob": os.path.join(directory, pattern)}
    return {"namespace": ns, "data_root": str(data_root), "arms": arms}


def check_namespace_fresh(plan, arms=None):
    """Every named arm's directory must be absent or hold NO product. Non-emptiness REFUSES.

    ⚠ EMPTINESS IS JUDGED BY THE ARM'S OWN PRODUCT GLOB, NOT BY `os.listdir`, and this is measured
    rather than stylistic. The live `uq_5d/block_slabs_5d` holds 18 directory entries and 8
    products; the other 10 are `knob_<band>.log`. An `os.listdir` test would call that namespace
    occupied for reasons that have nothing to do with products, and a guard that fires on every
    correct run is not a guard. A directory holding ONE real product IS populated, even though a
    count-based check calling it "nearly empty" would wave it through.

    ⚠ AND AN INCOMPLETE WRITE IS EXCLUDED, which a test caught rather than a reading did.
    Post-repair (Joseph, 2026-09-11) `_atomic_savez` names its temp `.mnv-incomplete.<product>.
    <token>.partial`, which is glob-INVISIBLE, so it cannot reach `hits` at all. The filter below
    is still live because a PRE-REPAIR temp is `<product>.<token>.tmp.npz`, which IS glob-visible
    and would read as a product, refusing a genuinely fresh namespace. NOT because such a file
    exists now: `find` over `uq_5d/` and `bank_uthrow_5d/` on 2026-09-11 returns ZERO of either
    era, and the over-claim is corrected at `unified_throw_cov.LEGACY_IN_PROGRESS_SUFFIX`. The
    ground is that an unrepaired checkout -- the pscratch tree runs a divergent local main -- can
    still create one. The predicate is IMPORTED from the producer, not retyped: a second spelling
    could stop matching and nothing would say so.

    NO ARM DEFAULTS TO UNCHECKED: `arms=None` means ALL of them. A per-arm opt-in would let the
    caller shrink the sweep to the arms it already believes are fresh.
    """
    import unified_throw_cov as producer

    names = sorted(plan["arms"]) if arms is None else sorted(set(arms))
    require(names, "check_namespace_fresh: no arms named; an empty sweep checks nothing")
    occupied = {}
    for arm in names:
        require(arm in plan["arms"], f"unknown arm {arm!r} in freshness sweep")
        entry = plan["arms"][arm]
        hits = sorted(p for p in globmod.glob(entry["product_glob"])
                      if not producer.is_incomplete_write(p))
        if hits:
            occupied[arm] = {"dir": entry["dir"], "n": len(hits),
                             "examples": [os.path.basename(h) for h in hits[:6]]}
    if occupied:
        detail = "; ".join(f"{a}: {v['n']} product(s) in {v['dir']} e.g. {v['examples']}"
                           for a, v in sorted(occupied.items()))
        raise PrecursorError(
            f"namespace {plan['namespace']!r} is NOT FRESH -- {detail}. Z derives its own unified "
            f"throw, so a namespace already holding products means either a previous campaign's "
            f"files or a partial run of this one, and the combine cannot tell those from its own: "
            f"its globs MATCH them. Name a fresh namespace. Refusing rather than assuming, because "
            f"non-emptiness here is exactly the state that makes the consumer silently wrong.")
    return {"namespace": plan["namespace"], "arms_checked": names, "fresh": True}


def check_no_member_axis(environ=None):
    """`mii/` stays empty because this REFUSES, not because nobody exported the variable.

    `lib_member_resume.sh:230`'s `mr_declared` is `[[ -n "${MNV_EST_SEED_OFFSET:-}" ]]`, and
    `:84`/`:120-135` then prepend `mii/member_kNNNNNN` to every product path. So the precursor's
    products would silently relocate under the member axis, into a tree the M(ii) grid owns. An
    offset of `0` is still a DECLARATION there -- `-n` is a NON-EMPTINESS test, not a truth test --
    so `0` is refused here too, and that asymmetry is why this cannot be a value check.

    ⚠ THIS GUARD AND THE SHELL PREDICATE DISAGREE ON ONE INPUT, DELIBERATELY, AND THE LEAN IS
    STATED HERE SO NOBODY LATER "ALIGNS" THEM WITHOUT KNOWING WHICH WAY IT LEANS. Raised by the
    independent review of 2026-09-11, which executed all four cases.

        MNV_EST_SEED_OFFSET   this guard   shell `mr_declared`
        unset                 passes       undeclared          -- agree
        "0"                   REFUSES      declared            -- agree
        "7"                   REFUSES      declared            -- agree
        ""  (set, empty)      REFUSES      undeclared          -- DISAGREE

    This keys on KEY PRESENCE (`env.get(...) is not None`); the shell keys on NON-EMPTINESS. On the
    exported-but-empty case this is therefore STRICTLY STRICTER, and that is the SAFE DIRECTION: it
    refuses a run the shell would have let through, and the cost is a false refusal rather than a
    silent relocation into `mii/`. `test_z_precursor` pins both sides -- the four cases here and
    the shell's own `("", False)` measured by executing `lib_member_resume.sh` itself -- so the
    disagreement is on record as intended rather than as drift.
    DO NOT "FIX" THIS BY SWITCHING TO NON-EMPTINESS. An exported-but-empty `MNV_EST_SEED_OFFSET` is
    a caller who meant to set it and got it wrong; treating that as "no member axis" is exactly the
    silently-empty-defaulted-variable failure the launchers' `${VAR:?}` forms exist to prevent.
    """
    env = os.environ if environ is None else environ
    value = env.get(MEMBER_OFFSET_ENV)
    if value is None:
        return {"member_axis": "absent", "ok": True}
    raise PrecursorError(
        f"{MEMBER_OFFSET_ENV}={value!r} is SET, so every precursor product would be relocated "
        f"under mii/member_kNNNNNN by lib_member_resume.sh:_mr_insert. Note that '0' is not an "
        f"exemption: that library's mr_declared is a PRESENCE test (-n), so 0 declares the member "
        f"axis just as 1200 does. The precursor is not a member of the M(ii) grid. Unset it.")


# ---------------------------------- THE CONTRACT, ENFORCED INSIDE THE GUARDED PROCESS ----------
def enforce_namespace_contract(arm, data_root, declared_dir, code_root=None, product=None,
                               bank=None, estimator_seed=None, draw_seed=None):
    """Resolve, refuse and report the namespace contract FROM INSIDE THE PRODUCER.

    ⚠⚠ WHY THIS IS A LIBRARY CALL AND NOT A CLI STEP IN THE LAUNCHER, AND IT IS RULING 21.
    My first implementation had each launcher run `python3 z_precursor.py require-fresh` and three
    siblings before the science invocation. `mnv_preflight_census.py` classifies every non-comment
    `python3` line as GUARDED, DECLARED-PREFLIGHT, INTERPRETER-PROBE or UNCLASSIFIED, and
    UNCLASSIFIED must be zero -- it measured 15 of mine and refused. The two ways out were both
    closed:

      * DECLARE it a preflight tool. `mnv_preflight_exclusions.json`'s criterion (5) requires the
        tool's repository imports to be a SUBSET OF {mnv_guarded_run}, and this module imports
        `unified_throw_cov` on purpose, so the guard HAS something to contain. Criteria (2) and (3)
        also require it in EVERY declared launcher at a FIXED per-launcher count, and it belongs to
        four arms at four different counts.
      * ROUTE it through the guard. That moves `guarded` off 14, which that file names as
        "RULING 21's PIN and the only count here that still requires a ruling to move".

    So the calls are GONE and the contract moved inside the process that is ALREADY guarded and
    already `--pair` bound. Strictly better, not merely compliant: the refusal now happens in the
    same interpreter that will do the writing, so nothing can change between the check and the use.

    `declared_dir` IS THE LAUNCHER'S OWN PATH EXPRESSION, AND IT IS VERIFIED RATHER THAN TRUSTED.
    The launcher still builds `uq_5d/${MNV_Z_PRECURSOR_NS}/<subdir>` in shell, because computing it
    here would need a `python3` call to get it back out. Two spellings of one layout is a
    divergence risk, so the shell spelling is CHECKED against this module's `ARM_LAYOUT` and a
    disagreement REFUSES. That is the same shape the two-roots design already uses: shell computes,
    Python verifies, and the composition is pinned in code rather than in prose.

    ⚠⚠ THE FRESHNESS CLAUSE MOVED, AND THIS IS WHERE THE ARRAY DEFECT WAS. Until 2026-09-13 this
    function ended in `check_namespace_fresh(plan, [arm])`, which is correct for ONE invocation and
    refuses every task of an ARRAY after the first one publishes -- see section (h) for the
    measured shape and for why a single-task probe could not find it. Freshness now lives at
    `initialize_campaign`, atomically, and the per-task predicate is `verify_task_ownership`.
    The `dump` arm is the one exception and it keeps the old predicate; the branch below says why.

    Returns
    -------
    dict or None
        ``None`` when `MNV_Z_PRECURSOR_NS` is unset -- the pre-existing behaviour, preserved
        exactly, because the archive reproduction paths must not change. Otherwise the plan, the
        member-axis result, and either the ownership result (covered arms) or the freshness result
        (the content-addressed `dump` arm).
    """
    if os.environ.get(NAMESPACE_ENV) is None:
        return None
    check_no_member_axis()
    plan = namespace_plan(data_root, environ=os.environ)
    require(arm in plan["arms"], f"unknown arm {arm!r}; known arms are {sorted(ARM_LAYOUT)}")
    expected = plan["arms"][arm]["dir"]
    got = str(Path(declared_dir).resolve()) if Path(declared_dir).is_absolute() else declared_dir
    require(os.path.normpath(got) == os.path.normpath(expected),
            f"the launcher's own path expression for arm {arm!r} is {declared_dir!r}, which "
            f"resolves to {got!r}, but this module's ARM_LAYOUT gives {expected!r}. The shell "
            f"spelling and the Python layout have diverged. Refusing rather than preferring one: "
            f"whichever is right, the other is writing or reading somewhere nobody declared.")
    if arm in CONTENT_ADDRESSED_ARMS:
        # THE ONE ARM THE CAMPAIGN DOES NOT COVER, AND ITS RESIDUAL IS LIVE. `unified_throw.do_dump`
        # addresses the bank by CONTENT -- bands and flux ids split round-robin over `--ngroups` --
        # so there is no (task id -> basename) map for a task to own, and `declare_arm_task_outputs`
        # refuses to invent one. This arm therefore keeps the per-invocation freshness predicate
        # EXACTLY as it was, which means its 8-task array (`--array=0-7`, no throttle) still has the
        # composition defect section (h) describes: the group that publishes first passes and the
        # rest refuse. Not repaired here because the authorized campaign consumes the digest-bound,
        # unmoved bank as an INPUT rather than re-dumping it, so no authorized task takes this path
        # -- and widening the repair to an arm with no ownable layout would need a second, weaker
        # ownership model, which is a separate subject with its own authorization.
        fresh = check_namespace_fresh(plan, [arm])
        print(f"[z-precursor] namespace {plan['namespace']!r} arm {arm}: FRESH, no member axis, "
              f"dir {expected} (content-addressed: NOT campaign-owned, and its array composition "
              f"defect is UNREPAIRED)", flush=True)
        return {"plan": plan, "arm": arm, "dir": expected, "fresh": fresh,
                "campaign": None, "expected_files": None}
    ownership = verify_task_ownership(arm=arm, plan=plan, product=product, bank=bank,
                                      estimator_seed=estimator_seed, draw_seed=draw_seed)
    files = None
    if arm in ("run", "block"):
        root = Path(code_root) if code_root else Path(_REPO)
        files = declare_arm_files(arm, root / ARM_LAUNCHERS[arm])
    print(f"[z-precursor] campaign {ownership['campaign']['campaign_digest'][:12]} namespace "
          f"{plan['namespace']!r} arm {arm} task {ownership['task_id']}: MEMBER, owns "
          f"{ownership['output']}, {ownership['n_sibling_products']} bound sibling product(s), "
          f"no member axis, dir {expected}", flush=True)
    return {"plan": plan, "arm": arm, "dir": expected, "expected_files": files, **ownership}


# ------------------------------------------------- (d) declarations DERIVED from the launcher ----
_ARRAY_RE = re.compile(r"^#SBATCH\s+.*?--array=(\S+)", re.MULTILINE)
_TIME_RE = re.compile(r"^#SBATCH\s+.*?--time=(\S+)", re.MULTILINE)
_NAME_RE = re.compile(r"^#SBATCH\s+.*?--job-name=(\S+)", re.MULTILINE)


def _parse_array_spec(spec):
    """Concrete array task ids from an `--array` value, THROTTLE STRIPPED.

    `%N` is a concurrency throttle, not a population: `0-39%40` is forty tasks. Stripping it is
    the whole point -- and it is also why a declared population must never be read back from
    `sacct -X`, whose bracket Slurm REWRITES (a declared `1-100` has been observed reported as
    `3-100`, truncated at the low end by throttling).
    """
    body = spec.split("%", 1)[0]
    ids = []
    for piece in body.split(","):
        piece = piece.strip()
        if not piece:
            continue
        if "-" in piece:
            lo_text, _, hi_text = piece.partition("-")
            require(lo_text.isdigit() and hi_text.isdigit(),
                    f"array range {piece!r} is not LO-HI over digits")
            lo, hi = int(lo_text), int(hi_text)
            require(lo <= hi, f"array range {piece!r} runs backwards")
            ids.extend(range(lo, hi + 1))
        else:
            require(piece.isdigit(), f"array id {piece!r} is not a number")
            ids.append(int(piece))
    require(ids, f"array spec {spec!r} declares no tasks")
    require(len(set(ids)) == len(ids), f"array spec {spec!r} repeats a task id")
    return sorted(ids)


def _parse_time_limit(text):
    """`--time` to seconds. Accepts the Slurm forms the four launchers actually use plus D-HH:MM:SS."""
    days, _, rest = text.partition("-")
    if not rest:
        days, rest = "0", days
    require(days.isdigit(), f"--time={text!r}: day field is not a number")
    parts = rest.split(":")
    require(1 <= len(parts) <= 3 and all(p.isdigit() for p in parts),
            f"--time={text!r} is not [D-]HH:MM:SS / MM:SS / MM")
    if len(parts) == 3:
        h, m, s = (int(p) for p in parts)
    elif len(parts) == 2:
        h, m, s = 0, int(parts[0]), int(parts[1])
    else:
        h, m, s = 0, int(parts[0]), 0
    total = int(days) * 86400 + h * 3600 + m * 60 + s
    require(total > 0, f"--time={text!r} resolves to zero seconds")
    return total


def parse_sbatch_arm(path):
    """One arm's DECLARED population and wall ceiling, read from its own `#SBATCH` lines.

    ⚠ PINNED BY PATH BY THE CALLER. This reads whatever file it is given; the sibling launchers
    differ in both population and time ceiling, so a stem-based lookup would answer correctly
    about the wrong arm. `ARM_LAUNCHERS` holds the paths.

    A launcher with NO `--array` is a single task -- the combine arm -- and that is reported as
    ``task_ids == [None]``-free: `n_tasks == 1` with ``array_spec is None``, so a consumer can tell
    "one task" from "an array of one".

    Returns
    -------
    dict
        ``job_name``, ``array_spec``, ``task_ids``, ``n_tasks``, ``throttle``,
        ``time_limit_seconds``, ``time_limit_hours``, ``launcher``.
    """
    text = Path(path).read_text()
    name_match = _NAME_RE.search(text)
    require(name_match is not None, f"{path}: no #SBATCH --job-name")
    time_match = _TIME_RE.search(text)
    require(time_match is not None,
            f"{path}: no #SBATCH --time. Without a wall ceiling an admitted task has UNBOUNDED "
            f"remaining exposure and no admission decision about it is possible.")
    array_match = _ARRAY_RE.search(text)
    if array_match is None:
        task_ids, spec, throttle = [0], None, None
    else:
        spec = array_match.group(1)
        task_ids = _parse_array_spec(spec)
        throttle = int(spec.split("%", 1)[1]) if "%" in spec else None
    seconds = _parse_time_limit(time_match.group(1))
    return {"launcher": str(path), "job_name": name_match.group(1), "array_spec": spec,
            "task_ids": task_ids, "n_tasks": len(task_ids), "throttle": throttle,
            "time_limit_seconds": seconds, "time_limit_hours": seconds / 3600.0}


def declare_arm_files(arm, launcher_path):
    """The exact product BASENAMES an arm will produce, derived from its own array declaration.

    This is the operand for `unified_throw_cov.check_slab_population`, and deriving it here is
    what keeps the declaration from being a second implementation of the arm's layout. The block
    arm's task 0 writes the knob slab and tasks 1..N write flux slabs -- that branch is in
    `sbatch_uthrow_block_5d.sh:338-346` and is mirrored, not reinvented.
    """
    outputs = declare_arm_task_outputs(arm, launcher_path)
    return [outputs[task] for task in sorted(outputs)]


def declare_arm_task_outputs(arm, launcher_path):
    """`{task id: product BASENAME}` for a per-task arm, derived from its own `#SBATCH --array`.

    THE MAPPING IS THE PRIMITIVE AND `declare_arm_files` RETURNS ITS VALUES, so the population
    declaration and the task-to-file binding are ONE implementation. They were one list until the
    campaign needed the mapping, and re-zipping a list against `task_ids` in the caller would have
    been an implicit ordering contract between two functions -- the shape that lets a layout change
    move one and leave the other silently plausible.
    """
    info = parse_sbatch_arm(launcher_path)
    if arm == "run":
        names = {t: f"uthrow5d_slab_{t}.npz" for t in info["task_ids"]}
    elif arm == "block":
        names = {t: ("block5d_knobs.npz" if t == 0 else f"block5d_flux_{t}.npz")
                 for t in info["task_ids"]}
    else:
        raise PrecursorError(
            f"declare_arm_files: arm {arm!r} has no per-task file layout. The dump arm's bank is "
            f"addressed by content (band and universe ids, checked by "
            f"`unified_throw_cov._load_bank`) rather than by task, and the combine arm writes one "
            f"named file. Declaring a task-derived basename list for either would be a fiction.")
    require(len(set(names.values())) == len(names),
            f"declare_arm_files({arm!r}): the derived names repeat; the array declaration and the "
            f"launcher's file layout disagree")
    return names


# ------------------------------------------------------------------ (f) the receipt, written LAST ----
RECEIPT_SCHEMA_VERSION = 1

#: Fields a precursor receipt must carry with a usable value. `UNAVAILABLE` is a usable value for
#: none of them -- `unified_throw_cov.code_provenance` stamps that literal rather than omitting a
#: key precisely so this gate can see it and refuse.
REQUIRED_PROVENANCE = ("code_revision", "producer_sha256", "bank_cv_sha256")


def sha256_file(path, _chunk=1 << 20):
    """Streaming SHA-256. The precursor's products run to gigabytes; a read_bytes would not fit."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(_chunk), b""):
            digest.update(block)
    return digest.hexdigest()


def _git_head(repo):
    try:
        out = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                             check=True).stdout.decode().strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNAVAILABLE"
    return out or "UNAVAILABLE"


def _product_opens(path):
    """Can the product actually be READ, not merely stat-ed?

    A zero-byte or truncated file exists and has a size. `_atomic_savez`'s tmp-then-rename means a
    `.npz` at its final name is closed -- but the ROOT combine output is written by `TFile` and its
    `Close()` is the only thing that finalizes it, so existence is not completion there either.
    An unreadable product gets a receipt only over this function's dead body.
    """
    suffix = Path(path).suffix.lower()
    if suffix == ".npz":
        import numpy as np
        with np.load(path, allow_pickle=True) as handle:
            return {"kind": "npz", "keys": sorted(handle.files)}
    if suffix == ".root":
        # ROOT's own trailer, checked WITHOUT importing ROOT: a valid TFile opens with the magic
        # bytes `root` and is finalized by a non-zero END offset in its header. A truncated or
        # never-Closed file fails one of the two. Checking bytes rather than importing keeps this
        # gate runnable on a checkout with no ROOT -- which is every local one, measured.
        with open(path, "rb") as handle:
            head = handle.read(8)
        require(head[:4] == b"root",
                f"{path} does not begin with ROOT's magic bytes; it is not a TFile")
        size = os.path.getsize(path)
        require(size > 100, f"{path} is {size} bytes -- a TFile header alone is longer")
        return {"kind": "root", "bytes": size}
    with open(path, "rb") as handle:
        handle.read(1)
    return {"kind": "opaque", "bytes": os.path.getsize(path)}


def producer_provenance(*, bank=None, population_declared=""):
    """The producer's OWN stamps, imported from it. Never recomputed and never built in shell.

    `unified_throw_cov.code_provenance` and `_bank_cv_digest` are the single source of the code
    revision, the producer digest and the bank digest, and they stamp the literal ``UNAVAILABLE``
    rather than omitting a key so `check_receipt` can refuse it. Recomputing any of them here --
    or, as the first version of the combine launcher did, in two nested `python3 -c` calls inside a
    shell-quoted JSON string -- would be a second implementation of exactly the object whose job is
    to be the one stamp.

    `population_declared` is a comma-separated subset of ``{"throw", "block"}``. Anything not
    listed is recorded as ``0``, which is a REACHABLE value that `check_receipt` refuses; writing 1
    unconditionally would be the vacuous-flag form this repository deleted from
    `eavailW_covariance.write_ew_outputs` under lane D's finding 1.
    """
    import unified_throw_cov as producer

    declared = {piece.strip() for piece in population_declared.split(",") if piece.strip()}
    unknown = declared - {"throw", "block"}
    require(not unknown,
            f"--population-declared names {sorted(unknown)}, which are not populations. The only "
            f"two are 'throw' and 'block'; a typo here would silently record 0 and read as a "
            f"deliberate non-declaration.")
    provenance = dict(producer.code_provenance())
    provenance["bank_cv_sha256"] = (producer._bank_cv_digest(bank) if bank else "UNAVAILABLE")
    provenance["throw_population_declared"] = 1 if "throw" in declared else 0
    provenance["block_population_declared"] = 1 if "block" in declared else 0
    provenance["cv_support_predicate"] = producer.CV_SUPPORT_PREDICATE
    return provenance


def write_receipt(*, product, out_path, arm, namespace, plan_json=None, extra=None,
                  code_root=None, allow_overwrite=False):
    """Write an arm's run receipt, STRICTLY AFTER the product exists and opens.

    THE ORDERING IS THE CONTENT. A receipt written before or beside its product records an
    intention; this one records an observation, because every check below runs against the file on
    disk and any failure raises instead of writing. That is why there is no `try/finally` here and
    no `os._exit` anywhere on the path: a receipt emitted from a bypassed `finally` would be the
    same declaration-in-parallel this exists to replace.

    Raises
    ------
    PrecursorError
        If the product is absent, empty, unreadable, or if the receipt path already exists and
        `allow_overwrite` is False.
    """
    product_path = Path(product)
    require(product_path.exists(),
            f"receipt refused: the product {product} does not exist. A receipt is written AFTER "
            f"the product, so an absent product means the arm did not complete -- and a receipt "
            f"claiming otherwise is exactly the artifact this ordering exists to prevent.")
    require(product_path.is_file(), f"receipt refused: {product} is not a regular file")
    size = product_path.stat().st_size
    require(size > 0, f"receipt refused: the product {product} is zero bytes")
    try:
        opened = _product_opens(str(product_path))
    except PrecursorError:
        raise
    except Exception as exc:                                  # noqa: BLE001 - reported, not hidden
        raise PrecursorError(
            f"receipt refused: the product {product} exists at {size} bytes but does not open "
            f"({type(exc).__name__}: {exc}). Existence is not completion.") from exc

    out = Path(out_path)
    require(not out.exists() or allow_overwrite,
            f"receipt refused: {out_path} already exists. Same rule and the same reason as "
            f"`z_build_path.preservation_guard`: overwriting a receipt destroys the record of the "
            f"run that wrote it. Name a new path, or pass --allow-overwrite deliberately.")

    receipt = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "subject": "z-prospective-unified-throw-precursor",
        "arm": arm,
        "namespace": namespace,
        "product": {
            "path": str(product_path.resolve()),
            "bytes": size,
            "sha256": sha256_file(str(product_path)),
            "opened_as": opened,
        },
        "code_root": str(Path(code_root).resolve()) if code_root else _REPO,
        "code_revision": _git_head(code_root or _REPO),
        "slurm": {key: os.environ.get(key, "") for key in
                  ("SLURM_JOB_ID", "SLURM_ARRAY_JOB_ID", "SLURM_ARRAY_TASK_ID",
                   "SLURM_JOB_NAME", "SLURM_NNODES", "SLURM_CPUS_PER_TASK")},
        "namespace_plan": plan_json,
        "extra": dict(extra or {}),
    }
    _atomic_write_json(out, receipt)
    return receipt


def _atomic_write_json(path, payload):
    """tmp-then-rename, so a receipt is never half-written. Mirrors `_atomic_savez`'s guarantee."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=str(path.parent),
                                         prefix=f".{path.name}.", delete=False)
    temporary = handle.name
    try:
        with handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        if os.path.exists(temporary):
            os.unlink(temporary)
        raise


def check_receipt(receipt_path, *, require_population=True):
    """Gate a precursor receipt: the product it names must still be the product it measured.

    BOTH DIRECTIONS. A receipt naming a product that has since been replaced is as much a finding
    as an absent receipt: the digest is re-read from disk here rather than trusted from the file.
    That is the difference between a receipt FIELD -- a timestamped observation -- and a current
    state.

    `require_population` gates on the two population flags the producer now writes. They have two
    reachable values each, so this is not a criterion that passes on every product carrying it:
    a 4D combine legitimately carries 0 and is refused here, which is correct, because it is not a
    Z precursor product.
    """
    path = Path(receipt_path)
    require(path.exists(), f"receipt {receipt_path} does not exist")
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PrecursorError(f"receipt {receipt_path} is not readable JSON: {exc}") from exc
    require(isinstance(receipt, dict), f"receipt {receipt_path} is not an object")
    require(receipt.get("schema_version") == RECEIPT_SCHEMA_VERSION,
            f"receipt schema_version {receipt.get('schema_version')!r} != "
            f"{RECEIPT_SCHEMA_VERSION}; refused rather than migrated")
    product = receipt.get("product")
    require(isinstance(product, dict) and product.get("path") and product.get("sha256"),
            "receipt carries no product path and digest")
    require(os.path.exists(product["path"]),
            f"the receipt's product {product['path']} no longer exists. A receipt field is a "
            f"timestamped observation, never a current state.")
    live = sha256_file(product["path"])
    require(live == product["sha256"],
            f"the receipt's product has CHANGED since it was measured: on disk {live}, in the "
            f"receipt {product['sha256']}. The receipt is stale, not the product wrong -- but "
            f"nothing downstream may cite the receipt for this file.")
    require(receipt.get("code_revision") not in (None, "", "UNAVAILABLE"),
            "receipt code_revision is absent or UNAVAILABLE; the run cannot be tied to a tree")
    if require_population:
        extra = receipt.get("extra") or {}
        for flag in ("throw_population_declared", "block_population_declared"):
            require(flag in extra,
                    f"receipt does not carry {flag}. The producer writes it with TWO reachable "
                    f"values, so its absence means this receipt predates population validation.")
            require(int(extra[flag]) == 1,
                    f"receipt {flag} = {extra[flag]!r}: the arm's file population was never "
                    f"declared, so this product cannot say its slabs are the ones its own run "
                    f"produced. A foreign inventory-complete namespace passes every content "
                    f"check -- measured -- so the undeclared case is refused.")
        for field in REQUIRED_PROVENANCE:
            value = extra.get(field)
            require(value not in (None, "", "UNAVAILABLE"),
                    f"receipt extra.{field} = {value!r}; UNAVAILABLE is stamped deliberately by "
                    f"the producer so this gate can see it, and it is refused here rather than "
                    f"in the producer, which must not make provenance a scheduler dependency")
    return {"ok": True, "receipt": str(path), "product": product["path"], "sha256": live}


# ======================= (h) THE CAMPAIGN: OWNERSHIP REPLACES PER-TASK EMPTINESS ================
# JOSEPH, 2026-09-13, authorizing this bounded repair. Three phases, verbatim in substance:
#
#   (1) CAMPAIGN INITIALIZATION -- *"Atomically establish a fresh namespace and bind it to one
#       immutable campaign manifest, including expected task identities, outputs, input digests,
#       and code revision."*
#   (2) TASK EXECUTION -- *"Verify campaign membership and exclusive ownership of that task's
#       output. Permit correctly bound sibling outputs from the same campaign. Refuse foreign
#       artifacts, duplicate execution, and overwrites."*
#   (3) COMBINATION -- *"Require the exact completed population and its bindings before
#       consumption."*
#
# THE DEFECT THIS REPLACES IS AN ARRAY DEFECT, NOT A CALL DEFECT, AND THAT DISTINCTION IS THE WHOLE
# REPAIR. `check_namespace_fresh` above is correct for ONE invocation and wrong for an ARRAY. The
# contract is enforced PER INVOCATION inside the producer (`unified_throw_cov.py` `do_throws`,
# `do_blockunits`, `do_combine`) while `sbatch_uthrow_block_5d.sh:398-402` passes
# `--z-namespace-arm block` for EVERY task whenever the namespace is set. So in the authorized
# 21-task block array (`--array=0-20%10`) task 0 writes `block5d_knobs.npz` and tasks 1-20 then
# glob `block5d_*.npz`, MATCH it, and REFUSE. The `run` arm's 40 tasks (`--array=0-39%40`) have
# the identical shape. At `%10` this is a RACE -- the tasks that start before task 0 publishes
# pass, the later ones refuse -- so the failure is timing-dependent and leaves a partially
# populated namespace that the next attempt also refuses.
# A SINGLE-TASK PROBE PASSED AND COMPLETED (array index 0, 3.3253 h). Index 0 is the one case that
# cannot hit this, so the probe could not have found it: a contract validated for one task did not
# compose to the array, and the composition is what is repaired here.
#
# FRESHNESS IS RELOCATED, NOT WEAKENED AND NOT BYPASSED. The empty-directory predicate moves to
# `initialize_campaign`, which is the only place it can hold once tasks are staggered, and there it
# becomes ATOMIC -- an exclusive `mkdir` rather than a glob another task can invalidate a second
# later. At task level it is replaced by an ownership predicate that is strictly stronger about the
# things that matter, and each clause names what the old predicate could not do:
#
#   * NOTHING FOREIGN. Every product in the arm directory must carry a CLAIM from THIS campaign.
#     The old predicate refused the NAME whoever wrote it, which is why it refused siblings -- and
#     it could not tell a foreign campaign's product at a DECLARED basename from this campaign's
#     own. `uq_5d/z_probe_20260912/block_slabs_5d/block5d_knobs.npz` is exactly that artifact: a
#     real, valid product of a DIFFERENT campaign, at a basename this campaign also declares.
#   * NOTHING DUPLICATED. One `O_EXCL` claim per (arm, task id). Two processes for one task id race
#     for one create and the loser refuses. The old predicate passed BOTH of them for as long as
#     neither had published, which is precisely the `%10` race window.
#   * NOTHING OVERWRITTEN. The task's declared product must not already exist.
#   * AND THREE BINDINGS THE OLD PREDICATE DID NOT CHECK AT ALL: the A-2(f) code listing digest,
#     the input digests, and the estimator/draw seeds.
#
# WHAT IS NOT COVERED, NAMED RATHER THAN LEFT TO BE DISCOVERED: the `dump` arm. Its 8-task array
# (`--array=0-7`, no throttle) has the same composition defect and is NOT repaired here. Two
# reasons, both measured: the authorized campaign CONSUMES the digest-bound, unmoved bank at
# `<data root>/nd-unfolding/bank_uthrow_5d` (374 entries, 2026-09-13) rather than re-dumping it, so
# no authorized task takes that path; and the dump arm has no derivable per-task output layout --
# `declare_arm_task_outputs` refuses to invent one because `unified_throw.do_dump` addresses its
# bank files by CONTENT (a round-robin of bands and flux ids over `--ngroups`), so there is no
# (task id -> basename) map to take ownership of. That arm therefore keeps the pre-existing
# per-invocation freshness predicate unchanged, and `enforce_namespace_contract` says so at the
# branch rather than here, where its next user would not meet it.

#: Refused rather than migrated, on `RECEIPT_SCHEMA_VERSION`'s precedent: a campaign is the
#: identity every product of one production binds to, and a silently migrated manifest is a
#: different campaign wearing the same digest.
CAMPAIGN_SCHEMA_VERSION = "z-campaign/1"

#: ONE directory inside the namespace holds the manifest, the claims and the completion records.
#: `_campaign` matches NO arm product glob -- not `block5d_*.npz`, not `uthrow5d_slab_*.npz`, not
#: `*.np[yz]`, not `unified_throw_cov_5d.root` -- and the test asserts that over `ARM_LAYOUT`
#: rather than over today's four literals. A campaign directory that its own freshness sweep or
#: population check selected would be self-defeating.
CAMPAIGN_DIR = "_campaign"
CAMPAIGN_MANIFEST_NAME = "campaign.json"

#: The A-2(f) source-manifest RECORD the launchers already require -- `sbatch_uthrow_run_5d_fast.sh
#: :161` makes `MNV_SOURCE_MANIFEST` mandatory with no default -- and already `--compare` against
#: the live code root with `--require-clean --require-checkout --require-no-nested-checkout
#: --require-not-nested --require-readonly` BEFORE the producer starts. The campaign binds the code
#: revision THROUGH that record rather than through a scheme of its own, and the composition is:
#: the launcher's preflight establishes record == live tree, `verify_campaign_code` establishes
#: manifest == record, so together manifest == live. BOTH HALVES ARE PINNED BY A TEST, because two
#: rulings that each hold only under the other's precondition compose into a defect when only prose
#: joins them.
#:
#: ⚠ READ, NOT IMPORTED, AND THE LAZINESS IS LOAD-BEARING. Importing `mnv_source_manifest` on the
#: task path would add a repository module to the guarded process's resolved import set, which
#: `mnv_import_set_ratchet.py` pins per entrypoint as an IDENTITY and not a floor -- so the binding
#: would be paid for with a pin that can only be rewritten from a clean guarded run. The import
#: happens ONLY inside `campaign_code_binding`, which runs at initialization, off the guarded path.
SOURCE_MANIFEST_ENV = "MNV_SOURCE_MANIFEST"

#: The array task id. This is the OTHER half of the ownership binding: the campaign says which
#: basename task N owns, and this says which task is running. Without it, the basename check
#: compares the product against itself.
ARRAY_TASK_ENV = "SLURM_ARRAY_TASK_ID"

#: Arms whose products are addressed by CONTENT rather than by task, so no (task -> basename)
#: ownership map exists. See the section header for why this is a named residual, not a hole.
CONTENT_ADDRESSED_ARMS = frozenset({"dump"})

#: Arm -> the arms it CONSUMES. Stated once, here, because it is the SAME relation `do_combine`
#: already enforces when it refuses a `--combine` or `--block-slabs` glob that does not resolve to
#: those two arms' directories. Phase 3 runs over this relation, and it runs BEFORE the consuming
#: task takes its claim -- which is not a detail:
#:
#:   ⚠ A CONSUMPTION GATE AFTER THE CLAIM WOULD BURN THE CLAIM ON A PREMATURE RUN. The combine is
#:   normally submitted while the arrays are still draining, so refusing it is the ORDINARY case,
#:   not an error; if the refusal happened after the `O_EXCL` create, the combine task would hold
#:   its own claim for a run that never happened and every later attempt would refuse itself as a
#:   duplicate. Measured: the first version of this repair did exactly that, and the integration
#:   test that runs the real `do_combine` twice -- once incomplete, once complete -- is what showed
#:   it. A guard that fires on every correct run is not a guard, and that one fired on the second.
CONSUMED_ARMS = {"combine": ("run", "block")}

#: The first attempt of a logical task. Recovery adds attempts 2, 3, ... ALONGSIDE it.
FIRST_ATTEMPT = 1

#: Where the per-attempt authorization records and the preserved evidence live, both under
#: `_campaign/`. Created by `initialize_campaign` for a new campaign and, for a campaign that was
#: initialized before recovery existed, by `recover_task` -- which ADDS two empty directories and
#: touches neither the manifest nor any existing record.
RECOVERY_DIRNAME = "recovery"
EVIDENCE_DIRNAME = "evidence"

#: Slurm states in which the previous attempt's process MAY STILL BE WRITING, so recovery refuses.
#:
#: ⚠ THIS IS NOT THE COMPLEMENT OF `z_precursor_admission.TERMINAL_STATES`, and reading it as one
#: is the mistake that module already recorded paying for. `REQUEUED` is in NEITHER set: it is a
#: historical attempt state -- that execution ended, and the TASK continued -- and a task whose
#: dump is 1882 `REQUEUED` rows plus a final `CANCELLED` is finished. Treating "not terminal" as
#: "live" made that guard fire on a correct state.
#:
#: ⚠ `SPECIAL_EXIT` IS LIVE HERE AND TERMINAL THERE, DELIBERATELY, AND THE DIVERGENCE IS THE POINT.
#: For ACCOUNTING it is terminal: nothing further will be charged unless somebody acts. For
#: "can the previous attempt still write", it is not: `SPECIAL_EXIT` is a requeue held in place,
#: and a release makes it run again. Two questions, two answers; the accounting module stays the
#: authority for charged hours and this stays the authority for whether a writer can reappear.
ATTEMPT_MAY_STILL_WRITE_STATES = frozenset({
    "PENDING", "RUNNING", "SUSPENDED", "COMPLETING", "CONFIGURING", "RESIZING", "STAGE_OUT",
    "SIGNALING", "REQUEUE_HOLD", "REQUEUE_FED", "RESV_DEL_HOLD", "SPECIAL_EXIT",
})

#: States that end an ATTEMPT without ending the TASK. Enumerated rather than inferred so an
#: unrecognised state falls through to the refusal below instead of being silently tolerated.
ATTEMPT_HISTORICAL_STATES = frozenset({"REQUEUED"})

_CLAIM_RE = re.compile(
    r"^(?P<arm>[a-z]+)\.task-(?P<task>\d+)(?:\.attempt-(?P<attempt>\d+))?\.claim\.json$")
_RECEIPT_RE = re.compile(
    r"^(?P<arm>[a-z]+)\.task-(?P<task>\d+)(?:\.attempt-(?P<attempt>\d+))?\.receipt\.json$")
_RECOVERY_RE = re.compile(
    r"^(?P<arm>[a-z]+)\.task-(?P<task>\d+)\.recovery-(?P<attempt>\d+)\.json$")


def campaign_arms():
    """The arms a campaign can own, DERIVED as the complement of the content-addressed set.

    Never a second literal list: one hand-written population here and another in `ARM_LAYOUT` is
    how two spellings of one set start disagreeing, and the disagreement would be invisible.
    """
    return tuple(sorted(set(ARM_LAYOUT) - CONTENT_ADDRESSED_ARMS))


def campaign_paths(data_root, namespace):
    """Every campaign-owned path under one namespace.

    Anchored on the COMBINE arm's directory, because that IS the namespace root (`ARM_LAYOUT`'s
    `"."`), so this cannot drift from `arm_directory`'s idea of where the namespace is.
    """
    root = Path(arm_directory(data_root, namespace, "combine")) / CAMPAIGN_DIR
    return {"root": str(root),
            "manifest": str(root / CAMPAIGN_MANIFEST_NAME),
            "claims": str(root / "claims"),
            "receipts": str(root / "receipts"),
            "recovery": str(root / RECOVERY_DIRNAME),
            "evidence": str(root / EVIDENCE_DIRNAME)}


def _canonical_json(body):
    """The exact bytes a campaign digest is taken over: sorted keys, no insignificant whitespace."""
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")


def campaign_digest(body):
    """The campaign's IDENTITY: sha256 over its own canonical body.

    Self-describing on purpose. A random token would identify the campaign without being able to
    detect an edit to it; this makes "what campaign is this" and "is this still the manifest that
    was written" the same question -- and `load_campaign` recomputes it on every read rather than
    trusting the stored value, which is the same rule `check_receipt` applies to a product digest.
    """
    return hashlib.sha256(_canonical_json(body)).hexdigest()


def claim_name(arm, task_id, attempt=FIRST_ATTEMPT):
    """The claim filename. THE TASK IDENTITY IS IN THE NAME, and that is not cosmetic.

    A concurrent reader of the claims directory must be able to attribute a claim to a task WITHOUT
    parsing its body: the claim is created by `O_EXCL` at its final name and only then filled, so a
    reader can legitimately observe it empty. Putting the identity in the name makes the ownership
    scan a set operation over filenames, with no window in which a real claim reads as unparseable.

    ⚠ ATTEMPT 1'S NAME IS UNSUFFIXED, AND THAT ASYMMETRY IS DELIBERATE. Recovery is ADDITIVE --
    Joseph: *"Do not implement recovery by deleting a claim and pretending the first attempt never
    existed"* -- so attempt 1's artifacts keep the exact names a campaign initialized before
    recovery existed already wrote. Renaming them to `attempt-1` would be a migration of the very
    records that prohibition protects, over a namespace that may already be populated.
    """
    attempt = int(attempt)
    require(attempt >= FIRST_ATTEMPT, f"attempt {attempt} is below the first attempt")
    if attempt == FIRST_ATTEMPT:
        return f"{arm}.task-{int(task_id)}.claim.json"
    return f"{arm}.task-{int(task_id)}.attempt-{attempt}.claim.json"


def receipt_name(arm, task_id, attempt=FIRST_ATTEMPT):
    """The completion-record filename, keyed the same way as the claim it closes."""
    attempt = int(attempt)
    require(attempt >= FIRST_ATTEMPT, f"attempt {attempt} is below the first attempt")
    if attempt == FIRST_ATTEMPT:
        return f"{arm}.task-{int(task_id)}.receipt.json"
    return f"{arm}.task-{int(task_id)}.attempt-{attempt}.receipt.json"


def recovery_name(arm, task_id, attempt):
    """The record that AUTHORIZES attempt `attempt` (>= 2) of a logical task.

    Its existence is what makes a later attempt runnable at all: `authorized_attempt` counts these
    and a task's current attempt is `1 + <how many recovery records it has>`. That is why the task
    side needs no new environment variable, and therefore no launcher flag -- the producer already
    knows the namespace, the arm and `SLURM_ARRAY_TASK_ID`, which is the whole key.
    """
    attempt = int(attempt)
    require(attempt > FIRST_ATTEMPT,
            f"recovery authorizes attempt {FIRST_ATTEMPT + 1} onwards; attempt {attempt} is the "
            f"first attempt and needs no authorization")
    return f"{arm}.task-{int(task_id)}.recovery-{attempt}.json"


def _utc_now():
    """One spelling of the timestamp, so the manifest and the claims cannot disagree in format."""
    return datetime.now(timezone.utc).isoformat()


def _write_json_exclusive(path, payload):
    """Create a JSON record at `path` with `O_EXCL`, or REFUSE.

    NOT tmp-then-rename, and the difference is the whole point. `_atomic_write_json` publishes by
    `os.replace`, which SILENTLY REPLACES an existing file -- right for a receipt written once by a
    process that has already proved it may, and wrong for the two records here, whose entire job is
    to fail when somebody got there first. `O_CREAT|O_EXCL` is the create-or-fail primitive: POSIX
    requires it to be atomic against other creates, and `/pscratch` is Lustre (measured
    2026-09-13), which serializes the create on the metadata server.
    ⚠ NOT MEASURED ON LUSTRE ITSELF. The concurrency controls in the test suite run on a local
    filesystem, because writing to `/pscratch` was outside this repair's authorization. The Lustre
    claim rests on POSIX `O_EXCL` semantics, not on an observation.
    """
    path = Path(path)
    body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    try:
        fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError as exc:
        raise PrecursorError(f"{path} already exists and this record is written EXCLUSIVELY: "
                             f"whoever created it got there first") from exc
    with os.fdopen(fd, "wb") as handle:
        handle.write(body)
        handle.flush()
        os.fsync(handle.fileno())
    return str(path)


# ------------------------------------------------- PHASE 1: the immutable campaign manifest ----
def campaign_code_binding(code_root, source_manifest):
    """Bind the code revision through the EXISTING A-2(f) listing digest.

    Not a new scheme: `mnv_source_manifest.build` already defines "the digest of this tree's
    tracked sources" as sha256 over the `<sha256>  <relpath>` listing, and already has a
    both-directions `compare`. The recorded manifest supplied here must be IDENTICAL to the live
    tree, so the campaign binds BYTES rather than a branch name.

    ⚠ CLEANLINESS IS NOT RE-ASSERTED HERE, DELIBERATELY. `--require-clean` and `--require-readonly`
    are enforced by each launcher's own preflight against the EXECUTING tree at run time
    (`sbatch_uthrow_run_5d_fast.sh:206-210`). Repeating them would be a second implementation of a
    rule that already has an instrument, and it would fire on a correct initialization from a tree
    carrying untracked scratch. `dirty_count` and `head` are RECORDED so a reader can see what the
    tree was; the LISTING digest -- over tracked content, so unaffected by untracked files -- is
    what is gated.
    """
    import mnv_source_manifest as srcman

    record_path = Path(source_manifest)
    require(record_path.is_file(),
            f"--source-manifest {source_manifest!r} is not a file. It must be the A-2(f) record "
            f"written by `mnv_source_manifest.py --repo <code root> --write`, which is the same "
            f"record the launchers require as {SOURCE_MANIFEST_ENV} and compare against the "
            f"executing tree before the producer starts.")
    try:
        recorded = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PrecursorError(f"the A-2(f) record {source_manifest} is not readable JSON: "
                             f"{exc}") from exc
    live = srcman.build(str(code_root))
    diff = srcman.compare(recorded, live)
    require(diff["identical"],
            f"the A-2(f) record {source_manifest} is NOT the code root {code_root}: "
            f"{len(diff['removed'])} removed, {len(diff['added'])} added, "
            f"{len(diff['changed'])} changed (recorded digest {diff['recorded_digest']}, live "
            f"{diff['live_digest']}). A campaign cannot bind a code revision it cannot name: "
            f"either the record is stale or the tree is not the one it describes.")
    return {"code_root": str(Path(code_root).resolve()),
            "listing_sha256": live["listing_sha256"],
            "file_count": live["file_count"],
            "head": live["head"],
            "dirty_count": live["dirty_count"],
            "source_manifest": str(record_path.resolve()),
            "source_manifest_sha256": sha256_file(str(record_path))}


def bank_listing(bank):
    """`(entry count, listing digest)` over the bank's regular files, by NAME and SIZE.

    The same listing IDIOM as `mnv_source_manifest.build`, for the reason recorded there: the
    digest is over a sorted listing rather than over a set, so a RENAME moves it even when no byte
    changed. `<size>  <name>` rather than `<sha256>  <name>` because the bank's `cv.npz` alone is
    2 939 596 884 bytes (measured 2026-09-13) -- a content digest over 374 entries totalling ~26 GB
    is affordable ONCE, at initialization, and is not affordable in each of 61 tasks.
    THE RESIDUAL IS STATED WHERE IT IS RELIED ON: this cannot see a same-size content change. The
    content binding for the two inputs carrying the physics is in `campaign_inputs` -- `cv.npz`
    once at initialization, and the 11 328-byte flux ratio table on EVERY task.

    ⚠ `os.listdir` AND NOT `Path.iterdir`, AND AN INCOMPLETE WRITE IS EXCLUDED. `iterdir` is on
    this repository's banned-call list (`test_the_INVISIBILITY_claim_is_SCOPED_to_the_idioms_it_
    covers`, enforced by AST over every `nd-unfolding/*.py`) precisely because it SEES the
    glob-invisible `.mnv-incomplete.<product>.<token>.partial` temps -- so a listing built with it
    would move when a producer died mid-write in the bank, making a transient look like a changed
    input. The predicate is IMPORTED from the producer rather than respelled here.
    """
    import unified_throw_cov as producer

    path = Path(bank)
    require(path.is_dir(), f"bank {bank!r} is not a directory")
    names = sorted(n for n in os.listdir(str(path))
                   if os.path.isfile(os.path.join(str(path), n))
                   and not producer.is_incomplete_write(n))
    listing = "".join(f"{os.path.getsize(os.path.join(str(path), n))}  {n}\n" for n in names)
    return len(names), hashlib.sha256(listing.encode()).hexdigest()


def campaign_inputs(bank):
    """The campaign's input bindings, measured ONCE, at initialization.

    `flux_univ_ratio.npy` is a REQUIRED validated input and not an incidental extra:
    `unified_throw_cov._flux_ratio_table` divides each flux universe by THAT universe's flux
    integral (J28), its fallback needs ROOT and a separate universe file, and the live table is
    measurably not all-ones (min 0.9104, max 1.1371 over shape (100, 14)) -- so a campaign that did
    not bind it could silently consume a different normalization. Its NAME comes from
    `flux_universe.BANKED_RATIO_NAME`, the producer's own constant, never from a literal here.
    """
    import flux_universe
    import unified_throw_cov as producer

    path = Path(bank)
    count, listing = bank_listing(path)
    cv_digest = producer._bank_cv_digest(str(path))
    require(cv_digest != "UNAVAILABLE",
            f"the bank {bank} has no readable cv.npz. `_bank_cv_digest` stamps the literal "
            f"UNAVAILABLE rather than omitting a key so that a gate can see it, and it is refused "
            f"here: a campaign whose central input cannot be digested binds nothing.")
    ratio = path / flux_universe.BANKED_RATIO_NAME
    require(ratio.is_file(),
            f"the bank {bank} carries no {flux_universe.BANKED_RATIO_NAME}. That table is a "
            f"REQUIRED validated input, not an incidental extra -- without it "
            f"`unified_throw_cov._flux_ratio_table` falls back to a ROOT-dependent rebuild from "
            f"--flux-universe-file, which is a different input with a different provenance.")
    return {"bank": str(path.resolve()),
            "entry_count": count,
            "listing_sha256": listing,
            "bank_cv_sha256": cv_digest,
            "flux_ratio_name": flux_universe.BANKED_RATIO_NAME,
            "flux_ratio_bytes": ratio.stat().st_size,
            "flux_ratio_sha256": sha256_file(str(ratio))}


def campaign_seeds(environ=None):
    """The seeds a campaign pins, DERIVED from `seed_offset_policy` rather than from a launcher.

    The precursor is coherence group 2, whose archive estimator baseline is 1000, and
    `ARCHIVE_DRAW_SEED` pins the draw seed at the literal 1000 for every offset. Both come from the
    policy module, which is their single source. A literal here would be a second statement of the
    grouping, and THE BASELINES ARE NOT SHARED -- group 1's is 42 -- so a wrong one would be
    silently plausible. Nothing is unified: only group 2's row is read.
    """
    import seed_offset_policy as policy

    group, baseline = policy.LEG_BASELINES["unified_throw_cov"]
    declared, value = policy.declared_offset(environ)
    return {"estimator_group": group,
            "estimator_baseline": int(baseline),
            "estimator_seed": int(baseline) + int(value),
            "draw_seed": int(policy.ARCHIVE_DRAW_SEED),
            "member_offset_declared": int(declared),
            "member_offset": int(value)}


def campaign_arm_table(code_root, arms=None):
    """Every covered arm's declared task identities and outputs, from its OWN `#SBATCH` lines.

    DERIVED, NEVER RETYPED, which is the rule `parse_sbatch_arm` already exists to keep: a range
    literal here would be a second implementation of the arm's population, and a declaration
    derived from anything but the launcher cannot be right about what the launcher will produce.
    """
    names = campaign_arms() if arms is None else tuple(sorted(set(arms)))
    require(names, "a campaign with no arms declares no task identities and can own nothing")
    table = {}
    for arm in names:
        require(arm in ARM_LAYOUT, f"unknown arm {arm!r}; known arms are {sorted(ARM_LAYOUT)}")
        require(arm not in CONTENT_ADDRESSED_ARMS,
                f"arm {arm!r} cannot be campaign-owned: its products are addressed by CONTENT and "
                f"not by task, so there is no (task id -> basename) map to take exclusive "
                f"ownership of. `unified_throw.do_dump` splits bands and flux ids round-robin over "
                f"--ngroups, and `declare_arm_task_outputs` refuses to invent a layout for it. The "
                f"authorized campaign consumes the digest-bound bank as an INPUT; see "
                f"`enforce_namespace_contract`, which leaves that arm's pre-existing "
                f"per-invocation freshness predicate exactly as it was.")
        launcher = Path(code_root) / ARM_LAUNCHERS[arm]
        require(launcher.is_file(),
                f"arm {arm!r}'s launcher {launcher} is absent from the code root. The declaration "
                f"is derived from that file's own #SBATCH lines, so without it there is nothing to "
                f"derive and a hand-written population would be a fiction.")
        info = parse_sbatch_arm(launcher)
        if arm == "combine":
            # NOT `declare_arm_task_outputs`, which refuses here and is RIGHT to. The combine arm's
            # basename is not DERIVED from the array -- it is the arm's single declared product in
            # `ARM_LAYOUT`, and the launcher's absence of an `--array` line only says there is one
            # task. Two different derivations, kept apart so neither borrows the other's warrant.
            require(info["array_spec"] is None and info["task_ids"] == [0],
                    f"the combine launcher now declares an array ({info['array_spec']!r}); its "
                    f"single-product layout no longer describes it, and the campaign must not "
                    f"guess which task writes the one file")
            outputs = {"0": ARM_LAYOUT["combine"][1]}
        else:
            outputs = {str(t): n for t, n in declare_arm_task_outputs(arm, launcher).items()}
        table[arm] = {"launcher": ARM_LAUNCHERS[arm],
                      "array_spec": info["array_spec"],
                      "task_ids": info["task_ids"],
                      "n_tasks": info["n_tasks"],
                      "throttle": info["throttle"],
                      "time_limit_seconds": info["time_limit_seconds"],
                      "product_glob": ARM_LAYOUT[arm][1],
                      "outputs": outputs}
    for consumer, consumed in CONSUMED_ARMS.items():
        missing = sorted(set(consumed) - set(table)) if consumer in table else []
        require(not missing,
                f"this campaign declares the consuming arm {consumer!r} but not {missing}, which "
                f"it reads. Phase 3 requires the exact completed population of every consumed arm, "
                f"and an undeclared arm has no declared population to require -- so the consumer "
                f"would proceed with its inputs ungated. Declare them, or drop the consumer.")
    return table


def initialize_campaign(*, data_root, code_root, source_manifest, bank, namespace=None,
                        arms=None, label="", environ=None):
    """PHASE 1. Establish a fresh namespace ATOMICALLY and bind it to one immutable manifest.

    THE ORDER OF THE FIRST TWO STEPS IS THE DESIGN, and neither replaces the other:

      * `check_namespace_fresh` first, for the DIAGNOSTIC. It names the arm, the product count and
        example basenames, which is what an operator needs; an `EEXIST` from the step below says
        only that a directory is there.
      * then an EXCLUSIVE `os.makedirs(..., exist_ok=False)`, for the ATOMICITY Joseph asked for.
        This is the step that makes "fresh" a fact rather than an observation: the glob above is
        true of an instant, and two operators initializing the same namespace concurrently both
        pass it. Exactly one can win the create.

    AN EXISTING BUT EMPTY NAMESPACE IS REFUSED, deliberately rather than by oversight: an empty
    directory somebody else made is indistinguishable from one this initialization made, so it
    cannot be claimed. There is NO `--force`. Overriding this is "bypassing freshness", which the
    authorization excludes by name; the remedy is a new namespace.
    """
    env = os.environ if environ is None else environ
    ns = (resolve_namespace(env) if namespace is None
          else resolve_namespace({NAMESPACE_ENV: namespace}))
    check_no_member_axis(env)
    require(Path(data_root).is_absolute(),
            f"--data-root {data_root!r} is relative. Every path in the manifest is resolved once, "
            f"here, and a relative root would anchor the campaign to whichever directory the "
            f"operator happened to be standing in.")
    plan = namespace_plan(data_root, namespace=ns)
    check_namespace_fresh(plan)
    # EVERY MEASUREMENT HAPPENS BEFORE THE FIRST `mkdir`, and that ordering is the difference
    # between a refusal and a namespace nobody can use. The A-2(f) rebuild and the bank digest can
    # both fail -- a stale record, an unreadable `cv.npz` -- and an earlier version of this
    # function created the directory tree first, so such a failure left a namespace root with no
    # manifest in it: unusable by every task (no campaign) AND unusable by a second attempt (the
    # exclusive create refuses it). Measuring first means a failure leaves NOTHING behind.
    # The window this opens is closed by the create itself: another operator who claims the
    # namespace while the 2.94 GB `cv.npz` is being digested wins, and this call refuses.
    body = {
        "schema_version": CAMPAIGN_SCHEMA_VERSION,
        "subject": "z-prospective-unified-throw-precursor-campaign",
        "label": str(label),
        "created_at_utc": _utc_now(),
        "namespace": ns,
        "data_root": str(Path(data_root).resolve()),
        "campaign_dir": CAMPAIGN_DIR,
        "arm_dirs": {arm: entry["dir"] for arm, entry in plan["arms"].items()},
        "code": campaign_code_binding(code_root, source_manifest),
        "inputs": campaign_inputs(bank),
        "seeds": campaign_seeds(env),
        "arms": campaign_arm_table(code_root, arms),
    }
    ns_root = Path(arm_directory(data_root, ns, "combine"))
    try:
        os.makedirs(ns_root, exist_ok=False)
    except FileExistsError as exc:
        raise PrecursorError(
            f"the namespace root {ns_root} ALREADY EXISTS. Initialization establishes a fresh "
            f"namespace atomically, by an exclusive create, so an existing directory is refused "
            f"even when its product globs are empty: an empty directory somebody else made cannot "
            f"be told from one this command made, and claiming it would be the adopt-what-is-"
            f"already-there move the authorization excludes. Name a fresh namespace.") from exc
    except OSError as exc:
        raise PrecursorError(f"cannot create the namespace root {ns_root}: {exc}") from exc
    paths = campaign_paths(data_root, ns)
    for directory in (paths["root"], paths["claims"], paths["receipts"], paths["recovery"],
                      paths["evidence"]):
        os.makedirs(directory, exist_ok=False)
    for arm, entry in plan["arms"].items():
        if arm != "combine":
            os.makedirs(entry["dir"], exist_ok=False)
    document = {"body": body, "campaign_digest": campaign_digest(body)}
    _write_json_exclusive(paths["manifest"], document)
    return {"campaign": {"body": body, "campaign_digest": document["campaign_digest"],
                         "path": paths["manifest"]},
            "plan": plan, "paths": paths}


def load_campaign(manifest_path):
    """Read a campaign manifest and RE-DERIVE its digest. Immutability is checked, not assumed.

    The stored digest is never trusted: `campaign_digest` is recomputed over the body on every
    read, so an edited manifest is a refusal rather than a differently-identified campaign. Same
    rule and the same reason as `check_receipt` re-reading the product digest from disk -- a
    recorded field is a timestamped observation, never a current state.
    """
    path = Path(manifest_path)
    require(path.is_file(),
            f"no campaign manifest at {manifest_path}. A precursor task must be a MEMBER of a "
            f"declared campaign: {NAMESPACE_ENV} names a namespace, and a namespace with no "
            f"manifest has no expected task identities, no bound inputs and no code revision, so "
            f"there is nothing for this task to own. Run `z_precursor.py campaign-init` first. "
            f"Freshness has not been bypassed -- it moved there, where it is atomic.")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PrecursorError(f"campaign manifest {manifest_path} is not readable JSON: "
                             f"{exc}") from exc
    require(isinstance(document, dict) and isinstance(document.get("body"), dict)
            and document.get("campaign_digest"),
            f"campaign manifest {manifest_path} is not a {{body, campaign_digest}} document")
    body = document["body"]
    require(body.get("schema_version") == CAMPAIGN_SCHEMA_VERSION,
            f"campaign schema_version {body.get('schema_version')!r} != "
            f"{CAMPAIGN_SCHEMA_VERSION}; refused rather than migrated")
    live = campaign_digest(body)
    require(live == document["campaign_digest"],
            f"the campaign manifest {manifest_path} has been EDITED since it was written: its body "
            f"now digests to {live}, the file records {document['campaign_digest']}. A campaign "
            f"manifest is IMMUTABLE -- every claim and every completion record binds that digest, "
            f"so an edit silently re-identifies the whole production.")
    return {"body": body, "campaign_digest": live, "path": str(path.resolve())}


# -------------------------------------------------------- PHASE 2: membership and ownership ----
def verify_campaign_code(campaign, environ):
    """The task's half of the code-revision binding: the A-2(f) record must be the bound one."""
    record = environ.get(SOURCE_MANIFEST_ENV)
    require(record not in (None, ""),
            f"{SOURCE_MANIFEST_ENV} is unset. The campaign binds the code revision through the "
            f"A-2(f) listing digest, and the launchers already make this variable mandatory with "
            f"no default (`sbatch_uthrow_run_5d_fast.sh:161`) and already compare the record "
            f"against the executing tree before the producer starts. Without it this task cannot "
            f"say which code revision it is running.")
    require(os.path.isfile(record),
            f"{SOURCE_MANIFEST_ENV}={record!r} does not name a readable file")
    try:
        recorded = json.loads(Path(record).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PrecursorError(f"the A-2(f) record {record} is not readable JSON: {exc}") from exc
    bound = campaign["body"]["code"]
    live = recorded.get("listing_sha256")
    require(live == bound["listing_sha256"],
            f"this task's A-2(f) record digests the tree to {live!r}, but the campaign is bound to "
            f"{bound['listing_sha256']!r} ({bound['file_count']} tracked files, HEAD "
            f"{bound['head']}). The code revision moved under the campaign. A staggered task must "
            f"run the revision its siblings ran, or the products are not one production.")
    # RECORDED, NOT GATED: re-emitting the record from a byte-identical tree changes `built_at_utc`
    # and therefore the FILE digest while the code revision is unchanged, so gating on the file
    # would refuse a correct run. The LISTING digest above is the code revision.
    return {"source_manifest": record,
            "listing_sha256": live,
            "source_manifest_sha256_bound": bound["source_manifest_sha256"],
            "source_manifest_sha256_live": sha256_file(record)}


def verify_campaign_inputs(campaign, bank):
    """The task's half of the input binding: the same bank, still the same listing and flux table.

    WHAT IS RE-VERIFIED PER TASK AND WHY IT IS NOT EVERYTHING, stated where it is relied on: the
    bank's listing (names and sizes, one `stat` per entry) and the 11 328-byte flux ratio table by
    CONTENT. `cv.npz` is 2 939 596 884 bytes and its content digest is bound ONCE, at
    initialization; re-reading 2.94 GB in each of 61 tasks to re-prove a fact the manifest already
    records would buy a same-size-content-change guarantee at a price the campaign does not have.
    """
    bound = campaign["body"]["inputs"]
    path = Path(bank)
    require(path.is_dir(), f"--bank {bank!r} is not a directory")
    require(str(path.resolve()) == bound["bank"],
            f"this task reads the bank at {path.resolve()}, but the campaign is bound to "
            f"{bound['bank']}. The inputs are part of the campaign identity: a task pointed at a "
            f"different bank is not a member of this production.")
    count, listing = bank_listing(path)
    require(count == bound["entry_count"] and listing == bound["listing_sha256"],
            f"the bank {bound['bank']} has CHANGED since the campaign was initialized: {count} "
            f"entries digesting to {listing}, bound {bound['entry_count']} entries at "
            f"{bound['listing_sha256']}. The listing is by name and size, so this is an added, "
            f"removed, renamed or resized input.")
    ratio = path / bound["flux_ratio_name"]
    require(ratio.is_file(), f"the bound input {ratio} is gone")
    live_ratio = sha256_file(str(ratio))
    require(live_ratio == bound["flux_ratio_sha256"],
            f"{bound['flux_ratio_name']} has CHANGED: on disk {live_ratio}, bound "
            f"{bound['flux_ratio_sha256']}. That table sets each flux universe's flux integral "
            f"(J28), so a changed one is a different normalization and not merely a different "
            f"file at the same name.")
    return {"bank": bound["bank"], "entry_count": count, "listing_sha256": listing,
            "flux_ratio_sha256": live_ratio}


def resolve_task_id(campaign, arm, environ):
    """WHICH task is this. The other half of every ownership statement below.

    REQUIRED FOR AN ARRAY ARM, and refused rather than inferred from the output path. Inferring it
    would make the basename check compare the product against itself -- a criterion that cannot
    disagree with the thing it checks. Every authorized precursor task of an array arm is an
    `sbatch` array task, so this variable is present on every correct run.
    """
    entry = campaign["body"]["arms"][arm]
    ids = sorted(int(t) for t in entry["task_ids"])
    raw = environ.get(ARRAY_TASK_ENV)
    if entry["array_spec"] is None:
        require(len(ids) == 1,
                f"arm {arm!r} declares no --array but carries {len(ids)} task ids; the campaign "
                f"cannot say which one is running")
        if raw not in (None, ""):
            require(raw.strip().isdigit() and int(raw) == ids[0],
                    f"{ARRAY_TASK_ENV}={raw!r}, but arm {arm!r} is the single non-array task "
                    f"{ids[0]}; this was submitted as something the campaign did not declare")
        return ids[0]
    require(raw not in (None, ""),
            f"{ARRAY_TASK_ENV} is unset and arm {arm!r} is an array ({entry['array_spec']}). "
            f"Ownership binds the ARRAY TASK to the one basename the campaign says it writes; "
            f"with no task id that binding compares the output to itself and holds vacuously.")
    text = raw.strip()
    require(text.isdigit(), f"{ARRAY_TASK_ENV}={raw!r} is not a non-negative integer")
    task = int(text)
    require(task in ids,
            f"{ARRAY_TASK_ENV}={task} is not a declared task of arm {arm!r}, whose campaign table "
            f"holds {len(ids)} ids derived from {entry['array_spec']}. A task outside the declared "
            f"population owns nothing here -- and note that a declared bracket must never be read "
            f"back from `sacct -X`, which Slurm REWRITES under throttling.")
    return task


def claimed_task_ids(claims_dir, arm):
    """Every task id of `arm` that holds a claim, read from FILENAMES only.

    RAISES rather than returning an empty set when the directory cannot be read -- the distinction
    `unified_throw_cov.ScanBlind` exists for. An unreadable claims directory is a check that could
    not look, and reporting it as "nothing is claimed" would make every product in the arm
    directory read as unclaimed and, worse, would leave a duplicate execution with no claim to
    collide with.
    """
    try:
        entries = os.listdir(claims_dir)
    except OSError as exc:
        raise PrecursorError(
            f"cannot read the campaign's claims directory {claims_dir} ({exc}). This is NOT "
            f"'no task has claimed anything': it is a check that could not look, and an empty "
            f"answer here would let a duplicate execution find no claim to collide with.") from exc
    found = set()
    for name in entries:
        match = _CLAIM_RE.match(name)
        if match is not None and match.group("arm") == arm:
            found.add(int(match.group("task")))
    return found


def _scan_attempts(directory, pattern, arm, task_id, *, kind):
    """`{attempt number: filename}` for one (arm, task) under `directory`, from FILENAMES only.

    Same could-not-look discipline as `claimed_task_ids`, and the same reason for reading names
    rather than bodies: a claim is created by `O_EXCL` and filled afterwards, so a concurrent
    reader can legitimately see it empty. An UNREADABLE directory raises; an ABSENT one is an empty
    result, because a campaign initialized before recovery existed has no `recovery/` directory and
    that is "no attempt has been authorized", not "nobody could look".
    """
    if not os.path.exists(directory):
        return {}
    try:
        entries = os.listdir(directory)
    except OSError as exc:
        raise PrecursorError(
            f"cannot read the campaign's {kind} directory {directory} ({exc}). This is NOT "
            f"'there are none': it is a check that could not look, and an empty answer here would "
            f"let a task run an attempt nobody authorized.") from exc
    found = {}
    for name in entries:
        match = pattern.match(name)
        if match is None or match.group("arm") != arm or int(match.group("task")) != int(task_id):
            continue
        raw = match.groupdict().get("attempt")
        found[FIRST_ATTEMPT if raw is None else int(raw)] = name
    return found


def task_claims(paths, arm, task_id):
    """`{attempt: claim filename}` for one logical task."""
    return _scan_attempts(paths["claims"], _CLAIM_RE, arm, task_id, kind="claims")


def task_receipts(paths, arm, task_id):
    """`{attempt: completion-record filename}` for one logical task."""
    return _scan_attempts(paths["receipts"], _RECEIPT_RE, arm, task_id, kind="receipts")


def task_recoveries(paths, arm, task_id):
    """`{attempt: recovery-record filename}` for one logical task; attempt numbers are >= 2."""
    return _scan_attempts(paths["recovery"], _RECOVERY_RE, arm, task_id, kind="recovery")


def authorized_attempt(paths, arm, task_id):
    """WHICH attempt of this logical task is authorized to run: `1 + <recovery records>`.

    THE RECOVERY RECORDS ARE THE AUTHORIZATION AND THE COUNTER AT ONCE, which is what keeps the
    task side free of a new flag: the producer already knows the namespace, the arm and
    `SLURM_ARRAY_TASK_ID`, and the campaign directory supplies the rest.

    A GAP REFUSES. Attempts must be authorized contiguously from 2, so `{2, 4}` is not "attempt 5
    is next" -- it is a record that was removed or hand-made, and either way the attempt history
    this repair exists to preserve is no longer intact.
    """
    numbers = sorted(task_recoveries(paths, arm, task_id))
    require(all(n > FIRST_ATTEMPT for n in numbers),
            f"{arm} task {task_id} has a recovery record for attempt {FIRST_ATTEMPT}, which needs "
            f"no authorization; the recovery directory has been hand-edited")
    expected = list(range(FIRST_ATTEMPT + 1, FIRST_ATTEMPT + 1 + len(numbers)))
    require(numbers == expected,
            f"{arm} task {task_id} has recovery records for attempts {numbers} but they must be "
            f"contiguous from {FIRST_ATTEMPT + 1}: {expected}. A gap means a record was removed or "
            f"written by hand, and the attempt history is no longer a record of what happened.")
    return FIRST_ATTEMPT + len(numbers)


# ------------------------------------------- (i) RECOVERY: a new attempt, never a reset --------
# JOSEPH, 2026-09-13, authorizing this bounded extension: *"explicitly approved per-task recovery"*,
# *"This authorizes implementation and tests, not any actual retry. Each retry still requires my
# explicit approval."* And the prohibition this whole design is shaped by, verbatim:
#
#     "Do not implement recovery by deleting a claim and pretending the first attempt never
#      existed."
#
# SO RECOVERY IS ADDITIVE. Nothing is deleted and nothing is rewritten: attempt 1's claim keeps its
# name and its bytes, its partial output is MOVED INTO EVIDENCE rather than overwritten, its logs
# are copied beside it, its charged expenditure is read from the meter and recorded, and a NEW
# attempt identity is created alongside. `authorized_attempt` counts forwards; there is no path in
# this module that unlinks a claim.
#
# WHY THE UNCERTAIN CASE IS THE HARD ONE, and it is the reason `confirm_attempt_terminal` refuses
# three different ways rather than one. A can't-look must not read as terminal: `sacct` prints a
# HEADER and ZERO ROWS with rc=1 when slurmdbd is down, so "no rows for this job" is exactly what a
# dead accounting database and a finished job look like alike. Zero rows REFUSE. An unresolvable
# state REFUSES. `COMPLETING` REFUSES. Only a job that is PRESENT in the dump, has no state in
# which it could still write, no state this module does not recognise, and at least one terminal
# state, is terminal.


def confirm_attempt_terminal(raw_text, job_id):
    """REQUIREMENT 1. The previous attempt is finished AND cannot still write -- or this refuses.

    `raw_text` is an `sacct` dump in `r5_meter.SACCT_FIELDS` order, the same operand
    `z_precursor_admission` takes, so ONE captured dump answers both this question and the
    admission recheck rather than two queries that could disagree about the instant they describe.

    FOUR REFUSALS, and they are four because they call for four different actions:

      * ZERO ROWS for this job id. `sacct` emits a header and no rows with rc=1 when slurmdbd is
        unreachable, and it emits no rows with rc=0 for a job id that never existed or has been
        purged. Neither is evidence of termination. This is the can't-look, and reading it as
        terminal is the failure shape this campaign has paid for repeatedly.
      * A STATE IN WHICH IT COULD STILL WRITE (`ATTEMPT_MAY_STILL_WRITE_STATES`), which includes
        `COMPLETING` -- a job in `COMPLETING` still holds its allocation and its file descriptors.
      * A STATE THIS MODULE DOES NOT RECOGNISE. Fail closed: an unclassified state is an unresolved
        state, and Slurm grows states faster than this list does.
      * NO TERMINAL STATE AT ALL, which is the all-`REQUEUED` history: every attempt ended and the
        task is still going.
    """
    import r5_meter
    import z_precursor_admission as admission

    want = str(job_id)
    rows, unresolved, live, terminal = [], [], [], []
    for line in raw_text.splitlines():
        fields = line.split("|")
        if len(fields) == len(r5_meter.SACCT_FIELDS) + 1 and fields[-1] == "":
            fields = fields[:-1]
        if len(fields) != len(r5_meter.SACCT_FIELDS):
            continue
        if admission._row_task_id(fields[0]) != want:
            continue
        state = (fields[2].split() or [""])[0].upper()
        rows.append({"job_id": fields[0], "job_name": fields[1], "state": fields[2],
                     "elapsed_raw": fields[3], "start": fields[5], "end": fields[6]})
        if state in ATTEMPT_MAY_STILL_WRITE_STATES:
            live.append(fields[2])
        elif state in admission.TERMINAL_STATES and state not in ATTEMPT_MAY_STILL_WRITE_STATES:
            terminal.append(fields[2])
        elif state in ATTEMPT_HISTORICAL_STATES:
            pass
        else:
            unresolved.append(fields[2])
    require(rows,
            f"the accounting dump contains NO rows for job {want}. That is a CANNOT-LOOK, not a "
            f"finished job: `sacct` prints a header and zero rows with rc=1 when slurmdbd is "
            f"unreachable, and zero rows with rc=0 for an id that never existed or has been "
            f"purged. Recovery may not assume termination from an absence -- capture a dump that "
            f"contains this job, and check the exit status of the command that captured it.")
    require(not unresolved,
            f"job {want} carries {len(unresolved)} state(s) this module does not classify: "
            f"{sorted(set(unresolved))}. Refusing rather than guessing: an unrecognised state is "
            f"an UNRESOLVED state, and the only safe reading of 'I do not know whether it can "
            f"still write' is that it can.")
    require(not live,
            f"job {want} is NOT terminal: {len(live)} row(s) in {sorted(set(live))}. It may still "
            f"be writing, so a new attempt would be a second concurrent writer to one product. "
            f"Note `COMPLETING` counts as live here -- a completing job still holds its allocation "
            f"and its open file descriptors -- and `SPECIAL_EXIT` counts as live because a held "
            f"requeue can be released, which is a deliberate divergence from "
            f"`z_precursor_admission.TERMINAL_STATES`, whose question is about ACCOUNTING.")
    require(terminal,
            f"job {want} has {len(rows)} row(s) and NONE of them is terminal "
            f"({sorted({r['state'] for r in rows})}). An all-REQUEUED history is a task that is "
            f"still going, not one that has finished.")
    return {"job_id": want, "n_rows": len(rows), "terminal_states": sorted(set(terminal)),
            "historical_rows": len(rows) - len(terminal), "rows": rows}


RECOVERY_SCHEMA_VERSION = "z-campaign-recovery/1"

#: ⚠ SCANNED PER `#SBATCH` LINE, NOT ANCHORED PER MATCH, AND THE FIRST VERSION WAS WRONG. All four
#: launchers put BOTH flags on ONE line -- `#SBATCH --output=... --error=...` -- and a pattern
#: anchored at `^#SBATCH` finds only the first of them, because `finditer` resumes after the match
#: and the anchor cannot match again mid-line. It reported "no #SBATCH --error" on a launcher that
#: declares one, which is a right-looking check over the wrong operand.
_SBATCH_LINE_RE = re.compile(r"^#SBATCH\s", re.MULTILINE)
_LOG_FLAG_RE = re.compile(r"--(?P<flag>output|error)=(?P<value>\S+)")


def _load_recovery_record(path):
    """Read and shape-check one recovery record. Refused rather than migrated, like the manifest."""
    p = Path(path)
    require(p.is_file(), f"recovery record {path} does not exist")
    try:
        record = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PrecursorError(f"recovery record {path} is not readable JSON: {exc}") from exc
    require(isinstance(record, dict)
            and record.get("schema_version") == RECOVERY_SCHEMA_VERSION,
            f"recovery record {path} has schema_version "
            f"{record.get('schema_version') if isinstance(record, dict) else None!r} != "
            f"{RECOVERY_SCHEMA_VERSION}; refused rather than migrated")
    for field in ("campaign_digest", "arm", "task_id", "attempt", "previous_attempt",
                  "previous_job_id", "terminal_evidence", "preserved", "admission",
                  "authorization"):
        require(field in record, f"recovery record {path} carries no {field!r}")
    return record


def launcher_log_patterns(launcher_path):
    """`{"output": pattern, "error": pattern}` from the launcher's OWN `#SBATCH` lines.

    DERIVED, like every other declaration in this module. A retyped log pattern is a second
    implementation of where a launcher puts its logs, and the four arms genuinely differ -- the
    array arms use `%a_%A` and the combine, which declares no array, uses `%j`. Reading the wrong
    one gives a well-formed answer about the wrong file.
    """
    found = {}
    for line in Path(launcher_path).read_text().splitlines():
        if not _SBATCH_LINE_RE.match(line):
            continue
        for match in _LOG_FLAG_RE.finditer(line):
            found.setdefault(match.group("flag"), match.group("value"))
    for flag in ("output", "error"):
        require(flag in found,
                f"{launcher_path}: no #SBATCH --{flag}. Recovery must PRESERVE the failed "
                f"attempt's logs, and it cannot name a file the launcher does not declare.")
    return found


def resolve_log_names(launcher_path, *, array_job_id, task_id, job_id, job_name):
    """Slurm's filename patterns, expanded. Only the four this repository's launchers use.

    `%%` first, so an escaped percent cannot be re-expanded by a later substitution -- the classic
    ordering bug in any substitution table. An UNRECOGNISED `%` token REFUSES rather than being
    left in the name: a literal `%x` in a filename is a file nobody will find.
    """
    out = {}
    for flag, pattern in launcher_log_patterns(launcher_path).items():
        pieces, index = [], 0
        while index < len(pattern):
            char = pattern[index]
            if char != "%":
                pieces.append(char)
                index += 1
                continue
            require(index + 1 < len(pattern), f"{pattern!r} ends in a bare '%'")
            token = pattern[index + 1]
            mapping = {"%": "%", "A": str(array_job_id), "a": str(task_id), "j": str(job_id),
                       "x": str(job_name)}
            require(token in mapping,
                    f"{pattern!r} uses the Slurm filename token %{token}, which this expansion "
                    f"does not know. Refusing rather than leaving it literal: a log path with an "
                    f"unexpanded token names a file nobody will find, and recovery would then "
                    f"report a preserved log that is not the attempt's.")
            pieces.append(mapping[token])
            index += 2
        out[flag] = "".join(pieces)
    return out


def verify_task_ownership(*, arm, plan, product, bank, estimator_seed, draw_seed, environ=None):
    """PHASE 2. Campaign membership, then exclusive ownership of THIS task's output.

    The clauses run in an order chosen so each is REACHABLE by a fault aimed at it -- a guard that
    another guard refuses first, with the same exit status, is untested rather than proven:

      1. the manifest exists, is unedited, and belongs to this namespace
      2. this arm is one the campaign covers, at the directory it was bound to
      3. the code revision is the bound one
      4. the inputs are the bound ones
      5. the seeds are the bound ones
      6. this task id is declared, and the product it is writing is the basename it owns
      7. NOTHING FOREIGN: every product present in the arm directory is claimed by this campaign
      8. PHASE 3, for a CONSUMING arm only: every arm in `CONSUMED_ARMS[arm]` is complete
      9. NOTHING OVERWRITTEN: this task's own product does not already exist
     10. NOTHING DUPLICATED: the `O_EXCL` claim

    7 before 9 because a product at this task's own declared name with NO claim is FOREIGN, and
    calling it an overwrite would send the reader after the wrong thing. 9 before 10 because (claim
    present, product present) means this task already ran to completion while (claim present,
    product absent) means an attempt died before publishing; those call for different actions and
    are reported as different findings rather than one message that half-fits both. 8 before 10 for
    the reason recorded at `CONSUMED_ARMS`: a consumption refusal taken AFTER the create would burn
    the consuming task's own claim on the ordinary case.
    ⚠ THIS LIST IS TEN ITEMS AND THE FIRST COMMIT BODY OF THIS REPAIR SAID NINE. Step 8 moved here
    from `do_combine` during the same review and the list was not renumbered with it. Corrected
    rather than left, because an ordered list that silently omits a step is the shape where a
    reviewer checks every item and still misses one.

    SIBLINGS ARE PERMITTED, which is the clause the old predicate got wrong: a product whose
    basename this campaign declares AND whose task holds a claim is a correctly bound sibling, and
    clause 7 passes it silently however many of them there are.
    """
    environ = os.environ if environ is None else environ
    paths = campaign_paths(plan["data_root"], plan["namespace"])
    campaign = load_campaign(paths["manifest"])
    body = campaign["body"]
    require(body["namespace"] == plan["namespace"],
            f"the manifest found in namespace {plan['namespace']!r} declares namespace "
            f"{body['namespace']!r}; a campaign manifest moved between namespaces identifies the "
            f"wrong production")
    require(arm in body["arms"],
            f"arm {arm!r} is not covered by this campaign, which declares {sorted(body['arms'])}. "
            f"Running it would write into a campaign's namespace with no declared identity and no "
            f"ownership. Initialize a campaign that declares it.")
    entry = body["arms"][arm]
    require(os.path.normpath(body["arm_dirs"][arm]) == os.path.normpath(plan["arms"][arm]["dir"]),
            f"the campaign binds arm {arm!r} to {body['arm_dirs'][arm]}, but this run resolves "
            f"{plan['arms'][arm]['dir']}; the namespace layout moved under the campaign")
    code = verify_campaign_code(campaign, environ)
    require(bank not in (None, ""),
            f"arm {arm!r} consumes the bank, so --bank must be supplied for the campaign's input "
            f"binding to have an operand")
    inputs = verify_campaign_inputs(campaign, bank)
    seeds = body["seeds"]
    require(estimator_seed is not None and draw_seed is not None,
            f"arm {arm!r} runs the estimator, so --estimator-seed and --draw-seed are both present "
            f"on every authorized invocation and are both bound by the campaign")
    require(int(estimator_seed) == seeds["estimator_seed"],
            f"--estimator-seed {int(estimator_seed)}, but the campaign is bound to "
            f"{seeds['estimator_seed']} (group {seeds['estimator_group']}, baseline "
            f"{seeds['estimator_baseline']} + offset {seeds['member_offset']}). Throws, block "
            f"units and the CV must share ONE estimator seed, or ML variation leaks out of C_ML "
            f"and into C_syst.")
    require(int(draw_seed) == seeds["draw_seed"],
            f"--draw-seed {int(draw_seed)}, but the campaign is bound to {seeds['draw_seed']}. The "
            f"throw realization for global index j is --draw-seed + j, so a second draw seed in "
            f"one campaign is a second throw ensemble -- and the combine's own seed guard cannot "
            f"see it, because per-member coherence is not ensemble coherence.")
    task_id = resolve_task_id(campaign, arm, environ)
    expected_name = entry["outputs"][str(task_id)]
    require(product not in (None, ""),
            f"arm {arm!r} task {task_id} owns the output {expected_name!r}, and no output path was "
            f"supplied to compare against it")
    product_path = Path(product)
    require(product_path.name == expected_name,
            f"task {task_id} of arm {arm!r} owns {expected_name!r}, but this invocation writes "
            f"{product_path.name!r}. The task and the file it is writing disagree, so whichever is "
            f"right the other names a product nobody declared -- and a task writing a SIBLING's "
            f"basename would destroy that sibling's output.")
    product_dir = (str(product_path.parent.resolve()) if product_path.is_absolute()
                   else os.path.normpath(str(product_path.parent)))
    require(os.path.normpath(product_dir) == os.path.normpath(plan["arms"][arm]["dir"]),
            f"task {task_id} of arm {arm!r} would write into {product_dir}, which is not the "
            f"campaign's arm directory {plan['arms'][arm]['dir']}")

    # WHICH ATTEMPT AM I, AND WAS IT AUTHORIZED. Attempt 1 needs nothing; every later attempt exists
    # only because a recovery record authorizes it, and each of those records is re-validated
    # against THIS campaign here rather than trusted for existing -- requirement 3's "linked to the
    # same logical task and immutable campaign inputs" is a binding that has to be CHECKED at the
    # point of use, or a recovered attempt could drift onto a different manifest.
    attempt = authorized_attempt(paths, arm, task_id)
    recoveries = task_recoveries(paths, arm, task_id)
    for number, filename in sorted(recoveries.items()):
        record = _load_recovery_record(os.path.join(paths["recovery"], filename))
        require(record["campaign_digest"] == campaign["campaign_digest"],
                f"the recovery record authorizing attempt {number} of {arm} task {task_id} binds "
                f"campaign {str(record['campaign_digest'])[:12]!r}, not this one "
                f"{campaign['campaign_digest'][:12]!r}. A recovered attempt inherits the campaign "
                f"binding; it does not get to re-derive one.")
        require(record["arm"] == arm and int(record["task_id"]) == int(task_id)
                and int(record["attempt"]) == number,
                f"the recovery record {filename} authorizes {record['arm']!r} task "
                f"{record['task_id']} attempt {record['attempt']}, which is not {arm!r} task "
                f"{task_id} attempt {number}")

    import unified_throw_cov as producer

    declared = {str(t): n for t, n in entry["outputs"].items()}
    declared_names = set(declared.values())
    claimed = claimed_task_ids(paths["claims"], arm)
    stray = sorted(t for t in claimed if str(t) not in declared)
    require(not stray,
            f"the campaign holds claims for UNDECLARED tasks of arm {arm!r}: {stray}. A claim "
            f"outside the declared population means something ran under this campaign's name that "
            f"the campaign never expected.")
    claimed_names = {declared[str(t)] for t in claimed}
    present = sorted(p for p in globmod.glob(plan["arms"][arm]["product_glob"])
                     if not producer.is_incomplete_write(p))
    present_names = {os.path.basename(p) for p in present}
    undeclared = sorted(present_names - declared_names)
    require(not undeclared,
            f"arm {arm!r} of namespace {plan['namespace']!r} holds {len(undeclared)} product(s) "
            f"this campaign never declared: {undeclared[:8]}"
            f"{' ...' if len(undeclared) > 8 else ''}. That is a FOREIGN or STALE product: every "
            f"content check this producer makes is satisfied by any inventory-complete population "
            f"at the matching seed, so a foreign member combines silently.")
    unclaimed = sorted(present_names - claimed_names)
    require(not unclaimed,
            f"arm {arm!r} of namespace {plan['namespace']!r} holds {len(unclaimed)} product(s) "
            f"whose basename this campaign DECLARES but which no task of this campaign has "
            f"CLAIMED: {unclaimed[:8]}{' ...' if len(unclaimed) > 8 else ''}. That is a valid "
            f"product of a DIFFERENT campaign sitting at a name this one owns -- the exact shape "
            f"of `uq_5d/z_probe_20260912/block_slabs_5d/block5d_knobs.npz` -- and a basename check "
            f"alone passes it, which is why ownership is by CLAIM and not by name.")
    # PHASE 3, FOR A CONSUMING ARM, AND BEFORE THE CLAIM. See `CONSUMED_ARMS` for why the order is
    # load-bearing: refusing a combine submitted while the arrays are still draining is the
    # ORDINARY case, and a refusal taken after the `O_EXCL` create would leave that task holding a
    # claim for a run that never happened.
    consumed = {}
    for role in CONSUMED_ARMS.get(arm, ()):
        consumed[role] = require_campaign_complete(
            campaign, role,
            os.path.join(body["arm_dirs"][role], body["arms"][role]["product_glob"]))
    require(not product_path.exists(),
            f"attempt {attempt} of task {task_id} of arm {arm!r} would write {product_path}, which "
            f"ALREADY EXISTS and is claimed by this campaign. Adopting or overwriting a "
            f"pre-existing output is not authorized: at attempt 1 this means the task already ran, "
            f"and at a later attempt it means the PREVIOUS attempt's partial output is still "
            f"sitting there -- `campaign-recover` moves it into `_campaign/evidence/` before it "
            f"authorizes anything, so a product still in place says the preservation step did not "
            f"happen and the evidence would be destroyed by this write.")
    claim_path = os.path.join(paths["claims"], claim_name(arm, task_id, attempt))
    try:
        _write_json_exclusive(claim_path, {
            "schema_version": CAMPAIGN_SCHEMA_VERSION,
            "campaign_digest": campaign["campaign_digest"],
            "arm": arm,
            "task_id": int(task_id),
            "attempt": int(attempt),
            "authorized_by": (None if attempt == FIRST_ATTEMPT
                              else recovery_name(arm, task_id, attempt)),
            "output": expected_name,
            "product": str(product_path),
            "claimed_at_utc": _utc_now(),
            "slurm": {key: environ.get(key, "") for key in
                      ("SLURM_JOB_ID", "SLURM_ARRAY_JOB_ID", "SLURM_ARRAY_TASK_ID",
                       "SLURM_JOB_NAME", "SLURM_NODELIST", "SLURM_RESTART_COUNT")},
            "code_listing_sha256": code["listing_sha256"],
            "inputs_listing_sha256": inputs["listing_sha256"],
        })
    except PrecursorError as exc:
        raise PrecursorError(
            f"DUPLICATE EXECUTION: attempt {attempt} of task {task_id} of arm {arm!r} is ALREADY "
            f"CLAIMED in campaign {campaign['campaign_digest'][:12]} ({exc}). Another process "
            f"holds this attempt's exclusive claim and no product has been published, so it is "
            f"either still running or it died before publishing. The claim is created with "
            f"O_CREAT|O_EXCL, so exactly one of two concurrent attempts can hold it. A LATER "
            f"attempt is not what this refuses -- that is what `z_precursor.py campaign-recover` "
            f"authorizes, per task, against Joseph's explicit approval -- what it refuses is a "
            f"SECOND process running the attempt this one is already running.") from exc
    # `arm` is IN the return so this result is self-sufficient: `record_task_completion` takes only
    # a contract, and a caller that had to remember to add the arm afterwards would be a contract
    # completed by convention.
    return {"campaign": campaign,
            "arm": arm,
            "task_id": int(task_id),
            "attempt": int(attempt),
            "output": expected_name,
            "claim": claim_path,
            "receipt": os.path.join(paths["receipts"], receipt_name(arm, task_id, attempt)),
            "campaign_paths": paths,
            "code": code,
            "inputs": inputs,
            "consumed": consumed,
            "n_sibling_products": len(present),
            "n_sibling_claims": len(claimed)}


def record_task_completion(contract, *, product):
    """Close this task's claim with a completion record, written STRICTLY AFTER the product.

    `write_receipt` is the mechanism, unchanged: it refuses unless the product exists, is non-empty
    and OPENS, so the record is an observation rather than a declaration made in parallel with the
    thing it describes. What is added is the campaign binding -- the digest, the arm and the task
    id -- which is what phase 3 reads. There is no `try`/`finally` and no `os._exit` on this path,
    for the reason stated at `write_receipt`: a record emitted from a bypassed handler would assert
    a completion that did not happen.

    `bank_cv_sha256` comes from the CAMPAIGN rather than from `producer_provenance(bank=...)`,
    which would re-digest a 2 939 596 884-byte `cv.npz` in each of 61 tasks to re-derive a value
    the manifest already binds.
    """
    require(contract is not None and contract.get("campaign") is not None,
            "record_task_completion: this run has no campaign contract, so there is no claim to "
            "close and no campaign to bind the product to")
    import unified_throw_cov as producer

    campaign = contract["campaign"]
    arm, task_id = contract["arm"], contract["task_id"]
    extra = dict(producer.code_provenance())
    extra.update({
        "campaign_digest": campaign["campaign_digest"],
        "campaign_schema_version": CAMPAIGN_SCHEMA_VERSION,
        "arm": arm,
        "task_id": int(task_id),
        "attempt": int(contract.get("attempt", FIRST_ATTEMPT)),
        "output": os.path.basename(product),
        "claim": os.path.basename(contract["claim"]),
        "bank_cv_sha256": campaign["body"]["inputs"]["bank_cv_sha256"],
        "bank_listing_sha256": campaign["body"]["inputs"]["listing_sha256"],
        "code_listing_sha256": campaign["body"]["code"]["listing_sha256"],
    })
    return write_receipt(product=product, out_path=contract["receipt"], arm=arm,
                         namespace=campaign["body"]["namespace"], plan_json=contract.get("plan"),
                         extra=extra, code_root=os.environ.get("MNV_CODE_ROOT"))


# ------------------------------------------------- PHASE 3: the completed population, bound ----
def check_task_completion(campaign, arm, task_id, receipts_dir, attempt=FIRST_ATTEMPT):
    """One ATTEMPT's completion record, gated against the product on disk AND against the campaign."""
    path = os.path.join(receipts_dir, receipt_name(arm, task_id, attempt))
    # `require_population=False`: the two population flags are a COMBINE-level declaration about
    # slab globs, and a per-task receipt has no population to declare. THE PROVENANCE FIELDS ARE
    # RE-CHECKED BELOW, because `check_receipt` gates them inside the same branch as the flags --
    # so turning the flag off silently drops them too, which is a relaxation wider than it reads.
    base = check_receipt(path, require_population=False)
    receipt = json.loads(Path(path).read_text(encoding="utf-8"))
    extra = receipt.get("extra") or {}
    require(extra.get("campaign_digest") == campaign["campaign_digest"],
            f"the completion record {path} binds campaign "
            f"{str(extra.get('campaign_digest'))[:12]!r}, not this one "
            f"{campaign['campaign_digest'][:12]!r}. A product completed under another campaign is "
            f"a foreign artifact however correct its own record is.")
    require(extra.get("arm") == arm and int(extra.get("task_id", -1)) == int(task_id),
            f"the completion record {path} claims arm {extra.get('arm')!r} task "
            f"{extra.get('task_id')!r}, not {arm!r} task {task_id}")
    expected = campaign["body"]["arms"][arm]["outputs"][str(task_id)]
    require(os.path.basename(receipt["product"]["path"]) == expected,
            f"the completion record for {arm} task {task_id} names product "
            f"{os.path.basename(receipt['product']['path'])!r}, but the campaign says that task "
            f"owns {expected!r}")
    require(int(extra.get("attempt", FIRST_ATTEMPT)) == int(attempt),
            f"the completion record {path} records attempt {extra.get('attempt')!r}, not "
            f"{attempt}; an attempt's record must name the attempt that wrote it or the "
            f"one-completion-per-logical-task count is over the wrong population")
    for field in REQUIRED_PROVENANCE:
        value = extra.get(field)
        require(value not in (None, "", "UNAVAILABLE"),
                f"completion record {path}: extra.{field} = {value!r}. UNAVAILABLE is stamped "
                f"deliberately by the producer so that a gate can see it.")
    return {"receipt": path, "attempt": int(attempt), "product": base["product"],
            "sha256": base["sha256"]}


def _completion_is_current(campaign, arm, task_id, receipts_dir, attempt):
    """Does this attempt's record still describe the product on disk? `None` = cannot tell.

    THREE-VALUED ON PURPOSE. `True` and `False` are the two answers `require_campaign_complete`
    classifies on -- a stale record is expected for a SUPERSEDED attempt and is a corruption
    finding for any other. `None` is the case that must NOT be classified here: an absent,
    unreadable or shapeless record is a defect `check_receipt` already knows how to describe, and
    guessing at it would be this function inventing a diagnosis it has no evidence for.

    ONLY THE DIGEST QUESTION LIVES HERE. Campaign binding, arm, task, attempt, product name and
    provenance are NOT consulted: they are never supersedable, and folding them in is exactly the
    over-broad classification this function was written to replace.
    """
    path = Path(receipts_dir) / receipt_name(arm, task_id, attempt)
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
        recorded = receipt["product"]["sha256"]
        product = receipt["product"]["path"]
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError):
        return None
    if not isinstance(recorded, str) or not isinstance(product, str):
        return None
    if not os.path.exists(product):
        return False
    return sha256_file(product) == recorded


def campaign_arm_status(campaign, arm):
    """Per-task state of one arm: claimed, published, recorded. A VIEW, never a gate.

    Separate from `require_campaign_complete` on purpose: a GATE must not be satisfiable by a
    summary, and a summary must not be mistaken for a gate. This is the view, that is the gate, and
    neither is the other's evidence.
    ⚠ IT IS NOT EXCEPTION-FREE, and saying so would be the over-claim. It raises on an arm the
    campaign does not cover, and it propagates `claimed_task_ids`'s could-not-look refusal on an
    unreadable claims directory -- because an operator shown "0 of 21 claimed" when nobody could
    read the directory is being shown a blind zero as a measurement.
    """
    body = campaign["body"]
    require(arm in body["arms"], f"arm {arm!r} is not covered by this campaign")
    entry = body["arms"][arm]
    paths = campaign_paths(body["data_root"], body["namespace"])
    claimed = claimed_task_ids(paths["claims"], arm)
    rows = []
    for task in sorted(int(t) for t in entry["task_ids"]):
        name = entry["outputs"][str(task)]
        attempts = sorted(task_claims(paths, arm, task))
        rows.append({"task_id": task, "output": name,
                     "claimed": task in claimed,
                     "attempts": attempts,
                     "recovered_attempts": sorted(task_recoveries(paths, arm, task)),
                     "published": os.path.exists(os.path.join(body["arm_dirs"][arm], name)),
                     "recorded": bool(task_receipts(paths, arm, task))})
    return {"arm": arm, "campaign_digest": campaign["campaign_digest"], "n_tasks": len(rows),
            "tasks": rows,
            "n_complete": sum(1 for r in rows if r["claimed"] and r["published"] and r["recorded"])}


def require_campaign_complete(campaign, arm, pattern):
    """PHASE 3. The EXACT completed population and its bindings, before anything consumes it.

    THREE THINGS, AND NONE SUBSUMES ANOTHER -- the same neither-subsumes discipline
    `check_slab_population` and `check_namespace_fresh` already divide between them:

      * FILE IDENTITY, both directions, by `unified_throw_cov.check_slab_population`: a declared
        member the glob did not find, and a member the glob found that was never declared.
      * COMPLETION, per task: a claim AND a completion record. A population whose files are all
        present but one of which was never recorded as finished is a DIFFERENT state from a missing
        file, and the incremental `_atomic_savez` in `do_blockunits` makes it reachable -- a killed
        task leaves a SHORT but perfectly loadable slab at the declared name.
      * BINDING, per record: the product digest re-read from disk, and the campaign digest, arm and
        task id checked against this campaign.

    Refuses ONCE with the whole incomplete set rather than at the first gap, so the operator sees
    the population and not a sample of it.

    ⚠ ATTEMPT-AWARE WITHOUT BEING ATTEMPT-AGNOSTIC (2026-09-13, requirement 5). A recovered task has
    N attempts and must contribute EXACTLY ONE consumed completion. Two ways to get that wrong, and
    this avoids both:
      * ATTEMPT-BLIND would look only for `<arm>.task-<id>.receipt.json`, so a task completed by
        attempt 2 would read as "never recorded a completion" and the combine would refuse a
        finished campaign forever.
      * ATTEMPT-AGNOSTIC would accept any receipt it found, so two records for one logical task
        would both count and a superseded attempt could supply the binding for a product it did
        not write.
    So: every attempt's record is gated, EXACTLY ONE must still validate against the product on
    disk, and every record that does NOT validate must be SUPERSEDED -- attempt k's record is
    allowed to be stale only if a recovery record authorized attempt k+1. A record that silently
    stopped matching with nothing superseding it is a finding, not a spare.
    """
    body = campaign["body"]
    require(arm in body["arms"],
            f"arm {arm!r} is not covered by campaign {campaign['campaign_digest'][:12]}")
    entry = body["arms"][arm]
    tasks = sorted(int(t) for t in entry["task_ids"])
    expected = [entry["outputs"][str(t)] for t in tasks]

    import unified_throw_cov as producer

    population = producer.check_slab_population(
        pattern, expected, f"campaign {campaign['campaign_digest'][:12]} arm {arm!r} population")
    paths = campaign_paths(body["data_root"], body["namespace"])
    claimed = claimed_task_ids(paths["claims"], arm)
    unclaimed = [t for t in tasks if t not in claimed]
    unrecorded = [t for t in tasks if not task_receipts(paths, arm, t)]
    require(not unclaimed and not unrecorded,
            f"campaign {campaign['campaign_digest'][:12]} arm {arm!r} is INCOMPLETE: "
            f"{len(unclaimed)} of {len(tasks)} task(s) never claimed their output "
            f"{unclaimed[:12]}{' ...' if len(unclaimed) > 12 else ''}; {len(unrecorded)} never "
            f"recorded a completion {unrecorded[:12]}{' ...' if len(unrecorded) > 12 else ''}. "
            f"The glob population can be exactly right while a task is still running or died "
            f"mid-write: `_atomic_savez` is called after every unit, so a killed task leaves a "
            f"SHORT slab at the declared name that loads cleanly. Consumption needs the COMPLETED "
            f"population, not the present one.")
    bindings, attempt_rows = [], []
    for task in tasks:
        recovered = set(task_recoveries(paths, arm, task))
        validating, superseded, stale = [], [], []
        for number in sorted(task_receipts(paths, arm, task)):
            # ⚠ CURRENCY IS DECIDED FIRST, AND THE FULL GATE IS ONLY CALLED ON A CURRENT RECORD.
            # My first version wrapped `check_task_completion` in `except PrecursorError` and
            # relabelled EVERY refusal as "stale" -- so a record bound to ANOTHER CAMPAIGN, or one
            # naming the wrong arm, or one carrying UNAVAILABLE provenance, was reported as a
            # superseded attempt. That is one message half-fitting four findings, and it silently
            # WEAKENED a guard that existed before recovery did: the foreign-campaign arm of
            # `test_z_campaign_ownership` caught it. Only the DIGEST question is supersedable;
            # every other defect must still speak for itself.
            current = _completion_is_current(campaign, arm, task, paths["receipts"], number)
            if current is False:
                (superseded if (number + 1) in recovered else stale).append(number)
                continue
            # `None` means the record could not be read well enough to answer -- pass it to the
            # gate, which is the thing that knows how to refuse an unreadable record.
            bound = check_task_completion(campaign, arm, task, paths["receipts"], number)
            validating.append((number, bound))
        require(not stale,
                f"campaign {campaign['campaign_digest'][:12]} arm {arm!r} task {task}: "
                f"attempt(s) {stale} recorded a completion that NO LONGER validates against the "
                f"product on disk, and no recovery record supersedes them. A superseded attempt's "
                f"record is allowed to go stale -- that is what recovery does -- but a record that "
                f"stopped matching on its own is a changed or replaced product, which is a "
                f"corruption finding and not a spare completion.")
        require(len(validating) == 1,
                f"campaign {campaign['campaign_digest'][:12]} arm {arm!r} task {task} contributes "
                f"{len(validating)} validated completion(s) "
                f"{[n for n, _b in validating]} across attempts "
                f"{sorted(task_receipts(paths, arm, task))}; the combine consumes EXACTLY ONE per "
                f"logical task. Zero means nothing finished; more than one means two attempts both "
                f"claim to have produced the single product at this task's declared name.")
        number, bound = validating[0]
        bindings.append(bound)
        attempt_rows.append({"task_id": task, "consumed_attempt": number,
                             "superseded_attempts": superseded,
                             "recovered_attempts": sorted(recovered)})
    return {"arm": arm, "campaign_digest": campaign["campaign_digest"], "n_tasks": len(tasks),
            "population": population, "bindings": bindings, "attempts": attempt_rows,
            "n_recovered_tasks": sum(1 for r in attempt_rows if r["recovered_attempts"])}


def check_recovery_authorization(path, *, campaign_digest, arm, task_id, attempt):
    """Joseph's approval for THIS retry, named and digested. It is a GATE, not a verification.

    ⚠ WHAT THIS CAN AND CANNOT ESTABLISH, said plainly because the difference matters. It can
    establish that a named artifact exists, that it is bound to THIS campaign digest, and that it
    names THIS arm, task and attempt -- so one approval cannot be recycled across 61 tasks, across
    two campaigns, or across two attempts of one task. It CANNOT establish that Joseph wrote it.
    There is no channel here that could: the record ATTESTS an approval and carries its digest so a
    later reader can check what was shown, and that is the whole of the claim.

    The required line is machine-checkable and short, so an approval cannot be satisfied by prose
    that happens to mention the words:

        z-campaign-recover <campaign digest> <arm> task <id> attempt <n>
    """
    p = Path(path)
    require(p.is_file(),
            f"--authorization {path!r} is not a file. Joseph: *\"Each retry still requires my "
            f"explicit approval.\"* There is no default and no implicit approval.")
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise PrecursorError(f"--authorization {path} is not readable text: {exc}") from exc
    wanted = (f"z-campaign-recover {campaign_digest} {arm} task {int(task_id)} "
              f"attempt {int(attempt)}")
    matched = [line.strip() for line in text.splitlines() if line.strip() == wanted]
    require(matched,
            f"--authorization {path} does not authorize THIS retry. It must contain, on a line of "
            f"its own:\n    {wanted}\nAn approval that does not name the campaign digest, the arm, "
            f"the task and the attempt is an approval that can be recycled -- across the other 60 "
            f"tasks of this arm, across a second attempt of this one, or across another campaign "
            f"entirely.")
    return {"path": str(p.resolve()), "sha256": sha256_file(str(p)), "line": wanted,
            "bytes": p.stat().st_size,
            "attests_only": ("this gate establishes that a named artifact exists and names this "
                             "exact retry; it cannot establish who wrote it")}


def recover_task(*, data_root, namespace, arm, task_id, previous_job_id, sacct_dump,
                 spend_basis, max_retries, now, authorization, log_dir, code_root,
                 admitted_launchers=(), environ=None):
    """Authorize ONE further attempt of ONE logical task. ADDITIVE: nothing is deleted.

    THE SIX REQUIREMENTS, in the order they are discharged, and every CHECK precedes every
    MUTATION for the reason `initialize_campaign` records: a failure after the first `mkdir` leaves
    a state that is neither recovered nor recoverable.

      (1) the previous attempt is terminal and cannot still write  -> `confirm_attempt_terminal`
      (6) charged expenditure and admitted exposure are re-checked -> `z_precursor_admission`
          (before any mutation, so a refused admission changes nothing)
      (2) the claim, the logs, the partial output and the charged expenditure are PRESERVED
      (3) a new attempt identity, inheriting the campaign binding rather than re-deriving it
      (4) concurrency and completed products are protected -- here by refusing to recover a task
          that has ANY completion record, and at run time by the `O_EXCL` claim per attempt
      (5) is not here: it is `require_campaign_complete`, which consumes exactly one per task.

    NOTHING IS SUBMITTED. Joseph: *"This authorizes implementation and tests, not any actual
    retry."* This writes a record that would PERMIT one attempt; the submission is a separate,
    human act, and this module contains no `sbatch`.
    """
    environ = os.environ if environ is None else environ
    import z_precursor_admission as admission

    paths = campaign_paths(data_root, namespace)
    campaign = load_campaign(paths["manifest"])
    body = campaign["body"]
    require(arm in body["arms"],
            f"arm {arm!r} is not covered by campaign {campaign['campaign_digest'][:12]}, which "
            f"declares {sorted(body['arms'])}")
    entry = body["arms"][arm]
    require(str(int(task_id)) in entry["outputs"],
            f"task {task_id} is not a declared task of arm {arm!r}")
    output_name = entry["outputs"][str(int(task_id))]
    product = os.path.join(body["arm_dirs"][arm], output_name)

    # (4a) A TASK THAT RECORDED A COMPLETION IS NOT A CANDIDATE FOR RECOVERY, whatever the product
    # looks like now. If the record still validates the task is done; if it does not, the product
    # was changed or replaced after a real completion, and that is a corruption finding with its
    # own owner -- not a retry. Either way, retrying would overwrite a completed valid product or
    # bury the evidence of one.
    existing_receipts = task_receipts(paths, arm, task_id)
    require(not existing_receipts,
            f"{arm} task {task_id} already has completion record(s) for attempt(s) "
            f"{sorted(existing_receipts)}. A task that recorded a completion DID complete. If its "
            f"product no longer matches that record, that is a changed or replaced product and a "
            f"corruption finding, not a failed attempt -- route it, do not retry it.")

    previous = authorized_attempt(paths, arm, task_id)
    attempt = previous + 1
    claims = task_claims(paths, arm, task_id)
    require(previous in claims,
            f"{arm} task {task_id} attempt {previous} holds NO claim, so it never started. There "
            f"is nothing to recover: submit the campaign, do not recover it.")
    previous_claim = os.path.join(paths["claims"], claims[previous])
    try:
        claim_body = json.loads(Path(previous_claim).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PrecursorError(
            f"the previous attempt's claim {previous_claim} is not readable JSON ({exc}). It is "
            f"the record recovery exists to preserve; refusing rather than proceeding over it."
        ) from exc
    slurm = claim_body.get("slurm") or {}
    array_job = (slurm.get("SLURM_ARRAY_JOB_ID") or "").strip()
    plain_job = (slurm.get("SLURM_JOB_ID") or "").strip()
    recorded_ids = {i for i in (f"{array_job}_{int(task_id)}" if array_job else "",
                                array_job, plain_job) if i}
    require(recorded_ids,
            f"the claim for {arm} task {task_id} attempt {previous} recorded NO Slurm identity "
            f"({slurm!r}), so there is no job whose terminality could be established. Refusing: "
            f"an attempt that cannot be pointed at a job cannot be shown to have stopped.")
    require(str(previous_job_id) in recorded_ids,
            f"--previous-job-id {previous_job_id!r} is not one of the identities the claim for "
            f"attempt {previous} recorded ({sorted(recorded_ids)}). The terminality evidence must "
            f"be about the job that ACTUALLY RAN this attempt; a dump for some other job is a "
            f"well-formed check over the wrong object.")

    # (1) TERMINAL, AND UNABLE TO WRITE. Reads the dump; refuses on zero rows, on an unresolvable
    # state, on any state in which it could still be writing, and on an all-historical history.
    try:
        raw_text = Path(sacct_dump).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise PrecursorError(f"cannot read the accounting dump {sacct_dump}: {exc}") from exc
    terminal_evidence = confirm_attempt_terminal(raw_text, previous_job_id)

    # (6) EXPENDITURE AND EXPOSURE, RE-CHECKED, BEFORE ANYTHING IS MOVED. The proposed arm is this
    # ONE task at the arm's own wall ceiling -- `committed_task_hours` is `n_tasks * (1 + retries) *
    # ceiling`, so a single-task proposal is the same function over `n_tasks = 1`. The job NAME is
    # left as the arm's, because that is how the meter attributes the hours already charged.
    launcher = Path(code_root) / ARM_LAUNCHERS[arm]
    arm_declaration = parse_sbatch_arm(launcher)
    proposed = dict(arm_declaration, n_tasks=1, task_ids=[int(task_id)])
    # THE METER'S OWN EXCEPTION IS CONVERTED, NOT LET THROUGH. `r5_meter.MeterError` is a
    # `ValueError` and the CLI below catches `PrecursorError`; letting it escape would turn a real
    # refusal -- a malformed or unparseable dump -- into a traceback, which is the wrong diagnosis
    # of a right refusal, the shape `do_combine` already carries a note about.
    import r5_meter

    try:
        report = admission.admission_report(
            raw_text=raw_text,
            admitted=[parse_sbatch_arm(p) for p in admitted_launchers],
            proposed=[proposed], max_retries=max_retries, spend_basis=spend_basis, now=now)
    except r5_meter.MeterError as exc:
        raise PrecursorError(
            f"the accounting dump {sacct_dump} could not be metered ({exc}). That is a "
            f"CANNOT-LOOK on the expenditure half, and recovery may not proceed on an unpriced "
            f"retry any more than on an unproven termination.") from exc
    require(report["decision"] == "PERMITTED",
            f"admission REFUSED this retry: {report['decision']} -- bound "
            f"{report['bound_cpu_task_hours']:.4f} CPU task-h against ceiling "
            f"{report['ceilings']['cpu_task_hours']:.1f}. Recovery re-prices the whole campaign, "
            f"not just this task: a retry is new committed exposure and R5's ceiling is over the "
            f"total.")
    charged = admission.charged_task_hours_for(raw_text, previous_job_id)

    # AUTHORIZATION, still before any mutation.
    approval = check_recovery_authorization(
        authorization, campaign_digest=campaign["campaign_digest"], arm=arm, task_id=task_id,
        attempt=attempt)

    # THE LOGS THIS ATTEMPT WROTE, derived from the launcher's OWN #SBATCH patterns.
    log_names = resolve_log_names(launcher, array_job_id=array_job or plain_job, task_id=task_id,
                                  job_id=plain_job or array_job,
                                  job_name=arm_declaration["job_name"])
    sources = {flag: Path(log_dir) / os.path.basename(name) for flag, name in log_names.items()}
    missing = sorted(str(p) for p in sources.values() if not p.is_file())
    require(not missing,
            f"the failed attempt's log(s) are not in --log-dir {log_dir}: {missing}. The names are "
            f"DERIVED from {ARM_LAUNCHERS[arm]}'s own #SBATCH --output/--error "
            f"({sorted(log_names.values())}). Requirement 2 is that the logs are PRESERVED, and a "
            f"recovery that cannot show the attempt's log has not preserved it -- say where it is "
            f"rather than proceeding without it.")

    # ---- MUTATIONS BEGIN. Everything above can refuse without changing a byte. -----------------
    os.makedirs(paths["recovery"], exist_ok=True)
    os.makedirs(paths["evidence"], exist_ok=True)
    evidence_dir = Path(paths["evidence"]) / f"{arm}.task-{int(task_id)}.attempt-{previous}"
    try:
        os.makedirs(evidence_dir, exist_ok=False)
    except FileExistsError as exc:
        raise PrecursorError(
            f"the evidence directory {evidence_dir} already exists, so attempt {previous} has "
            f"already been preserved once. Refusing rather than adding to it: a second preservation "
            f"would either overwrite the first attempt's evidence or leave two partial answers "
            f"about one attempt.") from exc

    preserved = {"claim": {"path": previous_claim, "name": claims[previous],
                           "sha256": sha256_file(previous_claim),
                           "bytes": os.path.getsize(previous_claim),
                           "note": "PRESERVED IN PLACE. Not moved and not rewritten -- the claim "
                                   "is the record that the first attempt existed."},
                 "logs": {}, "partial_output": None,
                 "charged_expenditure": dict(charged,
                                             source="z_precursor_admission."
                                                    "charged_task_hours_for")}
    for flag, source in sources.items():
        target = evidence_dir / source.name
        target.write_bytes(source.read_bytes())
        preserved["logs"][flag] = {"source": str(source.resolve()), "preserved": str(target),
                                   "bytes": target.stat().st_size,
                                   "sha256": sha256_file(str(target))}
    if os.path.exists(product):
        # MOVED, NOT COPIED AND NOT DELETED. `os.rename` within one namespace is same-filesystem and
        # atomic, and moving is what makes the arm directory ready for the next attempt WITHOUT
        # destroying what the last one wrote -- a copy would leave the partial in place and the
        # next attempt's overwrite refusal would (correctly) refuse forever.
        before = {"bytes": os.path.getsize(product), "sha256": sha256_file(product)}
        target = evidence_dir / os.path.basename(product)
        os.replace(product, target)
        after = {"bytes": target.stat().st_size, "sha256": sha256_file(str(target))}
        require(before == after,
                f"the partial output changed while it was being preserved: {before} -> {after}. "
                f"That is a writer this recovery believed was terminal.")
        preserved["partial_output"] = {"from": product, "preserved": str(target), **after}

    record = {
        "schema_version": RECOVERY_SCHEMA_VERSION,
        "campaign_digest": campaign["campaign_digest"],
        "arm": arm,
        "task_id": int(task_id),
        "attempt": attempt,
        "previous_attempt": previous,
        "previous_job_id": str(previous_job_id),
        "output": output_name,
        "authorized_at_utc": _utc_now(),
        # (3) THE BINDING IS INHERITED, NOT RE-DERIVED. These three fields are copied out of the
        # manifest rather than re-measured, so a recovered attempt cannot drift onto a different
        # code revision or a different bank: `verify_task_ownership` re-checks the LIVE values
        # against the manifest, and the manifest is what this record points at.
        "inherited": {"code_listing_sha256": body["code"]["listing_sha256"],
                      "inputs_listing_sha256": body["inputs"]["listing_sha256"],
                      "bank_cv_sha256": body["inputs"]["bank_cv_sha256"],
                      "seeds": body["seeds"]},
        "terminal_evidence": terminal_evidence,
        "preserved": preserved,
        "admission": {"decision": report["decision"],
                      "bound_cpu_task_hours": report["bound_cpu_task_hours"],
                      "ceiling_cpu_task_hours": report["ceilings"]["cpu_task_hours"],
                      "spend_basis": report["spend_basis"],
                      "max_retries": int(max_retries)},
        "authorization": approval,
        "submits_nothing": ("this record authorizes ONE further attempt; it does not submit it. "
                            "Joseph, 2026-09-13: this authorizes implementation and tests, not "
                            "any actual retry."),
    }
    _write_json_exclusive(os.path.join(paths["recovery"], recovery_name(arm, task_id, attempt)),
                          record)
    return {"campaign": campaign, "record": record, "paths": paths,
            "evidence_dir": str(evidence_dir),
            "recovery_record": os.path.join(paths["recovery"],
                                            recovery_name(arm, task_id, attempt))}


# ----------------------------------------------------------------------------------- the CLI ----
def _build_parser():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan", help="print every arm's directory under the ONE namespace")
    plan.add_argument("--data-root", required=True)

    fresh = sub.add_parser("require-fresh", help="refuse unless every arm's namespace is empty")
    fresh.add_argument("--data-root", required=True)
    fresh.add_argument("--arm", action="append", default=None,
                       help="restrict the sweep (default: ALL arms)")

    sub.add_parser("require-no-member-axis",
                   help=f"refuse if {MEMBER_OFFSET_ENV} is set at all")

    decl = sub.add_parser("declare-files",
                          help="the exact product basenames an arm will write, from its #SBATCH")
    decl.add_argument("--arm", required=True, choices=("run", "block"))
    decl.add_argument("--launcher", required=True)

    arm = sub.add_parser("arm", help="one arm's declared population and wall ceiling")
    arm.add_argument("--launcher", required=True)

    # A SUBCOMMAND RATHER THAN AN INLINE `python3 -c` IN THE LAUNCHER. An inline `-c` would put the
    # launcher's own working directory at `sys.path[0]` and need its own path arithmetic to find
    # this module -- OI-136's shape, inside the repair for OI-136's shape.
    armdir = sub.add_parser("arm-dir", help="the one directory an arm writes into")
    armdir.add_argument("--data-root", required=True)
    armdir.add_argument("--arm", required=True, choices=tuple(ARM_LAYOUT))

    rec = sub.add_parser("receipt", help="write a run receipt AFTER the product")
    rec.add_argument("--product", required=True)
    rec.add_argument("--out", required=True)
    rec.add_argument("--arm", required=True)
    rec.add_argument("--namespace", required=True)
    rec.add_argument("--code-root", default=None)
    # PROVENANCE IS IMPORTED FROM THE PRODUCER, NOT RECOMPUTED HERE AND NOT ASSEMBLED IN SHELL.
    # The first version of the combine launcher built this JSON inline with two nested `python3 -c`
    # digest calls -- a shell reimplementation of `unified_throw_cov.code_provenance`, which is a
    # second implementation of the thing whose whole job is to be the single stamp.
    rec.add_argument("--bank", default=None,
                     help="bank directory, so the receipt can carry the producer's own "
                          "`_bank_cv_digest` value rather than a shell-computed one")
    rec.add_argument("--population-declared", default="",
                     help="comma-separated subset of {throw,block} whose file identities were "
                          "declared to the producer. Absent entries are recorded as 0, which "
                          "`check-receipt` refuses -- the flag has two reachable values.")
    rec.add_argument("--extra-json", default=None,
                     help="JSON object merged into extra{} for anything not covered above")
    rec.add_argument("--allow-overwrite", action="store_true")

    chk = sub.add_parser("check-receipt", help="gate a receipt against the product on disk")
    chk.add_argument("--receipt", required=True)
    chk.add_argument("--no-require-population", action="store_true")

    # ⚠ THESE THREE ARE OPERATOR COMMANDS, RUN BEFORE THE FIRST `sbatch` AND AFTER THE LAST ONE.
    # They are NOT added to any launcher, and that is ruling 21 again: `mnv_preflight_census.py`
    # pins UNCLASSIFIED interpreter invocations in the declared launchers at zero, and this module
    # still cannot be a declared preflight tool (criterion (5) requires its repository imports to be
    # a subset of {mnv_guarded_run}, and it imports `unified_throw_cov` by design). The task-side
    # half of the campaign needs no launcher line at all: the producer already receives
    # `--z-namespace-arm`, and the namespace, the arm, the task id (`SLURM_ARRAY_TASK_ID`) and the
    # output path are all things it already has.
    init = sub.add_parser("campaign-init",
                          help="PHASE 1: establish a fresh namespace atomically and bind it to one "
                               "immutable campaign manifest")
    init.add_argument("--data-root", required=True,
                      help="absolute data root; every path in the manifest is resolved against it")
    init.add_argument("--namespace", default=None,
                      help=f"the namespace segment; defaults to ${NAMESPACE_ENV}")
    init.add_argument("--code-root", required=True,
                      help="the approved clean execution tree the campaign binds")
    init.add_argument("--source-manifest", required=True,
                      help=f"the A-2(f) record written by `mnv_source_manifest.py --write` from "
                           f"--code-root; the SAME record the launchers pass as "
                           f"${SOURCE_MANIFEST_ENV}. It is compared against the live tree here.")
    init.add_argument("--bank", required=True,
                      help="the bank directory the block/run/combine arms consume, bound by digest")
    init.add_argument("--arm", action="append", default=None, dest="arms",
                      help="restrict the campaign's arms (default: every campaign-ownable arm)")
    init.add_argument("--label", default="", help="free text carried into the manifest")

    show = sub.add_parser("campaign-show", help="print a namespace's campaign manifest and digest")
    show.add_argument("--data-root", required=True)
    show.add_argument("--namespace", default=None)

    status = sub.add_parser("campaign-status",
                            help="per-task claimed/published/recorded state of one arm (read-only)")
    status.add_argument("--data-root", required=True)
    status.add_argument("--namespace", default=None)
    status.add_argument("--arm", required=True, choices=campaign_arms())

    # ⚠ THIS SUBMITS NOTHING, and the help text says so because an operator reading `--help` is
    # exactly the reader who might assume otherwise. It writes a record that would PERMIT one
    # further attempt; submitting it is a separate human act and this module contains no `sbatch`.
    rec = sub.add_parser("campaign-recover",
                         help="PHASE 2b: authorize ONE further attempt of ONE task, additively. "
                              "Preserves the previous attempt's claim, logs, partial output and "
                              "charged expenditure. SUBMITS NOTHING.")
    rec.add_argument("--data-root", required=True)
    rec.add_argument("--namespace", default=None)
    rec.add_argument("--arm", required=True, choices=campaign_arms())
    rec.add_argument("--task-id", type=int, required=True)
    rec.add_argument("--previous-job-id", required=True,
                     help="the Slurm id of the attempt that failed, as its claim recorded it "
                          "(`<arrayjob>_<task>`, the array job id, or the plain job id)")
    rec.add_argument("--sacct-dump", required=True,
                     help="captured sacct dump in r5_meter.SACCT_FIELDS order. ONE dump answers "
                          "both the terminality question and the admission recheck, so the two "
                          "cannot disagree about the instant they describe. CHECK THE EXIT STATUS "
                          "OF THE COMMAND THAT CAPTURED IT: sacct prints a header and zero rows "
                          "with rc=1 when slurmdbd is down, and zero rows here REFUSE.")
    rec.add_argument("--log-dir", required=True,
                     help="directory holding the failed attempt's Slurm logs. The FILENAMES are "
                          "derived from the launcher's own #SBATCH --output/--error.")
    rec.add_argument("--authorization", required=True,
                     help="file containing Joseph's explicit approval line for THIS retry: "
                          "`z-campaign-recover <campaign digest> <arm> task <id> attempt <n>`")
    rec.add_argument("--code-root", required=True,
                     help="the approved execution tree, for the arm's own #SBATCH declarations")
    rec.add_argument("--spend-basis", required=True,
                     choices=("utc", "naive", "unknown"),
                     help="passed to z_precursor_admission; only 'utc' proceeds")
    rec.add_argument("--max-retries", type=int, required=True,
                     help="passed to z_precursor_admission; REQUIRED, no default")
    rec.add_argument("--now", required=True, help="ISO-8601 UTC decision instant")
    rec.add_argument("--admitted-launcher", action="append", default=[],
                     help="launcher PATH of an already-admitted arm (repeatable)")
    return parser


def _cli_namespace(args):
    """The namespace for an operator command: the flag, else the environment, never a default."""
    return (resolve_namespace() if getattr(args, "namespace", None) is None
            else resolve_namespace({NAMESPACE_ENV: args.namespace}))


def main(argv=None):
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "plan":
            print(json.dumps(namespace_plan(args.data_root), indent=2, sort_keys=True))
        elif args.command == "require-fresh":
            plan = namespace_plan(args.data_root)
            result = check_namespace_fresh(plan, args.arm)
            print(f"[z-precursor] namespace {result['namespace']!r} FRESH for arms "
                  f"{result['arms_checked']}")
        elif args.command == "require-no-member-axis":
            check_no_member_axis()
            print(f"[z-precursor] {MEMBER_OFFSET_ENV} absent; nothing can land under mii/")
        elif args.command == "declare-files":
            print(",".join(declare_arm_files(args.arm, args.launcher)))
        elif args.command == "arm":
            print(json.dumps(parse_sbatch_arm(args.launcher), indent=2, sort_keys=True))
        elif args.command == "arm-dir":
            print(namespace_plan(args.data_root)["arms"][args.arm]["dir"])
        elif args.command == "receipt":
            extra = producer_provenance(bank=args.bank,
                                        population_declared=args.population_declared)
            if args.extra_json:
                extra.update(json.loads(args.extra_json))
            # THE PLAN IS RECORDED, NOT REQUIRED. `MNV_DATA_ROOT` is a property of the RUN, and a
            # receipt written by hand over an archived product legitimately has no data root --
            # refusing there would make the receipt writer refuse the one case it is most needed
            # for. The plan is descriptive context in the receipt; the ARM's own product path is
            # the load-bearing field and it is verified above.
            data_root = os.environ.get("MNV_DATA_ROOT")
            plan = (namespace_plan(data_root, namespace=args.namespace) if data_root else None)
            receipt = write_receipt(product=args.product, out_path=args.out, arm=args.arm,
                                    namespace=args.namespace, plan_json=plan, extra=extra,
                                    code_root=args.code_root,
                                    allow_overwrite=args.allow_overwrite)
            print(f"[z-precursor] receipt written AFTER the product: {args.out} "
                  f"(product sha256 {receipt['product']['sha256']})")
        elif args.command == "check-receipt":
            result = check_receipt(args.receipt,
                                   require_population=not args.no_require_population)
            print(f"[z-precursor] receipt OK: {result['receipt']} -> {result['product']}")
        elif args.command == "campaign-init":
            started = initialize_campaign(
                data_root=args.data_root, namespace=args.namespace, code_root=args.code_root,
                source_manifest=args.source_manifest, bank=args.bank, arms=args.arms,
                label=args.label)
            campaign, body = started["campaign"], started["campaign"]["body"]
            print(f"[z-precursor] campaign {campaign['campaign_digest']} INITIALIZED")
            print(f"  namespace     {body['namespace']}  (established by an exclusive create)")
            print(f"  manifest      {campaign['path']}")
            print(f"  code          A-2(f) listing {body['code']['listing_sha256']} over "
                  f"{body['code']['file_count']} tracked files, HEAD {body['code']['head']}")
            print(f"  inputs        {body['inputs']['entry_count']} bank entries, listing "
                  f"{body['inputs']['listing_sha256']}, cv.npz "
                  f"{body['inputs']['bank_cv_sha256']}")
            print(f"  seeds         estimator {body['seeds']['estimator_seed']} "
                  f"({body['seeds']['estimator_group']} baseline "
                  f"{body['seeds']['estimator_baseline']}), draw {body['seeds']['draw_seed']}")
            for arm in sorted(body["arms"]):
                entry = body["arms"][arm]
                print(f"  arm {arm:<8} {entry['n_tasks']} task(s) from "
                      f"{entry['array_spec'] or '<no --array>'} -> "
                      f"{len(entry['outputs'])} declared output(s)")
        elif args.command == "campaign-show":
            ns = _cli_namespace(args)
            campaign = load_campaign(campaign_paths(args.data_root, ns)["manifest"])
            print(json.dumps({"campaign_digest": campaign["campaign_digest"],
                              "body": campaign["body"]}, indent=2, sort_keys=True))
        elif args.command == "campaign-status":
            ns = _cli_namespace(args)
            campaign = load_campaign(campaign_paths(args.data_root, ns)["manifest"])
            status = campaign_arm_status(campaign, args.arm)
            print(f"[z-precursor] campaign {status['campaign_digest'][:12]} arm {status['arm']}: "
                  f"{status['n_complete']} of {status['n_tasks']} task(s) complete "
                  f"(claimed AND published AND recorded)")
            for row in status["tasks"]:
                flags = "".join(("C" if row["claimed"] else "-",
                                 "P" if row["published"] else "-",
                                 "R" if row["recorded"] else "-"))
                attempts = (f"  attempts {row['attempts']}"
                            if row["attempts"] not in ([], [FIRST_ATTEMPT]) else "")
                print(f"  task {row['task_id']:>4}  {flags}  {row['output']}{attempts}")
        elif args.command == "campaign-recover":
            import r5_meter

            ns = _cli_namespace(args)
            try:
                decision_instant = r5_meter.parse_iso_utc(args.now)
            except r5_meter.MeterError as exc:
                raise PrecursorError(f"--now {args.now!r} is not an ISO-8601 UTC instant: "
                                     f"{exc}") from exc
            started = recover_task(
                data_root=args.data_root, namespace=ns, arm=args.arm, task_id=args.task_id,
                previous_job_id=args.previous_job_id, sacct_dump=args.sacct_dump,
                spend_basis=args.spend_basis, max_retries=args.max_retries,
                now=decision_instant, authorization=args.authorization,
                log_dir=args.log_dir, code_root=args.code_root,
                admitted_launchers=args.admitted_launcher)
            record = started["record"]
            print(f"[z-precursor] campaign {record['campaign_digest'][:12]} {record['arm']} task "
                  f"{record['task_id']}: attempt {record['attempt']} AUTHORIZED")
            print(f"  previous      attempt {record['previous_attempt']}, job "
                  f"{record['previous_job_id']}, TERMINAL in "
                  f"{record['terminal_evidence']['terminal_states']} over "
                  f"{record['terminal_evidence']['n_rows']} accounting row(s)")
            preserved = record["preserved"]
            print(f"  preserved     claim {preserved['claim']['name']} (in place, "
                  f"{preserved['claim']['sha256'][:12]})")
            for flag, entry in sorted(preserved["logs"].items()):
                print(f"                {flag} log -> {entry['preserved']} "
                      f"({entry['bytes']} B, {entry['sha256'][:12]})")
            partial = preserved["partial_output"]
            print(f"                partial output -> "
                  + (f"{partial['preserved']} ({partial['bytes']} B, {partial['sha256'][:12]})"
                     if partial else "NONE (the attempt published nothing)"))
            print(f"                charged {preserved['charged_expenditure']['cpu_task_hours']:.4f}"
                  f" CPU task-h over "
                  f"{preserved['charged_expenditure']['attempts']} counted attempt(s)")
            print(f"  admission     {record['admission']['decision']}, bound "
                  f"{record['admission']['bound_cpu_task_hours']:.4f} against ceiling "
                  f"{record['admission']['ceiling_cpu_task_hours']:.1f} CPU task-h")
            print(f"  record        {started['recovery_record']}")
            print(f"  NOTHING WAS SUBMITTED. {record['submits_nothing']}")
    except PrecursorError as exc:
        print(f"[z-precursor] FAIL: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
