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

    ⚠ EMPTINESS IS JUDGED BY THE ARM'S OWN PRODUCT GLOB, NOT BY `os.listdir`. A directory holding
    only a `.gitkeep`, a log, or a `*.tmp.npz` left by `_atomic_savez`'s interrupted rename is not
    a populated namespace, and refusing on those would make the guard fire on correct runs. A
    directory holding one real product IS populated, even though a count-based check calling it
    "nearly empty" would wave it through.

    NO ARM DEFAULTS TO UNCHECKED: `arms=None` means ALL of them. A per-arm opt-in would let the
    caller shrink the sweep to the arms it already believes are fresh.
    """
    names = sorted(plan["arms"]) if arms is None else sorted(set(arms))
    require(names, "check_namespace_fresh: no arms named; an empty sweep checks nothing")
    occupied = {}
    for arm in names:
        require(arm in plan["arms"], f"unknown arm {arm!r} in freshness sweep")
        entry = plan["arms"][arm]
        hits = sorted(globmod.glob(entry["product_glob"]))
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

    `lib_member_resume.sh:230` treats ANY non-empty `MNV_EST_SEED_OFFSET` as a declaration, and
    `:84`/`:120-135` then prepend `mii/member_kNNNNNN` to every product path. So the precursor's
    products would silently relocate under the member axis, into a tree the M(ii) grid owns. An
    offset of `0` is still a DECLARATION there -- `-n` is a presence test, not a truth test -- so
    `0` is refused here too, and that asymmetry is the whole reason this cannot be a value check.
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
    info = parse_sbatch_arm(launcher_path)
    if arm == "run":
        names = [f"uthrow5d_slab_{t}.npz" for t in info["task_ids"]]
    elif arm == "block":
        names = ["block5d_knobs.npz" if t == 0 else f"block5d_flux_{t}.npz"
                 for t in info["task_ids"]]
    else:
        raise PrecursorError(
            f"declare_arm_files: arm {arm!r} has no per-task file layout. The dump arm's bank is "
            f"addressed by content (band and universe ids, checked by "
            f"`unified_throw_cov._load_bank`) rather than by task, and the combine arm writes one "
            f"named file. Declaring a task-derived basename list for either would be a fiction.")
    require(len(set(names)) == len(names),
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
    return parser


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
            plan = None
            try:
                plan = namespace_plan(os.environ.get("MNV_DATA_ROOT", "."),
                                      namespace=args.namespace)
            except PrecursorError:
                plan = None
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
    except PrecursorError as exc:
        print(f"[z-precursor] FAIL: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
