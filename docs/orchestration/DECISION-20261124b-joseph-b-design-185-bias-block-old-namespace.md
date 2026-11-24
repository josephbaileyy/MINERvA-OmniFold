# DECISION 2026-11-24 (b) — Joseph: the (b) readout's design, the 185 screening threshold, pricing the 5D bias block, and removing IBUB's old namespace

**Recorded by** the director. It adds to `DECISION-20261124-joseph-covfix-rev12-cpu-rule-and-seven-decisions.md`.
Items 1–3 came through the rewrite helper, Joseph's wording channel, on 2026-11-24. Item 4 Joseph gave directly to
the director, in the director's session. Quoted words are Joseph's.

## 1. The (b) readout's design

The rewrite helper relayed Joseph's decisions with the specification `B-SPEC-DRAFT.md`, sha256
`2c735ebce02b49281561103311efca790ca1866d6c47036a2748a7ed5d157395`. It was built in a codex-school advisory session and
is not a record. cov2d folded its content into COVFIX rev 12 §4.4 and §4.5 on `cov2d/covfix-rev12-20261124`. Joseph's
decisions, as relayed:
- all 16 cells (R00–R15) are reported, each labelled measured or exploratory;
- κ = 1 for reporting, with 0.5·S_g required for claims that tell generators apart. The panel is fixed: GENIE CV,
  GENIE+MEC and NuWro, CH-harmonized, with Tune v1 excluded, plus a sensitivity printout that adds GiBUU;
- no absolute bias cap and no minimum number of cells;
- IBU is printed only, with a 2-SE paired flag;
- the joint 68.27% ellipsoid count at ≥ 185/300 per truth, plus the per-cell veto at 0.05/(kT);
- three outcomes with frozen labels (SUPPORT, INCONCLUSIVE, DEMONSTRATED DEFICIT) and Bonferroni deficit bounds;
- the 3-truth and 2-truth branches, both stated now.

## 2. The 185 threshold

Relayed: "confirm 185". A pass at ≥ 185/300 supports only "met the prespecified screening criterion" and "no cell
triggered the undercoverage flag". It does not support an affirmative claim that coverage exceeds 60% at every truth.
That claim would need 195: at 185, the one-sided 95% lower bound on joint coverage is 56.8%.

Two of the director's rulings carry over:
- each threshold is fixed by a declared pass probability at nominal, simulated with correlated toys;
- if that simulated rate falls below 0.90 in either branch, the threshold returns to Joseph before the amendment binds.

## 3. Pricing the 5D bias and fluctuation blocks

Relayed: "yes I suppose we should price the bias block". COVFIX builds bias and fluctuation blocks for 2D only.
tier3-design was asked to price the 5D blocks for the reported 16-cell covariance: the compute, the review stages, the
calendar, and whether they fit before PG seals. Until they exist, no support claim attaches to the 16-cell covariance.
They never delay the 2D result: if they are not ready by COVFIX's first seal spend, (b) is set aside and COVFIX runs
2D only. Pricing authorizes no compute.

## 4. Removing IBUB's old namespace

Joseph, directly to the director: "you can remove that old folder". This covers one path only,
`/pscratch/sd/j/josephrb/ibub-20261123`, the namespace of IBUB BINDING 1's stopped run.

director-helper-3 removed it with a script the director reviewed: `rm-ibub-20261123.sh`, sha256
`e7f875eabff78091a706d435165be2d507cd680736a61f44908e90c5165714bc`. The run is recorded in #1295:
- before removing, it checked the path and checked that no `ibub_` job was unended (61914825 CANCELLED);
- the inventory before removal was 32,660 entries, 29,413 files and 3,667,054,967 bytes;
- rm returned rc 0, then stat gave ENOENT;
- the B9-form deletion row is in `fd/receipts-ibub/rm-ibub-20261123/deletions.tsv`;
- connect R's STOP records were already on main in #1289.

**CITABLE FOR:** what Joseph decided on 2026-11-24 about (b), 185, the 5D block pricing and the old namespace.
**NOT CITABLE FOR:** any result, any threshold's pass probability (not yet simulated), any note wording.
