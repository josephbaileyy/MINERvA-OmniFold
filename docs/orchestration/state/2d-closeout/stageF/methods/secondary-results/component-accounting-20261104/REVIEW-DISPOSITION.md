# Source review and disposition: B-C and C-N

The owner is the component-accounting records lane. Following the handoff's invitation and the
campaign review's bounded source-check advice, a fresh read-only reviewer checked this packet.
The first requested `gpt-6-astra` high-effort review returned a service usage-limit error and no
review content. The fallback was `gpt-6.1-sol`, high effort, in a fresh context. This was a narrow
source/metadata review rather than an implementation or statistical campaign; no model-quality
comparison is inferred from the service substitution. Inference costs are unavailable.

`REVIEW-PROMPT.txt` is the exact initial prompt. `REVIEW-TARGET.sha256` records the pre-repair
packet identities. The two findings were checked by the owner against the actual source and
repaired in one focused round:

1. B-C had overstated the signal-fake guard. The ordinary refined path includes fakes in its
   background histogram and injected sample. Only the `p1_on` background-bootstrap stream rejects
   nonzero fakes (`re2_driver.py:1907–1924,2188–2193 @ 97f1ff8de`). E_R's health entry says
   `background_stream=false`; its successful central run does not exercise that guard. The table
   and c2/c1 handoff now preserve this distinction. No numerical E_R error was measured or inferred.
2. C-N's F1 refusal citation had the wrong reading lines. `flux_record` and its refusal are
   `fd_rpd_inputs.py:530–535 @ 97f1ff8de`; the report and source inventory now point there.

`REVIEW-REPAIR-PROMPT.txt` is the exact focused follow-up message, and `REVIEW-ANSWER.txt` preserves
the final answer verbatim with a final newline. The reviewer verified the source identities and
literal inventories, reread these repairs, and found no material issue remaining. It edited no
files. The single review and single repair budget is complete.

The verdict is for the inventory's bounded adequacy only. It is not numerical validation of the
original producers, current remote-storage verification, c2/c1 admission, permission to execute
P0 or d2, or a publication claim. Publication intermediate gaps and the identified F1/runtime
limits remain explicit. The QUESTION is prepared and unsent. No application source or manuscript
source changes; the checks for delivery are the repository's record checks.
