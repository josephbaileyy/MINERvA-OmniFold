# T2C LICENCE NOTE for Joseph: may the size of ENS1's one bias deficit enter the paper? (2026-11-10, DRAFT; no paper wording until Joseph rules)

**By** the valid-region lane (director-helper-2), at the director's request.

**Under** `DECISION-20261110-joseph-confirm-round-scope.md` (PR #1030, open at `04cb5b7d`), Tier 2, and the director's
rulings of 2026-11-10.

**Nothing is computed.** Every number below is already in a committed record. <!-- absence-ok: a statement about this draft's own status before binding, not a claim that a result does not exist -->

**The decision asked of you:** whether to amend the licence of `OUTCOME-20261109-ens1-stab-pass-bias-worse.md` so that
one sentence giving the deficit's size may enter the paper. The director notes that amending a record's licence on a
claim is yours.

## 1. What the referees asked

- **The blind Claude referee of the confirming round** asked for it (PR #1029,
  `state/2d-closeout/stageF/methods/secondary-results/referee-methods-confirm-20261110/claude.txt@879b9501`).
  - At :108-109: "the magnitude of that one difference is not given … At minimum, the authors should: report the
    magnitude of its deficit at the GiBUU Eavail shape".
  - At :172, its required revision 6(a): "reporting the ensemble average on data with the magnitude of its one deficit
    (M5)".
  - Its "GiBUU Eavail shape" is Stage 0c GiBUU, the `eavail_shape` truth (`FD-STAB-DECLARATION.md:118`).
- **gpt.txt makes no such request.** It asks only for the ensemble mitigation's placement in the text (:195).
  - Search: `grep -niE 'ensemble|deficit|GiBUU'` over gpt.txt@879b9501. <!-- absence-ok: scoped to that file -->
- **The director's Tier 2 list** (DECISION-20261110 "What led to it") records the request as "the ensemble average's
  result on data with the size of its one deficit".
- **The data half is not Tier 2.** No E₉₆ data result exists: ENS1 ran on simulated pseudo-data only
  (`ENS1-DECLARATION.md:105-107`). The director has moved it to the post-LL5D list with Tier 3, and will tell you.
- **This note is about the deficit only.**

## 2. The number, as recorded

`ensemble/receipts/stage2-a1-analysis/ens1_stage2.json`, sha256
`c2ee701d7c23643b257f633410c8416d4ca4e8ce5eb8b8ad38ff3afd244c01fd`, key `bias.stage0c_gibuu`, in the units of ENS1
§5 (RMS and MAX of the closure bias over the 16 cells):

| metric | E₉₆ | F (configuration (e)) | excess | floor (key) | excess / floor |
|---|---:|---:|---:|---:|---:|
| RMS | 0.056467 (`rms`) | 0.055955 (`rms_control`) | 0.000512 | 0.000418 (`delta_rms`) | 1.23 |
| MAX | 0.106699 (`max`) | 0.105771 (`max_control`) | 0.000929 | 0.001783 (`delta_max`) | 0.52 (within its floor) |

- The excess column is the director's arithmetic as the OUTCOME prints it: E₉₆ minus F. The ratio column is the same
  arithmetic.
- `verdict` BIAS_WORSE and `worse` ["stage0c_gibuu"].
- At the other 16 judged truths E₉₆ is no worse, and at `A7_gibuu` it is better on both metrics (the OUTCOME).

## 3. What the records say, and why the size is excluded today

- **FD-STAB §5.3** (`FD-STAB-DECLARATION.md:206-209`), which ENS1 adopts (`ENS1-DECLARATION.md:225-226`): "The closure
  biases at A7 GiBUU and Stage 0c GiBUU are printed per candidate. **Neither the bias criterion beyond 'no worse', nor
  any other criterion, nor the tie-break may use them** (the director's rule (i)). The verdict function takes no bias
  magnitude, and a test checks that an improvement at the GiBUU truths does not move the verdict."
  - The rule binds the **criteria**: no decision in FD-STAB or ENS1 may turn on a GiBUU bias magnitude.
  - It was fixed before either test ran. As written, it does not forbid **reporting** the magnitude.
  - Search: `git grep "rule (i)"` over `docs/` @`fc847d82` finds no written rationale beyond §5.3's own sentence.
    <!-- absence-ok: scoped to the search stated -->
- **The ENS1 OUTCOME** (`OUTCOME-20261109-ens1-stab-pass-bias-worse.md`, NOT CITABLE FOR) goes further than the rule.
  It excludes both:
  - "Any use of the GiBUU bias magnitudes beyond 'no worse'";
  - "Any absolute statement about E₉₆'s bias, or a ranking of the two estimators beyond the verdict".
- **The reason those exclusions are there:**
  - the magnitudes were declared descriptive;
  - a single deficit of 1.23 floors at one truth out of 17 sits inside the declared familywise false-"worse" rate. The
    OUTCOME gives that rate as about 0.5 % with correctly estimated SDs, and at most about 4.5 % if both SDs are
    underestimated (ENS1 :216-217).
  - So the record refuses any reading of whether the excess is noise. Its NOT CITABLE FOR also excludes "that the
    stage-0c excess is or is not noise".
- **The OUTCOME's CITABLE FOR already allows** the verdict sentence: "worse at one (Stage 0c GiBUU, by its RMS bias), by
  the criterion fixed before the test; it is therefore not adopted". The size is what it withholds.

## 4. The exact sentence that would enter the paper, if you amend the licence

> At the one truth where it was worse (Stage 0c GiBUU), the ensemble average's RMS closure bias over the 16 cells
> exceeded the reported estimator's by 0.000512 (0.056467 against 0.055955), 1.23 times the declared floor of 0.000418;
> its maximum-bias excess, 0.000929, was within its floor of 0.001783.

- **The sentence states the record's numbers and nothing more.**
  - It makes no reading of noise or significance.
  - It makes no claim that E₉₆ is a stabilised variant.
  - It ranks nothing beyond the verdict.
- **Where it would sit:** placement and the surrounding wording are the paper lane's, through the PRD-referee read.
- **What the amendment would need:** one line added to the OUTCOME's CITABLE FOR, naming this sentence. The exclusions
  on noise, stabilisation and ranking would stay.

## 5. The options

1. **Amend.** Add the sentence above to the OUTCOME's CITABLE FOR. The paper may then carry it, through the paper lane
   and the PRD-referee read.
2. **Keep the licence.** The paper gives the verdict sentence only. The response to the referees says that the
   magnitudes were declared descriptive before the test, and points to the committed record.

The director will route your answer. Until you rule, no wording about the deficit's size enters the paper or the note.

Nothing is submitted, deposited or tagged.
