# PART L — the coverage items: rows A-1 / A-2, §5, and §7's residues

**Owner:** independent-assessment lane. **Subject:** the endpoint-A packet at `05bf8647`, sha256
`e5fbd9a99cd27d9db0130246bbbded0e334de30e64161804e3735c05de3e5df1`, 623 lines.
**Code base:** `6f24fb00`. **Yardstick:** `F1`–`F21` as corrected in Part G §G.4, and §F.5's block
conditions, committed at `c695f209` before this packet existed.

**Assigned:** §2's rows **A-1** and **A-2**; **§5** (`:544-561`); **§7** (`:582-623`).
**No grade assigned** (`BEN-381`). A-3/A-5/A-7, §2.1a, §4.x, §6 and clause (d) are not mine.

---

## L.1 — A-1: "§3.3's **fifteen** reject conditions" IS NINETEEN, AND `4c` IS ONE OF THE FOUR OMITTED

A-1 declares its content **FIXED by spec**: *"SPEC §1.3a algebra, §1.3b identity set incl. the `g^c`
reconstruction gate, §3.3's fifteen reject conditions."* The first two verify — `z_assembly.py:4`
carries the algebra and `:20-25` the five gates with `G3` as the reconstruction gate.

**The count does not.** Enumerated at `6f24fb00`, §3.3 spans `:1242-1295` and carries **19** condition
labels: `1`–`15` integer-labelled, **plus `4b`, `4c`, `11b`, `11c`**.

**And the omission is load-bearing rather than cosmetic.** Condition `4c` is *"The run proceeds
against a fixed-seed null bound or a `(cause …)` boundary…"* — and it is **the condition this
packet's own §3 relies on**. §3.1(e) cites `reject_conditions=('4c',)` by name, and my Part I probe
reproduced it: adopting the correlation leg with the boundary withheld returns
`assessable=False`, `reject_conditions=('4c',)`, `is_met=False`. **§3.3's "costs nothing today" is
true because `4c` bites.** So A-1 declares a fixed set that excludes the very condition §3 depends on,
in the same document.

`11b` and `11c` are labelled *"RESTATED IN REV. 16"* and *"NEW IN REV. 16, and conditional by
construction"*, so the suffixed labels are later additions and **"fifteen" reads as a pre-rev-16
count quoted after the work that changed it.** This is the expected-count-selects-the-rows shape, and
this campaign has now paid for it three times — including once by me, in `B8`.

**What survives:** A-1's *class* (FIXED by spec, not reopened) is right, and nothing here reopens it.
The defect is the count and therefore the set it declares.

## L.2 — A-2: THE STATED GROUND SUPPORTS ONE DECLARATION AND THE ROW REQUIRES FOUR

A-2, as CONFORMANCE: *"the four inversion declarations of `app_statmethods.tex:645-658` travel with
any released projection **even for a diagonal consumer** — clause (iv) exists because 'the 5D
candidate, its 4D projection and the published 2D block have different ranks'."*

**"Four" is correct** and I will not manufacture a count error: `(v)` is A-6's, so `(i)`–`(iv)` is the
right set. The citation range is loose — `(i)`–`(iv)` end at `:651` and `:651-654` is `(v)` — but that
is not the finding.

**The finding is that the ground supports `(iv)` alone.** Taken one at a time against an endpoint that
performs no inversion:

| declaration | under Ruling 1 |
|---|---|
| **(i)** the inverse actually used — pseudo-inverse with its `rcond`, or the truncation rank | **no inverse exists.** Not merely over-demanded — **unsatisfiable**, except as "not applicable", which is the form Ruling 2 uses for `p` |
| **(ii)** the retained rank as `ndf` | **no `ndf` exists** without a χ². Same |
| **(iii)** the rank-truncation scan for that covariance | a **new measurement**, on a 10,694-bin object. This is a compute obligation, and `F20` requires satisfiability without new cluster compute |
| **(iv)** which covariance is meant | **transfers cleanly.** Naming which covariance a released error bar came from needs no inversion, and it is the only one A-2's own sentence argues for |

**So A-2 gives a reason for one declaration and requires four.** This is §F.5's pre-registered block
condition on `F18` — inversion-grade criteria imposed on an endpoint that releases no significance —
and it is the one I said I expected to have to defend, because those criteria have the most developed
mathematics behind them and are therefore the easiest to reach for. `(iv)` should be required on the
ground given; `(i)` and `(ii)` are answerable only as "not applicable"; `(iii)` needs its own
justification and its own cost, and has neither here.

## L.3 — §5: THE DISPOSITION IS RIGHT AND THE CHARACTERIZATION INVERTS THE NOTE'S OWN SCOPING

§5 asserts `2d-unfolding/uq/_ours_only_chi2.py:128-130` is *"a **LIVE 2D non-conformer** on `ndf`"*
against `app_statmethods.tex:648` clause (ii). The three code facts verify: `:130` prints
`ndf = {n_rep}`, `:123` computes `rank_at_1em12` and uses it only in the `:124` print, `:128` is
`np.linalg.inv`.

**But clause (ii) does not reach a 2D object, and the note says so twice.**

- `:645` — *"Therefore `ndf=n_reported` **must not be used for an N-D covariance**. **Any N-D χ²**
  shall instead quote (i)…(v)"*.
- `:628-634` — the 2D choice is **affirmatively justified**, not merely tolerated: *"This `ndf` is
  dimension-conditional, and is justified here by the truncation scan — not by convention… On the
  205-bin 2D problem that presumption is **tested and holds**… **The scan is the evidence; 205 is not
  assumed.**"*
- `:636` — *"**It does not transfer to the N-D covariances.**"*

So 2D is the case where `ndf = n_reported` is licensed, and calling a 2D object a clause-(ii)
non-conformer **runs the note's scoping backwards.**

**"LIVE" is also not established.** `RANK-AND-INVERSION-20260810.md:56` classifies the ours-only
`χ²/ndf = 252` as *"2D, **diagnostic** … explicitly labelled 'naive **pseudo-inverse**', used to
demonstrate a regularisation problem"* and verdicts it *"**safe — it is the illustration, not a
result**"*. This script's branch is the **direct** inverse (`:126` *"no pseudo-inverse"*), so it is
not even the source of that illustration. No released quantity depends on it.

**Qualification 1 is unverified, and its antecedent is doubtful for this object.** §5 says
*"`np.linalg.inv` is correct at full rank … the non-conformance is the `ndf` label, not the inverse."*
The inverted object is `Cs = 0.5*(C + C.T)` from `C = Cu + Cb` (`:117`, `:120`) — the **ours-only**
sum, which the note itself puts below full rank: `:693-696`, *"remove the external floor and our
finite-`N` blocks become precisely what fills the null space of `C^syst` (rank `140→201`)"*. And
`np.linalg.inv` **does not raise on a near-singular matrix** — only on an exactly singular one — so
the `try/except` at `:127-133` does not cover the case. "Correct at full rank" is true and, for this
object, unestablished; the file only *prints* the rank at `:124`, so the discriminating measurement
exists at runtime and nowhere in the tree.

**Qualification 2 is correct and well-made.** *"Being out of scope is **not** conformance"* is exactly
the distinction `F17` requires, and it is the right thing to state explicitly rather than leave to
inference.

**Net: the disposition survives on different grounds.** Do-not-change is right — but because the
script is a diagnostic outside the released set, not because Ruling 1 shields a published 2D
conformance defect. The difference matters in both directions: §5 tells Joseph a live conformance
defect sits inside the validated 2D scope, which overstates the defect; and it treats the file as
protected-and-untouchable, which overstates the protection, since Ruling 1 preserves the *validated 2D
scope* and a diagnostic script is not that.

**The concern that would survive, named and not authored:** the 2D license at `:628-634` rests on a
truncation scan of the **published** 205-bin object, while `Cu + Cb` is a different covariance with a
different rank — and clause (iv) itself exists because *"the 5D candidate, its 4D projection and the
published 2D block have different ranks."* That is a transfer-of-license question, not a clause-(ii)
conformance question. §5 does not make that argument, and I am not making it into a requirement.

## L.4 — §7: THE RESIDUE LIST IS THOROUGH, AND TWO THINGS ARE ABSENT

Assessed for completeness against `F1`–`F21`. **This is an unusually good residue list** and I want
that on the record before the gaps: residue 8 states the withdrawal-checker hole *at severity* with an
explicit handoff rather than as a tidy exemption, and names the detector that would catch it; residue
9 records two of its own claims corrected by a peer *"rather than by any check I ran"*; residue 11
records a population re-pin verified **by set difference on the tracked path lists, not by the
count** — which is the exact discipline the count failures in this campaign call for; residue 4
declines to rely on a `1-3 min` runtime figure it labels local and unestablished; residue 7 records
`BEN-381` and that no remedy was requested of this lane.

**Absent, and only one of the two is culpable.**

- **`F2` is unmet and unrecorded.** `F2` requires each released projection to name its **builder and
  commit**, because four non-equivalent builders exist at `6f24fb00` (`p4_lib.py:1353`,
  `project_cov_nd.py:79`, `pet/assemble_ctotal_bkgsub.py:36`, and the inline construction at
  `eavailW_covariance.py:404-406`) and `FINDING-20260910-projection-builders-agree-numerically-and-diverge-on-refusal.md`
  — in `main` — records that they **agree on weights and diverge on refusal**. Nothing in §2 or §7
  names which builder any released projection uses, and no residue records the omission. This one is
  a real gap: the finding is in `main` and the requirement was pre-registered.
- **The block-population assumption is unrecorded, and that is expected rather than culpable.** §I.2
  measured that §2.1's *"exactly two"* is three, because the third sample covariance sits one level
  inside `Σ_V C_b`. A residue list cannot record an assumption its author has not noticed, so its
  absence here is not a §7 defect — but it should become a residue or a correction in rev. 3, and I
  note it so that its absence is not later read as this lane having cleared it.

## L.5 — NOT ASSESSED

- **A-3, A-5, A-7, §2.1a, §4.1/§4.2/§4.3/§4.4x, §6** — routed elsewhere. §2.1a specifically because
  its content incorporates this lane's own equal-`N` strengthening, so confirming it would be partial
  self-confirmation; the coordinator routed it away without my asking, which was correct.
- **A-4 and clause (d)'s tolerance wherever they appear**, including A-4's row in §2's table.
  Disqualified; see Part J §J.1 for why that disqualification is spent on a **live** requirement.
- **Whether `_ours_only_chi2.py`'s object is in fact full rank** — not run. §L.3 does not claim it is
  rank-deficient; it claims the qualification's antecedent is unestablished and that the note's own
  text puts it in doubt.
- **Reviewer `F3`'s 500-trial split**, per Part K §K.4.
