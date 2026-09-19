# The step-2 representation for his arm: an open design decision, not an oversight

**CITABLE FOR:** what is built, what is not, and why the remaining choice is a
scientific one rather than an engineering one.
**NOT CITABLE FOR:** any comparative result. No arm has been trained.

---

## 1. What is built

His complete arm's **reco-side** inputs exist and are constructed from the real
tuples: tokens `[px, py, pz, log E, PID]`, auxiliary `[dE/dx, x, y, z, t]`,
sixteen globals, cap 33 with his aggregation. That is step 1 of OmniFold, where
MC reco is reweighted to data.

## 2. What is not, and why it is a decision

OmniFold **step 2** pulls the weight back to truth, and its network consumes a
**truth** representation. Ours is `build_truth_cloud`: `part_gen` `(N, P, 5)` =
`(E, px, py, pz, pdg)` expanded to eight features.

His complete arm is defined by a **reco-object vocabulary** — blobs, prongs,
photons, a muon, with dE/dx, positions and times. **Truth particles have none of
those.** There is no truth blob, no truth prong, no truth dE/dx. So "his
configuration at step 2" is not determined by his paper, because his paper does
not run OmniFold.

Three readings, and they are not equivalent:

| reading | step-2 input for his arm | what it makes the comparison mean |
|---|---|---|
| **A — shared truth** | the same truth cloud ours uses, mapped into his 4+PID+5 widths with zero auxiliary | the comparison is of the **reco-side architecture and inputs**, with the truth side held fixed. Cleanest attribution; his arm is not "his" at step 2 |
| **B — his schema on truth** | truth particles as his tokens: `[px, py, pz, log E, PDG→code]`, auxiliary all zero, globals from truth | symmetric in schema, but invents a PID mapping he never defined and feeds a 33-token cap to events with few truth particles |
| **C — his backbone, our truth features** | our eight truth features, his PET2 body | compares backbones only; the input-representation question disappears at step 2 |

**A is the only one that does not invent something of his.** B requires a
PDG→code map that exists nowhere in his repository; C changes his input width and
so is not his configuration either.

## 3. Why this is not a detail

`configuration_identity.py` and the goal both require that his complete arm
"retains the intended PID, auxiliary inputs, globals and cap". At step 2 the
auxiliary inputs do not exist and the PID vocabulary does not apply. Whichever
reading is taken, **his arm at step 2 is not the configuration his paper
describes**, and a result must say which reading produced it.

Picking one silently would be the failure this lane exists to avoid: the number
would be reported as "his configuration" when it is one of three things that
could bear that name.

## 4. Recommendation

**Reading A**, with the step-2 network identical between arms and the difference
confined to step 1, reported as: *a comparison of reco-side representation and
architecture, with the truth-side estimator held fixed.* It is the only reading
in which every element of his arm is his, and the one whose scope sentence is
true.

It also changes what the comparison can conclude, and that limit belongs in the
conclusion rather than in a footnote: it cannot speak to his configuration's
behaviour on the truth side, because that configuration does not exist.

## 5. What this blocks

Nothing that is already running. The reco-side inputs are building
(array 58591372). Step 2 needs this decision before the campaign launches,
because the frozen design must name the step-2 network for both arms before any
comparative result exists — item 13 requires exactly that.
