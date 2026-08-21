"""No single host can measure every section, so an unmeasurable field must CARRY, not blank.

OI-144, measured 2026-08-21 by generating `LIVE-STATE.md` on two hosts at one
commit. From the laptop the Slurm rows blanked (`STATE UNAVAILABLE`) while the
usage section was real; from a Perlmutter login node Slurm was real while every
provider percentage became `unknown` and `Usage gate` degraded to
`BLOCKED/UNKNOWN`. Each regeneration overwrote the other's truth, and nothing in
the output separated "measured as absent" from "this host could not look".

EVERY TEST HERE IS POWER-TESTED IN BOTH DIRECTIONS, because the dangerous failure
of a carry-forward feature is not that it fails to carry -- it is that it carries
something nobody measured, or that a carried value reads as a current verdict. So
each "it carries" test has a sibling asserting that a NON-observation is never
recorded and that a carried value never wears live-state vocabulary.

The Slurm/usage shapes below are the shapes those two hosts actually produced:
`slurm_array_status.build_snapshot` returns `overall="UNOBSERVED"` with
`observer_errors` when `squeue`/`sacct` are absent, and `usagectl.profile_error`
returns `status="error"` with a violation when a profile home cannot be read.
"""

from __future__ import annotations

import json
import pathlib
import tempfile
import unittest

from generate_live_state import (
    LastKnown,
    MAX_LINES,
    age_between,
    carried,
    render,
)

CLUSTER = "login04"
LAPTOP = "josephs-mac"
T_CLUSTER = "2026-08-21T18:13:13Z"
T_LATER = "2026-08-22T11:13:13Z"

# What build_snapshot returns where Slurm answers, and where it is not installed.
OBSERVED_JOB = {"overall": "ERROR", "counts": {"FAILED": 1}, "error_tasks": [0]}
UNOBSERVED_JOB = {
    "overall": "UNOBSERVED",
    "counts": {"UNKNOWN": 1},
    "error_tasks": [],
    "observer_errors": [
        "squeue:[Errno 2] No such file or directory: 'squeue'",
        "sacct:[Errno 2] No such file or directory: 'sacct'",
    ],
}
# usagectl on a host that can read its profile homes, and on one that cannot.
READABLE_USAGE = {
    "gate_ok": True,
    "profiles": {
        "codex-personal": {
            "provider": "codex",
            "status": "ok",
            "windows": {"seven_day": {"remaining_percent": 64, "resets_at_utc": "2026-08-24T00:00:00Z"}},
            "reset_credits": {"valid_available_full_reset_count": 1, "protected_reserve": 1},
        },
        "codex-school": {
            "provider": "codex",
            "status": "ok",
            "windows": {"seven_day": {"remaining_percent": 91, "resets_at_utc": "2026-08-25T00:00:00Z"}},
            "reset_credits": {"valid_available_full_reset_count": 2, "protected_reserve": 1},
        },
        "agy": {"provider": "agy", "status": "unknown"},
    },
    "accounts": {"claude-school": {"status": "ok"}},
    "warnings": [],
}
UNREADABLE_USAGE = {
    "gate_ok": False,
    "profiles": {
        "codex-personal": {"provider": "codex", "status": "error", "windows": {},
                           "violations": ["Account home contains a symlink below login home"]},
        "codex-school": {"provider": "codex", "status": "error", "windows": {},
                         "violations": ["Account home contains a symlink below login home"]},
        "claude-school": {"provider": "claude", "status": "error", "windows": {},
                          "violations": ["Account home contains a symlink below login home"]},
        "agy": {"provider": "agy", "status": "unknown"},
    },
    "accounts": {"claude-school": {"status": "unknown"}},
    "warnings": ["agy: agy usage is unknown", "account claude-school: no fresh alias cache"],
}


def config() -> dict:
    return {
        "campaign": "test",
        "current_dag_node": "node",
        "state": "ACTIVE",
        "orchestrator_thread_id": "thread",
        "owners": [{"role": "worker", "uuid": "uuid-1", "purpose": "test"}],
        "blockers": ["blocked"],
        "next_authorized_action": "next",
        "wake": {"tmux_session": "wake"},
        "canonical_science": ["VALIDATION_LEDGER.md"],
        "append_only_history": ["docs/orchestration/RUNS.tsv"],
        "archival_index_only": ["superseded followup prompts"],
    }


SESSIONS = {"sessions": {"worker": {"session_id": "uuid-1", "provider": "agy", "profile": "agy"}}}
WAKE_STATE = {"tmux": "INACTIVE", "event": "absent", "invoked": "absent", "completed": "absent"}


def jobs(snapshot: dict) -> list[dict]:
    return [{
        "job_id": "57266000",
        "tasks": "0-0",
        "receipt": {"cpus_per_task": 32, "memory_per_task": "1796M", "time_limit": "08:00:00",
                    "qos": "gpu_shared"},
        "snapshot": dict(snapshot),
    }]


def dashboard(*, snapshot, usage, usage_rc, host, observed_at, store, dirty=3, head="abc1234"):
    return render(
        config(), SESSIONS, usage, usage_rc, jobs(snapshot),
        {"head": head, "dirty_count": dirty, "host": host},
        WAKE_STATE, observed_at, last_known=store,
    )


def new_store(path=None, *, host, observed_at, head="abc1234"):
    return LastKnown(path, host=host, observed_at=observed_at, head=head)


class ComputeRowsCarry(unittest.TestCase):
    def test_an_observed_job_is_recorded_with_the_host_and_time_that_saw_it(self):
        store = new_store(host=CLUSTER, observed_at=T_CLUSTER)
        dashboard(snapshot=OBSERVED_JOB, usage=READABLE_USAGE, usage_rc=0,
                  host=CLUSTER, observed_at=T_CLUSTER, store=store)
        entry = store.get("compute:57266000")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["host"], CLUSTER)
        self.assertEqual(entry["at_utc"], T_CLUSTER)
        self.assertEqual(entry["git_head"], "abc1234")
        self.assertEqual(entry["value"]["overall"], "ERROR")

    def test_a_NON_observation_is_never_recorded(self):
        """The direction that matters most: the store must not launder a blank.

        If an UNOBSERVED row were recorded, the next host would carry "UNKNOWN=1,
        NOT OBSERVED" forward as though somebody had measured it -- a worse defect
        than the blanking this feature exists to fix.
        """
        store = new_store(host=LAPTOP, observed_at=T_LATER)
        dashboard(snapshot=UNOBSERVED_JOB, usage=UNREADABLE_USAGE, usage_rc=3,
                  host=LAPTOP, observed_at=T_LATER, store=store)
        self.assertEqual(store.probes, {})
        self.assertFalse(store.changed)

    def test_an_unobserved_job_carries_the_last_known_value_attributed_and_aged(self):
        store = new_store(host=CLUSTER, observed_at=T_CLUSTER)
        dashboard(snapshot=OBSERVED_JOB, usage=READABLE_USAGE, usage_rc=0,
                  host=CLUSTER, observed_at=T_CLUSTER, store=store)
        store.host, store.observed_at = LAPTOP, T_LATER
        text = dashboard(snapshot=UNOBSERVED_JOB, usage=UNREADABLE_USAGE, usage_rc=3,
                         host=LAPTOP, observed_at=T_LATER, store=store)
        self.assertIn("LAST KNOWN, NOT MEASURED HERE", text)
        self.assertIn("job state was ERROR", text)
        self.assertIn(f"measured on `{CLUSTER}`", text)
        self.assertIn(T_CLUSTER, text)
        self.assertIn("17.0 h before this snapshot", text)
        self.assertIn("at commit `abc1234`", text)

    def test_the_carried_row_still_refuses_to_claim_liveness(self):
        """Carrying must not weaken the BEN-323 guard it sits inside."""
        store = new_store(host=CLUSTER, observed_at=T_CLUSTER)
        dashboard(snapshot=OBSERVED_JOB, usage=READABLE_USAGE, usage_rc=0,
                  host=CLUSTER, observed_at=T_CLUSTER, store=store)
        store.host, store.observed_at = LAPTOP, T_LATER
        text = dashboard(snapshot=UNOBSERVED_JOB, usage=UNREADABLE_USAGE, usage_rc=3,
                         host=LAPTOP, observed_at=T_LATER, store=store)
        self.assertIn("STATE UNAVAILABLE — NOT A LIVENESS CLAIM", text)
        self.assertIn("THIS HOST COULD NOT LOOK", text)
        # The bolded state word is the one a reader takes as the finding, so the
        # carried state must never appear in that position.
        self.assertNotIn("**ERROR**", text)

    def test_no_history_reads_differently_from_history_withheld(self):
        store = new_store(host=LAPTOP, observed_at=T_LATER)
        text = dashboard(snapshot=UNOBSERVED_JOB, usage=UNREADABLE_USAGE, usage_rc=3,
                         host=LAPTOP, observed_at=T_LATER, store=store)
        self.assertIn("NO LAST-KNOWN VALUE EITHER", text)
        self.assertNotIn("LAST KNOWN, NOT MEASURED HERE", text)


class UsageGateIsNotBlockedByAnUnreadableProfile(unittest.TestCase):
    def test_unreadable_profiles_make_the_gate_NOT_ASSESSABLE_rather_than_BLOCKED(self):
        store = new_store(host=CLUSTER, observed_at=T_CLUSTER)
        text = dashboard(snapshot=OBSERVED_JOB, usage=UNREADABLE_USAGE, usage_rc=3,
                         host=CLUSTER, observed_at=T_CLUSTER, store=store)
        self.assertIn("NOT ASSESSABLE ON THIS HOST — NEITHER A PASS NOR A BLOCK", text)
        self.assertIn("could not be READ on this host", text)
        self.assertNotIn("BLOCKED/UNKNOWN", text)

    def test_a_real_policy_violation_still_renders_as_a_block(self):
        """The other direction: readable profiles that FAIL policy must stay BLOCKED."""
        usage = json.loads(json.dumps(READABLE_USAGE))
        usage["gate_ok"] = False
        store = new_store(host=LAPTOP, observed_at=T_LATER)
        text = dashboard(snapshot=OBSERVED_JOB, usage=usage, usage_rc=3,
                         host=LAPTOP, observed_at=T_LATER, store=store)
        self.assertIn("Usage gate: **BLOCKED/UNKNOWN**", text)
        self.assertNotIn("NOT ASSESSABLE ON THIS HOST", text)

    def test_capacity_is_carried_with_its_host_when_the_profile_is_unreadable(self):
        store = new_store(host=LAPTOP, observed_at=T_CLUSTER)
        dashboard(snapshot=UNOBSERVED_JOB, usage=READABLE_USAGE, usage_rc=0,
                  host=LAPTOP, observed_at=T_CLUSTER, store=store)
        self.assertEqual(store.get("usage:codex-personal")["host"], LAPTOP)
        store.host, store.observed_at = CLUSTER, T_LATER
        text = dashboard(snapshot=OBSERVED_JOB, usage=UNREADABLE_USAGE, usage_rc=3,
                         host=CLUSTER, observed_at=T_LATER, store=store)
        self.assertIn("64% weekly remaining", text)
        self.assertIn(f"measured on `{LAPTOP}`", text)
        self.assertIn("THIS HOST COULD NOT LOOK", text)

    def test_the_warning_COUNT_is_labelled_host_dependent_when_a_profile_is_unreadable(self):
        store = new_store(host=CLUSTER, observed_at=T_CLUSTER)
        text = dashboard(snapshot=OBSERVED_JOB, usage=UNREADABLE_USAGE, usage_rc=3,
                         host=CLUSTER, observed_at=T_CLUSTER, store=store)
        self.assertIn("this COUNT is a property of THIS host", text)

    def test_agy_unknown_is_a_measured_absence_and_is_never_carried(self):
        store = new_store(host=CLUSTER, observed_at=T_CLUSTER)
        text = dashboard(snapshot=OBSERVED_JOB, usage=UNREADABLE_USAGE, usage_rc=3,
                         host=CLUSTER, observed_at=T_CLUSTER, store=store)
        self.assertIn("`unknown` is a MEASURED absence here", text)
        self.assertIsNone(store.get("usage:agy"))


class TwoHostsComposeOneSnapshot(unittest.TestCase):
    """The OI's actual claim: no ONE host can produce a fully measured file."""

    def test_the_cluster_slurm_reading_survives_a_laptop_regeneration(self):
        store = new_store(host=CLUSTER, observed_at=T_CLUSTER)
        # 1. the login node: Slurm real, provider homes unreadable.
        dashboard(snapshot=OBSERVED_JOB, usage=UNREADABLE_USAGE, usage_rc=3,
                  host=CLUSTER, observed_at=T_CLUSTER, store=store)
        # 2. the laptop: no Slurm, provider homes real.
        store.host, store.observed_at = LAPTOP, T_LATER
        text = dashboard(snapshot=UNOBSERVED_JOB, usage=READABLE_USAGE, usage_rc=0,
                         host=LAPTOP, observed_at=T_LATER, store=store)
        # Both sections now say something, and each says where it came from.
        self.assertIn("job state was ERROR", text)          # carried from the cluster
        self.assertIn(f"measured on `{CLUSTER}`", text)
        self.assertIn("Usage gate: **PASS**", text)          # measured here
        self.assertIn("91% weekly remaining", text)
        self.assertLessEqual(len(text.splitlines()), MAX_LINES)


class TheDirtCountIsNotCampaignState(unittest.TestCase):
    """721 from the cluster, 726 from this laptop, same commit -- OI-144, BEN-183."""

    def test_the_count_names_the_checkout_and_the_host_that_produced_it(self):
        store = new_store(host=LAPTOP, observed_at=T_LATER)
        text = dashboard(snapshot=OBSERVED_JOB, usage=READABLE_USAGE, usage_rc=0,
                         host=LAPTOP, observed_at=T_LATER, store=store, dirty=726)
        self.assertIn("GENERATING CHECKOUT", text)
        self.assertIn(f"on `{LAPTOP}` had 726 uncommitted worktree entries", text)
        self.assertIn("never campaign state", text)

    def test_the_bare_unattributed_phrasing_is_gone(self):
        store = new_store(host=LAPTOP, observed_at=T_LATER)
        text = dashboard(snapshot=OBSERVED_JOB, usage=READABLE_USAGE, usage_rc=0,
                         host=LAPTOP, observed_at=T_LATER, store=store, dirty=726)
        self.assertNotIn("worktree entries: 726", text)

    def test_the_host_appears_on_the_Observed_line_so_the_default_scope_is_stated(self):
        store = new_store(host=CLUSTER, observed_at=T_CLUSTER)
        text = dashboard(snapshot=OBSERVED_JOB, usage=READABLE_USAGE, usage_rc=0,
                         host=CLUSTER, observed_at=T_CLUSTER, store=store)
        self.assertIn(f"- Observed: `{T_CLUSTER}` on host `{CLUSTER}`", text)


class StoreMechanics(unittest.TestCase):
    def test_a_pathless_store_neither_loads_nor_persists(self):
        store = LastKnown(None, host=LAPTOP, observed_at=T_LATER)
        store.record("k", {"a": 1})
        self.assertFalse(store.save())

    def test_roundtrip_through_disk_preserves_host_time_and_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "live-state-last-known.json"
            writer = LastKnown(path, host=CLUSTER, observed_at=T_CLUSTER, head="abc1234")
            writer.record("compute:1", {"overall": "ERROR"})
            self.assertTrue(writer.save())
            reader = LastKnown(path, host=LAPTOP, observed_at=T_LATER)
            entry = reader.get("compute:1")
            self.assertEqual(entry["host"], CLUSTER)
            self.assertEqual(entry["at_utc"], T_CLUSTER)
            self.assertEqual(entry["git_head"], "abc1234")

    def test_an_unwritten_store_reports_that_it_wrote_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "live-state-last-known.json"
            self.assertFalse(LastKnown(path, host=LAPTOP, observed_at=T_LATER).save())
            self.assertFalse(path.exists())

    def test_a_corrupt_store_degrades_to_no_history_and_does_not_raise(self):
        """The feature exists for degraded hosts; it must not be the thing that breaks one."""
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "live-state-last-known.json"
            path.write_text("{not json at all")
            store = LastKnown(path, host=LAPTOP, observed_at=T_LATER)
            self.assertEqual(store.probes, {})
            self.assertIsNone(store.get("anything"))

    def test_a_store_whose_probes_are_not_a_mapping_is_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "live-state-last-known.json"
            path.write_text(json.dumps({"schema_version": 1, "probes": ["not", "a", "mapping"]}))
            self.assertEqual(LastKnown(path, host=LAPTOP, observed_at=T_LATER).probes, {})


class WakeSectionCarriesAndDoesNotSayNONE(unittest.TestCase):
    """`events` had the watches bullet's own defect, one line below it.

    The watches bullet was fixed on 2026-08-19 to render NO EVIDENCE when the
    state dir is unreadable. The events bullet next to it kept `... or "none"`,
    so an unreadable events dir still published the claim that no events exist.
    """

    def ctx(self, directory, *, watches=True, events=False):
        import wakerctl
        path = pathlib.Path(directory)
        if watches:
            (path / "watches").mkdir()
        if events:
            (path / "events").mkdir()
        return wakerctl.Ctx(state_dir=path, runner=lambda *a, **k: (_ for _ in ()).throw(
            FileNotFoundError(2, "No such file or directory", "squeue")), clock=lambda: 0.0)

    def waker_dashboard(self, waker_ctx, wake_state, store, *, observed_at=T_LATER, host=LAPTOP):
        cfg = config()
        cfg["wake"] = {"waker": True}
        return render(
            cfg, SESSIONS, READABLE_USAGE, 0, jobs(UNOBSERVED_JOB),
            {"head": "abc1234", "dirty_count": 1, "host": host},
            wake_state, observed_at, waker_ctx=waker_ctx, last_known=store,
        )

    def test_an_absent_events_dir_is_NO_EVIDENCE_not_none(self):
        with tempfile.TemporaryDirectory() as directory:
            ctx = self.ctx(directory, events=False)
            store = new_store(host=LAPTOP, observed_at=T_LATER)
            text = self.waker_dashboard(
                ctx, {"waker_status": {"watches": [], "events": [], "last_tick": {}}}, store,
            )
            self.assertIn("knows of NO events -- that is NOT the same as there being none", text)
            self.assertNotIn("- wakerctl events: none", text)

    def test_a_readable_empty_events_dir_DOES_say_none_and_says_why_it_may(self):
        with tempfile.TemporaryDirectory() as directory:
            ctx = self.ctx(directory, events=True)
            store = new_store(host=LAPTOP, observed_at=T_LATER)
            text = self.waker_dashboard(
                ctx, {"waker_status": {"watches": [], "events": [], "last_tick": {}}}, store,
            )
            self.assertIn("none (events dir readable; 0 event records present)", text)
            self.assertEqual(store.get("waker:events")["value"]["count"], 0)

    def test_events_measured_on_one_host_are_carried_to_a_host_without_the_dir(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            store = new_store(host=CLUSTER, observed_at=T_CLUSTER)
            self.waker_dashboard(
                self.ctx(first, events=True),
                {"waker_status": {"watches": [],
                                  "events": [{"event_id": "evt-1", "state": "resumed"}],
                                  "last_tick": {}}},
                store, observed_at=T_CLUSTER, host=CLUSTER,
            )
            store.host, store.observed_at = LAPTOP, T_LATER
            text = self.waker_dashboard(
                self.ctx(second, events=False),
                {"waker_status": {"watches": [], "events": [], "last_tick": {}}}, store,
            )
            self.assertIn("1 event record(s): `evt-1`:resumed", text)
            self.assertIn(f"measured on `{CLUSTER}`", text)

    def test_a_tick_this_host_cannot_judge_carries_the_stamp_and_still_refuses_a_verdict(self):
        with tempfile.TemporaryDirectory() as directory:
            store = new_store(host=CLUSTER, observed_at=T_CLUSTER)
            store.record("waker:last-tick", {
                "at_utc": "2026-08-21T17:55:08+00:00", "node": "login04", "verdict": "loud"})
            store.host, store.observed_at = LAPTOP, T_LATER
            text = self.waker_dashboard(
                None, {"waker_status": {"watches": [], "events": [], "last_tick": {}}}, store,
            )
            self.assertIn("tick receipt `2026-08-21T17:55:08+00:00` on `login04`", text)
            self.assertIn("behind this snapshot's clock", text)
            self.assertIn("deliberately not a verdict", text)
            # It carried a stamp; it must not have manufactured a health word.
            # Scoped to the bullet, because the file's own FRESHNESS TEST paragraph
            # legitimately contains the word -- a whole-file grep here would be
            # asserting about the wrong subject.
            bullet = next(line for line in text.splitlines() if line.startswith("- Last tick:"))
            for word in ("FRESH,", "STALE", "SUPERVISION NET NOT HEALTHY", "runnable."):
                self.assertNotIn(word, bullet)

    def test_a_watch_render_with_no_state_dir_behind_it_is_never_recorded(self):
        """`wakerctl.status()` projects watches without `params`; that is not a measurement."""
        store = new_store(host=LAPTOP, observed_at=T_LATER)
        self.waker_dashboard(
            None,
            {"waker_status": {"watches": [{"watch_id": "w1", "kind": "slurm-job", "state": "armed"}],
                              "events": [{"event_id": "e1", "state": "new"}],
                              "last_tick": {"at_utc": "now", "node": "n"}}},
            store,
        )
        # Scoped to the wake probes: the usage section in this fixture IS readable
        # and is supposed to record. Asserting an empty store would pass for the
        # wrong reason the day the usage fixture changes.
        self.assertEqual([k for k in store.probes if k.startswith("waker:")], [])


class AgeAndAttribution(unittest.TestCase):
    def test_an_unparseable_stamp_yields_no_age_rather_than_a_small_one(self):
        self.assertEqual(age_between("never", T_LATER), "")
        self.assertEqual(age_between(T_CLUSTER, None), "")

    def test_age_is_computed_across_the_Z_and_offset_spellings(self):
        self.assertEqual(age_between("2026-08-21T18:13:13Z", "2026-08-21T19:13:13+00:00"), "60 min")

    def test_an_entry_with_no_host_or_time_says_so_instead_of_inventing_one(self):
        text = carried({"value": "x"}, T_LATER, str, "a thing")
        self.assertIn("an unrecorded host", text)
        self.assertIn("an unrecorded time", text)


if __name__ == "__main__":
    unittest.main()
