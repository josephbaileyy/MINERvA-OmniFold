
### Uncertainties: Step 0 protected the wrong two-thirds, then Step 1 produced a real number

With `56415634` sitting in the queue, the unblocked half of "central value **and** uncertainties" is the
budget. `PLAN-20260806-niter3-budget-and-J28-reroll.md` already had predeclared decision rules, so this
was execution, not a new decision.

**Step 0 — and I got it wrong the first time.** Protect the throw slabs the J28 re-roll consumes; a
`/pscratch` purge turns a two-minute rescale into a re-throw campaign. First pass protected **365 of
542** files and printed "365 readable, 0 unreadable", which reads as complete. The filter was
`"slab" in filename`, and the entire **block** ensemble is named `block5d_flux_17.npz`,
`blockfps_*.npz`, `block4d_0.npz` — no "slab" in the filename, only in the directory.
`rescale_flux_universes.py` rebuilds `C_blocksum` from exactly those, so a purge would have left Step 1
unrunnable while the manifest asserted the inputs were safe. **Filed BEN-032.** What makes it worth a
finding rather than a shrug: the count of what was checked is not the count of what exists, and nothing
inside the result set could reveal the missing third — the denominator had to come from somewhere else
(`find -name '*slab*'` vs `-path '*slab*'` differ by 49%). Found by asking what Step 1 *consumes*, not
by re-reading Step 0.

Corrected: 548 files / 8.1 GiB (542 slabs + 3 bank `flux_univ_ratio.npy` + 3 `cv.npz`), all readable via
`np.load` with every array materialised, every destination file re-hashed, and the copy re-verified
against the **CFS root** — the restore path — not just the source. The check has power: one flipped byte
yields `*** SLAB SET DIVERGED ***`. Excluded deliberately: the banks' 89 GB of per-universe
`sig_*`/`td_*` arrays, which are re-**throw** inputs, not inputs to this rescale. The plan's own "365"
precondition came from the same filter, so it inherited the gap it was written to close.

**Step 1 — the exact re-roll, job `56417324`, ~2 minutes on one CPU node.** Two blockers resolved en
route: ROOT segfaults under the absolute-path interpreter (cling cannot resolve the conda toolchain's
include paths) so it needs `source setup_salloc_env.sh`; and the adopted ensemble had to be *identified*
rather than guessed — `block_slabs_5d` holds 8 files and `block_slabs_5d_sb` holds 36, and re-rolling
the wrong one yields a confidently wrong number. Two independent sources agree on `_sb`.

    sqrt_tr_flux_block     3.892270e-39 -> 1.622406e-38   +316.83%
    sqrt_tr_blocksum       3.403264e-38 -> 3.750055e-38    +10.19%
    sqrt_tr_unified        4.343878e-38 -> 4.312442e-38     -0.72%
    sqrt_tr_cross          2.699457e-38 -> 2.129377e-38    -21.12%
    joint_mean_shift_norm  1.535143e-38 -> 1.885299e-38    +22.81%
    g_mean mean-centered   1.0565550    -> 1.0295687        -2.55%
    g_mean CV-centered     1.1117482    -> 1.1186232        +0.62%

**The defect was backwards from how it had been framed.** Dividing each universe by `Φ_CV` instead of
its own `Φu` *removes* the normalization spread the flux universes exist to carry, so J28
**understated** the Flux block — by ~4.2× on its sqrt-trace — rather than inflating it. Correcting it
raises the block sum toward a nearly unchanged unified total, which is why the cross term collapses 21%
and `g` falls toward 1.

Both predeclared rules fired, which is the only reason this reads as a result. **Rule 1:** the
first-order "+3–4% upward / ~+6% on the block" estimate is superseded and was **not** confirmed — exact
is +10.19% on the block sum and *down* 0.72% on the unified total. **Rule 2:** the `g` direction is
**convention-dependent** — `mean_shift` grew 22.81%, CV-centering adds `shift²`, so mean-centered
`g_mean` falls 2.55% while CV-centered `g_mean` *rises* 0.62%. "The correction reduces the inflation
factor" is true under one convention and false under the other, and the F7 choice is still open. Rule 3:
`g_max` falling ~23% is one bin out of 10,694 with no interval; `n = 122` throws.

**Adopts nothing.** The quarantine stays in force. And these are the **5-iteration GBDT** slabs, not the
PET lane whose policy moved 2 → 3 — Step 1 was deliberately `niter`-agnostic, so this is complete on its
own terms but does **not** discharge item (d). Landed in all three homes §6 requires plus the plan.

### Step 2: the classification, a sixth J28 site, and a correction I owe on the end-goal question

Fresh-context review before landing, per the 15:22Z standing condition. It corrected **two of my seven
findings**, and both corrections matter more than the classification did.

**Item (d) is misframed for the PET lane.** There is no full-event PET covariance to *recompute* —
`products/pet/fullevent_fps/` holds two non-covariance files, `PET_UQ_PRODUCTION_STATUS.md` contains
**zero** occurrences of "full-event", and no full-event counterpart to any `bkgsub` covariance launcher
exists. The work is a **BUILD**, which item 6 already required.

**Correction 1 — what is being written off is ~3× what I said.** Not "a C_stat plus a pilot" but a
complete assembled budget: C_syst 2.970e-38, C_retrain 2.190e-38, C_stat 7.439e-39, C_ml 8.036e-39,
C_lateral 4.690e-39, C_total 3.878e-38, plus a *newer* 42-replica interim C_stat and six combined ROOTs.
Conclusion unchanged; the inventory in the record was wrong.

**Correction 2 — `niter` IS recorded, and that makes the case stronger.** I had written that the
provenance "was never written down." `sbatch_pet_nominal_bkgsub.sh:42` pins `NITER=2`, `:29` states
`iters = 2`, and `:14` banners **"QUARANTINED RECOIL-ONLY CROSS-CHECK LAUNCHER — NOT a publication
path"**. So those components are disqualified by three *positive* facts — `niter=2`, a non-publication
path, a 10550-bin recoil domain against 10694 — which is exactly what rule 5 asks for, instead of by an
absence. I had committed the wrong version and corrected `KNOWN_ISSUES.md` in place; the real remaining
debt is the missing **stamp**, since none of that is visible from the artifact a reader would open.

**My "transfers" argument was the forbidden form, and I rewrote it.** "Different estimator family,
therefore irrelevant" is a *disjointness assertion* — what I would have written whether or not a hidden
dependency existed. The positive form: the 5D GBDT covariance is a **closed function of an enumerated
input list containing no PET quantity** (`adopt_unified_5d.py:75,78`; `--iters 5` on `bank_uthrow_5d`),
and `NOMINAL_SEED_POLICY['niter']` is read by exactly one driver that writes nothing any 5D GBDT product
reads. Falsifiable by one new dependency, which is the point. The dependency that *does* exist runs the
other way — PET C_syst consumes `bank_uthrow_5d` — so today's re-roll is a **prerequisite** for the PET
build rather than independent of it.

**A sixth J28 site: `eavailW_covariance.py`.** Absent from `081ae4a`'s twelve files and unscoped by the
audit. `:104` loads `flux_bins` once from the CV histogram; `:232` passes it into
`extract_cross_section_nd` on every call with no per-universe override; `_y_band` (`:259`) has no flux
parameter; `:274-276` runs all 100 PPFX universes through it into `C_flux`. The fixed
`unified_throw_cov_5d.py:67` threads `d["flux"] if flux is None else flux` for exactly this reason. So
`C_flux` is understated by the mechanism I measured today. I confirmed it at the mechanism level myself
rather than taking the review's word — but it is a **code read, not run**, so no magnitude.

**The correction I owe on "how far are we."** I told him the full-event PET budget was the main gap to a
cross section plus an uncertainty. **The note quotes no PET covariance at all**:
`\petTotalMedian`/`\petTotalTrace`/`\petFourMedian` are `QUARANTINED` and referenced **0 times** in the
tex tree; only `\petRatio` (2×) and `\petClosure` (3×) are used; `sec_pet.tex:1` titles the section a
cross-**check**; the headline budget is the GBDT 5D lane. So that build buys a precision comparison the
note presently *declines* to make, and whether it is publication-blocking or discretionary is recorded
nowhere. That is a bigger question than the classification, and it is his. Also: **"170–250 GPU-h" is
not verified** — the defensible floor is **≥100 GPU-h** for C_stat alone (one train ~1 h/GPU at
`sbatch_pet_nominal_bkgsub.sh:31`, 100 replicas, full-event at `niter=3` strictly more per train).

### Two corrections to this morning's re-roll, both from reading the product instead of the launcher

Nothing was unblocked this cycle — nominal still PENDING, no reply, Steps 3–5 gated on Joseph — so
instead of idling I went back at the two things I had escalated. Both turned out to be wrong in my
favour and against it respectively.

**1. The re-roll covers 122 of the adopted 160 throws (BEN-033).** I had written, in the finding, the
ledger, the RUN_LOG and a STATUS one-liner, that its inputs were "the ensemble the **adopted**
`unified_throw_cov_5d.root` was built from." The ROOT itself says **`n_throws = 160`**;
job `56417324` processed **122**. `uthrow_slabs_5d_sb/` holds slabs **0–30** and slabs **31–39 are
gone** (~38 throws), lost from purgeable scratch after the combine ran. So the "before" sits **−2.62%**
below the adopted `sqrt_tr_unified` (and −7.21% on the mean shift).

What survives: the before→after comparison uses the *same* 122 slabs on both sides, so it is a
controlled measurement of the correction and the +316.83% / +10.19% / −0.72% figures hold. What does
not: the corrected *absolute* numbers are a 76.2% subsample, **not** drop-in replacements for the
adopted covariance. Exact replacement needs slabs 31–39 re-thrown → `OPEN_ITEMS.md` (g).

The lesson is sharper than the slip. I had *cross-checked two independent sources* — the fast combine's
globs and a STATUS run-F entry — and they agreed. But both were the wrong **kind** of source: a launcher
says what it *would* consume, the product records what it *did*, and they diverge precisely when inputs
have been lost since. Agreement between two same-kind sources bought nothing; one `TFile.Open` +
`Get("n_throws")` would have caught it in seconds. Also worth stating plainly:
`--expected-throws 0-159` resolving to 122 files is a **failed precondition**, not a detail. And Step 0
can only ever protect survivors — it does not mitigate a loss that already happened.

**2. F7 was never an open decision, and I was wrong to escalate it to Joseph as one.**
`CORRECTED_UQ_PRODUCTION_STATUS.md:73-78` predeclared the criterion before the data existed: `~floor` →
mean-centered acceptable; `>> floor` → **also produce the CV-centered variant**, report the shift either
way, **never silently drop it**. Measured on the adopted ensemble:

    ||mean_shift|| = 1.6544e-38   sampling floor sqrt_tr/sqrt(160) = 3.5266e-39   ratio 4.69x
      -> 37.1% of sqrt_tr against a 7.9% floor;  after the correction, 4.83x / 43.7%

That is `>> floor` on any reading, and the 37% is not my interpretation — `:325` recorded exactly that
figure as "NON-negligible, FEED Fable-F7 adopt decision" when the headline landed on 07-13. So
**quoting mean-centered alone is disqualified**, the CV-centered variant must exist, and the operative
`g` change is CV-centered **+0.62%** — the corrected inflation edges slightly **up**. My "g falls toward
1" emphasis described the variant the rule rules out. Only *presentation* (sole headline vs both side by
side) is genuinely his.

Net: one of the two decisions I escalated last cycle answers itself from a rule the repo wrote in
advance. That is the campaign's own standard working — and the reason to re-read the predeclaration
before escalating, not after.

### Cluster access expired mid-cycle — and the durable watch is why that is survivable

Immediately after landing the two corrections above, `ssh` to the cluster began failing with **exit 255
and no stderr**, across `saul`, `perlmutter` and `dtn01` alike — which looks like a NERSC outage and is
not one.

`ssh-keygen -L -f ~/.ssh/nersc-cert.pub` gives it away: the sshproxy certificate was
**`Valid: 2026-08-05T06:07 → 2026-08-06T06:08:08`**. It expired this morning. Everything since then —
the launcher fix, the Step 0 protection, job `56417324`, two mails, several `git pull`s on the cluster —
ran over an **already-authenticated multiplexed master socket**, because `~/.ssh/config` sets
`ControlMaster auto` with `ControlPersist 12h`. When that master hit its persist limit `~/.ssh/cm/`
emptied and the next connection failed instantly. **`ControlPersist` masked an expired credential for
most of a working day.** Filed **BEN-034**.

Renewal needs `sshproxy.sh` with password + MFA, so I cannot do it. Joseph will need to run it —
`! sshproxy.sh -u josephrb` from this session works.

**What is blocked:** cluster propagation (the checkout is 3 commits behind: `5b7b59f`, `60af231`,
`9ee7622`) and **all outbound mail**, since `send_channel_mail.py` runs *on the cluster*. That is the
sharp edge — the same failure takes out the work channel and the channel I would use to report it. I
used `PushNotification` instead, which is local.

**What is not blocked, and this is the point:** the `wakerctl` watch armed two cycles ago is a **Slurm
cron job on the cluster**, so it does not care that my local session lost its credential. When
`56415634` ends, Joseph still gets the verdict mail — artifact digests, the actual `seed_policy`, the
partial-run warning, and the non-quotable notice. I armed it against *session death*; it is now earning
its keep against something I did not anticipate, which is the better argument for the CLAUDE.md rule
than the one I made at the time. A session does not have to die for its comms to.

Local work is unaffected: repo edits, commits and pushes to origin all still work, and everything this
cycle produced is safe on origin.

### He answered both escalations, and asked one back: is the 5D GBDT budget finished?

Mail 20:29:05Z: *"Ideally, the fill [full] event PET uncertainty budget is ready for the publication.
Is the 5d GBDT uncertainties finished?"* Still no ssh (cert expired 06:08), so the reply is **staged,
not sent** — the answer is reproduced here so any later cycle can send it without re-deriving it.

**His answer to my escalation:** the full-event PET budget **is wanted for publication**. Phrased as a
preference, not a hard gate, but the direction is settled — the ≥100 GPU-h build is planned work, not
discretionary. Recorded in `OPEN_ITEMS.md` (d) and the Step 2 classification. Two consequences I flagged
back: the PET macros must be **replaced** by full-event values rather than un-quarantined (the recoil
ones belong to a different estimator on a 10550-bin domain), and because the PET vertical block consumes
`bank_uthrow_5d`, **the J28 re-roll must be adopted before a PET budget is built on it** — which orders
the remaining work.

**My answer: no, the 5D GBDT budget is NOT finished — it is a CANDIDATE.** The ledger says so in its own
heading, `VALIDATION_LEDGER.md:64`: *"corrected 5D GBDT covariance — CANDIDATE; final lateral replacement
pending"*, with `:13-14` *"final adoption waits for the selection-complete lateral"*; `values.tex:56`
agrees. What **is** done is the budget chain — `STATUS:370` records "WORKSTREAM A (budget chain)
COMPLETE: boot5d + ssplit + budget + adopt both (5.80/6.23e-38) + eavailW", and the assembled numbers
exist (13.36%/bin block median, 5.81e-38 adopted, 6.24e-38 CV-centered, 1.65e-38 shift).

Three things stand between that and finished:

1. **Selection-complete five-band active laterals — explicitly "the publication gate"**
   (`OPEN_ITEMS.md:41`). Infrastructure is all committed; I find no adopted product or ledger row, and
   `followup-agent-C-fps-01.md` still frames it as work. *Caveat stated honestly in the reply:* "not
   adopted" is certain, "not produced" is likely but unverified, because I could not check cluster-side
   products this cycle.
2. **The J28 quarantine is still in force** — every scale in that ledger section is NOT QUOTABLE until
   the re-roll is **adopted**. Today's job was the sizing; and it covered 122 of 160 throws.
3. **The (E_avail,W) projected covariance cannot currently be rebuilt** — `eavailW_covariance.py` is the
   sixth J28 site, so it needs the same fix the other five got before `M C_5D M^T` can be projected.

**F7 needs nothing from him, for a second independent reason.** Beyond the predeclared rule already
settling it, **the note already complies**: it quotes `\gbdtFiveAdoptTrace` 5.81e-38 *and*
`\gbdtFiveCVTrace` 6.24e-38 *and* `\gbdtFiveMeanShift` 1.65e-38 separately — precisely "report the shift
either way, do not silently drop". So my escalation was unnecessary twice over. The lesson is the same
one BEN-033 makes: read what the repo already recorded before asking.

### Fixed the sixth J28 site in code — the one thing that was unblocked without a cluster

Still no ssh (cert expired 06:08), so the reply to his 20:29Z mail stays staged and nothing could be
run, submitted or propagated. One item was genuinely unblocked locally and is required rather than
invented work: **the sixth J28 site**, `eavailW_covariance.py`, which item (f) recorded as blocking a
stated deliverable (the `(E_avail,W)` projected covariance).

Two risk checks first, because modifying a covariance builder deserves them. (1) **It is bound by no
receipt or gate** — so the change voids no hash binding and needs no re-issue (verified after:
ALL BINDINGS INTACT). (2) **There is a precedent for landing this without numbers**: `KNOWN_ISSUES`
credits `081ae4a` with "the code fix is committed, fail-closed, and mutation-tested … **no corrected
number exists yet**." Fixing the sixth site on the same footing is consistent with how the first five
landed, not a new standard. And no fresh-context consult was possible — `ask_claude.sh` runs on the
cluster too — so I deliberately kept the change to *applying an already-decided pattern* rather than
choosing a new one.

The fix reuses the helper `081ae4a` already shipped rather than inventing a mechanism: `xsec_ew` and
`_y_band` take a `flux` override, and the flux loop resolves `r[u, b] = Φ_u(b)/Φ_CV(b)` once through
`flux_universe.resolve_flux_ratio_table`. `flux=None` still means CV flux, which is **correct** for the
CV and for every knob band — a knob does not move the flux integral — and wrong only for a flux
universe. Same `d["flux"] if flux is None else flux` shape as `unified_throw_cov_5d.py:67`.

**Fail-closed, deliberately with no silent fallback**, since a silent fallback *is* the bug:
`resolve_flux_ratio_table` refuses when neither a bank nor `--flux-universe-file` is usable, and
`_validate_ratio_table` independently rejects an all-ones table as "the J28/Task #70 bug, not a valid
table". Reproducing the old behaviour now takes an explicit `--allow-cv-flux-universes` that announces it
understates `C_flux`.

Two details I checked rather than assumed. The ratio table is **`r[u, b]` — universe-major** (a
transpose here would have been a silent wrong answer), and `resolve_flux_ratio_table`'s keyword
signature, which I had guessed and then read.

Test: `EavailWFluxBlockIsPerUniverse`, static like the existing `KernelsTakeAFluxOverride` because this
module imports ROOT and reads a 142 GB omnifile. It gets its own class because my override is wrapped in
`np.asarray(...)`, so the shared `_flux_arg` bare-`IfExp` assertion does not apply. **Proved to have
power** — `test_the_prefix_source_would_fail` reconstructs the pre-fix source and requires all three
guards to fire. I also converted the helpers from bare `assert` to unittest assertions: `python -O`
strips the former, which would have made every guard silently vacuous — the exact defect class this
campaign keeps finding.

**Collection: 703 → 708 local (+5), cluster 757 → 762. ANNOUNCED.** Suite 700 passed with the same 7
pre-existing cluster-path failures. **No number was produced** — rebuilding the `(E_avail,W)` covariance
needs the cluster and belongs with the `M C_5D M^T` projection.

### I orphaned a finding the same day the rule against it was written, so it is now checked

Still no ssh, no new mail, nothing cluster-side actionable. One local obligation remained, and it was
mine: `FINDINGS.md`'s index header says **"Every `FINDING-*.md` in this directory must appear here"**, and
CLAUDE.md explains why — *"an unindexed finding is one nobody will read, which is how nine of them sat
orphaned until 2026-08-06."* That file was written **today**, and today I created
`FINDING-20260806-j28-reroll-exact.md` and left it out of the index. Indexed now; all 11 `FINDING-*.md`
files check out in both directions.

Since remembering the rule demonstrably did not work, it is now a guard:
`test_every_longform_finding_is_indexed` and `test_the_index_has_no_dangling_rows` in
`tests/test_hash_bindings.py`. Both **mutation-proved** — dropping my new row fails the first, a row
naming a nonexistent file fails the second.

Two placement decisions worth recording. It lives in `nd-unfolding/tests/` and **not** in
`docs/orchestration/test_*.py`, because per `FINDING-20260802-orchestration-tests-never-run.md` those are
never collected — a guard placed there would itself be the antipattern it exists to prevent.
`test_hash_bindings.py` is the right file: it already guards `docs/orchestration` state invariants from
inside the collected suite. And the row parser reads **table rows only**, because the header prose
legitimately contains the literal `FINDING-*.md` and `FINDING-<YYYYMMDD>-<slug>.md`; scanning the whole
file reports those as index rows pointing at nonexistent files, which I saw on the first pass.

**Collection: 708 → 710 local (+2), cluster 762 → 764. ANNOUNCED.** 702 passed, same 7 pre-existing
cluster-path failures. Verifier ALL BINDINGS INTACT.

### Cert renewal worked; NERSC sessions now hang AFTER authentication (server-side)

Joseph ran `sshproxy.sh`. The credential is genuinely fixed — new cert `Valid: 2026-08-06T17:57:00 →
2026-08-07T17:58:56`, new fingerprint `8G7iAbZJ…` replacing `hNuQuFzU…`, and verbose ssh reports
**`Authenticated to saul.nersc.gov ([128.55.126.10]:22) using "publickey"`**. So BEN-034 is closed as a
*credential* problem.

**A different failure is now in front of it.** Every session hangs immediately after
`debug1: Entering interactive session` — the remote side never returns a byte. Reproduced on
`saul.nersc.gov` and `perlmutter.nersc.gov`, and, decisively, **`sftp` hangs identically**. That last
point matters: sftp uses the SFTP subsystem and never sources shell rc files, so this is **not** a hung
`$HOME` or a slow `.bashrc` — the session itself stalls post-auth, which is server-side and not
something this session can fix.

Two self-inflicted complications cleared along the way, worth recording because they made the picture
look worse than it was. (1) The early hung attempts left **wedged ControlMaster sockets** in `~/.ssh/cm/`
for both hosts, and `ControlMaster auto` then reused them — so config-based connections failed while a
`ControlPath=none` connection authenticated fine. Cleared with `ssh -O exit` per host plus killing the
orphaned clients (PIDs 19520, 20277 had been hanging 9m42s and 2m20s). (2) I filtered a verbose ssh
stream through `grep` into a file and saw **nothing**, because grep block-buffers a pipe — the same
write-time-truncation trap as BEN-026, in a new costume. Redirecting the whole stream and reading the
file showed the answer immediately.

Still queued and still blocked, now on NERSC rather than on the cert: the staged reply to his 20:29Z
mail, a `git pull` on a checkout **7 commits behind**, job state for `56415634`, and rebuilding the
`(E_avail,W)` covariance with the sixth-site fix. The nominal's wakerctl watch is cluster-side, so if the
login nodes are wedged but Slurm and the cron are not, its verdict mail still fires without me.

### CORRECTION: it *is* the home filesystem — a stale NFS handle — and my discriminator was invalid

The entry above concluded "**not** a hung `$HOME` … the session itself stalls post-auth, which is
server-side". The mechanism was wrong. The actual error, once I stopped filtering the stream at write
time and read it whole:

    Could not chdir to home directory /global/homes/j/josephrb: Stale file handle
    bash: /global/homes/j/josephrb/.bashrc: Stale file handle

**My reasoning failed because the discriminator was not one.** I argued "sftp hangs too, and sftp never
sources shell rc files, therefore not home" — but sftp resolves `$HOME` for its initial remote directory,
so a stale home breaks sftp for exactly the same reason. The test could not distinguish the two
hypotheses, which makes it a *vacuous* test in the same family the campaign keeps catching: it would have
returned the same answer whichever hypothesis was true.

Two other things that hid it, both self-inflicted, now **BEN-035**: `rc=$?` after `ssh … | tail -2`
reported `ssh_rc=0` for three hosts that had all hung (that is `tail`'s status on empty input), and
`ssh -v … | grep … > file` showed an empty file because grep block-buffers into a pipe. Each cost a
diagnostic round trip and each briefly asserted the opposite of the truth.

**Where this leaves the cluster: usable, with `$HOME` avoided.** `/pscratch` is healthy, the repo is
readable, and commands run (login04/22/23 all answered). `dtn01` is unreachable. So, working with
`HOME=/pscratch/sd/j/josephrb`:

- **The staged reply to his 20:29Z mail is SENT** — the 5D GBDT answer, with a note that NERSC home needs
  a remount from their side.
- `56415634` is **still PENDING**, 10h14m queued, priority 67871, `Start=Unknown`; no artifacts; the
  `nominal-56415634` watch is still **armed**.
- **`git pull` on the cluster fails** — not a repo problem: git needs the GitHub key from the stale
  `~/.ssh`. Propagating instead by `git bundle` streamed over ssh stdin, which needs no GitHub auth and
  no sftp. The checkout was 7 commits behind.

### Home recovered; two jobs I sized or launched wrong, both re-done

No new mail. `/global/homes/j/josephrb` is **readable again** — the stale handle cleared on NERSC's side,
so the `HOME=/pscratch` workaround is no longer needed. Two things I got wrong were exposed by that:

**The fresh-context consult on the `niter=4` decision was dead, not slow.** Zero `claude` processes and no
answer file, after ~20 minutes of me reporting it as "still running". Cause: I launched it *while* home was
stale, and `ask_claude.sh` sets `ACCOUNT_HOME=/global/homes/j/josephrb/claude-homes/school` — on exactly
the filesystem that was broken. So the one check I flagged as load-bearing (the closure-ceiling argument
behind the `niter=4` answer) never ran. Relaunched at 22:41:13Z now that `ACCOUNT_HOME` resolves. The
lesson is narrow and worth keeping: **when a filesystem is degraded, a background job that reads it fails
silently and "still running" is indistinguishable from "died"** — check for the process, not just for the
absence of output.

**The cluster suite allocation was sized from the local runtime.** I gave `srun` 20 minutes because the
suite takes ~30 s locally; on the cluster it reached only **~47%** before walltime, and the verifier
(which hashes ~1 TiB) never ran at all. The mistake is the same shape as BEN-030 — sizing a wall from a
differently-shaped run — and the fix is the same: measure the thing you are actually sizing. Resubmitted as
**batch** `56427511` (2 h, `shared`, 8 cores) rather than an interactive `srun`, so it also survives this
session rather than dying with it.

`56415634` is still `PENDING` — priority 67891, no start estimate, no artifacts, watch armed. Its queue wait
is now over 10.5 h.

### Regenerating the missing 38 throws — and the launcher that made them was never in git

Joseph: *"Can you do the J28 adoption and regeneration of the missing 38? Keep watching the PET niter=3"*.
Regeneration must come **first**: adopting on 122/160 would adopt the subsample I had already flagged as
not a drop-in replacement.

**Exactly which throws are missing, measured rather than inferred.** Slabs 0–30 hold throws **0–121**;
missing is **122–159**, contiguous, 38 of them. Note "slabs 31–39" understates it by 2, because slab 30 is
*partial* (2 rows, not 4) — which is why I enumerated throw ids from the slab contents (`throws` key)
instead of counting files.

**Regeneration is BIT-REPRODUCIBLE, which changes what this is.** `unified_throw_cov.py:222-223` seeds per
**global** throw index — `gj = throw_offset + j; rng = default_rng(seed + gj)` — so throw 122 depends only
on `--seed 1000` and its index, never on how tasks are packed. The regenerated throws are therefore the
*same* throws the adopted covariance used, with identical `flux_u` draws. This repairs the original
ensemble rather than substituting a statistically-equivalent one, and that distinction is what makes a
later adoption legitimate.

Submitted as **`56427580`, array tasks 30–39** of the existing `sbatch_uthrow_run_5d_fast.sh`, overriding
only `--array` on the command line so the launcher itself stays byte-identical provenance. Task 30 → offset
120 regenerates 120,121 identically *and* completes the partial slab with 122,123; tasks 31–39 → 124–159.
Original tasks cost ~42–54 min at ~30 GB RSS, and all inputs are intact (`cv.npz` 2.94 GB, 373 per-band
files, ratio table). Running within 36 s of submission.

**Two things I got wrong and fixed in the same turn.** (1) I armed the watch with `notify_nominal.sh`, which
reports `pet_fullevent_nominal_weights.npz` — artifacts this array does not produce. It would have fired
and reported them ABSENT, i.e. **invented a failure**, which is worse than no notification. Replaced with
`notify_uthrow_regen.sh`, which reports *throw completeness* — the actual gate for the re-roll — and says
explicitly not to proceed below 160. (2) `git status` on the launcher returned `??`: both
`sbatch_uthrow_run_5d_fast.sh` and `sbatch_uthrow_combine_5d_fast.sh` were **untracked**, existing only on
scratch — despite being the launchers that produced the adopted 160 throws and the adopted
`unified_throw_cov_5d.root`. That is load-bearing provenance on a purgeable filesystem, and losing it is
how the 38 throws became unreproducible in the first place. Both are now committed.

`56415634` (PET niter=3) remains **PENDING**, priority 67891, no artifacts, watch armed — still watching as
asked.
