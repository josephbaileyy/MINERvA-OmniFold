# DECISION 2026-11-01 — Joseph: approve both whole abstracts; let the event-loop files age out

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- **The abstracts.** The paper rewrite lane finalized the gpt-6-astra abstracts without the exclusions sentence
  (`DECISION-20261031-joseph-abstracts-astra-without-exclusions-line.md`) on PR #619 at `6ed1e5c91`. The director
  rebuilt the PDFs at that head (`build_all.sh` rc 0). Both abstracts print the lane's text word for word, apart from
  pdftotext artifacts (χ² as "χ2", hyphens lost at line breaks).
- **E_avail.** Step 0 of the switch pricing (PR #622 §7) measured the switch's size read-only: at most 0.21σ per cell
  (R06), and 0.42σ as a full-covariance norm, both first order.
- **The event-loop files.** The 12 per-playlist 5D universe event loops (about 159 GiB) are exposed to pscratch purge
  from 2026-11-09, and their merge (about 171 GB) from 2026-11-22. Neither fits the remaining HPSS quota, and
  Joseph's standing rule sends nothing to CFS.

> Approve the two final abstracts above as whole abstracts (then #619 merges and the four Sec. I-III edits start)?

Joseph's answer, verbatim:

> Approve both (Recommended)

sha256 of the text plus a final newline begins `a99a9d0ed33a1995`.

> E_avail: keep 135 MeV or switch to 139.57 MeV?

Joseph's answer, verbatim:

> is it an issue that we dont match their e-avail

sha256 of the text plus a final newline begins `7c56147626405a48`.

> The event-loop files exposed to purge from 11-09 (~159 GiB) and 11-22 (merge, ~171 GB): keep or let them age out?

Joseph's answer, verbatim:

> Let them age out (Recommended)

sha256 of the text plus a final newline begins `505fa7977ea00405`.

## What is decided

1. **Both whole abstracts are approved (A4)** as built at `6ed1e5c91`. The lane pins the abstract pairs, and #619
   merges on its gates. Then #620's four edits start. The departure sentence after Eq. (1) stays held.
2. **The per-playlist universe event loops and their merge are left to age out.** Nothing is copied to CFS or HPSS,
   and nothing is touched to change their purge exposure.
   - Consequence: a later switch to 139.57 MeV would need those event loops rerun, at a CPU cost not yet measured
     (#622 §3.2), instead of the cheaper route at the dump.
3. **E_avail is not yet decided.** Joseph asked whether it matters that we do not match MINERvA's E_avail. The director
   answers from `docs/EAVAIL_DEFINITION.md`, and the question goes back to him. Until then, 135 MeV stays the defined
   constant.

## Not changed

Every number, the E_avail definition, the 1B outcome (#634), and the pscratch files' state. Nothing is submitted,
deposited or tagged.
