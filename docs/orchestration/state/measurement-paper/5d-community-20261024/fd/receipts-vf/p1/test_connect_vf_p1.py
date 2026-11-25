"""Dry-run tests of connect-vf-p1.sh's gates and stage-vfp1.sh's checks, run locally against shims.

A copy of each script has only its site constants replaced (the run directory, the bound commit, the clone URL, the
conda paths, the host name and /dev/shm), pointing at a temporary tree: a small local origin holding the 22 bound
files at their committed bytes (so the blob ids are the real ones), a fake conda hook, and a fake python3 whose
behaviour each test sets. Every gate is driven to refuse once, and the happy path is run end to end.
Run: python3 -B test_connect_vf_p1.py (needs git, bash and this checkout's history at c0fa0d01)."""
import base64
import hashlib
import os
import re
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path(subprocess.check_output(["git", "-C", str(HERE), "rev-parse", "--show-toplevel"], text=True).strip())
CONNECT = HERE / "connect-vf-p1.sh"
STAGER = HERE / "stage-vfp1.sh"
PIN = "c0fa0d01aa05d5b6bb9793919768491d8d8a0c23"
BA0 = "/pscratch/sd/j/josephrb/vf-20261125-p1"
URL = "https://github.com/josephbaileyy/MINERvA-OmniFold.git"
HOOK = "/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda"

FAKE_PY = r"""#!/bin/bash
# fake python3: behaviour from FAKE_* variables; every call's argv is appended to $FAKE_ARGV
[ -n "$FAKE_ARGV" ] && printf '%s\n' "$*" >> "$FAKE_ARGV" && printf 'XDG=%s\n' "$XDG_CACHE_HOME" >> "$FAKE_ARGV.env"
if [ "$1" = -I ] && [ "$2" = -B ] && [ "$3" = -c ]; then [ -n "$FAKE_PROBE_FAIL" ] && exit 1; echo "${FAKE_VERSIONS:-3.11.14 1.26.4 3.10.8}"; exit 0; fi
for a in "$@"; do
  if [ "$a" = unittest ]; then
    [ -n "$FAKE_DIRTY" ] && touch ../../left-behind.txt
    printf '%b' "${FAKE_TESTS_OUT:-test_a (m.C.test_a) ... ok\n\n----------------------------------------------------------------------\nRan 541 tests in 1.0s\n\nOK\n}" >&2
    [ -n "$FAKE_STDOUT_AFTER" ] && { sleep 0.2; echo "late stdout line after the footer"; }
    exit "${FAKE_TESTS_RC:-0}"
  fi
  case "$a" in *fd_vf_addition.py)
    mkdir -p "$PWD/run/S"; [ -n "$FAKE_NO_RUN_FILES" ] || echo x > "$PWD/run/S/out.json"
    [ -n "$FAKE_UNREADABLE" ] && mkdir -p "$PWD/run/locked" && chmod 000 "$PWD/run/locked"
    echo "chain done"; exit "${FAKE_CHAIN_RC:-0}";;
  esac
done
echo "fake python: unexpected $*" >&2; exit 99
"""

FAKE_CONDA = r"""#!/bin/bash
# fake conda: `conda shell.bash hook` prints a hook defining conda(); FAKE_HOOK_EMPTY prints nothing
[ -n "$FAKE_HOOK_EMPTY" ] && exit 0
cat <<'H'
conda() { [ "$1" = activate ] || return 1; [ -n "$FAKE_ACTIVATE_FAIL" ] && return 1
  export CONDA_PREFIX="${FAKE_PREFIX:-$2}"; [ -n "$FAKE_NO_PATH" ] || export PATH="$2/bin:$PATH"; }
H
"""


def sh(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    path.chmod(0o755)


class Site:
    """A temporary site: origin repo with the 22 bound files, shims, and the script copies."""

    def __init__(self):
        self.t = Path(tempfile.mkdtemp(prefix="vfp1-"))
        want = re.findall(r'^  "([0-9a-f]{40}) (\S+)"$', CONNECT.read_text(), re.M)
        assert len(want) == 22, len(want)
        o = self.t / "origin"
        subprocess.run(["git", "init", "-q", str(o)], check=True)
        for _, p in want:
            q = o / p
            q.parent.mkdir(parents=True, exist_ok=True)
            q.write_bytes(subprocess.check_output(["git", "-C", str(REPO), "show", f"{PIN}:{p}"]))
        g = ["git", "-C", str(o), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(g + ["add", "-A"], check=True)
        subprocess.run(g + ["commit", "-qm", "bound files"], check=True)
        self.mini = subprocess.check_output(["git", "-C", str(o), "rev-parse", "HEAD"], text=True).strip()
        self.origin, self.want = o, want
        self.bin = self.t / "bin"
        sh(self.bin / "hostname", '#!/bin/bash\n[ -n "$FAKE_HOST_FAIL" ] && exit 1\necho "${FAKE_HOST:-login02}"\n')
        sh(self.bin / "timeout", '#!/bin/bash\nshift\nexec "$@"\n')
        sh(self.bin / "date", '#!/bin/bash\n[ -n "$FAKE_DATE_FAIL" ] && [ -d "$PWD/run" ] && exit 1\nexec /bin/date "$@"\n')
        sh(self.bin / "nice", '#!/bin/bash\n[ -n "$FAKE_NICE_HANG" ] && { sleep 3; exit 0; }\n'
                              '[ -n "$FAKE_NICE_LATE" ] && sleep 2\nexec /usr/bin/nice "$@"\n')
        sh(self.bin / "ps", '#!/bin/bash\n[ -n "$FAKE_PS_FAIL" ] && exit 1\nprintf "%b" "${FAKE_PS_OUT-  1 /sbin/init\\n}"\n')
        if shutil.which("setsid") is None:                # macOS has none; login02 has util-linux's
            sh(self.bin / "setsid", '#!/bin/bash\nexec /usr/bin/python3 -c "import os, sys; os.setsid(); '
                                    'os.execvp(sys.argv[1], sys.argv[1:])" "$@"\n')
        self.env = self.t / "envs" / "root_6_28"
        sh(self.env / "bin" / "python3", FAKE_PY)
        self.conda = self.t / "conda"
        sh(self.conda, FAKE_CONDA)
        self.shm = self.t / "shm"
        self.shm.mkdir()

    def connect_copy(self, n: int, mutate=None) -> tuple[Path, Path]:
        ba = self.t / f"BA{n}"
        s = CONNECT.read_text()
        for a, b in ((BA0, str(ba)), (PIN, self.mini), (URL, str(self.origin)), (HOOK, str(self.conda)),
                     ("$HOME/.conda/envs/root_6_28", str(self.env)), ("/pscratch/sd/j/josephrb/gencmp-e", "/x/gencmp-e")):
            assert a in s, a
            s = s.replace(a, b)
        assert re.search(r"^BA=/pscratch", s, re.M) is None and "github.com" not in s, "a production path survived"
        if mutate:
            s = mutate(s)
        p = self.t / f"connect{n}.sh"
        p.write_text(s)
        return p, ba

    def run(self, script: Path, args=(), stdin=None, **fake) -> subprocess.CompletedProcess:
        env = {"PATH": f"{self.bin}:/usr/bin:/bin:/usr/sbin:/sbin", "HOME": str(self.t), "USER": os.environ.get("USER", "u")}
        env.update({(k.upper() if k.startswith("vfp1_") else f"FAKE_{k.upper()}"): str(v) for k, v in fake.items()})
        return subprocess.run(["bash", str(script), *args], capture_output=True, text=True, env=env, input=stdin,
                              timeout=120)

    def close(self):
        for root, dirs, _ in os.walk(self.t):
            for d in dirs:
                try:
                    os.chmod(os.path.join(root, d), 0o755)
                except OSError:
                    pass
        shutil.rmtree(self.t, ignore_errors=True)


class Connect(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Site()
        cls.n = 0

    @classmethod
    def tearDownClass(cls):
        cls.s.close()

    def go(self, mutate=None, pre=None, **fake):
        type(self).n += 1
        p, ba = self.s.connect_copy(self.n, mutate)
        if pre:
            pre(ba)
        return self.s.run(p, argv=self.s.t / f"argv{self.n}", **fake), ba

    def stopped(self, r, text, rc=9):
        self.assertEqual(r.returncode, rc, r.stdout + r.stderr)
        self.assertIn("STOP", r.stdout)
        self.assertIn(text, r.stdout)

    def test_the_happy_path_runs_the_chain_and_writes_its_receipts(self):
        r, ba = self.go()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn(f"deploy ok at {self.s.mini}: 22 blobs", r.stdout)
        self.assertIn("tests rc=0 PASS", r.stdout)
        self.assertEqual(len((ba / "receipts/deploy-blobs.txt").read_text().splitlines()), 22)
        self.assertEqual((ba / "receipts/env.txt").read_text(), "3.11.14 1.26.4 3.10.8\n")
        self.assertIn("./S/out.json", (ba / "receipts/run.sha256").read_text())
        self.assertIn("porcelain after: empty", r.stdout)
        self.assertIn("chain rc=0", (ba / "receipts/host.txt").read_text())
        calls = (self.s.t / f"argv{self.n}").read_text().splitlines()
        self.assertEqual(calls[1].split(), ["-B", "-m", "unittest", "-v", "test_fd_vf_addition", "test_fd_cpl_addition",
            "test_fd_g_compare", "test_fd_g_diag", "test_fd_g_followup", "test_fd_flux_boot", "test_fd_f0_regrade",
            "test_fd_g_figures", "test_fd_deposit_candidate", "test_fd_data_product", "test_fd_gencmp_e.Sets",
            "test_fd_gencmp_e.Stage", "test_fd_gencmp_e.Materialize", "test_fd_gencmp_e.Chain"])
        self.assertEqual(calls[2].split(), ["-I", "-B", f"{ba}/deploy/nd-unfolding/fd_vf_addition.py", "chain",
            "--scratch", "/pscratch/sd/j/josephrb", "--run-e", "/x/gencmp-e-20261101/rerun1", "--run-dir", f"{ba}/run"])
        self.assertEqual(calls[0].split()[:3], ["-I", "-B", "-c"])
        self.assertEqual(set((self.s.t / f"argv{self.n}.env").read_text().splitlines()), {f"XDG={ba}/tmp/xdg-cache"})

    def test_stdout_after_the_footer_does_not_stop_a_passing_suite(self):
        r, _ = self.go(stdout_after=1)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_two_closing_blocks_refuse(self):
        two = r"----------\nRan 3 tests in 0.1s\n\nOK (skipped=1)\n----------\nRan 541 tests in 0.1s\n\nOK\n"
        self.stopped(self.go(tests_out=two)[0], "2 Ran lines")

    def test_a_failed_end_timestamp_makes_a_successful_chain_exit_7(self):
        r, ba = self.go(date_fail=1)
        self.assertEqual(r.returncode, 7, r.stdout + r.stderr)
        self.assertIn("RECEIPT: date", r.stdout)

    def test_another_host_refuses(self):
        r, ba = self.go(host="login37")
        self.stopped(r, "not login02", 2)
        self.assertFalse(ba.exists())

    def test_a_failed_hostname_refuses(self):
        self.stopped(self.go(host_fail=1)[0], "hostname failed", 2)

    def test_an_existing_run_directory_refuses_and_is_not_written(self):
        r, ba = self.go(pre=lambda ba: (ba.mkdir(), (ba / "keep").write_text("k")))
        self.stopped(r, "exists", 2)
        self.assertEqual(sorted(q.name for q in ba.iterdir()), ["keep"])

    def test_a_symlink_at_the_run_directory_refuses(self):
        r, ba = self.go(pre=lambda ba: ba.symlink_to(self.s.t))
        self.stopped(r, "exists", 2)

    def test_a_failed_clone_refuses(self):
        self.stopped(self.go(mutate=lambda s: s.replace(str(self.s.origin), "/nonexistent/origin"))[0], "clone")

    def test_a_head_that_is_not_the_bound_commit_refuses(self):
        self.stopped(self.go(mutate=lambda s: s.replace(f'"$head" = "$M"', '"$head" = "0000"'))[0], "not the bound")

    def test_a_dirty_or_unreadable_porcelain_refuses(self):
        r, _ = self.go(mutate=lambda s: s.replace('porcelain_empty || stop "porcelain after checkout"',
                                                  'touch "$BA/deploy/x"; porcelain_empty || stop "porcelain after checkout"'))
        self.stopped(r, "porcelain after checkout")
        r, _ = self.go(mutate=lambda s: s.replace('porcelain_empty || stop "porcelain after checkout"',
                                                  'mv "$BA/deploy/.git" "$BA/deploy/.g"; porcelain_empty || stop "porcelain after checkout"'))
        self.stopped(r, "porcelain after checkout")

    def test_an_untracked_file_is_seen_even_if_git_config_hides_untracked(self):
        r, _ = self.go(mutate=lambda s: s.replace(
            'porcelain_empty || stop "porcelain after checkout"',
            'git -C "$BA/deploy" config status.showUntrackedFiles no; touch "$BA/deploy/u"; '
            'porcelain_empty || stop "porcelain after checkout"'))
        self.stopped(r, "porcelain after checkout")

    def test_a_blob_that_differs_refuses(self):
        b, p = self.s.want[3]
        self.stopped(self.go(mutate=lambda s: s.replace(f'"{b} {p}"', f'"{"0" * 40} {p}"'))[0], f"blob {p}")

    def test_a_blob_list_that_is_not_22_refuses(self):
        b, p = self.s.want[0]
        self.stopped(self.go(mutate=lambda s: s.replace(f'  "{b} {p}"\n', ""))[0], "21 entries, not 22")

    def test_an_unresolvable_path_refuses(self):
        b, p = self.s.want[0]
        self.stopped(self.go(mutate=lambda s: s.replace(f'"{b} {p}"', f'"{b} no/such/file"'))[0], "cannot resolve")

    def test_an_empty_conda_hook_refuses(self):
        self.stopped(self.go(hook_empty=1)[0], "conda hook")

    def test_a_failed_activation_refuses(self):
        self.stopped(self.go(activate_fail=1)[0], "conda activate")

    def test_a_wrong_prefix_refuses(self):
        self.stopped(self.go(prefix="/elsewhere")[0], "CONDA_PREFIX")

    def test_python3_not_the_environments_refuses(self):
        self.stopped(self.go(no_path=1)[0], "python3 is")

    def test_a_failed_version_probe_refuses(self):
        self.stopped(self.go(probe_fail=1)[0], "version probe failed")

    def test_other_versions_refuse(self):
        self.stopped(self.go(versions="3.11.14 1.26.4 3.10.7")[0], "not E-A2's renderer")

    def test_failed_tests_refuse(self):
        self.stopped(self.go(tests_rc=1)[0], "tests (rc 1")

    def test_zero_tests_refuse(self):
        self.stopped(self.go(tests_out=r"\n----------\nRan 0 tests in 0.0s\n\nOK\n")[0], "Ran 0 tests")

    def test_a_narrowed_selection_refuses(self):
        self.stopped(self.go(tests_out=r"\n----------\nRan 540 tests in 1.0s\n\nOK\n")[0], "Ran 540 tests")

    def test_a_skip_refuses(self):
        r, _ = self.go(tests_out=r"t (m.C.t) ... skipped 'x'\n----------\nRan 541 tests in 0.1s\n\nOK (skipped=1)\n")
        self.stopped(r, "OK (skipped=1)")

    def test_no_result_line_refuses(self):
        self.stopped(self.go(tests_out=r"----------\nRan 541 tests in 0.1s\n")[0], "FAIL")

    def test_a_passing_suite_that_prints_the_word_skipped_still_passes(self):
        r, _ = self.go(tests_out=r"t (m.C.t) ... ok\nthe word skipped= in a message\n----------\nRan 541 tests in 0.1s\n\nOK\n")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_tests_that_leave_a_file_in_the_deploy_refuse(self):
        self.stopped(self.go(dirty=1)[0], "left files in the deploy")

    def test_the_chains_exit_code_is_the_scripts(self):
        r, ba = self.go(chain_rc=3)
        self.assertEqual(r.returncode, 3)
        self.assertIn("chain rc=3", (ba / "receipts/host.txt").read_text())

    def test_an_incomplete_run_receipt_makes_a_successful_chain_exit_7(self):
        if os.geteuid() == 0:
            self.skipTest("root reads mode-000 directories")
        r, _ = self.go(unreadable=1)
        self.assertEqual(r.returncode, 7, r.stdout + r.stderr)
        self.assertIn("RECEIPT: run.sha256 incomplete", r.stdout)

    def test_an_empty_run_manifest_makes_a_successful_chain_exit_7(self):
        r, _ = self.go(no_run_files=1)
        self.assertEqual(r.returncode, 7, r.stdout + r.stderr)
        self.assertIn("RECEIPT: run.sha256 empty", r.stdout)

    def test_a_dirty_deploy_after_the_chain_makes_a_successful_chain_exit_8(self):
        r, _ = self.go(mutate=lambda s: s.replace('final=$rc\n', 'final=$rc\ntouch "$BA/deploy/late"\n'))
        self.assertEqual(r.returncode, 8, r.stdout + r.stderr)
        self.assertIn("porcelain after: NOT empty", r.stdout)

    def test_temporary_files_stay_under_the_run_directory(self):
        r, ba = self.go(mutate=lambda s: s.replace('echo "deploy ok at', 'echo "tmpdir=$TMPDIR"; echo "deploy ok at'))
        self.assertIn(f"tmpdir={ba}/tmp", r.stdout)


HARMLESS = b"echo harmless worker\nexit 3\n"


class Stager(unittest.TestCase):
    """The stager's copy has /dev/shm and $BA moved into the temporary tree and, always, the embedded connect swapped
    for a harmless worker (WANT for its sha256), so no test can run the production connect, even if a guard regresses.
    Only test_the_embedded_bytes_are_the_connect_script reads the real payload, and it executes nothing."""

    @classmethod
    def setUpClass(cls):
        cls.s = Site()

    @classmethod
    def tearDownClass(cls):
        cls.s.close()

    def tearDown(self):
        for q in self.s.shm.iterdir():
            q.unlink()
        shutil.rmtree(self.s.t / "SBA", ignore_errors=True)

    @property
    def S(self) -> Path:
        return self.s.shm / "vfp1.sh"

    @property
    def L(self) -> Path:
        return self.s.shm / "vfp1.log"

    def copy(self, mutate=None, worker: bytes = HARMLESS) -> Path:
        s = STAGER.read_text().replace("/dev/shm", str(self.s.shm)).replace(BA0, str(self.s.t / "SBA"))
        s = re.sub(r"(<<'B64'[^\n]*\n).*?(\nB64\n)", lambda m: m.group(1) + base64.b64encode(worker).decode()
                   + m.group(2), s, flags=re.S)
        s = re.sub(r"^WANT=[0-9a-f]{64}$", "WANT=" + hashlib.sha256(worker).hexdigest(), s, flags=re.M)
        assert "/pscratch" not in s and base64.b64encode(CONNECT.read_bytes()).decode()[:200] not in s
        if mutate:
            s = mutate(s)
        p = self.s.t / "stage.sh"
        p.write_text(s)
        return p

    def receipts(self) -> Path:
        r = self.s.t / "SBA" / "receipts"
        r.mkdir(parents=True)
        return r

    def pair(self, tail: str, head: str | None = None, script: bytes = HARMLESS) -> None:
        self.S.write_bytes(script)
        h = head if head is not None else f"vfp1 sha {hashlib.sha256(HARMLESS).hexdigest()}\n"
        self.L.write_text(h + "worker start 4242\n" + tail)

    def run_(self, args, **kw):
        return self.s.run(self.copy(kw.pop("mutate", None)), args, **kw)

    def test_the_embedded_bytes_are_the_connect_script(self):
        s = STAGER.read_text()
        data = base64.b64decode(re.search(r"<<'B64'[^\n]*\n(.*?)\nB64\n", s, re.S).group(1))
        self.assertEqual(data, CONNECT.read_bytes())
        self.assertIn(f"\nWANT={hashlib.sha256(data).hexdigest()}\n", s)

    def test_start_refuses_on_another_host(self):
        r = self.run_(["start"], host="login37")
        self.assertEqual(r.returncode, 2)
        self.assertEqual(list(self.s.shm.iterdir()), [])

    def test_start_refuses_when_ps_fails_or_prints_nothing(self):
        for fake in ({"ps_fail": 1}, {"ps_out": ""}):
            r = self.run_(["start"], **fake)
            self.assertEqual(r.returncode, 2, fake)
            self.assertIn("ps failed", r.stdout)

    def test_start_refuses_while_a_chain_or_worker_of_mine_runs(self):
        py = f"{self.s.t}/.conda/envs/root_6_28/bin/python3"
        for line in (f"  77 {py} -I -B /x/deploy/nd-unfolding/fd_vf_addition.py chain --scratch /p\\n",
                     f"  78 bash {self.S}\\n",
                     f'  79 bash -c echo x; bash "$1" vfp1 {self.S}\\n',
                     f'  80 setsid nice -n 19 bash -c echo x; bash "$1" vfp1 {self.S}\\n'):
            r = self.run_(["start"], ps_out=line)
            self.assertEqual(r.returncode, 2, line)
            self.assertIn("already running", r.stdout)
        self.assertEqual(list(self.s.shm.iterdir()), [])

    def test_unrelated_processes_that_mention_the_names_do_not_block(self):
        py = f"{self.s.t}/.conda/envs/root_6_28/bin/python3"
        noise = (f"  81 vim /tmp/fd_vf_addition.py chain\\n  82 less notes-vfp1-run.txt\\n"
                 f"  83 grep {py} -I -B /x/nd-unfolding/fd_vf_addition.py chain x\\n  84 cat {self.S}\\n")
        r = self.run_(["start"], ps_out=noise, vfp1_wait=5)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_start_refuses_an_existing_run_directory_or_an_unfinished_pair(self):
        (self.s.t / "SBA").mkdir()
        self.assertIn("exists", self.run_(["start"]).stdout)
        shutil.rmtree(self.s.t / "SBA")
        self.L.write_text("old")
        r = self.run_(["start"])
        self.assertEqual(r.returncode, 2)
        self.assertEqual(self.L.read_text(), "old")

    def test_start_refuses_a_symlink_at_either_name_and_removes_nothing(self):
        for name in ("vfp1.sh", "vfp1.log"):
            for target in ("/dev/null", str(self.s.t / "no-such-target")):    # live and dangling
                (self.s.shm / name).symlink_to(target)
                r = self.run_(["start"])
                self.assertEqual(r.returncode, 2, r.stdout)
                self.assertTrue((self.s.shm / name).is_symlink())
                (self.s.shm / name).unlink()

    def test_a_symlink_raced_in_before_the_create_is_refused_and_kept(self):
        race = lambda s: s.replace('newfile() { absent "$1" || return 1; ',
                                   'newfile() { absent "$1" || return 1; ln -s /dev/null "$1"; ')
        r = self.run_(["start"], mutate=race)
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("nothing removed", r.stdout)
        self.assertTrue(self.S.is_symlink())

    def test_start_refuses_a_copy_whose_sha_differs_and_removes_only_its_own_files(self):
        r = self.run_(["start"], mutate=lambda s: re.sub(r"^WANT=[0-9a-f]{64}$", "WANT=" + "0" * 64, s, flags=re.M))
        self.assertEqual(r.returncode, 9, r.stdout)
        self.assertEqual(list(self.s.shm.iterdir()), [])

    def test_a_launcher_that_never_runs_the_wrapper_is_unconfirmed_and_left_alone(self):
        r = self.run_(["start"], nice_hang=1, vfp1_wait=1)
        self.assertEqual(r.returncode, 3, r.stdout)
        self.assertIn("UNCONFIRMED", r.stdout)
        self.assertIn("nothing was signalled", r.stdout)
        self.assertTrue(self.S.exists() and self.L.exists())
        f = self.run_(["finish"], ps_out="  1 /sbin/init\\n")
        self.assertEqual(f.returncode, 2)                  # no worker start: finish keeps both files
        self.assertTrue(self.S.exists() and self.L.exists())

    def test_a_late_wrapper_runs_to_its_exit_and_finish_archives_it(self):
        import time
        r = self.run_(["start"], nice_late=1, vfp1_wait=1)
        self.assertEqual(r.returncode, 3, r.stdout)
        for _ in range(80):
            if self.L.read_text().endswith("worker exit=3\n"):
                break
            time.sleep(0.1)
        self.assertRegex(self.L.read_text(), r"\nworker start \d+\nharmless worker\nworker exit=3\n$")
        self.receipts()
        f = self.run_(["finish"])
        self.assertEqual(f.returncode, 3, f.stdout)
        self.assertEqual(list(self.s.shm.iterdir()), [])

    def test_the_stager_never_signals_a_process(self):
        self.assertNotRegex(STAGER.read_text().split("<<'B64'")[0] + STAGER.read_text().split("\nB64\n")[-1],
                            r"\bkill\b|pkill|killall")

    def test_finish_refuses_a_run_directory_that_is_now_a_symlink(self):
        rec = self.receipts()
        self.pair("worker exit=0\n")
        moved = self.s.t / "moved"
        (self.s.t / "SBA").rename(moved)
        (self.s.t / "SBA").symlink_to(moved)
        r = self.run_(["finish"])
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertFalse((moved / "receipts" / "vfp1.log").exists())
        self.assertTrue(self.S.exists() and self.L.exists())
        (self.s.t / "SBA").unlink()
        shutil.rmtree(moved)

    def test_start_launches_the_worker_and_finish_returns_its_exit(self):
        import time
        r = self.run_(["start"], vfp1_wait=5)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for _ in range(50):
            if self.L.read_text().endswith("worker exit=3\n"):
                break
            time.sleep(0.1)
        lines = self.L.read_text().splitlines()
        self.assertEqual(lines[0], f"vfp1 sha {hashlib.sha256(HARMLESS).hexdigest()}")
        self.assertRegex(lines[1], r"^worker start \d+$")
        self.assertEqual(lines[2:], ["harmless worker", "worker exit=3"])
        rec = self.receipts()
        f = self.run_(["finish"])
        self.assertEqual(f.returncode, 3, f.stdout)
        self.assertEqual(list(self.s.shm.iterdir()), [])
        self.assertEqual((rec / "vfp1.log").read_text().splitlines()[-1], "worker exit=3")

    def test_finish_refuses_missing_or_foreign_files(self):
        self.assertEqual(self.run_(["finish"]).returncode, 2)
        self.receipts()
        for kw, why in (({"head": "something else\n"}, "not this stager's"),
                        ({"script": b"echo other\n"}, "not WANT")):
            self.pair("worker exit=0\n", **kw)
            r = self.run_(["finish"])
            self.assertEqual(r.returncode, 2, r.stdout)
            self.assertIn(why, r.stdout)
            self.assertTrue(self.S.exists() and self.L.exists())

    def test_finish_refuses_a_pair_whose_worker_never_started(self):
        self.receipts()
        self.S.write_bytes(HARMLESS)
        self.L.write_text(f"vfp1 sha {hashlib.sha256(HARMLESS).hexdigest()}\nworker exit=0\n")
        r = self.run_(["finish"])
        self.assertEqual(r.returncode, 2)
        self.assertIn("no worker start", r.stdout)

    def test_finish_refuses_while_the_worker_runs(self):
        self.pair("worker exit=0\n")
        self.receipts()
        r = self.run_(["finish"], ps_out=f"  78 bash {self.S}\\n")
        self.assertEqual(r.returncode, 2)
        self.assertTrue(self.S.exists() and self.L.exists())

    def test_finish_refuses_a_log_without_a_valid_exit(self):
        self.receipts()
        for tail in ("chain rc=0\n", "worker exit=256\n", "worker exit=-1\n"):
            self.pair(tail)
            r = self.run_(["finish"])
            self.assertEqual(r.returncode, 2, tail)
            self.assertIn("does not end with the worker's exit", r.stdout)

    def test_finish_never_creates_the_run_directory(self):
        self.pair("STOP: not login02\nworker exit=2\n")
        r = self.run_(["finish"])
        self.assertEqual(r.returncode, 2)
        self.assertFalse((self.s.t / "SBA").exists())
        self.assertTrue(self.S.exists() and self.L.exists())

    def test_finish_never_writes_through_a_symlink_or_into_a_fifo(self):
        rec = self.receipts()
        self.pair("worker exit=0\n")
        outside = self.s.t / "outside.txt"
        outside.write_text("untouched")
        fifo = self.s.t / "fifo"
        os.mkfifo(fifo)
        for target in (outside, fifo):
            (rec / "vfp1.log").symlink_to(target)
            r = self.run_(["finish"])
            self.assertEqual(r.returncode, 9, r.stdout)
            self.assertTrue(self.S.exists() and self.L.exists())
            (rec / "vfp1.log").unlink()
        self.assertEqual(outside.read_text(), "untouched")

    def test_finish_refuses_a_partial_archive_and_retries_a_complete_one(self):
        rec = self.receipts()
        self.pair("tests ok\nworker exit=0\n")
        (rec / "vfp1.log").write_text(self.L.read_text()[:8])
        r = self.run_(["finish"])
        self.assertEqual(r.returncode, 9, r.stdout)
        self.assertIn("not a complete copy", r.stdout)
        (rec / "vfp1.log").unlink()
        (rec / "vfp1.log").write_text(self.L.read_text())   # a complete copy from an interrupted finish
        r = self.run_(["finish"])
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(list(self.s.shm.iterdir()), [])

    def test_finish_copies_the_log_removes_only_the_two_files_and_returns_the_workers_exit(self):
        self.pair("tests ok\nworker exit=7\n")
        body = self.L.read_text()
        (self.s.shm / "other").write_text("keep")
        rec = self.receipts()
        r = self.run_(["finish"])
        self.assertEqual(r.returncode, 7, r.stdout + r.stderr)
        self.assertEqual(sorted(q.name for q in self.s.shm.iterdir()), ["other"])
        self.assertEqual((rec / "vfp1.log").read_text(), body)
        self.assertEqual((rec / "vfp1.log.sha256").read_text(), f"{hashlib.sha256(body.encode()).hexdigest()}  vfp1.log\n")

    def test_finish_refuses_a_different_sha_receipt(self):
        self.pair("worker exit=0\n")
        rec = self.receipts()
        (rec / "vfp1.log.sha256").write_text("old\n")
        r = self.run_(["finish"])
        self.assertEqual(r.returncode, 9)
        self.assertTrue(self.S.exists() and self.L.exists())


if __name__ == "__main__":
    unittest.main()
