# DECISION PACKET — OI-53: who owns `CLAIMS.md` rows CLM-001..012 (2026-10-29)

**For** Joseph, through the director. **By** the close-items session, as backlog candidate 3.

**Read-only.** This packet edits no row of `CLAIMS.md` and no cell of `ROW-OWNERS.tsv`. The owners below are
**proposals**. The decision is Joseph's (`OI-53`; `ROW-OWNERS.tsv` header: *"The twelve stay UNASSIGNED until someone
RULES them"*). Everything here was measured at `origin/main` `d84124c50` on 2026-10-29.

**CITABLE FOR:** the state of the twelve rows and of the lanes that could own them, as of 2026-10-29.
**NOT CITABLE FOR:** an assignment, or the scientific standing of any claim.

## 1. The question

`OI-53` asks for an adjudication of `CLM` row ownership. All twelve rows are `UNASSIGNED` in
[`ROW-OWNERS.tsv`](ROW-OWNERS.tsv), and `whose_row.py` exits 2 (CANNOT CHECK) on them.

The table's `basis` column is subject-matter judgement, not an artifact derivation (the header's account, corrected
2026-08-18), and the header forbids back-filling `owner` from it. Session A's 2026-08 routing of CLM-001..008 to C, 009..011 to B and 012 to D
is that same reading. The row calls it *"A PROPOSAL, NOT EVIDENCE"*.

## 2. What `UNASSIGNED` blocks today

- **The gate only runs by hand.** `whose_row.py` judges a CLM row's owner only when someone runs
  `merge_guard.sh <LANE>` while resolving a conflict. The hook and CI run `--check-owners`, `--self-test`,
  `--check-ledger-ids` and `--check-oi-ids` (`.githooks/pre-commit:238-248`, `record-checks.yml:117-129`).
  `--check-owners` passes today with 12 `UNASSIGNED`.
- **Nobody edits the file.** `CLAIMS.md` last changed on 2026-08-18 (`b8a0e117e`). It is classed LIVE / open. Its
  twelve detail files, `CLAIM-CLM-001.md` … `CLAIM-CLM-012.md`, are ARCHIVAL / terminal.

So `UNASSIGNED` blocks nothing at present. It would bind only if a session edited a row and hit a conflict.

## 3. Who wrote each row

Every row was committed under the author name `Joseph Bailey`. Agent sessions committed under that name in July and
August: CLM-006's verifier field reads *"orchestrator harvest"*, CLM-011's *"fresh-context claude-school opus x3"*, and
CLM-012's *"single-source (this session)"*. So git authorship does not identify a lane. The introducing commit, the
row's own `independent verifier` field and the recorded `basis` are what exist.

| id | claim, short | status | introduced | verifier field (excerpt) | recorded `basis` |
|---|---|---|---|---|---|
| CLM-001 | PET event-feature path was dead; KNN coords defaulted | VERIFIED-CODE | `79e1bc52d` 2026-07-16 | codex V1 + claude-school V2 | C (PET) |
| CLM-002 | no truth-only feature reaches step 1 | VERIFIED-CODE | `79e1bc52d` | codex + claude-school | C (PET) |
| CLM-003 | omitted-muon stress closure | VERIFIED-NUMERIC | `79e1bc52d` | fe5v re-run (me) | C (PET) |
| CLM-004 | self-consistency closure on xps2 | VERIFIED-NUMERIC | `79e1bc52d` | fe5v re-run (me) | C (PET) |
| CLM-005 | FPS census on xps2 | VERIFIED-NUMERIC | `79e1bc52d` | codex recompute + me | C (PET) |
| CLM-006 | full-event estimator works end to end | VERIFIED-NUMERIC | `79e1bc52d` | orchestrator harvest of predeclared gates | C (PET) |
| CLM-007 | `measured_scalars` fallback defect | VERIFIED-CODE | `79e1bc52d` | codex V1 + me | C (PET) |
| CLM-008 | P5B engineering debt F2–F10 | VERIFIED-CODE | `79e1bc52d` | codex V1 | C (PET) |
| CLM-009 | sieve reduction / negweight-purity equivalence | VERIFIED-NUMERIC | `79e1bc52d` | codex-school V5; orchestrator hand-check | B (uncertainty) |
| CLM-010 | `niter` 2→3 as regularization | VERIFIED-NUMERIC | `82968d4f5` 2026-08-06 | agy, separate provider account | B (uncertainty) |
| CLM-011 | extended-FPS cross section not divided by a reco efficiency | VERIFIED-CODE | `d22dd2007` 2026-08-06 | fresh-context claude-school opus x3 | B (uncertainty) |
| CLM-012 | D2's 0.80 bar vs the reco-acceptance limit | VERIFIED-NUMERIC | `b06d30dc7` 2026-08-07 | single-source (this session); Joseph commissioned it | D (verifier) |

`79e1bc52d`'s subject is *"orchestration: fe-fps-campaign ledgers — P5A verification verdicts, CLM-001..009"*.

## 4. Which lanes still exist

- **Lanes A–D are gone.** Their last commits under those names were Lane A on 2026-08-15, Lane B on 2026-08-18, and
  Lanes C and D on 2026-08-19. Lane D's last commit is *"Checkout preservation inventory before the lane reset"*.
- **No A–D session is live.** `ListAgents` on 2026-10-29 lists three peers besides this session: the director
  `[8d862e]`, the paper-rewrite session `[f64680]` and the coverage session `[e069ad]`.
- **The registry still lists them.** `control-plane/owners.tsv` keeps rows `pet`, `lane_b`, `lane_c` and `lane_d`
  marked `assigned`, with holders "lane B/C/D". These are registry rows, not running sessions.
- **The owner vocabulary names nobody.** `ROW-OWNERS.tsv` defines `owner` as a FINDINGS lane letter, A–D.
  `whose_row._lane_key` would accept a control-plane `owner_id` such as `director` mechanically, but using one would
  change the header's COLUMNS definition. That change needs its own dated amendment.

## 5. Where each row is used now

- **CLM-010 and CLM-012 are cited by the analysis note** as the grounds for the pinned three-iteration policy, which
  the note marks *frozen*: `app_history_pet.tex:27` and `:77`, and `values.tex:100`. The paper-tighten (director) and
  paper-rewrite lanes edit those files.
- **CLM-009's subject is in the note without its id:** the sieve / negweight-purity equivalence in
  `app_negweight.tex:36` and `:57`.
- **CLM-011:** no note or paper sentence cites it. The note's FPS section shows a reconstruction-efficiency panel
  (`sec_fps.tex:19`) but does not state the rule.
  Search: `git grep -n -P "CLM-0(0[1-9]|1[0-2])"` and `git grep -n -i -E "reco(nstruction)?[- ]efficienc|epsilon_\{?reco|not divided"`
  over `docs/analysis-note/*.tex` and `measurement-paper/**/*.tex` @ `d84124c50`.
- **CLM-001..008 are PET claims.** PET is diagnostic and method development, not a publication product
  (`DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md` R6, `:160-162`; `pet_note.tex:35`). Their latest
  users are the 2026-09-18 PET configuration-comparison files, for example
  `nd-unfolding/pet/configuration_comparison/CLAIM_EVIDENCE_INDEX-20260918.md:151` and `:158`.

## 6. Options

### A — freeze the ledger; no owners needed (recommended)

Reclassify `CLAIMS.md` LIVE → ARCHIVAL / terminal, as its twelve detail files already are. Add a dated line to
`ROW-OWNERS.tsv`'s header saying the twelve stay `UNASSIGNED` because no row is edited. `OI-53` then retires as moot.

- **Cost:** one overrides row and one header line. No row edits.
- **Why recommended:**
  - nobody has edited the file in 72 days;
  - the owner vocabulary names no live session;
  - the note cites CLM-010 and CLM-012 as the grounds of a policy it already marks frozen.
- **What it leaves open:** a future edit to a row, or a new claim, would need an owner decided at that point.

### B — assign each row to a live owner

This needs a dated amendment to `ROW-OWNERS.tsv`'s COLUMNS so that `owner` may be a control-plane `owner_id`. It also
needs each named lane's acceptance.

| rows | proposed owner | why |
|---|---|---|
| CLM-009, CLM-010, CLM-012 | `director` | the note cites or uses them, and the paper-tighten lane keeps the note's citations consistent |
| CLM-011 | `director` | its subject is the extended-FPS cross-section construction, which the note's FPS section reports; no sentence cites it (§5) |
| CLM-001..008 | `joseph` | PET is diagnostic, and lane C, the PET lane, last committed on 2026-08-19 (§4); naming it would assign rows to a lane with no running session |

### C — leave it as it is

**Cost:** none now. `OI-53` stays WAITING-JOSEPH with no trigger, and the twelve stay `UNASSIGNED`.

## 7. Not done here

- **No row, owner cell or classification was changed.**
- **No lane was asked to accept anything.** Option B's acceptance would come after Joseph's choice.
