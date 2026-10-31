# RECORD — Joseph's Q1–Q6 answers enacted: five rows retired, OI-137 owner set, UD-002 decided (2026-10-31)

**By** the close-items session, on the director's order of 2026-10-31, after #596 merged. Verbatim: *"retire OI-31,
OI-35, OI-51 and OI-131 whole (the OI-131(b) leaf deleted); close OI-75 as historical; set OI-137's owner to
coverage-5b-audit, as designated, still WAITING until that session takes it; mark UD-002 DECIDED in USER-DECISIONS.md
with Joseph's verbatim words and digest from the record; correct the stale OI-50/OI-55 pointers beside
USER-DECISIONS.md:37 and SESSION-WORKFLOW.md:159. Leave LIVE-STATE.md alone."*

**CITABLE FOR:** the register changes to six rows, the new owner row, UD-002's move to `DECIDED`, and the two
corrected HPSS pointer sentences.

**NOT CITABLE FOR:** any new measurement or decision. Every ground is one of Joseph's two decision records of
2026-10-31, or the triage record
([`RECORD-20261031-close-items-waiting-joseph-triage.md`](RECORD-20261031-close-items-waiting-joseph-triage.md), #594).
Nothing was run, and the cluster was not touched.
<!-- absence-ok: a scoping statement about this record's own method -->

**The two decision records:**
- [`DECISION-20261031-joseph-triage-q1-q2-q4-q5.md`](DECISION-20261031-joseph-triage-q1-q2-q4-q5.md#what-is-decided)
  (#600), for OI-31, OI-35, OI-75 and OI-131;
- [`DECISION-20261031-joseph-oi51-oi137-ud002.md`](DECISION-20261031-joseph-oi51-oi137-ud002.md#what-is-decided)
  (#603), for OI-51, OI-137 and UD-002.

**The digests, re-measured.** For each of Joseph's six answers, `printf '%s\n' "<answer>" | shasum -a 256` gives
the prefix the record prints: `131cc916d4d58e96` (OI-31 and OI-35, the same text), `17d74ee87a8acd04` (OI-75),
`3d9a8d6d6184c748` (OI-131), `bdac7abc93ad9db8` (OI-51), `1fa97d43de952918` (OI-137) and `2f53fcc2fb3a1160`
(UD-002).

**Register-only:**
- OI-31, OI-35, OI-51, OI-75 and OI-131 are set to `retired`, with owner `close_items`.
- The `OI-131(a)` and `OI-131(b)` leaf rows are deleted.
- OI-137 keeps `active` and `WAITING-JOSEPH`, and its owner becomes `coverage-5b-audit`, a new row in `owners.tsv`.

Each OPEN_ITEMS row gets a dated prefix, and the text below the prefix is left as it stood.

## 1. OI-31 retired

Joseph: *"No, retire (Recommended)"*, to *"adopt a ±10% E_avail-scale envelope as an extra per-bin systematic?"*
The envelope is not adopted. The 1.17 common scale is recorded as quantified (`KNOWN_ISSUES.md` issue 26,
`RESOLVED 2026-09-23`). The relative-response question stays with `C_resp` (decision item 1). Ground: triage §5, Q1.

## 2. OI-35 retired

Joseph: *"No, retire (Recommended)"*, to *"ask NEUT's maintainers for access, to add a fifth generator?"* NEUT stays an
outlook item, and no request is made (decision item 2). Ground: triage §5, Q2.

## 3. OI-51 retired

Joseph: *"Retire it (Recommended)"*. The reply to Ben was written against August's numbers. Any future HPSS headroom
request, with about 66 GiB left, is a new one (decision item 1). Ground: triage §5, Q3.

## 4. OI-75 closed as historical

Joseph: *"Yes, close it (Recommended)"*. The 2026-08-08 standard-P4 stage-3 run stays unratified. Its products stay
consumption-only under the 2026-09-15 grant (decision item 3).
- The register has no lifecycle for "historical", so the row is `retired`.
- The prefix says the run is not ratified.
Ground: triage §5, Q4.

## 5. OI-131 retired whole, both leaves deleted

Joseph: *"Yes, single copy (Recommended)"*. The 240 P3F objects stay single-copy on CFS, since nothing quoted descends
from them (decision item 4; sizing in triage §3).

**Both leaf rows go, not only (b).**
- The decision names the (b) leaf: *"The register's OI-131(b) leaf goes with it."*
- The (a) leaf must go too. A leaf whose source row is not active fails the lint: *"promoted leaf points to … source"*
  (`control_plane_lint.py:420-422` @ `4ede47e34`).
- Triage §3 said the same: *"If Q5 is answered "no", OI-131 retires whole, and both leaf rows go."* Q5 asked about a
  second copy, and "single copy" is that "no".

## 6. OI-137: owner coverage-5b-audit, still waiting

Joseph: *"Yes, designate one (Recommended)"*. The director designated the session `coverage-5b-audit` as Ruling 7's
*"scalar-5D adoption/statistics owner"*. It takes the role once its current work closes (decision item 2).

**Register:**
- the owner becomes `coverage-5b-audit`;
- the row stays `active`, `WAITING-JOSEPH`, `backlog`, as the director ordered.

**`owners.tsv` gains one row:** `coverage-5b-audit`, *"scalar-5D adoption/statistics owner (Ruling 7), designated
2026-10-31"*, holder *"coverage-5b-audit session"*, escalation Joseph, `assigned`. The holder carries no session id,
because none is in the decision record.

The work is item (v): a declaration for each block of the adopted 5D covariance, and a recommendation back to Joseph.
It is read-only and needs no compute. When the session takes it, the queue token should change. `WAITING-JOSEPH` will
then describe a step that has already happened; `NOW` or `BLOCKED-INTERNAL` would describe the work.

## 7. UD-002 decided

Joseph: *"Keep 135 MeV (Recommended)"*. The question was *"UD-002: keep 135 MeV as the defined constant in the
E_avail definition (the paper already says 'a defined constant of 135 MeV'; the alternative was 139.57 MeV)?"*
(decision item 3).

**In `USER-DECISIONS.md`:**
- the row leaves *Active decisions*;
- an entry in the file's own template is added under *Recorded decisions*, with the verbatim answer, its digest, the
  source and the two commit times;
- the agent's reading is in a separately labelled field, as the rules at `:10-11` require.

**No implementation is owed.** The paper says the constant *"is used consistently by the analysis and every
prediction"* (`docs/analysis-note/paper_body.tex:35` @ `4ede47e34`). The entry stays `DECIDED`, not `IMPLEMENTED`,
because the director asked for `DECIDED`. No commit implements it.

## 8. The HPSS pointers corrected

`USER-DECISIONS.md:37-38` and `SESSION-WORKFLOW.md:159-161` sent HPSS actions to *"`OI-50`/`OI-55`"*. Both are
`retired`, and so is OI-52.

Both sentences now say three things:
- the three rows are retired;
- the latest reading is in
  [`RECORD-20261031-close-items-waiting-joseph-rows-retired.md`](RECORD-20261031-close-items-waiting-joseph-rows-retired.md#4-oi-52-retired-with-josephs-iris-reading)
  §4 (446 of 512 GiB on the user quota, 2026-10-31, about 66 GiB headroom);
- a new HPSS action is filed as a new open item.

Both files are `LIVE` in `MANIFEST.tsv`, so they are edited in place.

## 9. Dependency check

Search: `git grep -l -E 'OI-<N>([^0-9]|$)'` for OI-31, OI-35, OI-51, OI-75, OI-131 and OI-137, and `git grep -n
'UD-002'`, @ `4ede47e34`. The searches excluded `OPEN_ITEMS.md`, the control plane, the generated views,
`MANIFEST.tsv`, `CATALOG.md`, the triage record and the two decision records. Each hit file was classed by
`MANIFEST.tsv`. ARCHIVAL hits are history.
<!-- absence-ok: the search and sha are named in this paragraph -->

**LIVE hits and files outside the manifest.** None routes open work to a retired row.
- **OI-31:**
  - `KNOWN_ISSUES.md:23`, issue 26, is already `RESOLVED 2026-09-23 — quantified`.
  - The study's code (`eavail_scale_study.py`, `compare_eavail_scale.py`, `sbatch_eavail_scale_study.sh`) and
    `RESPONSE_MISMATCH_CLOSURE.md:67` name it as provenance.
  - `ARTICLE-READINESS-20261006.md:46`, the s5c campaign table, the 08-22 readiness and the 08-22 walkdown list it as
    open. They are dated assessments.
- **OI-35, OI-51:** the backlog view, regenerated here, and the dated 08-22 readiness.
- **OI-75:**
  - `P4_STANDARD_STATUS.md:194` and `Z_PILOT_EXECUTION_DECLARATION.md:92-103` escalate to it. The decision now answers
    that escalation: the run stays unratified and its products stay consumption-only.
  - `LIVE-STATE.md:18` lists it as `WAITING-JOSEPH`. It is left alone, on the director's order.
  - The hit in `docs/analysis-note/values.tex:7` is not read further or edited.
- **OI-131:**
  - `LIVE-STATE.md:20-21` still lists both leaves. It is left alone.
  - `POST_PUBLICATION_REORG_PLAN.md:282` names the (b) leaf as left for its owner, since *"the lint gives a leaf row no
    retirement except deletion"*. This record does that deletion. The plan is a dated account and is not edited.
  - `control_plane_lint.py:526` and `generate_live_state.py:322` use OI-131 in comments as the example of a decomposed
    record. After this record no row is decomposed. Neither comment changes behaviour, and neither is edited.
  - The other hits are history: the 08-22 readiness, the 09-24 activation and handoff, and the r22 method fixtures.
- **OI-137:** the briefs, packets, reviews and the declaration-(v) provenance describe the work this owner will take.
  They route to the row, and the row is still active.
- **UD-002:** `sec_3d.tex:43`, a search comment in the note, and the 10-27 absence-audit transcript name it. Both
  record what was true when written.

## 10. Not changed

- `LIVE-STATE.md`, on the director's order.
- Every claim, number and storage object.
- No file under `docs/analysis-note/**` or `fd/**` is touched.
- The lint and live-state comments in §9 are left as they are.
