# The V_F recompute: the input-existence check (receipt, tier3-design, 2026-11-25)

**What this records:** a read-only check that every NERSC input of the V_F recompute still exists and equals its
committed pin. It covers Phase 1 and Phase 2 of the plan sent to the director after DECISION #1326 (V_F adopted).
Joseph asked for it first; nothing was recomputed.

**Result: every input exists.** All 9,862 pinned files that were read equal their pins. Nothing is missing, changed or
unreadable.

**CITABLE FOR:** which inputs of the V_F recompute exist on NERSC and equal their pins, as of the run below.

**NOT CITABLE FOR:** any recomputed number, any decision about the recompute's scope, any note wording.

## The counts

| phase | EXISTS | EXISTS-UNHASHED | CHANGED | MISSING | READ-ERROR | NOT-CHECKED |
|---|---|---|---|---|---|---|
| P1 | 8,580 | 0 | 0 | 0 | 0 | 0 |
| P2 | 1,286 | 1 | 0 | 0 | 0 | 0 |
| HPSS | 10 | 0 | 0 | 0 | 0 | 0 |

- **EXISTS:** 9,862 pinned files, each read once through `dd iflag=noatime` into sha256sum, and each equal to its pin.
  0 atimes moved.
- **The four unpinned files also exist:** `e96data-a1/log-full/DONE`; `e96data-a1/log-full/SHA256SUMS`; `fd-prr-20261108/log-ibu/SHA256SUMS`; `gencmp-20261101/d/rebuild/rebuild.json`.
- **EXISTS-UNHASHED:** `MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root`, xk's identity-check input (Phase 2). It is stat only, by the
  director's rule for files over 10 GiB, and its 171,117,087,867 bytes equal the pinned size.
- **HPSS:** all ten retention archives exist: central.tar (99,328 B); cpl.tar (3,934,720 B); cstat.tar (2,849,280 B); f0b.tar (1,590,736,896 B); prr.tar (33,495,552 B); rpd_dumps.tar (1,577,486,336 B); s1_cmodel_cresp_tables.tar (2,289,664 B); shared_inputs.tar (1,564,460,032 B); tier3_inputs.tar (2,164,736,000 B); zero_loops.tar (4,841,755,648 B). Nothing is missing, so no restore is needed.

## The run

- **Where:** login02, once, at 0 node-h. There was no Slurm job, and nothing was written on the cluster.
  - The script went on ssh stdin and was held in a shell variable. Its sha256 was checked on the node:
    `6d0725c11de27eaa63592e33e0127b9c0eaf29ebe070c373ca6387087c082640`, the approved one. It ran by eval in a subshell.
  - Output was stdout only.
- **When:** the launcher ran 2026-11-25T08:25:10Z to 2026-11-25T08:37:50Z; the node ran ? to 2026-11-25T08:37:49Z. The window ended at 2026-11-25T08:38:01Z.
- **Certificate:** checked by command, with 68,621 s left.
- **Fence:** sacct was clear for cov2d, rpd_, d2s0, covfix and ibub.
- **Acks** (each with the acker's own `date -u` time):
  - director-helper-3, 2026-11-25T08:23:01Z: `2d-closeout-re2-20261023/partb/out/ER/xsec.root`;
  - cov2d, 2026-11-25T08:23:06Z: its 291 protected paths, by root (the 175 G2R universes, the RE-2 part-B products
    and ER/xsec.root, the re2shapes products, the universes_full.root as stat only, and the flux constraint);
  - limitation-resolver, 2026-11-25T08:24:51Z: the NuE flux constraint.

  The window was the oldest ack plus 900 s. I told LR right before connecting, and sent END messages to all three after.
- **GO:** the director's, after he re-measured the check, launcher, inputs and generator shas.

## How the input list was built

1. **Extraction.** codex-school (GPT-6, read-only, main e75b6dd2) extracted each producer's NERSC inputs from the
   recorded argv and receipts (`extraction/`). The earlier scope read is in `scope/`.
2. **Expansion and pin checks.** `package/expand_inputs.py` expanded each manifest range and directory into files,
   with each file's pin read from the committed manifest. It checked that every explicit pin appears verbatim in the
   committed file it cites, with 0 failures, and deduplicated rows: a path read by any Phase 1 producer counts as P1.
   It also added the ten HPSS archives.
3. **The check and launcher.** `package/gen_vf_check.py` generates `vf_inputs_check.sh` and `vf_inputs_launch.sh` from
   `inputs.tsv`; rerunning it gives the same bytes.
4. **Overlap.** `package/vf_overlap.py` uses B5D's bound overlap composition, imported unchanged (`overlap.txt`). It
   found 293 read-on-read hits: cov2d 291, rpd flux2 1, ibub 1. All three owners acked.
5. **Stand-in** (`package/standin/`). Debian with a read-only root and no tmpfs, a non-root uid, a named volume, and
   stub sacct and hsi. Every status was exercised: EXISTS, CHANGED, MISSING, READ-ERROR, both size outcomes of
   EXISTS-UNHASHED, a directory, HPSS present and absent, a fence BAIL and a window BAIL. The logs are
   `standin2*.log`. One finding: O_NOATIME is refused on a file the reader doesn't own, which shows as READ-ERROR.

The run's TSV holds exactly the 9,877 (path, pin) pairs of `package/inputs.tsv`.

## Files

| file | sha256 |
|---|---|
| `extraction/p1-codex.txt` | `628e78f47bcd71aa43011ac6204fb7d71077897b92f42aa27c9425c0f3a21798` |
| `extraction/p1-prompt.txt` | `4d96f6a87d9ea799f8ddf78343f442002684ad05922d15d253eff60b5046e646` |
| `extraction/p1.tsv` | `c55ee52f7d300ea93bf47968e1c4e7a5fcd609d06c39f5078bd683aa7c61ee64` |
| `extraction/p2-codex.txt` | `95ab2411449b989bc7b72000e9ac7a71e4e109114bca689c35d05f8217b443f4` |
| `extraction/p2-prompt.txt` | `e4d1d00d7d12da2b5e3e3dca417aae91ee88f31d805316aa42cdb52aa49b7d83` |
| `extraction/p2.tsv` | `c054c586c716d7933be47c806b1805ef70401c45431054c98ba3d9b9f30e8c0d` |
| `package/expand_inputs.py` | `00895dacb339b40dbe27a54d09cb83ed143b86b671dc1dceaa58b6cd4ed52994` |
| `package/gen_vf_check.py` | `20aa6ac411c73ab58ab15c154c1332170c14e7b6a1ca6848c7a6194b4a128842` |
| `package/inputs.tsv` | `af859482f14caf44b44ebe1949a5ed3058c1fc1381a6e2e63729cfc956d9a959` |
| `package/overlap.txt` | `8a604d2fb24e408208766994ea31ed605ea94feb9060838af439c3cf0105161e` |
| `package/standin/hsi` | `7aabd97d96e0e9500568a17dc813fbbed2e723be834c63c6f4def38720fa5735` |
| `package/standin/inputs-standin.tsv` | `6ad1698cc1e7dc936f434ce735e0fdb420ddd9cec7f7c8a34984b0306e93648a` |
| `package/standin/inputs-standin2.tsv` | `8b61de950c41f1602d6650a2c333c9d90604436b0814f5a497082d57ab0fe0a2` |
| `package/standin/remote-standin2.sh` | `19a77a30f2d0eb3bdc1d5b23f419fd234bbe56a8a90ee99dc0bd3c4714d3a0a6` |
| `package/standin/remote.sh` | `df4063792eddfa3a44f8a07b8898212f9d8fa72b126ea193b9fa0d91ba4bddb0` |
| `package/standin/sacct` | `e1f9da4d9788f5f41492379a7bca37de8f0bfbd454f519d96319dd5003b0ebb8` |
| `package/standin/standin2-fence.log` | `4cb16850421765c17d6f10af085e51cd59ef84384737aaa2f8075b605b5e541b` |
| `package/standin/standin2-window.log` | `76ba7fcedbf3a223ae6573e765da0e5a7874304c538698e297caa49d6f4fe198` |
| `package/standin/standin2.log` | `0cdbdf2cfc55ffa0b5378cc0cb706fc9312d6ffcb9d457ef04b8b6467e7241ae` |
| `package/vf_inputs_check.sh` | `6d0725c11de27eaa63592e33e0127b9c0eaf29ebe070c373ca6387087c082640` |
| `package/vf_inputs_launch.sh` | `f8aa5f9ec551a8e36f0498877a12e69789b3fdb2bfbd404a9a318f754f9060e5` |
| `package/vf_overlap.py` | `f5e2c2cf01248801c89f97a0a654cac0a354e562df02ecf630c1d4aa2f4dc063` |
| `run/launcher-rc.txt` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` |
| `run/launcher.out.txt` | `a64cd3d9773d9f15a92d4c98eafd852a78a21c6bcf8b14adeba9ef251fc014fb` |
| `run/run-end-utc.txt` | `320adc88e69c1bc2c1e1bb8fb577fa0f10bf58be97caa383fbae12dfc21d840c` |
| `run/run-start-utc.txt` | `5896cc978593b26000c3b3bba2d77ed4cb1749438d56bb49617493b3c4b292d7` |
| `run/session.err` | `af9f98e88d6749dc0f4761b457ba093c7dd86e84357f9f9d612a38def7e8604e` |
| `run/session.out` | `d5de927724b19b24de758aa2f1a2146a5e68b545201389a9acae2b0e6f919d4e` |
| `run/vf_inputs_check.tsv` | `12ed8c98ac05b320c466322fdee2260dd641371464d6e7b16414e31062dc84af` |
| `scope/vf-scope-codex.txt` | `9ac8506c4608eef343061d6049f242f114488aea3c84329b7cf4413e3e6dc40f` |
| `scope/vf-scope-prompt.txt` | `a5f8c20818029f628cb6ad35d4c62a25081e02df73f2f20334e76d7420a0384a` |
