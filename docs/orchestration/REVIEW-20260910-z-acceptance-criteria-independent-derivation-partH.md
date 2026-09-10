# PART H — the scope of what Parts A–G actually clear, and F-0's disposition

**Owner:** independent-assessment lane (`lane/z-criteria-independent-assessment-20260910`).
**Base of measurement:** code `6f24fb00`; designer lane `b40686ec`; decision lane `ae876e14`.
**Continues:** Parts A–G (`1508ead0` … `2f1b9895`).

**CITABLE FOR:** §H.1's statement of what this lane has and has not reviewed, §H.2's disposition of
`F-0`, and §H.3's disqualification list.
**NOT CITABLE FOR:** any clearance of the endpoint-A acceptance packet. See §H.1 — this lane has not
opened it.

---

## H.1 — ⚠ WHAT PARTS A–G DO NOT COVER, AND IT IS AN ENTIRE ARTIFACT

Written at the top because a scope caveat at the end is not a caveat, and because Parts B and D carry
`READY` verdicts that a reader could mistake for clearance of the current tip.

**The latest designer commit any part of this assessment reviewed is `173baf44`.** Measured
`173baf44..b40686ec` (three commits: `92b2c468`, `8d3071a8`, `b40686ec`):

| file | delta | reviewed here? |
|---|---|---|
| `PACKET-20260910-z-endpoint-A-acceptance-and-cause3-corr-amendment.md` | **+505 / −0, new** | **NO — never opened** |
| `state/probe-z-projected-stability-20260910.py` | **+327 / −0, new** | **NO** |
| `PACKET-20260910-z-consumer-set-and-endpoint-requirements.md` | +35 / −10 | **NO** — Part G read only its `:40-44` and `:215-250` at `173baf44` |
| `state/check-consumer-set-20260910.py` | +12 / −3 | **NO** |
| `CATALOG.md`, `MANIFEST-overrides.tsv` | +52 / −3 | **NO** |

The new packet is `docs/orchestration/PACKET-20260910-z-endpoint-A-acceptance-and-cause3-corr-amendment.md`,
sha256 `e04b4983523e28c0a7c0a2e81c2f86c30bfd73d6e12acf5feb38c52e82a1e4f0`, 505 lines. Digested here,
**not read**; only its size, digest and section headings were measured, and only in order to size this
hole honestly.

**Per-part referents, so no reader has to infer them:**

| part | commit | subject reviewed | subject's referent |
|---|---|---|---|
| A | `1508ead0` | nothing, by design — derived first | `PROPOSAL-20260908` sha256 `3fc9fb87…`, digested-NOT-read |
| B, C | `09905260`, `69b9fde2` | `PROPOSAL-20260908` sha256 `3fc9fb87…` | `2ebdf095`; Part C re-measured at `c18f9daa` |
| D | `47ff4606` | `RECOMMENDATION-20260910` sha256 `622a9dcd…`, 885 lines | `2ebdf095` |
| E | `54c565a6` | this lane's own independence | — |
| F | `c695f209` | nothing — derived before the endpoint-A packet existed | `0dce72d2…` and `a528a8fd…` (1406 lines) at `173baf44`, digested-NOT-read |
| G | `2f1b9895` | named cells only | `173baf44` cells; rulings at `a11d6cdd`; code `6f24fb00` |

**Consequence, stated plainly: a `READY` in Part B or Part D is a verdict on `2ebdf095` and is two
revisions stale.** Nothing in this lane clears `8d3071a8` or `b40686ec`.

---

## H.2 — `F-0` CLOSES ON ITS OWN CRITERION, AND THE RESIDUAL IS A DIFFERENT, SMALLER GAP

`F-0` measured that neither ruling existed as a committed `DECISION-*`/`RULING-*` record across 131
refs. Both now exist on `origin/lane/decision-20260910-z-endpoint-a-ruling`, committed and pushed but
**not reachable from `main`**. Asked whether `F-0` therefore stays open, the answer has to come from
the criterion as written, not from what would be convenient.

**Part F's criterion was existence on *any* ref, and its stated consequence was diffability** — *"the
consequence is not that the rulings are doubtful — it is that they are undiffable. A requirement set
derived from an unrecorded ruling cannot later be checked against drift in that ruling, because there
is no text to compare against."* That condition is met. **`F-0` is CLOSED.** Re-reading it as
requiring reachability from `main` would be moving my own criterion after the fact in order to keep a
finding alive, which is the failure this document has catalogued three times.

**The criterion has since done its job, measured.** Both records changed between `a11d6cdd` and
`ae876e14`, and the change was confined to a metadata header — a `2026-09-10T20:0X` placeholder
corrected to `19:56:37Z`, caught by the mathematical reviewer against the commit's own timestamps. The
**verbatim Appendix A blocks are byte-identical** across the two commits:

| record | Appendix A `>` lines, sha256 (24) | at `a11d6cdd` vs `ae876e14` |
|---|---|---|
| `…joseph-b-deferred-and-finite-ensemble-disclosure.md` | `0bd716c2d0a719bfc6d7111d` | **IDENTICAL** |
| `…joseph-accepts-outcome-2-and-opens-replacement-packet.md` | `2d2587a48d9ec36f06deb02e` | **IDENTICAL** |

So Part G's quotations of Joseph's words hold at the decision lane's current tip. That is the whole
point of wanting a record: the drift check is now possible and it passed.

### H.2a — NEW GAP, filed narrowly rather than smuggled into `F-0`

**A ruling that governs `main` is not reachable from `main`.** Ruling 1 constrains what `main` may
publish — *"do not quote Z-dependent/non-2D generator significances, p-values, or calibrated exclusion
claims. Preserve the validated 2D scope unchanged"* — and measured at `origin/main`, the newest ruling
record present is `RULING-20260908`; both 09-10 records are **ABSENT** from `origin/main` and
**PRESENT** on the lane.

A session that pins `origin/main` and reads the routed records therefore cannot see the constraint
that binds it. This is an asymmetry between a ruling's **scope** and its record's **reachability**,
not an absence of record, and it is a smaller and truer claim than a still-open `F-0`. Closing it is
a merge, which this lane cannot authorize and does not request here.

---

## H.3 — DISQUALIFICATION LIST, AND WHERE THE LINE IS

Part E established that supplying a remedy spends this lane's verdict on that remedy. Applied:

**DISQUALIFIED — one item.** The retained-subspace gate: `‖P_0 − P_k‖_2 <= 1e-8` on the orthogonal
projectors onto the retained modes, terminal-outcome clause (d), together with its `1e-8` tolerance. I
found the hole (`D1`) and then supplied the fix, so assessing the clause that implements it would be
certifying my own design input. Likely moot in any case: Joseph's *"Do not reopen the universal-bound
approach"* removes the bound from the recommended gated set, so clause (d) binds only if the bound is
adopted regardless.

**NOT DISQUALIFIED — the projected-uncertainty boundary.** Part F left `F9` unanswered and Part G §G.1
recorded the convergence with Joseph's adequacy check and stopped, both deliberately, to keep this
slot spendable. **The line is between *"here is what must be true"* — a requirement, which does not
disqualify, because otherwise no reviewer could review twice — and *"here is the statistic, the
denominator and the number that make it true"*, which is a remedy and does.** This lane supplied only
the former.

**RECUSED FROM GRADING EITHER WAY.** Per `BEN-381` the drafting lane may not grade the legs it
defines. Assessment is not grading: this lane will assess a proposed boundary and will **not** assign
`MET`/`OPEN`/`UNRESOLVED` to it.

**DECLARED WEAKNESS, not a disqualification.** The new packet's §1 and §1.1 are titled as an operand
correction resolved per consumer, which is the shape of Part G's `F-III`. If those sections transcribe
that finding, this lane confirming them is partly self-confirmation. `F-III` is a **measurement of the
code**, so anyone can re-derive it and this lane will re-derive it rather than cite itself — but its
verdict on that slice carries less independent weight than elsewhere, and a second reviewer should
spot-check it. If a proposed boundary turns out to be a transcription of this lane's own text, the
recusal is per-slice and will be declared rather than quietly absorbed.

---

## H.4 — A ROUTING NOTE: "THE ORCHESTRATOR" RE-POINTS

The coordinating session that briefed Parts A–G ended, and a different session now holds that role.
Every unqualified *"the orchestrator"* in Parts A–G refers to the **earlier** session, including
Part C §C.1's misroute, Part E's routing gaps, and the four withdrawn relay claims. A definite
description is not a citation; it re-points, and it has now re-pointed. Peer identity in Parts A–G
should be read as of their commit dates.
