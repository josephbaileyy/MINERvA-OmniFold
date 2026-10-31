# RECORD — the WAITING-JOSEPH rows triaged: what is his, what is already decided, what is moot (2026-10-31)

**By** the close-items session, on the director's order of 2026-10-31, relaying Joseph's question: can the items
waiting on him be resolved without him, or do they have an obvious better choice? Read-only: `git grep`, `git log` and
`git show` at `990cce3c6`, plus two inputs from Joseph relayed by the director (§2). No cluster connection, no compute.

**CITABLE FOR:**
- one proposal per row: (R) resolvable without Joseph, (D) his decision, or (S) stale or moot;
- Joseph's Iris reading for OI-52, and the HPSS ledger that explains it (§2);
- the sizing of OI-131(a)'s candidate subset (§3);
- OI-151's retirement, on Joseph's decision (§4).

**NOT CITABLE FOR:**
- any ruling on the other fourteen rows. They are proposals; the register changes only for OI-151;
- HPSS or CFS state after the last committed reading, except Joseph's Iris figure.
<!-- absence-ok: scoping statements about what this record covers -->

## 1. The table

| row | proposal | ground |
|---|---|---|
| OI-29 | **S** | The 1431-bin covariance it asks MINERvA to endorse is no longer a publication product: *"These are audit descriptors, not publication uncertainties"* (`app_history.tex:226`). The open-data terms say *"We do not require MINERvA review of non-MINERvA manuscripts"* (`docs/publication/RELEASE-INVENTORY-20261005.md:38-39`). The paper's precedent premise was settled on 08-02 (`COLLABORATOR_QUESTIONS.md`). |
| OI-30 | **R** | The analysis has adopted the definition. The paper defines `E_avail` with *"a defined constant of 135 MeV … The constant defines the reported observable and is used consistently by the analysis and every prediction"* (`paper_body.tex:35`). On 2026-10-28 Joseph moved the 135 MeV sensitivity sentence to the note, and the record states *"The observable's definition stays"* (`DECISION-20261028-joseph-r19-variant-b-and-moves.md` item 2, O6). The row's materiality step was for a mis-set constant, so a defined constant needs none. The rule mismatch lives at OI-56, which is deferred. Caveat: "the definition stays" is the recorder's wording. If the director wants Joseph's own words: *"Keep 135 MeV as the defined charged-pion constant, as the paper prints it?"* |
| OI-31 | **D** | The study the row offered as its second route was run: KI 26 *"RESOLVED 2026-09-23 — quantified"*, medians of 0.4–0.7%, at the estimator-noise scale (`RESULT-20260923-issue26-issue5.md`). Only adopting the proposed band is left (Q1). |
| OI-35 | **D** | The note already prints *"NEUT … is not included"* (`sec_3d.tex:128`) and lists it as an outlook refinement (`sec_summary.tex:20`). Asking NEUT's maintainers is a contact, so it is his (Q2). |
| OI-50 | **R** | The measurement the row asked for is done: `hsi hashverify` over the quoted archive, **PASS 36/36**, rc 0, read back from tape (`RECEIPT-20260820-oi50-hashverify.md:3-4`). Its line 7, *"a claim for Joseph"*, is the measuring lane declining to discharge its own item, and no rule makes it his. Fallback, one line: *"Retire OI-50 on the 36/36 PASS?"* |
| OI-51 | **D** | An email to Ben Nachman, his relationship (Q3). The row's text is stale: it was written against 265.1% and an August move. |
| OI-52 | **R, retire** | Joseph read Iris on 2026-10-31, as the row asked. §2 records the reading and its ledger. The row's premise (*"Only he can read Iris"*) was already false (third-batch record). |
| OI-59 | **R, retire** | The missing caveat is printed. `sec_3d.tex:206` says the two analyses *"define true `E_avail` differently"*, gives the 11.0% migration (*"That shift has the sign and location of the residual"*), says the aggregate *"has not been computed"* and leaves it *"an alternative explanation that is not excluded"*. No pulls or χ² are reported, so the old `PASS (consistent)` is not printed. The super-grid computation is OI-56's arithmetic, and OI-56 is `deferred`. No freeze question remains for the paper. |
| OI-60 | **S**, retrospective half | The row's own recommendation is a documentary close. The family is PET's Gate-5 `C_stat`, and *"No PET covariance … is adopted as a publication uncertainty product"* (`sec_pet.tex:4`; Joseph, 2026-08-20, `AGENTS.md:17-18`). The re-run half is already deferred to the next Gate-5 re-issue, so the row becomes `deferred` on that trigger. |
| OI-71 | **S** | It asks whether PET recovery evidence (`VL100`) may be quoted. PET is diagnostic (`AGENTS.md:17-18`), and the note says *"No current real-data PET–GBDT level of agreement is quoted"* and withdraws the legacy closure level (`sec_pet.tex:110`). Search: `git grep -n -E 'VL100\|0\.5126'` over `docs/analysis-note/*.tex`, records views excluded, @ `990cce3c6`: no hits. Any future quote needs OI-126's equivalence and coverage evidence first (`sec_pet.tex:4`). |
| OI-75 | **D** | Whether the 2026-08-08 stage-3 run was authorized is his question by the row's own terms. A good receipt attests provenance, not permission (Q4). |
| OI-131(a) | **D** | §3: nothing quoted descends from any of the 240 objects, and no meaningful subset fits the headroom (Q5). |
| OI-131(b) | **fix the register** | §3. |
| OI-137 | **D** | Joseph's Ruling 7 settled the policy, and the note carries it (`app_statmethods_nd.tex:16, 19`: *"No generic correction is prescribed"*). What is left is naming the session that holds Ruling 7's role. The fourth-batch record calls that Joseph's act (Q6). |
| OI-151 | **retired here** | Joseph chose (C) (§4). |
| OI-188 | **S** | Its five findings grade the seven-cause board, which has not changed since 2026-09-02. That campaign runs under R5, whose stop fired on 2026-09-30, and R5 says *"Continuing past the stop requires a fresh decision; continuation is not the default"* (`DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md:143-144`). The 09-24 activation superseded R5 only for the new scalar-5D campaign (`AUTHORIZATION-20260924-scalar5d-campaign-activation.md:35-36`, table row S1 at `:103`). Search: `\bR5\b\|seven[- ]cause\|SCOREBOARD` in every `DECISION-*` dated 2026-09-30 or later @ `990cce3c6`. Three hits, all a different 2D "R5". No fresh decision is recorded, so R5's default answers (d). |
<!-- absence-ok: the searches and sha are named in the rows that make absence claims -->

## 2. OI-52 — Joseph's Iris reading, and what has filled HPSS since August

**The reading (Joseph, Iris, 2026-10-31), as relayed by the director:** user quota **446 GB used of 512 GB**.

**Which quota this is.** It is the HPSS user quota, by the 512 match. Every committed `hpssquota` and
`showquota --hpss` reading prints the line `josephrb usage on HPSS charged to m3246` against **512.00 GiB**. The 2026-10-23
Iris reading in `state/measurement-scoping/iris-20261023.txt` is the CPU and GPU node-hour allocation, a different
quantity. So the ~66 GiB of headroom is 512 − 446. That subtraction is arithmetic on Joseph's figure, which is in the
unit Iris printed.

**The readings, from committed receipts:**

| when (UTC) | used, GiB | source |
|---|---:|---|
| 2026-08-21 21:43 | 300.17 | `state/negweight-hpss-20260821/quota_before.txt` |
| 2026-09-24 | 300.20 | `state/s5c/d3/hpssquota-before.txt` |
| 2026-09-25 08:04 | 347.90 | `RECEIPT-20260925-d3-hpss-backup-of-nine-sole-copy-objects.md:57` |
| 2026-10-14 23:17 | 350.90 | `state/2d-closeout/preservation-20261014/outputs/showquota_hpss.txt` |
| 2026-10-25 00:36 | 353.98 | `S1-PRESERVE-REPORT.md:46` |
| 2026-10-25 21:54 | 422.78 | `FD-F0-REPORT.md:65, 80` |
| 2026-10-28 22:09 | 422.79 | `FD-CT-PRESERVE-REPORT.md:62` |
| 2026-10-29 | 444.50 | `FD-CT-3B-REPORT.md:171` |
| 2026-10-31 | 446 | Joseph, Iris |

`hpssquota` lags writes by hours to days. Every report since August says so, so readings move in steps.

**What the 300.17 GiB of August was:** the quoted archive `mnv-quoted-products-20260812` alone, 322,306,102,132 B =
300.17 GiB (`RECEIPT-20260820-oi50-hashverify.md:3`). It is still there.

**What has been written since, from the committed archive receipts:**

| date | archive | bytes | GiB |
|---|---|---:|---:|
| 08-21 | negweight historical, 5 objects (`RECEIPT-20260821-negweight-hpss-durability.md:35`) | 29,144,842 | 0.03 |
| 09-25 | D3: the nine sole-copy scalar-5D objects, `std_final5_candidate.root` 42.3 GB among them (`RECEIPT-20260925-d3-…:24`) | 51,218,246,681 | 47.70 |
| 10-08/09 | second copies of the s5p archive and `z-cv.npz` (`hsi du` 373,553,509,414 → 376,773,649,398 B; `RECORD-20261008-followups-g11-g12-preservation.md:60, 305`) | 3,220,139,984 | 3.00 |
| 10-23 | Stage 0 Part P inputs tar (`STAGE0-PRESERVE-REPORT.md:20`) | 3,303,587,840 | 3.08 |
| 10-24 | RE-2 part B and part C bundles (`re2/run/hpss/logs/7-du.log`, `partc_r2/…/7-du.log`) | 133,685,575 | 0.12 |
| 10-25 | **S1: the bank and detector dump** (`S1-PRESERVE-REPORT.md:61`) | 73,709,649,920 | **68.65** |
| 10-25 | F0 tar (`FD-F0-REPORT.md:89`) | 14,888,960 | 0.01 |
| 10-28 | F1 inputs tar (`FD-F1-REPORT.md:275`) | 1,229,916,160 | 1.15 |
| 10-28 | **the cheap tier's 42 npz** (`FD-CT-PRESERVE-REPORT.md:45`) | 22,076,692,480 | **20.56** |
| 10-29 | 3B closures tar (`FD-CT-3B-REPORT.md` §4) | 2,478,080 | 0.00 |
| 10-30 | 5B per-period unfolds tar (`FD-CT-5B-REPORT.md` §7) | 1,580,871,680 | 1.47 |
| | **sum** | | **145.77** |

Arithmetic: 300.17 + 145.77 = **445.94 GiB**, against Joseph's 446. The small gap is the sidecar files the tables leave
out, such as digests and indexes. Three archives account for 94% of the growth: **S1 (68.65), D3 (47.70) and the
cheap tier (20.56)**. Each was a preservation step that a binding or a Joseph decision required.

The 2026-10-29 retention decision's A1 archive (about 25 MB, `DECISION-20261029-joseph-retention-archive-a1.md`) has
no committed write receipt. Search: `git grep -n -i -E 'josephrb/mnv-[a-z0-9-]*(a1|retention)'` @ `990cce3c6`, outside
`fd/`: no hits. At 25 MB it does not change the total.
<!-- absence-ok: the search and sha are named in this paragraph -->

**Proposal: retire OI-52.** The reading it asked for now exists, taken by Joseph. The row's own residual clause
(*"state what it is, or close the row"*) is met.

**For whoever writes next to HPSS:** about 66 GiB remains. That is less than one more S1-sized archive.

## 3. OI-131 — the 240 CFS-only P3F objects

**What they are** (`state/hpss-footprint-and-dedup-20260813.json`, `QUESTION_2` and `QUESTION_4`):
- 120 ROOTs, `runEventLoopOmniFold_P3F_PET_FE_<universe>_<playlist>.root`, totalling 1,134,996,735,477 B =
  **1,057.0 GiB**;
- 120 Gate-3 JSON receipts, totalling 1,494,806 B;
- ten lateral universes (`BeamAngleX/Y`, `Muon_Energy_MINERvA/MINOS`, `MuonResolution`, ±1 each) times twelve
  playlists (`p3f_files.txt`).

They are the *"selection-shifted full-event lateral endpoint ROOTs"*, the inputs to a PET full-event detector block
(`nd-unfolding/PET_UQ_REMEDIATION_STATUS.md:54-58`). That block does not exist in any form.
<!-- absence-ok: reports the cited status record's own statement (:57-58, "it does not exist in any form"); this record did not search for the block -->

**What the paper or note quotes from them: nothing.**
- The only code that names them is their producer, `nd-unfolding/pet/sbatch_p3f_pet_fullevent_evloop_array.sh`.
  Search: `git grep -l -E 'P3F_PET_FE|P3F_PET_receipt'` @ `990cce3c6`. The other six hits are the migration and
  footprint records.
- The note says *"No PET covariance, historical recoil-only or full-event, is adopted as a publication uncertainty
  product"* (`sec_pet.tex:4`). It adds that a replacement detector block *"would need … the selection-complete FPS
  lateral samples"* (`app_history_pet.tex:103`).
- No estimator in `registry/ESTIMATORS.tsv` is a PET estimator.
<!-- absence-ok: the search and sha are named in this paragraph -->

**So the "irreplaceable subset" behind a quoted number is empty.**

**The sizes against ~66 GiB of headroom:**

| candidate subset | size | fits? |
|---|---:|---|
| all 240 | 1,057.0 GiB | no, 16× the headroom |
| one universe, all 12 playlists | ~106 GiB if the universes are of similar size (not measured per universe) | no |
| one playlist, all ten universes | 12.4 GiB (1L) to 186.3 GiB (1M) | the smaller ones fit, but a single playlist is 1/12 of every universe and is not usable alone (`QUESTION_4`) |
| the 120 receipts | 1.5 MB | yes. They are provenance for a product nothing quotes |

**Proposal for (a):** Q5. Recommended: no second copy, and retire (a).

**(b): fix the register.**
- The row's state cell says (b) was *"DISCHARGED BY MEASUREMENT, 2026-08-20T20:47:10Z"*: `hpssquota` read 300.17 GiB,
  58.6%, twice from two hosts. The 2026-08-21 negweight receipts read the same 300.17.
- The register still shows `OI-131(b)` as `BLOCKED-EXTERNAL`, owner `storage`.
- A leaf row cannot carry its own lifecycle (`control_plane_lint.py:412-414`), so the fix is to delete the
  `OI-131(b)` leaf row from `work-items.tsv`, with a dated prefix on the OPEN_ITEMS row.
- If Q5 is answered "no", OI-131 retires whole, and both leaf rows go.

## 4. OI-151 — retired

Joseph chose (C) on 2026-10-31: *"OI-151 lets do (C)"*. In
[`DECISION-20261031-joseph-oi151-option-c.md`](DECISION-20261031-joseph-oi151-option-c.md#what-is-decided), item 2 says
*"OI-151 is retired by the close-items session, citing this record."* The laptop is not a usage host, and quota is
read on a Perlmutter login node. No credential directory, `profiles.json` or validator is changed.

**Dependency check.** Search: `git grep -n -E 'OI-151([^0-9]|$)'` @ `990cce3c6`, excluding `OPEN_ITEMS.md`, the
control plane and the generated views. The hits are the decision, its CATALOG row, and two earlier close-items records
that describe its history. None routes open work to the row.
<!-- absence-ok: the search and sha are named in this paragraph -->

## 5. The questions for Joseph, as a batch

Each question has a recommended answer and its cost.

- **Q1 (OI-31).** *"Adopt the proposed ±10% `E_avail`-scale envelope as a per-bin systematic?"*
  - Recommended: **no**. Record the 1.17 common scale as quantified, and retire OI-31.
  - Why: the shifts are the size of the estimator-seed band and do not grow with the rescale. The result's own
    caveat says a band *"may partly double-count"* the ML/seed block, an overlap it calls unmeasured
    (`RESULT-20260923-issue26-issue5.md:110-112`).
  - The same caveat says the study does **not** cover a data/MC *relative* `E_avail` response
    (`:112-114`). That is a different question from the common scale. The 5D total has since adopted the
    species-response block `C_resp` (`DECISION-20261026-joseph-adopt-cresp.md`). Whether `C_resp` covers it is not
    checked here.
  <!-- absence-ok: reports the cited result's own caveat (RESULT-20260923-issue26-issue5.md:110-114), quoted; the last sentence scopes what this record did not check -->
  - Cost of yes: an uncertainty-model change on the 3D and 5D covariances, with rebuilds.
- **Q2 (OI-35).** *"Ask NEUT's maintainers for access, for a fifth generator?"*
  - Recommended: **no, retire**. The note already treats NEUT as an outlook item.
  - Cost of yes: your email, then a build, a run and a comparison pass, all unpriced here.
- **Q3 (OI-51).** *"Did the August reply to Ben go out, or is it no longer needed?"*
  - Recommended: **retire either way**. The row's message was written against the August numbers.
  - If HPSS headroom ever needs his help, that is a new request, about the ~66 GiB in §2.
  - Cost: none.
- **Q4 (OI-75).** *"Leave the 2026-08-08 standard-P4 stage-3 run unratified, and close OI-75 as historical?"*
  - Recommended: **yes**.
  - Its products stay consumption-only under your 2026-09-15 grant.
  - The derived `std_final5_candidate.root` is on tape (D3, §2).
  - No live quoted number descends from the standard-P4 chain (OI-7's reach check).
  - Cost: none. Ratifying instead would owe the landing set (products summary, ledger, RUN_LOG and STATUS) and one
    cluster read.
- **Q5 (OI-131(a)).** *"Keep the 240 P3F objects single-copy on CFS, with no second copy?"*
  - Recommended: **yes, and retire OI-131**. Nothing quoted descends from them, and only the 1.5 MB of receipts would
    fit.
  - Cost of no: more HPSS (about 1,057 GiB, 16× the headroom), or a second CFS copy. CFS held 2,512 GiB after the
    data AnaTuples copy (`RECORD-20261008-followups-g11-g12-preservation.md:294`), so another 1,057 GiB passes the
    3 TB rule.
- **Q6 (OI-137).** *"May the director designate the session that holds Ruling 7's statistics-owner role?"*
  - Recommended: **yes**. That turns a role assignment into routing.
  - The work itself needs no compute: the item-(v) declarations for each block of the adopted 5D covariance, and a
    recommendation back to you.
  - Cost: one read-only lane.

The register is changed only for OI-151. Every other row waits on the director's ruling, or on Joseph's answers to
Q1–Q6.
