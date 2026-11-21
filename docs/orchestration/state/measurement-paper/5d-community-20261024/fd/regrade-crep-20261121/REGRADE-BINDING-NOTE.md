# REGRADE binding note (tier3-design, 2026-11-21, under the director's standing go)

**Binds** [`REGRADE-DECLARATION.md`](REGRADE-DECLARATION.md) rev 2.1 (sha256 `9b7e318e135c6ac3898bbd908a123a6bea0b7c6a4415e6a15baab5782cd68b43`).

**Authority:** the director's message of 2026-11-21, relaying Joseph ("I authorize all the runs and compute you need to
do for the things we've talked about … you should start the runs so they may be done when I get back"). The director
wrote: "a+c: write the short declaration and have Grok read it. If it passes, treat it as bound: commit it with a
binding note citing this go and the read." The director's later message added: "on Grok's GO, bind as planned. The
driver and capture code go to cov2d for review before anything runs."

**The reads** (Grok, headless, read-only; prompts and reports in `grok/`):

| read | of | verdict |
|---|---|---|
| read 1 | rev 0 | 1 BLOCKING, 4 MAJOR, 7 MINOR (`grok/read1-REPORT-rev0.txt`) |
| recheck 1 | rev 1 | all closed except 1 new MAJOR and 1 MINOR partial; NO-GO (`grok/recheck1-REPORT-rev1.txt`) |
| recheck 2 | rev 2 | both closed, none reopened, no new blocking or major issue; **VERDICT: GO** (`grok/recheck2-REPORT-rev2.txt`) |

Rev 2.1 corrects one gloss recheck 2 flagged as false: NumPy's absolute floor is the looser one, so C-PSD's relative
floor binds first. It changes no rule or control.

**Joseph's reading rule, as relayed:** "on a fail, the wording rests on the mean χ²". The declaration's R-χ² is the
only reading wording may rest on.

**Before anything runs:**
1. cov2d reviews the code: `regrade_crep.py`, `ll5d_regrade_capture.py`, their tests and the mutation receipt
   (commit f6bb6185), and the capture connect (commit ad7e0d4a).
2. The 2D half runs locally (cov2d).
3. The sixteen-cell capture is one login connect, with fresh acks, a window epoch from `date`, sacct only and
   O_NOATIME. Any guard refusal is terminal for the item.

**CANNOT AUTHORIZE:** anything the declaration cannot. Each result is read once from its committed record.

## Addendum 1: amendment 1 bound (2026-11-21)

**Binds** [`REGRADE-AMENDMENT-1.md`](REGRADE-AMENDMENT-1.md) rev 1 (sha256 `c8db882f7fc505ac843c3834e47d4a4c9661bbc2622f6592c86e7deebaf0c96a`). Section 6's A0 row in the
declaration, now sha256 `20697e6b60b82488608d3b97d2b2fef3137c845b36817c1f4006c0c1c7da2d2d`, marks the old clause superseded. Driver `regrade_crep.py`: `479e03cc51d7be8f0c275c98305b2ab731b135093afacb74f98417529c84d9ad`.

- **Authority:** the director's call of 2026-11-21, under Joseph's standing go: "amend A0(b) in both the 2D and the
  16-cell paths to COV2D A5's rule … Have Grok read the amendment, then commit a binding-note addendum". Later, from
  the director: "Amendment 1 as you describe it is approved, including κ₂ over the χ²'s non-null subspace".
- **Adopted after the STOP:** cov2d's 2D G18 A0(b), 1.73e-8 against the flat 1e-9 (752c3f60, `run2d/regrade_2d.json`).
- **Grok's reads:**
  - read of rev 0: NO-GO (M1, a false claim about A5 at AR23; M2, the full-spectrum κ₂ mutant survived), in
    `grok/amend1-read-REPORT-rev0.txt`;
  - recheck of rev 1: everything closed, **VERDICT: GO**, in `grok/amend1-recheck-REPORT-rev1.txt`.
- **Tests and mutation:** 54 OK; 35 of 35 mutants killed (`receipts/`).
- **What stands:** the 2D AR23 record (752c3f60) and the sixteen-cell record (a923a02e), whose A0(b) passed at the
  flat 1e-9.
- **What reruns:** 2D G18, locally by cov2d, with `--tunes G18`, at this driver after cov2d's look at the diff.
