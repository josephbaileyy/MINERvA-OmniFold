"""Hand mutants for covfix_seal.py, covfix_pg.py and covfix_sealcheck.py: each must be killed by test_covfix_seal.py.

  python3 -B covfix_seal_mutation.py [--jobs N] [--only ID,ID]     one line per mutant; exit 0 only if all are killed

Each mutant runs in a fresh temp dir holding copies of the three modules and the tests (they import nothing else from
the repo), so nothing beside this file is touched. The unmutated copy must pass first. A run whose failure names no
test, or shows an import or discovery failure, is a HARNESS FAILURE, not a kill.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = ("covfix_seal.py", "covfix_pg.py", "covfix_sealcheck.py", "test_covfix_seal.py")
S, P, K = "covfix_seal.py", "covfix_pg.py", "covfix_sealcheck.py"
MUTANTS = [
    ('frame-uppercase', S, '_PG_FRAME = re.compile(rb"([0-9a-f]{64})', '_PG_FRAME = re.compile(rb"([0-9a-fA-F]{64})'),
    # Lowering SEED_BASE_LO is equivalent (the frame regex [1-9][0-9]{9} already rejects < 1e9); the raised bound is not.
    ('seed-lo-raised', S, 'SEED_BASE_LO, SEED_BASE_HI = 1_000_000_000, 2_000_000_000', 'SEED_BASE_LO, SEED_BASE_HI = 1_000_000_001, 2_000_000_000'),
    ('seed-hi', S, 'SEED_BASE_LO, SEED_BASE_HI = 1_000_000_000, 2_000_000_000', 'SEED_BASE_LO, SEED_BASE_HI = 1_000_000_000, 2_000_000_001'),
    ('seed-limit-strict', S, 'if max(seeds) >= SEED_LIMIT:', 'if max(seeds) > SEED_LIMIT:'),
    ('u-stride', S, 'U_STRIDE = 10_000', 'U_STRIDE = 1_000'),
    ('n-tasks', S, 'N_TASKS = 7 ', 'N_TASKS = 6 '),
    ('no-force-mdc', S, '"SHA512", "--force-mdc",\n', '"SHA512",\n'),
    ('decrypt-symkey-cache', S, '"--no-symkey-cache", "--decrypt")', '"--decrypt")'),
    ('gpg-rc-ignored', S, '    if rc != 0:\n        raise Refusal(f"gpg exited', '    if False:\n        raise Refusal(f"gpg exited'),
    # tools-relative-ok dropped: an absolute path is implied by realpath(p) == p, so it is equivalent.
    ('env-inherited', S, 'env = dict(GPG_ENV, GNUPGHOME=home)', 'env = dict(os.environ, GNUPGHOME=home)'),
    ('fds-not-closed', S, 'close_fds=True, pass_fds=(3,), preexec_fn', 'close_fds=False, preexec_fn'),
    ('core-not-limited', S, '        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))\n', ''),
    ('home-under-tmpdir', S, '    root = "/dev/shm" if os.path.isdir("/dev/shm") else "/tmp"\n', '    root = tempfile.gettempdir()\n'),
    ('scratch-root-ok', S, '    if scratch and _inside(root, scratch):\n', '    if False:\n'),
    ('home-max', S, 'GNUPG_HOME_MAX = 80', 'GNUPG_HOME_MAX = 800'),
    ('home-mode', S, '        os.chmod(home, 0o700)\n        if len(home)', '        os.chmod(home, 0o755)\n        if len(home)'),
    ('home-not-removed', S, '        shutil.rmtree(home, ignore_errors=True)\n        if os.path.lexists(home):\n            raise Refusal("the GNUPGHOME could not be removed")\n        if not agent_down:', '        pass\n        if os.path.lexists(home):\n            raise Refusal("the GNUPGHOME could not be removed")\n        if not agent_down:'),
    ('removal-unverified', S, '        if os.path.lexists(home):\n            raise Refusal("the GNUPGHOME could not be removed")\n        if not agent_down:', '        if False:\n            raise Refusal("the GNUPGHOME could not be removed")\n        if not agent_down:'),
    ('gpgconf-error-skips-removal', S, '            except (OSError, subprocess.SubprocessError, Refusal):\n                pass\n', '            except KeyError:\n                pass\n'),
    ('symlink-allowed', S, '                raise Refusal("a non-regular entry (symlink or special file) in a sealed tree")', '                pass'),
    ('walk-errors-ignored', S, '    for dirpath, dirnames, filenames in os.walk(root, followlinks=False, onerror=_raise):', '    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):'),
    ('ids-from-zero', S, 'return [f"p{i:04d}" for i in range(1, n + 1)]', 'return [f"p{i:04d}" for i in range(n)]'),
    ('max-products', S, 'MAX_PRODUCTS = 9999', 'MAX_PRODUCTS = 99999'),
    ('manifest-no-paths', S, 'json.dumps({"products": hashes, "paths": paths}, sort_keys=True)', 'json.dumps({"products": hashes}, sort_keys=True)'),
    ('round-trip-skipped', S, '        if hashlib.sha256(back).hexdigest() != hashes[pid]:', '        if False:'),
    ('manifest-trip-skipped', S, '    if back != man_plain:', '    if False:'),
    ('seal-publishes-paths', S, '        cipher[pid + ".gpg"] = hashlib.sha256(ct).hexdigest()', '        cipher[rel + ".gpg"] = hashlib.sha256(ct).hexdigest()'),
    ('overwrite-ciphertext', S, '    with open(path, "xb") as f:', '    with open(path, "wb") as f:'),
    ('delete-follows-dir-link', S, '            if os.path.islink(p):\n                os.unlink(p)', '            if False:\n                os.unlink(p)'),
    ('scan-inverted', S, 'hexdigest() in plaintext_hashes:', 'hexdigest() not in plaintext_hashes:'),
    ('scan-skips-file-root', S, '        yield root\n        return\n', '        return\n'),
    ('nofollow-off', S, 'NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)', 'NOFOLLOW = 0'),
    ('regular-check-off', S, '    fd = os.open(str(path), os.O_RDONLY | NOATIME | NOFOLLOW)\n    try:\n        if not stat.S_ISREG(os.fstat(fd).st_mode):', '    fd = os.open(str(path), os.O_RDONLY | NOATIME | NOFOLLOW)\n    try:\n        if False:'),
    ('seal-dup-allowed', S, 'if not m or m.group(2) in out:', 'if not m:'),
    ('seal-noncanonical-ok', S, 'if MANIFEST_CT not in out or not ids or ids != product_ids(len(ids)) or \\', 'if MANIFEST_CT not in out or \\'),
    ('check-mismatch-inverted', S, 'hexdigest() != want[r])', 'hexdigest() == want[r])'),
    ('check-extra-ignored', S, '    extra = have - set(want)', '    extra = set()'),
    ('check-seal-file-counted', S, '    have = regular - {SEAL_FILE}', '    have = regular'),
    ('reader-unlisted-break', S, '        raise Refusal("a requested name is not in the seal")', '        raise Break("a requested name is not in the seal")'),
    ('reader-missing-as-refusal', S, '        raise Break("a sealed ciphertext is missing") from e', '        raise Refusal("a sealed ciphertext is missing") from e'),
    ('reader-oserror-as-break', S, '        raise Refusal(f"a sealed ciphertext cannot be read', '        raise Break(f"a sealed ciphertext cannot be read'),
    ('reader-no-seal-sha', S, '    if hashlib.sha256(data).hexdigest() != seal_map[name]:', '    if False:'),
    ('manifest-dups-ok', S, 'json.loads(gpg_run(GPG_DECRYPT, passphrase, ct, tools), object_pairs_hook=_no_dup_pairs)', 'json.loads(gpg_run(GPG_DECRYPT, passphrase, ct, tools))'),
    ('manifest-hex-unchecked', S, '          and all(isinstance(h, str) and HEX64.fullmatch(h) for h in man["products"].values())', '          and True'),
    ('manifest-paths-unchecked', S, '          and all(_safe_rel(p) for p in man["paths"].values())\n', '          and True\n'),
    ('manifest-ids-unchecked', S, '          and set(man["products"]) == set(man["paths"]) == listed', '          and True'),
    ('manifest-not-json-refusal', S, '        raise Break("the manifest is not valid JSON") from e', '        raise Refusal("the manifest is not valid JSON") from e'),
    ('product-plain-unchecked', S, '    if hashlib.sha256(plain).hexdigest() != manifest.sha256(pid):', '    if False:'),
    ('product-unlisted-ok', S, '    if pid not in manifest:\n        raise Refusal', '    if False:\n        raise Refusal'),
    ('safe-rel-dotdot', S, '".." not in p.split("/"))', 'True)'),
    ('attempt-loose', P, 'ATTEMPT = re.compile(r"[0-9a-f]{32}")', 'ATTEMPT = re.compile(r"[0-9a-zA-Z]+")'),
    ('command-relative-ok', P, '          and os.path.isabs(spec["command"][0])\n', ''),
    ('command-sha-skipped', P, '    if file_sha256(resolved) != spec["command_sha256"]:', '    if False:'),
    ('tmpdir-keepable', P, '          and not {"TMPDIR", "SCRATCH"} & set(spec["env_keep"]) and _required_ok', '          and not {"SCRATCH"} & set(spec["env_keep"]) and _required_ok'),
    ('env-not-scrubbed', P, '        env = {k: os.environ[k] for k in spec["env_keep"] if k in os.environ}', '        env = dict(os.environ)'),
    ('tmpdir-not-set', P, '        env["TMPDIR"] = str(workdir / "tmp")', '        pass'),
    ('workdir-not-empty-ok', P, '    if not workdir.is_dir() or any(workdir.iterdir()):', '    if not workdir.is_dir():'),
    ('sealed-exists-ok', P, '    if os.path.lexists(sealed):\n        raise', '    if False:\n        raise'),
    ('disjoint-unchecked', P, '    if cs._inside(str(s), str(w)) or cs._inside(str(w), str(s)):', '    if False:'),
    ('products-json-optional', P, '        ok = (summary["generation_rc0"] and summary["command_unchanged"] and summary["products_json"]', '        ok = (summary["generation_rc0"] and summary["command_unchanged"]'),
    ('products-dups-ok', P, ' and len(set(lst)) == len(lst)):', '):'),
    ('command-change-ignored', P, 'summary["command_unchanged"] = file_sha256(spec["resolved"]) == spec["command_sha256"]', 'summary["command_unchanged"] = True'),
    ('synthetic-skipped', P, '        if cs.gpg_run(cs.GPG_DECRYPT, passphrase, cs.gpg_run(cs.GPG_ENCRYPT, passphrase, SYNTHETIC, tools),\n                      tools) != SYNTHETIC:', '        if False:'),
    ('scratch-optional', P, '        if stmp is None:\n            raise cs.Refusal("SCRATCH', '        if False:\n            raise cs.Refusal("SCRATCH'),
    ('workdir-empty-unchecked', P, 'and summary["workdir_empty"] and not hits', 'and not hits'),
    ('spill-not-failing', P, 'and not hits and not errs\n', 'and not errs\n'),
    ('spill-not-removed', P, '"spills_removed": remove_verified(stmp, hits),', '"spills_removed": True,'),
    ('seed-scan-off', P, 'names_a_secret(data, seeds, hashes)', 'names_a_secret(data, [], hashes)'),
    ('seed-name-scan-off', P, 'hit = names_a_secret(text, seeds, hashes)', 'hit = names_a_secret(text, [], hashes)'),
    ('snapshot-top-level-only', P, '    for dirpath, dirnames, filenames in os.walk(root, followlinks=False,\n                                                onerror=cs._raise if errors is None else errors.append):', '    for dirpath, dirnames, filenames in [next(os.walk(root))]:'),
    ('final-check-skipped', P, '        if not cs.seal_check(sealed, s["seal_text"])["ok"]:', '        if False:'),
    ('trap-removed', P, '        if started and workdir.is_dir():', '        if False:'),
    ('trap-spills-off', P, 'summary["trap_spills_removed"] = remove_verified(stmp, hits)', 'summary["trap_spills_removed"] = True'),
    ('trap-delete-coupled', P, '                summary["trap_spills_removed"] = "failed"\n            try:\n                summary["trap_deleted"] = cs.delete_plaintext(workdir)', '                summary["trap_spills_removed"] = "failed"\n                return 1, summary\n            try:\n                summary["trap_deleted"] = cs.delete_plaintext(workdir)'),
    ('internal-error-leaks', P, 'summary["refused"] = "terminated" if isinstance(e, SystemExit) else "internal error"', 'summary["refused"] = str(e)'),
    ('sigterm-not-installed', P, '    old = signal.signal(signal.SIGTERM, _term)', '    old = signal.getsignal(signal.SIGTERM)'),
    ('receipt-on-failure', P, '    if rc == 0:\n        print(f"covfix-receipt', '    if rc in (0, 1):\n        print(f"covfix-receipt'),
    ('break-line-missing', P, '    elif rc == cs.BREAK_RC:', '    elif False:'),
    ('pin-ignored', K, '        if not cs.HEX64.fullmatch(a.seal_sha256) or rec["seal_sha256"] != a.seal_sha256:', '        if False:'),
    ('check-message-leaks', K, 'rec = {"ok": False, "refused": "the seal file or the sealed dir cannot be read"}', 'rec = {"ok": False, "refused": "x"}'),
    ('index-check-skipped', S, 'index_ok = SEAL_FILE in regular and regular_read(sealed / SEAL_FILE) == seal_text.encode("ascii")', 'index_ok = True'),
    ('non-regular-uncounted', S, '            other += 1\n', '            pass\n'),
    ('non-regular-not-failing', S, 'not (missing or extra or mismatched or other)', 'not (missing or extra or mismatched)'),
    ('reader-opens-by-path', S, 'data = _read_in_dir(Path(seal_root), name)', 'data = regular_read(Path(seal_root) / name)'),
    ('reader-name-unchecked', S, ' or not (name == MANIFEST_CT or (name.endswith(".gpg") and ID.fullmatch(name[:-4])))', ''),
    ('dot-path-ok', S, 'p not in ("", ".")', 'p != ""'),
    ('dup-paths-ok', S, '\n          and len(set(man["paths"].values())) == len(man["paths"]))', ')'),
    ('agent-unconfirmed-ok', S, '        if not agent_down:\n            raise Refusal("the gpg-agent shutdown', '        if False:\n            raise Refusal("the gpg-agent shutdown'),
    ('chmod-failure-leaves-home', S, '    except BaseException:\n        shutil.rmtree(home, ignore_errors=True)\n', '    except BaseException:\n'),
    ('pin-unchecked', S, '        if h != self.pins[path]:', '        if False:'),
    ('gpg-unverified-at-exec', S, 'exe = (tools.verify(tools.gpg), tools.verify(tools.gpgconf))', 'exe = (tools.gpg, tools.verify(tools.gpgconf))'),
    ('gpgconf-unverified-at-exec', S, 'exe = (tools.verify(tools.gpg), tools.verify(tools.gpgconf))', 'exe = (tools.verify(tools.gpg), tools.gpgconf)'),
    ('unresolved-tool-ok', S, ' or os.path.realpath(p) != p', ''),
    ('same-file-tools-ok', S, ' if gpg != gpgconf else None', ''),
    ('sealcheck-pin-optional', K, 'ap.add_argument("--seal-sha256", required=True)', 'ap.add_argument("--seal-sha256", default="")'),
    ('group-not-ended', P, '            end_group(self.proc.pid)\n        self.proc = None', '        self.proc = None'),
    ('end-group-noop', P, '    deadline = time.monotonic() + GROUP_WAIT_S\n', '    return\n'),
    ('pg-owned-product-ok', P, ' or p.split("/")[0] in PG_OWNED', ''),
    ('link-target-unscanned', P, 'text = os.fsencode(rel) + (b"\\x00" + os.fsencode(sig[2]) if sig[0] == "l" else b"")', 'text = os.fsencode(rel)'),
    ('dirs-not-snapshotted', P, '        for name in dirnames + filenames:\n            p = os.path.join(dirpath, name)\n            try:', '        for name in filenames:\n            p = os.path.join(dirpath, name)\n            try:'),
    ('new-dir-not-removed', P, '                shutil.rmtree(p)', '                pass'),
    ('old-dir-removed', P, '                if not new:\n                    ok = False\n                    continue\n', ''),
    ('trap-disarmed-before-scan', P, '        errs: list = []\n', '        started = False\n        errs: list = []\n'),
    ('trap-forgets-sealed-hashes', P, '        seen["hashes"] |= known\n', ''),
    ('sig-ctime-dropped', P, 'return ("f", st.st_ino, st.st_mtime_ns, st.st_ctime_ns, st.st_size)', 'return ("f", st.st_ino, st.st_mtime_ns, st.st_size)'),
    ('unreadable-not-a-hit', P, '                hit = True                             # unverifiable', '                hit = False                             # unverifiable'),
    ('walk-error-raises', P, 'onerror=cs._raise if errors is None else errors.append):', 'onerror=cs._raise):'),
    ('lstat-error-raises', P, '                if errors is None:\n                    raise\n                errors.append(e)', '                raise'),
    ('scan-errors-ok', P, 'and not hits and not errs\n', 'and not hits\n'),
    ('trap-disarmed-on-failed-removal', P, '        if summary["spills_removed"]:\n            started = False', '        if True:\n            started = False'),
    ('trap-scan-strict', P, 'hits = spill_hits(stmp, changed(stmp, before, []), seen', 'hits = spill_hits(stmp, changed(stmp, before), seen'),
    ('required-ignored', P, '              and summary["required_products"] and summary["workdir_empty"]', '              and summary["workdir_empty"]'),
    ('required-count-loose', P, 'for r in rels) == q["count"] for q in req)', 'for r in rels) >= q["count"] for q in req)'),
    ('required-spec-unchecked', P, ' and _required_ok(spec["required"])', ''),
    ('required-empty-ok', P, '    return isinstance(req, list) and bool(req) and all(', '    return isinstance(req, list) and all('),
    ('required-dotdot-ok', P, ' and ".." not in r["pattern"].split("/")', ''),
    ('required-abs-ok', P, '        and not r["pattern"].startswith("/")', '        and True'),
    ('required-count-zero-ok', P, 'and type(r["count"]) is int and r["count"] >= 1 for r in req)', 'and type(r["count"]) is int and r["count"] >= 0 for r in req)'),
    ('required-keys-loose', P, 'isinstance(r, dict) and set(r) == {"pattern", "count"} and', 'isinstance(r, dict) and "pattern" in r and'),
    ('cgroup-check-skipped', P, '        summary["step_cgroup"] = step_cgroup_check()\n', ''),
    ('cgroup-extra-ok', P, '    if extra:\n', '    if False:\n'),
    ('cgroup-v1-ok', P, '        if len(lines) != 1 or not lines[0].startswith("0::/"):', '        if not lines:'),
    ('cgroup-unreadable-ok', P, '    except (OSError, ValueError) as e:\n        raise cs.Refusal("the job\'s cgroups cannot be read (a STOP)") from e', '    except (OSError, ValueError):\n        return {"pids": 0, "ancestors": 0}'),
    ('cgroup-ancestors-not-walked', P, '            allowed.add(pid)\n', '            break\n'),
    ('cgroup-any-ancestor', P, '            if pid not in where or pid in allowed:', '            if pid in allowed or pid <= 1:'),
    ('sigterm-not-held', S, '        old = signal.signal(signal.SIGTERM, record)', '        old = None'),
    ('sigterm-swallowed', S, '            if hold["pending"]:\n', '            if False:\n'),
    ('sigterm-handler-not-restored', S, '        if old is not None:\n            signal.signal(signal.SIGTERM, old)\n', '        if old is not None:\n'),
    ('sigterm-dfl-not-redelivered', S, '                elif old == signal.SIG_DFL:\n                    os.kill(os.getpid(), signal.SIGTERM)\n', ''),
    ('offthread-crashes', S, '    except ValueError:                                 # not the main thread', '    except TypeError:                                 # not the main thread'),
    ('r4-cgroup-own-only', P, '        for dirpath, _dirs, _files in os.walk(job, onerror=_raise, followlinks=False):', '        for dirpath in [str(Path(CGROUP_ROOT, *parts))]:'),
    ('r4-cgroup-user-dir-only', P, '        job = Path(CGROUP_ROOT, *parts[:jobs[0] + 1])', '        job = Path(CGROUP_ROOT, *parts[:-1])'),
    ('r4-cgroup-step-only', P, '        job = Path(CGROUP_ROOT, *parts[:jobs[0] + 1])', '        job = Path(CGROUP_ROOT, *parts[:jobs[0] + 2])'),
    ('r4-cgroup-walk-errors-ignored', P, 'os.walk(job, onerror=_raise, followlinks=False)', 'os.walk(job, onerror=None, followlinks=False)'),
    ('r4-cgroup-two-jobs-ok', P, '        if len(jobs) != 1:\n', '        if not jobs:\n'),
    ('r4-cgroup-job-pattern-loose', P, 'JOB_CGROUP = re.compile(r"job_[0-9]+")', 'JOB_CGROUP = re.compile(r"job_\\w+")'),
    ('r4-cgroup-sealer-absent-ok', P, '        if me not in where:\n', '        if False:\n'),
    ('r4-inventory-not-recorded', P, '            summary["step_cgroup_inventory"] = [dict(r, exe=exe_token(r["exe"], workdir, sealed)) for r in e.inventory]\n', '            pass\n'),
    ('r4-inventory-comm-dropped', P, '"comm": _proc_field(q, "comm")', '"comm": None'),
    ('r4-inventory-exe-dropped', P, '"exe": _proc_field(q, "exe")', '"exe": None'),
    ('r4-proc-field-exe-as-text', P, 'return os.readlink(p) if name == "exe" else p.read_bytes().decode("utf-8", "backslashreplace").strip()', 'return p.read_bytes().decode("utf-8", "backslashreplace").strip()'),
    ('r4-proc-field-unreadable-crashes', P, '    except OSError:\n        return None\n', '    except KeyError:\n        return None\n'),
    ('r4-gpg-not-killed-on-term', S, '        if hold["child"] is not None:\n            _kill(hold["child"])\n', ''),
    ('r4-gpg-not-killed-if-pending-first', S, '                if hold["pending"]:                    # a SIGTERM held before gpg started\n                    _kill(p)\n', ''),
    ('r4-child-not-registered', S, '                hold["child"] = p\n', '                pass\n'),
    ('r4-gpgconf-timeout-60', S, 'GPGCONF_TIMEOUT_S = 10', 'GPGCONF_TIMEOUT_S = 60'),
    ('r4-home-not-in-finally', S, '        finally:                                       # the home goes whatever the agent shutdown raised\n            shutil.rmtree(home, ignore_errors=True)', '        except ZeroDivisionError:\n            pass\n        shutil.rmtree(home, ignore_errors=True)'),
    ('r4-kill-oserror-crashes', S, '    try:\n        p.kill()\n    except OSError:\n        pass', '    try:\n        p.kill()\n    except KeyError:\n        pass'),
    # the director's 2026-11-25 GO on seed-bearing artifacts: M1, M2, (a), (b) and the gen-spec refusal
    ('sb-m1-guard-off', P, '    return leak_guard(rc, summary, seen["seeds"], seen["hashes"])', '    return rc, summary'),
    ('sb-m1-guard-no-seeds', P, 'leak_guard(rc, summary, seen["seeds"], seen["hashes"])', 'leak_guard(rc, summary, [], seen["hashes"])'),
    ('sb-m1-guard-no-hashes', P, 'leak_guard(rc, summary, seen["seeds"], seen["hashes"])', 'leak_guard(rc, summary, seen["seeds"], set())'),
    ('sb-m1-seeds-not-seen', P, 'seeds_b = seen["seeds"] = [', 'seeds_b = ['),
    ('sb-m1-trap-hashes-not-seen', P, '                seen["hashes"] |= hashes\n', ''),
    ('sb-m1-inventory-not-counted', P, 'out["step_cgroup_inventory"] = len(out["step_cgroup_inventory"])', 'out = {"refused": LEAK_REFUSAL}'),
    ('sb-m1-no-rescan', P, '    if hit(out):\n        out = {"refused": LEAK_REFUSAL}', '    if False:\n        out = {"refused": LEAK_REFUSAL}'),
    ('sb-m1-not-marked', P, '    out["summary_leak_redacted"] = True\n', ''),
    ('sb-m1-rc-kept', P, 'return (rc if rc == cs.BREAK_RC else 1), out', 'return rc, out'),
    ('sb-m1-break-not-kept', P, 'return (rc if rc == cs.BREAK_RC else 1), out', 'return 1, out'),
    ('sb-m1-exe-token-off', P, '[dict(r, exe=exe_token(r["exe"], workdir, sealed)) for r in e.inventory]', 'e.inventory'),
    ('sb-m1-token-no-workdir', P, '("<workdir>", workdir), ', ''),
    ('sb-m1-token-no-sealed', P, '("<sealed>", sealed), ', ''),
    ('sb-m1-token-no-scratch', P, ', ("<scratch>", os.environ.get("SCRATCH"))', ''),
    ('sb-m2-sums-file-missed', P, 'names_a_secret(data, seeds, hashes)', 'names_a_secret(data, seeds, set())'),
    ('sb-m2-name-hash-missed', P, 'hit = names_a_secret(text, seeds, hashes)', 'hit = names_a_secret(text, seeds, set())'),
    ('sb-m2-hex-lower-case-only', P, 'rb"(?=([0-9A-Fa-f]{64}))"', 'rb"(?=([0-9a-f]{64}))"'),
    ('sb-m2-hex-not-lowered', P, 'm.group(1).lower().decode()', 'm.group(1).decode()'),
    ('sb-m2-hex-not-overlapping', P, 'rb"(?=([0-9A-Fa-f]{64}))"', 'rb"([0-9A-Fa-f]{64})"'),
    ('sb-a-no-shuffle', S, '    _RNG.shuffle(order)\n', ''),
    ('sb-a-weak-rng', S, '_RNG = secrets.SystemRandom()', '_RNG = __import__("random").Random()'),
    ('sb-a-seal-ignores-permutation', S, '    for pid, rel in assigned.items():', '    for pid, rel in zip(assigned, rels):'),
    ('sb-b-compressed', S, '"--force-mdc",\n               "--compress-algo", "none")', '"--force-mdc")'),
    ('sb-g-spec-scan-off', P, '        if names_a_secret(json.dumps(spec, sort_keys=True).encode(), seeds_b, set()):\n', '        if False:\n'),
    ('sb-g-spec-raw-bytes', P, 'names_a_secret(json.dumps(spec, sort_keys=True).encode(), seeds_b, set())', 'names_a_secret(Path(spec_path).read_bytes(), seeds_b, set())'),
    # the director's rulings 3 and 4 of 2026-11-25 (SealedManifest, publish_guard) and the probe's argv
    ('sb-b-probe-argv-differs', P, 'cs.gpg_run(cs.GPG_ENCRYPT, passphrase, SYNTHETIC, tools)', 'cs.gpg_run(cs.GPG_ENCRYPT[:-2], passphrase, SYNTHETIC, tools)'),
    ('sm-repr-leaks', S, 'return f"<SealedManifest: {len(self._products)} products>"', 'return f"<SealedManifest: {self._paths}>"'),
    ('sm-picklable', S, '        raise TypeError("a SealedManifest is seed-bearing: it cannot be pickled or copied")', '        return object.__reduce_ex__(self, protocol)'),
    ('sm-writable', S, '    def __setattr__(self, name, value):\n        raise AttributeError("a SealedManifest is read-only")', '    def __setattr__(self, name, value):\n        object.__setattr__(self, name, value)'),
    ('sm-deletable', S, '    def __delattr__(self, name):\n        raise AttributeError("a SealedManifest is read-only")', '    def __delattr__(self, name):\n        object.__delattr__(self, name)'),
    ('sm-id-unchecked', S, '        if pid not in self._products:\n            raise Refusal("a requested id is not in the manifest")', '        if False:\n            raise Refusal("a requested id is not in the manifest")'),
    ('sm-ids-unsorted', S, '        return sorted(self._products)', '        return list(self._products)'),
    ('sm-aliases-input', S, 'object.__setattr__(self, "_paths", dict(paths))', 'object.__setattr__(self, "_paths", paths)'),
    ('sm-open-returns-dict', S, '    return SealedManifest(man["products"], man["paths"])', '    return man'),
    ('sm-read-product-takes-dict', S, '    if not isinstance(manifest, SealedManifest):\n        raise Refusal("read_product takes', '    if False:\n        raise Refusal("read_product takes'),
    ('pg-seed-decimal-off', S, 'needles |= {str(s).encode(), f"{s:x}".encode()}', 'needles |= {f"{s:x}".encode()}'),
    ('pg-seed-hex-off', S, 'needles |= {str(s).encode(), f"{s:x}".encode()}', 'needles |= {str(s).encode()}'),
    ('pg-case-sensitive', S, 'hit = any(n in low for n in needles)', 'hit = any(n in b for n in needles)'),
    ('pg-relpath-runs-off', S, '            needles |= {m.encode() for m in DIGIT_RUN.findall(comp)}', '            pass'),
    ('pg-relpath-run-11', S, 'DIGIT_RUN = re.compile(r"[0-9]{10,}")', 'DIGIT_RUN = re.compile(r"[0-9]{11,}")'),
    ('pg-hash-off', S, '        needles.add(manifest.sha256(pid).encode())', '        pass'),
    ('pg-fallback-always', S, '    if not hit and seeds is None:', '    if not hit:'),
    ('pg-fallback-off', S, '    if not hit and seeds is None:', '    if False:'),
    ('pg-range-hi', S, 'SEED_BASE_LO <= int(m.group(1)) < SEED_LIMIT', 'SEED_BASE_LO <= int(m.group(1)) <= SEED_LIMIT'),
    ('pg-range-lo', S, 'SEED_BASE_LO <= int(m.group(1)) < SEED_LIMIT', 'SEED_BASE_LO < int(m.group(1)) < SEED_LIMIT'),
    ('pg-fallback-unpadded', S, 'RANGE_TOKEN = re.compile(rb"(?<![0-9])0*([1-9][0-9]{9})(?![0-9])")', 'RANGE_TOKEN = re.compile(rb"(?<![0-9])([1-9][0-9]{9})(?![0-9])")'),
    ('pg-empty-list-ok', S, 'isinstance(seeds, list) and seeds and all(', 'isinstance(seeds, list) and all('),
    ('pg-bool-seed-ok', S, 'all(type(s) is int and s >= 0 for s in seeds)', 'all(isinstance(s, int) and s >= 0 for s in seeds)'),
    ('pg-dict-manifest-ok', S, 'isinstance(data, (bytes, str)) and isinstance(manifest, SealedManifest) and', 'isinstance(data, (bytes, str)) and'),
    # the director's 2026-11-25 rulings: the job check before generation, and publish_guard's one exemption
    ('pre-job-check-skipped', P, '        summary["step_cgroup_pre"] = step_cgroup_check()\n', ''),
    ('pg-exempt-unverified', S, '            if h != manifest.sha256(by_path[rel]):\n', '            if False:\n'),
    ('pg-exempt-not-allowlisted', S, '            if not any(fnmatch.fnmatchcase(rel, g) for g in allowlist):\n', '            if False:\n'),
    ('pg-exempt-not-in-manifest-ok', S, '            if rel not in by_path:\n                raise Refusal("publish_guard: a file published alongside is not in the manifest")\n', '            if rel not in by_path:\n                continue\n'),
    ('pg-exempt-all', S, '        if manifest.sha256(pid) not in exempt:\n', '        if not published:\n'),
    ('pg-exempt-inputs-unchecked', S, '    if published is not None or allowlist is not None:\n', '    if published and allowlist:\n'),
    ('specpin-off', P, '    if hashlib.sha256(raw).hexdigest() != sha256:\n', '    if False:\n'),
    ('specpin-second-read', P, '        spec = json.loads(raw, object_pairs_hook=_no_duplicate_keys)', '        spec = json.loads(Path(path).read_bytes(), object_pairs_hook=_no_duplicate_keys)'),
    ('specpin-arg-unchecked', P, '    if not cs.HEX64.fullmatch(a.gen_spec_sha256):\n', '    if False:\n'),
    ('envkeep-dup-ok', P, '    if len(set(spec["env_keep"])) != len(spec["env_keep"]):\n', '    if False:\n'),
    ('envkeep-unset-ok', P, '    if not all(k in os.environ for k in spec["env_keep"]):\n', '    if False:\n'),
    ('envkeep-slurm-only', P, '    if not all(k in os.environ for k in spec["env_keep"]):\n',
     '    if not all(k in os.environ for k in spec["env_keep"] if k.startswith("SLURM_")):\n'),
    ('envset-skipped', P, '        env.update(spec["env_set"])\n', ''),
    ('envset-conflict-off', P, '    if any(os.environ.get(k, v) != v for k, v in spec["env_set"].items()):\n', '    if False:\n'),
    ('envset-overlap-ok', P, '          and not {"TMPDIR", "SCRATCH"} & set(spec["env_set"]) and not set(spec["env_set"]) & set(spec["env_keep"]))', '          and not {"TMPDIR", "SCRATCH"} & set(spec["env_set"]))'),
    ('envset-tmpdir-ok', P, '          and not {"TMPDIR", "SCRATCH"} & set(spec["env_set"]) and not set(spec["env_set"]) & set(spec["env_keep"]))', '          and not {"SCRATCH"} & set(spec["env_set"]) and not set(spec["env_set"]) & set(spec["env_keep"]))'),
    ('envset-name-unchecked', P, '          and all(ENV_NAME.fullmatch(k) for k in spec["env_set"])\n', ''),
    ('envset-value-unchecked', P, '          and all(isinstance(v, str) and "\\0" not in v for v in spec["env_set"].values())\n', ''),
    ('envset-nul-ok', P, '          and all(isinstance(v, str) and "\\0" not in v for v in spec["env_set"].values())\n', '          and all(isinstance(v, str) for v in spec["env_set"].values())\n'),
    ('envset-not-dict-ok', P, '          and isinstance(spec["env_set"], dict)\n', ''),
    # W/tmp at mode 0700, pg_generate.sh's contract (the director's ruling of 2026-11-26)
    ('tmp-plain-mkdir', P, '        private_dir(workdir / "tmp")\n', '        (workdir / "tmp").mkdir()\n'),
    ('tmp-chmod-off', P, '    os.chmod(path, 0o700)\n', ''),
    # round 6 (codex-school2 round 5, the director's ruling of 2026-11-27)
    ('r5-verify-under-hold', S, '    exe = (tools.verify(tools.gpg), tools.verify(tools.gpgconf))   # hashed before the hold: never under a SIGTERM\n    hold: dict | None = {"pending": [], "child": None}\n\n    def record(signum, frame):\n        hold["pending"].append(signum)\n        if hold["child"] is not None:\n            _kill(hold["child"])\n\n    try:\n        old = signal.signal(signal.SIGTERM, record)\n    except ValueError:                                 # not the main thread: no handler to hold it\n        old, hold = None, None\n    try:\n        return _gpg_run(argv, passphrase, payload, exe, hold)\n', '    hold: dict | None = {"pending": [], "child": None}\n\n    def record(signum, frame):\n        hold["pending"].append(signum)\n        if hold["child"] is not None:\n            _kill(hold["child"])\n\n    try:\n        old = signal.signal(signal.SIGTERM, record)\n    except ValueError:                                 # not the main thread: no handler to hold it\n        old, hold = None, None\n    try:\n        exe = (tools.verify(tools.gpg), tools.verify(tools.gpgconf))\n        return _gpg_run(argv, passphrase, payload, exe, hold)\n'),
    ('r5-comm-strict-decode', P, '.decode("utf-8", "backslashreplace")', '.decode("utf-8")'),
    ('r5-hash-file-error-raises', P, '        except OSError:\n            unreadable += 1\n', '        except OSError:\n            raise\n'),
    ('r5-unreadable-not-counted', P, '            unreadable += 1\n', '            pass\n'),
    ('r5-inventory-kept-when-unreadable', P, '        if isinstance(summary.get("step_cgroup_inventory"), list):\n            summary["step_cgroup_inventory"] = len(summary["step_cgroup_inventory"])\n    return leak_guard', '    return leak_guard'),
    ('r5-duplicate-keys-allowed', P, 'json.loads(raw, object_pairs_hook=_no_duplicate_keys)', 'json.loads(raw)'),
    ('r5-scratch-keepable', P, '          and not {"TMPDIR", "SCRATCH"} & set(spec["env_keep"]) and _required_ok', '          and not {"TMPDIR"} & set(spec["env_keep"]) and _required_ok'),
    ('r5-scratch-settable', P, '          and not {"TMPDIR", "SCRATCH"} & set(spec["env_set"]) and not', '          and not {"TMPDIR"} & set(spec["env_set"]) and not'),
    ('r5-digest-token-not-exempt', S, '        low = re.sub(rb"(?<![0-9a-f])" + h.encode() + rb"(?![0-9a-f])", b"-" * 64, low)\n', '        pass\n'),
    ('r5-digest-substring-exempt', S, 'rb"(?<![0-9a-f])" + h.encode() + rb"(?![0-9a-f])"', 'h.encode()'),
]


def run_tests(d: Path) -> tuple[int, str]:
    env = dict(os.environ, OMP_NUM_THREADS="1")
    try:                                               # -f: a killed mutant stops at its first failure
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", "-f", "test_covfix_seal.py"], cwd=d, env=env,
                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                           timeout=3600, text=True)
    except subprocess.TimeoutExpired:
        return 0, "TIMEOUT after 3600 s (not counted as a kill)"
    lines = r.stderr.splitlines()
    named = [ln for ln in lines if ln.startswith(("FAIL: ", "ERROR: "))]
    if r.returncode != 0 and (not named or any("_FailedTest" in ln for ln in named)):
        return -1, "HARNESS: " + (lines[-1] if lines else "no stderr")
    return r.returncode, (named[0] if named else (lines[-1] if lines else ""))


def one(m) -> tuple[str, str, str]:
    mid, f, old, new = m
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        for name in FILES:
            shutil.copy2(HERE / name, d / name)
        if m[0] != "baseline":
            src = (d / f).read_text()
            if src.count(old) != 1:
                return mid, "NOT APPLIED", f"pattern occurs {src.count(old)} times"
            (d / f).write_text(src.replace(old, new))
        rc, why = run_tests(d)
    if why.startswith("TIMEOUT"):
        return mid, "TIMEOUT", why
    return mid, ("killed" if rc > 0 else "HARNESS FAILURE" if rc < 0 else "SURVIVED") if mid != "baseline" \
        else ("pass" if rc == 0 else "FAIL"), why


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--only", default="", help="comma-separated mutant ids (a partial rerun; the default runs all)")
    a = ap.parse_args()
    ids = [m[0] for m in MUTANTS]
    want = [x for x in a.only.split(",") if x]
    unknown = [x for x in want if x not in ids]
    if unknown:
        print(f"unknown mutant ids: {unknown}")
        return 2
    chosen = [m for m in MUTANTS if not want or m[0] in want]
    mid, status, why = one(("baseline", S, "", ""))
    print(f"baseline {status} {why}", flush=True)
    if status != "pass":
        return 2
    bad = []
    with ThreadPoolExecutor(a.jobs) as ex:
        for mid, status, why in ex.map(one, chosen):
            print(f"{mid}: {status} {why}", flush=True)
            if status != "killed":
                bad.append(mid)
    print(f"{len(chosen) - len(bad)}/{len(chosen)} killed; survived, harness or not applied: {bad}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
