# PART T — the pre-implementation baseline, pinned; and reuse-vs-regenerate is already decided in code

**Owner:** independent-assessment lane. **Base of measurement:** `6f24fb00`. **No grade assigned.**
**Nothing has been implemented yet.** Pins arrive piecewise. This part pins the **"before" state**,
because *"additive only, no implicit fallback or overwrite"* is a claim that can only be judged against
a baseline recorded beforehand.

**My slice:** the declared projection maps with both-direction support checks; the two ledgers;
build-path integrity. **Not mine:** terminal handling, `κ`, the mutation tests, the claim-scoping /
cause-3 amendment question, and **the 1% threshold** — which stays a proposed requirement and which I
am not assessing in either direction.

---

## T.1 — THE HANDED CLAIMS VERIFY, WITH TWO CITATIONS CORRECTED

| claim | verified at `6f24fb00` |
|---|---|
| `p4_build_components.py:180` opens `--out` with `RECREATE` | **yes** — `fo = ROOT.TFile.Open(a.out, "RECREATE")` |
| `adopt_unified_5d.py` **defaults** `--out` | **yes**, but at **`:80-81`**, not `:79-80` — `:79` is `--prod`. Default: `uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root` |
| `mr_declared()` is one variable | **yes** — `lib_member_resume.sh:230`, `mr_declared() { [[ -n "${MNV_EST_SEED_OFFSET:-}" ]]; }` |
| the destination arm already exists in `p4_lib` | **yes** — the expression is at **`:1394`**, `empty = np.nonzero(~M.any(axis=1))[0]`; `:1395` is its `require` |
| `:403-415` member-prefixes everything incl. `UTHROW` | **yes** — `UTHROW` `:412`, `STAT_COV` `:413`, `ML_COV` `:414`, plus `CV` `:405`, `OUTD` `:409`, `SWEEP_GLOB` `:411` |
| the `[3,100] GeV` catch bin is the 7th `E_avail` bin | **yes** — `EA_EDGES` has 7 bins and `[3.0, 100.0]` is the last |

## T.2 — THE GAP IS NOW TWO LINE NUMBERS, WHICH IS §S.1 MADE CONCRETE

Part S §S.1 found that arity and refusal are separated in the tree. The concrete form:

- **`project_cov_nd.py:99`** — `dropped = int((~keep).sum())`. **Source side only**, and it sits in the
  builder that *can* express P1–P4's arbitrary keep-axis arity.
- **`p4_lib.py:1394-1395`** — `empty = np.nonzero(~M.any(axis=1))[0]` with its `require`. **The
  destination arm**, and it sits in the builder with the wrong arity.

So the accounting that the capable builder performs is exactly the half that cannot see an unsupported
destination row, and the half that can is in the function that refuses P1–P4's shape. `dropped == 0`
passing while an all-zero row exists is `BEN-064`, whose own note at `p4_lib:1382-1393` calls it a
**masking** defect. **The destination arm does not need writing — it needs moving, or the arity does.**

## T.3 — NEW FINDING: REUSE-VS-REGENERATE IS NOT OPEN IN CODE. IT IS SELECTED BY `MNV_EST_SEED_OFFSET`.

`SPEC-20260906` §2.6c item 4 (`:1122-1125`) says: *"The ensemble question is OPEN and is named as
open. Whether Z reuses S's `stat_cov`/`ml_cov` digests or regenerates the replicas is a **scientific**
decision requiring a rationale … **This specification does not decide it**."*

**The launcher decides it on every run, and prints which way**, at `sbatch_finalize_5d_bkgaware_gpu.sh`:

- `:417` `if mr_declared; then` → `:421` *"MEMBER …: building **this member's OWN C_stat and C_ML**"*,
  with the two member-local combines at `:422-423`.
- `:424` `else` → `:425` *"undeclared: **reusing the archive's C_stat/C_ML**, per this script's
  original contract"*.

And the file's own header at `:8-10` — *"C_stat/C_ML are #13-invariant -> reuse existing"* — describes
**only the undeclared mode**, matching `:425`'s *"original contract"* wording.

**So the spec's open scientific question and the coded behaviour are not in correspondence.** A reader
of §2.6c item 4 concludes the choice is pending; a reader of `:421`/`:425` sees it already made, two
ways, per mode. Neither text is wrong — the scientific *rationale* is genuinely undecided — but the
**behaviour** is not, and it is bound to the same variable that declares membership. That is the
coupling authorized for decoupling, and it is visible in the launcher's own stdout.

**This refines my own Part R framing, against it.** Part R asked what happens *"if Joseph chooses
reuse."* In the code as written, **choosing a nontrivial `K` forces regenerate**, because declaring an
offset is what makes a run a member. So reuse is not independently selectable while `K` is nontrivial;
Part R's conditional supposed a freedom the launcher does not offer. The question was still worth
asking — §R.4 died to its own named falsifier — but its premise was looser than I stated.

## T.4 — AND EQUAL-`N` IS ENFORCED ACROSS MEMBERS BY DESIGN, NOT INCIDENTAL TO TWO ARMS

`:418-420`, verbatim: *"`--expected-ids` is an EXACT-POPULATION validator and is kept at the full
ranges **on purpose**: a member with a partial replica set must REFUSE rather than quietly combine
what it has. That is the barrier that makes a member's `C_stat` comparable to the archive's at all."*

**So every member's `C_stat` has `N = 100` and every member's `C_ML` has `N = 24`, by refusal.** My
equal-`N` finding (Part I §I.3, Part M §M.3) was filed as a property of two arms whose counts happened
to coincide. It is stronger than that: **the identity is enforced across the whole member family, and
deliberately, for a stated and good reason.** `N` therefore cannot distinguish *any* two members, not
merely the two arms — which is why *"record the **actual** seeds, component sources, and producing
revisions"* is the right instruction and why a count can never substitute for it.

## T.5 — `S2` IS HELD, NOT YET TRIGGERED

Part S §S2 binds only if a map is built by composing single-axis drops. No implementation exists, so
the route is undetermined and I am holding the condition rather than applying it. If composition is
the route, the order must be declared, for the reason measured in Part R §R.5a: the weights compose
exactly and the arithmetic does not (`~5e-16`–`1.3e-15` on reversal).

## T.6 — NOT ASSESSED

- **Any implementation** — none exists at this base.
- **The 1% threshold**, terminal handling, `κ`, the mutation tests, the claim-scoping question.
- **Whether `p4_build_components.py:180`'s `RECREATE` and `adopt_unified_5d.py:80-81`'s default
  actually get exercised** by the new path — that is a claim about the implementation, and §T.1 pins
  only that both exist to be checked against.
