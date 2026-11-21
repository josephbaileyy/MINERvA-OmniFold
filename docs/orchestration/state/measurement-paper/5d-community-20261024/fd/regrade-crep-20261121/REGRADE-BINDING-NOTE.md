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
