# The short methods paper: pending variants (2026-11-09)

**Recorded by** `director-helper-3`.

**How it works.** Every sentence that depends on a pending verdict is written once per class. The keys, their class
sets and their groups are in `make_values_fived16.py` (`PENDING`, `PENDING_GROUPS`).
- **In TeX:** `\fvgroup{g}{…}` prints one `[PENDING: …]` until group g's record lands. Inside it,
  `\fvcase{key}{class}{text}` prints `text` only when `key` has that class.
- **To fill a group:** pin the record's readout in `READOUTS` and give every key of the group its class in `VERDICTS`.
  `pending_lines` refuses a group that is only partly filled, and refuses a class that isn't declared.
- **The checks** (`check_round.py`):
  - 1: each paragraph's variant set equals the declared set, minus the EMPTY classes below;
  - 2: no variant prints a digit;
  - 6, `--fill-test`: the paper builds with every key at each class.

**What is not decided here.** The wording of each variant is a draft for the PRD-referee read and Joseph, like every
sentence of the paper. Filling a group needs that group's record and its CITABLE FOR; it needs no new prose.

**The class sets, and the lines that define them.** FD-PRR's paths are under
`state/measurement-paper/5d-community-20261024/`, read at main `c120e0d07`.

| key(s) | classes | source | sites |
|---|---|---|---|
| `prr-pr1-{F1..F4}-{gibuu,q3}` | reduces, increases, both, no-effect, undefined | FD-PRR §5.1, `:287-292` | Table 1 (printed as words) |
| `prr-pr2a-{gibuu,q3}` | less, more, same, undefined | FD-PRR §5.2, `:297-298`; "undefined" is what `prr_read.ibu_class` emits when ρ is undefined (`nd-unfolding/prior_retention/prr_read.py` @ `cf76aec7`, `:308-311`) | §5.3; abstract (gibuu) |
| `prr-pr2b-{gibuu,q3}` | falls, rises, flat, undefined | FD-PRR §5.2, `:299-300`; "undefined": `prr_read.ibu_k_class` @ `cf76aec7`, `:314-317` | §5.3 |
| `prr-pr3-any`, `prr-pr3-ibu` | clears, not | FD-PRR §5.3, `:307-310` ("clears / does not clear at these truths", the director's ruling 2) | §5.3 |
| `prr-label-{fir,info,impl,obs,stat,unattr}-{gibuu,q3}` | holds, not (EMPTY: not) | FD-PRR §5.4, `:321-332` | §5.3 |
| `prr-pr3-levels` | printed value (the levels that clear) | FD-PRR §5.3 | §5.3 |
| `ll5d-campaign` | graded, gate-failed, offset-stopped, stop | LL5D §5.2 `:427` (gate); §5.3 `:439-440` and §11 `:692` (the clipping-offset routing to Joseph, when the decision after it stops the test); §5.1 `:333-335` and `:684` (the STOP triggers). What follows a STOP is decided after it (`:66-71`; `DECISION-20261108-joseph-ll5d-stop-rule.md:28-35`) | §6.3; Table 1 |
| `ll5d-route` | direct, offset-proceeded, repaired, na (EMPTY: direct, na) | how a graded campaign got there: directly; past the offset routing by a decision to proceed (`:439-440`); or with a repair chosen after a STOP was seen, which the paper discloses (`:71`; the stop-rule decision item 4). na: not graded | §6.3 |
| `ll5d-stop-check` | printed value (the STOP's check) | `:333-335`, `:684` | §6.3 (stop; repaired) |
| `ll5d-{g18,ar23}-{minus2,all}` | covers, under-cells, under-joint, under-joint-only, invalid, na (EMPTY: na) | LL5D §6, `:473-475` | §6.3; Table 1 (printed through `WORDS`) |
| `ll5d-{g18,ar23}-{minus2,all}-{weak,over,clip}` | none, some, na (EMPTY: none, na) | LL5D §6: weakened passes `:478`; over-coverage, reported and not a failure, `:477`; "the flag may be the clipping artefact", which cannot un-flag, `:480-481`. na on an invalid or ungraded reading; clip is some only on a reading with a flagged cell | §6.3 |
| `ll5d-{g18,ar23}-{minus2,all}-{weak,over,clip}-cells` | printed value (the cells) | the same lines | §6.3 |
| `ll5d-{g18,ar23}-{minus2,all}-cells` | printed value (the flagged cells) | LL5D §6, `:474` ("each cell is named") | §6.3 |
| `ll5d-abstract` | both-cover, both-cover-bands-under-{one,both}, both-cover-bands-invalid-{one,both}, one-under, both-under, invalid-one-covers, invalid-one-under, invalid-both, stopped-early, stopped-offset | derived by `make_values_fived16.ll5d_derived()` (rule below); `pending_lines` refuses a filling that disagrees | abstract |
| `ll5d-status` | covers, under, invalid, stopped | derived the same way | Table 1's status (its caption's words) |
| `vhalf-outcome` | none-fail, some-fail | `DECISION-20261109-joseph-bias-half-rule.md` item 1, `:31-35` | §5.4 |
| `vhalf-n-{valid,notvalid,notassessed,unresolved}`, `vhalf-cells-notvalid` | printed values | the same item, and item 3, `:38-40` | §5.4; Table 1 |

**Derived classes, stated before any result is read:**
- **`under-cells` and `under-joint`** split LL5D's single UNDER-COVERS class (`:474`), using what that class already
  names: "each cell is named, with whether the joint fraction is under too".
  - `under-joint`: the joint fraction is under.
  - `under-cells`: only cells are flagged.
- **`under-joint-only`** (round 6 pre-read): the joint fraction is under and no cell is flagged, which `:474` allows.
  `under-joint` would print an empty cell list.
- **`na`:** the per-tune keys, their flags and `ll5d-route` take `na` exactly when `ll5d-campaign` is not `graded`;
  a flag is also `na` on an `invalid` reading. Their sentences sit inside the `graded` variant, so `na` prints nothing.
  `ll5d_derived()` asserts all of this.
- **`ll5d-abstract`** (`ll5d_derived()`; round 6 pre-read, the director's items 3-5):
  - `stopped-offset` if the campaign is `offset-stopped`, and `stopped-early` if it is `gate-failed` or `stop`;
  - if both primary keys are `covers`: `both-cover-bands-invalid-{one,both}` if a with-bands key is `invalid`, else
    `both-cover-bands-under-{one,both}` if one is `under-*`, else `both-cover`;
  - `invalid-both` if both primary keys are `invalid`; `invalid-one-under` or `invalid-one-covers` if one is, by the
    other's class;
  - `both-under` if both are `under-*`, else `one-under`.
- **`ll5d-status`:** `stopped` if not graded; else `under` if a primary key is `under-*`, else `invalid` if one is
  `invalid`, else `covers`.
- **`prr-pr3-any`:** `clears` if some level is "clears at these truths" in FD-PRR §5.3. The IBU is not counted here;
  its reading is `prr-pr3-ibu`.

**The EMPTY classes** print nothing by design. `check_round.EMPTY` subtracts them from the variant sets it requires.
- **The `not` of each label (V-P5):** a composite label that doesn't hold prints no sentence. The labels aren't
  exclusive (FD-PRR §5.4: "several can hold at once, and none excludes another"), so each label is its own sentence.
- **The `na` of the per-tune LL5D keys (V-L2),** as above.

**The variant rows.** Each row's text is in `paper_body.tex` or `main_paper.tex`, at the site named.

| id | site | key(s) | what each class prints |
|---|---|---|---|
| V-A1 | abstract | `prr-pr2a-gibuu` | one sentence per class: "retains less / more of the prior than the estimator"; "retains a share of the prior that differs from the estimator's by less than a bar fixed in advance"; "is not compared with the estimator, because a retained fraction is undefined there" |
| V-A2 | abstract | `ll5d-abstract` | one full sentence per class. The covering classes name the object, the procedure's covariance rebuilt at each tune, and the primary variant, and end "the result concerns the procedure's covariance at those tunes, not the reported intervals at the data" (`:52`, `:768-769`, R5 `:512`). Pending Joseph (#993 item 4) |
| V-T1 | Table 1 | `prr-pr1-*`, `prr-pr2a-*` | the class words |
| V-T2 | Table 1 | `vhalf-n-*` | the four counts |
| V-T3 | Table 1 | `ll5d-*-minus2`, `ll5d-*-all` (through `WORDS`), `ll5d-campaign`, `ll5d-status` | graded: the four readings in words; otherwise "Stopped …"; the status Covers / Under-covers / Invalid / Stopped. No raw class name prints (check_round check 8) |
| V-P1, V-P2 | §5.3 | `prr-pr2a-{gibuu,q3}`, `prr-pr2b-{gibuu,q3}` | IBU at five iterations "retains less / more of the prior than the five-observable estimator", "retains a share of the prior that differs from the five-observable estimator's by less than its bar", or "is not compared …, because a retained fraction is undefined at this truth"; its retention "falls / rises by that margin", "neither falls nor rises by that margin" (the margin, 0.05, in the fixed text) or "at longer iteration is undefined" |
| V-P3 to V-P5 | §5.3 | `prr-label-*` | one "consistent with …" or "sensitive to …" sentence per label that holds, per truth, in FD-PRR §5.4's own wording; `unattr` prints "no reading attributes the retained prior to a tested setting" |
| V-P6 | §5.3 | `prr-pr3-any`, `prr-pr3-levels` | "Some tested levels, ⟨levels⟩, clear both flagged truths at these truths … not a new estimator." / "No tested level clears both flagged truths at these truths …" |
| V-P7 | §5.3 | `prr-pr3-ibu` | "clears" / "does not clear" |
| V-L1 | §6.3 | `ll5d-campaign`, `ll5d-route` | graded: the four per-(tune, reading) clauses, the flag sentences, and "The result concerns the procedure's covariance at those tunes, not the reported intervals at the data."; a route sentence first for offset-proceeded and repaired; gate-failed, offset-stopped, stop: one sentence each, "gives no coverage reading", with "before the bulk of its pseudo-experiments" for offset-stopped (the pilot unfolds one toy, `:558`) |
| V-L3 | §6.3 | `ll5d-{g18,ar23}-{minus2,all}` | covers / under-covers in cells ⟨cells⟩ / under-covers jointly and in cells ⟨cells⟩ / under-covers jointly, with no cell flagged / "is not graded, the test being invalid by its own controls there" (the test, not the covariance, is invalid) |
| V-L4 | §6.3 | `ll5d-*-{weak,over,clip}` | one sentence per reading with a flag: weakened passes, over-coverage "reported and not counted as a failure", "may be the clipping artefact, a reading that does not remove them" |
| V-V1 | §5.4 | `vhalf-n-*` | the four counts |
| V-V2 | §5.4 | `vhalf-outcome` | some-fail adds the failing cells' list; none-fail adds nothing |

**The licences each variant keeps.** Every variant in a group keeps its record's NOT CITABLE FOR.
- **FD-PRR** (`FD-PRR-DECLARATION.md:40-56`):
  - no cause;
  - no estimator change, whatever PR-3 shows. V-P6's "not a new estimator" says this;
  - no held-out claim and no "would pass". PR-3's only wordings are "clears / does not clear at these truths";
  - no coverage, interval or measurement, and no data quantity.
- **LL5D** (`LL5D-DECLARATION.md:76-94`, and the consult `:39-43`):
  - no coverage rate, since there are two truths;
  - nothing about the reported data intervals or the ensemble average. The fixed sentence before the variants says
    both;
  - the two readings are correlated, and neither tests the other.
- **V-HALF** (the bias-half decision, `:49`):
  - no coverage, and no measurement;
  - no cause;
  - not ATLAS's rule, and not the advisor's exact formulation;
  - a failing cell is not to be read as excluded, wrong or unreported. The fixed sentence says the rule "grades bias
    under simulated truths; it does not assess the detector model, and it is not a coverage statement" (decision
    item 6 of `DECISION-20261109-joseph-methods-baseline-and-plan.md`).

**Round 6, the editor's C3: does every outcome leave the fixed sentences true?** Checked for each LL5D and FD-PRR
outcome:
- **§1, "the third is not established":** true under every LL5D outcome. A COVERS at both tunes is coverage at two
  truths, of the procedure, not of the reported intervals (`LL5D-DECLARATION.md:88`, `:76-94`).
- **§7 ¶1, "It does not yet provide validated interval coverage":** true for the same reason.
- **Limitation 1:** a fixed clause now says "the like-for-like test …, whatever its outcome, grades the procedure at
  two truths, not the reported intervals", which is true in every class.
- **The prior-retention finding (§1, §5):** it rests on Table 2, which no FD-PRR outcome changes (FD-PRR NOT CITABLE
  FOR: "Table II or its grades").
- **The abstract (C1):** each pending clause is now its own sentence, and every variant is grammatical alone.
- **The abstract (the editor's second read, item 1): no fixed calibration sentence is true for every outcome.** The
  current "The uncertainties are not calibrated" contradicts a both-cover variant. This is W-11, for the director,
  with per-class options in W-OPTIONS.md. It is the one C3 failure found, and it stays open until W-11 is decided.

**Round 6 pre-read (2026-11-09, the director's fix list on `preread-outcomes/NOTES.txt`):** the class sets, derived
rules and variant rows above are the ones the fixes introduced. `make_values_fived16.ll5d_fill_cases()` lists fillings
that reach every class of every like-for-like key, and the fill test uses them. The C3 check above was re-read for the
new classes: §1, §7 ¶1 and Limitation 1 stay true in each, and every covering abstract class now names the procedure's
rebuilt covariance and says the result is not about the reported intervals.
