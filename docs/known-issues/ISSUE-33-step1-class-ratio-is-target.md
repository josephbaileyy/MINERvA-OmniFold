## `step1_class_ratio` in the nominal artifact is a stored TARGET, not an achieved measurement

Found 2026-08-07 by making the mistake. Investigating the nominal's fold-forward failure I read
`pet_fullevent_nominal_weights.npz`'s `step1_class_ratio = 1.1240802949941018`, saw it equal Gate-2's R
exactly, and concluded *"not the classic step-1 defect — that signature is the class ratio forced to 1, ours
is exactly R."* **That inference is invalid.** `train_fullevent_nominal.py:464` sets
`class_ratio = target_meta.get("step1_class_ratio")` — from the loader's target metadata — and stores it
verbatim at `:505`. `fullevent_fps_dataloader.step1_class_ratio_from_dump` derives R from the dump's data/MC
yields. So the field is **the target R, re-stored**; it can never disagree with R and therefore carries **zero
information** about what step 1 achieved. Agreement is tautological.

The trap is the name. A field called `step1_class_ratio` sitting beside genuine measurements
(`cap_saturation_frac`, `fold_forward_sum_w_push_reco`) reads as "the class ratio step 1 produced". It is a
copy of the input. **Consequence:** the step-1 under-achievement hypothesis is *not* ruled out for the
2026-08-07 nominal, and it is now the leading candidate — the historical defect drives the effective ratio
toward 1, and a folded-forward ratio of 0.7465 against a required 1.1241 is the right direction for it.

**Fix forward, two parts.** (1) Rename or re-document the stored field so it cannot be read as an outcome —
`step1_class_ratio_target` would have prevented this. (2) The achieved value has now been measured by
trajectory job `56525829`: iteration 0 is correct-sign and within 9.74% of R, while iterations 1 and 2
are wrong-signed. The defect is therefore in post-feedback iteration dynamics, not an initial class-ratio
normalization failure. Detail and exact numbers: `docs/orchestration/FINDING-20260807-step1-under-achieves.md`.

