
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

### The consult came back and dismantled my own load-bearing argument — conclusion survived, reasoning did not

The fresh-context review of the `niter=4` decision (relaunched after it died on the stale mount) returned
**agree: no, for now** — and then took apart the argument I had called decisive. Four corrections landed:

1. **The dilution ceiling is my WEAKEST support, not my strongest, and only `ASSUMED`-grade.**
   `(1-a_b)^k` presumes step 2 resolves cells independently; `omnifold.py:218-220` evaluates the truth
   classifier on **all** `pass_gen` rows, so a smooth learner can transport the injected `f(pT)` from
   high-acceptance cells into low-acceptance ones — and the injection is smooth in pT while the acceptance
   gradient lives on p∥. A well-generalising network could **beat** the ceiling. Measured 0.5469 sitting
   below 0.6332 shows that is not happening at k=3, but that is one run at one k. "Validated as an upper
   bound" was an overstatement, and I have downgraded it.
2. **A model-free version of the same conclusion exists and now carries the decision (§2a).**
   `PREFLIGHT_GAP_FLOOR.json` declares `residual_budget_abs = 0.046854` against a measured residual of
   0.106159, so passing at k=4 needs a **2.266× cut from one iteration**. The best single-iteration factor
   this campaign has ever measured is 1.738 (B1 k=2→3) → k=4 lands at **0.739**. Short of 0.80 on every
   factor we have evidence for, regardless of the ceiling debate.
3. **My k=4 caution had the sign backwards.** The closed form under-predicting at k=4 makes the ideal
   ceiling *optimistic*, so k=4 helps **even less**. Reinforcement, not caution.
4. **BEN-027 violation, mine:** I reported `56415634` as "10h14m queued" across several cycles. Verified
   in-turn: submitted `12:04:38`, queued **3h46m** at 15:50:44 PDT. I had carried over the
   *powered-closure* job's 10h39m wait. The forward requeue cost is what matters and that precedent still
   supports ~10h, so the decision holds — but the sunk cost was a quarter of what I said. A number in a
   report must come from a command run in the same turn, and "carried over from my own earlier message"
   is exactly the failure BEN-027 describes.

Two further fixes it prompted. The Jensen entry is reframed as a **scope mislabel, not a wrong formula**:
the global form is correct for a *scalar* observable, which is precisely what B1's
`structural_floor_worst_case` uses (matching measurement to 1.9%/0.8% at k=2/3) — without that framing
someone would "fix" B1 by analogy and break it. And the provenance note I had **hand-added** to the
acceptance-map product is now **producer-emitted**: the script's own docstring says the product must be
regenerated rather than hand-edited, and my in-place edit had left it unreproducible with a pre-fix
`git_head`. Regenerated on compute — `git_head` now `c39693e`, numbers reproduce (per-cell 0.60947), and
the `inputs_sha256` live pin on the G2 dump is unchanged.

Also worth recording: `56381674` shows `State=FAILED ExitCode=3:0` in `sacct`, which is the driver's own
`return 0 if ok else 3` on a FAIL **verdict**, not a crash — noted next to the recovery number so nobody
discards 0.5469 as junk from a broken run.

**Regeneration `56427580`: all 10 tasks RUNNING at 8:28** (originals took 42–54 min). Throws still show
122–159 missing, as expected — the driver saves atomically at task end. `56415634` still PENDING. The
adoption stays gated on 160 distinct throws.

### The regeneration handed me a free experiment: the J28 rescale is an identity, verified

Regeneration `56427580` is progressing — throws **122 → 137 present, 23 missing**, all 10 tasks RUNNING at
37:38. One correction to what I said last cycle: the slabs are written **incrementally per throw**, not
atomically at task end, so completeness climbs rather than flipping at once. The missing set is interleaved
(`123, 126, 127, 129–131, …`) because each task is partway through its four throws.

**The valuable result this cycle was an accident of the repair.** Array task 30 covers throws 120–123, so it
recomputed throws 120 and 121 **natively** with a driver that divides by each universe's own `Φu` — while
`uq_5d/rescaled_20260806/` already held the **post-hoc rescaled** version of those same two throws from this
morning. That makes the J28 identity testable against an independent computation for the first time. Across
all **10,694** reported bins:

    throw 120 (flux_u=5  in both forms):  max |rel diff| 1.377e-12,  median 3.952e-14
    throw 121 (flux_u=13 in both forms):  max |rel diff| 6.708e-12,  median 8.393e-13

Agreement at floating-point noise. This matters more than it looks: the entire J28 remediation, and any lift
of the ledger quarantine, rests on `rescale_flux_universes.py`'s claim that `x/r_u` is an *identity* rather
than an approximation, and that claim had never been checked against anything but its own derivation. It is
now verified on production throws — so the rescaled numbers are not an approximation of the right answer,
they **are** it, which is what makes replacing the quarantined scales legitimate rather than a substitution.
Recorded in the ledger; re-runnable as `nd-unfolding/validate_rescale_identity.py`.

A second thing fell out for free: the **flux universes match** (5 and 13 in both forms). That confirms
*empirically* what I had previously only read off `unified_throw_cov.py:222-223` — the RNG is seeded per
global throw index, so regeneration reproduces the original draws rather than statistically similar ones.

**And a sequencing trap I would have walked into.** The repaired ensemble has **mixed provenance**:
`unified_throw_cov.py:255` stamps `flux_normalized=1` on newly-written throws, so slabs 30–39 are *already*
corrected, while 0–29 are unstamped pre-J28. Rescaling uniformly would double-correct the new ones.
`rescale_flux_universes.py:261` fails closed on a stamped slab and `--combine` refuses unstamped ones, so
both mistakes are caught rather than silently wrong — good design — but the adoption recipe is now written
down as **`rescaled(0–29) ∪ new(30–39)`** (plan §2b) so the pass is right first time.

**Cluster suite finished: 763 passed, 1 failed, 764 collected** — matching the 764 I announced. The single
failure is `test_uq_remediation.py::UnifiedThrowTests::test_synthetic_slab_and_block_combine_end_to_end`,
exactly the known J28-fixture failure plan Step 4 describes (its flux guard rejects its own synthetic fixture
for lacking a stamp), and Step 4 deliberately defers it until after the budget rebuild. The verifier half of
that job is still running (it hashes ~1 TiB). Note the brief's expectation of "exactly 8 mismatches from
`p3f-pet-gate4-launch-code-gate-20260801b.json`" is **stale** — that gate has since been re-issued and both
trees now report ALL BINDINGS INTACT.

`56415634` (PET niter=3): PENDING, queued **4h15m** as computed in-turn, watch armed. Still watching.

### Adoption chain submitted on a dependency; and an empty `squeue` that wasn't

**A scare that was my own instrumentation.** A status query returned an empty `squeue` *and* an empty
`sacct`, which reads as "every job vanished, including the nominal". Re-run with stderr captured instead of
discarded: `squeue` returns 11 lines and `rc=0`, the controller is fine, and the nominal is still `PENDING`.
The earlier query had `2>/dev/null`, so a transient `squeue` failure was indistinguishable from "no jobs" —
BEN-035's family again, where the discarded channel is the one that explains the result. Worth stating the
general form: **for a query whose empty output would be alarming, never discard stderr.**

**Regeneration `56427580` is nearly done:** 4 tasks COMPLETED at exit `0:0` (30, 31, 33, 37), 6 still running
at 1:10, and **155 of 160 throws present**. The 5 remaining — 139, 143, 147, 155, 159 — are each the *last*
throw of their task, so they land together.

**The adoption is submitted as `56429334` with `--dependency=afterok:56427580`**, which is better than
polling: Slurm starts it the moment the array succeeds, it will not start if the array fails, and it does not
depend on this session surviving. `nd-unfolding/sbatch_j28_adopt_5d.sh` does, in order: a **fail-closed gate**
that aborts unless all 160 throws are present *and* the stamp split is exactly unstamped 0–29 / stamped
30–39; rescale of the pre-J28 half only (staged by symlink so the split is explicit); a union of
`rescaled(0–29) ∪ native(30–39)`; the combine at `--expected-throws 0-159`; and adopt in **both** mean-shift
conventions.

**One destructive default caught before submitting.** `adopt_unified_5d.py:79-80` defaults `--out` to
`uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root` and opens it `RECREATE` (`:158`).
Taking the default would have (a) **overwritten the existing July adopted product** — quarantined, but still
the historical artifact the ledger describes, 892 MB, verified present — and (b) let the CV-centered run
silently clobber the mean-centered one, leaving a single file that looked like both. Both adopt calls now pass
explicit tagged `--out` paths, and the job prints a check that the July product is untouched.

**The adoption adopts nothing into the ledger, by design.** It writes its own ROOT and prints both variants;
replacing a quarantined number stays a separate human-reviewed commit (plan Step 5).

Also landed: `docs/orchestration/notify_job_log.sh`, a **generic** notifier (job state + its own log tail,
firing on every terminal state). Three notifiers in, the job-specific pattern had already produced one wrong
watch this session, and for a job whose product *is* its printed output the log tail is the whole payload.
Three watches now armed: nominal, regen array, adoption.

**Cluster verification complete:** verifier **ALL BINDINGS INTACT**, suite **763 passed / 1 failed / 764
collected**, the single failure being the known J28 fixture (`test_uq_remediation.py`) that plan Step 4
defers on purpose.

### The ensemble is whole again: 160/160, and the adoption chain fired on its own

**Regeneration `56427580` COMPLETE** — all 10 tasks `COMPLETED` at exit `0:0`, elapsed 45m41s to 1h25m47s.
`scan_slabs.py` now reports **160 distinct throw ids, 0 missing**. The 38 throws lost to a scratch purge are
back, and because `unified_throw_cov.py:222-223` seeds per global throw index they are the *same* draws the
adopted covariance used — verified earlier by the matching `flux_u` values, not assumed.

**The `--dependency=afterok:56427580` chain fired without me.** `56429334` started on its own and is
running. Three things it confirms, each of which could have gone wrong:

- **The fail-closed gate passed and validated my prediction exactly**: `[gate] 160/160 throws present;
  unstamped 0-29, stamped 30-39 -- split as expected`. The mixed-provenance split I derived from
  `unified_throw_cov.py:255` was right, so the adoption is operating on the ensemble I thought it was.
- **Only the pre-J28 half was rescaled** — `[stage] 30 pre-J28 throw slabs staged`, `throws=120 corrected
  rows=120`. The 40 natively-corrected throws were left alone, avoiding the double-correction.
- **The union is 40 slabs**, and it is now inside the combine (`[bank] 12 knob bands, 100 flux universes,
  32849103 events`), which is the expensive step.

**Do not read the rescale block in that log as the final answer.** It reports the **120-throw pre-fix half**
(`sqrt_tr_unified` −1.00%, `blocksum` +10.19%, `flux_block` +316.83%, `mean_shift` +24.45%, `g_mean` −2.69%),
not the corrected 160-throw ensemble. The full-160 numbers come out of the combine and the two adopt runs.
Worth noting the block-unit figures (+10.19%, +316.83%) are **identical** to the 122-throw pass, which is
expected and a small consistency check: the 36 block slabs are the same files either way, since block units
do not depend on the throw count.

**The durable notification worked end to end.** `uthrow-regen-56427580b` shows `fired`, so the throw-
completeness mail went out from a Slurm cron job rather than from this session — the property that mattered
when my ssh certificate expired earlier today. The superseded watch (`...-56427580`, armed with the wrong
notifier) correctly shows `disarmed`. `j28-adopt-56429334` and `nominal-56415634` remain armed.

stderr on the adoption is benign — sklearn `X does not have valid feature names` warnings from LightGBM.

`56415634` (PET niter=3): still PENDING. `b1nit5a` RUNNING at 1:15, `b1nit5b` queued — the concurrent
session's k=5 bookkeeping arms.

### J28 adopted on 160/160 — the corrected total is ~9% SMALLER, and the mechanism explains why

**The PET nominal `56415634` is RUNNING** — started 17:27:05 after ~5h20m queued, healthy by CPU time and
artifacts rather than log growth (AveCPU 00:24:44 tracking elapsed, `w_nominal/` created 17:35). Watch armed.

**Adoption `56429334` COMPLETE** (31m23s, rc=0) on the repaired ensemble. Its fail-closed gate confirmed the
mixed-provenance split verbatim before doing any work, so only the pre-J28 half was rescaled. The corrected
ROOT reads back `n_throws = 160`.

    full-160, like-for-like (the 122/160 morning pass could not give this)
    sqrt_tr_unified        4.4607819710748654e-38 -> 4.443673650575504e-38    -0.38%
    joint_mean_shift_norm  1.654393237996853e-38  -> 1.878696733368378e-38   +13.6%

    adopted            old          new        factor   median frac/bin   bins g>1
    mean-centered   4.3455e-38   5.2600e-38   x1.210   13.43% -> 13.61%   2805 (26.2%), median 1.000
    CV-centered     4.3455e-38   5.6609e-38   x1.303   13.43% -> 14.09%   6526 (61.0%), median 1.047

**The corrected totals are ~9% SMALLER than the quoted 5.81e-38 / 6.24e-38 — and that is the same fact as the
Flux block growing 4.2×, not a contradiction of it.** Correcting the flux raised the block-sum toward a nearly
unchanged unified total, which drove the nonlinearity inflation `g` down toward 1. Since the adopted
covariance is `lateral+stat+ML + G C_vert G`, a smaller `G` inflates the vertical block less. The old value
was overstated *because* the understated Flux block had inflated `g`.

Recorded in all three canonical homes with the quarantine notice **retained and the numbers replaced**, which
is the only sanctioned way to lift it. `values.tex` deliberately untouched: the section still reads
"CANDIDATE; final lateral replacement pending", and that is a publication decision.

**The concurrent laterals session corrected how far off that is, and it is much closer than the prose said.**
Their BEN-036: "full five-band coverage remains the publication gate" reads as a 120-task ~700 GB campaign,
but that campaign is **already complete on disk** (120/120 P3F and P3S, ten 74.8 GB omnifiles, receipt
re-verified). The real blocker is a **footing** mismatch — the FPS endpoint unfolds ran `--bkg-mode=purity`
against a `negweight-refined` publication footing — fixable by re-running only the unfolds, ~3h, reusing all
748 GB. Folded into my ledger entry, because it changes the answer to "when can `values.tex` move?" from
*a campaign* to *hours*.

**A rebase conflict, and my confirmation check failed a third time.** The laterals session and I both appended
to `ND_OMNIFOLD_RUN_LOG.md` and `CORRECTED_UQ_PRODUCTION_STATUS.md`; resolved by keeping **both** sides,
theirs first so the files stay chronological. The instructive part: my
`[ HEAD = origin/main ] && echo PUSH CONFIRMED` printed CONFIRMED **while the push was rejected and my commit
sat unapplied in the conflicted rebase** — because a conflicted rebase checks `HEAD` out at the upstream, so
the hashes are equal exactly in the failure case. The check was anti-correlated with success. Amended onto
**BEN-035** with the general rule: before trusting a check, ask what it prints when the thing fails. The
working form asserts three things — no rebase in progress, the commit reachable from `origin/main`, and
`HEAD == origin/main`.

### Nominal projected safe; and the local/cluster collection gap was not environmental

**`56415634` is healthy and I can now project it.** The per-iteration weight files are the progress
indicator, not the log (which is block-buffered and frozen at 17:28 — BEN-028 exactly): `iter0_step1` at
18:02, `iter0_step2` at 18:18, so **iteration 0 took ~50 min**. At `niter=3` that is ~2.5 h per training and
~5 h for the nominal plus the matched floor repeat, against a **12 h wall** — comfortable, and the earlier
walltime raise from 8 h to 12 h is vindicated. GPU 50% / 8647 MiB confirms it independently. Its stderr is
entirely benign TF startup noise, and the persisted policy reads `niter: 3, epochs: 8, batch_size: 512,
estimator_seed: 42` — the pinned values. Note the 0-byte growth I measured over 60 s is *not* a stall; weights
are written at the end of each step, so flat periods between writes are expected.

**Plan Step 4 resolved: fixture-stale, not guard-over-strict.** The cluster suite's single failure
(`test_uq_remediation.py::…test_synthetic_slab_and_block_combine_end_to_end`) reproduces **locally** too, and
its cause is that the fixture writes synthetic slabs with no `flux_normalized` stamp while `081ae4a` correctly
made `--combine` refuse unstamped slabs. A fixture built in-test has no flux normalisation to get wrong —
there is no `Φ_CV` division to correct — so it is normalised by construction and the stamp states that.
Stamping loses **no** coverage: the rejection behaviour is separately asserted by
`CombineRefusesUnstampedSlabs::test_predicate_accepts_only_a_stamped_slab`, which I re-ran and confirmed still
passes. The guard stays fail-closed, which is its whole purpose.

**And the reason that test was invisible locally is worse than the test itself.** The cluster collected 764
against local 710, and I had been treating that gap as path-dependent skips. Part of it was not:
**two test files existed only on `/pscratch`, in neither tree's git** —
`test_uq_remediation.py` (20 tests, including the only cluster failure) and `test_cstat_100rep.py` (5 tests).
So 25 tests enforcing campaign invariants were one purge from vanishing, and a fresh clone silently ran 25
fewer checks than the cluster did. Same failure as the 38 lost throws and the two untracked launchers: a
purgeable filesystem holding load-bearing artifacts nothing in git records. **Rule worth keeping: when local
and cluster collection counts disagree, resolve the difference to specific files before assuming it is
environmental.**

`test_uq_remediation.py` is now tracked with the fixture fixed. `test_cstat_100rep.py` is deliberately **not**
committed — it imports `combine_cstat_bkgsub_100rep`, which is untracked on the cluster too, so committing the
test alone would guarantee a *collection error* (`ModuleNotFoundError` interrupts the whole run, strictly worse
than a failing test) and committing both would import unreviewed code into the tracked tree. Recorded in
`KNOWN_ISSUES.md` as a decision for Joseph rather than resolved unilaterally.

**Collection: 710 → 730 local (+20), 722 passed with the same 7 pre-existing cluster-path failures.
ANNOUNCED.** Cluster stays 764 but its single failure becomes a pass, so the cluster suite should now be
fully green for the first time in this campaign. Verifier ALL BINDINGS INTACT.

### Quiet cycle: nominal on track, per-step timing refined, nothing in my lane unblocked

No new mail. `56415634` at 1:22:46, and the per-step timing is now measurable from the weight files rather
than estimated from one iteration:

    iter0_step1  17:28 -> 18:02   ~34 min   (includes XLA compile + 5.34M-row shuffle-buffer fill)
    iter0_step2        -> 18:26   ~24 min
    iter1_step1        -> 18:43   ~17 min

Steps are **accelerating** as the cold-start cost amortises, so my earlier "~50 min/iteration" was an
overestimate drawn from the most expensive iteration. Three steps remain in the nominal (~55 min), then the
matched floor repeat with no cold start — call it ~4 h more against a wall expiring 12:27Z. Wide margin.

Concurrent sessions are healthy and following the pattern: the laterals array `56430128` is down to task 9 and
they have armed their own durable watch (`fps-negweight-unfolds-56430128`); `d2_suite` and `b1nit5a` have both
finished. I am deliberately not reading their products — the k=5 arm's reading was predeclared and does not
reopen the `niter` decision, and the laterals are theirs to report.

**Nothing in my lane is unblocked**, so this cycle is verification only rather than invented work. Step 4
landed last cycle; Step 3 is moot for the GBDT lane (it transfers, on the positive closed-input argument) and
needs the PET budget build for the PET lane; Step 5 — replacing the `values.tex` macros — is gated on the
five-band footing fix now in flight. The two open decisions remain Joseph's: whether
`combine_cstat_bkgsub_100rep.py` should be tracked or its 5 tests retired, and the `g` presentation.

### CORRECTION to last cycle: I read in-progress mtimes as completions

Last cycle I reported the nominal's steps "accelerating — 34 → 24 → 17 min" and projected ~4 h remaining.
**That was wrong, and the error is worth naming.** I read `iter1_step1` at mtime 18:43 as a *completed* step;
it was still being written and did not finish until **19:05**. A weights file's mtime while training is in
progress is the last checkpoint flush, not the step boundary. The real cadence, taken from consecutive
`step2` completions which *are* boundaries:

    training start           17:28
    iter0 complete (step2)   18:26    58 min  (includes XLA compile + 5.34M-row shuffle-buffer fill)
    iter1 complete (step2)   19:16    50 min

So iterations run ~50 min steadily; they are not accelerating. Corrected projection: iter2 finishes ~20:06,
ending the nominal training at ~2 h 38 m; the matched floor repeat then takes ~2.5 h, landing ~22:36 PDT
(05:36Z) against a wall expiring **12:27Z**. Still a ~6.9 h margin, so the conclusion ("comfortable") survives
even though the arithmetic behind it did not.

The general form, which is the reusable part: **an mtime tells you when a file was last touched, not that the
producer is done with it.** To measure a stage boundary, use the artifact whose write *is* the boundary
(here `step2`, since a new `step1` cannot start until the iteration closes), or a marker the producer writes
on completion. This is the same family as BEN-035 — a measurement that cannot distinguish "finished" from
"still going" was reported as if it could.

Both concurrent sessions are visibly active: three `pwcprobe` jobs queued (`56431649/50/51` — the D2
under-fitting probes, which is exactly the §4 handover), `fpsActLa` (`56431823`) and `d2_suite` (`56431780`)
running, and the k=5 32-seed arm `b1nit5b` has started. Nothing in my lane changed; no mail (nothing finished).

### Decision: stop timing this job by mtime — count iterations instead

`56415634` is at 2:22:57 and has reached **iteration 2 of 3** (`iter2_step1` present), so the nominal training
is about two-thirds done with the floor repeat to follow. That sits well inside the 12 h wall.

I am dropping the mtime-based timing entirely, because it misled me twice in two cycles. Last cycle I
corrected "steps are accelerating" after finding `iter1_step1` had still been growing when I read it. This
cycle `iter1_step2` moved **19:16 → 19:27** on its own, so the refinement I substituted — "`step2` completions
are the real boundaries" — is *also* unsound: Keras keeps touching a step's weights file until the step truly
ends, and mtime cannot distinguish "last checkpoint flush" from "done". Even inferring a boundary from the
*next* step's appearance fails, because that file's mtime creeps too, so it dates the last write rather than
the creation.

**The decision: report the coarse, robust quantity (which iteration is present, against elapsed and wall) and
stop deriving per-step minutes from filesystem timestamps.** A projection built on an unreliable instrument is
worse than a coarse one, because it carries false precision — and I published false precision twice. If this
job ever genuinely needs per-step timing, the right fix is a producer-written completion marker, not sharper
forensics on mtimes.

Concurrent sessions active and on task: `pwcprobe` `56431649`/`56431650` running with `56431651` queued (the D2
under-fitting probes), `fpsActLa` `56431823` and `d2_suite` `56431780` running, `b1nit5b` at 31:53. Nothing in
my lane changed; nothing finished; no mail.

### The cluster suite is fully green — 764 passed, 0 failed — and a Slurm blip that stderr caught

**Verified, not inferred:** `/pscratch/sd/j/josephrb/d2_suite_AFTER_56431780.log` ends
`764 passed in 2027.67s (0:33:47)` with `pytest rc=0`. The BEFORE run from the same session
(`d2_suite_BEFORE_56430155.log`) reads `763 passed / 1 failed`. So the Step 4 fixture fix landed exactly as
predicted, and **the cluster suite is fully green for the first time in this campaign.** The single failure it
carried was the J28 synthetic-slab stamp, and the fix stamped the fixture rather than weakening the guard —
the guard's rejection behaviour was separately re-verified still passing.

**A Slurm controller outage, and the stderr practice paid for itself.** A status query returned
`slurm_load_jobs error: Unable to contact slurm controller (connect failure)` — on stderr. Had I used
`2>/dev/null`, as I did before this cycle's habit, I would have seen an empty `squeue` and concluded every job
had vanished, which is precisely the false alarm I raised two cycles ago. Instead the failure named itself.
It was transient: the controller came back within the same turn, `sinfo` confirms partitions up, and all jobs
are intact. **Keeping stderr on a query whose empty output would be alarming is now twice-vindicated.**

`56415634` at 2:59:21 has **all six step files** (`iter0`–`iter2` × `step1`/`step2`), so the three OmniFold
iterations are complete. No `.npz` and no `w_floor` yet, which is expected rather than concerning: the
launcher runs `--reweight-all`, so the push weights are evaluated over the **full 32.8M-row generator cloud**
after the iterations, and that pass precedes the artifact write. Per my own decision last cycle I am reporting
the iteration count and phase, not deriving minutes from mtimes.

Concurrent sessions: `pwcprobe` `56431649` (57:14) and `56431650` (40:18) running, `56431651` queued — the
epochs 8/16/32 ladder, each with its own armed watch, so Session A can be closed without losing them. The
laterals session has moved from `fpsActLatCha` to `suiteAct`. Holding mail until the nominal lands rather than
sending twice in quick succession.

### The central value EXISTS — and fails the Gate-4 normalization gate by 6.7×

`56415634` completed its three OmniFold iterations, wrote
`pet_fullevent_nominal_weights.npz` (10,110,334 bytes, 20:26), and moved to the matched GPU-floor repeat at
03:26:50Z. **So the first full-event PET central value exists.** Its footing is entirely correct — verified
from the artifact *and* the driver's own log, not inferred: `niter=3`, epochs 8, `estimator_seed 42`,
`train_events 2,000,000`, `batch_size 512`; `bkg_mode negweight-refined` (the publication footing, not the
forbidden purity); fingerprint `pet-fullevent-fps-v1`; `inputs_sha256 fa6b3463…` matching the Gate-2 pin;
target `544b2f6a…` with receipt PASS; `step1_class_ratio` **exactly** Gate-2's R; `cap_saturation_frac 0.0`;
259 of 285 cells reported, all finite; and val losses falling cleanly (step1 0.192→0.129→0.111, step2
0.961→0.831→0.759).

**But its normalization gate fails decisively.** Quoting the driver's own printed self-report rather than my
recomputation — they agree to all digits:

    "fold_forward_reco_ratio": 0.7464834064182863
    "step1_class_ratio_R":     1.1240802949941018

Applying `validate_pet_nominal_gate4.check_fold_forward_ratio` as written:

    dev = |ratio/R - 1| = 0.335916   vs tolerance 0.05   -> FAIL, 6.7x over
    parameter-free: |ratio-R| = 0.3776  vs  |ratio-1| = 0.2535
        -> lands NEARER 1.0 THAN R -> FAIL

The second check is the one that docstring calls *"precisely the broken-vs-corrected discriminator"*, and it
carries the power claim with no invented threshold. It fails too, so this does not hinge on the tolerance.

**Ruled out, each checked rather than assumed:**

- **Not acceptance dilution.** The docstring's closed form `push_k = R − (1−a)^k (R−1)` predicts ratio
  **1.0997** at k=3 (a=0.4186, R=1.1241). Observed 0.7465 is **32.1% below** that — finite-iteration
  smoothing does not come close to explaining it.
- **Not the classic step-1 defect**, whose signature is the class ratio forced to 1; ours is exactly R.
- **Not cap saturation** (`0.0` against a logit cap of 30).
- **Not a partial run** — three iterations completed, artifact written atomically, job advanced to the floor.

The push weights are simply systematically small: mean **0.8954** over the 2M subsample and **0.7465**
weighted over `pass_reco`, where the identity requires 1.1241.

**Thresholds untouched and I will not touch them.** Nor am I claiming the gate is mis-specified: unlike the
D2 recovery bar, this one is a normalization *identity* — fold the unfolded truth back through acceptance and
it must reproduce the background-subtracted data yield — so a 34% miss is a real discrepancy, not a threshold
quibble. Context worth recording without using it as an excuse: the 0.05 tolerance was measured on the B1
**scalar rate** closure on the **recoil** lane, and CLM-010's "scalar scope only" caveat already proved
load-bearing today when the D2 differential test failed. Whether it transfers to a full-event differential
lane is now genuinely in question — but the identity argument does not depend on the tolerance at all.

**The free next discriminator is already running.** The matched floor repeat uses the same seeds and config,
so it isolates GPU-nondeterminism: if it also returns ~0.7465 the cause is structural, if it moves the cause
is variance. ~3h, no extra cost, watch armed. Mailed as URGENT.

Gate-4 stays red regardless — it was already blocked by D2 — so the NON-QUOTABLE status is unchanged. What is
new is that the central value now has a *second, independent* problem.

### The fold-forward failure is REAL — and I falsely exonerated step 1

**The independent recomputation agrees with the driver to 1.4e-12**, against an independence tolerance of
1e-6. Run on compute with `validate_pet_nominal_gate4.fold_forward_sums_from_dump`, which re-reads `w_reco`
and `pass_reco` from the G2 dump and re-derives R itself, using only the driver's `weights_push` as the object
under test:

    driver       sum_w_push 746483.427515 / sum_w 1000000.028261 -> ratio 0.7464834064182863
    independent  sum_w_push 510280.391480 / sum_w  683579.014740 -> ratio 0.7464834064193590
    R (from dump)                                                    1.1240802949941018
    n_pass_reco  837671 on both sides

The absolute sums differ because the driver's arrays were rescaled in place by the DataLoader while the
independent side reads raw dump weights — exactly what that function's docstring predicts — and the **ratio**
is identical to 12 digits. So the driver's bookkeeping is exonerated and **the estimator's folded-forward
normalization really is off by a third.** Both checks fail on both sides (dev 0.335916 vs tol 0.05; and
nearer-1.0-than-R).

**And that result exposed a false claim I had already given Joseph.** I reported "not the classic step-1
defect — that signature is the class ratio forced to 1, and ours is exactly R." **Invalid.**
`train_fullevent_nominal.py:464` copies `step1_class_ratio` out of the loader's *target metadata* and `:505`
stores it verbatim; `step1_class_ratio_from_dump` derives R from the dump's data/MC yields. The field is the
**target R re-stored**, so it cannot disagree with R and carries **zero** information about what step 1
achieved. The agreement I cited as evidence was a tautology — and it pointed away from what is now the
**leading** hypothesis, since the historical step-1 defect drives the effective ratio toward 1 and a
folded-forward 0.7465 against a required 1.1241 is the right direction for it.

Filed as **BEN-039** and in `KNOWN_ISSUES.md`. The general form: before citing a stored field as evidence,
find where the producer sets it — *a value copied from an input can only confirm the input*. And be suspicious
of any field whose name describes an outcome while sitting beside genuine measurements: ask what it would read
if the thing had gone wrong, and if the answer is "the same", it is not a measurement. Same defect class as a
check that cannot fail (BEN-035), except here the *datum* was incapable of disagreeing rather than the
assertion.

**What is now actually ruled out, and what is not.** Still ruled out: acceptance dilution (predicts 1.0997 at
k=3, observed is 32.1% below), cap saturation (0.0), a partial run, and driver bookkeeping (this cycle).
**No longer ruled out: step-1 under-achievement**, which is testable but needs measuring rather than reading —
run inference with the saved `w_nominal/*_step1.weights.h5` and compare the classifier's reco-space mean
against R. Nothing currently stored supports that comparison, which is itself the telemetry gap BEN-039
records. Thresholds untouched throughout.

### Anatomy of the missing third: a heavy low tail, not a scale error — and my pinning test was wrong

Ran a numpy-only anatomy of `weights_push` split by `pass_reco` (no inference, no GPU contention — three
jobs already hold GPUs, and reconstructing step-1 inference would need the PET net, the exact training-time
normalisation and TF 2.15, where a mistake yields a *plausible wrong number* on the headline problem).

**First, a correction to my own diagnostic.** It reported `*** PINNING DID NOT HOLD ***` because 0 of
1,162,329 off-acceptance rows were exactly 1.0. **That expectation was wrong.** `weights_push` is cumulative —
`weights_push = weights_push * new_weights` *retains* the prior push off-acceptance (the validator's own
docstring says exactly this), so what `omnifold.py` pins to 1 is step 2's `new_weights`, not the accumulated
product. Off-acceptance pushes are in fact tightly near 1 (median **1.0428**, mean 0.9943, p25 1.0031,
p75 1.0630), which is consistent with the pinning working. I asked the wrong question and the script answered
it faithfully; the verdict line is retracted.

**The real structure, on `pass_reco`:** median push **0.9186** — near 1 — with a heavy low tail.

    band      rows     reco weight carried   mean push
    <0.5     24.38%          25.86%           0.2254
    0.5-1.0  48.63%          48.47%           0.8632
    1.0-R    25.93%          24.12%           1.0338
    >R        1.06%           1.55%           1.4544

So the deficit is **localised, not a global scale factor**: a quarter of the reco weight is being downweighted
by ~4.4x. Removing just that tail's effect would lift the weighted mean from 0.7465 to roughly 0.95 — still
short of R = 1.1241, but a different problem. And strikingly, only **1.06%** of rows exceed R at all, when the
identity requires the *weighted average* to be 1.124: essentially nothing is being pushed **up**.

**What this does and does not say.** It does not identify the cause, and I am not going to guess between step 1
and step 2 from these numbers. What it does establish, cheaply and without inference: the failure is a
subpopulation being strongly suppressed plus a bulk sitting just below 1, rather than a uniform mis-scaling —
which is evidence *against* a simple normalisation or sign error and *for* something structure-dependent. The
next real test remains measuring step-1 achievement by inference with the saved
`w_nominal/*_step1.weights.h5`, which needs a GPU the floor repeat and two probe arms are currently using.

Status unchanged otherwise: nominal at 3:52:49 with the floor repeat on iteration 0, probe arms at 1:50 and
1:33 with the third queued. Thresholds untouched. No mail this cycle — nothing finished, and this refines a
diagnosis I already sent rather than reversing it.

### The D2 scatter is deterministic structure, not noise — one remedy class eliminated

Session A's **epochs-8 control** (`56431649`) COMPLETED cleanly (1:58:13, rc=0) and its watch fired. Session A
is closed, so I read the science per brief item 2. It is an independent repeat of the D2 closure at the nominal
config and it reproduces the original:

                            56381674        56431649 (ctl8)
    recovery                0.546853            0.548769
    gap                     0.234270            0.234270   (identical)
    floor                   0.010747            0.010747   (identical)
    residual                0.106159            0.105710

`gap`/`floor` are bit-identical because they are training-independent, as the preflight states. Recovery
reproduces to 0.002.

**That makes the valuable question answerable.** Session A showed the shortfall is 97.8% per-bin scatter rather
than bias, but two very different worlds give that same number: independent per-run noise (averaging shrinks it
like 1/√N, so an ensemble could pass) versus deterministic structure (averaging changes nothing). With two
independent runs and all 285 cells in both reports:

    Pearson r(per-cell residual_A, residual_B)   0.999942
    L1 between the two unfolded spectra          0.001392   against gap 0.234270
    recovery of mean(A,B)                        0.547819   -- 0.21% WORSE than the better single run
    independent noise would have cut the scatter term 29.3% with two runs

**Structure, to five nines.** I measured the actual proposed remedy — recomputing recovery on the ensembled
spectrum — rather than a proxy for it. Session A's word "scatter" is doing double duty: this is cell-to-cell
**dispersion**, deterministic, not statistical randomness.

**The scope limit matters and I am stating it rather than letting the result be over-read.** Both runs share
identical seeds (`estimator_seed 42`, `subsample_seed 0`, `split_seed 7`), so r = 0.999942 measures **GPU
nondeterminism only**. Ruled out: averaging repeat runs at the same seeds. **Not** ruled out: averaging over
different **estimator seeds**, which is what "ensemble it" usually means and is untested. I am not claiming to
have killed ensembling, only its cheap version.

**Proposed next experiment, not queued:** one probe arm identical to the control but with a different
`estimator_seed`. If its residual pattern correlates as tightly as the GPU repeat did, the dispersion is a
property of the data and geometry, no ensemble helps, and the criterion must change — a definitive answer for
~2 GPU-h. If it decorrelates, seed ensembling is a real lever worth costing. **Deliberately not submitted**:
the floor repeat plus ep16 and ep32 are already contending and ep32 is still PENDING, so adding a fourth GPU
job would be inconsiderate rather than helpful. Flagged for Joseph's word.

Tool committed as `nd-unfolding/pet/scatter_reproducibility.py`. Thresholds untouched; `recovery_min = 0.80`
neither touched nor evaluated against. Mailed.

### The deficit is worst where acceptance is HIGHEST — an inverted-correction signature

I asked whether the nominal's fold-forward deficit and the D2 dispersion share an acceptance-driven cause,
expecting the suppression to sit in **low**-acceptance cells. It is acceptance-structured — with the sign
**inverted** from my hypothesis. Per-cell reco-weighted mean push against the committed acceptance map, over
`pass_reco`, on the canonical 285-cell grid (numpy only, no inference, no GPU):

    Pearson r(acceptance, mean push)   -0.4291      reco-weight-weighted  -0.5427

    acceptance band   cells   reco wt %   mean push
    [0.00,0.01)         31      0.17%      1.0534
    [0.01,0.05)         10      0.26%      1.0374
    [0.05,0.20)          7      1.59%      1.0259
    [0.20,0.40)         13      6.47%      1.0121
    [0.40,0.60)         25     15.51%      0.9751
    [0.60,0.80)         53     42.76%      0.7875
    [0.80,1.01)        117     33.23%      0.5180

**Monotonic across all seven bands.** Low-acceptance cells sit near 1.0 — exactly what the prior-dominated
picture predicts, and reassuring. But the 117 cells at acceptance ≥ 0.8, carrying a third of the reco weight,
are pushed **down to 0.518** where the identity requires an average of 1.124.

**The estimator is most wrong precisely where it has the most information, in the direction opposite to what
the data demand.** With the earlier finding that only 1.06% of rows exceed R at all, the pattern reads: the
better a cell is measured, the harder it is pushed the wrong way.

That is the signature of a correction applied with the wrong **sense** — an inverted likelihood ratio, or the
data and MC legs swapped between step 1 and the push. Where acceptance is high, step 1 has the most
discrimination and applies the largest correction, so an inversion hurts most there and fades toward the
prior-dominated cells. The observed monotonic profile is that shape.

**Recorded as a hypothesis with a matching signature, not a diagnosis.** I have not read the step-1 path for a
sign error and will not assert one from a correlation. But it is now the most specific testable candidate, it
subsumes the earlier "step-1 under-achievement" hypothesis, and it is a far better place to look than the
tolerance.

**Cheap falsification available, no GPU:** recompute the fold-forward ratio with `push` replaced by its
reciprocal, or by `2 − push`, on the high-acceptance subset. If an inversion reproduces R to within the
dilution residual, the sign hypothesis is arithmetically settled. Offered to Joseph rather than run
unprompted, since it is the kind of test whose framing he may want to set.

Tool committed as `nd-unfolding/pet/push_vs_acceptance.py`. Thresholds untouched. Mailed.

### The inversion screen weakens my own leading hypothesis — and rules out a global rescale twice over

I had offered this test and said its framing was Joseph's to set, because picking one inversion form is the
easiest way to manufacture a clean-looking answer. Resolved that by testing a **family** and reporting every
member, so there is no framing choice to get wrong. Reco-weighted mean over `pass_reco`, exactly as the gate
evaluates the real one:

    candidate           reco-wtd mean   dev vs R   r(acc,mean)   low-acc   high-acc
    push (observed)          0.746483     0.3359      -0.4291     1.0297     0.5180
    1/push                   2.532831     1.2532      +0.3995     0.9745     4.5146
    2 - push                 1.253517     0.1151      +0.4291     0.9703     1.4820
    R/push                   2.847105     1.5328      +0.3995     1.0955     5.0747
    R^2/push                 3.200375     1.8471      +0.3995     1.2314     5.7044
    push * R/mean            1.124080     0.0000      -0.4291     1.5506     0.7800

**No candidate meets both requirements** — a genuine explanation has to put *both* acceptance bands near R
*and* flatten the slope. Every inversion form flips `r` from −0.43 to **+0.40**: it mirrors the defect rather
than removing it, turning "suppressed at high acceptance" into "enhanced at high acceptance". And `1/push`
overshoots absurdly (mean 2.53, high-acceptance band 4.51, max 23), because the small-push tail (min 0.0432)
inverts to ~23 — a naive inversion does not shift the mean, it manufactures a tail the data cannot support.

**So the cheap version of my inverted-correction hypothesis is not supported.** The final cumulative push is
not a simple algebraic inversion of a correct one. I raised that hypothesis last cycle as "the most specific
testable candidate"; the test weakened it, and the record should say so rather than leave the stronger claim
standing.

**What it does NOT do is exonerate a step-1 sign error**, and the caveat was written into the script before
running it: `weights_push` is a product over three iterations with a step-2 regression that pins
off-acceptance rows, so an inverted step-1 likelihood ratio would not propagate to *any* of these closed
forms. This screen tests the final push, not step 1. That question still needs the inference test.

**One control earned its place.** `push * R/mean` is a pure global rescale: it hits R *exactly* by
construction, yet leaves the acceptance slope at −0.4291 with bands at 1.5506 and 0.7800. So no global
normalisation factor can fix this, re-confirming by a second and independent route what the band table already
implied — the defect is acceptance-structured, not a scale error. Worth keeping because it is the one
hypothesis someone would otherwise be tempted to try first.

Tool committed as `nd-unfolding/pet/inversion_screen.py`. Thresholds untouched. No mail: this weakens a
hypothesis I already sent rather than adding a decision, and the floor repeat is close enough that batching is
better than two mails an hour apart. Nominal at 5:22:53 with the floor on `iter2_step1`; ep16 at 3:03, ep32
queued, both watches armed.

### Holding: floor repeat in its final push; both decisive next steps need a GPU

No new mail, nothing finished. `56415634` at 5:53:21 has all six floor step files
(`iter0`–`iter2` × `step1`/`step2`) but no `pet_fullevent_floor_weights.npz` yet, so it is in the
`--reweight-all` pass over the full 32.8M-row cloud — the same phase that took the nominal ~45 min between
its last step file and its artifact. Wall expires 12:27Z, so there is ample margin.

Deliberately doing nothing this cycle. The two steps that would advance the diagnosis both need a GPU —
the step-1 inference test, and the different-`estimator_seed` arm that would settle whether *any* ensemble
can help — and `56415634`, `b1nit5b` and ep16 are already contending with ep32 still PENDING. Adding a
fourth GPU job to diagnose a problem is not worth delaying the floor repeat that is about to produce the
GPU-nondeterminism reference for that same problem.

The cheap numpy-only avenues are exhausted for now: the failure is independently confirmed, localised to
the high-acceptance cells, and both a global rescale and a naive inversion of the final push are excluded.
What remains genuinely requires either inference or Joseph's framing, and both are flagged.

### 56415634 COMPLETE — the floor repeat confirms the failure is deterministic, and measures the GPU floor

`[fe_pet_nom] DONE 2026-08-07T06:24:41Z`. Both artifacts written — `pet_fullevent_nominal_weights.npz`
(10,110,334 B) and `pet_fullevent_floor_weights.npz` (10,158,903 B) — with **no walltime kill and no partial
state**, so the failure mode the 8h→12h raise was made to avoid did not occur. Two full trainings in ~6h
against a 12h wall.

**The determinism answer, which is the entire point of the matched floor repeat.** Identical seeds and config,
so the only difference is GPU nondeterminism:

                                nominal                floor
    fold_forward_reco_ratio     0.7464834064182863     0.7388746403442940
    dev vs R = 1.1241           0.335916               0.342685
    mean push                   0.895412               0.886783
    n_pass_reco / cells         837671 / 259           identical
    cap_saturation_frac         0.0                    0.0

The runs differ by **1.02%** relative on the ratio (0.97% on mean push) while both miss R by ~34%. GPU
nondeterminism is two orders of magnitude too small to explain the failure: **deterministic**, matching what
the D2 control established independently at r=0.99994.

**Useful by-product worth keeping separately from the failure:** the GPU-nondeterminism floor for this
estimator is now **measured at ~1%** on the fold-forward ratio. That is exactly what the launcher's "matched
GPU-floor repeat" was built to expose, it is a legitimate deliverable, and it stands even though the central
value does not.

**Diagnosis status — every item established by an independent check rather than by argument.** Confirmed: the
failure is real (independent recomputation, 1.4e-12); deterministic (this repeat, plus the D2 control);
monotonic in acceptance and worst where acceptance is highest (push 0.518 in the 117 cells at a≥0.8 carrying a
third of the reco weight); **not** a global normalisation error (a pure rescale hits R exactly yet leaves the
slope at −0.4291); **not** a simple inversion of the final push (every form mirrors the slope rather than
flattening it, and 1/push overshoots to mean 2.53, max 23).

Still open, both needing a GPU rather than more arithmetic: **(1)** step-1 achievement by inference with the
saved `w_nominal/*_step1.weights.h5` — nothing stored supports that comparison, which is the BEN-039 trap
itself; **(2)** whether *any* ensemble helps, via one arm at a different `estimator_seed` — this repeat has
ruled out averaging over GPU noise specifically, which was the cheap version.

GPUs are freeing up now this job is done. I proposed (1) first, since it targets the leading hypothesis whereas
(2) prices a remedy for a cause not yet identified — asked Joseph whether he wants that order. Gate-4 stays
red and the product NON-QUOTABLE, unchanged and already red from D2. Slurm blipped again mid-cycle
(`Unable to contact slurm controller`) and was again caught only because stderr was kept. Mailed.

### The under-fitting hypothesis is dead, and dead in the wrong direction

`56431650` (ep16) COMPLETED 03:43:39 rc=0, watch fired. Session A owned the probes and is closed, so I read
the science per brief item 2. It was the handoff's *"what I would do first"*, so this closes that thread:

    arm                    epochs  niter   recovery   residual   verdict
    56381674 (original)         8      3   0.546853   0.106159    FAIL
    56431649 (ctl8 control)     8      3   0.548769   0.105710    FAIL
    56431650 (ep16)            16      3   0.536695   0.108539    FAIL
    criterion                              >= 0.80    <= 0.046854

**Doubling the epochs moved recovery 0.548769 → 0.536695 — a 2.2% relative DECREASE.** That is outside the
GPU-nondeterminism band the control pinned at ~0.35% (0.548769 vs 0.546853 at identical config), so the change
is real, small, and backwards. `56431651` (ep32, 4× budget) is still PENDING and will add a third point; I
expect confirmation but would rather have the point than assume, and it costs nothing now it is queued.

**Four independent directions now converge.** The shortfall is 97.8% per-bin dispersion rather than bias
(Session A); that dispersion is deterministic (r = 0.99994 across identical-seed runs); averaging repeat runs
does not help (measured on the ensembled spectrum, not inferred); and more training budget does not help
either. So D2 is not an optimization problem, not a convergence problem, and not a noise problem. What remains
is seed-ensembling (untested) or the criterion itself — and since the criterion takes a per-cell absolute
value, it converts deterministic dispersion into a one-sided penalty by construction. I have said so to Joseph
while flagging that "never raise a tolerance to make a check pass" cuts against me pressing that view too hard.

**On the step-1 test: I checked whether it could be done safely instead of hand-rolled, and only partly.**
`extract_fullevent_fps.py:152,247-253` already reads the `inference_contract`, builds the model and loads a
saved checkpoint — so that idiom is committed and supported. But it loads the **step-2** checkpoint in **truth**
space. Step-1 achievement needs the **reco** leg, which no committed consumer evaluates, so it is genuinely new
code in a different input space. **Still holding it.** A wrong preprocessing choice there yields a
plausible-looking wrong number on the headline failure, which is worse than having no number; if Joseph wants
it I will write it and put it through fresh-context review before trusting the output.

Also complete: `56415634` COMPLETED 05:57:38 rc=0 (mailed last cycle, watch fired) and `b1nit5b` COMPLETED
04:07:38 rc=0 — the latter belongs to the k-scan session, so I have deliberately not read it. Only ep32
remains queued. Thresholds untouched; Gate-4 red and product NON-QUOTABLE, both unchanged. Mailed.

### Quiet cycle: everything in my lane is either done or waiting on Joseph

No new mail, nothing finished. Only the `wakerctl` cron is running; `56431651` (ep32) is still PENDING,
submitted 18:54:02 — about 13h queued at priority 67996 with `Start=Unknown`. Its watch is armed.

**Kept ep32 rather than cancelling it, on purpose.** With only ctl8 (0.548769) and ep16 (0.536695) I cannot
separate a monotone worsening trend from scatter beyond the ~0.35% GPU band, and ep32 at 4× budget
discriminates those. Cancelling would free an allocation that is idle anyway, so there is nothing concrete to
gain and one real point to lose.

**Quiet integrity check** on the campaign's two new artifacts, both digests recorded so a later reader can
detect drift:

    pet_fullevent_nominal_weights.npz   sha 8d17140f697faca7   27 keys   no non-finite arrays
    pet_fullevent_floor_weights.npz     sha 28fe004c31dcb414   27 keys   no non-finite arrays

**Nothing else is actionable and I am not inventing work.** The two remaining diagnostic steps — step-1
achievement by inference, and the different-`estimator_seed` arm — are both held for Joseph's word, and the
step-1 one for a substantive reason rather than politeness: it needs new code evaluating the reco leg, which no
committed consumer does, and a wrong preprocessing choice would produce a plausible wrong number on the
headline failure. Plan Step 5 (`values.tex`) is gated on the five-band laterals another session owns; Step 3 is
moot for the GBDT lane and needs the PET budget build for the PET lane. No mail: nothing finished, and the last
three cycles each carried a real result, so another would be noise.

### Standing down — lane complete pending five decisions, all of which are Joseph's

Second consecutive cycle with nothing finished and nothing actionable, so this is the brief's "verify quietly,
mail a short status, and stop". `56431651` (ep32) is still PENDING after ~13.5h at priority 67996 with no start
estimate; only the cron is otherwise queued; no other session has pushed since `2bb1d21`.

Mailed a **consolidated decision list** rather than another report. That is worth one mail because the five
open items are currently spread across five separate mails, and a list of what is waiting on him is new
information even though each item is not:

1. **The nominal's normalization failure, where I have run out of safe diagnostics.** Everything cheap is done
   and everything cheap came back negative — bookkeeping, global rescale, naive inversion, dilution, saturation
   all excluded; deterministic; monotonic in acceptance and worst where acceptance is highest. The live
   hypothesis needs new code on the reco leg, which I will not hand-roll unreviewed on the headline product.
2. **The D2 criterion.** Four independent lines say the shortfall is neither optimization, convergence nor
   noise. I think the criterion is the defect, and I have said so once while noting that "never raise a
   tolerance to make a check pass" means I should not press it — a redesign is his call, not something to argue
   into.
3. **Seed-ensembling**, untested, ~2 GPU-h, sequenced after (1) because it prices a remedy for an unidentified
   cause.
4. **`values.tex`** — corrected numbers ready, macros untouched, gated on another session's laterals.
5. **`combine_cstat_bkgsub_100rep.py`** untracked, so its 5 tests cannot land without either tracking
   unreviewed code or guaranteeing a collection error.

**Deliberately not doing:** running the extraction on a nominal that fails its own normalization gate. It would
produce a cross section knowingly ~34% low in the reco-visible region, and creating that artifact invites a
later reader to mistake it for a result. The absence of that file is the correct state.

ep32's watch is armed, so its result reaches Joseph from Slurm cron whether or not this session is alive — which
is the property that has already justified itself twice today, once when my ssh certificate expired and once
when Slurm blipped. Thresholds untouched throughout.

### Verified the notification mechanism survived three Slurm outages — which is what makes standing down safe

Third Slurm controller outage today (~03:19Z, ~06:50Z, ~09:19Z), so `squeue`/`sacct` were unreadable this
cycle and ep32's state could not be polled. That prompted the one check worth doing while idle: `wakerctl`
evaluates a `slurm-job` watch by calling `sacct`, and on failure increments an `unreliable` counter that emits a
spurious `monitor-error` at 10 — so repeated blips could in principle degrade the very mechanism I am relying
on to deliver ep32's result.

It has not. `d2-probe-ep32-56431651.json` shows **`unreliable: 0`**, no `monitor-error` events are spooled, and
`evt-nominal-56415634.done` plus `evt-d2-probe-ep16-56431650.done` show both earlier watches fired **and
completed dispatch** — positive end-to-end evidence rather than merely "armed". The stale `cron-tick.log` mtime
is expected and not a symptom: `--open-mode=append` with `--quiet` writes nothing when there is nothing to say.

No mail, no other action: nothing finished and nothing to decide. Recording this because a future reader
otherwise has to re-derive whether today's intermittent Slurm affected the watches, and the answer is no.

### CORRECTION: there was no Slurm outage — I inferred one from a single flaky query

Earlier this cycle I reported a **sustained** Slurm outage because `squeue -u josephrb` failed at both 09:19Z and
09:49Z. **Wrong.** Probing the service directly: `scontrol ping` returns `Slurmctld(primary) at slurmctld is UP`,
`sinfo` lists partitions up, a single-job `squeue -j 56160911` works, the ep32 watch's `unreliable` counter is
still **0** — so the tick's own `sacct` calls had been succeeding the whole time — and three immediate retries of
the user-wide query succeeded 3/3. The user-wide form is simply heavier than a single-job query and times out
intermittently under load.

Both directions of this mistake happened within hours today: earlier an *empty* `squeue` (stderr discarded) led
me to report every job had vanished; now two failures led me to report an outage. Amended onto **BEN-035** with
the rule: **never infer service state from one client command** — probe the service (`scontrol ping`, `sinfo`,
single-job query) and check local state that would corroborate. Here the watch's `unreliable` counter was
decisive, because it records whether something *else* had been reaching Slurm all along.

`56431651` (ep32) is confirmed still **PENDING**, priority 68121, submitted 2026-08-06T18:54:02 — ~15h queued
with no start estimate. Watch armed, `unreliable=0`, so its result still arrives from cron regardless of this
session. Nothing finished; no mail.

### Memo items 0 and 1 (free check): checkpoints preserved; the leg mismatch is real but not the whole deficit

**Item 0 DONE — all checkpoints off scratch.** `w_nominal` and `w_floor` (12 files each: 3 iterations × 2 steps
× `.pkl`+`.weights.h5`, so both legs and every iteration), plus both weights artifacts and the run logs, copied
to `/global/cfs/cdirs/m3246/josephrb/fullevent-nominal-checkpoints-20260807`. **28 files re-hashed on both sides,
0 mismatches**, 31 MB. `iter2_step1` and `iter1_step2` — the pair the corrected diagnostic needs — confirmed
present. One self-inflicted scare: `du` initially reported **11K** while the per-file listing showed ~987 KB
files. It was a stale reading taken while CFS was still flushing; byte totals and a re-run both give 31M. I
had also hidden `cp` stderr with `2>/dev/null` on the artifact copies, which is exactly the habit I flagged
earlier today — the discrepancy is what forced me to check rather than assume.

**Item 1 free check: it did NOT delete the step-1 work, but it priced a real effect.**

    mean_w_truth(push | pass_truth) = 0.888234
    mean_w_reco (push | pass_reco)  = 0.746483
    ratio truth-leg / reco-leg      = 1.189891

The leg choice is worth **~19%** of the 34% gap — a genuine contribution, and the memo's mechanism is real. But
the truth leg is *also* far below R, so by the reading I predeclared before running ("both short → the deficit
is upstream of the leg choice"), the step-1 harness is still required.

**A caveat on the memo's framing, flagged rather than adopted:** comparing the truth-leg mean to R is plausibly a
**category error**. R is a reco-space quantity — background-subtracted data yield over MC reco — and nothing
requires the *truth*-weighted mean of push to equal it. That is structurally the same trap the memo itself warns
about for `iter2_step1` (an incremental factor compared against a cumulative target). The defensible number is
the inter-leg **ratio** 1.1899; "the truth leg is 21% short of R" should not be quoted as a defect.

**Two memo predictions checked, one confirmed exactly and one numerically void.** Stored `push` is **exactly
1.0** on truth-failing rows — 72/72, `max|push−1| = 0` — which is Gate B part (ii) satisfied in advance. But
only **72** of 2,000,000 rows fail truth, so the "deficit is worse than 0.7465" correction is negligible:
`f = 0.000089` gives 0.746461 against 0.746483, and the direct computation agrees with the memo's
`(ratio−f)/(1−f)` to 2e-16. Correct in principle, irrelevant in magnitude here.

**And it corrects an error of mine.** My earlier push anatomy split on `pass_reco` and reported off-acceptance
pushes as *near* 1 rather than exactly 1. The pinning is on `pass_truth` — a different mask — and with 99.996%
of rows passing truth, the two masks behave completely differently. Tool committed as
`nd-unfolding/pet/leg_mismatch.py`.

### Memo item 2 — the oracle says the D2 criterion is FINE, and kills my own redesign argument

Ran the assumption-free oracle with the criterion code **unmodified**, halves taken from the artifact's own
`dump_rows_a`/`dump_rows_b` so no loader re-run and no subsample-seed reproduction risk:

    variant 1, tilt recomputed on half B     oracle recovery 0.954204
    variant 2, A's quantiles applied to B    oracle recovery 0.954184
    bar                                                      0.80

**A perfect estimator scores 0.9542 against a 0.80 bar.** So the criterion is achievable with ~15 pp of
headroom, the estimator's 0.5469 is a genuine shortfall, and — exactly as the memo predicted for this branch —
**the redesign argument dies for free.** Both variants agree to 2e-5, so the ambiguity in "the same tilt applied
to B" (whose quantiles, whose normalisation) does not affect the conclusion; I computed both rather than pick.

**Gated before printing.** The reconstruction reproduces the committed report's gap/floor/residual/recovery to
≤2.2e-9 and the truth-passing counts match **exactly** (1999920, 1999941); on failure the script refuses to
print an oracle number at all. One tolerance note, since the memo explicitly forbids reconciling a gate by
loosening it: my first gate at 1e-9 fired on `floor` at 2.17e-9, and I re-scaled to 1e-7 **with the reasoning
written into the code** — Gate B's 1e-6 is justified because a wrong z-score moves logits by order unity, but
this gate sums 285 float64 absolute differences of ~1e-2 quantities where a wrong half or mask shifts the result
by 1e-2 to 1, so 1e-7 keeps five orders of margin. I also added an **exact, untoleranced** population check so
the structural half cannot be loosened at all.

**This refutes my own reasoning, not merely a number.** I argued the per-cell absolute value makes the criterion
measure variance and is therefore unfair. The oracle is subject to **the same absolute value** and scores
0.9542 — so the `|·|` is not the obstacle, and the dispersion is the estimator's own rather than an artifact of
the metric. My argument does not survive its own test, and item 2 is decided against the position I held.

**Memo defect (a) is measured and closed, not confirmed:**

    floor  (A/B, UNTILTED)   0.010747   floor/gap 0.045876
    oracle (A/B, TILTED)     0.010729   /gap      0.045796   understatement 0.998x

The tilted sampling difference is essentially identical to the untilted one and marginally *smaller*, so
`floor/gap <= 0.10` under-bounds nothing. Defect (b) — no split of signed response from scatter — still stands
as a design observation but is now a nice-to-have, not grounds for redesign.

**Effect on the picture:** sampling is only **10.1%** of the measured residual (0.010729 of 0.106159), so ~90%
is genuine estimator error. With the fold-forward gate also failing deterministically and worst where acceptance
is highest, both failures now point at the estimator rather than the criteria.

**Limit stated so this is not over-read:** the oracle bounds recovery given **sampling** only. It does *not*
establish that a real estimator can reach 0.80 given acceptance limits — the dilution model put that at 0.6332,
and BEN-038 records that it is not a bound (low-acceptance cells beat it 19×). "Achievable in the sampling
sense" is proven; "a real estimator can reach it" is not. Tool committed as `nd-unfolding/pet/d2_oracle.py`.
Mailed.

### Memo item 3 — the pre-registration is FALSIFIED IN ADVANCE, and D2's dominant term is not what we thought

Joseph's memo asked for a free pre-registration before ep32 lands: *"4x budget overfits the finite training
half harder => MORE per-cell scatter => recovery worse again."* Before registering it I decomposed the two
arms already in hand, and the hypothesis is **wrong in mechanism even where it is right in direction** —
so registering it would have been pre-registration in name only. What the decomposition turned up is
larger than the pre-registration question.

**The D2 miss is 81.4% a coherent under-application of the injected tilt, not 97.8% scatter.** Both
readings are the same two numbers over different denominators:

    total miss  E_w[|1-r|]              0.453147   (= 1 - recovery)
    coherent    |1-E_w[r]|              0.368714   81.4%   <- the estimator applies 63.1% of the tilt
    dispersion  published penalty       0.084433   18.6%

The published **97.8%** is measured against the *dilution ideal* 0.63321; the **0.80 bar** compares against
full recovery. 2b's denominator presupposes the under-application is unavoidable, which 2b's own refutation
paragraph says is not established. Verified two independent ways agreeing to **9.2e-06**: as `|1-E_w[r]|` in
response space, and as the pt-marginal L1 over the gap in spectrum space (the injection is a function of pt
alone, so what survives marginalising over p-parallel is the part coherent with what is measured).

**I nearly filed a false refutation, and that is the BEN-042 lesson (renumbered from 041: the concurrent GBDT lane took 041 in the same window, caught on a rejected push).** 2b closes with *"the scatter penalty
alone (0.08443) exceeds the entire residual headroom (residual_budget_abs = 0.046854)"*. The penalty is
weight-normalised; `residual_budget_abs` is an absolute `0.20 x gap`. In consistent units the penalty is
**2.37x INSIDE** the headroom — both ways of reconciling them agree — so the sentence inverts. I had
"2b is refuted on a unit error" written down. **It is not.** The penalty is not the cost of removing the
bias: with `x = 1-r`, a perfect-mean-response estimator pays `E_w[|x - E_w[x]|]`, a weighted MAD, not
`E_w[|x|] - |E_w[x]|`, because `|.|` is nonlinear under a shift. Measured **MAD/penalty = 4.38**, the honest
counterfactual is **recovery 0.6302, FAIL**, and the dispersion **exceeds** the headroom by 1.85x. So 2b's
conclusion is right by a route its own arithmetic did not take, and the corrected number makes it stronger.

**Each term alone fails the bar, which is what actually closes the remedy question:**

    perfect mean response, measured dispersion   ->  0.6302   FAIL
    zero dispersion, measured mean response      ->  0.6313   FAIL

So **no single-axis remedy passes D2**, and specifically **seed-ensembling caps at 0.6313 for ANY N** —
it moves dispersion and leaves the mean response alone. Against the memo's "N ~ 16-25 seeds, 30-50 GPU-h"
that is a number, not a preference, and it is why I am **not submitting the seed arm**: it remains a
legitimate diagnostic of whether the dispersion is seed-structured, but that answer now changes no
decision. Joseph's call to overrule. The two terms are also comparable in size (0.3687 vs 0.3698), which
neither previous framing showed.

**The ladder moved the coherent term, not the scatter term** — the arm the ladder was armed to read:

    ctl8(ep8) -> ep16   recovery 0.548769 -> 0.536695   E_w[r] 0.63250 -> 0.56324
                        coherent 0.367501 -> 0.436756  (+18.8%)
                        MAD      0.366439 -> 0.346135  (-5.5%)
                        penalty  0.083729 -> 0.026549  (-68.3%)   <- not a dispersion measure

Read through the penalty the ladder claims a 68% win that the MAD says did not happen: the penalty tracks
how many cells straddle `r = 1`, and 2x budget pushed 38 of 86 overshooting cells back under. Dispersion
went **down** on both measures, so the memo's mechanism is falsified; recovery fell because the coherent
term grew more.

**ep32 (`56431651`) is still PENDING** (submitted 18:54:02, ~16.4 h queued), so I pre-registered the
*corrected* prediction while the window is genuinely open: `E_w[r]` < 0.56324 in [0.48, 0.56], MAD < 0.346135
in [0.31, 0.346], recovery < 0.536695 in [0.49, 0.537], verdict FAIL — each with an explicit falsifier.

Tool committed as `nd-unfolding/pet/d2_response_decomposition.py`, gated on reproducing all four published
2b numbers plus the report's own recovery before it prints anything, and on the two constructions agreeing.
Finding: `FINDING-20260807-d2-response-reference-point.md`, indexed, with dated pointers added to 2b and to
the concurrent session's probe finding rather than rewriting either. **No threshold touched.** Also
confirmed this cycle from `sacct`: `56415634` COMPLETED 05:57:38 rc=0 and `56431650` COMPLETED 03:43:39
rc=0 (both already logged), `56431651` the only non-cron job left. Joseph's 20:29Z GBDT question was
answered in `STEP2-20260806-niter3-budget-classification.md:138`. Mailed.

### Memo item 5, gates only — THE SAVED CHECKPOINT IS NOT THE TRAINED MODEL, and it blocks extraction

I built the memo's two gates and ran them before writing any pull/push decomposition. Gate A passed
bit-exactly and **Gate B(i) failed at max rel dev 0.866 against a 1e-6 tolerance.** That is not a
formality failing; it is a real defect on the publication path, and it was found by building the gate the
memo asked for rather than by looking for it.

    A1  rebuilt mc_indices vs stored        BIT-EXACT, 0 differing rows of 2,000,000
    A2  rebuilt truth normalization         BIT-EXACT against the contract
    B(ii) stored push == 1.0 off pass_gen   72/72 EXACT (untoleranced, as the memo required)
    B(i)  checkpoint-rebuilt vs stored      max 8.663e-01  median 8.34e-03  p90 1.68e-01  FAIL

**Gate A passing is what makes it interpretable** — same rows, same input space, so this is not the
preprocessing failure I had been holding this task to avoid. The weights themselves differ.

**Mechanism, read off the engine while building the harness rather than found by guessing.**
`omnifold.py:272-275` checkpoints with `save_best_only=True`; `:266-268` sets `EarlyStopping(patience=10,
restore_best_weights=True)`; at `epochs=8` the patience can never be exhausted and Keras 2.15 restores
best weights only in the stop branch. So the model **in memory** at reweight time is the **last** epoch
and the file on disk is the **best-val-loss** epoch. `train_*:497` stores the last-epoch output;
`inference_contract["step2_checkpoint"]`, which `extract_fullevent_fps.py:253` loads, is the best-epoch
file. The nominal's own history has `argmin(val_loss)` at **epoch 4 of 8** for `iter2_step2`.

**The sharpest form: the weights that produced the published artifact do not exist on disk.**
`--step2-checkpoint` can point elsewhere, but `save_best_only=True` never wrote a last-epoch file, so
there is nothing to point at.

**Consequence, and it is a blocker.** `check_subsample_agreement` (`:347`, `tol=1e-3`, called
unconditionally at `:609`) fails closed at 0.866, so the full-event push stage **cannot run**. The gate is
right; the tolerance stays where it is. Full-event extraction is blocked until Joseph picks an option.

**I did not stop at "leading explanation".** Two controls, both off one loader build (job 56445569):

    Control 1  batch 1000 vs 512            2.901e-06  = 0.0003% of the deviation -> EXCLUDED
    Control 1b B(i) bit-identical across jobs           -> GPU nondeterminism EXCLUDED
    Control 2  matched floor run            max 8.643e-01, p90 1.650e-01, aggregate gap 1.53e-02
               shares the subsample bit-exactly, 72/72 off-shell exact -> STRUCTURAL, not a one-off

Six candidate explanations are now excluded by measurement and one survives. Unplanned corroboration: the
floor run has the larger best-vs-last val-loss gap (+0.00149 vs +0.00074) **and** the larger aggregate
deviation (1.53e-02 vs 4.63e-03) — right ordering, and I am claiming direction only, since 2.0x in val gap
against 3.3x in deviation is not proportionality.

**What it does NOT change.** The artifact is self-consistent (`central_vector` came from the same
in-process `weights_push`), so the central value is not invalidated — only its reproducibility. And both
models give the fold-forward ratio to 1e-4 (0.746483 vs 0.746407), so the normalization failure is a
property of the estimator, not of which epoch was saved. The memo's step-1 decomposition remains the right
next question; its harness is committed and **gated on this receipt**, refusing to run without Gate A and
copying Gate B's verdict into its own output so the caveat travels with the number.

**Memo item 4 (`values.tex`) — HELD, deliberately, and not silently.** The ledger half is already done
(5.2600e-38 / 5.6609e-38 are recorded at `VALIDATION_LEDGER.md:142-143`). The edit half touches
`\gbdtFive*`, which is squarely the GBDT lane Joseph launched today, and that session's prompt says in
its own words *"do not update values.tex until a G-5 adoption has landed in the ledger"*. Doing it now
would both cross a lane boundary and write a number G-5 is about to supersede. Left to G-5.

Also this cycle: ep32 (`56431651`) still PENDING, watch `d2-probe-ep32-56431651` armed with
`unreliable=0` and the cron ticking (11:45:13Z). The powered-closure driver and preflight shas were
re-verified against the launcher pins after each cluster fast-forward, so ep32 cannot be killed by my
transfers. Mailed.

### Memo item 5 ANSWERED — step 1 genuinely under-achieves, by 32%, and iteration 2 is where it breaks

Job `56445667`, 4m38s. The predeclared reading fired its **second** branch, not the one the leg-mismatch
result had me expecting.

    quantity      mean_w_reco|pass_reco   dev vs R   mean_w_truth|pass_gen
    push_stored              0.746483      -0.3359            0.888234
    push_final               0.746407      -0.3360            0.884253
    pull_final               0.765031      -0.3194            0.934530
    push_prev                0.936383      -0.1670            1.006938
    increment1               0.751119      -0.3318            0.894941

**`pull_final` is the quantity step 1 itself normalizes, and it misses R by 32%.** Step 1 trains data vs
reco MC with the MC side normalized to 1e6 and the target to 1e6*R, so `mean_w_reco(pull|pass_reco) == R`
is step 1's OWN objective, not an identity imported from elsewhere. It delivers **68.1%** of it. So the
fold-forward failure is **not** an artifact of reading a step-2 quantity against a reco-leg identity, which
was the live alternative after `leg_mismatch.py` priced the leg at only ~19%.

**Where it breaks, and it is not monotone convergence:**

    iter1 step2   push_prev   0.936  dev -0.167
    iter2 step1   pull_final  0.765  dev -0.319   <- largest single drop, and it is STEP 1's
    iter2 step2   push_final  0.746  dev -0.336

Step 1's last iteration moves the normalization AWAY from R. Nothing in the chain moves toward it. (Means
do not multiply: 0.936 x 0.751 = 0.703 against a measured 0.765, so the two are positively correlated —
stated as measured values, not as a product.)

**A second, independent signal in the truth column.** Step 2 should reproduce
`mean_w_truth(pull|pass_gen)`. At iteration 1 `push_prev` gives **1.0069**, within 0.7% of 1.0 — a
well-fitted step 2. At iteration 2 `push_final` gives 0.8843 against its target 0.9345, under-shooting by
**5.4%**. So both steps lose at iteration 2 and step 1 loses far more.

**The checkpoint caveat is bounded, not merely declared.** Everything is a checkpoint-based reconstruction
(BEN-043). But the one quantity that exists both ways agrees to **1e-4** — `push_stored` 0.746483 vs
`push_final` 0.746407 — three orders below the 32% effect, and both legs are reconstructed identically so
the comparison is sound by construction. Stated asymmetry: `push_prev` comes from `iter1_step2`, whose
argmin IS the last epoch, so that checkpoint is faithful; `increment1` comes from `iter2_step1` (argmin
6/8) and is not, which makes the 0.936 -> 0.765 drop the number most exposed to the caveat.

**Not claimed:** why step 1 under-achieves. Untested candidates are listed in the finding — reco-leg
under-training, asymmetric F3 cap saturation, the R=1.124 class imbalance being partly inexpressible, and
the `pass_reco`-only update interacting with acceptance. `cap_saturation_frac` is already in the artifact
and is the cheapest next check.

Also recorded this cycle: **a trap in my own recommended fix.** `self.model1`/`self.model2` are assigned
once at `omnifold.py:123-124` and never reassigned; training runs on the `clone_model` copies in
`step1_models`/`step2_models`, and `clone_model` does not copy weights — so **`of.model2` still holds its
initial random init when `Unfold()` returns**, and implementing option (1) as `of.model2.save_weights(...)`
would persist an untrained network. Correct objects: `of.step2_models[0]`, `of.step1_models[0]`. Also
`omnifold.py:302` logs `val_loss[0]`, the FIRST epoch, so the engine's own log cannot show the
best-vs-last gap at all; only the `.pkl` histories can.

**Fix NOT implemented, deliberately.** Both files that would change (`train_fullevent_nominal.py`,
`omnifold.py`) are sha-pinned by the live Gate-4 code gate (`...-20260806c.json`, keys `driver` and
`estimator_engine_multifold`), so the edit needs a gate re-issue in the same commit and
`_LAUNCH_CODE_FLOOR = 2` fails if a predecessor retires without its successor. Re-issuing a gate to enable
a ~6 GPU-h re-run on a choice that may redefine the nominal estimator is Joseph's call. No mail this cycle
beyond the batched one already sent — this result goes in the next batch. ep32 (`56431651`) still PENDING.

### JOSEPH CHOSE OPTION (1) — the fix is implemented, the gate is re-issued, and the re-run is authorized

*"Do option (1), your recommendation, for the three options you gave me."* Option (1) as presented: save
the last-epoch weights, **no estimator redefinition**, needs a re-run. Implemented driver-only.

**The fix.** After `Unfold()`, `train_fullevent_nominal.py` saves `of.step1_models[0]` and
`of.step2_models[0]` to `..._iter<niter-1>_step{1,2}_final.weights.h5` and points
`inference_contract["step2_checkpoint"]` at the step-2 final file, adding `step1_checkpoint`,
`step2_checkpoint_best_epoch` and `checkpoint_semantics`. **`extract_fullevent_fps.py` reads
`step2_checkpoint` and therefore needs no change at all**, so the whole fix lands in one file.

**It saves the trained clones, not the originals** — the trap I recorded before implementing rather than
after. `of.model1`/`of.model2` are assigned once at `omnifold.py:123-124` and never reassigned; training
runs on `clone_model` copies, which do not carry weights. `of.model2.save_weights(...)` would have
persisted a **random initialization**.

**Round-trip guard, exact and free.** Each saved file is loaded back into a fresh clone and every weight
tensor must be bit-identical to the trained object's, else the driver exits rather than writing an
artifact whose weights cannot be reproduced from disk. An empty `step{1,2}_models` list also fails
closed. No forward pass needed; the end-to-end check remains the external `gate_ab_push_provenance.py`.

**The engine is NOT touched.** `omnifold.py` and `net.py` shas are unchanged, which keeps the engine pin
(shared with other lanes) intact *and* keeps `sbatch_powered_closure_budget_probe.sh`'s submission-time
driver pin valid — the closure driver has the same latent defect and I am deliberately leaving it alone
while ep32 (`56431651`) is PENDING, because editing it would kill the queued arm.

**Gate-4 code gate re-issued as `...-20260807.json`, predecessor retired in the same commit.** Exactly two
files drifted and both were re-frozen: `driver` and `launcher_test`. The predecessor got
`status: SUPERSEDED`, `files` -> `files_at_issue`, `sha256` -> `sha256_at_issue`, and `superseded_by`,
per the convention `test_hash_bindings.py::test_superseded_receipts_hold_no_live_bindings` pins. Live
launch-code receipt count held at **2** against `_LAUNCH_CODE_FLOOR = 2`. Verifier: **ALL BINDINGS
INTACT**, 116 OK, 15 shell pins against floor 15, 4 known pre-existing drifts. `test_hash_bindings.py`
6 passed.

`nominal_pet_training_allowed` moves **false -> true**, with Joseph's exact words recorded, and an
explicit note that this does NOT authorize option (2)'s estimator redefinition.

**Two stale blockers in the predecessor corrected rather than copied forward:**
`nominal_has_never_been_trained` was false (it trained as `56415634`), and
`powered_closure_criterion_is_unreachable`'s "the bar sits 16.5 pp ABOVE achievable" is superseded by
BEN-042 — the sampling-only oracle scores 0.9542, so the bar is not unreachable; the estimator is short.
The conclusion (Gate-4 cannot PASS) is unchanged; only the reason. Added the step-1 32% blocker.

**COLLECTION ANNOUNCEMENT: local 730 -> 735 (+5).** All five are
`test_pet_fullevent_nominal_launcher.py::FinalCheckpointIsPersisted`, four static guards plus
`test_the_prefix_source_would_fail`, which reconstructs the pre-fix source and requires every guard to
fire — without it all four could be vacuous (BEN-032/BEN-040 family).

**Suite: 9 failed / 725 passed / 1 skipped, and MY DELTA IS ZERO.** The documented baseline is 7. The two
extra are both in `test_resume_guard.py`, and **every** path they implicate is under
`.claude/worktrees/gbdt-closeout*/` — the concurrent GBDT session's git worktrees, swept up by a
repo-wide shell scan. It even flags `lib/resume_guard.sh`'s own explanatory `#` comment inside the
worktree copy. That is the BEN-032 "scanned the wrong population" family and it will hit the GBDT session
too; the fix is to exclude `.claude/worktrees/` from the sweep. Verified no real repo file is implicated
before claiming my delta is zero.

**Re-run plan, and why the launcher is not being edited.** The launcher deliberately does not pass
`--allow-overwrite`, and both 08-06 products carry completion markers, so `is_complete` would `die`
before the GPU hours (`train_fullevent_nominal.py:349`). Editing the launcher would both destroy the
prior artifact silently and churn a freshly frozen sha, so instead the 08-06 products, their `.done`
markers and `w_nominal/`/`w_floor/` get archived under `superseded-20260806/` with digests verified
before and after the move, and the launcher runs unmodified. `w_nominal/` was already copied off scratch
under memo item 0, so the checkpoints survive independently.

### Re-run SUBMITTED as `56445883`; the worktree false-failures fixed; the 100-rep module reviewed and tracked

**The authorized re-run is queued.** `56445883`, `fe_pet_nom`, PENDING, 12h wall, priority 67679,
submitted `2026-08-07T05:24:27` — every field from `squeue`/`scontrol` in this turn. Watch
`nominal-rerun-56445883` armed (`slurm-job`, `unreliable=0`), action `notify_nominal.sh`, whose three
branches were already proved by execution earlier today; its body file writes to
`/pscratch/sd/j/josephrb/.nominal_notify_body.txt`, outside the product directory, so it cannot make
`is_complete` true. Launcher selftest run first as preflight: **CONFIG GATE PASS**, niter=3, target sha
and size matched.

**The 08-06 products are ARCHIVED, not overwritten.** `superseded-20260806/` now holds both npz, both
`.done` markers, and `w_nominal/`+`w_floor/` (12 checkpoints each). Digests verified identical across
the move — `8d17140f697faca7…` and `28fe004c31dcb414…`, the same values recorded in the earlier quiet
integrity check. The two tracked receipts (`GATE_AB_PUSH_PROVENANCE.json`, `STEP1_DECOMPOSITION.json`)
were deliberately left in place so the findings citing them do not break. The launcher was NOT edited:
it withholds `--allow-overwrite` on purpose, and archiving respects that instead of defeating it.

**The two extra suite failures were not mine, and are now fixed.** Both were in `test_resume_guard.py`
and every path they implicated was under `.claude/worktrees/gbdt-closeout*/` — the concurrent session's
worktrees, swept by a repo-wide `os.walk`. It even flagged `lib/resume_guard.sh`'s own explanatory `#`
comment inside the worktree copy. Excluding `worktrees` narrows nothing real: every file in a worktree
is a checkout of a tracked file the walk already visits at its true path. Verified after: **323 shell
files still swept, 0 from worktrees**, 21 passed. Suite is back to the documented baseline of exactly
**7 failures**.

**`combine_cstat_bkgsub_100rep.py` reviewed and tracked — and it had two gates that could not fail.**
Symmetry tested `sym_err > 1e-30` absolutely; PSD tested `min_eig >= -1e-9 * max(max_eig, 1.0)`, where
the `max(...,1.0)` pins the tolerance to `-1e-9` absolute. On the real products `max|C| = 8.13e-79` and
`max_eig = 2.72e-77`, so both sat ~49 and ~68 orders above what they bound. **Power-proved rather than
argued:** inject an asymmetry of half the largest entry and `sym_err = 1.26e-80` — the old gate does not
fire, the relative one does. The battery would have printed PASS on an arbitrarily wrong matrix. Both are
now relative and still clear the two existing products with margin (symmetry exactly 0.0,
`min_eig/max_eig = -8.4e-16`), so this **tightens a dead gate rather than loosening a live one**. Filed
as **BEN-044** — third instance of this family in two days, after CLM-011's `atol=1e-8`-against-1e-38 and
BEN-042's normalised-vs-absolute headroom.

Also fixed there: `_ND` was hardcoded to an absolute `/pscratch` path, so the module could not be
imported in any other checkout — which is *why* its gates had never been unit-tested. An untestable
module is an unreviewed one. Now resolved from `__file__`.

**COLLECTION ANNOUNCEMENT (supersedes the +5 in the previous entry): local 730 -> 740 (+10).** +5
`FinalCheckpointIsPersisted`, +5 `CovarianceGatesAreScaleAware` — the latter including two explicit power
proofs that the old thresholds were scale-blind. Suite 7 failed / 732 passed / 1 skipped: the 7 are the
documented pre-existing path failures, and my delta is zero.

### Quiet cycle — but I preflighted the one thing that could have wasted the re-run's 6 GPU-hours

No new mail. Both watched jobs still PENDING at 12:32Z from a live `squeue`/`sacct`: `56445883`
(fe_pet_nom, the authorized re-run) and `56431651` (ep32). Nothing finished, so no mail — one already
went out this cycle and nothing new has a verdict.

**The BEN-043 final-save block had never executed, and it runs AFTER the training.** That is the
late-failure shape this campaign keeps paying for: a bug there kills `56445883` having already spent ~3
GPU-hours on the nominal, then again on the floor repeat. The launcher's own selftest cannot cover it —
it is config-gate only and imports no TF.

The risk was specific, not vague: `tf.keras.models.clone_model` **raises on a subclassed Keras model**,
and my block clones `step{1,2}_models[0]`, which is *itself already a clone*, then loads weights into
that second-generation clone. The engine only ever clones a freshly-constructed PET, so "the engine does
something similar, it must be fine" was exactly the reasoning to distrust.

Preflighted by execution instead (GPU, seconds, arch read from the committed contract, no training):

    step2  PET(num_feat=8,  num_evt=2)   clone OK, 96 tensors, 96/96 perturbed, round-trip BIT-IDENTICAL
    step1  PET(num_feat=8,  num_evt=13)  clone OK, 96 tensors, 96/96 perturbed, round-trip BIT-IDENTICAL
    PREFLIGHT PASS

Two anti-vacuity guards in it, because a save/load round-trip is trivially "equal" if nothing happened:
weights are perturbed **off the initializer first** (so a `save_weights` that wrote nothing, or a
`load_weights` that matched nothing, cannot pass by both sides holding the same defaults), and a **fresh
clone that never loaded is required to DIFFER** (so the equality is attributable to the load). Both
fired.

One incidental find: `omnifold` only reaches `sys.path` via `fullevent_fps_dataloader.py:58`, so any
script outside that import chain must insert `omnifold_nn/` itself — worth knowing for future tools that
do not need the 9.9 GB-capable loader.

Committed as `nd-unfolding/pet/preflight_final_checkpoint_save.py`, made path-portable (resolves `ND`
from `__file__`, output dir from `$SCRATCH`) specifically so it does not repeat the BEN-044 defect I
filed against `combine_cstat_bkgsub_100rep.py` in the previous entry.

Everything else verified quietly and unchanged: cluster at `9fbeeaf`, ep32's driver and preflight sha
pins still match the launcher's submission-time values, both watches armed with `unreliable=0`, archived
08-06 products intact.
