"""Generate rpd_prologue5_login.sh from rerun 4's connect: new head, root, config and send list."""
import base64
import hashlib
import re

S = "/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/7e3f49f7-e8e4-452d-b380-399d4f6c529e/scratchpad/"
src = open(S + "rpd_prologue4_login.sh").read().split("\n")
cfg = open(S + "prol5/policy-config.json", "rb").read()
cfgsha = hashlib.sha256(cfg).hexdigest()
for name, want in (("p4_c3_check.py", "de19736936dacd767c6f4d81ecb502beb3dc049ae3c0718675486644fe12fb96"),
                   ("p4_check_redaction.py", "992be729a3604cf8bae7ea04dfab93aeae9e259b647d3a4d598fd287b2736316")):
    assert hashlib.sha256(open(S + name, "rb").read()).hexdigest() == want, name
header = """#!/bin/bash
# RPD-RECO data-free prologue, rerun 5 (the director's go to prepare, 2026-11-08: #848 GO at 9634aadf, tested source
# 4fb2add1, coverage-5b-audit https://github.com/josephbaileyy/MINERvA-OmniFold/pull/848#issuecomment-6726690708).
# What it must show: the environment guard, the platform-library pins, the classifier through process exit and the
# post-exit library verification all PASS (data-free-trace.json written). Any STOP is reported as recorded, unrepaired.
# Login node, no Slurm job, 0 node-h, fresh clone, the real MAT source, the traced worker, no analysis input read, no
# flux connect.
# In this connect, in order:
#   1. the COV2D fence: every josephrb job must be named rs1_* or ens1_*; cov2d-* or any other name refuses;
#   2. the fresh clone's HEAD and porcelain, with the blob and sha256 of the five prologue files;
#   3. the policy config, written from this script and checked against its sha256: the draft template
#      late-platform-library-repair-20261108/production-config.draft.json at the head, its slots resolved to rerun 4's
#      values (clone root prologue5-20261108; MAT prefix /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt;
#      EXTRACT_RUN left unresolved, as in rerun 4: the prologue extracts nothing; the template's RooUnfold build slot
#      "${BOUND_CHECKOUT}/unbinned_unfolding/build" resolved to /pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build,
#      the directory the MAT environment puts on LD_LIBRARY_PATH, rerun 4's trace opened and the head's replay test
#      names, test_fd_rpd_reco.py:4827-4829); the five repo pins, re-hashed at the
#      head, are unchanged. The two check scripts are rerun 4's, byte-identical: the C3 and public-export functions are
#      AST-identical between rerun 4's head and this one;
#   4. the strace probe;
#   5. the prologue wrapper at the head. Its stdout and stderr go to $R/wrapper.out and are printed only after the
#      redaction check passes;
#   6. C3 and the redaction check, under MAT_PYTHON -I -S, as in rerun 4;
#   7. only if both pass: a base64 tar of an explicit file list, which names nothing under .rpd-private.
# umask 077. The root /dev/shm/limres-rpd-prologue5-20261108 is refused if it exists, and it is left in place: the
# private record and the root are deleted after the receipt merges, under a ledger row, by a separate connect.
# Launched from a /dev/shm copy of itself ($1), which it deletes.""".split("\n")
i = next(k for k, l in enumerate(src) if l == "umask 077")
out, b64 = [], 0
for l in src[i:]:
    if l.startswith("S=6a287e1a"):
        l = "S=9634aadfa3564e0090caecc4dbf415e1318a2f5f"
    elif l.startswith("CFG_SHA="):
        l = "CFG_SHA=" + cfgsha
    elif l.startswith("printf '%s' '"):
        b64 += 1
        if b64 == 1:
            m = re.match(r"printf '%s' '([^']*)'(.*)$", l)
            l = "printf '%s' '" + base64.b64encode(cfg).decode() + "'" + m.group(2)
    l = l.replace("limres-rpd-prologue4-20261108", "limres-rpd-prologue5-20261108").replace("rpd-prologue4 rc=", "rpd-prologue5 rc=")
    l = l.replace("allowed names: rs1_*, ens1_* and, for this connect only, fd1b_pfd_*; anything else refuses",
                  "allowed names: rs1_*, ens1_*; anything else refuses")
    l = l.replace("$2 !~ /^(rs1_|ens1_|fd1b_pfd_)/", "$2 !~ /^(rs1_|ens1_)/")
    l = l.replace("run/prologue-worker.json run/data-free-trace.json; do",
                  "run/prologue-worker.json run/data-free-trace.json run/data-free-trace.STOP.json; do")
    out.append(l)
assert b64 == 3
body = "\n".join(out)
for bad in ("fd1b_pfd", "prologue4", "6a287e1a"):
    assert bad not in body, bad
assert "data-free-trace.STOP.json" in body and "(rs1_|ens1_)/" in body
txt = "\n".join(header) + "\n" + body
open(S + "prol5/rpd_prologue5_login.sh", "w").write(txt)
print("cfg", cfgsha)
print("connect", hashlib.sha256(txt.encode()).hexdigest())
