# RECORD — seven WAITING-JOSEPH rows retired and OI-60 deferred, register-only (2026-10-31)

**By** the close-items session, on the director's ruling of 2026-10-31, after #594 merged. Verbatim: *"I'm ruling the
R and S rows myself, since each rests on a record you cited: retire OI-30, OI-50, OI-52, OI-59, OI-29, OI-71, OI-188,
and OI-60's retrospective half (its rerun half stays deferred)."* For OI-188: *"the record says the 09-30 stop stands
because no continuation decision exists. Retiring records that it is not continued."* For OI-52: *"record Joseph's
Iris reading (446 of 512 GiB HPSS user quota, 2026-10-31), with your arithmetic and the ~66 GiB headroom."*

**CITABLE FOR:** the register changes to the eight rows, the ground each rests on, and Joseph's Iris reading (§4).

**NOT CITABLE FOR:** any new measurement apart from Joseph's Iris figure. Each ground is a section of
[`RECORD-20261031-close-items-waiting-joseph-triage.md`](RECORD-20261031-close-items-waiting-joseph-triage.md) (#594),
which was read-only at `990cce3c6`. This record touches nothing on the cluster.
<!-- absence-ok: a scoping statement about this record's own method -->

**Register-only:**
- seven rows are set to `retired`, with owner `close_items`;
- OI-60 is set to `deferred`, with owner `unassigned`, as the 2026-10-29 deferrals were.

Each row's authority is its section here. Each OPEN_ITEMS row gets a dated prefix, and the text below the prefix is
left as it stood. Q1–Q6 of the triage record go to Joseph. OI-31, OI-35, OI-51, OI-75, OI-131 and OI-137 are not
changed.

## 1. OI-29 retired

The collaboration endorsement it asks for concerns the 1431-bin covariance, and that covariance is no longer a
publication product: *"These are audit descriptors, not publication uncertainties"* (`app_history.tex:226`). The
MINERvA open-data terms say *"We do not require MINERvA review of non-MINERvA manuscripts"*
(`docs/publication/RELEASE-INVENTORY-20261005.md:38-39`). Ground: triage record §1.

## 2. OI-30 retired

The analysis defines the observable with the constant. The paper says it *"subtracts a defined constant of
135 MeV … The constant defines the reported observable and is used consistently by the analysis and every prediction"*
(`paper_body.tex:35`). Joseph's 2026-10-28 decision moved the 135 MeV sensitivity sentence to the note and records
that *"The observable's definition stays"* (`DECISION-20261028-joseph-r19-variant-b-and-moves.md` item 2, O6).

The row's materiality step tested a mis-set constant, so a defined one needs none. The species-rule mismatch is OI-56,
which is deferred. Ground: triage record §1.

## 3. OI-50 retired

The measurement the row asked for is done. `hsi hashverify` over `mnv-quoted-products-20260812` gave **PASS, 36 of 36
`(md5) OK`**, rc 0, read back from tape (`RECEIPT-20260820-oi50-hashverify.md:3-4`). Ground: triage record §1.

## 4. OI-52 retired, with Joseph's Iris reading

**The reading (Joseph, Iris, 2026-10-31):** **446 of 512 GiB used**, on the HPSS user quota. The 512 matches the
line `josephrb usage on HPSS charged to m3246` against 512.00 GiB in every committed `hpssquota` and
`showquota --hpss` reading.

**The arithmetic** (triage record §2):
- In August the 300.17 GiB was the quoted archive `mnv-quoted-products-20260812` alone, 322,306,102,132 B.
- The archive receipts committed since then add **145.77 GiB**, so 300.17 + 145.77 = **445.94 GiB**, against
  Joseph's 446. The remaining fraction is sidecar files the receipts leave out, such as digests and indexes.
- Three archives account for 94% of the growth:
  - S1's bank and detector dump, 68.65 GiB (2026-10-25);
  - D3's nine sole-copy scalar-5D objects, 47.70 GiB (2026-09-25);
  - the cheap tier's 42 npz, 20.56 GiB (2026-10-28).

**Headroom:** 512 − 446 = **~66 GiB** (arithmetic on Joseph's figure). That is less than one more S1-sized archive.

The row asked for an authoritative reading, and its residual clause was *"state what it is, or close the row"*. Both
are met. Ground: triage record §2.

## 5. OI-59 retired

The caveat the row found missing is printed in `sec_3d.tex:206`. It says:
- the two analyses *"define true `E_avail` differently"*;
- the 11.0% migration *"has the sign and location of the residual"*;
- the aggregate over the compared bins *"has not been computed"*;
- the difference *"remains an alternative explanation that is not excluded"*.
<!-- absence-ok: quotes the note's own sentences at sec_3d.tex:206; this record makes no absence claim of its own -->

No pulls or χ² are reported, so the old `PASS (consistent)` is not printed. The super-grid computation is OI-56's
arithmetic, and OI-56 is deferred. Ground: triage record §1.

## 6. OI-60 deferred: its retrospective half retired

**The retrospective close is retired.** The row's own recommendation was to close it documentarily, with the
151.175 A100-h figure recorded. The family it concerns is PET's Gate-5 `C_stat`, and the note says *"No PET
covariance … is adopted as a publication uncertainty product"* (`sec_pet.tex:4`; Joseph, 2026-08-20,
`AGENTS.md:17-18`).

**The re-run half stays deferred.** Trigger, from
[`RECORD-20261029-close-items-conditional-proposals-ruled.md`](RECORD-20261029-close-items-conditional-proposals-ruled.md):
*"the next Gate-5 re-issue whenever one happens for an independent reason"*. The row's own limit stands: the fix must
not motivate that re-issue.

## 7. OI-71 retired

The row asks whether PET recovery evidence (`VL100`) may be quoted. PET is diagnostic (`AGENTS.md:17-18`). The note
says *"No current real-data PET–GBDT level of agreement is quoted"* and withdraws the legacy closure level
(`sec_pet.tex:110`), and no build prints `VL100` (triage record §1, with its search). Any future quote needs OI-126's
equivalence and coverage evidence first (`sec_pet.tex:4`).

## 8. OI-188 retired: the seven-cause campaign is not continued

Its five findings grade the seven-cause board, which has not changed since 2026-09-02. That campaign runs under R5,
whose stop fired on 2026-09-30. R5 says *"Continuing past the stop requires a fresh decision; continuation is not the
default"* (`DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md:143-144`). The 2026-09-24 activation
superseded R5 only for the new scalar-5D campaign (`AUTHORIZATION-20260924-scalar5d-campaign-activation.md:35-36`,
row S1 at `:103`). No continuation decision is recorded (triage record §1, with its search).

**This retirement records that the seven-cause campaign is not continued past the 2026-09-30 stop.** If Joseph ever
continues it, the five findings are in the row, unchanged.

## 9. Dependency check

Search: `git grep -n -E 'OI-<N>([^0-9]|$)'` for each of the eight ids @ `73107b2f7`, excluding `OPEN_ITEMS.md`, the
control plane, the generated views, `MANIFEST.tsv`, `CATALOG.md` and the triage record. Each hit file was classed by
`MANIFEST.tsv`. ARCHIVAL hits are history.
<!-- absence-ok: the search and sha are named in this paragraph -->

**LIVE hits and files outside the manifest:**
- **OI-30:** `docs/orchestration/USER-DECISIONS.md:24`, row UD-002, `NEEDS JOSEPH`: *"Choose whether the production
  definition should retain exact MAT behavior (`135` MeV subtraction) or use the physical charged-pion mass"*.
  - This is the one live route to a retired row.
  - The register's rules require Joseph's verbatim words to move a row to `DECIDED` (`:9-11`).
  - The ground in §2 is the paper's text and the recorder's wording, not his words on this choice. So this record does
    **not** edit UD-002, and the director is told.
  - The 2026-09-24 campaign table (`CAMPAIGN-s5c-20260924-paper-wide-table.md:35, 125-126, 162, 202, 380`) makes OI-30
    part of R4's closure criterion, and `docs/publication/ARTICLE-READINESS-20261006.md:46` lists it as open. Both are
    dated assessments and stay as they are.
  - `docs/EAVAIL_DEFINITION.md` indexes OI-30 as history.
- **OI-50:** `USER-DECISIONS.md:37` and `SESSION-WORKFLOW.md:159` point HPSS retention and verification actions to
  *"`OI-50`/`OI-55`"*. OI-55 is already `retired` in the register, so after this record the pointer names two retired
  rows. It is a pointer sentence, not a work route, and is left for the director: the live HPSS facts are in §4 here
  and in the triage record §2.
- **OI-29:** `PUBLICATION-READINESS-20260822.md:273, 414, 1134` lists it as an open publication item. That is a dated
  assessment.
  - `nd-unfolding/pet/gate5_cstat_contract.json:216` holds the question *"does OI-29's already-disclosed treatment
    extend to this 262-cell object"*. It is a frozen PET Gate-5 operand. PET is diagnostic, and the file is not
    edited.
- **OI-71:** `LIVE-STATE.md:17` still lists the row as `WAITING-JOSEPH`. That file is generated by
  `generate_live_state.py`, from a snapshot of 2026-10-29, and is not regenerated here.
  - The PET configuration-comparison records under `nd-unfolding/pet/configuration_comparison/` say *"nothing
    discharges `OI-71`"*. They describe their own scope, and they stay true.
- **OI-59, OI-60, OI-188:** history only, in the ledger, the E_avail definition record, the release READMEs, the PET
  status, a code comment (`reconcile_gate5_family.py:553`) and the 2026-09-02 rulings. None routes open work.
- **OI-52:** no LIVE hits.

## 10. Not changed

- Q1–Q6 of the triage record are with Joseph. OI-31, OI-35, OI-51, OI-75, OI-131 and OI-137 stay as they are.
- `USER-DECISIONS.md`, `LIVE-STATE.md` and the frozen PET contract are not changed.
- No file under `docs/analysis-note/**` or `fd/**` is touched.
