#!/usr/bin/python3.11
"""Approval-gated deterministic command queue for unattended campaign plumbing.

Staging is not authorization.  A staged item becomes runnable only after a
human reviews its complete digest and approves it from an interactive TTY.
The ticker executes at most one ready item per invocation, without a shell.
Compute items also require a committed campaign contract, a guarded producer,
an independently bound terminal validator that is guarded under exactly the
same rules as the producer, and a fresh R5 meter receipt pinned to the ruled
instant.  The validator always runs after the producer and alone selects an
exhaustive terminal branch with a decision consequence.  One wall deadline
covers the whole execution: the producer and the validator share
``maximum_cost.wall_hours``, and a validator with no budget left is not
started.

R5 admission is ATOMIC and RESERVED, not per-item.  A ceiling is a property of
the whole queue, so the headroom check counts the receipt's spend, this item's
``maximum_cost`` AND the ``maximum_cost`` of every other compute item whose
hours are not yet accounted for; the check and the claim that admits the item
happen under one exclusive lock, so two tickers cannot both admit against the
same headroom.  A reservation is released by COUNTED SPEND -- not by finishing,
and not by a receipt that merely carries a later timestamp.  An item that RAN
keeps reserving its full declared maximum until a committed receipt is measured
after its outcome AND lists every scheduler task identity that item recorded in
``spend.metered_task_ids``: a fresh receipt still reporting the same spend proves
only that the meter ran, never that it saw these tasks.  The queue gives each
claim an exclusive run directory and passes its task-ids file to the producer
and validator in ``MNV_CAMPAIGN_TASK_IDS_FILE``.  campaignctl reads that file
before the validator and records the ids in the outcome.  An item that never ran
releases at once; an item that ran and recorded NO ids -- missing or malformed
file, crash, launcher error,
timeout -- never releases automatically.  R5 authorizes a stop, not spending,
so only a fresh continuation decision in a committed ``DECISION-*`` or
``AUTHORIZATION-*`` record can release that unmeasurable reservation.  An
operator's typed phrase is additional confirmation, never the authorization.
Re-metering after every compute item, with that item's task ids in the receipt,
is therefore the ordinary reconciliation step.

THE ADMISSION NAMESPACE IS THE REPOSITORY'S ORIGIN REMOTE, AND EVERY ADMISSION IS
A COMPARE-AND-SWAP ON ONE REF THERE.  A ceiling is a property of the whole
campaign, so the inventory that bounds it has to be one object that every process
which could spend can read and can lose a race to.  A passwd home is not that: it
is a property of a HOST, so a queue rooted there is global only for the processes
sharing that filesystem, and two hosts -- or two uids -- each admitted a six-hour
item against one 490-hour receipt and projected 502 against a prohibition of 500.
The origin remote IS that object: it is the one thing every clone on every host
already shares, and it is where the committed receipt itself lives.  It is pinned
in the committed ``docs/orchestration/control-plane/campaign-origin.json``, which
carries the campaign key, the ruling record and its sha256, and the ref name; the
queue refuses every operation -- compute or not -- when the checkout has no
``origin``, when its URL differs from the pinned one after normalisation, or when
the pin is not byte-identical to its blob at ``HEAD``.

A REMOTE HAS TWO URLS, AND THE PIN HAS TO HOLD FOR BOTH OF THEM IN THE REPOSITORY
THAT PUSHES.  ``git remote get-url origin`` prints the FETCH url; a push resolves
its destination through ``remote.origin.pushurl`` and ``url.<base>.pushInsteadOf``,
which only ``get-url --push`` expands.  Under that asymmetry ``ls-remote`` and
``fetch`` answered from the pinned origin while the lease-protected push landed in
a second repository -- every host fetching one base, each pushing to its own
diverted destination, each seeing a successful lease, and the admission log
recording the pinned url either way, which is finding 4's split inventory
returning through a different door.  Three environment variables reached it, all
of them configuration injection: ``GIT_CONFIG_COUNT`` with its indexed pairs,
``GIT_CONFIG_PARAMETERS`` -- which is exactly what git EXPORTS TO ITS CHILDREN, so
a hook-invoked campaignctl inherits it as it inherits ``GIT_DIR`` -- and
``GIT_CONFIG_GLOBAL``.  So: every git invocation this module makes runs with the
whole configuration-injecting and program-selecting family REMOVED and with both
file scopes pointed at nothing, leaving only repository-local configuration; the
queue's own git directory, which is the thing that fetches and pushes, has BOTH of
its urls proved equal to the pin after ``ensure_scratch`` and again before every
fetch and every push, and refuses any local key under ``remote.origin.*`` or
``url.*`` it did not itself write, plus a hooks path, an ssh command or a shell
credential helper; the push names the literal pinned url rather than the remote;
and the admission log records that resolved destination beside the origin url.
The last two are belt and braces -- an ``insteadOf`` rewrite applies to a
command-line url too, so the cleared environment and the configuration check are
the load-bearing halves.

Every state family that decides admission -- items, approvals, claims, outcomes,
releases, revocations, and the admission log -- lives in a git tree on
``refs/campaign/<CAMPAIGN_KEY>/queue`` at that origin.  The passwd-home directory
is now a CACHE of that tree plus purely local files: the producer and validator
logs, the run directories, the admission lock and the queue's own bare git
directory.  Every operation, under the local lock, fetches the ref, makes the
cached families EXACTLY that tree (deleting anything the tree lacks, because a
record only one host has is a record no other host counts), does its work, and
lands any mutation with ``--force-with-lease`` against the sha it fetched.  A
fetch that cannot reach the origin REFUSES: no network is no admission, because
the reservations that bound the ceiling are in that ref and a queue that cannot
read them cannot tell an empty campaign from a full one.  A rejected push means
another host moved the ref: the mutation is discarded, the ref is re-read, and
the operation refuses with a lost-race reason a later tick may retry from the
top.  Nothing is ever merged -- merging two states each computed against headroom
the other had not taken is exactly how 502 hours fit under 500.

The admission window is therefore ONE push: the reservation scan and the claim
that admits the item are computed against one fetched tree and land together, so
two hosts cannot both claim against the same sha.  An outcome, release or
revocation records something that ALREADY HAPPENED, so a push that does not land
does not discard it: the record waits in the cache and every later operation
retries it, while the item stays claimed in the ref and keeps RESERVING on every
host.  An unpushed outcome releases nothing anywhere.  The reservation scan and
the release rule are unchanged in logic, but they read the fetched tree, so a
reservation made on any host counts on every host.  The local lock and the passwd
home remain, for same-host serialisation only; the cross-host serialisation is
the lease.  Items still record the absolute ``repo_path`` they were staged from,
and a ticker runs only its own repository's items while every other item still
reserves and is listed.  A queue pointed elsewhere by ``--state-dir`` may still
stage, approve and run non-compute items, but it refuses compute admission,
because the lock and the run directories are still properties of one directory.

The residual is the origin itself.  The origin remote named in the pinned file is
the namespace: a clone whose ``origin`` is a different repository is a different
repository, and its receipts and its ceiling are its own.  The ref moves only by
lease, so a force-push of that ref without a lease -- or any other direct write to
it -- is a repository write from outside this tool, and no check inside this tool
can prevent it.

The receipt itself must be committed: an R5 measurement that lives only in a
working tree, or in ``/tmp``, is not evidence and cannot authorize compute.  On
a compute arm the guard argv must pin ``--expect-root`` to this repository and
must not carry ``--allow`` or any interpreter/PYTHONPATH escape, because those
turn the guard's own positive control into a pass for the wrong tree.  Binding
the guard binds its subprocess shim as well: the guard reaches inheriting Python
children only through ``nd-unfolding/mnv_guard_shim/sitecustomize.py``, so an
unbound shim is a mutable half of the guard and replacing it alone let a child
load the wrong tree while the run returned 0.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import pwd
import re
import shutil
import socket
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
from typing import Callable, Iterator, NamedTuple, Sequence


HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.resolve()
#: A former per-process root override split the queue when two processes supplied
#: different values.  Its presence is now a refusal: silently ignoring a variable
#: an operator expected to work would conceal the unsafe configuration.
PROHIBITED_CAMPAIGN_STATE_ROOT_ENV = "MNV_CAMPAIGN_STATE_ROOT"
#: Directory below the passwd database's home, OUTSIDE every checkout.  A queue kept under
#: ``<repo>/docs/orchestration/state`` is one queue per clone and per linked worktree,
#: which is how two "campaign-global" inventories came to exist on one host.  The
#: directory name is spelled with an underscore on purpose: ``generate_manifest.py``
#: reads a hyphen-joined campaign word appearing anywhere in a file as that file's
#: campaign attribution (its ``CAMPAIGN_RE``), and a state directory must not
#: fabricate one for this module, its tests or the operator guide.
CAMPAIGN_STATE_ROOT_NAME = ".mnv_campaign"
#: Identity of the ONE campaign this queue serves, spelled so it cannot be confused
#: with a neighbouring one: ``20260902`` is the ruling record's date and ``0836139b``
#: the first eight hex digits of its sha256 --
#: ``shasum -a 256 docs/orchestration/DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md``
#: = ``0836139b1c9a057c194a81a94d45c9f979209a9ac293d4bc8434e6b43fc1a064``, measured at
#: ``180527b0``.  It is a NAME derived from that digest, deliberately not a digest
#: recomputed at run time: an amendment to the record must not silently repoint the
#: queue and orphan every live claim and reservation in it.  Re-deriving it is a
#: decision, and it belongs in a commit that also migrates the directory.
CAMPAIGN_KEY = "r5-20260902-0836139b"
#: Committed pin of the ONE repository whose ref namespace holds this campaign's
#: admission state.  A passwd home is a property of a HOST, so a queue rooted there
#: is global only for the processes sharing that filesystem: two hosts, or two uids,
#: held two complete inventories that each admitted six hours against one 490-hour
#: receipt and projected 502 against a ceiling of 500.  The origin remote is the one
#: object every clone on every host already shares -- it is where the committed
#: receipt itself lives -- so admission is a compare-and-swap on one ref there.  The
#: pin is COMMITTED and checked HEAD-identical through the same identity check the
#: receipt uses, because a working-tree edit to it would otherwise repoint the
#: namespace without leaving a record anybody else could read.
CAMPAIGN_ORIGIN_FILE = Path("docs/orchestration/control-plane/campaign-origin.json")
CAMPAIGN_ORIGIN_KEYS = frozenset(
    {
        "schema_version",
        "campaign_key",
        "ruling_record",
        "ruling_record_sha256",
        "origin_url",
        "queue_ref",
    }
)
#: sha256 of the ruling record :data:`CAMPAIGN_KEY` is a name for.  The pin repeats it
#: so the pinned origin and the queue key are demonstrably the same campaign's, and a
#: pin copied from a neighbouring campaign is a refusal rather than a redirection.
CAMPAIGN_RULING_RECORD_SHA256 = (
    "0836139b1c9a057c194a81a94d45c9f979209a9ac293d4bc8434e6b43fc1a064"
)
#: The one ref at the pinned origin that carries this campaign's queue tree.  Its
#: name is derived from the campaign key for the same reason the directory is: an
#: amendment to the record must not silently repoint the ref and orphan live claims.
CAMPAIGN_QUEUE_REF = f"refs/campaign/{CAMPAIGN_KEY}/queue"
#: State families that DECIDE admission, and therefore live in the ref's tree rather
#: than on one host.  Everything :func:`reserved_task_hours` and
#: :func:`reservation_hold` read is here: the items and their declared costs, the
#: approvals, the claims that open a reservation, the outcomes that date it, and the
#: releases and revocations that close it.  A record that only one host has is a
#: record no other host counts, which is the whole defect the ref exists to close.
QUEUE_STATE_FAMILIES = (
    "approvals",
    "claims",
    "items",
    "outcomes",
    "releases",
    "revocations",
)
#: Leaf directory under the campaign key.  Kept as a separate component so a future
#: campaign-global surface can sit beside the queue rather than inside it.
QUEUE_DIRECTORY_NAME = "campaign-queue"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RELEASE_RECORD_NAME_RE = re.compile(r"^(?:DECISION|AUTHORIZATION)-.+\.md$")
#: Scheduler task identity, in exactly the form ``r5_meter.py`` meters and publishes
#: in ``spend.metered_task_ids``: a job id, optionally with an array-task suffix.  The
#: two patterns must stay identical or a producer could declare ids no receipt could
#: ever list, so a cross-module test compares them rather than trusting this comment.
TASK_ID_RE = re.compile(r"^[0-9]+(?:_[0-9]+)?$")
PYTHON = Path("/usr/bin/python3.11")
ALLOWED_PYTHONS = {PYTHON, Path(sys.executable).resolve()}
GUARD_PATH = Path("nd-unfolding/mnv_guarded_run.py")
#: The guard's subprocess half.  ``mnv_guarded_run.py`` reaches an inheriting Python
#: child only by prepending this directory to ``PYTHONPATH``, so the child's guard is
#: whatever bytes sit at this path when the child starts.  Binding the guard without
#: binding this file leaves the enforcing half mutable, which is why it is bound
#: everywhere the guard is.
GUARD_SHIM_PATH = Path("nd-unfolding/mnv_guard_shim/sitecustomize.py")
# Every file the guard executes in a child or a PATH-resolved launch: the sitecustomize
# shim, the interpreter wrappers, the scanner they delegate to, and -- since the guard
# began running every admitted shell as restricted bash whose PATH is the wrapper
# directory -- the wrappers for the shells and tools that directory has to hold.  All are
# bound under the guard's own rules; a swap of any one of them after staging is a stale
# item.  The list is `mnv_guarded_run.COMMITTED_SHIM_FILES`, spelled here as repository
# paths: a file added to `bin/` and not bound is a file the queue cannot detect a swap of.
GUARD_SHIM_PATHS = (
    GUARD_SHIM_PATH,
    Path("nd-unfolding/mnv_guard_shim/scan_argv.py"),
    Path("nd-unfolding/mnv_guard_shim/wrapper_exec.py"),
    Path("nd-unfolding/mnv_guard_shim/bin/python3"),
    Path("nd-unfolding/mnv_guard_shim/bin/python"),
    Path("nd-unfolding/mnv_guard_shim/bin/_wrapper_body"),
    Path("nd-unfolding/mnv_guard_shim/bin/bash"),
    Path("nd-unfolding/mnv_guard_shim/bin/sh"),
    Path("nd-unfolding/mnv_guard_shim/bin/git"),
    Path("nd-unfolding/mnv_guard_shim/bin/sbatch"),
    Path("nd-unfolding/mnv_guard_shim/bin/srun"),
    Path("nd-unfolding/mnv_guard_shim/bin/sacct"),
    Path("nd-unfolding/mnv_guard_shim/bin/squeue"),
    Path("nd-unfolding/mnv_guard_shim/bin/sinfo"),
    Path("nd-unfolding/mnv_guard_shim/bin/scancel"),
    Path("nd-unfolding/mnv_guard_shim/bin/sstat"),
)
DEFAULT_R5_RECEIPT = Path("docs/orchestration/state/r5-meter-receipt.json")
R5_STOP_DATE = dt.datetime(2026, 9, 30, tzinfo=dt.timezone.utc)
# R5 §3 fixes the baseline at "the commit instant of this record", so the instant is
# a property of the commit that landed the decision record, not of its filename date.
# Derived from `git log -1 --format=%cI 9ce59a59` = 2026-09-02T15:44:27+02:00, which is
# 2026-09-02T13:44:27Z.  A receipt metered from any other t0 counted a different
# interval and is not this stop's receipt, so only this exact instant is accepted.
R5_T0 = dt.datetime(2026, 9, 2, 13, 44, 27, tzinfo=dt.timezone.utc)
R5_DECISION_RECORD = (
    "docs/orchestration/"
    "DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md"
)
R5_CEILINGS = {"gpu_task_hours": 500.0, "cpu_task_hours": 500.0}
R5_METERED_RESOURCES = ("gpu_task_hours", "cpu_task_hours")
# A receipt is evidence, and AGENTS.md makes a result live only once its evidence has
# landed in a commit.  A receipt reachable at an arbitrary absolute path is not that:
# a copy under /tmp, an untracked file, or a working-tree edit made after the commit
# all read as measurements nobody can re-derive from the repository.  So the override
# may name a REPOSITORY-RELATIVE path only, and the file must be tracked and byte
# identical to its blob at HEAD.
R5_UNCOMMITTED_REASON = "receipt is not committed at HEAD"
R5_MAX_AGE = dt.timedelta(hours=24)
# A receipt cannot have measured the future.  Clock skew between the metering host and
# the queue host is real and small; anything beyond this is a fabricated or misdated
# measurement and must not buy freshness the meter never observed.
R5_MAX_FUTURE_SKEW = dt.timedelta(seconds=60)

CONTRACT_KEYS = frozenset(
    {
        "schema_version",
        "campaign_id",
        "scientific_question",
        "candidate",
        "inputs",
        "terminal_validator",
        "terminal_branches",
        "maximum_cost",
        "output_namespace",
        "producer",
        "independent_validator",
        "decision_authority",
        "validator_version",
        "preservation_behavior",
        "retry_policy",
        "accounting",
    }
)
TERMINAL_VALIDATOR_KEYS = frozenset({"argv", "cwd"})
ACCOUNTING_KEYS = frozenset({"expects_scheduler_tasks"})
ARTIFACT_IDENTITY_KEYS = frozenset({"id", "uri", "sha256"})
TERMINAL_BRANCH_KEYS = frozenset(
    {"id", "return_codes", "condition", "decision", "unlocks", "forbids"}
)
MAXIMUM_COST_KEYS = frozenset(
    {"gpu_task_hours", "cpu_task_hours", "wall_hours"}
)
PRESERVATION_KEYS = frozenset({"mode", "artifacts"})
RETRY_POLICY_KEYS = frozenset(
    {"automatic_retraining", "requires_new_authorization"}
)
R5_RECEIPT_KEYS = frozenset(
    {
        "schema_version",
        "decision_record",
        "t0_utc",
        "stop_date_utc",
        "ceilings",
        "unit",
        "measured_at_utc",
        "measured_on_host",
        "source",
        "spend",
        "fired",
        "headroom",
    }
)
R5_SOURCE_KEYS = frozenset({"kind", "argv_or_path", "raw_sha256"})
R5_SPEND_KEYS = frozenset(
    {
        "gpu_task_hours",
        "cpu_task_hours",
        "task_count",
        "metered_task_ids",
        "by_state",
    }
)
R5_FIRED_KEYS = frozenset({"date", "gpu", "cpu", "any"})

#: States in which a compute item holds its declared task-hours against the R5
#: ceilings whatever any receipt says.  ``staged`` and ``approved`` have not spent
#: yet and may spend at any tick; ``outcome-unknown`` is the claimed-or-running case,
#: where the claim exists and no terminal receipt has been written.  A TERMINAL state
#: is not automatically a release: see :func:`reservation_hold`.
RESERVING_STATES = frozenset({"staged", "approved", "outcome-unknown"})
#: Field :func:`write_outcome` stamps with the queue clock, and therefore the instant
#: an item's terminal outcome was recorded.  A receipt must be measured strictly after
#: it before that item's reservation is released.
OUTCOME_INSTANT_FIELD = "completed_at_utc"
#: Field :func:`run_compute_item` stamps with the scheduler task identities the
#: producer wrote to the queue-owned file for this claim.  Its
#: PRESENCE distinguishes "this item's spend is identifiable" from "this item ran and
#: nothing can say which tasks were its", which are released by different acts.
OUTCOME_TASK_IDS_FIELD = "scheduler_task_ids"
#: Environment variable through which the queue gives the producer and validator
#: this claim's exclusive task-ids file.  It is an output capability, not a
#: configurable queue root or a contract field.
CAMPAIGN_TASK_IDS_FILE_ENV = "MNV_CAMPAIGN_TASK_IDS_FILE"
#: Fixed leaf below an exclusive claim directory.  Contracts cannot name this path,
#: because two contracts naming one file can overwrite each other's attribution.
TASK_IDS_FILE_NAME = "scheduler-task-ids.json"
#: Claim and outcome field naming the queue-owned directory for this run.
RUN_DIRECTORY_FIELD = "run_dir"
#: Outcome field naming the exact queue-owned file whose bytes were read.
OUTCOME_TASK_IDS_PATH_FIELD = "scheduler_task_ids_path"
#: Field carrying the sha256 of the task-ids file exactly as read, so the ids in an
#: outcome can be traced back to bytes rather than to this program's parse of them.
OUTCOME_TASK_IDS_SHA256_FIELD = "scheduler_task_ids_sha256"
#: Field carrying the reason the task ids could not be read, when they could not.
OUTCOME_ACCOUNTING_ERROR_FIELD = "accounting_error"
#: Field carrying the seconds the producer and the terminal validator together
#: occupied, measured on a monotonic clock from the instant the producer was
#: started.  ``maximum_cost.wall_hours`` is ONE deadline for both commands, and
#: that is a property of THIS span -- not of the tick, which also fetches the
#: campaign queue ref and pushes the claim and this outcome to it.  Recording the
#: span makes the deadline checkable from the record instead of from a stopwatch
#: held around the whole invocation.
OUTCOME_EXECUTION_SECONDS_FIELD = "execution_seconds"
#: Reason a finished compute item still reserves: it ran, so it may have spent, and no
#: committed receipt has been measured since it stopped.
UNREMEASURED_HOLD = "terminal, not yet remeasured"
#: Reason a finished compute item still reserves although a LATER receipt exists: the
#: receipt does not list this item's scheduler task identities, so it measured an
#: interval that did not include this item's spend.  A later timestamp proves the
#: meter ran; only inclusion proves it counted these tasks.
UNCOUNTED_HOLD = "ran, task ids not yet in a receipt"
#: Reason a finished compute item reserves PERMANENTLY: it ran, and no scheduler task
#: identity was ever recorded for it, so no receipt can ever demonstrate inclusion.
#: Only ``revoke`` before a claim or a committed continuation decision after one
#: clears it. R5 authorizes a stop rather than spending, so a typed phrase alone
#: cannot carry unmeasurable spend into another admission.
UNIDENTIFIED_HOLD = "ran with no recorded task ids; operator release required"
#: Refusal for a queue whose state directory is not the campaign's single canonical
#: one.  The lock and the reservation inventory are properties of that ONE directory,
#: so a second directory cannot see -- and cannot be seen by -- the reservations that
#: bound the ceiling.
NON_CANONICAL_STATE_REASON = "non-canonical state dir cannot admit compute"
#: Fields every queue item record must carry before anything reads it.  The tree
#: now crosses HOSTS, so a record may have been written by a campaignctl that is
#: not this one.  A record missing one of these is a refusal naming the file, not
#: a traceback and not an item that quietly reserves nothing: :func:`summary`,
#: :func:`ready_item` and :func:`reserved_task_hours` all index these directly,
#: and an item whose declared cost cannot be reached must never pass as an item
#: with no cost.
QUEUE_ITEM_REQUIRED_FIELDS = ("id", "kind", "proposal_digest", "created_at_utc")
#: Refusal for an item staged from another checkout.  It reserves and is listed here,
#: because the queue is campaign-global, but its bindings and HEAD are properties of
#: the repository it was staged from and only a ticker there can validate them.
FOREIGN_ITEM_REASON = "item was staged from another checkout"
ADMISSION_LOCK_NAME = "admission.lock"
ADMISSION_LOCK_LOG = "admission-lock.log"
#: Every path in the ref's tree: the state families plus the admission log, which is
#: the record of what admitted what and of every lock broken to get there, and so has
#: to reach the other hosts rather than stay on the one that wrote it.
QUEUE_TREE_PATHS = QUEUE_STATE_FAMILIES + (f"logs/{ADMISSION_LOCK_LOG}",)
#: The queue's own bare git directory, inside the cache.  The state commits are NEVER
#: written through the checkout's ``.git``: campaign bookkeeping does not belong in
#: the science repository's history, and a failed push would leave objects and a moved
#: ref behind in it.  The checkout's ``.git`` is read for HEAD, the receipt identity,
#: the pin identity and the origin URL, and written never.
QUEUE_SCRATCH_GIT_NAME = "queue-git"
#: EVERY local configuration key this git directory legitimately holds: the three
#: :meth:`QueueSync.ensure_scratch` writes, and the ones ``git init`` writes before
#: campaignctl configures anything.  With the one exception below this is the WHOLE
#: rule, and it is an ALLOWLIST, not a list of forbidden keys.  Round 8 spelled the
#: rule as the two namespaces that decide a destination plus a list of the two keys
#: that install a program, and ``core.fsmonitor`` -- which the queue's own ``add``
#: and ``write-tree`` EXECUTE once each per state commit -- was in neither, so it
#: was admitted.  A list has to be extended for every key git adds and the failure
#: of the missing entry is a diverted push, or an executed program, that reports
#: success; the allowlist has no missing entry, because the queue creates this
#: directory and knows what it put in it.  Anything else arrived from outside this
#: module and is refused.
QUEUE_SCRATCH_WRITTEN_CONFIG_KEYS = frozenset(
    {
        # Written by `ensure_scratch`.
        "gc.auto",
        "core.bare",
        "remote.origin.url",
        # Written by `git init --bare` itself.  The format version always; the
        # filesystem probes only where they apply, `core.filemode` and
        # `core.ignorecase` per what git measured and `core.precomposeunicode` on
        # macOS.  They are listed because the directory really does hold them --
        # `test_a_fresh_queue_git_directory_holds_only_keys_this_module_admits` is
        # what proves this set complete for the git that runs it.
        "core.repositoryformatversion",
        "core.filemode",
        "core.ignorecase",
        "core.precomposeunicode",
    }
)
#: The one key admitted OUTSIDE that set: an https origin needs a credential helper,
#: global configuration is out of scope since the environment was cleared, and a
#: helper is the documented way to supply one -- so refusing it would refuse every
#: correct unattended tick.  It is admitted only in the spellings git does not hand
#: to a shell; a leading ``!`` is the spelling git runs as a shell command.
CREDENTIAL_HELPER_KEY = "credential.helper"
CREDENTIAL_HELPER_SHELL_PREFIX = "!"
#: Same-host serialisation for one cache.  It is a LOCAL file and it is not the thing
#: that makes admission global: the cross-host serialisation is the ref lease.
QUEUE_SYNC_LOCK_NAME = "queue-sync.lock"
#: Index used to build a state commit.  Kept inside the queue's own git directory so
#: it can never be confused with the checkout's index, and rebuilt from empty every
#: time so a stale entry cannot add a path this operation did not write.
QUEUE_STATE_INDEX_NAME = "queue-state-index"
#: Records written locally whose push did not land.  An outcome, release or revocation
#: that never reached the ref must be neither forgotten nor believed, so it waits here
#: and every later operation retries it in the order it was recorded.
QUEUE_PENDING_NAME = "pending"
#: The only families a record may wait in.  An unpushed CLAIM is a lost race and is
#: discarded outright -- retrying it would claim against headroom another host has
#: already taken -- while an unpushed OUTCOME is spend that really happened, so
#: dropping it would release a reservation nobody ever counted.
QUEUE_PENDING_FAMILIES = frozenset({"outcomes", "releases", "revocations"})
#: Name of one set-aside record: a sequence, the family, and the item.  The
#: sequence is what preserves ORDER on retry -- a release means nothing before the
#: outcome it releases -- and a name that does not match this is refused rather
#: than sorted into an arbitrary position.
QUEUE_PENDING_NAME_RE = re.compile(
    r"^(?P<sequence>[0-9]{6})-(?P<family>[a-z]+)-.+\.json$"
)
#: Field the returned copy of a record carries when its push has not landed yet.  It
#: is never written into the record itself: the record is what the ref will hold, and
#: "this host has not managed to publish it" is a property of this host and this tick.
QUEUE_PUSH_PENDING_FIELD = "queue_push_pending"
#: Author of every state commit.  A fixed identity, not the operator's: the commit
#: records that campaignctl moved the ref, and the acting host, uid and pid are
#: already in the claim, the outcome and the admission log.
QUEUE_COMMIT_AUTHOR_NAME = "campaignctl"
QUEUE_COMMIT_AUTHOR_EMAIL = "campaignctl@localhost"
#: Environment variables that would redirect a ``git`` invocation away from the
#: repository or index its arguments name.  campaignctl can run from a git hook, and a
#: hook is handed ``GIT_INDEX_FILE`` and ``GIT_DIR`` for a DIFFERENT index and
#: repository, so every git call this module makes clears them first.
GIT_REDIRECTING_ENVIRONMENT = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_NAMESPACE",
)
#: Environment variables that make ``git`` load configuration nobody committed, or run
#: a program nobody named, and so decide where a push GOES.  Three of them landed the
#: lease-protected queue push in a SECOND bare repository while ``ls-remote`` and
#: ``fetch`` still answered from the pinned origin, because ``remote.origin.pushurl``
#: and ``url.<base>.pushInsteadOf`` are expanded for a push -- even for a push to an
#: explicit URL on the command line -- and are invisible to ``git remote get-url``,
#: which prints only the FETCH url.  The configuration-injecting family is three
#: spellings of one capability:
#:
#: * the indexed pairs ``GIT_CONFIG_COUNT`` with ``GIT_CONFIG_KEY_<n>`` and
#:   ``GIT_CONFIG_VALUE_<n>``, which are command-line ``-c`` options in disguise;
#: * ``GIT_CONFIG_PARAMETERS``, the serialised form, which is exactly what git
#:   EXPORTS TO ITS CHILDREN -- so a hook-invoked campaignctl inherits it the way it
#:   inherits ``GIT_DIR``, which is why this module could not be trusted to run
#:   under an inherited environment at all;
#: * the scope-substituting ``GIT_CONFIG_GLOBAL``, ``GIT_CONFIG_SYSTEM``,
#:   ``GIT_CONFIG_NOSYSTEM`` and the legacy ``GIT_CONFIG``, each of which replaces a
#:   whole configuration file with one the caller chose.
#:
#: The rest are the program-selecting family the OI-136 guard lane already refuses for
#: a read-only ``git``: each hands git an arbitrary program to run, so any allowlist
#: over the argv is worth nothing while one of them is set.  The guard refused them and
#: this lane passed all of them straight through.
GIT_INJECTING_ENVIRONMENT = (
    "GIT_CONFIG_COUNT",
    "GIT_CONFIG_PARAMETERS",
    "GIT_CONFIG_GLOBAL",
    "GIT_CONFIG_SYSTEM",
    "GIT_CONFIG_NOSYSTEM",
    "GIT_CONFIG",
    "GIT_SSH",
    "GIT_SSH_COMMAND",
    "GIT_SSH_VARIANT",
    "GIT_PAGER",
    "GIT_EDITOR",
    "GIT_SEQUENCE_EDITOR",
    "GIT_EXTERNAL_DIFF",
    "GIT_ASKPASS",
    "GIT_EXEC_PATH",
    "GIT_PROXY_COMMAND",
)
#: The one member of that family whose names are NUMBERED, and so cannot be listed.
#: The suffix is deliberately not required to be a number: removing a variable git
#: would have ignored costs nothing, and re-implementing git's own parse of the index
#: is how a filter comes to wave one through.
GIT_INJECTING_ENVIRONMENT_INDEXED_RE = re.compile(r"^GIT_CONFIG_(?:KEY|VALUE)_")
#: SET, not merely cleared.  Removing ``GIT_CONFIG_GLOBAL`` restores ``~/.gitconfig``,
#: a file every other tool running as this uid may append ``pushInsteadOf`` to, and
#: removing ``GIT_CONFIG_NOSYSTEM`` restores ``/etc/gitconfig``.  Pointing both file
#: scopes at nothing leaves only REPOSITORY-LOCAL configuration -- the one scope
#: :meth:`QueueSync.verify_push_destination` can enumerate, and therefore refuse.  The
#: cost is real and is stated in OPERATOR-GUIDE: a credential helper or an SSH command
#: configured globally is no longer visible to this tool.
GIT_ISOLATED_CONFIGURATION_ENVIRONMENT = {
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
}
#: A git object name, in either hash size, as ``ls-remote`` and ``rev-parse`` print it.
GIT_OBJECT_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
#: What ``git push`` says when the remote ref was not where the lease said it was.
#: All of these mean the same thing -- another host moved the ref between this
#: operation's fetch and its push -- and none may be resolved by merging.  The
#: bare ``[rejected]``/``[remote rejected]`` tokens are deliberately NOT here: a
#: server-side ruleset that forbids creating ``refs/campaign/*`` prints one too,
#: and calling that a lost race would publish a mechanism nobody could act on.
#: It is still a refusal, just not this one.
PUSH_REJECTION_MARKERS = (
    "stale info",
    "fetch first",
    "non-fast-forward",
    "cannot lock ref",
)
#: Refusal for an operation whose push lost the compare-and-swap.  A tick may retry
#: from the top: re-fetch, re-scan the reservations against the tree that actually
#: won, and refuse again on the reservation if that is what the tree now says.
RACE_LOST_REASON = "lost the admission race"
#: Refusals for a checkout that cannot establish the admission namespace at all.
#: Every one of them refuses EVERY operation, compute or not: a queue that cannot
#: prove which namespace it is in cannot be trusted to stage into it either.
NO_ORIGIN_REASON = "checkout has no origin remote"
ORIGIN_MISMATCH_REASON = "checkout origin is not this campaign's pinned origin"
ORIGIN_PIN_UNCOMMITTED_REASON = "campaign origin pin is not committed at HEAD"
ORIGIN_UNREACHABLE_REASON = "campaign origin is unreachable"
#: A remote has TWO urls, and ``get-url`` prints only the fetch one.  A checkout whose
#: origin fetches from the pin and pushes elsewhere is a checkout whose operator has
#: told git the namespace is somewhere else, so it is refused on the same footing as a
#: mismatched fetch url even though this tool never pushes through the checkout.
ORIGIN_PUSH_MISMATCH_REASON = (
    "checkout origin does not push to this campaign's pinned origin"
)
#: Measured where it MATTERS: in the queue's own git directory, the repository that
#: actually fetches and pushes.  Both of its urls are re-read before every fetch and
#: every push, because the destination is a property of that repository's
#: configuration and of the environment, neither of which the checkout's answer
#: covers.
QUEUE_PUSH_MISMATCH_REASON = (
    "the campaign queue does not push to this campaign's pinned origin"
)
#: The queue creates and configures its own git directory, so EVERY key in it is one
#: this module wrote or one that arrived from outside it.  The second case is a
#: refusal rather than a value to interpret, and the refusal does not depend on
#: anybody having predicted what the key does.
QUEUE_SCRATCH_CONFIG_REASON = (
    "the campaign queue's git configuration was written from outside campaignctl"
)
#: Interpreter flags that change where imports come from, and therefore defeat the
#: OI-136 guard from inside its own argv: ``-S`` drops ``site``, ``-I`` implies ``-s``
#: and ``-E``, and ``-E`` discards the environment the arm was declared with.
FORBIDDEN_INTERPRETER_LETTERS = frozenset("SIE")
SHORT_FLAG_RE = re.compile(r"-[A-Za-z]+")
EXPECT_ROOT_FLAG = "--expect-root"
ALLOW_FLAG = "--allow"


class QueueError(RuntimeError):
    pass


class AdmissionLockHeld(QueueError):
    """Another ticker holds the exclusive admission lock."""


class AdmissionRaceLost(QueueError):
    """Another host moved the campaign queue ref between this fetch and this push.

    It is not an error in the operation and it is not a reason to merge: the ref
    that won holds a complete state, and the losing mutation was computed against
    headroom that host has now taken.  The mutation is discarded, the ref is
    re-read, and a later tick decides again against what the origin actually
    says -- which may well be a refusal on the reservation.
    """


class ReceiptAccounting(NamedTuple):
    """What a committed receipt proves about spend, for the reservation scan.

    Both fields are required together because either alone releases a reservation
    it has not accounted for: ``measured_at`` alone releases an item the meter
    never saw (a fresh query over the wrong interval, or over rows this item's
    tasks are not in), and inclusion alone would release an item whose ids appear
    in a receipt taken BEFORE it stopped and therefore before its final spend.
    """

    measured_at: dt.datetime
    metered_task_ids: frozenset[str]


def _refuse_process_state_root() -> None:
    """Refuse a legacy per-process root before it can split the queue."""
    if PROHIBITED_CAMPAIGN_STATE_ROOT_ENV in os.environ:
        raise QueueError(
            f"{PROHIBITED_CAMPAIGN_STATE_ROOT_ENV} is forbidden: the campaign "
            "state root is fixed by the passwd home for this uid"
        )


def git_environment(**overrides: str) -> dict[str, str]:
    """Return an environment in which ``git`` obeys its own arguments AND its own pin.

    campaignctl can run from a git hook, and a hook is handed ``GIT_DIR`` and its
    own ``GIT_INDEX_FILE`` for a different repository and a different index.
    Those variables OUTRANK ``-C`` and ``--git-dir``, so a HEAD identity check or
    a state commit made under them would silently measure or write the wrong
    object.  They are cleared for every git invocation this module makes, and
    terminal prompting is disabled so a missing credential refuses instead of
    hanging an unattended tick.

    The same inheritance decides WHERE A PUSH GOES.  A hook exports
    ``GIT_CONFIG_PARAMETERS`` to its children, and every member of
    :data:`GIT_INJECTING_ENVIRONMENT` can install a ``pushurl`` or a
    ``pushInsteadOf`` that diverts the lease-protected queue push to another
    repository while ``ls-remote`` and ``fetch`` still answer from the pinned
    origin -- a diverted push that reports success, and an admission log that
    records the pinned url either way.  The whole family is therefore removed,
    the numbered half by :data:`GIT_INJECTING_ENVIRONMENT_INDEXED_RE`, and
    :data:`GIT_ISOLATED_CONFIGURATION_ENVIRONMENT` is SET, so the only
    configuration any of these invocations can read is repository-local.
    """
    environment = {
        key: value
        for key, value in os.environ.items()
        if key not in GIT_REDIRECTING_ENVIRONMENT
        and key not in GIT_INJECTING_ENVIRONMENT
        and not GIT_INJECTING_ENVIRONMENT_INDEXED_RE.match(key)
    }
    environment.update(GIT_ISOLATED_CONFIGURATION_ENVIRONMENT)
    # The ticker is unattended.  A credential prompt on the fetch or the push
    # would HANG it with the admission lock held, which is worse than any
    # refusal: a refusal is retried at the next tick and says why, a hang holds
    # the lock until someone notices.  Prompts off means missing credentials read
    # as an unreachable origin.
    environment["GIT_TERMINAL_PROMPT"] = "0"
    environment.update(overrides)
    return environment


def _passwd_home() -> Path:
    """Return this UID's home directory from the system passwd database."""
    try:
        return Path(pwd.getpwuid(os.getuid()).pw_dir)
    except (KeyError, OSError) as exc:
        raise QueueError(f"cannot resolve passwd home for uid {os.getuid()}") from exc


def campaign_state_root() -> Path:
    """Return the UID-derived host directory that holds this campaign's queue.

    Returns
    -------
    Path
        The passwd database home for ``os.getuid()``, with ``.mnv_campaign``
        appended.  ``$HOME`` is deliberately irrelevant because it is mutable per
        process and could split the queue.

    Raises
    ------
    QueueError
        If the retired per-process root override is present or the passwd home
        cannot be resolved.  Ignoring the retired variable would hide an operator
        configuration that no longer has its expected effect.
    """
    _refuse_process_state_root()
    return _passwd_home() / CAMPAIGN_STATE_ROOT_NAME


def canonical_state_dir() -> Path:
    """Return the ONE queue directory every checkout on this host shares."""
    return (campaign_state_root() / CAMPAIGN_KEY / QUEUE_DIRECTORY_NAME).resolve()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inside(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise QueueError(f"path is outside repository: {path}") from exc
    return resolved


def atomic_json(path: Path, value: dict, *, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        if exclusive:
            try:
                os.link(temporary, path)
            except FileExistsError as exc:
                raise QueueError(f"refusing to overwrite: {path}") from exc
        else:
            os.replace(temporary, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            temporary.unlink()


def read_object(path: Path) -> dict:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise QueueError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise QueueError(f"expected JSON object: {path}")
    return value


def require_object(
    value: object,
    *,
    field: str,
    keys: frozenset[str],
) -> dict[str, object]:
    """Return an object after checking its complete key set."""
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise QueueError(f"{field} must be an object")
    actual = set(value)
    missing = sorted(keys - actual)
    unknown = sorted(actual - keys)
    if missing:
        raise QueueError(f"{field} is missing required field(s): {', '.join(missing)}")
    if unknown:
        raise QueueError(f"{field} has unknown field(s): {', '.join(unknown)}")
    return value


def require_text(value: object, *, field: str) -> str:
    """Return a nonempty text field with surrounding whitespace removed."""
    if not isinstance(value, str) or not value.strip():
        raise QueueError(f"{field} must be a nonempty string")
    return value.strip()


def require_text_list(value: object, *, field: str) -> list[str]:
    """Return an explicit list whose entries are nonempty strings."""
    if not isinstance(value, list):
        raise QueueError(f"{field} must be an array")
    values = [require_text(entry, field=f"{field} entry") for entry in value]
    if len(values) != len(set(values)):
        raise QueueError(f"{field} contains duplicate entries")
    return values


def require_argv(value: object, *, field: str) -> list[str]:
    """Return a nonempty subprocess argument vector."""
    if not isinstance(value, list) or not value:
        raise QueueError(f"{field} must be a nonempty array")
    return [require_text(entry, field=f"{field} entry") for entry in value]


def parse_utc(value: object, *, field: str) -> dt.datetime:
    """Parse an offset-aware UTC timestamp."""
    text = require_text(value, field=field)
    try:
        parsed = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise QueueError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise QueueError(f"{field} must include a UTC offset")
    return parsed.astimezone(dt.timezone.utc)


def require_nonnegative_number(value: object, *, field: str) -> float:
    """Return a finite nonnegative numeric value."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise QueueError(f"{field} must be numeric")
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise QueueError(f"{field} must be finite and nonnegative")
    return number


def require_finite_number(value: object, *, field: str) -> float:
    """Return a finite numeric value."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise QueueError(f"{field} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise QueueError(f"{field} must be finite")
    return number


def validate_artifact_identity(value: object, *, field: str) -> dict[str, object]:
    """Validate an immutable candidate or input identity."""
    artifact = require_object(value, field=field, keys=ARTIFACT_IDENTITY_KEYS)
    require_text(artifact["id"], field=f"{field}.id")
    require_text(artifact["uri"], field=f"{field}.uri")
    sha256 = require_text(artifact["sha256"], field=f"{field}.sha256")
    if not SHA256_RE.fullmatch(sha256):
        raise QueueError(f"{field}.sha256 must be 64 lowercase hexadecimal characters")
    return artifact


def validate_campaign_contract(
    value: object,
    *,
    expected_campaign_id: str | None = None,
) -> dict[str, object]:
    """Validate the complete pre-execution contract for a compute campaign.

    Parameters
    ----------
    value : object
        Decoded JSON value to validate.
    expected_campaign_id : str or None, optional
        Queue item identifier that the contract must name when supplied.

    Returns
    -------
    dict[str, object]
        The validated contract object.

    Raises
    ------
    QueueError
        If a required field or cross-field safety rule is not satisfied.
    """
    contract = require_object(value, field="campaign contract", keys=CONTRACT_KEYS)
    if contract["schema_version"] != 2:
        if contract["schema_version"] == 1:
            raise QueueError(
                "campaign contract schema_version 1 is refused: "
                "accounting.task_ids_file is queue-owned since schema v2"
            )
        raise QueueError("campaign contract schema_version must be 2")

    campaign_id = require_text(contract["campaign_id"], field="campaign_id")
    validate_id(campaign_id)
    if expected_campaign_id is not None and campaign_id != expected_campaign_id:
        raise QueueError(
            f"campaign contract id {campaign_id!r} does not match queue item "
            f"{expected_campaign_id!r}"
        )
    require_text(contract["scientific_question"], field="scientific_question")
    validate_artifact_identity(contract["candidate"], field="candidate")

    inputs = contract["inputs"]
    if not isinstance(inputs, list) or not inputs:
        raise QueueError("inputs must be a nonempty array")
    input_identities = [
        validate_artifact_identity(entry, field=f"inputs[{index}]")
        for index, entry in enumerate(inputs)
    ]
    input_ids = [str(identity["id"]) for identity in input_identities]
    input_uris = [str(identity["uri"]) for identity in input_identities]
    if len(input_ids) != len(set(input_ids)):
        raise QueueError("inputs contain duplicate ids")
    if len(input_uris) != len(set(input_uris)):
        raise QueueError("inputs contain duplicate uris")

    terminal_validator = require_object(
        contract["terminal_validator"],
        field="terminal_validator",
        keys=TERMINAL_VALIDATOR_KEYS,
    )
    require_argv(terminal_validator["argv"], field="terminal_validator.argv")
    validator_cwd = require_text(
        terminal_validator["cwd"], field="terminal_validator.cwd"
    )
    if Path(validator_cwd).is_absolute():
        raise QueueError("terminal_validator.cwd must be repository-relative")

    terminal_branches = contract["terminal_branches"]
    if not isinstance(terminal_branches, list) or not terminal_branches:
        raise QueueError("terminal_branches must be a nonempty array")
    branch_ids: set[str] = set()
    claimed_return_codes: set[int] = set()
    fallback_count = 0
    for index, value_branch in enumerate(terminal_branches):
        field = f"terminal_branches[{index}]"
        branch = require_object(value_branch, field=field, keys=TERMINAL_BRANCH_KEYS)
        branch_id = require_text(branch["id"], field=f"{field}.id")
        validate_id(branch_id)
        if branch_id in branch_ids:
            raise QueueError(f"duplicate terminal branch id: {branch_id}")
        branch_ids.add(branch_id)

        return_codes = branch["return_codes"]
        if return_codes == "otherwise":
            fallback_count += 1
        elif isinstance(return_codes, list) and return_codes:
            if any(
                isinstance(code, bool) or not isinstance(code, int)
                for code in return_codes
            ):
                raise QueueError(f"{field}.return_codes must contain only integers")
            if len(return_codes) != len(set(return_codes)):
                raise QueueError(f"{field}.return_codes contains duplicates")
            overlap = claimed_return_codes.intersection(return_codes)
            if overlap:
                raise QueueError(
                    "return code(s) assigned to multiple terminal branches: "
                    + ", ".join(str(code) for code in sorted(overlap))
                )
            claimed_return_codes.update(return_codes)
        else:
            raise QueueError(
                f"{field}.return_codes must be a nonempty integer array or 'otherwise'"
            )

        require_text(branch["condition"], field=f"{field}.condition")
        require_text(branch["decision"], field=f"{field}.decision")
        require_text_list(branch["unlocks"], field=f"{field}.unlocks")
        require_text_list(branch["forbids"], field=f"{field}.forbids")
    if fallback_count != 1:
        raise QueueError(
            "terminal_branches must contain exactly one 'otherwise' branch so every "
            "possible terminal result has a decision consequence"
        )

    maximum_cost = require_object(
        contract["maximum_cost"], field="maximum_cost", keys=MAXIMUM_COST_KEYS
    )
    costs: dict[str, float] = {}
    for key in sorted(MAXIMUM_COST_KEYS):
        costs[key] = require_nonnegative_number(
            maximum_cost[key], field=f"maximum_cost.{key}"
        )
    if costs["wall_hours"] <= 0:
        raise QueueError("maximum_cost.wall_hours must be positive")
    if costs["gpu_task_hours"] == 0 and costs["cpu_task_hours"] == 0:
        raise QueueError("maximum_cost must allow positive GPU or CPU task-hours")

    require_text(contract["output_namespace"], field="output_namespace")
    producer = require_text(contract["producer"], field="producer")
    validator = require_text(
        contract["independent_validator"], field="independent_validator"
    )
    authority = require_text(
        contract["decision_authority"], field="decision_authority"
    )
    identities = [producer.casefold(), validator.casefold(), authority.casefold()]
    if len(set(identities)) != len(identities):
        raise QueueError(
            "producer, independent_validator, and decision_authority identities "
            "must be pairwise distinct"
        )
    require_text(contract["validator_version"], field="validator_version")

    preservation = require_object(
        contract["preservation_behavior"],
        field="preservation_behavior",
        keys=PRESERVATION_KEYS,
    )
    if preservation["mode"] != "preserve-first":
        raise QueueError("preservation_behavior.mode must be 'preserve-first'")
    preserved_artifacts = require_text_list(
        preservation["artifacts"], field="preservation_behavior.artifacts"
    )
    if not preserved_artifacts:
        raise QueueError("preservation_behavior.artifacts must be nonempty")

    retry_policy = require_object(
        contract["retry_policy"], field="retry_policy", keys=RETRY_POLICY_KEYS
    )
    if retry_policy["automatic_retraining"] is not False:
        raise QueueError("retry_policy.automatic_retraining must be false")
    if retry_policy["requires_new_authorization"] is not True:
        raise QueueError("retry_policy.requires_new_authorization must be true")

    # The accounting block says whether a task identity is expected, but it cannot
    # name the file. Two concurrent contracts sharing one path can overwrite each
    # other's attribution, so schema v2 makes that path a queue-owned claim detail.
    raw_accounting = contract["accounting"]
    if isinstance(raw_accounting, dict) and "task_ids_file" in raw_accounting:
        raise QueueError(
            "accounting.task_ids_file is queue-owned since schema v2 and must "
            "not appear in a contract"
        )
    accounting = require_object(
        raw_accounting, field="accounting", keys=ACCOUNTING_KEYS
    )
    if not isinstance(accounting["expects_scheduler_tasks"], bool):
        raise QueueError("accounting.expects_scheduler_tasks must be a boolean")
    return contract


def terminal_plan(
    contract: dict[str, object], returncode: int | None
) -> dict[str, object]:
    """Resolve a process result to its required preservation and decision actions."""
    branches = contract["terminal_branches"]
    if not isinstance(branches, list):
        raise QueueError("validated campaign contract lost terminal_branches")
    selected: dict[str, object] | None = None
    fallback: dict[str, object] | None = None
    for value_branch in branches:
        if not isinstance(value_branch, dict):
            raise QueueError("validated campaign contract has a non-object branch")
        if value_branch["return_codes"] == "otherwise":
            fallback = value_branch
        elif returncode in value_branch["return_codes"]:
            selected = value_branch
            break
    branch = selected or fallback
    if branch is None:
        raise QueueError("validated campaign contract has no fallback branch")

    preservation = contract["preservation_behavior"]
    retry_policy = contract["retry_policy"]
    if not isinstance(preservation, dict) or not isinstance(retry_policy, dict):
        raise QueueError("validated campaign contract lost terminal policy objects")
    return {
        "terminal_branch": branch["id"],
        "decision_consequence": branch["decision"],
        "unlocks": branch["unlocks"],
        "forbids": branch["forbids"],
        "required_actions": [
            {
                "action": "preserve",
                "mode": preservation["mode"],
                "artifacts": preservation["artifacts"],
            },
            {
                "action": "refer-decision",
                "authority": contract["decision_authority"],
                "consequence": branch["decision"],
            },
        ],
        "automatic_retraining": retry_policy["automatic_retraining"],
        "retry_requires_new_authorization": retry_policy[
            "requires_new_authorization"
        ],
    }


class Queue:
    def __init__(
        self,
        repo: Path = REPO,
        state: Path | None = None,
        clock: Callable[[], str] = utc_now,
    ) -> None:
        _refuse_process_state_root()
        self.repo = repo.resolve()
        self.state = (canonical_state_dir() if state is None else state).resolve()
        self.clock = clock
        # Built on first use rather than in the constructor: constructing a Queue
        # must not reach the network, because `list` on a laptop with no route to
        # the origin has to be able to say WHY it refuses rather than fail while
        # the object is being made.
        self._sync: QueueSync | None = None

    def require_fixed_state_root(self) -> None:
        """Refuse a per-process root added after this queue was constructed."""
        _refuse_process_state_root()

    @property
    def canonical_state(self) -> Path:
        """Return the one state directory that may admit compute on this host.

        It is a property of the HOST and the campaign, not of this repository: a
        directory inside a checkout is one directory per clone and per linked
        worktree, and two of those each considered its own queue canonical.
        """
        self.require_fixed_state_root()
        return canonical_state_dir()

    def state_is_canonical(self) -> bool:
        """Report whether this queue IS the campaign-global queue.

        Returns
        -------
        bool
            ``True`` only when the resolved state directory is the resolved
            ``<state root>/<campaign key>/campaign-queue``.  The comparison is on
            resolved paths so a spelling with ``..``, a relative path or a
            symlinked temporary root is recognised, and so a directory that merely
            looks similar is not.
        """
        self.require_fixed_state_root()
        return self.state == self.canonical_state

    def path(self, family: str, item_id: str) -> Path:
        self.require_fixed_state_root()
        validate_id(item_id)
        return self.state / family / f"{item_id}.json"

    def item(self, item_id: str) -> dict:
        path = self.path("items", item_id)
        return require_queue_item(read_object(path), path)

    def items(self) -> list[dict]:
        self.require_fixed_state_root()
        root = self.state / "items"
        if not root.is_dir():
            return []
        return [
            require_queue_item(read_object(path), path)
            for path in sorted(root.glob("*.json"))
        ]

    def sync(self) -> QueueSync:
        """Return this queue's compare-and-swap channel to the origin's queue ref.

        One channel per cache directory per process.  The LOCK it serialises on is
        shared with every other ``Queue`` in this process that resolves the same
        cache, so a nested operation is re-entered rather than deadlocked.
        """
        self.require_fixed_state_root()
        if self._sync is None:
            self._sync = QueueSync(self)
        return self._sync

    def git_head(self) -> str:
        result = subprocess.run(
            ["git", "-C", str(self.repo), "rev-parse", "HEAD"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            env=git_environment(),
        )
        if result.returncode != 0:
            raise QueueError(f"cannot resolve repository HEAD: {result.stdout.strip()}")
        return result.stdout.strip()

    def committed_file_sha256(self, path: Path) -> str:
        """Return the SHA-256 of a file as committed at the queue's HEAD."""
        relative = inside(path, self.repo).relative_to(self.repo).as_posix()
        digests = self.committed_file_sha256_many([relative])
        committed = digests.get(relative)
        if committed is None:
            raise QueueError(
                f"bound file must be committed at repository HEAD: {relative}"
            )
        return committed

    def committed_blob_id(self, path: Path) -> str:
        """Return the git blob object name of a file as committed at ``HEAD``.

        The admission log records this for the origin pin, so a reader can name
        the exact object that decided which namespace the admission belonged to
        without re-deriving it from a path that may since have been rewritten.
        """
        relative = inside(path, self.repo).relative_to(self.repo).as_posix()
        result = subprocess.run(
            ["git", "-C", str(self.repo), "rev-parse", f"HEAD:{relative}"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            env=git_environment(),
        )
        blob = result.stdout.strip()
        if result.returncode != 0 or not GIT_OBJECT_RE.fullmatch(blob):
            raise QueueError(
                f"cannot resolve the blob committed at HEAD for {relative}: {blob}"
            )
        return blob

    def committed_file_sha256_many(
        self, relatives: Sequence[str]
    ) -> dict[str, str | None]:
        """SHA-256 of each path as committed at HEAD, in ONE ``git`` process.

        WHY IT IS BATCHED, MEASURED RATHER THAN ASSUMED.  ``git show HEAD:<path>``
        per binding is one subprocess per bound file, and the guard's shim grew from
        four committed files to sixteen when every admitted shell began running as
        restricted bash out of a wrapper directory.  Twelve extra ``git`` processes
        inside ``validate_unchanged`` cost ~60 ms, which is measured by
        ``test_one_wall_deadline_covers_producer_and_validator``: that control asserts
        a one-second wall budget ends the run inside 1.5 s, and the per-binding
        spelling pushed it to 1.52 s.  ``git cat-file --batch`` answers all of them
        from one process, so the cost of binding a file is a line of stdin.

        A path missing at HEAD maps to ``None`` rather than raising, because the
        caller owns the message: ``require_committed_binding`` and the contract check
        say different things about the same absence.
        """
        wanted = list(dict.fromkeys(relatives))
        if not wanted:
            return {}
        process = subprocess.Popen(
            ["git", "-C", str(self.repo), "cat-file", "--batch"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=git_environment(),
        )
        request = "".join(f"HEAD:{relative}\n" for relative in wanted).encode()
        assert process.stdin is not None and process.stdout is not None
        process.stdin.write(request)
        process.stdin.close()
        digests: dict[str, str | None] = {}
        try:
            for relative in wanted:
                header = process.stdout.readline()
                if not header:
                    digests[relative] = None
                    continue
                fields = header.decode("utf-8", "replace").split()
                # `<oid> <type> <size>` for a blob that exists; `<name> missing` for
                # one that does not.  A tree or a tag at that path is not a file and
                # is reported absent for the same reason a missing blob is.
                if len(fields) != 3 or fields[1] != "blob":
                    digests[relative] = None
                    continue
                size = int(fields[2])
                contents = process.stdout.read(size)
                process.stdout.read(1)       # the newline `cat-file` appends
                digests[relative] = hashlib.sha256(contents).hexdigest()
        finally:
            process.stdout.close()
            process.wait()
        return digests

    def require_committed_binding(
        self, binding: dict[str, str], committed: dict[str, str | None] | None = None
    ) -> None:
        """Require a binding to match the corresponding blob at ``HEAD``.

        ``committed`` is a batch already read by ``committed_file_sha256_many``; a
        caller with many bindings passes one rather than paying a ``git`` process per
        file.  A path absent from the batch falls back to the single lookup, so the
        two spellings cannot disagree about a file the batch did not cover.
        """
        path = resolve_repo_path(self.repo, binding["path"])
        if committed is not None and binding["path"] in committed:
            committed_sha256 = committed[binding["path"]]
            if committed_sha256 is None:
                relative = inside(path, self.repo).relative_to(self.repo).as_posix()
                raise QueueError(
                    f"bound file must be committed at repository HEAD: {relative}"
                )
        else:
            committed_sha256 = self.committed_file_sha256(path)
        if (
            binding["sha256"] != committed_sha256
            or sha256_file(path) != committed_sha256
        ):
            raise QueueError(
                "bound file differs from the file committed at HEAD: "
                f"{binding['path']}"
            )


ORIGIN_URL_SCHEME_RE = re.compile(
    r"^(?P<scheme>[A-Za-z][A-Za-z0-9+.\-]*)://(?P<host>[^/]*)(?P<path>/.*)?$"
)
ORIGIN_URL_SCP_RE = re.compile(
    r"^(?:(?P<user>[^/@]+)@)?(?P<host>[^/:]+):(?P<path>.+)$"
)


def normalize_origin_url(value: str) -> str:
    """Return the comparable spelling of a git remote URL.

    Two spellings of ONE repository must not read as two namespaces, and two
    repositories must not read as one.  Only the differences git itself treats as
    cosmetic are removed: a trailing ``/``, a trailing ``.git``, and the case of
    the scheme and the host, which URL schemes and DNS define
    case-insensitively.  The PATH keeps its case, because a server's paths may be
    case sensitive and folding them would merge two repositories into one
    namespace -- which is the failure this whole check exists to prevent.

    Parameters
    ----------
    value : str
        Remote URL as ``git remote get-url`` prints it, or as the pin records it.

    Returns
    -------
    str
        The normalised spelling, for equality comparison only.  It is never
        handed to git: every git invocation uses the URL the checkout actually
        configured, after that URL has been proven equal to the pinned one.
    """
    text = require_text(value, field="origin url").rstrip("/")
    if text.endswith(".git"):
        text = text[: -len(".git")]
    text = text.rstrip("/")
    if not text:
        raise QueueError("origin url must not be empty after normalisation")
    scheme_match = ORIGIN_URL_SCHEME_RE.fullmatch(text)
    if scheme_match is not None:
        return (
            f"{scheme_match.group('scheme').lower()}://"
            f"{scheme_match.group('host').lower()}"
            f"{scheme_match.group('path') or ''}"
        )
    scp_match = ORIGIN_URL_SCP_RE.fullmatch(text)
    if scp_match is not None:
        user = scp_match.group("user")
        return (
            f"{user + '@' if user else ''}"
            f"{scp_match.group('host').lower()}:{scp_match.group('path')}"
        )
    # A local path, which is what the suite's throwaway origin is.  Nothing about
    # it is case insensitive on any filesystem this campaign runs on, so it is
    # compared exactly as written.
    return text


class RemoteUrls(NamedTuple):
    """One remote's two urls, which are two DIFFERENT measurements of it.

    ``git remote get-url`` prints the fetch url.  ``git remote get-url --push``
    is the only spelling that expands ``remote.<name>.pushurl`` and
    ``url.<base>.pushInsteadOf``, which is what a push resolves its destination
    through.  Reading only the first is the asymmetry round 8 found: ls-remote and
    fetch answered from the pinned origin while the push landed in a second
    repository, and every check in this module agreed the pin was satisfied.
    """

    fetch: str
    push: str


def read_remote_urls(
    arguments: Sequence[str], *, no_remote_reason: str
) -> RemoteUrls:
    """Return both urls of the ``origin`` remote of one repository.

    Parameters
    ----------
    arguments : Sequence[str]
        Leading git arguments that select the repository -- ``-C <path>`` for a
        checkout, ``--git-dir <path>`` for the queue's own git directory.
    no_remote_reason : str
        Refusal to raise when the remote does not resolve at all.

    Returns
    -------
    RemoteUrls
        Both urls, exactly as git printed them.

    Raises
    ------
    QueueError
        If either read fails.  ``stderr`` is kept SEPARATE from ``stdout`` here,
        unlike the refusal-quoting calls elsewhere in this module: these two
        answers are PARSED and compared against the pin, and a warning git wrote
        to stderr would be read as part of a url.
    """
    urls: list[str] = []
    for direction, flags in (("fetch", ()), ("push", ("--push",))):
        result = subprocess.run(
            ["git", *arguments, "remote", "get-url", *flags, "origin"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            env=git_environment(),
        )
        if result.returncode != 0:
            raise QueueError(
                f"{no_remote_reason}: the campaign's admission namespace is the "
                f"origin remote, so there is nothing to admit into: reading its "
                f"{direction} url failed: {result.stderr.strip()}"
            )
        urls.append(require_text(result.stdout, field=f"origin {direction} url"))
    return RemoteUrls(fetch=urls[0], push=urls[1])


def checkout_origin_urls(queue: Queue) -> RemoteUrls:
    """Return the checkout's ``origin`` urls in both directions, or refuse.

    A checkout with no ``origin`` has no admission namespace.  That is a refusal
    rather than a fallback to the passwd home: falling back is precisely how one
    campaign came to have as many inventories as it had hosts.
    """
    return read_remote_urls(
        ["-C", str(queue.repo)], no_remote_reason=NO_ORIGIN_REASON
    )


def campaign_origin(queue: Queue) -> dict[str, str]:
    """Return the origin this queue may use, or refuse in one of five directions.

    The queue refuses EVERY operation -- compute or not -- when the checkout has
    no ``origin``; when its fetch URL differs from the pinned one after
    normalisation; when its PUSH url differs from it, which is a separate
    measurement and the one round 8 found unmeasured; when the pin is not
    committed and byte-identical to its blob at ``HEAD``; or when the pin names
    another campaign.  A queue that cannot prove which namespace it is in must
    not stage into it either: an item staged into the wrong namespace reserves
    nothing where it will actually run.

    This is the CHECKOUT's answer, and the checkout is not what pushes.  The
    binding check is :meth:`QueueSync.verify_push_destination`, in the queue's own
    git directory.

    Parameters
    ----------
    queue : Queue
        Queue whose repository carries the pin and configures the remote.

    Returns
    -------
    dict[str, str]
        ``origin_url`` exactly as the checkout configured it, and the pin's
        identity for the admission log.

    Raises
    ------
    QueueError
        In every one of those four directions, each naming what it measured.
    """
    path, pin_sha256, _head = committed_file_identity(
        queue,
        CAMPAIGN_ORIGIN_FILE,
        missing_label="campaign origin pin",
        uncommitted_reason=ORIGIN_PIN_UNCOMMITTED_REASON,
    )
    pin = require_object(
        read_object(path), field="campaign origin pin", keys=CAMPAIGN_ORIGIN_KEYS
    )
    if pin["schema_version"] != 1:
        raise QueueError("campaign origin pin schema_version must be 1")
    for field, expected in (
        ("campaign_key", CAMPAIGN_KEY),
        ("ruling_record", R5_DECISION_RECORD),
        ("ruling_record_sha256", CAMPAIGN_RULING_RECORD_SHA256),
        ("queue_ref", CAMPAIGN_QUEUE_REF),
    ):
        actual = require_text(pin[field], field=f"campaign origin pin {field}")
        if actual != expected:
            raise QueueError(
                f"campaign origin pin {field} is {actual!r}, which is not this "
                f"campaign's {expected!r}"
            )
    pinned = require_text(pin["origin_url"], field="campaign origin pin origin_url")
    configured = checkout_origin_urls(queue)
    if normalize_origin_url(configured.fetch) != normalize_origin_url(pinned):
        raise QueueError(
            f"{ORIGIN_MISMATCH_REASON}: origin is {configured.fetch!r} and the "
            f"pin at {CAMPAIGN_ORIGIN_FILE.as_posix()} names {pinned!r}; a clone "
            "whose origin is a different repository is a different repository"
        )
    # The push url is compared SEPARATELY because it is a separate value: a
    # `pushurl`, or a `url.<base>.pushInsteadOf` that matches the pin, leaves the
    # fetch url identical to the pin and sends every push elsewhere.
    if normalize_origin_url(configured.push) != normalize_origin_url(pinned):
        raise QueueError(
            f"{ORIGIN_PUSH_MISMATCH_REASON}: origin fetches from "
            f"{configured.fetch!r}, which is the pin, but pushes to "
            f"{configured.push!r}; a remote has two urls and only "
            "`get-url --push` expands pushurl and url.<base>.pushInsteadOf"
        )
    return {
        "origin_url": configured.fetch,
        "pin_path": CAMPAIGN_ORIGIN_FILE.as_posix(),
        "pin_sha256": pin_sha256,
    }


class _SyncLock:
    """Same-host serialisation for one queue cache.

    Re-entrant per THREAD and shared by every ``Queue`` in this process that
    resolves the same cache: a second lock object on the same file would
    deadlock a nested operation instead of re-entering it.  This lock does NOT
    make admission global -- it cannot see another host at all.  It keeps two
    processes on one host from interleaving a fetch, a mutation and a push
    through the same working files; the cross-host serialisation is the lease.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.guard = threading.RLock()
        self.depth = 0
        self.descriptor: int | None = None

    @contextlib.contextmanager
    def held(self) -> Iterator[None]:
        with self.guard:
            if self.depth == 0:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                self.descriptor = os.open(
                    self.path, os.O_CREAT | os.O_RDWR, 0o644
                )
                fcntl.flock(self.descriptor, fcntl.LOCK_EX)
            self.depth += 1
            try:
                yield
            finally:
                self.depth -= 1
                if self.depth == 0 and self.descriptor is not None:
                    fcntl.flock(self.descriptor, fcntl.LOCK_UN)
                    os.close(self.descriptor)
                    self.descriptor = None


_SYNC_LOCKS: dict[Path, _SyncLock] = {}
_SYNC_LOCKS_GUARD = threading.Lock()


def _sync_lock(path: Path) -> _SyncLock:
    """Return the ONE lock object for a cache path in this process."""
    with _SYNC_LOCKS_GUARD:
        lock = _SYNC_LOCKS.get(path)
        if lock is None:
            lock = _SyncLock(path)
            _SYNC_LOCKS[path] = lock
        return lock


class QueueSync:
    """The origin's queue ref is the admission namespace; this is the CAS on it.

    The passwd-home directory is a CACHE of one git tree plus purely local files
    -- the producer and validator logs, the run directories, the admission lock,
    and this object's own git directory.  Every operation fetches the ref, makes
    the cached state families EXACTLY that tree, does its work, and lands any
    mutation with ``--force-with-lease`` against the sha it fetched.  A rejected
    push means another host moved the ref: the mutation is discarded and the
    operation refuses, because merging two states each computed against headroom
    the other had not taken is how 502 hours fit under a ceiling of 500.
    """

    def __init__(self, queue: Queue) -> None:
        self.queue = queue
        self.cache = queue.state
        self.scratch = self.cache / QUEUE_SCRATCH_GIT_NAME
        self.lock = _sync_lock(self.cache / QUEUE_SYNC_LOCK_NAME)
        self.depth = 0
        #: Sha the current operation's lease is taken against; ``None`` when the
        #: ref does not exist and the lease is against the empty value.
        self.base: str | None = None
        #: Sha whose tree the cache was last made equal to, and the fingerprint
        #: it had immediately afterwards.  Together they say whether the cache is
        #: still that tree, so an unchanged ref does not pay for a re-extraction
        #: and a LOCALLY changed cache is reset even when the ref stood still.
        self.cache_sha: str | None = None
        self.fingerprint: dict[str, str] = {}
        self.scratch_origin: str | None = None
        #: Pin and URL this channel last proved, re-measured every refresh: a
        #: working-tree edit to the pin must not be believed for a second
        #: operation just because the first one passed.
        self.origin: dict[str, str] | None = None
        #: Where this git directory's pushes actually GO, as ``get-url --push``
        #: resolves it there.  Re-measured before every fetch and every push, and
        #: recorded in the admission log beside the origin url: the fetch url was
        #: what that record used to carry, and it is the one value that stays
        #: equal to the pin while the push is diverted.
        self.push_url: str | None = None

    # -- git plumbing ----------------------------------------------------------

    def git(
        self,
        *arguments: str,
        check: bool = True,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess:
        """Run one git command against the queue's own bare git directory."""
        result = subprocess.run(
            ["git", "--git-dir", str(self.scratch), *arguments],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            env=git_environment() if environment is None else environment,
        )
        if check and result.returncode != 0:
            raise QueueError(
                f"campaign queue git failed: git {' '.join(arguments)}: "
                f"{result.stdout.strip()}"
            )
        return result

    def scratch_config(self) -> list[tuple[str, str]]:
        """Return the queue git directory's LOCAL configuration, key by value.

        ``-z`` rather than line splitting because a configuration value may
        contain a newline, and a parser that split on newlines would read one
        such value as a second key -- a key an attacker chooses.  ``stderr`` is
        kept apart from ``stdout`` for the same reason it is in
        :func:`read_remote_urls`: this output is parsed, not quoted.
        """
        result = subprocess.run(
            [
                "git",
                "--git-dir",
                str(self.scratch),
                "config",
                "--list",
                "--local",
                "-z",
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            env=git_environment(),
        )
        if result.returncode != 0:
            raise QueueError(
                f"cannot read the campaign queue's own git configuration at "
                f"{self.scratch}, so its push destination is unproven: "
                f"{result.stderr.strip()}"
            )
        entries: list[tuple[str, str]] = []
        for chunk in result.stdout.split("\0"):
            if not chunk:
                continue
            key, _, value = chunk.partition("\n")
            entries.append((key, value))
        return entries

    def refuse_unwritten_scratch_config(self) -> None:
        """Refuse configuration in the queue's git directory it did not write.

        The url comparison reads what git resolves NOW.  This reads what could
        resolve it somewhere else NEXT time and what could run a program on the
        way -- a ``pushurl`` written behind the queue's back, an ``insteadOf``
        rewrite, a proxy, an ssh command, a hooks directory, an ``fsmonitor``
        the queue's own ``add`` and ``write-tree`` execute -- and it names none
        of them.  The queue CREATES this directory and it holds exactly
        :data:`QUEUE_SCRATCH_WRITTEN_CONFIG_KEYS`, so every other key arrived
        from outside this module and is refused rather than interpreted.  That
        allowlist is the whole rule, because the categories it replaced were
        lists: ``core.fsmonitor`` was in neither the two destination namespaces
        nor the two program-installing keys, and pointed at a script in this
        directory's own config it ran twice per state commit and the operation
        was admitted.  The only exception is
        :data:`CREDENTIAL_HELPER_KEY`, and only when its value is not the
        spelling git hands to a shell.

        A git version that writes a key this set lacks REFUSES rather than
        admits, which is the safe direction: the queue stops until an operator
        removes the key or the set is extended with a comment saying git wrote
        it.  The unsafe direction is what this replaces -- a rule that had to be
        extended for every key git adds, whose missing entry is a push that
        lands elsewhere, or a program that runs, and reports success.
        """
        for key, value in self.scratch_config():
            lowered = key.lower()
            if lowered in QUEUE_SCRATCH_WRITTEN_CONFIG_KEYS:
                continue
            if lowered == CREDENTIAL_HELPER_KEY and not value.startswith(
                CREDENTIAL_HELPER_SHELL_PREFIX
            ):
                continue
            raise QueueError(
                f"{QUEUE_SCRATCH_CONFIG_REASON}: {self.scratch} sets {key} to "
                f"{value!r}.  campaignctl creates that directory and it holds "
                f"exactly {sorted(QUEUE_SCRATCH_WRITTEN_CONFIG_KEYS)} -- what "
                f"campaignctl writes plus what `git init` wrote -- and outside "
                f"that set only a {CREDENTIAL_HELPER_KEY} whose value does not "
                f"begin with {CREDENTIAL_HELPER_SHELL_PREFIX!r} is admitted.  "
                f"The remedy is to REMOVE {key} from {self.scratch}/config (a "
                f"{CREDENTIAL_HELPER_KEY} may instead be respelled without the "
                "leading marker), NOT to add an allowance for it: a key this "
                "module did not write is a key that can send a push elsewhere "
                "or install a program in the queue's own git invocations."
            )

    def verify_push_destination(self) -> str:
        """Prove this git directory pushes to the PIN, and return where it pushes.

        The measurement is taken HERE, in the repository that fetches and pushes,
        rather than in the checkout: the destination is decided by this
        directory's local configuration and by the environment the push runs
        under, and the checkout's answer covers neither.  Both urls are read,
        because ``get-url`` prints only the fetch one and a diverted push leaves
        it identical to the pin.  It runs after :meth:`ensure_scratch` and again
        before every fetch and every push, so a key written between two
        operations is caught by the second, and it is read with the SAME
        environment the push will use -- an environment measured with any other
        one is a measurement of a different command.

        Returns
        -------
        str
            The push destination as ``get-url --push`` resolves it, which is
            what the admission log records.

        Raises
        ------
        QueueError
            If the directory has not been pointed at the pin yet, if either url
            is not the pin after normalisation, or if the local configuration
            holds a key the queue did not write.
        """
        if self.scratch_origin is None:
            raise QueueError(
                f"{QUEUE_PUSH_MISMATCH_REASON}: {self.scratch} has not been "
                "pointed at the pinned origin yet, so nothing about its "
                "destination has been proved"
            )
        self.refuse_unwritten_scratch_config()
        urls = read_remote_urls(
            ["--git-dir", str(self.scratch)],
            no_remote_reason=QUEUE_PUSH_MISMATCH_REASON,
        )
        pinned = normalize_origin_url(self.scratch_origin)
        for direction, url in (("fetch", urls.fetch), ("push", urls.push)):
            if normalize_origin_url(url) != pinned:
                raise QueueError(
                    f"{QUEUE_PUSH_MISMATCH_REASON}: {self.scratch} resolves its "
                    f"{direction} url to {url!r} and the pin names "
                    f"{self.scratch_origin!r}; the lease protects one ref at one "
                    "repository, and a push to any other one is admitted by a "
                    "lease nobody else can lose"
                )
        self.push_url = urls.push
        return urls.push

    def author_environment(self) -> dict[str, str]:
        """Return the environment that names campaignctl as the commit's author."""
        return git_environment(
            GIT_AUTHOR_NAME=QUEUE_COMMIT_AUTHOR_NAME,
            GIT_AUTHOR_EMAIL=QUEUE_COMMIT_AUTHOR_EMAIL,
            GIT_COMMITTER_NAME=QUEUE_COMMIT_AUTHOR_NAME,
            GIT_COMMITTER_EMAIL=QUEUE_COMMIT_AUTHOR_EMAIL,
        )

    def ensure_scratch(self, origin_url: str) -> None:
        """Create the queue's own bare git directory, point it at the pin, prove it.

        The proof is taken unconditionally, including on the path that finds the
        directory already pointed at ``origin_url`` and writes nothing: what has
        to be re-measured is not what this process last wrote but what the
        directory says NOW, and anything else may have written it since.
        """
        if not (self.scratch / "HEAD").is_file():
            self.cache.mkdir(parents=True, exist_ok=True)
            result = subprocess.run(
                ["git", "init", "--bare", "-q", str(self.scratch)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
                env=git_environment(),
            )
            if result.returncode != 0:
                raise QueueError(
                    f"cannot create the campaign queue git directory "
                    f"{self.scratch}: {result.stdout.strip()}"
                )
            # A commit that only exists here must not be collected between the
            # push that created it and the fetch that reads it back, and this
            # directory is never a checkout, so `add` needs an explicit worktree.
            self.git("config", "gc.auto", "0")
            self.git("config", "core.bare", "false")
            self.scratch_origin = None
        if self.scratch_origin != origin_url:
            self.git("config", "remote.origin.url", origin_url)
            self.scratch_origin = origin_url
        self.verify_push_destination()

    def remote_head(self) -> str | None:
        """Return the origin's current queue-ref sha, or ``None`` when it is unset.

        Raises
        ------
        QueueError
            If the origin cannot be reached.  No network is NO ADMISSION: the
            reservations that bound the ceiling live in that ref, and a queue
            that cannot read them cannot tell an empty campaign from a full one.
        """
        result = self.git(
            "ls-remote", "origin", CAMPAIGN_QUEUE_REF, check=False
        )
        if result.returncode != 0:
            raise QueueError(
                f"{ORIGIN_UNREACHABLE_REASON}: {self.scratch_origin}: no "
                f"operation is possible without {CAMPAIGN_QUEUE_REF}, because "
                f"every reservation that bounds the R5 ceiling lives in it: "
                f"{result.stdout.strip()}"
            )
        for line in result.stdout.splitlines():
            sha, _, name = line.partition("\t")
            if name.strip() == CAMPAIGN_QUEUE_REF and GIT_OBJECT_RE.fullmatch(
                sha.strip()
            ):
                return sha.strip()
        return None

    def local_head(self) -> str | None:
        """Return the sha the queue's own copy of the ref points at."""
        result = self.git(
            "rev-parse", "--verify", "--quiet", f"{CAMPAIGN_QUEUE_REF}^{{commit}}",
            check=False,
        )
        sha = result.stdout.strip()
        if result.returncode != 0 or not GIT_OBJECT_RE.fullmatch(sha):
            return None
        return sha

    # -- the cache -------------------------------------------------------------

    def state_fingerprint(self) -> dict[str, str]:
        """Return a digest per cached state file, for mutation detection.

        Covers every file under the state families rather than only ``*.json``,
        so a path this module does not write is still noticed and still resets
        the cache instead of being carried silently into a commit.
        """
        values: dict[str, str] = {}
        for family in QUEUE_STATE_FAMILIES:
            root = self.cache / family
            if not root.is_dir():
                continue
            for path in sorted(root.rglob("*")):
                if path.is_file():
                    values[
                        f"{family}/{path.relative_to(root).as_posix()}"
                    ] = sha256_file(path)
        log = self.cache / "logs" / ADMISSION_LOCK_LOG
        if log.is_file():
            values[f"logs/{ADMISSION_LOCK_LOG}"] = sha256_file(log)
        return values

    def tree_target(self, name: str) -> Path:
        """Return where one tree entry belongs in the cache, or refuse.

        Fail-closed on anything unmodelled.  A tree entry outside the families
        this module knows would be extracted somewhere nothing reads and,
        worse, would be dropped from the next commit -- so a queue running an
        older campaignctl would silently delete a newer one's records.
        """
        parts = PurePosixPath(name).parts
        if not parts or ".." in parts or name.startswith("/"):
            raise QueueError(f"campaign queue tree holds an unusable path: {name!r}")
        if len(parts) == 2 and parts[0] in QUEUE_STATE_FAMILIES:
            return self.cache / parts[0] / parts[1]
        if name == f"logs/{ADMISSION_LOCK_LOG}":
            return self.cache / "logs" / ADMISSION_LOCK_LOG
        raise QueueError(
            f"campaign queue tree holds a path this campaignctl does not model, "
            f"so it must not be rewritten: {name!r}"
        )

    def extract_tree(self, sha: str) -> None:
        """Write one commit's tree into the cache's state families."""
        result = subprocess.run(
            ["git", "--git-dir", str(self.scratch), "archive", "--format=tar", sha],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=git_environment(),
        )
        if result.returncode != 0:
            raise QueueError(
                f"cannot read the campaign queue tree at {sha}: "
                f"{result.stderr.decode('utf-8', 'replace').strip()}"
            )
        with tarfile.open(fileobj=io.BytesIO(result.stdout), mode="r:") as archive:
            for member in archive.getmembers():
                if member.isdir():
                    continue
                if not member.isfile():
                    raise QueueError(
                        f"campaign queue tree holds an entry that is not a file: "
                        f"{member.name!r}"
                    )
                target = self.tree_target(member.name)
                source = archive.extractfile(member)
                if source is None:
                    raise QueueError(
                        f"campaign queue tree entry cannot be read: {member.name!r}"
                    )
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read())

    def reset_cache(self, sha: str | None) -> None:
        """Make the cached state families EXACTLY the given tree.

        A cached file the tree lacks is DELETED rather than kept.  A record only
        one host has is a record no other host counts, and that is the whole
        defect the ref exists to close; keeping it would rebuild, inside the
        cache, the per-host inventory this design removed.  Everything else in
        the directory -- the run directories, the producer and validator logs,
        the admission lock, the pending records and this git directory -- is
        local by construction and is left untouched.
        """
        for family in QUEUE_STATE_FAMILIES:
            shutil.rmtree(self.cache / family, ignore_errors=True)
        with contextlib.suppress(FileNotFoundError):
            (self.cache / "logs" / ADMISSION_LOCK_LOG).unlink()
        if sha is not None:
            self.extract_tree(sha)
        self.cache_sha = sha
        self.fingerprint = self.state_fingerprint()

    # -- the operation cycle ---------------------------------------------------

    def refresh(self, *, force: bool = False) -> None:
        """Steps (a) and (b): fetch the ref and make the cache equal to its tree."""
        origin = campaign_origin(self.queue)
        self.ensure_scratch(origin["origin_url"])
        self.origin = origin
        remote = self.remote_head()
        if remote is not None and remote != self.local_head():
            # Re-measured immediately before the fetch, not only after
            # `ensure_scratch`: the tree this operation reads is the tree its
            # lease will be taken against, so it must come from the pin.
            self.verify_push_destination()
            self.git(
                "fetch",
                "--no-tags",
                "origin",
                f"+{CAMPAIGN_QUEUE_REF}:{CAMPAIGN_QUEUE_REF}",
            )
            # Read the ref back rather than trusting the `ls-remote` answer: the
            # origin may have moved between the two, and the lease has to be
            # taken against the tree this operation is about to READ.
            remote = self.local_head()
            if remote is None:
                raise QueueError(
                    f"{ORIGIN_UNREACHABLE_REASON}: {CAMPAIGN_QUEUE_REF} was "
                    "fetched but is not readable afterwards"
                )
        self.base = remote
        # Re-extract when the ref moved, and ALSO when the cache no longer
        # matches what it held right after the last reset: a record written here
        # by hand, or a mutation an operation could not land, must not survive
        # into a scan just because the ref happened to stand still.
        drifted = self.state_fingerprint() != self.fingerprint
        if force or remote != self.cache_sha or drifted:
            self.reset_cache(remote)

    def discard(self) -> None:
        """Throw away a local mutation that never reached the ref."""
        self.refresh(force=True)

    def push(self, message: str) -> str:
        """Steps (d) and (e): commit the cache's state and CAS the origin's ref.

        Parameters
        ----------
        message : str
            Commit subject, naming the operation and the item it acted on.

        Returns
        -------
        str
            The commit the ref now points at.

        Raises
        ------
        AdmissionRaceLost
            If the lease failed, which means another host moved the ref.
        QueueError
            If the commit could not be built or the push could not be delivered.
        """
        # Before the commit is even built: this is the invocation the whole check
        # exists for, and a refusal here must leave the ref untouched.
        self.verify_push_destination()
        index = self.scratch / QUEUE_STATE_INDEX_NAME
        with contextlib.suppress(FileNotFoundError):
            index.unlink()
        environment = git_environment(GIT_INDEX_FILE=str(index))
        self.git("read-tree", "--empty", environment=environment)
        present = [
            path
            for path in QUEUE_TREE_PATHS
            if (self.cache / path).is_dir() or (self.cache / path).is_file()
        ]
        if present:
            self.git(
                "--work-tree",
                str(self.cache),
                "add",
                "--all",
                "--force",
                "--",
                *present,
                environment=environment,
            )
        tree = self.git("write-tree", environment=environment).stdout.strip()
        arguments = ["commit-tree", tree]
        if self.base is not None:
            arguments += ["-p", self.base]
        commit = self.git(
            *arguments, "-m", message, environment=self.author_environment()
        ).stdout.strip()
        if not GIT_OBJECT_RE.fullmatch(commit):
            raise QueueError(f"campaign queue commit-tree returned {commit!r}")
        # An absent ref leases against the EMPTY value, which git reads as "this
        # ref must not already exist".  Without that, the first push of a
        # campaign would be an unconditional create and two hosts starting at
        # once would each overwrite the other's first admission.
        lease = f"--force-with-lease={CAMPAIGN_QUEUE_REF}:{self.base or ''}"
        # The DESTINATION IS THE LITERAL PINNED STRING, not the remote name, so
        # that reading `remote.origin.pushurl` is not the only thing standing
        # between the lease and another repository.  Belt and braces: an
        # `url.<base>.pushInsteadOf` rewrites a command-line url too, which is
        # why the cleared environment and the configuration check above are the
        # load-bearing halves and this is the third.  The remote name stays for
        # the fetch, where the refspec is explicit and the answer is verified by
        # re-reading the ref.
        result = self.git(
            "push",
            self.scratch_origin,
            f"{commit}:{CAMPAIGN_QUEUE_REF}",
            lease,
            check=False,
        )
        if result.returncode != 0:
            output = result.stdout.strip()
            if any(marker in output for marker in PUSH_REJECTION_MARKERS):
                raise AdmissionRaceLost(
                    f"{RACE_LOST_REASON}: {CAMPAIGN_QUEUE_REF} moved away from "
                    f"{self.base or 'the empty value'} between this operation's "
                    f"fetch and its push, so {message!r} was computed against a "
                    f"state another host has replaced: {output}"
                )
            raise QueueError(
                f"cannot publish {message!r} to {CAMPAIGN_QUEUE_REF} at "
                f"{self.scratch_origin}: {output}"
            )
        self.git("update-ref", CAMPAIGN_QUEUE_REF, commit)
        self.base = commit
        self.cache_sha = commit
        self.fingerprint = self.state_fingerprint()
        return commit

    def flush_pending(self) -> list[str]:
        """Retry every record an earlier tick wrote but could not land.

        Retried in the order recorded, because a release only means anything
        after the outcome it releases.  A retry that loses the race or cannot be
        delivered leaves the record pending and the cache reset to the ref: the
        item stays claimed there and therefore keeps RESERVING on every host,
        which is the fail-closed direction and the reason an unpushed outcome
        releases nothing anywhere.
        """
        root = self.cache / QUEUE_PENDING_NAME
        if not root.is_dir():
            return []
        landed: list[str] = []
        for path in sorted(root.glob("*.json")):
            entry = read_object(path)
            family = require_text(entry.get("family"), field="pending family")
            item_id = require_text(entry.get("id"), field="pending id")
            message = require_text(entry.get("message"), field="pending message")
            record = entry.get("record")
            if family not in QUEUE_PENDING_FAMILIES or not isinstance(record, dict):
                raise QueueError(
                    f"pending campaign queue record is unmodelled: {path}"
                )
            validate_id(item_id)
            atomic_json(self.cache / family / f"{item_id}.json", record)
            try:
                self.push(message)
            except QueueError:
                # Including AdmissionRaceLost.  Neither forgotten nor believed:
                # the record stays here and the next operation tries again.
                self.discard()
                break
            path.unlink()
            landed.append(f"{family}/{item_id}")
        return landed

    def defer(self, family: str, item_id: str, record: dict, message: str) -> Path:
        """Set aside a record whose push did not land, and un-apply it locally."""
        if family not in QUEUE_PENDING_FAMILIES:
            raise QueueError(f"{family} records are not deferrable")
        root = self.cache / QUEUE_PENDING_NAME
        root.mkdir(parents=True, exist_ok=True)
        # A sequence, because order matters: a release means nothing before the
        # outcome it releases, and a millisecond clock could tie.
        sequences = []
        for path in sorted(root.glob("*.json")):
            match = QUEUE_PENDING_NAME_RE.fullmatch(path.name)
            if match is None:
                raise QueueError(
                    f"pending campaign queue record has an unmodelled name, so "
                    f"the retry order cannot be established: {path}"
                )
            sequences.append(int(match.group("sequence")))
        sequence = 1 + max(sequences, default=0)
        path = root / f"{sequence:06d}-{family}-{item_id}.json"
        atomic_json(
            path,
            {
                "schema_version": 1,
                "family": family,
                "id": item_id,
                "message": message,
                "recorded_at_utc": self.queue.clock(),
                "record": record,
            },
            exclusive=True,
        )
        try:
            self.discard()
        except QueueError:
            # The origin is very likely unreachable -- that is usually WHY the
            # push failed -- so the reset that would normally un-apply the record
            # is not available.  Un-apply it here instead: a read on this host
            # must not believe a record the campaign has never seen.  The next
            # successful refresh restores whatever the ref actually holds.
            with contextlib.suppress(FileNotFoundError):
                (self.cache / family / f"{item_id}.json").unlink()
        return path


@contextlib.contextmanager
def queue_operation(queue: Queue, message: str) -> Iterator[QueueSync]:
    """Run one queue operation as a compare-and-swap on the origin's queue ref.

    Under the local lock: fetch the ref, make the cache exactly its tree, retry
    anything an earlier tick left pending, run the operation, and -- only if the
    cached state actually changed -- commit and push with a lease against the
    fetched sha.  A rejected push discards the mutation, re-reads the ref, and
    raises :class:`AdmissionRaceLost`; nothing is ever merged.

    A NESTED operation is part of the outer one's single push.  That is what
    makes the admission window one push: the headroom scan and the claim it
    admits are computed against one fetched tree and land together or not at
    all, so two hosts cannot both claim against the same sha.

    Parameters
    ----------
    queue : Queue
        Queue whose cache and origin this operation acts on.
    message : str
        Commit subject naming the operation and its item.

    Yields
    ------
    QueueSync
        The channel, whose ``base`` is the sha this operation's lease is against.
    """
    sync = queue.sync()
    with sync.lock.held():
        if sync.depth > 0:
            sync.depth += 1
            try:
                yield sync
            finally:
                sync.depth -= 1
            return
        sync.depth += 1
        try:
            sync.refresh()
            sync.flush_pending()
            before = dict(sync.fingerprint)
            yield sync
            if sync.state_fingerprint() != before:
                sync.push(message)
        except BaseException:
            # Whatever went wrong, a mutation that did not land must not be left
            # where the next read would count it.  A discard that cannot reach
            # the origin is suppressed so the ORIGINAL refusal is the one raised.
            with contextlib.suppress(Exception):
                sync.discard()
            raise
        finally:
            sync.depth -= 1


def refresh_queue(queue: Queue) -> None:
    """Make the cache exactly the origin's queue tree, and retry what is pending.

    Every read of the queue's state is a read of the ORIGIN's tree: the ready
    set, the item states and the reservations that bound the R5 ceiling are
    properties of the campaign, not of the host that happens to be ticking.
    """
    with queue_operation(queue, f"refresh {CAMPAIGN_QUEUE_REF}"):
        pass


def commit_state_record(
    queue: Queue,
    family: str,
    item_id: str,
    record: dict,
    message: str,
    *,
    exclusive: bool = True,
) -> dict:
    """Write one deferrable state record and land it on the origin's queue ref.

    Outcomes, releases and revocations record something that ALREADY HAPPENED,
    so a push that does not land must not discard them: the record waits in the
    cache's pending area and every later operation retries it.  Until it lands
    the item stays claimed in the ref and keeps reserving on every host, so the
    conservative direction is the automatic one.  The returned copy then carries
    :data:`QUEUE_PUSH_PENDING_FIELD`, which is a property of this tick and is
    never written into the record itself.

    Returns
    -------
    dict
        The record, with ``queue_push_pending`` added when it has not landed.
    """
    sync = queue.sync()
    write_refused = False
    try:
        with queue_operation(queue, message):
            try:
                atomic_json(
                    queue.path(family, item_id), record, exclusive=exclusive
                )
            except QueueError:
                write_refused = True
                raise
    except QueueError as exc:
        if sync.depth or write_refused:
            # A refused WRITE is not retryable: the exclusive link found a record
            # already there, and a record that cannot be written now cannot be
            # written later either, so setting it aside would retry it at every
            # tick forever and report the tick unresolved rather than wrong.  A
            # failure anywhere else in the cycle -- an unreachable origin at the
            # fetch, a lost lease at the push -- IS retryable, and the record
            # describes something that already happened.  ``sync.depth`` means an
            # enclosing operation owns the push, so deferring here would set
            # aside a record it is still holding open.
            raise
        sync.defer(family, item_id, record, message)
        return {**record, QUEUE_PUSH_PENDING_FIELD: str(exc)}
    return record


def publish_cached_state(queue: Queue, message: str) -> str | None:
    """Land whatever the cache now holds, WITHOUT resetting it to the ref first.

    Every ordinary operation resets the cache before it acts, so a record placed
    in the cache by hand -- migrating an existing per-host queue into the ref, or
    repairing one after an operator edit -- would be deleted before it could be
    published.  This is the one entry point that publishes such a state, and it
    is still a compare-and-swap: it learns the ref's current sha, leases against
    it, and refuses on a race rather than overwriting another host's records.
    """
    sync = queue.sync()
    with sync.lock.held():
        origin = campaign_origin(queue)
        sync.ensure_scratch(origin["origin_url"])
        remote = sync.remote_head()
        if remote is not None and remote != sync.local_head():
            sync.verify_push_destination()
            sync.git(
                "fetch",
                "--no-tags",
                "origin",
                f"+{CAMPAIGN_QUEUE_REF}:{CAMPAIGN_QUEUE_REF}",
            )
            remote = sync.local_head()
        sync.base = remote
        if not sync.state_fingerprint():
            # Nothing local to publish.  Pushing an empty tree here would DELETE
            # whatever the ref holds, and creating the ref at an empty tree would
            # commit this host's emptiness as the campaign's state.
            return None
        return sync.push(message)


def require_queue_item(value: dict, path: Path) -> dict:
    """Return an item record after checking the fields every reader indexes.

    The queue tree crosses hosts, so a record here may have been written by a
    campaignctl that is not this one.  A missing field is a refusal naming the
    file: the alternative is a ``KeyError`` from inside a reservation scan, which
    reads as a crash rather than as "this queue cannot be scanned right now".
    """
    missing = [field for field in QUEUE_ITEM_REQUIRED_FIELDS if field not in value]
    if missing:
        raise QueueError(
            f"queue item record is missing required field(s) "
            f"{', '.join(missing)}: {path}"
        )
    return value


def validate_id(value: str) -> None:
    if not ID_RE.fullmatch(value):
        raise QueueError(f"invalid item id: {value!r}")


def resolve_repo_path(repo: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = repo / path
    return inside(path, repo)


def validate_guarded_argv(repo: Path, argv: list[str], *, role: str) -> None:
    """Require the production form of an OI-136 guard command.

    The guard decides which tree an interpreter may import from, so its own
    argument vector decides what it will accept.  ``--allow`` widens that set to
    another checkout and the guard's header says it is forbidden outright on a
    production arm; an ``--expect-root`` naming a foreign tree makes the guard's
    positive control pass for the wrong tree; and ``-S``/``-I``/``-E`` or a
    ``PYTHON...=`` element rewrites import resolution before the guard is even
    installed.  Each of those turns a green guard into no guard at all, so a
    compute arm is refused for carrying any of them rather than trusted to have
    meant something harmless.

    Parameters
    ----------
    repo : Path
        Resolved repository root the arm belongs to.
    argv : list[str]
        Complete guard argument vector, including everything after ``--``.
    role : str
        Name of the command's role, used in refusal messages so a producer
        refusal and a terminal-validator refusal are distinguishable.

    Raises
    ------
    QueueError
        If ``--allow``, a forbidden interpreter flag or a ``PYTHON...=`` element
        is present, or if exactly one ``--expect-root`` naming ``repo`` by
        absolute path does not precede the mandatory ``--``.
    """
    for element in argv:
        if element == ALLOW_FLAG or element.startswith(f"{ALLOW_FLAG}="):
            raise QueueError(
                f"guarded {role} command must not carry --allow: it declares an "
                "import tree from another checkout and is forbidden on a "
                "production arm"
            )
        if SHORT_FLAG_RE.fullmatch(element) and FORBIDDEN_INTERPRETER_LETTERS.intersection(
            element[1:]
        ):
            raise QueueError(
                f"guarded {role} command must not carry the interpreter flag "
                f"{element}: it changes import resolution the guard is measuring"
            )
        if element.startswith("PYTHON") and "=" in element:
            raise QueueError(
                f"guarded {role} command must not set a PYTHON environment "
                f"variable in argv: {element}"
            )
    head = argv[: argv.index("--")] if "--" in argv else list(argv)
    named: list[str] = []
    index = 0
    while index < len(head):
        element = head[index]
        if element == EXPECT_ROOT_FLAG:
            if index + 1 >= len(head):
                raise QueueError(
                    f"guarded {role} command requires a value after --expect-root"
                )
            named.append(head[index + 1])
            index += 2
            continue
        if element.startswith(f"{EXPECT_ROOT_FLAG}="):
            named.append(element.split("=", 1)[1])
            index += 1
            continue
        index += 1
    if len(named) != 1:
        raise QueueError(
            f"guarded {role} command must pass exactly one --expect-root before "
            f"'--', naming the queue repository root {repo}"
        )
    expect_root = Path(named[0])
    if not expect_root.is_absolute() or expect_root.resolve() != repo:
        raise QueueError(
            f"guarded {role} command must pass --expect-root {repo}, not "
            f"{named[0]}"
        )


def command_bindings(
    repo: Path,
    argv: list[str],
    explicit: list[str],
    *,
    require_guard: bool = False,
    role: str = "compute producer",
) -> list[dict[str, str]]:
    """Resolve one command to repository paths and return its file bindings.

    Parameters
    ----------
    repo : Path
        Repository root every resolved path must lie inside.
    argv : list[str]
        Argument vector, rewritten in place with resolved absolute paths.
    explicit : list[str]
        Additional repository files to bind.
    require_guard : bool, optional
        Require the command to route through ``nd-unfolding/mnv_guarded_run.py``
        in its production form (see :func:`validate_guarded_argv`) and bind the
        guarded target after the mandatory ``--`` together with the guard's
        subprocess shim ``nd-unfolding/mnv_guard_shim/sitecustomize.py``.
    role : str, optional
        Name of the command's role, used in guard refusal messages so a producer
        refusal and a terminal-validator refusal are distinguishable.

    Returns
    -------
    list[dict[str, str]]
        One ``{"path", "sha256"}`` binding per bound file, ordered by path.

    Raises
    ------
    QueueError
        If a path escapes the repository or a guard rule is not satisfied.
    """
    require_argv(argv, field="command")
    executable = Path(argv[0])
    bound: list[Path] = []
    if executable.resolve() in ALLOWED_PYTHONS:
        if len(argv) < 2 or argv[1].startswith("-"):
            raise QueueError("python commands must name a repository .py file")
        script = resolve_repo_path(repo, argv[1])
        if script.suffix != ".py" or not script.is_file():
            raise QueueError(f"python target is not a repository .py file: {script}")
        argv[1] = str(script)
        bound.append(script)
    else:
        executable = resolve_repo_path(repo, argv[0])
        if not executable.is_file() or not os.access(executable, os.X_OK):
            raise QueueError(
                f"command is not an executable repository file: {executable}"
            )
        argv[0] = str(executable)
        bound.append(executable)
    if require_guard:
        guard = (repo / GUARD_PATH).resolve()
        command_file_index = 1 if Path(argv[0]).resolve() in ALLOWED_PYTHONS else 0
        if Path(argv[command_file_index]).resolve() != guard:
            raise QueueError(
                f"{role} must route through nd-unfolding/mnv_guarded_run.py"
            )
        validate_guarded_argv(repo, argv, role=role)
        try:
            separator_index = argv.index("--", command_file_index + 1)
        except ValueError as exc:
            raise QueueError(
                f"guarded {role} command requires '-- <script>'"
            ) from exc
        if separator_index + 1 >= len(argv):
            raise QueueError(
                f"guarded {role} command requires a target script after '--'"
            )
        target = resolve_repo_path(repo, argv[separator_index + 1])
        if target.suffix != ".py" or not target.is_file():
            raise QueueError(f"guarded target is not a repository .py file: {target}")
        argv[separator_index + 1] = str(target)
        bound.append(target)
        # The shim is the guard's other half, not one of its inputs.  `install()`
        # prepends its directory to PYTHONPATH and every inheriting Python child
        # loads the guard through it, so a child's guard is whatever bytes are at
        # this path when the child starts.  Bound here, it obeys the guard's own
        # rules -- tracked, HEAD-identical at staging, re-verified before execution
        # -- and swapping only the shim can no longer send a child to another tree.
        for shim_path in GUARD_SHIM_PATHS:
            shim = (repo / shim_path).resolve()
            if not shim.is_file():
                raise QueueError(
                    f"guarded {role} command requires the guard's subprocess shim "
                    f"{shim_path.as_posix()}, which is how the guard reaches "
                    "inheriting Python children and PATH-resolved interpreters"
                )
            bound.append(shim)
    for value in explicit:
        path = resolve_repo_path(repo, value)
        if not path.is_file():
            raise QueueError(f"bound input is not a file: {path}")
        bound.append(path)
    unique = sorted(set(bound), key=lambda p: str(p))
    return [
        {"path": str(path.relative_to(repo)), "sha256": sha256_file(path)}
        for path in unique
    ]


def merge_bindings(*binding_groups: list[dict[str, str]]) -> list[dict[str, str]]:
    """Merge command binding groups while requiring identical repeated hashes."""
    merged: dict[str, str] = {}
    for bindings in binding_groups:
        for binding in bindings:
            previous = merged.setdefault(binding["path"], binding["sha256"])
            if previous != binding["sha256"]:
                raise QueueError(f"inconsistent binding hash: {binding['path']}")
    return [
        {"path": path, "sha256": merged[path]}
        for path in sorted(merged)
    ]


def proposal_payload(item: dict) -> dict:
    keys = (
        "schema_version", "id", "description", "kind", "argv", "cwd",
        "depends_on", "bindings", "repo_path", "git_head", "timeout_seconds",
    )
    payload = {key: item[key] for key in keys}
    for key in ("campaign_contract_path", "campaign_contract"):
        if key in item:
            payload[key] = item[key]
    return payload


def stage(
    queue: Queue,
    item_id: str,
    description: str,
    kind: str,
    cwd: str,
    depends_on: list[str],
    bind: list[str],
    argv: list[str],
    timeout_seconds: int,
    campaign_contract: str | None = None,
) -> dict:
    with queue_operation(queue, f"stage {item_id}"):
        return _stage(
            queue,
            item_id,
            description,
            kind,
            cwd,
            depends_on,
            bind,
            argv,
            timeout_seconds,
            campaign_contract,
        )


def _stage(
    queue: Queue,
    item_id: str,
    description: str,
    kind: str,
    cwd: str,
    depends_on: list[str],
    bind: list[str],
    argv: list[str],
    timeout_seconds: int,
    campaign_contract: str | None = None,
) -> dict:
    """Stage one item into the fetched queue tree, under the caller's operation."""
    validate_id(item_id)
    if not description.strip():
        raise QueueError("description is required")
    if timeout_seconds < 1 or timeout_seconds > 3600:
        raise QueueError("timeout must be between 1 and 3600 seconds")
    for dependency in depends_on:
        validate_id(dependency)
        if dependency == item_id:
            raise QueueError("an item cannot depend on itself")
        queue.item(dependency)

    contract: dict[str, object] | None = None
    contract_path: Path | None = None
    if campaign_contract is None:
        if kind == "compute":
            raise QueueError("compute items require a committed campaign contract")
    else:
        contract_path = resolve_repo_path(queue.repo, campaign_contract)
        if not contract_path.is_file():
            raise QueueError(f"campaign contract is not a file: {contract_path}")
        contract = validate_campaign_contract(
            read_object(contract_path), expected_campaign_id=item_id
        )
        committed_sha256 = queue.committed_file_sha256(contract_path)
        if sha256_file(contract_path) != committed_sha256:
            raise QueueError(
                "campaign contract differs from the file committed at HEAD"
            )

    command = list(argv)
    if command and command[0] == "--":
        command = command[1:]
    bound_inputs = list(bind)
    if contract_path is not None:
        bound_inputs.append(str(contract_path))
    bindings = command_bindings(
        queue.repo,
        command,
        bound_inputs,
        require_guard=kind == "compute",
    )
    if contract is not None:
        terminal_validator = contract["terminal_validator"]
        if not isinstance(terminal_validator, dict):
            raise QueueError("validated campaign contract lost terminal_validator")
        validator_command = list(
            require_argv(
                terminal_validator["argv"], field="terminal_validator.argv"
            )
        )
        # The validator alone resolves the terminal branch, so it is the LAST place
        # that may import its decisive logic from another tree.  It therefore routes
        # through the guard under exactly the producer's rules: guarded, committed at
        # HEAD, working-tree identical, and bound.
        validator_bindings = command_bindings(
            queue.repo,
            validator_command,
            [],
            require_guard=kind == "compute",
            role="compute terminal validator",
        )
        bindings = merge_bindings(bindings, validator_bindings)
        validator_cwd = resolve_repo_path(
            queue.repo,
            require_text(terminal_validator["cwd"], field="terminal_validator.cwd"),
        )
        if not validator_cwd.is_dir():
            raise QueueError(
                f"terminal validator cwd is not a directory: {validator_cwd}"
            )
        if kind == "compute":
            maximum_cost = contract["maximum_cost"]
            if not isinstance(maximum_cost, dict):
                raise QueueError("validated campaign contract lost maximum_cost")
            maximum_wall_seconds = float(maximum_cost["wall_hours"]) * 3600
            if timeout_seconds > maximum_wall_seconds:
                # The wall budget is shared by the producer and the validator, so a
                # staged per-command timeout larger than the whole budget could never
                # be honoured by either command.
                raise QueueError(
                    "staged timeout exceeds maximum_cost.wall_hours, which is the "
                    "single deadline the producer and terminal validator share"
                )
    if kind == "compute":
        for binding in bindings:
            queue.require_committed_binding(binding)
    cwd_path = resolve_repo_path(queue.repo, cwd)
    if not cwd_path.is_dir():
        raise QueueError(f"cwd is not a directory: {cwd_path}")
    item = {
        "schema_version": 1,
        "id": item_id,
        "description": description.strip(),
        "kind": kind,
        "argv": command,
        "cwd": str(cwd_path.relative_to(queue.repo)) or ".",
        "depends_on": sorted(set(depends_on)),
        "bindings": bindings,
        # The queue is campaign-global, so an item has to say which checkout its
        # bindings, cwd and HEAD are properties of.  Only a ticker in that
        # repository can validate them; every other ticker still counts the item's
        # reservation and lists it.
        "repo_path": str(queue.repo),
        "git_head": queue.git_head(),
        "timeout_seconds": timeout_seconds,
        "created_at_utc": queue.clock(),
        "created_by": f"{os.environ.get('USER', 'unknown')}@{socket.gethostname()}",
    }
    if contract is not None and contract_path is not None:
        item["campaign_contract_path"] = str(contract_path.relative_to(queue.repo))
        item["campaign_contract"] = contract
    item["proposal_digest"] = digest(proposal_payload(item))
    atomic_json(queue.path("items", item_id), item, exclusive=True)
    return item


def item_repo_path(item: dict) -> str | None:
    """Return the checkout an item was staged from, or ``None`` when unrecorded."""
    value = item.get("repo_path")
    return value if isinstance(value, str) and value.strip() else None


def runs_in_this_repo(queue: Queue, item: dict) -> bool:
    """Report whether ``queue`` is the checkout that may execute ``item``.

    An item with no recorded ``repo_path`` is NOT this repository's: it predates
    the campaign-global queue, so nothing says which bindings its hashes were
    taken from.  Failing closed leaves it reserving and listed, which is the
    conservative half; the alternative would let any ticker validate another
    checkout's bindings against its own files.
    """
    recorded = item_repo_path(item)
    if recorded is None:
        return False
    return Path(recorded).resolve() == queue.repo


def validate_unchanged(queue: Queue, item: dict) -> None:
    expected = item.get("proposal_digest")
    if item_repo_path(item) is None:
        raise QueueError(
            "item does not record the checkout it was staged from, so its "
            "bindings cannot be attributed to a repository"
        )
    if expected != digest(proposal_payload(item)):
        raise QueueError("proposal JSON does not match its digest")
    if not runs_in_this_repo(queue, item):
        raise QueueError(
            f"{FOREIGN_ITEM_REASON}: {item_repo_path(item)}, while this queue "
            f"serves {queue.repo}"
        )
    if queue.git_head() != item["git_head"]:
        raise QueueError("repository HEAD changed after staging")
    contract = item.get("campaign_contract")
    if item.get("kind") == "compute" and not isinstance(contract, dict):
        raise QueueError("compute items require a committed campaign contract")
    if contract is not None:
        if not isinstance(contract, dict):
            raise QueueError("embedded campaign contract must be an object")
        validate_campaign_contract(contract, expected_campaign_id=item["id"])
        if item.get("kind") == "compute":
            # The guard argv is re-checked here and not only at staging: the item
            # JSON lives in the state directory, outside Git, so a hand-edited argv
            # with a recomputed digest reaches the claim without passing staging
            # again.  This runs BEFORE the binding comparison so an argv carrying
            # --allow is refused for what it is, not for a hash that happens to
            # have moved with it.
            validate_guarded_argv(
                queue.repo, list(item["argv"]), role="compute producer"
            )
            terminal_validator = contract["terminal_validator"]
            if not isinstance(terminal_validator, dict):
                raise QueueError("validated campaign contract lost terminal_validator")
            validate_guarded_argv(
                queue.repo,
                require_argv(
                    terminal_validator["argv"], field="terminal_validator.argv"
                ),
                role="compute terminal validator",
            )
        contract_path = item.get("campaign_contract_path")
        if not isinstance(contract_path, str):
            raise QueueError("campaign contract path is missing")
        if read_object(resolve_repo_path(queue.repo, contract_path)) != contract:
            raise QueueError("embedded campaign contract differs from its bound file")
    committed = (
        queue.committed_file_sha256_many([b["path"] for b in item["bindings"]])
        if item.get("kind") == "compute"
        else {}
    )
    for binding in item["bindings"]:
        path = resolve_repo_path(queue.repo, binding["path"])
        if not path.is_file() or sha256_file(path) != binding["sha256"]:
            raise QueueError(f"bound file changed after staging: {binding['path']}")
        if item.get("kind") == "compute":
            queue.require_committed_binding(binding, committed=committed)


def validate_r5_receipt(value: object) -> dict[str, object]:
    """Validate the complete R5 meter receipt and its internal accounting."""
    receipt = require_object(value, field="R5 meter receipt", keys=R5_RECEIPT_KEYS)
    if receipt["schema_version"] != 1:
        raise QueueError("R5 meter receipt schema_version must be 1")
    decision_record = require_text(
        receipt["decision_record"], field="R5 meter decision_record"
    )
    t0 = parse_utc(receipt["t0_utc"], field="R5 meter t0_utc")
    stop_date = parse_utc(
        receipt["stop_date_utc"], field="R5 meter stop_date_utc"
    )
    measured_at = parse_utc(
        receipt["measured_at_utc"], field="R5 meter measured_at_utc"
    )
    if decision_record != R5_DECISION_RECORD:
        raise QueueError(
            "R5 meter decision_record does not match the ruling record"
        )
    if t0 != R5_T0:
        raise QueueError("R5 meter t0_utc does not match the ruled instant")
    if stop_date != R5_STOP_DATE:
        raise QueueError("R5 meter stop_date_utc does not match the ruled stop")
    if measured_at < t0:
        raise QueueError("R5 meter measured_at_utc precedes t0_utc")

    ceilings = require_object(
        receipt["ceilings"],
        field="R5 meter ceilings",
        keys=MAXIMUM_COST_KEYS - {"wall_hours"},
    )
    spend = require_object(
        receipt["spend"], field="R5 meter spend", keys=R5_SPEND_KEYS
    )
    headroom = require_object(
        receipt["headroom"],
        field="R5 meter headroom",
        keys=MAXIMUM_COST_KEYS - {"wall_hours"},
    )
    for resource, ruled_ceiling in R5_CEILINGS.items():
        ceiling = require_nonnegative_number(
            ceilings[resource], field=f"R5 meter ceilings.{resource}"
        )
        spent = require_nonnegative_number(
            spend[resource], field=f"R5 meter spend.{resource}"
        )
        remaining = require_finite_number(
            headroom[resource], field=f"R5 meter headroom.{resource}"
        )
        if ceiling != ruled_ceiling:
            raise QueueError(
                f"R5 meter ceilings.{resource} does not match the ruled ceiling"
            )
        if not math.isclose(remaining, ceiling - spent, abs_tol=1e-9):
            raise QueueError(
                f"R5 meter headroom.{resource} is inconsistent with spend"
            )

    unit = require_text(receipt["unit"], field="R5 meter unit")
    # r5_meter.py writes the unit token followed by its definition ("task-hours: sum of
    # ElapsedRaw over distinct task identities; ..."); only the token is load-bearing here.
    if unit != "task-hours" and not unit.startswith("task-hours:"):
        raise QueueError("R5 meter unit must be 'task-hours'")
    require_text(receipt["measured_on_host"], field="R5 meter measured_on_host")
    source = require_object(
        receipt["source"], field="R5 meter source", keys=R5_SOURCE_KEYS
    )
    require_text(source["kind"], field="R5 meter source.kind")
    argv_or_path = source["argv_or_path"]
    if isinstance(argv_or_path, list):
        require_argv(argv_or_path, field="R5 meter source.argv_or_path")
    else:
        require_text(argv_or_path, field="R5 meter source.argv_or_path")
    raw_sha256 = require_text(
        source["raw_sha256"], field="R5 meter source.raw_sha256"
    )
    if not SHA256_RE.fullmatch(raw_sha256):
        raise QueueError(
            "R5 meter source.raw_sha256 must be 64 lowercase hexadecimal characters"
        )

    task_count = spend["task_count"]
    if (
        isinstance(task_count, bool)
        or not isinstance(task_count, int)
        or task_count < 0
    ):
        raise QueueError("R5 meter spend.task_count must be a nonnegative integer")
    metered_task_ids = require_text_list(
        spend["metered_task_ids"], field="R5 meter spend.metered_task_ids"
    )
    if len(metered_task_ids) != task_count:
        raise QueueError("R5 meter spend.task_count does not match metered_task_ids")
    by_state = spend["by_state"]
    if not isinstance(by_state, dict) or not all(
        isinstance(state, str)
        and state
        and isinstance(count, int)
        and not isinstance(count, bool)
        and count >= 0
        for state, count in by_state.items()
    ):
        raise QueueError(
            "R5 meter spend.by_state must map state names to nonnegative integers"
        )
    if sum(by_state.values()) != task_count:
        raise QueueError("R5 meter spend.by_state does not sum to task_count")

    fired = require_object(
        receipt["fired"], field="R5 meter fired", keys=R5_FIRED_KEYS
    )
    if any(not isinstance(fired[key], bool) for key in R5_FIRED_KEYS):
        raise QueueError("R5 meter fired fields must be booleans")
    if fired["any"] != (fired["date"] or fired["gpu"] or fired["cpu"]):
        raise QueueError("R5 meter fired.any is inconsistent with trigger fields")
    return receipt


def committed_file_identity(
    queue: Queue,
    relative: Path,
    *,
    missing_label: str,
    uncommitted_reason: str,
) -> tuple[Path, str, str]:
    """Return a worktree file and its blob SHA when both match ``HEAD``.

    This is the single identity check for evidence and decision records.  A
    second implementation could drift until one path accepted uncommitted bytes
    that the other refused.
    """
    if relative.is_absolute():
        raise QueueError(
            f"{uncommitted_reason}: path must be repository-relative, not {relative}"
        )
    try:
        path = resolve_repo_path(queue.repo, relative.as_posix())
    except QueueError as exc:
        raise QueueError(f"{uncommitted_reason}: {exc}") from exc
    if not path.is_file():
        raise QueueError(f"{missing_label} missing: {path}")
    head = queue.git_head()
    try:
        committed_sha256 = queue.committed_file_sha256(path)
    except QueueError as exc:
        raise QueueError(
            f"{uncommitted_reason}: {relative.as_posix()} is not tracked at "
            "the repository HEAD"
        ) from exc
    if sha256_file(path) != committed_sha256:
        raise QueueError(
            f"{uncommitted_reason}: {relative.as_posix()} differs from the blob "
            "committed at HEAD"
        )
    if queue.git_head() != head:
        raise QueueError(f"{uncommitted_reason}: repository HEAD changed during check")
    return path, committed_sha256, head


def committed_r5_receipt(queue: Queue) -> tuple[Path | None, str | None]:
    """Locate the R5 receipt and require it to be committed at ``HEAD``.

    ``CAMPAIGN_R5_RECEIPT`` may override only the REPOSITORY-RELATIVE path, so a
    test can commit a receipt inside its own temporary repository.  It cannot
    point the queue at a file the repository does not record: an absolute path,
    a path outside the checkout, an untracked file and a working-tree edit made
    after the commit are all refusals, because none of them is evidence anybody
    else can re-read.

    Parameters
    ----------
    queue : Queue
        Queue whose repository root and ``HEAD`` bound the receipt.

    Returns
    -------
    tuple[Path or None, str or None]
        The resolved receipt path and ``None``, or ``None`` and the refusal
        reason.
    """
    override = os.environ.get("CAMPAIGN_R5_RECEIPT")
    relative = DEFAULT_R5_RECEIPT if override is None else Path(override)
    try:
        receipt_path, _, _ = committed_file_identity(
            queue,
            relative,
            missing_label="R5 receipt",
            uncommitted_reason=R5_UNCOMMITTED_REASON,
        )
    except QueueError as exc:
        return None, str(exc)
    return receipt_path, None


def terminal_outcome_instant(queue: Queue, item_id: str) -> dt.datetime:
    """Return the instant a queue item's terminal outcome was recorded.

    Raises
    ------
    QueueError
        If the outcome cannot be read or carries no parseable
        ``completed_at_utc``.  Refusing beats guessing: an undated terminal
        outcome must not read as "old enough that the meter has seen it", so the
        refusal is loud and names the item rather than releasing its hours.
    """
    outcome = read_object(queue.path("outcomes", item_id))
    return parse_utc(
        outcome.get(OUTCOME_INSTANT_FIELD),
        field=f"outcome {item_id} {OUTCOME_INSTANT_FIELD}",
    )


def outcome_task_ids(queue: Queue, item_id: str) -> list[str] | None:
    """Return the scheduler task identities an outcome recorded, or ``None``.

    ``None`` is not an empty list.  ``[]`` is a MEASUREMENT -- the producer wrote
    its task-ids file and it held no tasks, which a contract may declare with
    ``expects_scheduler_tasks`` false -- while ``None`` means nothing was ever
    recorded, so no receipt can demonstrate that this item's spend was counted.
    The two are released by different acts, so they must not collapse.

    Raises
    ------
    QueueError
        If the recorded value is present but is not a list of task identities.
        A malformed field must not read as "no ids", which releases on a
        timestamp alone.
    """
    outcome = read_object(queue.path("outcomes", item_id))
    if OUTCOME_TASK_IDS_FIELD not in outcome:
        return None
    task_ids = require_text_list(
        outcome[OUTCOME_TASK_IDS_FIELD],
        field=f"outcome {item_id} {OUTCOME_TASK_IDS_FIELD}",
    )
    for task_id in task_ids:
        if not TASK_ID_RE.fullmatch(task_id):
            raise QueueError(
                f"outcome {item_id} {OUTCOME_TASK_IDS_FIELD} contains a value "
                f"that is not a scheduler task identity: {task_id}"
            )
    return task_ids


def expects_scheduler_tasks(item: dict) -> bool:
    """Report whether ``item``'s contract declares that it schedules tasks.

    Fails CLOSED at ``True``: an item whose declaration cannot be read must be
    treated as one whose spend has to be demonstrated in a receipt, never as one
    that releases on a timestamp alone.
    """
    contract = item.get("campaign_contract")
    if not isinstance(contract, dict):
        return True
    accounting = contract.get("accounting")
    if not isinstance(accounting, dict):
        return True
    declared = accounting.get("expects_scheduler_tasks")
    return True if not isinstance(declared, bool) else declared


def reservation_hold(
    queue: Queue, item: dict, accounting: ReceiptAccounting
) -> str | None:
    """Return why ``item`` still reserves its declared task-hours, or ``None``.

    A reservation is released by COUNTED SPEND, not by finishing and not by a
    later timestamp.  R5 §3 counts a failed, cancelled or timed-out task in full
    and lets jobs running at the stop run to completion with their spend counted,
    so the hours an item consumed are real from the moment it was claimed.  An
    item that reached a terminal outcome by RUNNING therefore keeps its full
    declared maximum reserved until a committed receipt

    * is measured strictly LATER than that item's outcome -- the meter had the
      chance to see the spend -- AND
    * lists EVERY scheduler task identity the item recorded in
      ``spend.metered_task_ids`` -- the meter demonstrably DID see it.

    The second clause is the reviewer's mutation: a receipt measured after the
    outcome, still reporting 490 GPU task-hours and listing none of the item's
    tasks, satisfies the timestamp and proves only that a query ran.  An item
    whose contract declares ``expects_scheduler_tasks`` false schedules nothing,
    so there is no identity to look for and the timestamp is the whole test.  An
    item that ran and recorded NO ids at all can never satisfy the second clause,
    so it reserves permanently until an operator releases it -- see
    :func:`release`.  An item that never ran has no claim, so refused, stale,
    revoked and never-claimed items release at once.

    Parameters
    ----------
    queue : Queue
        Queue whose claims, outcomes and release records date the item.
    item : dict
        Compute item whose reservation is being classified.
    accounting : ReceiptAccounting
        What the committed receipt admission is checking against proves: when it
        was measured, and which task identities it counted.

    Returns
    -------
    str or None
        A short reason the reservation is held, used verbatim in the refusal so
        the held hours are attributable; ``None`` when the item releases.
    """
    state = state_of(queue, item)
    if state in RESERVING_STATES:
        return state
    item_id = str(item["id"])
    if not queue.path("claims", item_id).exists():
        return None
    if queue.path("releases", item_id).exists():
        return None
    if accounting.measured_at <= terminal_outcome_instant(queue, item_id):
        return UNREMEASURED_HOLD
    task_ids = outcome_task_ids(queue, item_id)
    if task_ids is None:
        return UNIDENTIFIED_HOLD
    if not expects_scheduler_tasks(item):
        return None
    uncounted = sorted(set(task_ids) - accounting.metered_task_ids)
    if uncounted:
        return f"{UNCOUNTED_HOLD}: {', '.join(uncounted)}"
    return None


def reserved_task_hours(
    queue: Queue, item: dict, accounting: ReceiptAccounting
) -> tuple[dict[str, float], list[str]]:
    """Sum the task-hours other compute items hold in reserve.

    A ceiling is a property of the whole queue, not of one item.  Checking only
    ``spend + this item`` lets each of two items pass while their combined
    projection is over the ceiling, so every other compute item that
    :func:`reservation_hold` still holds reserves its full declared
    ``maximum_cost`` here.  The scan covers the campaign-global queue, so an item
    staged from ANOTHER checkout reserves here too even though no ticker in this
    repository will ever run it.  When the total reservation leaves no headroom
    the refusal is retryable and applies to every affected item: releasing it is a
    human act -- revoke an item, release one whose spend can never be identified,
    or meter and commit a receipt that lists its task ids -- and never something a
    tick decides for itself.

    Parameters
    ----------
    queue : Queue
        Queue whose items, claims and outcome records define the current states.
    item : dict
        Item being admitted, excluded from its own reservation total.
    accounting : ReceiptAccounting
        What the committed receipt admission is checking against proves, which is
        what releases a finished item's reservation.

    Returns
    -------
    tuple[dict[str, float], list[str]]
        Reserved task-hours per metered resource, and the sorted holders, each
        given as ``"<id> (<reason>)"``.
    """
    reservations = {resource: 0.0 for resource in R5_METERED_RESOURCES}
    reserving: list[str] = []
    for other in queue.items():
        if other.get("id") == item["id"] or other.get("kind") != "compute":
            continue
        contract = other.get("campaign_contract")
        if not isinstance(contract, dict):
            continue
        maximum_cost = contract.get("maximum_cost")
        if not isinstance(maximum_cost, dict):
            continue
        hold = reservation_hold(queue, other, accounting)
        if hold is None:
            continue
        for resource in R5_METERED_RESOURCES:
            if resource not in maximum_cost:
                # Refusing beats under-reserving: an item whose declared cost cannot
                # be read must not pass as an item that reserves nothing.
                raise QueueError(
                    f"queue item {other['id']} has no maximum_cost.{resource} to "
                    "reserve against the R5 ceiling"
                )
            reservations[resource] += require_nonnegative_number(
                maximum_cost[resource], field=f"maximum_cost.{resource}"
            )
        reserving.append(f"{other['id']} ({hold})")
    return reservations, sorted(reserving)


def non_canonical_state_refusal(queue: Queue) -> str | None:
    """Return the refusal for a queue that may not admit compute, or ``None``.

    The admission lock, the reservation inventory and the R5 headroom check are
    all properties of ONE state directory.  Two queues in different directories
    read the same committed receipt, take separate locks, scan separate
    inventories, and each admit an item the other never counted -- the reviewer's
    mutation, reached first by two ``--state-dir`` values and then by two CLONES
    of one repository, each with a queue of its own inside it.  That is why the
    canonical directory is a property of the host and the campaign rather than of
    a checkout: every clone and linked worktree resolves the same one.  Compute
    admission is possible only from there; a queue elsewhere may still stage,
    approve and run non-compute items.
    """
    if queue.state_is_canonical():
        return None
    return (
        f"{NON_CANONICAL_STATE_REASON}: the lock and the reservation inventory "
        f"are properties of {queue.canonical_state}, not of {queue.state}"
    )


def r5_refusal_reason(queue: Queue, item: dict) -> str | None:
    """Return the compute-prohibition reason, or ``None`` when R5 permits a run."""
    # First, because a headroom answer computed from a partial inventory is not a
    # weaker answer, it is a different question.  This queue can only count the
    # reservations its own state directory holds.
    non_canonical = non_canonical_state_refusal(queue)
    if non_canonical is not None:
        return non_canonical
    receipt_path, refusal = committed_r5_receipt(queue)
    if receipt_path is None:
        return refusal
    try:
        receipt = validate_r5_receipt(read_object(receipt_path))
    except QueueError as exc:
        return f"R5 receipt malformed: {exc}"

    now = parse_utc(queue.clock(), field="queue clock")
    measured_at = parse_utc(
        receipt["measured_at_utc"], field="R5 meter measured_at_utc"
    )
    # Freshness is bounded on BOTH sides.  An age-only bound waves through a receipt
    # dated after the queue clock, which is the one direction in which a stale
    # measurement can be made to look permanently fresh.
    if measured_at - now > R5_MAX_FUTURE_SKEW:
        return (
            "receipt is dated in the future: measured_at_utc is later than the "
            "queue clock"
        )
    if now - measured_at > R5_MAX_AGE:
        return "R5 receipt stale: measured_at_utc is older than 24 hours"

    fired = receipt["fired"]
    if not isinstance(fired, dict):
        raise QueueError("validated R5 receipt lost fired")
    if fired["any"] is True:
        return "R5 stop fired: receipt fired.any is true"
    stop_date = parse_utc(
        receipt["stop_date_utc"], field="R5 meter stop_date_utc"
    )
    if now >= stop_date:
        return "R5 stop date reached: queue clock is at or after stop_date_utc"

    spend = receipt["spend"]
    ceilings = receipt["ceilings"]
    contract = item["campaign_contract"]
    if not all(isinstance(value, dict) for value in (spend, ceilings, contract)):
        raise QueueError("validated compute item lost R5 accounting fields")
    maximum_cost = contract["maximum_cost"]
    if not isinstance(maximum_cost, dict):
        raise QueueError("validated campaign contract lost maximum_cost")
    metered_task_ids = spend["metered_task_ids"]
    if not isinstance(metered_task_ids, list):
        raise QueueError("validated R5 receipt lost spend.metered_task_ids")
    reservations, reserving = reserved_task_hours(
        queue,
        item,
        ReceiptAccounting(
            measured_at=measured_at,
            metered_task_ids=frozenset(str(value) for value in metered_task_ids),
        ),
    )
    for resource in R5_METERED_RESOURCES:
        spent = float(spend[resource])
        reserved = reservations[resource]
        declared = float(maximum_cost[resource])
        ceiling = float(ceilings[resource])
        if spent + reserved + declared >= ceiling:
            held = (
                "; reserved by " + ", ".join(reserving)
                if reserving
                else "; no other item holds a reservation"
            )
            return (
                f"R5 {resource} ceiling would be reached: spend plus reservations "
                "plus maximum_cost is greater than or equal to the ceiling "
                f"({spent:g} + {reserved:g} + {declared:g} >= {ceiling:g}){held}"
            )
    return None


def state_of(queue: Queue, item: dict) -> str:
    item_id = item["id"]
    outcome_path = queue.path("outcomes", item_id)
    if outcome_path.exists():
        outcome_status = str(read_object(outcome_path).get("status", "outcome"))
        if outcome_status != "refused":
            return outcome_status
    if queue.path("claims", item_id).exists():
        return "outcome-unknown"
    if queue.path("revocations", item_id).exists():
        return "revoked"
    if outcome_path.exists():
        return "refused"
    if queue.path("approvals", item_id).exists():
        return "approved"
    return "staged"


def summary(queue: Queue) -> dict:
    """Report every item in the campaign-global queue, whose ever it is.

    An item staged from another checkout is LISTED here and counted in the state
    tally, because it holds a reservation this queue's headroom check enforces.
    ``runs_here`` says whether a ticker in this repository may execute it, so a
    reader can tell "waiting for me" from "waiting for another checkout" without
    inferring it from a path.
    """
    refresh_queue(queue)
    values = {"staged": 0, "approved": 0, "succeeded": 0, "failed": 0,
              "refused": 0, "stale": 0, "revoked": 0, "outcome-unknown": 0}
    rows = []
    for item in queue.items():
        state = state_of(queue, item)
        values[state] = values.get(state, 0) + 1
        rows.append(
            {
                "id": item["id"],
                "state": state,
                "digest": item["proposal_digest"],
                "repo_path": item_repo_path(item) or "",
                "runs_here": runs_in_this_repo(queue, item),
            }
        )
    return {"counts": values, "items": rows}


def approval_phrase(item: dict) -> str:
    return f"APPROVE {item['id']} {item['proposal_digest'][:12]}"


def approve(queue: Queue, item_id: str, supplied_digest: str, interactive: bool = True) -> dict:
    with queue_operation(queue, f"approve {item_id}"):
        return _approve(queue, item_id, supplied_digest, interactive)


def _approve(
    queue: Queue, item_id: str, supplied_digest: str, interactive: bool
) -> dict:
    """Approve one item against the fetched tree, under the caller's operation."""
    item = queue.item(item_id)
    if state_of(queue, item) != "staged":
        raise QueueError(f"item is not staged: {state_of(queue, item)}")
    validate_unchanged(queue, item)
    if supplied_digest != item["proposal_digest"]:
        raise QueueError("supplied digest does not match the staged proposal")
    if interactive:
        if not sys.stdin.isatty():
            raise QueueError("approval requires an interactive TTY")
        print(json.dumps(item, indent=2, sort_keys=True))
        phrase = approval_phrase(item)
        print(f"Type exactly: {phrase}")
        if input("> ").strip() != phrase:
            raise QueueError("approval phrase did not match")
    receipt = {
        "schema_version": 1,
        "id": item_id,
        "proposal_digest": supplied_digest,
        "approved_at_utc": queue.clock(),
        "approved_by": f"{os.environ.get('USER', 'unknown')}@{socket.gethostname()}",
        "interactive_tty": interactive,
    }
    atomic_json(queue.path("approvals", item_id), receipt, exclusive=True)
    return receipt


def revoke(queue: Queue, item_id: str, interactive: bool = True) -> dict:
    """Retire an item that never ran, and land the revocation on the queue ref.

    The state is read from the ORIGIN's tree, and the typed phrase is taken
    OUTSIDE the operation: holding the ref's local lock while a human types would
    stall every tick on the host.  The record itself cannot release a claimed
    item -- :func:`state_of` reads the claim first and :func:`reservation_hold`
    holds a claimed item whatever else exists -- so the window between the check
    and the push cannot free hours that are being spent.
    """
    refresh_queue(queue)
    item = queue.item(item_id)
    if state_of(queue, item) not in {"staged", "approved", "refused"}:
        raise QueueError(f"item cannot be revoked from state {state_of(queue, item)}")
    if interactive:
        if not sys.stdin.isatty():
            raise QueueError("revocation requires an interactive TTY")
        phrase = f"REVOKE {item_id}"
        print(f"Type exactly: {phrase}")
        if input("> ").strip() != phrase:
            raise QueueError("revocation phrase did not match")
    receipt = {"schema_version": 1, "id": item_id, "revoked_at_utc": queue.clock()}
    return commit_state_record(
        queue, "revocations", item_id, receipt, f"revoke {item_id}"
    )


def queue_record_identity(queue: Queue) -> dict[str, object]:
    """Return the host and UID identity that delimit this queue's scope."""
    return {
        "state_dir": str(queue.state),
        "uid": os.getuid(),
        "hostname": socket.gethostname(),
    }


def queue_run_directory(queue: Queue, item_id: str) -> Path:
    """Return the only run directory the queue may assign to an item."""
    validate_id(item_id)
    return queue.state / "runs" / item_id


def create_claim_run_directory(queue: Queue, item_id: str) -> Path:
    """Create the exclusive run directory that makes task attribution private."""
    queue.require_fixed_state_root()
    run_directory = queue_run_directory(queue, item_id)
    run_directory.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.mkdir(run_directory)
    except FileExistsError as exc:
        raise QueueError(
            f"claim run directory already exists, so the claim is not exclusive: "
            f"{run_directory}"
        ) from exc
    except OSError as exc:
        raise QueueError(
            f"cannot create claim run directory: {run_directory}: {exc}"
        ) from exc
    return run_directory


def claimed_run_directory(queue: Queue, item_id: str) -> Path:
    """Return the claim's run directory after verifying queue ownership."""
    claim = read_object(queue.path("claims", item_id))
    recorded = require_text(
        claim.get(RUN_DIRECTORY_FIELD), field=f"claim {item_id} run_dir"
    )
    expected = queue_run_directory(queue, item_id)
    if Path(recorded) != expected:
        raise QueueError(
            f"claim {item_id} run_dir is not the queue-owned path: {recorded}"
        )
    if not expected.is_dir():
        raise QueueError(f"claim {item_id} run_dir is missing: {expected}")
    return expected


def release(
    queue: Queue, item_id: str, record: str, interactive: bool = True
) -> dict:
    """Carry an unmeasurable reservation under a committed continuation decision.

    An item that ran and recorded no scheduler task identities -- it crashed
    before its task-ids file was read, the launcher never started, the producer
    timed out -- can never satisfy the inclusion half of the release rule, so it
    reserves its full declared maximum forever.  That is deliberate: those hours
    were probably spent and nothing in any receipt can be pointed at.  R5
    authorizes a stop, not spending; an unmeasurable spend can be carried only by
    a fresh continuation decision recorded in a committed ruling-family
    document, never by an operator's typed phrase.  The phrase confirms the
    interactive act in addition to that record and never replaces it.

    ``revoke`` remains the act for an item that never ran; this one is refused
    for those, and refused for an item that is still ``staged``, ``approved`` or
    claimed-and-running, because such an item may be spending right now.  It is
    also refused when an outcome records any task-ID measurement: identifiable
    spend releases only through inclusion in a committed meter receipt.

    Parameters
    ----------
    queue : Queue
        Queue holding the item, its claim and its outcome.
    item_id : str
        Item whose reservation is being cleared.
    record : str
        Repository-relative ``DECISION-*.md`` or ``AUTHORIZATION-*.md`` path
        committed at ``HEAD`` and bound to the canonical outcome digest.
    interactive : bool, optional
        Require the typed phrase from a TTY.  ``False`` is for the suite only.

    Returns
    -------
    dict
        The written release record.
    """
    refresh_queue(queue)
    item = queue.item(item_id)
    state = state_of(queue, item)
    if not queue.path("claims", item_id).exists():
        raise QueueError(
            f"item {item_id} was never claimed, so it holds no ran-reservation "
            "to release; revoke retires an item that never ran"
        )
    if state in RESERVING_STATES:
        raise QueueError(
            f"item {item_id} is {state}, so it may be spending now: its "
            "reservation is not an operator's to clear"
        )
    outcome_path = queue.path("outcomes", item_id)
    if not outcome_path.is_file():
        raise QueueError(f"item {item_id} has no terminal outcome to release")
    outcome = read_object(outcome_path)
    require_text(outcome.get("status"), field=f"outcome {item_id} status")
    if item.get("kind") != "compute":
        raise QueueError("release applies only to a compute reservation")
    if not expects_scheduler_tasks(item):
        raise QueueError(
            f"item {item_id} declares expects_scheduler_tasks false and releases "
            "on the receipt timestamp; there is nothing for an operator to release"
        )
    task_ids = outcome_task_ids(queue, item_id)
    if task_ids:
        raise QueueError(
            f"item {item_id} recorded scheduler task ids; only a committed receipt "
            "listing every id can release its reservation"
        )
    if task_ids is not None:
        raise QueueError(
            f"item {item_id} recorded an empty scheduler task-id measurement; "
            "release applies only when outcome_task_ids is None"
        )

    outcome_sha256 = digest(outcome)
    relative_record = Path(require_text(record, field="release record"))
    record_path, record_sha256, record_head = committed_file_identity(
        queue,
        relative_record,
        missing_label="release record",
        uncommitted_reason="release record is not committed at HEAD",
    )
    committed_relative = record_path.relative_to(queue.repo)
    if committed_relative.parts[:2] != ("docs", "orchestration"):
        raise QueueError("release record must be under docs/orchestration/")
    if not RELEASE_RECORD_NAME_RE.fullmatch(record_path.name):
        raise QueueError(
            "release record must be named DECISION-*.md or AUTHORIZATION-*.md"
        )
    binding_line = (
        f"RELEASE-RESERVATION {item_id} outcome-sha256 {outcome_sha256}"
    )
    try:
        record_lines = record_path.read_text().splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise QueueError(
            f"release record cannot be read as text: {record_path}"
        ) from exc
    if binding_line not in record_lines:
        raise QueueError(
            "release record does not bind this item and canonical outcome digest: "
            f"required literal line {binding_line!r}"
        )
    if interactive:
        if not sys.stdin.isatty():
            raise QueueError("release requires an interactive TTY")
        print(json.dumps(queue.item(item_id), indent=2, sort_keys=True))
        phrase = f"RELEASE {item_id}"
        print(f"Type exactly: {phrase}")
        if input("> ").strip() != phrase:
            raise QueueError("release phrase did not match")
    receipt = {
        "schema_version": 1,
        "id": item_id,
        "state_at_release": state,
        "record_path": committed_relative.as_posix(),
        "record_sha256": record_sha256,
        "git_head": record_head,
        "outcome_sha256": outcome_sha256,
        "released_at_utc": queue.clock(),
        "released_by": f"{os.environ.get('USER', 'unknown')}@{socket.gethostname()}",
        "interactive_tty": interactive,
    }
    with queue_operation(queue, f"release {item_id}") as sync:
        # One push for the record and its log line: a released reservation that
        # no other host can see is exactly the split this ref closed, and a log
        # line without its record would attest to a release that never happened.
        atomic_json(queue.path("releases", item_id), receipt, exclusive=True)
        log_admission_event(
            queue,
            {
                "event": "reservation-released",
                "queue_ref": CAMPAIGN_QUEUE_REF,
                "fetched_ref_sha": sync.base or "",
                **receipt,
            },
        )
    return receipt


def dependencies_succeeded(queue: Queue, item: dict) -> bool:
    for dependency in item["depends_on"]:
        outcome_path = queue.path("outcomes", dependency)
        if not outcome_path.exists() or read_object(outcome_path).get("status") != "succeeded":
            return False
    return True


def ready_item(queue: Queue) -> dict | None:
    """Return the next item THIS repository may run, or ``None``.

    The queue is campaign-global, so it also holds items staged from other
    checkouts.  Their bindings, ``cwd`` and ``git_head`` are properties of the
    repository they were staged from and only a ticker there can validate them,
    so this ticker skips them: it must not mark another checkout's item ``stale``
    against its own files, and it must not run one.  They keep reserving and they
    stay listed.
    """
    candidates = sorted(queue.items(), key=lambda x: (x["created_at_utc"], x["id"]))
    for item in candidates:
        if not runs_in_this_repo(queue, item):
            continue
        if state_of(queue, item) in {
            "approved",
            "refused",
        } and dependencies_succeeded(queue, item):
            return item
    return None


def write_outcome(queue: Queue, item: dict, status: str, **extra: object) -> dict:
    """Record a terminal outcome, stamped with the instant it became terminal.

    ``completed_at_utc`` is not decoration: :func:`reservation_hold` compares a
    receipt's ``measured_at_utc`` against it to decide whether the meter has yet
    had the chance to see this item's spend, so it is written for every outcome
    and never omitted.
    """
    value = {
        "schema_version": 1,
        "id": item["id"],
        "proposal_digest": item["proposal_digest"],
        "status": status,
        OUTCOME_INSTANT_FIELD: queue.clock(),
        **queue_record_identity(queue),
        **extra,
    }
    outcome_path = queue.path("outcomes", item["id"])
    replace_refusal = False
    if outcome_path.exists():
        existing = read_object(outcome_path)
        replace_refusal = existing.get("status") == "refused"
        if not replace_refusal:
            raise QueueError(f"refusing to overwrite: {outcome_path}")
    return commit_state_record(
        queue,
        "outcomes",
        str(item["id"]),
        value,
        f"outcome {item['id']} {status}",
        exclusive=not replace_refusal,
    )


def run_logged_command(
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout_seconds: float,
    log_path: Path,
    proposal_digest: str,
) -> tuple[int | None, str | None]:
    """Run one bound command and return its code plus any launch failure."""
    try:
        with log_path.open("w") as log:
            log.write(f"proposal_digest={proposal_digest}\n")
            log.write(f"argv={canonical(argv)}\n")
            log.flush()
            completed = subprocess.run(
                argv,
                cwd=cwd,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
                timeout=timeout_seconds,
            )
        return completed.returncode, None
    except subprocess.TimeoutExpired:
        return None, "command timed out"
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        return None, f"command could not be started: {exc}"


def read_declared_task_ids(
    path: Path, contract: dict[str, object]
) -> tuple[list[str], str, None] | tuple[None, None, str]:
    """Read scheduler task identities from the queue-owned claim path.

    This runs after the producer and BEFORE the terminal validator, because the
    ids are what let a later receipt demonstrate that this item's spend was
    counted.  Without them the reservation can only be released by a timestamp,
    and a receipt measured after an outcome may have metered rows this item's
    tasks are not in.

    The file must be a JSON array of scheduler task identities in the exact form
    ``r5_meter.py`` publishes (:data:`TASK_ID_RE`).  It must be nonempty when the
    contract declares ``expects_scheduler_tasks``, and empty when it does not:
    both directions are refusals, because "the producer scheduled nothing" and
    "the producer's ids were never written" are different facts and only the
    declaration says which one this arm is allowed to report.

    Returns
    -------
    tuple[list[str], str, None] or tuple[None, None, str]
        The sorted ids and the sha256 of the file's exact bytes, or ``None``,
        ``None`` and the refusal reason.
    """
    accounting = contract["accounting"]
    if not isinstance(accounting, dict):
        raise QueueError("validated campaign contract lost accounting")
    expects = accounting["expects_scheduler_tasks"]
    if not path.is_file():
        return None, None, (
            f"queue-owned task-ids file was not written by the producer: {path}"
        )
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, None, f"queue-owned task-ids file is not JSON: {exc}"
    try:
        task_ids = require_text_list(value, field="declared task ids")
    except QueueError as exc:
        return None, None, f"queue-owned task-ids file is malformed: {exc}"
    for task_id in task_ids:
        if not TASK_ID_RE.fullmatch(task_id):
            return None, None, (
                "queue-owned task-ids file holds a value that is not a scheduler "
                f"task identity: {task_id}"
            )
    if expects is True and not task_ids:
        return None, None, (
            "queue-owned task-ids file is empty while the contract declares "
            "accounting.expects_scheduler_tasks true"
        )
    if expects is False and task_ids:
        return None, None, (
            "queue-owned task-ids file lists scheduler tasks while the contract "
            "declares accounting.expects_scheduler_tasks false: "
            + ", ".join(sorted(task_ids))
        )
    return sorted(task_ids), hashlib.sha256(raw).hexdigest(), None


def normalized_terminal_validator(
    queue: Queue, contract: dict[str, object], *, require_guard: bool
) -> tuple[list[str], Path]:
    """Resolve the validator command and working directory from a contract.

    Parameters
    ----------
    queue : Queue
        Queue whose repository root bounds every resolved path.
    contract : dict[str, object]
        Contract already accepted by :func:`validate_campaign_contract`.
    require_guard : bool
        Require the validator to route through the OI-136 guard, as compute
        items do.  A refusal here is a launch failure and therefore resolves to
        the contract's ``otherwise`` branch, never to a pass.

    Returns
    -------
    tuple[list[str], Path]
        The resolved argument vector and the validator working directory.

    Raises
    ------
    QueueError
        If the command, its guarded target, or the working directory is not a
        repository path satisfying the compute rules.
    """
    terminal_validator = contract["terminal_validator"]
    if not isinstance(terminal_validator, dict):
        raise QueueError("validated campaign contract lost terminal_validator")
    argv = list(
        require_argv(terminal_validator["argv"], field="terminal_validator.argv")
    )
    command_bindings(
        queue.repo,
        argv,
        [],
        require_guard=require_guard,
        role="compute terminal validator",
    )
    cwd = resolve_repo_path(
        queue.repo,
        require_text(terminal_validator["cwd"], field="terminal_validator.cwd"),
    )
    return argv, cwd


def run_compute_item(queue: Queue, item: dict, env: dict[str, str]) -> tuple[int, dict]:
    """Run a producer and its mandatory independent terminal validator.

    ``maximum_cost.wall_hours`` is ONE deadline for the whole execution, not a
    per-command allowance: the deadline is fixed when the producer starts, the
    producer is capped by whichever of ``timeout_seconds`` and the remaining
    budget is smaller, and the validator receives exactly what the producer left.
    A validator with no budget left is not started, which is a terminal result
    the contract's ``otherwise`` branch must cover.

    Between the two commands the queue-owned task-ids file is read.  The queue
    passes its absolute path to both commands in
    ``MNV_CAMPAIGN_TASK_IDS_FILE``.  Its ids are recorded in the outcome and are
    what a later receipt must list before this item's reservation is released, so
    a file that is missing, malformed, or disagrees with
    ``accounting.expects_scheduler_tasks`` is a refusal: the validator is NOT
    started, the outcome resolves to the contract's ``otherwise`` branch with the
    reason recorded, and -- because no ids were recorded -- the reservation is
    permanent until an operator releases it.
    """
    contract = item["campaign_contract"]
    if not isinstance(contract, dict):
        raise QueueError("validated compute item lost its campaign contract")
    maximum_cost = contract["maximum_cost"]
    if not isinstance(maximum_cost, dict):
        raise QueueError("validated campaign contract lost maximum_cost")
    timeout_seconds = float(item["timeout_seconds"])
    wall_seconds = float(maximum_cost["wall_hours"]) * 3600
    logs_dir = queue.state / "logs"
    producer_log = logs_dir / f"{item['id']}.producer.log"
    validator_log = logs_dir / f"{item['id']}.validator.log"
    run_directory = claimed_run_directory(queue, str(item["id"]))
    task_ids_path = run_directory / TASK_IDS_FILE_NAME
    command_env = env.copy()
    command_env[CAMPAIGN_TASK_IDS_FILE_ENV] = str(task_ids_path)
    started = time.monotonic()
    deadline = started + wall_seconds
    producer_timeout = min(timeout_seconds, deadline - started)
    producer_returncode, producer_error = run_logged_command(
        item["argv"],
        cwd=resolve_repo_path(queue.repo, item["cwd"]),
        env=command_env,
        timeout_seconds=producer_timeout,
        log_path=producer_log,
        proposal_digest=item["proposal_digest"],
    )
    task_ids, task_ids_sha256, accounting_error = read_declared_task_ids(
        task_ids_path, contract
    )

    validator_env = command_env.copy()
    validator_env["CAMPAIGN_PRODUCER_RETURNCODE"] = (
        str(producer_returncode)
        if producer_returncode is not None
        else "TIMEOUT_OR_NOT_STARTED"
    )
    validator_timeout = deadline - time.monotonic()
    wall_budget_exhausted = validator_timeout <= 0
    if accounting_error is not None:
        # The accounting refusal comes first because it is about whether this run
        # can ever be accounted for, which no validator verdict can repair.
        validator_returncode = None
        validator_error = f"not started: {accounting_error}"
        validator_log.write_text(validator_error + "\n")
    elif wall_budget_exhausted:
        validator_returncode = None
        validator_error = "wall budget exhausted before validation"
        validator_log.write_text(validator_error + "\n")
    else:
        try:
            validator_argv, validator_cwd = normalized_terminal_validator(
                queue, contract, require_guard=True
            )
        except QueueError as exc:
            validator_returncode = None
            validator_error = f"command could not be started: {exc}"
            validator_log.write_text(validator_error + "\n")
        else:
            validator_returncode, validator_error = run_logged_command(
                validator_argv,
                cwd=validator_cwd,
                env=validator_env,
                timeout_seconds=validator_timeout,
                log_path=validator_log,
                proposal_digest=item["proposal_digest"],
            )
    status = "succeeded" if validator_returncode == 0 else "failed"
    extra: dict[str, object] = {
        "producer_returncode": producer_returncode,
        "validator_returncode": validator_returncode,
        "producer_log": str(producer_log),
        "validator_log": str(validator_log),
        "wall_seconds": round(wall_seconds, 3),
        "producer_timeout_seconds": round(producer_timeout, 3),
        "validator_timeout_seconds": round(max(validator_timeout, 0.0), 3),
        "wall_budget_exhausted": wall_budget_exhausted,
        RUN_DIRECTORY_FIELD: str(run_directory),
        OUTCOME_TASK_IDS_PATH_FIELD: str(task_ids_path),
        OUTCOME_EXECUTION_SECONDS_FIELD: round(time.monotonic() - started, 3),
        **terminal_plan(contract, validator_returncode),
    }
    if accounting_error is None:
        # Recorded whenever they could be read, including on a failing validator:
        # the tasks spent whatever they spent, and the release rule needs their
        # identities to demonstrate that a later receipt counted them.
        extra[OUTCOME_TASK_IDS_FIELD] = task_ids
        extra[OUTCOME_TASK_IDS_SHA256_FIELD] = task_ids_sha256
    else:
        extra[OUTCOME_ACCOUNTING_ERROR_FIELD] = accounting_error
    if producer_error is not None:
        extra["producer_error"] = producer_error
    if validator_error is not None:
        extra["validator_error"] = validator_error
    outcome = write_outcome(queue, item, status, **extra)
    if QUEUE_PUSH_PENDING_FIELD in outcome:
        # The run happened, but the campaign does not know it yet.  A terminal
        # exit code here would report that the accounting landed: it has not, the
        # item is still claimed and RESERVING in the ref, and every later
        # operation retries the push before it does anything else.
        return 5, outcome
    return (0 if validator_returncode == 0 else 3), outcome


def run_non_compute_item(
    queue: Queue, item: dict, env: dict[str, str]
) -> tuple[int, dict]:
    """Run a non-compute queue item with the legacy single-command outcome."""
    log_path = queue.state / "logs" / f"{item['id']}.log"
    returncode, error = run_logged_command(
        item["argv"],
        cwd=resolve_repo_path(queue.repo, item["cwd"]),
        env=env,
        timeout_seconds=int(item["timeout_seconds"]),
        log_path=log_path,
        proposal_digest=item["proposal_digest"],
    )
    if returncode is None:
        outcome = write_outcome(
            queue,
            item,
            "failed",
            error=error,
            log=str(log_path),
        )
        return (
            5 if QUEUE_PUSH_PENDING_FIELD in outcome else 3
        ), outcome
    status = "succeeded" if returncode == 0 else "failed"
    outcome = write_outcome(
        queue,
        item,
        status,
        returncode=returncode,
        log=str(log_path),
    )
    if QUEUE_PUSH_PENDING_FIELD in outcome:
        return 5, outcome
    return (0 if returncode == 0 else 3), outcome


def admission_lock_seconds(item: dict) -> float:
    """Return the age after which an admission lock for ``item`` is stale.

    The bound is the item's own worst case -- its staged ``timeout_seconds`` plus
    the whole shared wall budget -- so a lock is only ever removed after the run
    that could have held it can no longer be running.

    Parameters
    ----------
    item : dict
        Queue item being admitted.

    Returns
    -------
    float
        Maximum age in seconds for which the lock is treated as held.
    """
    seconds = float(item.get("timeout_seconds") or 0)
    contract = item.get("campaign_contract")
    if isinstance(contract, dict):
        maximum_cost = contract.get("maximum_cost")
        if isinstance(maximum_cost, dict):
            seconds += float(maximum_cost.get("wall_hours") or 0) * 3600
    return seconds


def log_admission_event(queue: Queue, event: dict[str, object]) -> None:
    """Append one admission event to the campaign's log and to stderr.

    The log lives in the queue ref's tree, so an event recorded OUTSIDE an
    operation takes its own compare-and-swap: an append only this host had would
    be reset away by the next fetch, and the record of a lock broken here is
    exactly the thing another host has to be able to read.  Inside an operation
    it joins that operation's single push, so the event and the record it
    attests to land together or not at all.
    """
    with queue_operation(queue, f"log {event.get('event', 'admission-event')}"):
        log_path = queue.state / "logs" / ADMISSION_LOCK_LOG
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a") as handle:
            handle.write(canonical(event) + "\n")
    print(f"campaignctl: {canonical(event)}", file=sys.stderr)


def clear_stale_admission_lock(queue: Queue, item: dict, path: Path) -> None:
    """Remove an admission lock older than the item timeout plus wall budget.

    Parameters
    ----------
    queue : Queue
        Queue whose clock dates the lock and whose log records the removal.
    item : dict
        Item being admitted, whose timeout and wall budget bound the lock age.
    path : Path
        Existing lock file.

    Raises
    ------
    AdmissionLockHeld
        If the lock is younger than that bound, or its owner record cannot be
        read or dated.  An unreadable lock fails CLOSED: "we cannot tell how old
        this is" must never be resolved as "it is old enough to break".
    """
    try:
        holder = read_object(path)
        acquired = parse_utc(
            holder.get("acquired_at_utc"), field="admission lock acquired_at_utc"
        )
    except QueueError as exc:
        raise AdmissionLockHeld(
            f"admission lock exists and cannot be dated, so it is treated as "
            f"held: {exc}"
        ) from exc
    age = (
        parse_utc(queue.clock(), field="queue clock") - acquired
    ).total_seconds()
    limit = admission_lock_seconds(item)
    if age <= limit:
        raise AdmissionLockHeld(
            f"admission lock held by {holder.get('owner')} for item "
            f"{holder.get('id')} since {holder.get('acquired_at_utc')}: age "
            f"{age:g}s is within the {limit:g}s timeout plus wall budget"
        )
    log_admission_event(
        queue,
        {
            "event": "stale-admission-lock-removed",
            "removed_at_utc": queue.clock(),
            "removed_by": f"{socket.gethostname()}:{os.getpid()}",
            "age_seconds": round(age, 3),
            "stale_after_seconds": round(limit, 3),
            "holder": holder,
        },
    )
    with contextlib.suppress(FileNotFoundError):
        path.unlink()


@contextlib.contextmanager
def admission_lock(queue: Queue, item: dict) -> Iterator[Path]:
    """Hold the queue's single exclusive admission lock.

    The headroom check and the claim that admits an item must be ONE atomic act.
    Checked separately, two tickers each read the same receipt, each find room
    for their own item, and each create their own claim -- both admitted against
    headroom that only covered one.  The lock is a ``O_EXCL`` file in the state
    directory naming its owner ``host:pid``; a lock older than the admitting
    item's timeout plus wall budget is removed after the removal is logged.
    Because the state directory is campaign-global rather than per checkout, this
    is one lock for every clone and worktree on the host: two tickers in two
    clones contend for the same file, which is the whole point.

    Parameters
    ----------
    queue : Queue
        Queue whose state directory holds the lock.
    item : dict
        Item being admitted.

    Yields
    ------
    Path
        The held lock file, removed when the block exits.

    Raises
    ------
    AdmissionLockHeld
        If another ticker holds a lock that is not yet stale.
    """
    path = queue.state / ADMISSION_LOCK_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    try:
        descriptor = os.open(path, flags, 0o644)
    except FileExistsError:
        clear_stale_admission_lock(queue, item, path)
        try:
            descriptor = os.open(path, flags, 0o644)
        except FileExistsError as exc:
            raise AdmissionLockHeld(
                "admission lock was taken by another ticker while this one was "
                "clearing a stale lock"
            ) from exc
    try:
        with os.fdopen(descriptor, "w") as handle:
            json.dump(
                {
                    "schema_version": 1,
                    "id": item["id"],
                    "owner": f"{socket.gethostname()}:{os.getpid()}",
                    "acquired_at_utc": queue.clock(),
                },
                handle,
                indent=2,
                sort_keys=True,
            )
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        yield path
    finally:
        with contextlib.suppress(FileNotFoundError):
            path.unlink()


def admit(queue: Queue, item: dict) -> tuple[int, dict] | None:
    """Check R5 headroom and claim ``item`` in ONE push against the queue ref.

    The reservation scan and the claim that admits the item are computed against
    ONE fetched tree and land together, leased against the sha they were computed
    from.  So two hosts cannot both claim against the same sha: the second push
    is rejected, its claim is discarded, and the tick refuses with the race
    reason for a later tick to retry -- by which time the winner's claim is in
    the tree and the reservation scan sees it.  Nothing is ever merged: merging
    two claims each admitted against headroom the other had not taken is exactly
    how 502 hours fit under a ceiling of 500.

    A compute item is admissible only from the canonical cache directory, and
    that is settled BEFORE the lock: a lock file in a second state directory
    excludes nobody, so taking one there would manufacture the appearance of the
    exclusion it cannot provide.

    Parameters
    ----------
    queue : Queue
        Queue being ticked.
    item : dict
        Ready item to admit.

    Returns
    -------
    tuple[int, dict] or None
        ``None`` when the item is admitted and its claim is in the ref;
        otherwise the exit code and value the tick must return without running
        anything.
    """
    if item["kind"] == "compute":
        non_canonical = non_canonical_state_refusal(queue)
        if non_canonical is not None:
            return 6, write_outcome(
                queue, item, "refused", reason=non_canonical, consumed=False
            )
    item_id = str(item["id"])
    refusal: str | None = None
    claim_conflict = False
    try:
        with admission_lock(queue, item):
            try:
                with queue_operation(queue, f"claim {item_id}") as sync:
                    if item["kind"] == "compute":
                        refusal = r5_refusal_reason(queue, item)
                    if refusal is None:
                        try:
                            run_directory = create_claim_run_directory(
                                queue, item_id
                            )
                        except QueueError as exc:
                            refusal = str(exc)
                    if refusal is None:
                        claim = {
                            "schema_version": 1,
                            "id": item["id"],
                            "proposal_digest": item["proposal_digest"],
                            "claimed_at_utc": queue.clock(),
                            "owner": f"{socket.gethostname()}:{os.getpid()}",
                            RUN_DIRECTORY_FIELD: str(run_directory),
                            **queue_record_identity(queue),
                        }
                        try:
                            atomic_json(
                                queue.path("claims", item_id),
                                claim,
                                exclusive=True,
                            )
                        except QueueError:
                            claim_conflict = True
                        if not claim_conflict and item["kind"] == "compute":
                            log_admission_event(
                                queue, admission_evidence(queue, item_id, sync)
                            )
            except AdmissionRaceLost as exc:
                # The run directory is part of the discarded mutation: leaving it
                # would refuse the retry for a claim that never existed anywhere.
                with contextlib.suppress(OSError):
                    os.rmdir(queue_run_directory(queue, item_id))
                return 5, {
                    "status": "race-lost",
                    "id": item["id"],
                    "reason": str(exc),
                }
            if refusal is not None:
                outcome = write_outcome(
                    queue, item, "refused", reason=refusal, consumed=False
                )
                return (
                    5 if QUEUE_PUSH_PENDING_FIELD in outcome else 6
                ), outcome
            if claim_conflict:
                return 5, {"status": "outcome-unknown", "id": item["id"]}
    except AdmissionLockHeld as exc:
        return 5, {
            "status": "outcome-unknown",
            "id": item["id"],
            "reason": str(exc),
        }
    return None


def admission_evidence(
    queue: Queue, item_id: str, sync: QueueSync
) -> dict[str, object]:
    """Return what an admission is attributable to, for the admission log.

    The pinned file's committed blob is recorded because it, and not a path,
    decided WHICH namespace this admission belonged to: a reader who later finds
    two clones disagreeing about their origin can name the exact object each one
    admitted under.  The fetched sha is recorded beside it because it is the
    state the headroom was computed against and the value the lease was taken on.

    ``push_url`` is recorded BESIDE ``origin_url`` because the two can differ and
    only the second one used to be here.  ``origin_url`` is the checkout's fetch
    url; ``push_url`` is where the queue's own git directory actually delivers,
    as ``get-url --push`` resolves it there.  Every host diverted by a
    configuration injection recorded the pinned url and pushed somewhere else, so
    the log agreed with itself across hosts that had never shared a ref.
    """
    origin = sync.origin if sync.origin is not None else campaign_origin(queue)
    if sync.push_url is None:
        # Measure it rather than record an empty field: the destination is what
        # this record exists to attribute the admission to.  `ensure_scratch`
        # ends in the proof, so this either sets it or refuses.
        sync.ensure_scratch(origin["origin_url"])
    return {
        "event": "compute-admitted",
        "id": item_id,
        "admitted_at_utc": queue.clock(),
        "queue_ref": CAMPAIGN_QUEUE_REF,
        "origin_url": origin["origin_url"],
        "push_url": require_text(sync.push_url, field="queue push url"),
        "campaign_origin_pin": origin["pin_path"],
        "campaign_origin_blob": queue.committed_blob_id(
            resolve_repo_path(queue.repo, origin["pin_path"])
        ),
        "campaign_origin_sha256": origin["pin_sha256"],
        "fetched_ref_sha": sync.base or "",
        **queue_record_identity(queue),
    }


def run_ready(queue: Queue) -> tuple[int, dict]:
    """Tick the queue once against the state the ORIGIN's queue ref holds."""
    try:
        return _run_ready(queue)
    except AdmissionRaceLost as exc:
        # A tick may retry from the top.  Nothing was merged and nothing was
        # consumed: the ref that won holds a complete state, and the next tick
        # decides again against it -- possibly with a refusal on the reservation
        # the winner now holds.
        return 5, {"status": "race-lost", "reason": str(exc)}


def _run_ready(queue: Queue) -> tuple[int, dict]:
    # (a) and (b) before anything is read: the ready set, the item states and
    # the reservations that bound the ceiling are properties of the campaign, and
    # this host's cache is only a copy of them.
    refresh_queue(queue)
    item = ready_item(queue)
    if item is None:
        # Only THIS repository's claimed-without-outcome items make this tick
        # unknown.  Another checkout's in-flight item is not this ticker's
        # business: it reserves and is listed, but reporting it here would make
        # every tick on every clone exit 5 while any one clone was running.
        unknown = [
            row
            for row in summary(queue)["items"]
            if row["state"] == "outcome-unknown" and row["runs_here"]
        ]
        if unknown:
            return 5, {"status": "outcome-unknown", "items": [x["id"] for x in unknown]}
        return 0, {"status": "idle"}
    approval = read_object(queue.path("approvals", item["id"]))
    if approval.get("proposal_digest") != item["proposal_digest"]:
        outcome = write_outcome(queue, item, "stale", error="approval digest mismatch")
        return (5 if QUEUE_PUSH_PENDING_FIELD in outcome else 4), outcome
    try:
        validate_unchanged(queue, item)
    except QueueError as exc:
        outcome = write_outcome(queue, item, "stale", error=str(exc))
        return (5 if QUEUE_PUSH_PENDING_FIELD in outcome else 4), outcome
    not_admitted = admit(queue, item)
    if not_admitted is not None:
        return not_admitted
    (queue.state / "logs").mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["CAMPAIGN_QUEUE_ITEM_ID"] = item["id"]
    if item["kind"] == "compute":
        return run_compute_item(queue, item, env)
    return run_non_compute_item(queue, item, env)


def default_state_dir() -> Path:
    """Return the cache directory a bare invocation uses.

    ``CAMPAIGN_QUEUE_STATE_DIR`` may select a noncanonical cache for non-compute
    work.  It cannot change the canonical root, make that queue eligible for
    compute admission, or change the admission namespace: the namespace is the
    pinned origin's queue ref, and every cache is a copy of it.
    """
    override = os.environ.get("CAMPAIGN_QUEUE_STATE_DIR")
    return Path(override) if override else canonical_state_dir()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--state-dir",
        default=None,
        help=(
            "local CACHE of the campaign queue tree; defaults to "
            "$CAMPAIGN_QUEUE_STATE_DIR or the passwd home / "
            f"{CAMPAIGN_STATE_ROOT_NAME} / {CAMPAIGN_KEY} / {QUEUE_DIRECTORY_NAME}, "
            "which is the ONLY directory that may admit compute items, since the "
            "admission lock and the run directories are properties of that one "
            "directory for every checkout owned by the uid on the host.  The "
            f"admission NAMESPACE is not this directory: it is {CAMPAIGN_QUEUE_REF} "
            "at the origin pinned in "
            f"{CAMPAIGN_ORIGIN_FILE.as_posix()}, and every cache is a copy of it"
        ),
    )
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("stage")
    p.add_argument("--id", required=True)
    p.add_argument("--description", required=True)
    p.add_argument("--kind", choices=("read-only", "write", "compute"), required=True)
    p.add_argument("--cwd", default=".")
    p.add_argument("--depends-on", action="append", default=[])
    p.add_argument("--bind", action="append", default=[])
    p.add_argument("--contract")
    p.add_argument("--timeout-seconds", type=int, default=600)
    p.add_argument("argv", nargs=argparse.REMAINDER)
    p = sub.add_parser("show")
    p.add_argument("--id", required=True)
    p = sub.add_parser("approve")
    p.add_argument("--id", required=True)
    p.add_argument("--digest", required=True)
    p = sub.add_parser("revoke")
    p.add_argument("--id", required=True)
    p = sub.add_parser(
        "release",
        help=(
            "clear the reservation of an item that RAN and recorded no scheduler "
            "task ids under a committed continuation decision"
        ),
    )
    p.add_argument("--id", required=True)
    p.add_argument("--record", required=True)
    sub.add_parser("list")
    sub.add_parser("status").add_argument("--json", action="store_true")
    sub.add_parser("run-ready").add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        queue = Queue(
            state=Path(args.state_dir) if args.state_dir else default_state_dir()
        )
        if args.action == "stage":
            value = stage(
                queue,
                args.id,
                args.description,
                args.kind,
                args.cwd,
                args.depends_on,
                args.bind,
                args.argv,
                args.timeout_seconds,
                args.contract,
            )
            print(json.dumps(value, indent=2, sort_keys=True))
            return 0
        if args.action == "show":
            print(json.dumps(queue.item(args.id), indent=2, sort_keys=True))
            return 0
        if args.action == "approve":
            print(json.dumps(approve(queue, args.id, args.digest), indent=2, sort_keys=True))
            return 0
        if args.action == "revoke":
            print(json.dumps(revoke(queue, args.id), indent=2, sort_keys=True))
            return 0
        if args.action == "release":
            print(
                json.dumps(
                    release(queue, args.id, args.record), indent=2, sort_keys=True
                )
            )
            return 0
        if args.action in {"list", "status"}:
            value = summary(queue)
            if args.action == "status" and args.json:
                print(canonical(value))
            else:
                for row in value["items"]:
                    # The checkout is printed for every row, not only foreign
                    # ones: an operator reading one queue from several clones must
                    # be able to see whose item each is without a second command.
                    where = "here" if row["runs_here"] else row["repo_path"]
                    print(
                        f"{row['id']}\t{row['state']}\t{row['digest'][:12]}\t{where}"
                    )
                print("counts " + canonical(value["counts"]))
            return 0
        if args.action == "run-ready":
            rc, value = run_ready(queue)
            print(canonical(value) if args.json else json.dumps(value, indent=2, sort_keys=True))
            return rc
        raise QueueError(f"unknown action: {args.action}")
    except QueueError as exc:
        print(f"campaignctl: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
