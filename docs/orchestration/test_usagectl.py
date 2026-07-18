import argparse
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

import usagectl


NOW = 1_800_000_000


def policy():
    return {
        "schema_version": 1,
        "claude_cache_max_age_seconds": 1800,
        "codex_personal_reset_credit_reserve": 1,
        "never_consume_codex_reset_credits_automatically": True,
        "seven_day_low_remaining_percent": 20,
        "required_codex_profiles": ["codex-personal", "codex-school"],
        "profile_account_groups": {
            "claude-school": ["claude-school", "claude-school-legacy"]
        },
    }


def credit(expiry_offset=2_000_000, title="Full reset", status="available"):
    return {"title": title, "status": status, "expiresAt": NOW + expiry_offset}


def codex_raw(
    *,
    personal=True,
    envelope="rateLimitsByLimitId",
    five_used=30,
    seven_used=40,
    include_five=True,
):
    limits = {
        "planType": "plus" if personal else "unknown",
        "secondary": {
            "usedPercent": seven_used,
            "windowDurationMins": 10080,
            "resetsAt": NOW + 600_000,
        },
    }
    if include_five:
        limits["primary"] = {
            "usedPercent": five_used,
            "windowDurationMins": 300,
            "resetsAt": NOW + 10_000,
        }
    if envelope == "rateLimitsByLimitId":
        result = {"rateLimitsByLimitId": {"codex": limits}}
    else:
        result = {"rateLimits": limits}
    credits = [credit(), credit(3_000_000)] if personal else []
    result["rateLimitResetCredits"] = {
        "availableCount": len(credits),
        "credits": credits,
    }
    return result


def claude_payload(five=12, seven=34, include_five=True, include_seven=True):
    windows = {}
    if include_five:
        windows["five_hour"] = {
            "used_percentage": five,
            "resets_at": NOW + 10_000,
        }
    if include_seven:
        windows["seven_day"] = {
            "used_percentage": seven,
            "resets_at": NOW + 600_000,
        }
    return {"model": {"display_name": "Opus"}, "rate_limits": windows}


class CodexNormalizationTests(unittest.TestCase):
    def test_both_envelopes_and_swapped_windows(self):
        for envelope in ("rateLimitsByLimitId", "rateLimits"):
            raw = codex_raw(envelope=envelope)
            limits = (
                raw["rateLimitsByLimitId"]["codex"]
                if envelope == "rateLimitsByLimitId"
                else raw["rateLimits"]
            )
            limits["primary"], limits["secondary"] = limits["secondary"], limits["primary"]
            value = usagectl.normalize_codex("codex-personal", raw, policy(), NOW)
            self.assertEqual(value["status"], "ok")
            self.assertEqual(value["windows"]["five_hour"]["remaining_percent"], 70)
            self.assertEqual(value["windows"]["seven_day"]["remaining_percent"], 60)
            self.assertEqual(value["reset_credits"]["valid_available_full_reset_count"], 2)
            self.assertEqual(value["violations"], [])

    def test_missing_five_hour_is_explicitly_unknown_but_weekly_gate_remains_valid(self):
        value = usagectl.normalize_codex(
            "codex-personal", codex_raw(include_five=False), policy(), NOW
        )
        self.assertEqual(value["status"], "ok")
        self.assertNotIn("five_hour", value["windows"])
        self.assertTrue(any("five-hour" in item for item in value["warnings"]))

    def test_window_percentage_rejects_nonfinite_bool_and_range_errors(self):
        for bad in (True, float("nan"), float("inf"), -0.1, 100.1, "40"):
            with self.subTest(bad=bad):
                raw = codex_raw()
                raw["rateLimitsByLimitId"]["codex"]["secondary"]["usedPercent"] = bad
                with self.assertRaises(usagectl.UsageError):
                    usagectl.normalize_codex("codex-personal", raw, policy(), NOW)

    def test_window_shapes_fail_closed(self):
        cases = []
        missing_week = codex_raw()
        del missing_week["rateLimitsByLimitId"]["codex"]["secondary"]
        cases.append(missing_week)
        duplicate = codex_raw()
        duplicate["rateLimitsByLimitId"]["codex"]["secondary"]["windowDurationMins"] = 300
        cases.append(duplicate)
        unknown = codex_raw()
        unknown["rateLimitsByLimitId"]["codex"]["primary"]["windowDurationMins"] = 60
        cases.append(unknown)
        bad_plan = codex_raw()
        bad_plan["rateLimitsByLimitId"]["codex"]["planType"] = None
        cases.append(bad_plan)
        for raw in cases:
            with self.subTest(raw=raw):
                with self.assertRaises(usagectl.UsageError):
                    usagectl.normalize_codex("codex-personal", raw, policy(), NOW)

    def test_reset_epoch_must_be_integer_future_and_plausible(self):
        for bad in (True, "1800000100", NOW - 10, NOW + 700_000):
            with self.subTest(bad=bad):
                raw = codex_raw()
                raw["rateLimitsByLimitId"]["codex"]["primary"]["resetsAt"] = bad
                with self.assertRaises(usagectl.UsageError):
                    usagectl.normalize_codex("codex-personal", raw, policy(), NOW)

    def test_credit_reserve_uncertainty_and_inconsistency_fail_closed(self):
        mutations = [
            lambda item: item.pop("rateLimitResetCredits"),
            lambda item: item["rateLimitResetCredits"].update(availableCount="2"),
            lambda item: item["rateLimitResetCredits"].update(availableCount=True),
            lambda item: item["rateLimitResetCredits"].update(availableCount=-1),
            lambda item: item["rateLimitResetCredits"].update(credits=None),
            lambda item: item["rateLimitResetCredits"].update(credits=[credit()]),
            lambda item: item["rateLimitResetCredits"]["credits"][0].update(title="Partial reset"),
            lambda item: item["rateLimitResetCredits"]["credits"][0].update(status="used"),
            lambda item: item["rateLimitResetCredits"]["credits"][0].update(expiresAt=NOW - 1),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                raw = codex_raw()
                mutate(raw)
                try:
                    value = usagectl.normalize_codex("codex-personal", raw, policy(), NOW)
                except usagectl.UsageError:
                    continue
                self.assertEqual(value["status"], "blocked")
                self.assertTrue(value["violations"])

    def test_low_weekly_warning_is_separate_from_hard_reserve_gate(self):
        value = usagectl.normalize_codex(
            "codex-personal", codex_raw(seven_used=85), policy(), NOW
        )
        self.assertEqual(value["status"], "ok")
        self.assertTrue(any("seven-day" in item for item in value["warnings"]))

    def test_one_authorized_remaining_credit_passes_but_zero_blocks(self):
        one = codex_raw()
        one["rateLimitResetCredits"] = {
            "availableCount": 1,
            "credits": [credit()],
        }
        value = usagectl.normalize_codex("codex-personal", one, policy(), NOW)
        self.assertEqual(value["status"], "ok")
        self.assertEqual(value["reset_credits"]["protected_reserve"], 1)

        none = codex_raw()
        none["rateLimitResetCredits"] = {"availableCount": 0, "credits": []}
        value = usagectl.normalize_codex("codex-personal", none, policy(), NOW)
        self.assertEqual(value["status"], "blocked")
        self.assertTrue(any("below 1" in item for item in value["violations"]))


class JsonLineReaderTests(unittest.TestCase):
    def start(self, source):
        return subprocess.Popen(
            [sys.executable, "-c", source],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            bufsize=0,
        )

    def test_partial_line_obeys_deadline_and_process_is_cleaned(self):
        process = self.start("import os,time; os.write(1,b'{\\\"id\\\":1'); time.sleep(5)")
        reader = usagectl.JsonLineReader(process)
        started = time.monotonic()
        try:
            with self.assertRaisesRegex(usagectl.UsageError, "Timed out"):
                reader.response(1, time.monotonic() + 0.1)
        finally:
            reader.close()
            usagectl.cleanup_process(process)
        self.assertLess(time.monotonic() - started, 1.0)
        self.assertIsNotNone(process.poll())

    def test_stderr_flood_does_not_deadlock_success(self):
        source = (
            "import os; os.write(2,b'x'*200000); "
            "os.write(1,b'{\\\"id\\\":2,\\\"result\\\":{\\\"ok\\\":true}}\\n')"
        )
        process = self.start(source)
        reader = usagectl.JsonLineReader(process)
        try:
            self.assertEqual(reader.response(2, time.monotonic() + 3), {"ok": True})
            self.assertLessEqual(len(reader.stderr_buffer), usagectl.MAX_STDERR_BYTES)
        finally:
            reader.close()
            usagectl.cleanup_process(process)

    def test_notifications_then_server_error_are_framed(self):
        source = (
            "import os; "
            "os.write(1,b'{\\\"method\\\":\\\"notice\\\"}\\n'); "
            "os.write(1,b'{\\\"id\\\":4,\\\"error\\\":{\\\"message\\\":\\\"nope\\\"}}\\n')"
        )
        process = self.start(source)
        reader = usagectl.JsonLineReader(process)
        try:
            with self.assertRaisesRegex(usagectl.UsageError, "app-server error"):
                reader.response(4, time.monotonic() + 2)
        finally:
            reader.close()
            usagectl.cleanup_process(process)

    def test_early_exit_reports_eof_and_stderr(self):
        process = self.start("import os,sys; os.write(2,b'failure-detail'); sys.exit(7)")
        reader = usagectl.JsonLineReader(process)
        try:
            with self.assertRaisesRegex(usagectl.UsageError, "EOF before response") as raised:
                reader.response(9, time.monotonic() + 2)
            self.assertIn("failure-detail", str(raised.exception))
        finally:
            reader.close()
            usagectl.cleanup_process(process)


class ClaudeCacheTests(unittest.TestCase):
    def record(self, cache_dir, payload, now=NOW, profile="claude-personal"):
        with mock.patch.object(sys, "stdin", io.StringIO(json.dumps(payload))):
            with mock.patch.object(usagectl.time, "time", return_value=now):
                usagectl.record_claude(profile, Path(cache_dir))
        return Path(cache_dir) / f"{profile}.json"

    def test_missing_status_payload_preserves_valid_cache_and_timestamp(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.record(tmp, claude_payload())
            before = path.read_bytes()
            self.record(tmp, {"model": {"display_name": "Opus"}}, NOW + 100)
            self.assertEqual(path.read_bytes(), before)

    def test_unchanged_payload_does_not_refresh_window_observations(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.record(tmp, claude_payload())
            before = json.loads(path.read_text())
            self.record(tmp, claude_payload(), NOW + 100)
            after = json.loads(path.read_text())
            self.assertEqual(after, before)
            self.assertEqual(
                after["rate_limits"]["five_hour"]["observed_at_epoch"], NOW
            )

    def test_partial_payload_merges_and_tracks_each_window_observation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.record(tmp, claude_payload())
            self.record(
                tmp,
                claude_payload(five=13, include_seven=False),
                NOW + 100,
            )
            value = json.loads(path.read_text())
            self.assertEqual(value["rate_limits"]["five_hour"]["observed_at_epoch"], NOW + 100)
            self.assertEqual(value["rate_limits"]["seven_day"]["observed_at_epoch"], NOW)

    def test_stale_windows_are_suppressed_not_exposed(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.record(tmp, claude_payload())
            with mock.patch.object(usagectl.time, "time", return_value=NOW + 2000):
                value = usagectl.read_claude_cache("claude-personal", Path(tmp), policy())
            self.assertEqual(value["status"], "stale")
            self.assertEqual(value["windows"], {})
            self.assertTrue(value["warnings"])

    def test_per_window_staleness_yields_only_fresh_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.record(tmp, claude_payload())
            value = json.loads(path.read_text())
            value["rate_limits"]["five_hour"]["observed_at_epoch"] = NOW - 2000
            value["snapshot_signature"] = usagectl.claude_snapshot_signature(
                "claude-personal", value["rate_limits"]
            )
            path.write_text(json.dumps(value))
            with mock.patch.object(usagectl.time, "time", return_value=NOW):
                result = usagectl.read_claude_cache("claude-personal", Path(tmp), policy())
            self.assertEqual(result["status"], "partial")
            self.assertNotIn("five_hour", result["windows"])
            self.assertIn("seven_day", result["windows"])

    def test_wrong_profile_future_timestamp_and_signature_tamper_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.record(tmp, claude_payload())
            original = json.loads(path.read_text())
            cases = []
            wrong_profile = json.loads(json.dumps(original))
            wrong_profile["profile"] = "claude-school"
            cases.append(wrong_profile)
            future = json.loads(json.dumps(original))
            future["rate_limits"]["five_hour"]["observed_at_epoch"] = NOW + 60
            future["snapshot_signature"] = usagectl.claude_snapshot_signature(
                "claude-personal", future["rate_limits"]
            )
            cases.append(future)
            tampered = json.loads(json.dumps(original))
            tampered["rate_limits"]["seven_day"]["used_percentage"] = 99
            cases.append(tampered)
            for value in cases:
                with self.subTest(value=value):
                    path.write_text(json.dumps(value))
                    with mock.patch.object(usagectl.time, "time", return_value=NOW):
                        with self.assertRaises(usagectl.UsageError):
                            usagectl.read_claude_cache("claude-personal", Path(tmp), policy())


class HomeAndInstallerTests(unittest.TestCase):
    def profile(self, home, provider="codex"):
        return {"home": home, "provider": provider}

    def test_account_home_rejects_unsafe_paths_symlinks_and_provider_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "real").mkdir()
            (root / "link").symlink_to(root / "real", target_is_directory=True)
            with mock.patch.object(usagectl, "trusted_login_home", return_value=(root, root)):
                for home in ("relative", "$HOME/real", "~/../real", "~/link"):
                    with self.subTest(home=home):
                        with self.assertRaises(usagectl.UsageError):
                            usagectl.validate_account_home(
                                "codex-personal", self.profile(home)
                            )
                with self.assertRaises(usagectl.UsageError):
                    usagectl.validate_account_home(
                        "codex-personal", self.profile("~/real", "claude")
                    )

    def test_duplicate_real_account_home_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "same").mkdir()
            profiles = {
                "codex-personal": self.profile("~/same"),
                "codex-school": self.profile("~/same"),
            }
            with mock.patch.object(usagectl, "trusted_login_home", return_value=(root, root)):
                with self.assertRaises(usagectl.UsageError):
                    usagectl.validate_profile_homes(
                        profiles, ["codex-personal", "codex-school"]
                    )

    def test_installer_refuses_every_falsey_existing_statusline(self):
        with tempfile.TemporaryDirectory() as tmp:
            account = Path(tmp) / "account"
            settings_path = account / ".claude" / "settings.json"
            settings_path.parent.mkdir(parents=True)
            for existing in ({}, "", None, False):
                with self.subTest(existing=existing):
                    original = {"statusLine": existing, "keep": {"x": 1}}
                    settings_path.write_text(json.dumps(original))
                    with self.assertRaises(usagectl.UsageError):
                        usagectl.install_claude_statusline(
                            "claude-personal",
                            {"provider": "claude"},
                            account,
                            Path(tmp) / "cache",
                            False,
                        )
                    self.assertEqual(json.loads(settings_path.read_text()), original)


class AccountAliasTests(unittest.TestCase):
    def profile_value(self, used, observed, reset=NOW + 10_000):
        return {
            "provider": "claude",
            "status": "partial",
            "windows": {
                "five_hour": {
                    "used_percent": float(used),
                    "remaining_percent": 100.0 - float(used),
                    "resets_at_epoch": reset,
                    "resets_at_utc": usagectl.iso_from_epoch(reset),
                    "observed_at_epoch": observed,
                }
            },
            "warnings": [],
            "violations": [],
        }

    def test_school_aliases_use_freshest_observation_and_never_sum(self):
        values = {
            "claude-school": self.profile_value(85, NOW + 100),
            "claude-school-legacy": self.profile_value(81, NOW),
        }
        accounts = usagectl.consolidate_account_groups(
            values, {"claude-school": ["claude-school", "claude-school-legacy"]}
        )
        account = accounts["claude-school"]
        self.assertEqual(account["windows"]["five_hour"]["used_percent"], 85)
        self.assertEqual(account["windows"]["five_hour"]["remaining_percent"], 15)
        self.assertEqual(account["window_sources"]["five_hour"], "claude-school")
        self.assertTrue(values["claude-school"]["capacity_is_shared"])
        self.assertEqual(values["claude-school-legacy"]["account_id"], "claude-school")
        self.assertTrue(any("must not be summed" in item for item in account["warnings"]))

    def test_missing_flat_cache_falls_back_to_fresh_legacy_cache(self):
        missing = {
            "provider": "claude",
            "status": "missing",
            "windows": {},
            "warnings": [],
            "violations": [],
        }
        values = {
            "claude-school": missing,
            "claude-school-legacy": self.profile_value(77, NOW),
        }
        account = usagectl.consolidate_account_groups(
            values, {"claude-school": ["claude-school", "claude-school-legacy"]}
        )["claude-school"]
        self.assertEqual(account["windows"]["five_hour"]["remaining_percent"], 23)
        self.assertEqual(account["window_sources"]["five_hour"], "claude-school-legacy")

    def test_equal_timestamp_disagreement_chooses_highest_usage(self):
        values = {
            "claude-school": self.profile_value(91, NOW),
            "claude-school-legacy": self.profile_value(12, NOW),
        }
        account = usagectl.consolidate_account_groups(
            values, {"claude-school": ["claude-school", "claude-school-legacy"]}
        )["claude-school"]
        self.assertEqual(account["windows"]["five_hour"]["used_percent"], 91)
        self.assertEqual(account["window_sources"]["five_hour"], "claude-school")

    def test_alias_group_rejects_missing_or_non_claude_members(self):
        good = self.profile_value(10, NOW)
        for values in (
            {"claude-school": good},
            {
                "claude-school": good,
                "claude-school-legacy": {**good, "provider": "codex"},
            },
        ):
            with self.subTest(values=values):
                with self.assertRaises(usagectl.UsageError):
                    usagectl.consolidate_account_groups(
                        values,
                        {"claude-school": ["claude-school", "claude-school-legacy"]},
                    )


class PolicyAndGateTests(unittest.TestCase):
    def write_policy(self, directory):
        path = Path(directory) / "policy.json"
        path.write_text(json.dumps(policy()))
        return path

    def args(self, directory, profile=None):
        return argparse.Namespace(
            config=str(Path(directory) / "profiles.json"),
            policy=str(self.write_policy(directory)),
            cache_dir=str(Path(directory) / "cache"),
            profile=profile,
            timeout=1.0,
            json=True,
        )

    def profiles(self):
        result = {}
        for name in usagectl.DEFAULT_PROFILES:
            provider = name.split("-", 1)[0]
            result[name] = {"provider": provider, "home": f"~/{name}", "tag": name}
        return result

    def run_snapshot(self, directory, profile=None, fail_school=False):
        args = self.args(directory, profile)
        profiles = self.profiles()

        def read(profile_value, _home, timeout):
            if profile_value["tag"] == "codex-school" and fail_school:
                raise usagectl.UsageError("synthetic school failure")
            return codex_raw(personal=profile_value["tag"] == "codex-personal")

        missing = {
            "provider": "claude",
            "status": "missing",
            "source": "test",
            "windows": {},
            "warnings": ["unknown"],
            "violations": [],
        }
        homes = {
            name: Path(directory) / name
            for name, value in profiles.items()
            if value["provider"] in {"codex", "claude"}
        }
        with mock.patch.object(usagectl.agentctl, "load_profiles", return_value=profiles):
            with mock.patch.object(usagectl, "validate_profile_homes", return_value=homes):
                with mock.patch.object(usagectl, "read_codex_rate_limits", side_effect=read):
                    with mock.patch.object(usagectl, "read_claude_cache", return_value=missing):
                        with mock.patch.object(usagectl.time, "time", return_value=NOW):
                            return usagectl.snapshot(args)

    def test_policy_schema_is_strict_and_remaining_reserve_cannot_be_lowered(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_policy(tmp)
            self.assertEqual(usagectl.load_policy(path), policy())
            for mutation in (
                lambda value: value.update(codex_personal_reset_credit_reserve=0),
                lambda value: value.update(never_consume_codex_reset_credits_automatically=False),
                lambda value: value.update(extra=True),
            ):
                value = policy()
                mutation(value)
                path.write_text(json.dumps(value))
                with self.assertRaises(usagectl.UsageError):
                    usagectl.load_policy(path)

    def test_required_codex_error_and_partial_profile_are_nonpassing(self):
        with tempfile.TemporaryDirectory() as tmp:
            failed = self.run_snapshot(tmp, fail_school=True)
            self.assertFalse(failed["gate_ok"])
            self.assertTrue(failed["policy_violations"])
        with tempfile.TemporaryDirectory() as tmp:
            partial = self.run_snapshot(tmp, profile=["codex-school"])
            self.assertFalse(partial["gate_ok"])
            self.assertTrue(any("Partial" in item for item in partial["policy_violations"]))

    def test_last_valid_snapshot_records_first_unchanged_and_material_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = self.run_snapshot(tmp)
            self.assertTrue(first["gate_ok"])
            self.assertEqual(first["changes"][0]["field"], "baseline")
            second = self.run_snapshot(tmp)
            self.assertTrue(second["gate_ok"])
            self.assertEqual(second["changes"], [])
            state_path = Path(tmp) / "cache" / "last-valid-snapshot.json"
            prior = json.loads(state_path.read_text())
            prior["profiles"]["codex-personal"]["windows"]["seven_day"]["resets_at_utc"] = "old"
            usagectl.agentctl.atomic_write_json(state_path, prior)
            third = self.run_snapshot(tmp)
            self.assertTrue(any(item["field"] == "seven_day.resets_at_utc" for item in third["changes"]))

    def test_main_exit_code_is_zero_only_for_gate_ok_and_json_is_standard(self):
        args = argparse.Namespace(command="snapshot", json=True)
        parser = mock.Mock()
        parser.parse_args.return_value = args
        for gate_ok, expected in ((True, 0), (False, 3)):
            value = {
                "gate_ok": gate_ok,
                "profiles": {},
                "warnings": [],
                "policy_violations": [] if gate_ok else ["blocked"],
            }
            with self.subTest(gate_ok=gate_ok):
                with mock.patch.object(usagectl, "parser", return_value=parser):
                    with mock.patch.object(usagectl, "snapshot", return_value=value):
                        with mock.patch.object(sys, "stdout", io.StringIO()) as output:
                            self.assertEqual(usagectl.main(), expected)
                            parsed = json.loads(output.getvalue())
                            self.assertEqual(parsed["gate_ok"], gate_ok)

    def test_change_tracking_uses_shared_account_and_not_alias_sum(self):
        old_account = {
            "status": "partial",
            "windows": {
                "five_hour": {
                    "remaining_percent": 23.0,
                    "resets_at_utc": "2026-07-18T18:00:00+00:00",
                }
            },
        }
        new_account = json.loads(json.dumps(old_account))
        new_account["windows"]["five_hour"]["remaining_percent"] = 15.0
        previous = {
            "profiles": {},
            "accounts": {"claude-school": old_account},
        }
        current = {
            "profiles": {},
            "accounts": {"claude-school": new_account},
        }
        changes = usagectl.snapshot_changes(previous, current)
        self.assertEqual(
            changes,
            [
                {
                    "profile": "account:claude-school",
                    "field": "five_hour.remaining_percent",
                    "old": 23.0,
                    "new": 15.0,
                }
            ],
        )


class CleanRuntimeTests(unittest.TestCase):
    def test_script_pins_available_python311(self):
        first = Path(usagectl.__file__).read_text().splitlines()[0]
        self.assertEqual(first, "#!/usr/bin/python3.11")
        self.assertTrue(Path("/usr/bin/python3.11").exists())


if __name__ == "__main__":
    unittest.main()
