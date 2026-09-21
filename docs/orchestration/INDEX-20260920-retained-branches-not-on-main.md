# INDEX 2026-09-20 — branches retained on `origin` whose content is NOT on `main`

**CITABLE FOR:** where to find work that `main` does not contain, by name and SHA.
**NOT CITABLE FOR:** the content, status, or correctness of anything on those branches.

`main` is the discovery route. Every other branch on `origin` whose tip is an ancestor of `main` was
deleted on 2026-09-20; its commits remain reachable from `main`. The branches below are **not**
ancestors of `main` — they hold commits `main` does not — and were retained. A SHA here is a route:
`git fetch origin <sha>` reaches it without a merge.

✅ **AMENDED 2026-09-20 — THE LIMITATION THIS RECORD OPENED WITH IS CLOSED.** It read:

> ⚠ **READ THIS ROW FIRST. The independent verification of the scalar-5D adoption lives on a branch,
> not on `main`.** An auditor reading only `main` will find the adoption and its decision record, and
> will NOT find the independent clause-(c) verification that was required before it. … This is a
> stated limitation of `main` as a single route, not an oversight.

**It is now on `main`**, merged at `ff0b6df0` after `OI-189` repaired the guard that had refused the
merge. `git rev-list --count main..lane/z-criteria-independent-assessment-20260910` measures **0**.
The row is struck below rather than deleted, because citations to it exist.

⚠ **What did NOT change:** the verification's `BLOCK` is answered by
[`DECISION-20260920-joseph-rules-clause-c-disposition.md`](DECISION-20260920-joseph-rules-clause-c-disposition.md),
not by the merge. **Landing a verdict on `main` is not disposing of it**, and the ordering defect it
disclosed — verification after adoption — is **ratified, not cured**.

Counts are `git rev-list --count main..origin/<branch>`, **re-measured 2026-09-20 after the merge at `ff0b6df0`** — a count in a document is a measurement with a date, and `main` moved. **Exactly one row changed: the clause-(c) lane, `69 → 0`.** The other fourteen re-measure to the values already printed — the merge brought in only that branch's commits. ⚠ Measure against `origin/<branch>`, not the local ref: this checkout's local `feat/production-interface` is **2** ahead of `main` while `origin`'s is **6**, so the two refs have forked and the local one would understate it. Re-measure before citing any row.

| branch | head | ahead | what it holds that `main` does not |
|---|---|---|---|
| ~~`lane/z-criteria-independent-assessment-20260910`~~ **MERGED — NOTHING LEFT TO FIND HERE** | `935b75585a7b9cc39cd52d4aa001df4edbea875f` | ~~69~~ **0** | ~~The independent clause-(c) verification…~~ **All 69 commits are on `main` as of `ff0b6df0` (2026-09-20): the verification with its BLOCK and `V1`–`V9`, the guard exercise with its positive control, the independent acceptance-criteria derivation parts A–H, and the NULL per-bin re-check.** |
| `pet-direct-token-comparison` | `c934c52757f0273b51ddd5e814bd12cf73953773` | 211 | The PET direct token-comparison campaign: grid behaviour, launch and failure records. |
| `lane/z-criteria-recommendation-20260910` | `a6bff83e7c9bb861ee4983bfce5d4ff4f9e234eb` | 60 | The criteria-owner lane: recommendations, and the writer fix upgraded from RELAYED to VERIFIED. |
| `lane/z-assembly-pilot-20260914` | `c4baf0d29297de0d0f50d5ea1d8b869ddaf83520` | 51 | The Z assembly pilot, its E1/E2 reconstruction assessment, and a refuted-then-relocated amendment finding. |
| `pet-gate6-strategy-20260825` | `a05baab141e777d2c77290c3de2bf9844a11e178` | 34 | PET Gate-6 diagnostic launches and their terminal-failure records. |
| `codex/pet-gate6-gap1-full-inventory-20260830` | `310d7e63d3690f1cd2df5ac3fcaf37ab0c5d39ed` | 17 | PET Gate-6 GAP 1: submission and terminal result. |
| `codex/pet-gate6-strategy-20260825` | `0969e787c7773520bfb7076aa24b39ae08852c2e` | 14 | PET Gate-6 08-25 strategy handoff, its three gaps, and the 56847059 cost correction. |
| `pet-prong-semantics` | `57b707b737ce817c1ef8d8bd0f0a39ce4becb7ba` | 14 | PET prong source audit: mapping PASS with a semantic discrepancy, and the follow-up. |
| `lane/z-campaign-ownership-20260913` | `e09513d842ad3acc1964c1af740696f02eaed7d9` | 10 | Campaign ordering certified optimal, with two of the lane's own claims withdrawn. |
| `feat/production-interface` | `7a2d9897a42c39d0413eef938cb90b6cae7239c0` | 6 | Production workflow recipes, member execution checks, and matched single-band systematic operations. |
| `lane/decision-20260910-z-endpoint-a-ruling` | `ae876e1441dfedfcf6df8501e84a387cd3de42da` | 2 | Two Z decisions that existed only in chat, landed as records; closes F-0. |
| `audit/scalar-5d-publication-gaps` | `ebba67ab6af17a159ae395cb06312b0dcbdca841` | 1 | The scalar-5D covariance and inference publication-gap audit. |
| `lane/cause3-voi-20260906` | `47494dbeda1a58f6ed8ee63c7bc698e580c04c5b` | 1 | The corrected cause-3 VOI packet: the composite is the Gate-2-blocked M(ii) family. |
| `lane/null-only-plan` | `819c64cad3925861d0388f215998f64fa3c3a00a` | 1 | The revised null-only plan: no slab migration, no pinning, one overclaim withdrawn. |
| `salvage-pet-gate6-preservation-20260903` | `93a75cf685c42ff9e26b0e0b990383f94949fa1d` | 1 | The PET Gate-6 branch-family preservation anchor: two pushed tags, removal proposed and not executed. |

---

## ⚠ FINDING 2026-09-20 — the revision that BUILT the adopted covariance was reachable from no tag and not from `main`

**`fb9ec3560fd6d62295dffc81b5694c9e26667d5b`** is named as the **assembling revision** in
`z-cv.npz`'s **own metadata**, in `z-receipt-cv.json`, in the adoption record §5, and in **every**
`git show fb9ec356:<path>` command of the third-lane verification. Measured while profiling the
retained set:

| question | measured |
|---|---|
| `git merge-base --is-ancestor fb9ec356 main` | **NO** *(at the time of measurement; **YES** after `db9f91d8` merged the pilot lane — the finding stands as the state that was true when the tag was made)* |
| `git tag --contains fb9ec356` | **empty** |
| branches containing it | **`lane/z-assembly-pilot-20260914` only** |

**And `main` having `z_*.py` is not a substitute.** Five of the six build modules differ from that
revision — only `z_assembly.py` is byte-identical:

| module | `main` vs `fb9ec356` |
|---|---|
| `z_assembly.py` | **SAME** |
| `z_build.py`, `z_contract.py`, `z_receipt.py`, `z_statistics.py`, `z_validator.py` | **DIFFER** |

So the code that built the published product was **one branch deletion away from being unreadable**,
while `main` would still have looked like it carried the build path.

**REPAIRED, per `CLAUDE.md`'s rule that pre-freeze provenance may leave `main` only through a pushed
evidence tag:**

    evidence/z-assembling-revision-fb9ec356   ->  fb9ec3560fd6d62295dffc81b5694c9e26667d5b

Annotated, **pushed**, and verified **on the remote** by peeling
(`refs/tags/…^{}` = `fb9ec356`) rather than by reading the push's output. Durability of that commit
no longer depends on any branch.

⚠ **What the tag does NOT do:** it does not put the build path on `main`, and it does not make
`lane/z-assembly-pilot-20260914` deletable *on its own merits* — that branch holds 51 commits and 41
files beyond this one revision. It removes the single worst consequence of deleting it.

### Disposition of the retained set — RECOMMENDED, not decided

| group | branches | recommendation |
|---|---|---|
| **PET — live workstream** | `pet-direct-token-comparison` (tip 2026-09-20), `pet-prong-semantics`, `pet-gate6-strategy-20260825`, `codex/pet-gate6-strategy-20260825`, `codex/pet-gate6-gap1-full-inventory-20260830`, `salvage-pet-gate6-preservation-20260903` | **LEAVE.** Not this closeout's subject, and PET has six PENDING jobs. Two already carry `evidence/preserved-…` tags. |
| **Scalar-5D docs, small** | `audit/scalar-5d-publication-gaps` (1 commit, 1 file), `lane/cause3-voi-20260906` (5 files), `lane/decision-20260910-z-endpoint-a-ruling` (5 files) | **MERGE, then delete.** Each is a handful of `docs/` files; the conflicts will be `CATALOG.md` / `MANIFEST-overrides.tsv`, which the repaired guard now reports rather than refuses. |
| **Scalar-5D, code-bearing** | `lane/z-assembly-pilot-20260914` (51), `lane/z-criteria-recommendation-20260910` (60), `lane/z-campaign-ownership-20260913` (10), `lane/null-only-plan` (2 files) | **DECIDE PER BRANCH — do not bulk-merge.** These carry executable files that would land on the publication path. The assembling revision is now tagged, so the urgency is gone. |
| **Infrastructure** | `feat/production-interface` (6 commits, 46 non-doc files, tip 2026-09-12) | **ITS OWNER'S CALL.** It is a feature branch, not closeout residue. |

**The rule that makes any of this safe is already written:** verify the tip is an ancestor of `main`
before deleting, and record every name→SHA **before** the deletion, not after
([`LEDGER-20260920-deleted-branch-names-to-sha.md`](LEDGER-20260920-deleted-branch-names-to-sha.md)).
⚠ **Add one clause to it, which this finding is the reason for: before deleting a branch, check
whether any SHA it uniquely reaches is CITED** — by a receipt, a product's metadata, or a decision
record. An ancestor check protects history; it does not protect a citation.

