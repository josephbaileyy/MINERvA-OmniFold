# DECISION 2026-10-23 — Joseph: run the GPU timing test now; a GPU campaign only if a measurement-quality paper is reasonably expected

**Recorded by** the paper-tighten lane, as director.

**What led to it.** Joseph drafted a note to Ben asking whether a share of the `m3246_g` GPU pool could fund a
brute-force validation of the 5D uncertainties. The director advised adding the chance of success (low with the
current method, on the record), and proposed a short GPU-node timing test to replace the unmeasured 2× estimate.

Joseph's answer, verbatim:

> yes do the GPU test right now and I will wait to send the message until that comes back. I feel like we would only want to use this many GPU hours if we reasonably believe this will result in a measurement-quality paper

sha256 of the text plus a final newline begins `698823bc22db3ecc`.

## What is decided

1. **The GPU timing test runs now**, as assigned in `state/gpu-timing-20261023/ASSIGNMENT.md`, within the
   measurement session's phase-1 grant (at most 1.0 GPU and 0.5 CPU node-h for this test).
2. **Joseph sends his note to Ben after the timing result is in.** Contacting Ben is Joseph's act.
3. **Criterion for any large GPU campaign:** it is proposed only when the record gives reasonable grounds to expect
   that it will produce a measurement-quality paper. A campaign that would most likely confirm a failure already
   measured at small scale does not meet it. Today the record does not meet it: s5e's development-scale departure
   coverage for configuration (e) is 0.017–0.157 against 0.68 (`state/s5e/cand/assess_receipt.json`), and KI 98,
   D-ID and MP4-A point the same way. The cheap tests (IBU-1; the reconstruction-information test R10 in the
   validation lane's scoping memo) come first.

## Not changed

- No campaign is authorized. Claims, the other lanes' grants, MP-2's hold.
