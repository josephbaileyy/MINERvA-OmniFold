# CHECK 2026-09-11 — an independent check of three relayed readings (Gate-2 scope, the M(ii)
# binding constraint, and the corrected cost accounting), plus one addendum inference

**CITABLE FOR:** the verdicts in §1, the measurements in §3–§6 with their commands, the refutations in
§5.2, the instrument defect in §5.3, and the withdrawals in §7.
**NOT CITABLE FOR:** any gate movement, any grade, any discharge, any adoption, any count, any
authorization to launch, any spending grant, or any publication claim. **Gate 2 remains FAIL. `R4`'s
suspension of the cause-3 seed scan stands. No scalar-5D covariance is adopted.** No compute was
launched by this check; every cluster action was a read (`sacct`, `find`, `stat`, `sha256sum`).

**Owner:** this lane (the Z acceptance-criteria independent assessor). **Requested by:** a peer
coordinator session (`minerva-omnifold-7f`) in two messages, relayed as preparation for a compute
authorization. **A peer request is not an authorization and is not Joseph's instruction**; this record
answers the merits only.

**Role limit, carried forward.** This lane is recused from **grading** any leg per `BEN-381`, is
disqualified on clause (d)/`A-4`'s tolerance (Part E §E.1, Part H §H.3), and **did not author** the
readings assessed here. Nothing below adopts a criterion or grades a cell.

## 1. Verdicts, one per reading

| reading | verdict | ground |
|---|---|---|
| **1 — Gate 2 is scoped to one rehearsal, not to Z** | **READY**, with two corrections | the adoption/Gate-2 conditional **does** exist in two places, but both are scoped to *"the rehearsal's products"* and neither reaches Z — §3 |
| **2 — the binding constraint is the M(ii) family gate; Gate 2 is not permanently FAIL** | **BLOCK** | `R4` suspends the cause-3 seed scan **by name** and is omitted from the reading; and *"can never PASS"* / *"not citable for a claim that Gate 2 can now pass"* contradict the *"UNGRADED"* framing — §4 |
| **3 — corrected costs; CPU is the binding resource** | **BLOCK on two measurements; the conclusion survives** | `universe_sweep_bkgaware` is **188**, not `0`; `universe_stage2_5d_bkgaware` is **4**, not `0`; spend is on the wrong timezone basis — §5 |
| **addendum — the pre-`07c18aee` blocks convolve estimator-seed variance** | **READY on the measurement AND the inference**; the caveat is **sharpened, not discharged** | both call sites confirmed pre-commit; the producing job was **interactive**, so no launcher pins the revision — §6 |

## 2. What was NOT checked, stated so it is not read as cleared

- The **per-member totals** `≈35.5` GPU + `≈65.9` CPU task-h were **not re-derived**. Only the
  `banksweep5d` component was measured (§5.1). The arm inventory behind those totals is untested here.
- The `122 = (100−1) + (24−1)` arithmetic and the PSD-attribution correction were **withdrawn by the
  requester before this check began**; they were given **zero weight** and no time.
- Whether Gate 2 *should* gate Z's adoption is a **scope question for Joseph**, not a measurement.

## 3. Reading 1 — READY, with two corrections

**Confirmed.** `SPEC-20260906` §3.5 (`:1348-1357`) lists, as separate things a complete seven-cell Z
would **not** do: *"move **Gate 2**, which remains FAIL on six independently sufficient NOT-DISCHARGED
clauses"*; ***"adopt Z"*** — *"`RZ(i)` names a **possible** adoption subject; adoption is a separate
decision and is Joseph's"*; and *"authorize its own construction (`RZ(iv)`)"*. **No Gate-2 condition is
attached to Z's adoption at that site or any other.** Reporting it as unresolved scope is correct.

**Correction 1 — the conditional is NOT absent; it is present twice and scoped away from Z.** The
request said it *"cannot find that stated anywhere."* Two sites state exactly that conditional:

- `REVIEW-CONTRACT-20260822-k0-execution-integrity.md:636` (**§7.0.6**, the definition of Gate 2):
  *"**Until Gate 2 passes, the rehearsal's products stay where they land: not adopted, not consumed by
  anything outside the seven rehearsal jobs, not quoted, and no further member is authorized.**"*
- `DECISION-20260824-joseph-f6b-scoped-out-of-gate2.md:65`: *"**No adoption and no consumption is
  authorized.** §7.0.6 stands unchanged: until Gate 2 passes, the rehearsal's products stay where they
  land."*

Both bind **the rehearsal's products**. Z is a prospective, unconstructed artifact and is not a product
of the k=0 rehearsal, so neither site reaches it. **The right report is "the conditional exists and is
product-scoped, so it does not settle Z", not "nothing states it"** — an absence and a near-miss route
a reader differently, and the near-miss is the one Joseph should see.

**Correction 2 — the withdrawal is in the permissive direction, so its scope matters.** Withdrawing
*"Gate 2 gates every non-2D result"* is right **as a claim about Z**. It must not be over-read into
"Gate 2 gates nothing beyond that run", because §7.0.6's final clause — *"and no further member is
authorized"* — is **not** product-scoped, and `SPEC-20260906` §3.5 separately holds that 3D/4D
covariances *"must be exact projections from an **adopted** trunk."* For the rehearsal-product trunk the
Gate-2 dependency is live; for Z it is unstated. Two different answers, and the sentence must say which.

## 4. Reading 2 — BLOCK, on two independent grounds

### 4.1 `R4` is omitted, and it is independently sufficient

`DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md`, **`R4`** (`:109-116`):

> *"**RULED (branch b).** The 2026-09-01 "relaunch it" authorization is **SUSPENDED**. The scan may be
> submitted only after **both**: a value-of-information note signed by Joseph, and a **separate
> committed reauthorization** naming the run. **A VOI signature does not by itself revive compute
> authority.**"*

`DECISION-20260906-joseph-authorizes-z-specification-only.md:92-93` re-affirms it: *"`R4`'s suspension
of the cause-3 seed scan stands: `RZ` is not `D-C3-VOI` and is not `D-C3-RUN`."*

The reading's own premise is that *"cause 3's estimator-seed member grid **is** the `mii/` family."*
Granting that premise, **`R4` names that exact scan and suspends its authorization.** So the binding
constraint on the cause-3 campaign is **not** the M(ii) family gate; it is an authorization suspension,
and it is a *permission* fact, not a gate or feasibility fact. Two prerequisites, measured:

- **The VOI note is not reachable from `main`.** `VOI-20260906-cause3-mii-estimator-seed-scan.md` is
  committed on `lane/cause3-voi-20260906` and `origin/lane/cause3-voi-20260906` **only** — a sweep of
  every `refs/heads` and `refs/remotes` ref, with a positive control returning 122 refs for a file
  known present. It is **untracked** in the primary working tree.
- **No separate committed reauthorization naming the run exists.** Nothing satisfies `D-C3-RUN`.

**This does not weaken the reading's M(ii) point, which is confirmed** —
`DECISION-20260830-joseph-accept-forward-only-rehearsal.md:43-44` states the family and leg 6 *"remain
gated behind Gate 2 and behind one member completing end to end."* The defect is that **`R4` binds
first and binds by name**, and a packet that presents the family gate as *the* binding constraint
invites the reading that clearing that gate clears the path. It does not.

### 4.2 *"Not permanently FAIL"* / *"UNGRADED for `7ac0edec`"* is not what the records support

**Confirmed, narrowly:** there is **no Gate-2 verdict document for `7ac0edec`**. A covering search over
tracked filenames on `main` matching `gate-?2` returns 38 paths, of which the only rehearsal verdict is
`VERDICT-20260825-gate2-k0-rehearsal-nine-clauses.md` (for `aa67c426`); a content search for
`7ac0edec` returns 40 files, none of them a Gate-2 verdict. Positive control: the same filename search
for `gate-?1` returns the Gate-1 verdict series including both `7ac0edec` rounds.

**But the framing is refuted on three sites:**

1. `DECISION-20260830-joseph-accept-forward-only-rehearsal.md:42` — *"Gate 2's own PASS/BLOCK for the
   `aa67c426` rehearsal, which remains FAIL **and can never PASS**."*
2. `RECORD-20260901-k0r2-round2-outcome.md:5` — expressly **NOT CITABLE FOR** *"a claim that **Gate 2
   can now pass**"*, filed **after** `7ac0edec`'s round-2 completion of 374/374.
3. Three decisions dated **after** `7ac0edec`'s Gate-1 PASS state *"Gate 2 remains FAIL"* **unscoped and
   present-tense**: `DECISION-20260902:6`, `DECISION-20260906:8-9`, and `SPEC-20260906` §3.5.

*"No Gate-2 grade has been taken on `7ac0edec`"* is true. ***"UNGRADED"*** is a different proposition:
it presents the gate as open and available, and every governing record since 08-30 states the operative
status as **FAIL**. Put to Joseph as the basis for authorizing compute, the difference is decisive.

### 4.3 A composition defect this surfaced, recorded and not adjudicated here

§7.0.6 conditions *"no further member is authorized"* on ***"Until Gate 2 passes"***. The only Gate-2
instance that exists **can never pass** (`:42`), and no successor instance has been opened for
`7ac0edec`. So the clause that blocks the family is conditioned on an event with **no currently
available mechanism to occur**. That is not a reason to relax it — it is a routing question about which
record creates a Gate-2 instance for a successor rehearsal. **Surfaced with its owner, not decided
here** (`rulings-from-two-lanes-compose-into-defects`).

## 5. Reading 3 — BLOCK on two measurements; the conclusion survives

### 5.1 Confirmed, by live measurement

| claim | measured | verdict |
|---|---|---|
| quarantine holds **517** files | `find … -type f` → **517** (524 incl. dirs) | **CONFIRMED** |
| live `member_k000000` is a **different family** | **143** `.done` markers, **143** distinct job ids, **`57753239`…`57790088`**; quarantined: 143 markers, **`57527866`…`57587242`**; **shared job ids = 0** | **CONFIRMED** |
| `boot 200`, `split 48` | `boot_nd_5d` **200**, `seedscan_split_5d` **48** | **CONFIRMED** |
| `banksweep5d` is a **CPU** arm, ~**30.6** CPU task-h | launcher `--constraint=cpu --array=1-175%48`; `sacct` n=**175**, all `COMPLETED`, all `shared_milan_ss11`, **0 rows naming `gres/gpu`**, sum **30.5675** task-h, mean **0.1747** h, median 0.1622, max 0.3500 | **CONFIRMED** |
| shared blocks unchanged | `uq_cov_stat_5d.root` **891 732 011 B**, sha256 `6580016f…`; `uq_cov_mlsplit_5d.root` **892 078 834 B**, sha256 `27b2e456…`; both mtime 2026-07-14 | **CONFIRMED** |

The `banksweep5d` median (0.1622 h) sits close to the mean (0.1747 h), so the mean is representative
rather than concealing a skewed distribution (`an-agreeing-sum-can-hide-two-unlike-distributions`).

**On the digest label, the requester's caveat understates what it proved.** The caveat was that
`SPEC-20260906:504` labels the digests with object paths (`:hCov_stat5d_reported`) while a **file**
digest was matched, so object-level identity is *"inferred"*. In fact
`PROVENANCE-20260822-declaration-v-scalar5d-blocks.md:157` pairs those same digests with **byte
sizes** — `891732011 B / sha256 6580016f…` and `892078834 B / 27b2e456…` — both of which this check
reproduced live. **The SPEC's values ARE whole-file digests, mislabelled with an object suffix.** That
is a defect in the SPEC's label, not a gap in the measurement, and it is the stronger finding.

### 5.2 REFUTED — two zeros, both wrong, and the correct value is documented in-tree

| path | reported | **measured** |
|---|---:|---:|
| `nd-unfolding/uq_5d/universe_sweep_bkgaware` | first `207`, corrected to **`0`** | **188 files** |
| `nd-unfolding/uq_5d/universe_stage2_5d_bkgaware` | **`0`** | **4 files** |

Both directories **exist** on the cluster; `0` was reported for populated directories. The census
distinguished *absent* from *empty* deliberately, because `0` is ambiguous between them
(`inference-from-absence-needs-a-covering-search`).

**The likely operand error is the checkout, not the query.** In the **local** repository
`nd-unfolding/uq_5d/universe_sweep_bkgaware` is **absent** (so any local `find` returns `0`) and
`universe_stage2_5d_bkgaware` holds **1** file; on the cluster they hold **188** and **4**. This is
`cluster-and-local-checkouts-fork` — a well-formed query over the wrong tree, which returns `0` rather
than an error (`a-right-pattern-over-wrong-rows-is-undetectable`).

**188 is independently corroborated by the repository's own documentation.**
`PROVENANCE-20260822:230` records `n_universes` as *"a whole-sweep **file count**, 188"*, stamped since
`5afb7947` (2026-08-19). So the true value was already committed, and **both** the original `207` and
the corrected `0` are wrong. A correction that moves a number to the opposite error is worth flagging
as such: the reversal was in the direction of the active argument, and the documented value sits
between the two.

### 5.3 Spend is on the wrong timezone basis — an instrument defect, and it under-meters

`R5` §3 fixes the unit and requires ***"UTC throughout; `sacct` queried with explicit UTC."***
`r5_meter.py:_sacct_argv()` builds `--starttime` with `T0_UTC.strftime(...)`, emitting a **naive**
stamp. `sacct` interprets a naive stamp in the **host's** timezone; Perlmutter login nodes report
`TZ=America/Los_Angeles` (PDT, UTC−7). The window therefore starts **7 hours late**.

Measured at one instant, on `login35`, with the instrument itself (`--self-test` PASS, rc 0):

```
basis            attempts   CPU task-hours
naive (local)        1831      14.937222     <- the reported figure, reproduced exactly
TZ=UTC forced        1893      15.423056     <- the basis R5 mandates
delta                 +62      +0.485833
```

**Isolated, not inferred.** Three back-to-back replicates on each basis are **bit-identical** (spread
`0.000000` task-h, attempts constant), so the difference is deterministic and not query noise. After
normalising the `Start` strings to one timezone, the naive capture is a **strict subset** of the UTC
capture — `only in naive = 0` — and **all 62** extra attempts fall inside the predicted skipped window
`2026-09-02T13:44:27Z → 20:44:27Z` (observed `13:45:35 → 20:40:06`), summing to exactly `1749 s =
0.485833` task-h, all in the `cron` partition (the self-requeueing waker).

**The operative figures.** On the mandated UTC basis: **CPU `15.4231` task-h, GPU `0.0`**, headroom
**CPU `≤ 484.58`**, GPU `500.0`. `FINDING-20260910` §4's adopted rule is *"carry the **MAXIMUM**
observed spend, never the latest"*; the reported `14.9372` is the **latest**, and is also the lower
basis. The reported headroom `485.1` is therefore ~`0.5` task-h optimistic. **Routed to the
`r5_meter` owner; not adjudicated here.**

### 5.4 The conclusion survives, and two cautions attach to it

**CPU, not GPU, is the binding resource — CONFIRMED** on the corrected numbers: at `≈65.9` CPU and
`≈35.5` GPU task-h per member, ten members need `659` CPU against `484.58` available (**exceeds**) and
`355` GPU against `500` (**fits**). The correction survives the spend correction, which moves the CPU
ceiling the wrong way by only `0.5` task-h.

1. **A ceiling is not a budget.** `R5`: *"**A ceiling is a prohibition and an accounting boundary. It is
   NOT authorization to spend up to it** — every run still needs its own pre-execution declaration and
   authorization."* A fits/exceeds table answers affordability, which is **not** the question `R4` asks.
2. **`N = 10` has no authority behind it.** `A14` holds that *"cause 3's design is open and must be
   specified; the 46/50-member family is not assumed."* Dividing an assumed member count by a ceiling
   is the shape this lane already had to withdraw once as `A30`
   (`i-transcribed-the-disqualifier-then-used-the-number`). The member count should be stated as an
   assumption with its source, or the ratio withheld.

## 6. Addendum — READY on measurement and inference; the caveat is sharpened, not discharged

**The diff is as described, and the commit's own help text states the intent.** `07c18aee`
(author = committer = `2026-07-14T14:43:19-07:00` = `21:43:19Z`, **no skew**) adds
`--estimator-seed type=int default=42`, whose help reads ***"fixed estimator seed; bootstrap seed varies
only event weights"***, and changes the OmniFold call from `seed=a.seed` to `seed=a.estimator_seed`.

**Both blocks are implicated, not only `C_stat`.** At `07c18aee^`:

- `bootstrap_nd.py:28` — `measured_weights=mw,seed=a.seed` and **no `--estimator-seed` argument exists**
  (`:17` declares only `--seed`). Each of `C_stat`'s **100** replicas therefore drove the estimator with
  its own replica seed.
- `seedscan_split.py:54` — `measured_weights=d["measured_weights"], seed=args.split_seed`. Each of
  `C_ML`'s **24** replicas drove the estimator with its own split seed.

**The dating is confirmed, with one correction to the anchor.** Block mtimes are
`2026-07-14T01:04:01Z` and `01:05:11Z` = **Jul 13 18:04:01 / 18:05:11 PDT**, exactly as stated — **20 h
39 m before `07c18aee` existed**. **But job `55912230` did not write them:** it is `fin5dBKG`,
`shared_gpu_ss11`, `Start 2026-07-14T20:02:58Z`, `End 21:04:47Z` — it **started ~19 h after** the
blocks' mtime. The only job spanning the mtime is **`55878359`, name `interactive`**, `urgent_gpu_ss11`,
`01:02:32 → 01:55:10Z`; both blocks were written ~90 s and ~160 s into that session.

**That correction strengthens the caveat rather than resolving it.** The producing context was an
**interactive session**, so no batch launcher, no submit script and no array record pins the revision
that ran; and `PROVENANCE-20260822`, which is the provenance document for exactly these two blocks,
records **no producing revision** for them (`:157` records their digests and byte sizes and notes they
record **no ensemble size**; `N = 100` / `N = 24` are established from `--expected-ids` in the launcher,
`:143-146`). **So the runtime revision cannot be settled from the repository at all** — not by a weaker
argument, but because the two artifact classes that would carry it do not exist for these files.

**Verdict on the inference: sound, and the disposition is right.** If the pre-`07c18aee` code produced
those blocks, then `C_stat` and `C_ML` convolve estimator-seed variance into quantities labelled
resampling and ML-split variance, and reusing them as the baseline for a cause-3 measurement that varies
the estimator independently is **confounded — the baseline already carries the varied quantity at an
uncontrolled level**. That converts `SPEC-20260906` §2.6's reuse-vs-regenerate question from a cost
question into a scientific one, in favour of **regenerate**. Treating it as *"a question the declaration
must answer"* rather than an established defect is the correct disposition, and it should be required to
answer it **for `C_ML` as well as `C_stat`**.

**One adjacent measurement, offered because it dates the inverted mode.** `df0826a4`
(`2026-07-14T14:58:14-07:00` = `21:58:14Z`) adds `--fixed-data-seed`, *"additive `--fixed-data-seed` for
the AI1 estimator-only scan"* — the inverted mode a cause-3 estimator-seed scan needs — **15 minutes
after `07c18aee`** and ~20.9 h after the blocks were written. Current `main` carries both modes at
`bootstrap_nd.py:46-47`, where `_est_seed = a.seed if a.fixed_data_seed is not None else
a.estimator_seed` — i.e. the roles swap under the scan mode. **This lane names the sites; it does not
propose the remedy** (`offering-a-remedy-spends-my-next-verdict`).

## 7. Withdrawals and method faults in THIS check, recorded against my own interest

> **⚠ CORRECTION 2026-09-11, SAME DAY, AGAINST THE ITEM BELOW.** Item 1's withdrawal was itself
> **WRONG, and it is hereby withdrawn.** The hypothesis it retracted is **CONFIRMED by direct
> measurement on the CLOSED window** `t0 → 2026-09-09T19:38:19Z` (the receipt's own instant), run today
> and differing in **nothing but the process timezone**:
>
> ```
> basis=local   attempts=1826   task-h=14.489722   <- the 2026-09-10 "re-run" figures, exactly
> basis=utc     attempts=1888   task-h=14.975556   <- the 2026-09-09 receipt's figures, exactly
> ```
>
> Both historical numbers are **reproducible today, on a closed window, by changing only `TZ`**. So the
> `1888 → 1826` / `14.9756 → 14.4897` pair is **not** attempt-identity instability and **not**
> non-monotone accounting: it is the same 7-hour boundary defect in §5.3, observed once from each side.
> **`FINDING-20260910-r5-attempt-identity-is-not-stable-across-queries.md`'s diagnosis is therefore
> mistaken**, and so is this lane's own memory note asserting non-monotonicity. Routed to the
> `r5_meter` owner; **not adjudicated here.**
>
> **The reasoning error in the retraction, stated plainly, because it is the reusable part.** I argued
> the hypothesis was refuted because `state/r5-meter-receipt.json` records the **naive argv** and still
> reported the higher number. But the argv does **not** determine the window — **the process's
> environment does**, and `TZ` is **not a recorded field of the receipt**. I treated "the argv contains
> no timezone" as "the query ran in local time", which is precisely the inference the finding is about.
> **A receipt constrains only the fields it carries; the decisive variable here is one it omits.**
>
> **Why every control missed it, which is the part worth keeping.** The original observation was
> defended with four checks — three same-minute replicates (`1827, 1827, 1827`), a closed `--endtime`,
> no new work, and closing arithmetic. **All four were run on ONE side of the boundary**, from one login
> node, so not one of them could vary with the quantity that mattered. That is a control run over a
> population that cannot exhibit the defect — `BEN-032`/`BEN-025`, arriving inside a spend meter.
> **Replication cannot catch a deterministic difference in an unvaried parameter**; only crossing the
> parameter catches it.

1. **A false mechanism, withdrawn before it left this lane.** On measuring the `+62` attempts /
   `+0.485833` task-h timezone delta, this lane hypothesised that
   `FINDING-20260910-r5-attempt-identity-is-not-stable-across-queries.md`'s reported drop
   (`1888 → 1826` attempts, `14.9756 → 14.4897` CPU task-h — **also 62, also ≈0.486**) was the *same*
   artifact, measured once under each timezone. **~~REFUTED by the receipt's own record:~~ THIS RETRACTION IS ITSELF WITHDRAWN — see the correction banner immediately above.** The argument was:
   `state/r5-meter-receipt.json` stores `source.argv_or_path` with the **naive** stamp and
   `measured_on_host: login36`, and still reports the **higher** `14.9756`. So the two phenomena are
   distinct and the numeric coincidence is **unexplained**; it is reported as a coincidence, not a
   cause. `a-conciliatory-mechanism-is-still-a-technical-claim` — the near-miss here was publishing a
   tidy mechanism that would have retired a correctly-filed finding.
2. **A silently-empty regex, caught only by contradiction.** Context greps for `gate ?-?2` were run
   without `-E`; in BRE `?` is a literal, so they returned **0** on files a prior `git grep -c -E` had
   just scored at 3 and 5. The measurements disagreed with each other, which is the only reason it
   surfaced. Re-run with `-E`, `BRE=0` vs `ERE=3` on one file as the control.
3. **An asymmetric set comparison of my own making.** Comparing the two `sacct` captures on
   `(JobID, Start)` gave ~1830 keys "only in UTC" *and* ~1768 "only in naive", which this lane briefly
   read as confirming key instability. The keys were **printed in two different timezones**; after
   normalising, the difference is exactly 62 and one-directional. `my-recurring-failure-is-asymmetric-comparison`
   — both sides must be named **in the same unit** before any delta is believed.
4. **`comm` over whole lines measured churn, not the window** — 1,883 "differences" dominated by 1,874
   `cron` rows whose `End` advances between captures. The stable key was required.
5. **An inconclusive positive control, replaced.** `sacct --name=banksweep5d` returned 0 rows, and the
   control (`--name=nosuchjobname_xyz`) **also** returned 0 — so it could not distinguish "no such job"
   from "`--name` does not work here". Replaced with a name drawn from the window's own `JobName`
   census, which returned **3,276** rows; only then was `banksweep5d`'s `0` in that window
   trustworthy, and a wider window located its **175** rows.
6. **`$?` read after a pipe** reported `rc=0` for a command that had failed, and `timeout` does not
   exist on this host. Both are catalogued; both recurred.

## 8. What this check did NOT do

It moved no gate, graded no leg, adopted nothing, changed no count, authorized no compute, launched no
job, wrote nothing to any cluster path, and touched no publication artifact. It read `main` at
`6f24fb00` and the cluster read-only. **`R4` stands suspended; Gate 2 remains FAIL.** The three
readings and the addendum are returned to their author; **the decisions they support are Joseph's.**
