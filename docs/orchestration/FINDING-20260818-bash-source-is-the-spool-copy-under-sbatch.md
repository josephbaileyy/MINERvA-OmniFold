# `${BASH_SOURCE[0]}` is the SPOOL COPY under `sbatch` — and the two harnesses that verify launchers both preserve it

**Lane B, 2026-08-18. `BEN-484`.** Cost: nine GPU tasks, 12 s each. Found by the first real submission of
the campaign. Fixed at `576b0cd5`.

---

## THE ONE PARAGRAPH

Slurm **copies the batch script** to `/var/spool/slurmd/job<N>/slurm_script` and executes the copy, so
inside a batch job `${BASH_SOURCE[0]}` — and `$0` — is the **spool path**, not the launcher's home. Any
self-location idiom built on either resolves to a directory containing nothing but the script. **The two
harnesses this repo uses to verify launchers — direct execution and the argv probe, which `source`s them
from a parent shell — BOTH preserve `BASH_SOURCE` as the real path.** So the idiom was verified twice, in
two environments that **share the property it depends on**, and the one environment that breaks it is the
only one production uses.

---

## 1. The failure

Three arrays, nine tasks, `exit 1:0` at `00:00:12`:

    /var/spool/slurmd/job57250483/slurm_script: line 34:
    /var/spool/slurmd/job57250483/lib_member_resume.sh: No such file or directory

The library was exactly where it belonged — 13,845 bytes in the frozen tree. Nothing was written; `mii/`
was never created.

## 2. What `sbatch` actually provides — measured, not inferred

One 1-second CPU job (the mediator's, submitted and cleaned up):

| variable | value |
|---|---|
| `BASH_SOURCE[0]` | `/var/spool/slurmd/job57252060/slurm_script` |
| `$0` | `/var/spool/slurmd/job57252060/slurm_script` |
| `SLURM_SUBMIT_DIR` | `/pscratch/.../laneb-c1-30c4d766/nd-unfolding` |
| `PWD` at start | `/pscratch/.../laneb-c1-30c4d766/nd-unfolding` |
| `scontrol show job … Command=` | `/pscratch/sd/j/josephrb/bashsource_probe.sh` — **the true original path** |

**`$0` is not an escape hatch** — it is the same spool copy. **`scontrol … Command=` is the only source
of the script's real location inside a batch job.**

## 3. Why the obvious alternative is a trap, not a fix

`SLURM_SUBMIT_DIR` **would have worked** for this run. It is refused anyway, and this is the load-bearing
judgement in the fix:

- It is the **submit** directory, not the script's. It coincided with the launcher's directory only
  because the submitter had `cd`'d there — as the run instructions told them to.
- The canonical checkout **also contains a `lib_member_resume.sh`**. So a submission from anywhere else
  would **silently source a different tree's library**, reintroducing the exact frozen-deployment defect
  the relative source was written to close — *invisibly*, by succeeding with the wrong file rather than
  failing.

**"Works because the submit cwd happened to be right" is the same class of claim as "works because
`BASH_SOURCE` happened to be real."** `PWD` at start equals `SLURM_SUBMIT_DIR`, so resolving against
`pwd` has the same property and the same fragility.

**A candidate that can resolve to the WRONG TREE is worse than one that fails closed.** Going back to a
hardcoded `${REPO}` is refused on the same grounds and one more: today's **27.5-hour stale-canonical
window** made that exposure measured rather than theoretical (`BEN-483`).

## 4. The fix is not a mechanism — it is a cascade that VALIDATES ITS OWN ANSWER

Each candidate is accepted **only if the library is actually readable there**:

    1. MNV_LAUNCHER_DIR      explicit, ZERO cost, the recommended primary
    2. dirname BASH_SOURCE   correct for direct execution and for the probe; falls through under sbatch
    3. scontrol Command=     the script's true path inside a batch job
    else                     exit 2, naming every candidate, plus BASH_SOURCE, SLURM_JOB_ID, and WHY

**That is the actual lesson: a resolver that ASSUMES cannot detect the environment where its assumption
is false.** Validating by the file's presence makes the resolver's own answer falsifiable at run time,
which is what neither the go-line nor its two verifications could do.

**`scontrol` cost is zero in the planned run** — the cascade only reaches it if 1 and 2 both fail, so
setting `MNV_LAUNCHER_DIR` at submission means 0 calls across 50 members × 189 tasks rather than 9,450.
It exists so a run whose export was dropped resolves instead of dying.

**And the distinction between the two externally-supplied paths matters:** *an explicit override that is
wrong is a mistake someone made; an implicit default that is wrong is a trap.*

## 5. WHY EVERY PRIOR VERIFICATION MISSED IT — the transferable part

| harness | `BASH_SOURCE` under it | could it have caught this? |
|---|---|---|
| direct execution | real path | **no** |
| argv probe (`source`s the launcher) | real path | **no** |
| `bash -n` | not evaluated | no |
| 1,828 local tests | no launcher executed | no |
| **one real `sbatch`** | **spool path** | **yes, in 12 s** |

`BEN-452` is *a probe that forces a guard false, so the guard cannot be tested.* **This is the deployment
layer's version: a harness that PRESERVES the assumption under test.** Both make a check unable to fail,
but the second is worse to spot, because the harness looks maximally faithful — it runs the real script,
in the real shell, with real arguments.

**Third instance today of "verified" meaning "verified in the environment that could not falsify it":**
PATH stubs that `conda activate` displaced; a `.githooks/pre-commit` executed directly that gates nothing;
and this. **The pattern is not carelessness — each verification was performed correctly in a venue that
structurally excluded the defect.**

**AND THE PROBE STILL CANNOT VERIFY THE FIX**, for the same reason. So the tests simulate the spool
directly: a script copied to a directory with no library, run with no override and no job id, must exit 2
and name what it tried. The `scontrol` branch is exercised against a **stub written by the same person who
wrote the parser**, and its docstring says so — that is this finding's shape one layer down, labelled
rather than hidden, and it is why the explicit override is primary.

## 6. Scope, and what is NOT claimed

- **The resolver is INLINED in seven launchers** — it is the code that *finds* the library, so it cannot
  live inside it. A test pins all seven copies byte-identical by `sha256` rather than trusting seven hand
  edits.
- **Only the seven hooked leg launchers changed.** The nine fenced ones (`S1`) do not source the member
  library.
- **The `scontrol` parser WAS shipped unverified against real output, labelled as such, and the label
  is now discharged.** The mediator ran the exact one-liner against a real existing job (no new
  submission) and it returned the true script path:
  `Command=/pscratch/.../gate5-data-only-frozen-52df398/nd-unfolding/pet/sbatch_gate5_data_only_target_array.sh`,
  parsed identically, path exists and is ours. **The space-in-path limitation stands** — `tr ' '` splits
  on spaces — and that is a property of the paths rather than of the parser. *Recording the discharge
  rather than deleting the caveat, because "shipped labelled, closed later" is the pattern worth
  imitating and it is invisible if the label just disappears.*
- **A `BEN-027` instance in the verification itself, the mediator's, worth keeping beside the result:**
  its first attempt ran `scontrol show job $J` with an **empty** job id (because
  `squeue -h -u josephrb -t RUNNING` returned nothing), and scontrol defaulted to *another user's* job —
  parsing `/global/u2/n/nquota/src/git/nersc-cron/daily_darshan_summary.sh`. **The parser worked and the
  evidence was a stranger's.** *"The parser works"* would have been a true sentence supported by the wrong
  artifact. Second time this campaign that another user's job has stood in for ours.
- **This does not fix the 279 launchers that hardcode `${REPO}`.** That migration is separate
  (`BEN-483` §4), and the relative-source idiom those launchers would migrate *to* is exactly what this
  row shows to be insufficient on its own — **so anyone doing that migration must carry this cascade, not
  the one-line `_HERE` form.** That is this row's main forward-looking claim.
