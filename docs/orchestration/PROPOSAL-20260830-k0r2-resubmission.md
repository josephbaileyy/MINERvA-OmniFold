# PROPOSAL 2026-08-30 — re-submit the seven k=0 arms with the submitter allowlist declared

**CITABLE FOR:** the measured preconditions in §0, the measured allowlist result in §1, and the
submission shape in §3–§4 as PROPOSED. **NOT CITABLE FOR:** any gate movement; any claim that this
rehearsal's Gate 2 can become PASS; a `PACKET-20260823` correction (`OI-179` defect 1, still open); a
launcher edit; ratification of `PROPOSAL-20260830-forward-only-rehearsal.md` §6's ceilings (`OI-177`,
still open); leg 6; the M(ii) family; or covariance adoption. **Gate 2 remains FAIL and no scalar-5D
covariance is adopted.**

## Authority

Joseph, 2026-08-30, in response to this lane's summary of the `OI-179` filing and a drafted
resubmission: **"do all of it, can you continue on the runs too?"** — read by this lane as
authorizing the correction commit, the push, this document, and **the re-submission set out below**.

**What that wording does NOT reach, and this lane is not treating as authorized:** editing
`PACKET-20260823-round5-f2a-f17a-repair.md` (`OI-179` defect 1), editing any launcher, ratifying
`OI-177`, moving any gate, leg 6, the M(ii) family, or any adoption. The earlier delegation recorded
in `LIVE-STATE.md` covers per-arm compute decisions only where an arm is strictly under 500 GPU-hours
and strictly under 500 CPU-hours; every arm here is far inside that.

**One divergence is created deliberately and is flagged rather than fixed:** §1's corrected
three-entry line is what will actually be exported, while `PACKET:122` still documents the
two-entry line that §1 measures as FAILING. Correcting the packet is Joseph's call and stays open at
`OI-179`. Until it is made, **this document is the operative recipe and the packet is not.**

**RESOLVED 2026-08-30, so the divergence above no longer exists.** Joseph authorized the correction
and `PACKET-20260823-round5-f2a-f17a-repair.md` §3 now carries a marked note giving the three-entry
line, with `:218`'s count corrected. **The two documents agree and the packet may be followed again.**
The packet's transcript was deliberately left byte-unchanged: it was FAITHFUL when run, and it is what
round 1 followed. **The packet never contained an error — `$HOME/bin` entered the login `PATH` when
that directory was created on 2026-08-26, three days after the packet, via `/etc/profile:171`, which
adds it conditionally on the directory EXISTING. No file this campaign tracks or pins was edited.**

## 0. What changed since the failed submission, and what did not

| property | at submission 15:46Z | measured now (~16:5xZ) | consequence |
|---|---|---|---|
| canonical HEAD | `32e403b8` | `32e403b8` | unchanged |
| canonical porcelain | 726 | **726** | unchanged |
| canonical status digest | `d429f0f3…8146a` | **`d429f0f3daa5efe43519…`** | unchanged |
| `mii/member_k000000` | 0 entries, 0 `.done` | **0 entries, 0 `.done`** | still the clean §4 state |
| deploy tree | frozen detached `7ac0edec` | not re-verified by this lane | assume frozen; verify before submitting |

**So the F-17(a) operands captured at 07:01–07:45Z still describe their subject.** Whether that
satisfies `F-17(a)`'s currency requirement at a *new* `sbatch` time is a **grading judgement, not
this lane's call** — but a fresh capture may be unnecessary rather than mandatory, which is cheaper
than the handoff assumed. **The live risk is not drift that happened; it is drift that is now
permitted:** `CLOSE-20260830-canonical-quiesce-window-k0-7ac0edec.md` released the dashboard lane and
says it "may land the OI-175 fix", which moves porcelain **726 → 725** and would break currency
mid-window. That is what a re-quiesce protects.

## 1. The one substantive change: declare the allowlist

This is the entire fix. **No file in the repository changes.**

```bash
export MNV_ENV_SYSTEM_PREFIXES="/usr /bin /sbin /lib /lib64 /etc /opt /global/common/software \
$HOME/.local/bin $HOME/.nvm $HOME/bin"
```

**Measured, not proposed on paper.** Both arms run against the DEPLOYED
`k0r2/clean/nd-unfolding/lib_mnv_env_pathcheck.sh` with the real login PATH:

- `PACKET-20260823:122` **as documented** (two home entries) → **rc 3**, one `VIOLATION`,
  `/global/homes/j/josephrb/bin`. **The documented recipe still fails.**
- The **three-entry** line above → `[env-pathcheck] OK: 37 search-path entr(ies) checked`.

**Limitation, stated rather than hidden:** both arms ran the guard **without activation**, so 37 is
the login PATH. After activation there are additional entries under the env root and conda prefix,
which branch (b) allows via `MNV_ENV_ROOT` / `MNV_CONDA_PREFIX` rather than via this list. The
in-job proof is §3's control, not this one.

**Residual risk this widening accepts, and it is the risk the guard was written to name:**
`lib_mnv_env_pathcheck.sh:37` says "A user `bin` directory can shadow a tool". Declaring
`$HOME/.local/bin` permits shadowing by anything installed there. The mitigations are that the
activator prepends the environment, and that guard (4) at `sbatch_bootstrap_5d_gpu.sh:120` asserts the
active `python3` can run the preflight tools. **If you want the exposure narrower**, the alternative
is to declare nothing and instead set an explicit clean `PATH` at submission via
`--export=ALL,HOME=…,PATH=…`, making the same act visible at the same boundary without granting a
home prefix. That is a launcher edit and triggers the `F-14` / §7.0.7 pin ceremony, so it is more
expensive and is **not** what this draft recommends.

## 2. Preconditions, in order, none of them performed

1. **Re-quiesce the canonical checkout.** The hold is *prose*, "preventive by convention and
   detective by `F-17(a)`" (`FREEZE-20260830:53-55`) — so it is a new FREEZE record plus an explicit
   message to the dashboard lane asking it to hold the OI-175 fix again. It is not mechanical and
   nothing prevents a write.
2. **Re-verify the deploy tree** is still detached at `7ac0edec` with porcelain 0 and read-only modes.
3. **Re-read canonical porcelain and the status digest** immediately before the first `sbatch`, with
   the recipe named (`sha256` of the raw bytes of `git status --porcelain`, default `-unormal`, no
   `--branch`, no `--ignored`) — and decide, or have graded, whether the existing operands suffice
   or a fresh `F-17(a)` capture is required.
4. **Confirm `mii/member_k000000` is still empty**, or the resume guard has something to adopt.

## 3. The submission preamble, corrected

Identical to `RECORD-20260830` §5 with **one added line**. The addition is marked.

```bash
export MNV_CODE_ROOT=/pscratch/sd/j/josephrb/k0r2/clean
export MNV_DATA_ROOT=/pscratch/sd/j/josephrb/MINERvA-OmniFold
export MNV_ENV_ROOT=/pscratch/sd/j/josephrb/k0env
export MNV_CONDA_PREFIX=/global/u2/j/josephrb/.conda/envs/root_6_28
export MNV_GUARD_INVENTORY_DIR=/pscratch/sd/j/josephrb/k0r2/runs/<RUN>/inv
export MNV_SOURCE_MANIFEST=/pscratch/sd/j/josephrb/k0r2/runs/<RUN>/source-manifest.json
export MNV_LAUNCHER_DIR=/pscratch/sd/j/josephrb/k0r2/clean/nd-unfolding
export MNV_EST_SEED_OFFSET=0
export MNV_ENV_SYSTEM_PREFIXES="/usr /bin /sbin /lib /lib64 /etc /opt /global/common/software \
$HOME/.local/bin $HOME/.nvm $HOME/bin"          # <-- THE ONLY ADDITION
```

**Then run `PACKET-20260823:123-127`'s positive control before any `sbatch`** — the launcher preamble
truncated at the `mnv_env_pathcheck` line — and require `[env-pathcheck] OK` **in the job's own
environment**. This is the step whose absence let six tasks reach a compute node to fail in 12
seconds. **It is cheap and it is the whole lesson of this incident.**

**AND RECORD THE ENVIRONMENT THIS TIME.** `OI-179` defect 3: the previous run pinned its tree at five
timestamps and recorded nothing about its environment, so the omission was only provable because §5
happened to list the eight exports.

**AN INSTRUMENT NOW EXISTS FOR THIS, 2026-08-31: `nd-unfolding/mnv_env_provenance.py`.** Round 2's
provenance was written BY HAND, which is exactly as perishable as the allowlist it documents. Use the
tool instead, after the exports and before the first `sbatch`:

```bash
python3 $MNV_CODE_ROOT/nd-unfolding/mnv_env_provenance.py --emit  "$R/submission-environment.json"
# ... and on any later leg, re-submission, or post-mortem:
python3 $MNV_CODE_ROOT/nd-unfolding/mnv_env_provenance.py --check "$R/submission-environment.json"
```

`--check` exits **3** on drift and names what moved, including a GAINED search-path entry — which is
the shape of `OI-179` defect 1, where a `mkdir` put `$HOME/bin` on `PATH` with no edit to any tracked
file. **It compares against the RECORDED BASELINE and refuses (exit 2) if the baseline is absent**,
rather than falling back to comparing the environment with itself; that fallback would always pass and
would read as coverage, which is defect 2's shape.

**✅ ENFORCED 2026-09-01 — the paragraph below is SUPERSEDED and is kept because a reader of the
2026-08-31 records will meet it.** It said: *"this is a separate tool a submitter must remember to
invoke. An emitter inlined into each launcher preamble could not be skipped, but that would edit
eight pinned launchers and trigger the `F-14` / §7.0.7 coupling and `OI-123` supersession. Joseph
chose the new-files shape on 2026-08-31 with that trade-off named. So defect 3 is INSTRUMENTED, not
yet ENFORCED."*

**THE COST IT WAS AVOIDING DOES NOT EXIST, and that was measured rather than argued.** The launchers'
pre-source loop compares each library against **`HEAD`**, not against a hardcoded digest, so a
committed edit keeps it green; `verify_hash_bindings.py` reports `ALL BINDINGS INTACT` with **none of
the eight bound by an active run receipt** (which is precisely what blocks the `OI-123` launchers, and
does not apply here); and each launcher's `--pair` set already includes itself. **No pin is
superseded and no `OI-123` ceremony is triggered.** `F-14` / §7.0.7 still applies exactly as it
applies to any commit — `generate_manifest.py --check` exiting 0 at the graded sha — which is a
condition on this change, not a cost peculiar to it.

**WHAT THE LAUNCHERS NOW DO, in all eight, byte-identically:** `MNV_ENV_PROVENANCE` is **mandatory
with no default** (`:?`, so an exported-but-empty value refuses too); the task **records its own
environment** to `${MNV_GUARD_INVENTORY_DIR}/env-provenance.<job>.<jobid>.<task>.json`; and
`--check-inherited` asserts that `HOME` and every `MNV_*` reached the task intact, propagating **2 for
"could not look"** and **3 for "measured drift"** rather than collapsing them.

**WHY `--check-inherited` AND NOT `--check` INSIDE A LAUNCHER.** The baseline is recorded on a login
node before `sbatch`; the launcher's check necessarily runs **after** the activator, because a compute
node's pre-activation `/usr/bin/python3` is **3.6.15** and this tool needs 3.7+ — both measured
directly in job `57819105` on 2026-09-01, not assumed. Post-activation the search paths legitimately
differ (round 2 saw 47 entries against the submitter's 27), so they are **observed and printed, never
asserted**. A guard that fires on every correct run is not a guard. The same job measured that a
compute node's *pre*-activation environment is byte-identical to the login node's for `HOME`, `PATH`
and `PYTHONPATH` and gains exactly one `LD_LIBRARY_PATH` entry
(`/opt/cray/libfabric/default/lib64`) — which is why the `HOME`/`MNV_*` half is asserted strictly.

**THE SUBMIT-SIDE STEP ABOVE IS STILL REQUIRED AND IS NOW ALSO UNSKIPPABLE** — not because the
submitter is reminded, but because every launcher refuses without the baseline the `--emit` produces.
`--check` remains the submitter's own cross-submission comparison and is the only thing that can catch
defect 1's `mkdir`; the launcher cannot, because that is a login-environment fact.

## 4. The arms

Unchanged from `RECORD-20260830` §5, same order, same two dependencies:

```bash
sbatch --parsable $C/sbatch_bootstrap_5d_gpu.sh                 # arm 1
sbatch --parsable $C/sbatch_seedscan_split_5d.sh                # arm 2
sbatch --parsable $C/sbatch_unfold_5d_detector_bkgaware_gpu.sh  # arm 3
sbatch --parsable $C/sbatch_uthrow_run_5d_fast.sh               # arm 4
sbatch --parsable $C/sbatch_uthrow_block_5d.sh                  # arm 5
sbatch --parsable --dependency=afterok:<arm3> $C/sbatch_sweep_bank_5d_run_bkgaware_gpu.sh  # arm 6
sbatch --parsable --dependency=afterok:<arm4>:<arm5> $C/sbatch_uthrow_combine_5d_fast.sh   # arm 7
```

Two operational notes from the failed attempt, both cheap to honour:

- **Do not truncate the job-id column when reading the queue.** `%.14i` cuts `[1-169%48]` to
  `[1-16`, which misreads an array population by an order of magnitude. Use `%i` unpadded or
  `scontrol show job`.
- **`sacct` prints cluster-local PDT.** A 15:46Z submission reads `08:46`. Read a window query as a
  window, not a population: `sacct -S 08:00 -E now` listed five of the seven arms; arms 6 and 7
  appeared only under an explicit `-j`.

## 5. Open items this does NOT resolve

- **`OI-177` is open and is Joseph's** — §6's per-arm CPU ceilings for arms 2, 5 and 6, which three
  prior actuals exceed by 1.38 CPU task-h in total. A re-submission runs the same arms against the
  same unratified ceilings.
- **`OI-179` defect 1 is REPAIRED 2026-08-30** — see the resolution note under ## Authority. What
  keeps the row open is **defect 3**, not defect 1: environment provenance was recorded for this run
  BY HAND, and no launcher, gate or instrument emits it, so the next run reproduces the gap.
  **CORRECTED 2026-08-30: this bullet said "defects 1 and 2" and that was wrong when written.**
  Defect 2, the missing branch-(b) test arm, was already repaired at `b512760d` — two commits before
  this document existed. This lane wrote a stale sentence about its own completed work, which is the
  cheapest kind of error to make and the easiest to propagate.
- **Gate 2 remains FAIL** on the six clauses at `327bc105`, none of which this touches. Even a
  complete successful run does not turn this rehearsal's Gate 2 into PASS.
- The **quarantine branch gates adoption independently of this run** and nothing today moved it.
  `OI-172` is **OPEN**, is routed to Joseph, and needs **no compute**: its row, re-derived at HEAD
  `32e403b8`, records that cause 1 "has content on all four legs" and that "one routed judgement is
  the only thing left". **The count has TWO numbers and quoting one is the known error.** Committed
  form, verified at `PREDECLARE-20260812-stamped-footing-adoption-candidate.md:60` and
  `CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md:388`: **CAND `1 of 7`, QUOTED `0 of 7`** — one
  footing-matched candidate, and **zero** for the artifact `values.tex` actually quotes.
  `CRITERIA-20260811:42` names the failure explicitly — *"'1 of 7 done' is what obscures that"* — and
  the `OI-172` row says outright **"THIS ROW DECLARES NO DISCHARGE."** So **nothing is discharged**;
  never write a bare "1 of 7", and give both labelled numbers or neither.
