#!/usr/bin/env python3
"""Tests for geanttw shell scripts: build, evloop, and connect.

Runs with: python3 -m pytest <this file> -q -p no:cacheprovider

Every refusal has both a failing case and the matching pass case (smoke mode).
Stubs for squeue, sbatch, ssh, md5sum, conda, ldd, strace, readelf, cmake, make,
sha256sum, git, the binary, stat, and others live in a per-test PATH-prepended
directory.
"""
import hashlib
import json
import shutil
import os
import pathlib
import re
import stat
import subprocess
import sys
import textwrap
import time

import pytest

HERE = pathlib.Path(__file__).resolve().parent.parent
BUILD_SH = HERE / "geanttw_build.sh"
EVLOOP_SH = HERE / "geanttw_evloop.sbatch"
CONNECT_SH = HERE / "geanttw_connect.sh"


# ──────────────────────────────────────────────────────────────────────
# helpers
# ──────────────────────────────────────────────────────────────────────

def _write_stub(bindir: pathlib.Path, name: str, body: str, mode: int = 0o755):
    p = bindir / name
    p.write_text(f"#!/bin/bash\n{body}\n")
    p.chmod(mode)
    return p


def sha256_of(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def md5_of(path: pathlib.Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def _run(cmd: list, env: dict, cwd=None, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
        timeout=timeout,
    )


# ──────────────────────────────────────────────────────────────────────
# evloop fixtures
# ──────────────────────────────────────────────────────────────────────

class EvloopHarness:
    """Set up a fake B, deploy, and stubs for testing geanttw_evloop.sbatch."""

    def __init__(self, tmp_path: pathlib.Path, build: str = "pin", pl: str = "1L",
                 phase: str = "p0"):
        self.tmp = tmp_path
        self.B = tmp_path / "B"
        self.deploy = tmp_path / "deploy"
        self.bindir = tmp_path / "bin"
        self.build = build
        self.pl = pl
        self.phase = phase

        self.bindir.mkdir()
        self.B.mkdir()

        # Create prefix structure
        pfx = self.B / f"prefix-{build}"
        pfx_lib = pfx / "lib"
        pfx_bin = pfx / "bin"
        pfx_lib.mkdir(parents=True)
        pfx_bin.mkdir(parents=True)

        # Create etc/MParamFiles for NuE file
        pfx_etc = pfx / "etc" / "MParamFiles" / "data" / "FluxConstraints"
        pfx_etc.mkdir(parents=True)
        nue_file = pfx_etc / "sorted_NuEConstraint_FHC_RHC_IMD.txt"
        nue_file.write_text("NuE constraint data\n")

        # Create the binary
        binary = pfx_bin / "runEventLoopOmniFold"
        binary.write_text("#!/bin/bash\ntouch runEventLoopOmniFold.root\n")
        binary.chmod(0o755)
        self.binary = binary
        self.binary_md5 = md5_of(binary)

        # Create setup.sh
        setup = pfx_bin / "setup.sh"
        setup.write_text(
            f'export LD_LIBRARY_PATH="{pfx_lib}:${{LD_LIBRARY_PATH:-}}"\n'
        )

        # Create deploy with playlist manifests and anatuple checksums
        self.deploy.mkdir()
        self._init_deploy_git()

        # Create the run dirs
        run_dir = self.B / "run" / phase / build
        run_dir.mkdir(parents=True)
        (self.B / "run" / "logs").mkdir(parents=True, exist_ok=True)

        # Create stubs
        self._create_stubs()

    def _init_deploy_git(self):
        """Create a git repo at deploy with playlist manifests and anatuple TSV."""
        manifest_dir = self.deploy / "2d-unfolding" / "playlist_manifests"
        manifest_dir.mkdir(parents=True)

        anatuple_dir = self.deploy / "publication" / "release" / "preservation" / "anatuple-checksums"
        anatuple_dir.mkdir(parents=True)

        # Create anatuple root with one file
        self.anatuple_root = self.tmp / "anatuple_root"
        self.anatuple_root.mkdir()
        at_file = self.anatuple_root / "file1.root"
        at_file.write_text("anatuple data")
        at_mtime = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(int(at_file.stat().st_mtime)))
        at_size = at_file.stat().st_size
        at_sha = sha256_of(at_file)

        # Write manifests pointing at the anatuple
        for suf in ("Data", "MC"):
            mf = manifest_dir / f"{self.pl}_{suf}.txt"
            mf.write_text(f"{self.anatuple_root}/file1.root\n")

        # Write ANATUPLE-SHA256.tsv
        tsv = anatuple_dir / "ANATUPLE-SHA256.tsv"
        tsv.write_text(f"{at_sha}\t{at_size}\t{at_mtime}\tfile1.root\n")

        # the launcher reads its sacct fence from the deploy (sbatch runs a copy of the script)
        code = self.deploy / "docs" / "orchestration" / "state" / "geanttw-20261124" / "code"
        code.mkdir(parents=True)
        shutil.copy(HERE / "geanttw_sacct.py", code / "geanttw_sacct.py")

        # Init git
        subprocess.run(["git", "init", "-q"], cwd=self.deploy, check=True)
        subprocess.run(["git", "add", "."], cwd=self.deploy, check=True)
        subprocess.run(
            ["git", "-c", "user.name=test", "-c", "user.email=t@t", "commit", "-q", "-m", "init"],
            cwd=self.deploy,
            check=True,
        )

    def _create_stubs(self):
        """Create stub executables for all external commands."""
        # sacct: no rows by default (the fence is clear)
        _write_stub(self.bindir, "sacct", 'true')
        _write_stub(self.bindir, "squeue", 'echo "squeue must never be called" >&2; exit 99')
        # md5sum
        _write_stub(self.bindir, "md5sum", r'''
nf=0
for f in "$@"; do
  case "$f" in
    -*) continue ;;
    *)  nf=$((nf+1)); python3 -c "import hashlib,sys; print(hashlib.md5(open(sys.argv[1],'rb').read()).hexdigest()+' '+sys.argv[1])" "$f" ;;
  esac
done
# like the real tool: no file operand means hash stdin
[ "$nf" -eq 0 ] && python3 -c "import hashlib,sys; print(hashlib.md5(sys.stdin.buffer.read()).hexdigest()+' '+'-')"
true
''')
        # sha256sum
        _write_stub(self.bindir, "sha256sum", r'''
nf=0
for f in "$@"; do
  case "$f" in
    -*) continue ;;
    *)  nf=$((nf+1)); python3 -c "import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest()+'  '+sys.argv[1])" "$f" ;;
  esac
done
# like the real tool: no file operand means hash stdin
[ "$nf" -eq 0 ] && python3 -c "import hashlib,sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest()+'  '+'-')"
true
''')
        # ldd: by default resolves libMAT inside our prefix
        pfx = self.B / f"prefix-{self.build}"
        _write_stub(self.bindir, "ldd", f'echo "libMAT-MINERvA.so => {pfx}/lib/libMAT-MINERvA.so"')
        # strace: just exec the command (skip the -f -e -o args)
        _write_stub(self.bindir, "strace", r'''
# skip strace flags, then exec the command
while [[ "$1" == -* ]]; do
  case "$1" in
    -o) shift 2 ;;
    -e) shift 2 ;;
    -f) shift ;;
    *) shift ;;
  esac
done
exec "$@"
''')
        # readelf
        _write_stub(self.bindir, "readelf", 'echo "  no RPATH or RUNPATH"')
        # conda: `conda shell.bash hook` prints a conda() function whose `activate` sets CONDA_PREFIX and, like
        # root_6_28's, exports BUILD=x86_64-conda-linux-gnu (RDX-BINDING-1.md:189-190)
        self.conda_env = self.tmp / "conda-env-root_6_28"
        self.conda_env.mkdir()
        _write_stub(self.bindir, "conda", r'''
if [ "$1" = shell.bash ] && [ "$2" = hook ]; then
  echo 'conda() { if [ "$1" = activate ]; then : "${ADDR2LINE}"; export CONDA_PREFIX="$2" BUILD=x86_64-conda-linux-gnu; fi; }'
fi
''')
        # a binary that records its environment and writes the output the job expects
        self.binary.write_text(
            "#!/bin/bash\n"
            "env | grep '^MNV101_' | sort > \"$PWD/../binary_env.txt\"\n"
            "echo \"$CONDA_PREFIX\" > \"$PWD/../binary_conda.txt\"\n"
            "echo fake-root-output > runEventLoopOmniFold.root\n"
        )
        self.binary.chmod(0o755)
        self.binary_md5 = md5_of(self.binary)
        # stat (GNU stat -c stub for macOS)
        _write_stub(self.bindir, "stat", r'''
if [[ "$1" == "-c" ]]; then
  fmt="$2"; shift 2
  for f in "$@"; do
    case "$fmt" in
      %s) python3 -c "import os,sys; print(os.stat(sys.argv[1]).st_size)" "$f" ;;
      *)  python3 -c "import os,sys; print(os.stat(sys.argv[1]).st_size)" "$f" ;;
    esac
  done
else
  /usr/bin/stat "$@"
fi
''')

    @property
    def job_name(self) -> str:
        if self.phase == "p0":
            return f"geanttw_p0_{self.build}_{self.pl}"
        return f"geanttw_p2_{self.pl}"

    def env(self, **overrides) -> dict:
        e = os.environ.copy()
        e["PATH"] = f"{self.bindir}:{e['PATH']}"
        e["GEANTTW_SMOKE"] = "1"
        e["GEANTTW_NAME"] = overrides.pop("name", self.job_name)
        e["GEANTTW_TIMELIMIT"] = overrides.pop("timelimit", "01:00:00" if self.phase == "p0" else "01:00:00")
        e["GEANTTW_ANATUPLE_ROOT"] = str(self.anatuple_root) + "/"
        e["ROOT628_CONDA"] = str(self.bindir / "conda")
        e["ROOT628_PREFIX"] = str(self.conda_env)
        e.pop("CONDA_PREFIX", None)
        # Remove any MNV101_ vars
        for k in list(e.keys()):
            if k.startswith("MNV101_"):
                del e[k]
        e.update(overrides)
        return e

    def slurm_stubs(self, fence_lines=("",), timelimit="01:00:00"):
        """sacct answers `-j ID ... -o Timelimit` with the TimeLimit, and each fence snapshot with the next entry of
        fence_lines (psv rows; the last one repeats)."""
        cnt = self.tmp / "fence_count"
        cnt.write_text("0")
        lines_file = self.tmp / "fence_lines.json"
        lines_file.write_text(json.dumps(list(fence_lines)))
        _write_stub(self.bindir, "sacct", f'''
case " $* " in
  *" -j "*) echo "{timelimit}"; exit 0 ;;
esac
python3 - "{lines_file}" "{cnt}" <<'PY'
import json, sys
lines = json.load(open(sys.argv[1])); c = int(open(sys.argv[2]).read())
open(sys.argv[2], "w").write(str(c + 1))
print(lines[min(c, len(lines) - 1)])
PY
''')

    def run_full(self, *extra_args, **env_overrides) -> subprocess.CompletedProcess:
        """Run the job for real (no smoke) as Slurm job 4242 named job_name."""
        env = self.env(**env_overrides)
        env.pop("GEANTTW_SMOKE", None)
        env["SLURM_JOB_ID"] = "4242"
        env["SLURM_JOB_NAME"] = env.pop("GEANTTW_NAME")
        return _run(["bash", str(EVLOOP_SH), str(self.B), self.build, self.pl, self.binary_md5,
                     str(self.deploy), *extra_args], env)

    def run_evloop(self, extra_args=None, **env_overrides) -> subprocess.CompletedProcess:
        args = [
            "bash", str(EVLOOP_SH),
            str(self.B), self.build, self.pl, self.binary_md5, str(self.deploy),
        ]
        if extra_args:
            args.extend(extra_args)
        return _run(args, self.env(**env_overrides))


# ──────────────────────────────────────────────────────────────────────
# build fixtures
# ──────────────────────────────────────────────────────────────────────

class BuildHarness:
    """Set up a fake B and deploy for testing geanttw_build.sh."""

    def __init__(self, tmp_path: pathlib.Path, *, diff_pass: bool = True):
        self.tmp = tmp_path
        self.B = tmp_path / "B"
        self.deploy = tmp_path / "deploy"
        self.bindir = tmp_path / "bin"
        self.diff_pass = diff_pass

        self.bindir.mkdir()

        # The canonical event-loop tree (46 files on the cluster; three here), and a deploy at "M" that tracks one of
        # them and carries the provenance checker with the manifest made from the canonical tree.
        self.canon = tmp_path / "canon"
        canon_files = {"CMakeLists.txt": "cmake_minimum_required(VERSION 3.0)\n", "util/Binning.h": "// binning\n",
                       "systematics/Systematics.h": "// systematics\n"}
        for rel, text in canon_files.items():
            (self.canon / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.canon / rel).write_text(text)
        cs_dir = self.deploy / "MINERvA101" / "MINERvA-101-Cross-Section"
        cs_dir.mkdir(parents=True)
        (cs_dir / "CMakeLists.txt").write_text(canon_files["CMakeLists.txt"])
        code = self.deploy / "docs" / "orchestration" / "state" / "geanttw-20261124" / "code"
        code.mkdir(parents=True)
        shutil.copy(HERE / "geanttw_provenance.py", code / "geanttw_provenance.py")
        (code / "S0-src_base.sha256").write_text("# test manifest\n" + "".join(
            f"{hashlib.sha256(t.encode()).hexdigest()}  {r}\n" for r, t in sorted(canon_files.items())))
        subprocess.run(["git", "init", "-q"], cwd=self.deploy, check=True)
        subprocess.run(["git", "add", "."], cwd=self.deploy, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "M"],
                       cwd=self.deploy, check=True)

        # Create MAT and MAT-MINERvA repos as local bare repos
        self.mat_repo = tmp_path / "mat-repo"
        self.matminerva_repo = tmp_path / "matminerva-repo"
        self._create_mat_repo()
        self._create_matminerva_repo()

        self._create_stubs()

    def _create_mat_repo(self):
        """Create a fake MAT git repo at the pinned commit."""
        self.mat_repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.mat_repo, check=True)
        (self.mat_repo / "CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.0)\nproject(MAT)\n")
        subprocess.run(["git", "add", "."], cwd=self.mat_repo, check=True)
        subprocess.run(
            ["git", "-c", "user.name=test", "-c", "user.email=t@t",
             "commit", "-q", "-m", "MAT pin"],
            cwd=self.mat_repo, check=True,
        )

    def _create_matminerva_repo(self):
        """Create a fake MAT-MINERvA git repo with the pin and patch commits."""
        self.matminerva_repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.matminerva_repo, check=True)
        # Pin commit
        (self.matminerva_repo / "GeantHadronUniverse.h").write_text("// pin version\nreturn 1;\n")
        (self.matminerva_repo / "CMakeLists.txt").write_text(
            "cmake_minimum_required(VERSION 3.0)\nproject(MAT-MINERvA)\n"
        )
        subprocess.run(["git", "add", "."], cwd=self.matminerva_repo, check=True)
        subprocess.run(
            ["git", "-c", "user.name=test", "-c", "user.email=t@t",
             "commit", "-q", "-m", "MATMINERvA pin"],
            cwd=self.matminerva_repo, check=True,
        )
        # The patch commit on a branch
        subprocess.run(["git", "checkout", "-q", "-b", "patch-branch"], cwd=self.matminerva_repo, check=True)
        if self.diff_pass:
            (self.matminerva_repo / "GeantHadronUniverse.h").write_text("// patched version\nreturn ratio;\n")
        else:
            # Extra change to make the diff different
            (self.matminerva_repo / "GeantHadronUniverse.h").write_text("// patched version\nreturn ratio;\n")
            (self.matminerva_repo / "extra_file.txt").write_text("extra\n")
            subprocess.run(["git", "add", "."], cwd=self.matminerva_repo, check=True)
        subprocess.run(["git", "add", "."], cwd=self.matminerva_repo, check=True)
        subprocess.run(
            ["git", "-c", "user.name=test", "-c", "user.email=t@t",
             "commit", "-q", "-m", "the patch"],
            cwd=self.matminerva_repo, check=True,
        )
        # Save the commit hashes
        self.pin_sha = subprocess.run(
            ["git", "rev-parse", "HEAD~1"], cwd=self.matminerva_repo,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        self.patch_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.matminerva_repo,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        self.mat_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.mat_repo,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        # Go back to main
        subprocess.run(["git", "checkout", "-q", "-"], cwd=self.matminerva_repo, check=True)

    def _create_stubs(self):
        """Create cmake/make stubs for DRYRUN mode."""
        # cmake stub: creates CMakeCache and a Makefile
        _write_stub(self.bindir, "cmake", r'''
# Parse args to find the source dir and CMAKE_INSTALL_PREFIX
SRC=""; PREFIX=""
for arg in "$@"; do
  case "$arg" in
    -DCMAKE_INSTALL_PREFIX=*) PREFIX="${arg#*=}" ;;
    -D*) ;;
    /*|./*) SRC="$arg" ;;
  esac
done
echo "cmake stub: src=$SRC prefix=$PREFIX" > cmake.log
echo "args: $*" >> cmake.log
''')
        # make stub: creates the expected outputs
        # We need to know what we're building from the cmake.log
        _write_stub(self.bindir, "make", r'''
# Parse cmake.log for PREFIX and SRC
PREFIX=""
SRC=""
if [ -f cmake.log ]; then
  PREFIX=$(sed -n 's/.*prefix=\(.*\)/\1/p' cmake.log)
  SRC=$(sed -n 's/.*src=\([^ ]*\).*/\1/p' cmake.log)
fi
# When "install" is an argument, install files
case "$*" in
  *install*)
    if [ -n "$PREFIX" ]; then
      mkdir -p "$PREFIX/lib" "$PREFIX/bin" "$PREFIX/lib/cmake/MAT" "$PREFIX/lib/cmake/MAT-MINERvA"
      # Determine what we're building from the source dir name or content
      if echo "$SRC" | grep -q "MAT-MINERvA"; then
        # Different content for pin vs pat so sha256 differs
        if echo "$SRC" | grep -q "MAT-MINERvA-pat" && [ -z "${TEST_MM_SAME:-}" ]; then
          echo "libMAT-MINERvA-patched" > "$PREFIX/lib/libMAT-MINERvA.so"
        else
          echo "libMAT-MINERvA-pinned" > "$PREFIX/lib/libMAT-MINERvA.so"
        fi
      elif echo "$SRC" | grep -q "MAT"; then
        # Same content for both so sha256 matches
        if [ -n "${TEST_MAT_DIFFERS:-}" ]; then echo "libMAT-$PREFIX" > "$PREFIX/lib/libMAT.so"
        else echo "libMAT-identical" > "$PREFIX/lib/libMAT.so"; fi
      fi
    fi
    ;;
  *runEventLoopOmniFold*)
    # Building the binary — create it in cwd
    echo "binary-content-$$" > runEventLoopOmniFold
    chmod +x runEventLoopOmniFold
    ;;
  *)
    # Regular make: create runEventLoopOmniFold if building the event loop
    ;;
esac
''')
        # sha256sum
        _write_stub(self.bindir, "sha256sum", r'''
nf=0
for f in "$@"; do
  case "$f" in
    -*) continue ;;
    *)  nf=$((nf+1)); python3 -c "import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest()+'  '+sys.argv[1])" "$f" ;;
  esac
done
# like the real tool: no file operand means hash stdin
[ "$nf" -eq 0 ] && python3 -c "import hashlib,sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest()+'  '+'-')"
true
''')
        # readelf
        _write_stub(self.bindir, "readelf", 'echo "  0x000000000000001d (RUNPATH)            Library runpath: '
                    f'[{self.tmp / "conda-env-root_6_28"}/lib]"')
        # md5sum (macOS has none)
        _write_stub(self.bindir, "md5sum", r'''
for f in "$@"; do python3 -c "import hashlib,sys; print(hashlib.md5(open(sys.argv[1],'rb').read()).hexdigest()+' '+sys.argv[1])" "$f"; done
''')
        # conda hook whose activate, like root_6_28's, reads an unset variable and exports BUILD
        self.conda_env = self.tmp / "conda-env-root_6_28"
        self.conda_env.mkdir()
        _write_stub(self.bindir, "conda", r'''
if [ "$1" = shell.bash ] && [ "$2" = hook ]; then
  echo 'conda() { if [ "$1" = activate ]; then : "${ADDR2LINE}"; export CONDA_PREFIX="$2" BUILD=x86_64-conda-linux-gnu; fi; }'
fi
''')
        # a fake production opt with the two files whose md5s the build records
        self.prod_opt = self.tmp / "prod-opt"
        (self.prod_opt / "lib").mkdir(parents=True)
        (self.prod_opt / "bin").mkdir(parents=True)
        (self.prod_opt / "lib" / "libMAT-MINERvA.so").write_text("prod lib\n")
        (self.prod_opt / "bin" / "runEventLoopOmniFold").write_text("prod bin\n")
        for d in ("lib/data", "etc/MParamFiles/data", "etc/MATFluxAndReweightFiles", "lib/cmake/UnfoldUtils",
                  "lib/cmake/GENIEXSecExtract"):
            (self.prod_opt / d).mkdir(parents=True, exist_ok=True)

    def env(self, **overrides) -> dict:
        e = os.environ.copy()
        e["PATH"] = f"{self.bindir}:{e['PATH']}"
        e["GEANTTW_SMOKE_B"] = str(self.B)
        e["GEANTTW_BUILD_DRYRUN"] = "1"
        e["GEANTTW_MAT_URL"] = str(self.mat_repo)
        e["GEANTTW_MATMINERVA_URL"] = str(self.matminerva_repo)
        e["GEANTTW_CANON_SRC"] = str(self.canon)
        e["GEANTTW_MAT_PIN"] = self.mat_sha
        e["GEANTTW_MATMINERVA_PIN"] = self.pin_sha
        e["GEANTTW_PATCH_COMMIT"] = self.patch_sha
        e["GEANTTW_PATCH_FILES"] = "GeantHadronUniverse.h"
        e["GEANTTW_PROD_OPT"] = str(self.prod_opt)
        e["ROOT628_CONDA"] = str(self.bindir / "conda")
        e["ROOT628_PREFIX"] = str(self.conda_env)
        e.pop("CONDA_PREFIX", None)
        e.update(overrides)
        return e

    def run_build(self, **env_overrides) -> subprocess.CompletedProcess:
        return _run(
            ["bash", str(BUILD_SH), str(self.B), str(self.deploy)],
            self.env(**env_overrides),
        )


# ──────────────────────────────────────────────────────────────────────
# connect fixtures
# ──────────────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────────────
# evloop tests
# ──────────────────────────────────────────────────────────────────────

class TestEvloopSmoke:
    """Test that evloop passes all checks in smoke mode with correct setup."""

    def test_smoke_pass(self, tmp_path):
        h = EvloopHarness(tmp_path)
        r = h.run_evloop()
        assert r.returncode == 0, f"stdout={r.stdout}\nstderr={r.stderr}"
        assert "smoke: checks passed" in r.stdout

    def test_smoke_pass_pat(self, tmp_path):
        h = EvloopHarness(tmp_path, build="pat")
        r = h.run_evloop()
        assert r.returncode == 0, f"stdout={r.stdout}\nstderr={r.stderr}"


class TestEvloopJobName:
    """Test job name validation."""

    def test_wrong_job_name_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        r = h.run_evloop(name="wrong_name")
        assert r.returncode != 0
        assert "REFUSE" in r.stderr

    def test_correct_job_name_passes(self, tmp_path):
        h = EvloopHarness(tmp_path)
        r = h.run_evloop()
        assert r.returncode == 0


class TestEvloopP2Build:
    """Test that p2 refuses build=pin."""

    def test_p2_with_build_pin_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path, build="pin", phase="p2")
        # Create a p2 limits file
        limits = tmp_path / "limits.txt"
        limits.write_text("1L 01:00:00\n")
        limits_sha = sha256_of(limits)
        r = h.run_evloop(
            extra_args=[str(limits), limits_sha],
            name="geanttw_p2_1L",
        )
        assert r.returncode != 0
        assert "REFUSE" in r.stderr
        assert "pat" in r.stderr

    def test_p2_with_build_pat_passes(self, tmp_path):
        h = EvloopHarness(tmp_path, build="pat", phase="p2")
        limits = tmp_path / "limits.txt"
        limits.write_text("1L 01:00:00\n")
        limits_sha = sha256_of(limits)
        r = h.run_evloop(
            extra_args=[str(limits), limits_sha],
            name="geanttw_p2_1L",
        )
        assert r.returncode == 0, f"stdout={r.stdout}\nstderr={r.stderr}"


class TestEvloopTimeLimit:
    """Test TimeLimit too long."""

    def test_timelimit_too_long_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        r = h.run_evloop(timelimit="02:00:00")
        assert r.returncode != 0
        assert "REFUSE" in r.stderr
        assert "TimeLimit" in r.stderr

    def test_timelimit_within_limit_passes(self, tmp_path):
        h = EvloopHarness(tmp_path)
        r = h.run_evloop(timelimit="00:30:00")
        assert r.returncode == 0, f"stdout={r.stdout}\nstderr={r.stderr}"


class TestEvloopFencedJobs:
    """Test fence check for cov2d/t2a jobs."""

    def test_cov2d_job_running_at_start_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        _write_stub(h.bindir, "sacct", 'echo "11|cov2d_a|RUNNING|5|1|60"')
        r = h.run_evloop()
        assert r.returncode != 0
        assert "REFUSE" in r.stderr
        assert "fenced" in r.stderr

    def test_cov2d_job_appearing_before_binary(self, tmp_path):
        """The start check is clear; a cov2d job appears by the pre-binary check, which must refuse."""
        h = EvloopHarness(tmp_path)
        h.slurm_stubs(fence_lines=("", "12|cov2d_ll5d|PENDING|0|1|60"))
        r = h.run_full()
        assert r.returncode == 2, r.stderr
        assert "fenced jobs are live, or sacct is unreadable (immediately before the binary" in r.stderr
        assert not (h.tmp / "binary_env.txt").exists(), "the binary ran"

    def test_t2a_job_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        _write_stub(h.bindir, "sacct", 'echo "13|t2a_job|PENDING|0|1|60"')
        r = h.run_evloop()
        assert r.returncode != 0
        assert "REFUSE" in r.stderr

    def test_ended_cov2d_job_does_not_block(self, tmp_path):
        h = EvloopHarness(tmp_path)
        _write_stub(h.bindir, "sacct", 'echo "11|cov2d_a|COMPLETED|5|1|60"; echo "12|ibub_run|RUNNING|5|1|60"')
        assert h.run_evloop().returncode == 0

    def test_sacct_error_line_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        _write_stub(h.bindir, "sacct", 'echo "sacct: error: slurmdbd unreachable"')
        r = h.run_evloop()
        assert r.returncode == 2 and "sacct is unreadable" in r.stderr

    def test_sacct_failing_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        _write_stub(h.bindir, "sacct", 'exit 1')
        r = h.run_evloop()
        assert r.returncode == 2 and "sacct failed" in r.stderr

    def test_no_fenced_jobs_passes(self, tmp_path):
        h = EvloopHarness(tmp_path)
        r = h.run_evloop()
        assert r.returncode == 0


class TestEvloopMd5Mismatch:
    """Test binary md5 mismatch."""

    def test_md5_mismatch_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        r = h.run_evloop()
        # Pass with correct md5 first
        assert r.returncode == 0

        # Now with wrong md5
        args = [
            "bash", str(EVLOOP_SH),
            str(h.B), h.build, h.pl, "deadbeef" * 4, str(h.deploy),
        ]
        r2 = _run(args, h.env())
        assert r2.returncode != 0
        assert "REFUSE" in r2.stderr
        assert "md5" in r2.stderr

    def test_md5_match_passes(self, tmp_path):
        h = EvloopHarness(tmp_path)
        r = h.run_evloop()
        assert r.returncode == 0


class TestEvloopManifest:
    """Test manifest differs from deploy HEAD."""

    def test_manifest_differs_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        # Modify the manifest file after the git commit
        mf = h.deploy / "2d-unfolding" / "playlist_manifests" / f"{h.pl}_Data.txt"
        mf.write_text("modified path\n")
        r = h.run_evloop()
        assert r.returncode != 0
        assert "REFUSE" in r.stderr
        assert "committed" in r.stderr

    def test_manifest_matches_passes(self, tmp_path):
        h = EvloopHarness(tmp_path)
        r = h.run_evloop()
        assert r.returncode == 0


class TestEvloopAnaTuple:
    """Test AnaTuple size/mtime mismatch."""

    def test_anatuple_size_mismatch_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        # Modify the file to change its size
        at_file = h.anatuple_root / "file1.root"
        at_file.write_text("extra data to change size")
        r = h.run_evloop()
        assert r.returncode != 0
        assert "REFUSE" in r.stderr
        assert "AnaTuple" in r.stderr

    def test_anatuple_ok_passes(self, tmp_path):
        h = EvloopHarness(tmp_path)
        r = h.run_evloop()
        assert r.returncode == 0


class TestEvloopOutputExists:
    """Test output file already exists."""

    def test_output_exists_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        out = h.B / "run" / "p0" / h.build / f"runEventLoopOmniFold_GEANTTW_{h.build}_{h.pl}.root"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("existing output")
        r = h.run_evloop()
        assert r.returncode != 0
        assert "REFUSE" in r.stderr or r.returncode == 3

    def test_output_not_exists_passes(self, tmp_path):
        h = EvloopHarness(tmp_path)
        r = h.run_evloop()
        assert r.returncode == 0


class TestEvloopLddResolve:
    """ldd resolving libMAT-MINERvA.so to the production opt/lib must refuse; the prefix's own lib passes."""

    def test_ldd_outside_prefix_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        _write_stub(h.bindir, "ldd",
                    'echo "libMAT-MINERvA.so => /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/lib/libMAT-MINERvA.so"')
        r = h.run_evloop()
        assert r.returncode == 2, r.stderr
        assert "resolve outside" in r.stderr

    def test_ldd_libmat_outside_prefix_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        pfx = h.B / f"prefix-{h.build}" / "lib"
        _write_stub(h.bindir, "ldd", f'''echo "libMAT-MINERvA.so => {pfx}/libMAT-MINERvA.so"
echo "libMAT.so => /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/lib/libMAT.so"''')
        r = h.run_evloop()
        assert r.returncode == 2, r.stderr
        assert "resolve outside" in r.stderr

    def test_ldd_other_production_library_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        pfx = h.B / f"prefix-{h.build}" / "lib"
        _write_stub(h.bindir, "ldd", f'''echo "libMAT-MINERvA.so => {pfx}/libMAT-MINERvA.so"
echo "libUnfoldUtils.so => /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/lib/libUnfoldUtils.so"''')
        r = h.run_evloop()
        assert r.returncode == 2 and "libUnfoldUtils" in r.stderr

    def test_ldd_libmat_not_found_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        _write_stub(h.bindir, "ldd", 'echo "libMAT.so => not found"')
        r = h.run_evloop()
        assert r.returncode == 2 and "resolve outside" in r.stderr

    def test_ldd_inside_prefix_passes(self, tmp_path):
        h = EvloopHarness(tmp_path)
        r = h.run_evloop()
        assert r.returncode == 0, r.stderr
        assert "smoke: checks passed" in r.stdout


class TestEvloopConda:
    """The ROOT env is activated by conda; a missing conda or a failed activation refuses."""

    def test_missing_conda_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        r = h.run_evloop(ROOT628_CONDA=str(tmp_path / "no-conda"))
        assert r.returncode == 2, r.stderr
        assert "is missing" in r.stderr

    def test_activation_without_prefix_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        _write_stub(h.bindir, "conda", 'echo "conda() { :; }"')
        r = h.run_evloop()
        assert r.returncode == 2, r.stderr
        assert "conda activation did not give CONDA_PREFIX" in r.stderr

    def test_nue_missing_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        (h.B / f"prefix-{h.build}" / "etc" / "MParamFiles" / "data" / "FluxConstraints" /
         "sorted_NuEConstraint_FHC_RHC_IMD.txt").unlink()
        r = h.run_evloop()
        assert r.returncode == 2, r.stderr
        assert "NuE file" in r.stderr


class TestEvloopFullRun:
    """A real (non-smoke) p0 run with a stub binary: the environment the binary sees, the NuE log, strace and the
    output's mode."""

    def run(self, tmp_path, **env):
        h = EvloopHarness(tmp_path)
        h.slurm_stubs()
        strace_seen = tmp_path / "strace_args.txt"
        _write_stub(h.bindir, "strace", f'''
echo "$*" > "{strace_seen}"
out=""
while [[ "$1" == -* ]]; do
  case "$1" in -o) out="$2"; shift 2 ;; -e) shift 2 ;; *) shift ;; esac
done
echo 'openat(AT_FDCWD, "/x", O_RDONLY) = 3' > "$out"
exec "$@"
''')
        return h, h.run_full(**env), strace_seen

    def test_full_run_writes_output_0440(self, tmp_path):
        h, r, _ = self.run(tmp_path)
        assert r.returncode == 0, r.stderr
        out = h.B / "run" / "p0" / h.build / f"runEventLoopOmniFold_GEANTTW_{h.build}_{h.pl}.root"
        assert out.read_text() == "fake-root-output\n"
        assert (out.stat().st_mode & 0o777) == 0o440
        assert not list((h.B / "run" / "p0" / h.build).glob("*.partial"))
        assert not list((h.B / "run" / "p0" / h.build).glob("work_*")), "work dir left behind"

    def test_binary_sees_only_dump_universes(self, tmp_path):
        h, r, _ = self.run(tmp_path, MNV101_SKIP_SYST="1", MNV101_TRUTH_ONLY="1")
        assert r.returncode == 0, r.stderr
        env_seen = (h.B / "run" / "p0" / h.build / "binary_env.txt").read_text().split()
        assert env_seen == ["MNV101_DUMP_UNIVERSES=GEANT_Neutron,GEANT_Pion,GEANT_Proton"]
        assert (h.B / "run" / "p0" / h.build / "binary_conda.txt").read_text().strip() == str(h.conda_env)

    def test_nue_logged_before_and_after(self, tmp_path):
        h, r, _ = self.run(tmp_path)
        assert r.returncode == 0, r.stderr
        lines = [ln for ln in r.stdout.splitlines() if "] NUE " in ln]
        assert [ln.split()[2] for ln in lines] == ["before", "after"], r.stdout
        for ln in lines:
            assert "atime_ns=" in ln and "mtime_ns=" in ln and "utc=" in ln

    def test_p0_runs_under_strace(self, tmp_path):
        h, r, seen = self.run(tmp_path)
        assert r.returncode == 0, r.stderr
        args = seen.read_text().split()
        assert args[:5] == ["-f", "-y", "-e", "trace=openat,open", "-o"]
        assert args[5] == str(h.B / "run" / "p0" / h.build / f"strace.{h.build}.{h.pl}")
        assert (h.B / "run" / "p0" / h.build / f"strace.{h.build}.{h.pl}").exists()

    def test_binary_failure_exits_5_and_writes_nothing(self, tmp_path):
        h = EvloopHarness(tmp_path)
        h.slurm_stubs()
        h.binary.write_text("#!/bin/bash\nexit 7\n")
        h.binary_md5 = md5_of(h.binary)
        r = h.run_full()
        assert r.returncode == 5, r.stderr
        assert not (h.B / "run" / "p0" / h.build / f"runEventLoopOmniFold_GEANTTW_{h.build}_{h.pl}.root").exists()

    def test_p2_full_run_without_strace(self, tmp_path):
        h = EvloopHarness(tmp_path, build="pat", phase="p2")
        h.slurm_stubs()
        _write_stub(h.bindir, "strace", 'echo "strace must not run in p2" >&2; exit 99')
        limits = tmp_path / "limits.txt"
        limits.write_text("1L 01:00:00\n")
        r = h.run_full(str(limits), sha256_of(limits))
        assert r.returncode == 0, r.stderr
        out = h.B / "run" / "p2" / "pat" / "runEventLoopOmniFold_GEANTTW_pat_1L.root"
        assert out.read_text() == "fake-root-output\n"
        assert not list((h.B / "run" / "p2" / "pat").glob("strace.*"))

    def test_slurm_timelimit_too_long_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        h.slurm_stubs(timelimit="01:00:01")
        r = h.run_full()
        assert r.returncode == 2, r.stderr
        assert "TimeLimit" in r.stderr


class TestEvloopPointCloud:
    """Test MNV101_DUMP_POINTCLOUD preset is refused."""

    def test_pointcloud_set_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        r = h.run_evloop(MNV101_DUMP_POINTCLOUD="1")
        assert r.returncode != 0
        assert "REFUSE" in r.stderr
        assert "POINTCLOUD" in r.stderr

    def test_pointcloud_unset_passes(self, tmp_path):
        h = EvloopHarness(tmp_path)
        r = h.run_evloop()
        assert r.returncode == 0


# ──────────────────────────────────────────────────────────────────────
# build tests
# ──────────────────────────────────────────────────────────────────────

class TestBuildRefusals:
    """The path guard, existing targets and the ROOT environment."""

    def test_wrong_B_without_smoke_refuses(self, tmp_path):
        h = BuildHarness(tmp_path)
        env = h.env()
        del env["GEANTTW_SMOKE_B"]
        r = _run(["bash", str(BUILD_SH), str(h.B), str(h.deploy)], env)
        assert r.returncode == 2, r.stderr
        assert "REFUSE: B is" in r.stderr

    @pytest.mark.parametrize("sub", ["src", "prefix-pin", "prefix-pat", "build-mat-pin"])
    def test_existing_target_refuses(self, tmp_path, sub):
        h = BuildHarness(tmp_path)
        (h.B / sub).mkdir(parents=True)
        r = h.run_build()
        assert r.returncode == 2, r.stderr
        assert "exists" in r.stderr

    def test_missing_conda_refuses(self, tmp_path):
        h = BuildHarness(tmp_path)
        r = h.run_build(ROOT628_CONDA=str(tmp_path / "none"))
        assert r.returncode == 2, r.stderr
        assert "is missing" in r.stderr

    def test_failed_activation_refuses(self, tmp_path):
        h = BuildHarness(tmp_path)
        _write_stub(h.bindir, "conda", 'echo "conda() { :; }"')
        r = h.run_build()
        assert r.returncode == 2, r.stderr
        assert "conda activation" in r.stderr


def _log(h):
    return (h.B / "run" / "p0" / "build.log").read_text().splitlines()


class TestBuildFull:
    """A whole build against fake repos and stub cmake/make."""

    def test_full_build_passes_with_all_records(self, tmp_path):
        h = BuildHarness(tmp_path)
        r = h.run_build()
        assert r.returncode == 0, r.stderr
        log = _log(h)
        checks = sorted(ln for ln in log if ln.startswith("CHECK "))
        assert checks == ["CHECK DIFF_EQUALS_UPSTREAM PASS", "CHECK LIBMATMINERVA_DIFFER PASS",
                          "CHECK LIBMAT_IDENTICAL PASS", "CHECK RPATH_CLEAN PASS", "CHECK SOURCE_PROVENANCE PASS"]
        kinds = {ln.split()[0] for ln in log}
        assert {"SO", "BIN", "RPATH", "PROD", "CHECK"} <= kinds
        assert sum(ln.startswith("BIN ") for ln in log) == 2
        prod = [ln for ln in log if ln.startswith("PROD ")]
        assert len(prod) == 2 and all(len(ln.split()[2]) == 32 for ln in prod)
        for b in ("pin", "pat"):
            assert os.readlink(h.B / f"prefix-{b}" / "lib" / "data") == str(h.prod_opt / "lib" / "data")
            assert os.readlink(h.B / f"prefix-{b}" / "etc" / "MParamFiles") == str(h.prod_opt / "etc" / "MParamFiles")
            assert os.readlink(h.B / f"prefix-{b}" / "etc" / "MATFluxAndReweightFiles") == str(
                h.prod_opt / "etc" / "MATFluxAndReweightFiles")
            args = (h.B / f"build-evloop-{b}" / "cmake.log").read_text()
            assert f"src={h.B}/src/evloop" in args
            assert f"-DUnfoldUtils_DIR={h.prod_opt}/lib/cmake/UnfoldUtils" in args
            assert f"-DGENIEXSecExtract_DIR={h.prod_opt}/lib/cmake/GENIEXSecExtract" in args
            assert f"-DMAT-MINERvA_DIR={h.B}/prefix-{b}/lib/cmake/MAT-MINERvA" in args
            assert (h.B / f"prefix-{b}" / "bin" / "runEventLoopOmniFold").exists()

    def test_setup_sh_names_only_its_prefix(self, tmp_path):
        h = BuildHarness(tmp_path)
        assert h.run_build().returncode == 0
        for b in ("pin", "pat"):
            pfx = h.B / f"prefix-{b}"
            r = _run(["bash", "-c", f'export MINERVA_PREFIX="{pfx}"; LD_LIBRARY_PATH=/x; source "{pfx}/bin/setup.sh" && '
                      'echo "$PLOTUTILSROOT|$LD_LIBRARY_PATH|$MPARAMFILES|$MATFLUXANDWEIGHTFILES"'], os.environ.copy())
            assert r.returncode == 0, r.stderr
            assert r.stdout.strip() == (f"{pfx}/lib|{pfx}/lib:/x|{pfx}/etc/MParamFiles/data|"
                                        f"{pfx}/etc/MATFluxAndReweightFiles")
            other = h.B / ("prefix-pat" if b == "pin" else "prefix-pin")
            r = _run(["bash", "-c", f'export MINERVA_PREFIX="{other}"; source "{pfx}/bin/setup.sh"'], os.environ.copy())
            assert r.returncode != 0 and "MINERVA_PREFIX is not" in r.stderr

    @pytest.mark.parametrize("plant", ["extra", "mismatch", "missing"])
    def test_source_provenance_failure_stops_before_build(self, tmp_path, plant):
        h = BuildHarness(tmp_path)
        if plant == "extra":
            (h.canon / "util" / "Stray.h").write_text("x")
        elif plant == "mismatch":
            (h.canon / "systematics" / "Systematics.h").write_text("// edited\n")
        else:
            (h.canon / "util" / "Binning.h").unlink()
        r = h.run_build()
        assert r.returncode == 1, r.stderr
        assert "CHECK SOURCE_PROVENANCE FAIL" in _log(h)
        assert "nothing is built" in r.stderr
        assert not (h.B / "prefix-pin" / "lib" / "libMAT.so").exists()

    @pytest.mark.parametrize("rpath", ["/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/lib", "OTHER"])
    def test_rpath_not_clean_fails(self, tmp_path, rpath):
        h = BuildHarness(tmp_path)
        if rpath == "OTHER":
            rpath = f"{h.conda_env}/lib:{h.B}/prefix-pat/lib"   # pin's binary pointing at pat's prefix
        _write_stub(h.bindir, "readelf", f'echo "  0x1d (RUNPATH)  Library runpath: [{rpath}]"')
        r = h.run_build()
        assert r.returncode == 1, r.stderr
        assert "CHECK RPATH_CLEAN FAIL" in _log(h)

    def test_patch_tree_is_the_cherry_pick(self, tmp_path):
        h = BuildHarness(tmp_path)
        assert h.run_build().returncode == 0
        pat = h.B / "src" / "MAT-MINERvA-pat"
        parent = subprocess.run(["git", "-C", str(pat), "rev-parse", "HEAD~1"], capture_output=True,
                                text=True).stdout.strip()
        assert parent == h.pin_sha
        assert "return ratio;" in (pat / "GeantHadronUniverse.h").read_text()
        assert "return 1;" in (h.B / "src" / "MAT-MINERvA-pin" / "GeantHadronUniverse.h").read_text()

    def test_extra_file_in_patch_stops_before_build(self, tmp_path):
        h = BuildHarness(tmp_path, diff_pass=False)
        r = h.run_build()
        assert r.returncode == 1, r.stderr
        assert "changed files" in r.stderr
        assert _log(h) == ["CHECK DIFF_EQUALS_UPSTREAM FAIL"]
        assert not (h.B / "prefix-pin" / "lib" / "libMAT.so").exists(), "built despite the failed check"

    def test_diff_mismatch_stops(self, tmp_path):
        """The upstream commit's parent is not the pin: the cherry-pick applies at an offset, so its diff's hunk
        header differs from `git show` of the commit, byte for byte."""
        h = BuildHarness(tmp_path)
        repo = h.matminerva_repo
        g = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(g + ["checkout", "-q", "-b", "offset", h.pin_sha], check=True)
        f = repo / "GeantHadronUniverse.h"
        f.write_text("// a\n// b\n// c\n" + f.read_text())
        subprocess.run(g + ["commit", "-q", "-am", "lines above"], check=True)
        f.write_text(f.read_text().replace("return 1;", "return ratio;"))
        subprocess.run(g + ["commit", "-q", "-am", "the patch, at an offset"], check=True)
        offset_patch = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True,
                                      text=True, check=True).stdout.strip()
        subprocess.run(g + ["checkout", "-q", "-"], check=True)
        r = h.run_build(GEANTTW_PATCH_COMMIT=offset_patch)
        assert r.returncode == 1, r.stderr
        assert "diffs are not byte-identical" in r.stderr
        assert _log(h) == ["CHECK DIFF_EQUALS_UPSTREAM FAIL"]
        assert not (h.B / "prefix-pin" / "lib" / "libMAT.so").exists()

    def test_missing_production_file_is_recorded(self, tmp_path):
        h = BuildHarness(tmp_path)
        (h.prod_opt / "bin" / "runEventLoopOmniFold").unlink()
        r = h.run_build()
        assert r.returncode == 0, r.stderr
        assert f"PROD {h.prod_opt}/bin/runEventLoopOmniFold MISSING" in _log(h)

    def test_libmat_differs_fails(self, tmp_path):
        h = BuildHarness(tmp_path)
        r = h.run_build(TEST_MAT_DIFFERS="1")
        assert r.returncode == 1, r.stderr
        assert "CHECK LIBMAT_IDENTICAL FAIL" in _log(h)

    def test_libmatminerva_same_fails(self, tmp_path):
        h = BuildHarness(tmp_path)
        r = h.run_build(TEST_MM_SAME="1")
        assert r.returncode == 1, r.stderr
        assert "CHECK LIBMATMINERVA_DIFFER FAIL" in _log(h)

    def test_pin_overrides_ignored_without_smoke_b(self, tmp_path):
        """Outside the tests' smoke mode the real pins are used, so the fake repos cannot be checked out."""
        h = BuildHarness(tmp_path)
        prod = tmp_path / "prodB"
        env = h.env()
        del env["GEANTTW_SMOKE_B"]
        r = _run(["bash", "-c", f'sed "s#^PROD_B=.*#PROD_B={prod}#" "{BUILD_SH}" > "{tmp_path}/b.sh"; '
                  f'bash "{tmp_path}/b.sh" "{prod}" "{h.deploy}"'], env)
        assert r.returncode != 0
        assert not (prod / "prefix-pin").exists()


# ──────────────────────────────────────────────────────────────────────
# connect + remote: a fake repository holding the real geanttw_remote.sh and stubs for the rest
# ──────────────────────────────────────────────────────────────────────

REMOTE_SH = HERE / "geanttw_remote.sh"
CODE_REL = "docs/orchestration/state/geanttw-20261124/code"
FENCE_REL = "docs/orchestration/state/2d-closeout/cov2d-fence-20261122/cov2d_fence.sh"
SUMS_REL = ("docs/orchestration/state/measurement-paper/5d-community-20261024/fd/retention-20261110/hpss-20261111/"
            "manifests/SHA256SUMS.zero_loops")


class RemoteHarness:
    def __init__(self, tmp_path: pathlib.Path):
        self.tmp = tmp_path
        self.repo = tmp_path / "repo"
        self.B = tmp_path / "B"
        self.bindir = tmp_path / "bin"
        self.bindir.mkdir()
        self.calls = tmp_path / "calls.log"
        code = self.repo / CODE_REL
        code.mkdir(parents=True)
        shutil.copy(REMOTE_SH, code / "geanttw_remote.sh")
        (code / "geanttw_build.sh").write_text(
            "#!/bin/bash\n"
            'echo "build $*" >> "$TEST_CALLS"\n'
            'mkdir -p "$1/run/p0"\n'
            'for c in DIFF_EQUALS_UPSTREAM SOURCE_PROVENANCE RPATH_CLEAN LIBMAT_IDENTICAL LIBMATMINERVA_DIFFER; do\n'
            '  v=PASS; [ "$c" = "${TEST_FAIL_CHECK:-}" ] && v=FAIL; echo "CHECK $c $v" >> "$1/run/p0/build.log"\n'
            'done\n'
            'for b in pin pat; do mkdir -p "$1/prefix-$b/bin"; echo "bin-$b" > "$1/prefix-$b/bin/runEventLoopOmniFold";'
            ' chmod +x "$1/prefix-$b/bin/runEventLoopOmniFold"; done\n'
            'exit ${TEST_BUILD_RC:-0}\n')
        (code / "geanttw_evloop.sbatch").write_text(
            "#!/bin/bash\n"
            'echo "smoke $2 $GEANTTW_NAME $GEANTTW_TIMELIMIT smoke=$GEANTTW_SMOKE" >> "$TEST_CALLS"\n'
            '[ "$2" = "${TEST_SMOKE_REFUSES:-}" ] && exit 2\n'
            "exit 0\n")
        shutil.copy(HERE / "geanttw_sacct.py", code / "geanttw_sacct.py")
        for f in ("dumpcmp.py", "S0-src_base.sha256", "geanttw_provenance.py"):
            (code / f).write_text("# stub\n")
        (code / "p0_check.py").write_text(
            "import os, sys\n"
            "open(os.environ['TEST_CALLS'], 'a').write('p0_check ' + ' '.join(sys.argv[1:]) + '\\n')\n"
            "sys.exit(int(os.environ.get('TEST_P0CHECK_RC', '0')))\n")
        self.ref = tmp_path / "zero" / "runEventLoopOmniFold_5D_1L_zero.root"
        self.ref.parent.mkdir()
        self.ref.write_bytes(b"the MP-1 1L reference\n")
        sums = self.repo / SUMS_REL
        sums.parent.mkdir(parents=True)
        sums.write_text(f"{'0' * 64}  /elsewhere/other.root\n"
                        f"{hashlib.sha256(self.ref.read_bytes()).hexdigest()}  {self.ref}\n")
        fence = self.repo / FENCE_REL
        fence.parent.mkdir(parents=True)
        fence.write_text('echo "fence" >> "$TEST_CALLS"; exit ${TEST_FENCE_RC:-0}\n')
        g = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(g + ["commit", "-q", "-m", "M"], cwd=self.repo, check=True)
        self.M = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo, capture_output=True, text=True,
                                check=True).stdout.strip()
        _write_stub(self.bindir, "ssh-local", 'exec "$@"')
        _write_stub(self.bindir, "hostname", 'echo "${TEST_HOSTNAME:-login07}"')
        _write_stub(self.bindir, "sacct", 'cat "$TEST_SACCT" 2>/dev/null; exit ${TEST_SACCT_RC:-0}')
        _write_stub(self.bindir, "squeue", 'echo "squeue must never be called" >&2; exit 99')
        _write_stub(self.bindir, "sbatch",
                    'echo "sbatch $*" >> "$TEST_CALLS"; n=$(grep -c "^sbatch" "$TEST_CALLS"); echo "9000$n"')
        _write_stub(self.bindir, "md5sum", r'''
for f in "$@"; do python3 -c "import hashlib,sys; print(hashlib.md5(open(sys.argv[1],'rb').read()).hexdigest()+' '+sys.argv[1])" "$f"; done
''')
        _write_stub(self.bindir, "sha256sum", r'''
for f in "$@"; do python3 -c "import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest()+'  '+sys.argv[1])" "$f"; done
''')
        self.sacct = tmp_path / "sacct.psv"
        self.sacct.write_text("")

    def env(self, **kw):
        e = os.environ.copy()
        e.pop("SLURM_JOB_ID", None)
        e["PATH"] = f"{self.bindir}:{e['PATH']}"
        e["GEANTTW_SSH"] = str(self.bindir / "ssh-local")
        e["GEANTTW_LOCAL_REPO"] = str(self.repo)
        e["GEANTTW_TEST_B"] = str(self.B)
        e["GEANTTW_TEST_REPO"] = str(self.repo)
        e["TEST_CALLS"] = str(self.calls)
        e["TEST_SACCT"] = str(self.sacct)
        e["GEANTTW_TEST_PY"] = "python3"
        e["GEANTTW_TEST_REF"] = str(self.ref)
        e.update(kw)
        return e

    def connect(self, step, *args, m=None, acks=("cov2d:ack-0001", "nue:ack-0001"), **kw):
        return _run(["bash", str(CONNECT_SH), step, m or self.M, *acks, *args], self.env(**kw), timeout=60)

    def live(self, *jobs):
        self.sacct.write_text("".join(f"{i}|{j}|0|1|60\n" for i, j in enumerate(jobs, 100)))

    def calls_lines(self):
        return self.calls.read_text().splitlines() if self.calls.exists() else []


PAST = "2026-01-01T00:00:00Z"


class TestConnect:
    def test_bad_step_and_bad_m_refuse(self, tmp_path):
        h = RemoteHarness(tmp_path)
        assert h.connect("p2").returncode == 9
        assert h.connect("deploy", m="abc").returncode == 9
        assert h.connect("deploy", m="f" * 40).returncode == 9   # not a commit of the local repository
        assert not h.calls_lines(), "something ran"

    def test_fence_failure_stops_before_any_remote_step(self, tmp_path):
        h = RemoteHarness(tmp_path)
        r = h.connect("deploy", TEST_FENCE_RC="3")
        assert r.returncode == 8, r.stdout
        assert "cov2d_fence.sh exited 3" in r.stdout
        assert h.calls_lines() == ["fence"]
        assert not (h.B / "deploy").exists()

    def test_deploy_clones_clean_at_m_and_prints_shas(self, tmp_path):
        h = RemoteHarness(tmp_path)
        r = h.connect("deploy")
        assert r.returncode == 0, r.stdout + r.stderr
        head = subprocess.run(["git", "-C", str(h.B / "deploy"), "rev-parse", "HEAD"], capture_output=True,
                              text=True).stdout.strip()
        assert head == h.M
        assert "deploy at %s: clean" % h.M in r.stdout
        assert r.stdout.count("geanttw_remote.sh") >= 2   # the Mac's line and the remote's sha256sum line
        for f in ("geanttw_build.sh", "geanttw_evloop.sbatch", "geanttw_sacct.py", "geanttw_provenance.py",
                  "dumpcmp.py", "p0_check.py", "S0-src_base.sha256"):
            assert f"  {f}" in r.stdout, f

    def test_deploy_twice_refuses(self, tmp_path):
        h = RemoteHarness(tmp_path)
        assert h.connect("deploy").returncode == 0
        r = h.connect("deploy")
        assert r.returncode == 8 and "exists" in r.stdout

    def test_remote_script_must_match_m(self, tmp_path):
        h = RemoteHarness(tmp_path)
        assert h.connect("deploy").returncode == 0
        rs = h.B / "deploy" / CODE_REL / "geanttw_remote.sh"
        rs.write_text(rs.read_text() + "\n# edited\n")
        r = h.connect("build")
        assert r.returncode == 8 and "the deploy's geanttw_remote.sh" in r.stdout
        assert not any(c.startswith("build ") for c in h.calls_lines())

    def test_build_runs_once(self, tmp_path):
        h = RemoteHarness(tmp_path)
        assert h.connect("deploy").returncode == 0
        r = h.connect("build")
        assert r.returncode == 0, r.stdout
        assert "CHECK LIBMAT_IDENTICAL PASS" in r.stdout
        r2 = h.connect("build")
        assert r2.returncode == 8 and "build.log exists" in r2.stdout

    def test_build_failure_stops(self, tmp_path):
        h = RemoteHarness(tmp_path)
        assert h.connect("deploy").returncode == 0
        r = h.connect("build", TEST_BUILD_RC="1")
        assert r.returncode == 8 and "geanttw_build.sh exited 1" in r.stdout


class TestRemoteGuards:
    def deployed(self, tmp_path):
        h = RemoteHarness(tmp_path)
        assert h.connect("deploy").returncode == 0
        return h

    def test_not_a_login_node_refuses(self, tmp_path):
        h = RemoteHarness(tmp_path)
        r = h.connect("deploy", TEST_HOSTNAME="nid004211")
        assert r.returncode == 8 and "not a login node" in r.stdout

    def test_inside_slurm_refuses(self, tmp_path):
        h = RemoteHarness(tmp_path)
        r = h.connect("deploy", SLURM_JOB_ID="77")
        assert r.returncode == 8 and "inside Slurm job" in r.stdout

    def test_deploy_moved_off_m_stops(self, tmp_path):
        h = self.deployed(tmp_path)
        d = h.B / "deploy"
        (d / "x").write_text("x")
        subprocess.run(["git", "-C", str(d), "add", "x"], check=True)
        subprocess.run(["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m",
                        "x"], check=True)
        r = h.connect("build")
        assert r.returncode == 8 and "not %s" % h.M in r.stdout

    def test_dirty_deploy_stops(self, tmp_path):
        h = self.deployed(tmp_path)
        (h.B / "deploy" / "stray.txt").write_text("x")
        r = h.connect("build")
        assert r.returncode == 8 and "porcelain" in r.stdout


class TestP0:
    def built(self, tmp_path, **kw):
        h = RemoteHarness(tmp_path)
        assert h.connect("deploy").returncode == 0
        assert h.connect("build", **kw).returncode in (0, 8)
        return h

    def test_p0_submits_both_after_both_smokes(self, tmp_path):
        h = self.built(tmp_path)
        r = h.connect("p0", PAST)
        assert r.returncode == 0, r.stdout + r.stderr
        calls = [c for c in h.calls_lines() if c.startswith(("smoke", "sbatch"))]
        assert [c.split()[0] for c in calls] == ["smoke", "smoke", "sbatch", "sbatch"]
        assert "geanttw_p0_pin_1L 01:00:00 smoke=1" in calls[0]
        assert "geanttw_p0_pat_1L 01:00:00 smoke=1" in calls[1]
        assert "--job-name=geanttw_p0_pin_1L --time=01:00:00" in calls[2]
        assert "--job-name=geanttw_p0_pat_1L --time=01:00:00" in calls[3]
        md5 = hashlib.md5((h.B / "prefix-pin" / "bin" / "runEventLoopOmniFold").read_bytes()).hexdigest()
        assert f" pin 1L {md5} " in calls[2]
        g = (h.B / "run" / "gates" / "ll5d_atime_post.txt").read_text()
        assert f"ll5d_atime_post_utc={PAST}" in g
        assert len((h.B / "run" / "p0" / "submissions.log").read_text().splitlines()) == 2

    @pytest.mark.parametrize("arg", ["", "2026-01-01 00:00:00", "2099-01-01T00:00:00Z"])
    def test_p0_atime_post_must_be_given_well_formed_and_past(self, tmp_path, arg):
        h = self.built(tmp_path)
        r = h.connect("p0", *( [arg] if arg else [] ))
        assert r.returncode == 8, r.stdout
        assert not (h.B / "run" / "gates" / "ll5d_atime_post.txt").exists()
        assert not any(c.startswith("sbatch") for c in h.calls_lines())

    def test_p0_gate_records_another_time_stops(self, tmp_path):
        h = self.built(tmp_path)
        (h.B / "run" / "gates").mkdir(parents=True)
        (h.B / "run" / "gates" / "ll5d_atime_post.txt").write_text("ll5d_atime_post_utc=2025-01-01T00:00:00Z\n")
        r = h.connect("p0", PAST)
        assert r.returncode == 8 and "records another time" in r.stdout

    def test_p0_needs_every_check_pass(self, tmp_path):
        h = RemoteHarness(tmp_path)
        assert h.connect("deploy").returncode == 0
        h.connect("build", TEST_FAIL_CHECK="LIBMAT_IDENTICAL")
        r = h.connect("p0", PAST)
        assert r.returncode == 8 and "CHECK LIBMAT_IDENTICAL is not PASS" in r.stdout
        assert not any(c.startswith("sbatch") for c in h.calls_lines())

    @pytest.mark.parametrize("job", ["cov2d_ll5d|RUNNING", "t2a_x|PENDING", "geanttw_p0_pin_1L|PENDING"])
    def test_p0_refuses_fenced_or_duplicate_jobs(self, tmp_path, job):
        h = self.built(tmp_path)
        h.live(job)
        r = h.connect("p0", PAST)
        assert r.returncode == 8, r.stdout
        assert not any(c.startswith("sbatch") for c in h.calls_lines())

    def test_p0_unrelated_jobs_do_not_block(self, tmp_path):
        h = self.built(tmp_path)
        h.live("ibub_run|RUNNING", "xcov2d|RUNNING", "cov2d_old|COMPLETED")
        assert h.connect("p0", PAST).returncode == 0

    def test_p0_twice_refuses(self, tmp_path):
        h = self.built(tmp_path)
        assert h.connect("p0", PAST).returncode == 0
        r = h.connect("p0", PAST)
        assert r.returncode == 8 and "already submitted" in r.stdout
        assert sum(c.startswith("sbatch") for c in h.calls_lines()) == 2

    def test_p0_smoke_refusal_submits_nothing(self, tmp_path):
        h = self.built(tmp_path)
        r = h.connect("p0", PAST, TEST_SMOKE_REFUSES="pat")
        assert r.returncode == 8 and "smoke refuses geanttw_p0_pat_1L" in r.stdout
        assert not any(c.startswith("sbatch") for c in h.calls_lines())

    def test_p0_sbatch_failure_stops(self, tmp_path):
        h = self.built(tmp_path)
        _write_stub(h.bindir, "sbatch", 'echo "sbatch $*" >> "$TEST_CALLS"; exit 1')
        r = h.connect("p0", PAST)
        assert r.returncode == 8 and "sbatch geanttw_p0_pin_1L failed" in r.stdout
        sub = h.B / "run" / "p0" / "submissions.log"
        assert not sub.exists() or not sub.read_text().strip()

    def test_p0_unwritable_gate_stops(self, tmp_path):
        h = self.built(tmp_path)
        (h.B / "run" / "gates").write_text("a file, not a directory\n")
        r = h.connect("p0", PAST)
        assert r.returncode == 8 and "cannot record" in r.stdout
        assert not any(c.startswith("sbatch") for c in h.calls_lines())

    def test_remote_unknown_step_refuses(self, tmp_path):
        h = self.built(tmp_path)
        r = _run(["bash", str(h.B / "deploy" / CODE_REL / "geanttw_remote.sh"), "p2", h.M, "cov2d:ack-0001",
                  "nue:ack-0001"], h.env())
        assert r.returncode == 9 and "unknown step" in r.stdout

    def test_p0_missing_binary_stops(self, tmp_path):
        h = self.built(tmp_path)
        (h.B / "prefix-pat" / "bin" / "runEventLoopOmniFold").unlink()
        r = h.connect("p0", PAST)
        assert r.returncode == 8 and "no binary" in r.stdout


class TestAcks:
    @pytest.mark.parametrize("acks", [("", "nue:ack-0001"), ("cov2d:ack-0001", ""), ("cov2d ack", "nue:ack-0001"),
                                      ("short", "nue:ack-0001")])
    def test_connect_requires_both_acks(self, tmp_path, acks):
        h = RemoteHarness(tmp_path)
        r = h.connect("deploy", acks=acks)
        assert r.returncode == 9 and "ack" in r.stdout
        assert not h.calls_lines()

    def test_remote_requires_both_acks(self, tmp_path):
        h = RemoteHarness(tmp_path)
        assert h.connect("deploy").returncode == 0
        rs = str(h.B / "deploy" / CODE_REL / "geanttw_remote.sh")
        for m, acks, msg in ((h.M, ["x"], "the cov2d ack is missing or not a token"),
                             (h.M, ["cov2d:ack-0001", "bad ack!"], "the NuE exception's ack is missing or not a token"),
                             ("abc", ["cov2d:ack-0001", "nue:ack-0001"], "M 'abc' is not a 40-hex commit")):
            r = _run(["bash", rs, "build", m, *acks], h.env())
            assert r.returncode == 9 and f"REFUSED (nothing written): {msg}" in r.stdout, r.stdout

    def test_every_step_records_its_acks(self, tmp_path):
        h = RemoteHarness(tmp_path)
        assert h.connect("deploy", acks=("cov2d:a-0001", "nue:b-0001")).returncode == 0
        assert h.connect("build", acks=("cov2d:a-0002", "nue:b-0002")).returncode == 0
        log = (h.B / "run" / "acks.log").read_text().splitlines()
        assert [ln.split()[1] for ln in log] == ["step=deploy", "step=build"]
        assert log[0].endswith("cov2d=cov2d:a-0001 nue=nue:b-0001")
        assert log[1].endswith("cov2d=cov2d:a-0002 nue=nue:b-0002")


class TestP0Gates:
    def built(self, tmp_path):
        h = RemoteHarness(tmp_path)
        assert h.connect("deploy").returncode == 0
        assert h.connect("build").returncode == 0
        return h

    def test_gate_is_recorded_only_after_the_checks(self, tmp_path):
        h = self.built(tmp_path)
        r = h.connect("p0", PAST, TEST_SMOKE_REFUSES="pin")
        assert r.returncode == 8
        assert not (h.B / "run" / "gates" / "ll5d_atime_post.txt").exists()

    def test_cap_gate_refuses(self, tmp_path):
        h = self.built(tmp_path)
        h.sacct.write_text("".join(f"{i}|geanttw_p2_1A|COMPLETED|{3600 * 30}|1|60\n" for i in range(7)))
        r = h.connect("p0", PAST)
        assert r.returncode == 8 and "the cap gate refuses geanttw_p0_pin_1L" in r.stdout
        assert not any(c.startswith("sbatch") for c in h.calls_lines())

    def test_unreadable_sacct_stops(self, tmp_path):
        h = self.built(tmp_path)
        h.sacct.write_text("sacct: error: slurmdbd down\n")
        r = h.connect("p0", PAST)
        assert r.returncode == 8 and "sacct fence" in r.stdout


class TestCheck:
    def submitted(self, tmp_path, outputs=("pin", "pat")):
        h = RemoteHarness(tmp_path)
        assert h.connect("deploy").returncode == 0
        assert h.connect("build").returncode == 0
        assert h.connect("p0", PAST).returncode == 0
        for b in outputs:
            (h.B / "run" / "p0" / b / f"runEventLoopOmniFold_GEANTTW_{b}_1L.root").write_text(f"dump {b}\n")
        return h

    def test_check_copies_the_reference_and_runs_p0_check(self, tmp_path):
        h = self.submitted(tmp_path)
        r = h.connect("check")
        assert r.returncode == 0, r.stdout + r.stderr
        copy = h.B / "run" / "p0" / "ref" / h.ref.name
        assert copy.read_bytes() == h.ref.read_bytes()
        call = [c for c in h.calls_lines() if c.startswith("p0_check ")][0].split()
        want = hashlib.sha256(h.ref.read_bytes()).hexdigest()
        assert call[call.index("--ref") + 1] == str(copy) and call[call.index("--ref-sha") + 1] == want
        assert call[call.index("--json") + 1] == str(h.B / "run" / "p0" / "p0_check.json")

    def test_check_needs_both_outputs(self, tmp_path):
        h = self.submitted(tmp_path, outputs=("pin",))
        r = h.connect("check")
        assert r.returncode == 8 and "no P0 output for pat" in r.stdout

    def test_check_waits_for_live_p0_jobs(self, tmp_path):
        h = self.submitted(tmp_path)
        h.live("geanttw_p0_pat_1L|RUNNING")
        r = h.connect("check")
        assert r.returncode == 8 and "P0 jobs still live" in r.stdout

    def test_check_needs_the_committed_sha(self, tmp_path):
        h = self.submitted(tmp_path)
        r = h.connect("check", GEANTTW_TEST_REF=str(tmp_path / "not-in-the-manifest.root"))
        assert r.returncode == 8 and "no committed sha256" in r.stdout

    def test_check_failure_stops(self, tmp_path):
        h = self.submitted(tmp_path)
        r = h.connect("check", TEST_P0CHECK_RC="1")
        assert r.returncode == 8 and "p0_check.py exited 1" in r.stdout


class TestScriptText:
    """Properties that are absences or static headers, checked on the text."""

    def test_sbatch_headers(self, tmp_path):
        script = EVLOOP_SH.read_text()
        assert "#SBATCH --qos=shared" in script
        assert "#SBATCH --constraint=cpu" in script
        assert "#SBATCH --cpus-per-task=2" in script
        assert "#SBATCH --mem=16G" in script
        assert "#SBATCH --no-requeue" in script

    def test_no_source_setup_salloc(self, tmp_path):
        """Must never source setup_salloc_env.sh."""
        lines = EVLOOP_SH.read_text().split("\n")
        for line in lines:
            s = line.strip()
            if s.startswith("#"):
                continue
            if "source" in s and "setup_salloc_env" in s:
                pytest.fail(f"sources setup_salloc_env.sh: {line}")




def _commit(repo, *git_args):
    g = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(g + list(git_args), check=True)
    subprocess.run(g + ["commit", "-q", "-m", "x"], check=True)
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()


class TestEachStopIsItsOwn:
    """Every error-path stop, pinned by its own message: a later guard that catches the same failure is not enough,
    since a mutant that skips the first stop would still exit nonzero there."""

    def test_connect_mktemp_failure_stops(self, tmp_path):
        h = RemoteHarness(tmp_path)
        _write_stub(h.bindir, "mktemp", "exit 1")   # macOS mktemp falls back from a bad TMPDIR, so a stub fails it
        r = h.connect("deploy")
        assert r.returncode == 8 and "STOP: mktemp" in r.stdout, r.stdout
        assert not h.calls_lines()

    @pytest.mark.parametrize("rel,msg", [(FENCE_REL, "no %s at {m}" % FENCE_REL),
                                         (CODE_REL + "/geanttw_remote.sh", "no geanttw_remote.sh at {m}")])
    def test_connect_script_missing_at_m_stops(self, tmp_path, rel, msg):
        h = RemoteHarness(tmp_path)
        m2 = _commit(h.repo, "rm", "-q", rel)
        r = h.connect("deploy", m=m2)
        assert r.returncode == 8 and "STOP: " + msg.format(m=m2) in r.stdout, r.stdout
        assert not h.calls_lines(), "the fence or a remote step ran"
        assert not (h.B / "deploy").exists()

    def test_clone_failure_stops(self, tmp_path):
        h = RemoteHarness(tmp_path)
        r = h.connect("deploy", GEANTTW_TEST_REPO=str(tmp_path / "no-repo"))
        assert r.returncode == 8 and "STOP: clone failed" in r.stdout, r.stdout

    def test_checkout_failure_stops(self, tmp_path):
        h = RemoteHarness(tmp_path)
        other = tmp_path / "other"
        subprocess.run(["git", "clone", "-q", str(h.repo), str(other)], check=True)
        (h.repo / "y").write_text("y")
        m2 = _commit(h.repo, "add", "y")   # a commit of the local repository the remote's clone lacks
        r = h.connect("deploy", m=m2, GEANTTW_TEST_REPO=str(other))
        assert r.returncode == 8 and f"STOP: checkout {m2} failed" in r.stdout, r.stdout

    def test_unreadable_deploy_head_stops(self, tmp_path):
        h = RemoteHarness(tmp_path)
        assert h.connect("deploy").returncode == 0
        (h.B / "deploy" / ".git" / "HEAD").write_text("ref: refs/heads/no-such-branch\n")
        r = h.connect("build")
        assert r.returncode == 8 and "STOP: git rev-parse failed in" in r.stdout, r.stdout

    def test_p0_without_build_log_stops(self, tmp_path):
        h = RemoteHarness(tmp_path)
        assert h.connect("deploy").returncode == 0
        r = h.connect("p0", PAST)
        assert r.returncode == 8 and "STOP: no build.log" in r.stdout, r.stdout

    def test_p0_sacct_failure_stops(self, tmp_path):
        h = TestP0Gates().built(tmp_path)
        r = h.connect("p0", PAST, TEST_SACCT_RC="1")
        assert r.returncode == 8 and "STOP: sacct failed" in r.stdout, r.stdout
        assert not any(c.startswith("sbatch") for c in h.calls_lines())

    def test_p0_run_dirs_failure_stops(self, tmp_path):
        h = TestP0Gates().built(tmp_path)
        (h.B / "run" / "logs").write_text("a file where the logs directory goes\n")
        r = h.connect("p0", PAST)
        assert r.returncode == 8 and "STOP: mkdir run dirs" in r.stdout, r.stdout
        assert not any(c.startswith(("sbatch", "smoke")) for c in h.calls_lines())

    def test_check_ref_dir_failure_stops(self, tmp_path):
        h = TestCheck().submitted(tmp_path)
        (h.B / "run" / "p0" / "ref").write_text("a file where the ref directory goes\n")
        r = h.connect("check")
        assert r.returncode == 8 and "STOP: mkdir ref" in r.stdout, r.stdout
        assert not any(c.startswith("p0_check") for c in h.calls_lines())

    def test_check_reference_copy_failure_stops(self, tmp_path):
        h = TestCheck().submitted(tmp_path)
        h.ref.unlink()   # its sha is still in the committed manifest; the copy is what fails
        r = h.connect("check")
        assert r.returncode == 8 and "STOP: the O_NOATIME copy of the reference failed" in r.stdout, r.stdout
        assert not any(c.startswith("p0_check") for c in h.calls_lines())


def only_refusal(r, msg, rc=2):
    """The guard under test refused, and it alone: one REFUSE line, the expected one. A mutant that drops the guard's
    `exit` still prints its message, then either runs on to success or dies at a later guard with a second REFUSE."""
    refs = [ln for ln in r.stderr.splitlines() if "REFUSE" in ln]
    assert r.returncode == rc, r.stderr
    assert len(refs) == 1 and msg in refs[0], refs


class TestEachEvloopGuardIsItsOwn:
    def args(self, h, build=None, pl=None, extra=()):
        return ["bash", str(EVLOOP_SH), str(h.B), build or h.build, pl or h.pl, h.binary_md5, str(h.deploy), *extra]

    def test_build_must_be_pin_or_pat(self, tmp_path):
        h = EvloopHarness(tmp_path)
        only_refusal(_run(self.args(h, build="xyz"), h.env(name="geanttw_p0_xyz_1L")),
                     "REFUSE: build must be pin or pat, got 'xyz'")

    def test_outside_slurm_without_smoke_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        only_refusal(h.run_evloop(GEANTTW_SMOKE=""), "REFUSE: not inside a Slurm job")

    def test_name_outside_both_phases_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        only_refusal(h.run_evloop(name="cov2d_p0_pin_1L"), "does not match geanttw_p0_* or geanttw_p2_*")

    def test_name_of_another_build_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        only_refusal(h.run_evloop(name="geanttw_p0_pat_1L"), "REFUSE: job name 'geanttw_p0_pat_1L' is not 'geanttw_p0_pin_1L'")

    def test_p0_needs_1L(self, tmp_path):
        h = EvloopHarness(tmp_path)
        only_refusal(_run(self.args(h, pl="1A"), h.env(name="geanttw_p0_pin_1A")), "REFUSE: p0 requires PL=1L, got '1A'")

    def p2(self, tmp_path, text="1L 01:00:00\n", sha=None, extra=None):
        h = EvloopHarness(tmp_path, build="pat", phase="p2")
        lim = tmp_path / "limits.txt"
        lim.write_text(text)
        ex = [str(lim), sha or sha256_of(lim)] if extra is None else extra
        return h.run_evloop(extra_args=ex, name="geanttw_p2_1L")

    def test_p2_needs_a_limits_file(self, tmp_path):
        only_refusal(self.p2(tmp_path, extra=[]), "REFUSE: p2 requires a limits file and its sha256")

    def test_p2_limits_sha_must_match(self, tmp_path):
        only_refusal(self.p2(tmp_path, sha="0" * 64), "REFUSE: p2 limits file sha256")

    def test_p2_limits_must_name_the_playlist(self, tmp_path):
        only_refusal(self.p2(tmp_path, text="1A 01:00:00\n"), "REFUSE: no limit found for playlist 1L")

    def test_fence_mktemp_failure_refuses(self, tmp_path):
        h = EvloopHarness(tmp_path)
        _write_stub(h.bindir, "mktemp", "exit 1")
        only_refusal(h.run_evloop(), "REFUSE: mktemp failed (at start)")

    def test_fence_sacct_failure_refuses_alone(self, tmp_path):
        h = EvloopHarness(tmp_path)
        _write_stub(h.bindir, "sacct", "exit 1")
        only_refusal(h.run_evloop(), "REFUSE: sacct failed (at start)")

    def test_manifest_differs_refuses_alone(self, tmp_path):
        h = EvloopHarness(tmp_path)
        (h.deploy / "2d-unfolding" / "playlist_manifests" / f"{h.pl}_Data.txt").write_text("modified path\n")
        only_refusal(h.run_evloop(), "is not the deploy's committed 2d-unfolding/playlist_manifests/1L_Data.txt")

    def test_missing_conda_refuses_alone(self, tmp_path):
        h = EvloopHarness(tmp_path)
        only_refusal(h.run_evloop(ROOT628_CONDA=str(tmp_path / "no-conda")), "is missing (no legacy module fallback)")

    def test_work_dir_failure_exits_4_before_the_binary(self, tmp_path):
        h = EvloopHarness(tmp_path)
        h.slurm_stubs()
        d = h.B / "run" / "p0" / h.build
        d.rmdir()
        d.write_text("a file where the build's run directory goes\n")
        r = h.run_full()
        assert r.returncode == 4, r.stderr
        assert "start=" not in r.stderr, "the binary was started"


class TestEachRemoteStopIsItsOwn:
    def test_no_deploy_stops(self, tmp_path):
        h = RemoteHarness(tmp_path)
        rs = h.repo / CODE_REL / "geanttw_remote.sh"
        r = _run(["bash", str(rs), "build", h.M, "cov2d:ack-0001", "nue:ack-0001"], h.env())
        assert r.returncode == 8 and f"STOP: no deploy at {h.B}/deploy" in r.stdout, r.stdout

    def test_run_dir_failure_stops(self, tmp_path):
        h = RemoteHarness(tmp_path)
        h.B.mkdir()
        (h.B / "run").write_text("a file where run/ goes\n")
        r = h.connect("deploy")
        assert r.returncode == 8 and f"STOP: mkdir {h.B}/run" in r.stdout, r.stdout

    def test_unwritable_acks_log_stops(self, tmp_path):
        h = RemoteHarness(tmp_path)
        (h.B / "run" / "acks.log").mkdir(parents=True)
        r = h.connect("deploy")
        assert r.returncode == 8 and f"STOP: cannot write {h.B}/run/acks.log" in r.stdout, r.stdout

    def test_connect_names_each_refusal(self, tmp_path):
        h = RemoteHarness(tmp_path)
        r = h.connect("p2")
        assert r.returncode == 9 and "REFUSED: step must be deploy, build, p0 or check, got 'p2'" in r.stdout
        r = h.connect("deploy", m="abc")
        assert r.returncode == 9 and "REFUSED: M 'abc' is not a 40-hex commit" in r.stdout
        r = h.connect("deploy", m="f" * 40)
        assert r.returncode == 9 and f"REFUSED: {'f' * 40} is not a commit of" in r.stdout


def test_build_missing_conda_refuses_alone(tmp_path):
    h = BuildHarness(tmp_path)
    r = h.run_build(ROOT628_CONDA=str(tmp_path / "none"))
    assert r.returncode == 2, r.stderr
    refs = [ln for ln in r.stderr.splitlines() if "REFUSE" in ln]
    assert len(refs) == 1 and "is missing" in refs[0], refs


def test_build_activation_survives_nounset(tmp_path):
    """root_6_28's activate.d reads unset variables; the harness's conda stub does too, so a build that left
    nounset on through the activation would die here instead of passing."""
    h = BuildHarness(tmp_path)
    r = h.run_build()
    assert "unbound variable" not in r.stderr, r.stderr
    assert r.returncode == 0, r.stderr


def test_build_binary_without_rpath_records_none_and_passes(tmp_path):
    """No RPATH/RUNPATH at all is an empty array; under set -u, bash 3.2 calls expanding it unbound."""
    h = BuildHarness(tmp_path)
    _write_stub(h.bindir, "readelf", "exit 0")
    r = h.run_build()
    assert r.returncode == 0, r.stderr
    log = (h.B / "run" / "p0" / "build.log").read_text()
    assert "CHECK RPATH_CLEAN PASS" in log
    assert all(ln.endswith(" NONE") for ln in log.splitlines() if ln.startswith("RPATH "))
