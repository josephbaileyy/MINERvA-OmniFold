# REGRADE sixteen-cell half: capture and local regrade (tier3-design, 2026-11-21)

**Under** REGRADE-DECLARATION.md rev 2.1, bound by REGRADE-BINDING-NOTE.md under the director's standing go. cov2d
reviewed the code (OK at 427063e1; F1–F4 fixed at 831c095d, OK).

**CANNOT AUTHORIZE:** any wording. Joseph's reading rule applies: on a fail, the wording rests on the mean χ² (R-χ²).
The record is read once, from this commit.

## The capture connect

- **Fence.** Acks from cov2d, limitation-resolver and director-helper-3, at 11:04:41–11:04:44Z, all reporting no jobs.
  Window end 11:19:41Z, from `date`.
- **The run.** login25, 2026-11-21T11:04:56–11:06:26Z, `capture_connect.sh` c14801be (its node copy is committed as
  `connect/capture_connect.sh.txt` and equals the committed script). See `connect/connect-capture.log.txt`.
  - fence clear (sacct);
  - a fresh clone at M_L 4231b14d, clean;
  - the capture tool fed8c971 and the hpss list 980bb95e, taken from f6bb6185 and pin-checked;
  - setup_salloc_env.sh at ea3c6998, with the paths surviving the source;
  - root_6_28 python 3.11.14.
- **The capture manifest.** `capture/capture-manifest.json`, 4cabeeb6.
  - S1 assembly db000707 and constraint e38ad7d2 pin-checked; 1,654 products pin-checked;
  - 1,656 watched paths: atime moved [], changed [];
  - capture 11:05:53–11:06:25Z;
  - four captures, each equal to the manifest's sha256 after the fetch.
- **Cost:** 0 node-h, no Slurm job.

## The local regrade

`regrade_crep.py run16` at driver 5073bb7a (reviewed), writing `capture/regrade16.json` (df590558…; beside the captures it names). The statuses printed:
`{"g18/minus2": "done", "g18/all": "done", "ar23/minus2": "done", "ar23/all": "done"}`, rc 0.

The record was committed before any of its numbers was read. A0(b) passed at the declaration's flat 1e-9 at all four
evaluations, so amendment 1's looser rule (adopted afterwards, for the 2D G18 STOP) does not touch this record.
