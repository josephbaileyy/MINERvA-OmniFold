# PART U — pin 1 (`f4aa0f08`): BLOCK, narrowly, on the enumeration's population

**Owner:** independent-assessment lane. **Subject:** `f4aa0f08` — `nd-unfolding/z_build_path.py` (366
lines) and `nd-unfolding/tests/test_z_build_path.py` (324 lines). **Baseline:** Part T at `7b9214cd`,
pinned at `6f24fb00` before this code existed. **No grade assigned** (`BEN-381`).

## VERDICT ON THIS PIN'S PORTION OF MY SLICE

> **BLOCK — one consequential issue: `MEMBER_LOCAL_TODAY`'s population is selected by a line window
> and omits the two most expensive member-local components.** Everything else in my slice on this pin
> is **READY**: the decoupling is sound, additivity holds, and the suites verify.

---

## U.1 — THE BLOCKING ISSUE: A POPULATION SELECTED BY A 13-LINE WINDOW

`z_build_path.py:105-113` declares `MEMBER_LOCAL_TODAY` with **seven** entries, and **each carries a
line number** — `# :404-408`, `# :409`, `# :410`, `# :411`, `# :412`, `# :413`, `# :414`. The window
is visible in the artifact: the population is *"the variables assigned in `:403-415`"*.

**Measured against the behaviour rather than the window.** `sbatch_finalize_5d_bkgaware_gpu.sh`
contains **eight** `mr_prefix`/`mr_dir_prefix` call sites. **Six** are inside `:403-415`. The other
two are at **`:422-423`**:

    mr_prefix boot_nd_5d
    mr_prefix seedscan_split_5d

**Those are the replica INPUT directories** — the 100 bootstrap replicas and the 24 seedscan splits —
and they are member-prefixed on exactly the same condition as the seven that are listed.

**They appear nowhere in the module.** `grep -ci 'boot_nd_5d|seedscan_split|replica'` over
`z_build_path.py` returns **0**.

**Why this is consequential and not cosmetic — three reasons, ascending.**

1. **They fall in neither returned category.** `enumerate_recomputation` returns `recomputed`,
   `pinned` and a prose `note` (`:130-142`). A component that is member-local and must be *populated*
   is in a third category the function does not have, so the deliverable cannot express it.
2. **`:141`'s note is a universal over the enumerated set only.** Under `PER_MEMBER` it reads
   *"**every** component varies"*. That is true of the seven and silent about the two — the
   comment-says-EVERY-while-the-code-lists-literals shape.
3. **⚠ THE OMITTED TWO ARE THE EXPENSIVE ONES.** `STAT_COV` and `ML_COV` are cheap combines over
   existing replicas; `boot_nd_5d`'s 100 replicas and `seedscan_split_5d`'s 24 splits are the actual
   compute. **An enumeration used to price a member run understates its cost by omitting precisely the
   costly entries**, while including five cheap ones. The requirement's words are *"identify **exactly
   which** other components are recomputed when the estimator baseline changes"*, and the two most
   expensive are absent.

   And `:418-420` keeps `--expected-ids` at the full ranges *"on purpose"* so *"a member with a partial
   replica set must REFUSE"* — so a member either has its own 100 + 24 or the run fails. There is no
   cheap third option that would make the omission harmless.

**The irony, recorded because it is the campaign's standing law.** The module's own header at
`:103-104` warns: *"⚠ `UTHROW` is on it — so under a declared member the UNIFIED-THROW covariance is
member-local too. **It is NOT only the bands, which is what a reader of the COMB line alone would
conclude.**"* It warns, correctly, against inferring the population from a subset of the lines — and
then defines its own population from a **window** of the lines. **The catalogued shape reappears one
layer below where it was catalogued**, which is the fourth instance in this campaign.

**What would clear it:** the two paths named, and placed in whichever category is true of them —
recomputed, pinned, or a third the function does not yet have. **Which of the three, and whether a
third category is warranted, is not mine to choose.**

## U.2 — READY: THE DECOUPLING IS SOUND, AND I CHECKED THE DEFAULTS MYSELF

| claim | verified at `f4aa0f08` |
|---|---|
| membership and block source are independent | `:67` — *"INDEPENDENT of `member_offset` — that independence IS…"*; `is_member` (`:87`) and `blocks_are_shared` (`:92`) are derived properties |
| no default on block source | `:75-76` — `require(self.block_source in BLOCK_SOURCES, f"… there is no default")` |
| sharing is **digest**-bound, not path-bound | `:80-82` — `if block_source == "SHARED_DIGEST_BOUND": require(bool(self.stat_digest) and bool(self.ml_digest), "… Sharing a PATH …")` |

That is the mechanism Part I §I.3 and Part M §M.3's equal-`N` work argued for, and Part T §T.4 is why
it is the only available route: `N = 100/24` is enforced across the whole member family, so **no count
can identify a member** and a digest is the remaining discriminator. **Sound as implemented.**

## U.3 — READY: ADDITIVITY HOLDS AT BOTH LEVELS FOR THIS PIN, AND THE LIVE HAZARD IS CORRECTLY CITED

- **File level, measured here:** `git diff --name-status f4aa0f08^..f4aa0f08` is **two `A` lines, 690
  insertions, zero deletions or modifications.**
- **Behavioural level — mine to check, and it holds trivially:** `z_build_path.py` performs **no file
  I/O**. It imports only `os`, `dataclasses`, `typing`, `numpy` and `z_contract`, and greps for
  `open(` / `TFile` / `RECREATE` / `.Write(` / `json.dump` / `np.save` return **one** hit, at `:355`,
  which is a **comment** citing `SPEC` §1.6's warning. A module that writes nothing cannot overwrite
  anything.
- **So the `RECREATE` / defaulted-`--out` hazards are neither triggered nor mitigated here.** They
  remain live for whichever pin invokes the producers, and the module **cites** them rather than
  claiming to have addressed them — which is the right disposition and the reason Part T's baseline
  is still the thing to diff against later.

## U.4 — READY: THE SUITES, RE-RUN WITH A CONTROL, AND THE SKIP IS BENIGN

Run in an isolated worktree at `f4aa0f08`, **control first**:

| suite | result |
|---|---|
| `tests/test_z_validator.py` **[control]** | **136 passed** — matches its standing claim |
| `tests/test_z_build_path.py` | **30 passed** |
| `tests/test_z_contract.py` | **56 passed, 1 skipped** |

**The coordinator's precision correction is confirmed:** the designer reported *"57 OK"*; 57 is the
**collected** count. A skip is not a pass.

**And the skip is benign and self-documenting**, which I checked rather than assumed:
`tests/test_z_contract.py:628` — *"lightgbm absent from this interpreter — which is itself the finding
recorded in `z_reproducibility`'s docstring."* A declared environmental coverage limit, not a masked
failure.

**My own instrument failed first and the control caught it.** My initial run reported *"no tests ran"*
for all three suites — a can't-look zero, caused by a worktree that had not been created. The control
failing is what distinguished a broken harness from a broken tree.

## U.5 — `S2` NOT TRIGGERED, AND WHAT I DID NOT ASSESS

- **`S2` is held.** The projection maps are not in this pin, so the compose-or-not route is still
  undetermined. Part S §S2 binds only if a map composes single-axis drops.
- **Not assessed:** the 1% threshold (in either direction), terminal handling, `κ`, the mutation
  tests, the claim-scoping / cause-3-amendment question, and the *contents* of the 30 new tests beyond
  their pass count — I verified they run and pass, not that they have power.
- **Still open and undischarged**, per Joseph's standing note: `A-6(a)`, `A-6(b)`, the excluded
  producing execution, and the three-or-four block population.
