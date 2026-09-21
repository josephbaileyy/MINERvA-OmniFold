# PART J — the clause-(d) mootness claim is WITHDRAWN, and I held its disproof

**Owner:** independent-assessment lane. **Base of measurement:** `05bf8647` (packet), `173baf44`
(recommendation), `6f24fb00` (code).

**CITABLE FOR:** the withdrawal in §J.1 and the stage correction in §J.3.
**NOT CITABLE FOR:** anything about clause (d)'s substance — this lane is disqualified on it (§J.2).

---

## J.1 — WITHDRAWN: "clause (d) is moot"

**The claim.** Parts F §F.6, G §G.1 and H §H.3 each said that Joseph's *"Do not reopen the
universal-bound approach"* makes the clause-(d) independence question moot for the recommended path,
leaving it live only if the ρ bound is adopted anyway.

**It is false, and the measurement is one line.** At `05bf8647` the endpoint-A packet's §2 requirement
table carries:

> **A-4** | declaration stability | retained rank and retained-subspace projector gap across members,
> `‖P_0 − P_k‖_2 ≤ 1e-8`. … | PROPOSED, **narrowed**

That is clause (d)'s exact test, as a live endpoint-A requirement, and the row makes **no reference to
the ρ bound** — the only occurrence of "bound" in it is *"this **bounds** the subspace"*, describing
what A-4 does.

**Where the claim was true, and why that does not save it.** `RECOMMENDATION:392`'s clause (d) is a
sub-clause of the ρ-leg's terminal-outcome list, whose `MET` condition is `rho <= rho_max`. Retiring
the bound retires *that list*. It does not retire **the test the clause states**, which A-4 carries
independently. I conflated a clause's **role** with its **content** — and a requirement that survives
its original host is exactly the thing a mootness claim must be checked against.

**The consequence is the reason this matters:** anyone acting on "clause (d) is moot" drops a live
A-4 requirement. The error's direction is permissive, which is the direction `F18` warns about in
reverse and the direction a reviewer's errors should never take.

**Withdrawal banners are placed at all three sites**, not only here. An incomplete withdrawal is worse
than none, because the surviving site is the one a reader lands on: Part F §F.6 item 2, Part G §G.1's
third bullet, Part H §H.3's `DISQUALIFIED` paragraph.

### J.1a — I HELD THE DISPROOF, IN A LATER PART, AND DID NOT COLLIDE IT

Part I §I.6 recuses from *"A-4's `1e-8` tolerance wherever it appears, **including its row in §2's
table**. A-4 is clause (d); I supplied that gate and am disqualified."*

**A recusal from A-4 presupposes A-4 is live.** So Part I contradicts Parts F, G and H, and Part I is
the *later* document — written after all three, by me, quoting the very table row that disproves them,
without noticing. Part I was right and never said it was correcting anything, so a reader of Part H
alone — which is the artifact I told the coordinator to use for sizing what is and is not cleared —
gets the wrong answer.

This is the same failure as `A14` versus `A30` in Part B: both halves in my own documents, in my own
words, never collided, because *reading a caveat* and *using the claim it disqualifies* happen at
different moments and nothing mechanical connects them. Writing it up as a lesson the first time did
not prevent the second. **The mechanical form that would have caught it: when recusing from an item,
grep my own corpus for that item's name and read every hit.** Three of the four sites would have
turned up on `grep -in moot`.

---

## J.2 — CLAUSE (d)'s SUBSTANCE: RELAYED, NOT ASSESSED

Recorded because it bears on the record, and explicitly **not** reviewed — this lane supplied the
gate and is disqualified. The mathematical reviewer reports it sound as a **necessary** condition with
*"MET additionally requires"* the right logical form; not sufficient, because the retained subspace
can be identical while the retained eigenvalues — what `pinv` actually inverts — move arbitrarily;
and the `1e-8` not load-bearing, since for orthogonal projectors a rank change gives exactly `1` and a
structural match gives round-off, so `1e-12` through `1e-3` behave identically.

**RELAYED. I take no view on any of it**, including the parts that are favourable to what I supplied.
The insufficiency point is consistent with what `F-I` says from the other side, and I note only that
consistency.

---

## J.3 — THE SHARING-STRUCTURE FINDING IS REAL AND A-6 IS THE WRONG HOME FOR IT

Relayed: `B`'s adequacy depends on how members share replica draws — ratio `5.17` at independent
draws down to `0.81` at 99% shared — and A-6 declares `N`, not the sharing structure. Offered as A-6
being *"under-specified in two independent ways at once"*, alongside my equal-`N` finding.

**The finding is real. Attributing it to A-6 mislocates it, and the two are not the same kind of
defect.**

- **Ruling 2 fixes A-6's field list**, verbatim: *"Record each sample-covariance block's verified
  ensemble size and normalization convention. State explicitly where no finite-ensemble treatment was
  applied. Where no inversion is performed, mark the inverted dimension as not applicable."* Sharing
  structure is **not in it**. So requiring it of A-6 is a proposal to **extend Ruling 2**, which is
  Joseph's to make — not an A-6 conformance defect. Loading it onto A-6 is the over-demand `F18`
  exists to prevent, and it would hand Joseph an inflated A-6 defect list.
- **My equal-`N` finding is a different kind:** it says A-6's own part **(a)** cannot substitute for
  A-6's own part **(b)**, which the packet itself names. That is an **internal** insufficiency,
  decided entirely inside A-6's declared purpose, and it needs no new field from Joseph.

**So the honest split: one A-6 defect, one live gap in whatever criterion consumes `B`.** Both are
"`N` is not enough", and they are not additive against the same requirement. This is the wrong-stage
shape — a real finding routed to a stage whose predicate does not cover it — and naming the stage with
**its own** predicate rather than the finding's is what keeps the count honest.

I record without assessing that `A-7` is withdrawn as not adoptable and the "supply `S`" ask to Joseph
retracted; `A-7` is outside my slice.

---

## J.4 — UNCHANGED

Part I's assessment of §2, §2.1, §2.1a and §3–§3.3 at `05bf8647` stands as written, including §I.2's
flux-band finding. Nothing in this part touches it. My disqualification on clause (d) and on A-4's
tolerance is unchanged and, per §J.1, is now correctly understood as spent on a **live** requirement.
