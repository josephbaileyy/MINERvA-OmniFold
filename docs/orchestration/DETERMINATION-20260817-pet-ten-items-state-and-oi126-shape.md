# DETERMINATION — PET: the `OI-64/65` renumber is a DENY, one of the ten items is already closed, and the map asks `OI-126` a different question than the row does

**Lane E, 2026-08-17, at `29e1a7c`.** Dispatched by session `personal`: (1) disambiguate `OI-64`/`OI-65`,
(2) re-derive and action the ten "blocked on nothing" items, (3) report on `OI-126` without deciding it.

**Adopts nothing. No compute. `docs/analysis-note/` untouched, not one character. No sbatch, no scancel,
no scontrol. `/pscratch/sd/j/josephrb/gate6traj-reconcile-56847059` not touched — see §2c, where that
prohibition bounds a conclusion.**

**A note on method, stated rather than performed.** My last two tasks predeclared a branch set before
measuring. **This one is a documentary state audit and a branch set would have been ceremony** — there is
no single measurement whose outcome could have been chosen after the fact. The discipline I substituted,
and held to: **every `CLOSED` verdict below is backed by a named commit plus a test run in this turn**,
and every `OPEN` verdict by a file:line that currently exhibits the defect. Where I could not establish a
state, the row says so.

---

## 1. `OI-64` / `OI-65` — **DENY. Do not renumber.** Four independent reasons, any one sufficient.

The dispatch asked me to *"renumber into the correct blocks."* **I am not doing that, and the strongest
reason is that the check meant to police this namespace forbids it in its own failure text.**

**(i) `whose_row.py:623-624` — the message a renumbering committer would be trying to satisfy:**

> `DUPLICATE {i} x{n} -- two lanes allocated it. **Do NOT renumber a row that is already cited
> elsewhere; annotate both and add a waiver with the reason**`

**(ii) The decision was already taken, with reasons, and is recorded in `OPEN_ITEMS.md`'s own header:**
*"The two collided ids are NOT renumbered and are waived by id in `whose_row.OI_ID_WAIVERS`, dated and
with reasons. Both are cited in landed commits and sibling documents; renumbering would silently break
those references (`BEN-216`/`BEN-219`)."* The waivers exist and carry those reasons verbatim
(`whose_row.py:480-485`).

**(iii) The references are real and I counted them rather than trusting the claim.** `git log -S` returns
**8 landed commits** citing `OI-64` and **8** citing `OI-65`; `git grep -l` returns **12+ documents**
including `.githooks/pre-commit`, four `AUTHORIZATION-*` and `FINDING-*` files. Renumbering silently
falsifies every one.

**(iv) It is not ours to decide anyway.** `OI-62(b)` — whether `OI-*` should use lane blocks at all
rather than lane-prefixed ids — is recorded as **formally Joseph's call** and is open.

**Renumbering would also trip the check in the other direction:** removing a duplicate makes its waiver
stale, and `whose_row.py:625-628` fails on a stale waiver *"or it silently permits the next real
collision on that id."* So the requested action fails the gate coming and going.

### 1a. The dispatch's underlying concern is REAL, and the ledger is not where it is unfixed

*"A dispatch naming `OI-64` is ambiguous TODAY"* is correct. **But the ambiguity is not in the ledger** —
each row already leads with `⚠ ID COLLISION` naming the other's subject, which is a working
disambiguation at the point of reading. **It is unfixed in the DISPATCH**, which is not in the repository
and which no committed check can see.

**Proposed, not applied:** a dispatch or document naming a waived id must name the lane and the subject —
*"C's `OI-64`, the deployment-parity check with no caller"* — never the bare id. That is a one-line
addition to the `OPEN_ITEMS.md` header beside the existing waiver note. **I did not add it**, because it
is a convention change to a shared header on the same ground I declined `BEN-381`. **It is also not
mechanically enforceable and I will not pretend otherwise** — a check cannot see a message.

**One hazard for whoever does allocate next**, since the dispatch raised it and it is worse than stated:
`whose_row._committer()` reads `git config user.name`, and **every lane in this repo commits as
`Joseph Bailey`.** So the block arm attributes by an identity that does not distinguish lanes at all —
`OI-126`'s own row says exactly this (*"the id is in the `Joseph / unattributed` block because this lane
commits as `Joseph Bailey` and the table constrains rather than exempts that identity"*). Any new id I
allocated would land in that fallback block regardless of which lane I am. **Recorded, not fixed.**

---

## 2. The ten items — re-derived. One is CLOSED, one has a stale artifact, one cannot ever close.

The dispatch warned ~28% of PET-relevant rows read `OPEN` while closed. **Measured here: 1 of 10 is
closed outright, 1 of 10 is half-closed with a stale supporting artifact, and 1 of 10 has no
closure condition at all.**

| item | declared | **measured** | evidence | what it actually needs |
|---|---|---|---|---|
| **`OI-57`** | OPEN | **CLOSED** | §2a | nothing — close the row |
| `OI-58` | OPEN | **hop 1 CLOSED, hop 2 open + stale artifact** | §2b | the quoting rule; and lane C to banner its JSON |
| `OI-60` | NARROWED, open | **OPEN, confirmed** | `fullevent_fps_dataloader.py:1326-1330` — `meta["bootstrap"]` carries `sig_bootstrap_factor` and `bkg_bootstrap_factor` and **no `data_bootstrap_factor`**, though `data_factor` is computed at `:1321` | the one-line add, plus the array-compare in the replay stage |
| `OI-61` | OPEN | **OPEN** | row states two receipt-vocabulary defects, neither affecting a value | the next Gate-5 launcher run — **not actionable without one** |
| `OI-64` (C's) | OPEN | **OPEN** | deployment-parity check with no caller | §1 first; then a caller |
| `OI-82` | OPEN | **OPEN** | `1.0840529829474115` carried at `pet/inversion_screen.py:52`, `pet/leg_mismatch.py:48`, `pet/push_vs_acceptance.py:53`, and pinned in `tests/test_pet_diagnostic_artifact_identity_guards.py:62` | resolve which measurement it is — **its row says "do not overwrite blind" and a fourth site is a TEST that pins it**, so a blind edit turns a red test into a green wrong one |
| `OI-90` | OPEN | **OPEN** | `RUNS.tsv:296` reads *"50 targets and all data/signal/background factors independently verified"* — the overstatement, verbatim | narrow the cell; **but `RUNS.tsv` is a cross-lane ledger and the row says it is lane-owned elsewhere** |
| `OI-96` | OPEN | **OPEN** | `check_canonical_designation.py:276-287` — its own comment says *"The right instrument is a per-field pin in `verify_hash_bindings.py`, not a count here; that is `OI-96` and is not built"* | **a change to a pre-commit gate (check 6)** — routed, not a free one-liner |
| `OI-12` | OPEN | **OPEN, and correctly latent** | `VALIDATOR-TOLERANCE-UNITS-20260808.md:24-39` — the absolute diagonal tolerance sits ~59 orders below the PSD check, which subsumes it; the audit itself says *"Left to the owning lane"* | relative check + mutation test at real scale — **FPS/Agent C's** |
| `OI-41` | OPEN | **OPEN AND UNCLOSABLE AS WRITTEN** | §2d | re-file as a convention, or give it a closure condition |

### 2a. `OI-57` is CLOSED — and it closed under another item's name, which is why nobody noticed

The row still asserts the live defect: *"`train_fullevent_replica.py:112` copies `source["sha256"]` into
`_verified_input_sha256` without hashing."* **That is no longer true.** At `29e1a7c` the file reads:

```
    source_sha = sha256_file(inputs_npz)                        # :133
    if source_sha != source["sha256"]:            raise SystemExit(...)
    frozen_input_sha = os.environ.get("GATE5_EXPECTED_INPUT_SHA", "")
    if not frozen_input_sha:                      raise SystemExit(...)
    if source_sha != frozen_input_sha:            raise SystemExit(...)
    receipt["_verified_input_sha256"] = source_sha
```

Landed in **`a764a72`**, and it does **more** than `OI-57` asked — the code's own comment says *"(1)
alone is what `OI-57` prescribed"*, and it adds a second binding to the frozen `GATE5_EXPECTED_INPUT_SHA`
that *"was already exported and NO Python read it."*

**The second half of the row is also done.** It required a positive control, because D's probe showed a
**same-size source swap PASSED** where the same mutation on the target two lines away was caught.
`tests/test_gate5_replica_driver.py:193` is `test_source_digest_is_measured_not_copied_from_the_receipt`,
and it does a **same-size** tamper (`tampered[-1] ^= 0xFF`) plus the missing-env-var and wrong-frozen-digest
cases. **Run in this turn: `pytest tests/test_gate5_replica_driver.py` → 5 passed.**

**Why the row survived: `a764a72` is titled *"OI-58 hop 1 fixed on the unpinned side…"*.** The commit
closed `OI-57`'s prescription as a **side effect of another item's work**, and named only the item its
author was thinking about. `git log -S'OI-57'` does return that commit — **so the evidence was one command
away and the row is three days stale.** This is `BEN-113`'s shape inverted: there a commit's message
under-described its diff; here it described its diff accurately and under-described *which ledger rows it
discharged*.

### 2b. `OI-58` hop 2 — and a state artifact that now asserts something false

`docs/orchestration/state/gate5-source-npz-verified-20260813.json` carries a field literally named
**`recommended_repair_not_applied`**, whose value still reads *"Replace `:112` with
`computed = sha256_file(inputs_npz)` … The RECOMMENDATION itself stands unchanged."*

**The repair it recommends landed in `a764a72`.** So the field name and its body are both false as of
2026-08-15, at full confidence, with no banner — while a sibling field
(`CORRECTION_20260813_deferral_reason_withdrawn`) shows the file's author does banner corrections when
they know about one. **`BEN-084`: an artifact asserting the wrong thing beats no artifact for damage.**

**Not edited — it is lane C's file and `OI-57`'s row says so explicitly (*"C's file, C's call"*).**
Routed.

### 2c. One conclusion I cannot reach, and the prohibition is why

`OI-57`'s row records the trap that **the repair reaches production only when `CODE_ROOT` is synced**, and
names `CODE_ROOT` as `/pscratch/sd/j/josephrb/gate6traj-reconcile-56847059` — **a directory I am
prohibited from touching.** So *"is the repaired driver actually what a Gate-5 launch would run?"* is
**not established here**, and I did not read that directory even read-only rather than interpret the
prohibition myself.

**One read-only command settles it, for whoever is permitted:**
`git -C /pscratch/sd/j/josephrb/gate6traj-reconcile-56847059 log --oneline -1 -- nd-unfolding/pet/train_fullevent_replica.py`
— if it does not contain `a764a72`, the fix is on `main` and **not** in production, which is the exact
failure mode the row predicts.

### 2d. `OI-41` has no closure condition and will sit OPEN forever

Its next-action reads *"Correct **future** W-offset citations to use the committed fullcloud projection
artifact."* **No action closes that** — it is a standing rule about writing that has not happened yet, so
the item is permanently open by construction. It is a **convention wearing an item's clothes**, and the cost is not
cosmetic: it inflates the open-item count and it is indistinguishable, in the table, from the nine items
that *can* be finished. Re-file it in the conventions set, or give it a closure condition (e.g. *"the
three existing mis-citations at X, Y, Z are corrected"* — if they exist; **I did not enumerate them**).

---

## 3. `OI-126` — **the map asks a different question than the row does, and the map's binary excludes the row's own leading candidate**

**Reported, not decided.** The dispatch said a reading that changes the decision's shape is high value.
**This one does, and it is a routing defect rather than a physics claim.**

**`MAP-20260817-pet-critical-path.md:80` states `OI-126` as a question about SPREAD:**

> *"Is the p∥ 6–20 GeV **bootstrap spread** **(a)** this estimator honestly reporting instability, so
> `C_stat`'s **large bands** are published as-is, or **(b)** evidence that a Poisson bootstrap of the
> measured leg is not a valid `C_stat` construction…?"*

**`OPEN_ITEMS.md`'s `OI-126` row states it as a question about CONTAINMENT:**

> *"**THE P5A ANNEALED NOMINAL IS NOT INSIDE ITS OWN 50-REPLICA BOOTSTRAP FAMILY, AND THE FAILURE IS
> SPATIALLY ORGANISED.**"* — p∥ < 6 GeV behaves perfectly (median z = −0.13, 4 of 128 cells outside the
> full range); in the 63-cell p∥ 6–20 GeV band **the nominal exceeds ALL FIFTY replicas in 44 of 63
> cells**; at p∥ > 20 GeV **the sign reverses** (44 of 45 cells nominal *below* the family mean); the
> nominal's integral sits at the **98th percentile** of the 50 member totals.

**These are not the same question.** A family can have honest width and still fail to contain its
nominal; a containment failure with a **sign flip across a kinematic boundary** is evidence of an
*offset between two constructions*, not of the family's *width*. **Neither (a) nor (b) is about an
offset.**

**And the row already names a measured candidate that the map's binary cannot express:**

> *"**LEADING CANDIDATE, MEASURED BUT EXPLICITLY NOT ESTABLISHED AS THE CAUSE: the two arms use different
> Stay-Positive backends.**"* — the nominal carries `refinement_backend = 'precomputed:gate2-published-target'`;
> each replica **recomputes** it (`refinement_estimator = 'exact'`, `max_mc_events = 200000`,
> `refinement_random_state = 45`). Other differences are recorded as **RULED OUT**.

**Measured, and bounded:** `grep -in 'backend|stay-positive|containment|outside|percentile'` over the
whole map returns **nothing**. The map never mentions the containment failure, the sign flip, the 98th
percentile, or the backend candidate.

**Consequence, which is the operational point.** A lane dispatched off the map — which is what the map is
*for* — investigates *"is this spread honest?"* and would reach for estimator-stability evidence. The row
says the live question is *"why is the nominal outside its own family, in one kinematic band, with the
sign reversing outside it?"*, whose leading measured candidate is **a construction difference between the
nominal and the replicas.** If that candidate holds, the answer is neither (a) nor (b): it is *"the two
arms are not the same object,"* and `C_stat`'s validity is untouched while its **pairing with this
particular nominal** is what fails.

**I am not deciding it, and I am not claiming the backend explains it** — the row says explicitly that it
is *measured but not established as the cause*, and I did not re-derive any of its numbers. **What I
establish is narrower and checkable: the map's one-line summary replaced the item's question, and the
binary it offers does not contain the item's own leading candidate.** `BEN-383`.

**One thing I checked and will not build on**, because it is my documented failure mode: Gate-6 Leg F's
`VL130` measures a per-bin GPU/process non-determinism floor stratified by occupancy — **2.17%** in the
top occupancy quartile rising to **28.12%** in the lowest — and `OI-126`'s band is plausibly
low-occupancy. **I did not compare them and no one else has** (`git grep -l VL130 | xargs grep -l OI-126`
returns only `OPEN_ITEMS.md`, `CATALOG.md` and the RUN_LOG, none of which compares them). **The two are
not obviously commensurable**: `VL130` is n=4 replicates on a 2,000,000-row subsample at
`bootstrap_seed = −1` over 259 bins, and `OI-126` is 50 members on the full data over 257 quotable cells.
**Naming a comparison is not making it**, and asserting a floor explains a band without establishing they
are the same quantity is exactly the asymmetric comparison I keep having to catch in my own work. Offered
as a question for the owning lane, with both sides named.

---

## 4. What I did NOT do

* **No renumbering** (§1), **no edit to lane C's state JSON** (§2b), **no change to
  `verify_hash_bindings.py`** (`OI-96` is a gate change), **no edit to `RUNS.tsv`** (`OI-90` is
  cross-lane), **no touch of `CODE_ROOT`** (§2c).
* **No compute of any kind.** Nothing here needs a run. **Flagged with its unit, per the dispatch:**
  `OI-96` and `OI-12` are CPU-only code changes; `OI-61` needs a **GPU** Gate-5 launcher run it cannot be
  done without; `CSTAT-O2a` is **released and superseded** — `SPEC:845-868` records that Gate-6 Leg F
  already pins the no-draw floor, so O2a is now *"one comparison rather than a fresh measurement."*
* **`OI-126` not decided**, and its leading candidate not adjudicated.
* **I closed one row** — `OI-57`, on evidence stated in §2a. Every other verdict in §2 is reported, not
  actioned.
