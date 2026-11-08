RPD-RECO #848: the pymon fetch (2026-11-08T02:26Z, login27, 0 node-h)

Asked by the director, 2026-11-07, for Codex2's round 2 on the prepare-receipt environment guard. Go given at
connect sha256 a404aab6fa8019dd10f6c44c899cd6b9733941611b9adc4fa8cdb4a3cdf5979a, with the four extra pymon files and
the step-5 probe kept. The question was whether NERSC's pymon sitecustomize, which #881's worker trace
(../prologue2-20261107/run/prologue.strace, lines 100-184, pid 1198232) shows executing at interpreter start, sets a
per-process key that would differ between prepare and worker.

WHAT RAN
  fence-mac.out          cov2d_fence.sh from the Mac before the connect: no cov2d-* job (02:23:37Z).
  survey.txt             login-node load survey; login27 was lowest (7.87 on 244).
  pymon_fetch_login.sh   the connect, sha256 a404aab6...979a. Launched by one ssh (saul -> login27) that writes it to
                         a /dev/shm mktemp, compares its sha256 to the expected value, then runs bash $T $T. The
                         script deletes its copy. ssh rc=0, read unpiped.
  fetch.out              its stdout. It records the remote sha256, the in-script fence (one row, 60982139 rs1_a1,
                         RUNNING: allowed), the /opt/nersc/pymon listing, each file's stat, sha256 and base64, the
                         Python version, and the probe. pymon-fetch rc=0.
  fetch.err              its stderr: the NERSC login banner and the host line only.
  No analysis input is read and no file is written on the cluster other than the self-deleting /dev/shm copy.

THE COPIES (copies/*.txt: base64 from fetch.out, decoded on the Mac; each sha256 and size equals the remote value)
  b087a13d52e0e6a2734ad076eb50f53d74dd27fced76751ca39452558de26b15   435  /opt/nersc/pymon/sitecustomize/__init__.py
  9c59539084c0a595b92b78221f3da86b7569a5c386cd7e063be67410a6102cef  9044  /opt/nersc/pymon/nersc_pymon/__init__.py
  92e89483971fd8eb9dcb35f1a65a2a409e0c6fd8304a145df83e08fcc0ed9de2   745  /opt/nersc/pymon/nersc_pymon/log.py
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855     0  /opt/nersc/pymon/nersc_pymon/_vendor/__init__.py
  5c7001de126a23bd543db1c8a0ba6924a72afecc972faa85ad8007d6d389931c  4273  /opt/nersc/pymon/nersc_pymon/_vendor/nerscjson.py
  7f867dcd9840b0b97e82ffae8eef3e6bc29e4b983841f2a82744f926e0e094c1  1485  /opt/nersc/pymon/nersc_pymon/config/default.ini
  The copies are saved as .txt so that nothing imports or collects them.

PYTHON UNDER THE SOURCED ENVIRONMENT (set +u; source setup_salloc_env.sh; set -u, as #881's wrapper does)
  python3 on PATH and MAT_PYTHON are the same interpreter: /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3,
  3.11.14 | packaged by conda-forge | (main, Oct 22 2025, 22:46:25) [GCC 14.3.0]. PYTHONPATH ends in /opt/nersc/pymon.

WHAT THE SOURCE SAYS (file:line in the copies)
  sitecustomize__init__.py.txt:9-11   unless NERSC_PYMON_DISABLE is set to something other than "0", every Python 3
                                      interpreter start runs `PyMon().site_hooks()`.
  nersc_pymon__init__.py.txt:128      PyMon.__init__ draws self.uuid = str(uuid.uuid4()).
  nersc_pymon__init__.py.txt:150-151  it reads any inherited NERSC_PYMON_UUID as parent_uuid, then unconditionally sets
                                      os.environ["NERSC_PYMON_UUID"] to its own new uuid.
  The early returns in site_hooks (:245-249: /usr/lib64 on LD_LIBRARY_PATH, SLURM_PROCID > 0) come after the
  constructor, so they do not prevent the overwrite.

THE PROBE (step 5; a hypothesis test, not the guard's diff)
  shell (after source):       <unset>
  interpreter start 1:        f2b8a283-ce01-46a5-859d-f4e6db604314
  interpreter start 2:        edc6fb99-c1a5-481e-8c79-cedbe726dd1c
  parent interpreter:         bb7a8e2f-1bb6-43a3-a2c9-2dbbb2c40c12
  its child (inherits env):   e033427f-2031-48bc-a6a1-14767a2b9932
  shell after:                <unset>
  Every interpreter start sees a different value, including a child whose inherited environment carried the parent's.
  So a full os.environ snapshot taken inside one Python process differs from one taken inside any other Python
  process in at least NERSC_PYMON_UUID.

WHAT THIS DOES NOT SETTLE
  It does not show that NERSC_PYMON_UUID is what failed #881's checked_prepared_mat, or that it is the only
  differing key. #881 recorded neither the worker's environment nor which conjunct failed. Round 2's exclusions need
  the real worker diff from the prologue rerun at Codex2's diagnostics head.
