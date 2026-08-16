# BEN-347 — an environment prescription that travels in a message, and the uniformity tell that caught it

**Date:** 2026-08-16 · **Lane:** B, with the wrong incantation supplied by the mediator
**Near-miss:** a 10-endpoint re-unfold escalated to Joseph on a harness artifact
**Index row:** `docs/orchestration/FINDINGS.md`

---

## The instance

I was asked to establish whether stage 2's receipt-validated resume would SKIP or re-run each of the
10 standard-P4 endpoints. I reproduced the launcher's own SKIP predicate read-only and got:

```
BeamAngleX_0 … Muon_Energy_MINOS_1     10/10   WOULD-RERUN: valid_root failed
```

That reading is **false**, and it was one message away from being escalated as *ten corrupt physics
products*, which would have authorised a full re-unfold. The cause:

```
$ module load tensorflow/2.15.0 && python3 -c "import ROOT"
ModuleNotFoundError: No module named 'ROOT'
```

**ROOT is not importable under the TF module.** My probe's `valid_root` check was
`python3 -c "import ROOT; …" >/dev/null 2>&1`, so an `ImportError` became a verdict about ten files.
Re-run in the launcher's own environment — `setup_salloc_env.sh`, which activates the `root_6_28`
conda prefix (Python 3.11.14, ROOT 6.28/12):

```
STAGE 1   10/10   WOULD-SKIP   (valid merged: all 4 trees)
STAGE 2   10/10   WOULD-SKIP   (receipt validated)
```

**The opposite answer.** Both directions were then power-controlled in the same run — a wrong `--tag`
and a foreign `--merged` are each rejected with a specific message — so the SKIPs are a measurement
rather than a tautology.

## THE TELL, which is the transferable part

**Uniformity. 10/10 identical failures is a property of the harness, not of ten independently
produced files.** Ten artifacts built on different days from different inputs do not fail the same
way for the same reason; when they appear to, the thing they share is the instrument. This is cheap,
requires no domain knowledge, and is available *before* any investigation of the artifacts themselves.

It generalises past environments: any time a check returns the same verdict for every member of a set
that ought to vary, suspect the check. Sibling of `BEN-344` (a null that could not have been
otherwise) with a different detection route — there the question is *could this have come out
differently*, here it is *why did everything come out the same*.

## Why the prescription was wrong rather than merely stale

The mediator supplied `module load tensorflow/2.15.0` as "the environment", and **for the thing it was
supplied for it is correct**: the cluster's default `python3` is 3.6.15, where `p4_lib.py:13`'s
`from __future__ import annotations` is a `SyntaxError`, and the TF module is what yields a Python new
enough to import `p4_lib` for the verifier-token check. It is simply not the environment for anything
touching ROOT.

**So this repo needs two different environments for two different checks, and which one you need is
not visible from the command you are about to run.** That is the actual defect, and it is not fixable
by relaying a better incantation:

> **An environment prescription that travels in a message is the failure. The executable form is a
> script that sources its own environment.**

Both probes now begin with `source "$REPO/setup_salloc_env.sh"` and **print the resolved
`python3 -V` and `ROOT.gROOT.GetVersion()` in their output**, so the environment is evidenced in the
artifact rather than assumed from the caller's shell. A future reader of those logs can see which
interpreter produced the verdict; a future reader of the original could not.

Rule, stated so it can be checked: **`setup_salloc_env.sh` for anything that touches ROOT; the TF
module only for `p4_lib`-only checks; and any script that cares must source its own.**

## Second instance, same day, same class

Dispatching the run:

```
bash: /tmp/p4_runner_laneB.sh: No such file or directory
srun: error: nid004254: task 0: Exited with exit code 127
```

**`/tmp` is node-local on Perlmutter.** `scp` put the runner on the login node; `srun` ran it on
`nid004254`, which has its own `/tmp`. Earlier read-only probes worked from `/tmp` only because they
ran on the login node via `bash -lc` and never crossed to a compute node — **a location assumption
carried from a context where it happened to hold.** Same shape as the ROOT/TF error: an environmental
fact that was true where it was learned and false where it was used. Cost ~1 minute because the
failure was loud; the ROOT one cost more because it was silent.

## The rule that would have caught both immediately

**Never suppress stderr on a check whose failure you intend to interpret.** `2>/dev/null` on the
`valid_root` probe converted a diagnosable `ModuleNotFoundError` into an undiagnosable physics claim,
and it is `BEN-026`'s principle — *do not destroy the evidence at write time* — applied to a probe
rather than to a long run. The probes now capture the failure text and print it beside the verdict, so
a wrong environment announces itself instead of masquerading as a result.

## Attribution

The wrong incantation came from the mediator, which reported that in full and unprompted; the
suppressed stderr, the non-covering assumption, and the false result were mine. **The escalation would
have been the mediator's, of my artifact, on its incantation** — which is worth stating because no
single lane's diligence would have caught it: the mediator could not see my `2>/dev/null`, and I could
not see that its incantation was scoped to a different check.

## Related

`BEN-344` (a null shown capable of being non-null), `BEN-026` (never truncate a diagnostic at write
time), `BEN-315` (a null result is evidence about the search), `BEN-228` (a hand-maintained fact about
a machine-derivable one), `BEN-346` (an artifact read as covering more than it does).
